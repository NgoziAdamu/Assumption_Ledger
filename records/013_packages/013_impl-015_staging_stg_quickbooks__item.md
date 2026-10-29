# impl-015 | staging | stg_quickbooks__item | 差异：S1；日期 原记录

## 契约完整原文

S3:407–461

```yaml
    - name: stg_quickbooks__item
      description: "Cleaned product and service items with standardized pricing and inventory information"
      source_table: "raw.item_data"
      columns:
        - name: item_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: parent_item_id
          data_type: VARCHAR
        - name: income_account_id
          data_type: VARCHAR
        - name: expense_account_id
          data_type: VARCHAR
        - name: asset_account_id
          data_type: VARCHAR
        - name: tax_code_id
          data_type: VARCHAR
        - name: sales_tax_code_id
          data_type: VARCHAR
        - name: purchase_tax_code_id
          data_type: VARCHAR
        - name: name
          data_type: VARCHAR
          constraints: [not_null]
        - name: description
          data_type: VARCHAR
        - name: fully_qualified_name
          data_type: VARCHAR
        - name: sku
          data_type: VARCHAR
        - name: type
          data_type: VARCHAR
        - name: unit_price
          data_type: DECIMAL(28,6)
        - name: purchase_cost
          data_type: DECIMAL(28,6)
        - name: quantity_on_hand
          data_type: DECIMAL(28,6)
        - name: is_active
          data_type: BOOLEAN
        - name: is_taxable
          data_type: BOOLEAN
        - name: track_quantity_on_hand
          data_type: BOOLEAN
        - name: created_at
          data_type: TIMESTAMP
        - name: updated_at
          data_type: TIMESTAMP
        - name: sync_token
          data_type: VARCHAR
        - name: source_relation
          data_type: VARCHAR
      filter_conditions:
        - "id is not null and name is not null and track_quantity_on_hand is not null"

```

## agent 最终 SQL

S4

```sql
WITH typed AS (
    SELECT
        CAST(r.id AS VARCHAR) AS "item_id",
        CAST(r.parent_item_id AS VARCHAR) AS "parent_item_id",
        CAST(r.income_account_id AS VARCHAR) AS "income_account_id",
        CAST(r.expense_account_id AS VARCHAR) AS "expense_account_id",
        CAST(r.asset_account_id AS VARCHAR) AS "asset_account_id",
        CAST(r.sales_tax_code_id AS VARCHAR) AS "tax_code_id",
        CAST(r.sales_tax_code_id AS VARCHAR) AS "sales_tax_code_id",
        CAST(r.purchase_tax_code_id AS VARCHAR) AS "purchase_tax_code_id",
        CAST(r.name AS VARCHAR) AS "name",
        CAST(r.description AS VARCHAR) AS "description",
        CAST(r.fully_qualified_name AS VARCHAR) AS "fully_qualified_name",
        CAST(r.stock_keeping_unit AS VARCHAR) AS "sku",
        CAST(r.type AS VARCHAR) AS "type",
        TRY_CAST(r.unit_price AS DECIMAL(28,6)) AS "unit_price",
        TRY_CAST(r.purchase_cost AS DECIMAL(28,6)) AS "purchase_cost",
        TRY_CAST(r.quantity_on_hand AS DECIMAL(28,6)) AS "quantity_on_hand",
        TRY_CAST(r.active AS BOOLEAN) AS "is_active",
        TRY_CAST(r.taxable AS BOOLEAN) AS "is_taxable",
        TRY_CAST(r.track_quantity_on_hand AS BOOLEAN) AS "track_quantity_on_hand",
        TRY_CAST(r.created_at AS TIMESTAMP) AS "created_at",
        TRY_CAST(r.updated_at AS TIMESTAMP) AS "updated_at",
        CAST(r.sync_token AS VARCHAR) AS "sync_token",
        'quickbooks' AS "source_relation"
    FROM raw.item_data AS r
)
SELECT * FROM typed
WHERE (item_id IS NOT NULL AND name IS NOT NULL AND track_quantity_on_hand IS NOT NULL)
```

## gold SQL（仅供定位差异）

S5

