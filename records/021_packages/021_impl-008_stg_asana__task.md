# impl-008 | staging | stg_asana__task | 差异：S1；日期 原记录

## 契约完整原文

S3:117–151

```yaml
    - name: stg_asana__task
      description: "Standardized task entities with validated completion status, dates, and assignment relationships. Uses robust parsing and pattern checks to exclude rows where modified_at is clearly non-date text; other non-parsable date fields are set to NULL."
      source_table: "raw.task_data"
      columns:
        - name: task_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: assignee_user_id
          data_type: BIGINT
        - name: is_completed
          data_type: BOOLEAN
          constraints: [not_null]
        - name: completed_at
          data_type: TIMESTAMP
        - name: completed_by_user_id
          data_type: BIGINT
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: due_date
          data_type: TIMESTAMP
        - name: modified_at
          data_type: TIMESTAMP
        - name: task_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: parent_task_id
          data_type: BIGINT
        - name: start_date
          data_type: TIMESTAMP
        - name: task_description
          data_type: VARCHAR
        - name: workspace_id
          data_type: BIGINT

```

## agent 最终 SQL

S4

```sql
WITH cleaned AS (
    SELECT CAST(id AS VARCHAR) task_id, TRY_CAST(assignee_id AS BIGINT) assignee_user_id, COALESCE(completed,FALSE) is_completed, CAST(TRY_STRPTIME(completed_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP) completed_at, TRY_CAST(completed_by_id AS BIGINT) completed_by_user_id, CAST(TRY_STRPTIME(created_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP) created_at, COALESCE(CAST(TRY_STRPTIME(due_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP), CAST(TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP)) due_date, CAST(TRY_STRPTIME(modified_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP) modified_at, name task_name, TRY_CAST(parent_id AS BIGINT) parent_task_id, CAST(TRY_STRPTIME(start_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP) start_date, notes task_description, workspace_id, ROW_NUMBER() OVER (PARTITION BY id ORDER BY id) AS _rn
    FROM raw.task_data
    WHERE id IS NOT NULL AND completed IS NOT NULL AND CAST(TRY_STRPTIME(created_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP) IS NOT NULL AND (modified_at IS NULL OR CAST(TRY_STRPTIME(modified_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP) IS NOT NULL OR regexp_matches(TRIM(modified_at), '^\d{4}-\d{2}-\d{2}'))
)
SELECT * EXCLUDE (_rn)
FROM cleaned
WHERE _rn = 1
```

## gold SQL（仅供定位差异）

S5

