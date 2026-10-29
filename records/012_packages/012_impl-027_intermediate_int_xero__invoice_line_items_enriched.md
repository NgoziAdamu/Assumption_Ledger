# impl-027 / int_xero__invoice_line_items_enriched

## basic_information

```json
{
  "task": "impl-027",
  "layer": "intermediate",
  "table": "int_xero__invoice_line_items_enriched",
  "status": "待标注",
  "difference_source": {
    "kind": "original_007_009",
    "record": "records/007_tolerance_tables.jsonl",
    "detail_record": "/home/katherine/Assumption_Ledger/records/005_cs_impl-027.json",
    "candidate_date": null,
    "selection_reason": "未进入 011，沿用原差异"
  },
  "status_record": "records/012_statuses.jsonl",
  "package_scope": "仅原文和机械统计；未概括轨迹、未推测原因"
}
```

## contract_specification

```json
{
  "source_path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
  "source_sha256": "61ecf2358ccdfd717fb69bc6c6a6b5336ef7eae90ca5bb486aaae106afa5a9c9",
  "parse_mode": "strict",
  "requested_table": "int_xero__invoice_line_items_enriched",
  "status": "found"
}
```
```json
{
  "yaml_path": [
    "modeling_spec",
    "intermediate_models",
    2
  ],
  "start_line": 430,
  "end_line": 542
}
```
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

## agent_final_SQL

```json
{
  "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
  "sha256": "60f138a9ab8273d7ab5d23b13fbdcefde6237f7b2c9e14169f87b8cb3066ce6c",
  "start_line": 1,
  "end_line": 68
}
```
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

## gold_SQL_仅供定位差异

```json
{
  "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
  "sha256": "0599aee7efdd2ded959f8bd8430d0e45e5e2c6992535ec3e70d164c531b14c33",
  "start_line": 1,
  "end_line": 130
}
```
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

## differences

```json
{
  "kind": "original_007_009",
  "record": "records/007_tolerance_tables.jsonl",
  "detail_record": "/home/katherine/Assumption_Ledger/records/005_cs_impl-027.json",
  "prediction_database": "/home/katherine/Assumption_Ledger/data/005_cs_work/impl-027_parallel/node_results.duckdb",
  "gold_database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb",
  "actual_schema": "intermediate",
  "table": "int_xero__invoice_line_items_enriched",
  "candidate_date": null,
  "comparison_columns": [
    "account_class",
    "account_code",
    "account_name",
    "account_type",
    "class",
    "contact_id",
    "contact_name",
    "cost_center",
    "customer",
    "department",
    "description",
    "discount_rate",
    "effective_tax_rate",
    "invoice_id",
    "line_amount",
    "line_item_id",
    "location",
    "project",
    "quantity",
    "region",
    "tax_amount",
    "tax_type",
    "unit_amount"
  ],
  "key_columns": [
    "line_item_id"
  ],
  "prediction_rows": 5000,
  "gold_rows": 5209,
  "row_delta": -209,
  "key_statistics": {
    "pred_distinct_keys": 5000,
    "gold_distinct_keys": 5000,
    "pred_duplicate_key_groups": 0,
    "gold_duplicate_key_groups": 209,
    "pred_only_keys": 0,
    "gold_only_keys": 0,
    "shared_keys": 5000,
    "shared_nonunique_key_groups": 209
  },
  "l0_column_differences": [
    {
      "column": "line_item_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "invoice_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "account_code",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "account_name",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "account_type",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "account_class",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "description",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "quantity",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "unit_amount",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "line_amount",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "tax_amount",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "effective_tax_rate",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "tax_type",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "discount_rate",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "contact_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "contact_name",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "region",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "department",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "project",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "location",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "class",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "customer",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "cost_center",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "count_semantics": "minimum_value_mismatch_pairs"
    }
  ],
  "l3_column_differences": [
    {
      "column": "account_class",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "account_code",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "account_name",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "account_type",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "class",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "contact_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "contact_name",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "cost_center",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "customer",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "department",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "description",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "discount_rate",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "effective_tax_rate",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "invoice_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "line_amount",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "line_item_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "location",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "project",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "quantity",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "region",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "tax_amount",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "tax_type",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    },
    {
      "column": "unit_amount",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 209,
      "marginal_multisets_equal": false,
      "count_semantics": "minimum_value_mismatch_pairs"
    }
  ],
  "whole_match_level": "仍不匹配",
  "keyed_match_level": "仍不匹配",
  "selection_reason": "未进入 011，沿用原差异",
  "value_representation": "Unmodified DuckDB CAST AS VARCHAR; SQL NULL is JSON null. Keys use the unchanged historical L0 normalization.",
  "new_queries_only_read_existing_results": true,
  "one_side_key_examples": {
    "prediction_only": [],
    "gold_only": []
  },
  "column_details": [
    {
      "column": "line_item_id",
      "l0_counts_verbatim": {
        "column": "line_item_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "line_item_id",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "0074e9c6-d137-4c0f-82b6-237997b3e378",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "0074e9c6-d137-4c0f-82b6-237997b3e378",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "007e2652-9012-4f67-8c96-2e0220e71f40",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "007e2652-9012-4f67-8c96-2e0220e71f40",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "00f25fdb-a6b5-4730-bf30-682d163873cc",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "00f25fdb-a6b5-4730-bf30-682d163873cc",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "invoice_id",
      "l0_counts_verbatim": {
        "column": "invoice_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "invoice_id",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "68252a67-64c4-44a4-af75-0bfa4eb73e55",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "68252a67-64c4-44a4-af75-0bfa4eb73e55",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "237c1f6a-2b82-4447-8878-b85a3e12602e",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "237c1f6a-2b82-4447-8878-b85a3e12602e",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "63f68993-747d-4609-9ac3-c52fc32078d3",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "63f68993-747d-4609-9ac3-c52fc32078d3",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "5613403d-2b1d-41ab-91dd-c00c2df8c2d4",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "5613403d-2b1d-41ab-91dd-c00c2df8c2d4",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "14414fd9-f82c-454d-be27-3aca7446e788",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "14414fd9-f82c-454d-be27-3aca7446e788",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "account_code",
      "l0_counts_verbatim": {
        "column": "account_code",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "account_code",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "820",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "820",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "802",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "802",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "200",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "200",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "200",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "200",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "200",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "200",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "account_name",
      "l0_counts_verbatim": {
        "column": "account_name",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "account_name",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "Sales Tax",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "Rent",
              "rows": 1
            },
            {
              "value": "Sales Tax",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "Accrued Liabilites",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "Accrued Liabilites",
              "rows": 1
            },
            {
              "value": "Vehicles",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "Sales",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "Sales",
              "rows": 1
            },
            {
              "value": "Subscriptions",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "Sales",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "Sales",
              "rows": 1
            },
            {
              "value": "Subscriptions",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "Sales",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "Sales",
              "rows": 1
            },
            {
              "value": "Subscriptions",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "account_type",
      "l0_counts_verbatim": {
        "column": "account_type",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "account_type",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "CURRLIAB",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "CURRLIAB",
              "rows": 1
            },
            {
              "value": "TERMLIAB",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "CURRLIAB",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "CURRLIAB",
              "rows": 1
            },
            {
              "value": "INVENTORY",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "REVENUE",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "REVENUE",
              "rows": 1
            },
            {
              "value": "TERMLIAB",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "REVENUE",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "REVENUE",
              "rows": 1
            },
            {
              "value": "TERMLIAB",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "REVENUE",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "REVENUE",
              "rows": 1
            },
            {
              "value": "TERMLIAB",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "account_class",
      "l0_counts_verbatim": {
        "column": "account_class",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "account_class",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "LIABILITY",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "EXPENSE",
              "rows": 1
            },
            {
              "value": "LIABILITY",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "LIABILITY",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "LIABILITY",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "REVENUE",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "ASSET",
              "rows": 1
            },
            {
              "value": "REVENUE",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "REVENUE",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "ASSET",
              "rows": 1
            },
            {
              "value": "REVENUE",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "REVENUE",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "ASSET",
              "rows": 1
            },
            {
              "value": "REVENUE",
              "rows": 1
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "description",
      "l0_counts_verbatim": {
        "column": "description",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "description",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "RGF0YSBBbmFseXNpcw==",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "RGF0YSBBbmFseXNpcw==",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "Premium Support",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "Premium Support",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "n/6TWOga+SeQg13EF9l/bw==",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "n/6TWOga+SeQg13EF9l/bw==",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "sYJ7/T3dKikSFc+tyKqUpw==",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "sYJ7/T3dKikSFc+tyKqUpw==",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "n/6TWOga+SeQg13EF9l/bw==",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "n/6TWOga+SeQg13EF9l/bw==",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "quantity",
      "l0_counts_verbatim": {
        "column": "quantity",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "quantity",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "44.5397",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "44.5397",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "25.2018",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "25.2018",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "8.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "8.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "1.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "1.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "8.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "8.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "unit_amount",
      "l0_counts_verbatim": {
        "column": "unit_amount",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "unit_amount",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "277.52",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "277.52",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "409.13",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "409.13",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "750.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "750.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "2800.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "2800.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "750.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "750.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "line_amount",
      "l0_counts_verbatim": {
        "column": "line_amount",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "line_amount",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "12360.66",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "12360.66",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "10310.81",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "10310.81",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "6000.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "6000.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "2800.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "2800.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "6000.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "6000.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "tax_amount",
      "l0_counts_verbatim": {
        "column": "tax_amount",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "tax_amount",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "1854.1",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "1854.1",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "1546.62",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "1546.62",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "0.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "0.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "0.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "0.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "0.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "0.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "effective_tax_rate",
      "l0_counts_verbatim": {
        "column": "effective_tax_rate",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "effective_tax_rate",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "17.65",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "17.65",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "17.65",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "17.65",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "0.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "0.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "0.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "0.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "0.0",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "0.0",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "tax_type",
      "l0_counts_verbatim": {
        "column": "tax_type",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "tax_type",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "NONE",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "NONE",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "OUTPUT",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "OUTPUT",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "OUTPUT",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "OUTPUT",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "OUTPUT",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "OUTPUT",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "OUTPUT",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "OUTPUT",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "discount_rate",
      "l0_counts_verbatim": {
        "column": "discount_rate",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "discount_rate",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "5.86",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "5.86",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "2.64",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "2.64",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "contact_id",
      "l0_counts_verbatim": {
        "column": "contact_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "contact_id",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "aea2f772-eff4-4b70-99c1-f8dfe35e072d",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "aea2f772-eff4-4b70-99c1-f8dfe35e072d",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "b03d1c5f-5adf-4d36-bf55-b93de89aa8ed",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "b03d1c5f-5adf-4d36-bf55-b93de89aa8ed",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "b958faad-9781-4ca5-a654-7bb3e22be5a5",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "b958faad-9781-4ca5-a654-7bb3e22be5a5",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "cfeedcb2-65d8-4f36-af83-5b3cb971bf20",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "cfeedcb2-65d8-4f36-af83-5b3cb971bf20",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "b958faad-9781-4ca5-a654-7bb3e22be5a5",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "b958faad-9781-4ca5-a654-7bb3e22be5a5",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "contact_name",
      "l0_counts_verbatim": {
        "column": "contact_name",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "contact_name",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "RW1tYSBEYXZpcw==",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "RW1tYSBEYXZpcw==",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "3+NWgUhibEvJS90jO92UZw==",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "3+NWgUhibEvJS90jO92UZw==",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "IuvBYv899Pt+Q8Nn/BrpXQ==",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "IuvBYv899Pt+Q8Nn/BrpXQ==",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": "3+NWgUhibEvJS90jO92UZw==",
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": "3+NWgUhibEvJS90jO92UZw==",
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "region",
      "l0_counts_verbatim": {
        "column": "region",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "region",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "department",
      "l0_counts_verbatim": {
        "column": "department",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "department",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "project",
      "l0_counts_verbatim": {
        "column": "project",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "project",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "location",
      "l0_counts_verbatim": {
        "column": "location",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "location",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "class",
      "l0_counts_verbatim": {
        "column": "class",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "class",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "customer",
      "l0_counts_verbatim": {
        "column": "customer",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "customer",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "cost_center",
      "l0_counts_verbatim": {
        "column": "cost_center",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "l3_counts_verbatim": {
        "column": "cost_center",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "gold_key_raw_text": {
            "line_item_id": "0050f62f-3244-4d1e-aaa4-fa8e8cad6555"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "gold_key_raw_text": {
            "line_item_id": "0074e9c6-d137-4c0f-82b6-237997b3e378"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "gold_key_raw_text": {
            "line_item_id": "007e2652-9012-4f67-8c96-2e0220e71f40"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "gold_key_raw_text": {
            "line_item_id": "00f25fdb-a6b5-4730-bf30-682d163873cc"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        },
        {
          "key_normalized": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "gold_key_raw_text": {
            "line_item_id": "0177f296-4abd-4824-ac8c-b5e1e6f2de7a"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 2,
          "agent_values": [
            {
              "value": null,
              "rows": 1
            }
          ],
          "gold_values": [
            {
              "value": null,
              "rows": 2
            }
          ],
          "kind": "duplicate_key_group_not_a_unique_row_pair",
          "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 209
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    }
  ]
}
```

## agent_constraints_006

