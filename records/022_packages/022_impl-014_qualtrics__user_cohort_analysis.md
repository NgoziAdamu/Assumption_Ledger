# impl-014 | marts | qualtrics__user_cohort_analysis | 差异：S1；日期 原记录

## 契约完整原文

S3:1206–1242

```yaml
    - name: qualtrics__user_cohort_analysis
      description: 'Monthly user cohort metrics from Qualtrics responses: cohort size, per-user averages, value-tier counts, and a 0–100 health score'
      grain: One row per cohort_month
      source_models:
      - staging.stg_qualtrics__survey_response
      business_logic: 'Build cohorts from staging.stg_qualtrics__survey_response: - Keep only records with recorded_date present. - Define user_identifier: use recipient_email when available; otherwise use the literal prefix "anonymous_" followed by response_id. - Per user_identifier: - first_response_date: the earliest timestamp parsed from recorded_date. - cohort_month: the first calendar day of the month of first_response_date. - total_responses: count of distinct response_id. - completed_responses: count of distinct response_id where is_finished is true (null/false excluded). - completion_rate (percent): if total_responses > 0, completed_responses / total_responses × 100; otherwise 0. Use decimal division. - user_value_tier by total_responses: ≥20 Power User; ≥10 High Value; ≥5 Medium Value; ≥2 Low Value; else One-time User. Aggregate by cohort_month: - cohort_size: distinct users in the cohort. - avg_responses_per_user: average of per-user total_responses. - avg_completion_rate: average of per-user completion_rate (percent). - power_users/high_value_users/medium_value_users/low_value_users/one_time_users: counts of users in each tier. - cohort_health_score: 0.6 × avg_completion_rate + 40 × (count of Power or High Value users ÷ cohort_size). Expected range 0–100. Finalize: - Exclude cohorts where cohort_size = 0. - Return one row per cohort_month; sorted descending by cohort_month (sorting does not affect values).'
      columns:
      - name: cohort_month
        data_type: DATE
        description: First day of the month of each user's first response; cohort grouping key.
      - name: cohort_size
        data_type: BIGINT
        description: Number of distinct users in the cohort_month.
      - name: avg_responses_per_user
        data_type: DOUBLE
        description: Mean per-user count of distinct responses within the cohort.
      - name: avg_completion_rate
        data_type: DOUBLE
        description: Mean per-user completion rate in percent, where per-user rate is completed distinct responses divided by total distinct responses times 100.
      - name: power_users
        data_type: BIGINT
        description: Count of users with total_responses ≥ 20 in the cohort.
      - name: high_value_users
        data_type: BIGINT
        description: Count of users with total_responses ≥ 10 and < 20 in the cohort.
      - name: medium_value_users
        data_type: BIGINT
        description: Count of users with total_responses ≥ 5 and < 10 in the cohort.
      - name: low_value_users
        data_type: BIGINT
        description: Count of users with total_responses ≥ 2 and < 5 in the cohort.
      - name: one_time_users
        data_type: BIGINT
        description: Count of users with total_responses = 1 in the cohort.
      - name: cohort_health_score
        data_type: DOUBLE
        description: '0–100 score: 0.6×avg_completion_rate + 40×(share of Power or High Value users in the cohort).'
```

## agent 最终 SQL

S4

```sql
WITH eligible_responses AS (
    SELECT
        coalesce(recipient_email, 'anonymous_' || response_id) AS user_identifier,
        response_id,
        is_finished,
        try_strptime(recorded_date, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS recorded_at
    FROM staging.stg_qualtrics__survey_response
    WHERE recorded_date IS NOT NULL
),
user_metrics AS (
    SELECT
        user_identifier,
        date_trunc('month', min(recorded_at))::DATE AS cohort_month,
        count(DISTINCT response_id)::BIGINT AS total_responses,
        count(DISTINCT response_id) FILTER (WHERE is_finished IS TRUE)::BIGINT AS completed_responses
    FROM eligible_responses
    WHERE recorded_at IS NOT NULL
    GROUP BY user_identifier
),
user_tiers AS (
    SELECT
        *,
        completed_responses::DOUBLE / nullif(total_responses, 0) * 100 AS completion_rate,
        CASE
            WHEN total_responses >= 20 THEN 'Power User'
            WHEN total_responses >= 10 THEN 'High Value'
            WHEN total_responses >= 5 THEN 'Medium Value'
            WHEN total_responses >= 2 THEN 'Low Value'
            ELSE 'One-time User'
        END AS user_value_tier
    FROM user_metrics
),
cohort_metrics AS (
    SELECT
        cohort_month,
        count(DISTINCT user_identifier)::BIGINT AS cohort_size,
        avg(total_responses)::DOUBLE AS avg_responses_per_user,
        avg(completion_rate)::DOUBLE AS avg_completion_rate,
        count(*) FILTER (WHERE user_value_tier = 'Power User')::BIGINT AS power_users,
        count(*) FILTER (WHERE user_value_tier = 'High Value')::BIGINT AS high_value_users,
        count(*) FILTER (WHERE user_value_tier = 'Medium Value')::BIGINT AS medium_value_users,
        count(*) FILTER (WHERE user_value_tier = 'Low Value')::BIGINT AS low_value_users,
        count(*) FILTER (WHERE user_value_tier = 'One-time User')::BIGINT AS one_time_users
    FROM user_tiers
    GROUP BY cohort_month
)
SELECT
    cohort_month,
    cohort_size,
    avg_responses_per_user,
    avg_completion_rate,
    power_users,
    high_value_users,
    medium_value_users,
    low_value_users,
    one_time_users,
    0.6 * avg_completion_rate + 40.0 * (power_users + high_value_users)::DOUBLE / cohort_size AS cohort_health_score
FROM cohort_metrics
WHERE cohort_size > 0
ORDER BY cohort_month DESC
```

