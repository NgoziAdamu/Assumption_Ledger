"""Inventory task 010 and infer candidate dates from retained gold content."""

from collections import Counter,defaultdict
from datetime import date,timedelta
import json
from pathlib import Path
import re
import sys

import duckdb
import sqlglot
from sqlglot import exp

from check_dacomp_constraints import open_readonly,raw_dependency
from compare_dacomp_staging import fingerprint,quote
from complete_dacomp_comparisons import ROOT,RECORDS,PROJECT,CONFIG,SUITE,save,stamp
from dacomp_trace_scan import layer_key,runtime_hits,sql_scan
from dacomp_gold_clock import freeze_sql,runtime_tokens


def old_data():
    statuses={(r['task'],r['layer'],r['table']):r for r in map(json.loads,(RECORDS/'009_corrected_statuses.jsonl').read_text().splitlines())}
    tables=list(map(json.loads,(RECORDS/'008_table_scan.jsonl').read_text().splitlines()))
    triggers=[r for r in tables if statuses[(r['task'],r['layer'],r['table'])]['status'] in ('待标注','格式差异') and r['time_dependencies']['gold_sql']['appears']]
    return statuses,tables,triggers


def snapshot():
    target=RECORDS/'010_input_before.json'
    if target.exists():return
    _,_,triggers=old_data();tasks=sorted({r['task'] for r in triggers})
    files={CONFIG,SUITE/'utils.py',PROJECT/'src/de_gold_dependencies.py',PROJECT/'src/safe_env.py'}
    for n in range(1,31):
        case=json.loads((RECORDS/f'006_contract_impl-{n:03d}.json').read_text())
        files.update(Path(case[k]) for k in ('agent_database','gold_database'))
        if n==13:
            for side in ('agent','gold'):
                db=Path(case[side+'_database']);files.add(db.with_name(db.stem+'_start.duckdb'))
        if f'impl-{n:03d}' in tasks:
            base=Path(case['gold_database']).parent
            files.update(p for p in base.rglob('*') if p.is_file() and p.suffix not in ('.duckdb','.pyc'))
    for prefix in ('004_','005_','006_','007_','008_','009_'):
        files.update(RECORDS.glob(prefix+'*'));files.update((ROOT/'notes').glob(prefix+'*'))
    code=PROJECT/'benchmarks/DAComp-code'
    files.update([code/'README.md',code/'dacomp-de/README.md',code/'dacomp-de/evaluation_suite/README.md'])
    save(target,{'started_at':stamp(),'files':{str(p):fingerprint(p) for p in sorted(files)}})


def clock_expression(expression):
    return bool(list(expression.find_all(exp.CurrentDate))) or bool(list(expression.find_all(exp.CurrentTimestamp)))


def direct_offset(expression):
    node=expression
    while isinstance(node,(exp.Cast,exp.TryCast,exp.Paren)):node=node.this
    if isinstance(node,(exp.CurrentDate,exp.CurrentTimestamp)):return 0
    if isinstance(node,(exp.Add,exp.Sub)) and isinstance(node.expression,exp.Interval):
        offset=direct_offset(node.this)
        unit=str(node.expression.args.get('unit','')).lower()
        if offset is not None and unit in ('day','days','week','weeks'):
            try:
                amount=int(node.expression.this.this)*(7 if unit.startswith('week') else 1)
                return offset+(amount if isinstance(node,exp.Add) else -amount)
            except (TypeError,ValueError):pass
    return None


