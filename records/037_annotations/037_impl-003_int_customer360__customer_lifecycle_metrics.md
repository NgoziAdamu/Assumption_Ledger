# impl-003_int_customer360__customer_lifecycle_metrics（037 正式批次）

主要原因：**其他**；把握：中。019旧主要原因原样保留：`O`，不作为新类别依据。

## 范围与材料

- 层：intermediate；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_lifecycle_metrics.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-003_int_customer360__customer_lifecycle_metrics.json`；037补充：`records/037_checks/`。

## 逐点标注

### frequency_score

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确active30/60高分分支，agent只按交易计数分档；缺的是规定的算法，不是数据事实。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: frequency_score
>         data_type: INTEGER
>         description: Engagement frequency score (1–5) from platform consistency and recent activity per ordered rules

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_lifecycle_metrics.sql`，第 23–23 行：

```sql
case when platform_sum>=2 and active_90_days=1 then 3 when active_180_days=1 then 2 else 1 end as frequency_score
```

单改/诊断：`records/019_reruns_impl-003_int_customer360__customer_lifecycle_metrics.json#frequency_score`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2641/2657 | 2637/2637 | 4/20 |
| L1 | 2641/2657 | 2637/2637 | 4/20 |
| L2 | 2641/2657 | 2637/2637 | 4/20 |
| L3 | 2641/2657 | 2637/2637 | 4/20 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：

> - name: frequency_score
>         data_type: INTEGER
>         description: Engagement frequency score (1–5) from platform consistency and recent activity per ordered rules

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### stochastic_evaluation

