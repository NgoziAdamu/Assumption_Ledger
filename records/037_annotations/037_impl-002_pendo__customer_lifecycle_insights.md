# impl-002_pendo__customer_lifecycle_insights（037 正式批次）

主要原因：**多因并列**；把握：高。019旧主要原因原样保留：`D`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，finish 59 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-002_pendo__customer_lifecycle_insights.json`；037补充：`records/037_checks/`。

## 逐点标注

### customer_journey_stage

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项给出派生规则，交付SQL用固定默认标签替代。报告点名lifecycle insights使用defaulted derivations。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: customer_journey_stage
>         data_type: VARCHAR
>         description: Journey stage derived from days since first event and lifecycle/RFM value and risk conditions via ordered rules

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，第 1–1 行：

```sql
'Maintenance' customer_journey_stage
```

单改/诊断：`records/019_reruns_impl-002_pendo__customer_lifecycle_insights.json#customer_journey_stage`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L1 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L2 | 895934/5703915 | 895934/4807981 | 0/895934 |
| L3 | 895934/5703915 | 895934/4807981 | 0/895934 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### predicted_ltv_tier

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项给出派生规则，交付SQL用固定默认标签替代。报告点名lifecycle insights使用defaulted derivations。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: predicted_ltv_tier
>         data_type: VARCHAR
>         description: Predicted LTV tier derived from lifecycle, RFM value/score, churn risk, and health thresholds via ordered rules

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，第 1–1 行：

```sql
'Standard LTV' predicted_ltv_tier
```

单改/诊断：`records/019_reruns_impl-002_pendo__customer_lifecycle_insights.json#predicted_ltv_tier`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L1 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L2 | 895934/5703915 | 895934/4807981 | 0/895934 |
| L3 | 895934/5703915 | 895934/4807981 | 0/895934 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### engagement_velocity

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项给出派生规则，交付SQL用固定默认标签替代。报告点名lifecycle insights使用defaulted derivations。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: engagement_velocity
>         data_type: FLOAT
>         description: Ratio of count_active_days to days since first event; set to 0 when either value is non-positive

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，第 1–1 行：

```sql
0::FLOAT engagement_velocity
```

单改/诊断：`records/019_reruns_impl-002_pendo__customer_lifecycle_insights.json#engagement_velocity`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L1 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L2 | 895934/5703915 | 895934/5460467 | 0/243448 |
| L3 | 895934/5703915 | 895934/5460467 | 0/243448 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### usage_trend

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项给出派生规则，交付SQL用固定默认标签替代。报告点名lifecycle insights使用defaulted derivations。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: usage_trend
>         data_type: VARCHAR
>         description: Usage trend label based on average_daily_events relative to a baseline of sum_events per active day; baseline missing yields Declining

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，第 1–1 行：

```sql
'Declining' usage_trend
```

单改/诊断：`records/019_reruns_impl-002_pendo__customer_lifecycle_insights.json#usage_trend`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L1 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L2 | 895934/5703915 | 895934/4807981 | 0/895934 |
| L3 | 895934/5703915 | 895934/4807981 | 0/895934 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### customer_importance_level

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项给出派生规则，交付SQL用固定默认标签替代。报告点名lifecycle insights使用defaulted derivations。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: customer_importance_level
>         data_type: VARCHAR
>         description: Importance category from ordered rules over segment, predicted LTV, composite value, needs_attention, and journey stage

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，第 1–1 行：

```sql
'Standard' customer_importance_level
```

单改/诊断：`records/019_reruns_impl-002_pendo__customer_lifecycle_insights.json#customer_importance_level`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L1 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L2 | 895934/5703915 | 895934/4807981 | 0/895934 |
| L3 | 895934/5703915 | 895934/4807981 | 0/895934 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### investment_expectation

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约逐项给出派生规则，交付SQL用固定默认标签替代。报告点名lifecycle insights使用defaulted derivations。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: investment_expectation
>         data_type: VARCHAR
>         description: Expected ROI label mapped from customer_segment_label with a default of Standard ROI - Maintenance

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，第 1–1 行：

