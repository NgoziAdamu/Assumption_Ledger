# 042 正式标注：impl-019_apple_store__territory_report

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。

## 结论

主要原因：**Unstated Choice**；把握高；9点。只能组合修复：否。023旧主要原因`A`仅存档。

## 详细发现

### 比较口径与原始数据

原始session相关变化在gold raw同样存在；按015结论及本次要求照常标注，staging仍使用agent留存raw。benchmark加载原因仅记为推测；两个marts按CS取gold上游。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/apple_store.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### join_ses

**Unstated Choice**；主要；把握高。

ses来源的连接使用IS NOT DISTINCT FROM，gold用普通等号；契约指定连接键但未规定NULL键相互匹配与否。NULL-safe键是未定选择，不从gold做法推出数据事实。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__territory_report.json` / `join_ses`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 12 | 1 | 24 | 2 |
| L1 | 12 | 1 | 24 | 2 |
| L2 | 12 | 1 | 24 | 2 |
| L3 | 12 | 1 | 24 | 2 |

L0减少：[11, 22]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory).
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory).
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql` / `text`。

```text
LEFT JOIN ses ON g.source_relation IS NOT DISTINCT FROM ses.source_relation AND g.date_day IS NOT DISTINCT FROM ses.date_day AND g.app_id IS NOT DISTINCT FROM ses.app_id AND g.source_type IS NOT DISTINCT FROM ses.source_type AND g.territory IS NOT DISTINCT FROM ses.territory
```

### join_ip

**Unstated Choice**；非原因；把握高。

ip来源的连接使用IS NOT DISTINCT FROM，gold用普通等号；契约指定连接键但未规定NULL键相互匹配与否。NULL-safe键是未定选择，不从gold做法推出数据事实。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__territory_report.json` / `join_ip`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 12 | 12 | 24 | 24 |
| L1 | 12 | 12 | 24 | 24 |
| L2 | 12 | 12 | 24 | 24 |
| L3 | 12 | 12 | 24 | 24 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory).
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory).
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql` / `text`。

```text
LEFT JOIN ip ON g.source_relation IS NOT DISTINCT FROM ip.source_relation AND g.date_day IS NOT DISTINCT FROM ip.date_day AND g.app_id IS NOT DISTINCT FROM ip.app_id AND g.source_type IS NOT DISTINCT FROM ip.source_type AND g.territory IS NOT DISTINCT FROM ip.territory
```

### join_dl

**Unstated Choice**；参与；把握高。

dl来源的连接使用IS NOT DISTINCT FROM，gold用普通等号；契约指定连接键但未规定NULL键相互匹配与否。NULL-safe键是未定选择，不从gold做法推出数据事实。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__territory_report.json` / `join_dl`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 12 | 11 | 24 | 22 |
| L1 | 12 | 11 | 24 | 22 |
| L2 | 12 | 11 | 24 | 22 |
| L3 | 12 | 11 | 24 | 22 |

L0减少：[1, 2]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory).
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory).
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql` / `text`。

```text
LEFT JOIN dl ON g.source_relation IS NOT DISTINCT FROM dl.source_relation AND g.date_day IS NOT DISTINCT FROM dl.date_day AND g.app_id IS NOT DISTINCT FROM dl.app_id AND g.source_type IS NOT DISTINCT FROM dl.source_type AND g.territory IS NOT DISTINCT FROM dl.territory
```

### join_ins

**Unstated Choice**；非原因；把握高。

ins来源的连接使用IS NOT DISTINCT FROM，gold用普通等号；契约指定连接键但未规定NULL键相互匹配与否。NULL-safe键是未定选择，不从gold做法推出数据事实。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__territory_report.json` / `join_ins`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 12 | 12 | 24 | 24 |
| L1 | 12 | 12 | 24 | 24 |
| L2 | 12 | 12 | 24 | 24 |
| L3 | 12 | 12 | 24 | 24 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory).
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory).
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql` / `text`。

```text
LEFT JOIN ins ON g.source_relation IS NOT DISTINCT FROM ins.source_relation AND g.date_day IS NOT DISTINCT FROM ins.date_day AND g.app_id IS NOT DISTINCT FROM ins.app_id AND g.source_type IS NOT DISTINCT FROM ins.source_type AND g.territory IS NOT DISTINCT FROM ins.territory
```

### join_app

**Unstated Choice**；非原因；把握高。

app来源的连接使用IS NOT DISTINCT FROM，gold用普通等号；契约指定连接键但未规定NULL键相互匹配与否。NULL-safe键是未定选择，不从gold做法推出数据事实。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__territory_report.json` / `join_app`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 12 | 12 | 24 | 24 |
| L1 | 12 | 12 | 24 | 24 |
| L2 | 12 | 12 | 24 | 24 |
| L3 | 12 | 12 | 24 | 24 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory).
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory).
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql` / `text`。

```text
LEFT JOIN app ON g.source_relation IS NOT DISTINCT FROM app.source_relation AND g.app_id IS NOT DISTINCT FROM app.app_id
```

