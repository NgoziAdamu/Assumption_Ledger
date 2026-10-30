# impl-013 / stg_netsuite2__account_types（全量；v2）

## 1. 差异与结论

原internalid和按longname排序生成row_number均唯一，契约未给生成规则；不能据gold选排序号否定原标识。单换编号L0一致，A。

主要原因：**A**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| type_key | A | 6 | 12 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_stg_netsuite2__account_types.md](../../records/022_packages/022_impl-013_stg_netsuite2__account_types.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_stg_netsuite2__account_types/022_impl-013_stg_netsuite2__account_types.json`。
- 比较结果：[022_reruns_impl-013_stg_netsuite2__account_types.json](../022_reruns_impl-013_stg_netsuite2__account_types.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第443–455行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__account_types.sql`；原件第1–11行。

```sql
   1: WITH source_data AS (
   2:     SELECT
   3:     TRY_CAST(r."internalid" AS BIGINT) AS account_type_id,
   4:     TRY_CAST(r."longname" AS VARCHAR) AS type_name,
   5:     CASE WHEN lower(trim(cast(r."balancesheet" AS VARCHAR))) IN ('true','t','1','yes','y') THEN TRUE WHEN lower(trim(cast(r."balancesheet" AS VARCHAR))) IN ('false','f','0','no','n') THEN FALSE ELSE TRY_CAST(r."balancesheet" AS BOOLEAN) END AS is_balancesheet,
   6:     CASE WHEN lower(trim(cast(r."left" AS VARCHAR))) IN ('true','t','1','yes','y') THEN TRUE WHEN lower(trim(cast(r."left" AS VARCHAR))) IN ('false','f','0','no','n') THEN FALSE ELSE TRY_CAST(r."left" AS BOOLEAN) END AS is_leftside
   7:     FROM raw.netsuite2_account_type_data r
   8: )
   9: SELECT *
  10: FROM source_data
  11: WHERE account_type_id IS NOT NULL
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/staging/stg_netsuite2__account_types.sql`；原件第1–20行。

```sql
   1: with base as (
   2:     select distinct
   3:         longname as type_name,
   4:         "left" as is_leftside,
   5:         balancesheet as is_balancesheet
   6:     from raw.netsuite2_account_type_data
   7:     -- Removed date_deleted filter for mock data OR date_deleted = ''
   8: ),
   9: 
  10: final as (
  11:     select 
  12:         row_number() over (order by type_name) as account_type_id,
  13:         type_name,
  14:         case when is_balancesheet = 'T' then true else false end as is_balancesheet,
  15:         case when is_leftside = 'T' then true else false end as is_leftside
  16:     from base
  17: )
  18: 
  19: select *
  20: from final
```

## 3. agent看到的材料与不确定性

已检视该题全部67个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 11 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/11.json`。
- event 12 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/12.json`。

四档：**看到了但没提**。

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

## 4. 核实查询与诊断

核实查询共**3条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'raw.netsuite2_account_type_data' source_table,count(*) rows FROM raw.netsuite2_account_type_data
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ... 'raw.netsuite2_account_type_data' source_table,count(*) rows FROM raw.netsuite2_account_type_data\n                                                                    ^"}
```

### 核实 V2：两种type标识

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT internalid,longname,row_number() OVER(ORDER BY longname) ordered_id FROM raw.netsuite2_account_type_data ORDER BY internalid
```

```json
{"columns": ["internalid", "longname", "ordered_id"], "result": [[1, "Bank", 3], [2, "Accounts Receivable", 2], [3, "Fixed Asset", 7], [4, "Accounts Payable", 1], [5, "Equity", 5], [6, "Income", 8], [7, "Expense", 6], [8, "Cost of Goods Sold", 4]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'raw.netsuite2_account_type_data' source_table,count(*) source_rows FROM raw.netsuite2_account_type_data
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.netsuite2_account_type_data", 8]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["account_type_id"]`；比较列：`["account_type_id", "is_balancesheet", "is_leftside", "type_name"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 8/8 | 0/0 | 0/0 | 6 | 6 | 12 | False |
| L1 | 8/8 | 0/0 | 0/0 | 6 | 6 | 12 | False |
| L2 | 8/8 | 0/0 | 0/0 | 6 | 6 | 12 | False |
| L3 | 8/8 | 0/0 | 0/0 | 6 | 6 | 12 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_type_id | 0 | 0 | 0 | 0 |
| is_balancesheet | 2 | 2 | 2 | 2 |
| is_leftside | 4 | 4 | 4 | 4 |
| type_name | 6 | 6 | 6 | 6 |

### baseline

SQL：`data/022_work/impl-013_stg_netsuite2__account_types/baseline.sql`；SHA-256：`63dc63092a2f91a2b467aa4316947b2767d9b921f09d02b49d21fe34a1eb62b4`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 8/8 | 0/0 | 0/0 | 6 | 6 | 12 | False |
| L1 | 8/8 | 0/0 | 0/0 | 6 | 6 | 12 | False |
| L2 | 8/8 | 0/0 | 0/0 | 6 | 6 | 12 | False |
| L3 | 8/8 | 0/0 | 0/0 | 6 | 6 | 12 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_type_id | 0 | 0 | 0 | 0 |
| is_balancesheet | 2 | 2 | 2 | 2 |
| is_leftside | 4 | 4 | 4 | 4 |
| type_name | 6 | 6 | 6 | 6 |

### type_key

SQL：`data/022_work/impl-013_stg_netsuite2__account_types/type_key.sql`；SHA-256：`ff40b39a13f912bee0cddabb7af05cc9a44e21b3011ca6a2af9943aba8380aac`。

替换offset=37，原表达式所在行约3（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
TRY_CAST(r."internalid" AS BIGINT)
-- 新
row_number() OVER (ORDER BY r."longname")
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 8/8 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 8/8 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 8/8 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 8/8 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_type_id | 0 | 0 | 0 | 0 |
| is_balancesheet | 0 | 0 | 0 | 0 |
| is_leftside | 0 | 0 | 0 | 0 |
| type_name | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：type_key；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- type_key：A；主项。契约未给account_type_id生成规则；internalid与按名称row_number两种标识。（行减少6，格减少12）

## 规则问题

无。按v2冻结定义执行。
