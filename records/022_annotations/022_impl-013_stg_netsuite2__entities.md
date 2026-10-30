# impl-013 / stg_netsuite2__entities（全量；v2）

## 1. 差异与结论

生成器明列entity_id=id等映射；修复源名后仍NULL并被ID过滤成空。主导空表来自投影未刷新，I。附带entity_name映射意图的旧名称不同不影响本次主因证据。

主要原因：**I**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| placeholder_mapping | I | 700 | 4900 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_stg_netsuite2__entities.md](../../records/022_packages/022_impl-013_stg_netsuite2__entities.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_stg_netsuite2__entities/022_impl-013_stg_netsuite2__entities.json`。
- 比较结果：[022_reruns_impl-013_stg_netsuite2__entities.json](../022_reruns_impl-013_stg_netsuite2__entities.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第145–170行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql`；原件第1–17行。

```sql
   1: WITH source_data AS (
   2:     SELECT
   3:     CAST(NULL AS VARCHAR) AS entity_id,
   4:     CAST(NULL AS VARCHAR) AS parent_id,
   5:     CAST(NULL AS VARCHAR) AS entity_name,
   6:     CAST(NULL AS VARCHAR) AS entity_type,
   7:     CAST(NULL AS BOOLEAN) AS is_person,
   8:     CAST(NULL AS DOUBLE) AS contact_id,
   9:     CAST(NULL AS VARCHAR) AS customer_id,
  10:     CAST(NULL AS DOUBLE) AS employee_id,
  11:     CAST(NULL AS DOUBLE) AS job_id,
  12:     CAST(NULL AS DOUBLE) AS vendor_id
  13:     FROM raw.netsuite2_entities_data r
  14: )
  15: SELECT *
  16: FROM source_data
  17: WHERE entity_id IS NOT NULL
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql`；原件第1–23行。

```sql
   1: with base as (
   2:     select *
   3:     from raw.netsuite2_entities_data
   4:     -- Removed date_deleted filter for mock data
   5: ),
   6: 
   7: final as (
   8:     select
   9:         id as entity_id,
  10:         parent as parent_id,
  11:         entitytitle as entity_name,
  12:         type as entity_type,
  13:         isperson = 'T' as is_person,
  14:         try_cast(contact as double) as contact_id,
  15:         cast(customer as varchar) as customer_id,
  16:         try_cast(employee as double) as employee_id,
  17:         try_cast(project as double) as job_id,
  18:         try_cast(vendor as double) as vendor_id
  19:     from base
  20: )
  21: 
  22: select *
  23: from final
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
SELECT 'raw.netsuite2_entities_data' source_table,count(*) rows FROM raw.netsuite2_entities_data
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.netsuite2_entities_data' source_table,count(*) rows FROM raw.netsuite2_entities_data\n                                                                   ^"}
```

### 核实 V2：候选ID列

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT count(*) n,count(id) nonnull_ids,count(DISTINCT id) distinct_ids FROM raw.netsuite2_entities_data
```

```json
{"columns": ["n", "nonnull_ids", "distinct_ids"], "result": [[700, 700, 700]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'raw.netsuite2_entities_data' source_table,count(*) source_rows FROM raw.netsuite2_entities_data
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.netsuite2_entities_data", 700]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["entity_id"]`；比较列：`["customer_id", "employee_id", "entity_id", "entity_name", "entity_type", "job_id", "vendor_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 0/700 | 0/700 | 0/0 | 0 | 700 | 4900 | False |
| L1 | 0/700 | 0/700 | 0/0 | 0 | 700 | 4900 | False |
| L2 | 0/700 | 0/700 | 0/0 | 0 | 700 | 4900 | False |
| L3 | 0/700 | 0/700 | 0/0 | 0 | 700 | 4900 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| entity_id | 0 | 0 | 0 | 0 |
| customer_id | 0 | 0 | 0 | 0 |
| employee_id | 0 | 0 | 0 | 0 |
| entity_name | 0 | 0 | 0 | 0 |
| entity_type | 0 | 0 | 0 | 0 |
| job_id | 0 | 0 | 0 | 0 |
| vendor_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_stg_netsuite2__entities/baseline.sql`；SHA-256：`1e8241e8a238acb2aea104580dc60b307bb4dee018eb0d77a79cacbb7e45e1a7`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 0/700 | 0/700 | 0/0 | 0 | 700 | 4900 | False |
| L1 | 0/700 | 0/700 | 0/0 | 0 | 700 | 4900 | False |
| L2 | 0/700 | 0/700 | 0/0 | 0 | 700 | 4900 | False |
| L3 | 0/700 | 0/700 | 0/0 | 0 | 700 | 4900 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| entity_id | 0 | 0 | 0 | 0 |
| customer_id | 0 | 0 | 0 | 0 |
| employee_id | 0 | 0 | 0 | 0 |
| entity_name | 0 | 0 | 0 | 0 |
| entity_type | 0 | 0 | 0 | 0 |
| job_id | 0 | 0 | 0 | 0 |
| vendor_id | 0 | 0 | 0 | 0 |

### placeholder_mapping

SQL：`data/022_work/impl-013_stg_netsuite2__entities/placeholder_mapping.sql`；SHA-256：`8a57b268b8d0f80cf26cc50cd65cb3542cdc36cbb87710400f1c87864ca10e07`。

替换offset=37，原表达式所在行约3（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS VARCHAR) AS entity_id
-- 新
id AS entity_id
```

替换offset=58，原表达式所在行约4（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS VARCHAR) AS parent_id
-- 新
parent AS parent_id
```

替换offset=83，原表达式所在行约5（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS VARCHAR) AS entity_name
-- 新
entitytitle AS entity_name
```

替换offset=115，原表达式所在行约6（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS VARCHAR) AS entity_type
-- 新
type AS entity_type
```

替换offset=140，原表达式所在行约7（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS BOOLEAN) AS is_person
-- 新
isperson = 'T' AS is_person
```

替换offset=173，原表达式所在行约8（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS DOUBLE) AS contact_id
-- 新
try_cast(contact as double) AS contact_id
```

替换offset=220，原表达式所在行约9（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS VARCHAR) AS customer_id
-- 新
cast(customer as varchar) AS customer_id
```

替换offset=266，原表达式所在行约10（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS DOUBLE) AS employee_id
-- 新
try_cast(employee as double) AS employee_id
```

替换offset=315，原表达式所在行约11（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS DOUBLE) AS job_id
-- 新
try_cast(project as double) AS job_id
```

替换offset=358，原表达式所在行约12（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS DOUBLE) AS vendor_id
-- 新
try_cast(vendor as double) AS vendor_id
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 700/700 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 700/700 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 700/700 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 700/700 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| entity_id | 0 | 0 | 0 | 0 |
| customer_id | 0 | 0 | 0 | 0 |
| employee_id | 0 | 0 | 0 | 0 |
| entity_name | 0 | 0 | 0 | 0 |
| entity_type | 0 | 0 | 0 | 0 |
| job_id | 0 | 0 | 0 | 0 |
| vendor_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：placeholder_mapping；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- placeholder_mapping：I；主项。event15生成器已写出正确列映射，因契约旧源名取不到raw schema而填NULL；event25只修FROM，忘记重生投影。明确实现意图与最终SQL不一致。（行减少700，格减少4900）

## 规则问题

同classes，选择I。entity_name旧映射entityid与实际entitytitle另有差别；本次导致0行的主导机制是ID投影仍NULL，不能把整体恢复作为每一列映射独立正确的证明。
