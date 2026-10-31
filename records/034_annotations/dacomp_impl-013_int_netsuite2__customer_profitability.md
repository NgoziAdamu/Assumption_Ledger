# DAComp / impl-013_int_netsuite2__customer_profitability（v3）

## 错在哪里
把契约规定的连续分位阈值评分写成NTILE(5)，造成2行4格差异。

证据复用入口：[018_impl-013_int_netsuite2__customer_profitability.md](../018_annotations/018_impl-013_int_netsuite2__customer_profitability.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## percentile_score
- 角色：主要；类别：**Intent Misreading**；把握：中。
- 依据：规格20/40/60/80百分位阈值，agent ntile(5)等量桶；2行4格→0。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-013.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
r_value_scoring: - revenue_score: 5 for total_revenue at or above the 80th percentile; 4 at or above the 60th; 3 at or above the 40th; 2 at or above the 20th; otherwise 1. Percentiles are computed over all rows in customer_segmentation (before the final filter). - frequency_score: 5 for 20 or more transactions; 4 for 10–19; 3 for 5–9; 2 for 2–4; otherwise 1. - margin_score: 5 for net_margin_pct at or above 0.30; 4 at or above 0.20; 3 at or above 0.10; 2 at or above 0.05; 1 for greater than 0; otherwise 0. Final computations and filter: - total_customer_score equals revenue_score plus frequency_score plus margin_score. - customer_segment: Champion for scores 12 or higher; Loyal for 9–11; Potential for 6–8; At Risk for 3–5; Lost for below 3. - predicted_clv: if customer_lifetime_months and active_months are both greater than 0, multiply net_profit per month by the larger of 12 months and 1.2 times customer_li
```
## clv_denominator
- 角色：非原因；类别：**Unstated Choice**；把握：中。
- 依据：CLV分母对照2行4格不变；不作为参与因素。
- 是否说出：没有迹象。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。

## 规模、证据复用与新做
主要原因：Intent Misreading。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-013_int_netsuite2__customer_profitability.md](../018_annotations/018_impl-013_int_netsuite2__customer_profitability.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: int_netsuite2__customer_profitability
      description: Customer profitability metrics, scoring, and recommendations per customer and subsidiary based on converted_amount aggregations; final rows require total_revenue > 0.
      grain: One row per customer_id per subsidiary_id (after filtering to total_revenue > 0)
      source_models:
      - intermediate.int_netsuite2__transaction_details
      - staging.stg_netsuite2__transaction_lines
      business_logic: 'Build customer_transactions: - Join transaction details to transaction lines on transaction_line_id. - Keep rows where entity_id is present and account_type_name is one of Income, COGS, Expense, or OthExpense. - Derive customer fields from entity_id: customer_id equals entity_id; customer_name as ''Customer_'' plus the first 8 characters of customer_id; customer_email as ''customer_'' plus the first 8 characters of customer_id plus ''@example.com''. - Set customer_creation_date to the current date minus 365 days and customer_age_days to 365. - Categorize transactions by account_type_name: Income as Revenue; COGS as Cost_of_Sales; Expense and OthExpense as Operating_Expense. Aggregate to customer_metrics at the level of customer_id, customer_name, customer_email, customer_creation_date, customer_age_days, subsidiary_id: - total_revenue: sum of converted_amount for Revenue transactions (signed). - total_cogs: sum of absolute converted_amount for Cost_of_Sales. - allocated_expenses: sum of absolute converted_amount for Operating_Expense. - gross_profit: total_revenue minus total_cogs. - net_profit: gross_profit minus allocated_expenses. - transaction_count: distinct count of transaction_id. - active_months: distinct count of calendar months from accounting_period_ending. - first_transaction_date and last_transaction_date: earliest and latest accounting_period_ending. - average_order_value: total_revenue divided by transaction_count; use 0 when transaction_count is 0. Enrich in customer_segmentation: - gross_margin_pct: gross_profit divided by total_revenue; use 0 when total_revenue is 0. - net_margin_pct: net_profit divided by total_revenue; use 0 when total_revenue is 0. - customer_lifetime_months: months between first and last transaction, inclusive; use 1 when either date is missing. - customer_maturity from customer_age_days: under 90 days is New Customer; under 365 is Growing Relationship; under 1095 is Established Customer; otherwise Long-term Customer. - activity_status from days since last_transaction_date at run time: 30 or fewer is Highly Active; 31–90 is Active; 91–180 is At Risk; over 180 is Inactive. - analysis_date equals the current date. Score in customer_value_scoring: - revenue_score: 5 for total_revenue at or above the 80th percentile; 4 at or above the 60th; 3 at or above the 40th; 2 at or above the 20th; otherwise 1. Percentiles are computed over all rows in customer_segmentation (before the final filter). - frequency_score: 5 for 20 or more transactions; 4 for 10–19; 3 for 5–9; 2 for 2–4; otherwise 1. - margin_score: 5 for net_margin_pct at or above 0.30; 4 at or above 0.20; 3 at or above 0.10; 2 at or above 0.05; 1 for greater than 0; otherwise 0. Final computations and filter: - total_customer_score equals revenue_score plus frequency_score plus margin_score. - customer_segment: Champion for scores 12 or higher; Loyal for 9–11; Potential for 6–8; At Risk for 3–5; Lost for below 3. - predicted_clv: if customer_lifetime_months and active_months are both greater than 0, multiply net_profit per month by the larger of 12 months and 1.2 times customer_lifetime_months; otherwise use net_profit. - investment_recommendation: High Investment when net_margin_pct is at least 0.20 and activity_status is Highly Active or Active; Medium Investment when net_margin_pct is at least 0.10 and total_revenue exceeds the average total_revenue across customer_segmentation; Low Investment when net_margin_pct is greater than 0; otherwise Review Required. - Keep rows where customer_id is present and total_revenue is greater than 0. - customer_profitability_id is the MD5 hash of the string formed by customer_id, an underscore, and subsidiary_id; it is null if either component is null.'
      columns:
      - name: customer_profitability_id
        data_type: VARCHAR
        description: MD5 of customer_id + '_' + subsidiary_id; null when either component is null; unique per (customer_id, subsidiary_id).
      - name: customer_id
        data_type: VARCHAR
        description: Customer identifier from transaction lines; final rows require non-null.
      - name: customer_name
        data_type: VARCHAR
        description: 'Synthetic name: ''Customer_'' plus the first 8 characters of customer_id.'
      - name: customer_email
        data_type: VARCHAR
        description: 'Synthetic email: ''customer_'' plus the first 8 characters of customer_id and ''@example.com''.'
      - name: customer_creation_date
        data_type: TIMESTAMP
        description: Current date minus 365 days at run time for all rows.
      - name: customer_age_days
        data_type: INTEGER
        description: Fixed value 365 representing days since customer_creation_date.
      - name: customer_maturity
        data_type: VARCHAR
        description: 'Bucket from customer_age_days: New (<90), Growing (<365), Established (<1095), Long-term (otherwise).'
      - name: subsidiary_id
        data_type: VARCHAR
        description: Subsidiary from transaction details; may be null; part of the row grain and ID hash.
      - name: total_revenue
        data_type: DOUBLE
        description: Signed sum of converted_amount for Revenue transactions; final rows require > 0.
      - name: total_cogs
        data_type: DOUBLE
        description: Sum of absolute converted_amount for Cost_of_Sales; non-negative.
      - name: allocated_expenses
        data_type: DOUBLE
        description: Sum of absolute converted_amount for Operating_Expense; non-negative.
      - name: gross_profit
        data_type: DOUBLE
        description: total_revenue minus total_cogs; may be negative.
      - name: net_profit
        data_type: DOUBLE
        description: gross_profit minus allocated_expenses; may be negative.
      - name: gross_margin_pct
        data_type: DOUBLE
        description: gross_profit divided by total_revenue when total_revenue > 0, else 0; ratio not a formatted percent.
      - name: net_margin_pct
        data_type: DOUBLE
        description: net_profit divided by total_revenue when total_revenue > 0, else 0; ratio not a formatted percent.
      - name: transaction_count
        data_type: BIGINT
        description: Distinct count of transaction_id across included categories; at least 1 in final rows.
      - name: active_months
        data_type: BIGINT
        description: Distinct count of calendar months present in accounting_period_ending; at least 1.
      - name: customer_lifetime_months
        data_type: BIGINT
        description: Inclusive months between first and last transaction; 1 when either date is missing.
      - name: first_transaction_date
        data_type: DATE
        description: Earliest accounting_period_ending for the customer and subsidiary.
      - name: last_transaction_date
        data_type: DATE
        description: Latest accounting_period_ending for the customer and subsidiary.
      - name: average_order_value
        data_type: DOUBLE
        description: total_revenue divided by transaction_count when transaction_count > 0, else 0.
      - name: revenue_score
        data_type: INTEGER
        description: 'Score based on total_revenue percentiles across customer_segmentation: 80th+→5, 60th+→4, 40th+→3, 20th+→2, otherwise 1.'
      - name: frequency_score
        data_type: INTEGER
        description: 'Score from transaction_count thresholds: 20+→5; 10–19→4; 5–9→3; 2–4→2; otherwise 1.'
      - name: margin_score
        data_type: INTEGER
        description: 'Score from net_margin_pct thresholds: ≥0.30→5; ≥0.20→4; ≥0.10→3; ≥0.05→2; >0→1; otherwise 0.'
      - name: total_customer_score
        data_type: INTEGER
        description: Sum of revenue_score, frequency_score, and margin_score.
      - name: customer_segment
        data_type: VARCHAR
        description: 'Segment by total_customer_score: Champion (≥12), Loyal (≥9), Potential (≥6), At Risk (≥3), Lost (otherwise).'
      - name: activity_status
        data_type: VARCHAR
        description: 'Recency category by days since last_transaction_date: ≤30 Highly Active; ≤90 Active; ≤180 At Risk; otherwise Inactive.'
      - name: predicted_clv
        data_type: DOUBLE
        description: If customer_lifetime_months and active_months are both > 0, scale net_profit per month by the larger of 12 months or 1.2×customer_lifetime_months; otherwise use net_profit.
      - name: investment_recommendation
        data_type: VARCHAR
        description: High when net_margin_pct ≥ 0.20 and activity is Highly Active/Active; Medium when net_margin_pct ≥ 0.10 and total_revenue exceeds the average across customer_segmentation; Low when net_margin_pct > 0; otherwise Review Required.
      - name: analysis_date
        data_type: DATE
        description: The current date at model run, identical across all rows for the run.
```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-013_int_netsuite2__customer_profitability.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-013_int_netsuite2__customer_profitability.md:131)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-013_int_netsuite2__customer_profitability.md:442)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-013_int_netsuite2__customer_profitability.md:489)
- [重跑 percentile_score](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-013_int_netsuite2__customer_profitability.md:533)
- [重跑 clv_month_denominator](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-013_int_netsuite2__customer_profitability.md:584)
