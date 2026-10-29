"""Explicit manual single-cause patch specifications; original bytes outside spans preserved."""
import json,re
from pathlib import Path
import sqlglot
from sqlglot import exp
ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records'
inv=json.loads((REC/'019_package_inventory.json').read_text());docs={r['table']:json.loads((ROOT/r['full_json']).read_text()) for r in inv};plan={}
def add(t,label,old,new,category,reason):
 s=docs[t]['agent_final_SQL'][0]['text'];assert s.count(old)==1,(t,label,old,s.count(old));plan.setdefault(t,[]).append(dict(label=label,edits=[[old,new]],category=category,reason=reason))
def gold(t,col):
 tree=sqlglot.parse_one(docs[t]['gold_SQL_仅供定位差异'][0]['text'],read='duckdb')
 return next(e.this.sql(dialect='duckdb',comments=False) for e in tree.find_all(exp.Alias) if e.alias==col)
def expr(t,col):
 s=docs[t]['agent_final_SQL'][0]['text'];tok=sqlglot.tokenize(s,read='duckdb');depth=0;depths=[]
 for x in tok:
  depths.append(depth)
  if x.text=='(':depth+=1
  if x.text==')':depth-=1
 for i,x in enumerate(tok):
  if x.text.upper()!='SELECT':continue
  dep=depths[i];start=i+1
  for j in range(start,len(tok)):
   if depths[j]<dep:break
   if depths[j]==dep and (tok[j].text==',' or tok[j].text.upper()=='FROM'):
    piece=s[tok[start].start:tok[j-1].end+1]
    try:
     e=sqlglot.parse_one('SELECT '+piece,read='duckdb').expressions[0]
     if isinstance(e,exp.Alias) and e.alias==col:return piece
    except Exception:pass
    start=j+1
    if tok[j].text.upper()=='FROM':break
 raise ValueError((t,col))
def alias(t,col,new,cat,reason):add(t,col,expr(t,col),new+' AS '+col,cat,reason)
def goldalias(t,col,cat,reason):alias(t,col,gold(t,col),cat,reason)
# Staging validation clauses.
t='stg_lever__offer';add(t,'status_filter',"status IN ('open','closed','cancelled','draft','pending') AND",'TRUE AND','C','契约对 offer.status 要求非法枚举置空，agent 使用 requisition 枚举删行。');alias(t,'status',"CASE WHEN r.status IN ('draft','pending','sent','accepted','declined','rescinded') THEN r.status END",'C','非法 status 应 nullify_field。')
for col,vals in [('categories_commitment',"'full-time','part-time','contract','internship'"),('categories_level',"'Entry','Mid','Senior','Lead','Principal','Executive'")]:alias('stg_lever__posting',col,f'CASE WHEN r.{col} IN ({vals}) THEN r.{col} END','C','遗漏契约枚举 nullify_field。')
for col,vals in [('compensation_band_currency',"'USD','EUR','GBP','CNY','CAD','AUD'"),('compensation_band_interval',"'hourly','monthly','yearly'")]:alias('stg_lever__requisition',col,f'CASE WHEN r.{col} IN ({vals}) THEN r.{col} END','C','遗漏契约枚举 nullify_field。')
for t in ['stg_pendo__event','stg_pendo__page_event','stg_pendo__poll_event']:
 col={'stg_pendo__event':'event_key','stg_pendo__page_event':'page_event_key','stg_pendo__poll_event':'poll_event_key'}[t]
 reason='契约规定 MD5 的六个来源字段，但没有规定连接分隔符；agent 与 gold 分别使用带分隔符和直接连接。' if t=='stg_pendo__event' else '契约只声明代理键及类型，没有规定生成字段和拼接公式；差异取决于未规定的键生成选择。'
 goldalias(t,col,'A',reason)
