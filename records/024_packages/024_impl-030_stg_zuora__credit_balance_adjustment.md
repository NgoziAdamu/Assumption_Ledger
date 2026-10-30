# impl-030 | staging | stg_zuora__credit_balance_adjustment | 差异：S1；日期 原记录

## 契约完整原文

S3:1094–1164

```yaml
    - name: stg_zuora__credit_balance_adjustment
      description: "Cleaned credit balance adjustments; latest snapshot indicator."
      source_table: raw.zuora_credit_balance_adjustment_data
      columns:
        - name: credit_balance_adjustment_id
          data_type: VARCHAR
        - name: account_id
          data_type: VARCHAR
        - name: account_receivable_accounting_code_id
          data_type: VARCHAR
        - name: accounting_code
          data_type: VARCHAR
        - name: adjustment_date
          data_type: DATE
        - name: amount
          data_type: DOUBLE
        - name: amount_home_currency
          data_type: VARCHAR
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: cancelled_on
          data_type: TIMESTAMP
        - name: comment
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: default_payment_method_id
          data_type: VARCHAR
        - name: exchange_rate
          data_type: VARCHAR
        - name: exchange_rate_date
          data_type: DATE
        - name: home_currency
          data_type: VARCHAR
        - name: invoice_id
          data_type: VARCHAR
        - name: journal_entry_id
          data_type: VARCHAR
        - name: number
          data_type: VARCHAR
        - name: parent_account_id
          data_type: VARCHAR
        - name: reason_code
          data_type: VARCHAR
        - name: reference_id
          data_type: VARCHAR
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: source_transaction_id
          data_type: VARCHAR
        - name: source_transaction_number
          data_type: VARCHAR
        - name: source_transaction_type
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
        - name: transaction_currency
          data_type: VARCHAR
        - name: transferred_to_accounting
          data_type: VARCHAR
        - name: type
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
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
    FROM raw.zuora_credit_balance_adjustment_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT
        try_cast("id" AS VARCHAR) AS credit_balance_adjustment_id,
        try_cast("id" AS VARCHAR) AS account_id,
        try_cast("account_receivable_accounting_code_id" AS VARCHAR) AS account_receivable_accounting_code_id,
        try_cast("accounting_code" AS VARCHAR) AS accounting_code,
        try_cast("adjustment_date" AS DATE) AS adjustment_date,
        try_cast("amount" AS DOUBLE) AS amount,
        try_cast("amount_home_currency" AS VARCHAR) AS amount_home_currency,
        try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
        try_cast("cancelled_on" AS TIMESTAMP) AS cancelled_on,
        try_cast("comment" AS VARCHAR) AS comment,
        try_cast("created_by_id" AS VARCHAR) AS created_by_id,
        try_cast("created_date" AS TIMESTAMP) AS created_date,
        try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
        try_cast("exchange_rate" AS VARCHAR) AS exchange_rate,
        try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date,
        try_cast("home_currency" AS VARCHAR) AS home_currency,
        try_cast("id" AS VARCHAR) AS invoice_id,
        try_cast("journal_entry_id" AS VARCHAR) AS journal_entry_id,
        try_cast("number" AS VARCHAR) AS number,
        try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
        try_cast("reason_code" AS VARCHAR) AS reason_code,
        try_cast("reference_id" AS VARCHAR) AS reference_id,
        try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
        try_cast("source_transaction_id" AS VARCHAR) AS source_transaction_id,
        try_cast("source_transaction_number" AS VARCHAR) AS source_transaction_number,
        try_cast("source_transaction_type" AS VARCHAR) AS source_transaction_type,
        try_cast("status" AS VARCHAR) AS status,
        try_cast("transaction_currency" AS VARCHAR) AS transaction_currency,
        try_cast("transferred_to_accounting" AS VARCHAR) AS transferred_to_accounting,
        try_cast("type" AS VARCHAR) AS type,
        try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
        try_cast("updated_date" AS TIMESTAMP) AS updated_date,
        row_number() over (partition by id order by try_cast(updated_date as timestamp) desc NULLS LAST) = 1 AS is_most_recent_record
FROM source_rows
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select * from raw.zuora_credit_balance_adjustment_data
    where _fivetran_deleted is null or _fivetran_deleted = false
),
final as (
    select
        id as credit_balance_adjustment_id,
        account_id,
        account_receivable_accounting_code_id,
        accounting_code,
        adjustment_date,
        amount,
        amount_home_currency,
        bill_to_contact_id,
        cast(cancelled_on as TIMESTAMP) as cancelled_on,
        comment,
        created_by_id,
        cast(created_date as TIMESTAMP) as created_date,
        default_payment_method_id,
        exchange_rate,
        exchange_rate_date,
        home_currency,
        invoice_id,
        journal_entry_id,
        number,
        parent_account_id,
        reason_code,
        reference_id,
        sold_to_contact_id,
        source_transaction_id,
        source_transaction_number,
        source_transaction_type,
        status,
        transaction_currency,
        transferred_to_accounting,
        type,
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
| 6 | 6 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"credit_balance_adjustment_id":"dff38ac013d167917d82b246268e5b83"}</code> |
| K2 | <code>{"credit_balance_adjustment_id":"dff38ac015cf0d852d3dfff06e63a038"}</code> |
| K3 | <code>{"credit_balance_adjustment_id":"dff38ac015cf0d852d3dfff06e63a039"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| credit_balance_adjustment_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 6 | 6 | 6 | VARCHAR | VARCHAR |
| account_receivable_accounting_code_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| accounting_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| adjustment_date | 0 | 0 | 0 | DATE | DATE |
| amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| amount_home_currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| bill_to_contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| cancelled_on | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| comment | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| default_payment_method_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| exchange_rate | 0 | 0 | 0 | VARCHAR | VARCHAR |
| exchange_rate_date | 0 | 0 | 0 | DATE | DATE |
| home_currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| invoice_id | 6 | 6 | 6 | VARCHAR | VARCHAR |
| journal_entry_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| parent_account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| reason_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| reference_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sold_to_contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| source_transaction_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| source_transaction_number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| source_transaction_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| transaction_currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| transferred_to_accounting | 0 | 0 | 0 | VARCHAR | VARCHAR |
| type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| is_most_recent_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

account_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | dff38ac013d167917d82b246268e5b83 | dff38ac0c42164706d15f0e7fee92ab2 |
| K2 | dff38ac015cf0d852d3dfff06e63a038 | dff38ac05ae066e479f6ba9b68a23d47 |
| K3 | dff38ac015cf0d852d3dfff06e63a039 | dff38ac05ae066e479f6ba9b68a23d47 |

invoice_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | dff38ac013d167917d82b246268e5b83 | dff38ac0dfa53a25cf026658c1631e92 |
| K2 | dff38ac015cf0d852d3dfff06e63a038 | dff38ac0ea5bbc65bce34ebdb935e174 |
| K3 | dff38ac015cf0d852d3dfff06e63a039 | dff38ac0ea5bbc65bce34ebdb935e174 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>6列；[{"column":"amount_home_currency","table_rows":6},{"column":"cancelled_on","table_rows":6},{"column":"comment","table_rows":6}]</code> |
| A3_constant_nonnull_column | <code>12列；[{"column":"account_receivable_accounting_code_id","value":"dff38ac0507cfccf7b1585994a315868"},{"column":"accounting_code","value":"Customer Cash on Account"},{"column":"adjustment_date","value":"2016-01-15"}]</code> |
| A4_equal_columns | <code>5组；[{"columns":["credit_balance_adjustment_id","account_id","invoice_id"],"nonnull_equal_rows":6,"meaning_status":"契约未描述含义差别"},{"columns":["adjustment_date","exchange_rate_date"],"nonnull_equal_rows":6,"meaning_status":"契约未描述含义差别"},{"columns":["bill_to_contact_id","sold_to_contact_id"],"nonnull_equal_rows":6,"meaning_status":"契约未描述含义差别"}]</code> |

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

### agent action 的 thought/message 命中原句

event 29 / message

```text
    FROM staging.stg_zuora__credit_balance_adjustment
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-030.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__credit_balance_adjustment.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__credit_balance_adjustment.sql`
- S6: `records/006_contract_impl-030.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/result.md`
- S10: `data/024_packages_work/024_impl-030_stg_zuora__credit_balance_adjustment/024_impl-030_stg_zuora__credit_balance_adjustment.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions`
