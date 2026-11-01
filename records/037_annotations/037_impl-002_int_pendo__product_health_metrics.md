# impl-002_int_pendo__product_health_metrics（037 正式批次）

主要原因：**已说出的降级**；把握：中。019旧主要原因原样保留：`D`，不作为新类别依据。

## 范围与材料

- 层：intermediate；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，finish 59 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-002_int_pendo__product_health_metrics.json`；037补充：`records/037_checks/`。

## 逐点标注

### retention_join

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约规定feature先FULL OUTER JOIN账户retention，再接engagement；agent省略中间账户来源，只f/e连接。连接算法已写明，归Intent。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '- NPS metrics (by account_id from intermediate.int_pendo__latest_nps_rating): - total_nps_responses is the total row count per account; avg_nps_score is the mean of nps_rating (ignoring NULLs). - promoter_rate is the share of rows with nps_rating ≥ 9 using total_nps_responses as the denominator (NULL ratings not counted in the numerator but included in the denominator). - detractor_rate is the share of rows with nps_rating ≤ 6 using total_nps_responses as the denominator (NULL ratings not counted in the numerator but included in the denominator). - net_promoter_score = promoter_rate − detractor_rate. - Feature adoption metrics (by app_id, account_id from staging.stg_pendo__feature_event): - total_features_available is distinct features; features_used is distinct features with any usage (>0 events); features_heavily_used is distinct features with ≥10 events. - total_users is distinct visitors; active_feature_users is distinct visitors with any feature usage (>0 events). - feature_adoption_rate = features_used ÷ total_features_available (returns NULL when total_features_available = 0). - feature_depth_adoption_rate = features_heavily_used ÷ total_features_available (returns NULL when total_features_available = 0). - user_feature_adoption_rate = active_feature_users ÷ total_users (returns NULL when total_users = 0). - avg_features_per_user = features_used ÷ active_feature_users (returns NULL when active_feature_users = 0). - Distinct counts exclude NULL IDs; duplicates are removed. - Visitor aggregated metrics (by account_id, visitor_id from staging.stg_pendo__event): - count_active_days is the distinct count of active calendar days; sum_events and sum_minutes are totals across events; last_event_on is the most recent active calendar day. - User retention metrics (by account_id from visitor_aggregated_metrics): - total_users is distinct visitors. - retention_7d/30d/90d are the shares of visitors whose last_event_on is within 7/30/90 days of current_date; denominators are total_users (no explicit zero-division guard). - highly_active_user_rate is the share of visitors with count_active_days ≥ 20 (denominator is total_users; no explicit zero-division guard). - avg_lifetime_events is the mean of sum_events per visitor; avg_active_days_per_user is the mean of count_active_days per visitor. - Engagement quality metrics (by account_id, app_id from staging.stg_pendo__event): - avg_session_duration is the mean minutes per session; avg_events_per_session is the mean events per session (NULLs ignored in averages). - unique_users is distinct visitors; total_sessions is the session row count; sessions_per_user = total_sessions ÷ unique_users (no explicit zero-division guard). - deep_engagement_session_rate is the share of sessions with ≥10 minutes or ≥20 events (denominator is total_sessions). - power_user_rate assumes 20% are high-frequency users: equals 0.2 when unique_users > 0, else NULL. - Product health scores: - Join feature_adoption_metrics (fam) and user_retention_metrics (urm) with a full outer join on account_id. - Join engagement_quality_metrics (eqm) with a full outer join on the coalesced account_id from fam/urm and require app_id to match fam.app_id; rows with only engagement data are kept but will have app_id NULL in the output. - Join nps_metrics (nm) with a left join on the coalesced account_id from fam/urm; NPS does not attach for engagement-only rows. - account_id is coalesced from fam, then urm, then eqm; app_id comes only from fam. - overall_health_score is a 0–100 score capped at 100, computed as the sum of: - up to 25 points from NPS by scaling net_promoter_score from [-1,1] to [0,25] (missing treated as 0), - up to 25 points from feature_adoption_rate (missing treated as 0), - up to 25 points from retention_30d (missing treated as 0), - up to 25 points from engagement: deep_engagement_session_rate (up to 12.5) and power_user_rate (up to 12.5) (missing treated as 0). - Health categorization: - health_grade: Excellent (score ≥ 80), Good (≥ 60), Fair (≥ 40), Poor (≥ 20), else Critical. - primary_improvement_area (first match wins): if net_promoter_score is missing treat as −1; if feature_adoption_rate, retention_30d, or deep_engagement_session_rate are missing treat as 0; then check in order: NPS < 0, adoption < 0.3, 30‑day retention < 0.5, deep engagement < 0.2; otherwise maintain/optimize. - risk_level: High Risk if score < 30; Medium Risk if (score < 50 and 30‑day retention < 0.4, treating missing retention as 0) or net_promoter_score < −0.2 (treating missing NPS as 0); else Low. - calculated_at is set to the current timestamp at execution.'

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
FROM f FULL OUTER JOIN e ON f.account_id=e.account_id AND f.app_id=e.app_id
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#retention_join`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/316634 | 0/20 |
| L1 | 47678/316654 | 47678/316634 | 0/20 |
| L2 | 47678/316642 | 47678/316622 | 0/20 |
| L3 | 47678/316642 | 47678/316622 | 0/20 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### avg_active_days_per_user

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_active_days_per_user
>         data_type: DOUBLE
>         description: Mean distinct active days per visitor by account; NULLs are ignored in the average

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
NULL::DOUBLE avg_active_days_per_user
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#avg_active_days_per_user`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/296947 | 0/19707 |
| L1 | 47678/316654 | 47678/296947 | 0/19707 |
| L2 | 47678/316642 | 47678/296935 | 0/19707 |
| L3 | 47678/316642 | 47678/296935 | 0/19707 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_lifetime_events

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_lifetime_events
>         data_type: DOUBLE
>         description: Mean total events per visitor by account; NULLs are ignored in the average

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
NULL::DOUBLE avg_lifetime_events
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#avg_lifetime_events`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/296947 | 0/19707 |
| L1 | 47678/316654 | 47678/296947 | 0/19707 |
| L2 | 47678/316642 | 47678/296935 | 0/19707 |
| L3 | 47678/316642 | 47678/296935 | 0/19707 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### highly_active_user_rate

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: highly_active_user_rate
>         data_type: FLOAT
>         description: Share of visitors with count_active_days ≥ 20; denominator is distinct visitors; no zero-division guard

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
NULL::FLOAT highly_active_user_rate
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#highly_active_user_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/296947 | 0/19707 |
| L1 | 47678/316654 | 47678/296947 | 0/19707 |
| L2 | 47678/316642 | 47678/296935 | 0/19707 |
| L3 | 47678/316642 | 47678/296935 | 0/19707 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### feature_depth_adoption_rate

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: feature_depth_adoption_rate
>         data_type: FLOAT
>         description: Proportion of distinct features with ≥10 events over all distinct features; returns NULL when no features

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
NULL::FLOAT feature_depth_adoption_rate
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#feature_depth_adoption_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/296551 | 0/20103 |
| L1 | 47678/316654 | 47678/296551 | 0/20103 |
| L2 | 47678/316642 | 47678/296539 | 0/20103 |
| L3 | 47678/316642 | 47678/296539 | 0/20103 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_features_per_user

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_features_per_user
>         data_type: FLOAT
>         description: Features_used divided by active_feature_users; returns NULL when there are no active feature users

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
NULL::FLOAT avg_features_per_user
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#avg_features_per_user`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/296551 | 0/20103 |
| L1 | 47678/316654 | 47678/296551 | 0/20103 |
| L2 | 47678/316642 | 47678/296539 | 0/20103 |
| L3 | 47678/316642 | 47678/296539 | 0/20103 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### deep_engagement_session_rate

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: deep_engagement_session_rate
>         data_type: FLOAT
>         description: Share of sessions with ≥10 minutes or ≥20 events; denominator is total sessions

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
NULL::FLOAT deep_engagement_session_rate
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#deep_engagement_session_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/294538 | 0/22116 |
| L1 | 47678/316654 | 47678/294538 | 0/22116 |
| L2 | 47678/316642 | 47678/294526 | 0/22116 |
| L3 | 47678/316642 | 47678/294526 | 0/22116 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### health_grade

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: health_grade
>         data_type: VARCHAR
>         description: 'Grade by score: Excellent (≥80), Good (≥60), Fair (≥40), Poor (≥20), else Critical'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
'Critical' health_grade
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#health_grade`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/316654 | 0/0 |
| L1 | 47678/316654 | 47678/316654 | 0/0 |
| L2 | 47678/316642 | 47678/316642 | 0/0 |
| L3 | 47678/316642 | 47678/316642 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### risk_level

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: risk_level
>         data_type: VARCHAR
>         description: High if score<30; Medium if (score<50 and 30‑day retention<0.4 treating missing as 0) or NPS<−0.2 treating missing as 0; else Low

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
'High Risk' risk_level
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#risk_level`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/316654 | 0/0 |
| L1 | 47678/316654 | 47678/316654 | 0/0 |
| L2 | 47678/316642 | 47678/316642 | 0/0 |
| L3 | 47678/316642 | 47678/316642 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### health_score_complete

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复完整评分公式，仍保留其他列原先NULL/默认输入；只改score表达式。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '- NPS metrics (by account_id from intermediate.int_pendo__latest_nps_rating): - total_nps_responses is the total row count per account; avg_nps_score is the mean of nps_rating (ignoring NULLs). - promoter_rate is the share of rows with nps_rating ≥ 9 using total_nps_responses as the denominator (NULL ratings not counted in the numerator but included in the denominator). - detractor_rate is the share of rows with nps_rating ≤ 6 using total_nps_responses as the denominator (NULL ratings not counted in the numerator but included in the denominator). - net_promoter_score = promoter_rate − detractor_rate. - Feature adoption metrics (by app_id, account_id from staging.stg_pendo__feature_event): - total_features_available is distinct features; features_used is distinct features with any usage (>0 events); features_heavily_used is distinct features with ≥10 events. - total_users is distinct visitors; active_feature_users is distinct visitors with any feature usage (>0 events). - feature_adoption_rate = features_used ÷ total_features_available (returns NULL when total_features_available = 0). - feature_depth_adoption_rate = features_heavily_used ÷ total_features_available (returns NULL when total_features_available = 0). - user_feature_adoption_rate = active_feature_users ÷ total_users (returns NULL when total_users = 0). - avg_features_per_user = features_used ÷ active_feature_users (returns NULL when active_feature_users = 0). - Distinct counts exclude NULL IDs; duplicates are removed. - Visitor aggregated metrics (by account_id, visitor_id from staging.stg_pendo__event): - count_active_days is the distinct count of active calendar days; sum_events and sum_minutes are totals across events; last_event_on is the most recent active calendar day. - User retention metrics (by account_id from visitor_aggregated_metrics): - total_users is distinct visitors. - retention_7d/30d/90d are the shares of visitors whose last_event_on is within 7/30/90 days of current_date; denominators are total_users (no explicit zero-division guard). - highly_active_user_rate is the share of visitors with count_active_days ≥ 20 (denominator is total_users; no explicit zero-division guard). - avg_lifetime_events is the mean of sum_events per visitor; avg_active_days_per_user is the mean of count_active_days per visitor. - Engagement quality metrics (by account_id, app_id from staging.stg_pendo__event): - avg_session_duration is the mean minutes per session; avg_events_per_session is the mean events per session (NULLs ignored in averages). - unique_users is distinct visitors; total_sessions is the session row count; sessions_per_user = total_sessions ÷ unique_users (no explicit zero-division guard). - deep_engagement_session_rate is the share of sessions with ≥10 minutes or ≥20 events (denominator is total_sessions). - power_user_rate assumes 20% are high-frequency users: equals 0.2 when unique_users > 0, else NULL. - Product health scores: - Join feature_adoption_metrics (fam) and user_retention_metrics (urm) with a full outer join on account_id. - Join engagement_quality_metrics (eqm) with a full outer join on the coalesced account_id from fam/urm and require app_id to match fam.app_id; rows with only engagement data are kept but will have app_id NULL in the output. - Join nps_metrics (nm) with a left join on the coalesced account_id from fam/urm; NPS does not attach for engagement-only rows. - account_id is coalesced from fam, then urm, then eqm; app_id comes only from fam. - overall_health_score is a 0–100 score capped at 100, computed as the sum of: - up to 25 points from NPS by scaling net_promoter_score from [-1,1] to [0,25] (missing treated as 0), - up to 25 points from feature_adoption_rate (missing treated as 0), - up to 25 points from retention_30d (missing treated as 0), - up to 25 points from engagement: deep_engagement_session_rate (up to 12.5) and power_user_rate (up to 12.5) (missing treated as 0). - Health categorization: - health_grade: Excellent (score ≥ 80), Good (≥ 60), Fair (≥ 40), Poor (≥ 20), else Critical. - primary_improvement_area (first match wins): if net_promoter_score is missing treat as −1; if feature_adoption_rate, retention_30d, or deep_engagement_session_rate are missing treat as 0; then check in order: NPS < 0, adoption < 0.3, 30‑day retention < 0.5, deep engagement < 0.2; otherwise maintain/optimize. - risk_level: High Risk if score < 30; Medium Risk if (score < 50 and 30‑day retention < 0.4, treating missing retention as 0) or net_promoter_score < −0.2 (treating missing NPS as 0); else Low. - calculated_at is set to the current timestamp at execution.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
0::FLOAT overall_health_score
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#health_score_complete`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/283033 | 0/33621 |
| L1 | 47678/316654 | 47678/283033 | 0/33621 |
| L2 | 47678/316642 | 47678/283021 | 0/33621 |
| L3 | 47678/316642 | 47678/283021 | 0/33621 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### retention_7d

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: retention_7d
>         data_type: FLOAT
>         description: Share of visitors whose last active day is within 7 days of current_date; denominator is distinct visitors and no zero-division guard is applied

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
NULL::FLOAT retention_7d
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#retention_7d`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/296947 | 0/19707 |
| L1 | 47678/316654 | 47678/296947 | 0/19707 |
| L2 | 47678/316642 | 47678/296935 | 0/19707 |
| L3 | 47678/316642 | 47678/296935 | 0/19707 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### retention_30d

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: retention_30d
>         data_type: FLOAT
>         description: Share of visitors whose last active day is within 30 days of current_date; denominator is distinct visitors and no zero-division guard is applied

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
NULL::FLOAT retention_30d
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#retention_30d`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/296947 | 0/19707 |
| L1 | 47678/316654 | 47678/296947 | 0/19707 |
| L2 | 47678/316642 | 47678/296935 | 0/19707 |
| L3 | 47678/316642 | 47678/296935 | 0/19707 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### retention_90d

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: retention_90d
>         data_type: FLOAT
>         description: Share of visitors whose last active day is within 90 days of current_date; denominator is distinct visitors and no zero-division guard is applied

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
NULL::FLOAT retention_90d
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#retention_90d`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/296947 | 0/19707 |
| L1 | 47678/316654 | 47678/296947 | 0/19707 |
| L2 | 47678/316642 | 47678/296935 | 0/19707 |
| L3 | 47678/316642 | 47678/296935 | 0/19707 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### primary_improvement_area

- 类别：已说出的降级；角色：主要；把握：中。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

只恢复契约首优先NPS缺失视为-1分支；条件源于契约，文字代表由只读gold诊断获得。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: primary_improvement_area
>         data_type: VARCHAR
>         description: 'Priority guidance (first match wins): treat missing NPS as −1 and other metrics as 0, then check NPS<0, feature adoption<0.3, 30‑day retention<0.5, deep engagement<0.2; otherwise maintain/optimize'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：

```sql
'Improve feature adoption' primary_improvement_area
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#primary_improvement_area`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 47678/316654 | 47678/268977 | 0/47677 |
| L1 | 47678/316654 | 47678/268977 | 0/47677 |
| L2 | 47678/316642 | 47678/268965 | 0/47677 |
| L3 | 47678/316642 | 47678/268965 | 0/47677 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

不确定：部分恢复公式的干预在其他默认输入仍错误时不能对齐gold，甚至增加差异；保留非原因而不外推整套模型已修复。恢复条件的文字代表若契约未固定，只用于测量，不能反过来当契约。
