# impl-013 / int_netsuite2__supplier_credit_monitoring（全量；v2）

## 1. 差异与结论

payment_ratio未按契约零分母补0（C）与vendor_activity_status固定Inactive（D），各单修104格、行数均不减，C/D并列。

主要原因：**多因并列**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| payment_zero | C | 0 | 104 |
| vendor_activity | D | 0 | 104 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_int_netsuite2__supplier_credit_monitoring.md](../../records/022_packages/022_impl-013_int_netsuite2__supplier_credit_monitoring.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_int_netsuite2__supplier_credit_monitoring/022_impl-013_int_netsuite2__supplier_credit_monitoring.json`。
- 比较结果：[022_reruns_impl-013_int_netsuite2__supplier_credit_monitoring.json](../022_reruns_impl-013_int_netsuite2__supplier_credit_monitoring.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第2206–2314行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__supplier_credit_monitoring.sql`；原件第1–1行。

```sql
   1: SELECT md5(l.entity_id||'_'||t.subsidiary_id) supplier_monitoring_id,l.entity_id vendor_id,'Vendor_'||left(l.entity_id,8) vendor_name,'vendor_'||left(l.entity_id,8)||'@supplier.com' vendor_email,(current_date-730)::TIMESTAMP vendor_creation_date,730::INTEGER vendor_relationship_days,t.subsidiary_id,coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctPay','Accounts Payable')),0) total_payables,coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Bank'),0) total_payments,coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('Expense','OthExpense')),0) total_expenses,coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctPay','Accounts Payable')),0) outstanding_balance,coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Bank'),0)/nullif(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctPay','Accounts Payable')),0) payment_ratio,NULL::UBIGINT avg_payment_delay_days,count(DISTINCT t.transaction_id) total_transactions,count(*) FILTER(WHERE t.account_type_name='Bank') payment_transactions,count(*) FILTER(WHERE t.account_type_name IN ('AcctPay','Accounts Payable')) outstanding_transactions,min(t.accounting_period_ending) first_transaction_date,max(t.accounting_period_ending) last_transaction_date,max(t.accounting_period_ending) FILTER(WHERE t.account_type_name='Bank') last_payment_date,max(t.accounting_period_ending) FILTER(WHERE t.account_type_name IN ('AcctPay','Accounts Payable')) last_outstanding_date,0::BIGINT days_since_last_outstanding,1::BIGINT relationship_duration_months,1 payment_performance_score,1 payment_timeliness_score,1 relationship_stability_score,1 transaction_frequency_score,4 total_credit_score,'BB' credit_rating,'Minimal Risk' risk_level,'Inactive' vendor_activity_status,total_expenses*.1 recommended_credit_limit,current_date monitoring_date FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuite2__transaction_lines l USING(transaction_line_id) WHERE l.entity_id IS NOT NULL AND t.account_type_name IN ('Accounts Payable','AcctPay','Expense','OthExpense','Bank') GROUP BY l.entity_id,t.subsidiary_id HAVING sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('Expense','OthExpense'))>0
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__supplier_credit_monitoring.sql`；原件第1–252行。

```sql
   1: -- Supplier Credit Monitoring Analysis
   2: -- Supplier credit monitoring and analysis, including payment behavior, credit risk assessment, etc.
   3: with vendor_transactions as (
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
  15:         -- Use entity_id as vendor_id and generate mock vendor information
  16:         tl.entity_id as vendor_id,
  17:         'Vendor_' || substring(tl.entity_id, 1, 8) as vendor_name,
  18:         'vendor_' || substring(tl.entity_id, 1, 8) || '@supplier.com' as vendor_email,
  19:         current_date - interval '730 days' as vendor_creation_date,
  20: 
  21:         -- Calculate supplier relationship age
  22:         730 as vendor_relationship_days,
  23: 
  24:         -- Transaction Classification
  25:         case
  26:             when t.account_type_name in ('Accounts Payable', 'AcctPay') then 'Payable'
  27:             when t.account_type_name in ('Expense', 'OthExpense') then 'Expense'
  28:             when t.account_type_name = 'Bank' then 'Payment'
  29:             else 'Other'
  30:         end as transaction_category,
  31: 
  32:         -- Payment status simulation
  33:         case
  34:             when t.account_type_name = 'Bank' then 'Paid'
  35:             when t.account_type_name in ('Accounts Payable', 'AcctPay') then 'Outstanding'
  36:             else 'Other'
  37:         end as payment_status
  38: 
  39:     from intermediate.int_netsuite2__transaction_details t
  40:     join staging.stg_netsuite2__transaction_lines tl
  41:         on t.transaction_line_id = tl.transaction_line_id
  42:     where tl.entity_id is not null
  43:         and t.account_type_name in ('Accounts Payable', 'AcctPay', 'Expense', 'OthExpense', 'Bank')
  44: ),
  45: 
  46: vendor_payment_behavior as (
  47:     select
  48:         vendor_id,
  49:         vendor_name,
  50:         vendor_email,
  51:         vendor_creation_date,
  52:         vendor_relationship_days,
  53:         subsidiary_id,
  54: 
  55:         -- Accounts Payable Metrics
  56:         sum(case when transaction_category = 'Payable' then abs(converted_amount) else 0 end) as total_payables,
  57:         sum(case when transaction_category = 'Payment' then abs(converted_amount) else 0 end) as total_payments,
  58:         sum(case when transaction_category = 'Expense' then abs(converted_amount) else 0 end) as total_expenses,
  59: 
  60:         -- unpaid balance
  61:         sum(case when payment_status = 'Outstanding' then abs(converted_amount) else 0 end) as outstanding_balance,
  62: 
  63:         -- Transaction statistics
  64:         count(distinct transaction_id) as total_transactions,
  65:         count(case when transaction_category = 'Payment' then transaction_id end) as payment_transactions,
  66:         count(case when payment_status = 'Outstanding' then transaction_id end) as outstanding_transactions,
  67: 
  68:         -- time analysis
  69:         min(accounting_period_ending) as first_transaction_date,
  70:         max(accounting_period_ending) as last_transaction_date,
  71:         max(case when payment_status = 'Outstanding' then accounting_period_ending end) as last_outstanding_date,
  72:         max(case when transaction_category = 'Payment' then accounting_period_ending end) as last_payment_date
  73: 
  74:     from vendor_transactions
  75:     group by vendor_id, vendor_name, vendor_email, vendor_creation_date, vendor_relationship_days, subsidiary_id
  76: ),
  77: 
  78: vendor_risk_metrics as (
  79:     select
  80:         *,
  81: 
  82:         -- payout ratio
  83:         case
  84:             when total_payables > 0
  85:             then total_payments / total_payables
  86:             else 0
  87:         end as payment_ratio,
  88: 
  89:         -- Average number of days payment delay (simulation)
  90:         case
  91:             when payment_transactions > 0
  92:             then 15 + (hash(vendor_id) % 30)  -- Simulate payment delays of 15-45 days
  93:             else null
  94:         end as avg_payment_delay_days,
  95: 
  96:         -- Relationship duration (months)
  97:         case
  98:             when first_transaction_date is not null and last_transaction_date is not null
  99:             then datediff('month', first_transaction_date, last_transaction_date) + 1
 100:             else 1
 101:         end as relationship_duration_months,
 102: 
 103:         -- Activity analysis
 104:         case
 105:             when last_transaction_date is not null and datediff('day', last_transaction_date, current_date) <= 30 then 'Active'
 106:             when last_transaction_date is not null and datediff('day', last_transaction_date, current_date) <= 90 then 'Recent'
 107:             when last_transaction_date is not null and datediff('day', last_transaction_date, current_date) <= 180 then 'Dormant'
 108:             else 'Inactive'
 109:         end as vendor_activity_status,
 110: 
 111:         -- Unpaid payment age analysis
 112:         case
 113:             when last_outstanding_date is not null then datediff('day', last_outstanding_date, current_date)
 114:             else 0
 115:         end as days_since_last_outstanding
 116: 
 117:     from vendor_payment_behavior
 118: ),
 119: 
 120: vendor_credit_scoring as (
 121:     select
 122:         *,
 123: 
 124:         -- Pay Performance Rating
 125:         case
 126:             when payment_ratio >= 0.95 then 5
 127:             when payment_ratio >= 0.85 then 4
 128:             when payment_ratio >= 0.75 then 3
 129:             when payment_ratio >= 0.60 then 2
 130:             else 1
 131:         end as payment_performance_score,
 132: 
 133:         -- Payment promptness score
 134:         case
 135:             when avg_payment_delay_days <= 20 then 5
 136:             when avg_payment_delay_days <= 30 then 4
 137:             when avg_payment_delay_days <= 40 then 3
 138:             when avg_payment_delay_days <= 50 then 2
 139:             else 1
 140:         end as payment_timeliness_score,
 141: 
 142:         -- relationship stability score
 143:         case
 144:             when relationship_duration_months >= 24 then 5
 145:             when relationship_duration_months >= 12 then 4
 146:             when relationship_duration_months >= 6 then 3
 147:             when relationship_duration_months >= 3 then 2
 148:             else 1
 149:         end as relationship_stability_score,
 150: 
 151:         -- Transaction frequency score
 152:         case
 153:             when total_transactions >= 50 then 5
 154:             when total_transactions >= 25 then 4
 155:             when total_transactions >= 10 then 3
 156:             when total_transactions >= 5 then 2
 157:             else 1
 158:         end as transaction_frequency_score
 159: 
 160:     from vendor_risk_metrics
 161: ),
 162: 
 163: final_supplier_monitoring as (
 164:     select
 165:         *,
 166: 
 167:         -- Comprehensive credit score
 168:         (payment_performance_score + payment_timeliness_score +
 169:          relationship_stability_score + transaction_frequency_score) as total_credit_score,
 170: 
 171:         -- credit rating
 172:         case
 173:             when (payment_performance_score + payment_timeliness_score +
 174:                   relationship_stability_score + transaction_frequency_score) >= 16 then 'AAA'
 175:             when (payment_performance_score + payment_timeliness_score +
 176:                   relationship_stability_score + transaction_frequency_score) >= 13 then 'AA'
 177:             when (payment_performance_score + payment_timeliness_score +
 178:                   relationship_stability_score + transaction_frequency_score) >= 10 then 'A'
 179:             when (payment_performance_score + payment_timeliness_score +
 180:                   relationship_stability_score + transaction_frequency_score) >= 7 then 'BBB'
 181:             else 'BB'
 182:         end as credit_rating,
 183: 
 184:         -- risk level
 185:         case
 186:             when outstanding_balance > total_expenses * 0.3 and days_since_last_outstanding > 60 then 'High Risk'
 187:             when outstanding_balance > total_expenses * 0.2 and days_since_last_outstanding > 45 then 'Medium Risk'
 188:             when outstanding_balance > 0 and days_since_last_outstanding > 30 then 'Low Risk'
 189:             else 'Minimal Risk'
 190:         end as risk_level,
 191: 
 192:         -- Credit limit advice
 193:         case
 194:             when total_credit_score >= 16 then total_expenses * 0.5
 195:             when total_credit_score >= 13 then total_expenses * 0.4
 196:             when total_credit_score >= 10 then total_expenses * 0.3
 197:             when total_credit_score >= 7 then total_expenses * 0.2
 198:             else total_expenses * 0.1
 199:         end as recommended_credit_limit,
 200: 
 201:         current_date as monitoring_date
 202: 
 203:     from vendor_credit_scoring
 204: )
 205: 
 206: select
 207:     vendor_id,
 208:     vendor_name,
 209:     vendor_email,
 210:     vendor_creation_date,
 211:     vendor_relationship_days,
 212:     relationship_duration_months,
 213:     subsidiary_id,
 214: 
 215:     -- financial indicators
 216:     total_payables,
 217:     total_payments,
 218:     total_expenses,
 219:     outstanding_balance,
 220:     payment_ratio,
 221:     avg_payment_delay_days,
 222: 
 223:     -- trading indicators
 224:     total_transactions,
 225:     payment_transactions,
 226:     outstanding_transactions,
 227:     first_transaction_date,
 228:     last_transaction_date,
 229:     last_payment_date,
 230:     last_outstanding_date,
 231:     days_since_last_outstanding,
 232: 
 233:     -- Ratings and ratings
 234:     payment_performance_score,
 235:     payment_timeliness_score,
 236:     relationship_stability_score,
 237:     transaction_frequency_score,
 238:     total_credit_score,
 239:     credit_rating,
 240:     risk_level,
 241: 
 242:     -- Status and recommendations
 243:     vendor_activity_status,
 244:     recommended_credit_limit,
 245: 
 246:     monitoring_date,
 247: 
 248:     md5(cast(vendor_id as varchar) || '_' || cast(subsidiary_id as varchar)) as supplier_monitoring_id
 249: 
 250: from final_supplier_monitoring
 251: where vendor_id is not null
 252:     and total_expenses > 0
```

## 3. agent看到的材料与不确定性

已检视该题全部67个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。


四档：**没有迹象**。

| 并列项 | 四档 |
|---|---|
| payment_zero | 没有迹象 |
| vendor_activity | 没有迹象 |

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

## 4. 核实查询与诊断

核实查询共**2条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__transaction_details' source_table,count(*) rows FROM intermediate.int_netsuite2__transaction_details UNION ALL SELECT 'staging.stg_netsuite2__transaction_lines' source_table,count(*) rows FROM staging.stg_netsuite2__transaction_lines
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ....int_netsuite2__transaction_details' source_table,count(*) rows FROM intermediate.int_netsuite2__transaction_details...\n                                                                      ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__transaction_details' source_table,count(*) source_rows FROM intermediate.int_netsuite2__transaction_details UNION ALL SELECT 'staging.stg_netsuite2__transaction_lines' source_table,count(*) source_rows FROM staging.stg_netsuite2__transaction_lines
```

```json
{"columns": ["source_table", "source_rows"], "result": [["intermediate.int_netsuite2__transaction_details", 700], ["staging.stg_netsuite2__transaction_lines", 700]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 2}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["supplier_monitoring_id"]`；比较列：`["vendor_id", "vendor_name", "vendor_email", "vendor_creation_date", "vendor_relationship_days", "relationship_duration_months", "subsidiary_id", "total_payables", "total_payments", "total_expenses", "outstanding_balance", "payment_ratio", "avg_payment_delay_days", "total_transactions", "payment_transactions", "outstanding_transactions", "days_since_last_outstanding", "payment_performance_score", "payment_timeliness_score", "relationship_stability_score", "transaction_frequency_score", "total_credit_score", "credit_rating", "risk_level", "vendor_activity_status", "recommended_credit_limit", "supplier_monitoring_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 104/104 | 0/0 | 0/0 | 104 | 104 | 208 | False |
| L1 | 104/104 | 0/0 | 0/0 | 104 | 104 | 208 | False |
| L2 | 104/104 | 0/0 | 0/0 | 104 | 104 | 208 | False |
| L3 | 104/104 | 0/0 | 0/0 | 104 | 104 | 208 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| supplier_monitoring_id | 0 | 0 | 0 | 0 |
| vendor_id | 0 | 0 | 0 | 0 |
| vendor_name | 0 | 0 | 0 | 0 |
| vendor_email | 0 | 0 | 0 | 0 |
| vendor_creation_date | 0 | 0 | 0 | 0 |
| vendor_relationship_days | 0 | 0 | 0 | 0 |
| relationship_duration_months | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| total_payables | 0 | 0 | 0 | 0 |
| total_payments | 0 | 0 | 0 | 0 |
| total_expenses | 0 | 0 | 0 | 0 |
| outstanding_balance | 0 | 0 | 0 | 0 |
| payment_ratio | 104 | 104 | 104 | 104 |
| avg_payment_delay_days | 0 | 0 | 0 | 0 |
| total_transactions | 0 | 0 | 0 | 0 |
| payment_transactions | 0 | 0 | 0 | 0 |
| outstanding_transactions | 0 | 0 | 0 | 0 |
| days_since_last_outstanding | 0 | 0 | 0 | 0 |
| payment_performance_score | 0 | 0 | 0 | 0 |
| payment_timeliness_score | 0 | 0 | 0 | 0 |
| relationship_stability_score | 0 | 0 | 0 | 0 |
| transaction_frequency_score | 0 | 0 | 0 | 0 |
| total_credit_score | 0 | 0 | 0 | 0 |
| credit_rating | 0 | 0 | 0 | 0 |
| risk_level | 0 | 0 | 0 | 0 |
| vendor_activity_status | 104 | 104 | 104 | 104 |
| recommended_credit_limit | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_int_netsuite2__supplier_credit_monitoring/baseline.sql`；SHA-256：`110fc9ddc33b2198d79f166e38dcc399140bafae5a26393168023ea83b7adb41`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 104/104 | 0/0 | 0/0 | 104 | 104 | 208 | False |
| L1 | 104/104 | 0/0 | 0/0 | 104 | 104 | 208 | False |
| L2 | 104/104 | 0/0 | 0/0 | 104 | 104 | 208 | False |
| L3 | 104/104 | 0/0 | 0/0 | 104 | 104 | 208 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| supplier_monitoring_id | 0 | 0 | 0 | 0 |
| vendor_id | 0 | 0 | 0 | 0 |
| vendor_name | 0 | 0 | 0 | 0 |
| vendor_email | 0 | 0 | 0 | 0 |
| vendor_creation_date | 0 | 0 | 0 | 0 |
| vendor_relationship_days | 0 | 0 | 0 | 0 |
| relationship_duration_months | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| total_payables | 0 | 0 | 0 | 0 |
| total_payments | 0 | 0 | 0 | 0 |
| total_expenses | 0 | 0 | 0 | 0 |
| outstanding_balance | 0 | 0 | 0 | 0 |
| payment_ratio | 104 | 104 | 104 | 104 |
| avg_payment_delay_days | 0 | 0 | 0 | 0 |
| total_transactions | 0 | 0 | 0 | 0 |
| payment_transactions | 0 | 0 | 0 | 0 |
| outstanding_transactions | 0 | 0 | 0 | 0 |
| days_since_last_outstanding | 0 | 0 | 0 | 0 |
| payment_performance_score | 0 | 0 | 0 | 0 |
| payment_timeliness_score | 0 | 0 | 0 | 0 |
| relationship_stability_score | 0 | 0 | 0 | 0 |
| transaction_frequency_score | 0 | 0 | 0 | 0 |
| total_credit_score | 0 | 0 | 0 | 0 |
| credit_rating | 0 | 0 | 0 | 0 |
| risk_level | 0 | 0 | 0 | 0 |
| vendor_activity_status | 104 | 104 | 104 | 104 |
| recommended_credit_limit | 0 | 0 | 0 | 0 |

### payment_zero

SQL：`data/022_work/impl-013_int_netsuite2__supplier_credit_monitoring/payment_zero.sql`；SHA-256：`f9947f643daac91fa708f7ef34e3dc16d2e74fbbbeb11c8ea7cae8e7783cc234`。

替换offset=773，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Bank'),0)/nullif(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctPay','Accounts Payable')),0)
-- 新
coalesce(coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Bank'),0)/nullif(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctPay','Accounts Payable')),0),0)
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 104/104 | 0/0 | 0/0 | 104 | 104 | 104 | False |
| L1 | 104/104 | 0/0 | 0/0 | 104 | 104 | 104 | False |
| L2 | 104/104 | 0/0 | 0/0 | 104 | 104 | 104 | False |
| L3 | 104/104 | 0/0 | 0/0 | 104 | 104 | 104 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| supplier_monitoring_id | 0 | 0 | 0 | 0 |
| vendor_id | 0 | 0 | 0 | 0 |
| vendor_name | 0 | 0 | 0 | 0 |
| vendor_email | 0 | 0 | 0 | 0 |
| vendor_creation_date | 0 | 0 | 0 | 0 |
| vendor_relationship_days | 0 | 0 | 0 | 0 |
| relationship_duration_months | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| total_payables | 0 | 0 | 0 | 0 |
| total_payments | 0 | 0 | 0 | 0 |
| total_expenses | 0 | 0 | 0 | 0 |
| outstanding_balance | 0 | 0 | 0 | 0 |
| payment_ratio | 0 | 0 | 0 | 0 |
| avg_payment_delay_days | 0 | 0 | 0 | 0 |
| total_transactions | 0 | 0 | 0 | 0 |
| payment_transactions | 0 | 0 | 0 | 0 |
| outstanding_transactions | 0 | 0 | 0 | 0 |
| days_since_last_outstanding | 0 | 0 | 0 | 0 |
| payment_performance_score | 0 | 0 | 0 | 0 |
| payment_timeliness_score | 0 | 0 | 0 | 0 |
| relationship_stability_score | 0 | 0 | 0 | 0 |
| transaction_frequency_score | 0 | 0 | 0 | 0 |
| total_credit_score | 0 | 0 | 0 | 0 |
| credit_rating | 0 | 0 | 0 | 0 |
| risk_level | 0 | 0 | 0 | 0 |
| vendor_activity_status | 104 | 104 | 104 | 104 |
| recommended_credit_limit | 0 | 0 | 0 | 0 |

### vendor_activity

SQL：`data/022_work/impl-013_int_netsuite2__supplier_credit_monitoring/vendor_activity.sql`；SHA-256：`d369defe8143234723d1c61b2eb7438f411f6c50e3b88d15ffc4b9ae604c5a41`。

替换offset=1819，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
'Inactive' vendor_activity_status
-- 新
CASE WHEN date_diff('day',last_transaction_date,DATE '2025-10-14')<=30 THEN 'Active' WHEN date_diff('day',last_transaction_date,DATE '2025-10-14')<=90 THEN 'Recent' WHEN date_diff('day',last_transaction_date,DATE '2025-10-14')<=180 THEN 'Dormant' ELSE 'Inactive' END vendor_activity_status
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 104/104 | 0/0 | 0/0 | 104 | 104 | 104 | False |
| L1 | 104/104 | 0/0 | 0/0 | 104 | 104 | 104 | False |
| L2 | 104/104 | 0/0 | 0/0 | 104 | 104 | 104 | False |
| L3 | 104/104 | 0/0 | 0/0 | 104 | 104 | 104 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| supplier_monitoring_id | 0 | 0 | 0 | 0 |
| vendor_id | 0 | 0 | 0 | 0 |
| vendor_name | 0 | 0 | 0 | 0 |
| vendor_email | 0 | 0 | 0 | 0 |
| vendor_creation_date | 0 | 0 | 0 | 0 |
| vendor_relationship_days | 0 | 0 | 0 | 0 |
| relationship_duration_months | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| total_payables | 0 | 0 | 0 | 0 |
| total_payments | 0 | 0 | 0 | 0 |
| total_expenses | 0 | 0 | 0 | 0 |
| outstanding_balance | 0 | 0 | 0 | 0 |
| payment_ratio | 104 | 104 | 104 | 104 |
| avg_payment_delay_days | 0 | 0 | 0 | 0 |
| total_transactions | 0 | 0 | 0 | 0 |
| payment_transactions | 0 | 0 | 0 | 0 |
| outstanding_transactions | 0 | 0 | 0 | 0 |
| days_since_last_outstanding | 0 | 0 | 0 | 0 |
| payment_performance_score | 0 | 0 | 0 | 0 |
| payment_timeliness_score | 0 | 0 | 0 | 0 |
| relationship_stability_score | 0 | 0 | 0 | 0 |
| transaction_frequency_score | 0 | 0 | 0 | 0 |
| total_credit_score | 0 | 0 | 0 | 0 |
| credit_rating | 0 | 0 | 0 | 0 |
| risk_level | 0 | 0 | 0 | 0 |
| vendor_activity_status | 0 | 0 | 0 | 0 |
| recommended_credit_limit | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：payment_zero,vendor_activity；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- payment_zero：C；主项。契约分母无应付时payment_ratio=0，agent返回NULL。（行减少0，格减少104）
- vendor_activity：D；主项。agent用Inactive常数替代契约活动分档。（行减少0，格减少104）

## 规则问题

无。按v2冻结定义执行。
