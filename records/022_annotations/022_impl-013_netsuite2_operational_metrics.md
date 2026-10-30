# impl-013 / netsuite2_operational_metrics（全量；v2）

## 1. 差异与结论

department_revenue无Income时用NULL而非契约0，后续IS NOT NULL排掉585行并改变窗口分母；单改收入默认恢复行但暴露其他不同列，行规模不减，格子大幅减少。净利率零分母NULL/0单修也减格，C参与因素。class遗漏与其他候选本批单修不减，不计参与因素。

主要原因：**C**；参与因素：C：zero_net_margin_percentage；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| zero_department_revenue | C | 0 | 12661 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_netsuite2_operational_metrics.md](../../records/022_packages/022_impl-013_netsuite2_operational_metrics.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_netsuite2_operational_metrics/022_impl-013_netsuite2_operational_metrics.json`。
- 比较结果：[022_reruns_impl-013_netsuite2_operational_metrics.json](../022_reruns_impl-013_netsuite2_operational_metrics.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第3007–3105行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_operational_metrics.sql`；原件第1–1行。

```sql
   1: WITH grouped AS (SELECT t.subsidiary_id,l.department_id,d.name department_name,l.location_id,loc.name location_name,l.class_id,date_trunc('month',t.accounting_period_ending)::DATE performance_month,sum(t.converted_amount) FILTER(WHERE t.account_type_name='Income') department_revenue, sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='COGS') department_cogs,sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Expense') department_expenses,count(DISTINCT t.transaction_id) transaction_count,count(DISTINCT t.transaction_id) FILTER(WHERE t.account_type_name='Income') revenue_transactions,count(DISTINCT t.transaction_id) FILTER(WHERE t.account_type_name IN ('COGS','Expense')) expense_transactions,count(DISTINCT l.entity_id) unique_entities_involved FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuite2__transaction_lines l USING(transaction_line_id) LEFT JOIN staging.stg_netsuite2__departments d ON d.department_id=l.department_id LEFT JOIN intermediate.int_netsuite2__locations loc ON loc.location_id=l.location_id WHERE t.accounting_period_ending>=current_date-interval '24 months' GROUP BY ALL), calc AS (SELECT *,coalesce(department_revenue,0)-coalesce(department_cogs,0) gross_profit,coalesce(department_revenue,0)-coalesce(department_cogs,0)-coalesce(department_expenses,0) net_profit,(coalesce(department_revenue,0)-coalesce(department_cogs,0))/nullif(department_revenue,0) gross_margin_percentage,(coalesce(department_revenue,0)-coalesce(department_cogs,0)-coalesce(department_expenses,0))/nullif(department_revenue,0) net_margin_percentage,department_revenue/nullif(department_expenses,0) revenue_to_expense_ratio,lag(department_revenue) OVER(PARTITION BY subsidiary_id,department_id ORDER BY performance_month) prev_month_revenue,lag(department_revenue,12) OVER(PARTITION BY subsidiary_id,department_id ORDER BY performance_month) prior_year_revenue,avg(department_revenue) OVER(PARTITION BY subsidiary_id,department_id ORDER BY performance_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) three_month_avg_revenue,avg((coalesce(department_revenue,0)-coalesce(department_cogs,0))/nullif(department_revenue,0)) OVER(PARTITION BY subsidiary_id,department_id ORDER BY performance_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) three_month_avg_margin FROM grouped), calculated AS (SELECT *,round((department_revenue-prev_month_revenue)/nullif(prev_month_revenue,0)*100,2) month_over_month_growth,round((department_revenue-prior_year_revenue)/nullif(prior_year_revenue,0)*100,2) year_over_year_growth,CASE WHEN net_margin_percentage>=.2 AND revenue_to_expense_ratio>=2 THEN 'Excellent' WHEN net_margin_percentage>=.1 AND revenue_to_expense_ratio>=1.5 THEN 'Good' WHEN net_margin_percentage>=.05 AND revenue_to_expense_ratio>=1.2 THEN 'Fair' WHEN net_margin_percentage>0 THEN 'Poor' ELSE 'Loss Making' END performance_grade FROM calc), bench AS (SELECT *,rank() OVER(PARTITION BY subsidiary_id,performance_month ORDER BY department_revenue DESC) revenue_rank_within_company,rank() OVER(PARTITION BY subsidiary_id,performance_month ORDER BY net_margin_percentage DESC) margin_rank_within_company,department_revenue/nullif(avg(department_revenue) OVER(PARTITION BY subsidiary_id,performance_month),0) revenue_vs_company_avg,net_margin_percentage-avg(net_margin_percentage) OVER(PARTITION BY subsidiary_id,performance_month) margin_vs_company_avg,department_revenue/nullif(sum(department_revenue) OVER(PARTITION BY subsidiary_id,performance_month),0) internal_market_share,CASE WHEN department_revenue>1.1*three_month_avg_revenue THEN 'Accelerating' WHEN department_revenue>.9*three_month_avg_revenue THEN 'Stable' WHEN department_revenue>.8*three_month_avg_revenue THEN 'Declining' ELSE 'Sharp Decline' END revenue_trend,CASE WHEN gross_margin_percentage>1.05*three_month_avg_margin THEN 'Improving' WHEN gross_margin_percentage>.95*three_month_avg_margin THEN 'Stable' ELSE 'Declining' END margin_trend FROM calculated) SELECT subsidiary_id,department_id,department_name,location_id,location_name,performance_month,department_revenue,gross_profit,net_profit,gross_margin_percentage,net_margin_percentage,revenue_to_expense_ratio,month_over_month_growth,year_over_year_growth,three_month_avg_revenue,revenue_trend,margin_trend,performance_grade,revenue_rank_within_company,margin_rank_within_company,revenue_vs_company_avg,margin_vs_company_avg,internal_market_share,CASE WHEN year_over_year_growth < -20 THEN 'Revenue Decline Alert' WHEN net_margin_percentage<0 AND month_over_month_growth < -10 THEN 'Loss Alert' WHEN revenue_to_expense_ratio<1 THEN 'Efficiency Alert' WHEN gross_margin_percentage<.1 THEN 'Margin Alert' ELSE 'Normal' END alert_status,CASE WHEN performance_grade='Loss Making' THEN 'Urgent restructuring required' WHEN performance_grade='Poor' AND revenue_trend='Declining' THEN 'Review operations and cost structure' WHEN margin_trend='Declining' AND revenue_trend='Stable' THEN 'Focus on cost optimization' WHEN revenue_trend='Declining' AND margin_trend='Stable' THEN 'Increase sales and marketing efforts' WHEN performance_grade IN ('Good','Excellent') THEN 'Scale successful practices' ELSE 'Monitor performance closely' END improvement_recommendation,CASE WHEN performance_grade='Excellent' AND revenue_trend='Accelerating' THEN 'Increase Investment' WHEN performance_grade IN ('Good','Excellent') AND internal_market_share<.3 THEN 'Growth Investment' WHEN performance_grade='Fair' AND margin_trend='Improving' THEN 'Selective Investment' WHEN performance_grade IN ('Poor','Loss Making') THEN 'Review Investment' ELSE 'Maintain Current Investment' END investment_recommendation,current_date analysis_date,CASE WHEN subsidiary_id IS NULL OR department_id IS NULL THEN NULL ELSE md5(subsidiary_id||'_'||department_id||'_'||cast(performance_month AS VARCHAR)) END operational_metrics_id FROM bench WHERE performance_month>=date_trunc('month',current_date-interval '12 months') AND department_revenue IS NOT NULL
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/marts/netsuite2_operational_metrics.sql`；原件第1–301行。

```sql
   1: -- Operational Metrics and KPIs
   2: -- Operational indicators and key performance indicators, including efficiency, productivity, department performance analysis
   3: with departmental_performance as (
   4:     select 
   5:         t.subsidiary_id,
   6:         tl.department_id,
   7:         d.name as department_name,
   8:         tl.location_id,
   9:         l.name as location_name,
  10:         tl.class_id,
  11:         c.name as class_name,
  12:         
  13:         -- time dimension
  14:         date_trunc('month', t.accounting_period_ending) as performance_month,
  15:         date_trunc('quarter', t.accounting_period_ending) as performance_quarter,
  16:         
  17:         -- revenue metric
  18:         sum(case when t.account_type_name = 'Income' then t.converted_amount else 0 end) as department_revenue,
  19:         
  20:         -- cost index
  21:         sum(case when t.account_type_name = 'COGS' then abs(t.converted_amount) else 0 end) as department_cogs,
  22:         sum(case when t.account_type_name = 'Expense' then abs(t.converted_amount) else 0 end) as department_expenses,
  23:         
  24:         -- trading activity
  25:         count(distinct t.transaction_id) as transaction_count,
  26:         count(distinct case when t.account_type_name = 'Income' then t.transaction_id end) as revenue_transactions,
  27:         count(distinct case when t.account_type_name in ('COGS', 'Expense') then t.transaction_id end) as expense_transactions,
  28:         
  29:         -- Employee related (if there is an employee assigned to the transaction)
  30:         count(distinct tl.entity_id) as unique_entities_involved,
  31:         
  32:         current_date as analysis_date
  33:         
  34:     from intermediate.int_netsuite2__transaction_details t
  35:     join staging.stg_netsuite2__transaction_lines tl
  36:         on t.transaction_line_id = tl.transaction_line_id
  37:     left join staging.stg_netsuite2__departments d
  38:         on tl.department_id = d.department_id
  39:     left join staging.stg_netsuite2__locations l
  40:         on tl.location_id = l.location_id
  41:     left join staging.stg_netsuite2__classes c
  42:         on tl.class_id = c.class_id
  43:     where t.accounting_period_ending >= current_date - interval '24 months'
  44:     group by 
  45:         t.subsidiary_id, tl.department_id, d.name, tl.location_id, l.name, 
  46:         tl.class_id, c.name, performance_month, performance_quarter
  47: ),
  48: 
  49: operational_efficiency as (
  50:     select 
  51:         dp.*,
  52:         
  53:         -- efficiency index
  54:         case 
  55:             when dp.department_expenses > 0 
  56:             then dp.department_revenue / dp.department_expenses
  57:             else null 
  58:         end as revenue_to_expense_ratio,
  59:         
  60:         -- gross profit and gross profit margin
  61:         (dp.department_revenue - dp.department_cogs) as gross_profit,
  62:         case 
  63:             when dp.department_revenue > 0 
  64:             then (dp.department_revenue - dp.department_cogs) / dp.department_revenue
  65:             else 0 
  66:         end as gross_margin_percentage,
  67:         
  68:         -- Net profit (simplified)
  69:         (dp.department_revenue - dp.department_cogs - dp.department_expenses) as net_profit,
  70:         case 
  71:             when dp.department_revenue > 0 
  72:             then (dp.department_revenue - dp.department_cogs - dp.department_expenses) / dp.department_revenue
  73:             else 0 
  74:         end as net_margin_percentage,
  75:         
  76:         -- average transaction value
  77:         case 
  78:             when dp.revenue_transactions > 0 
  79:             then dp.department_revenue / dp.revenue_transactions
  80:             else 0 
  81:         end as avg_revenue_per_transaction,
  82:         
  83:         -- cost efficiency
  84:         case 
  85:             when dp.expense_transactions > 0 
  86:             then dp.department_expenses / dp.expense_transactions
  87:             else 0 
  88:         end as avg_expense_per_transaction,
  89:         
  90:         -- productivity indicators
  91:         case 
  92:             when dp.unique_entities_involved > 0 
  93:             then dp.department_revenue / dp.unique_entities_involved
  94:             else 0 
  95:         end as revenue_per_entity
  96:         
  97:     from departmental_performance dp
  98: ),
  99: 
 100: monthly_trends as (
 101:     select 
 102:         oe.subsidiary_id,
 103:         oe.department_id,
 104:         oe.department_name,
 105:         oe.location_id,
 106:         oe.location_name,
 107:         oe.performance_month,
 108:         
 109:         -- Indicators for the month
 110:         oe.department_revenue,
 111:         oe.gross_profit,
 112:         oe.net_profit,
 113:         oe.gross_margin_percentage,
 114:         oe.net_margin_percentage,
 115:         oe.revenue_to_expense_ratio,
 116:         
 117:         -- Year-on-year and month-on-month
 118:         lag(oe.department_revenue, 1) over (
 119:             partition by oe.subsidiary_id, oe.department_id 
 120:             order by oe.performance_month
 121:         ) as prev_month_revenue,
 122:         
 123:         lag(oe.department_revenue, 12) over (
 124:             partition by oe.subsidiary_id, oe.department_id 
 125:             order by oe.performance_month
 126:         ) as same_month_last_year_revenue,
 127:         
 128:         -- moving average
 129:         avg(oe.department_revenue) over (
 130:             partition by oe.subsidiary_id, oe.department_id 
 131:             order by oe.performance_month 
 132:             rows between 2 preceding and current row
 133:         ) as three_month_avg_revenue,
 134:         
 135:         avg(oe.gross_margin_percentage) over (
 136:             partition by oe.subsidiary_id, oe.department_id 
 137:             order by oe.performance_month 
 138:             rows between 2 preceding and current row
 139:         ) as three_month_avg_margin,
 140:         
 141:         oe.analysis_date
 142:         
 143:     from operational_efficiency oe
 144: ),
 145: 
 146: performance_analysis as (
 147:     select 
 148:         mt.*,
 149:         
 150:         -- Growth rate calculation
 151:         case 
 152:             when mt.prev_month_revenue > 0 
 153:             then round(((mt.department_revenue - mt.prev_month_revenue) / mt.prev_month_revenue) * 100, 2)
 154:             else null 
 155:         end as month_over_month_growth,
 156:         
 157:         case 
 158:             when mt.same_month_last_year_revenue > 0 
 159:             then round(((mt.department_revenue - mt.same_month_last_year_revenue) / mt.same_month_last_year_revenue) * 100, 2)
 160:             else null 
 161:         end as year_over_year_growth,
 162:         
 163:         -- trend analysis
 164:         case 
 165:             when mt.department_revenue > mt.three_month_avg_revenue * 1.1 then 'Accelerating'
 166:             when mt.department_revenue > mt.three_month_avg_revenue * 0.9 then 'Stable'
 167:             when mt.department_revenue > mt.three_month_avg_revenue * 0.8 then 'Declining'
 168:             else 'Sharp Decline'
 169:         end as revenue_trend,
 170:         
 171:         case 
 172:             when mt.gross_margin_percentage > mt.three_month_avg_margin * 1.05 then 'Improving'
 173:             when mt.gross_margin_percentage > mt.three_month_avg_margin * 0.95 then 'Stable'
 174:             else 'Declining'
 175:         end as margin_trend,
 176:         
 177:         -- performance rating
 178:         case 
 179:             when mt.net_margin_percentage >= 0.2 and mt.revenue_to_expense_ratio >= 2.0 then 'Excellent'
 180:             when mt.net_margin_percentage >= 0.1 and mt.revenue_to_expense_ratio >= 1.5 then 'Good'
 181:             when mt.net_margin_percentage >= 0.05 and mt.revenue_to_expense_ratio >= 1.2 then 'Fair'
 182:             when mt.net_margin_percentage > 0 then 'Poor'
 183:             else 'Loss Making'
 184:         end as performance_grade
 185:         
 186:     from monthly_trends mt
 187: ),
 188: 
 189: department_benchmarking as (
 190:     select 
 191:         pa.*,
 192:         
 193:         -- Ranking within departments
 194:         rank() over (
 195:             partition by pa.subsidiary_id, pa.performance_month 
 196:             order by pa.department_revenue desc
 197:         ) as revenue_rank_within_company,
 198:         
 199:         rank() over (
 200:             partition by pa.subsidiary_id, pa.performance_month 
 201:             order by pa.net_margin_percentage desc
 202:         ) as margin_rank_within_company,
 203:         
 204:         -- relative to average
 205:         pa.department_revenue / avg(pa.department_revenue) over (
 206:             partition by pa.subsidiary_id, pa.performance_month
 207:         ) as revenue_vs_company_avg,
 208:         
 209:         pa.net_margin_percentage - avg(pa.net_margin_percentage) over (
 210:             partition by pa.subsidiary_id, pa.performance_month
 211:         ) as margin_vs_company_avg,
 212:         
 213:         -- Market share (internal)
 214:         pa.department_revenue / sum(pa.department_revenue) over (
 215:             partition by pa.subsidiary_id, pa.performance_month
 216:         ) as internal_market_share
 217:         
 218:     from performance_analysis pa
 219: ),
 220: 
 221: operational_alerts as (
 222:     select 
 223:         db.*,
 224:         
 225:         -- Warning signs
 226:         case 
 227:             when db.year_over_year_growth < -20 then 'Revenue Decline Alert'
 228:             when db.net_margin_percentage < 0 and db.month_over_month_growth < -10 then 'Loss Alert'
 229:             when db.revenue_to_expense_ratio < 1.0 then 'Efficiency Alert'
 230:             when db.gross_margin_percentage < 0.1 then 'Margin Alert'
 231:             else 'Normal'
 232:         end as alert_status,
 233:         
 234:         -- Improvement suggestions
 235:         case 
 236:             when db.performance_grade = 'Loss Making' then 'Urgent restructuring required'
 237:             when db.performance_grade = 'Poor' and db.revenue_trend = 'Declining' then 'Review operations and cost structure'
 238:             when db.margin_trend = 'Declining' and db.revenue_trend = 'Stable' then 'Focus on cost optimization'
 239:             when db.revenue_trend = 'Declining' and db.margin_trend = 'Stable' then 'Increase sales and marketing efforts'
 240:             when db.performance_grade in ('Good', 'Excellent') then 'Scale successful practices'
 241:             else 'Monitor performance closely'
 242:         end as improvement_recommendation,
 243:         
 244:         -- investment advice
 245:         case 
 246:             when db.performance_grade = 'Excellent' and db.revenue_trend = 'Accelerating' then 'Increase Investment'
 247:             when db.performance_grade in ('Good', 'Excellent') and db.internal_market_share < 0.3 then 'Growth Investment'
 248:             when db.performance_grade = 'Fair' and db.margin_trend = 'Improving' then 'Selective Investment'
 249:             when db.performance_grade in ('Poor', 'Loss Making') then 'Review Investment'
 250:             else 'Maintain Current Investment'
 251:         end as investment_recommendation
 252:         
 253:     from department_benchmarking db
 254: )
 255: 
 256: select 
 257:     subsidiary_id,
 258:     department_id,
 259:     department_name,
 260:     location_id,
 261:     location_name,
 262:     performance_month,
 263:     
 264:     -- core financial indicators
 265:     department_revenue,
 266:     gross_profit,
 267:     net_profit,
 268:     gross_margin_percentage,
 269:     net_margin_percentage,
 270:     revenue_to_expense_ratio,
 271:     
 272:     -- growth indicators
 273:     month_over_month_growth,
 274:     year_over_year_growth,
 275:     three_month_avg_revenue,
 276:     
 277:     -- Trends and Ratings
 278:     revenue_trend,
 279:     margin_trend,
 280:     performance_grade,
 281:     
 282:     -- Benchmark comparison
 283:     revenue_rank_within_company,
 284:     margin_rank_within_company,
 285:     revenue_vs_company_avg,
 286:     margin_vs_company_avg,
 287:     internal_market_share,
 288:     
 289:     -- Warnings and recommendations
 290:     alert_status,
 291:     improvement_recommendation,
 292:     investment_recommendation,
 293:     
 294:     analysis_date,
 295:     
 296:     md5(cast(subsidiary_id as varchar) || '_' || cast(department_id as varchar) || '_' || cast(performance_month as varchar)) as operational_metrics_id
 297:     
 298: from operational_alerts
 299: where performance_month >= current_date - interval '12 months'  -- Keep the last 12 months
 300:     and department_revenue is not null
 301: order by subsidiary_id, performance_month desc, department_revenue desc
```

## 3. agent看到的材料与不确定性

已检视该题全部67个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 53 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/53.json`。
- event 54 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/54.json`。

四档：**看到了但没提**。

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

## 4. 核实查询与诊断

核实查询共**2条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__locations' source_table,count(*) rows FROM intermediate.int_netsuite2__locations UNION ALL SELECT 'intermediate.int_netsuite2__transaction_details' source_table,count(*) rows FROM intermediate.int_netsuite2__transaction_details UNION ALL SELECT 'staging.stg_netsuite2__departments' source_table,count(*) rows FROM staging.stg_netsuite2__departments UNION ALL SELECT 'staging.stg_netsuite2__transaction_lines' source_table,count(*) rows FROM staging.stg_netsuite2__transaction_lines
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ... 'intermediate.int_netsuite2__locations' source_table,count(*) rows FROM intermediate.int_netsuite2__locations UNION ALL...\n                                                                          ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__locations' source_table,count(*) source_rows FROM intermediate.int_netsuite2__locations UNION ALL SELECT 'intermediate.int_netsuite2__transaction_details' source_table,count(*) source_rows FROM intermediate.int_netsuite2__transaction_details UNION ALL SELECT 'staging.stg_netsuite2__departments' source_table,count(*) source_rows FROM staging.stg_netsuite2__departments UNION ALL SELECT 'staging.stg_netsuite2__transaction_lines' source_table,count(*) source_rows FROM staging.stg_netsuite2__transaction_lines
```

```json
{"columns": ["source_table", "source_rows"], "result": [["intermediate.int_netsuite2__locations", 100], ["intermediate.int_netsuite2__transaction_details", 700], ["staging.stg_netsuite2__departments", 100], ["staging.stg_netsuite2__transaction_lines", 700]]}
```

### 诊断（允许gold，不计5条）

`records/022_diagnostics.json` 本表条目：

```json
{"index": 16, "kind": "诊断查询", "queries": [{"label": "评分日期和窗口边界", "sql": "SELECT min(analysis_date),max(analysis_date),min(performance_month),max(performance_month),count(*) FROM gold.mart.netsuite2_operational_metrics", "columns": ["min(analysis_date)", "max(analysis_date)", "min(performance_month)", "max(performance_month)", "count_star()"], "result": [["2025-10-14", "2025-10-14", "2025-10-01", "2025-10-01", 700]]}]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 3}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["subsidiary_id", "department_id", "location_id", "operational_metrics_id"]`；比较列：`["subsidiary_id", "department_id", "department_name", "location_id", "location_name", "performance_month", "department_revenue", "gross_profit", "net_profit", "gross_margin_percentage", "net_margin_percentage", "revenue_to_expense_ratio", "month_over_month_growth", "year_over_year_growth", "three_month_avg_revenue", "revenue_trend", "margin_trend", "performance_grade", "revenue_rank_within_company", "margin_rank_within_company", "revenue_vs_company_avg", "margin_vs_company_avg", "internal_market_share", "alert_status", "improvement_recommendation", "investment_recommendation", "operational_metrics_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L1 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L2 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L3 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| subsidiary_id | 0 | 0 | 0 | 0 |
| department_id | 0 | 0 | 0 | 0 |
| location_id | 0 | 0 | 0 | 0 |
| operational_metrics_id | 0 | 0 | 0 | 0 |
| department_name | 0 | 0 | 0 | 0 |
| location_name | 0 | 0 | 0 | 0 |
| performance_month | 0 | 0 | 0 | 0 |
| department_revenue | 0 | 0 | 0 | 0 |
| gross_profit | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| gross_margin_percentage | 0 | 0 | 0 | 0 |
| net_margin_percentage | 0 | 0 | 0 | 0 |
| revenue_to_expense_ratio | 0 | 0 | 0 | 0 |
| month_over_month_growth | 0 | 0 | 0 | 0 |
| year_over_year_growth | 0 | 0 | 0 | 0 |
| three_month_avg_revenue | 0 | 0 | 0 | 0 |
| revenue_trend | 0 | 0 | 0 | 0 |
| margin_trend | 0 | 0 | 0 | 0 |
| performance_grade | 0 | 0 | 0 | 0 |
| revenue_rank_within_company | 0 | 0 | 0 | 0 |
| margin_rank_within_company | 0 | 0 | 0 | 0 |
| revenue_vs_company_avg | 78 | 78 | 78 | 78 |
| margin_vs_company_avg | 78 | 78 | 78 | 78 |
| internal_market_share | 0 | 0 | 0 | 0 |
| alert_status | 0 | 0 | 0 | 0 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| investment_recommendation | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_netsuite2_operational_metrics/baseline.sql`；SHA-256：`8893ceb3cf9103ae5724ec60425019cc213496e2fa7c2d895b75da6e57d5e604`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L1 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L2 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L3 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| subsidiary_id | 0 | 0 | 0 | 0 |
| department_id | 0 | 0 | 0 | 0 |
| location_id | 0 | 0 | 0 | 0 |
| operational_metrics_id | 0 | 0 | 0 | 0 |
| department_name | 0 | 0 | 0 | 0 |
| location_name | 0 | 0 | 0 | 0 |
| performance_month | 0 | 0 | 0 | 0 |
| department_revenue | 0 | 0 | 0 | 0 |
| gross_profit | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| gross_margin_percentage | 0 | 0 | 0 | 0 |
| net_margin_percentage | 0 | 0 | 0 | 0 |
| revenue_to_expense_ratio | 0 | 0 | 0 | 0 |
| month_over_month_growth | 0 | 0 | 0 | 0 |
| year_over_year_growth | 0 | 0 | 0 | 0 |
| three_month_avg_revenue | 0 | 0 | 0 | 0 |
| revenue_trend | 0 | 0 | 0 | 0 |
| margin_trend | 0 | 0 | 0 | 0 |
| performance_grade | 0 | 0 | 0 | 0 |
| revenue_rank_within_company | 0 | 0 | 0 | 0 |
| margin_rank_within_company | 0 | 0 | 0 | 0 |
| revenue_vs_company_avg | 78 | 78 | 78 | 78 |
| margin_vs_company_avg | 78 | 78 | 78 | 78 |
| internal_market_share | 0 | 0 | 0 | 0 |
| alert_status | 0 | 0 | 0 | 0 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| investment_recommendation | 0 | 0 | 0 | 0 |

### zero_department_revenue

SQL：`data/022_work/impl-013_netsuite2_operational_metrics/zero_department_revenue.sql`；SHA-256：`e400821ad8816546970773729d4e7f01edaed57afb890696ce0560eb4bcd38ee`。

替换offset=198，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(t.converted_amount) FILTER(WHERE t.account_type_name='Income') department_revenue
-- 新
coalesce(sum(t.converted_amount) FILTER(WHERE t.account_type_name='Income'),0) department_revenue
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 700/700 | 0/0 | 0/0 | 663 | 663 | 3290 | False |
| L1 | 700/700 | 0/0 | 0/0 | 663 | 663 | 3290 | False |
| L2 | 700/700 | 0/0 | 0/0 | 663 | 663 | 3290 | False |
| L3 | 700/700 | 0/0 | 0/0 | 663 | 663 | 3290 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| subsidiary_id | 0 | 0 | 0 | 0 |
| department_id | 0 | 0 | 0 | 0 |
| location_id | 0 | 0 | 0 | 0 |
| operational_metrics_id | 0 | 0 | 0 | 0 |
| department_name | 0 | 0 | 0 | 0 |
| location_name | 0 | 0 | 0 | 0 |
| performance_month | 0 | 0 | 0 | 0 |
| department_revenue | 0 | 0 | 0 | 0 |
| gross_profit | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| gross_margin_percentage | 585 | 585 | 585 | 585 |
| net_margin_percentage | 585 | 585 | 585 | 585 |
| revenue_to_expense_ratio | 0 | 0 | 0 | 0 |
| month_over_month_growth | 0 | 0 | 0 | 0 |
| year_over_year_growth | 0 | 0 | 0 | 0 |
| three_month_avg_revenue | 0 | 0 | 0 | 0 |
| revenue_trend | 0 | 0 | 0 | 0 |
| margin_trend | 0 | 0 | 0 | 0 |
| performance_grade | 0 | 0 | 0 | 0 |
| revenue_rank_within_company | 0 | 0 | 0 | 0 |
| margin_rank_within_company | 0 | 0 | 0 | 0 |
| revenue_vs_company_avg | 488 | 488 | 488 | 488 |
| margin_vs_company_avg | 663 | 663 | 663 | 663 |
| internal_market_share | 488 | 488 | 488 | 488 |
| alert_status | 481 | 481 | 481 | 481 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| investment_recommendation | 0 | 0 | 0 | 0 |

### zero_department_cogs

SQL：`data/022_work/impl-013_netsuite2_operational_metrics/zero_department_cogs.sql`；SHA-256：`28fccf5caec8267d2e9b32f7f993bc9af547b3c4044c02d7baa11b129b68e7e2`。

替换offset=285，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='COGS') department_cogs
-- 新
coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='COGS'),0) department_cogs
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L1 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L2 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L3 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| subsidiary_id | 0 | 0 | 0 | 0 |
| department_id | 0 | 0 | 0 | 0 |
| location_id | 0 | 0 | 0 | 0 |
| operational_metrics_id | 0 | 0 | 0 | 0 |
| department_name | 0 | 0 | 0 | 0 |
| location_name | 0 | 0 | 0 | 0 |
| performance_month | 0 | 0 | 0 | 0 |
| department_revenue | 0 | 0 | 0 | 0 |
| gross_profit | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| gross_margin_percentage | 0 | 0 | 0 | 0 |
| net_margin_percentage | 0 | 0 | 0 | 0 |
| revenue_to_expense_ratio | 0 | 0 | 0 | 0 |
| month_over_month_growth | 0 | 0 | 0 | 0 |
| year_over_year_growth | 0 | 0 | 0 | 0 |
| three_month_avg_revenue | 0 | 0 | 0 | 0 |
| revenue_trend | 0 | 0 | 0 | 0 |
| margin_trend | 0 | 0 | 0 | 0 |
| performance_grade | 0 | 0 | 0 | 0 |
| revenue_rank_within_company | 0 | 0 | 0 | 0 |
| margin_rank_within_company | 0 | 0 | 0 | 0 |
| revenue_vs_company_avg | 78 | 78 | 78 | 78 |
| margin_vs_company_avg | 78 | 78 | 78 | 78 |
| internal_market_share | 0 | 0 | 0 | 0 |
| alert_status | 0 | 0 | 0 | 0 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| investment_recommendation | 0 | 0 | 0 | 0 |

### zero_department_expenses

SQL：`data/022_work/impl-013_netsuite2_operational_metrics/zero_department_expenses.sql`；SHA-256：`c4672450abd8edc9ce743e8ed791ebefd181a0d74f3193d790446d8d23ad5b8d`。

替换offset=371，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Expense') department_expenses
-- 新
coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Expense'),0) department_expenses
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L1 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L2 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L3 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| subsidiary_id | 0 | 0 | 0 | 0 |
| department_id | 0 | 0 | 0 | 0 |
| location_id | 0 | 0 | 0 | 0 |
| operational_metrics_id | 0 | 0 | 0 | 0 |
| department_name | 0 | 0 | 0 | 0 |
| location_name | 0 | 0 | 0 | 0 |
| performance_month | 0 | 0 | 0 | 0 |
| department_revenue | 0 | 0 | 0 | 0 |
| gross_profit | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| gross_margin_percentage | 0 | 0 | 0 | 0 |
| net_margin_percentage | 0 | 0 | 0 | 0 |
| revenue_to_expense_ratio | 0 | 0 | 0 | 0 |
| month_over_month_growth | 0 | 0 | 0 | 0 |
| year_over_year_growth | 0 | 0 | 0 | 0 |
| three_month_avg_revenue | 0 | 0 | 0 | 0 |
| revenue_trend | 0 | 0 | 0 | 0 |
| margin_trend | 0 | 0 | 0 | 0 |
| performance_grade | 0 | 0 | 0 | 0 |
| revenue_rank_within_company | 0 | 0 | 0 | 0 |
| margin_rank_within_company | 0 | 0 | 0 | 0 |
| revenue_vs_company_avg | 78 | 78 | 78 | 78 |
| margin_vs_company_avg | 78 | 78 | 78 | 78 |
| internal_market_share | 0 | 0 | 0 | 0 |
| alert_status | 0 | 0 | 0 | 0 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| investment_recommendation | 0 | 0 | 0 | 0 |

### class_group

SQL：`data/022_work/impl-013_netsuite2_operational_metrics/class_group.sql`；SHA-256：`a8af33d390780e30f96acf8a4ca66e5b7d44aa17804240bc855f87599ad9ea3b`。

替换offset=127，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
date_trunc('month',t.accounting_period_ending)::DATE performance_month
-- 新
l.class_id,date_trunc('month',t.accounting_period_ending)::DATE performance_month
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L1 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L2 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L3 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| subsidiary_id | 0 | 0 | 0 | 0 |
| department_id | 0 | 0 | 0 | 0 |
| location_id | 0 | 0 | 0 | 0 |
| operational_metrics_id | 0 | 0 | 0 | 0 |
| department_name | 0 | 0 | 0 | 0 |
| location_name | 0 | 0 | 0 | 0 |
| performance_month | 0 | 0 | 0 | 0 |
| department_revenue | 0 | 0 | 0 | 0 |
| gross_profit | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| gross_margin_percentage | 0 | 0 | 0 | 0 |
| net_margin_percentage | 0 | 0 | 0 | 0 |
| revenue_to_expense_ratio | 0 | 0 | 0 | 0 |
| month_over_month_growth | 0 | 0 | 0 | 0 |
| year_over_year_growth | 0 | 0 | 0 | 0 |
| three_month_avg_revenue | 0 | 0 | 0 | 0 |
| revenue_trend | 0 | 0 | 0 | 0 |
| margin_trend | 0 | 0 | 0 | 0 |
| performance_grade | 0 | 0 | 0 | 0 |
| revenue_rank_within_company | 0 | 0 | 0 | 0 |
| margin_rank_within_company | 0 | 0 | 0 | 0 |
| revenue_vs_company_avg | 78 | 78 | 78 | 78 |
| margin_vs_company_avg | 78 | 78 | 78 | 78 |
| internal_market_share | 0 | 0 | 0 | 0 |
| alert_status | 0 | 0 | 0 | 0 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| investment_recommendation | 0 | 0 | 0 | 0 |

### zero_gross_margin_percentage

SQL：`data/022_work/impl-013_netsuite2_operational_metrics/zero_gross_margin_percentage.sql`；SHA-256：`4e8bc0e332384c516755174dbe5989800b7311519265d412145484f216a05c56`。

替换offset=1352，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
(coalesce(department_revenue,0)-coalesce(department_cogs,0))/nullif(department_revenue,0) gross_margin_percentage
-- 新
coalesce((coalesce(department_revenue,0)-coalesce(department_cogs,0))/nullif(department_revenue,0),0) gross_margin_percentage
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L1 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L2 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |
| L3 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15951 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| subsidiary_id | 0 | 0 | 0 | 0 |
| department_id | 0 | 0 | 0 | 0 |
| location_id | 0 | 0 | 0 | 0 |
| operational_metrics_id | 0 | 0 | 0 | 0 |
| department_name | 0 | 0 | 0 | 0 |
| location_name | 0 | 0 | 0 | 0 |
| performance_month | 0 | 0 | 0 | 0 |
| department_revenue | 0 | 0 | 0 | 0 |
| gross_profit | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| gross_margin_percentage | 0 | 0 | 0 | 0 |
| net_margin_percentage | 0 | 0 | 0 | 0 |
| revenue_to_expense_ratio | 0 | 0 | 0 | 0 |
| month_over_month_growth | 0 | 0 | 0 | 0 |
| year_over_year_growth | 0 | 0 | 0 | 0 |
| three_month_avg_revenue | 0 | 0 | 0 | 0 |
| revenue_trend | 0 | 0 | 0 | 0 |
| margin_trend | 0 | 0 | 0 | 0 |
| performance_grade | 0 | 0 | 0 | 0 |
| revenue_rank_within_company | 0 | 0 | 0 | 0 |
| margin_rank_within_company | 0 | 0 | 0 | 0 |
| revenue_vs_company_avg | 78 | 78 | 78 | 78 |
| margin_vs_company_avg | 78 | 78 | 78 | 78 |
| internal_market_share | 0 | 0 | 0 | 0 |
| alert_status | 0 | 0 | 0 | 0 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| investment_recommendation | 0 | 0 | 0 | 0 |

### zero_net_margin_percentage

SQL：`data/022_work/impl-013_netsuite2_operational_metrics/zero_net_margin_percentage.sql`；SHA-256：`9aa4c81d8156595e2a4a8a19f2d5b382db4724f676ef9ad1d5c9cf36bc01bfe1`。

替换offset=1466，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
(coalesce(department_revenue,0)-coalesce(department_cogs,0)-coalesce(department_expenses,0))/nullif(department_revenue,0) net_margin_percentage
-- 新
coalesce((coalesce(department_revenue,0)-coalesce(department_cogs,0)-coalesce(department_expenses,0))/nullif(department_revenue,0),0) net_margin_percentage
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15873 | False |
| L1 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15873 | False |
| L2 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15873 | False |
| L3 | 115/700 | 0/585 | 0/0 | 78 | 663 | 15873 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| subsidiary_id | 0 | 0 | 0 | 0 |
| department_id | 0 | 0 | 0 | 0 |
| location_id | 0 | 0 | 0 | 0 |
| operational_metrics_id | 0 | 0 | 0 | 0 |
| department_name | 0 | 0 | 0 | 0 |
| location_name | 0 | 0 | 0 | 0 |
| performance_month | 0 | 0 | 0 | 0 |
| department_revenue | 0 | 0 | 0 | 0 |
| gross_profit | 0 | 0 | 0 | 0 |
| net_profit | 0 | 0 | 0 | 0 |
| gross_margin_percentage | 0 | 0 | 0 | 0 |
| net_margin_percentage | 0 | 0 | 0 | 0 |
| revenue_to_expense_ratio | 0 | 0 | 0 | 0 |
| month_over_month_growth | 0 | 0 | 0 | 0 |
| year_over_year_growth | 0 | 0 | 0 | 0 |
| three_month_avg_revenue | 0 | 0 | 0 | 0 |
| revenue_trend | 0 | 0 | 0 | 0 |
| margin_trend | 0 | 0 | 0 | 0 |
| performance_grade | 0 | 0 | 0 | 0 |
| revenue_rank_within_company | 0 | 0 | 0 | 0 |
| margin_rank_within_company | 0 | 0 | 0 | 0 |
| revenue_vs_company_avg | 78 | 78 | 78 | 78 |
| margin_vs_company_avg | 0 | 0 | 0 | 0 |
| internal_market_share | 0 | 0 | 0 | 0 |
| alert_status | 0 | 0 | 0 | 0 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| investment_recommendation | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：zero_department_revenue；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- zero_department_revenue：C；主项。类别无匹配时SUM FILTER产生NULL；契约聚合为0。（行减少0，格减少12661）
- zero_department_cogs：C；单修未满足本表所选尺度的参与门槛。类别无匹配时SUM FILTER产生NULL；契约聚合为0。（行减少0，格减少0）
- zero_department_expenses：C；单修未满足本表所选尺度的参与门槛。类别无匹配时SUM FILTER产生NULL；契约聚合为0。（行减少0，格减少0）
- class_group：C；单修未满足本表所选尺度的参与门槛。契约内部按class_id分组，agent遗漏。（行减少0，格减少0）
- zero_gross_margin_percentage：C；单修未满足本表所选尺度的参与门槛。契约revenue非正时margin为0，agent NULL。（行减少0，格减少0）
- zero_net_margin_percentage：C；参与因素。契约revenue非正时margin为0，agent NULL。（行减少0，格减少78）

## 规则问题

无。按v2冻结定义执行。
