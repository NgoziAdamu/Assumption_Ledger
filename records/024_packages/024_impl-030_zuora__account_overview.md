# impl-030 | marts | zuora__account_overview | 差异：S1；日期 原记录

## 契约完整原文

S3:3152–3231

```yaml
    - name: zuora__account_overview
      description: Account-level overview combining current account fields, current contact fields, invoice aggregates, and invoice item counts
      grain: One row per account_id present in int_zuora__account_current
      source_models:
      - intermediate.int_zuora__account_current
      - intermediate.int_zuora__contact_current
      - intermediate.int_zuora__invoice_base
      - intermediate.int_zuora__invoice_item_base
      - intermediate.int_zuora__billing_enriched
      business_logic: '- Base: Start from intermediate.int_zuora__account_current (assumed one current row per account_id). - Contact: Left join intermediate.int_zuora__contact_current on account_id; if no contact row, all contact fields are NULL. - Invoice item count: - Build items_by_account by joining intermediate.int_zuora__invoice_base to intermediate.int_zuora__invoice_item_base on invoice_id, then counting distinct invoice_item_id per account_id. - Left join items_by_account to accounts. The count reflects distinct item IDs across all invoices of the account. If an account has invoices but none have items, the count is 0. If an account has no invoices, there is no items_by_account row and the joined count is NULL. - Invoice aggregates: - Build per_invoice by left joining intermediate.int_zuora__billing_enriched to intermediate.int_zuora__invoice_base on invoice_id, then grouping by account_id to compute: - first_charge_date: earliest non-NULL first_charge_date across the account’s invoices. - total_amount_paid: sum of invoice_amount_paid. - total_amount_not_paid: sum of invoice_amount_unpaid. - total_taxes: sum of tax_amount. - total_invoice_amount: sum of invoice_amount. - Summations skip NULL inputs per row; if an account has invoices but all values for a summed field are NULL, the result is NULL. If an account has no invoices, no per_invoice row exists and all joined aggregates are NULL. - Invoice count: - Compute per account_id using a correlated subquery over intermediate.int_zuora__invoice_base that counts distinct invoices; returns 0 when no invoices exist. - Output: - Select pass-through account fields, joined contact fields, per_invoice.first_charge_date as first_charge_processed_at, items_by_account.invoice_item_count, the scalar invoice_count, and the per_invoice totals. No zero-coalescing, rounding, or casting; all joins from accounts are left joins.'
      columns:
      - name: account_id
        data_type: VARCHAR
        description: Account identifier from int_zuora__account_current; exactly one output row per account_id
        tests:
        - not_null
        - unique
      - name: account_created_at
        data_type: TIMESTAMP
        description: Account created_date from int_zuora__account_current
      - name: account_name
        data_type: VARCHAR
        description: Account name from int_zuora__account_current
      - name: account_number
        data_type: VARCHAR
        description: Account number from int_zuora__account_current
      - name: account_credit_balance
        data_type: VARCHAR
        description: Raw credit_balance from int_zuora__account_current (string as stored; no casting)
      - name: account_zuora_calculated_mrr
        data_type: VARCHAR
        description: Raw mrr from int_zuora__account_current (Zuora-calculated MRR; string as stored)
      - name: account_status
        data_type: VARCHAR
        description: Account status from int_zuora__account_current
      - name: is_auto_pay
        data_type: VARCHAR
        description: Raw auto_pay flag from int_zuora__account_current (string as stored)
      - name: account_country
        data_type: VARCHAR
        description: Country from int_zuora__contact_current.country (NULL if no contact)
      - name: account_city
        data_type: VARCHAR
        description: City from int_zuora__contact_current.city (NULL if no contact)
      - name: account_email
        data_type: VARCHAR
        description: Work email from int_zuora__contact_current.work_email (NULL if no contact)
      - name: account_first_name
        data_type: VARCHAR
        description: First name from int_zuora__contact_current.first_name (NULL if no contact)
      - name: account_last_name
        data_type: VARCHAR
        description: Last name from int_zuora__contact_current.last_name (NULL if no contact)
      - name: account_postal_code
        data_type: VARCHAR
        description: Postal code from int_zuora__contact_current.postal_code (NULL if no contact)
      - name: account_state
        data_type: VARCHAR
        description: State from int_zuora__contact_current.state (NULL if no contact)
      - name: first_charge_processed_at
        data_type: TIMESTAMP
        description: Earliest non-NULL first_charge_date from billing_enriched across all invoices for the account; NULL if no invoices or all values NULL
      - name: invoice_item_count
        data_type: BIGINT
        description: Distinct count of invoice_item_id across all invoices for the account; 0 if invoices exist but no items; NULL if the account has no invoices
      - name: invoice_count
        data_type: BIGINT
        description: Distinct count of invoices for the account; returns 0 when no invoices exist
      - name: total_taxes
        data_type: DOUBLE
        description: Sum of tax_amount across all invoices for the account; NULL if no invoices or if all values are NULL
      - name: total_invoice_amount
        data_type: DOUBLE
        description: Sum of invoice_amount across all invoices for the account; NULL if no invoices or if all values are NULL
      - name: total_amount_paid
        data_type: DOUBLE
        description: Sum of invoice_amount_paid across all invoices for the account; NULL if no invoices or if all values are NULL
      - name: total_amount_not_paid
        data_type: DOUBLE
        description: Sum of invoice_amount_unpaid across all invoices for the account; NULL if no invoices or if all values are NULL
```

