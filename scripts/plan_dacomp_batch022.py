from review_dacomp_batch022 import *
import re
plans={i:[] for i in range(38)}
def add(i,label,old,new,cat,reason):
 s=pkg(i)['agent_final_SQL'][0]['text'];assert s.count(old)==1,(i,label,s.count(old),old)
 plans[i].append(dict(label=label,edits=[[old,new]],category=cat,reason=reason))
def multi(i,label,edits,cat,reason):
 for old,new in edits:assert pkg(i)['agent_final_SQL'][0]['text'].count(old)==1,(i,label,old)
 plans[i].append(dict(label=label,edits=edits,category=cat,reason=reason))
add(1,'missing_segment',"CASE WHEN total_lead_score>=100", "CASE WHEN total_emails_sent=0 THEN 'Unknown' WHEN total_lead_score>=100",'C','契约无engagement时rfm_segment为Unknown；agent在补零后分段为Inactive。')
add(1,'missing_action',"WHEN total_emails_opened=0 THEN 'Welcome Series'", "WHEN total_emails_sent>0 AND total_emails_opened=0 THEN 'Welcome Series'",'O','契约无打开时Welcome Series；gold缺失engagement的NULL未命中0而给Standard Campaign Flow。')
add(4,'send_id',"CAST(id AS VARCHAR) AS email_send_id", "MD5(CONCAT(COALESCE(CAST(primary_attribute_value_id AS VARCHAR), ''),COALESCE(CAST(campaign_id AS VARCHAR), ''),COALESCE(CAST(campaign_run_id AS VARCHAR), ''),COALESCE(CAST(lead_id AS VARCHAR), ''))) AS email_send_id",'A','email_send_id派生方式契约未规定；agent源id、gold组合MD5。')
add(5,'blank_names'," AND TRIM(name) <> ''",'', 'O','契约显式删除空白campaign_name；gold保留一行。')
add(6,'calendar_end','CURRENT_DATE AS max_date',"CURRENT_DATE + INTERVAL '1 week' AS max_date",'A','契约未检出该utils表定义；gold多未来7天。')
# A common missing-category aggregation error, each output separately.
for i in [8,10]:
 s=pkg(i)['agent_final_SQL'][0]['text']
 for m in re.finditer(r'sum\((abs\([^)]*\)|[\w.]+)\) FILTER\(WHERE ([^)]*(?:\)[^)]*)?)\) ([a-z_]+)',s,re.I):
  old=m.group(0)
  # robust extraction below replaces only complete SUM FILTER expressions using sqlglot elsewhere
import sqlglot
for i,cols in [(8,['total_receivables','total_collections','outstanding_receivables']),(10,['total_current_assets','total_current_liabilities','cash_and_equivalents','accounts_receivable','total_equity'])]:
 s=pkg(i)['agent_final_SQL'][0]['text']
 for col in cols:
  end=s.index(' '+col);start=s.rfind('sum(',0,end);old=s[start:end]
  add(i,'zero_'+col,old+' '+col,'coalesce('+old+',0) '+col,'C','契约按类别SUM CASE ELSE 0；FILTER无匹配得到NULL。')
