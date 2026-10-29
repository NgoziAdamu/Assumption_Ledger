# impl-027 | intermediate | int_xero__invoice_line_items_enriched | 差异：S1；日期 原记录

## 契约完整原文

S3:430–542

```yaml
    - name: int_xero__invoice_line_items_enriched
      description: Enriched Xero invoice line items with account, invoice/contact, and active tracking attributes; includes effective tax rate (percent, 2 decimals)
      grain: One row per line_item_id (rows with NULL line_item_id or NULL invoice_id are excluded)
      source_models:
      - staging.stg_xero__invoice_line_item
      - staging.stg_xero__invoice
      - staging.stg_xero__account
      - staging.stg_xero__contact
      - staging.stg_xero__invoice_line_item_has_tracking_category
      - staging.stg_xero__tracking_category
      - staging.stg_xero__tracking_category_option
      - staging.stg_xero__tracking_category_has_option
      business_logic: '- Start from staging.stg_xero__invoice_line_item selecting: line_item_id, invoice_id, account_code, description, quantity, unit_amount, line_amount, tax_amount, tax_type, discount_rate, processed_at. - Exclude rows where line_item_id or invoice_id is NULL. - Join invoice header by invoice_id to add contact_id (left join; if no match, contact_id is NULL). - Join contacts by contact_id to add contact_name (left join; if no match, contact_name is NULL). - Join accounts by account_code after converting the line item account_code to text to match the account table; add account_name, account_type, account_class (left join; if no match, these are NULL). The output account_code remains the original numeric value from the line item. - Build tracking attributes: - Take invoice_id, line_item_id, tracking_option, tracking_category_id from staging.stg_xero__invoice_line_item_has_tracking_category. - Construct the set of active category/option pairs by linking categories to options through their relationship and keeping only options marked active. - Keep only tracking pairs whose option name exactly matches an active option for that category. - For each (invoice_id, line_item_id), pivot to columns for Region, Department, Project, Location, Class, Customer, and any category whose name contains "Cost Center". If multiple active options exist for the same category on a line, choose the lexicographically greatest non-null option name; if none, leave NULL. - Compute effective_tax_rate as: tax_amount divided by (line_amount minus tax_amount), multiplied by 100, then rounded to 2 decimals. If the denominator is zero or any input is null, the result is null. - All numeric values (quantity, unit_amount, line_amount, tax_amount, discount_rate) and processed_at are passed through without rescaling; processed_at retains its timezone.'
      columns:
      - name: line_item_id
        data_type: VARCHAR
        description: Unique identifier for the invoice line item; exactly one output row per value
        tests:
        - not_null
        - unique
      - name: invoice_id
        data_type: VARCHAR
        description: Invoice identifier from the line item; rows with NULL are excluded
        tests:
        - not_null
      - name: account_code
        data_type: BIGINT
        description: Numeric account code from the line item; joined to accounts by converting to text; output remains numeric
        tests: []
      - name: account_name
        data_type: VARCHAR
        description: Account name from the accounts table via left join; NULL if no match
        tests: []
      - name: account_type
        data_type: VARCHAR
        description: Account type from the accounts table via left join; NULL if no match
        tests: []
      - name: account_class
        data_type: VARCHAR
        description: High-level account classification from the accounts table via left join; NULL if no match
        tests: []
      - name: description
        data_type: VARCHAR
        description: Line item description from staging
        tests: []
      - name: quantity
        data_type: DOUBLE
        description: Quantity from the line item; pass-through with no rounding or rescaling
        tests: []
      - name: unit_amount
        data_type: DOUBLE
        description: Unit amount from the line item; pass-through with no rescaling
        tests: []
      - name: line_amount
        data_type: DOUBLE
        description: Extended line amount from the line item; used with tax_amount to compute effective_tax_rate
        tests: []
      - name: tax_amount
        data_type: DOUBLE
        description: Tax amount for the line item; pass-through
        tests: []
      - name: effective_tax_rate
        data_type: DOUBLE
        description: Tax amount divided by (line amount minus tax amount) times 100, rounded to 2 decimals; NULL if denominator is zero or inputs are NULL
        tests: []
      - name: tax_type
        data_type: VARCHAR
        description: Tax type code from the line item; pass-through
        tests: []
      - name: discount_rate
        data_type: DOUBLE
        description: Discount rate from the line item; pass-through without normalization
        tests: []
      - name: contact_id
        data_type: VARCHAR
        description: Contact identifier from the invoice header via left join; NULL if not found
        tests: []
      - name: contact_name
        data_type: VARCHAR
        description: Contact name from the contacts table via left join on contact_id; NULL if no match
        tests: []
      - name: region
        data_type: VARCHAR
        description: Tracking option for category 'Region' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none
        tests: []
      - name: department
        data_type: VARCHAR
        description: Tracking option for category 'Department' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none
        tests: []
      - name: project
        data_type: VARCHAR
        description: Tracking option for category 'Project' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none
        tests: []
      - name: location
        data_type: VARCHAR
        description: Tracking option for category 'Location' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none
        tests: []
      - name: class
        data_type: VARCHAR
        description: Tracking option for category 'Class' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none
        tests: []
      - name: customer
        data_type: VARCHAR
        description: Tracking option for category 'Customer' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none
        tests: []
      - name: cost_center
        data_type: VARCHAR
        description: Tracking option for any category whose name contains 'Cost Center' (active only); if multiple, the lexicographically greatest option is chosen; NULL if none
        tests: []
      - name: processed_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Processing timestamp from line item staging; passed through with timezone preserved
        tests: []
```

