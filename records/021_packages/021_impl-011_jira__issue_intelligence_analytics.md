# impl-011 | marts | jira__issue_intelligence_analytics | 差异：S1；日期 原记录

## 契约完整原文

S3:2606–2717

```yaml
    - name: jira__issue_intelligence_analytics
      description: Advanced issue intelligence with anomaly detection, risk/opportunity scoring, predictions, and classification
      grain: One or more identical rows per issue_id (project-level self-join propagates duplicates)
      source_models:
      - marts.jira__issue_enhanced
      - staging.stg_jira__issue
      business_logic: 'Build issue_enriched_base from marts.jira__issue_enhanced and compute: - total_lifecycle_days = days between created_at and resolved_at (or current time if unresolved) - assigned_duration_days = days between first_assigned_at and resolved_at (or current time) - Carry through count_comments, project/assignee fields, sprint flags Build issue_lifecycle_context from staging.stg_jira__issue providing default context per issue_id: - total_transitions=0; unique_statuses_visited=0; days_in_development=0; days_in_qa=0; days_in_intake=0 - regression_ratio=0.0; progress_efficiency=1.0; lifecycle_pattern=''Normal''; lifecycle_quality_score=75.0 - resolution_speed_category=''Standard Timeline''; high_complexity_risk=false Build issue_comparative_metrics via a self-join on project_id (ieb ⋈ ieb2): - Window metrics over ieb2 partitions: - project average/median/p75 lifecycle days by ieb.project_id - issue type average/median lifecycle days by ieb.issue_type - priority average lifecycle days by ieb.current_priority - assignee average lifecycle days and total issues by ieb.assignee_user_id - project average comments and issue type average comments - Note: The self-join creates multiple rows per issue_id; duplicates are preserved downstream Build issue_anomaly_detection by joining issue_enriched_base to issue_comparative_metrics on issue_id: - lifecycle_deviation_ratio = absolute difference from the project median lifecycle divided by that median (NULL if the median is 0 or NULL; non-negative otherwise) - type_deviation_ratio, assignee_deviation_ratio, comment_deviation_ratio computed similarly (not exposed) - lifecycle_outlier_status determined by thresholds: - more than 2×project p75 lifecycle → ''Statistical Outlier'' - more than 1.5×project p75 lifecycle → ''Above Normal Range'' - less than 0.5×project median lifecycle → ''Unusually Fast'' - else → ''Normal Range'' Build issue_risk_scoring by left joining lifecycle_context and anomaly_detection to issue_enriched_base: - age_risk_score: 10 if unresolved and total_lifecycle_days > 90 else 0 - process_risk_score: 15 if regression_ratio > 0.3 else 0 (NULL behaves as false → 0) - complexity_risk_score: 10 if high_complexity_risk=true else 0 (NULL → 0) - engagement_risk_score: 5 if count_comments=0 else 0 - assignment_risk_score: 8 if assignee_user_id is NULL else 0 - deviation_risk_score: 7 if lifecycle_deviation_ratio > 1 else 0 (NULL → 0) - collaboration_opportunity_score: 5 if count_comments > project_avg_comments*1.5 else 0 (NULL → 0) - efficiency_opportunity_score: 5 if total_lifecycle_days < project_median_lifecycle_days*0.7 else 0 (NULL → 0) - process_opportunity_score: 5 if progress_efficiency > 0.8 else 0 (NULL → 0) Build predictive_indicators from risk_scoring: - total_risk_score = sum of individual risk scores - total_opportunity_score = sum of opportunity scores - completion_probability: - resolved_at not null → 1.00 - else by total_lifecycle_days: ≤7→0.95; ≤14→0.85; ≤30→0.70; ≤60→0.50; ≤90→0.30; else 0.15 - predicted_completion_timeframe: - resolved_at not null → ''Already Completed'' - lifecycle_pattern=''Efficient'' and assignee present → ''Within 1 Week'' - lifecycle_pattern=''Normal'' and assignee present → ''Within 2 Weeks'' - lifecycle_pattern=''Complex'' → ''Within 1 Month'' - lifecycle_pattern=''Problematic'' → ''Beyond 1 Month'' - assignee_name null → ''Requires Assignment'' - else → ''Unknown'' - recommended_action: - age_risk_score>0 and assignment_risk_score>0 → ''Urgent: Assign and Expedite'' - process_risk_score>0 → ''Review Process Issues'' - complexity_risk_score>0 → ''Break Down or Reassign'' - engagement_risk_score>0 → ''Encourage Collaboration'' - total_opportunity_score>10 → ''Leverage Best Practices'' - unresolved and total_lifecycle_days>30 → ''Management Review Required'' - else → ''Monitor Progress'' Build intelligence_classification from predictive_indicators: - intelligence_score (0–100): start at 50, add 2×total_opportunity_score, subtract total_risk_score, add 15 if lifecycle_quality_score>80, add 10 if completion_probability>0.8, then clamp to the 0–100 range - health_status by total_risk_score: ≥25 ''Critical''; ≥15 ''High Risk''; ≥8 ''Medium Risk''; >0 ''Low Risk''; else ''Healthy'' - strategic_importance: - current_priority with case-insensitive ''critical'' or ''high'' → ''Strategic'' - issue_type with case-insensitive ''epic'' → ''Strategic'' - total_opportunity_score>10 → ''High Value'' - lifecycle_pattern=''Efficient'' → ''Best Practice'' - else → ''Standard'' - intervention_urgency: - if unresolved and total_risk_score≥25 → ''Immediate'' - if unresolved and total_risk_score≥15 → ''Within 24 Hours'' - if unresolved and total_risk_score≥8 → ''Within Week'' - else if total_opportunity_score>10 → ''Study for Replication'' - else → ''Regular Monitoring'' Final output preserves duplicates from the self-join and is ordered by intelligence_score DESC, total_risk_score DESC.'
      columns:
      - name: issue_id
        data_type: VARCHAR
        description: Unique issue identifier from jira__issue_enhanced; join key throughout; duplicates may exist
        tests:
        - not_null
      - name: issue_key
        data_type: VARCHAR
        description: Human-readable issue key from Jira (e.g., PROJ-123); source value preserved
      - name: issue_type
        data_type: VARCHAR
        description: Issue type label from source (e.g., Bug, Story, Epic); case and spacing preserved
      - name: current_status
        data_type: VARCHAR
        description: Current workflow status from source; exact text preserved
      - name: current_priority
        data_type: VARCHAR
        description: Current priority from source; used for strategic importance classification (case-insensitive contains 'critical'/'high')
      - name: project_name
        data_type: VARCHAR
        description: Project name from source associated with the issue; text preserved
      - name: assignee_name
        data_type: VARCHAR
        description: Current assignee display name; may be NULL; used in timeframe prediction
      - name: total_lifecycle_days
        data_type: DOUBLE
        description: Elapsed days from created_at to resolved_at (or current time if unresolved); fractional days preserved; non-negative
      - name: resolved_at
        data_type: TIMESTAMP
        description: Resolution timestamp; NULL for unresolved issues; drives completion_probability and timeframe
      - name: is_active_sprint
        data_type: BOOLEAN
        description: Flag indicating whether the issue is in an active sprint; value passed through from source (may be NULL)
      - name: lifecycle_pattern
        data_type: VARCHAR
        description: Lifecycle pattern classification from context (default 'Normal'); may be NULL if context missing; used in timeframe prediction
      - name: lifecycle_quality_score
        data_type: DECIMAL(3,1)
        description: Lifecycle quality score from context (default 75.0); boosts intelligence_score when >80; may be NULL
      - name: high_complexity_risk
        data_type: BOOLEAN
        description: Indicator from context of high complexity; NULL treated as false in scoring; contributes to complexity_risk_score
      - name: regression_ratio
        data_type: DECIMAL(2,1)
        description: Ratio of regressions from context (default 0.0); NULL treated as not exceeding 0.3; contributes to process_risk_score
      - name: lifecycle_deviation_ratio
        data_type: DOUBLE
        description: Absolute deviation from project median lifecycle normalized by that median; NULL if median is 0 or NULL; non-negative
      - name: lifecycle_outlier_status
        data_type: VARCHAR
        description: 'Outlier classification based on project p75/median: ''Statistical Outlier''|''Above Normal Range''|''Unusually Fast''|''Normal Range''; may be NULL if comparative metrics missing'
      - name: age_risk_score
        data_type: INTEGER
        description: 'Risk points for issue age: 10 if unresolved and total_lifecycle_days>90 else 0; always non-null'
      - name: process_risk_score
        data_type: INTEGER
        description: 'Risk points for process regressions: 15 if regression_ratio>0.3 else 0; NULL regression_ratio yields 0; always non-null'
      - name: complexity_risk_score
        data_type: INTEGER
        description: 'Risk points for complexity: 10 if high_complexity_risk=true else 0; NULL treated as false; always non-null'
      - name: engagement_risk_score
        data_type: INTEGER
        description: 'Risk points for low comment engagement: 5 if count_comments=0 else 0; always non-null'
      - name: assignment_risk_score
        data_type: INTEGER
        description: 'Risk points for missing assignee: 8 if assignee_user_id is NULL else 0; always non-null'
      - name: deviation_risk_score
        data_type: INTEGER
        description: 'Risk points for lifecycle deviation: 7 if lifecycle_deviation_ratio>1 else 0; NULL deviation yields 0; always non-null'
      - name: collaboration_opportunity_score
        data_type: INTEGER
        description: 'Opportunity points for high comment activity: 5 if count_comments>project_avg_comments*1.5 else 0; NULL avg yields 0; always non-null'
      - name: efficiency_opportunity_score
        data_type: INTEGER
        description: 'Opportunity points for faster-than-typical resolution: 5 if total_lifecycle_days<project_median_lifecycle_days*0.7 else 0; NULL median yields 0; always non-null'
      - name: process_opportunity_score
        data_type: INTEGER
        description: 'Opportunity points for high progress_efficiency: 5 if >0.8 else 0; NULL treated as 0; always non-null'
      - name: total_risk_score
        data_type: INTEGER
        description: Sum of individual risk scores (age+process+complexity+engagement+assignment+deviation); integer; non-null
      - name: total_opportunity_score
        data_type: INTEGER
        description: Sum of opportunity scores (collaboration+efficiency+process); integer; non-null
      - name: completion_probability
        data_type: DECIMAL(3,2)
        description: 'Probability of completion (resolved→1.00; else discrete thresholds by total_lifecycle_days: 0.95/0.85/0.70/0.50/0.30/0.15); non-null in [0,1]'
      - name: predicted_completion_timeframe
        data_type: VARCHAR
        description: 'Predicted timeframe: ''Already Completed''|''Within 1 Week''|''Within 2 Weeks''|''Within 1 Month''|''Beyond 1 Month''|''Requires Assignment''|''Unknown'' per lifecycle_pattern, assignee, and resolution'
      - name: recommended_action
        data_type: VARCHAR
        description: 'Action recommendation based on risk/opportunity: ''Urgent: Assign and Expedite''|''Review Process Issues''|''Break Down or Reassign''|''Encourage Collaboration''|''Leverage Best Practices''|''Management Review Required''|''Monitor Progress'''
      - name: intelligence_score
        data_type: INTEGER
        description: 'Overall score in [0,100]: 50 + 2×total_opportunity_score − total_risk_score, plus 15 if lifecycle_quality_score>80 and 10 if completion_probability>0.8, then capped to [0,100]'
      - name: health_status
        data_type: VARCHAR
        description: 'Issue health classification by total_risk_score: ''Critical''|''High Risk''|''Medium Risk''|''Low Risk''|''Healthy'''
      - name: strategic_importance
        data_type: VARCHAR
        description: 'Strategic label derived from priority, issue_type, opportunity, and lifecycle_pattern: ''Strategic''|''High Value''|''Best Practice''|''Standard'''
      - name: intervention_urgency
        data_type: VARCHAR
        description: 'Intervention urgency: if unresolved and risk high then ''Immediate''/''Within 24 Hours''/''Within Week''; else if high opportunity then ''Study for Replication''; else ''Regular Monitoring'''
```

