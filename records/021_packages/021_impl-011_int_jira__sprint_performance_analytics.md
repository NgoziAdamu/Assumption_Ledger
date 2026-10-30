# impl-011 | intermediate | int_jira__sprint_performance_analytics | 差异：S1；日期 原记录

## 契约完整原文

S3:1265–1414

```yaml
    - name: int_jira__sprint_performance_analytics
      description: Advanced sprint performance analytics with start/end snapshots, burndown, velocity trends, and risk/health classification
      grain: 'One row per sprint_id per generated snapshot (at most two: start and end/complete)'
      source_models:
      - staging.stg_jira__sprint
      - staging.stg_jira__issue
      - staging.stg_jira__issue_field_history
      - staging.stg_jira__field
      business_logic: 'Data assembly: - From staging.stg_jira__sprint, keep sprints with started_at not null. Derive start_date = date(started_at), end_date = date(ended_at), complete_date = date(completed_at). - planned_duration_days = (ended_at - started_at) in days when both exist, else null. actual_duration_days = (completed_at - started_at) in days when both exist (not used later). Sprint issues: - Create sprint_issues by pairing issues with sprints (cross join) and keeping only issue rows where issue.created_at falls between sprint.started_at and coalesce(sprint.completed_at, sprint.ended_at, current_timestamp). Apply a global LIMIT 1000 without ordering, so metrics are based on an arbitrary subset of qualifying rows. - story_points per issue: take the latest active field value whose field name contains “story” and “point”; use the numeric value if the field is numeric or extract the first numeric substring; if unavailable/unparsable, default to 1. - time_spent_seconds and original_estimate_seconds default to 0 when null. Snapshots: - For each sprint, create: - Start snapshot: snapshot_date = start_date, day_number = 1 (always). - End snapshot: only when planned_duration_days > 1; snapshot_date = complete_date, else end_date, else current_date; day_number = planned_duration_days. Metrics per snapshot (group by sprint and snapshot): - total_story_points_committed: sum of story_points across all included issue rows (no de-duplication). - story_points_completed: sum of story_points where issue_resolved_at date is on/before snapshot_date. story_points_remaining: sum of story_points where issue_resolved_at is null or its date is after snapshot_date. - total_issues_committed: count of issue rows. issues_completed: count where resolved on/before snapshot_date. issues_remaining: count where unresolved or resolved after snapshot_date. - total_estimated_hours: sum(original_estimate_seconds)/3600.0. hours_spent_completed: sum(time_spent_seconds) for issues resolved by snapshot_date divided by 3600.0. total_hours_spent: sum(time_spent_seconds)/3600.0. Burndown and indicators (computed within each sprint ordered by day_number): - ideal_story_points_remaining: a linear ideal line from committed at day 1 down to 0 at the end; if planned_duration_days > 0, scale by (1 - (day_number - 1)/planned_duration_days); otherwise keep at committed. - daily_velocity: previous snapshot’s story_points_remaining minus current (null for the first snapshot; may be negative). - completion_ratio: story_points_completed / committed, rounded to 3 decimals; 0 when committed is 0. - timeline_progress_ratio: day_number / planned_duration_days, rounded to 3 decimals when planned_duration_days > 0; otherwise set to 1 (can exceed 1 when planned_duration_days < 1). - scope_change_points and scope_change_issues: change in committed story points and issue count since the previous snapshot (null for the first snapshot). - burndown_variance: story_points_remaining minus ideal_story_points_remaining. - performance_index: completion_ratio divided by timeline_progress_ratio when timeline_progress_ratio > 0; otherwise null. - velocity_trend_3d: moving average of daily_velocity over up to the last three snapshots in the sprint; null when the window has no non-null values. - predicted_completion_day: when daily_velocity > 0 and remaining > 0, forecast as day_number plus (remaining/daily_velocity); otherwise null. Classifications: - sprint_risk_status: Behind Schedule if completion_ratio < timeline_progress_ratio - 0.2; Ahead of Schedule if completion_ratio > timeline_progress_ratio + 0.1; Scope Creep if abs(scope_change_points) > 10% of committed; otherwise On Track. - sprint_health_score (0–100): start at 100; subtract 30 if Behind Schedule; subtract 20 if Scope Creep; subtract 25 if abs(burndown_variance) > 30% of committed; add 10 if Ahead of Schedule; add 15 if performance_index > 1.1; clamp to [0,100]. - velocity_category: High Velocity (>5), Good Velocity (>2), Low Velocity (>0), No Progress (=0), else Negative Velocity. - sprint_phase: Early Phase (timeline_progress_ratio ≤ 0.3), Mid Phase (≤ 0.6), Late Phase (≤ 0.9), else Final Phase. Output is ordered by sprint_id then day_number.'
      columns:
      - name: sprint_id
        data_type: VARCHAR
        description: Sprint primary identifier used for grouping and ordering
        tests:
        - not_null
      - name: sprint_name
        data_type: VARCHAR
        description: Sprint name from staging.stg_jira__sprint
      - name: snapshot_date
        data_type: DATE
        description: Snapshot date (start_date; and end/complete/current_date when planned_duration_days > 1)
        tests:
        - not_null
      - name: day_number
        data_type: DOUBLE
        description: 'Snapshot index: 1 at start; planned_duration_days at end/complete; ordered ascending within each sprint'
        tests:
        - not_null
        - day_number >= 1
      - name: planned_duration_days
        data_type: DOUBLE
        description: Planned sprint duration in days as (ended_at − started_at)/86400; null if ended_at is null; non-negative when present
        tests:
        - planned_duration_days IS NULL OR planned_duration_days >= 0
      - name: total_story_points_committed
        data_type: DECIMAL(38,3)
        description: Sum of story points for included issue rows; defaults to 1 per issue when the field is missing or unparseable; no de-duplication
        tests:
        - not_null
        - total_story_points_committed >= 0
      - name: story_points_completed
        data_type: DECIMAL(38,3)
        description: Sum of story points for issues resolved on/before snapshot_date
        tests:
        - not_null
        - story_points_completed >= 0
      - name: story_points_remaining
        data_type: DECIMAL(38,3)
        description: Sum of story points for issues unresolved or resolved after snapshot_date
        tests:
        - not_null
        - story_points_remaining >= 0
      - name: total_issues_committed
        data_type: BIGINT
        description: Count of included issue rows within the sprint window
        tests:
        - not_null
        - total_issues_committed >= 0
      - name: issues_completed
        data_type: BIGINT
        description: Count of issues resolved on/before snapshot_date
        tests:
        - not_null
        - issues_completed >= 0
      - name: issues_remaining
        data_type: BIGINT
        description: Count of issues unresolved or resolved after snapshot_date
        tests:
        - not_null
        - issues_remaining >= 0
      - name: total_estimated_hours
        data_type: DOUBLE
        description: Total original estimate hours across included issues (seconds summed and divided by 3600.0)
        tests:
        - not_null
        - total_estimated_hours >= 0
      - name: hours_spent_completed
        data_type: DOUBLE
        description: Total hours spent on issues resolved by snapshot_date (seconds summed for those issues and divided by 3600.0)
        tests:
        - not_null
        - hours_spent_completed >= 0
      - name: total_hours_spent
        data_type: DOUBLE
        description: Total hours spent across included issues (seconds summed and divided by 3600.0)
        tests:
        - not_null
        - total_hours_spent >= 0
      - name: ideal_story_points_remaining
        data_type: DOUBLE
        description: Ideal remaining story points based on a straight-line burndown from committed at day 1 to 0 at the end; if no planned duration, equals committed
        tests:
        - not_null
        - ideal_story_points_remaining >= 0
      - name: daily_velocity
        data_type: DECIMAL(38,3)
        description: Change in story_points_remaining since the previous snapshot; null for the first snapshot; may be negative
      - name: completion_ratio
        data_type: DOUBLE
        description: 'Rounded to 3 decimals: story_points_completed divided by committed; 0 when committed is 0; range [0,1]'
        tests:
        - completion_ratio >= 0 AND completion_ratio <= 1
      - name: timeline_progress_ratio
        data_type: DOUBLE
        description: 'Rounded to 3 decimals: day_number divided by planned_duration_days when planned_duration_days > 0, else 1; may exceed 1 when planned_duration_days < 1'
        tests:
        - timeline_progress_ratio >= 0
      - name: scope_change_points
        data_type: DECIMAL(38,3)
        description: Change in committed story points since the previous snapshot; null for the first snapshot; may be positive or negative
      - name: scope_change_issues
        data_type: BIGINT
        description: Change in committed issue count since the previous snapshot; null for the first snapshot; may be positive or negative
      - name: burndown_variance
        data_type: DOUBLE
        description: Difference between actual remaining and ideal remaining story points; positive means behind ideal, negative means ahead
        tests:
        - not_null
      - name: performance_index
        data_type: DOUBLE
        description: Ratio of completion to timeline progress when progress is > 0; null otherwise; values > 1 indicate ahead of timeline
      - name: velocity_trend_3d
        data_type: DOUBLE
        description: Moving average of daily_velocity over up to the last three snapshots within the sprint; null when the window has no non-null values
      - name: predicted_completion_day
        data_type: DOUBLE
        description: 'Forecasted completion snapshot index: current day_number plus remaining divided by daily_velocity when both positive; otherwise null'
        tests:
        - predicted_completion_day IS NULL OR predicted_completion_day > day_number
      - name: sprint_risk_status
        data_type: VARCHAR
        description: 'Risk label based on completion vs timeline thresholds and scope change: Behind/Ahead/Scope Creep/On Track'
        tests:
        - not_null
      - name: sprint_health_score
        data_type: INTEGER
        description: Score from 0 to 100 using penalties for risk and variance and bonuses for positive indicators, clamped to the range
        tests:
        - not_null
        - sprint_health_score BETWEEN 0 AND 100
      - name: velocity_category
        data_type: VARCHAR
        description: 'Velocity tier from velocity_trend_3d: High/Good/Low/No Progress/Negative Velocity (Negative on null)'
        tests:
        - not_null
      - name: sprint_phase
        data_type: VARCHAR
        description: 'Phase bucket by timeline_progress_ratio: Early (≤0.3), Mid (≤0.6), Late (≤0.9), Final (>0.9)'
        tests:
        - not_null
```

