# DAComp / impl-020_stg_intercom__conversation_part_history：v3.1 修订

相对034：**改类别**。主要原因：其他 → **其他**；只能组合修复：否 → 否；把握：中。

基础错误机制及原有查询见 [034原标注](../034_annotations/dacomp_impl-020_stg_intercom__conversation_part_history.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。

## conversation_direct

- 角色：主要；类别：其他 → **其他**。
- 是否说出：针对本处的具体说明 → **交付物里针对本处说明了**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

最终交付有针对本处的具体说明。

来源：`records/016_trace_impl-020.json`，事件/位置 `61.args.final_thought`。
```text
原始 conversation part 文件中的实际列数据与源 schema 声明不一致：对话 ID 实际可从 part `id` 的前缀提取，事件时间可从错位的原始 `conversation_id` 字段解析，事件类型可从 `subject` 字段回退获取。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-020_stg_intercom__conversation_part_history.md;records/016_trace_impl-020.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## part_type_direct

- 角色：非原因；类别：Unstated Choice → **已说出的选择**。
- 是否说出：没有迹象 → **交付物里针对本处说明了**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

最终交付有针对本处的具体说明。

来源：`records/016_trace_impl-020.json`，事件/位置 `61.args.final_thought`。
```text
原始 conversation part 文件中的实际列数据与源 schema 声明不一致：对话 ID 实际可从 part `id` 的前缀提取，事件时间可从错位的原始 `conversation_id` 字段解析，事件类型可从 `subject` 字段回退获取。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-020_stg_intercom__conversation_part_history.md;records/016_trace_impl-020.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## created_at_source

- 角色：非原因；类别：Intent Misreading → **Intent Misreading**。
- 是否说出：没有迹象 → **交付物里针对本处说明了**。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用（均沿用034）。

最终交付有针对本处的具体说明。

来源：`records/016_trace_impl-020.json`，事件/位置 `61.args.final_thought`。
```text
原始 conversation part 文件中的实际列数据与源 schema 声明不一致：对话 ID 实际可从 part `id` 的前缀提取，事件时间可从错位的原始 `conversation_id` 字段解析，事件类型可从 `subject` 字段回退获取。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-020_stg_intercom__conversation_part_history.md;records/016_trace_impl-020.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。
