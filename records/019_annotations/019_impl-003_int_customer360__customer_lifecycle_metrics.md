# impl-003 / int_customer360__customer_lifecycle_metrics

## 结论

主要原因：**O**；把握：中；标记：无。

契约允许每次变化的模拟量；共同屏蔽随机输出的诊断。

参与因素：frequency_score=C。

不确定性四档：**针对本表的具体说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-003_int_customer360__customer_lifecycle_metrics.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：5001/5001。本次固定控制下 baseline 行/格规模：2641/2657。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`；原文行段 914–1037。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_lifecycle_metrics.sql`，L1–77；SHA-256 `d7df359e7fa0d024561b5a4d5b163ca9171e45c87e0e7d3d2b80a945c0e241bb`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_lifecycle_metrics.sql`，L1–337；SHA-256 `55bd25e284df597c61ba6c45dd00acb66c70a0c6e8a52bb9d9fd52f2a5606d34`。

frequency_score：agent SQL L23，替换原片段如下。
```sql
case when platform_sum>=2 and active_90_days=1 then 3 when active_180_days=1 then 2 else 1 end as frequency_score
```
替换为：
```sql
CASE WHEN platform_sum = 3 AND active_30_days = 1 THEN 5 WHEN platform_sum >= 2 AND active_60_days = 1 THEN 4 WHEN platform_sum >= 2 AND active_90_days = 1 THEN 3 WHEN active_180_days = 1 THEN 2 ELSE 1 END AS frequency_score
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-003_int_customer360__customer_lifecycle_metrics.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 2641 | 2657 | {"customer_tier": 2, "estimated_customer_ltv": 7, "estimated_transaction_count": 2637, "expected_retention_rate": 2, "frequency_score": 7, "performance_vs_expectation": 2} | L0–L3均不匹配 |
| baseline | L1 | 2641 | 2657 | {"customer_tier": 2, "estimated_customer_ltv": 7, "estimated_transaction_count": 2637, "expected_retention_rate": 2, "frequency_score": 7, "performance_vs_expectation": 2} | L0–L3均不匹配 |
| baseline | L2 | 2641 | 2657 | {"customer_tier": 2, "estimated_customer_ltv": 7, "estimated_transaction_count": 2637, "expected_retention_rate": 2, "frequency_score": 7, "performance_vs_expectation": 2} | L0–L3均不匹配 |
| baseline | L3 | 2641 | 2657 | {"customer_tier": 2, "estimated_customer_ltv": 7, "estimated_transaction_count": 2637, "expected_retention_rate": 2, "frequency_score": 7, "performance_vs_expectation": 2} | L0–L3均不匹配 |
| frequency_score | L0 | 2637 | 2637 | {"estimated_transaction_count": 2637} | L0–L3均不匹配 |
| frequency_score | L1 | 2637 | 2637 | {"estimated_transaction_count": 2637} | L0–L3均不匹配 |
| frequency_score | L2 | 2637 | 2637 | {"estimated_transaction_count": 2637} | L0–L3均不匹配 |
| frequency_score | L3 | 2637 | 2637 | {"estimated_transaction_count": 2637} | L0–L3均不匹配 |

- frequency_score（C，单处 SQL 改动）：行减少 4，格减少 20。频率评分缺失 active30/60 的高分分支。

- stochastic_evaluation（O，评测条件诊断，非代码修复）：行减少 2634，格减少 2637。契约允许每次变化的模拟量；共同屏蔽随机输出的诊断。

随机诊断：`records/019_stochastic_diagnostics.json`，保留全部比较列与官方键，只共同屏蔽指定随机量。没有复原 gold seed，不把它记为 U 单修。

## agent 可见证据及不确定性

event 51 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，字段字符偏移 1121。

> 生命周期模拟交易数、活动量和依赖它们的派生指标按契约使用 `random()`，因此跨次执行不保证完全可复现；执行时间字段及基于当前日期的指标同样随运行时间变化。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

手册明确固定时间，但未规定随机模拟量的共同控制。保留官方判错，以固定 setseed 的私有执行减小试验噪声；gold 原 seed 未知。共同将契约允许随机的输出替换为0，仅作 O 诊断，不能当作普通代码修复或 U 第4条件。
