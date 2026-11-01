# impl-009_google_play__comprehensive_performance_dashboard（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Quiet Downgrade**；把握：中；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 3568, "cell_scale": 124880}, "L1": {"row_scale": 3568, "cell_scale": 124880}, "L2": {"row_scale": 3568, "cell_scale": 124880}, "L3": {"row_scale": 3568, "cell_scale": 124880}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| 同类缺口组：机械fallback投影 | Quiet Downgrade | 主要 | 3568 | 124880 | 2 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: google_play__comprehensive_performance_dashboard
      description: Daily Google Play app performance combining installs, stability, engagement, retention, revenue, store conversion, risk, and recommended actions.
      grain: One or more rows per date_day and package_name (rows can repeat when multiple countries exist for the same day and app).
      source_models:
      - intermediate.int_google_play__user_behavior_metrics
      - intermediate.int_google_play__revenue_analytics
      - intermediate.int_google_play__user_retention_analysis
      - mart.google_play__overview_report
      business_logic: 'Build user_behavior per date_day, package_name, and country by summing installs, uninstalls, and active devices, averaging churn and weekly installs, and counting distinct countries meeting engagement and growth conditions. Build revenue_performance per date_day and package_name by summing net revenue, transactions, and new subscriptions, averaging transaction value, refund rate, ARPU, and revenue health. Build retention_insights per package_name over the last 30 days by averaging day-1/7/30 retention and retention quality, and counting distinct countries with strong retention or high churn risk. Build overview_base per date_day and package_name by summing installs, uninstalls, crashes, ANRs, store acquisitions, and visitors, and averaging rating. Fully outer join these on date_day and package_name; for each metric, prefer overview_base where applicable, then user_behavior or revenue_performance, and default to 0 when unavailable (except conversion rate). Set default quality_score=75.0, crash_rate_per_1k=0.0, anr_rate_per_1k=0.0, and version_fragmentation=1. Compute store_conversion_rate only when visitors > 0 as acquisitions divided by visitors times 100, rounded to 2 decimals; otherwise NULL. Derive business_health_status with tiers: Thriving (installs > 2x uninstalls, quality >= 70, and revenue > 0), Healthy (installs > uninstalls, quality >= 50, and churn <= 0.10), Stable (installs >= uninstalls or quality >= 40), At Risk (quality >= 30), else Critical. Compute overall_performance_score (0–100) by adding points: installs activity (15 if installs > 0), quality (up to 20 by thresholds 80/60/40), rating (up to 15 by thresholds 4.5/4.0/3.5), retention via churn (up to 20 by thresholds 0.05/0.10/0.20), revenue (15 if revenue > 0), and store conversion (up to 15 by thresholds 5/2/1 percent); clamp to 0–100 and round to 2 decimals. Set growth_trend by comparing installs to the value 7 days earlier within the same package: Growing if higher, Declining if lower, else Stable (also Stable when no prior value). Compute install_uninstall_ratio as installs divided by uninstalls rounded to 2 decimals when uninstalls > 0; else NULL. Compute total_issues_per_1k_devices as (crashes + ANRs) per 1,000 active devices rounded to 2 decimals when active devices > 0; else NULL. Left join retention_insights by package_name so the same package-level 30-day averages apply to all dates. In the final output, round: quality_score to 1 decimal; average_rating to 2 decimals; crash and ANR rates per 1k to 2 decimals; daily_churn_rate to 4 decimals; day-1/7/30 retention to 1 decimal; daily_net_revenue to 2 decimals; avg_transaction_value to 2 decimals; refund_rate to 4 decimals; ARPU to 2 decimals; revenue_health_score to 1 decimal; overall_performance_score to 2 decimals; store_conversion_rate is already rounded to 2 decimals. Set primary_risk_flag with priority: Stability Risk (high crash/ANR rates), Retention Risk (high churn), Revenue Risk (high refunds), Performance Risk (low score), else Low Risk. Set recommended_action from the score: Optimize and Scale (>=80), Improve Quality (>=60), Focus on Retention (>=40), else Critical Review Required. Exclude rows where date_day or package_name is NULL and sort by date_day descending, then by overall_performance_score descending.'
      columns:
      - name: date_day
        description: Calendar date of the metrics; rows with NULL are excluded.
      - name: package_name
        description: Android app package identifier; rows with NULL are excluded.
      - name: daily_installs
        description: Device installs for the day, preferring overview data, else user_behavior totals; defaults to 0.
      - name: daily_uninstalls
        description: Device uninstalls for the day, preferring overview data, else user_behavior totals; defaults to 0.
      - name: active_devices
        description: Active devices from user_behavior; defaults to 0 when unavailable.
      - name: daily_crashes
        description: Crash count from overview; defaults to 0.
      - name: daily_anrs
        description: ANR count from overview; defaults to 0.
      - name: quality_score
        description: Default quality score set to 75.0 and rounded to 1 decimal.
      - name: average_rating
        description: Average store rating from overview, rounded to 2 decimals; defaults to 0.
      - name: crash_rate_per_1k_devices
        description: Crashes per 1,000 active devices; currently defaults to 0.00 and is rounded to 2 decimals.
      - name: anr_rate_per_1k_devices
        description: ANRs per 1,000 active devices; currently defaults to 0.00 and is rounded to 2 decimals.
      - name: version_fragmentation
        description: Default value set to 1.
      - name: daily_churn_rate
        description: Average churn rate from user_behavior, rounded to 4 decimals; defaults to 0.
      - name: high_engagement_markets
        description: Count of distinct countries classified as High Engagement for the day; defaults to 0.
      - name: accelerating_markets
        description: Count of distinct countries with Accelerating growth momentum for the day; defaults to 0.
      - name: day_1_retention_rate
        description: Average day-1 retention over the last 30 days per package, rounded to 1 decimal.
      - name: day_7_retention_rate
        description: Average day-7 retention over the last 30 days per package, rounded to 1 decimal.
      - name: day_30_retention_rate
        description: Average day-30 retention over the last 30 days per package, rounded to 1 decimal.
      - name: strong_retention_markets
        description: Distinct countries with Excellent/Good retention over the last 30 days.
      - name: high_churn_markets
        description: Distinct countries flagged High Churn Risk over the last 30 days.
      - name: daily_net_revenue
        description: Total net revenue for the day from revenue analytics, rounded to 2 decimals; defaults to 0.
      - name: daily_transactions
        description: Total paying transactions for the day; defaults to 0.
      - name: avg_transaction_value
        description: Average transaction value, rounded to 2 decimals; defaults to 0.
      - name: refund_rate
        description: Average refund rate, rounded to 4 decimals; defaults to 0.
      - name: new_subscriptions
        description: New subscriptions started on the day; defaults to 0.
      - name: average_revenue_per_user
        description: Average revenue per user (ARPU), rounded to 2 decimals; defaults to 0.
      - name: revenue_health_score
        description: Average revenue health score, rounded to 1 decimal; defaults to 0.
      - name: store_acquisitions
        description: Store listing acquisitions from overview; defaults to 0.
      - name: store_visitors
        description: Store listing visitors from overview; defaults to 0.
      - name: store_conversion_rate
        description: If visitors > 0, acquisitions divided by visitors times 100 rounded to 2 decimals; otherwise NULL.
      - name: business_health_status
        description: 'Tiered status from installs vs uninstalls, quality, churn, and revenue: Thriving, Healthy, Stable, At Risk, or Critical.'
      - name: overall_performance_score
        description: 0–100 score from weighted components (installs, quality, rating, retention via churn, revenue, store conversion), clamped and rounded to 2 decimals.
      - name: growth_trend
        description: Growing, Declining, or Stable based on installs versus the value 7 days earlier within the same package.
      - name: install_uninstall_ratio
        description: Installs divided by uninstalls rounded to 2 decimals when uninstalls > 0; otherwise NULL.
      - name: total_issues_per_1k_devices
        description: Crashes plus ANRs per 1,000 active devices rounded to 2 decimals when active devices > 0; otherwise NULL.
      - name: primary_risk_flag
        description: 'Risk priority based on thresholds: Stability, Retention, Revenue, or Performance; Low Risk if none apply.'
      - name: recommended_action
        description: 'Action based on overall_performance_score: Optimize and Scale (>=80), Improve Quality (>=60), Focus on Retention (>=40), else Critical Review Required.'
