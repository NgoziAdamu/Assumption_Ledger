# impl-011 | marts | jira__stakeholder_engagement_insights | 差异：S1；日期 原记录

## 契约完整原文

S3:2913–3015

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

## agent 最终 SQL

S4

```sql
with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i.issue_id) filter(where i.reporter_user_id=user_id) issues_reported,count(distinct i.issue_id) filter(where i.assignee_user_id=user_id) issues_assigned,count(distinct i.project_id) filter(where i.reporter_user_id=user_id or i.assignee_user_id=user_id) total_projects_involved from active u left join staging.stg_jira__issue i on u.user_id in (i.reporter_user_id,i.assignee_user_id) group by user_id), cm as (select author_user_id,count(*) total_comments from staging.stg_jira__comment group by author_user_id) select u.user_id stakeholder_id,u.user_display_name,coalesce(a.issues_reported,0)::bigint issues_reported,coalesce(a.issues_assigned,0)::bigint issues_assigned,coalesce(cm.total_comments,0)::bigint total_comments_authored,coalesce(a.total_projects_involved,0)::bigint total_projects_involved,0::bigint direct_network_connections,'Slow' response_pattern_type,null::double avg_outbound_influence_strength,null::decimal(38,2) total_outbound_influence,null::decimal(38,2) total_inbound_influence,coalesce(a.total_projects_involved,0)::bigint cross_functional_projects,least(25,coalesce(a.total_projects_involved,0)*8)::bigint engagement_breadth_score,null::double engagement_depth_score,0::integer engagement_quality_score,0::integer engagement_impact_score,null::double total_engagement_score,'Standard Participant' stakeholder_archetype,'Minimal' influence_level,30::integer strategic_value_score,'Healthy Engagement' engagement_risk_status,'Standard Engagement' recommended_engagement_strategy,'Advanced Leadership Opportunities' development_opportunity from active u left join acts a using(user_id) left join cm on u.user_id=cm.author_user_id
```

## gold SQL（仅供定位差异）

S5

