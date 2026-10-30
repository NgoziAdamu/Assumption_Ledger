# impl-013 / stg_netsuite2__classes（全量；v2）

## 1. 差异与结论

生成器已有class映射；因契约源表名与实际库不同先填全NULL，修复FROM后未刷新投影。显式映射意图与留存SQL不一致，I；不是无依据地推测想法。

主要原因：**I**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| placeholder_mapping | I | 100 | 500 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_stg_netsuite2__classes.md](../../records/022_packages/022_impl-013_stg_netsuite2__classes.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_stg_netsuite2__classes/022_impl-013_stg_netsuite2__classes.json`。
- 比较结果：[022_reruns_impl-013_stg_netsuite2__classes.json](../022_reruns_impl-013_stg_netsuite2__classes.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第330–344行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__classes.sql`；原件第1–12行。

```sql
   1: WITH source_data AS (
   2:     SELECT
   3:     CAST(NULL AS VARCHAR) AS class_id,
   4:     CAST(NULL AS VARCHAR) AS class_external_id,
   5:     CAST(NULL AS VARCHAR) AS name,
   6:     CAST(NULL AS VARCHAR) AS full_name,
   7:     CAST(NULL AS BOOLEAN) AS is_inactive
   8:     FROM raw.netsuite2_classification_data r
   9: )
  10: SELECT *
  11: FROM source_data
  12: WHERE class_id IS NOT NULL
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/staging/stg_netsuite2__classes.sql`；原件第1–18行。

```sql
   1: with base as (
   2:     select * 
   3:     from raw.netsuite2_classification_data
   4:     -- Removed date_deleted filter for mock data
   5: ),
   6: 
   7: final as (
   8:     select
   9:         id as class_id,
  10:         externalid as class_external_id,
  11:         name,
  12:         fullname as full_name,
  13:         isinactive = 'T' as is_inactive
  14:     from base
  15: )
  16: 
  17: select * 
  18: from final
```

## 3. agent看到的材料与不确定性

已检视该题全部67个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 11 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/11.json`。
- event 12 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/12.json`。
- event 23 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/23.json`。
- event 24 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/24.json`。
- event 25 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json`。

四档：**看到了但没提**。

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

I的明确意图证据：event15原始生成器包含本表源列字典；event24显示旧源名不存在的报错；event25仅将FROM改为实际源表，未重建SELECT投影。不是仅凭事后gold反推意图。

## 4. 核实查询与诊断

核实查询共**3条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'raw.netsuite2_classification_data' source_table,count(*) rows FROM raw.netsuite2_classification_data
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ... 'raw.netsuite2_classification_data' source_table,count(*) rows FROM raw.netsuite2_classification_data\n                                                                      ^"}
```

### 核实 V2：候选ID列

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT count(*) n,count(id) nonnull_ids,count(DISTINCT id) distinct_ids FROM raw.netsuite2_classification_data
```

```json
{"columns": ["n", "nonnull_ids", "distinct_ids"], "result": [[100, 100, 100]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'raw.netsuite2_classification_data' source_table,count(*) source_rows FROM raw.netsuite2_classification_data
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.netsuite2_classification_data", 100]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["class_id"]`；比较列：`["class_external_id", "class_id", "full_name", "is_inactive", "name"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 0/100 | 0/100 | 0/0 | 0 | 100 | 500 | False |
| L1 | 0/100 | 0/100 | 0/0 | 0 | 100 | 500 | False |
| L2 | 0/100 | 0/100 | 0/0 | 0 | 100 | 500 | False |
| L3 | 0/100 | 0/100 | 0/0 | 0 | 100 | 500 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| class_id | 0 | 0 | 0 | 0 |
| class_external_id | 0 | 0 | 0 | 0 |
| full_name | 0 | 0 | 0 | 0 |
| is_inactive | 0 | 0 | 0 | 0 |
| name | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_stg_netsuite2__classes/baseline.sql`；SHA-256：`f711e7d6b37096ed703e65ff549a61ef342b3b02ac156353a3f89aeb80157cde`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 0/100 | 0/100 | 0/0 | 0 | 100 | 500 | False |
| L1 | 0/100 | 0/100 | 0/0 | 0 | 100 | 500 | False |
| L2 | 0/100 | 0/100 | 0/0 | 0 | 100 | 500 | False |
| L3 | 0/100 | 0/100 | 0/0 | 0 | 100 | 500 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| class_id | 0 | 0 | 0 | 0 |
| class_external_id | 0 | 0 | 0 | 0 |
| full_name | 0 | 0 | 0 | 0 |
| is_inactive | 0 | 0 | 0 | 0 |
| name | 0 | 0 | 0 | 0 |

### placeholder_mapping

SQL：`data/022_work/impl-013_stg_netsuite2__classes/placeholder_mapping.sql`；SHA-256：`10d284d081d3327ff63fbeaaa92841e1a08eae119623791a402f0bea3466f7a6`。

替换offset=37，原表达式所在行约3（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS VARCHAR) AS class_id
-- 新
id AS class_id
```

替换offset=57，原表达式所在行约4（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS VARCHAR) AS class_external_id
-- 新
externalid AS class_external_id
```

替换offset=94，原表达式所在行约5（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS VARCHAR) AS name
-- 新
name AS name
```

替换offset=112，原表达式所在行约6（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS VARCHAR) AS full_name
-- 新
fullname AS full_name
```

替换offset=139，原表达式所在行约7（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS BOOLEAN) AS is_inactive
-- 新
isinactive = 'T' AS is_inactive
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 100/100 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 100/100 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 100/100 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 100/100 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| class_id | 0 | 0 | 0 | 0 |
| class_external_id | 0 | 0 | 0 | 0 |
| full_name | 0 | 0 | 0 | 0 |
| is_inactive | 0 | 0 | 0 | 0 |
| name | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：placeholder_mapping；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- placeholder_mapping：I；主项。event15生成器已写出正确列映射，因契约旧源名取不到raw schema而填NULL；event25只修FROM，忘记重生投影。明确实现意图与最终SQL不一致。（行减少100，格减少500）

## 规则问题

U（误判列不存在）、D（NULL占位）与I（修表名漏投影）边界：event15有正确列映射，event24报错，event25明确修源名，最终投影仍旧。因此选I，以代码证据支撑意图。
