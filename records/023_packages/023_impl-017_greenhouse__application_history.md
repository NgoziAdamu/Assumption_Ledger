# impl-017 | marts | greenhouse__application_history | 差异：S1；日期 原记录

## 契约完整原文

S3:1509–1590

```yaml
    - name: greenhouse__application_history
      description: Application status-change intervals enriched with candidate/job attributes and per-interval activity counts
      grain: One row per application_id per status-change interval (valid_from→valid_until)
      source_models:
      - staging.stg_greenhouse__application_history
      - mart.greenhouse__application_enhanced
      - staging.stg_greenhouse__job_stage
      - staging.stg_greenhouse__activity
      business_logic: '- Build status-change intervals from staging.stg_greenhouse__application_history: - For each application_id, order records by updated_at ascending. - Set valid_from to updated_at of the record. - Set valid_until to the next updated_at for the same application_id; if none, use the current timestamp at query time. - Intervals are half-open: include valid_from, exclude valid_until. - Enrich each interval: - Inner join mart.greenhouse__application_enhanced on application_id to add candidate and job attributes. - Left join staging.stg_greenhouse__job_stage on new_stage_id = job_stage_id to add the stage name; if no match, the name is NULL. - Compute days_in_stage as the exact seconds between valid_until and valid_from divided by 86,400; fractional days with no rounding. - Count activities per interval: - Left join staging.stg_greenhouse__activity on candidate_id only; counts include all activities for the candidate across applications. - For each interval, count activity rows where created_at (as a timestamp) is on or after valid_from and before valid_until. - Duplicates are counted; rows with NULL created_at do not count; if a candidate has no matching activities, the count is 0. - One row is produced per application_id per interval with all selected attributes; the last open interval is time-variant because valid_until uses the current timestamp.'
      columns:
      - name: application_id
        data_type: BIGINT
        description: Application identifier; multiple intervals may exist per application_id
      - name: new_stage_id
        data_type: BIGINT
        description: Stage identifier assigned at this change
      - name: new_status
        data_type: VARCHAR
        description: Status recorded at this change
      - name: valid_from
        data_type: TIMESTAMP
        description: Inclusive lower bound of the interval; equals updated_at of the change
      - name: valid_until
        data_type: TIMESTAMP WITH TIME ZONE
        description: Exclusive upper bound; next updated_at for the same application_id or the current timestamp if none
      - name: new_stage
        data_type: VARCHAR
        description: Stage name joined by new_stage_id; may be NULL if not matched
      - name: full_name
        data_type: VARCHAR
        description: Candidate full name
      - name: current_status
        data_type: VARCHAR
        description: Current application status at model run time
      - name: recruiter_name
        data_type: VARCHAR
        description: Primary recruiter name
      - name: hiring_managers
        data_type: VARCHAR
        description: Hiring managers list as stored
      - name: sourced_from
        data_type: VARCHAR
        description: Candidate source name
      - name: sourced_from_type
        data_type: VARCHAR
        description: Candidate source type
      - name: job_title
        data_type: VARCHAR
        description: Job title
      - name: job_id
        data_type: BIGINT
        description: Job identifier
      - name: candidate_id
        data_type: BIGINT
        description: Candidate identifier; join key for activity counts
      - name: days_in_stage
        data_type: DOUBLE
        description: Fractional days in the interval computed from the exact seconds between bounds divided by 86,400; no rounding
      - name: job_departments
        data_type: VARCHAR
        description: Departments associated with the job
      - name: job_parent_departments
        data_type: VARCHAR
        description: Parent departments associated with the job
      - name: job_offices
        data_type: VARCHAR
        description: Job offices
      - name: candidate_gender
        data_type: VARCHAR
        description: Self-reported gender
      - name: candidate_disability_status
        data_type: VARCHAR
        description: Self-reported disability status
      - name: candidate_race
        data_type: VARCHAR
        description: Self-reported race/ethnicity
      - name: candidate_veteran_status
        data_type: VARCHAR
        description: Self-reported veteran status
      - name: count_activities_in_stage
        data_type: HUGEINT
        description: Number of activity rows for the same candidate with created_at in [valid_from, valid_until); duplicates counted; NULL created_at excluded; 0 when none
```

## agent 最终 SQL

S4

