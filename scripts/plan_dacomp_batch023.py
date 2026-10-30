"""Explicit one-code-location interventions; no automatic category inference."""
from annotate_dacomp_batch023 import *
inv=json.loads((REC/'023_package_inventory.json').read_text());plans=[]
def pkg(t): return json.loads((ROOT/next(r['full_json'] for r in inv if r['table']==t)).read_text())
def add(t,label,old,new,cat,why):
 d=pkg(t);s=d['agent_final_SQL'][0]['text'];assert s.count(old)==1,(t,label,old,s.count(old))
 p=next((p for p in plans if p['table']==t),None)
 if p is None:
  b=d['differences'];clock=(b.get('candidate_date') or '2025-10-24')+' 00:00:00+00'
  p=dict(task=d['basic_information']['task'],table=t,clock=clock if re.search(r'current_(date|timestamp)',s,re.I) else None,patches=[]);plans.append(p)
 p['patches'].append(dict(label=label,edits=[[old,new]],category=cat,reason=why))
add('stg_quickbooks__invoice_line','item_mapping','CAST(r.item_id AS VARCHAR)','CAST(r.sales_item_item_id AS VARCHAR)','U','item_id 全空，候选 sales_item_item_id 有值；核实其与商品主表关系后判定。')
add('stg_quickbooks__payment_line','linked_id','CAST(NULL AS VARCHAR) AS "linked_txn_payment_id"','CAST(r.invoice_id AS VARCHAR) AS "linked_txn_payment_id"','D','有 invoice_id 候选但直接整列占位。')
add('stg_quickbooks__vendor','vendor_name','CAST(NULL AS VARCHAR) AS "name"','CAST(r.display_name AS VARCHAR) AS "name"','D','存在 display_name 候选，name 整列占位。')
add('int_workday__organization_metrics','tenure_all_assignments','coalesce(c.avg_tenure_days,0)::DOUBLE avg_tenure_days',"coalesce((SELECT avg(date_diff('day',w.effective_start,coalesce(w.effective_end,current_date))) FROM staging.stg_workday__worker_position_organization w WHERE w.organization_id=o.organization_id AND w.source_relation=o.source_relation),0)::DOUBLE avg_tenure_days",'C','契约明确平均任期涵盖全部历史与当前 assignment，代码只取当前。')
add('stg_workday__position','validation_order',"TRIM(r.employee_type) NOT IN",'r.employee_type NOT IN','C','契约先对原始值执行枚举检查、再 trim；agent 用 trim 后值校验。')
for t in ['workday__employee_overview','workday__position_overview']:
 s=pkg(t)['agent_final_SQL'][0]['text'];old=next(x for x in s.splitlines() if 'CASE WHEN' in x and 'END compensation_tier' in x);a=old.index('CASE WHEN');end=old.index('END compensation_tier')+3
 add(t,'compensation_regex',old[a:end],"'Ungraded'",'O','契约要求提取首段数字，agent 符合；gold 双反斜杠正则对当前 grade 未提取数字。常量仅为定位 gold 差异的诊断。')
# Preserve compensation join multiplicity specified by employee_base join.
t='workday__employee_overview';s=pkg(t)['agent_final_SQL'][0]['text']
old='FROM staging.stg_workday__position_job_profile p\n LEFT JOIN staging.stg_workday__job_profile jp ON p.job_profile_id=jp.job_profile_id AND p.source_relation=jp.source_relation'
new=old+'\n JOIN intermediate.int_workday__worker_employee_enhanced eb ON eb.position_id=p.position_id AND eb.source_relation=p.source_relation'
add(t,'comp_base_multiplicity',old,new,'C','契约明确 compensation 从 ebe 出发并按 worker/source/position 回接；agent 直接按 position profile 连接省略 ebe 重复。')
# Further refine this intervention against original gold join keys before final decisions.
t='workday__position_overview';s=pkg(t)['agent_final_SQL'][0]['text']
old='SELECT organization_id,source_relation,organization_name,organization_type,organization_sub_type,staffing_model,current_employee_count,organization_health_score,annual_turnover_rate,performance_category,organization_size_category FROM intermediate.int_workday__organization_metrics'
new='SELECT o.organization_id,o.source_relation,o.organization_name,o.organization_type,o.organization_sub_type,o.staffing_model,m.current_employee_count,m.organization_health_score,m.annual_turnover_rate,m.performance_category,m.organization_size_category FROM staging.stg_workday__organization o LEFT JOIN intermediate.int_workday__organization_metrics m USING(organization_id,source_relation)'
add(t,'organization_dimension',old,new,'C','契约组织维度应来自 organization，agent 只读 active organization metrics，丢失非 active 组织属性。')
add(t,'organization_id',"coalesce(po.organization_id,'Unknown') organization_id","coalesce(o.organization_id,'Unknown') organization_id",'A','组织关联不存在时保留关系 ID 还是输出 Unknown。')
for t in [r['table'] for r in inv if r['task']=='impl-017' and r['layer']=='staging']:
 add(t,'uniqueness','WHERE _row_num = 1','WHERE TRUE','O','契约声明 primary_key/unique，agent 去重而 gold 保留重复。移除去重仅为定位诊断。')
