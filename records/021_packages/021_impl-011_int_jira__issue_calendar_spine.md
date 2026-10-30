# impl-011 | intermediate | int_jira__issue_calendar_spine | 差异：S1；日期 2025-10-13

## 契约完整原文

S3:1415–1444

```yaml
    - name: int_jira__issue_calendar_spine
      description: Daily calendar spine of Jira issues with open-state window and derived week metrics
      grain: One row per issue_id per date_day
      source_models:
      - staging.stg_jira__issue (issue_id, created_at, resolved_at)
      - intermediate.int_jira__field_history_scd (issue_id, valid_starting_on)
      business_logic: '- Build a daily date spine from 2016-01-01 through seven days after today. - For each issue, derive created_on as the calendar date of created_at. Set open_until to today if the issue is unresolved; otherwise to the calendar date of the field-history valid_starting_on. - Join issues to the date spine and include a row when date_day is on or after created_on and on or before one month after open_until. If multiple history records match, earliest_open_until_date is the minimum open_until for that issue_id and date_day. - Create issue_day_id as an MD5 hash of date_day and issue_id concatenated with no delimiter. - Derive earliest_open_until_week as the Monday start of the week containing earliest_open_until_date. - Limit the final output to date_day not later than today. - Determinism and null policy: - All timestamps are converted to calendar dates; comparisons are inclusive. - Only (issue_id, date_day) pairs that meet the window are emitted; earliest_open_until_date is non-null for all rows. - Grouping enforces one row per (issue_id, date_day); issue_day_id is unique.'
      columns:
      - name: date_day
        data_type: DATE
        description: Calendar date in scope (2016-01-01 through today, inclusive) when the issue is within its open window
        tests:
        - not_null
      - name: issue_id
        data_type: VARCHAR
        description: Jira issue identifier associated with the date_day
        tests:
        - not_null
      - name: issue_day_id
        data_type: VARCHAR
        description: MD5 of date_day and issue_id concatenated with no delimiter; unique per (date_day, issue_id)
        tests:
        - not_null
        - unique
      - name: earliest_open_until_date
        data_type: DATE
        description: Minimum open_until among matched history rows for this (issue_id, date_day); open_until is today if unresolved, else the field-history starting date
      - name: earliest_open_until_week
        data_type: DATE
        description: Monday week start derived from earliest_open_until_date
```

## agent 最终 SQL

S4

```sql
with dates as (select unnest(generate_series(date '2016-01-01',current_date,interval 1 day))::date date_day), bounds as (select issue_id,cast(created_at as date) created_on,coalesce(cast(valid_starting_on as date),current_date) open_until from staging.stg_jira__issue i left join intermediate.int_jira__field_history_scd f using(issue_id)), joined as (select b.issue_id,d.date_day,min(b.open_until) earliest_open_until_date from bounds b join dates d on d.date_day>=b.created_on and d.date_day<=b.open_until+interval 1 month group by b.issue_id,d.date_day) select date_day,issue_id,md5(cast(date_day as varchar)||issue_id) issue_day_id,earliest_open_until_date,cast(date_trunc('week',earliest_open_until_date) as date) earliest_open_until_week from joined
```

## gold SQL（仅供定位差异）

S5

