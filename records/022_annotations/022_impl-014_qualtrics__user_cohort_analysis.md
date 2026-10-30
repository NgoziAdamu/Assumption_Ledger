# impl-014 / qualtrics__user_cohort_analysis（全量；v2）

## 1. 差异与结论

gold对带偏移时间直接TRY_CAST全部NULL，且cohort_month输出TIMESTAMP而契约DATE。agent正确解析得到4个月份；只改gold解析后仍有DATE/TIMESTAMP键差，再按契约DATE投影后复核一致。两项都是gold条件差异，归O；不是因agent额外WHERE就直接定C。

主要原因：**O**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| parse_timestamp | O | 4 | 32 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_qualtrics__user_cohort_analysis.md](../../records/022_packages/022_impl-014_qualtrics__user_cohort_analysis.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_qualtrics__user_cohort_analysis/022_impl-014_qualtrics__user_cohort_analysis.json`。
- 比较结果：[022_reruns_impl-014_qualtrics__user_cohort_analysis.json](../022_reruns_impl-014_qualtrics__user_cohort_analysis.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第1206–1242行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/marts/qualtrics__user_cohort_analysis.sql`；原件第1–60行。

```sql
   1: WITH eligible_responses AS (
   2:     SELECT
   3:         coalesce(recipient_email, 'anonymous_' || response_id) AS user_identifier,
   4:         response_id,
   5:         is_finished,
   6:         try_strptime(recorded_date, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS recorded_at
   7:     FROM staging.stg_qualtrics__survey_response
   8:     WHERE recorded_date IS NOT NULL
   9: ),
  10: user_metrics AS (
  11:     SELECT
  12:         user_identifier,
  13:         date_trunc('month', min(recorded_at))::DATE AS cohort_month,
  14:         count(DISTINCT response_id)::BIGINT AS total_responses,
  15:         count(DISTINCT response_id) FILTER (WHERE is_finished IS TRUE)::BIGINT AS completed_responses
  16:     FROM eligible_responses
  17:     WHERE recorded_at IS NOT NULL
  18:     GROUP BY user_identifier
  19: ),
  20: user_tiers AS (
  21:     SELECT
  22:         *,
  23:         completed_responses::DOUBLE / nullif(total_responses, 0) * 100 AS completion_rate,
  24:         CASE
  25:             WHEN total_responses >= 20 THEN 'Power User'
  26:             WHEN total_responses >= 10 THEN 'High Value'
  27:             WHEN total_responses >= 5 THEN 'Medium Value'
  28:             WHEN total_responses >= 2 THEN 'Low Value'
  29:             ELSE 'One-time User'
  30:         END AS user_value_tier
  31:     FROM user_metrics
  32: ),
  33: cohort_metrics AS (
  34:     SELECT
  35:         cohort_month,
  36:         count(DISTINCT user_identifier)::BIGINT AS cohort_size,
  37:         avg(total_responses)::DOUBLE AS avg_responses_per_user,
  38:         avg(completion_rate)::DOUBLE AS avg_completion_rate,
  39:         count(*) FILTER (WHERE user_value_tier = 'Power User')::BIGINT AS power_users,
  40:         count(*) FILTER (WHERE user_value_tier = 'High Value')::BIGINT AS high_value_users,
  41:         count(*) FILTER (WHERE user_value_tier = 'Medium Value')::BIGINT AS medium_value_users,
  42:         count(*) FILTER (WHERE user_value_tier = 'Low Value')::BIGINT AS low_value_users,
  43:         count(*) FILTER (WHERE user_value_tier = 'One-time User')::BIGINT AS one_time_users
  44:     FROM user_tiers
  45:     GROUP BY cohort_month
  46: )
  47: SELECT
  48:     cohort_month,
  49:     cohort_size,
  50:     avg_responses_per_user,
  51:     avg_completion_rate,
  52:     power_users,
  53:     high_value_users,
  54:     medium_value_users,
  55:     low_value_users,
  56:     one_time_users,
  57:     0.6 * avg_completion_rate + 40.0 * (power_users + high_value_users)::DOUBLE / cohort_size AS cohort_health_score
  58: FROM cohort_metrics
  59: WHERE cohort_size > 0
  60: ORDER BY cohort_month DESC
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/marts/qualtrics__user_cohort_analysis.sql`；原件第1–73行。

```sql
   1: -- User Engagement Mart Dashboard
   2: 
   3: with user_engagement as (
   4:     select *
   5:     from intermediate.int_qualtrics__user_engagement
   6: ),
   7: 
   8: survey_responses as (
   9:     select *
  10:     from staging.stg_qualtrics__survey_response
  11: ),
  12: 
  13: -- Cohort analysis based on first response date
  14: user_cohorts as (
  15:     select 
  16:         coalesce(sr.recipient_email, 'anonymous_' || sr.response_id) as user_identifier,
  17:         min(try_cast(sr.recorded_date as timestamp)) as first_response_date,
  18:         date_trunc('month', min(try_cast(sr.recorded_date as timestamp))) as cohort_month,
  19:         count(distinct sr.response_id) as total_responses,
  20:         count(distinct case when sr.is_finished then sr.response_id end) as completed_responses,
  21:         count(distinct sr.survey_id) as surveys_participated,
  22:         
  23:         -- User value tier
  24:         case 
  25:             when count(distinct sr.response_id) >= 20 then 'Power User'
  26:             when count(distinct sr.response_id) >= 10 then 'High Value'
  27:             when count(distinct sr.response_id) >= 5 then 'Medium Value'
  28:             when count(distinct sr.response_id) >= 2 then 'Low Value'
  29:             else 'One-time User'
  30:         end as user_value_tier,
  31:         
  32:         -- Engagement consistency
  33:         case 
  34:             when count(distinct sr.response_id) > 0 
  35:             then count(distinct case when sr.is_finished then sr.response_id end)::decimal / count(distinct sr.response_id) * 100
  36:             else 0 
  37:         end as completion_rate,
  38:         
  39:         current_timestamp as analysis_date
  40:         
  41:     from survey_responses sr
  42:     where sr.recorded_date is not null
  43:     group by coalesce(sr.recipient_email, 'anonymous_' || sr.response_id)
  44: ),
  45: 
  46: -- Cohort summary statistics
  47: cohort_summary as (
  48:     select 
  49:         uc.cohort_month,
  50:         count(distinct uc.user_identifier) as cohort_size,
  51:         avg(uc.total_responses) as avg_responses_per_user,
  52:         avg(uc.completion_rate) as avg_completion_rate,
  53:         
  54:         -- Value distribution
  55:         count(case when uc.user_value_tier = 'Power User' then 1 end) as power_users,
  56:         count(case when uc.user_value_tier = 'High Value' then 1 end) as high_value_users,
  57:         count(case when uc.user_value_tier = 'Medium Value' then 1 end) as medium_value_users,
  58:         count(case when uc.user_value_tier = 'Low Value' then 1 end) as low_value_users,
  59:         count(case when uc.user_value_tier = 'One-time User' then 1 end) as one_time_users,
  60:         
  61:         -- Cohort health score
  62:         (avg(uc.completion_rate) * 0.6 + 
  63:          (count(case when uc.user_value_tier in ('Power User', 'High Value') then 1 end)::decimal / 
  64:           count(distinct uc.user_identifier)) * 40) as cohort_health_score
  65:          
  66:     from user_cohorts uc
  67:     group by uc.cohort_month
  68: )
  69: 
  70: select * 
  71: from cohort_summary
  72: where cohort_size > 0
  73: order by cohort_month desc
```

## 3. agent看到的材料与不确定性

已检视该题全部81个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 55 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/55.json`。
- event 56 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/56.json`。
- event 57 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/57.json`。
- event 58 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/58.json`。
- event 69 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/69.json`。
- event 70 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/70.json`。
- event 79 / finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/79.json`。

四档：**针对本表的具体说明**。

原句（见上述最终报告事件）：

```text
无法按已观察到的带时区格式解析的日期仍保留在原文本字段，但不进入 cohort、30 日窗口及按日统计，可能造成日期类指标低估。
```

## 4. 核实查询与诊断

核实查询共**3条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'staging.stg_qualtrics__survey_response' source_table,count(*) rows FROM staging.stg_qualtrics__survey_response
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ...'staging.stg_qualtrics__survey_response' source_table,count(*) rows FROM staging.stg_qualtrics__survey_response\n                                                                          ^"}
```

### 核实 V2：cohort时间解析

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) n,count(try_cast(recorded_date AS TIMESTAMP)) direct_parsed,count(try_strptime(recorded_date,'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM staging.stg_qualtrics__survey_response WHERE recorded_date IS NOT NULL
```

```json
{"columns": ["n", "direct_parsed", "format_parsed"], "result": [[17995, 0, 17995]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'staging.stg_qualtrics__survey_response' source_table,count(*) source_rows FROM staging.stg_qualtrics__survey_response
```

```json
{"columns": ["source_table", "source_rows"], "result": [["staging.stg_qualtrics__survey_response", 17995]]}
```

### 诊断（允许gold，不计5条）

`records/022_diagnostics.json` 本表条目：

```json
{"index": 25, "kind": "诊断查询", "queries": [], "gold_parser_diagnostic": {"old": "try_cast(sr.recorded_date as timestamp)", "new": "try_strptime(sr.recorded_date, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP", "occurrences": 2, "comparison": {"levels": [{"level": "L0", "agent_rows": 4, "gold_rows": 4, "agent_only_key_rows": 4, "gold_only_key_rows": 4, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"cohort_month": 0, "avg_responses_per_user": 0, "cohort_size": 0, "high_value_users": 0, "low_value_users": 0, "medium_value_users": 0, "one_time_users": 0, "power_users": 0}, "key_aware_agent_unmatched": 4, "key_aware_gold_unmatched": 4, "whole_match": false, "row_scale": 8, "cell_scale": 64, "comparison_column_count_including_keys": 8}, {"level": "L1", "agent_rows": 4, "gold_rows": 4, "agent_only_key_rows": 4, "gold_only_key_rows": 4, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"cohort_month": 0, "avg_responses_per_user": 0, "cohort_size": 0, "high_value_users": 0, "low_value_users": 0, "medium_value_users": 0, "one_time_users": 0, "power_users": 0}, "key_aware_agent_unmatched": 4, "key_aware_gold_unmatched": 4, "whole_match": false, "row_scale": 8, "cell_scale": 64, "comparison_column_count_including_keys": 8}, {"level": "L2", "agent_rows": 4, "gold_rows": 4, "agent_only_key_rows": 4, "gold_only_key_rows": 4, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"cohort_month": 0, "avg_responses_per_user": 0, "cohort_size": 0, "high_value_users": 0, "low_value_users": 0, "medium_value_users": 0, "one_time_users": 0, "power_users": 0}, "key_aware_agent_unmatched": 4, "key_aware_gold_unmatched": 4, "whole_match": false, "row_scale": 8, "cell_scale": 64, "comparison_column_count_including_keys": 8}, {"level": "L3", "agent_rows": 4, "gold_rows": 4, "agent_only_key_rows": 4, "gold_only_key_rows": 4, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"cohort_month": 0, "avg_responses_per_user": 0, "cohort_size": 0, "high_value_users": 0, "low_value_users": 0, "medium_value_users": 0, "one_time_users": 0, "power_users": 0}, "key_aware_agent_unmatched": 4, "key_aware_gold_unmatched": 4, "whole_match": false, "row_scale": 8, "cell_scale": 64, "comparison_column_count_including_keys": 8}], "first_match": null}}, "gold_parser_and_contract_date_diagnostic": {"sql": "SELECT * REPLACE(CAST(cohort_month AS DATE) AS cohort_month) FROM repaired_gold", "comparison": {"levels": [{"level": "L0", "agent_rows": 4, "gold_rows": 4, "agent_only_key_rows": 0, "gold_only_key_rows": 0, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"cohort_month": 0, "avg_responses_per_user": 0, "cohort_size": 0, "high_value_users": 0, "low_value_users": 0, "medium_value_users": 0, "one_time_users": 0, "power_users": 0}, "key_aware_agent_unmatched": 0, "key_aware_gold_unmatched": 0, "whole_match": true, "row_scale": 0, "cell_scale": 0, "comparison_column_count_including_keys": 8}, {"level": "L1", "agent_rows": 4, "gold_rows": 4, "agent_only_key_rows": 0, "gold_only_key_rows": 0, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"cohort_month": 0, "avg_responses_per_user": 0, "cohort_size": 0, "high_value_users": 0, "low_value_users": 0, "medium_value_users": 0, "one_time_users": 0, "power_users": 0}, "key_aware_agent_unmatched": 0, "key_aware_gold_unmatched": 0, "whole_match": true, "row_scale": 0, "cell_scale": 0, "comparison_column_count_including_keys": 8}, {"level": "L2", "agent_rows": 4, "gold_rows": 4, "agent_only_key_rows": 0, "gold_only_key_rows": 0, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"cohort_month": 0, "avg_responses_per_user": 0, "cohort_size": 0, "high_value_users": 0, "low_value_users": 0, "medium_value_users": 0, "one_time_users": 0, "power_users": 0}, "key_aware_agent_unmatched": 0, "key_aware_gold_unmatched": 0, "whole_match": true, "row_scale": 0, "cell_scale": 0, "comparison_column_count_including_keys": 8}, {"level": "L3", "agent_rows": 4, "gold_rows": 4, "agent_only_key_rows": 0, "gold_only_key_rows": 0, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"cohort_month": 0, "avg_responses_per_user": 0, "cohort_size": 0, "high_value_users": 0, "low_value_users": 0, "medium_value_users": 0, "one_time_users": 0, "power_users": 0}, "key_aware_agent_unmatched": 0, "key_aware_gold_unmatched": 0, "whole_match": true, "row_scale": 0, "cell_scale": 0, "comparison_column_count_including_keys": 8}], "first_match": "L0"}, "purpose": "同时纠正gold解析和契约DATE键类型，只作O诊断，不作为agent单改干预"}}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["cohort_month"]`；比较列：`["avg_responses_per_user", "cohort_size", "high_value_users", "low_value_users", "medium_value_users", "one_time_users", "power_users"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |
| L1 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |
| L2 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |
| L3 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| cohort_month | 0 | 0 | 0 | 0 |
| avg_responses_per_user | 0 | 0 | 0 | 0 |
| cohort_size | 0 | 0 | 0 | 0 |
| high_value_users | 0 | 0 | 0 | 0 |
| low_value_users | 0 | 0 | 0 | 0 |
| medium_value_users | 0 | 0 | 0 | 0 |
| one_time_users | 0 | 0 | 0 | 0 |
| power_users | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-014_qualtrics__user_cohort_analysis/baseline.sql`；SHA-256：`195536d0a23ffdb981fa28b5f9d7f29a32cb5b3b1dbb3af11b10e4265a5dc36f`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |
| L1 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |
| L2 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |
| L3 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| cohort_month | 0 | 0 | 0 | 0 |
| avg_responses_per_user | 0 | 0 | 0 | 0 |
| cohort_size | 0 | 0 | 0 | 0 |
| high_value_users | 0 | 0 | 0 | 0 |
| low_value_users | 0 | 0 | 0 | 0 |
| medium_value_users | 0 | 0 | 0 | 0 |
| one_time_users | 0 | 0 | 0 | 0 |
| power_users | 0 | 0 | 0 | 0 |

### parse_timestamp

SQL：`data/022_work/impl-014_qualtrics__user_cohort_analysis/parse_timestamp.sql`；SHA-256：`9467e826820602c4ea5ba469ac3fd39dfabda463deaf06d7e5a3189ddd2f805a`。

替换offset=173，原表达式所在行约6（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(recorded_date, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP
-- 新
try_cast(recorded_date AS TIMESTAMP)
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 0/1 | 0/1 | 0/0 | 0 | 1 | 8 | False |
| L1 | 0/1 | 0/1 | 0/0 | 0 | 1 | 8 | False |
| L2 | 0/1 | 0/1 | 0/0 | 0 | 1 | 8 | False |
| L3 | 0/1 | 0/1 | 0/0 | 0 | 1 | 8 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| cohort_month | 0 | 0 | 0 | 0 |
| avg_responses_per_user | 0 | 0 | 0 | 0 |
| cohort_size | 0 | 0 | 0 | 0 |
| high_value_users | 0 | 0 | 0 | 0 |
| low_value_users | 0 | 0 | 0 | 0 |
| medium_value_users | 0 | 0 | 0 | 0 |
| one_time_users | 0 | 0 | 0 | 0 |
| power_users | 0 | 0 | 0 | 0 |

### keep_null_dates

SQL：`data/022_work/impl-014_qualtrics__user_cohort_analysis/keep_null_dates.sql`；SHA-256：`9767ce7325c16f70740485d7457101693428a6ebbff8b33dc0a2c30998fed261`。

替换offset=658，原表达式所在行约17（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    WHERE recorded_at IS NOT NULL

-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |
| L1 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |
| L2 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |
| L3 | 4/1 | 4/1 | 0/0 | 0 | 5 | 40 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| cohort_month | 0 | 0 | 0 | 0 |
| avg_responses_per_user | 0 | 0 | 0 | 0 |
| cohort_size | 0 | 0 | 0 | 0 |
| high_value_users | 0 | 0 | 0 | 0 |
| low_value_users | 0 | 0 | 0 | 0 |
| medium_value_users | 0 | 0 | 0 | 0 |
| one_time_users | 0 | 0 | 0 | 0 |
| power_users | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：parse_timestamp；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- parse_timestamp：O；主项。契约按实际首次响应月份聚合，gold解析失败合到NULL月份。（行减少4，格减少32）
- keep_null_dates：C；单修未满足本表所选尺度的参与门槛。契约仅筛recorded_date非空，agent增加解析成功过滤；单改需检验是否原因。（行减少0，格减少0）

## 规则问题

O与A边界：契约明确首次响应月份及DATE键，gold解析全部NULL且类型TIMESTAMP；有原始日期可解析的诊断，按O。给gold改解析并cast DATE是诊断，不冒充agent单改。
