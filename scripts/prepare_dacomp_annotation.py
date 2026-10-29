"""Task 012: derive a new status ledger and reproducible per-task pilot sample."""

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import random

from compare_dacomp_staging import fingerprint
from complete_dacomp_comparisons import ROOT, RECORDS, save, stamp
from reconcile_dacomp_scope import key, jsonl

EXPORT=ROOT/'data/dacomp_deimpl_prev'
ARCHIVE=ROOT/'traces/dacomp_deimpl_prev.tar.gz'


def indices():
    old=jsonl(RECORDS/'009_corrected_statuses.jsonl')
    scans={key(r['task'],r['layer'],r['table']):r for r in jsonl(RECORDS/'008_table_scan.jsonl')}
    aligned={key(r['task'],r['layer'],r['table']):r for r in jsonl(RECORDS/'011_table_alignment.jsonl')}
    gold={key(r['task'],r['layer'],r['table']):r for r in jsonl(RECORDS/'010_table_verification.jsonl')}
    tolerance={key(r['task'],r['layer'],r['table']):(r,f'records/{prefix}_tolerance_tables.jsonl') for prefix in ('007','009') for r in jsonl(RECORDS/f'{prefix}_tolerance_tables.jsonl')}
    return old,scans,aligned,gold,tolerance


def original_basis(identity,tolerance):
    record,source=tolerance[identity]
    detail_path=Path(record['baseline_record']);details=json.loads(detail_path.read_text())
    detail=next(t for t in details['tables'] if key(identity[0],t.get('layer',record['layer']),t['table'])==identity)
    return {'kind':'original_007_009','record':source,'detail_record':str(detail_path),
        'prediction_database':record['prediction_database'],'gold_database':record['gold_database'],
        'actual_schema':record['layer'],'table':record['table'],'candidate_date':None,
        'comparison_columns':record['comparison_columns'],'key_columns':record['baseline_alignment']['columns'],
        'prediction_rows':record['baseline_prediction_rows'],'gold_rows':record['baseline_gold_rows'],
        'row_delta':record['baseline_row_delta'],'key_statistics':record['current_key_statistics'],
        'l0_column_differences':[{k:v for k,v in c.items() if k!='examples'} for c in detail['column_differences'] if c['column'] in record['comparison_columns']],
        'l3_column_differences':record['l3_column_differences'],'whole_match_level':record['whole_match_level'],
        'keyed_match_level':record['keyed_match_level']}


def choose_verified_attempt(entry,gold,task_dates):
    if gold['verification']=='未能验证':return None
    own=set(gold['validated_dates']+gold['date_only_validated_dates'])
    possible=[a for a in entry['attempts'] if a['executed'] and a.get('after',{}).get('comparison_status')=='compared' and a['candidate_date'] in own]
    if not possible:return None
    preferred=set(task_dates['inferred_content_supported_candidates'])|set(task_dates['shared_successful_trial_dates'])
    return min(possible,key=lambda a:(a['candidate_date'] not in preferred,a['candidate_date']))


