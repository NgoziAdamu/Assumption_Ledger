"""Run the task 008 inventory and observational scans without executing agent SQL."""

import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile

import duckdb

from check_dacomp_constraints import open_readonly, raw_dependency, save
from compare_dacomp_staging import fingerprint
from dacomp_trace_scan import (canonical_source, column_contract, contract_index, contract_sources,
                              layer_key, profile_table, protect_constant_values, runtime_hits, sql_scan, table_key)

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path('/home/katherine/dac/.venv-openhands/bin/python')
ARCHIVE = ROOT / 'traces/dacomp_deimpl_prev.tar.gz'
RECORDS = ROOT / 'records'
STATUS_PENDING = '待标注'


def info(number):
    task = f'impl-{number:03d}'
    previous = json.loads((RECORDS / f'006_contract_{task}.json').read_text())
    return {'number':number,'task':task,'agent_database':previous['agent_database'], 'gold_database':previous['gold_database'],
            'contract':previous['contract']['path'], 'agent_directory':str(Path(previous['agent_database']).parent),
            'gold_directory':str(Path(previous['gold_database']).parent)}


def inputs():
    paths = {ARCHIVE, ROOT/'AGENTS.md'}
    for number in range(1,31):
        case = info(number)
        paths.add(Path(case['contract']))
        for side in ('agent','gold'):
            db = Path(case[side+'_database'])
            paths.add(db)
            dependency = raw_dependency(db)
            if dependency:
                paths.add(dependency)
            paths.update(Path(case[side+'_directory']).joinpath('sql').rglob('*.sql'))
            if db.with_suffix(db.suffix+'.wal').exists():
                paths.add(db.with_suffix(db.suffix+'.wal'))
        if number==2:
            paths.add(Path(case['agent_directory'])/'run.py')
            paths.add(Path(case['agent_directory'])/'config/layer_dependencies.yaml')
    for prefix in ('004_', '005_', '006_', '007_'):
        paths.update(RECORDS.glob(prefix+'*'))
        paths.update((ROOT/'notes').glob(prefix+'*'))
    return sorted(paths)


def status_for(task, key, gold_exists, tolerance, cs_records, failed_sets):
    original_004 = f'records/004_staging_{task}.json'
    original_005 = f'records/005_cs_{task}.json'
    if not (ROOT/original_005).is_file():
        original_005='records/005_cs_selection.json'
    original_007 = 'records/007_tolerance_tables.jsonl'
    prior = cs_records.get((task,*key))
    relaxed = tolerance.get((task,*key))
    evidence = {'gold_table_exists_in_original_gold':gold_exists, 'whole_level_007':relaxed['whole_match_level'] if relaxed else None,
        '007_present':relaxed is not None,'004_failed_set_member':(task,*key) in failed_sets['004'],
        '005_failed_set_member':(task,*key) in failed_sets['005'],
        '005_current_pred_execution':prior.get('current_pred_execution') if prior else None,
        'status_sources':[]}
    if not gold_exists or prior and not prior['gold']['exists']:
        status = '不可评估'
        evidence['status_sources'].append({'record':original_005 if prior and not prior['gold']['exists'] else 'original_gold_database_information_schema',
                                           'rule':'gold target missing under original comparison name' if prior else 'gold table missing'})
    elif prior and not prior['current_pred_execution']:
        status = '不可评估'
        evidence['status_sources'].append({'record':original_005,'rule':'current_pred_execution is false'})
    elif relaxed:
        level = relaxed['whole_match_level']
        status = STATUS_PENDING if level in ('仍不匹配','L3') else '格式差异' if level in ('L1','L2') else '官方判为通过' if level == 'L0' else '不可评估'
        evidence['status_sources'].append({'record':original_007,'scope':relaxed['scope'],'rule':'whole_match_level', 'value':level,
                                           '007_prediction_database':relaxed['prediction_database']})
    else:
        status = '官方判为通过'
        evidence['status_sources'].append({'records':[original_004,original_005],
            'rule':'outside 004/005 failure sets, as requested; not a new evaluation'})
    evidence['status'] = status
    return evidence


