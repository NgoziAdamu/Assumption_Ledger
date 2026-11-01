# impl-009_int_google_play__app_quality_metrics（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**已说出的降级**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 2928, "cell_scale": 10884}, "L1": {"row_scale": 2928, "cell_scale": 10884}, "L2": {"row_scale": 2928, "cell_scale": 10884}, "L3": {"row_scale": 2928, "cell_scale": 10884}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| avg_7d_crashes | 已说出的降级 | 并列 | 0 | 2928 | 1 |
| avg_7d_anrs | 已说出的降级 | 并列 | 0 | 2928 | 1 |
| active_versions_count | 已说出的降级 | 参与 | 0 | 272 | 1 |
| supported_os_versions | 已说出的降级 | 参与 | 0 | 272 | 1 |
| version_with_most_crashes | 已说出的降级 | 参与 | 0 | 271 | 1 |
| os_with_most_crashes | 已说出的降级 | 参与 | 0 | 270 | 1 |
| worst_version_crashes | 已说出的降级 | 参与 | 0 | 271 | 1 |
| worst_version_anrs | 已说出的降级 | 参与 | 0 | 271 | 1 |
| worst_os_crashes | 已说出的降级 | 参与 | 0 | 270 | 1 |
| worst_os_anrs | 已说出的降级 | 参与 | 0 | 270 | 1 |
| stability_trend | 已说出的降级 | 参与 | 0 | 2852 | 1 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: int_google_play__app_quality_metrics
      description: Daily Google Play app stability and quality metrics per package (crashes, ANRs, rates, rolling averages, fragmentation, scoring, trend, category, and risk)
      grain: One row per package_name per date_day (driven by crashes_overview)
      source_models:
      - staging.stg_google_play__stats_crashes_overview
      - staging.stg_google_play__stats_crashes_app_version
      - staging.stg_google_play__stats_crashes_os_version
      - staging.stg_google_play__stats_installs_overview
      - staging.stg_google_play__stats_ratings_overview
      business_logic: '- Filter sources to valid ranges: - crashes_overview, crashes_by_version, crashes_by_os: keep rows with crashes >= 0 and ANRs >= 0. - installs_overview: keep rows with daily_device_installs >= 0 and active_device_installs >= 0. - ratings_overview: keep rows with daily_average_rating and total_average_rating between 1.0 and 5.0. - Build stability_metrics per (package_name, date_day) from crashes_overview: - Left join installs_overview and ratings_overview by (date_day, package_name). - crash_rate_per_1k_devices: daily_crashes divided by active_device_installs, scaled to per 1,000 devices, rounded to 4 decimals; only when active_device_installs > 0, otherwise NULL. - anr_rate_per_1k_devices: daily_anrs divided by active_device_installs, scaled to per 1,000 devices, rounded to 4 decimals; only when active_device_installs > 0, otherwise NULL. - total_stability_issues = daily_crashes + daily_anrs. - Rolling 7-day averages per package_name ordered by date_day using a window that includes the current day and up to the prior 6 days: - avg_7d_crashes and avg_7d_anrs average the available daily values; inputs are non-NULL so these averages are defined. - avg_7d_rating averages available non-NULL ratings; returns NULL when no ratings exist in the window. - Version fragmentation: - active_versions_count: count distinct app_version_code from crashes_by_version per (date_day, package_name); NULL when no version data exists. - version_with_most_crashes: select the app_version_code with the highest sum of crashes + ANRs on that day; ties follow default engine ordering; associated crashes and ANRs are reported. - OS fragmentation: - supported_os_versions: count distinct android_os_version from crashes_by_os per (date_day, package_name); NULL when no OS data exists. - os_with_most_crashes: select the OS version with the highest sum of crashes + ANRs on that day; ties follow default engine ordering; associated crashes and ANRs are reported. - Quality scoring: - If daily_average_rating is NULL, quality_score is NULL. Otherwise compute points: - Rating: (daily_average_rating / 5) × 40. - Crash rate: 30 points if ≤1, 20 if ≤5, 10 if ≤10, else 0; NULL rate contributes 0. - ANR rate: 20 points if ≤1, 15 if ≤5, 10 if ≤10, else 0; NULL rate contributes 0. - Version fragmentation: 10 points if active_versions_count ≤3, 5 if ≤5, else 0; NULL contributes 0. - Sum points, clamp at a minimum of 0, and round to 2 decimals to produce quality_score. - Stability trend: - Compare avg_7d_crashes to the value 7 days earlier within the same package: if lower → Improving; if higher → Degrading; otherwise → Stable. If the prior value is missing, treat as Stable. - Final output: - Round avg_7d_crashes, avg_7d_anrs, avg_7d_rating to 2 decimals. - quality_category: Excellent (≥80), Good (≥65), Fair (≥50), Poor (≥35), Critical (<35 when not NULL), Unrated (NULL score). - stability_risk_level: High Risk if crash rate >20 or ANR rate >15; Medium Risk if >10 or >8; Low Risk if >5 or >3; otherwise Minimal Risk. NULL rates do not trigger thresholds. - Emit one row per (package_name, date_day) and remove rows where either key is NULL.'
      columns:
      - name: date_day
        data_type: DATE
        description: Metric date (UTC); exactly one output row per package_name per date_day
        tests:
        - not_null
      - name: package_name
        data_type: VARCHAR
        description: Google Play package identifier; grouping key with date_day
        tests:
        - not_null
      - name: daily_crashes
        data_type: BIGINT
        description: Number of crashes on date_day from crashes_overview; source rows require crashes >= 0
        tests:
        - not_null
      - name: daily_anrs
        data_type: BIGINT
        description: Number of ANRs on date_day from crashes_overview; source rows require anrs >= 0
        tests:
        - not_null
      - name: total_stability_issues
        data_type: BIGINT
        description: Sum of daily_crashes + daily_anrs for the day; always >= 0
        tests:
        - not_null
      - name: crash_rate_per_1k_devices
        data_type: DOUBLE
        description: Daily crashes per 1,000 active devices; computed only when active_device_installs > 0; rounded to 4 decimals; else NULL
        tests: []
      - name: anr_rate_per_1k_devices
        data_type: DOUBLE
        description: Daily ANRs per 1,000 active devices; computed only when active_device_installs > 0; rounded to 4 decimals; else NULL
        tests: []
      - name: avg_7d_crashes
        data_type: DOUBLE
        description: 7-day rolling average of daily_crashes per package_name ordered by date_day (current day plus up to 6 prior days); rounded to 2 decimals; never NULL
        tests: []
      - name: avg_7d_anrs
        data_type: DOUBLE
        description: 7-day rolling average of daily_anrs per package_name ordered by date_day (current day plus up to 6 prior days); rounded to 2 decimals; never NULL
        tests: []
      - name: avg_7d_rating
        data_type: DOUBLE
        description: 7-day rolling average of daily_average_rating using non-NULL values only; NULL if window has no ratings; rounded to 2 decimals
        tests: []
      - name: active_versions_count
        data_type: BIGINT
        description: Count of distinct app_version_code with non-negative metrics on date_day; NULL if no version data
        tests: []
      - name: version_with_most_crashes
        data_type: VARCHAR
        description: App version_code with highest total of crashes + ANRs on date_day; ties resolved by engine-default order; NULL if no version data
        tests: []
      - name: worst_version_crashes
        data_type: BIGINT
        description: Crashes for version_with_most_crashes on date_day; NULL if no version selected
        tests: []
      - name: worst_version_anrs
        data_type: BIGINT
        description: ANRs for version_with_most_crashes on date_day; NULL if no version selected
        tests: []
      - name: supported_os_versions
        data_type: BIGINT
        description: Count of distinct android_os_version with non-negative metrics on date_day; NULL if no OS data
        tests: []
      - name: os_with_most_crashes
        data_type: VARCHAR
        description: Android OS version with highest total of crashes + ANRs on date_day; ties resolved by engine-default order; NULL if no OS data
        tests: []
      - name: worst_os_crashes
        data_type: BIGINT
        description: Crashes for os_with_most_crashes on date_day; NULL if no OS selected
        tests: []
      - name: worst_os_anrs
        data_type: BIGINT
        description: ANRs for os_with_most_crashes on date_day; NULL if no OS selected
        tests: []
      - name: quality_score
        data_type: DOUBLE
        description: Weighted score (0–100) combining rating (40%), crash rate (30%), ANR rate (20%), and version fragmentation (10); NULL rates or counts contribute 0; rounded to 2 decimals; NULL if daily_average_rating is NULL
        tests: []
      - name: stability_trend
        data_type: VARCHAR
        description: 'Trend vs the value 7 days earlier using avg_7d_crashes: Improving if lower, Degrading if higher, else Stable; missing prior value treated as Stable'
        tests:
        - not_null
        - in_set('Improving','Degrading','Stable')
      - name: quality_category
        data_type: VARCHAR
        description: 'Category from quality_score: Excellent (≥80), Good (≥65), Fair (≥50), Poor (≥35), Critical (<35 and not NULL), Unrated (quality_score NULL)'
        tests:
        - not_null
        - in_set('Excellent','Good','Fair','Poor','Critical','Unrated')
      - name: stability_risk_level
        data_type: VARCHAR
        description: 'Risk from crash/anr rates: High Risk (>20 or >15), Medium Risk (>10 or >8), Low Risk (>5 or >3), else Minimal Risk; NULL rates do not trigger thresholds'
        tests:
        - not_null
        - in_set('High Risk','Medium Risk','Low Risk','Minimal Risk')
