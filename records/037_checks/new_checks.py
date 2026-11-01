"""Single-location interventions; original DBs READ_ONLY, private tables in memory."""
from pathlib import Path
import sys,json,re,hashlib,datetime
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'scripts'),str(R/'data/005_tools')]
from annotate_dacomp_batch016 import compare_sql,udf_forms
import duckdb
CAT=json.loads((R/'records/037_checks/evidence_catalog.json').read_text())
PLAN={}
def add(id,label,old,new,why,kind='单改重跑'):
 PLAN.setdefault(id,[]).append(dict(label=label,old=old,new=new,why=why,kind=kind))
id='impl-001_lever__hiring_manager_scorecard'
for col in ['total_applications','posting_performance_score']:
 add(id,'unweighted_'+col,'avg(pp.'+col+')','(SELECT avg(pp2.'+col+') FROM staging.stg_lever__posting p2 LEFT JOIN intermediate.int_lever__posting_performance pp2 USING(posting_id) WHERE p2.owner_user_id=p.owner_user_id)','契约按posting聚合；移除application扩行对均值的权重，仅替换一个聚合表达式。')
id='impl-002_pendo__customer_lifecycle_insights'
old="WHEN l.lifecycle_stage='New User' AND r.rfm_segment='New Customers' THEN 'Fresh Prospect' ELSE 'Standard Customer' END customer_segment_label"
new="WHEN l.lifecycle_stage='New User' AND r.rfm_segment='New Customers' THEN 'Fresh Prospect' WHEN l.lifecycle_stage='Growing User' AND r.rfm_segment='Potential Loyalists' THEN 'Rising Star' WHEN l.churn_risk_level IN ('High Risk','Medium Risk') AND r.rfm_segment='At Risk' THEN 'Save Immediately' WHEN l.lifecycle_stage='At Risk' AND r.action_priority='Re-engagement' THEN 'Rescue Mission' WHEN l.lifecycle_stage='Churned' THEN 'Lost Customer' ELSE 'Standard Customer' END customer_segment_label"
add(id,'customer_segment_branches',old,new,'只补齐契约已写明的customer_segment_label四个遗漏分支，不修改其他默认列。')
add(id,'recommended_next_action',"'Standard nurturing; Regular check-ins; Content engagement' recommended_next_action", "CASE WHEN l.lifecycle_stage='Power User' AND r.rfm_segment='Champions' THEN 'Leverage as advocate; Offer exclusive features; Request testimonials' WHEN l.is_new_user AND r.rfm_segment='New Customers' THEN 'Intensive onboarding; Feature education; Success manager assignment' WHEN l.needs_attention AND r.action_priority='Re-engagement' THEN 'Personalized outreach; Usage analysis; Feature recommendations' WHEN l.churn_risk_level='High Risk' THEN 'Immediate intervention; Executive outreach; Value demonstration' WHEN l.lifecycle_stage='Growing User' THEN 'Feature adoption campaign; Usage optimization; Upgrade path guidance' WHEN r.rfm_segment='Loyal Customers' THEN 'Upsell opportunities; Loyalty rewards; Advanced feature training' ELSE 'Standard nurturing; Regular check-ins; Content engagement' END recommended_next_action",'将单个固定输出改为契约逐字规则。')
add(id,'account_influence_level',"'Single Account User' account_influence_level","CASE WHEN v.count_associated_accounts>3 THEN 'Multi-Account Influencer' WHEN v.count_associated_accounts>1 THEN 'Cross-Account User' ELSE 'Single Account User' END account_influence_level",'核验未覆盖的常量输出；即使净改善0也保留非原因标记。')
id='impl-003_customer360__conversion_funnel_analysis'
add(id,'presentation_round_revenue',None,'SELECT * REPLACE(round(revenue_velocity_monthly,2) AS revenue_velocity_monthly) FROM result_baseline','只对最终输出舍入，不改变计算链，检验Form Mismatch。','呈现诊断')
id='impl-005_google_ads__executive_dashboard'
add(id,'trending_null','(spend_wow_growth_pct>50 OR conversions_wow_growth_pct< -30) trending_alert','coalesce((spend_wow_growth_pct>50 OR conversions_wow_growth_pct< -30),false) trending_alert','契约trending_alert的else false；核实SQL原片段后执行。')
from additional_plan import extend
extend(add,CAT)
from extended_plan import extend as extend_more
extend_more(add,CAT)
from funnel_plan import extend as extend_funnel
extend_funnel(add,CAT)
from final_plan import extend as extend_final
extend_final(add,CAT)
# Emit exact edits for audit before execution.
(R/'records/037_checks/new_patch_plan.json').write_text(json.dumps(PLAN,ensure_ascii=False,indent=2)+'\n')
def run(id):
 o=CAT[id];record=json.loads((R/o['rerun_path']).read_text());b=o['basis'];orig=(R/record['runs'][0]['sql_path']).read_text()
 for p in PLAN[id]:
  for clock in o['clock_control']:
   p['new']=re.sub(clock['pattern'],clock['replacement'],p['new'],flags=re.I)
   if p['old'] is not None:p['old']=re.sub(clock['pattern'],clock['replacement'],p['old'],flags=re.I)
  if p['old'] is not None:assert orig.count(p['old'])==1,(id,p['label'],p['old'])
 out={'object':id,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'basis':b,'source':o['source'],'original_databases_read_only':True,'private_database':':memory:','baseline_sql_path':record['runs'][0]['sql_path'],'baseline_sql_sha256':hashlib.sha256(orig.encode()).hexdigest(),'clock_control':o['clock_control'],'runs':[]}
 outpath=R/f'records/037_checks/rerun_{id}.json'
 if outpath.exists():out=json.loads(outpath.read_text())
 done={x['label'] for x in out['runs']}
 with duckdb.connect(':memory:') as c:
  c.execute("SET threads=2;SET memory_limit='2000MB'");tmp=R/'data/037_temp'/id;tmp.mkdir(parents=True,exist_ok=True);c.execute(f"SET temp_directory='{tmp}'")
  c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  c.execute(f"ATTACH '{o['source']}' AS src (READ_ONLY)")
  if o['source']==b['gold_database']:gold='src'
  else:c.execute(f"ATTACH '{b['gold_database']}' AS gold (READ_ONLY)");gold='gold'
  refs=set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate|marts|mart)\.\w+)',orig+' '+ ' '.join(p['new'] for p in PLAN[id]),re.I))
  for ref in sorted(refs):c.execute(f'CREATE SCHEMA IF NOT EXISTS {ref.split(".")[0]}');c.execute(f'CREATE TABLE {ref} AS SELECT * FROM src.{ref}')
  out['private_copy_tables']=sorted(refs)
  for p in [dict(label='baseline',old=None,new=orig,kind='基线')]+PLAN[id]:
   if p['label']!='baseline' and p['label'] in done:continue
   sql=p['new'] if p['kind'] in ['基线','呈现诊断'] else orig.replace(p['old'],p['new'],1)
   c.execute('SELECT setseed(0.019)');c.execute('CREATE OR REPLACE TABLE result_current AS '+sql)
   if p['label']=='baseline':c.execute('CREATE TABLE result_baseline AS SELECT * FROM result_current')
   r={'label':p['label'],'kind':p['kind'],'edits':[] if p['old'] is None else [{'old':p['old'],'new':p['new'],'offset':orig.index(p['old'])}],'sql':sql if p['kind']=='呈现诊断' else None,'comparison':compare_sql(c,'result_current',gold+'.'+b['actual_schema']+'.'+b['table'],b)}
   if p['label'] not in done:out['runs'].append(r)
   outpath.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');z=r['comparison']['levels'][0];print(id,p['label'],z['row_scale'],z['cell_scale'],flush=True)
if __name__=='__main__':
 for id in sys.argv[1:]:run(id)
