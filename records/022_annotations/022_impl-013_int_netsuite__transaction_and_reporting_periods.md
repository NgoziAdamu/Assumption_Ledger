# impl-013 / int_netsuite__transaction_and_reporting_periods（全量；v2）

## 1. 差异与结论

starting_at含偏移文本，TRY_CAST结果NULL，过滤排空。契约明确截到秒再解释为timestamp；按该规则单修后2230行L0完全一致，C而非U。

主要原因：**C**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| parse_period | C | 2230 | 4460 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_int_netsuite__transaction_and_reporting_periods.md](../../records/022_packages/022_impl-013_int_netsuite__transaction_and_reporting_periods.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_int_netsuite__transaction_and_reporting_periods/022_impl-013_int_netsuite__transaction_and_reporting_periods.json`。
- 比较结果：[022_reruns_impl-013_int_netsuite__transaction_and_reporting_periods.json](../022_reruns_impl-013_int_netsuite__transaction_and_reporting_periods.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第2460–2477行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite__transaction_and_reporting_periods.sql`；原件第1–1行。

```sql
   1: SELECT b.accounting_period_id,m.accounting_period_id reporting_accounting_period_id FROM staging.stg_netsuite__accounting_periods b JOIN staging.stg_netsuite__accounting_periods m ON b.fiscal_calendar_id=m.fiscal_calendar_id AND m.starting_at>=b.starting_at AND try_cast(m.starting_at AS TIMESTAMP)<=current_timestamp AND NOT b.quarter AND NOT b.year_0 AND NOT m.quarter AND NOT m.year_0 WHERE b.fiscal_calendar_id IN (SELECT DISTINCT fiscal_calendar_id FROM staging.stg_netsuite__subsidiaries)
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite__transaction_and_reporting_periods.sql`；原件第1–30行。

```sql
   1: with accounting_periods as (
   2:     select * 
   3:     from staging.stg_netsuite__accounting_periods
   4: ),
   5: 
   6: subsidiaries as (
   7:     select * 
   8:     from staging.stg_netsuite__subsidiaries
   9: ),
  10: 
  11: transaction_and_reporting_periods as ( 
  12:   select
  13:     base.accounting_period_id as accounting_period_id,
  14:     multiplier.accounting_period_id as reporting_accounting_period_id
  15:   from accounting_periods as base
  16: 
  17:   join accounting_periods as multiplier
  18:     on multiplier.starting_at >= base.starting_at
  19:       and multiplier.quarter = base.quarter
  20:       and multiplier.year_0 = base.year_0
  21:       and multiplier.fiscal_calendar_id = base.fiscal_calendar_id
  22:       and strptime(substr(multiplier.starting_at, 1, 19), '%Y-%m-%d %H:%M:%S') <= current_timestamp
  23: 
  24:   where base.quarter = false
  25:     and base.year_0 = false
  26:     and base.fiscal_calendar_id in (select distinct fiscal_calendar_id from subsidiaries) -- fiscal calendar will align with subsidiary calendars
  27: )
  28: 
  29: select * 
  30: from transaction_and_reporting_periods
```

## 3. agent看到的材料与不确定性

已检视该题全部67个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 65 / finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/65.json`。

四档：**只有通用策略说明**。

原句（见上述最终报告事件）：

```text
采用 TRY_CAST 安全解析原始日期/类型；不可解析的值成为 NULL。
```

## 4. 核实查询与诊断

核实查询共**3条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'staging.stg_netsuite__accounting_periods' source_table,count(*) rows FROM staging.stg_netsuite__accounting_periods UNION ALL SELECT 'staging.stg_netsuite__subsidiaries' source_table,count(*) rows FROM staging.stg_netsuite__subsidiaries
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ....stg_netsuite__accounting_periods' source_table,count(*) rows FROM staging.stg_netsuite__accounting_periods UNION...\n                                                                    ^"}
```

### 核实 V2：期间解析

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT count(*) n,count(try_cast(starting_at AS TIMESTAMP)) direct_parsed,count(try_strptime(substr(starting_at,1,19),'%Y-%m-%d %H:%M:%S')) seconds_parsed FROM staging.stg_netsuite__accounting_periods
```

```json
{"columns": ["n", "direct_parsed", "seconds_parsed"], "result": [[710, 0, 710]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'staging.stg_netsuite__accounting_periods' source_table,count(*) source_rows FROM staging.stg_netsuite__accounting_periods UNION ALL SELECT 'staging.stg_netsuite__subsidiaries' source_table,count(*) source_rows FROM staging.stg_netsuite__subsidiaries
```

```json
{"columns": ["source_table", "source_rows"], "result": [["staging.stg_netsuite__accounting_periods", 710], ["staging.stg_netsuite__subsidiaries", 705]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["accounting_period_id", "reporting_accounting_period_id"]`；比较列：`["accounting_period_id", "reporting_accounting_period_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 0/2230 | 0/2230 | 0/0 | 0 | 2230 | 4460 | False |
| L1 | 0/2230 | 0/2230 | 0/0 | 0 | 2230 | 4460 | False |
| L2 | 0/2230 | 0/2230 | 0/0 | 0 | 2230 | 4460 | False |
| L3 | 0/2230 | 0/2230 | 0/0 | 0 | 2230 | 4460 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| accounting_period_id | 0 | 0 | 0 | 0 |
| reporting_accounting_period_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_int_netsuite__transaction_and_reporting_periods/baseline.sql`；SHA-256：`e99d4c8d90fcd5e486ce0f6062af1a500a02538abceaf36734c169ee014f89f8`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 0/2230 | 0/2230 | 0/0 | 0 | 2230 | 4460 | False |
| L1 | 0/2230 | 0/2230 | 0/0 | 0 | 2230 | 4460 | False |
| L2 | 0/2230 | 0/2230 | 0/0 | 0 | 2230 | 4460 | False |
| L3 | 0/2230 | 0/2230 | 0/0 | 0 | 2230 | 4460 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| accounting_period_id | 0 | 0 | 0 | 0 |
| reporting_accounting_period_id | 0 | 0 | 0 | 0 |

### parse_period

SQL：`data/022_work/impl-013_int_netsuite__transaction_and_reporting_periods/parse_period.sql`；SHA-256：`b785b8e51a49b42bb3f89824bbf87be4ae744d69b79790eab602a7402970cf6b`。

替换offset=262，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_cast(m.starting_at AS TIMESTAMP)
-- 新
strptime(substr(m.starting_at,1,19), '%Y-%m-%d %H:%M:%S')
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 2230/2230 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 2230/2230 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 2230/2230 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 2230/2230 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| accounting_period_id | 0 | 0 | 0 | 0 |
| reporting_accounting_period_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：parse_period；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- parse_period：C；主项。契约明确截到秒解析；直接TRY_CAST带偏移字符串失败。（行减少2230，格减少4460）

## 规则问题

无。按v2冻结定义执行。