## agent 最终 SQL

S4

```sql
with s as (select *,cast(started_at as date) start_date,cast(ended_at as date) end_date,cast(completed_at as date) complete_date,epoch(ended_at-started_at)/86400.0 planned_duration_days from staging.stg_jira__sprint where started_at is not null), snapshots as (select *,start_date snapshot_date,1.0 day_number from s union all select *,coalesce(complete_date,end_date,current_date) snapshot_date,planned_duration_days day_number from s where planned_duration_days>1), issues as (select s.sprint_id,s.sprint_name,s.snapshot_date,s.day_number,s.planned_duration_days,i.issue_id,i.resolved_at,i.original_estimate_seconds,i.time_spent_seconds,1.0 points from snapshots s join staging.stg_jira__issue i on cast(i.created_at as date) between s.start_date and coalesce(s.completed_at,s.ended_at,current_timestamp) limit 1000), agg as (select sprint_id,sprint_name,snapshot_date,day_number,planned_duration_days,sum(points) committed_points,sum(points) filter(where cast(resolved_at as date)<=snapshot_date) completed,sum(points) filter(where resolved_at is null or cast(resolved_at as date)>snapshot_date) remaining,count(*) total_issues,count(*) filter(where cast(resolved_at as date)<=snapshot_date) issues_completed,count(*) filter(where resolved_at is null or cast(resolved_at as date)>snapshot_date) issues_remaining,sum(coalesce(original_estimate_seconds,0))/3600.0 estimated,sum(case when cast(resolved_at as date)<=snapshot_date then coalesce(time_spent_seconds,0) else 0 end)/3600.0 spent_completed,sum(coalesce(time_spent_seconds,0))/3600.0 spent from issues group by all), w as (select *,lag(remaining) over(partition by sprint_id order by day_number) prev_remaining,lag(committed_points) over(partition by sprint_id order by day_number) prev_committed_points,lag(total_issues) over(partition by sprint_id order by day_number) prev_issues from agg), x as (select *,round(coalesce(completed/nullif(committed_points,0),0),3) completion_ratio,round(case when planned_duration_days>0 then day_number/planned_duration_days else 1 end,3) timeline_progress_ratio,case when planned_duration_days>0 then committed_points*(1-(day_number-1)/planned_duration_days) else committed_points end ideal from w) select sprint_id,sprint_name,snapshot_date,day_number,planned_duration_days,committed_points::decimal(38,3) total_story_points_committed,coalesce(completed,0)::decimal(38,3) story_points_completed,coalesce(remaining,0)::decimal(38,3) story_points_remaining,total_issues total_issues_committed,issues_completed,issues_remaining,estimated total_estimated_hours,spent_completed hours_spent_completed,spent total_hours_spent,ideal ideal_story_points_remaining,(prev_remaining-remaining)::decimal(38,3) daily_velocity,completion_ratio,timeline_progress_ratio,(committed_points-prev_committed_points)::decimal(38,3) scope_change_points,(total_issues-prev_issues)::bigint scope_change_issues,remaining-ideal burndown_variance,completion_ratio/nullif(timeline_progress_ratio,0) performance_index,null::double velocity_trend_3d,null::double predicted_completion_day,case when completion_ratio<timeline_progress_ratio-0.2 then 'Behind Schedule' when completion_ratio>timeline_progress_ratio+0.1 then 'Ahead of Schedule' when abs(coalesce(committed_points-prev_committed_points,0))>committed_points*0.1 then 'Scope Creep' else 'On Track' end sprint_risk_status,100::integer sprint_health_score,case when coalesce(prev_remaining-remaining,0)>5 then 'High Velocity' when coalesce(prev_remaining-remaining,0)>2 then 'Good Velocity' when coalesce(prev_remaining-remaining,0)>0 then 'Low Velocity' when coalesce(prev_remaining-remaining,0)=0 then 'No Progress' else 'Negative Velocity' end velocity_category,case when timeline_progress_ratio<=0.3 then 'Early Phase' when timeline_progress_ratio<=0.6 then 'Mid Phase' when timeline_progress_ratio<=0.9 then 'Late Phase' else 'Final Phase' end sprint_phase from x
```

