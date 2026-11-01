# impl-001_lever__candidate_experience_insights（037 正式批次）

主要原因：**其他**；把握：中。019旧主要原因原样保留：`O`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，finish 67 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-001_lever__candidate_experience_insights.json`；037补充：`records/037_checks/`。

## 逐点标注

### contact_join

- 类别：Intent Misreading；角色：非原因；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约要求连接contact_info，SQL省略；单改没有减少评测差异，列为非原因。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build candidate_journey by joining: - intermediate.int_lever__candidate_lifecycle (cl) to staging.stg_lever__opportunity (o) on opportunity_id, left join intermediate.int_lever__contact_info (c) on contact_id, join staging.stg_lever__stage (s) on o.stage_id, and left join staging.stg_lever__archive_reason (ar) on o.archived_reason_id. - Derive fields: - activity_status: constant ''Active''. - lifecycle_speed_category: total_lifecycle_days bucketed as ≤14 ''Fast'', ≤30 ''Standard'', ≤60 ''Slow'', else ''Very Slow''. - interview_completion_rate_pct: completed_interviews divided by total_interviews times 100, rounded to 1 decimal; no explicit zero-division guard; NULLs propagate. - Carry through totals (interviews, completed, canceled), avg_interview_duration_minutes, total_interview_time_minutes, avg_recommendation_score, feedback_completion_rate_pct, is_archived, application_date (o.created_at), last_interaction_at, last_advanced_at, current_stage (s.stage_name), archive_reason (ar.archive_reason_title). Compute communication_quality per opportunity_id: - days_from_application_to_last_contact: difference in days between last_interaction_at and application_date; NULL if either is NULL. - days_from_application_to_last_advancement: difference in days between last_advanced_at and application_date; NULL if either is NULL. - response_quality from days_since_last_advancement: ≤1 ''Excellent Response (≤1 day)''; ≤3 ''Good Response (2-3 days)''; ≤7 ''Moderate Response (4-7 days)''; ≤14 ''Slow Response (8-14 days)''; else ''Very Slow Response (>14 days)'' (NULL falls to the else bucket). - transparency_score from feedback_completion_rate_pct: ≥90→5; ≥70→4; ≥50→3; ≥30→2; else 1 (NULL falls to 1). Compute interview_experience per opportunity_id: - interview_experience_score: - If total_interviews = 0 → NULL. - Else if completion rate ≥95 and avg duration in 30–90 minutes → 5. - Else if completion rate ≥80 and avg duration in 20–120 minutes → 4. - Else if completion rate ≥60 → 3; else if ≥40 → 2; else → 1. - interview_burden_category: - If total_interviews = 0 → ''No Interviews''. - Else if total_interviews ≤2 and total_interview_time_minutes ≤120 → ''Light Process''; ≤4 and ≤240 → ''Standard Process''; ≤6 and ≤360 → ''Intensive Process''; else ''Heavy Process''. - interview_consistency_score: - If total_interviews = 0 → NULL. - Else if canceled_interviews = 0 → 5; else if canceled/total ≤10% → 4; ≤20% → 3; ≤30% → 2; else → 1. Compute outcome_fairness per opportunity_id: - outcome_fairness_score: - If not archived → NULL. - Else 5 for stage indicating hire/accept or reason indicating withdrew/declined; 4 for offer stage or skills/qualification mismatch; 3 for culture fit issues or other; 2 if rejected without a stated reason. - process_completeness_assessment: - If not archived → ''In Progress''; else if avg_recommendation_score ≥4 and stage does not indicate hire → ''Potential Mismatch''; else if avg_recommendation_score ≤2 → ''Consistent Outcome''; else if avg_recommendation_score is NULL → ''Incomplete Process''; else → ''Normal Process''. Compute timeline_experience per opportunity_id: - timeline_experience_score compares lifecycle_speed_category to labels ''Fast Track (≤7 days)'', ''Normal (8-30 days)'', ''Extended (31-60 days)'', ''Long Process (>60 days)''; because candidate_journey uses ''Fast''/''Standard''/''Slow''/''Very Slow'', no label matches and the else branch applies, yielding 1 for all rows. - candidate_anxiety_level from activity_status: ''Active'' maps to ''Low Anxiety''. Final projection and derived fields: - overall_candidate_experience_score: weighted average of subscores (transparency 20%, interview experience 25%, interview consistency 15%, outcome fairness 20%, timeline 20%), defaulting missing subscores to 3, rounded to 1 decimal. - experience_grade from the same rounded overall score: ≥4.5 ''Exceptional Experience''; ≥4.0 ''Excellent Experience''; ≥3.5 ''Good Experience''; ≥3.0 ''Average Experience''; ≥2.0 ''Below Average Experience''; else ''Poor Experience''. - improvement_recommendations: concatenate in this order (each fragment ends with ''; '' and no trimming): if transparency_score ≤2 add ''Improve feedback transparency; ''; if interview_experience_score ≤2 add ''Optimize interview process; ''; if timeline_experience_score ≤2 add ''Accelerate decision timeline; ''; if days_since_last_advancement ≥14 add ''Increase communication frequency; ''. - experience_risk_flag (first match): if days_since_last_advancement ≥21 and not archived → ''High Abandonment Risk''; else if canceled_interviews ≥2 → ''Poor Interview Experience''; else if transparency_score ≤2 and total_interviews ≥3 → ''Low Process Transparency''; else if timeline_experience_score ≤2 and total_lifecycle_days ≥60 → ''Extended Timeline Concern''; else ''Normal''. - calculated_at = current timestamp at model execution. - Final result ordered by overall_candidate_experience_score descending, then total_lifecycle_days ascending.'

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`，第 1–1 行：

```sql
LEFT JOIN staging.stg_lever__stage s
```