```

### 逐点结论

#### avg_7d_crashes

并列；**已说出的降级**；把握高。

avg_7d_crashes直接NULL，省略已有CS crashes/anrs序列上的7日窗口。finish的app quality一一对应本表，且明说窗口未实现及NULL占位。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 7956 |
| L1 | 2928 | 2928 | 10884 | 7956 |
| L2 | 2928 | 2928 | 10884 | 7956 |
| L3 | 2928 | 2928 | 10884 | 7956 |

重跑：`records/021_extra_reruns_impl-009_int_google_play__app_quality_metrics.json` / `avg_7d_crashes`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
CAST(NULL AS DOUBLE) AS avg_7d_crashes
```

#### avg_7d_anrs

并列；**已说出的降级**；把握高。

avg_7d_anrs直接NULL，省略已有CS crashes/anrs序列上的7日窗口。finish的app quality一一对应本表，且明说窗口未实现及NULL占位。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 7956 |
| L1 | 2928 | 2928 | 10884 | 7956 |
| L2 | 2928 | 2928 | 10884 | 7956 |
| L3 | 2928 | 2928 | 10884 | 7956 |

重跑：`records/021_extra_reruns_impl-009_int_google_play__app_quality_metrics.json` / `avg_7d_anrs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
CAST(NULL AS DOUBLE) AS avg_7d_anrs
```