```

### 逐点结论

#### 同类缺口组：机械fallback投影

主要；**Quiet Downgrade**；把握中。

同类缺口组：用户行为、留存、app quality、finance等多源连接；收入/安装/稳定性指标；综合评分、分类及时间窗口。event39用同一个fallback循环，取source_models[0]、只投影少数维度，其余常量/NULL；整表没有实现要求的关系。该首源在CS可为空，缺少其他分支仍是本表自己的缺口。只能整体诊断的机械生成模型按第7节同类候选处理，不能称每个字段都已单改。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 3568 | 0 | 124880 | 0 |
| L1 | 3568 | 0 | 124880 | 0 |
| L2 | 3568 | 0 | 124880 | 0 |
| L3 | 3568 | 0 | 124880 | 0 |

重跑：`records/021_reruns_impl-009_google_play__comprehensive_performance_dashboard.json` / `whole_implementation_diagnostic`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__comprehensive_performance_dashboard.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as VARCHAR) AS date_day,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as VARCHAR) AS daily_installs,
cast(0 as VARCHAR) AS daily_uninstalls,
cast(0 as VARCHAR) AS active_devices,
cast(0 as VARCHAR) AS daily_crashes,
cast(0 as VARCHAR) AS daily_anrs,
cast(75.0 as VARCHAR) AS quality_score,
cast(NULL as VARCHAR) AS average_rating,
cast(0 as VARCHAR) AS crash_rate_per_1k_devices,
cast(0 as VARCHAR) AS anr_rate_per_1k_devices,
cast(1 as INTEGER) AS version_fragmentation,
cast(NULL as VARCHAR) AS daily_churn_rate,
cast(NULL as VARCHAR) AS high_engagement_markets,
cast(NULL as VARCHAR) AS accelerating_markets,
cast(NULL as VARCHAR) AS day_1_retention_rate,
cast(NULL as VARCHAR) AS day_7_retention_rate,
cast(NULL as VARCHAR) AS day_30_retention_rate,
cast(NULL as VARCHAR) AS strong_retention_markets,
cast(NULL as VARCHAR) AS high_churn_markets,
cast(0 as VARCHAR) AS daily_net_revenue,
cast(0 as VARCHAR) AS daily_transactions,
cast(NULL as VARCHAR) AS avg_transaction_value,
cast(NULL as VARCHAR) AS refund_rate,
cast(0 as VARCHAR) AS new_subscriptions,
cast(NULL as VARCHAR) AS average_revenue_per_user,
cast(NULL as VARCHAR) AS revenue_health_score,
cast(NULL as VARCHAR) AS store_acquisitions,
cast(NULL as VARCHAR) AS store_visitors,
cast(NULL as VARCHAR) AS store_conversion_rate,
cast(NULL as VARCHAR) AS business_health_status,
cast(NULL as VARCHAR) AS overall_performance_score,
cast(NULL as VARCHAR) AS growth_trend,
cast(NULL as VARCHAR) AS install_uninstall_ratio,
cast(NULL as VARCHAR) AS total_issues_per_1k_devices,
cast(NULL as VARCHAR) AS primary_risk_flag,
cast(NULL as VARCHAR) AS recommended_action
FROM intermediate.int_google_play__user_behavior_metrics AS src
WHERE src.date_day IS NOT NULL
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，行[1140, 1223]；材料包 `records/021_packages/021_impl-009_google_play__comprehensive_performance_dashboard.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__comprehensive_performance_dashboard.sql`；SHA-256 `cd6a49f2020efd454d71e81b434e6c22b8d81854910386fa46e7d02e24153ba4`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / event 67。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 10，失败=True。
  - `records/021_supplement_queries.json` / index 11，失败=False。

## 不确定或没查到的（含规则问题）

- 规则问题：按用户允许的同脚本机械生成例外记一个同类缺口组；只确立类别，不从整表恢复推导各子指标贡献。event39原脚本见轨迹审计。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
