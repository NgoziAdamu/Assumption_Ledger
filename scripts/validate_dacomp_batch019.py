"""Delivery integrity: scope, schema, U gate, immutable-byte trials and evidence quotes."""
from pathlib import Path
import json,csv,hashlib,re
ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records';inv=json.loads((REC/'019_package_inventory.json').read_text());scope=json.loads((REC/'019_scope.json').read_text());rows=list(csv.DictReader((REC/'019_annotations/019_summary.csv').open()));checks={};checks['45_annotations']=len(rows)==len(inv)==len(scope)==len(list((REC/'019_annotations').glob('*.md')))==45
pilot={(x['task'],x['table']) for x in json.loads((REC/'012_sampling.json').read_text())['samples']};expected={(r['task'],r['table']) for r in csv.DictReader((REC/'013_statuses.csv').open()) if r['task'] in [f'impl-{i:03}' for i in range(1,6)] and r['status']=='待标注' and (r['task'],r['table']) not in pilot};checks['exact_43_scope']={(r['题目'],r['表']) for r in rows[:-2]}==expected and len(expected)==43
checks['calibration_last']=[x['表'] for x in rows[-2:]]==['int_asana__task_projects','int_klaviyo__person_metrics'] and all(x['一句话描述'].startswith('【校准】') for x in rows[-2:]);old=next(csv.DictReader((REC/'018_annotations/018_summary.csv').open()));checks['exact_csv_fields']=list(rows[0])==[x for x in old if x!='与上一版相比是否变化及原因'];checks['verification_limit']=all(int(x['核实查询条数'])<=5 for x in rows)
before=json.loads((REC/'019_input_before.json').read_text());supp=json.loads((REC/'019_input_supplement_before.json').read_text());before['files'].update(supp['files']);missing=[];bad=[];trials=0
for r in inv:
 d=json.loads((ROOT/r['full_json']).read_text());run=json.loads((REC/('019_reruns_'+r['task']+'_'+r['table']+'.json')).read_text());orig=d['agent_final_SQL'][0]['text'];baseline=orig
 if r['table'] in supp['affected_tables']:
  from datetime import datetime
  checks['post_supplement_'+r['table']]=run['started_utc']>=supp['started_utc'] and (ROOT/r['full_json']).stat().st_mtime>=datetime.fromisoformat(supp['started_utc']).timestamp()
 for ce in run.get('clock_control',[]):baseline=re.sub(ce['pattern'],ce['replacement'],baseline,flags=re.I)
 for trial in run['runs']:
  trials+=1
  if trial.get('error'):bad.append((r['table'],trial['label'],'error'));continue
  expectedsql=baseline
  for e in trial['edits']:
   if expectedsql.count(e['old'])!=1:bad.append((r['table'],trial['label'],'nonunique edit'))
   expectedsql=expectedsql.replace(e['old'],e['new'],1)
  p=ROOT/trial['sql_path'];actual=p.read_text()
  if actual!=expectedsql or hashlib.sha256(p.read_bytes()).hexdigest()!=trial['sql_sha256']:bad.append((r['table'],trial['label'],'bytes mismatch'))
  if len(trial['comparison']['levels'])!=4:bad.append((r['table'],trial['label'],'levels'))
 for p in d['original_files']['paths']:
  if str(Path(p)) not in before['files']:missing.append(p)
 checks['raw_'+r['table']]=run['source']==(json.loads((REC/'013_cases.json').read_text())[int(r['task'][-3:])-1]['agent_database'] if r['layer']=='staging' else d['differences']['gold_database'])
checks['successful_byte_exact_trials']=not bad;checks['original_inputs_in_snapshot']=not missing
uq=json.loads((REC/'019_uncertainty.json').read_text());quote_bad=[]
for u in uq:
 e=json.loads((ROOT/u['path']).read_text());text=e.get('message','') if u['field']=='message' else e['args']['final_thought']
 if text[u['start_offset']:u['start_offset']+len(u['quote'])]!=u['quote']:quote_bad.append(u['table'])
checks['trace_quotes_exact']=not quote_bad;checks['U_gate']=all(x['重跑是否满足 U 的第 4 个条件']=='是' for x in rows if x['主要原因类别']=='U');checks['43_slim_packages']=len(list((REC/'019_packages').glob('*.md')))==43
# Verify deterministic source/count conservation for all scales.
scale_bad=[]
for p in REC.glob('019_reruns_*.json'):
 for r in json.loads(p.read_text())['runs']:
  for x in r['comparison']['levels']:
   a=x['agent_only_key_rows']+x['gold_only_key_rows']+x['common_key_agent_excess_rows']+x['common_key_gold_excess_rows'];nr=a+x['common_key_different_rows_or_min_pairs'];nc=a*x['comparison_column_count_including_keys']+sum(x['column_mismatches'].values())
   if nr!=x['row_scale'] or nc!=x['cell_scale']:scale_bad.append([p.name,r['label'],x['level']])
checks['scale_arithmetic']=not scale_bad
out=dict(passed=all(checks.values()),checks=checks,trial_count=trials,byte_errors=bad,missing_fingerprints=sorted(set(missing)),quote_errors=quote_bad,scale_errors=scale_bad);(REC/'019_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'},ensure_ascii=False,indent=2));assert out['passed']
