# impl-014 | staging | stg_qualtrics__survey_version | 差异：S1；日期 原记录

## 契约完整原文

S3:632–657

```yaml
    - name: stg_qualtrics__survey_version
      description: "Survey version history and metadata"
      source_table: "raw.survey_version"
      primary_key: ["version_id"]
      columns:
        - name: version_id
          data_type: BIGINT
          constraints: [not_null, unique]
        - name: survey_id
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
        - name: version_description
          data_type: VARCHAR
        - name: is_published
          data_type: BOOLEAN
        - name: publisher_user_id
          data_type: VARCHAR
        - name: version_number
          data_type: BIGINT
        - name: was_published
          data_type: BOOLEAN

# --------------------------------------------------------------------------- #
# PHASE 2: Defines the business logic from staging tables to analytical models. #
# --------------------------------------------------------------------------- #
```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        try_cast(src."id" AS BIGINT) AS version_id,
        try_cast(src."survey_id" AS VARCHAR) AS survey_id,
        try_strptime(cast(src."creation_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS created_at,
        try_cast(src."description" AS VARCHAR) AS version_description,
        try_cast(src."published" AS BOOLEAN) AS is_published,
        try_cast(src."user_id" AS VARCHAR) AS publisher_user_id,
        try_cast(src."version_number" AS BIGINT) AS version_number,
        try_cast(src."was_published" AS BOOLEAN) AS was_published
    FROM raw.survey_version AS src
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE 1 = 1
      AND version_id IS NOT NULL
),
deduplicated_rows AS (
    SELECT *
    FROM validated_rows
    QUALIFY row_number() OVER (PARTITION BY version_id ORDER BY version_id) = 1
)
SELECT *
FROM deduplicated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- DuckDB-compatible staging model for survey_version table
-- Converted from dbt stg_qualtrics__survey_version.sql
-- Implements validation rules and data quality transformations per staging_data_specification.yaml

with validated_survey_version_data as (
    select
        id as version_id,
        try_cast(creation_date as timestamp) as created_at,
        trim(description) as version_description,
        cast(published as boolean) as is_published,
        trim(survey_id) as survey_id,
        trim(user_id) as publisher_user_id,
        cast(version_number as bigint) as version_number,
        cast(was_published as boolean) as was_published
    from raw.survey_version
    where id is not null  -- Basic primary key validation
)

select
    version_id,
    created_at,
    version_description,
    is_published,
    survey_id,
    publisher_user_id,
    version_number,
    was_published
from validated_survey_version_data
where version_id is not null
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 12000 | 12000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"version_id":"100030119"}</code> |
| K2 | <code>{"version_id":"100115705"}</code> |
| K3 | <code>{"version_id":"10015456"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| version_id | 0 | 0 | 0 | BIGINT | BIGINT |
| created_at | 12000 | 12000 | 12000 | TIMESTAMP | TIMESTAMP |
| version_description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_published | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| survey_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| publisher_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| version_number | 0 | 0 | 0 | BIGINT | BIGINT |
| was_published | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

created_at 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2025-06-28 14:13:35.322 | null |
| K2 | 2024-12-25 15:10:59.9 | null |
| K3 | 2025-07-27 01:48:21.157 | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

没有 True 痕迹。

## 轨迹索引（不放输出原文）

本题事件总数：81；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 2649 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9208 | false | false |
| 13 | run | <code>find sql -maxdepth 3 -type f -printf '%p %s bytes\n'; sed -n '180,420p' qualtrics_start.yaml; sed -n '180,380p' run.py; wc -l docs/data_contract.yaml</code> | 11247 | false | false |
| 19 | run | <code>cat &gt; /tmp/gen_stg.py &lt;&lt;'PY'<br>import yaml, pathlib<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>colmaps={<br>'user':{'user_id':'id','account_created_at':'account_creation_date','account_expires_at':'</code> | 0 | false | false |
| 25 | run | <code>cat &gt; sql/intermediate/int_qualtrics__survey.sql &lt;&lt;'SQL'<br>WITH latest_version AS (<br>    SELECT *<br>    FROM staging.stg_qualtrics__survey_version<br>    WHERE is_published IS TRUE<br>),<br>previous_versions AS (<br> </code> | 0 | false | false |

### agent action 的 thought/message 命中原句

event 25 / message

```text
    FROM staging.stg_qualtrics__survey_version
```
event 25 / message

```text
    FROM staging.stg_qualtrics__survey_version
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-014.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__survey_version.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__survey_version.sql`
- S6: `records/006_contract_impl-014.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/result.md`
- S10: `records/012_packages/012_impl-014_staging_stg_qualtrics__survey_version.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions`
