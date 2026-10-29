from annotate_dacomp_batch014 import *
def run():
 # Comparator checks distinguish absent keys, duplicate multiplicity and numeric tolerances.
 checks=[]
 for name,pr,gr,expected in [('key_only',[(1,1)],[(2,1)],None),('numeric',[(1,'1.00')],[(1,'1')],'L1'),('rounded',[(1,'1.001')],[(1,'1.002')],'L2'),('duplicate',[(1,'x'),(1,'x')],[(1,'x')],None)]:
  with duckdb.connect() as a,duckdb.connect() as g:
   for c,rows in [(a,pr),(g,gr)]:
    c.execute('create schema staging');c.execute('create table staging.t(k integer,v varchar)');c.executemany('insert into staging.t values (?,?)',rows)
   r=compare(a,g,'staging','t',['v'],['k']);assert r['first_match']==expected,(name,r);checks.append(name)
 # Original bytes, schema and source preservation are verified separately by fingerprints.
 for n in range(1,11):
  r=json.loads((REC/f'014_reruns_impl-{n:03}.json').read_text());orig=Path(package(n)['agent_final_SQL'][0]['path']).read_text()
  for trial in r['runs']:
   assert 'error' not in trial,(n,trial)
   s=orig
   for edit in trial['edits']:assert s.count(edit['old'])==1;s=s.replace(edit['old'],edit['new'],1)
   assert (ROOT/trial['sql_path']).read_text()==s
   assert len(trial['comparison']['levels'])==4
  queries=json.loads((REC/f'014_queries_impl-{n:03}.json').read_text());assert sum(q['kind']=='核实查询' for q in queries)<=5
 assert (ROOT/'docs/标注手册_v0.md').read_bytes()==Path('/mnt/c/Users/jucc116/Desktop/标注手册_v0.md').read_bytes()
 save(REC/'014_validation.json',{'comparator_checks_passed':checks,'tables':10,'patch_bytes_verified':True,'query_budget_verified':True,'manual_exact_bytes':True})
 print('Validation passed',checks)
if __name__=='__main__':run()