def old_indices():
    tolerance = {}
    for line in (RECORDS/'007_tolerance_tables.jsonl').read_text().splitlines():
        row = json.loads(line)
        tolerance[(row['task'],*table_key(row['layer'],row['table']))] = row
    cs, failed = {}, {'004':set(),'005':set()}
    for prefix in ('004_staging','005_cs'):
        for path in RECORDS.glob(prefix+'_impl-*.json'):
            record = json.loads(path.read_text())
            task = record['task']
            for row in record['tables']:
                layer = 'staging' if prefix.startswith('004') else row['actual_schema']
                key = (task,*table_key(layer,row['table']))
                failed[prefix[:3]].add(key)
                if prefix.startswith('005'):
                    cs[key] = row
    return tolerance, cs, failed


def sql_paths(directory):
    index = defaultdict(list)
    for path in sorted((Path(directory)/'sql').rglob('*.sql')):
        layer = path.relative_to(Path(directory)/'sql').parts[0]
        index[table_key(layer,path.stem)].append(path)
    return dict(index)


def delivery_names(case, agentsql, goldsql, contracts):
    """Apply the literal filename-to-target rule verified in the Pendo runner."""
    aliases={};evidence=[]
    if case['number']==2:
        import yaml
        runner=Path(case['agent_directory'])/'run.py'
        text=runner.read_text();lines=text.splitlines()
        assert "if table_name.startswith('pendo__'):" in text and "file_name = table_name[7:] + '.sql'" in text
        config=Path(case['agent_directory'])/'config/layer_dependencies.yaml'
        configured=yaml.safe_load(config.read_text())['layers']['marts']['tables']
        for name in configured:
            if name.startswith('pendo__'):
                old=('marts',name[7:]);new=('marts',name)
                if old in agentsql:
                    aliases[new]=old
        for collection in (agentsql,goldsql,contracts):
            for new,old in aliases.items():
                if old in collection:collection[new]=collection.pop(old)
        evidence=[{'path':str(runner),'line':i+1,'original_text':line} for i,line in enumerate(lines) if "table_name.startswith('pendo__')" in line or "file_name = table_name[7:]" in line]
        evidence.append({'path':str(config),'basis':'explicit marts target table list'})
    return aliases,evidence


