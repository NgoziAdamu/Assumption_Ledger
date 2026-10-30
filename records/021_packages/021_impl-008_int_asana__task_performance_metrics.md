# impl-008 | intermediate | int_asana__task_performance_metrics | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:688–774

```yaml
    - name: int_asana__task_performance_metrics
      description: Task performance metrics with lifecycle status, response/delay days, activity/urgency/complexity scores, validity flag, performance grade, and health score; only valid records are output.
      grain: One row per task_id (only records with is_valid_record = true)
      source_models:
      - staging.stg_asana__task
      - intermediate.int_asana__task_open_length
      - intermediate.int_asana__task_story
      business_logic: 'Data preparation: - Use tasks where created_at is present from staging.stg_asana__task. - Bring per-task durations from intermediate.int_asana__task_open_length (days_open, days_since_first_assignment, days_since_last_assignment). - Use stories from intermediate.int_asana__task_story where action_taken is present. Timeline and status: - For each task_id, left join open-length metrics. - Assign task_status_category using ordered rules: - unassigned: no assignee and not completed - assigned_active: has assignee and not completed - completed_on_time: completed_at on or before due_date - completed_late: completed_at after due_date - overdue: not completed and today is after the due_date’s calendar date - otherwise active - first_assigned_at: the earliest story timestamp where action_taken = ''assigned'' for this task; null if none. - last_activity_at: the later of modified_at and the latest story timestamp for the task; if no story exists, use created_at. Metrics: - response_time_days: number of days from created_at to first_assigned_at when first_assigned_at exists; otherwise null (expected non-negative). - delay_days: - If due_date exists and the task is completed late: days between due_date and completed_at. - If due_date exists and the task is still open and past due today: days between due_date and today. - Otherwise 0 (never negative). - activity_score (1–5) based on days since last_activity_at: - 0–1 days → 5; 2–3 → 4; 4–7 → 3; 8–14 → 2; else 1. - urgency_score (1–5) only when due_date exists and the task is not completed: - due in 0–1 days → 5; 2–3 → 4; 4–7 → 3; 8–30 → 2; else 1; otherwise 1. - complexity_score (1–3) from description length (treat missing description as empty): - >500 chars → 3; >100 → 2; else 1. Constraints and classifications: - is_valid_record is true only if task_name is not blank, created_at is present, days_open ≥ 0, response_time_days is not negative (null allowed), and delay_days ≥ 0. - performance_grade: - completed with delay_days = 0 and response_time_days ≤ 1 → excellent - completed with delay_days ≤ 2 and response_time_days ≤ 2 → good - completed with delay_days ≤ 5 → fair - completed with delay_days > 5 → poor - not completed and status is overdue → at_risk - otherwise pending. Health score: - Start from 0 and add components, then clamp to [0,100]: - Activity: add 20 points per activity_score unit (1–5). - Timeliness: add 25 if delay_days = 0; otherwise subtract 5 points per day of delay down to 0. - Responsiveness: add 25 if response_time_days ≤ 1; otherwise subtract 3 points per day down to 0. - Assignment: add 15 if an assignee is present; else 0. - Description: add 15 if description is present; else 0. Output: - Return rows with is_valid_record = true. - Sort by health_score (descending), then urgency_score (descending), then task_id.'
      columns:
      - name: task_id
        data_type: VARCHAR
        description: Unique task identifier; exactly one output row per task_id that passes validity checks
        tests:
        - not_null
        - unique
      - name: task_name
        data_type: VARCHAR
        description: Task display name/title sourced from stg_asana__task; must be non-null and non-blank
      - name: task_description
        data_type: VARCHAR
        description: Task description text from stg_asana__task; presence contributes to health_score
      - name: created_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Original task creation timestamp; non-null by filter and used in multiple day-based calculations
        tests:
        - not_null
      - name: modified_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Most recent task modification timestamp used to determine last_activity_at; may be null
      - name: completed_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Timestamp when the task was completed; used to label completed_on_time vs completed_late and to compute delay_days
      - name: due_date
        data_type: TIMESTAMP WITH TIME ZONE
        description: Target due timestamp used for status, urgency_score, and delay_days; overdue checks compare the due date’s calendar date to today
      - name: is_completed
        data_type: BOOLEAN
        description: Completion flag from stg_asana__task used in status, delay_days, urgency_score, and performance_grade
      - name: assignee_user_id
        data_type: BIGINT
        description: Assigned user id (nullable); presence affects status and adds +15 to health_score
      - name: task_status_category
        data_type: VARCHAR
        description: 'Lifecycle status from ordered rules: unassigned, assigned_active, completed_on_time, completed_late, overdue, or active'
      - name: first_assigned_at
        data_type: TIMESTAMP
        description: Earliest story timestamp where action_taken='assigned' for this task; null if never assigned
      - name: last_activity_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Later of modified_at and the latest story timestamp; if no story exists, uses created_at
      - name: days_open
        data_type: BIGINT
        description: Non-negative days the task has been open sourced from int_asana__task_open_length
      - name: days_since_first_assignment
        data_type: BIGINT
        description: Days since the first assignment sourced from int_asana__task_open_length
      - name: days_since_last_assignment
        data_type: BIGINT
        description: Days since the most recent assignment sourced from int_asana__task_open_length
      - name: response_time_days
        data_type: BIGINT
        description: Days from created_at to first_assigned_at; null if never assigned; must not be negative
      - name: delay_days
        data_type: BIGINT
        description: Days overdue (0 if due_date absent or on time); completed late uses days between due_date and completed_at; open overdue uses days between due_date and today
      - name: activity_score
        data_type: INTEGER
        description: 1–5 score based on days since last_activity_at vs now (≤1→5, ≤3→4, ≤7→3, ≤14→2, else 1)
      - name: urgency_score
        data_type: INTEGER
        description: 1–5 score when due_date present and not completed, based on days until due_date thresholds; otherwise 1
      - name: complexity_score
        data_type: INTEGER
        description: '1–3 score based on description length: >500→3, >100→2, else 1'
      - name: is_valid_record
        data_type: BOOLEAN
        description: True only if task_name not blank, created_at present, and days_open/response_time_days/delay_days are not negative
        tests:
        - accepted_values:
            values:
            - true
      - name: performance_grade
        data_type: VARCHAR
        description: 'Classification: excellent, good, fair, poor, at_risk, or pending per rules combining completion, delay_days, and response_time_days'
      - name: health_score
        data_type: BIGINT
        description: Overall 0–100 score from weighted components (activity, timeliness, responsiveness, assignment, description) clamped to [0,100]
```

