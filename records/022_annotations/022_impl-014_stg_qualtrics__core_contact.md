# impl-014 / stg_qualtrics__core_contact（全量；v2）

## 1. 差异与结论

契约contact_id主键；agent4994行，gold8000行，撤去重后全表L0一致，O。

主要原因：**O**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| preserve_duplicates | O | 3006 | 24048 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_stg_qualtrics__core_contact.md](../../records/022_packages/022_impl-014_stg_qualtrics__core_contact.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_stg_qualtrics__core_contact/022_impl-014_stg_qualtrics__core_contact.json`。
- 比较结果：[022_reruns_impl-014_stg_qualtrics__core_contact.json](../022_reruns_impl-014_stg_qualtrics__core_contact.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第525–549行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__core_contact.sql`；原件第1–26行。

```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."id" AS VARCHAR) AS contact_id,
   4:         try_cast(src."mailing_list_id" AS VARCHAR) AS mailing_list_id,
   5:         try_cast(src."first_name" AS VARCHAR) AS first_name,
   6:         try_cast(src."last_name" AS VARCHAR) AS last_name,
   7:         try_cast(src."email" AS VARCHAR) AS email,
   8:         CASE WHEN src."email" IS NOT NULL THEN lower(split_part(trim(src."email"), '@', 2)) ELSE NULL END AS email_domain,
   9:         try_cast(src."external_data_reference" AS VARCHAR) AS external_data_reference,
  10:         try_cast(src."language" AS VARCHAR) AS language,
  11:         try_cast(src."unsubscribed" AS BOOLEAN) AS is_unsubscribed
  12:     FROM raw.core_contact AS src
  13: ),
  14: validated_rows AS (
  15:     SELECT *
  16:     FROM source_rows
  17:     WHERE 1 = 1
  18:       AND contact_id IS NOT NULL
  19: ),
  20: deduplicated_rows AS (
  21:     SELECT *
  22:     FROM validated_rows
  23:     QUALIFY row_number() OVER (PARTITION BY contact_id ORDER BY contact_id) = 1
  24: )
  25: SELECT *
  26: FROM deduplicated_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__core_contact.sql`；原件第1–40行。

```sql
   1: -- DuckDB-compatible staging model for core_contact table
   2: -- Converted from dbt stg_qualtrics__core_contact.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_core_contact_data as (
   6:     select
   7:         id as contact_id,
   8:         mailing_list_id,
   9:         first_name,
  10:         last_name,
  11:         -- Email validation and normalization
  12:         case
  13:             when email is not null and trim(email) != ''
  14:             then lower(trim(email))
  15:             else null
  16:         end as email,
  17:         case
  18:             when email is not null and trim(email) != ''
  19:                  and email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
  20:             then split_part(email, '@', 2)
  21:             else null
  22:         end as email_domain,
  23:         external_data_reference,
  24:         language,
  25:         cast(unsubscribed as boolean) as is_unsubscribed
  26:     from raw.core_contact
  27: )
  28: 
  29: select
  30:     contact_id,
  31:     mailing_list_id,
  32:     first_name,
  33:     last_name,
  34:     email,
  35:     email_domain,
  36:     external_data_reference,
  37:     language,
  38:     is_unsubscribed
  39: from validated_core_contact_data
  40: where contact_id is not null  -- Primary key validation
```

## 3. agent看到的材料与不确定性

已检视该题全部81个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 79 / finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/79.json`。

四档：**只有通用策略说明**。

原句（见上述最终报告事件）：

```text
重复主键记录按主键仅保留一条；合同未指定冲突记录排序规则，因此非主键字段冲突时，具体保留行不保证业务优先级，可能丢失冲突值。
```

## 4. 核实查询与诊断

核实查询共**4条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.core_contact' source_table,count(*) rows FROM raw.core_contact
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.core_contact' source_table,count(*) rows FROM raw.core_contact\n                                                        ^"}
```

### 核实 V2：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "id",count(*) n FROM raw.core_contact GROUP BY "id")
```

```json
{"error": "Parser Error: syntax error at or near \"groups\"\n\nLINE 1: SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n...\n                        ^"}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.core_contact' source_table,count(*) source_rows FROM raw.core_contact
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.core_contact", 8000]]}
```

### 核实 V4：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) key_groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "id",count(*) n FROM raw.core_contact GROUP BY "id")
```

```json
{"columns": ["key_groups", "duplicate_groups", "excess"], "result": [[4994, 902, 3006]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["contact_id"]`；比较列：`["contact_id", "email", "external_data_reference", "first_name", "is_unsubscribed", "language", "last_name", "mailing_list_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4994/8000 | 0/0 | 0/3006 | 0 | 3006 | 24048 | False |
| L1 | 4994/8000 | 0/0 | 0/3006 | 0 | 3006 | 24048 | False |
| L2 | 4994/8000 | 0/0 | 0/3006 | 0 | 3006 | 24048 | False |
| L3 | 4994/8000 | 0/0 | 0/3006 | 0 | 3006 | 24048 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| contact_id | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| external_data_reference | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| is_unsubscribed | 0 | 0 | 0 | 0 |
| language | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| mailing_list_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-014_stg_qualtrics__core_contact/baseline.sql`；SHA-256：`c8d95598c53055861bcb3892c6c24b80e211eec512d7a9d93cbf54e89730ba73`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4994/8000 | 0/0 | 0/3006 | 0 | 3006 | 24048 | False |
| L1 | 4994/8000 | 0/0 | 0/3006 | 0 | 3006 | 24048 | False |
| L2 | 4994/8000 | 0/0 | 0/3006 | 0 | 3006 | 24048 | False |
| L3 | 4994/8000 | 0/0 | 0/3006 | 0 | 3006 | 24048 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| contact_id | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| external_data_reference | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| is_unsubscribed | 0 | 0 | 0 | 0 |
| language | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| mailing_list_id | 0 | 0 | 0 | 0 |

### preserve_duplicates

SQL：`data/022_work/impl-014_stg_qualtrics__core_contact/preserve_duplicates.sql`；SHA-256：`7e29632666f610e6093a5b37195972fffc762abecf9ed0ae22eb58bc118f49f5`。

替换offset=864，原表达式所在行约23（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY contact_id ORDER BY contact_id) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 8000/8000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 8000/8000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 8000/8000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 8000/8000 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| contact_id | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| external_data_reference | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| is_unsubscribed | 0 | 0 | 0 | 0 |
| language | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| mailing_list_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：preserve_duplicates；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- preserve_duplicates：O；主项。契约primary_key/unique；gold未去重。（行减少3006，格减少24048）

## 规则问题

无。按v2冻结定义执行。
