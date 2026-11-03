# 043：impl-027_xero__profit_and_loss_report

## 结论

主要原因：**其他**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为8行/8格。行增多时即使格减少也不作为改善。

层：marts。024旧主要原因原样保留：`O`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/marts/xero__profit_and_loss_report.sql`；无SQL注释。材料包：`records/024_packages/024_impl-027_xero__profit_and_loss_report.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-027.json`；与gold关系见 `records/015_raw_impl-027.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 21,23，`/tmp/models.py`：同一models脚本写两个正式marts；窗口和数值表达式仍逐项列点。 目录编号：`027-models`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共0条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 诊断 `排除并列顺序派生列后的整表诊断`：`records/024_extra_diagnostics.json` 数组索引19（从0开始）。

- 诊断 `gold SQL同gold输入重跑`：`records/024_diagnostics.json` 数组索引35（从0开始）。

涉及运行时间的基线与单改沿用同一固定时刻：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-17 11:30:25.438839+08:00'", "count": 1}]`；完整控制记录见复用重跑JSON。

## 点：window_frame

类别：**其他**；角色：主要；把握：中。

契约running total允许并列行顺序不确定，agent ROWS逐行累计符合自然读法；gold RANGE将并列组一起累计，其他内容诊断一致。另一读法是仅允许展示顺序不确定，本次按逐行累计的自然读法取其他、中把握。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_xero__profit_and_loss_report.json`，条目 `window_frame`。

基线：L0=11行/11格; L1=11行/11格; L2=8行/8格; L3=8行/8格。

单改后：L0=3行/3格; L1=3行/3格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：8行/8格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW",
    "new": "RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW",
    "offset": 2385
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
      - name: cumulative_net
        data_type: DOUBLE
        description: Within report_month, running total of net_amount ordered by pl_category (alphabetical) then account_code ascending; ties are nondeterministic; nulls ignored
      - name: region
        data_type: VARCHAR
        description: Tracking dimension carried from source; part of the grouping; nulls preserved
      - name: department
        data_type: VARCHAR
        description: Tracking dimension carried from source; part of the grouping; nulls preserved
      - name: project
        data_type: VARCHAR
        description: Tracking dimension carried from source; part of the grouping; nulls preserved
      - name: report_generated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Execution timestamp for the run; identical across rows; time zone per engine configuration
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-models`；根源决定单元 `impl-027_xero__profit_and_loss_report:window_frame`。

## 规则问题与限制

- window_frame：契约running total允许并列行顺序不确定，agent ROWS逐行累计符合自然读法；gold RANGE将并列组一起累计，其他内容诊断一致。另一读法是仅允许展示顺序不确定，本次按逐行累计的自然读法取其他、中把握。
