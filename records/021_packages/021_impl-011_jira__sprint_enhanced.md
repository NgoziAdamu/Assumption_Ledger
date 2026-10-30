# impl-011 | marts | jira__sprint_enhanced | 差异：S1；日期 原记录

## 契约完整原文

S3:2177–2245

```yaml
    - name: jira__sprint_enhanced
      description: Enhanced sprint metrics aggregated from daily sprint issue history
      grain: One row per sprint_id
      source_models:
      - marts.jira__daily_sprint_issue_history
      business_logic: 'Build sprint-level metrics from marts.jira__daily_sprint_issue_history: - Sprint metadata: Keep distinct combinations of sprint_id, sprint_name, sprint_started_at, sprint_ended_at, sprint_completed_at, board_id, original_estimate_seconds, remaining_estimate_seconds, and time_spent_seconds. - Sprint issue metrics (evaluated across all daily rows for the sprint_id): - sprint_issues: count distinct issue_id across all days. - sprint_assignees: count distinct assignee_user_id across all days (NULL user_ids are not counted). - open_sprint_issues: count distinct issues that are marked as sprint-active and open on any recorded day. - resolved_sprint_issues: count distinct issues whose resolution timestamp is on or before the sprint end and for which there is at least one daily record on or after the resolution date (distinct prevents multi-day double counting). - Commit-at-start metrics (snapshot at sprint start, or today''s snapshot for future-start sprints): - Filter rows where date_day equals the sprint start date, or where date_day equals today and the sprint start date is in the future. - story_points_committed and story_point_estimate_committed: sum values with per-row NULL treated as 0. - issues_committed: count distinct issue_id in the filtered set. - If no rows match this filter for a sprint_id, these fields are NULL after the LEFT JOIN. - End-of-sprint metrics (snapshot on the sprint end date): - Filter rows where date_day equals the sprint end date. - story_points_end and story_point_estimate_end: sum values with per-row NULL treated as 0. - story_points_completed and story_point_estimate_completed: sum values only for rows where the issue is marked resolved-in-sprint; NULL values are ignored by the SUM; if the end snapshot exists but none qualify, the sum is 0; if no end snapshot exists, the value is NULL. - Final assembly: - LEFT JOIN the issue, start, and end metrics to the metadata by sprint_id. - For original_estimate_seconds, remaining_estimate_seconds, and time_spent_seconds, sum across all distinct metadata rows for each sprint_id, treating NULL as 0; other selected fields are carried through to produce one row per sprint_id.'
      columns:
      - name: sprint_id
        data_type: VARCHAR
        description: Sprint primary key from daily history; grouping key for all metrics
        tests:
        - not_null
      - name: sprint_name
        data_type: VARCHAR
        description: Sprint name from daily history
      - name: sprint_started_at
        data_type: TIMESTAMP
        description: Sprint planned start timestamp from daily history
      - name: sprint_ended_at
        data_type: TIMESTAMP
        description: Sprint planned end timestamp from daily history
      - name: sprint_completed_at
        data_type: TIMESTAMP
        description: Timestamp when the sprint was completed (may be NULL if not completed)
      - name: board_id
        data_type: VARCHAR
        description: Board identifier associated with the sprint
      - name: story_points_committed
        data_type: HUGEINT
        description: Sum of story_points at the start snapshot or today's snapshot for future sprints; per-row NULLs treated as 0; NULL if no start snapshot
      - name: story_point_estimate_committed
        data_type: HUGEINT
        description: Sum of story_point_estimate at the start snapshot or today's snapshot for future sprints; per-row NULLs treated as 0; NULL if no start snapshot
      - name: story_points_end
        data_type: HUGEINT
        description: Sum of story_points on the sprint end date; per-row NULLs treated as 0; NULL if no end snapshot
      - name: story_point_estimate_end
        data_type: HUGEINT
        description: Sum of story_point_estimate on the sprint end date; per-row NULLs treated as 0; NULL if no end snapshot
      - name: story_points_completed
        data_type: HUGEINT
        description: Sum of story_points for issues marked resolved in the sprint on the end snapshot; 0 if snapshot exists but none qualify; NULL if no end snapshot
      - name: story_point_estimate_completed
        data_type: HUGEINT
        description: Sum of story_point_estimate for issues marked resolved in the sprint on the end snapshot; 0 if snapshot exists but none qualify; NULL if no end snapshot
      - name: sprint_assignees
        data_type: BIGINT
        description: Distinct assignee_user_id count across all daily rows (NULLs not counted)
      - name: sprint_issues
        data_type: BIGINT
        description: Distinct issue_id count across all daily rows for the sprint_id
      - name: issues_committed
        data_type: BIGINT
        description: Distinct issue count at the start snapshot; NULL if no start snapshot
      - name: open_sprint_issues
        data_type: BIGINT
        description: Distinct issues active in the sprint and open on any recorded day
      - name: resolved_sprint_issues
        data_type: BIGINT
        description: Distinct issues resolved on or before sprint end and with a daily record on or after their resolution date
      - name: original_estimate_seconds
        data_type: DOUBLE
        description: Sum of original_estimate_seconds across distinct metadata rows; NULLs treated as 0; unit seconds
      - name: remaining_estimate_seconds
        data_type: DOUBLE
        description: Sum of remaining_estimate_seconds across distinct metadata rows; NULLs treated as 0; unit seconds
      - name: time_spent_seconds
        data_type: DOUBLE
        description: Sum of time_spent_seconds across distinct metadata rows; NULLs treated as 0; unit seconds
```

