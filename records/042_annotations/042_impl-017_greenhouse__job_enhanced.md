# 042 正式标注：impl-017_greenhouse__job_enhanced

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。

## 结论

主要原因：**Intent Misreading**；把握高；3点。只能组合修复：否。023旧主要原因`C`仅存档。

## 详细发现

### 比较口径与原始数据

013/015的变更发生在scheduled_interview_snowflake，gold raw也有同样变化；本批七张staging的直接源不在变更清单，两个marts用gold上游。benchmark加载导致是015推测，非agent行为的独立证明；按用户指定口径照常标注。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/greenhouse.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-24 00:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-24'", "count": 0}]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### days_clock

**Intent Misreading**；主要；把握高。

days_since_created明定当前日期与created_at之间的天数；agent改用CURRENT_TIMESTAMP，改变时间范围，不是仅运行时点差异。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-017_greenhouse__job_enhanced.json` / `days_clock`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 1200 | 102 | 1333 | 133 |
| L1 | 1200 | 102 | 1333 | 133 |
| L2 | 1200 | 102 | 1333 | 133 |
| L3 | 1200 | 102 | 1333 | 133 |

L0减少：[1098, 1200]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml` / `text`。

```text
- name: days_since_created
        data_type: DOUBLE
        description: Days between the current date and created_at; updates daily and may be fractional
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/1.json` / event 1 / `message`。

```text
- name: days_since_created
        data_type: DOUBLE
        description: Days between the current date and created_at; updates daily and may be fractional
```

### prospect_cast

**Intent Misreading**；参与；把握高。

契约给出prospect = 'True'可执行比较；agent先转VARCHAR，BOOLEAN转为小写true后不等于True。按引擎字面效果遵从规则，不推测契约本意。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-017_greenhouse__job_enhanced.json` / `prospect_cast`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 1200 | 1200 | 1333 | 1293 |
| L1 | 1200 | 1200 | 1333 | 1293 |
| L2 | 1200 | 1200 | 1333 | 1293 |
| L3 | 1200 | 1200 | 1333 | 1293 |

L0减少：[0, 40]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml` / `text`。

```text
prospect equals the string ''True''. Notes: all comparisons are exact, case-sensitive.
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/1.json` / event 1 / `message`。

```text
prospect equals the string ''True''. Notes: all comparisons are exact, case-sensitive.
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/marts/greenhouse__job_enhanced.sql` / `text`。

```text
prospect::VARCHAR = 'True'
```

### ratio_zero_vs_null

**其他**；参与；把握高。

契约对缺失job-level计数补0，agent据此得到0比率；gold保留NULL计数导致93格不同。替换为gold表达式是诊断，不表示agent应违背计数默认。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-017_greenhouse__job_enhanced.json` / `ratio_zero_vs_null`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 1200 | 1200 | 1333 | 1240 |
| L1 | 1200 | 1200 | 1333 | 1240 |
| L2 | 1200 | 1200 | 1333 | 1240 |
| L3 | 1200 | 1200 | 1333 | 1240 |

L0减少：[0, 93]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml` / `text`。

```text
- name: application_to_interview_rate
        data_type: DOUBLE
        description: 'Percent: total interviews / total applications × 100; returns 0 if total applications is 0 or missing; no rounding'
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/1.json` / event 1 / `message`。

```text
- name: application_to_interview_rate
        data_type: DOUBLE
        description: 'Percent: total interviews / total applications × 100; returns 0 if total applications is 0 or missing; no rounding'
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/marts/greenhouse__job_enhanced.sql` / `text`。

```text
count_total_interviews * 100.0 / count_total_applications
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`；SHA-256 `f4a1c779c8359b7fd5d9c8cae9760669aceb5b35f661d0fab07d0bf376762e41`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/marts/greenhouse__job_enhanced.sql`；SHA-256 `3c26acfd5d6935a3967b3f8c69e5a8c264f706120026a39dc4f1400b5aa602fc`。
- 023材料包：`records/023_packages/023_impl-017_greenhouse__job_enhanced.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引15，prospect 类型比较。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
