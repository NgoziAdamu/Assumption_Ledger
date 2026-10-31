# DAComp / impl-004_stg_salesforce__contact_history：v3.1 修订

相对034：**只改档位**。主要原因：已说出的选择 → **已说出的选择**；只能组合修复：否 → 否；把握：中。

基础错误机制及原有查询见 [034原标注](../034_annotations/dacomp_impl-004_stg_salesforce__contact_history.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。

## history_key_frozen

- 角色：主要；类别：已说出的选择 → **已说出的选择**。
- 是否说出：针对本处的具体说明 → **交付物里针对本处说明了**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

最终交付有针对本处的具体说明。

来源：`records/014_trace_impl-004.json`，事件/位置 `51.args.final_thought`。
```text
History 原始表没有契约字段 `created_date` / `history_unique_key`，使用源 `_fivetran_start` 作为变更时间，并以 `_fivetran_start` 与 `_fivetran_end` 计算字符串唯一标识；该映射使快照能够按源可用的版本时间运行。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-004_stg_salesforce__contact_history.md;records/014_trace_impl-004.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## activity_rule_gold_day

- 角色：非原因；类别：Intent Misreading → **Intent Misreading**。
- 是否说出：没有迹象 → **交付物里只有通用说明**。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/014_trace_impl-004.json`，事件/位置 `51.args.final_thought`。
```text
不合格必填字段、无效日期和过短邮编按规则筛除。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-004_stg_salesforce__contact_history.md;records/014_trace_impl-004.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。