## agent 最终 SQL

S4

```sql
WITH tracking AS (
    SELECT *
    FROM intermediate.int_xero__invoice_line_item_pivoted_tracking_categories
),
account_by_code AS (
    SELECT account_code, account_name, account_type, account_class
    FROM staging.stg_xero__account
    QUALIFY row_number() OVER (PARTITION BY account_code ORDER BY account_id) = 1
),
line_items AS (
    SELECT
        line_item_id,
        invoice_id,
        account_code,
        description,
        quantity,
        unit_amount,
        line_amount,
        tax_amount,
        tax_type,
        discount_rate,
        processed_at
    FROM staging.stg_xero__invoice_line_item
    WHERE line_item_id IS NOT NULL
      AND invoice_id IS NOT NULL
),
enriched AS (
    SELECT
        line.line_item_id,
        line.invoice_id,
        TRY_CAST(line.account_code AS BIGINT) AS account_code,
        account.account_name,
        account.account_type,
        account.account_class,
        line.description,
        line.quantity::DOUBLE AS quantity,
        line.unit_amount::DOUBLE AS unit_amount,
        line.line_amount::DOUBLE AS line_amount,
        line.tax_amount::DOUBLE AS tax_amount,
        CASE
            WHEN line.tax_amount IS NULL OR line.line_amount IS NULL
              OR line.line_amount - line.tax_amount = 0 THEN NULL
            ELSE round(line.tax_amount / (line.line_amount - line.tax_amount) * 100, 2)::DOUBLE
        END AS effective_tax_rate,
        line.tax_type,
        line.discount_rate::DOUBLE AS discount_rate,
        invoice.contact_id,
        contact.contact_name,
        tracking.region,
        tracking.department,
        tracking.project,
        tracking.location,
        tracking.class,
        tracking.customer,
        tracking.cost_center,
        line.processed_at::TIMESTAMPTZ AS processed_at
    FROM line_items AS line
    LEFT JOIN staging.stg_xero__invoice AS invoice
        ON line.invoice_id = invoice.invoice_id
    LEFT JOIN staging.stg_xero__contact AS contact
        ON invoice.contact_id = contact.contact_id
    LEFT JOIN account_by_code AS account
        ON line.account_code::VARCHAR = account.account_code
    LEFT JOIN tracking
        ON line.invoice_id = tracking.invoice_id
       AND line.line_item_id = tracking.line_item_id
)
SELECT * FROM enriched
```

## gold SQL（仅供定位差异）

S5

