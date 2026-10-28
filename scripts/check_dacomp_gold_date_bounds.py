"""Gold-only neighbor-date trials to distinguish compatible and identified days."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed

from complete_dacomp_comparisons import ROOT,RECORDS,PROJECT,PYTHON,save


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--complete-candidate-coverage',action='store_true');args=parser.parse_args()
    sys.path.insert(0,str(PROJECT/'src'))
    from safe_env import scrubbed_env
    jobs=[(task,day) for task in ('impl-009','impl-022','impl-025','impl-030') for day in ('2025-10-12','2025-10-13')]
    jobs.extend([('impl-028','2024-01-29'),('impl-028','2024-01-31')])
    jobs.extend(('impl-023',day) for day in ('2025-10-16','2025-10-17','2025-10-18'))
    jobs=[(task,day,None) for task,day in jobs]
    if args.complete_candidate_coverage:
        rows=[json.loads(line) for line in (RECORDS/'010_table_verification.jsonl').read_text().splitlines()]
        summaries=json.loads((RECORDS/'010_task_summary.json').read_text());jobs=[]
        for summary in summaries:
            if not summary['inferred_content_supported_candidates']:continue
            day=summary['inferred_content_supported_candidates'][0]
            tables=[r['table'] for r in rows if r['task']==summary['task'] and r['gold_exists'] and not any(a['candidate_date']==day for a in r['attempts'])]
            if tables:jobs.append((summary['task'],day,tables))
    def run(task,day,tables):
        name=f'{task}_{day}';prefix='010_common_day' if args.complete_candidate_coverage else '010_boundary_trials'
        destination=RECORDS/f'{prefix}_{name}.json'
        if destination.exists():return {'task':task,'date':day,'reused':True,'returncode':0}
        work=ROOT/('data/010_common_day_replays' if args.complete_candidate_coverage else 'data/010_boundary_replays')/name;work.mkdir(parents=True,exist_ok=False);(work/'.tmp').mkdir()
        command=[shutil.which('bwrap'),'--ro-bind','/','/','--tmpfs','/home/katherine','--ro-bind',str(PROJECT),str(PROJECT),
            '--ro-bind',str(ROOT),str(ROOT),'--bind',str(work),str(work),'--bind',str(work/'.tmp'),'/tmp','--unshare-pid',
            '--proc','/proc','--dev','/dev','--unshare-net','--die-with-parent','--chdir',str(work),'--',str(PYTHON),'-B',
            str(ROOT/'scripts/verify_dacomp_gold_dates.py'),'--worker',task,'--case',str(work),'--candidate-date',day]
        for table in tables or []:command.extend(['--only-table',table])
        environment=scrubbed_env();environment.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'data/005_tools'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        with (RECORDS/f'{prefix}_{name}.log').open('w') as log:result=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=7200)
        if result.returncode:raise RuntimeError('Gold neighbor trial did not finish: '+name)
        value=json.loads((work/'results.json').read_text());value['date_trial_purpose']='finite neighbor dates for identifiability; no prior status changes';save(destination,value)
        print(name,'completed',flush=True)
        return {'task':task,'date':day,'tables':tables,'command':command,'returncode':result.returncode}
    with ThreadPoolExecutor(max_workers=2) as pool:execution=[f.result() for f in as_completed([pool.submit(run,*job) for job in jobs])]
    save(RECORDS/('010_common_day_execution.json' if args.complete_candidate_coverage else '010_boundary_execution.json'),execution)


if __name__=='__main__':main()
