"""Read-only independent checks for task 009 artifacts and corrected denominators."""

from collections import Counter
import csv
import json
from pathlib import Path
import sys

import duckdb

from compare_dacomp_staging import fingerprint,quote,schema
from complete_dacomp_comparisons import RECORDS,ROOT,SUITE,info,mapped_config,save
from reconcile_dacomp_scope import key
from validate_dacomp_tolerance import spot_check


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    selected=json.loads((RECORDS/'009_selection.json').read_text())
    for target in selected:
        value=json.loads(Path(target['score_source']).read_text())
        for part in target['score_json_path']:value=value[part]
        assert value is target['archived_cs_match']
        assert target['eligible']==(value is False)
    rows=read_jsonl(RECORDS/'009_tolerance_tables.jsonl')
    assert len(rows)==sum(t['eligible'] for t in selected)
    assert {key(r['task'],r['layer'],r['table']) for r in rows}=={key(r['task'],r['layer'],r['table']) for r in selected if r['eligible']}
    evidence=json.loads((RECORDS/'009_official_evaluator_evidence.json').read_text())
    for block in evidence['code']:
        lines=Path(block['path']).read_text().splitlines(keepends=True)
        assert ''.join(lines[block['start_line']-1:block['end_line']])==block['original_text']
    assert all(not r['official_gold_membership'] and r['prefixed_gold_membership'] for r in evidence['impl002_name_checks'])
    baseline008={key(r['task'],r['layer'],r['table']):r for r in read_jsonl(RECORDS/'008_table_scan.jsonl')}
    details={}
    for path in RECORDS.glob('009_cs_impl-*.json'):
        source=json.loads(path.read_text())
        for row in source['tables']:details[key(source['task'],row['layer'],row['table'])]=row
    sys.path.insert(0,str(SUITE))
    from utils import CoreAccuracyEvaluator
    independent=[];official=[];upstreams=[]
    for row in rows:
        identity=key(row['task'],row['layer'],row['table']);detail=details[identity];case=info(int(row['task'][-3:]))
        with duckdb.connect(row['prediction_database'],read_only=True) as pred,duckdb.connect(row['gold_database'],read_only=True) as gold:
            assert schema(pred,row['table'],row['layer'])==detail['prediction']
            assert schema(gold,row['table'],row['layer'])==detail['gold']
            for upstream in detail['actual_gold_upstreams']:
                parts=upstream['name'].split('.')
                if 'rows_after_gold_restore' in upstream:
                    count=gold.execute('SELECT count(*) FROM '+quote(parts[0])+'.'+quote(parts[1])).fetchone()[0]
                    assert count==upstream['rows_after_gold_restore']
                    upstreams.append({'task':row['task'],'target':row['table'],'upstream':upstream['name'],'gold_rows':count})
        expected={s for s in baseline008[identity]['source_comparison']['agent_direct_read_sources']}
        actual={s['canonical'] for s in detail['actual_gold_upstreams']}
        assert expected==actual,identity
        assert not detail['dependency_restore_errors'],identity
        assert row['baseline_alignment']==detail['alignment']
        assert row['key_statistics_match_baseline'] is True
        assert row['execution_date']==detail['execution_started']['Asia/Singapore'][:10]
        assert row['time_dependencies']==baseline008[identity]['time_dependencies']
        assert row['run_time_sensitive']==any(h['context']=='code' for h in row['time_dependencies']['agent_sql']['hits'])
        value=CoreAccuracyEvaluator(Path(row['prediction_database']),Path(row['gold_database']),mapped_config(case['config'],case['number'])).compare_table(row['layer'],row['table'])
        assert value==row['baseline_l0_whole_match']==detail['official_current_match']
        official.append({'task':row['task'],'table':row['table'],'official_readonly_recheck':value})
        for field in ('whole_match','keyed_match'):
            found=False
            for level in row['levels']:
                if level[field] is True:found=True
                if found:assert level[field] is True
        cells=(detail['prediction']['row_count']+detail['gold']['row_count'])*len(set(row['comparison_columns']+row['baseline_alignment']['columns']))
        if cells<=300000:independent.append(spot_check(row))
        print(row['task'],row['table'],'verified',flush=True)
    assert any(r['task']=='impl-002' for r in independent)
    assert any(r['task']=='impl-010' for r in independent)
    assert any(r['task']=='impl-012' for r in independent)
    with (RECORDS/'009_tolerance_tables.csv').open() as stream:flat=list(csv.DictReader(stream))
    assert len(flat)==len(rows)
    for raw,r in zip(flat,rows):
        assert (raw['task'],raw['layer'],raw['table'])==(r['task'],r['layer'],r['table'])
        assert raw['whole_level']==(r['whole_match_level'] or '不可比较')
        assert raw['keyed_level']==(r['keyed_match_level'] or '不可比较')
        assert json.loads(raw['l3_columns'])==r['l3_inconsistent_columns']
    summary=json.loads((RECORDS/'009_denominator_summary.json').read_text())
    catalog=json.loads((RECORDS/'009_nonstaging_failure_catalog.json').read_text())
    raw_failure_keys=set()
    for number in range(1,31):
        task=f'impl-{number:03d}';base=Path('/home/katherine/dac/runs/20261025_de_batch_review_02')
        path=base/(f'compatibility/{task}/score.json' if number in (13,19,22) else f'scoring/{task}/cs/score.json')
        for layer in json.loads(path.read_text())['partial_evaluation']['layer_results']:
            if layer['layer_name']!='staging':
                raw_failure_keys.update(key(task,layer['layer_name'],name) for name,match in layer['comparison_results'].items() if match is False)
    assert raw_failure_keys=={key(r['task'],r['layer'],r['table']) for r in catalog}
    counts=summary['nonstaging_total']
    bad_exec={key(r['task'],r['layer'],r['table']) for r in catalog if not r['current_pred_execution']}
    no_gold={key(r['task'],r['layer'],r['table']) for r in catalog if not r['gold_exists']}
    replay={key(r['task'],r['layer'],r['table']) for r in catalog if r['replay_l0_match']}
    comparable=raw_failure_keys-(bad_exec|no_gold)-replay
    assert counts['unavailable_union']==len(bad_exec|no_gold)
    assert counts['execution_failed_and_gold_missing']==len(bad_exec&no_gold)
    assert counts['comparable_failed_excluding_replay_pass']==len(comparable)
    corrected=read_jsonl(RECORDS/'009_corrected_statuses.jsonl')
    assert len(corrected)==len(baseline008)==1069
    assert dict(Counter(r['status'] for r in corrected))==summary['corrected_status_counts']
    reviewed=json.loads((RECORDS/'009_target_status_review.json').read_text())
    reviewed_index={key(r['task'],r['layer'],r['table']):r for r in reviewed}
    for r in corrected:
        identity=key(r['task'],r['layer'],r['table'])
        assert r['old_008_status']==baseline008[identity]['status_007']['status']
        if identity not in reviewed_index:assert not r['changed'] and r['status']==r['old_008_status']
    combined=summary['combined']
    assert combined['comparable_failed']==combined['format_difference_L1_L2']+combined['pending_annotation_L3_or_unmatched']
    integrity=json.loads((RECORDS/'009_input_integrity.json').read_text());assert integrity['all_unchanged']
    assert all(fingerprint(Path(path))==old for path,old in integrity['before'].items())
    result={'passed':True,'selection_records_verified':len(selected),'official_code_blocks_verified':len(evidence['code']),
        'official_readonly_rechecks':official,'independent_decimal_counter_checks':independent,'upstream_gold_row_checks':upstreams,
        'all_21_csv_jsonl_consistent':True,'nonstaging_failure_catalog_matches_raw_scores':len(raw_failure_keys),
        'corrected_status_rows_verified':len(corrected),'denominator_set_arithmetic_verified':True,
        'input_files_unchanged':len(integrity['before']),
        'original_databases_unchanged':sum(path.endswith('.duckdb') for path in integrity['before'])}
    save(RECORDS/'009_validation.json',result)
    print('009 validation passed; independent references:',len(independent),flush=True)


if __name__=='__main__':main()
