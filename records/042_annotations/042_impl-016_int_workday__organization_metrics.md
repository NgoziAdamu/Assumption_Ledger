# 042 正式标注：impl-016_int_workday__organization_metrics

## 任务

按冻结v3.2第3～8节逐点重标；层：intermediate。

## 结论

主要原因：**Intent Misreading**；把握高；1点。只能组合修复：否。023旧主要原因`C`仅存档。

## 详细发现

### 比较口径与原始数据

raw.person_contact_email_address由7284降至2448，少4836行；已回查85个事件及013/015记录，改动步骤和原因均未找到。不得编造是哪次run导致。当前stg_position直读position没有该变化；三个非staging表采用gold上游，不能把email原始减量直接计入本表CS误差。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 5}]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### tenure_all_assignments

**Intent Misreading**；主要；把握高。

契约把avg_tenure_days列在all assignments的mobility段；agent从仅当前任职的current_stats取平均。本数据当前任职0不改变历史任职应纳入的明文要求。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-016_int_workday__organization_metrics.json` / `tenure_all_assignments`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 117 | 0 | 117 | 0 |
| L1 | 117 | 0 | 117 | 0 |
| L2 | 117 | 0 | 117 | 0 |
| L3 | 117 | 0 | 117 | 0 |

L0减少：[117, 117]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。

```text
Derive mobility from all assignments (historical and current), grouped by organization and source: new_hires_last_year counts distinct workers whose assignment started in the past year; departures_last_year counts distinct workers whose assignment ended in the past year; internal_transfers_in counts distinct workers who started in the past year and had any earlier assignment in a different organization within the same source; internal_transfers_out counts distinct workers who ended in the past year and had any later assignment in a different organization within the same source; avg_tenure_days averages days between start and end (or start and today if still active). Derive compensation distribution from current assignments: count distinct compensation grades, job families, and job family groups; most_common_grade is the most frequent comp
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。

```text
Derive mobility from all assignments (historical and current), grouped by organization and source: new_hires_last_year counts distinct workers whose assignment started in the past year; departures_last_year counts distinct workers whose assignment ended in the past year; internal_transfers_in counts distinct workers who started in the past year and had any earlier assignment in a different organization within the same source; internal_transfers_out counts distinct workers who ended in the past year and had any later assignment in a different organization within the same source; avg_tenure_days averages days between start and end (or start and today if still active). Derive compensation distribution from current assignments: count distinct compensation grades, job families, and job family groups; most_common_grade is the most frequent comp
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/intermediate/int_workday__organization_metrics.sql` / `text`。

```text
coalesce(c.avg_tenure_days,0)::DOUBLE avg_tenure_days
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`；SHA-256 `8f0707fc595c6f2f1e46a1983436959278e10315cb723e975c2811858d737c91`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/intermediate/int_workday__organization_metrics.sql`；SHA-256 `48a68b720ccfe1acaac3c2ba6ec665c87c317b28e32d769df198341174bc8bc9`。
- 023材料包：`records/023_packages/023_impl-016_int_workday__organization_metrics.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引3，当前与历史。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
