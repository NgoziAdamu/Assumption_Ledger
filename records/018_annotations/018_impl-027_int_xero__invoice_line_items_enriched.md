# impl-027 / int_xero__invoice_line_items_enriched（v2定稿）

## 1. 差异描述与判定

agent为满足line_item_id唯一性对重复account_code取一行，gold保留一对多连接，额外产生209行。

已核实：契约grain及line_item_id tests明确每id恰好1行。CS下agent5000行、gold5209行，209个line_item多出1行；移除account_by_code的QUALIFY就L0匹配，说明差异仅来自该去重。agent并非假定account_code唯一：event27→28已查出重复及5209/5000规模，event29才新增按最低account_id选1行。gold重复输出与契约唯一要求矛盾，归O；agent选择哪组账户属性仍有未规定部分，但本次删除去重的完整对照足以定位判错差异。

主要原因：**O**；把握：**高**。
参与因素：无。标记：无。

与上一版（017）相比：原因类别及参与因素不变。不确定性由017的“已提到”改按四档逐项记录：account_keep_duplicates=针对本表的具体说明。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../017_annotations/017_impl-027_int_xero__invoice_line_items_enriched.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自017，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-027_intermediate_int_xero__invoice_line_items_enriched.md)；不修改既有官方判错状态。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml` 第430–542行。
- [完整轨迹](../017_trace_impl-027.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。
- [查询原文及结果](../017_queries_impl-027.json)、[重跑完整记录](../017_reruns_impl-027.json)、[原始表库存](../015_raw_impl-027.json)。
- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。
- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。

### 契约原文

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

### SQL定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: WITH tracking AS (
   2:     SELECT *
   3:     FROM intermediate.int_xero__invoice_line_item_pivoted_tracking_categories
   4: ),
   5: account_by_code AS (
   6:     SELECT account_code, account_name, account_type, account_class
   7:     FROM staging.stg_xero__account
   8:     QUALIFY row_number() OVER (PARTITION BY account_code ORDER BY account_id) = 1
   9: ),
  10: line_items AS (
  11:     SELECT
  12:         line_item_id,
  13:         invoice_id,
  14:         account_code,
  15:         description,
  16:         quantity,
  17:         unit_amount,
  18:         line_amount,
  19:         tax_amount,
  20:         tax_type,
  21:         discount_rate,
  22:         processed_at
  23:     FROM staging.stg_xero__invoice_line_item
  24:     WHERE line_item_id IS NOT NULL
  25:       AND invoice_id IS NOT NULL
  26: ),
  27: enriched AS (
  28:     SELECT
  29:         line.line_item_id,
  30:         line.invoice_id,
  31:         TRY_CAST(line.account_code AS BIGINT) AS account_code,
  32:         account.account_name,
  33:         account.account_type,
  34:         account.account_class,
  35:         line.description,
  36:         line.quantity::DOUBLE AS quantity,
  37:         line.unit_amount::DOUBLE AS unit_amount,
  38:         line.line_amount::DOUBLE AS line_amount,
  39:         line.tax_amount::DOUBLE AS tax_amount,
  40:         CASE
  41:             WHEN line.tax_amount IS NULL OR line.line_amount IS NULL
  42:               OR line.line_amount - line.tax_amount = 0 THEN NULL
  43:             ELSE round(line.tax_amount / (line.line_amount - line.tax_amount) * 100, 2)::DOUBLE
  44:         END AS effective_tax_rate,
  45:         line.tax_type,
  46:         line.discount_rate::DOUBLE AS discount_rate,
  47:         invoice.contact_id,
  48:         contact.contact_name,
  49:         tracking.region,
  50:         tracking.department,
  51:         tracking.project,
  52:         tracking.location,
  53:         tracking.class,
  54:         tracking.customer,
  55:         tracking.cost_center,
  56:         line.processed_at::TIMESTAMPTZ AS processed_at
  57:     FROM line_items AS line
  58:     LEFT JOIN staging.stg_xero__invoice AS invoice
  59:         ON line.invoice_id = invoice.invoice_id
  60:     LEFT JOIN staging.stg_xero__contact AS contact
  61:         ON invoice.contact_id = contact.contact_id
  62:     LEFT JOIN account_by_code AS account
  63:         ON line.account_code::VARCHAR = account.account_code
  64:     LEFT JOIN tracking
  65:         ON line.invoice_id = tracking.invoice_id
  66:        AND line.line_item_id = tracking.line_item_id
  67: )
  68: SELECT * FROM enriched
```

