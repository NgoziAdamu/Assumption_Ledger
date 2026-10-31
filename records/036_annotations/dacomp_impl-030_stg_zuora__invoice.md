# DAComp / impl-030_stg_zuora__invoice：v3.1 修订

相对034：**只改档位**。主要原因：多因并列 → **多因并列**；只能组合修复：否 → 否；把握：中。

基础错误机制及原有查询见 [034原标注](../034_annotations/dacomp_impl-030_stg_zuora__invoice.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。

## account_source

- 角色：并列；类别：Data Misconception → **Data Misconception**。
- 是否说出：只有通用策略说明 → **交付物里只有通用说明**。
- 证据在场：否；曾经理解对过：否；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## adjustment_amount_representation

- 角色：并列；类别：其他 → **其他**。
- 是否说出：只有通用策略说明 → **交付物里只有通用说明**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## credit_balance_adjustment_amount_representation

- 角色：并列；类别：其他 → **其他**。
- 是否说出：只有通用策略说明 → **交付物里只有通用说明**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## credit_memo_amount_representation

- 角色：并列；类别：其他 → **其他**。
- 是否说出：只有通用策略说明 → **交付物里只有通用说明**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## exchange_rate_representation

- 角色：并列；类别：其他 → **其他**。
- 是否说出：只有通用策略说明 → **交付物里只有通用说明**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## created_date_nullable

- 角色：参与；类别：Intent Misreading → **Intent Misreading**。
- 是否说出：看到了但没提 → **交付物里只有通用说明**。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
Staging 采用安全类型转换、删除标记过滤、更新时间驱动的最新记录标记；账户状态按契约规范化/过滤，invoice 创建日期按契约限制时间范围。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## amount_without_tax_representation

- 角色：参与；类别：其他 → **其他**。
- 是否说出：没有迹象 → **交付物里只有通用说明**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## amount_without_tax_home_currency_representation

- 角色：参与；类别：其他 → **其他**。
- 是否说出：没有迹象 → **交付物里只有通用说明**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## exchange_rate_date_representation

- 角色：参与；类别：其他 → **其他**。
- 是否说出：没有迹象 → **交付物里只有通用说明**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## target_date_representation

- 角色：参与；类别：其他 → **其他**。
- 是否说出：没有迹象 → **交付物里只有通用说明**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## balance_representation

- 角色：参与；类别：其他 → **其他**。
- 是否说出：没有迹象 → **交付物里只有通用说明**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。

来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。
