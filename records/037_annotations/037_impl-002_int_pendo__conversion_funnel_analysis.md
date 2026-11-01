# impl-002_int_pendo__conversion_funnel_analysis（037 正式批次）

主要原因：**已说出的降级**；把握：中。019旧主要原因原样保留：`D`，不作为新类别依据。

## 范围与材料

- 层：intermediate；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，finish 59 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-002_int_pendo__conversion_funnel_analysis.json`；037补充：`records/037_checks/`。

## 逐点标注

### daily_event_sources

- 类别：已说出的降级；角色：主要；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

修复同一个daily来源模块：按契约三源UNION ALL与类型存在标志，替代event.num_events/num_minutes代理；不改后续占位或cohort。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: 'Build daily account-level conversion funnel metrics and 30-day cohort summaries: - daily_events (union all) - Page views: from staging.stg_pendo__event as event_type=page_view; fields include visitor_id, account_id, app_id, event_date (day-level from occurred_at), entity_id=page_id, num_events, num_minutes. - Feature interactions: from staging.stg_pendo__feature_event as event_type=feature_click; entity_id=feature_id; carry num_events and num_minutes. - Deep page interactions: from staging.stg_pendo__page_event as event_type=page_interaction; per visitor/account/app/day/page aggregate counts of interactions (num_events) and summed minutes (num_minutes). - user_daily_funnel (per visitor_id, account_id, app_id, event_date) - Presence flags by type: has_page_view, has_feature_interaction, has_deep_interaction set to 1 if any such event exists that day, else 0. - Distinct entities: unique_pages_viewed, unique_features_used, unique_pages_interacted are distinct counts of entity_id by type. - Totals: total_page_events/total_feature_events/total_interaction_events and corresponding minutes are summed by type. - funnel_progression (per visitor/day) - Funnel stage precedence: Deep Engaged (all three flags=1) > Feature User (page and feature flags=1) > Page Visitor (page flag=1) > No Activity. - engagement_score = 0.1×total_page_events + 0.3×total_feature_events + 0.6×total_interaction_events + 0.05×(total_page_minutes + total_feature_minutes + total_interaction_minutes). - session_quality: High Quality if total_minutes≥10 and unique_pages_viewed≥3 and unique_features_used≥2; else Medium Quality if total_minutes≥5 and unique_pages_viewed≥2; else Low Quality if total_page_minutes≥1; else Bounce. Here total_minutes = total_page_minutes + total_feature_minutes + total_interaction_minutes. - account_funnel_metrics (per account_id, app_id, event_date) - Visitor counts: total_visitors = distinct visitor_id; visitors_with_page_views/features/deep = distinct visitors with the corresponding presence flag=1. - Conversion rates: page_to_feature = visitors_with_feature_use / visitors_with_page_views; feature_to_deep = visitors_with_deep_engagement / visitors_with_feature_use; overall = visitors_with_deep_engagement / visitors_with_page_views. If the denominator is 0, the rate is NULL. - Averages: avg_engagement_score and avg_pages_per_visitor are averaged over visitors with has_page_view=1; avg_features_per_user over visitors with has_feature_interaction=1; if no qualifying visitors, result is NULL. - Quality rates: high_quality_session_rate = distinct visitors with session_quality=''High Quality'' divided by total_visitors; bounce_rate = distinct visitors with session_quality=''Bounce'' divided by total_visitors; NULL if total_visitors=0. - conversion_cohort_analysis (per account_id, app_id; joined back to each daily row) - 30-day rolling averages relative to today (lower bound inclusive): average of daily page_to_feature, feature_to_deep, and overall conversion rates for dates on or after 30 days before today. - conversion_rate_trend = average overall conversion rate for dates on or after 7 days before today minus the average for dates from 30 to 7 days before today; both windows include the day 7 days ago. - funnel_health_rating by the 30-day average overall rate: Excellent (≥0.3), Good (≥0.2), Fair (≥0.1), else Poor. If the 30-day average is NULL, rating is Poor. - optimization_recommendation (first matching rule): if the 30-day average page→feature rate < 0.2 then “Focus on feature discovery and onboarding”; else if the 30-day average feature→deep rate < 0.3 then “Improve feature engagement and user guidance”; else if the 30-day average bounce rate > 0.6 then “Reduce bounce rate through better landing experience”; else “Maintain current optimization efforts”. - Final step: left join the cohort metrics to the daily account_funnel_metrics by account_id and app_id; set calculated_at to the query execution timestamp. Distinct counting ensures a visitor is counted once per day; averages ignore NULLs; no rounding is applied.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
SELECT account_id,app_id,CAST(occurred_at AS DATE) event_date,count(DISTINCT visitor_id) total_visitors,count(DISTINCT CASE WHEN page_id IS NOT NULL THEN visitor_id END) visitors_with_page_views,count(DISTINCT CASE WHEN num_events>0 THEN visitor_id END) visitors_with_feature_use,count(DISTINCT CASE WHEN num_minutes>=1 THEN visitor_id END) visitors_with_deep_engagement FROM staging.stg_pendo__event GROUP BY 1,2,3
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#daily_event_sources`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/782088 | 0/1039706 |
| L1 | 104898/1821792 | 104898/782039 | 0/1039753 |
| L2 | 104898/1821806 | 104898/782026 | 0/1039780 |
| L3 | 104898/1821806 | 104898/782026 | 0/1039780 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_engagement_score

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