def infer_table(connection,entry,db_columns):
    path=Path(entry['sql_path']);text=path.read_text();scan=sql_scan(path,db_columns)
    entry['sql_scan_status']=scan['status'];entry['direct_gold_sources']=scan.get('sources');entry['candidate_evidence']=[]
    if not entry['gold_exists'] or scan['status']!='parsed':return
    relation=quote(entry['gold_schema'])+'.'+quote(entry['table'])
    columns=entry['columns'];mapping={c['name'].lower():c for c in columns}
    outputs=scan['outputs'] or []
    if len(outputs)==len(columns):
        for item,col in zip(outputs,columns):item['name']=col['name']
    def add_probe(column,formula,basis,expr,confidence='candidate'):
        query=f'SELECT cast(candidate_day as varchar),count(*) n FROM (SELECT {formula} candidate_day FROM {relation}) WHERE candidate_day IS NOT NULL GROUP BY candidate_day ORDER BY n DESC,candidate_day LIMIT 8'
        try:
            values=connection.execute(query).fetchall()
            candidates=[{'date':str(day)[:10],'supporting_rows':count} for day,count in values if re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(day)[:10])]
            entry['candidate_evidence'].append({'table':entry['table'],'schema':entry['gold_schema'],'column':column,'sql_path':str(path),
                'basis':basis,'original_expression':expr,'probe_sql':query,'candidate_dates':candidates,'status':confidence})
        except Exception as error:
            entry['candidate_evidence'].append({'column':column,'basis':basis,'original_expression':expr,'probe_sql':query,'status':'probe_unavailable','message':str(error)})
    seen=set()
    for output in outputs:
        column=output['name'];kind=mapping.get(column.lower(),{}).get('type','')
        for alternative in output['alternatives']:
            expression_text=alternative['expression_sql']
            if (column,expression_text) in seen:continue
            seen.add((column,expression_text))
            try:expression=sqlglot.parse_one(expression_text,read='duckdb')
            except Exception:continue
            if not clock_expression(expression):continue
            offset=direct_offset(expression)
            if offset is not None and ('DATE' in kind or 'TIMESTAMP' in kind):
                add_probe(column,f"try_cast({quote(column)} AS DATE)-INTERVAL '{offset} days'",'direct_clock_projection_inverse',expression_text,'direct_projection')
            for difference in expression.find_all(exp.DateDiff):
                if kind not in ('TINYINT','SMALLINT','INTEGER','BIGINT','HUGEINT','DOUBLE','FLOAT') and not kind.startswith('DECIMAL'):continue
                unit=str(difference.args.get('unit','')).lower()
                finish,start=difference.this,difference.expression
                while isinstance(start,(exp.Cast,exp.TryCast,exp.Paren)):start=start.this
                while isinstance(finish,(exp.Cast,exp.TryCast,exp.Paren)):finish=finish.this
                if unit not in ('day','days'):continue
                if isinstance(finish,(exp.CurrentDate,exp.CurrentTimestamp)) and isinstance(start,exp.Column) and start.name.lower() in mapping:
                    add_probe(column,f"try_cast({quote(mapping[start.name.lower()]['name'])} AS DATE)+try_cast({quote(column)} AS INTEGER)",'datediff_days_inverse',expression_text)
                elif isinstance(start,(exp.CurrentDate,exp.CurrentTimestamp)) and isinstance(finish,exp.Column) and finish.name.lower() in mapping:
                    add_probe(column,f"try_cast({quote(mapping[finish.name.lower()]['name'])} AS DATE)-try_cast({quote(column)} AS INTEGER)",'datediff_days_inverse',expression_text)
            if offset is None and ('DATE' in kind or 'TIMESTAMP' in kind):
                # COALESCE/window/CASE may retain historical values as well as the clock.
                # Its maximum is only a candidate, never asserted to be the bake date.
                query=f'SELECT cast(max({quote(column)}) AS DATE)::VARCHAR FROM {relation}'
                try:value=connection.execute(query).fetchone()[0]
                except Exception:value=None
                if value:entry['candidate_evidence'].append({'table':entry['table'],'schema':entry['gold_schema'],'column':column,'sql_path':str(path),
                    'basis':'maximum_of_runtime_containing_date_projection_candidate','original_expression':expression_text,'probe_sql':query,
                    'candidate_dates':[{'date':value,'supporting_rows':1}],'status':'candidate_not_unique_inference'})
    # Resolve a named CTE endpoint only if it is an explicit, column-free day/week shift.
    try:root=sqlglot.parse_one(text,read='duckdb')
    except Exception:return
    aliases={a.alias.lower():a.this for a in root.find_all(exp.Alias) if a.alias}
    for generator in root.find_all(exp.GenerateSeries):
        endpoint=generator.args.get('end')
        if isinstance(endpoint,exp.Subquery):
            selects=list(endpoint.find_all(exp.Select))
            endpoint=selects[0].expressions[0] if selects and len(selects[0].expressions)==1 else endpoint
        if isinstance(endpoint,exp.Column) and endpoint.name.lower() in aliases:endpoint=aliases[endpoint.name.lower()]
        offset=direct_offset(endpoint) if endpoint else None
        exclusive=bool(generator.args.get('is_end_exclusive'))
        if offset is not None and exclusive:
            step=generator.args.get('step')
            if isinstance(step,exp.Interval) and str(step.args.get('unit','')).lower() in ('day','days'):
                offset-=int(step.this.this)
            else:offset=None
        datecols=[c['name'] for c in columns if c['type']=='DATE' or c['name'].lower() in ('date_day','date','date_month')]
        if offset is not None and len(datecols)==1:
            col=datecols[0];query=f'SELECT cast(max({quote(col)}) AS DATE)::VARCHAR FROM {relation}'
            value=connection.execute(query).fetchone()[0]
            candidate=(date.fromisoformat(value)-timedelta(days=offset)).isoformat() if value else None
            entry['candidate_evidence'].append({'table':entry['table'],'schema':entry['gold_schema'],'column':col,'sql_path':str(path),
                'basis':'calendar_series_endpoint_inverse','original_expression':endpoint.sql(dialect='duckdb'),
                'probe_sql':query,'observed_max_date':value,'endpoint_day_offset':offset,
                'endpoint_is_exclusive':exclusive,
                'candidate_dates':[{'date':candidate,'supporting_rows':1}] if candidate else [],'status':'series_endpoint'})
    if not any(e.get('candidate_dates') for e in entry['candidate_evidence']):
        referenced={c.name.lower() for c in root.find_all(exp.Column)}
        for col in columns:
            if ('DATE' not in col['type'] and 'TIMESTAMP' not in col['type']) or col['name'].lower() not in referenced:continue
            name=col['name'];query=f'SELECT cast(max({quote(name)}) AS DATE)::VARCHAR FROM {relation}'
            try:value=connection.execute(query).fetchone()[0]
            except Exception:value=None
            if value:
                entry['candidate_evidence'].append({'table':entry['table'],'schema':entry['gold_schema'],'column':name,'sql_path':str(path),
                    'basis':'maximum_retained_date_in_runtime_SQL_candidate_only','probe_sql':query,
                    'candidate_dates':[{'date':value,'supporting_rows':1}],
                    'status':'observed_gold_date_candidate_not_a_proven_execution_date'})


