# 042 正式标注：impl-019_apple_store__app_version_report

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。

## 结论

主要原因：**Unstated Choice**；把握高；4点。只能组合修复：否。023旧主要原因`A`仅存档。

## 详细发现

### 比较口径与原始数据

原始session相关变化在gold raw同样存在；按015结论及本次要求照常标注，staging仍使用agent留存raw。benchmark加载原因仅记为推测；两个marts按CS取gold上游。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/apple_store.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### join_cr

**Unstated Choice**；非原因；把握高。

cr来源的连接使用IS NOT DISTINCT FROM，gold用普通等号；契约指定连接键但未规定NULL键相互匹配与否。NULL-safe键是未定选择，不从gold做法推出数据事实。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__app_version_report.json` / `join_cr`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 342 | 342 | 959 | 959 |
| L1 | 342 | 342 | 959 | 959 |
| L2 | 342 | 342 | 959 | 959 |
| L3 | 342 | 342 | 959 | 959 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
business_logic: '- Drive the output from intermediate.int_apple_store__app_version_report (reporting_grain), emitting exactly one row per (source_relation, date_day, app_id, source_type, app_version).
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
business_logic: '- Drive the output from intermediate.int_apple_store__app_version_report (reporting_grain), emitting exactly one row per (source_relation, date_day, app_id, source_type, app_version).
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__app_version_report.sql` / `text`。

```text
LEFT JOIN cr ON g.source_relation IS NOT DISTINCT FROM cr.source_relation AND g.date_day IS NOT DISTINCT FROM cr.date_day AND g.app_id IS NOT DISTINCT FROM cr.app_id AND g.source_type IS NOT DISTINCT FROM cr.source_type AND g.app_version IS NOT DISTINCT FROM cr.app_version
```

### join_inst

**Unstated Choice**；非原因；把握高。

inst来源的连接使用IS NOT DISTINCT FROM，gold用普通等号；契约指定连接键但未规定NULL键相互匹配与否。NULL-safe键是未定选择，不从gold做法推出数据事实。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__app_version_report.json` / `join_inst`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 342 | 342 | 959 | 959 |
| L1 | 342 | 342 | 959 | 959 |
| L2 | 342 | 342 | 959 | 959 |
| L3 | 342 | 342 | 959 | 959 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
business_logic: '- Drive the output from intermediate.int_apple_store__app_version_report (reporting_grain), emitting exactly one row per (source_relation, date_day, app_id, source_type, app_version).
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
business_logic: '- Drive the output from intermediate.int_apple_store__app_version_report (reporting_grain), emitting exactly one row per (source_relation, date_day, app_id, source_type, app_version).
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__app_version_report.sql` / `text`。

```text
LEFT JOIN inst ON g.source_relation IS NOT DISTINCT FROM inst.source_relation AND g.date_day IS NOT DISTINCT FROM inst.date_day AND g.app_id IS NOT DISTINCT FROM inst.app_id AND g.source_type IS NOT DISTINCT FROM inst.source_type AND g.app_version IS NOT DISTINCT FROM inst.app_version
```

### join_ses

**Unstated Choice**；主要；把握高。

ses来源的连接使用IS NOT DISTINCT FROM，gold用普通等号；契约指定连接键但未规定NULL键相互匹配与否。NULL-safe键是未定选择，不从gold做法推出数据事实。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__app_version_report.json` / `join_ses`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 342 | 0 | 959 | 0 |
| L1 | 342 | 0 | 959 | 0 |
| L2 | 342 | 0 | 959 | 0 |
| L3 | 342 | 0 | 959 | 0 |

L0减少：[342, 959]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
business_logic: '- Drive the output from intermediate.int_apple_store__app_version_report (reporting_grain), emitting exactly one row per (source_relation, date_day, app_id, source_type, app_version).
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
business_logic: '- Drive the output from intermediate.int_apple_store__app_version_report (reporting_grain), emitting exactly one row per (source_relation, date_day, app_id, source_type, app_version).
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__app_version_report.sql` / `text`。

```text
LEFT JOIN ses ON g.source_relation IS NOT DISTINCT FROM ses.source_relation AND g.date_day IS NOT DISTINCT FROM ses.date_day AND g.app_id IS NOT DISTINCT FROM ses.app_id AND g.source_type IS NOT DISTINCT FROM ses.source_type AND g.app_version IS NOT DISTINCT FROM ses.app_version
```

### join_app

**Unstated Choice**；非原因；把握高。

app来源的连接使用IS NOT DISTINCT FROM，gold用普通等号；契约指定连接键但未规定NULL键相互匹配与否。NULL-safe键是未定选择，不从gold做法推出数据事实。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__app_version_report.json` / `join_app`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 342 | 342 | 959 | 959 |
| L1 | 342 | 342 | 959 | 959 |
| L2 | 342 | 342 | 959 | 959 |
| L3 | 342 | 342 | 959 | 959 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
business_logic: '- Drive the output from intermediate.int_apple_store__app_version_report (reporting_grain), emitting exactly one row per (source_relation, date_day, app_id, source_type, app_version).
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
business_logic: '- Drive the output from intermediate.int_apple_store__app_version_report (reporting_grain), emitting exactly one row per (source_relation, date_day, app_id, source_type, app_version).
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__app_version_report.sql` / `text`。

```text
LEFT JOIN app ON g.source_relation IS NOT DISTINCT FROM app.source_relation AND g.app_id IS NOT DISTINCT FROM app.app_id
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml`；SHA-256 `0546320393fa39035bd8afc85a91a28a2aedccc8bcd9f41662f8fb862b7f5be2`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__app_version_report.sql`；SHA-256 `92d385b5ca9e6368c72376c0eddccc816c026dc3af5dce071eb64f790ff783f5`。
- 023材料包：`records/023_packages/023_impl-019_apple_store__app_version_report.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引25，NULL 连接键。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
