# 042 正式标注：impl-018_stg_salesforce__user

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**其他**；把握高；3点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

013未发现raw结构/类型/行数变化；这项检查不被扩张为所有格子内容的字节等同。staging用agent留存raw，marts用gold上游。

直接raw逐表013核对：`[{"table": "user", "found_in_013": true, "different": false, "columns_types_equal": true, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### email_filter

**其他**；主要；把握高。

邮箱格式非法应delete_row，agent实施而gold保留5条。

是否说出：第2档——交付物里只有通用说明。最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__user.json` / `email_filter`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 2 | 189 | 54 |
| L1 | 7 | 2 | 189 | 54 |
| L2 | 7 | 2 | 189 | 54 |
| L3 | 7 | 2 | 189 | 54 |

L0减少：[5, 135]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: email
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "email IS NOT NULL"
              on_failure: delete_row
            - rule: "email = LOWER(TRIM(email))"
              on_failure: correct
            - rule: "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
              on_failure: delete_row
            - rule: "LENGTH(email) <= 255"
              on_failure: delete_row
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: email
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "email IS NOT NULL"
              on_failure: delete_row
            - rule: "email = LOWER(TRIM(email))"
              on_failure: correct
            - rule: "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
              on_failure: delete_row
            - rule: "LENGTH(email) <= 255"
              on_failure: delete_row
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json` / event 99 / `args.final_thought`。

```text
严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空；规范化处理保留可用记录。
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__user.sql` / `text`。

```text
and regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
```

### email_length

**其他**；参与；把握高。

邮箱长度上限255并要求delete_row，agent实施而gold保留1条。

是否说出：第2档——交付物里只有通用说明。最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-018_stg_salesforce__user.json` / `email_length`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 6 | 189 | 162 |
| L1 | 7 | 6 | 189 | 162 |
| L2 | 7 | 6 | 189 | 162 |
| L3 | 7 | 6 | 189 | 162 |

L0减少：[1, 27]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: email
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "email IS NOT NULL"
              on_failure: delete_row
            - rule: "email = LOWER(TRIM(email))"
              on_failure: correct
            - rule: "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
              on_failure: delete_row
            - rule: "LENGTH(email) <= 255"
              on_failure: delete_row
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: email
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "email IS NOT NULL"
              on_failure: delete_row
            - rule: "email = LOWER(TRIM(email))"
              on_failure: correct
            - rule: "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
              on_failure: delete_row
            - rule: "LENGTH(email) <= 255"
              on_failure: delete_row
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json` / event 99 / `args.final_thought`。

```text
严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空；规范化处理保留可用记录。
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__user.sql` / `text`。

```text
and length(lower(trim(email))) <= 255
```

### email_not_null

**其他**；非原因；把握高。

email要求not_null；此单点被其他邮箱过滤覆盖，解除非空约束不改善，不能算参与。

是否说出：第2档——交付物里只有通用说明。最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-018_stg_salesforce__user.json` / `email_not_null`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 7 | 189 | 189 |
| L1 | 7 | 7 | 189 | 189 |
| L2 | 7 | 7 | 189 | 189 |
| L3 | 7 | 7 | 189 | 189 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: email
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "email IS NOT NULL"
              on_failure: delete_row
            - rule: "email = LOWER(TRIM(email))"
              on_failure: correct
            - rule: "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
              on_failure: delete_row
            - rule: "LENGTH(email) <= 255"
              on_failure: delete_row
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: email
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "email IS NOT NULL"
              on_failure: delete_row
            - rule: "email = LOWER(TRIM(email))"
              on_failure: correct
            - rule: "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
              on_failure: delete_row
            - rule: "LENGTH(email) <= 255"
              on_failure: delete_row
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json` / event 99 / `args.final_thought`。

```text
严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空；规范化处理保留可用记录。
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__user.sql` / `text`。

```text
and email is not null
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__user.sql`；SHA-256 `cca4c7cf2ff74050466df829d496915608f94ccafcc2b33b9672a760c9b82cc7`。
- 023材料包：`records/023_packages/023_impl-018_stg_salesforce__user.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引24，各过滤条件。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
