# impl-010_hubspot__sales_performance_dashboard（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`O`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 7, "cell_scale": 10}, "L1": {"row_scale": 7, "cell_scale": 10}, "L2": {"row_scale": 7, "cell_scale": 7}, "L3": {"row_scale": 7, "cell_scale": 7}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| rating_labels | 其他 | 主要 | 4 | 7 | 4 |
| growth_arithmetic | 其他 | 参与 | 0 | 3 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: hubspot__sales_performance_dashboard
      schema: sales
      description: Quarterly sales performance metrics and forecasts derived from deal-level activity
      grain: One row per created_year and created_quarter
      source_models:
      - intermediate.int_hubspot__deal_performance_metrics
      business_logic: '- Build quarterly_sales_metrics (qsm) from intermediate.int_hubspot__deal_performance_metrics (dpb): - Keep records where created_year and created_quarter are present; aggregate by created_year, created_quarter. - Distinct counts of deal_id: total created, Won, Lost, Open; null deal_id never counted. - Revenue: - revenue_won_in_quarter: sum of deal_amount for Won deals; non-Won contribute zero; null amounts do not affect the sum. - pipeline_value_in_quarter: sum of deal_amount for Open deals; others contribute zero; null amounts ignored. - Averages and distribution for Won deals only: - avg_won_deal_size: average deal_amount; null amounts ignored; returns null if no values. - avg_sales_cycle_days: average deal_cycle_time_days; null values ignored; returns null if none. - median_sales_cycle_days: continuous 50th percentile of deal_cycle_time_days; null if none. - p25_deal_size: continuous 25th percentile of deal_amount; null if none. - p75_deal_size: continuous 75th percentile of deal_amount; null if none. - quarterly_win_rate (%): 100 times distinct Won divided by distinct Won+Lost; returns 0 if no Won+Lost. - active_sales_reps_in_quarter: distinct owner_id across all deals; null owner_id excluded. - Build forecast_metrics (fm), grouped by created_year, created_quarter: - total_open_pipeline: sum of deal_amount for Open deals; null amounts ignored. - weighted_pipeline_forecast: for Open deals, sum of deal_amount multiplied by the deal_size_category’s historical win rate (average of 1 for Won, 0 otherwise across all data); use 0.15 if no category history; null amounts ignored. - time_weighted_forecast: for Open deals with unknown cycle time, sum of deal_amount multiplied by a recency factor based on created_date relative to quarter boundaries at execution time (0.3 for current quarter, 0.5 for last quarter, 0.7 if older); null amounts ignored. - Left join qsm to fm on created_year and created_quarter. - Previous-quarter benchmarks: - Sort by created_year, created_quarter ascending; prev_quarter_revenue and prev_quarter_win_rate take the prior row’s values; first applicable row returns null. - Growth and indicators: - revenue_growth_rate (%): 100 times (current revenue_won_in_quarter minus previous) divided by previous; null if previous is null or not positive. - quarterly_performance_rating: Excellent if win_rate ≥ 30 and avg cycle ≤ 60; Good if win_rate ≥ 20 and avg cycle ≤ 90; Average if win_rate ≥ 15 and avg cycle ≤ 120; otherwise Below Average. - revenue_per_sales_rep: revenue_won_in_quarter divided by active_sales_reps_in_quarter; returns 0 if rep count is 0. - revenue_per_deal_created: revenue_won_in_quarter divided by deals_created_in_quarter; returns 0 if deal count is 0. - quarterly_goal_status: Exceeded Target if revenue_won_in_quarter ≥ 1,000,000; Met Target if ≥ 750,000; Close to Target if ≥ 500,000; otherwise Below Target. - Final output is sorted by created_year and created_quarter descending; the grain is one row per year-quarter.'
      columns:
      - name: created_year
        data_type: BIGINT
        description: Calendar year of deal creation; grouping key; never NULL in output
      - name: created_quarter
        data_type: BIGINT
        description: Calendar quarter (1–4) of deal creation; grouping key; never NULL in output
      - name: deals_created_in_quarter
        data_type: BIGINT
        description: Distinct count of deal_id in the quarter; NULL deal_id excluded
      - name: deals_won_in_quarter
        data_type: BIGINT
        description: Distinct count of deal_id with status Won in the quarter; NULL deal_id excluded
      - name: deals_lost_in_quarter
        data_type: BIGINT
        description: Distinct count of deal_id with status Lost in the quarter; NULL deal_id excluded
      - name: deals_still_open
        data_type: BIGINT
        description: Distinct count of deal_id with status Open in the quarter; NULL deal_id excluded
      - name: revenue_won_in_quarter
        data_type: DECIMAL(38,2)
        description: Sum of deal_amount for Won deals in the quarter; others contribute zero; NULL amounts ignored
      - name: pipeline_value_in_quarter
        data_type: DECIMAL(38,2)
        description: Sum of deal_amount for Open deals in the quarter; others contribute zero; NULL amounts ignored
      - name: total_open_pipeline
        data_type: DECIMAL(38,2)
        description: Sum of deal_amount for Open deals in the quarter from forecast metrics; NULL amounts ignored
      - name: quarterly_win_rate
        data_type: DOUBLE
        description: 'Percentage: 100 × distinct Won divided by distinct Won+Lost for the quarter; returns 0 when none Closed'
      - name: prev_quarter_win_rate
        data_type: DOUBLE
        description: Win rate from the previous quarter based on ascending year-quarter order; NULL for the first applicable row
      - name: prev_quarter_revenue
        data_type: DECIMAL(38,2)
        description: Revenue_won_in_quarter from the previous quarter based on ascending year-quarter order; NULL for the first applicable row
      - name: revenue_growth_rate
        data_type: DOUBLE
        description: Percent change vs previous quarter revenue; NULL if previous is NULL or not positive
      - name: avg_won_deal_size
        data_type: DOUBLE
        description: Average deal_amount for Won deals in the quarter; NULL amounts ignored; NULL if no values
      - name: p25_deal_size
        data_type: DECIMAL(18,2)
        description: Continuous 25th percentile of deal_amount for Won deals in the quarter; NULL if no values
      - name: p75_deal_size
        data_type: DECIMAL(18,2)
        description: Continuous 75th percentile of deal_amount for Won deals in the quarter; NULL if no values
      - name: avg_sales_cycle_days
        data_type: DOUBLE
        description: Average deal_cycle_time_days for Won deals in the quarter; NULL values ignored; NULL if none
      - name: median_sales_cycle_days
        data_type: DOUBLE
        description: Continuous 50th percentile of deal_cycle_time_days for Won deals in the quarter; NULL if none
      - name: active_sales_reps_in_quarter
        data_type: BIGINT
        description: Distinct count of owner_id across all deals in the quarter; NULL owner_id excluded
      - name: revenue_per_sales_rep
        data_type: DOUBLE
        description: Revenue_won_in_quarter divided by active_sales_reps_in_quarter; returns 0 when rep count is 0
      - name: revenue_per_deal_created
        data_type: DOUBLE
        description: Revenue_won_in_quarter divided by deals_created_in_quarter; returns 0 when deal count is 0
      - name: weighted_pipeline_forecast
        data_type: DOUBLE
        description: Sum for Open deals of deal_amount × category win rate (average of 1 for Won, 0 otherwise by deal_size_category); uses 0.15 if no history; NULL amounts ignored
      - name: time_weighted_forecast
        data_type: DECIMAL(38,3)
        description: Sum for Open deals with unknown cycle time of deal_amount × recency factor (0.3 current quarter, 0.5 last quarter, 0.7 older) using quarter boundaries at execution; NULL amounts ignored
      - name: quarterly_performance_rating
        data_type: VARCHAR
        description: Rating determined by win rate and average cycle time using ordered thresholds
      - name: quarterly_goal_status
        data_type: VARCHAR
        description: 'Target attainment from revenue_won_in_quarter: ≥1,000,000 Exceeded, ≥750,000 Met, ≥500,000 Close, otherwise Below'
