# impl-013 / netsuite2_transaction_details_original（全量；v2）

## 1. 差异与结论

最终SQL直接透传另一个transaction_details模型，省去契约的源表和INNER subsidiaries连接。未找到误认为源数据缺失的判断。仅补subsidiary INNER连接便从700行到gold空表，按D。

主要原因：**D**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| required_join | D | 700 | 12600 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_netsuite2_transaction_details_original.md](../../records/022_packages/022_impl-013_netsuite2_transaction_details_original.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_netsuite2_transaction_details_original/022_impl-013_netsuite2_transaction_details_original.json`。
- 比较结果：[022_reruns_impl-013_netsuite2_transaction_details_original.json](../022_reruns_impl-013_netsuite2_transaction_details_original.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第3219–3473行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_transaction_details_original.sql`；原件第1–1行。

```sql
   1: SELECT * FROM intermediate.int_netsuite2__transaction_details
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/marts/netsuite2_transaction_details_original.sql`；原件第1–279行。

```sql
   1: with transaction_lines as (
   2:     select *
   3:     from intermediate.int_netsuite2__transaction_lines
   4: ),
   5: 
   6: transactions_with_converted_amounts as (
   7:     select * 
   8:     from intermediate.int_netsuite2__tran_with_converted_amounts
   9: ),
  10: 
  11: accounts as (
  12:     select * 
  13:     from intermediate.int_netsuite2__accounts
  14: ),
  15: 
  16: accounting_periods as (
  17:     select * 
  18:     from intermediate.int_netsuite2__accounting_periods
  19: ),
  20: 
  21: subsidiaries as (
  22:     select * 
  23:     from staging.stg_netsuite2__subsidiaries
  24: ),
  25: 
  26: transactions as (
  27:     select * 
  28:     from staging.stg_netsuite2__transactions
  29: ),
  30: 
  31: customers as (
  32:     select * 
  33:     from intermediate.int_netsuite2__customers
  34: ),
  35: 
  36: items as (
  37:     select * 
  38:     from staging.stg_netsuite2__items
  39: ),
  40: 
  41: locations as (
  42:     select * 
  43:     from intermediate.int_netsuite2__locations
  44: ),
  45: 
  46: vendors as (
  47:     select * 
  48:     from staging.stg_netsuite2__vendors
  49: ),
  50: 
  51: vendor_categories as (
  52:     select * 
  53:     from staging.stg_netsuite2__vendor_categories
  54: ),
  55: 
  56: departments as (
  57:     select * 
  58:     from staging.stg_netsuite2__departments
  59: ),
  60: 
  61: currencies as (
  62:     select * 
  63:     from staging.stg_netsuite2__currencies
  64: ),
  65: 
  66: classes as (
  67:     select *
  68:     from staging.stg_netsuite2__classes
  69: ),
  70: 
  71: transaction_details as (
  72:   select
  73:     transaction_lines.transaction_line_id,
  74:     transaction_lines.memo as transaction_memo,
  75:     not transaction_lines.is_posting as is_transaction_non_posting,
  76:     transaction_lines.is_main_line,
  77:     transaction_lines.is_tax_line,
  78:     transaction_lines.is_closed,
  79:     transactions.transaction_id,
  80:     transactions.status as transaction_status,
  81:     transactions.transaction_date,
  82:     transactions.due_date_at as transaction_due_date,
  83:     transactions.transaction_type as transaction_type,
  84:     transactions.transaction_number,
  85:     coalesce(transaction_lines.entity_id, transactions.entity_id) as entity_id,
  86:     false as is_transaction_intercompany_adjustment,
  87:     transactions.is_reversal,
  88:     transactions.reversal_transaction_id,
  89:     transactions.reversal_date,
  90:     transactions.is_reversal_defer,
  91: 
  92:     accounting_periods.ending_at as accounting_period_ending,
  93:     accounting_periods.name as accounting_period_name,
  94:     accounting_periods.accounting_period_id as accounting_period_id,
  95:     accounting_periods.is_adjustment as is_accounting_period_adjustment,
  96:     accounting_periods.is_closed as is_accounting_period_closed,
  97:     accounts.name as account_name,
  98:     accounts.type_name as account_type_name,
  99:     accounts.account_id as account_id,
 100:     accounts.account_number,
 101: 
 102:     accounts.is_leftside as is_account_leftside,
 103:     lower(accounts.type_name) = 'acctpay' as is_accounts_payable,
 104:     lower(accounts.type_name) = 'acctrec' as is_accounts_receivable,
 105:     false as is_account_intercompany,
 106:     false as is_eliminate,
 107:     coalesce(parent_account.account_id, accounts.account_id) as parent_account_id,
 108:     coalesce(parent_account.name, accounts.name) as parent_account_name,
 109:     lower(accounts.type_name) in ('expense', 'othexpense', 'deferexpense') as is_expense_account,
 110:     lower(accounts.type_name) in ('income', 'othincome') as is_income_account,
 111:     case 
 112:       when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.customer_id
 113:       else customers__transaction_lines.customer_id
 114:         end as customer_id,
 115:     case 
 116:       when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.alt_name
 117:       else customers__transaction_lines.alt_name
 118:         end as customer_alt_name,
 119:     case 
 120:       when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.company_name
 121:       else customers__transaction_lines.company_name
 122:         end as company_name,
 123:     case 
 124:       when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.city
 125:       else customers__transaction_lines.city
 126:         end as customer_city,
 127:     case 
 128:       when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.state
 129:       else customers__transaction_lines.state
 130:         end as customer_state,
 131:     case 
 132:       when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.zipcode
 133:       else customers__transaction_lines.zipcode
 134:         end as customer_zipcode,
 135:     case 
 136:       when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.country
 137:       else customers__transaction_lines.country
 138:         end as customer_country,
 139:     case 
 140:       when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.date_first_order_at
 141:       else customers__transaction_lines.date_first_order_at
 142:         end as customer_date_first_order,
 143:     case 
 144:       when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.customer_external_id
 145:       else customers__transaction_lines.customer_external_id
 146:         end as customer_external_id,
 147:     classes.class_id,
 148:     classes.full_name as class_full_name,
 149:     transaction_lines.item_id,
 150:     items.name as item_name,
 151:     items.item_type as item_type_name,
 152:     items.description as sales_description,
 153:     locations.location_id,
 154:     locations.name as location_name,
 155:     locations.city as location_city,
 156:     locations.country as location_country,
 157: 
 158:     case 
 159:       when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendor_categories__transactions.vendor_category_id
 160:       else vendor_categories__transaction_lines.vendor_category_id
 161:         end as vendor_category_id,
 162:     case 
 163:       when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendor_categories__transactions.name
 164:       else vendor_categories__transaction_lines.name
 165:         end as vendor_category_name,
 166:     case 
 167:       when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendors__transactions.vendor_id
 168:       else vendors__transaction_lines.vendor_id
 169:         end as vendor_id,
 170:     case 
 171:       when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendors__transactions.alt_name
 172:       else vendors__transaction_lines.alt_name
 173:         end as vendor_alt_name,
 174:     case 
 175:       when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendors__transactions.company_name
 176:       else vendors__transaction_lines.company_name
 177:         end as vendor_name,
 178:     case 
 179:       when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendors__transactions.created_at
 180:       else vendors__transaction_lines.created_at
 181:         end as vendor_create_date,
 182:     currencies.currency_id,
 183:     currencies.name as currency_name,
 184:     currencies.symbol as currency_symbol,
 185:     transaction_lines.department_id,
 186:     transaction_lines.exchange_rate,
 187:     departments.full_name as department_full_name,
 188:     departments.name as department_name,
 189: 
 190:     subsidiaries.subsidiary_id,
 191:     subsidiaries.full_name as subsidiary_full_name,
 192:     subsidiaries.name as subsidiary_name,
 193:     subsidiaries_currencies.symbol as subsidiary_currency_symbol,
 194: 
 195:     case
 196:       when lower(accounts.type_name) in ('income', 'othincome') then -transactions_with_converted_amounts.converted_amount_using_transaction_accounting_period
 197:       else transactions_with_converted_amounts.converted_amount_using_transaction_accounting_period
 198:         end as converted_amount,
 199:     case
 200:       when lower(accounts.type_name) in ('income', 'othincome') then -transaction_lines.amount
 201:       else transaction_lines.amount
 202:         end as transaction_amount,
 203:     case
 204:       when lower(accounts.type_name) in ('income', 'othincome') then -transaction_lines.netamount
 205:       else transaction_lines.netamount
 206:         end as transaction_line_amount  
 207:   from transaction_lines
 208: 
 209:   join transactions
 210:     on transactions.transaction_id = transaction_lines.transaction_id
 211: 
 212:   left join transactions_with_converted_amounts
 213:     on transactions_with_converted_amounts.transaction_line_id = transaction_lines.transaction_line_id
 214:       and transactions_with_converted_amounts.transaction_id = transaction_lines.transaction_id
 215:       and transactions_with_converted_amounts.transaction_accounting_period_id = transactions_with_converted_amounts.reporting_accounting_period_id
 216: 
 217:   left join accounts 
 218:     on accounts.account_id = transaction_lines.account_id
 219: 
 220:   left join accounts as parent_account 
 221:     on parent_account.account_id = cast(accounts.parent_id as varchar)
 222: 
 223:   left join accounting_periods 
 224:     on accounting_periods.accounting_period_id = transactions.accounting_period_id
 225: 
 226:   left join customers customers__transactions
 227:     on customers__transactions.customer_id = transactions.entity_id
 228: 
 229:   left join customers customers__transaction_lines
 230:     on customers__transaction_lines.customer_id = transaction_lines.entity_id
 231: 
 232:   left join classes
 233:     on classes.class_id = transaction_lines.class_id
 234: 
 235:   left join items 
 236:     on items.item_id = transaction_lines.item_id
 237: 
 238:   left join locations 
 239:     on locations.location_id = transaction_lines.location_id
 240: 
 241:   left join vendors vendors__transactions
 242:     on vendors__transactions.vendor_id = transactions.entity_id
 243: 
 244:   left join vendors vendors__transaction_lines
 245:     on vendors__transaction_lines.vendor_id = transaction_lines.entity_id
 246: 
 247:   left join vendor_categories vendor_categories__transactions
 248:     on vendor_categories__transactions.vendor_category_id = vendors__transactions.vendor_category_id
 249: 
 250:   left join vendor_categories vendor_categories__transaction_lines
 251:     on vendor_categories__transaction_lines.vendor_category_id = vendors__transaction_lines.vendor_category_id
 252: 
 253:   left join currencies 
 254:     on currencies.currency_id = transactions.currency_id
 255: 
 256:   left join departments 
 257:     on departments.department_id = transaction_lines.department_id
 258: 
 259:   join subsidiaries 
 260:     on subsidiaries.subsidiary_id = transaction_lines.subsidiary_id
 261:  
 262:   left join currencies subsidiaries_currencies
 263:     on subsidiaries_currencies.currency_id = subsidiaries.currency_id
 264:   
 265:   -- Simplified WHERE clause for mock data compatibility
 266:   where 1=1 -- always true, removes fiscal_calendar_id restriction for mock data
 267:   -- Original condition: (accounting_periods.fiscal_calendar_id is null
 268:   --   or accounting_periods.fiscal_calendar_id  = (select fiscal_calendar_id from subsidiaries where parent_id is null))
 269: ),
 270: 
 271: surrogate_key as ( 
 272:     select 
 273:         *,
 274:         md5(cast(transaction_line_id as varchar) || '_' || cast(transaction_id as varchar)) as transaction_details_id
 275:     from transaction_details
 276: )
 277: 
 278: select *
 279: from surrogate_key
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
SELECT 'intermediate.int_netsuite2__transaction_details' source_table,count(*) rows FROM intermediate.int_netsuite2__transaction_details
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ....int_netsuite2__transaction_details' source_table,count(*) rows FROM intermediate.int_netsuite2__transaction_details\n                                                                      ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__transaction_details' source_table,count(*) source_rows FROM intermediate.int_netsuite2__transaction_details
```

```json
{"columns": ["source_table", "source_rows"], "result": [["intermediate.int_netsuite2__transaction_details", 700]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["transaction_details_id"]`；比较列：`["account_id", "account_name", "account_number", "account_type_name", "accounting_period_ending", "accounting_period_name", "converted_amount", "is_account_leftside", "is_accounting_period_adjustment", "is_accounting_period_closed", "subsidiary_full_name", "subsidiary_id", "subsidiary_name", "transaction_amount", "transaction_details_id", "transaction_id", "transaction_line_amount", "transaction_line_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 700/0 | 700/0 | 0/0 | 0 | 700 | 12600 | False |
| L1 | 700/0 | 700/0 | 0/0 | 0 | 700 | 12600 | False |
| L2 | 700/0 | 700/0 | 0/0 | 0 | 700 | 12600 | False |
| L3 | 700/0 | 700/0 | 0/0 | 0 | 700 | 12600 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| transaction_details_id | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| is_account_leftside | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_amount | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_netsuite2_transaction_details_original/baseline.sql`；SHA-256：`dc1c56c4b4df405f08bc91d3ff0ee30472c99857e1271ac0cab5172c49a81d68`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 700/0 | 700/0 | 0/0 | 0 | 700 | 12600 | False |
| L1 | 700/0 | 700/0 | 0/0 | 0 | 700 | 12600 | False |
| L2 | 700/0 | 700/0 | 0/0 | 0 | 700 | 12600 | False |
| L3 | 700/0 | 700/0 | 0/0 | 0 | 700 | 12600 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| transaction_details_id | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| is_account_leftside | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_amount | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### required_join

SQL：`data/022_work/impl-013_netsuite2_transaction_details_original/required_join.sql`；SHA-256：`eb1d79aec6ad88fad6123fa20737ef8035710c15fa715348bb191fad68dd02f4`。

替换offset=0，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
SELECT * FROM intermediate.int_netsuite2__transaction_details
-- 新
SELECT d.* FROM intermediate.int_netsuite2__transaction_details d JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=d.subsidiary_id
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 0/0 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 0/0 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 0/0 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 0/0 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| transaction_details_id | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| is_account_leftside | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_amount | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：required_join；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- required_join：D；主项。整张替换成另一表并省掉契约inner subsidiaries连接。仅补该连接，非全表gold替换。（行减少700，格减少12600）

## 规则问题

无。按v2冻结定义执行。
