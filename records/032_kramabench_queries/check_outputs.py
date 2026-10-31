"""Verify literal snippet edits and the saved complete output artifacts."""
from pathlib import Path
import hashlib,json,re
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def original(tid,n):
    t=(ROOT/'records/028_kramabench_packages'/f'{tid}.md').read_text()
    m=re.search(r'<!-- original:step\.'+str(n)+r'\.code chars:(\d+) -->\n`+[^\n]*\n',t)
    return t[m.end():m.end()+int(m.group(1))]
checks=[]
for prefix,tid,n,old,new in [('06','astronomy-hard-9',9,'om[50]','om[49]'),('08','wildfire-hard-6',5,'between(2002,2024)','between(2000,2024)')]:
    src=original(tid,n)
    assert src==(OUT/f'{prefix}_step{n:02d}_original.txt').read_text()
    assert src.count(old)==1
    p=next(OUT.glob(prefix+'_*.py'));text=p.read_text()
    actual=text.split(f'# BEGIN MODIFIED STEP {n}\n',1)[1].split(f'# END MODIFIED STEP {n}',1)[0]
    assert actual==src.replace(old,new)
    checks.append({'script':p.name,'original_step':n,'only_replacement':[old,new],'passed':True})
assert original('astronomy-hard-9',8) in (OUT/'06_astronomy_hard_9.py').read_text()
m=json.loads((OUT/'run_manifest.json').read_text());r=json.loads((OUT/'results.json').read_text())
assert len(m['queries'])==len(r)==9
for q in m['queries']:
    p=OUT/q['script'];o=OUT/q['stdout'];e=OUT/q['stderr']
    assert sha(p)==q['script_sha256'] and sha(o)==q['stdout_sha256']
    assert o.stat().st_size==q['stdout_bytes'] and e.stat().st_size==q['stderr_bytes']
    assert json.loads(o.read_text().split('\nRESULT_JSON\n')[1])==r[p.stem]
assert not m['sources_changed']
result={'passed':True,'literal_code_checks':checks,'step_8_prerequisite_verbatim':True,
 'nine_script_and_stdout_hashes_verified':True,'stdout_results_match_results_json':True,
 'source_hashes_verified_before_and_after_execution':m['source_files_checked'],'sources_changed':m['sources_changed']}
print(json.dumps(result,ensure_ascii=False,indent=2))