```json
{
  "source_record": "records/006_contract_impl-027.json",
  "declarations": {
    "grain": [
      {
        "raw_text": "One row per line_item_id (rows with NULL line_item_id or NULL invoice_id are excluded)",
        "status": "parsed",
        "columns": [
          "line_item_id"
        ],
        "qualifier_original": "(rows with NULL line_item_id or NULL invoice_id are excluded)",
        "policy": "explicit identifiers matched to contract columns; no synonyms or inferred IDs",
        "sources": [
          {
            "yaml_path": [
              "modeling_spec",
              "intermediate_models",
              2,
              "grain"
            ],
            "start_line": 432,
            "end_line": 432,
            "original_excerpt": "      grain: One row per line_item_id (rows with NULL line_item_id or NULL invoice_id are excluded)\n",
            "decoded_value": "One row per line_item_id (rows with NULL line_item_id or NULL invoice_id are excluded)"
          }
        ]
      }
    ],
    "primary_key": [],
    "not_null": [
      {
        "columns": [
          "line_item_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "modeling_spec",
              "intermediate_models",
              2,
              "columns",
              0,
              "tests",
              0
            ],
            "start_line": 447,
            "end_line": 450,
            "original_excerpt": "        tests:\n        - not_null\n        - unique\n      - name: invoice_id\n",
            "decoded_value": [
              "not_null",
              "unique"
            ]
          }
        ]
      },
      {
        "columns": [
          "invoice_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "modeling_spec",
              "intermediate_models",
              2,
              "columns",
              1,
              "tests",
              0
            ],
            "start_line": 453,
            "end_line": 455,
            "original_excerpt": "        tests:\n        - not_null\n      - name: account_code\n",
            "decoded_value": [
              "not_null"
            ]
          }
        ]
      }
    ],
    "unique": [
      {
        "columns": [
          "line_item_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "modeling_spec",
              "intermediate_models",
              2,
              "columns",
              0,
              "tests",
              1
            ],
            "start_line": 447,
            "end_line": 450,
            "original_excerpt": "        tests:\n        - not_null\n        - unique\n      - name: invoice_id\n",
            "decoded_value": [
              "not_null",
              "unique"
            ]
          }
        ]
      }
    ]
  },
  "agent": {
    "table_exists": true,
    "actual_schema": "intermediate",
    "table_type": "BASE TABLE",
    "same_name_other_schemas": [],
    "row_count": 5000,
    "checks": {
      "grain": [
        {
          "columns": [
            "line_item_id"
          ],
          "status": "checked",
          "violated": false,
          "sql": "SELECT count(*),count(*) FILTER(WHERE \"__ledger_group_count\">1),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1),0),\n                      coalesce(sum(\"__ledger_group_count\"-1) FILTER(WHERE \"__ledger_group_count\">1),0),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"line_item_id\" IS NULL),0),\n                      count(*) FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"line_item_id\" IS NULL)),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"line_item_id\" IS NULL)),0),\n                      coalesce(sum(\"__ledger_group_count\"-1) FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"line_item_id\" IS NULL)),0),count(*) FILTER(WHERE \"__ledger_group_count\">1 AND (\"line_item_id\" IS NULL)),\n                      coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1 AND (\"line_item_id\" IS NULL)),0)\n                      FROM (SELECT \"line_item_id\",count(*) AS \"__ledger_group_count\" FROM \"intermediate\".\"int_xero__invoice_line_items_enriched\" GROUP BY \"line_item_id\") grouped_keys",
          "sql_key_order": [
            "line_item_id"
          ],
          "distinct_key_groups": 5000,
          "duplicate_key_groups": 0,
          "rows_in_duplicate_groups": 0,
          "excess_duplicate_rows": 0,
          "null_key_rows": 0,
          "nonnull_duplicate_key_groups": 0,
          "nonnull_rows_in_duplicate_groups": 0,
          "nonnull_excess_duplicate_rows": 0,
          "null_containing_duplicate_key_groups": 0,
          "rows_in_null_containing_duplicate_groups": 0
        }
      ],
      "primary_key": [],
      "not_null": [
        {
          "columns": [
            "line_item_id"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        },
        {
          "columns": [
            "invoice_id"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        }
      ],
      "unique": [
        {
          "columns": [
            "line_item_id"
          ],
          "status": "checked",
          "violated": false,
          "sql": "SELECT count(*),count(*) FILTER(WHERE \"__ledger_group_count\">1),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1),0),\n                      coalesce(sum(\"__ledger_group_count\"-1) FILTER(WHERE \"__ledger_group_count\">1),0),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"line_item_id\" IS NULL),0),\n                      count(*) FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"line_item_id\" IS NULL)),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"line_item_id\" IS NULL)),0),\n                      coalesce(sum(\"__ledger_group_count\"-1) FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"line_item_id\" IS NULL)),0),count(*) FILTER(WHERE \"__ledger_group_count\">1 AND (\"line_item_id\" IS NULL)),\n                      coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1 AND (\"line_item_id\" IS NULL)),0)\n                      FROM (SELECT \"line_item_id\",count(*) AS \"__ledger_group_count\" FROM \"intermediate\".\"int_xero__invoice_line_items_enriched\" GROUP BY \"line_item_id\") grouped_keys",
          "sql_key_order": [
            "line_item_id"
          ],
          "distinct_key_groups": 5000,
          "duplicate_key_groups": 0,
          "rows_in_duplicate_groups": 0,
          "excess_duplicate_rows": 0,
          "null_key_rows": 0,
          "nonnull_duplicate_key_groups": 0,
          "nonnull_rows_in_duplicate_groups": 0,
          "nonnull_excess_duplicate_rows": 0,
          "null_containing_duplicate_key_groups": 0,
          "rows_in_null_containing_duplicate_groups": 0,
          "including_nulls_duplicate_key_groups": 0,
          "including_nulls_rows_in_duplicate_groups": 0
        }
      ]
    },
    "actual_table": "int_xero__invoice_line_items_enriched",
    "actual_columns": [
      "line_item_id",
      "invoice_id",
      "account_code",
      "account_name",
      "account_type",
      "account_class",
      "description",
      "quantity",
      "unit_amount",
      "line_amount",
      "tax_amount",
      "effective_tax_rate",
      "tax_type",
      "discount_rate",
      "contact_id",
      "contact_name",
      "region",
      "department",
      "project",
      "location",
      "class",
      "customer",
      "cost_center",
      "processed_at"
    ],
    "missing_declared_columns": [],
    "not_null_count_sql": "SELECT count(*) FILTER(WHERE \"invoice_id\" IS NULL),count(*) FILTER(WHERE \"line_item_id\" IS NULL) FROM \"intermediate\".\"int_xero__invoice_line_items_enriched\"",
    "categories": {
      "grain": {
        "status": "checked_no_violation",
        "violated": false,
        "declared_checks": 1,
        "checked_checks": 1,
        "unknown_checks": 0,
        "complete": true
      },
      "primary_key": {
        "status": "not_declared",
        "violated": null,
        "declared_checks": 0,
        "checked_checks": 0,
        "unknown_checks": 0
      },
      "not_null": {
        "status": "checked_no_violation",
        "violated": false,
        "declared_checks": 2,
        "checked_checks": 2,
        "unknown_checks": 0,
        "complete": true
      },
      "unique": {
        "status": "checked_no_violation",
        "violated": false,
        "declared_checks": 1,
        "checked_checks": 1,
        "unknown_checks": 0,
        "complete": true
      }
    },
    "any_constraint_violated": false
  }
}
```

## all_markers_and_evidence_008

