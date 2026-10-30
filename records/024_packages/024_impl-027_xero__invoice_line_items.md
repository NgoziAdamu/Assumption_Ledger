# impl-027 | marts | xero__invoice_line_items | 差异：S1；日期 原记录

## 契约完整原文

S3:725–840

```yaml
    - name: xero__invoice_line_items
      description: Invoice line items enriched with invoice-level non-negative metrics, shares, sequencing, and run timestamp
      grain: One row per input line with non-null invoice_id and line_item_id; duplicates preserved
      source_models:
      - intermediate.int_xero__invoice_line_items_enriched
      business_logic: '- Source rows from intermediate.int_xero__invoice_line_items_enriched where both line_item_id and invoice_id are present. - Pass through descriptive, account, contact, tracking fields, and processed_at unchanged. - Standardize amounts and quantity: - line_amount_nonneg: if line_amount is null then null; if negative then 0; otherwise keep line_amount. - tax_amount_nonneg: if tax_amount is null then null; if negative then 0; otherwise keep tax_amount. - line_net_of_tax: line_amount minus tax_amount (treat missing tax_amount as 0); if result is negative then 0; if line_amount is null then null. - quantity: set to null when source quantity is null or negative; otherwise keep the source value. - Per invoice_id, compute: - invoice_gross_nonneg: sum of line_amount_nonneg (nulls ignored; null if all inputs are null). - invoice_net_nonneg: sum of line_net_of_tax (nulls ignored; null if all inputs are null). - invoice_line_count: number of lines after the ID filters (includes lines with null amounts). - Attach invoice-level totals back to each line. - Per-line shares (only when denominators are positive): - line_share_gross: line_amount_nonneg divided by invoice_gross_nonneg; otherwise null. - line_share_net: line_net_of_tax divided by invoice_net_nonneg; otherwise null. - Within each invoice_id, order lines by line_item_id ascending to compute: - invoice_cum_gross_nonneg: cumulative sum of line_amount_nonneg from the first ordered line through the current line. - line_seq_in_invoice: 1-based sequence in that order. If multiple lines share the same line_item_id within an invoice, their relative order is unspecified. - Classify line_item_type by line_amount: positive → Revenue; negative → Expense/Refund; zero or null → Neutral. - Set report_generated_at to the current timestamp at model execution. - Final result: one row per input line that passed the ID filters, ordered by invoice_id and line_seq_in_invoice ascending.'
      columns:
      - name: line_item_id
        data_type: VARCHAR
        description: Invoice line item identifier from source; NULLs are filtered out upstream
        tests:
        - not_null
      - name: invoice_id
        data_type: VARCHAR
        description: Invoice identifier from source; NULLs are filtered out upstream
        tests:
        - not_null
      - name: account_code
        data_type: BIGINT
        description: Account code of the line item (numeric code from source)
      - name: account_name
        data_type: VARCHAR
        description: Account name associated with the line item
      - name: account_type
        data_type: VARCHAR
        description: Account type classification from source
      - name: account_class
        data_type: VARCHAR
        description: Account class/category from source
      - name: description
        data_type: VARCHAR
        description: Free-text line description from source
      - name: quantity
        data_type: DOUBLE
        description: 'Quantity with guard: null if source quantity is null or negative; otherwise pass-through'
      - name: unit_amount
        data_type: DOUBLE
        description: Unit price from source (pass-through; no rounding)
      - name: line_amount
        data_type: DOUBLE
        description: Line amount from source (pass-through; may be negative or null)
      - name: tax_amount
        data_type: DOUBLE
        description: Tax amount from source (pass-through; may be negative or null)
      - name: tax_type
        data_type: VARCHAR
        description: Tax type/code from source
      - name: discount_rate
        data_type: DOUBLE
        description: Discount rate from source (pass-through; no transformation)
      - name: contact_id
        data_type: VARCHAR
        description: Contact identifier associated with the invoice line
      - name: contact_name
        data_type: VARCHAR
        description: Contact name associated with the invoice line
      - name: region
        data_type: VARCHAR
        description: Region tracking dimension from source
      - name: department
        data_type: VARCHAR
        description: Department tracking dimension from source
      - name: project
        data_type: VARCHAR
        description: Project tracking dimension from source
      - name: location
        data_type: VARCHAR
        description: Location tracking dimension from source
      - name: class
        data_type: VARCHAR
        description: Class tracking dimension from source
      - name: customer
        data_type: VARCHAR
        description: Customer tracking dimension from source
      - name: cost_center
        data_type: VARCHAR
        description: Cost center tracking dimension from source
      - name: line_amount_nonneg
        data_type: DOUBLE
        description: If line_amount is null then null; if negative then 0; otherwise equal to line_amount
      - name: tax_amount_nonneg
        data_type: DOUBLE
        description: If tax_amount is null then null; if negative then 0; otherwise equal to tax_amount
      - name: line_net_of_tax
        data_type: DOUBLE
        description: Line amount minus tax (missing tax treated as 0), floored at 0; null if line_amount is null
      - name: invoice_gross_nonneg
        data_type: DOUBLE
        description: Sum of non-negative line amounts per invoice; ignores nulls; null if all inputs are null
      - name: invoice_net_nonneg
        data_type: DOUBLE
        description: Sum of non-negative net-of-tax amounts per invoice; ignores nulls; null if all inputs are null
      - name: invoice_line_count
        data_type: BIGINT
        description: Number of lines per invoice after filtering out null line_item_id and invoice_id
      - name: line_share_gross
        data_type: DOUBLE
        description: Per-line proportion of invoice gross; computed only when invoice gross is > 0; otherwise null
      - name: line_share_net
        data_type: DOUBLE
        description: Per-line proportion of invoice net; computed only when invoice net is > 0; otherwise null
      - name: invoice_cum_gross_nonneg
        data_type: DOUBLE
        description: Cumulative sum of non-negative line amounts within invoice ordered by line_item_id; includes current row; tie order for duplicate line_item_id is unspecified
      - name: line_seq_in_invoice
        data_type: BIGINT
        description: 1-based position within invoice ordered by line_item_id; tie order for duplicate line_item_id is unspecified
      - name: line_item_type
        data_type: VARCHAR
        description: 'Classification by line_amount sign: positive Revenue; negative Expense/Refund; otherwise Neutral (includes null and zero)'
      - name: processed_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: ETL processing timestamp from the source intermediate model
      - name: report_generated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Query run timestamp set at model execution time
```

