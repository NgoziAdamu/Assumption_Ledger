# impl-017 | staging | stg_greenhouse__eeoc | 差异：S1；日期 原记录

## 契约完整原文

S3:200–237

```yaml
    - name: stg_greenhouse__eeoc
      description: "Cleaned EEOC demographic data with standardized category values and privacy compliance"
      source_table: "raw.eeoc"
      primary_key: ["application_id"]
      columns:
        - name: application_id
          data_type: BIGINT
          constraints: [not_null, unique]
        - name: disability_status_description
          data_type: VARCHAR(100)
          validation_rules:
            - rule: "disability_status_description = TRIM(disability_status_description)"
              on_failure: correct
            - rule: "disability_status_description IN ('Yes', 'No', 'Prefer not to answer') OR disability_status_description IS NULL"
              on_failure: nullify_field
        - name: disability_status_id
          data_type: BIGINT
        - name: gender_description
          data_type: VARCHAR(100)
        - name: gender_id
          data_type: BIGINT
        - name: race_description
          data_type: VARCHAR(100)
        - name: race_id
          data_type: BIGINT
        - name: veteran_status_id
          data_type: BIGINT
        - name: veteran_status_description
          data_type: VARCHAR(100)
          validation_rules:
            - rule: "veteran_status_description = TRIM(veteran_status_description)"
              on_failure: correct
            - rule: "veteran_status_description IN ('Yes', 'No', 'Prefer not to answer') OR veteran_status_description IS NULL"
              on_failure: nullify_field
        - name: submitted_at
          data_type: TIMESTAMP

    # Additional staging tables for complete coverage of database schema
```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        TRY_CAST(application_id AS BIGINT) AS "application_id",
        CASE WHEN TRIM(disability_status_description) IN ('Yes', 'No', 'Prefer not to answer') THEN TRIM(disability_status_description) ELSE NULL END AS disability_status_description,
        TRY_CAST(disability_status_id AS BIGINT) AS "disability_status_id",
        TRY_CAST(gender_description AS VARCHAR(100)) AS "gender_description",
        TRY_CAST(gender_id AS BIGINT) AS "gender_id",
        TRY_CAST(race_description AS VARCHAR(100)) AS "race_description",
        TRY_CAST(race_id AS BIGINT) AS "race_id",
        TRY_CAST(veteran_status_id AS BIGINT) AS "veteran_status_id",
        CASE WHEN TRIM(veteran_status_description) IN ('Yes', 'No', 'Prefer not to answer') THEN TRIM(veteran_status_description) ELSE NULL END AS veteran_status_description,
        TRY_CAST(submitted_at AS TIMESTAMP) AS "submitted_at",
        ROW_NUMBER() OVER (PARTITION BY "application_id" ORDER BY "application_id") AS _row_num
    FROM raw.eeoc
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE "application_id" IS NOT NULL AND "application_id" IS NOT NULL
)
SELECT "application_id", "disability_status_description", "disability_status_id", "gender_description", "gender_id", "race_description", "race_id", "veteran_status_id", "veteran_status_description", "submitted_at"
FROM validated_rows
WHERE _row_num = 1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Purpose: Standardize EEOC demographic data with validation
-- Source: raw.eeoc
-- Target: staging.stg_greenhouse__eeoc

with source as (
    select * from raw.eeoc
),

renamed as (
    select
        application_id,
        LTRIM(RTRIM(disability_status_description)) as disability_status_description,
        disability_status_id,
        gender_description,
        gender_id,
        race_description,
        race_id,
        veteran_status_id,
        LTRIM(RTRIM(veteran_status_description)) as veteran_status_description,
        submitted_at

    from source
),

validated as (
    select
        application_id,
        -- Validate disability status values
        case
            when disability_status_description in ('Yes', 'No', 'Prefer not to answer') or disability_status_description is null
            then disability_status_description
            else null
        end as disability_status_description,
        disability_status_id,
        gender_description,
        gender_id,
        race_description,
        race_id,
        veteran_status_id,
        -- Validate veteran status values
        case
            when veteran_status_description in ('Yes', 'No', 'Prefer not to answer') or veteran_status_description is null
            then veteran_status_description
            else null
        end as veteran_status_description,
        submitted_at

    from renamed

    where
        -- Ensure primary key field is not null
        application_id is not null
)