```sql
/*
 * Asana Task Data Processing Strategy - Robust Date Quality Version
 * Solution: Only exclude records where modified_at clearly contains text instead of dates
 * Data pipeline runs successfully while preserving majority of data
 */

SELECT
    CAST(id AS VARCHAR) AS task_id,
    CAST(assignee_id AS BIGINT) AS assignee_user_id,
    CAST(completed AS BOOLEAN) AS is_completed,
    CASE WHEN completed_at IS NOT NULL
         THEN strptime(completed_at, '%Y-%m-%d %H:%M:%S.%f %z') END AS completed_at,
    CAST(completed_by_id AS BIGINT) AS completed_by_user_id,
    strptime(created_at, '%Y-%m-%d %H:%M:%S.%f %z') AS created_at,
    CASE WHEN due_on IS NOT NULL
         THEN strptime(due_on, '%Y-%m-%d %H:%M:%S.%f %z') END AS due_date,
    CASE WHEN modified_at IS NOT NULL
           AND (modified_at LIKE '20%-%-% %:%:%' OR modified_at LIKE '202%-%-% %:%:%')
         THEN strptime(modified_at, '%Y-%m-%d %H:%M:%S.%f %z') END AS modified_at,
    name AS task_name,
    CAST(parent_id AS BIGINT) AS parent_task_id,
    CASE WHEN start_on IS NOT NULL
         THEN strptime(start_on, '%Y-%m-%d %H:%M:%S.%f %z') END AS start_date,
    CAST(notes AS VARCHAR) AS task_description,
    CAST(workspace_id AS BIGINT) AS workspace_id
FROM raw.task_data
WHERE id IS NOT NULL
  AND completed IS NOT NULL
  AND name IS NOT NULL
  -- Only exclude records where modified_at clearly doesn't match date pattern
  AND (modified_at IS NULL
       OR modified_at LIKE '20%-%-% %:%:%'
       OR modified_at LIKE '202%-%-% %:%:%')
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2986 | 2986 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"task_id":"1001301507647"}</code> |
| K2 | <code>{"task_id":"100559893763"}</code> |
| K3 | <code>{"task_id":"1008996167568"}</code> |
| K4 | <code>{"task_id":"1011440584699"}</code> |
| K5 | <code>{"task_id":"1023238231632"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| is_completed | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| due_date | 1736 | 1736 | 1736 | TIMESTAMP | TIMESTAMP WITH TIME ZONE |
| task_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| start_date | 887 | 887 | 887 | TIMESTAMP | TIMESTAMP WITH TIME ZONE |
| task_description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| workspace_id | 0 | 0 | 0 | BIGINT | BIGINT |

due_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2025-09-05 18:32:08.441 | null |
| K2 | 2025-09-05 18:34:52.256 | null |
| K3 | 2025-09-05 18:33:45.254 | null |

start_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | 2025-09-05 18:30:54.21 | 2025-09-05 18:30:54.21+08 |
| K4 | 2025-09-05 18:32:11.273 | 2025-09-05 18:32:11.273+08 |
| K5 | 2025-09-05 18:30:41.83 | 2025-09-05 18:30:41.83+08 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| D10_keyword_in_any_result_field | <code>命中数=20；task_instruction_not_agent_report         description: Current assignee user_id from stg_asana__task; may be null</code> |

## 轨迹索引（不放输出原文）

本题事件总数：55；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 12054 | true | false |
| 11 | run | cat asana_start.yaml | 1314 | false | false |
| 13 | run | <code>find sql -maxdepth 2 -type f -print; sed -n '240,420p' run.py; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana_start.duckdb',read_only=True)<br>print(c.execute("show tables from raw").fetchall())<br>f</code> | 7217 | false | false |
| 15 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/build.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging')<br># source columns select expressions and row filters<br>models={<br>'stg_asana__user':("</code> | 0 | false | false |
| 17 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/intermediate')<br>q={<br>'int_asana__task_story':'''SELECT s.story_id, s.created_at, s.created_by_user_id, s.story_type, s.story_text, s.targe</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/inter.py &lt;&lt;'PY'<br>q2={<br>'int_asana__project_health_indicators':'''WITH project_base AS (<br> SELECT * FROM staging.stg_asana__project WHERE project_name IS NOT NULL AND created_at IS NOT NULL<br>),</code> | 0 | false | false |
| 23 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>q={<br>'asana__user':'''SELECT u.user_id,u.user_name,u.email,COALESCE(m.number_of_open_tasks,0)::BIGINT number_of_open_tasks,COALES</code> | 0 | false | false |
| 25 | run | <code>cat &gt; /tmp/marts2.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>q={<br>'asana__project_analytics':'''WITH base AS (<br> SELECT p.project_id,p.project_name,p.team_id,t.team_name,p.owner_user_id proj</code> | 0 | false | false |
| 27 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7124 | true | false |
| 29 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana_start.duckdb',read_only=True)<br>for t,col in [('project_data','created_at'),('task_data','created_at'),('story_data','created_at'),('section_data','</code> | 1958 | false | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana_start.duckdb',read_only=True)<br>for fmt in ['%Y-%m-%d %H:%M:%S.%f %z','%Y-%m-%d %H:%M:%S %z','%Y-%m-%d %H:%M:%S.%f %z']:<br> try: print(fmt,c.execute(f</code> | 696 | false | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_asana__project.sql';s=open(p).read();<br>for x in ['created_at','due_date','modified_at']:<br> s=s.replace(f'TRY_CAST({x} AS TIMESTAMP)',f'CAST(TRY_STRPTIME({x}, \'%Y-%m-%</code> | 551 | false | false |
| 35 | run | <code>cat &gt; sql/marts/asana__daily_metrics.sql &lt;&lt;'SQL'<br>WITH creations AS (<br>    SELECT CAST(CAST(created_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC' AS date_day,<br>           COUNT(*)::HUGEINT AS tasks_create</code> | 328 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana.duckdb',read_only=True)<br>for sch in ['staging','intermediate','mart']:<br> print('\n',sch)<br> for (t,) in c.execute(f"select table_name from information</code> | 1027 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana.duckdb',read_only=True)<br>print(c.execute('select min(created_at),max(created_at),count(*) filter(where assignee_user_id is not null),current_date f</code> | 872 | false | false |
| 41 | run | <code>grep -R -nE ';[[:space:]]*$&#124;ref\(' sql &#124;&#124; true; python - &lt;&lt;'PY'<br>from pathlib import Path<br>expected={<br>'staging':'stg_asana__user stg_asana__team stg_asana__project stg_asana__task stg_asana__section stg</code> | 105 | false | false |

### agent action 的 thought/message 命中原句

event 15 / message

```text
'stg_asana__task':("raw.task_data","CAST(id AS VARCHAR) task_id, TRY_CAST(assignee_id AS BIGINT) assignee_user_id, COALESCE(completed,FALSE) is_completed, TRY_CAST(completed_at AS TIMESTAMP) completed_at, TRY_CAST(completed_by_id AS BIGINT) completed_by_user_id, TRY_CAST(created_at AS TIMESTAMP) created_at, COALESCE(TRY_CAST(due_at AS TIMESTAMP), TRY_CAST(due_on AS TIMESTAMP)) due_date, TRY_CAST(modified_at AS TIMESTAMP) modified_at, name task_name, TRY_CAST(parent_id AS BIGINT) parent_task_id, TRY_CAST(start_on AS TIMESTAMP) start_date, notes task_description, workspace_id", "id IS NOT NULL AND completed IS NOT NULL AND TRY_CAST(created_at AS TIMESTAMP) IS NOT NULL AND (modified_at IS NULL OR TRY_CAST(modified_at AS TIMESTAMP) IS NOT NULL OR regexp_matches(TRIM(modified_at), '^\\d{4}-\\d{2}-\\d{2}'))",'id'),
```
event 17 / message

```text
JOIN staging.stg_asana__task t ON s.target_id::VARCHAR = t.task_id
```
event 17 / message

```text
FROM staging.stg_asana__task t LEFT JOIN staging.stg_asana__user u ON t.assignee_user_id::VARCHAR = u.user_id''',
```
event 17 / message

```text
FROM staging.stg_asana__task t LEFT JOIN assignments a ON t.task_id = a.target_task_id''',
```
event 17 / message

```text
FROM staging.stg_asana__task child JOIN staging.stg_asana__task parent
```
event 17 / message

```text
 FROM staging.stg_asana__project_task pt JOIN staging.stg_asana__task t ON pt.task_id::VARCHAR=t.task_id