#### active_versions_count

参与；**已说出的降级**；把握高。

active_versions_count为占位NULL/常量，未使用现有版本、系统及崩溃统计完成计数、最差项选择或趋势。每列独立恢复从CS重算的值；未将整表恢复规模分摊。finish明确点名app quality。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 10612 |
| L1 | 2928 | 2928 | 10884 | 10612 |
| L2 | 2928 | 2928 | 10884 | 10612 |
| L3 | 2928 | 2928 | 10884 | 10612 |

重跑：`records/039_checks/supplement_impl-009_int_google_play__app_quality_metrics.json` / `active_versions_count`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
SELECT
CAST(date_day AS DATE) AS date_day,
CAST(package_name AS VARCHAR) AS package_name,
CAST(crashes AS BIGINT) AS daily_crashes,
CAST(anrs AS BIGINT) AS daily_anrs,
CAST(coalesce(crashes,0)+coalesce(anrs,0) AS BIGINT) AS total_stability_issues,
CAST(NULL AS DOUBLE) AS crash_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS anr_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS avg_7d_crashes,
CAST(NULL AS DOUBLE) AS avg_7d_anrs,
CAST(NULL AS DOUBLE) AS avg_7d_rating,
CAST(NULL AS BIGINT) AS active_versions_count,
CAST(NULL AS VARCHAR) AS version_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_version_crashes,
CAST(NULL AS BIGINT) AS worst_version_anrs,
CAST(NULL AS BIGINT) AS supported_os_versions,
CAST(NULL AS VARCHAR) AS os_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_os_crashes,
CAST(NULL AS BIGINT) AS worst_os_anrs,
CAST(NULL AS DOUBLE) AS quality_score,
CAST('Stable' AS VARCHAR) AS stability_trend,
CAST('Unrated' AS VARCHAR) AS quality_category,
CAST('Minimal Risk' AS VARCHAR) AS stability_risk_level
FROM staging.stg_google_play__stats_crashes_overview WHERE crashes>=0 AND anrs>=0 AND date_day IS NOT NULL AND package_name IS NOT NULL

