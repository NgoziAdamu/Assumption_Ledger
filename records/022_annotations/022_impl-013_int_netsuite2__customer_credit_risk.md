# impl-013 / int_netsuite2__customer_credit_risk（全量；v2）

## 1. 差异与结论

按无匹配类别SUM FILTER得到NULL；契约SUM CASE ELSE 0。三列各115格，单改均不减少行数但各减少115格，三项同为C。

主要原因：**C**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| zero_total_receivables | C | 0 | 115 |
| zero_total_collections | C | 0 | 115 |
| zero_outstanding_receivables | C | 0 | 115 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_int_netsuite2__customer_credit_risk.md](../../records/022_packages/022_impl-013_int_netsuite2__customer_credit_risk.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_int_netsuite2__customer_credit_risk/022_impl-013_int_netsuite2__customer_credit_risk.json`。
- 比较结果：[022_reruns_impl-013_int_netsuite2__customer_credit_risk.json](../022_reruns_impl-013_int_netsuite2__customer_credit_risk.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第1868–2042行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_credit_risk.sql`；原件第1–1行。

```sql
   1: SELECT md5(l.entity_id||'_'||t.subsidiary_id) customer_risk_id,l.entity_id customer_id,'Customer_'||left(l.entity_id,8) customer_name,'customer_'||left(l.entity_id,8)||'@client.com' customer_email,(current_date-365)::TIMESTAMP customer_creation_date,365::INTEGER customer_relationship_days,t.subsidiary_id,sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')) total_receivables,sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Bank') total_collections,sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Income') total_revenue,sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')) outstanding_receivables,count(DISTINCT t.transaction_id) total_transactions,count(*) FILTER(WHERE t.account_type_name='Bank') payment_transactions,count(*) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')) outstanding_transactions,min(t.accounting_period_ending) first_transaction_date,max(t.accounting_period_ending) last_transaction_date,max(t.accounting_period_ending) FILTER(WHERE t.account_type_name='Bank') last_payment_date,max(t.accounting_period_ending) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')) last_outstanding_date FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuite2__transaction_lines l USING(transaction_line_id) WHERE l.entity_id IS NOT NULL AND t.account_type_name IN ('Accounts Receivable','AcctRec','Income','Bank') GROUP BY l.entity_id,t.subsidiary_id HAVING sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Income')>0
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_credit_risk.sql`；原件第1–285行。

```sql
   1: -- Customer Credit Risk Analysis
   2: -- Customer credit risk analysis, including accounts receivable analysis, credit assessment, etc.
   3: with customer_receivables as (
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
  18:         'customer_' || substring(tl.entity_id, 1, 8) || '@client.com' as customer_email,
  19:         current_date - interval '365 days' as customer_creation_date,
  20: 
  21:         -- Calculate customer relationship age
  22:         365 as customer_relationship_days,
  23: 
  24:         -- Transaction Classification
  25:         case
  26:             when t.account_type_name in ('Accounts Receivable', 'AcctRec') then 'Receivable'
  27:             when t.account_type_name = 'Income' then 'Revenue'
  28:             when t.account_type_name = 'Bank' then 'Payment'
  29:             else 'Other'
  30:         end as transaction_category,
  31: 
  32:         -- Payment status simulation
  33:         case
  34:             when t.account_type_name = 'Bank' then 'Collected'
  35:             when t.account_type_name in ('Accounts Receivable', 'AcctRec') then 'Outstanding'
  36:             when t.account_type_name = 'Income' then 'Billed'
  37:             else 'Other'
  38:         end as collection_status
  39: 
  40:     from intermediate.int_netsuite2__transaction_details t
  41:     join staging.stg_netsuite2__transaction_lines tl
  42:         on t.transaction_line_id = tl.transaction_line_id
  43:     where tl.entity_id is not null
  44:         and t.account_type_name in ('Accounts Receivable', 'AcctRec', 'Income', 'Bank')
  45: ),
  46: 
  47: customer_payment_behavior as (
  48:     select
  49:         customer_id,
  50:         customer_name,
  51:         customer_email,
  52:         customer_creation_date,
  53:         customer_relationship_days,
  54:         subsidiary_id,
  55: 
  56:         -- Accounts Receivable Metrics
  57:         sum(case when transaction_category = 'Receivable' then abs(converted_amount) else 0 end) as total_receivables,
  58:         sum(case when transaction_category = 'Payment' then abs(converted_amount) else 0 end) as total_collections,
  59:         sum(case when transaction_category = 'Revenue' then abs(converted_amount) else 0 end) as total_revenue,
  60: 
  61:         -- uncollected balance
  62:         sum(case when collection_status = 'Outstanding' then abs(converted_amount) else 0 end) as outstanding_receivables,
  63: 
  64:         -- Transaction statistics
  65:         count(distinct transaction_id) as total_transactions,
  66:         count(case when transaction_category = 'Payment' then transaction_id end) as payment_transactions,
  67:         count(case when collection_status = 'Outstanding' then transaction_id end) as outstanding_transactions,
  68: 
  69:         -- time analysis
  70:         min(accounting_period_ending) as first_transaction_date,
  71:         max(accounting_period_ending) as last_transaction_date,
  72:         max(case when collection_status = 'Outstanding' then accounting_period_ending end) as last_outstanding_date,
  73:         max(case when transaction_category = 'Payment' then accounting_period_ending end) as last_payment_date
  74: 
  75:     from customer_receivables
  76:     group by customer_id, customer_name, customer_email, customer_creation_date, customer_relationship_days, subsidiary_id
  77: ),
  78: 
  79: customer_risk_metrics as (
  80:     select
  81:         *,
  82: 
  83:         -- collection ratio
  84:         case
  85:             when total_receivables > 0
  86:             then total_collections / total_receivables
  87:             else 0
  88:         end as collection_ratio,
  89: 
  90:         -- Average collection delay days (simulation)
  91:         case
  92:             when payment_transactions > 0
  93:             then 30 + (hash(customer_id) % 60)  -- Simulate a 30-90 day collection delay
  94:             else null
  95:         end as avg_collection_delay_days,
  96: 
  97:         -- Relationship duration (months)
  98:         case
  99:             when first_transaction_date is not null and last_transaction_date is not null
 100:             then datediff('month', first_transaction_date, last_transaction_date) + 1
 101:             else 1
 102:         end as relationship_duration_months,
 103: 
 104:         -- Activity analysis
 105:         case
 106:             when last_transaction_date is not null and datediff('day', last_transaction_date, current_date) <= 30 then 'Active'
 107:             when last_transaction_date is not null and datediff('day', last_transaction_date, current_date) <= 90 then 'Recent'
 108:             when last_transaction_date is not null and datediff('day', last_transaction_date, current_date) <= 180 then 'Dormant'
 109:             else 'Inactive'
 110:         end as customer_activity_status,
 111: 
 112:         -- Accounts receivable age analysis
 113:         case
 114:             when last_outstanding_date is not null then datediff('day', last_outstanding_date, current_date)
 115:             else 0
 116:         end as days_since_last_outstanding,
 117: 
 118:         -- Accounts Receivable to Revenue Ratio
 119:         case
 120:             when total_revenue > 0
 121:             then outstanding_receivables / total_revenue
 122:             else 0
 123:         end as receivables_to_revenue_ratio
 124: 
 125:     from customer_payment_behavior
 126: ),
 127: 
 128: customer_credit_scoring as (
 129:     select
 130:         *,
 131: 
 132:         -- Payment performance score
 133:         case
 134:             when collection_ratio >= 0.95 then 5
 135:             when collection_ratio >= 0.85 then 4
 136:             when collection_ratio >= 0.75 then 3
 137:             when collection_ratio >= 0.60 then 2
 138:             else 1
 139:         end as payment_performance_score,
 140: 
 141:         -- Payment promptness score
 142:         case
 143:             when avg_collection_delay_days <= 35 then 5
 144:             when avg_collection_delay_days <= 45 then 4
 145:             when avg_collection_delay_days <= 60 then 3
 146:             when avg_collection_delay_days <= 75 then 2
 147:             else 1
 148:         end as payment_timeliness_score,
 149: 
 150:         -- relationship stability score
 151:         case
 152:             when relationship_duration_months >= 24 then 5
 153:             when relationship_duration_months >= 12 then 4
 154:             when relationship_duration_months >= 6 then 3
 155:             when relationship_duration_months >= 3 then 2
 156:             else 1
 157:         end as relationship_stability_score,
 158: 
 159:         -- Volume Score
 160:         case
 161:             when total_revenue >= 100000 then 5
 162:             when total_revenue >= 50000 then 4
 163:             when total_revenue >= 25000 then 3
 164:             when total_revenue >= 10000 then 2
 165:             else 1
 166:         end as revenue_volume_score,
 167: 
 168:         -- Accounts Receivable Control Score
 169:         case
 170:             when receivables_to_revenue_ratio <= 0.1 then 5
 171:             when receivables_to_revenue_ratio <= 0.2 then 4
 172:             when receivables_to_revenue_ratio <= 0.3 then 3
 173:             when receivables_to_revenue_ratio <= 0.4 then 2
 174:             else 1
 175:         end as receivables_control_score
 176: 
 177:     from customer_risk_metrics
 178: ),
 179: 
 180: final_customer_risk as (
 181:     select
 182:         *,
 183: 
 184:         -- Comprehensive credit score
 185:         (payment_performance_score + payment_timeliness_score +
 186:          relationship_stability_score + revenue_volume_score +
 187:          receivables_control_score) as total_credit_score,
 188: 
 189:         -- credit rating
 190:         case
 191:             when (payment_performance_score + payment_timeliness_score +
 192:                   relationship_stability_score + revenue_volume_score +
 193:                   receivables_control_score) >= 20 then 'AAA'
 194:             when (payment_performance_score + payment_timeliness_score +
 195:                   relationship_stability_score + revenue_volume_score +
 196:                   receivables_control_score) >= 16 then 'AA'
 197:             when (payment_performance_score + payment_timeliness_score +
 198:                   relationship_stability_score + revenue_volume_score +
 199:                   receivables_control_score) >= 12 then 'A'
 200:             when (payment_performance_score + payment_timeliness_score +
 201:                   relationship_stability_score + revenue_volume_score +
 202:                   receivables_control_score) >= 8 then 'BBB'
 203:             else 'BB'
 204:         end as credit_rating,
 205: 
 206:         -- risk level
 207:         case
 208:             when outstanding_receivables > total_revenue * 0.4 and days_since_last_outstanding > 90 then 'High Risk'
 209:             when outstanding_receivables > total_revenue * 0.3 and days_since_last_outstanding > 60 then 'Medium Risk'
 210:             when outstanding_receivables > total_revenue * 0.2 and days_since_last_outstanding > 45 then 'Low Risk'
 211:             else 'Minimal Risk'
 212:         end as risk_level,
 213: 
 214:         -- Credit limit advice
 215:         case
 216:             when total_credit_score >= 20 then total_revenue * 0.5
 217:             when total_credit_score >= 16 then total_revenue * 0.4
 218:             when total_credit_score >= 12 then total_revenue * 0.3
 219:             when total_credit_score >= 8 then total_revenue * 0.2
 220:             else total_revenue * 0.1
 221:         end as recommended_credit_limit,
 222: 
 223:         -- Prediction of payment difficulty
 224:         case
 225:             when days_since_last_outstanding > 90 and collection_ratio < 0.7 then 'Very Difficult'
 226:             when days_since_last_outstanding > 60 and collection_ratio < 0.8 then 'Difficult'
 227:             when days_since_last_outstanding > 30 and collection_ratio < 0.9 then 'Moderate'
 228:             else 'Easy'
 229:         end as collection_difficulty,
 230: 
 231:         current_date as risk_assessment_date
 232: 
 233:     from customer_credit_scoring
 234: )
 235: 
 236: select
 237:     customer_id,
 238:     customer_name,
 239:     customer_email,
 240:     customer_creation_date,
 241:     customer_relationship_days,
 242:     relationship_duration_months,
 243:     subsidiary_id,
 244: 
 245:     -- financial indicators
 246:     total_receivables,
 247:     total_collections,
 248:     total_revenue,
 249:     outstanding_receivables,
 250:     collection_ratio,
 251:     receivables_to_revenue_ratio,
 252:     avg_collection_delay_days,
 253: 
 254:     -- trading indicators
 255:     total_transactions,
 256:     payment_transactions,
 257:     outstanding_transactions,
 258:     first_transaction_date,
 259:     last_transaction_date,
 260:     last_payment_date,
 261:     last_outstanding_date,
 262:     days_since_last_outstanding,
 263: 
 264:     -- Ratings and ratings
 265:     payment_performance_score,
 266:     payment_timeliness_score,
 267:     relationship_stability_score,
 268:     revenue_volume_score,
 269:     receivables_control_score,
 270:     total_credit_score,
 271:     credit_rating,
 272:     risk_level,
 273: 
 274:     -- Status and recommendations
 275:     customer_activity_status,
 276:     recommended_credit_limit,
 277:     collection_difficulty,
 278: 
 279:     risk_assessment_date,
 280: 
 281:     md5(cast(customer_id as varchar) || '_' || cast(subsidiary_id as varchar)) as customer_risk_id
 282: 
 283: from final_customer_risk
 284: where customer_id is not null
 285:     and total_revenue > 0
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

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 1}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["customer_risk_id"]`；比较列：`["customer_id", "customer_name", "customer_email", "customer_creation_date", "customer_relationship_days", "subsidiary_id", "total_receivables", "total_collections", "total_revenue", "outstanding_receivables", "total_transactions", "payment_transactions", "outstanding_transactions", "customer_risk_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/115 | 0/0 | 0/0 | 115 | 115 | 345 | False |
| L1 | 115/115 | 0/0 | 0/0 | 115 | 115 | 345 | False |
| L2 | 115/115 | 0/0 | 0/0 | 115 | 115 | 345 | False |
| L3 | 115/115 | 0/0 | 0/0 | 115 | 115 | 345 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_risk_id | 0 | 0 | 0 | 0 |
| customer_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| customer_creation_date | 0 | 0 | 0 | 0 |
| customer_relationship_days | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| total_receivables | 115 | 115 | 115 | 115 |
| total_collections | 115 | 115 | 115 | 115 |
| total_revenue | 0 | 0 | 0 | 0 |
| outstanding_receivables | 115 | 115 | 115 | 115 |
| total_transactions | 0 | 0 | 0 | 0 |
| payment_transactions | 0 | 0 | 0 | 0 |
| outstanding_transactions | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_int_netsuite2__customer_credit_risk/baseline.sql`；SHA-256：`2fddf70d03beb30cfbfbc791dd8a25835aa17037c1122f901c7cdca3e59d5364`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/115 | 0/0 | 0/0 | 115 | 115 | 345 | False |
| L1 | 115/115 | 0/0 | 0/0 | 115 | 115 | 345 | False |
| L2 | 115/115 | 0/0 | 0/0 | 115 | 115 | 345 | False |
| L3 | 115/115 | 0/0 | 0/0 | 115 | 115 | 345 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_risk_id | 0 | 0 | 0 | 0 |
| customer_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| customer_creation_date | 0 | 0 | 0 | 0 |
| customer_relationship_days | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| total_receivables | 115 | 115 | 115 | 115 |
| total_collections | 115 | 115 | 115 | 115 |
| total_revenue | 0 | 0 | 0 | 0 |
| outstanding_receivables | 115 | 115 | 115 | 115 |
| total_transactions | 0 | 0 | 0 | 0 |
| payment_transactions | 0 | 0 | 0 | 0 |
| outstanding_transactions | 0 | 0 | 0 | 0 |

### zero_total_receivables

SQL：`data/022_work/impl-013_int_netsuite2__customer_credit_risk/zero_total_receivables.sql`；SHA-256：`91c26a66f521b46bca2bcd8f7e3ca8c89f4219cb40450e412ab8a64e2c42e643`。

替换offset=311，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')) total_receivables
-- 新
coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')),0) total_receivables
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |
| L1 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |
| L2 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |
| L3 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_risk_id | 0 | 0 | 0 | 0 |
| customer_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| customer_creation_date | 0 | 0 | 0 | 0 |
| customer_relationship_days | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| total_receivables | 0 | 0 | 0 | 0 |
| total_collections | 115 | 115 | 115 | 115 |
| total_revenue | 0 | 0 | 0 | 0 |
| outstanding_receivables | 115 | 115 | 115 | 115 |
| total_transactions | 0 | 0 | 0 | 0 |
| payment_transactions | 0 | 0 | 0 | 0 |
| outstanding_transactions | 0 | 0 | 0 | 0 |

### zero_total_collections

SQL：`data/022_work/impl-013_int_netsuite2__customer_credit_risk/zero_total_collections.sql`；SHA-256：`043d22c635412277b008be92be51ae84f4f8f81ac46153d9dd9481292e3794b1`。

替换offset=429，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Bank') total_collections
-- 新
coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Bank'),0) total_collections
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |
| L1 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |
| L2 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |
| L3 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_risk_id | 0 | 0 | 0 | 0 |
| customer_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| customer_creation_date | 0 | 0 | 0 | 0 |
| customer_relationship_days | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| total_receivables | 115 | 115 | 115 | 115 |
| total_collections | 0 | 0 | 0 | 0 |
| total_revenue | 0 | 0 | 0 | 0 |
| outstanding_receivables | 115 | 115 | 115 | 115 |
| total_transactions | 0 | 0 | 0 | 0 |
| payment_transactions | 0 | 0 | 0 | 0 |
| outstanding_transactions | 0 | 0 | 0 | 0 |

### zero_outstanding_receivables

SQL：`data/022_work/impl-013_int_netsuite2__customer_credit_risk/zero_outstanding_receivables.sql`；SHA-256：`67481fdee11a3d2b52d6c01f47315ec76d4f164291307f89f566e38f8e99ec43`。

替换offset=603，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')) outstanding_receivables
-- 新
coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')),0) outstanding_receivables
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |
| L1 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |
| L2 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |
| L3 | 115/115 | 0/0 | 0/0 | 115 | 115 | 230 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_risk_id | 0 | 0 | 0 | 0 |
| customer_id | 0 | 0 | 0 | 0 |
| customer_name | 0 | 0 | 0 | 0 |
| customer_email | 0 | 0 | 0 | 0 |
| customer_creation_date | 0 | 0 | 0 | 0 |
| customer_relationship_days | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| total_receivables | 115 | 115 | 115 | 115 |
| total_collections | 115 | 115 | 115 | 115 |
| total_revenue | 0 | 0 | 0 | 0 |
| outstanding_receivables | 0 | 0 | 0 | 0 |
| total_transactions | 0 | 0 | 0 | 0 |
| payment_transactions | 0 | 0 | 0 | 0 |
| outstanding_transactions | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

未达到/不适用；本表没有U归因。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- zero_total_receivables：C；主项。契约按类别SUM CASE ELSE 0；FILTER无匹配得到NULL。（行减少0，格减少115）
- zero_total_collections：C；主项。契约按类别SUM CASE ELSE 0；FILTER无匹配得到NULL。（行减少0，格减少115）
- zero_outstanding_receivables：C；主项。契约按类别SUM CASE ELSE 0；FILTER无匹配得到NULL。（行减少0，格减少115）

## 规则问题

无。按v2冻结定义执行。
