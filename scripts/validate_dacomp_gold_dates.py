"""Audit every clock replacement and independently replay representative gold nodes."""

import argparse
from collections import Counter
from datetime import date,datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import duckdb

from check_dacomp_constraints import open_readonly
from compare_dacomp_staging import fingerprint,quote
from complete_dacomp_comparisons import ROOT,RECORDS,PROJECT,PYTHON,save,stamp
from dacomp_gold_clock import freeze_sql


def reference_date(value):
    try:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:$|[ t].*)',value):return ('literal',value)
        parsed=date.fromisoformat(value) if len(value)==10 else datetime.fromisoformat(value.replace('z','Z'))
        return ('date',(parsed.date() if isinstance(parsed,datetime) else parsed).isoformat())
    except ValueError:return ('literal',value)


def replay_worker(work):
    sys.path.insert(0,str(PROJECT/'src'))
    from de_gold_dependencies import source_dependency
    selected=json.loads((RECORDS/'010_validation_selection.json').read_text());checks=[]
    for index,item in enumerate(selected):
        row=item['row'];trial=item['attempt'];gold=Path(row['gold_database']);private=work/f'node_{index}.duckdb'
        shutil.copyfile(gold,private);private.chmod(0o600)
        with duckdb.connect(str(private)) as conn:
            conn.execute("SET memory_limit='768MB'; SET threads=2")
            conn.execute("SET temp_directory='"+str(work/'spill').replace("'","''")+"'")
            dependency=source_dependency(gold)
            if dependency:conn.execute("ATTACH '"+str(dependency).replace("'","''")+"' AS source (READ_ONLY)")
            conn.execute("ATTACH '"+str(gold).replace("'","''")+"' AS gold_clock_reference (READ_ONLY)")
            relation=quote(row['layer'] if row['layer'] not in ('mart','marts') else next(t['gold_schema'] for t in json.loads((RECORDS/f'010_plan_{row["task"]}.json').read_text())['tables'] if t['sql_path']==row['sql_path']))+'.'+quote(row['table'])
            existing=conn.execute('SELECT table_type FROM information_schema.tables WHERE table_catalog=current_database() AND table_name=?',[row['table']]).fetchone()
            if existing and existing[0]=='VIEW':conn.execute('DROP VIEW '+relation)
            conn.execute('CREATE OR REPLACE TABLE '+relation+' AS SELECT * FROM gold_clock_reference.'+relation)
            frozen=Path(trial['frozen_sql_path']).read_bytes().decode()
            query=frozen if trial['execution_mode']=='original frozen statements' else 'CREATE OR REPLACE TABLE '+relation+' AS\n'+frozen
            conn.execute(query)
            metadata=conn.execute('DESCRIBE SELECT * FROM gold_clock_reference.'+relation).fetchall()
            columns=[r[0] for r in metadata]
            expressions=','.join("coalesce(lower(trim(cast("+quote(c)+" as varchar))),'null')" for c in columns)
            pred=conn.execute('SELECT '+expressions+' FROM '+relation).fetchall()
            expected=conn.execute('SELECT '+expressions+' FROM gold_clock_reference.'+relation).fetchall()
            l0=Counter(pred)==Counter(expected)
            only=Counter(tuple(reference_date(v) for v in r) for r in pred)==Counter(tuple(reference_date(v) for v in r) for r in expected)
            assert l0==trial['comparison']['l0_full_match'],(row['task'],row['table'],'L0')
            assert only==trial['comparison']['date_only_full_match'],(row['task'],row['table'],'date_only')
            checks.append({'task':row['task'],'table':row['table'],'candidate_date':trial['candidate_date'],
                'independent_gold_replay':True,'reference_l0':l0,'reference_date_only':only,
                'comparison_rows':len(pred),'columns':len(columns),'reference':'independent tuple Counter and ISO date parser; no production comparator/normalizer',
                'duckdb_timezone':conn.execute("SELECT current_setting('TimeZone')").fetchone()[0]})
    save(work/'validation.json',checks)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker',type=Path);args=parser.parse_args()
    if args.worker:replay_worker(args.worker);return
    rows=[json.loads(line) for line in (RECORDS/'010_table_verification.jsonl').read_text().splitlines()]
    plans={t['sql_path']:t for path in RECORDS.glob('010_plan_impl-*.json') for t in json.loads(path.read_text())['tables']}
    assert set(plans)=={r['sql_path'] for r in rows} and len(rows)==303
    audited_attempts=audited_spans=0
    for row in rows:
        source=Path(row['sql_path']);assert source.resolve().is_relative_to(PROJECT/'benchmarks/dacomp-de-gold')
        original=source.read_bytes().decode('utf-8');raw_hash=hashlib.sha256(original.encode()).hexdigest()
        for trial in row['attempts']:
            assert trial['only_runtime_spans_changed'] and trial['source_bytes_preserved']
            assert raw_hash==trial['original_sql_sha256']
            generated,replacements=freeze_sql(original,trial['candidate_date'],source)
            assert replacements==trial['replacements']
            assert hashlib.sha256(generated.encode()).hexdigest()==trial['frozen_sql_sha256']
            assert Path(trial['frozen_sql_path']).read_bytes()==generated.encode()
            audited_attempts+=1;audited_spans+=len(replacements)
        if row['retained_gold_view_has_runtime']:assert row['verification']=='未能验证'
        if row['verification']=='L0整表一致':assert row['validated_dates']
        if row['verification']=='仅日期层面一致':assert not row['validated_dates'] and row['date_only_validated_dates']
    summary=json.loads((RECORDS/'010_summary.json').read_text());counts=Counter(r['verification'] for r in rows)
    assert (counts['L0整表一致'],counts['仅日期层面一致'],counts['未能验证'])==(summary['l0_verified'],summary['date_only_verified'],summary['unverified'])
    chosen=[];used=set()
    labels=[('L0',lambda r:r['verification']=='L0整表一致'),
        ('timestamp_only_date',lambda r:r['verification']=='仅日期层面一致' and r['timestamp_only']),
        ('mixed_date',lambda r:r['verification']=='仅日期层面一致' and not r['timestamp_only']),
        ('unverified_executed',lambda r:r['verification']=='未能验证' and r['gold_exists']),
        ('runtime_view',lambda r:r.get('retained_gold_view_has_runtime'))]
    for label,predicate in labels:
        for row in rows:
            if not predicate(row) or row['sql_path'] in used:continue
            options=[a for a in row['attempts'] if a.get('executed') and 'comparison' in a and max(a['comparison']['gold_rows'],a['comparison']['prediction_rows'])<=2000 and a['comparison']['same_column_names_and_order']]
            if not options:continue
            used.add(row['sql_path']);chosen.append({'label':label,'row':row,'attempt':options[0]});break
    # Include the exclusive calendar endpoint and one raw-CRLF gold statement.
    for task in ('impl-019','impl-030'):
        for row in rows:
            if row['task']!=task or row['sql_path'] in used or not row['gold_exists']:continue
            options=[a for a in row['attempts'] if a.get('executed') and a.get('comparison',{}).get('same_column_names_and_order') and max(a['comparison']['gold_rows'],a['comparison']['prediction_rows'])<=4000]
            if options:used.add(row['sql_path']);chosen.append({'label':task,'row':row,'attempt':options[0]});break
    save(RECORDS/'010_validation_selection.json',chosen)
    sys.path.insert(0,str(PROJECT/'src'));from safe_env import scrubbed_env
    work=ROOT/'data/010_independent_validation';attempt=1
    while work.exists():work=ROOT/f'data/010_independent_validation_{attempt:02d}';attempt+=1
    work.mkdir(parents=True);(work/'.tmp').mkdir()
    command=[shutil.which('bwrap'),'--ro-bind','/','/','--tmpfs','/home/katherine','--ro-bind',str(PROJECT),str(PROJECT),'--ro-bind',str(ROOT),str(ROOT),
        '--bind',str(work),str(work),'--bind',str(work/'.tmp'),'/tmp','--unshare-pid','--proc','/proc','--dev','/dev','--unshare-net','--die-with-parent',
        '--chdir',str(work),'--',str(PYTHON),'-B',str(Path(__file__).resolve()),'--worker',str(work)]
    environment=scrubbed_env();environment.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'data/005_tools'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    with (RECORDS/'010_validation_execution.log').open('w') as log:done=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=3600)
    assert done.returncode==0,'independent gold replay did not finish; see log'
    checks=json.loads((work/'validation.json').read_text())
    before=json.loads((RECORDS/'010_input_before.json').read_text())['files'];after={p:fingerprint(Path(p)) for p in before}
    assert before==after
    prior009=json.loads((RECORDS/'009_input_integrity.json').read_text())['after']
    cross=[p for p in before if p.endswith('.duckdb') and p in prior009]
    assert all(after[p]==prior009[p] for p in cross)
    save(RECORDS/'010_input_integrity.json',{'before':before,'after':after,'all_unchanged':True,'changed_files':[],
        'finished_at':stamp(),'scope':'final check after all supplementary and neighbor-date replays',
        'cross_checked_with_009_original_databases':len(cross)})
    annotations=json.loads((RECORDS/'010_impl002_replay_annotations.json').read_text())
    assert len(annotations)==12 and all(a['official_scoring_match'] is False and a['replay_equal_gold'] and not a['status_modified'] for a in annotations)
    evidence=json.loads((RECORDS/'010_additional_candidate_evidence.json').read_text());probe_checks=[]
    for item in evidence:
        scratch=ROOT/'data/010_probe_validation';scratch.mkdir(exist_ok=True)
        with open_readonly(Path(item['gold_database']),scratch/'spill') as connection:observed=connection.execute(item['probe_sql']).fetchall()
        assert [list(v) for v in observed]==item['observed_values']
        probe_checks.append({'task':item['task'],'candidate_date':item['candidate_date'],'content_probe_reproduced':True})
    save(RECORDS/'010_validation.json',{'passed':True,'gold_SQL_scope_verified':len(rows),'replacement_attempts_audited':audited_attempts,
        'replacement_spans_audited':audited_spans,'unmodified_SQL_bytes_verified':True,
        'independent_gold_replays':checks,'independent_execution_command':command,'additional_content_probes':probe_checks,
        'original_input_files_unchanged':len(before),'original_databases_unchanged':sum(p.endswith('.duckdb') for p in before),
        'old_004_009_records_unchanged':True,'impl002_non_overwriting_annotations_verified':12,
        'six_rule_tests':'records/010_tests.log','agent_SQL_executions':0})
    print('010 validation passed:',audited_attempts,'attempts,',audited_spans,'replacement spans,',len(checks),'independent gold replays')


if __name__=='__main__':main()