gold（仅用于定位差异）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: -- Intermediate fact: Invoice Line Items Enriched (staging -> intermediate only)
   2:
   3: WITH invoice_line_items AS (
   4:     SELECT
   5:         line_item_id,
   6:         invoice_id,
   7:         account_code,
   8:         description,
   9:         quantity,
  10:         unit_amount,
  11:         line_amount,
  12:         tax_amount,
  13:         tax_type,
  14:         discount_rate,
  15:         processed_at
  16:     FROM staging.stg_xero__invoice_line_item
  17: ),
  18:
  19: invoices AS (
  20:     SELECT
  21:         invoice_id,
  22:         contact_id
  23:     FROM staging.stg_xero__invoice
  24: ),
  25:
  26: accounts AS (
  27:     SELECT
  28:         account_code,
  29:         account_name,
  30:         account_type,
  31:         account_class
  32:     FROM staging.stg_xero__account
  33: ),
  34:
  35: contacts AS (
  36:     SELECT
  37:         contact_id,
  38:         contact_name
  39:     FROM staging.stg_xero__contact
  40: ),
  41:
  42: pivoted_invoice_tracking AS (
  43:     -- Build pivot locally from staging to avoid same-layer dependency
  44:     WITH invoice_tracking AS (
  45:         SELECT invoice_id, line_item_id, tracking_option, tracking_category_id
  46:         FROM staging.stg_xero__invoice_line_item_has_tracking_category
  47:     ),
  48:     tracking_categories_with_options AS (
  49:         WITH tracking_categories AS (
  50:             SELECT tracking_category_id, tracking_category_name FROM staging.stg_xero__tracking_category
  51:         ),
  52:         tracking_options AS (
  53:             SELECT tracking_option_id, tracking_option_name, is_active FROM staging.stg_xero__tracking_category_option
  54:         ),
  55:         tracking_relationships AS (
  56:             SELECT tracking_category_id, tracking_option_id FROM staging.stg_xero__tracking_category_has_option
  57:         )
  58:         SELECT tc.tracking_category_id, tc.tracking_category_name, topt.tracking_option_name
  59:         FROM tracking_categories tc
  60:         JOIN tracking_relationships tr ON tc.tracking_category_id = tr.tracking_category_id
  61:         JOIN tracking_options topt ON tr.tracking_option_id = topt.tracking_option_id
  62:         WHERE topt.is_active = TRUE
  63:     ),
  64:     invoice_mapped AS (
  65:         SELECT it.invoice_id, it.line_item_id, tcwo.tracking_category_name, tcwo.tracking_option_name
  66:         FROM invoice_tracking it
  67:         JOIN tracking_categories_with_options tcwo
  68:           ON it.tracking_category_id = tcwo.tracking_category_id
  69:          AND it.tracking_option = tcwo.tracking_option_name
  70:     )
  71:     SELECT
  72:         invoice_id,
  73:         line_item_id,
  74:         MAX(CASE WHEN tracking_category_name = 'Region' THEN tracking_option_name END) AS region,
  75:         MAX(CASE WHEN tracking_category_name = 'Department' THEN tracking_option_name END) AS department,
  76:         MAX(CASE WHEN tracking_category_name = 'Project' THEN tracking_option_name END) AS project,
  77:         MAX(CASE WHEN tracking_category_name = 'Location' THEN tracking_option_name END) AS location,
  78:         MAX(CASE WHEN tracking_category_name = 'Class' THEN tracking_option_name END) AS class,
  79:         MAX(CASE WHEN tracking_category_name = 'Customer' THEN tracking_option_name END) AS customer,
  80:         MAX(CASE WHEN tracking_category_name LIKE '%Cost Center%' THEN tracking_option_name END) AS cost_center
  81:     FROM invoice_mapped
  82:     GROUP BY invoice_id, line_item_id
  83: )
  84:
  85: SELECT
  86:     -- Line item identity
  87:     ili.line_item_id,
  88:     ili.invoice_id,
  89:
  90:     -- Line item details
  91:     ili.account_code,
  92:     acc.account_name,
  93:     acc.account_type,
  94:     acc.account_class,
  95:     ili.description,
  96:     ili.quantity,
  97:     ili.unit_amount,
  98:     ili.line_amount,
  99:     ili.tax_amount,
 100:     ROUND(ili.tax_amount / NULLIF(ili.line_amount - ili.tax_amount, 0) * 100, 2) AS effective_tax_rate,
 101:     ili.tax_type,
 102:     ili.discount_rate,
 103:
 104:     -- Basic invoice and contact info
 105:     inv.contact_id,
 106:     con.contact_name,
 107:
 108:     -- Tracking dimensions (pivoted from categories)
 109:     pit.region,
 110:     pit.department,
 111:     pit.project,
 112:     pit.location,
 113:     pit.class,
 114:     pit.customer,
 115:     pit.cost_center,
 116:
 117:     -- Processing metadata
 118:     ili.processed_at
 119: FROM invoice_line_items ili
 120: LEFT JOIN invoices inv
 121:     ON ili.invoice_id = inv.invoice_id
 122: LEFT JOIN accounts acc
 123:     ON CAST(ili.account_code AS VARCHAR) = acc.account_code
 124: LEFT JOIN contacts con
 125:     ON inv.contact_id = con.contact_id
 126: LEFT JOIN pivoted_invoice_tracking pit
 127:     ON ili.invoice_id = pit.invoice_id
 128:     AND ili.line_item_id = pit.line_item_id
 129: WHERE ili.line_item_id IS NOT NULL
 130:   AND ili.invoice_id IS NOT NULL
