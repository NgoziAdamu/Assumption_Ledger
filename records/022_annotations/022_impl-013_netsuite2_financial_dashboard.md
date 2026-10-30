# impl-013 / netsuite2_financial_dashboard（全量；v2）

## 1. 差异与结论

波动率用score*0占位，契约要求standard deviation；13个单观测分组gold为NULL，恢复stddev_samp后L0一致。未找到agent对单观测stddev作数据判断的文字，依D。

主要原因：**D**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| volatility | D | 13 | 13 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_netsuite2_financial_dashboard.md](../../records/022_packages/022_impl-013_netsuite2_financial_dashboard.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_netsuite2_financial_dashboard/022_impl-013_netsuite2_financial_dashboard.json`。
- 比较结果：[022_reruns_impl-013_netsuite2_financial_dashboard.json](../022_reruns_impl-013_netsuite2_financial_dashboard.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第2870–3006行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_financial_dashboard.sql`；原件第1–1行。

```sql
   1: WITH cf AS (SELECT * FROM intermediate.int_netsuite2__cash_flow_analysis WHERE analysis_month=date_trunc('month',current_date-interval '1 month')), ar AS (SELECT subsidiary_id,sum(total_ar_amount) total_ar_amount,sum(overdue_amount) overdue_amount,sum(overdue_amount)/nullif(sum(total_ar_amount),0) overdue_percentage,avg(weighted_average_days_outstanding) weighted_average_days_outstanding FROM intermediate.int_netsuite2__ar_aging_analysis GROUP BY subsidiary_id), cp AS (SELECT subsidiary_id,count(*) total_customers,count(*) FILTER(WHERE customer_segment IN ('Champion','Loyal')) high_value_customers,count(*) FILTER(WHERE customer_segment='At Risk' OR activity_status='At Risk') at_risk_customers,sum(total_revenue) total_customer_revenue,avg(total_revenue) average_customer_value FROM intermediate.int_netsuite2__customer_profitability GROUP BY subsidiary_id), base AS (SELECT fr.*,current_date dashboard_date,cf.net_cash_flow,cf.operating_cash_flow,cf.cash_flow_health,cf.predicted_next_month_cash_flow,cf.cash_flow_risk_level,ar.total_ar_amount,ar.overdue_amount,ar.overdue_percentage,ar.weighted_average_days_outstanding,cp.total_customers,cp.high_value_customers,cp.at_risk_customers,cp.total_customer_revenue,cp.average_customer_value FROM intermediate.int_netsuite2__financial_ratios fr LEFT JOIN cf USING(subsidiary_id) LEFT JOIN ar USING(subsidiary_id) LEFT JOIN cp USING(subsidiary_id)), trends AS (SELECT *,overall_financial_health_score avg_financial_health,overall_financial_health_score*0 financial_health_volatility,net_profit_margin avg_net_margin,current_ratio avg_current_ratio,CASE WHEN cash_flow_health IN ('Excellent','Good') THEN 100.0 ELSE 0 END cash_flow_consistency_percentage FROM base), risk AS (SELECT *,CASE WHEN overall_financial_health_score<40 THEN 30 WHEN overall_financial_health_score<60 THEN 20 WHEN overall_financial_health_score<80 THEN 10 ELSE 5 END + CASE WHEN cash_flow_risk_level='High Risk - Negative Trend' THEN 25 WHEN cash_flow_risk_level LIKE '%High Risk%' THEN 20 WHEN cash_flow_risk_level LIKE '%Medium Risk%' THEN 10 ELSE 5 END + CASE WHEN overdue_percentage>.30 THEN 20 WHEN overdue_percentage>.20 THEN 15 WHEN overdue_percentage>.10 THEN 10 ELSE 5 END + CASE WHEN current_ratio<1 THEN 25 WHEN current_ratio<1.5 THEN 15 WHEN current_ratio<2 THEN 10 ELSE 5 END total_risk_score FROM trends) SELECT subsidiary_id,accounting_period_id,dashboard_date,current_ratio,quick_ratio,return_on_equity,gross_margin_ratio,net_profit_margin,overall_financial_health_score,financial_health_grade,net_cash_flow,operating_cash_flow,cash_flow_health,predicted_next_month_cash_flow,cash_flow_risk_level,total_ar_amount,overdue_amount,overdue_percentage,weighted_average_days_outstanding,total_customers,high_value_customers,at_risk_customers,total_customer_revenue,average_customer_value,avg_financial_health,financial_health_volatility,avg_net_margin,avg_current_ratio,cash_flow_consistency_percentage::FLOAT, total_risk_score::INTEGER,CASE WHEN total_risk_score>=70 THEN 'Critical Risk' WHEN total_risk_score>=50 THEN 'High Risk' WHEN total_risk_score>=30 THEN 'Medium Risk' ELSE 'Low Risk' END risk_level,CASE WHEN overall_financial_health_score<40 THEN 'Poor Financial Health' WHEN cash_flow_risk_level LIKE '%High Risk%' THEN 'Cash Flow Issues' WHEN overdue_percentage>.3 THEN 'High Receivables Risk' WHEN current_ratio<1 THEN 'Liquidity Concerns' ELSE 'No Major Risk Factors' END primary_risk_factor,CASE WHEN current_ratio>=2 THEN 'Above Target' WHEN current_ratio>=1.5 THEN 'At Target' ELSE 'Below Target' END liquidity_performance,CASE WHEN net_profit_margin>=.15 THEN 'Above Target' WHEN net_profit_margin>=.05 THEN 'At Target' ELSE 'Below Target' END profitability_performance,CASE WHEN return_on_equity>=.15 THEN 'Above Target' WHEN return_on_equity>=.1 THEN 'At Target' ELSE 'Below Target' END roe_performance,CASE WHEN overdue_percentage<=.05 THEN 'Above Target' WHEN overdue_percentage<=.15 THEN 'At Target' ELSE 'Below Target' END collection_performance,'Maintain Current Performance' improvement_recommendation,CASE WHEN overall_financial_health_score>=80 AND total_risk_score<30 THEN 'A+ Excellent' WHEN overall_financial_health_score>=70 AND total_risk_score<50 THEN 'A Good' WHEN overall_financial_health_score>=60 AND total_risk_score<70 THEN 'B Fair' WHEN overall_financial_health_score>=40 THEN 'C Poor' ELSE 'D Critical' END overall_rating,CASE WHEN total_risk_score>=70 THEN 'URGENT: Multiple Critical Risk Factors' WHEN cash_flow_risk_level LIKE '%High Risk%' THEN 'WARNING: Cash Flow Issues' WHEN current_ratio<1 THEN 'ALERT: Liquidity Below Safe Levels' WHEN overdue_percentage>.3 THEN 'CAUTION: High Receivables Risk' ELSE 'Normal Operations' END key_alert,md5(subsidiary_id||'_'||cast(dashboard_date AS VARCHAR)) dashboard_id FROM risk WHERE subsidiary_id IS NOT NULL
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/marts/netsuite2_financial_dashboard.sql`；原件第1–357行。

```sql
   1: -- Financial Dashboard KPIs
   2: -- Financial dashboard core metrics that provide high-level financial overview and trend analysis
   3: with financial_ratios as (
   4:     select * from intermediate.int_netsuite2__financial_ratios
   5: ),
   6: 
   7: customer_profitability as (
   8:     select * from intermediate.int_netsuite2__customer_profitability
   9: ),
  10: 
  11: cash_flow_analysis as (
  12:     select * from intermediate.int_netsuite2__cash_flow_analysis
  13: ),
  14: 
  15: ar_aging as (
  16:     select * from intermediate.int_netsuite2__ar_aging_analysis
  17: ),
  18: 
  19: -- Summary of core financial indicators
  20: financial_kpis as (
  21:     select 
  22:         fr.subsidiary_id,
  23:         fr.accounting_period_id,
  24:         current_date as dashboard_date,
  25:         
  26:         -- financial ratio indicator
  27:         fr.current_ratio,
  28:         fr.quick_ratio,
  29:         fr.return_on_equity,
  30:         fr.gross_margin_ratio,
  31:         fr.net_profit_margin,
  32:         fr.overall_financial_health_score,
  33:         fr.financial_health_grade,
  34:         
  35:         -- cash flow indicator
  36:         cf.net_cash_flow,
  37:         cf.operating_cash_flow,
  38:         cf.cash_flow_health,
  39:         cf.predicted_next_month_cash_flow,
  40:         cf.cash_flow_risk_level,
  41:         
  42:         -- Accounts Receivable Metrics
  43:         ar.total_ar_amount,
  44:         ar.overdue_amount,
  45:         ar.overdue_percentage,
  46:         ar.weighted_average_days_outstanding,
  47:         
  48:         -- Customer Metrics
  49:         cp_summary.total_customers,
  50:         cp_summary.high_value_customers,
  51:         cp_summary.at_risk_customers,
  52:         cp_summary.total_customer_revenue,
  53:         cp_summary.average_customer_value
  54:         
  55:     from financial_ratios fr
  56:     left join (
  57:         select 
  58:             subsidiary_id,
  59:             analysis_month,
  60:             net_cash_flow,
  61:             operating_cash_flow,
  62:             cash_flow_health,
  63:             predicted_next_month_cash_flow,
  64:             cash_flow_risk_level
  65:         from cash_flow_analysis
  66:         where analysis_month = date_trunc('month', current_date - interval '1 month')
  67:     ) cf on fr.subsidiary_id = cf.subsidiary_id
  68:     left join (
  69:         select 
  70:             subsidiary_id,
  71:             sum(total_ar_amount) as total_ar_amount,
  72:             sum(overdue_amount) as overdue_amount,
  73:             case 
  74:                 when sum(total_ar_amount) > 0 
  75:                 then sum(overdue_amount) / sum(total_ar_amount)
  76:                 else 0 
  77:             end as overdue_percentage,
  78:             avg(weighted_average_days_outstanding) as weighted_average_days_outstanding
  79:         from ar_aging
  80:         group by subsidiary_id
  81:     ) ar on fr.subsidiary_id = ar.subsidiary_id
  82:     left join (
  83:         select 
  84:             subsidiary_id,
  85:             count(*) as total_customers,
  86:             count(case when customer_segment in ('Champion', 'Loyal') then 1 end) as high_value_customers,
  87:             count(case when customer_segment = 'At Risk' or activity_status = 'At Risk' then 1 end) as at_risk_customers,
  88:             sum(total_revenue) as total_customer_revenue,
  89:             avg(total_revenue) as average_customer_value
  90:         from customer_profitability
  91:         group by subsidiary_id
  92:     ) cp_summary on fr.subsidiary_id = cp_summary.subsidiary_id
  93: ),
  94: 
  95: -- trend analysis
  96: financial_trends as (
  97:     select 
  98:         subsidiary_id,
  99:         
 100:         -- Financial Wellness Trends
 101:         avg(overall_financial_health_score) as avg_financial_health,
 102:         stddev(overall_financial_health_score) as financial_health_volatility,
 103:         
 104:         -- Profitability Trends
 105:         avg(net_profit_margin) as avg_net_margin,
 106:         max(net_profit_margin) - min(net_profit_margin) as margin_range,
 107:         
 108:         -- liquidity trends
 109:         avg(current_ratio) as avg_current_ratio,
 110:         min(current_ratio) as min_current_ratio,
 111:         
 112:         -- cash flow trends
 113:         sum(case when cash_flow_health in ('Excellent', 'Good') then 1 else 0 end) as positive_cash_flow_periods,
 114:         count(*) as total_periods,
 115:         
 116:         current_date as trend_analysis_date
 117:         
 118:     from financial_kpis
 119:     group by subsidiary_id
 120: ),
 121: 
 122: -- risk assessment
 123: risk_assessment as (
 124:     select 
 125:         fk.subsidiary_id,
 126:         
 127:         -- Comprehensive risk score (0-100, higher is more dangerous)
 128:         case 
 129:             when fk.overall_financial_health_score < 40 then 30
 130:             when fk.overall_financial_health_score < 60 then 20
 131:             when fk.overall_financial_health_score < 80 then 10
 132:             else 5
 133:         end +
 134:         case 
 135:             when fk.cash_flow_risk_level = 'High Risk - Negative Trend' then 25
 136:             when fk.cash_flow_risk_level like '%High Risk%' then 20
 137:             when fk.cash_flow_risk_level like '%Medium Risk%' then 10
 138:             else 5
 139:         end +
 140:         case 
 141:             when fk.overdue_percentage > 0.3 then 20
 142:             when fk.overdue_percentage > 0.2 then 15
 143:             when fk.overdue_percentage > 0.1 then 10
 144:             else 5
 145:         end +
 146:         case 
 147:             when fk.current_ratio < 1.0 then 25
 148:             when fk.current_ratio < 1.5 then 15
 149:             when fk.current_ratio < 2.0 then 10
 150:             else 5
 151:         end as total_risk_score,
 152:         
 153:         -- risk level
 154:         case 
 155:             when (
 156:                 case 
 157:                     when fk.overall_financial_health_score < 40 then 30
 158:                     when fk.overall_financial_health_score < 60 then 20
 159:                     when fk.overall_financial_health_score < 80 then 10
 160:                     else 5
 161:                 end +
 162:                 case 
 163:                     when fk.cash_flow_risk_level = 'High Risk - Negative Trend' then 25
 164:                     when fk.cash_flow_risk_level like '%High Risk%' then 20
 165:                     when fk.cash_flow_risk_level like '%Medium Risk%' then 10
 166:                     else 5
 167:                 end +
 168:                 case 
 169:                     when fk.overdue_percentage > 0.3 then 20
 170:                     when fk.overdue_percentage > 0.2 then 15
 171:                     when fk.overdue_percentage > 0.1 then 10
 172:                     else 5
 173:                 end +
 174:                 case 
 175:                     when fk.current_ratio < 1.0 then 25
 176:                     when fk.current_ratio < 1.5 then 15
 177:                     when fk.current_ratio < 2.0 then 10
 178:                     else 5
 179:                 end
 180:             ) >= 70 then 'Critical Risk'
 181:             when (
 182:                 case 
 183:                     when fk.overall_financial_health_score < 40 then 30
 184:                     when fk.overall_financial_health_score < 60 then 20
 185:                     when fk.overall_financial_health_score < 80 then 10
 186:                     else 5
 187:                 end +
 188:                 case 
 189:                     when fk.cash_flow_risk_level = 'High Risk - Negative Trend' then 25
 190:                     when fk.cash_flow_risk_level like '%High Risk%' then 20
 191:                     when fk.cash_flow_risk_level like '%Medium Risk%' then 10
 192:                     else 5
 193:                 end +
 194:                 case 
 195:                     when fk.overdue_percentage > 0.3 then 20
 196:                     when fk.overdue_percentage > 0.2 then 15
 197:                     when fk.overdue_percentage > 0.1 then 10
 198:                     else 5
 199:                 end +
 200:                 case 
 201:                     when fk.current_ratio < 1.0 then 25
 202:                     when fk.current_ratio < 1.5 then 15
 203:                     when fk.current_ratio < 2.0 then 10
 204:                     else 5
 205:                 end
 206:             ) >= 50 then 'High Risk'
 207:             when (
 208:                 case 
 209:                     when fk.overall_financial_health_score < 40 then 30
 210:                     when fk.overall_financial_health_score < 60 then 20
 211:                     when fk.overall_financial_health_score < 80 then 10
 212:                     else 5
 213:                 end +
 214:                 case 
 215:                     when fk.cash_flow_risk_level = 'High Risk - Negative Trend' then 25
 216:                     when fk.cash_flow_risk_level like '%High Risk%' then 20
 217:                     when fk.cash_flow_risk_level like '%Medium Risk%' then 10
 218:                     else 5
 219:                 end +
 220:                 case 
 221:                     when fk.overdue_percentage > 0.3 then 20
 222:                     when fk.overdue_percentage > 0.2 then 15
 223:                     when fk.overdue_percentage > 0.1 then 10
 224:                     else 5
 225:                 end +
 226:                 case 
 227:                     when fk.current_ratio < 1.0 then 25
 228:                     when fk.current_ratio < 1.5 then 15
 229:                     when fk.current_ratio < 2.0 then 10
 230:                     else 5
 231:                 end
 232:             ) >= 30 then 'Medium Risk'
 233:             else 'Low Risk'
 234:         end as risk_level,
 235:         
 236:         -- Main risk factors
 237:         case 
 238:             when fk.overall_financial_health_score < 40 then 'Poor Financial Health'
 239:             when fk.cash_flow_risk_level like '%High Risk%' then 'Cash Flow Issues'
 240:             when fk.overdue_percentage > 0.3 then 'High Receivables Risk'
 241:             when fk.current_ratio < 1.0 then 'Liquidity Concerns'
 242:             else 'No Major Risk Factors'
 243:         end as primary_risk_factor,
 244:         
 245:         current_date as risk_assessment_date
 246:         
 247:     from financial_kpis fk
 248: ),
 249: 
 250: -- Performance goals and benchmarks
 251: performance_benchmarks as (
 252:     select 
 253:         fk.subsidiary_id,
 254:         
 255:         -- Set performance targets (industry benchmarks)
 256:         case when fk.current_ratio >= 2.0 then 'Above Target' when fk.current_ratio >= 1.5 then 'At Target' else 'Below Target' end as liquidity_performance,
 257:         case when fk.net_profit_margin >= 0.15 then 'Above Target' when fk.net_profit_margin >= 0.05 then 'At Target' else 'Below Target' end as profitability_performance,
 258:         case when fk.return_on_equity >= 0.15 then 'Above Target' when fk.return_on_equity >= 0.10 then 'At Target' else 'Below Target' end as roe_performance,
 259:         case when fk.overdue_percentage <= 0.05 then 'Above Target' when fk.overdue_percentage <= 0.15 then 'At Target' else 'Below Target' end as collection_performance,
 260:         
 261:         -- Improvement suggestions
 262:         case 
 263:             when fk.current_ratio < 1.5 and fk.net_profit_margin < 0.05 then 'Focus on Operations & Liquidity'
 264:             when fk.current_ratio < 1.5 then 'Improve Working Capital Management'
 265:             when fk.net_profit_margin < 0.05 then 'Review Cost Structure'
 266:             when fk.overdue_percentage > 0.15 then 'Strengthen Collections'
 267:             else 'Maintain Current Performance'
 268:         end as improvement_recommendation,
 269:         
 270:         current_date as benchmark_date
 271:         
 272:     from financial_kpis fk
 273: )
 274: 
 275: select 
 276:     fk.subsidiary_id,
 277:     fk.accounting_period_id,
 278:     fk.dashboard_date,
 279:     
 280:     -- core financial indicators
 281:     fk.current_ratio,
 282:     fk.quick_ratio,
 283:     fk.return_on_equity,
 284:     fk.gross_margin_ratio,
 285:     fk.net_profit_margin,
 286:     fk.overall_financial_health_score,
 287:     fk.financial_health_grade,
 288:     
 289:     -- cash flow indicator
 290:     fk.net_cash_flow,
 291:     fk.operating_cash_flow,
 292:     fk.cash_flow_health,
 293:     fk.predicted_next_month_cash_flow,
 294:     fk.cash_flow_risk_level,
 295:     
 296:     -- Accounts Receivable Metrics
 297:     fk.total_ar_amount,
 298:     fk.overdue_amount,
 299:     fk.overdue_percentage,
 300:     fk.weighted_average_days_outstanding,
 301:     
 302:     -- Customer Metrics
 303:     fk.total_customers,
 304:     fk.high_value_customers,
 305:     fk.at_risk_customers,
 306:     fk.total_customer_revenue,
 307:     fk.average_customer_value,
 308:     
 309:     -- trend analysis
 310:     ft.avg_financial_health,
 311:     ft.financial_health_volatility,
 312:     ft.avg_net_margin,
 313:     ft.avg_current_ratio,
 314:     case 
 315:         when ft.total_periods > 0 
 316:         then round((ft.positive_cash_flow_periods::float / ft.total_periods) * 100, 1)
 317:         else 0 
 318:     end as cash_flow_consistency_percentage,
 319:     
 320:     -- risk assessment
 321:     ra.total_risk_score,
 322:     ra.risk_level,
 323:     ra.primary_risk_factor,
 324:     
 325:     -- performance benchmark
 326:     pb.liquidity_performance,
 327:     pb.profitability_performance,
 328:     pb.roe_performance,
 329:     pb.collection_performance,
 330:     pb.improvement_recommendation,
 331:     
 332:     -- Overall rating
 333:     case 
 334:         when fk.overall_financial_health_score >= 80 and ra.risk_level = 'Low Risk' then 'A+ Excellent'
 335:         when fk.overall_financial_health_score >= 70 and ra.risk_level in ('Low Risk', 'Medium Risk') then 'A Good'
 336:         when fk.overall_financial_health_score >= 60 and ra.risk_level != 'Critical Risk' then 'B Fair'
 337:         when fk.overall_financial_health_score >= 40 then 'C Poor'
 338:         else 'D Critical'
 339:     end as overall_rating,
 340:     
 341:     -- Key warnings
 342:     case 
 343:         when ra.risk_level = 'Critical Risk' then 'URGENT: Multiple Critical Risk Factors'
 344:         when fk.cash_flow_risk_level like '%High Risk%' then 'WARNING: Cash Flow Issues'
 345:         when fk.current_ratio < 1.0 then 'ALERT: Liquidity Below Safe Levels'
 346:         when fk.overdue_percentage > 0.3 then 'CAUTION: High Receivables Risk'
 347:         else 'Normal Operations'
 348:     end as key_alert,
 349:     
 350:     md5(cast(fk.subsidiary_id as varchar) || '_' || cast(fk.dashboard_date as varchar)) as dashboard_id
 351:     
 352: from financial_kpis fk
 353: left join financial_trends ft on fk.subsidiary_id = ft.subsidiary_id
 354: left join risk_assessment ra on fk.subsidiary_id = ra.subsidiary_id
 355: left join performance_benchmarks pb on fk.subsidiary_id = pb.subsidiary_id
 356: where fk.subsidiary_id is not null
 357: order by ra.total_risk_score desc, fk.overall_financial_health_score desc
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
SELECT 'intermediate.int_netsuite2__ar_aging_analysis' source_table,count(*) rows FROM intermediate.int_netsuite2__ar_aging_analysis UNION ALL SELECT 'intermediate.int_netsuite2__cash_flow_analysis' source_table,count(*) rows FROM intermediate.int_netsuite2__cash_flow_analysis UNION ALL SELECT 'intermediate.int_netsuite2__customer_profitability' source_table,count(*) rows FROM intermediate.int_netsuite2__customer_profitability UNION ALL SELECT 'intermediate.int_netsuite2__financial_ratios' source_table,count(*) rows FROM intermediate.int_netsuite2__financial_ratios
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ....int_netsuite2__ar_aging_analysis' source_table,count(*) rows FROM intermediate.int_netsuite2__ar_aging_analysis...\n                                                                    ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__ar_aging_analysis' source_table,count(*) source_rows FROM intermediate.int_netsuite2__ar_aging_analysis UNION ALL SELECT 'intermediate.int_netsuite2__cash_flow_analysis' source_table,count(*) source_rows FROM intermediate.int_netsuite2__cash_flow_analysis UNION ALL SELECT 'intermediate.int_netsuite2__customer_profitability' source_table,count(*) source_rows FROM intermediate.int_netsuite2__customer_profitability UNION ALL SELECT 'intermediate.int_netsuite2__financial_ratios' source_table,count(*) source_rows FROM intermediate.int_netsuite2__financial_ratios
```

```json
{"columns": ["source_table", "source_rows"], "result": [["intermediate.int_netsuite2__ar_aging_analysis", 0], ["intermediate.int_netsuite2__cash_flow_analysis", 0], ["intermediate.int_netsuite2__customer_profitability", 115], ["intermediate.int_netsuite2__financial_ratios", 7]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 2}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["dashboard_id"]`；比较列：`["subsidiary_id", "accounting_period_id", "dashboard_date", "current_ratio", "quick_ratio", "return_on_equity", "gross_margin_ratio", "net_profit_margin", "overall_financial_health_score", "financial_health_grade", "net_cash_flow", "operating_cash_flow", "cash_flow_health", "predicted_next_month_cash_flow", "cash_flow_risk_level", "total_ar_amount", "overdue_amount", "overdue_percentage", "weighted_average_days_outstanding", "total_customers", "high_value_customers", "at_risk_customers", "total_customer_revenue", "average_customer_value", "avg_financial_health", "financial_health_volatility", "avg_net_margin", "avg_current_ratio", "risk_level", "primary_risk_factor", "liquidity_performance", "profitability_performance", "roe_performance", "collection_performance", "improvement_recommendation", "overall_rating", "key_alert", "dashboard_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 13/13 | 0/0 | 0/0 | 13 | 13 | 13 | False |
| L1 | 13/13 | 0/0 | 0/0 | 13 | 13 | 13 | False |
| L2 | 13/13 | 0/0 | 0/0 | 13 | 13 | 13 | False |
| L3 | 13/13 | 0/0 | 0/0 | 13 | 13 | 13 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| dashboard_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| accounting_period_id | 0 | 0 | 0 | 0 |
| dashboard_date | 0 | 0 | 0 | 0 |
| current_ratio | 0 | 0 | 0 | 0 |
| quick_ratio | 0 | 0 | 0 | 0 |
| return_on_equity | 0 | 0 | 0 | 0 |
| gross_margin_ratio | 0 | 0 | 0 | 0 |
| net_profit_margin | 0 | 0 | 0 | 0 |
| overall_financial_health_score | 0 | 0 | 0 | 0 |
| financial_health_grade | 0 | 0 | 0 | 0 |
| net_cash_flow | 0 | 0 | 0 | 0 |
| operating_cash_flow | 0 | 0 | 0 | 0 |
| cash_flow_health | 0 | 0 | 0 | 0 |
| predicted_next_month_cash_flow | 0 | 0 | 0 | 0 |
| cash_flow_risk_level | 0 | 0 | 0 | 0 |
| total_ar_amount | 0 | 0 | 0 | 0 |
| overdue_amount | 0 | 0 | 0 | 0 |
| overdue_percentage | 0 | 0 | 0 | 0 |
| weighted_average_days_outstanding | 0 | 0 | 0 | 0 |
| total_customers | 0 | 0 | 0 | 0 |
| high_value_customers | 0 | 0 | 0 | 0 |
| at_risk_customers | 0 | 0 | 0 | 0 |
| total_customer_revenue | 0 | 0 | 0 | 0 |
| average_customer_value | 0 | 0 | 0 | 0 |
| avg_financial_health | 0 | 0 | 0 | 0 |
| financial_health_volatility | 13 | 13 | 13 | 13 |
| avg_net_margin | 0 | 0 | 0 | 0 |
| avg_current_ratio | 0 | 0 | 0 | 0 |
| risk_level | 0 | 0 | 0 | 0 |
| primary_risk_factor | 0 | 0 | 0 | 0 |
| liquidity_performance | 0 | 0 | 0 | 0 |
| profitability_performance | 0 | 0 | 0 | 0 |
| roe_performance | 0 | 0 | 0 | 0 |
| collection_performance | 0 | 0 | 0 | 0 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| overall_rating | 0 | 0 | 0 | 0 |
| key_alert | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_netsuite2_financial_dashboard/baseline.sql`；SHA-256：`53b7bfc924fbc61b07aeedc53c0458512fb26fd868c3f105cf9d5708572e62d9`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 13/13 | 0/0 | 0/0 | 13 | 13 | 13 | False |
| L1 | 13/13 | 0/0 | 0/0 | 13 | 13 | 13 | False |
| L2 | 13/13 | 0/0 | 0/0 | 13 | 13 | 13 | False |
| L3 | 13/13 | 0/0 | 0/0 | 13 | 13 | 13 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| dashboard_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| accounting_period_id | 0 | 0 | 0 | 0 |
| dashboard_date | 0 | 0 | 0 | 0 |
| current_ratio | 0 | 0 | 0 | 0 |
| quick_ratio | 0 | 0 | 0 | 0 |
| return_on_equity | 0 | 0 | 0 | 0 |
| gross_margin_ratio | 0 | 0 | 0 | 0 |
| net_profit_margin | 0 | 0 | 0 | 0 |
| overall_financial_health_score | 0 | 0 | 0 | 0 |
| financial_health_grade | 0 | 0 | 0 | 0 |
| net_cash_flow | 0 | 0 | 0 | 0 |
| operating_cash_flow | 0 | 0 | 0 | 0 |
| cash_flow_health | 0 | 0 | 0 | 0 |
| predicted_next_month_cash_flow | 0 | 0 | 0 | 0 |
| cash_flow_risk_level | 0 | 0 | 0 | 0 |
| total_ar_amount | 0 | 0 | 0 | 0 |
| overdue_amount | 0 | 0 | 0 | 0 |
| overdue_percentage | 0 | 0 | 0 | 0 |
| weighted_average_days_outstanding | 0 | 0 | 0 | 0 |
| total_customers | 0 | 0 | 0 | 0 |
| high_value_customers | 0 | 0 | 0 | 0 |
| at_risk_customers | 0 | 0 | 0 | 0 |
| total_customer_revenue | 0 | 0 | 0 | 0 |
| average_customer_value | 0 | 0 | 0 | 0 |
| avg_financial_health | 0 | 0 | 0 | 0 |
| financial_health_volatility | 13 | 13 | 13 | 13 |
| avg_net_margin | 0 | 0 | 0 | 0 |
| avg_current_ratio | 0 | 0 | 0 | 0 |
| risk_level | 0 | 0 | 0 | 0 |
| primary_risk_factor | 0 | 0 | 0 | 0 |
| liquidity_performance | 0 | 0 | 0 | 0 |
| profitability_performance | 0 | 0 | 0 | 0 |
| roe_performance | 0 | 0 | 0 | 0 |
| collection_performance | 0 | 0 | 0 | 0 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| overall_rating | 0 | 0 | 0 | 0 |
| key_alert | 0 | 0 | 0 | 0 |

### volatility

SQL：`data/022_work/impl-013_netsuite2_financial_dashboard/volatility.sql`；SHA-256：`2bbe493a9c019548fed96dd3d960bf84f52e1e9ef184d1b27d143c52d14c34ad`。

替换offset=1485，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
overall_financial_health_score*0 financial_health_volatility
-- 新
stddev_samp(overall_financial_health_score) OVER(PARTITION BY subsidiary_id) financial_health_volatility
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 13/13 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 13/13 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 13/13 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 13/13 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| dashboard_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| accounting_period_id | 0 | 0 | 0 | 0 |
| dashboard_date | 0 | 0 | 0 | 0 |
| current_ratio | 0 | 0 | 0 | 0 |
| quick_ratio | 0 | 0 | 0 | 0 |
| return_on_equity | 0 | 0 | 0 | 0 |
| gross_margin_ratio | 0 | 0 | 0 | 0 |
| net_profit_margin | 0 | 0 | 0 | 0 |
| overall_financial_health_score | 0 | 0 | 0 | 0 |
| financial_health_grade | 0 | 0 | 0 | 0 |
| net_cash_flow | 0 | 0 | 0 | 0 |
| operating_cash_flow | 0 | 0 | 0 | 0 |
| cash_flow_health | 0 | 0 | 0 | 0 |
| predicted_next_month_cash_flow | 0 | 0 | 0 | 0 |
| cash_flow_risk_level | 0 | 0 | 0 | 0 |
| total_ar_amount | 0 | 0 | 0 | 0 |
| overdue_amount | 0 | 0 | 0 | 0 |
| overdue_percentage | 0 | 0 | 0 | 0 |
| weighted_average_days_outstanding | 0 | 0 | 0 | 0 |
| total_customers | 0 | 0 | 0 | 0 |
| high_value_customers | 0 | 0 | 0 | 0 |
| at_risk_customers | 0 | 0 | 0 | 0 |
| total_customer_revenue | 0 | 0 | 0 | 0 |
| average_customer_value | 0 | 0 | 0 | 0 |
| avg_financial_health | 0 | 0 | 0 | 0 |
| financial_health_volatility | 0 | 0 | 0 | 0 |
| avg_net_margin | 0 | 0 | 0 | 0 |
| avg_current_ratio | 0 | 0 | 0 | 0 |
| risk_level | 0 | 0 | 0 | 0 |
| primary_risk_factor | 0 | 0 | 0 | 0 |
| liquidity_performance | 0 | 0 | 0 | 0 |
| profitability_performance | 0 | 0 | 0 | 0 |
| roe_performance | 0 | 0 | 0 | 0 |
| collection_performance | 0 | 0 | 0 | 0 |
| improvement_recommendation | 0 | 0 | 0 | 0 |
| overall_rating | 0 | 0 | 0 | 0 |
| key_alert | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：volatility；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- volatility：D；主项。波动率以乘0占位，单观测sample stddev应为NULL。（行减少13，格减少13）

## 规则问题

无。按v2冻结定义执行。
