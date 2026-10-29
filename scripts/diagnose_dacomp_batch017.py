from annotate_dacomp_batch017 import *
from collections import Counter

def runq(c,q):
 try:
  r=c.execute(q);return {'sql':q,'columns':[d[0] for d in r.description],'rows':r.fetchall()}
 except Exception as e:return {'sql':q,'error':str(e)}
def full_input_hash28(inventory):
 import hashlib
 results={}
 q='SELECT * FROM raw.youtube_channel_demographics_data ORDER BY ALL NULLS FIRST'
 for side in ['initial','agent']:
  path=inventory['sides'][side]['database']
  with duckdb.connect(path,read_only=True) as c:
   r=c.execute(q);columns=[(d[0],str(d[1])) for d in r.description];h=hashlib.sha256();n=0
   for row in r.fetchall():
    h.update(repr(tuple((type(v).__name__,v) for v in row)).encode());h.update(b'\n');n+=1
   results[side]={'database':path,'sql':q,'columns':columns,'row_count':n,'sha256':h.hexdigest()}
 return {'kind':'complete_table_diagnostic','serialization':'Python repr of (type name,value) tuples, SQL ORDER BY ALL NULLS FIRST, newline separator','sides':results,'initial_agent_columns_equal':results['initial']['columns']==results['agent']['columns'],'initial_agent_row_counts_equal':results['initial']['row_count']==results['agent']['row_count'],'complete_typed_row_multiset_equal':results['initial']['sha256']==results['agent']['sha256']}
def main():
 cases=json.loads((REC/'013_cases.json').read_text());out=[]
 for n,old,new in [(21,' day,',' event_day,'),(27,') names ',') distinct_names ')]:
  p=REC/f'017_queries_impl-{n:03}.json';qs=json.loads(p.read_text());q=qs[0]['sql'].replace(old,new)
  with duckdb.connect(cases[n-1]['agent_database'],read_only=True) as c:x=runq(c,q)
  x.update(id='V2',kind='核实查询',database=cases[n-1]['agent_database'],executed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());qs.append(x);save(p,qs);print(n,x,flush=True)
 # Only gold-dependent diagnostics below; not tests of an agent-visible P.
 n=21;b=package(n)['differences'];q="SELECT person_id,source_relation,count(*) n,count(distinct cast(occurred_at AS DATE)) days,min(cast(occurred_at AS DATE)) first_day,max(cast(occurred_at AS DATE)) last_day FROM staging.stg_klaviyo__event GROUP BY 1,2 ORDER BY 1,2"
 with duckdb.connect(b['gold_database'],read_only=True) as c:x=runq(c,q)
 out.append(dict(task='impl-021',kind='诊断查询',database=b['gold_database'],**x))
 n=28;inventory=json.loads((REC/'015_raw_impl-028.json').read_text());n28=[];canon=[]
 for side in ['initial','agent','gold']:
  path=inventory['sides'][side]['database'];table='channel_demographics_a_1' if side=='gold' else 'youtube_channel_demographics_data'
  with duckdb.connect(path,read_only=True) as c:
   for q in ["SELECT table_name FROM information_schema.tables WHERE table_schema='raw' ORDER BY 1", f'SELECT count(*) n,min(cast(date AS VARCHAR)) first_day,max(cast(date AS VARCHAR)) last_day,count(distinct video_id) videos FROM raw.{table}']:
    n28.append(dict(side=side,kind='诊断查询',database=path,**runq(c,q)))
   q=f'SELECT date,channel_id,video_id,country_code,age_group,gender,views_percentage FROM raw.{table}';rs=c.execute(q).fetchall();canon.append((side,Counter(tuple(None if v is None else str(v) for v in row) for row in rs)))
   n28.append({'side':side,'kind':'诊断查询','database':path,'sql':q,'rows':len(rs),'result_storage':'comparison counts only, not full original rows'})
 initial,agent,gold=[x[1] for x in canon];n28.append({'initial_agent_same_selected_row_multiset':initial==agent,'agent_only_vs_gold_rows':sum((agent-gold).values()),'gold_only_vs_agent_rows':sum((gold-agent).values()),'note':'same semantic column names; exact Python scalar text, no invented source-name equivalence'})
 n28.append(full_input_hash28(inventory))
 save(REC/'017_ineligible_diagnostic_impl-028.json',n28)
 # Relevant raw eligibility uses both agent SQL and contract/gold dependency names.
 edges=[json.loads(l) for l in (REC/'015_lineage_edges.jsonl').read_text().splitlines() if l]
 audits={}
 for n in range(21,31):
  p=package(n);b=p['differences'];inventory=json.loads((REC/f'015_raw_impl-{n:03}.json').read_text());todo=[b['actual_schema']+'.'+b['table']];visited=set();refs=set()
  for k in ['agent_final_SQL','gold_SQL_仅供定位差异']:refs.update(re.findall(r'\braw\.[\w]+',Path(p[k][0]['path']).read_text()))
  while todo:
   t=todo.pop()
   if t in visited:continue
   visited.add(t)
   if t.startswith('raw.'):refs.add(t)
   todo.extend(e['source'] for e in edges if e['task']==f'impl-{n:03}' and e['target'].split('.')[-1]==t.split('.')[-1])
  audits[f'impl-{n:03}']={'raw_dependencies':sorted(refs),'source':f'records/015_raw_impl-{n:03}.json','comparisons':[{k:v for k,v in r.items() if k not in ['gold','agent','initial']} for r in inventory['comparisons'] if r['raw_table'] in refs]}
 save(REC/'017_dependency_raw_audit.json',audits);save(REC/'017_diagnostics.json',out);print('diagnostics complete',flush=True)
if __name__=='__main__':main()
