# impl-017 · greenhouse__job_enhanced

用途：**全量**；层：`marts`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**C**；把握：高；主要错误点：days_clock。

days_since_created 使用 current_timestamp 而契约指定 current_date；另有 prospect 预转 VARCHAR 与 gold 未补零比率的差异。

参与因素：C：prospect_cast（行减少0，格减少40）；O：ratio_zero_vs_null（行减少0，格减少93）。

标记：无。

prospect_cast 为C参与因素；ratio_zero_vs_null 为O参与因素：契约要求count先默认0，gold直接使用NULL原聚合。

## 材料与比较口径

精简材料包：[023_impl-017_greenhouse__job_enhanced.md](../023_packages/023_impl-017_greenhouse__job_enhanced.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`；SHA-256 `f4a1c779c8359b7fd5d9c8cae9760669aceb5b35f661d0fab07d0bf376762e41`。
契约行 1950–2042：

```
1950:     - name: greenhouse__job_enhanced
1951:       description: Enhanced job facts with applications, interviews, ratings, conversion rates, and time-derived fields per job
1952:       grain: One row per job_id; if multiple distinct hiring team combinations exist for a job_id, one row per distinct combination
1953:       source_models:
1954:       - intermediate.int_greenhouse__job_info
1955:       - intermediate.int_greenhouse__hiring_team
1956:       - intermediate.int_greenhouse__application_info
1957:       - intermediate.int_greenhouse__interview_scorecard
1958:       business_logic: '- Start with all jobs from intermediate.int_greenhouse__job_info (job_id, name, status, requisition_id, created_at, departments, offices). - Build hiring_teams from intermediate.int_greenhouse__hiring_team by selecting job_id, hiring_managers, recruiters, sourcers and removing exact duplicate rows; if a job has multiple distinct combinations, all persist and create multiple output rows. - Build application_stats by job_id from intermediate.int_greenhouse__application_info: - Total applications: number of application rows. - Active applications: rows where status equals ''active''. - Hired applications: rows where status equals ''hired''. - Rejected applications: rows where status equals ''rejected''. - Prospect applications: rows where prospect equals the string ''True''. Notes: all comparisons are exact, case-sensitive. - Build interview_stats by joining interview scorecards to applications on application_id and aggregating by job_id: - Total interviews: number of scorecards for the job. - Completed interviews: scorecards where status equals ''completed''. - Average interviews per application: total scorecards divided by the count of distinct applications that have at least one scorecard; returns NULL if there are none. - Average job rating: mean of mapped recommendations (definitely_not→1, no→2, yes→3, strong_yes→4); other values and NULLs are excluded. - Rated applications count: number of scorecards with a non-NULL recommendation (counts scorecards, not distinct applications). - Rating completion rate: constant 1.0 for jobs with at least one scorecard. - Create the final set by left joining jobs to hiring_teams, application_stats, and interview_stats on job_id: - Pass through job and hiring team fields. - Replace NULLs in all count fields with 0; keep averages and rating_completion_rate as returned (they will be NULL when no scorecards exist for the job). - Conversion rates (percent, 0–100, no rounding): - Application to interview: if total applications > 0, total interviews divided by total applications times 100; otherwise 0. - Interview to hire: if total interviews > 0, hired applications divided by total interviews times 100; otherwise 0. - Overall conversion: if total applications > 0, hired applications divided by total applications times 100; otherwise 0. - Time fields: created_year and created_month from created_at; days_since_created is the number of days between the current date and created_at and may be fractional.'
1959:       columns:
1960:       - name: job_id
1961:         data_type: BIGINT
1962:         description: Unique job identifier; determines row granularity
1963:         tests:
1964:         - not_null
1965:       - name: name
1966:         data_type: VARCHAR
1967:         description: Job name from job_info
1968:       - name: status
1969:         data_type: VARCHAR
1970:         description: Job status from job_info
1971:       - name: requisition_id
1972:         data_type: BIGINT
1973:         description: Requisition identifier; may be NULL
1974:       - name: created_at
1975:         data_type: TIMESTAMP
1976:         description: Job creation timestamp; used to derive year, month, and days_since_created
1977:       - name: departments
1978:         data_type: VARCHAR
1979:         description: Departments from job_info
1980:       - name: offices
1981:         data_type: VARCHAR
1982:         description: Offices from job_info
1983:       - name: hiring_managers
1984:         data_type: VARCHAR
1985:         description: Hiring managers from hiring_team; NULL if no team row
1986:       - name: recruiters
1987:         data_type: VARCHAR
1988:         description: Recruiters from hiring_team; NULL if no team row
1989:       - name: sourcers
1990:         data_type: VARCHAR
1991:         description: Sourcers from hiring_team; NULL if no team row
1992:       - name: count_total_applications
1993:         data_type: BIGINT
1994:         description: Total applications for the job; NULL replaced with 0
1995:       - name: count_active_applications
1996:         data_type: BIGINT
1997:         description: Applications with status='active'; NULL replaced with 0
1998:       - name: count_hired_applications
1999:         data_type: BIGINT
2000:         description: Applications with status='hired'; NULL replaced with 0
2001:       - name: count_rejected_applications
2002:         data_type: BIGINT
2003:         description: Applications with status='rejected'; NULL replaced with 0
2004:       - name: count_prospect_applications
2005:         data_type: BIGINT
2006:         description: Applications where prospect equals 'True' (case-sensitive); NULL replaced with 0
2007:       - name: count_total_interviews
2008:         data_type: BIGINT
2009:         description: Number of interview scorecards for the job; NULL replaced with 0
2010:       - name: count_completed_interviews
2011:         data_type: BIGINT
2012:         description: Scorecards with status='completed'; NULL replaced with 0
2013:       - name: avg_interviews_per_application
2014:         data_type: DOUBLE
2015:         description: Total scorecards divided by distinct applications with a scorecard; NULL if none; no rounding
2016:       - name: avg_job_rating
2017:         data_type: DOUBLE
2018:         description: Average mapped recommendation (definitely_not=1, no=2, yes=3, strong_yes=4); excludes other values and NULLs; NULL if none
2019:       - name: count_rated_applications
2020:         data_type: BIGINT
2021:         description: Scorecards with a non-NULL recommendation (counts scorecards, not distinct applications); NULL replaced with 0
2022:       - name: rating_completion_rate
2023:         data_type: DECIMAL(2,1)
2024:         description: Constant 1.0 when at least one scorecard exists for the job; NULL otherwise
2025:       - name: application_to_interview_rate
2026:         data_type: DOUBLE
2027:         description: 'Percent: total interviews / total applications × 100; returns 0 if total applications is 0 or missing; no rounding'
2028:       - name: interview_to_hire_rate
2029:         data_type: DOUBLE
2030:         description: 'Percent: hired applications / total interviews × 100; returns 0 if total interviews is 0 or missing; no rounding'
2031:       - name: overall_conversion_rate
2032:         data_type: DOUBLE
2033:         description: 'Percent: hired applications / total applications × 100; returns 0 if total applications is 0 or missing; no rounding'
2034:       - name: created_year
2035:         data_type: BIGINT
2036:         description: Year extracted from created_at
2037:       - name: created_month
2038:         data_type: BIGINT
2039:         description: Month (1–12) extracted from created_at
2040:       - name: days_since_created
2041:         data_type: DOUBLE
2042:         description: Days between the current date and created_at; updates daily and may be fractional
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/marts/greenhouse__job_enhanced.sql`，SHA-256 `3c26acfd5d6935a3967b3f8c69e5a8c264f706120026a39dc4f1400b5aa602fc`，行 1–56。

```
1: WITH hiring_teams AS (
2:     SELECT DISTINCT job_id, hiring_managers, recruiters, sourcers
3:     FROM intermediate.int_greenhouse__hiring_team
4: ),
5: application_stats AS (
6:     SELECT job_id,
7:         COUNT(*)::BIGINT AS count_total_applications,
8:         COUNT(*) FILTER (WHERE status = 'active')::BIGINT AS count_active_applications,
9:         COUNT(*) FILTER (WHERE status = 'hired')::BIGINT AS count_hired_applications,
10:         COUNT(*) FILTER (WHERE status = 'rejected')::BIGINT AS count_rejected_applications,
11:         COUNT(*) FILTER (WHERE prospect::VARCHAR = 'True')::BIGINT AS count_prospect_applications
12:     FROM intermediate.int_greenhouse__application_info
13:     WHERE job_id IS NOT NULL
14:     GROUP BY job_id
15: ),
16: interview_stats AS (
17:     SELECT app.job_id,
18:         COUNT(*)::BIGINT AS count_total_interviews,
19:         COUNT(*) FILTER (WHERE interview.status = 'completed')::BIGINT AS count_completed_interviews,
20:         COUNT(DISTINCT app.application_id) AS application_count,
21:         AVG(CASE sc.overall_recommendation WHEN 'definitely_not' THEN 1 WHEN 'no' THEN 2 WHEN 'yes' THEN 3 WHEN 'strong_yes' THEN 4 END) AS avg_job_rating,
22:         COUNT(*) FILTER (WHERE sc.overall_recommendation IS NOT NULL)::BIGINT AS count_rated_applications
23:     FROM intermediate.int_greenhouse__application_info AS app
24:     INNER JOIN intermediate.int_greenhouse__interview_scorecard AS interview ON app.application_id = interview.application_id
25:     LEFT JOIN staging.stg_greenhouse__scorecard AS sc ON interview.scorecard_id = sc.scorecard_id
26:     GROUP BY app.job_id
27: ),
28: job_metrics AS (
29:     SELECT j.*, ht.hiring_managers, ht.recruiters, ht.sourcers,
30:         COALESCE(a.count_total_applications, 0)::BIGINT AS count_total_applications,
31:         COALESCE(a.count_active_applications, 0)::BIGINT AS count_active_applications,
32:         COALESCE(a.count_hired_applications, 0)::BIGINT AS count_hired_applications,
33:         COALESCE(a.count_rejected_applications, 0)::BIGINT AS count_rejected_applications,
34:         COALESCE(a.count_prospect_applications, 0)::BIGINT AS count_prospect_applications,
35:         COALESCE(i.count_total_interviews, 0)::BIGINT AS count_total_interviews,
36:         COALESCE(i.count_completed_interviews, 0)::BIGINT AS count_completed_interviews,
37:         i.application_count, i.avg_job_rating,
38:         COALESCE(i.count_rated_applications, 0)::BIGINT AS count_rated_applications,
39:         CASE WHEN i.count_total_interviews > 0 THEN 1.0::DECIMAL(2,1) END AS rating_completion_rate
40:     FROM intermediate.int_greenhouse__job_info AS j
41:     LEFT JOIN hiring_teams AS ht ON j.job_id = ht.job_id
42:     LEFT JOIN application_stats AS a ON j.job_id = a.job_id
43:     LEFT JOIN interview_stats AS i ON j.job_id = i.job_id
44: )
45: SELECT job_id, name, status, requisition_id, created_at, departments, offices,
46:     hiring_managers, recruiters, sourcers,
47:     count_total_applications, count_active_applications, count_hired_applications, count_rejected_applications, count_prospect_applications,
48:     count_total_interviews, count_completed_interviews,
49:     count_total_interviews::DOUBLE / NULLIF(application_count, 0) AS avg_interviews_per_application,
50:     avg_job_rating, count_rated_applications, rating_completion_rate,
51:     CASE WHEN count_total_applications > 0 THEN count_total_interviews * 100.0 / count_total_applications ELSE 0.0 END AS application_to_interview_rate,
52:     CASE WHEN count_total_interviews > 0 THEN count_hired_applications * 100.0 / count_total_interviews ELSE 0.0 END AS interview_to_hire_rate,
53:     CASE WHEN count_total_applications > 0 THEN count_hired_applications * 100.0 / count_total_applications ELSE 0.0 END AS overall_conversion_rate,
54:     YEAR(created_at)::BIGINT AS created_year, MONTH(created_at)::BIGINT AS created_month,
55:     DATE_DIFF('microsecond', created_at, CURRENT_TIMESTAMP) / 86400000000.0 AS days_since_created
56: FROM job_metrics
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/sql/marts/greenhouse__job_enhanced.sql`，SHA-256 `6418ae6aa8b6b669287eb046f368d0f0e51a837907137ba6afd4c924fbe0bc45`，行 1–104。

```
1: -- Purpose: Job effectiveness analysis and recruiting team workload
2: -- Dependencies: intermediate layer tables
3: -- Business Owner: HR Analytics Team
4: 
5: with job_base as (
6:     select * from intermediate.int_greenhouse__job_info
7: ),
8: 
9: hiring_teams as (
10:     select 
11:         job_id,
12:         hiring_managers,
13:         recruiters,
14:         sourcers
15:     from intermediate.int_greenhouse__hiring_team
16:     group by job_id, hiring_managers, recruiters, sourcers
17: ),
18: 
19: application_stats as (
20:     select 
21:         job_id,
22:         count(*) as count_total_applications,
23:         count(case when status = 'active' then 1 end) as count_active_applications,
24:         count(case when status = 'hired' then 1 end) as count_hired_applications,
25:         count(case when status = 'rejected' then 1 end) as count_rejected_applications,
26:         count(case when prospect = 'True' then 1 end) as count_prospect_applications
27:     from intermediate.int_greenhouse__application_info
28:     group by job_id
29: ),
30: 
31: interview_stats as (
32:     select 
33:         ai.job_id,
34:         count(*) as count_total_interviews,
35:         count(case when isc.status = 'completed' then 1 end) as count_completed_interviews,
36:         count(*) * 1.0 / nullif(count(distinct isc.application_id), 0) as avg_interviews_per_application,
37:         avg(case when isc.overall_recommendation = 'definitely_not' then 1
38:                  when isc.overall_recommendation = 'no' then 2
39:                  when isc.overall_recommendation = 'yes' then 3
40:                  when isc.overall_recommendation = 'strong_yes' then 4
41:                  else null end) as avg_job_rating,
42:         count(case when isc.overall_recommendation is not null then 1 end) as count_rated_applications,
43:         1.0 as rating_completion_rate
44:     from intermediate.int_greenhouse__interview_scorecard isc
45:     join intermediate.int_greenhouse__application_info ai on isc.application_id = ai.application_id
46:     group by ai.job_id
47: ),
48: 
49: enhanced_jobs as (
50:     select
51:         -- Job basics
52:         jb.job_id,
53:         jb.name,
54:         jb.status,
55:         jb.requisition_id,
56:         jb.created_at,
57:         
58:         -- Organizational info
59:         jb.departments,
60:         jb.offices,
61:         ht.hiring_managers,
62:         ht.recruiters,
63:         ht.sourcers,
64:         
65:         -- Application statistics
66:         coalesce(aps.count_total_applications, 0) as count_total_applications,
67:         coalesce(aps.count_active_applications, 0) as count_active_applications,
68:         coalesce(aps.count_hired_applications, 0) as count_hired_applications,
69:         coalesce(aps.count_rejected_applications, 0) as count_rejected_applications,
70:         coalesce(aps.count_prospect_applications, 0) as count_prospect_applications,
71:         
72:         -- Interview statistics
73:         coalesce(ins.count_total_interviews, 0) as count_total_interviews,
74:         coalesce(ins.count_completed_interviews, 0) as count_completed_interviews,
75:         ins.avg_interviews_per_application,
76:         
77:         -- Rating statistics
78:         ins.avg_job_rating,
79:         coalesce(ins.count_rated_applications, 0) as count_rated_applications,
80:         ins.rating_completion_rate,
81:         
82:         -- Conversion rates
83:         case when aps.count_total_applications > 0 
84:              then ins.count_total_interviews * 100.0 / aps.count_total_applications
85:              else 0 end as application_to_interview_rate,
86:         case when ins.count_total_interviews > 0 
87:              then aps.count_hired_applications * 100.0 / ins.count_total_interviews
88:              else 0 end as interview_to_hire_rate,
89:         case when aps.count_total_applications > 0 
90:              then aps.count_hired_applications * 100.0 / aps.count_total_applications
91:              else 0 end as overall_conversion_rate,
92:         
93:         -- Time dimensions
94:         extract(year from jb.created_at) as created_year,
95:         extract(month from jb.created_at) as created_month,
96:         extract(epoch from (current_date - jb.created_at)) / 86400 as days_since_created
97:         
98:     from job_base jb
99:     left join hiring_teams ht on jb.job_id = ht.job_id
100:     left join application_stats aps on jb.job_id = aps.job_id
101:     left join interview_stats ins on jb.job_id = ins.job_id
102: )
103: 
104: select * from enhanced_jobs
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 1 契约明确 current date 和 prospect 比较原式；event 21/23 生成模型；event 53 的层级实施清单不计通用策略。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/1.json`。
- event 21：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/21.json`。
- event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/23.json`。
- event 53：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/53.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：prospect 类型比较

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/greenhouse.duckdb`。

```sql
SELECT typeof(prospect),count(*),count(*) FILTER(WHERE prospect='True'),count(*) FILTER(WHERE prospect::VARCHAR='True') FROM intermediate.int_greenhouse__application_info GROUP BY 1
```


```json
{"columns":["typeof(prospect)","count_star()","count_star() FILTER (WHERE (prospect = 'True'))","count_star() FILTER (WHERE (CAST(prospect AS VARCHAR) = 'True'))"],"rows":[["BOOLEAN",668,209,0]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-017_greenhouse__job_enhanced.json](../023_reruns_impl-017_greenhouse__job_enhanced.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/greenhouse.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-24 00:00:00+00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-24'","count":0}]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|1333|否|
|L1|1200|1200|1200|1333|否|
|L2|1200|1200|1200|1333|否|
|L3|1200|1200|1200|1333|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`
- L1：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`
- L2：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`
- L3：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-017_greenhouse__job_enhanced/baseline.sql`；SHA-256 `57405b67279700c0cb485b0449cd98e5fd58ddd4f58e944824a814f3099d4937`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|1333|否|
|L1|1200|1200|1200|1333|否|
|L2|1200|1200|1200|1333|否|
|L3|1200|1200|1200|1333|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`
- L1：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`
- L2：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`
- L3：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`

#### prospect_cast

判定：参与因素；类别候选 C。契约给出了可执行的 prospect = True 字符串比较，agent 预先转 VARCHAR 改变 BOOLEAN 比较。

相对本轮基线减少行 0、格 40；按行优先、格次之排序。
共同控制后 SQL 第 11 行起、字符 offset 535 的唯一连续替换；其余字节不动。
替换前：
```sql
prospect::VARCHAR = 'True'
```

替换后：
```sql
prospect = 'True'
```

私有 SQL：`data/023_work/impl-017_greenhouse__job_enhanced/prospect_cast.sql`；SHA-256 `b7c3ddd515cc81f60eab14baf576c55a30edf5bb8d27bf7cf88fe5350eab1a98`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|1293|否|
|L1|1200|1200|1200|1293|否|
|L2|1200|1200|1200|1293|否|
|L3|1200|1200|1200|1293|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"application_to_interview_rate":93,"days_since_created":1200}`
- L1：`{"application_to_interview_rate":93,"days_since_created":1200}`
- L2：`{"application_to_interview_rate":93,"days_since_created":1200}`
- L3：`{"application_to_interview_rate":93,"days_since_created":1200}`

#### days_clock

判定：主因；类别候选 C。契约要求 current date，agent 使用 current timestamp。

相对本轮基线减少行 1098、格 1200；按行优先、格次之排序。
共同控制后 SQL 第 55 行起、字符 offset 3728 的唯一连续替换；其余字节不动。
替换前：
```sql
DATE_DIFF('microsecond', created_at, TIMESTAMPTZ '2025-10-24 00:00:00+00')
```

替换后：
```sql
DATE_DIFF('microsecond', created_at, DATE '2025-10-24')
```

私有 SQL：`data/023_work/impl-017_greenhouse__job_enhanced/days_clock.sql`；SHA-256 `9a3ae16f58951bd1a3be025b9925f5929e505335669822eab97779312b24ac6e`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|102|133|否|
|L1|1200|1200|102|133|否|
|L2|1200|1200|102|133|否|
|L3|1200|1200|102|133|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"application_to_interview_rate":93,"count_prospect_applications":40}`
- L1：`{"application_to_interview_rate":93,"count_prospect_applications":40}`
- L2：`{"application_to_interview_rate":93,"count_prospect_applications":40}`
- L3：`{"application_to_interview_rate":93,"count_prospect_applications":40}`
### 补充轮：[023_supplement_reruns_impl-017_greenhouse__job_enhanced.json](../023_supplement_reruns_impl-017_greenhouse__job_enhanced.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/greenhouse.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-24 00:00:00+00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-24'","count":0}]`。

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_supplement_work/impl-017_greenhouse__job_enhanced/baseline.sql`；SHA-256 `57405b67279700c0cb485b0449cd98e5fd58ddd4f58e944824a814f3099d4937`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|1333|否|
|L1|1200|1200|1200|1333|否|
|L2|1200|1200|1200|1333|否|
|L3|1200|1200|1200|1333|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`
- L1：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`
- L2：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`
- L3：`{"application_to_interview_rate":93,"count_prospect_applications":40,"days_since_created":1200}`

#### ratio_zero_vs_null

判定：参与因素；类别候选 O。契约先将 count 默认0；gold 用未补零的原始聚合生成 NULL 比率。

相对本轮基线减少行 0、格 93；按行优先、格次之排序。
共同控制后 SQL 第 51 行起、字符 offset 3236 的唯一连续替换；其余字节不动。
替换前：
```sql
count_total_interviews * 100.0 / count_total_applications
```

替换后：
```sql
nullif(count_total_interviews,0) * 100.0 / count_total_applications
```

私有 SQL：`data/023_supplement_work/impl-017_greenhouse__job_enhanced/ratio_zero_vs_null.sql`；SHA-256 `51f7ffa298d1852236c520c82e63bb6d791768ba39c7c836dc71bdf5e98d3350`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|1240|否|
|L1|1200|1200|1200|1240|否|
|L2|1200|1200|1200|1240|否|
|L3|1200|1200|1200|1240|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"count_prospect_applications":40,"days_since_created":1200}`
- L1：`{"count_prospect_applications":40,"days_since_created":1200}`
- L2：`{"count_prospect_applications":40,"days_since_created":1200}`
- L3：`{"count_prospect_applications":40,"days_since_created":1200}`

## 规则问题

无
