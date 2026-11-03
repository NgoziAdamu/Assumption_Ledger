# 042 正式标注：impl-020_stg_intercom__contact_history

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**其他**；把握高；1点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

原始数据变化在gold raw同样存在，包含本批两张staging直接源。按指定口径用agent留存raw并照常标注，列错位据此核查；benchmark加载原因是015推测，不归为agent自己改raw。

直接raw逐表013核对：`[{"table": "contact_history_data", "found_in_013": true, "different": true, "columns_types_equal": false, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### phone_gold_regex

**其他**；主要；把握高。

契约给E.164格式，agent去分隔符、保留/补+并验证；1079个有效号码满足明文，gold双反斜杠模式失配成NULL。非任意解析选择。

是否说出：第2档——交付物里只有通用说明。最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-020_stg_intercom__contact_history.json` / `phone_gold_regex`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 1079 | 0 | 1079 | 0 |
| L1 | 1079 | 0 | 1079 | 0 |
| L2 | 1079 | 0 | 1079 | 0 |
| L3 | 1079 | 0 | 1079 | 0 |

L0减少：[1079, 1079]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml` / `text`。

```text
- name: phone
          data_type: VARCHAR
          validation_rules:
            - rule: "Normalize to E.164 where deterministically possible"
              on_failure: correct
            - rule: "phone IS NULL OR phone matches E.164 (^[+][1-9][0-9]{1,14}$)"
              on_failure: nullify_field
      row_filters:
        - rule: "Retain record unless _fivetran_active is explicitly false after type coercion (null or missing treated as active)"
          on_failure: delete_row
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/1.json` / event 1 / `message`。

```text
- name: phone
          data_type: VARCHAR
          validation_rules:
            - rule: "Normalize to E.164 where deterministically possible"
              on_failure: correct
            - rule: "phone IS NULL OR phone matches E.164 (^[+][1-9][0-9]{1,14}$)"
              on_failure: nullify_field
      row_filters:
        - rule: "Retain record unless _fivetran_active is explicitly false after type coercion (null or missing treated as active)"
          on_failure: delete_row
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/61.json` / event 61 / `args.final_thought`。

```text
电话标准化/无效字段置空
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/staging/stg_intercom__contact_history.sql` / `text`。

```text
regexp_matches(normalized_phone, '^\+[1-9][0-9]{1,14}$')
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml`；SHA-256 `b19cdce65b55dd44086f5a7ef864055abfe48bd66f5d6f430785084ab3cd5314`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/staging/stg_intercom__contact_history.sql`；SHA-256 `4fb7b8075a4174b44c4e5ba50b573400700d9803626cfb0a3bbba63a51e5c705`。
- 023材料包：`records/023_packages/023_impl-020_stg_intercom__contact_history.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引31，显式 phone 规则与 gold regexp。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
