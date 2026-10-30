# impl-030 | staging | stg_zuora__contact | 差异：S1；日期 原记录

## 契约完整原文

S3:111–168

```yaml
    - name: stg_zuora__contact
      description: "Cleaned contacts with email normalization and phone format standardization; latest per contact and per account-contact flags."
      source_table: raw.zuora_contact_data
      columns:
        - name: contact_id
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: address_1
          data_type: VARCHAR
        - name: address_2
          data_type: VARCHAR
        - name: city
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
          source_expression: "cast(created_date as TIMESTAMP)"
        - name: description
          data_type: VARCHAR
        - name: first_name
          data_type: VARCHAR
        - name: last_name
          data_type: VARCHAR
        - name: postal_code
          data_type: VARCHAR
        - name: state
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
          source_expression: "cast(updated_date as TIMESTAMP)"
        - name: work_email
          data_type: VARCHAR
          source_expression: "lower(trim(work_email))"
          validation_rules:
            - rule: "work_email IS NULL OR work_email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
              on_failure: nullify_field
        - name: work_phone
          data_type: VARCHAR
        - name: mobile_phone
          data_type: VARCHAR
          source_expression: "case when mobile_phone is null then null else (case when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 10 then '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),1,3) || ') ' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),4,3) || '-' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),7,4) when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 11 then '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),2,3) || ') ' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),5,3) || '-' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),8,4) else null end) end"
        - name: is_most_recent_record
          data_type: BOOLEAN
          source_expression: "row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1"
        - name: is_most_recent_account_contact
          data_type: BOOLEAN
          source_expression: "row_number() over (partition by account_id order by try_cast(created_date as TIMESTAMP) desc) = 1"
      row_filters:
        - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
          on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_contact_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT
        id AS contact_id,
        try_cast("id" AS VARCHAR) AS account_id,
        try_cast("address_1" AS VARCHAR) AS address_1,
        try_cast("address_2" AS VARCHAR) AS address_2,
        try_cast("city" AS VARCHAR) AS city,
        try_cast("country" AS VARCHAR) AS country,
        try_cast("created_by_id" AS VARCHAR) AS created_by_id,
        try_cast(created_date as TIMESTAMP) AS created_date,
        try_cast("description" AS VARCHAR) AS description,
        try_cast("first_name" AS VARCHAR) AS first_name,
        try_cast("last_name" AS VARCHAR) AS last_name,
        try_cast("postal_code" AS VARCHAR) AS postal_code,
        try_cast("state" AS VARCHAR) AS state,
        try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
        try_cast(updated_date as TIMESTAMP) AS updated_date,
        CASE WHEN work_email IS NULL OR regexp_matches(lower(trim(work_email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') THEN lower(trim(work_email)) ELSE NULL END AS work_email,
        try_cast("work_phone" AS VARCHAR) AS work_phone,
        case when mobile_phone is null then null else (case when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 10 then '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),1,3) || ') ' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),4,3) || '-' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),7,4) when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 11 then '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),2,3) || ') ' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),5,3) || '-' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),8,4) else null end) end AS mobile_phone,
        row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 AS is_most_recent_record,
        row_number() over (partition by account_id order by try_cast(created_date as TIMESTAMP) desc) = 1 AS is_most_recent_account_contact
FROM source_rows
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select * from raw.zuora_contact_data where _fivetran_deleted is null or _fivetran_deleted = false
),
normalized as (
    select
        id as contact_id,
        account_id,
        address_1,
        address_2,
        city,
        country,
        created_by_id,
        cast(created_date as TIMESTAMP) as created_date,
        description,
        first_name,
        last_name,
        postal_code,
        state,
        updated_by_id,
        cast(updated_date as TIMESTAMP) as updated_date,
        -- email normalization and validation
        lower(trim(work_email)) as work_email_norm,
        work_phone,
        mobile_phone,
        row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 as is_most_recent_record,
        row_number() over (partition by account_id order by try_cast(created_date as TIMESTAMP) desc) = 1 as is_most_recent_account_contact
    from base
),
cleaned as (
    select
        contact_id,
        account_id,
        address_1,
        address_2,
        city,
        country,
        created_by_id,
        created_date,
        description,
        first_name,
        last_name,
        postal_code,
        state,
        updated_by_id,
        updated_date,
        case
            when work_email_norm is null then null
            when regexp_matches(work_email_norm, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') then work_email_norm
            else null
        end as work_email,
        work_phone,
        -- phone standardization: keep digits, format (XXX) XXX-XXXX if 10 digits; else null
        case
            when mobile_phone is null then null
            else (
                case
                    when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 10 then
                        '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),1,3) || ') ' ||
                        substr(regexp_replace(mobile_phone, '[^0-9]', ''),4,3) || '-' ||
                        substr(regexp_replace(mobile_phone, '[^0-9]', ''),7,4)
                    when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 11 then
                        '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),2,3) || ') ' ||
                        substr(regexp_replace(mobile_phone, '[^0-9]', ''),5,3) || '-' ||
                        substr(regexp_replace(mobile_phone, '[^0-9]', ''),8,4)
                    else null
                end
            )
        end as mobile_phone,
        is_most_recent_record,
        is_most_recent_account_contact
    from normalized
)
select * from cleaned
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 3741 | 3741 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"contact_id":"000da68a5f9241e98714f8aa063e2453"}</code> |
| K2 | <code>{"contact_id":"0092de36f7b24de2bff7c1a2297e539f"}</code> |
| K3 | <code>{"contact_id":"009528c5cdc943c9968de31e8c38c4dd"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 3741 | 3741 | 3741 | VARCHAR | VARCHAR |
| address_1 | 0 | 0 | 0 | VARCHAR | VARCHAR |
| address_2 | 0 | 0 | 0 | VARCHAR | VARCHAR |
| city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| first_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| postal_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| work_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| work_phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mobile_phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_most_recent_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_most_recent_account_contact | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

account_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 000da68a5f9241e98714f8aa063e2453 | b31133b1d7ec400883d3e3bea7fb8eaa |
| K2 | 0092de36f7b24de2bff7c1a2297e539f | 3085e1caa85944b2a2d3a91bf2204130 |
| K3 | 009528c5cdc943c9968de31e8c38c4dd | 23c4aee1960b45f784c2596284380201 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>3列；[{"column":"address_2","value":""},{"column":"description","value":""},{"column":"is_most_recent_record","value":"true"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["contact_id","account_id"],"nonnull_equal_rows":3741,"meaning_status":"契约未描述含义差别"},{"columns":["address_2","description"],"nonnull_equal_rows":3741,"meaning_status":"契约未描述含义差别"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：73；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print -exec sh -c 'echo --- $1; wc -l "$1"' _ {} \; &amp;&amp; cat config/layer_dependencies.yaml</code> | 3638 | true | false |
| 13 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('zuora_start.duckdb',read_only=True)<br>print(c.execute("select table_name from information_schema.tables where table_schema='raw'").fetchall())<br>for t, in </code> | 39412 | false | false |
| 15 | run | <code>python3 - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(x['staging_contract']['tables']), [t['name'] for t in x['staging_contract']['tables']])<br>print('inter', [m['name</code> | 1273 | true | false |
| 17 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb,yaml<br>c=duckdb.connect('zuora_start.duckdb',read_only=True)<br>y=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in y['staging_contract']['tables']:<br> raw=t['source_tab</code> | 3209 | true | false |
| 27 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb,glob<br>c=duckdb.connect(':memory:'); c.execute('ATTACH \'zuora_start.duckdb\' AS src_db')<br># import raw alias relevant exact as run logic<br>for tbl, in c.execute("select tabl</code> | 3906 | true | false |
| 29 | run | <code>cat &gt; /tmp/build_models.py &lt;&lt;'PY'<br>from pathlib import Path<br>P=Path('sql/intermediate')<br>pass_models={<br>'int_zuora__account_current':('stg_zuora__account','is_most_recent_record = TRUE'),<br>'int_zuora__cont</code> | 0 | false | false |
| 31 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8482 | true | false |
| 39 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('zuora.duckdb',read_only=True)<br>for t in ['zuora_account_data','zuora_invoice_data','zuora_contact_data','zuora_invoice_payment_data','zuora_order_data',</code> | 4803 | false | false |
| 51 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; grep -E 'ERROR&#124;WARNING:&#124;✓&#124;Execution failed&#124;successfully' /tmp/runlog &#124; tail -80</code> | 3588 | true | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
'int_zuora__contact_current':('stg_zuora__contact','is_most_recent_record = TRUE AND is_most_recent_account_contact = TRUE'),
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-030.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__contact.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__contact.sql`
- S6: `records/006_contract_impl-030.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/result.md`
- S10: `data/024_packages_work/024_impl-030_stg_zuora__contact/024_impl-030_stg_zuora__contact.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions`