```

### 原始数据可评估性

下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。

|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|
|---|---|---|---|---|---|
|raw.xero_account_data|gold_vs_initial|True|True|True||
|raw.xero_contact_data|gold_vs_initial|True|True|True||
|raw.xero_invoice_data|gold_vs_initial|True|True|True||
|raw.xero_invoice_line_item_data|gold_vs_initial|True|True|True||
|raw.xero_invoice_line_item_has_tracking_category_data|gold_vs_initial|True|True|True||
|raw.xero_tracking_category_data|gold_vs_initial|True|True|True||
|raw.xero_tracking_category_has_option_data|gold_vs_initial|True|True|True||
|raw.xero_tracking_category_option_data|gold_vs_initial|True|True|True||
|raw.xero_account_data|gold_vs_agent|True|True|True||
|raw.xero_contact_data|gold_vs_agent|True|True|True||
|raw.xero_invoice_data|gold_vs_agent|True|True|True||
|raw.xero_invoice_line_item_data|gold_vs_agent|True|True|True||
|raw.xero_invoice_line_item_has_tracking_category_data|gold_vs_agent|True|True|True||
|raw.xero_tracking_category_data|gold_vs_agent|True|True|True||
|raw.xero_tracking_category_has_option_data|gold_vs_agent|True|True|True||
|raw.xero_tracking_category_option_data|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event27→28分别查输出重复、staging account_code重复及源line_item5000行；event29加入确定性去重；event31→32验证5000个唯一id。event41明确披露选择lowest account_id并会丢弃冲突账户属性。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|account_keep_duplicates|O|针对本表的具体说明|41|

### account_keep_duplicates：针对本表的具体说明

明确指出invoice enrichment重复account_code、确定性选行、原因和丢失属性的代价。

事件 **41**，字段`args.final_thought`；[轨迹原文](../017_trace_impl-027.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/41.json`。
```text
Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.
```

