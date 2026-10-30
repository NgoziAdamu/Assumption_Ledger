# impl-014 / stg_qualtrics__user（全量；v2）

## 1. 差异与结论

契约先LOWER(TRIM)再邮箱验证；gold先验证原文而丢弃5个带空格邮箱。agent按契约顺序；变更验证对象后L0一致，O。

主要原因：**O**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| email_validation_order | O | 5 | 70 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_stg_qualtrics__user.md](../../records/022_packages/022_impl-014_stg_qualtrics__user.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_stg_qualtrics__user/022_impl-014_stg_qualtrics__user.json`。
- 比较结果：[022_reruns_impl-014_stg_qualtrics__user.json](../022_reruns_impl-014_stg_qualtrics__user.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第31–90行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__user.sql`；原件第1–38行。

```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."id" AS VARCHAR) AS user_id,
   4:         lower(trim(try_cast(src."email" AS VARCHAR))) AS email,
   5:         try_cast(src."first_name" AS VARCHAR) AS first_name,
   6:         try_cast(src."last_name" AS VARCHAR) AS last_name,
   7:         try_strptime(cast(src."account_creation_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS account_created_at,
   8:         CASE WHEN try_strptime(cast(src."account_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP IS NULL OR try_strptime(cast(src."account_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP > try_strptime(cast(src."account_creation_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP THEN try_strptime(cast(src."account_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP ELSE NULL END AS account_expires_at,
   9:         try_cast(src."account_status" AS VARCHAR) AS account_status,
  10:         try_cast(src."division_id" AS BIGINT) AS division_id,
  11:         try_cast(src."language" AS VARCHAR) AS language,
  12:         try_strptime(cast(src."last_login_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_login_at,
  13:         try_cast(src."organization_id" AS VARCHAR) AS organization_id,
  14:         try_strptime(cast(src."password_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS password_expires_at,
  15:         try_strptime(cast(src."password_last_changed_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS password_last_changed_at,
  16:         try_cast(src."response_count_auditable" AS DOUBLE) AS response_count_auditable,
  17:         try_cast(src."response_count_deleted" AS DOUBLE) AS response_count_deleted,
  18:         try_cast(src."response_count_generated" AS DOUBLE) AS response_count_generated,
  19:         try_cast(src."time_zone" AS VARCHAR) AS time_zone,
  20:         try_cast(src."unsubscribed" AS BOOLEAN) AS is_unsubscribed,
  21:         try_cast(src."user_type" AS VARCHAR) AS user_type,
  22:         try_cast(src."username" AS VARCHAR) AS username
  23:     FROM raw.user AS src
  24: ),
  25: validated_rows AS (
  26:     SELECT *
  27:     FROM source_rows
  28:     WHERE 1 = 1
  29:       AND user_id IS NOT NULL AND email IS NOT NULL AND regexp_matches(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') AND account_status IS NOT NULL AND account_status IN ('active','inactive','suspended','deleted','pending')
  30:       AND user_id IS NOT NULL
  31: ),
  32: deduplicated_rows AS (
  33:     SELECT *
  34:     FROM validated_rows
  35:     QUALIFY row_number() OVER (PARTITION BY user_id ORDER BY user_id) = 1
  36: )
  37: SELECT *
  38: FROM deduplicated_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__user.sql`；原件第1–72行。

```sql
   1: -- DuckDB-compatible staging model for user table
   2: -- Converted from dbt stg_qualtrics__user.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_user_data as (
   6:     select
   7:         id as user_id,
   8:         -- Email validation and normalization
   9:         case
  10:             when email is not null and trim(email) != ''
  11:                  and email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
  12:             then lower(trim(email))
  13:             else null
  14:         end as email,
  15:         first_name,
  16:         last_name,
  17:         try_cast(substr(account_creation_date, 1, 23) as timestamp) as account_created_at,
  18:         -- Account expires validation
  19:         case
  20:             when account_expiration_date is not null
  21:                  and try_cast(substr(account_expiration_date, 1, 23) as timestamp) > try_cast(substr(account_creation_date, 1, 23) as timestamp)
  22:             then try_cast(substr(account_expiration_date, 1, 23) as timestamp)
  23:             else null
  24:         end as account_expires_at,
  25:         -- Account status validation
  26:         case
  27:             when account_status in ('active', 'inactive', 'suspended', 'deleted', 'pending')
  28:             then account_status
  29:             else null  -- This will cause the row to be deleted below
  30:         end as account_status,
  31:         division_id,
  32:         language,
  33:         try_cast(substr(last_login_date, 1, 23) as timestamp) as last_login_at,
  34:         organization_id,
  35:         try_cast(substr(password_expiration_date, 1, 23) as timestamp) as password_expires_at,
  36:         try_cast(substr(password_last_changed_date, 1, 23) as timestamp) as password_last_changed_at,
  37:         cast(response_count_auditable as double) as response_count_auditable,
  38:         cast(response_count_deleted as double) as response_count_deleted,
  39:         cast(response_count_generated as double) as response_count_generated,
  40:         time_zone,
  41:         cast(unsubscribed as boolean) as is_unsubscribed,
  42:         user_type,
  43:         username
  44:     from raw.user
  45:     where id is not null  -- Basic primary key validation
  46: )
  47: 
  48: select
  49:     user_id,
  50:     email,
  51:     first_name,
  52:     last_name,
  53:     account_created_at,
  54:     account_expires_at,
  55:     account_status,
  56:     division_id,
  57:     language,
  58:     last_login_at,
  59:     organization_id,
  60:     password_expires_at,
  61:     password_last_changed_at,
  62:     response_count_auditable,
  63:     response_count_deleted,
  64:     response_count_generated,
  65:     time_zone,
  66:     is_unsubscribed,
  67:     user_type,
  68:     username
  69: from validated_user_data
  70: where user_id is not null
  71:   and email is not null  -- Essential field validation
  72:   and account_status is not null  -- Required field with validation
```

## 3. agent看到的材料与不确定性

已检视该题全部81个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 79 / finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/79.json`。

四档：**只有通用策略说明**。

原句（见上述最终报告事件）：

```text
缺失/无效关键 ID 及合同要求删除的非法状态、邮箱或必需字段记录予以剔除；非关键无效值置 NULL。
```

## 4. 核实查询与诊断

核实查询共**5条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.user' source_table,count(*) rows FROM raw.user
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.user' source_table,count(*) rows FROM raw.user\n                                                ^"}
```

### 核实 V2：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "id",count(*) n FROM raw.user GROUP BY "id")
```

```json
{"error": "Parser Error: syntax error at or near \"groups\"\n\nLINE 1: SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n...\n                        ^"}
```

### 核实 V3：两种时间解析

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'account_creation_date' field,count(*) n,count(try_cast("account_creation_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("account_creation_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.user UNION ALL SELECT 'last_login_date' field,count(*) n,count(try_cast("last_login_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("last_login_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.user UNION ALL SELECT 'password_expiration_date' field,count(*) n,count(try_cast("password_expiration_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("password_expiration_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.user UNION ALL SELECT 'password_last_changed_date' field,count(*) n,count(try_cast("password_last_changed_date" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("password_last_changed_date" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.user
```

```json
{"columns": ["field", "n", "direct_parsed", "format_parsed"], "result": [["account_creation_date", 2000, 0, 2000], ["last_login_date", 2000, 0, 2000], ["password_expiration_date", 2000, 0, 2000], ["password_last_changed_date", 2000, 0, 2000]]}
```

### 核实 V4：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.user' source_table,count(*) source_rows FROM raw.user
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.user", 2000]]}
```

### 核实 V5：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) key_groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "id",count(*) n FROM raw.user GROUP BY "id")
```

```json
{"columns": ["key_groups", "duplicate_groups", "excess"], "result": [[2000, 0, 0]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["user_id"]`；比较列：`["account_status", "division_id", "email", "first_name", "language", "last_name", "organization_id", "response_count_auditable", "response_count_deleted", "response_count_generated", "time_zone", "user_id", "user_type", "username"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |
| L1 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |
| L2 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |
| L3 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| user_id | 0 | 0 | 0 | 0 |
| account_status | 0 | 0 | 0 | 0 |
| division_id | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| language | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| response_count_auditable | 0 | 0 | 0 | 0 |
| response_count_deleted | 0 | 0 | 0 | 0 |
| response_count_generated | 0 | 0 | 0 | 0 |
| time_zone | 0 | 0 | 0 | 0 |
| user_type | 0 | 0 | 0 | 0 |
| username | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-014_stg_qualtrics__user/baseline.sql`；SHA-256：`2ed68458f8b97928946059f5874d448f910b979d6bcb0ff77f818060fa9382e2`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |
| L1 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |
| L2 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |
| L3 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| user_id | 0 | 0 | 0 | 0 |
| account_status | 0 | 0 | 0 | 0 |
| division_id | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| language | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| response_count_auditable | 0 | 0 | 0 | 0 |
| response_count_deleted | 0 | 0 | 0 | 0 |
| response_count_generated | 0 | 0 | 0 | 0 |
| time_zone | 0 | 0 | 0 | 0 |
| user_type | 0 | 0 | 0 | 0 |
| username | 0 | 0 | 0 | 0 |

### preserve_duplicates

SQL：`data/022_work/impl-014_stg_qualtrics__user/preserve_duplicates.sql`；SHA-256：`418767e2219f47309b0db8702efb2314800a8db511f7a40cd95c2bed7bd716b0`。

替换offset=2439，原表达式所在行约35（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY user_id ORDER BY user_id) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |
| L1 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |
| L2 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |
| L3 | 1987/1982 | 5/0 | 0/0 | 0 | 5 | 70 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| user_id | 0 | 0 | 0 | 0 |
| account_status | 0 | 0 | 0 | 0 |
| division_id | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| language | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| response_count_auditable | 0 | 0 | 0 | 0 |
| response_count_deleted | 0 | 0 | 0 | 0 |
| response_count_generated | 0 | 0 | 0 | 0 |
| time_zone | 0 | 0 | 0 | 0 |
| user_type | 0 | 0 | 0 | 0 |
| username | 0 | 0 | 0 | 0 |

