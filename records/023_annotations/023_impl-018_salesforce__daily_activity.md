# impl-018 · salesforce__daily_activity

用途：**全量**；层：`marts`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**C**；把握：高；主要错误点：won_amount_null。

对 Won 金额全 NULL 的8个日分组也补0，契约只对无 Won 的分组规定0。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-018_salesforce__daily_activity.md](../023_packages/023_impl-018_salesforce__daily_activity.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
契约行 2425–2474：

```
2425:     - name: salesforce__daily_activity
2426:       description: Daily summary by date_day of leads created/converted, tasks/events counts, and opportunity creation/closure metrics with amounts rounded to 0 decimals.
2427:       grain: One row per date_day
2428:       source_models:
2429:       - staging.stg_salesforce__lead
2430:       - staging.stg_salesforce__task
2431:       - staging.stg_salesforce__event
2432:       - staging.stg_salesforce__opportunity
2433:       - intermediate.int_salesforce__date_spine
2434:       business_logic: '- Start from the date spine (one row per date_day); this drives the output. - Tasks: group tasks by the calendar day of activity_date; tasks_completed is the number of non-null task records on that day; tasks with a null activity_date do not contribute and will not join; no additional filters. - Events: define each event’s activity day as the calendar day of activity_date, otherwise the calendar day of activity_date_time; if both are null the event is excluded; events_completed is the number of non-null event records on that day. - Leads created: group leads by the calendar day of created_date; leads_created is the number of non-null lead records on that day; rows with a null created_date are excluded. - Leads converted: restrict to leads where is_converted is true; group by the calendar day of converted_date; leads_converted is the number of non-null lead records on that day; rows with a null converted_date are excluded. - Opportunities base: for each opportunity derive created_day from created_date and close_day from close_date; set status as: • Won when is_won is true • Lost when is_won is false and is_closed is true • Pipeline when not closed and forecast_category (case-insensitive) is one of pipeline, forecast, bestcase • Other otherwise Amount may be null and is used in sums. - Opportunities created (by created_day): • opportunities_created: number of non-null opportunity records • opportunities_created_amount: sum of amount rounded to 0 decimals; sums ignore null amounts and are null when all amounts are null - Opportunities closed (by close_day): • opportunities_won: number of opportunities with status Won; zero when there are close_day records but none Won; null when no close_day records • opportunities_won_amount: sum of amounts for status Won rounded to 0 decimals; zero when there are close_day records but none Won; null when no close_day records • opportunities_lost: number of opportunities with status Lost; zero when there are close_day records but none Lost; null when no close_day records • opportunities_lost_amount: sum of amounts for status Lost rounded to 0 decimals; null when there are close_day records but none Lost; null when no close_day records • pipeline_amount: sum of amounts for status Pipeline rounded to 0 decimals; null when there are close_day records but none Pipeline; null when no close_day records - Output: left join each aggregate to the date spine on date_day; if a date has no matching aggregate row, the corresponding fields remain null; no defaulting to zero beyond the rules above.'
2435:       columns:
2436:       - name: date_day
2437:         data_type: DATE
2438:         description: Calendar date from the date spine and join key; exactly one row per date_day.
2439:         tests:
2440:         - not_null
2441:         - unique
2442:       - name: leads_created
2443:         data_type: BIGINT
2444:         description: Number of leads created on date_day based on created_date; only non-null lead records counted; null when no leads match that day.
2445:       - name: leads_converted
2446:         data_type: BIGINT
2447:         description: Number of leads with is_converted=true whose converted_date falls on date_day; only non-null lead records counted; null when none match that day.
2448:       - name: tasks_completed
2449:         data_type: BIGINT
2450:         description: Number of tasks whose activity_date falls on date_day; tasks with null activity_date are excluded; null when none match that day.
2451:       - name: events_completed
2452:         data_type: BIGINT
2453:         description: Number of events by day using activity_date when present else activity_date_time; events with both timestamps null are excluded; null when none match that day.
2454:       - name: opportunities_created
2455:         data_type: BIGINT
2456:         description: Number of opportunities created on date_day (by created_date); only non-null records counted; null when none match that day.
2457:       - name: opportunities_created_amount
2458:         data_type: DECIMAL(38,0)
2459:         description: Sum of amounts for opportunities created on date_day, rounded to 0 decimals; null when all amounts are null or no records match that day.
2460:       - name: opportunities_won
2461:         data_type: BIGINT
2462:         description: Number of opportunities with close_date on date_day and status Won; zero when close_date records exist but none Won; null when no close_date records.
2463:       - name: opportunities_won_amount
2464:         data_type: DECIMAL(38,0)
2465:         description: Sum of amounts for opportunities with close_date on date_day and status Won, rounded to 0 decimals; zero when close_date records exist but none Won; null when no close_date records.
2466:       - name: opportunities_lost
2467:         data_type: BIGINT
2468:         description: Number of opportunities with close_date on date_day and status Lost; zero when close_date records exist but none Lost; null when no close_date records.
2469:       - name: opportunities_lost_amount
2470:         data_type: DECIMAL(38,0)
2471:         description: Sum of amounts for opportunities with close_date on date_day and status Lost, rounded to 0 decimals; null when close_date records exist but none Lost or when no close_date records.
2472:       - name: pipeline_amount
2473:         data_type: DECIMAL(38,0)
2474:         description: Sum of amounts for opportunities with close_date on date_day and status Pipeline, rounded to 0 decimals; null when close_date records exist but none Pipeline or when no close_date records.
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__daily_activity.sql`，SHA-256 `c0b35be7574e7d0188bdc41738e1eec1183fd92be26051c5d28c50da6252f6c9`，行 1–37。

```
1: with task_daily as (
2:  select activity_date::date as date_day,count(*) as tasks_completed from staging.stg_salesforce__task where activity_date is not null group by 1
3: ),
4: event_daily as (
5:  select coalesce(activity_date::date,activity_date_time::date) as date_day,count(*) as events_completed
6:  from staging.stg_salesforce__event where coalesce(activity_date,activity_date_time) is not null group by 1
7: ),
8: lead_created as (
9:  select created_date::date as date_day,count(*) as leads_created from staging.stg_salesforce__lead where created_date is not null group by 1
10: ),
11: lead_converted as (
12:  select converted_date::date as date_day,count(*) as leads_converted from staging.stg_salesforce__lead
13:  where is_converted is true and converted_date is not null group by 1
14: ),
15: opportunity_base as (
16:  select *,created_date::date as created_day,close_date::date as close_day,
17:  case when is_won is true then 'Won' when is_won is false and is_closed is true then 'Lost'
18:  when is_closed is false and lower(forecast_category) in ('pipeline','forecast','bestcase') then 'Pipeline' else 'Other' end as deal_status
19:  from staging.stg_salesforce__opportunity
20: ),
21: opp_created as (
22:  select created_day as date_day,count(*) as opportunities_created,round(sum(amount)) as opportunities_created_amount
23:  from opportunity_base where created_day is not null group by 1
24: ),
25: opp_closed as (
26:  select close_day as date_day,count(*) filter(where deal_status='Won') as opportunities_won,
27:  coalesce(round(sum(amount) filter(where deal_status='Won')),0) as opportunities_won_amount,
28:  count(*) filter(where deal_status='Lost') as opportunities_lost,
29:  round(sum(amount) filter(where deal_status='Lost')) as opportunities_lost_amount,
30:  round(sum(amount) filter(where deal_status='Pipeline')) as pipeline_amount
31:  from opportunity_base where close_day is not null group by 1
32: )
33: select d.date_day,lc.leads_created,lcv.leads_converted,t.tasks_completed,e.events_completed,oc.opportunities_created,oc.opportunities_created_amount,
34:  oh.opportunities_won,oh.opportunities_won_amount,oh.opportunities_lost,oh.opportunities_lost_amount,oh.pipeline_amount
35: from intermediate.int_salesforce__date_spine d left join lead_created lc using(date_day)
36: left join lead_converted lcv using(date_day) left join task_daily t using(date_day) left join event_daily e using(date_day)
37: left join opp_created oc using(date_day) left join opp_closed oh using(date_day)
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/marts/salesforce__daily_activity.sql`，SHA-256 `f5e944e349141d7450a16d1c419fb76778b1945aaf4cc79694e3aa697260a835`，行 1–108。

```
1: with date_spine as (
2:     select 
3:         date_day
4:     from intermediate.int_salesforce__date_spine
5: ),
6: 
7: task as (
8:     select 
9:         date_trunc('day', activity_date) as activity_date,
10:         count(task_id) as tasks_completed
11:     from staging.stg_salesforce__task
12:     group by 1
13: ), 
14: 
15: salesforce_event as (
16:     select 
17:         coalesce(date_trunc('day', activity_date), date_trunc('day', activity_date_time)) as activity_date,
18:         count(event_id) as events_completed
19:     from staging.stg_salesforce__event
20:     group by 1
21: ), 
22: 
23: salesforce_lead as (
24:     select 
25:         date_trunc('day', created_date) as created_date,
26:         count(lead_id) as leads_created 
27:     from staging.stg_salesforce__lead
28:     group by 1
29: ), 
30: 
31: salesforce_converted_lead as (
32:     select 
33:         date_trunc('day', converted_date) as converted_date,
34:         count(lead_id) as leads_converted
35:     from staging.stg_salesforce__lead
36:     where is_converted
37:     group by 1
38: ), 
39: 
40: opportunity as (
41:     select 
42:         opportunity_id,
43:         date_trunc('day', created_date) as created_date,
44:         account_id,
45:         date_trunc('day', close_date) as close_date,
46:         is_closed,
47:         is_deleted,
48:         is_won,
49:         owner_id, 
50:         stage_name,
51:         type,
52:         amount,
53:         case
54:             when is_won then 'Won'
55:             when not is_won and is_closed then 'Lost'
56:             when not is_closed and lower(forecast_category) in ('pipeline','forecast','bestcase') then 'Pipeline'
57:             else 'Other'
58:         end as status
59:     from staging.stg_salesforce__opportunity
60: ),
61: 
62: opportunities_created as (
63:     select
64:         created_date,
65:         count(opportunity_id) as opportunities_created,
66:         round(sum(amount)) as opportunities_created_amount
67:     from opportunity
68:     group by 1
69: ),
70: 
71: opportunities_closed as (
72:     select
73:         close_date,
74:         count(case when status = 'Won' then opportunity_id else null end) as opportunities_won,
75:         round(sum(case when status = 'Won' then amount else 0 end)) as opportunities_won_amount,
76:         count(case when status = 'Lost' then opportunity_id else null end) as opportunities_lost,
77:         round(sum(case when status = 'Lost' then amount else null end)) as opportunities_lost_amount,
78:         round(sum(case when status = 'Pipeline' then amount else null end)) as pipeline_amount
79:     from opportunity
80:     group by 1
81: )
82: 
83: select
84:     date_spine.date_day,
85:     salesforce_lead.leads_created,
86:     salesforce_converted_lead.leads_converted,
87:     task.tasks_completed,
88:     salesforce_event.events_completed,
89:     opportunities_created.opportunities_created,
90:     opportunities_created.opportunities_created_amount,
91:     opportunities_closed.opportunities_won,
92:     opportunities_closed.opportunities_won_amount,
93:     opportunities_closed.opportunities_lost,
94:     opportunities_closed.opportunities_lost_amount,
95:     opportunities_closed.pipeline_amount
96: from date_spine
97: left join salesforce_lead
98:     on date_spine.date_day = salesforce_lead.created_date
99: left join salesforce_converted_lead
100:     on date_spine.date_day = salesforce_converted_lead.converted_date
101: left join task
102:     on date_spine.date_day = task.activity_date
103: left join salesforce_event
104:     on date_spine.date_day = salesforce_event.activity_date
105: left join opportunities_created
106:     on date_spine.date_day = opportunities_created.created_date
107: left join opportunities_closed
108:     on date_spine.date_day = opportunities_closed.close_date
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 1 已给 Won/no-Won 的NULL语义；event 31 生成日活动 SQL；event 99 未说明此聚合边界。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json`。
- event 31：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/31.json`。
- event 99：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json`。
## 查询

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：Won 全 NULL 分组

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`。

```sql
SELECT count(*) FROM (SELECT close_date::DATE d FROM staging.stg_salesforce__opportunity GROUP BY 1 HAVING count(*) FILTER(WHERE is_won)=count(*) AND count(amount)=0)
```


```json
{"columns":["count_star()"],"rows":[[8]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-018_salesforce__daily_activity.json](../023_reruns_impl-018_salesforce__daily_activity.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2124|2124|8|8|否|
|L1|2124|2124|8|8|否|
|L2|2124|2124|8|8|否|
|L3|2124|2124|8|8|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"opportunities_won_amount":8}`
- L1：`{"opportunities_won_amount":8}`
- L2：`{"opportunities_won_amount":8}`
- L3：`{"opportunities_won_amount":8}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-018_salesforce__daily_activity/baseline.sql`；SHA-256 `c0b35be7574e7d0188bdc41738e1eec1183fd92be26051c5d28c50da6252f6c9`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2124|2124|8|8|否|
|L1|2124|2124|8|8|否|
|L2|2124|2124|8|8|否|
|L3|2124|2124|8|8|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"opportunities_won_amount":8}`
- L1：`{"opportunities_won_amount":8}`
- L2：`{"opportunities_won_amount":8}`
- L3：`{"opportunities_won_amount":8}`

#### won_amount_null

判定：主因；类别候选 C。只应在无 Won 记录时为零；有 Won 且 amount 全 NULL 时保留 NULL。

相对本轮基线减少行 8、格 8；按行优先、格次之排序。
共同控制后 SQL 第 27 行起、字符 offset 1444 的唯一连续替换；其余字节不动。
替换前：
```sql
coalesce(round(sum(amount) filter(where deal_status='Won')),0)
```

替换后：
```sql
round(sum(case when deal_status='Won' then amount else 0 end))
```

私有 SQL：`data/023_work/impl-018_salesforce__daily_activity/won_amount_null.sql`；SHA-256 `7d2a930f1189d764727008e7e356833bb783b3bcd706431fc924e311cf2baa8b`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2124|2124|0|0|是|
|L1|2124|2124|0|0|是|
|L2|2124|2124|0|0|是|
|L3|2124|2124|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 规则问题

无
