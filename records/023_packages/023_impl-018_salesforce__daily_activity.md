# impl-018 | marts | salesforce__daily_activity | 差异：S1；日期 原记录

## 契约完整原文

S3:2425–2474

```yaml
    - name: salesforce__daily_activity
      description: Daily summary by date_day of leads created/converted, tasks/events counts, and opportunity creation/closure metrics with amounts rounded to 0 decimals.
      grain: One row per date_day
      source_models:
      - staging.stg_salesforce__lead
      - staging.stg_salesforce__task
      - staging.stg_salesforce__event
      - staging.stg_salesforce__opportunity
      - intermediate.int_salesforce__date_spine
      business_logic: '- Start from the date spine (one row per date_day); this drives the output. - Tasks: group tasks by the calendar day of activity_date; tasks_completed is the number of non-null task records on that day; tasks with a null activity_date do not contribute and will not join; no additional filters. - Events: define each event’s activity day as the calendar day of activity_date, otherwise the calendar day of activity_date_time; if both are null the event is excluded; events_completed is the number of non-null event records on that day. - Leads created: group leads by the calendar day of created_date; leads_created is the number of non-null lead records on that day; rows with a null created_date are excluded. - Leads converted: restrict to leads where is_converted is true; group by the calendar day of converted_date; leads_converted is the number of non-null lead records on that day; rows with a null converted_date are excluded. - Opportunities base: for each opportunity derive created_day from created_date and close_day from close_date; set status as: • Won when is_won is true • Lost when is_won is false and is_closed is true • Pipeline when not closed and forecast_category (case-insensitive) is one of pipeline, forecast, bestcase • Other otherwise Amount may be null and is used in sums. - Opportunities created (by created_day): • opportunities_created: number of non-null opportunity records • opportunities_created_amount: sum of amount rounded to 0 decimals; sums ignore null amounts and are null when all amounts are null - Opportunities closed (by close_day): • opportunities_won: number of opportunities with status Won; zero when there are close_day records but none Won; null when no close_day records • opportunities_won_amount: sum of amounts for status Won rounded to 0 decimals; zero when there are close_day records but none Won; null when no close_day records • opportunities_lost: number of opportunities with status Lost; zero when there are close_day records but none Lost; null when no close_day records • opportunities_lost_amount: sum of amounts for status Lost rounded to 0 decimals; null when there are close_day records but none Lost; null when no close_day records • pipeline_amount: sum of amounts for status Pipeline rounded to 0 decimals; null when there are close_day records but none Pipeline; null when no close_day records - Output: left join each aggregate to the date spine on date_day; if a date has no matching aggregate row, the corresponding fields remain null; no defaulting to zero beyond the rules above.'
      columns:
      - name: date_day
        data_type: DATE
        description: Calendar date from the date spine and join key; exactly one row per date_day.
        tests:
        - not_null
        - unique
      - name: leads_created
        data_type: BIGINT
        description: Number of leads created on date_day based on created_date; only non-null lead records counted; null when no leads match that day.
      - name: leads_converted
        data_type: BIGINT
        description: Number of leads with is_converted=true whose converted_date falls on date_day; only non-null lead records counted; null when none match that day.
      - name: tasks_completed
        data_type: BIGINT
        description: Number of tasks whose activity_date falls on date_day; tasks with null activity_date are excluded; null when none match that day.
      - name: events_completed
        data_type: BIGINT
        description: Number of events by day using activity_date when present else activity_date_time; events with both timestamps null are excluded; null when none match that day.
      - name: opportunities_created
        data_type: BIGINT
        description: Number of opportunities created on date_day (by created_date); only non-null records counted; null when none match that day.
      - name: opportunities_created_amount
        data_type: DECIMAL(38,0)
        description: Sum of amounts for opportunities created on date_day, rounded to 0 decimals; null when all amounts are null or no records match that day.
      - name: opportunities_won
        data_type: BIGINT
        description: Number of opportunities with close_date on date_day and status Won; zero when close_date records exist but none Won; null when no close_date records.
      - name: opportunities_won_amount
        data_type: DECIMAL(38,0)
        description: Sum of amounts for opportunities with close_date on date_day and status Won, rounded to 0 decimals; zero when close_date records exist but none Won; null when no close_date records.
      - name: opportunities_lost
        data_type: BIGINT
        description: Number of opportunities with close_date on date_day and status Lost; zero when close_date records exist but none Lost; null when no close_date records.
      - name: opportunities_lost_amount
        data_type: DECIMAL(38,0)
        description: Sum of amounts for opportunities with close_date on date_day and status Lost, rounded to 0 decimals; null when close_date records exist but none Lost or when no close_date records.
      - name: pipeline_amount
        data_type: DECIMAL(38,0)
        description: Sum of amounts for opportunities with close_date on date_day and status Pipeline, rounded to 0 decimals; null when close_date records exist but none Pipeline or when no close_date records.
```