### aggregate_ip

**Intent Misreading**；非原因；把握高。

契约明确不在此模型聚合、重复组合传播；agent预聚合ip上游。去掉该处聚合单改无收益，保留为未确立前提但非判错原因，不混入参与统计。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__territory_report.json` / `aggregate_ip`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 12 | 12 | 24 | 24 |
| L1 | 12 | 12 | 24 | 24 |
| L2 | 12 | 12 | 24 | 24 |
| L3 | 12 | 12 | 24 | 24 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
No aggregation or sorting is applied; base rows are preserved and any duplicates in joined sources will propagate. String casing and spacing are unchanged, and date_day is not truncated or timezone-adjusted.'
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
No aggregation or sorting is applied; base rows are preserved and any duplicates in joined sources will propagate. String casing and spacing are unchanged, and date_day is not truncated or timezone-adjusted.'
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql` / `text`。

```text
ip AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(impressions) AS impressions, SUM(impressions_unique_device) AS impressions_unique_device, SUM(page_views) AS page_views, SUM(page_views_unique_device) AS page_views_unique_device FROM intermediate.int_apple_store__territory_impressions_page_views GROUP BY source_relation, date_day, app_id, source_type, territory),
```

### aggregate_dl

**Intent Misreading**；非原因；把握高。

契约明确不在此模型聚合、重复组合传播；agent预聚合dl上游。去掉该处聚合单改无收益，保留为未确立前提但非判错原因，不混入参与统计。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__territory_report.json` / `aggregate_dl`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 12 | 12 | 24 | 24 |
| L1 | 12 | 12 | 24 | 24 |
| L2 | 12 | 12 | 24 | 24 |
| L3 | 12 | 12 | 24 | 24 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
No aggregation or sorting is applied; base rows are preserved and any duplicates in joined sources will propagate. String casing and spacing are unchanged, and date_day is not truncated or timezone-adjusted.'
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
No aggregation or sorting is applied; base rows are preserved and any duplicates in joined sources will propagate. String casing and spacing are unchanged, and date_day is not truncated or timezone-adjusted.'
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql` / `text`。

```text
dl AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(first_time_downloads) AS first_time_downloads, SUM(redownloads) AS redownloads, SUM(total_downloads) AS total_downloads FROM intermediate.int_apple_store__territory_downloads_daily GROUP BY source_relation, date_day, app_id, source_type, territory),
```

### aggregate_ins

**Intent Misreading**；非原因；把握高。

契约明确不在此模型聚合、重复组合传播；agent预聚合ins上游。去掉该处聚合单改无收益，保留为未确立前提但非判错原因，不混入参与统计。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__territory_report.json` / `aggregate_ins`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 12 | 12 | 24 | 24 |
| L1 | 12 | 12 | 24 | 24 |
| L2 | 12 | 12 | 24 | 24 |
| L3 | 12 | 12 | 24 | 24 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
No aggregation or sorting is applied; base rows are preserved and any duplicates in joined sources will propagate. String casing and spacing are unchanged, and date_day is not truncated or timezone-adjusted.'
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
No aggregation or sorting is applied; base rows are preserved and any duplicates in joined sources will propagate. String casing and spacing are unchanged, and date_day is not truncated or timezone-adjusted.'
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql` / `text`。

```text
ins AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(deletions) AS deletions, SUM(installations) AS installations FROM intermediate.int_apple_store__territory_install_deletions GROUP BY source_relation, date_day, app_id, source_type, territory),
```

### aggregate_ses

**Intent Misreading**；非原因；把握高。

契约明确不在此模型聚合、重复组合传播；agent预聚合ses上游。去掉该处聚合单改无收益，保留为未确立前提但非判错原因，不混入参与统计。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_apple_store__territory_report.json` / `aggregate_ses`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 12 | 12 | 24 | 24 |
| L1 | 12 | 12 | 24 | 24 |
| L2 | 12 | 12 | 24 | 24 |
| L3 | 12 | 12 | 24 | 24 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
No aggregation or sorting is applied; base rows are preserved and any duplicates in joined sources will propagate. String casing and spacing are unchanged, and date_day is not truncated or timezone-adjusted.'
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
No aggregation or sorting is applied; base rows are preserved and any duplicates in joined sources will propagate. String casing and spacing are unchanged, and date_day is not truncated or timezone-adjusted.'
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql` / `text`。

```text
ses AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(active_devices) AS active_devices, SUM(sessions) AS sessions FROM intermediate.int_apple_store__territory_sessions_activity GROUP BY source_relation, date_day, app_id, source_type, territory),
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml`；SHA-256 `0546320393fa39035bd8afc85a91a28a2aedccc8bcd9f41662f8fb862b7f5be2`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql`；SHA-256 `06fdff20044f5fd61c0f5030c2cd3871a147abb4974c4d1ceea3e2ccd7d5653e`。
- 023材料包：`records/023_packages/023_impl-019_apple_store__territory_report.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引26，NULL 连接键。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
