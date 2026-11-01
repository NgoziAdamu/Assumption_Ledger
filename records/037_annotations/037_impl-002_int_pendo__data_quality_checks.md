# impl-002_int_pendo__data_quality_checks（037 正式批次）

主要原因：**已说出的降级**；把握：高。019旧主要原因原样保留：`D`，不作为新类别依据。

## 范围与材料

- 层：intermediate；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__data_quality_checks.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，finish 59 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-002_int_pendo__data_quality_checks.json`；037补充：`records/037_checks/`。

## 逐点标注

### completeness_rows

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

报告只交summary，遗漏event completeness详情行；019单独插回该行已确认其贡献。其余章节在037继续分别检查。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build a four-section report by computing intermediate checks and then UNION ALLing section-specific rows (column meanings vary by section; see column rules below). No output ordering is enforced. All timestamps use current_timestamp at query time. 1) Data completeness checks: - account_history: total records; count of NULL account_id; count of NULL first_visit_at; count of NULL last_visit_at; other counts set to 0. - visitor_history: total records; count of NULL visitor_id; other counts set to 0; sixth position is count of NULL account_id. - event: total records; second–sixth positions respectively count NULL visitor_id, NULL account_id, NULL occurred_at, NULL app_id, and count of num_events that are NULL or negative. - Later UNIONs align values by position from the first select’s column order. 2) Data consistency checks: five issue types with counts and descriptions: - timestamp_consistency: events with occurred_at in the future. - account_visitor_relationship: visitor_history rows whose non-NULL account_id does not exist in account_history. - event_visitor_relationship: events whose visitor_id does not exist in visitor_history. - negative_metrics: events with negative num_minutes or num_events. - chronological_consistency: accounts where first_visit_at and last_visit_at are both present and first_visit_at is after last_visit_at. 3) Business logic violations: four rules with counts and descriptions: - impossible_session_duration: events with num_minutes > 480. - excessive_daily_events: per visitor and day, sum num_events; count groups with sum > 10000. - duplicate_primary_keys: difference between total events and distinct event_key. - inactive_paying_accounts: accounts with no events in the last 90 days. 4) Summary quality metrics: - completeness_score: compute the share of complete records by subtracting the ratio of (sum of NULL primary keys + sum of missing names + sum of missing first visits) to (three times the sum of total records) from 1, then multiply by 100; return NULL if the denominator is zero. - consistency_score: compute 1 minus the ratio of total consistency violations to the overall total records, then multiply by 100; return NULL if the denominator is zero. - business_logic_score: compute 1 minus the ratio of total business logic violations to the overall total records, then multiply by 100; return NULL if the denominator is zero. - These totals are evaluated over a Cartesian product of the completeness, consistency, and business-logic CTEs, so each component’s sum is multiplied by the row counts of the other two CTEs. - calculated_at uses the current time. 5) Final UNION ALL report rows: - Data Quality Summary: 1 row with the three percentage scores; overall_quality_score is their average; quality_grade is Excellent (>=95), Good (>=85), Fair (>=70), else Poor; calculated_at from the summary CTE. - Data Completeness Details: one row per table_name with column mapping by position: table_name (text), total_records, null_primary_keys, missing_names, missing_first_visit (as text), and calculated_at as current time. - Data Consistency Issues: one row per check_type with column mapping by position: check_type (text), total_violations, NULL, NULL, violation_description (text), and calculated_at as current time. - Business Logic Violations: one row per violation_type with column mapping by position: violation_type (text), violation_count, NULL, NULL, description (text), and calculated_at as current time. Notes: - Outlier detection and data freshness CTEs are computed but not included in the final UNION, so they do not appear in the output. - DuckDB coerces types across the UNION by position: columns 2 and 6 are VARCHAR; columns 3–5 are FLOAT; NULLs are preserved.'

SQL原处：

`data/019_work/impl-002_int_pendo__data_quality_checks/baseline.sql`，第 1–1 行：

```sql
SELECT 'Data Quality Summary'::VARCHAR report_section,NULL::VARCHAR completeness_score,NULL::FLOAT consistency_score,NULL::FLOAT business_logic_score,NULL::FLOAT overall_quality_score,'Poor'::VARCHAR quality_grade,TIMESTAMPTZ '2025-10-11 14:44:19.830000+08:00' calculated_at
```

单改/诊断：`records/019_reruns_impl-002_int_pendo__data_quality_checks.json#completeness_rows`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 13/63 | 12/58 | 1/5 |
| L1 | 13/63 | 12/58 | 1/5 |
| L2 | 13/63 | 12/58 | 1/5 |
| L3 | 13/63 | 12/58 | 1/5 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> the data-quality report is summary-only;

