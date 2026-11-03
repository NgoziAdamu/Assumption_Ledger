# 042 正式标注：impl-018_stg_salesforce__task

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**其他**；把握高；1点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

013未发现raw结构/类型/行数变化；这项检查不被扩张为所有格子内容的字节等同。staging用agent留存raw，marts用gold上游。

直接raw逐表013核对：`[{"table": "task", "found_in_013": true, "different": false, "columns_types_equal": true, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### status_filter

**其他**；主要；把握高。

契约列举task status合法值并要求非法值delete_row；agent执行，gold保留2条非法值。

是否说出：第2档——交付物里只有通用说明。最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__task.json` / `status_filter`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 2 | 0 | 32 | 0 |
| L1 | 2 | 0 | 32 | 0 |
| L2 | 2 | 0 | 32 | 0 |
| L3 | 2 | 0 | 32 | 0 |

L0减少：[2, 32]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: status
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "status IS NOT NULL"
              on_failure: delete_row
            - rule: "status IN ('Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred')"
              on_failure: delete_row
            - rule: "status = TRIM(status)"
              on_failure: correct
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: status
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "status IS NOT NULL"
              on_failure: delete_row
            - rule: "status IN ('Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred')"
              on_failure: delete_row
            - rule: "status = TRIM(status)"
              on_failure: correct
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json` / event 99 / `args.final_thought`。

```text
严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空；规范化处理保留可用记录。
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__task.sql` / `text`。

```text
and trim(status) in ('Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred')
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__task.sql`；SHA-256 `c8b08eb610b74932ac7ef89b47969b0690b0730f0b75de7d17c30233e3144d5c`。
- 023材料包：`records/023_packages/023_impl-018_stg_salesforce__task.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引23，status 删除条件。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
