"""Task 011: freeze agent clock tokens and replay single nodes on private inputs."""

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

import duckdb
import sqlglot
from sqlglot import exp
from sqlglot.lineage import lineage

from compare_dacomp_staging import fingerprint, quote, schema
from compare_dacomp_tolerance import first_level
from complete_dacomp_comparisons import ROOT, PROJECT, RECORDS, PYTHON, SUITE, CONFIG, save, stamp
from dacomp_gold_clock import freeze_sql, runtime_tokens
from dacomp_sql_diff import adaptive_alignment
from dacomp_tolerance import compare_python, compare_sql
from reconcile_dacomp_scope import key, jsonl


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def select():
    statuses={key(r['task'],r['layer'],r['table']):r for r in jsonl(RECORDS/'009_corrected_statuses.jsonl')}
    baseline={key(r['task'],r['layer'],r['table']):(r,source) for source in ('007','009')
              for r in jsonl(RECORDS/f'{source}_tolerance_tables.jsonl')}
    verified={key(r['task'],r['layer'],r['table']):r for r in jsonl(RECORDS/'010_table_verification.jsonl')}
    dates={r['task']:r for r in json.loads((RECORDS/'010_task_summary.json').read_text())}
    access={r['task'].removeprefix('dacomp-de-'):r for r in json.loads((RECORDS/'003_dacomp_source_access.json').read_text())['tasks']}
    rows=[]
    for scan in jsonl(RECORDS/'008_table_scan.jsonl'):
        identity=key(scan['task'],scan['layer'],scan['table'])
        if statuses[identity]['status']!='待标注' or not all(scan['time_dependencies'][s]['appears'] for s in ('agent_sql','gold_sql')):continue
        assert all(any(h['context']=='code' for h in scan['time_dependencies'][s]['hits']) for s in ('agent_sql','gold_sql'))
        old,source=baseline[identity];gold=verified[identity];task=scan['task']
        taskdates=dates[task]
        days=taskdates['inferred_content_supported_candidates'] or taskdates['all_successful_trial_dates']
        assert days and len(scan['agent_sql'])==1
        original=Path(scan['agent_sql'][0]['path']);raw=original.read_bytes().decode('utf-8')
        assert runtime_tokens(raw),original
        details_path=Path(old['baseline_record'])
        details=json.loads(details_path.read_text())
        detail=next(t for t in details['tables'] if key(task,t.get('layer',old['layer']),t['table'])==identity)
        before={
            'source_record':f'records/{source}_tolerance_tables.jsonl',
            'source_table_record':str(details_path),
            'prediction_rows':old['baseline_prediction_rows'],'gold_rows':old['baseline_gold_rows'],
            'row_count_delta_pred_minus_gold':old['baseline_row_delta'],
            'key_statistics':old['current_key_statistics'],
            'alignment':old['baseline_alignment'],
            'levels':old['levels'],'whole_match_level':old['whole_match_level'],
            'keyed_match_level':old['keyed_match_level'],
            'l0_column_differences':[{k:v for k,v in c.items() if k!='examples'} for c in detail['column_differences'] if c['column'] in old['comparison_columns']],
            'l3_column_differences':old['l3_column_differences'],
            'numbers_copied_without_recalculation':True,
        }
        rows.append({
            'task':task,'layer':scan['layer'],'table':scan['table'],'comparison_schema':old['layer'],
            'scope':'staging' if scan['layer']=='staging' else 'cs',
            'comparison_columns':old['comparison_columns'],'key_columns':old['baseline_alignment']['columns'],
            'agent_sql_path':str(original),'agent_sql_sha256':digest(raw),
            'agent_runtime_function_names':sorted({r['function_name'] for r in freeze_sql(raw,days[0],original)[1]}),
            'gold_sql_path':gold['sql_path'],'gold_database':gold['gold_database'],
            'initial_database':next(v['path'] for v in access[task]['database_checks'] if v['kind']=='initial'),
            'retained_agent_database':scan['inventory_sources']['retained_database'],
            'original_sources':[s for f in scan['agent_sql'] for s in f.get('sources',[])],
            'dates':days,'date_selection_source':'records/010_task_summary.json',
            'date_selection_policy':'content-supported task candidate' if taskdates['inferred_content_supported_candidates'] else 'every all_successful_trial_dates value, including dates compatible with only some gold nodes',
            'task_shared_compatible_dates_010':taskdates['shared_successful_trial_dates'],
            'gold_verification_010':gold['verification'],
            'gold_verified_dates_010':gold['validated_dates'],
            'gold_date_only_dates_010':gold['date_only_validated_dates'],
            'gold_verification_source':'records/010_table_verification.jsonl',
            'status_009':statuses[identity]['status'],'status_modified':False,'before':before,
        })
    return rows


