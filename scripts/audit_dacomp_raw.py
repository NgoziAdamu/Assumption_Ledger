"""Task 013: read-only raw schema/count comparison and literal write-syntax evidence."""

import ast
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import re

from build_dacomp_annotation_packages import fence
from check_dacomp_constraints import open_readonly
from compare_dacomp_staging import quote
from complete_dacomp_comparisons import ROOT,RECORDS,save,stamp

RAW=r'(?:(?:[A-Za-z_][\w$]*|"[^"]+")\s*\.\s*)?(?:raw|"raw"|`raw`)\s*\.'
PATTERNS=[
 ('CREATE TABLE/VIEW',r'\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:(?:TEMP|TEMPORARY)\s+)?(?:TABLE|VIEW)\s+(?:IF\s+NOT\s+EXISTS\s+)?'+RAW),
 ('CREATE/DROP SCHEMA',r'\b(?:CREATE|DROP)\s+SCHEMA\s+(?:(?:IF\s+NOT\s+EXISTS|IF\s+EXISTS)\s+)?(?:raw|"raw"|`raw`)(?![\w.])'),
 ('ALTER/DROP/TRUNCATE TABLE',r'\b(?:ALTER|DROP|TRUNCATE)\s+(?:TABLE|VIEW)\s+(?:IF\s+EXISTS\s+)?'+RAW),
 ('INSERT/REPLACE INTO',r'\b(?:INSERT\s+(?:OR\s+REPLACE\s+)?INTO|REPLACE\s+INTO|MERGE\s+INTO)\s+'+RAW),
 ('UPDATE',r'\bUPDATE\s+'+RAW),('DELETE FROM',r'\bDELETE\s+FROM\s+'+RAW),
 ('COPY FROM',r'\bCOPY\s+'+RAW),
 ('SET SCHEMA raw',r'\bALTER\s+TABLE\s+[^;\n]{1,200}?\s+SET\s+SCHEMA\s+(?:raw|"raw"|`raw`)(?!\w)'),
 ('write API',r'\.(?:to_sql|write_database|create_view|insert_into|to_table)\s*\([^\n]{0,300}?(?:schema\s*=\s*[\'\"]raw[\'\"]|[\'\"]raw\.)')]
CALL=re.compile(r'\b(?:python(?:[0-9.]+)?|bash|sh)\s+(?:(?:-[A-Za-z]+)\s+)*[\'\"]?([^\s;|&<>\'\"]+\.(?:py|sh))',re.I)


def write_hits(text,path):
    hits=[];lines=text.splitlines(keepends=True)
    for operation,pattern in PATTERNS:
        for match in re.finditer(pattern,text,re.I):
            if operation=='COPY FROM':
                tail=re.split(r';',text[match.end():match.end()+1200],maxsplit=1)[0]
                direction=re.search(r'\b(FROM|TO)\b',tail,re.I)
                if not direction or direction.group().upper()!='FROM':continue
            line=text.count('\n',0,match.start())+1;end=text.count('\n',0,match.end())+1
            hits.append({'operation_syntax':operation,'source':str(path),'start_line':line,'end_line':end,
                'original_match':match.group(),'original_line':''.join(lines[line-1:end]),
                'original_context':''.join(lines[max(0,line-2):min(len(lines),end+3)])})
    return sorted(hits,key=lambda h:(h['start_line'],h['operation_syntax']))


def historical_scripts(command):
    """Recover literal file bodies only; never execute recorded shell/Python code."""
    result={}
    patterns=[r'\bcat\s*>\s*[\'\"]?([^\s\'\"<>]+)[\'\"]?\s*<<\s*[\'\"]?([A-Za-z_][\w]*)[\'\"]?[^\n]*\n',
              r'\bcat\s*<<\s*[\'\"]?([A-Za-z_][\w]*)[\'\"]?\s*>\s*[\'\"]?([^\s\'\"<>]+)[\'\"]?[^\n]*\n']
    for number,pattern in enumerate(patterns):
        for match in re.finditer(pattern,command):
            name,delimiter=match.groups() if number==0 else tuple(reversed(match.groups()))
            ending=re.search(r'^'+re.escape(delimiter)+r'\s*$',command[match.end():],re.M)
            if ending:result[name]={'text':command[match.end():match.end()+ending.start()],
                'provenance':'literal heredoc in recorded command','name':name}
    # Literal Path(...).write_text(...) inside Python heredocs.
    for start in re.finditer(r'\bpython[0-9.]*\s+-\s*<<\s*[\'\"]?([A-Za-z_][\w]*)[\'\"]?[^\n]*\n',command):
        ending=re.search(r'^'+re.escape(start.group(1))+r'\s*$',command[start.end():],re.M)
        if not ending:continue
        body=command[start.end():start.end()+ending.start()]
        try:tree=ast.parse(body)
        except SyntaxError:continue
        variables={};paths={}
        def literal(node):
            if isinstance(node,ast.Constant) and isinstance(node.value,str):return node.value
            if isinstance(node,ast.Name):return variables.get(node.id)
            if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Add):
                a,b=literal(node.left),literal(node.right)
                return a+b if a is not None and b is not None else None
            return None
        def filename(node):
            if isinstance(node,ast.Name):return paths.get(node.id)
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='Path' and node.args:return literal(node.args[0])
            return None
        for node in tree.body:
            if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
                name=node.targets[0].id;value=literal(node.value);path=filename(node.value)
                if value is not None:variables[name]=value
                if path is not None:paths[name]=path
            for call in ast.walk(node):
                if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Attribute) or call.func.attr!='write_text' or not call.args:continue
                name=filename(call.func.value);text=literal(call.args[0])
                if name is not None and text is not None:result[name]={'text':text,'provenance':'literal Python Path.write_text in recorded command','name':name}
    return result


