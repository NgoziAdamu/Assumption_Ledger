# 040 正式标注：impl-013_netsuite2_vendor_risk_analysis

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。022旧主要原因仅原样存档为 `D`，不作为新类别依据。

## 结论

主要原因：**Quiet Downgrade**；把握高；共3个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### contract_recommendation

主要；**Quiet Downgrade**；把握高。

合同建议固定Standard purchase agreement，省去supplier_tier条件分支。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。finish只有“高阶指标受模拟数据/合同指定占位日期及字段可用性影响”，没有说明本处用常量/透传代替计算；该句并非本类省略计算的披露。event1已有指标定义，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 52 | 0 | 52 | 0 |
| L1 | 52 | 0 | 52 | 0 |
| L2 | 52 | 0 | 52 | 0 |
| L3 | 52 | 0 | 52 | 0 |



来源：`records/022_reruns_impl-013_netsuite2_vendor_risk_analysis.json` / `contract_recommendation`。L0减少52行、52格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

contract_recommendation by supplier_tier: Strategic Partner → Long-term strategic contract with SLA; Key Supplier → Multi-year contract with performance metrics; Important Supplier → Annual contract with review clause; otherwise Standard purchase agreement.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

contract_recommendation by supplier_tier: Strategic Partner → Long-term strategic contract with SLA; Key Supplier → Multi-year contract with performance metrics; Important Supplier → Annual contract with review clause; otherwise Standard purchase agreement.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_vendor_risk_analysis.sql` / `text`（sql；普通SQL表达式不是披露）

```text

'Standard purchase agreement' contract_recommendation

```

### payment_recommendation_placeholder

非原因；**Quiet Downgrade**；把握高。

付款建议固定Standard payment terms，未实现逾期比率与supplier_tier分支。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。finish只有“高阶指标受模拟数据/合同指定占位日期及字段可用性影响”，没有说明本处用常量/透传代替计算；该句并非本类省略计算的披露。event1已有指标定义，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 52 | 52 | 52 | 52 |
| L1 | 52 | 52 | 52 | 52 |
| L2 | 52 | 52 | 52 | 52 |
| L3 | 52 | 52 | 52 | 52 |



来源：`records/040_checks/supplement_extra_impl-013_netsuite2_vendor_risk_analysis.json` / `payment_recommendation_placeholder`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: payment_recommendation
        data_type: VARCHAR
        description: Payment guidance based on overdue_payment_percentage and supplier_tier

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: payment_recommendation
        data_type: VARCHAR
        description: Payment guidance based on overdue_payment_percentage and supplier_tier

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_vendor_risk_analysis.sql` / `text`（sql；普通SQL表达式不是披露）

```text

'Standard payment terms' payment_recommendation

```

### dependency_percentiles

非原因；**Intent Misreading**；把握高。

契约按支出percentile阈值含等号分类，agent用percent_rank。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 52 | 52 | 52 | 52 |
| L1 | 52 | 52 | 52 | 52 |
| L2 | 52 | 52 | 52 | 52 |
| L3 | 52 | 52 | 52 | 52 |



来源：`records/040_checks/supplement_extra_impl-013_netsuite2_vendor_risk_analysis.json` / `dependency_percentiles`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

dependency_level uses total_vendor_spend compared to percentile thresholds of total_vendor_spend across all vendors: ≥90th → Critical Dependency; ≥70th → High Dependency; ≥50th → Medium Dependency; ≥30th → Low Dependency; otherwise Minimal Dependency.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

dependency_level uses total_vendor_spend compared to percentile thresholds of total_vendor_spend across all vendors: ≥90th → Critical Dependency; ≥70th → High Dependency; ≥50th → Medium Dependency; ≥30th → Low Dependency; otherwise Minimal Dependency.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_vendor_risk_analysis.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CASE WHEN pct>=.9 THEN 'Critical Dependency' WHEN pct>=.7 THEN 'High Dependency' WHEN pct>=.5 THEN 'Medium Dependency' WHEN pct>=.3 THEN 'Low Dependency' ELSE 'Minimal Dependency' END

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`；行段[[3106, 3218]]；SHA-256 `c152a30bcad4df785d3f0ea461101eb8a4b36e4fa06059739a80e04998c4150f`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_vendor_risk_analysis.sql`；SHA-256 `9b63d6fca3bac324bd98cff7f07e30618f9e65fd2b44bf0469e9d82ab7074b8a`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`；材料包：`records/022_packages/022_impl-013_netsuite2_vendor_risk_analysis.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 4}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共2条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 24；上游可见行数；失败=True。

  - `records/022_queries_retry.json` / index 18；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
