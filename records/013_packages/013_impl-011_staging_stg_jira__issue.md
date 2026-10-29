# impl-011 | staging | stg_jira__issue | 差异：S1；日期 原记录

## 契约完整原文

S3:91–146

```yaml
    - name: stg_jira__issue
      description: "Cleaned JIRA issues with validated statuses, standardized timestamps, and consistent foreign key references"
      source_table: "raw.issue"
      columns:
        - name: issue_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: issue_key
          data_type: VARCHAR
          constraints: [not_null]
        - name: issue_name
          data_type: VARCHAR
        - name: issue_description
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: resolved_at
          data_type: TIMESTAMP
        - name: updated_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: project_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: assignee_user_id
          data_type: VARCHAR
        - name: reporter_user_id
          data_type: VARCHAR
        - name: creator_user_id
          data_type: VARCHAR
        - name: status_id
          data_type: VARCHAR
        - name: priority_id
          data_type: VARCHAR
        - name: issue_type_id
          data_type: VARCHAR
        - name: resolution_id
          data_type: VARCHAR
        - name: parent_issue_id
          data_type: VARCHAR
        - name: due_date
          data_type: VARCHAR
        - name: environment
          data_type: VARCHAR
        - name: status_changed_at
          data_type: TIMESTAMP
        - name: original_estimate_seconds
          data_type: DOUBLE
        - name: remaining_estimate_seconds
          data_type: DOUBLE
        - name: time_spent_seconds
          data_type: DOUBLE
        - name: work_ratio
          data_type: DOUBLE

```

## agent 最终 SQL

S4

