# impl-001 / lever__departmental_hiring_trends

## 结论

主要原因：**D**；把握：中；标记：已披露。

成本分类常数占位；仅恢复无 hire 时分支。

参与因素：referral_count=C。

不确定性四档：**针对本表的具体说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-001_lever__departmental_hiring_trends.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：148/148。本次固定控制下 baseline 行/格规模：148/1420。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`；原文行段 2148–2281。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，L1–49；SHA-256 `0f1835fb4495999932eabe685337143390c08ac717ef33cac699bb9ca83355e4`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，L1–379；SHA-256 `8e822d72eb46613af402ca1d532ce2d2560e94a9d3246e1780664d89968f8df7`。

referral_count：agent SQL L13，替换原片段如下。
```sql
count(DISTINCT referrer_user_id) AS referred
```
替换为：
```sql
count(DISTINCT application_id) FILTER(WHERE referrer_user_id IS NOT NULL) AS referred
```

cost_tier：agent SQL L38，替换原片段如下。
```sql
'No Data' AS cost_efficiency_tier
```
替换为：
```sql
'No Hires' AS cost_efficiency_tier
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-001_lever__departmental_hiring_trends.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 148 | 1420 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "cost_efficiency_tier": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "referral_rate": 7, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| baseline | L1 | 148 | 1420 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "cost_efficiency_tier": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "referral_rate": 7, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| baseline | L2 | 148 | 1420 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "cost_efficiency_tier": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "referral_rate": 7, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| baseline | L3 | 148 | 1420 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "cost_efficiency_tier": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "referral_rate": 7, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| referral_count | L0 | 148 | 1413 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "cost_efficiency_tier": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| referral_count | L1 | 148 | 1413 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "cost_efficiency_tier": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| referral_count | L2 | 148 | 1413 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "cost_efficiency_tier": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| referral_count | L3 | 148 | 1413 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "cost_efficiency_tier": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| cost_tier | L0 | 148 | 1272 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "referral_rate": 7, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| cost_tier | L1 | 148 | 1272 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "referral_rate": 7, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| cost_tier | L2 | 148 | 1272 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "referral_rate": 7, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |
| cost_tier | L3 | 148 | 1272 | {"avg_candidate_experience_score": 148, "avg_interview_duration_minutes": 148, "avg_screening_pass_rate": 148, "department_performance_score": 148, "department_strength": 81, "high_efficiency_postings": 148, "interview_completion_rate": 148, "referral_rate": 7, "total_interviews_conducted": 148, "unique_interviewers": 148} | L0–L3均不匹配 |

- referral_count（C，单处 SQL 改动）：行减少 0，格减少 7。referral 应数申请而非去重 referrer。

- cost_tier（D，单处 SQL 改动）：行减少 0，格减少 148。成本分类常数占位；仅恢复无 hire 时分支。

## agent 可见证据及不确定性

event 67 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，字段字符偏移 639。

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

错误点粒度存在两种读法：每个占位输出列分别算一处，或将同一遗漏聚合/规则模块视为一个降级错误点。本次以模块为错误点，列出全部可见占位及残余列统计，以局部恢复模块内表达式/来源证明贡献；没有用整份 gold SQL 替换来宣称因果成立。未逐一补齐全部占位列，不能据局部修法宣称已覆盖模块内所有修复。若后续决定按列拆分，需重新比较这些因素的贡献排序。
