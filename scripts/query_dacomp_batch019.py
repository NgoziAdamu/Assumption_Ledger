"""Aggregate-only verification and O diagnostics; originals opened read-only."""
import json,re,duckdb
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records';inv=json.loads((REC/'019_package_inventory.json').read_text());cases=json.loads((REC/'013_cases.json').read_text());out=[]
def query(r,kind,db,q):
 try:
  with duckdb.connect(str(db),read_only=True) as c:
   z=c.execute(q);v=z.fetchall();out.append(dict(task=r['task'],table=r['table'],kind=kind,database=str(db),sql=q,columns=[x[0] for x in z.description],result=v))
 except Exception as e:out.append(dict(task=r['task'],table=r['table'],kind=kind,sql=q,error=str(e)))
for r in inv:
 if r['purpose']=='校准':continue
 d=json.loads((ROOT/r['full_json']).read_text());t=r['table'];n=int(r['task'][-3:]);case=cases[n-1];b=d['differences'];db=case['agent_database'];gold=b['gold_database']
 if t=='stg_pendo__user':query(r,'核实',db,"SELECT count(*) n,count(*) FILTER(WHERE deleted_at IS NOT NULL AND deleted_at<>'' AND try_cast(deleted_at AS TIMESTAMP) IS NULL AND try_cast(substring(deleted_at,1,23) AS TIMESTAMP) IS NOT NULL) failed_direct FROM raw.user")
 if t=='stg_pendo__visitor_history':query(r,'核实',db,"SELECT count(*) n,count(*) FILTER(WHERE try_cast(last_visit AS TIMESTAMP) IS NULL AND try_cast(substring(last_visit,1,23) AS TIMESTAMP) IS NOT NULL) failed_direct FROM raw.visitor_history")
 if t=='customer360__customer':
  query(r,'核实',db,'SELECT count(*) duplicate_keys,sum(n-1) excess_rows FROM (SELECT m.customer360_id,count(*) n FROM marts.customer360__mapping m JOIN marts.customer360__summary s USING(customer360_id) GROUP BY m.customer360_id HAVING count(*)>1)')
 if t=='stg_customer360__country_codes':query(r,'诊断',gold,'SELECT count(*) duplicate_keys,sum(n-1) excess_rows FROM (SELECT country_code_alpha_2,count(*) n FROM staging.stg_customer360__country_codes GROUP BY 1 HAVING count(*)>1)')
 if t in ['customer360__status','customer360__updates','customer360__phone']:
  cols=b['key_columns']+b['comparison_columns'];cols=list(dict.fromkeys(cols));express=[]
  for col in cols:
   if t.endswith('__phone') and col=='index':continue
   express.append(f"list_sort(string_split(\"{col}\", ', ')) AS \"{col}\"" if col in ['source_systems','updated_by_systems','update_types'] else '"'+col+'"')
  select=','.join(express);work=ROOT/'data/019_work'/(r['task']+'_'+t)/'work.duckdb'
  if work.exists():
   with duckdb.connect(str(work),read_only=True) as c:
    c.execute("ATTACH '"+gold+"' AS g (READ_ONLY)");a=f'SELECT {select} FROM {b["actual_schema"]}.{t}';z=f'SELECT {select} FROM g.{b["actual_schema"]}.{t}';q=f'SELECT (SELECT count(*) FROM (({a}) EXCEPT ALL ({z}))) agent_only,(SELECT count(*) FROM (({z}) EXCEPT ALL ({a}))) gold_only'
    out.append(dict(task=r['task'],table=t,kind='诊断',sql=q,result=c.execute(q).fetchall()))
 if t in ['int_lever__posting_applications','salesforce__account_daily_history','salesforce__contact_daily_history']:
  source={'int_lever__posting_applications':'staging.stg_lever__application','salesforce__account_daily_history':'staging.stg_salesforce__account_history','salesforce__contact_daily_history':'staging.stg_salesforce__contact_history'}[t];ident='posting_id' if n==1 else 'account_id' if 'account' in t else 'contact_id';date='created_at' if n==1 else 'created_date'
  query(r,'核实',db,f'SELECT count(*) tied_groups,sum(n-1) excess_rows FROM (SELECT {ident},{date},count(*) n FROM {source} GROUP BY ALL HAVING count(*)>1)')
  # Each output's varying fields must occur on an admissible maximal-time input record, not merely an arbitrary tie.
  fields=['posting_hiring_manager_user_id'] if n==1 else [c for c in b['comparison_columns'] if c!='snapshot_date'];fields=list(dict.fromkeys([ident]+fields));pred=b['prediction_database']
  with duckdb.connect(gold,read_only=True) as c:
   c.execute("ATTACH '"+pred+"' AS a (READ_ONLY)")
   cond=' AND '.join(f'o."{x}" IS NOT DISTINCT FROM s."{x}"' for x in fields)
   filt='' if n==1 else ' WHERE coalesce(is_deleted,false)=false'
   partition=ident if n==1 else ident+',cast('+date+' AS DATE)'
   admissible=f'SELECT * FROM {source}{filt} QUALIFY rank() OVER(PARTITION BY {partition} ORDER BY {date} DESC)=1'
   for side in ['a.','']:
    q=f'SELECT count(*) non_admissible FROM {side}{b["actual_schema"]}.{t} o WHERE NOT EXISTS(SELECT 1 FROM ({admissible}) s WHERE {cond})'
    out.append(dict(task=r['task'],table=t,kind='诊断',side=side or 'gold',sql=q,result=c.execute(q).fetchall()))
 if t=='int_customer360__risk_assessment':
  for side,path in [('历史agent比较',b['prediction_database']),('gold',gold)]:query(r,'诊断',path,'SELECT typeof(intervention_success_probability) AS type,count(*) n FROM intermediate.int_customer360__risk_assessment GROUP BY ALL')
 if t=='int_google_ads__account_performance_metrics':
  for side,path in [('agent',db),('gold',gold)]:
   query(r,'诊断',path,'DESCRIBE staging.stg_google_ads__account_stats')
   query(r,'核实' if side=='agent' else '诊断',path,"SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_google_ads__account_stats' AND column_name='cost_per_conversion'")
(REC/'019_queries.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n');print('queries',len(out),'errors',[x for x in out if 'error' in x])