```json
{
  "source_record": "records/008_table_scan.jsonl",
  "verbatim_record": {
    "task": "impl-027",
    "layer": "intermediate",
    "table": "int_xero__invoice_line_items_enriched",
    "logical_contract_table": "int_xero__invoice_line_items_enriched",
    "delivery_name_mapping_evidence": [],
    "inventory_sources": {
      "retained_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb",
      "present_in_database": true,
      "agent_final_sql_files": [
        "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql"
      ]
    },
    "status_007": {
      "gold_table_exists_in_original_gold": true,
      "whole_level_007": "仍不匹配",
      "007_present": true,
      "004_failed_set_member": false,
      "005_failed_set_member": true,
      "005_current_pred_execution": true,
      "status_sources": [
        {
          "record": "records/007_tolerance_tables.jsonl",
          "scope": "cs",
          "rule": "whole_match_level",
          "value": "仍不匹配",
          "007_prediction_database": "/home/katherine/Assumption_Ledger/data/005_cs_work/impl-027_parallel/node_results.duckdb"
        }
      ],
      "status": "待标注",
      "comparison_lookup_layer": "intermediate",
      "comparison_lookup_table": "int_xero__invoice_line_items_enriched",
      "actual_gold_relation_exists": true
    },
    "contract": {
      "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
      "blocks": [
        {
          "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
          "start_line": 430,
          "end_line": 542,
          "original_text": "    - name: int_xero__invoice_line_items_enriched\n      description: Enriched Xero invoice line items with account, invoice/contact, and active tracking attributes; includes effective tax rate (percent, 2 decimals)\n      grain: One row per line_item_id (rows with NULL line_item_id or NULL invoice_id are excluded)\n      source_models:\n      - staging.stg_xero__invoice_line_item\n      - staging.stg_xero__invoice\n      - staging.stg_xero__account\n      - staging.stg_xero__contact\n      - staging.stg_xero__invoice_line_item_has_tracking_category\n      - staging.stg_xero__tracking_category\n      - staging.stg_xero__tracking_category_option\n      - staging.stg_xero__tracking_category_has_option\n      business_logic: '- Start from staging.stg_xero__invoice_line_item selecting: line_item_id, invoice_id, account_code, description, quantity, unit_amount, line_amount, tax_amount, tax_type, discount_rate, processed_at. - Exclude rows where line_item_id or invoice_id is NULL. - Join invoice header by invoice_id to add contact_id (left join; if no match, contact_id is NULL). - Join contacts by contact_id to add contact_name (left join; if no match, contact_name is NULL). - Join accounts by account_code after converting the line item account_code to text to match the account table; add account_name, account_type, account_class (left join; if no match, these are NULL). The output account_code remains the original numeric value from the line item. - Build tracking attributes: - Take invoice_id, line_item_id, tracking_option, tracking_category_id from staging.stg_xero__invoice_line_item_has_tracking_category. - Construct the set of active category/option pairs by linking categories to options through their relationship and keeping only options marked active. - Keep only tracking pairs whose option name exactly matches an active option for that category. - For each (invoice_id, line_item_id), pivot to columns for Region, Department, Project, Location, Class, Customer, and any category whose name contains \"Cost Center\". If multiple active options exist for the same category on a line, choose the lexicographically greatest non-null option name; if none, leave NULL. - Compute effective_tax_rate as: tax_amount divided by (line_amount minus tax_amount), multiplied by 100, then rounded to 2 decimals. If the denominator is zero or any input is null, the result is null. - All numeric values (quantity, unit_amount, line_amount, tax_amount, discount_rate) and processed_at are passed through without rescaling; processed_at retains its timezone.'\n      columns:\n      - name: line_item_id\n        data_type: VARCHAR\n        description: Unique identifier for the invoice line item; exactly one output row per value\n        tests:\n        - not_null\n        - unique\n      - name: invoice_id\n        data_type: VARCHAR\n        description: Invoice identifier from the line item; rows with NULL are excluded\n        tests:\n        - not_null\n      - name: account_code\n        data_type: BIGINT\n        description: Numeric account code from the line item; joined to accounts by converting to text; output remains numeric\n        tests: []\n      - name: account_name\n        data_type: VARCHAR\n        description: Account name from the accounts table via left join; NULL if no match\n        tests: []\n      - name: account_type\n        data_type: VARCHAR\n        description: Account type from the accounts table via left join; NULL if no match\n        tests: []\n      - name: account_class\n        data_type: VARCHAR\n        description: High-level account classification from the accounts table via left join; NULL if no match\n        tests: []\n      - name: description\n        data_type: VARCHAR\n        description: Line item description from staging\n        tests: []\n      - name: quantity\n        data_type: DOUBLE\n        description: Quantity from the line item; pass-through with no rounding or rescaling\n        tests: []\n      - name: unit_amount\n        data_type: DOUBLE\n        description: Unit amount from the line item; pass-through with no rescaling\n        tests: []\n      - name: line_amount\n        data_type: DOUBLE\n        description: Extended line amount from the line item; used with tax_amount to compute effective_tax_rate\n        tests: []\n      - name: tax_amount\n        data_type: DOUBLE\n        description: Tax amount for the line item; pass-through\n        tests: []\n      - name: effective_tax_rate\n        data_type: DOUBLE\n        description: Tax amount divided by (line amount minus tax amount) times 100, rounded to 2 decimals; NULL if denominator is zero or inputs are NULL\n        tests: []\n      - name: tax_type\n        data_type: VARCHAR\n        description: Tax type code from the line item; pass-through\n        tests: []\n      - name: discount_rate\n        data_type: DOUBLE\n        description: Discount rate from the line item; pass-through without normalization\n        tests: []\n      - name: contact_id\n        data_type: VARCHAR\n        description: Contact identifier from the invoice header via left join; NULL if not found\n        tests: []\n      - name: contact_name\n        data_type: VARCHAR\n        description: Contact name from the contacts table via left join on contact_id; NULL if no match\n        tests: []\n      - name: region\n        data_type: VARCHAR\n        description: Tracking option for category 'Region' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none\n        tests: []\n      - name: department\n        data_type: VARCHAR\n        description: Tracking option for category 'Department' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none\n        tests: []\n      - name: project\n        data_type: VARCHAR\n        description: Tracking option for category 'Project' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none\n        tests: []\n      - name: location\n        data_type: VARCHAR\n        description: Tracking option for category 'Location' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none\n        tests: []\n      - name: class\n        data_type: VARCHAR\n        description: Tracking option for category 'Class' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none\n        tests: []\n      - name: customer\n        data_type: VARCHAR\n        description: Tracking option for category 'Customer' (active options only); if multiple, the lexicographically greatest option is chosen; NULL if none\n        tests: []\n      - name: cost_center\n        data_type: VARCHAR\n        description: Tracking option for any category whose name contains 'Cost Center' (active only); if multiple, the lexicographically greatest option is chosen; NULL if none\n        tests: []\n      - name: processed_at\n        data_type: TIMESTAMP WITH TIME ZONE\n        description: Processing timestamp from line item staging; passed through with timezone preserved\n        tests: []\n",
          "yaml_path": [
            "modeling_spec",
            "intermediate_models",
            2
          ]
        }
      ]
    },
    "output": {
      "status": "checked",
      "exists": true,
      "row_count": 5000,
      "zero_rows": false,
      "columns": [
        {
          "name": "line_item_id",
          "type": "VARCHAR",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        },
        {
          "name": "invoice_id",
          "type": "VARCHAR",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        },
        {
          "name": "account_code",
          "type": "BIGINT",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        },
        {
          "name": "account_name",
          "type": "VARCHAR",
          "nonnull_rows": 1571,
          "sql_null_rows": 3429
        },
        {
          "name": "account_type",
          "type": "VARCHAR",
          "nonnull_rows": 1571,
          "sql_null_rows": 3429
        },
        {
          "name": "account_class",
          "type": "VARCHAR",
          "nonnull_rows": 1571,
          "sql_null_rows": 3429
        },
        {
          "name": "description",
          "type": "VARCHAR",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        },
        {
          "name": "quantity",
          "type": "DOUBLE",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        },
        {
          "name": "unit_amount",
          "type": "DOUBLE",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        },
        {
          "name": "line_amount",
          "type": "DOUBLE",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        },
        {
          "name": "tax_amount",
          "type": "DOUBLE",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        },
        {
          "name": "effective_tax_rate",
          "type": "DOUBLE",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        },
        {
          "name": "tax_type",
          "type": "VARCHAR",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        },
        {
          "name": "discount_rate",
          "type": "DOUBLE",
          "nonnull_rows": 4357,
          "sql_null_rows": 643
        },
        {
          "name": "contact_id",
          "type": "VARCHAR",
          "nonnull_rows": 4975,
          "sql_null_rows": 25
        },
        {
          "name": "contact_name",
          "type": "VARCHAR",
          "nonnull_rows": 2297,
          "sql_null_rows": 2703
        },
        {
          "name": "region",
          "type": "VARCHAR",
          "nonnull_rows": 2,
          "sql_null_rows": 4998
        },
        {
          "name": "department",
          "type": "VARCHAR",
          "nonnull_rows": 2,
          "sql_null_rows": 4998
        },
        {
          "name": "project",
          "type": "VARCHAR",
          "nonnull_rows": 3,
          "sql_null_rows": 4997
        },
        {
          "name": "location",
          "type": "VARCHAR",
          "nonnull_rows": 2,
          "sql_null_rows": 4998
        },
        {
          "name": "class",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 5000
        },
        {
          "name": "customer",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 5000
        },
        {
          "name": "cost_center",
          "type": "VARCHAR",
          "nonnull_rows": 1,
          "sql_null_rows": 4999
        },
        {
          "name": "processed_at",
          "type": "TIMESTAMP WITH TIME ZONE",
          "nonnull_rows": 5000,
          "sql_null_rows": 0
        }
      ],
      "all_null_columns": [
        {
          "column": "class",
          "table_rows": 5000
        },
        {
          "column": "customer",
          "table_rows": 5000
        }
      ],
      "constant_nonnull_columns": [],
      "equal_column_groups": [],
      "profile_sql": "SELECT count(*),count(\"line_item_id\"),min(CAST(\"line_item_id\" AS VARCHAR)),max(CAST(\"line_item_id\" AS VARCHAR)),sum(hash(CAST(\"line_item_id\" AS VARCHAR))),count(\"invoice_id\"),min(CAST(\"invoice_id\" AS VARCHAR)),max(CAST(\"invoice_id\" AS VARCHAR)),sum(hash(CAST(\"invoice_id\" AS VARCHAR))),count(\"account_code\"),min(CAST(\"account_code\" AS VARCHAR)),max(CAST(\"account_code\" AS VARCHAR)),sum(hash(CAST(\"account_code\" AS VARCHAR))),count(\"account_name\"),min(CAST(\"account_name\" AS VARCHAR)),max(CAST(\"account_name\" AS VARCHAR)),sum(hash(CAST(\"account_name\" AS VARCHAR))),count(\"account_type\"),min(CAST(\"account_type\" AS VARCHAR)),max(CAST(\"account_type\" AS VARCHAR)),sum(hash(CAST(\"account_type\" AS VARCHAR))),count(\"account_class\"),min(CAST(\"account_class\" AS VARCHAR)),max(CAST(\"account_class\" AS VARCHAR)),sum(hash(CAST(\"account_class\" AS VARCHAR))),count(\"description\"),min(CAST(\"description\" AS VARCHAR)),max(CAST(\"description\" AS VARCHAR)),sum(hash(CAST(\"description\" AS VARCHAR))),count(\"quantity\"),min(CAST(\"quantity\" AS VARCHAR)),max(CAST(\"quantity\" AS VARCHAR)),sum(hash(CAST(\"quantity\" AS VARCHAR))),count(\"unit_amount\"),min(CAST(\"unit_amount\" AS VARCHAR)),max(CAST(\"unit_amount\" AS VARCHAR)),sum(hash(CAST(\"unit_amount\" AS VARCHAR))),count(\"line_amount\"),min(CAST(\"line_amount\" AS VARCHAR)),max(CAST(\"line_amount\" AS VARCHAR)),sum(hash(CAST(\"line_amount\" AS VARCHAR))),count(\"tax_amount\"),min(CAST(\"tax_amount\" AS VARCHAR)),max(CAST(\"tax_amount\" AS VARCHAR)),sum(hash(CAST(\"tax_amount\" AS VARCHAR))),count(\"effective_tax_rate\"),min(CAST(\"effective_tax_rate\" AS VARCHAR)),max(CAST(\"effective_tax_rate\" AS VARCHAR)),sum(hash(CAST(\"effective_tax_rate\" AS VARCHAR))),count(\"tax_type\"),min(CAST(\"tax_type\" AS VARCHAR)),max(CAST(\"tax_type\" AS VARCHAR)),sum(hash(CAST(\"tax_type\" AS VARCHAR))),count(\"discount_rate\"),min(CAST(\"discount_rate\" AS VARCHAR)),max(CAST(\"discount_rate\" AS VARCHAR)),sum(hash(CAST(\"discount_rate\" AS VARCHAR))),count(\"contact_id\"),min(CAST(\"contact_id\" AS VARCHAR)),max(CAST(\"contact_id\" AS VARCHAR)),sum(hash(CAST(\"contact_id\" AS VARCHAR))),count(\"contact_name\"),min(CAST(\"contact_name\" AS VARCHAR)),max(CAST(\"contact_name\" AS VARCHAR)),sum(hash(CAST(\"contact_name\" AS VARCHAR))),count(\"region\"),min(CAST(\"region\" AS VARCHAR)),max(CAST(\"region\" AS VARCHAR)),sum(hash(CAST(\"region\" AS VARCHAR))),count(\"department\"),min(CAST(\"department\" AS VARCHAR)),max(CAST(\"department\" AS VARCHAR)),sum(hash(CAST(\"department\" AS VARCHAR))),count(\"project\"),min(CAST(\"project\" AS VARCHAR)),max(CAST(\"project\" AS VARCHAR)),sum(hash(CAST(\"project\" AS VARCHAR))),count(\"location\"),min(CAST(\"location\" AS VARCHAR)),max(CAST(\"location\" AS VARCHAR)),sum(hash(CAST(\"location\" AS VARCHAR))),count(\"class\"),min(CAST(\"class\" AS VARCHAR)),max(CAST(\"class\" AS VARCHAR)),sum(hash(CAST(\"class\" AS VARCHAR))),count(\"customer\"),min(CAST(\"customer\" AS VARCHAR)),max(CAST(\"customer\" AS VARCHAR)),sum(hash(CAST(\"customer\" AS VARCHAR))),count(\"cost_center\"),min(CAST(\"cost_center\" AS VARCHAR)),max(CAST(\"cost_center\" AS VARCHAR)),sum(hash(CAST(\"cost_center\" AS VARCHAR))),count(\"processed_at\"),min(CAST(\"processed_at\" AS VARCHAR)),max(CAST(\"processed_at\" AS VARCHAR)),sum(hash(CAST(\"processed_at\" AS VARCHAR))) FROM \"intermediate\".\"int_xero__invoice_line_items_enriched\"",
      "equal_column_confirmation_queries": [],
      "equality_policy": "exact CAST AS VARCHAR per row; no trim/case/numeric/date normalization; both NULL ignored; at least one nonnull equal row; one-sided NULL differs",
      "actual_schema": "intermediate",
      "actual_table": "int_xero__invoice_line_items_enriched",
      "relation_type": "BASE TABLE"
    },
    "agent_sql": [
      {
        "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
        "status": "parsed",
        "parser": "30.25.0",
        "sources": [
          {
            "name": "staging.stg_xero__invoice_line_item",
            "canonical": "staging.stg_xero__invoice_line_item",
            "locations": [
              {
                "line": 23,
                "end_line": 23
              }
            ]
          },
          {
            "name": "staging.stg_xero__invoice",
            "canonical": "staging.stg_xero__invoice",
            "locations": [
              {
                "line": 58,
                "end_line": 58
              }
            ]
          },
          {
            "name": "staging.stg_xero__contact",
            "canonical": "staging.stg_xero__contact",
            "locations": [
              {
                "line": 60,
                "end_line": 60
              }
            ]
          },
          {
            "name": "staging.stg_xero__account",
            "canonical": "staging.stg_xero__account",
            "locations": [
              {
                "line": 7,
                "end_line": 7
              }
            ]
          },
          {
            "name": "intermediate.int_xero__invoice_line_item_pivoted_tracking_categories",
            "canonical": "intermediate.int_xero__invoice_line_item_pivoted_tracking_categories",
            "locations": [
              {
                "line": 3,
                "end_line": 3
              }
            ]
          }
        ],
        "unresolved_source_expressions": [],
        "row_generator_expressions": [],
        "outputs": [
          {
            "name": "line_item_id",
            "alternatives": [
              {
                "expression_sql": "line_item_id",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 12,
                "end_line": 12,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "line.line_item_id",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "line_item_id",
            "retained_output_ordinal": 1
          },
          {
            "name": "invoice_id",
            "alternatives": [
              {
                "expression_sql": "invoice_id",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 13,
                "end_line": 13,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "line.invoice_id",
                "outer_line": 30
              }
            ],
            "sql_projection_name": "invoice_id",
            "retained_output_ordinal": 2
          },
          {
            "name": "account_code",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(line.account_code AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 31,
                "end_line": 31,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "account_code",
            "retained_output_ordinal": 3
          },
          {
            "name": "account_name",
            "alternatives": [
              {
                "expression_sql": "account_name",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 6,
                "end_line": 6,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "account.account_name",
                "outer_line": 32
              }
            ],
            "sql_projection_name": "account_name",
            "retained_output_ordinal": 4
          },
          {
            "name": "account_type",
            "alternatives": [
              {
                "expression_sql": "account_type",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 6,
                "end_line": 6,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "account.account_type",
                "outer_line": 33
              }
            ],
            "sql_projection_name": "account_type",
            "retained_output_ordinal": 5
          },
          {
            "name": "account_class",
            "alternatives": [
              {
                "expression_sql": "account_class",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 6,
                "end_line": 6,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "account.account_class",
                "outer_line": 34
              }
            ],
            "sql_projection_name": "account_class",
            "retained_output_ordinal": 6
          },
          {
            "name": "description",
            "alternatives": [
              {
                "expression_sql": "description",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 15,
                "end_line": 15,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "line.description",
                "outer_line": 35
              }
            ],
            "sql_projection_name": "description",
            "retained_output_ordinal": 7
          },
          {
            "name": "quantity",
            "alternatives": [
              {
                "expression_sql": "CAST(line.quantity AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 36,
                "end_line": 36,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "quantity",
            "retained_output_ordinal": 8
          },
          {
            "name": "unit_amount",
            "alternatives": [
              {
                "expression_sql": "CAST(line.unit_amount AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 37,
                "end_line": 37,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "unit_amount",
            "retained_output_ordinal": 9
          },
          {
            "name": "line_amount",
            "alternatives": [
              {
                "expression_sql": "CAST(line.line_amount AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 38,
                "end_line": 38,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "line_amount",
            "retained_output_ordinal": 10
          },
          {
            "name": "tax_amount",
            "alternatives": [
              {
                "expression_sql": "CAST(line.tax_amount AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 39,
                "end_line": 39,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "tax_amount",
            "retained_output_ordinal": 11
          },
          {
            "name": "effective_tax_rate",
            "alternatives": [
              {
                "expression_sql": "CASE WHEN line.tax_amount IS NULL OR line.line_amount IS NULL OR line.line_amount - line.tax_amount = 0 THEN NULL ELSE CAST(ROUND(line.tax_amount / (line.line_amount - line.tax_amount) * 100, 2) AS DOUBLE) END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 41,
                "end_line": 44,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "effective_tax_rate",
            "retained_output_ordinal": 12
          },
          {
            "name": "tax_type",
            "alternatives": [
              {
                "expression_sql": "tax_type",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 20,
                "end_line": 20,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "line.tax_type",
                "outer_line": 45
              }
            ],
            "sql_projection_name": "tax_type",
            "retained_output_ordinal": 13
          },
          {
            "name": "discount_rate",
            "alternatives": [
              {
                "expression_sql": "CAST(line.discount_rate AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 46,
                "end_line": 46,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "discount_rate",
            "retained_output_ordinal": 14
          },
          {
            "name": "contact_id",
            "alternatives": [
              {
                "expression_sql": "invoice.contact_id",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 47,
                "end_line": 47,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "contact_id",
            "retained_output_ordinal": 15
          },
          {
            "name": "contact_name",
            "alternatives": [
              {
                "expression_sql": "contact.contact_name",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 48,
                "end_line": 48,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "contact_name",
            "retained_output_ordinal": 16
          },
          {
            "name": "region",
            "alternatives": [
              {
                "expression_sql": "tracking.region",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 49,
                "end_line": 49,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "region",
            "retained_output_ordinal": 17
          },
          {
            "name": "department",
            "alternatives": [
              {
                "expression_sql": "tracking.department",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 50,
                "end_line": 50,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "department",
            "retained_output_ordinal": 18
          },
          {
            "name": "project",
            "alternatives": [
              {
                "expression_sql": "tracking.project",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 51,
                "end_line": 51,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "project",
            "retained_output_ordinal": 19
          },
          {
            "name": "location",
            "alternatives": [
              {
                "expression_sql": "tracking.location",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 52,
                "end_line": 52,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "location",
            "retained_output_ordinal": 20
          },
          {
            "name": "class",
            "alternatives": [
              {
                "expression_sql": "tracking.class",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 53,
                "end_line": 53,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "class",
            "retained_output_ordinal": 21
          },
          {
            "name": "customer",
            "alternatives": [
              {
                "expression_sql": "tracking.customer",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 54,
                "end_line": 54,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "customer",
            "retained_output_ordinal": 22
          },
          {
            "name": "cost_center",
            "alternatives": [
              {
                "expression_sql": "tracking.cost_center",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 55,
                "end_line": 55,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "cost_center",
            "retained_output_ordinal": 23
          },
          {
            "name": "processed_at",
            "alternatives": [
              {
                "expression_sql": "CAST(line.processed_at AS TIMESTAMPTZ)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
                "line": 56,
                "end_line": 56,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "processed_at",
            "retained_output_ordinal": 24
          }
        ],
        "null_literal_outputs": [],
        "constant_literal_outputs": [],
        "runtime_hits": []
      }
    ],
    "source_comparison": {
      "contract": {
        "status": "specified",
        "references": [
          {
            "name": "staging.stg_xero__invoice_line_item",
            "canonical": "staging.stg_xero__invoice_line_item",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "block_start_line": 430
          },
          {
            "name": "staging.stg_xero__invoice",
            "canonical": "staging.stg_xero__invoice",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "block_start_line": 430
          },
          {
            "name": "staging.stg_xero__account",
            "canonical": "staging.stg_xero__account",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "block_start_line": 430
          },
          {
            "name": "staging.stg_xero__contact",
            "canonical": "staging.stg_xero__contact",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "block_start_line": 430
          },
          {
            "name": "staging.stg_xero__invoice_line_item_has_tracking_category",
            "canonical": "staging.stg_xero__invoice_line_item_has_tracking_category",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "block_start_line": 430
          },
          {
            "name": "staging.stg_xero__tracking_category",
            "canonical": "staging.stg_xero__tracking_category",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "block_start_line": 430
          },
          {
            "name": "staging.stg_xero__tracking_category_option",
            "canonical": "staging.stg_xero__tracking_category_option",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "block_start_line": 430
          },
          {
            "name": "staging.stg_xero__tracking_category_has_option",
            "canonical": "staging.stg_xero__tracking_category_has_option",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "block_start_line": 430
          },
          {
            "name": "staging.stg_xero__invoice_line_item",
            "canonical": "staging.stg_xero__invoice_line_item",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "line": 434,
            "line_text": "      - staging.stg_xero__invoice_line_item"
          },
          {
            "name": "staging.stg_xero__invoice",
            "canonical": "staging.stg_xero__invoice",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "line": 435,
            "line_text": "      - staging.stg_xero__invoice"
          },
          {
            "name": "staging.stg_xero__account",
            "canonical": "staging.stg_xero__account",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "line": 436,
            "line_text": "      - staging.stg_xero__account"
          },
          {
            "name": "staging.stg_xero__contact",
            "canonical": "staging.stg_xero__contact",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "line": 437,
            "line_text": "      - staging.stg_xero__contact"
          },
          {
            "name": "staging.stg_xero__invoice_line_item_has_tracking_category",
            "canonical": "staging.stg_xero__invoice_line_item_has_tracking_category",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "line": 438,
            "line_text": "      - staging.stg_xero__invoice_line_item_has_tracking_category"
          },
          {
            "name": "staging.stg_xero__tracking_category",
            "canonical": "staging.stg_xero__tracking_category",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "line": 439,
            "line_text": "      - staging.stg_xero__tracking_category"
          },
          {
            "name": "staging.stg_xero__tracking_category_option",
            "canonical": "staging.stg_xero__tracking_category_option",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "line": 440,
            "line_text": "      - staging.stg_xero__tracking_category_option"
          },
          {
            "name": "staging.stg_xero__tracking_category_has_option",
            "canonical": "staging.stg_xero__tracking_category_has_option",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "line": 441,
            "line_text": "      - staging.stg_xero__tracking_category_has_option"
          },
          {
            "name": "staging.stg_xero__invoice_line_item",
            "canonical": "staging.stg_xero__invoice_line_item",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
            "line": 442,
            "line_text": "      business_logic: '- Start from staging.stg_xero__invoice_line_item selecting: line_item_id, invoice_id, account_code, description, quantity, unit_amount, line_amount, tax_amount, tax_type, discount_rate, processed_at. - Exclude rows where line_item_id or invoice_id is NULL. - Join invoice header by invoice_id to add contact_id (left join; if no match, contact_id is NULL). - Join contacts by contact_id to add contact_name (left join; if no match, contact_name is NULL). - Join accounts by account_code after converting the line item account_code to text to match the account table; add account_name, account_type, account_class (left join; if no match, these are NULL). The output account_code remains the original numeric value from the line item. - Build tracking attributes: - Take invoice_id, line_item_id, tracking_option, tracking_category_id from staging.stg_xero__invoice_line_item_has_tracking_category. - Construct the set of active category/option pairs by linking categories to options through their relationship and keeping only options marked active. - Keep only tracking pairs whose option name exactly matches an active option for that category. - For each (invoice_id, line_item_id), pivot to columns for Region, Department, Project, Location, Class, Customer, and any category whose name contains \"Cost Center\". If multiple active options exist for the same category on a line, choose the lexicographically greatest non-null option name; if none, leave NULL. - Compute effective_tax_rate as: tax_amount divided by (line_amount minus tax_amount), multiplied by 100, then rounded to 2 decimals. If the denominator is zero or any input is null, the result is null. - All numeric values (quantity, unit_amount, line_amount, tax_amount, discount_rate) and processed_at are passed through without rescaling; processed_at retains its timezone.'"
          }
        ],
        "canonical_names": [
          "staging.stg_xero__account",
          "staging.stg_xero__contact",
          "staging.stg_xero__invoice",
          "staging.stg_xero__invoice_line_item",
          "staging.stg_xero__invoice_line_item_has_tracking_category",
          "staging.stg_xero__tracking_category",
          "staging.stg_xero__tracking_category_has_option",
          "staging.stg_xero__tracking_category_option"
        ]
      },
      "agent_direct_read_sources": [
        "intermediate.int_xero__invoice_line_item_pivoted_tracking_categories",
        "staging.stg_xero__account",
        "staging.stg_xero__contact",
        "staging.stg_xero__invoice",
        "staging.stg_xero__invoice_line_item"
      ],
      "scope": "direct physical relation references through reachable local CTE/subqueries; no transitive expansion through other output tables or stored views",
      "complete": true,
      "specified_but_not_read": [
        "staging.stg_xero__invoice_line_item_has_tracking_category",
        "staging.stg_xero__tracking_category",
        "staging.stg_xero__tracking_category_has_option",
        "staging.stg_xero__tracking_category_option"
      ],
      "read_but_not_specified": [
        "intermediate.int_xero__invoice_line_item_pivoted_tracking_categories"
      ]
    },
    "time_dependencies": {
      "agent_sql": {
        "available": true,
        "appears": false,
        "hits": []
      },
      "gold_sql": {
        "available": true,
        "appears": false,
        "hits": [],
        "paths": [
          "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql"
        ]
      },
      "contract": {
        "available": true,
        "appears": false,
        "hits": []
      }
    },
    "any_result_keyword_excerpt_ids": [
      "008-012794"
    ],
    "trace_flags": {
      "A1_zero_rows": false,
      "A2_all_null_column": true,
      "A3_constant_nonnull_column": false,
      "A4_equal_columns": false,
      "A4_equal_columns_different_description_texts": false,
      "B5_null_literal_output": false,
      "B6_constant_literal_output": false,
      "B7_specified_not_read": true,
      "B7_read_not_specified": true,
      "B8_shared_single_source": false,
      "C9_agent_runtime_text": false,
      "C9_gold_runtime_text": false,
      "C9_contract_runtime_text": false,
      "D10_keyword_in_final_report": false,
      "D10_keyword_in_any_result_field": true
    }
  }
}
```