```sql
WITH status_intervals AS (
    SELECT application_id, new_stage_id, new_status, updated_at AS valid_from,
        LEAD(updated_at) OVER (PARTITION BY application_id ORDER BY updated_at) AS next_valid_from
    FROM staging.stg_greenhouse__application_history
),
intervals AS (
    SELECT application_id, new_stage_id, new_status, valid_from,
        COALESCE(next_valid_from, CURRENT_TIMESTAMP)::TIMESTAMPTZ AS valid_until
    FROM status_intervals
)
SELECT
    history.application_id,
    history.new_stage_id,
    history.new_status,
    history.valid_from,
    history.valid_until,
    stage.name AS new_stage,
    app.candidate_full_name AS full_name,
    app.status AS current_status,
    app.recruiter_name,
    app.hiring_managers,
    app.sourced_from,
    app.sourced_from_type,
    app.job_title,
    app.job_id,
    app.candidate_id,
    DATE_DIFF('microsecond', history.valid_from, history.valid_until) / 86400000000.0 AS days_in_stage,
    app.job_departments,
    app.job_parent_departments,
    app.job_offices,
    app.candidate_gender,
    app.candidate_disability_status,
    app.candidate_race,
    app.candidate_veteran_status,
    COUNT(activity.activity_id)::HUGEINT AS count_activities_in_stage
FROM intervals AS history
INNER JOIN mart.greenhouse__application_enhanced AS app ON history.application_id = app.application_id
LEFT JOIN staging.stg_greenhouse__job_stage AS stage ON history.new_stage_id = stage.job_stage_id
LEFT JOIN staging.stg_greenhouse__activity AS activity
    ON app.candidate_id = activity.candidate_id
    AND activity.created_at >= history.valid_from
    AND activity.created_at < history.valid_until
GROUP BY ALL
```

## gold SQL（仅供定位差异）

S5

