# impl-013 / int_netsuite2__balance_sheet（全量；v2）

## 1. 差异与结论

NULL account_id在MD5中补空串或0的选择导致219行变成双侧独有键（438规模）；遗漏388条CTA为另一处C。主因为A，CTA为C参与因素；其他type/rate局部变动当前同口径规模未变。

主要原因：**A**；参与因素：C：cta_branch；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| key_null | A | 438 | 9636 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_int_netsuite2__balance_sheet.md](../../records/022_packages/022_impl-013_int_netsuite2__balance_sheet.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_int_netsuite2__balance_sheet/022_impl-013_int_netsuite2__balance_sheet.json`。
- 比较结果：[022_reruns_impl-013_int_netsuite2__balance_sheet.json](../022_reruns_impl-013_int_netsuite2__balance_sheet.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第1277–1362行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__balance_sheet.sql`；原件第1–1行。

```sql
   1: WITH base AS (SELECT t.*, a.name, a.type_name, a.account_number, a.is_balancesheet, a.is_leftside, a.general_rate_type, p.ending_at, p.name AS period_name, p.is_adjustment, p.is_closed, p.fiscal_year_trunc, tp.fiscal_year_trunc AS transaction_fiscal_year, tp.fiscal_calendar_id AS transaction_calendar, p.fiscal_calendar_id, s.full_name AS subsidiary_full_name, s.name AS subsidiary_name, cur.symbol AS subsidiary_currency_symbol FROM intermediate.int_netsuite2__tran_with_converted_amounts t LEFT JOIN intermediate.int_netsuite2__accounts a ON a.account_id=t.account_id LEFT JOIN intermediate.int_netsuite2__accounting_periods p ON p.accounting_period_id=t.reporting_accounting_period_id LEFT JOIN intermediate.int_netsuite2__accounting_periods tp ON tp.accounting_period_id=t.transaction_accounting_period_id LEFT JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=t.subsidiary_id LEFT JOIN staging.stg_netsuite2__currencies cur ON cur.currency_id=s.currency_id WHERE a.is_balancesheet OR t.is_income_statement), presented AS (SELECT *, CASE WHEN NOT is_balancesheet AND fiscal_year_trunc=transaction_fiscal_year AND fiscal_calendar_id=transaction_calendar THEN 'Net Income' WHEN NOT is_balancesheet THEN 'Retained Earnings' ELSE name END AS out_name, CASE WHEN NOT is_balancesheet AND fiscal_year_trunc=transaction_fiscal_year AND fiscal_calendar_id=transaction_calendar THEN 'Net Income' WHEN NOT is_balancesheet THEN 'Retained Earnings' ELSE type_name END AS out_type FROM base) SELECT md5(transaction_line_id||'_'||transaction_id||'_'||reporting_accounting_period_id||'_'||out_name||'_'||coalesce(CASE WHEN is_balancesheet THEN account_id END,'')) AS balance_sheet_id, transaction_id, transaction_line_id, subsidiary_id, subsidiary_full_name, subsidiary_name, subsidiary_currency_symbol, reporting_accounting_period_id AS accounting_period_id, ending_at AS accounting_period_ending, period_name AS accounting_period_name, is_adjustment AS is_accounting_period_adjustment, is_closed AS is_accounting_period_closed, account_category, out_name AS account_name, out_name AS account_display_name, out_type AS account_type_name, lower(replace(out_type,' ', '_')) AS account_type_id, CASE WHEN is_balancesheet THEN account_id END AS account_id, CASE WHEN is_balancesheet THEN account_number END AS account_number, FALSE AS is_account_intercompany, CASE WHEN is_balancesheet THEN is_leftside ELSE FALSE END AS is_account_leftside, CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) ELSE coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) END AS converted_amount, CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -unconverted_amount ELSE unconverted_amount END AS transaction_amount, CASE lower(type_name) WHEN 'bank' THEN 1 WHEN 'acctrec' THEN 2 WHEN 'unbilledrec' THEN 3 WHEN 'othcurrasset' THEN 4 WHEN 'fixedasset' THEN 5 WHEN 'othasset' THEN 6 WHEN 'deferexpense' THEN 7 WHEN 'acctpay' THEN 8 WHEN 'credcard' THEN 9 WHEN 'othcurrliab' THEN 10 WHEN 'longtermliab' THEN 11 WHEN 'deferrevenue' THEN 12 WHEN 'equity' THEN 13 ELSE CASE WHEN out_name='Retained Earnings' THEN 14 WHEN out_name='Net Income' THEN 15 END END::INTEGER AS balance_sheet_sort_helper FROM presented
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__balance_sheet.sql`；原件第1–221行。

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
  26: balance_sheet as ( 
  27:     select
  28:         transactions_with_converted_amounts.transaction_id,
  29:         transactions_with_converted_amounts.transaction_line_id,
  30:         transactions_with_converted_amounts.subsidiary_id,
  31:         subsidiaries.full_name as subsidiary_full_name,
  32:         subsidiaries.name as subsidiary_name,
  33:         subsidiaries_currencies.symbol as subsidiary_currency_symbol,
  34: 
  35:         reporting_accounting_periods.accounting_period_id as accounting_period_id,
  36:         reporting_accounting_periods.ending_at as accounting_period_ending,
  37:         reporting_accounting_periods.name as accounting_period_name,
  38:         reporting_accounting_periods.is_adjustment as is_accounting_period_adjustment,
  39:         reporting_accounting_periods.is_closed as is_accounting_period_closed,
  40:         transactions_with_converted_amounts.account_category as account_category,
  41:         case
  42:         when (not accounts.is_balancesheet 
  43:                 and reporting_accounting_periods.fiscal_year_trunc = transaction_accounting_periods.fiscal_year_trunc 
  44:                 and reporting_accounting_periods.fiscal_calendar_id = transaction_accounting_periods.fiscal_calendar_id) then 'Net Income'
  45:         when not accounts.is_balancesheet then 'Retained Earnings'
  46:         else accounts.name
  47:             end as account_name,
  48:         case
  49:         when (not accounts.is_balancesheet 
  50:                 and reporting_accounting_periods.fiscal_year_trunc = transaction_accounting_periods.fiscal_year_trunc 
  51:                 and reporting_accounting_periods.fiscal_calendar_id = transaction_accounting_periods.fiscal_calendar_id) then 'Net Income'
  52:         when not accounts.is_balancesheet then 'Retained Earnings'
  53:         else accounts.name
  54:             end as account_display_name,
  55:         case
  56:         when (not accounts.is_balancesheet 
  57:                 and reporting_accounting_periods.fiscal_year_trunc = transaction_accounting_periods.fiscal_year_trunc 
  58:                 and reporting_accounting_periods.fiscal_calendar_id = transaction_accounting_periods.fiscal_calendar_id) then 'Net Income'
  59:         when not accounts.is_balancesheet then 'Retained Earnings'
  60:         when lower(accounts.type_name) = 'retearnings' then 'Retained Earnings'
  61:         when lower(accounts.type_name) in ('cta-e', 'cumultransadj') then 'Cumulative Translation Adjustment'
  62:         else accounts.type_name
  63:             end as account_type_name,
  64:         case
  65:         when (not accounts.is_balancesheet 
  66:                 and reporting_accounting_periods.fiscal_year_trunc = transaction_accounting_periods.fiscal_year_trunc 
  67:                 and reporting_accounting_periods.fiscal_calendar_id = transaction_accounting_periods.fiscal_calendar_id) then 'net_income'
  68:         when not accounts.is_balancesheet then 'retained_earnings'
  69:         when lower(accounts.type_name) = 'retearnings' then 'retained_earnings'
  70:         when lower(accounts.type_name) in ('cta-e', 'cumultransadj') then 'cumulative_translation_adjustment'
  71:         else accounts.type_name
  72:             end as account_type_id,
  73:         case
  74:         when not accounts.is_balancesheet then null
  75:         else accounts.account_id
  76:             end as account_id,
  77:         case
  78:         when not accounts.is_balancesheet then (select accounts.account_number from accounts where lower(accounts.type_name) = 'retearnings' limit 1)
  79:         else accounts.account_number
  80:             end as account_number,
  81:         case
  82:         when not accounts.is_balancesheet then false
  83:         else false
  84:             end as is_account_intercompany,
  85:         case
  86:         when not accounts.is_balancesheet then false
  87:         else accounts.is_leftside
  88:             end as is_account_leftside,
  89: 
  90:         case
  91:         when not accounts.is_balancesheet and lower(accounts.general_rate_type) in ('historical', 'average') then -converted_amount_using_transaction_accounting_period
  92:         when not accounts.is_balancesheet then -converted_amount_using_reporting_month
  93:         when accounts.is_balancesheet and not accounts.is_leftside and lower(accounts.general_rate_type) in ('historical', 'average') then -converted_amount_using_transaction_accounting_period
  94:         when accounts.is_balancesheet and accounts.is_leftside and lower(accounts.general_rate_type) in ('historical', 'average') then converted_amount_using_transaction_accounting_period
  95:         when accounts.is_balancesheet and not accounts.is_leftside then -converted_amount_using_reporting_month
  96:         when accounts.is_balancesheet and accounts.is_leftside then converted_amount_using_reporting_month
  97:         else 0
  98:             end as converted_amount,
  99: 
 100:         case
 101:         when not accounts.is_balancesheet then -unconverted_amount
 102:         when accounts.is_balancesheet and not accounts.is_leftside then -unconverted_amount
 103:         when accounts.is_balancesheet and accounts.is_leftside then unconverted_amount
 104:         else 0
 105:             end as transaction_amount,
 106: 
 107:         case
 108:         when lower(accounts.type_name) = 'bank' then 1
 109:         when lower(accounts.type_name) = 'acctrec' then 2
 110:         when lower(accounts.type_name) = 'unbilledrec' then 3
 111:         when lower(accounts.type_name) = 'othcurrasset' then 4
 112:         when lower(accounts.type_name) = 'fixedasset' then 5
 113:         when lower(accounts.type_name) = 'othasset' then 6
 114:         when lower(accounts.type_name) = 'deferexpense' then 7
 115:         when lower(accounts.type_name) = 'acctpay' then 8
 116:         when lower(accounts.type_name) = 'credcard' then 9
 117:         when lower(accounts.type_name) = 'othcurrliab' then 10
 118:         when lower(accounts.type_name) = 'longtermliab' then 11
 119:         when lower(accounts.type_name) = 'deferrevenue' then 12
 120:         when lower(accounts.type_name) = 'retearnings' then 14
 121:         when lower(accounts.type_name) in ('cta-e', 'cumultransadj') then 16
 122:         when lower(accounts.type_name) = 'equity' then 13
 123:         when (not accounts.is_balancesheet 
 124:                 and reporting_accounting_periods.fiscal_year_trunc = transaction_accounting_periods.fiscal_year_trunc
 125:                 and reporting_accounting_periods.fiscal_calendar_id = transaction_accounting_periods.fiscal_calendar_id) then 15
 126:         when not accounts.is_balancesheet then 14
 127:         else null
 128:             end as balance_sheet_sort_helper
 129: 
 130:     from transactions_with_converted_amounts
 131: 
 132:     left join accounts 
 133:         on accounts.account_id = transactions_with_converted_amounts.account_id
 134: 
 135:     left join accounting_periods as reporting_accounting_periods 
 136:         on reporting_accounting_periods.accounting_period_id = transactions_with_converted_amounts.reporting_accounting_period_id
 137: 
 138:     left join accounting_periods as transaction_accounting_periods 
 139:         on transaction_accounting_periods.accounting_period_id = transactions_with_converted_amounts.transaction_accounting_period_id
 140: 
 141:     left join subsidiaries
 142:         on subsidiaries.subsidiary_id = transactions_with_converted_amounts.subsidiary_id
 143: 
 144:     left join currencies subsidiaries_currencies
 145:         on subsidiaries_currencies.currency_id = subsidiaries.currency_id
 146: 
 147:     where 1=1 -- fiscal_calendar_id filters removed for mock data compatibility
 148:         -- and reporting_accounting_periods.fiscal_calendar_id = (select fiscal_calendar_id from subsidiaries where parent_id is null)
 149:         -- and transaction_accounting_periods.fiscal_calendar_id = (select fiscal_calendar_id from subsidiaries where parent_id is null)
 150:         and (accounts.is_balancesheet
 151:         or transactions_with_converted_amounts.is_income_statement)
 152: 
 153:     union all
 154: 
 155:     select
 156:         transactions_with_converted_amounts.transaction_id,
 157:         transactions_with_converted_amounts.transaction_line_id,
 158:         transactions_with_converted_amounts.subsidiary_id,
 159:         subsidiaries.full_name as subsidiary_full_name,
 160:         subsidiaries.name as subsidiary_name,
 161:         subsidiaries_currencies.symbol as subsidiary_currency_symbol,
 162:         
 163:         reporting_accounting_periods.accounting_period_id as accounting_period_id,
 164:         reporting_accounting_periods.ending_at as accounting_period_ending,
 165:         reporting_accounting_periods.name as accounting_period_name,
 166:         reporting_accounting_periods.is_adjustment as is_accounting_period_adjustment,
 167:         reporting_accounting_periods.is_closed as is_accounting_period_closed,
 168:         'Equity' as account_category,
 169:         'Cumulative Translation Adjustment' as account_name,
 170:         'Cumulative Translation Adjustment' as account_display_name,
 171:         'Cumulative Translation Adjustment' as account_type_name,
 172:         'cumulative_translation_adjustment' as account_type_id,
 173:         null as account_id,
 174:         (select accounts.account_number from accounts where lower(accounts.type_name) = 'cumultransadj' limit 1) as account_number,
 175:         false as is_account_intercompany,
 176:         false as is_account_leftside,
 177: 
 178:         case
 179:         when lower(accounts.general_rate_type) in ('historical', 'average') then converted_amount_using_transaction_accounting_period
 180:         else converted_amount_using_reporting_month
 181:             end as converted_amount,
 182: 
 183:         unconverted_amount as transaction_amount,
 184: 
 185:         16 as balance_sheet_sort_helper
 186: 
 187:     from transactions_with_converted_amounts
 188: 
 189:     left join accounts
 190:         on accounts.account_id = transactions_with_converted_amounts.account_id
 191: 
 192:     left join accounting_periods as reporting_accounting_periods 
 193:         on reporting_accounting_periods.accounting_period_id = transactions_with_converted_amounts.reporting_accounting_period_id
 194: 
 195:     left join subsidiaries
 196:         on subsidiaries.subsidiary_id = transactions_with_converted_amounts.subsidiary_id
 197: 
 198:     left join currencies subsidiaries_currencies
 199:         on subsidiaries_currencies.currency_id = subsidiaries.currency_id
 200: 
 201:     where 1=1 -- fiscal_calendar_id filter removed for mock data compatibility
 202:         -- and reporting_accounting_periods.fiscal_calendar_id = (select fiscal_calendar_id from subsidiaries where parent_id is null)
 203:         and (accounts.is_balancesheet
 204:         or transactions_with_converted_amounts.is_income_statement)
 205:     ),
 206: 
 207:     surrogate_key as ( 
 208:     select 
 209:         *,
 210:         md5(
 211:           cast(transaction_line_id as varchar) || '_' ||
 212:           cast(transaction_id as varchar) || '_' ||
 213:           cast(accounting_period_id as varchar) || '_' ||
 214:           cast(account_name as varchar) || '_' ||
 215:           cast(coalesce(account_id, '0') as varchar)
 216:         ) as balance_sheet_id
 217:     from balance_sheet
 218: )
 219: 
 220: select *
 221: from surrogate_key
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
SELECT 'intermediate.int_netsuite2__accounting_periods' source_table,count(*) rows FROM intermediate.int_netsuite2__accounting_periods UNION ALL SELECT 'intermediate.int_netsuite2__accounts' source_table,count(*) rows FROM intermediate.int_netsuite2__accounts UNION ALL SELECT 'intermediate.int_netsuite2__tran_with_converted_amounts' source_table,count(*) rows FROM intermediate.int_netsuite2__tran_with_converted_amounts UNION ALL SELECT 'staging.stg_netsuite2__currencies' source_table,count(*) rows FROM staging.stg_netsuite2__currencies UNION ALL SELECT 'staging.stg_netsuite2__subsidiaries' source_table,count(*) rows FROM staging.stg_netsuite2__subsidiaries
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ....int_netsuite2__accounting_periods' source_table,count(*) rows FROM intermediate.int_netsuite2__accounting_periods...\n                                                                     ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__accounting_periods' source_table,count(*) source_rows FROM intermediate.int_netsuite2__accounting_periods UNION ALL SELECT 'intermediate.int_netsuite2__accounts' source_table,count(*) source_rows FROM intermediate.int_netsuite2__accounts UNION ALL SELECT 'intermediate.int_netsuite2__tran_with_converted_amounts' source_table,count(*) source_rows FROM intermediate.int_netsuite2__tran_with_converted_amounts UNION ALL SELECT 'staging.stg_netsuite2__currencies' source_table,count(*) source_rows FROM staging.stg_netsuite2__currencies UNION ALL SELECT 'staging.stg_netsuite2__subsidiaries' source_table,count(*) source_rows FROM staging.stg_netsuite2__subsidiaries
```

```json
{"columns": ["source_table", "source_rows"], "result": [["intermediate.int_netsuite2__accounting_periods", 31], ["intermediate.int_netsuite2__accounts", 184], ["intermediate.int_netsuite2__tran_with_converted_amounts", 700], ["staging.stg_netsuite2__currencies", 4], ["staging.stg_netsuite2__subsidiaries", 5]]}
```

### 诊断（允许gold，不计5条）

`records/022_diagnostics.json` 本表条目：

```json
{"index": 7, "kind": "诊断查询", "queries": [{"label": "主支与CTA行数", "sql": "SELECT account_name,count(*) FROM gold.intermediate.int_netsuite2__balance_sheet GROUP BY 1 ORDER BY 2 DESC", "columns": ["account_name", "count_star()"], "result": [["Cumulative Translation Adjustment", 388], ["Retained Earnings", 219], ["Bank Account 088", 4], ["Bank Account 034", 4], ["Bank Account 033", 4], ["Bank Account 036", 4], ["Equity Account 058", 4], ["Equity Account 062", 4], ["Equity Account 066", 4], ["Bank Account 091", 4], ["Equity Account 095", 4], ["Equity Account 028", 4], ["Equity Account 133", 4], ["Equity Account 020", 4], ["Bank Account 136", 4], ["Equity Account 141", 4], ["Equity Account 147", 4], ["Bank Account 157", 4], ["Bank Account 162", 4], ["Bank Account 006", 4], ["Equity Account 138", 4], ["Equity Account 124", 4], ["Equity Account 121", 4], ["Equity Account 134", 4], ["Equity Account 110", 4], ["Bank Account 101", 4], ["Equity Account 009", 4], ["Equity Account 026", 4], ["Bank Account 087", 4], ["Bank Account 035", 4], ["Equity Account 054", 4], ["Equity Account 057", 4], ["Equity Account 063", 4], ["Bank Account 075", 4], ["Bank Account 081", 4], ["Equity Account 108", 4], ["Bank Account 180", 3], ["Bank Account 173", 3], ["Equity Account 191", 3], ["Bank Account 188", 3], ["Bank Account 174", 3], ["Equity Account 168", 3], ["Equity Account 165", 3], ["Equity Account 171", 3], ["Equity Account 181", 3], ["Equity Account 183", 3], ["Equity Account 195", 3]]}]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["balance_sheet_id"]`；比较列：`["account_category", "account_display_name", "account_id", "account_name", "account_number", "account_type_name", "accounting_period_ending", "accounting_period_name", "balance_sheet_id", "balance_sheet_sort_helper", "converted_amount", "is_account_intercompany", "is_account_leftside", "is_accounting_period_adjustment", "is_accounting_period_closed", "subsidiary_currency_symbol", "subsidiary_full_name", "subsidiary_id", "subsidiary_name", "transaction_amount", "transaction_id", "transaction_line_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L1 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L2 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L3 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| balance_sheet_id | 0 | 0 | 0 | 0 |
| account_category | 0 | 0 | 0 | 0 |
| account_display_name | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| balance_sheet_sort_helper | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| is_account_intercompany | 0 | 0 | 0 | 0 |
| is_account_leftside | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| subsidiary_currency_symbol | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_int_netsuite2__balance_sheet/baseline.sql`；SHA-256：`7a8a68abcafcc6c720519326892520dd557807837d6a28b3b7b4794e6d37fe26`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L1 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L2 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L3 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| balance_sheet_id | 0 | 0 | 0 | 0 |
| account_category | 0 | 0 | 0 | 0 |
| account_display_name | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| balance_sheet_sort_helper | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| is_account_intercompany | 0 | 0 | 0 | 0 |
| is_account_leftside | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| subsidiary_currency_symbol | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### cta_branch

SQL：`data/022_work/impl-013_int_netsuite2__balance_sheet/cta_branch.sql`；SHA-256：`52ec43501eb1b73975b4789d56dbb24e61bd6e842878c65cba2518e461e4f350`。

替换offset=3340，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
FROM presented
-- 新
FROM presented UNION ALL SELECT md5(transaction_line_id||'_'||transaction_id||'_'||reporting_accounting_period_id||'_Cumulative Translation Adjustment_0'),transaction_id,transaction_line_id,subsidiary_id,subsidiary_full_name,subsidiary_name,subsidiary_currency_symbol,reporting_accounting_period_id,ending_at,period_name,is_adjustment,is_closed,'Equity','Cumulative Translation Adjustment','Cumulative Translation Adjustment','Cumulative Translation Adjustment','cumulative_translation_adjustment',NULL,(SELECT account_number FROM intermediate.int_netsuite2__accounts WHERE lower(type_name)='cumultransadj' LIMIT 1),FALSE,FALSE,CASE WHEN lower(general_rate_type) IN ('historical','average') THEN converted_amount_using_transaction_accounting_period ELSE converted_amount_using_reporting_month END,unconverted_amount,16 FROM presented
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 776/776 | 219/219 | 0/0 | 0 | 438 | 9636 | False |
| L1 | 776/776 | 219/219 | 0/0 | 0 | 438 | 9636 | False |
| L2 | 776/776 | 219/219 | 0/0 | 0 | 438 | 9636 | False |
| L3 | 776/776 | 219/219 | 0/0 | 0 | 438 | 9636 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| balance_sheet_id | 0 | 0 | 0 | 0 |
| account_category | 0 | 0 | 0 | 0 |
| account_display_name | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| balance_sheet_sort_helper | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| is_account_intercompany | 0 | 0 | 0 | 0 |
| is_account_leftside | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| subsidiary_currency_symbol | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### key_null

SQL：`data/022_work/impl-013_int_netsuite2__balance_sheet/key_null.sql`；SHA-256：`60b35673ff0255a6d32e1d6621f301321aa8e98e2326a75581fdcad09c343de2`。

替换offset=1605，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
coalesce(CASE WHEN is_balancesheet THEN account_id END,'')
-- 新
coalesce(CASE WHEN is_balancesheet THEN account_id END,'0')
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 388/776 | 0/388 | 0/0 | 0 | 388 | 8536 | False |
| L1 | 388/776 | 0/388 | 0/0 | 0 | 388 | 8536 | False |
| L2 | 388/776 | 0/388 | 0/0 | 0 | 388 | 8536 | False |
| L3 | 388/776 | 0/388 | 0/0 | 0 | 388 | 8536 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| balance_sheet_id | 0 | 0 | 0 | 0 |
| account_category | 0 | 0 | 0 | 0 |
| account_display_name | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| balance_sheet_sort_helper | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| is_account_intercompany | 0 | 0 | 0 | 0 |
| is_account_leftside | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| subsidiary_currency_symbol | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### account_type_id

SQL：`data/022_work/impl-013_int_netsuite2__balance_sheet/account_type_id.sql`；SHA-256：`9d199c19b659d8ab95cbfe7bf50db03a4eea74db2e4299f8675325e9bf6cd0eb`。

替换offset=2140，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
lower(replace(out_type,' ', '_'))
-- 新
CASE WHEN NOT is_balancesheet THEN lower(replace(out_type,' ', '_')) WHEN lower(type_name)='retearnings' THEN 'retained_earnings' WHEN lower(type_name) IN ('cta-e','cumultransadj') THEN 'cumulative_translation_adjustment' ELSE type_name END
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L1 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L2 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L3 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| balance_sheet_id | 0 | 0 | 0 | 0 |
| account_category | 0 | 0 | 0 | 0 |
| account_display_name | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| balance_sheet_sort_helper | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| is_account_intercompany | 0 | 0 | 0 | 0 |
| is_account_leftside | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| subsidiary_currency_symbol | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### rate_selection

SQL：`data/022_work/impl-013_int_netsuite2__balance_sheet/rate_selection.sql`；SHA-256：`90fa044ae7059f0e616b18d111ad1d40a4cc074dc5cf17f1365936a0b3fa0932`。

替换offset=2440，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) ELSE coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) END AS converted_amount
-- 新
CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -CASE WHEN lower(general_rate_type) IN ('historical','average') THEN converted_amount_using_transaction_accounting_period ELSE converted_amount_using_reporting_month END WHEN is_leftside THEN CASE WHEN lower(general_rate_type) IN ('historical','average') THEN converted_amount_using_transaction_accounting_period ELSE converted_amount_using_reporting_month END ELSE 0 END AS converted_amount
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L1 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L2 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |
| L3 | 388/776 | 219/607 | 0/0 | 0 | 826 | 18172 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| balance_sheet_id | 0 | 0 | 0 | 0 |
| account_category | 0 | 0 | 0 | 0 |
| account_display_name | 0 | 0 | 0 | 0 |
| account_id | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| account_type_name | 0 | 0 | 0 | 0 |
| accounting_period_ending | 0 | 0 | 0 | 0 |
| accounting_period_name | 0 | 0 | 0 | 0 |
| balance_sheet_sort_helper | 0 | 0 | 0 | 0 |
| converted_amount | 0 | 0 | 0 | 0 |
| is_account_intercompany | 0 | 0 | 0 | 0 |
| is_account_leftside | 0 | 0 | 0 | 0 |
| is_accounting_period_adjustment | 0 | 0 | 0 | 0 |
| is_accounting_period_closed | 0 | 0 | 0 | 0 |
| subsidiary_currency_symbol | 0 | 0 | 0 | 0 |
| subsidiary_full_name | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| subsidiary_name | 0 | 0 | 0 | 0 |
| transaction_amount | 0 | 0 | 0 | 0 |
| transaction_id | 0 | 0 | 0 | 0 |
| transaction_line_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：key_null；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- cta_branch：C；参与因素。契约显式要求每行UNION ALL第二条CTA，agent完全遗漏。（行减少388，格减少8536）
- key_null：A；主项。契约只说coalesced account_id，没有规定空值哨兵；gold用0、agent空串。（行减少438，格减少9636）
- account_type_id：C；单修未满足本表所选尺度的参与门槛。契约正常账户type_id原样取type_name，agent全部小写。（行减少0，格减少0）
- rate_selection：C；单修未满足本表所选尺度的参与门槛。契约按rate_type选换算金额，agent优先coalesce交易期间。（行减少0，格减少0）

## 规则问题

coalesced account_id未写默认值；A（空串/0约定）与C（把gold的0看作默认）两读法。本轮A，不从gold补默认常量；缺CTA独立C。