def worker(number,reuse_output=False):
    case = info(number)
    task = case['task']
    scratch = ROOT/'data/008_scan_scratch'/task
    scratch.mkdir(parents=True,exist_ok=True)
    contracts, parse_mode = contract_index(case['contract'])
    agentsql, goldsql = sql_paths(case['agent_directory']), sql_paths(case['gold_directory'])
    aliases,mapping_evidence=delivery_names(case,agentsql,goldsql,contracts)
    tolerance, cs_records, failed = old_indices()
    result = {**case,'contract_parse_mode':parse_mode,'delivery_name_mapping_evidence':mapping_evidence,
              'tables':[], 'started_at_utc':datetime.now(timezone.utc).isoformat()}
    old_path=RECORDS/f'008_scan_{task}.json'
    retained={(r['layer'],r['table']):r['output'] for r in json.loads(old_path.read_text())['tables']} if reuse_output else {}
    with open_readonly(Path(case['agent_database']),scratch/'agent') as agent, open_readonly(Path(case['gold_database']),scratch/'gold') as gold:
        actual = {table_key(s,n):(s,n,t) for s,n,t in agent.execute("SELECT table_schema,table_name,table_type FROM information_schema.tables WHERE table_catalog=current_database() AND table_schema NOT IN ('raw','information_schema','pg_catalog')").fetchall()}
        gold_actual = {table_key(s,n):(s,n) for s,n in gold.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_catalog=current_database()").fetchall()}
        dbcolumns = defaultdict(list)
        for s,n,c in agent.execute('SELECT table_schema,table_name,column_name FROM information_schema.columns WHERE table_catalog=current_database() ORDER BY table_schema,table_name,ordinal_position').fetchall():
            dbcolumns[canonical_source(s+'.'+n)].append(c)
        keys = sorted(set(actual)|set(agentsql))
        result['inventory_counts'] = {'retained_output_tables':len(actual),'final_sql_files':sum(map(len,agentsql.values())),
            'union_table_targets':len(keys), 'database_only_targets':[list(k) for k in set(actual)-set(agentsql)],
            'sql_only_targets':[list(k) for k in set(agentsql)-set(actual)],
            'contract_only_not_delivered':[list(k) for k in set(contracts)-set(keys)]}
        for key in keys:
            layer, name = key
            blocks = contracts.get(key,[])
            comparison_key=aliases.get(key,key)
            state = status_for(task,comparison_key,key in gold_actual,tolerance,cs_records,failed)
            state['comparison_lookup_layer'],state['comparison_lookup_table']=comparison_key
            state['actual_gold_relation_exists']=key in gold_actual
            agent_scans = [sql_scan(path,dbcolumns) for path in agentsql.get(key,[])]
            gold_time = [{'path':str(path),'hits':runtime_hits(path.read_text(),path,sql=True)} for path in goldsql.get(key,[])]
            contract_time = [h for block in blocks for h in runtime_hits(block['original_text'],block['path'],block['start_line'])]
            specified = contract_sources(blocks)
            actual_sources = sorted({s['canonical'] for scan in agent_scans if scan['sources'] is not None for s in scan['sources']})
            parsed = bool(agent_scans) and all(s['status']=='parsed' for s in agent_scans)
            sources_complete = parsed and not any(s.get('unresolved_source_expressions') for s in agent_scans)
            source_comparison = {'contract':specified, 'agent_direct_read_sources':actual_sources,
                'scope':'direct physical relation references through reachable local CTE/subqueries; no transitive expansion through other output tables or stored views',
                'complete':sources_complete,
                'specified_but_not_read':sorted(set(specified['canonical_names'])-set(actual_sources)) if specified['status']=='specified' and sources_complete else None,
                'read_but_not_specified':sorted(set(actual_sources)-set(specified['canonical_names'])) if specified['status']=='specified' and sources_complete else None}
            if key in retained:
                output=retained[key]
            elif key in actual:
                schema,table,table_type = actual[key]
                try:
                    output = profile_table(agent,schema,table,blocks)
                    output['actual_schema'],output['actual_table'],output['relation_type'] = schema,table,table_type
                except Exception as error:
                    output = {'status':'query_unavailable','exists':True,'row_count':None,'error':str(error),
                              'zero_rows':None,'all_null_columns':None,'constant_nonnull_columns':None,'equal_column_groups':None}
            else:
                output = {'status':'table_missing','exists':False,'row_count':None,'zero_rows':None,
                          'all_null_columns':None,'constant_nonnull_columns':None,'equal_column_groups':None}
            protect_constant_values(output)
            for scan in agent_scans:
                if scan['status']=='parsed' and output['status']=='checked' and len(scan['outputs'])==len(output['columns']):
                    for ordinal,(projection,column) in enumerate(zip(scan['outputs'],output['columns']),1):
                        projection['sql_projection_name']=projection['name']
                        projection['name']=column['name']
                        projection['retained_output_ordinal']=ordinal
            row = {'task':task,'layer':layer,'table':name,'logical_contract_table':comparison_key[1],
                'delivery_name_mapping_evidence':mapping_evidence if key in aliases else [],
                'inventory_sources':{'retained_database':case['agent_database'],
                'present_in_database':key in actual,'agent_final_sql_files':[str(p) for p in agentsql.get(key,[])]},
                'status_007':state,'contract':{'path':case['contract'],'blocks':[{k:v for k,v in b.items() if k not in ('specification','columns')} for b in blocks]},
                'output':output,'agent_sql':agent_scans,'source_comparison':source_comparison,
                'time_dependencies':{'agent_sql':{'available':bool(agent_scans),'appears':any(s['runtime_hits'] for s in agent_scans),
                    'hits':[h for s in agent_scans for h in s['runtime_hits']]},
                    'gold_sql':{'available':bool(gold_time),'appears':any(s['hits'] for s in gold_time),'hits':[h for s in gold_time for h in s['hits']],
                                'paths':[s['path'] for s in gold_time]},
                    'contract':{'available':bool(blocks),'appears':bool(contract_time),'hits':contract_time}}}
            result['tables'].append(row)
            print(task,layer,name,'rows='+str(output['row_count']),'status='+state['status'],flush=True)
    result['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    save(RECORDS/f'008_scan_{task}.json',result)


KEYWORDS = ['简化','占位','默认','空表','跳过','模拟','simplif','placeholder','default','empty','stub','mock','dummy','skip','fallback','NULL']
KEYWORD_PATTERN = re.compile('|'.join(re.escape(k) for k in KEYWORDS),re.I)


def json_strings(text):
    """Yield decoded JSON text fields with exact original token offsets and paths."""
    decoder = json.JSONDecoder()
    def whitespace(position):
        while position < len(text) and text[position].isspace():position+=1
        return position
    def value(position,path):
        position=whitespace(position)
        if text[position]=='{':
            position=whitespace(position+1)
            while text[position]!='}':
                key,end=decoder.raw_decode(text,position);position=whitespace(end)
                assert text[position]==':'
                position=yield from value(position+1,path+[key]);position=whitespace(position)
                if text[position]==',':position=whitespace(position+1)
                else:break
            return position+1
        if text[position]=='[':
            position=whitespace(position+1);index=0
            while text[position]!=']':
                position=yield from value(position,path+[index]);index+=1;position=whitespace(position)
                if text[position]==',':position=whitespace(position+1)
                else:break
            return position+1
        decoded,end=decoder.raw_decode(text,position)
        if isinstance(decoded,str):yield path,decoded,position,end
        return end
    yield from value(0,[])


def sentence_units(text):
    offset=0
    for line in text.splitlines(keepends=True):
        # Preserve original text; periods inside names/decimals are not boundaries.
        for match in re.finditer(r'.+?(?:[。！？]|[.!?](?=\s|$)|$)',line.rstrip('\r\n')):
            yield match.group(),offset+match.start(),offset+match.end()
        offset+=len(line)


def excerpt_archive(rows):
    table_names=defaultdict(set)
    table_aliases=defaultdict(lambda:defaultdict(set))
    for row in rows:
        for name in (row['table'],row.get('logical_contract_table',row['table'])):
            table_names[row['task']].add(name)
            table_aliases[row['task']][name].add(row['table'])
    excerpts, inventory = [], []
    with tarfile.open(ARCHIVE,'r:gz') as archive:
        members=archive.getmembers()
        for number in range(1,31):
            task=f'impl-{number:03d}'
            prefix=f'dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/dacomp-de-{task}/'
            selected=[m for m in members if m.isfile() and m.name.startswith(prefix) and Path(m.name).name in ('result.md','result.json')]
            inventory.append({'task':task,'result_md_present':any(m.name.endswith('/result.md') for m in selected),
                'result_json_present':any(m.name.endswith('/result.json') for m in selected),'paths':[m.name for m in selected]})
            name_regex=re.compile(r'(?<![A-Za-z0-9_])(?:'+ '|'.join(re.escape(n) for n in sorted(table_names[task],key=len,reverse=True))+r')(?![A-Za-z0-9_])',re.I)
            for member in selected:
                original=archive.extractfile(member).read().decode()
                line_starts=[0]+[m.end() for m in re.finditer('\n',original)]
                obj=json.loads(original) if member.name.endswith('.json') else None
                fields=list(json_strings(original)) if obj is not None else [([],original,0,len(original))]
                for trail,value,start,end in fields:
                    if member.name.endswith('.md'):origin='result_md_final_report'
                    elif trail and trail[0]=='instruction':origin='task_instruction_not_agent_report'
                    elif trail and trail[0]=='run_py_output':origin='execution_output_not_agent_report'
                    elif len(trail)>=3 and trail[0]=='trajectory':
                        step=obj['trajectory'][trail[1]]
                        origin='assistant_finish' if step.get('action')=='finish' else 'assistant_trajectory' if step.get('role')=='assistant' else 'observation_or_other_trajectory'
                    else:origin='result_json_metadata_or_other'
                    for sentence,first,last in sentence_units(value):
                        matches=list(KEYWORD_PATTERN.finditer(sentence))
                        if not matches:continue
                        matched_names=sorted({m.group().lower() for m in name_regex.finditer(sentence)})
                        names=sorted({target for name in matched_names for target in table_aliases[task][name]})
                        line=bisect_right(line_starts,start) if obj is not None else value.count('\n',0,first)+1
                        excerpts.append({'task':task,'archive':str(ARCHIVE),'archive_member':member.name,
                            'file_line':line,'json_path':trail if obj is not None else None,
                            'json_string_token_start_offset':start if obj is not None else None,
                            'decoded_field_line':value.count('\n',0,first)+1,'decoded_sentence_start_offset':first,'decoded_sentence_end_offset':last,
                            'origin':origin,'original_text':sentence,
                            'keywords':sorted({KEYWORDS[next(i for i,k in enumerate(KEYWORDS) if k.lower()==m.group().lower())] for m in matches},key=KEYWORDS.index),
                            'matched_substrings':[m.group() for m in matches],
                            'table_name_strings_in_sentence':matched_names,
                            'tables_named_in_sentence':names,'association':'explicit_table_name_in_this_sentence' if names else '未指明表'})
    return excerpts,inventory


def flags(row):
    output=row['output'];sql=row['agent_sql'];sources=row['source_comparison'];time=row['time_dependencies']
    checked=output['status']=='checked'
    sql_checked=bool(sql) and all(s['status']=='parsed' for s in sql)
    return {'A1_zero_rows':output.get('zero_rows'),
        'A2_all_null_column':bool(output.get('all_null_columns')) if checked else None,
        'A3_constant_nonnull_column':bool(output.get('constant_nonnull_columns')) if checked else None,
        'A4_equal_columns':bool(output.get('equal_column_groups')) if checked else None,
        'A4_equal_columns_different_description_texts':any(g['has_pair_with_different_explicit_description'] for g in output.get('equal_column_groups') or []) if checked else None,
        'B5_null_literal_output':any(s.get('null_literal_outputs') for s in sql) if sql_checked else None,
        'B6_constant_literal_output':any(s.get('constant_literal_outputs') for s in sql) if sql_checked else None,
        'B7_specified_not_read':bool(sources.get('specified_but_not_read')) if sources['specified_but_not_read'] is not None else None,
        'B7_read_not_specified':bool(sources.get('read_but_not_specified')) if sources['read_but_not_specified'] is not None else None,
        'B8_shared_single_source':bool(row.get('shared_single_source_targets')) if sources['complete'] else None,
        'C9_agent_runtime_text':time['agent_sql']['appears'] if time['agent_sql']['available'] else None,
        'C9_gold_runtime_text':time['gold_sql']['appears'] if time['gold_sql']['available'] else None,
        'C9_contract_runtime_text':time['contract']['appears'] if time['contract']['available'] else None,
        'D10_keyword_in_final_report':bool(row.get('final_report_keyword_excerpt_ids')),
        'D10_keyword_in_any_result_field':bool(row.get('any_result_keyword_excerpt_ids'))}


def summarize():
    tasks=[json.loads((RECORDS/f'008_scan_impl-{n:03d}.json').read_text()) for n in range(1,31)]
    rows=[row for task in tasks for row in task['tables']]
    for row in rows:
        row.setdefault('logical_contract_table',row['table'])
        row.setdefault('delivery_name_mapping_evidence',[])
    groups=defaultdict(list)
    for row in rows:
        sources=row['source_comparison']
        if sources['complete'] and len(sources['agent_direct_read_sources'])==1:
            groups[(row['task'],sources['agent_direct_read_sources'][0])].append(row)
    group_records=[]
    for (task,source),targets in sorted(groups.items()):
        if len(targets)>1:
            targets_named=[r['layer']+'.'+r['table'] for r in targets]
            group_records.append({'task':task,'sole_source':source,'targets':targets_named})
            for row in targets:row['shared_single_source_targets']={'source':source,'targets':targets_named}
    excerpts,report_inventory=excerpt_archive(rows)
    index={(r['task'],r['table']):r for r in rows}
    for i,excerpt in enumerate(excerpts,1):
        excerpt['excerpt_id']=f'008-{i:06d}'
        for table in excerpt['tables_named_in_sentence']:
            row=index[(excerpt['task'],table)]
            row.setdefault('any_result_keyword_excerpt_ids',[]).append(excerpt['excerpt_id'])
            if excerpt['origin'] in ('result_md_final_report','assistant_finish'):
                row.setdefault('final_report_keyword_excerpt_ids',[]).append(excerpt['excerpt_id'])
    for row in rows:row['trace_flags']=flags(row)
    summary={'generated_at_utc':datetime.now(timezone.utc).isoformat(), 'total_tables':len(rows),
        'total_tasks':len(tasks),'status_counts':dict(Counter(r['status_007']['status'] for r in rows)),
        'inventory_by_task':[{'task':t['task'],**t['inventory_counts']} for t in tasks],
        'agent_query_status_counts':dict(Counter(r['output']['status'] for r in rows)),
        'agent_sql_parse_status_counts':dict(Counter(s['status'] for r in rows for s in r['agent_sql'])),
        'contract_missing_tables':[{'task':r['task'],'layer':r['layer'],'table':r['table']} for r in rows if not r['contract']['blocks']],
        'trace_counts':{},'shared_single_source_groups':len(group_records),
        'report_inventory':report_inventory,'excerpt_count':len(excerpts),
        'excerpt_counts_by_origin':dict(Counter(e['origin'] for e in excerpts)),
        'excerpts_without_named_table':sum(not e['tables_named_in_sentence'] for e in excerpts)}
    pending=[r for r in rows if r['status_007']['status']==STATUS_PENDING]
    summary['pending_denominator']=len(pending)
    for flag in rows[0]['trace_flags']:
        summary['trace_counts'][flag]={'pending_tables':sum(r['trace_flags'][flag] is True for r in pending),
            'pending_denominator':len(pending),'all_tables':sum(r['trace_flags'][flag] is True for r in rows),'all_denominator':len(rows),
            'pending_unknown':sum(r['trace_flags'][flag] is None for r in pending),'all_unknown':sum(r['trace_flags'][flag] is None for r in rows)}
    # Keep a single flat table row, with nested evidence encoded as JSON in CSV cells.
    (RECORDS/'008_table_scan.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    columns=['task','layer','table','logical_contract_table','delivery_name_mapping_evidence','status_007','whole_level_007','output_status','row_count']+list(rows[0]['trace_flags'])+['inventory_sources','status_evidence','all_null_columns','constant_nonnull_columns','equal_column_groups','agent_sql','source_comparison','shared_single_source_targets','time_dependencies','contract','final_report_keyword_excerpt_ids','any_result_keyword_excerpt_ids']
    with (RECORDS/'008_table_scan.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns,lineterminator='\n');writer.writeheader()
        for row in rows:
            flat={k:row.get(k) for k in ('task','layer','table','logical_contract_table','delivery_name_mapping_evidence','inventory_sources','agent_sql','source_comparison','time_dependencies','contract')}
            flat.update(status_007=row['status_007']['status'],whole_level_007=row['status_007']['whole_level_007'],status_evidence=row['status_007'],
                        output_status=row['output']['status'],row_count=row['output']['row_count'],**row['trace_flags'])
            for k in ('all_null_columns','constant_nonnull_columns','equal_column_groups'):flat[k]=row['output'].get(k)
            for k in ('shared_single_source_targets','final_report_keyword_excerpt_ids','any_result_keyword_excerpt_ids'):flat[k]=row.get(k)
            writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in flat.items()})
    (RECORDS/'008_keyword_excerpts.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in excerpts))
    save(RECORDS/'008_report_inventory.json',report_inventory)
    save(RECORDS/'008_shared_single_source_groups.json',group_records)
    save(RECORDS/'008_scan_summary.json',summary)
    print(json.dumps({k:summary[k] for k in ('total_tables','pending_denominator','status_counts','trace_counts')},ensure_ascii=False,indent=2))
    return rows,summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker',type=int);parser.add_argument('--jobs',type=int,default=2)
    parser.add_argument('--finalize-only',action='store_true');parser.add_argument('--refresh-static',action='store_true');args=parser.parse_args()
    if args.worker:worker(args.worker,args.refresh_static);return
    if args.finalize_only:summarize();return
    before_path=RECORDS/'008_input_before.json'
    if not before_path.exists():
        files=inputs()
        print('Fingerprinting',len(files),'inputs',flush=True)
        before={str(p):fingerprint(p) for p in files}
        save(before_path,{'started_at_utc':datetime.now(timezone.utc).isoformat(),'files':before})
    else:before=json.loads(before_path.read_text())['files']
    def run(number):
        task=f'impl-{number:03d}'
        if (RECORDS/f'008_scan_{task}.json').exists() and not args.refresh_static:return {'task':task,'resumed':True,'returncode':0}
        with (RECORDS/f"008_execution_{task}{'_static' if args.refresh_static else ''}.log").open('w') as log:
            command=[str(PYTHON),'-B',str(Path(__file__)),'--worker',str(number)]
            if args.refresh_static:command.append('--refresh-static')
            result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        print(task,'finished',result.returncode,flush=True)
        return {'task':task,'returncode':result.returncode,'command':command}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        execution=[f.result() for f in as_completed([pool.submit(run,n) for n in range(1,31)])]
    save(RECORDS/'008_execution.json',execution)
    if any(x['returncode'] for x in execution):raise RuntimeError('Worker failure; inspect 008 execution logs')
    summarize()
    print('Rechecking input fingerprints',flush=True)
    after={p:fingerprint(Path(p)) for p in before}
    changed=[p for p in before if before[p]!=after[p]]
    save(RECORDS/'008_input_integrity.json',{'before':before,'after':after,'changed_files':changed,'all_unchanged':not changed})
    assert not changed,changed


if __name__=='__main__':main()
