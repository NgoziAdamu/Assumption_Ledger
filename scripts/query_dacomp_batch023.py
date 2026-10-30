"""Explicit verification and diagnostic queries, originals READ_ONLY."""
from annotate_dacomp_batch023 import *
inv=json.loads((REC/'023_package_inventory.json').read_text());out=[]
def q(t,label,sql,diagnostic=False,side=None):
 r=next(r for r in inv if r['table']==t);p=json.loads((ROOT/r['full_json']).read_text());case=json.loads((REC/'013_cases.json').read_text())[int(r['task'][-3:])-1];db=side or (p['differences']['gold_database'] if diagnostic else case['agent_database'])
 row=dict(task=r['task'],table=t,label=label,kind='诊断' if diagnostic else '核实',database=db,sql=sql)
 try:
  with duckdb.connect(db,read_only=True) as c:
   result=c.execute(sql);row.update(columns=[x[0] for x in result.description],rows=result.fetchall())
 except Exception as e:row['error']=str(e)
 out.append(row);save(REC/'023_queries.json',out)
q('stg_quickbooks__invoice_line','选列有效性',"SELECT count(*) n,count(item_id) item_id_nonnull,count(sales_item_item_id) sales_item_nonnull,count(*) FILTER(WHERE sales_item_item_id IN(SELECT id FROM raw.item_data)) sales_item_matches FROM raw.invoice_line_data")
q('stg_quickbooks__payment_line','候选 linked ID',"SELECT count(*) n,count(invoice_id) invoice_id_nonnull,count(distinct invoice_id) invoice_ids FROM raw.payment_line_data")
q('stg_quickbooks__vendor','候选名称',"SELECT count(*) n,count(display_name) display_name_nonnull,count(company_name) company_name_nonnull FROM raw.vendor_data")
q('int_workday__organization_metrics','当前与历史',"SELECT count(*) n,count(*) FILTER(WHERE effective_end IS NULL) current_rows FROM staging.stg_workday__worker_position_organization")
q('stg_workday__position','校验次序',"SELECT count(*) FILTER(WHERE employee_type NOT IN ('Regular','Contingent','Intern','Contractor') AND trim(employee_type) IN ('Regular','Contingent','Intern','Contractor')) trim_rescues FROM raw.position")
q('workday__employee_overview','grade regexp',r"SELECT count(*) n,count(*) FILTER(WHERE regexp_extract(compensation_grade_id,'([0-9]+)',1)<>'') agent_matches,count(*) FILTER(WHERE regexp_extract(compensation_grade_id,'\\d+',0)<>'') gold_matches FROM staging.stg_workday__job_profile",True)
q('workday__position_overview','组织和 NULL 连接',"SELECT (SELECT count(*) FROM staging.stg_workday__organization WHERE is_inactive) inactive_orgs,(SELECT count(*) FROM staging.stg_workday__position_organization po WHERE NOT EXISTS(SELECT 1 FROM staging.stg_workday__organization o WHERE po.organization_id=o.organization_id)) orphan_relations",True)
for r in inv:
 if r['task']=='impl-017' and r['layer']=='staging':
  p=json.loads((ROOT/r['full_json']).read_text());s=p['agent_final_SQL'][0]['text'];raw=re.search(r'FROM (raw.\w+)',s).group(1);key=re.search(r'PARTITION BY (.*?) ORDER BY',s).group(1).replace('"phone_index"','"index"')
  q(r['table'],'契约主键重复',f'SELECT count(*) raw_rows,count(*)-count(DISTINCT row({key})) duplicate_excess FROM {raw}')
