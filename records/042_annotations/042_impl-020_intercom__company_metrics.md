# 042 正式标注：impl-020_intercom__company_metrics

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。

## 结论

主要原因：**Unstated Choice**；把握高；3点。只能组合修复：否。023旧主要原因`A`仅存档。

## 详细发现

### 比较口径与原始数据

原始数据变化在gold raw同样存在，包含本批两张staging直接源。按指定口径用agent留存raw并照常标注，列错位据此核查；benchmark加载原因是015推测，不归为agent自己改raw。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### contacts_total

**Unstated Choice**；并列；把握高。

contacts_total在无匹配聚合时agent补0，gold保留NULL；契约没有给该缺失场景的默认值。三点各减少2509格，行数不降，但仍同类并列主因，不是只能组合修复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-020_intercom__company_metrics.json` / `contacts_total`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 2509 | 2509 | 7527 | 5018 |
| L1 | 2509 | 2509 | 7527 | 5018 |
| L2 | 2509 | 2509 | 7527 | 5018 |
| L3 | 2509 | 2509 | 7527 | 5018 |

L0减少：[0, 2509]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml` / `text`。

```text
- name: contacts_total
          data_type: BIGINT
          description: "Total number of contacts associated with the company."
          tests: ["contacts_total >= 0"]
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/1.json` / event 1 / `message`。

```text
- name: contacts_total
          data_type: BIGINT
          description: "Total number of contacts associated with the company."
          tests: ["contacts_total >= 0"]
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/marts/intercom__company_metrics.sql` / `text`。

```text
coalesce(co.contacts_total,0)
```

### contacts_active_7d

**Unstated Choice**；并列；把握高。

contacts_active_7d在无匹配聚合时agent补0，gold保留NULL；契约没有给该缺失场景的默认值。三点各减少2509格，行数不降，但仍同类并列主因，不是只能组合修复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-020_intercom__company_metrics.json` / `contacts_active_7d`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 2509 | 2509 | 7527 | 5018 |
| L1 | 2509 | 2509 | 7527 | 5018 |
| L2 | 2509 | 2509 | 7527 | 5018 |
| L3 | 2509 | 2509 | 7527 | 5018 |

L0减少：[0, 2509]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml` / `text`。

```text
- name: contacts_active_7d
          data_type: BIGINT
          description: "Active contacts in the past 7 days."
          tests: ["contacts_active_7d >= 0"]
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/1.json` / event 1 / `message`。

```text
- name: contacts_active_7d
          data_type: BIGINT
          description: "Active contacts in the past 7 days."
          tests: ["contacts_active_7d >= 0"]
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/marts/intercom__company_metrics.sql` / `text`。

```text
coalesce(co.contacts_active_7d,0)
```

### contacts_active_30d

**Unstated Choice**；并列；把握高。

contacts_active_30d在无匹配聚合时agent补0，gold保留NULL；契约没有给该缺失场景的默认值。三点各减少2509格，行数不降，但仍同类并列主因，不是只能组合修复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-020_intercom__company_metrics.json` / `contacts_active_30d`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 2509 | 2509 | 7527 | 5018 |
| L1 | 2509 | 2509 | 7527 | 5018 |
| L2 | 2509 | 2509 | 7527 | 5018 |
| L3 | 2509 | 2509 | 7527 | 5018 |

L0减少：[0, 2509]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml` / `text`。

```text
- name: contacts_active_30d
          data_type: BIGINT
          description: "Active contacts in the past 30 days."
          tests: ["contacts_active_30d >= 0"]
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/1.json` / event 1 / `message`。

```text
- name: contacts_active_30d
          data_type: BIGINT
          description: "Active contacts in the past 30 days."
          tests: ["contacts_active_30d >= 0"]
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/marts/intercom__company_metrics.sql` / `text`。

```text
coalesce(co.contacts_active_30d,0)
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml`；SHA-256 `b19cdce65b55dd44086f5a7ef864055abfe48bd66f5d6f430785084ab3cd5314`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/marts/intercom__company_metrics.sql`；SHA-256 `8ac171989fee70519dd2ee0067250239ab50b0012dd313041c4185922e750863`。
- 023材料包：`records/023_packages/023_impl-020_intercom__company_metrics.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引30，contact 映射覆盖。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
