# impl-001 | staging | stg_lever__requisition | 差异：S1；日期 原记录

## 契约完整原文

S3:84–175

```yaml
    - name: stg_lever__requisition
      description: "Cleaned job requisitions with validated compensation bands, hiring requirements, and standardized employment classifications"
      source_table: "raw.requisition"
      columns:
        - name: requisition_id
          data_type: VARCHAR(50)
          constraints: [not_null, unique]
          validation_rules:
            - rule: "requisition_id = TRIM(requisition_id)"
              on_failure: correct
            - rule: "LENGTH(TRIM(requisition_id)) > 0"
              on_failure: delete_row
        - name: requisition_code
          data_type: VARCHAR(20)
          constraints: [not_null, unique]
          validation_rules:
            - rule: "requisition_code LIKE 'REQ-%'"
              on_failure: delete_row
        - name: requisition_name
          data_type: VARCHAR(500)
          constraints: [not_null]
        - name: status
          data_type: VARCHAR(20)
          constraints: [not_null]
          validation_rules:
            - rule: "status IN ('open', 'closed', 'cancelled', 'draft', 'pending')"
              on_failure: delete_row
        - name: employment_status
          data_type: VARCHAR(20)
          constraints: [not_null]
          validation_rules:
            - rule: "employment_status IN ('full-time', 'part-time', 'contract', 'internship', 'temporary')"
              on_failure: delete_row
        - name: compensation_band_currency
          data_type: VARCHAR(3)
          validation_rules:
            - rule: "compensation_band_currency IS NULL OR compensation_band_currency IN ('USD', 'EUR', 'GBP', 'CNY', 'CAD', 'AUD')"
              on_failure: nullify_field
        - name: compensation_band_interval
          data_type: VARCHAR(10)
          validation_rules:
            - rule: "compensation_band_interval IS NULL OR compensation_band_interval IN ('hourly', 'monthly', 'yearly')"
              on_failure: nullify_field
        - name: compensation_band_min
          data_type: DOUBLE
          validation_rules:
            - rule: "compensation_band_min IS NULL OR compensation_band_min >= 0"
              on_failure: nullify_field
        - name: compensation_band_max
          data_type: DOUBLE
          validation_rules:
            - rule: "compensation_band_max IS NULL OR compensation_band_max >= compensation_band_min"
              on_failure: nullify_field
        - name: location
          data_type: VARCHAR(255)
        - name: team
          data_type: VARCHAR(255)
        - name: creator_user_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: owner_user_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: hiring_manager_user_id
          data_type: VARCHAR(50)
        - name: created_at
          data_type: TIMESTAMP
        - name: backfill
          data_type: BOOLEAN
          constraints: [not_null]
          validation_rules:
            - rule: "backfill IN (TRUE, FALSE)"
              on_failure: delete_row
        - name: headcount_hired
          data_type: INT
          validation_rules:
            - rule: "headcount_hired IS NULL OR headcount_hired >= 0"
              on_failure: nullify_field
            - rule: "headcount_total IS NULL OR headcount_hired <= headcount_total"
              on_failure: nullify_field
        - name: headcount_infinite
          data_type: BOOLEAN
        - name: headcount_total
          data_type: INT
          validation_rules:
            - rule: "headcount_total IS NULL OR headcount_total >= 0"
              on_failure: nullify_field
            - rule: "headcount_infinite IS FALSE OR headcount_total IS NULL"
              on_failure: nullify_field
        - name: internal_notes
          data_type: VARCHAR(1000)

```

## agent 最终 SQL

S4

