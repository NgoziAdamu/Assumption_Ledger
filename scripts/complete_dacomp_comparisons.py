"""Task 009: complete 21 CS targets using gold upstreams on private copies."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import csv
import inspect
import json
from pathlib import Path
import shutil
import subprocess
import sys

import duckdb
import yaml

from compare_dacomp_cs_nodes import RecordingConnection
from compare_dacomp_staging import compare_table, fingerprint, quote
from compare_dacomp_tolerance import anchor_l0, first_level
from dacomp_sql_diff import adaptive_alignment
from dacomp_sql_extract import contract_blocks, key_spec, sql_structure
from dacomp_tolerance import compare_python, compare_sql
from dacomp_trace_scan import canonical_source, runtime_hits, sql_scan

ROOT=Path(__file__).resolve().parents[1]
PROJECT=Path('/home/katherine/dac')
SUITE=PROJECT/'benchmarks/DAComp-code/dacomp-de/evaluation_suite'
CONFIG=SUITE/'evaluation_config_compare.yaml'
REVIEW=PROJECT/'runs/20261025_de_batch_review_02'
RECORDS=ROOT/'records'
PYTHON=PROJECT/'.venv-openhands/bin/python'
WORK=ROOT/'data/009_cs_work'


def save(path,value):
    temporary=path.with_suffix(path.suffix+'.pending')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    temporary.replace(path)


def info(number):
    task=f'impl-{number:03d}';instance=f'dacomp-de-{task}'
    cfg=yaml.safe_load(CONFIG.read_text())['examples'][instance]
    return {'task':task,'number':number,'instance':instance,'config':cfg,
        'prediction_directory':PROJECT/'runs/20261025_de_official_batch_01'/task/'agent'/instance,
        'gold_directory':PROJECT/'benchmarks/dacomp-de-gold'/instance,
        'contract':PROJECT/'benchmarks/dacomp-de'/instance/'docs/data_contract.yaml',
        'score_path':REVIEW/'scoring'/task/'cs/score.json'}


def stamp():
    utc=datetime.now(timezone.utc)
    return {'utc':utc.isoformat(),'Asia/Singapore':utc.astimezone(ZoneInfo('Asia/Singapore')).isoformat()}


def selection():
    selected=[]
    for number in (2,10,12):
        case=info(number);score=json.loads(case['score_path'].read_text())
        wanted=[('marts',name) for name in case['config']['layers']['marts']['tables']] if number==2 else [
            ('sales','hubspot__sales_performance_dashboard'),('sales','hubspot__sales_rep_performance')] if number==10 else [('utils','marketo__calendar_spine')]
        for layer,logical in wanted:
            index,result=next((i,v) for i,v in enumerate(score['partial_evaluation']['layer_results']) if v['layer_name']==layer)
            actual='pendo__'+logical if number==2 else logical
            # The raw score is never replaced by the replay's result.
            selected.append({'task':case['task'],'number':number,'layer':layer,'table':actual,'scoring_table':logical,
                'sql_name':logical,'contract_table':logical,'archived_cs_match':result['comparison_results'].get(logical),
                'archived_pred_execution':result['pred_execution'].get(logical),'archived_gold_execution':result['gold_execution'].get(logical),
                'eligible':result['comparison_results'].get(logical) is False,'score_source':str(case['score_path']),
                'score_json_path':['partial_evaluation','layer_results',index,'comparison_results',logical],
                'score_timestamp':score.get('timestamp')})
    assert len(selected)==21
    return selected


def mapped_config(config,number):
    result=deepcopy(config)
    if number==2:
        result['layers']['marts']['tables']={'pendo__'+name:{**entry,'sql_name':name}
            for name,entry in result['layers']['marts']['tables'].items()}
    return result


def originals():
    files={CONFIG,SUITE/'utils.py',PROJECT/'src/safe_env.py',PROJECT/'src/de_gold_dependencies.py'}
    for number in range(1,31):
        old=json.loads((RECORDS/f'006_contract_impl-{number:03d}.json').read_text())
        files.update(Path(old[k]) for k in ('agent_database','gold_database'))
        files.add(Path(old['contract']['path']))
        for side in ('agent','gold'):
            db=Path(old[side+'_database']);dependency=db.with_name(db.stem+'_start.duckdb')
            if dependency.is_file() and number==13:files.add(dependency)
        score=REVIEW/(f'compatibility/impl-{number:03d}/score.json' if number in (13,19,22) else f'scoring/impl-{number:03d}/cs/score.json')
        files.add(score)
    for number in (2,10,12):
        case=info(number)
        files.add(REVIEW/'scoring'/case['task']/'cfs/score.json')
        for side in ('prediction_directory','gold_directory'):
            files.update((case[side]/'sql').rglob('*.sql'))
        if number==2:
            files.update([case['prediction_directory']/'run.py',case['prediction_directory']/'config/layer_dependencies.yaml'])
    for prefix in ('004_','005_','006_','007_','008_'):
        files.update(RECORDS.glob(prefix+'*'));files.update((ROOT/'notes').glob(prefix+'*'))
    return sorted(files)


def evaluator_evidence():
    sys.path.insert(0,str(SUITE))
    from utils import CSEvaluator,CoreAccuracyEvaluator
    symbols=[(CSEvaluator,name) for name in ('_sql_name_for_table','_read_sql','_resolve_schema_name','_list_tables','_ensure_gold_dependencies','_build_pred_table','evaluate_all_layers')]+[(CoreAccuracyEvaluator,'compare_table')]
    code=[]
    for cls,name in symbols:
        lines,start=inspect.getsourcelines(getattr(cls,name))
        code.append({'path':str(SUITE/'utils.py'),'symbol':cls.__name__+'.'+name,'start_line':start,
                     'end_line':start+len(lines)-1,'original_text':''.join(lines)})
    case=info(2);original=case['config'];mapper=CSEvaluator(case['prediction_directory'],case['gold_directory'],original,original['database_file'])
    with duckdb.connect(str(case['gold_directory']/original['database_file']),read_only=True) as gold:
        schema=mapper._resolve_schema_name(gold,'marts');tables=mapper._list_tables(gold,schema)
        name_checks=[{'scoring_table':name,'official_schema':schema,'official_gold_membership':name in tables,
                      'prefixed_table':'pendo__'+name,'prefixed_gold_membership':'pendo__'+name in tables,
                      'official_sql_name':mapper._sql_name_for_table('marts',name)} for name in original['layers']['marts']['tables']]
    return {'source_sha256':fingerprint(SUITE/'utils.py')['sha256'],'code':code,'impl002_name_checks':name_checks,
        'behavior':'Gold membership and compare_table require the exact configured table name; only mart/marts schema names are resolved. No Pendo table-name prefix fallback is present.',
        'replay_adapter':'In-memory config maps each impl-002 marts target to pendo__<configured name>, preserves compare_cols and weights, and sets sql_name=<configured name>. Original config and SQL remain unchanged.'}


def tolerance(diff,case,snapshot,gold_path,work):
    table,layer=diff['table'],diff['actual_schema'];columns=diff['official_compare_cols_available'];keys=diff['alignment']['columns']
    row={'scope':'cs','task':case['task'],'layer':layer,'table':table,
        'baseline_record':str(RECORDS/f"009_cs_{case['task']}.json"),'prediction_database':str(snapshot),'gold_database':str(gold_path),
        'comparison_columns':columns,'comparison_columns_outside_official_config':diff['columns_outside_official_comparison'],
        'baseline_prediction_rows':diff['prediction']['row_count'],'baseline_gold_rows':diff['gold']['row_count'],
        'baseline_row_delta':diff['row_count_delta_pred_minus_gold'],'baseline_alignment':diff['alignment'],
        'baseline_l0_whole_match':diff['official_current_match'],'baseline_l0_mismatching_official_columns':diff['mismatching_official_columns'],
        'current_prediction':diff['prediction'],'current_gold':diff['gold'],'input_row_counts_match_baseline':True,
        'execution_date':diff['execution_started']['Asia/Singapore'][:10],'execution_started':diff['execution_started'],
        'time_dependencies':diff['time_dependencies'],'run_time_sensitive':diff['run_time_sensitive']}
    if not(diff['current_pred_execution'] and diff['prediction']['exists'] and diff['gold']['exists'] and columns and keys):
        result={'engine':None,'levels':[{'level':f'L{i}','keyed_match':None,'whole_match':None} for i in range(4)],'current_key_statistics':None,'l3_column_differences':None}
        status='unavailable_missing_table_or_columns'
    else:
        cells=(diff['prediction']['row_count']+diff['gold']['row_count'])*len(set(columns+keys))
        if cells<=600000:
            with duckdb.connect(str(snapshot),read_only=True) as pred,duckdb.connect(str(gold_path),read_only=True) as gold:
                result=compare_python(pred,gold,table,layer,columns,keys)
        else:
            result=compare_sql(str(snapshot),str(gold_path),table,layer,columns,keys,
                diff['prediction']['row_count'],diff['gold']['row_count'],work/'tolerance_scratch',diff['alignment'])
        status='compared'
    row.update(result);row['comparison_status']=status
    anchor_l0(row,rechecked_official=diff['official_current_match'])
    row['keyed_match_level']=first_level(row['levels'],'keyed_match')
    row['whole_match_level']=first_level(row['levels'],'whole_match')
    stats=row['current_key_statistics'];diffs=row['l3_column_differences']
    row['keyed_availability']='no_shared_keys' if status=='compared' and not stats['shared_keys'] else 'comparable' if status=='compared' else status
    row['key_statistics_match_baseline']=all(v==diff['alignment'].get(k) for k,v in stats.items()) if stats else None
    row['l3_inconsistent_columns']=[c for c in diffs if not c['marginal_multisets_equal']] if diffs is not None else None
    row['l3_value_difference_columns']=[c for c in diffs if c['mismatch_rows_or_minimum_pairs']>0] if diffs is not None else None
    row['l3_keyed_rows_differ_with_equal_column_marginals']=not row['levels'][3]['keyed_match'] and all(c['marginal_multisets_equal'] for c in diffs) if diffs is not None else None
    return row


def worker(number,work):
    sys.path[:0]=[str(SUITE),str(PROJECT/'src')]
    from utils import CSEvaluator,CoreAccuracyEvaluator
    from de_gold_dependencies import install_source_attachment
    case=info(number);cfg=mapped_config(case['config'],number)
    targets=[r for r in selection() if r['number']==number and r['eligible']]
    old008=[json.loads(line) for line in (RECORDS/'008_table_scan.jsonl').read_text().splitlines()]
    old008={(r['task'],r['layer'],r['table']):r for r in old008}
    gold_path=case['gold_directory']/cfg['database_file'];hybrid=work/'cs_hybrid.duckdb';snapshot=work/'node_results.duckdb'
    shutil.copy2(gold_path,hybrid);hybrid.chmod(0o600)
    class TaskEvaluator(CSEvaluator):pass
    install_source_attachment(TaskEvaluator,gold_path)
    evaluator=TaskEvaluator(case['prediction_directory'],case['gold_directory'],cfg,cfg['database_file'])
    ordered=evaluator._ordered_layers()
    with duckdb.connect(str(gold_path),read_only=True) as gold:
        schemas={layer:evaluator._resolve_schema_name(gold,layer) for layer in ordered}
        available={layer:evaluator._list_tables(gold,schemas[layer]) for layer in ordered}
    result={'task':case['task'],'score_source':str(case['score_path']),'prediction_sql_directory':str(case['prediction_directory']),
        'gold_database':str(gold_path),'private_node_results':str(snapshot),'private_work_directory':str(work),
        'config_mapping_applied':number==2,'original_config':case['config'],'effective_config':cfg,
        'ordered_layers':ordered,'started_at':stamp(),'tables':[],'tolerance_tables':[]}

    def connect():
        connection=duckdb.connect(str(hybrid))
        connection.execute("SET memory_limit='768MB'; SET threads=2")
        connection.execute("SET temp_directory='"+str(work/'spill').replace("'","''")+"'")
        return connection,evaluator._attach_gold_alias(connection)
    connection,alias=connect()
    assert alias
    try:
        for target in targets:
            layer,table=target['layer'],target['table'];schema=schemas[layer]
            path=case['prediction_directory']/'sql'/layer/(target['sql_name']+'.sql')
            raw=evaluator._read_sql(case['prediction_directory'],layer,table)
            assert raw==path.read_text()
            contract=contract_blocks(case['contract'],target['contract_table'])
            scan=sql_scan(path)
            upstream=[]
            for source in scan['sources'] or []:
                parts=source['name'].split('.')
                count=None
                if len(parts)==2 and parts[0] in schemas.values():
                    count=connection.execute('SELECT count(*) FROM '+quote(parts[0])+'.'+quote(parts[1])).fetchone()[0]
                upstream.append({**source,'input_origin':'gold private copy / read-only gold restoration','rows_before_execution':count})
            recorder=RecordingConnection(connection)
            evaluator._ensure_gold_dependencies(recorder,layer,table,alias,schemas,available,ordered)
            restore_errors=list(recorder.errors);recorder.errors.clear()
            # Record after restoration: these are the actual immediate inputs to the node.
            for item in upstream:
                parts=item['name'].split('.')
                if len(parts)==2 and parts[0] in schemas.values():
                    item['rows_after_gold_restore']=connection.execute('SELECT count(*) FROM '+quote(parts[0])+'.'+quote(parts[1])).fetchone()[0]
            start=stamp();sql_clock=connection.execute("SELECT current_date::VARCHAR,current_timestamp::VARCHAR,current_setting('TimeZone')").fetchone()
            ok=evaluator._build_pred_table(recorder,layer,table,schema)
            finish=stamp();build_errors=list(recorder.errors)
            evaluator._detach_gold_alias(connection,alias);connection.close();connection=None
            official=CoreAccuracyEvaluator(hybrid,gold_path,cfg).compare_table(schema,table) if ok else False
            with duckdb.connect(str(hybrid) if ok else ':memory:',read_only=ok) as pred,duckdb.connect(str(gold_path),read_only=True) as gold:
                diff=compare_table(pred,gold,table,cfg['layers'][layer]['tables'][table],key_spec(contract,target['contract_table']),schema,schema,alignment_engine=adaptive_alignment)
            if ok:
                with duckdb.connect(str(snapshot)) as output:
                    output.execute("ATTACH '"+str(hybrid).replace("'","''")+"' AS hybrid (READ_ONLY)")
                    output.execute('CREATE SCHEMA IF NOT EXISTS '+quote(schema))
                    output.execute(f'CREATE TABLE {quote(schema)}.{quote(table)} AS SELECT * FROM hybrid.{quote(schema)}.{quote(table)}')
            prior=old008[(case['task'],layer,table)]
            times=prior['time_dependencies']
            diff.update(target)
            diff.update(actual_schema=schema,current_pred_execution=ok,official_current_match=official,
                dependency_restore_errors=restore_errors,build_errors=build_errors,prediction_unavailable_reason=None if ok else 'official_build_returned_false',
                execution_started=start,execution_finished=finish,
                sql_execution_clock={'current_date':sql_clock[0],'current_timestamp':sql_clock[1],'TimeZone':sql_clock[2]},
                run_time_sensitive=any(h['context']=='code' for h in times['agent_sql']['hits']),
                time_dependencies=times,time_dependency_source='records/008_table_scan.jsonl',
                actual_gold_upstreams=upstream,upstream_row_generators=scan.get('row_generator_expressions',[]),
                dependency_restoration_policy={'ordered_layers':ordered,'all_earlier_configured_layers':ordered[:ordered.index(layer)],
                    'same_layer_peers_restored_from_gold':True,'target_reset_to_gold_between_nodes':True},
                agent_sql={'used_source_paths':[str(path)],'candidate_paths':[str(path)],'raw_text':raw,
                    'official_processed_text':evaluator._process_sql(raw,layer,schema),'structure':sql_structure(raw)},contract=contract)
            result['tables'].append(diff)
            result['tolerance_tables'].append(tolerance(diff,case,snapshot,gold_path,work))
            save(work/'results.json',result)
            level=result['tolerance_tables'][-1]['whole_match_level']
            print(case['task'],layer,table,'executed='+str(ok),'whole='+str(level),flush=True)
            connection,alias=connect()
            evaluator._copy_table_from_gold(connection,schema,table,alias,available[layer])
    finally:
        if connection is not None:evaluator._detach_gold_alias(connection,alias);connection.close()
    result['finished_at']=stamp();save(work/'results.json',result)


def export():
    rows=[];details=[]
    for number in (2,10,12):
        case=info(number);path=RECORDS/f"009_cs_{case['task']}.json"
        value=json.loads(path.read_text());details.extend(value['tables'])
        tolerances=value.pop('tolerance_tables',None)
        if tolerances is None:tolerances=json.loads((RECORDS/f"009_tolerance_cs_{case['task']}.json").read_text())['tables']
        else:save(path,value)
        save(RECORDS/f"009_tolerance_cs_{case['task']}.json",{'scope':'cs','task':case['task'],'tables':tolerances})
        rows.extend(tolerances)
    (RECORDS/'009_tolerance_tables.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    flat=[]
    for r in rows:
        a=r['baseline_alignment']
        flat.append({'scope':r['scope'],'task':r['task'],'layer':r['layer'],'table':r['table'],
            'pred_rows':r['baseline_prediction_rows'],'gold_rows':r['baseline_gold_rows'],'row_delta':r['baseline_row_delta'],
            'key_columns':json.dumps(a['columns'],ensure_ascii=False),'pred_only_keys':a.get('pred_only_keys'),'gold_only_keys':a.get('gold_only_keys'),
            'shared_keys':a.get('shared_keys'),'keyed_level':r['keyed_match_level'] or '不可比较','whole_level':r['whole_match_level'] or '不可比较',
            'l3_columns':json.dumps(r['l3_inconsistent_columns'],ensure_ascii=False),'execution_date':r['execution_date'],
            'run_time_sensitive':r['run_time_sensitive'],'time_dependencies':json.dumps(r['time_dependencies'],ensure_ascii=False)})
    with (RECORDS/'009_tolerance_tables.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(flat[0]),lineterminator='\n');writer.writeheader();writer.writerows(flat)
    save(RECORDS/'009_comparison_summary.json',{'target_count':len(rows),'whole_levels':dict(Counter(r['whole_match_level'] or '不可比较' for r in rows)),
        'keyed_levels':dict(Counter(r['keyed_match_level'] or '不可比较' for r in rows)),
        'runtime_sensitive_targets':sum(r['run_time_sensitive'] for r in rows),
        'executed':sum(r['current_pred_execution'] for r in details),'gold_missing':sum(not r['gold']['exists'] for r in details),
        'official_replay_matches':sum(r['official_current_match'] for r in details),
        'l0_tuple_official_discrepancies':[{'task':r['task'],'table':r['table']} for r in rows if r['l0_exact_tuple_agrees_with_original_official'] is False]})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker',type=int);parser.add_argument('--case',type=Path)
    parser.add_argument('--export-only',action='store_true');args=parser.parse_args()
    if args.worker:worker(args.worker,args.case);return
    if args.export_only:export();return
    sys.path.insert(0,str(PROJECT/'src'))
    from safe_env import scrubbed_env
    snapshot=RECORDS/'009_input_before.json'
    if not snapshot.exists():
        paths=originals();print('Fingerprinting',len(paths),'inputs',flush=True)
        save(snapshot,{'started_at':stamp(),'files':{str(p):fingerprint(p) for p in paths}})
    before=json.loads(snapshot.read_text())['files']
    selected=selection();save(RECORDS/'009_selection.json',selected);save(RECORDS/'009_official_evaluator_evidence.json',evaluator_evidence())
    def run(number):
        task=f'impl-{number:03d}';destination=RECORDS/f'009_cs_{task}.json'
        if destination.exists():return {'task':task,'reused':True,'returncode':0}
        directory=WORK/task;attempt=1
        while directory.exists():directory=WORK/f'{task}_attempt_{attempt:02d}';attempt+=1
        directory.mkdir(parents=True);(directory/'.tmp').mkdir()
        command=[shutil.which('bwrap'),'--ro-bind','/','/','--tmpfs','/home/katherine',
            '--ro-bind',str(PROJECT),str(PROJECT),'--ro-bind',str(ROOT),str(ROOT),'--bind',str(directory),str(directory),
            '--bind',str(directory/'.tmp'),'/tmp','--unshare-pid','--proc','/proc','--dev','/dev','--unshare-net','--die-with-parent',
            '--chdir',str(directory),'--',str(PYTHON),'-B',str(Path(__file__).resolve()),'--worker',str(number),'--case',str(directory)]
        environment=scrubbed_env();environment.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'data/005_tools'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        with (RECORDS/f'009_execution_{task}.log').open('w') as log:
            done=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=7200)
        if not done.returncode:save(destination,json.loads((directory/'results.json').read_text()))
        print(task,'returncode',done.returncode,flush=True)
        return {'task':task,'command':command,'returncode':done.returncode,'private_work_directory':str(directory)}
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            execution=[f.result() for f in as_completed([pool.submit(run,n) for n in (2,10,12)])]
        save(RECORDS/'009_execution.json',execution)
        if any(r['returncode'] for r in execution):raise RuntimeError('A 009 worker failed; see its execution log')
        export()
    finally:
        after={p:fingerprint(Path(p)) for p in before}
        changed=[p for p in before if before[p]!=after[p]]
        save(RECORDS/'009_input_integrity.json',{'before':before,'after':after,'changed_files':changed,'all_unchanged':not changed,'finished_at':stamp()})
        assert not changed,changed


if __name__=='__main__':main()
