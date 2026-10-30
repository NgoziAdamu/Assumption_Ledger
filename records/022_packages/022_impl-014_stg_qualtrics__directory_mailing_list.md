# impl-014 | staging | stg_qualtrics__directory_mailing_list | 差异：S1；日期 原记录

## 契约完整原文

S3:506–524

```yaml
    - name: stg_qualtrics__directory_mailing_list
      description: "Directory-specific mailing lists"
      source_table: "raw.directory_mailing_list"
      primary_key: ["mailing_list_id"]
      columns:
        - name: mailing_list_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: created_at
          data_type: TIMESTAMP
        - name: directory_id
          data_type: VARCHAR
        - name: last_modified_at
          data_type: TIMESTAMP
        - name: name
          data_type: VARCHAR
        - name: owner_user_id
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        try_cast(src."id" AS VARCHAR) AS mailing_list_id,
        try_strptime(cast(src."creation_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS created_at,
        try_cast(src."directory_id" AS VARCHAR) AS directory_id,
        try_strptime(cast(src."last_modified_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_modified_at,
        try_cast(src."name" AS VARCHAR) AS name,
        try_cast(src."owner_id" AS VARCHAR) AS owner_user_id
    FROM raw.directory_mailing_list AS src
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE 1 = 1
      AND mailing_list_id IS NOT NULL
),
deduplicated_rows AS (
    SELECT *
    FROM validated_rows
    QUALIFY row_number() OVER (PARTITION BY mailing_list_id ORDER BY mailing_list_id) = 1
)
SELECT *
FROM deduplicated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- DuckDB-compatible staging model for directory_mailing_list table
-- Converted from dbt stg_qualtrics__directory_mailing_list.sql
-- Implements validation rules and data quality transformations per staging_data_specification.yaml

with validated_directory_mailing_list_data as (
    select
        id as mailing_list_id,
        try_cast(creation_date as timestamp) as created_at,
        trim(directory_id) as directory_id,
        try_cast(last_modified_date as timestamp) as last_modified_at,
        trim(name) as name,
        trim(owner_id) as owner_user_id
    from raw.directory_mailing_list
    where id is not null  -- Basic primary key validation
)

select
    mailing_list_id,
    created_at,
    directory_id,
    last_modified_at,
    name,
    owner_user_id
from validated_directory_mailing_list_data
where mailing_list_id is not null
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1000 | 1000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"mailing_list_id":"dml_003d4e86b27b"}</code> |
| K2 | <code>{"mailing_list_id":"dml_009fc005ca05"}</code> |
| K3 | <code>{"mailing_list_id":"dml_00b7385daf31"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| mailing_list_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_at | 1000 | 1000 | 1000 | TIMESTAMP | TIMESTAMP |
| directory_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_modified_at | 1000 | 1000 | 1000 | TIMESTAMP | TIMESTAMP |
| name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |

created_at 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2024-09-21 05:09:33.941 | null |
| K2 | 2024-12-27 19:05:26.835 | null |
| K3 | 2024-09-21 08:04:31.908 | null |

last_modified_at 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2025-07-16 19:05:02.92 | null |
| K2 | 2025-08-27 00:35:55.899 | null |
| K3 | 2025-07-09 15:11:37.038 | null |

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
| 11 | run | <code>sed -n '1,180p' qualtrics_start.yaml</code> | 4629 | false | false |
| 13 | run | <code>find sql -maxdepth 3 -type f -printf '%p %s bytes\n'; sed -n '180,420p' qualtrics_start.yaml; sed -n '180,380p' run.py; wc -l docs/data_contract.yaml</code> | 11247 | false | false |
| 19 | run | <code>cat &gt; /tmp/gen_stg.py &lt;&lt;'PY'<br>import yaml, pathlib<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>colmaps={<br>'user':{'user_id':'id','account_created_at':'account_creation_date','account_expires_at':'</code> | 0 | false | false |
| 29 | run | <code>cat &gt; sql/marts/qualtrics__contact.sql &lt;&lt;'SQL'<br>WITH distribution_response AS (<br>    SELECT<br>        distribution_contact.contact_id,<br>        distribution.survey_id,<br>        distribution_contact.sent_at,</code> | 0 | false | false |
| 31 | run | <code>cat &gt; /tmp/gen_distribution.py &lt;&lt;'PY'<br>from pathlib import Path<br>statuses='pending success error opened complaint skipped blocked failure unknown softbounce hardbounce surveystarted surveypartiallyfinis</code> | 0 | false | false |
| 39 | run | <code>python run.py &gt; /tmp/pipeline.log 2&gt;&amp;1; tail -100 /tmp/pipeline.log</code> | 6507 | true | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
    FROM staging.stg_qualtrics__directory_mailing_list
```
event 31 / message

```text
LEFT JOIN staging.stg_qualtrics__directory_mailing_list AS mailing_list
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-014.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__directory_mailing_list.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__directory_mailing_list.sql`
- S6: `records/006_contract_impl-014.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/result.md`
- S10: `data/022_packages_work/022_impl-014_stg_qualtrics__directory_mailing_list/022_impl-014_stg_qualtrics__directory_mailing_list.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions`