## trace_excerpts

```json
{
  "archive": "/home/katherine/Assumption_Ledger/traces/dacomp_deimpl_prev.tar.gz",
  "event_source_root": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent",
  "actual_read_sources_from_008_B7": [
    "intermediate.int_xero__invoice_line_item_pivoted_tracking_categories",
    "staging.stg_xero__account",
    "staging.stg_xero__contact",
    "staging.stg_xero__invoice",
    "staging.stg_xero__invoice_line_item"
  ],
  "name_match_policy": "Case-insensitive complete identifier-name boundaries; source names include qualified form and bare leaf name. No semantic association inferred.",
  "matched_step_count": 9,
  "full_original_characters_before_budget": 49460,
  "budget_triggered": false,
  "source_only_steps_indexed": 0,
  "retained_full_original_characters": 49460,
  "full_target_steps_exceed_60000": false,
  "budget_policy": "If total command/output text exceeds 60000 characters, keep every target-table step complete and retain only id/location/first line for source-only steps. Do not rewrite or truncate a kept original step."
}
```

### event 7

```json
{
  "event_id": 7,
  "agent_command_sequence": 2,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/7.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1764,
    "decoded_characters": 91
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/7.json",
  "timestamp": "2026-10-25T05:48:21.354318",
  "target_table_name_hits": [
    "int_xero__invoice_line_items_enriched"
  ],
  "source_table_name_hits": [
    "int_xero__invoice_line_item_pivoted_tracking_categories",
    "stg_xero__invoice_line_item",
    "stg_xero__account",
    "stg_xero__contact",
    "stg_xero__invoice"
  ],
  "full_original_characters": 1839,
  "retention": "full_original"
}
```
```bash
find sql -type f -maxdepth 4 -print -exec wc -l {} \; && cat config/layer_dependencies.yaml
```
```json
{
  "event_id": 8,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/8.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1449,
    "decoded_characters": 1748
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/8.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
find: warning: you have specified the global option -maxdepth after the argument -type, but global options are not positional, i.e., -maxdepth affects tests specified before it as well as those specified after it.  Please specify global options before other arguments.
# Xero Data Layer Execution Dependencies
# This file defines the execution order for SQL transformations in the xero project

layers:
  staging:
    description: "Raw data standardization and cleaning with validation rules"
    dependencies: []  # staging only references raw layer (implicit)
    tables:
      - stg_xero__account
      - stg_xero__bank_transaction
      - stg_xero__contact
      - stg_xero__credit_note
      - stg_xero__invoice
      - stg_xero__invoice_line_item
      - stg_xero__invoice_line_item_has_tracking_category
      - stg_xero__journal
      - stg_xero__journal_line
      - stg_xero__journal_line_has_tracking_category
      - stg_xero__organization
      - stg_xero__tracking_category
      - stg_xero__tracking_category_has_option
      - stg_xero__tracking_category_option

  intermediate:
    description: "Business logic and data integration with pivoted tracking categories and facts"
    dependencies: ["staging"]
    tables:
      - int_xero__tracking_categories_with_options
      - int_xero__invoice_line_item_pivoted_tracking_categories
      - int_xero__journal_line_pivoted_tracking_categories
      - int_xero__general_ledger_fact
      - int_xero__invoice_line_items_enriched

  marts:
    description: "Analysis-ready business entities and reports"
    dependencies: ["intermediate"]
    tables:
      - xero__general_ledger
      - xero__balance_sheet_report
      - xero__profit_and_loss_report
      - xero__invoice_line_items
```

### event 9