## agent 最终 SQL

S4

```sql
WITH source_lines AS (
    SELECT *
    FROM intermediate.int_xero__invoice_line_items_enriched
    WHERE line_item_id IS NOT NULL
      AND invoice_id IS NOT NULL
),
standardized AS (
    SELECT
        line_item_id,
        invoice_id,
        account_code,
        account_name,
        account_type,
        account_class,
        description,
        CASE WHEN quantity IS NULL OR quantity < 0 THEN NULL ELSE quantity END AS quantity,
        unit_amount,
        line_amount,
        tax_amount,
        tax_type,
        discount_rate,
        contact_id,
        contact_name,
        region,
        department,
        project,
        location,
        class,
        customer,
        cost_center,
        CASE WHEN line_amount IS NULL THEN NULL ELSE greatest(line_amount, 0) END AS line_amount_nonneg,
        CASE WHEN tax_amount IS NULL THEN NULL ELSE greatest(tax_amount, 0) END AS tax_amount_nonneg,
        CASE
            WHEN line_amount IS NULL THEN NULL
            ELSE greatest(line_amount - coalesce(tax_amount, 0), 0)
        END AS line_net_of_tax,
        processed_at
    FROM source_lines
),
invoice_totals AS (
    SELECT
        *,
        sum(line_amount_nonneg) OVER (PARTITION BY invoice_id) AS invoice_gross_nonneg,
        sum(line_net_of_tax) OVER (PARTITION BY invoice_id) AS invoice_net_nonneg,
        count(*) OVER (PARTITION BY invoice_id) AS invoice_line_count,
        sum(line_amount_nonneg) OVER (
            PARTITION BY invoice_id
            ORDER BY line_item_id ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS invoice_cum_gross_nonneg,
        row_number() OVER (PARTITION BY invoice_id ORDER BY line_item_id ASC) AS line_seq_in_invoice
    FROM standardized
)
SELECT
    line_item_id,
    invoice_id,
    account_code,
    account_name,
    account_type,
    account_class,
    description,
    quantity,
    unit_amount,
    line_amount,
    tax_amount,
    tax_type,
    discount_rate,
    contact_id,
    contact_name,
    region,
    department,
    project,
    location,
    class,
    customer,
    cost_center,
    line_amount_nonneg,
    tax_amount_nonneg,
    line_net_of_tax,
    invoice_gross_nonneg,
    invoice_net_nonneg,
    invoice_line_count,
    CASE WHEN invoice_gross_nonneg > 0 THEN line_amount_nonneg / invoice_gross_nonneg END AS line_share_gross,
    CASE WHEN invoice_net_nonneg > 0 THEN line_net_of_tax / invoice_net_nonneg END AS line_share_net,
    invoice_cum_gross_nonneg,
    line_seq_in_invoice,
    CASE
        WHEN line_amount > 0 THEN 'Revenue'
        WHEN line_amount < 0 THEN 'Expense/Refund'
        ELSE 'Neutral'
    END AS line_item_type,
    processed_at,
    current_timestamp AS report_generated_at
FROM invoice_totals
ORDER BY invoice_id, line_seq_in_invoice
```

