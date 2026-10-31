# DAComp / impl-018_stg_salesforce__opportunity_line_item：v3.1 修订

相对034：**只改档位**。主要原因：代码写错 → **代码写错**；只能组合修复：否 → 否；把握：中。

基础错误机制及原有查询见 [034原标注](../034_annotations/dacomp_impl-018_stg_salesforce__opportunity_line_item.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。

## opportunity_source

- 角色：并列；类别：代码写错 → **代码写错**。
- 是否说出：看到了但没提 → **过程中意识到了，交付物里没提**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

中间代码注释明确识别外键不能取行自身id这一前提；未修到本表两外键，也未在最终报告说明。本组共享前提的意识归第3档，非已正确修复。

来源：`records/016_trace_impl-018.json`，事件/位置 `57.args.command`。
```text
# Correct field source mapping; canonical foreign keys should remain FK columns, not the row's own id.
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md;records/016_trace_impl-018.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## product_source

- 角色：并列；类别：代码写错 → **代码写错**。
- 是否说出：看到了但没提 → **过程中意识到了，交付物里没提**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

中间代码注释明确识别外键不能取行自身id这一前提；未修到本表两外键，也未在最终报告说明。本组共享前提的意识归第3档，非已正确修复。

来源：`records/016_trace_impl-018.json`，事件/位置 `57.args.command`。
```text
# Correct field source mapping; canonical foreign keys should remain FK columns, not the row's own id.
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md;records/016_trace_impl-018.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。