已检视43个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **2条**；018新增核实查询 **0条**。核实代价：多条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../017_reruns_impl-027.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用017的查询与重跑证据；其中“新增/本次”的执行归属仍为017，018没有重复执行。
核实查询执行 **2条**（失败尝试也计入）；核实代价档：**多条查询**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。

### V1 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb`。
```sql
SELECT account_code,count(*) n,count(distinct account_name) names FROM staging.stg_xero__account GROUP BY account_code HAVING count(*)>1 ORDER BY account_code
```
结果原文：
```json
{
  "executed_utc": "2026-10-29T11:33:05.786821+00:00",
  "error": "Parser Error: syntax error at or near \"names\"\n\nLINE 1: ...ELECT account_code,count(*) n,count(distinct account_name) names FROM staging.stg_xero__account GROUP BY account_code...\n                                                                      ^"
}
```

### V2 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb`。
```sql
SELECT account_code,count(*) n,count(distinct account_name) distinct_names FROM staging.stg_xero__account GROUP BY account_code HAVING count(*)>1 ORDER BY account_code
```
结果原文：
```json
{
  "columns": [
    "account_code",
    "n",
    "distinct_names"
  ],
  "rows": [
    [
      "193",
      2,
      2
    ],
    [
      "200",
      2,
      2
    ],
    [
      "310",
      2,
      2
    ],
    [
      "314",
      2,
      2
    ],
    [
      "372",
      2,
      2
    ],
    [
      "410",
      2,
      2
    ],
    [
      "433",
      2,
      2
    ],
    [
      "475",
      2,
      2
    ],
    [
      "498",
      2,
      2
    ],
    [
      "610",
      2,
      2
    ],
    [
      "640",
      2,
      2
    ],
    [
      "676",
      2,
      2
    ],
    [
      "711",
      2,
      2
    ],
    [
      "7551",
      2,
      2
    ],
    [
      "802",
      2,
      2
    ],
    [
      "820",
      2,
      2
    ],
    [
      "INVALIDACCTCODE",
      2,
      2
    ]
  ],
  "executed_utc": "2026-10-29T11:34:22.535399+00:00"
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['line_item_id']`；原评分比较列：`['account_class', 'account_code', 'account_name', 'account_type', 'class', 'contact_id', 'contact_name', 'cost_center', 'customer', 'department', 'description', 'discount_rate', 'effective_tax_rate', 'invoice_id', 'line_amount', 'line_item_id', 'location', 'project', 'quantity', 'region', 'tax_amount', 'tax_type', 'unit_amount']`。与键取并集，不自行纳入原评分排除列。

全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。

共同时间控制：`[]`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|account_keep_duplicates|209→0|4807→0|L0|

### 原留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|5000|5209|0|0|0/209|0|209|4807|False|
|L1|5000|5209|0|0|0/209|0|209|4807|False|
|L2|5000|5209|0|0|0/209|0|209|4807|False|
|L3|5000|5209|0|0|0/209|0|209|4807|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|line_item_id|0|0|0|0|
|account_class|0|0|0|0|
|account_code|0|0|0|0|
|account_name|0|0|0|0|
|account_type|0|0|0|0|
|class|0|0|0|0|
|contact_id|0|0|0|0|
|contact_name|0|0|0|0|
|cost_center|0|0|0|0|
|customer|0|0|0|0|
|department|0|0|0|0|
|description|0|0|0|0|
|discount_rate|0|0|0|0|
|effective_tax_rate|0|0|0|0|
|invoice_id|0|0|0|0|
|line_amount|0|0|0|0|
|location|0|0|0|0|
|project|0|0|0|0|
|quantity|0|0|0|0|
|region|0|0|0|0|
|tax_amount|0|0|0|0|
|tax_type|0|0|0|0|
|unit_amount|0|0|0|0|

