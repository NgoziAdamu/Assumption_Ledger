"""Select exact 019 scope; reuse 012 evidence extraction and 013 verbatim renderer."""
import csv,json,inspect
from pathlib import Path
import build_dacomp_annotation_packages as full
from build_dacomp_slim_packages import render
ROOT=full.ROOT; REC=full.RECORDS

def main():
 assert (REC/'019_input_before.json').exists()
 pilot={(x['task'],x['table']) for x in json.loads((REC/'012_sampling.json').read_text())['samples']}
 rows=[r for r in csv.DictReader((REC/'013_statuses.csv').open()) if r['task'] in [f'impl-{n:03}' for n in range(1,6)] and r['status']=='待标注' and (r['task'],r['table']) not in pilot]
 for task,table in [('impl-008','int_asana__task_projects'),('impl-021','int_klaviyo__person_metrics')]:
  r=next(r for r in csv.DictReader((REC/'013_statuses.csv').open()) if r['task']==task and r['table']==table);rows.append({**r,'purpose':'校准'})
 for r in rows:r.setdefault('purpose','全量');r['stem']='019_'+r['task']+'_'+r['table']
 full.save(REC/'019_scope.json',rows)
 dest=REC/'019_packages';dest.mkdir(exist_ok=True); inventory=[]
 src=inspect.getsource(full.worker).replace('def worker(task,work):','def worker(task,work,sample):')
 src='\n'.join(line for line in src.splitlines() if "sample=next(r for r in json.loads" not in line)
 ns=dict(vars(full));
 result_src=inspect.getsource(full.result_sentences).replace("candidates=sorted(root.rglob('result.md'))","candidates=[root/'result.md'] if (root/'result.md').exists() else sorted(root.rglob('result.md'))")
 exec(result_src,ns);exec(src,ns)
 for r in rows:
  existing=list((REC/'013_packages').glob('*'+r['task']+'*'+r['table']+'*.md'))
  if existing:
   inventory.append({**r,'path':str(existing[0].relative_to(ROOT)),'full_json':str(next((REC/'012_packages').glob('*'+r['task']+'*'+r['table']+'*.json')).relative_to(ROOT))});continue
  work=ROOT/'data/019_packages_work'/r['stem'];work.mkdir(parents=True,exist_ok=True)
  if not (work/(r['stem']+'.json')).exists():ns['worker'](r['task'],work,{**r,'package_stem':r['stem']})
  doc=json.loads((work/(r['stem']+'.json')).read_text());text,summary=render(doc,r)
  if summary['without_SQL_contract_original_characters']>15000:text,summary=render(doc,r,examples=1,key_examples=1,evidence_limit=1)
  text=text.replace('records/012_packages/'+r['stem']+'.json',str((work/(r['stem']+'.json')).relative_to(ROOT)))
  (dest/(r['stem']+'.md')).write_text(text)
  inventory.append({**r,'path':str((dest/(r['stem']+'.md')).relative_to(ROOT)),'full_json':str((work/(r['stem']+'.json')).relative_to(ROOT)),**summary});print(r['stem'],flush=True)
 full.save(REC/'019_package_inventory.json',inventory)
if __name__=='__main__':main()