select * from validated
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1846 | 2000 | 0 | 0 | 0 | 146 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"application_id":"10382"}</code> |
| K2 | <code>{"application_id":"10489"}</code> |
| K3 | <code>{"application_id":"10507"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| application_id | 0 | 0 | 154 | BIGINT | BIGINT |
| disability_status_description | 0 | 0 | 154 | VARCHAR | VARCHAR |
| disability_status_id | 0 | 0 | 154 | BIGINT | BIGINT |
| gender_description | 0 | 0 | 154 | VARCHAR | VARCHAR |
| gender_id | 0 | 0 | 154 | BIGINT | BIGINT |
| race_description | 0 | 0 | 154 | VARCHAR | VARCHAR |
| race_id | 0 | 0 | 154 | BIGINT | BIGINT |
| veteran_status_id | 0 | 0 | 154 | BIGINT | BIGINT |
| veteran_status_description | 0 | 0 | 154 | VARCHAR | VARCHAR |

application_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"10382","rows":1}]</code> | <code>[{"value":"10382","rows":2}]</code> |
| K2 | <code>[{"value":"10489","rows":1}]</code> | <code>[{"value":"10489","rows":2}]</code> |
| K3 | <code>[{"value":"10507","rows":1}]</code> | <code>[{"value":"10507","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

disability_status_description 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
| K2 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
| K3 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

disability_status_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
| K2 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
| K3 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

gender_description 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Prefer not to say","rows":1}]</code> | <code>[{"value":"Male","rows":1},{"value":"Prefer not to say","rows":1}]</code> |
| K2 | <code>[{"value":"Male","rows":1}]</code> | <code>[{"value":"Male","rows":1},{"value":"Prefer not to say","rows":1}]</code> |
| K3 | <code>[{"value":"Non-binary","rows":1}]</code> | <code>[{"value":null,"rows":1},{"value":"Non-binary","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

gender_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"4","rows":1}]</code> | <code>[{"value":"3","rows":1},{"value":"4","rows":1}]</code> |
| K2 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":1},{"value":"3","rows":1}]</code> |
| K3 | <code>[{"value":"2","rows":1}]</code> | <code>[{"value":"2","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

race_description 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Native American","rows":1}]</code> | <code>[{"value":"Native American","rows":2}]</code> |
| K2 | <code>[{"value":"White","rows":1}]</code> | <code>[{"value":"Hispanic","rows":1},{"value":"White","rows":1}]</code> |
| K3 | <code>[{"value":"Other","rows":1}]</code> | <code>[{"value":"Black","rows":1},{"value":"Other","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

race_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":1},{"value":"2","rows":1}]</code> |
| K2 | <code>[{"value":"6","rows":1}]</code> | <code>[{"value":"3","rows":1},{"value":"6","rows":1}]</code> |
| K3 | <code>[{"value":"3","rows":1}]</code> | <code>[{"value":"2","rows":1},{"value":"3","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

veteran_status_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
| K2 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
| K3 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

veteran_status_description 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
| K2 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
| K3 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"disability_status_description","table_rows":1846},{"column":"veteran_status_description","table_rows":1846}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；task_instruction_not_agent_report  - Left join staging.stg_greenhouse__eeoc (eeoc) on application_id to add candidate_gender, candidate_disability_status, candidate_race, and candidate_veteran_status; NULL if no EEOC record.</code> |

## 轨迹索引（不放输出原文）

本题事件总数：55；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find . -maxdepth 3 -type f &#124; sort &#124; head -100</code> | 2041 | false | false |
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 12604 | true | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('greenhouse_start.duckdb',read_only=True)<br>for t in c.execute("select table_name from information_schema.tables where table_schema='raw' order by 1").fetc</code> | 3529 | false | false |
| 17 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; python - &lt;&lt;'PY'<br>import yaml, pathlib<br>c=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br># raw source names differ from c</code> | 0 | false | false |
| 19 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>I=Path('sql/intermediate'); M=Path('sql/marts')<br>def w(d,n,s): (d/f'{n}.sql').write_text(s.strip()+"\n")<br>w(I,'int_greenhouse__user_emails', '''WITH ema</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br>w(M,'greenhouse__diversity_metrics', '''WITH application_demographics AS (<br>    SELECT YEAR(a.applied_at)::BIGINT AS application_year,<br>        QUARTER(a.applied_at)::BIGINT AS</code> | 0 | false | false |
| 27 | run | <code>python run.py &gt; /tmp/run.log 2&gt;&amp;1; tail -100 /tmp/run.log</code> | 5955 | false | false |
| 29 | run | <code>grep -E 'Executing: staging&#124;ERROR - ✗ staging&#124;staging\.' /tmp/run.log &#124; head -90</code> | 7093 | true | false |
| 31 | run | <code>sed -n '1,40p' sql/staging/stg_greenhouse__user.sql &amp;&amp; sed -n '1,30p' sql/staging/stg_greenhouse__eeoc.sql</code> | 2438 | false | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('greenhouse.duckdb',read_only=True)<br>for s in ['staging','intermediate','mart']:<br> print('\n',s)<br> for (t,) in c.execute(f"select table_name from informatio</code> | 1807 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
LEFT JOIN staging.stg_greenhouse__eeoc AS ee ON au.application_id = ee.application_id''')
```
event 25 / message

```text
    LEFT JOIN staging.stg_greenhouse__eeoc AS e ON a.application_id = e.application_id
```
event 31 / message

```text
Running command: sed -n '1,40p' sql/staging/stg_greenhouse__user.sql && sed -n '1,30p' sql/staging/stg_greenhouse__eeoc.sql
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-017.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/staging/stg_greenhouse__eeoc.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/sql/staging/stg_greenhouse__eeoc.sql`
- S6: `records/006_contract_impl-017.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/result.md`
- S10: `data/023_packages_work/023_impl-017_stg_greenhouse__eeoc/023_impl-017_stg_greenhouse__eeoc.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/greenhouse.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/greenhouse.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions`
