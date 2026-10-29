# impl-013 / int_netsuite2__customer_profitability（v2定稿）

## 1. 差异描述与判定

把契约规定的连续分位阈值评分写成NTILE(5)，造成2行4格差异。

已核实：CS固定2025-10-14共同日期；契约要求按revenue第20/40/60/80百分位阈值分配分数。agent直接ntile(5)，等量桶与数值阈值不等价。单替换评分表达式为quantile_cont阈值后L0整表匹配。另改CLV分母为gold方式不改变2行/4格，不列参与因素。

主要原因：**C**；把握：**高**。
参与因素：无：CLV分母对照未改善。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-013_int_netsuite2__customer_profitability.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-013_intermediate_int_netsuite2__customer_profitability.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` 第929–1026行。
- [原始轨迹转录](../016_trace_impl-013.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-013.json)；[015三方raw核对](../015_raw_impl-013.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: int_netsuite2__customer_profitability
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

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_profitability.sql`
```sql
   1: WITH tx AS (SELECT t.*, l.entity_id AS customer_id, 'Customer_'||left(l.entity_id,8) AS customer_name, 'customer_'||left(l.entity_id,8)||'@example.com' AS customer_email FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuite2__transaction_lines l USING(transaction_line_id) WHERE l.entity_id IS NOT NULL AND t.account_type_name IN ('Income','COGS','Expense','OthExpense')), agg AS (SELECT customer_id, customer_name, customer_email, (current_date-365)::TIMESTAMP customer_creation_date, 365::INTEGER customer_age_days, subsidiary_id, sum(CASE WHEN account_type_name='Income' THEN converted_amount ELSE 0 END)::DOUBLE total_revenue, sum(CASE WHEN account_type_name='COGS' THEN abs(converted_amount) ELSE 0 END)::DOUBLE total_cogs, sum(CASE WHEN account_type_name IN ('Expense','OthExpense') THEN abs(converted_amount) ELSE 0 END)::DOUBLE allocated_expenses, count(DISTINCT transaction_id) transaction_count, count(DISTINCT date_trunc('month', accounting_period_ending)) active_months, min(accounting_period_ending) first_transaction_date, max(accounting_period_ending) last_transaction_date FROM tx GROUP BY ALL), metrics AS (SELECT *, total_revenue-total_cogs gross_profit, total_revenue-total_cogs-allocated_expenses net_profit, (total_revenue-total_cogs)/nullif(total_revenue,0) gross_margin_pct, (total_revenue-total_cogs-allocated_expenses)/nullif(total_revenue,0) net_margin_pct, date_diff('month',first_transaction_date,last_transaction_date)+1 customer_lifetime_months,total_revenue/nullif(transaction_count,0) average_order_value FROM agg), scores AS (SELECT *, ntile(5) OVER(ORDER BY total_revenue) revenue_score, CASE WHEN transaction_count>=20 THEN 5 WHEN transaction_count>=10 THEN 4 WHEN transaction_count>=5 THEN 3 WHEN transaction_count>=2 THEN 2 ELSE 1 END frequency_score, CASE WHEN net_margin_pct>=.3 THEN 5 WHEN net_margin_pct>=.2 THEN 4 WHEN net_margin_pct>=.1 THEN 3 WHEN net_margin_pct>=.05 THEN 2 WHEN net_margin_pct>0 THEN 1 ELSE 0 END margin_score, CASE WHEN date_diff('day',last_transaction_date,current_date)<=30 THEN 'Highly Active' WHEN date_diff('day',last_transaction_date,current_date)<=90 THEN 'Active' WHEN date_diff('day',last_transaction_date,current_date)<=180 THEN 'At Risk' ELSE 'Inactive' END activity_status FROM metrics), final AS (SELECT *, revenue_score+frequency_score+margin_score total_customer_score FROM scores) SELECT CASE WHEN customer_id IS NULL OR subsidiary_id IS NULL THEN NULL ELSE md5(customer_id||'_'||subsidiary_id) END customer_profitability_id, customer_id, customer_name, customer_email, customer_creation_date, customer_age_days, CASE WHEN customer_age_days<90 THEN 'New Customer' WHEN customer_age_days<365 THEN 'Growing Relationship' WHEN customer_age_days<1095 THEN 'Established Customer' ELSE 'Long-term Customer' END customer_maturity, subsidiary_id,total_revenue,total_cogs,allocated_expenses,gross_profit,net_profit,gross_margin_pct,net_margin_pct,transaction_count,active_months,coalesce(customer_lifetime_months,1) customer_lifetime_months,first_transaction_date,last_transaction_date,average_order_value,revenue_score,frequency_score,margin_score,total_customer_score,CASE WHEN total_customer_score>=12 THEN 'Champion' WHEN total_customer_score>=9 THEN 'Loyal' WHEN total_customer_score>=6 THEN 'Potential' WHEN total_customer_score>=3 THEN 'At Risk' ELSE 'Lost' END customer_segment,activity_status,net_profit/nullif(active_months,0)*greatest(12,1.2*coalesce(customer_lifetime_months,1)) predicted_clv,CASE WHEN net_margin_pct>=.2 AND activity_status IN ('Highly Active','Active') THEN 'High Investment' WHEN net_margin_pct>=.1 AND total_revenue>(SELECT avg(total_revenue) FROM agg) THEN 'Medium Investment' WHEN net_margin_pct>0 THEN 'Low Investment' ELSE 'Review Required' END investment_recommendation,current_date analysis_date FROM final WHERE customer_id IS NOT NULL AND total_revenue>0
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_profitability.sql`
```sql
   1: -- Customer Profitability Analysis
   2: -- Customer profitability analysis, including customer lifetime value, contribution analysis, etc.
   3: with customer_transactions as (
   4:     select 
   5:         t.transaction_id,
   6:         t.transaction_line_id,
   7:         t.subsidiary_id,
   8:         t.account_id,
   9:         t.account_name,
  10:         t.account_type_name,
  11:         t.converted_amount,
  12:         t.transaction_amount,
  13:         t.accounting_period_ending,
  14:         
  15:         -- Use entity_id as customer_id and generate simulated customer information
  16:         tl.entity_id as customer_id,
  17:         'Customer_' || substring(tl.entity_id, 1, 8) as customer_name,
  18:         'customer_' || substring(tl.entity_id, 1, 8) || '@example.com' as customer_email,
  19:         current_date - interval '365 days' as customer_creation_date,
  20:         
  21:         -- Calculate account age
  22:         365 as customer_age_days,
  23:         
  24:         -- Transaction Classification
  25:         case 
  26:             when t.account_type_name = 'Income' then 'Revenue'
  27:             when t.account_type_name = 'COGS' then 'Cost_of_Sales'
  28:             when t.account_type_name in ('Expense', 'OthExpense') then 'Operating_Expense'
  29:             else 'Other'
  30:         end as transaction_category
  31:         
  32:     from intermediate.int_netsuite2__transaction_details t
  33:     join staging.stg_netsuite2__transaction_lines tl
  34:         on t.transaction_line_id = tl.transaction_line_id
  35:     where tl.entity_id is not null
  36:         and t.account_type_name in ('Income', 'COGS', 'Expense', 'OthExpense')
  37: ),
  38: 
  39: customer_metrics as (
  40:     select 
  41:         customer_id,
  42:         customer_name,
  43:         customer_email,
  44:         customer_creation_date,
  45:         customer_age_days,
  46:         subsidiary_id,
  47:         
  48:         -- revenue metric
  49:         sum(case when transaction_category = 'Revenue' then converted_amount else 0 end) as total_revenue,
  50:         sum(case when transaction_category = 'Cost_of_Sales' then abs(converted_amount) else 0 end) as total_cogs,
  51:         sum(case when transaction_category = 'Operating_Expense' then abs(converted_amount) else 0 end) as allocated_expenses,
  52:         
  53:         -- gross profit
  54:         sum(case when transaction_category = 'Revenue' then converted_amount else 0 end) - 
  55:         sum(case when transaction_category = 'Cost_of_Sales' then abs(converted_amount) else 0 end) as gross_profit,
  56:         
  57:         -- Net profit (simplified calculation)
  58:         sum(case when transaction_category = 'Revenue' then converted_amount else 0 end) - 
  59:         sum(case when transaction_category = 'Cost_of_Sales' then abs(converted_amount) else 0 end) - 
  60:         sum(case when transaction_category = 'Operating_Expense' then abs(converted_amount) else 0 end) as net_profit,
  61:         
  62:         -- Transaction statistics
  63:         count(distinct transaction_id) as transaction_count,
  64:         count(distinct date_trunc('month', accounting_period_ending)) as active_months,
  65:         min(accounting_period_ending) as first_transaction_date,
  66:         max(accounting_period_ending) as last_transaction_date,
  67:         
  68:         -- average order value
  69:         case 
  70:             when count(distinct transaction_id) > 0 
  71:             then sum(case when transaction_category = 'Revenue' then converted_amount else 0 end) / count(distinct transaction_id)
  72:             else 0 
  73:         end as average_order_value
  74:         
  75:     from customer_transactions
  76:     group by customer_id, customer_name, customer_email, customer_creation_date, customer_age_days, subsidiary_id
  77: ),
  78: 
  79: customer_segmentation as (
  80:     select 
  81:         *,
  82:         
  83:         -- Gross profit margin
  84:         case 
  85:             when total_revenue > 0 
  86:             then gross_profit / total_revenue 
  87:             else 0 
  88:         end as gross_margin_pct,
  89:         
  90:         -- net profit margin
  91:         case 
  92:             when total_revenue > 0 
  93:             then net_profit / total_revenue 
  94:             else 0 
  95:         end as net_margin_pct,
  96:         
  97:         -- Customer life cycle length (months)
  98:         case 
  99:             when first_transaction_date is not null and last_transaction_date is not null
 100:             then datediff('month', first_transaction_date, last_transaction_date) + 1
 101:             else 1
 102:         end as customer_lifetime_months,
 103:         
 104:         -- Customer Maturity Classification
 105:         case 
 106:             when customer_age_days < 90 then 'New Customer'
 107:             when customer_age_days < 365 then 'Growing Relationship'
 108:             when customer_age_days < 1095 then 'Established Customer'
 109:             else 'Long-term Customer'
 110:         end as customer_maturity,
 111:         
 112:         -- Activity Classification
 113:         case 
 114:             when datediff('day', last_transaction_date, current_date) <= 30 then 'Highly Active'
 115:             when datediff('day', last_transaction_date, current_date) <= 90 then 'Active'
 116:             when datediff('day', last_transaction_date, current_date) <= 180 then 'At Risk'
 117:             else 'Inactive'
 118:         end as activity_status,
 119:         
 120:         current_date as analysis_date
 121:         
 122:     from customer_metrics
 123: ),
 124: 
 125: -- Customer Value Stratification (Simplified Version of RFM Analysis)
 126: customer_value_scoring as (
 127:     select 
 128:         *,
 129:         
 130:         -- Revenue Value Rating (R - Revenue)
 131:         case 
 132:             when total_revenue >= (select percentile_cont(0.8) within group (order by total_revenue) from customer_segmentation) then 5
 133:             when total_revenue >= (select percentile_cont(0.6) within group (order by total_revenue) from customer_segmentation) then 4
 134:             when total_revenue >= (select percentile_cont(0.4) within group (order by total_revenue) from customer_segmentation) then 3
 135:             when total_revenue >= (select percentile_cont(0.2) within group (order by total_revenue) from customer_segmentation) then 2
 136:             else 1
 137:         end as revenue_score,
 138:         
 139:         -- Frequency score (F - Frequency)
 140:         case 
 141:             when transaction_count >= 20 then 5
 142:             when transaction_count >= 10 then 4
 143:             when transaction_count >= 5 then 3
 144:             when transaction_count >= 2 then 2
 145:             else 1
 146:         end as frequency_score,
 147:         
 148:         -- Profitability score (M - Margin)
 149:         case 
 150:             when net_margin_pct >= 0.3 then 5
 151:             when net_margin_pct >= 0.2 then 4
 152:             when net_margin_pct >= 0.1 then 3
 153:             when net_margin_pct >= 0.05 then 2
 154:             when net_margin_pct > 0 then 1
 155:             else 0
 156:         end as margin_score
 157:         
 158:     from customer_segmentation
 159: ),
 160: 
 161: final_customer_profitability as (
 162:     select 
 163:         *,
 164:         
 165:         -- Comprehensive customer ratings
 166:         (revenue_score + frequency_score + margin_score) as total_customer_score,
 167:         
 168:         -- Customer value layering
 169:         case 
 170:             when (revenue_score + frequency_score + margin_score) >= 12 then 'Champion'
 171:             when (revenue_score + frequency_score + margin_score) >= 9 then 'Loyal'
 172:             when (revenue_score + frequency_score + margin_score) >= 6 then 'Potential'
 173:             when (revenue_score + frequency_score + margin_score) >= 3 then 'At Risk'
 174:             else 'Lost'
 175:         end as customer_segment,
 176:         
 177:         -- Expected customer lifetime value (CLV)
 178:         case 
 179:             when customer_lifetime_months > 0 and active_months > 0
 180:             then (net_profit / customer_lifetime_months) * 
 181:                  greatest(12, customer_lifetime_months * 1.2) -- Assuming future growth of 20%
 182:             else net_profit
 183:         end as predicted_clv,
 184:         
 185:         -- Return on Investment Advice
 186:         case 
 187:             when net_margin_pct >= 0.2 and activity_status in ('Highly Active', 'Active') then 'High Investment'
 188:             when net_margin_pct >= 0.1 and total_revenue > (select avg(total_revenue) from customer_segmentation) then 'Medium Investment'
 189:             when net_margin_pct > 0 then 'Low Investment'
 190:             else 'Review Required'
 191:         end as investment_recommendation
 192:         
 193:     from customer_value_scoring
 194: )
 195: 
 196: select 
 197:     customer_id,
 198:     customer_name,
 199:     customer_email,
 200:     customer_creation_date,
 201:     customer_age_days,
 202:     customer_maturity,
 203:     subsidiary_id,
 204:     
 205:     -- financial indicators
 206:     total_revenue,
 207:     total_cogs,
 208:     allocated_expenses,
 209:     gross_profit,
 210:     net_profit,
 211:     gross_margin_pct,
 212:     net_margin_pct,
 213:     
 214:     -- trading indicators
 215:     transaction_count,
 216:     active_months,
 217:     customer_lifetime_months,
 218:     first_transaction_date,
 219:     last_transaction_date,
 220:     average_order_value,
 221:     
 222:     -- Rating and classification
 223:     revenue_score,
 224:     frequency_score,
 225:     margin_score,
 226:     total_customer_score,
 227:     customer_segment,
 228:     activity_status,
 229:     
 230:     -- value assessment
 231:     predicted_clv,
 232:     investment_recommendation,
 233:     
 234:     analysis_date,
 235:     
 236:     md5(cast(customer_id as varchar) || '_' || cast(subsidiary_id as varchar)) as customer_profitability_id
 237:     
 238: from final_customer_profitability
 239: where customer_id is not null
 240:     and total_revenue > 0
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.netsuite2_account_data|gold_vs_initial|True|True|True||
|raw.netsuite2_accounting_period_data|gold_vs_initial|True|True|True||
|raw.netsuite2_accounting_period_fiscal_cal_data|gold_vs_initial|True|True|True||
|raw.netsuite2_subsidiary_data|gold_vs_initial|True|True|True||
|raw.netsuite2_transaction_line_data|gold_vs_initial|True|True|True||
|raw.netsuite2_account_data|gold_vs_agent|True|True|True||
|raw.netsuite2_accounting_period_data|gold_vs_agent|True|True|True||
|raw.netsuite2_accounting_period_fiscal_cal_data|gold_vs_agent|True|True|True||
|raw.netsuite2_subsidiary_data|gold_vs_agent|True|True|True||
|raw.netsuite2_transaction_line_data|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event1给出完整业务规则；event19生成ntile(5)表达式。未发现正确分位阈值意图的相反代码证据，直接按契约执行遗漏归C，不推断I。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|percentile_score|C|看到了但没提|1|

### percentile_score：看到了但没提

契约中的分位阈值可见；没有说明采用NTILE而不是连续分位阈值。

事件 **1**，字段`args.content`；[轨迹原文](../016_trace_impl-013.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`。
```text
r_value_scoring: - revenue_score: 5 for total_revenue at or above the 80th percentile; 4 at or above the 60th; 3 at or above the 40th; 2 at or above the 20th; otherwise 1. Percentiles are computed over all rows in customer_segmentation (before the final filter). - frequency_score: 5 for 20 or more transactions; 4 for 10–19; 3 for 5–9; 2 for 2–4; otherwise 1. - margin_score: 5 for net_margin_pct at or above 0.30; 4 at or above 0.20; 3 at or above 0.10; 2 at or above 0.05; 1 for greater than 0; otherwise 0. Final computations and filter: - total_customer_score equals revenue_score plus frequency_score plus margin_score. - customer_segment: Champion for scores 12 or higher; Loyal for 9–11; Potential for 6–8; At Risk for 3–5; Lost for below 3. - predicted_clv: if customer_lifetime_months and active_months are both greater than 0, multiply net_profit per month by the larger of 12 months and 1.2 times customer_li
```

