# KramaBench / archeology-easy-8：v3.1 修订

相对034：**只改档位**。主要原因：其他 → **其他**；只能组合修复：否 → 否；把握：中。

基础错误机制及原有查询见 [034原标注](../034_annotations/kramabench_archeology-easy-8.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。

## 最终参考值与子任务不一致

- 角色：主要；类别：其他 → **其他**。
- 是否说出：针对本处的具体说明 → **过程中意识到了，交付物里没提**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

中间明确比较含空串56与剔除空串55；这是对计数处理的意识，并不表示agent看过隐藏参考52。最终仅55。

来源：`records/028_kramabench_packages/archeology-easy-8.md`，事件/位置 `step.5.reasoning.1`。
```text
**Inspecting data format**

I need to figure out why my source is coming up empty. It looks like I might need to split values using a period. I have 56 entries, including empty ones, and it seems like 1995 might have some punctuation issues in the reference entries. When I exclude the empty entries, it gives me 55. I should check for distinct sources around delimiters and see if any citations are using commas or semicolons incorrectly. Let's inspect these strings closely!
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/archeology-easy-8.md;subtask.4.answer;records/036_checks/disclosure_audit.json。