```sql
'Standard ROI - Maintenance' investment_expectation
```

单改/诊断：`records/019_reruns_impl-002_pendo__customer_lifecycle_insights.json#investment_expectation`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 895934/6356401 | 895934/6356401 | 0/0 |
| L1 | 895934/6356401 | 895934/6356401 | 0/0 |
| L2 | 895934/5703915 | 895934/5703915 | 0/0 |
| L3 | 895934/5703915 | 895934/5703915 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### customer_segment_branches

- 类别：Intent Misreading；角色：并列；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

已实现有条件的分类，但漏掉契约明写的四个分支；不是数据性质假设。报告只泛称lifecycle简化，没有点出这几个被漏分支。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build a comprehensive customer record per visitor_id by joining base visitor activity with lifecycle, RFM, and product health, then derive journey labels, values, and recommendations: 1) Base rowset and joins - Start from marts.pendo__visitor (vb), one row per visitor_id; carry: visitor_id, account_id, first_event_on, last_event_on, count_active_days, count_active_months, sum_events, sum_minutes, average_daily_events, average_daily_minutes, count_associated_accounts. - Left join intermediate.int_pendo__user_lifecycle_segments (lc) on visitor_id. - Left join intermediate.int_pendo__customer_rfm_analysis (rfm) on visitor_id. - Left join intermediate.int_pendo__product_health_metrics (ph) on account_id. - Null policy: Left joins may yield missing lifecycle/RFM/health attributes; unless explicitly defaulted in rules below, missing values do not match conditions and fall to the default outcome. 2) Customer segmentation label (customer_segment_label) evaluated in order: - Power User + Champions → "Star Customer" - (Mature User or Power User) + High Value → "Key Account" - New User + New Customers → "Fresh Prospect" - Growing User + Potential Loyalists → "Rising Star" - churn_risk_level in (High Risk, Medium Risk) + At Risk → "Save Immediately" - lifecycle_stage = At Risk + action_priority = Re-engagement → "Rescue Mission" - lifecycle_stage = Churned → "Lost Customer" - Else → "Standard Customer" 3) Comprehensive customer value (comprehensive_customer_value, 0–100): - Compute a weighted sum: 40% of user_value_score (defaults to 0 if missing), 30% of (rfm_composite_score scaled to 0–100 by multiplying by 20; defaults to 0 if missing), and 30% of overall_health_score (defaults to 50 if missing). Cap the result at 100. No rounding beyond native numeric evaluation. 4) Recommended next action (recommended_next_action) evaluated in order: - Power User + Champions → "Leverage as advocate; Offer exclusive features; Request testimonials" - is_new_user = true + New Customers → "Intensive onboarding; Feature education; Success manager assignment" - needs_attention = true + action_priority = Re-engagement → "Personalized outreach; Usage analysis; Feature recommendations" - churn_risk_level = High Risk → "Immediate intervention; Executive outreach; Value demonstration" - lifecycle_stage = Growing User → "Feature adoption campaign; Usage optimization; Upgrade path guidance" - rfm_segment = Loyal Customers → "Upsell opportunities; Loyalty rewards; Advanced feature training" - Else → "Standard nurturing; Regular check-ins; Content engagement" 5) Customer journey stage (customer_journey_stage): - Define days since first event as the number of days from the first_event_on date to today. - If days since first event ≤ 30 → "Onboarding" - Else if lifecycle_stage in (Growing User, Mature User) and customer_value_tier in (High Value, Medium Value) → "Growth" - Else if lifecycle_stage in (Power User, Mature User) and rfm_segment in (Champions, Loyal Customers) → "Maturity" - Else if churn_risk_level in (High Risk, Medium Risk) or lifecycle_stage = At Risk → "Retention" - Else if lifecycle_stage = Churned → "Win-back" - Else → "Maintenance" 6) Predicted LTV tier (predicted_ltv_tier) evaluated in order: - lifecycle_stage in (Power User, Mature User) + customer_value_tier = High Value + overall_health_score ≥ 70 (treat missing health as 60 for this rule) → "Very High LTV" - (user_value_score ≥ 70 or rfm_composite_score ≥ 4) + churn_risk_level = Low Risk → "High LTV" - lifecycle_stage in (Growing User, New User) + predicted_clv_tier in (High CLV, Medium CLV) → "Moderate LTV" - churn_risk_level = High Risk or lifecycle_stage = Churned → "Low LTV" - Else → "Standard LTV" 7) Engagement velocity and trends (from comprehensive view): - engagement_velocity: ratio of count_active_days to days since first event; if either value is not positive, set to 0. - usage_trend: define a baseline average as sum_events divided by count_active_days when count_active_days > 0; if average_daily_events exceeds the baseline by more than 20% → "Accelerating"; if within ±20% → "Stable"; otherwise → "Declining". When count_active_days = 0, the baseline is undefined and the outcome is "Declining". - account_influence_level: count_associated_accounts > 3 → "Multi-Account Influencer"; > 1 → "Cross-Account User"; else → "Single Account User". - calculated_at: timestamp when the metrics are computed. 8) Final importance and investment expectation: - customer_importance_level (in order): - customer_segment_label in (Star Customer, Key Account) + predicted_ltv_tier = Very High LTV → "Critical" - comprehensive_customer_value ≥ 80 + customer_journey_stage in (Growth, Maturity) → "High" - comprehensive_customer_value ≥ 60 or customer_segment_label in (Rising Star, Fresh Prospect) → "Medium" - needs_attention = true or customer_journey_stage = Retention → "At Risk" - Else → "Standard" - investment_expectation: - Star Customer → "High ROI - Advocacy & Expansion" - Key Account → "High ROI - Retention & Upsell" - Rising Star → "Medium ROI - Growth Investment" - Fresh Prospect → "Medium ROI - Onboarding Investment" - Save Immediately → "Low ROI - Retention Cost" - Lost Customer → "Negative ROI - Win-back Cost" - Else → "Standard ROI - Maintenance" 9) Output all selected and derived columns; no additional filtering; grain remains one row per visitor_id.'

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，第 1–1 行：

