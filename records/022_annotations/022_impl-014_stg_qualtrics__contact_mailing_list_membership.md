# impl-014 / stg_qualtrics__contact_mailing_list_membership（全量；v2）

## 1. 差异与结论

时间解析策略A主导7981个共同键差异；额外19条重复记录来自agent执行primary_key而gold保留。按本表行尺度去重单修不减（8000→8000），因此O不列参与因素，详列为非贡献差异。

主要原因：**A**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| timestamp_unsubscribed_at | A | 7981 | 8023 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_stg_qualtrics__contact_mailing_list_membership.md](../../records/022_packages/022_impl-014_stg_qualtrics__contact_mailing_list_membership.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_stg_qualtrics__contact_mailing_list_membership/022_impl-014_stg_qualtrics__contact_mailing_list_membership.json`。
- 比较结果：[022_reruns_impl-014_stg_qualtrics__contact_mailing_list_membership.json](../022_reruns_impl-014_stg_qualtrics__contact_mailing_list_membership.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第288–311行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__contact_mailing_list_membership.sql`；原件第1–26行。

```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."contact_id" AS VARCHAR) AS contact_id,
   4:         try_cast(src."contact_lookup_id" AS VARCHAR) AS contact_lookup_id,
   5:         try_cast(src."directory_id" AS VARCHAR) AS directory_id,
   6:         try_cast(src."mailing_list_id" AS VARCHAR) AS mailing_list_id,
   7:         try_cast(src."name" AS VARCHAR) AS name,
   8:         try_cast(src."owner_id" AS VARCHAR) AS owner_user_id,
   9:         try_strptime(cast(src."unsubscribe_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS unsubscribed_at,
  10:         try_cast(src."unsubscribed" AS BOOLEAN) AS is_unsubscribed
  11:     FROM raw.contact_mailing_list_membership AS src
  12: ),
  13: validated_rows AS (
  14:     SELECT *
  15:     FROM source_rows
  16:     WHERE 1 = 1
  17:       AND contact_id IS NOT NULL
  18:       AND mailing_list_id IS NOT NULL
  19: ),
  20: deduplicated_rows AS (
  21:     SELECT *
  22:     FROM validated_rows
  23:     QUALIFY row_number() OVER (PARTITION BY contact_id, mailing_list_id ORDER BY contact_id, mailing_list_id) = 1
  24: )
  25: SELECT *
  26: FROM deduplicated_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__contact_mailing_list_membership.sql`；原件第1–39行。

```sql
   1: -- DuckDB-compatible staging model for contact_mailing_list_membership table
   2: -- Converted from dbt stg_qualtrics__contact_mailing_list_membership.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_contact_mailing_list_data as (
   6:     select
   7:         -- Required field validation
   8:         case
   9:             when contact_id is not null and trim(contact_id) != ''
  10:             then contact_id
  11:             else null
  12:         end as contact_id,
  13:         contact_lookup_id,
  14:         directory_id,
  15:         -- Required field validation
  16:         case
  17:             when mailing_list_id is not null and trim(mailing_list_id) != ''
  18:             then mailing_list_id
  19:             else null
  20:         end as mailing_list_id,
  21:         name,
  22:         owner_id as owner_user_id,
  23:         try_cast(unsubscribe_date as timestamp) as unsubscribed_at,
  24:         cast(unsubscribed as boolean) as is_unsubscribed
  25:     from raw.contact_mailing_list_membership
  26: )
  27: 
  28: select
  29:     contact_id,
  30:     contact_lookup_id,
  31:     directory_id,
  32:     mailing_list_id,
  33:     name,
  34:     owner_user_id,
  35:     unsubscribed_at,
  36:     is_unsubscribed
  37: from validated_contact_mailing_list_data
  38: where contact_id is not null
  39:   and mailing_list_id is not null  -- Required fields for composite primary key
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
SELECT 'raw.contact_mailing_list_membership' source_table,count(*) rows FROM raw.contact_mailing_list_membership
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ... 'raw.contact_mailing_list_membership' source_table,count(*) rows FROM raw.contact_mailing_list_membership\n                                                                        ^"}
```

### 核实 V2：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "contact_id","mailing_list_id",count(*) n FROM raw.contact_mailing_list_membership GROUP BY "contact_id","mailing_list_id")
```

```json
{"error": "Parser Error: syntax error at or near \"groups\"\n\nLINE 1: SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n...\n                        ^"}
```

### 核实 V3：两种时间解析

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'unsubscribe_date' field,count(*) n,count(try_cast("unsubscribe_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("unsubscribe_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.contact_mailing_list_membership
```

```json
{"columns": ["field", "n", "direct_parsed", "format_parsed"], "result": [["unsubscribe_date", 8000, 0, 8000]]}
```

### 核实 V4：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.contact_mailing_list_membership' source_table,count(*) source_rows FROM raw.contact_mailing_list_membership
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.contact_mailing_list_membership", 8000]]}
```

### 核实 V5：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) key_groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "contact_id","mailing_list_id",count(*) n FROM raw.contact_mailing_list_membership GROUP BY "contact_id","mailing_list_id")
```

```json
{"columns": ["key_groups", "duplicate_groups", "excess"], "result": [[7981, 18, 19]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["contact_id", "mailing_list_id"]`；比较列：`["contact_id", "contact_lookup_id", "directory_id", "is_unsubscribed", "mailing_list_id", "name", "owner_user_id", "unsubscribed_at"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 7981/8000 | 0/0 | 0/19 | 7981 | 8000 | 8175 | False |
| L1 | 7981/8000 | 0/0 | 0/19 | 7981 | 8000 | 8175 | False |
| L2 | 7981/8000 | 0/0 | 0/19 | 7981 | 8000 | 8175 | False |
| L3 | 7981/8000 | 0/0 | 0/19 | 7981 | 8000 | 8175 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| contact_id | 0 | 0 | 0 | 0 |
| mailing_list_id | 0 | 0 | 0 | 0 |
| contact_lookup_id | 9 | 9 | 9 | 9 |
| directory_id | 9 | 9 | 9 | 9 |
| is_unsubscribed | 6 | 6 | 6 | 6 |
| name | 9 | 9 | 9 | 9 |
| owner_user_id | 9 | 9 | 9 | 9 |
| unsubscribed_at | 7981 | 7981 | 7981 | 7981 |

### baseline

SQL：`data/022_work/impl-014_stg_qualtrics__contact_mailing_list_membership/baseline.sql`；SHA-256：`abb1be4183137a84a6d3a754e2a4c3e0a9cf07e26a3b5ce82252a36e55f2e72c`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 7981/8000 | 0/0 | 0/19 | 7981 | 8000 | 8175 | False |
| L1 | 7981/8000 | 0/0 | 0/19 | 7981 | 8000 | 8175 | False |
| L2 | 7981/8000 | 0/0 | 0/19 | 7981 | 8000 | 8175 | False |
| L3 | 7981/8000 | 0/0 | 0/19 | 7981 | 8000 | 8175 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| contact_id | 0 | 0 | 0 | 0 |
| mailing_list_id | 0 | 0 | 0 | 0 |
| contact_lookup_id | 9 | 9 | 9 | 9 |
| directory_id | 9 | 9 | 9 | 9 |
| is_unsubscribed | 6 | 6 | 6 | 6 |
| name | 9 | 9 | 9 | 9 |
| owner_user_id | 9 | 9 | 9 | 9 |
| unsubscribed_at | 7981 | 7981 | 7981 | 7981 |

### preserve_duplicates

SQL：`data/022_work/impl-014_stg_qualtrics__contact_mailing_list_membership/preserve_duplicates.sql`；SHA-256：`11cedf8ac5b2a0fdf4db9f49d045d758f18bc25ae1e18e682c35a4bfc74b78b7`。

替换offset=862，原表达式所在行约23（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY contact_id, mailing_list_id ORDER BY contact_id, mailing_list_id) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 8000/8000 | 0/0 | 0/0 | 8000 | 8000 | 8000 | False |
| L1 | 8000/8000 | 0/0 | 0/0 | 8000 | 8000 | 8000 | False |
| L2 | 8000/8000 | 0/0 | 0/0 | 8000 | 8000 | 8000 | False |
| L3 | 8000/8000 | 0/0 | 0/0 | 8000 | 8000 | 8000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| contact_id | 0 | 0 | 0 | 0 |
| mailing_list_id | 0 | 0 | 0 | 0 |
| contact_lookup_id | 0 | 0 | 0 | 0 |
| directory_id | 0 | 0 | 0 | 0 |
| is_unsubscribed | 0 | 0 | 0 | 0 |
| name | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |
| unsubscribed_at | 8000 | 8000 | 8000 | 8000 |

### timestamp_unsubscribed_at

SQL：`data/022_work/impl-014_stg_qualtrics__contact_mailing_list_membership/timestamp_unsubscribed_at.sql`；SHA-256：`02a379f3b72f7e7867c5a49ab13b1f2f95e7f9a2762bb3fabb7a7da135130678`。

替换offset=424，原表达式所在行约9（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(cast(src."unsubscribe_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS unsubscribed_at
-- 新
try_cast(src."unsubscribe_date" AS TIMESTAMP) AS unsubscribed_at
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 7981/8000 | 0/0 | 0/19 | 0 | 19 | 152 | False |
| L1 | 7981/8000 | 0/0 | 0/19 | 0 | 19 | 152 | False |
| L2 | 7981/8000 | 0/0 | 0/19 | 0 | 19 | 152 | False |
| L3 | 7981/8000 | 0/0 | 0/19 | 0 | 19 | 152 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| contact_id | 0 | 0 | 0 | 0 |
| mailing_list_id | 0 | 0 | 0 | 0 |
| contact_lookup_id | 0 | 0 | 0 | 0 |
| directory_id | 0 | 0 | 0 | 0 |
| is_unsubscribed | 0 | 0 | 0 | 0 |
| name | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |
| unsubscribed_at | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：timestamp_unsubscribed_at；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- preserve_duplicates：O；单修未满足本表所选尺度的参与门槛。契约primary_key/unique；gold未去重。（行减少0，格减少175）
- timestamp_unsubscribed_at：A；主项。契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。（行减少7981，格减少8023）

## 规则问题

同一张表行口径能选主因时，不把只减少格子、行规模不减的去重差异另列参与因素；保留单改完整数字供复核。