## gold SQL（仅供定位差异）

S5

```sql
-- Mart table: Invoice Line Items - enriched with invoice-level metrics and defensible constraints
-- Layer contract: ONLY reference intermediate layer

WITH base AS (
    SELECT
        ili.line_item_id,
        ili.invoice_id,
        ili.account_code,
        ili.account_name,
        ili.account_type,
        ili.account_class,
        ili.description,
        ili.quantity,
        ili.unit_amount,
        ili.line_amount,
        ili.tax_amount,
        ili.tax_type,
        ili.discount_rate,
        ili.contact_id,
        ili.contact_name,
        ili.region,
        ili.department,
        ili.project,
        ili.location,
        ili.class,
        ili.customer,
        ili.cost_center,
        ili.processed_at
    FROM intermediate.int_xero__invoice_line_items_enriched ili
    WHERE ili.line_item_id IS NOT NULL
      AND ili.invoice_id IS NOT NULL
),

validated AS (
    SELECT
        b.*,
        -- Enforce non-negative amounts for metric denominators; keep raw for audit
        GREATEST(b.line_amount, 0) AS line_amount_nonneg,
        GREATEST(b.tax_amount, 0)  AS tax_amount_nonneg,
        -- Net of tax (non-negative)
        GREATEST(b.line_amount - COALESCE(b.tax_amount, 0), 0) AS line_net_of_tax,
        -- Guard quantity
        CASE WHEN b.quantity IS NULL OR b.quantity < 0 THEN NULL ELSE b.quantity END AS quantity_valid
    FROM base b
),

invoice_sums AS (
    SELECT
        invoice_id,
        SUM(line_amount_nonneg) AS invoice_gross_nonneg,
        SUM(line_net_of_tax)    AS invoice_net_nonneg,
        COUNT(*)                AS invoice_line_count
    FROM validated
    GROUP BY invoice_id
),

scored AS (
    SELECT
        v.*,
        s.invoice_gross_nonneg,
        s.invoice_net_nonneg,
        s.invoice_line_count,
        -- Line share of invoice totals (defensive denominators)
        CASE WHEN s.invoice_gross_nonneg > 0 THEN v.line_amount_nonneg / s.invoice_gross_nonneg END AS line_share_gross,
        CASE WHEN s.invoice_net_nonneg   > 0 THEN v.line_net_of_tax   / s.invoice_net_nonneg   END AS line_share_net,
        -- Window metrics per invoice
        SUM(v.line_amount_nonneg) OVER (PARTITION BY v.invoice_id ORDER BY v.line_item_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS invoice_cum_gross_nonneg,
        ROW_NUMBER() OVER (PARTITION BY v.invoice_id ORDER BY v.line_item_id) AS line_seq_in_invoice,
        -- Classification
        CASE
            WHEN v.line_amount > 0 THEN 'Revenue'
            WHEN v.line_amount < 0 THEN 'Expense/Refund'
            ELSE 'Neutral'
        END AS line_item_type
    FROM validated v
    JOIN invoice_sums s USING (invoice_id)
)

SELECT
    -- Identity
    line_item_id,
    invoice_id,

    -- Details
    account_code,
    account_name,
    account_type,
    account_class,
    description,
    quantity_valid AS quantity,
    unit_amount,
    line_amount,
    tax_amount,
    tax_type,
    discount_rate,

    -- Contact
    contact_id,
    contact_name,

    -- Tracking dims
    region,
    department,
    project,
    location,
    class,
    customer,
    cost_center,

    -- Metrics
    line_amount_nonneg,
    tax_amount_nonneg,
    line_net_of_tax,
    invoice_gross_nonneg,
    invoice_net_nonneg,
    invoice_line_count,
    line_share_gross,
    line_share_net,
    invoice_cum_gross_nonneg,
    line_seq_in_invoice,
    line_item_type,

    -- Processing metadata
    processed_at,
    CURRENT_TIMESTAMP AS report_generated_at

FROM scored

ORDER BY invoice_id, line_seq_in_invoice
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5209 | 5209 | 0 | 0 | 209 | 209 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"line_item_id":"002b1260-f2c9-4b35-b293-359447a86793","invoice_id":"660e3497-99d1-4af2-be7c-c2c0c29281fa","account_code":"628","contact_id":"20f6e8ee-ce44-433e-ab23-020ecc0ddf21","region":"null"}</code> |
| K2 | <code>{"line_item_id":"00a677a0-b2d9-4386-8759-397ec2f547c7","invoice_id":"b56bd5d9-8a2b-4fef-81ae-4b5a20bcf20e","account_code":"162","contact_id":"00acba72-b8c7-4d1c-94ea-998683864d58","region":"null"}</code> |
| K3 | <code>{"line_item_id":"0248cd77-ab35-4585-96e0-f565776788c2","invoice_id":"c8d67b95-84ad-4b82-a185-a728a1c881b4","account_code":"553","contact_id":"5c8625c6-42ed-49f3-8bff-60dc0cf0c29b","region":"null"}</code> |
| K4 | <code>{"line_item_id":"007e2652-9012-4f67-8c96-2e0220e71f40","invoice_id":"63f68993-747d-4609-9ac3-c52fc32078d3","account_code":"200","contact_id":"b958faad-9781-4ca5-a654-7bb3e22be5a5","region":"null"}</code> |
| K5 | <code>{"line_item_id":"01e1331d-879c-4e36-bb43-a099a2be098b","invoice_id":"020b7b7a-3bae-47e2-bc79-80db16c5fb79","account_code":"441","contact_id":"a38fa4bf-4b06-4560-96a8-177d0cdb8260","region":"null"}</code> |
| K6 | <code>{"line_item_id":"02a98856-0075-4ae2-85ae-58bbeb802844","invoice_id":"7acef931-9a38-48dc-b418-95754d937c44","account_code":"422","contact_id":"156d7a9c-7800-41e1-b7a9-583036ee5f50","region":"null"}</code> |
| K7 | <code>{"line_item_id":"03817b39-d05a-4640-9909-1b3a4dcb15a6","invoice_id":"9926465e-a764-4394-a057-c1e5c446d918","account_code":"239","contact_id":"13d352d4-ad46-47b0-9066-4d30f9b2eacf","region":"null"}</code> |
| K8 | <code>{"line_item_id":"048cddd5-6ea7-4abe-9b20-8633be07ad01","invoice_id":"231d189f-54a6-4b22-9986-73f7be952d1e","account_code":"309","contact_id":"35deefc0-6169-4709-830c-12155592f0bf","region":"null"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| line_item_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| invoice_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_code | 0 | 0 | 0 | BIGINT | BIGINT |
| account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_class | 0 | 0 | 0 | VARCHAR | VARCHAR |
| description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| quantity | 0 | 0 | 0 | DOUBLE | DOUBLE |
| unit_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| line_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| tax_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| tax_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| discount_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| contact_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| department | 0 | 0 | 0 | VARCHAR | VARCHAR |
| class | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer | 0 | 0 | 0 | VARCHAR | VARCHAR |
| cost_center | 0 | 0 | 0 | VARCHAR | VARCHAR |
| line_amount_nonneg | 0 | 0 | 0 | DOUBLE | DOUBLE |
| tax_amount_nonneg | 0 | 0 | 0 | DOUBLE | DOUBLE |
| line_net_of_tax | 0 | 0 | 0 | DOUBLE | DOUBLE |
| invoice_gross_nonneg | 520 | 520 | 520 | DOUBLE | DOUBLE |
| invoice_net_nonneg | 522 | 522 | 522 | DOUBLE | DOUBLE |
| invoice_line_count | 0 | 0 | 0 | BIGINT | BIGINT |
| line_share_gross | 457 | 457 | 457 | DOUBLE | DOUBLE |
| line_share_net | 476 | 476 | 476 | DOUBLE | DOUBLE |
| invoice_cum_gross_nonneg | 0 | 0 | 0 | DOUBLE | DOUBLE |
| line_seq_in_invoice | 0 | 0 | 0 | BIGINT | BIGINT |
| line_item_type | 0 | 0 | 0 | VARCHAR | VARCHAR |

invoice_gross_nonneg 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 31447.94 | 31447.939999999995 |
| K2 | 29476.25 | 29476.250000000004 |
| K3 | 11222.51 | 11222.509999999998 |

invoice_net_nonneg 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 28454.960000000003 | 28454.96 |
| K4 | <code>[{"value":"26240.140000000003","rows":2}]</code> | <code>[{"value":"26240.14","rows":2}]</code> |
| K5 | 41609.46 | 41609.45999999999 |
重复键为同键值/次数，列表位置不是唯一配对。

line_share_gross 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.04824640342101899 | 0.048246403421019 |
| K6 | 0.656352157807707 | 0.6563521578077067 |
| K7 | 0.1464513674796786 | 0.14645136747967857 |

line_share_net 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.046922575185486114 | 0.04692257518548612 |
| K4 | <code>[{"value":"0.22865731661492658","rows":2}]</code> | <code>[{"value":"0.2286573166149266","rows":2}]</code> |
| K8 | 0.41134742682278524 | 0.4113474268227852 |
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
| A2_all_null_column | <code>2列；[{"column":"class","table_rows":5000},{"column":"customer","table_rows":5000}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"report_generated_at","value":"2026-10-25 05:52:30.431276+08"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["tax_amount","tax_amount_nonneg"],"nonnull_equal_rows":5000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["tax_amount","tax_amount_nonneg"],"nonnull_equal_rows":5000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| C9_agent_runtime_text | <code>S4:93 current_timestamp；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:125 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:730 current timestamp；命中数=1</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory  'mart_invoice_pk':"select count(*) total, count(distinct line_item_id) distinct_ids, count(*) filter(where line_item_id is null or invoice_id is null) bad_ids from marts.xero__invoice_line_items",</code> |

## 轨迹索引（不放输出原文）

本题事件总数：43；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 4 -print -exec wc -l {} \; &amp;&amp; cat config/layer_dependencies.yaml</code> | 1748 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9771 | true | false |
| 21 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br><br>def write(layer,name,sql): Path(f'sql/{layer}/{name}.sql').write_text(sql.strip()+'\n')<br>write('intermediate','int_xero__tracking_categories_with_o</code> | 0 | false | false |
| 23 | run | <code>cat &gt;&gt; /tmp/models.py &lt;&lt;'PY'<br><br>write('marts','xero__invoice_line_items', '''<br>WITH source_lines AS (<br>    SELECT *<br>    FROM intermediate.int_xero__invoice_line_items_enriched<br>    WHERE line_item_id IS NO</code> | 3 | false | false |
| 25 | run | <code>python run.py &gt; /tmp/run.log 2&gt;&amp;1; status=$?; tail -100 /tmp/run.log; exit $status</code> | 7453 | true | false |
| 27 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('xero.duckdb',read_only=True)<br>for q in ["select count(*),count(distinct line_item_id) from intermediate.int_xero__invoice_line_items_enriched", "select l</code> | 1073 | false | false |
| 29 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_xero__invoice_line_items_enriched.sql'<br>s=open(p).read()<br>s=s.replace('WITH tracking AS (\n    SELECT *\n    FROM intermediate.int_xero__invoice_line_item_pivoted</code> | 470 | false | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('xero.duckdb',read_only=True)<br>checks={<br> 'invoice_item_enriched_pk':"select count(*) total, count(distinct line_item_id) distinct_ids, count(*) filter(whe</code> | 214 | false | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
write('marts','xero__invoice_line_items', '''
```
event 31 / message

```text
 'mart_invoice_pk':"select count(*) total, count(distinct line_item_id) distinct_ids, count(*) filter(where line_item_id is null or invoice_id is null) bad_ids from marts.xero__invoice_line_items",
```
event 31 / message

```text
 'totals':"select count(*) filter(where invoice_gross_nonneg < 0 or invoice_net_nonneg < 0 or line_share_gross > 1.000001) invalid from marts.xero__invoice_line_items"
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-027.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/marts/xero__invoice_line_items.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/marts/xero__invoice_line_items.sql`
- S6: `records/006_contract_impl-027.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/result.md`
- S10: `data/024_packages_work/024_impl-027_xero__invoice_line_items/024_impl-027_xero__invoice_line_items.json`
- S11: `data/005_cs_work/impl-027_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions`
