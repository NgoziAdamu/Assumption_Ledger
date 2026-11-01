# 040 正式标注：impl-012_marketo__operational_health_simple

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。022旧主要原因仅原样存档为 `A`，不作为新类别依据。

## 结论

主要原因：**多因并列**；把握中；共2个点。不是只能组合修复。

并列项：score_weights（Unstated Choice）；recommendation_wording（其他）

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### score_weights

并列；**Unstated Choice**；把握中。

契约给四项分量和总体范围，未列各档分值；不同权重都可据此构造，差异取决于材料没定的选择。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1 | 1 | 2 | 1 |
| L1 | 1 | 1 | 2 | 1 |
| L2 | 1 | 1 | 2 | 1 |
| L3 | 1 | 1 | 2 | 1 |



来源：`records/022_reruns_impl-012_marketo__operational_health_simple.json` / `score_weights`。L0减少0行、1格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

overall_health_score is the sum of four point components based on thresholds (deliverability, engagement, campaign mix, stability); the sum is rounded and stored as an integer (range ~35–100).

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

overall_health_score is the sum of four point components based on thresholds (deliverability, engagement, campaign mix, stability); the sum is rounded and stored as an integer (range ~35–100).

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/marts/marketo__operational_health_simple.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(ROUND((CASE WHEN overall_delivery_rate_pct>=95 THEN 25 WHEN overall_delivery_rate_pct>=90 THEN 20 WHEN overall_delivery_rate_pct>=85 THEN 15 ELSE 5 END)+(CASE WHEN engaged_leads_pct>=40 THEN 25 WHEN engaged_leads_pct>=25 THEN 20 WHEN engaged_leads_pct>=15 THEN 15 ELSE 5 END)+(CASE WHEN healthy_campaigns_pct>=50 THEN 25 WHEN healthy_campaigns_pct>=25 THEN 20 WHEN healthy_campaigns_pct>=10 THEN 15 ELSE 5 END)+(CASE WHEN delivery_stability='Stable' THEN 25 WHEN delivery_stability='Moderate Variance' THEN 15 ELSE 5 END)) AS INTEGER) AS overall_health_score

```

### recommendation_wording

并列；**其他**；把握高。

分类条件相同，均建议改善deliverability；契约只有语义没有字面短语规定，纯文字写法差异按第5节其他。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1 | 1 | 2 | 1 |
| L1 | 1 | 1 | 2 | 1 |
| L2 | 1 | 1 | 2 | 1 |
| L3 | 1 | 1 | 2 | 1 |



来源：`records/022_reruns_impl-012_marketo__operational_health_simple.json` / `recommendation_wording`。L0减少0行、1格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

primary_recommendation chosen in order: if overall_delivery_rate_pct < 85 then focus on deliverability; else if at_risk_leads_pct > 30 then re-engage leads; else if critical_campaigns > 3 then optimize campaigns; else if delivery_stability is High Variance then stabilize sending; otherwise continue current efforts.'

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

primary_recommendation chosen in order: if overall_delivery_rate_pct < 85 then focus on deliverability; else if at_risk_leads_pct > 30 then re-engage leads; else if critical_campaigns > 3 then optimize campaigns; else if delivery_stability is High Variance then stabilize sending; otherwise continue current efforts.'

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/marts/marketo__operational_health_simple.sql` / `text`（sql；普通SQL表达式不是披露）

```text

'Focus on improving email deliverability'

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`；行段[[1580, 1699]]；SHA-256 `9162d6f365aa651428fe0b03f4854de1e85296668fc5edaf34e599c15b3ac1a4`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/marts/marketo__operational_health_simple.sql`；SHA-256 `f472e1fa6b2a10d66e5db88244ca26ef14f104817f2c0d40dea36682c38cf999`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json`；材料包：`records/022_packages/022_impl-012_marketo__operational_health_simple.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 22:47:14.925+08'", "count": 3}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 4}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共2条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 5；上游可见行数；失败=True。

  - `records/022_queries_retry.json` / index 3；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