goldalias('stg_pendo__poll_event','url','C','URL 校验没有执行契约正则字面规则。')
add('stg_pendo__user','deleted_at_parse',"TRY_CAST(NULLIF(deleted_at, '') AS TIMESTAMP)","TRY_CAST(SUBSTRING(NULLIF(deleted_at, ''),1,23) AS TIMESTAMP)",'U','P：日期文本可直接 TRY_CAST；实际含时区后缀而解析失败。')
add('stg_pendo__visitor_history','last_visit_parse','TRY_CAST(last_visit AS TIMESTAMP)','TRY_CAST(SUBSTRING(last_visit,1,23) AS TIMESTAMP)','I','同一个 SQL 对 first_visit/last_updated_at 正确截取，对 last_visit 遗漏。')
for t in ['stg_google_ads__account_history','stg_google_ads__ad_history','stg_google_ads__campaign_history']:
 add(t,'timestamp_cast',"try_strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP",'try_cast(updated_at AS TIMESTAMP)','C','契约含可直接执行 try_cast 校验；agent 采用另一种解析。')
add('stg_google_ads__ad_group_history','timestamp_type',"try_strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP",'try_cast(updated_at AS TIMESTAMPTZ)','O','契约 TIMESTAMP 与 gold TIMESTAMPTZ 类型不一致，修改用于诊断。')
# Explicit missing modules: one local calculation replaces a placeholder per trial.
for t,col,old,new in [
 ('int_lever__posting_analytics','referral_rate_pct','0.0 referral_rate_pct',"count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL)*100.0/nullif(count(DISTINCT a.application_id),0) referral_rate_pct"),
 ('int_lever__posting_performance','referral_rate','0.0 referral_rate',"count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL)*100.0/nullif(count(DISTINCT a.application_id),0) referral_rate")]:add(t,col,old,new,'D','指标直接用 0 占位，缺少所需聚合。')
# Explicit partition requirement.
add('lever__opportunity_enhanced','candidate_partition','PARTITION BY opportunity_id ORDER BY created_at DESC','PARTITION BY candidate_id ORDER BY created_at DESC','C','契约规定每 candidate 的最新 offer，代码按 opportunity 分区。')
# Correct numeric computation on existing inputs.
t='int_google_ads__account_performance_metrics';add(t,'ctr_precision','clicks::DOUBLE / impressions','clicks::FLOAT / impressions','A','浮点计算精度顺序不同，需契约精度核对。');add(t,'cost_round','round(CASE WHEN conversions > 0 THEN spend / conversions END, 4)','CASE WHEN conversions > 0 THEN round(spend / conversions,4) END','I','ROUND(CASE...) 与 CASE(ROUND...) 引擎类型行为诊断。')
t='google_ads__executive_dashboard';add(t,'rounded_alias','SELECT *,round(spend_30d_avg,2)','SELECT * EXCLUDE(spend_30d_avg,roas_30d_avg,performance_score_30d_avg),round(spend_30d_avg,2)','I','SELECT * 已含同名列，新增舍入列自动改名，最终仍选旧列。');add(t,'scale_null','(star_pct>15) scale_opportunity','coalesce(star_pct>15,false) scale_opportunity','C','契约规定布尔 false 默认，agent 保留 NULL。')
t='google_ads__customer_acquisition_analysis'
for col in ['cohort_avg_cac','cohort_avg_ltv','cac_efficiency_percentile','ltv_cac_performance_percentile','acquisition_sophistication_score','strategic_customer_segment','acquisition_recommendation']:goldalias(t,col,'C','输出表达式/排序与契约规定不一致。')
# Non-deterministic choices: deterministic tie order as diagnostic only.
for t,key in [('salesforce__account_daily_history','annual_revenue'),('salesforce__contact_daily_history','title')]:add(t,'tie_order','ORDER BY created_date DESC',f'ORDER BY created_date DESC, {key} ASC','O','契约明确同时间记录任取；改变并列次序诊断。')
add('int_lever__posting_applications','tie_order','ORDER BY created_at DESC','ORDER BY created_at DESC, posting_hiring_manager_user_id','O','契约允许引擎默认并列次序。')
for t,col in [('customer360__status','source_systems'),('customer360__updates','updated_by_systems')]:
 add(t,'string_order',"string_agg(distinct source_system,', ')","string_agg(distinct source_system,', ' ORDER BY source_system)",'O','STRING_AGG 的无序元素顺序诊断。')
add('customer360__phone','phone_tie','order by phone','order by phone,extension','O','相同 phone 不同 extension 的 row_number 并列顺序。')