add(11,'subsidiary_source','a.account_number, t.subsidiary_id,','a.account_number, s.subsidiary_id,','C','契约subsidiary_id列明确来自joined subsidiaries；agent保留驱动外键。')
add(13,'parse_period','try_cast(m.starting_at AS TIMESTAMP)',"strptime(substr(m.starting_at,1,19), '%Y-%m-%d %H:%M:%S')",'C','契约明确截到秒解析；直接TRY_CAST带偏移字符串失败。')
add(15,'volatility', 'stddev_samp(financial_health_score)', 'stddev_samp(financial_health_score)', 'C','placeholder') if False else None
add(17,'required_join','SELECT * FROM intermediate.int_netsuite2__transaction_details', 'SELECT d.* FROM intermediate.int_netsuite2__transaction_details d JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=d.subsidiary_id','D','整张替换成另一表并省掉契约inner subsidiaries连接。仅补该连接，非全表gold替换。')
add(19,'type_key','TRY_CAST(r."internalid" AS BIGINT)', 'row_number() OVER (ORDER BY r."longname")','A','契约未给account_type_id生成规则；internalid与按名称row_number两种标识。')
for i in [21,22,24]:
 d=pkg(i);s=d['agent_final_SQL'][0]['text'];gold=d['gold_SQL_仅供定位差异'][0]['text']
 maps={21:{'class_id':'id','class_external_id':'externalid','name':'name','full_name':'fullname','is_inactive':"isinactive = 'T'"},22:{'consolidated_exchange_rate_id':'id','accounting_period_id':'postingperiod','from_currency_id':'fromcurrency','from_subsidiary_id':'fromsubsidiary','to_currency_id':'tocurrency','to_subsidiary_id':'tosubsidiary','accounting_book_id':'accountingbook','current_rate':'coalesce(try_cast(currentrate as double),0) <> 0','average_rate':'coalesce(try_cast(averagerate as double),0) <> 0','historical_rate':'coalesce(try_cast(historicalrate as double),0) <> 0'},24:{'entity_id':'id','parent_id':'parent','entity_name':'entitytitle','entity_type':'type','is_person':"isperson = 'T'",'contact_id':'try_cast(contact as double)','customer_id':'cast(customer as varchar)','employee_id':'try_cast(employee as double)','job_id':'try_cast(project as double)','vendor_id':'try_cast(vendor as double)'}}[i]
 edits=[]
 for m in re.finditer(r'CAST\(NULL AS \w+\) AS (\w+)',s):edits.append((m.group(0),maps[m[1]]+' AS '+m[1]))
 multi(i,'placeholder_mapping',edits,'D','生成器整组映射失败后占位NULL；恢复本表源列映射，不动FROM与过滤。另查轨迹判断是否U。')
add(23,'email_order','regexp_full_match(trim(source_email),','regexp_full_match(source_email,','C','契约列出的验证在清洗之前；agent先trim再验证保留空白邮箱。')
# Qualtrics: separate duplicate, parser, and optional filters, independent interventions.
for i in range(26,38):
 s=pkg(i)['agent_final_SQL'][0]['text'];m=re.search(r'    QUALIFY row_number\(\) OVER \([^\n]+\) = 1',s)
 if m:add(i,'preserve_duplicates',m[0],'','O','契约primary_key/unique；gold未去重。')
 for m in re.finditer(r"try_strptime\(cast\(src\.\"([^\"]+)\" AS VARCHAR\), '%Y-%m-%d %H:%M:%S.%f %z'\)::TIMESTAMP AS (\w+)",s):
  if i==37:continue # timestamps excluded from official compared columns here
  add(i,'timestamp_'+m[2],m[0],f'try_cast(src."{m[1]}" AS TIMESTAMP) AS {m[2]}','A','契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。')
add(25,'parse_timestamp',"try_strptime(recorded_date, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP",'try_cast(recorded_date AS TIMESTAMP)','O','契约按实际首次响应月份聚合，gold解析失败合到NULL月份。')
add(25,'keep_null_dates','    WHERE recorded_at IS NOT NULL\n','','C','契约仅筛recorded_date非空，agent增加解析成功过滤；单改需检验是否原因。')
add(37,'email_validation_order',"regexp_matches(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')", "user_id NOT IN (SELECT id FROM raw.user WHERE NOT regexp_full_match(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'))",'O','契约先LOWER(TRIM)再验证，gold验证原文后trim，排除5个带空白邮箱。')
(REC/'022_patch_plan.json').write_text(json.dumps([dict(index=i,**{k:v for k,v in inventory()[i].items() if k in ['task','table','layer']},patches=plans[i]) for i in plans],ensure_ascii=False,indent=2)+'\n')