## gold SQL（仅供定位差异）

S5

```sql
-- Advanced sprint performance analytics with velocity trending and capacity planning
-- Comprehensive sprint metrics including burndown analysis and predictive indicators

with sprint_base as (
    select 
        s.sprint_id as sprint_id,
        s.sprint_name as sprint_name,
        s.board_id,
        s.started_at::date as start_date,
        s.ended_at::date as end_date,
        s.completed_at::date as complete_date,
        
        -- Sprint duration calculations
        case 
            when s.started_at is not null and s.ended_at is not null then
                extract('epoch' from (s.ended_at::timestamp - s.started_at::timestamp)) / 86400.0
            else null
        end as planned_duration_days,
        
        case 
            when s.started_at is not null and s.completed_at is not null then
                extract('epoch' from (s.completed_at::timestamp - s.started_at::timestamp)) / 86400.0
            else null
        end as actual_duration_days
    from staging.stg_jira__sprint s
    where s.started_at is not null
),

sprint_issues as (
    -- Simplified version without issue_sprint_history table
    -- Using project-sprint relationship as proxy
    select 
        i.issue_id,
        s.sprint_id,
        i.issue_key as issue_key,
        i.issue_type_id,
        i.priority_id,
        i.project_id,
        i.created_at as issue_created_at,
        i.resolved_at as issue_resolved_at,
        
        -- Extract story points from issue (assuming it's in a field)
        coalesce(
            (select
                case
                    when fh.field_value ~ '^[0-9]+\.?[0-9]*$' then fh.field_value::numeric
                    when fh.field_value ~ '^.*([0-9]+\.?[0-9]*).*$' then
                        regexp_extract(fh.field_value, '([0-9]+\.?[0-9]*)', 1)::numeric
                    else null
                end
             from staging.stg_jira__issue_field_history fh
             join staging.stg_jira__field f on fh.field_id = f.field_id
             where fh.issue_id = i.issue_id
               and f.field_name ilike '%story%point%'
               and fh.is_active = true
             order by fh.updated_at desc
             limit 1),
            1  -- Default story point value
        ) as story_points,
        
        -- Time spent calculation
        coalesce(i.time_spent_seconds, 0) as time_spent_seconds,
        coalesce(i.original_estimate_seconds, 0) as original_estimate_seconds
    from staging.stg_jira__issue i
    cross join staging.stg_jira__sprint s  -- Simple cross join as proxy
    where i.created_at between s.started_at and coalesce(s.completed_at, s.ended_at, current_timestamp)
    limit 1000  -- Limit to prevent cartesian explosion
),

sprint_daily_snapshots as (
    -- Simplified approach without generate_series to avoid DuckDB compatibility issues
    select 
        sb.sprint_id,
        sb.sprint_name,
        sb.start_date,
        sb.end_date,
        sb.complete_date,
        sb.planned_duration_days,
        
        -- Use start date as representative snapshot date
        sb.start_date as snapshot_date,
        1 as day_number
    from sprint_base sb
    
    union all
    
    select 
        sb.sprint_id,
        sb.sprint_name,
        sb.start_date,
        sb.end_date,
        sb.complete_date,
        sb.planned_duration_days,
        
        -- Add mid-point and end date snapshots
        coalesce(sb.complete_date, sb.end_date, current_date) as snapshot_date,
        coalesce(sb.planned_duration_days, 1) as day_number
    from sprint_base sb
    where sb.planned_duration_days > 1
),

daily_sprint_metrics as (
    select 
        sds.sprint_id,
        sds.sprint_name,
        sds.snapshot_date,
        sds.day_number,
        sds.planned_duration_days,
        
        -- Story points metrics
        sum(si.story_points) as total_story_points_committed,
        sum(case when si.issue_resolved_at::date <= sds.snapshot_date then si.story_points else 0 end) as story_points_completed,
        sum(case when si.issue_resolved_at is null or si.issue_resolved_at::date > sds.snapshot_date then si.story_points else 0 end) as story_points_remaining,
        
        -- Issue count metrics  
        count(si.issue_id) as total_issues_committed,
        count(case when si.issue_resolved_at::date <= sds.snapshot_date then 1 end) as issues_completed,
        count(case when si.issue_resolved_at is null or si.issue_resolved_at::date > sds.snapshot_date then 1 end) as issues_remaining,
        
        -- Time tracking metrics
        sum(si.original_estimate_seconds) / 3600.0 as total_estimated_hours,
        sum(case when si.issue_resolved_at::date <= sds.snapshot_date then si.time_spent_seconds else 0 end) / 3600.0 as hours_spent_completed,
        sum(si.time_spent_seconds) / 3600.0 as total_hours_spent
    from sprint_daily_snapshots sds
    join sprint_issues si on sds.sprint_id = si.sprint_id
    group by 1,2,3,4,5
),

sprint_burndown_analysis as (
    select 
        dsm.*,
        
        -- Ideal burndown line
        case 
            when planned_duration_days > 0 then
                total_story_points_committed * (1 - (day_number - 1) / planned_duration_days)
            else total_story_points_committed
        end as ideal_story_points_remaining,
        
        -- Burndown velocity
        lag(story_points_remaining) over (partition by sprint_id order by day_number) - story_points_remaining as daily_velocity,
        
        -- Progress ratios
        case 
            when total_story_points_committed > 0 then
                round(story_points_completed::numeric / total_story_points_committed::numeric, 3)
            else 0
        end as completion_ratio,
        
        case 
            when planned_duration_days > 0 then
                round(day_number / planned_duration_days, 3)
            else 1
        end as timeline_progress_ratio,
        
        -- Scope change detection
        total_story_points_committed - lag(total_story_points_committed) over (partition by sprint_id order by day_number) as scope_change_points,
        total_issues_committed - lag(total_issues_committed) over (partition by sprint_id order by day_number) as scope_change_issues
    from daily_sprint_metrics dsm
),

sprint_performance_indicators as (
    select 
        sba.*,
        
        -- Performance indicators
        story_points_remaining - ideal_story_points_remaining as burndown_variance,
        
        case 
            when timeline_progress_ratio > 0 then
                completion_ratio / timeline_progress_ratio
            else null
        end as performance_index,
        
        -- Trend analysis using 3-day moving average
        avg(daily_velocity) over (
            partition by sprint_id 
            order by day_number 
            rows between 2 preceding and current row
        ) as velocity_trend_3d,
        
        -- Predictive completion
        case 
            when daily_velocity > 0 and story_points_remaining > 0 then
                day_number + (story_points_remaining / daily_velocity)
            else null
        end as predicted_completion_day,
        
        -- Risk indicators
        case 
            when completion_ratio < timeline_progress_ratio - 0.2 then 'Behind Schedule'
            when completion_ratio > timeline_progress_ratio + 0.1 then 'Ahead of Schedule'
            when abs(scope_change_points) > total_story_points_committed * 0.1 then 'Scope Creep'
            else 'On Track'
        end as sprint_risk_status
    from sprint_burndown_analysis sba
),

final_sprint_analytics as (
    select 
        spi.*,
        
        -- Sprint health score (0-100)
        least(100, greatest(0,
            100 
            - (case when sprint_risk_status = 'Behind Schedule' then 30 else 0 end)
            - (case when sprint_risk_status = 'Scope Creep' then 20 else 0 end)
            - (case when abs(burndown_variance) > total_story_points_committed * 0.3 then 25 else 0 end)
            + (case when sprint_risk_status = 'Ahead of Schedule' then 10 else 0 end)
            + (case when performance_index > 1.1 then 15 else 0 end)
        )) as sprint_health_score,
        
        -- Velocity classification
        case 
            when velocity_trend_3d > 5 then 'High Velocity'
            when velocity_trend_3d > 2 then 'Good Velocity'
            when velocity_trend_3d > 0 then 'Low Velocity'
            when velocity_trend_3d = 0 then 'No Progress'
            else 'Negative Velocity'
        end as velocity_category,
        
        -- Sprint phase classification
        case 
            when timeline_progress_ratio <= 0.3 then 'Early Phase'
            when timeline_progress_ratio <= 0.6 then 'Mid Phase'
            when timeline_progress_ratio <= 0.9 then 'Late Phase'
            else 'Final Phase'
        end as sprint_phase
    from sprint_performance_indicators spi
)

select * from final_sprint_analytics
order by sprint_id, day_number
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 65 | 138 | 31 | 91 | 1 | 14 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"sprint_id":"spr42801988712","performance_index":"0.0"}</code> |
| K2 | <code>{"sprint_id":"spr12927558116","performance_index":"0.0"}</code> |
| K3 | <code>{"sprint_id":"spr13366279730","performance_index":"0.0"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| sprint_id | 0 | 0 | 1 | VARCHAR | VARCHAR |
| sprint_name | 0 | 0 | 1 | VARCHAR | VARCHAR |
| snapshot_date | 0 | 0 | 1 | DATE | DATE |
| day_number | 0 | 0 | 1 | DOUBLE | DOUBLE |
| total_story_points_committed | 32 | 32 | 33 | DECIMAL(38,3) | DECIMAL(38,3) |
| story_points_completed | 0 | 0 | 1 | DECIMAL(38,3) | DECIMAL(38,3) |
| story_points_remaining | 32 | 32 | 33 | DECIMAL(38,3) | DECIMAL(38,3) |
| total_issues_committed | 25 | 25 | 26 | BIGINT | BIGINT |
| issues_completed | 0 | 0 | 1 | BIGINT | BIGINT |
| issues_remaining | 25 | 25 | 26 | BIGINT | BIGINT |
| daily_velocity | 0 | 0 | 1 | DECIMAL(38,3) | DECIMAL(38,3) |
| timeline_progress_ratio | 0 | 0 | 1 | DOUBLE | DOUBLE |
| scope_change_points | 0 | 0 | 1 | DECIMAL(38,3) | DECIMAL(38,3) |
| scope_change_issues | 0 | 0 | 1 | BIGINT | BIGINT |
| burndown_variance | 1 | 1 | 2 | DOUBLE | DOUBLE |
| velocity_trend_3d | 2 | 2 | 3 | DOUBLE | DOUBLE |
| sprint_risk_status | 0 | 0 | 1 | VARCHAR | VARCHAR |
| sprint_health_score | 2 | 2 | 3 | INTEGER | INTEGER |
| velocity_category | 31 | 31 | 32 | VARCHAR | VARCHAR |
| sprint_phase | 0 | 0 | 1 | VARCHAR | VARCHAR |

sprint_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"SPR42801988712","rows":1}]</code> | <code>[{"value":"SPR42801988712","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

sprint_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Sprint 186","rows":1}]</code> | <code>[{"value":"Sprint 186","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

snapshot_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"2024-10-21","rows":1}]</code> | <code>[{"value":"2024-10-21","rows":1},{"value":"2024-11-04","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

day_number 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"1.0","rows":1}]</code> | <code>[{"value":"1.0","rows":1},{"value":"14.0","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

total_story_points_committed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":"12.000","rows":2}]</code> | <code>[{"value":"1161.000","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

story_points_completed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0.000","rows":1}]</code> | <code>[{"value":"0.000","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

story_points_remaining 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":"12.000","rows":2}]</code> | <code>[{"value":"1161.000","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

total_issues_committed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | 3 | 2 |

issues_completed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":1}]</code> | <code>[{"value":"0","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

issues_remaining 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | 3 | 2 |

daily_velocity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":1},{"value":"0.000","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

timeline_progress_ratio 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0.071","rows":1}]</code> | <code>[{"value":"0.071","rows":1},{"value":"1.0","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

scope_change_points 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":1},{"value":"0.000","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

scope_change_issues 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":1},{"value":"0","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

burndown_variance 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":"0.0","rows":1},{"value":"11.142857142857142","rows":1}]</code> | <code>[{"value":"0.0","rows":1},{"value":"1078.0714285714287","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

velocity_trend_3d 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":null,"rows":2}]</code> | <code>[{"value":null,"rows":1},{"value":"0.0","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

sprint_risk_status 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"On Track","rows":1}]</code> | <code>[{"value":"Behind Schedule","rows":1},{"value":"On Track","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

sprint_health_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":"100","rows":2}]</code> | <code>[{"value":"100","rows":1},{"value":"45","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

velocity_category 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":"No Progress","rows":2}]</code> | <code>[{"value":"Negative Velocity","rows":1},{"value":"No Progress","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

sprint_phase 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Early Phase","rows":1}]</code> | <code>[{"value":"Early Phase","rows":1},{"value":"Final Phase","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"sprint_id":"SPR13366279730","performance_index":"0.667"}]</code> | <code>[{"sprint_id":"2","performance_index":"0.0"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"velocity_trend_3d","table_rows":65}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"planned_duration_days","value":"14.0"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["completion_ratio","performance_index"],"nonnull_equal_rows":65,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["completion_ratio","performance_index"],"nonnull_equal_rows":65,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>2输出列；[{"column":"velocity_trend_3d","expression":["CAST(NULL AS DOUBLE)"]}]</code> |
| B6_constant_literal_output | <code>2输出列；[{"column":"day_number","expression":["1.0"]}]</code> |
| B7_specified_not_read | <code>["staging.stg_jira__field"]</code> |
| C9_agent_runtime_text | <code>S4:1 current_date；命中数=2</code> |
| C9_gold_runtime_text | <code>S5:66 current_timestamp；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:1273 current_timestamp；命中数=3</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'int_jira__sprint_performance_analytics':"with s as (select *,cast(started_at as date) start_date,cast(ended_at as date) end_date,cast(completed_at as date) complete_date,epoch(ended_at-started_at)/86400.0 planned_duration_days from staging.stg_jira__sprint where started_at is not null), snapshots as (select *,start_date snapshot_date,1.0 day_number from s union all select *,coalesce(complete_date,end_date,current_date) snapshot_date,planned_duration_days day_number from s where planned_duration_days&gt;1), issues as (select s.sprint_id,s.sprint_name,s.snapshot_date,s.day_number,s.planned_duration_days,i.issue_id,i.resolved_at,i.original_estimate_seconds,i.time_spent_seconds,1.0 points from snapshots s join staging.stg_jira__issue i on cast(i.created_at as date) between s.start_date and coalesce(s.completed_at,s.ended_at,current_timestamp) limit 1000), agg as (select sprint_id,sprint_name,snapshot_date,day_number,planned_duration_days,sum(points) committed,sum(points) filter(where cast(resolved_at as date)&lt;=snapshot_date) completed,sum(points) filter(where resolved_at is null or cast(resolved_at as date)&gt;snapshot_date) remaining,count(*) total_issues,count(*) filter(where cast(resolved_at as date)&lt;=snapshot_date) issues_completed,count(*) filter(where resolved_at is null or cast(resolved_at as date)&gt;snapshot_date) issues_remaining,sum(coalesce(original_estimate_seconds,0))/3600.0 estimated,sum(case when cast(resolved_at as date)&lt;=snapshot_date then coalesce(time_spent_seconds,0) else 0 end)/3600.0 spent_completed,sum(coalesce(time_spent_seconds,0))/3600.0 spent from issues group by all), w as (select *,lag(remaining) over(partition by sprint_id order by day_number) prev_remaining,lag(committed) over(partition by sprint_id order by day_number) prev_committed,lag(total_issues) over(partition by sprint_id order by day_number) prev_issues from agg), x as (select *,round(coalesce(completed/nullif(committed,0),0),3) completion_ratio,round(case when planned_duration_days&gt;0 then day_number/planned_duration_days else 1 end,3) timeline_progress_ratio,case when planned_duration_days&gt;0 then committed*(1-(day_number-1)/planned_duration_days) else committed end ideal from w) select sprint_id,sprint_name,snapshot_date,day_number,planned_duration_days,committed::decimal(38,3) total_story_points_committed,coalesce(completed,0)::decimal(38,3) story_points_completed,coalesce(remaining,0)::decimal(38,3) story_points_remaining,total_issues total_issues_committed,issues_completed,issues_remaining,estimated total_estimated_hours,spent_completed hours_spent_completed,spent total_hours_spent,ideal ideal_story_points_remaining,(prev_remaining-remaining)::decimal(38,3) daily_velocity,completion_ratio,timeline_progress_ratio,(committed-prev_committed)::decimal(38,3) scope_change_points,(total_issues-prev_issues)::bigint scope_change_issues,remaining-ideal burndown_variance,completion_ratio/nullif(timeline_progress_ratio,0) performance_index,null::double velocity_trend_3d,null::double predicted_completion_day,case when completion_ratio&lt;timeline_progress_ratio-0.2 then 'Behind Schedule' when completion_ratio&gt;timeline_progress_ratio+0.1 then 'Ahead of Schedule' when abs(coalesce(committed-prev_committed,0))&gt;committed*0.1 then 'Scope Creep' else 'On Track' end sprint_risk_status,100::integer sprint_health_score,case when coalesce(prev_remaining-remaining,0)&gt;5 then 'High Velocity' when coalesce(prev_remaining-remaining,0)&gt;2 then 'Good Velocity' when coalesce(prev_remaining-remaining,0)&gt;0 then 'Low Velocity' when coalesce(prev_remaining-remaining,0)=0 then 'No Progress' else 'Negative Velocity' end velocity_category,case when timeline_progress_ratio&lt;=0.3 then 'Early Phase' when timeline_progress_ratio&lt;=0.6 then 'Mid Phase' when timeline_progress_ratio&lt;=0.9 then 'Late Phase' else 'Final Phase' end sprint_phase from x",</code> |

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
| 21 | run | <code>cat &gt;&gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>Q.update({<br>'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i</code> | 6630 | false | false |
| 23 | run | <code>grep -E 'WARNING -  ⏭&#124;WARNING -   ⏭&#124;Catalog Error&#124;Binder Error&#124;Parser Error&#124;Conversion Error' /tmp/runlog &#124; head -80</code> | 8767 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_jira__issue_type.sql';s=open(p).read().replace('is_subtask from','subtask as is_subtask from');open(p,'w').write(s)<br>p='sql/intermediate/int_jira__issue_versions.sql'</code> | 995 | false | false |
| 27 | run | <code>grep -oE '.{0,25}committed.{0,25}' sql/intermediate/int_jira__sprint_performance_analytics.sql &#124; head; python - &lt;&lt;'PY'<br>p='sql/intermediate/int_jira__user_activity_metrics.sql'<br>s=open(p).read(); start=</code> | 613 | false | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> s=re.sub(r'try_cast\((\w+) as timestamp\)',r"try_cast(regexp_replace(\1, '([+-][0-9]{2}</code> | 9550 | true | false |
| 33 | run | <code>cat sql/staging/stg_jira__issue_type.sql; grep -o '.\{0,30\}prev_committed.\{0,30\}' sql/intermediate/int_jira__sprint_performance_analytics.sql; cat sql/staging/stg_jira__issue.sql &#124; head -c 800</code> | 1230 | false | false |
| 35 | run | <code>sed -i 's/description,is_subtask subtask as is_subtask/description,subtask as is_subtask/' sql/staging/stg_jira__issue_type.sql; sed -i 's/committed_points-prev_committed)/committed_points-prev_commit</code> | 53 | false | false |
| 41 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; grep -E 'INTERMEDIATE Layer&#124;✓ intermediate.int_jira__issue_join&#124;✓ intermediate.int_jira__issue_users&#124;staging.stg_jira__issue:' /tmp/runlog3</code> | 836 | false | false |
| 43 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; cat sql/intermediate/int_jira__issue_calendar_spine.sql</code> | 1202 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('jira.duckdb',read_only=True)<br>checks=[('staging.stg_jira__issue','issue_id'),('staging.stg_jira__project','project_id'),('intermediate.int_jira__issue_jo</code> | 422 | false | false |
| 49 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 顺序实现并写入 `sql/staging/`、`sql/intermediate/` 和 `sql/marts/`，共 49 个 SQL 文件。所有模型均使用 DuckDB SQL、直接使用 `s</code> | 117 | false | false |

