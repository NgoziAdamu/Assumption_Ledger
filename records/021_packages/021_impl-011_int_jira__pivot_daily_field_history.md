# impl-011 | intermediate | int_jira__pivot_daily_field_history | 差异：S1；日期 原记录

## 契约完整原文

S3:1716–1753

```yaml
    - name: int_jira__pivot_daily_field_history
      description: Daily pivot of latest status, sprint, story points, and story point estimate per issue on days with changes
      grain: One row per issue_id per valid_starting_on (only days with a change in any pivoted field)
      source_models:
      - intermediate.int_jira__issue_field_history
      - intermediate.int_jira__issue_multiselect_history
      business_logic: '- Read single-value field changes from intermediate.int_jira__issue_field_history and multiselect field changes from intermediate.int_jira__issue_multiselect_history. - For multiselect changes, aggregate all values per (field_id, field_name, issue_id, updated_at) into one string joined by ", "; duplicates are preserved; NULL inputs are excluded; no ordering is enforced in the concatenation. - Union the aggregated multiselect changes with the single-value changes. - For each issue and field, each change timestamp starts a validity period that lasts until the next change; also derive the calendar date of the start. - Keep only relevant fields: status by field_id (case-insensitive), and sprint, story points, story point estimate by field_name (case-insensitive). - For each issue, field, and calendar date, retain the last change of that day (the highest change timestamp for that day; no tie-breaker beyond timestamp). - Replace a NULL field value with the literal "is_null"; otherwise keep the original text (including any comma-joined multiselect values). - Pivot to columns: status from field_id; sprint, story points, and story point estimate from field_name. Group by issue and date, and carry the week-start of the selected change timestamp. Use max as a pass-through since there is at most one selected value per field per day. - Output includes only dates where at least one relevant field changed for the issue. Unchanged fields on that date remain NULL; fields changed to true NULL appear as "is_null". - Compute issue_day_id as the MD5 of valid_starting_on concatenated with issue_id, with no delimiter.'
      columns:
      - name: valid_starting_on
        data_type: DATE
        description: Calendar date on which the day's selected field updates became valid
        tests:
        - not_null
      - name: issue_id
        data_type: VARCHAR
        description: Jira issue identifier for the daily pivot row
        tests:
        - not_null
      - name: valid_starting_at_week
        data_type: DATE
        description: Week start date based on the selected change timestamp for the day
      - name: status
        data_type: VARCHAR
        description: Latest status recorded that day; 'is_null' if the latest status was NULL; otherwise NULL when status did not change that day
      - name: sprint
        data_type: VARCHAR
        description: Latest sprint value(s) recorded that day as a comma-separated list; 'is_null' if the latest sprint was NULL; otherwise NULL when sprint did not change that day
      - name: story_points
        data_type: VARCHAR
        description: Latest 'story points' recorded that day; 'is_null' if the latest value was NULL; otherwise NULL when it did not change that day
      - name: story_point_estimate
        data_type: VARCHAR
        description: Latest 'story point estimate' recorded that day; 'is_null' if the latest value was NULL; otherwise NULL when it did not change that day
      - name: issue_day_id
        data_type: VARCHAR
        description: MD5 hash of valid_starting_on and issue_id concatenated with no delimiter
        tests:
        - not_null
```

## agent 最终 SQL

S4

```sql
with h as (select field_id,issue_id,updated_at,field_value,field_name from intermediate.int_jira__issue_field_history union all select field_id,issue_id,updated_at,string_agg(field_value,', '),field_name from intermediate.int_jira__issue_multiselect_history group by field_id,issue_id,updated_at,field_name), f as (select *,cast(updated_at as date) valid_starting_on,row_number() over(partition by issue_id,field_id,cast(updated_at as date) order by updated_at desc) rn from h where lower(field_id)='status' or lower(field_name) in ('sprint','story points','story point estimate')), p as (select issue_id,valid_starting_on,max(updated_at) valid_starting_at,max(field_value) filter(where lower(field_id)='status') status,max(field_value) filter(where lower(field_name)='sprint') sprint,max(field_value) filter(where lower(field_name)='story points') story_points,max(field_value) filter(where lower(field_name)='story point estimate') story_point_estimate from f where rn=1 group by issue_id,valid_starting_on) select valid_starting_on,issue_id,cast(date_trunc('week',valid_starting_at) as date) valid_starting_at_week,coalesce(status,'is_null') status,coalesce(sprint,'is_null') sprint,coalesce(story_points,'is_null') story_points,coalesce(story_point_estimate,'is_null') story_point_estimate,md5(cast(valid_starting_on as varchar)||issue_id) issue_day_id from p
```

