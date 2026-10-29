from annotate_dacomp_batch017 import *
import csv,hashlib

def main():
 before=json.loads((REC/'017_input_before.json').read_text());start=before['completed_utc'];checks=[];u=json.loads((REC/'017_uncertainty_audit.json').read_text());a=json.loads((REC/'017_decisions.json').read_text());rows=list(csv.DictReader((REC/'017_annotations/017_summary.csv').open()))
 assert len(rows)==10 and len(list((REC/'017_annotations').glob('*.md')))==10
 qcount=0
 for n in range(21,31):
  task=f'impl-{n:03}';p=package(n);r=json.loads((REC/f'017_reruns_{task}.json').read_text());assert r['started_utc']>start
  original=Path(p['agent_final_SQL'][0]['path']).read_text();controlled=original
  for e in r.get('clock_control',[]):controlled=re.sub(e['pattern'],e['replacement'],controlled,flags=re.I)
  for t in r['runs']:
   assert not t.get('error'),(n,t)
   expected=controlled
   for e in t['edits']:
    assert expected.count(e['old'])==1 and expected.index(e['old'])==e['offset'],(n,t['label'])
    expected=expected.replace(e['old'],e['new'],1)
   actual=(ROOT/t['sql_path']).read_text();assert expected==actual,(n,t['label'],'extra edits');assert hashlib.sha256(actual.encode()).hexdigest()==t['sql_sha256']
   c=t['comparison'];assert c['first_match']==next((x['level'] for x in c['levels'] if x['whole_match']),None)
   for x in c['levels']:
    extra=x['agent_only_key_rows']+x['gold_only_key_rows']+x['common_key_agent_excess_rows']+x['common_key_gold_excess_rows'];colcount=len(set(r['basis']['key_columns']+r['basis']['comparison_columns']))
    assert x['row_scale']==extra+x['common_key_different_rows_or_min_pairs']
    assert x['cell_scale']==extra*colcount+sum(x['column_mismatches'].values())
    assert x['cell_scale']>=x['row_scale']
    assert x['whole_match']==(x['row_scale']==x['cell_scale']==0)
   checks.append({'task':task,'trial':t['label'],'exact_declared_edits_only':True,'scales_valid':True})
  qs=json.loads((REC/f'017_queries_{task}.json').read_text());assert len(qs)<=5;qcount+=len(qs);assert all(q['executed_utc']>start for q in qs)
  row=rows[n-21];assert int(row['核实查询条数'])==len(qs) and row['主要原因类别']==a[str(n)]['cat']
  assert u[task]['status'] in ['已提到','看到了但没提','没有迹象']
  assert row['agent 是否意识到或提到了与本表差异相关的不确定性'].startswith(u[task]['status'])
  es={x['id']:x for x in json.loads((REC/f'017_trace_{task}.json').read_text())}
  for e in u[task]['evidence']:
   source=es[e['event']]['args']['final_thought'] if e['field']=='args.final_thought' else es[e['event']]['content'];assert e['quote'] in source,(n,e['event'])
  if u[task]['status']=='已提到':assert any(e['field']=='args.final_thought' for e in u[task]['evidence'])
  if n!=28:
   base=r['runs'][0]['comparison']['levels'][0];trials=r['runs'][1:];gains=[base['row_scale']-t['comparison']['levels'][0]['row_scale'] for t in trials];mode='row_scale' if len(set(gains))>1 else 'cell_scale';maximum=max(base[mode]-t['comparison']['levels'][0][mode] for t in trials)
   for label in a[str(n)]['primary']:
    trial=next(t for t in trials if t['label']==label);assert base[mode]-trial['comparison']['levels'][0][mode]==maximum,(n,label,mode)
  md=next((REC/'017_annotations').glob(f'017_{task}_*.md')).read_text();assert '## 规则问题' in md
  for link in re.findall(r'\]\(([^)]+)\)',md):
   if link=='../017_input_after.json' and not (REC/'017_input_after.json').exists():continue
   assert ((REC/'017_annotations')/link).exists(),(n,link)
 raw=json.loads((REC/'017_ineligible_diagnostic_impl-028.json').read_text())[-1];assert raw['complete_typed_row_multiset_equal'] and raw['initial_agent_columns_equal']
 if (REC/'017_input_after.json').exists():assert not json.loads((REC/'017_input_after.json').read_text())['changes']
 ledger=[]
 for file in ['017_rerun.log','017_supplement.log']:
  for line in (REC/file).read_text().splitlines():
   m=re.fullmatch(r'(\d+) (\w+) done\s*',line)
   if m:ledger.append({'task':f'impl-{int(m[1]):03}','trial':m[2],'execution_log':file})
 save(REC/'017_validation.json',{'all_passed':True,'annotation_count':10,'verification_queries_including_failed_attempts':qcount,'distinct_sql_trials':len(checks),'logged_sql_executions':len(ledger),'snapshot_completed_before_queries_and_reruns':True,'verbatim_uncertainty_evidence_checked':True,'checks':checks,'execution_ledger':ledger,'repeat_note':'026追加DATE类型对照时重跑了相同baseline和date_day_type；这两项前后数值一致，JSON保留最后结果，日志保留39次执行记录。'})
 print('PASS',len(checks),'SQL trials;',qcount,'verification attempts; snapshot order; uncertainty quotations; raw identity',flush=True)
if __name__=='__main__':main()
