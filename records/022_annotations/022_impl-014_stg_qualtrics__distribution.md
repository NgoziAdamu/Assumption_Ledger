# impl-014 / stg_qualtrics__distribution（全量；v2）

## 1. 差异与结论

四列时间戳解析格式未规定，四个单项各改3000格，同类A。

主要原因：**A**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| timestamp_created_at | A | 0 | 3000 |
| timestamp_last_modified_at | A | 0 | 3000 |
| timestamp_send_at | A | 0 | 3000 |
| timestamp_survey_link_expires_at | A | 0 | 3000 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_stg_qualtrics__distribution.md](../../records/022_packages/022_impl-014_stg_qualtrics__distribution.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_stg_qualtrics__distribution/022_impl-014_stg_qualtrics__distribution.json`。
- 比较结果：[022_reruns_impl-014_stg_qualtrics__distribution.json](../022_reruns_impl-014_stg_qualtrics__distribution.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第384–436行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__distribution.sql`；原件第1–40行。

```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."id" AS VARCHAR) AS distribution_id,
   4:         try_strptime(cast(src."created_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS created_at,
   5:         try_cast(src."header_from_email" AS VARCHAR) AS header_from_email,
   6:         try_cast(src."header_from_name" AS VARCHAR) AS header_from_name,
   7:         try_cast(src."header_reply_to_email" AS VARCHAR) AS header_reply_to_email,
   8:         try_cast(src."header_subject" AS VARCHAR) AS header_subject,
   9:         try_cast(src."message_library_id" AS BIGINT) AS message_library_id,
  10:         try_cast(src."message_message_id" AS BIGINT) AS message_id,
  11:         try_cast(src."message_message_text" AS VARCHAR) AS message_text,
  12:         try_strptime(cast(src."modified_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_modified_at,
  13:         try_cast(src."organization_id" AS BIGINT) AS organization_id,
  14:         try_cast(src."owner_id" AS VARCHAR) AS owner_user_id,
  15:         try_cast(src."parent_distribution_id" AS VARCHAR) AS parent_distribution_id,
  16:         try_cast(src."recipient_contact_id" AS VARCHAR) AS recipient_contact_id,
  17:         try_cast(src."recipient_library_id" AS BIGINT) AS recipient_library_id,
  18:         try_cast(src."recipient_mailing_list_id" AS VARCHAR) AS recipient_mailing_list_id,
  19:         try_cast(src."recipient_sample_id" AS BIGINT) AS recipient_sample_id,
  20:         try_cast(src."request_status" AS VARCHAR) AS request_status,
  21:         try_cast(src."request_type" AS VARCHAR) AS request_type,
  22:         try_strptime(cast(src."send_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS send_at,
  23:         try_strptime(cast(src."survey_link_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS survey_link_expires_at,
  24:         try_cast(src."survey_link_link_type" AS VARCHAR) AS survey_link_type,
  25:         try_cast(src."survey_link_survey_id" AS VARCHAR) AS survey_id
  26:     FROM raw.distribution AS src
  27: ),
  28: validated_rows AS (
  29:     SELECT *
  30:     FROM source_rows
  31:     WHERE 1 = 1
  32:       AND distribution_id IS NOT NULL
  33: ),
  34: deduplicated_rows AS (
  35:     SELECT *
  36:     FROM validated_rows
  37:     QUALIFY row_number() OVER (PARTITION BY distribution_id ORDER BY distribution_id) = 1
  38: )
  39: SELECT *
  40: FROM deduplicated_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__distribution.sql`；原件第1–59行。

```sql
   1: -- DuckDB-compatible staging model for distribution table
   2: -- Converted from dbt stg_qualtrics__distribution.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_distribution_data as (
   6:     select
   7:         id as distribution_id,
   8:         try_cast(created_date as timestamp) as created_at,
   9:         lower(trim(header_from_email)) as header_from_email,
  10:         trim(header_from_name) as header_from_name,
  11:         lower(trim(header_reply_to_email)) as header_reply_to_email,
  12:         trim(header_subject) as header_subject,
  13:         cast(message_library_id as bigint) as message_library_id,
  14:         cast(message_message_id as bigint) as message_id,
  15:         cast(message_message_text as varchar) as message_text,
  16:         try_cast(modified_date as timestamp) as last_modified_at,
  17:         cast(organization_id as bigint) as organization_id,
  18:         trim(owner_id) as owner_user_id,
  19:         trim(parent_distribution_id) as parent_distribution_id,
  20:         trim(recipient_contact_id) as recipient_contact_id,
  21:         cast(recipient_library_id as bigint) as recipient_library_id,
  22:         trim(recipient_mailing_list_id) as recipient_mailing_list_id,
  23:         cast(recipient_sample_id as bigint) as recipient_sample_id,
  24:         trim(request_status) as request_status,
  25:         trim(request_type) as request_type,
  26:         try_cast(send_date as timestamp) as send_at,
  27:         try_cast(survey_link_expiration_date as timestamp) as survey_link_expires_at,
  28:         trim(survey_link_link_type) as survey_link_type,
  29:         trim(survey_link_survey_id) as survey_id
  30:     from raw.distribution
  31:     where id is not null  -- Basic primary key validation
  32: )
  33: 
  34: select
  35:     distribution_id,
  36:     created_at,
  37:     header_from_email,
  38:     header_from_name,
  39:     header_reply_to_email,
  40:     header_subject,
  41:     message_library_id,
  42:     message_id,
  43:     message_text,
  44:     last_modified_at,
  45:     organization_id,
  46:     owner_user_id,
  47:     parent_distribution_id,
  48:     recipient_contact_id,
  49:     recipient_library_id,
  50:     recipient_mailing_list_id,
  51:     recipient_sample_id,
  52:     request_status,
  53:     request_type,
  54:     send_at,
  55:     survey_link_expires_at,
  56:     survey_link_type,
  57:     survey_id
  58: from validated_distribution_data
  59: where distribution_id is not null
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
SELECT 'raw.distribution' source_table,count(*) rows FROM raw.distribution
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.distribution' source_table,count(*) rows FROM raw.distribution\n                                                        ^"}
```

### 核实 V2：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "id",count(*) n FROM raw.distribution GROUP BY "id")
```

```json
{"error": "Parser Error: syntax error at or near \"groups\"\n\nLINE 1: SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n...\n                        ^"}
```

### 核实 V3：两种时间解析

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'created_date' field,count(*) n,count(try_cast("created_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("created_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.distribution UNION ALL SELECT 'modified_date' field,count(*) n,count(try_cast("modified_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("modified_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.distribution UNION ALL SELECT 'send_date' field,count(*) n,count(try_cast("send_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("send_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.distribution UNION ALL SELECT 'survey_link_expiration_date' field,count(*) n,count(try_cast("survey_link_expiration_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("survey_link_expiration_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.distribution
```

```json
{"columns": ["field", "n", "direct_parsed", "format_parsed"], "result": [["created_date", 3000, 0, 3000], ["modified_date", 3000, 0, 3000], ["send_date", 3000, 0, 3000], ["survey_link_expiration_date", 3000, 0, 3000]]}
```

### 核实 V4：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.distribution' source_table,count(*) source_rows FROM raw.distribution
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.distribution", 3000]]}
```

### 核实 V5：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) key_groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "id",count(*) n FROM raw.distribution GROUP BY "id")
```

```json
{"columns": ["key_groups", "duplicate_groups", "excess"], "result": [[3000, 0, 0]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["distribution_id"]`；比较列：`["created_at", "distribution_id", "header_from_email", "header_from_name", "header_reply_to_email", "header_subject", "last_modified_at", "message_id", "message_library_id", "message_text", "organization_id", "owner_user_id", "parent_distribution_id", "recipient_contact_id", "recipient_library_id", "recipient_mailing_list_id", "recipient_sample_id", "request_status", "request_type", "send_at", "survey_id", "survey_link_expires_at", "survey_link_type"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |
| L1 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |
| L2 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |
| L3 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | 0 |
| created_at | 3000 | 3000 | 3000 | 3000 |
| header_from_email | 0 | 0 | 0 | 0 |
| header_from_name | 0 | 0 | 0 | 0 |
| header_reply_to_email | 0 | 0 | 0 | 0 |
| header_subject | 0 | 0 | 0 | 0 |
| last_modified_at | 3000 | 3000 | 3000 | 3000 |
| message_id | 0 | 0 | 0 | 0 |
| message_library_id | 0 | 0 | 0 | 0 |
| message_text | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |
| parent_distribution_id | 0 | 0 | 0 | 0 |
| recipient_contact_id | 0 | 0 | 0 | 0 |
| recipient_library_id | 0 | 0 | 0 | 0 |
| recipient_mailing_list_id | 0 | 0 | 0 | 0 |
| recipient_sample_id | 0 | 0 | 0 | 0 |
| request_status | 0 | 0 | 0 | 0 |
| request_type | 0 | 0 | 0 | 0 |
| send_at | 3000 | 3000 | 3000 | 3000 |
| survey_id | 0 | 0 | 0 | 0 |
| survey_link_expires_at | 3000 | 3000 | 3000 | 3000 |
| survey_link_type | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-014_stg_qualtrics__distribution/baseline.sql`；SHA-256：`55a1a3c4a02d493d3b00a8dbd00046c864b26de867bd5dc47ec14ce041d7fbb2`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |
| L1 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |
| L2 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |
| L3 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | 0 |
| created_at | 3000 | 3000 | 3000 | 3000 |
| header_from_email | 0 | 0 | 0 | 0 |
| header_from_name | 0 | 0 | 0 | 0 |
| header_reply_to_email | 0 | 0 | 0 | 0 |
| header_subject | 0 | 0 | 0 | 0 |
| last_modified_at | 3000 | 3000 | 3000 | 3000 |
| message_id | 0 | 0 | 0 | 0 |
| message_library_id | 0 | 0 | 0 | 0 |
| message_text | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |
| parent_distribution_id | 0 | 0 | 0 | 0 |
| recipient_contact_id | 0 | 0 | 0 | 0 |
| recipient_library_id | 0 | 0 | 0 | 0 |
| recipient_mailing_list_id | 0 | 0 | 0 | 0 |
| recipient_sample_id | 0 | 0 | 0 | 0 |
| request_status | 0 | 0 | 0 | 0 |
| request_type | 0 | 0 | 0 | 0 |
| send_at | 3000 | 3000 | 3000 | 3000 |
| survey_id | 0 | 0 | 0 | 0 |
| survey_link_expires_at | 3000 | 3000 | 3000 | 3000 |
| survey_link_type | 0 | 0 | 0 | 0 |

### preserve_duplicates

SQL：`data/022_work/impl-014_stg_qualtrics__distribution/preserve_duplicates.sql`；SHA-256：`050c85f90f096f02ee5ebcf7ec01b32c68c406c017fca94217e464d676e468d9`。

替换offset=2116，原表达式所在行约37（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY distribution_id ORDER BY distribution_id) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |
| L1 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |
| L2 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |
| L3 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 12000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | 0 |
| created_at | 3000 | 3000 | 3000 | 3000 |
| header_from_email | 0 | 0 | 0 | 0 |
| header_from_name | 0 | 0 | 0 | 0 |
| header_reply_to_email | 0 | 0 | 0 | 0 |
| header_subject | 0 | 0 | 0 | 0 |
| last_modified_at | 3000 | 3000 | 3000 | 3000 |
| message_id | 0 | 0 | 0 | 0 |
| message_library_id | 0 | 0 | 0 | 0 |
| message_text | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |
| parent_distribution_id | 0 | 0 | 0 | 0 |
| recipient_contact_id | 0 | 0 | 0 | 0 |
| recipient_library_id | 0 | 0 | 0 | 0 |
| recipient_mailing_list_id | 0 | 0 | 0 | 0 |
| recipient_sample_id | 0 | 0 | 0 | 0 |
| request_status | 0 | 0 | 0 | 0 |
| request_type | 0 | 0 | 0 | 0 |
| send_at | 3000 | 3000 | 3000 | 3000 |
| survey_id | 0 | 0 | 0 | 0 |
| survey_link_expires_at | 3000 | 3000 | 3000 | 3000 |
| survey_link_type | 0 | 0 | 0 | 0 |