仅恢复单个按visitor聚合的指标，daily主行集仍使用原agent来源。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_engagement_score
>         data_type: DOUBLE
>         description: Average engagement_score over visitors with has_page_view=1; NULL if none

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
NULL::DOUBLE avg_engagement_score
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#avg_engagement_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/1756674 | 0/65120 |
| L1 | 104898/1821792 | 104898/1756674 | 0/65118 |
| L2 | 104898/1821806 | 104898/1756674 | 0/65132 |
| L3 | 104898/1821806 | 104898/1756674 | 0/65132 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_pages_per_visitor

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

仅恢复单个按visitor聚合的指标，daily主行集仍使用原agent来源。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_pages_per_visitor
>         data_type: DOUBLE
>         description: Average unique_pages_viewed over visitors with has_page_view=1; NULL if none

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
NULL::DOUBLE avg_pages_per_visitor
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#avg_pages_per_visitor`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/1771831 | 0/49963 |
| L1 | 104898/1821792 | 104898/1771829 | 0/49963 |
| L2 | 104898/1821806 | 104898/1771843 | 0/49963 |
| L3 | 104898/1821806 | 104898/1771843 | 0/49963 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_features_per_user

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

仅恢复单个按visitor聚合的指标，daily主行集仍使用原agent来源。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_features_per_user
>         data_type: DOUBLE
>         description: Average unique_features_used over visitors with has_feature_interaction=1; NULL if none

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
NULL::DOUBLE avg_features_per_user
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#avg_features_per_user`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/1821797 | 0/-3 |
| L1 | 104898/1821792 | 104898/1821796 | 0/-4 |
| L2 | 104898/1821806 | 104898/1821809 | 0/-3 |
| L3 | 104898/1821806 | 104898/1821809 | 0/-3 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### high_quality_session_rate

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

仅恢复单个按visitor聚合的指标，daily主行集仍使用原agent来源。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: high_quality_session_rate
>         data_type: FLOAT
>         description: Distinct visitors with session_quality='High Quality' divided by total_visitors; NULL if total_visitors=0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
NULL::FLOAT high_quality_session_rate
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#high_quality_session_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/1771831 | 0/49963 |
| L1 | 104898/1821792 | 104898/1771829 | 0/49963 |
| L2 | 104898/1821806 | 104898/1771843 | 0/49963 |
| L3 | 104898/1821806 | 104898/1771843 | 0/49963 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### bounce_rate

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

