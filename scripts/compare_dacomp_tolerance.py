"""Recompare report 004/005 values under L0-L3; never execute agent SQL."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

import duckdb
from compare_dacomp_staging import fingerprint, schema
from dacomp_tolerance import compare_python, compare_sql

ROOT=Path(__file__).resolve().parents[1]
PYTHON=Path('/home/katherine/dac/.venv-openhands/bin/python')


def save(path,value):
    temporary=path.with_suffix(path.suffix+'.pending')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temporary.replace(path)


def jobs_for(scope,task):
    filename=f"{'004_staging' if scope=='staging' else '005_cs'}_{task}.json"
    path=ROOT/'records'/filename;source=json.loads(path.read_text());jobs=[]
    for table in source['tables']:
        if scope=='cs' and not(table['prediction']['exists'] and table['gold']['exists'] and table['current_pred_execution']):continue
        jobs.append({'scope':scope,'task':task,'table':table['table'],'schema':'staging' if scope=='staging' else table['actual_schema'],
                     'prediction_database':source['prediction_database'] if scope=='staging' else source['private_node_results'],
                     'gold_database':source['gold_database'],'baseline_record':str(path),'baseline':table})
    return jobs


def selection():
    jobs=[]
    for scope,prefix in [('staging','004_staging'),('cs','005_cs')]:
        for path in sorted((ROOT/'records').glob(prefix+'_impl-*.json')):
            jobs.extend(jobs_for(scope,path.stem[-8:]))
    return jobs


def first_level(levels,field):
    return next((x['level'] for x in levels if x[field] is True),None if all(x[field] is None for x in levels) else '仍不匹配')


def anchor_l0(record,rechecked_official=None):
    """Keep the requested official L0 anchor separately from exact tuple equality."""
    if 'l0_exact_row_tuple_match' in record:return
    exact=record['levels'][0]['whole_match'];official=record['baseline_l0_whole_match']
    record['l0_exact_row_tuple_match']=exact
    record['l0_exact_tuple_agrees_with_original_official']=exact==official if exact is not None else None
    if exact is not None and exact!=official and rechecked_official is None:
        suite=Path('/home/katherine/dac/benchmarks/DAComp-code/dacomp-de/evaluation_suite')
        sys.path.insert(0,str(suite))
        from utils import CoreAccuracyEvaluator
        prior=json.loads(Path(record['baseline_record']).read_text())
        old=next(t for t in prior['tables'] if t['table']==record['table'])
        config={'layers':{record['layer']:{'tables':{record['table']:{'compare_cols':old['official_compare_cols_configured']}}}}}
        rechecked_official=CoreAccuracyEvaluator(Path(record['prediction_database']),Path(record['gold_database']),config).compare_table(record['layer'],record['table'])
    record['l0_readonly_official_recheck']=rechecked_official
    record['l0_whole_reproduced']=(rechecked_official==official if exact!=official else True) if exact is not None else None
    if exact is not None:record['levels'][0]['whole_match']=official
    record['whole_match_level']=first_level(record['levels'],'whole_match')


def compare_one(job,pred,gold):
    old=job['baseline'];table=job['table'];layer=job['schema'];columns=old['official_compare_cols_available'];keys=old['alignment']['columns']
    pm,gm=schema(pred,table,layer),schema(gold,table,layer)
    base={'scope':job['scope'],'task':job['task'],'layer':layer,'table':table,'baseline_record':job['baseline_record'],
          'prediction_database':job['prediction_database'],'gold_database':job['gold_database'],
          'comparison_columns':columns,'comparison_columns_outside_official_config':old['columns_outside_official_comparison'],
          'baseline_prediction_rows':old['prediction']['row_count'],'baseline_gold_rows':old['gold']['row_count'],
          'baseline_row_delta':old['row_count_delta_pred_minus_gold'],'baseline_alignment':old['alignment'],
          'baseline_l0_whole_match':old['official_current_match'],'baseline_l0_mismatching_official_columns':old['mismatching_official_columns'],
          'current_prediction':pm,'current_gold':gm,'input_row_counts_match_baseline':pm['row_count']==old['prediction']['row_count'] and gm['row_count']==old['gold']['row_count']}
    if not pm['exists'] or not gm['exists'] or not columns or not keys:
        result={'engine':None,'levels':[{'level':f'L{i}','keyed_match':None,'whole_match':None} for i in range(4)],'current_key_statistics':None,'l3_column_differences':None}
        status='unavailable_missing_table_or_columns'
    else:
        status='compared'
        cells=(pm['row_count']+gm['row_count'])*len(set(keys+columns))
        if cells<=600000:
            result=compare_python(pred,gold,table,layer,columns,keys)
        else:
            result=compare_sql(job['prediction_database'],job['gold_database'],table,layer,columns,keys,pm['row_count'],gm['row_count'],ROOT/'data/007_tolerance_scratch'/job['scope']/job['task'],old['alignment'])
    base.update(result)
    base['comparison_status']=status
    anchor_l0(base)
    base['keyed_match_level']=first_level(result['levels'],'keyed_match')
    base['whole_match_level']=first_level(result['levels'],'whole_match')
    base['keyed_availability']='no_shared_keys' if status=='compared' and not result['current_key_statistics']['shared_keys'] else 'comparable' if status=='compared' else status
    stats=result['current_key_statistics']
    base['key_statistics_match_baseline']=all(v==old['alignment'].get(k) for k,v in stats.items()) if stats else None
    diffs=result['l3_column_differences']
    base['l3_inconsistent_columns']=[c for c in diffs if not c['marginal_multisets_equal']] if diffs is not None else None
    base['l3_value_difference_columns']=[c for c in diffs if c['mismatch_rows_or_minimum_pairs']>0] if diffs is not None else None
    base['l3_keyed_rows_differ_with_equal_column_marginals']=not result['levels'][3]['keyed_match'] and all(c['marginal_multisets_equal'] for c in diffs) if diffs is not None else None
    return base


def worker(scope,task):
    jobs=jobs_for(scope,task)
    if not jobs:return
    with duckdb.connect(jobs[0]['prediction_database'],read_only=True) as pred,duckdb.connect(jobs[0]['gold_database'],read_only=True) as gold:
        result={'scope':scope,'task':task,'started_at_utc':datetime.now(timezone.utc).isoformat(),'tables':[]}
        for job in jobs:
            result['tables'].append(compare_one(job,pred,gold))
            r=result['tables'][-1]
            print(f"{scope} {task} {job['table']}: keyed={r['keyed_match_level']}, whole={r['whole_match_level']}",flush=True)
        result['finished_at_utc']=datetime.now(timezone.utc).isoformat()
    save(ROOT/f'records/007_tolerance_{scope}_{task}.json',result)


def summarize(jobs):
    groups=sorted({(j['scope'],j['task']) for j in jobs},key=lambda x:(x[0]!='staging',x[1]))
    records=[]
    for s,task in groups:
        path=ROOT/f'records/007_tolerance_{s}_{task}.json';document=json.loads(path.read_text())
        for record in document['tables']:anchor_l0(record)
        save(path,document);records.extend(document['tables'])
    with (ROOT/'records/007_tolerance_tables.jsonl').open('w') as stream:
        for r in records:stream.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
    rows=[]
    for r in records:
        a=r['baseline_alignment']
        rows.append({'scope':r['scope'],'task':r['task'],'layer':r['layer'],'table':r['table'],
                     'keyed_level':r['keyed_match_level'] or '不可比较','whole_level':r['whole_match_level'] or '不可比较',
                     'keyed_availability':r['keyed_availability'],'pred_rows':r['baseline_prediction_rows'],'gold_rows':r['baseline_gold_rows'],
                     'row_delta':r['baseline_row_delta'],'key_columns':';'.join(a['columns']),'pred_only_keys':a.get('pred_only_keys'),
                     'gold_only_keys':a.get('gold_only_keys'),'shared_keys':a.get('shared_keys'),'shared_nonunique_groups':a.get('shared_nonunique_key_groups'),
                     'l3_columns':json.dumps(r['l3_inconsistent_columns'],ensure_ascii=False,separators=(',',':')),
                     'baseline_l0_whole':r['baseline_l0_whole_match'],'l0_reproduced':r['l0_whole_reproduced']})
    with (ROOT/'records/007_tolerance_tables.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    overview={'created_at_utc':datetime.now(timezone.utc).isoformat(),'tables':len(records),'python':sys.version.split()[0],'duckdb':duckdb.__version__,
              'scopes':{s:{'tables':sum(r['scope']==s for r in records),
                            'keyed_levels':dict(Counter(r['keyed_match_level'] or '不可比较' for r in records if r['scope']==s)),
                            'whole_levels':dict(Counter(r['whole_match_level'] or '不可比较' for r in records if r['scope']==s)),
                            'keyed_availability':dict(Counter(r['keyed_availability'] for r in records if r['scope']==s))} for s in ('staging','cs')},
              'baseline_discrepancies':[{'scope':r['scope'],'task':r['task'],'table':r['table'],'rows':r['input_row_counts_match_baseline'],'keys':r['key_statistics_match_baseline'],'l0':r['l0_whole_reproduced']} for r in records if not r['input_row_counts_match_baseline'] or r['key_statistics_match_baseline'] is False or r['l0_whole_reproduced'] is False],
              'l0_tuple_vs_official_discrepancies':[{'scope':r['scope'],'task':r['task'],'table':r['table'],'official':r['baseline_l0_whole_match'],'exact_row_tuple':r['l0_exact_row_tuple_match'],'readonly_official_recheck':r['l0_readonly_official_recheck']} for r in records if r['l0_exact_tuple_agrees_with_original_official'] is False],
              'engines':dict(Counter(r['engine'] for r in records)),
              'keyed_joint_mismatch_with_equal_l3_marginals':sum(r['l3_keyed_rows_differ_with_equal_column_marginals'] is True for r in records),
              'agent_or_node_sql_executions':0,'rounding':'decimal ROUND_HALF_UP (negative ties away from zero); no binary float conversion',
              'date_policy':'strict ISO date/datetime; keep represented date, discard time; no slash-date or Unix-epoch inference',
              'key_policy':'fixed L0-normalized report 004/005 key columns; exact row multisets within shared keys; no matching claim for zero shared keys',
              'whole_policy':'L0 keeps the original official decision; L1-L3 require equal row counts and exact normalized row-tuple multisets on the original available official compare columns'}
    save(ROOT/'records/007_tolerance_summary.json',overview)
    print(json.dumps(overview,ensure_ascii=False),flush=True)


def main():
    jobs=selection();assert Counter(j['scope'] for j in jobs)=={'staging':176,'cs':155}
    save(ROOT/'records/007_selection.json',[{k:v for k,v in j.items() if k!='baseline'} for j in jobs])
    paths={Path(j[k]) for j in jobs for k in ('baseline_record','prediction_database','gold_database')}
    paths.add(Path('/home/katherine/dac/benchmarks/DAComp-code/dacomp-de/evaluation_suite/utils.py'))
    integrity=ROOT/'records/007_input_integrity.json'
    print('Hashing read-only source files',flush=True)
    current={str(p):fingerprint(p) for p in sorted(paths)}
    before=json.loads(integrity.read_text())['before'] if integrity.exists() else current
    if current!=before:raise RuntimeError('Inputs changed from the saved checkpoint')
    save(integrity,{'before':before,'after':None,'unchanged':None,'files_checked':len(before)})
    groups=sorted({(j['scope'],j['task']) for j in jobs},key=lambda x:(x[0]!='staging',x[1]))
    def run(group):
        scope,task=group;target=ROOT/f'records/007_tolerance_{scope}_{task}.json'
        if target.exists():return {'scope':scope,'task':task,'reused_completed':True}
        command=[str(PYTHON),str(Path(__file__).resolve()),'--worker-scope',scope,'--task',task]
        with (ROOT/f'records/007_execution_{scope}_{task}.log').open('w') as stream:
            r=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=10800,env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
        if r.returncode:raise RuntimeError(f'{group} failed; read its execution log')
        return {'scope':scope,'task':task,'command':command,'returncode':r.returncode}
    executions=[]
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(run,g) for g in groups]
            for f in as_completed(futures):
                r=f.result();executions.append(r);save(ROOT/'records/007_execution.json',executions)
                print('Completed '+r['scope']+' '+r['task'],flush=True)
        summarize(jobs)
    finally:
        after={str(p):fingerprint(p) for p in sorted(paths)}
        save(integrity,{'before':before,'after':after,'unchanged':before==after,'files_checked':len(before)})
        if before!=after:raise RuntimeError('A read-only input changed')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--worker-scope',choices=['staging','cs']);parser.add_argument('--task');args=parser.parse_args()
    if args.worker_scope:worker(args.worker_scope,args.task)
    else:main()