```json
{
  "event_id": 9,
  "agent_command_sequence": 3,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/9.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1694,
    "decoded_characters": 22
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/9.json",
  "timestamp": "2026-10-25T05:48:21.381595",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "intermediate.int_xero__invoice_line_item_pivoted_tracking_categories",
    "int_xero__invoice_line_item_pivoted_tracking_categories",
    "staging.stg_xero__invoice_line_item",
    "stg_xero__invoice_line_item",
    "staging.stg_xero__account",
    "staging.stg_xero__contact",
    "staging.stg_xero__invoice",
    "stg_xero__account",
    "stg_xero__contact",
    "stg_xero__invoice"
  ],
  "full_original_characters": 9793,
  "retention": "full_original"
}
```
```bash
sed -n '1,240p' run.py
```
```json
{
  "event_id": 10,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/10.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1380,
    "decoded_characters": 9771
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/10.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
#!/usr/bin/env python3

import os
import yaml
import duckdb
from pathlib import Path
from typing import List, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XeroDataPipeline:
    """Xero Data Pipeline Orchestrator - Supports layered schema architecture and processing of Xero accounting data"""

    def __init__(self,
                 source_db_path: str = "xero_start.duckdb",
                 target_db_path: str = "xero.duckdb",
                 config_path: str = "config/layer_dependencies.yaml"):
        self.source_db_path = source_db_path
        self.target_db_path = target_db_path
        self.config_path = config_path
        self.config = self._load_config()
        self.sql_dir = Path("sql")

  
        self.schema_config = {
            'raw': 'raw',                                  
            'staging': 'staging',                         
            'intermediate': 'intermediate',                      
            'marts': 'marts'                               
        }

  
        self.conn = None

    def _load_config(self) -> dict:
        """Load the configuration file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Configuration file parsing error: {e}")
            raise

    def _initialize_database(self):
        """Initialize the working database, create the layered schema architecture, and import raw data"""
        logger.info(f"📥 Creating new layered database: {self.target_db_path}")

  
        if not os.path.exists(self.source_db_path):
            raise FileNotFoundError(f"Source database file not found: {self.source_db_path}")

        self.conn = duckdb.connect(self.target_db_path)

  
        self._create_schemas()

  
        self._import_raw_data()

        logger.info(f"✓ Layered database initialization complete: {self.target_db_path}")

    def _create_schemas(self):
        """Create schemas for data layers"""
        logger.info("🏗️ Creating Schema layered architecture")

        for layer, schema_name in self.schema_config.items():
            try:
                self.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                logger.info(f"  ✓ Created schema: {schema_name}")
            except Exception as e:
                logger.error(f"  ✗ Failed to create schema {schema_name}: {e}")
                raise

    def _import_raw_data(self):
        """Import raw data from the source database to the raw schema"""
        logger.info("📥 Importing raw data to raw schema")

  
        try:
            source_conn = duckdb.connect(self.source_db_path)
        except Exception as e:
            logger.error(f"Unable to connect to source database {self.source_db_path}: {e}")
            raise

        try:
      
            tables_result = source_conn.execute("SHOW TABLES FROM raw").fetchall()
            source_tables = [table[0] for table in tables_result]

            logger.info(f"Found {len(source_tables)} raw tables")

      
            for table_name in source_tables:
                try:
              
                    data = source_conn.execute(f"SELECT * FROM raw.{table_name}").fetchall()
                    columns_info = source_conn.execute(f"DESCRIBE raw.{table_name}").fetchall()

              
                    column_defs = []
                    for col_info in columns_info:
                        col_name, col_type = col_info[0], col_info[1]
                  
                        if col_name.lower() in ['end', 'start', 'order', 'group', 'select', 'from', 'where']:
                            safe_col_name = f'"{col_name}"'
                        else:
                            safe_col_name = col_name
                        column_defs.append(f"{safe_col_name} {col_type}")

                    create_sql = f"CREATE OR REPLACE TABLE raw.{table_name} ({', '.join(column_defs)})"
                    self.conn.execute(create_sql)

              
                    if data:
                        placeholders = ', '.join(['?' for _ in columns_info])
                        insert_sql = f"INSERT INTO raw.{table_name} VALUES ({placeholders})"
                        self.conn.executemany(insert_sql, data)

                    logger.info(f"  ✓ raw.{table_name}: {len(data)} rows")

                except Exception as e:
                    logger.error(f"  ✗ Failed to import table {table_name}: {e}")

        finally:
            source_conn.close()

        logger.info("✓ Raw data import complete")

    def _load_sql_file(self, file_path: Path) -> str:
        """Load SQL file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"SQL file {file_path} not found")
            raise

    def _execute_sql(self, sql: str, table_name: str, layer_name: str) -> bool:
        """Execute SQL and create a table in the specified schema"""
        try:
      
            target_schema = self.schema_config[layer_name]
            full_table_name = f"{target_schema}.{table_name}"

      
            processed_sql = self._process_sql_references(sql, layer_name)

      
            create_table_sql = f"CREATE OR REPLACE TABLE {full_table_name} AS ({processed_sql})"

            logger.info(f"Executing: {full_table_name}")
            self.conn.execute(create_table_sql)

      
            count_result = self.conn.execute(f"SELECT COUNT(*) FROM {full_table_name}").fetchone()
            row_count = count_result[0] if count_result else 0

            logger.info(f"✓ {full_table_name}: {row_count:,} rows")
            return True

        except Exception as e:
            logger.error(f"✗ {full_table_name}: {e}")
            return False

    def _process_sql_references(self, sql: str, current_layer: str) -> str:
        """Process table references in SQL, converting them to schema.table format"""
        import re
        processed_sql = sql

  
        staging_table_mappings = {
            'stg_xero__account': 'staging.stg_xero__account',
            'stg_xero__bank_transaction': 'staging.stg_xero__bank_transaction',
            'stg_xero__contact': 'staging.stg_xero__contact',
            'stg_xero__credit_note': 'staging.stg_xero__credit_note',
            'stg_xero__invoice': 'staging.stg_xero__invoice',
            'stg_xero__invoice_line_item': 'staging.stg_xero__invoice_line_item',
            'stg_xero__invoice_line_item_has_tracking_category': 'staging.stg_xero__invoice_line_item_has_tracking_category',
            'stg_xero__journal': 'staging.stg_xero__journal',
            'stg_xero__journal_line': 'staging.stg_xero__journal_line',
            'stg_xero__journal_line_has_tracking_category': 'staging.stg_xero__journal_line_has_tracking_category',
            'stg_xero__organization': 'staging.stg_xero__organization',
            'stg_xero__tracking_category': 'staging.stg_xero__tracking_category',
            'stg_xero__tracking_category_has_option': 'staging.stg_xero__tracking_category_has_option',
            'stg_xero__tracking_category_option': 'staging.stg_xero__tracking_category_option',
            'int_xero__tracking_categories_with_options': 'intermediate.int_xero__tracking_categories_with_options',
            'int_xero__invoice_line_item_pivoted_tracking_categories': 'intermediate.int_xero__invoice_line_item_pivoted_tracking_categories',
            'int_xero__journal_line_pivoted_tracking_categories': 'intermediate.int_xero__journal_line_pivoted_tracking_categories',
            'xero__general_ledger': 'marts.xero__general_ledger',
            'xero__balance_sheet_report': 'marts.xero__balance_sheet_report',
            'xero__profit_and_loss_report': 'marts.xero__profit_and_loss_report',
            'xero__invoice_line_items': 'marts.xero__invoice_line_items'
        }

  
        cte_pattern = r'(\w+)\s+as\s*\('
        cte_names = set(re.findall(cte_pattern, processed_sql, re.IGNORECASE))

  
        for table_name, schema_table in staging_table_mappings.items():
            if table_name not in cte_names:
          
                patterns = [
                    r'\bFROM\s+' + re.escape(table_name) + r'\b',
                    r'\bJOIN\s+' + re.escape(table_name) + r'\b',
                    r'\bfrom\s+' + re.escape(table_name) + r'\b',
                    r'\bjoin\s+' + re.escape(table_name) + r'\b',
                    r'\b' + re.escape(table_name) + r'\s+ON\b',
                    r'\b' + re.escape(table_name) + r'\s+on\b'
                ]

                for pattern in patterns:
                    replacement = re.sub(table_name, schema_table, '', count=1)
                    if 'FROM' in pattern.upper():
                        replacement = f'FROM {schema_table}'
                    elif 'JOIN' in pattern.upper():
                        replacement = f'JOIN {schema_table}'

                    processed_sql = re.sub(pattern, replacement, processed_sql, flags=re.IGNORECASE)

        return processed_sql

    def _execute_layer(self, layer_name: str) -> bool:
        """Execute all tables in a specified layer"""
        layer_config = self.config['layers'][layer_name]
        tables = layer_config.get('tables', [])

  
        execution_order = self.config.get('execution_order', {}).get(layer_name, tables)

        logger.info(f"\n=== Executing {layer_name.upper()} Layer ===")
```

### event 19

```json
{
  "event_id": 19,
  "agent_command_sequence": 8,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/19.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 15487,
    "decoded_characters": 6900
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/19.json",
  "timestamp": "2026-10-25T05:48:58.001501",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "stg_xero__invoice_line_item",
    "stg_xero__account",
    "stg_xero__contact",
    "stg_xero__invoice"
  ],
  "full_original_characters": 6900,
  "retention": "full_original"
}
```
```bash
mkdir -p sql/staging sql/intermediate sql/marts && cat > /tmp/gen.py <<'PY'
from pathlib import Path
stages={
'stg_xero__account':('xero_account_data', '''    account_id::VARCHAR AS account_id,
    name::VARCHAR AS account_name,
    NULLIF(regexp_replace(trim(code), '[!@#$%^&*()]', '', 'g'), '')::VARCHAR AS account_code,
    type::VARCHAR AS account_type,
    class::VARCHAR AS account_class,
    TRY_CAST(_fivetran_synced AS TIMESTAMP) AS processed_at''', 'WHERE NULLIF(trim(account_id), \'\') IS NOT NULL\n  AND NULLIF(trim(name), \'\') IS NOT NULL'),
'stg_xero__bank_transaction':('xero_bank_transaction_data', '''    bank_transaction_id::VARCHAR AS bank_transaction_id,
    contact_id::VARCHAR AS contact_id,
    NULL::TIMESTAMP AS processed_at''', "WHERE NULLIF(trim(bank_transaction_id), '') IS NOT NULL"),
'stg_xero__contact':('xero_contact_data', '''    contact_id::VARCHAR AS contact_id,
    CASE
        WHEN name IS NULL OR trim(name) = '' THEN NULL
        WHEN regexp_matches(name, '(INVALID|BAD|XXX)') THEN NULL
        WHEN strpos(name, '!@#$%^&*()') > 0 THEN NULL
        WHEN NOT regexp_matches(name, '^[A-Za-z0-9+/]+==$') THEN NULL
        ELSE name::VARCHAR
    END AS contact_name,
    NULL::TIMESTAMP AS processed_at''', "WHERE NULLIF(trim(contact_id), '') IS NOT NULL"),
'stg_xero__credit_note':('xero_credit_note_data', '''    credit_note_id::VARCHAR AS credit_note_id,
    contact_id::VARCHAR AS contact_id,
    NULL::TIMESTAMP AS processed_at''', "WHERE NULLIF(trim(credit_note_id), '') IS NOT NULL"),
'stg_xero__invoice':('xero_invoice_data', '''    invoice_id::VARCHAR AS invoice_id,
    contact_id::VARCHAR AS contact_id,
    TRY_CAST(date AS DATE) AS invoice_date,
    TRY_CAST(_fivetran_synced AS TIMESTAMP) AS processed_at''', "WHERE NULLIF(trim(invoice_id), '') IS NOT NULL\n  AND TRY_CAST(date AS DATE) IS NOT NULL\n  AND TRY_CAST(date AS DATE) <= current_date + INTERVAL '1 year'"),
'stg_xero__invoice_line_item':('xero_invoice_line_item_data', '''    line_item_id::VARCHAR AS line_item_id,
    invoice_id::VARCHAR AS invoice_id,
    account_code::VARCHAR AS account_code,
    description::VARCHAR AS description,
    discount_entered_as_percent::BOOLEAN AS discount_entered_as_percent,
    TRY_CAST(discount_rate AS DECIMAL(18, 2)) AS discount_rate,
    item_code::VARCHAR AS item_code,
    TRY_CAST(line_amount AS DECIMAL(18, 2)) AS line_amount,
    TRY_CAST(quantity AS DECIMAL(18, 2)) AS quantity,
    TRY_CAST(tax_amount AS DECIMAL(18, 2)) AS tax_amount,
    tax_type::VARCHAR AS tax_type,
    TRY_CAST(unit_amount AS DECIMAL(18, 2)) AS unit_amount,
    TRY_CAST(_fivetran_synced AS TIMESTAMP) AS processed_at''', "WHERE NULLIF(trim(line_item_id), '') IS NOT NULL\n  AND NULLIF(trim(invoice_id), '') IS NOT NULL\n  AND unit_amount IS NOT NULL\n  AND unit_amount = round(unit_amount, 2)\n  AND unit_amount BETWEEN -1000000 AND 1000000"),
'stg_xero__invoice_line_item_has_tracking_category':('xero_invoice_line_item_has_tracking_category_data', '''    _fivetran_synced::VARCHAR AS _fivetran_synced,
    invoice_id::VARCHAR AS invoice_id,
    line_item_id::VARCHAR AS line_item_id,
    tracking_category_id::VARCHAR AS tracking_category_id,
    "option"::VARCHAR AS tracking_option,
    TRY_CAST(_fivetran_synced AS TIMESTAMP) AS processed_at''', "WHERE invoice_id IS NOT NULL AND line_item_id IS NOT NULL AND tracking_category_id IS NOT NULL"),
'stg_xero__journal':('xero_journal_data', '''    journal_id::VARCHAR AS journal_id,
    TRY_CAST(created_date_utc AS TIMESTAMP) AS created_date_utc,
    TRY_CAST(journal_date AS TIMESTAMP) AS journal_date,
    CASE
        WHEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS BIGINT) <= 9999999
            THEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS INTEGER)
        ELSE NULL
    END AS journal_number,
    reference::VARCHAR AS reference,
    source_id::VARCHAR AS source_id,
    source_type::VARCHAR AS source_type,
    NULL::TIMESTAMP AS processed_at''', "WHERE NULLIF(trim(journal_id), '') IS NOT NULL"),
'stg_xero__journal_line':('xero_journal_line_data', '''    journal_line_id::VARCHAR AS journal_line_id,
    journal_id::VARCHAR AS journal_id,
    TRY_CAST(account_code AS BIGINT) AS account_code,
    account_id::VARCHAR AS account_id,
    account_name::VARCHAR AS account_name,
    account_type::VARCHAR AS account_type,
    description::VARCHAR AS description,
    TRY_CAST(gross_amount AS DECIMAL(18, 2)) AS gross_amount,
    TRY_CAST(net_amount AS DECIMAL(18, 2)) AS net_amount,
    TRY_CAST(tax_amount AS DECIMAL(18, 2)) AS tax_amount,
    tax_name::VARCHAR AS tax_name,
    tax_type::VARCHAR AS tax_type,
    NULL::TIMESTAMP AS processed_at''', ''),
'stg_xero__journal_line_has_tracking_category':('xero_journal_line_has_tracking_category_data', '''    _fivetran_synced::VARCHAR AS _fivetran_synced,
    journal_id::VARCHAR AS journal_id,
    journal_line_id::VARCHAR AS journal_line_id,
    tracking_category_id::VARCHAR AS tracking_category_id,
    "option"::VARCHAR AS tracking_option,
    TRY_CAST(_fivetran_synced AS TIMESTAMP) AS processed_at''', "WHERE journal_line_id IS NOT NULL AND tracking_category_id IS NOT NULL"),
'stg_xero__organization':('xero_organization_data', '''    organisation_id::VARCHAR AS organisation_id,
    financial_year_end_day::BIGINT AS financial_year_end_day,
    financial_year_end_month::BIGINT AS financial_year_end_month,
    NULL::TIMESTAMP AS processed_at''', 'WHERE organisation_id IS NOT NULL'),
'stg_xero__tracking_category':('xero_tracking_category_data', '''    tracking_category_id::VARCHAR AS tracking_category_id,
    name::VARCHAR AS tracking_category_name,
    CASE WHEN status IS NULL OR starts_with(status, 'INVALID') THEN 'UNKNOWN' ELSE status END::VARCHAR AS status,
    TRY_CAST(_fivetran_synced AS TIMESTAMP) AS processed_at''', 'WHERE tracking_category_id IS NOT NULL'),
'stg_xero__tracking_category_has_option':('xero_tracking_category_has_option_data', '''    _fivetran_synced::VARCHAR AS _fivetran_synced,
    tracking_category_id::VARCHAR AS tracking_category_id,
    tracking_option_id::VARCHAR AS tracking_option_id,
    TRY_CAST(_fivetran_synced AS TIMESTAMP) AS processed_at''', 'WHERE tracking_category_id IS NOT NULL AND tracking_option_id IS NOT NULL'),
'stg_xero__tracking_category_option':('xero_tracking_category_option_data', '''    tracking_option_id::VARCHAR AS tracking_option_id,
    name::VARCHAR AS tracking_option_name,
    status::VARCHAR AS status,
    is_active::BOOLEAN AS is_active,
    is_archived::BOOLEAN AS is_archived,
    TRY_CAST(_fivetran_synced AS TIMESTAMP) AS processed_at''', 'WHERE tracking_option_id IS NOT NULL'),
}
for name,(src,cols,where) in stages.items():
    sql=f"SELECT\n{cols}\nFROM raw.{src}"
    if where: sql+='\n'+where
    Path(f'sql/staging/{name}.sql').write_text(sql+'\n')
PY
python /tmp/gen.py
```
```json
{
  "event_id": 20,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/20.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 15172,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/20.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text

```

