# impl-011 | intermediate | int_jira__issue_users | 差异：S1；日期 原记录

## 契约完整原文

S3:1559–1695

```yaml
    - name: int_jira__issue_users
      description: Issue records from int_jira__issue_type_parents enriched with assignee and reporter attributes; parent_issue_id is derived from revised_parent_issue_id or parent_issue_id
      grain: One row per issue; may produce multiple rows per issue if the user table has duplicate user_id entries
      source_models:
      - intermediate.int_jira__issue_type_parents
      - staging.stg_jira__user
      business_logic: '- Start with all columns from intermediate.int_jira__issue_type_parents. - Derive parent_issue_id by taking revised_parent_issue_id when present; otherwise use the original parent_issue_id; both are treated as text, and the result is null if both are missing. - Keep all source columns unchanged; because issue_id is also selected explicitly, the output includes duplicate source versions named issue_id_1 and parent_issue_id_1. - Join the user table twice using left joins: on assignee_user_id to add assignee_name, assignee_timezone, assignee_email; on reporter_user_id to add reporter_email, reporter_name, reporter_timezone. - No filters, aggregation, or ordering are applied. All issues are retained; unmatched users yield null attributes. If the user table has multiple rows for a user_id, the result may have multiple rows per issue (no de-duplication).'
      columns:
      - name: issue_id
        data_type: VARCHAR
        description: Issue identifier selected explicitly from the source
        tests:
        - not_null
      - name: parent_issue_id
        data_type: VARCHAR
        description: 'Derived parent identifier: use revised_parent_issue_id when present, otherwise the original parent_issue_id; stored as text; null if both are missing'
      - name: original_estimate_seconds
        data_type: DOUBLE
        description: Original time estimate in seconds from the source
        tests:
        - original_estimate_seconds IS NULL OR original_estimate_seconds >= 0
      - name: remaining_estimate_seconds
        data_type: DOUBLE
        description: Remaining time estimate in seconds from the source
        tests:
        - remaining_estimate_seconds IS NULL OR remaining_estimate_seconds >= 0
      - name: time_spent_seconds
        data_type: DOUBLE
        description: Time spent in seconds from the source
        tests:
        - time_spent_seconds IS NULL OR time_spent_seconds >= 0
      - name: assignee_user_id
        data_type: VARCHAR
        description: Assignee user identifier from the source used to join user attributes
      - name: created_at
        data_type: TIMESTAMP
        description: Issue creation timestamp from the source
        tests:
        - not_null
      - name: resolved_at
        data_type: TIMESTAMP
        description: Issue resolution timestamp from the source; may be null
      - name: creator_user_id
        data_type: VARCHAR
        description: Creator user identifier from the source
      - name: issue_description
        data_type: VARCHAR
        description: Issue description text from the source
      - name: due_date
        data_type: VARCHAR
        description: Due date as stored in the source text; no parsing or conversion
      - name: environment
        data_type: VARCHAR
        description: Environment field from the source
      - name: issue_id_1
        data_type: VARCHAR
        description: Duplicate of the original issue_id retained when all source columns are included
      - name: issue_type_id
        data_type: VARCHAR
        description: Issue type identifier from the source
      - name: issue_key
        data_type: VARCHAR
        description: Human-readable issue key from the source
        tests:
        - not_null
      - name: parent_issue_id_1
        data_type: VARCHAR
        description: Original parent_issue_id from the source retained alongside the derived parent_issue_id
      - name: priority_id
        data_type: VARCHAR
        description: Priority identifier from the source
      - name: project_id
        data_type: VARCHAR
        description: Project identifier from the source
        tests:
        - not_null
      - name: reporter_user_id
        data_type: VARCHAR
        description: Reporter user identifier from the source used to join user attributes
      - name: resolution_id
        data_type: VARCHAR
        description: Resolution identifier from the source
      - name: status_id
        data_type: VARCHAR
        description: Status identifier from the source
      - name: status_changed_at
        data_type: TIMESTAMP
        description: Timestamp of the last status change from the source
      - name: issue_name
        data_type: VARCHAR
        description: Issue summary or title from the source
      - name: updated_at
        data_type: TIMESTAMP
        description: Last update timestamp from the source
        tests:
        - not_null
      - name: work_ratio
        data_type: DOUBLE
        description: Work completion ratio from the source
        tests:
        - work_ratio IS NULL OR work_ratio >= 0
      - name: revised_parent_issue_id
        data_type: VARCHAR
        description: Revised parent issue identifier used to derive parent_issue_id
      - name: issue_type
        data_type: VARCHAR
        description: Issue type name from the source
      - name: parent_issue_type
        data_type: VARCHAR
        description: Parent issue type name from the source
      - name: parent_issue_name
        data_type: VARCHAR
        description: Parent issue name from the source
      - name: parent_issue_key
        data_type: VARCHAR
        description: Parent issue key from the source
      - name: is_parent_epic
        data_type: BOOLEAN
        description: Indicates whether the parent issue is an epic, as provided by the source
      - name: assignee_name
        data_type: VARCHAR
        description: Assignee display name from the user table; null if no matching user
      - name: assignee_timezone
        data_type: VARCHAR
        description: Assignee time zone from the user table; null if no matching user
      - name: assignee_email
        data_type: VARCHAR
        description: Assignee email from the user table; null if no matching user
      - name: reporter_email
        data_type: VARCHAR
        description: Reporter email from the user table; null if no matching user
      - name: reporter_name
        data_type: VARCHAR
        description: Reporter display name from the user table; null if no matching user
      - name: reporter_timezone
        data_type: VARCHAR
        description: Reporter time zone from the user table; null if no matching user
```

