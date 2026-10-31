# DAComp / impl-007_stg_apple_store__sales_subscription_event_summary：v3.1 修订

相对034：**只改档位**。主要原因：Unstated Choice → **Unstated Choice**；只能组合修复：否 → 否；把握：中。

基础错误机制及原有查询见 [034原标注](../034_annotations/dacomp_impl-007_stg_apple_store__sales_subscription_event_summary.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。

## subscriber_source

- 角色：主要；类别：Unstated Choice → **Unstated Choice**。
- 是否说出：只有通用策略说明 → **过程中意识到了，交付物里没提**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

报告草稿明确意识到本组来源映射的语义不一致；event66/68两次写入失败，未留finish或报告文件，只算过程中意识到。草稿未点名两个字段，组级意识的读法列为规则问题。

来源：`records/014_trace_impl-007.json`，事件/位置 `65.args.command`。
```text
Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。若这类字段用于正式订阅财务决策，应以源端字段定义进一步确认。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md;records/014_trace_impl-007.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## marketing_source

- 角色：非原因；类别：Unstated Choice → **Unstated Choice**。
- 是否说出：没有迹象 → **过程中意识到了，交付物里没提**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

报告草稿明确意识到本组来源映射的语义不一致；event66/68两次写入失败，未留finish或报告文件，只算过程中意识到。草稿未点名两个字段，组级意识的读法列为规则问题。

来源：`records/014_trace_impl-007.json`，事件/位置 `65.args.command`。
```text
Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。若这类字段用于正式订阅财务决策，应以源端字段定义进一步确认。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md;records/014_trace_impl-007.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。