仅恢复单个按visitor聚合的指标，daily主行集仍使用原agent来源。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: bounce_rate
>         data_type: FLOAT
>         description: Distinct visitors with session_quality='Bounce' divided by total_visitors; NULL if total_visitors=0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
NULL::FLOAT bounce_rate
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#bounce_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/1771879 | 0/49915 |
| L1 | 104898/1821792 | 104898/1771884 | 0/49908 |
| L2 | 104898/1821806 | 104898/1771897 | 0/49909 |
| L3 | 104898/1821806 | 104898/1771897 | 0/49909 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_30d_page_to_feature_rate

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确相对today的30日下界、cohort按account/app等值连接；agent对全历史做窗口平均，未执行规定算法。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_30d_page_to_feature_rate
>         data_type: DOUBLE
>         description: Average of daily page_to_feature_conversion_rate for dates on or after 30 days before today (inclusive); NULL if no data

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
avg(page_to_feature_conversion_rate) OVER(PARTITION BY account_id,app_id) avg_30d_page_to_feature_rate
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#avg_30d_page_to_feature_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/1771831 | 0/49963 |
| L1 | 104898/1821792 | 104898/1771829 | 0/49963 |
| L2 | 104898/1821806 | 104898/1771843 | 0/49963 |
| L3 | 104898/1821806 | 104898/1771843 | 0/49963 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### avg_30d_feature_to_deep_rate

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确相对today的30日下界、cohort按account/app等值连接；agent对全历史做窗口平均，未执行规定算法。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_30d_feature_to_deep_rate
>         data_type: DOUBLE
>         description: Average of daily feature_to_deep_conversion_rate for dates on or after 30 days before today (inclusive); NULL if no data

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
avg(feature_to_deep_conversion_rate) OVER(PARTITION BY account_id,app_id) avg_30d_feature_to_deep_rate
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#avg_30d_feature_to_deep_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/1771831 | 0/49963 |
| L1 | 104898/1821792 | 104898/1771829 | 0/49963 |
| L2 | 104898/1821806 | 104898/1771843 | 0/49963 |
| L3 | 104898/1821806 | 104898/1771843 | 0/49963 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### avg_30d_overall_conversion_rate

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确相对today的30日下界、cohort按account/app等值连接；agent对全历史做窗口平均，未执行规定算法。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_30d_overall_conversion_rate
>         data_type: DOUBLE
>         description: Average of daily overall_conversion_rate for dates on or after 30 days before today (inclusive); NULL if no data

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
avg(overall_conversion_rate) OVER(PARTITION BY account_id,app_id) avg_30d_overall_conversion_rate
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#avg_30d_overall_conversion_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/1771831 | 0/49963 |
| L1 | 104898/1821792 | 104898/1771829 | 0/49963 |
| L2 | 104898/1821806 | 104898/1771843 | 0/49963 |
| L3 | 104898/1821806 | 104898/1771843 | 0/49963 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### funnel_health_rating

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复固定分类为规定阈值，不改其输入。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: funnel_health_rating
>         data_type: VARCHAR
>         description: 'Rating by 30-day average overall rate: Excellent (≥0.3), Good (≥0.2), Fair (≥0.1), else Poor'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
'Poor' funnel_health_rating
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#funnel_health_rating`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/1868246 | 0/-46452 |
| L1 | 104898/1821792 | 104898/1868244 | 0/-46452 |
| L2 | 104898/1821806 | 104898/1868258 | 0/-46452 |
| L3 | 104898/1821806 | 104898/1868258 | 0/-46452 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;

交付报告明确点到这张表/这类指标及其占位或选择。

### optimization_recommendation

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复建议分支；bounce输入仍保留原NULL占位。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: optimization_recommendation
>         data_type: VARCHAR
>         description: 'Based on 30-day averages: feature discovery if page→feature<0.2; engagement if feature→deep<0.3; reduce bounce if bounce rate>0.6; else maintain'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：

```sql
'Focus on feature discovery and onboarding' optimization_recommendation
```

单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#optimization_recommendation`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 104898/1821794 | 104898/1775342 | 0/46452 |
| L1 | 104898/1821792 | 104898/1775340 | 0/46452 |
| L2 | 104898/1821806 | 104898/1775354 | 0/46452 |
| L3 | 104898/1821806 | 104898/1775354 | 0/46452 |

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
