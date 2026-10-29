# impl-008 | intermediate | int_asana__task_projects | 差异：S1；日期 原记录

## 契约完整原文

S3:775–799

```yaml
    - name: int_asana__task_projects
      description: Task-project relationships with aggregated project IDs, names, and sections
      grain: One row per task_id
      source_models:
      - staging.stg_asana__project_task
      - staging.stg_asana__project
      - staging.stg_asana__task_section
      - staging.stg_asana__section
      business_logic: 'Build task-project relationships and aggregates: - Start from staging.stg_asana__project_task (project_task). - Left join staging.stg_asana__project (project) on project_id after casting project_task.project_id to VARCHAR to match project.project_id; retain rows when the project is missing. - Left join staging.stg_asana__task_section (task_section) on task_id after casting both sides to VARCHAR; this can multiply project rows for tasks with multiple sections. - Left join staging.stg_asana__section (section) on section_id after casting task_section.section_id to VARCHAR; set section_name to "(no section)" when missing. - Produce task_projects_base with task_id, project_id, project_name, section_name. - Aggregate by task_id to form the output: - project_ids: concatenate all non-NULL project_id values using ", ", ordered ascending by project_id; duplicates are kept; if there are no non-NULL values the result is NULL; casing and whitespace are preserved. - project_names: concatenate all non-NULL project_name values using ", ", ordered ascending by project_name; duplicates are kept; if there are no non-NULL values the result is NULL; casing and whitespace are preserved. - projects_sections: for each row, create "project_name (section_name)" using "(no section)" when section is missing; exclude rows where project_name is NULL; concatenate using ", ", ordered ascending by project_name; duplicates are kept; if there are no non-NULL pairs the result is NULL; casing and whitespace are preserved. - number_of_projects: count distinct project_id values per task_id; NULL project_id is excluded; duplicates caused by multiple sections do not increase the count. - Output includes only task_ids present in project_task.'
      columns:
      - name: task_id
        data_type: BIGINT
        description: Unique task identifier; exactly one output row per task_id
      - name: project_ids
        data_type: VARCHAR
        description: Comma + space separated project_id values ordered ascending by project_id; duplicates kept; NULL project_id excluded; if none → NULL; casing/whitespace preserved
      - name: project_names
        data_type: VARCHAR
        description: Comma + space separated project_name values ordered ascending by project_name; duplicates kept; NULL names excluded; if none → NULL; casing/whitespace preserved
      - name: projects_sections
        data_type: VARCHAR
        description: Comma + space separated 'project_name (section_name)' pairs ordered ascending by project_name; section_name uses '(no section)' when missing; pairs with NULL project_name excluded; duplicates kept; if none → NULL; casing/whitespace preserved
      - name: number_of_projects
        data_type: BIGINT
        description: Distinct count of project_id per task_id; NULL project_id excluded; duplicates from multiple sections do not increase the count
```

## agent 最终 SQL

S4

```sql
WITH task_projects_base AS (
 SELECT pt.task_id, p.project_id, p.project_name, COALESCE(s.section_name, '(no section)') AS section_name
 FROM staging.stg_asana__project_task pt
 LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR = p.project_id
 LEFT JOIN staging.stg_asana__task_section ts ON pt.task_id::VARCHAR = ts.task_id::VARCHAR
 LEFT JOIN staging.stg_asana__section s ON ts.section_id::VARCHAR = s.section_id
)
SELECT task_id, STRING_AGG(project_id, ', ' ORDER BY project_id) AS project_ids,
       STRING_AGG(project_name, ', ' ORDER BY project_name) AS project_names,
       STRING_AGG(project_name || ' (' || section_name || ')', ', ' ORDER BY project_name) FILTER (WHERE project_name IS NOT NULL) AS projects_sections,
       COUNT(DISTINCT project_id)::BIGINT AS number_of_projects
FROM task_projects_base GROUP BY task_id
```

## gold SQL（仅供定位差异）

S5

