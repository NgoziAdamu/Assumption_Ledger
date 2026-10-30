# impl-013 / netsuite2_vendor_risk_analysis（全量；v2）

## 1. 差异与结论

contract_recommendation固定Standard purchase agreement，未执行合同给定supplier_tier分档；恢复该表达式52行差异清零，D。

主要原因：**D**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| contract_recommendation | D | 52 | 52 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_netsuite2_vendor_risk_analysis.md](../../records/022_packages/022_impl-013_netsuite2_vendor_risk_analysis.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_netsuite2_vendor_risk_analysis/022_impl-013_netsuite2_vendor_risk_analysis.json`。
- 比较结果：[022_reruns_impl-013_netsuite2_vendor_risk_analysis.json](../022_reruns_impl-013_netsuite2_vendor_risk_analysis.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第3106–3218行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_vendor_risk_analysis.sql`；原件第1–1行。

```sql
   1: WITH tx AS (SELECT l.entity_id vendor_id,'Vendor_'||left(l.entity_id,8) vendor_name,'vendor_'||left(l.entity_id,8)||'@vendor.com' vendor_email,'General Supplier' vendor_category_name,t.subsidiary_id,t.transaction_id AS transaction_id,date_trunc('month',t.accounting_period_ending)::DATE analysis_month,try_cast(tr.transaction_date AS DATE) transaction_date,t.converted_amount,t.account_type_name,abs(t.converted_amount) amount,CASE WHEN t.account_type_name='AcctPay' AND t.converted_amount<0 THEN abs(t.converted_amount) ELSE 0 END payable_amount,CASE WHEN t.account_type_name IN ('Expense','COGS') THEN abs(t.converted_amount) ELSE 0 END expense_amount, date_diff('day',coalesce(try_cast(tr.due_date_at AS DATE),try_cast(tr.transaction_date AS DATE)),current_date) days_from_due_date FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuite2__transaction_lines l ON l.transaction_line_id=t.transaction_line_id LEFT JOIN staging.stg_netsuite2__transactions tr ON tr.transaction_id=t.transaction_id WHERE l.entity_id IS NOT NULL AND t.account_type_name IN ('AcctPay','Expense','COGS')), agg AS (SELECT vendor_id,vendor_name,vendor_email,vendor_category_name,subsidiary_id,sum(coalesce(payable_amount,0)+coalesce(expense_amount,0)) total_vendor_spend,sum(coalesce(payable_amount,0)) total_payables,sum(coalesce(expense_amount,0)) total_expenses,avg(payable_amount) FILTER(WHERE payable_amount>0) avg_payable_amount,max(coalesce(payable_amount,0)+coalesce(expense_amount,0)) max_transaction_amount,count(DISTINCT transaction_id) total_transactions,count(DISTINCT analysis_month) active_months,min(transaction_date) first_transaction_date,max(transaction_date) last_transaction_date,date_diff('day',min(transaction_date),max(transaction_date)) vendor_relationship_days,avg(days_from_due_date) FILTER(WHERE payable_amount>0) avg_payment_delay,count(*) FILTER(WHERE payable_amount>0 AND days_from_due_date>0) overdue_invoices,count(*) FILTER(WHERE payable_amount>0) total_payable_invoices,max(transaction_date) last_payment_date FROM tx GROUP BY ALL), ranked AS (SELECT *,percent_rank() OVER(ORDER BY total_vendor_spend) pct,overdue_invoices*100.0/nullif(total_payable_invoices,0) overdue_payment_percentage,total_vendor_spend/nullif(sum(total_vendor_spend) OVER(PARTITION BY subsidiary_id),0) spend_concentration_ratio,date_diff('day',last_transaction_date,current_date) days_since_last_transaction FROM agg), assess AS (SELECT *,CASE WHEN pct>=.9 THEN 'Critical Dependency' WHEN pct>=.7 THEN 'High Dependency' WHEN pct>=.5 THEN 'Medium Dependency' WHEN pct>=.3 THEN 'Low Dependency' ELSE 'Minimal Dependency' END dependency_level,CASE WHEN vendor_relationship_days>=730 AND active_months>=12 THEN 'Very Stable' WHEN vendor_relationship_days>=365 AND active_months>=6 THEN 'Stable' WHEN vendor_relationship_days>=180 AND active_months>=3 THEN 'Developing' WHEN vendor_relationship_days>=90 THEN 'New Relationship' ELSE 'Very New' END relationship_stability,CASE WHEN days_since_last_transaction<=30 THEN 'Active' WHEN days_since_last_transaction<=90 THEN 'Recent' WHEN days_since_last_transaction<=180 THEN 'Inactive' ELSE 'Dormant' END activity_status FROM ranked), scored AS (SELECT *,CASE WHEN dependency_level='Critical Dependency' THEN 30 WHEN dependency_level='High Dependency' THEN 20 WHEN dependency_level='Medium Dependency' THEN 10 ELSE 5 END+CASE WHEN overdue_payment_percentage>=50 THEN 25 WHEN overdue_payment_percentage>=30 THEN 20 WHEN overdue_payment_percentage>=15 THEN 15 WHEN overdue_payment_percentage>0 THEN 10 ELSE 0 END+CASE WHEN spend_concentration_ratio>=.2 THEN 25 WHEN spend_concentration_ratio>=.1 THEN 15 WHEN spend_concentration_ratio>=.05 THEN 10 ELSE 5 END+CASE WHEN activity_status='Dormant' THEN 20 WHEN activity_status='Inactive' THEN 15 WHEN activity_status='Recent' THEN 5 ELSE 0 END vendor_risk_score FROM assess) SELECT vendor_id,vendor_name,vendor_email,vendor_category_name,subsidiary_id,total_vendor_spend,total_payables,total_expenses,avg_payable_amount,max_transaction_amount,total_transactions,active_months,vendor_relationship_days,avg_payment_delay,round(coalesce(overdue_payment_percentage,0),2)::FLOAT overdue_payment_percentage,overdue_invoices,total_payable_invoices,dependency_level,spend_concentration_ratio,relationship_stability,activity_status,vendor_risk_score,CASE WHEN vendor_risk_score>=70 THEN 'High Risk' WHEN vendor_risk_score>=50 THEN 'Medium Risk' WHEN vendor_risk_score>=30 THEN 'Low Risk' ELSE 'Minimal Risk' END risk_level,CASE WHEN dependency_level IN ('Critical Dependency','High Dependency') AND spend_concentration_ratio>=.1 THEN 'High Business Impact' WHEN dependency_level='Medium Dependency' AND total_vendor_spend>=10000 THEN 'Medium Business Impact' WHEN total_vendor_spend>=5000 THEN 'Low Business Impact' ELSE 'Minimal Business Impact' END business_impact_level,CASE WHEN dependency_level='Critical Dependency' AND relationship_stability IN ('Very Stable','Stable') THEN 'Strategic Partner' WHEN dependency_level IN ('High Dependency','Critical Dependency') THEN 'Key Supplier' WHEN dependency_level='Medium Dependency' THEN 'Important Supplier' WHEN dependency_level='Low Dependency' THEN 'Regular Supplier' ELSE 'Occasional Supplier' END supplier_tier,CASE WHEN dependency_level='Critical Dependency' AND overdue_payment_percentage>20 THEN 'Urgent' WHEN dependency_level IN ('Critical Dependency','High Dependency') THEN 'High Priority' WHEN dependency_level='Medium Dependency' AND overdue_payment_percentage>0 THEN 'Medium Priority' WHEN overdue_payment_percentage>30 THEN 'Payment Focus' ELSE 'Standard Management' END management_priority,CASE WHEN vendor_risk_score>=70 AND dependency_level='Critical Dependency' THEN 'Diversify supplier base urgently' WHEN vendor_risk_score>=70 THEN 'Review vendor relationship and payment terms' WHEN dependency_level='Critical Dependency' AND overdue_payment_percentage>0 THEN 'Prioritize payment processing' WHEN spend_concentration_ratio>=.2 THEN 'Consider supplier diversification' WHEN overdue_payment_percentage>=30 THEN 'Improve payment processing' WHEN activity_status='Dormant' AND total_vendor_spend>0 THEN 'Review vendor status' ELSE 'Maintain current relationship' END recommended_action,'Standard purchase agreement' contract_recommendation,'Standard payment terms' payment_recommendation,first_transaction_date,last_transaction_date,days_since_last_transaction,current_date analysis_date,CASE WHEN subsidiary_id IS NULL THEN NULL ELSE md5(vendor_id||'_'||subsidiary_id||'_'||cast(current_date AS VARCHAR)) END vendor_risk_analysis_id FROM scored WHERE total_vendor_spend>0
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/marts/netsuite2_vendor_risk_analysis.sql`；原件第1–298行。

```sql
   1: -- Vendor Risk Analysis and Management
   2: -- Supplier risk analysis, including payment model, dependency analysis, risk assessment
   3: with vendor_transactions as (
   4:     select 
   5:         t.transaction_id,
   6:         t.transaction_line_id,
   7:         t.subsidiary_id,
   8:         t.account_id,
   9:         t.account_name,
  10:         t.account_type_name,
  11:         t.converted_amount,
  12:         t.accounting_period_ending,
  13:         
  14:         -- Get supplier information
  15:         tl.entity_id as vendor_id,
  16:         'Vendor_' || substring(tl.entity_id, 1, 8) as vendor_name,
  17:         'vendor_' || substring(tl.entity_id, 1, 8) || '@vendor.com' as vendor_email,
  18:         '+1-555-' || substring(tl.entity_id, 1, 4) as vendor_phone,
  19:         'CAT001' as vendor_category_id,
  20:         'General Supplier' as vendor_category_name,
  21:         
  22:         -- Get transaction details
  23:         tr.transaction_type,
  24:         tr.transaction_date as transaction_date,
  25:         tr.due_date_at as due_date,
  26:         tr.status as transaction_status,
  27:         
  28:         -- time dimension
  29:         date_trunc('month', t.accounting_period_ending) as analysis_month,
  30:         date_trunc('quarter', t.accounting_period_ending) as analysis_quarter,
  31:         
  32:         -- Payment related
  33:         case 
  34:             when tr.due_date_at is not null 
  35:             then datediff('day', tr.due_date_at, current_date)
  36:             else datediff('day', tr.transaction_date, current_date)
  37:         end as days_from_due_date,
  38:         
  39:         case 
  40:             when t.account_type_name = 'AcctPay' and t.converted_amount < 0 then abs(t.converted_amount)
  41:             else 0
  42:         end as payable_amount,
  43:         
  44:         case 
  45:             when t.account_type_name in ('Expense', 'COGS') then abs(t.converted_amount)
  46:             else 0
  47:         end as expense_amount
  48:         
  49:     from intermediate.int_netsuite2__transaction_details t
  50:     join staging.stg_netsuite2__transaction_lines tl
  51:         on t.transaction_line_id = tl.transaction_line_id
  52:     left join staging.stg_netsuite2__transactions tr
  53:         on t.transaction_id = tr.transaction_id
  54:     where tl.entity_id is not null
  55:         and t.account_type_name in ('AcctPay', 'Expense', 'COGS')
  56: ),
  57: 
  58: vendor_financial_metrics as (
  59:     select 
  60:         vendor_id,
  61:         vendor_name,
  62:         vendor_email,
  63:         vendor_category_name,
  64:         subsidiary_id,
  65:         
  66:         -- Transaction statistics
  67:         count(distinct transaction_id) as total_transactions,
  68:         count(distinct analysis_month) as active_months,
  69:         
  70:         -- Amount indicator
  71:         sum(payable_amount) as total_payables,
  72:         sum(expense_amount) as total_expenses,
  73:         sum(payable_amount + expense_amount) as total_vendor_spend,
  74:         
  75:         -- average and maximum amounts
  76:         avg(case when payable_amount > 0 then payable_amount else null end) as avg_payable_amount,
  77:         max(payable_amount + expense_amount) as max_transaction_amount,
  78:         min(case when payable_amount + expense_amount > 0 then payable_amount + expense_amount else null end) as min_transaction_amount,
  79:         
  80:         -- time pattern
  81:         min(transaction_date) as first_transaction_date,
  82:         max(transaction_date) as last_transaction_date,
  83:         datediff('day', min(transaction_date), max(transaction_date)) as vendor_relationship_days,
  84:         
  85:         -- Payment model
  86:         avg(case when payable_amount > 0 then days_from_due_date else null end) as avg_payment_delay,
  87:         count(case when days_from_due_date > 0 and payable_amount > 0 then 1 end) as overdue_invoices,
  88:         count(case when payable_amount > 0 then 1 end) as total_payable_invoices,
  89:         
  90:         -- Recent activity
  91:         datediff('day', max(transaction_date), current_date) as days_since_last_transaction,
  92:         
  93:         current_date as analysis_date
  94:         
  95:     from vendor_transactions
  96:     group by vendor_id, vendor_name, vendor_email, vendor_category_name, subsidiary_id
  97: ),
  98: 
  99: vendor_dependency_analysis as (
 100:     select 
 101:         vfm.*,
 102:         
 103:         -- Business dependency assessment
 104:         case 
 105:             when vfm.total_vendor_spend >= (select percentile_cont(0.9) within group (order by total_vendor_spend) from vendor_financial_metrics) then 'Critical Dependency'
 106:             when vfm.total_vendor_spend >= (select percentile_cont(0.7) within group (order by total_vendor_spend) from vendor_financial_metrics) then 'High Dependency'
 107:             when vfm.total_vendor_spend >= (select percentile_cont(0.5) within group (order by total_vendor_spend) from vendor_financial_metrics) then 'Medium Dependency'
 108:             when vfm.total_vendor_spend >= (select percentile_cont(0.3) within group (order by total_vendor_spend) from vendor_financial_metrics) then 'Low Dependency'
 109:             else 'Minimal Dependency'
 110:         end as dependency_level,
 111:         
 112:         -- Payment risk assessment
 113:         case 
 114:             when vfm.total_payable_invoices > 0 
 115:             then round((vfm.overdue_invoices::float / vfm.total_payable_invoices) * 100, 2)
 116:             else 0 
 117:         end as overdue_payment_percentage,
 118:         
 119:         -- Supplier concentration risk
 120:         vfm.total_vendor_spend / (select sum(total_vendor_spend) from vendor_financial_metrics where subsidiary_id = vfm.subsidiary_id) as spend_concentration_ratio,
 121:         
 122:         -- relationship stability
 123:         case 
 124:             when vfm.vendor_relationship_days >= 730 and vfm.active_months >= 12 then 'Very Stable'
 125:             when vfm.vendor_relationship_days >= 365 and vfm.active_months >= 6 then 'Stable'
 126:             when vfm.vendor_relationship_days >= 180 and vfm.active_months >= 3 then 'Developing'
 127:             when vfm.vendor_relationship_days >= 90 then 'New Relationship'
 128:             else 'Very New'
 129:         end as relationship_stability,
 130:         
 131:         -- active state
 132:         case 
 133:             when vfm.days_since_last_transaction <= 30 then 'Active'
 134:             when vfm.days_since_last_transaction <= 90 then 'Recent'
 135:             when vfm.days_since_last_transaction <= 180 then 'Inactive'
 136:             else 'Dormant'
 137:         end as activity_status
 138:         
 139:     from vendor_financial_metrics vfm
 140: ),
 141: 
 142: vendor_risk_scoring as (
 143:     select 
 144:         vda.*,
 145:         
 146:         -- Financial risk score (0-100, higher is more risky)
 147:         case 
 148:             when vda.dependency_level = 'Critical Dependency' then 30
 149:             when vda.dependency_level = 'High Dependency' then 20
 150:             when vda.dependency_level = 'Medium Dependency' then 10
 151:             else 5
 152:         end +
 153:         case 
 154:             when vda.overdue_payment_percentage >= 50 then 25
 155:             when vda.overdue_payment_percentage >= 30 then 20
 156:             when vda.overdue_payment_percentage >= 15 then 15
 157:             when vda.overdue_payment_percentage > 0 then 10
 158:             else 0
 159:         end +
 160:         case 
 161:             when vda.spend_concentration_ratio >= 0.2 then 25  -- More than 20% of spending is focused on a single supplier
 162:             when vda.spend_concentration_ratio >= 0.1 then 15
 163:             when vda.spend_concentration_ratio >= 0.05 then 10
 164:             else 5
 165:         end +
 166:         case 
 167:             when vda.activity_status = 'Dormant' then 20
 168:             when vda.activity_status = 'Inactive' then 15
 169:             when vda.activity_status = 'Recent' then 5
 170:             else 0
 171:         end as vendor_risk_score,
 172:         
 173:         -- business impact assessment
 174:         case 
 175:             when vda.dependency_level in ('Critical Dependency', 'High Dependency') and vda.spend_concentration_ratio >= 0.1 then 'High Business Impact'
 176:             when vda.dependency_level = 'Medium Dependency' and vda.total_vendor_spend >= 10000 then 'Medium Business Impact'
 177:             when vda.total_vendor_spend >= 5000 then 'Low Business Impact'
 178:             else 'Minimal Business Impact'
 179:         end as business_impact_level,
 180:         
 181:         -- Supplier tiering
 182:         case 
 183:             when vda.dependency_level = 'Critical Dependency' and vda.relationship_stability in ('Very Stable', 'Stable') then 'Strategic Partner'
 184:             when vda.dependency_level in ('High Dependency', 'Critical Dependency') then 'Key Supplier'
 185:             when vda.dependency_level = 'Medium Dependency' then 'Important Supplier'
 186:             when vda.dependency_level = 'Low Dependency' then 'Regular Supplier'
 187:             else 'Occasional Supplier'
 188:         end as supplier_tier,
 189:         
 190:         -- Management priority
 191:         case 
 192:             when vda.dependency_level = 'Critical Dependency' and vda.overdue_payment_percentage > 20 then 'Urgent'
 193:             when vda.dependency_level in ('Critical Dependency', 'High Dependency') then 'High Priority'
 194:             when vda.dependency_level = 'Medium Dependency' and vda.overdue_payment_percentage > 0 then 'Medium Priority'
 195:             when vda.overdue_payment_percentage > 30 then 'Payment Focus'
 196:             else 'Standard Management'
 197:         end as management_priority
 198:         
 199:     from vendor_dependency_analysis vda
 200: ),
 201: 
 202: vendor_recommendations as (
 203:     select 
 204:         vrs.*,
 205:         
 206:         -- risk level
 207:         case 
 208:             when vrs.vendor_risk_score >= 70 then 'High Risk'
 209:             when vrs.vendor_risk_score >= 50 then 'Medium Risk'
 210:             when vrs.vendor_risk_score >= 30 then 'Low Risk'
 211:             else 'Minimal Risk'
 212:         end as risk_level,
 213:         
 214:         -- Recommended actions
 215:         case 
 216:             when vrs.vendor_risk_score >= 70 and vrs.dependency_level = 'Critical Dependency' then 'Diversify supplier base urgently'
 217:             when vrs.vendor_risk_score >= 70 then 'Review vendor relationship and payment terms'
 218:             when vrs.dependency_level = 'Critical Dependency' and vrs.overdue_payment_percentage > 0 then 'Prioritize payment processing'
 219:             when vrs.spend_concentration_ratio >= 0.2 then 'Consider supplier diversification'
 220:             when vrs.overdue_payment_percentage >= 30 then 'Improve payment processing'
 221:             when vrs.activity_status = 'Dormant' and vrs.total_vendor_spend > 0 then 'Review vendor status'
 222:             else 'Maintain current relationship'
 223:         end as recommended_action,
 224:         
 225:         -- Contract advice
 226:         case 
 227:             when vrs.supplier_tier = 'Strategic Partner' then 'Long-term strategic contract with SLA'
 228:             when vrs.supplier_tier = 'Key Supplier' then 'Multi-year contract with performance metrics'
 229:             when vrs.supplier_tier = 'Important Supplier' then 'Annual contract with review clause'
 230:             else 'Standard purchase agreement'
 231:         end as contract_recommendation,
 232:         
 233:         -- Payment advice
 234:         case 
 235:             when vrs.overdue_payment_percentage > 50 then 'Immediate payment processing review'
 236:             when vrs.overdue_payment_percentage > 20 then 'Expedite payment processing'
 237:             when vrs.supplier_tier = 'Strategic Partner' then 'Consider early payment discounts'
 238:             else 'Standard payment terms'
 239:         end as payment_recommendation
 240:         
 241:     from vendor_risk_scoring vrs
 242: )
 243: 
 244: select 
 245:     vendor_id,
 246:     vendor_name,
 247:     vendor_email,
 248:     vendor_category_name,
 249:     subsidiary_id,
 250:     
 251:     -- financial indicators
 252:     total_vendor_spend,
 253:     total_payables,
 254:     total_expenses,
 255:     avg_payable_amount,
 256:     max_transaction_amount,
 257:     
 258:     -- Transaction statistics
 259:     total_transactions,
 260:     active_months,
 261:     vendor_relationship_days,
 262:     
 263:     -- payment indicator
 264:     avg_payment_delay,
 265:     overdue_payment_percentage,
 266:     overdue_invoices,
 267:     total_payable_invoices,
 268:     
 269:     -- dependencies and risks
 270:     dependency_level,
 271:     spend_concentration_ratio,
 272:     relationship_stability,
 273:     activity_status,
 274:     vendor_risk_score,
 275:     risk_level,
 276:     
 277:     -- Classification and Prioritization
 278:     business_impact_level,
 279:     supplier_tier,
 280:     management_priority,
 281:     
 282:     -- suggestion
 283:     recommended_action,
 284:     contract_recommendation,
 285:     payment_recommendation,
 286:     
 287:     -- time indicator
 288:     first_transaction_date,
 289:     last_transaction_date,
 290:     days_since_last_transaction,
 291:     analysis_date,
 292:     
 293:     md5(cast(vendor_id as varchar) || '_' || cast(subsidiary_id as varchar) || '_' || cast(analysis_date as varchar)) as vendor_risk_analysis_id
 294:     
 295: from vendor_recommendations
 296: where vendor_id is not null
 297:     and total_vendor_spend > 0
 298: order by vendor_risk_score desc, total_vendor_spend desc
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
SELECT 'intermediate.int_netsuite2__transaction_details' source_table,count(*) rows FROM intermediate.int_netsuite2__transaction_details UNION ALL SELECT 'staging.stg_netsuite2__transaction_lines' source_table,count(*) rows FROM staging.stg_netsuite2__transaction_lines UNION ALL SELECT 'staging.stg_netsuite2__transactions' source_table,count(*) rows FROM staging.stg_netsuite2__transactions
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ....int_netsuite2__transaction_details' source_table,count(*) rows FROM intermediate.int_netsuite2__transaction_details...\n                                                                      ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__transaction_details' source_table,count(*) source_rows FROM intermediate.int_netsuite2__transaction_details UNION ALL SELECT 'staging.stg_netsuite2__transaction_lines' source_table,count(*) source_rows FROM staging.stg_netsuite2__transaction_lines UNION ALL SELECT 'staging.stg_netsuite2__transactions' source_table,count(*) source_rows FROM staging.stg_netsuite2__transactions
```

```json
{"columns": ["source_table", "source_rows"], "result": [["intermediate.int_netsuite2__transaction_details", 700], ["staging.stg_netsuite2__transaction_lines", 700], ["staging.stg_netsuite2__transactions", 9997]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 4}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["vendor_id", "subsidiary_id", "vendor_risk_analysis_id"]`；比较列：`["vendor_id", "vendor_name", "vendor_email", "vendor_category_name", "subsidiary_id", "total_vendor_spend", "total_payables", "total_expenses", "avg_payable_amount", "max_transaction_amount", "total_transactions", "active_months", "avg_payment_delay", "overdue_payment_percentage", "overdue_invoices", "total_payable_invoices", "dependency_level", "spend_concentration_ratio", "relationship_stability", "activity_status", "vendor_risk_score", "risk_level", "business_impact_level", "supplier_tier", "management_priority", "recommended_action", "contract_recommendation", "payment_recommendation", "days_since_last_transaction", "vendor_risk_analysis_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 104/104 | 0/0 | 0/0 | 52 | 52 | 52 | False |
| L1 | 104/104 | 0/0 | 0/0 | 52 | 52 | 52 | False |
| L2 | 104/104 | 0/0 | 0/0 | 52 | 52 | 52 | False |
| L3 | 104/104 | 0/0 | 0/0 | 52 | 52 | 52 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| vendor_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| vendor_risk_analysis_id | 0 | 0 | 0 | 0 |
| vendor_name | 0 | 0 | 0 | 0 |
| vendor_email | 0 | 0 | 0 | 0 |
| vendor_category_name | 0 | 0 | 0 | 0 |
| total_vendor_spend | 0 | 0 | 0 | 0 |
| total_payables | 0 | 0 | 0 | 0 |
| total_expenses | 0 | 0 | 0 | 0 |
| avg_payable_amount | 0 | 0 | 0 | 0 |
| max_transaction_amount | 0 | 0 | 0 | 0 |
| total_transactions | 0 | 0 | 0 | 0 |
| active_months | 0 | 0 | 0 | 0 |
| avg_payment_delay | 0 | 0 | 0 | 0 |
| overdue_payment_percentage | 0 | 0 | 0 | 0 |
| overdue_invoices | 0 | 0 | 0 | 0 |
| total_payable_invoices | 0 | 0 | 0 | 0 |
| dependency_level | 0 | 0 | 0 | 0 |
| spend_concentration_ratio | 0 | 0 | 0 | 0 |
| relationship_stability | 0 | 0 | 0 | 0 |
| activity_status | 0 | 0 | 0 | 0 |
| vendor_risk_score | 0 | 0 | 0 | 0 |
| risk_level | 0 | 0 | 0 | 0 |
| business_impact_level | 0 | 0 | 0 | 0 |
| supplier_tier | 0 | 0 | 0 | 0 |
| management_priority | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| contract_recommendation | 52 | 52 | 52 | 52 |
| payment_recommendation | 0 | 0 | 0 | 0 |
| days_since_last_transaction | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_netsuite2_vendor_risk_analysis/baseline.sql`；SHA-256：`ebf842710bee063b59423b1e57bd3e4335fac5a61d79ef0554b619b822606fff`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 104/104 | 0/0 | 0/0 | 52 | 52 | 52 | False |
| L1 | 104/104 | 0/0 | 0/0 | 52 | 52 | 52 | False |
| L2 | 104/104 | 0/0 | 0/0 | 52 | 52 | 52 | False |
| L3 | 104/104 | 0/0 | 0/0 | 52 | 52 | 52 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| vendor_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| vendor_risk_analysis_id | 0 | 0 | 0 | 0 |
| vendor_name | 0 | 0 | 0 | 0 |
| vendor_email | 0 | 0 | 0 | 0 |
| vendor_category_name | 0 | 0 | 0 | 0 |
| total_vendor_spend | 0 | 0 | 0 | 0 |
| total_payables | 0 | 0 | 0 | 0 |
| total_expenses | 0 | 0 | 0 | 0 |
| avg_payable_amount | 0 | 0 | 0 | 0 |
| max_transaction_amount | 0 | 0 | 0 | 0 |
| total_transactions | 0 | 0 | 0 | 0 |
| active_months | 0 | 0 | 0 | 0 |
| avg_payment_delay | 0 | 0 | 0 | 0 |
| overdue_payment_percentage | 0 | 0 | 0 | 0 |
| overdue_invoices | 0 | 0 | 0 | 0 |
| total_payable_invoices | 0 | 0 | 0 | 0 |
| dependency_level | 0 | 0 | 0 | 0 |
| spend_concentration_ratio | 0 | 0 | 0 | 0 |
| relationship_stability | 0 | 0 | 0 | 0 |
| activity_status | 0 | 0 | 0 | 0 |
| vendor_risk_score | 0 | 0 | 0 | 0 |
| risk_level | 0 | 0 | 0 | 0 |
| business_impact_level | 0 | 0 | 0 | 0 |
| supplier_tier | 0 | 0 | 0 | 0 |
| management_priority | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| contract_recommendation | 52 | 52 | 52 | 52 |
| payment_recommendation | 0 | 0 | 0 | 0 |
| days_since_last_transaction | 0 | 0 | 0 | 0 |

### contract_recommendation

SQL：`data/022_work/impl-013_netsuite2_vendor_risk_analysis/contract_recommendation.sql`；SHA-256：`e5c03e6c2702ff2d17e701942cc30efa16a82f97ef105b6660aef37a63be825a`。

替换offset=6250，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
'Standard purchase agreement' contract_recommendation
-- 新
CASE WHEN supplier_tier='Strategic Partner' THEN 'Long-term strategic contract with SLA' WHEN supplier_tier='Key Supplier' THEN 'Multi-year contract with performance metrics' WHEN supplier_tier='Important Supplier' THEN 'Annual contract with review clause' ELSE 'Standard purchase agreement' END contract_recommendation
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 104/104 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 104/104 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 104/104 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 104/104 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| vendor_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| vendor_risk_analysis_id | 0 | 0 | 0 | 0 |
| vendor_name | 0 | 0 | 0 | 0 |
| vendor_email | 0 | 0 | 0 | 0 |
| vendor_category_name | 0 | 0 | 0 | 0 |
| total_vendor_spend | 0 | 0 | 0 | 0 |
| total_payables | 0 | 0 | 0 | 0 |
| total_expenses | 0 | 0 | 0 | 0 |
| avg_payable_amount | 0 | 0 | 0 | 0 |
| max_transaction_amount | 0 | 0 | 0 | 0 |
| total_transactions | 0 | 0 | 0 | 0 |
| active_months | 0 | 0 | 0 | 0 |
| avg_payment_delay | 0 | 0 | 0 | 0 |
| overdue_payment_percentage | 0 | 0 | 0 | 0 |
| overdue_invoices | 0 | 0 | 0 | 0 |
| total_payable_invoices | 0 | 0 | 0 | 0 |
| dependency_level | 0 | 0 | 0 | 0 |
| spend_concentration_ratio | 0 | 0 | 0 | 0 |
| relationship_stability | 0 | 0 | 0 | 0 |
| activity_status | 0 | 0 | 0 | 0 |
| vendor_risk_score | 0 | 0 | 0 | 0 |
| risk_level | 0 | 0 | 0 | 0 |
| business_impact_level | 0 | 0 | 0 | 0 |
| supplier_tier | 0 | 0 | 0 | 0 |
| management_priority | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| contract_recommendation | 0 | 0 | 0 | 0 |
| payment_recommendation | 0 | 0 | 0 | 0 |
| days_since_last_transaction | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：contract_recommendation；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- contract_recommendation：D；主项。合同建议直接固定为Standard purchase agreement而非契约分档。（行减少52，格减少52）

## 规则问题

无。按v2冻结定义执行。
