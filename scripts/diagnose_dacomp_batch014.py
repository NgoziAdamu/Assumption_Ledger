from annotate_dacomp_batch014 import *
def main():
 raw={1:'application',2:'guide_event',4:'contact_history',5:'ad_group_stats_data',6:'reddit_ads_campaign_report_data',7:'sales_subscription_event_summary',9:'stats_store_performance_country',10:'form_data'}
 for n,table in raw.items():
  pkg=package(n);case=json.loads((REC/'013_cases.json').read_text())[n-1];p=REC/f'014_queries_impl-{n:03}.json';out=json.loads(p.read_text())
  with duckdb.connect(case['agent_database'],read_only=True) as a,duckdb.connect(pkg['differences']['gold_database'],read_only=True) as g:
   q=f'SELECT * FROM raw.{table}'
   # Diagnostic full raw multiset comparison; retain only aggregate counts, not raw datasets.
   ra=a.execute(q);cols=[x[0] for x in ra.description];ar=ra.fetchall();rg=g.execute(q);gcols=[x[0] for x in rg.description];gr=rg.fetchall()
   if cols==gcols:
    ac,gc=Counter(map(tuple,ar)),Counter(map(tuple,gr));res={'columns_identical':True,'agent_rows':len(ar),'gold_rows':len(gr),'agent_only_rows':sum((ac-gc).values()),'gold_only_rows':sum((gc-ac).values())}
   else:res={'columns_identical':False,'agent_columns':cols,'gold_columns':gcols,'agent_rows':len(ar),'gold_rows':len(gr)}
   out.append({'id':'D_raw','kind':'诊断查询','sql':q,'databases':[case['agent_database'],pkg['differences']['gold_database']],'result':res,'operation':'Python Counter of full typed rows, exact multiset difference'})
   if n==10:
    q="SELECT count(*) n,count(distinct guid) guids,min(cast(guid as varchar)) min_guid,max(cast(guid as varchar)) max_guid FROM raw.form_data";r=g.execute(q);out.append({'id':'D2','kind':'诊断查询','database':pkg['differences']['gold_database'],'sql':q,'columns':[x[0] for x in r.description],'rows':r.fetchall()})
  save(p,out);print(n,res,flush=True)
 # O diagnostics: compare stored outputs after relaxing only the underspecified rank or key.
 for n,remove in [(3,['rank']),(4,[]),(8,['projects_sections'])]:
  b=package(n)['differences']
  with duckdb.connect(b['prediction_database'],read_only=True) as a,duckdb.connect(b['gold_database'],read_only=True) as g:
   cols=[c for c in b['comparison_columns'] if c not in remove]
   result=compare(a,g,b['actual_schema'],b['table'],cols,b['key_columns'])
  save(REC/f'014_relaxed_impl-{n:03}.json',{'diagnostic_only':True,'excluded_columns':remove,'comparison':result})
if __name__=='__main__':main()
