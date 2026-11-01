# impl-011_jira__stakeholder_engagement_insights（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**多因并列**；把握：中；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`多因并列（D、O）`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 4524, "cell_scale": 43122}, "L1": {"row_scale": 4524, "cell_scale": 43122}, "L2": {"row_scale": 4524, "cell_scale": 43122}, "L3": {"row_scale": 4524, "cell_scale": 43122}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| engagement_depth_score | 其他 | 并列 | 0 | 4524 | 4 |
| total_engagement_score | 其他 | 并列 | 0 | 4524 | 4 |
| influence_level | 其他 | 并列 | 0 | 4524 | 4 |
| stakeholder_archetype | 已说出的降级 | 并列 | 0 | 4524 | 1 |
| development_opportunity | 已说出的降级 | 并列 | 0 | 4524 | 1 |
| strategic_value_score | 已说出的降级 | 参与 | 0 | 3999 | 1 |
| recommended_engagement_strategy | 已说出的降级 | 参与 | 0 | 2441 | 1 |
| engagement_risk_status | 已说出的降级 | 参与 | 0 | 2231 | 1 |
| engagement_quality_score | 已说出的降级 | 参与 | 0 | 1309 | 1 |
| engagement_impact_score | 已说出的降级 | 参与 | 0 | 12 | 1 |
| total_comments_authored | 其他 | 参与 | 0 | 1633 | 4 |
| total_projects_involved | 其他 | 参与 | 0 | 2418 | 4 |
| cross_functional_projects | 其他 | 参与 | 0 | 356 | 4 |
| engagement_breadth_score | 其他 | 参与 | 0 | 1579 | 4 |
| response_label_only | 其他 | 参与 | 0 | 3215 | 4 |
| response_calculation_only | 已说出的降级 | 非原因 | 0 | 0 | 1 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: jira__stakeholder_engagement_insights
      description: Stakeholder engagement analysis with interaction network metrics, scorecards, and strategic recommendations (one row per active Jira user)
      grain: One row per active stakeholder_id
      source_models:
      - staging.stg_jira__user
      - staging.stg_jira__issue
      - staging.stg_jira__comment
      - staging.stg_jira__project
      - intermediate.int_jira__issue_join
      business_logic: 'Build base activity for each active user (is_active = true): - Reporter metrics: unique issues reported and unique projects reported to; average lifecycle in days from creation to resolution, using current time for unresolved issues. - Assignee metrics: unique issues assigned and unique projects assigned to; average resolution time in days, using current time for unresolved issues. - Comment metrics: total comments authored; average comment length over authored comments. - Total projects involved: unique projects seen across the user’s reported or assigned issues (null projects excluded). Construct interaction network between commenters on the same issue: - Pair comments by different authors where the partner’s comment occurs on or after the author’s comment and within 7 days. - Aggregate per author–partner pair: unique issues discussed together; total interaction instances; average response time in hours (absolute time gap); average combined comment length; count of same-calendar-day interactions. - Compute interaction strength as interaction count, upweighted for broad discussions (>10 distinct issues) and for faster average responses (<24 hours). - Keep only pairs with at least 3 interaction instances. Compute stakeholder influence metrics by joining users to the interaction network: - Outbound (user as author): direct network connections (unique partners), average outbound interaction strength, and total outbound interaction strength. - Inbound (user as partner): total inbound interaction strength. - Cross-functional projects: unique projects tied to any issue the user reported or was assigned (nulls excluded). - Response pattern from average assigned resolution days: Rapid (≤7), Timely (≤14), Standard (≤30), else Slow; if no value, treat as Slow. Score engagement (each capped at 25): - Breadth: 3 points per project involved + 5 points per cross-functional project + up to 10 points for direct connections (maximum 25). - Depth: communication component (15 points if >100 comments, else comments ÷ 7) plus influence component (10 points if average outbound strength >50, else average outbound strength ÷ 5); capped at 25; if average outbound strength is null, depth is null. - Quality: responder class points (Rapid 15; Timely 10; Standard 5; Slow 0) plus 10 points if average outbound strength >30; capped at 25. - Impact: outbound influence tier (>500: 15; >200: 10; >50: 5; else 0) plus workload tier by issues assigned (>50: 10; >20: 7; >5: 3; else 0); capped at 25. Behavioral patterns and classifications: - Total engagement score = breadth + depth + quality + impact (0–100 when depth is present; null if depth is null). - Stakeholder archetype (first match): Power Collaborator (breadth ≥20 and depth ≥15); Quality Influencer (quality ≥20 and impact ≥15); Cross-Functional Coordinator (breadth ≥15 and projects involved ≥5); Deep Specialist (depth ≥20); High Impact Contributor (impact ≥20); Active Communicator (comments >100); Heavy Executor (issues assigned >20); Requirements Driver (issues reported >20); Network Hub (connections >10); else Standard Participant. - Influence level (first match): High (outbound influence >500 and connections >15); Medium (outbound influence >200 and connections >8); Low (outbound influence >50 or connections >3); else Minimal. - Engagement risk (first match): Disengagement Risk (total engagement <20); Delivery Risk (Slow responder and issues assigned >10); Overwhelm Risk (inbound influence more than double outbound); Isolation Risk (connections <2 and projects involved >1); else Healthy Engagement. Strategic insights: - Strategic value score (first match): 100 (Power Collaborator or Quality Influencer with High Influence); 85 (Cross-Functional Coordinator or High Impact Contributor with High/Medium Influence); 70 (Deep Specialist or Network Hub); 75 (High Influence); 60 (total engagement ≥70); 45 (≥50); else 30. - Recommended strategy (first match): Re-engagement Campaign; Performance Support; Workload Optimization; Network Integration; Leverage and Amplify (Power Collaborator); Strategic Partnering (Quality Influencer); Key Relationship Management (High Influence); else Standard Engagement. - Development opportunity (first match): Cross-Project Exposure (breadth <10 and depth ≥15); Communication Effectiveness Training (quality <10 and comments >50); Leadership Development (impact <10 and issues assigned >20); Network Building (connections <3); Cross-Functional Assignment (no cross-functional projects); else Advanced Leadership Opportunities. Final output: one row per active stakeholder_id with all fields above; rows are ordered by strategic value score descending, then total engagement score descending.'
      columns:
      - name: stakeholder_id
        data_type: VARCHAR
        description: Active user_id serving as the stakeholder key; exactly one output row per stakeholder_id
        tests:
        - not_null
        - unique
      - name: user_display_name
        data_type: VARCHAR
        description: Display name for the stakeholder from the user source
        tests:
        - not_null
      - name: issues_reported
        data_type: BIGINT
        description: Unique issues the stakeholder reported; null issue_ids excluded; returns 0 if none
      - name: issues_assigned
        data_type: BIGINT
        description: Unique issues assigned to the stakeholder; null issue_ids excluded; returns 0 if none
      - name: total_comments_authored
        data_type: BIGINT
        description: Total comments authored by the stakeholder; returns 0 if none
      - name: total_projects_involved
        data_type: BIGINT
        description: Unique projects seen across the stakeholder’s reported or assigned issues; null projects excluded; returns 0 if none
      - name: direct_network_connections
        data_type: BIGINT
        description: Unique interaction partners from the filtered network (only pairs with at least 3 interactions); returns 0 if none
      - name: response_pattern_type
        data_type: VARCHAR
        description: 'Assignee resolution speed class: Rapid (≤7d), Timely (≤14d), Standard (≤30d), else Slow; null values treated as Slow'
        tests:
        - not_null
      - name: avg_outbound_influence_strength
        data_type: DOUBLE
        description: Average interaction strength across outbound connections; excludes nulls; null if no outbound interactions
      - name: total_outbound_influence
        data_type: DECIMAL(38,2)
        description: Total interaction strength across outbound connections; null if no outbound interactions
      - name: total_inbound_influence
        data_type: DECIMAL(38,2)
        description: Total interaction strength across inbound connections (where the stakeholder is the partner); null if no inbound interactions
      - name: cross_functional_projects
        data_type: BIGINT
        description: Unique projects for issues where the stakeholder is reporter or assignee; null projects excluded; returns 0 if none
      - name: engagement_breadth_score
        data_type: BIGINT
        description: 0–25, calculated as 3 points per project involved + 5 per cross-functional project + up to 10 for direct connections; capped at 25; never null
      - name: engagement_depth_score
        data_type: DOUBLE
        description: 0–25, sum of a communication component (15 if comments >100 else comments ÷ 7) and an influence component (10 if avg strength >50 else avg strength ÷ 5); capped at 25; null if average outbound strength is null
      - name: engagement_quality_score
        data_type: INTEGER
        description: 0–25, responder class points (Rapid 15, Timely 10, Standard 5, Slow 0) plus 10 if average outbound strength >30; capped at 25; never null
        tests:
        - not_null
      - name: engagement_impact_score
        data_type: INTEGER
        description: 0–25, sum of outbound influence tier (>500:15, >200:10, >50:5, else 0) and issues-assigned tier (>50:10, >20:7, >5:3, else 0); capped at 25; never null
        tests:
        - not_null
      - name: total_engagement_score
        data_type: DOUBLE
        description: Sum of breadth, depth, quality, and impact (0–100 when depth is present); null if engagement_depth_score is null
      - name: stakeholder_archetype
        data_type: VARCHAR
        description: 'Ordered classification: Power Collaborator, Quality Influencer, Cross-Functional Coordinator, Deep Specialist, High Impact Contributor, Active Communicator, Heavy Executor, Requirements Driver, Network Hub, else Standard Participant'
        tests:
        - not_null
      - name: influence_level
        data_type: VARCHAR
        description: 'Ordered tiers: High (outbound >500 and connections >15), Medium (outbound >200 and connections >8), Low (outbound >50 or connections >3), else Minimal'
        tests:
        - not_null
      - name: strategic_value_score
        data_type: INTEGER
        description: 'Ordered mapping: 100 for Power Collaborator or Quality Influencer with High Influence; 85 for Cross-Functional Coordinator or High Impact Contributor with High/Medium Influence; 70 for Deep Specialist or Network Hub; 75 for High Influence; 60 if total engagement ≥70; 45 if ≥50; else 30'
        tests:
        - not_null
      - name: engagement_risk_status
        data_type: VARCHAR
        description: 'Ordered risks: Disengagement (<20 total engagement), Delivery (Slow responder and issues assigned >10), Overwhelm (inbound > 2× outbound), Isolation (connections <2 and projects involved >1), else Healthy'
        tests:
        - not_null
      - name: recommended_engagement_strategy
        data_type: VARCHAR
        description: 'Ordered strategies: Re-engagement Campaign, Performance Support, Workload Optimization, Network Integration, Leverage and Amplify, Strategic Partnering, Key Relationship Management, else Standard Engagement'
        tests:
        - not_null
      - name: development_opportunity
        data_type: VARCHAR
        description: 'Ordered opportunities: Cross-Project Exposure, Communication Effectiveness Training, Leadership Development, Network Building, Cross-Functional Assignment, else Advanced Leadership Opportunities'
        tests:
        - not_null
