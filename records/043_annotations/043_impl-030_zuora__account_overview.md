# 043：impl-030_zuora__account_overview

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为454行/454格。行增多时即使格减少也不作为改善。

层：marts。024旧主要原因原样保留：`C`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/marts/zuora__account_overview.sql`；无SQL注释。材料包：`records/024_packages/024_impl-030_zuora__account_overview.md`。

本表最终SQL执行时Zuora库内raw已为正常多列（invoice为54列），但本次CS输入直接使用gold上游。早期检查的invoice单列坏结构不作为本表CS输入。 初始与agent的run.py SHA-256相同，event10已展示单列按逗号拆分导入逻辑；不是agent另写修复原库。015确认gold与agent raw一致。正常结构不代表所有字段内容位置都符合语义，需逐列核实。

已逐张读取 `records/013_raw_impl-030.json`；与gold关系见 `records/015_raw_impl-030.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 47，`event47 shell heredoc批量写SQL`：同一命令写三个marts；本批仅account_overview在范围内，错误点为invoice/item INNER JOIN。 目录编号：`030-account-command`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共1条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `agent可见有invoice无item的账户`：`records/024_queries.json` 数组索引40（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：invoice_items_left

类别：**Intent Misreading**；角色：主要；把握：高。

契约明确有invoice而无item时计数0；INNER JOIN丢掉这样的账户分组。做法可由规格确定，不用Data覆盖事实替代。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-030_zuora__account_overview.json`，条目 `invoice_items_left`。

基线：L0=454行/454格; L1=454行/454格; L2=454行/454格; L3=454行/454格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：454行/454格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "JOIN intermediate.int_zuora__invoice_item_base AS ii",
    "new": "LEFT JOIN intermediate.int_zuora__invoice_item_base AS ii",
    "offset": 168
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
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
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `030-account-command`；根源决定单元 `impl-030_zuora__account_overview:invoice_items_left`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