```sql
WITH typed AS (
    SELECT
        trim(cast(r."id" AS VARCHAR)) AS requisition_id,
        try_cast(r."requisition_code" AS VARCHAR(20)) AS requisition_code,
        try_cast(r."name" AS VARCHAR(500)) AS requisition_name,
        try_cast(r."status" AS VARCHAR(20)) AS status,
        try_cast(r."employment_status" AS VARCHAR(20)) AS employment_status,
        try_cast(r."compensation_band_currency" AS VARCHAR(3)) AS compensation_band_currency,
        try_cast(r."compensation_band_interval" AS VARCHAR(10)) AS compensation_band_interval,
        try_cast(r."compensation_band_min" AS DOUBLE) AS compensation_band_min,
        try_cast(r."compensation_band_max" AS DOUBLE) AS compensation_band_max,
        try_cast(r."location" AS VARCHAR(255)) AS location,
        try_cast(r."team" AS VARCHAR(255)) AS team,
        try_cast(r."creator_id" AS VARCHAR(50)) AS creator_user_id,
        try_cast(r."owner_id" AS VARCHAR(50)) AS owner_user_id,
        try_cast(r."hiring_manager_id" AS VARCHAR(50)) AS hiring_manager_user_id,
        try_cast(r."created_at" AS TIMESTAMP) AS created_at,
        try_cast(r."backfill" AS BOOLEAN) AS backfill,
        try_cast(r."headcount_hired" AS INT) AS headcount_hired,
        try_cast(r."headcount_infinite" AS BOOLEAN) AS headcount_infinite,
        try_cast(r."headcount_total" AS INT) AS headcount_total,
        try_cast(r."internal_notes" AS VARCHAR(1000)) AS internal_notes
    FROM raw.requisition AS r
),
valid AS (
    SELECT * FROM typed
    WHERE         status IN ('open','closed','cancelled','draft','pending') AND
              employment_status IN ('full-time','part-time','contract','internship','temporary') AND
              requisition_id IS NOT NULL AND
              length(requisition_id) > 0 AND
              requisition_code IS NOT NULL AND
              requisition_code LIKE 'REQ-%' AND
              requisition_name IS NOT NULL AND
              status IS NOT NULL AND
              employment_status IS NOT NULL AND
              creator_user_id IS NOT NULL AND
              owner_user_id IS NOT NULL AND
              backfill IS NOT NULL
),
ranked AS (
    SELECT *, row_number() OVER (PARTITION BY requisition_id, requisition_code ORDER BY requisition_id, requisition_code) AS _row_num
    FROM valid
)
SELECT requisition_id, requisition_code, requisition_name, status, employment_status, compensation_band_currency, compensation_band_interval, compensation_band_min, compensation_band_max, location, team, creator_user_id, owner_user_id, hiring_manager_user_id, created_at, backfill, headcount_hired, headcount_infinite, headcount_total, internal_notes
FROM ranked
WHERE _row_num = 1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Standardized cleaning of job requirement information (aligned with docs/staging_data_specification.yaml)

with base as (
    select
        trim(id) as requisition_id,
        name as requisition_name,
        requisition_code as requisition_code,
        status,
        employment_status,
        backfill,

        -- Salary range field cleaning
        nullif(compensation_band_currency, '') as compensation_band_currency_raw,
        nullif(compensation_band_interval, '') as compensation_band_interval_raw,
        compensation_band_min as compensation_band_min_raw,
        compensation_band_max as compensation_band_max_raw,

        -- Location/Team
        location as location,
        team as team,

        -- foreign key/user
        creator_id as creator_user_id,
        owner_id as owner_user_id,
        hiring_manager_id as hiring_manager_user_id,

        -- time
        try_cast(created_at as timestamp) as created_at,

        -- other
        internal_notes,
        headcount_hired,
        headcount_infinite,
        headcount_total
    from raw.requisition
), comp as (
    select
        *,
        -- Currency whitelist (leave blank if invalid)
        case when compensation_band_currency_raw in ('USD','EUR','GBP','CNY','CAD','AUD')
             then compensation_band_currency_raw else null end as compensation_band_currency,
        -- Payment interval whitelist (invalid and blank)
        case when compensation_band_interval_raw in ('hourly','monthly','yearly')
             then compensation_band_interval_raw else null end as compensation_band_interval,
        -- Minimum amount (<0, leave blank)
        case when compensation_band_min_raw is null or compensation_band_min_raw >= 0
             then compensation_band_min_raw else null end as compensation_band_min,
        -- The upper limit of the amount (leave blank if it is less than the lower limit)
        case when compensation_band_max_raw is null then null
             when compensation_band_min_raw is null then compensation_band_max_raw
             when compensation_band_max_raw >= compensation_band_min_raw then compensation_band_max_raw
             else null end as compensation_band_max,

        -- headcount rule (blank if invalid)
        case when headcount_hired is null or headcount_hired >= 0 then headcount_hired else null end as headcount_hired_adj,
        headcount_infinite as headcount_infinite_adj,
        case when headcount_total is null or headcount_total >= 0 then headcount_total else null end as headcount_total_nonneg,
        case when headcount_infinite then null else (case when headcount_total is null or headcount_total >= 0 then headcount_total else null end) end as headcount_total_adj
    from base
), filtered as (
    select
        created_at,
        creator_user_id,
        hiring_manager_user_id,
        requisition_id,
        requisition_name,
        owner_user_id,
        status,
        backfill,
        compensation_band_currency,
        compensation_band_interval,
        compensation_band_max,
        compensation_band_min,
        employment_status,
        -- If hired > total, leave hired empty.
        case when headcount_total_adj is not null and headcount_hired_adj is not null and headcount_hired_adj > headcount_total_adj then null else headcount_hired_adj end as headcount_hired,
        headcount_infinite_adj as headcount_infinite,
        headcount_total_adj as headcount_total,
        internal_notes,
        location,
        requisition_code,
        team
    from comp
    where
        -- Delete row: primary key/name/creation time
        length(requisition_id) > 0
        and requisition_name is not null
        -- Remove rows: encoding format assumptions
        and requisition_code like 'REQ-%'
        -- Delete rows: enumeration limit
        and status in ('open','closed','cancelled','draft','pending')
        and employment_status in ('full-time','part-time','contract','internship','temporary')
        -- Delete row: foreign key is not empty
        and creator_user_id is not null
        and owner_user_id is not null
        -- Delete rows: backfill boolean constraint
        and backfill in (true,false)
)

select * from filtered
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 146 | 146 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"requisition_id":"req67153496041"}</code> |
| K2 | <code>{"requisition_id":"req68555383119"}</code> |
| K3 | <code>{"requisition_id":"req80358733549"}</code> |
| K4 | <code>{"requisition_id":"req91223100448"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| creator_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| hiring_manager_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| requisition_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| requisition_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| backfill | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| compensation_band_currency | 3 | 3 | 3 | VARCHAR | VARCHAR |
| compensation_band_interval | 2 | 2 | 2 | VARCHAR | VARCHAR |
| compensation_band_max | 0 | 0 | 0 | DOUBLE | DOUBLE |
| compensation_band_min | 0 | 0 | 0 | DOUBLE | DOUBLE |
| employment_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| headcount_infinite | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| internal_notes | 0 | 0 | 0 | VARCHAR | VARCHAR |
| location | 0 | 0 | 0 | VARCHAR | VARCHAR |
| requisition_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team | 0 | 0 | 0 | VARCHAR | VARCHAR |

compensation_band_currency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | GBP2 | null |
| K2 | CNY2 | null |
| K3 | EUR2 | null |

compensation_band_interval 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | hourly2 | null |
| K4 | hourly7 | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

| 约束 | 列 | 违反计数 |
|---|---|---|
| unique | requisition_code | <code>{"distinct_key_groups":144,"duplicate_key_groups":2,"rows_in_duplicate_groups":4,"excess_duplicate_rows":2,"null_key_rows":0,"nonnull_duplicate_key_groups":2,"nonnull_rows_in_duplicate_groups":4,"nonnull_excess_duplicate_rows":2,"null_containing_duplicate_key_groups":0,"rows_in_null_containing_duplicate_groups":0,"including_nulls_duplicate_key_groups":2,"including_nulls_rows_in_duplicate_groups":4}</code> |

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"created_at","table_rows":146}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find sql -maxdepth 3 -type f &#124; sort &#124; head -100 &amp;&amp; cat config/layer_dependencies.yaml</code> | 4500 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9689 | false | false |
| 11 | run | cat lever_start.yaml | 4283 | false | false |
| 17 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml, pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>base=pathlib.Path('sql'); rawmaps={<br>'application':{'application_id':'id','posting_hiring_manager_</code> | 0 | false | false |
| 19 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate')<br>models={<br>'int_lever__contact_info':'''WITH emails AS (SELECT contact_id, string_agg('&lt;' &#124;&#124; email &#124;&#124; '&gt;', ', ') AS emails</code> | 0 | false | false |
| 27 | run | <code>grep -E 'ERROR -&#124;Executing: staging&#124;STAGING layer complete' /tmp/run.log</code> | 5620 | true | false |
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | true | false |
| 37 | run | <code>sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred&gt;external+10/referred&gt;external_avg+10/; s/internal&gt;external+10/internal&gt;external_avg+10/" sql/marts/lever__candidate_quality_insights.sq</code> | 2929 | false | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
'int_lever__requisition_users':'''SELECT r.*, o.user_name AS owner_name, c.user_name AS creator_name FROM staging.stg_lever__requisition r LEFT JOIN staging.stg_lever__user o ON r.owner_user_id=o.user_id LEFT JOIN staging.stg_lever__user c ON r.creator_user_id=c.user_id''',
```
event 37 / message

```text
    FROM staging.stg_lever__requisition GROUP BY hiring_manager_user_id
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-001.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__requisition.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__requisition.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_stg_lever__requisition/019_impl-001_stg_lever__requisition.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
