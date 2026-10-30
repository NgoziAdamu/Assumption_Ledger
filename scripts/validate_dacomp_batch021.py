"""Validate deliverable scope, blind lock, isolated edits, comparisons and fingerprints."""
from pathlib import Path
import csv, json, hashlib, datetime, subprocess
ROOT=Path(__file__).resolve().parents[1]; REC=ROOT/'records'
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 scope=load(REC/'021_scope.json'); inv=load(REC/'021_package_inventory.json')
 pilot={(r['task'],r['table']) for r in load(REC/'012_sampling.json')['samples']}
 expected={(r['task'],r['table']) for r in csv.DictReader((REC/'013_statuses.csv').open()) if r['task'] in ['impl-008','impl-009','impl-010','impl-011'] and r['status']=='待标注' and (r['task'],r['table']) not in pilot}
 assert len(expected)==40 and expected=={(r['task'],r['table']) for r in scope[:40]}
 assert [(r['task'],r['table']) for r in scope[40:]]==[('impl-013','int_netsuite2__customer_profitability'),('impl-030','stg_zuora__invoice')]
 assert len(scope)==len(inv)==42
 assert len(list((REC/'021_packages').glob('*.md')))==40
 assert all((ROOT/x['path']).is_file() and (ROOT/x['full_json']).is_file() for x in inv)
 out=REC/'021_annotations'; files=list(out.glob('*.md')); assert len(files)==42
 fields=next(csv.reader(next((REC/'018_annotations').glob('*.csv')).open())); fields=[f for f in fields if not f.startswith('与上一版相比')]
 with (out/'021_summary.csv').open() as f:
  reader=csv.DictReader(f); assert reader.fieldnames==fields; summary=list(reader)
 assert len(summary)==42 and [(r['题目'],r['表']) for r in summary]==[(r['task'],r['table']) for r in scope]
 assert all('校准' in x['一句话描述'] for x in summary[-2:])
 decisions=load(REC/'021_decisions.json')
 for i,r in enumerate(scope):
  p=out/(r['stem']+'.md'); txt=p.read_text()
  assert all(s in txt for s in ['## 结论','## 原始数据一致性与查询','## 固定时间与重跑','## 规则问题'])
  assert 0<=int(summary[i]['核实查询条数'])<=5
  assert summary[i]['主要原因类别']==decisions[i]['main']
  assert summary[i]['不确定性四档']==decisions[i]['uncertainty']
  if decisions[i]['ranking']:
   rank=decisions[i]['ranking']; best=max(tuple(x['gain']) for x in rank); cats={x['category'] for x in rank if tuple(x['gain'])==best}
   if len(cats)==1: assert decisions[i]['main']==next(iter(cats)),(i,cats)
   else: assert decisions[i]['main'].startswith('多因并列') and all(c in decisions[i]['main'] for c in cats)
 lock=load(REC/'021_calibration_blind_lock.json'); blind=load(REC/'021_calibration_blind.json'); comparison=load(REC/'021_calibration_comparison.json')
 assert sha(REC/'021_calibration_blind.json')==lock['sha256']
 assert blind['locked_utc']<comparison['compared_utc']
 assert [x['blind'] for x in comparison['comparisons']]==blind['rows']
 raw=load(REC/'021_raw_diagnosis.json'); ne=[x for x in raw['tables'] if x['unevaluable']]
 assert len(raw['tables'])==11 and len(ne)==9
 assert {x['index'] for x in ne}=={x['index'] for x in decisions if x['main']=='不可评估'}
 assert all(any(c['initial_eq_agent'] and not c['gold_eq_initial'] for c in x['checks']) for x in ne)
 runs=[]; failures=[]; sql_count=0
 for p in sorted(REC.glob('021_*reruns_impl-*.json')):
  d=load(p); assert d['runs'][0]['label']=='baseline' and 'comparison' in d['runs'][0]
  baseline=(ROOT/d['runs'][0]['sql_path']).read_text()
  schema=d['basis']['actual_schema']
  assert d['source']==(next(x for x in load(REC/'013_cases.json') if x['task']==d['task'])['agent_database'] if schema=='staging' else d['basis']['gold_database'])
  for run in d['runs']:
   path=ROOT/run['sql_path']; assert path.is_relative_to(ROOT/'data')
   assert sha(path)==run['sql_sha256'],(p.name,run['label'])
   expected_sql=baseline
   for edit in run['edits']:
    start=edit['offset']; assert expected_sql[start:start+len(edit['old'])]==edit['old']
    expected_sql=expected_sql[:start]+edit['new']+expected_sql[start+len(edit['old']):]
   assert path.read_text()==expected_sql,(p.name,run['label'],'unrecorded edits')
   sql_count+=1
   if 'error' in run: failures.append(dict(record=p.name,label=run['label'],error=run['error']));continue
   cmp=run['comparison']; assert [z['level'] for z in cmp['levels']]==['L0','L1','L2','L3']
   for z in cmp['levels']:
    assert z['row_scale']>=0 and z['cell_scale']>=0 and set(z['column_mismatches'])==set(d['basis']['comparison_columns']+d['basis']['key_columns'])
   runs.append(dict(record=p.name,label=run['label'],first_match=cmp['first_match']))
 assert all(x['all_levels_exact_equal'] for x in load(REC/'021_comparator_validation.json'))
 before=load(REC/'021_input_before.json'); after=load(REC/'021_input_after.json')
 assert after['changes']==[] and before['files']==after['files']
 changed=subprocess.check_output(['git','diff','HEAD','--name-only','-z'],cwd=ROOT).decode().split('\0')
 assert not [p for p in changed if p and str(ROOT/p) in before['files']]
 result=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=True,formal_tables=40,calibration_tables=2,new_packages=40,reused_packages=2,summary_columns=len(fields),markdown_files=len(files),input_files=len(before['files']),input_changes=after['changes'],unevaluable_tables=len(ne),sql_files_verified=sql_count,successful_comparisons=len(runs),failed_exploratory_trials=failures,maximum_verification_queries=max(int(x['核实查询条数']) for x in summary),blind_lock_intact=True,ranking_consistent=True,duplicate_key_comparator_cases=12)
 (REC/'021_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='failed_exploratory_trials'},ensure_ascii=False,indent=2));print('failed exploratory trials retained:',len(failures))
if __name__=='__main__':main()
