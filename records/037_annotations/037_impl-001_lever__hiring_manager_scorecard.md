# impl-001_lever__hiring_manager_scorecard（037 正式批次）

主要原因：**已说出的降级**；把握：中。019旧主要原因原样保留：`D`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，finish 67 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-001_lever__hiring_manager_scorecard.json`；037补充：`records/037_checks/`。

## 逐点标注

### decision_speed

- 类别：已说出的降级；角色：并列；把握：中。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

决策速度整列Unknown占位；019对无hire输入恢复Slow分支仅作局部贡献证据。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: decision_speed_category
>         data_type: VARCHAR
>         description: 'Derived from avg_total_days_to_hire: <=30 Fast Decision Maker; <=45 Standard Decision Maker; <=60 Deliberate Decision Maker; else Slow Decision Maker; NULL → ''Unknown'''

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 39–39 行：

```sql
'Unknown' decision_speed_category
```

单改/诊断：`records/019_reruns_impl-001_lever__hiring_manager_scorecard.json#decision_speed`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1607 | 0/166 |
| L1 | 166/1773 | 166/1607 | 0/166 |
| L2 | 166/1751 | 166/1585 | 0/166 |
| L3 | 166/1751 | 166/1585 | 0/166 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### unweighted_total_applications

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约要求每posting简单均值；agent在application扩行后求AVG，形成按申请量加权。知道契约规定的汇总层次即可改正，归Intent。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '- Define hiring_manager_base: - From users keep access_role in {''admin'',''team_admin'',''limited''}. - Left join requisitions, postings, and applications (via postings) to compute workload: - total_requisitions_owned, total_postings_owned, total_applications_received, total_candidates_managed as distinct counts. - Keep only users with at least one requisition or posting. - Requisition performance per hiring_manager_user_id: - Distinct counts of requisitions by status: open, closed, filled. - avg_salary_range_width = mean of (compensation_band_max - compensation_band_min); NULLs ignored. - unique_teams_hired_for and unique_locations_hired_for as distinct counts. - requisition_fill_rate = filled/total as percent, rounded to 2 decimals; 0 when no requisitions. - Posting effectiveness per owner_user_id: - Distinct counts of postings and by state (published, closed). - Averages from posting_performance: avg_applications_per_posting, avg_posting_conversion_rate, avg_posting_performance_score. - high_performing_postings = postings with performance_tier = ''High Performing''; postings_with_no_applications = total_applications = 0. - departments_managed and teams_managed as distinct category counts. - high_performing_posting_rate = high_performing_postings/total as percent, rounded to 2 decimals; 0 when no postings. - Candidate management per posting_hiring_manager_user_id: - Distinct counts: total_candidates_managed (opportunities) and total_applications_overseen. - Averages over candidate_lifecycle: avg_candidate_lifecycle_days, avg_stages_per_candidate, avg_interview_completion_rate. - Outcome counts: candidates_hired if stage_name contains ''hire'' or ''accept'' (case-insensitive); offers_extended if contains ''offer''; candidates_rejected if archived_at present. - Candidate experience: average overall_candidate_experience_score; positive_experience_candidates for grades in {''Exceptional Experience'',''Excellent Experience''}. - candidate_hire_rate = candidates_hired/total_candidates_managed as percent, rounded to 2 decimals; 0 when none. - Interview coordination per posting_hiring_manager_user_id: - Distinct interviews coordinated; successful if not canceled; canceled if canceled. - Unique interviewers engaged; average interview duration. - Feedback: total_feedback_collected = distinct feedback_form_id; completed_feedback_collected = distinct feedback_form_id. - feedback_completion_rate_managed = distinct non-null feedback_form_id / distinct feedback_form_id as percent, rounded to 2 decimals; 0 when none. - interview_success_rate = successful/total as percent, rounded to 2 decimals; 0 when none. - Time efficiency per posting_hiring_manager_user_id (joining funnel metrics via applications, thus weighting postings by application volume): - Averages of avg_days_to_screening, avg_days_screening_to_technical, avg_total_days_to_hire. - high_efficiency_postings = distinct postings with hiring_efficiency_grade = ''High Efficiency (≥10%)''. - decision_speed_category from avg_total_days_to_hire thresholds: <=30 Fast, <=45 Standard, <=60 Deliberate, else Slow. - Final assembly per hiring_manager_id: - Pass identity fields; coalesce numeric metrics to 0 and decision_speed_category to ''Unknown''. - overall_performance_score = rounded (0 decimals), clamped [0,100] sum of: - 0.25*requisition_fill_rate + 0.25*high_performing_posting_rate + 0.25*candidate_hire_rate + 0.15*interview_success_rate - plus time-efficiency bonus based on avg_total_days_to_hire: +10 if <=45 else decreasing by 0.2 per day above 45, floored at 0; if avg_total_days_to_hire is missing, the score is NULL. - performance_tier by score thresholds: >=80 Outstanding; >=65 Effective; >=50 Competent; else Developing if total_candidates_managed>=5, otherwise New/Limited Experience. - hiring_specialization first-match: high_performing_posting_rate>=70 → Job Marketing Expert; else avg_candidate_experience_score>=4.0 → Candidate Experience Specialist; else feedback_completion_rate_managed>=85 → Process Coordinator; else avg_total_days_to_hire<=30 → Fast Decision Maker; else teams_supported>=3 → Multi-Team Recruiter; else Generalist. - development_recommendations = concatenation (in order) of segments with "; " when condition met: requisition_fill_rate<50, avg_applications_per_posting<10, interview_success_rate<80, avg_total_days_to_hire>60; empty string if none. - calculated_at = current query timestamp. - Order output by overall_performance_score descending, then total_candidates_hired descending.'

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 18–18 行：

