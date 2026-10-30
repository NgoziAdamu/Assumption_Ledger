# impl-013 / netsuite2_customer_analytics（全量；v2）

## 1. 差异与结论

遗漏contract指定的customer_insights对behavior的第二次连接，单补该连接恢复44行的多重性，减少1078格；另外频率NULL/0为C、简短/长标签为O、未指定具体权重为A。按格子选连接遗漏C为主因。

主要原因：**C**；参与因素：C：frequency_zero；O：retention_labels；A：score_weights；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| second_join | C | 0 | 1078 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_netsuite2_customer_analytics.md](../../records/022_packages/022_impl-013_netsuite2_customer_analytics.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_netsuite2_customer_analytics/022_impl-013_netsuite2_customer_analytics.json`。
- 比较结果：[022_reruns_impl-013_netsuite2_customer_analytics.json](../022_reruns_impl-013_netsuite2_customer_analytics.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第2533–2631行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql`；原件第1–1行。

```sql
   1: WITH behavior AS (SELECT l.entity_id customer_id,t.subsidiary_id,count(DISTINCT t.transaction_id) total_transactions,count(DISTINCT date_trunc('month',t.accounting_period_ending)) active_months,count(DISTINCT quarter(t.accounting_period_ending)) active_quarters,sum(t.converted_amount) total_revenue,avg(t.converted_amount) avg_transaction_value,stddev_samp(t.converted_amount) transaction_value_volatility,max(t.converted_amount) max_transaction_value,min(t.converted_amount) min_transaction_value,min(t.accounting_period_ending) first_transaction_date,max(t.accounting_period_ending) last_transaction_date,date_diff('day',min(t.accounting_period_ending),max(t.accounting_period_ending)) customer_lifespan_days,date_diff('day',max(t.accounting_period_ending),current_date) days_since_last_transaction,current_date analysis_date,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=1) q1_transactions,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=2) q2_transactions,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=3) q3_transactions,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=4) q4_transactions FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuite2__transaction_lines l USING(transaction_line_id) WHERE l.entity_id IS NOT NULL AND t.account_type_name='Income' AND t.converted_amount>0 GROUP BY l.entity_id,t.subsidiary_id), retention AS (SELECT *,CASE WHEN customer_lifespan_days>=365 THEN 'Long-term' WHEN customer_lifespan_days>=180 THEN 'Medium-term' WHEN customer_lifespan_days>=90 THEN 'Short-term' WHEN customer_lifespan_days>=30 THEN 'New' ELSE 'Very New' END retention_category,CASE WHEN days_since_last_transaction<=30 THEN 'Highly Active' WHEN days_since_last_transaction<=90 THEN 'Active' WHEN days_since_last_transaction<=180 THEN 'At Risk' WHEN days_since_last_transaction<=365 THEN 'Dormant' ELSE 'Lost' END activity_status,total_transactions/nullif(customer_lifespan_days/30.0,0) avg_transactions_per_month,CASE WHEN days_since_last_transaction<=30 AND total_transactions>=5 THEN .95 WHEN days_since_last_transaction<=60 AND total_transactions>=3 THEN .80 WHEN days_since_last_transaction<=90 AND total_transactions>=2 THEN .60 WHEN days_since_last_transaction<=180 THEN .30 WHEN days_since_last_transaction<=365 THEN .10 ELSE .05 END::DECIMAL(3,2) retention_probability FROM behavior), cp AS (SELECT *,percent_rank() OVER(ORDER BY total_revenue) rev_pct FROM intermediate.int_netsuite2__customer_profitability), enriched AS (SELECT cp.*,r.*,CASE WHEN cp.rev_pct>=.9 THEN 'Platinum' WHEN cp.rev_pct>=.7 THEN 'Gold' WHEN cp.rev_pct>=.5 THEN 'Silver' WHEN cp.rev_pct>=.3 THEN 'Bronze' ELSE 'Basic' END value_tier FROM cp LEFT JOIN retention r ON r.customer_id=cp.customer_id), scored AS (SELECT *,least(100,revenue_score*10+frequency_score*5+margin_score*5+CASE WHEN activity_status='Highly Active' THEN 15 WHEN activity_status='Active' THEN 10 ELSE 0 END+retention_probability*20)::INTEGER comprehensive_customer_score,CASE WHEN customer_age_days<=90 AND activity_status IN ('Highly Active','Active') THEN 'Onboarding' WHEN customer_age_days<=365 AND total_revenue>(SELECT avg(total_revenue) FROM cp) THEN 'Growth' WHEN retention_category IN ('Long-term','Medium-term') AND activity_status IN ('Highly Active','Active') THEN 'Mature' WHEN activity_status='At Risk' THEN 'At Risk' WHEN activity_status IN ('Dormant','Lost') THEN 'Churned' ELSE 'Developing' END lifecycle_stage FROM enriched), insights AS (SELECT *,CASE WHEN q1_transactions>=greatest(q2_transactions,q3_transactions,q4_transactions) THEN 'Q1 Peak' WHEN q2_transactions>=greatest(q1_transactions,q3_transactions,q4_transactions) THEN 'Q2 Peak' WHEN q3_transactions>=greatest(q1_transactions,q2_transactions,q4_transactions) THEN 'Q3 Peak' WHEN q4_transactions>=greatest(q1_transactions,q2_transactions,q3_transactions) THEN 'Q4 Peak' ELSE 'No Clear Pattern' END seasonal_preference,CASE WHEN transaction_value_volatility IS NULL OR transaction_value_volatility=0 THEN 'Single Transaction' WHEN transaction_value_volatility<=.3*avg_transaction_value THEN 'Very Consistent' WHEN transaction_value_volatility<=.6*avg_transaction_value THEN 'Consistent' WHEN transaction_value_volatility<=avg_transaction_value THEN 'Moderate Variance' ELSE 'High Variance' END transaction_consistency,CASE WHEN lifecycle_stage='Onboarding' AND comprehensive_customer_score>=70 THEN 'High Growth Potential' WHEN lifecycle_stage='Growth' AND value_tier IN ('Gold','Platinum') THEN 'Expansion Ready' WHEN lifecycle_stage='Mature' AND activity_status='Highly Active' THEN 'Loyalty Program Candidate' WHEN lifecycle_stage='At Risk' AND value_tier IN ('Silver','Gold','Platinum') THEN 'Recovery Priority' ELSE 'Standard Growth' END growth_potential FROM scored) SELECT customer_id,customer_name,customer_email,subsidiary_id,customer_segment profitability_segment,value_tier,lifecycle_stage,activity_status,retention_category,total_revenue,net_profit,transaction_count,avg_transactions_per_month,comprehensive_customer_score,retention_probability,seasonal_preference,transaction_consistency,growth_potential,CASE WHEN lifecycle_stage='Churned' AND value_tier IN ('Gold','Platinum') THEN 'Win-Back Campaign' WHEN lifecycle_stage='At Risk' THEN 'Retention Campaign' WHEN lifecycle_stage='Onboarding' THEN 'Onboarding Support' WHEN growth_potential='Expansion Ready' THEN 'Upsell Opportunity' WHEN value_tier='Platinum' AND activity_status='Highly Active' THEN 'VIP Treatment' ELSE 'Regular Engagement' END recommended_action,CASE WHEN value_tier='Platinum' THEN 'Weekly' WHEN value_tier='Gold' THEN 'Bi-weekly' WHEN value_tier='Silver' THEN 'Monthly' WHEN lifecycle_stage='At Risk' THEN 'Immediate' ELSE 'Quarterly' END engagement_frequency,customer_age_days,current_date segmentation_date,transaction_value_volatility,q1_transactions,q2_transactions,q3_transactions,q4_transactions,md5(customer_id||'_'||cast(current_date AS VARCHAR)) customer_analytics_id FROM insights WHERE customer_id IS NOT NULL AND total_revenue>0
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql`；原件第1–272行。

```sql
   1: -- Customer Analytics and Insights
   2: -- In-depth customer analysis, including behavior patterns, value stratification, and retention analysis
   3: with customer_profitability as (
   4:     select * from intermediate.int_netsuite2__customer_profitability
   5: ),
   6: 
   7: -- Customer transaction behavior analysis
   8: customer_behavior_patterns as (
   9:     select 
  10:         t.subsidiary_id,
  11:         tl.entity_id as customer_id,
  12:         'Customer_' || substring(tl.entity_id, 1, 8) as customer_name,
  13:         'customer_' || substring(tl.entity_id, 1, 8) || '@example.com' as customer_email,
  14:         
  15:         -- Transaction frequency pattern
  16:         count(distinct t.transaction_id) as total_transactions,
  17:         count(distinct date_trunc('month', t.accounting_period_ending)) as active_months,
  18:         count(distinct date_trunc('quarter', t.accounting_period_ending)) as active_quarters,
  19:         
  20:         -- Amount mode
  21:         sum(case when t.account_type_name = 'Income' then t.converted_amount else 0 end) as total_revenue,
  22:         avg(case when t.account_type_name = 'Income' then t.converted_amount else null end) as avg_transaction_value,
  23:         stddev(case when t.account_type_name = 'Income' then t.converted_amount else null end) as transaction_value_volatility,
  24:         max(case when t.account_type_name = 'Income' then t.converted_amount else 0 end) as max_transaction_value,
  25:         min(case when t.account_type_name = 'Income' and t.converted_amount > 0 then t.converted_amount else null end) as min_transaction_value,
  26:         
  27:         -- time pattern
  28:         min(t.accounting_period_ending) as first_transaction_date,
  29:         max(t.accounting_period_ending) as last_transaction_date,
  30:         datediff('day', min(t.accounting_period_ending), max(t.accounting_period_ending)) as customer_lifespan_days,
  31:         
  32:         -- seasonal pattern
  33:         count(distinct case when extract(quarter from t.accounting_period_ending) = 1 then t.transaction_id end) as q1_transactions,
  34:         count(distinct case when extract(quarter from t.accounting_period_ending) = 2 then t.transaction_id end) as q2_transactions,
  35:         count(distinct case when extract(quarter from t.accounting_period_ending) = 3 then t.transaction_id end) as q3_transactions,
  36:         count(distinct case when extract(quarter from t.accounting_period_ending) = 4 then t.transaction_id end) as q4_transactions,
  37:         
  38:         -- Recent activity
  39:         datediff('day', max(t.accounting_period_ending), current_date) as days_since_last_transaction,
  40:         
  41:         current_date as analysis_date
  42:         
  43:     from intermediate.int_netsuite2__transaction_details t
  44:     join staging.stg_netsuite2__transaction_lines tl
  45:         on t.transaction_line_id = tl.transaction_line_id
  46:     where tl.entity_id is not null
  47:         and t.account_type_name = 'Income'
  48:         and t.converted_amount > 0
  49:     group by t.subsidiary_id, tl.entity_id
  50: ),
  51: 
  52: -- Customer retention analysis (simplified version of Cohort analysis)
  53: customer_retention as (
  54:     select 
  55:         cbp.customer_id,
  56:         cbp.customer_name,
  57:         cbp.subsidiary_id,
  58:         cbp.first_transaction_date,
  59:         
  60:         -- Retention period calculation
  61:         case 
  62:             when cbp.customer_lifespan_days >= 365 then 'Long-term (1+ Years)'
  63:             when cbp.customer_lifespan_days >= 180 then 'Medium-term (6-12 Months)'
  64:             when cbp.customer_lifespan_days >= 90 then 'Short-term (3-6 Months)'
  65:             when cbp.customer_lifespan_days >= 30 then 'New Customer (1-3 Months)'
  66:             else 'Very New (<1 Month)'
  67:         end as retention_category,
  68:         
  69:         -- activity score
  70:         case 
  71:             when cbp.days_since_last_transaction <= 30 then 'Highly Active'
  72:             when cbp.days_since_last_transaction <= 90 then 'Active'
  73:             when cbp.days_since_last_transaction <= 180 then 'At Risk'
  74:             when cbp.days_since_last_transaction <= 365 then 'Dormant'
  75:             else 'Lost'
  76:         end as activity_status,
  77:         
  78:         -- Transaction frequency rating
  79:         case 
  80:             when cbp.active_months > 0 and cbp.customer_lifespan_days > 0 
  81:             then (cbp.total_transactions::float / (cbp.customer_lifespan_days / 30.0))
  82:             else 0 
  83:         end as avg_transactions_per_month,
  84:         
  85:         -- Predicted probability of retention
  86:         case 
  87:             when cbp.days_since_last_transaction <= 30 and cbp.total_transactions >= 5 then 0.95
  88:             when cbp.days_since_last_transaction <= 60 and cbp.total_transactions >= 3 then 0.80
  89:             when cbp.days_since_last_transaction <= 90 and cbp.total_transactions >= 2 then 0.60
  90:             when cbp.days_since_last_transaction <= 180 then 0.30
  91:             when cbp.days_since_last_transaction <= 365 then 0.10
  92:             else 0.05
  93:         end as retention_probability,
  94:         
  95:         cbp.total_transactions,
  96:         cbp.total_revenue,
  97:         cbp.avg_transaction_value,
  98:         cbp.days_since_last_transaction
  99:         
 100:     from customer_behavior_patterns cbp
 101: ),
 102: 
 103: -- Customer segmentation enhancement
 104: enhanced_customer_segmentation as (
 105:     select 
 106:         cp.customer_id,
 107:         cp.customer_name,
 108:         cp.customer_email,
 109:         cp.subsidiary_id,
 110:         cp.customer_segment as profitability_segment,
 111:         cr.retention_category,
 112:         cr.activity_status,
 113:         
 114:         -- RFM-Enhanced Analysis
 115:         cp.total_revenue,
 116:         cp.net_profit,
 117:         cp.transaction_count,
 118:         cp.customer_age_days,
 119:         cr.avg_transactions_per_month,
 120:         cr.retention_probability,
 121:         
 122:         -- value stratification
 123:         case 
 124:             when cp.total_revenue >= (select percentile_cont(0.9) within group (order by total_revenue) from customer_profitability) then 'Platinum'
 125:             when cp.total_revenue >= (select percentile_cont(0.7) within group (order by total_revenue) from customer_profitability) then 'Gold'
 126:             when cp.total_revenue >= (select percentile_cont(0.5) within group (order by total_revenue) from customer_profitability) then 'Silver'
 127:             when cp.total_revenue >= (select percentile_cont(0.3) within group (order by total_revenue) from customer_profitability) then 'Bronze'
 128:             else 'Basic'
 129:         end as value_tier,
 130:         
 131:         -- Overall customer rating (0-100)
 132:         least(100, 
 133:             (cp.revenue_score * 20) +
 134:             (cp.frequency_score * 15) +
 135:             (cp.margin_score * 20) +
 136:             (case when cr.activity_status = 'Highly Active' then 25
 137:                   when cr.activity_status = 'Active' then 20
 138:                   when cr.activity_status = 'At Risk' then 10
 139:                   when cr.activity_status = 'Dormant' then 5
 140:                   else 0 end) +
 141:             (case when cr.retention_category = 'Long-term (1+ Years)' then 20
 142:                   when cr.retention_category = 'Medium-term (6-12 Months)' then 15
 143:                   when cr.retention_category = 'Short-term (3-6 Months)' then 10
 144:                   when cr.retention_category = 'New Customer (1-3 Months)' then 5
 145:                   else 0 end)
 146:         ) as comprehensive_customer_score,
 147:         
 148:         -- Customer life cycle stages
 149:         case 
 150:             when cp.customer_age_days <= 90 and cr.activity_status in ('Highly Active', 'Active') then 'Onboarding'
 151:             when cp.customer_age_days <= 365 and cp.total_revenue > (select avg(total_revenue) from customer_profitability) then 'Growth'
 152:             when cr.retention_category in ('Long-term (1+ Years)', 'Medium-term (6-12 Months)') and cr.activity_status in ('Highly Active', 'Active') then 'Mature'
 153:             when cr.activity_status = 'At Risk' then 'At Risk'
 154:             when cr.activity_status in ('Dormant', 'Lost') then 'Churned'
 155:             else 'Developing'
 156:         end as lifecycle_stage,
 157:         
 158:         current_date as segmentation_date
 159:         
 160:     from customer_profitability cp
 161:     left join customer_retention cr on cp.customer_id = cr.customer_id
 162: ),
 163: 
 164: -- Customer Behavior Insights
 165: customer_insights as (
 166:     select 
 167:         ecs.*,
 168:         cbp.transaction_value_volatility,
 169:         cbp.q1_transactions,
 170:         cbp.q2_transactions,
 171:         cbp.q3_transactions,
 172:         cbp.q4_transactions,
 173:         
 174:         -- seasonal preference
 175:         case 
 176:             when greatest(cbp.q1_transactions, cbp.q2_transactions, cbp.q3_transactions, cbp.q4_transactions) = cbp.q1_transactions then 'Q1 Peak'
 177:             when greatest(cbp.q1_transactions, cbp.q2_transactions, cbp.q3_transactions, cbp.q4_transactions) = cbp.q2_transactions then 'Q2 Peak'
 178:             when greatest(cbp.q1_transactions, cbp.q2_transactions, cbp.q3_transactions, cbp.q4_transactions) = cbp.q3_transactions then 'Q3 Peak'
 179:             when greatest(cbp.q1_transactions, cbp.q2_transactions, cbp.q3_transactions, cbp.q4_transactions) = cbp.q4_transactions then 'Q4 Peak'
 180:             else 'No Clear Pattern'
 181:         end as seasonal_preference,
 182:         
 183:         -- transaction consistency
 184:         case 
 185:             when cbp.transaction_value_volatility is null or cbp.transaction_value_volatility = 0 then 'Single Transaction'
 186:             when cbp.transaction_value_volatility <= cbp.avg_transaction_value * 0.3 then 'Very Consistent'
 187:             when cbp.transaction_value_volatility <= cbp.avg_transaction_value * 0.6 then 'Consistent'
 188:             when cbp.transaction_value_volatility <= cbp.avg_transaction_value * 1.0 then 'Moderate Variance'
 189:             else 'High Variance'
 190:         end as transaction_consistency,
 191:         
 192:         -- Growth potential assessment
 193:         case 
 194:             when ecs.lifecycle_stage = 'Onboarding' and ecs.comprehensive_customer_score >= 70 then 'High Growth Potential'
 195:             when ecs.lifecycle_stage = 'Growth' and ecs.value_tier in ('Gold', 'Platinum') then 'Expansion Ready'
 196:             when ecs.lifecycle_stage = 'Mature' and ecs.activity_status = 'Highly Active' then 'Loyalty Program Candidate'
 197:             when ecs.lifecycle_stage = 'At Risk' and ecs.value_tier in ('Silver', 'Gold', 'Platinum') then 'Recovery Priority'
 198:             else 'Standard Growth'
 199:         end as growth_potential,
 200:         
 201:         -- Recommended action
 202:         case 
 203:             when ecs.lifecycle_stage = 'Churned' and ecs.value_tier in ('Gold', 'Platinum') then 'Win-Back Campaign'
 204:             when ecs.lifecycle_stage = 'At Risk' then 'Retention Campaign'
 205:             when ecs.lifecycle_stage = 'Onboarding' then 'Onboarding Support'
 206:             when growth_potential = 'Expansion Ready' then 'Upsell Opportunity'
 207:             when ecs.value_tier = 'Platinum' and ecs.activity_status = 'Highly Active' then 'VIP Treatment'
 208:             else 'Regular Engagement'
 209:         end as recommended_action,
 210:         
 211:         -- Contact frequency recommendations
 212:         case 
 213:             when ecs.value_tier = 'Platinum' then 'Weekly'
 214:             when ecs.value_tier = 'Gold' then 'Bi-weekly'
 215:             when ecs.value_tier = 'Silver' then 'Monthly'
 216:             when ecs.lifecycle_stage = 'At Risk' then 'Immediate'
 217:             else 'Quarterly'
 218:         end as engagement_frequency
 219:         
 220:     from enhanced_customer_segmentation ecs
 221:     left join customer_behavior_patterns cbp on ecs.customer_id = cbp.customer_id
 222: )
 223: 
 224: select 
 225:     customer_id,
 226:     customer_name,
 227:     customer_email,
 228:     subsidiary_id,
 229:     
 230:     -- Core categories
 231:     profitability_segment,
 232:     value_tier,
 233:     lifecycle_stage,
 234:     activity_status,
 235:     retention_category,
 236:     
 237:     -- financial indicators
 238:     total_revenue,
 239:     net_profit,
 240:     transaction_count,
 241:     avg_transactions_per_month,
 242:     
 243:     -- score
 244:     comprehensive_customer_score,
 245:     retention_probability,
 246:     
 247:     -- behavioral insights
 248:     seasonal_preference,
 249:     transaction_consistency,
 250:     growth_potential,
 251:     
 252:     -- suggestion
 253:     recommended_action,
 254:     engagement_frequency,
 255:     
 256:     -- time indicator
 257:     customer_age_days,
 258:     segmentation_date,
 259:     
 260:     -- Trading pattern statistics
 261:     transaction_value_volatility,
 262:     q1_transactions,
 263:     q2_transactions, 
 264:     q3_transactions,
 265:     q4_transactions,
 266:     
 267:     md5(cast(customer_id as varchar) || '_' || cast(segmentation_date as varchar)) as customer_analytics_id
 268:     
 269: from customer_insights
 270: where customer_id is not null
 271:     and total_revenue > 0
 272: order by comprehensive_customer_score desc, total_revenue desc
```

## 3. agent看到的材料与不确定性

已检视该题全部67个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。


四档：**没有迹象**。

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

## 4. 核实查询与诊断

核实查询共**2条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__customer_profitability' source_table,count(*) rows FROM intermediate.int_netsuite2__customer_profitability UNION ALL SELECT 'intermediate.int_netsuite2__transaction_details' source_table,count(*) rows FROM intermediate.int_netsuite2__transaction_details UNION ALL SELECT 'staging.stg_netsuite2__transaction_lines' source_table,count(*) rows FROM staging.stg_netsuite2__transaction_lines
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ....int_netsuite2__customer_profitability' source_table,count(*) rows FROM intermediate.int_netsuite2__customer_profitability...\n                                                                         ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__customer_profitability' source_table,count(*) source_rows FROM intermediate.int_netsuite2__customer_profitability UNION ALL SELECT 'intermediate.int_netsuite2__transaction_details' source_table,count(*) source_rows FROM intermediate.int_netsuite2__transaction_details UNION ALL SELECT 'staging.stg_netsuite2__transaction_lines' source_table,count(*) source_rows FROM staging.stg_netsuite2__transaction_lines
```

```json
{"columns": ["source_table", "source_rows"], "result": [["intermediate.int_netsuite2__customer_profitability", 115], ["intermediate.int_netsuite2__transaction_details", 700], ["staging.stg_netsuite2__transaction_lines", 700]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 4}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["customer_id", "customer_analytics_id", "subsidiary_id"]`；比较列：`["customer_id", "customer_name", "customer_email", "subsidiary_id", "profitability_segment", "value_tier", "lifecycle_stage", "activity_status", "retention_category", "total_revenue", "net_profit", "transaction_count", "avg_transactions_per_month", "comprehensive_customer_score", "retention_probability", "seasonal_preference", "transaction_consistency", "growth_potential", "recommended_action", "engagement_frequency", "customer_age_days", "transaction_value_volatility", "q1_transactions", "q2_transactions", "q3_transactions", "q4_transactions", "customer_analytics_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1544 | False |
| L1 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1544 | False |
| L2 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1544 | False |
| L3 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1544 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_id | 0 | 0 | 0 | 0 |
| customer_analytics_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| profitability_segment | 0 | 0 | 0 | 0 |
| value_tier | 0 | 0 | 0 | 0 |
| lifecycle_stage | 0 | 0 | 0 | 0 |
| activity_status | 0 | 0 | 0 | 0 |
| retention_category | 137 | 137 | 137 | 137 |
| total_revenue | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| transaction_count | 0 | 0 | 0 | 0 |
| avg_transactions_per_month | 137 | 137 | 137 | 137 |
| comprehensive_customer_score | 82 | 82 | 82 | 82 |
| retention_probability | 0 | 0 | 0 | 0 |
| seasonal_preference | 0 | 0 | 0 | 0 |
| transaction_consistency | 0 | 0 | 0 | 0 |
| growth_potential | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| engagement_frequency | 0 | 0 | 0 | 0 |
| customer_age_days | 0 | 0 | 0 | 0 |
| transaction_value_volatility | 0 | 0 | 0 | 0 |
| q1_transactions | 0 | 0 | 0 | 0 |
| q2_transactions | 0 | 0 | 0 | 0 |
| q3_transactions | 0 | 0 | 0 | 0 |
| q4_transactions | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_netsuite2_customer_analytics/baseline.sql`；SHA-256：`4a0d3792adbe9e732d315a667ae38d668b022bbed5b35a705c4c74746133e751`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1544 | False |
| L1 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1544 | False |
| L2 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1544 | False |
| L3 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1544 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_id | 0 | 0 | 0 | 0 |
| customer_analytics_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| profitability_segment | 0 | 0 | 0 | 0 |
| value_tier | 0 | 0 | 0 | 0 |
| lifecycle_stage | 0 | 0 | 0 | 0 |
| activity_status | 0 | 0 | 0 | 0 |
| retention_category | 137 | 137 | 137 | 137 |
| total_revenue | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| transaction_count | 0 | 0 | 0 | 0 |
| avg_transactions_per_month | 137 | 137 | 137 | 137 |
| comprehensive_customer_score | 82 | 82 | 82 | 82 |
| retention_probability | 0 | 0 | 0 | 0 |
| seasonal_preference | 0 | 0 | 0 | 0 |
| transaction_consistency | 0 | 0 | 0 | 0 |
| growth_potential | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| engagement_frequency | 0 | 0 | 0 | 0 |
| customer_age_days | 0 | 0 | 0 | 0 |
| transaction_value_volatility | 0 | 0 | 0 | 0 |
| q1_transactions | 0 | 0 | 0 | 0 |
| q2_transactions | 0 | 0 | 0 | 0 |
| q3_transactions | 0 | 0 | 0 | 0 |
| q4_transactions | 0 | 0 | 0 | 0 |

### second_join

SQL：`data/022_work/impl-013_netsuite2_customer_analytics/second_join.sql`；SHA-256：`8c4faa786a0f092138375dbbc9092f90c2da7b0ed2090b593ff265ca73778eb4`。

替换offset=3566，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
FROM enriched)
-- 新
FROM enriched e LEFT JOIN (SELECT customer_id AS b_id FROM behavior) b ON e.customer_id=b.b_id)
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 181/181 | 0/0 | 0/0 | 181 | 181 | 466 | False |
| L1 | 181/181 | 0/0 | 0/0 | 181 | 181 | 466 | False |
| L2 | 181/181 | 0/0 | 0/0 | 181 | 181 | 466 | False |
| L3 | 181/181 | 0/0 | 0/0 | 181 | 181 | 466 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_id | 0 | 0 | 0 | 0 |
| customer_analytics_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| profitability_segment | 0 | 0 | 0 | 0 |
| value_tier | 0 | 0 | 0 | 0 |
| lifecycle_stage | 0 | 0 | 0 | 0 |
| activity_status | 0 | 0 | 0 | 0 |
| retention_category | 181 | 181 | 181 | 181 |
| total_revenue | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| transaction_count | 0 | 0 | 0 | 0 |
| avg_transactions_per_month | 181 | 181 | 181 | 181 |
| comprehensive_customer_score | 104 | 104 | 104 | 104 |
| retention_probability | 0 | 0 | 0 | 0 |
| seasonal_preference | 0 | 0 | 0 | 0 |
| transaction_consistency | 0 | 0 | 0 | 0 |
| growth_potential | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| engagement_frequency | 0 | 0 | 0 | 0 |
| customer_age_days | 0 | 0 | 0 | 0 |
| transaction_value_volatility | 0 | 0 | 0 | 0 |
| q1_transactions | 0 | 0 | 0 | 0 |
| q2_transactions | 0 | 0 | 0 | 0 |
| q3_transactions | 0 | 0 | 0 | 0 |
| q4_transactions | 0 | 0 | 0 | 0 |

### frequency_zero

SQL：`data/022_work/impl-013_netsuite2_customer_analytics/frequency_zero.sql`；SHA-256：`9011fb6d77b8e0bc4cecb52a50cb8551f8bf307b9bd32d49edc19b02cb3fdaca`。

替换offset=2014，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
total_transactions/nullif(customer_lifespan_days/30.0,0) avg_transactions_per_month
-- 新
coalesce(total_transactions/nullif(customer_lifespan_days/30.0,0),0) avg_transactions_per_month
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1407 | False |
| L1 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1407 | False |
| L2 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1407 | False |
| L3 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1407 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_id | 0 | 0 | 0 | 0 |
| customer_analytics_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| profitability_segment | 0 | 0 | 0 | 0 |
| value_tier | 0 | 0 | 0 | 0 |
| lifecycle_stage | 0 | 0 | 0 | 0 |
| activity_status | 0 | 0 | 0 | 0 |
| retention_category | 137 | 137 | 137 | 137 |
| total_revenue | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| transaction_count | 0 | 0 | 0 | 0 |
| avg_transactions_per_month | 0 | 0 | 0 | 0 |
| comprehensive_customer_score | 82 | 82 | 82 | 82 |
| retention_probability | 0 | 0 | 0 | 0 |
| seasonal_preference | 0 | 0 | 0 | 0 |
| transaction_consistency | 0 | 0 | 0 | 0 |
| growth_potential | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| engagement_frequency | 0 | 0 | 0 | 0 |
| customer_age_days | 0 | 0 | 0 | 0 |
| transaction_value_volatility | 0 | 0 | 0 | 0 |
| q1_transactions | 0 | 0 | 0 | 0 |
| q2_transactions | 0 | 0 | 0 | 0 |
| q3_transactions | 0 | 0 | 0 | 0 |
| q4_transactions | 0 | 0 | 0 | 0 |

### retention_labels

SQL：`data/022_work/impl-013_netsuite2_customer_analytics/retention_labels.sql`；SHA-256：`9af4023faeef4da58d317bf7068618ba340b6c0a72fe4ac21746ddeb81b1b758`。

替换offset=1523，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CASE WHEN customer_lifespan_days>=365 THEN 'Long-term' WHEN customer_lifespan_days>=180 THEN 'Medium-term' WHEN customer_lifespan_days>=90 THEN 'Short-term' WHEN customer_lifespan_days>=30 THEN 'New' ELSE 'Very New' END retention_category
-- 新
CASE WHEN customer_lifespan_days>=365 THEN 'Long-term (1+ Years)' WHEN customer_lifespan_days>=180 THEN 'Medium-term (6-12 Months)' WHEN customer_lifespan_days>=90 THEN 'Short-term (3-6 Months)' WHEN customer_lifespan_days>=30 THEN 'New Customer (1-3 Months)' ELSE 'Very New (<1 Month)' END retention_category
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1407 | False |
| L1 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1407 | False |
| L2 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1407 | False |
| L3 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1407 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_id | 0 | 0 | 0 | 0 |
| customer_analytics_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| profitability_segment | 0 | 0 | 0 | 0 |
| value_tier | 0 | 0 | 0 | 0 |
| lifecycle_stage | 0 | 0 | 0 | 0 |
| activity_status | 0 | 0 | 0 | 0 |
| retention_category | 0 | 0 | 0 | 0 |
| total_revenue | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| transaction_count | 0 | 0 | 0 | 0 |
| avg_transactions_per_month | 137 | 137 | 137 | 137 |
| comprehensive_customer_score | 82 | 82 | 82 | 82 |
| retention_probability | 0 | 0 | 0 | 0 |
| seasonal_preference | 0 | 0 | 0 | 0 |
| transaction_consistency | 0 | 0 | 0 | 0 |
| growth_potential | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| engagement_frequency | 0 | 0 | 0 | 0 |
| customer_age_days | 0 | 0 | 0 | 0 |
| transaction_value_volatility | 0 | 0 | 0 | 0 |
| q1_transactions | 0 | 0 | 0 | 0 |
| q2_transactions | 0 | 0 | 0 | 0 |
| q3_transactions | 0 | 0 | 0 | 0 |
| q4_transactions | 0 | 0 | 0 | 0 |

### score_weights

SQL：`data/022_work/impl-013_netsuite2_customer_analytics/score_weights.sql`；SHA-256：`7ed7d5cfd7dbb0569a2509a73086f9b08990b2b62eede4cb4800ec93f11371a3`。

替换offset=2886，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
least(100,revenue_score*10+frequency_score*5+margin_score*5+CASE WHEN activity_status='Highly Active' THEN 15 WHEN activity_status='Active' THEN 10 ELSE 0 END+retention_probability*20)::INTEGER comprehensive_customer_score
-- 新
least(100,revenue_score*20+frequency_score*15+margin_score*20+CASE WHEN activity_status='Highly Active' THEN 25 WHEN activity_status='Active' THEN 20 WHEN activity_status='At Risk' THEN 10 WHEN activity_status='Dormant' THEN 5 ELSE 0 END+CASE WHEN retention_category='Long-term' THEN 20 WHEN retention_category='Medium-term' THEN 15 WHEN retention_category='Short-term' THEN 10 WHEN retention_category='New' THEN 5 ELSE 0 END)::INTEGER comprehensive_customer_score
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1462 | False |
| L1 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1462 | False |
| L2 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1462 | False |
| L3 | 137/181 | 0/0 | 0/44 | 137 | 181 | 1462 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_id | 0 | 0 | 0 | 0 |
| customer_analytics_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| profitability_segment | 0 | 0 | 0 | 0 |
| value_tier | 0 | 0 | 0 | 0 |
| lifecycle_stage | 0 | 0 | 0 | 0 |
| activity_status | 0 | 0 | 0 | 0 |
| retention_category | 137 | 137 | 137 | 137 |
| total_revenue | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| transaction_count | 0 | 0 | 0 | 0 |
| avg_transactions_per_month | 137 | 137 | 137 | 137 |
| comprehensive_customer_score | 0 | 0 | 0 | 0 |
| retention_probability | 0 | 0 | 0 | 0 |
| seasonal_preference | 0 | 0 | 0 | 0 |
| transaction_consistency | 0 | 0 | 0 | 0 |
| growth_potential | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| engagement_frequency | 0 | 0 | 0 | 0 |
| customer_age_days | 0 | 0 | 0 | 0 |
| transaction_value_volatility | 0 | 0 | 0 | 0 |
| q1_transactions | 0 | 0 | 0 | 0 |
| q2_transactions | 0 | 0 | 0 | 0 |
| q3_transactions | 0 | 0 | 0 | 0 |
| q4_transactions | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：second_join；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- second_join：C；主项。契约customer_insights再LEFT JOIN behavior；agent遗漏导致少44行。（行减少0，格减少1078）
- frequency_zero：C；参与因素。契约lifespan=0时频率为0，agent NULL。（行减少0，格减少137）
- retention_labels：O；参与因素。契约明确简短标签，gold输出带括号标签。（行减少0，格减少137）
- score_weights：A；参与因素。契约未给weighted sum的权重及bonus具体数字。（行减少0，格减少82）

## 规则问题

grain写一行/customer，但business_logic明示两次按customer_id连接，会放大多subsidiary记录；按明确可执行连接规定判遗漏C，不自行删除第二次连接。