```

### 逐点结论

#### engagement_depth_score

并列；**其他**；把握高。

契约明确avg_outbound_influence_strength为NULL时depth为NULL，total随之NULL；诊断4524行均无该strength，而gold的LEAST忽略NULL产生非空分数。agent的本列NULL与契约一致。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 38598 |
| L1 | 4524 | 4524 | 43122 | 38598 |
| L2 | 4524 | 4524 | 43122 | 38598 |
| L3 | 4524 | 4524 | 43122 | 38598 |

重跑：`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `engagement_depth_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
null::double engagement_depth_score
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### total_engagement_score

并列；**其他**；把握高。

契约明确avg_outbound_influence_strength为NULL时depth为NULL，total随之NULL；诊断4524行均无该strength，而gold的LEAST忽略NULL产生非空分数。agent的本列NULL与契约一致。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 38598 |
| L1 | 4524 | 4524 | 43122 | 38598 |
| L2 | 4524 | 4524 | 43122 | 38598 |
| L3 | 4524 | 4524 | 43122 | 38598 |

重跑：`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `total_engagement_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
null::double total_engagement_score
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### influence_level

并列；**其他**；把握高。

agent的Minimal短标签符合契约；gold加Influence后缀，分类含义相同。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 38598 |
| L1 | 4524 | 4524 | 43122 | 38598 |
| L2 | 4524 | 4524 | 43122 | 38598 |
| L3 | 4524 | 4524 | 43122 | 38598 |

重跑：`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `influence_level`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
'Minimal' influence_level
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### stakeholder_archetype

