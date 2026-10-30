# impl-017 | marts | greenhouse__job_enhanced | 差异：S1；日期 2025-10-24

## 契约完整原文

S3:1950–2042

```yaml
    - name: greenhouse__job_enhanced
      description: Enhanced job facts with applications, interviews, ratings, conversion rates, and time-derived fields per job
      grain: One row per job_id; if multiple distinct hiring team combinations exist for a job_id, one row per distinct combination
      source_models:
      - intermediate.int_greenhouse__job_info
      - intermediate.int_greenhouse__hiring_team
      - intermediate.int_greenhouse__application_info
      - intermediate.int_greenhouse__interview_scorecard
      business_logic: '- Start with all jobs from intermediate.int_greenhouse__job_info (job_id, name, status, requisition_id, created_at, departments, offices). - Build hiring_teams from intermediate.int_greenhouse__hiring_team by selecting job_id, hiring_managers, recruiters, sourcers and removing exact duplicate rows; if a job has multiple distinct combinations, all persist and create multiple output rows. - Build application_stats by job_id from intermediate.int_greenhouse__application_info: - Total applications: number of application rows. - Active applications: rows where status equals ''active''. - Hired applications: rows where status equals ''hired''. - Rejected applications: rows where status equals ''rejected''. - Prospect applications: rows where prospect equals the string ''True''. Notes: all comparisons are exact, case-sensitive. - Build interview_stats by joining interview scorecards to applications on application_id and aggregating by job_id: - Total interviews: number of scorecards for the job. - Completed interviews: scorecards where status equals ''completed''. - Average interviews per application: total scorecards divided by the count of distinct applications that have at least one scorecard; returns NULL if there are none. - Average job rating: mean of mapped recommendations (definitely_not→1, no→2, yes→3, strong_yes→4); other values and NULLs are excluded. - Rated applications count: number of scorecards with a non-NULL recommendation (counts scorecards, not distinct applications). - Rating completion rate: constant 1.0 for jobs with at least one scorecard. - Create the final set by left joining jobs to hiring_teams, application_stats, and interview_stats on job_id: - Pass through job and hiring team fields. - Replace NULLs in all count fields with 0; keep averages and rating_completion_rate as returned (they will be NULL when no scorecards exist for the job). - Conversion rates (percent, 0–100, no rounding): - Application to interview: if total applications > 0, total interviews divided by total applications times 100; otherwise 0. - Interview to hire: if total interviews > 0, hired applications divided by total interviews times 100; otherwise 0. - Overall conversion: if total applications > 0, hired applications divided by total applications times 100; otherwise 0. - Time fields: created_year and created_month from created_at; days_since_created is the number of days between the current date and created_at and may be fractional.'
      columns:
      - name: job_id
        data_type: BIGINT
        description: Unique job identifier; determines row granularity
        tests:
        - not_null
      - name: name
        data_type: VARCHAR
        description: Job name from job_info
      - name: status
        data_type: VARCHAR
        description: Job status from job_info
      - name: requisition_id
        data_type: BIGINT
        description: Requisition identifier; may be NULL
      - name: created_at
        data_type: TIMESTAMP
        description: Job creation timestamp; used to derive year, month, and days_since_created
      - name: departments
        data_type: VARCHAR
        description: Departments from job_info
      - name: offices
        data_type: VARCHAR
        description: Offices from job_info
      - name: hiring_managers
        data_type: VARCHAR
        description: Hiring managers from hiring_team; NULL if no team row
      - name: recruiters
        data_type: VARCHAR
        description: Recruiters from hiring_team; NULL if no team row
      - name: sourcers
        data_type: VARCHAR
        description: Sourcers from hiring_team; NULL if no team row
      - name: count_total_applications
        data_type: BIGINT
        description: Total applications for the job; NULL replaced with 0
      - name: count_active_applications
        data_type: BIGINT
        description: Applications with status='active'; NULL replaced with 0
      - name: count_hired_applications
        data_type: BIGINT
        description: Applications with status='hired'; NULL replaced with 0
      - name: count_rejected_applications
        data_type: BIGINT
        description: Applications with status='rejected'; NULL replaced with 0
      - name: count_prospect_applications
        data_type: BIGINT
        description: Applications where prospect equals 'True' (case-sensitive); NULL replaced with 0
      - name: count_total_interviews
        data_type: BIGINT
        description: Number of interview scorecards for the job; NULL replaced with 0
      - name: count_completed_interviews
        data_type: BIGINT
        description: Scorecards with status='completed'; NULL replaced with 0
      - name: avg_interviews_per_application
        data_type: DOUBLE
        description: Total scorecards divided by distinct applications with a scorecard; NULL if none; no rounding
      - name: avg_job_rating
        data_type: DOUBLE
        description: Average mapped recommendation (definitely_not=1, no=2, yes=3, strong_yes=4); excludes other values and NULLs; NULL if none
      - name: count_rated_applications
        data_type: BIGINT
        description: Scorecards with a non-NULL recommendation (counts scorecards, not distinct applications); NULL replaced with 0
      - name: rating_completion_rate
        data_type: DECIMAL(2,1)
        description: Constant 1.0 when at least one scorecard exists for the job; NULL otherwise
      - name: application_to_interview_rate
        data_type: DOUBLE
        description: 'Percent: total interviews / total applications × 100; returns 0 if total applications is 0 or missing; no rounding'
      - name: interview_to_hire_rate
        data_type: DOUBLE
        description: 'Percent: hired applications / total interviews × 100; returns 0 if total interviews is 0 or missing; no rounding'
      - name: overall_conversion_rate
        data_type: DOUBLE
        description: 'Percent: hired applications / total applications × 100; returns 0 if total applications is 0 or missing; no rounding'
      - name: created_year
        data_type: BIGINT
        description: Year extracted from created_at
      - name: created_month
        data_type: BIGINT
        description: Month (1–12) extracted from created_at
      - name: days_since_created
        data_type: DOUBLE
        description: Days between the current date and created_at; updates daily and may be fractional
```

