# impl-017 · greenhouse__application_history

用途：**全量**；层：`marts`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：直接诊断（无正改善的单点排序）。

最后区间使用运行时刻；共同固定到 gold 的时刻后 L2 全匹配，剩余 L0 为等价时长计算的浮点尾差。

参与因素：无。

标记：无。

023_history_clock 固定到 gold max(valid_until)；基线本身首次 L2匹配。未把运行时间变化当作单独错误点。

## 材料与比较口径

精简材料包：[023_impl-017_greenhouse__application_history.md](../023_packages/023_impl-017_greenhouse__application_history.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`；SHA-256 `f4a1c779c8359b7fd5d9c8cae9760669aceb5b35f661d0fab07d0bf376762e41`。
契约行 1509–1590：

```
1509:     - name: greenhouse__application_history
1510:       description: Application status-change intervals enriched with candidate/job attributes and per-interval activity counts
1511:       grain: One row per application_id per status-change interval (valid_from→valid_until)
1512:       source_models:
1513:       - staging.stg_greenhouse__application_history
1514:       - mart.greenhouse__application_enhanced
1515:       - staging.stg_greenhouse__job_stage
1516:       - staging.stg_greenhouse__activity
1517:       business_logic: '- Build status-change intervals from staging.stg_greenhouse__application_history: - For each application_id, order records by updated_at ascending. - Set valid_from to updated_at of the record. - Set valid_until to the next updated_at for the same application_id; if none, use the current timestamp at query time. - Intervals are half-open: include valid_from, exclude valid_until. - Enrich each interval: - Inner join mart.greenhouse__application_enhanced on application_id to add candidate and job attributes. - Left join staging.stg_greenhouse__job_stage on new_stage_id = job_stage_id to add the stage name; if no match, the name is NULL. - Compute days_in_stage as the exact seconds between valid_until and valid_from divided by 86,400; fractional days with no rounding. - Count activities per interval: - Left join staging.stg_greenhouse__activity on candidate_id only; counts include all activities for the candidate across applications. - For each interval, count activity rows where created_at (as a timestamp) is on or after valid_from and before valid_until. - Duplicates are counted; rows with NULL created_at do not count; if a candidate has no matching activities, the count is 0. - One row is produced per application_id per interval with all selected attributes; the last open interval is time-variant because valid_until uses the current timestamp.'
1518:       columns:
1519:       - name: application_id
1520:         data_type: BIGINT
1521:         description: Application identifier; multiple intervals may exist per application_id
1522:       - name: new_stage_id
1523:         data_type: BIGINT
1524:         description: Stage identifier assigned at this change
1525:       - name: new_status
1526:         data_type: VARCHAR
1527:         description: Status recorded at this change
1528:       - name: valid_from
1529:         data_type: TIMESTAMP
1530:         description: Inclusive lower bound of the interval; equals updated_at of the change
1531:       - name: valid_until
1532:         data_type: TIMESTAMP WITH TIME ZONE
1533:         description: Exclusive upper bound; next updated_at for the same application_id or the current timestamp if none
1534:       - name: new_stage
1535:         data_type: VARCHAR
1536:         description: Stage name joined by new_stage_id; may be NULL if not matched
1537:       - name: full_name
1538:         data_type: VARCHAR
1539:         description: Candidate full name
1540:       - name: current_status
1541:         data_type: VARCHAR
1542:         description: Current application status at model run time
1543:       - name: recruiter_name
1544:         data_type: VARCHAR
1545:         description: Primary recruiter name
1546:       - name: hiring_managers
1547:         data_type: VARCHAR
1548:         description: Hiring managers list as stored
1549:       - name: sourced_from
1550:         data_type: VARCHAR
1551:         description: Candidate source name
1552:       - name: sourced_from_type
1553:         data_type: VARCHAR
1554:         description: Candidate source type
1555:       - name: job_title
1556:         data_type: VARCHAR
1557:         description: Job title
1558:       - name: job_id
1559:         data_type: BIGINT
1560:         description: Job identifier
1561:       - name: candidate_id
1562:         data_type: BIGINT
1563:         description: Candidate identifier; join key for activity counts
1564:       - name: days_in_stage
1565:         data_type: DOUBLE
1566:         description: Fractional days in the interval computed from the exact seconds between bounds divided by 86,400; no rounding
1567:       - name: job_departments
1568:         data_type: VARCHAR
1569:         description: Departments associated with the job
1570:       - name: job_parent_departments
1571:         data_type: VARCHAR
1572:         description: Parent departments associated with the job
1573:       - name: job_offices
1574:         data_type: VARCHAR
1575:         description: Job offices
1576:       - name: candidate_gender
1577:         data_type: VARCHAR
1578:         description: Self-reported gender
1579:       - name: candidate_disability_status
1580:         data_type: VARCHAR
1581:         description: Self-reported disability status
1582:       - name: candidate_race
1583:         data_type: VARCHAR
1584:         description: Self-reported race/ethnicity
1585:       - name: candidate_veteran_status
1586:         data_type: VARCHAR
1587:         description: Self-reported veteran status
1588:       - name: count_activities_in_stage
1589:         data_type: HUGEINT
1590:         description: Number of activity rows for the same candidate with created_at in [valid_from, valid_until); duplicates counted; NULL created_at excluded; 0 when none
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/marts/greenhouse__application_history.sql`，SHA-256 `858519d3e09ec304887d05e672eb703614e6f876305085492523aa49a3a75c69`，行 1–43。

```
1: WITH status_intervals AS (
2:     SELECT application_id, new_stage_id, new_status, updated_at AS valid_from,
3:         LEAD(updated_at) OVER (PARTITION BY application_id ORDER BY updated_at) AS next_valid_from
4:     FROM staging.stg_greenhouse__application_history
5: ),
6: intervals AS (
7:     SELECT application_id, new_stage_id, new_status, valid_from,
8:         COALESCE(next_valid_from, CURRENT_TIMESTAMP)::TIMESTAMPTZ AS valid_until
9:     FROM status_intervals
10: )
11: SELECT
12:     history.application_id,
13:     history.new_stage_id,
14:     history.new_status,
15:     history.valid_from,
16:     history.valid_until,
17:     stage.name AS new_stage,
18:     app.candidate_full_name AS full_name,
19:     app.status AS current_status,
20:     app.recruiter_name,
21:     app.hiring_managers,
22:     app.sourced_from,
23:     app.sourced_from_type,
24:     app.job_title,
25:     app.job_id,
26:     app.candidate_id,
27:     DATE_DIFF('microsecond', history.valid_from, history.valid_until) / 86400000000.0 AS days_in_stage,
28:     app.job_departments,
29:     app.job_parent_departments,
30:     app.job_offices,
31:     app.candidate_gender,
32:     app.candidate_disability_status,
33:     app.candidate_race,
34:     app.candidate_veteran_status,
35:     COUNT(activity.activity_id)::HUGEINT AS count_activities_in_stage
36: FROM intervals AS history
37: INNER JOIN mart.greenhouse__application_enhanced AS app ON history.application_id = app.application_id
38: LEFT JOIN staging.stg_greenhouse__job_stage AS stage ON history.new_stage_id = stage.job_stage_id
39: LEFT JOIN staging.stg_greenhouse__activity AS activity
40:     ON app.candidate_id = activity.candidate_id
41:     AND activity.created_at >= history.valid_from
42:     AND activity.created_at < history.valid_until
43: GROUP BY ALL
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/sql/marts/greenhouse__application_history.sql`，SHA-256 `c1a91562b5befd7250c84e97bc1a72c85e3b5e95734a7baa3027dd4b50ded0aa`，行 1–123。

```
1: with application_history as (
2:     select 
3:         application_id,
4:         new_stage_id,
5:         new_status,
6:         updated_at as valid_from,
7:         coalesce(lead(updated_at) over (partition by application_id order by updated_at asc), 
8:             current_timestamp) as valid_until
9: 
10:     from staging.stg_greenhouse__application_history
11: ),
12: 
13: application as (
14:     select *
15:     from mart.greenhouse__application_enhanced
16: ),
17: 
18: job_stage as (
19:     select *
20:     from staging.stg_greenhouse__job_stage
21: ),
22: 
23: activity as (
24:     select *
25:     from staging.stg_greenhouse__activity
26: ),
27: 
28: join_application_history as (
29:     select 
30:         application_history.*,
31:         job_stage.name as new_stage,
32:         application.candidate_full_name as full_name,
33:         application.status as current_status,
34:         application.recruiter_name,
35:         application.hiring_managers,
36:         application.sourced_from, 
37:         application.sourced_from_type,
38:         application.job_title,
39:         application.job_id,
40:         application.candidate_id,
41:         application.job_departments,
42:         application.job_parent_departments,
43:         application.job_offices,
44:         application.candidate_gender,
45:         application.candidate_disability_status,
46:         application.candidate_race,
47:         application.candidate_veteran_status
48: 
49:     from application_history 
50:     join application
51:         on application_history.application_id = application.application_id
52:     left join job_stage
53:         on application_history.new_stage_id = job_stage.job_stage_id
54: ),
55: 
56: time_in_stages as (
57:     select 
58:         *,
59:         extract(epoch from (valid_until - valid_from)) / 86400 as days_in_stage
60: 
61:     from join_application_history
62: ),
63: 
64: activities_in_stages as (
65:     select 
66:         time_in_stages.application_id,
67:         time_in_stages.new_stage_id,
68:         time_in_stages.new_status,
69:         time_in_stages.valid_from,
70:         time_in_stages.valid_until,
71:         time_in_stages.new_stage,
72:         time_in_stages.full_name,
73:         time_in_stages.current_status,
74:         time_in_stages.recruiter_name,
75:         time_in_stages.hiring_managers,
76:         time_in_stages.sourced_from, 
77:         time_in_stages.sourced_from_type,
78:         time_in_stages.job_title,
79:         time_in_stages.job_id,
80:         time_in_stages.candidate_id,
81:         time_in_stages.days_in_stage,
82:         time_in_stages.job_departments,
83:         time_in_stages.job_parent_departments,
84:         time_in_stages.job_offices,
85:         time_in_stages.candidate_gender,
86:         time_in_stages.candidate_disability_status,
87:         time_in_stages.candidate_race,
88:         time_in_stages.candidate_veteran_status,
89: 
90:         sum(case when activity.created_at::timestamp >= valid_from and activity.created_at::timestamp < valid_until 
91:             then 1 else 0 end) as count_activities_in_stage
92: 
93:     from time_in_stages
94:     left join activity on activity.candidate_id = time_in_stages.candidate_id
95: 
96:     group by 
97:         time_in_stages.application_id,
98:         time_in_stages.new_stage_id,
99:         time_in_stages.new_status,
100:         time_in_stages.valid_from,
101:         time_in_stages.valid_until,
102:         time_in_stages.new_stage,
103:         time_in_stages.full_name,
104:         time_in_stages.current_status,
105:         time_in_stages.recruiter_name,
106:         time_in_stages.hiring_managers,
107:         time_in_stages.sourced_from, 
108:         time_in_stages.sourced_from_type,
109:         time_in_stages.job_title,
110:         time_in_stages.job_id,
111:         time_in_stages.candidate_id,
112:         time_in_stages.days_in_stage,
113:         time_in_stages.job_departments,
114:         time_in_stages.job_parent_departments,
115:         time_in_stages.job_offices,
116:         time_in_stages.candidate_gender,
117:         time_in_stages.candidate_disability_status,
118:         time_in_stages.candidate_race,
119:         time_in_stages.candidate_veteran_status
120: )
121: 
122: select *
123: from activities_in_stages
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 1 契约说明最后区间 time-variant；event 23 生成区间 SQL；event 53 未对本表时间选择作说明。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/1.json`。
- event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/23.json`。
- event 53：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/53.json`。
## 查询

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：时间边界

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/greenhouse.duckdb`。

```sql
SELECT min(valid_until),max(valid_until) FROM mart.greenhouse__application_history
```


```json
{"columns":["min(valid_until)","max(valid_until)"],"rows":[["2025-08-10 08:54:14.818931+08:00","2025-10-24 18:32:44.279463+08:00"]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-017_greenhouse__application_history.json](../023_reruns_impl-017_greenhouse__application_history.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/greenhouse.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-24 18:32:44.279463+08:00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-24'","count":0}]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|121|121|113|220|否|
|L1|121|121|113|220|否|
|L2|121|121|107|214|否|
|L3|121|121|107|214|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"days_in_stage":113,"valid_until":107}`
- L1：`{"days_in_stage":113,"valid_until":107}`
- L2：`{"days_in_stage":107,"valid_until":107}`
- L3：`{"days_in_stage":107,"valid_until":107}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-017_greenhouse__application_history/baseline.sql`；SHA-256 `3a7cac5b673a83c4da0aee907a877181a432726da8620e5b6cd9328e5e6bff44`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|121|121|40|40|否|
|L1|121|121|40|40|否|
|L2|121|121|0|0|是|
|L3|121|121|0|0|是|

整表首次匹配档位：L2。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"days_in_stage":40}`
- L1：`{"days_in_stage":40}`
- L2：`{}`
- L3：`{}`

## 规则问题

无