t='lever__candidate_experience_insights'
add(t,'contact_join','LEFT JOIN staging.stg_lever__stage s', 'LEFT JOIN intermediate.int_lever__contact_info c ON cl.contact_id=c.contact_id LEFT JOIN staging.stg_lever__stage s','C','遗漏契约明确指定 contact_info 左连接；其重复键会放大输出。')
add(t,'stage_inner','LEFT JOIN staging.stg_lever__stage s','JOIN staging.stg_lever__stage s','C','stage 要求 inner join。')
add(t,'completion_zero',"round(cl.completed_interviews*100.0/nullif(cl.total_interviews,0),1) completion_rate","round(cl.completed_interviews*100.0/cl.total_interviews,1) completion_rate",'C','契约明确 no explicit zero-division guard。')
old=expr(t,'overall_candidate_experience_score');add(t,'timeline_score',old,old.replace('+3*.2','+1*.2'),'I','代码已输出 timeline=1，却在 overall 中写常数3。')
add(t,'recommendations',"'' improvement_recommendations", "concat(CASE WHEN transparency_score<=2 THEN 'Improve feedback transparency; ' ELSE '' END,CASE WHEN interview_experience_score<=2 THEN 'Optimize interview process; ' ELSE '' END,'Accelerate decision timeline; ',CASE WHEN days_since_last_advancement>=14 THEN 'Increase communication frequency; ' ELSE '' END) improvement_recommendations",'D','建议整列空字符串占位。')
t='lever__candidate_quality_insights'
for col in ['key_finding_source','key_finding_overall','primary_recommendation','process_recommendation']:
 # Contract specifies semantic messages but not exact complete literals: isolate each text encoding choice.
 old=expr(t,col);g=gold(t,col)
 # Keep agent conditions, replace only branch string literals in order.
 a=re.findall("'([^']*)'",old);b=re.findall("'([^']*)'",g)
 # Extract THEN/ELSE literals only, excluding condition literals.
 av=re.findall(r"(?:THEN|ELSE)\s+'([^']*)'",old,re.I);bv=re.findall(r"(?:THEN|ELSE)\s+'([^']*)'",g,re.I)
 if len(av)==len(bv):
  new=old
  for v,w in zip(av,bv):new=new.replace("'"+v+"'","'"+w+"'")
  if new!=old:add(t,col,old,new,'A','契约只给出消息含义，未规定完全相同英文字符串。')
t='customer360__mapping'
# Replace first source assembly only, keeping ID hashes and headers unchanged.
gtree=sqlglot.parse_one(docs[t]['gold_SQL_仅供定位差异'][0]['text'],read='duckdb')
# Other concrete fixes added separately after inspecting source assembly.
add('stg_customer360__country_codes','dedup','where _row_num = 1','where TRUE','O','契约 country_code_alpha_2 unique；gold 未去重，移除去重作诊断。')
add('stg_customer360__state_territory_codes','membership','inner join staging.stg_customer360__country_codes cc\n    on c.alpha2_country_code = cc.country_code_alpha_2','where c.alpha2_country_code IN (SELECT country_code_alpha_2 FROM staging.stg_customer360__country_codes)','I','契约要求集合成员检查，inner join 在 reference 重复时扩行。')
t='int_customer360__customer_behavior_analysis'
add(t,'first_touch',"case when m_created is null or s_created is null or z_created is null then null else least(m_created,s_created,z_created) end",'least(m_created,s_created,z_created)','C','契约忽略缺失平台时间取最早非空，agent 任一空即全空。')
add(t,'last_activity',"case when m_updated is null or s_updated is null or z_updated is null then null else greatest(m_updated,s_updated,z_updated) end",'greatest(m_updated,s_updated,z_updated)','C','契约忽略缺失平台时间取最晚非空，agent 任一空即全空。')
t='customer360__conversion_funnel_analysis'
old=expr(t,'revenue_velocity_monthly');new=gold(t,'revenue_velocity_monthly');new=re.sub(r'\b[a-z]+\.', '', new);add(t,'revenue_velocity_monthly',old,new+' AS revenue_velocity_monthly','C','收入速度分母/单位与契约公式不同。')
t='int_customer360__risk_assessment'
for col in ['primary_risk_factor','recommended_intervention','intervention_success_probability']:
 new=gold(t,col);new=re.sub(r'\b[a-z]+\.', '', new);alias(t,col,new,'C','阈值、条件或概率值与契约规定不同。')

