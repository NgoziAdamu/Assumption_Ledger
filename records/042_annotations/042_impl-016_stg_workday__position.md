# 042 正式标注：impl-016_stg_workday__position

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**Intent Misreading**；把握高；1点。只能组合修复：否。023旧主要原因`C`仅存档。

## 详细发现

### 比较口径与原始数据

raw.person_contact_email_address由7284降至2448，少4836行；已回查85个事件及013/015记录，改动步骤和原因均未找到。不得编造是哪次run导致。当前stg_position直读position没有该变化；三个非staging表采用gold上游，不能把email原始减量直接计入本表CS误差。

直接raw逐表013核对：`[{"table": "position", "found_in_013": true, "different": false, "columns_types_equal": true, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/workday.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### validation_order

**Intent Misreading**；主要；把握高。

employee_type规则先检查原值枚举，再TRIM纠正；agent先TRIM再验证，使2个原值非法的记录被救回。规则已有可执行条件，按Intent而非解析Choice或Data。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-016_stg_workday__position.json` / `validation_order`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 2 | 0 | 2 | 0 |
| L1 | 2 | 0 | 2 | 0 |
| L2 | 2 | 0 | 2 | 0 |
| L3 | 2 | 0 | 2 | 0 |

L0减少：[2, 2]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。

```text
- name: employee_type
          data_type: VARCHAR
          validation_rules:
            - rule: "employee_type IS NULL OR employee_type IN ('Regular', 'Contingent', 'Intern', 'Contractor')"
              on_failure: nullify_field
            - rule: "employee_type = TRIM(employee_type)"
              on_failure: correct
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。

```text
- name: employee_type
          data_type: VARCHAR
          validation_rules:
            - rule: "employee_type IS NULL OR employee_type IN ('Regular', 'Contingent', 'Intern', 'Contractor')"
              on_failure: nullify_field
            - rule: "employee_type = TRIM(employee_type)"
              on_failure: correct
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/staging/stg_workday__position.sql` / `text`。

```text
TRIM(r.employee_type) NOT IN
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`；SHA-256 `8f0707fc595c6f2f1e46a1983436959278e10315cb723e975c2811858d737c91`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/staging/stg_workday__position.sql`；SHA-256 `e6a9659207c103c785eed0696c8411ef9d89d23dbaec4fa621ac372889c11528`。
- 023材料包：`records/023_packages/023_impl-016_stg_workday__position.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引4，校验次序。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