```

#### supported_os_versions

参与；**已说出的降级**；把握高。

supported_os_versions为占位NULL/常量，未使用现有版本、系统及崩溃统计完成计数、最差项选择或趋势。每列独立恢复从CS重算的值；未将整表恢复规模分摊。finish明确点名app quality。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 10612 |
| L1 | 2928 | 2928 | 10884 | 10612 |
| L2 | 2928 | 2928 | 10884 | 10612 |
| L3 | 2928 | 2928 | 10884 | 10612 |

重跑：`records/039_checks/supplement_impl-009_int_google_play__app_quality_metrics.json` / `supported_os_versions`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
SELECT
CAST(date_day AS DATE) AS date_day,
CAST(package_name AS VARCHAR) AS package_name,
CAST(crashes AS BIGINT) AS daily_crashes,
CAST(anrs AS BIGINT) AS daily_anrs,
CAST(coalesce(crashes,0)+coalesce(anrs,0) AS BIGINT) AS total_stability_issues,
CAST(NULL AS DOUBLE) AS crash_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS anr_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS avg_7d_crashes,
CAST(NULL AS DOUBLE) AS avg_7d_anrs,
CAST(NULL AS DOUBLE) AS avg_7d_rating,
CAST(NULL AS BIGINT) AS active_versions_count,
CAST(NULL AS VARCHAR) AS version_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_version_crashes,
CAST(NULL AS BIGINT) AS worst_version_anrs,
CAST(NULL AS BIGINT) AS supported_os_versions,
CAST(NULL AS VARCHAR) AS os_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_os_crashes,
CAST(NULL AS BIGINT) AS worst_os_anrs,
CAST(NULL AS DOUBLE) AS quality_score,
CAST('Stable' AS VARCHAR) AS stability_trend,
CAST('Unrated' AS VARCHAR) AS quality_category,
CAST('Minimal Risk' AS VARCHAR) AS stability_risk_level
FROM staging.stg_google_play__stats_crashes_overview WHERE crashes>=0 AND anrs>=0 AND date_day IS NOT NULL AND package_name IS NOT NULL

```

#### version_with_most_crashes

参与；**已说出的降级**；把握高。

version_with_most_crashes为占位NULL/常量，未使用现有版本、系统及崩溃统计完成计数、最差项选择或趋势。每列独立恢复从CS重算的值；未将整表恢复规模分摊。finish明确点名app quality。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 10613 |
| L1 | 2928 | 2928 | 10884 | 10613 |
| L2 | 2928 | 2928 | 10884 | 10613 |
| L3 | 2928 | 2928 | 10884 | 10613 |

重跑：`records/039_checks/supplement_impl-009_int_google_play__app_quality_metrics.json` / `version_with_most_crashes`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
SELECT
CAST(date_day AS DATE) AS date_day,
CAST(package_name AS VARCHAR) AS package_name,
CAST(crashes AS BIGINT) AS daily_crashes,
CAST(anrs AS BIGINT) AS daily_anrs,
CAST(coalesce(crashes,0)+coalesce(anrs,0) AS BIGINT) AS total_stability_issues,
CAST(NULL AS DOUBLE) AS crash_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS anr_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS avg_7d_crashes,
CAST(NULL AS DOUBLE) AS avg_7d_anrs,
CAST(NULL AS DOUBLE) AS avg_7d_rating,
CAST(NULL AS BIGINT) AS active_versions_count,
CAST(NULL AS VARCHAR) AS version_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_version_crashes,
CAST(NULL AS BIGINT) AS worst_version_anrs,
CAST(NULL AS BIGINT) AS supported_os_versions,
CAST(NULL AS VARCHAR) AS os_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_os_crashes,
CAST(NULL AS BIGINT) AS worst_os_anrs,
CAST(NULL AS DOUBLE) AS quality_score,
CAST('Stable' AS VARCHAR) AS stability_trend,
CAST('Unrated' AS VARCHAR) AS quality_category,
CAST('Minimal Risk' AS VARCHAR) AS stability_risk_level
FROM staging.stg_google_play__stats_crashes_overview WHERE crashes>=0 AND anrs>=0 AND date_day IS NOT NULL AND package_name IS NOT NULL