def raw_inventory(path,scratch):
    with open_readonly(Path(path),scratch) as connection:
        tables=connection.execute("SELECT table_name,table_type FROM information_schema.tables WHERE table_catalog=current_database() AND table_schema='raw' ORDER BY table_name").fetchall()
        inventory={}
        for name,kind in tables:
            columns=connection.execute("SELECT column_name,data_type,ordinal_position FROM information_schema.columns WHERE table_catalog=current_database() AND table_schema='raw' AND table_name=? ORDER BY ordinal_position",[name]).fetchall()
            count=connection.execute('SELECT count(*) FROM raw.'+quote(name)).fetchone()[0]
            inventory[name]={'table_type':kind,'row_count':count,'columns':[{'name':n,'type':t,'ordinal_position':i} for n,t,i in columns]}
    return inventory


def compare_raw(case):
    scratch=ROOT/'data/013_raw_compare'/case['task'];scratch.mkdir(parents=True,exist_ok=True)
    initial=raw_inventory(case['initial_database'],scratch/'initial');agent=raw_inventory(case['agent_database'],scratch/'agent')
    rows=[]
    for name in sorted(set(initial)|set(agent)):
        a,b=initial.get(name),agent.get(name);ac={c['name']:c for c in a['columns']} if a else {};bc={c['name']:c for c in b['columns']} if b else {}
        rows.append({'task':case['task'],'table':name,'initial_exists':a is not None,'agent_exists':b is not None,
            'initial':a,'agent':b,'initial_only_columns':[c for c in a['columns'] if c['name'] not in bc] if a else [],
            'agent_only_columns':[c for c in b['columns'] if c['name'] not in ac] if b else [],
            'type_differences':[{'column':n,'initial_type':ac[n]['type'],'agent_type':bc[n]['type']} for n in sorted(ac.keys()&bc.keys()) if ac[n]['type']!=bc[n]['type']],
            'column_order_differences':[{'column':n,'initial_position':ac[n]['ordinal_position'],'agent_position':bc[n]['ordinal_position']} for n in sorted(ac.keys()&bc.keys()) if ac[n]['ordinal_position']!=bc[n]['ordinal_position']],
            'columns_and_types_equal':bool(a and b and a['columns']==b['columns']),
            'row_counts_equal':bool(a and b and a['row_count']==b['row_count']),
            'row_delta_agent_minus_initial':b['row_count']-a['row_count'] if a and b else None,
            'different':a is None or b is None or a['columns']!=b['columns'] or a['row_count']!=b['row_count'],
            'initial_database':case['initial_database'],'agent_database':case['agent_database']})
    return rows,{'task':case['task'],'initial_raw_tables':len(initial),'agent_raw_tables':len(agent),'union_tables':len(rows),
        'different_tables':sum(r['different'] for r in rows),'schema_different_tables':sum(not r['columns_and_types_equal'] for r in rows),
        'row_count_different_tables':sum(not r['row_counts_equal'] for r in rows),
        'initial_only_tables':sorted(set(initial)-set(agent)),'agent_only_tables':sorted(set(agent)-set(initial)),
        'different_table_names':[r['table'] for r in rows if r['different']]}