## agent 最终 SQL

S4

```sql
WITH items_by_account AS (
    SELECT inv.account_id, count(DISTINCT ii.invoice_item_id) AS invoice_item_count
    FROM intermediate.int_zuora__invoice_base AS inv
    JOIN intermediate.int_zuora__invoice_item_base AS ii ON inv.invoice_id = ii.invoice_id
    GROUP BY inv.account_id
),
per_invoice AS (
    SELECT inv.account_id,
           min(be.first_charge_date) AS first_charge_processed_at,
           sum(inv.invoice_amount_paid) AS total_amount_paid,
           sum(inv.invoice_amount_unpaid) AS total_amount_not_paid,
           sum(inv.tax_amount) AS total_taxes,
           sum(inv.invoice_amount) AS total_invoice_amount
    FROM intermediate.int_zuora__invoice_base AS inv
    LEFT JOIN intermediate.int_zuora__billing_enriched AS be ON inv.invoice_id = be.invoice_id
    GROUP BY inv.account_id
)
SELECT a.account_id,
       a.created_date AS account_created_at,
       a.name AS account_name,
       a.account_number,
       CAST(a.credit_balance AS VARCHAR) AS account_credit_balance,
       CAST(a.mrr AS VARCHAR) AS account_zuora_calculated_mrr,
       a.status AS account_status,
       CAST(a.auto_pay AS VARCHAR) AS is_auto_pay,
       c.country AS account_country,
       c.city AS account_city,
       c.work_email AS account_email,
       c.first_name AS account_first_name,
       c.last_name AS account_last_name,
       c.postal_code AS account_postal_code,
       c.state AS account_state,
       pi.first_charge_processed_at,
       iba.invoice_item_count,
       (SELECT count(DISTINCT i.invoice_id)
        FROM intermediate.int_zuora__invoice_base AS i
        WHERE i.account_id = a.account_id) AS invoice_count,
       pi.total_taxes,
       pi.total_invoice_amount,
       pi.total_amount_paid,
       pi.total_amount_not_paid
FROM intermediate.int_zuora__account_current AS a
LEFT JOIN intermediate.int_zuora__contact_current AS c ON a.account_id = c.account_id
LEFT JOIN items_by_account AS iba ON a.account_id = iba.account_id
LEFT JOIN per_invoice AS pi ON a.account_id = pi.account_id
```

## gold SQL（仅供定位差异）

S5