- 类别：其他；角色：主要；把握：中。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约允许random()模拟；不同执行产生不同交易数。复用019共同屏蔽随机输出的诊断，不能把随机种子差异归为agent错误。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Starting from intermediate.int_customer360__customer_behavior_analysis (one row per resolved customer), compute lifecycle metrics and enrichments: - Activity windows and recency: - days_since_last_activity = number of days between customer_last_activity and today; NULL if customer_last_activity is missing. - active_X_days flags (X ∈ {30,60,90,180,365}) = 1 if customer_last_activity occurred within X days of today, else 0; missing customer_last_activity yields 0. - Lifecycle stage (first match wins): - ''Acquisition'' if account_age_days ≤ 30 - ''Activation'' if account_age_days ≤ 90 and last_activity within 30 days - ''Growth'' if account_age_days ≤ 365 and last_activity within 60 days - ''Maturity'' if account_age_days > 365 and last_activity within 90 days - ''Dormant'' if last_activity older than 180 days - Else ''Retention'' - Note: NULL account_age_days or last_activity causes earlier conditions to fail and typically falls through to ''Retention''. - Cohort and platform consistency: - acquisition_cohort_month = month of the first touchpoint (truncated to month); NULL if first_touchpoint is missing. - platform_consistency_score ∈ {1,2,3}: sum of presence flags (in_marketo + in_stripe + in_zendesk); 3 if sum ≥ 3, 2 if sum = 2, else 1. NULL in any flag leads to the else path → 1. - Value and engagement scores: - estimated_customer_value (DECIMAL(6,2)) by customer_segment: - ''Champion'' 5000.00; ''Loyal Customer'' 3500.00; ''Potential Loyalist'' 2000.00; ''New Customer'' 800.00; ''At Risk'' 1200.00; ''Hibernating'' 500.00; else 200.00. - frequency_score (1–5): 5 if platform_consistency_score = 3 and active_30_days = 1; 4 if platform_consistency_score ≥ 2 and active_60_days = 1; 3 if platform_consistency_score ≥ 2 and active_90_days = 1; 2 if active_180_days = 1; else 1. - recency_score (1–5) by days_since_last_activity: 5 (≤7), 4 (≤30), 3 (≤60), 2 (≤180), else 1; NULL days_since_last_activity maps to 1. - estimated_transaction_count (DOUBLE): simulated per run: - If segment in (''Champion'',''Loyal Customer'') → integer 2–9 - If ''Potential Loyalist'' → integer 1–4 - Else → integer 0–1 - Stored as DOUBLE; values vary each execution. - customer_health_score (DECIMAL(15,2)) = rounded to 2 decimals from: recency_component*0.3 + platform_consistency_score*0.3 + segment_component*0.4, where: - recency_component: 5/4/3/2/1 as in recency_score logic - segment_component: ''Champion'' 5.0; ''Loyal Customer'' 4.5; ''Potential Loyalist'' 3.5; ''New Customer'' 3.0; ''At Risk'' 2.0; ''Hibernating'' 1.5; else 1.0 - Advanced lifecycle metrics: - estimated_customer_ltv (DECIMAL(18,2)) = estimated_customer_value × (1 + 0.2 × frequency_score) × (1 + 0.1 × platform_consistency_score) × stage_factor; rounded to 2 decimals, where stage_factor: Growth 1.5; Maturity 2.0; Retention 1.8; Activation 1.2; else 1.0. - retention_probability (DECIMAL(3,2)) by customer_health_score: ≥4.5→0.95; ≥4.0→0.85; ≥3.5→0.75; ≥3.0→0.65; ≥2.5→0.50; ≥2.0→0.35; else 0.20. - churn_probability (DECIMAL(3,2)) inverse mapping: ≥4.5→0.05; ≥4.0→0.15; ≥3.5→0.25; ≥3.0→0.35; ≥2.5→0.50; ≥2.0→0.65; else 0.80. - revenue_at_risk (DECIMAL(9,2)) = estimated_customer_value × churn-probability mapping above; rounded to 2 decimals. - growth_potential (first match wins): - ''High Growth Potential'' if lifecycle_stage in (''Acquisition'',''Activation'') and customer_health_score ≥ 3.5 - ''Expansion Ready'' if lifecycle_stage = ''Growth'' and platform_consistency_score ≥ 2 - ''Upsell Candidate'' if lifecycle_stage = ''Maturity'' and customer_health_score ≥ 4.0 - ''Stable Account'' if lifecycle_stage = ''Retention'' and customer_health_score ≥ 3.0 - ''Reactivation Needed'' if lifecycle_stage = ''Dormant'' - Else ''Monitor'' - action_priority (INT, first match wins): - 5 if churn-probability mapping ≥ 0.65 - 4 if lifecycle_stage = ''Acquisition'' and customer_health_score ≥ 3.5 - 4 if lifecycle_stage = ''Growth'' and platform_consistency_score ≥ 2 - 3 if customer_health_score ≥ 4.0 and estimated_customer_value ≥ 3000 - 3 if churn-probability mapping ≥ 0.35 - Else 2 - acquisition_year = year of acquisition_cohort_month; acquisition_month = month number; months_since_acquisition = whole months between acquisition_cohort_month and today; NULL if acquisition_cohort_month is NULL. - acquisition_season: ''Holiday Season'' if month in (11,12,1); ''Summer Season'' if in (6,7,8); ''Spring Season'' if in (3,4,5); else ''Fall Season'' (default for NULL or not matched). - Final enrichments: - customer_tier by estimated_customer_ltv: Platinum (≥8000), Gold (≥5000), Silver (≥2500), Bronze (≥1000), else Basic. - is_strategic_account = TRUE if estimated_customer_ltv ≥ 10000 OR (customer_segment in (''Champion'',''Loyal Customer'') AND platform_consistency_score = 3); else FALSE. - intervention_urgency by action_priority: 5→''Immediate''; 4→''This Week''; 3→''This Month''; else ''Routine''. - expected_retention_rate by LTV and lifecycle: 0.90 if LTV ≥ 8000; 0.85 if LTV ≥ 5000; 0.75 if LTV ≥ 2500 and lifecycle_stage ≠ ''Dormant''; 0.60 if LTV ≥ 1000 and lifecycle_stage in (''Growth'',''Maturity''); else 0.45. - performance_vs_expectation: ''Above Expectation'' if retention_probability > expected_retention_rate; ''Meeting Expectation'' if retention_probability ≥ 80% of expected_retention_rate; else ''Below Expectation''. - Output ordering: sorted by is_strategic_account (true first), then action_priority descending, then estimated_customer_ltv descending, then customer_health_score descending.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_lifecycle_metrics.sql`，第 29–29 行：

```sql
       case when customer_segment in ('Champion','Loyal Customer') then 2+floor(random()*8)
```

单改/诊断：`records/019_stochastic_diagnostics.json#stochastic_evaluation`。共同屏蔽契约允许的随机输出，仅诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2641/2657 | 7/20 | 2634/2637 |
| L1 | 2641/2657 | 7/20 | 2634/2637 |
| L2 | 2641/2657 | 7/20 | 2634/2637 |
| L3 | 2641/2657 | 7/20 | 2634/2637 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，event `51.args.final_thought`：

> 生命周期模拟交易数、活动量和依赖它们的派生指标按契约使用 `random()`，因此跨次执行不保证完全可复现；执行时间字段及基于当前日期的指标同样随运行时间变化。

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
