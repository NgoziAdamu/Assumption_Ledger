"""Check recorded inputs, official metric returns, candidate witnesses and CSV."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP, localcontext
import collections
import csv
import hashlib
import importlib.util
import json
import logging
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('tolerance',ROOT/'records/030_kramabench_tolerance.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
logging.getLogger().handlers=[logging.NullHandler()]

def main():
    recs=json.loads((ROOT/'records/030_kramabench_tolerance_details.json').read_bytes())
    calls=json.loads((ROOT/'records/030_kramabench_metric_calls.json').read_bytes())
    summary=json.loads((ROOT/'records/030_kramabench_tolerance_summary.json').read_bytes())
    rows=list(csv.DictReader((ROOT/'records/030_kramabench_tolerance.csv').open()))
    old={r['题号']:r for r in csv.DictReader((ROOT/'records/029_kramabench_final_scores.csv').open()) if r['最终状态'] in ['未通过','未交卷']}
    assert len(rows)==len(recs)==len(old)==42
    assert {r['题号'] for r in rows}=={r['task_id'] for r in recs}==set(old)
    byid={r['题号']:r for r in rows}
    success,f1,definitions=module.official_functions()
    assert definitions==summary['official_definition_provenance']
    for event in calls:
        if event['metric']=='F1':
            assert isinstance(event['predicted'],list) and isinstance(event['target'],list)
            result=f1(event['predicted'],event['target'])
        else:
            assert event['metric']=='Success'
            result=success(event['predicted'],event['target'])
        assert list(result)==event['return']
        assert result[1:]==(0,0,0)
    used=set();quote_checks=rounding_checks=0
    for r in recs:
        tid=r['task_id'];row=byid[tid]
        meta=json.loads((ROOT/r['meta_source']).read_bytes())
        text=(ROOT/r['workload_source']).read_text()
        task=next(t for t in json.loads(text) if t['id']==tid)
        exact=next(t for t in json.loads(text,parse_float=Decimal,parse_int=Decimal) if t['id']==tid)
        assert r['official_029_row']==old[tid]
        assert r['answer_original']==meta['final_answer'] and type(r['answer_original'])==type(meta['final_answer'])
        assert r['gold_original']==task['answer'] and type(r['gold_original'])==type(task['answer'])
        assert row['最终答案原文']==module.display(meta['final_answer']) and row['标准答案原文']==module.display(task['answer'])
        assert row['第0档_029最终状态']==old[tid]['最终状态'] and row['第0档_029分数']==old[tid]['最终分数']
        assert r['query']==meta['prompt_values']['query']==task['query']
        for quote in r['format_sentences']:
            assert r['query'][quote['start']:quote['end']]==quote['text']
            assert quote['keyword_hits']==[m.group() for m in module.FORMAT.finditer(quote['text'])]
            quote_checks+=1
        assert row['题面中关于答案形式的原句']=='\n'.join(q['text'] for q in r['format_sentences'])
        matches=[]
        for n in [1,2,3]:
            s=r['stages'][str(n)]
            assert row[f'第{n}档是否对上']==s['status']
            trials=[{'candidate':s['candidate'],'score':s['score'],'event':s['event']}] if 'event' in s else s.get('trials',[])
            for trial in trials:
                event=calls[trial['event']];used.add(trial['event'])
                assert trial['score']==event['return'][0]
                assert trial['candidate']['value']==event['predicted']
                candidate=trial['candidate']
                if candidate['operation']=='prefix_before_delimiter':
                    core=r['answer_original'].split(candidate['delimiter'],1)[0]
                    assert core==candidate['original_core']
                    assert module.normalize(core)==candidate['value']
                elif candidate['operation']=='extract_number':
                    start,end=candidate['cleaned_text_span']
                    assert r['numeric_cleaned_text'][start:end]==candidate['token']
                    assert Decimal(candidate['token'])==Decimal(str(candidate['value']))
                elif candidate['operation']=='round_half_up':
                    p=max(0,-exact['answer'].as_tuple().exponent)
                    assert candidate['decimal_places']==p
                    with localcontext() as ctx:
                        ctx.prec=60
                        rounded=Decimal(candidate['source_candidate']['token']).quantize(Decimal(1).scaleb(-p),rounding=ROUND_HALF_UP)
                    assert format(rounded,'f')==candidate['rounded_decimal_text']
                    assert rounded==Decimal(str(candidate['value']));rounding_checks+=1
                elif candidate['operation']=='round_numeric_list_items_by_target_position':
                    for item in candidate['items']:
                        p=max(0,-exact['answer'][item['index']].as_tuple().exponent)
                        assert p==item['decimal_places']
                        rounded=Decimal(str(item['before'])).quantize(Decimal(1).scaleb(-p),rounding=ROUND_HALF_UP)
                        assert format(rounded,'f')==item['rounded_decimal_text']
                        assert rounded==Decimal(str(candidate['value'][item['index']]));rounding_checks+=1
            if trials:
                matched=[t for t in trials if t['score']==1]
                assert s['status']==('对上' if matched else '未对上')
                if matched:matches.append((n,matched[0]['candidate']))
        if meta['final_answer'] is None:
            assert r['first_match']=='无答案' and not matches
        elif task['answer_type']=='string_approximate':
            assert r['first_match']=='不适用' and not matches
        elif matches:
            assert (r['first_match'],r['matched_using'])==matches[0]
        else:assert r['first_match']=='各适用档均未对上'
        assert row['第一次对上的档']==str(r['first_match'])
        if r['matched_using'] is not None:
            assert json.loads(row['对上时用的是什么'])==r['matched_using']
        else:assert not row['对上时用的是什么']
        if task['answer_type']=='string_exact' and isinstance(meta['final_answer'],str) and isinstance(task['answer'],str):
            assert r['gold_literal_substring_in_answer']==(task['answer'] in meta['final_answer'])
    assert used==set(range(len(calls)))
    assert dict(collections.Counter(str(r['first_match']) for r in recs))==summary['first_match_counts']
    for name,digest in summary['source_sha256_before_and_after'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    assert not subprocess.check_output(['git','diff','--name-only'],cwd=ROOT)
    assert 'openai' not in sys.modules and 'benchmark.llm_tools' not in sys.modules
    result={'passed':True,'tasks_checked':42,'official_metric_return_replay_checks':len(calls),
            'source_sentence_substring_checks':quote_checks,'rounding_witness_checks':rounding_checks,
            'first_match_and_csv_verified':True,'sources_unchanged':True,'model_modules_imported':False,
            'model_calls':0,'all_F1_arguments_are_lists_no_eval_branch':True,
            'existing_tracked_files_modified':False}
    with (ROOT/'records/030_kramabench_validation.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