```

#### os_with_most_crashes

参与；**已说出的降级**；把握高。

os_with_most_crashes为占位NULL/常量，未使用现有版本、系统及崩溃统计完成计数、最差项选择或趋势。每列独立恢复从CS重算的值；未将整表恢复规模分摊。finish明确点名app quality。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 10614 |
| L1 | 2928 | 2928 | 10884 | 10614 |
| L2 | 2928 | 2928 | 10884 | 10614 |
| L3 | 2928 | 2928 | 10884 | 10614 |

重跑：`records/039_checks/supplement_impl-009_int_google_play__app_quality_metrics.json` / `os_with_most_crashes`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
SELECT
CAST(date_day AS DATE) AS date_day,
CAST(package_name AS VARCHAR) AS package_name,
CAST(crashes AS BIGINT) AS daily_crashes,
CAST(anrs AS BIGINT) AS daily_anrs,
CAST(coalesce(crashes,0)+coalesce(anrs,0) AS BIGINT) AS total_stability_issues,
CAST(NULL AS DOUBLE) AS crash_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS anr_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS avg_7d_crashes,
CAST(NULL AS DOUBLE) AS avg_7d_anrs,
CAST(NULL AS DOUBLE) AS avg_7d_rating,
CAST(NULL AS BIGINT) AS active_versions_count,
CAST(NULL AS VARCHAR) AS version_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_version_crashes,
CAST(NULL AS BIGINT) AS worst_version_anrs,
CAST(NULL AS BIGINT) AS supported_os_versions,
CAST(NULL AS VARCHAR) AS os_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_os_crashes,
CAST(NULL AS BIGINT) AS worst_os_anrs,
CAST(NULL AS DOUBLE) AS quality_score,
CAST('Stable' AS VARCHAR) AS stability_trend,
CAST('Unrated' AS VARCHAR) AS quality_category,
CAST('Minimal Risk' AS VARCHAR) AS stability_risk_level
FROM staging.stg_google_play__stats_crashes_overview WHERE crashes>=0 AND anrs>=0 AND date_day IS NOT NULL AND package_name IS NOT NULL

```

#### worst_version_crashes

参与；**已说出的降级**；把握高。

worst_version_crashes为占位NULL/常量，未使用现有版本、系统及崩溃统计完成计数、最差项选择或趋势。每列独立恢复从CS重算的值；未将整表恢复规模分摊。finish明确点名app quality。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 10613 |
| L1 | 2928 | 2928 | 10884 | 10613 |
| L2 | 2928 | 2928 | 10884 | 10613 |
| L3 | 2928 | 2928 | 10884 | 10613 |

重跑：`records/039_checks/supplement_impl-009_int_google_play__app_quality_metrics.json` / `worst_version_crashes`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
SELECT
CAST(date_day AS DATE) AS date_day,
CAST(package_name AS VARCHAR) AS package_name,
CAST(crashes AS BIGINT) AS daily_crashes,
CAST(anrs AS BIGINT) AS daily_anrs,
CAST(coalesce(crashes,0)+coalesce(anrs,0) AS BIGINT) AS total_stability_issues,
CAST(NULL AS DOUBLE) AS crash_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS anr_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS avg_7d_crashes,
CAST(NULL AS DOUBLE) AS avg_7d_anrs,
CAST(NULL AS DOUBLE) AS avg_7d_rating,
CAST(NULL AS BIGINT) AS active_versions_count,
CAST(NULL AS VARCHAR) AS version_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_version_crashes,
CAST(NULL AS BIGINT) AS worst_version_anrs,
CAST(NULL AS BIGINT) AS supported_os_versions,
CAST(NULL AS VARCHAR) AS os_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_os_crashes,
CAST(NULL AS BIGINT) AS worst_os_anrs,
CAST(NULL AS DOUBLE) AS quality_score,
CAST('Stable' AS VARCHAR) AS stability_trend,
CAST('Unrated' AS VARCHAR) AS quality_category,
CAST('Minimal Risk' AS VARCHAR) AS stability_risk_level
FROM staging.stg_google_play__stats_crashes_overview WHERE crashes>=0 AND anrs>=0 AND date_day IS NOT NULL AND package_name IS NOT NULL

