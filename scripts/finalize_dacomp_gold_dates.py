"""Aggregate all gold-only trials, preserve provenance, and leave 004-009 unchanged."""

from collections import Counter,defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sqlglot
from sqlglot import exp

from complete_dacomp_comparisons import ROOT,RECORDS,save,stamp
from dacomp_gold_clock import DATE_NAMES


def raw_day_count(expression):
    try:node=sqlglot.parse_one(expression,read='duckdb')
    except Exception:return False
    while isinstance(node,(exp.Cast,exp.TryCast,exp.Paren)):node=node.this
    if isinstance(node,exp.DateDiff):return str(node.args.get('unit','')).upper() in ('DAY','DAYS') and bool(list(node.find_all(exp.CurrentDate,exp.CurrentTimestamp)))
    if isinstance(node,exp.Case):
        values=[item.args.get('true') for item in node.args.get('ifs',[])]+[node.args.get('default')]
        values=[item for item in values if item is not None and not isinstance(item,exp.Null)]
        return bool(values) and all(raw_day_count(item.sql(dialect='duckdb')) for item in values)
    return False


def sanitize(value):
    if isinstance(value,dict):
        if 'frozen_sql' in value:
            raw=value.pop('frozen_sql').encode()
            digest=hashlib.sha256(raw).hexdigest();directory=ROOT/'data/010_frozen_sql';directory.mkdir(exist_ok=True)
            path=directory/(digest+'.sql');path.write_bytes(raw)
            value['frozen_sql_path']=str(path)
        for item in value.values():sanitize(item)
    elif isinstance(value,list):
        for item in value:sanitize(item)