并列；**已说出的降级**；把握高。

stakeholder_archetype是固定值，未执行契约的评分/阈值/分类分支；现有活动、用户与issue数据足以计算。finish点名stakeholder dashboard详细业务计算使用默认/简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 38598 |
| L1 | 4524 | 4524 | 43122 | 38598 |
| L2 | 4524 | 4524 | 43122 | 38598 |
| L3 | 4524 | 4524 | 43122 | 38598 |

重跑：`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `stakeholder_archetype`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
'Standard Participant' stakeholder_archetype
```

#### development_opportunity

并列；**已说出的降级**；把握高。

development_opportunity是固定值，未执行契约的评分/阈值/分类分支；现有活动、用户与issue数据足以计算。finish点名stakeholder dashboard详细业务计算使用默认/简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 38598 |
| L1 | 4524 | 4524 | 43122 | 38598 |
| L2 | 4524 | 4524 | 43122 | 38598 |
| L3 | 4524 | 4524 | 43122 | 38598 |

重跑：`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `development_opportunity`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
'Advanced Leadership Opportunities' development_opportunity
```

#### strategic_value_score

参与；**已说出的降级**；把握高。

strategic_value_score是固定值，未执行契约的评分/阈值/分类分支；现有活动、用户与issue数据足以计算。finish点名stakeholder dashboard详细业务计算使用默认/简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 39123 |
| L1 | 4524 | 4524 | 43122 | 39123 |
| L2 | 4524 | 4524 | 43122 | 39123 |
| L3 | 4524 | 4524 | 43122 | 39123 |

