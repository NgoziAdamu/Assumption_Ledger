# impl-008 | marts | asana__daily_metrics | 差异：S1；日期 原记录

## 契约完整原文

S3:974–992

```yaml
    - name: asana__daily_metrics
      description: Daily counts of tasks created, tasks completed, and their net difference, aggregated by calendar day.
      grain: One row per date_day
      source_models:
      - staging.stg_asana__task (created_at, completed_at)
      business_logic: 'Build two daily aggregates from staging.stg_asana__task: - Creations: for each task, take the calendar day of its creation timestamp; tasks missing a creation timestamp are counted under a single NULL day; count tasks per day and label as task_created. - Completions: for each task with a completion timestamp, take the calendar day of that timestamp; count tasks per day and label as task_completed. Combine both sets without deduplication, then for each day: - tasks_created = total counts from task_created entries for that day (else 0). - tasks_completed = total counts from task_completed entries for that day (else 0). - net_task_change = tasks_created minus tasks_completed. Output one row per day present in either set (including a NULL day if any tasks lack a creation timestamp), ordered ascending by date_day.'
      columns:
      - name: date_day
        data_type: TIMESTAMP WITH TIME ZONE
        description: Calendar day used for aggregation (midnight in its time zone); may be NULL only from missing created_at; one row per distinct value.
      - name: tasks_created
        data_type: HUGEINT
        description: Number of tasks whose creation timestamp falls on date_day; 0 if none; never NULL.
      - name: tasks_completed
        data_type: HUGEINT
        description: Number of tasks with a completion timestamp that falls on date_day; 0 if none; never NULL.
      - name: net_task_change
        data_type: HUGEINT
        description: tasks_created minus tasks_completed for the same date_day; can be negative; never NULL.
```

## agent 最终 SQL

S4

```sql
WITH creations AS (
    SELECT CAST(CAST(created_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC' AS date_day,
           COUNT(*)::HUGEINT AS tasks_created
    FROM staging.stg_asana__task
    GROUP BY CAST(created_at AS DATE)
),
completions AS (
    SELECT CAST(CAST(completed_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC' AS date_day,
           COUNT(*)::HUGEINT AS tasks_completed
    FROM staging.stg_asana__task
    WHERE completed_at IS NOT NULL
    GROUP BY CAST(completed_at AS DATE)
),
days AS (
    SELECT date_day FROM creations
    UNION
    SELECT date_day FROM completions
)
SELECT d.date_day,
       COALESCE(c.tasks_created, 0)::HUGEINT AS tasks_created,
       COALESCE(x.tasks_completed, 0)::HUGEINT AS tasks_completed,
       (COALESCE(c.tasks_created, 0) - COALESCE(x.tasks_completed, 0))::HUGEINT AS net_task_change
FROM days d
LEFT JOIN creations c ON d.date_day IS NOT DISTINCT FROM c.date_day
LEFT JOIN completions x ON d.date_day IS NOT DISTINCT FROM x.date_day
ORDER BY d.date_day
```

## gold SQL（仅供定位差异）

S5