```

### 逐点结论

#### rating_labels

主要；**其他**；把握高。

agent使用契约Excellent/Good等短标签，gold另附Performance后缀；同分类的文字差异，不改变数值业务计算。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 3 | 10 | 3 |
| L1 | 7 | 3 | 10 | 3 |
| L2 | 7 | 0 | 7 | 0 |
| L3 | 7 | 0 | 7 | 0 |

重跑：`records/039_checks/025_evidence_impl-010_hubspot__sales_performance_dashboard.json` / `rating_labels`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_performance_dashboard.sql` / `SQL.text`（sql）：

```text
case when quarterly_win_rate>=30 and avg_sales_cycle_days<=60 then 'Excellent' when quarterly_win_rate>=20 and avg_sales_cycle_days<=90 then 'Good' when quarterly_win_rate>=15 and avg_sales_cycle_days<=120 then 'Average' else 'Below Average' end
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### growth_arithmetic

参与；**其他**；把握高。

相同growth公式的浮点结合顺序造成3格末位差异；025宽松诊断可对齐。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 7 | 10 | 7 |
| L1 | 7 | 7 | 10 | 7 |
| L2 | 7 | 7 | 7 | 7 |
| L3 | 7 | 7 | 7 | 7 |

重跑：`records/039_checks/025_evidence_impl-010_hubspot__sales_performance_dashboard.json` / `growth_arithmetic`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_performance_dashboard.sql` / `SQL.text`（sql）：

```text
(revenue_won_in_quarter-prev_quarter_revenue)*100.0/prev_quarter_revenue
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`，行[1932, 2014]；材料包 `records/021_packages/021_impl-010_hubspot__sales_performance_dashboard.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_performance_dashboard.sql`；SHA-256 `4320249c8643dcd2edd3778d5acec9177ffef0e322ae2eb9ae8ea792659b68f7`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json` / event 73。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共0条，新核实0条（总数≤5）。诊断/单改不计作核实查询：


## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。
- 025明确此表在CS下不受raw版本差异影响；本次上游均用gold，原021“不可评估”不再使用。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
