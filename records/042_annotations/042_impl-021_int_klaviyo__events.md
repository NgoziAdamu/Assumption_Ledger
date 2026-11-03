# 042 正式标注：impl-021_int_klaviyo__events

## 任务

按冻结v3.2第3～8节逐点重标；层：intermediate。

## 结论

主要原因：**其他**；把握中；2点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

五张raw均有013/015记录的变化，gold raw也包含变化；按指定口径用agent留存raw标五张staging，intermediate用gold上游。ID稀疏是实际可见事实，其形成原因未查证，不能从稀疏反推agent删raw。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/klaviyo.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。

两列均Other；双侧屏蔽inter_event_minutes减少1行2格，session_seq减少0行1格，定位主因前者。诊断减量非可执行修复的因果收益，类别在同类候选下不受此限制影响，把握中。

### mask_inter_event_minutes

**其他**；主要；把握高。

契约允许同occurred_at的prev_event任意次序，两个并列事件的分钟间隔分别不同；其余字段诊断一致。042双侧逐列屏蔽用于定位Other，不是实际修复SQL。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用+新做；`records/042_checks/diagnostic_impl-021_int_klaviyo__events.json` / `mask_inter_event_minutes`。双侧逐列屏蔽诊断（Other定位，非agent SQL修复）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 2 | 1 | 3 | 1 |
| L1 | 2 | 1 | 3 | 1 |
| L2 | 2 | 1 | 3 | 1 |
| L3 | 2 | 1 | 3 | 1 |

L0减少：[1, 2]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml` / `text`。

```text
- name: inter_event_minutes
        data_type: BIGINT
        description: Rounded difference in minutes between prev_event_at and occurred_at; NULL when prev_event_at is NULL
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/1.json` / event 1 / `message`。

```text
- name: inter_event_minutes
        data_type: BIGINT
        description: Rounded difference in minutes between prev_event_at and occurred_at; NULL when prev_event_at is NULL
```

### mask_session_seq

**其他**；参与；把握高。

契约明定session_seq从1开始，首事件NULL prev_event时增加；agent实现，gold有session_seq=0。042双侧逐列屏蔽用于定位Other，不是实际修复SQL。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用+新做；`records/042_checks/diagnostic_impl-021_int_klaviyo__events.json` / `mask_session_seq`。双侧逐列屏蔽诊断（Other定位，非agent SQL修复）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 2 | 2 | 3 | 2 |
| L1 | 2 | 2 | 3 | 2 |
| L2 | 2 | 2 | 3 | 2 |
| L3 | 2 | 2 | 3 | 2 |

L0减少：[0, 1]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml` / `text`。

```text
- name: session_seq
        data_type: HUGEINT
        description: Running session counter per person ordered by occurred_at; starts at 1 and increments when the gap exceeds 30 minutes; ties follow engine-defined order
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/1.json` / event 1 / `message`。

```text
- name: session_seq
        data_type: HUGEINT
        description: Running session counter per person ordered by occurred_at; starts at 1 and increments when the gap exceeds 30 minutes; ties follow engine-defined order
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml`；SHA-256 `db04fb84955b6385dd63b72bdf7aae27ac9f612a685f938eabf7051f12cd675f`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/intermediate/int_klaviyo__events.sql`；SHA-256 `e2b24ec5b4a45ac5f486543e23c597a716edd332394b23d947de7b963f17ecdd`。
- 023材料包：`records/023_packages/023_impl-021_int_klaviyo__events.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：2条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引33，tied 窗口诊断。
- 查询：`records/023_queries.json` 数组索引34，gold session 起点。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