def main():
    old,scans,aligned,gold,tolerance=indices()
    annotations={key(r['task'],r['layer'],r['table']):r for r in json.loads((RECORDS/'010_impl002_replay_annotations.json').read_text())}
    task_dates={r['task']:r for r in json.loads((RECORDS/'010_task_summary.json').read_text())}
    verified_by_task=defaultdict(set)
    for g in gold.values():
        if g['verification']!='未能验证':verified_by_task[g['task']].update(g['validated_dates']+g['date_only_validated_dates'])
    states=[];changes=[]
    for original in old:
        identity=key(original['task'],original['layer'],original['table']);g=gold.get(identity);entry=aligned.get(identity)
        row={**original,'status_009':original['status'],'status_source_009':original['status_source'],
            'status_record':'records/012_statuses.jsonl','status_rule_revision_date':'2026-10-29',
            'prior_records_modified':False,'date_evidence':[],'evidence_marker':None,
            'official_failed_replay_equal':identity in annotations,'official_failed_replay_equal_annotation':annotations.get(identity),
            'gold_verification_010':g['verification'] if g else None,'difference_basis':None}
        if original['status']=='待标注' and entry:
            own=set(g['validated_dates']+g['date_only_validated_dates']) if g['verification']!='未能验证' else set()
            for attempt in entry['attempts']:
                day=attempt['candidate_date'];level=attempt.get('after',{}).get('whole_match_level')
                if not attempt['executed']:continue
                first=level in ('L0','L1','L2') and (day in own or g['verification']=='未能验证' and day in verified_by_task[original['task']])
                second=g['verification']=='仅日期层面一致' and day in own and level in ('L0','L1','L2','L3')
                if first or second:
                    witnesses=[{'task':w['task'],'layer':w['layer'],'table':w['table'],'verification':w['verification']}
                        for wid,w in gold.items() if wid!=identity and w['task']==original['task'] and w['verification']!='未能验证'
                        and day in w['validated_dates']+w['date_only_validated_dates']]
                    row['date_evidence'].append({'candidate_date':day,'whole_match_level':level,'rule_1':first,'rule_2':second,
                        'date_verified_for_this_table':day in own,'date_verified_elsewhere_in_task':bool(witnesses),
                        'same_task_date_witness_tables':witnesses,
                        'source_record':'records/011_table_alignment.jsonl','gold_date_source':'records/010_table_verification.jsonl'})
        if row['date_evidence']:
            row['status']='日期差异'
            row['evidence_marker']='日期层面证据' if g['verification']=='仅日期层面一致' else '同题已验证日期支持' if g['verification']=='未能验证' else '该表已验证日期'
            row['status_basis']='012 日期规则 1 / 2；每个通过的日期和档位另列，未改变 009/010'
            changes.append(row)
        elif original['status']=='格式差异':
            row['status']='格式差异（待核契约）';row['status_basis']='007/009 整表首次在 L1 或 L2 匹配；本任务仅摘契约原文'
        else:row['status_basis']='沿用 009 更正状态'
        if row['status']=='待标注':
            basis=original_basis(identity,tolerance)
            if entry and g['verification']!='未能验证':
                attempt=choose_verified_attempt(entry,g,task_dates[original['task']])
                if attempt:
                    after=attempt['after'];basis={'kind':'date_aligned_011','record':'records/011_table_alignment.jsonl',
                        'detail_record':f"records/011_alignment_{original['task']}.json",'prediction_database':attempt['prediction_snapshot'],
                        'gold_database':entry['gold_database'],'actual_schema':entry['comparison_schema'],'table':entry['table'],
                        'candidate_date':attempt['candidate_date'],'comparison_columns':entry['comparison_columns'],'key_columns':entry['key_columns'],
                        'prediction_rows':after['prediction']['row_count'],'gold_rows':after['gold']['row_count'],
                        'row_delta':after['row_count_delta_pred_minus_gold'],'key_statistics':after['current_key_statistics'],
                        'l0_column_differences':after['l0_column_differences'],'l3_column_differences':after['l3_column_differences'],
                        'whole_match_level':after['whole_match_level'],'keyed_match_level':after['keyed_match_level']}
                    reason='011 执行与比较成功，使用该表已验证日期；优先 010 同题候选 / 共同兼容日，再按日期升序'
                else:reason='011 执行失败' if all(not a['executed'] for a in entry['attempts']) else '011 无该表已验证日期上的成功比较'
            elif entry:reason='该表 gold 日期未能验证，沿用原差异'
            else:reason='未进入 011，沿用原差异'
            basis['selection_reason']=reason;row['difference_basis']=basis
        elif row['status'].startswith('格式差异'):
            row['difference_basis']=original_basis(identity,tolerance)
            row['difference_basis']['selection_reason']='007/009 原始格式差异结果，不使用 011 改写'
        row['status_changed_from_009']=row['status']!=original['status']
        row['status_source']='records/012_statuses.jsonl'
        row['source_records']=['records/009_corrected_statuses.jsonl',row['status_source_009']]
        if row['date_evidence']:row['source_records'].extend(['records/010_table_verification.jsonl','records/011_table_alignment.jsonl','records/012_status_summary.json'])
        if row['difference_basis']:row['source_records'].extend([row['difference_basis']['record'],row['difference_basis']['detail_record']])
        row['source_records']=list(dict.fromkeys(row['source_records']));states.append(row)
    assert len(states)==1069
    pending=[r for r in states if r['status']=='待标注']
    rng=random.Random(20261029);sample=[]
    for task in sorted({r['task'] for r in pending}):
        candidates=sorted([r for r in pending if r['task']==task],key=lambda r:(r['layer'],r['table']))
        chosen=rng.choice(candidates)
        sample.append({'task':task,'layer':chosen['layer'],'table':chosen['table'],
            'candidate_count_in_task':len(candidates),'sampled_index':candidates.index(chosen),
            'difference_basis_kind':chosen['difference_basis']['kind'],'candidate_date':chosen['difference_basis']['candidate_date'],
            'package_stem':f"012_{task}_{chosen['layer']}_{chosen['table']}"})
    (RECORDS/'012_statuses.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in states))
    flat=[]
    for r in states:
        b=r['difference_basis'] or {}
        flat.append({'task':r['task'],'layer':r['layer'],'table':r['table'],'status_009':r['status_009'],'status':r['status'],
            'status_basis':r['status_basis'],'evidence_marker':r['evidence_marker'],'date_evidence':json.dumps(r['date_evidence'],ensure_ascii=False),
            'difference_basis':b.get('kind'),'difference_record':b.get('record'),'difference_detail_record':b.get('detail_record'),
            'difference_selection_reason':b.get('selection_reason'),'candidate_date':b.get('candidate_date'),
            'official_failed_replay_equal':r['official_failed_replay_equal'],'official_failed_replay_equal_label':r['official_failed_replay_equal_annotation']['display_label'] if r['official_failed_replay_equal'] else None,
            'gold_verification_010':r['gold_verification_010'],'prior_records_modified':False})
        flat[-1]['source_records']=json.dumps(r['source_records'],ensure_ascii=False)
    with (RECORDS/'012_statuses.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(flat[0]),lineterminator='\n');writer.writeheader();writer.writerows(flat)
    save(RECORDS/'012_sampling.json',{'seed':20261029,'generator':'Python random.Random (MT19937)',
        'procedure':'Sort task names ascending; within each task sort pending rows by (layer, table); use one rng.choice sequentially, without resetting the seed.',
        'program':'scripts/prepare_dacomp_annotation.py','samples':sample,'layers':dict(Counter(r['layer'] for r in sample))})
    save(RECORDS/'012_status_summary.json',{'created_at':stamp(),'total':len(states),'statuses':dict(Counter(r['status'] for r in states)),
        'expected_date_differences':34,'actual_date_differences':len(changes),'expected_pending':283,'actual_pending':len(pending),
        'expected_counts_match':len(changes)==34 and len(pending)==283,'date_changes':[{k:r[k] for k in ('task','layer','table','gold_verification_010','evidence_marker','date_evidence')} for r in changes],
        'pending_basis_counts':dict(Counter(r['difference_basis']['kind'] for r in pending)),
        'pending_fallback_reasons':dict(Counter(r['difference_basis']['selection_reason'] for r in pending if r['difference_basis']['kind']=='original_007_009')),
        'official_failed_replay_equal_annotations':sum(r['official_failed_replay_equal'] for r in states),
        'rule_revision':'2026-10-29: 未验证该表日期、但所用日期是同题其他表已验证日期且整表 L0/L1/L2 匹配，也归日期差异。'})
    before=RECORDS/'012_input_before.json'
    if not before.exists():
        files={Path(p) for p in json.loads((RECORDS/'011_input_before.json').read_text())['files']};files.add(ARCHIVE)
        for prefix in [f'{n:03d}_' for n in range(4,12)]:files.update(RECORDS.glob(prefix+'*'));files.update((ROOT/'notes').glob(prefix+'*'))
        needed=[r for r in states if r['status'].startswith('格式差异') or any((r['task'],r['layer'],r['table'])==(s['task'],s['layer'],s['table']) for s in sample)]
        for r in needed:
            scan=scans[key(r['task'],r['layer'],r['table'])]
            files.update(Path(p) for p in scan['inventory_sources']['agent_final_sql_files'])
            files.update(Path(h['path']) for h in scan['time_dependencies']['gold_sql']['hits'])
            for side in ('prediction_database','gold_database'):files.add(Path(r['difference_basis'][side]))
            case=json.loads((RECORDS/f"006_contract_{r['task']}.json").read_text());files.add(Path(case['contract']['path']))
            goldroot=Path(case['gold_database']).parent;files.update(goldroot.rglob('*.sql'))
        for s in sample:
            root=EXPORT/'runs/20261025_de_official_batch_01'/s['task']/'agent'
            files.update(root.glob('.events/sessions/*/events/*.json'))
            files.update(root.glob('sidecar/*/commands.jsonl'))
            for name in ('result.md','result.json'):
                p=root/f"dacomp-de-{s['task']}"/name
                if p.is_file():files.add(p)
            files.update((root/f"dacomp-de-{s['task']}").rglob('result.md'))
        for number in (19,30):
            case=json.loads((RECORDS/f'006_contract_impl-{number:03d}.json').read_text());db=Path(case['agent_database'])
            files.update([db.with_name(db.stem+'_start.duckdb'),db.parent/'run.py'])
        print('Fingerprinting',len(files),'inputs',flush=True)
        save(before,{'started_at':stamp(),'files':{str(p):fingerprint(p) for p in sorted(files)}})
    print('States',dict(Counter(r['status'] for r in states)),'sampled',len(sample),flush=True)


if __name__=='__main__':main()