```sql
-- Intermediate fact: Invoice Line Items Enriched (staging -> intermediate only)

WITH invoice_line_items AS (
    SELECT
        line_item_id,
        invoice_id,
        account_code,
        description,
        quantity,
        unit_amount,
        line_amount,
        tax_amount,
        tax_type,
        discount_rate,
        processed_at
    FROM staging.stg_xero__invoice_line_item
),

invoices AS (
    SELECT
        invoice_id,
        contact_id
    FROM staging.stg_xero__invoice
),

accounts AS (
    SELECT
        account_code,
        account_name,
        account_type,
        account_class
    FROM staging.stg_xero__account
),

contacts AS (
    SELECT
        contact_id,
        contact_name
    FROM staging.stg_xero__contact
),

pivoted_invoice_tracking AS (
    -- Build pivot locally from staging to avoid same-layer dependency
    WITH invoice_tracking AS (
        SELECT invoice_id, line_item_id, tracking_option, tracking_category_id
        FROM staging.stg_xero__invoice_line_item_has_tracking_category
    ),
    tracking_categories_with_options AS (
        WITH tracking_categories AS (
            SELECT tracking_category_id, tracking_category_name FROM staging.stg_xero__tracking_category
        ),
        tracking_options AS (
            SELECT tracking_option_id, tracking_option_name, is_active FROM staging.stg_xero__tracking_category_option
        ),
        tracking_relationships AS (
            SELECT tracking_category_id, tracking_option_id FROM staging.stg_xero__tracking_category_has_option
        )
        SELECT tc.tracking_category_id, tc.tracking_category_name, topt.tracking_option_name
        FROM tracking_categories tc
        JOIN tracking_relationships tr ON tc.tracking_category_id = tr.tracking_category_id
        JOIN tracking_options topt ON tr.tracking_option_id = topt.tracking_option_id
        WHERE topt.is_active = TRUE
    ),
    invoice_mapped AS (
        SELECT it.invoice_id, it.line_item_id, tcwo.tracking_category_name, tcwo.tracking_option_name
        FROM invoice_tracking it
        JOIN tracking_categories_with_options tcwo
          ON it.tracking_category_id = tcwo.tracking_category_id
         AND it.tracking_option = tcwo.tracking_option_name
    )
    SELECT
        invoice_id,
        line_item_id,
        MAX(CASE WHEN tracking_category_name = 'Region' THEN tracking_option_name END) AS region,
        MAX(CASE WHEN tracking_category_name = 'Department' THEN tracking_option_name END) AS department,
        MAX(CASE WHEN tracking_category_name = 'Project' THEN tracking_option_name END) AS project,
        MAX(CASE WHEN tracking_category_name = 'Location' THEN tracking_option_name END) AS location,
        MAX(CASE WHEN tracking_category_name = 'Class' THEN tracking_option_name END) AS class,
        MAX(CASE WHEN tracking_category_name = 'Customer' THEN tracking_option_name END) AS customer,
        MAX(CASE WHEN tracking_category_name LIKE '%Cost Center%' THEN tracking_option_name END) AS cost_center
    FROM invoice_mapped
    GROUP BY invoice_id, line_item_id
)

SELECT
    -- Line item identity
    ili.line_item_id,
    ili.invoice_id,

    -- Line item details
    ili.account_code,
    acc.account_name,
    acc.account_type,
    acc.account_class,
    ili.description,
    ili.quantity,
    ili.unit_amount,
    ili.line_amount,
    ili.tax_amount,
    ROUND(ili.tax_amount / NULLIF(ili.line_amount - ili.tax_amount, 0) * 100, 2) AS effective_tax_rate,
    ili.tax_type,
    ili.discount_rate,

    -- Basic invoice and contact info
    inv.contact_id,
    con.contact_name,

    -- Tracking dimensions (pivoted from categories)
    pit.region,
    pit.department,
    pit.project,
    pit.location,
    pit.class,
    pit.customer,
    pit.cost_center,

    -- Processing metadata
    ili.processed_at
FROM invoice_line_items ili
LEFT JOIN invoices inv
    ON ili.invoice_id = inv.invoice_id
LEFT JOIN accounts acc
    ON CAST(ili.account_code AS VARCHAR) = acc.account_code
LEFT JOIN contacts con
    ON inv.contact_id = con.contact_id
LEFT JOIN pivoted_invoice_tracking pit
    ON ili.invoice_id = pit.invoice_id
    AND ili.line_item_id = pit.line_item_id
WHERE ili.line_item_id IS NOT NULL
  AND ili.invoice_id IS NOT NULL
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5000 | 5209 | 0 | 0 | 0 | 209 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"line_item_id":"0050f62f-3244-4d1e-aaa4-fa8e8cad6555"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| line_item_id | 0 | 0 | 209 | VARCHAR | VARCHAR |
| invoice_id | 0 | 0 | 209 | VARCHAR | VARCHAR |
| account_code | 0 | 0 | 209 | BIGINT | BIGINT |
| account_name | 0 | 0 | 209 | VARCHAR | VARCHAR |
| account_type | 0 | 0 | 209 | VARCHAR | VARCHAR |
| account_class | 0 | 0 | 209 | VARCHAR | VARCHAR |
| description | 0 | 0 | 209 | VARCHAR | VARCHAR |
| quantity | 0 | 0 | 209 | DOUBLE | DOUBLE |
| unit_amount | 0 | 0 | 209 | DOUBLE | DOUBLE |
| line_amount | 0 | 0 | 209 | DOUBLE | DOUBLE |
| tax_amount | 0 | 0 | 209 | DOUBLE | DOUBLE |
| effective_tax_rate | 0 | 0 | 209 | DOUBLE | DOUBLE |
| tax_type | 0 | 0 | 209 | VARCHAR | VARCHAR |
| discount_rate | 0 | 0 | 209 | DOUBLE | DOUBLE |
| contact_id | 0 | 0 | 209 | VARCHAR | VARCHAR |
| contact_name | 0 | 0 | 209 | VARCHAR | VARCHAR |
| region | 0 | 0 | 209 | VARCHAR | VARCHAR |
| department | 0 | 0 | 209 | VARCHAR | VARCHAR |
| project | 0 | 0 | 209 | VARCHAR | VARCHAR |
| location | 0 | 0 | 209 | VARCHAR | VARCHAR |
| class | 0 | 0 | 209 | VARCHAR | VARCHAR |
| customer | 0 | 0 | 209 | VARCHAR | VARCHAR |
| cost_center | 0 | 0 | 209 | VARCHAR | VARCHAR |

line_item_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0050f62f-3244-4d1e-aaa4-fa8e8cad6555","rows":1}]</code> | <code>[{"value":"0050f62f-3244-4d1e-aaa4-fa8e8cad6555","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

invoice_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"68252a67-64c4-44a4-af75-0bfa4eb73e55","rows":1}]</code> | <code>[{"value":"68252a67-64c4-44a4-af75-0bfa4eb73e55","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

account_code 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"820","rows":1}]</code> | <code>[{"value":"820","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

account_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Sales Tax","rows":1}]</code> | <code>[{"value":"Rent","rows":1},{"value":"Sales Tax","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

account_type 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"CURRLIAB","rows":1}]</code> | <code>[{"value":"CURRLIAB","rows":1},{"value":"TERMLIAB","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

account_class 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"LIABILITY","rows":1}]</code> | <code>[{"value":"EXPENSE","rows":1},{"value":"LIABILITY","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

description 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"RGF0YSBBbmFseXNpcw==","rows":1}]</code> | <code>[{"value":"RGF0YSBBbmFseXNpcw==","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

quantity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"44.5397","rows":1}]</code> | <code>[{"value":"44.5397","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

unit_amount 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"277.52","rows":1}]</code> | <code>[{"value":"277.52","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

line_amount 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"12360.66","rows":1}]</code> | <code>[{"value":"12360.66","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

tax_amount 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"1854.1","rows":1}]</code> | <code>[{"value":"1854.1","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

effective_tax_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"17.65","rows":1}]</code> | <code>[{"value":"17.65","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

tax_type 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"NONE","rows":1}]</code> | <code>[{"value":"NONE","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

discount_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"5.86","rows":1}]</code> | <code>[{"value":"5.86","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"aea2f772-eff4-4b70-99c1-f8dfe35e072d","rows":1}]</code> | <code>[{"value":"aea2f772-eff4-4b70-99c1-f8dfe35e072d","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

region 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

department 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

project 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

location 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

class 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

customer 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

cost_center 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
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
| A2_all_null_column | <code>2列；[{"column":"class","table_rows":5000}]</code> |
| B7_specified_not_read | <code>["staging.stg_xero__invoice_line_item_has_tracking_category"]</code> |
| B7_read_not_specified | <code>["intermediate.int_xero__invoice_line_item_pivoted_tracking_categories"]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory  'invoice_item_enriched_pk':"select count(*) total, count(distinct line_item_id) distinct_ids, count(*) filter(where line_item_id is null or invoice_id is null) bad_ids from intermediate.int_xero__invoice_line_items_enriched",</code> |

## 轨迹索引（不放输出原文）

本题事件总数：43；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 4 -print -exec wc -l {} \; &amp;&amp; cat config/layer_dependencies.yaml</code> | 1748 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9771 | false | false |
| 19 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>stages={<br>'stg_xero__account':('xero_account_data', '''    account_id::VARCHAR AS account_id,<br>    na</code> | 0 | false | false |
| 21 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br><br>def write(layer,name,sql): Path(f'sql/{layer}/{name}.sql').write_text(sql.strip()+'\n')<br>write('intermediate','int_xero__tracking_categories_with_o</code> | 0 | false | false |
| 23 | run | <code>cat &gt;&gt; /tmp/models.py &lt;&lt;'PY'<br><br>write('marts','xero__invoice_line_items', '''<br>WITH source_lines AS (<br>    SELECT *<br>    FROM intermediate.int_xero__invoice_line_items_enriched<br>    WHERE line_item_id IS NO</code> | 3 | false | false |
| 25 | run | <code>python run.py &gt; /tmp/run.log 2&gt;&amp;1; status=$?; tail -100 /tmp/run.log; exit $status</code> | 7453 | true | false |
| 27 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('xero.duckdb',read_only=True)<br>for q in ["select count(*),count(distinct line_item_id) from intermediate.int_xero__invoice_line_items_enriched", "select l</code> | 1073 | true | false |
| 29 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_xero__invoice_line_items_enriched.sql'<br>s=open(p).read()<br>s=s.replace('WITH tracking AS (\n    SELECT *\n    FROM intermediate.int_xero__invoice_line_item_pivoted</code> | 470 | true | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('xero.duckdb',read_only=True)<br>checks={<br> 'invoice_item_enriched_pk':"select count(*) total, count(distinct line_item_id) distinct_ids, count(*) filter(whe</code> | 214 | false | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
write('intermediate','int_xero__invoice_line_items_enriched', '''
```
event 23 / message