### event 21

```json
{
  "event_id": 21,
  "agent_command_sequence": 9,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/21.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 17132,
    "decoded_characters": 7652
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/21.json",
  "timestamp": "2026-10-25T05:49:16.949822",
  "target_table_name_hits": [
    "int_xero__invoice_line_items_enriched"
  ],
  "source_table_name_hits": [
    "intermediate.int_xero__invoice_line_item_pivoted_tracking_categories",
    "int_xero__invoice_line_item_pivoted_tracking_categories",
    "staging.stg_xero__invoice_line_item",
    "stg_xero__invoice_line_item",
    "staging.stg_xero__account",
    "staging.stg_xero__contact",
    "staging.stg_xero__invoice",
    "stg_xero__account",
    "stg_xero__contact",
    "stg_xero__invoice"
  ],
  "full_original_characters": 7652,
  "retention": "full_original"
}
```
```bash
cat > /tmp/models.py <<'PY'
from pathlib import Path

def write(layer,name,sql): Path(f'sql/{layer}/{name}.sql').write_text(sql.strip()+'\n')
write('intermediate','int_xero__tracking_categories_with_options', '''
SELECT
    category.tracking_category_id,
    category.tracking_category_name,
    category.status,
    option.tracking_option_id,
    option.tracking_option_name,
    option.status AS option_status,
    option.is_active,
    option.is_archived,
    category.processed_at
FROM staging.stg_xero__tracking_category AS category
INNER JOIN staging.stg_xero__tracking_category_has_option AS relationship
    ON category.tracking_category_id = relationship.tracking_category_id
INNER JOIN staging.stg_xero__tracking_category_option AS option
    ON relationship.tracking_option_id = option.tracking_option_id
WHERE option.is_active = TRUE
  AND category.tracking_category_id IS NOT NULL
  AND option.tracking_option_id IS NOT NULL
''')

def pivot(assign_table, key1, key2, journal=False):
    keys=f"assignment.{key1}, assignment.{key2}"
    # source mapping option text is exact matched against relationship-based active option names.
    return f'''WITH active_category_options AS (
    SELECT
        category.tracking_category_id,
        category.tracking_category_name,
        option.tracking_option_name
    FROM staging.stg_xero__tracking_category AS category
    INNER JOIN staging.stg_xero__tracking_category_has_option AS relationship
        ON category.tracking_category_id = relationship.tracking_category_id
    INNER JOIN staging.stg_xero__tracking_category_option AS option
        ON relationship.tracking_option_id = option.tracking_option_id
    WHERE option.is_active = TRUE
),
valid_assignments AS (
    SELECT DISTINCT
        {keys},
        reference.tracking_category_name,
        assignment.tracking_option
    FROM staging.{assign_table} AS assignment
    INNER JOIN active_category_options AS reference
        ON assignment.tracking_category_id = reference.tracking_category_id
       AND assignment.tracking_option = reference.tracking_option_name
    WHERE assignment.{key1} IS NOT NULL
      AND assignment.{key2} IS NOT NULL
),
pivoted AS (
    SELECT
        {key1},
        {key2},
        MAX(assignment.tracking_option) FILTER (WHERE tracking_category_name = 'Region') AS region,
        MAX(assignment.tracking_option) FILTER (WHERE tracking_category_name = 'Department') AS department,
        MAX(assignment.tracking_option) FILTER (WHERE tracking_category_name = 'Project') AS project,
        MAX(assignment.tracking_option) FILTER (WHERE tracking_category_name = 'Location') AS location,
        MAX(assignment.tracking_option) FILTER (WHERE tracking_category_name = 'Class') AS class,
        MAX(assignment.tracking_option) FILTER (WHERE tracking_category_name = 'Customer') AS customer,
        MAX(assignment.tracking_option) FILTER (WHERE contains(tracking_category_name, 'Cost Center')) AS cost_center
    FROM valid_assignments AS assignment
    GROUP BY {key1}, {key2}
)
SELECT * FROM pivoted'''

write('intermediate','int_xero__invoice_line_item_pivoted_tracking_categories', pivot('stg_xero__invoice_line_item_has_tracking_category','invoice_id','line_item_id'))
write('intermediate','int_xero__journal_line_pivoted_tracking_categories', pivot('stg_xero__journal_line_has_tracking_category','journal_id','journal_line_id'))

write('intermediate','int_xero__invoice_line_items_enriched', '''
WITH tracking AS (
    SELECT *
    FROM intermediate.int_xero__invoice_line_item_pivoted_tracking_categories
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
    LEFT JOIN staging.stg_xero__account AS account
        ON line.account_code = TRY_CAST(account.account_code AS BIGINT)::VARCHAR
    LEFT JOIN tracking
        ON line.invoice_id = tracking.invoice_id
       AND line.line_item_id = tracking.line_item_id
)
SELECT * FROM enriched
''')

write('intermediate','int_xero__general_ledger_fact', '''
WITH tracking AS (
    SELECT *
    FROM intermediate.int_xero__journal_line_pivoted_tracking_categories
),
base AS (
    SELECT
        journal.journal_id,
        line.journal_line_id,
        journal.created_date_utc::VARCHAR AS created_date_utc,
        journal.journal_date::VARCHAR AS journal_date,
        journal.journal_number::INTEGER AS journal_number,
        journal.reference,
        journal.source_id,
        journal.source_type,
        line.account_code::DOUBLE AS account_code,
        line.account_id,
        line.account_name,
        line.account_type,
        account.account_class,
        line.description,
        line.gross_amount::DOUBLE AS gross_amount,
        line.net_amount::DOUBLE AS net_amount,
        line.tax_amount::DOUBLE AS tax_amount,
        line.tax_name,
        line.tax_type,
        CASE WHEN journal.source_type IN ('ACCPAY', 'ACCREC') THEN invoice.contact_id END AS contact_id,
        CASE WHEN journal.source_type IN ('ACCPAY', 'ACCREC') THEN contact.contact_name END AS contact_name,
        tracking.region,
        tracking.department,
        tracking.project,
        tracking.location,
        tracking.class,
        tracking.customer,
        tracking.cost_center
    FROM staging.stg_xero__journal AS journal
    INNER JOIN staging.stg_xero__journal_line AS line
        ON journal.journal_id = line.journal_id
    LEFT JOIN staging.stg_xero__account AS account
        ON line.account_id = account.account_id
    LEFT JOIN staging.stg_xero__invoice AS invoice
        ON journal.source_type IN ('ACCPAY', 'ACCREC')
       AND journal.source_id = invoice.invoice_id
    LEFT JOIN staging.stg_xero__contact AS contact
        ON invoice.contact_id = contact.contact_id
    LEFT JOIN tracking
        ON line.journal_id = tracking.journal_id
       AND line.journal_line_id = tracking.journal_line_id
    WHERE journal.journal_id IS NOT NULL
      AND line.journal_line_id IS NOT NULL
)
SELECT
    *,
    current_timestamp AS processed_at
FROM base
''')
PY
python /tmp/models.py
```
```json
{
  "event_id": 22,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/22.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 16816,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/22.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text

```

### event 23

