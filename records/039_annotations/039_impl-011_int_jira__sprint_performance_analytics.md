# impl-011_int_jira__sprint_performance_analytics（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**已说出的降级**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 168, "cell_scale": 2947}, "L1": {"row_scale": 168, "cell_scale": 2947}, "L2": {"row_scale": 168, "cell_scale": 2947}, "L3": {"row_scale": 168, "cell_scale": 2947}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| story_points_mapping | 已说出的降级 | 主要 | 19 | 703 | 1 |
| velocity_trend | 已说出的降级 | 参与 | 0 | 2 | 1 |
| health_score | 已说出的降级 | 参与 | 0 | 2 | 1 |
| timestamp_window | Intent Misreading | 参与 | 2 | 236 | 4 |
| velocity_null_default | Intent Misreading | 参与 | 1 | 33 | 4 |
| limit_before_snapshots | Intent Misreading | 非原因 | -29 | 44 | 4 |

### 契约原句（所有点共用，逐字回查event1）

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

### 逐点结论

#### story_points_mapping

主要；**已说出的降级**；把握高。

用常量1代替现有字段历史中的story points；没有做候选映射判断。 finish点名sprint performance analytics的趋势/评分简化，对应本处。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 168 | 149 | 2947 | 2244 |
| L1 | 168 | 149 | 2947 | 2244 |
| L2 | 168 | 149 | 2947 | 2244 |
| L3 | 168 | 149 | 2947 | 2244 |

重跑：`records/021_extra_reruns_impl-011_int_jira__sprint_performance_analytics.json` / `story_points_mapping`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql` / `SQL.text`（sql）：

```text
1.0 points
```

#### velocity_trend

参与；**已说出的降级**；把握高。

velocity_trend_3d固定NULL，省略契约要求的三快照移动平均。 finish点名sprint performance analytics的趋势/评分简化，对应本处。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 168 | 168 | 2947 | 2945 |
| L1 | 168 | 168 | 2947 | 2945 |
| L2 | 168 | 168 | 2947 | 2945 |
| L3 | 168 | 168 | 2947 | 2945 |

重跑：`records/021_detailed_reruns_impl-011_int_jira__sprint_performance_analytics.json` / `velocity_trend`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql` / `SQL.text`（sql）：

```text
null::double velocity_trend_3d
```

#### health_score

参与；**已说出的降级**；把握高。

固定健康分，省略实际指标计算。 finish点名sprint performance analytics的趋势/评分简化，对应本处。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 168 | 168 | 2947 | 2945 |
| L1 | 168 | 168 | 2947 | 2945 |
| L2 | 168 | 168 | 2947 | 2945 |
| L3 | 168 | 168 | 2947 | 2945 |

重跑：`records/021_extra_reruns_impl-011_int_jira__sprint_performance_analytics.json` / `health_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql` / `SQL.text`（sql）：

```text
100::integer sprint_health_score
```

#### timestamp_window

参与；**Intent Misreading**；把握高。

P：sprint边界可以截为DATE。契约用时间戳限定承诺/完成窗口，截日会改变同日窗口内外。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 168 | 166 | 2947 | 2711 |
| L1 | 168 | 166 | 2947 | 2711 |
| L2 | 168 | 166 | 2947 | 2711 |
| L3 | 168 | 166 | 2947 | 2711 |

重跑：`records/021_extra_reruns_impl-011_int_jira__sprint_performance_analytics.json` / `timestamp_window`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql` / `SQL.text`（sql）：

```text
cast(i.created_at as date) between s.start_date
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### velocity_null_default

参与；**Intent Misreading**；把握高。

P：没有速度基线可先COALESCE为0再分档。契约CASE明确NULL落ELSE Negative Velocity；不是任意缺失政策或纯标签呈现。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 168 | 167 | 2947 | 2914 |
| L1 | 168 | 167 | 2947 | 2914 |
| L2 | 168 | 167 | 2947 | 2914 |
| L3 | 168 | 167 | 2947 | 2914 |

重跑：`records/021_detailed_reruns_impl-011_int_jira__sprint_performance_analytics.json` / `velocity_null_default`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql` / `SQL.text`（sql）：

```text
case when coalesce(prev_remaining-remaining,0)>5 then 'High Velocity' when coalesce(prev_remaining-remaining,0)>2 then 'Good Velocity' when coalesce(prev_remaining-remaining,0)>0 then 'Low Velocity' when coalesce(prev_remaining-remaining,0)=0 then 'No Progress' else 'Negative Velocity' end
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### limit_before_snapshots

非原因；**Intent Misreading**；把握高。

P：LIMIT可在快照展开后作用于最终结果。契约先限制sprint再展开快照；修复改变行范围，行规模变坏，不记参与。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 168 | 197 | 2947 | 2903 |
| L1 | 168 | 197 | 2947 | 2903 |
| L2 | 168 | 197 | 2947 | 2903 |
| L3 | 168 | 197 | 2947 | 2903 |