t='greenhouse__job_enhanced'
add(t,'prospect_cast',"prospect::VARCHAR = 'True'","prospect = 'True'",'C','契约给出了可执行的 prospect = True 字符串比较，agent 预先转 VARCHAR 改变 BOOLEAN 比较。')
add(t,'days_clock',"DATE_DIFF('microsecond', created_at, CURRENT_TIMESTAMP)","DATE_DIFF('microsecond', created_at, CURRENT_DATE)",'C','契约要求 current date，agent 使用 current timestamp。')
t='salesforce__daily_activity'
add(t,'won_amount_null',"coalesce(round(sum(amount) filter(where deal_status='Won')),0)","round(sum(case when deal_status='Won' then amount else 0 end))",'C','只应在无 Won 记录时为零；有 Won 且 amount 全 NULL 时保留 NULL。')
t='salesforce__team_performance'
for label,old,new,cat,why in [
 ('health_growth_null',"case when coalesce(revenue_growth_qoq_percentage,0)>10 then 20 when coalesce(revenue_growth_qoq_percentage,0)>0 then 15 when coalesce(revenue_growth_qoq_percentage,0)>=-10 then 10 else 5 end","case when revenue_growth_qoq_percentage>10 then 20 when revenue_growth_qoq_percentage>0 then 15 when revenue_growth_qoq_percentage>=-10 then 10 else 5 end",'C','契约增长率 NULL 落 else=5，agent COALESCE 成0给10分。'),
 ('revenue_sum','sum(total_revenue_won) as team_total_revenue','sum(total_won_amount) as team_total_revenue','A','total revenue 的来源两种聚合未明确列映射。'),
 ('revenue_avg','round(avg(total_revenue_won)) as avg_revenue_per_member','round(avg(total_won_amount)) as avg_revenue_per_member','A','平均 revenue 来源不同。'),
 ('revenue_top','arg_max(full_name,total_revenue_won) filter(where total_revenue_won is not null)','arg_max(full_name,total_won_amount) filter(where total_won_amount is not null)','C','契约明确 highest total won amount。')]:add(t,label,old,new,cat,why)
for t in ['stg_salesforce__contact','stg_salesforce__lead','stg_salesforce__opportunity']:
 d=pkg(t);s=d['agent_final_SQL'][0]['text'];b=d['differences']
 for col in [c['column'] for c in b['column_details'] if c['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs']]:
  if col in ['annual_revenue','converted_date','status']:continue
  line=next(l for l in s.splitlines() if re.search(r'\bas '+col+r'[,]?$',l));old=line.strip().rstrip(',');expr=old.rsplit(' as ',1)[0]
  add(t,'null_empty_'+col,old,f"coalesce({expr}, '') as {col}",'A','契约没有规定该列 NULL 与空串默认；两侧选择不同。')