```text
    FROM intermediate.int_xero__invoice_line_items_enriched
```
event 27 / message

```text
for q in ["select count(*),count(distinct line_item_id) from intermediate.int_xero__invoice_line_items_enriched", "select line_item_id,count(*) n from intermediate.int_xero__invoice_line_items_enriched group by 1 having count(*)>1 order by n desc limit 10", "select account_code,count(*) n from staging.stg_xero__account group by 1 having count(*)>1 order by n desc limit 15", "select count(*) from staging.stg_xero__invoice_line_item"]:
```
event 29 / message

```text
p='sql/intermediate/int_xero__invoice_line_items_enriched.sql'
```
event 29 / message

```text
python run.py > /tmp/run2.log 2>&1; status=$?; grep -E 'ERROR|✗|layer complete|int_xero__invoice_line_items_enriched:|MARTS layer' /tmp/run2.log; exit $status
```
event 31 / message

```text
 'invoice_item_enriched_pk':"select count(*) total, count(distinct line_item_id) distinct_ids, count(*) filter(where line_item_id is null or invoice_id is null) bad_ids from intermediate.int_xero__invoice_line_items_enriched",
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-027.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql`
- S6: `records/006_contract_impl-027.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/result.md`
- S10: `records/012_packages/012_impl-027_intermediate_int_xero__invoice_line_items_enriched.json`
- S11: `data/005_cs_work/impl-027_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions`