## gold SQL（仅供定位差异）

S5

```sql
-- Note: This file has been converted from dbt format to DuckDB compatible SQL
-- Original used incremental models and dynamic field configuration. This version uses standard table logic
-- and includes common Jira fields. You may need to adjust based on your specific requirements.

-- issue_multiselect_history splits out an array-type field into multiple rows with unique individual values
-- to combine with issue_field_history we need to aggregate the multiselect field values.

with issue_field_history as (

    select *
    from intermediate.int_jira__issue_field_history

),

issue_multiselect_history as (

    select *
    from intermediate.int_jira__issue_multiselect_history

),

issue_multiselect_batch_history as (

    select 
        field_id,
        field_name,
        issue_id,
        updated_at,
        date_trunc('day', updated_at)::date as date_day,

        -- if the field refers to an object captured in a table elsewhere (ie sprint, users, field_option for custom fields),
        -- the value is actually a foreign key to that table. 
        string_agg(field_value, ', ') as field_values 

    from issue_multiselect_history

    group by 1, 2, 3, 4, 5
),

combine_field_history as (
-- combining all the field histories together
    select 
        field_id,
        issue_id,
        updated_at,
        field_value,
        field_name

    from issue_field_history

    union all

    select 
        field_id,
        issue_id,
        updated_at,
        field_values as field_value, -- this is an aggregated list but we'll just call it field_value
        field_name

    from issue_multiselect_batch_history
),

get_valid_dates as (

    select 
        field_id,
        issue_id,
        field_value,
        field_name,
        updated_at as valid_starting_at,

        -- this value is valid until the next value is updated
        lead(updated_at, 1) over(partition by issue_id, field_id order by updated_at asc) as valid_ending_at, 
        date_trunc('day', updated_at)::date as valid_starting_on

    from combine_field_history
),

limit_to_relevant_fields as (
    -- let's remove unncessary rows moving forward and grab field names 
    select 
        get_valid_dates.*

    from get_valid_dates

    where lower(field_id) = 'status'
        or lower(field_name) in ('sprint', 'story points', 'story point estimate')
),

order_daily_values as (

    select 
        *,
        -- want to grab last value for an issue's field for each day
        row_number() over (
            partition by valid_starting_on, issue_id, field_id
            order by valid_starting_at desc
            ) as row_num

    from limit_to_relevant_fields
),

-- only looking at the latest value for each day
get_latest_daily_value as (

    select * 

    from order_daily_values
    where row_num = 1
), 

int_jira__daily_field_history as (

    select
        field_id,
        issue_id,
        field_name,

        -- doing this to figure out what values are actually null and what needs to be backfilled in jira__daily_issue_field_history
        case when field_value is null then 'is_null' else field_value end as field_value,
        valid_starting_at,
        valid_ending_at, 
        valid_starting_on

    from get_latest_daily_value
),

pivot_out as (

    -- pivot out default columns (status and sprint) and others specified
    -- only days on which a field value was actively changed will have a non-null value. the nulls will need to 
    -- be backfilled in the final jira__daily_issue_field_history model
    select 
        valid_starting_on,
        issue_id,
        date_trunc('week', valid_starting_at)::date as valid_starting_at_week,
        max(case when lower(field_id) = 'status' then field_value end) as status,
        max(case when lower(field_name) = 'sprint' then field_value end) as sprint,
        max(case when lower(field_name) = 'story points' then field_value end) as story_points,
        max(case when lower(field_name) = 'story point estimate' then field_value end) as story_point_estimate

    from int_jira__daily_field_history

    group by 1, 2, 3
),

final as (
    select 
        *,
        md5(valid_starting_on::varchar || issue_id::varchar) as issue_day_id

    from pivot_out
)

select *
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 9755 | 9755 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"issue_id":"iss10000140937","issue_day_id":"08a17465b63dc7835279c894ea253873"}</code> |
| K2 | <code>{"issue_id":"iss10000140937","issue_day_id":"98df19704905f8d3c3860bf19dc6fc88"}</code> |
| K3 | <code>{"issue_id":"iss10003041400","issue_day_id":"cb9713a528fef27b51c7b8a2e99a657c"}</code> |
| K4 | <code>{"issue_id":"iss10011664312","issue_day_id":"211c84d4ee5fde2d1156f69e292348e6"}</code> |
| K5 | <code>{"issue_id":"iss10016662655","issue_day_id":"1a682ad873b3c55e47120eba94a0226f"}</code> |
| K6 | <code>{"issue_id":"iss10011664312","issue_day_id":"a603929a851ac103056a2ea24b097004"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| valid_starting_on | 0 | 0 | 0 | DATE | DATE |
| issue_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 9738 | 9738 | 9738 | VARCHAR | VARCHAR |
| sprint | 2025 | 2025 | 2025 | VARCHAR | VARCHAR |
| story_points | 7746 | 7746 | 7746 | VARCHAR | VARCHAR |
| story_point_estimate | 9755 | 9755 | 9755 | VARCHAR | VARCHAR |

status 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | is_null | null |
| K2 | is_null | null |
| K3 | is_null | null |

sprint 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | is_null | null |
| K4 | is_null | null |
| K5 | is_null | null |

story_points 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | is_null | null |
| K2 | is_null | null |
| K6 | is_null | null |

story_point_estimate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | is_null | null |
| K2 | is_null | null |
| K3 | is_null | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"story_point_estimate","value":"is_null"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'int_jira__pivot_daily_field_history':"with h as (select field_id,issue_id,updated_at,field_value,field_name from intermediate.int_jira__issue_field_history union all select field_id,issue_id,updated_at,string_agg(field_value,', '),field_name from intermediate.int_jira__issue_multiselect_history group by field_id,issue_id,updated_at,field_name), f as (select *,cast(updated_at as date) valid_starting_on,row_number() over(partition by issue_id,field_id,cast(updated_at as date) order by updated_at desc) rn from h where lower(field_id)='status' or lower(field_name) in ('sprint','story points','story point estimate')), p as (select issue_id,valid_starting_on,max(updated_at) valid_starting_at,max(field_value) filter(where lower(field_id)='status') status,max(field_value) filter(where lower(field_name)='sprint') sprint,max(field_value) filter(where lower(field_name)='story points') story_points,max(field_value) filter(where lower(field_name)='story point estimate') story_point_estimate from f where rn=1 group by issue_id,valid_starting_on) select valid_starting_on,issue_id,cast(date_trunc('week',valid_starting_at) as date) valid_starting_at_week,coalesce(status,'is_null') status,coalesce(sprint,'is_null') sprint,coalesce(story_points,'is_null') story_points,coalesce(story_point_estimate,'is_null') story_point_estimate,md5(cast(valid_starting_on as varchar)&#124;&#124;issue_id) issue_day_id from p",</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,240p' run.py</code> | 14395 | true | false |
| 13 | run | <code>cat &gt; /tmp/gen_inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/intermediate')<br>Q={<br>'int_jira__issue_field_history':"select h.field_id,h.issue_id,h.updated_at,h.field_value,h.is_active,lower(f.fiel</code> | 0 | false | false |
| 15 | run | <code>cat &gt;&gt; /tmp/gen_inter.py &lt;&lt;'PY'<br>Q.update({<br>'int_jira__pivot_daily_field_history':"with h as (select field_id,issue_id,updated_at,field_value,field_name from intermediate.int_jira__issue_field_history </code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen_marts.py &lt;&lt;'PY'<br>Q.update({<br>'jira__stakeholder_engagement_insights':"with active as (select * from staging.stg_jira__user where is_active=true), acts as (select user_id,count(distinct i</code> | 6630 | true | false |
| 23 | run | <code>grep -E 'WARNING -  ⏭&#124;WARNING -   ⏭&#124;Catalog Error&#124;Binder Error&#124;Parser Error&#124;Conversion Error' /tmp/runlog &#124; head -80</code> | 8767 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_jira__issue_type.sql';s=open(p).read().replace('is_subtask from','subtask as is_subtask from');open(p,'w').write(s)<br>p='sql/intermediate/int_jira__issue_versions.sql'</code> | 995 | false | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> s=re.sub(r'try_cast\((\w+) as timestamp\)',r"try_cast(regexp_replace(\1, '([+-][0-9]{2}</code> | 9550 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text().replace("regexp_replace(created, '([+-][0-9]{2})([0-9]{2})$', '\\\\1:\\\\2')", "regexp_replace(cre</code> | 4200 | true | false |

### agent action 的 thought/message 命中原句

event 15 / message

```text
'int_jira__pivot_daily_field_history':"with h as (select field_id,issue_id,updated_at,field_value,field_name from intermediate.int_jira__issue_field_history union all select field_id,issue_id,updated_at,string_agg(field_value,', '),field_name from intermediate.int_jira__issue_multiselect_history group by field_id,issue_id,updated_at,field_name), f as (select *,cast(updated_at as date) valid_starting_on,row_number() over(partition by issue_id,field_id,cast(updated_at as date) order by updated_at desc) rn from h where lower(field_id)='status' or lower(field_name) in ('sprint','story points','story point estimate')), p as (select issue_id,valid_starting_on,max(updated_at) valid_starting_at,max(field_value) filter(where lower(field_id)='status') status,max(field_value) filter(where lower(field_name)='sprint') sprint,max(field_value) filter(where lower(field_name)='story points') story_points,max(field_value) filter(where lower(field_name)='story point estimate') story_point_estimate from f where rn=1 group by issue_id,valid_starting_on) select valid_starting_on,issue_id,cast(date_trunc('week',valid_starting_at) as date) valid_starting_at_week,coalesce(status,'is_null') status,coalesce(sprint,'is_null') sprint,coalesce(story_points,'is_null') story_points,coalesce(story_point_estimate,'is_null') story_point_estimate,md5(cast(valid_starting_on as varchar)||issue_id) issue_day_id from p",
```
event 15 / message

```text
'int_jira__field_history_scd':"with d as (select *,count(status) over(partition by issue_id order by valid_starting_on rows unbounded preceding) gs,count(sprint) over(partition by issue_id order by valid_starting_on rows unbounded preceding) gp,count(story_points) over(partition by issue_id order by valid_starting_on rows unbounded preceding) gsp,count(story_point_estimate) over(partition by issue_id order by valid_starting_on rows unbounded preceding) gse from intermediate.int_jira__pivot_daily_field_history) select valid_starting_on,issue_id,issue_day_id,first(status) over(partition by issue_id,gs order by valid_starting_on rows unbounded preceding) status_id,first(sprint) over(partition by issue_id,gp order by valid_starting_on rows unbounded preceding) sprint,first(story_points) over(partition by issue_id,gsp order by valid_starting_on rows unbounded preceding) story_points,first(story_point_estimate) over(partition by issue_id,gse order by valid_starting_on rows unbounded preceding) story_point_estimate from d",
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-011.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/intermediate/field_history/int_jira__pivot_daily_field_history.sql`
- S6: `records/006_contract_impl-011.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/result.md`
- S10: `data/021_packages_work/021_impl-011_int_jira__pivot_daily_field_history/021_impl-011_int_jira__pivot_daily_field_history.json`
- S11: `data/005_cs_work/impl-011_retry_02/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/jira.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions`