### agent action 的 thought/message 命中原句

event 15 / message

```text
'int_jira__sprint_performance_analytics':"with s as (select *,cast(started_at as date) start_date,cast(ended_at as date) end_date,cast(completed_at as date) complete_date,epoch(ended_at-started_at)/86400.0 planned_duration_days from staging.stg_jira__sprint where started_at is not null), snapshots as (select *,start_date snapshot_date,1.0 day_number from s union all select *,coalesce(complete_date,end_date,current_date) snapshot_date,planned_duration_days day_number from s where planned_duration_days>1), issues as (select s.sprint_id,s.sprint_name,s.snapshot_date,s.day_number,s.planned_duration_days,i.issue_id,i.resolved_at,i.original_estimate_seconds,i.time_spent_seconds,1.0 points from snapshots s join staging.stg_jira__issue i on cast(i.created_at as date) between s.start_date and coalesce(s.completed_at,s.ended_at,current_timestamp) limit 1000), agg as (select sprint_id,sprint_name,snapshot_date,day_number,planned_duration_days,sum(points) committed,sum(points) filter(where cast(resolved_at as date)<=snapshot_date) completed,sum(points) filter(where resolved_at is null or cast(resolved_at as date)>snapshot_date) remaining,count(*) total_issues,count(*) filter(where cast(resolved_at as date)<=snapshot_date) issues_completed,count(*) filter(where resolved_at is null or cast(resolved_at as date)>snapshot_date) issues_remaining,sum(coalesce(original_estimate_seconds,0))/3600.0 estimated,sum(case when cast(resolved_at as date)<=snapshot_date then coalesce(time_spent_seconds,0) else 0 end)/3600.0 spent_completed,sum(coalesce(time_spent_seconds,0))/3600.0 spent from issues group by all), w as (select *,lag(remaining) over(partition by sprint_id order by day_number) prev_remaining,lag(committed) over(partition by sprint_id order by day_number) prev_committed,lag(total_issues) over(partition by sprint_id order by day_number) prev_issues from agg), x as (select *,round(coalesce(completed/nullif(committed,0),0),3) completion_ratio,round(case when planned_duration_days>0 then day_number/planned_duration_days else 1 end,3) timeline_progress_ratio,case when planned_duration_days>0 then committed*(1-(day_number-1)/planned_duration_days) else committed end ideal from w) select sprint_id,sprint_name,snapshot_date,day_number,planned_duration_days,committed::decimal(38,3) total_story_points_committed,coalesce(completed,0)::decimal(38,3) story_points_completed,coalesce(remaining,0)::decimal(38,3) story_points_remaining,total_issues total_issues_committed,issues_completed,issues_remaining,estimated total_estimated_hours,spent_completed hours_spent_completed,spent total_hours_spent,ideal ideal_story_points_remaining,(prev_remaining-remaining)::decimal(38,3) daily_velocity,completion_ratio,timeline_progress_ratio,(committed-prev_committed)::decimal(38,3) scope_change_points,(total_issues-prev_issues)::bigint scope_change_issues,remaining-ideal burndown_variance,completion_ratio/nullif(timeline_progress_ratio,0) performance_index,null::double velocity_trend_3d,null::double predicted_completion_day,case when completion_ratio<timeline_progress_ratio-0.2 then 'Behind Schedule' when completion_ratio>timeline_progress_ratio+0.1 then 'Ahead of Schedule' when abs(coalesce(committed-prev_committed,0))>committed*0.1 then 'Scope Creep' else 'On Track' end sprint_risk_status,100::integer sprint_health_score,case when coalesce(prev_remaining-remaining,0)>5 then 'High Velocity' when coalesce(prev_remaining-remaining,0)>2 then 'Good Velocity' when coalesce(prev_remaining-remaining,0)>0 then 'Low Velocity' when coalesce(prev_remaining-remaining,0)=0 then 'No Progress' else 'Negative Velocity' end velocity_category,case when timeline_progress_ratio<=0.3 then 'Early Phase' when timeline_progress_ratio<=0.6 then 'Mid Phase' when timeline_progress_ratio<=0.9 then 'Late Phase' else 'Final Phase' end sprint_phase from x",
```
event 25 / message

