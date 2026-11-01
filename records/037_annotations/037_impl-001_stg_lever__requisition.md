# impl-001_stg_lever__requisition（037 正式批次）

主要原因：**Intent Misreading**；把握：高。019旧主要原因原样保留：`C`，不作为新类别依据。

## 范围与材料

- 层：staging；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__requisition.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，finish 67 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-001_stg_lever__requisition.json`；037补充：`records/037_checks/`。

## 逐点标注

### compensation_band_currency

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约已逐字段给出合法枚举及nullify_field；agent未执行，改变保留值而不只是呈现。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: compensation_band_currency
>           data_type: VARCHAR(3)
>           validation_rules:
>             - rule: "compensation_band_currency IS NULL OR compensation_band_currency IN ('USD', 'EUR', 'GBP', 'CNY', 'CAD', 'AUD')"
>               on_failure: nullify_field

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__requisition.sql`，第 8–8 行：

```sql
try_cast(r."compensation_band_currency" AS VARCHAR(3)) AS compensation_band_currency
```

单改/诊断：`records/019_reruns_impl-001_stg_lever__requisition.json#compensation_band_currency`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4/5 | 2/2 | 2/3 |
| L1 | 4/5 | 2/2 | 2/3 |
| L2 | 4/5 | 2/2 | 2/3 |
| L3 | 4/5 | 2/2 | 2/3 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。唯一键重复仅保留一行。

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### compensation_band_interval

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约已逐字段给出合法枚举及nullify_field；agent未执行，改变保留值而不只是呈现。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: compensation_band_interval
>           data_type: VARCHAR(10)
>           validation_rules:
>             - rule: "compensation_band_interval IS NULL OR compensation_band_interval IN ('hourly', 'monthly', 'yearly')"
>               on_failure: nullify_field

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__requisition.sql`，第 9–9 行：

```sql
try_cast(r."compensation_band_interval" AS VARCHAR(10)) AS compensation_band_interval
```

单改/诊断：`records/019_reruns_impl-001_stg_lever__requisition.json#compensation_band_interval`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4/5 | 3/3 | 1/2 |
| L1 | 4/5 | 3/3 | 1/2 |
| L2 | 4/5 | 3/3 | 1/2 |
| L3 | 4/5 | 3/3 | 1/2 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。唯一键重复仅保留一行。

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