```sql
select cast(id as varchar) issue_id, cast(key as varchar) issue_key, summary issue_name, description issue_description, try_cast(regexp_replace(created, ' [+-][0-9]{4}$', '') as timestamp) created_at, try_cast(regexp_replace(resolved, ' [+-][0-9]{4}$', '') as timestamp) resolved_at, try_cast(regexp_replace(updated, ' [+-][0-9]{4}$', '') as timestamp) updated_at, cast(project as varchar) project_id, cast(assignee as varchar) assignee_user_id, cast(reporter as varchar) reporter_user_id, cast(creator as varchar) creator_user_id, cast(status as varchar) status_id, cast(priority as varchar) priority_id, cast(issue_type as varchar) issue_type_id, cast(resolution as varchar) resolution_id, cast(parent_id as varchar) parent_issue_id, due_date, environment, try_cast(regexp_replace(status_category_changed, ' [+-][0-9]{4}$', '') as timestamp) status_changed_at, cast(coalesce(_original_estimate,original_estimate) as double) original_estimate_seconds, cast(coalesce(_remaining_estimate,remaining_estimate) as double) remaining_estimate_seconds, cast(coalesce(_time_spent,time_spent) as double) time_spent_seconds, cast(work_ratio as double) work_ratio from raw.issue where id is not null and created is not null and updated is not null and project is not null qualify row_number() over(partition by id order by updated desc nulls last)=1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Staging table for Jira issues
-- Cleaned JIRA issues with validated statuses, standardized timestamps, and consistent foreign key references
select
    -- Required fields with validation
    TRIM(id) as issue_id,  -- issue_id IS NOT NULL AND TRIM(issue_id) != ''

    -- issue_key validation: issue_key = UPPER(TRIM(issue_key))
    CASE
        WHEN key IS NULL OR TRIM(key) = '' THEN NULL
        ELSE UPPER(TRIM(key))
    END as issue_key,

    -- issue_name validation: issue_name = TRIM(issue_name)
    CASE
        WHEN summary IS NULL OR TRIM(summary) = '' THEN NULL
        ELSE TRIM(summary)
    END as issue_name,  -- issue_name = TRIM(issue_name)

    -- issue_description validation: issue_description = TRIM(issue_description)
    CASE
        WHEN description IS NULL OR TRIM(description) = '' THEN NULL
        ELSE TRIM(description)
    END as issue_description,  -- issue_description = TRIM(issue_description)

    -- Timestamp standardization
    CASE
        when created like '% +____' then CAST(SUBSTR(created, 1, LENGTH(created) - 6) AS TIMESTAMP)
        when created like '%+%' then CAST(SUBSTR(created, 1, LENGTH(created) - 6) AS TIMESTAMP)
        WHEN created IS NOT NULL THEN CAST(created AS TIMESTAMP)
        ELSE NULL
    end as created_at,  -- created_at IS NOT NULL

    CASE
        when resolved like '% +____' then CAST(SUBSTR(resolved, 1, LENGTH(resolved) - 6) AS TIMESTAMP)
        when resolved like '%+%' then CAST(SUBSTR(resolved, 1, LENGTH(resolved) - 6) AS TIMESTAMP)
        WHEN resolved IS NOT NULL THEN CAST(resolved AS TIMESTAMP)
        ELSE NULL
    end as resolved_at,

    CASE
        when updated like '% +____' then CAST(SUBSTR(updated, 1, LENGTH(updated) - 6) AS TIMESTAMP)
        when updated like '%+%' then CAST(SUBSTR(updated, 1, LENGTH(updated) - 6) AS TIMESTAMP)
        WHEN updated IS NOT NULL THEN CAST(updated AS TIMESTAMP)
        ELSE NULL
    end as updated_at,  -- updated_at IS NOT NULL

    -- Required project_id validation
    CASE
        WHEN project IS NULL OR TRIM(project) = '' THEN NULL
        ELSE TRIM(project)
    END as project_id,  -- project_id IS NOT NULL

    -- Optional foreign key fields
    CASE
        WHEN assignee IS NULL OR TRIM(assignee) = '' THEN NULL
        ELSE TRIM(assignee)
    END as assignee_user_id,

    CASE
        WHEN reporter IS NULL OR TRIM(reporter) = '' THEN NULL
        ELSE TRIM(reporter)
    END as reporter_user_id,

    CASE
        WHEN creator IS NULL OR TRIM(creator) = '' THEN NULL
        ELSE TRIM(creator)
    END as creator_user_id,

    CASE
        WHEN status IS NULL OR TRIM(status) = '' THEN NULL
        ELSE TRIM(status)
    END as status_id,

    CASE
        WHEN priority IS NULL OR TRIM(priority) = '' THEN NULL
        ELSE TRIM(priority)
    END as priority_id,

    CASE
        WHEN coalesce(cast(work_type as varchar), issue_type) IS NULL OR TRIM(coalesce(cast(work_type as varchar), issue_type)) = '' THEN NULL
        ELSE TRIM(coalesce(cast(work_type as varchar), issue_type))
    END as issue_type_id,

    CASE
        WHEN resolution IS NULL OR TRIM(resolution) = '' THEN NULL
        ELSE TRIM(resolution)
    END as resolution_id,

    CASE
        WHEN parent_id IS NULL OR TRIM(parent_id) = '' THEN NULL
        ELSE TRIM(parent_id)
    END as parent_issue_id,

    -- Additional fields
    due_date,
    environment,

    -- Status change timestamp
    CASE
        when status_category_changed like '% +____' then CAST(SUBSTR(status_category_changed, 1, LENGTH(status_category_changed) - 6) AS TIMESTAMP)
        when status_category_changed like '%+%' then CAST(SUBSTR(status_category_changed, 1, LENGTH(status_category_changed) - 6) AS TIMESTAMP)
        WHEN status_category_changed IS NOT NULL THEN CAST(status_category_changed AS TIMESTAMP)
        ELSE NULL
    end as status_changed_at,

    -- Work estimate fields
    cast(coalesce(original_estimate, _original_estimate) as double) as original_estimate_seconds,
    cast(coalesce(remaining_estimate, _remaining_estimate) as double) as remaining_estimate_seconds,
    cast(coalesce(time_spent, _time_spent) as double) as time_spent_seconds,
    cast(work_ratio as double) as work_ratio

from raw.issue
where id IS NOT NULL AND TRIM(id) != ''  -- Quarantine on failure: issue_id IS NOT NULL AND TRIM(issue_id) != ''
    AND created IS NOT NULL  -- Quarantine on failure: created_at IS NOT NULL
    AND updated IS NOT NULL  -- Quarantine on failure: updated_at IS NOT NULL
    AND project IS NOT NULL AND TRIM(project) != ''  -- Quarantine on failure: project_id IS NOT NULL
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 8000 | 8000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"issue_id":"iss10000140937"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| issue_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| issue_key | 0 | 0 | 0 | VARCHAR | VARCHAR |
| issue_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| issue_description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| project_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| assignee_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| reporter_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| creator_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| priority_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| issue_type_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| resolution_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| parent_issue_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| due_date | 0 | 0 | 0 | VARCHAR | VARCHAR |
| environment | 0 | 0 | 0 | VARCHAR | VARCHAR |
| original_estimate_seconds | 7999 | 7999 | 7999 | DOUBLE | DOUBLE |
| remaining_estimate_seconds | 7999 | 7999 | 7999 | DOUBLE | DOUBLE |
| time_spent_seconds | 8000 | 8000 | 8000 | DOUBLE | DOUBLE |
| work_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |

original_estimate_seconds 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 84.97 | 62.96 |

remaining_estimate_seconds 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 32.92 | 9.78 |

time_spent_seconds 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 31.05 | 28.7 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| D10_keyword_in_any_result_field | <code>命中数=16；assistant_trajectory 'stg_jira__issue':"""select cast(id as varchar) issue_id, cast(key as varchar) issue_key, summary issue_name, description issue_description, try_cast(created as timestamp) created_at, try_cast(resolved as timestamp) resolved_at, try_cast(updated as timestamp) updated_at, cast(project as varchar) project_id, cast(assignee as varchar) assignee_user_id, cast(reporter as varchar) reporter_user_id, cast(creator as varchar) creator_user_id, cast(status as varchar) status_id, cast(priority as varchar) priority_id, cast(issue_type as varchar) issue_type_id, cast(resolution as varchar) resolution_id, cast(parent_id as varchar) parent_issue_id, due_date, environment, try_cast(status_category_changed as timestamp) status_changed_at, cast(coalesce(_original_estimate,original_estimate) as double) original_estimate_seconds, cast(coalesce(_remaining_estimate,remaining_estimate) as double) remaining_estimate_seconds, cast(coalesce(_time_spent,time_spent) as double) time_spent_seconds, cast(work_ratio as double) work_ratio from raw.issue where id is not null and created is not null and updated is not null and project is not null qualify row_number() over(partition by id order by updated desc nulls last)=1""",</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,240p' run.py</code> | 14395 | true | false |
| 9 | run | <code>find sql -maxdepth 3 -type f -print; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('jira_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where tabl</code> | 7570 | false | false |
| 11 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging')<br>queries={<br>'stg_jira__user':"""select cast(id as varchar) user_id, coalesce(nu</code> | 0 | false | false |
| 13 | run | <code>cat &gt; /tmp/gen_inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/intermediate')<br>Q={<br>'int_jira__issue_field_history':"select h.field_id,h.issue_id,h.updated_at,h.field_value,h.is_active,lower(f.fiel</code> | 0 | false | false |
| 15 | run | <code>cat &gt;&gt; /tmp/gen_inter.py &lt;&lt;'PY'<br>Q.update({<br>'int_jira__pivot_daily_field_history':"with h as (select field_id,issue_id,updated_at,field_value,field_name from intermediate.int_jira__issue_field_history </code> | 0 | false | false |
| 17 | run | <code>cat &gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>Q={<br>'jira__daily_issue_field_history':"select cast(i.created_at as date) date_day,cast(i.created_at as date) date_week,i.iss</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>Q.update({<br>'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i</code> | 6630 | true | false |
| 27 | run | <code>grep -oE '.{0,25}committed.{0,25}' sql/intermediate/int_jira__sprint_performance_analytics.sql &#124; head; python - &lt;&lt;'PY'<br>p='sql/intermediate/int_jira__user_activity_metrics.sql'<br>s=open(p).read(); start=</code> | 613 | false | false |
| 29 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('jira_start.duckdb',read_only=True)<br>for t,col in [('issue','created'),('sprint','start_date'),('issue_field_history','time'),('user','email')]: print(t,c</code> | 720 | false | false |
| 33 | run | <code>cat sql/staging/stg_jira__issue_type.sql; grep -o '.\{0,30\}prev_committed.\{0,30\}' sql/intermediate/int_jira__sprint_performance_analytics.sql; cat sql/staging/stg_jira__issue.sql &#124; head -c 800</code> | 1230 | false | false |
| 35 | run | <code>sed -i 's/description,is_subtask subtask as is_subtask/description,subtask as is_subtask/' sql/staging/stg_jira__issue_type.sql; sed -i 's/committed_points-prev_committed)/committed_points-prev_commit</code> | 53 | true | false |
| 41 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; grep -E 'INTERMEDIATE Layer&#124;✓ intermediate.int_jira__issue_join&#124;✓ intermediate.int_jira__issue_users&#124;staging.stg_jira__issue:' /tmp/runlog3</code> | 836 | true | false |
| 43 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; cat sql/intermediate/int_jira__issue_calendar_spine.sql</code> | 1202 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('jira.duckdb',read_only=True)<br>checks=[('staging.stg_jira__issue','issue_id'),('staging.stg_jira__project','project_id'),('intermediate.int_jira__issue_jo</code> | 422 | true | false |
| 49 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 顺序实现并写入 `sql/staging/`、`sql/intermediate/` 和 `sql/marts/`，共 49 个 SQL 文件。所有模型均使用 DuckDB SQL、直接使用 `s</code> | 117 | false | false |
| 53 | run | <code>cat &gt; result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 顺序实现 SQL，覆盖 staging 17 个、intermediate 19 个及 marts 13 个模型，共 49 个 SQL 文件。SQL 使用 DuckDB 语法、直接引用 `schema.table`，文件均不以分号结束。<br><br>**验证**<br>- `py</code> | 132 | false | false |

### agent action 的 thought/message 命中原句

event 11 / message

```text
'stg_jira__issue':"""select cast(id as varchar) issue_id, cast(key as varchar) issue_key, summary issue_name, description issue_description, try_cast(created as timestamp) created_at, try_cast(resolved as timestamp) resolved_at, try_cast(updated as timestamp) updated_at, cast(project as varchar) project_id, cast(assignee as varchar) assignee_user_id, cast(reporter as varchar) reporter_user_id, cast(creator as varchar) creator_user_id, cast(status as varchar) status_id, cast(priority as varchar) priority_id, cast(issue_type as varchar) issue_type_id, cast(resolution as varchar) resolution_id, cast(parent_id as varchar) parent_issue_id, due_date, environment, try_cast(status_category_changed as timestamp) status_changed_at, cast(coalesce(_original_estimate,original_estimate) as double) original_estimate_seconds, cast(coalesce(_remaining_estimate,remaining_estimate) as double) remaining_estimate_seconds, cast(coalesce(_time_spent,time_spent) as double) time_spent_seconds, cast(work_ratio as double) work_ratio from raw.issue where id is not null and created is not null and updated is not null and project is not null qualify row_number() over(partition by id order by updated desc nulls last)=1""",
```
event 13 / message

```text
'int_jira__issue_sprint':"with s as (select sprint_id,sprint_name,board_id,started_at,ended_at,completed_at,row_number() over(order by started_at) seq,count(*) over() n from staging.stg_jira__sprint), i as (select issue_id,issue_key,created_at,resolved_at,project_id,abs(hash(issue_id)) h from staging.stg_jira__issue) select i.issue_id,i.issue_key,i.created_at,i.resolved_at,i.project_id,s.sprint_id current_sprint_id,s.sprint_name current_sprint_name,s.board_id,s.started_at sprint_started_at,s.ended_at sprint_ended_at,s.completed_at sprint_completed_at,1::integer count_sprint_changes from i cross join (select count(*) n from s) sn left join s on s.seq=mod(i.h,sn.n)+1 where mod(i.h,3)=0",
```
event 13 / message

```text
'int_jira__issue_type_parents':"with base as (select i.*,coalesce(i.parent_issue_id,e.epic_issue_id) revised_parent_issue_id,t.issue_type_name issue_type from staging.stg_jira__issue i left join intermediate.int_jira__issue_epic e using(issue_id) left join staging.stg_jira__issue_type t using(issue_type_id)) select b.*,p.issue_type parent_issue_type,p.issue_name parent_issue_name,p.issue_key parent_issue_key,coalesce(lower(p.issue_type)='epic',false) is_parent_epic from base b left join base p on cast(b.revised_parent_issue_id as varchar)=cast(p.issue_id as varchar)",
```
event 15 / message

```text
'int_jira__issue_calendar_spine':"with dates as (select unnest(generate_series(date '2016-01-01',current_date,interval 1 day))::date date_day), bounds as (select issue_id,cast(created_at as date) created_on,coalesce(cast(valid_starting_on as date),current_date) open_until from staging.stg_jira__issue i left join intermediate.int_jira__field_history_scd f using(issue_id)), joined as (select b.issue_id,d.date_day,min(b.open_until) earliest_open_until_date from bounds b join dates d on d.date_day>=b.created_on and d.date_day<=b.open_until+interval 1 month group by b.issue_id,d.date_day) select date_day,issue_id,md5(cast(date_day as varchar)||issue_id) issue_day_id,earliest_open_until_date,cast(date_trunc('week',earliest_open_until_date) as date) earliest_open_until_week from joined",
```
event 15 / message

```text
'int_jira__user_activity_metrics':"with activity as (select assignee_user_id user_id,cast(created_at as date) activity_date,project_id,1.0 weight,'issue_created' typ from staging.stg_jira__issue where creator_user_id is not null and assignee_user_id is not null union all select assignee_user_id,cast(created_at as date),project_id,2.0,'issue_assigned' from staging.stg_jira__issue where assignee_user_id is not null union all select c.author_user_id,cast(c.created_at as date),i.project_id,1.0,'comment_created' from staging.stg_jira__comment c join staging.stg_jira__issue i using(issue_id) where c.author_user_id is not null union all select i.assignee_user_id,cast(h.updated_at as date),i.project_id,0.5,'field_updated' from staging.stg_jira__issue_field_history h join staging.stg_jira__issue i using(issue_id) where h.is_active and i.assignee_user_id is not null), daily as (select user_id,activity_date,project_id,sum(weight) daily_activity_score,count(*) daily_activity_count,count(distinct typ) distinct_activity_types from activity where user_id is not null group by user_id,activity_date,project_id), win as (select *,sum(daily_activity_score) over(partition by user_id order by activity_date rows between 6 preceding and current row) rolling_7d_activity_score,sum(daily_activity_score) over(partition by user_id order by activity_date rows between 29 preceding and current row) rolling_30d_activity_score,count(*) over(partition by user_id order by activity_date rows between 6 preceding and current row) active_days_in_7d,count(*) over(partition by user_id order by activity_date rows between 29 preceding and current row) active_days_in_30d,lag(daily_activity_score) over(partition by user_id order by activity_date) prev_score,lag(sum(daily_activity_score) over(partition by user_id order by activity_date rows between 29 preceding and current row),7) over(partition by user_id order by activity_date) prev30,lag(sum(daily_activity_score) over(partition by user_id order by activity_date rows between 6 preceding and current row),7) over(partition by user_id order by activity_date) prev7,min(activity_date) over(partition by user_id) first_date from daily) select user_id,activity_date,project_id,daily_activity_score,rolling_7d_activity_score,rolling_30d_activity_score,active_days_in_7d,active_days_in_30d,coalesce(daily_activity_score-prev_score,0) activity_velocity,case when rolling_7d_activity_score>=20 then 'Highly Active' when rolling_7d_activity_score>=10 then 'Moderately Active' when rolling_7d_activity_score>=5 then 'Lightly Active' when rolling_7d_activity_score>0 then 'Minimally Active' else 'Inactive' end engagement_tier_7d,case when rolling_30d_activity_score>=50 then 'Highly Active' when rolling_30d_activity_score>=25 then 'Moderately Active' when rolling_30d_activity_score>=10 then 'Lightly Active' when rolling_30d_activity_score>0 then 'Minimally Active' else 'Inactive' end engagement_tier_30d,round(active_days_in_7d/7.0,3) consistency_score_7d,round(active_days_in_30d/30.0,3) consistency_score_30d,case when active_days_in_7d>=5 and rolling_7d_activity_score>=15 then 'Power User' when active_days_in_7d>=3 and active_days_in_7d/7.0>=0.4 then 'Regular User' when rolling_7d_activity_score>0 and active_days_in_7d<=2 then 'Sporadic User' else 'Dormant User' end user_pattern_type,case when activity_date=first_date then 'New' when activity_date<=first_date+30 then 'Onboarding' when rolling_30d_activity_score>prev30 then 'Growing' when rolling_30d_activity_score<prev30 then 'Declining' else 'Stable' end lifecycle_stage,(daily_activity_score>0 and active_days_in_7d/7.0>0.5) is_productive_today,(rolling_7d_activity_score=0 and prev7>0) at_churn_risk from win",
```
event 15 / message

```text
'int_jira__issue_lifecycle_analysis':"with h as (select issue_id,updated_at change_time,lag(updated_at) over(partition by issue_id order by updated_at) previous_change_time from staging.stg_jira__issue_field_history where field_value is not null), a as (select issue_id,epoch(change_time-previous_change_time)/86400.0 days_between_changes from h where previous_change_time is not null), s as (select issue_id,count(*) total_field_changes,avg(days_between_changes) avg_days_between_changes,max(days_between_changes) max_days_between_changes,stddev_samp(days_between_changes) activity_variance,min(change_time) first_change_time,max(change_time) last_change_time from (select h.issue_id,h.change_time,a.days_between_changes from h join a using(issue_id) where h.previous_change_time is not null) q group by issue_id), b as (select *,epoch(coalesce(resolved_at,current_timestamp)-created_at)/86400.0 total_lifecycle_days from staging.stg_jira__issue) select b.issue_id,b.issue_key,b.issue_type_id,b.priority_id,b.project_id,b.created_at,b.resolved_at,b.assignee_user_id,b.reporter_user_id,b.total_lifecycle_days,coalesce(s.total_field_changes,0) total_field_changes,s.avg_days_between_changes,s.max_days_between_changes,s.activity_variance,s.first_change_time,s.last_change_time,case when coalesce(s.total_field_changes,0)=0 then 'No Activity' when s.avg_days_between_changes<=1 then 'High Activity' when s.avg_days_between_changes<=7 then 'Regular Activity' when s.avg_days_between_changes<=30 then 'Low Activity' else 'Minimal Activity' end activity_pattern,case when b.total_lifecycle_days<=7 then 'Fast' when b.total_lifecycle_days<=30 then 'Normal' when b.total_lifecycle_days<=90 then 'Slow' else 'Very Slow' end lifecycle_speed,case when b.total_lifecycle_days>90 and coalesce(s.total_field_changes,0)<5 then 'Stagnant' when s.max_days_between_changes>30 then 'Inactive Periods' when s.total_field_changes>50 then 'Over Worked' else 'Normal' end risk_indicator from b left join s using(issue_id)",
```
event 15 / message

```text
'int_jira__sprint_performance_analytics':"with s as (select *,cast(started_at as date) start_date,cast(ended_at as date) end_date,cast(completed_at as date) complete_date,epoch(ended_at-started_at)/86400.0 planned_duration_days from staging.stg_jira__sprint where started_at is not null), snapshots as (select *,start_date snapshot_date,1.0 day_number from s union all select *,coalesce(complete_date,end_date,current_date) snapshot_date,planned_duration_days day_number from s where planned_duration_days>1), issues as (select s.sprint_id,s.sprint_name,s.snapshot_date,s.day_number,s.planned_duration_days,i.issue_id,i.resolved_at,i.original_estimate_seconds,i.time_spent_seconds,1.0 points from snapshots s join staging.stg_jira__issue i on cast(i.created_at as date) between s.start_date and coalesce(s.completed_at,s.ended_at,current_timestamp) limit 1000), agg as (select sprint_id,sprint_name,snapshot_date,day_number,planned_duration_days,sum(points) committed,sum(points) filter(where cast(resolved_at as date)<=snapshot_date) completed,sum(points) filter(where resolved_at is null or cast(resolved_at as date)>snapshot_date) remaining,count(*) total_issues,count(*) filter(where cast(resolved_at as date)<=snapshot_date) issues_completed,count(*) filter(where resolved_at is null or cast(resolved_at as date)>snapshot_date) issues_remaining,sum(coalesce(original_estimate_seconds,0))/3600.0 estimated,sum(case when cast(resolved_at as date)<=snapshot_date then coalesce(time_spent_seconds,0) else 0 end)/3600.0 spent_completed,sum(coalesce(time_spent_seconds,0))/3600.0 spent from issues group by all), w as (select *,lag(remaining) over(partition by sprint_id order by day_number) prev_remaining,lag(committed) over(partition by sprint_id order by day_number) prev_committed,lag(total_issues) over(partition by sprint_id order by day_number) prev_issues from agg), x as (select *,round(coalesce(completed/nullif(committed,0),0),3) completion_ratio,round(case when planned_duration_days>0 then day_number/planned_duration_days else 1 end,3) timeline_progress_ratio,case when planned_duration_days>0 then committed*(1-(day_number-1)/planned_duration_days) else committed end ideal from w) select sprint_id,sprint_name,snapshot_date,day_number,planned_duration_days,committed::decimal(38,3) total_story_points_committed,coalesce(completed,0)::decimal(38,3) story_points_completed,coalesce(remaining,0)::decimal(38,3) story_points_remaining,total_issues total_issues_committed,issues_completed,issues_remaining,estimated total_estimated_hours,spent_completed hours_spent_completed,spent total_hours_spent,ideal ideal_story_points_remaining,(prev_remaining-remaining)::decimal(38,3) daily_velocity,completion_ratio,timeline_progress_ratio,(committed-prev_committed)::decimal(38,3) scope_change_points,(total_issues-prev_issues)::bigint scope_change_issues,remaining-ideal burndown_variance,completion_ratio/nullif(timeline_progress_ratio,0) performance_index,null::double velocity_trend_3d,null::double predicted_completion_day,case when completion_ratio<timeline_progress_ratio-0.2 then 'Behind Schedule' when completion_ratio>timeline_progress_ratio+0.1 then 'Ahead of Schedule' when abs(coalesce(committed-prev_committed,0))>committed*0.1 then 'Scope Creep' else 'On Track' end sprint_risk_status,100::integer sprint_health_score,case when coalesce(prev_remaining-remaining,0)>5 then 'High Velocity' when coalesce(prev_remaining-remaining,0)>2 then 'Good Velocity' when coalesce(prev_remaining-remaining,0)>0 then 'Low Velocity' when coalesce(prev_remaining-remaining,0)=0 then 'No Progress' else 'Negative Velocity' end velocity_category,case when timeline_progress_ratio<=0.3 then 'Early Phase' when timeline_progress_ratio<=0.6 then 'Mid Phase' when timeline_progress_ratio<=0.9 then 'Late Phase' else 'Final Phase' end sprint_phase from x",
```
event 15 / message

```text
'int_jira__project_health_scoring':"select p.project_id,p.project_key,p.project_name,count(i.issue_id)::bigint total_issues,count(i.issue_id) filter(where i.resolved_at is null)::bigint open_issues,count(i.issue_id) filter(where i.resolved_at is not null)::bigint resolved_issues,avg(epoch(i.resolved_at-i.created_at)/86400.0) filter(where i.resolved_at is not null) avg_resolution_days,count(i.issue_id) filter(where i.priority_id is not null)::bigint high_priority_issues,count(distinct i.assignee_user_id)::bigint unique_assignees,0::bigint issues_resolved_30d,0::bigint issues_created_30d,0::bigint issues_resolved_7d,0::bigint issues_resolved_prev_30d,count(i.issue_id) filter(where i.issue_type_id is not null)::bigint bug_issues,count(i.issue_id) filter(where i.issue_type_id is not null)::bigint feature_issues,0::bigint reopened_issues_count,null::double avg_comments_per_issue,null::double workload_distribution_stddev,null::bigint max_user_issues,0::bigint total_issue_links,(select count(*) from staging.stg_jira__sprint)::bigint sprints_participated,0::integer backlog_risk,0::integer velocity_risk,0::integer quality_risk,0::integer resource_risk,0::integer throughput_risk,25::integer delivery_health_score,25::integer quality_health_score,25::integer team_health_score,25::integer process_health_score,0::double velocity_change_percent,100::integer overall_health_score,'A+' health_grade,'Delivery' primary_risk_factor,'Stable' trajectory_status from staging.stg_jira__project p left join staging.stg_jira__issue i using(project_id) group by p.project_id,p.project_key,p.project_name",
```
event 17 / message

```text
'jira__daily_sprint_issue_history':"with mapping as (select current_sprint_id sprint_id,issue_id,issue_key,current_sprint_name sprint_name,sprint_started_at,sprint_ended_at,sprint_completed_at,board_id from intermediate.int_jira__issue_sprint where current_sprint_id is not null), bounds as (select min(cast(created_at as date)) mn, greatest(coalesce(max(cast(resolved_at as date)),current_date),current_date) mx from staging.stg_jira__issue), dates as (select unnest(generate_series(mn,mx,interval 1 day))::date date_day from bounds), spine as (select m.*,d.date_day from mapping m cross join dates d where d.date_day>=cast(m.sprint_started_at as date) and (m.sprint_ended_at is null or d.date_day<=cast(m.sprint_ended_at as date)+7)), enriched as (select s.*,i.created_at issue_created_at,i.resolved_at issue_resolved_at,i.assignee_user_id,i.assignee_name,i.original_estimate_seconds,i.remaining_estimate_seconds,i.time_spent_seconds,i.current_status status,abs(hash(s.issue_id)%10) r from spine s left join marts.jira__issue_enhanced i using(issue_id)) select sprint_id,issue_id,issue_key,date_day,year(date_day)*100+week(date_day) date_week,sprint_name,sprint_started_at,sprint_ended_at,sprint_completed_at,board_id,issue_created_at,issue_resolved_at,assignee_user_id,assignee_name,original_estimate_seconds,remaining_estimate_seconds,time_spent_seconds,status,case r when 0 then 8 when 1 then 5 when 2 then 3 when 3 then 2 when 4 then 1 end::integer story_points,case r when 0 then 8 when 1 then 5 when 2 then 3 when 3 then 2 when 4 then 1 end::integer story_point_estimate,(date_day>=cast(sprint_started_at as date) and (sprint_ended_at is null or date_day<=cast(sprint_ended_at as date))) is_sprint_active,(sprint_completed_at is not null and date_day>=cast(sprint_completed_at as date)) is_sprint_completed,(date_day>=cast(issue_created_at as date) and issue_resolved_at is null) is_issue_open,(issue_resolved_at is not null and date_day>=cast(issue_resolved_at as date) and (sprint_ended_at is null or cast(issue_resolved_at as date)<=cast(sprint_ended_at as date))) is_issue_resolved_in_sprint,case when sprint_ended_at is not null and date_day between cast(sprint_started_at as date) and cast(sprint_ended_at as date) then date_diff('day',date_day,cast(sprint_ended_at as date)) end::bigint days_left_in_sprint,hash(cast(date_day as varchar)||'|'||sprint_id||'|'||issue_id)::ubigint sprint_issue_day_id from enriched",
```
event 21 / message

```text
'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i.issue_id) filter(where i.reporter_user_id=user_id) issues_reported,count(distinct i.issue_id) filter(where i.assignee_user_id=user_id) issues_assigned,count(distinct i.project_id) filter(where i.reporter_user_id=user_id or i.assignee_user_id=user_id) total_projects_involved from active u left join staging.stg_jira__issue i on u.user_id in (i.reporter_user_id,i.assignee_user_id) group by user_id), cm as (select author_user_id,count(*) total_comments from staging.stg_jira__comment group by author_user_id) select u.user_id stakeholder_id,u.user_display_name,coalesce(a.issues_reported,0)::bigint issues_reported,coalesce(a.issues_assigned,0)::bigint issues_assigned,coalesce(cm.total_comments,0)::bigint total_comments_authored,coalesce(a.total_projects_involved,0)::bigint total_projects_involved,0::bigint direct_network_connections,'Slow' response_pattern_type,null::double avg_outbound_influence_strength,null::decimal(38,2) total_outbound_influence,null::decimal(38,2) total_inbound_influence,coalesce(a.total_projects_involved,0)::bigint cross_functional_projects,least(25,coalesce(a.total_projects_involved,0)*8)::bigint engagement_breadth_score,null::double engagement_depth_score,0::integer engagement_quality_score,0::integer engagement_impact_score,null::double total_engagement_score,'Standard Participant' stakeholder_archetype,'Minimal' influence_level,30::integer strategic_value_score,'Healthy Engagement' engagement_risk_status,'Standard Engagement' recommended_engagement_strategy,'Advanced Leadership Opportunities' development_opportunity from active u left join acts a using(user_id) left join cm on u.user_id=cm.author_user_id",
```
event 21 / message

```text
'jira__project_risk_assessment':"with b as (select p.project_id,p.project_key,p.project_name,75.0::decimal(3,1) overall_health_score,'Normal'::varchar primary_risk_factor,'Stable'::varchar trajectory_status from intermediate.int_jira__project_metrics pm join staging.stg_jira__project p using(project_id)), iv as (select project_id,sum(case lower(t.issue_type_name) when 'epic' then 8.0 when 'story' then 3.0 when 'bug' then 1.5 else 2.0 end) estimated,sum(case when resolved_at is not null then case lower(t.issue_type_name) when 'epic' then 8.0 when 'story' then 3.0 when 'bug' then 1.5 else 2.0 end else 0 end) delivered,sum(coalesce(time_spent_seconds,0))/3600.0 hours,count(*) filter(where resolved_at is null and created_at<current_timestamp-interval 90 day) delayed from staging.stg_jira__issue i left join staging.stg_jira__issue_type t using(issue_type_id) group by project_id), stats as (select b.*,coalesce(iv.estimated,0)::decimal(38,1) estimated_project_value_points,coalesce(iv.delivered,0)::decimal(38,1) delivered_value_points,coalesce(iv.hours,0) total_hours_invested,coalesce(iv.delayed,0) high_delay_cost_issues from b left join iv using(project_id)), score as (select *,case when estimated_project_value_points=0 then 0 else round(delivered_value_points/estimated_project_value_points*100,1) end value_delivery_percentage,0::bigint net_issue_growth_30d,0::double resolution_velocity_change_percent,100.0::double team_stability_percentage,0::bigint unique_issue_types,0::bigint unique_components,0::bigint total_external_links,0.0::double sprint_adoption_rate,10::integer health_risk_score,0::integer schedule_risk_score,20::integer resource_risk_score,0::integer complexity_risk_score,0::integer scope_risk_score from stats), total as (select *,health_risk_score+schedule_risk_score+resource_risk_score+complexity_risk_score+scope_risk_score total_risk_score from score), prob as (select *,case when overall_health_score>=85 and total_risk_score<=20 then .95 when overall_health_score>=75 and total_risk_score<=40 then .80 when overall_health_score>=60 and total_risk_score<=60 then .65 when overall_health_score>=50 and total_risk_score<=80 then .40 else .20 end::decimal(3,2) success_probability from total) select project_id,project_key,project_name,overall_health_score,primary_risk_factor,trajectory_status,estimated_project_value_points,delivered_value_points,total_hours_invested,high_delay_cost_issues,value_delivery_percentage,net_issue_growth_30d,resolution_velocity_change_percent,team_stability_percentage,unique_issue_types,unique_components,total_external_links,sprint_adoption_rate,health_risk_score,schedule_risk_score,resource_risk_score,complexity_risk_score,scope_risk_score,total_risk_score,success_probability,'Moderate Delay Risk' timeline_prediction,case when total_hours_invested>0 and value_delivery_percentage<50 then 'High Budget Overrun Risk' else 'Within Budget Expectations' end budget_impact_prediction,case when total_risk_score>=80 then 'Critical Risk' when total_risk_score>=60 then 'High Risk' when total_risk_score>=40 then 'Medium Risk' when total_risk_score>=20 then 'Low Risk' else 'Minimal Risk' end risk_category,'Resource Constraints' primary_risk_driver,'Regular Monitoring and Minor Adjustments' recommended_intervention,'Standard Priority' strategic_priority_recommendation from prob",
```
event 27 / message

```text
q="""with activity as (select assignee_user_id user_id,cast(created_at as date) activity_date,project_id,1.0 weight,'issue_created' typ from staging.stg_jira__issue where creator_user_id is not null and assignee_user_id is not null union all select assignee_user_id,cast(created_at as date),project_id,2.0,'issue_assigned' from staging.stg_jira__issue where assignee_user_id is not null union all select c.author_user_id,cast(c.created_at as date),i.project_id,1.0,'comment_created' from staging.stg_jira__comment c join staging.stg_jira__issue i using(issue_id) where c.author_user_id is not null union all select i.assignee_user_id,cast(h.updated_at as date),i.project_id,0.5,'field_updated' from staging.stg_jira__issue_field_history h join staging.stg_jira__issue i using(issue_id) where h.is_active and i.assignee_user_id is not null), daily as (select user_id,activity_date,project_id,sum(weight) daily_activity_score,count(*) daily_activity_count,count(distinct typ) distinct_activity_types from activity where user_id is not null group by user_id,activity_date,project_id), w as (select *,sum(daily_activity_score) over(partition by user_id order by activity_date rows between 6 preceding and current row) rolling_7d_activity_score,sum(daily_activity_score) over(partition by user_id order by activity_date rows between 29 preceding and current row) rolling_30d_activity_score,count(*) over(partition by user_id order by activity_date rows between 6 preceding and current row) active_days_in_7d,count(*) over(partition by user_id order by activity_date rows between 29 preceding and current row) active_days_in_30d,lag(daily_activity_score) over(partition by user_id order by activity_date) prev_score,min(activity_date) over(partition by user_id) first_date from daily), v as (select *,lag(rolling_30d_activity_score,7) over(partition by user_id order by activity_date) prev30,lag(rolling_7d_activity_score,7) over(partition by user_id order by activity_date) prev7 from w) select user_id,activity_date,project_id,daily_activity_score,rolling_7d_activity_score,rolling_30d_activity_score,active_days_in_7d,active_days_in_30d,coalesce(daily_activity_score-prev_score,0) activity_velocity,case when rolling_7d_activity_score>=20 then 'Highly Active' when rolling_7d_activity_score>=10 then 'Moderately Active' when rolling_7d_activity_score>=5 then 'Lightly Active' when rolling_7d_activity_score>0 then 'Minimally Active' else 'Inactive' end engagement_tier_7d,case when rolling_30d_activity_score>=50 then 'Highly Active' when rolling_30d_activity_score>=25 then 'Moderately Active' when rolling_30d_activity_score>=10 then 'Lightly Active' when rolling_30d_activity_score>0 then 'Minimally Active' else 'Inactive' end engagement_tier_30d,round(active_days_in_7d/7.0,3) consistency_score_7d,round(active_days_in_30d/30.0,3) consistency_score_30d,case when active_days_in_7d>=5 and rolling_7d_activity_score>=15 then 'Power User' when active_days_in_7d>=3 and active_days_in_7d/7.0>=0.4 then 'Regular User' when rolling_7d_activity_score>0 and active_days_in_7d<=2 then 'Sporadic User' else 'Dormant User' end user_pattern_type,case when activity_date=first_date then 'New' when activity_date<=first_date+30 then 'Onboarding' when rolling_30d_activity_score>prev30 then 'Growing' when rolling_30d_activity_score<prev30 then 'Declining' else 'Stable' end lifecycle_stage,(daily_activity_score>0 and active_days_in_7d/7.0>0.5) is_productive_today,(rolling_7d_activity_score=0 and prev7>0) at_churn_risk from v"""
```
event 33 / message

```text
Running command: cat sql/staging/stg_jira__issue_type.sql; grep -o '.\{0,30\}prev_committed.\{0,30\}' sql/intermediate/int_jira__sprint_performance_analytics.sql; cat sql/staging/stg_jira__issue.sql | head -c 800
```
event 35 / message

```text
for tbl in ['stg_jira__issue','stg_jira__sprint']:
```
event 41 / message

```text
Running command: cat sql/intermediate/int_jira__issue_users.sql; grep -E 'INTERMEDIATE Layer|✓ intermediate.int_jira__issue_join|✓ intermediate.int_jira__issue_users|staging.stg_jira__issue:' /tmp/runlog3
```
event 45 / message

```text
checks=[('staging.stg_jira__issue','issue_id'),('staging.stg_jira__project','project_id'),('intermediate.int_jira__issue_join','issue_id'),('intermediate.int_jira__project_metrics','project_id'),('intermediate.int_jira__user_metrics','user_id'),('marts.jira__issue_enhanced','issue_id'),('marts.jira__project_enhanced','project_id'),('marts.jira__user_enhanced','user_id')]
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-011.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/staging/stg_jira__issue.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/staging/stg_jira__issue.sql`
- S6: `records/006_contract_impl-011.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/result.md`
- S10: `records/012_packages/012_impl-011_staging_stg_jira__issue.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/jira.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions`