## agent 最终 SQL

S4

```sql
with task_daily as (
 select activity_date::date as date_day,count(*) as tasks_completed from staging.stg_salesforce__task where activity_date is not null group by 1
),
event_daily as (
 select coalesce(activity_date::date,activity_date_time::date) as date_day,count(*) as events_completed
 from staging.stg_salesforce__event where coalesce(activity_date,activity_date_time) is not null group by 1
),
lead_created as (
 select created_date::date as date_day,count(*) as leads_created from staging.stg_salesforce__lead where created_date is not null group by 1
),
lead_converted as (
 select converted_date::date as date_day,count(*) as leads_converted from staging.stg_salesforce__lead
 where is_converted is true and converted_date is not null group by 1
),
opportunity_base as (
 select *,created_date::date as created_day,close_date::date as close_day,
 case when is_won is true then 'Won' when is_won is false and is_closed is true then 'Lost'
 when is_closed is false and lower(forecast_category) in ('pipeline','forecast','bestcase') then 'Pipeline' else 'Other' end as deal_status
 from staging.stg_salesforce__opportunity
),
opp_created as (
 select created_day as date_day,count(*) as opportunities_created,round(sum(amount)) as opportunities_created_amount
 from opportunity_base where created_day is not null group by 1
),
opp_closed as (
 select close_day as date_day,count(*) filter(where deal_status='Won') as opportunities_won,
 coalesce(round(sum(amount) filter(where deal_status='Won')),0) as opportunities_won_amount,
 count(*) filter(where deal_status='Lost') as opportunities_lost,
 round(sum(amount) filter(where deal_status='Lost')) as opportunities_lost_amount,
 round(sum(amount) filter(where deal_status='Pipeline')) as pipeline_amount
 from opportunity_base where close_day is not null group by 1
)
select d.date_day,lc.leads_created,lcv.leads_converted,t.tasks_completed,e.events_completed,oc.opportunities_created,oc.opportunities_created_amount,
 oh.opportunities_won,oh.opportunities_won_amount,oh.opportunities_lost,oh.opportunities_lost_amount,oh.pipeline_amount
from intermediate.int_salesforce__date_spine d left join lead_created lc using(date_day)
left join lead_converted lcv using(date_day) left join task_daily t using(date_day) left join event_daily e using(date_day)
left join opp_created oc using(date_day) left join opp_closed oh using(date_day)
```

## gold SQL（仅供定位差异）

S5