交付报告明确点到这张表/这类指标及其占位或选择。

### completeness_account

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

只补一条缺失详情行；沿契约的UNION按位置映射，不改summary。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build a four-section report by computing intermediate checks and then UNION ALLing section-specific rows (column meanings vary by section; see column rules below). No output ordering is enforced. All timestamps use current_timestamp at query time. 1) Data completeness checks: - account_history: total records; count of NULL account_id; count of NULL first_visit_at; count of NULL last_visit_at; other counts set to 0. - visitor_history: total records; count of NULL visitor_id; other counts set to 0; sixth position is count of NULL account_id. - event: total records; second–sixth positions respectively count NULL visitor_id, NULL account_id, NULL occurred_at, NULL app_id, and count of num_events that are NULL or negative. - Later UNIONs align values by position from the first select’s column order. 2) Data consistency checks: five issue types with counts and descriptions: - timestamp_consistency: events with occurred_at in the future. - account_visitor_relationship: visitor_history rows whose non-NULL account_id does not exist in account_history. - event_visitor_relationship: events whose visitor_id does not exist in visitor_history. - negative_metrics: events with negative num_minutes or num_events. - chronological_consistency: accounts where first_visit_at and last_visit_at are both present and first_visit_at is after last_visit_at. 3) Business logic violations: four rules with counts and descriptions: - impossible_session_duration: events with num_minutes > 480. - excessive_daily_events: per visitor and day, sum num_events; count groups with sum > 10000. - duplicate_primary_keys: difference between total events and distinct event_key. - inactive_paying_accounts: accounts with no events in the last 90 days. 4) Summary quality metrics: - completeness_score: compute the share of complete records by subtracting the ratio of (sum of NULL primary keys + sum of missing names + sum of missing first visits) to (three times the sum of total records) from 1, then multiply by 100; return NULL if the denominator is zero. - consistency_score: compute 1 minus the ratio of total consistency violations to the overall total records, then multiply by 100; return NULL if the denominator is zero. - business_logic_score: compute 1 minus the ratio of total business logic violations to the overall total records, then multiply by 100; return NULL if the denominator is zero. - These totals are evaluated over a Cartesian product of the completeness, consistency, and business-logic CTEs, so each component’s sum is multiplied by the row counts of the other two CTEs. - calculated_at uses the current time. 5) Final UNION ALL report rows: - Data Quality Summary: 1 row with the three percentage scores; overall_quality_score is their average; quality_grade is Excellent (>=95), Good (>=85), Fair (>=70), else Poor; calculated_at from the summary CTE. - Data Completeness Details: one row per table_name with column mapping by position: table_name (text), total_records, null_primary_keys, missing_names, missing_first_visit (as text), and calculated_at as current time. - Data Consistency Issues: one row per check_type with column mapping by position: check_type (text), total_violations, NULL, NULL, violation_description (text), and calculated_at as current time. - Business Logic Violations: one row per violation_type with column mapping by position: violation_type (text), violation_count, NULL, NULL, description (text), and calculated_at as current time. Notes: - Outlier detection and data freshness CTEs are computed but not included in the final UNION, so they do not appear in the output. - DuckDB coerces types across the UNION by position: columns 2 and 6 are VARCHAR; columns 3–5 are FLOAT; NULLs are preserved.'

SQL原处：

`data/019_work/impl-002_int_pendo__data_quality_checks/baseline.sql`，第 1–1 行：