### email_validation_order

SQL：`data/022_work/impl-014_stg_qualtrics__user/email_validation_order.sql`；SHA-256：`26033f7ade4ac6ccb8224e18a5a580545d17ebf4be163e72549a95179fe9fb13`。

替换offset=2165，原表达式所在行约29（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
regexp_matches(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
-- 新
user_id NOT IN (SELECT id FROM raw.user WHERE NOT regexp_full_match(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'))
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1982/1982 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 1982/1982 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 1982/1982 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 1982/1982 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| user_id | 0 | 0 | 0 | 0 |
| account_status | 0 | 0 | 0 | 0 |
| division_id | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| language | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| organization_id | 0 | 0 | 0 | 0 |
| response_count_auditable | 0 | 0 | 0 | 0 |
| response_count_deleted | 0 | 0 | 0 | 0 |
| response_count_generated | 0 | 0 | 0 | 0 |
| time_zone | 0 | 0 | 0 | 0 |
| user_type | 0 | 0 | 0 | 0 |
| username | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：email_validation_order；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- preserve_duplicates：O；单修未满足本表所选尺度的参与门槛。契约primary_key/unique；gold未去重。（行减少0，格减少0）
- email_validation_order：O；主项。契约先LOWER(TRIM)再验证，gold验证原文后trim，排除5个带空白邮箱。（行减少5，格减少70）

## 规则问题

无。按v2冻结定义执行。
