# impl-001_lever__departmental_hiring_trends（037 正式批次）

主要原因：**已说出的降级**；把握：高。019旧主要原因原样保留：`D`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，finish 67 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-001_lever__departmental_hiring_trends.json`；037补充：`records/037_checks/`。

## 逐点标注

### referral_count

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约数有referrer的distinct application；agent数distinct referrer，漏算同一推荐人关联的多个申请。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: referral_rate
>         data_type: DOUBLE
>         description: Percentage with 2 decimals; referred applications divided by total applications *100; 0 when no applications; joined on department+team only

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 13–13 行：

```sql
count(DISTINCT referrer_user_id) AS referred
```

单改/诊断：`records/019_reruns_impl-001_lever__departmental_hiring_trends.json#referral_count`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1420 | 148/1413 | 0/7 |
| L1 | 148/1420 | 148/1413 | 0/7 |
| L2 | 148/1420 | 148/1413 | 0/7 |
| L3 | 148/1420 | 148/1413 | 0/7 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> - name: referral_rate
>         data_type: DOUBLE
>         description: Percentage with 2 decimals; referred applications divided by total applications *100; 0 when no applications; joined on department+team only

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### cost_tier

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

未实现成本分类，固定No Data；即使无hire也没有输出契约要求的No Hires。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: cost_efficiency_tier
>         data_type: VARCHAR
>         description: Tier by interview_hours_per_hire thresholds (≤10 Highly Efficient, ≤20 Efficient, ≤40 Moderate Efficiency, else Low Efficiency; No Hires when hires=0); COALESCE to 'No Data' if join missing; replicated across rows

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 38–38 行：

```sql
'No Data' AS cost_efficiency_tier
```

单改/诊断：`records/019_reruns_impl-001_lever__departmental_hiring_trends.json#cost_tier`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1420 | 148/1272 | 0/148 |
| L1 | 148/1420 | 148/1272 | 0/148 |
| L2 | 148/1420 | 148/1272 | 0/148 |
| L3 | 148/1420 | 148/1272 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### total_interviews_conducted

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: total_interviews_conducted
>         data_type: BIGINT
>         description: Distinct interviews at department+team; replicated across rows; COALESCE to 0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 32–32 行：

```sql
0::BIGINT AS total_interviews_conducted
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__departmental_hiring_trends.json#total_interviews_conducted`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1420 | 148/1272 | 0/148 |
| L1 | 148/1420 | 148/1272 | 0/148 |
| L2 | 148/1420 | 148/1272 | 0/148 |
| L3 | 148/1420 | 148/1272 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### unique_interviewers

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: unique_interviewers
>         data_type: BIGINT
>         description: Distinct interviewer users at department+team; replicated across rows; COALESCE to 0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 33–33 行：

```sql
0::BIGINT AS unique_interviewers
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__departmental_hiring_trends.json#unique_interviewers`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1420 | 148/1272 | 0/148 |
| L1 | 148/1420 | 148/1272 | 0/148 |
| L2 | 148/1420 | 148/1272 | 0/148 |
| L3 | 148/1420 | 148/1272 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_interview_duration_minutes

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_interview_duration_minutes
>         data_type: DOUBLE
>         description: Average interview duration in minutes at department+team; NULL→0 via COALESCE; replicated across rows

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 34–34 行：

```sql
0.0 AS avg_interview_duration_minutes
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__departmental_hiring_trends.json#avg_interview_duration_minutes`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1420 | 148/1272 | 0/148 |
| L1 | 148/1420 | 148/1272 | 0/148 |
| L2 | 148/1420 | 148/1272 | 0/148 |
| L3 | 148/1420 | 148/1272 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### interview_completion_rate

- 类别：已说出的降级；角色：主要；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: interview_completion_rate
>         data_type: DOUBLE
>         description: Percentage with 2 decimals; completed interviews (not canceled) divided by total interviews *100 at department+team; 0 when no interviews; replicated; COALESCE to 0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 32–32 行：

```sql
0.0 AS interview_completion_rate
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__departmental_hiring_trends.json#interview_completion_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1420 | 148/1124 | 0/296 |
| L1 | 148/1420 | 148/1124 | 0/296 |
| L2 | 148/1420 | 148/1124 | 0/296 |
| L3 | 148/1420 | 148/1124 | 0/296 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_candidate_experience_score

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_candidate_experience_score
>         data_type: DOUBLE
>         description: Average overall candidate experience score at department+team; NULL→0 via COALESCE; replicated across rows

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 34–34 行：

```sql
0.0 AS avg_candidate_experience_score
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__departmental_hiring_trends.json#avg_candidate_experience_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1420 | 148/1272 | 0/148 |
| L1 | 148/1420 | 148/1272 | 0/148 |
| L2 | 148/1420 | 148/1272 | 0/148 |
| L3 | 148/1420 | 148/1272 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_screening_pass_rate

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_screening_pass_rate
>         data_type: DOUBLE
>         description: Average screening pass rate from hiring funnel metrics at department+team; NULL→0 via COALESCE; replicated across rows

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 35–35 行：

```sql
0.0 AS avg_screening_pass_rate
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__departmental_hiring_trends.json#avg_screening_pass_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1420 | 148/1372 | 0/48 |
| L1 | 148/1420 | 148/1372 | 0/48 |
| L2 | 148/1420 | 148/1272 | 0/148 |
| L3 | 148/1420 | 148/1272 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### high_efficiency_postings

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: high_efficiency_postings
>         data_type: BIGINT
>         description: Distinct postings with hiring_efficiency_grade='High Efficiency (≥10%)' at department+team; replicated across rows; COALESCE to 0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 36–36 行：

```sql
0::BIGINT AS high_efficiency_postings
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__departmental_hiring_trends.json#high_efficiency_postings`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1420 | 148/1272 | 0/148 |
| L1 | 148/1420 | 148/1272 | 0/148 |
| L2 | 148/1420 | 148/1272 | 0/148 |
| L3 | 148/1420 | 148/1272 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### department_strength_referral