单改/诊断：`records/019_reruns_impl-001_lever__candidate_experience_insights.json#contact_join`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 764216/22017288 | 764216/22017288 | 0/0 |
| L1 | 764216/22017288 | 764216/22017288 | 0/0 |
| L2 | 764216/22017288 | 764216/22017288 | 0/0 |
| L3 | 764216/22017288 | 764216/22017288 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> business_logic: 'Build candidate_journey by joining: - intermediate.int_lever__candidate_lifecycle (cl) to staging.stg_lever__opportunity (o) on opportunity_id, left join intermediate.int_lever__contact_info (c) on contact_id, join staging.stg_lever__stage (s) on o.stage_id, and left join staging.stg_lever__archive_reason (ar) on o.archived_reason_id. - Derive fields: - activity_status: constant ''Active''. - lifecycle_speed_category: total_lifecycle_days bucketed as ≤14 ''Fast'', ≤30 ''Standard'', ≤60 ''Slow'', else ''Very Slow''. - interview_completion_rate_pct: completed_interviews divided by total_interviews times 100, rounded to 1 decimal; no explicit zero-division guard; NULLs propagate. - Carry through totals (interviews, completed, canceled), avg_interview_duration_minutes, total_interview_time_minutes, avg_recommendation_score, feedback_completion_rate_pct, is_archived, application_date (o.created_at), last_interaction_at, last_advanced_at, current_stage (s.stage_name), archive_reason (ar.archive_reason_title). Compute communication_quality per opportunity_id: - days_from_application_to_last_contact: difference in days between last_interaction_at and application_date; NULL if either is NULL. - days_from_application_to_last_advancement: difference in days between last_advanced_at and application_date; NULL if either is NULL. - response_quality from days_since_last_advancement: ≤1 ''Excellent Response (≤1 day)''; ≤3 ''Good Response (2-3 days)''; ≤7 ''Moderate Response (4-7 days)''; ≤14 ''Slow Response (8-14 days)''; else ''Very Slow Response (>14 days)'' (NULL falls to the else bucket). - transparency_score from feedback_completion_rate_pct: ≥90→5; ≥70→4; ≥50→3; ≥30→2; else 1 (NULL falls to 1). Compute interview_experience per opportunity_id: - interview_experience_score: - If total_interviews = 0 → NULL. - Else if completion rate ≥95 and avg duration in 30–90 minutes → 5. - Else if completion rate ≥80 and avg duration in 20–120 minutes → 4. - Else if completion rate ≥60 → 3; else if ≥40 → 2; else → 1. - interview_burden_category: - If total_interviews = 0 → ''No Interviews''. - Else if total_interviews ≤2 and total_interview_time_minutes ≤120 → ''Light Process''; ≤4 and ≤240 → ''Standard Process''; ≤6 and ≤360 → ''Intensive Process''; else ''Heavy Process''. - interview_consistency_score: - If total_interviews = 0 → NULL. - Else if canceled_interviews = 0 → 5; else if canceled/total ≤10% → 4; ≤20% → 3; ≤30% → 2; else → 1. Compute outcome_fairness per opportunity_id: - outcome_fairness_score: - If not archived → NULL. - Else 5 for stage indicating hire/accept or reason indicating withdrew/declined; 4 for offer stage or skills/qualification mismatch; 3 for culture fit issues or other; 2 if rejected without a stated reason. - process_completeness_assessment: - If not archived → ''In Progress''; else if avg_recommendation_score ≥4 and stage does not indicate hire → ''Potential Mismatch''; else if avg_recommendation_score ≤2 → ''Consistent Outcome''; else if avg_recommendation_score is NULL → ''Incomplete Process''; else → ''Normal Process''. Compute timeline_experience per opportunity_id: - timeline_experience_score compares lifecycle_speed_category to labels ''Fast Track (≤7 days)'', ''Normal (8-30 days)'', ''Extended (31-60 days)'', ''Long Process (>60 days)''; because candidate_journey uses ''Fast''/''Standard''/''Slow''/''Very Slow'', no label matches and the else branch applies, yielding 1 for all rows. - candidate_anxiety_level from activity_status: ''Active'' maps to ''Low Anxiety''. Final projection and derived fields: - overall_candidate_experience_score: weighted average of subscores (transparency 20%, interview experience 25%, interview consistency 15%, outcome fairness 20%, timeline 20%), defaulting missing subscores to 3, rounded to 1 decimal. - experience_grade from the same rounded overall score: ≥4.5 ''Exceptional Experience''; ≥4.0 ''Excellent Experience''; ≥3.5 ''Good Experience''; ≥3.0 ''Average Experience''; ≥2.0 ''Below Average Experience''; else ''Poor Experience''. - improvement_recommendations: concatenate in this order (each fragment ends with ''; '' and no trimming): if transparency_score ≤2 add ''Improve feedback transparency; ''; if interview_experience_score ≤2 add ''Optimize interview process; ''; if timeline_experience_score ≤2 add ''Accelerate decision timeline; ''; if days_since_last_advancement ≥14 add ''Increase communication frequency; ''. - experience_risk_flag (first match): if days_since_last_advancement ≥21 and not archived → ''High Abandonment Risk''; else if canceled_interviews ≥2 → ''Poor Interview Experience''; else if transparency_score ≤2 and total_interviews ≥3 → ''Low Process Transparency''; else if timeline_experience_score ≤2 and total_lifecycle_days ≥60 → ''Extended Timeline Concern''; else ''Normal''. - calculated_at = current timestamp at model execution. - Final result ordered by overall_candidate_experience_score descending, then total_lifecycle_days ascending.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### stage_inner