t='lever__departmental_hiring_trends'
add(t,'referral_count','count(DISTINCT referrer_user_id) AS referred',"count(DISTINCT application_id) FILTER(WHERE referrer_user_id IS NOT NULL) AS referred",'C','referral 应数申请而非去重 referrer。')
add(t,'cost_tier',"'No Data' AS cost_efficiency_tier","'No Hires' AS cost_efficiency_tier",'D','成本分类常数占位；仅恢复无 hire 时分支。')
t='lever__hiring_manager_scorecard';add(t,'decision_speed',"'Unknown' decision_speed_category","'Slow Decision Maker' decision_speed_category",'D','速度分类使用 Unknown 占位；恢复无 hire 分支。')
t='int_pendo__customer_rfm_analysis'
for col in ['recommended_strategy','predicted_clv_tier','action_priority']:goldalias(t,col,'C','契约对应 segment 分类/建议映射遗漏或合并。')
for col,formula in [('account_total_visitors','count(*)'),('account_high_value_ratio',"count(*) FILTER(WHERE az.customer_value_tier='High Value')::FLOAT/count(*)"),('account_top_segment_ratio',"count(*) FILTER(WHERE az.rfm_segment IN ('Champions','Loyal Customers'))::FLOAT/count(*)"),('account_at_risk_ratio',"count(*) FILTER(WHERE az.rfm_segment IN ('At Risk','Cannot Be Retrieved'))::FLOAT/count(*)"),('account_avg_rfm_score','avg(az.rfm_composite_score)')]:alias(t,col,'(SELECT '+formula+' FROM z az WHERE az.account_id=z.account_id)','D','account 聚合列 NULL 占位。')
t='int_pendo__product_health_metrics';add(t,'health_score','0::FLOAT overall_health_score',"least(100,coalesce(f.features_used::FLOAT/nullif(f.total_features_available,0),0)*25) overall_health_score",'D','健康总分常数占位；只恢复 feature adoption 项，用于局部贡献诊断。')
t='pendo__customer_lifecycle_insights'
for col in ['customer_journey_stage','predicted_ltv_tier','engagement_velocity','usage_trend','customer_importance_level','investment_expectation']:
 new=gold(t,col)
 # Gold uses visitor/lifecycle/rfm/product aliases; inspect replacements below before execution.
 for a,b in [('vb.','v.'),('lc.','l.'),('ph.','h.'),('vls.','l.'),('rfm.','r.'),('phm.','h.'),('vl.','v.')]:new=new.replace(a,b)
 alias(t,col,new,'D','高级派生字段用固定值代替规则。')
t='pendo__executive_dashboard_metrics';alias(t,'avg_platform_health_score','(SELECT avg(overall_health_score) FROM intermediate.int_pendo__product_health_metrics)','D','平台健康分直接 NULL 占位。')
t='int_customer360__customer_lifecycle_metrics';new=gold(t,'frequency_score').replace('caw.','').replace('platform_consistency_score','platform_sum');alias(t,'frequency_score',new,'C','频率评分缺失 active30/60 的高分分支。')
t='customer360__customer_activity_metrics'
new=gold(t,'cross_platform_consistency').replace('ba.','');alias(t,'cross_platform_consistency',new,'C','一致性指标遗漏除以在场平台数。')
new=gold(t,'primary_engagement_channel').replace('ap.','');alias(t,'primary_engagement_channel',new,'C','主渠道要求比较原始 engagement；agent 比较衰减后 score。')

t='customer360__customer';add(t,'metrics_key_multiplicity','select * from non_headers union all select * from headers','select n.* from non_headers n JOIN dimensions d USING(customer360_id) union all select * from headers','U','P：dimensions 的 customer360_id 唯一，直接内联 metrics 与按键结合等价；私有上游可核实重复。')
t='customer360__mapping'
old=docs[t]['agent_final_SQL'][0]['text'].split(' union all')[0].split('with source_rows as (')[1]
new=old.replace('left join intermediate.', 'full outer join intermediate.')
new=new.replace('select sm.marketo_lead_id, sm.stripe_customer_id, sm.zendesk_user_id,','select coalesce(sm.marketo_lead_id,m.lead_id) marketo_lead_id, coalesce(sm.stripe_customer_id,s.customer_id) stripe_customer_id, coalesce(sm.zendesk_user_id,z.user_id) zendesk_user_id,')
for col,prefix in [('marketo','m'),('stripe','s'),('zendesk','z')]:
 for suffix in ['updated_at','created_at']:
  new=new.replace('sm.'+col+'_'+suffix, 'coalesce(sm.'+col+'_'+suffix+','+prefix+'.'+suffix+') '+col+'_'+suffix)
