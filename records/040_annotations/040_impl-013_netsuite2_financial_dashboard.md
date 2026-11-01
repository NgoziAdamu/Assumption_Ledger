# 040 正式标注：impl-013_netsuite2_financial_dashboard

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。022旧主要原因仅原样存档为 `D`，不作为新类别依据。

## 结论

主要原因：**Quiet Downgrade**；把握高；共5个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### volatility

主要；**Quiet Downgrade**；把握高。

标准差用overall_financial_health_score*0占位，不是要求的波动率计算；没有agent根据单观测合理选择总体标准差的记录。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。finish只有“高阶指标受模拟数据/合同指定占位日期及字段可用性影响”，没有说明本处用常量/透传代替计算；该句并非本类省略计算的披露。event1已有指标定义，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 0 | 13 | 0 |
| L1 | 13 | 0 | 13 | 0 |
| L2 | 13 | 0 | 13 | 0 |
| L3 | 13 | 0 | 13 | 0 |



来源：`records/022_reruns_impl-013_netsuite2_financial_dashboard.json` / `volatility`。L0减少13行、13格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

avg_financial_health is the average of overall_financial_health_score; financial_health_volatility is its standard deviation.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

avg_financial_health is the average of overall_financial_health_score; financial_health_volatility is its standard deviation.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_financial_dashboard.sql` / `text`（sql；普通SQL表达式不是披露）

```text

overall_financial_health_score*0 financial_health_volatility

```

### passthrough_avg_financial_health

非原因；**Quiet Downgrade**；把握高。

要求按subsidiary汇总平均，agent直接透传本行值；单观测组可能恰好相同。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。finish只有“高阶指标受模拟数据/合同指定占位日期及字段可用性影响”，没有说明本处用常量/透传代替计算；该句并非本类省略计算的披露。event1已有指标定义，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 13 | 13 | 13 |
| L1 | 13 | 13 | 13 | 13 |
| L2 | 13 | 13 | 13 | 13 |
| L3 | 13 | 13 | 13 | 13 |



来源：`records/040_checks/supplement_extra_impl-013_netsuite2_financial_dashboard.json` / `passthrough_avg_financial_health`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: avg_financial_health
        data_type: DOUBLE
        description: Average of overall_financial_health_score across fk rows per subsidiary; NULLs ignored

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: avg_financial_health
        data_type: DOUBLE
        description: Average of overall_financial_health_score across fk rows per subsidiary; NULLs ignored

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_financial_dashboard.sql` / `text`（sql；普通SQL表达式不是披露）

```text

overall_financial_health_score avg_financial_health

```

### passthrough_avg_net_margin

非原因；**Quiet Downgrade**；把握高。

要求按subsidiary汇总平均，agent直接透传本行值；单观测组可能恰好相同。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。finish只有“高阶指标受模拟数据/合同指定占位日期及字段可用性影响”，没有说明本处用常量/透传代替计算；该句并非本类省略计算的披露。event1已有指标定义，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 13 | 13 | 13 |
| L1 | 13 | 13 | 13 | 13 |
| L2 | 13 | 13 | 13 | 13 |
| L3 | 13 | 13 | 13 | 13 |



来源：`records/040_checks/supplement_extra_impl-013_netsuite2_financial_dashboard.json` / `passthrough_avg_net_margin`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: avg_net_margin
        data_type: DOUBLE
        description: Average of net_profit_margin across fk rows per subsidiary; NULLs ignored

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: avg_net_margin
        data_type: DOUBLE
        description: Average of net_profit_margin across fk rows per subsidiary; NULLs ignored

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_financial_dashboard.sql` / `text`（sql；普通SQL表达式不是披露）

```text

net_profit_margin avg_net_margin

```

### passthrough_avg_current_ratio

非原因；**Quiet Downgrade**；把握高。

要求按subsidiary汇总平均，agent直接透传本行值；单观测组可能恰好相同。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。finish只有“高阶指标受模拟数据/合同指定占位日期及字段可用性影响”，没有说明本处用常量/透传代替计算；该句并非本类省略计算的披露。event1已有指标定义，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 13 | 13 | 13 |
| L1 | 13 | 13 | 13 | 13 |
| L2 | 13 | 13 | 13 | 13 |
| L3 | 13 | 13 | 13 | 13 |



来源：`records/040_checks/supplement_extra_impl-013_netsuite2_financial_dashboard.json` / `passthrough_avg_current_ratio`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: avg_current_ratio
        data_type: DOUBLE
        description: Average of current_ratio across fk rows per subsidiary; NULLs ignored

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: avg_current_ratio
        data_type: DOUBLE
        description: Average of current_ratio across fk rows per subsidiary; NULLs ignored

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_financial_dashboard.sql` / `text`（sql；普通SQL表达式不是披露）

```text

current_ratio avg_current_ratio

```

### improvement_placeholder

非原因；**Quiet Downgrade**；把握高。

改善建议固定Maintain Current Performance，未执行流动性/利润/逾期分支。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。finish只有“高阶指标受模拟数据/合同指定占位日期及字段可用性影响”，没有说明本处用常量/透传代替计算；该句并非本类省略计算的披露。event1已有指标定义，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 13 | 13 | 13 |
| L1 | 13 | 13 | 13 | 13 |
| L2 | 13 | 13 | 13 | 13 |
| L3 | 13 | 13 | 13 | 13 |



来源：`records/040_checks/supplement_extra_impl-013_netsuite2_financial_dashboard.json` / `improvement_placeholder`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: improvement_recommendation
        data_type: VARCHAR
        description: 'Recommendation per priority: Ops & Liquidity, Working Capital, Cost, Collections, else Maintain'

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: improvement_recommendation
        data_type: VARCHAR
        description: 'Recommendation per priority: Ops & Liquidity, Working Capital, Cost, Collections, else Maintain'

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_financial_dashboard.sql` / `text`（sql；普通SQL表达式不是披露）

```text

'Maintain Current Performance' improvement_recommendation

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`；行段[[2870, 3006]]；SHA-256 `c152a30bcad4df785d3f0ea461101eb8a4b36e4fa06059739a80e04998c4150f`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_financial_dashboard.sql`；SHA-256 `f2191a6d461f047c0f26491cea314514caf3a4e888b5ea2cb637ead2dd2d17f0`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`；材料包：`records/022_packages/022_impl-013_netsuite2_financial_dashboard.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 2}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共2条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 21；上游可见行数；失败=True。

  - `records/022_queries_retry.json` / index 15；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