```sql
TIMESTAMPTZ '2025-10-11 14:44:19.830000+08:00' calculated_at
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__data_quality_checks.json#completeness_account`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 13/63 | 12/58 | 1/5 |
| L1 | 13/63 | 12/58 | 1/5 |
| L2 | 13/63 | 12/58 | 1/5 |
| L3 | 13/63 | 12/58 | 1/5 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> the data-quality report is summary-only;

交付报告明确点到这张表/这类指标及其占位或选择。

### completeness_visitor

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

只补一条缺失详情行；沿契约的UNION按位置映射，不改summary。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build a four-section report by computing intermediate checks and then UNION ALLing section-specific rows (column meanings vary by section; see column rules below). No output ordering is enforced. All timestamps use current_timestamp at query time. 1) Data completeness checks: - account_history: total records; count of NULL account_id; count of NULL first_visit_at; count of NULL last_visit_at; other counts set to 0. - visitor_history: total records; count of NULL visitor_id; other counts set to 0; sixth position is count of NULL account_id. - event: total records; second–sixth positions respectively count NULL visitor_id, NULL account_id, NULL occurred_at, NULL app_id, and count of num_events that are NULL or negative. - Later UNIONs align values by position from the first select’s column order. 2) Data consistency checks: five issue types with counts and descriptions: - timestamp_consistency: events with occurred_at in the future. - account_visitor_relationship: visitor_history rows whose non-NULL account_id does not exist in account_history. - event_visitor_relationship: events whose visitor_id does not exist in visitor_history. - negative_metrics: events with negative num_minutes or num_events. - chronological_consistency: accounts where first_visit_at and last_visit_at are both present and first_visit_at is after last_visit_at. 3) Business logic violations: four rules with counts and descriptions: - impossible_session_duration: events with num_minutes > 480. - excessive_daily_events: per visitor and day, sum num_events; count groups with sum > 10000. - duplicate_primary_keys: difference between total events and distinct event_key. - inactive_paying_accounts: accounts with no events in the last 90 days. 4) Summary quality metrics: - completeness_score: compute the share of complete records by subtracting the ratio of (sum of NULL primary keys + sum of missing names + sum of missing first visits) to (three times the sum of total records) from 1, then multiply by 100; return NULL if the denominator is zero. - consistency_score: compute 1 minus the ratio of total consistency violations to the overall total records, then multiply by 100; return NULL if the denominator is zero. - business_logic_score: compute 1 minus the ratio of total business logic violations to the overall total records, then multiply by 100; return NULL if the denominator is zero. - These totals are evaluated over a Cartesian product of the completeness, consistency, and business-logic CTEs, so each component’s sum is multiplied by the row counts of the other two CTEs. - calculated_at uses the current time. 5) Final UNION ALL report rows: - Data Quality Summary: 1 row with the three percentage scores; overall_quality_score is their average; quality_grade is Excellent (>=95), Good (>=85), Fair (>=70), else Poor; calculated_at from the summary CTE. - Data Completeness Details: one row per table_name with column mapping by position: table_name (text), total_records, null_primary_keys, missing_names, missing_first_visit (as text), and calculated_at as current time. - Data Consistency Issues: one row per check_type with column mapping by position: check_type (text), total_violations, NULL, NULL, violation_description (text), and calculated_at as current time. - Business Logic Violations: one row per violation_type with column mapping by position: violation_type (text), violation_count, NULL, NULL, description (text), and calculated_at as current time. Notes: - Outlier detection and data freshness CTEs are computed but not included in the final UNION, so they do not appear in the output. - DuckDB coerces types across the UNION by position: columns 2 and 6 are VARCHAR; columns 3–5 are FLOAT; NULLs are preserved.'

SQL原处：

`data/019_work/impl-002_int_pendo__data_quality_checks/baseline.sql`，第 1–1 行：

```sql
TIMESTAMPTZ '2025-10-11 14:44:19.830000+08:00' calculated_at
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__data_quality_checks.json#completeness_visitor`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 13/63 | 12/58 | 1/5 |
| L1 | 13/63 | 12/58 | 1/5 |
| L2 | 13/63 | 12/58 | 1/5 |
| L3 | 13/63 | 12/58 | 1/5 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> the data-quality report is summary-only;

