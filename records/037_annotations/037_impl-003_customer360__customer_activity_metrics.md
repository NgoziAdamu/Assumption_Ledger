# impl-003_customer360__customer_activity_metrics（037 正式批次）

主要原因：**Intent Misreading**；把握：高。019旧主要原因原样保留：`C`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer_activity_metrics.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-003_customer360__customer_activity_metrics.json`；037补充：`records/037_checks/`。

## 逐点标注

### cross_platform_consistency

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约规定按在场平台数取平均，agent只相加未除；算法已写明，归Intent。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: cross_platform_consistency
>         data_type: DOUBLE
>         description: Average of raw engagement across active platforms (in_*=1) rounded to 2 decimals; NULL if no active platforms or any included operand is NULL

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer_activity_metrics.sql`，第 41–41 行：

```sql
round(case when in_marketo=1 then marketo_engagement else 0 end + case when in_stripe=1 then stripe_engagement else 0 end + case when in_zendesk=1 then zendesk_engagement else 0 end,2) as cross_platform_consistency
```

单改/诊断：`records/019_reruns_impl-003_customer360__customer_activity_metrics.json#cross_platform_consistency`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 6947/27613 | 6561/20666 | 386/6947 |
| L1 | 6583/26930 | 6561/20659 | 22/6271 |
| L2 | 6583/26930 | 6561/20659 | 22/6271 |
| L3 | 6583/26930 | 6561/20659 | 22/6271 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：

> - name: cross_platform_consistency
>         data_type: DOUBLE
>         description: Average of raw engagement across active platforms (in_*=1) rounded to 2 decimals; NULL if no active platforms or any included operand is NULL

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### primary_engagement_channel

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约要求比较原始engagement，agent比较时间衰减后score，属于规定的指标定义未落实。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: primary_engagement_channel
>         data_type: VARCHAR
>         description: Channel with highest raw engagement; ties break Marketing Driven > Sales Driven > Support Driven; fallback Balanced when comparisons cannot be resolved (e.g., NULL inputs)

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer_activity_metrics.sql`，第 30–31 行：

```sql
case when marketing_engagement_score>=sales_engagement_score and marketing_engagement_score>=support_engagement_score then 'Marketing Driven'
 when sales_engagement_score>=support_engagement_score then 'Sales Driven' when support_engagement_score is not null then 'Support Driven' else 'Balanced' end as primary_engagement_channel
```

单改/诊断：`records/019_reruns_impl-003_customer360__customer_activity_metrics.json#primary_engagement_channel`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 6947/27613 | 6947/18081 | 0/9532 |
| L1 | 6583/26930 | 6583/17398 | 0/9532 |
| L2 | 6583/26930 | 6583/17398 | 0/9532 |
| L3 | 6583/26930 | 6583/17398 | 0/9532 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：

> - name: primary_engagement_channel
>         data_type: VARCHAR
>         description: Channel with highest raw engagement; ties break Marketing Driven > Sales Driven > Support Driven; fallback Balanced when comparisons cannot be resolved (e.g., NULL inputs)

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### stochastic_evaluation

