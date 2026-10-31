# DAComp / impl-027_int_xero__invoice_line_items_enriched（v3）

## 错在哪里
agent为满足line_item_id唯一性对重复account_code取一行，gold保留一对多连接，额外产生209行。

证据复用入口：[018_impl-027_int_xero__invoice_line_items_enriched.md](../018_annotations/018_impl-027_int_xero__invoice_line_items_enriched.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## account_keep_duplicates
- 角色：主要；类别：**其他**；把握：中。
- 依据：契约每line_item_id唯一，agent去重符合要求，gold多209行；去重已具体披露。
- 是否说出：针对本处的具体说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 41 / args.final_thought：
```text
Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.
```

## 规模、证据复用与新做
主要原因：其他。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-027_int_xero__invoice_line_items_enriched.md](../018_annotations/018_impl-027_int_xero__invoice_line_items_enriched.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: int_xero__invoice_line_items_enriched
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

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-027_int_xero__invoice_line_items_enriched.md:29)
- [SQL定位](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-027_int_xero__invoice_line_items_enriched.md:147)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-027_int_xero__invoice_line_items_enriched.md:577)
- [重跑 account_keep_duplicates](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-027_int_xero__invoice_line_items_enriched.md:618)
