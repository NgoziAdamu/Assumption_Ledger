"""Aggregate task 011 without modifying any earlier comparison or status."""

from collections import Counter
import csv
import json
from pathlib import Path

from complete_dacomp_comparisons import ROOT, RECORDS, save, stamp


def column_numbers(items):
    if items is None:return None
    return {c['column']:{k:c[k] for k in ('mismatch_rows_or_minimum_pairs','pred_unmatched_value_occurrences','gold_unmatched_value_occurrences')} for c in items}


def vector(value,before=False):
    alignment=value['key_statistics'] if before else value['current_key_statistics']
    result={'absolute_row_delta':abs(value['row_count_delta_pred_minus_gold']),
            'pred_only_keys':alignment['pred_only_keys'],'gold_only_keys':alignment['gold_only_keys']}
    for level in ('l0','l3'):
        numbers=column_numbers(value.get(level+'_column_differences'))
        if numbers is None:continue
        for column,counts in numbers.items():
            for name,count in counts.items():result[f'{level}/{column}/{name}']=count
    return result


def change(before,attempt):
    after=attempt.get('after',{})
    if after.get('comparison_status')!='compared':
        return {'outcome':'不可比较','metrics_change':'unavailable','exception_type':attempt.get('exception_type'),
                'exception_message':attempt.get('exception_message'),'comparison_status':after.get('comparison_status')}
    b,a=vector(before,True),vector(after)
    common=sorted(set(b)&set(a));missing=sorted(set(b)^set(a))
    reductions={k:{'before':b[k],'after':a[k]} for k in common if a[k]<b[k]}
    increases={k:{'before':b[k],'after':a[k]} for k in common if a[k]>b[k]}
    if missing:direction='部分数字不可直接比较'
    elif reductions and not increases:direction='差异数字缩小'
    elif increases and not reductions:direction='差异数字增大'
    elif increases and reductions:direction='部分缩小且部分增大'
    else:direction='数字没有变化'
    level=after['whole_match_level']
    if level in ('L0','L1','L2'):outcome='L0/L1/L2匹配'
    elif level=='L3':outcome='只在L3匹配'
    elif direction=='差异数字缩小':outcome='差异缩小但仍不匹配'
    elif direction=='数字没有变化':outcome='没有变化且仍不匹配'
    else:outcome='其他变化或不可直接比较且仍不匹配'
    return {'outcome':outcome,'metrics_change':direction,'reduced_components':reductions,'increased_components':increases,
            'components_missing_on_one_side':missing,'compared_component_count':len(common),
            'definition':'Compare absolute row delta, pred-only/gold-only key counts, and per-column L0/L3 mismatch and unmatched-occurrence counts. Shrunk means every comparable component non-increasing and at least one smaller, with no unavailable component. No sum or causal attribution.'}


OUTCOMES=['L0/L1/L2匹配','只在L3匹配','差异缩小但仍不匹配','没有变化且仍不匹配','其他变化或不可直接比较且仍不匹配','不可比较']
GOLD=['L0整表一致','仅日期层面一致','未能验证']


def summarize(rows):
    counts={g:{o:0 for o in OUTCOMES} for g in GOLD}
    for row in rows:counts[row['gold_verification_010']][row['outcome']]+=1
    return {g:{'total':sum(c.values()),**c,'有退化标记':sum(bool(r['degeneracy_flagged']) for r in rows if r['gold_verification_010']==g)} for g,c in counts.items()}


