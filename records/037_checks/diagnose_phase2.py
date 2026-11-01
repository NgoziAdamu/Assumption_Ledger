from pathlib import Path
import json,duckdb
R=Path(__file__).resolve().parents[2];C=json.loads((R/'records/037_checks/evidence_catalog.json').read_text());out=[]
queries={
'impl-001_lever__hiring_manager_scorecard':["SELECT DISTINCT development_recommendations FROM marts.lever__hiring_manager_scorecard", "SELECT feedback_completion_rate_managed,hiring_specialization,overall_performance_score,count(*) n FROM marts.lever__hiring_manager_scorecard GROUP BY ALL"],
'impl-001_lever__departmental_hiring_trends':["SELECT DISTINCT department_strength,referral_rate,offer_acceptance_rate,avg_candidate_experience_score,avg_time_to_hire_days,cost_efficiency_tier FROM marts.lever__departmental_hiring_trends"],
'impl-002_int_pendo__product_health_metrics':["SELECT DISTINCT primary_improvement_area FROM intermediate.int_pendo__product_health_metrics"],
'impl-002_int_pendo__data_quality_checks':["SELECT * FROM intermediate.int_pendo__data_quality_checks"]}
for id,qs in queries.items():
 path=C[id]['basis']['gold_database']
 with duckdb.connect(path,read_only=True) as con:
  for sql in qs:
   cur=con.execute(sql);out.append(dict(object=id,kind='诊断，标准答案仅定位差异与未规定的文字表示；不作为契约',database=path,read_only=True,sql=sql,columns=[x[0] for x in cur.description],rows=cur.fetchall()))
(R/'records/037_checks/additional_diagnostics.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n')
for x in out:print(x['object'],x['columns'],x['rows'][:10])