## agent 最终 SQL

S4

```sql
WITH tasks AS (
 SELECT t.*, ol.days_open, ol.days_since_first_assignment, ol.days_since_last_assignment,
        a.first_assigned_at,
        COALESCE((SELECT MAX(s.created_at) FROM intermediate.int_asana__task_story s WHERE s.target_task_id=t.task_id), t.created_at) AS latest_story_at
 FROM staging.stg_asana__task t LEFT JOIN intermediate.int_asana__task_open_length ol ON t.task_id=ol.task_id
 LEFT JOIN (SELECT target_task_id, MIN(created_at) first_assigned_at FROM intermediate.int_asana__task_story WHERE action_taken='assigned' GROUP BY target_task_id) a ON t.task_id=a.target_task_id
 WHERE t.created_at IS NOT NULL
), calculated AS (
 SELECT *, CASE WHEN NOT is_completed AND assignee_user_id IS NULL THEN 'unassigned'
 WHEN NOT is_completed AND assignee_user_id IS NOT NULL THEN 'assigned_active'
 WHEN is_completed AND completed_at::DATE <= due_date::DATE THEN 'completed_on_time'
 WHEN is_completed AND completed_at::DATE > due_date::DATE THEN 'completed_late'
 WHEN NOT is_completed AND due_date::DATE < CURRENT_DATE THEN 'overdue' ELSE 'active' END AS task_status_category,
 CASE WHEN due_date IS NOT NULL AND is_completed AND completed_at::DATE > due_date::DATE THEN DATE_DIFF('day',due_date::DATE,completed_at::DATE)
      WHEN due_date IS NOT NULL AND NOT is_completed AND due_date::DATE < CURRENT_DATE THEN DATE_DIFF('day',due_date::DATE,CURRENT_DATE) ELSE 0 END::BIGINT AS delay_days,
 CASE WHEN first_assigned_at IS NOT NULL THEN DATE_DIFF('day',created_at,first_assigned_at) END::BIGINT AS response_time_days,
 CASE WHEN DATE_DIFF('day',latest_story_at,CURRENT_TIMESTAMP)<=1 THEN 5 WHEN DATE_DIFF('day',latest_story_at,CURRENT_TIMESTAMP)<=3 THEN 4 WHEN DATE_DIFF('day',latest_story_at,CURRENT_TIMESTAMP)<=7 THEN 3 WHEN DATE_DIFF('day',latest_story_at,CURRENT_TIMESTAMP)<=14 THEN 2 ELSE 1 END AS activity_score,
 CASE WHEN due_date IS NULL OR is_completed THEN 1 WHEN DATE_DIFF('day',CURRENT_DATE,due_date::DATE)<=1 THEN 5 WHEN DATE_DIFF('day',CURRENT_DATE,due_date::DATE)<=3 THEN 4 WHEN DATE_DIFF('day',CURRENT_DATE,due_date::DATE)<=7 THEN 3 WHEN DATE_DIFF('day',CURRENT_DATE,due_date::DATE)<=30 THEN 2 ELSE 1 END AS urgency_score,
 CASE WHEN LENGTH(COALESCE(task_description,''))>500 THEN 3 WHEN LENGTH(COALESCE(task_description,''))>100 THEN 2 ELSE 1 END AS complexity_score
 FROM tasks
), classified AS (
 SELECT *, (task_name IS NOT NULL AND LENGTH(TRIM(task_name))>0 AND days_open>=0 AND (response_time_days IS NULL OR response_time_days>=0) AND delay_days>=0) AS is_valid_record,
 CASE WHEN is_completed AND delay_days=0 AND response_time_days<=1 THEN 'excellent'
 WHEN is_completed AND delay_days<=2 AND response_time_days<=2 THEN 'good'
 WHEN is_completed AND delay_days<=5 THEN 'fair' WHEN is_completed AND delay_days>5 THEN 'poor'
 WHEN NOT is_completed AND task_status_category='overdue' THEN 'at_risk' ELSE 'pending' END AS performance_grade,
 GREATEST(0,LEAST(100,activity_score*20 + CASE WHEN delay_days=0 THEN 25 ELSE GREATEST(0,25-delay_days*5) END + CASE WHEN response_time_days<=1 THEN 25 WHEN response_time_days IS NULL THEN 0 ELSE GREATEST(0,25-response_time_days*3) END + CASE WHEN assignee_user_id IS NOT NULL THEN 15 ELSE 0 END + CASE WHEN COALESCE(task_description,'')<>'' THEN 15 ELSE 0 END))::BIGINT AS health_score
 FROM calculated
)
SELECT task_id,task_name,task_description,created_at,modified_at,completed_at,due_date,is_completed,assignee_user_id,task_status_category,first_assigned_at,latest_story_at AS last_activity_at,
 days_open,days_since_first_assignment,days_since_last_assignment,response_time_days,delay_days,activity_score,urgency_score,complexity_score,is_valid_record,performance_grade,health_score
FROM classified WHERE is_valid_record
```