```sql
with source as (
    select *
    from raw.item_data
)

select
    cast(id as varchar) as item_id,
    cast(parent_item_id as varchar) as parent_item_id,
    cast(income_account_id as varchar) as income_account_id,
    cast(expense_account_id as varchar) as expense_account_id,
    cast(asset_account_id as varchar) as asset_account_id,
    cast(null as varchar) as tax_code_id,
    cast(sales_tax_code_id as varchar) as sales_tax_code_id,
    cast(purchase_tax_code_id as varchar) as purchase_tax_code_id,
    cast(name as varchar) as name,
    cast(description as varchar) as description,
    cast(fully_qualified_name as varchar) as fully_qualified_name,
    cast(stock_keeping_unit as varchar) as sku,
    cast(type as varchar) as type,
    case
        when cast(unit_price as decimal(28,6)) is not null and (cast(unit_price as decimal(28,6)) < -999999.99 or cast(unit_price as decimal(28,6)) > 999999.99)
        then null
        else cast(unit_price as decimal(28,6))
    end as unit_price,
    case
        when cast(purchase_cost as decimal(28,6)) is not null and (cast(purchase_cost as decimal(28,6)) < -999999.99 or cast(purchase_cost as decimal(28,6)) > 999999.99)
        then null
        else cast(purchase_cost as decimal(28,6))
    end as purchase_cost,
    cast(quantity_on_hand as decimal(28,6)) as quantity_on_hand,
    cast(active as boolean) as is_active,
    cast(taxable as boolean) as is_taxable,
    cast(track_quantity_on_hand as boolean) as track_quantity_on_hand,
    strptime(created_at, '%Y-%m-%d %H:%M:%S.%f %z') as created_at,
    strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f %z') as updated_at,
    cast(sync_token as varchar) as sync_token,
    'main' as source_relation
from source
where id is not null and name is not null and track_quantity_on_hand is not null
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2000 | 2000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"item_id":"itm00051258218"}</code> |
| K2 | <code>{"item_id":"itm00052239746"}</code> |
| K3 | <code>{"item_id":"itm00052832660"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| item_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| parent_item_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| income_account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| expense_account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| asset_account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| tax_code_id | 2000 | 2000 | 2000 | VARCHAR | VARCHAR |
| sales_tax_code_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| purchase_tax_code_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| fully_qualified_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sku | 0 | 0 | 0 | VARCHAR | VARCHAR |
| type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| unit_price | 0 | 0 | 0 | DECIMAL(28,6) | DECIMAL(28,6) |
| purchase_cost | 0 | 0 | 0 | DECIMAL(28,6) | DECIMAL(28,6) |
| quantity_on_hand | 0 | 0 | 0 | DECIMAL(28,6) | DECIMAL(28,6) |
| is_active | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_taxable | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| track_quantity_on_hand | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| sync_token | 0 | 0 | 0 | VARCHAR | VARCHAR |

tax_code_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 21999955356 | null |
| K2 | 47881215281 | null |
| K3 | 79916828398 | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>3列；[{"column":"parent_item_id","table_rows":2000},{"column":"created_at","table_rows":2000},{"column":"updated_at","table_rows":2000}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"source_relation","value":"quickbooks"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["tax_code_id","sales_tax_code_id"],"nonnull_equal_rows":2000,"meaning_status":"契约未描述含义差别"},{"columns":["name","fully_qualified_name"],"nonnull_equal_rows":2000,"meaning_status":"契约未描述含义差别"}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"source_relation","expression":["'quickbooks'"]}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=8；assistant_trajectory       'stg_quickbooks__item':'item_id IS NOT NULL AND name IS NOT NULL AND track_quantity_on_hand IS NOT NULL',</code> |

## 轨迹索引（不放输出原文）

本题事件总数：75；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 12257 | true | false |
| 13 | run | <code>find sql -maxdepth 3 -type f -print; sed -n '240,520p' run.py; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('quickbooks_start.duckdb',read_only=True)<br>print(c.execute("show all tables").fetchall()[:5</code> | 53948 | false | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml<br>c=duckdb.connect('quickbooks_start.duckdb',read_only=True)<br>for n in ['account_data','bill_data','bill_line_data','customer_data','department_data','invoice_data','in</code> | 5491 | false | false |
| 17 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/gen_stage.py &lt;&lt;'PY'<br>import yaml, pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']<br>rawmap={'account_id'</code> | 0 | false | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob<br>c=duckdb.connect('quickbooks_start.duckdb',read_only=True)<br>for f in glob.glob('sql/staging/*.sql'):<br> s=open(f).read();<br> try:c.execute('select * from ('+s+') x limit </code> | 2847 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>p='/tmp/gen_stage.py'<br>s=open(p).read(); s=s.replace("for t in contract['tables']:\n    name=t['name']; src=t['source_table']", "special={'stg_quickbooks__account':{'account_id':'id','i</code> | 602 | false | false |
| 25 | run | <code>cat &gt; sql/intermediate/int_quickbooks__account_classifications.sql &lt;&lt;'SQL'<br>WITH account_base AS (<br>    SELECT * FROM staging.stg_quickbooks__account<br>),<br>classified AS (<br>    SELECT a.*,<br>        COALESCE(</code> | 0 | false | false |
| 27 | run | <code>cat &gt; sql/intermediate/int_quickbooks__invoice_double_entry.sql &lt;&lt;'SQL'<br>WITH ar_accounts AS (<br> SELECT account_id,source_relation FROM staging.stg_quickbooks__account WHERE account_type='Accounts Recei</code> | 0 | false | false |
| 31 | run | <code>cat &gt; sql/intermediate/int_quickbooks__vendor_spend_analysis.sql &lt;&lt;'SQL'<br>WITH bills AS (SELECT *,transaction_date bill_date,balance outstanding_balance,total_amount-COALESCE(balance,0) paid_amount,dat</code> | 0 | false | false |
| 37 | run | <code>cat &gt; sql/marts/quickbooks__cashflow_forecast.sql &lt;&lt;'SQL'<br>WITH cash AS (SELECT * FROM intermediate.int_quickbooks__cashflow_analysis), future AS (SELECT date_trunc('month',expected_cash_date)::DATE fo</code> | 0 | false | false |
| 41 | run | <code>grep -E 'ERROR - ✗&#124;Executing: staging&#124;staging\.' /tmp/runlog &#124; head -100</code> | 6111 | true | false |
| 43 | run | <code>head -40 /tmp/runlog; ls -l quickbooks.duckdb &#124;&#124; true; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('quickbooks.duckdb')<br>print(c.execute("select schema_name from information_schema.schemata").fetcha</code> | 10396 | false | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>p='/tmp/gen_stage.py';s=open(p).read();s=s.replace("'stg_quickbooks__bill':{'bill_id':'id'}", "'stg_quickbooks__bill':{'bill_id':'id'}")<br>s=s.replace("'stg_quickbooks__department':{'dep</code> | 0 | false | false |
| 61 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob,os<br>c=duckdb.connect('quickbooks.duckdb',read_only=True)<br>for s in ['staging','intermediate','marts']:<br> print('\n',s)<br> for (t,) in c.execute(f"select table_name from i</code> | 1080 | true | false |

### agent action 的 thought/message 命中原句

event 17 / message

```text
      elif name=='stg_quickbooks__item': where.append('item_id IS NOT NULL AND name IS NOT NULL AND track_quantity_on_hand IS NOT NULL')