```sql
avg(pp.total_applications)
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#unweighted_total_applications`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1763 | 0/10 |
| L1 | 166/1773 | 166/1763 | 0/10 |
| L2 | 166/1751 | 166/1741 | 0/10 |
| L3 | 166/1751 | 166/1741 | 0/10 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### unweighted_posting_performance_score

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约要求每posting简单均值；agent在application扩行后求AVG，形成按申请量加权。知道契约规定的汇总层次即可改正，归Intent。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '- Define hiring_manager_base: - From users keep access_role in {''admin'',''team_admin'',''limited''}. - Left join requisitions, postings, and applications (via postings) to compute workload: - total_requisitions_owned, total_postings_owned, total_applications_received, total_candidates_managed as distinct counts. - Keep only users with at least one requisition or posting. - Requisition performance per hiring_manager_user_id: - Distinct counts of requisitions by status: open, closed, filled. - avg_salary_range_width = mean of (compensation_band_max - compensation_band_min); NULLs ignored. - unique_teams_hired_for and unique_locations_hired_for as distinct counts. - requisition_fill_rate = filled/total as percent, rounded to 2 decimals; 0 when no requisitions. - Posting effectiveness per owner_user_id: - Distinct counts of postings and by state (published, closed). - Averages from posting_performance: avg_applications_per_posting, avg_posting_conversion_rate, avg_posting_performance_score. - high_performing_postings = postings with performance_tier = ''High Performing''; postings_with_no_applications = total_applications = 0. - departments_managed and teams_managed as distinct category counts. - high_performing_posting_rate = high_performing_postings/total as percent, rounded to 2 decimals; 0 when no postings. - Candidate management per posting_hiring_manager_user_id: - Distinct counts: total_candidates_managed (opportunities) and total_applications_overseen. - Averages over candidate_lifecycle: avg_candidate_lifecycle_days, avg_stages_per_candidate, avg_interview_completion_rate. - Outcome counts: candidates_hired if stage_name contains ''hire'' or ''accept'' (case-insensitive); offers_extended if contains ''offer''; candidates_rejected if archived_at present. - Candidate experience: average overall_candidate_experience_score; positive_experience_candidates for grades in {''Exceptional Experience'',''Excellent Experience''}. - candidate_hire_rate = candidates_hired/total_candidates_managed as percent, rounded to 2 decimals; 0 when none. - Interview coordination per posting_hiring_manager_user_id: - Distinct interviews coordinated; successful if not canceled; canceled if canceled. - Unique interviewers engaged; average interview duration. - Feedback: total_feedback_collected = distinct feedback_form_id; completed_feedback_collected = distinct feedback_form_id. - feedback_completion_rate_managed = distinct non-null feedback_form_id / distinct feedback_form_id as percent, rounded to 2 decimals; 0 when none. - interview_success_rate = successful/total as percent, rounded to 2 decimals; 0 when none. - Time efficiency per posting_hiring_manager_user_id (joining funnel metrics via applications, thus weighting postings by application volume): - Averages of avg_days_to_screening, avg_days_screening_to_technical, avg_total_days_to_hire. - high_efficiency_postings = distinct postings with hiring_efficiency_grade = ''High Efficiency (≥10%)''. - decision_speed_category from avg_total_days_to_hire thresholds: <=30 Fast, <=45 Standard, <=60 Deliberate, else Slow. - Final assembly per hiring_manager_id: - Pass identity fields; coalesce numeric metrics to 0 and decision_speed_category to ''Unknown''. - overall_performance_score = rounded (0 decimals), clamped [0,100] sum of: - 0.25*requisition_fill_rate + 0.25*high_performing_posting_rate + 0.25*candidate_hire_rate + 0.15*interview_success_rate - plus time-efficiency bonus based on avg_total_days_to_hire: +10 if <=45 else decreasing by 0.2 per day above 45, floored at 0; if avg_total_days_to_hire is missing, the score is NULL. - performance_tier by score thresholds: >=80 Outstanding; >=65 Effective; >=50 Competent; else Developing if total_candidates_managed>=5, otherwise New/Limited Experience. - hiring_specialization first-match: high_performing_posting_rate>=70 → Job Marketing Expert; else avg_candidate_experience_score>=4.0 → Candidate Experience Specialist; else feedback_completion_rate_managed>=85 → Process Coordinator; else avg_total_days_to_hire<=30 → Fast Decision Maker; else teams_supported>=3 → Multi-Team Recruiter; else Generalist. - development_recommendations = concatenation (in order) of segments with "; " when condition met: requisition_fill_rate<50, avg_applications_per_posting<10, interview_success_rate<80, avg_total_days_to_hire>60; empty string if none. - calculated_at = current query timestamp. - Order output by overall_performance_score descending, then total_candidates_hired descending.'

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 20–20 行：

