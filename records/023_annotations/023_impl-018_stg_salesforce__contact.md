# impl-018 · stg_salesforce__contact

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**A**；把握：高；主要错误点：null_empty_master_record_id。

主要为 master_record_id 的 NULL 与空串选择；另13处字段默认选择各自独立构成 A 因素。

参与因素：A：null_empty_assistant_name（行减少0，格减少2667）；A：null_empty_department（行减少0，格减少1210）；A：null_empty_email_bounced_reason（行减少0，格减少2955）；A：null_empty_fax（行减少0，格减少2854）；A：null_empty_lead_source（行减少0，格减少906）；A：null_empty_other_city（行减少0，格减少2407）；A：null_empty_other_country（行减少0，格减少2389）；A：null_empty_other_postal_code（行减少0，格减少2409）；A：null_empty_other_state（行减少0，格减少2430）；A：null_empty_other_street（行减少0，格减少2421）；A：null_empty_photo_url（行减少0，格减少2713）；A：null_empty_salutation（行减少0，格减少1250）；A：null_empty_title（行减少0，格减少579）。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-018_stg_salesforce__contact.md](../023_packages/023_impl-018_stg_salesforce__contact.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
契约行 124–286：

```
124:     - name: stg_salesforce__contact
125:       description: "Cleaned and validated individual contact records with standardized personal and professional information"
126:       source_table: raw.contact
127:       columns:
128:         - name: account_id
129:           data_type: VARCHAR
130:           validation_rules:
131:             - rule: "account_id IS NULL OR account_id ~ '^[A-Za-z0-9]{15,18}$'"
132:               on_failure: nullify_field
133:             - rule: "account_id IS NULL OR account_id IN (SELECT id FROM raw.account)"
134:               on_failure: nullify_field
135:         - name: assistant_name
136:           data_type: VARCHAR
137:         - name: assistant_phone
138:           data_type: VARCHAR
139:           validation_rules:
140:             - rule: "assistant_phone IS NULL OR LENGTH(assistant_phone) <= 50"
141:               on_failure: nullify_field
142:             - rule: "assistant_phone IS NULL OR assistant_phone = TRIM(assistant_phone)"
143:               on_failure: correct
144:         - name: birthdate
145:           data_type: DATE
146:           validation_rules:
147:             - rule: "birthdate IS NULL OR birthdate >= DATE '1900-01-01'"
148:               on_failure: nullify_field
149:             - rule: "birthdate IS NULL OR birthdate <= CURRENT_DATE"
150:               on_failure: nullify_field
151:         - name: created_date
152:           data_type: TIMESTAMP
153:         - name: department
154:           data_type: VARCHAR
155:         - name: contact_description
156:           data_type: VARCHAR
157:         - name: email
158:           data_type: VARCHAR
159:           validation_rules:
160:             - rule: "email = LOWER(TRIM(email))"
161:               on_failure: correct
162:             - rule: "email IS NULL OR LENGTH(email) <= 255"
163:               on_failure: nullify_field
164:             - rule: "email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
165:               on_failure: nullify_field
166:         - name: email_bounced_date
167:           data_type: TIMESTAMP
168:         - name: email_bounced_reason
169:           data_type: VARCHAR
170:         - name: fax
171:           data_type: VARCHAR
172:         - name: first_name
173:           data_type: VARCHAR
174:         - name: home_phone
175:           data_type: VARCHAR
176:           validation_rules:
177:             - rule: "home_phone IS NULL OR LENGTH(home_phone) <= 50"
178:               on_failure: nullify_field
179:             - rule: "home_phone IS NULL OR home_phone = TRIM(home_phone)"
180:               on_failure: correct
181:         - name: contact_id
182:           data_type: VARCHAR
183:           constraints: [not_null]
184:           validation_rules:
185:             - rule: "contact_id ~ '^[A-Za-z0-9]{15,18}$'"
186:               on_failure: delete_row
187:         - name: is_deleted
188:           data_type: BOOLEAN
189:           validation_rules:
190:             - rule: "NOT COALESCE(is_deleted, false)"
191:               on_failure: delete_row
192:         - name: is_email_bounced
193:           data_type: BOOLEAN
194:         - name: last_activity_date
195:           data_type: DATE
196:         - name: last_curequest_date
197:           data_type: TIMESTAMP
198:         - name: last_cuupdate_date
199:           data_type: TIMESTAMP
200:         - name: last_modified_date
201:           data_type: TIMESTAMP
202:         - name: last_name
203:           data_type: VARCHAR
204:           constraints: [not_null]
205:         - name: last_referenced_date
206:           data_type: TIMESTAMP
207:         - name: last_viewed_date
208:           data_type: TIMESTAMP
209:         - name: lead_source
210:           data_type: VARCHAR
211:         - name: mailing_city
212:           data_type: VARCHAR
213:         - name: mailing_country
214:           data_type: VARCHAR
215:         - name: mailing_country_code
216:           data_type: VARCHAR
217:         - name: mailing_postal_code
218:           data_type: VARCHAR
219:         - name: mailing_state
220:           data_type: VARCHAR
221:         - name: mailing_state_code
222:           data_type: VARCHAR
223:         - name: mailing_street
224:           data_type: VARCHAR
225:         - name: master_record_id
226:           data_type: VARCHAR
227:         - name: mobile_phone
228:           data_type: VARCHAR
229:           validation_rules:
230:             - rule: "mobile_phone IS NULL OR LENGTH(mobile_phone) <= 50"
231:               on_failure: nullify_field
232:             - rule: "mobile_phone IS NULL OR mobile_phone = TRIM(mobile_phone)"
233:               on_failure: correct
234:         - name: contact_name
235:           data_type: VARCHAR
236:           constraints: [not_null]
237:         - name: other_city
238:           data_type: VARCHAR
239:         - name: other_country
240:           data_type: VARCHAR
241:         - name: other_phone
242:           data_type: VARCHAR
243:           validation_rules:
244:             - rule: "other_phone IS NULL OR LENGTH(other_phone) <= 50"
245:               on_failure: nullify_field
246:             - rule: "other_phone IS NULL OR other_phone = TRIM(other_phone)"
247:               on_failure: correct
248:         - name: other_postal_code
249:           data_type: VARCHAR
250:         - name: other_state
251:           data_type: VARCHAR
252:         - name: other_street
253:           data_type: VARCHAR
254:         - name: owner_id
255:           data_type: VARCHAR
256:           validation_rules:
257:             - rule: "owner_id IS NULL OR owner_id ~ '^[A-Za-z0-9]{15,18}$'"
258:               on_failure: nullify_field
259:             - rule: "owner_id IS NULL OR owner_id IN (SELECT id FROM raw.user)"
260:               on_failure: nullify_field
261:         - name: phone
262:           data_type: VARCHAR
263:           validation_rules:
264:             - rule: "phone IS NULL OR LENGTH(phone) <= 50"
265:               on_failure: nullify_field
266:             - rule: "phone IS NULL OR phone = TRIM(phone)"
267:               on_failure: correct
268:         - name: photo_url
269:           data_type: VARCHAR
270:           validation_rules:
271:             - rule: "photo_url IS NULL OR LENGTH(photo_url) <= 500"
272:               on_failure: nullify_field
273:             - rule: "photo_url IS NULL OR photo_url = TRIM(photo_url)"
274:               on_failure: correct
275:         - name: reports_to_id
276:           data_type: VARCHAR
277:           validation_rules:
278:             - rule: "reports_to_id IS NULL OR reports_to_id ~ '^[A-Za-z0-9]{15,18}$'"
279:               on_failure: nullify_field
280:             - rule: "reports_to_id IS NULL OR reports_to_id IN (SELECT id FROM raw.contact)"
281:               on_failure: nullify_field
282:         - name: salutation
283:           data_type: VARCHAR
284:         - name: title
285:           data_type: VARCHAR
286:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql`，SHA-256 `8976caf476c66d76c48755f33237c4aa1504a5359decca61fc8955c9807e96ce`，行 1–51。

```
1: select
2:       case when account_id is null or (regexp_matches(account_id, '^[A-Za-z0-9]{15,18}$') and account_id in (select id from raw.account)) then account_id else null end as account_id,
3:       assistant_name as assistant_name,
4:       case when assistant_phone is null or length(trim(assistant_phone)) <= 50 then trim(assistant_phone) end as assistant_phone,
5:       case when try_cast(birthdate as date) between date '1900-01-01' and current_date then try_cast(birthdate as date) else null end as birthdate,
6:       cast(null as TIMESTAMP) as created_date,
7:       department as department,
8:       description as contact_description,
9:       case when email is null or (length(lower(trim(email))) <= 255 and regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')) then lower(trim(email)) else null end as email,
10:       try_cast(email_bounced_date as TIMESTAMP) as email_bounced_date,
11:       email_bounced_reason as email_bounced_reason,
12:       fax as fax,
13:       first_name as first_name,
14:       case when home_phone is null or length(trim(home_phone)) <= 50 then trim(home_phone) end as home_phone,
15:       id as contact_id,
16:       is_deleted as is_deleted,
17:       is_email_bounced as is_email_bounced,
18:       try_cast(last_activity_date as DATE) as last_activity_date,
19:       try_cast(last_curequest_date as TIMESTAMP) as last_curequest_date,
20:       try_cast(last_cuupdate_date as TIMESTAMP) as last_cuupdate_date,
21:       try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
22:       last_name as last_name,
23:       try_cast(last_referenced_date as TIMESTAMP) as last_referenced_date,
24:       try_cast(last_viewed_date as TIMESTAMP) as last_viewed_date,
25:       lead_source as lead_source,
26:       mailing_city as mailing_city,
27:       mailing_country as mailing_country,
28:       mailing_country_code as mailing_country_code,
29:       mailing_postal_code as mailing_postal_code,
30:       mailing_state as mailing_state,
31:       mailing_state_code as mailing_state_code,
32:       mailing_street as mailing_street,
33:       master_record_id as master_record_id,
34:       case when mobile_phone is null or length(trim(mobile_phone)) <= 50 then trim(mobile_phone) end as mobile_phone,
35:       name as contact_name,
36:       other_city as other_city,
37:       other_country as other_country,
38:       case when other_phone is null or length(trim(other_phone)) <= 50 then trim(other_phone) end as other_phone,
39:       other_postal_code as other_postal_code,
40:       other_state as other_state,
41:       other_street as other_street,
42:       case when owner_id is null or (regexp_matches(owner_id, '^[A-Za-z0-9]{15,18}$') and owner_id in (select id from raw.user)) then owner_id else null end as owner_id,
43:       case when phone is null or length(trim(phone)) <= 50 then trim(phone) end as phone,
44:       case when photo_url is null or length(trim(photo_url)) <= 500 then trim(photo_url) end as photo_url,
45:       case when reports_to_id is null or (regexp_matches(reports_to_id, '^[A-Za-z0-9]{15,18}$') and reports_to_id in (select id from raw.contact)) then reports_to_id else null end as reports_to_id,
46:       salutation as salutation,
47:       title as title
48: from raw.contact
49: where id is not null
50:   and regexp_matches(id, '^[A-Za-z0-9]{15,18}$')
51:   and not coalesce(is_deleted, false)
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql`，SHA-256 `c6dce6cc2474727db86789f21d3472aa9508df5191a2c7e924d14c9942bf3e8b`，行 1–188。

```
1: with fields as (
2:     select *
3:     from raw.contact
4: ),
5: 
6: validated as (
7:     select
8:         *,
9: 
10:         -- Contact ID validation - primary key format and existence
11:         case
12:             when id is null then 1
13:             when not (id ~ '^[A-Za-z0-9]{15,18}$') then 1
14:             else 0
15:         end as contact_id_validation_failed,
16: 
17:         -- Account ID foreign key validation
18:         case
19:             when account_id is not null and not (account_id ~ '^[A-Za-z0-9]{15,18}$') then 1
20:             when account_id is not null and account_id not in (select id from raw.account) then 1
21:             else 0
22:         end as account_id_validation_failed,
23: 
24:         -- Reports to ID foreign key validation
25:         case
26:             when reports_to_id is not null and not (reports_to_id ~ '^[A-Za-z0-9]{15,18}$') then 1
27:             when reports_to_id is not null and reports_to_id not in (select id from raw.contact) then 1
28:             else 0
29:         end as reports_to_id_validation_failed,
30: 
31:         -- Email validation - format and length per YAML spec
32:         case
33:             when email is null then 0 -- Optional field, null OK
34:             when trim(email) = '' then 0 -- Empty is OK
35:             when length(trim(email)) > 255 then 1 -- Too long per YAML spec
36:             when not (lower(trim(email)) ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') then 1 -- Invalid format
37:             else 0
38:         end as email_validation_failed,
39: 
40:         -- Phone number validation - basic format check (per YAML spec)
41:         case
42:             when phone is null then 0 -- Optional field, null OK
43:             when length(phone) > 50 then 1 -- Too long per YAML spec
44:             else 0
45:         end as phone_validation_failed,
46: 
47:         -- Mobile phone validation
48:         case
49:             when mobile_phone is null then 0 -- Optional field, null OK
50:             when length(mobile_phone) > 50 then 1 -- Too long per yaml spec
51:             else 0
52:         end as mobile_phone_validation_failed,
53: 
54:         -- Name validation - required field according to business rules
55:         case
56:             when coalesce(trim(first_name), '''') = '''' and coalesce(trim(last_name), '''') = '''' then 1
57:             else 0
58:         end as contact_name_validation_failed,
59: 
60:         -- Birthdate validation - reasonable ranges
61:         case
62:             when birthdate is null then 0 -- Optional field
63:             when birthdate < '1900-01-01' then 1 -- Too old per YAML spec
64:             when birthdate > current_date then 1 -- Future date per YAML spec
65:             else 0
66:         end as birthdate_validation_failed,
67: 
68:         -- Owner ID foreign key validation
69:         case
70:             when owner_id is not null and not (owner_id ~ '^[A-Za-z0-9]{15,18}$') then 1
71:             when owner_id is not null and owner_id not in (select id from raw.user) then 1
72:             else 0
73:         end as owner_id_validation_failed,
74: 
75:         -- Is deleted validation - ensure it's actually boolean
76:         case
77:             when coalesce(is_deleted, false) not in (true, false) then 1
78:             else 0
79:         end as is_deleted_validation_failed
80: 
81:     from fields
82: ),
83: 
84: final as (
85:     select
86:         case
87:             when account_id_validation_failed = 1 then null
88:             else cast(account_id as varchar)
89:         end as account_id,
90:         cast(trim(coalesce(assistant_name, '')) as varchar) as assistant_name,
91:         case
92:             when assistant_phone is null then null
93:             when length(assistant_phone) > 50 then null
94:             else cast(trim(assistant_phone) as varchar)
95:         end as assistant_phone,
96:         case
97:             when birthdate_validation_failed = 1 then null
98:             else cast(birthdate as date)
99:         end as birthdate,
100:         cast(system_modstamp as timestamp) as created_date,
101:         cast(trim(coalesce(department, '')) as varchar) as department,
102:         cast(trim(coalesce(description, '')) as varchar) as contact_description,
103:         case
104:             when email_validation_failed = 1 then null
105:             when trim(email) = '' then null
106:             else lower(trim(email))
107:         end as email,
108:         cast(email_bounced_date as timestamp) as email_bounced_date,
109:         cast(trim(coalesce(email_bounced_reason, '')) as varchar) as email_bounced_reason,
110:         cast(trim(coalesce(fax, '')) as varchar) as fax,
111:         cast(trim(coalesce(first_name, '')) as varchar) as first_name,
112:         case
113:             when phone_validation_failed = 1 then null
114:             when home_phone is null then null
115:             when length(home_phone) > 50 then null
116:             else cast(trim(home_phone) as varchar)
117:         end as home_phone,
118:         case
119:             when contact_id_validation_failed = 1 then null
120:             else cast(id as varchar)
121:         end as contact_id,
122:         cast(coalesce(is_deleted, false) as boolean) as is_deleted,
123:         cast(coalesce(is_email_bounced, false) as boolean) as is_email_bounced,
124:         cast(last_activity_date as date) as last_activity_date,
125:         cast(last_curequest_date as timestamp) as last_curequest_date,
126:         cast(last_cuupdate_date as timestamp) as last_cuupdate_date,
127:         cast(last_modified_date as timestamp) as last_modified_date,
128:         cast(trim(coalesce(last_name, '')) as varchar) as last_name,
129:         cast(last_referenced_date as timestamp) as last_referenced_date,
130:         cast(last_viewed_date as timestamp) as last_viewed_date,
131:         cast(trim(coalesce(lead_source, '')) as varchar) as lead_source,
132:         cast(trim(coalesce(mailing_city, '')) as varchar) as mailing_city,
133:         cast(trim(coalesce(mailing_country, '')) as varchar) as mailing_country,
134:         cast(trim(coalesce(mailing_country_code, '')) as varchar) as mailing_country_code,
135:         cast(trim(coalesce(mailing_postal_code, '')) as varchar) as mailing_postal_code,
136:         cast(trim(coalesce(mailing_state, '')) as varchar) as mailing_state,
137:         cast(trim(coalesce(mailing_state_code, '')) as varchar) as mailing_state_code,
138:         cast(trim(coalesce(mailing_street, '')) as varchar) as mailing_street,
139:         cast(trim(coalesce(master_record_id, '')) as varchar) as master_record_id,
140:         case
141:             when mobile_phone_validation_failed = 1 then null
142:             when mobile_phone is null then null
143:             when length(mobile_phone) > 50 then null
144:             else cast(trim(mobile_phone) as varchar)
145:         end as mobile_phone,
146:         cast(trim(coalesce(name, '')) as varchar) as contact_name,
147:         cast(trim(coalesce(other_city, '')) as varchar) as other_city,
148:         cast(trim(coalesce(other_country, '')) as varchar) as other_country,
149:         case
150:             when other_phone is null then null
151:             when length(other_phone) > 50 then null
152:             else cast(trim(other_phone) as varchar)
153:         end as other_phone,
154:         cast(trim(coalesce(other_postal_code, '')) as varchar) as other_postal_code,
155:         cast(trim(coalesce(other_state, '')) as varchar) as other_state,
156:         cast(trim(coalesce(other_street, '')) as varchar) as other_street,
157:         case
158:             when owner_id_validation_failed = 1 then null
159:             else cast(owner_id as varchar)
160:         end as owner_id,
161:         case
162:             when phone_validation_failed = 1 then null
163:             when phone is null then null
164:             when length(phone) > 50 then null
165:             else cast(trim(phone) as varchar)
166:         end as phone,
167:         case
168:             when photo_url is not null and length(photo_url) > 500 then null
169:             else cast(trim(coalesce(photo_url, '')) as varchar)
170:         end as photo_url,
171:         case
172:             when reports_to_id_validation_failed = 1 then null
173:             else cast(reports_to_id as varchar)
174:         end as reports_to_id,
175:         cast(trim(coalesce(salutation, '')) as varchar) as salutation,
176:         cast(trim(coalesce(title, '')) as varchar) as title,
177: 
178:         -- Standard audit trail field per YAML spec
179:         current_timestamp as _dbt_loaded_at
180: 
181:     from validated
182:     where contact_id_validation_failed = 0
183:       and contact_name_validation_failed = 0
184: )
185: 
186: select *
187: from final
188: where not coalesce(is_deleted, false)
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 17/18 查看 raw 列和样例；event 55/56 查看本表 SQL；event 99 未解释 NULL→空串选择。通用“无效字段置空”不覆盖这里合法的缺失值默认。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/17.json`。
- event 18：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/18.json`。
- event 55：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/55.json`。
- event 56：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/56.json`。
- event 99：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：非必填字段 NULL

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE master_record_id IS NULL) missing_master FROM raw.contact
```


```json
{"columns":["n","missing_master"],"rows":[[3000,3000]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-018_stg_salesforce__contact.json](../023_reruns_impl-018_stg_salesforce__contact.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-24 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-24'","count":1}]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|30190|否|
|L1|3000|3000|3000|30190|否|
|L2|3000|3000|3000|30190|否|
|L3|3000|3000|3000|30190|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/baseline.sql`；SHA-256 `ef70d6320a10702b78c03bc75517e171cd4860f94cb9628adca4f9afa53b183e`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|30190|否|
|L1|3000|3000|3000|30190|否|
|L2|3000|3000|3000|30190|否|
|L3|3000|3000|3000|30190|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_assistant_name

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2667；按行优先、格次之排序。
共同控制后 SQL 第 3 行起、字符 offset 196 的唯一连续替换；其余字节不动。
替换前：
```sql
assistant_name as assistant_name
```

替换后：
```sql
coalesce(assistant_name, '') as assistant_name
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_assistant_name.sql`；SHA-256 `129c7eee5cb2e635e9353ecd02b0aa83148961d3ca82c9b37e4ead572ac8fa4b`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|27523|否|
|L1|3000|3000|3000|27523|否|
|L2|3000|3000|3000|27523|否|
|L3|3000|3000|3000|27523|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_department

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 1210；按行优先、格次之排序。
共同控制后 SQL 第 7 行起、字符 offset 566 的唯一连续替换；其余字节不动。
替换前：
```sql
department as department
```

替换后：
```sql
coalesce(department, '') as department
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_department.sql`；SHA-256 `e091c1744f5a930be21fee17386ff6073f52d228ed335042ba6915b119e4ab37`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|28980|否|
|L1|3000|3000|3000|28980|否|
|L2|3000|3000|3000|28980|否|
|L3|3000|3000|3000|28980|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_email_bounced_reason

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2955；按行优先、格次之排序。
共同控制后 SQL 第 11 行起、字符 offset 919 的唯一连续替换；其余字节不动。
替换前：
```sql
email_bounced_reason as email_bounced_reason
```

替换后：
```sql
coalesce(email_bounced_reason, '') as email_bounced_reason
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_email_bounced_reason.sql`；SHA-256 `b7726f6399d9abf29d20225dd40a351351c630140476d4b54f950985c770be22`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|27235|否|
|L1|3000|3000|3000|27235|否|
|L2|3000|3000|3000|27235|否|
|L3|3000|3000|3000|27235|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_fax

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2854；按行优先、格次之排序。
共同控制后 SQL 第 12 行起、字符 offset 971 的唯一连续替换；其余字节不动。
替换前：
```sql
fax as fax
```

替换后：
```sql
coalesce(fax, '') as fax
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_fax.sql`；SHA-256 `666cbfd1ab9a90cddd856795e45b270b0876b956d4aebefed3ba34a949138d95`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|27336|否|
|L1|3000|3000|3000|27336|否|
|L2|3000|3000|3000|27336|否|
|L3|3000|3000|3000|27336|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_lead_source

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 906；按行优先、格次之排序。
共同控制后 SQL 第 25 行起、字符 offset 1684 的唯一连续替换；其余字节不动。
替换前：
```sql
lead_source as lead_source
```

替换后：
```sql
coalesce(lead_source, '') as lead_source
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_lead_source.sql`；SHA-256 `f513c8e2bce77f7524a380ee89a90df35aa560c4d13853d90b156fb0b49d9ff7`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|29284|否|
|L1|3000|3000|3000|29284|否|
|L2|3000|3000|3000|29284|否|
|L3|3000|3000|3000|29284|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_master_record_id

判定：主因；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 3000；按行优先、格次之排序。
共同控制后 SQL 第 33 行起、字符 offset 2024 的唯一连续替换；其余字节不动。
替换前：
```sql
master_record_id as master_record_id
```

替换后：
```sql
coalesce(master_record_id, '') as master_record_id
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_master_record_id.sql`；SHA-256 `5fbf6a9464d0144f000b9387b2208e8ca78234a02b939abb23b756f61c8be608`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|27190|否|
|L1|3000|3000|3000|27190|否|
|L2|3000|3000|3000|27190|否|
|L3|3000|3000|3000|27190|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_other_city

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2407；按行优先、格次之排序。
共同控制后 SQL 第 36 行起、字符 offset 2214 的唯一连续替换；其余字节不动。
替换前：
```sql
other_city as other_city
```

替换后：
```sql
coalesce(other_city, '') as other_city
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_other_city.sql`；SHA-256 `2e9fcdc96fe491e9e227a9fe3d5ea10ecb6c077c8afe6fd04bc2c6f0a6ddf916`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|27783|否|
|L1|3000|3000|3000|27783|否|
|L2|3000|3000|3000|27783|否|
|L3|3000|3000|3000|27783|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_other_country

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2389；按行优先、格次之排序。
共同控制后 SQL 第 37 行起、字符 offset 2246 的唯一连续替换；其余字节不动。
替换前：
```sql
other_country as other_country
```

替换后：
```sql
coalesce(other_country, '') as other_country
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_other_country.sql`；SHA-256 `aa1b4c608f28a40eb41ccc3386d846ab5ffc22542d4c9e51e0071ab6c11584f8`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|27801|否|
|L1|3000|3000|3000|27801|否|
|L2|3000|3000|3000|27801|否|
|L3|3000|3000|3000|27801|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_other_postal_code

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2409；按行优先、格次之排序。
共同控制后 SQL 第 39 行起、字符 offset 2398 的唯一连续替换；其余字节不动。
替换前：
```sql
other_postal_code as other_postal_code
```

替换后：
```sql
coalesce(other_postal_code, '') as other_postal_code
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_other_postal_code.sql`；SHA-256 `93feb294d136b116e509cd38b583ad7105c8787bcde0a532d80ca542125c820d`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|27781|否|
|L1|3000|3000|3000|27781|否|
|L2|3000|3000|3000|27781|否|
|L3|3000|3000|3000|27781|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_other_state

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2430；按行优先、格次之排序。
共同控制后 SQL 第 40 行起、字符 offset 2444 的唯一连续替换；其余字节不动。
替换前：
```sql
other_state as other_state
```

替换后：
```sql
coalesce(other_state, '') as other_state
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_other_state.sql`；SHA-256 `694e586ca0e80076767ddbc6d02a1b868c7d658d838419677e5c81508eae243f`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|27760|否|
|L1|3000|3000|3000|27760|否|
|L2|3000|3000|3000|27760|否|
|L3|3000|3000|3000|27760|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_street":2421,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_other_street

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2421；按行优先、格次之排序。
共同控制后 SQL 第 41 行起、字符 offset 2478 的唯一连续替换；其余字节不动。
替换前：
```sql
other_street as other_street
```

替换后：
```sql
coalesce(other_street, '') as other_street
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_other_street.sql`；SHA-256 `6bba70821097282c5a9aba56c492ad59d2b8ebf223bc847067bfa5bda6a789b1`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|27769|否|
|L1|3000|3000|3000|27769|否|
|L2|3000|3000|3000|27769|否|
|L3|3000|3000|3000|27769|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"photo_url":2713,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"photo_url":2713,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"photo_url":2713,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"photo_url":2713,"salutation":1250,"title":579}`

#### null_empty_photo_url

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 2713；按行优先、格次之排序。
共同控制后 SQL 第 44 行起、字符 offset 2774 的唯一连续替换；其余字节不动。
替换前：
```sql
case when photo_url is null or length(trim(photo_url)) <= 500 then trim(photo_url) end as photo_url
```

替换后：
```sql
coalesce(case when photo_url is null or length(trim(photo_url)) <= 500 then trim(photo_url) end, '') as photo_url
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_photo_url.sql`；SHA-256 `fec3b756941061047b1535c7b6cb9d1779c9b627802dc6f56ed6920288fc8f89`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|27477|否|
|L1|3000|3000|3000|27477|否|
|L2|3000|3000|3000|27477|否|
|L3|3000|3000|3000|27477|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"salutation":1250,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"salutation":1250,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"salutation":1250,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"salutation":1250,"title":579}`

