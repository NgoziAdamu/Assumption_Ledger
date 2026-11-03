# 043：impl-030_zuora__monthly_recurring_revenue

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为1行/8格。行增多时即使格减少也不作为改善。

层：marts。024旧主要原因原样保留：`C`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/marts/zuora__monthly_recurring_revenue.sql`；无SQL注释。材料包：`records/024_packages/024_impl-030_zuora__monthly_recurring_revenue.md`。

本表最终SQL执行时Zuora库内raw已为正常多列（invoice为54列），但本次CS输入直接使用gold上游。早期检查的invoice单列坏结构不作为本表CS输入。 初始与agent的run.py SHA-256相同，event10已展示单列按逗号拆分导入逻辑；不是agent另写修复原库。015确认gold与agent raw一致。正常结构不代表所有字段内容位置都符合语义，需逐列核实。

已逐张读取 `records/013_raw_impl-030.json`；与gold关系见 `records/015_raw_impl-030.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 49，`event49 shell heredoc批量写SQL`：同一命令写四个marts；本批仅MRR在范围内，两处非空服务日期过滤逐点记录。 目录编号：`030-mrr-command`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共1条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `agent可见NULL服务日期`：`records/024_queries.json` 数组索引41（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：spine_null_month

类别：**Intent Misreading**；角色：主要；把握：高。

契约要求覆盖spine的所有account/month；额外非空服务日期过滤丢掉NULL月份行。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-030_zuora__monthly_recurring_revenue.json`，条目 `spine_null_month`。

基线：L0=1行/8格; L1=1行/8格; L2=1行/8格; L3=1行/8格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：1行/8格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "    WHERE service_start_day IS NOT NULL",
    "new": "    WHERE TRUE",
    "offset": 175
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
      - intermediate.int_zuora__invoice_item_base
      - intermediate.int_zuora__rate_plan_charge_current
      business_logic: '- Inputs: - From intermediate.int_zuora__invoice_item_base: account_id, service_start_day, rate_plan_charge_id, charge_amount, discount_amount. - From intermediate.int_zuora__rate_plan_charge_current: rate_plan_charge_id, charge_type. - Build the month spine as distinct pairs of (account_id, month of service_start_day set to the first day). - Left join invoice items to the month spine on account_id and month; then left join the current rate plan charge on rate_plan_charge_id. - Classification for each invoice item: - Recurring (MRR): charge_type equals "recurring" when compared case-insensitively (no trimming). - Non-MRR: charge_type is present and, case-insensitively, not equal to "recurring". - If the rate plan charge is missing or charge_type is NULL, the item contributes 0 to both categories. - Per-line numeric handling: - charge_amount is converted to a DOUBLE; invalid or NULL values are treated as 0.0. - discount_amount treats NULL as 0.0; signs are preserved; no rounding or currency conversion. - If the rate plan charge join returns multiple matches for a line, that line’s amounts are counted multiple times. - Aggregations per (account_id, account_month): - Gross MRR: sum of charge_amount over recurring items. - Discount MRR: sum of discount_amount over recurring items. - Net MRR: sum over recurring items of (charge_amount minus discount_amount). - Gross non-MRR: sum of charge_amount over non-MRR items. - Discount non-MRR: sum of discount_amount over non-MRR items. - Net non-MRR: sum over non-MRR items of (charge_amount minus discount_amount). - Output includes every (account_id, account_month) from the month spine; if no items match a category, the corresponding sums are 0.0.'
      columns:
      - name: account_id
        data_type: VARCHAR
        description: Account identifier used for grouping.
      - name: account_month
        data_type: DATE
        description: Month derived from service_start_day, set to the first day of that month.
      - name: gross_current_month_mrr
        data_type: DOUBLE
        description: Sum of charge_amount (invalid or NULL treated as 0.0) for items classified as recurring (case-insensitive match to 'recurring').
      - name: discount_current_month_mrr
        data_type: DOUBLE
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `030-mrr-command`；根源决定单元 `impl-030_zuora__monthly_recurring_revenue:spine_null_month`。

## 点：items_null_month

类别：**Intent Misreading**；角色：非原因；把握：高。

对分类输入另加非空日期过滤，规则未允许删掉这部分输入；单改未影响最终输出。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-030_zuora__monthly_recurring_revenue.json`，条目 `items_null_month`。

基线：L0=1行/8格; L1=1行/8格; L2=1行/8格; L3=1行/8格。

单改后：L0=1行/8格; L1=1行/8格; L2=1行/8格; L3=1行/8格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "    WHERE ii.service_start_day IS NOT NULL",
    "new": "    WHERE TRUE",
    "offset": 833
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
    - name: zuora__monthly_recurring_revenue
      description: Monthly sums of recurring vs non-recurring invoice amounts per account using the current rate plan charge type.
      grain: One row per account_id and account_month (month of service_start_day)
      source_models:
      - intermediate.int_zuora__invoice_item_base
      - intermediate.int_zuora__rate_plan_charge_current
      business_logic: '- Inputs: - From intermediate.int_zuora__invoice_item_base: account_id, service_start_day, rate_plan_charge_id, charge_amount, discount_amount. - From intermediate.int_zuora__rate_plan_charge_current: rate_plan_charge_id, charge_type. - Build the month spine as distinct pairs of (account_id, month of service_start_day set to the first day). - Left join invoice items to the month spine on account_id and month; then left join the current rate plan charge on rate_plan_charge_id. - Classification for each invoice item: - Recurring (MRR): charge_type equals "recurring" when compared case-insensitively (no trimming). - Non-MRR: charge_type is present and, case-insensitively, not equal to "recurring". - If the rate plan charge is missing or charge_type is NULL, the item contributes 0 to both categories. - Per-line numeric handling: - charge_amount is converted to a DOUBLE; invalid or NULL values are treated as 0.0. - discount_amount treats NULL as 0.0; signs are preserved; no rounding or currency conversion. - If the rate plan charge join returns multiple matches for a line, that line’s amounts are counted multiple times. - Aggregations per (account_id, account_month): - Gross MRR: sum of charge_amount over recurring items. - Discount MRR: sum of discount_amount over recurring items. - Net MRR: sum over recurring items of (charge_amount minus discount_amount). - Gross non-MRR: sum of charge_amount over non-MRR items. - Discount non-MRR: sum of discount_amount over non-MRR items. - Net non-MRR: sum over non-MRR items of (charge_amount minus discount_amount). - Output includes every (account_id, account_month) from the month spine; if no items match a category, the corresponding sums are 0.0.'
      columns:
      - name: account_id
        data_type: VARCHAR
        description: Account identifier used for grouping.
      - name: account_month
        data_type: DATE
        description: Month derived from service_start_day, set to the first day of that month.
      - name: gross_current_month_mrr
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `030-mrr-command`；根源决定单元 `impl-030_zuora__monthly_recurring_revenue:items_null_month`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
