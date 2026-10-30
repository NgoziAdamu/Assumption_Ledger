# impl-014 | staging | stg_qualtrics__survey | 差异：S1；日期 原记录

## 契约完整原文

S3:91–147

```yaml
    - name: stg_qualtrics__survey
      description: "Cleaned survey metadata including configuration settings, ownership, and lifecycle information"
      source_table: "raw.survey"
      primary_key: ["survey_id"]
      columns:
        - name: survey_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: survey_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: survey_status
          data_type: VARCHAR
          constraints: [not_null]
        - name: brand_base_url
          data_type: VARCHAR
        - name: brand_id
          data_type: VARCHAR
        - name: bundle_short_name
          data_type: DOUBLE
        - name: composition_type
          data_type: DOUBLE
        - name: auto_scoring_category
          data_type: DOUBLE
        - name: default_scoring_category
          data_type: DOUBLE
        - name: division_id
          data_type: BIGINT
        - name: creator_user_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: owner_user_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: project_category
          data_type: VARCHAR
        - name: project_type
          data_type: VARCHAR
        - name: registry_sha
          data_type: DOUBLE
        - name: registry_version
          data_type: DOUBLE
        - name: schema_version
          data_type: DOUBLE
        - name: scoring_summary_after_questions
          data_type: BOOLEAN
        - name: scoring_summary_after_survey
          data_type: BOOLEAN
        - name: scoring_summary_category
          data_type: DOUBLE
        - name: last_accessed_at
          data_type: TIMESTAMP
        - name: last_activated_at
          data_type: TIMESTAMP
        - name: last_modified_at
          data_type: TIMESTAMP

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        try_cast(src."id" AS VARCHAR) AS survey_id,
        try_cast(src."survey_name" AS VARCHAR) AS survey_name,
        try_cast(src."survey_status" AS VARCHAR) AS survey_status,
        try_cast(src."brand_base_url" AS VARCHAR) AS brand_base_url,
        try_cast(src."brand_id" AS VARCHAR) AS brand_id,
        try_cast(src."bundle_short_name" AS DOUBLE) AS bundle_short_name,
        try_cast(src."composition_type" AS DOUBLE) AS composition_type,
        try_cast(src."auto_scoring_category" AS DOUBLE) AS auto_scoring_category,
        try_cast(src."default_scoring_category" AS DOUBLE) AS default_scoring_category,
        try_cast(src."division_id" AS BIGINT) AS division_id,
        try_cast(src."creator_id" AS VARCHAR) AS creator_user_id,
        try_cast(src."owner_id" AS VARCHAR) AS owner_user_id,
        try_cast(src."project_category" AS VARCHAR) AS project_category,
        try_cast(src."project_type" AS VARCHAR) AS project_type,
        try_cast(src."registry_sha" AS DOUBLE) AS registry_sha,
        try_cast(src."registry_version" AS DOUBLE) AS registry_version,
        try_cast(src."schema_version" AS DOUBLE) AS schema_version,
        try_cast(src."scoring_summary_after_questions" AS BOOLEAN) AS scoring_summary_after_questions,
        try_cast(src."scoring_summary_after_survey" AS BOOLEAN) AS scoring_summary_after_survey,
        try_cast(src."scoring_summary_category" AS DOUBLE) AS scoring_summary_category,
        try_strptime(cast(src."last_accessed" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_accessed_at,
        try_strptime(cast(src."last_activated" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_activated_at,
        try_strptime(cast(src."last_modified" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_modified_at
    FROM raw.survey AS src
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE 1 = 1
      AND survey_id IS NOT NULL AND survey_name IS NOT NULL AND survey_status IS NOT NULL AND creator_user_id IS NOT NULL AND owner_user_id IS NOT NULL
      AND survey_id IS NOT NULL
),
deduplicated_rows AS (
    SELECT *
    FROM validated_rows
    QUALIFY row_number() OVER (PARTITION BY survey_id ORDER BY survey_id) = 1
)
SELECT *
FROM deduplicated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- DuckDB-compatible staging model for survey table
-- Converted from dbt stg_qualtrics__survey.sql
-- Implements validation rules and data quality transformations per staging_data_specification.yaml

with validated_survey_data as (
    select
        id as survey_id,
        -- Required field validation
        case
            when survey_name is not null and trim(survey_name) != ''
            then survey_name
            else null
        end as survey_name,
        case
            when survey_status is not null and trim(survey_status) != ''
            then survey_status
            else null
        end as survey_status,
        brand_base_url,
        brand_id,
        cast(bundle_short_name as double) as bundle_short_name,
        cast(composition_type as double) as composition_type,
        cast(auto_scoring_category as double) as auto_scoring_category,
        cast(default_scoring_category as double) as default_scoring_category,
        cast(division_id as bigint) as division_id,
        -- Required field validation
        case
            when creator_id is not null and trim(creator_id) != ''
            then creator_id
            else null
        end as creator_user_id,
        case
            when owner_id is not null and trim(owner_id) != ''
            then owner_id
            else null
        end as owner_user_id,
        project_category,
        project_type,
        cast(registry_sha as double) as registry_sha,
        cast(registry_version as double) as registry_version,
        cast(schema_version as double) as schema_version,
        cast(scoring_summary_after_questions as boolean) as scoring_summary_after_questions,
        cast(scoring_summary_after_survey as boolean) as scoring_summary_after_survey,
        cast(scoring_summary_category as double) as scoring_summary_category,
        try_cast(last_accessed as timestamp) as last_accessed_at,
        try_cast(last_activated as timestamp) as last_activated_at,
        try_cast(last_modified as timestamp) as last_modified_at
    from raw.survey
    where id is not null  -- Primary key validation
)

select
    survey_id,
    survey_name,
    survey_status,
    brand_base_url,
    brand_id,
    bundle_short_name,
    composition_type,
    auto_scoring_category,
    default_scoring_category,
    division_id,
    creator_user_id,
    owner_user_id,
    project_category,
    project_type,
    registry_sha,
    registry_version,
    schema_version,
    scoring_summary_after_questions,
    scoring_summary_after_survey,
    scoring_summary_category,
    last_accessed_at,
    last_activated_at,
    last_modified_at
from validated_survey_data
where survey_id is not null
  and survey_name is not null  -- Required field
  and survey_status is not null  -- Required field
  and creator_user_id is not null  -- Required field
  and owner_user_id is not null  -- Required field
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 6000 | 6000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"survey_id":"sur10000000431"}</code> |
| K2 | <code>{"survey_id":"sur10000000903"}</code> |
| K3 | <code>{"survey_id":"sur10000001484"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| survey_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| survey_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| survey_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| brand_base_url | 0 | 0 | 0 | VARCHAR | VARCHAR |
| brand_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| bundle_short_name | 0 | 0 | 0 | DOUBLE | DOUBLE |
| composition_type | 0 | 0 | 0 | DOUBLE | DOUBLE |
| auto_scoring_category | 0 | 0 | 0 | DOUBLE | DOUBLE |
| default_scoring_category | 0 | 0 | 0 | DOUBLE | DOUBLE |
| division_id | 0 | 0 | 0 | BIGINT | BIGINT |
| creator_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| project_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| project_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| registry_sha | 0 | 0 | 0 | DOUBLE | DOUBLE |
| registry_version | 0 | 0 | 0 | DOUBLE | DOUBLE |
| schema_version | 0 | 0 | 0 | DOUBLE | DOUBLE |
| scoring_summary_after_questions | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| scoring_summary_after_survey | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| scoring_summary_category | 0 | 0 | 0 | DOUBLE | DOUBLE |
| last_accessed_at | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| last_activated_at | 6000 | 6000 | 6000 | TIMESTAMP | TIMESTAMP |
| last_modified_at | 6000 | 6000 | 6000 | TIMESTAMP | TIMESTAMP |

last_activated_at 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2025-04-09 08:08:01.202 | null |
| K2 | 2025-08-26 06:49:30.114 | null |
| K3 | 2025-03-30 18:59:07.797 | null |

last_modified_at 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2025-07-03 15:50:11.124 | null |
| K2 | 2025-06-17 01:47:59.576 | null |
| K3 | 2025-08-28 07:02:55.784 | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"last_accessed_at","table_rows":6000}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=3；task_instruction_not_agent_report       business_logic: '- Load all survey fields from staging.stg_qualtrics__survey unchanged; NULLs, casing, and whitespace are preserved.</code> |

## 轨迹索引（不放输出原文）

本题事件总数：81；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 2649 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9208 | false | false |
| 11 | run | <code>sed -n '1,180p' qualtrics_start.yaml</code> | 4629 | false | false |
| 13 | run | <code>find sql -maxdepth 3 -type f -printf '%p %s bytes\n'; sed -n '180,420p' qualtrics_start.yaml; sed -n '180,380p' run.py; wc -l docs/data_contract.yaml</code> | 11247 | false | false |
| 19 | run | <code>cat &gt; /tmp/gen_stg.py &lt;&lt;'PY'<br>import yaml, pathlib<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>colmaps={<br>'user':{'user_id':'id','account_created_at':'account_creation_date','account_expires_at':'</code> | 0 | false | false |
| 21 | run | <code>cat &gt; sql/intermediate/int_qualtrics__survey_performance.sql &lt;&lt;'SQL'<br>WITH response_aggregates AS (<br>    SELECT<br>        survey_id,<br>        count(DISTINCT response_id) AS total_responses,<br>        count(D</code> | 0 | false | false |
| 25 | run | <code>cat &gt; sql/intermediate/int_qualtrics__survey.sql &lt;&lt;'SQL'<br>WITH latest_version AS (<br>    SELECT *<br>    FROM staging.stg_qualtrics__survey_version<br>    WHERE is_published IS TRUE<br>),<br>previous_versions AS (<br> </code> | 0 | false | false |
| 33 | run | <code>cat &gt; sql/marts/qualtrics__response.sql &lt;&lt;'SQL'<br>WITH rollup_contacts AS (<br>    SELECT<br>        email,<br>        max(first_name) AS first_name,<br>        max(last_name) AS last_name,<br>        max(email_domain</code> | 0 | false | false |
| 35 | run | <code>cat &gt; /tmp/gen_survey_mart.py &lt;&lt;'PY'<br>from pathlib import Path<br>c=yaml.safe_load(open('docs/data_contract.yaml')) if False else None<br>base='survey_id survey_name survey_status brand_base_url brand_id bun</code> | 0 | false | false |
| 73 | run | <code>cat &gt; /workspace/result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 Qualtrics SQL 数据管道，按 **staging → intermediate → marts** 顺序实现，共创建 36 个 DuckDB SQL 文件：19 个 s</code> | 115 | false | false |
| 75 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 Qualtrics SQL 数据管道，按 **staging → intermediate → marts** 顺序实现，共创建 36</code> | 82 | false | false |
| 77 | run | <code>pwd; ls -ld / /home /workspace 2&gt;&amp;1; touch result.md &amp;&amp; cat &gt; result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 Qualtrics SQL 数据管道，按 **staging → intermediate</code> | 1637 | false | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
 if name=='stg_qualtrics__survey': sql+="      AND survey_id IS NOT NULL AND survey_name IS NOT NULL AND survey_status IS NOT NULL AND creator_user_id IS NOT NULL AND owner_user_id IS NOT NULL\n"
```
event 21 / message

```text
    FROM staging.stg_qualtrics__survey AS survey
```
event 25 / message

```text
FROM staging.stg_qualtrics__survey AS survey
```
event 33 / message

```text
LEFT JOIN staging.stg_qualtrics__survey AS survey
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-014.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__survey.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__survey.sql`
- S6: `records/006_contract_impl-014.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/result.md`
- S10: `data/022_packages_work/022_impl-014_stg_qualtrics__survey/022_impl-014_stg_qualtrics__survey.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions`
