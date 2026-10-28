"""Reconcile the historical failure universe and 008 statuses after task 009."""

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path

from complete_dacomp_comparisons import RECORDS, REVIEW, ROOT, save
from dacomp_trace_scan import layer_key


def key(task,layer,table):
    if task=='impl-002' and layer_key(layer)=='marts' and not table.startswith('pendo__'):
        table='pendo__'+table
    return task,layer_key(layer),table


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def partition(rows):
    executed_missing=sum(not r['current_pred_execution'] for r in rows)
    gold_missing=sum(not r['gold_exists'] for r in rows)
    overlap=sum(not r['current_pred_execution'] and not r['gold_exists'] for r in rows)
    unavailable=sum(not r['bilateral_comparable'] for r in rows)
    replay=sum(r['replay_l0_match'] for r in rows)
    comparable=sum(r['comparable_failed'] for r in rows)
    levels=Counter(r['whole_level'] for r in rows if r['comparable_failed'])
    assert unavailable==executed_missing+gold_missing-overlap
    assert len(rows)-unavailable-replay==comparable
    assert comparable==sum(levels.values())
    return {'historical_failed':len(rows),'cs_execution_failed':executed_missing,'gold_missing':gold_missing,
        'execution_failed_and_gold_missing':overlap,'unavailable_union':unavailable,
        'bilateral_comparable_including_replay_pass':len(rows)-unavailable,'replay_l0_matches':replay,
        'comparable_failed_excluding_replay_pass':comparable,'whole_levels_of_comparable_failures':dict(levels),
        'format_difference':levels['L1']+levels['L2'],'pending_annotation':levels['L3']+levels['仍不匹配']}


