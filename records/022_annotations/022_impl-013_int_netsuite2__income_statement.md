# impl-013 / int_netsuite2__income_statement（全量；v2）

## 1. 差异与结论

交易的subsidiary外键与left join后维表ID分别保留原值/NULL。契约未指明输出取哪一侧；维表缺失本身不能规定业务上应丢失还是保留外键，归A。

主要原因：**A**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| subsidiary_source | A | 219 | 219 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_int_netsuite2__income_statement.md](../../records/022_packages/022_impl-013_int_netsuite2__income_statement.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_int_netsuite2__income_statement/022_impl-013_int_netsuite2__income_statement.json`。
- 比较结果：[022_reruns_impl-013_int_netsuite2__income_statement.json](../022_reruns_impl-013_int_netsuite2__income_statement.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第1363–1458行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__income_statement.sql`；原件第1–1行。

```sql
   1: SELECT md5(t.transaction_line_id||'_'||t.transaction_id||'_'||p.accounting_period_id||'_'||a.name) AS income_statement_id, t.transaction_id, t.transaction_line_id, p.accounting_period_id, p.ending_at AS accounting_period_ending, p.name AS accounting_period_name, p.is_adjustment AS is_accounting_period_adjustment, p.is_closed AS is_accounting_period_closed, a.name AS account_name, a.type_name AS account_type_name, a.account_id, a.account_number, t.subsidiary_id, s.full_name AS subsidiary_full_name, s.name AS subsidiary_name, cur.symbol AS subsidiary_currency_symbol, CASE WHEN a.account_number IS NULL OR a.name IS NULL THEN NULL ELSE a.account_number||'-'||a.name END AS account_number_and_name, l.class_id, cl.full_name AS class_full_name, l.location_id, loc.full_name AS location_full_name, l.department_id, d.full_name AS department_full_name, t.account_category, CASE lower(a.type_name) WHEN 'income' THEN 1 WHEN 'cogs' THEN 2 WHEN 'expense' THEN 3 WHEN 'othincome' THEN 4 WHEN 'othexpense' THEN 5 END::INTEGER AS income_statement_sort_helper, -t.converted_amount_using_transaction_accounting_period AS converted_amount, -t.unconverted_amount AS transaction_amount FROM intermediate.int_netsuite2__tran_with_converted_amounts t JOIN intermediate.int_netsuite2__transaction_lines l ON l.transaction_id=t.transaction_id AND l.transaction_line_id=t.transaction_line_id LEFT JOIN intermediate.int_netsuite2__accounts a ON a.account_id=t.account_id JOIN intermediate.int_netsuite2__accounting_periods p ON p.accounting_period_id=t.reporting_accounting_period_id LEFT JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=t.subsidiary_id LEFT JOIN staging.stg_netsuite2__currencies cur ON cur.currency_id=s.currency_id LEFT JOIN staging.stg_netsuite2__classes cl ON cl.class_id=l.class_id LEFT JOIN staging.stg_netsuite2__locations loc ON loc.location_id=l.location_id LEFT JOIN staging.stg_netsuite2__departments d ON d.department_id=l.department_id WHERE t.is_income_statement AND t.transaction_accounting_period_id=t.reporting_accounting_period_id
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__income_statement.sql`；原件第1–132行。

```sql
   1: with transactions_with_converted_amounts as (
   2:     select * 
   3:     from intermediate.int_netsuite2__tran_with_converted_amounts
   4: ), 
   5: 
   6: accounts as (
   7:     select * 
   8:     from intermediate.int_netsuite2__accounts
   9: ), 
  10: 
  11: accounting_periods as (
  12:     select * 
  13:     from intermediate.int_netsuite2__accounting_periods
  14: ),
  15: 
  16: subsidiaries as (
  17:     select * 
  18:     from staging.stg_netsuite2__subsidiaries
  19: ),
  20: 
  21: currencies as (
  22:     select *
  23:     from staging.stg_netsuite2__currencies
  24: ),
  25: 
  26: transaction_lines as (
  27:     select * 
  28:     from intermediate.int_netsuite2__transaction_lines
  29: ),
  30: 
  31: classes as (
  32:     select * 
  33:     from staging.stg_netsuite2__classes
  34: ),
  35: 
  36: locations as (
  37:     select * 
  38:     from staging.stg_netsuite2__locations
  39: ),
  40: 
  41: departments as (
  42:     select * 
  43:     from staging.stg_netsuite2__departments
  44: ),
  45: 
  46: income_statement as (
  47:     select
  48:         transactions_with_converted_amounts.transaction_id,
  49:         transactions_with_converted_amounts.transaction_line_id,
  50: 
  51:         reporting_accounting_periods.accounting_period_id as accounting_period_id,
  52:         reporting_accounting_periods.ending_at as accounting_period_ending,
  53:         reporting_accounting_periods.name as accounting_period_name,
  54:         reporting_accounting_periods.is_adjustment as is_accounting_period_adjustment,
  55:         reporting_accounting_periods.is_closed as is_accounting_period_closed,
  56:         accounts.name as account_name,
  57:         accounts.type_name as account_type_name,
  58:         accounts.account_id as account_id,
  59:         accounts.account_number,
  60:         subsidiaries.subsidiary_id,
  61:         subsidiaries.full_name as subsidiary_full_name,
  62:         subsidiaries.name as subsidiary_name,
  63:         subsidiaries_currencies.symbol as subsidiary_currency_symbol,
  64: 
  65:         (accounts.account_number || '-' || accounts.name) as account_number_and_name,
  66:         classes.class_id,
  67:         classes.full_name as class_full_name,
  68: 
  69:         locations.location_id,
  70:         locations.full_name as location_full_name,
  71:         departments.department_id,
  72:         departments.full_name as department_full_name,
  73: 
  74:         transactions_with_converted_amounts.account_category as account_category,
  75:         case when lower(accounts.type_name) = 'income' then 1
  76:             when lower(accounts.type_name) = 'cogs' then 2
  77:             when lower(accounts.type_name) = 'expense' then 3
  78:             when lower(accounts.type_name) = 'othincome' then 4
  79:             when lower(accounts.type_name) = 'othexpense' then 5
  80:             else null
  81:             end as income_statement_sort_helper,
  82: 
  83:         -converted_amount_using_transaction_accounting_period as converted_amount,
  84:         -unconverted_amount as transaction_amount
  85:         
  86:     from transactions_with_converted_amounts
  87: 
  88:     join transaction_lines as transaction_lines
  89:         on transaction_lines.transaction_line_id = transactions_with_converted_amounts.transaction_line_id
  90:             and transaction_lines.transaction_id = transactions_with_converted_amounts.transaction_id
  91: 
  92:     left join departments 
  93:         on departments.department_id = transaction_lines.department_id
  94:     
  95:     left join accounts 
  96:         on accounts.account_id = transactions_with_converted_amounts.account_id
  97: 
  98:     left join locations
  99:         on locations.location_id = transaction_lines.location_id
 100: 
 101:     left join classes 
 102:         on classes.class_id = transaction_lines.class_id
 103: 
 104:     left join accounting_periods as reporting_accounting_periods 
 105:         on reporting_accounting_periods.accounting_period_id = transactions_with_converted_amounts.reporting_accounting_period_id
 106:     
 107:     left join subsidiaries
 108:         on transactions_with_converted_amounts.subsidiary_id = subsidiaries.subsidiary_id
 109: 
 110:     left join currencies subsidiaries_currencies
 111:         on subsidiaries_currencies.currency_id = subsidiaries.currency_id
 112: 
 113:     where 1=1 -- fiscal_calendar_id filter removed for mock data compatibility
 114:         -- and reporting_accounting_periods.fiscal_calendar_id = (select fiscal_calendar_id from subsidiaries where parent_id is null)
 115:         and transactions_with_converted_amounts.transaction_accounting_period_id = transactions_with_converted_amounts.reporting_accounting_period_id
 116:         and transactions_with_converted_amounts.is_income_statement
 117: ),
 118: 
 119: surrogate_key as ( 
 120:     select 
 121:         *,
 122:         md5(
 123:           cast(transaction_line_id as varchar) || '_' ||
 124:           cast(transaction_id as varchar) || '_' ||
 125:           cast(accounting_period_id as varchar) || '_' ||
 126:           cast(account_name as varchar)
 127:         ) as income_statement_id
 128:     from income_statement
 129: )
 130: 
 131: select *
 132: from surrogate_key
```

## 3. agent看到的材料与不确定性

已检视该题全部67个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。


四档：**没有迹象**。

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

## 4. 核实查询与诊断

核实查询共**3条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__accounting_periods' source_table,count(*) rows FROM intermediate.int_netsuite2__accounting_periods UNION ALL SELECT 'intermediate.int_netsuite2__accounts' source_table,count(*) rows FROM intermediate.int_netsuite2__accounts UNION ALL SELECT 'intermediate.int_netsuite2__tran_with_converted_amounts' source_table,count(*) rows FROM intermediate.int_netsuite2__tran_with_converted_amounts UNION ALL SELECT 'intermediate.int_netsuite2__transaction_lines' source_table,count(*) rows FROM intermediate.int_netsuite2__transaction_lines UNION ALL SELECT 'staging.stg_netsuite2__classes' source_table,count(*) rows FROM staging.stg_netsuite2__classes UNION ALL SELECT 'staging.stg_netsuite2__currencies' source_table,count(*) rows FROM staging.stg_netsuite2__currencies UNION ALL SELECT 'staging.stg_netsuite2__departments' source_table,count(*) rows FROM staging.stg_netsuite2__departments UNION ALL SELECT 'staging.stg_netsuite2__locations' source_table,count(*) rows FROM staging.stg_netsuite2__locations UNION ALL SELECT 'staging.stg_netsuite2__subsidiaries' source_table,count(*) rows FROM staging.stg_netsuite2__subsidiaries
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ....int_netsuite2__accounting_periods' source_table,count(*) rows FROM intermediate.int_netsuite2__accounting_periods...\n                                                                     ^"}
```

### 核实 V2：维表外键匹配

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE s.subsidiary_id IS NULL) unmatched FROM intermediate.int_netsuite2__tran_with_converted_amounts t LEFT JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=t.subsidiary_id WHERE t.is_income_statement
```

```json
{"columns": ["n", "unmatched"], "result": [[219, 219]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__accounting_periods' source_table,count(*) source_rows FROM intermediate.int_netsuite2__accounting_periods UNION ALL SELECT 'intermediate.int_netsuite2__accounts' source_table,count(*) source_rows FROM intermediate.int_netsuite2__accounts UNION ALL SELECT 'intermediate.int_netsuite2__tran_with_converted_amounts' source_table,count(*) source_rows FROM intermediate.int_netsuite2__tran_with_converted_amounts UNION ALL SELECT 'intermediate.int_netsuite2__transaction_lines' source_table,count(*) source_rows FROM intermediate.int_netsuite2__transaction_lines UNION ALL SELECT 'staging.stg_netsuite2__classes' source_table,count(*) source_rows FROM staging.stg_netsuite2__classes UNION ALL SELECT 'staging.stg_netsuite2__currencies' source_table,count(*) source_rows FROM staging.stg_netsuite2__currencies UNION ALL SELECT 'staging.stg_netsuite2__departments' source_table,count(*) source_rows FROM staging.stg_netsuite2__departments UNION ALL SELECT 'staging.stg_netsuite2__locations' source_table,count(*) source_rows FROM staging.stg_netsuite2__locations UNION ALL SELECT 'staging.stg_netsuite2__subsidiaries' source_table,count(*) source_rows FROM staging.stg_netsuite2__subsidiaries
```

```json
{"columns": ["source_table", "source_rows"], "result": [["intermediate.int_netsuite2__accounting_periods", 31], ["intermediate.int_netsuite2__accounts", 184], ["intermediate.int_netsuite2__tran_with_converted_amounts", 700], ["intermediate.int_netsuite2__transaction_lines", 700], ["staging.stg_netsuite2__classes", 0], ["staging.stg_netsuite2__currencies", 4], ["staging.stg_netsuite2__departments", 100], ["staging.stg_netsuite2__locations", 100], ["staging.stg_netsuite2__subsidiaries", 5]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["income_statement_id"]`；比较列：`["account_category", "account_id", "account_name", "account_number", "account_number_and_name", "account_type_name", "accounting_period_ending", "accounting_period_name", "class_full_name", "converted_amount", "department_full_name", "income_statement_id", "income_statement_sort_helper", "is_accounting_period_adjustment", "is_accounting_period_closed", "location_full_name", "subsidiary_currency_symbol", "subsidiary_full_name", "subsidiary_id", "subsidiary_name", "transaction_amount", "transaction_id", "transaction_line_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 219/219 | 0/0 | 0/0 | 219 | 219 | 219 | False |
| L1 | 219/219 | 0/0 | 0/0 | 219 | 219 | 219 | False |
| L2 | 219/219 | 0/0 | 0/0 | 219 | 219 | 219 | False |
| L3 | 219/219 | 0/0 | 0/0 | 219 | 219 | 219 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| income_statement_id | 0 | 0 | 0 | 0 |
| account_category | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_number_and_name | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| class_full_name | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| department_full_name | 0 | 0 | 0 | 0 |
| income_statement_sort_helper | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| location_full_name | 0 | 0 | 0 | 0 |
| subsidiary_currency_symbol | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 219 | 219 | 219 | 219 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_int_netsuite2__income_statement/baseline.sql`；SHA-256：`b269ae81d42a277684455b6d0eb212069991f0bde05f2c896629f4da59a315aa`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 219/219 | 0/0 | 0/0 | 219 | 219 | 219 | False |
| L1 | 219/219 | 0/0 | 0/0 | 219 | 219 | 219 | False |
| L2 | 219/219 | 0/0 | 0/0 | 219 | 219 | 219 | False |
| L3 | 219/219 | 0/0 | 0/0 | 219 | 219 | 219 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| income_statement_id | 0 | 0 | 0 | 0 |
| account_category | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_number_and_name | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| class_full_name | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| department_full_name | 0 | 0 | 0 | 0 |
| income_statement_sort_helper | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| location_full_name | 0 | 0 | 0 | 0 |
| subsidiary_currency_symbol | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 219 | 219 | 219 | 219 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### subsidiary_source

SQL：`data/022_work/impl-013_int_netsuite2__income_statement/subsidiary_source.sql`；SHA-256：`f664676e567fbe1bf412a1cbef52744cc7056692840840b6b9c7264a14c1d40e`。

替换offset=431，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
a.account_number, t.subsidiary_id,
-- 新
a.account_number, s.subsidiary_id,
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 219/219 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 219/219 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 219/219 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 219/219 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| income_statement_id | 0 | 0 | 0 | 0 |
| account_category | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_number_and_name | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| class_full_name | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| department_full_name | 0 | 0 | 0 | 0 |
| income_statement_sort_helper | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| location_full_name | 0 | 0 | 0 | 0 |
| subsidiary_currency_symbol | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：subsidiary_source；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- subsidiary_source：A；主项。subsidiary_id契约只说明关联交易的subsidiary标识，未定驱动外键或维表匹配键；维表对应缺失，gold NULL、agent保留外键。（行减少219，格减少219）

## 规则问题

“associated with transaction”的ID可取驱动外键或joined维表键。A与C（将from joined tables理解为必须取维表）都可读；选A，未将维表匹配失败推断为U。