- 类别：Intent Misreading；角色：非原因；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约规定stage内连接，agent使用LEFT JOIN；单改没有减少差异。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build candidate_journey by joining: - intermediate.int_lever__candidate_lifecycle (cl) to staging.stg_lever__opportunity (o) on opportunity_id, left join intermediate.int_lever__contact_info (c) on contact_id, join staging.stg_lever__stage (s) on o.stage_id, and left join staging.stg_lever__archive_reason (ar) on o.archived_reason_id. - Derive fields: - activity_status: constant ''Active''. - lifecycle_speed_category: total_lifecycle_days bucketed as ≤14 ''Fast'', ≤30 ''Standard'', ≤60 ''Slow'', else ''Very Slow''. - interview_completion_rate_pct: completed_interviews divided by total_interviews times 100, rounded to 1 decimal; no explicit zero-division guard; NULLs propagate. - Carry through totals (interviews, completed, canceled), avg_interview_duration_minutes, total_interview_time_minutes, avg_recommendation_score, feedback_completion_rate_pct, is_archived, application_date (o.created_at), last_interaction_at, last_advanced_at, current_stage (s.stage_name), archive_reason (ar.archive_reason_title). Compute communication_quality per opportunity_id: - days_from_application_to_last_contact: difference in days between last_interaction_at and application_date; NULL if either is NULL. - days_from_application_to_last_advancement: difference in days between last_advanced_at and application_date; NULL if either is NULL. - response_quality from days_since_last_advancement: ≤1 ''Excellent Response (≤1 day)''; ≤3 ''Good Response (2-3 days)''; ≤7 ''Moderate Response (4-7 days)''; ≤14 ''Slow Response (8-14 days)''; else ''Very Slow Response (>14 days)'' (NULL falls to the else bucket). - transparency_score from feedback_completion_rate_pct: ≥90→5; ≥70→4; ≥50→3; ≥30→2; else 1 (NULL falls to 1). Compute interview_experience per opportunity_id: - interview_experience_score: - If total_interviews = 0 → NULL. - Else if completion rate ≥95 and avg duration in 30–90 minutes → 5. - Else if completion rate ≥80 and avg duration in 20–120 minutes → 4. - Else if completion rate ≥60 → 3; else if ≥40 → 2; else → 1. - interview_burden_category: - If total_interviews = 0 → ''No Interviews''. - Else if total_interviews ≤2 and total_interview_time_minutes ≤120 → ''Light Process''; ≤4 and ≤240 → ''Standard Process''; ≤6 and ≤360 → ''Intensive Process''; else ''Heavy Process''. - interview_consistency_score: - If total_interviews = 0 → NULL. - Else if canceled_interviews = 0 → 5; else if canceled/total ≤10% → 4; ≤20% → 3; ≤30% → 2; else → 1. Compute outcome_fairness per opportunity_id: - outcome_fairness_score: - If not archived → NULL. - Else 5 for stage indicating hire/accept or reason indicating withdrew/declined; 4 for offer stage or skills/qualification mismatch; 3 for culture fit issues or other; 2 if rejected without a stated reason. - process_completeness_assessment: - If not archived → ''In Progress''; else if avg_recommendation_score ≥4 and stage does not indicate hire → ''Potential Mismatch''; else if avg_recommendation_score ≤2 → ''Consistent Outcome''; else if avg_recommendation_score is NULL → ''Incomplete Process''; else → ''Normal Process''. Compute timeline_experience per opportunity_id: - timeline_experience_score compares lifecycle_speed_category to labels ''Fast Track (≤7 days)'', ''Normal (8-30 days)'', ''Extended (31-60 days)'', ''Long Process (>60 days)''; because candidate_journey uses ''Fast''/''Standard''/''Slow''/''Very Slow'', no label matches and the else branch applies, yielding 1 for all rows. - candidate_anxiety_level from activity_status: ''Active'' maps to ''Low Anxiety''. Final projection and derived fields: - overall_candidate_experience_score: weighted average of subscores (transparency 20%, interview experience 25%, interview consistency 15%, outcome fairness 20%, timeline 20%), defaulting missing subscores to 3, rounded to 1 decimal. - experience_grade from the same rounded overall score: ≥4.5 ''Exceptional Experience''; ≥4.0 ''Excellent Experience''; ≥3.5 ''Good Experience''; ≥3.0 ''Average Experience''; ≥2.0 ''Below Average Experience''; else ''Poor Experience''. - improvement_recommendations: concatenate in this order (each fragment ends with ''; '' and no trimming): if transparency_score ≤2 add ''Improve feedback transparency; ''; if interview_experience_score ≤2 add ''Optimize interview process; ''; if timeline_experience_score ≤2 add ''Accelerate decision timeline; ''; if days_since_last_advancement ≥14 add ''Increase communication frequency; ''. - experience_risk_flag (first match): if days_since_last_advancement ≥21 and not archived → ''High Abandonment Risk''; else if canceled_interviews ≥2 → ''Poor Interview Experience''; else if transparency_score ≤2 and total_interviews ≥3 → ''Low Process Transparency''; else if timeline_experience_score ≤2 and total_lifecycle_days ≥60 → ''Extended Timeline Concern''; else ''Normal''. - calculated_at = current timestamp at model execution. - Final result ordered by overall_candidate_experience_score descending, then total_lifecycle_days ascending.'

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`，第 1–1 行：

```sql
LEFT JOIN staging.stg_lever__stage s
```

单改/诊断：`records/019_reruns_impl-001_lever__candidate_experience_insights.json#stage_inner`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 764216/22017288 | 764216/22017288 | 0/0 |
| L1 | 764216/22017288 | 764216/22017288 | 0/0 |
| L2 | 764216/22017288 | 764216/22017288 | 0/0 |
| L3 | 764216/22017288 | 764216/22017288 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> business_logic: 'Build candidate_journey by joining: - intermediate.int_lever__candidate_lifecycle (cl) to staging.stg_lever__opportunity (o) on opportunity_id, left join intermediate.int_lever__contact_info (c) on contact_id, join staging.stg_lever__stage (s) on o.stage_id, and left join staging.stg_lever__archive_reason (ar) on o.archived_reason_id. - Derive fields: - activity_status: constant ''Active''. - lifecycle_speed_category: total_lifecycle_days bucketed as ≤14 ''Fast'', ≤30 ''Standard'', ≤60 ''Slow'', else ''Very Slow''. - interview_completion_rate_pct: completed_interviews divided by total_interviews times 100, rounded to 1 decimal; no explicit zero-division guard; NULLs propagate. - Carry through totals (interviews, completed, canceled), avg_interview_duration_minutes, total_interview_time_minutes, avg_recommendation_score, feedback_completion_rate_pct, is_archived, application_date (o.created_at), last_interaction_at, last_advanced_at, current_stage (s.stage_name), archive_reason (ar.archive_reason_title). Compute communication_quality per opportunity_id: - days_from_application_to_last_contact: difference in days between last_interaction_at and application_date; NULL if either is NULL. - days_from_application_to_last_advancement: difference in days between last_advanced_at and application_date; NULL if either is NULL. - response_quality from days_since_last_advancement: ≤1 ''Excellent Response (≤1 day)''; ≤3 ''Good Response (2-3 days)''; ≤7 ''Moderate Response (4-7 days)''; ≤14 ''Slow Response (8-14 days)''; else ''Very Slow Response (>14 days)'' (NULL falls to the else bucket). - transparency_score from feedback_completion_rate_pct: ≥90→5; ≥70→4; ≥50→3; ≥30→2; else 1 (NULL falls to 1). Compute interview_experience per opportunity_id: - interview_experience_score: - If total_interviews = 0 → NULL. - Else if completion rate ≥95 and avg duration in 30–90 minutes → 5. - Else if completion rate ≥80 and avg duration in 20–120 minutes → 4. - Else if completion rate ≥60 → 3; else if ≥40 → 2; else → 1. - interview_burden_category: - If total_interviews = 0 → ''No Interviews''. - Else if total_interviews ≤2 and total_interview_time_minutes ≤120 → ''Light Process''; ≤4 and ≤240 → ''Standard Process''; ≤6 and ≤360 → ''Intensive Process''; else ''Heavy Process''. - interview_consistency_score: - If total_interviews = 0 → NULL. - Else if canceled_interviews = 0 → 5; else if canceled/total ≤10% → 4; ≤20% → 3; ≤30% → 2; else → 1. Compute outcome_fairness per opportunity_id: - outcome_fairness_score: - If not archived → NULL. - Else 5 for stage indicating hire/accept or reason indicating withdrew/declined; 4 for offer stage or skills/qualification mismatch; 3 for culture fit issues or other; 2 if rejected without a stated reason. - process_completeness_assessment: - If not archived → ''In Progress''; else if avg_recommendation_score ≥4 and stage does not indicate hire → ''Potential Mismatch''; else if avg_recommendation_score ≤2 → ''Consistent Outcome''; else if avg_recommendation_score is NULL → ''Incomplete Process''; else → ''Normal Process''. Compute timeline_experience per opportunity_id: - timeline_experience_score compares lifecycle_speed_category to labels ''Fast Track (≤7 days)'', ''Normal (8-30 days)'', ''Extended (31-60 days)'', ''Long Process (>60 days)''; because candidate_journey uses ''Fast''/''Standard''/''Slow''/''Very Slow'', no label matches and the else branch applies, yielding 1 for all rows. - candidate_anxiety_level from activity_status: ''Active'' maps to ''Low Anxiety''. Final projection and derived fields: - overall_candidate_experience_score: weighted average of subscores (transparency 20%, interview experience 25%, interview consistency 15%, outcome fairness 20%, timeline 20%), defaulting missing subscores to 3, rounded to 1 decimal. - experience_grade from the same rounded overall score: ≥4.5 ''Exceptional Experience''; ≥4.0 ''Excellent Experience''; ≥3.5 ''Good Experience''; ≥3.0 ''Average Experience''; ≥2.0 ''Below Average Experience''; else ''Poor Experience''. - improvement_recommendations: concatenate in this order (each fragment ends with ''; '' and no trimming): if transparency_score ≤2 add ''Improve feedback transparency; ''; if interview_experience_score ≤2 add ''Optimize interview process; ''; if timeline_experience_score ≤2 add ''Accelerate decision timeline; ''; if days_since_last_advancement ≥14 add ''Increase communication frequency; ''. - experience_risk_flag (first match): if days_since_last_advancement ≥21 and not archived → ''High Abandonment Risk''; else if canceled_interviews ≥2 → ''Poor Interview Experience''; else if transparency_score ≤2 and total_interviews ≥3 → ''Low Process Transparency''; else if timeline_experience_score ≤2 and total_lifecycle_days ≥60 → ''Extended Timeline Concern''; else ''Normal''. - calculated_at = current timestamp at model execution. - Final result ordered by overall_candidate_experience_score descending, then total_lifecycle_days ascending.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### completion_zero

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确不加零除保护，agent增加NULLIF，改变计算出的值；不是呈现差异。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build candidate_journey by joining: - intermediate.int_lever__candidate_lifecycle (cl) to staging.stg_lever__opportunity (o) on opportunity_id, left join intermediate.int_lever__contact_info (c) on contact_id, join staging.stg_lever__stage (s) on o.stage_id, and left join staging.stg_lever__archive_reason (ar) on o.archived_reason_id. - Derive fields: - activity_status: constant ''Active''. - lifecycle_speed_category: total_lifecycle_days bucketed as ≤14 ''Fast'', ≤30 ''Standard'', ≤60 ''Slow'', else ''Very Slow''. - interview_completion_rate_pct: completed_interviews divided by total_interviews times 100, rounded to 1 decimal; no explicit zero-division guard; NULLs propagate. - Carry through totals (interviews, completed, canceled), avg_interview_duration_minutes, total_interview_time_minutes, avg_recommendation_score, feedback_completion_rate_pct, is_archived, application_date (o.created_at), last_interaction_at, last_advanced_at, current_stage (s.stage_name), archive_reason (ar.archive_reason_title). Compute communication_quality per opportunity_id: - days_from_application_to_last_contact: difference in days between last_interaction_at and application_date; NULL if either is NULL. - days_from_application_to_last_advancement: difference in days between last_advanced_at and application_date; NULL if either is NULL. - response_quality from days_since_last_advancement: ≤1 ''Excellent Response (≤1 day)''; ≤3 ''Good Response (2-3 days)''; ≤7 ''Moderate Response (4-7 days)''; ≤14 ''Slow Response (8-14 days)''; else ''Very Slow Response (>14 days)'' (NULL falls to the else bucket). - transparency_score from feedback_completion_rate_pct: ≥90→5; ≥70→4; ≥50→3; ≥30→2; else 1 (NULL falls to 1). Compute interview_experience per opportunity_id: - interview_experience_score: - If total_interviews = 0 → NULL. - Else if completion rate ≥95 and avg duration in 30–90 minutes → 5. - Else if completion rate ≥80 and avg duration in 20–120 minutes → 4. - Else if completion rate ≥60 → 3; else if ≥40 → 2; else → 1. - interview_burden_category: - If total_interviews = 0 → ''No Interviews''. - Else if total_interviews ≤2 and total_interview_time_minutes ≤120 → ''Light Process''; ≤4 and ≤240 → ''Standard Process''; ≤6 and ≤360 → ''Intensive Process''; else ''Heavy Process''. - interview_consistency_score: - If total_interviews = 0 → NULL. - Else if canceled_interviews = 0 → 5; else if canceled/total ≤10% → 4; ≤20% → 3; ≤30% → 2; else → 1. Compute outcome_fairness per opportunity_id: - outcome_fairness_score: - If not archived → NULL. - Else 5 for stage indicating hire/accept or reason indicating withdrew/declined; 4 for offer stage or skills/qualification mismatch; 3 for culture fit issues or other; 2 if rejected without a stated reason. - process_completeness_assessment: - If not archived → ''In Progress''; else if avg_recommendation_score ≥4 and stage does not indicate hire → ''Potential Mismatch''; else if avg_recommendation_score ≤2 → ''Consistent Outcome''; else if avg_recommendation_score is NULL → ''Incomplete Process''; else → ''Normal Process''. Compute timeline_experience per opportunity_id: - timeline_experience_score compares lifecycle_speed_category to labels ''Fast Track (≤7 days)'', ''Normal (8-30 days)'', ''Extended (31-60 days)'', ''Long Process (>60 days)''; because candidate_journey uses ''Fast''/''Standard''/''Slow''/''Very Slow'', no label matches and the else branch applies, yielding 1 for all rows. - candidate_anxiety_level from activity_status: ''Active'' maps to ''Low Anxiety''. Final projection and derived fields: - overall_candidate_experience_score: weighted average of subscores (transparency 20%, interview experience 25%, interview consistency 15%, outcome fairness 20%, timeline 20%), defaulting missing subscores to 3, rounded to 1 decimal. - experience_grade from the same rounded overall score: ≥4.5 ''Exceptional Experience''; ≥4.0 ''Excellent Experience''; ≥3.5 ''Good Experience''; ≥3.0 ''Average Experience''; ≥2.0 ''Below Average Experience''; else ''Poor Experience''. - improvement_recommendations: concatenate in this order (each fragment ends with ''; '' and no trimming): if transparency_score ≤2 add ''Improve feedback transparency; ''; if interview_experience_score ≤2 add ''Optimize interview process; ''; if timeline_experience_score ≤2 add ''Accelerate decision timeline; ''; if days_since_last_advancement ≥14 add ''Increase communication frequency; ''. - experience_risk_flag (first match): if days_since_last_advancement ≥21 and not archived → ''High Abandonment Risk''; else if canceled_interviews ≥2 → ''Poor Interview Experience''; else if transparency_score ≤2 and total_interviews ≥3 → ''Low Process Transparency''; else if timeline_experience_score ≤2 and total_lifecycle_days ≥60 → ''Extended Timeline Concern''; else ''Normal''. - calculated_at = current timestamp at model execution. - Final result ordered by overall_candidate_experience_score descending, then total_lifecycle_days ascending.'

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`，第 1–1 行：

```sql
round(cl.completed_interviews*100.0/nullif(cl.total_interviews,0),1) completion_rate
```

单改/诊断：`records/019_reruns_impl-001_lever__candidate_experience_insights.json#completion_zero`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 764216/22017288 | 764216/22011712 | 0/5576 |
| L1 | 764216/22017288 | 764216/22011712 | 0/5576 |
| L2 | 764216/22017288 | 764216/22011712 | 0/5576 |
| L3 | 764216/22017288 | 764216/22011712 | 0/5576 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> business_logic: 'Build candidate_journey by joining: - intermediate.int_lever__candidate_lifecycle (cl) to staging.stg_lever__opportunity (o) on opportunity_id, left join intermediate.int_lever__contact_info (c) on contact_id, join staging.stg_lever__stage (s) on o.stage_id, and left join staging.stg_lever__archive_reason (ar) on o.archived_reason_id. - Derive fields: - activity_status: constant ''Active''. - lifecycle_speed_category: total_lifecycle_days bucketed as ≤14 ''Fast'', ≤30 ''Standard'', ≤60 ''Slow'', else ''Very Slow''. - interview_completion_rate_pct: completed_interviews divided by total_interviews times 100, rounded to 1 decimal; no explicit zero-division guard; NULLs propagate. - Carry through totals (interviews, completed, canceled), avg_interview_duration_minutes, total_interview_time_minutes, avg_recommendation_score, feedback_completion_rate_pct, is_archived, application_date (o.created_at), last_interaction_at, last_advanced_at, current_stage (s.stage_name), archive_reason (ar.archive_reason_title). Compute communication_quality per opportunity_id: - days_from_application_to_last_contact: difference in days between last_interaction_at and application_date; NULL if either is NULL. - days_from_application_to_last_advancement: difference in days between last_advanced_at and application_date; NULL if either is NULL. - response_quality from days_since_last_advancement: ≤1 ''Excellent Response (≤1 day)''; ≤3 ''Good Response (2-3 days)''; ≤7 ''Moderate Response (4-7 days)''; ≤14 ''Slow Response (8-14 days)''; else ''Very Slow Response (>14 days)'' (NULL falls to the else bucket). - transparency_score from feedback_completion_rate_pct: ≥90→5; ≥70→4; ≥50→3; ≥30→2; else 1 (NULL falls to 1). Compute interview_experience per opportunity_id: - interview_experience_score: - If total_interviews = 0 → NULL. - Else if completion rate ≥95 and avg duration in 30–90 minutes → 5. - Else if completion rate ≥80 and avg duration in 20–120 minutes → 4. - Else if completion rate ≥60 → 3; else if ≥40 → 2; else → 1. - interview_burden_category: - If total_interviews = 0 → ''No Interviews''. - Else if total_interviews ≤2 and total_interview_time_minutes ≤120 → ''Light Process''; ≤4 and ≤240 → ''Standard Process''; ≤6 and ≤360 → ''Intensive Process''; else ''Heavy Process''. - interview_consistency_score: - If total_interviews = 0 → NULL. - Else if canceled_interviews = 0 → 5; else if canceled/total ≤10% → 4; ≤20% → 3; ≤30% → 2; else → 1. Compute outcome_fairness per opportunity_id: - outcome_fairness_score: - If not archived → NULL. - Else 5 for stage indicating hire/accept or reason indicating withdrew/declined; 4 for offer stage or skills/qualification mismatch; 3 for culture fit issues or other; 2 if rejected without a stated reason. - process_completeness_assessment: - If not archived → ''In Progress''; else if avg_recommendation_score ≥4 and stage does not indicate hire → ''Potential Mismatch''; else if avg_recommendation_score ≤2 → ''Consistent Outcome''; else if avg_recommendation_score is NULL → ''Incomplete Process''; else → ''Normal Process''. Compute timeline_experience per opportunity_id: - timeline_experience_score compares lifecycle_speed_category to labels ''Fast Track (≤7 days)'', ''Normal (8-30 days)'', ''Extended (31-60 days)'', ''Long Process (>60 days)''; because candidate_journey uses ''Fast''/''Standard''/''Slow''/''Very Slow'', no label matches and the else branch applies, yielding 1 for all rows. - candidate_anxiety_level from activity_status: ''Active'' maps to ''Low Anxiety''. Final projection and derived fields: - overall_candidate_experience_score: weighted average of subscores (transparency 20%, interview experience 25%, interview consistency 15%, outcome fairness 20%, timeline 20%), defaulting missing subscores to 3, rounded to 1 decimal. - experience_grade from the same rounded overall score: ≥4.5 ''Exceptional Experience''; ≥4.0 ''Excellent Experience''; ≥3.5 ''Good Experience''; ≥3.0 ''Average Experience''; ≥2.0 ''Below Average Experience''; else ''Poor Experience''. - improvement_recommendations: concatenate in this order (each fragment ends with ''; '' and no trimming): if transparency_score ≤2 add ''Improve feedback transparency; ''; if interview_experience_score ≤2 add ''Optimize interview process; ''; if timeline_experience_score ≤2 add ''Accelerate decision timeline; ''; if days_since_last_advancement ≥14 add ''Increase communication frequency; ''. - experience_risk_flag (first match): if days_since_last_advancement ≥21 and not archived → ''High Abandonment Risk''; else if canceled_interviews ≥2 → ''Poor Interview Experience''; else if transparency_score ≤2 and total_interviews ≥3 → ''Low Process Transparency''; else if timeline_experience_score ≤2 and total_lifecycle_days ≥60 → ''Extended Timeline Concern''; else ''Normal''. - calculated_at = current timestamp at model execution. - Final result ordered by overall_candidate_experience_score descending, then total_lifecycle_days ascending.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### timeline_score