- 类别：已说出的降级；角色：参与；把握：中。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

只恢复契约规定的首个referral>=30分支；文字未写死，用诊断所得gold表达测量该分支贡献，不把这个英文标签当契约要求。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '- Build department_posting_base from postings: - Dimensions defaulted via COALESCE: department=''Unknown Department'', team=''Unknown Team'', location=''Unknown Location'', level=''Unknown Level'', commitment_type=''Unknown Commitment''. - Keep posting_id and timestamps; derive posting_month and posting_quarter by truncating created_at. - application_volume (dept+team+location+level+commitment_type+month+quarter): - Distinct counts: applications, candidates, opportunities, postings; referred applications where referrer_user_id is present. - referral_rate = referred applications / total applications * 100, rounded to 2 decimals; 0 when no applications. - avg_applications_per_posting = total applications / active postings, rounded to 1 decimal; NULL when active postings=0 (later COALESCE to 0). - hiring_outcomes (dept+team): - candidates_hired: distinct opportunities with stage name containing ''hire'' or ''accept''; offers_extended: distinct opportunities with stage name containing ''offer''. - Averages for hired/accepted only: time_to_hire (lifecycle days) and interviews_per_hire. - hire_conversion_rate = candidates_hired / distinct opportunities * 100, rounded to 2 decimals; 0 when no opportunities. - offer_acceptance_rate = candidates_hired / offers_extended * 100, rounded to 2 decimals; 0 when no offers. - interview_metrics (dept+team): - total_interviews_conducted: distinct interviews; completed when not canceled; canceled when canceled. - unique_interviewers: distinct interviewer users; avg_interview_duration: average interview duration (minutes); total_interview_time_minutes: sum of durations. - interview_completion_rate = completed / total * 100, rounded to 2 decimals; 0 when no interviews. - feedback_completion_rate = 100 when any feedback exists else 0, rounded to 2 decimals. - candidate_quality (dept+team): - avg_candidate_experience_score: average overall_candidate_experience_score. - positive_experience_rate = exceptional/excellent experience opportunities / total opportunities * 100, rounded to 2 decimals; 0 when no opportunities. - avg_screening_pass_rate: average application_to_screening_rate; high_efficiency_postings: distinct postings with hiring_efficiency_grade=''High Efficiency (≥10%)''. - cost_efficiency (dept+team): - Join dpb to application_volume, hiring_outcomes, and interview_metrics on dept+team; group by dept+team. - total_interview_hours = sum(total_interview_time_minutes) / 60.0. - interview_hours_per_hire = total_interview_hours / total hires, rounded to 1 decimal; NULL when no hires (later COALESCE to 0). - applications_per_hire = sum(total_applications) / total hires, rounded to 1 decimal; NULL when no hires (later COALESCE to 0). - hires_per_posting = total hires / sum(active_postings), rounded to 2 decimals; 0 when no active postings. - cost_efficiency_tier by interview_hours_per_hire: ≤10 Highly Efficient, ≤20 Efficient, ≤40 Moderate Efficiency, >40 Low Efficiency; No Hires when hires=0 (later COALESCE to ''No Data'' if join missing). - Note: dept+team joins cause ho/im to repeat across each application_volume row and posting; sums aggregate repeated rows (scaled by both postings and application_volume rows per dept+team), while ratios dividing repeated sums (e.g., interview_hours_per_hire) cancel the scaling. - Final assembly: - Join department_posting_base to all aggregates on dept+team only, replicating dept+team metrics across each posting’s location/level/commitment slice and across application_volume slices. - Keep rows where application_volume.total_applications>0 OR application_volume.active_postings>0. - Ranks (global across the final set): hiring_volume_rank by candidates_hired DESC, conversion_efficiency_rank by hire_conversion_rate DESC, candidate_experience_rank by avg_candidate_experience_score DESC; ties share rank with gaps. - department_performance_score (0–100, rounded to 0 decimals, clamped): min(25, hires*2.5) + (hire_conversion_rate*0.2) + (interview_completion_rate*0.2) + (positive_experience_rate*0.15) + ([cost_efficiency_tier in {Highly Efficient, Efficient} → 20 else 10]*0.2). - performance_tier: ≥75 Top Performing Department; ≥60 High Performing Department; ≥45 Standard Performing Department; else if total_applications≥10 Underperforming Department; otherwise Low Activity Department. - department_strength priority: referral_rate≥30 → offer_acceptance_rate≥80 → avg_candidate_experience_score≥4.0 → avg_time_to_hire_days≤30 → cost_efficiency_tier in {Highly Efficient, Efficient} → else Standard Operations. - calculated_at = current_timestamp; final output ordered by department_performance_score DESC, then total_applications DESC.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 46–46 行：

```sql
'Standard Operations' AS department_strength
```

单改/诊断：`records/037_checks/rerun_impl-001_lever__departmental_hiring_trends.json#department_strength_referral`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1420 | 148/1341 | 0/79 |
| L1 | 148/1420 | 148/1341 | 0/79 |
| L2 | 148/1420 | 148/1341 | 0/79 |
| L3 | 148/1420 | 148/1341 | 0/79 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
