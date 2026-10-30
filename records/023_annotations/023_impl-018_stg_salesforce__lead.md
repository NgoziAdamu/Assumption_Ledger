# impl-018 · stg_salesforce__lead

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**A**；把握：高；主要错误点：null_empty_master_record_id。

主因是 master_record_id 的 NULL/空串默认；其他字段默认、日期范围、gold 状态规则与契约不一致形成独立因素。

参与因素：A：null_empty_email_bounced_reason（行减少0，格减少2931）；A：null_empty_fax（行减少0，格减少2703）；A：null_empty_geocode_accuracy（行减少0，格减少2103）；A：null_empty_industry（行减少0，格减少895）；A：null_empty_photo_url（行减少0，格减少2847）；A：null_empty_salutation（行减少0，格减少1470）；A：null_empty_title（行减少0，格减少608）；O：status_filter（行减少0，格减少145）；O：status_value（行减少0，格减少1488）；A：revenue_range（行减少0，格减少1222）；A：converted_date（行减少0，格减少275）。

标记：无。

范围额外清洗不是直接硬约束结论；annual_revenue 主差为小数类型，L2已消失。status_value/status_filter 是gold与契约不一致的O；各处独立记录，不捆绑。

## 材料与比较口径

精简材料包：[023_impl-018_stg_salesforce__lead.md](../023_packages/023_impl-018_stg_salesforce__lead.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
契约行 482–594：

```
482:     - name: stg_salesforce__lead
483:       description: "Cleaned prospect/lead records with validated contact information and lead qualification data"
484:       source_table: raw.lead
485:       columns:
486:         - name: lead_id
487:           data_type: VARCHAR
488:           constraints: [not_null, unique]
489:         - name: first_name
490:           data_type: VARCHAR
491:         - name: last_name
492:           data_type: VARCHAR
493:           constraints: [not_null]
494:         - name: lead_name
495:           data_type: VARCHAR
496:           constraints: [not_null]
497:         - name: email
498:           data_type: VARCHAR
499:         - name: company
500:           data_type: VARCHAR
501:         - name: title
502:           data_type: VARCHAR
503:         - name: phone
504:           data_type: VARCHAR
505:         - name: lead_source
506:           data_type: VARCHAR
507:         - name: status
508:           data_type: VARCHAR
509:           constraints: [not_null]
510:           validation_rules:
511:             - rule: "status IS NOT NULL"
512:               on_failure: delete_row
513:             - rule: "status IN ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')"
514:               on_failure: delete_row
515:             - rule: "status = TRIM(status)"
516:               on_failure: correct
517:         - name: owner_id
518:           data_type: VARCHAR
519:           constraints: [not_null]
520:         - name: is_deleted
521:           data_type: BOOLEAN
522:         - name: lead_description
523:           data_type: VARCHAR
524:         - name: annual_revenue
525:           data_type: DECIMAL(18,3)
526:         - name: city
527:           data_type: VARCHAR
528:         - name: converted_account_id
529:           data_type: VARCHAR
530:         - name: converted_contact_id
531:           data_type: VARCHAR
532:         - name: converted_date
533:           data_type: TIMESTAMP
534:         - name: converted_opportunity_id
535:           data_type: VARCHAR
536:         - name: country
537:           data_type: VARCHAR
538:         - name: country_code
539:           data_type: VARCHAR
540:         - name: created_by_id
541:           data_type: VARCHAR
542:         - name: created_date
543:           data_type: TIMESTAMP
544:         - name: email_bounced_date
545:           data_type: TIMESTAMP
546:         - name: email_bounced_reason
547:           data_type: VARCHAR
548:         - name: fax
549:           data_type: VARCHAR
550:         - name: geocode_accuracy
551:           data_type: VARCHAR
552:         - name: has_opted_out_of_email
553:           data_type: BOOLEAN
554:         - name: industry
555:           data_type: VARCHAR
556:         - name: is_converted
557:           data_type: BOOLEAN
558:         - name: is_unread_by_owner
559:           data_type: BOOLEAN
560:         - name: last_activity_date
561:           data_type: DATE
562:         - name: last_modified_date
563:           data_type: TIMESTAMP
564:         - name: last_referenced_date
565:           data_type: TIMESTAMP
566:         - name: last_viewed_date
567:           data_type: TIMESTAMP
568:         - name: latitude
569:           data_type: DECIMAL(18,3)
570:         - name: longitude
571:           data_type: DECIMAL(18,3)
572:         - name: master_record_id
573:           data_type: VARCHAR
574:         - name: mobile_phone
575:           data_type: VARCHAR
576:         - name: number_of_employees
577:           data_type: INTEGER
578:         - name: photo_url
579:           data_type: VARCHAR
580:         - name: postal_code
581:           data_type: VARCHAR
582:         - name: salutation
583:           data_type: VARCHAR
584:         - name: state
585:           data_type: VARCHAR
586:         - name: state_code
587:           data_type: VARCHAR
588:         - name: street
589:           data_type: VARCHAR
590:         - name: system_modstamp
591:           data_type: TIMESTAMP
592:         - name: website
593:           data_type: VARCHAR
594:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql`，SHA-256 `0c27be47fffe6caeea74f98483c946b23932f44c10ebaa44a8ba2c311e877885`，行 1–55。

```
1: select
2:       id as lead_id,
3:       first_name as first_name,
4:       last_name as last_name,
5:       name as lead_name,
6:       email as email,
7:       company as company,
8:       title as title,
9:       phone as phone,
10:       lead_source as lead_source,
11:       trim(status) as status,
12:       owner_id as owner_id,
13:       is_deleted as is_deleted,
14:       description as lead_description,
15:       try_cast(annual_revenue as DECIMAL(18,3)) as annual_revenue,
16:       city as city,
17:       converted_account_id as converted_account_id,
18:       converted_contact_id as converted_contact_id,
19:       try_cast(converted_date as TIMESTAMP) as converted_date,
20:       converted_opportunity_id as converted_opportunity_id,
21:       country as country,
22:       country_code as country_code,
23:       created_by_id as created_by_id,
24:       try_cast(created_date as TIMESTAMP) as created_date,
25:       try_cast(email_bounced_date as TIMESTAMP) as email_bounced_date,
26:       email_bounced_reason as email_bounced_reason,
27:       fax as fax,
28:       geocode_accuracy as geocode_accuracy,
29:       has_opted_out_of_email as has_opted_out_of_email,
30:       industry as industry,
31:       is_converted as is_converted,
32:       is_unread_by_owner as is_unread_by_owner,
33:       try_cast(last_activity_date as DATE) as last_activity_date,
34:       try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
35:       try_cast(last_referenced_date as TIMESTAMP) as last_referenced_date,
36:       try_cast(last_viewed_date as TIMESTAMP) as last_viewed_date,
37:       try_cast(latitude as DECIMAL(18,3)) as latitude,
38:       try_cast(longitude as DECIMAL(18,3)) as longitude,
39:       master_record_id as master_record_id,
40:       mobile_phone as mobile_phone,
41:       try_cast(number_of_employees as INTEGER) as number_of_employees,
42:       photo_url as photo_url,
43:       postal_code as postal_code,
44:       salutation as salutation,
45:       state as state,
46:       state_code as state_code,
47:       street as street,
48:       try_cast(system_modstamp as TIMESTAMP) as system_modstamp,
49:       website as website
50: from raw.lead
51: where id is not null
52:   and last_name is not null
53:   and name is not null
54:   and trim(status) in ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')
55: qualify row_number() over (partition by id order by id) = 1
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql`，SHA-256 `7f5a80fd8f184a014545a111099712393c91a562be05ef45d8c805d98a8494e1`，行 1–202。

```
1: with fields as (
2:     select *
3:     from raw.lead
4: ),
5: 
6: validated as (
7:     select
8:         *,
9: 
10:         -- Primary key validation
11:         case
12:             when id is null then 1
13:             when not (id ~ '^[A-Za-z0-9]{15,18}$') then 1
14:             else 0
15:         end as lead_id_validation_failed,
16: 
17:         -- Email validation - format and length per YAML spec
18:         case
19:             when email is null then 0 -- Optional field, null OK
20:             when trim(email) = '' then 0 -- Empty is OK
21:             when length(trim(email)) > 255 then 1 -- Too long per YAML spec
22:             when not (lower(trim(email)) ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') then 1 -- Invalid format
23:             else 0
24:         end as email_validation_failed,
25: 
26:         -- Phone number validation - basic format check per YAML spec
27:         case
28:             when phone is null then 0 -- Optional field, null OK
29:             when length(phone) > 50 then 1 -- Too long per YAML spec
30:             else 0
31:         end as phone_validation_failed,
32: 
33:         -- Mobile phone validation
34:         case
35:             when mobile_phone is null then 0 -- Optional field, null OK
36:             when length(mobile_phone) > 50 then 1 -- Too long per YAML spec
37:             else 0
38:         end as mobile_phone_validation_failed,
39: 
40:         -- Name validation - required field per YAML spec
41:         case
42:             when name is null then 1 -- Required field
43:             when trim(name) = '' then 1 -- Empty name not allowed
44:             when length(trim(name)) > 255 then 1 -- Length validation per YAML spec
45:             else 0
46:         end as lead_name_validation_failed,
47: 
48:         -- Company validation - business requirement
49:         case
50:             when company is null then 1 -- Required field per business rules
51:             when trim(company) = '' then 1 -- Empty company not allowed
52:             when length(trim(company)) > 255 then 1 -- Length validation
53:             else 0
54:         end as company_validation_failed,
55: 
56:         -- Owner ID foreign key validation
57:         case
58:             when owner_id is not null and not (owner_id ~ '^[A-Za-z0-9]{15,18}$') then 1
59:             when owner_id is not null and owner_id not in (select id from raw.user) then 1
60:             else 0
61:         end as owner_id_validation_failed,
62: 
63:         -- Status validation per YAML spec - validate against allowed values
64:         case
65:             when status is null then 0 -- Status can be null
66:             when trim(status) in ('Open', 'Closed - Converted', 'Closed - Not Converted') then 0 -- Valid values
67:             when trim(status) not in ('Open', 'Closed - Converted', 'Closed - Not Converted') then 1 -- Invalid values
68:             else 0
69:         end as status_validation_failed,
70: 
71:         -- Date validation - converted date validation per YAML spec
72:         case
73:             when converted_date is null then 0 -- Converted date can be null
74:             when converted_date < '1900-01-01' then 1 -- Too old per YAML spec
75:             when converted_date > current_date + interval '1 year' then 1 -- Too far future per YAML spec
76:             when converted_date < created_date::DATE then 1 -- Logical violation
77:             else 0
78:         end as converted_date_validation_failed,
79: 
80:         -- Annual revenue validation
81:         case
82:             when annual_revenue is null then 0 -- Annual revenue can be null
83:             when annual_revenue < 0 then 1 -- Negative revenue not allowed per YAML spec
84:             when annual_revenue > 999999999999.99 then 1 -- Revenue too large per YAML spec
85:             else 0
86:         end as annual_revenue_validation_failed,
87: 
88:         -- Website validation per YAML spec
89:         case
90:             when website is null then 0 -- Website can be null
91:             when length(website) > 255 then 1 -- Too long per YAML spec
92:             when not (website ~ '^https?://[A-Za-z0-9\-\.]+\.[A-Za-z]{2,}.*$') then 1 -- URL format validation
93:             else 0
94:         end as website_validation_failed
95: 
96:     from fields
97: ),
98: 
99: final as (
100:     select
101:         case
102:             when lead_id_validation_failed = 1 then null
103:             else cast(id as varchar)
104:         end as lead_id,
105:         case
106:             when annual_revenue_validation_failed = 1 then null
107:             else cast(annual_revenue as decimal(18,2))  -- Per YAML spec precision
108:         end as annual_revenue,
109:         cast(trim(coalesce(city, '')) as varchar) as city,
110:         case
111:             when company_validation_failed = 1 then trim(company)
112:             else trim(company)
113:         end as company,
114:         cast(converted_account_id as varchar) as converted_account_id,
115:         cast(converted_contact_id as varchar) as converted_contact_id,
116:         case
117:             when converted_date_validation_failed = 1 then null
118:             else cast(converted_date as timestamp)
119:         end as converted_date,
120:         cast(converted_opportunity_id as varchar) as converted_opportunity_id,
121:         cast(trim(coalesce(country, '')) as varchar) as country,
122:         cast(trim(coalesce(country_code, '')) as varchar) as country_code,
123:         cast(created_by_id as varchar) as created_by_id,
124:         cast(created_date as timestamp) as created_date,
125:         cast(trim(coalesce(description, '')) as varchar) as lead_description,
126:         case
127:             when email_validation_failed = 1 then null
128:             when trim(email) = '' then null
129:             else lower(trim(email))
130:         end as email,
131:         cast(email_bounced_date as timestamp) as email_bounced_date,
132:         cast(trim(coalesce(email_bounced_reason, '')) as varchar) as email_bounced_reason,
133:         cast(trim(coalesce(fax, '')) as varchar) as fax,
134:         cast(trim(coalesce(first_name, '')) as varchar) as first_name,
135:         cast(trim(coalesce(geocode_accuracy, '')) as varchar) as geocode_accuracy,
136:         cast(coalesce(has_opted_out_of_email, false) as boolean) as has_opted_out_of_email,
137:         cast(trim(coalesce(industry, '')) as varchar) as industry,
138:         cast(coalesce(is_converted, false) as boolean) as is_converted,
139:         cast(coalesce(is_deleted, false) as boolean) as is_deleted,
140:         cast(coalesce(is_unread_by_owner, false) as boolean) as is_unread_by_owner,
141:         cast(last_activity_date as date) as last_activity_date,
142:         cast(last_modified_date as timestamp) as last_modified_date,
143:         cast(trim(coalesce(last_name, '')) as varchar) as last_name,
144:         cast(last_referenced_date as timestamp) as last_referenced_date,
145:         cast(last_viewed_date as timestamp) as last_viewed_date,
146:         cast(latitude as decimal(10,6)) as latitude,
147:         cast(trim(coalesce(lead_source, '')) as varchar) as lead_source,
148:         cast(longitude as decimal(10,6)) as longitude,
149:         cast(trim(coalesce(master_record_id, '')) as varchar) as master_record_id,
150:         case
151:             when mobile_phone_validation_failed = 1 then null
152:             when mobile_phone is null then null
153:             when length(mobile_phone) > 50 then null
154:             else cast(trim(mobile_phone) as varchar)
155:         end as mobile_phone,
156:         case
157:             when lead_name_validation_failed = 1 then trim(name)
158:             else trim(name)
159:         end as lead_name,
160:         cast(number_of_employees as integer) as number_of_employees,
161:         case
162:             when owner_id_validation_failed = 1 then null
163:             else cast(owner_id as varchar)
164:         end as owner_id,
165:         case
166:             when phone_validation_failed = 1 then null
167:             when phone is null then null
168:             when length(phone) > 50 then null
169:             else cast(trim(phone) as varchar)
170:         end as phone,
171:         case
172:             when photo_url is not null and length(photo_url) > 500 then null
173:             else cast(trim(coalesce(photo_url, '')) as varchar)
174:         end as photo_url,
175:         cast(trim(coalesce(postal_code, '')) as varchar) as postal_code,
176:         cast(trim(coalesce(salutation, '')) as varchar) as salutation,
177:         cast(trim(coalesce(state, '')) as varchar) as state,
178:         cast(trim(coalesce(state_code, '')) as varchar) as state_code,
179:         case
180:             when status_validation_failed = 1 then null -- nullify invalid status
181:             else cast(trim(status) as varchar)
182:         end as status,
183:         cast(trim(coalesce(street, '')) as varchar) as street,
184:         cast(system_modstamp as timestamp) as system_modstamp,
185:         cast(trim(coalesce(title, '')) as varchar) as title,
186:         case
187:             when website_validation_failed = 1 then null
188:             else trim(website)
189:         end as website,
190: 
191:         -- Standard audit trail field per YAML spec
192:         current_timestamp as _dbt_loaded_at
193: 
194:     from validated
195:     where lead_id_validation_failed = 0
196:       and lead_name_validation_failed = 0
197:       and company_validation_failed = 0
198: )
199: 
200: select *
201: from final
202: where not coalesce(is_deleted, false)
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 17/18 查看raw；event 89/90 检查契约；event 99 未解释 master_record_id 默认。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/17.json`。
- event 18：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/18.json`。
- event 89：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/89.json`。
- event 90：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/90.json`。
- event 99：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：status 与缺失字段

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE status IS NULL OR trim(status) NOT IN ('Open - Not Contacted','Working - Contacted','Closed - Converted','Closed - Not Converted')) invalid_status,count(*) FILTER(WHERE master_record_id IS NULL) missing_master FROM raw.lead
```


```json
{"columns":["n","invalid_status","missing_master"],"rows":[[3000,4,3000]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-018_stg_salesforce__lead.json](../023_reruns_impl-018_stg_salesforce__lead.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|19710|否|
|L1|2996|3000|3000|18488|否|
|L2|2996|3000|3000|18488|否|
|L3|2996|3000|3000|18488|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/baseline.sql`；SHA-256 `0c27be47fffe6caeea74f98483c946b23932f44c10ebaa44a8ba2c311e877885`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|19710|否|
|L1|2996|3000|3000|18488|否|
|L2|2996|3000|3000|18488|否|
|L3|2996|3000|3000|18488|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### null_empty_email_bounced_reason

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2931；按行优先、格次之排序。
共同控制后 SQL 第 26 行起、字符 offset 920 的唯一连续替换；其余字节不动。
替换前：
```sql
email_bounced_reason as email_bounced_reason
```

替换后：
```sql
coalesce(email_bounced_reason, '') as email_bounced_reason
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/null_empty_email_bounced_reason.sql`；SHA-256 `08c1324fd6194add5937c8b49c0b20693bd4e13fc26885da2c75b1621dd75358`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|16779|否|
|L1|2996|3000|3000|15557|否|
|L2|2996|3000|3000|15557|否|
|L3|2996|3000|3000|15557|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":4,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":4,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":4,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":4,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### null_empty_fax

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2703；按行优先、格次之排序。
共同控制后 SQL 第 27 行起、字符 offset 972 的唯一连续替换；其余字节不动。
替换前：
```sql
fax as fax
```

替换后：
```sql
coalesce(fax, '') as fax
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/null_empty_fax.sql`；SHA-256 `eb3a842952ee65962479899155d97313425e3bbcc0f250513df505c32091d0ce`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|17007|否|
|L1|2996|3000|3000|15785|否|
|L2|2996|3000|3000|15785|否|
|L3|2996|3000|3000|15785|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":4,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":4,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":4,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":4,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### null_empty_geocode_accuracy

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2103；按行优先、格次之排序。
共同控制后 SQL 第 28 行起、字符 offset 990 的唯一连续替换；其余字节不动。
替换前：
```sql
geocode_accuracy as geocode_accuracy
```

替换后：
```sql
coalesce(geocode_accuracy, '') as geocode_accuracy
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/null_empty_geocode_accuracy.sql`；SHA-256 `467ddce2219b6421ea0c851df8800490d90a581655f78ce8b66fd638cba54c5a`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|17607|否|
|L1|2996|3000|3000|16385|否|
|L2|2996|3000|3000|16385|否|
|L3|2996|3000|3000|16385|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":4,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":4,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":4,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":4,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### null_empty_industry

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 895；按行优先、格次之排序。
共同控制后 SQL 第 30 行起、字符 offset 1090 的唯一连续替换；其余字节不动。
替换前：
```sql
industry as industry
```

替换后：
```sql
coalesce(industry, '') as industry
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/null_empty_industry.sql`；SHA-256 `2068056f65f5379b3a2fb7ee45035b8c41635556e7201ed242ed26b92b75e82f`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|18815|否|
|L1|2996|3000|3000|17593|否|
|L2|2996|3000|3000|17593|否|
|L3|2996|3000|3000|17593|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":4,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":4,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":4,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":4,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### null_empty_master_record_id

判定：主因；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2996；按行优先、格次之排序。
共同控制后 SQL 第 39 行起、字符 offset 1593 的唯一连续替换；其余字节不动。
替换前：
```sql
master_record_id as master_record_id
```

替换后：
```sql
coalesce(master_record_id, '') as master_record_id
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/null_empty_master_record_id.sql`；SHA-256 `b7ef7d78af847450730a0088dd44cc6dd7257ba37668c2416dd2897c86241fdd`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|16714|否|
|L1|2996|3000|3000|15492|否|
|L2|2996|3000|3000|15492|否|
|L3|2996|3000|3000|15492|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":4,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":4,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":4,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":4,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### null_empty_photo_url

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2847；按行优先、格次之排序。
共同控制后 SQL 第 42 行起、字符 offset 1744 的唯一连续替换；其余字节不动。
替换前：
```sql
photo_url as photo_url
```

替换后：
```sql
coalesce(photo_url, '') as photo_url
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/null_empty_photo_url.sql`；SHA-256 `3a6faba34c6205b88f3404de44e79c4d721efe59f1b271710f11034f0875d3e3`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|16863|否|
|L1|2996|3000|3000|15641|否|
|L2|2996|3000|3000|15641|否|
|L3|2996|3000|3000|15641|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":4,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":4,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":4,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":4,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### null_empty_salutation

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 1470；按行优先、格次之排序。
共同控制后 SQL 第 44 行起、字符 offset 1808 的唯一连续替换；其余字节不动。
替换前：
```sql
salutation as salutation
```

替换后：
```sql
coalesce(salutation, '') as salutation
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/null_empty_salutation.sql`；SHA-256 `b3dde8552bc2c37c8e7084ececb94793f99f37b76fee9de40703eaa81e9994ee`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|18240|否|
|L1|2996|3000|3000|17018|否|
|L2|2996|3000|3000|17018|否|
|L3|2996|3000|3000|17018|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":4,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":4,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":4,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":4,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### null_empty_title

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 608；按行优先、格次之排序。
共同控制后 SQL 第 8 行起、字符 offset 169 的唯一连续替换；其余字节不动。
替换前：
```sql
title as title
```

替换后：
```sql
coalesce(title, '') as title
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/null_empty_title.sql`；SHA-256 `ee07878e3754d16b48bae760ccb1e7f9d8c33d07031ff444871907b70e40748c`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|19102|否|
|L1|2996|3000|3000|17880|否|
|L2|2996|3000|3000|17880|否|
|L3|2996|3000|3000|17880|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":4,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":4,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":4,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":4,"website":4}`

#### status_filter

判定：参与因素；类别候选 O。契约要求枚举并删除无效值，gold 留存。

相对本轮基线减少行 0、格 145；按行优先、格次之排序。
共同控制后 SQL 第 54 行起、字符 offset 2090 的唯一连续替换；其余字节不动。
替换前：
```sql
and trim(status) in ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')
```

替换后：
```sql
and TRUE
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/status_filter.sql`；SHA-256 `af0f423fd5a23ba4078f12f4f556e06450f9a022bbed3feaf5cad5d0e58f9593`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|19565|否|
|L1|3000|3000|3000|18342|否|
|L2|3000|3000|3000|18342|否|
|L3|3000|3000|3000|18342|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"annual_revenue":1223,"converted_date":276,"email_bounced_reason":2935,"fax":2707,"geocode_accuracy":2106,"industry":895,"master_record_id":3000,"photo_url":2851,"salutation":1471,"status":1492,"title":609}`
- L1：`{"converted_date":276,"email_bounced_reason":2935,"fax":2707,"geocode_accuracy":2106,"industry":895,"master_record_id":3000,"photo_url":2851,"salutation":1471,"status":1492,"title":609}`
- L2：`{"converted_date":276,"email_bounced_reason":2935,"fax":2707,"geocode_accuracy":2106,"industry":895,"master_record_id":3000,"photo_url":2851,"salutation":1471,"status":1492,"title":609}`
- L3：`{"converted_date":276,"email_bounced_reason":2935,"fax":2707,"geocode_accuracy":2106,"industry":895,"master_record_id":3000,"photo_url":2851,"salutation":1471,"status":1492,"title":609}`

