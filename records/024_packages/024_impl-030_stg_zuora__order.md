# impl-030 | staging | stg_zuora__order | 差异：S1；日期 原记录

## 契约完整原文

S3:1049–1093

```yaml
    - name: stg_zuora__order
      description: "Cleaned orders including scheduling and error metadata; latest snapshot indicator."
      source_table: raw.zuora_order_data
      columns:
        - name: order_id
          data_type: VARCHAR
        - name: account_id
          data_type: VARCHAR
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: category
          data_type: VARCHAR
        - name: created_by_id
          data_type: BIGINT
        - name: created_date
          data_type: TIMESTAMP
        - name: default_payment_method_id
          data_type: VARCHAR
        - name: description
          data_type: VARCHAR
        - name: error_code
          data_type: VARCHAR
        - name: error_message
          data_type: VARCHAR
        - name: order_date
          data_type: DATE
        - name: order_number
          data_type: VARCHAR
        - name: response
          data_type: VARCHAR
        - name: scheduled_date
          data_type: VARCHAR
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: state
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
        - name: updated_by_id
          data_type: BIGINT
        - name: updated_date
          data_type: TIMESTAMP
        - name: is_most_recent_record
          data_type: BOOLEAN

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_order_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT
        try_cast("id" AS VARCHAR) AS order_id,
        try_cast("id" AS VARCHAR) AS account_id,
        try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
        try_cast("category" AS VARCHAR) AS category,
        try_cast("created_by_id" AS BIGINT) AS created_by_id,
        try_cast("created_date" AS TIMESTAMP) AS created_date,
        try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
        try_cast("description" AS VARCHAR) AS description,
        try_cast("error_code" AS VARCHAR) AS error_code,
        try_cast("error_message" AS VARCHAR) AS error_message,
        try_cast("order_date" AS DATE) AS order_date,
        try_cast("order_number" AS VARCHAR) AS order_number,
        try_cast("response" AS VARCHAR) AS response,
        try_cast("scheduled_date" AS VARCHAR) AS scheduled_date,
        try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
        try_cast("state" AS VARCHAR) AS state,
        try_cast("status" AS VARCHAR) AS status,
        try_cast("updated_by_id" AS BIGINT) AS updated_by_id,
        try_cast("updated_date" AS TIMESTAMP) AS updated_date,
        row_number() over (partition by id order by try_cast(updated_date as timestamp) desc NULLS LAST) = 1 AS is_most_recent_record
FROM source_rows
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select * from raw.zuora_order_data
    where _fivetran_deleted is null or _fivetran_deleted = false
),
final as (
    select
        id as order_id,
        account_id,
        bill_to_contact_id,
        category,
        created_by_id,
        cast(created_date as TIMESTAMP) as created_date,
        default_payment_method_id,
        description,
        error_code,
        error_message,
        order_date,
        order_number,
        response,
        scheduled_date,
        sold_to_contact_id,
        state,
        status,
        updated_by_id,
        cast(updated_date as TIMESTAMP) as updated_date,
        row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
    from base
)
select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5 | 5 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"order_id":"2c92c0996f5603c5016f61609aa87cf2"}</code> |
| K2 | <code>{"order_id":"2c92c0996f5603c5016f61609aab7cf3"}</code> |
| K3 | <code>{"order_id":"8ad0823f7e0e9d7a017e16fca2625404"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| order_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 5 | 5 | 5 | VARCHAR | VARCHAR |
| bill_to_contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_by_id | 0 | 0 | 0 | BIGINT | BIGINT |
| default_payment_method_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| error_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| error_message | 0 | 0 | 0 | VARCHAR | VARCHAR |
| order_date | 0 | 0 | 0 | DATE | DATE |
| order_number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| response | 0 | 0 | 0 | VARCHAR | VARCHAR |
| scheduled_date | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sold_to_contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_by_id | 0 | 0 | 0 | BIGINT | BIGINT |
| updated_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| is_most_recent_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

account_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2c92c0996f5603c5016f61609aa87cf2 | dff38ac0e09e5a914e7cddb66f92e2af |
| K2 | 2c92c0996f5603c5016f61609aab7cf3 | dff38ac0e5e1b210b55e785af668c300 |
| K3 | 8ad0823f7e0e9d7a017e16fca2625404 | dff38ac0df6edbfb4cb3774f7e21f752 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>4列；[{"column":"error_code","table_rows":5},{"column":"error_message","table_rows":5},{"column":"response","table_rows":5}]</code> |
| A3_constant_nonnull_column | <code>5列；[{"column":"created_by_id","value":"3"},{"column":"description","value":"Created by migration"},{"column":"status","value":"Completed"}]</code> |
| A4_equal_columns | <code>4组；[{"columns":["order_id","account_id"],"nonnull_equal_rows":5,"meaning_status":"契约未描述含义差别"},{"columns":["bill_to_contact_id","sold_to_contact_id"],"nonnull_equal_rows":5,"meaning_status":"契约未描述含义差别"},{"columns":["created_by_id","updated_by_id"],"nonnull_equal_rows":5,"meaning_status":"契约未描述含义差别"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：73；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print -exec sh -c 'echo --- $1; wc -l "$1"' _ {} \; &amp;&amp; cat config/layer_dependencies.yaml</code> | 3638 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py &amp;&amp; sed -n '1,240p' zuora_start.yaml</code> | 12667 | false | false |
| 13 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('zuora_start.duckdb',read_only=True)<br>print(c.execute("select table_name from information_schema.tables where table_schema='raw'").fetchall())<br>for t, in </code> | 39412 | false | false |
| 15 | run | <code>python3 - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(x['staging_contract']['tables']), [t['name'] for t in x['staging_contract']['tables']])<br>print('inter', [m['name</code> | 1273 | true | false |
| 17 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb,yaml<br>c=duckdb.connect('zuora_start.duckdb',read_only=True)<br>y=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in y['staging_contract']['tables']:<br> raw=t['source_tab</code> | 3209 | true | false |
| 27 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb,glob<br>c=duckdb.connect(':memory:'); c.execute('ATTACH \'zuora_start.duckdb\' AS src_db')<br># import raw alias relevant exact as run logic<br>for tbl, in c.execute("select tabl</code> | 3906 | true | false |
| 31 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8482 | true | false |
| 37 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('zuora.duckdb',read_only=True)<br>for t in ['zuora_account_data','zuora_invoice_payment_data','zuora_order_data']:<br> print(t,c.execute(f"pragma table_info('</code> | 689 | false | false |
| 39 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('zuora.duckdb',read_only=True)<br>for t in ['zuora_account_data','zuora_invoice_data','zuora_contact_data','zuora_invoice_payment_data','zuora_order_data',</code> | 4803 | false | false |
| 51 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; grep -E 'ERROR&#124;WARNING:&#124;✓&#124;Execution failed&#124;successfully' /tmp/runlog &#124; tail -80</code> | 3588 | true | false |

### agent action 的 thought/message 命中原句

未找到命中原句。

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-030.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__order.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__order.sql`
- S6: `records/006_contract_impl-030.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/result.md`
- S10: `data/024_packages_work/024_impl-030_stg_zuora__order/024_impl-030_stg_zuora__order.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions`
