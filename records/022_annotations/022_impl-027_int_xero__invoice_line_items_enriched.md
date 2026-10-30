# impl-027 / int_xero__invoice_line_items_enriched（校准；v2）

## 1. 差异与结论

契约grain一行/line_item_id；agent按account_code去重保留5000行，gold直接JOIN为5209行，209个重复键。撤去QUALIFY单修L0完全一致。agent已查询重复且明确披露最低account_id选择及丢弃其他属性，不是U。

主要原因：**O**；参与因素：无；把握：高；标记：校准。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

校准过程：盲标固定文件 `records/022_calibration_blind_decisions.json`，哈希锁 `records/022_blind_lock.json`；之后才读018。对照见 `records/022_calibration_comparison.json`。

## 2. 来源、契约及SQL位置

- 精简材料包：[records/013_packages/013_impl-027_intermediate_int_xero__invoice_line_items_enriched.md](../../records/013_packages/013_impl-027_intermediate_int_xero__invoice_line_items_enriched.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`records/012_packages/012_impl-027_intermediate_int_xero__invoice_line_items_enriched.json`。
- 比较结果：[022_reruns_impl-027_int_xero__invoice_line_items_enriched.json](../022_reruns_impl-027_int_xero__invoice_line_items_enriched.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`。

原件第430–542行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql`；原件第1–68行。

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

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql`；原件第1–130行。

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

## 3. agent看到的材料与不确定性

- event 27：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/27.json`。
- event 28：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/28.json`。
- event 29：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/29.json`。
- event 39：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/39.json`。
- event 41：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/41.json`。

四档：**针对本表的具体说明**。

原句（见上述最终报告事件）：

```text
Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.
```

## 4. 核实查询与诊断

核实查询共**1条**（含失败尝试），代价档：**一条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：账号重复和行粒度核实

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb`。

```sql
SELECT (SELECT count(*) FROM staging.stg_xero__account) accounts,(SELECT count(distinct account_code) FROM staging.stg_xero__account) codes,(SELECT count(*) FROM staging.stg_xero__invoice_line_item) lines,(SELECT count(distinct line_item_id) FROM staging.stg_xero__invoice_line_item) line_ids
```

```json
{"columns": ["accounts", "codes", "lines", "line_ids"], "rows": [[500, 482, 5000, 5000]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["line_item_id"]`；比较列：`["account_class", "account_code", "account_name", "account_type", "class", "contact_id", "contact_name", "cost_center", "customer", "department", "description", "discount_rate", "effective_tax_rate", "invoice_id", "line_amount", "line_item_id", "location", "project", "quantity", "region", "tax_amount", "tax_type", "unit_amount"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 5000/5209 | 0/0 | 0/209 | 0 | 209 | 4807 | False |
| L1 | 5000/5209 | 0/0 | 0/209 | 0 | 209 | 4807 | False |
| L2 | 5000/5209 | 0/0 | 0/209 | 0 | 209 | 4807 | False |
| L3 | 5000/5209 | 0/0 | 0/209 | 0 | 209 | 4807 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| line_item_id | 0 | 0 | 0 | 0 |
| account_class | 0 | 0 | 0 | 0 |
| account_code | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_type | 0 | 0 | 0 | 0 |
| class | 0 | 0 | 0 | 0 |
| contact_id | 0 | 0 | 0 | 0 |
| contact_name | 0 | 0 | 0 | 0 |
| cost_center | 0 | 0 | 0 | 0 |
| customer | 0 | 0 | 0 | 0 |
| department | 0 | 0 | 0 | 0 |
| description | 0 | 0 | 0 | 0 |
| discount_rate | 0 | 0 | 0 | 0 |
| effective_tax_rate | 0 | 0 | 0 | 0 |
| invoice_id | 0 | 0 | 0 | 0 |
| line_amount | 0 | 0 | 0 | 0 |
| location | 0 | 0 | 0 | 0 |
| project | 0 | 0 | 0 | 0 |
| quantity | 0 | 0 | 0 | 0 |
| region | 0 | 0 | 0 | 0 |
| tax_amount | 0 | 0 | 0 | 0 |
| tax_type | 0 | 0 | 0 | 0 |
| unit_amount | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-027_int_xero__invoice_line_items_enriched/baseline.sql`；SHA-256：`60f138a9ab8273d7ab5d23b13fbdcefde6237f7b2c9e14169f87b8cb3066ce6c`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 5000/5209 | 0/0 | 0/209 | 0 | 209 | 4807 | False |
| L1 | 5000/5209 | 0/0 | 0/209 | 0 | 209 | 4807 | False |
| L2 | 5000/5209 | 0/0 | 0/209 | 0 | 209 | 4807 | False |
| L3 | 5000/5209 | 0/0 | 0/209 | 0 | 209 | 4807 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| line_item_id | 0 | 0 | 0 | 0 |
| account_class | 0 | 0 | 0 | 0 |
| account_code | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_type | 0 | 0 | 0 | 0 |
| class | 0 | 0 | 0 | 0 |
| contact_id | 0 | 0 | 0 | 0 |
| contact_name | 0 | 0 | 0 | 0 |
| cost_center | 0 | 0 | 0 | 0 |
| customer | 0 | 0 | 0 | 0 |
| department | 0 | 0 | 0 | 0 |
| description | 0 | 0 | 0 | 0 |
| discount_rate | 0 | 0 | 0 | 0 |
| effective_tax_rate | 0 | 0 | 0 | 0 |
| invoice_id | 0 | 0 | 0 | 0 |
| line_amount | 0 | 0 | 0 | 0 |
| location | 0 | 0 | 0 | 0 |
| project | 0 | 0 | 0 | 0 |
| quantity | 0 | 0 | 0 | 0 |
| region | 0 | 0 | 0 | 0 |
| tax_amount | 0 | 0 | 0 | 0 |
| tax_type | 0 | 0 | 0 | 0 |
| unit_amount | 0 | 0 | 0 | 0 |

### account_duplicates

SQL：`data/022_work/impl-027_int_xero__invoice_line_items_enriched/account_duplicates.sql`；SHA-256：`f3514ae47c521a791728957adc3b1e4dd7f9bb35e4639a64fb234a70b2ad7b20`。

替换offset=236，原表达式所在行约8（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY account_code ORDER BY account_id) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 5209/5209 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 5209/5209 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 5209/5209 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 5209/5209 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| line_item_id | 0 | 0 | 0 | 0 |
| account_class | 0 | 0 | 0 | 0 |
| account_code | 0 | 0 | 0 | 0 |
| account_name | 0 | 0 | 0 | 0 |
| account_type | 0 | 0 | 0 | 0 |
| class | 0 | 0 | 0 | 0 |
| contact_id | 0 | 0 | 0 | 0 |
| contact_name | 0 | 0 | 0 | 0 |
| cost_center | 0 | 0 | 0 | 0 |
| customer | 0 | 0 | 0 | 0 |
| department | 0 | 0 | 0 | 0 |
| description | 0 | 0 | 0 | 0 |
| discount_rate | 0 | 0 | 0 | 0 |
| effective_tax_rate | 0 | 0 | 0 | 0 |
| invoice_id | 0 | 0 | 0 | 0 |
| line_amount | 0 | 0 | 0 | 0 |
| location | 0 | 0 | 0 | 0 |
| project | 0 | 0 | 0 | 0 |
| quantity | 0 | 0 | 0 | 0 |
| region | 0 | 0 | 0 | 0 |
| tax_amount | 0 | 0 | 0 | 0 |
| tax_type | 0 | 0 | 0 | 0 |
| unit_amount | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：account_duplicates；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。


## 规则问题

无；依v2标准答案与契约唯一粒度冲突归O。