```json
{
  "event_id": 23,
  "agent_command_sequence": 10,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/23.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 24003,
    "decoded_characters": 10861
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/23.json",
  "timestamp": "2026-10-25T05:49:41.543044",
  "target_table_name_hits": [
    "int_xero__invoice_line_items_enriched"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 10864,
  "retention": "full_original"
}
```
```bash
cat >> /tmp/models.py <<'PY'

write('marts','xero__invoice_line_items', '''
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
''')

write('marts','xero__general_ledger', '''
SELECT
    pj.journal_id,
    pj.journal_line_id,
    pj.created_date_utc,
    pj.journal_date,
    pj.journal_number,
    pj.reference,
    pj.source_id,
    pj.source_type,
    pj.account_code,
    pj.account_id,
    pj.account_name,
    pj.account_type,
    pj.account_class,
    pj.description,
    pj.gross_amount,
    pj.net_amount,
    pj.tax_amount,
    pj.tax_name,
    pj.tax_type,
    CASE WHEN pj.source_type IN ('ACCPAY', 'ACCREC') THEN pj.source_id END AS invoice_id,
    CASE WHEN pj.source_type IN ('CASHREC', 'CASHPAID') THEN pj.source_id END AS bank_transaction_id,
    CASE WHEN pj.source_type = 'MANJOURNAL' THEN pj.source_id END AS manual_journal_id,
    pj.contact_id,
    pj.contact_name,
    pj.region,
    pj.department,
    pj.project,
    pj.location,
    pj.class,
    pj.customer,
    pj.cost_center,
    current_timestamp AS report_generated_at
FROM intermediate.int_xero__general_ledger_fact AS pj
WHERE pj.journal_id IS NOT NULL
  AND pj.journal_line_id IS NOT NULL
ORDER BY pj.journal_date DESC, pj.journal_id ASC, pj.journal_line_id ASC
''')

write('marts','xero__balance_sheet_report', '''
WITH ledger AS (
    SELECT
        TRY_CAST(journal_date AS DATE) AS journal_date,
        account_code,
        account_name,
        account_type,
        account_class,
        net_amount,
        region,
        department,
        project
    FROM intermediate.int_xero__general_ledger_fact
    WHERE journal_date IS NOT NULL
),
calendar AS (
    SELECT unnest(generate_series(min(journal_date), max(journal_date), INTERVAL 1 DAY))::DATE AS report_date
    FROM ledger
),
account_dimensions AS (
    SELECT DISTINCT
        account_code,
        account_name,
        account_type,
        account_class,
        region,
        department,
        project,
        min(journal_date) AS first_activity_date
    FROM ledger
    GROUP BY account_code, account_name, account_type, account_class, region, department, project
),
running_balances AS (
    SELECT
        calendar.report_date,
        dimensions.account_code,
        dimensions.account_name,
        dimensions.account_type,
        dimensions.account_class,
        dimensions.region,
        dimensions.department,
        dimensions.project,
        sum(ledger.net_amount) AS running_balance
    FROM calendar
    INNER JOIN account_dimensions AS dimensions
        ON calendar.report_date >= dimensions.first_activity_date
    INNER JOIN ledger
        ON ledger.journal_date <= calendar.report_date
       AND ledger.account_code IS NOT DISTINCT FROM dimensions.account_code
       AND ledger.account_name IS NOT DISTINCT FROM dimensions.account_name
       AND ledger.account_type IS NOT DISTINCT FROM dimensions.account_type
       AND ledger.account_class IS NOT DISTINCT FROM dimensions.account_class
       AND ledger.region IS NOT DISTINCT FROM dimensions.region
       AND ledger.department IS NOT DISTINCT FROM dimensions.department
       AND ledger.project IS NOT DISTINCT FROM dimensions.project
    GROUP BY
        calendar.report_date,
        dimensions.account_code,
        dimensions.account_name,
        dimensions.account_type,
        dimensions.account_class,
        dimensions.region,
        dimensions.department,
        dimensions.project
),
classified AS (
    SELECT
        report_date,
        CASE
            WHEN account_class = 'ASSET' THEN 'Assets'
            WHEN account_class = 'LIABILITY' THEN 'Liabilities'
            WHEN account_class IN ('EQUITY', 'REVENUE', 'EXPENSE') THEN 'Equity'
            ELSE 'Other'
        END AS balance_sheet_category,
        CASE
            WHEN account_class = 'ASSET' AND account_type IN ('BANK', 'CURRENT') THEN 'Current Assets'
            WHEN account_class = 'ASSET' AND account_type = 'FIXED' THEN 'Fixed Assets'
            WHEN account_class = 'LIABILITY' AND account_type IN ('CURRLIAB', 'TERMLIAB') THEN 'Liabilities'
            WHEN account_class = 'EQUITY' THEN 'Equity'
            ELSE 'Other'
        END AS balance_sheet_subcategory,
        account_code,
        account_name,
        running_balance AS amount,
        region,
        department,
        project
    FROM running_balances
    WHERE running_balance IS NOT NULL
      AND running_balance <> 0
),
with_totals AS (
    SELECT
        *,
        sum(amount) OVER (PARTITION BY report_date, balance_sheet_category) AS category_total,
        sum(amount) OVER (PARTITION BY report_date, balance_sheet_subcategory) AS subcategory_total
    FROM classified
)
SELECT
    report_date,
    balance_sheet_category,
    balance_sheet_subcategory,
    account_code,
    account_name,
    amount,
    region,
    department,
    project,
    category_total,
    subcategory_total,
    current_timestamp AS report_generated_at
FROM with_totals
ORDER BY report_date DESC, balance_sheet_category, balance_sheet_subcategory, account_code
''')

write('marts','xero__profit_and_loss_report', '''
WITH journal_lines AS (
    SELECT
        TRY_CAST(journal_date AS DATE) AS journal_date,
        account_class,
        account_type,
        account_code,
        account_name,
        net_amount,
        region,
        department,
        project,
        CASE WHEN account_class = 'REVENUE' THEN net_amount ELSE 0 END AS revenue_amount,
        CASE WHEN account_class = 'EXPENSE' THEN abs(net_amount) ELSE 0 END AS expense_amount,
        CASE
            WHEN account_class = 'REVENUE' THEN 'Revenue'
            WHEN account_class = 'EXPENSE' THEN 'Expenses'
            WHEN account_class IN ('ASSET', 'LIABILITY', 'EQUITY') THEN 'Balance Sheet'
            ELSE 'Other'
        END AS pl_category,
        CASE
            WHEN account_type = 'REVENUE' THEN 'Operating Revenue'
            WHEN account_type = 'EXPENSE' AND starts_with(CAST(account_code AS VARCHAR), '4') THEN 'Operating Expenses'
            WHEN account_type = 'EXPENSE' AND starts_with(CAST(account_code AS VARCHAR), '6') THEN 'Administrative Expenses'
            WHEN account_type = 'DIRECTCOSTS' THEN 'Cost of Goods Sold'
            WHEN account_type = 'OVERHEADS' THEN 'Overhead'
            WHEN account_type = 'DEPRECIATN' THEN 'Depreciation'
            ELSE 'Other'
        END AS pl_subcategory
    FROM intermediate.int_xero__general_ledger_fact
    WHERE journal_date IS NOT NULL
),
monthly AS (
    SELECT
        date_trunc('month', journal_date)::DATE AS report_month,
        year(journal_date)::INTEGER AS fiscal_year,
        month(journal_date)::INTEGER AS fiscal_month,
        quarter(journal_date)::INTEGER AS fiscal_quarter,
        account_code,
        account_name,
        pl_category,
        pl_subcategory,
        region,
        department,
        project,
        sum(revenue_amount)::DOUBLE AS revenue,
        sum(expense_amount)::DOUBLE AS expenses,
        sum(net_amount)::DOUBLE AS net_amount
    FROM journal_lines
    GROUP BY
        report_month, fiscal_year, fiscal_month, fiscal_quarter,
        account_code, account_name, pl_category, pl_subcategory,
        region, department, project
),
filtered AS (
    SELECT *
    FROM monthly
    WHERE revenue <> 0 OR expenses <> 0
),
with_cumulative AS (
    SELECT
        *,
        sum(net_amount) OVER (
            PARTITION BY report_month
            ORDER BY pl_category ASC, account_code ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_net
    FROM filtered
)
SELECT
    report_month,
    fiscal_year,
    fiscal_month,
    'Monthly' AS period_type,
    pl_category,
    pl_subcategory,
    account_code,
    account_name,
    revenue,
    expenses,
    net_amount,
    cumulative_net,
    region,
    department,
    project,
    current_timestamp AS report_generated_at
FROM with_cumulative
ORDER BY
    report_month DESC,
    CASE pl_category WHEN 'Revenue' THEN 1 WHEN 'Expenses' THEN 2 ELSE 3 END,
    account_code ASC
''')
PY
python /tmp/models.py
find sql -type f | sort | wc -l
```
```json
{
  "event_id": 24,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/24.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 23687,
    "decoded_characters": 3
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/24.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
23
```

### event 25

```json
{
  "event_id": 25,
  "agent_command_sequence": 11,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/25.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1416,
    "decoded_characters": 82
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/25.json",
  "timestamp": "2026-10-25T05:49:46.136114",
  "target_table_name_hits": [
    "int_xero__invoice_line_items_enriched"
  ],
  "source_table_name_hits": [
    "intermediate.int_xero__invoice_line_item_pivoted_tracking_categories",
    "int_xero__invoice_line_item_pivoted_tracking_categories",
    "staging.stg_xero__invoice_line_item",
    "stg_xero__invoice_line_item",
    "staging.stg_xero__account",
    "staging.stg_xero__contact",
    "staging.stg_xero__invoice",
    "stg_xero__account",
    "stg_xero__contact",
    "stg_xero__invoice"
  ],
  "full_original_characters": 7535,
  "retention": "full_original"
}
```
```bash
python run.py > /tmp/run.log 2>&1; status=$?; tail -100 /tmp/run.log; exit $status
```
```json
{
  "event_id": 26,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/26.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1100,
    "decoded_characters": 7453
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/26.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
2026-10-25 05:51:18,581 - INFO - ✓ staging.stg_xero__journal: 3,500 rows
2026-10-25 05:51:18,583 - INFO - Executing: staging.stg_xero__journal_line
2026-10-25 05:51:18,597 - INFO - ✓ staging.stg_xero__journal_line: 8,000 rows
2026-10-25 05:51:18,599 - INFO - Executing: staging.stg_xero__journal_line_has_tracking_category
2026-10-25 05:51:18,604 - INFO - ✓ staging.stg_xero__journal_line_has_tracking_category: 200 rows
2026-10-25 05:51:18,605 - INFO - Executing: staging.stg_xero__organization
2026-10-25 05:51:18,610 - INFO - ✓ staging.stg_xero__organization: 5 rows
2026-10-25 05:51:18,611 - INFO - Executing: staging.stg_xero__tracking_category
2026-10-25 05:51:18,615 - INFO - ✓ staging.stg_xero__tracking_category: 22 rows
2026-10-25 05:51:18,616 - INFO - Executing: staging.stg_xero__tracking_category_has_option
2026-10-25 05:51:18,621 - INFO - ✓ staging.stg_xero__tracking_category_has_option: 150 rows
2026-10-25 05:51:18,622 - INFO - Executing: staging.stg_xero__tracking_category_option
2026-10-25 05:51:18,626 - INFO - ✓ staging.stg_xero__tracking_category_option: 135 rows
2026-10-25 05:51:18,626 - INFO - STAGING layer complete: 14/14 tables created successfully
2026-10-25 05:51:18,626 - INFO - 
=== Executing INTERMEDIATE Layer ===
2026-10-25 05:51:18,626 - INFO - Description: Business logic and data integration with pivoted tracking categories and facts
2026-10-25 05:51:18,628 - INFO - Executing: intermediate.int_xero__tracking_categories_with_options
2026-10-25 05:51:18,635 - INFO - ✓ intermediate.int_xero__tracking_categories_with_options: 142 rows
2026-10-25 05:51:18,639 - INFO - Executing: intermediate.int_xero__invoice_line_item_pivoted_tracking_categories
2026-10-25 05:51:18,650 - INFO - ✓ intermediate.int_xero__invoice_line_item_pivoted_tracking_categories: 7 rows
2026-10-25 05:51:18,654 - INFO - Executing: intermediate.int_xero__journal_line_pivoted_tracking_categories
2026-10-25 05:51:18,668 - INFO - ✓ intermediate.int_xero__journal_line_pivoted_tracking_categories: 13 rows
2026-10-25 05:51:18,672 - INFO - Executing: intermediate.int_xero__general_ledger_fact
2026-10-25 05:51:19,088 - INFO - ✓ intermediate.int_xero__general_ledger_fact: 8,000 rows
2026-10-25 05:51:19,092 - INFO - Executing: intermediate.int_xero__invoice_line_items_enriched
2026-10-25 05:51:19,118 - INFO - ✓ intermediate.int_xero__invoice_line_items_enriched: 5,209 rows
2026-10-25 05:51:19,118 - INFO - INTERMEDIATE layer complete: 5/5 tables created successfully
2026-10-25 05:51:19,118 - INFO - 
=== Executing MARTS Layer ===
2026-10-25 05:51:19,118 - INFO - Description: Analysis-ready business entities and reports
2026-10-25 05:51:19,120 - INFO - Executing: marts.xero__general_ledger
2026-10-25 05:51:19,164 - INFO - ✓ marts.xero__general_ledger: 8,000 rows
2026-10-25 05:51:19,170 - INFO - Executing: marts.xero__balance_sheet_report
2026-10-25 05:51:20,879 - INFO - ✓ marts.xero__balance_sheet_report: 955,643 rows
2026-10-25 05:51:20,886 - INFO - Executing: marts.xero__profit_and_loss_report
2026-10-25 05:51:20,915 - INFO - ✓ marts.xero__profit_and_loss_report: 1,657 rows
2026-10-25 05:51:20,921 - INFO - Executing: marts.xero__invoice_line_items
2026-10-25 05:51:20,959 - INFO - ✓ marts.xero__invoice_line_items: 5,209 rows
2026-10-25 05:51:20,959 - INFO - MARTS layer complete: 4/4 tables created successfully
2026-10-25 05:51:20,959 - INFO - 
🎉 Xero data pipeline executed successfully!
2026-10-25 05:51:20,959 - INFO - ✨ Complete accounting data warehouse has been generated: xero.duckdb
2026-10-25 05:51:20,959 - INFO - 
=== Xero Data Warehouse Final Statistics (by Schema Layer) ===
2026-10-25 05:51:20,964 - INFO - 
RAW Layer (Schema: raw):
2026-10-25 05:51:20,965 - INFO -   ✓ raw.xero_account_data: 500 rows
2026-10-25 05:51:20,966 - INFO -   ✓ raw.xero_bank_transaction_data: 800 rows
2026-10-25 05:51:20,967 - INFO -   ✓ raw.xero_contact_data: 3,000 rows
2026-10-25 05:51:20,968 - INFO -   ✓ raw.xero_credit_note_data: 50 rows
2026-10-25 05:51:20,968 - INFO -   ✓ raw.xero_invoice_data: 3,500 rows
2026-10-25 05:51:20,969 - INFO -   ✓ raw.xero_invoice_line_item_data: 5,000 rows
2026-10-25 05:51:20,970 - INFO -   ✓ raw.xero_invoice_line_item_has_tracking_category_data: 100 rows
2026-10-25 05:51:20,971 - INFO -   ✓ raw.xero_journal_data: 3,500 rows
2026-10-25 05:51:20,972 - INFO -   ✓ raw.xero_journal_line_data: 8,000 rows
2026-10-25 05:51:20,972 - INFO -   ✓ raw.xero_journal_line_has_tracking_category_data: 200 rows
2026-10-25 05:51:20,973 - INFO -   ✓ raw.xero_organization_data: 5 rows
2026-10-25 05:51:20,974 - INFO -   ✓ raw.xero_tracking_category_data: 22 rows
2026-10-25 05:51:20,975 - INFO -   ✓ raw.xero_tracking_category_has_option_data: 150 rows
2026-10-25 05:51:20,976 - INFO -   ✓ raw.xero_tracking_category_option_data: 135 rows
2026-10-25 05:51:20,978 - INFO - 
STAGING Layer (Schema: staging):
2026-10-25 05:51:20,979 - INFO -   ✓ staging.stg_xero__account: 500 rows
2026-10-25 05:51:20,979 - INFO -   ✓ staging.stg_xero__bank_transaction: 800 rows
2026-10-25 05:51:20,980 - INFO -   ✓ staging.stg_xero__contact: 3,000 rows
2026-10-25 05:51:20,981 - INFO -   ✓ staging.stg_xero__credit_note: 50 rows
2026-10-25 05:51:20,982 - INFO -   ✓ staging.stg_xero__invoice: 3,489 rows
2026-10-25 05:51:20,983 - INFO -   ✓ staging.stg_xero__invoice_line_item: 5,000 rows
2026-10-25 05:51:20,984 - INFO -   ✓ staging.stg_xero__invoice_line_item_has_tracking_category: 100 rows
2026-10-25 05:51:20,984 - INFO -   ✓ staging.stg_xero__journal: 3,500 rows
2026-10-25 05:51:20,985 - INFO -   ✓ staging.stg_xero__journal_line: 8,000 rows
2026-10-25 05:51:20,986 - INFO -   ✓ staging.stg_xero__journal_line_has_tracking_category: 200 rows
2026-10-25 05:51:20,986 - INFO -   ✓ staging.stg_xero__organization: 5 rows
2026-10-25 05:51:20,987 - INFO -   ✓ staging.stg_xero__tracking_category: 22 rows
2026-10-25 05:51:20,988 - INFO -   ✓ staging.stg_xero__tracking_category_has_option: 150 rows
2026-10-25 05:51:20,988 - INFO -   ✓ staging.stg_xero__tracking_category_option: 135 rows
2026-10-25 05:51:20,991 - INFO - 
INTERMEDIATE Layer (Schema: intermediate):
2026-10-25 05:51:20,991 - INFO -   ✓ intermediate.int_xero__general_ledger_fact: 8,000 rows
2026-10-25 05:51:20,992 - INFO -   ✓ intermediate.int_xero__invoice_line_item_pivoted_tracking_categories: 7 rows
2026-10-25 05:51:20,993 - INFO -   ✓ intermediate.int_xero__invoice_line_items_enriched: 5,209 rows
2026-10-25 05:51:20,993 - INFO -   ✓ intermediate.int_xero__journal_line_pivoted_tracking_categories: 13 rows
2026-10-25 05:51:20,994 - INFO -   ✓ intermediate.int_xero__tracking_categories_with_options: 142 rows
2026-10-25 05:51:20,996 - INFO - 
MARTS Layer (Schema: marts):
2026-10-25 05:51:20,997 - INFO -   ✓ marts.xero__balance_sheet_report: 955,643 rows
2026-10-25 05:51:20,998 - INFO -   ✓ marts.xero__general_ledger: 8,000 rows
2026-10-25 05:51:20,999 - INFO -   ✓ marts.xero__invoice_line_items: 5,209 rows
2026-10-25 05:51:21,000 - INFO -   ✓ marts.xero__profit_and_loss_report: 1,657 rows

✅ Xero data transformation completed successfully!
📋 Transformation Results:
  📥 Source Database: xero_start.duckdb (raw tables only)
  📤 Target Database: xero.duckdb (complete layered architecture)

🏗️ Data Architecture:
  📊 Staging Layer - Standardized raw data (data cleaning and validation)
  🔄 Intermediate Layer - Business logic processing (tracking category roll-ups)
  🎯 Marts Layer - Analysis-ready data (financial reports and details)
```