## gold SQL（仅供定位差异）

S5

```sql
-- User Engagement Mart Dashboard

with user_engagement as (
    select *
    from intermediate.int_qualtrics__user_engagement
),

survey_responses as (
    select *
    from staging.stg_qualtrics__survey_response
),

-- Cohort analysis based on first response date
user_cohorts as (
    select 
        coalesce(sr.recipient_email, 'anonymous_' || sr.response_id) as user_identifier,
        min(try_cast(sr.recorded_date as timestamp)) as first_response_date,
        date_trunc('month', min(try_cast(sr.recorded_date as timestamp))) as cohort_month,
        count(distinct sr.response_id) as total_responses,
        count(distinct case when sr.is_finished then sr.response_id end) as completed_responses,
        count(distinct sr.survey_id) as surveys_participated,
        
        -- User value tier
        case 
            when count(distinct sr.response_id) >= 20 then 'Power User'
            when count(distinct sr.response_id) >= 10 then 'High Value'
            when count(distinct sr.response_id) >= 5 then 'Medium Value'
            when count(distinct sr.response_id) >= 2 then 'Low Value'
            else 'One-time User'
        end as user_value_tier,
        
        -- Engagement consistency
        case 
            when count(distinct sr.response_id) > 0 
            then count(distinct case when sr.is_finished then sr.response_id end)::decimal / count(distinct sr.response_id) * 100
            else 0 
        end as completion_rate,
        
        current_timestamp as analysis_date
        
    from survey_responses sr
    where sr.recorded_date is not null
    group by coalesce(sr.recipient_email, 'anonymous_' || sr.response_id)
),

-- Cohort summary statistics
cohort_summary as (
    select 
        uc.cohort_month,
        count(distinct uc.user_identifier) as cohort_size,
        avg(uc.total_responses) as avg_responses_per_user,
        avg(uc.completion_rate) as avg_completion_rate,
        
        -- Value distribution
        count(case when uc.user_value_tier = 'Power User' then 1 end) as power_users,
        count(case when uc.user_value_tier = 'High Value' then 1 end) as high_value_users,
        count(case when uc.user_value_tier = 'Medium Value' then 1 end) as medium_value_users,
        count(case when uc.user_value_tier = 'Low Value' then 1 end) as low_value_users,
        count(case when uc.user_value_tier = 'One-time User' then 1 end) as one_time_users,
        
        -- Cohort health score
        (avg(uc.completion_rate) * 0.6 + 
         (count(case when uc.user_value_tier in ('Power User', 'High Value') then 1 end)::decimal / 
          count(distinct uc.user_identifier)) * 40) as cohort_health_score
         
    from user_cohorts uc
    group by uc.cohort_month
)

select * 
from cohort_summary
where cohort_size > 0
order by cohort_month desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 4 | 1 | 4 | 1 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| cohort_size | 0 | 0 | 0 | BIGINT | BIGINT |
| avg_responses_per_user | 0 | 0 | 0 | DOUBLE | DOUBLE |
| power_users | 0 | 0 | 0 | BIGINT | BIGINT |
| high_value_users | 0 | 0 | 0 | BIGINT | BIGINT |
| medium_value_users | 0 | 0 | 0 | BIGINT | BIGINT |
| low_value_users | 0 | 0 | 0 | BIGINT | BIGINT |
| one_time_users | 0 | 0 | 0 | BIGINT | BIGINT |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"cohort_month":"2025-06-01"},{"cohort_month":"2025-07-01"},{"cohort_month":"2025-08-01"},{"cohort_month":"2025-09-01"}]</code> | <code>[{"cohort_month":null}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"power_users","value":"0"}]</code> |
| B8_shared_single_source | <code>唯一源=staging.stg_qualtrics__survey_response；目标数=4；例=["intermediate.int_qualtrics__response_quality","intermediate.int_qualtrics__user_engagement","marts.qualtrics__channel_performance"]</code> |
| C9_gold_runtime_text | <code>S5:39 current_timestamp；命中数=1</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory sql/marts/qualtrics__user_cohort_analysis.sql:17:    WHERE recorded_at IS NOT NULL</code> |

## 轨迹索引（不放输出原文）

本题事件总数：81；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 2649 | true | false |
| 19 | run | <code>cat &gt; /tmp/gen_stg.py &lt;&lt;'PY'<br>import yaml, pathlib<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>colmaps={<br>'user':{'user_id':'id','account_created_at':'account_creation_date','account_expires_at':'</code> | 0 | false | false |
| 21 | run | <code>cat &gt; sql/intermediate/int_qualtrics__survey_performance.sql &lt;&lt;'SQL'<br>WITH response_aggregates AS (<br>    SELECT<br>        survey_id,<br>        count(DISTINCT response_id) AS total_responses,<br>        count(D</code> | 0 | false | false |
| 23 | run | <code>cat &gt; sql/intermediate/int_qualtrics__contacts.sql &lt;&lt;'SQL'<br>WITH membership_aggregates AS (<br>    SELECT<br>        directory_id,<br>        contact_id,<br>        string_agg(mailing_list_id, ', ') FILTER (WHERE </code> | 0 | false | false |
| 27 | run | <code>cat &gt; sql/marts/qualtrics__survey_analytics.sql &lt;&lt;'SQL'<br>WITH quality_summary AS (<br>    SELECT<br>        survey_id,<br>        count(DISTINCT response_id)::BIGINT AS total_assessed_responses,<br>        count(D</code> | 0 | false | false |
| 29 | run | <code>cat &gt; sql/marts/qualtrics__contact.sql &lt;&lt;'SQL'<br>WITH distribution_response AS (<br>    SELECT<br>        distribution_contact.contact_id,<br>        distribution.survey_id,<br>        distribution_contact.sent_at,</code> | 0 | false | false |
| 35 | run | <code>cat &gt; /tmp/gen_survey_mart.py &lt;&lt;'PY'<br>from pathlib import Path<br>c=yaml.safe_load(open('docs/data_contract.yaml')) if False else None<br>base='survey_id survey_name survey_status brand_base_url brand_id bun</code> | 0 | false | false |
| 39 | run | <code>python run.py &gt; /tmp/pipeline.log 2&gt;&amp;1; tail -100 /tmp/pipeline.log</code> | 6507 | true | false |
| 45 | run | <code>grep -A10 -B3 'Binder Error' /tmp/pipeline2.log</code> | 1149 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('qualtrics.duckdb',read_only=True)<br>for t,col in [('raw.survey_response','recorded_date'),('raw.survey_response','start_date'),('raw.user','account_creati</code> | 1177 | false | false |
| 61 | run | <code>python - &lt;&lt;'PY'<br>import duckdb, yaml, pathlib<br>c=duckdb.connect('qualtrics.duckdb',read_only=True)<br>for schema,t in [('intermediate','int_qualtrics__survey_performance'),('intermediate','int_qualtrics__u</code> | 370 | true | false |
| 65 | run | <code>grep -R 'try_cast\&#124;try_strptime' -n sql/marts/qualtrics__daily_breakdown.sql sql/marts/qualtrics__directory.sql &#124; head -30; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('qualtrics.duckdb',read_only=</code> | 1628 | false | false |
| 69 | run | grep -n recorded_at sql/marts/qualtrics__survey.sql sql/marts/qualtrics__user_cohort_analysis.sql | 927 | true | false |

### agent action 的 thought/message 命中原句

event 27 / message

```text
cat > sql/marts/qualtrics__user_cohort_analysis.sql <<'SQL'
```
event 61 / message

```text
for schema,t in [('intermediate','int_qualtrics__survey_performance'),('intermediate','int_qualtrics__user_engagement'),('intermediate','int_qualtrics__response_quality'),('mart','qualtrics__survey_analytics'),('mart','qualtrics__channel_performance'),('mart','qualtrics__daily_breakdown'),('mart','qualtrics__user_cohort_analysis')]:
```
event 61 / message

```text
print('cohort dates',c.execute('select count(*) from mart.qualtrics__user_cohort_analysis').fetchone()[0])
```
event 65 / message

```text
print(c.execute('select * from mart.qualtrics__user_cohort_analysis').fetchall())
```
event 69 / message

```text
Running command: grep -n recorded_at sql/marts/qualtrics__survey.sql sql/marts/qualtrics__user_cohort_analysis.sql
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-014.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/marts/qualtrics__user_cohort_analysis.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/marts/qualtrics__user_cohort_analysis.sql`
- S6: `records/006_contract_impl-014.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/result.md`
- S10: `data/022_packages_work/022_impl-014_qualtrics__user_cohort_analysis/022_impl-014_qualtrics__user_cohort_analysis.json`
- S11: `data/005_cs_work/impl-014_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions`