```sql
with application_history as (
    select 
        application_id,
        new_stage_id,
        new_status,
        updated_at as valid_from,
        coalesce(lead(updated_at) over (partition by application_id order by updated_at asc), 
            current_timestamp) as valid_until

    from staging.stg_greenhouse__application_history
),

application as (
    select *
    from mart.greenhouse__application_enhanced
),

job_stage as (
    select *
    from staging.stg_greenhouse__job_stage
),

activity as (
    select *
    from staging.stg_greenhouse__activity
),

join_application_history as (
    select 
        application_history.*,
        job_stage.name as new_stage,
        application.candidate_full_name as full_name,
        application.status as current_status,
        application.recruiter_name,
        application.hiring_managers,
        application.sourced_from, 
        application.sourced_from_type,
        application.job_title,
        application.job_id,
        application.candidate_id,
        application.job_departments,
        application.job_parent_departments,
        application.job_offices,
        application.candidate_gender,
        application.candidate_disability_status,
        application.candidate_race,
        application.candidate_veteran_status

    from application_history 
    join application
        on application_history.application_id = application.application_id
    left join job_stage
        on application_history.new_stage_id = job_stage.job_stage_id
),

time_in_stages as (
    select 
        *,
        extract(epoch from (valid_until - valid_from)) / 86400 as days_in_stage

    from join_application_history
),

activities_in_stages as (
    select 
        time_in_stages.application_id,
        time_in_stages.new_stage_id,
        time_in_stages.new_status,
        time_in_stages.valid_from,
        time_in_stages.valid_until,
        time_in_stages.new_stage,
        time_in_stages.full_name,
        time_in_stages.current_status,
        time_in_stages.recruiter_name,
        time_in_stages.hiring_managers,
        time_in_stages.sourced_from, 
        time_in_stages.sourced_from_type,
        time_in_stages.job_title,
        time_in_stages.job_id,
        time_in_stages.candidate_id,
        time_in_stages.days_in_stage,
        time_in_stages.job_departments,
        time_in_stages.job_parent_departments,
        time_in_stages.job_offices,
        time_in_stages.candidate_gender,
        time_in_stages.candidate_disability_status,
        time_in_stages.candidate_race,
        time_in_stages.candidate_veteran_status,

        sum(case when activity.created_at::timestamp >= valid_from and activity.created_at::timestamp < valid_until 
            then 1 else 0 end) as count_activities_in_stage

    from time_in_stages
    left join activity on activity.candidate_id = time_in_stages.candidate_id

    group by 
        time_in_stages.application_id,
        time_in_stages.new_stage_id,
        time_in_stages.new_status,
        time_in_stages.valid_from,
        time_in_stages.valid_until,
        time_in_stages.new_stage,
        time_in_stages.full_name,
        time_in_stages.current_status,
        time_in_stages.recruiter_name,
        time_in_stages.hiring_managers,
        time_in_stages.sourced_from, 
        time_in_stages.sourced_from_type,
        time_in_stages.job_title,
        time_in_stages.job_id,
        time_in_stages.candidate_id,
        time_in_stages.days_in_stage,
        time_in_stages.job_departments,
        time_in_stages.job_parent_departments,
        time_in_stages.job_offices,
        time_in_stages.candidate_gender,
        time_in_stages.candidate_disability_status,
        time_in_stages.candidate_race,
        time_in_stages.candidate_veteran_status
)

select *
from activities_in_stages
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 121 | 121 | 0 | 0 | 2 | 2 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"application_id":"10000","new_stage_id":"453","job_id":"null","candidate_id":"4202"}</code> |
| K2 | <code>{"application_id":"10137","new_stage_id":"3893","job_id":"911","candidate_id":"1220"}</code> |
| K3 | <code>{"application_id":"10166","new_stage_id":"409","job_id":"null","candidate_id":"930"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| application_id | 0 | 0 | 0 | BIGINT | BIGINT |
| new_stage_id | 0 | 0 | 0 | BIGINT | BIGINT |
| new_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| valid_from | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| valid_until | 107 | 107 | 107 | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE |
| new_stage | 0 | 0 | 0 | VARCHAR | VARCHAR |
| full_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| current_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| recruiter_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| hiring_managers | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sourced_from | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sourced_from_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| job_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| job_id | 0 | 0 | 0 | BIGINT | BIGINT |
| candidate_id | 0 | 0 | 0 | BIGINT | BIGINT |
| days_in_stage | 113 | 113 | 113 | DOUBLE | DOUBLE |
| job_departments | 0 | 0 | 0 | VARCHAR | VARCHAR |
| job_parent_departments | 0 | 0 | 0 | VARCHAR | VARCHAR |
| job_offices | 0 | 0 | 0 | VARCHAR | VARCHAR |
| candidate_gender | 0 | 0 | 0 | VARCHAR | VARCHAR |
| candidate_disability_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| candidate_race | 0 | 0 | 0 | VARCHAR | VARCHAR |
| candidate_veteran_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| count_activities_in_stage | 0 | 0 | 0 | HUGEINT | HUGEINT |

valid_until 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2026-10-27 19:03:43.444736+08 | 2025-10-24 18:32:44.279463+08 |
| K2 | 2026-10-27 19:03:43.444736+08 | 2025-10-24 18:32:44.279463+08 |
| K3 | 2026-10-27 19:03:43.444736+08 | 2025-10-24 18:32:44.279463+08 |

days_in_stage 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 431.87000436516206 | 63.848486248576386 |
| K2 | 436.9961687895139 | 68.97465067292825 |
| K3 | 431.52733340107636 | 63.505815284490744 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"candidate_disability_status","table_rows":119},{"column":"candidate_veteran_status","table_rows":119}]</code> |
| C9_agent_runtime_text | <code>S4:8 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:8 current_timestamp；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:1517 current timestamp；命中数=3</code> |

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
| 27 | run | <code>python run.py &gt; /tmp/run.log 2&gt;&amp;1; tail -100 /tmp/run.log</code> | 5955 | true | false |
| 29 | run | <code>grep -E 'Executing: staging&#124;ERROR - ✗ staging&#124;staging\.' /tmp/run.log &#124; head -90</code> | 7093 | false | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text(); start=s.index('    SELECT\n')+len('    SELECT\n'); end=s.index('\n        ROW_NUMBER()',start)<br> b</code> | 3337 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('greenhouse.duckdb',read_only=True)<br>for s in ['staging','intermediate','mart']:<br> print('\n',s)<br> for (t,) in c.execute(f"select table_name from informatio</code> | 1807 | true | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
w(M,'greenhouse__application_history', '''WITH status_intervals AS (
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-017.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/marts/greenhouse__application_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/sql/marts/greenhouse__application_history.sql`
- S6: `records/006_contract_impl-017.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/result.md`
- S10: `data/023_packages_work/023_impl-017_greenhouse__application_history/023_impl-017_greenhouse__application_history.json`
- S11: `data/005_cs_work/impl-017_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/greenhouse.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions`