- 类别：代码写错；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

同一SQL已经输出timeline_experience_score=1，overall表达式却把这一项写成3；正确计算意图有代码内证据。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: overall_candidate_experience_score
>         data_type: DECIMAL(17,1)
>         description: Weighted subscore average (20% transparency, 25% interview experience, 15% consistency, 20% fairness, 20% timeline), missing subscores default to 3, rounded to 1 decimal

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`，第 1–1 行：

```sql
round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1) overall_candidate_experience_score
```

单改/诊断：`records/019_reruns_impl-001_lever__candidate_experience_insights.json#timeline_score`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 764216/22017288 | 764216/22011712 | 0/5576 |
| L1 | 764216/22017288 | 764216/22011712 | 0/5576 |
| L2 | 764216/22017288 | 764216/22011712 | 0/5576 |
| L3 | 764216/22017288 | 764216/22011712 | 0/5576 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> - name: overall_candidate_experience_score
>         data_type: DECIMAL(17,1)
>         description: Weighted subscore average (20% transparency, 25% interview experience, 15% consistency, 20% fairness, 20% timeline), missing subscores default to 3, rounded to 1 decimal

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### recommendations

- 类别：Quiet Downgrade；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

有契约条件和候选输入，却把所有improvement_recommendations写成空串；本表不在最终报告点名的占位表名单中。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: improvement_recommendations
>         data_type: VARCHAR
>         description: Concatenation of advisory fragments (fixed order, each ends with '; ') for triggered conditions; empty string if none

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`，第 1–1 行：

```sql
'' improvement_recommendations
```

单改/诊断：`records/019_reruns_impl-001_lever__candidate_experience_insights.json#recommendations`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 764216/22017288 | 764216/22011712 | 0/5576 |
| L1 | 764216/22017288 | 764216/22011712 | 0/5576 |
| L2 | 764216/22017288 | 764216/22011712 | 0/5576 |
| L3 | 764216/22017288 | 764216/22011712 | 0/5576 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> - name: improvement_recommendations
>         data_type: VARCHAR
>         description: Concatenation of advisory fragments (fixed order, each ends with '; ') for triggered conditions; empty string if none

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### gold_join_multiplicity