q('greenhouse__application_history','时间边界',"SELECT min(valid_until),max(valid_until) FROM mart.greenhouse__application_history",True)
q('greenhouse__job_enhanced','prospect 类型比较',"SELECT typeof(prospect),count(*),count(*) FILTER(WHERE prospect='True'),count(*) FILTER(WHERE prospect::VARCHAR='True') FROM intermediate.int_greenhouse__application_info GROUP BY 1")
q('salesforce__daily_activity','Won 全 NULL 分组',"SELECT count(*) FROM (SELECT close_date::DATE d FROM staging.stg_salesforce__opportunity GROUP BY 1 HAVING count(*) FILTER(WHERE is_won)=count(*) AND count(amount)=0)",True)
q('salesforce__team_performance','增长率 NULL',"SELECT count(*) n,count(*) FILTER(WHERE revenue_growth_qoq_percentage IS NULL) null_growth FROM marts.salesforce__team_performance",True)
q('stg_salesforce__contact','非必填字段 NULL',"SELECT count(*) n,count(*) FILTER(WHERE master_record_id IS NULL) missing_master FROM raw.contact")
q('stg_salesforce__contact_history','gold 时间型键',"SELECT min(created_date),max(created_date),min(history_unique_key),max(history_unique_key) FROM staging.stg_salesforce__contact_history",True)
q('stg_salesforce__lead','status 与缺失字段',"SELECT count(*) n,count(*) FILTER(WHERE status IS NULL OR trim(status) NOT IN ('Open - Not Contacted','Working - Contacted','Closed - Converted','Closed - Not Converted')) invalid_status,count(*) FILTER(WHERE master_record_id IS NULL) missing_master FROM raw.lead")
q('stg_salesforce__opportunity','缺失可选字段',"SELECT count(*) FILTER(WHERE lead_source IS NULL) null_lead_source,count(*) FILTER(WHERE type IS NULL) null_type FROM raw.opportunity")
q('stg_salesforce__order','ID 对应 account',"SELECT count(*) n,count(*) FILTER(WHERE id IN(SELECT id FROM raw.account)) order_matches_account,count(*) FILTER(WHERE account_id IN(SELECT id FROM raw.account)) fk_matches_account FROM raw.order_data")
q('stg_salesforce__task','status 删除条件',"SELECT count(*) FILTER(WHERE status IS NULL OR trim(status) NOT IN ('Not Started','In Progress','Completed','Waiting on someone else','Deferred')) invalid_status FROM raw.task")
q('stg_salesforce__user','各过滤条件',r"SELECT count(*) FILTER(WHERE email IS NULL) null_email,count(*) FILTER(WHERE NOT regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')) invalid_email,count(*) FILTER(WHERE length(email)>255) long_email,count(*) FILTER(WHERE is_active IS NULL) null_active,count(*) FILTER(WHERE last_name IS NULL) null_last_name,count(*) FILTER(WHERE name IS NULL) null_name,count(*) FILTER(WHERE username IS NULL) null_username FROM raw.user")
q('apple_store__app_version_report','NULL 连接键',"SELECT count(*) n,count(*) FILTER(WHERE source_relation IS NULL OR date_day IS NULL OR app_id IS NULL OR source_type IS NULL OR app_version IS NULL) null_keys FROM intermediate.int_apple_store__app_version_sessions_activity")
q('apple_store__territory_report','NULL 连接键',"SELECT count(*) n,count(*) FILTER(WHERE source_relation IS NULL OR date_day IS NULL OR app_id IS NULL OR source_type IS NULL OR territory IS NULL) null_keys FROM intermediate.int_apple_store__territory_sessions_activity")
q('stg_apple_store__app_session_daily','NULL 版本与字母',"SELECT count(*) n,count(*) FILTER(WHERE app_version IS NULL) null_versions FROM raw.app_session_standard_daily")
q('int_intercom__conversation_part_aggregates','agent 可见连接覆盖',"SELECT (SELECT count(*) FROM staging.stg_intercom__conversation_history) conversations,(SELECT count(*) FROM staging.stg_intercom__conversation_history c WHERE NOT EXISTS(SELECT 1 FROM staging.stg_intercom__conversation_part_history p WHERE p.conversation_id=c.conversation_id)) conversations_without_parts,(SELECT count(*) FROM staging.stg_intercom__conversation_part_history p WHERE NOT EXISTS(SELECT 1 FROM staging.stg_intercom__conversation_history c WHERE p.conversation_id=c.conversation_id)) orphan_parts")
q('int_intercom__conversation_part_aggregates','CS 连接覆盖',"SELECT (SELECT count(*) FROM staging.stg_intercom__conversation_history) conversations,(SELECT count(*) FROM staging.stg_intercom__conversation_part_history p JOIN staging.stg_intercom__conversation_history c USING(conversation_id)) joined_parts",True)
q('intercom__company_metrics','contact 映射覆盖',"SELECT count(*) joined_contacts FROM intermediate.int_intercom__contact_company_history r JOIN intermediate.int_intercom__contact_latest c USING(contact_id)",True)
q('stg_intercom__contact_history','显式 phone 规则与 gold regexp',r"WITH x AS(SELECT regexp_replace(phone,'[^0-9+]','','g') p FROM raw.contact_history_data WHERE coalesce(try_cast(_fivetran_active AS BOOLEAN),true)) SELECT count(*) FILTER(WHERE regexp_full_match(p,'^[+][1-9][0-9]{1,14}$')) contract_valid,count(*) FILTER(WHERE regexp_full_match(p,'^\\+[1-9]\\d{1,14}$')) gold_valid FROM x",True)
q('stg_intercom__conversation_contact_history','列值域与主表覆盖',"SELECT count(*) n,count(*) FILTER(WHERE try_cast(contact_id AS BIGINT) IS NOT NULL) contact_numeric,count(*) FILTER(WHERE try_cast(conversation_id AS BIGINT) IS NOT NULL) conversation_numeric,count(*) FILTER(WHERE conversation_id IN(SELECT id FROM raw.contact_history_data)) swapped_contact_matches,count(*) FILTER(WHERE contact_id IN(SELECT id FROM raw.contact_history_data)) named_contact_matches FROM raw.conversation_contact_history_data")
q('int_klaviyo__events','tied 窗口诊断',"SELECT person_id,occurred_at,count(*) n FROM staging.stg_klaviyo__event GROUP BY 1,2 ORDER BY 1,2",True)
q('int_klaviyo__events','gold session 起点',"SELECT event_id,person_id,occurred_at,prev_event_at,inter_event_minutes,session_seq FROM intermediate.int_klaviyo__events ORDER BY event_id",True)
for name in ['campaign','flow','metric','person']:
 q('stg_klaviyo__'+name,'ID 空值',f'SELECT count(*) n,count(*) FILTER(WHERE id IS NULL) null_id,count(*) FILTER(WHERE trim(id)=\'\') blank_id FROM raw.{name}')
q('stg_klaviyo__event','email 两种正则',r"SELECT count(*) n,count(*) FILTER(WHERE property_email IS NULL OR regexp_matches(property_email,'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')) ordinary_email,count(*) FILTER(WHERE property_email IS NULL OR regexp_matches(property_email,'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')) gold_email FROM raw.event",True)
print(len(out),[(x['table'],x['error']) for x in out if 'error' in x])