重跑：`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `strategic_value_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
30::integer strategic_value_score
```

#### recommended_engagement_strategy

参与；**已说出的降级**；把握高。

recommended_engagement_strategy是固定值，未执行契约的评分/阈值/分类分支；现有活动、用户与issue数据足以计算。finish点名stakeholder dashboard详细业务计算使用默认/简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 40681 |
| L1 | 4524 | 4524 | 43122 | 40681 |
| L2 | 4524 | 4524 | 43122 | 40681 |
| L3 | 4524 | 4524 | 43122 | 40681 |

重跑：`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `recommended_engagement_strategy`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
'Standard Engagement' recommended_engagement_strategy
```

#### engagement_risk_status

参与；**已说出的降级**；把握高。

engagement_risk_status是固定值，未执行契约的评分/阈值/分类分支；现有活动、用户与issue数据足以计算。finish点名stakeholder dashboard详细业务计算使用默认/简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 40891 |
| L1 | 4524 | 4524 | 43122 | 40891 |
| L2 | 4524 | 4524 | 43122 | 40891 |
| L3 | 4524 | 4524 | 43122 | 40891 |

重跑：`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `engagement_risk_status`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
'Healthy Engagement' engagement_risk_status
```

#### engagement_quality_score

参与；**已说出的降级**；把握高。

engagement_quality_score是固定值，未执行契约的评分/阈值/分类分支；现有活动、用户与issue数据足以计算。finish点名stakeholder dashboard详细业务计算使用默认/简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 41813 |
| L1 | 4524 | 4524 | 43122 | 41813 |
| L2 | 4524 | 4524 | 43122 | 41813 |
| L3 | 4524 | 4524 | 43122 | 41813 |

重跑：`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `engagement_quality_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
0::integer engagement_quality_score
```

#### engagement_impact_score

参与；**已说出的降级**；把握高。

engagement_impact_score是固定值，未执行契约的评分/阈值/分类分支；现有活动、用户与issue数据足以计算。finish点名stakeholder dashboard详细业务计算使用默认/简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 43110 |
| L1 | 4524 | 4524 | 43122 | 43110 |
| L2 | 4524 | 4524 | 43122 | 43110 |
| L3 | 4524 | 4524 | 43122 | 43110 |

重跑：`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `engagement_impact_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
0::integer engagement_impact_score
```

#### total_comments_authored

参与；**其他**；把握高。

agent直接按author计评论符合契约；gold在reporter/assignee多表连接后count(*)放大评论。021诊断1633名用户被多计，总超额5921。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 41489 |
| L1 | 4524 | 4524 | 43122 | 41489 |
| L2 | 4524 | 4524 | 43122 | 41489 |
| L3 | 4524 | 4524 | 43122 | 41489 |

重跑：`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `total_comments_authored`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
coalesce(cm.total_comments,0)::bigint total_comments_authored
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### total_projects_involved

