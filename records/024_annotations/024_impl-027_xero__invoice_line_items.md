# impl-027 · xero__invoice_line_items

用途：**全量**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

除浮点SUM累加末位外，差异在契约明确允许任意序的重复line_item_id上产生line_seq和累计值变化；209个并列组，去掉两列后L2全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-027_xero__invoice_line_items.md](../024_packages/024_impl-027_xero__invoice_line_items.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`。

```text
725:     - name: xero__invoice_line_items
726:       description: Invoice line items enriched with invoice-level non-negative metrics, shares, sequencing, and run timestamp
727:       grain: One row per input line with non-null invoice_id and line_item_id; duplicates preserved
728:       source_models:
729:       - intermediate.int_xero__invoice_line_items_enriched
730:       business_logic: '- Source rows from intermediate.int_xero__invoice_line_items_enriched where both line_item_id and invoice_id are present. - Pass through descriptive, account, contact, tracking fields, and processed_at unchanged. - Standardize amounts and quantity: - line_amount_nonneg: if line_amount is null then null; if negative then 0; otherwise keep line_amount. - tax_amount_nonneg: if tax_amount is null then null; if negative then 0; otherwise keep tax_amount. - line_net_of_tax: line_amount minus tax_amount (treat missing tax_amount as 0); if result is negative then 0; if line_amount is null then null. - quantity: set to null when source quantity is null or negative; otherwise keep the source value. - Per invoice_id, compute: - invoice_gross_nonneg: sum of line_amount_nonneg (nulls ignored; null if all inputs are null). - invoice_net_nonneg: sum of line_net_of_tax (nulls ignored; null if all inputs are null). - invoice_line_count: number of lines after the ID filters (includes lines with null amounts). - Attach invoice-level totals back to each line. - Per-line shares (only when denominators are positive): - line_share_gross: line_amount_nonneg divided by invoice_gross_nonneg; otherwise null. - line_share_net: line_net_of_tax divided by invoice_net_nonneg; otherwise null. - Within each invoice_id, order lines by line_item_id ascending to compute: - invoice_cum_gross_nonneg: cumulative sum of line_amount_nonneg from the first ordered line through the current line. - line_seq_in_invoice: 1-based sequence in that order. If multiple lines share the same line_item_id within an invoice, their relative order is unspecified. - Classify line_item_type by line_amount: positive → Revenue; negative → Expense/Refund; zero or null → Neutral. - Set report_generated_at to the current timestamp at model execution. - Final result: one row per input line that passed the ID filters, ordered by invoice_id and line_seq_in_invoice ascending.'
731:       columns:
732:       - name: line_item_id
733:         data_type: VARCHAR
734:         description: Invoice line item identifier from source; NULLs are filtered out upstream
735:         tests:
736:         - not_null
737:       - name: invoice_id
738:         data_type: VARCHAR
739:         description: Invoice identifier from source; NULLs are filtered out upstream
740:         tests:
741:         - not_null
742:       - name: account_code
743:         data_type: BIGINT
744:         description: Account code of the line item (numeric code from source)
745:       - name: account_name
746:         data_type: VARCHAR
747:         description: Account name associated with the line item
748:       - name: account_type
749:         data_type: VARCHAR
750:         description: Account type classification from source
751:       - name: account_class
752:         data_type: VARCHAR
753:         description: Account class/category from source
754:       - name: description
755:         data_type: VARCHAR
756:         description: Free-text line description from source
757:       - name: quantity
758:         data_type: DOUBLE
759:         description: 'Quantity with guard: null if source quantity is null or negative; otherwise pass-through'
760:       - name: unit_amount
761:         data_type: DOUBLE
762:         description: Unit price from source (pass-through; no rounding)
763:       - name: line_amount
764:         data_type: DOUBLE
765:         description: Line amount from source (pass-through; may be negative or null)
766:       - name: tax_amount
767:         data_type: DOUBLE
768:         description: Tax amount from source (pass-through; may be negative or null)
769:       - name: tax_type
770:         data_type: VARCHAR
771:         description: Tax type/code from source
772:       - name: discount_rate
773:         data_type: DOUBLE
774:         description: Discount rate from source (pass-through; no transformation)
775:       - name: contact_id
776:         data_type: VARCHAR
777:         description: Contact identifier associated with the invoice line
778:       - name: contact_name
779:         data_type: VARCHAR
780:         description: Contact name associated with the invoice line
781:       - name: region
782:         data_type: VARCHAR
783:         description: Region tracking dimension from source
784:       - name: department
785:         data_type: VARCHAR
786:         description: Department tracking dimension from source
787:       - name: project
788:         data_type: VARCHAR
789:         description: Project tracking dimension from source
790:       - name: location
791:         data_type: VARCHAR
792:         description: Location tracking dimension from source
793:       - name: class
794:         data_type: VARCHAR
795:         description: Class tracking dimension from source
796:       - name: customer
797:         data_type: VARCHAR
798:         description: Customer tracking dimension from source
799:       - name: cost_center
800:         data_type: VARCHAR
801:         description: Cost center tracking dimension from source
802:       - name: line_amount_nonneg
803:         data_type: DOUBLE
804:         description: If line_amount is null then null; if negative then 0; otherwise equal to line_amount
805:       - name: tax_amount_nonneg
806:         data_type: DOUBLE
807:         description: If tax_amount is null then null; if negative then 0; otherwise equal to tax_amount
808:       - name: line_net_of_tax
809:         data_type: DOUBLE
810:         description: Line amount minus tax (missing tax treated as 0), floored at 0; null if line_amount is null
811:       - name: invoice_gross_nonneg
812:         data_type: DOUBLE
813:         description: Sum of non-negative line amounts per invoice; ignores nulls; null if all inputs are null
814:       - name: invoice_net_nonneg
815:         data_type: DOUBLE
816:         description: Sum of non-negative net-of-tax amounts per invoice; ignores nulls; null if all inputs are null
817:       - name: invoice_line_count
818:         data_type: BIGINT
819:         description: Number of lines per invoice after filtering out null line_item_id and invoice_id
820:       - name: line_share_gross
821:         data_type: DOUBLE
822:         description: Per-line proportion of invoice gross; computed only when invoice gross is > 0; otherwise null
823:       - name: line_share_net
824:         data_type: DOUBLE
825:         description: Per-line proportion of invoice net; computed only when invoice net is > 0; otherwise null
826:       - name: invoice_cum_gross_nonneg
827:         data_type: DOUBLE
828:         description: Cumulative sum of non-negative line amounts within invoice ordered by line_item_id; includes current row; tie order for duplicate line_item_id is unspecified
829:       - name: line_seq_in_invoice
830:         data_type: BIGINT
831:         description: 1-based position within invoice ordered by line_item_id; tie order for duplicate line_item_id is unspecified
832:       - name: line_item_type
833:         data_type: VARCHAR
834:         description: 'Classification by line_amount sign: positive Revenue; negative Expense/Refund; otherwise Neutral (includes null and zero)'
835:       - name: processed_at
836:         data_type: TIMESTAMP WITH TIME ZONE
837:         description: ETL processing timestamp from the source intermediate model
838:       - name: report_generated_at
839:         data_type: TIMESTAMP WITH TIME ZONE
840:         description: Query run timestamp set at model execution time
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/marts/xero__invoice_line_items.sql`；SHA-256 `f1f358457382caa6ba6c4761a2fac468c27a4fc7824261c03cba447db56e275f`。

```text
1: WITH source_lines AS (
2:     SELECT *
3:     FROM intermediate.int_xero__invoice_line_items_enriched
4:     WHERE line_item_id IS NOT NULL
5:       AND invoice_id IS NOT NULL
6: ),
7: standardized AS (
8:     SELECT
9:         line_item_id,
10:         invoice_id,
11:         account_code,
12:         account_name,
13:         account_type,
14:         account_class,
15:         description,
16:         CASE WHEN quantity IS NULL OR quantity < 0 THEN NULL ELSE quantity END AS quantity,
17:         unit_amount,
18:         line_amount,
19:         tax_amount,
20:         tax_type,
21:         discount_rate,
22:         contact_id,
23:         contact_name,
24:         region,
25:         department,
26:         project,
27:         location,
28:         class,
29:         customer,
30:         cost_center,
31:         CASE WHEN line_amount IS NULL THEN NULL ELSE greatest(line_amount, 0) END AS line_amount_nonneg,
32:         CASE WHEN tax_amount IS NULL THEN NULL ELSE greatest(tax_amount, 0) END AS tax_amount_nonneg,
33:         CASE
34:             WHEN line_amount IS NULL THEN NULL
35:             ELSE greatest(line_amount - coalesce(tax_amount, 0), 0)
36:         END AS line_net_of_tax,
37:         processed_at
38:     FROM source_lines
39: ),
40: invoice_totals AS (
41:     SELECT
42:         *,
43:         sum(line_amount_nonneg) OVER (PARTITION BY invoice_id) AS invoice_gross_nonneg,
44:         sum(line_net_of_tax) OVER (PARTITION BY invoice_id) AS invoice_net_nonneg,
45:         count(*) OVER (PARTITION BY invoice_id) AS invoice_line_count,
46:         sum(line_amount_nonneg) OVER (
47:             PARTITION BY invoice_id
48:             ORDER BY line_item_id ASC
49:             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
50:         ) AS invoice_cum_gross_nonneg,
51:         row_number() OVER (PARTITION BY invoice_id ORDER BY line_item_id ASC) AS line_seq_in_invoice
52:     FROM standardized
53: )
54: SELECT
55:     line_item_id,
56:     invoice_id,
57:     account_code,
58:     account_name,
59:     account_type,
60:     account_class,
61:     description,
62:     quantity,
63:     unit_amount,
64:     line_amount,
65:     tax_amount,
66:     tax_type,
67:     discount_rate,
68:     contact_id,
69:     contact_name,
70:     region,
71:     department,
72:     project,
73:     location,
74:     class,
75:     customer,
76:     cost_center,
77:     line_amount_nonneg,
78:     tax_amount_nonneg,
79:     line_net_of_tax,
80:     invoice_gross_nonneg,
81:     invoice_net_nonneg,
82:     invoice_line_count,
83:     CASE WHEN invoice_gross_nonneg > 0 THEN line_amount_nonneg / invoice_gross_nonneg END AS line_share_gross,
84:     CASE WHEN invoice_net_nonneg > 0 THEN line_net_of_tax / invoice_net_nonneg END AS line_share_net,
85:     invoice_cum_gross_nonneg,
86:     line_seq_in_invoice,
87:     CASE
88:         WHEN line_amount > 0 THEN 'Revenue'
89:         WHEN line_amount < 0 THEN 'Expense/Refund'
90:         ELSE 'Neutral'
91:     END AS line_item_type,
92:     processed_at,
93:     current_timestamp AS report_generated_at
94: FROM invoice_totals
95: ORDER BY invoice_id, line_seq_in_invoice
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/marts/xero__invoice_line_items.sql`；SHA-256 `bfa31c0bdc1b6cc2be2249bb4aa7df8777bc6863452e35527c41b48a8a0ba2e9`。

```text
1: -- Mart table: Invoice Line Items - enriched with invoice-level metrics and defensible constraints
2: -- Layer contract: ONLY reference intermediate layer
3: 
4: WITH base AS (
5:     SELECT
6:         ili.line_item_id,
7:         ili.invoice_id,
8:         ili.account_code,
9:         ili.account_name,
10:         ili.account_type,
11:         ili.account_class,
12:         ili.description,
13:         ili.quantity,
14:         ili.unit_amount,
15:         ili.line_amount,
16:         ili.tax_amount,
17:         ili.tax_type,
18:         ili.discount_rate,
19:         ili.contact_id,
20:         ili.contact_name,
21:         ili.region,
22:         ili.department,
23:         ili.project,
24:         ili.location,
25:         ili.class,
26:         ili.customer,
27:         ili.cost_center,
28:         ili.processed_at
29:     FROM intermediate.int_xero__invoice_line_items_enriched ili
30:     WHERE ili.line_item_id IS NOT NULL
31:       AND ili.invoice_id IS NOT NULL
32: ),
33: 
34: validated AS (
35:     SELECT
36:         b.*,
37:         -- Enforce non-negative amounts for metric denominators; keep raw for audit
38:         GREATEST(b.line_amount, 0) AS line_amount_nonneg,
39:         GREATEST(b.tax_amount, 0)  AS tax_amount_nonneg,
40:         -- Net of tax (non-negative)
41:         GREATEST(b.line_amount - COALESCE(b.tax_amount, 0), 0) AS line_net_of_tax,
42:         -- Guard quantity
43:         CASE WHEN b.quantity IS NULL OR b.quantity < 0 THEN NULL ELSE b.quantity END AS quantity_valid
44:     FROM base b
45: ),
46: 
47: invoice_sums AS (
48:     SELECT
49:         invoice_id,
50:         SUM(line_amount_nonneg) AS invoice_gross_nonneg,
51:         SUM(line_net_of_tax)    AS invoice_net_nonneg,
52:         COUNT(*)                AS invoice_line_count
53:     FROM validated
54:     GROUP BY invoice_id
55: ),
56: 
57: scored AS (
58:     SELECT
59:         v.*,
60:         s.invoice_gross_nonneg,
61:         s.invoice_net_nonneg,
62:         s.invoice_line_count,
63:         -- Line share of invoice totals (defensive denominators)
64:         CASE WHEN s.invoice_gross_nonneg > 0 THEN v.line_amount_nonneg / s.invoice_gross_nonneg END AS line_share_gross,
65:         CASE WHEN s.invoice_net_nonneg   > 0 THEN v.line_net_of_tax   / s.invoice_net_nonneg   END AS line_share_net,
66:         -- Window metrics per invoice
67:         SUM(v.line_amount_nonneg) OVER (PARTITION BY v.invoice_id ORDER BY v.line_item_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS invoice_cum_gross_nonneg,
68:         ROW_NUMBER() OVER (PARTITION BY v.invoice_id ORDER BY v.line_item_id) AS line_seq_in_invoice,
69:         -- Classification
70:         CASE
71:             WHEN v.line_amount > 0 THEN 'Revenue'
72:             WHEN v.line_amount < 0 THEN 'Expense/Refund'
73:             ELSE 'Neutral'
74:         END AS line_item_type
75:     FROM validated v
76:     JOIN invoice_sums s USING (invoice_id)
77: )
78: 
79: SELECT
80:     -- Identity
81:     line_item_id,
82:     invoice_id,
83: 
84:     -- Details
85:     account_code,
86:     account_name,
87:     account_type,
88:     account_class,
89:     description,
90:     quantity_valid AS quantity,
91:     unit_amount,
92:     line_amount,
93:     tax_amount,
94:     tax_type,
95:     discount_rate,
96: 
97:     -- Contact
98:     contact_id,
99:     contact_name,
100: 
101:     -- Tracking dims
102:     region,
103:     department,
104:     project,
105:     location,
106:     class,
107:     customer,
108:     cost_center,
109: 
110:     -- Metrics
111:     line_amount_nonneg,
112:     tax_amount_nonneg,
113:     line_net_of_tax,
114:     invoice_gross_nonneg,
115:     invoice_net_nonneg,
116:     invoice_line_count,
117:     line_share_gross,
118:     line_share_net,
119:     invoice_cum_gross_nonneg,
120:     line_seq_in_invoice,
121:     line_item_type,
122: 
123:     -- Processing metadata
124:     processed_at,
125:     CURRENT_TIMESTAMP AS report_generated_at
126: 
127: FROM scored
128: 
129: ORDER BY invoice_id, line_seq_in_invoice
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- 本表主要差异（O）：**看到了但没提**；事件 21、23、27、28、39。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 21：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/21.json`；命令首行：`cat > /tmp/models.py <<'PY'`。
event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/23.json`；命令首行：`cat >> /tmp/models.py <<'PY'`。
event 27：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/27.json`；命令首行：`python - <<'PY'`。
event 28：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/28.json`；原始观察输出。
event 39：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/39.json`；命令首行：`cat > result.md <<'EOF'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

Implemented the Xero SQL pipeline in `sql/`, following the staging → intermediate → marts order and the provided data contract.

- Created 14 staging models, 5 intermediate models, and 4 marts models with DuckDB SQL, fully qualified upstream references, and no trailing semicolons.
- Applied contract-driven field cleaning, casting, and row filters; active-option matching and tracking pivots; invoice and general-ledger enrichment; and financial reporting calculations.
- Avoided duplicate account-code join expansion by selecting one account row per code. Duplicate source relationships remain preserved in the relationship model as contracted; pivots collapse repeated assignments and select the lexicographically greatest valid option.
- Validation results: invoice-line enriched and mart models each have 5,000 rows and 5,000 unique line-item IDs; the general ledger has 8,000 unique journal/journal-line combinations; staged invoices have 3,489 valid dates and no dates beyond the allowed horizon; no staged invoice unit amounts violate the defined range; and two of 22 tracking categories normalize to `UNKNOWN`.

Validation: `python run.py` completed successfully with all 14 staging, 5 intermediate, and 4 marts models created. Sanity checks verified unique IDs/keys and nonnegative invoice-level aggregates. No SQL execution failures remained.

Contract assumptions: Raw data does not provide a processing timestamp for some entities, so `processed_at` is NULL where unavailable. Available source timestamp strings are parsed with DuckDB `TRY_CAST`; invalid timestamps become NULL. General-ledger fact and report timestamps use `current_timestamp`. Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.
```

## 查询

核实查询 **0** 条；代价档：**需要查业务说明**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 诊断：排除并列顺序派生列后的整表诊断
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

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
    TIMESTAMPTZ '2025-10-17 11:30:25.511140+08:00' AS report_generated_at
FROM invoice_totals
ORDER BY invoice_id, line_seq_in_invoice
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5209|5209|872|1975|否|
|L1|5209|5209|872|1975|否|
|L2|5209|5209|0|0|是|
|L3|5209|5209|0|0|是|

首次整表匹配：**L2**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_gross_nonneg":520,"invoice_net_nonneg":522,"line_share_gross":457,"line_share_net":476}`
- L1：`{"invoice_gross_nonneg":520,"invoice_net_nonneg":522,"line_share_gross":457,"line_share_net":476}`
- L2：`{}`
- L3：`{}`
excluded：`["line_seq_in_invoice","invoice_cum_gross_nonneg"]`
tie_groups：`{"sql":"SELECT count(*) FROM (SELECT invoice_id,line_item_id FROM pred GROUP BY ALL HAVING count(*)>1)","count":209}`

### 诊断：gold SQL同gold输入重跑
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

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
    TIMESTAMPTZ '2025-10-17 11:30:25.511140+08:00' AS report_generated_at

FROM scored

ORDER BY invoice_id, line_seq_in_invoice
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5209|5209|245|506|否|
|L1|5209|5209|245|506|否|
|L2|5209|5209|198|396|否|
|L3|5209|5209|198|396|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_cum_gross_nonneg":198,"invoice_gross_nonneg":23,"invoice_net_nonneg":34,"line_seq_in_invoice":198,"line_share_gross":20,"line_share_net":33}`
- L1：`{"invoice_cum_gross_nonneg":198,"invoice_gross_nonneg":23,"invoice_net_nonneg":34,"line_seq_in_invoice":198,"line_share_gross":20,"line_share_net":33}`
- L2：`{"invoice_cum_gross_nonneg":198,"line_seq_in_invoice":198}`
- L3：`{"invoice_cum_gross_nonneg":198,"line_seq_in_invoice":198}`

### 诊断：固定时间
[024_history_clock.json](../024_history_clock.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

```sql
SELECT min(report_generated_at),max(report_generated_at) FROM marts.xero__invoice_line_items
```


```json
{"rows":[["2025-10-17 11:30:25.511140+08:00","2025-10-17 11:30:25.511140+08:00"]]}
```

## 独立单点重跑

### 024_reruns_impl-027_xero__invoice_line_items.json
[024_reruns_impl-027_xero__invoice_line_items.json](../024_reruns_impl-027_xero__invoice_line_items.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-17 11:30:25.511140+08:00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-17'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5209|5209|1030|2355|否|
|L1|5209|5209|1030|2355|否|
|L2|5209|5209|190|380|否|
|L3|5209|5209|190|380|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_cum_gross_nonneg":190,"invoice_gross_nonneg":520,"invoice_net_nonneg":522,"line_seq_in_invoice":190,"line_share_gross":457,"line_share_net":476}`
- L1：`{"invoice_cum_gross_nonneg":190,"invoice_gross_nonneg":520,"invoice_net_nonneg":522,"line_seq_in_invoice":190,"line_share_gross":457,"line_share_net":476}`
- L2：`{"invoice_cum_gross_nonneg":190,"line_seq_in_invoice":190}`
- L3：`{"invoice_cum_gross_nonneg":190,"line_seq_in_invoice":190}`

#### baseline
私有SQL：`data/024_work/impl-027_xero__invoice_line_items/baseline.sql`；SHA-256 `e5b7d476a97629b6a138569115ce824ffaa4ae621a45df960258733d4b86754c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5209|5209|1030|2355|否|
|L1|5209|5209|1030|2355|否|
|L2|5209|5209|190|380|否|
|L3|5209|5209|190|380|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_cum_gross_nonneg":190,"invoice_gross_nonneg":520,"invoice_net_nonneg":522,"line_seq_in_invoice":190,"line_share_gross":457,"line_share_net":476}`
- L1：`{"invoice_cum_gross_nonneg":190,"invoice_gross_nonneg":520,"invoice_net_nonneg":522,"line_seq_in_invoice":190,"line_share_gross":457,"line_share_net":476}`
- L2：`{"invoice_cum_gross_nonneg":190,"line_seq_in_invoice":190}`
- L3：`{"invoice_cum_gross_nonneg":190,"line_seq_in_invoice":190}`

#### sum_gross
不计参与因素；类别候选O。窗口SUM与分组SUM浮点累加顺序造成末位差异；诊断比较容差及改写。
相对本轮基线：行减少-17，格减少17。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第43行、offset 1173起替换；其他字节相同。
原表达式：
```sql
sum(line_amount_nonneg) OVER (PARTITION BY invoice_id)
```

修改后：
```sql
(SELECT sum(s.line_amount_nonneg) FROM standardized s WHERE s.invoice_id=standardized.invoice_id)
```

私有SQL：`data/024_work/impl-027_xero__invoice_line_items/sum_gross.sql`；SHA-256 `d813275331717bf9d788ddd5b1d2380cb1490653d046feb98803ff98a9f698d2`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5209|5209|1047|2338|否|
|L1|5209|5209|1047|2338|否|
|L2|5209|5209|190|380|否|
|L3|5209|5209|190|380|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_cum_gross_nonneg":190,"invoice_gross_nonneg":509,"invoice_net_nonneg":522,"line_seq_in_invoice":190,"line_share_gross":451,"line_share_net":476}`
- L1：`{"invoice_cum_gross_nonneg":190,"invoice_gross_nonneg":509,"invoice_net_nonneg":522,"line_seq_in_invoice":190,"line_share_gross":451,"line_share_net":476}`
- L2：`{"invoice_cum_gross_nonneg":190,"line_seq_in_invoice":190}`
- L3：`{"invoice_cum_gross_nonneg":190,"line_seq_in_invoice":190}`

#### sum_net
不计参与因素；类别候选O。窗口SUM与分组SUM浮点累加顺序造成末位差异；诊断比较容差及改写。
相对本轮基线：行减少334，格减少982。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第44行、offset 1261起替换；其他字节相同。
原表达式：
```sql
sum(line_net_of_tax) OVER (PARTITION BY invoice_id)
```

修改后：
```sql
(SELECT sum(s.line_net_of_tax) FROM standardized s WHERE s.invoice_id=standardized.invoice_id)
```

私有SQL：`data/024_work/impl-027_xero__invoice_line_items/sum_net.sql`；SHA-256 `67d9d8627c2c9a95b7c10697fb15f6265a6e463bbde0a228f96efd15eb012121`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5209|5209|696|1373|否|
|L1|5209|5209|696|1373|否|
|L2|5209|5209|198|396|否|
|L3|5209|5209|198|396|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_cum_gross_nonneg":198,"invoice_gross_nonneg":520,"line_seq_in_invoice":198,"line_share_gross":457}`
- L1：`{"invoice_cum_gross_nonneg":198,"invoice_gross_nonneg":520,"line_seq_in_invoice":198,"line_share_gross":457}`
- L2：`{"invoice_cum_gross_nonneg":198,"line_seq_in_invoice":198}`
- L3：`{"invoice_cum_gross_nonneg":198,"line_seq_in_invoice":198}`
## 规则问题

运行时浮点累加顺序与允许的并列行序同属O；不把SUM改写造成的偶然行数改善解释为agent数据错误。诊断排除列仅用于确认O，官方判错状态不变。