def main():
    selection=json.loads((RECORDS/'011_selection.json').read_text());entries=[];trials=[];table_rows=[]
    for task in sorted({r['task'] for r in selection['tables']}):
        path=RECORDS/f'011_alignment_{task}.json';doc=json.loads(path.read_text())
        for entry in doc['tables']:
            assert len(entry['attempts'])==len(entry['dates'])
            for attempt in entry['attempts']:
                if not attempt['executed']:
                    attempt.setdefault('after',{'prediction':{'exists':False,'row_count':None,'columns':[]},
                        'gold':{'exists':True,'row_count':entry['before']['gold_rows'],'row_count_source':entry['before']['source_record']},
                        'comparison_status':'execution_failed','row_count_delta_pred_minus_gold':None})
                    attempt.setdefault('degeneracy',{'evaluation_status':'unavailable_execution_failure','flagged':None,
                        'both_zero_rows':None,'clock_output_degeneracy':None,'clock_output_columns':[]})
                for c in attempt.get('after',{}).get('l0_column_differences',[]):c.pop('examples',None)
                for c in attempt.get('degeneracy',{}).get('clock_output_columns',[]):
                    c['included_in_comparison']=c['column'].lower() in {v.lower() for v in entry['comparison_columns']}
                attempt['change']=change(entry['before'],attempt)
                trials.append({'task':entry['task'],'layer':entry['layer'],'table':entry['table'],
                    'candidate_date':attempt['candidate_date'],'gold_verification_010':entry['gold_verification_010'],
                    'outcome':attempt['change']['outcome'],'metrics_change':attempt['change']['metrics_change'],
                    'whole_match_level':attempt.get('after',{}).get('whole_match_level'),
                    'degeneracy_flagged':attempt.get('degeneracy',{}).get('flagged',False)})
            outcomes=[a['change']['outcome'] for a in entry['attempts']]
            # Count each table once in a transparent best-observed summary. Every
            # date retains its own record; no date is selected as the true date.
            if 'L0/L1/L2匹配' in outcomes:outcome='L0/L1/L2匹配'
            elif '只在L3匹配' in outcomes:outcome='只在L3匹配'
            elif '差异缩小但仍不匹配' in outcomes:outcome='差异缩小但仍不匹配'
            elif all(o=='没有变化且仍不匹配' for o in outcomes):outcome='没有变化且仍不匹配'
            elif all(o=='不可比较' for o in outcomes):outcome='不可比较'
            else:outcome='其他变化或不可直接比较且仍不匹配'
            levels=[a.get('after',{}).get('whole_match_level') for a in entry['attempts']]
            best=next((l for l in ['L0','L1','L2','L3'] if l in levels),'仍不匹配' if any(l=='仍不匹配' for l in levels) else None)
            entry['aggregate']={'outcome':outcome,'best_observed_whole_level':best,
                'degeneracy_flagged':any(a.get('degeneracy',{}).get('flagged',False) for a in entry['attempts']),
                'degeneracy_available_for_all_dates':all(a.get('degeneracy',{}).get('flagged') is not None for a in entry['attempts']),
                'date_outcomes_differ':len(set(zip(outcomes,levels)))>1,
                'summary_rule':'For ambiguous dates, any matching date is counted once at the best observed level. Otherwise any strict componentwise reduction is counted as shrink; unchanged requires all dates unchanged. Individual dates remain separate; no historical date is chosen.'}
            table_rows.append({'task':entry['task'],'layer':entry['layer'],'table':entry['table'],
                'gold_verification_010':entry['gold_verification_010'],'outcome':outcome,
                'whole_match_level':best,'degeneracy_flagged':entry['aggregate']['degeneracy_flagged']})
            entries.append(entry)
        save(path,doc)
    assert len(entries)==selection['actual'] and len(trials)==selection['planned_attempts']
    (RECORDS/'011_table_alignment.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in entries))
    csvrows=[]
    for entry in entries:
        before=entry['before'];bk=before['key_statistics']
        for attempt in entry['attempts']:
            after=attempt.get('after',{});ak=after.get('current_key_statistics') or {};deg=attempt.get('degeneracy',{})
            csvrows.append({'task':entry['task'],'layer':entry['layer'],'table':entry['table'],
                'candidate_date':attempt['candidate_date'],'gold_verification_010':entry['gold_verification_010'],
                'gold_candidate_verified_010':attempt['date_validated_for_this_gold_table_010'],
                'task_common_compatible_date_010':attempt['date_in_task_shared_compatible_dates_010'],
                'comparison_columns':json.dumps(entry['comparison_columns'],ensure_ascii=False),'key_columns':json.dumps(entry['key_columns'],ensure_ascii=False),
                'before_pred_rows':before['prediction_rows'],'before_gold_rows':before['gold_rows'],'before_row_delta':before['row_count_delta_pred_minus_gold'],
                'before_pred_only_keys':bk['pred_only_keys'],'before_gold_only_keys':bk['gold_only_keys'],'before_shared_keys':bk['shared_keys'],
                'before_whole_level':before['whole_match_level'],'before_keyed_level':before['keyed_match_level'],
                'before_l0_column_counts':json.dumps(column_numbers(before['l0_column_differences']),ensure_ascii=False),
                'before_l3_column_counts':json.dumps(column_numbers(before['l3_column_differences']),ensure_ascii=False),
                'after_pred_rows':after.get('prediction',{}).get('row_count'),'after_gold_rows':after.get('gold',{}).get('row_count'),
                'after_row_delta':after.get('row_count_delta_pred_minus_gold'),'after_pred_only_keys':ak.get('pred_only_keys'),
                'after_gold_only_keys':ak.get('gold_only_keys'),'after_shared_keys':ak.get('shared_keys'),
                'after_whole_level':after.get('whole_match_level'),'after_keyed_level':after.get('keyed_match_level'),
                'after_l0_column_counts':json.dumps(column_numbers(after.get('l0_column_differences')),ensure_ascii=False),
                'after_l3_column_counts':json.dumps(column_numbers(after.get('l3_column_differences')),ensure_ascii=False),
                'outcome':attempt['change']['outcome'],'metrics_change':attempt['change']['metrics_change'],
                'both_zero_rows':deg.get('both_zero_rows'),'clock_output_degeneracy':deg.get('clock_output_degeneracy'),
                'degeneracy_flagged':deg.get('flagged'),'executed':attempt['executed'],
                'comparison_status':after.get('comparison_status'),'exception_type':attempt.get('exception_type'),
                'before_source':before['source_record'],'detail_record':f"records/011_alignment_{entry['task']}.json",'status_modified':False})
    with (RECORDS/'011_date_alignment.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(csvrows[0]),lineterminator='\n');writer.writeheader();writer.writerows(csvrows)
    save(RECORDS/'011_trial_summary.json',trials)
    save(RECORDS/'011_summary.json',{'generated_at':stamp(),'tables':len(entries),'attempts':len(trials),
        'tables_by_gold_verification':summarize(table_rows),'attempts_by_gold_verification':summarize(trials),
        'all_dates_numeric_unchanged_tables_by_gold_verification':{g:sum(all(a['change']['metrics_change']=='数字没有变化' for a in e['attempts']) for e in entries if e['gold_verification_010']==g) for g in GOLD},
        'best_observed_whole_levels':dict(Counter(r['whole_match_level'] or '不可比较' for r in table_rows)),
        'single_date_tables':sum(len(r['dates'])==1 for r in entries),'multiple_date_tables':sum(len(r['dates'])>1 for r in entries),
        'tables_with_date_dependent_outcomes':[{'task':e['task'],'layer':e['layer'],'table':e['table']} for e in entries if e['aggregate']['date_outcomes_differ']],
        'execution_failures':[{'task':e['task'],'table':e['table'],'date':a['candidate_date'],'exception':a.get('exception_message')} for e in entries for a in e['attempts'] if not a['executed']],
        'comparison_failures':[{'task':e['task'],'table':e['table'],'date':a['candidate_date'],'exception':a.get('exception_message'),'status':a.get('after',{}).get('comparison_status')} for e in entries for a in e['attempts'] if a['executed'] and a.get('after',{}).get('comparison_status')!='compared'],
        'unresolved_lineage_outputs':sum(len(a.get('output_lineage',{}).get('unresolved_outputs',[])) for e in entries for a in e['attempts']),
        'tables_with_unavailable_degeneracy_check':sum(not e['aggregate']['degeneracy_available_for_all_dates'] for e in entries),
        'prior_status_updates':0,'gold_SQL_executions':0,
        'summary_policy':'Count each table once at its best observed compatible-date outcome; retain every date separately. Degeneracy is an overlapping flag, not an explanation or prior-status update.'})
    print(json.dumps(json.loads((RECORDS/'011_summary.json').read_text()),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