def main():
    plans={p.stem[-8:]:json.loads(p.read_text()) for p in RECORDS.glob('010_plan_impl-*.json')}
    additional=json.loads((RECORDS/'010_additional_candidate_evidence.json').read_text())
    prior=defaultdict(list)
    for path in RECORDS.glob('010_preliminary_impl-*.json'):
        for row in json.loads(path.read_text())['tables']:prior[row['sql_path']].append((str(path),row))
    for path in RECORDS.glob('010_boundary_trials_impl-*.json'):
        for row in json.loads(path.read_text())['tables']:prior[row['sql_path']].append((str(path),row))
    for path in RECORDS.glob('010_common_day_impl-*.json'):
        for row in json.loads(path.read_text())['tables']:prior[row['sql_path']].append((str(path),row))
    rows=[];candidates=[];summaries=[]
    for task,plan in sorted(plans.items()):
        file=RECORDS/f'010_verification_{task}.json';result=json.loads(file.read_text());plan_index={t['sql_path']:t for t in plan['tables']}
        for row in result['tables']:
            entry=plan_index[row['sql_path']];raw_hash=hashlib.sha256(Path(row['sql_path']).read_bytes()).hexdigest()
            attempts=[];identities=set()
            for origin,earlier in [(str(file),row)]+prior[row['sql_path']]:
                for attempt in earlier['attempts']:
                    identity=(attempt['execution_started']['utc'],attempt['frozen_sql_sha256'])
                    if identity in identities:continue
                    identities.add(identity)
                    attempt['attempt_source_record']=origin
                    attempt.setdefault('candidate_reason',earlier.get('candidate_reasons',{}).get(attempt['candidate_date']))
                    attempt['source_bytes_preserved']=attempt['original_sql_sha256']==raw_hash
                    if attempt['source_bytes_preserved']:attempts.append(attempt)
            row['latest_replay_verification']=row['verification'];row['attempts']=attempts
            row['prior_attempt_sources']=[origin for origin,_ in prior[row['sql_path']]]
            row['validated_dates']=sorted({a['candidate_date'] for a in attempts if a.get('comparison',{}).get('l0_full_match')})
            row['date_only_validated_dates']=sorted({a['candidate_date'] for a in attempts if a.get('comparison',{}).get('date_only_full_match') and a['candidate_date'] not in row['validated_dates']})
            if row.get('retained_gold_view_has_runtime'):
                row['verification']='未能验证';row['date_identification']='runtime_gold_view_cannot_establish_historical_generation_day'
            else:
                row['verification']='L0整表一致' if row['validated_dates'] else '仅日期层面一致' if row['date_only_validated_dates'] else '未能验证'
            own_direct={c['date'] for e in entry.get('candidate_evidence',[]) if e.get('status')=='direct_projection' or e.get('status')=='series_endpoint' and any(w in row['table'] for w in ('spine','calendar')) for c in e.get('candidate_dates',[]) if c['date']}
            row['direct_projection_or_calendar_dates']=sorted(own_direct)
            passed=set(row['validated_dates']+row['date_only_validated_dates'])
            row['date_identification']='direct_content_day_reproduced' if own_direct&passed and row['gold_rows'] else 'compatible_trial_dates_not_a_unique_day' if passed and row['verification']!='未能验证' else 'unverified'
            row['unique_day_not_claimed_for_weak_or_empty_output']=not bool(own_direct&passed and row['gold_rows'])
            row['candidate_evidence']=entry.get('candidate_evidence',[])
            for evidence in row['candidate_evidence']:
                if evidence['basis']=='datediff_days_inverse':
                    evidence['raw_day_inverse_supported']=raw_day_count(evidence.get('original_expression',''))
                    if not evidence['raw_day_inverse_supported']:
                        evidence['inference_limit']='The output is transformed/scored or mixes a historical datediff branch; not an unconditional day count. Retained only as an exploratory hypothesis, not as a generation-date inference.'
            row['gold_relation_type']=entry.get('gold_relation_type')
            row['gold_database']=plan['gold_database']
            row['has_timestamp_runtime_function']=any(n not in DATE_NAMES for n in row['runtime_function_names'])
            row['additional_candidate_evidence_source']='records/010_additional_candidate_evidence.json' if task in ('impl-011','impl-015','impl-019') else None
            sanitize(row);rows.append(row)
            for i,evidence in enumerate(row['candidate_evidence']):
                for candidate in evidence.get('candidate_dates',[]):
                    candidates.append({'evidence_id':f'{task}:{row["layer"]}.{row["table"]}:{i}',
                        'task':task,'layer':row['layer'],'table':row['table'],'column':evidence.get('column'),
                        'candidate_date':candidate['date'],'supporting_rows':candidate['supporting_rows'],
                        'basis':evidence['basis'],'status':evidence['status'],'probe_sql':evidence['probe_sql'],
                        'raw_day_inverse_supported':evidence.get('raw_day_inverse_supported'),'inference_limit':evidence.get('inference_limit'),
                        'expression_rendered_for_inference':evidence.get('original_expression'),
                        'source_sql_path':row['sql_path'],'source_runtime_locations':[h for h in entry['runtime_lexical_hits'] if h['context']=='code'],
                        'calculation':evidence.get('calculation'), 'observed_max_date':evidence.get('observed_max_date')})
        save(file,result)
        taskrows=result['tables'];counts=Counter(r['verification'] for r in taskrows)
        strong=Counter()
        for entry in plan['tables']:
            verified_row=next(r for r in taskrows if r['sql_path']==entry['sql_path'])
            passed_dates=set(verified_row['validated_dates']+verified_row['date_only_validated_dates']) if verified_row['verification']!='未能验证' else set()
            for e in entry.get('candidate_evidence',[]):
                if e['status']=='direct_projection' or e['status']=='series_endpoint' and any(w in entry['table'] for w in ('spine','calendar')):
                    strong.update(c['date'] for c in e.get('candidate_dates',[]) if c['date'] in passed_dates)
                elif e['basis']=='datediff_days_inverse' and raw_day_count(e.get('original_expression','')):
                    cs=e.get('candidate_dates',[])
                    if cs and cs[0]['supporting_rows']>=10 and cs[0]['date'] in passed_dates:strong[cs[0]['date']]+=1
        for e in additional:
            if e['task']==task:strong[e['candidate_date']]+=100
        anchor_dates=[d for d,_ in strong.most_common()]
        validated=[r for r in taskrows if r['verification']!='未能验证']
        sets=[set(r['validated_dates']+r['date_only_validated_dates']) for r in validated]
        intersection=sorted(set.intersection(*sets)) if sets else []
        union=sorted(set.union(*sets)) if sets else []
        summaries.append({'task':task,'inferred_content_supported_candidates':anchor_dates,
            'date_inference_status':'content_supported_candidates_require_tablewise_validation' if anchor_dates else 'no_unique_generation_day_inferred',
            'tables_total':len(taskrows),'l0_verified_tables':counts['L0整表一致'],'date_only_verified_tables':counts['仅日期层面一致'],
            'timestamp_only_date_verified_tables':sum(r['verification']=='仅日期层面一致' and r['timestamp_only'] for r in taskrows),
            'mixed_clock_date_verified_tables':sum(r['verification']=='仅日期层面一致' and not r['timestamp_only'] for r in taskrows),
            'unverified_tables':counts['未能验证'],'missing_gold_tables':sum(not r['gold_exists'] for r in taskrows),
            'runtime_gold_view_tables':sum(r.get('retained_gold_view_has_runtime',False) for r in taskrows),
            'all_successful_trial_dates':union,'shared_successful_trial_dates':intersection,
            'successful_trial_date_sets_agree':len(union)<=1,
            'consistency_limit':'A compatible trial is not necessarily a unique generation date. Untested common dates are not ruled out; unverified tables do not establish consistency.',
            'at_inferred_candidate':{day:{'l0':sum(day in r['validated_dates'] and r['verification']!='未能验证' for r in taskrows),
                'date_only':sum(day in r['date_only_validated_dates'] and r['verification']!='未能验证' for r in taskrows),
                'tested_without_match':sum(any(a['candidate_date']==day for a in r['attempts']) and day not in r['validated_dates']+r['date_only_validated_dates'] for r in taskrows),
                'not_tested':sum(not any(a['candidate_date']==day for a in r['attempts']) for r in taskrows)} for day in anchor_dates}})
        save(RECORDS/f'010_plan_{task}.json',plan)
    # Remove complete gold SQL payloads from tracked metadata; lossless recipes and
    # hashes remain, while exact frozen SQL stays under ignored data/.
    for path in RECORDS.glob('010_*.json'):
        value=json.loads(path.read_text());sanitize(value);save(path,value)
    (RECORDS/'010_table_verification.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    (RECORDS/'010_candidate_evidence.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in candidates))
    fields=['task','layer','table','verification','gold_rows','gold_relation_type','timestamp_only','validated_dates','date_only_validated_dates',
        'date_identification','unique_day_not_claimed_for_weak_or_empty_output','retained_gold_view_has_runtime','attempt_count','sql_path','candidate_evidence_record','replacement_record']
    with (RECORDS/'010_table_verification.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader()
        for row in rows:
            flat={f:row.get(f) for f in fields};flat['attempt_count']=len(row['attempts'])
            flat['candidate_evidence_record']='records/010_candidate_evidence.jsonl';flat['replacement_record']=f'records/010_verification_{row["task"]}.json'
            for f in ('validated_dates','date_only_validated_dates'):flat[f]=json.dumps(flat[f],ensure_ascii=False)
            writer.writerow(flat)
    save(RECORDS/'010_task_summary.json',summaries)
    total={'generated_at':stamp(),'tasks':len(summaries),'tables':len(rows),'l0_verified':sum(s['l0_verified_tables'] for s in summaries),
        'tasks_with_content_supported_candidates':sum(bool(s['inferred_content_supported_candidates']) for s in summaries),
        'tasks_without_unique_day_inference':sum(not s['inferred_content_supported_candidates'] for s in summaries),
        'date_only_verified':sum(s['date_only_verified_tables'] for s in summaries),'unverified':sum(s['unverified_tables'] for s in summaries),
        'timestamp_only_date_verified':sum(s['timestamp_only_date_verified_tables'] for s in summaries),
        'mixed_clock_date_verified':sum(s['mixed_clock_date_verified_tables'] for s in summaries),
        'date_only_with_DATE_and_TIMESTAMP':sum(r['verification']=='仅日期层面一致' and not r['timestamp_only'] and r['has_timestamp_runtime_function'] for r in rows),
        'date_only_without_TIMESTAMP_function':sum(r['verification']=='仅日期层面一致' and not r['has_timestamp_runtime_function'] for r in rows),
        'gold_missing':sum(s['missing_gold_tables'] for s in summaries),'runtime_gold_views':sum(s['runtime_gold_view_tables'] for s in summaries),
        'final_attempts':sum(len(r['attempts']) for r in rows),
        'verification_policy':'all gold columns, exact L0 text row multisets; date-only changes only ISO date/time to date, without numeric tolerances; midnight UTC for unknown time of day; no unique-day claim for merely compatible dates',
        'agent_SQL_executions':0,'prior_agent_status_updates':0,'impl002_replay_annotations':12}
    assert total['l0_verified']+total['date_only_verified']+total['unverified']==total['tables']==303
    save(RECORDS/'010_summary.json',total)
    print(json.dumps(total,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
