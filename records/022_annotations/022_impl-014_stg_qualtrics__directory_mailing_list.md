# impl-014 / stg_qualtrics__directory_mailing_list（全量；v2）

## 1. 差异与结论

两列时间戳解析格式未规定，agent格式解析、gold直接TRY_CAST得到NULL；各单改1000格，同类A。

主要原因：**A**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| timestamp_created_at | A | 0 | 1000 |
| timestamp_last_modified_at | A | 0 | 1000 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_stg_qualtrics__directory_mailing_list.md](../../records/022_packages/022_impl-014_stg_qualtrics__directory_mailing_list.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_stg_qualtrics__directory_mailing_list/022_impl-014_stg_qualtrics__directory_mailing_list.json`。
- 比较结果：[022_reruns_impl-014_stg_qualtrics__directory_mailing_list.json](../022_reruns_impl-014_stg_qualtrics__directory_mailing_list.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第506–524行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__directory_mailing_list.sql`；原件第1–23行。

```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."id" AS VARCHAR) AS mailing_list_id,
   4:         try_strptime(cast(src."creation_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS created_at,
   5:         try_cast(src."directory_id" AS VARCHAR) AS directory_id,
   6:         try_strptime(cast(src."last_modified_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_modified_at,
   7:         try_cast(src."name" AS VARCHAR) AS name,
   8:         try_cast(src."owner_id" AS VARCHAR) AS owner_user_id
   9:     FROM raw.directory_mailing_list AS src
  10: ),
  11: validated_rows AS (
  12:     SELECT *
  13:     FROM source_rows
  14:     WHERE 1 = 1
  15:       AND mailing_list_id IS NOT NULL
  16: ),
  17: deduplicated_rows AS (
  18:     SELECT *
  19:     FROM validated_rows
  20:     QUALIFY row_number() OVER (PARTITION BY mailing_list_id ORDER BY mailing_list_id) = 1
  21: )
  22: SELECT *
  23: FROM deduplicated_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__directory_mailing_list.sql`；原件第1–25行。

```sql
   1: -- DuckDB-compatible staging model for directory_mailing_list table
   2: -- Converted from dbt stg_qualtrics__directory_mailing_list.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_directory_mailing_list_data as (
   6:     select
   7:         id as mailing_list_id,
   8:         try_cast(creation_date as timestamp) as created_at,
   9:         trim(directory_id) as directory_id,
  10:         try_cast(last_modified_date as timestamp) as last_modified_at,
  11:         trim(name) as name,
  12:         trim(owner_id) as owner_user_id
  13:     from raw.directory_mailing_list
  14:     where id is not null  -- Basic primary key validation
  15: )
  16: 
  17: select
  18:     mailing_list_id,
  19:     created_at,
  20:     directory_id,
  21:     last_modified_at,
  22:     name,
  23:     owner_user_id
  24: from validated_directory_mailing_list_data
  25: where mailing_list_id is not null
```

## 3. agent看到的材料与不确定性

已检视该题全部81个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 79 / finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/79.json`。

四档：**只有通用策略说明**。

原句（见上述最终报告事件）：

```text
原始 Qualtrics 时间文本带时区后缀（例如 `+0800`），DuckDB 直接 `try_cast(... AS TIMESTAMP)` 无法解析。日期相关 SQL 改用 `try_strptime(..., '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP`；不可解析日期在日期计算中排除。
```

## 4. 核实查询与诊断

核实查询共**5条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.directory_mailing_list' source_table,count(*) rows FROM raw.directory_mailing_list
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.directory_mailing_list' source_table,count(*) rows FROM raw.directory_mailing_list\n                                                                  ^"}
```

### 核实 V2：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "id",count(*) n FROM raw.directory_mailing_list GROUP BY "id")
```

```json
{"error": "Parser Error: syntax error at or near \"groups\"\n\nLINE 1: SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n...\n                        ^"}
```

### 核实 V3：两种时间解析

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'creation_date' field,count(*) n,count(try_cast("creation_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("creation_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.directory_mailing_list UNION ALL SELECT 'last_modified_date' field,count(*) n,count(try_cast("last_modified_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("last_modified_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.directory_mailing_list
```

```json
{"columns": ["field", "n", "direct_parsed", "format_parsed"], "result": [["creation_date", 1000, 0, 1000], ["last_modified_date", 1000, 0, 1000]]}
```

### 核实 V4：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.directory_mailing_list' source_table,count(*) source_rows FROM raw.directory_mailing_list
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.directory_mailing_list", 1000]]}
```

### 核实 V5：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) key_groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "id",count(*) n FROM raw.directory_mailing_list GROUP BY "id")
```

```json
{"columns": ["key_groups", "duplicate_groups", "excess"], "result": [[1000, 0, 0]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["mailing_list_id"]`；比较列：`["created_at", "directory_id", "last_modified_at", "mailing_list_id", "name", "owner_user_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |
| L1 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |
| L2 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |
| L3 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| mailing_list_id | 0 | 0 | 0 | 0 |
| created_at | 1000 | 1000 | 1000 | 1000 |
| directory_id | 0 | 0 | 0 | 0 |
| last_modified_at | 1000 | 1000 | 1000 | 1000 |
| name | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-014_stg_qualtrics__directory_mailing_list/baseline.sql`；SHA-256：`275df312f03adc8ba75c74b76636eed57bb0fb8a035a066d94281b41bee8be9e`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |
| L1 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |
| L2 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |
| L3 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| mailing_list_id | 0 | 0 | 0 | 0 |
| created_at | 1000 | 1000 | 1000 | 1000 |
| directory_id | 0 | 0 | 0 | 0 |
| last_modified_at | 1000 | 1000 | 1000 | 1000 |
| name | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |

### preserve_duplicates

SQL：`data/022_work/impl-014_stg_qualtrics__directory_mailing_list/preserve_duplicates.sql`；SHA-256：`9e9d58920348e980cdf4204f43ddd6c227f39b87d56e501c4bd6d1add4a42c05`。

替换offset=718，原表达式所在行约20（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY mailing_list_id ORDER BY mailing_list_id) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |
| L1 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |
| L2 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |
| L3 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 2000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| mailing_list_id | 0 | 0 | 0 | 0 |
| created_at | 1000 | 1000 | 1000 | 1000 |
| directory_id | 0 | 0 | 0 | 0 |
| last_modified_at | 1000 | 1000 | 1000 | 1000 |
| name | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |

