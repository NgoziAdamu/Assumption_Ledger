# impl-004 | staging | stg_salesforce__contact_history | 差异：S1；日期 原记录

## 契约完整原文

S3:432–490

```yaml
    - name: stg_salesforce__contact_history
      description: "Historical tracking of contact changes"
      source_table: "raw.contact_history"
      columns:
        - name: contact_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: account_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: contact_description
          data_type: VARCHAR
        - name: email
          data_type: VARCHAR
        - name: first_name
          data_type: VARCHAR
        - name: is_deleted
          data_type: BOOLEAN
        - name: last_activity_date
          data_type: DATE
          validation_rules:
            - rule: "last_activity_date = CASE WHEN last_activity_date IS NOT NULL AND last_activity_date > CURRENT_DATE THEN NULL WHEN last_activity_date IS NOT NULL AND last_activity_date < '2020-01-01' THEN NULL ELSE last_activity_date END"
              on_failure: nullify_field
        - name: last_modified_date
          data_type: TIMESTAMP
        - name: last_name
          data_type: VARCHAR
        - name: lead_source
          data_type: VARCHAR
        - name: mailing_city
          data_type: VARCHAR
        - name: mailing_country
          data_type: VARCHAR
        - name: mailing_postal_code
          data_type: VARCHAR
          validation_rules:
            - rule: "mailing_postal_code = CASE WHEN mailing_postal_code = '' THEN NULL WHEN mailing_postal_code IS NOT NULL AND LENGTH(TRIM(mailing_postal_code)) < 3 THEN DELETE_ROW WHEN mailing_postal_code IS NOT NULL AND LENGTH(TRIM(mailing_postal_code)) > 12 THEN NULL ELSE UPPER(TRIM(mailing_postal_code)) END"
              on_failure: correct
        - name: mailing_state
          data_type: VARCHAR
        - name: mailing_street
          data_type: VARCHAR
        - name: mobile_phone
          data_type: VARCHAR
          validation_rules:
            - rule: "mobile_phone = CASE WHEN mobile_phone = '' THEN NULL WHEN mobile_phone IS NOT NULL AND LENGTH(REGEXP_REPLACE(mobile_phone, '[^0-9]', '')) < 10 THEN NULL ELSE REGEXP_REPLACE(mobile_phone, '[^0-9+()-]', '') END"
              on_failure: nullify_field
        - name: contact_name
          data_type: VARCHAR
        - name: owner_id
          data_type: VARCHAR
        - name: phone
          data_type: VARCHAR
        - name: title
          data_type: VARCHAR
        - name: history_unique_key
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        CAST("id" AS VARCHAR) AS contact_id,
        CAST("account_id" AS VARCHAR) AS account_id,
        CAST("_fivetran_start" AS TIMESTAMP) AS created_date,
        CAST("description" AS VARCHAR) AS contact_description,
        CAST("email" AS VARCHAR) AS email,
        CAST("first_name" AS VARCHAR) AS first_name,
        CAST("is_deleted" AS BOOLEAN) AS is_deleted,
        CAST("last_activity_date" AS DATE) AS last_activity_date,
        CAST("last_modified_date" AS TIMESTAMP) AS last_modified_date,
        CAST("last_name" AS VARCHAR) AS last_name,
        CAST("lead_source" AS VARCHAR) AS lead_source,
        CAST("mailing_city" AS VARCHAR) AS mailing_city,
        CAST("mailing_country" AS VARCHAR) AS mailing_country,
        CASE WHEN CAST("mailing_postal_code" AS VARCHAR) = '' THEN NULL WHEN LENGTH(TRIM(CAST("mailing_postal_code" AS VARCHAR))) > 12 THEN NULL ELSE UPPER(TRIM(CAST("mailing_postal_code" AS VARCHAR))) END AS mailing_postal_code,
        CAST("mailing_state" AS VARCHAR) AS mailing_state,
        CAST("mailing_street" AS VARCHAR) AS mailing_street,
        CASE WHEN CAST("mobile_phone" AS VARCHAR) = '' THEN NULL WHEN LENGTH(REGEXP_REPLACE(CAST("mobile_phone" AS VARCHAR), '[^0-9]', '')) < 10 THEN NULL ELSE REGEXP_REPLACE(CAST("mobile_phone" AS VARCHAR), '[^0-9+()-]', '') END AS mobile_phone,
        CAST("name" AS VARCHAR) AS contact_name,
        CAST("owner_id" AS VARCHAR) AS owner_id,
        CAST("phone" AS VARCHAR) AS phone,
        CAST("title" AS VARCHAR) AS title,
        CAST(hash("_fivetran_start", "_fivetran_end") AS VARCHAR) AS history_unique_key
    FROM raw.contact_history
)
SELECT *
FROM source_rows
WHERE contact_id IS NOT NULL AND
        ("mailing_postal_code" IS NULL OR "mailing_postal_code" = '' OR LENGTH(TRIM(CAST("mailing_postal_code" AS VARCHAR))) >= 3)
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *
    from raw.contact_history
),

validated as (
    select
        id,
        account_id,
        -- Generate created_date as current timestamp for history tracking since raw table might not have it
        current_timestamp as created_date,
        description,
        email,
        first_name,
        -- Apply validation rule for is_deleted
        case
            when is_deleted is null then false
            when is_deleted not in (true, false) then false
            else is_deleted
        end as is_deleted,
        -- Apply validation rule for last_activity_date
        case
            when last_activity_date is not null and last_activity_date > current_date then null
            when last_activity_date is not null and last_activity_date < '2020-01-01' then null
            else last_activity_date
        end as last_activity_date,
        last_modified_date,
        last_name,
        lead_source,
        mailing_city,
        mailing_country,
        -- Missing column from raw data - set to null
        cast(null as varchar) as mailing_country_code,
        -- Apply validation rule for mailing_postal_code
        case
            when mailing_postal_code = '' then null
            when mailing_postal_code is not null and length(trim(mailing_postal_code)) < 3 then null
            when mailing_postal_code is not null and length(trim(mailing_postal_code)) > 12 then null
            else upper(trim(mailing_postal_code))
        end as mailing_postal_code,
        mailing_state,
        mailing_street,
        -- Apply validation rule for mobile_phone - delete rows with invalid phone numbers
        case
            when mobile_phone = '' then null
            when mobile_phone is not null and length(regexp_replace(mobile_phone, '[^0-9]', '')) < 10 then null
            else regexp_replace(mobile_phone, '[^0-9+()-]', '')
        end as mobile_phone,
        name,
        owner_id,
        phone,
        title,
        -- Generate unique key for history tracking
        concat(id, '_', current_timestamp::varchar) as history_unique_key
    from base
    -- Delete rows with invalid phone numbers according to YAML spec
    where (mobile_phone = '' or mobile_phone is null or length(regexp_replace(mobile_phone, '[^0-9]', '')) >= 10)
)

select
    cast(contact_id as varchar) as contact_id,
    cast(account_id as varchar) as account_id,
    cast(created_date as timestamp) as created_date,
    cast(description as varchar) as contact_description,
    cast(email as varchar) as email,
    cast(first_name as varchar) as first_name,
    cast(is_deleted as boolean) as is_deleted,
    cast(last_activity_date as date) as last_activity_date,
    cast(last_modified_date as timestamp) as last_modified_date,
    cast(last_name as varchar) as last_name,
    cast(lead_source as varchar) as lead_source,
    cast(mailing_city as varchar) as mailing_city,
    cast(mailing_country as varchar) as mailing_country,
    cast(mailing_country_code as varchar) as mailing_country_code,
    cast(mailing_postal_code as varchar) as mailing_postal_code,
    cast(mailing_state as varchar) as mailing_state,
    cast(mailing_street as varchar) as mailing_street,
    cast(mobile_phone as varchar) as mobile_phone,
    cast(name as varchar) as contact_name,
    cast(owner_id as varchar) as owner_id,
    cast(phone as varchar) as phone,
    cast(title as varchar) as title,
    cast(history_unique_key as varchar) as history_unique_key
from (
    select
        id as contact_id,
        account_id,
        created_date,
        description,
        email,
        first_name,
        is_deleted,
        last_activity_date,
        last_modified_date,
        last_name,
        lead_source,
        mailing_city,
        mailing_country,
        mailing_country_code,
        mailing_postal_code,
        mailing_state,
        mailing_street,
        mobile_phone,
        name,
        owner_id,
        phone,
        title,
        history_unique_key
    from validated
) as final_data
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 3000 | 3000 | 3000 | 2369 | 0 | 559 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| contact_description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| first_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| last_activity_date | 0 | 0 | 0 | DATE | DATE |
| last_modified_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| last_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| lead_source | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_postal_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_street | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mobile_phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| contact_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| title | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"contact_id":"00302EQ38cvTeOD","account_id":"00183XzBVYWN0mM","mailing_postal_code":"69843","owner_id":"005HmN9BTohnmdp","history_unique_key":"4938918593705415477"},{"contact_id":"00302EQ38cvTeOD","account_id":"00183XzBVYWN0mM","mailing_postal_code":"69843","owner_id":"005HmN9BTohnmdp","history_unique_key":"9858790954915291170"},{"contact_id":"00302XSINEEu7pO","account_id":"001KAFBrz7NSUyQ","mailing_postal_code":"89468","owner_id":"005QWQE3wcCg6Dr","history_unique_key":"13740525663967025893"},{"contact_id":"00304G8e3czm60C","account_id":"001TWaJUQkHENNu","mailing_postal_code":"19774","owner_id":"005GsOSTEM9gsuM","history_unique_key":"7820150521184537574"},{"contact_id":"00306XQXXhoKuF1","account_id":"001TD22iyaji4Q2","mailing_postal_code":"23558","owner_id":"005e7g2czEDicdr","history_unique_key":"16311265144497965042"}]</code> | <code>[{"contact_id":"00302EQ38cvTeOD","account_id":"00183XzBVYWN0mM","mailing_postal_code":"69843","owner_id":"005HmN9BTohnmdp","history_unique_key":"00302EQ38cvTeOD_2025-10-24 15:03:11.630125+08"},{"contact_id":"00302XSINEEu7pO","account_id":"001KAFBrz7NSUyQ","mailing_postal_code":"89468","owner_id":"005QWQE3wcCg6Dr","history_unique_key":"00302XSINEEu7pO_2025-10-24 15:03:11.630125+08"},{"contact_id":"00304G8e3czm60C","account_id":"001TWaJUQkHENNu","mailing_postal_code":"19774","owner_id":"005GsOSTEM9gsuM","history_unique_key":"00304G8e3czm60C_2025-10-24 15:03:11.630125+08"},{"contact_id":"00306XQXXhoKuF1","account_id":"001TD22iyaji4Q2","mailing_postal_code":"23558","owner_id":"005e7g2czEDicdr","history_unique_key":"00306XQXXhoKuF1_2025-10-24 15:03:11.630125+08"},{"contact_id":"0030bfFnWfXxUye","account_id":"001mSu7xTLzwqi6","mailing_postal_code":"04853","owner_id":"005rio1CjB4LvZd","history_unique_key":"0030bfFnWfXxUye_2025-10-24 15:03:11.630125+08"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"is_deleted","value":"false"}]</code> |
| C9_gold_runtime_text | <code>S5:10 current timestamp；命中数=4</code> |
| C9_contract_runtime_text | <code>S3:454 CURRENT_DATE；命中数=1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：53；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/.events/sessions/024a80d8-934c-43-4e69514191069ca/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print -exec wc -l {} \; &amp;&amp; cat config/layer_dependencies.yaml</code> | 1475 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9373 | false | false |
| 11 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print('tables', [a['name'] for a in x['staging_contract']['tables']])<br>print('intermediate', [a['name'] for a in x['modelin</code> | 354 | true | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw' order by table_n</code> | 31400 | false | false |
| 21 | run | <code>cat &gt; sql/marts/salesforce__account_daily_history.sql &lt;&lt;'SQL'<br>WITH history_rows AS (<br>    SELECT<br>        account_id,<br>        CAST(created_date AS DATE) AS snapshot_date,<br>        account_name,<br>        a</code> | 6930 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>p='/tmp/gen.py'<br>s=open(p).read()<br>s=s.replace("map_common={'account_id':'id','contact_id':'id','lead_id':'id','event_id':'id','account_name':'name','contact_name':'name','lead_name':'na</code> | 428 | false | false |
| 27 | run | <code>nl -ba /tmp/gen.py &#124; sed -n '1,100p'</code> | 5354 | false | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>import duckdb, pathlib<br>c=duckdb.connect('salesforce_start.duckdb')<br>for schema in ('staging','intermediate','marts'): c.execute(f'create schema if not exists {schema}')<br>for layer in ('s</code> | 639 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_salesforce__contact.sql'; s=open(p).read().replace('CAST("created_date" AS TIMESTAMP) AS created_date','CAST(NULL AS TIMESTAMP) AS created_date'); open(p,'w').write(</code> | 501 | true | false |
| 39 | run | python run.py | 6107 | true | false |
| 41 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已根据 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Salesforce SQL pipeline，实现顺序为 staging → intermediate → marts，SQL 位</code> | 82 | false | false |
| 43 | run | <code>ls -ld /workspace /tmp &amp;&amp; cat &gt; result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已根据 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Salesforce SQL pipeline，实现顺序为 staging → intermediate → marts，SQL 位于规定的 `sq</code> | 169 | false | false |
| 47 | run | <code>id &amp;&amp; cat &gt; .tmp/report/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已根据 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Salesforce SQL pipeline，实现顺序为 staging → intermediate → marts，SQL 位于规定的 `sql/&lt;layer</code> | 153 | false | false |
| 49 | run | <code>cp .tmp/report/result.md result.md &amp;&amp; cat result.md</code> | 1797 | true | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
    FROM staging.stg_salesforce__contact_history
```
event 41 / message

```text
| Staging | `stg_salesforce__contact_history` | 3,000 |
```
event 43 / message

```text
| Staging | `stg_salesforce__contact_history` | 3,000 |
```
event 47 / message

```text
| Staging | `stg_salesforce__contact_history` | 3,000 |
```

## result.md 本表名原句

S9:16

```text
| Staging | `stg_salesforce__contact_history` | 3,000 |
```

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-004.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-004/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/sql/staging/stg_salesforce__contact_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/sql/staging/stg_salesforce__contact_history.sql`
- S6: `records/006_contract_impl-004.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/result.md`
- S10: `records/012_packages/012_impl-004_staging_stg_salesforce__contact_history.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/salesforce.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/.events/sessions`