- 类别：其他；角色：参与；把握：中。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约允许random模拟活动量及派生量，单次gold随机输出不是唯一有效值；复用019屏蔽随机列诊断。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Overview - Start from behavior_analysis (intermediate.int_customer360__customer_behavior_analysis, one row per customer) and left join lifecycle_metrics (intermediate.int_customer360__customer_lifecycle_metrics) on primary_email. - Enrich with platform data via left joins on platform IDs: - Marketo: intermediate.int_customer360__marketo on lead_id - Stripe: intermediate.int_customer360__stripe on customer_id - Zendesk: intermediate.int_customer360__zendesk on user_id - Filter: exclude rows where primary_email is NULL; no de-duplication beyond joins. - Time anchors: current_date for recency calculations and current_timestamp for activity_analysis_timestamp; results vary by execution time. - Ordering: rows are sorted by activity_priority_score (desc), then weighted_engagement_score (desc), then active_channel_count (desc). Activity recency and counts - days/weeks/months_since_last_activity: difference between customer_last_activity and current_date by unit; returns NULL if customer_last_activity is NULL. - active_channel_count: integer sum (in_marketo + in_stripe + in_zendesk); if any flag is NULL the sum becomes NULL; expected domain is 0–3 from 0/1 flags. Estimated and adjusted activity (stochastic components) - estimated_monthly_activities: simulated with random() per run based on composite_engagement_score: - >=4.0 → 15 + floor(random()*10) ∈ [15,24] - >=3.0 → 8 + floor(random()*7) ∈ [8,14] - >=2.0 → 3 + floor(random()*5) ∈ [3,7] - >=1.0 → 1 + floor(random()*3) ∈ [1,3] - else → floor(random()*2) ∈ [0,1] - Note: random() yields different results each execution; this column is non-deterministic by design. - seasonally_adjusted_activity: estimated_monthly_activities multiplied by a month factor (Nov/Dec/Jan ×1.2; Jun/Jul/Aug ×0.8; else ×1.0); no rounding. - predicted_next_month_activity: estimated_monthly_activities multiplied by a factor from engagement_velocity category (Accelerating ×1.3; Steady High ×1.1; Steady Medium ×1.0; Declining ×0.7; Slow ×0.4; Stagnant ×0.2); no rounding. Engagement velocity, momentum, maturity (rule-based categories) - engagement_velocity (uses activity recency and composite_engagement_score): - <=7 days and score>=3.0 → Accelerating - <=14 days and score>=2.5 → Steady High - <=30 days and score>=2.0 → Steady Medium - <=60 days → Declining - <=90 days → Slow - else → Stagnant - activity_momentum (uses days_since_last_activity and composite_engagement_score): - <=7 days and score>=3.5 → High Momentum - <=14 days and score>=3.0 → Medium Momentum - <=30 days and score>=2.0 → Low Momentum - <=60 days → Losing Momentum - else → No Momentum - engagement_maturity (uses account_age_days and active_channel_count): - age>=365 and channels>=3 → Mature Multi-channel - age>=180 and channels>=2 → Developing Multi-channel - age>=90 and channels>=1 → Single Channel Engaged - age<90 → Early Stage - else → Minimal Engagement Channel scores and depths - marketing_engagement_score: if in_marketo=1 and is_unsubscribed=false and is_email_invalid=false then round(marketo_engagement × (1 − days since last Marketo update / 90), 2); else 0; may be negative; if the last update timestamp is NULL the result is NULL in the true branch. - sales_engagement_score: if in_stripe=1 and is_deleted=false and is_delinquent=false then round(stripe_engagement × (1 − days since last Stripe update / 60), 2); else 0; may be negative; NULL if the last update timestamp is NULL in the true branch. - support_engagement_score: if in_zendesk=1 and is_active=true and is_suspended=false and is_deleted=false then round(zendesk_engagement × (1 − days since last Zendesk update / 120), 2); else 0; may be negative; NULL if the last update timestamp is NULL in the true branch. - primary_engagement_channel: choose the channel with the highest raw engagement; ties break in order Marketing Driven > Sales Driven > Support Driven; if comparisons do not resolve (e.g., NULL inputs) fallback is Balanced. - marketing_depth/sales_depth/support_depth (per channel): if in_* = 1: engagement>=4 → Deep; engagement>=2 → Medium; else → Shallow; if in_*=0 → None. Cross-platform and composite scores - cross_platform_consistency: round( average of raw engagement across platforms where in_*=1, 2 decimals ); returns NULL if no active platforms or if any included operand (flags or raw engagements) is NULL. - activity_efficiency: round(composite_engagement_score divided by active_channel_count, 2); NULL if active_channel_count is 0 or NULL. - weighted_engagement_score: round(0.3×marketing_engagement_score (NULL→0) + 0.5×sales_engagement_score (NULL→0) + 0.2×support_engagement_score (NULL→0), 2); can be negative. - activity_grade: from weighted_engagement_score and active_channel_count: >=4.0 & channels>=3 → A+; >=3.5 & channels>=2 → A; >=3.0 → B+; >=2.5 → B; >=2.0 → C+; >=1.5 → C; >=1.0 → D; else → F. - activity_priority_score: round(0.4×weighted_engagement_score + 0.3×active_channel_count + 0.3×priority_component, 2) where priority_component is 5/4/3/2/1 by recency+composite rules (<=7 days & score>=3.5 → 5; <=14 & score>=3.0 → 4; <=30 & score>=2.0 → 3; <=60 → 2; else → 1). Risk and interventions - activity_risk_level: if days_since_last_activity>90 and customer_health_score<3.0 → High Activity Risk; else if days_since_last_activity>60 or active_channel_count=1 → Medium Activity Risk; else if days_since_last_activity>30 → Low Activity Risk; else → No Activity Risk. - recommended_activity_intervention (evaluated top-to-bottom): Declining/Slow/Stagnant with health>=3.0 → Re-engagement Campaign; else single channel (count=1) with composite>=2.5 → Channel Expansion; else Marketing Driven with in_stripe=0 → Sales Conversion Focus; else Sales Driven with in_zendesk=0 → Success Onboarding; else recent (<=7 days) with composite>=3.5 → Upsell Opportunity; else Standard Engagement.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer_activity_metrics.sql`，第 37–37 行：

```sql
 case when composite_engagement_score>=4 then 15+floor(random()*10) when composite_engagement_score>=3 then 8+floor(random()*7) when composite_engagement_score>=2 then 3+floor(random()*5) when composite_engagement_score>=1 then 1+floor(random()*3) else floor(random()*2) end as estimated_monthly_activities
```

单改/诊断：`records/019_stochastic_diagnostics.json#stochastic_evaluation`。共同屏蔽契约允许的随机输出，仅诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 6947/27613 | 6947/16486 | 0/11127 |
| L1 | 6583/26930 | 6271/15803 | 312/11127 |
| L2 | 6583/26930 | 6271/15803 | 312/11127 |
| L3 | 6583/26930 | 6271/15803 | 312/11127 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，event `51.args.final_thought`：

> 生命周期模拟交易数、活动量和依赖它们的派生指标按契约使用 `random()`，因此跨次执行不保证完全可复现；执行时间字段及基于当前日期的指标同样随运行时间变化。

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