## agent 最终 SQL

S4

```sql
select sprint_id,any_value(sprint_name) sprint_name,any_value(sprint_started_at) sprint_started_at,any_value(sprint_ended_at) sprint_ended_at,any_value(sprint_completed_at) sprint_completed_at,any_value(board_id) board_id,null::hugeint story_points_committed,null::hugeint story_point_estimate_committed,null::hugeint story_points_end,null::hugeint story_point_estimate_end,null::hugeint story_points_completed,null::hugeint story_point_estimate_completed,count(distinct assignee_user_id)::bigint sprint_assignees,count(distinct issue_id)::bigint sprint_issues,null::bigint issues_committed,count(distinct issue_id) filter(where is_sprint_active and is_issue_open)::bigint open_sprint_issues,count(distinct issue_id) filter(where is_issue_resolved_in_sprint)::bigint resolved_sprint_issues,sum(coalesce(original_estimate_seconds,0)) original_estimate_seconds,sum(coalesce(remaining_estimate_seconds,0)) remaining_estimate_seconds,sum(coalesce(time_spent_seconds,0)) time_spent_seconds from marts.jira__daily_sprint_issue_history group by sprint_id
```

## gold SQL（仅供定位差异）

S5

```sql
-- Enhanced sprint view with metrics and aggregated sprint performance data

with daily_sprint_issue_history as (
    select *
    from marts.jira__daily_sprint_issue_history
),

sprint_metrics_grouped as (
    select
        sprint_id, 
        sprint_name,
        sprint_started_at,
        sprint_ended_at,
        sprint_completed_at,
        board_id,
        original_estimate_seconds,
        remaining_estimate_seconds,
        time_spent_seconds
    from daily_sprint_issue_history
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9
),

sprint_issue_metrics as (
    select 
        sprint_id,
        count(distinct issue_id) as sprint_issues,
        count(distinct assignee_user_id) as sprint_assignees,
        count(distinct case when is_sprint_active and is_issue_open then issue_id end) as open_sprint_issues,
        count(distinct case when date_day >= cast(issue_resolved_at as date) 
            and issue_resolved_at <= sprint_ended_at
            then issue_id end) as resolved_sprint_issues
    from daily_sprint_issue_history
    group by 1
),

sprint_start_metrics as (
    select 
        sprint_id,
        sum(case when story_points is null then 0 else story_points end) as story_points_committed,
        sum(case when story_point_estimate is null then 0 else story_point_estimate end) as story_point_estimate_committed,
        count(distinct issue_id) as issues_committed
    from daily_sprint_issue_history
    -- to capture both sprints that have started or will start in the future
    where date_day = cast(sprint_started_at as date)
        or (date_day < cast(sprint_started_at as date)
            and date_day = cast(current_timestamp as date))
    group by 1
),

sprint_end_metrics as (
    select 
        sprint_id,
        sum(case when story_points is null then 0 else story_points end) as story_points_end,
        sum(case when story_point_estimate is null then 0 else story_point_estimate end) as story_point_estimate_end,
        sum(case when is_issue_resolved_in_sprint then story_points else 0 end) as story_points_completed,
        sum(case when is_issue_resolved_in_sprint then story_point_estimate else 0 end) as story_point_estimate_completed
    from daily_sprint_issue_history
    where date_day = cast(sprint_ended_at as date)
    group by 1
), 

final as (
    select 
        sprint_metrics_grouped.sprint_id, 
        sprint_metrics_grouped.sprint_name, 
        sprint_metrics_grouped.sprint_started_at,
        sprint_metrics_grouped.sprint_ended_at,
        sprint_metrics_grouped.sprint_completed_at,
        sprint_metrics_grouped.board_id,
        sprint_start_metrics.story_points_committed,
        sprint_start_metrics.story_point_estimate_committed,
        sprint_end_metrics.story_points_end,
        sprint_end_metrics.story_point_estimate_end,
        sprint_end_metrics.story_points_completed,
        sprint_end_metrics.story_point_estimate_completed,
        sprint_issue_metrics.sprint_assignees,
        sprint_issue_metrics.sprint_issues,
        sprint_start_metrics.issues_committed,
        sprint_issue_metrics.open_sprint_issues,
        sprint_issue_metrics.resolved_sprint_issues,
        sum(case when sprint_metrics_grouped.original_estimate_seconds is null then 0 else sprint_metrics_grouped.original_estimate_seconds end) as original_estimate_seconds,
        sum(case when sprint_metrics_grouped.remaining_estimate_seconds is null then 0 else sprint_metrics_grouped.remaining_estimate_seconds end) as remaining_estimate_seconds,
        sum(case when sprint_metrics_grouped.time_spent_seconds is null then 0 else sprint_metrics_grouped.time_spent_seconds end) as time_spent_seconds
    from sprint_metrics_grouped
    left join sprint_issue_metrics
        on sprint_metrics_grouped.sprint_id = sprint_issue_metrics.sprint_id
    left join sprint_start_metrics
        on sprint_metrics_grouped.sprint_id = sprint_start_metrics.sprint_id
    left join sprint_end_metrics
        on sprint_metrics_grouped.sprint_id = sprint_end_metrics.sprint_id
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
)

select * 
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 298 | 298 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"sprint_id":"2"}</code> |
| K2 | <code>{"sprint_id":"4"}</code> |
| K3 | <code>{"sprint_id":"5"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| sprint_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sprint_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| board_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| story_points_committed | 298 | 298 | 298 | HUGEINT | HUGEINT |
| story_point_estimate_committed | 298 | 298 | 298 | HUGEINT | HUGEINT |
| story_points_end | 298 | 298 | 298 | HUGEINT | HUGEINT |
| story_point_estimate_end | 298 | 298 | 298 | HUGEINT | HUGEINT |
| story_points_completed | 298 | 298 | 298 | HUGEINT | HUGEINT |
| story_point_estimate_completed | 298 | 298 | 298 | HUGEINT | HUGEINT |
| sprint_assignees | 0 | 0 | 0 | BIGINT | BIGINT |
| sprint_issues | 0 | 0 | 0 | BIGINT | BIGINT |
| issues_committed | 298 | 298 | 298 | BIGINT | BIGINT |
| open_sprint_issues | 0 | 0 | 0 | BIGINT | BIGINT |
| resolved_sprint_issues | 0 | 0 | 0 | BIGINT | BIGINT |

story_points_committed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 38 |
| K2 | null | 5 |
| K3 | null | 9 |

story_point_estimate_committed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 38 |
| K2 | null | 5 |
| K3 | null | 9 |

story_points_end 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 38 |
| K2 | null | 5 |
| K3 | null | 9 |

story_point_estimate_end 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 38 |
| K2 | null | 5 |
| K3 | null | 9 |

story_points_completed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 17 |
| K2 | null | 0 |
| K3 | null | 2 |

story_point_estimate_completed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 17 |
| K2 | null | 0 |
| K3 | null | 2 |

issues_committed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 10 |
| K2 | null | 6 |
| K3 | null | 12 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>7列；[{"column":"story_points_committed","table_rows":298},{"column":"story_point_estimate_committed","table_rows":298},{"column":"story_points_end","table_rows":298}]</code> |
| B5_null_literal_output | <code>7输出列；[{"column":"story_points_committed","expression":["CAST(NULL AS INT128)"]},{"column":"story_point_estimate_committed","expression":["CAST(NULL AS INT128)"]},{"column":"story_points_end","expression":["CAST(NULL AS INT128)"]}]</code> |
| C9_gold_runtime_text | <code>S5:46 current_timestamp；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:2182 today；命中数=4</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'jira__sprint_enhanced':"select sprint_id,any_value(sprint_name) sprint_name,any_value(sprint_started_at) sprint_started_at,any_value(sprint_ended_at) sprint_ended_at,any_value(sprint_completed_at) sprint_completed_at,any_value(board_id) board_id,null::hugeint story_points_committed,null::hugeint story_point_estimate_committed,null::hugeint story_points_end,null::hugeint story_point_estimate_end,null::hugeint story_points_completed,null::hugeint story_point_estimate_completed,count(distinct assignee_user_id)::bigint sprint_assignees,count(distinct issue_id)::bigint sprint_issues,null::bigint issues_committed,count(distinct issue_id) filter(where is_sprint_active and is_issue_open)::bigint open_sprint_issues,count(distinct issue_id) filter(where is_issue_resolved_in_sprint)::bigint resolved_sprint_issues,sum(coalesce(original_estimate_seconds,0)) original_estimate_seconds,sum(coalesce(remaining_estimate_seconds,0)) remaining_estimate_seconds,sum(coalesce(time_spent_seconds,0)) time_spent_seconds from marts.jira__daily_sprint_issue_history group by sprint_id",</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,240p' run.py</code> | 14395 | true | false |
| 17 | run | <code>cat &gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>Q={<br>'jira__daily_issue_field_history':"select cast(i.created_at as date) date_day,cast(i.created_at as date) date_week,i.iss</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>Q.update({<br>'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i</code> | 6630 | true | false |
| 23 | run | <code>grep -E 'WARNING -  ⏭&#124;WARNING -   ⏭&#124;Catalog Error&#124;Binder Error&#124;Parser Error&#124;Conversion Error' /tmp/runlog &#124; head -80</code> | 8767 | true | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> s=re.sub(r'try_cast\((\w+) as timestamp\)',r"try_cast(regexp_replace(\1, '([+-][0-9]{2}</code> | 9550 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text().replace("regexp_replace(created, '([+-][0-9]{2})([0-9]{2})$', '\\\\1:\\\\2')", "regexp_replace(cre</code> | 4200 | true | false |

### agent action 的 thought/message 命中原句

event 17 / message

```text
'jira__sprint_enhanced':"select sprint_id,any_value(sprint_name) sprint_name,any_value(sprint_started_at) sprint_started_at,any_value(sprint_ended_at) sprint_ended_at,any_value(sprint_completed_at) sprint_completed_at,any_value(board_id) board_id,null::hugeint story_points_committed,null::hugeint story_point_estimate_committed,null::hugeint story_points_end,null::hugeint story_point_estimate_end,null::hugeint story_points_completed,null::hugeint story_point_estimate_completed,count(distinct assignee_user_id)::bigint sprint_assignees,count(distinct issue_id)::bigint sprint_issues,null::bigint issues_committed,count(distinct issue_id) filter(where is_sprint_active and is_issue_open)::bigint open_sprint_issues,count(distinct issue_id) filter(where is_issue_resolved_in_sprint)::bigint resolved_sprint_issues,sum(coalesce(original_estimate_seconds,0)) original_estimate_seconds,sum(coalesce(remaining_estimate_seconds,0)) remaining_estimate_seconds,sum(coalesce(time_spent_seconds,0)) time_spent_seconds from marts.jira__daily_sprint_issue_history group by sprint_id",
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-011.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql`
- S6: `records/006_contract_impl-011.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/result.md`
- S10: `data/021_packages_work/021_impl-011_jira__sprint_enhanced/021_impl-011_jira__sprint_enhanced.json`
- S11: `data/005_cs_work/impl-011_retry_02/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/jira.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions`