```sql
with date_spine as (
    select 
        date_day
    from intermediate.int_salesforce__date_spine
),

task as (
    select 
        date_trunc('day', activity_date) as activity_date,
        count(task_id) as tasks_completed
    from staging.stg_salesforce__task
    group by 1
), 

salesforce_event as (
    select 
        coalesce(date_trunc('day', activity_date), date_trunc('day', activity_date_time)) as activity_date,
        count(event_id) as events_completed
    from staging.stg_salesforce__event
    group by 1
), 

salesforce_lead as (
    select 
        date_trunc('day', created_date) as created_date,
        count(lead_id) as leads_created 
    from staging.stg_salesforce__lead
    group by 1
), 

salesforce_converted_lead as (
    select 
        date_trunc('day', converted_date) as converted_date,
        count(lead_id) as leads_converted
    from staging.stg_salesforce__lead
    where is_converted
    group by 1
), 

opportunity as (
    select 
        opportunity_id,
        date_trunc('day', created_date) as created_date,
        account_id,
        date_trunc('day', close_date) as close_date,
        is_closed,
        is_deleted,
        is_won,
        owner_id, 
        stage_name,
        type,
        amount,
        case
            when is_won then 'Won'
            when not is_won and is_closed then 'Lost'
            when not is_closed and lower(forecast_category) in ('pipeline','forecast','bestcase') then 'Pipeline'
            else 'Other'
        end as status
    from staging.stg_salesforce__opportunity
),

opportunities_created as (
    select
        created_date,
        count(opportunity_id) as opportunities_created,
        round(sum(amount)) as opportunities_created_amount
    from opportunity
    group by 1
),

opportunities_closed as (
    select
        close_date,
        count(case when status = 'Won' then opportunity_id else null end) as opportunities_won,
        round(sum(case when status = 'Won' then amount else 0 end)) as opportunities_won_amount,
        count(case when status = 'Lost' then opportunity_id else null end) as opportunities_lost,
        round(sum(case when status = 'Lost' then amount else null end)) as opportunities_lost_amount,
        round(sum(case when status = 'Pipeline' then amount else null end)) as pipeline_amount
    from opportunity
    group by 1
)

select
    date_spine.date_day,
    salesforce_lead.leads_created,
    salesforce_converted_lead.leads_converted,
    task.tasks_completed,
    salesforce_event.events_completed,
    opportunities_created.opportunities_created,
    opportunities_created.opportunities_created_amount,
    opportunities_closed.opportunities_won,
    opportunities_closed.opportunities_won_amount,
    opportunities_closed.opportunities_lost,
    opportunities_closed.opportunities_lost_amount,
    opportunities_closed.pipeline_amount
from date_spine
left join salesforce_lead
    on date_spine.date_day = salesforce_lead.created_date
left join salesforce_converted_lead
    on date_spine.date_day = salesforce_converted_lead.converted_date
left join task
    on date_spine.date_day = task.activity_date
left join salesforce_event
    on date_spine.date_day = salesforce_event.activity_date
left join opportunities_created
    on date_spine.date_day = opportunities_created.created_date
left join opportunities_closed
    on date_spine.date_day = opportunities_closed.close_date
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2124 | 2124 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"date_day":"2022-02-07"}</code> |
| K2 | <code>{"date_day":"2023-04-04"}</code> |
| K3 | <code>{"date_day":"2023-05-10"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| leads_created | 0 | 0 | 0 | BIGINT | BIGINT |
| leads_converted | 0 | 0 | 0 | BIGINT | BIGINT |
| tasks_completed | 0 | 0 | 0 | BIGINT | BIGINT |
| events_completed | 0 | 0 | 0 | BIGINT | BIGINT |
| opportunities_created | 0 | 0 | 0 | BIGINT | BIGINT |
| opportunities_created_amount | 0 | 0 | 0 | DECIMAL(38,0) | DECIMAL(38,0) |
| opportunities_won | 0 | 0 | 0 | BIGINT | BIGINT |
| opportunities_won_amount | 8 | 8 | 8 | DECIMAL(38,0) | DECIMAL(38,0) |
| opportunities_lost | 0 | 0 | 0 | BIGINT | BIGINT |
| opportunities_lost_amount | 0 | 0 | 0 | DECIMAL(38,0) | DECIMAL(38,0) |
| pipeline_amount | 0 | 0 | 0 | DECIMAL(38,0) | DECIMAL(38,0) |

opportunities_won_amount 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | null |
| K2 | 0 | null |
| K3 | 0 | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

没有 True 痕迹。

## 轨迹索引（不放输出原文）

本题事件总数：101；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,220p' run.py</code> | 11932 | true | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print([t['name'] for t in x['staging_contract']['tables']])<br>for t in x['staging_contract']['tables']:<br> print(t['name'], [c</code> | 6786 | false | false |
| 19 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts; cat &gt; /tmp/build.py &lt;&lt;'PY'<br>import yaml, pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>source=yaml.safe_load(open('salesforce_start.y</code> | 0 | false | false |
| 21 | run | <code>cat &gt; sql/intermediate/int_salesforce__account_enhanced.sql &lt;&lt;'SQL'<br>with account_base as (<br>    select *<br>    from staging.stg_salesforce__account<br>    where not coalesce(is_deleted, false)<br>),<br>account_de</code> | 0 | false | false |
| 23 | run | <code>cat &gt; sql/intermediate/int_salesforce__lead_conversion_funnel.sql &lt;&lt;'SQL'<br>with lead_base as (<br>    select * from staging.stg_salesforce__lead where not coalesce(is_deleted, false)<br>),<br>scored as (<br>    se</code> | 0 | false | false |
| 25 | run | <code>cat &gt; sql/intermediate/int_salesforce__opportunity_aggregation_by_owner.sql &lt;&lt;'SQL'<br>with enhanced_opportunity as (<br>    select o.*, u.manager_id,<br>        case when o.is_won then 'Won' when o.is_won = f</code> | 0 | false | false |
| 29 | run | <code>cat &gt; sql/marts/dim_salesforce__user.sql &lt;&lt;'SQL'<br>with user_base as (<br> select u.*,ur.user_role_name,ur.developer_name,ur.parent_role_id,ur.rollup_description,<br> m.user_id as matched_manager_id,m.first_n</code> | 0 | false | false |
| 31 | run | <code>cat &gt; sql/marts/salesforce__opportunity_line_item_enhanced.sql &lt;&lt;'SQL'<br>with line_items as (<br> select oli.*,opp.opportunity_name,opp.account_id,opp.owner_id as opportunity_owner_id,opp.stage_name,opp.cl</code> | 0 | false | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>src=yaml.safe_load(open('salesforce_start.yaml')); co=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br>mp={'account_id':'id','account_name':'na</code> | 847 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_salesforce__contact.sql'<br>s=open(p).read().replace('try_cast(created_date as TIMESTAMP) as created_date','cast(null as TIMESTAMP) as created_date')<br>open(p,'w').write(</code> | 0 | false | false |
| 43 | run | <code>tail -180 /tmp/run2.log; grep -E '✗&#124;ERROR&#124;layer complete' /tmp/run2.log</code> | 15611 | true | false |
| 45 | run | <code>cat sql/staging/stg_salesforce__opportunity.sql; cat sql/staging/stg_salesforce__opportunity_history.sql</code> | 3625 | false | false |
| 47 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_salesforce__opportunity.sql';s=open(p).read().replace('try_cast(days_since_created as INTEGER) as days_since_created',"case when created_date is not null then date_d</code> | 331 | false | false |
| 49 | run | <code>for f in sql/staging/*.sql; do echo ==== $f; grep -E 'md5&#124;history_unique_key&#124;created_date as&#124;last_modified_date' $f; done; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=</code> | 14873 | true | false |
| 51 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>x=yaml.safe_load(open('docs/data_contract.yaml'))['modeling_spec']; c=duckdb.connect('salesforce.duckdb',read_only=True)<br>for layer,sch in [('intermediate_models','in</code> | 1355 | true | false |
| 53 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_salesforce__contact_history.sql');s=p.read_text().replace('id as account_id,','account_id as account_id,');p.write_text(s)<br>p=Path('sql/</code> | 331 | false | false |
| 55 | run | <code>cat sql/staging/stg_salesforce__contact.sql; cat sql/staging/stg_salesforce__user.sql; cat sql/staging/stg_salesforce__event.sql</code> | 4202 | false | false |
| 57 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br># Correct field source mapping; canonical foreign keys should remain FK columns, not the row's own id.<br>fixes={<br>'stg_salesforce__contact':'id as account_id','st</code> | 3263 | true | false |
| 59 | run | <code>grep -n account_ sql/staging/stg_salesforce__{opportunity,contact_history,opportunity_history}.sql</code> | 270 | false | false |
| 61 | run | <code>sed -i 's/account_account_id/account_id/g' sql/staging/stg_salesforce__opportunity.sql sql/staging/stg_salesforce__contact_history.sql sql/staging/stg_salesforce__opportunity_history.sql; python run.p</code> | 331 | false | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml,pathlib<br>c=duckdb.connect('salesforce.duckdb',read_only=True)<br>con=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer, schema, key in [('staging_contract','stag</code> | 589 | false | false |
| 65 | run | <code>head -10 sql/staging/stg_salesforce__user.sql &amp;&amp; head -8 sql/staging/stg_salesforce__contact.sql &amp;&amp; head -5 sql/staging/stg_salesforce__opportunity.sql; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect(</code> | 1340 | false | false |
| 67 | run | <code>for f in sql/staging/*.sql; do printf '%-55s ' "$(basename "$f")"; sed -n '2p' "$f"; done</code> | 1156 | false | false |
| 71 | run | <code>sed -i 's/account_account_id/account_id/g' sql/staging/stg_salesforce__account_history.sql sql/staging/stg_salesforce__opportunity_history.sql; python run.py &gt; /tmp/run7.log 2&gt;&amp;1; grep -E '✗&#124;ERROR&#124;lay</code> | 1397 | false | false |
| 83 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('salesforce.duckdb',read_only=True)<br>for layer,sch in [('staging_contract','staging</code> | 225 | false | false |
| 85 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('salesforce.duckdb',read_only=True)<br>for layer,sch in [('staging_contract','staging</code> | 295 | false | false |
| 87 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_salesforce__contact.sql');s=p.read_text()<br>s=s.replace('      account_id as account_id,',"      case when account_id is null or (regexp_</code> | 331 | false | false |
| 89 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=True); spec=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in spec['staging_contract']['tables']:<br> name=t['name</code> | 1149 | false | false |

### agent action 的 thought/message 命中原句

event 31 / message

```text
cat > sql/marts/salesforce__daily_activity.sql <<'SQL'
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-018.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__daily_activity.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/marts/salesforce__daily_activity.sql`
- S6: `records/006_contract_impl-018.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/.tmp/result.md`
- S10: `data/023_packages_work/023_impl-018_salesforce__daily_activity/023_impl-018_salesforce__daily_activity.json`
- S11: `data/005_cs_work/impl-018_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions`