#### status_value

判定：参与因素；类别候选 O。gold 对契约允许的两种 status 置空。

相对本轮基线减少行 0、格 1488；按行优先、格次之排序。
共同控制后 SQL 第 11 行起、字符 offset 247 的唯一连续替换；其余字节不动。
替换前：
```sql
trim(status) as status
```

替换后：
```sql
case when trim(status) in ('Open', 'Closed - Converted', 'Closed - Not Converted') then trim(status) else null end as status
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/status_value.sql`；SHA-256 `e1e96c43f717f6e07022ed2bea694bbfcc2c25e4d2ecee87902c06555eca3e61`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|18222|否|
|L1|2996|3000|3000|17000|否|
|L2|2996|3000|3000|17000|否|
|L3|2996|3000|3000|17000|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":4,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":4,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":4,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":4,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### revenue_range

判定：参与因素；类别候选 A。契约未规定 annual revenue 边界，gold 额外范围清洗；负收入不一概视为硬约束。

相对本轮基线减少行 0、格 1222；按行优先、格次之排序。
共同控制后 SQL 第 15 行起、字符 offset 376 的唯一连续替换；其余字节不动。
替换前：
```sql
try_cast(annual_revenue as DECIMAL(18,3))
```

替换后：
```sql
case when annual_revenue<0 or annual_revenue>999999999999.99 then null else try_cast(annual_revenue as DECIMAL(18,2)) end
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/revenue_range.sql`；SHA-256 `c152a7703b870a00c2b58f080fbb118496dd70f8926dbbd35f9256aadf3df665`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|18488|否|
|L1|2996|3000|3000|18488|否|
|L2|2996|3000|3000|18488|否|
|L3|2996|3000|3000|18488|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":279,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