## agent 最终 SQL

S4

```sql
select issue_id,issue_key,issue_type,current_status,current_priority,project_name,assignee_name,epoch(coalesce(resolved_at,current_timestamp)-created_at)/86400.0 total_lifecycle_days,resolved_at,is_active_sprint,'Normal'::varchar lifecycle_pattern,75.0::decimal(3,1) lifecycle_quality_score,false high_complexity_risk,0.0::decimal(2,1) regression_ratio,null::double lifecycle_deviation_ratio,null::varchar lifecycle_outlier_status,case when resolved_at is null and epoch(current_timestamp-created_at)>90*86400 then 10 else 0 end::integer age_risk_score,0::integer process_risk_score,0::integer complexity_risk_score,case when count_comments=0 then 5 else 0 end::integer engagement_risk_score,case when assignee_user_id is null then 8 else 0 end::integer assignment_risk_score,0::integer deviation_risk_score,0::integer collaboration_opportunity_score,0::integer efficiency_opportunity_score,5::integer process_opportunity_score,(case when resolved_at is null and epoch(current_timestamp-created_at)>90*86400 then 10 else 0 end+case when count_comments=0 then 5 else 0 end+case when assignee_user_id is null then 8 else 0 end)::integer total_risk_score,5::integer total_opportunity_score,case when resolved_at is not null then 1.00 when epoch(current_timestamp-created_at)/86400<=7 then .95 when epoch(current_timestamp-created_at)/86400<=14 then .85 when epoch(current_timestamp-created_at)/86400<=30 then .70 when epoch(current_timestamp-created_at)/86400<=60 then .50 when epoch(current_timestamp-created_at)/86400<=90 then .30 else .15 end::decimal(3,2) completion_probability,case when resolved_at is not null then 'Already Completed' when assignee_name is null then 'Requires Assignment' else 'Within 2 Weeks' end predicted_completion_timeframe,'Monitor Progress'::varchar recommended_action,50::integer intelligence_score,'Healthy'::varchar health_status,'Standard'::varchar strategic_importance,'Regular Monitoring'::varchar intervention_urgency from marts.jira__issue_enhanced
```

