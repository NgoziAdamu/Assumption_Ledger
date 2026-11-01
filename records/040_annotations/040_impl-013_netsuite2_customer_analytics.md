# 040 正式标注：impl-013_netsuite2_customer_analytics

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。022旧主要原因仅原样存档为 `C`，不作为新类别依据。

## 结论

主要原因：**Intent Misreading**；把握高；共5个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### second_join

主要；**Intent Misreading**；把握高。

业务逻辑明确customer_insights再从ecs LEFT JOIN cbp；agent跳过该连接，丢失44行的多重性。明文连接优先于笼统一客户一行描述。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 181 | 181 | 1544 | 466 |
| L1 | 181 | 181 | 1544 | 466 |
| L2 | 181 | 181 | 1544 | 466 |
| L3 | 181 | 181 | 1544 | 466 |



来源：`records/022_reruns_impl-013_netsuite2_customer_analytics.json` / `second_join`。L0减少0行、1078格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

customer_insights by left joining ecs to cbp on customer_id:

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

customer_insights by left joining ecs to cbp on customer_id:

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql` / `text`（sql；普通SQL表达式不是披露）

```text

FROM enriched)

```

### frequency_zero

参与；**Intent Misreading**；把握高。

lifespan或active_months不正时频率应0；agent NULLIF得到NULL。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 181 | 181 | 1544 | 1407 |
| L1 | 181 | 181 | 1544 | 1407 |
| L2 | 181 | 181 | 1544 | 1407 |
| L3 | 181 | 181 | 1544 | 1407 |



来源：`records/022_reruns_impl-013_netsuite2_customer_analytics.json` / `frequency_zero`。L0减少0行、137格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

avg_transactions_per_month = total_transactions divided by (customer_lifespan_days/30.0) when active_months > 0 and customer_lifespan_days > 0; otherwise 0; no rounding.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

avg_transactions_per_month = total_transactions divided by (customer_lifespan_days/30.0) when active_months > 0 and customer_lifespan_days > 0; otherwise 0; no rounding.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql` / `text`（sql；普通SQL表达式不是披露）

```text

total_transactions/nullif(customer_lifespan_days/30.0,0) avg_transactions_per_month

```

### retention_labels

参与；**其他**；把握高。

agent输出Long-term等契约短标签，gold使用括号长标签；单改模拟gold，非agent不遵契约。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 181 | 181 | 1544 | 1407 |
| L1 | 181 | 181 | 1544 | 1407 |
| L2 | 181 | 181 | 1544 | 1407 |
| L3 | 181 | 181 | 1544 | 1407 |



来源：`records/022_reruns_impl-013_netsuite2_customer_analytics.json` / `retention_labels`。L0减少0行、137格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

retention_category by customer_lifespan_days thresholds: ≥365 Long-term; ≥180 Medium-term; ≥90 Short-term; ≥30 New; else Very New.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

retention_category by customer_lifespan_days thresholds: ≥365 Long-term; ≥180 Medium-term; ≥90 Short-term; ≥30 New; else Very New.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CASE WHEN customer_lifespan_days>=365 THEN 'Long-term' WHEN customer_lifespan_days>=180 THEN 'Medium-term' WHEN customer_lifespan_days>=90 THEN 'Short-term' WHEN customer_lifespan_days>=30 THEN 'New' ELSE 'Very New' END retention_category

```

### score_weights

参与；**Unstated Choice**；把握中。

综合客户评分只规定加权和及活动/留存加分，未给权重数字。差异取决于材料没定的选择。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 181 | 181 | 1544 | 1462 |
| L1 | 181 | 181 | 1544 | 1462 |
| L2 | 181 | 181 | 1544 | 1462 |
| L3 | 181 | 181 | 1544 | 1462 |



来源：`records/022_reruns_impl-013_netsuite2_customer_analytics.json` / `score_weights`。L0减少0行、82格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

comprehensive_customer_score = weighted sum of cp revenue/frequency/margin scores plus activity and retention bonuses, capped at 100.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

comprehensive_customer_score = weighted sum of cp revenue/frequency/margin scores plus activity and retention bonuses, capped at 100.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql` / `text`（sql；普通SQL表达式不是披露）

```text

least(100,revenue_score*10+frequency_score*5+margin_score*5+CASE WHEN activity_status='Highly Active' THEN 15 WHEN activity_status='Active' THEN 10 ELSE 0 END+retention_probability*20)::INTEGER comprehensive_customer_score

```

### value_percentiles

非原因；**Intent Misreading**；把握高。

契约按总体收入percentile阈值含等号分档；agent用percent_rank的行位置比较，分别诊断是否造成当前差异。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 181 | 181 | 1544 | 1544 |
| L1 | 181 | 181 | 1544 | 1544 |
| L2 | 181 | 181 | 1544 | 1544 |
| L3 | 181 | 181 | 1544 | 1544 |



来源：`records/040_checks/supplement_extra_impl-013_netsuite2_customer_analytics.json` / `value_percentiles`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

value_tier via overall revenue percentile thresholds across cp: ≥90th Platinum; ≥70th Gold; ≥50th Silver; ≥30th Bronze; else Basic (inclusive comparisons).

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

value_tier via overall revenue percentile thresholds across cp: ≥90th Platinum; ≥70th Gold; ≥50th Silver; ≥30th Bronze; else Basic (inclusive comparisons).

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CASE WHEN cp.rev_pct>=.9 THEN 'Platinum' WHEN cp.rev_pct>=.7 THEN 'Gold' WHEN cp.rev_pct>=.5 THEN 'Silver' WHEN cp.rev_pct>=.3 THEN 'Bronze' ELSE 'Basic' END

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`；行段[[2533, 2631]]；SHA-256 `c152a30bcad4df785d3f0ea461101eb8a4b36e4fa06059739a80e04998c4150f`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql`；SHA-256 `bb972ea1e4294370c3a95f7fb505cd231555524d7f277694a0fa1cf826ab44a3`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`；材料包：`records/022_packages/022_impl-013_netsuite2_customer_analytics.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 4}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共2条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 20；上游可见行数；失败=True。

  - `records/022_queries_retry.json` / index 14；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

- 一客户一行grain与明确两次LEFT JOIN在重复上游下有张力；按可执行连接条款判遗漏Intent，不自行删第二次连接。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