def prepare():
    rows=select()
    save(RECORDS/'011_selection.json',{'selected_at':stamp(),'expected_by_user':122,'actual':len(rows),
        'expected_count_matches':len(rows)==122,'tasks':len({r['task'] for r in rows}),
        'planned_attempts':sum(len(r['dates']) for r in rows),
        'by_gold_verification':dict(Counter(r['gold_verification_010'] for r in rows)),
        'absent_from_scope_among_5_ambiguous_tasks':['impl-009'],'tables':rows})
    path=RECORDS/'011_input_before.json'
    if not path.exists():
        files={Path(p) for p in json.loads((RECORDS/'010_input_before.json').read_text())['files']}
        for prefix in ('004_','005_','006_','007_','008_','009_','010_'):
            files.update(RECORDS.glob(prefix+'*'));files.update((ROOT/'notes').glob(prefix+'*'))
        files.update([CONFIG,SUITE/'utils.py',PROJECT/'src/safe_env.py',PROJECT/'src/de_gold_dependencies.py'])
        for row in rows:
            files.update(Path(row[k]) for k in ('agent_sql_path','gold_sql_path','gold_database','initial_database','retained_agent_database'))
        print('Fingerprinting',len(files),'original inputs',flush=True)
        save(path,{'started_at':stamp(),'files':{str(p):fingerprint(p) for p in sorted(files)}})
    print('Selected',len(rows),'tables /',sum(len(r['dates']) for r in rows),'node executions',flush=True)
    return rows


def connect(path,work,source=None):
    con=duckdb.connect(str(path));con.execute("SET memory_limit='768MB'; SET threads=2")
    con.execute("SET temp_directory='"+str(work/'spill').replace("'","''")+"'")
    if source:con.execute("ATTACH '"+str(source).replace("'","''")+"' AS source (READ_ONLY)")
    return con


def output_clock_columns(raw,connection,table,layer,output_names=None):
    """SQLGlot value lineage: reachable projection expressions, not filter-only clocks."""
    ast=sqlglot.parse_one(raw,read='duckdb')
    database_schema=defaultdict(dict)
    for s,t,c,kind in connection.execute('SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE table_catalog=current_database() ORDER BY ordinal_position').fetchall():
        database_schema[s].setdefault(t,{})[c]=kind
    outputs=output_names or [r[0] for r in connection.execute('DESCRIBE SELECT * FROM '+quote(layer)+'.'+quote(table)).fetchall()]
    clock=[];unresolved=[]
    for index,name in enumerate(outputs):
        try:
            if len(ast.selects)==len(outputs) and not isinstance(ast.selects[index],(exp.Alias,exp.Column,exp.Star)):
                # Analysis-only alias for an unaliased expression whose DuckDB
                # output name differs from SQLGlot's generated name. Never execute it.
                analysis=ast.copy();synthetic=f'__clock_output_{index}'
                analysis.set('expressions',[exp.alias_(p.copy(),synthetic,quoted=True) if i==index else p.copy() for i,p in enumerate(analysis.expressions)])
                tree=lineage(synthetic,analysis,schema=dict(database_schema),dialect='duckdb')
            else:tree=lineage(name,ast,schema=dict(database_schema),dialect='duckdb')
            hits=[]
            for node in tree.walk():
                expression=node.expression.sql(dialect='duckdb')
                if runtime_tokens(expression):hits.append({'node':node.name,'expression_sql':expression})
            if hits:clock.append({'column':name,'lineage_clock_expressions':hits})
        except Exception as error:
            unresolved.append({'column':name,'exception_type':type(error).__name__,'message':str(error)})
    return {'method':'SQLGlot output value lineage through local CTEs/subqueries; filter-only clocks do not imply every output value depends on time',
            'runtime_output_columns':clock,'unresolved_outputs':unresolved}


