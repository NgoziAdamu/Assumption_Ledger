# impl-018 · stg_salesforce__opportunity

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**A**；把握：高；主要错误点：null_empty_lead_source。

lead_source 与 type 两处可选字段 NULL/空串默认未由契约规定；前者行数减少更多。

参与因素：A：null_empty_type（行减少410，格减少595）。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-018_stg_salesforce__opportunity.md](../023_packages/023_impl-018_stg_salesforce__opportunity.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
契约行 287–405：

```
287:     - name: stg_salesforce__opportunity
288:       description: "Cleaned sales opportunity records with validated amounts, dates, and stage information"
289:       source_table: raw.opportunity
290:       columns:
291:         - name: account_id
292:           data_type: VARCHAR
293:           validation_rules:
294:             - rule: "account_id IS NULL OR account_id ~ '^[A-Za-z0-9]{15,18}$'"
295:               on_failure: nullify_field
296:             - rule: "account_id IS NULL OR account_id IN (SELECT id FROM raw.account)"
297:               on_failure: nullify_field
298:         - name: amount
299:           data_type: DECIMAL(18,2)
300:           validation_rules:
301:             - rule: "amount IS NULL OR amount >= 0"
302:               on_failure: nullify_field
303:             - rule: "amount IS NULL OR amount <= 999999999999.99"
304:               on_failure: nullify_field
305:         - name: campaign_id
306:           data_type: VARCHAR
307:         - name: close_date
308:           data_type: DATE
309:           validation_rules:
310:             - rule: "close_date IS NULL OR close_date >= DATE '1900-01-01'"
311:               on_failure: nullify_field
312:             - rule: "close_date IS NULL OR close_date <= CURRENT_DATE + INTERVAL '1 year'"
313:               on_failure: nullify_field
314:             - rule: "close_date IS NULL OR close_date >= created_date::DATE"
315:               on_failure: nullify_field
316:         - name: created_date
317:           data_type: TIMESTAMP
318:         - name: opportunity_description
319:           data_type: VARCHAR
320:         - name: expected_revenue
321:           data_type: DECIMAL(15,2)
322:         - name: fiscal
323:           data_type: VARCHAR
324:         - name: fiscal_quarter
325:           data_type: INTEGER
326:         - name: fiscal_year
327:           data_type: INTEGER
328:         - name: forecast_category
329:           data_type: VARCHAR
330:         - name: forecast_category_name
331:           data_type: VARCHAR
332:         - name: has_open_activity
333:           data_type: BOOLEAN
334:         - name: has_opportunity_line_item
335:           data_type: BOOLEAN
336:         - name: has_overdue_task
337:           data_type: BOOLEAN
338:         - name: opportunity_id
339:           data_type: VARCHAR
340:           constraints: [not_null]
341:           validation_rules:
342:             - rule: "opportunity_id ~ '^[A-Za-z0-9]{15,18}$'"
343:               on_failure: delete_row
344:         - name: is_closed
345:           data_type: BOOLEAN
346:         - name: is_deleted
347:           data_type: BOOLEAN
348:           validation_rules:
349:             - rule: "NOT COALESCE(is_deleted, false)"
350:               on_failure: delete_row
351:         - name: is_won
352:           data_type: BOOLEAN
353:         - name: last_activity_date
354:           data_type: DATE
355:         - name: last_referenced_date
356:           data_type: TIMESTAMP
357:         - name: last_viewed_date
358:           data_type: TIMESTAMP
359:         - name: lead_source
360:           data_type: VARCHAR
361:         - name: opportunity_name
362:           data_type: VARCHAR
363:           constraints: [not_null]
364:           validation_rules:
365:             - rule: "TRIM(opportunity_name) <> ''"
366:               on_failure: delete_row
367:             - rule: "LENGTH(TRIM(opportunity_name)) <= 255"
368:               on_failure: delete_row
369:         - name: next_step
370:           data_type: VARCHAR
371:         - name: owner_id
372:           data_type: VARCHAR
373:           validation_rules:
374:             - rule: "owner_id IS NULL OR owner_id ~ '^[A-Za-z0-9]{15,18}$'"
375:               on_failure: nullify_field
376:             - rule: "owner_id IS NULL OR owner_id IN (SELECT id FROM raw.user)"
377:               on_failure: nullify_field
378:         - name: probability
379:           data_type: DECIMAL(5,2)
380:           validation_rules:
381:             - rule: "probability IS NULL OR probability >= 0"
382:               on_failure: nullify_field
383:             - rule: "probability IS NULL OR probability <= 100"
384:               on_failure: nullify_field
385:         - name: record_type_id
386:           data_type: VARCHAR
387:         - name: stage_name
388:           data_type: VARCHAR
389:         - name: synced_quote_id
390:           data_type: VARCHAR
391:         - name: type
392:           data_type: VARCHAR
393:         - name: is_created_this_month
394:           data_type: BOOLEAN
395:         - name: is_created_this_quarter
396:           data_type: BOOLEAN
397:         - name: days_since_created
398:           data_type: INTEGER
399:         - name: days_to_close
400:           data_type: INTEGER
401:         - name: is_closed_this_month
402:           data_type: BOOLEAN
403:         - name: is_closed_this_quarter
404:           data_type: BOOLEAN
405:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity.sql`，SHA-256 `cef3f9d078bf1d7e079ae3afe43012f3c5a8bc7066ccc4dd9cbeb588b67657b7`，行 1–44。

```
1: select
2:       case when account_id is null or (regexp_matches(account_id, '^[A-Za-z0-9]{15,18}$') and account_id in (select id from raw.account)) then account_id else null end as account_id,
3:       case when try_cast(amount as DECIMAL(18,2)) >= 0 and try_cast(amount as DECIMAL(18,2)) <= 999999999999.99 then try_cast(amount as DECIMAL(18,2)) else null end as amount,
4:       campaign_id as campaign_id,
5:       case when try_cast(close_date as date) between date '1900-01-01' and current_date + interval 1 year and (created_date is null or try_cast(close_date as date) >= created_date::date) then try_cast(close_date as date) else null end as close_date,
6:       try_cast(created_date as TIMESTAMP) as created_date,
7:       description as opportunity_description,
8:       try_cast(expected_revenue as DECIMAL(15,2)) as expected_revenue,
9:       fiscal as fiscal,
10:       try_cast(fiscal_quarter as INTEGER) as fiscal_quarter,
11:       try_cast(fiscal_year as INTEGER) as fiscal_year,
12:       forecast_category as forecast_category,
13:       forecast_category_name as forecast_category_name,
14:       has_open_activity as has_open_activity,
15:       has_opportunity_line_item as has_opportunity_line_item,
16:       has_overdue_task as has_overdue_task,
17:       id as opportunity_id,
18:       is_closed as is_closed,
19:       is_deleted as is_deleted,
20:       is_won as is_won,
21:       try_cast(last_activity_date as DATE) as last_activity_date,
22:       try_cast(last_referenced_date as TIMESTAMP) as last_referenced_date,
23:       try_cast(last_viewed_date as TIMESTAMP) as last_viewed_date,
24:       lead_source as lead_source,
25:       name as opportunity_name,
26:       next_step as next_step,
27:       case when owner_id is null or (regexp_matches(owner_id, '^[A-Za-z0-9]{15,18}$') and owner_id in (select id from raw.user)) then owner_id else null end as owner_id,
28:       case when try_cast(probability as DECIMAL(5,2)) between 0 and 100 then try_cast(probability as DECIMAL(5,2)) else null end as probability,
29:       record_type_id as record_type_id,
30:       stage_name as stage_name,
31:       synced_quote_id as synced_quote_id,
32:       "type" as type,
33:       (created_date is not null and year(created_date)=year(current_date) and month(created_date)=month(current_date)) as is_created_this_month,
34:       (created_date is not null and year(created_date)=year(current_date) and quarter(created_date)=quarter(current_date)) as is_created_this_quarter,
35:       case when created_date is not null then date_diff('day', created_date::date, current_date)::integer end as days_since_created,
36:       case when close_date is not null and created_date is not null then date_diff('day', created_date::date, close_date::date)::integer end as days_to_close,
37:       (close_date is not null and year(close_date)=year(current_date) and month(close_date)=month(current_date)) as is_closed_this_month,
38:       (close_date is not null and year(close_date)=year(current_date) and quarter(close_date)=quarter(current_date)) as is_closed_this_quarter
39: from raw.opportunity
40: where id is not null
41:   and regexp_matches(id, '^[A-Za-z0-9]{15,18}$')
42:   and not coalesce(is_deleted, false)
43:   and trim(name) <> ''
44:   and length(trim(name)) <= 255
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity.sql`，SHA-256 `6cc01ba621d3b0e70950ca4354f00cd936d5a7ae5ecaebcf06c3d5668b09a6ec`，行 1–148。

```
1: with fields as (
2:     select *
3:     from raw.opportunity
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
15:         end as opportunity_id_validation_failed,
16: 
17:         -- Account ID foreign key validation
18:         case
19:             when account_id is not null and not (account_id ~ '^[A-Za-z0-9]{15,18}$') then 1
20:             when account_id is not null and account_id not in (select id from raw.account) then 1
21:             else 0
22:         end as account_id_validation_failed,
23: 
24:         -- Date validation - logical business rules (per YAML spec)
25:         case
26:             when close_date is null then 0 -- Close date can be null
27:             when close_date < '1900-01-01' then 1 -- Too old per YAML spec
28:             when close_date > current_date + interval '1 year' then 1 -- Too far future per YAML spec
29:             when close_date < created_date::DATE then 1 -- Logical violation per YAML spec
30:             else 0
31:         end as close_date_validation_failed,
32: 
33:         -- Amount validation - per YAML spec business rules
34:         case
35:             when amount is null then 0 -- Amount can be null
36:             when amount < 0 then 1 -- Negative amounts per YAML spec
37:             when amount > 999999999999.99 then 1 -- Exceeds reasonable limit per YAML spec
38:             else 0
39:         end as amount_validation_failed,
40: 
41:         -- Probability validation - should be 0-100, but handle null
42:         case
43:             when probability is null then 0 -- Probability can be null
44:             when probability < 0 then 1 -- Invalid probability per YAML spec
45:             when probability > 100 then 1 -- Invalid probability per YAML spec
46:             else 0
47:         end as probability_validation_failed,
48: 
49:         -- Owner ID foreign key validation
50:         case
51:             when owner_id is not null and not (owner_id ~ '^[A-Za-z0-9]{15,18}$') then 1
52:             when owner_id is not null and owner_id not in (select id from raw.user) then 1
53:             else 0
54:         end as owner_id_validation_failed,
55: 
56:         -- Opportunity name validation per YAML spec
57:         case
58:             when name is null then 1 -- Required field per YAML spec
59:             when trim(name) = '' then 1 -- Empty name not allowed per YAML spec
60:             when length(trim(name)) > 255 then 1 -- Length validation per YAML spec
61:             else 0
62:         end as opportunity_name_validation_failed
63: 
64:     from fields
65: ),
66: 
67: final as (
68:     select
69:         case
70:             when opportunity_id_validation_failed = 1 then null
71:             else cast(id as varchar)
72:         end as opportunity_id,
73:         case
74:             when account_id_validation_failed = 1 then null
75:             else cast(account_id as varchar)
76:         end as account_id,
77:         case
78:             when amount_validation_failed = 1 then null
79:             else cast(amount as decimal(18,2))  -- Per YAML spec decimal precision
80:         end as amount,
81:         cast(campaign_id as varchar) as campaign_id,
82:         case
83:             when close_date_validation_failed = 1 then null
84:             else cast(close_date as date)
85:         end as close_date,
86:         cast(created_date as timestamp) as created_date,
87:         cast(trim(coalesce(description, '')) as varchar) as opportunity_description,
88:         cast(expected_revenue as decimal(15,2)) as expected_revenue,
89:         cast(fiscal as varchar) as fiscal,
90:         cast(fiscal_quarter as integer) as fiscal_quarter,
91:         cast(fiscal_year as integer) as fiscal_year,
92:         cast(forecast_category as varchar) as forecast_category,
93:         cast(forecast_category_name as varchar) as forecast_category_name,
94:         cast(coalesce(has_open_activity, false) as boolean) as has_open_activity,
95:         cast(coalesce(has_opportunity_line_item, false) as boolean) as has_opportunity_line_item,
96:         cast(coalesce(has_overdue_task, false) as boolean) as has_overdue_task,
97:         cast(coalesce(is_closed, false) as boolean) as is_closed,
98:         cast(coalesce(is_deleted, false) as boolean) as is_deleted,
99:         cast(coalesce(is_won, false) as boolean) as is_won,
100:         cast(last_activity_date as date) as last_activity_date,
101:         cast(last_referenced_date as timestamp) as last_referenced_date,
102:         cast(last_viewed_date as timestamp) as last_viewed_date,
103:         cast(trim(coalesce(lead_source, '')) as varchar) as lead_source,
104:         case
105:             when opportunity_name_validation_failed = 1 then trim(name)
106:             else trim(name)
107:         end as opportunity_name,
108:         cast(trim(coalesce(next_step, '')) as varchar) as next_step,
109:         case
110:             when owner_id_validation_failed = 1 then null
111:             else cast(owner_id as varchar)
112:         end as owner_id,
113:         case
114:             when probability_validation_failed = 1 then null
115:             else cast(probability as decimal(5,2))  -- 100.00 format
116:         end as probability,
117:         cast(record_type_id as varchar) as record_type_id,
118:         cast(trim(coalesce(stage_name, '')) as varchar) as stage_name,
119:         cast(synced_quote_id as varchar) as synced_quote_id,
120:         cast(trim(coalesce(type, '')) as varchar) as type,
121: 
122:         -- Standard audit fields per YAML spec
123:         current_timestamp as _dbt_loaded_at
124: 
125:     from validated
126:     where opportunity_id_validation_failed = 0
127:       and opportunity_name_validation_failed = 0
128: ),
129: 
130: calculated as (
131:     select
132:         *,
133:         created_date >= date_trunc('month', current_timestamp) as is_created_this_month,
134:         created_date >= date_trunc('quarter', current_timestamp) as is_created_this_quarter,
135:         date_diff('day', created_date, current_timestamp) as days_since_created,
136:         case
137:             when close_date is null then null
138:             when created_date::DATE > close_date then null  -- Prevent negative days
139:             else date_diff('day', created_date::DATE, close_date)
140:         end as days_to_close,
141:         date_trunc('month', close_date) = date_trunc('month', current_timestamp) as is_closed_this_month,
142:         date_trunc('quarter', close_date) = date_trunc('quarter', current_timestamp) as is_closed_this_quarter
143:     from final
144: )
145: 
146: select *
147: from calculated
148: where not coalesce(is_deleted, false)
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 17/18 查看raw；event 45/46 查看SQL；event 99 未解释这两个字段缺失默认。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/17.json`。
- event 18：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/18.json`。
- event 45：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/45.json`。
- event 46：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/46.json`。
- event 99：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：缺失可选字段

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

```sql
SELECT count(*) FILTER(WHERE lead_source IS NULL) null_lead_source,count(*) FILTER(WHERE type IS NULL) null_type FROM raw.opportunity
```


```json
{"columns":["null_lead_source","null_type"],"rows":[[904,595]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-018_stg_salesforce__opportunity.json](../023_reruns_impl-018_stg_salesforce__opportunity.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-24 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-24'","count":10}]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|1314|1499|否|
|L1|3000|3000|1314|1499|否|
|L2|3000|3000|1314|1499|否|
|L3|3000|3000|1314|1499|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_source":904,"type":595}`
- L1：`{"lead_source":904,"type":595}`
- L2：`{"lead_source":904,"type":595}`
- L3：`{"lead_source":904,"type":595}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-018_stg_salesforce__opportunity/baseline.sql`；SHA-256 `3262b583c3862c3ade9a9b7e1c8eb00f37e90ec7134bca5389a2a222961a8607`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|1314|1499|否|
|L1|3000|3000|1314|1499|否|
|L2|3000|3000|1314|1499|否|
|L3|3000|3000|1314|1499|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_source":904,"type":595}`
- L1：`{"lead_source":904,"type":595}`
- L2：`{"lead_source":904,"type":595}`
- L3：`{"lead_source":904,"type":595}`

#### null_empty_lead_source

判定：主因；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 719、格 904；按行优先、格次之排序。
共同控制后 SQL 第 24 行起、字符 offset 1553 的唯一连续替换；其余字节不动。
替换前：
```sql
lead_source as lead_source
```

替换后：
```sql
coalesce(lead_source, '') as lead_source
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__opportunity/null_empty_lead_source.sql`；SHA-256 `1f48aba4ff3aa4267067620c78f719a9704641f8f93070f81d03f2a4a9885505`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|595|595|否|
|L1|3000|3000|595|595|否|
|L2|3000|3000|595|595|否|
|L3|3000|3000|595|595|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"type":595}`
- L1：`{"type":595}`
- L2：`{"type":595}`
- L3：`{"type":595}`

#### null_empty_type

判定：参与因素；类别候选 A。契约没有规定该列 NULL 与空串默认；两侧选择不同。

相对本轮基线减少行 410、格 595；按行优先、格次之排序。
共同控制后 SQL 第 32 行起、字符 offset 2078 的唯一连续替换；其余字节不动。
替换前：
```sql
"type" as type
```

替换后：
```sql
coalesce("type", '') as type
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__opportunity/null_empty_type.sql`；SHA-256 `84f7953d8ebb08ae6e0dfe931196da1bdb5b8328261eb41b414976d574d34e2e`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|904|904|否|
|L1|3000|3000|904|904|否|
|L2|3000|3000|904|904|否|
|L3|3000|3000|904|904|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"lead_source":904}`
- L1：`{"lead_source":904}`
- L2：`{"lead_source":904}`
- L3：`{"lead_source":904}`

## 规则问题

无