```sql
with task as (
    select *
    from staging.stg_asana__task
),

daily_task_activity as (
    select
        date_trunc('day', created_at) as date_day,
        'task_created' as metric_type,
        count(*) as metric_value
    from task
    group by 1, 2
    
    union all
    
    select
        date_trunc('day', completed_at) as date_day,
        'task_completed' as metric_type,
        count(*) as metric_value
    from task
    where completed_at is not null
    group by 1, 2
),

daily_metrics as (
    select
        date_day,
        sum(case when metric_type = 'task_created' then metric_value else 0 end) as tasks_created,
        sum(case when metric_type = 'task_completed' then metric_value else 0 end) as tasks_completed,
        sum(case when metric_type = 'task_created' then metric_value else 0 end) - 
        sum(case when metric_type = 'task_completed' then metric_value else 0 end) as net_task_change
    from daily_task_activity
    group by 1
)

select * from daily_metrics
order by date_day
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1 | 1 | 1 | 1 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE |
| tasks_created | 0 | 0 | 0 | HUGEINT | HUGEINT |
| tasks_completed | 0 | 0 | 0 | HUGEINT | HUGEINT |
| net_task_change | 0 | 0 | 0 | HUGEINT | HUGEINT |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"date_day":"2025-09-05 08:00:00+08"}]</code> | <code>[{"date_day":"2025-09-05 00:00:00+08"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| B7_specified_not_read | <code>["staging.stg_asana__task (created_at, completed_at)"]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：55；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 12054 | true | false |
| 13 | run | <code>find sql -maxdepth 2 -type f -print; sed -n '240,420p' run.py; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana_start.duckdb',read_only=True)<br>print(c.execute("show tables from raw").fetchall())<br>f</code> | 7217 | true | false |
| 15 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/build.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging')<br># source columns select expressions and row filters<br>models={<br>'stg_asana__user':("</code> | 0 | false | false |
| 17 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/intermediate')<br>q={<br>'int_asana__task_story':'''SELECT s.story_id, s.created_at, s.created_by_user_id, s.story_type, s.story_text, s.targe</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/inter.py &lt;&lt;'PY'<br>q2={<br>'int_asana__project_health_indicators':'''WITH project_base AS (<br> SELECT * FROM staging.stg_asana__project WHERE project_name IS NOT NULL AND created_at IS NOT NULL<br>),</code> | 0 | false | false |
| 23 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>q={<br>'asana__user':'''SELECT u.user_id,u.user_name,u.email,COALESCE(m.number_of_open_tasks,0)::BIGINT number_of_open_tasks,COALES</code> | 0 | false | false |
| 25 | run | <code>cat &gt; /tmp/marts2.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>q={<br>'asana__project_analytics':'''WITH base AS (<br> SELECT p.project_id,p.project_name,p.team_id,t.team_name,p.owner_user_id proj</code> | 0 | false | false |
| 27 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7124 | true | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_asana__project.sql';s=open(p).read();<br>for x in ['created_at','due_date','modified_at']:<br> s=s.replace(f'TRY_CAST({x} AS TIMESTAMP)',f'CAST(TRY_STRPTIME({x}, \'%Y-%m-%</code> | 551 | true | false |
| 35 | run | <code>cat &gt; sql/marts/asana__daily_metrics.sql &lt;&lt;'SQL'<br>WITH creations AS (<br>    SELECT CAST(CAST(created_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC' AS date_day,<br>           COUNT(*)::HUGEINT AS tasks_create</code> | 328 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana.duckdb',read_only=True)<br>for sch in ['staging','intermediate','mart']:<br> print('\n',sch)<br> for (t,) in c.execute(f"select table_name from information</code> | 1027 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana.duckdb',read_only=True)<br>print(c.execute('select min(created_at),max(created_at),count(*) filter(where assignee_user_id is not null),current_date f</code> | 872 | false | false |
| 41 | run | <code>grep -R -nE ';[[:space:]]*$&#124;ref\(' sql &#124;&#124; true; python - &lt;&lt;'PY'<br>from pathlib import Path<br>expected={<br>'staging':'stg_asana__user stg_asana__team stg_asana__project stg_asana__task stg_asana__section stg</code> | 105 | false | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
'asana__daily_metrics':'''WITH daily AS (
```
event 35 / message

```text
Running command: cat > sql/marts/asana__daily_metrics.sql <<'SQL'
```
event 41 / message

```text
'marts':'asana__user asana__team asana__tag asana__project asana__task asana__daily_metrics asana__user_performance_dashboard asana__project_analytics asana__team_efficiency_metrics asana__task_lifecycle_analysis'.split()}
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-008.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__daily_metrics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/marts/asana__daily_metrics.sql`
- S6: `records/006_contract_impl-008.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/result.md`
- S10: `data/021_packages_work/021_impl-008_asana__daily_metrics/021_impl-008_asana__daily_metrics.json`
- S11: `data/005_cs_work/impl-008/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/asana.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions`