def degeneracy(pred,gold,table,layer,lineage_result):
    def profile(con,column):
        relation=quote(layer)+'.'+quote(table);c=quote(column)
        total,nonnull,distinct=con.execute(f'SELECT count(*),count({c}),count(DISTINCT {c}) FROM {relation}').fetchone()
        value=con.execute(f'SELECT cast({c} AS VARCHAR) FROM {relation} WHERE {c} IS NOT NULL LIMIT 1').fetchone() if distinct==1 else None
        return {'rows':total,'sql_null_rows':total-nonnull,'nonnull_distinct_values':distinct,
                'all_null':total>0 and nonnull==0,'single_nonnull_value':total>0 and nonnull==total and distinct==1,
                'single_value':value[0] if value else None}
    pcount=schema(pred,table,layer)['row_count'];gcount=schema(gold,table,layer)['row_count']
    result={'both_zero_rows':pcount==gcount==0,'clock_output_columns':[],'unresolved_clock_output_lineage':lineage_result['unresolved_outputs']}
    goldcols={c['name'].lower() for c in schema(gold,table,layer)['columns']}
    for item in lineage_result['runtime_output_columns']:
        name=item['column']
        if name.lower() not in goldcols:continue
        p,g=profile(pred,name),profile(gold,name)
        # Mixed NULL/non-NULL columns with one non-NULL value are separately described,
        # but are not a whole column with a single value.
        flag=(p['all_null'] or p['single_nonnull_value']) and (g['all_null'] or g['single_nonnull_value'])
        result['clock_output_columns'].append({**item,'prediction':p,'gold':g,'both_all_null_or_single_value':flag})
    result['clock_output_degeneracy']=any(c['both_all_null_or_single_value'] for c in result['clock_output_columns'])
    result['flagged']=result['both_zero_rows'] or result['clock_output_degeneracy']
    return result


def compare(snapshot,gold_path,row,work):
    table,layer,cols,keys=row['table'],row['comparison_schema'],row['comparison_columns'],row['key_columns']
    with duckdb.connect(str(snapshot),read_only=True) as pred,duckdb.connect(str(gold_path),read_only=True) as gold:
        pm,gm=schema(pred,table,layer),schema(gold,table,layer)
        result={'prediction':pm,'gold':gm,'row_count_delta_pred_minus_gold':pm['row_count']-gm['row_count'] if pm['exists'] and gm['exists'] else None}
        if not pm['exists'] or not gm['exists']:
            return {**result,'comparison_status':'missing_relation'}
        pnames={c['name'].lower() for c in pm['columns']};gnames={c['name'].lower() for c in gm['columns']}
        missing=[c for c in dict.fromkeys(keys+cols) if c.lower() not in pnames or c.lower() not in gnames]
        if missing:return {**result,'comparison_status':'missing_comparison_columns','missing_columns':missing}
        cells=(pm['row_count']+gm['row_count'])*len(set(keys+cols))
        if cells<=600000:values=compare_python(pred,gold,table,layer,cols,keys)
        else:values=compare_sql(str(snapshot),str(gold_path),table,layer,cols,keys,pm['row_count'],gm['row_count'],work/'tolerance_scratch',row['before']['alignment'])
        # Force precisely the historical key columns; do not select a new key after alignment.
        alignment,diffs=adaptive_alignment(pred,gold,table,list(dict.fromkeys(keys+cols)),{'primary_key':keys},cols,layer,layer)
        assert alignment['columns']==keys
        result.update(values,alignment=alignment,l0_column_differences=[{k:v for k,v in c.items() if k!='examples'} for c in diffs if c['column'] in cols],comparison_status='compared')
        for k,v in values['current_key_statistics'].items():assert alignment[k]==v,(k,v,alignment[k])
        result['l0_exact_row_tuple_match']=values['levels'][0]['whole_match']
        if result['l0_exact_row_tuple_match']:
            official=True
        elif pm['row_count']!=gm['row_count']:
            official=False
        else:
            # Same MD5(CONCAT_WS('|', ...)) as the official evaluator, with spillable
            # aggregation rather than materializing millions of hashes in Python.
            with tempfile.TemporaryDirectory(prefix='official_',dir=work) as directory:
                with duckdb.connect(str(Path(directory)/'official.duckdb')) as scratch:
                    scratch.execute("SET memory_limit='768MB'; SET threads=2")
                    scratch.execute("SET temp_directory='"+str(Path(directory)/'spill').replace("'","''")+"'")
                    expressions=','.join("coalesce(lower(trim(cast("+quote(c)+" as varchar))),'null')" for c in cols)
                    for side,path in [('p',snapshot),('g',gold_path)]:
                        scratch.execute("ATTACH '"+str(path).replace("'","''")+f"' AS {side}source (READ_ONLY)")
                        scratch.execute(f"CREATE TABLE {side} AS SELECT md5(concat_ws('|',{expressions})) rh,count(*) n FROM {side}source.{quote(layer)}.{quote(table)} GROUP BY rh")
                    official=scratch.execute('SELECT count(*)=0 FROM p FULL JOIN g USING(rh) WHERE coalesce(p.n,0)<>coalesce(g.n,0)').fetchone()[0]
        result['l0_official_hash_multiset_match']=official
        result['levels'][0]['whole_match']=official
        result['whole_match_level']=first_level(result['levels'],'whole_match')
        result['keyed_match_level']=first_level(result['levels'],'keyed_match')
        return result


