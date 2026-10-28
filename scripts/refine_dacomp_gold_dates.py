"""Focused supplementary gold-only checks; merge after the first batch has ended."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from complete_dacomp_comparisons import ROOT,RECORDS,PROJECT,PYTHON,save,stamp


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--merge',action='store_true');args=parser.parse_args()
    if args.merge:
        for path in sorted(RECORDS.glob('010_refinement_impl-*.json')):
            refinement=json.loads(path.read_text());task=refinement['task'];target=RECORDS/f'010_verification_{task}.json'
            original=json.loads(target.read_text());by_path={r['sql_path']:r for r in refinement['tables']}
            if str(path) in original.get('supplementary_replays',[]):continue
            preliminary=[]
            for i,row in enumerate(original['tables']):
                if row['sql_path'] not in by_path:continue
                raw=Path(row['sql_path']).read_bytes()
                import hashlib
                raw_hash=hashlib.sha256(raw).hexdigest()
                for attempt in row['attempts']:
                    if attempt['original_sql_sha256']!=raw_hash:
                        attempt['only_runtime_spans_changed']=False
                        attempt['preliminary_run_limit']='read_text normalized original CRLF; raw-byte-preserving replay supersedes this attempt'
                preliminary.append(row)
                original['tables'][i]=by_path[row['sql_path']]
            save(RECORDS/f'010_preliminary_{task}.json',{'task':task,'excluded_from_final_verification_counts':True,
                'reason':'superseded by stronger content date and/or CRLF-preserving execution','tables':preliminary})
            original.setdefault('supplementary_replays',[]).append(str(path));save(target,original)
        print('Supplementary results merged; preliminary attempts retained separately');return
    sys.path.insert(0,str(PROJECT/'src'))
    from safe_env import scrubbed_env
    specs=[('impl-011',None,'2025-10-13'),('impl-015',None,'2025-10-13'),('impl-019','stg_apple_store__app_session_daily','2025-10-15')]
    for task,table in [('impl-004','stg_salesforce__opportunity'),('impl-022','recharge__customer_details'),('impl-030','int_zuora__invoice_base')]:
        source=RECORDS/f'010_verification_{task}.json'
        if not source.exists():continue
        row=next(r for r in json.loads(source.read_text())['tables'] if r['table']==table)
        import hashlib
        raw_hash=hashlib.sha256(Path(row['sql_path']).read_bytes()).hexdigest()
        if all(a['original_sql_sha256']==raw_hash for a in row['attempts']):continue
        day=(row['validated_dates']+row['date_only_validated_dates']+row['initial_candidate_dates'])[0]
        specs.append((task,table,day))
    execution=json.loads((RECORDS/'010_additional_execution.json').read_text()) if (RECORDS/'010_additional_execution.json').exists() else []
    for task,table,day in specs:
        destination=RECORDS/f'010_refinement_{task}.json'
        if destination.exists():continue
        work=ROOT/'data/010_gold_refinement'/task;attempt=1
        while work.exists():work=ROOT/'data/010_gold_refinement'/f'{task}_attempt_{attempt:02d}';attempt+=1
        work.mkdir(parents=True);(work/'.tmp').mkdir()
        command=[shutil.which('bwrap'),'--ro-bind','/','/','--tmpfs','/home/katherine','--ro-bind',str(PROJECT),str(PROJECT),
            '--ro-bind',str(ROOT),str(ROOT),'--bind',str(work),str(work),'--bind',str(work/'.tmp'),'/tmp','--unshare-pid',
            '--proc','/proc','--dev','/dev','--unshare-net','--die-with-parent','--chdir',str(work),'--',str(PYTHON),'-B',
            str(ROOT/'scripts/verify_dacomp_gold_dates.py'),'--worker',task,'--case',str(work),'--candidate-date',day]
        if table:command.extend(['--only-table',table])
        environment=scrubbed_env();environment.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'data/005_tools'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        with (RECORDS/f'010_refinement_{task}.log').open('w') as log:result=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=14400)
        execution.append({'task':task,'table':table,'candidate_date':day,'command':command,'returncode':result.returncode})
        save(RECORDS/'010_additional_execution.json',execution)
        if result.returncode:raise RuntimeError('Supplementary gold replay did not finish')
        save(destination,json.loads((work/'results.json').read_text()));print(task,'supplement completed',flush=True)


if __name__=='__main__':main()