```
event 17 / message

```text
 FROM staging.stg_asana__project_task pt JOIN staging.stg_asana__task t ON pt.task_id::VARCHAR=t.task_id WHERE t.assignee_user_id IS NOT NULL
```
event 17 / message

```text
FROM staging.stg_asana__task t JOIN intermediate.int_asana__task_open_length ol ON t.task_id=ol.task_id
```
event 17 / message

```text
 FROM staging.stg_asana__task t LEFT JOIN intermediate.int_asana__task_open_length ol ON t.task_id=ol.task_id
```
event 21 / message

```text
 LEFT JOIN staging.stg_asana__task t ON rel.task_id::VARCHAR=t.task_id
```
event 21 / message

```text
 FROM staging.stg_asana__task t JOIN intermediate.int_asana__task_performance_metrics p ON t.task_id=p.task_id
```
event 23 / message

```text
FROM staging.stg_asana__task t JOIN intermediate.int_asana__task_open_length o ON t.task_id=o.task_id
```
event 23 / message

```text
 SELECT CAST(created_at AS DATE)::TIMESTAMPTZ date_day,COUNT(*)::HUGEINT tasks_created,0::HUGEINT tasks_completed FROM staging.stg_asana__task GROUP BY CAST(created_at AS DATE)
```
event 23 / message

```text
 UNION ALL SELECT CAST(completed_at AS DATE)::TIMESTAMPTZ,0::HUGEINT,COUNT(*)::HUGEINT FROM staging.stg_asana__task WHERE completed_at IS NOT NULL GROUP BY CAST(completed_at AS DATE)
```
event 25 / message

```text
counts AS (SELECT team_id::VARCHAR team_id,COUNT(DISTINCT assignee_user_id)::BIGINT unique_team_members,COUNT(*) FILTER(WHERE FALSE)::BIGINT zero_rows FROM staging.stg_asana__project p JOIN staging.stg_asana__project_task pt ON p.project_id=pt.project_id::VARCHAR JOIN staging.stg_asana__task t ON pt.task_id::VARCHAR=t.task_id WHERE t.assignee_user_id IS NOT NULL GROUP BY team_id)
```
event 25 / message

```text
FROM staging.stg_asana__task t LEFT JOIN intermediate.int_asana__task_performance_metrics m ON t.task_id=m.task_id LEFT JOIN story_agg s ON t.task_id=s.target_task_id WHERE t.created_at IS NOT NULL),
```
event 33 / message

```text
p='sql/staging/stg_asana__task.sql';s=open(p).read()
```
event 35 / message

```text
    FROM staging.stg_asana__task
```
event 35 / message

```text
    FROM staging.stg_asana__task
```
event 39 / message

```text
print(c.execute('select min(created_at),max(created_at),count(*) filter(where assignee_user_id is not null),current_date from staging.stg_asana__task').fetchall())
```
event 39 / message

```text
print(c.execute('select count(*) from staging.stg_asana__task t join intermediate.int_asana__task_performance_metrics p on t.task_id=p.task_id where t.created_at>=current_date-interval \'24 months\' and t.assignee_user_id is not null').fetchall())
```
event 39 / message

```text
print(c.execute('describe staging.stg_asana__task').fetchall())
```
event 41 / message

```text
'staging':'stg_asana__user stg_asana__team stg_asana__project stg_asana__task stg_asana__section stg_asana__story stg_asana__tag stg_asana__project_task stg_asana__task_follower stg_asana__task_section stg_asana__task_tag'.split(),
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-008.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/staging/stg_asana__task.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/staging/stg_asana__task.sql`
- S6: `records/006_contract_impl-008.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/result.md`
- S10: `data/021_packages_work/021_impl-008_stg_asana__task/021_impl-008_stg_asana__task.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/asana.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions`