def worker(task,work):
    sys.path.insert(0,str(PROJECT/'src'))
    from de_gold_dependencies import source_dependency
    rows=[r for r in json.loads((RECORDS/'011_selection.json').read_text())['tables'] if r['task']==task]
    gold_path=Path(rows[0]['gold_database']);initial=Path(rows[0]['initial_database'])
    private={scope:work/(scope+'_inputs.duckdb') for scope in {'staging' if r['scope']=='staging' else 'cs' for r in rows}}
    for scope,path in private.items():shutil.copy2(initial if scope=='staging' else gold_path,path);path.chmod(0o600)
    result={'task':task,'started_at':stamp(),'gold_database':str(gold_path),'initial_database':str(initial),'tables':[]}
    for row in rows:
        entry={**row,'attempts':[]};raw=Path(row['agent_sql_path']).read_bytes().decode('utf-8')
        assert digest(raw)==row['agent_sql_sha256']
        roots=[r for r in sqlglot.parse(raw,read='duckdb') if r]
        assert len(roots)==1 and isinstance(roots[0],exp.Query),'Expected one unchanged SELECT body'
        table,layer=row['table'],row['comparison_schema'];relation=quote(layer)+'.'+quote(table)
        hybrid=private[row['scope']];source=source_dependency(initial if row['scope']=='staging' else gold_path)
        for day in row['dates']:
            connection=connect(hybrid,work,source)
            connection.execute("ATTACH '"+str(initial if row['scope']=='staging' else gold_path).replace("'","''")+"' AS reset_reference (READ_ONLY)")
            original_relation=connection.execute('SELECT table_type FROM information_schema.tables WHERE table_catalog=\'reset_reference\' AND table_schema=? AND table_name=?',[layer,table]).fetchone()
            def reset():
                current=connection.execute('SELECT table_type FROM information_schema.tables WHERE table_catalog=current_database() AND table_schema=? AND table_name=?',[layer,table]).fetchone()
                if current:connection.execute(('DROP VIEW ' if current[0]=='VIEW' else 'DROP TABLE ')+relation)
                if original_relation:connection.execute('CREATE TABLE '+relation+' AS SELECT * FROM reset_reference.'+relation)
            frozen,replacements=freeze_sql(raw,day,row['agent_sql_path']);directory=work/'frozen_sql';directory.mkdir(exist_ok=True)
            frozen_path=directory/(digest(frozen)+'.sql');frozen_path.write_bytes(frozen.encode('utf-8'))
            attempt={'candidate_date':day,'started_at':stamp(),'original_sql_sha256':digest(raw),'frozen_sql_sha256':digest(frozen),
                'frozen_sql_path':str(frozen_path),'replacements':replacements,'only_runtime_spans_changed':True,
                'date_in_task_shared_compatible_dates_010':day in row['task_shared_compatible_dates_010'],
                'date_validated_for_this_gold_table_010':day in row['gold_verified_dates_010']+row['gold_date_only_dates_010'],
                'execution_mode':'CREATE OR REPLACE TABLE <target> AS newline + unchanged frozen SELECT body; no official _process_sql trim or schema rewrite',
                'input_policy':'original initial database, no other agent nodes' if row['scope']=='staging' else 'gold private copy; restore only target before and after; all other upstream relations remain gold',
                'clock_assumption':'010 policy: date literals; timestamp 00:00:00 UTC placeholder; unknown historical time and timezone'}
            old_handler=signal.getsignal(signal.SIGALRM)
            def timeout(signum,frame):raise TimeoutError('agent node exceeded 300 seconds')
            try:
                reset();connection.execute('CREATE SCHEMA IF NOT EXISTS '+quote(layer))
                signal.signal(signal.SIGALRM,timeout);signal.alarm(300)
                connection.execute('CREATE OR REPLACE TABLE '+relation+' AS\n'+frozen);signal.alarm(0)
                attempt['executed']=True
                attempt['output_lineage']=output_clock_columns(raw,connection,table,layer)
                connection.close();connection=None
                snapshot=work/(table+'_'+day+'.duckdb')
                with duckdb.connect(str(snapshot)) as output:
                    output.execute("ATTACH '"+str(hybrid).replace("'","''")+"' AS frozen_inputs (READ_ONLY)")
                    output.execute('CREATE SCHEMA IF NOT EXISTS '+quote(layer))
                    output.execute('CREATE TABLE '+relation+' AS SELECT * FROM frozen_inputs.'+relation)
                attempt['prediction_snapshot']=str(snapshot)
                attempt['after']=compare(snapshot,gold_path,row,work)
                with duckdb.connect(str(snapshot),read_only=True) as pred,duckdb.connect(str(gold_path),read_only=True) as gold:
                    attempt['degeneracy']=degeneracy(pred,gold,table,layer,attempt['output_lineage'])
            except Exception as error:
                attempt.update(executed=attempt.get('executed',False),exception_type=type(error).__name__,exception_message=str(error))
            finally:
                signal.alarm(0);signal.signal(signal.SIGALRM,old_handler)
                if connection is None:connection=connect(hybrid,work,source);connection.execute("ATTACH '"+str(initial if row['scope']=='staging' else gold_path).replace("'","''")+"' AS reset_reference (READ_ONLY)")
                reset();connection.close()
            attempt['finished_at']=stamp();entry['attempts'].append(attempt)
            print(task,layer,table,day,'executed='+str(attempt['executed']),'whole='+str(attempt.get('after',{}).get('whole_match_level')),flush=True)
            save(work/'current_table.json',entry)
        result['tables'].append(entry);save(work/'results.json',result)
    result['finished_at']=stamp();save(work/'results.json',result)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true');parser.add_argument('--worker');parser.add_argument('--case',type=Path);parser.add_argument('--jobs',type=int,default=2)
    args=parser.parse_args()
    if args.worker:worker(args.worker,args.case);return
    rows=prepare()
    if args.prepare_only:return
    sys.path.insert(0,str(PROJECT/'src'));from safe_env import scrubbed_env
    def run(task):
        destination=RECORDS/f'011_alignment_{task}.json'
        if destination.exists():return {'task':task,'reused':True,'returncode':0}
        work=ROOT/'data/011_agent_alignment'/task;index=1
        while work.exists():work=ROOT/'data/011_agent_alignment'/f'{task}_attempt_{index:02d}';index+=1
        work.mkdir(parents=True);(work/'.tmp').mkdir()
        command=[shutil.which('bwrap'),'--ro-bind','/','/','--tmpfs','/home/katherine','--ro-bind',str(PROJECT),str(PROJECT),
            '--ro-bind',str(ROOT),str(ROOT),'--bind',str(work),str(work),'--bind',str(work/'.tmp'),'/tmp',
            '--unshare-pid','--proc','/proc','--dev','/dev','--unshare-net','--die-with-parent','--chdir',str(work),
            '--',str(PYTHON),'-B',str(Path(__file__).resolve()),'--worker',task,'--case',str(work)]
        environment=scrubbed_env();environment.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'data/005_tools'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        with (RECORDS/f'011_execution_{task}.log').open('w') as log:done=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=21600)
        if not done.returncode:save(destination,json.loads((work/'results.json').read_text()))
        print(task,'worker finished',done.returncode,flush=True)
        return {'task':task,'returncode':done.returncode,'command':command,'private_directory':str(work)}
    try:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:execution=[f.result() for f in as_completed([pool.submit(run,t) for t in sorted({r['task'] for r in rows})])]
        save(RECORDS/'011_execution.json',execution)
        if any(r['returncode'] for r in execution):raise RuntimeError('011 worker failed; inspect corresponding execution log')
    finally:
        before=json.loads((RECORDS/'011_input_before.json').read_text())['files'];after={p:fingerprint(Path(p)) for p in before}
        changed=[p for p in before if before[p]!=after[p]]
        save(RECORDS/'011_input_integrity.json',{'before':before,'after':after,'changed_files':changed,'all_unchanged':not changed,'finished_at':stamp()})
        assert not changed,changed


if __name__=='__main__':main()
