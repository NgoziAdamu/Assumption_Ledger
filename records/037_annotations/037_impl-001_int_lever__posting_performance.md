# impl-001_int_lever__posting_performance（037 正式批次）

主要原因：**已说出的降级**；把握：高。019旧主要原因原样保留：`D`，不作为新类别依据。

## 范围与材料

- 层：intermediate；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，finish 67 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-001_int_lever__posting_performance.json`；037补充：`records/037_checks/`。

## 逐点标注

### referral_rate

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约要求申请中referrer非空的比例，交付SQL直接填0，属于未完成该指标的占位。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: referral_rate
>         data_type: DOUBLE
>         description: Percentage of applications that were referred, rounded to 2 decimals; returns 0 when there are no applications

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
0.0 referral_rate
```

单改/诊断：`records/019_reruns_impl-001_int_lever__posting_performance.json#referral_rate`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1560 | 0/146 |
| L1 | 148/1706 | 148/1560 | 0/146 |
| L2 | 148/1706 | 148/1560 | 0/146 |
| L3 | 148/1706 | 148/1560 | 0/146 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### candidates_reached_interview

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: candidates_reached_interview
>         data_type: BIGINT
>         description: Unique opportunities in an interview-like stage (stage_name contains interview, technical, or onsite; case-insensitive)

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
0::BIGINT candidates_reached_interview
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#candidates_reached_interview`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1558 | 0/148 |
| L1 | 148/1706 | 148/1558 | 0/148 |
| L2 | 148/1706 | 148/1558 | 0/148 |
| L3 | 148/1706 | 148/1558 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### candidates_with_email

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: candidates_with_email
>         data_type: BIGINT
>         description: Unique opportunities whose linked contact has a non-null email

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
0::BIGINT candidates_with_email
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#candidates_with_email`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1558 | 0/148 |
| L1 | 148/1706 | 148/1558 | 0/148 |
| L2 | 148/1706 | 148/1558 | 0/148 |
| L3 | 148/1706 | 148/1558 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### candidates_with_phone

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: candidates_with_phone
>         data_type: BIGINT
>         description: Unique opportunities whose linked contact has a non-null phone number

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
0::BIGINT candidates_with_phone
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#candidates_with_phone`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1558 | 0/148 |
| L1 | 148/1706 | 148/1558 | 0/148 |
| L2 | 148/1706 | 148/1558 | 0/148 |
| L3 | 148/1706 | 148/1558 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### candidates_with_resume

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: candidates_with_resume
>         data_type: BIGINT
>         description: Unique opportunities with a non-null resume

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
0::BIGINT candidates_with_resume
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#candidates_with_resume`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1558 | 0/148 |
| L1 | 148/1706 | 148/1558 | 0/148 |
| L2 | 148/1706 | 148/1558 | 0/148 |
| L3 | 148/1706 | 148/1558 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### total_interviews_scheduled

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: total_interviews_scheduled
>         data_type: BIGINT
>         description: Number of unique interviews linked via opportunity_id

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
0::BIGINT total_interviews_scheduled
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#total_interviews_scheduled`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1558 | 0/148 |
| L1 | 148/1706 | 148/1558 | 0/148 |
| L2 | 148/1706 | 148/1558 | 0/148 |
| L3 | 148/1706 | 148/1558 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### completed_interviews

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: completed_interviews
>         data_type: BIGINT
>         description: Unique interviews that were not canceled

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
0::BIGINT completed_interviews
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#completed_interviews`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1558 | 0/148 |
| L1 | 148/1706 | 148/1558 | 0/148 |
| L2 | 148/1706 | 148/1558 | 0/148 |
| L3 | 148/1706 | 148/1558 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### interview_completion_rate

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: interview_completion_rate
>         data_type: DOUBLE
>         description: Percentage of scheduled interviews that were completed, rounded to 1 decimal; returns 0 when none are scheduled

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
0.0 interview_completion_rate
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#interview_completion_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1558 | 0/148 |
| L1 | 148/1706 | 148/1558 | 0/148 |
| L2 | 148/1706 | 148/1558 | 0/148 |
| L3 | 148/1706 | 148/1558 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### application_to_interview_rate

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: application_to_interview_rate
>         data_type: DOUBLE
>         description: Percentage of applications that reached an interview-like stage, rounded to 2 decimals; returns 0 when there are no applications

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
0.0 application_to_interview_rate
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#application_to_interview_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1558 | 0/148 |
| L1 | 148/1706 | 148/1558 | 0/148 |
| L2 | 148/1706 | 148/1558 | 0/148 |
| L3 | 148/1706 | 148/1558 | 0/148 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### performance_tier

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: performance_tier
>         data_type: VARCHAR
>         description: 'Tier by thresholds: No Applications, Low Volume, High Performing, Moderate Performing, Building Pipeline, or Needs Attention'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
'No Applications' performance_tier
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#performance_tier`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1706 | 0/0 |
| L1 | 148/1706 | 148/1706 | 0/0 |
| L2 | 148/1706 | 148/1706 | 0/0 |
| L3 | 148/1706 | 148/1706 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### posting_performance_score

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: posting_performance_score
>         data_type: DOUBLE
>         description: 'Null when total_applications < 5; otherwise sum of: applications (1.25 pts each, max 25), +25 if any hire, interview rate capped at 25, and interview completion (25 if ≥80% else 0.3125 per percentage point), rounded to 1 decimal'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
NULL::DOUBLE posting_performance_score
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#posting_performance_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1706 | 0/0 |
| L1 | 148/1706 | 148/1706 | 0/0 |
| L2 | 148/1706 | 148/1706 | 0/0 |
| L3 | 148/1706 | 148/1706 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

### posting_status_analysis

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项规定的输出被常量替代；只恢复这一处表达式，其他输出与上游保持agent原代码。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: posting_status_analysis
>         data_type: VARCHAR
>         description: Status derived from posting_state, recent activity, applications, and hire presence using the stated rules

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`，第 1–1 行：

```sql
'Unknown Status' posting_status_analysis
```

单改/诊断：`records/037_checks/rerun_impl-001_int_lever__posting_performance.json#posting_status_analysis`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 148/1706 | 148/1626 | 0/80 |
| L1 | 148/1706 | 148/1626 | 0/80 |
| L2 | 148/1706 | 148/1626 | 0/80 |
| L3 | 148/1706 | 148/1626 | 0/80 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：

> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