def scan_task(case):
    root=Path(case['agent_directory']);scripts={}
    for filename in case['final_script_files']:
        path=Path(filename)
        if path.suffix not in ('.py','.sh'):continue
        text=path.read_bytes().decode('utf-8')
        scripts[str(path)]={'text':text,'path':str(path),'provenance':'final retained script; historical runtime version not established',
            'write_syntax':write_hits(text,path),'sha256':hashlib.sha256(text.encode()).hexdigest()}
    events=[(p,json.loads(p.read_text())) for p in Path(case['trace_directory']).glob('.events/sessions/*/events/*.json')]
    actions=sorted([(p,e) for p,e in events if e.get('action')=='run'],key=lambda x:x[1]['id'])
    observations=defaultdict(list)
    for p,e in events:
        if e.get('observation'):observations[e.get('cause')].append(e)
    history={};found=[];unresolved=[]
    for path,event in actions:
        command=event.get('args',{}).get('command','');direct=write_hits(command,path);calls=[]
        recovered=historical_scripts(command)
        for name,script in recovered.items():
            full=str(Path(name) if Path(name).is_absolute() else root/name)
            script.update(path=full,event_id=event['id'],write_syntax=write_hits(script['text'],f'{path}#script:{name}'))
            history[full]=script
        for match in CALL.finditer(command):
            name=match.group(1);full=str(Path(name) if Path(name).is_absolute() else root/name)
            script=history.get(full) or scripts.get(full)
            if script is None:
                unresolved.append({'task':case['task'],'event_id':event['id'],'event_file':str(path),'script_name':name,
                    'command':command,'status':'script body not recoverable from literal prior commands or final retained files'})
            elif script['write_syntax']:
                calls.append({'script_name':name,'script_path':full,'provenance':script['provenance'],
                    'script_text_recorded_event':script.get('event_id'),'script_sha256':hashlib.sha256(script['text'].encode()).hexdigest(),
                    'matching_original_statements':script['write_syntax'],
                    'runtime_branch_execution_proven':False,'exact_runtime_file_version_verified':False})
        if direct or calls:
            found.append({'task':case['task'],'event_id':event['id'],'event_file':str(path),
                'archive_member':'dacomp_deimpl_prev/'+path.relative_to(ROOT/'data/dacomp_deimpl_prev').as_posix(),
                'action_type':event['action'],'command':command,'command_direct_write_syntax':direct,'invoked_script_write_syntax':calls,
                'recorded_exit_codes':[o.get('extras',{}).get('metadata',{}).get('exit_code') for o in observations[event['id']]],
                'scope':'Literal write syntax / invoked script source evidence; does not assert a branch executed or a write changed data.'})
    return found,unresolved,scripts


def main():
    cases=json.loads((RECORDS/'013_cases.json').read_text());allrows=[];summaries=[];writes=[];unresolved=[]
    directory=RECORDS/'013_raw_writes';directory.mkdir(exist_ok=True)
    for case in cases:
        rows,summary=compare_raw(case);allrows.extend(rows)
        found,unknown,scripts=scan_task(case);writes.extend(found);unresolved.extend(unknown)
        summary.update(raw_write_syntax_steps=len(found),direct_command_steps=sum(bool(s['command_direct_write_syntax']) for s in found),
            invoked_script_steps=sum(bool(s['invoked_script_write_syntax']) for s in found),unresolved_script_calls=len(unknown))
        summaries.append(summary)
        text='# '+case['task']+'：raw 写语法与脚本调用原文\n\n'
        text+='仅记录语法命中和调用源码；脚本分支执行、历史文件版本、操作是否改变数据未由静态匹配证明。\n'
        for step in found:
            text+='\n## event '+str(step['event_id'])+'\n\n'+str(step['event_file'])+'\n\n'
            text+=fence(step['command'],'bash')
            for hit in step['command_direct_write_syntax']:
                text+='\n命令语法：'+hit['operation_syntax']+'；命令内行 '+str(hit['start_line'])+'\n\n'+fence(hit['original_context'])
            for call in step['invoked_script_write_syntax']:
                text+='\n脚本：'+call['script_path']+'；'+call['provenance']+'\n'
                for hit in call['matching_original_statements']:
                    text+='\n'+hit['operation_syntax']+'；源码行 '+str(hit['start_line'])+'\n\n'+fence(hit['original_context'])
        if not found:text+='\n未发现所列语法 / 已留存脚本调用匹配。\n'
        (directory/f"013_{case['task']}_raw写操作.md").write_text(text)
        save(RECORDS/f"013_raw_{case['task']}.json",{'task':case['task'],'initial_database':case['initial_database'],
            'agent_database':case['agent_database'],'tables':rows,'summary':summary,'write_steps':found,'unresolved_script_calls':unknown})
        print(case['task'],'different raw tables',summary['different_tables'],'write-syntax steps',len(found),flush=True)
    (RECORDS/'013_raw_tables.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in allrows))
    (RECORDS/'013_raw_write_steps.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in writes))
    save(RECORDS/'013_unresolved_script_calls.json',unresolved)
    save(RECORDS/'013_raw_summary.json',{'completed_at':stamp(),'tasks':len(cases),'raw_table_pairs':len(allrows),
        'different_tables':sum(r['different'] for r in allrows),'tasks_with_raw_differences':sum(s['different_tables']>0 for s in summaries),
        'raw_write_syntax_steps':len(writes),'unresolved_script_calls':len(unresolved),'tasks_summary':summaries,
        'scope':'Table names, ordered column names/types and row counts; no cell-value/content comparison, no cause or correctness judgment.'})


if __name__=='__main__':main()
