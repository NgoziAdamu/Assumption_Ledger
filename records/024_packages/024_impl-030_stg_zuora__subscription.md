# impl-030 | staging | stg_zuora__subscription | 差异：S1；日期 原记录

## 契约完整原文

S3:851–955

```yaml
    - name: stg_zuora__subscription
      description: "Cleaned subscriptions with status, term and key dates; latest snapshot indicator."
      source_table: raw.zuora_subscription_data
      columns:
        - name: subscription_id
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: auto_renew
          data_type: BOOLEAN
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: cancel_reason
          data_type: VARCHAR
        - name: cancelled_date
          data_type: TIMESTAMP
          source_expression: "cast(cancelled_date as TIMESTAMP)"
        - name: contract_acceptance_date
          data_type: TIMESTAMP
          source_expression: "cast(contract_acceptance_date as TIMESTAMP)"
        - name: contract_effective_date
          data_type: TIMESTAMP
          source_expression: "cast(contract_effective_date as TIMESTAMP)"
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
          source_expression: "cast(created_date as TIMESTAMP)"
        - name: current_term
          data_type: BIGINT
        - name: current_term_period_type
          data_type: VARCHAR
        - name: default_payment_method_id
          data_type: VARCHAR
        - name: externally_managed_by
          data_type: VARCHAR
        - name: initial_term
          data_type: BIGINT
        - name: initial_term_period_type
          data_type: VARCHAR
        - name: invoice_owner_id
          data_type: VARCHAR
        - name: is_invoice_separate
          data_type: BOOLEAN
        - name: is_latest_version
          data_type: BOOLEAN
        - name: last_booking_date
          data_type: DATE
        - name: subscription_name
          data_type: VARCHAR
          source_expression: "_name"
        - name: notes
          data_type: VARCHAR
        - name: original_created_date
          data_type: TIMESTAMP
          source_expression: "cast(original_created_date as TIMESTAMP)"
        - name: original_id
          data_type: VARCHAR
        - name: parent_account_id
          data_type: VARCHAR
        - name: payment_term
          data_type: VARCHAR
        - name: previous_subscription_id
          data_type: VARCHAR
        - name: renewal_term
          data_type: BIGINT
        - name: renewal_term_period_type
          data_type: VARCHAR
        - name: revision
          data_type: BIGINT
        - name: service_activation_date
          data_type: TIMESTAMP
          source_expression: "cast(service_activation_date as TIMESTAMP)"
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
        - name: subscription_end_date
          data_type: TIMESTAMP
        - name: subscription_start_date
          data_type: TIMESTAMP
        - name: term_end_date
          data_type: TIMESTAMP
          source_expression: "cast(term_end_date as TIMESTAMP)"
        - name: term_start_date
          data_type: TIMESTAMP
          source_expression: "cast(term_start_date as TIMESTAMP)"
        - name: term_type
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
          source_expression: "cast(updated_date as TIMESTAMP)"
        - name: version
          data_type: VARCHAR
          source_expression: "_version"
        - name: is_most_recent_record
          data_type: BOOLEAN
          source_expression: "row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1"
      row_filters:
        - rule: "coalesce(lower(cast(_fivetran_deleted as varchar)),'false') = 'false'"
          on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_subscription_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT
        id AS subscription_id,
        try_cast("id" AS VARCHAR) AS account_id,
        try_cast("auto_renew" AS BOOLEAN) AS auto_renew,
        try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
        try_cast("cancel_reason" AS VARCHAR) AS cancel_reason,
        try_cast(cancelled_date as TIMESTAMP) AS cancelled_date,
        try_cast(contract_acceptance_date as TIMESTAMP) AS contract_acceptance_date,
        try_cast(contract_effective_date as TIMESTAMP) AS contract_effective_date,
        try_cast("created_by_id" AS VARCHAR) AS created_by_id,
        try_cast(created_date as TIMESTAMP) AS created_date,
        try_cast("current_term" AS BIGINT) AS current_term,
        try_cast("current_term_period_type" AS VARCHAR) AS current_term_period_type,
        try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
        try_cast("externally_managed_by" AS VARCHAR) AS externally_managed_by,
        try_cast("initial_term" AS BIGINT) AS initial_term,
        try_cast("initial_term_period_type" AS VARCHAR) AS initial_term_period_type,
        try_cast("invoice_owner_id" AS VARCHAR) AS invoice_owner_id,
        try_cast("is_invoice_separate" AS BOOLEAN) AS is_invoice_separate,
        try_cast("is_latest_version" AS BOOLEAN) AS is_latest_version,
        try_cast("last_booking_date" AS DATE) AS last_booking_date,
        _name AS subscription_name,
        try_cast("notes" AS VARCHAR) AS notes,
        try_cast(original_created_date as TIMESTAMP) AS original_created_date,
        try_cast("original_id" AS VARCHAR) AS original_id,
        try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
        try_cast("payment_term" AS VARCHAR) AS payment_term,
        try_cast("previous_subscription_id" AS VARCHAR) AS previous_subscription_id,
        try_cast("renewal_term" AS BIGINT) AS renewal_term,
        try_cast("renewal_term_period_type" AS VARCHAR) AS renewal_term_period_type,
        try_cast("revision" AS BIGINT) AS revision,
        try_cast(service_activation_date as TIMESTAMP) AS service_activation_date,
        try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
        try_cast("status" AS VARCHAR) AS status,
        try_cast("subscription_end_date" AS TIMESTAMP) AS subscription_end_date,
        try_cast("subscription_start_date" AS TIMESTAMP) AS subscription_start_date,
        try_cast(term_end_date as TIMESTAMP) AS term_end_date,
        try_cast(term_start_date as TIMESTAMP) AS term_start_date,
        try_cast("term_type" AS VARCHAR) AS term_type,
        try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
        try_cast(updated_date as TIMESTAMP) AS updated_date,
        _version AS version,
        row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 AS is_most_recent_record
FROM source_rows
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select * from raw.zuora_subscription_data
    where coalesce(lower(cast(_fivetran_deleted as varchar)),'false') = 'false'
),
final as (
    select
        id as subscription_id,
        account_id,
        auto_renew,
        bill_to_contact_id,
        cancel_reason,
        cast(cancelled_date as TIMESTAMP) as cancelled_date,
        cast(contract_acceptance_date as TIMESTAMP) as contract_acceptance_date,
        cast(contract_effective_date as TIMESTAMP) as contract_effective_date,
        created_by_id,
        cast(created_date as TIMESTAMP) as created_date,
        current_term,
        current_term_period_type,
        default_payment_method_id,
        externally_managed_by,
        initial_term,
        initial_term_period_type,
        invoice_owner_id,
        is_invoice_separate,
        is_latest_version,
        last_booking_date,
        _name as subscription_name,
        notes,
        cast(original_created_date as TIMESTAMP) as original_created_date,
        original_id,
        parent_account_id,
        payment_term,
        previous_subscription_id,
        renewal_term,
        renewal_term_period_type,
        revision,
        cast(service_activation_date as TIMESTAMP) as service_activation_date,
        sold_to_contact_id,
        status,
        subscription_end_date,
        subscription_start_date,
        cast(term_end_date as TIMESTAMP) as term_end_date,
        cast(term_start_date as TIMESTAMP) as term_start_date,
        term_type,
        updated_by_id,
        cast(updated_date as TIMESTAMP) as updated_date,
        _version as version,
        row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 as is_most_recent_record
    from base
)
select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 732 | 732 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"subscription_id":"013353a8b1454804bf540b3e8eba9412"}</code> |
| K2 | <code>{"subscription_id":"017d1b04dfec451fbe13b324adb3880d"}</code> |
| K3 | <code>{"subscription_id":"01ccfd80e33f41cfa301e5d53a251f9d"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| subscription_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 732 | 732 | 732 | VARCHAR | VARCHAR |
| auto_renew | 0 | 0 | 0 | BOOLEAN | VARCHAR |
| bill_to_contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| cancel_reason | 0 | 0 | 0 | VARCHAR | VARCHAR |
| current_term | 0 | 0 | 0 | BIGINT | VARCHAR |
| current_term_period_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| default_payment_method_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| externally_managed_by | 0 | 0 | 0 | VARCHAR | VARCHAR |
| initial_term | 0 | 0 | 0 | BIGINT | VARCHAR |
| initial_term_period_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| invoice_owner_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_invoice_separate | 0 | 0 | 0 | BOOLEAN | VARCHAR |
| is_latest_version | 0 | 0 | 0 | BOOLEAN | VARCHAR |
| subscription_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| notes | 0 | 0 | 0 | VARCHAR | VARCHAR |
| original_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| parent_account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| payment_term | 0 | 0 | 0 | VARCHAR | VARCHAR |
| previous_subscription_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| renewal_term | 0 | 0 | 0 | BIGINT | VARCHAR |
| renewal_term_period_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| revision | 0 | 0 | 0 | BIGINT | VARCHAR |
| sold_to_contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| term_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| version | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_most_recent_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

account_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 013353a8b1454804bf540b3e8eba9412 | c2999ab1162943a98408df71381201c0 |
| K2 | 017d1b04dfec451fbe13b324adb3880d | abb112cb8ba943678c1cc429bd791577 |
| K3 | 01ccfd80e33f41cfa301e5d53a251f9d | 149cc97b6a9a484fb1207c56237806e1 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>6列；[{"column":"cancel_reason","table_rows":732},{"column":"cancelled_date","table_rows":732},{"column":"externally_managed_by","table_rows":732}]</code> |
| A3_constant_nonnull_column | <code>7列；[{"column":"current_term_period_type","value":"Month"},{"column":"initial_term_period_type","value":"Month"},{"column":"is_latest_version","value":"true"}]</code> |
| A4_equal_columns | <code>5组；[{"columns":["subscription_id","account_id","original_id"],"nonnull_equal_rows":732,"meaning_status":"契约未描述含义差别"},{"columns":["bill_to_contact_id","sold_to_contact_id"],"nonnull_equal_rows":732,"meaning_status":"契约未描述含义差别"},{"columns":["current_term_period_type","initial_term_period_type","renewal_term_period_type"],"nonnull_equal_rows":732,"meaning_status":"契约未描述含义差别"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory stg_zuora__subscription [('subscription_id', 'VARCHAR'), ('account_id', 'VARCHAR'), ('auto_renew', 'BOOLEAN'), ('bill_to_contact_id', 'VARCHAR'), ('cancel_reason', 'VARCHAR'), ('cancelled_date', 'TIMESTAMP'), ('contract_acceptance_date', 'TIMESTAMP'), ('contract_effective_date', 'TIMESTAMP'), ('created_by_id', 'VARCHAR'), ('created_date', 'TIMESTAMP'), ('current_term', 'BIGINT'), ('current_term_period_type', 'VARCHAR'), ('default_payment_method_id', 'VARCHAR'), ('externally_managed_by', 'VARCHAR'), ('initial_term', 'BIGINT'), ('initial_term_period_type', 'VARCHAR'), ('invoice_owner_id', 'VARCHAR'), ('is_invoice_separate', 'BOOLEAN'), ('is_latest_version', 'BOOLEAN'), ('last_booking_date', 'DATE'), ('subscription_name', 'VARCHAR'), ('notes', 'VARCHAR'), ('original_created_date', 'TIMESTAMP'), ('original_id', 'VARCHAR'), ('parent_account_id', 'VARCHAR'), ('payment_term', 'VARCHAR'), ('previous_subscription_id', 'VARCHAR'), ('renewal_term', 'BIGINT'), ('renewal_term_period_type', 'VARCHAR'), ('revision', 'BIGINT'), ('service_activation_date', 'TIMESTAMP'), ('sold_to_contact_id', 'VARCHAR'), ('status', 'VARCHAR'), ('subscription_end_date', 'TIMESTAMP'), ('subscription_start_date', 'TIMESTAMP'), ('term_end_date', 'TIMESTAMP'), ('term_start_date', 'TIMESTAMP'), ('term_type', 'VARCHAR'), ('updated_by_id', 'VARCHAR'), ('updated_date', 'TIMESTAMP'), ('version', 'VARCHAR'), ('is_most_recent_record', 'BOOLEAN')]</code> |

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
| 51 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; grep -E 'ERROR&#124;WARNING:&#124;✓&#124;Execution failed&#124;successfully' /tmp/runlog &#124; tail -80</code> | 3588 | true | false |
| 53 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('zuora.duckdb',read_only=True)<br>for t in ['stg_zuora__invoice_item','stg_zuora__rate_plan_charge','stg_zuora__subscription','stg_zuora__account']:<br> print</code> | 6294 | true | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
'int_zuora__subscription_current':('stg_zuora__subscription','is_most_recent_record = TRUE'),
```
event 53 / message

```text
for t in ['stg_zuora__invoice_item','stg_zuora__rate_plan_charge','stg_zuora__subscription','stg_zuora__account']:
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-030.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__subscription.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__subscription.sql`
- S6: `records/006_contract_impl-030.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/result.md`
- S10: `data/024_packages_work/024_impl-030_stg_zuora__subscription/024_impl-030_stg_zuora__subscription.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions`