## gold SQL（仅供定位差异）

S5

```sql
-- Task Performance Metrics Analysis
-- Analysis of task performance indicators, including core KPIs such as cycle time, response time, delay, etc.

with task_base as (
    select *
    from staging.stg_asana__task
    where created_at is not null  -- Data quality constraint: creation time cannot be empty
),

task_open_length as (
    select *
    from intermediate.int_asana__task_open_length
),

task_story as (
    select *
    from intermediate.int_asana__task_story
    where action_taken is not null  -- Constraint: Action type must have a value
),

-- Calculate critical time points for tasks
task_timeline as (
    select 
        t.task_id,
        t.task_name,
        t.task_description,
        t.created_at,
        t.modified_at,
        t.completed_at,
        t.due_date,
        t.is_completed,
        t.assignee_user_id,
        
        -- Task life cycle stage analysis
        case 
            when t.assignee_user_id is null and not t.is_completed then 'unassigned'
            when t.assignee_user_id is not null and not t.is_completed then 'assigned_active'
            when t.is_completed and t.completed_at <= t.due_date then 'completed_on_time'
            when t.is_completed and t.completed_at > t.due_date then 'completed_late'
            when not t.is_completed and current_date > date(t.due_date) then 'overdue'
            else 'active'
        end as task_status_category,
        
        -- First allocation time (obtained from story table)
        (select min(ts.created_at) 
         from task_story ts 
         where ts.target_task_id = t.task_id 
           and ts.action_taken = 'assigned') as first_assigned_at,
           
        -- last modified time
        greatest(
            t.modified_at,
            coalesce((select max(ts.created_at) from task_story ts where ts.target_task_id = t.task_id), t.created_at)
        ) as last_activity_at,
        
        tol.days_open,
        tol.days_since_first_assignment,
        tol.days_since_last_assignment
        
    from task_base t
    left join task_open_length tol on t.task_id = tol.task_id
),

-- 计算复杂的性能指标
performance_calculations as (
    select 
        *,
        
        -- 响应时间：从创建到首次分配的时间
        case 
            when first_assigned_at is not null then
                date_diff('day', created_at, first_assigned_at)
            else null
        end as response_time_days,
        
        -- Late days: the number of days beyond the deadline
        case 
            when due_date is not null and is_completed and completed_at > due_date then
                date_diff('day', due_date, completed_at)
            when due_date is not null and not is_completed and current_date > date(due_date) then
                date_diff('day', due_date, current_date)
            else 0
        end as delay_days,
        
        -- Activity score: based on last activity time
        case 
            when date_diff('day', last_activity_at, current_timestamp) <= 1 then 5  -- very active
            when date_diff('day', last_activity_at, current_timestamp) <= 3 then 4  -- active
            when date_diff('day', last_activity_at, current_timestamp) <= 7 then 3  -- generally
            when date_diff('day', last_activity_at, current_timestamp) <= 14 then 2 -- inactive
            else 1  -- Very inactive
        end as activity_score,
        
        -- Priority scoring: considering deadlines and delays
        case 
            when due_date is not null and not is_completed then
                case 
                    when date_diff('day', current_date, due_date) <= 1 then 5  -- urgent
                    when date_diff('day', current_date, due_date) <= 3 then 4  -- high priority
                    when date_diff('day', current_date, due_date) <= 7 then 3  -- medium priority
                    when date_diff('day', current_date, due_date) <= 30 then 2 -- low priority
                    else 1  -- lowest priority
                end
            else 1
        end as urgency_score,
        
        -- Complexity score: based on description length and frequency of modifications
        case 
            when length(coalesce(task_description, '')) > 500 then 3  -- complex
            when length(coalesce(task_description, '')) > 100 then 2  -- medium
            else 1  -- Simple
        end as complexity_score
        
    from task_timeline
),

-- Add constraint checks
final_with_constraints as (
    select 
        *,
        
        -- Data quality mark
        case 
            when task_name is null or trim(task_name) = '' then false
            when created_at is null then false
            when days_open < 0 then false  -- Constraint: The number of open days cannot be negative
            when response_time_days < 0 then false  -- Constraint: response time cannot be negative  
            when delay_days < 0 then false  -- Constraint: Delay days cannot be negative
            else true
        end as is_valid_record,
        
        -- Performance level classification
        case 
            when is_completed and delay_days = 0 and response_time_days <= 1 then 'excellent'
            when is_completed and delay_days <= 2 and response_time_days <= 2 then 'good'
            when is_completed and delay_days <= 5 then 'fair'
            when is_completed and delay_days > 5 then 'poor'
            when not is_completed and task_status_category = 'overdue' then 'at_risk'
            else 'pending'
        end as performance_grade,
        
        -- Overall health score (1-100)
        least(100, greatest(0, 
            (activity_score * 20) +  -- Activity weight 20%
            (case when delay_days = 0 then 25 else greatest(0, 25 - delay_days * 5) end) +  -- Timeliness weight 25%
            (case when response_time_days <= 1 then 25 else greatest(0, 25 - response_time_days * 3) end) +  -- Responsiveness weight 25%
            (case when assignee_user_id is not null then 15 else 0 end) +  -- Assign status weight 15%
            (case when task_description is not null then 15 else 0 end)  -- Completeness weight 15%
        )) as health_score
        
    from performance_calculations
)

select * 
from final_with_constraints
where is_valid_record = true  -- Only output records that pass the data quality check
order by health_score desc, urgency_score desc, task_id
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2986 | 2986 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"task_id":"104142255084"}</code> |
| K2 | <code>{"task_id":"1174951657634"}</code> |
| K3 | <code>{"task_id":"1219555648771"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| activity_score | 0 | 0 | 0 | INTEGER | INTEGER |
| assignee_user_id | 0 | 0 | 0 | BIGINT | BIGINT |
| complexity_score | 0 | 0 | 0 | INTEGER | INTEGER |
| days_open | 0 | 0 | 0 | BIGINT | BIGINT |
| days_since_first_assignment | 0 | 0 | 0 | BIGINT | BIGINT |
| days_since_last_assignment | 0 | 0 | 0 | BIGINT | BIGINT |
| delay_days | 0 | 0 | 0 | BIGINT | BIGINT |
| due_date | 0 | 0 | 0 | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE |
| health_score | 0 | 0 | 0 | BIGINT | BIGINT |
| is_completed | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_valid_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| performance_grade | 0 | 0 | 0 | VARCHAR | VARCHAR |
| response_time_days | 0 | 0 | 0 | BIGINT | BIGINT |
| task_description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| task_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| task_status_category | 91 | 91 | 91 | VARCHAR | VARCHAR |
| urgency_score | 0 | 0 | 0 | INTEGER | INTEGER |

task_status_category 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | completed_on_time | completed_late |
| K2 | completed_on_time | completed_late |
| K3 | completed_on_time | completed_late |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>4列；[{"column":"first_assigned_at","table_rows":2986},{"column":"days_since_first_assignment","table_rows":2986},{"column":"days_since_last_assignment","table_rows":2986}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"activity_score","value":"1"},{"column":"is_valid_record","value":"true"}]</code> |
| C9_agent_runtime_text | <code>S4:13 CURRENT_DATE；命中数=11</code> |
| C9_gold_runtime_text | <code>S5:40 current_date；命中数=11</code> |
| C9_contract_runtime_text | <code>S3:695 today；命中数=6</code> |
| D10_keyword_in_any_result_field | <code>命中数=6；task_instruction_not_agent_report  5) Task portfolio (current snapshot): - From intermediate.int_asana__task_performance_metrics where assignee_user_id IS NOT NULL and is_valid_record = true; group by assignee_user_id.</code> |

## 轨迹索引（不放输出原文）

本题事件总数：55；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 12054 | true | false |
| 15 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/build.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging')<br># source columns select expressions and row filters<br>models={<br>'stg_asana__user':("</code> | 0 | false | false |
| 17 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/intermediate')<br>q={<br>'int_asana__task_story':'''SELECT s.story_id, s.created_at, s.created_by_user_id, s.story_type, s.story_text, s.targe</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/inter.py &lt;&lt;'PY'<br>q2={<br>'int_asana__project_health_indicators':'''WITH project_base AS (<br> SELECT * FROM staging.stg_asana__project WHERE project_name IS NOT NULL AND created_at IS NOT NULL<br>),</code> | 0 | false | false |
| 23 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>q={<br>'asana__user':'''SELECT u.user_id,u.user_name,u.email,COALESCE(m.number_of_open_tasks,0)::BIGINT number_of_open_tasks,COALES</code> | 0 | false | false |
| 25 | run | <code>cat &gt; /tmp/marts2.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>q={<br>'asana__project_analytics':'''WITH base AS (<br> SELECT p.project_id,p.project_name,p.team_id,t.team_name,p.owner_user_id proj</code> | 0 | false | false |
| 27 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7124 | true | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_asana__project.sql';s=open(p).read();<br>for x in ['created_at','due_date','modified_at']:<br> s=s.replace(f'TRY_CAST({x} AS TIMESTAMP)',f'CAST(TRY_STRPTIME({x}, \'%Y-%m-%</code> | 551 | false | false |
| 35 | run | <code>cat &gt; sql/marts/asana__daily_metrics.sql &lt;&lt;'SQL'<br>WITH creations AS (<br>    SELECT CAST(CAST(created_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC' AS date_day,<br>           COUNT(*)::HUGEINT AS tasks_create</code> | 328 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana.duckdb',read_only=True)<br>for sch in ['staging','intermediate','mart']:<br> print('\n',sch)<br> for (t,) in c.execute(f"select table_name from information</code> | 1027 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana.duckdb',read_only=True)<br>print(c.execute('select min(created_at),max(created_at),count(*) filter(where assignee_user_id is not null),current_date f</code> | 872 | false | false |
| 41 | run | <code>grep -R -nE ';[[:space:]]*$&#124;ref\(' sql &#124;&#124; true; python - &lt;&lt;'PY'<br>from pathlib import Path<br>expected={<br>'staging':'stg_asana__user stg_asana__team stg_asana__project stg_asana__task stg_asana__section stg</code> | 105 | false | false |

### agent action 的 thought/message 命中原句

event 17 / message

```text
'int_asana__task_performance_metrics':'''WITH tasks AS (
```
event 21 / message

```text
 LEFT JOIN intermediate.int_asana__task_performance_metrics pm ON t.task_id=pm.task_id
```
event 21 / message

```text
 FROM staging.stg_asana__task t JOIN intermediate.int_asana__task_performance_metrics p ON t.task_id=p.task_id
```
event 23 / message

```text
portfolio AS (SELECT assignee_user_id::VARCHAR user_id,COUNT(*)::BIGINT portfolio_task_count,COUNT(*) FILTER(WHERE task_status_category='assigned_active')::BIGINT portfolio_active_tasks,COUNT(*) FILTER(WHERE task_status_category='overdue')::BIGINT portfolio_overdue_tasks,COUNT(*) FILTER(WHERE urgency_score>=4)::BIGINT portfolio_high_priority,COUNT(*) FILTER(WHERE complexity_score=3)::BIGINT portfolio_complex_tasks,AVG(health_score) portfolio_avg_health,AVG(urgency_score) FILTER(WHERE due_date IS NOT NULL) portfolio_avg_urgency FROM intermediate.int_asana__task_performance_metrics WHERE assignee_user_id IS NOT NULL AND is_valid_record GROUP BY assignee_user_id),
```
event 25 / message

```text
FROM staging.stg_asana__task t LEFT JOIN intermediate.int_asana__task_performance_metrics m ON t.task_id=m.task_id LEFT JOIN story_agg s ON t.task_id=s.target_task_id WHERE t.created_at IS NOT NULL),
```
event 39 / message

```text
print(c.execute('select count(*) from staging.stg_asana__task t join intermediate.int_asana__task_performance_metrics p on t.task_id=p.task_id where t.created_at>=current_date-interval \'24 months\' and t.assignee_user_id is not null').fetchall())
```
event 41 / message

```text
'intermediate':'int_asana__task_story int_asana__task_assignee int_asana__task_open_length int_asana__task_comments int_asana__task_followers int_asana__task_tags int_asana__task_first_modifier int_asana__subtask_parent int_asana__task_projects int_asana__project_task_metrics int_asana__project_user int_asana__user_task_metrics int_asana__task_performance_metrics int_asana__user_productivity_trends int_asana__project_health_indicators'.split(),
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-008.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_performance_metrics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/intermediate/int_asana__task_performance_metrics.sql`
- S6: `records/006_contract_impl-008.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/result.md`
- S10: `data/021_packages_work/021_impl-008_int_asana__task_performance_metrics/021_impl-008_int_asana__task_performance_metrics.json`
- S11: `data/011_agent_alignment/impl-008_attempt_01/int_asana__task_performance_metrics_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/asana.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions`