```sql
-- Note: This file has been converted from dbt format to DuckDB compatible SQL
-- Original file used dynamic date calculations. This version uses fixed date ranges

with spine as (

    -- Create a date spine from 2016-01-01 to current date + 1 week
    -- You may want to adjust the start date based on your data
    select
        date_day::date as date_day
    from (
        select (date '2016-01-01' + interval (row_number() over () - 1) day) as date_day
        from (
            select 1 from range(0, 3653) -- approximately 10 years worth of days
        )
    ) as date_spine
    where date_day <= current_date + interval '1 week'
),

issue_history_scd as (
    
    select *
    from intermediate.int_jira__field_history_scd
),

issue_dates as (

    select
        issue_history_scd.issue_id,
        date_trunc('day', issue.created_at)::date as created_on,
        -- resolved_at will become null if an issue is marked as un-resolved. if this sorta thing happens often, you may want to run full-refreshes of the field_history models often
        -- if it's not resolved include everything up to today. if it is, look at the last time it was updated 
        date_trunc('day',
            case when issue.resolved_at is null then current_timestamp else issue_history_scd.valid_starting_on::timestamp end)::date as open_until
    from issue_history_scd
    left join staging.stg_jira__issue as issue
        on issue_history_scd.issue_id = issue.issue_id
),

issue_spine as (

    select 
        spine.date_day,
        issue_dates.issue_id,
        -- will take the table-wide min of this in the incremental block at the top of this model
        min(issue_dates.open_until) as earliest_open_until_date

    from spine 
    join issue_dates on
        issue_dates.created_on <= spine.date_day
        and (issue_dates.open_until + interval '1 month') >= spine.date_day
        -- if we cut off issues, we're going to have to do a full refresh to catch issues that have been un-resolved
    group by 1,2
),

surrogate_key as (

    select 
        date_day,
        issue_id,
        md5(date_day::varchar || issue_id::varchar) as issue_day_id,
        earliest_open_until_date,
        date_trunc('week', earliest_open_until_date)::date as earliest_open_until_week

    from issue_spine

    where date_day <= current_date
)

select *
from surrogate_key
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 4073273 | 4809621 | 1482146 | 2218494 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"issue_day_id":"0000422b5ce4ad785c99c5862cb5680d"}</code> |
| K2 | <code>{"issue_day_id":"000045b5ded46ed71902d641ffe3c21f"}</code> |
| K3 | <code>{"issue_day_id":"0000461aaee98cfbc55b1e455bcfa583"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| issue_day_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| earliest_open_until_week | 1014536 | 1014536 | 1014536 | DATE | DATE |
| issue_id | 0 | 0 | 0 | VARCHAR | VARCHAR |

earliest_open_until_week 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2024-02-26 | 2025-10-13 |
| K2 | 2022-10-17 | 2025-10-13 |
| K3 | 2023-05-29 | 2025-10-13 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"issue_day_id":"00000e8378b96bf635cb85158ff9a4b3"},{"issue_day_id":"00000e8ff61cf4b585d2e4ece673a90b"},{"issue_day_id":"00000f83789b673229f4ac41edad6a79"},{"issue_day_id":"00001445ec26aec595b82e395db3f7bd"},{"issue_day_id":"00001ba122f81d371436917e4aa40b77"}]</code> | <code>[{"issue_day_id":"000001bdcf8e4bcbf1535ad08e3ff0ce"},{"issue_day_id":"0000054782cbd4a34da9f60d9be2f7e1"},{"issue_day_id":"000005db98989e9ec0daa4cf04bc4d78"},{"issue_day_id":"000009a09631840f810e319cf231b15c"},{"issue_day_id":"0000120c382303b852f2e2d53972fc2f"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| B7_specified_not_read | <code>["intermediate.int_jira__field_history_scd (issue_id, valid_starting_on)","staging.stg_jira__issue (issue_id, created_at, resolved_at)"]</code> |
| C9_agent_runtime_text | <code>S4:1 current_date；命中数=2</code> |
| C9_gold_runtime_text | <code>S5:6 current date；命中数=5</code> |
| C9_contract_runtime_text | <code>S3:1421 today；命中数=5</code> |

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
| 23 | run | <code>grep -E 'WARNING -  ⏭&#124;WARNING -   ⏭&#124;Catalog Error&#124;Binder Error&#124;Parser Error&#124;Conversion Error' /tmp/runlog &#124; head -80</code> | 8767 | true | false |
| 27 | run | <code>grep -oE '.{0,25}committed.{0,25}' sql/intermediate/int_jira__sprint_performance_analytics.sql &#124; head; python - &lt;&lt;'PY'<br>p='sql/intermediate/int_jira__user_activity_metrics.sql'<br>s=open(p).read(); start=</code> | 613 | false | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> s=re.sub(r'try_cast\((\w+) as timestamp\)',r"try_cast(regexp_replace(\1, '([+-][0-9]{2}</code> | 9550 | true | false |
| 33 | run | <code>cat sql/staging/stg_jira__issue_type.sql; grep -o '.\{0,30\}prev_committed.\{0,30\}' sql/intermediate/int_jira__sprint_performance_analytics.sql; cat sql/staging/stg_jira__issue.sql &#124; head -c 800</code> | 1230 | false | false |
| 35 | run | <code>sed -i 's/description,is_subtask subtask as is_subtask/description,subtask as is_subtask/' sql/staging/stg_jira__issue_type.sql; sed -i 's/committed_points-prev_committed)/committed_points-prev_commit</code> | 53 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text().replace("regexp_replace(created, '([+-][0-9]{2})([0-9]{2})$', '\\\\1:\\\\2')", "regexp_replace(cre</code> | 4200 | true | false |
| 41 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; grep -E 'INTERMEDIATE Layer&#124;✓ intermediate.int_jira__issue_join&#124;✓ intermediate.int_jira__issue_users&#124;staging.stg_jira__issue:' /tmp/runlog3</code> | 836 | false | false |
| 43 | run | <code>cat sql/intermediate/int_jira__issue_users.sql; cat sql/intermediate/int_jira__issue_calendar_spine.sql</code> | 1202 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('jira.duckdb',read_only=True)<br>checks=[('staging.stg_jira__issue','issue_id'),('staging.stg_jira__project','project_id'),('intermediate.int_jira__issue_jo</code> | 422 | false | false |
| 53 | run | <code>cat &gt; result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 顺序实现 SQL，覆盖 staging 17 个、intermediate 19 个及 marts 13 个模型，共 49 个 SQL 文件。SQL 使用 DuckDB 语法、直接引用 `schema.table`，文件均不以分号结束。<br><br>**验证**<br>- `py</code> | 132 | false | false |

