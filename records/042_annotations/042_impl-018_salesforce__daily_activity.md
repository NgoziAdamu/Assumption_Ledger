# 042 正式标注：impl-018_salesforce__daily_activity

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。

## 结论

主要原因：**Intent Misreading**；把握高；1点。只能组合修复：否。023旧主要原因`C`仅存档。

## 详细发现

### 比较口径与原始数据

013未发现raw结构/类型/行数变化；这项检查不被扩张为所有格子内容的字节等同。staging用agent留存raw，marts用gold上游。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### won_amount_null

**Intent Misreading**；主要；把握高。

契约仅在没有任何Won记录时补0；存在Won行但amount全NULL时SUM应为NULL。agent无条件COALESCE(sum,0)扩大补零范围。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_salesforce__daily_activity.json` / `won_amount_null`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 8 | 0 | 8 | 0 |
| L1 | 8 | 0 | 8 | 0 |
| L2 | 8 | 0 | 8 | 0 |
| L3 | 8 | 0 | 8 | 0 |

L0减少：[8, 8]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: opportunities_won_amount
        data_type: DECIMAL(38,0)
        description: Sum of amounts for opportunities with close_date on date_day and status Won, rounded to 0 decimals; zero when close_date records exist but none Won; null when no close_date records.
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: opportunities_won_amount
        data_type: DECIMAL(38,0)
        description: Sum of amounts for opportunities with close_date on date_day and status Won, rounded to 0 decimals; zero when close_date records exist but none Won; null when no close_date records.
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__daily_activity.sql` / `text`。

```text
coalesce(round(sum(amount) filter(where deal_status='Won')),0)
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__daily_activity.sql`；SHA-256 `c0b35be7574e7d0188bdc41738e1eec1183fd92be26051c5d28c50da6252f6c9`。
- 023材料包：`records/023_packages/023_impl-018_salesforce__daily_activity.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引16，Won 全 NULL 分组。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