## agent 最终 SQL

S4

```sql
WITH hiring_teams AS (
    SELECT DISTINCT job_id, hiring_managers, recruiters, sourcers
    FROM intermediate.int_greenhouse__hiring_team
),
application_stats AS (
    SELECT job_id,
        COUNT(*)::BIGINT AS count_total_applications,
        COUNT(*) FILTER (WHERE status = 'active')::BIGINT AS count_active_applications,
        COUNT(*) FILTER (WHERE status = 'hired')::BIGINT AS count_hired_applications,
        COUNT(*) FILTER (WHERE status = 'rejected')::BIGINT AS count_rejected_applications,
        COUNT(*) FILTER (WHERE prospect::VARCHAR = 'True')::BIGINT AS count_prospect_applications
    FROM intermediate.int_greenhouse__application_info
    WHERE job_id IS NOT NULL
    GROUP BY job_id
),
interview_stats AS (
    SELECT app.job_id,
        COUNT(*)::BIGINT AS count_total_interviews,
        COUNT(*) FILTER (WHERE interview.status = 'completed')::BIGINT AS count_completed_interviews,
        COUNT(DISTINCT app.application_id) AS application_count,
        AVG(CASE sc.overall_recommendation WHEN 'definitely_not' THEN 1 WHEN 'no' THEN 2 WHEN 'yes' THEN 3 WHEN 'strong_yes' THEN 4 END) AS avg_job_rating,
        COUNT(*) FILTER (WHERE sc.overall_recommendation IS NOT NULL)::BIGINT AS count_rated_applications
    FROM intermediate.int_greenhouse__application_info AS app
    INNER JOIN intermediate.int_greenhouse__interview_scorecard AS interview ON app.application_id = interview.application_id
    LEFT JOIN staging.stg_greenhouse__scorecard AS sc ON interview.scorecard_id = sc.scorecard_id
    GROUP BY app.job_id
),
job_metrics AS (
    SELECT j.*, ht.hiring_managers, ht.recruiters, ht.sourcers,
        COALESCE(a.count_total_applications, 0)::BIGINT AS count_total_applications,
        COALESCE(a.count_active_applications, 0)::BIGINT AS count_active_applications,
        COALESCE(a.count_hired_applications, 0)::BIGINT AS count_hired_applications,
        COALESCE(a.count_rejected_applications, 0)::BIGINT AS count_rejected_applications,
        COALESCE(a.count_prospect_applications, 0)::BIGINT AS count_prospect_applications,
        COALESCE(i.count_total_interviews, 0)::BIGINT AS count_total_interviews,
        COALESCE(i.count_completed_interviews, 0)::BIGINT AS count_completed_interviews,
        i.application_count, i.avg_job_rating,
        COALESCE(i.count_rated_applications, 0)::BIGINT AS count_rated_applications,
        CASE WHEN i.count_total_interviews > 0 THEN 1.0::DECIMAL(2,1) END AS rating_completion_rate
    FROM intermediate.int_greenhouse__job_info AS j
    LEFT JOIN hiring_teams AS ht ON j.job_id = ht.job_id
    LEFT JOIN application_stats AS a ON j.job_id = a.job_id
    LEFT JOIN interview_stats AS i ON j.job_id = i.job_id
)
SELECT job_id, name, status, requisition_id, created_at, departments, offices,
    hiring_managers, recruiters, sourcers,
    count_total_applications, count_active_applications, count_hired_applications, count_rejected_applications, count_prospect_applications,
    count_total_interviews, count_completed_interviews,
    count_total_interviews::DOUBLE / NULLIF(application_count, 0) AS avg_interviews_per_application,
    avg_job_rating, count_rated_applications, rating_completion_rate,
    CASE WHEN count_total_applications > 0 THEN count_total_interviews * 100.0 / count_total_applications ELSE 0.0 END AS application_to_interview_rate,
    CASE WHEN count_total_interviews > 0 THEN count_hired_applications * 100.0 / count_total_interviews ELSE 0.0 END AS interview_to_hire_rate,
    CASE WHEN count_total_applications > 0 THEN count_hired_applications * 100.0 / count_total_applications ELSE 0.0 END AS overall_conversion_rate,
    YEAR(created_at)::BIGINT AS created_year, MONTH(created_at)::BIGINT AS created_month,
    DATE_DIFF('microsecond', created_at, CURRENT_TIMESTAMP) / 86400000000.0 AS days_since_created
FROM job_metrics
```