```text
p='sql/intermediate/int_jira__sprint_performance_analytics.sql';s=open(p).read().replace(' committed',' committed_points').replace('committed)', 'committed_points)').replace('committed,','committed_points,').replace('committed ', 'committed_points ').replace('committed/', 'committed_points/').replace('committed*','committed_points*').replace('committed::','committed_points::').replace('committed-prev','committed_points-prev').replace('committed>','committed_points>');open(p,'w').write(s)
```
event 25 / message

```text
cat sql/intermediate/int_jira__issue_versions.sql; head -c 300 sql/intermediate/int_jira__sprint_performance_analytics.sql
```
event 27 / message

```text
Running command: grep -oE '.{0,25}committed.{0,25}' sql/intermediate/int_jira__sprint_performance_analytics.sql | head; python - <<'PY'
```
event 31 / message

```text
p=Path('sql/intermediate/int_jira__sprint_performance_analytics.sql');s=p.read_text().replace('total_story_points_committed_points','total_story_points_committed').replace('total_issues_committed_points','total_issues_committed').replace('committed_points-prev_committed_points','committed_points-prev_committed').replace('committed_points::decimal','committed_points::decimal').replace('lag(committed_points) over','lag(committed_points) over')
```
event 33 / message

```text
Running command: cat sql/staging/stg_jira__issue_type.sql; grep -o '.\{0,30\}prev_committed.\{0,30\}' sql/intermediate/int_jira__sprint_performance_analytics.sql; cat sql/staging/stg_jira__issue.sql | head -c 800
```
event 35 / message

```text
Running command: sed -i 's/description,is_subtask subtask as is_subtask/description,subtask as is_subtask/' sql/staging/stg_jira__issue_type.sql; sed -i 's/committed_points-prev_committed)/committed_points-prev_committed_points)/g;s/committed_points-prev_committed,/committed_points-prev_committed_points,/g' sql/intermediate/int_jira__sprint_performance_analytics.sql; python - <<'PY'
```
event 49 / message

```text
- 有些分析模型在当前实现中是可运行的基础版本，尚未完整覆盖合同里很长的所有计算细节：尤其 `int_jira__project_health_scoring` 的多项趋势、评论、链接、工作量指标，`int_jira__sprint_performance_analytics` 的部分故事点提取、趋势与健康评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细交互、分数及分类逻辑。
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-011.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql`
- S6: `records/006_contract_impl-011.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/result.md`
- S10: `data/021_packages_work/021_impl-011_int_jira__sprint_performance_analytics/021_impl-011_int_jira__sprint_performance_analytics.json`
- S11: `data/005_cs_work/impl-011_retry_02/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/jira.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions`
