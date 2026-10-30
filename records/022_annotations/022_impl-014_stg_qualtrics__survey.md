# impl-014 / stg_qualtrics__survey（全量；v2）

## 1. 差异与结论

last_activated_at/last_modified_at两列各6000格解析差异，契约未指定偏移解析表达式，同类A；last_accessed_at及去重单修无贡献。本表是survey，不是试标survey_version。

主要原因：**A**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| timestamp_last_activated_at | A | 0 | 6000 |
| timestamp_last_modified_at | A | 0 | 6000 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_stg_qualtrics__survey.md](../../records/022_packages/022_impl-014_stg_qualtrics__survey.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_stg_qualtrics__survey/022_impl-014_stg_qualtrics__survey.json`。
- 比较结果：[022_reruns_impl-014_stg_qualtrics__survey.json](../022_reruns_impl-014_stg_qualtrics__survey.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第91–147行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__survey.sql`；原件第1–41行。

```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."id" AS VARCHAR) AS survey_id,
   4:         try_cast(src."survey_name" AS VARCHAR) AS survey_name,
   5:         try_cast(src."survey_status" AS VARCHAR) AS survey_status,
   6:         try_cast(src."brand_base_url" AS VARCHAR) AS brand_base_url,
   7:         try_cast(src."brand_id" AS VARCHAR) AS brand_id,
   8:         try_cast(src."bundle_short_name" AS DOUBLE) AS bundle_short_name,
   9:         try_cast(src."composition_type" AS DOUBLE) AS composition_type,
  10:         try_cast(src."auto_scoring_category" AS DOUBLE) AS auto_scoring_category,
  11:         try_cast(src."default_scoring_category" AS DOUBLE) AS default_scoring_category,
  12:         try_cast(src."division_id" AS BIGINT) AS division_id,
  13:         try_cast(src."creator_id" AS VARCHAR) AS creator_user_id,
  14:         try_cast(src."owner_id" AS VARCHAR) AS owner_user_id,
  15:         try_cast(src."project_category" AS VARCHAR) AS project_category,
  16:         try_cast(src."project_type" AS VARCHAR) AS project_type,
  17:         try_cast(src."registry_sha" AS DOUBLE) AS registry_sha,
  18:         try_cast(src."registry_version" AS DOUBLE) AS registry_version,
  19:         try_cast(src."schema_version" AS DOUBLE) AS schema_version,
  20:         try_cast(src."scoring_summary_after_questions" AS BOOLEAN) AS scoring_summary_after_questions,
  21:         try_cast(src."scoring_summary_after_survey" AS BOOLEAN) AS scoring_summary_after_survey,
  22:         try_cast(src."scoring_summary_category" AS DOUBLE) AS scoring_summary_category,
  23:         try_strptime(cast(src."last_accessed" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_accessed_at,
  24:         try_strptime(cast(src."last_activated" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_activated_at,
  25:         try_strptime(cast(src."last_modified" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_modified_at
  26:     FROM raw.survey AS src
  27: ),
  28: validated_rows AS (
  29:     SELECT *
  30:     FROM source_rows
  31:     WHERE 1 = 1
  32:       AND survey_id IS NOT NULL AND survey_name IS NOT NULL AND survey_status IS NOT NULL AND creator_user_id IS NOT NULL AND owner_user_id IS NOT NULL
  33:       AND survey_id IS NOT NULL
  34: ),
  35: deduplicated_rows AS (
  36:     SELECT *
  37:     FROM validated_rows
  38:     QUALIFY row_number() OVER (PARTITION BY survey_id ORDER BY survey_id) = 1
  39: )
  40: SELECT *
  41: FROM deduplicated_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__survey.sql`；原件第1–81行。

```sql
   1: -- DuckDB-compatible staging model for survey table
   2: -- Converted from dbt stg_qualtrics__survey.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_survey_data as (
   6:     select
   7:         id as survey_id,
   8:         -- Required field validation
   9:         case
  10:             when survey_name is not null and trim(survey_name) != ''
  11:             then survey_name
  12:             else null
  13:         end as survey_name,
  14:         case
  15:             when survey_status is not null and trim(survey_status) != ''
  16:             then survey_status
  17:             else null
  18:         end as survey_status,
  19:         brand_base_url,
  20:         brand_id,
  21:         cast(bundle_short_name as double) as bundle_short_name,
  22:         cast(composition_type as double) as composition_type,
  23:         cast(auto_scoring_category as double) as auto_scoring_category,
  24:         cast(default_scoring_category as double) as default_scoring_category,
  25:         cast(division_id as bigint) as division_id,
  26:         -- Required field validation
  27:         case
  28:             when creator_id is not null and trim(creator_id) != ''
  29:             then creator_id
  30:             else null
  31:         end as creator_user_id,
  32:         case
  33:             when owner_id is not null and trim(owner_id) != ''
  34:             then owner_id
  35:             else null
  36:         end as owner_user_id,
  37:         project_category,
  38:         project_type,
  39:         cast(registry_sha as double) as registry_sha,
  40:         cast(registry_version as double) as registry_version,
  41:         cast(schema_version as double) as schema_version,
  42:         cast(scoring_summary_after_questions as boolean) as scoring_summary_after_questions,
  43:         cast(scoring_summary_after_survey as boolean) as scoring_summary_after_survey,
  44:         cast(scoring_summary_category as double) as scoring_summary_category,
  45:         try_cast(last_accessed as timestamp) as last_accessed_at,
  46:         try_cast(last_activated as timestamp) as last_activated_at,
  47:         try_cast(last_modified as timestamp) as last_modified_at
  48:     from raw.survey
  49:     where id is not null  -- Primary key validation
  50: )
  51: 
  52: select
  53:     survey_id,
  54:     survey_name,
  55:     survey_status,
  56:     brand_base_url,
  57:     brand_id,
  58:     bundle_short_name,
  59:     composition_type,
  60:     auto_scoring_category,
  61:     default_scoring_category,
  62:     division_id,
  63:     creator_user_id,
  64:     owner_user_id,
  65:     project_category,
  66:     project_type,
  67:     registry_sha,
  68:     registry_version,
  69:     schema_version,
  70:     scoring_summary_after_questions,
  71:     scoring_summary_after_survey,
  72:     scoring_summary_category,
  73:     last_accessed_at,
  74:     last_activated_at,
  75:     last_modified_at
  76: from validated_survey_data
  77: where survey_id is not null
  78:   and survey_name is not null  -- Required field
  79:   and survey_status is not null  -- Required field
  80:   and creator_user_id is not null  -- Required field
  81:   and owner_user_id is not null  -- Required field
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
SELECT 'raw.survey' source_table,count(*) rows FROM raw.survey
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.survey' source_table,count(*) rows FROM raw.survey\n                                                  ^"}
```

### 核实 V2：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "id",count(*) n FROM raw.survey GROUP BY "id")
```

```json
{"error": "Parser Error: syntax error at or near \"groups\"\n\nLINE 1: SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n...\n                        ^"}
```

### 核实 V3：两种时间解析

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'last_accessed' field,count(*) n,count(try_cast("last_accessed" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("last_accessed" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.survey UNION ALL SELECT 'last_activated' field,count(*) n,count(try_cast("last_activated" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("last_activated" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.survey UNION ALL SELECT 'last_modified' field,count(*) n,count(try_cast("last_modified" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("last_modified" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM raw.survey
```

```json
{"columns": ["field", "n", "direct_parsed", "format_parsed"], "result": [["last_accessed", 6000, 0, 0], ["last_activated", 6000, 0, 6000], ["last_modified", 6000, 0, 6000]]}
```

### 核实 V4：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.survey' source_table,count(*) source_rows FROM raw.survey
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.survey", 6000]]}
```

### 核实 V5：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) key_groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "id",count(*) n FROM raw.survey GROUP BY "id")
```

```json
{"columns": ["key_groups", "duplicate_groups", "excess"], "result": [[6000, 0, 0]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["survey_id"]`；比较列：`["auto_scoring_category", "brand_base_url", "brand_id", "bundle_short_name", "composition_type", "creator_user_id", "default_scoring_category", "division_id", "last_accessed_at", "last_activated_at", "last_modified_at", "owner_user_id", "project_category", "project_type", "registry_sha", "registry_version", "schema_version", "scoring_summary_after_questions", "scoring_summary_after_survey", "scoring_summary_category", "survey_id", "survey_name", "survey_status"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L1 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L2 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L3 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| survey_id | 0 | 0 | 0 | 0 |
| auto_scoring_category | 0 | 0 | 0 | 0 |
| brand_base_url | 0 | 0 | 0 | 0 |
| brand_id | 0 | 0 | 0 | 0 |
| bundle_short_name | 0 | 0 | 0 | 0 |
| composition_type | 0 | 0 | 0 | 0 |
| creator_user_id | 0 | 0 | 0 | 0 |
| default_scoring_category | 0 | 0 | 0 | 0 |
| division_id | 0 | 0 | 0 | 0 |
| last_accessed_at | 0 | 0 | 0 | 0 |
| last_activated_at | 6000 | 6000 | 6000 | 6000 |
| last_modified_at | 6000 | 6000 | 6000 | 6000 |
| owner_user_id | 0 | 0 | 0 | 0 |
| project_category | 0 | 0 | 0 | 0 |
| project_type | 0 | 0 | 0 | 0 |
| registry_sha | 0 | 0 | 0 | 0 |
| registry_version | 0 | 0 | 0 | 0 |
| schema_version | 0 | 0 | 0 | 0 |
| scoring_summary_after_questions | 0 | 0 | 0 | 0 |
| scoring_summary_after_survey | 0 | 0 | 0 | 0 |
| scoring_summary_category | 0 | 0 | 0 | 0 |
| survey_name | 0 | 0 | 0 | 0 |
| survey_status | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-014_stg_qualtrics__survey/baseline.sql`；SHA-256：`bdbb36b83200984cc291414811720c7e473df715ec3a78b0ca4421e9a16465aa`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L1 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L2 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L3 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| survey_id | 0 | 0 | 0 | 0 |
| auto_scoring_category | 0 | 0 | 0 | 0 |
| brand_base_url | 0 | 0 | 0 | 0 |
| brand_id | 0 | 0 | 0 | 0 |
| bundle_short_name | 0 | 0 | 0 | 0 |
| composition_type | 0 | 0 | 0 | 0 |
| creator_user_id | 0 | 0 | 0 | 0 |
| default_scoring_category | 0 | 0 | 0 | 0 |
| division_id | 0 | 0 | 0 | 0 |
| last_accessed_at | 0 | 0 | 0 | 0 |
| last_activated_at | 6000 | 6000 | 6000 | 6000 |
| last_modified_at | 6000 | 6000 | 6000 | 6000 |
| owner_user_id | 0 | 0 | 0 | 0 |
| project_category | 0 | 0 | 0 | 0 |
| project_type | 0 | 0 | 0 | 0 |
| registry_sha | 0 | 0 | 0 | 0 |
| registry_version | 0 | 0 | 0 | 0 |
| schema_version | 0 | 0 | 0 | 0 |
| scoring_summary_after_questions | 0 | 0 | 0 | 0 |
| scoring_summary_after_survey | 0 | 0 | 0 | 0 |
| scoring_summary_category | 0 | 0 | 0 | 0 |
| survey_name | 0 | 0 | 0 | 0 |
| survey_status | 0 | 0 | 0 | 0 |

### preserve_duplicates

SQL：`data/022_work/impl-014_stg_qualtrics__survey/preserve_duplicates.sql`；SHA-256：`a137e7caacfdd593efe7753d7cc7bc7a3ca375db2bdeaf628fdf8989640ebee0`。

替换offset=2179，原表达式所在行约38（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY survey_id ORDER BY survey_id) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L1 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L2 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L3 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| survey_id | 0 | 0 | 0 | 0 |
| auto_scoring_category | 0 | 0 | 0 | 0 |
| brand_base_url | 0 | 0 | 0 | 0 |
| brand_id | 0 | 0 | 0 | 0 |
| bundle_short_name | 0 | 0 | 0 | 0 |
| composition_type | 0 | 0 | 0 | 0 |
| creator_user_id | 0 | 0 | 0 | 0 |
| default_scoring_category | 0 | 0 | 0 | 0 |
| division_id | 0 | 0 | 0 | 0 |
| last_accessed_at | 0 | 0 | 0 | 0 |
| last_activated_at | 6000 | 6000 | 6000 | 6000 |
| last_modified_at | 6000 | 6000 | 6000 | 6000 |
| owner_user_id | 0 | 0 | 0 | 0 |
| project_category | 0 | 0 | 0 | 0 |
| project_type | 0 | 0 | 0 | 0 |
| registry_sha | 0 | 0 | 0 | 0 |
| registry_version | 0 | 0 | 0 | 0 |
| schema_version | 0 | 0 | 0 | 0 |
| scoring_summary_after_questions | 0 | 0 | 0 | 0 |
| scoring_summary_after_survey | 0 | 0 | 0 | 0 |
| scoring_summary_category | 0 | 0 | 0 | 0 |
| survey_name | 0 | 0 | 0 | 0 |
| survey_status | 0 | 0 | 0 | 0 |