## gold SQL（仅供定位差异）

S5

```sql
-- Purpose: Job effectiveness analysis and recruiting team workload
-- Dependencies: intermediate layer tables
-- Business Owner: HR Analytics Team

with job_base as (
    select * from intermediate.int_greenhouse__job_info
),

hiring_teams as (
    select 
        job_id,
        hiring_managers,
        recruiters,
        sourcers
    from intermediate.int_greenhouse__hiring_team
    group by job_id, hiring_managers, recruiters, sourcers
),

application_stats as (
    select 
        job_id,
        count(*) as count_total_applications,
        count(case when status = 'active' then 1 end) as count_active_applications,
        count(case when status = 'hired' then 1 end) as count_hired_applications,
        count(case when status = 'rejected' then 1 end) as count_rejected_applications,
        count(case when prospect = 'True' then 1 end) as count_prospect_applications
    from intermediate.int_greenhouse__application_info
    group by job_id
),

interview_stats as (
    select 
        ai.job_id,
        count(*) as count_total_interviews,
        count(case when isc.status = 'completed' then 1 end) as count_completed_interviews,
        count(*) * 1.0 / nullif(count(distinct isc.application_id), 0) as avg_interviews_per_application,
        avg(case when isc.overall_recommendation = 'definitely_not' then 1
                 when isc.overall_recommendation = 'no' then 2
                 when isc.overall_recommendation = 'yes' then 3
                 when isc.overall_recommendation = 'strong_yes' then 4
                 else null end) as avg_job_rating,
        count(case when isc.overall_recommendation is not null then 1 end) as count_rated_applications,
        1.0 as rating_completion_rate
    from intermediate.int_greenhouse__interview_scorecard isc
    join intermediate.int_greenhouse__application_info ai on isc.application_id = ai.application_id
    group by ai.job_id
),

enhanced_jobs as (
    select
        -- Job basics
        jb.job_id,
        jb.name,
        jb.status,
        jb.requisition_id,
        jb.created_at,
        
        -- Organizational info
        jb.departments,
        jb.offices,
        ht.hiring_managers,
        ht.recruiters,
        ht.sourcers,
        
        -- Application statistics
        coalesce(aps.count_total_applications, 0) as count_total_applications,
        coalesce(aps.count_active_applications, 0) as count_active_applications,
        coalesce(aps.count_hired_applications, 0) as count_hired_applications,
        coalesce(aps.count_rejected_applications, 0) as count_rejected_applications,
        coalesce(aps.count_prospect_applications, 0) as count_prospect_applications,
        
        -- Interview statistics
        coalesce(ins.count_total_interviews, 0) as count_total_interviews,
        coalesce(ins.count_completed_interviews, 0) as count_completed_interviews,
        ins.avg_interviews_per_application,
        
        -- Rating statistics
        ins.avg_job_rating,
        coalesce(ins.count_rated_applications, 0) as count_rated_applications,
        ins.rating_completion_rate,
        
        -- Conversion rates
        case when aps.count_total_applications > 0 
             then ins.count_total_interviews * 100.0 / aps.count_total_applications
             else 0 end as application_to_interview_rate,
        case when ins.count_total_interviews > 0 
             then aps.count_hired_applications * 100.0 / ins.count_total_interviews
             else 0 end as interview_to_hire_rate,
        case when aps.count_total_applications > 0 
             then aps.count_hired_applications * 100.0 / aps.count_total_applications
             else 0 end as overall_conversion_rate,
        
        -- Time dimensions
        extract(year from jb.created_at) as created_year,
        extract(month from jb.created_at) as created_month,
        extract(epoch from (current_date - jb.created_at)) / 86400 as days_since_created
        
    from job_base jb
    left join hiring_teams ht on jb.job_id = ht.job_id
    left join application_stats aps on jb.job_id = aps.job_id
    left join interview_stats ins on jb.job_id = ins.job_id
)

select * from enhanced_jobs
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1200 | 1200 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"job_id":"1006"}</code> |
| K2 | <code>{"job_id":"1022"}</code> |
| K3 | <code>{"job_id":"1036"}</code> |
| K4 | <code>{"job_id":"1078"}</code> |
| K5 | <code>{"job_id":"1095"}</code> |
| K6 | <code>{"job_id":"1"}</code> |
| K7 | <code>{"job_id":"10"}</code> |
| K8 | <code>{"job_id":"100"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| job_id | 0 | 0 | 0 | BIGINT | BIGINT |
| application_to_interview_rate | 93 | 93 | 93 | DOUBLE | DOUBLE |
| count_active_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| count_completed_interviews | 0 | 0 | 0 | BIGINT | BIGINT |
| count_hired_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| count_prospect_applications | 40 | 40 | 40 | BIGINT | BIGINT |
| count_rated_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| count_rejected_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| count_total_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| count_total_interviews | 0 | 0 | 0 | BIGINT | BIGINT |
| created_month | 0 | 0 | 0 | BIGINT | BIGINT |
| created_year | 0 | 0 | 0 | BIGINT | BIGINT |
| days_since_created | 1200 | 1200 | 1200 | DOUBLE | DOUBLE |
| departments | 0 | 0 | 0 | VARCHAR | VARCHAR |
| hiring_managers | 0 | 0 | 0 | VARCHAR | VARCHAR |
| interview_to_hire_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| offices | 0 | 0 | 0 | VARCHAR | VARCHAR |
| overall_conversion_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| recruiters | 0 | 0 | 0 | VARCHAR | VARCHAR |
| requisition_id | 0 | 0 | 0 | BIGINT | BIGINT |
| sourcers | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 0 | 0 | 0 | VARCHAR | VARCHAR |

application_to_interview_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | null |
| K2 | 0.0 | null |
| K3 | 0.0 | null |

count_prospect_applications 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0 | 1 |
| K4 | 0 | 1 |
| K5 | 0 | 1 |

days_since_created 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K6 | 48.695335648148145 | 48.362002314814816 |
| K7 | 48.69532407407407 | 48.361990740740744 |
| K8 | 48.696168981481485 | 48.36283564814815 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"sourcers","table_rows":1200}]</code> |
| A3_constant_nonnull_column | <code>3列；[{"column":"count_prospect_applications","value":"0"},{"column":"created_year","value":"2025"},{"column":"created_month","value":"9"}]</code> |
| B7_read_not_specified | <code>["staging.stg_greenhouse__scorecard"]</code> |
| C9_agent_runtime_text | <code>S4:55 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:96 current_date；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:1958 current date；命中数=2</code> |

## 轨迹索引（不放输出原文）

本题事件总数：55；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 12604 | true | false |
| 19 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>I=Path('sql/intermediate'); M=Path('sql/marts')<br>def w(d,n,s): (d/f'{n}.sql').write_text(s.strip()+"\n")<br>w(I,'int_greenhouse__user_emails', '''WITH ema</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br>w(M,'greenhouse__interview_enhanced', '''SELECT<br>    interview.*,<br>    js.name AS job_stage,<br>    app.candidate_full_name AS candidate_name,<br>    app.current_job_stage AS applica</code> | 0 | false | false |
| 23 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br>w(M,'greenhouse__application_history', '''WITH status_intervals AS (<br>    SELECT application_id, new_stage_id, new_status, updated_at AS valid_from,<br>        LEAD(updated_at) O</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br>w(M,'greenhouse__diversity_metrics', '''WITH application_demographics AS (<br>    SELECT YEAR(a.applied_at)::BIGINT AS application_year,<br>        QUARTER(a.applied_at)::BIGINT AS</code> | 0 | false | false |
| 27 | run | <code>python run.py &gt; /tmp/run.log 2&gt;&amp;1; tail -100 /tmp/run.log</code> | 5955 | true | false |
| 29 | run | <code>grep -E 'Executing: staging&#124;ERROR - ✗ staging&#124;staging\.' /tmp/run.log &#124; head -90</code> | 7093 | false | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text(); start=s.index('    SELECT\n')+len('    SELECT\n'); end=s.index('\n        ROW_NUMBER()',start)<br> b</code> | 3337 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('greenhouse.duckdb',read_only=True)<br>for s in ['staging','intermediate','mart']:<br> print('\n',s)<br> for (t,) in c.execute(f"select table_name from informatio</code> | 1807 | true | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
w(M,'greenhouse__job_enhanced', '''WITH hiring_teams AS (
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-017.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/marts/greenhouse__job_enhanced.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/sql/marts/greenhouse__job_enhanced.sql`
- S6: `records/006_contract_impl-017.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/result.md`
- S10: `data/023_packages_work/023_impl-017_greenhouse__job_enhanced/023_impl-017_greenhouse__job_enhanced.json`
- S11: `data/011_agent_alignment/impl-017/greenhouse__job_enhanced_2025-10-24.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/greenhouse.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions`
