# impl-001 / lever__candidate_quality_insights

## 结论

主要原因：**A**；把握：中；标记：无。

契约只给出消息含义，未规定完全相同英文字符串。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-001_lever__candidate_quality_insights.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：1/1。本次固定控制下 baseline 行/格规模：1/4。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`；原文行段 2057–2147。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_quality_insights.sql`，L1–1；SHA-256 `73f42921ac5052984b551327377de089bc95373f9fa1c0077267e74aadb94ff9`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/marts/lever__candidate_quality_insights.sql`，L1–231；SHA-256 `7c1aecaa8eea22231ca6029ea100ece87ecfee97069b3e1b73010bbd67037f6e`。

key_finding_source：agent SQL L1，替换原片段如下。
```sql
CASE WHEN referred>external_avg+10 THEN 'Referral sources produce higher-quality candidates' WHEN internal>external_avg+10 THEN 'Internal mobility produces higher-quality candidates' ELSE 'No significant source difference' END key_finding_source
```
替换为：
```sql
CASE WHEN referred>external_avg+10 THEN 'Referrals produce significantly higher quality candidates' WHEN internal>external_avg+10 THEN 'Internal candidates show higher quality scores' ELSE 'No significant source quality difference observed' END key_finding_source
```

key_finding_overall：agent SQL L1，替换原片段如下。
```sql
CASE WHEN (exceptional+highq)*1.0/nullif(total,0)>=.4 THEN 'Strong candidate quality distribution' WHEN (exceptional+highq)*1.0/nullif(total,0)>=.25 THEN 'Good candidate quality distribution' ELSE 'Opportunity to improve candidate quality' END key_finding_overall
```
替换为：
```sql
CASE WHEN (exceptional+highq)*1.0/nullif(total,0)>=.4 THEN 'Strong candidate quality - 40%+ are high/exceptional quality' WHEN (exceptional+highq)*1.0/nullif(total,0)>=.25 THEN 'Good candidate quality - 25%+ are high/exceptional quality' ELSE 'Opportunity to improve candidate quality - focus on sourcing' END key_finding_overall
```

primary_recommendation：agent SQL L1，替换原片段如下。
```sql
CASE WHEN (SELECT source_type FROM src WHERE rn=1)='Referred' THEN 'Invest in referral programs' WHEN (SELECT source_type FROM src WHERE rn=1)='Internal' THEN 'Promote internal mobility' ELSE 'Optimize external channels' END primary_recommendation
```
替换为：
```sql
CASE WHEN (SELECT source_type FROM src WHERE rn=1)='Referred' THEN 'Invest more in employee referral programs' WHEN (SELECT source_type FROM src WHERE rn=1)='Internal' THEN 'Promote internal mobility and development' ELSE 'Optimize external sourcing channels' END primary_recommendation
```

process_recommendation：agent SQL L1，替换原片段如下。
```sql
CASE WHEN highdays<lowdays THEN 'Fast-track high-quality candidates' ELSE 'Improve early screening' END process_recommendation
```
替换为：
```sql
CASE WHEN highdays<lowdays THEN 'Fast-track high-quality candidates to reduce time-to-hire' ELSE 'Review screening process to identify quality candidates earlier' END process_recommendation
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-001_lever__candidate_quality_insights.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 1 | 4 | {"key_finding_overall": 1, "key_finding_source": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| baseline | L1 | 1 | 4 | {"key_finding_overall": 1, "key_finding_source": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| baseline | L2 | 1 | 4 | {"key_finding_overall": 1, "key_finding_source": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| baseline | L3 | 1 | 4 | {"key_finding_overall": 1, "key_finding_source": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| key_finding_source | L0 | 1 | 3 | {"key_finding_overall": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| key_finding_source | L1 | 1 | 3 | {"key_finding_overall": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| key_finding_source | L2 | 1 | 3 | {"key_finding_overall": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| key_finding_source | L3 | 1 | 3 | {"key_finding_overall": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| key_finding_overall | L0 | 1 | 3 | {"key_finding_source": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| key_finding_overall | L1 | 1 | 3 | {"key_finding_source": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| key_finding_overall | L2 | 1 | 3 | {"key_finding_source": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| key_finding_overall | L3 | 1 | 3 | {"key_finding_source": 1, "primary_recommendation": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| primary_recommendation | L0 | 1 | 3 | {"key_finding_overall": 1, "key_finding_source": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| primary_recommendation | L1 | 1 | 3 | {"key_finding_overall": 1, "key_finding_source": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| primary_recommendation | L2 | 1 | 3 | {"key_finding_overall": 1, "key_finding_source": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| primary_recommendation | L3 | 1 | 3 | {"key_finding_overall": 1, "key_finding_source": 1, "process_recommendation": 1} | L0–L3均不匹配 |
| process_recommendation | L0 | 1 | 3 | {"key_finding_overall": 1, "key_finding_source": 1, "primary_recommendation": 1} | L0–L3均不匹配 |
| process_recommendation | L1 | 1 | 3 | {"key_finding_overall": 1, "key_finding_source": 1, "primary_recommendation": 1} | L0–L3均不匹配 |
| process_recommendation | L2 | 1 | 3 | {"key_finding_overall": 1, "key_finding_source": 1, "primary_recommendation": 1} | L0–L3均不匹配 |
| process_recommendation | L3 | 1 | 3 | {"key_finding_overall": 1, "key_finding_source": 1, "primary_recommendation": 1} | L0–L3均不匹配 |

- key_finding_source（A，单处 SQL 改动）：行减少 0，格减少 1。契约只给出消息含义，未规定完全相同英文字符串。

- key_finding_overall（A，单处 SQL 改动）：行减少 0，格减少 1。契约只给出消息含义，未规定完全相同英文字符串。

- primary_recommendation（A，单处 SQL 改动）：行减少 0，格减少 1。契约只给出消息含义，未规定完全相同英文字符串。

- process_recommendation（A，单处 SQL 改动）：行减少 0，格减少 1。契约只给出消息含义，未规定完全相同英文字符串。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，字段字符偏移 132384。

> lever__candidate_quality_insights
>       description: Single-row snapshot computed at run time summarizing candidate quality distributions, percentiles, and top contributing factors.
>       grain: Exactly one row per run (point-in-time snapshot)
>       source_models:
>       - intermediate.int_lever__candidate_insights (opportunity_id, candidate_quality_score, total_lifecycle_days, total_interviews, interview_completion_rate, positive_feedback_rate, candidate_status_category, candidate_experience_qua

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

契约规定消息的含义但没给完整英文常量。四个文本选择单修的行/格改善并列，类别均为 A，按 v2 第5节直接记 A。
