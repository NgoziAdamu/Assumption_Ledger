# 042 正式标注：impl-015_quickbooks__general_ledger

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。

## 结论

主要原因：**其他**；把握中；2点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

013显示30张raw列/类型不同，行数均未变。event45为解决同库重复ATTACH的Unique file handle conflict，改用fetchdf/register复制raw；这是agent改动，照常标注。直接源按下面逐表检查；CS表使用gold上游，不将本题全部raw变化归给该表。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/quickbooks.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。

两列Other，无法构造改变允许并列顺序的可靠独立SQL修复；同宽逐列屏蔽均减少23907格作为定位。按第7节候选同类无需强造不同类排序，主因Other，把握中。

### mask_running_balance

**其他**；并列；把握高。

running_balance 的同排序键累计次序不同；契约明文允许 engine-defined ties。023诊断排除两列后其余含键完全一致，5475组并列覆盖28106行。042逐列双侧屏蔽诊断每列减少23907格，行不变；这是允许并列的定位，不是建议改agent算法。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用+新做；`records/042_checks/diagnostic_impl-015_quickbooks__general_ledger.json` / `mask_running_balance`。双侧逐列屏蔽诊断（Other定位，非agent SQL修复）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 23907 | 23907 | 47814 | 23907 |
| L1 | 23907 | 23907 | 47814 | 23907 |
| L2 | 23907 | 23907 | 47814 | 23907 |
| L3 | 23907 | 23907 | 47814 | 23907 |

L0减少：[0, 23907]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml` / `text`。

```text
Window ties on all ordering keys are engine-defined; cumulative sums skip NULL values and return NULL only when the entire frame is NULL.
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/1.json` / event 1 / `message`。

```text
Window ties on all ordering keys are engine-defined; cumulative sums skip NULL values and return NULL only when the entire frame is NULL.
```

### mask_running_converted_balance

**其他**；并列；把握高。

running_converted_balance 的同排序键累计次序不同；契约明文允许 engine-defined ties。023诊断排除两列后其余含键完全一致，5475组并列覆盖28106行。042逐列双侧屏蔽诊断每列减少23907格，行不变；这是允许并列的定位，不是建议改agent算法。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用+新做；`records/042_checks/diagnostic_impl-015_quickbooks__general_ledger.json` / `mask_running_converted_balance`。双侧逐列屏蔽诊断（Other定位，非agent SQL修复）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 23907 | 23907 | 47814 | 23907 |
| L1 | 23907 | 23907 | 47814 | 23907 |
| L2 | 23907 | 23907 | 47814 | 23907 |
| L3 | 23907 | 23907 | 47814 | 23907 |

L0减少：[0, 23907]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml` / `text`。

```text
Window ties on all ordering keys are engine-defined; cumulative sums skip NULL values and return NULL only when the entire frame is NULL.
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/1.json` / event 1 / `message`。

```text
Window ties on all ordering keys are engine-defined; cumulative sums skip NULL values and return NULL only when the entire frame is NULL.
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml`；SHA-256 `c7c31842035fff7336164f7713a735dde48f8f77e19e992d2dae072b0144c51a`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/marts/quickbooks__general_ledger.sql`；SHA-256 `4a55ee021407c2bd5381f6828e53d9caebd02189834feee6304b57765ba1b409`。
- 023材料包：`records/023_packages/023_impl-015_quickbooks__general_ledger.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：0条；诊断不计5条上限。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