```

#### worst_version_anrs

参与；**已说出的降级**；把握高。

worst_version_anrs为占位NULL/常量，未使用现有版本、系统及崩溃统计完成计数、最差项选择或趋势。每列独立恢复从CS重算的值；未将整表恢复规模分摊。finish明确点名app quality。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 10613 |
| L1 | 2928 | 2928 | 10884 | 10613 |
| L2 | 2928 | 2928 | 10884 | 10613 |
| L3 | 2928 | 2928 | 10884 | 10613 |

重跑：`records/039_checks/supplement_impl-009_int_google_play__app_quality_metrics.json` / `worst_version_anrs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
SELECT
CAST(date_day AS DATE) AS date_day,
CAST(package_name AS VARCHAR) AS package_name,
CAST(crashes AS BIGINT) AS daily_crashes,
CAST(anrs AS BIGINT) AS daily_anrs,
CAST(coalesce(crashes,0)+coalesce(anrs,0) AS BIGINT) AS total_stability_issues,
CAST(NULL AS DOUBLE) AS crash_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS anr_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS avg_7d_crashes,
CAST(NULL AS DOUBLE) AS avg_7d_anrs,
CAST(NULL AS DOUBLE) AS avg_7d_rating,
CAST(NULL AS BIGINT) AS active_versions_count,
CAST(NULL AS VARCHAR) AS version_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_version_crashes,
CAST(NULL AS BIGINT) AS worst_version_anrs,
CAST(NULL AS BIGINT) AS supported_os_versions,
CAST(NULL AS VARCHAR) AS os_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_os_crashes,
CAST(NULL AS BIGINT) AS worst_os_anrs,
CAST(NULL AS DOUBLE) AS quality_score,
CAST('Stable' AS VARCHAR) AS stability_trend,
CAST('Unrated' AS VARCHAR) AS quality_category,
CAST('Minimal Risk' AS VARCHAR) AS stability_risk_level
FROM staging.stg_google_play__stats_crashes_overview WHERE crashes>=0 AND anrs>=0 AND date_day IS NOT NULL AND package_name IS NOT NULL

```

#### worst_os_crashes

参与；**已说出的降级**；把握高。

worst_os_crashes为占位NULL/常量，未使用现有版本、系统及崩溃统计完成计数、最差项选择或趋势。每列独立恢复从CS重算的值；未将整表恢复规模分摊。finish明确点名app quality。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 10614 |
| L1 | 2928 | 2928 | 10884 | 10614 |
| L2 | 2928 | 2928 | 10884 | 10614 |
| L3 | 2928 | 2928 | 10884 | 10614 |

重跑：`records/039_checks/supplement_impl-009_int_google_play__app_quality_metrics.json` / `worst_os_crashes`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
SELECT
CAST(date_day AS DATE) AS date_day,
CAST(package_name AS VARCHAR) AS package_name,
CAST(crashes AS BIGINT) AS daily_crashes,
CAST(anrs AS BIGINT) AS daily_anrs,
CAST(coalesce(crashes,0)+coalesce(anrs,0) AS BIGINT) AS total_stability_issues,
CAST(NULL AS DOUBLE) AS crash_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS anr_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS avg_7d_crashes,
CAST(NULL AS DOUBLE) AS avg_7d_anrs,
CAST(NULL AS DOUBLE) AS avg_7d_rating,
CAST(NULL AS BIGINT) AS active_versions_count,
CAST(NULL AS VARCHAR) AS version_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_version_crashes,
CAST(NULL AS BIGINT) AS worst_version_anrs,
CAST(NULL AS BIGINT) AS supported_os_versions,
CAST(NULL AS VARCHAR) AS os_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_os_crashes,
CAST(NULL AS BIGINT) AS worst_os_anrs,
CAST(NULL AS DOUBLE) AS quality_score,
CAST('Stable' AS VARCHAR) AS stability_trend,
CAST('Unrated' AS VARCHAR) AS quality_category,
CAST('Minimal Risk' AS VARCHAR) AS stability_risk_level
FROM staging.stg_google_play__stats_crashes_overview WHERE crashes>=0 AND anrs>=0 AND date_day IS NOT NULL AND package_name IS NOT NULL

```

#### worst_os_anrs

参与；**已说出的降级**；把握高。

worst_os_anrs为占位NULL/常量，未使用现有版本、系统及崩溃统计完成计数、最差项选择或趋势。每列独立恢复从CS重算的值；未将整表恢复规模分摊。finish明确点名app quality。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 10614 |
| L1 | 2928 | 2928 | 10884 | 10614 |
| L2 | 2928 | 2928 | 10884 | 10614 |
| L3 | 2928 | 2928 | 10884 | 10614 |

