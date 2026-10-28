"""Audit 011 substitutions/baselines; independently replay small representative nodes."""

import argparse
from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import duckdb

from align_dacomp_agent_dates import select
from compare_dacomp_staging import fingerprint, quote
from complete_dacomp_comparisons import ROOT, PROJECT, PYTHON, RECORDS, save, stamp
from reconcile_dacomp_scope import jsonl


def forms(value,level):
    if level==0:return value
    if value in ('true','t'):value='1'
    elif value in ('false','f'):value='0'
    if re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:e[+-]?[0-9]+)?',value):
        try:
            with localcontext() as context:
                context.prec=max(80,len(value)+30)
                number=Decimal(value)
                if level>=2:number=number.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
                return ('number',number)
        except InvalidOperation:pass
    if value in ('inf','+inf','infinity','+infinity','-inf','-infinity'):
        return ('number','-infinity' if value.startswith('-') else 'infinity')
    if level>=3 and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}(?:$|[ t].*)',value):
        try:
            parsed=date.fromisoformat(value) if len(value)==10 else datetime.fromisoformat(value.replace('z','Z'))
            return ('day',(parsed.date() if isinstance(parsed,datetime) else parsed).isoformat())
        except ValueError:pass
    return ('string',value)


def independent(connection,reference,entry):
    layer,table,columns,keys=entry['comparison_schema'],entry['table'],entry['comparison_columns'],entry['key_columns']
    names=list(dict.fromkeys(keys+columns));expressions=','.join("coalesce(lower(trim(cast("+quote(c)+" as varchar))),'null')" for c in names)
    rows={s:c.execute('SELECT '+expressions+' FROM '+quote(layer)+'.'+quote(table)).fetchall() for s,c in [('p',connection),('g',reference)]}
    keysides={s:Counter(tuple(r[names.index(k)] for k in keys) for r in rs) for s,rs in rows.items()}
    common=set(keysides['p'])&set(keysides['g']);levels=[];column_counts={}
    for level in range(4):
        weighted={};keyed={}
        for side,rs in rows.items():
            weighted[side]=Counter(tuple(forms(r[names.index(c)],level) for c in columns) for r in rs)
            keyed[side]=Counter((tuple(r[names.index(k)] for k in keys),tuple(forms(r[names.index(c)],level) for c in columns)) for r in rs if tuple(r[names.index(k)] for k in keys) in common)
        whole=weighted['p']==weighted['g']
        if level==0:
            hashed={s:Counter() for s in rows}
            for side,rs in rows.items():
                for r in rs:hashed[side][hashlib.md5('|'.join(r[names.index(c)] for c in columns).encode()).hexdigest()]+=1
            whole=hashed['p']==hashed['g']
        levels.append({'level':f'L{level}','whole_match':whole,'keyed_match':keyed['p']==keyed['g'] if common else None})
        if level in (0,3):
            column_counts[str(level)]={}
            grouped={s:defaultdict(list) for s in rows}
            for side,rs in rows.items():
                for r in rs:
                    k=tuple(r[names.index(c)] for c in keys)
                    if k in common:grouped[side][k].append(r)
            for c in columns:
                mismatch=pu=gu=0
                for k in common:
                    p=Counter(forms(r[names.index(c)],level) for r in grouped['p'][k]);g=Counter(forms(r[names.index(c)],level) for r in grouped['g'][k])
                    pn,gn=sum((p-g).values()),sum((g-p).values());mismatch+=min(pn,gn);pu+=pn;gu+=gn
                column_counts[str(level)][c]={'mismatch_rows_or_minimum_pairs':mismatch,'pred_unmatched_value_occurrences':pu,'gold_unmatched_value_occurrences':gu}
    pk,gk=keysides['p'],keysides['g']
    return {'levels':levels,'column_counts':column_counts,'prediction_rows':len(rows['p']),'gold_rows':len(rows['g']),
            'keys':{'pred_only_keys':len(set(pk)-set(gk)),'gold_only_keys':len(set(gk)-set(pk)),'shared_keys':len(common)}}


