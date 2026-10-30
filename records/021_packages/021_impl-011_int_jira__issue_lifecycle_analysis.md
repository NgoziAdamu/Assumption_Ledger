# impl-011 | intermediate | int_jira__issue_lifecycle_analysis | 差异：S1；日期 原记录

## 契约完整原文

S3:676–755

```yaml
    - name: int_jira__issue_lifecycle_analysis
      description: Issue lifecycle metrics and activity-based classifications derived from non-null field history changes
      grain: One row per issue_id
      source_models:
      - staging.stg_jira__issue
      - staging.stg_jira__issue_field_history
      business_logic: '- Build issue_activity_history from staging.stg_jira__issue_field_history: - Keep only records where field_value is present. - For each issue_id, sort changes by updated_at ascending and derive: - previous_change_time: the timestamp of the immediately prior change for the same issue; null for the first change. - change_sequence: the 1-based position of the change in the sorted list. - total_changes: the total number of non-null field_value changes for the issue (reference only). - If multiple changes share an identical updated_at within an issue, their tie-order is implementation-dependent (no secondary tiebreaker). - Build activity_patterns by retaining only changes with a previous_change_time and compute: - days_between_changes: elapsed time in days between change_time and previous_change_time. - hours_between_changes: elapsed time in hours between change_time and previous_change_time (intermediate only; not output). - Summarize per issue_id (issue_activity_summary): - total_field_changes: the count of retained changes (number of consecutive intervals). - avg_days_between_changes: average of days_between_changes. - max_days_between_changes: maximum of days_between_changes. - activity_variance: standard deviation of days_between_changes. - first_change_time: earliest change_time among retained changes. - last_change_time: latest change_time among retained changes. - When no retained changes exist, the summary has no row; downstream metrics remain null, with total_field_changes set to 0 in the final step. - Build issue_base_info from staging.stg_jira__issue and compute: - total_lifecycle_days: elapsed time in days from created_at to resolved_at; if unresolved, to the current timestamp at execution. - Final integration and classifications (left join summary to base on issue_id): - total_field_changes: set to 0 when summary is missing; other summary metrics remain null when missing. - activity_pattern: - If total_field_changes = 0 → "No Activity". - Otherwise by avg_days_between_changes: ≤1 → "High Activity"; ≤7 → "Regular Activity"; ≤30 → "Low Activity"; else → "Minimal Activity". - lifecycle_speed: - By total_lifecycle_days: ≤7 → "Fast"; ≤30 → "Normal"; ≤90 → "Slow"; else → "Very Slow". - risk_indicator (applied in order): - If total_lifecycle_days > 90 and total_field_changes < 5 → "Stagnant". - Else if max_days_between_changes > 30 → "Inactive Periods". - Else if total_field_changes > 50 → "Over Worked". - Else → "Normal". - Output one row per issue_id from staging.stg_jira__issue; the final result is ordered by issue_id ascending.'
      columns:
      - name: issue_id
        data_type: VARCHAR
        description: Primary grouping key from Jira; exactly one output row per issue_id
        tests:
        - not_null
        - unique
      - name: issue_key
        data_type: VARCHAR
        description: Human-readable Jira issue key (e.g., PROJ-123)
        tests:
        - not_null
      - name: issue_type_id
        data_type: VARCHAR
        description: Issue type identifier from Jira
      - name: priority_id
        data_type: VARCHAR
        description: Priority identifier from Jira
      - name: project_id
        data_type: VARCHAR
        description: Project identifier from Jira
        tests:
        - not_null
      - name: created_at
        data_type: TIMESTAMP
        description: Issue creation timestamp from Jira
        tests:
        - not_null
      - name: resolved_at
        data_type: TIMESTAMP
        description: Issue resolution timestamp; null if unresolved
      - name: assignee_user_id
        data_type: VARCHAR
        description: Current assignee user identifier from Jira
      - name: reporter_user_id
        data_type: VARCHAR
        description: Reporter user identifier from Jira
      - name: total_lifecycle_days
        data_type: DOUBLE
        description: Fractional days from created_at to resolved_at; if unresolved, to current_timestamp at execution; no rounding
      - name: total_field_changes
        data_type: BIGINT
        description: Count of consecutive change intervals (rows with non-null previous_change_time) over non-null field_value changes; 0 when none
      - name: avg_days_between_changes
        data_type: DOUBLE
        description: 'Average of days_between_changes across change intervals; unit: days; null when no intervals'
      - name: max_days_between_changes
        data_type: DOUBLE
        description: 'Maximum of days_between_changes across change intervals; unit: days; null when no intervals'
      - name: activity_variance
        data_type: DOUBLE
        description: Standard deviation of days_between_changes across change intervals; null when no intervals
      - name: first_change_time
        data_type: TIMESTAMP
        description: Earliest change_time among intervals (second or later change); null when no intervals
      - name: last_change_time
        data_type: TIMESTAMP
        description: Latest change_time among intervals; null when no intervals
      - name: activity_pattern
        data_type: VARCHAR
        description: 'Classification: No Activity if total_field_changes=0; else High/Regular/Low/Minimal based on avg_days_between_changes thresholds'
        tests:
        - activity_pattern IN ('No Activity', 'High Activity', 'Regular Activity', 'Low Activity', 'Minimal Activity')
      - name: lifecycle_speed
        data_type: VARCHAR
        description: 'Classification from total_lifecycle_days: Fast (≤7), Normal (≤30), Slow (≤90), else Very Slow'
        tests:
        - lifecycle_speed IN ('Fast', 'Normal', 'Slow', 'Very Slow')
      - name: risk_indicator
        data_type: VARCHAR
        description: 'Risk classification applied in order: Stagnant, then Inactive Periods, then Over Worked, else Normal'
        tests:
        - risk_indicator IN ('Normal', 'Stagnant', 'Inactive Periods', 'Over Worked')
```