### timestamp_last_accessed_at

SQL：`data/022_work/impl-014_stg_qualtrics__survey/timestamp_last_accessed_at.sql`；SHA-256：`9660ca8fe5535b179f9657e8390f6c2beba38fb670933d2f59080010cd2692f9`。

替换offset=1485，原表达式所在行约23（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(cast(src."last_accessed" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_accessed_at
-- 新
try_cast(src."last_accessed" AS TIMESTAMP) AS last_accessed_at
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L1 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L2 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |
| L3 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 12000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| survey_id | 0 | 0 | 0 | 0 |
| auto_scoring_category | 0 | 0 | 0 | 0 |
| brand_base_url | 0 | 0 | 0 | 0 |
| brand_id | 0 | 0 | 0 | 0 |
| bundle_short_name | 0 | 0 | 0 | 0 |
| composition_type | 0 | 0 | 0 | 0 |
| creator_user_id | 0 | 0 | 0 | 0 |
| default_scoring_category | 0 | 0 | 0 | 0 |
| division_id | 0 | 0 | 0 | 0 |
| last_accessed_at | 0 | 0 | 0 | 0 |
| last_activated_at | 6000 | 6000 | 6000 | 6000 |
| last_modified_at | 6000 | 6000 | 6000 | 6000 |
| owner_user_id | 0 | 0 | 0 | 0 |
| project_category | 0 | 0 | 0 | 0 |
| project_type | 0 | 0 | 0 | 0 |
| registry_sha | 0 | 0 | 0 | 0 |
| registry_version | 0 | 0 | 0 | 0 |
| schema_version | 0 | 0 | 0 | 0 |
| scoring_summary_after_questions | 0 | 0 | 0 | 0 |
| scoring_summary_after_survey | 0 | 0 | 0 | 0 |
| scoring_summary_category | 0 | 0 | 0 | 0 |
| survey_name | 0 | 0 | 0 | 0 |
| survey_status | 0 | 0 | 0 | 0 |

### timestamp_last_activated_at

SQL：`data/022_work/impl-014_stg_qualtrics__survey/timestamp_last_activated_at.sql`；SHA-256：`b8d04e70d302ef596b5dfb37874365d23f778f083be3dd5d2516e6b4560beb58`。

替换offset=1603，原表达式所在行约24（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(cast(src."last_activated" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_activated_at
-- 新
try_cast(src."last_activated" AS TIMESTAMP) AS last_activated_at
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 6000 | False |
| L1 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 6000 | False |
| L2 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 6000 | False |
| L3 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 6000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| survey_id | 0 | 0 | 0 | 0 |
| auto_scoring_category | 0 | 0 | 0 | 0 |
| brand_base_url | 0 | 0 | 0 | 0 |
| brand_id | 0 | 0 | 0 | 0 |
| bundle_short_name | 0 | 0 | 0 | 0 |
| composition_type | 0 | 0 | 0 | 0 |
| creator_user_id | 0 | 0 | 0 | 0 |
| default_scoring_category | 0 | 0 | 0 | 0 |
| division_id | 0 | 0 | 0 | 0 |
| last_accessed_at | 0 | 0 | 0 | 0 |
| last_activated_at | 0 | 0 | 0 | 0 |
| last_modified_at | 6000 | 6000 | 6000 | 6000 |
| owner_user_id | 0 | 0 | 0 | 0 |
| project_category | 0 | 0 | 0 | 0 |
| project_type | 0 | 0 | 0 | 0 |
| registry_sha | 0 | 0 | 0 | 0 |
| registry_version | 0 | 0 | 0 | 0 |
| schema_version | 0 | 0 | 0 | 0 |
| scoring_summary_after_questions | 0 | 0 | 0 | 0 |
| scoring_summary_after_survey | 0 | 0 | 0 | 0 |
| scoring_summary_category | 0 | 0 | 0 | 0 |
| survey_name | 0 | 0 | 0 | 0 |
| survey_status | 0 | 0 | 0 | 0 |

### timestamp_last_modified_at

SQL：`data/022_work/impl-014_stg_qualtrics__survey/timestamp_last_modified_at.sql`；SHA-256：`6a544b6354c0e2d57f652a3e066ff536fb3c8bcdbdba0a9900ae716ef423b6a3`。

替换offset=1723，原表达式所在行约25（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
try_strptime(cast(src."last_modified" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_modified_at
-- 新
try_cast(src."last_modified" AS TIMESTAMP) AS last_modified_at
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 6000 | False |
| L1 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 6000 | False |
| L2 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 6000 | False |
| L3 | 6000/6000 | 0/0 | 0/0 | 6000 | 6000 | 6000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| survey_id | 0 | 0 | 0 | 0 |
| auto_scoring_category | 0 | 0 | 0 | 0 |
| brand_base_url | 0 | 0 | 0 | 0 |
| brand_id | 0 | 0 | 0 | 0 |
| bundle_short_name | 0 | 0 | 0 | 0 |
| composition_type | 0 | 0 | 0 | 0 |
| creator_user_id | 0 | 0 | 0 | 0 |
| default_scoring_category | 0 | 0 | 0 | 0 |
| division_id | 0 | 0 | 0 | 0 |
| last_accessed_at | 0 | 0 | 0 | 0 |
| last_activated_at | 6000 | 6000 | 6000 | 6000 |
| last_modified_at | 0 | 0 | 0 | 0 |
| owner_user_id | 0 | 0 | 0 | 0 |
| project_category | 0 | 0 | 0 | 0 |
| project_type | 0 | 0 | 0 | 0 |
| registry_sha | 0 | 0 | 0 | 0 |
| registry_version | 0 | 0 | 0 | 0 |
| schema_version | 0 | 0 | 0 | 0 |
| scoring_summary_after_questions | 0 | 0 | 0 | 0 |
| scoring_summary_after_survey | 0 | 0 | 0 | 0 |
| scoring_summary_category | 0 | 0 | 0 | 0 |
| survey_name | 0 | 0 | 0 | 0 |
| survey_status | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：timestamp_last_activated_at,timestamp_last_modified_at；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- preserve_duplicates：O；单修未满足本表所选尺度的参与门槛。契约primary_key/unique；gold未去重。（行减少0，格减少0）
- timestamp_last_accessed_at：A；单修未满足本表所选尺度的参与门槛。契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。（行减少0，格减少0）
- timestamp_last_activated_at：A；主项。契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。（行减少0，格减少6000）
- timestamp_last_modified_at：A；主项。契约仅给TIMESTAMP类型，未规定offset字符串解析表达式；gold TRY_CAST全部NULL。（行减少0，格减少6000）

## 规则问题

无。按v2冻结定义执行。