```
event 21 / message

```text
s=open(p).read(); s=s.replace("for t in contract['tables']:\n    name=t['name']; src=t['source_table']", "special={'stg_quickbooks__account':{'account_id':'id','is_active':'active','is_sub_account':'sub_account'},'stg_quickbooks__bill':{'bill_id':'id'},'stg_quickbooks__customer':{'customer_id':'id','sales_term_id':'sales_term_id','tax_code_id':'default_tax_code_id','name':'given_name','is_active':'active','is_job':'job','is_taxable':'taxable'},'stg_quickbooks__department':{'department_id':'id','is_active':'active','is_sub_department':'sub_department'},'stg_quickbooks__invoice':{'invoice_id':'id','global_tax_calculation':'global_tax_calculation'},'stg_quickbooks__invoice_line':{'invoice_id':'invoice_id','sales_item_item_id':'item_id','sales_item_quantity':'sales_item_quantity','sales_item_discount_amount':'sales_item_discount_amount','discount_percent':'discount_discount_percent'},'stg_quickbooks__item':{'item_id':'id','sku':'stock_keeping_unit','tax_code_id':'sales_tax_code_id'},'stg_quickbooks__journal_entry':{'journal_entry_id':'id','is_adjustment':'adjustment'},'stg_quickbooks__journal_entry_line':{'journal_entry_id':'journal_entry_id'},'stg_quickbooks__payment':{'payment_id':'id','payment_ref_number':'reference_number'},'stg_quickbooks__payment_line':{'payment_id':'payment_id'},'stg_quickbooks__vendor':{'vendor_id':'id','sales_term_id':'term_id','acct_num':'account_number'}}\nfor t in contract['tables']:\n    name=t['name']; src=t['source_table']; rawcols={r[0] for r in __import__('duckdb').connect('quickbooks_start.duckdb',read_only=True).execute(f'describe {src}').fetchall()}")
```
event 25 / message

```text
    LEFT JOIN staging.stg_quickbooks__item i ON l.item_expense_item_id=i.item_id AND l.source_relation=i.source_relation
```
event 27 / message

```text
 LEFT JOIN staging.stg_quickbooks__item it ON l.sales_item_item_id=it.item_id AND l.source_relation=it.source_relation