重跑：`records/021_detailed_reruns_impl-011_int_jira__sprint_performance_analytics.json` / `limit_before_snapshots`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

标记：存在未确立的前提，但不是判错原因。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql` / `SQL.text`（sql）：

```text
with s as (select *,cast(started_at as date) start_date,cast(ended_at as date) end_date,cast(completed_at as date) complete_date,epoch(ended_at-started_at)/86400.0 planned_duration_days from staging.stg_jira__sprint where started_at is not null), snapshots as (select *,start_date snapshot_date,1.0 day_number from s union all select *,coalesce(complete_date,end_date,current_date) snapshot_date,planned_duration_days day_number from s where planned_duration_days>1), issues as (select s.sprint_id,s.sprint_name,s.snapshot_date,s.day_number,s.planned_duration_days,i.issue_id,i.resolved_at,i.original_estimate_seconds,i.time_spent_seconds,1.0 points from snapshots s join staging.stg_jira__issue i on cast(i.created_at as date) between s.start_date and coalesce(s.completed_at,s.ended_at,current_timestamp) limit 1000), agg as (select sprint_id,sprint_name,snapshot_date,day_number,planned_duration_days,sum(points) committed_points,sum(points) filter(where cast(resolved_at as date)<=snapshot_date) completed,sum(points) filter(where resolved_at is null or cast(resolved_at as date)>snapshot_date) remaining,count(*) total_issues,count(*) filter(where cast(resolved_at as date)<=snapshot_date) issues_completed,count(*) filter(where resolved_at is null or cast(resolved_at as date)>snapshot_date) issues_remaining,sum(coalesce(original_estimate_seconds,0))/3600.0 estimated,sum(case when cast(resolved_at as date)<=snapshot_date then coalesce(time_spent_seconds,0) else 0 end)/3600.0 spent_completed,sum(coalesce(time_spent_seconds,0))/3600.0 spent from issues group by all), w as (select *,lag(remaining) over(partition by sprint_id order by day_number) prev_remaining,lag(committed_points) over(partition by sprint_id order by day_number) prev_committed_points,lag(total_issues) over(partition by sprint_id order by day_number) prev_issues from agg), x as (select *,round(coalesce(completed/nullif(committed_points,0),0),3) completion_ratio,round(case when planned_duration_days>0 then day_number/planned_duration_days else 1 end,3) timeline_progress_ratio,case when planned_duration_days>0 then committed_points*(1-(day_number-1)/planned_duration_days) else committed_points end ideal from w) select sprint_id,sprint_name,snapshot_date,day_number,planned_duration_days,committed_points::decimal(38,3) total_story_points_committed,coalesce(completed,0)::decimal(38,3) story_points_completed,coalesce(remaining,0)::decimal(38,3) story_points_remaining,total_issues total_issues_committed,issues_completed,issues_remaining,estimated total_estimated_hours,spent_completed hours_spent_completed,spent total_hours_spent,ideal ideal_story_points_remaining,(prev_remaining-remaining)::decimal(38,3) daily_velocity,completion_ratio,timeline_progress_ratio,(committed_points-prev_committed_points)::decimal(38,3) scope_change_points,(total_issues-prev_issues)::bigint scope_change_issues,remaining-ideal burndown_variance,completion_ratio/nullif(timeline_progress_ratio,0) performance_index,null::double velocity_trend_3d,null::double predicted_completion_day,case when completion_ratio<timeline_progress_ratio-0.2 then 'Behind Schedule' when completion_ratio>timeline_progress_ratio+0.1 then 'Ahead of Schedule' when abs(coalesce(committed_points-prev_committed_points,0))>committed_points*0.1 then 'Scope Creep' else 'On Track' end sprint_risk_status,100::integer sprint_health_score,case when coalesce(prev_remaining-remaining,0)>5 then 'High Velocity' when coalesce(prev_remaining-remaining,0)>2 then 'Good Velocity' when coalesce(prev_remaining-remaining,0)>0 then 'Low Velocity' when coalesce(prev_remaining-remaining,0)=0 then 'No Progress' else 'Negative Velocity' end velocity_category,case when timeline_progress_ratio<=0.3 then 'Early Phase' when timeline_progress_ratio<=0.6 then 'Mid Phase' when timeline_progress_ratio<=0.9 then 'Late Phase' else 'Final Phase' end sprint_phase from x

```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`，行[1265, 1414]；材料包 `records/021_packages/021_impl-011_int_jira__sprint_performance_analytics.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql`；SHA-256 `221c358679c9d7256c3291fe27d0d6dcdbc63a8d8b8989afe4837dccde884525`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / event 55。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共3条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 25，失败=True。
  - `records/021_supplement_queries.json` / index 18，失败=False。
  - `records/021_final_diagnostics.json` / index 5，失败=False。

## 不确定或没查到的（含规则问题）

- remove_limit探针违反契约允许LIMIT，不是合法单点修复；有限集合任意取样的残差不硬归agent。limit_before_snapshots虽减少44格但行数增加，按用户行优先口径不列参与。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