```sql
with project_task as (
    select * 
    from staging.stg_asana__project_task
),

project as (
    select *
    from staging.stg_asana__project
),

task_section as (
    select * 
    from staging.stg_asana__task_section
),

section as (
    select *
    from staging.stg_asana__section
),

task_projects_base as (
    select
        project_task.task_id,
        project_task.project_id,
        project.project_name,
        coalesce(section.section_name, '(no section)') as section_name
    from project_task
    left join project 
        on cast(project_task.project_id as varchar) = project.project_id
    left join task_section 
        on cast(project_task.task_id as varchar) = cast(task_section.task_id as varchar)
    left join section 
        on cast(task_section.section_id as varchar) = section.section_id
),

task_projects as (
    select
        task_id,
        string_agg(project_id, ', ' order by project_id) as project_ids,
        string_agg(project_name, ', ' order by project_name) as project_names,
        string_agg(project_name || ' (' || section_name || ')', ', ' order by project_name) as projects_sections,
        count(distinct project_id) as number_of_projects
    from task_projects_base
    group by 1
)

select * from task_projects
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 3000 | 3000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"task_id":"1080152928806"}</code> |
| K2 | <code>{"task_id":"1270649233742"}</code> |
| K3 | <code>{"task_id":"1297506264186"}</code> |
| K4 | <code>{"task_id":"1035448413397"}</code> |
| K5 | <code>{"task_id":"1089889808217"}</code> |
| K6 | <code>{"task_id":"1167313861402"}</code> |
| K7 | <code>{"task_id":"1330379355764"}</code> |
| K8 | <code>{"task_id":"1377982649407"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| task_id | 0 | 0 | 0 | BIGINT | BIGINT |
| project_ids | 122 | 122 | 122 | VARCHAR | VARCHAR |
| project_names | 0 | 0 | 0 | VARCHAR | VARCHAR |
| projects_sections | 79 | 79 | 79 | VARCHAR | VARCHAR |
| number_of_projects | 44 | 44 | 44 | BIGINT | BIGINT |

project_ids 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 4309758137882, 945437615856 | 945437615856, 4309758137882 |
| K2 | 3273909936148, 3273909936148, 6159614827449, 6159614827449, 642933064381, 642933064381, 9725287060500, 9725287060500 | 642933064381, 642933064381, 3273909936148, 3273909936148, 6159614827449, 6159614827449, 9725287060500, 9725287060500 |
| K3 | null | 8742785114493 |

projects_sections 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | Website Redesign 5 (To Do), Website Redesign 5 (Planning) | Website Redesign 5 (Planning), Website Redesign 5 (To Do) |
| K5 | Quality Assurance 3 (Bug Fixes), Quality Assurance 3 (Backlog), Quality Assurance 3 (Bug Fixes), Quality Assurance 3 (Bug Fixes) | Quality Assurance 3 (Bug Fixes), Quality Assurance 3 (Bug Fixes), Quality Assurance 3 (Backlog), Quality Assurance 3 (Bug Fixes) |
| K6 | Marketing Automation 21 (Backlog), Marketing Automation 21 ((no section)), Performance Optimization 30 (Backlog), Performance Optimization 30 ((no section)) | Marketing Automation 21 ((no section)), Marketing Automation 21 (Backlog), Performance Optimization 30 (Backlog), Performance Optimization 30 ((no section)) |

number_of_projects 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | 0 | 1 |
| K7 | 1 | 2 |
| K8 | 0 | 1 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| D10_keyword_in_any_result_field | <code>命中数=5；task_instruction_not_agent_report         description: Project names aggregation from int_asana__task_projects; null when none.</code> |

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
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana.duckdb',read_only=True)<br>for sch in ['staging','intermediate','mart']:<br> print('\n',sch)<br> for (t,) in c.execute(f"select table_name from information</code> | 1027 | true | false |
| 41 | run | <code>grep -R -nE ';[[:space:]]*$&#124;ref\(' sql &#124;&#124; true; python - &lt;&lt;'PY'<br>from pathlib import Path<br>expected={<br>'staging':'stg_asana__user stg_asana__team stg_asana__project stg_asana__task stg_asana__section stg</code> | 105 | false | false |

### agent action 的 thought/message 命中原句

event 17 / message

```text
'int_asana__task_projects':'''WITH task_projects_base AS (
```
event 23 / message

```text
LEFT JOIN intermediate.int_asana__task_projects p ON t.task_id::BIGINT=p.task_id
```
event 41 / message

```text
'intermediate':'int_asana__task_story int_asana__task_assignee int_asana__task_open_length int_asana__task_comments int_asana__task_followers int_asana__task_tags int_asana__task_first_modifier int_asana__subtask_parent int_asana__task_projects int_asana__project_task_metrics int_asana__project_user int_asana__user_task_metrics int_asana__task_performance_metrics int_asana__user_productivity_trends int_asana__project_health_indicators'.split(),
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-008.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`
- S6: `records/006_contract_impl-008.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/result.md`
- S10: `records/012_packages/012_impl-008_intermediate_int_asana__task_projects.json`
- S11: `data/005_cs_work/impl-008/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/asana.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions`
