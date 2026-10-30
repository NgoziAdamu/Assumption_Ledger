# impl-014 | staging | stg_qualtrics__survey_embedded_data | 差异：S1；日期 原记录

## 契约完整原文

S3:455–470

```yaml
    - name: stg_qualtrics__survey_embedded_data
      description: "Survey embedded data for response tracking"
      source_table: "raw.survey_embedded_data"
      primary_key: ["response_id", "key"]
      columns:
        - name: import_id
          data_type: VARCHAR
        - name: key
          data_type: VARCHAR
          constraints: [not_null]
        - name: response_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: value
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        try_cast(src."import_id" AS VARCHAR) AS import_id,
        try_cast(src."key" AS VARCHAR) AS key,
        try_cast(src."response_id" AS VARCHAR) AS response_id,
        try_cast(src."value" AS VARCHAR) AS value
    FROM raw.survey_embedded_data AS src
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE 1 = 1
      AND response_id IS NOT NULL
      AND key IS NOT NULL
),
deduplicated_rows AS (
    SELECT *
    FROM validated_rows
    QUALIFY row_number() OVER (PARTITION BY response_id, key ORDER BY response_id, key) = 1
)
SELECT *
FROM deduplicated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- DuckDB-compatible staging model for survey_embedded_data table
-- Converted from dbt stg_qualtrics__survey_embedded_data.sql
-- Implements validation rules and data quality transformations per staging_data_specification.yaml

with validated_survey_embedded_data as (
    select
        trim(import_id) as import_id,
        trim(key) as key,
        trim(response_id) as response_id,
        trim(value) as value
    from raw.survey_embedded_data
    where response_id is not null
      and key is not null  -- Composite primary key validation
)

select
    import_id,
    key,
    response_id,
    value
from validated_survey_embedded_data
where response_id is not null
  and key is not null
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5998 | 6000 | 0 | 0 | 0 | 2 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"response_id":"sur10011027257","key":"custom_field_958"}</code> |
| K2 | <code>{"response_id":"sur10011735702","key":"custom_field_95"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| import_id | 0 | 0 | 2 | VARCHAR | VARCHAR |
| key | 0 | 0 | 2 | VARCHAR | VARCHAR |
| response_id | 0 | 0 | 2 | VARCHAR | VARCHAR |
| value | 0 | 0 | 2 | VARCHAR | VARCHAR |

import_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"IMP_8258324","rows":1}]</code> | <code>[{"value":"IMP_5920024","rows":1},{"value":"IMP_8258324","rows":1}]</code> |
| K2 | <code>[{"value":"IMP_6486089","rows":1}]</code> | <code>[{"value":"IMP_3712154","rows":1},{"value":"IMP_6486089","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

key 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"custom_field_958","rows":1}]</code> | <code>[{"value":"custom_field_958","rows":2}]</code> |
| K2 | <code>[{"value":"custom_field_95","rows":1}]</code> | <code>[{"value":"custom_field_95","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

response_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"SUR10011027257","rows":1}]</code> | <code>[{"value":"SUR10011027257","rows":2}]</code> |
| K2 | <code>[{"value":"SUR10011735702","rows":1}]</code> | <code>[{"value":"SUR10011735702","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

value 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"value_838","rows":1}]</code> | <code>[{"value":"value_259","rows":1},{"value":"value_838","rows":1}]</code> |
| K2 | <code>[{"value":"value_312","rows":1}]</code> | <code>[{"value":"value_242","rows":1},{"value":"value_312","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

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
| 23 | run | <code>cat &gt; sql/intermediate/int_qualtrics__contacts.sql &lt;&lt;'SQL'<br>WITH membership_aggregates AS (<br>    SELECT<br>        directory_id,<br>        contact_id,<br>        string_agg(mailing_list_id, ', ') FILTER (WHERE </code> | 0 | false | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
    FROM staging.stg_qualtrics__survey_embedded_data
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-014.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__survey_embedded_data.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__survey_embedded_data.sql`
- S6: `records/006_contract_impl-014.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/result.md`
- S10: `data/022_packages_work/022_impl-014_stg_qualtrics__survey_embedded_data/022_impl-014_stg_qualtrics__survey_embedded_data.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions`
