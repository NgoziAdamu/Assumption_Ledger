# 043：impl-027_xero__invoice_line_items

## 结论

主要原因：**其他**；把握：中；只能组合修复：否。

手册第7节同类候选例外：全部候选均其他，但并列顺序点只有组级诊断，未逐项排序。旧数值单改列原数字，不能与没有单改的点伪造完整名次。

层：marts。024旧主要原因原样保留：`O`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/marts/xero__invoice_line_items.sql`；无SQL注释。材料包：`records/024_packages/024_impl-027_xero__invoice_line_items.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-027.json`；与gold关系见 `records/015_raw_impl-027.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 21,23，`/tmp/models.py`：同一models脚本写两个正式marts；窗口和数值表达式仍逐项列点。 目录编号：`027-models`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共0条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 诊断 `排除并列顺序派生列后的整表诊断`：`records/024_extra_diagnostics.json` 数组索引18（从0开始）。

- 诊断 `gold SQL同gold输入重跑`：`records/024_diagnostics.json` 数组索引34（从0开始）。

涉及运行时间的基线与单改沿用同一固定时刻：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-17 11:30:25.511140+08:00'", "count": 1}]`；完整控制记录见复用重跑JSON。

## 点：sum_gross

类别：**其他**；角色：同类候选；把握：高。

窗口SUM与分组SUM的浮点累加末位不同，L2数值容差与其余列诊断定位此差异；不是未确立的数据前提。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_xero__invoice_line_items.json`，条目 `sum_gross`。

基线：L0=1030行/2355格; L1=1030行/2355格; L2=190行/380格; L3=190行/380格。

单改后：L0=1047行/2338格; L1=1047行/2338格; L2=190行/380格; L3=190行/380格。L0减量（先行后格）：-17行/17格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "sum(line_amount_nonneg) OVER (PARTITION BY invoice_id)",
    "new": "(SELECT sum(s.line_amount_nonneg) FROM standardized s WHERE s.invoice_id=standardized.invoice_id)",
    "offset": 1173
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
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
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-models`；根源决定单元 `impl-027_xero__invoice_line_items:sum_gross`。

## 点：sum_net

类别：**其他**；角色：同类候选；把握：高。

同一非负net求和仅累加方式不同，末位差异在L2消失；契约没有规定浮点累加次序。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_xero__invoice_line_items.json`，条目 `sum_net`。

基线：L0=1030行/2355格; L1=1030行/2355格; L2=190行/380格; L3=190行/380格。

单改后：L0=696行/1373格; L1=696行/1373格; L2=198行/396格; L3=198行/396格。L0减量（先行后格）：334行/982格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "sum(line_net_of_tax) OVER (PARTITION BY invoice_id)",
    "new": "(SELECT sum(s.line_net_of_tax) FROM standardized s WHERE s.invoice_id=standardized.invoice_id)",
    "offset": 1261
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
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
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-models`；根源决定单元 `impl-027_xero__invoice_line_items:sum_net`。

## 点：line_seq_in_invoice

类别：**其他**；角色：同类候选；把握：中。

契约允许并列键的任意行次序；024诊断核对并列组及排除相应派生列后的其他内容。该列单独列点，但没有独立单改收益，不用成组清零冒充该列清零。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_extra_diagnostics.json`，条目 `排除并列顺序派生列后的整表诊断`。

基线：L0=1030行/2355格; L1=1030行/2355格; L2=190行/380格; L3=190行/380格。

只有成组诊断：排除 ['line_seq_in_invoice', 'invoice_cum_gross_nonneg'] 后 L0=872行/1975格; L1=872行/1975格; L2=0行/0格; L3=0行/0格；没有该列独立单改收益。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。event1完整看到允许并列规则；交付报告没交代本处，写窗口实现不等于意识到另一个合法顺序。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
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
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-models`；根源决定单元 `impl-027_xero__invoice_line_items:line_seq_in_invoice`。

## 点：invoice_cum_gross_nonneg

类别：**其他**；角色：同类候选；把握：中。

契约允许并列键的任意行次序；024诊断核对并列组及排除相应派生列后的其他内容。该列单独列点，但没有独立单改收益，不用成组清零冒充该列清零。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_extra_diagnostics.json`，条目 `排除并列顺序派生列后的整表诊断`。

基线：L0=1030行/2355格; L1=1030行/2355格; L2=190行/380格; L3=190行/380格。

只有成组诊断：排除 ['line_seq_in_invoice', 'invoice_cum_gross_nonneg'] 后 L0=872行/1975格; L1=872行/1975格; L2=0行/0格; L3=0行/0格；没有该列独立单改收益。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。event1完整看到允许并列规则；交付报告没交代本处，写窗口实现不等于意识到另一个合法顺序。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
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
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-models`；根源决定单元 `impl-027_xero__invoice_line_items:invoice_cum_gross_nonneg`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。

只可定同类主因，不能报告这几列的完整单改名次；采用手册第7节同类候选例外。