交付报告明确点到这张表/这类指标及其占位或选择。

### consistency_details

- 类别：已说出的降级；角色：主要；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

一处恢复整段缺失报告章节；只读原staging，不更改summary。未评分的说明文字只作可读表达。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build a four-section report by computing intermediate checks and then UNION ALLing section-specific rows (column meanings vary by section; see column rules below). No output ordering is enforced. All timestamps use current_timestamp at query time. 1) Data completeness checks: - account_history: total records; count of NULL account_id; count of NULL first_visit_at; count of NULL last_visit_at; other counts set to 0. - visitor_history: total records; count of NULL visitor_id; other counts set to 0; sixth position is count of NULL account_id. - event: total records; second–sixth positions respectively count NULL visitor_id, NULL account_id, NULL occurred_at, NULL app_id, and count of num_events that are NULL or negative. - Later UNIONs align values by position from the first select’s column order. 2) Data consistency checks: five issue types with counts and descriptions: - timestamp_consistency: events with occurred_at in the future. - account_visitor_relationship: visitor_history rows whose non-NULL account_id does not exist in account_history. - event_visitor_relationship: events whose visitor_id does not exist in visitor_history. - negative_metrics: events with negative num_minutes or num_events. - chronological_consistency: accounts where first_visit_at and last_visit_at are both present and first_visit_at is after last_visit_at. 3) Business logic violations: four rules with counts and descriptions: - impossible_session_duration: events with num_minutes > 480. - excessive_daily_events: per visitor and day, sum num_events; count groups with sum > 10000. - duplicate_primary_keys: difference between total events and distinct event_key. - inactive_paying_accounts: accounts with no events in the last 90 days. 4) Summary quality metrics: - completeness_score: compute the share of complete records by subtracting the ratio of (sum of NULL primary keys + sum of missing names + sum of missing first visits) to (three times the sum of total records) from 1, then multiply by 100; return NULL if the denominator is zero. - consistency_score: compute 1 minus the ratio of total consistency violations to the overall total records, then multiply by 100; return NULL if the denominator is zero. - business_logic_score: compute 1 minus the ratio of total business logic violations to the overall total records, then multiply by 100; return NULL if the denominator is zero. - These totals are evaluated over a Cartesian product of the completeness, consistency, and business-logic CTEs, so each component’s sum is multiplied by the row counts of the other two CTEs. - calculated_at uses the current time. 5) Final UNION ALL report rows: - Data Quality Summary: 1 row with the three percentage scores; overall_quality_score is their average; quality_grade is Excellent (>=95), Good (>=85), Fair (>=70), else Poor; calculated_at from the summary CTE. - Data Completeness Details: one row per table_name with column mapping by position: table_name (text), total_records, null_primary_keys, missing_names, missing_first_visit (as text), and calculated_at as current time. - Data Consistency Issues: one row per check_type with column mapping by position: check_type (text), total_violations, NULL, NULL, violation_description (text), and calculated_at as current time. - Business Logic Violations: one row per violation_type with column mapping by position: violation_type (text), violation_count, NULL, NULL, description (text), and calculated_at as current time. Notes: - Outlier detection and data freshness CTEs are computed but not included in the final UNION, so they do not appear in the output. - DuckDB coerces types across the UNION by position: columns 2 and 6 are VARCHAR; columns 3–5 are FLOAT; NULLs are preserved.'

SQL原处：

`data/019_work/impl-002_int_pendo__data_quality_checks/baseline.sql`，第 1–1 行：

```sql
TIMESTAMPTZ '2025-10-11 14:44:19.830000+08:00' calculated_at
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__data_quality_checks.json#consistency_details`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 13/63 | 8/38 | 5/25 |
| L1 | 13/63 | 8/38 | 5/25 |
| L2 | 13/63 | 8/38 | 5/25 |
| L3 | 13/63 | 8/38 | 5/25 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> the data-quality report is summary-only;