已检视67个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **0条**；018新增核实查询 **0条**。核实代价：需要查业务说明。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-013.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **0条**（含014复用；本轮新增0条）；核实代价档：**需要查业务说明**。诊断不计入5条上限。查询失败与重复执行如实保留。

无新增数据核实查询；本表依据契约/SQL和只读诊断或重跑判断。

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['customer_profitability_id']`；比较列（与键取并集）：`['customer_id', 'customer_name', 'customer_email', 'customer_maturity', 'subsidiary_id', 'total_revenue', 'total_cogs', 'allocated_expenses', 'gross_profit', 'net_profit', 'gross_margin_pct', 'net_margin_pct', 'transaction_count', 'first_transaction_date', 'last_transaction_date', 'average_order_value', 'revenue_score', 'frequency_score', 'margin_score', 'total_customer_score', 'customer_segment', 'activity_status', 'predicted_clv', 'investment_recommendation', 'analysis_date', 'customer_profitability_id']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 12:00:00+08'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 5}]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|percentile_score|2→0|4→0|L0|
|clv_month_denominator|2→2|4→4|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|115|115|0|0|0/0|2|2|4|False|
|L1|115|115|0|0|0/0|2|2|4|False|
|L2|115|115|0|0|0/0|2|2|4|False|
|L3|115|115|0|0|0/0|2|2|4|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|customer_profitability_id|0|0|0|0|
|customer_id|0|0|0|0|
|customer_name|0|0|0|0|
|customer_email|0|0|0|0|
|customer_maturity|0|0|0|0|
|subsidiary_id|0|0|0|0|
|total_revenue|0|0|0|0|
|total_cogs|0|0|0|0|
|allocated_expenses|0|0|0|0|
|gross_profit|0|0|0|0|
|net_profit|0|0|0|0|
|gross_margin_pct|0|0|0|0|
|net_margin_pct|0|0|0|0|
|transaction_count|0|0|0|0|
|first_transaction_date|0|0|0|0|
|last_transaction_date|0|0|0|0|
|average_order_value|0|0|0|0|
|revenue_score|2|2|2|2|
|frequency_score|0|0|0|0|
|margin_score|0|0|0|0|
|total_customer_score|2|2|2|2|
|customer_segment|0|0|0|0|
|activity_status|0|0|0|0|
|predicted_clv|0|0|0|0|
|investment_recommendation|0|0|0|0|
|analysis_date|0|0|0|0|