t='stg_salesforce__contact_history'
add(t,'history_key',"md5(concat_ws('|', coalesce(cast(contact_id as varchar), ''), coalesce(cast(_fivetran_start as varchar), ''), coalesce(cast(_fivetran_end as varchar), '')))","concat(id, '_', created_date::varchar)",'A','契约没有规定 history_unique_key 的构造算法。')
add(t,'unique_contact','qualify row_number() over (partition by id order by id) = 1','','O','契约 contact_id unique 而 gold 保留重复。')
t='stg_salesforce__lead'
add(t,'status_filter',"and trim(status) in ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')",'and TRUE','O','契约要求枚举并删除无效值，gold 留存。')
add(t,'status_value','trim(status) as status',"case when trim(status) in ('Open', 'Closed - Converted', 'Closed - Not Converted') then trim(status) else null end as status",'O','gold 对契约允许的两种 status 置空。')
add(t,'revenue_range','try_cast(annual_revenue as DECIMAL(18,3))',"case when annual_revenue<0 or annual_revenue>999999999999.99 then null else try_cast(annual_revenue as DECIMAL(18,2)) end",'A','契约未规定 annual revenue 边界，gold 额外范围清洗；负收入不一概视为硬约束。')
add(t,'converted_date','try_cast(converted_date as TIMESTAMP)',"case when converted_date < DATE '1900-01-01' or converted_date > current_date + interval '1 year' or converted_date < created_date::DATE then null else try_cast(converted_date as TIMESTAMP) end",'A','契约未规定 converted_date 清洗范围，gold 额外清洗。')
add('stg_salesforce__order','account_mapping','id as account_id','account_id as account_id','U','ID 指订单，不对应 raw.account；需查询证实可见数据唯一指向 account_id。')
t='stg_salesforce__task';add(t,'status_filter',"and trim(status) in ('Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred')",'and TRUE','O','agent 按契约删除无效状态，gold 留存。')
t='stg_salesforce__user';add(t,'email_filter',"and regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')",'and TRUE','O','契约 email 正则校验删除，gold 未执行。')
for t in ['apple_store__app_version_report','apple_store__territory_report']:
 s=pkg(t)['agent_final_SQL'][0]['text']
 for alias in ['cr','inst','ses','ip','dl','ins','app']:
  line=next((l for l in s.splitlines() if l.startswith('LEFT JOIN '+alias+' ON ')),None)
  if line:add(t,'join_'+alias,line,line.replace(' IS NOT DISTINCT FROM ',' = '),'A','契约未明确 NULL 键是否相等连接；agent null-safe，gold 普通等号。')
 if t.endswith('territory_report'):
  for alias in ['ip','dl','ins','ses']:
   line=next(l for l in s.splitlines() if l.startswith(alias+' AS ('));new=re.sub(r'SUM\((\w+)\) AS \1',r'\1',line);new=re.sub(r' GROUP BY .*\),$', '),',new)
   add(t,'aggregate_'+alias,line,new,'C','契约明确不聚合，agent 额外 group by。')
t='stg_apple_store__app_session_daily'
add(t,'null_version_filter',"coalesce(cast(r.app_version AS VARCHAR), '')","cast(r.app_version AS VARCHAR)",'C','契约原式 NOT regexp(NULL) 为 UNKNOWN 而筛除；COALESCE 为空串额外保留。')
t='int_intercom__conversation_part_aggregates';add(t,'left_conversation','from rollup r join staging.stg_intercom__conversation_history c','from rollup r left join staging.stg_intercom__conversation_history c','U','假设每个 part conversation 均存在 history 主表；需可见数据核实。')
t='intercom__company_metrics'
for col in ['contacts_total','contacts_active_7d','contacts_active_30d']:add(t,col,f'coalesce(co.{col},0)',f'co.{col}','A','契约未指定无匹配 contact 聚合时补0还是 NULL。')
for t in ['stg_klaviyo__campaign','stg_klaviyo__flow','stg_klaviyo__metric','stg_klaviyo__person']:
 s=pkg(t)['agent_final_SQL'][0]['text'];old=next(re.finditer(r'nullif\(trim\(cast\("?id"? as varchar\)\), \'\'\) is not null',s,re.I)).group()
 add(t,'null_id_filter',old,'TRUE','O' if not t.endswith('person') else 'A','前三表契约明确 ID not_null，gold 保留 NULL；person 没有非空要求，额外删除为未规定取舍。')
t='stg_klaviyo__event';s=pkg(t)['agent_final_SQL'][0]['text'];old=next(l.strip()[4:] for l in s.splitlines() if l.strip().startswith('and '));new="(property_email is null or regexp_matches(property_email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$'))"
add(t,'email_regex',old,new,'O','gold 双反斜杠正则拒绝普通有效邮箱，而契约只要求删除 invalid property_email；需诊断确认。')
# Ensure every full-scope table has at least an unmodified baseline.
for r in inv:
 if r['purpose']=='校准':continue
 if not any(p['table']==r['table'] for p in plans):plans.append(dict(task=r['task'],table=r['table'],clock=None,patches=[]))
save(REC/'023_patch_plan.json',plans)
print(len(plans),sum(len(p['patches']) for p in plans))
