from review_dacomp_batch022 import *
import csv,hashlib,re,collections,datetime
checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
sc=json.loads((REC/'022_scope.json').read_text());inv=inventory();dec=json.loads((REC/'022_decisions.json').read_text());rs=list(csv.DictReader((REC/'022_annotations/022_summary.csv').open()))
pilot={(x['task'],x['table']) for x in json.loads((REC/'012_sampling.json').read_text())['samples']}
expected={(r['task'],r['table']) for r in csv.DictReader((REC/'013_statuses.csv').open()) if r['task'] in ['impl-012','impl-013','impl-014'] and r['status']=='待标注' and (r['task'],r['table']) not in pilot}
check('38 exact pending nonpilot tables',len(expected)==38 and {(r['task'],r['table']) for r in sc[:38]}==expected)
check('40 rows, calibration last in requested order',len(rs)==40 and [(r['题目'],r['表']) for r in rs[-2:]]==[('impl-005','stg_google_ads__ad_group_stats'),('impl-027','int_xero__invoice_line_items_enriched')] and all('校准' in r['标记'] for r in rs[-2:]))
old=next(csv.reader((REC/'018_annotations/018_summary.csv').open()));check('CSV schema exactly 018 minus previous-version column',list(rs[0])==[x for x in old if x!='与上一版相比是否变化及原因'])
check('40 individual Markdown, 38 new packages',len(list((REC/'022_annotations').glob('*.md')))==40 and len(list((REC/'022_packages').glob('*.md')))==38)
for i,r in enumerate(inv):
 p=pkg(i);check('package identity '+str(i),(r['task'],r['table'],r['layer'])==(p['basic_information']['task'],p['basic_information']['table'],p['basic_information']['layer']))
 check('package originals '+str(i),all(x['text'] in (ROOT/r['path']).read_text() for x in p['agent_final_SQL']+p['gold_SQL_仅供定位差异']))
qs=json.loads((REC/'022_queries.json').read_text())+json.loads((REC/'022_queries_retry.json').read_text());counts=collections.Counter(x['index'] for x in qs);check('query budget includes failures and retries',max(counts.values())<=5)
check('failed verification queries preserved and corrected',sum('error' in x for x in qs)==len(json.loads((REC/'022_queries_retry.json').read_text())))
run_count=0
for path in list(REC.glob('022_reruns_impl-*.json'))+list(REC.glob('022_calibration_supplement_reruns_impl-*.json')):
 d=json.loads(path.read_text());row=next(r for r in inv if r['task']==d['task'] and r['table']==d['basis']['table']);orig=pkg(inv.index(row))['agent_final_SQL'][0]['text'];controlled=orig
 for x in d['clock_control']:controlled=re.sub(x['pattern'],x['replacement'],controlled,flags=re.I)
 for run in d['runs']:
  check('run success '+path.name+run['label'],'error' not in run);s=controlled
  for edit in run['edits']:
   check('single local replacement '+path.name+run['label']+str(edit['offset']),s.count(edit['old'])==1 and s.index(edit['old'])==edit['offset']);s=s.replace(edit['old'],edit['new'],1)
  check('unchanged other bytes '+path.name+run['label'],hashlib.sha256(s.encode()).hexdigest()==run['sql_sha256'] and (ROOT/run['sql_path']).read_text()==s)
  run_count+=1
 for comp in [d['retained']]+[x['comparison'] for x in d['runs']]:
  check('L0–L3 '+path.name,[x['level'] for x in comp['levels']]==['L0','L1','L2','L3'])
  for x in comp['levels']:
   extra=x['agent_only_key_rows']+x['gold_only_key_rows']+x['common_key_agent_excess_rows']+x['common_key_gold_excess_rows'];check('scale arithmetic '+path.name+x['level'],x['row_scale']==extra+x['common_key_different_rows_or_min_pairs'] and x['cell_scale']==extra*x['comparison_column_count_including_keys']+sum(x['column_mismatches'].values()))
lock=json.loads((REC/'022_blind_lock.json').read_text());check('blind lock unchanged',all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in lock['files'].items()))
check('main and uncertainty calibration agreement',all(x['main_consistent'] and x['uncertainty_consistent'] for x in json.loads((REC/'022_calibration_comparison.json').read_text())))
check('015 raw evidence reusable',all(all(f['covered_022'] and f['covered_015'] and f['same_sha256_since_015'] for f in x['physical_files']) and not x['different_tables'] for x in json.loads((REC/'022_raw_reuse_audit.json').read_text())))
for d in dec:
 f=REC/'022_annotations'/('022_'+d['task']+'_'+d['table']+'.md');text=f.read_text();check('required sections '+str(d['index']),all(s in text for s in ['规则问题','核实查询','L0–L3','不确定性','类别门槛']))
 check('decision reason matches summary '+str(d['index']),rs[d['index']]['主要原因类别']==d['main'])
after=REC/'022_input_after.json'
if after.exists():check('immutable input fingerprints',not json.loads(after.read_text())['changes'])
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'checks':len(checks),'reruns_including_baselines_and_blind_combination_diagnostic':run_count,'scope':38,'calibration':2,'max_verification_queries_including_failed':max(counts.values()),'new_packages':38,'annotations':40,'input_after_checked':after.exists(),'checks_list':checks}
(REC/'022_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in result.items() if k!='checks_list'})
