"""Execute only frozen gold SQL nodes, keeping original gold and 004-009 read-only."""

import argparse
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import date,timedelta
import hashlib
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys

import duckdb
import sqlglot
from sqlglot import exp

from compare_dacomp_staging import fingerprint,quote
from complete_dacomp_comparisons import ROOT,RECORDS,PROJECT,PYTHON,save,stamp
from dacomp_gold_clock import DATE_NAMES,freeze_sql,compare_full_rows


def plans():
    return [json.loads(path.read_text()) for path in sorted(RECORDS.glob('010_plan_impl-*.json'))]


def ranked_dates(plan,table,global_strong):
    strong=Counter();other=Counter()
    for evidence in table.get('candidate_evidence',[]):
        target=strong if evidence['status'] in ('direct_projection','series_endpoint') or evidence['basis']=='datediff_days_inverse' else other
        for item in evidence.get('candidate_dates',[]):
            day=item['date']
            if day and '2020-01-01'<=day<='2025-11-28':target[day]+=item['supporting_rows']
    taskstrong=Counter()
    for t in plan['tables']:
        for evidence in t.get('candidate_evidence',[]):
            if evidence['status'] not in ('direct_projection','series_endpoint'):continue
            for item in evidence.get('candidate_dates',[]):
                if item['date'] and item['date']<='2025-11-28':taskstrong[item['date']]+=1
    dated=[];sources={}
    def add(day,reason):
        if day not in dated:dated.append(day);sources[day]=reason
    for day in plan.get('extra_content_supported_candidates',[]):add(day,'additional same-task content inversion; see 010_additional_candidate_evidence.json')
    for day,_ in strong.most_common(3):add(day,'this table: direct clock / calendar / datediff inverse')
    for day,_ in taskstrong.most_common(2):add(day,'same task: directly observed clock or calendar endpoint')
    # Conditional clock projections such as COALESCE(LEAD(...), CURRENT_TIMESTAMP).
    for evidence in table.get('candidate_evidence',[]):
        if evidence['basis']=='maximum_of_runtime_containing_date_projection_candidate':
            for item in evidence.get('candidate_dates',[]):
                if item['date'] and item['date']<='2025-11-28':add(item['date'],'this table: maximum of conditional clock-containing projection')
    for day,_ in other.most_common(1):add(day,'this table: observed retained temporal maximum, candidate only')
    for day,_ in global_strong.most_common(7):add(day,'other scoped tasks: directly observed clock/calendars; search candidate, not an inference for this task')
    if not dated:
        add('2025-10-12','fallback hypothesis within other directly observed scoped dates; not a measured generation date')
    initial=dated[:8]
    center=date.fromisoformat(initial[0])
    fallback=[]
    for delta in (-1,1):
        day=(center+timedelta(days=delta)).isoformat()
        if day not in initial and day<='2025-11-28':fallback.append(day);sources[day]='bounded daily search: primary candidate ±1 day; allows a one-day boundary uncertainty'
    return initial,fallback,sources