```sql
-- Advanced stakeholder engagement insights with behavioral analytics and influence mapping
-- Analyzes stakeholder interaction patterns, influence networks, and engagement effectiveness

with stakeholder_base_activity as (
    select 
        u.user_id,
        u.user_display_name,
        u.email,
        u.time_zone,
        u.is_active,
        
        -- Reporter activity
        count(distinct ir.issue_id) as issues_reported,
        count(distinct ir.project_id) as projects_reported_to,
        avg(extract('epoch' from (coalesce(ir.resolved_at, current_timestamp) - ir.created_at)) / 86400.0) as avg_reported_issue_lifecycle_days,
        
        -- Assignee activity  
        count(distinct ia.issue_id) as issues_assigned,
        count(distinct ia.project_id) as projects_assigned_to,
        avg(extract('epoch' from (coalesce(ia.resolved_at, current_timestamp) - ia.created_at)) / 86400.0) as avg_assigned_resolution_days,
        
        -- Comment engagement
        count(distinct c.issue_id) as issues_commented_on,
        count(*) filter (where c.author_user_id = u.user_id) as total_comments_authored,
        avg(length(c.body)) filter (where c.author_user_id = u.user_id) as avg_comment_length,
        
        -- Cross-project activity
        count(distinct coalesce(ir.project_id, ia.project_id)) as total_projects_involved
    from staging.stg_jira__user u
    left join staging.stg_jira__issue ir on u.user_id = ir.reporter_user_id
    left join staging.stg_jira__issue ia on u.user_id = ia.assignee_user_id
    left join staging.stg_jira__comment c on u.user_id = c.author_user_id
    left join intermediate.int_jira__issue_join ij on ia.issue_id = ij.issue_id
    where u.is_active = true
    group by 1,2,3,4,5
),

stakeholder_interaction_network as (
    select 
        c1.author_user_id as stakeholder_id,
        c2.author_user_id as interaction_partner_id,
        count(distinct c1.issue_id) as shared_issue_discussions,
        count(*) as total_interaction_instances,
        avg(abs(extract('epoch' from (c2.created_at - c1.created_at)) / 3600.0)) as avg_response_time_hours,
        
        -- Interaction quality indicators
        avg(length(c1.body) + length(c2.body)) as avg_combined_comment_length,
        count(case when c1.created_at::date = c2.created_at::date then 1 end) as same_day_interactions,
        
        -- Calculate interaction strength
        count(*) * 
        case when count(distinct c1.issue_id) > 10 then 1.5 else 1.0 end *
        case when avg(abs(extract('epoch' from (c2.created_at - c1.created_at)) / 3600.0)) < 24 then 1.2 else 1.0 end
        as interaction_strength_score
    from staging.stg_jira__comment c1
    join staging.stg_jira__comment c2 on c1.issue_id = c2.issue_id 
        and c1.author_user_id != c2.author_user_id
        and c2.created_at >= c1.created_at
        and c2.created_at <= c1.created_at + interval '7 days'
    where c1.author_user_id is not null and c2.author_user_id is not null
    group by 1,2
    having count(*) >= 3  -- Minimum interaction threshold
),

stakeholder_influence_metrics as (
    select 
        sba.user_id as stakeholder_id,
        sba.user_display_name,
        
        -- Direct influence indicators
        sba.issues_reported,
        sba.issues_assigned,
        sba.total_comments_authored,
        sba.total_projects_involved,
        
        -- Network influence indicators
        count(distinct sin_out.interaction_partner_id) as direct_network_connections,
        avg(sin_out.interaction_strength_score) as avg_outbound_influence_strength,
        sum(sin_out.interaction_strength_score) as total_outbound_influence,
        
        -- Being influenced indicators
        count(distinct sin_in.stakeholder_id) as influenced_by_count,
        avg(sin_in.interaction_strength_score) as avg_inbound_influence_strength,
        sum(sin_in.interaction_strength_score) as total_inbound_influence,
        
        -- Cross-functional collaboration (simplified)
        count(distinct p.project_id) as cross_functional_projects,
        
        -- Response and engagement patterns
        sba.avg_comment_length,
        case when sba.avg_assigned_resolution_days <= 7 then 'Rapid Responder'
             when sba.avg_assigned_resolution_days <= 14 then 'Timely Responder'
             when sba.avg_assigned_resolution_days <= 30 then 'Standard Responder'
             else 'Slow Responder'
        end as response_pattern_type
    from stakeholder_base_activity sba
    left join stakeholder_interaction_network sin_out on sba.user_id = sin_out.stakeholder_id
    left join stakeholder_interaction_network sin_in on sba.user_id = sin_in.interaction_partner_id
    left join staging.stg_jira__issue i on sba.user_id in (i.assignee_user_id, i.reporter_user_id)
    left join staging.stg_jira__project p on i.project_id = p.project_id
    group by 1,2,3,4,5,6,14,15
),

stakeholder_engagement_scoring as (
    select 
        sim.stakeholder_id,
        sim.user_display_name,
        sim.issues_reported,
        sim.issues_assigned,
        sim.total_comments_authored,
        sim.total_projects_involved,
        sim.direct_network_connections,
        sim.response_pattern_type,
        sim.avg_outbound_influence_strength,
        sim.total_outbound_influence,
        sim.total_inbound_influence,
        sim.cross_functional_projects,
        
        -- Engagement breadth score (0-25)
        least(25, 
            (sim.total_projects_involved * 3) +
            (sim.cross_functional_projects * 5) +
            (case when sim.direct_network_connections > 10 then 10 else sim.direct_network_connections end)
        ) as engagement_breadth_score,
        
        -- Engagement depth score (0-25)
        least(25,
            (case when sim.total_comments_authored > 100 then 15 else sim.total_comments_authored / 7 end) +
            (case when sim.avg_outbound_influence_strength > 50 then 10 else sim.avg_outbound_influence_strength / 5 end)
        ) as engagement_depth_score,
        
        -- Engagement quality score (0-25)
        least(25,
            (case when sim.response_pattern_type = 'Rapid Responder' then 15
                  when sim.response_pattern_type = 'Timely Responder' then 10
                  when sim.response_pattern_type = 'Standard Responder' then 5
                  else 0 end) +
            (case when sim.avg_outbound_influence_strength > 30 then 10 else 0 end)
        ) as engagement_quality_score,
        
        -- Engagement impact score (0-25)
        least(25,
            (case when sim.total_outbound_influence > 500 then 15
                  when sim.total_outbound_influence > 200 then 10
                  when sim.total_outbound_influence > 50 then 5
                  else 0 end) +
            (case when sim.issues_assigned > 50 then 10
                  when sim.issues_assigned > 20 then 7
                  when sim.issues_assigned > 5 then 3
                  else 0 end)
        ) as engagement_impact_score
    from stakeholder_influence_metrics sim
),

stakeholder_behavioral_patterns as (
    select 
        ses.*,
        
        -- Overall engagement score (0-100)
        engagement_breadth_score + engagement_depth_score + 
        engagement_quality_score + engagement_impact_score as total_engagement_score,
        
        -- Stakeholder archetype classification
        case 
            when engagement_breadth_score >= 20 and engagement_depth_score >= 15 then 'Power Collaborator'
            when engagement_quality_score >= 20 and engagement_impact_score >= 15 then 'Quality Influencer'
            when engagement_breadth_score >= 15 and total_projects_involved >= 5 then 'Cross-Functional Coordinator'
            when engagement_depth_score >= 20 then 'Deep Specialist'
            when engagement_impact_score >= 20 then 'High Impact Contributor'
            when total_comments_authored > 100 then 'Active Communicator'
            when issues_assigned > 20 then 'Heavy Executor'
            when issues_reported > 20 then 'Requirements Driver'
            when direct_network_connections > 10 then 'Network Hub'
            else 'Standard Participant'
        end as stakeholder_archetype,
        
        -- Influence level classification
        case 
            when total_outbound_influence > 500 and direct_network_connections > 15 then 'High Influence'
            when total_outbound_influence > 200 and direct_network_connections > 8 then 'Medium Influence'
            when total_outbound_influence > 50 or direct_network_connections > 3 then 'Low Influence'
            else 'Minimal Influence'
        end as influence_level,
        
        -- Engagement risk assessment
        case 
            when total_engagement_score < 20 then 'Disengagement Risk'
            when response_pattern_type = 'Slow Responder' and issues_assigned > 10 then 'Delivery Risk'
            when total_inbound_influence > total_outbound_influence * 2 then 'Overwhelm Risk'
            when direct_network_connections < 2 and total_projects_involved > 1 then 'Isolation Risk'
            else 'Healthy Engagement'
        end as engagement_risk_status
    from stakeholder_engagement_scoring ses
),

strategic_stakeholder_insights as (
    select 
        sbp.*,
        
        -- Strategic value calculation
        case 
            when stakeholder_archetype in ('Power Collaborator', 'Quality Influencer') and influence_level = 'High Influence' then 100
            when stakeholder_archetype in ('Cross-Functional Coordinator', 'High Impact Contributor') and influence_level in ('High Influence', 'Medium Influence') then 85
            when stakeholder_archetype in ('Deep Specialist', 'Network Hub') then 70
            when influence_level = 'High Influence' then 75
            when total_engagement_score >= 70 then 60
            when total_engagement_score >= 50 then 45
            else 30
        end as strategic_value_score,
        
        -- Recommended engagement strategy
        case 
            when engagement_risk_status = 'Disengagement Risk' then 'Re-engagement Campaign'
            when engagement_risk_status = 'Delivery Risk' then 'Performance Support'
            when engagement_risk_status = 'Overwhelm Risk' then 'Workload Optimization'
            when engagement_risk_status = 'Isolation Risk' then 'Network Integration'
            when stakeholder_archetype = 'Power Collaborator' then 'Leverage and Amplify'
            when stakeholder_archetype = 'Quality Influencer' then 'Strategic Partnering'
            when influence_level = 'High Influence' then 'Key Relationship Management'
            else 'Standard Engagement'
        end as recommended_engagement_strategy,
        
        -- Development opportunity identification
        case 
            when engagement_breadth_score < 10 and engagement_depth_score >= 15 then 'Cross-Project Exposure'
            when engagement_quality_score < 10 and total_comments_authored > 50 then 'Communication Effectiveness Training'
            when engagement_impact_score < 10 and issues_assigned > 20 then 'Leadership Development'
            when direct_network_connections < 3 then 'Network Building'
            when cross_functional_projects = 0 then 'Cross-Functional Assignment'
            else 'Advanced Leadership Opportunities'
        end as development_opportunity
    from stakeholder_behavioral_patterns sbp
)

select * from strategic_stakeholder_insights
order by strategic_value_score desc, total_engagement_score desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 4524 | 4524 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"stakeholder_id":"use10057335705"}</code> |
| K2 | <code>{"stakeholder_id":"use10081304164"}</code> |
| K3 | <code>{"stakeholder_id":"use10026174483"}</code> |
| K4 | <code>{"stakeholder_id":"use10473869886"}</code> |
| K5 | <code>{"stakeholder_id":"use10109626404"}</code> |
| K6 | <code>{"stakeholder_id":"use10295761032"}</code> |
| K7 | <code>{"stakeholder_id":"use16659753652"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| stakeholder_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| user_display_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| issues_reported | 0 | 0 | 0 | BIGINT | BIGINT |
| issues_assigned | 0 | 0 | 0 | BIGINT | BIGINT |
| total_comments_authored | 1633 | 1633 | 1633 | BIGINT | BIGINT |
| total_projects_involved | 2418 | 2418 | 2418 | BIGINT | BIGINT |
| direct_network_connections | 0 | 0 | 0 | BIGINT | BIGINT |
| response_pattern_type | 4524 | 4524 | 4524 | VARCHAR | VARCHAR |
| cross_functional_projects | 356 | 356 | 356 | BIGINT | BIGINT |
| engagement_breadth_score | 1579 | 1579 | 1579 | BIGINT | BIGINT |
| engagement_depth_score | 4524 | 4524 | 4524 | DOUBLE | DOUBLE |
| engagement_quality_score | 1309 | 1309 | 1309 | INTEGER | INTEGER |
| engagement_impact_score | 12 | 12 | 12 | INTEGER | INTEGER |
| total_engagement_score | 4524 | 4524 | 4524 | DOUBLE | DOUBLE |
| stakeholder_archetype | 4524 | 4524 | 4524 | VARCHAR | VARCHAR |
| influence_level | 4524 | 4524 | 4524 | VARCHAR | VARCHAR |
| engagement_risk_status | 2231 | 2231 | 2231 | VARCHAR | VARCHAR |
| strategic_value_score | 3999 | 3999 | 3999 | INTEGER | INTEGER |
| recommended_engagement_strategy | 2441 | 2441 | 2441 | VARCHAR | VARCHAR |
| development_opportunity | 4524 | 4524 | 4524 | VARCHAR | VARCHAR |

total_comments_authored 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2 | 6 |

total_projects_involved 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 4 | 2 |

response_pattern_type 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | Slow | Slow Responder |

cross_functional_projects 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | 5 | 4 |

engagement_breadth_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | 16 | 13 |

engagement_depth_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | null | 25.0 |

engagement_quality_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K6 | 0 | 10 |

engagement_impact_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K7 | 0 | 3 |

total_engagement_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | null | 25.0 |

stakeholder_archetype 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | Standard Participant | Deep Specialist |

influence_level 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | Minimal | Minimal Influence |

engagement_risk_status 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Healthy Engagement | Isolation Risk |

strategic_value_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | 30 | 70 |

recommended_engagement_strategy 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Standard Engagement | Network Integration |

development_opportunity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | Advanced Leadership Opportunities | Cross-Project Exposure |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>5列；[{"column":"avg_outbound_influence_strength","table_rows":4524}]</code> |
| A3_constant_nonnull_column | <code>10列；[{"column":"direct_network_connections","value":"0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["total_projects_involved","cross_functional_projects"],"nonnull_equal_rows":4524,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["total_projects_involved","cross_functional_projects"],"nonnull_equal_rows":4524,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>5输出列；[{"column":"avg_outbound_influence_strength","expression":["CAST(NULL AS DOUBLE)"]}]</code> |
| B6_constant_literal_output | <code>10输出列；[{"column":"direct_network_connections","expression":["CAST(0 AS BIGINT)"]}]</code> |
| B7_specified_not_read | <code>["intermediate.int_jira__issue_join"]</code> |
| C9_gold_runtime_text | <code>S5:15 current_timestamp；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:2922 current time；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory 'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i.issue_id) filter(where i.reporter_user_id=user_id) issues_reported,count(distinct i.issue_id) filter(where i.assignee_user_id=user_id) issues_assigned,count(distinct i.project_id) filter(where i.reporter_user_id=user_id or i.assignee_user_id=user_id) total_projects_involved from active u left join staging.stg_jira__issue i on u.user_id in (i.reporter_user_id,i.assignee_user_id) group by user_id), cm as (select author_user_id,count(*) total_comments from staging.stg_jira__comment group by author_user_id) select u.user_id stakeholder_id,u.user_display_name,coalesce(a.issues_reported,0)::bigint issues_reported,coalesce(a.issues_assigned,0)::bigint issues_assigned,coalesce(cm.total_comments,0)::bigint total_comments_authored,coalesce(a.total_projects_involved,0)::bigint total_projects_involved,0::bigint direct_network_connections,'Slow' response_pattern_type,null::double avg_outbound_influence_strength,null::decimal(38,2) total_outbound_influence,null::decimal(38,2) total_inbound_influence,coalesce(a.total_projects_involved,0)::bigint cross_functional_projects,least(25,coalesce(a.total_projects_involved,0)*8)::bigint engagement_breadth_score,null::double engagement_depth_score,0::integer engagement_quality_score,0::integer engagement_impact_score,null::double total_engagement_score,'Standard Participant' stakeholder_archetype,'Minimal' influence_level,30::integer strategic_value_score,'Healthy Engagement' engagement_risk_status,'Standard Engagement' recommended_engagement_strategy,'Advanced Leadership Opportunities' development_opportunity from active u left join acts a using(user_id) left join cm on u.user_id=cm.author_user_id",</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,240p' run.py</code> | 14395 | true | false |
| 11 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging')<br>queries={<br>'stg_jira__user':"""select cast(id as varchar) user_id, coalesce(nu</code> | 0 | false | false |
| 13 | run | <code>cat &gt; /tmp/gen_inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/intermediate')<br>Q={<br>'int_jira__issue_field_history':"select h.field_id,h.issue_id,h.updated_at,h.field_value,h.is_active,lower(f.fiel</code> | 0 | false | false |
| 15 | run | <code>cat &gt;&gt; /tmp/gen_inter.py &lt;&lt;'PY'<br>Q.update({<br>'int_jira__pivot_daily_field_history':"with h as (select field_id,issue_id,updated_at,field_value,field_name from intermediate.int_jira__issue_field_history </code> | 0 | false | false |
| 17 | run | <code>cat &gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>Q={<br>'jira__daily_issue_field_history':"select cast(i.created_at as date) date_day,cast(i.created_at as date) date_week,i.iss</code> | 0 | false | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import yaml,pathlib<br>c=yaml.safe_load(open('config/layer_dependencies.yaml'))<br>for layer,v in c['execution_order'].items():<br> existing={p.stem for p in pathlib.Path('sql',layer).glob('*.s</code> | 212 | true | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>Q.update({<br>'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i</code> | 6630 | true | false |
| 27 | run | <code>grep -oE '.{0,25}committed.{0,25}' sql/intermediate/int_jira__sprint_performance_analytics.sql &#124; head; python - &lt;&lt;'PY'<br>p='sql/intermediate/int_jira__user_activity_metrics.sql'<br>s=open(p).read(); start=</code> | 613 | false | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> s=re.sub(r'try_cast\((\w+) as timestamp\)',r"try_cast(regexp_replace(\1, '([+-][0-9]{2}</code> | 9550 | true | false |
| 33 | run | <code>cat sql/staging/stg_jira__issue_type.sql; grep -o '.\{0,30\}prev_committed.\{0,30\}' sql/intermediate/int_jira__sprint_performance_analytics.sql; cat sql/staging/stg_jira__issue.sql &#124; head -c 800</code> | 1230 | false | false |
| 35 | run | <code>sed -i 's/description,is_subtask subtask as is_subtask/description,subtask as is_subtask/' sql/staging/stg_jira__issue_type.sql; sed -i 's/committed_points-prev_committed)/committed_points-prev_commit</code> | 53 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text().replace("regexp_replace(created, '([+-][0-9]{2})([0-9]{2})$', '\\\\1:\\\\2')", "regexp_replace(cre</code> | 4200 | true | false |
| 41 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; grep -E 'INTERMEDIATE Layer&#124;✓ intermediate.int_jira__issue_join&#124;✓ intermediate.int_jira__issue_users&#124;staging.stg_jira__issue:' /tmp/runlog3</code> | 836 | false | false |
| 43 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; cat sql/intermediate/int_jira__issue_calendar_spine.sql</code> | 1202 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('jira.duckdb',read_only=True)<br>checks=[('staging.stg_jira__issue','issue_id'),('staging.stg_jira__project','project_id'),('intermediate.int_jira__issue_jo</code> | 422 | false | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i.issue_id) filter(where i.reporter_user_id=user_id) issues_reported,count(distinct i.issue_id) filter(where i.assignee_user_id=user_id) issues_assigned,count(distinct i.project_id) filter(where i.reporter_user_id=user_id or i.assignee_user_id=user_id) total_projects_involved from active u left join staging.stg_jira__issue i on u.user_id in (i.reporter_user_id,i.assignee_user_id) group by user_id), cm as (select author_user_id,count(*) total_comments from staging.stg_jira__comment group by author_user_id) select u.user_id stakeholder_id,u.user_display_name,coalesce(a.issues_reported,0)::bigint issues_reported,coalesce(a.issues_assigned,0)::bigint issues_assigned,coalesce(cm.total_comments,0)::bigint total_comments_authored,coalesce(a.total_projects_involved,0)::bigint total_projects_involved,0::bigint direct_network_connections,'Slow' response_pattern_type,null::double avg_outbound_influence_strength,null::decimal(38,2) total_outbound_influence,null::decimal(38,2) total_inbound_influence,coalesce(a.total_projects_involved,0)::bigint cross_functional_projects,least(25,coalesce(a.total_projects_involved,0)*8)::bigint engagement_breadth_score,null::double engagement_depth_score,0::integer engagement_quality_score,0::integer engagement_impact_score,null::double total_engagement_score,'Standard Participant' stakeholder_archetype,'Minimal' influence_level,30::integer strategic_value_score,'Healthy Engagement' engagement_risk_status,'Standard Engagement' recommended_engagement_strategy,'Advanced Leadership Opportunities' development_opportunity from active u left join acts a using(user_id) left join cm on u.user_id=cm.author_user_id",
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-011.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql`
- S6: `records/006_contract_impl-011.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/result.md`
- S10: `data/021_packages_work/021_impl-011_jira__stakeholder_engagement_insights/021_impl-011_jira__stakeholder_engagement_insights.json`
- S11: `data/005_cs_work/impl-011_retry_02/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/jira.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions`