- 类别：其他；角色：主要；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

gold将同键的四份子结果再次连接，出现n^5重数；agent结果与契约每opportunity一行的粒度一致。019该改动是复现gold重数的诊断，不是建议修复agent。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build candidate_journey by joining: - intermediate.int_lever__candidate_lifecycle (cl) to staging.stg_lever__opportunity (o) on opportunity_id, left join intermediate.int_lever__contact_info (c) on contact_id, join staging.stg_lever__stage (s) on o.stage_id, and left join staging.stg_lever__archive_reason (ar) on o.archived_reason_id. - Derive fields: - activity_status: constant ''Active''. - lifecycle_speed_category: total_lifecycle_days bucketed as ≤14 ''Fast'', ≤30 ''Standard'', ≤60 ''Slow'', else ''Very Slow''. - interview_completion_rate_pct: completed_interviews divided by total_interviews times 100, rounded to 1 decimal; no explicit zero-division guard; NULLs propagate. - Carry through totals (interviews, completed, canceled), avg_interview_duration_minutes, total_interview_time_minutes, avg_recommendation_score, feedback_completion_rate_pct, is_archived, application_date (o.created_at), last_interaction_at, last_advanced_at, current_stage (s.stage_name), archive_reason (ar.archive_reason_title). Compute communication_quality per opportunity_id: - days_from_application_to_last_contact: difference in days between last_interaction_at and application_date; NULL if either is NULL. - days_from_application_to_last_advancement: difference in days between last_advanced_at and application_date; NULL if either is NULL. - response_quality from days_since_last_advancement: ≤1 ''Excellent Response (≤1 day)''; ≤3 ''Good Response (2-3 days)''; ≤7 ''Moderate Response (4-7 days)''; ≤14 ''Slow Response (8-14 days)''; else ''Very Slow Response (>14 days)'' (NULL falls to the else bucket). - transparency_score from feedback_completion_rate_pct: ≥90→5; ≥70→4; ≥50→3; ≥30→2; else 1 (NULL falls to 1). Compute interview_experience per opportunity_id: - interview_experience_score: - If total_interviews = 0 → NULL. - Else if completion rate ≥95 and avg duration in 30–90 minutes → 5. - Else if completion rate ≥80 and avg duration in 20–120 minutes → 4. - Else if completion rate ≥60 → 3; else if ≥40 → 2; else → 1. - interview_burden_category: - If total_interviews = 0 → ''No Interviews''. - Else if total_interviews ≤2 and total_interview_time_minutes ≤120 → ''Light Process''; ≤4 and ≤240 → ''Standard Process''; ≤6 and ≤360 → ''Intensive Process''; else ''Heavy Process''. - interview_consistency_score: - If total_interviews = 0 → NULL. - Else if canceled_interviews = 0 → 5; else if canceled/total ≤10% → 4; ≤20% → 3; ≤30% → 2; else → 1. Compute outcome_fairness per opportunity_id: - outcome_fairness_score: - If not archived → NULL. - Else 5 for stage indicating hire/accept or reason indicating withdrew/declined; 4 for offer stage or skills/qualification mismatch; 3 for culture fit issues or other; 2 if rejected without a stated reason. - process_completeness_assessment: - If not archived → ''In Progress''; else if avg_recommendation_score ≥4 and stage does not indicate hire → ''Potential Mismatch''; else if avg_recommendation_score ≤2 → ''Consistent Outcome''; else if avg_recommendation_score is NULL → ''Incomplete Process''; else → ''Normal Process''. Compute timeline_experience per opportunity_id: - timeline_experience_score compares lifecycle_speed_category to labels ''Fast Track (≤7 days)'', ''Normal (8-30 days)'', ''Extended (31-60 days)'', ''Long Process (>60 days)''; because candidate_journey uses ''Fast''/''Standard''/''Slow''/''Very Slow'', no label matches and the else branch applies, yielding 1 for all rows. - candidate_anxiety_level from activity_status: ''Active'' maps to ''Low Anxiety''. Final projection and derived fields: - overall_candidate_experience_score: weighted average of subscores (transparency 20%, interview experience 25%, interview consistency 15%, outcome fairness 20%, timeline 20%), defaulting missing subscores to 3, rounded to 1 decimal. - experience_grade from the same rounded overall score: ≥4.5 ''Exceptional Experience''; ≥4.0 ''Excellent Experience''; ≥3.5 ''Good Experience''; ≥3.0 ''Average Experience''; ≥2.0 ''Below Average Experience''; else ''Poor Experience''. - improvement_recommendations: concatenate in this order (each fragment ends with ''; '' and no trimming): if transparency_score ≤2 add ''Improve feedback transparency; ''; if interview_experience_score ≤2 add ''Optimize interview process; ''; if timeline_experience_score ≤2 add ''Accelerate decision timeline; ''; if days_since_last_advancement ≥14 add ''Increase communication frequency; ''. - experience_risk_flag (first match): if days_since_last_advancement ≥21 and not archived → ''High Abandonment Risk''; else if canceled_interviews ≥2 → ''Poor Interview Experience''; else if transparency_score ≤2 and total_interviews ≥3 → ''Low Process Transparency''; else if timeline_experience_score ≤2 and total_lifecycle_days ≥60 → ''Extended Timeline Concern''; else ''Normal''. - calculated_at = current timestamp at model execution. - Final result ordered by overall_candidate_experience_score descending, then total_lifecycle_days ascending.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`，第 1–1 行：

```sql
FROM calc
```

单改/诊断：`records/019_reruns_impl-001_lever__candidate_experience_insights.json#gold_join_multiplicity`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 764216/22017288 | 764216/2292648 | 0/19724640 |
| L1 | 764216/22017288 | 764216/2292648 | 0/19724640 |
| L2 | 764216/22017288 | 764216/2292648 | 0/19724640 |
| L3 | 764216/22017288 | 764216/2292648 | 0/19724640 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> business_logic: 'Build candidate_journey by joining: - intermediate.int_lever__candidate_lifecycle (cl) to staging.stg_lever__opportunity (o) on opportunity_id, left join intermediate.int_lever__contact_info (c) on contact_id, join staging.stg_lever__stage (s) on o.stage_id, and left join staging.stg_lever__archive_reason (ar) on o.archived_reason_id. - Derive fields: - activity_status: constant ''Active''. - lifecycle_speed_category: total_lifecycle_days bucketed as ≤14 ''Fast'', ≤30 ''Standard'', ≤60 ''Slow'', else ''Very Slow''. - interview_completion_rate_pct: completed_interviews divided by total_interviews times 100, rounded to 1 decimal; no explicit zero-division guard; NULLs propagate. - Carry through totals (interviews, completed, canceled), avg_interview_duration_minutes, total_interview_time_minutes, avg_recommendation_score, feedback_completion_rate_pct, is_archived, application_date (o.created_at), last_interaction_at, last_advanced_at, current_stage (s.stage_name), archive_reason (ar.archive_reason_title). Compute communication_quality per opportunity_id: - days_from_application_to_last_contact: difference in days between last_interaction_at and application_date; NULL if either is NULL. - days_from_application_to_last_advancement: difference in days between last_advanced_at and application_date; NULL if either is NULL. - response_quality from days_since_last_advancement: ≤1 ''Excellent Response (≤1 day)''; ≤3 ''Good Response (2-3 days)''; ≤7 ''Moderate Response (4-7 days)''; ≤14 ''Slow Response (8-14 days)''; else ''Very Slow Response (>14 days)'' (NULL falls to the else bucket). - transparency_score from feedback_completion_rate_pct: ≥90→5; ≥70→4; ≥50→3; ≥30→2; else 1 (NULL falls to 1). Compute interview_experience per opportunity_id: - interview_experience_score: - If total_interviews = 0 → NULL. - Else if completion rate ≥95 and avg duration in 30–90 minutes → 5. - Else if completion rate ≥80 and avg duration in 20–120 minutes → 4. - Else if completion rate ≥60 → 3; else if ≥40 → 2; else → 1. - interview_burden_category: - If total_interviews = 0 → ''No Interviews''. - Else if total_interviews ≤2 and total_interview_time_minutes ≤120 → ''Light Process''; ≤4 and ≤240 → ''Standard Process''; ≤6 and ≤360 → ''Intensive Process''; else ''Heavy Process''. - interview_consistency_score: - If total_interviews = 0 → NULL. - Else if canceled_interviews = 0 → 5; else if canceled/total ≤10% → 4; ≤20% → 3; ≤30% → 2; else → 1. Compute outcome_fairness per opportunity_id: - outcome_fairness_score: - If not archived → NULL. - Else 5 for stage indicating hire/accept or reason indicating withdrew/declined; 4 for offer stage or skills/qualification mismatch; 3 for culture fit issues or other; 2 if rejected without a stated reason. - process_completeness_assessment: - If not archived → ''In Progress''; else if avg_recommendation_score ≥4 and stage does not indicate hire → ''Potential Mismatch''; else if avg_recommendation_score ≤2 → ''Consistent Outcome''; else if avg_recommendation_score is NULL → ''Incomplete Process''; else → ''Normal Process''. Compute timeline_experience per opportunity_id: - timeline_experience_score compares lifecycle_speed_category to labels ''Fast Track (≤7 days)'', ''Normal (8-30 days)'', ''Extended (31-60 days)'', ''Long Process (>60 days)''; because candidate_journey uses ''Fast''/''Standard''/''Slow''/''Very Slow'', no label matches and the else branch applies, yielding 1 for all rows. - candidate_anxiety_level from activity_status: ''Active'' maps to ''Low Anxiety''. Final projection and derived fields: - overall_candidate_experience_score: weighted average of subscores (transparency 20%, interview experience 25%, interview consistency 15%, outcome fairness 20%, timeline 20%), defaulting missing subscores to 3, rounded to 1 decimal. - experience_grade from the same rounded overall score: ≥4.5 ''Exceptional Experience''; ≥4.0 ''Excellent Experience''; ≥3.5 ''Good Experience''; ≥3.0 ''Average Experience''; ≥2.0 ''Below Average Experience''; else ''Poor Experience''. - improvement_recommendations: concatenate in this order (each fragment ends with ''; '' and no trimming): if transparency_score ≤2 add ''Improve feedback transparency; ''; if interview_experience_score ≤2 add ''Optimize interview process; ''; if timeline_experience_score ≤2 add ''Accelerate decision timeline; ''; if days_since_last_advancement ≥14 add ''Increase communication frequency; ''. - experience_risk_flag (first match): if days_since_last_advancement ≥21 and not archived → ''High Abandonment Risk''; else if canceled_interviews ≥2 → ''Poor Interview Experience''; else if transparency_score ≤2 and total_interviews ≥3 → ''Low Process Transparency''; else if timeline_experience_score ≤2 and total_lifecycle_days ≥60 → ''Extended Timeline Concern''; else ''Normal''. - calculated_at = current timestamp at model execution. - Final result ordered by overall_candidate_experience_score descending, then total_lifecycle_days ascending.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