def worker(work):
    sys.path.insert(0,str(PROJECT/'src'));from de_gold_dependencies import source_dependency
    samples=json.loads((RECORDS/'011_validation_selection.json').read_text());results=[]
    for i,sample in enumerate(samples):
        entry=sample['entry'];attempt=sample['attempt'];original=Path(entry['initial_database'] if entry['scope']=='staging' else entry['gold_database'])
        private=work/f'replay_{i:02d}.duckdb';shutil.copy2(original,private);private.chmod(0o600)
        with duckdb.connect(str(private)) as connection:
            connection.execute("SET memory_limit='768MB'; SET threads=2")
            source=source_dependency(original)
            if source:connection.execute("ATTACH '"+str(source).replace("'","''")+"' AS source (READ_ONLY)")
            layer,table=entry['comparison_schema'],entry['table'];relation=quote(layer)+'.'+quote(table)
            exists=connection.execute('SELECT table_type FROM information_schema.tables WHERE table_catalog=current_database() AND table_schema=? AND table_name=?',[layer,table]).fetchone()
            if exists:connection.execute(('DROP VIEW ' if exists[0]=='VIEW' else 'DROP TABLE ')+relation)
            connection.execute('CREATE SCHEMA IF NOT EXISTS '+quote(layer))
            frozen=Path(attempt['frozen_sql_path']).read_bytes().decode('utf-8')
            connection.execute('CREATE TABLE '+relation+' AS\n'+frozen)
            with duckdb.connect(entry['gold_database'],read_only=True) as gold:
                measured=independent(connection,gold,entry)
            expected=attempt['after']
            assert measured['levels']==expected['levels'],(entry['table'],'levels',measured['levels'],expected['levels'])
            for k,v in measured['keys'].items():assert v==expected['current_key_statistics'][k]
            for level in (0,3):
                for c in expected[f'l{level}_column_differences'] or []:
                    for k,v in measured['column_counts'][str(level)][c['column']].items():assert c[k]==v,(entry['table'],level,c['column'],k,v,c[k])
            with duckdb.connect(attempt['prediction_snapshot'],read_only=True) as snapshot:
                cols=','.join('cast('+quote(c['name'])+' as varchar)' for c in expected['prediction']['columns'])
                assert Counter(connection.execute('SELECT '+cols+' FROM '+relation).fetchall())==Counter(snapshot.execute('SELECT '+cols+' FROM '+relation).fetchall())
            results.append({'task':entry['task'],'layer':entry['layer'],'table':table,'candidate_date':attempt['candidate_date'],
                'gold_verification_010':entry['gold_verification_010'],'independent_replay_equals_saved_prediction':True,
                'independent_L0_L3_and_column_counts_agree':True,'whole_match_level':expected['whole_match_level']})
    save(work/'results.json',results)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker',type=Path);args=parser.parse_args()
    if args.worker:worker(args.worker);return
    entries=jsonl(RECORDS/'011_table_alignment.jsonl');selected=select()
    selection={(r['task'],r['layer'],r['table']):r for r in selected}
    attempts=spans=0
    for entry in entries:
        before=selection[(entry['task'],entry['layer'],entry['table'])]
        for field in ('before','comparison_columns','key_columns','gold_verification_010','dates'):assert entry[field]==before[field],(entry['table'],field)
        raw=Path(entry['agent_sql_path']).read_bytes().decode('utf-8')
        for attempt in entry['attempts']:
            cursor=0;pieces=[]
            for replacement in attempt['replacements']:
                start,end=replacement['start_offset'],replacement['end_offset']
                assert raw[start:end]==replacement['original_text']
                assert replacement['line']==raw.count('\n',0,start)+1
                assert replacement['column']==start-raw.rfind('\n',0,start)
                expected=f"DATE '{attempt['candidate_date']}'" if replacement['replacement_kind']=='date' else f"TIMESTAMPTZ '{attempt['candidate_date']} 00:00:00+00:00'"
                assert replacement['replacement_text']==expected
                pieces.extend([raw[cursor:start],replacement['replacement_text']]);cursor=end;spans+=1
            pieces.append(raw[cursor:]);frozen=''.join(pieces)
            assert Path(attempt['frozen_sql_path']).read_bytes()==frozen.encode('utf-8')
            assert hashlib.sha256(raw.encode()).hexdigest()==attempt['original_sql_sha256']
            assert hashlib.sha256(frozen.encode()).hexdigest()==attempt['frozen_sql_sha256']
            assert attempt['candidate_date'] in entry['dates'];attempts+=1
    candidates=[]
    for entry in entries:
        for attempt in entry['attempts']:
            a=attempt.get('after',{})
            if a.get('comparison_status')=='compared' and (a['prediction']['row_count']+a['gold']['row_count'])*max(1,len(entry['comparison_columns']))<=120000:
                candidates.append((entry,attempt))
    samples=[];covered=set()
    for category in [('scope','staging'),('scope','cs')]+[('gold_verification_010',v) for v in ('L0整表一致','仅日期层面一致','未能验证')]+[('level','L0'),('level','L3')]:
        possible=[(e,a) for e,a in candidates if ((a['after']['whole_match_level'] if category[0]=='level' else e[category[0]])==category[1]) and (e['task'],e['table']) not in covered]
        if possible:
            entry,attempt=min(possible,key=lambda pair:(min(pair[1]['after']['prediction']['row_count'],pair[1]['after']['gold']['row_count'])==0,pair[1]['after']['prediction']['row_count']+pair[1]['after']['gold']['row_count']))
            samples.append({'entry':entry,'attempt':attempt});covered.add((entry['task'],entry['table']))
    save(RECORDS/'011_validation_selection.json',samples)
    work=ROOT/'data/011_independent_validation';index=1
    while work.exists():work=ROOT/'data'/f'011_independent_validation_{index:02d}';index+=1
    work.mkdir();(work/'.tmp').mkdir()
    command=[shutil.which('bwrap'),'--ro-bind','/','/','--tmpfs','/home/katherine','--ro-bind',str(PROJECT),str(PROJECT),
        '--ro-bind',str(ROOT),str(ROOT),'--bind',str(work),str(work),'--bind',str(work/'.tmp'),'/tmp','--unshare-pid',
        '--proc','/proc','--dev','/dev','--unshare-net','--die-with-parent','--chdir',str(work),'--',str(PYTHON),'-B',str(Path(__file__).resolve()),'--worker',str(work)]
    sys.path.insert(0,str(PROJECT/'src'));from safe_env import scrubbed_env
    environment=scrubbed_env();environment.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'data/005_tools'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    with (RECORDS/'011_validation_execution.log').open('w') as log:done=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=3600)
    assert done.returncode==0,'See records/011_validation_execution.log'
    original=json.loads((RECORDS/'011_input_before.json').read_text())['files'];after={p:fingerprint(Path(p)) for p in original}
    changed=[p for p in original if original[p]!=after[p]];assert not changed,changed
    integrity={'before':original,'after':after,'changed_files':changed,'all_unchanged':True,'finished_at':stamp()}
    save(RECORDS/'011_input_integrity.json',integrity)
    with (RECORDS/'011_date_alignment.csv').open(newline='') as stream:csvrows=list(__import__('csv').DictReader(stream))
    assert len(csvrows)==attempts
    save(RECORDS/'011_validation.json',{'passed':True,'scope_tables':len(entries),'expected_scope_122_verified':len(entries)==122,
        'attempts_audited':attempts,'replacement_spans_audited':spans,'non_clock_SQL_bytes_preserved':True,
        'before_numbers_and_gold_verification_copied_verbatim':True,'fixed_historical_keys_and_columns_verified':True,
        'independent_replays':json.loads((work/'results.json').read_text()),'independent_replay_command':command,
        'original_input_files_unchanged':len(original),'original_databases_unchanged':sum(Path(p).suffix=='.duckdb' for p in original),
        'old_004_010_records_unchanged':True,'CSV_attempt_rows_verified':len(csvrows),'prior_status_updates':0,
        'runtime_SQL_policy_tests':'records/011_tests.log','completed_at':stamp()})
    print('Validated',len(entries),'tables,',attempts,'replays,',spans,'substitutions,',len(samples),'independent fixture-sized replays',flush=True)


if __name__=='__main__':main()