def worker(task,work,only_tables=None,explicit_day=None):
    sys.path.insert(0,str(PROJECT/'src'))
    from de_gold_dependencies import source_dependency
    allplans=plans();plan=next(p for p in allplans if p['task']==task)
    global_strong=Counter()
    for p in allplans:
        for t in p['tables']:
            for e in t.get('candidate_evidence',[]):
                if e['status'] in ('direct_projection','series_endpoint'):
                    global_strong.update(c['date'] for c in e.get('candidate_dates',[]) if c['date'] and c['date']<='2025-11-28')
    gold=Path(plan['gold_database']);hybrid=work/'gold_hybrid.duckdb';shutil.copy2(gold,hybrid);hybrid.chmod(0o600)
    result={'task':task,'gold_database':str(gold),'private_hybrid':str(hybrid),'started_at':stamp(),'tables':[]}
    connection=duckdb.connect(str(hybrid));connection.execute("SET memory_limit='768MB'; SET threads=2")
    connection.execute("SET temp_directory='"+str(work/'spill').replace("'","''")+"'")
    dependency=source_dependency(gold)
    if dependency:connection.execute("ATTACH '"+str(dependency).replace("'","''")+"' AS source (READ_ONLY)")
    connection.execute("ATTACH '"+str(gold).replace("'","''")+"' AS gold_clock_reference (READ_ONLY)")

    def restore(entry):
        schema,table=entry['gold_schema'],entry['table'];relation=quote(schema)+'.'+quote(table)
        existing=connection.execute('SELECT table_type FROM information_schema.tables WHERE table_catalog=current_database() AND table_schema=? AND table_name=?',[schema,table]).fetchone()
        if existing and existing[0]=='VIEW':connection.execute('DROP VIEW '+relation)
        connection.execute('CREATE OR REPLACE TABLE '+relation+' AS SELECT * FROM gold_clock_reference.'+relation)
    try:
        for entry in plan['tables']:
            if only_tables and entry['table'] not in only_tables:continue
            initial,fallback,reasons=ranked_dates(plan,entry,global_strong)
            if explicit_day:
                initial,fallback,reasons=[explicit_day],[],{explicit_day:'focused validation of additional directly inferred content date / raw-byte-preserving correction'}
            row={'task':task,'layer':entry['layer'],'table':entry['table'],'sql_path':entry['sql_path'],
                'gold_exists':entry['gold_exists'],'gold_rows':entry['gold_rows'],'runtime_function_names':entry['runtime_function_names'],
                'retained_gold_view_has_runtime':entry.get('retained_gold_view_has_runtime',False),
                'timestamp_only':bool(entry['runtime_function_names']) and not any(n in DATE_NAMES for n in entry['runtime_function_names']),
                'candidate_evidence':entry.get('candidate_evidence',[]),'initial_candidate_dates':initial,'candidate_reasons':reasons,
                'bounded_search_dates':fallback,'bounded_search_rationale':'primary content-supported candidate ±1 day, finite three-day neighborhood; no unrestricted date search',
                'attempts':[],'validated_dates':[],'date_only_validated_dates':[]}
            if not entry['gold_exists']:
                row.update(verification='未能验证',unavailable_reason='gold_relation_missing',date_identification='unavailable')
                result['tables'].append(row);save(work/'results.json',result);continue
            original=Path(entry['sql_path']).read_bytes().decode('utf-8')
            roots=[r for r in sqlglot.parse(original,read='duckdb') if r]
            original_ddl=any(isinstance(r,(exp.Create,exp.Drop,exp.Alter)) for r in roots)
            for stage,dates in [('candidate',initial),('bounded_daily_search',fallback)]:
                if row['validated_dates'] or row['date_only_validated_dates']:break
                for day in dates:
                    restore(entry)
                    frozen,replacements=freeze_sql(original,day,entry['sql_path'])
                    frozen_directory=work/'frozen_sql';frozen_directory.mkdir(exist_ok=True)
                    frozen_path=frozen_directory/(hashlib.sha256(frozen.encode()).hexdigest()+'.sql')
                    frozen_path.write_bytes(frozen.encode())
                    attempt={'candidate_date':day,'search_stage':stage,'replacements':replacements,
                        'original_sql_sha256':hashlib.sha256(original.encode()).hexdigest(),
                        'frozen_sql_sha256':hashlib.sha256(frozen.encode()).hexdigest(),
                        'frozen_sql_path':str(frozen_path),'only_runtime_spans_changed':True,
                        'execution_started':stamp(),'time_of_day_assumption':'00:00:00 UTC placeholder; historical time of day not inferred',
                        'execution_mode':'original frozen statements' if original_ddl else 'CREATE OR REPLACE TABLE <target> AS + original frozen SELECT text'}
                    query=frozen if original_ddl else 'CREATE OR REPLACE TABLE '+quote(entry['gold_schema'])+'.'+quote(entry['table'])+' AS\n'+frozen
                    old_handler=signal.getsignal(signal.SIGALRM)
                    def timeout(signum,frame):raise TimeoutError('gold node exceeded 300 seconds')
                    signal.signal(signal.SIGALRM,timeout);signal.alarm(300)
                    try:
                        connection.execute(query);signal.alarm(0)
                        attempt['executed']=True
                        comparison=compare_full_rows(connection,entry['gold_schema'],entry['table'],entry['gold_schema'],[c['name'] for c in entry['columns']],work/'comparison')
                        attempt['comparison']=comparison
                        if comparison['l0_full_match']:row['validated_dates'].append(day)
                        elif comparison['date_only_full_match']:row['date_only_validated_dates'].append(day)
                    except Exception as error:
                        attempt.update(executed=False,exception_type=type(error).__name__,exception_message=str(error))
                    finally:signal.alarm(0);signal.signal(signal.SIGALRM,old_handler)
                    attempt['execution_finished']=stamp();row['attempts'].append(attempt)
                    print(task,entry['table'],day,'L0='+str(attempt.get('comparison',{}).get('l0_full_match')),'date_only='+str(attempt.get('comparison',{}).get('date_only_full_match')),flush=True)
                    save(work/'current_attempt.json',{'task':task,'entry':row})
                    if row['validated_dates'] or row['date_only_validated_dates']:break
                    if not attempt['executed'] and attempt.get('exception_type') in ('BinderException','ParserException','CatalogException'):
                        row['remaining_dates_not_executed_reason']='same gold schema and SQL body bind/parse failure; candidate date cannot rename missing columns/tables'
                        break
                if row.get('remaining_dates_not_executed_reason'):break
            if entry.get('retained_gold_view_has_runtime'):
                row.update(verification='未能验证',unavailable_reason='retained_gold_is_runtime_view_not_a_frozen_historical_table',
                           current_view_matches_do_not_establish_historical_generation_date=True)
            elif row['validated_dates']:row['verification']='L0整表一致'
            elif row['date_only_validated_dates']:row['verification']='仅日期层面一致'
            else:row['verification']='未能验证'
            own_anchors=[e for e in row['candidate_evidence'] if e.get('status') in ('direct_projection','series_endpoint') or e['basis']=='datediff_days_inverse']
            row['date_identification']='content_clock_anchor_with_replay' if own_anchors and row['verification']!='未能验证' else 'compatible_candidate_only_no_unique_date_claim' if row['verification']!='未能验证' else 'unavailable'
            row['empty_output_does_not_identify_date']=entry['gold_rows']==0
            restore(entry);result['tables'].append(row);save(work/'results.json',result)
    finally:connection.close()
    result['finished_at']=stamp();save(work/'results.json',result)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker');parser.add_argument('--case',type=Path);parser.add_argument('--jobs',type=int,default=2)
    parser.add_argument('--only-table',action='append');parser.add_argument('--candidate-date');args=parser.parse_args()
    if args.worker:worker(args.worker,args.case,args.only_table,args.candidate_date);return
    sys.path.insert(0,str(PROJECT/'src'))
    from safe_env import scrubbed_env
    before=json.loads((RECORDS/'010_input_before.json').read_text())['files']
    def run(plan):
        task=plan['task'];destination=RECORDS/f'010_verification_{task}.json'
        if destination.exists():return {'task':task,'reused':True,'returncode':0}
        directory=ROOT/'data/010_gold_replay'/task;attempt=1
        while directory.exists():directory=ROOT/'data/010_gold_replay'/f'{task}_attempt_{attempt:02d}';attempt+=1
        directory.mkdir(parents=True);(directory/'.tmp').mkdir()
        command=[shutil.which('bwrap'),'--ro-bind','/','/','--tmpfs','/home/katherine','--ro-bind',str(PROJECT),str(PROJECT),
            '--ro-bind',str(ROOT),str(ROOT),'--bind',str(directory),str(directory),'--bind',str(directory/'.tmp'),'/tmp',
            '--unshare-pid','--proc','/proc','--dev','/dev','--unshare-net','--die-with-parent','--chdir',str(directory),'--',
            str(PYTHON),'-B',str(Path(__file__).resolve()),'--worker',task,'--case',str(directory)]
        environment=scrubbed_env();environment.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'data/005_tools'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        with (RECORDS/f'010_execution_{task}.log').open('w') as log:result=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=14400)
        if result.returncode==0:save(destination,json.loads((directory/'results.json').read_text()))
        print(task,'finished',result.returncode,flush=True)
        return {'task':task,'command':command,'returncode':result.returncode,'private_directory':str(directory)}
    try:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:execution=[f.result() for f in as_completed([pool.submit(run,p) for p in plans()])]
        save(RECORDS/'010_execution.json',execution)
        if any(e['returncode'] for e in execution):raise RuntimeError('Some gold verification workers did not complete')
    finally:
        after={p:fingerprint(Path(p)) for p in before};changed=[p for p in before if before[p]!=after[p]]
        save(RECORDS/'010_input_integrity.json',{'before':before,'after':after,'changed_files':changed,'all_unchanged':not changed,'finished_at':stamp()})
        assert not changed,changed


if __name__=='__main__':main()
