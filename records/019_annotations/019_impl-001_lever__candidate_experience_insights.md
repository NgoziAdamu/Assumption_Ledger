# impl-001 / lever__candidate_experience_insights

## 结论

主要原因：**O**；把握：中；标记：无。

诊断复现 gold 四个同键子结果再连接的 n^5 重数；契约声明每 opportunity 一行且没要求最终四次自连接。

参与因素：completion_zero=C；timeline_score=I；recommendations=D。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-001_lever__candidate_experience_insights.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：5576/764216。本次固定控制下 baseline 行/格规模：764216/22017288。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`；原文行段 1951–2056。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`，L1–1；SHA-256 `8aacb580e54ccaa9c147a9121eef271d40f5e39e91d886b51b49fa7d518dcd8c`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`，L1–292；SHA-256 `7a4ac1db1f6a63a05a49d627db1300f32bd2ab88ccb837df6d78ed56bfa59f34`。

contact_join：agent SQL L1，替换原片段如下。
```sql
LEFT JOIN staging.stg_lever__stage s
```
替换为：
```sql
LEFT JOIN intermediate.int_lever__contact_info c ON cl.contact_id=c.contact_id LEFT JOIN staging.stg_lever__stage s
```

stage_inner：agent SQL L1，替换原片段如下。
```sql
LEFT JOIN staging.stg_lever__stage s
```
替换为：
```sql
JOIN staging.stg_lever__stage s
```

completion_zero：agent SQL L1，替换原片段如下。
```sql
round(cl.completed_interviews*100.0/nullif(cl.total_interviews,0),1) completion_rate
```
替换为：
```sql
round(cl.completed_interviews*100.0/cl.total_interviews,1) completion_rate
```

timeline_score：agent SQL L1，替换原片段如下。
```sql
round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1) overall_candidate_experience_score
```
替换为：
```sql
round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+1*.2),1) overall_candidate_experience_score
```

recommendations：agent SQL L1，替换原片段如下。
```sql
'' improvement_recommendations
```
替换为：
```sql
concat(CASE WHEN transparency_score<=2 THEN 'Improve feedback transparency; ' ELSE '' END,CASE WHEN interview_experience_score<=2 THEN 'Optimize interview process; ' ELSE '' END,'Accelerate decision timeline; ',CASE WHEN days_since_last_advancement>=14 THEN 'Increase communication frequency; ' ELSE '' END) improvement_recommendations
```

gold_join_multiplicity：agent SQL L1，替换原片段如下。
```sql
FROM calc
```
替换为：
```sql
FROM calc, LATERAL (SELECT count(*) n FROM base b WHERE b.opportunity_id=calc.opportunity_id) rep, UNNEST(range(cast(pow(rep.n,4) AS BIGINT))) mult(j)
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-001_lever__candidate_experience_insights.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| baseline | L1 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| baseline | L2 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| baseline | L3 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| contact_join | L0 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| contact_join | L1 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| contact_join | L2 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| contact_join | L3 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| stage_inner | L0 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| stage_inner | L1 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| stage_inner | L2 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| stage_inner | L3 | 764216 | 22017288 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| completion_zero | L0 | 764216 | 22011712 | {"improvement_recommendations": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| completion_zero | L1 | 764216 | 22011712 | {"improvement_recommendations": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| completion_zero | L2 | 764216 | 22011712 | {"improvement_recommendations": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| completion_zero | L3 | 764216 | 22011712 | {"improvement_recommendations": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| timeline_score | L0 | 764216 | 22011712 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576} | L0–L3均不匹配 |
| timeline_score | L1 | 764216 | 22011712 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576} | L0–L3均不匹配 |
| timeline_score | L2 | 764216 | 22011712 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576} | L0–L3均不匹配 |
| timeline_score | L3 | 764216 | 22011712 | {"improvement_recommendations": 5576, "interview_completion_rate_pct": 5576} | L0–L3均不匹配 |
| recommendations | L0 | 764216 | 22011712 | {"interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| recommendations | L1 | 764216 | 22011712 | {"interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| recommendations | L2 | 764216 | 22011712 | {"interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| recommendations | L3 | 764216 | 22011712 | {"interview_completion_rate_pct": 5576, "overall_candidate_experience_score": 5576} | L0–L3均不匹配 |
| gold_join_multiplicity | L0 | 764216 | 2292648 | {"improvement_recommendations": 764216, "interview_completion_rate_pct": 764216, "overall_candidate_experience_score": 764216} | L0–L3均不匹配 |
| gold_join_multiplicity | L1 | 764216 | 2292648 | {"improvement_recommendations": 764216, "interview_completion_rate_pct": 764216, "overall_candidate_experience_score": 764216} | L0–L3均不匹配 |
| gold_join_multiplicity | L2 | 764216 | 2292648 | {"improvement_recommendations": 764216, "interview_completion_rate_pct": 764216, "overall_candidate_experience_score": 764216} | L0–L3均不匹配 |
| gold_join_multiplicity | L3 | 764216 | 2292648 | {"improvement_recommendations": 764216, "interview_completion_rate_pct": 764216, "overall_candidate_experience_score": 764216} | L0–L3均不匹配 |

- contact_join（C，单处 SQL 改动）：行减少 0，格减少 0。遗漏契约明确指定 contact_info 左连接；其重复键会放大输出。

- stage_inner（C，单处 SQL 改动）：行减少 0，格减少 0。stage 要求 inner join。

- completion_zero（C，单处 SQL 改动）：行减少 0，格减少 5576。契约明确 no explicit zero-division guard。

- timeline_score（I，单处 SQL 改动）：行减少 0，格减少 5576。代码已输出 timeline=1，却在 overall 中写常数3。

- recommendations（D，单处 SQL 改动）：行减少 0，格减少 5576。建议整列空字符串占位。

- gold_join_multiplicity（O，单处 SQL 改动）：行减少 0，格减少 19724640。诊断复现 gold 四个同键子结果再连接的 n^5 重数；契约声明每 opportunity 一行且没要求最终四次自连接。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，字段字符偏移 121472。

> lever__candidate_experience_insights
>       description: Candidate experience metrics and scores per opportunity derived from lifecycle, interview, communication, and outcome signals
>       grain: One row per opportunity_id
>       source_models:
>       - intermediate.int_lever__candidate_lifecycle
>       - staging.stg_lever__opportunity
>       - staging.stg_lever__stage
>       - staging.stg_lever__archive_reason
>       - intermediate.int_lever__contact_info
>       business_logic: 'Build candidate_journey

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

gold 将同一 journey 派生的四个非唯一键子结果再次连接，产生 n^5 重数；契约声明每 opportunity 一行，且未规定最终四次连接。两种读法：按 SQL 缺少连接判 C/U，或按契约粒度与 gold 重数不一致判 O。本次选 O；乘数试验是复现评测条件的诊断，不是推荐实现。其他 C/I/D 差异仍按单修量记录。
