from annotate_dacomp_batch014 import *
from run_dacomp_batch014 import P
for n,queries in {
4:[('D_clock',"SELECT min(created_date),max(created_date),min(history_unique_key),max(history_unique_key) FROM staging.stg_salesforce__contact_history"),('D_activity',"SELECT contact_id,last_activity_date FROM staging.stg_salesforce__contact_history WHERE last_activity_date IS NULL")],
9:[('V2',"SELECT country_code_numeric,count(*) n,list(country_code_alpha_2 ORDER BY country_code_alpha_2) codes FROM raw.google_play__country_codes GROUP BY 1 HAVING count(*)>1 ORDER BY 1")],
10:[('D_ids',"SELECT count(*) n,count(distinct guid) guids,count(*) FILTER(WHERE CAST(guid AS VARCHAR) LIKE 'FORM_%') form_ids,min(CAST(guid AS VARCHAR)),max(CAST(guid AS VARCHAR)) FROM raw.form_data")]
}.items():
 pkg=package(n);case=json.loads((REC/'013_cases.json').read_text())[n-1];p=REC/f'014_queries_impl-{n:03}.json';out=json.loads(p.read_text())
 for id,q in queries:
  path=case['agent_database'] if id.startswith('V') else pkg['differences']['gold_database']
  with duckdb.connect(path,read_only=True) as c:
   r=c.execute(q);cols=[x[0] for x in r.description];rows=r.fetchall()
   out.append({'id':id,'kind':'核实查询' if id.startswith('V') else '诊断查询','database':path,'sql':q,'columns':cols,'rows':rows})
   print(n,id,rows[:5])
 save(p,out)
 if n==4:
  key=out[-2]['rows'][0][2];suffix=key.split('_',1)[1];day=suffix[:10]
  P[4].append(('history_key_frozen',[('CAST(hash("_fivetran_start", "_fivetran_end") AS VARCHAR)',"concat(id, '_', '"+suffix+"')")]))
  P[4].append(('activity_rule_gold_day',[('CAST("last_activity_date" AS DATE) AS last_activity_date',f"CASE WHEN last_activity_date > DATE '{day}' OR last_activity_date < DATE '2020-01-01' THEN NULL ELSE CAST(last_activity_date AS DATE) END AS last_activity_date")]))
P[9].extend([('country_value_only',[('CAST(cc.country_code_alpha_2 AS VARCHAR)','CAST(country_region AS VARCHAR)')]),('unique_lookup', [('LEFT JOIN raw.google_play__country_codes AS cc','LEFT JOIN (SELECT country_code_numeric,min(country_code_alpha_2) AS country_code_alpha_2 FROM raw.google_play__country_codes GROUP BY country_code_numeric) AS cc')])])
for n in [4,9]:reruns(n,P[n])
# Per-output-cell, not full-row, diagnostic for the tied aggregate order.
b=package(8)['differences']
with duckdb.connect(b['prediction_database'],read_only=True) as a,duckdb.connect(b['gold_database'],read_only=True) as g:
 q='SELECT task_id, projects_sections FROM intermediate.int_asana__task_projects'
 ar=dict(a.execute(q).fetchall());gr=dict(g.execute(q).fetchall());different=sum(ar[k]!=gr[k] for k in ar);equalbags=sum(ar[k]!=gr[k] and Counter((ar[k] or '').split(', '))==Counter((gr[k] or '').split(', ')) for k in ar)
 save(REC/'014_order_diagnostic_impl-008.json',{'sql':q,'databases':[b['prediction_database'],b['gold_database']],'different_strings':different,'different_strings_equal_pair_multisets':equalbags,'operation':"split exact ', ' delimiter and compare Counters; diagnostic, not official score"})