for suffix in ['updated_at','created_at']:new=new.replace('sm.zendesk_organization_'+suffix,'coalesce(sm.zendesk_organization_'+suffix+',z.organization_'+suffix+') zendesk_organization_'+suffix)
add(t,'outer_source',old,new,'C','契约明确 full outer join 后还 union unmatched；agent left join 少了第一批 unmatched。')
t='int_pendo__conversion_funnel_analysis'
# Restore just the missing feature-source membership used by the feature-user count.
add(t,'feature_source',"count(DISTINCT CASE WHEN num_events>0 THEN visitor_id END) visitors_with_feature_use", "(SELECT count(DISTINCT f.visitor_id) FROM staging.stg_pendo__feature_event f WHERE f.account_id=staging.stg_pendo__event.account_id AND f.app_id=staging.stg_pendo__event.app_id AND cast(f.occurred_at AS DATE)=cast(staging.stg_pendo__event.occurred_at AS DATE)) visitors_with_feature_use",'D','feature use 被换成 event.num_events>0；恢复规定 feature_event 来源。')
t='int_pendo__data_quality_checks';old=docs[t]['agent_final_SQL'][0]['text'];add(t,'completeness_rows',old,old+" UNION ALL SELECT 'Data Completeness Details', 'event', count(*)::FLOAT, count(*) FILTER(WHERE visitor_id IS NULL)::FLOAT, count(*) FILTER(WHERE account_id IS NULL)::FLOAT, count(*) FILTER(WHERE occurred_at IS NULL)::VARCHAR, current_timestamp FROM staging.stg_pendo__event",'D','summary-only 降级遗漏所有详情；单独恢复 event completeness 行。')

# Final category corrections after checking the complete frozen contract (gold is not normative).
for x in plan['int_customer360__customer_behavior_analysis']:
 x['category']='O';x['reason']='契约明确任一输入 NULL 则输出 NULL，agent 照做；gold least/greatest 忽略 NULL。'
for x in plan['int_customer360__risk_assessment']:
 x['category']='C' if x['label']=='intervention_success_probability' else 'A'
 x['reason']='契约要求 DECIMAL(3,2)，agent .30 等字面量推断为 DECIMAL(2,2)，VARCHAR 表示少前导0。' if x['category']=='C' else '契约给出类别优先级，但未完整规定触发阈值；agent 与 gold 采用不同阈值。'
for x in plan['int_pendo__customer_rfm_analysis']:
 if x['category']=='C':x['category']='A';x['reason']='契约未给出完整 segment→文本/CLV 档位映射；不把 gold 的具体文本当要求。'
for x in plan['google_ads__customer_acquisition_analysis']:
 if x['label'] in ['cac_efficiency_percentile','ltv_cac_performance_percentile','acquisition_sophistication_score','strategic_customer_segment','acquisition_recommendation']:
  x['category']='A';x['reason']='契约没有可直接执行排序表达式/完整公式阈值表；higher rank 的名次与数值读法，以及细分规则存在歧义。'
for x in plan['pendo__customer_lifecycle_insights']:
 old,new=x['edits'][0]
 for col in ['count_active_days','first_event_on','average_daily_events','sum_events']:
  new=re.sub(r'(?<![\w.])'+col+r'\b','v.'+col,new)
 new=re.sub(r'(?<![\w.])needs_attention\b','l.needs_attention',new)
 x['edits']=[[old,new]]