```sql
WHEN l.lifecycle_stage='New User' AND r.rfm_segment='New Customers' THEN 'Fresh Prospect' ELSE 'Standard Customer' END customer_segment_label
```

单改/诊断：`records/037_checks/rerun_impl-002_pendo__customer_lifecycle_insights.json#customer_segment_branches`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L1 | 895934/6356401 | 895934/5460467 | 0/895934 |
| L2 | 895934/5703915 | 895934/4807981 | 0/895934 |
| L3 | 895934/5703915 | 895934/4807981 | 0/895934 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### recommended_next_action

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

将单个固定输出改为契约逐字规则。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: recommended_next_action
>         data_type: VARCHAR
>         description: Deterministic next-action recommendation from ordered rules over lifecycle and RFM signals

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，第 1–1 行：

```sql
'Standard nurturing; Regular check-ins; Content engagement' recommended_next_action
```

单改/诊断：`records/037_checks/rerun_impl-002_pendo__customer_lifecycle_insights.json#recommended_next_action`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 895934/6356401 | 895934/6271538 | 0/84863 |
| L1 | 895934/6356401 | 895934/6271538 | 0/84863 |
| L2 | 895934/5703915 | 895934/5619052 | 0/84863 |
| L3 | 895934/5703915 | 895934/5619052 | 0/84863 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### account_influence_level

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

核验未覆盖的常量输出；即使净改善0也保留非原因标记。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: account_influence_level
>         data_type: VARCHAR
>         description: 'Influence classification by count_associated_accounts: >3 Multi-Account Influencer; >1 Cross-Account User; else Single Account User'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，第 1–1 行：

```sql
'Single Account User' account_influence_level
```

单改/诊断：`records/037_checks/rerun_impl-002_pendo__customer_lifecycle_insights.json#account_influence_level`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 895934/6356401 | 895934/6356401 | 0/0 |
| L1 | 895934/6356401 | 895934/6356401 | 0/0 |
| L2 | 895934/5703915 | 895934/5703915 | 0/0 |
| L3 | 895934/5703915 | 895934/5703915 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
