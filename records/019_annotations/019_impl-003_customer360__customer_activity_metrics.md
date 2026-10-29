# impl-003 / customer360__customer_activity_metrics

## 结论

主要原因：**C**；把握：中；标记：无。

一致性指标遗漏除以在场平台数。

参与因素：primary_engagement_channel=C；stochastic_evaluation=O。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-003_customer360__customer_activity_metrics.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：6947/6947。本次固定控制下 baseline 行/格规模：6947/27613。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`；原文行段 1481–1662。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer_activity_metrics.sql`，L1–60；SHA-256 `ef6a507771a29589773387e1fe94484f28860d3be6a09fbf1a418a92c3a405d8`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__customer_activity_metrics.sql`，L1–389；SHA-256 `8d42ca0fe47bd9e57f4f8aae44da61d923549eeecc63a0f35834fc558a0fa6aa`。

cross_platform_consistency：agent SQL L41，替换原片段如下。
```sql
round(case when in_marketo=1 then marketo_engagement else 0 end + case when in_stripe=1 then stripe_engagement else 0 end + case when in_zendesk=1 then zendesk_engagement else 0 end,2) as cross_platform_consistency
```
替换为：
```sql
ROUND((CASE WHEN in_marketo = 1 THEN marketo_engagement ELSE 0 END + CASE WHEN in_stripe = 1 THEN stripe_engagement ELSE 0 END + CASE WHEN in_zendesk = 1 THEN zendesk_engagement ELSE 0 END) / NULLIF((in_marketo + in_stripe + in_zendesk), 0), 2) AS cross_platform_consistency
```

primary_engagement_channel：agent SQL L30，替换原片段如下。
```sql
case when marketing_engagement_score>=sales_engagement_score and marketing_engagement_score>=support_engagement_score then 'Marketing Driven'
 when sales_engagement_score>=support_engagement_score then 'Sales Driven' when support_engagement_score is not null then 'Support Driven' else 'Balanced' end as primary_engagement_channel
```
替换为：
```sql
CASE WHEN marketo_engagement >= stripe_engagement AND marketo_engagement >= zendesk_engagement THEN 'Marketing Driven' WHEN stripe_engagement >= marketo_engagement AND stripe_engagement >= zendesk_engagement THEN 'Sales Driven' WHEN zendesk_engagement >= marketo_engagement AND zendesk_engagement >= stripe_engagement THEN 'Support Driven' ELSE 'Balanced' END AS primary_engagement_channel
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-003_customer360__customer_activity_metrics.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 6947 | 27613 | {"activity_priority_score": 7, "cross_platform_consistency": 6947, "estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "primary_engagement_channel": 6219, "recommended_activity_intervention": 3313, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| baseline | L1 | 6583 | 26930 | {"cross_platform_consistency": 6271, "estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "primary_engagement_channel": 6219, "recommended_activity_intervention": 3313, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| baseline | L2 | 6583 | 26930 | {"cross_platform_consistency": 6271, "estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "primary_engagement_channel": 6219, "recommended_activity_intervention": 3313, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| baseline | L3 | 6583 | 26930 | {"cross_platform_consistency": 6271, "estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "primary_engagement_channel": 6219, "recommended_activity_intervention": 3313, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| cross_platform_consistency | L0 | 6561 | 20666 | {"activity_priority_score": 7, "estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "primary_engagement_channel": 6219, "recommended_activity_intervention": 3313, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| cross_platform_consistency | L1 | 6561 | 20659 | {"estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "primary_engagement_channel": 6219, "recommended_activity_intervention": 3313, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| cross_platform_consistency | L2 | 6561 | 20659 | {"estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "primary_engagement_channel": 6219, "recommended_activity_intervention": 3313, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| cross_platform_consistency | L3 | 6561 | 20659 | {"estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "primary_engagement_channel": 6219, "recommended_activity_intervention": 3313, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| primary_engagement_channel | L0 | 6947 | 18081 | {"activity_priority_score": 7, "cross_platform_consistency": 6947, "estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| primary_engagement_channel | L1 | 6583 | 17398 | {"cross_platform_consistency": 6271, "estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| primary_engagement_channel | L2 | 6583 | 17398 | {"cross_platform_consistency": 6271, "estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |
| primary_engagement_channel | L3 | 6583 | 17398 | {"cross_platform_consistency": 6271, "estimated_monthly_activities": 3703, "lifecycle_stage": 18, "predicted_next_month_activity": 3703, "seasonally_adjusted_activity": 3703} | L0–L3均不匹配 |

- cross_platform_consistency（C，单处 SQL 改动）：行减少 386，格减少 6947。一致性指标遗漏除以在场平台数。

- primary_engagement_channel（C，单处 SQL 改动）：行减少 0，格减少 9532。主渠道要求比较原始 engagement；agent 比较衰减后 score。

- stochastic_evaluation（O，评测条件诊断，非代码修复）：行减少 0，格减少 11127。契约允许每次变化的模拟量；共同屏蔽随机输出的诊断。

随机诊断：`records/019_stochastic_diagnostics.json`，保留全部比较列与官方键，只共同屏蔽指定随机量。没有复原 gold seed，不把它记为 U 单修。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，字段字符偏移 91993。

> customer360__customer_activity_metrics (primary_email, activity_grade, weighted_engagement_score, primary_engagement_channel)
>       business_logic: '- Begin with behavior_analysis and left join lifecycle_metrics and activity_metrics on primary_email. - Stage flags: reached_awareness = in_marketo; reached_conversion = in_stripe; reached_support = in_zendesk (1/0/NULL passthrough). - Speed buckets: awareness_to_conversion_speed from marketing_to_sales_days: ≤30 → Fast; ≤90 → Medium; ≤180 → Slow; >

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

random() 派生的三列同样采用共同屏蔽诊断；不修改官方评分。主因比较使用完整列数，随机差异作为评测条件因素。