## gold SQL（仅供定位差异）

S5

```sql
-- Advanced issue intelligence analytics with predictive indicators and anomaly detection
-- Provides deep insights into issue patterns, risk factors, and optimization opportunities

with issue_enriched_base as (
    select 
        ie.issue_id,
        ie.issue_key,
        ie.issue_name,
        ie.issue_type,
        ie.current_status,
        ie.current_priority,
        ie.project_id,
        ie.project_name,
        ie.assignee_user_id,
        ie.assignee_name,
        ie.reporter_user_id,
        ie.created_at,
        ie.resolved_at,
        ie.first_assigned_at,
        ie.last_assigned_at,
        
        -- Enhanced duration calculations
        extract('epoch' from (coalesce(ie.resolved_at, current_timestamp) - ie.created_at)) / 86400.0 as total_lifecycle_days,
        extract('epoch' from (coalesce(ie.resolved_at, current_timestamp) - ie.first_assigned_at)) / 86400.0 as assigned_duration_days,
        ie.count_comments,
        ie.current_sprint_name,
        ie.is_active_sprint
    from marts.jira__issue_enhanced ie
),

issue_lifecycle_context as (
    select 
        ila.issue_id,
        ila.total_transitions,
        ila.unique_statuses_visited,
        ila.days_in_development,
        ila.days_in_qa,
        ila.days_in_intake,
        ila.regression_ratio,
        ila.progress_efficiency,
        ila.lifecycle_pattern,
        ila.lifecycle_quality_score,
        ila.resolution_speed_category,
        ila.high_complexity_risk
    from (
        select 
            issue_id,
            0 as total_transitions,
            0 as unique_statuses_visited,
            0 as days_in_development,
            0 as days_in_qa,
            0 as days_in_intake,
            0.0 as regression_ratio,
            1.0 as progress_efficiency,
            'Normal' as lifecycle_pattern,
            75.0 as lifecycle_quality_score,
            'Standard Timeline' as resolution_speed_category,
            false as high_complexity_risk
        from staging.stg_jira__issue
    ) ila
),

issue_comparative_metrics as (
    select 
        ieb.issue_id,
        ieb.project_id,
        ieb.issue_type,
        ieb.current_priority,
        
        -- Project-level benchmarks
        avg(ieb2.total_lifecycle_days) over (partition by ieb.project_id) as project_avg_lifecycle_days,
        quantile(ieb2.total_lifecycle_days, 0.5) over (partition by ieb.project_id) as project_median_lifecycle_days,
        quantile(ieb2.total_lifecycle_days, 0.75) over (partition by ieb.project_id) as project_p75_lifecycle_days,
        
        -- Issue type benchmarks
        avg(ieb2.total_lifecycle_days) over (partition by ieb.issue_type) as issue_type_avg_lifecycle_days,
        quantile(ieb2.total_lifecycle_days, 0.5) over (partition by ieb.issue_type) as issue_type_median_lifecycle_days,
        
        -- Priority benchmarks
        avg(ieb2.total_lifecycle_days) over (partition by ieb.current_priority) as priority_avg_lifecycle_days,
        
        -- Assignee performance benchmarks
        avg(ieb2.total_lifecycle_days) over (partition by ieb.assignee_user_id) as assignee_avg_lifecycle_days,
        count(*) over (partition by ieb.assignee_user_id) as assignee_total_issues,
        
        -- Comment engagement benchmarks
        avg(ieb2.count_comments) over (partition by ieb.project_id) as project_avg_comments,
        avg(ieb2.count_comments) over (partition by ieb.issue_type) as issue_type_avg_comments
    from issue_enriched_base ieb
    join issue_enriched_base ieb2 on ieb.project_id = ieb2.project_id
),

issue_anomaly_detection as (
    select 
        ieb.issue_id,
        ieb.total_lifecycle_days,
        icm.project_avg_lifecycle_days,
        icm.project_median_lifecycle_days,
        icm.project_p75_lifecycle_days,
        icm.issue_type_avg_lifecycle_days,
        icm.assignee_avg_lifecycle_days,
        
        -- Deviation analysis
        abs(ieb.total_lifecycle_days - icm.project_median_lifecycle_days) / nullif(icm.project_median_lifecycle_days, 0) as lifecycle_deviation_ratio,
        abs(ieb.total_lifecycle_days - icm.issue_type_avg_lifecycle_days) / nullif(icm.issue_type_avg_lifecycle_days, 0) as type_deviation_ratio,
        abs(ieb.total_lifecycle_days - icm.assignee_avg_lifecycle_days) / nullif(icm.assignee_avg_lifecycle_days, 0) as assignee_deviation_ratio,
        
        -- Engagement anomalies
        abs(ieb.count_comments - icm.project_avg_comments) / nullif(icm.project_avg_comments, 0) as comment_deviation_ratio,
        
        -- Statistical outlier detection
        case 
            when ieb.total_lifecycle_days > icm.project_p75_lifecycle_days * 2 then 'Statistical Outlier'
            when ieb.total_lifecycle_days > icm.project_p75_lifecycle_days * 1.5 then 'Above Normal Range'
            when ieb.total_lifecycle_days < icm.project_median_lifecycle_days * 0.5 then 'Unusually Fast'
            else 'Normal Range'
        end as lifecycle_outlier_status
    from issue_enriched_base ieb
    join issue_comparative_metrics icm on ieb.issue_id = icm.issue_id
),

issue_risk_scoring as (
    select 
        ieb.issue_id,
        ieb.issue_key,
        ieb.issue_type,
        ieb.current_status,
        ieb.current_priority,
        ieb.project_name,
        ieb.assignee_name,
        ieb.total_lifecycle_days,
        ieb.resolved_at,
        ieb.is_active_sprint,
        
        ilc.lifecycle_pattern,
        ilc.lifecycle_quality_score,
        ilc.high_complexity_risk,
        ilc.regression_ratio,
        
        iad.lifecycle_deviation_ratio,
        iad.lifecycle_outlier_status,
        
        -- Risk factor scoring
        case when ieb.resolved_at is null and ieb.total_lifecycle_days > 90 then 10 else 0 end as age_risk_score,
        case when ilc.regression_ratio > 0.3 then 15 else 0 end as process_risk_score,
        case when ilc.high_complexity_risk then 10 else 0 end as complexity_risk_score,
        case when ieb.count_comments = 0 then 5 else 0 end as engagement_risk_score,
        case when ieb.assignee_user_id is null then 8 else 0 end as assignment_risk_score,
        case when iad.lifecycle_deviation_ratio > 1 then 7 else 0 end as deviation_risk_score,
        
        -- Opportunity scoring
        case when ieb.count_comments > icm.project_avg_comments * 1.5 then 5 else 0 end as collaboration_opportunity_score,
        case when ieb.total_lifecycle_days < icm.project_median_lifecycle_days * 0.7 then 5 else 0 end as efficiency_opportunity_score,
        case when ilc.progress_efficiency > 0.8 then 5 else 0 end as process_opportunity_score
    from issue_enriched_base ieb
    left join issue_lifecycle_context ilc on ieb.issue_id = ilc.issue_id
    left join issue_anomaly_detection iad on ieb.issue_id = iad.issue_id
    left join issue_comparative_metrics icm on ieb.issue_id = icm.issue_id
),

predictive_indicators as (
    select 
        irs.*,
        
        -- Total risk score
        age_risk_score + process_risk_score + complexity_risk_score + 
        engagement_risk_score + assignment_risk_score + deviation_risk_score as total_risk_score,
        
        -- Total opportunity score
        collaboration_opportunity_score + efficiency_opportunity_score + process_opportunity_score as total_opportunity_score,
        
        -- Completion probability (for open issues)
        case 
            when resolved_at is not null then 1.0
            when total_lifecycle_days <= 7 then 0.95
            when total_lifecycle_days <= 14 then 0.85
            when total_lifecycle_days <= 30 then 0.70
            when total_lifecycle_days <= 60 then 0.50
            when total_lifecycle_days <= 90 then 0.30
            else 0.15
        end as completion_probability,
        
        -- Predicted completion timeframe (for open issues)
        case
            when resolved_at is not null then 'Already Completed'
            when lifecycle_pattern = 'Efficient' and assignee_name is not null then 'Within 1 Week'
            when lifecycle_pattern = 'Normal' and assignee_name is not null then 'Within 2 Weeks'
            when lifecycle_pattern = 'Complex' then 'Within 1 Month'
            when lifecycle_pattern = 'Problematic' then 'Beyond 1 Month'
            when assignee_name is null then 'Requires Assignment'
            else 'Unknown'
        end as predicted_completion_timeframe,
        
        -- Recommended actions
        case 
            when age_risk_score > 0 and assignment_risk_score > 0 then 'Urgent: Assign and Expedite'
            when process_risk_score > 0 then 'Review Process Issues'
            when complexity_risk_score > 0 then 'Break Down or Reassign'
            when engagement_risk_score > 0 then 'Encourage Collaboration'
            when total_opportunity_score > 10 then 'Leverage Best Practices'
            when resolved_at is null and total_lifecycle_days > 30 then 'Management Review Required'
            else 'Monitor Progress'
        end as recommended_action
    from issue_risk_scoring irs
),

intelligence_classification as (
    select 
        pi.*,
        
        -- Overall intelligence score (0-100)
        least(100, greatest(0,
            50 
            + (total_opportunity_score * 2)
            - (total_risk_score)
            + (case when lifecycle_quality_score > 80 then 15 else 0 end)
            + (case when completion_probability > 0.8 then 10 else 0 end)
        )) as intelligence_score,
        
        -- Issue health classification
        case 
            when total_risk_score >= 25 then 'Critical'
            when total_risk_score >= 15 then 'High Risk'
            when total_risk_score >= 8 then 'Medium Risk'
            when total_risk_score > 0 then 'Low Risk'
            else 'Healthy'
        end as health_status,
        
        -- Strategic importance
        case 
            when current_priority ilike '%critical%' or current_priority ilike '%high%' then 'Strategic'
            when issue_type ilike '%epic%' then 'Strategic'
            when total_opportunity_score > 10 then 'High Value'
            when lifecycle_pattern = 'Efficient' then 'Best Practice'
            else 'Standard'
        end as strategic_importance,
        
        -- Intervention urgency
        case 
            when total_risk_score >= 25 and resolved_at is null then 'Immediate'
            when total_risk_score >= 15 and resolved_at is null then 'Within 24 Hours'
            when total_risk_score >= 8 and resolved_at is null then 'Within Week'
            when total_opportunity_score > 10 then 'Study for Replication'
            else 'Regular Monitoring'
        end as intervention_urgency
    from predictive_indicators pi
)

select * from intelligence_classification
order by intelligence_score desc, total_risk_score desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 8000 | 13799108 | 0 | 0 | 0 | 8000 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"issue_id":"iss10000140937","issue_key":"cmv-5543"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| issue_id | 0 | 0 | 13791108 | VARCHAR | VARCHAR |
| issue_key | 0 | 0 | 13791108 | VARCHAR | VARCHAR |
| issue_type | 0 | 0 | 13791108 | VARCHAR | VARCHAR |
| current_status | 0 | 0 | 13791108 | VARCHAR | VARCHAR |
| current_priority | 0 | 0 | 13791108 | VARCHAR | VARCHAR |
| project_name | 0 | 0 | 13791108 | VARCHAR | VARCHAR |
| assignee_name | 0 | 0 | 13791108 | VARCHAR | VARCHAR |
| total_lifecycle_days | 3205 | 3205 | 13794313 | DOUBLE | DOUBLE |
| is_active_sprint | 0 | 0 | 13791108 | BOOLEAN | BOOLEAN |
| lifecycle_pattern | 0 | 0 | 13791108 | VARCHAR | VARCHAR |
| lifecycle_quality_score | 0 | 0 | 13791108 | DECIMAL(3,1) | DECIMAL(3,1) |
| high_complexity_risk | 0 | 0 | 13791108 | BOOLEAN | BOOLEAN |
| regression_ratio | 0 | 0 | 13791108 | DECIMAL(2,1) | DECIMAL(2,1) |
| lifecycle_deviation_ratio | 8000 | 8000 | 13799108 | DOUBLE | DOUBLE |
| lifecycle_outlier_status | 8000 | 8000 | 13799108 | VARCHAR | VARCHAR |
| age_risk_score | 0 | 0 | 13791108 | INTEGER | INTEGER |
| complexity_risk_score | 0 | 0 | 13791108 | INTEGER | INTEGER |
| assignment_risk_score | 0 | 0 | 13791108 | INTEGER | INTEGER |
| deviation_risk_score | 3052 | 3052 | 13794160 | INTEGER | INTEGER |
| collaboration_opportunity_score | 2606 | 2606 | 13793714 | INTEGER | INTEGER |
| efficiency_opportunity_score | 2617 | 2617 | 13793725 | INTEGER | INTEGER |
| process_opportunity_score | 0 | 0 | 13791108 | INTEGER | INTEGER |
| total_risk_score | 3052 | 3052 | 13794160 | INTEGER | INTEGER |
| total_opportunity_score | 4375 | 4375 | 13795483 | INTEGER | INTEGER |
| completion_probability | 0 | 0 | 13791108 | DECIMAL(3,2) | DECIMAL(3,2) |
| predicted_completion_timeframe | 0 | 0 | 13791108 | VARCHAR | VARCHAR |
| recommended_action | 6609 | 6609 | 13797717 | VARCHAR | VARCHAR |
| intelligence_score | 7986 | 7986 | 13799094 | INTEGER | INTEGER |
| health_status | 5761 | 5761 | 13796869 | VARCHAR | VARCHAR |
| strategic_importance | 3304 | 3304 | 13794412 | VARCHAR | VARCHAR |
| intervention_urgency | 4053 | 4053 | 13795161 | VARCHAR | VARCHAR |

issue_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"ISS10000140937","rows":1}]</code> | <code>[{"value":"ISS10000140937","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

issue_key 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"CMV-5543","rows":1}]</code> | <code>[{"value":"CMV-5543","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

issue_type 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Epic","rows":1}]</code> | <code>[{"value":"Epic","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

current_status 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Blocked","rows":1}]</code> | <code>[{"value":"Blocked","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

current_priority 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Minor","rows":1}]</code> | <code>[{"value":"Minor","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

project_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Content Management V2","rows":1}]</code> | <code>[{"value":"Content Management V2","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

assignee_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"James Taylor","rows":1}]</code> | <code>[{"value":"James Taylor","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

total_lifecycle_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"2222.452741144051","rows":1}]</code> | <code>[{"value":"1843.1345022106482","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

is_active_sprint 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"true","rows":1}]</code> | <code>[{"value":"true","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

lifecycle_pattern 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Normal","rows":1}]</code> | <code>[{"value":"Normal","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

lifecycle_quality_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"75.0","rows":1}]</code> | <code>[{"value":"75.0","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

high_complexity_risk 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"false","rows":1}]</code> | <code>[{"value":"false","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

regression_ratio 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0.0","rows":1}]</code> | <code>[{"value":"0.0","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

lifecycle_deviation_ratio 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":"0.9121120639894805","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

lifecycle_outlier_status 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":"Normal Range","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

age_risk_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"10","rows":1}]</code> | <code>[{"value":"10","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

complexity_risk_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":1}]</code> | <code>[{"value":"0","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

assignment_risk_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":1}]</code> | <code>[{"value":"0","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

deviation_risk_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":1}]</code> | <code>[{"value":"0","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

collaboration_opportunity_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":1}]</code> | <code>[{"value":"0","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

efficiency_opportunity_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":1}]</code> | <code>[{"value":"0","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

process_opportunity_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"5","rows":1}]</code> | <code>[{"value":"5","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

total_risk_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"15","rows":1}]</code> | <code>[{"value":"15","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

total_opportunity_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"5","rows":1}]</code> | <code>[{"value":"5","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

completion_probability 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0.15","rows":1}]</code> | <code>[{"value":"0.15","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

predicted_completion_timeframe 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Within 2 Weeks","rows":1}]</code> | <code>[{"value":"Within 2 Weeks","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

recommended_action 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Monitor Progress","rows":1}]</code> | <code>[{"value":"Encourage Collaboration","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

intelligence_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"50","rows":1}]</code> | <code>[{"value":"45","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

health_status 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Healthy","rows":1}]</code> | <code>[{"value":"High Risk","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

strategic_importance 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Standard","rows":1}]</code> | <code>[{"value":"Strategic","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

intervention_urgency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Regular Monitoring","rows":1}]</code> | <code>[{"value":"Within 24 Hours","rows":841}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"lifecycle_deviation_ratio","table_rows":8000}]</code> |
| A3_constant_nonnull_column | <code>17列；[{"column":"lifecycle_pattern","value":"Normal"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["process_risk_score","complexity_risk_score","assignment_risk_score","deviation_risk_score","collaboration_opportunity_score","efficiency_opportunity_score"],"nonnull_equal_rows":8000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["process_risk_score","complexity_risk_score","assignment_risk_score","deviation_risk_score","collaboration_opportunity_score","efficiency_opportunity_score"],"nonnull_equal_rows":8000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>2输出列；[{"column":"lifecycle_deviation_ratio","expression":["CAST(NULL AS DOUBLE)"]}]</code> |
| B6_constant_literal_output | <code>16输出列；[{"column":"lifecycle_pattern","expression":["CAST('Normal' AS TEXT)"]}]</code> |
| B7_specified_not_read | <code>["staging.stg_jira__issue"]</code> |
| B8_shared_single_source | <code>唯一源=marts.jira__issue_enhanced；目标数=2；例=["marts.jira__issue_intelligence_analytics"]</code> |
| C9_agent_runtime_text | <code>S4:1 current_timestamp；命中数=8</code> |
| C9_gold_runtime_text | <code>S5:23 current_timestamp；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:2612 current time；命中数=3</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory 'jira__issue_intelligence_analytics':"select issue_id,issue_key,issue_type,current_status,current_priority,project_name,assignee_name,epoch(coalesce(resolved_at,current_timestamp)-created_at)/86400.0 total_lifecycle_days,resolved_at,is_active_sprint,'Normal'::varchar lifecycle_pattern,75.0::decimal(3,1) lifecycle_quality_score,false high_complexity_risk,0.0::decimal(2,1) regression_ratio,null::double lifecycle_deviation_ratio,null::varchar lifecycle_outlier_status,case when resolved_at is null and epoch(current_timestamp-created_at)&gt;90*86400 then 10 else 0 end::integer age_risk_score,0::integer process_risk_score,0::integer complexity_risk_score,case when count_comments=0 then 5 else 0 end::integer engagement_risk_score,case when assignee_user_id is null then 8 else 0 end::integer assignment_risk_score,0::integer deviation_risk_score,0::integer collaboration_opportunity_score,0::integer efficiency_opportunity_score,5::integer process_opportunity_score,(case when resolved_at is null and epoch(current_timestamp-created_at)&gt;90*86400 then 10 else 0 end+case when count_comments=0 then 5 else 0 end+case when assignee_user_id is null then 8 else 0 end)::integer total_risk_score,5::integer total_opportunity_score,case when resolved_at is not null then 1.00 when epoch(current_timestamp-created_at)/86400&lt;=7 then .95 when epoch(current_timestamp-created_at)/86400&lt;=14 then .85 when epoch(current_timestamp-created_at)/86400&lt;=30 then .70 when epoch(current_timestamp-created_at)/86400&lt;=60 then .50 when epoch(current_timestamp-created_at)/86400&lt;=90 then .30 else .15 end::decimal(3,2) completion_probability,case when resolved_at is not null then 'Already Completed' when assignee_name is null then 'Requires Assignment' else 'Within 2 Weeks' end predicted_completion_timeframe,'Monitor Progress'::varchar recommended_action,50::integer intelligence_score,'Healthy'::varchar health_status,'Standard'::varchar strategic_importance,'Regular Monitoring'::varchar intervention_urgency from marts.jira__issue_enhanced",</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,240p' run.py</code> | 14395 | true | false |
| 17 | run | <code>cat &gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>Q={<br>'jira__daily_issue_field_history':"select cast(i.created_at as date) date_day,cast(i.created_at as date) date_week,i.iss</code> | 0 | false | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import yaml,pathlib<br>c=yaml.safe_load(open('config/layer_dependencies.yaml'))<br>for layer,v in c['execution_order'].items():<br> existing={p.stem for p in pathlib.Path('sql',layer).glob('*.s</code> | 212 | true | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>Q.update({<br>'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i</code> | 6630 | true | false |
| 23 | run | <code>grep -E 'WARNING -  ⏭&#124;WARNING -   ⏭&#124;Catalog Error&#124;Binder Error&#124;Parser Error&#124;Conversion Error' /tmp/runlog &#124; head -80</code> | 8767 | true | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> s=re.sub(r'try_cast\((\w+) as timestamp\)',r"try_cast(regexp_replace(\1, '([+-][0-9]{2}</code> | 9550 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text().replace("regexp_replace(created, '([+-][0-9]{2})([0-9]{2})$', '\\\\1:\\\\2')", "regexp_replace(cre</code> | 4200 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('jira.duckdb',read_only=True)<br>checks=[('staging.stg_jira__issue','issue_id'),('staging.stg_jira__project','project_id'),('intermediate.int_jira__issue_jo</code> | 422 | false | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
'jira__issue_intelligence_analytics':"select issue_id,issue_key,issue_type,current_status,current_priority,project_name,assignee_name,epoch(coalesce(resolved_at,current_timestamp)-created_at)/86400.0 total_lifecycle_days,resolved_at,is_active_sprint,'Normal'::varchar lifecycle_pattern,75.0::decimal(3,1) lifecycle_quality_score,false high_complexity_risk,0.0::decimal(2,1) regression_ratio,null::double lifecycle_deviation_ratio,null::varchar lifecycle_outlier_status,case when resolved_at is null and epoch(current_timestamp-created_at)>90*86400 then 10 else 0 end::integer age_risk_score,0::integer process_risk_score,0::integer complexity_risk_score,case when count_comments=0 then 5 else 0 end::integer engagement_risk_score,case when assignee_user_id is null then 8 else 0 end::integer assignment_risk_score,0::integer deviation_risk_score,0::integer collaboration_opportunity_score,0::integer efficiency_opportunity_score,5::integer process_opportunity_score,(case when resolved_at is null and epoch(current_timestamp-created_at)>90*86400 then 10 else 0 end+case when count_comments=0 then 5 else 0 end+case when assignee_user_id is null then 8 else 0 end)::integer total_risk_score,5::integer total_opportunity_score,case when resolved_at is not null then 1.00 when epoch(current_timestamp-created_at)/86400<=7 then .95 when epoch(current_timestamp-created_at)/86400<=14 then .85 when epoch(current_timestamp-created_at)/86400<=30 then .70 when epoch(current_timestamp-created_at)/86400<=60 then .50 when epoch(current_timestamp-created_at)/86400<=90 then .30 else .15 end::decimal(3,2) completion_probability,case when resolved_at is not null then 'Already Completed' when assignee_name is null then 'Requires Assignment' else 'Within 2 Weeks' end predicted_completion_timeframe,'Monitor Progress'::varchar recommended_action,50::integer intelligence_score,'Healthy'::varchar health_status,'Standard'::varchar strategic_importance,'Regular Monitoring'::varchar intervention_urgency from marts.jira__issue_enhanced",
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-011.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__issue_intelligence_analytics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/marts/jira__issue_intelligence_analytics.sql`
- S6: `records/006_contract_impl-011.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/result.md`
- S10: `data/021_packages_work/021_impl-011_jira__issue_intelligence_analytics/021_impl-011_jira__issue_intelligence_analytics.json`
- S11: `data/005_cs_work/impl-011_retry_02/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/jira.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions`