```sql
avg(pp.posting_performance_score)
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#unweighted_posting_performance_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1742 | 0/31 |
| L1 | 166/1773 | 166/1742 | 0/31 |
| L2 | 166/1751 | 166/1742 | 0/9 |
| L3 | 166/1751 | 166/1742 | 0/9 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### avg_candidate_experience_score

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_candidate_experience_score
>         data_type: DOUBLE
>         description: Average overall_candidate_experience_score from lever__candidate_experience_insights across the manager’s candidates; NULL → 0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 37–37 行：

```sql
0.0 avg_candidate_experience_score
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#avg_candidate_experience_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1607 | 0/166 |
| L1 | 166/1773 | 166/1607 | 0/166 |
| L2 | 166/1751 | 166/1585 | 0/166 |
| L3 | 166/1751 | 166/1585 | 0/166 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### interview_success_rate

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: interview_success_rate
>         data_type: DOUBLE
>         description: Successful interviews (canceled_at IS NULL) / total interviews as a percent (0–100), rounded to 2 decimals; 0 when none

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 38–38 行：

```sql
0.0 interview_success_rate
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#interview_success_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1607 | 0/166 |
| L1 | 166/1773 | 166/1607 | 0/166 |
| L2 | 166/1751 | 166/1585 | 0/166 |
| L3 | 166/1751 | 166/1585 | 0/166 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### interviewer_network_size

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: interviewer_network_size
>         data_type: BIGINT
>         description: Distinct count of interviewer user_ids across the manager’s interviews; NULL → 0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 38–38 行：

```sql
0::BIGINT interviewer_network_size
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#interviewer_network_size`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1607 | 0/166 |
| L1 | 166/1773 | 166/1607 | 0/166 |
| L2 | 166/1751 | 166/1585 | 0/166 |
| L3 | 166/1751 | 166/1585 | 0/166 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### total_interviews_coordinated

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: total_interviews_coordinated
>         data_type: BIGINT
>         description: Distinct count of interviews associated to opportunities under the manager; NULL → 0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 39–39 行：

```sql
0::BIGINT total_interviews_coordinated
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#total_interviews_coordinated`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1607 | 0/166 |
| L1 | 166/1773 | 166/1607 | 0/166 |
| L2 | 166/1751 | 166/1585 | 0/166 |
| L3 | 166/1751 | 166/1585 | 0/166 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### high_efficiency_postings

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: high_efficiency_postings
>         data_type: BIGINT
>         description: Distinct count of postings with hiring_efficiency_grade = 'High Efficiency (≥10%)' from int_lever__hiring_funnel_metrics; NULL → 0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 40–40 行：

