# 042 正式标注：impl-020_int_intercom__conversation_part_aggregates

## 任务

按冻结v3.2第3～8节逐点重标；层：intermediate。

## 结论

主要原因：**Data Misconception**；把握中；1点。只能组合修复：否。023旧主要原因`U`仅存档。

## 详细发现

### 比较口径与原始数据

原始数据变化在gold raw同样存在，包含本批两张staging直接源。按指定口径用agent留存raw并照常标注，列错位据此核查；benchmark加载原因是015推测，不归为agent自己改raw。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### conversation_coverage

**Data Misconception**；主要；把握中。

P：每个conversation至少有一条可连接的part，所以以part聚合为基表足以覆盖所有对话。契约For each conversation但没有指定LEFT JOIN算法；缺的是覆盖事实。023在agent可见库核实6703对话中5726个无匹配part；CS换gold上游时6703个全部无匹配，导致全表消失。以conversation为基表覆盖修复清零。

P：每个conversation至少有一条可连接的part。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：否。只看见相关字段/样例，未找到足以定下本点P的全量唯一性或覆盖核实出现在轨迹；不能用本次查询反填证据在场。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-020_int_intercom__conversation_part_aggregates.json` / `conversation_coverage`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 6703 | 0 | 26812 | 0 |
| L1 | 6703 | 0 | 26812 | 0 |
| L2 | 6703 | 0 | 26812 | 0 |
| L3 | 6703 | 0 | 26812 | 0 |

L0减少：[6703, 26812]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml` / `text`。

```text
For each conversation, compute counts of parts, assignments, and reopen events.
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/1.json` / event 1 / `message`。

```text
For each conversation, compute counts of parts, assignments, and reopen events.
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/intermediate/int_intercom__conversation_part_aggregates.sql` / `text`。

```text
from rollup r join staging.stg_intercom__conversation_history c on r.conversation_id=c.conversation_id
```

### 排除的旧控制/混合补丁

- `records/023_reruns_impl-020_int_intercom__conversation_part_aggregates.json#left_conversation`：改为从part出发LEFT JOIN仍不能覆盖无part的conversation；不是覆盖前提的有效修复，以conversation_coverage代替。

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml`；SHA-256 `b19cdce65b55dd44086f5a7ef864055abfe48bd66f5d6f430785084ab3cd5314`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/intermediate/int_intercom__conversation_part_aggregates.sql`；SHA-256 `20c9d50c5125f7db529695fb5fba8fb4fde3d634c4f31c70deff77d3c899e0a1`。
- 023材料包：`records/023_packages/023_impl-020_int_intercom__conversation_part_aggregates.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：2条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引28，agent 可见连接覆盖。
- 查询：`records/023_queries.json` 数组索引29，CS 连接覆盖。

## 不确定或没查到的（含规则问题）

026的020-5提出Intent/Data边界：For each conversation规定输出范围但未规定连接算法。本轮按P“每个对话都有part”的可核实覆盖事实归Data（手册第4节也以此为例），而非从gold的LEFT JOIN逆推Intent；把握中。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