### 重跑 baseline

SQL：`data/016_work/impl-013/baseline.sql`；SHA-256：`0777ede0f6a02f622497b3003220552f93a92e5f96f2af158a51addb6f8b4989`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|115|115|0|0|0/0|2|2|4|False|
|L1|115|115|0|0|0/0|2|2|4|False|
|L2|115|115|0|0|0/0|2|2|4|False|
|L3|115|115|0|0|0/0|2|2|4|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|customer_profitability_id|0|0|0|0|
|customer_id|0|0|0|0|
|customer_name|0|0|0|0|
|customer_email|0|0|0|0|
|customer_maturity|0|0|0|0|
|subsidiary_id|0|0|0|0|
|total_revenue|0|0|0|0|
|total_cogs|0|0|0|0|
|allocated_expenses|0|0|0|0|
|gross_profit|0|0|0|0|
|net_profit|0|0|0|0|
|gross_margin_pct|0|0|0|0|
|net_margin_pct|0|0|0|0|
|transaction_count|0|0|0|0|
|first_transaction_date|0|0|0|0|
|last_transaction_date|0|0|0|0|
|average_order_value|0|0|0|0|
|revenue_score|2|2|2|2|
|frequency_score|0|0|0|0|
|margin_score|0|0|0|0|
|total_customer_score|2|2|2|2|
|customer_segment|0|0|0|0|
|activity_status|0|0|0|0|
|predicted_clv|0|0|0|0|
|investment_recommendation|0|0|0|0|
|analysis_date|0|0|0|0|