交付报告明确点到这张表/这类指标及其占位或选择。

### business_details

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

一处恢复整段缺失报告章节；只读原staging，不更改summary。未评分的说明文字只作可读表达。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build a four-section report by computing intermediate checks and then UNION ALLing section-specific rows (column meanings vary by section; see column rules below). No output ordering is enforced. All timestamps use current_timestamp at query time. 1) Data completeness checks: - account_history: total records; count of NULL account_id; count of NULL first_visit_at; count of NULL last_visit_at; other counts set to 0. - visitor_history: total records; count of NULL visitor_id; other counts set to 0; sixth position is count of NULL account_id. - event: total records; second–sixth positions respectively count NULL visitor_id, NULL account_id, NULL occurred_at, NULL app_id, and count of num_events that are NULL or negative. - Later UNIONs align values by position from the first select’s column order. 2) Data consistency checks: five issue types with counts and descriptions: - timestamp_consistency: events with occurred_at in the future. - account_visitor_relationship: visitor_history rows whose non-NULL account_id does not exist in account_history. - event_visitor_relationship: events whose visitor_id does not exist in visitor_history. - negative_metrics: events with negative num_minutes or num_events. - chronological_consistency: accounts where first_visit_at and last_visit_at are both present and first_visit_at is after last_visit_at. 3) Business logic violations: four rules with counts and descriptions: - impossible_session_duration: events with num_minutes > 480. - excessive_daily_events: per visitor and day, sum num_events; count groups with sum > 10000. - duplicate_primary_keys: difference between total events and distinct event_key. - inactive_paying_accounts: accounts with no events in the last 90 days. 4) Summary quality metrics: - completeness_score: compute the share of complete records by subtracting the ratio of (sum of NULL primary keys + sum of missing names + sum of missing first visits) to (three times the sum of total records) from 1, then multiply by 100; return NULL if the denominator is zero. - consistency_score: compute 1 minus the ratio of total consistency violations to the overall total records, then multiply by 100; return NULL if the denominator is zero. - business_logic_score: compute 1 minus the ratio of total business logic violations to the overall total records, then multiply by 100; return NULL if the denominator is zero. - These totals are evaluated over a Cartesian product of the completeness, consistency, and business-logic CTEs, so each component’s sum is multiplied by the row counts of the other two CTEs. - calculated_at uses the current time. 5) Final UNION ALL report rows: - Data Quality Summary: 1 row with the three percentage scores; overall_quality_score is their average; quality_grade is Excellent (>=95), Good (>=85), Fair (>=70), else Poor; calculated_at from the summary CTE. - Data Completeness Details: one row per table_name with column mapping by position: table_name (text), total_records, null_primary_keys, missing_names, missing_first_visit (as text), and calculated_at as current time. - Data Consistency Issues: one row per check_type with column mapping by position: check_type (text), total_violations, NULL, NULL, violation_description (text), and calculated_at as current time. - Business Logic Violations: one row per violation_type with column mapping by position: violation_type (text), violation_count, NULL, NULL, description (text), and calculated_at as current time. Notes: - Outlier detection and data freshness CTEs are computed but not included in the final UNION, so they do not appear in the output. - DuckDB coerces types across the UNION by position: columns 2 and 6 are VARCHAR; columns 3–5 are FLOAT; NULLs are preserved.'

SQL原处：

`data/019_work/impl-002_int_pendo__data_quality_checks/baseline.sql`，第 1–1 行：

```sql
TIMESTAMPTZ '2025-10-11 14:44:19.830000+08:00' calculated_at
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__data_quality_checks.json#business_details`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 13/63 | 9/43 | 4/20 |
| L1 | 13/63 | 9/43 | 4/20 |
| L2 | 13/63 | 9/43 | 4/20 |
| L3 | 13/63 | 9/43 | 4/20 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> the data-quality report is summary-only;

交付报告明确点到这张表/这类指标及其占位或选择。

### consistency_score

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