### agent action 的 thought/message 命中原句

event 15 / message

```text
'int_jira__issue_calendar_spine':"with dates as (select unnest(generate_series(date '2016-01-01',current_date,interval 1 day))::date date_day), bounds as (select issue_id,cast(created_at as date) created_on,coalesce(cast(valid_starting_on as date),current_date) open_until from staging.stg_jira__issue i left join intermediate.int_jira__field_history_scd f using(issue_id)), joined as (select b.issue_id,d.date_day,min(b.open_until) earliest_open_until_date from bounds b join dates d on d.date_day>=b.created_on and d.date_day<=b.open_until+interval 1 month group by b.issue_id,d.date_day) select date_day,issue_id,md5(cast(date_day as varchar)||issue_id) issue_day_id,earliest_open_until_date,cast(date_trunc('week',earliest_open_until_date) as date) earliest_open_until_week from joined",
```
event 43 / message

```text
Running command: cat sql/intermediate/int_jira__issue_users.sql; cat sql/intermediate/int_jira__issue_calendar_spine.sql
```
event 53 / message

```text
`int_jira__issue_calendar_spine` 在当前数据和日期窗口下结果为空，但该空结果不影响 `run.py` 全流程执行。
```

## result.md 本表名原句

S9:13

```text
`int_jira__issue_calendar_spine` 在当前数据和日期窗口下结果为空，但该空结果不影响 `run.py` 全流程执行。
```

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-011.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_calendar_spine.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/intermediate/field_history/int_jira__issue_calendar_spine.sql`
- S6: `records/006_contract_impl-011.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/result.md`
- S10: `data/021_packages_work/021_impl-011_int_jira__issue_calendar_spine/021_impl-011_int_jira__issue_calendar_spine.json`
- S11: `data/011_agent_alignment/impl-011_attempt_01/int_jira__issue_calendar_spine_2025-10-13.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/jira.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions`