def prepare():
    snapshot();statuses,old,triggers=old_data();tasks=sorted({r['task'] for r in triggers})
    plans=[]
    for task in tasks:
        oldcase=json.loads((RECORDS/f'006_contract_{task}.json').read_text())
        db=Path(oldcase['gold_database']);base=db.parent;scratch=ROOT/'data/010_probe_scratch'/task;scratch.mkdir(parents=True,exist_ok=True)
        result={'task':task,'gold_database':str(db),'tables':[],'trigger_tables':[{'layer':r['layer'],'table':r['table'],'status':statuses[task,r['layer'],r['table']]['status']} for r in triggers if r['task']==task]}
        with open_readonly(db,scratch/'spill') as connection:
            actual={(layer_key(s),n.lower()):(s,n) for s,n in connection.execute('SELECT table_schema,table_name FROM information_schema.tables WHERE table_catalog=current_database()').fetchall()}
            dbcols=defaultdict(list);columns=defaultdict(list)
            for s,n,c,t in connection.execute('SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE table_catalog=current_database() ORDER BY table_schema,table_name,ordinal_position').fetchall():
                dbcols[layer_key(s)+'.'+n].append(c);columns[s,n].append({'name':c,'type':t})
            views={(s,n):sql for s,n,sql in connection.execute('SELECT schema_name,view_name,sql FROM duckdb_views() WHERE database_name=current_database() AND NOT internal').fetchall()}
            for path in sorted((base/'sql').rglob('*.sql')):
                text=path.read_text();hits=runtime_hits(text,path,sql=True)
                if not hits:continue
                layer=layer_key(path.relative_to(base/'sql').parts[0]);name=path.stem
                if task=='impl-002' and layer=='marts' and (layer,'pendo__'+name) in actual:name='pendo__'+name
                found=actual.get((layer,name.lower()))
                entry={'task':task,'layer':layer,'table':name,'gold_schema':found[0] if found else layer,'gold_exists':found is not None,
                    'sql_path':str(path),'sql_sha256':fingerprint(path)['sha256'],'runtime_lexical_hits':hits,
                    'runtime_function_occurrences':len(runtime_tokens(text)),
                    'runtime_function_names':sorted({re.sub(r'\s*\(\s*\)$','',m.group()).upper() for m in runtime_tokens(text)}),
                    'columns':columns.get(found,[]) if found else []}
                view_sql=views.get(found,'')
                entry['gold_relation_type']='VIEW' if view_sql else 'BASE TABLE' if found else None
                entry['retained_gold_view_sql']=view_sql or None
                entry['retained_gold_view_has_runtime']=bool(runtime_tokens(view_sql))
                if found:
                    entry['table']=found[1]
                    entry['gold_rows']=connection.execute('SELECT count(*) FROM '+quote(found[0])+'.'+quote(found[1])).fetchone()[0]
                else:entry['gold_rows']=None
                infer_table(connection,entry,dbcols)
                result['tables'].append(entry)
        evidence=[{**e,'date':c['date'],'supporting_rows':c['supporting_rows']} for t in result['tables'] for e in t.get('candidate_evidence',[]) for c in e.get('candidate_dates',[]) if c['date']]
        votes=Counter(e['date'] for e in evidence)
        result['candidate_date_votes']=dict(votes.most_common())
        result['task_candidates']=[d for d,_ in votes.most_common()]
        plans.append(result);save(RECORDS/f'010_plan_{task}.json',result)
        print(task,len(result['tables']),'dates',result['candidate_date_votes'],flush=True)
    save(RECORDS/'010_scope.json',{'tasks':tasks,'trigger_count':len(triggers),'gold_sql_file_count':sum(len(p['tables']) for p in plans),
        'gold_missing_file_targets':sum(not t['gold_exists'] for p in plans for t in p['tables']),
        'policy':'25 tasks triggered by 008 C9 gold SQL and 009 pending/format status; all gold SQL files containing runtime text in each task included; no agent SQL execution'})
    return plans


if __name__=='__main__':prepare()