### timestamp_created_at

SQL：`data/022_work/impl-014_stg_qualtrics__directory_mailing_list/timestamp_created_at.sql`；SHA-256：`24c6b746c9b2389a1a99e9ee7f9f948a8515d6f0d0a09e2f8ef1edf6970bfd40`。

替换offset=99，原表达式所在行约4（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(cast(src."creation_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS created_at
-- 新
try_cast(src."creation_date" AS TIMESTAMP) AS created_at
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 1000 | False |
| L1 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 1000 | False |
| L2 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 1000 | False |
| L3 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 1000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| mailing_list_id | 0 | 0 | 0 | 0 |
| created_at | 0 | 0 | 0 | 0 |
| directory_id | 0 | 0 | 0 | 0 |
| last_modified_at | 1000 | 1000 | 1000 | 1000 |
| name | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |

### timestamp_last_modified_at

SQL：`data/022_work/impl-014_stg_qualtrics__directory_mailing_list/timestamp_last_modified_at.sql`；SHA-256：`fef5f58f0672b3debcd8466acd9af1dc15476a6eb5329ab8130f00e6a87726fc`。

替换offset=276，原表达式所在行约6（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(cast(src."last_modified_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_modified_at
-- 新
try_cast(src."last_modified_date" AS TIMESTAMP) AS last_modified_at
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 1000 | False |
| L1 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 1000 | False |
| L2 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 1000 | False |
| L3 | 1000/1000 | 0/0 | 0/0 | 1000 | 1000 | 1000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| mailing_list_id | 0 | 0 | 0 | 0 |
| created_at | 1000 | 1000 | 1000 | 1000 |
| directory_id | 0 | 0 | 0 | 0 |
| last_modified_at | 0 | 0 | 0 | 0 |
| name | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：timestamp_created_at,timestamp_last_modified_at；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- preserve_duplicates：O；单修未满足本表所选尺度的参与门槛。契约primary_key/unique；gold未去重。（行减少0，格减少0）
- timestamp_created_at：A；主项。契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。（行减少0，格减少1000）
- timestamp_last_modified_at：A；主项。契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。（行减少0，格减少1000）

## 规则问题

无。按v2冻结定义执行。
