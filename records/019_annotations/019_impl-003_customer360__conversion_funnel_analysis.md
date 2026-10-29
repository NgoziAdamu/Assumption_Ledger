# impl-003 / customer360__conversion_funnel_analysis

## 结论

主要原因：**C**；把握：高；标记：无。

收入速度分母/单位与契约公式不同。

参与因素：journey_completeness_score=O。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-003_customer360__conversion_funnel_analysis.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：441119/441119。本次固定控制下 baseline 行/格规模：99356/449116。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`；原文行段 1257–1394。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__conversion_funnel_analysis.sql`，L1–43；SHA-256 `05450eb3b18261e6a791d84d8bf44e4b4b4c26dd084cfd3f4d00cdc51eb62afb`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__conversion_funnel_analysis.sql`，L1–370；SHA-256 `55ace929b28cf7a613f6b4fee226d0a55456768c105b753224b76f7af4a723e1`。

revenue_velocity_monthly：agent SQL L18，替换原片段如下。
```sql
case when in_stripe=1 then estimated_customer_ltv*30.0/greatest(coalesce(marketing_to_sales_days,30),30) else 0 end as revenue_velocity_monthly
```
替换为：
```sql
CASE WHEN reached_conversion = 1 THEN ROUND(estimated_customer_ltv / GREATEST(COALESCE(marketing_to_sales_days, 30), 30) * 30, 2) ELSE 0 END AS revenue_velocity_monthly
```

rounded_consistency：agent SQL L41，替换原片段如下。
```sql
.4*cross_stage_engagement_consistency,2) as journey_efficiency_index
```
替换为：
```sql
.4*round(cross_stage_engagement_consistency,2),2) as journey_efficiency_index
```

journey_completeness_score：agent SQL L8，替换原片段如下。
```sql
case when in_marketo=1 and in_stripe=1 and in_zendesk=1 then 3 when in_marketo+in_stripe+in_zendesk>=2 then 2 when in_marketo+in_stripe+in_zendesk=1 then 1 else 0 end as journey_completeness_score
```
替换为：
```sql
CASE WHEN in_marketo = 1 AND in_stripe = 1 AND in_zendesk = 1 THEN 3 WHEN (in_marketo = 1 AND in_stripe = 1) OR (in_stripe = 1 AND in_zendesk = 1) THEN 2 WHEN in_marketo = 1 OR in_stripe = 1 OR in_zendesk = 1 THEN 1 ELSE 0 END AS journey_completeness_score
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-003_customer360__conversion_funnel_analysis.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 99356 | 449116 | {"revenue_velocity_monthly": 90612} | L0–L3均不匹配 |
| baseline | L1 | 99356 | 449116 | {"revenue_velocity_monthly": 90612} | L0–L3均不匹配 |
| baseline | L2 | 8744 | 358504 | {} | L0–L3均不匹配 |
| baseline | L3 | 8744 | 358504 | {} | L0–L3均不匹配 |
| revenue_velocity_monthly | L0 | 8744 | 358504 | {} | L0–L3均不匹配 |
| revenue_velocity_monthly | L1 | 8744 | 358504 | {} | L0–L3均不匹配 |
| revenue_velocity_monthly | L2 | 8744 | 358504 | {} | L0–L3均不匹配 |
| revenue_velocity_monthly | L3 | 8744 | 358504 | {} | L0–L3均不匹配 |
| rounded_consistency | L0 | 99356 | 449116 | {"revenue_velocity_monthly": 90612} | L0–L3均不匹配 |
| rounded_consistency | L1 | 99356 | 449116 | {"revenue_velocity_monthly": 90612} | L0–L3均不匹配 |
| rounded_consistency | L2 | 8744 | 358504 | {} | L0–L3均不匹配 |
| rounded_consistency | L3 | 8744 | 358504 | {} | L0–L3均不匹配 |
| journey_completeness_score | L0 | 90612 | 90612 | {"revenue_velocity_monthly": 90612} | L2 |
| journey_completeness_score | L1 | 90612 | 90612 | {"revenue_velocity_monthly": 90612} | L2 |
| journey_completeness_score | L2 | 0 | 0 | {} | L2 |
| journey_completeness_score | L3 | 0 | 0 | {} | L2 |

- revenue_velocity_monthly（C，单处 SQL 改动）：行减少 90612，格减少 90612。收入速度分母/单位与契约公式不同。

- rounded_consistency（C，单处 SQL 改动）：行减少 0，格减少 0。契约要求先将 consistency 四舍五入到2位；agent 在依赖键公式中使用未舍入值。

- journey_completeness_score（O，单处 SQL 改动）：行减少 8744，格减少 358504。契约规定任意两个平台为2；gold 两平台分支遗漏 Marketo+Zendesk，agent 按契约使用总数。

补充键诊断：`records/019_funnel_key_diagnostic.json`。将 journey_efficiency_index 临时移出键仅用于定位，未改变本表官方判错或主试验比较键。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，字段字符偏移 91142。

> customer360__conversion_funnel_analysis
>       description: Conversion funnel metrics and optimization insights derived from behavior, lifecycle, and activity sources
>       grain: One row per behavior_analysis record with non-null primary_email
>       source_models:
>       - intermediate.int_customer360__customer_behavior_analysis (marketo_lead_id, stripe_customer_id, zendesk_user_id, primary_email, primary_organization, customer_first_touchpoint, customer_last_activity, customer_journey_pattern, c

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
