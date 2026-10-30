# impl-030 | staging | stg_zuora__invoice_item | 差异：S1；日期 原记录

## 契约完整原文

S3:282–385

```yaml
    - name: stg_zuora__invoice_item
      description: "Cleaned invoice line items with safe casting of dates and derived service period buckets; latest snapshot indicator provided."
      source_table: raw.zuora_invoice_item_data
      columns:
        - name: invoice_item_id
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: account_receivable_accounting_code_id
          data_type: VARCHAR
        - name: accounting_code
          data_type: VARCHAR
        - name: amendment_id
          data_type: VARCHAR
        - name: applied_to_invoice_item_id
          data_type: VARCHAR
        - name: balance
          data_type: BIGINT
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: charge_amount
          data_type: BIGINT
        - name: charge_amount_home_currency
          data_type: VARCHAR
        - name: charge_date
          data_type: TIMESTAMP
          source_expression: "try_cast(charge_date as TIMESTAMP)"
        - name: charge_name
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
          source_expression: "try_cast(created_date as TIMESTAMP)"
        - name: deferred_revenue_accounting_code_id
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
        - name: parent_account_id
          data_type: VARCHAR
        - name: processing_type
          data_type: BOOLEAN
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_charge_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: quantity
          data_type: BIGINT
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
          data_type: VARCHAR
        - name: recognized_revenue_accounting_code_id
          data_type: VARCHAR
        - name: rev_rec_start_date
          data_type: TIMESTAMP
          source_expression: "try_cast(rev_rec_start_date as TIMESTAMP)"
        - name: service_end_date
          data_type: DATE
          source_expression: "try_cast(service_end_date as DATE)"
        - name: service_start_date
          data_type: DATE
          source_expression: "try_cast(service_start_date as DATE)"
        - name: sku
          data_type: VARCHAR
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: source_item_type
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: tax_amount
          data_type: BIGINT
        - name: tax_mode
          data_type: VARCHAR
        - name: transaction_currency
          data_type: VARCHAR
        - name: unit_price
          data_type: BIGINT
        - name: uom
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
          source_expression: "cast(updated_date as TIMESTAMP)"
        - name: is_most_recent_record
          data_type: BOOLEAN
          source_expression: "row_number() over (partition by id order by updated_date desc) = 1"
      row_filters:
        - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
          on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_invoice_item_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT
        id AS invoice_item_id,
        try_cast("id" AS VARCHAR) AS account_id,
        try_cast("account_receivable_accounting_code_id" AS VARCHAR) AS account_receivable_accounting_code_id,
        try_cast("accounting_code" AS VARCHAR) AS accounting_code,
        try_cast("id" AS VARCHAR) AS amendment_id,
        try_cast("applied_to_invoice_item_id" AS VARCHAR) AS applied_to_invoice_item_id,
        try_cast("balance" AS BIGINT) AS balance,
        try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
        try_cast("charge_amount" AS BIGINT) AS charge_amount,
        try_cast("charge_amount_home_currency" AS VARCHAR) AS charge_amount_home_currency,
        try_cast(charge_date as TIMESTAMP) AS charge_date,
        try_cast("charge_name" AS VARCHAR) AS charge_name,
        try_cast("created_by_id" AS VARCHAR) AS created_by_id,
        try_cast(created_date as TIMESTAMP) AS created_date,
        try_cast("deferred_revenue_accounting_code_id" AS VARCHAR) AS deferred_revenue_accounting_code_id,
        try_cast("exchange_rate" AS VARCHAR) AS exchange_rate,
        try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date,
        try_cast("home_currency" AS VARCHAR) AS home_currency,
        try_cast("id" AS VARCHAR) AS invoice_id,
        try_cast("journal_entry_id" AS VARCHAR) AS journal_entry_id,
        try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
        try_cast("processing_type" AS BOOLEAN) AS processing_type,
        try_cast("id" AS VARCHAR) AS product_id,
        try_cast("product_rate_plan_charge_id" AS VARCHAR) AS product_rate_plan_charge_id,
        try_cast("id" AS VARCHAR) AS product_rate_plan_id,
        try_cast("quantity" AS BIGINT) AS quantity,
        try_cast("id" AS VARCHAR) AS rate_plan_charge_id,
        try_cast("id" AS VARCHAR) AS rate_plan_id,
        try_cast("recognized_revenue_accounting_code_id" AS VARCHAR) AS recognized_revenue_accounting_code_id,
        try_cast(rev_rec_start_date as TIMESTAMP) AS rev_rec_start_date,
        try_cast(service_end_date as DATE) AS service_end_date,
        try_cast(service_start_date as DATE) AS service_start_date,
        try_cast("sku" AS VARCHAR) AS sku,
        try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
        try_cast("source_item_type" AS VARCHAR) AS source_item_type,
        try_cast("id" AS VARCHAR) AS subscription_id,
        try_cast("tax_amount" AS BIGINT) AS tax_amount,
        try_cast("tax_mode" AS VARCHAR) AS tax_mode,
        try_cast("transaction_currency" AS VARCHAR) AS transaction_currency,
        try_cast("unit_price" AS BIGINT) AS unit_price,
        try_cast("uom" AS VARCHAR) AS uom,
        try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
        try_cast(updated_date as TIMESTAMP) AS updated_date,
        row_number() over (partition by id order by updated_date desc) = 1 AS is_most_recent_record
FROM source_rows
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select * from raw.zuora_invoice_item_data
    where _fivetran_deleted is null or _fivetran_deleted = false
),
final as (
    select
        id as invoice_item_id,
        account_id,
        account_receivable_accounting_code_id,
        accounting_code,
        amendment_id,
        applied_to_invoice_item_id,
        balance,
        bill_to_contact_id,
        charge_amount,
        charge_amount_home_currency,
        try_cast(charge_date as TIMESTAMP) as charge_date,
        charge_name,
        created_by_id,
        try_cast(created_date as TIMESTAMP) as created_date,
        deferred_revenue_accounting_code_id,
        exchange_rate,
        exchange_rate_date,
        home_currency,
        invoice_id,
        journal_entry_id,
        parent_account_id,
        processing_type,
        product_id,
        product_rate_plan_charge_id,
        product_rate_plan_id,
        quantity,
        rate_plan_charge_id,
        rate_plan_id,
        recognized_revenue_accounting_code_id,
        try_cast(rev_rec_start_date as TIMESTAMP) as rev_rec_start_date,
        try_cast(service_end_date as DATE) as service_end_date,
        try_cast(service_start_date as DATE) as service_start_date,
        sku,
        sold_to_contact_id,
        source_item_type,
        subscription_id,
        tax_amount,
        tax_mode,
        transaction_currency,
        unit_price,
        uom,
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
| 1495 | 1495 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"invoice_item_id":"0039e61a9bed44c3a0b226317af17c1e"}</code> |
| K2 | <code>{"invoice_item_id":"003e697c138945f399cd6c0c3c64d4e1"}</code> |
| K3 | <code>{"invoice_item_id":"00535fb82ea2401b8869f5beee41c83c"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| invoice_item_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 1495 | 1495 | 1495 | VARCHAR | VARCHAR |
| account_receivable_accounting_code_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| accounting_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| amendment_id | 1495 | 1495 | 1495 | VARCHAR | VARCHAR |
| applied_to_invoice_item_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| balance | 1490 | 1490 | 1490 | BIGINT | VARCHAR |
| bill_to_contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| charge_amount | 0 | 0 | 0 | BIGINT | VARCHAR |
| charge_amount_home_currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| charge_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| charge_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| deferred_revenue_accounting_code_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| exchange_rate | 0 | 0 | 0 | VARCHAR | VARCHAR |
| exchange_rate_date | 1490 | 1490 | 1490 | DATE | VARCHAR |
| home_currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| invoice_id | 1495 | 1495 | 1495 | VARCHAR | VARCHAR |
| journal_entry_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| parent_account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| processing_type | 1495 | 1495 | 1495 | BOOLEAN | VARCHAR |
| product_id | 1495 | 1495 | 1495 | VARCHAR | VARCHAR |
| product_rate_plan_charge_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| product_rate_plan_id | 1495 | 1495 | 1495 | VARCHAR | VARCHAR |
| quantity | 0 | 0 | 0 | BIGINT | VARCHAR |
| rate_plan_charge_id | 1495 | 1495 | 1495 | VARCHAR | VARCHAR |
| rate_plan_id | 1495 | 1495 | 1495 | VARCHAR | VARCHAR |
| recognized_revenue_accounting_code_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| rev_rec_start_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| service_end_date | 0 | 0 | 0 | DATE | DATE |
| service_start_date | 0 | 0 | 0 | DATE | DATE |
| sku | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sold_to_contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| source_item_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subscription_id | 1495 | 1495 | 1495 | VARCHAR | VARCHAR |
| tax_amount | 0 | 0 | 0 | BIGINT | VARCHAR |
| tax_mode | 0 | 0 | 0 | VARCHAR | VARCHAR |
| transaction_currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| unit_price | 0 | 0 | 0 | BIGINT | VARCHAR |
| uom | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| is_most_recent_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

account_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0039e61a9bed44c3a0b226317af17c1e | Subscription Revenue |
| K2 | 003e697c138945f399cd6c0c3c64d4e1 | Subscription Revenue |
| K3 | 00535fb82ea2401b8869f5beee41c83c | Subscription Revenue |

amendment_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0039e61a9bed44c3a0b226317af17c1e | 2023-10-06 02:25:48.000000 |
| K2 | 003e697c138945f399cd6c0c3c64d4e1 | 2020-03-16 11:42:16.000000 |
| K3 | 00535fb82ea2401b8869f5beee41c83c | 2022-08-20 01:13:12.000000 |

balance 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 8ad0965d7ba11a18017ba1983ba31908 |
| K2 | null | 2c92c0946736733a016750d344222932 |
| K3 | null | 2c92c0946736733a016750d344222932 |

exchange_rate_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | SKU-442712 |
| K2 | null | SKU-734164 |
| K3 | null | SKU-393623 |

invoice_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0039e61a9bed44c3a0b226317af17c1e | 0 |
| K2 | 003e697c138945f399cd6c0c3c64d4e1 | 0 |
| K3 | 00535fb82ea2401b8869f5beee41c83c | 0 |

processing_type 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 2c92c0946736733a016750d344222932 |
| K2 | null | 8ad0965d7ba11a18017ba1983ba31908 |
| K3 | null | 2c92c0946736733a016750d344222932 |

product_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0039e61a9bed44c3a0b226317af17c1e | 2020-05-02 11:26:18.000000 |
| K2 | 003e697c138945f399cd6c0c3c64d4e1 | 2020-01-15 13:51:24.000000 |
| K3 | 00535fb82ea2401b8869f5beee41c83c | 2023-09-20 18:10:16.000000 |

product_rate_plan_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0039e61a9bed44c3a0b226317af17c1e | null |
| K2 | 003e697c138945f399cd6c0c3c64d4e1 | null |
| K3 | 00535fb82ea2401b8869f5beee41c83c | null |

rate_plan_charge_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0039e61a9bed44c3a0b226317af17c1e | null |
| K2 | 003e697c138945f399cd6c0c3c64d4e1 | null |
| K3 | 00535fb82ea2401b8869f5beee41c83c | null |

rate_plan_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0039e61a9bed44c3a0b226317af17c1e | null |
| K2 | 003e697c138945f399cd6c0c3c64d4e1 | null |
| K3 | 00535fb82ea2401b8869f5beee41c83c | null |

subscription_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0039e61a9bed44c3a0b226317af17c1e | null |
| K2 | 003e697c138945f399cd6c0c3c64d4e1 | null |
| K3 | 00535fb82ea2401b8869f5beee41c83c | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"rev_rec_start_date","table_rows":1495}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"is_most_recent_record","value":"true"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["invoice_item_id","account_id","amendment_id","invoice_id","product_id","product_rate_plan_id","rate_plan_charge_id","rate_plan_id","subscription_id"],"nonnull_equal_rows":1495,"meaning_status":"契约未描述含义差别"},{"columns":["charge_date","created_date","updated_date"],"nonnull_equal_rows":5,"meaning_status":"契约未描述含义差别"}]</code> |

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
| 61 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('zuora.duckdb',read_only=True)<br>print(c.execute('select processing_type,count(*) from raw.zuora_invoice_item_data group by 1').fetchall())<br>print(c.execut</code> | 126 | false | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
FROM staging.stg_zuora__invoice_item AS ii
```
event 29 / message

```text
    FROM staging.stg_zuora__invoice_item
```
event 29 / message

```text
    FROM staging.stg_zuora__invoice_item
```
event 29 / message

```text
    FROM staging.stg_zuora__invoice_item
```
event 53 / message

```text
for t in ['stg_zuora__invoice_item','stg_zuora__rate_plan_charge','stg_zuora__subscription','stg_zuora__account']:
```
event 61 / message

```text
print(c.execute('select processing_type,count(*) from staging.stg_zuora__invoice_item group by 1').fetchall())
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-030.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice_item.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__invoice_item.sql`
- S6: `records/006_contract_impl-030.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/result.md`
- S10: `data/024_packages_work/024_impl-030_stg_zuora__invoice_item/024_impl-030_stg_zuora__invoice_item.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions`