参与；**其他**；把握高。

agent对reported或assigned项目取并集去重，符合契约。gold用coalesce(reporter_project,assignee_project)遗漏另一侧，不能把并集改成gold读法归Intent。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 40704 |
| L1 | 4524 | 4524 | 43122 | 40704 |
| L2 | 4524 | 4524 | 43122 | 40704 |
| L3 | 4524 | 4524 | 43122 | 40704 |

重跑：`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `total_projects_involved`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
coalesce(a.total_projects_involved,0)::bigint total_projects_involved
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### cross_functional_projects

参与；**其他**；把握中。

契约按用户报告或被分配issue涉及的唯一非空项目计数，agent按此计数；gold另连接project实体，只计匹配成功的项目，排除孤立项目ID。不是0/NULL默认政策。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 42766 |
| L1 | 4524 | 4524 | 43122 | 42766 |
| L2 | 4524 | 4524 | 43122 | 42766 |
| L3 | 4524 | 4524 | 43122 | 42766 |

重跑：`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `cross_functional_projects`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
coalesce(a.total_projects_involved,0)::bigint cross_functional_projects
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### engagement_breadth_score

参与；**其他**；把握中。

本数据network无满足阈值的边，agent的8×项目数等价契约3×projects+5×cross_functional（同一issue项目并集）。gold分别用coalesce漏项目和匹配实体排除项目，造成分数不同；未另虚构独立Intent点。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 41543 |
| L1 | 4524 | 4524 | 43122 | 41543 |
| L2 | 4524 | 4524 | 43122 | 41543 |
| L3 | 4524 | 4524 | 43122 | 41543 |

重跑：`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json` / `engagement_breadth_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
least(25,coalesce(a.total_projects_involved,0)*8)::bigint engagement_breadth_score
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### response_label_only

参与；**其他**；把握高。

契约列举Rapid/Timely/Standard/Slow短标签；gold附加Responder。本探针只把现有常量Slow变成Slow Responder，不修复缺失的响应计算。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 39907 |
| L1 | 4524 | 4524 | 43122 | 39907 |
| L2 | 4524 | 4524 | 43122 | 39907 |
| L3 | 4524 | 4524 | 43122 | 39907 |

重跑：`records/039_checks/supplement_impl-011_jira__stakeholder_engagement_insights.json` / `response_label_only`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
'Slow' response_pattern_type
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### response_calculation_only

非原因；**已说出的降级**；把握高。

response_pattern_type固定Slow，省略按assigned issue解决时长均值分档。用契约短标签恢复计算后，gold长标签使L0–L3仍全不匹配；标记非原因而不遗漏缺口。finish点名stakeholder简化分类。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4524 | 4524 | 43122 | 43122 |
| L1 | 4524 | 4524 | 43122 | 43122 |
| L2 | 4524 | 4524 | 43122 | 43122 |
| L3 | 4524 | 4524 | 43122 | 43122 |

重跑：`records/039_checks/supplement_impl-011_jira__stakeholder_engagement_insights.json` / `response_calculation_only`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

标记：存在未确立的前提，但不是判错原因。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql` / `SQL.text`（sql）：

```text
'Slow' response_pattern_type
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`，行[2913, 3015]；材料包 `records/021_packages/021_impl-011_jira__stakeholder_engagement_insights.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql`；SHA-256 `1000170045dc47269013cfe3b754873bff7ca78237e23dcdfe658086d7662d12`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / event 55。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 29，失败=True。
  - `records/021_supplement_queries.json` / index 22，失败=False。

## 不确定或没查到的（含规则问题）

- 旧response_pattern_type同时补计算和Responder后缀，不能当一个降级点的贡献；039拆开标签、计算和仅诊断组合。
- 规则问题：breadth和cross_functional按契约“issue所涉及项目”读为不另要求project实体匹配；另一读法是只计有效项目。选前者，与契约对null项目排除的明确限定相容，把握中。
- 总分、分类恢复探针用于定位输出差异；gold中项目/评论及NULL传播偏差已单列，不能用gold的类别直接证明agent应选择该类别。
- 039补充诊断stakeholder_diagnostic.json：4524用户，gold与原issue项目计数差356、与有效project实体计数差0；并集差2418；breadth差1579；非零网络0。支持本处Other，而非仅按旧标签或单改成功推定。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