### event 27

```json
{
  "event_id": 27,
  "agent_command_sequence": 12,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/27.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2384,
    "decoded_characters": 552
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/27.json",
  "timestamp": "2026-10-25T05:51:31.624707",
  "target_table_name_hits": [
    "int_xero__invoice_line_items_enriched"
  ],
  "source_table_name_hits": [
    "staging.stg_xero__invoice_line_item",
    "stg_xero__invoice_line_item",
    "staging.stg_xero__account",
    "stg_xero__account"
  ],
  "full_original_characters": 1625,
  "retention": "full_original"
}
```
```bash
python - <<'PY'
import duckdb
c=duckdb.connect('xero.duckdb',read_only=True)
for q in ["select count(*),count(distinct line_item_id) from intermediate.int_xero__invoice_line_items_enriched", "select line_item_id,count(*) n from intermediate.int_xero__invoice_line_items_enriched group by 1 having count(*)>1 order by n desc limit 10", "select account_code,count(*) n from staging.stg_xero__account group by 1 having count(*)>1 order by n desc limit 15", "select count(*) from staging.stg_xero__invoice_line_item"]:
 print(q, c.execute(q).fetchall())
PY
```
```json
{
  "event_id": 28,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/28.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2068,
    "decoded_characters": 1073
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/28.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
select count(*),count(distinct line_item_id) from intermediate.int_xero__invoice_line_items_enriched [(5209, 5000)]
select line_item_id,count(*) n from intermediate.int_xero__invoice_line_items_enriched group by 1 having count(*)>1 order by n desc limit 10 [('77f00e74-13fc-49d4-a9a1-33aacacbf93e', 2), ('a7a17e96-1fce-486e-bdd5-9c7eedf2bb29', 2), ('589801d4-5287-4e9b-93e3-cdf2823148a4', 2), ('d3aff52a-406e-4d33-a2e7-154106660b93', 2), ('024cd473-0ae5-4417-b911-26f4435565c7', 2), ('bb96f7f9-530c-44b4-8776-9f74b115f9b9', 2), ('ecec2012-0d8f-4b82-82c4-c1df552e123d', 2), ('40d95410-9ebd-40b1-9238-1f625546bab9', 2), ('f3357a6e-b1ae-4a91-8eb7-995ee35dd227', 2), ('eef5a152-30ef-4a0d-9cee-476f6fe79b9f', 2)]
select account_code,count(*) n from staging.stg_xero__account group by 1 having count(*)>1 order by n desc limit 15 [('610', 2), ('498', 2), ('7551', 2), ('433', 2), ('200', 2), ('314', 2), ('640', 2), ('820', 2), ('410', 2), ('676', 2), ('475', 2), ('372', 2), ('802', 2), ('711', 2), ('193', 2)]
select count(*) from staging.stg_xero__invoice_line_item [(5000,)]
```

### event 29

```json
{
  "event_id": 29,
  "agent_command_sequence": 13,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/29.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 3289,
    "decoded_characters": 981
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/29.json",
  "timestamp": "2026-10-25T05:51:40.120769",
  "target_table_name_hits": [
    "int_xero__invoice_line_items_enriched"
  ],
  "source_table_name_hits": [
    "intermediate.int_xero__invoice_line_item_pivoted_tracking_categories",
    "int_xero__invoice_line_item_pivoted_tracking_categories",
    "staging.stg_xero__account",
    "stg_xero__account"
  ],
  "full_original_characters": 1451,
  "retention": "full_original"
}
```
```bash
python - <<'PY'
p='sql/intermediate/int_xero__invoice_line_items_enriched.sql'
s=open(p).read()
s=s.replace('WITH tracking AS (\n    SELECT *\n    FROM intermediate.int_xero__invoice_line_item_pivoted_tracking_categories\n),','''WITH tracking AS (
    SELECT *
    FROM intermediate.int_xero__invoice_line_item_pivoted_tracking_categories
),
account_by_code AS (
    SELECT account_code, account_name, account_type, account_class
    FROM staging.stg_xero__account
    QUALIFY row_number() OVER (PARTITION BY account_code ORDER BY account_id) = 1
),''')
s=s.replace('LEFT JOIN staging.stg_xero__account AS account\n        ON line.account_code = TRY_CAST(account.account_code AS BIGINT)::VARCHAR','LEFT JOIN account_by_code AS account\n        ON line.account_code::VARCHAR = account.account_code')
open(p,'w').write(s)
PY
python run.py > /tmp/run2.log 2>&1; status=$?; grep -E 'ERROR|✗|layer complete|int_xero__invoice_line_items_enriched:|MARTS layer' /tmp/run2.log; exit $status
```
```json
{
  "event_id": 30,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/30.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2973,
    "decoded_characters": 470
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/30.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
2026-10-25 05:51:40,448 - INFO - STAGING layer complete: 14/14 tables created successfully
2026-10-25 05:51:40,662 - INFO - ✓ intermediate.int_xero__invoice_line_items_enriched: 5,000 rows
2026-10-25 05:51:40,662 - INFO - INTERMEDIATE layer complete: 5/5 tables created successfully
2026-10-25 05:51:42,265 - INFO - MARTS layer complete: 4/4 tables created successfully
2026-10-25 05:51:42,355 - INFO -   ✓ intermediate.int_xero__invoice_line_items_enriched: 5,000 rows
```

### event 31

```json
{
  "event_id": 31,
  "agent_command_sequence": 14,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/31.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 4509,
    "decoded_characters": 1587
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/31.json",
  "timestamp": "2026-10-25T05:51:52.397440",
  "target_table_name_hits": [
    "int_xero__invoice_line_items_enriched"
  ],
  "source_table_name_hits": [
    "staging.stg_xero__invoice_line_item",
    "stg_xero__invoice_line_item",
    "staging.stg_xero__invoice",
    "stg_xero__invoice"
  ],
  "full_original_characters": 1801,
  "retention": "full_original"
}
```
```bash
python - <<'PY'
import duckdb
c=duckdb.connect('xero.duckdb',read_only=True)
checks={
 'invoice_item_enriched_pk':"select count(*) total, count(distinct line_item_id) distinct_ids, count(*) filter(where line_item_id is null or invoice_id is null) bad_ids from intermediate.int_xero__invoice_line_items_enriched",
 'mart_invoice_pk':"select count(*) total, count(distinct line_item_id) distinct_ids, count(*) filter(where line_item_id is null or invoice_id is null) bad_ids from marts.xero__invoice_line_items",
 'ledger_key':"select count(*) total, count(distinct journal_id || '|' || journal_line_id) distinct_keys, count(*) filter(where journal_id is null or journal_line_id is null) bad_ids from intermediate.int_xero__general_ledger_fact",
 'tracking_enum':"select count(*) filter(where status='UNKNOWN') unknown_status, count(*) total from staging.stg_xero__tracking_category",
 'invoice date':"select count(*) filter(where invoice_date is null or invoice_date > current_date + interval '1 year') bad_dates, count(*) total from staging.stg_xero__invoice",
 'line amount domain':"select count(*) filter(where unit_amount is null or abs(unit_amount)>1000000) invalid from staging.stg_xero__invoice_line_item",
 'totals':"select count(*) filter(where invoice_gross_nonneg < 0 or invoice_net_nonneg < 0 or line_share_gross > 1.000001) invalid from marts.xero__invoice_line_items"
}
for n,q in checks.items(): print(n,c.execute(q).fetchall())
print('SQL semicolons:', [(str(p), ';' in p.read_text()) for p in __import__('pathlib').Path('sql').rglob('*.sql') if ';' in p.read_text()])
PY
```
```json
{
  "event_id": 32,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/32.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 4192,
    "decoded_characters": 214
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/32.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
invoice_item_enriched_pk [(5000, 5000, 0)]
mart_invoice_pk [(5000, 5000, 0)]
ledger_key [(8000, 8000, 0)]
tracking_enum [(2, 22)]
invoice date [(0, 3489)]
line amount domain [(0,)]
totals [(0,)]
SQL semicolons: []
```

## result_md_table_sentences

```json
{
  "present": true,
  "path": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/result.md",
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/result.md",
  "sha256": "6b0b5b5bf62fc536497b62d1112ff46ca4ff4999341d49d765f3a340cee40491",
  "sentences": [],
  "policy": "All sentences naming the table; includes sentences without 008 keywords. Existing D10 ids attached where applicable."
}
```

## original_files

```json
{
  "paths": [
    "/home/katherine/Assumption_Ledger/data/005_cs_work/impl-027_parallel/node_results.duckdb",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/10.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/19.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/20.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/21.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/22.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/23.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/24.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/25.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/26.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/27.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/28.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/29.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/30.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/31.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/32.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/7.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/8.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/9.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/result.md",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb",
    "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml",
    "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql"
  ],
  "archive": "/home/katherine/Assumption_Ledger/traces/dacomp_deimpl_prev.tar.gz",
  "gold_SQL_search_root": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql",
  "gold_SQL_search_names": [
    "int_xero__invoice_line_items_enriched",
    "int_xero__invoice_line_items_enriched"
  ],
  "source_fingerprints": "records/012_input_before.json"
}
```