## agent 最终 SQL

S4

```sql
select i.*,coalesce(i.revised_parent_issue_id,i.parent_issue_id) parent_issue_id_derived,a.user_display_name assignee_name,a.time_zone assignee_timezone,a.email assignee_email,r.email reporter_email,r.user_display_name reporter_name,r.time_zone reporter_timezone from intermediate.int_jira__issue_type_parents i left join staging.stg_jira__user a on i.assignee_user_id=a.user_id left join staging.stg_jira__user r on i.reporter_user_id=r.user_id
```

## gold SQL（仅供定位差异）

S5

```sql
-- just grabs user attributes for issue assignees and reporters 

with issue as (

    select
        issue_id,
        coalesce(cast(revised_parent_issue_id as varchar), cast(parent_issue_id as varchar)) as parent_issue_id,
        -- Get all columns from int_jira__issue_type_parents
        *

    from intermediate.int_jira__issue_type_parents
),

-- user is a reserved keyword in AWS
jira_user as (

    select *
    from staging.stg_jira__user
),

issue_user_join as (

    select
        issue.*,
        assignee.user_display_name as assignee_name,
        assignee.time_zone as assignee_timezone,
        assignee.email as assignee_email,
        reporter.email as reporter_email,
        reporter.user_display_name as reporter_name,
        reporter.time_zone as reporter_timezone
    from issue
    left join jira_user as assignee 
        on issue.assignee_user_id = assignee.user_id 
    left join jira_user as reporter 
        on issue.reporter_user_id = reporter.user_id
)

select * 
from issue_user_join
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 8000 | 8000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"issue_id":"iss17351159434","project_id":"pro23776881491"}</code> |
| K2 | <code>{"issue_id":"iss17931452884","project_id":"pro32285371102"}</code> |
| K3 | <code>{"issue_id":"iss24940795322","project_id":"pro34223569346"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| issue_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| parent_issue_id | 13 | 13 | 13 | VARCHAR | VARCHAR |
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
| due_date | 0 | 0 | 0 | VARCHAR | VARCHAR |
| environment | 0 | 0 | 0 | VARCHAR | VARCHAR |
| original_estimate_seconds | 0 | 0 | 0 | DOUBLE | DOUBLE |
| remaining_estimate_seconds | 0 | 0 | 0 | DOUBLE | DOUBLE |
| time_spent_seconds | 0 | 0 | 0 | DOUBLE | DOUBLE |
| work_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |
| assignee_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| assignee_timezone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| assignee_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| reporter_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| reporter_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| reporter_timezone | 0 | 0 | 0 | VARCHAR | VARCHAR |

parent_issue_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | Updated field value 897 |
| K2 | null | Updated field value 685 |
| K3 | null | Updated field value 815 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A4_equal_columns | <code>1组；[{"columns":["revised_parent_issue_id","parent_issue_id_derived"],"nonnull_equal_rows":794,"meaning_status":"契约未描述含义差别"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'int_jira__issue_join':"select iu.*,p.project_name,s.status_name current_status,sc.status_category_name current_status_category,r.resolution_name resolution_type,pr.priority_name current_priority,sp.current_sprint_id,sp.current_sprint_name,coalesce(sp.count_sprint_changes,0)::integer count_sprint_changes,sp.sprint_started_at,sp.sprint_ended_at,sp.sprint_completed_at,(sp.sprint_started_at&lt;=current_timestamp and (sp.sprint_completed_at is null or sp.sprint_completed_at&gt;=current_timestamp)) is_active_sprint,ar.first_assigned_at,ar.last_assigned_at,ar.first_resolved_at,v.fixes_versions,v.affects_versions,c.conversation,coalesce(c.count_comments,0)::bigint count_comments from intermediate.int_jira__issue_users iu left join staging.stg_jira__project p using(project_id) left join staging.stg_jira__status s using(status_id) left join staging.stg_jira__status_category sc on cast(s.status_category_id as varchar)=cast(sc.status_category_id as varchar) left join staging.stg_jira__resolution r using(resolution_id) left join staging.stg_jira__priority pr using(priority_id) left join intermediate.int_jira__issue_sprint sp using(issue_id) left join intermediate.int_jira__issue_assign_resolution ar using(issue_id) left join intermediate.int_jira__issue_versions v using(issue_id) left join intermediate.int_jira__issue_comments c using(issue_id)",</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,240p' run.py</code> | 14395 | true | false |
| 11 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging')<br>queries={<br>'stg_jira__user':"""select cast(id as varchar) user_id, coalesce(nu</code> | 0 | false | false |
| 13 | run | <code>cat &gt; /tmp/gen_inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/intermediate')<br>Q={<br>'int_jira__issue_field_history':"select h.field_id,h.issue_id,h.updated_at,h.field_value,h.is_active,lower(f.fiel</code> | 0 | false | false |
| 17 | run | <code>cat &gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>Q={<br>'jira__daily_issue_field_history':"select cast(i.created_at as date) date_day,cast(i.created_at as date) date_week,i.iss</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>Q.update({<br>'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i</code> | 6630 | false | false |
| 23 | run | <code>grep -E 'WARNING -  ⏭&#124;WARNING -   ⏭&#124;Catalog Error&#124;Binder Error&#124;Parser Error&#124;Conversion Error' /tmp/runlog &#124; head -80</code> | 8767 | true | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> s=re.sub(r'try_cast\((\w+) as timestamp\)',r"try_cast(regexp_replace(\1, '([+-][0-9]{2}</code> | 9550 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text().replace("regexp_replace(created, '([+-][0-9]{2})([0-9]{2})$', '\\\\1:\\\\2')", "regexp_replace(cre</code> | 4200 | true | false |
| 41 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; grep -E 'INTERMEDIATE Layer&#124;✓ intermediate.int_jira__issue_join&#124;✓ intermediate.int_jira__issue_users&#124;staging.stg_jira__issue:' /tmp/runlog3</code> | 836 | true | false |
| 43 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; cat sql/intermediate/int_jira__issue_calendar_spine.sql</code> | 1202 | false | false |

### agent action 的 thought/message 命中原句

event 13 / message

```text
'int_jira__issue_users':"select i.*,coalesce(i.revised_parent_issue_id,i.parent_issue_id) parent_issue_id_derived,a.user_display_name assignee_name,a.time_zone assignee_timezone,a.email assignee_email,r.email reporter_email,r.user_display_name reporter_name,r.time_zone reporter_timezone from intermediate.int_jira__issue_type_parents i left join staging.stg_jira__user a on i.assignee_user_id=a.user_id left join staging.stg_jira__user r on i.reporter_user_id=r.user_id",
```
event 13 / message

```text
'int_jira__issue_join':"select iu.*,p.project_name,s.status_name current_status,sc.status_category_name current_status_category,r.resolution_name resolution_type,pr.priority_name current_priority,sp.current_sprint_id,sp.current_sprint_name,coalesce(sp.count_sprint_changes,0)::integer count_sprint_changes,sp.sprint_started_at,sp.sprint_ended_at,sp.sprint_completed_at,(sp.sprint_started_at<=current_timestamp and (sp.sprint_completed_at is null or sp.sprint_completed_at>=current_timestamp)) is_active_sprint,ar.first_assigned_at,ar.last_assigned_at,ar.first_resolved_at,v.fixes_versions,v.affects_versions,c.conversation,coalesce(c.count_comments,0)::bigint count_comments from intermediate.int_jira__issue_users iu left join staging.stg_jira__project p using(project_id) left join staging.stg_jira__status s using(status_id) left join staging.stg_jira__status_category sc on cast(s.status_category_id as varchar)=cast(sc.status_category_id as varchar) left join staging.stg_jira__resolution r using(resolution_id) left join staging.stg_jira__priority pr using(priority_id) left join intermediate.int_jira__issue_sprint sp using(issue_id) left join intermediate.int_jira__issue_assign_resolution ar using(issue_id) left join intermediate.int_jira__issue_versions v using(issue_id) left join intermediate.int_jira__issue_comments c using(issue_id)",
```
event 41 / message

```text
Running command: cat sql/intermediate/int_jira__issue_users.sql; grep -E 'INTERMEDIATE Layer|✓ intermediate.int_jira__issue_join|✓ intermediate.int_jira__issue_users|staging.stg_jira__issue:' /tmp/runlog3
```
event 43 / message

```text
Running command: cat sql/intermediate/int_jira__issue_users.sql; cat sql/intermediate/int_jira__issue_calendar_spine.sql
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-011.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_users.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/intermediate/int_jira__issue_users.sql`
- S6: `records/006_contract_impl-011.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/result.md`
- S10: `data/021_packages_work/021_impl-011_int_jira__issue_users/021_impl-011_int_jira__issue_users.json`
- S11: `data/005_cs_work/impl-011_retry_02/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/jira.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions`