def main():
    old008=jsonl(RECORDS/'008_table_scan.jsonl');old008_index={key(r['task'],r['layer'],r['table']):r for r in old008}
    old007=jsonl(RECORDS/'007_tolerance_tables.jsonl')
    levels={key(r['task'],r['layer'],r['table']):r for r in old007}
    newlevels=jsonl(RECORDS/'009_tolerance_tables.jsonl')
    for r in newlevels:levels[key(r['task'],r['layer'],r['table'])]=r
    details={};detail_sources={}
    for prefix in ('005','009'):
        for path in sorted(RECORDS.glob(prefix+'_cs_impl-*.json')):
            record=json.loads(path.read_text())
            for row in record['tables']:
                identity=key(record['task'],row['layer'],row['table'])
                details[identity]=row;detail_sources[identity]=str(path.relative_to(ROOT))
    failures=[]
    for number in range(1,31):
        task=f'impl-{number:03d}'
        path=REVIEW/(f'compatibility/{task}/score.json' if number in (13,19,22) else f'scoring/{task}/cs/score.json')
        score=json.loads(path.read_text())
        for li,layer in enumerate(score['partial_evaluation']['layer_results']):
            if layer['layer_name']=='staging':continue
            for name,match in layer['comparison_results'].items():
                if match is not False:continue
                identity=key(task,layer['layer_name'],name);row=details[identity]
                comparable=bool(row['current_pred_execution'] and row['prediction']['exists'] and row['gold']['exists'] and row['official_compare_cols_available'])
                replay=bool(comparable and row['official_current_match'])
                level=levels.get(identity,{}).get('whole_match_level')
                if comparable:assert level is not None,identity
                failures.append({'task':task,'layer':identity[1],'table':identity[2],'scoring_table':name,
                    'historical_match':match,'score_source':str(path),'score_json_path':['partial_evaluation','layer_results',li,'comparison_results',name],
                    'compatibility_score':number in (13,19,22),'comparison_record':detail_sources[identity],
                    'current_pred_execution':row['current_pred_execution'],'prediction_exists':row['prediction']['exists'],
                    'gold_exists':row['gold']['exists'],'bilateral_comparable':comparable,
                    'replay_l0_match':replay,'comparable_failed':comparable and not replay,'whole_level':level,
                    'in_008_delivered_inventory':identity in old008_index})
    assert len(failures)==189
    staging=[]
    for r in old007:
        if r['scope']=='staging':
            staging.append({'task':r['task'],'layer':'staging','table':r['table'],
                'historical_failed':True,'comparable':r['whole_match_level'] is not None,
                'whole_level':r['whole_match_level'],'source':'records/007_tolerance_tables.jsonl'})
    assert len(staging)==176
    stage_counts={'historical_failed':len(staging),'unavailable':sum(not r['comparable'] for r in staging),
        'comparable_failed':sum(r['comparable'] for r in staging),
        'whole_levels':dict(Counter(r['whole_level'] for r in staging if r['comparable']))}
    assert stage_counts['whole_levels'].get('L0',0)==0
    totals=partition(failures)
    groups={group:partition([r for r in failures if ('intermediate' if r['layer']=='intermediate' else 'marts' if r['layer']=='marts' else 'other')==group]) for group in ('intermediate','marts','other')}
    review=[];updates={}
    for r in newlevels:
        identity=key(r['task'],r['layer'],r['table']);prior=old008_index[identity]['status_007']['status']
        if r['comparison_status']!='compared':status='不可评估'
        elif r['whole_match_level']=='L0':status='官方判为通过'
        elif r['whole_match_level'] in ('L1','L2'):status='格式差异'
        else:status='待标注'
        explanation='009 显式映射带前缀目标，补齐 gold 双边结果并完成节点比较' if r['task']=='impl-002' else '009 纳入原始 CS 不匹配的 sales / utils 目标并完成节点比较'
        record={'task':r['task'],'layer':r['layer'],'table':r['table'],'old_008_status':prior,'new_009_status':status,
            'changed':prior!=status,'whole_level':r['whole_match_level'],'keyed_level':r['keyed_match_level'],
            'reason_for_status_update':explanation,'old_record':'records/008_table_scan.jsonl',
            'new_record':'records/009_tolerance_tables.jsonl','run_time_sensitive':r['run_time_sensitive'],'execution_date':r['execution_date']}
        review.append(record);updates[identity]=record
    inventory=[]
    for r in old008:
        identity=key(r['task'],r['layer'],r['table']);update=updates.get(identity)
        inventory.append({'task':r['task'],'layer':r['layer'],'table':r['table'],'old_008_status':r['status_007']['status'],
            'status':update['new_009_status'] if update else r['status_007']['status'],
            'changed':update['changed'] if update else False,
            'status_source':'records/009_tolerance_tables.jsonl' if update else 'records/008_table_scan.jsonl'})
    statuses=dict(Counter(r['status'] for r in inventory));oldstatus=dict(Counter(r['old_008_status'] for r in inventory))
    oldexpected={'待标注':309,'格式差异':18,'官方判为通过':703,'不可评估':39}
    assert oldstatus==oldexpected
    combined=stage_counts['comparable_failed']+totals['comparable_failed_excluding_replay_pass']
    stage_levels=stage_counts['whole_levels']
    formats=stage_levels.get('L1',0)+stage_levels.get('L2',0)+totals['format_difference']
    pending=stage_levels.get('L3',0)+stage_levels.get('仍不匹配',0)+totals['pending_annotation']
    assert combined==formats+pending
    assert statuses['待标注']==pending and statuses['格式差异']==formats
    summary={'comparison_basis':{'staging':'004 historical CFS-failed targets; use 007 results',
                'nonstaging':'final CS score.json across all layers except staging; compatibility for impl-013/019/022',
                'comparable_failed_definition':'bilateral available and replay L0 does not pass; L1/L2 format differences stay in this denominator'},
        'staging':stage_counts,'nonstaging_total':totals,'nonstaging_by_layer_group':groups,
        'combined':{'historical_failed':len(staging)+len(failures),'unavailable':stage_counts['unavailable']+totals['unavailable_union'],
            'bilateral_comparable_including_replay_pass':stage_counts['comparable_failed']+totals['bilateral_comparable_including_replay_pass'],
            'replay_l0_matches':totals['replay_l0_matches'],'comparable_failed':combined,
            'format_difference_L1_L2':formats,'pending_annotation_L3_or_unmatched':pending},
        'old_008_status_counts':oldstatus,'corrected_status_counts':statuses,
        'status_deltas':{k:statuses.get(k,0)-v for k,v in oldstatus.items()},
        'reviewed_targets':len(review),'changed_targets':sum(r['changed'] for r in review),
        'outside_delivered_inventory':[r for r in failures if not r['in_008_delivered_inventory']],
        'inventory_unavailable_outside_historical_failure_sets':[r for r in inventory if r['status']=='不可评估' and key(r['task'],r['layer'],r['table']) not in {key(x['task'],x['layer'],x['table']) for x in failures+staging}],
        'derived_from':'009 additions overlay 004-008; prior records unchanged'}
    save(RECORDS/'009_denominator_summary.json',summary)
    save(RECORDS/'009_status_changes.json',[r for r in review if r['changed']])
    save(RECORDS/'009_target_status_review.json',review)
    save(RECORDS/'009_nonstaging_failure_catalog.json',failures)
    save(RECORDS/'009_staging_denominator_catalog.json',staging)
    (RECORDS/'009_corrected_statuses.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in inventory))
    for filename,rows in [('009_target_status_review.csv',review),('009_corrected_statuses.csv',inventory)]:
        with (RECORDS/filename).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