### 重跑 percentile_score

SQL：`data/016_work/impl-013/percentile_score.sql`；SHA-256：`367a445531b117c32a2de574c70c7d22830b492fff7bd6228bfc63c4e60212c5`。

唯一原文位置offset=1601，替换前：
```sql
ntile(5) OVER(ORDER BY total_revenue)
```
替换后：
```sql
CASE WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.8) FROM metrics) THEN 5 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.6) FROM metrics) THEN 4 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.4) FROM metrics) THEN 3 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.2) FROM metrics) THEN 2 ELSE 1 END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|115|115|0|0|0/0|0|0|0|True|
|L1|115|115|0|0|0/0|0|0|0|True|
|L2|115|115|0|0|0/0|0|0|0|True|
|L3|115|115|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|customer_profitability_id|0|0|0|0|
|customer_id|0|0|0|0|
|customer_name|0|0|0|0|
|customer_email|0|0|0|0|
|customer_maturity|0|0|0|0|
|subsidiary_id|0|0|0|0|
|total_revenue|0|0|0|0|
|total_cogs|0|0|0|0|
|allocated_expenses|0|0|0|0|
|gross_profit|0|0|0|0|
|net_profit|0|0|0|0|
|gross_margin_pct|0|0|0|0|
|net_margin_pct|0|0|0|0|
|transaction_count|0|0|0|0|
|first_transaction_date|0|0|0|0|
|last_transaction_date|0|0|0|0|
|average_order_value|0|0|0|0|
|revenue_score|0|0|0|0|
|frequency_score|0|0|0|0|
|margin_score|0|0|0|0|
|total_customer_score|0|0|0|0|
|customer_segment|0|0|0|0|
|activity_status|0|0|0|0|
|predicted_clv|0|0|0|0|
|investment_recommendation|0|0|0|0|
|analysis_date|0|0|0|0|

### 重跑 clv_month_denominator

SQL：`data/016_work/impl-013/clv_month_denominator.sql`；SHA-256：`aa9744427b1900333f0ca8536492cb3ca72549466f922deee49dda516d087efd`。

唯一原文位置offset=3419，替换前：
```sql
net_profit/nullif(active_months,0)*greatest(12,1.2*coalesce(customer_lifetime_months,1))
```
替换后：
```sql
CASE WHEN customer_lifetime_months>0 AND active_months>0 THEN net_profit/customer_lifetime_months*greatest(12,1.2*customer_lifetime_months) ELSE net_profit END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|115|115|0|0|0/0|2|2|4|False|
|L1|115|115|0|0|0/0|2|2|4|False|
|L2|115|115|0|0|0/0|2|2|4|False|
|L3|115|115|0|0|0/0|2|2|4|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|customer_profitability_id|0|0|0|0|
|customer_id|0|0|0|0|
|customer_name|0|0|0|0|
|customer_email|0|0|0|0|
|customer_maturity|0|0|0|0|
|subsidiary_id|0|0|0|0|
|total_revenue|0|0|0|0|
|total_cogs|0|0|0|0|
|allocated_expenses|0|0|0|0|
|gross_profit|0|0|0|0|
|net_profit|0|0|0|0|
|gross_margin_pct|0|0|0|0|
|net_margin_pct|0|0|0|0|
|transaction_count|0|0|0|0|
|first_transaction_date|0|0|0|0|
|last_transaction_date|0|0|0|0|
|average_order_value|0|0|0|0|
|revenue_score|2|2|2|2|
|frequency_score|0|0|0|0|
|margin_score|0|0|0|0|
|total_customer_score|2|2|2|2|
|customer_segment|0|0|0|0|
|activity_status|0|0|0|0|
|predicted_clv|0|0|0|0|
|investment_recommendation|0|0|0|0|
|analysis_date|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**C**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|percentile_score|C|2→0|4→0|L0|

重跑是否满足U第4条件：**是（percentile_score单改L0整表一致；非U）**。

规则已经直接规定计算方式，不需把数据分布构造为U命题；无需额外核实查询。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：不适用：第二批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

固定日期是所有基线/干预共同的运行条件，不能把这个共同控制当成与局部修改捆绑的第二处原因。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