### timestamp_created_at

SQL：`data/022_work/impl-014_stg_qualtrics__distribution/timestamp_created_at.sql`；SHA-256：`afdd8dee4b8106642d171e1df7ed72810a9e14e3e9f50f8eaf41dff71707f557`。

替换offset=99，原表达式所在行约4（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(cast(src."created_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS created_at
-- 新
try_cast(src."created_date" AS TIMESTAMP) AS created_at
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L1 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L2 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L3 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | 0 |
| created_at | 0 | 0 | 0 | 0 |
| header_from_email | 0 | 0 | 0 | 0 |
| header_from_name | 0 | 0 | 0 | 0 |
| header_reply_to_email | 0 | 0 | 0 | 0 |
| header_subject | 0 | 0 | 0 | 0 |
| last_modified_at | 3000 | 3000 | 3000 | 3000 |
| message_id | 0 | 0 | 0 | 0 |
| message_library_id | 0 | 0 | 0 | 0 |
| message_text | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |
| parent_distribution_id | 0 | 0 | 0 | 0 |
| recipient_contact_id | 0 | 0 | 0 | 0 |
| recipient_library_id | 0 | 0 | 0 | 0 |
| recipient_mailing_list_id | 0 | 0 | 0 | 0 |
| recipient_sample_id | 0 | 0 | 0 | 0 |
| request_status | 0 | 0 | 0 | 0 |
| request_type | 0 | 0 | 0 | 0 |
| send_at | 3000 | 3000 | 3000 | 3000 |
| survey_id | 0 | 0 | 0 | 0 |
| survey_link_expires_at | 3000 | 3000 | 3000 | 3000 |
| survey_link_type | 0 | 0 | 0 | 0 |

### timestamp_last_modified_at

SQL：`data/022_work/impl-014_stg_qualtrics__distribution/timestamp_last_modified_at.sql`；SHA-256：`d31fe857c486eb3abf84822039f638393cf9a6609719c8ed0e92eca21df7a0f0`。

替换offset=727，原表达式所在行约12（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(cast(src."modified_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_modified_at
-- 新
try_cast(src."modified_date" AS TIMESTAMP) AS last_modified_at
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L1 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L2 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L3 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | 0 |
| created_at | 3000 | 3000 | 3000 | 3000 |
| header_from_email | 0 | 0 | 0 | 0 |
| header_from_name | 0 | 0 | 0 | 0 |
| header_reply_to_email | 0 | 0 | 0 | 0 |
| header_subject | 0 | 0 | 0 | 0 |
| last_modified_at | 0 | 0 | 0 | 0 |
| message_id | 0 | 0 | 0 | 0 |
| message_library_id | 0 | 0 | 0 | 0 |
| message_text | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |
| parent_distribution_id | 0 | 0 | 0 | 0 |
| recipient_contact_id | 0 | 0 | 0 | 0 |
| recipient_library_id | 0 | 0 | 0 | 0 |
| recipient_mailing_list_id | 0 | 0 | 0 | 0 |
| recipient_sample_id | 0 | 0 | 0 | 0 |
| request_status | 0 | 0 | 0 | 0 |
| request_type | 0 | 0 | 0 | 0 |
| send_at | 3000 | 3000 | 3000 | 3000 |
| survey_id | 0 | 0 | 0 | 0 |
| survey_link_expires_at | 3000 | 3000 | 3000 | 3000 |
| survey_link_type | 0 | 0 | 0 | 0 |

### timestamp_send_at

SQL：`data/022_work/impl-014_stg_qualtrics__distribution/timestamp_send_at.sql`；SHA-256：`bdb9633ef6c7507fd2cb20d86d61de6a0104096a6620129d8e02ab0d98365554`。

替换offset=1526，原表达式所在行约22（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(cast(src."send_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS send_at
-- 新
try_cast(src."send_date" AS TIMESTAMP) AS send_at
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L1 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L2 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L3 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | 0 |
| created_at | 3000 | 3000 | 3000 | 3000 |
| header_from_email | 0 | 0 | 0 | 0 |
| header_from_name | 0 | 0 | 0 | 0 |
| header_reply_to_email | 0 | 0 | 0 | 0 |
| header_subject | 0 | 0 | 0 | 0 |
| last_modified_at | 3000 | 3000 | 3000 | 3000 |
| message_id | 0 | 0 | 0 | 0 |
| message_library_id | 0 | 0 | 0 | 0 |
| message_text | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |
| parent_distribution_id | 0 | 0 | 0 | 0 |
| recipient_contact_id | 0 | 0 | 0 | 0 |
| recipient_library_id | 0 | 0 | 0 | 0 |
| recipient_mailing_list_id | 0 | 0 | 0 | 0 |
| recipient_sample_id | 0 | 0 | 0 | 0 |
| request_status | 0 | 0 | 0 | 0 |
| request_type | 0 | 0 | 0 | 0 |
| send_at | 0 | 0 | 0 | 0 |
| survey_id | 0 | 0 | 0 | 0 |
| survey_link_expires_at | 3000 | 3000 | 3000 | 3000 |
| survey_link_type | 0 | 0 | 0 | 0 |

### timestamp_survey_link_expires_at

SQL：`data/022_work/impl-014_stg_qualtrics__distribution/timestamp_survey_link_expires_at.sql`；SHA-256：`4c9b77d5e1262b3c7319df0723073b2483e0bb800c6c61ee80ae45ebfde20515`。

替换offset=1631，原表达式所在行约23（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(cast(src."survey_link_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS survey_link_expires_at
-- 新
try_cast(src."survey_link_expiration_date" AS TIMESTAMP) AS survey_link_expires_at
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L1 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L2 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |
| L3 | 3000/3000 | 0/0 | 0/0 | 3000 | 3000 | 9000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | 0 |
| created_at | 3000 | 3000 | 3000 | 3000 |
| header_from_email | 0 | 0 | 0 | 0 |
| header_from_name | 0 | 0 | 0 | 0 |
| header_reply_to_email | 0 | 0 | 0 | 0 |
| header_subject | 0 | 0 | 0 | 0 |
| last_modified_at | 3000 | 3000 | 3000 | 3000 |
| message_id | 0 | 0 | 0 | 0 |
| message_library_id | 0 | 0 | 0 | 0 |
| message_text | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |
| parent_distribution_id | 0 | 0 | 0 | 0 |
| recipient_contact_id | 0 | 0 | 0 | 0 |
| recipient_library_id | 0 | 0 | 0 | 0 |
| recipient_mailing_list_id | 0 | 0 | 0 | 0 |
| recipient_sample_id | 0 | 0 | 0 | 0 |
| request_status | 0 | 0 | 0 | 0 |
| request_type | 0 | 0 | 0 | 0 |
| send_at | 3000 | 3000 | 3000 | 3000 |
| survey_id | 0 | 0 | 0 | 0 |
| survey_link_expires_at | 0 | 0 | 0 | 0 |
| survey_link_type | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

未达到/不适用；本表没有U归因。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- preserve_duplicates：O；单修未满足本表所选尺度的参与门槛。契约primary_key/unique；gold未去重。（行减少0，格减少0）
- timestamp_created_at：A；主项。契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。（行减少0，格减少3000）
- timestamp_last_modified_at：A；主项。契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。（行减少0，格减少3000）
- timestamp_send_at：A；主项。契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。（行减少0，格减少3000）
- timestamp_survey_link_expires_at：A；主项。契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。（行减少0，格减少3000）

## 规则问题

无。按v2冻结定义执行。