t='int_google_ads__account_performance_metrics'
add(t,'cs_column_collision','SELECT * FROM staging.stg_google_ads__account_stats','SELECT * EXCLUDE(cost_per_conversion) FROM staging.stg_google_ads__account_stats','O','gold CS 上游额外 cost_per_conversion 被 SELECT * 带入，遮蔽后来正确舍入列；agent 当时上游没有此列。')
t='customer360__conversion_funnel_analysis';add(t,'rounded_consistency','.4*cross_stage_engagement_consistency,2) as journey_efficiency_index','.4*round(cross_stage_engagement_consistency,2),2) as journey_efficiency_index','C','契约要求先将 consistency 四舍五入到2位；agent 在依赖键公式中使用未舍入值。')
t='int_customer360__risk_assessment';old=expr(t,'intervention_success_probability');add(t,'probability_type',old,old.split(' as intervention_success_probability')[0]+'::DECIMAL(3,2) AS intervention_success_probability','C','只显式转换类型，验证前导0表示差异；与展开S修法为同一错误点。')
t='lever__candidate_experience_insights';add(t,'gold_join_multiplicity','FROM calc',"FROM calc, LATERAL (SELECT count(*) n FROM base b WHERE b.opportunity_id=calc.opportunity_id) rep, UNNEST(range(cast(pow(rep.n,4) AS BIGINT))) mult(j)",'O','诊断复现 gold 四个同键子结果再连接的 n^5 重数；契约声明每 opportunity 一行且没要求最终四次自连接。')
for t,digits,col in [('int_lever__posting_analytics',1,'referral_rate_pct'),('int_lever__posting_performance',2,'referral_rate')]:
 x=plan[t][0];x['edits'][0][1]=f"CASE WHEN count(DISTINCT a.application_id)>0 THEN round(count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL)::DECIMAL(18,3)/count(DISTINCT a.application_id)*100,{digits}) ELSE 0 END {col}"

add('stg_customer360__state_territory_codes','distinct_rows','select c.state_territory, c.state_code, c.alpha2_country_code','select distinct c.state_territory, c.state_code, c.alpha2_country_code','A','契约未规定整行去重；gold DISTINCT 删除完全重复行，agent 保留。')
add('stg_pendo__user','required_user_id',"WHERE user_type IN", "WHERE id IS NOT NULL AND id<>'' AND user_type IN",'C','契约必需 user_id 过滤遗漏。')

add('stg_pendo__event','account_id_validation','CAST(account_id AS VARCHAR) AS account_id',"CASE WHEN account_id ~ '^(ACC[0-9]+|[0-9]+)$' THEN CAST(account_id AS VARCHAR) END AS account_id",'C','契约指定 account_id 正则，不合法应 nullify_field。')
add('stg_pendo__user','normalized_user_type',"WHERE user_type IN", "WHERE lower(trim(user_type)) IN",'C','契约要求规范化后枚举判断；agent 在原始值上筛选。')
t='pendo__executive_dashboard_metrics';alias(t,'avg_feature_adoption','(SELECT avg(v) FROM (SELECT ah.account_id,ah.first_visit_at,ah.last_visit_at,max(ph.feature_adoption_rate) v FROM staging.stg_pendo__account_history ah LEFT JOIN intermediate.int_pendo__product_health_metrics ph ON ah.account_id=ph.account_id GROUP BY 1,2,3))','D','dashboard 账户汇总列 NULL 占位；恢复 account 上游的 feature adoption 平均。')

for t in ['stg_google_ads__account_history','stg_google_ads__ad_history','stg_google_ads__campaign_history']:
 for x in plan[t]:x['category']='A';x['reason']='契约只指定 TIMESTAMP 及校验，没有规定源时区文本解析器与失败策略；agent STRPTIME 与 gold TRY_CAST 产生有效时间/NULL 两种结果。'

t='customer360__conversion_funnel_analysis';alias(t,'journey_completeness_score',gold(t,'journey_completeness_score').replace('ba.',''),'O','契约规定任意两个平台为2；gold 两平台分支遗漏 Marketo+Zendesk，agent 按契约使用总数。')
for x in plan['int_google_ads__account_performance_metrics']:
 if x['label']=='ctr_precision':x['reason']='契约未指定中间运算用 FLOAT 还是 DOUBLE；两种浮点精度在最终舍入边界产生差异。'
(REC/'019_patch_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n');print('plans',len(plan),sum(map(len,plan.values())))