```sql
0::BIGINT high_efficiency_postings
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#high_efficiency_postings`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1607 | 0/166 |
| L1 | 166/1773 | 166/1607 | 0/166 |
| L2 | 166/1751 | 166/1585 | 0/166 |
| L3 | 166/1751 | 166/1585 | 0/166 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### overall_performance_score

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: overall_performance_score
>         data_type: DOUBLE
>         description: Composite score = 0.25*requisition_fill_rate + 0.25*high_performing_posting_rate + 0.25*candidate_hire_rate + 0.15*interview_success_rate + time-efficiency bonus; rounded to 0 decimals, clamped to [0,100], may be NULL if avg_total_days_to_hire is missing

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 40–40 行：

```sql
NULL::DOUBLE overall_performance_score
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#overall_performance_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1773 | 0/0 |
| L1 | 166/1773 | 166/1773 | 0/0 |
| L2 | 166/1751 | 166/1751 | 0/0 |
| L3 | 166/1751 | 166/1751 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### performance_tier

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: performance_tier
>         data_type: VARCHAR
>         description: 'Tier from overall_performance_score: >=80 Outstanding Hiring Manager; >=65 Effective Hiring Manager; >=50 Competent Hiring Manager; else Developing Hiring Manager if total_candidates_managed>=5, otherwise New/Limited Experience'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 40–40 行：

```sql
'New/Limited Experience' performance_tier
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#performance_tier`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1683 | 0/90 |
| L1 | 166/1773 | 166/1683 | 0/90 |
| L2 | 166/1751 | 166/1661 | 0/90 |
| L3 | 166/1751 | 166/1661 | 0/90 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### hiring_specialization

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: hiring_specialization
>         data_type: VARCHAR
>         description: 'First-match classification: high_performing_posting_rate>=70 → Job Marketing Expert; else avg_candidate_experience_score>=4.0 → Candidate Experience Specialist; else feedback_completion_rate_managed>=85 → Process Coordinator; else avg_total_days_to_hire<=30 → Fast Decision Maker; else teams_supported>=3 → Multi-Team Recruiter; else Generalist'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 41–41 行：

```sql
'Generalist' hiring_specialization
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#hiring_specialization`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1782 | 0/-9 |
| L1 | 166/1773 | 166/1782 | 0/-9 |
| L2 | 166/1751 | 166/1760 | 0/-9 |
| L3 | 166/1751 | 166/1760 | 0/-9 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### feedback_completion_rate_managed

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: feedback_completion_rate_managed
>         data_type: DOUBLE
>         description: Completion rate over interview_feedback computed as distinct non-null feedback_form_id divided by distinct feedback_form_id; percent (0–100), rounded to 2 decimals; 0 when none

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 38–38 行：

```sql
0.0 feedback_completion_rate_managed
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#feedback_completion_rate_managed`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1616 | 0/157 |
| L1 | 166/1773 | 166/1616 | 0/157 |
| L2 | 166/1751 | 166/1594 | 0/157 |
| L3 | 166/1751 | 166/1594 | 0/157 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### development_recommendations

- 类别：已说出的降级；角色：非原因；把握：中。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复四段条件拼接，沿原SQL的现有指标值；缺失其他指标仍保留原值。仅文字代表采用gold已有片段/语义表述，不把gold当规则。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: development_recommendations
>         data_type: VARCHAR
>         description: 'Concatenated recommendations (in order) with ''; '' suffix per rule: fill_rate<50, avg_apps_per_posting<10, interview_success_rate<80, avg_total_days_to_hire>60; empty string if none; trailing space preserved'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 41–41 行：

```sql
'' development_recommendations
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#development_recommendations`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 166/1773 | 166/1773 | 0/0 |
| L1 | 166/1773 | 166/1773 | 0/0 |
| L2 | 166/1751 | 166/1751 | 0/0 |
| L3 | 166/1751 | 166/1751 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

不确定：部分恢复公式的干预在其他默认输入仍错误时不能对齐gold，甚至增加差异；保留非原因而不外推整套模型已修复。恢复条件的文字代表若契约未固定，只用于测量，不能反过来当契约。