```sql
with account as (
    select * from intermediate.int_zuora__account_current
),
contact as (
    select * from intermediate.int_zuora__contact_current
),
inv as (
    select * from intermediate.int_zuora__invoice_base
),
items_by_account as (
    select i.account_id, count(distinct iib.invoice_item_id) as invoice_item_count
    from inv i
    left join intermediate.int_zuora__invoice_item_base iib on i.invoice_id = iib.invoice_id
    group by i.account_id
),
per_invoice as (
    select inv.account_id,
           min(ii.first_charge_date) as first_charge_date,
           max(ii.most_recent_charge_date) as most_recent_charge_date,
           sum(inv.invoice_amount_paid) as total_amount_paid,
           sum(inv.invoice_amount_unpaid) as total_amount_not_paid,
           sum(inv.tax_amount) as total_taxes,
           sum(inv.invoice_amount) as total_invoice_amount
    from inv
    left join intermediate.int_zuora__billing_enriched ii on inv.invoice_id = ii.invoice_id
    group by inv.account_id
)
select
    a.account_id as account_id,
    a.created_date as account_created_at,
    a.name as account_name,
    a.account_number,
    a.credit_balance as account_credit_balance,
    a.mrr as account_zuora_calculated_mrr,
    a.status as account_status,
    a.auto_pay as is_auto_pay,
    c.country as account_country,
    c.city as account_city,
    c.work_email as account_email,
    c.first_name as account_first_name,
    c.last_name as account_last_name,
    c.postal_code as account_postal_code,
    c.state as account_state,
    per_invoice.first_charge_date as first_charge_processed_at,
    items_by_account.invoice_item_count,
    (select count(distinct i2.invoice_id) from inv i2 where i2.account_id = a.account_id) as invoice_count,
    per_invoice.total_taxes,
    per_invoice.total_invoice_amount,
    per_invoice.total_amount_paid,
    per_invoice.total_amount_not_paid
from account a
left join contact c on a.account_id = c.account_id
left join per_invoice on a.account_id = per_invoice.account_id
left join items_by_account on items_by_account.account_id = a.account_id
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 3791 | 3791 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"account_id":"00eeae747e2a42ad8f087ee6a47de266"}</code> |
| K2 | <code>{"account_id":"026424b7575e458f91cc8d156e793c5e"}</code> |
| K3 | <code>{"account_id":"02d0f5031be1471da2883436df797323"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_credit_balance | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_zuora_calculated_mrr | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_auto_pay | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_first_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_last_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_postal_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| invoice_item_count | 454 | 454 | 454 | BIGINT | BIGINT |
| invoice_count | 0 | 0 | 0 | BIGINT | BIGINT |
| total_taxes | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_invoice_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_amount_paid | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_amount_not_paid | 0 | 0 | 0 | DOUBLE | DOUBLE |

invoice_item_count 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>13列；[{"column":"account_country","table_rows":3791},{"column":"account_city","table_rows":3791},{"column":"account_email","table_rows":3791}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"invoice_count","value":"0"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory 2026-10-25 06:03:38,793 - WARNING - Skipping zuora__account_overview: missing sql/marts/zuora__account_overview.sql</code> |

## 轨迹索引（不放输出原文）

本题事件总数：73；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print -exec sh -c 'echo --- $1; wc -l "$1"' _ {} \; &amp;&amp; cat config/layer_dependencies.yaml</code> | 3638 | true | false |
| 15 | run | <code>python3 - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(x['staging_contract']['tables']), [t['name'] for t in x['staging_contract']['tables']])<br>print('inter', [m['name</code> | 1273 | true | false |
| 29 | run | <code>cat &gt; /tmp/build_models.py &lt;&lt;'PY'<br>from pathlib import Path<br>P=Path('sql/intermediate')<br>pass_models={<br>'int_zuora__account_current':('stg_zuora__account','is_most_recent_record = TRUE'),<br>'int_zuora__cont</code> | 0 | false | false |
| 31 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8482 | true | false |
| 47 | run | <code>cat &gt; sql/marts/zuora__account_overview.sql &lt;&lt;'SQL'<br>WITH items_by_account AS (<br>    SELECT inv.account_id, count(DISTINCT ii.invoice_item_id) AS invoice_item_count<br>    FROM intermediate.int_zuora__invo</code> | 0 | false | false |
| 49 | run | <code>cat &gt; sql/marts/zuora__monthly_recurring_revenue.sql &lt;&lt;'SQL'<br>WITH month_spine AS (<br>    SELECT DISTINCT account_id, CAST(date_trunc('month', service_start_day) AS DATE) AS account_month<br>    FROM interm</code> | 0 | false | false |
| 51 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; grep -E 'ERROR&#124;WARNING:&#124;✓&#124;Execution failed&#124;successfully' /tmp/runlog &#124; tail -80</code> | 3588 | true | false |
| 55 | run | <code>python3 - &lt;&lt;'PY'<br>p='sql/marts/zuora__line_item_enhanced.sql';s=open(p).read().replace('CASE ii.processing_type WHEN', 'CASE CAST(ii.processing_type AS VARCHAR) WHEN').replace("ii.processing_type = '1'</code> | 1694 | true | false |
| 57 | run | <code>python3 - &lt;&lt;'PY'<br>p='sql/staging/stg_zuora__account.sql';s=open(p).read();s=s.replace('try_cast("balance" AS DECIMAL(18,2)) AS balance,', "CASE WHEN try_cast(\"balance\" AS DECIMAL(18,2)) BETWEEN -1000</code> | 145 | false | false |

### agent action 的 thought/message 命中原句

event 47 / message

```text
Running command: cat > sql/marts/zuora__account_overview.sql <<'SQL'
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-030.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/marts/zuora__account_overview.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/marts/zuora__account_overview.sql`
- S6: `records/006_contract_impl-030.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/result.md`
- S10: `data/024_packages_work/024_impl-030_zuora__account_overview/024_impl-030_zuora__account_overview.json`
- S11: `data/005_cs_work/impl-030_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions`