#### null_empty_salutation

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 1250；按行优先、格次之排序。
共同控制后 SQL 第 46 行起、字符 offset 3079 的唯一连续替换；其余字节不动。
替换前：
```sql
salutation as salutation
```

替换后：
```sql
coalesce(salutation, '') as salutation
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_salutation.sql`；SHA-256 `efc677872f804f556f08c7036bfa4001b8d6968a261e0abebafdbc4acc870854`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|28940|否|
|L1|3000|3000|3000|28940|否|
|L2|3000|3000|3000|28940|否|
|L3|3000|3000|3000|28940|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"title":579}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"title":579}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"title":579}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"title":579}`

#### null_empty_title

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 0、格 579；按行优先、格次之排序。
共同控制后 SQL 第 47 行起、字符 offset 3111 的唯一连续替换；其余字节不动。
替换前：
```sql
title as title
```

替换后：
```sql
coalesce(title, '') as title
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact/null_empty_title.sql`；SHA-256 `58a79bc23796d204d29c5e80e8463329663390f219aeb5190c1bb3855d996e47`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|29611|否|
|L1|3000|3000|3000|29611|否|
|L2|3000|3000|3000|29611|否|
|L3|3000|3000|3000|29611|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250}`
- L1：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250}`
- L2：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250}`
- L3：`{"assistant_name":2667,"department":1210,"email_bounced_reason":2955,"fax":2854,"lead_source":906,"master_record_id":3000,"other_city":2407,"other_country":2389,"other_postal_code":2409,"other_state":2430,"other_street":2421,"photo_url":2713,"salutation":1250}`

## 规则问题

无
