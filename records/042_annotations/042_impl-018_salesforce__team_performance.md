# 042 正式标注：impl-018_salesforce__team_performance

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。

## 结论

主要原因：**Intent Misreading**；把握高；5点。只能组合修复：否。023旧主要原因`C`仅存档。

## 详细发现

### 比较口径与原始数据

013未发现raw结构/类型/行数变化；这项检查不被扩张为所有格子内容的字节等同。staging用agent留存raw，marts用gold上游。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### health_growth_null

**Intent Misreading**；主要；把握高。

Revenue growth贡献明定>10给20、>0给15、>=-10给10、否则5；agent将NULL growth补0，落10而不是else5，改变健康分。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_salesforce__team_performance.json` / `health_growth_null`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 496 | 292 | 1334 | 838 |
| L1 | 496 | 292 | 1334 | 838 |
| L2 | 496 | 292 | 1334 | 838 |
| L3 | 496 | 292 | 1334 | 838 |

L0减少：[204, 496]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
Revenue growth: 20 if > 10%, else 15 if > 0%, else 10 if ≥ -10%, else 5
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
Revenue growth: 20 if > 10%, else 15 if > 0%, else 10 if ≥ -10%, else 5
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql` / `text`。

```text
case when coalesce(revenue_growth_qoq_percentage,0)>10 then 20 when coalesce(revenue_growth_qoq_percentage,0)>0 then 15 when coalesce(revenue_growth_qoq_percentage,0)>=-10 then 10 else 5 end
```

### revenue_sum

**Unstated Choice**；参与；把握中。

team_total_revenue可从user_performance的total_won_amount或另算revenue_data的total_revenue_won取得；契约这里用revenue/won revenue描述但未点明取哪个已存在的量。两者均有业务读法，按材料未定选择。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_salesforce__team_performance.json` / `revenue_sum`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 496 | 496 | 1334 | 1062 |
| L1 | 496 | 496 | 1334 | 1062 |
| L2 | 496 | 496 | 1334 | 1062 |
| L3 | 496 | 496 | 1334 | 1062 |

L0减少：[0, 272]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: team_total_revenue
        data_type: DECIMAL(38,2)
        description: Total revenue won summed across team; currency formatted to two decimals; nulls ignored and result is null if all inputs are null.
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: team_total_revenue
        data_type: DECIMAL(38,2)
        description: Total revenue won summed across team; currency formatted to two decimals; nulls ignored and result is null if all inputs are null.
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql` / `text`。

```text
sum(total_revenue_won) as team_total_revenue
```

### revenue_avg

**Unstated Choice**；参与；把握中。

avg_revenue_per_member可从user_performance的total_won_amount或另算revenue_data的total_revenue_won取得；契约这里用revenue/won revenue描述但未点明取哪个已存在的量。两者均有业务读法，按材料未定选择。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_salesforce__team_performance.json` / `revenue_avg`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 496 | 496 | 1334 | 1042 |
| L1 | 496 | 496 | 1334 | 1042 |
| L2 | 496 | 496 | 1334 | 1042 |
| L3 | 496 | 496 | 1334 | 1042 |

L0减少：[0, 292]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: avg_revenue_per_member
        data_type: DOUBLE
        description: Average revenue won per user rounded to the nearest whole unit; excludes nulls and is null if no values.
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: avg_revenue_per_member
        data_type: DOUBLE
        description: Average revenue won per user rounded to the nearest whole unit; excludes nulls and is null if no values.
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql` / `text`。

```text
round(avg(total_revenue_won)) as avg_revenue_per_member
```

### revenue_top

**Intent Misreading**；参与；把握高。

top_revenue_performer明确按highest total won amount排名；agent按另一revenue_data聚合量排名。此处有明文，不把相邻sum/avg的歧义推广过来。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_salesforce__team_performance.json` / `revenue_top`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 496 | 496 | 1334 | 1064 |
| L1 | 496 | 496 | 1334 | 1064 |
| L2 | 496 | 496 | 1334 | 1064 |
| L3 | 496 | 496 | 1334 | 1064 |

L0减少：[0, 270]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
top_revenue_performer = the full_name of the member with the highest total won amount; members without a value are ranked last; ties are arbitrary
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
top_revenue_performer = the full_name of the member with the highest total won amount; members without a value are ranked last; ties are arbitrary
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql` / `text`。

```text
arg_max(full_name,total_revenue_won) filter(where total_revenue_won is not null)
```

### mask_top_win_rate_performer

**其他**；参与；把握高。

契约允许最高win rate的ties arbitrary；023_team_ties显示差异2组各有4个最高0候选，agent与gold均在其中。逐列双侧屏蔽只减少2格，作为Other参与因素，不虚称实际单改SQL。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用+新做；`records/042_checks/diagnostic_impl-018_salesforce__team_performance.json` / `mask_top_win_rate_performer`。双侧逐列屏蔽诊断（Other定位，非agent SQL修复）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 496 | 496 | 1334 | 1332 |
| L1 | 496 | 496 | 1334 | 1332 |
| L2 | 496 | 496 | 1334 | 1332 |
| L3 | 496 | 496 | 1334 | 1332 |

L0减少：[0, 2]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
top_win_rate_performer = the full_name of the member with the highest win rate percentage; members without a value are ranked last; ties are arbitrary
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
top_win_rate_performer = the full_name of the member with the highest win rate percentage; members without a value are ranked last; ties are arbitrary
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql`；SHA-256 `f0fcb6526b209972c74c557815cdae25a35354208eae21ea4c0cf1b09a1336e9`。
- 023材料包：`records/023_packages/023_impl-018_salesforce__team_performance.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引17，增长率 NULL。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