## agent 最终 SQL

S4

```sql
with h as (select issue_id,updated_at change_time,lag(updated_at) over(partition by issue_id order by updated_at) previous_change_time from staging.stg_jira__issue_field_history where field_value is not null), a as (select issue_id,epoch(change_time-previous_change_time)/86400.0 days_between_changes from h where previous_change_time is not null), s as (select issue_id,count(*) total_field_changes,avg(days_between_changes) avg_days_between_changes,max(days_between_changes) max_days_between_changes,stddev_samp(days_between_changes) activity_variance,min(change_time) first_change_time,max(change_time) last_change_time from (select h.issue_id,h.change_time,a.days_between_changes from h join a using(issue_id) where h.previous_change_time is not null) q group by issue_id), b as (select *,epoch(coalesce(resolved_at,current_timestamp)-created_at)/86400.0 total_lifecycle_days from staging.stg_jira__issue) select b.issue_id,b.issue_key,b.issue_type_id,b.priority_id,b.project_id,b.created_at,b.resolved_at,b.assignee_user_id,b.reporter_user_id,b.total_lifecycle_days,coalesce(s.total_field_changes,0) total_field_changes,s.avg_days_between_changes,s.max_days_between_changes,s.activity_variance,s.first_change_time,s.last_change_time,case when coalesce(s.total_field_changes,0)=0 then 'No Activity' when s.avg_days_between_changes<=1 then 'High Activity' when s.avg_days_between_changes<=7 then 'Regular Activity' when s.avg_days_between_changes<=30 then 'Low Activity' else 'Minimal Activity' end activity_pattern,case when b.total_lifecycle_days<=7 then 'Fast' when b.total_lifecycle_days<=30 then 'Normal' when b.total_lifecycle_days<=90 then 'Slow' else 'Very Slow' end lifecycle_speed,case when b.total_lifecycle_days>90 and coalesce(s.total_field_changes,0)<5 then 'Stagnant' when s.max_days_between_changes>30 then 'Inactive Periods' when s.total_field_changes>50 then 'Over Worked' else 'Normal' end risk_indicator from b left join s using(issue_id)
```