仅恢复一个summary聚合值；笛卡尔积权重按契约3×5×4，不改变其他NULL列。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: consistency_score
>         data_type: FLOAT
>         description: 'Numeric metric by section: summary shows the consistency percentage; completeness details show total_records; consistency issues show total_violations; business logic violations show violation_count.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__data_quality_checks.sql`，第 1–1 行：

```sql
NULL::FLOAT consistency_score
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__data_quality_checks.json#consistency_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 13/63 | 13/63 | 0/0 |
| L1 | 13/63 | 13/63 | 0/0 |
| L2 | 13/63 | 13/63 | 0/0 |
| L3 | 13/63 | 13/63 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> the data-quality report is summary-only;

交付报告明确点到这张表/这类指标及其占位或选择。

### business_logic_score

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

仅恢复一个summary聚合值；笛卡尔积权重按契约3×5×4，不改变其他NULL列。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: business_logic_score
>         data_type: FLOAT
>         description: 'Numeric metric by section: summary shows the business logic percentage; completeness details show null_primary_keys; consistency issues and business logic violations are NULL.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__data_quality_checks.sql`，第 1–1 行：

```sql
NULL::FLOAT business_logic_score
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__data_quality_checks.json#business_logic_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 13/63 | 13/63 | 0/0 |
| L1 | 13/63 | 13/63 | 0/0 |
| L2 | 13/63 | 13/63 | 0/0 |
| L3 | 13/63 | 13/63 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> the data-quality report is summary-only;

交付报告明确点到这张表/这类指标及其占位或选择。

### completeness_score

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复summary完整度公式；该列不在本表官方比较列中，须明确非原因。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: completeness_score
>         data_type: VARCHAR
>         description: 'Section-dependent text: summary shows the completeness percentage as text (no explicit rounding); completeness details show table_name; consistency issues show check_type; business logic violations show violation_type; summary can be NULL if the denominator is zero.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__data_quality_checks.sql`，第 1–1 行：

```sql
NULL::VARCHAR completeness_score
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__data_quality_checks.json#completeness_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 13/63 | 13/63 | 0/0 |
| L1 | 13/63 | 13/63 | 0/0 |
| L2 | 13/63 | 13/63 | 0/0 |
| L3 | 13/63 | 13/63 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> the data-quality report is summary-only;

交付报告明确点到这张表/这类指标及其占位或选择。

### overall_quality_score

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复三分数平均，其他列仍保留NULL；遮蔽下允许净改善0。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: overall_quality_score
>         data_type: FLOAT
>         description: 'Numeric metric by section: summary is the average of the three percentage scores; completeness details show missing_names; consistency issues and business logic violations are NULL.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__data_quality_checks.sql`，第 1–1 行：

```sql
NULL::FLOAT overall_quality_score
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__data_quality_checks.json#overall_quality_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 13/63 | 13/63 | 0/0 |
| L1 | 13/63 | 13/63 | 0/0 |
| L2 | 13/63 | 13/63 | 0/0 |
| L3 | 13/63 | 13/63 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> the data-quality report is summary-only;

交付报告明确点到这张表/这类指标及其占位或选择。

### quality_grade

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复等级分支，输入仍为原NULL；该列不在官方比较列中。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: quality_grade
>         data_type: VARCHAR
>         description: 'Section-dependent text: summary grade (Excellent/Good/Fair/Poor using thresholds 95/85/70); completeness details show missing_first_visit as text; consistency issues show violation_description; business logic violations show description.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__data_quality_checks.sql`，第 1–1 行：

```sql
'Poor'::VARCHAR quality_grade
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__data_quality_checks.json#quality_grade`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 13/63 | 13/63 | 0/0 |
| L1 | 13/63 | 13/63 | 0/0 |
| L2 | 13/63 | 13/63 | 0/0 |
| L3 | 13/63 | 13/63 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> the data-quality report is summary-only;

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

不确定：部分恢复公式的干预在其他默认输入仍错误时不能对齐gold，甚至增加差异；保留非原因而不外推整套模型已修复。恢复条件的文字代表若契约未固定，只用于测量，不能反过来当契约。