### 重跑 baseline

SQL：`data/017_work/impl-027/baseline.sql`；SHA-256：`60f138a9ab8273d7ab5d23b13fbdcefde6237f7b2c9e14169f87b8cb3066ce6c`。

同输入、同时间控制、不增加因果改动的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|5000|5209|0|0|0/209|0|209|4807|False|
|L1|5000|5209|0|0|0/209|0|209|4807|False|
|L2|5000|5209|0|0|0/209|0|209|4807|False|
|L3|5000|5209|0|0|0/209|0|209|4807|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|line_item_id|0|0|0|0|
|account_class|0|0|0|0|
|account_code|0|0|0|0|
|account_name|0|0|0|0|
|account_type|0|0|0|0|
|class|0|0|0|0|
|contact_id|0|0|0|0|
|contact_name|0|0|0|0|
|cost_center|0|0|0|0|
|customer|0|0|0|0|
|department|0|0|0|0|
|description|0|0|0|0|
|discount_rate|0|0|0|0|
|effective_tax_rate|0|0|0|0|
|invoice_id|0|0|0|0|
|line_amount|0|0|0|0|
|location|0|0|0|0|
|project|0|0|0|0|
|quantity|0|0|0|0|
|region|0|0|0|0|
|tax_amount|0|0|0|0|
|tax_type|0|0|0|0|
|unit_amount|0|0|0|0|

### 重跑 account_keep_duplicates

SQL：`data/017_work/impl-027/account_keep_duplicates.sql`；SHA-256：`f3514ae47c521a791728957adc3b1e4dd7f9bb35e4639a64fb234a70b2ad7b20`。

唯一替换位置offset=236；原文：
```sql
    QUALIFY row_number() OVER (PARTITION BY account_code ORDER BY account_id) = 1
```
新文：
```sql

```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|5209|5209|0|0|0/0|0|0|0|True|
|L1|5209|5209|0|0|0/0|0|0|0|True|
|L2|5209|5209|0|0|0/0|0|0|0|True|
|L3|5209|5209|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|line_item_id|0|0|0|0|
|account_class|0|0|0|0|
|account_code|0|0|0|0|
|account_name|0|0|0|0|
|account_type|0|0|0|0|
|class|0|0|0|0|
|contact_id|0|0|0|0|
|contact_name|0|0|0|0|
|cost_center|0|0|0|0|
|customer|0|0|0|0|
|department|0|0|0|0|
|description|0|0|0|0|
|discount_rate|0|0|0|0|
|effective_tax_rate|0|0|0|0|
|invoice_id|0|0|0|0|
|line_amount|0|0|0|0|
|location|0|0|0|0|
|project|0|0|0|0|
|quantity|0|0|0|0|
|region|0|0|0|0|
|tax_amount|0|0|0|0|
|tax_type|0|0|0|0|
|unit_amount|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**O**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|account_keep_duplicates|O|209→0|4807→0|L0|

重跑是否满足U第4条件：**是：单取消account去重209行/4807格→0，L0匹配；非U**。

P“account_code唯一”已被agent亲自查否并处理，不能归U。说明了选择与代价，也不能按无解释占位/降级归D。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。不确定性由017的“已提到”改按四档逐项记录：account_keep_duplicates=针对本表的具体说明。

与014相比的历史对比沿用原字段：不适用：第三批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

契约一方面要求one row per line_item_id，另一方面叙述left join accounts；冲突码如何选未写明。以明确unique/grain要求识别gold的209行额外输出为O；A可描述保留哪组属性的未定约定，但不能把该约定直接改写为本次未通过核实的U。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
