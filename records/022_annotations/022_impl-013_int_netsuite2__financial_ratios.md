# impl-013 / int_netsuite2__financial_ratios（全量；v2）

## 1. 差异与结论

五列分类SUM FILTER对空类别返回NULL，契约要求0。行数区分不了，按格子数current_liabilities与accounts_receivable各减13格并列同类C；其余三个减格的C为参与因素。

主要原因：**C**；参与因素：C：zero_total_current_assets；C：zero_cash_and_equivalents；C：zero_total_equity；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| zero_total_current_liabilities | C | 0 | 13 |
| zero_accounts_receivable | C | 0 | 13 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_int_netsuite2__financial_ratios.md](../../records/022_packages/022_impl-013_int_netsuite2__financial_ratios.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_int_netsuite2__financial_ratios/022_impl-013_int_netsuite2__financial_ratios.json`。
- 比较结果：[022_reruns_impl-013_int_netsuite2__financial_ratios.json](../022_reruns_impl-013_int_netsuite2__financial_ratios.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第1101–1189行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__financial_ratios.sql`；原件第1–1行。

```sql
   1: WITH latest AS (SELECT max(accounting_period_ending) latest_date FROM intermediate.int_netsuite2__balance_sheet), bs AS (SELECT subsidiary_id,accounting_period_id,accounting_period_ending,account_type_name,sum(converted_amount) period_balance FROM intermediate.int_netsuite2__balance_sheet CROSS JOIN latest WHERE accounting_period_ending=latest_date GROUP BY ALL), assets AS (SELECT subsidiary_id,accounting_period_id,sum(period_balance) FILTER(WHERE account_type_name IN ('Bank','AcctRec','UnbilledRec','OthCurrAsset')) total_current_assets,sum(period_balance) FILTER(WHERE account_type_name='Bank') cash_and_equivalents,sum(period_balance) FILTER(WHERE account_type_name IN ('AcctRec','UnbilledRec')) accounts_receivable FROM bs GROUP BY subsidiary_id,accounting_period_id), liabs AS (SELECT subsidiary_id,accounting_period_id,sum(abs(period_balance)) FILTER(WHERE account_type_name IN ('AcctPay','CredCard','OthCurrLiab')) total_current_liabilities FROM bs GROUP BY subsidiary_id,accounting_period_id), eq AS (SELECT subsidiary_id,accounting_period_id,sum(period_balance) FILTER(WHERE account_type_name IN ('Equity','Retained Earnings','Net Income')) total_equity FROM bs GROUP BY subsidiary_id,accounting_period_id), inc AS (SELECT subsidiary_id,sum(converted_amount) FILTER(WHERE account_type_name='Income') total_revenue,sum(converted_amount) FILTER(WHERE account_type_name='COGS') total_cogs,sum(converted_amount) FILTER(WHERE account_type_name IN ('Income','COGS','Expense','OthIncome','OthExpense')) net_income FROM intermediate.int_netsuite2__income_statement WHERE accounting_period_ending>=current_date-interval '12 months' GROUP BY subsidiary_id), ratios AS (SELECT a.*,l.total_current_liabilities,e.total_equity,i.total_revenue,i.total_cogs,i.net_income,a.total_current_assets/nullif(l.total_current_liabilities,0) current_ratio,(a.cash_and_equivalents+a.accounts_receivable)/nullif(l.total_current_liabilities,0) quick_ratio,a.cash_and_equivalents/nullif(l.total_current_liabilities,0) cash_ratio,i.net_income/nullif(e.total_equity,0) return_on_equity,(i.total_revenue-i.total_cogs)/nullif(i.total_revenue,0) gross_margin_ratio,i.net_income/nullif(i.total_revenue,0) net_profit_margin,i.total_revenue/nullif(a.accounts_receivable,0) receivables_turnover FROM assets a LEFT JOIN liabs l USING(subsidiary_id,accounting_period_id) LEFT JOIN eq e USING(subsidiary_id,accounting_period_id) LEFT JOIN inc i USING(subsidiary_id)) , scores AS (SELECT *,CASE WHEN current_ratio>=2 THEN 100 WHEN current_ratio>=1.5 THEN 80 WHEN current_ratio>=1 THEN 60 WHEN current_ratio>=.8 THEN 40 WHEN current_ratio>=.5 THEN 20 ELSE 0 END liquidity_score,CASE WHEN net_profit_margin>=.15 THEN 100 WHEN net_profit_margin>=.1 THEN 80 WHEN net_profit_margin>=.05 THEN 60 WHEN net_profit_margin>=.02 THEN 40 WHEN net_profit_margin>=0 THEN 20 ELSE 0 END profitability_score,CASE WHEN receivables_turnover>=12 THEN 100 WHEN receivables_turnover>=8 THEN 80 WHEN receivables_turnover>=6 THEN 60 WHEN receivables_turnover>=4 THEN 40 WHEN receivables_turnover>=2 THEN 20 ELSE 0 END efficiency_score FROM ratios) SELECT subsidiary_id,accounting_period_id,current_ratio,quick_ratio,cash_ratio,return_on_equity,gross_margin_ratio,net_profit_margin,receivables_turnover,total_current_assets,total_current_liabilities,cash_and_equivalents,accounts_receivable,total_equity,total_revenue,total_cogs,net_income,current_date calculation_date,liquidity_score,profitability_score,efficiency_score,round((liquidity_score+profitability_score+efficiency_score)/3.0,2) overall_financial_health_score,CASE WHEN (liquidity_score+profitability_score+efficiency_score)/3.0>=80 THEN 'Excellent' WHEN (liquidity_score+profitability_score+efficiency_score)/3.0>=60 THEN 'Good' WHEN (liquidity_score+profitability_score+efficiency_score)/3.0>=40 THEN 'Fair' WHEN (liquidity_score+profitability_score+efficiency_score)/3.0>=20 THEN 'Poor' ELSE 'Critical' END financial_health_grade,md5(subsidiary_id||'_'||accounting_period_id) financial_ratios_id FROM scores WHERE subsidiary_id IS NOT NULL
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__financial_ratios.sql`；原件第1–201行。

```sql
   1: -- Financial Ratios Calculation
   2: -- Calculate key financial ratios, including current ratio, quick ratio, ROE, etc.
   3: with current_period_balances as (
   4:     select 
   5:         subsidiary_id,
   6:         account_type_name,
   7:         accounting_period_id,
   8:         accounting_period_ending,
   9:         sum(converted_amount) as period_balance
  10:     from intermediate.int_netsuite2__balance_sheet
  11:     where accounting_period_ending = (
  12:         select max(accounting_period_ending) 
  13:         from intermediate.int_netsuite2__balance_sheet
  14:     )
  15:     group by 
  16:         subsidiary_id,
  17:         account_type_name,
  18:         accounting_period_id,
  19:         accounting_period_ending
  20: ),
  21: 
  22: current_assets as (
  23:     select 
  24:         subsidiary_id,
  25:         accounting_period_id,
  26:         sum(case when account_type_name in ('Bank', 'AcctRec', 'UnbilledRec', 'OthCurrAsset') 
  27:                  then period_balance else 0 end) as total_current_assets,
  28:         sum(case when account_type_name in ('Bank') 
  29:                  then period_balance else 0 end) as cash_and_equivalents,
  30:         sum(case when account_type_name in ('AcctRec', 'UnbilledRec') 
  31:                  then period_balance else 0 end) as accounts_receivable
  32:     from current_period_balances
  33:     group by subsidiary_id, accounting_period_id
  34: ),
  35: 
  36: current_liabilities as (
  37:     select 
  38:         subsidiary_id,
  39:         accounting_period_id,
  40:         sum(case when account_type_name in ('AcctPay', 'CredCard', 'OthCurrLiab') 
  41:                  then abs(period_balance) else 0 end) as total_current_liabilities
  42:     from current_period_balances
  43:     group by subsidiary_id, accounting_period_id
  44: ),
  45: 
  46: total_equity as (
  47:     select 
  48:         subsidiary_id,
  49:         accounting_period_id,
  50:         sum(case when account_type_name in ('Equity', 'Retained Earnings', 'Net Income') 
  51:                  then period_balance else 0 end) as total_equity
  52:     from current_period_balances
  53:     group by subsidiary_id, accounting_period_id
  54: ),
  55: 
  56: income_metrics as (
  57:     select 
  58:         subsidiary_id,
  59:         sum(case when account_type_name = 'Income' 
  60:                  then converted_amount else 0 end) as total_revenue,
  61:         sum(case when account_type_name = 'COGS' 
  62:                  then converted_amount else 0 end) as total_cogs,
  63:         sum(case when account_type_name in ('Income', 'COGS', 'Expense', 'OthIncome', 'OthExpense') 
  64:                  then converted_amount else 0 end) as net_income
  65:     from intermediate.int_netsuite2__income_statement
  66:     where accounting_period_ending >= current_date - interval '12 months'
  67:     group by subsidiary_id
  68: ),
  69: 
  70: calculated_ratios as (
  71:     select 
  72:         ca.subsidiary_id,
  73:         ca.accounting_period_id,
  74:         
  75:         -- liquidity ratio
  76:         case 
  77:             when cl.total_current_liabilities > 0 
  78:             then ca.total_current_assets / cl.total_current_liabilities
  79:             else null 
  80:         end as current_ratio,
  81:         
  82:         -- Quick Ratio
  83:         case 
  84:             when cl.total_current_liabilities > 0 
  85:             then (ca.cash_and_equivalents + ca.accounts_receivable) / cl.total_current_liabilities
  86:             else null 
  87:         end as quick_ratio,
  88:         
  89:         -- cash ratio
  90:         case 
  91:             when cl.total_current_liabilities > 0 
  92:             then ca.cash_and_equivalents / cl.total_current_liabilities
  93:             else null 
  94:         end as cash_ratio,
  95:         
  96:         -- Return on Equity (ROE)
  97:         case 
  98:             when te.total_equity > 0 
  99:             then im.net_income / te.total_equity
 100:             else null 
 101:         end as return_on_equity,
 102:         
 103:         -- Gross profit margin
 104:         case 
 105:             when im.total_revenue > 0 
 106:             then (im.total_revenue - im.total_cogs) / im.total_revenue
 107:             else null 
 108:         end as gross_margin_ratio,
 109:         
 110:         -- net profit margin
 111:         case 
 112:             when im.total_revenue > 0 
 113:             then im.net_income / im.total_revenue
 114:             else null 
 115:         end as net_profit_margin,
 116:         
 117:         -- Accounts receivable turnover ratio
 118:         case 
 119:             when ca.accounts_receivable > 0 
 120:             then im.total_revenue / ca.accounts_receivable
 121:             else null 
 122:         end as receivables_turnover,
 123:         
 124:         -- Raw data used for verification
 125:         ca.total_current_assets,
 126:         cl.total_current_liabilities,
 127:         ca.cash_and_equivalents,
 128:         ca.accounts_receivable,
 129:         te.total_equity,
 130:         im.total_revenue,
 131:         im.total_cogs,
 132:         im.net_income,
 133:         
 134:         current_date as calculation_date
 135:         
 136:     from current_assets ca
 137:     left join current_liabilities cl
 138:         on ca.subsidiary_id = cl.subsidiary_id 
 139:         and ca.accounting_period_id = cl.accounting_period_id
 140:     left join total_equity te
 141:         on ca.subsidiary_id = te.subsidiary_id 
 142:         and ca.accounting_period_id = te.accounting_period_id
 143:     left join income_metrics im
 144:         on ca.subsidiary_id = im.subsidiary_id
 145: ),
 146: 
 147: -- Add financial health score
 148: financial_health_scoring as (
 149:     select 
 150:         *,
 151:         -- Liquidity Score (0-100)
 152:         case 
 153:             when current_ratio >= 2.0 then 100
 154:             when current_ratio >= 1.5 then 80
 155:             when current_ratio >= 1.0 then 60
 156:             when current_ratio >= 0.8 then 40
 157:             when current_ratio >= 0.5 then 20
 158:             else 0
 159:         end as liquidity_score,
 160:         
 161:         -- Profitability score (0-100)
 162:         case 
 163:             when net_profit_margin >= 0.15 then 100
 164:             when net_profit_margin >= 0.10 then 80
 165:             when net_profit_margin >= 0.05 then 60
 166:             when net_profit_margin >= 0.02 then 40
 167:             when net_profit_margin >= 0 then 20
 168:             else 0
 169:         end as profitability_score,
 170:         
 171:         -- Efficiency score (0-100)
 172:         case 
 173:             when receivables_turnover >= 12 then 100
 174:             when receivables_turnover >= 8 then 80
 175:             when receivables_turnover >= 6 then 60
 176:             when receivables_turnover >= 4 then 40
 177:             when receivables_turnover >= 2 then 20
 178:             else 0
 179:         end as efficiency_score
 180:         
 181:     from calculated_ratios
 182: )
 183: 
 184: select 
 185:     *,
 186:     -- Comprehensive Financial Health Score
 187:     round((liquidity_score + profitability_score + efficiency_score) / 3.0, 2) as overall_financial_health_score,
 188:     
 189:     -- Financial health level
 190:     case 
 191:         when round((liquidity_score + profitability_score + efficiency_score) / 3.0, 2) >= 80 then 'Excellent'
 192:         when round((liquidity_score + profitability_score + efficiency_score) / 3.0, 2) >= 60 then 'Good'
 193:         when round((liquidity_score + profitability_score + efficiency_score) / 3.0, 2) >= 40 then 'Fair'
 194:         when round((liquidity_score + profitability_score + efficiency_score) / 3.0, 2) >= 20 then 'Poor'
 195:         else 'Critical'
 196:     end as financial_health_grade,
 197:     
 198:     md5(cast(subsidiary_id as varchar) || '_' || cast(accounting_period_id as varchar)) as financial_ratios_id
 199:     
 200: from financial_health_scoring
 201: where subsidiary_id is not null
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
SELECT 'intermediate.int_netsuite2__balance_sheet' source_table,count(*) rows FROM intermediate.int_netsuite2__balance_sheet UNION ALL SELECT 'intermediate.int_netsuite2__income_statement' source_table,count(*) rows FROM intermediate.int_netsuite2__income_statement
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ...ediate.int_netsuite2__balance_sheet' source_table,count(*) rows FROM intermediate.int_netsuite2__balance_sheet UNION...\n                                                                      ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'intermediate.int_netsuite2__balance_sheet' source_table,count(*) source_rows FROM intermediate.int_netsuite2__balance_sheet UNION ALL SELECT 'intermediate.int_netsuite2__income_statement' source_table,count(*) source_rows FROM intermediate.int_netsuite2__income_statement
```

```json
{"columns": ["source_table", "source_rows"], "result": [["intermediate.int_netsuite2__balance_sheet", 219], ["intermediate.int_netsuite2__income_statement", 219]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 2}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["financial_ratios_id"]`；比较列：`["subsidiary_id", "accounting_period_id", "current_ratio", "quick_ratio", "cash_ratio", "return_on_equity", "gross_margin_ratio", "net_profit_margin", "receivables_turnover", "total_current_assets", "total_current_liabilities", "cash_and_equivalents", "accounts_receivable", "total_equity", "total_revenue", "total_cogs", "net_income", "calculation_date", "liquidity_score", "profitability_score", "efficiency_score", "overall_financial_health_score", "financial_health_grade", "financial_ratios_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 13/13 | 0/0 | 0/0 | 13 | 13 | 49 | False |
| L1 | 13/13 | 0/0 | 0/0 | 13 | 13 | 49 | False |
| L2 | 13/13 | 0/0 | 0/0 | 13 | 13 | 49 | False |
| L3 | 13/13 | 0/0 | 0/0 | 13 | 13 | 49 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| financial_ratios_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| accounting_period_id | 0 | 0 | 0 | 0 |
| current_ratio | 0 | 0 | 0 | 0 |
| quick_ratio | 0 | 0 | 0 | 0 |
| cash_ratio | 0 | 0 | 0 | 0 |
| return_on_equity | 0 | 0 | 0 | 0 |
| gross_margin_ratio | 0 | 0 | 0 | 0 |
| net_profit_margin | 0 | 0 | 0 | 0 |
| receivables_turnover | 0 | 0 | 0 | 0 |
| total_current_assets | 10 | 10 | 10 | 10 |
| total_current_liabilities | 13 | 13 | 13 | 13 |
| cash_and_equivalents | 10 | 10 | 10 | 10 |
| accounts_receivable | 13 | 13 | 13 | 13 |
| total_equity | 3 | 3 | 3 | 3 |
| total_revenue | 0 | 0 | 0 | 0 |
| total_cogs | 0 | 0 | 0 | 0 |
| net_income | 0 | 0 | 0 | 0 |
| calculation_date | 0 | 0 | 0 | 0 |
| liquidity_score | 0 | 0 | 0 | 0 |
| profitability_score | 0 | 0 | 0 | 0 |
| efficiency_score | 0 | 0 | 0 | 0 |
| overall_financial_health_score | 0 | 0 | 0 | 0 |
| financial_health_grade | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_int_netsuite2__financial_ratios/baseline.sql`；SHA-256：`e19fcb92b1a1dca646f60beb943ef3aebb0ae7debc42f724757ae294df5223c9`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 13/13 | 0/0 | 0/0 | 13 | 13 | 49 | False |
| L1 | 13/13 | 0/0 | 0/0 | 13 | 13 | 49 | False |
| L2 | 13/13 | 0/0 | 0/0 | 13 | 13 | 49 | False |
| L3 | 13/13 | 0/0 | 0/0 | 13 | 13 | 49 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| financial_ratios_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| accounting_period_id | 0 | 0 | 0 | 0 |
| current_ratio | 0 | 0 | 0 | 0 |
| quick_ratio | 0 | 0 | 0 | 0 |
| cash_ratio | 0 | 0 | 0 | 0 |
| return_on_equity | 0 | 0 | 0 | 0 |
| gross_margin_ratio | 0 | 0 | 0 | 0 |
| net_profit_margin | 0 | 0 | 0 | 0 |
| receivables_turnover | 0 | 0 | 0 | 0 |
| total_current_assets | 10 | 10 | 10 | 10 |
| total_current_liabilities | 13 | 13 | 13 | 13 |
| cash_and_equivalents | 10 | 10 | 10 | 10 |
| accounts_receivable | 13 | 13 | 13 | 13 |
| total_equity | 3 | 3 | 3 | 3 |
| total_revenue | 0 | 0 | 0 | 0 |
| total_cogs | 0 | 0 | 0 | 0 |
| net_income | 0 | 0 | 0 | 0 |
| calculation_date | 0 | 0 | 0 | 0 |
| liquidity_score | 0 | 0 | 0 | 0 |
| profitability_score | 0 | 0 | 0 | 0 |
| efficiency_score | 0 | 0 | 0 | 0 |
| overall_financial_health_score | 0 | 0 | 0 | 0 |
| financial_health_grade | 0 | 0 | 0 | 0 |

### zero_total_current_assets

SQL：`data/022_work/impl-013_int_netsuite2__financial_ratios/zero_total_current_assets.sql`；SHA-256：`bac94853b0c6745ac699a34408980e90afa0fbdeca4376547e1f7e1d4e1d3790`。

替换offset=419，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(period_balance) FILTER(WHERE account_type_name IN ('Bank','AcctRec','UnbilledRec','OthCurrAsset')) total_current_assets
-- 新
coalesce(sum(period_balance) FILTER(WHERE account_type_name IN ('Bank','AcctRec','UnbilledRec','OthCurrAsset')),0) total_current_assets
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 13/13 | 0/0 | 0/0 | 13 | 13 | 39 | False |
| L1 | 13/13 | 0/0 | 0/0 | 13 | 13 | 39 | False |
| L2 | 13/13 | 0/0 | 0/0 | 13 | 13 | 39 | False |
| L3 | 13/13 | 0/0 | 0/0 | 13 | 13 | 39 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| financial_ratios_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| accounting_period_id | 0 | 0 | 0 | 0 |
| current_ratio | 0 | 0 | 0 | 0 |
| quick_ratio | 0 | 0 | 0 | 0 |
| cash_ratio | 0 | 0 | 0 | 0 |
| return_on_equity | 0 | 0 | 0 | 0 |
| gross_margin_ratio | 0 | 0 | 0 | 0 |
| net_profit_margin | 0 | 0 | 0 | 0 |
| receivables_turnover | 0 | 0 | 0 | 0 |
| total_current_assets | 0 | 0 | 0 | 0 |
| total_current_liabilities | 13 | 13 | 13 | 13 |
| cash_and_equivalents | 10 | 10 | 10 | 10 |
| accounts_receivable | 13 | 13 | 13 | 13 |
| total_equity | 3 | 3 | 3 | 3 |
| total_revenue | 0 | 0 | 0 | 0 |
| total_cogs | 0 | 0 | 0 | 0 |
| net_income | 0 | 0 | 0 | 0 |
| calculation_date | 0 | 0 | 0 | 0 |
| liquidity_score | 0 | 0 | 0 | 0 |
| profitability_score | 0 | 0 | 0 | 0 |
| efficiency_score | 0 | 0 | 0 | 0 |
| overall_financial_health_score | 0 | 0 | 0 | 0 |
| financial_health_grade | 0 | 0 | 0 | 0 |

### zero_total_current_liabilities

SQL：`data/022_work/impl-013_int_netsuite2__financial_ratios/zero_total_current_liabilities.sql`；SHA-256：`dae313d7a81897c4c5a8f5413a63b0390945f0271ad6ece21da0601cd07b8e89`。

替换offset=830，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(abs(period_balance)) FILTER(WHERE account_type_name IN ('AcctPay','CredCard','OthCurrLiab')) total_current_liabilities
-- 新
coalesce(sum(abs(period_balance)) FILTER(WHERE account_type_name IN ('AcctPay','CredCard','OthCurrLiab')),0) total_current_liabilities
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 13/13 | 0/0 | 0/0 | 13 | 13 | 36 | False |
| L1 | 13/13 | 0/0 | 0/0 | 13 | 13 | 36 | False |
| L2 | 13/13 | 0/0 | 0/0 | 13 | 13 | 36 | False |
| L3 | 13/13 | 0/0 | 0/0 | 13 | 13 | 36 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| financial_ratios_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| accounting_period_id | 0 | 0 | 0 | 0 |
| current_ratio | 0 | 0 | 0 | 0 |
| quick_ratio | 0 | 0 | 0 | 0 |
| cash_ratio | 0 | 0 | 0 | 0 |
| return_on_equity | 0 | 0 | 0 | 0 |
| gross_margin_ratio | 0 | 0 | 0 | 0 |
| net_profit_margin | 0 | 0 | 0 | 0 |
| receivables_turnover | 0 | 0 | 0 | 0 |
| total_current_assets | 10 | 10 | 10 | 10 |
| total_current_liabilities | 0 | 0 | 0 | 0 |
| cash_and_equivalents | 10 | 10 | 10 | 10 |
| accounts_receivable | 13 | 13 | 13 | 13 |
| total_equity | 3 | 3 | 3 | 3 |
| total_revenue | 0 | 0 | 0 | 0 |
| total_cogs | 0 | 0 | 0 | 0 |
| net_income | 0 | 0 | 0 | 0 |
| calculation_date | 0 | 0 | 0 | 0 |
| liquidity_score | 0 | 0 | 0 | 0 |
| profitability_score | 0 | 0 | 0 | 0 |
| efficiency_score | 0 | 0 | 0 | 0 |
| overall_financial_health_score | 0 | 0 | 0 | 0 |
| financial_health_grade | 0 | 0 | 0 | 0 |

### zero_cash_and_equivalents

SQL：`data/022_work/impl-013_int_netsuite2__financial_ratios/zero_cash_and_equivalents.sql`；SHA-256：`75f7d9af8de8ca9fee7ba3e862c34b29230c3a70d88c921aa61f2d7db2a6fe9c`。

替换offset=543，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(period_balance) FILTER(WHERE account_type_name='Bank') cash_and_equivalents
-- 新
coalesce(sum(period_balance) FILTER(WHERE account_type_name='Bank'),0) cash_and_equivalents
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 13/13 | 0/0 | 0/0 | 13 | 13 | 39 | False |
| L1 | 13/13 | 0/0 | 0/0 | 13 | 13 | 39 | False |
| L2 | 13/13 | 0/0 | 0/0 | 13 | 13 | 39 | False |
| L3 | 13/13 | 0/0 | 0/0 | 13 | 13 | 39 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| financial_ratios_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| accounting_period_id | 0 | 0 | 0 | 0 |
| current_ratio | 0 | 0 | 0 | 0 |
| quick_ratio | 0 | 0 | 0 | 0 |
| cash_ratio | 0 | 0 | 0 | 0 |
| return_on_equity | 0 | 0 | 0 | 0 |
| gross_margin_ratio | 0 | 0 | 0 | 0 |
| net_profit_margin | 0 | 0 | 0 | 0 |
| receivables_turnover | 0 | 0 | 0 | 0 |
| total_current_assets | 10 | 10 | 10 | 10 |
| total_current_liabilities | 13 | 13 | 13 | 13 |
| cash_and_equivalents | 0 | 0 | 0 | 0 |
| accounts_receivable | 13 | 13 | 13 | 13 |
| total_equity | 3 | 3 | 3 | 3 |
| total_revenue | 0 | 0 | 0 | 0 |
| total_cogs | 0 | 0 | 0 | 0 |
| net_income | 0 | 0 | 0 | 0 |
| calculation_date | 0 | 0 | 0 | 0 |
| liquidity_score | 0 | 0 | 0 | 0 |
| profitability_score | 0 | 0 | 0 | 0 |
| efficiency_score | 0 | 0 | 0 | 0 |
| overall_financial_health_score | 0 | 0 | 0 | 0 |
| financial_health_grade | 0 | 0 | 0 | 0 |

### zero_accounts_receivable

SQL：`data/022_work/impl-013_int_netsuite2__financial_ratios/zero_accounts_receivable.sql`；SHA-256：`1cafab3b6650caa56786639c5b311db641fb46cab479489dda989b191ebb571b`。

替换offset=623，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(period_balance) FILTER(WHERE account_type_name IN ('AcctRec','UnbilledRec')) accounts_receivable
-- 新
coalesce(sum(period_balance) FILTER(WHERE account_type_name IN ('AcctRec','UnbilledRec')),0) accounts_receivable
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 13/13 | 0/0 | 0/0 | 13 | 13 | 36 | False |
| L1 | 13/13 | 0/0 | 0/0 | 13 | 13 | 36 | False |
| L2 | 13/13 | 0/0 | 0/0 | 13 | 13 | 36 | False |
| L3 | 13/13 | 0/0 | 0/0 | 13 | 13 | 36 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| financial_ratios_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| accounting_period_id | 0 | 0 | 0 | 0 |
| current_ratio | 0 | 0 | 0 | 0 |
| quick_ratio | 0 | 0 | 0 | 0 |
| cash_ratio | 0 | 0 | 0 | 0 |
| return_on_equity | 0 | 0 | 0 | 0 |
| gross_margin_ratio | 0 | 0 | 0 | 0 |
| net_profit_margin | 0 | 0 | 0 | 0 |
| receivables_turnover | 0 | 0 | 0 | 0 |
| total_current_assets | 10 | 10 | 10 | 10 |
| total_current_liabilities | 13 | 13 | 13 | 13 |
| cash_and_equivalents | 10 | 10 | 10 | 10 |
| accounts_receivable | 0 | 0 | 0 | 0 |
| total_equity | 3 | 3 | 3 | 3 |
| total_revenue | 0 | 0 | 0 | 0 |
| total_cogs | 0 | 0 | 0 | 0 |
| net_income | 0 | 0 | 0 | 0 |
| calculation_date | 0 | 0 | 0 | 0 |
| liquidity_score | 0 | 0 | 0 | 0 |
| profitability_score | 0 | 0 | 0 | 0 |
| efficiency_score | 0 | 0 | 0 | 0 |
| overall_financial_health_score | 0 | 0 | 0 | 0 |
| financial_health_grade | 0 | 0 | 0 | 0 |

### zero_total_equity

SQL：`data/022_work/impl-013_int_netsuite2__financial_ratios/zero_total_equity.sql`；SHA-256：`eb9970457105172b09b6c619bf7970ffd03c5b8342e020f0a6dc2457a2c28775`。

替换offset=1056，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
sum(period_balance) FILTER(WHERE account_type_name IN ('Equity','Retained Earnings','Net Income')) total_equity
-- 新
coalesce(sum(period_balance) FILTER(WHERE account_type_name IN ('Equity','Retained Earnings','Net Income')),0) total_equity
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 13/13 | 0/0 | 0/0 | 13 | 13 | 46 | False |
| L1 | 13/13 | 0/0 | 0/0 | 13 | 13 | 46 | False |
| L2 | 13/13 | 0/0 | 0/0 | 13 | 13 | 46 | False |
| L3 | 13/13 | 0/0 | 0/0 | 13 | 13 | 46 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| financial_ratios_id | 0 | 0 | 0 | 0 |
| subsidiary_id | 0 | 0 | 0 | 0 |
| accounting_period_id | 0 | 0 | 0 | 0 |
| current_ratio | 0 | 0 | 0 | 0 |
| quick_ratio | 0 | 0 | 0 | 0 |
| cash_ratio | 0 | 0 | 0 | 0 |
| return_on_equity | 0 | 0 | 0 | 0 |
| gross_margin_ratio | 0 | 0 | 0 | 0 |
| net_profit_margin | 0 | 0 | 0 | 0 |
| receivables_turnover | 0 | 0 | 0 | 0 |
| total_current_assets | 10 | 10 | 10 | 10 |
| total_current_liabilities | 13 | 13 | 13 | 13 |
| cash_and_equivalents | 10 | 10 | 10 | 10 |
| accounts_receivable | 13 | 13 | 13 | 13 |
| total_equity | 0 | 0 | 0 | 0 |
| total_revenue | 0 | 0 | 0 | 0 |
| total_cogs | 0 | 0 | 0 | 0 |
| net_income | 0 | 0 | 0 | 0 |
| calculation_date | 0 | 0 | 0 | 0 |
| liquidity_score | 0 | 0 | 0 | 0 |
| profitability_score | 0 | 0 | 0 | 0 |
| efficiency_score | 0 | 0 | 0 | 0 |
| overall_financial_health_score | 0 | 0 | 0 | 0 |
| financial_health_grade | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

未达到/不适用；本表没有U归因。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- zero_total_current_assets：C；参与因素。契约按类别SUM CASE ELSE 0；FILTER无匹配得到NULL。（行减少0，格减少10）
- zero_total_current_liabilities：C；主项。契约按类别SUM CASE ELSE 0；FILTER无匹配得到NULL。（行减少0，格减少13）
- zero_cash_and_equivalents：C；参与因素。契约按类别SUM CASE ELSE 0；FILTER无匹配得到NULL。（行减少0，格减少10）
- zero_accounts_receivable：C；主项。契约按类别SUM CASE ELSE 0；FILTER无匹配得到NULL。（行减少0，格减少13）
- zero_total_equity：C；参与因素。契约按类别SUM CASE ELSE 0；FILTER无匹配得到NULL。（行减少0，格减少3）

## 规则问题

无。按v2冻结定义执行。