## gold SQL（仅供定位差异）

S5

```sql
-- Simplified issue lifecycle analysis using available field history data
-- Analyzes issue change patterns and activity over time

with issue_activity_history as (
    select 
        h.issue_id,
        h.field_id,
        h.updated_at as change_time,
        h.field_value,
        h.is_active,
        lag(h.updated_at) over (partition by h.issue_id order by h.updated_at) as previous_change_time,
        row_number() over (partition by h.issue_id order by h.updated_at) as change_sequence,
        count(*) over (partition by h.issue_id) as total_changes
    from staging.stg_jira__issue_field_history h
    where h.field_value is not null
),

activity_patterns as (
    select 
        issue_id,
        change_sequence,
        change_time,
        previous_change_time,
        total_changes,
        case when previous_change_time is not null then
            extract('epoch' from (change_time - previous_change_time)) / 86400.0 
        end as days_between_changes,
        case when previous_change_time is not null then
            extract('epoch' from (change_time - previous_change_time)) / 3600.0 
        end as hours_between_changes
    from issue_activity_history
    where previous_change_time is not null
),

issue_base_info as (
    select 
        i.issue_id,
        i.issue_key,
        i.issue_type_id,
        i.priority_id,
        i.project_id,
        i.created_at,
        i.resolved_at,
        i.assignee_user_id,
        i.reporter_user_id,
        case 
            when i.resolved_at is null then extract('epoch' from (current_timestamp - i.created_at)) / 86400.0
            else extract('epoch' from (i.resolved_at - i.created_at)) / 86400.0
        end as total_lifecycle_days
    from staging.stg_jira__issue i
),

issue_activity_summary as (
    select 
        ap.issue_id,
        count(*) as total_field_changes,
        avg(ap.days_between_changes) as avg_days_between_changes,
        max(ap.days_between_changes) as max_days_between_changes,
        min(ap.days_between_changes) as min_days_between_changes,
        stddev(ap.days_between_changes) as activity_variance,
        min(ap.change_time) as first_change_time,
        max(ap.change_time) as last_change_time
    from activity_patterns ap
    group by ap.issue_id
),

final_analysis as (
    select 
        ib.issue_id,
        ib.issue_key,
        ib.issue_type_id,
        ib.priority_id,
        ib.project_id,
        ib.created_at,
        ib.resolved_at,
        ib.assignee_user_id,
        ib.reporter_user_id,
        ib.total_lifecycle_days,
        
        -- Activity metrics
        coalesce(ias.total_field_changes, 0) as total_field_changes,
        ias.avg_days_between_changes,
        ias.max_days_between_changes,
        ias.activity_variance,
        ias.first_change_time,
        ias.last_change_time,
        
        -- Activity pattern classification
        case 
            when coalesce(ias.total_field_changes, 0) = 0 then 'No Activity'
            when ias.avg_days_between_changes <= 1 then 'High Activity'
            when ias.avg_days_between_changes <= 7 then 'Regular Activity'
            when ias.avg_days_between_changes <= 30 then 'Low Activity'
            else 'Minimal Activity'
        end as activity_pattern,
        
        -- Lifecycle efficiency
        case 
            when ib.total_lifecycle_days <= 7 then 'Fast'
            when ib.total_lifecycle_days <= 30 then 'Normal'
            when ib.total_lifecycle_days <= 90 then 'Slow'
            else 'Very Slow'
        end as lifecycle_speed,
        
        -- Risk indicators
        case 
            when ib.total_lifecycle_days > 90 and coalesce(ias.total_field_changes, 0) < 5 then 'Stagnant'
            when ias.max_days_between_changes > 30 then 'Inactive Periods'
            when coalesce(ias.total_field_changes, 0) > 50 then 'Over Worked'
            else 'Normal'
        end as risk_indicator
    from issue_base_info ib
    left join issue_activity_summary ias on ib.issue_id = ias.issue_id
)

select * from final_analysis
order by issue_id
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 8000 | 8000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"issue_id":"iss10291827892"}</code> |
| K2 | <code>{"issue_id":"iss10368173535"}</code> |
| K3 | <code>{"issue_id":"iss10417446517"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| issue_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| issue_key | 0 | 0 | 0 | VARCHAR | VARCHAR |
| issue_type_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| priority_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| project_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| assignee_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| reporter_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_field_changes | 1542 | 1542 | 1542 | BIGINT | BIGINT |
| activity_pattern | 0 | 0 | 0 | VARCHAR | VARCHAR |
| lifecycle_speed | 0 | 0 | 0 | VARCHAR | VARCHAR |

total_field_changes 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 16 | 4 |
| K2 | 4 | 2 |
| K3 | 9 | 3 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| C9_agent_runtime_text | <code>S4:1 current_timestamp；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:47 current_timestamp；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:682 current timestamp；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'int_jira__issue_lifecycle_analysis':"with h as (select issue_id,updated_at change_time,lag(updated_at) over(partition by issue_id order by updated_at) previous_change_time from staging.stg_jira__issue_field_history where field_value is not null), a as (select issue_id,epoch(change_time-previous_change_time)/86400.0 days_between_changes from h where previous_change_time is not null), s as (select issue_id,count(*) total_field_changes,avg(days_between_changes) avg_days_between_changes,max(days_between_changes) max_days_between_changes,stddev_samp(days_between_changes) activity_variance,min(change_time) first_change_time,max(change_time) last_change_time from (select h.issue_id,h.change_time,a.days_between_changes from h join a using(issue_id) where h.previous_change_time is not null) q group by issue_id), b as (select *,epoch(coalesce(resolved_at,current_timestamp)-created_at)/86400.0 total_lifecycle_days from staging.stg_jira__issue) select b.issue_id,b.issue_key,b.issue_type_id,b.priority_id,b.project_id,b.created_at,b.resolved_at,b.assignee_user_id,b.reporter_user_id,b.total_lifecycle_days,coalesce(s.total_field_changes,0) total_field_changes,s.avg_days_between_changes,s.max_days_between_changes,s.activity_variance,s.first_change_time,s.last_change_time,case when coalesce(s.total_field_changes,0)=0 then 'No Activity' when s.avg_days_between_changes&lt;=1 then 'High Activity' when s.avg_days_between_changes&lt;=7 then 'Regular Activity' when s.avg_days_between_changes&lt;=30 then 'Low Activity' else 'Minimal Activity' end activity_pattern,case when b.total_lifecycle_days&lt;=7 then 'Fast' when b.total_lifecycle_days&lt;=30 then 'Normal' when b.total_lifecycle_days&lt;=90 then 'Slow' else 'Very Slow' end lifecycle_speed,case when b.total_lifecycle_days&gt;90 and coalesce(s.total_field_changes,0)&lt;5 then 'Stagnant' when s.max_days_between_changes&gt;30 then 'Inactive Periods' when s.total_field_changes&gt;50 then 'Over Worked' else 'Normal' end risk_indicator from b left join s using(issue_id)",</code> |

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
| 21 | run | <code>cat &gt;&gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>Q.update({<br>'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i</code> | 6630 | true | false |
| 27 | run | <code>grep -oE '.{0,25}committed.{0,25}' sql/intermediate/int_jira__sprint_performance_analytics.sql &#124; head; python - &lt;&lt;'PY'<br>p='sql/intermediate/int_jira__user_activity_metrics.sql'<br>s=open(p).read(); start=</code> | 613 | false | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> s=re.sub(r'try_cast\((\w+) as timestamp\)',r"try_cast(regexp_replace(\1, '([+-][0-9]{2}</code> | 9550 | true | false |
| 33 | run | <code>cat sql/staging/stg_jira__issue_type.sql; grep -o '.\{0,30\}prev_committed.\{0,30\}' sql/intermediate/int_jira__sprint_performance_analytics.sql; cat sql/staging/stg_jira__issue.sql &#124; head -c 800</code> | 1230 | false | false |
| 35 | run | <code>sed -i 's/description,is_subtask subtask as is_subtask/description,subtask as is_subtask/' sql/staging/stg_jira__issue_type.sql; sed -i 's/committed_points-prev_committed)/committed_points-prev_commit</code> | 53 | false | false |
| 41 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; grep -E 'INTERMEDIATE Layer&#124;✓ intermediate.int_jira__issue_join&#124;✓ intermediate.int_jira__issue_users&#124;staging.stg_jira__issue:' /tmp/runlog3</code> | 836 | false | false |
| 43 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; cat sql/intermediate/int_jira__issue_calendar_spine.sql</code> | 1202 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('jira.duckdb',read_only=True)<br>checks=[('staging.stg_jira__issue','issue_id'),('staging.stg_jira__project','project_id'),('intermediate.int_jira__issue_jo</code> | 422 | false | false |

### agent action 的 thought/message 命中原句

event 15 / message

```text
'int_jira__issue_lifecycle_analysis':"with h as (select issue_id,updated_at change_time,lag(updated_at) over(partition by issue_id order by updated_at) previous_change_time from staging.stg_jira__issue_field_history where field_value is not null), a as (select issue_id,epoch(change_time-previous_change_time)/86400.0 days_between_changes from h where previous_change_time is not null), s as (select issue_id,count(*) total_field_changes,avg(days_between_changes) avg_days_between_changes,max(days_between_changes) max_days_between_changes,stddev_samp(days_between_changes) activity_variance,min(change_time) first_change_time,max(change_time) last_change_time from (select h.issue_id,h.change_time,a.days_between_changes from h join a using(issue_id) where h.previous_change_time is not null) q group by issue_id), b as (select *,epoch(coalesce(resolved_at,current_timestamp)-created_at)/86400.0 total_lifecycle_days from staging.stg_jira__issue) select b.issue_id,b.issue_key,b.issue_type_id,b.priority_id,b.project_id,b.created_at,b.resolved_at,b.assignee_user_id,b.reporter_user_id,b.total_lifecycle_days,coalesce(s.total_field_changes,0) total_field_changes,s.avg_days_between_changes,s.max_days_between_changes,s.activity_variance,s.first_change_time,s.last_change_time,case when coalesce(s.total_field_changes,0)=0 then 'No Activity' when s.avg_days_between_changes<=1 then 'High Activity' when s.avg_days_between_changes<=7 then 'Regular Activity' when s.avg_days_between_changes<=30 then 'Low Activity' else 'Minimal Activity' end activity_pattern,case when b.total_lifecycle_days<=7 then 'Fast' when b.total_lifecycle_days<=30 then 'Normal' when b.total_lifecycle_days<=90 then 'Slow' else 'Very Slow' end lifecycle_speed,case when b.total_lifecycle_days>90 and coalesce(s.total_field_changes,0)<5 then 'Stagnant' when s.max_days_between_changes>30 then 'Inactive Periods' when s.total_field_changes>50 then 'Over Worked' else 'Normal' end risk_indicator from b left join s using(issue_id)",
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-011.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_lifecycle_analysis.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/intermediate/int_jira__issue_lifecycle_analysis.sql`
- S6: `records/006_contract_impl-011.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/result.md`
- S10: `data/021_packages_work/021_impl-011_int_jira__issue_lifecycle_analysis/021_impl-011_int_jira__issue_lifecycle_analysis.json`
- S11: `data/005_cs_work/impl-011_retry_02/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/jira.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions`