#### converted_date

判定：参与因素；类别候选 A。契约未规定 converted_date 清洗范围，gold 额外清洗。

相对本轮基线减少行 0、格 275；按行优先、格次之排序。
共同控制后 SQL 第 19 行起、字符 offset 567 的唯一连续替换；其余字节不动。
替换前：
```sql
try_cast(converted_date as TIMESTAMP)
```

替换后：
```sql
case when converted_date < DATE '1900-01-01' or converted_date > current_date + interval '1 year' or converted_date < created_date::DATE then null else try_cast(converted_date as TIMESTAMP) end
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__lead/converted_date.sql`；SHA-256 `42b3c79360e068f683c92c7452a55fcd95e67793fc89ee3b79e2a6ac39d79645`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2996|3000|3000|19435|否|
|L1|2996|3000|3000|18213|否|
|L2|2996|3000|3000|18213|否|
|L3|2996|3000|3000|18213|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_id":4,"annual_revenue":1226,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":4,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L1：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":4,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L2：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":4,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`
- L3：`{"lead_id":4,"annual_revenue":4,"city":4,"company":4,"converted_account_id":4,"converted_contact_id":4,"converted_date":4,"converted_opportunity_id":4,"country":4,"country_code":4,"created_by_id":4,"email":4,"email_bounced_date":4,"email_bounced_reason":2935,"fax":2707,"first_name":4,"geocode_accuracy":2107,"has_opted_out_of_email":4,"industry":899,"is_converted":4,"is_deleted":4,"is_unread_by_owner":4,"last_activity_date":4,"last_modified_date":4,"last_name":4,"last_referenced_date":4,"last_viewed_date":4,"lead_source":4,"master_record_id":3000,"mobile_phone":4,"number_of_employees":4,"owner_id":4,"phone":4,"photo_url":2851,"postal_code":4,"salutation":1474,"state":4,"state_code":4,"status":1492,"street":4,"system_modstamp":4,"title":612,"website":4}`

## 规则问题

无
