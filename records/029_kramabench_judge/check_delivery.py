"""Check final artifacts and secrets without displaying or copying credentials."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent

def main():
    key=(Path.home()/'.openrouter_key').read_bytes().strip()
    assert key and b'\n' not in key
    files=sorted([p for p in OUT.rglob('*') if p.is_file()]
                 +[ROOT/'records/029_kramabench_final_scores.csv']
                 +list((ROOT/'notes').glob('029_*_KramaBench待裁判补评.md')))
    secret_pattern=re.compile(rb'(?<![A-Za-z0-9_-])(?:sk-(?:or-v1-|proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|Bearer\s+[A-Za-z0-9._-]{20,})')
    for p in files:
        data=p.read_bytes()
        assert key not in data, 'Exact credential match: value suppressed.'
        assert not secret_pattern.search(data), 'Potential credential pattern: value suppressed.'
    assert not list((ROOT/'records/027_kramabench_source/official').rglob('__pycache__'))
    totals=json.loads((OUT/'validation_and_totals.json').read_bytes())
    mf=json.loads((OUT/'run_manifest.json').read_bytes())
    for name,expected in mf['source_sha256_before'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected
    metas={}
    for p in (ROOT/'records/027_kramabench_source/runs').glob('*/*/meta.json'):
        m=json.loads(p.read_bytes());metas[m['task_id']]=m
    final=list(csv.DictReader((ROOT/'records/029_kramabench_final_scores.csv').open()))
    assert len(final)==104 and {x['题号'] for x in final}==set(metas)
    original_count=judge_count=0
    for row in final:
        m=metas[row['题号']]
        assert row['原评分状态']==m['score']['status']
        if m['score']['status']=='needs_judge':
            r=json.loads((OUT/(row['题号']+'_call1.json')).read_bytes())
            assert row['最终分数']==('' if r['score'] is None else str(r['score']))
            assert row['最终状态']==r['judge_status'];judge_count+=1
        else:
            assert row['最终分数']==str(m['score']['success'])
            expected='未交卷' if m['score']['status']=='unanswered' else ('通过' if m['score']['success']==1 else '未通过')
            assert row['最终状态']==expected;original_count+=1
    assert (original_count,judge_count)==(94,10)
    assert dict(collections.Counter(x['最终状态'] for x in final))==totals['all_104_final_status_counts']
    # Existing tracked working-tree files must remain untouched. New files are
    # checked independently above and staged contents are checked again below.
    assert not subprocess.check_output(['git','diff','--name-only'],cwd=ROOT)
    staged=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0')
    staged=[p for p in staged if p]
    for p in staged:
        assert p.startswith(('records/029_kramabench_judge/','records/029_kramabench_final_scores.csv','notes/029_'))
        data=subprocess.check_output(['git','show',':'+p],cwd=ROOT)
        assert key not in data and not secret_pattern.search(data), 'Credential in staged data: value suppressed.'
    result={'passed':True,'exact_key_matches_in_new_files':0,'credential_pattern_matches_in_new_files':0,
            'scanned_new_files':len(files),'scanned_staged_files':len(staged),'exact_key_matches_in_staged_files':0,
            'credential_file_copied':False,'request_authentication_headers_saved':False,
            'all_original_input_hashes_unchanged':True,'existing_tracked_working_tree_files_modified':False,
            'official_source_cache_directories_created':False,'final_score_rows':104,
            'original_scores_preserved':94,'first_call_scores_used':10,
            'final_status_counts':totals['all_104_final_status_counts']}
    target=OUT/('delivery_check_staged.json' if staged else 'delivery_check.json')
    with target.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