重跑：`records/039_checks/supplement_impl-009_int_google_play__app_quality_metrics.json` / `worst_os_anrs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
SELECT
CAST(date_day AS DATE) AS date_day,
CAST(package_name AS VARCHAR) AS package_name,
CAST(crashes AS BIGINT) AS daily_crashes,
CAST(anrs AS BIGINT) AS daily_anrs,
CAST(coalesce(crashes,0)+coalesce(anrs,0) AS BIGINT) AS total_stability_issues,
CAST(NULL AS DOUBLE) AS crash_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS anr_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS avg_7d_crashes,
CAST(NULL AS DOUBLE) AS avg_7d_anrs,
CAST(NULL AS DOUBLE) AS avg_7d_rating,
CAST(NULL AS BIGINT) AS active_versions_count,
CAST(NULL AS VARCHAR) AS version_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_version_crashes,
CAST(NULL AS BIGINT) AS worst_version_anrs,
CAST(NULL AS BIGINT) AS supported_os_versions,
CAST(NULL AS VARCHAR) AS os_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_os_crashes,
CAST(NULL AS BIGINT) AS worst_os_anrs,
CAST(NULL AS DOUBLE) AS quality_score,
CAST('Stable' AS VARCHAR) AS stability_trend,
CAST('Unrated' AS VARCHAR) AS quality_category,
CAST('Minimal Risk' AS VARCHAR) AS stability_risk_level
FROM staging.stg_google_play__stats_crashes_overview WHERE crashes>=0 AND anrs>=0 AND date_day IS NOT NULL AND package_name IS NOT NULL

```

#### stability_trend

参与；**已说出的降级**；把握高。

stability_trend为占位NULL/常量，未使用现有版本、系统及崩溃统计完成计数、最差项选择或趋势。每列独立恢复从CS重算的值；未将整表恢复规模分摊。finish明确点名app quality。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 2928 | 10884 | 8032 |
| L1 | 2928 | 2928 | 10884 | 8032 |
| L2 | 2928 | 2928 | 10884 | 8032 |
| L3 | 2928 | 2928 | 10884 | 8032 |

重跑：`records/039_checks/supplement_impl-009_int_google_play__app_quality_metrics.json` / `stability_trend`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql` / `SQL.text`（sql）：

```text
SELECT
CAST(date_day AS DATE) AS date_day,
CAST(package_name AS VARCHAR) AS package_name,
CAST(crashes AS BIGINT) AS daily_crashes,
CAST(anrs AS BIGINT) AS daily_anrs,
CAST(coalesce(crashes,0)+coalesce(anrs,0) AS BIGINT) AS total_stability_issues,
CAST(NULL AS DOUBLE) AS crash_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS anr_rate_per_1k_devices,
CAST(NULL AS DOUBLE) AS avg_7d_crashes,
CAST(NULL AS DOUBLE) AS avg_7d_anrs,
CAST(NULL AS DOUBLE) AS avg_7d_rating,
CAST(NULL AS BIGINT) AS active_versions_count,
CAST(NULL AS VARCHAR) AS version_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_version_crashes,
CAST(NULL AS BIGINT) AS worst_version_anrs,
CAST(NULL AS BIGINT) AS supported_os_versions,
CAST(NULL AS VARCHAR) AS os_with_most_crashes,
CAST(NULL AS BIGINT) AS worst_os_crashes,
CAST(NULL AS BIGINT) AS worst_os_anrs,
CAST(NULL AS DOUBLE) AS quality_score,
CAST('Stable' AS VARCHAR) AS stability_trend,
CAST('Unrated' AS VARCHAR) AS quality_category,
CAST('Minimal Risk' AS VARCHAR) AS stability_risk_level
FROM staging.stg_google_play__stats_crashes_overview WHERE crashes>=0 AND anrs>=0 AND date_day IS NOT NULL AND package_name IS NOT NULL

```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，行[993, 1102]；材料包 `records/021_packages/021_impl-009_int_google_play__app_quality_metrics.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql`；SHA-256 `9eca93d98d48211f80bcb3e23d5f8610ed393bd7aa263775978bed8c7fee4de7`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / event 67。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共3条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 8，失败=True。
  - `records/021_supplement_queries.json` / index 9，失败=False。
  - `records/021_final_diagnostics.json` / index 3，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