```
event 31 / message

```text
FROM staging.stg_quickbooks__bill_line l LEFT JOIN staging.stg_quickbooks__item it ON l.item_expense_item_id=it.item_id AND l.source_relation=it.source_relation WHERE l.amount>0),
```
event 37 / message

```text
WITH inv AS (SELECT * FROM intermediate.int_quickbooks__revenue_analysis), line_cost AS (SELECT l.invoice_id,l.sales_item_item_id item_id,l.sales_item_quantity quantity,l.amount line_revenue,COALESCE(i.purchase_cost,0)::DECIMAL(28,6) unit_cost,COALESCE(l.sales_item_quantity,0)*COALESCE(i.purchase_cost,0) total_item_cost,l.amount-COALESCE(l.sales_item_quantity,0)*COALESCE(i.purchase_cost,0) line_gross_profit,CASE WHEN l.amount>0 THEN round((l.amount-COALESCE(l.sales_item_quantity,0)*COALESCE(i.purchase_cost,0))/l.amount*100,2) ELSE 0 END line_gross_margin_pct FROM staging.stg_quickbooks__invoice_line l JOIN staging.stg_quickbooks__item i ON l.sales_item_item_id=i.item_id AND l.source_relation=i.source_relation WHERE l.sales_item_item_id IS NOT NULL AND l.amount>0), ip AS (SELECT v.invoice_id,v.customer_id,v.transaction_date,v.revenue_month_start,v.revenue_year,v.revenue_quarter,v.total_amount invoice_total,v.collected_amount,v.outstanding_balance,v.customer_tier,v.invoice_size_category,sum(l.total_item_cost)::DECIMAL(38,12) total_cogs,sum(l.line_gross_profit)::DECIMAL(38,12) gross_profit,CASE WHEN v.total_amount>0 THEN round(sum(l.line_gross_profit)/v.total_amount*100,2) ELSE 0 END invoice_gross_margin_pct,count(DISTINCT l.item_id) unique_products,sum(l.quantity)::DECIMAL(38,6) total_quantity,avg(l.line_gross_margin_pct) avg_product_margin,CASE WHEN sum(l.line_gross_profit)/nullif(v.total_amount,0)>.4 THEN 'Highly Profitable' WHEN sum(l.line_gross_profit)/nullif(v.total_amount,0)>.2 THEN 'Profitable' WHEN sum(l.line_gross_profit)/nullif(v.total_amount,0)>.1 THEN 'Marginally Profitable' WHEN sum(l.line_gross_profit)/nullif(v.total_amount,0)>0 THEN 'Break Even' ELSE 'Loss Making' END profitability_tier FROM inv v LEFT JOIN line_cost l USING(invoice_id) GROUP BY v.invoice_id,v.customer_id,v.transaction_date,v.revenue_month_start,v.revenue_year,v.revenue_quarter,v.total_amount,v.collected_amount,v.outstanding_balance,v.customer_tier,v.invoice_size_category), customer AS (SELECT customer_id,sum(invoice_total)::DECIMAL(38,6) customer_total_revenue,sum(gross_profit)::DECIMAL(38,12) customer_total_profit,CASE WHEN sum(invoice_total)>0 THEN round(sum(gross_profit)/sum(invoice_total)*100,2) ELSE 0 END customer_gross_margin_pct,avg(gross_profit) customer_avg_profit_per_invoice,stddev_samp(invoice_gross_margin_pct) customer_margin_volatility,sum(CASE WHEN revenue_month_start>=date_trunc('month',current_date-INTERVAL 6 MONTH) THEN gross_profit ELSE 0 END)::DECIMAL(38,12) customer_profit_last_6_months,sum(CASE WHEN revenue_month_start>=date_trunc('month',current_date-INTERVAL 12 MONTH) AND revenue_month_start<date_trunc('month',current_date-INTERVAL 6 MONTH) THEN gross_profit ELSE 0 END)::DECIMAL(38,12) customer_profit_prev_6_months FROM ip GROUP BY customer_id), monthly AS (SELECT revenue_month_start,sum(invoice_total)::DECIMAL(38,6) monthly_revenue,sum(gross_profit)::DECIMAL(38,12) monthly_gross_profit,CASE WHEN sum(invoice_total)>0 THEN round(sum(gross_profit)/sum(invoice_total)*100,2) ELSE 0 END monthly_gross_margin_pct,count(DISTINCT customer_id) monthly_customers FROM ip GROUP BY revenue_month_start)
```
event 49 / message

```text
      'stg_quickbooks__item':'item_id IS NOT NULL AND name IS NOT NULL AND track_quantity_on_hand IS NOT NULL',
```
event 49 / message

```text
s=s.replace("('stg_quickbooks__item'", "('stg_quickbooks__item'")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-015.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/staging/stg_quickbooks__item.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/sql/staging/stg_quickbooks__item.sql`
- S6: `records/006_contract_impl-015.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/workspace/result.md`
- S10: `records/012_packages/012_impl-015_staging_stg_quickbooks__item.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/quickbooks.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/quickbooks.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions`
