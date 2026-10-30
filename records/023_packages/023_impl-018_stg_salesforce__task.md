# impl-018 | staging | stg_salesforce__task | 差异：S1；日期 原记录

## 契约完整原文

S3:595–646

```yaml
    - name: stg_salesforce__task
      description: "Cleaned task records with validated activity information and completion status"
      source_table: raw.task
      columns:
        - name: task_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: activity_date
          data_type: DATE
        - name: call_disposition
          data_type: VARCHAR
        - name: call_duration_in_seconds
          data_type: INTEGER
        - name: call_object
          data_type: VARCHAR
        - name: call_type
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: task_description
          data_type: VARCHAR
        - name: is_closed
          data_type: BOOLEAN
          constraints: [not_null]
        - name: is_deleted
          data_type: BOOLEAN
        - name: is_high_priority
          data_type: BOOLEAN
        - name: owner_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: priority
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "status IS NOT NULL"
              on_failure: delete_row
            - rule: "status IN ('Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred')"
              on_failure: delete_row
            - rule: "status = TRIM(status)"
              on_failure: correct
        - name: subject
          data_type: VARCHAR
        - name: type
          data_type: VARCHAR
        - name: what_id
          data_type: VARCHAR
        - name: who_id
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
select
      id as task_id,
      try_cast(activity_date as DATE) as activity_date,
      call_disposition as call_disposition,
      try_cast(call_duration_in_seconds as INTEGER) as call_duration_in_seconds,
      call_object as call_object,
      call_type as call_type,
      try_cast(created_date as TIMESTAMP) as created_date,
      description as task_description,
      is_closed as is_closed,
      is_deleted as is_deleted,
      is_high_priority as is_high_priority,
      owner_id as owner_id,
      priority as priority,
      trim(status) as status,
      subject as subject,
      "type" as type,
      what_id as what_id,
      who_id as who_id
from raw.task
where id is not null
  and is_closed is not null
  and owner_id is not null
  and trim(status) in ('Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred')
qualify row_number() over (partition by id order by id) = 1
```

## gold SQL（仅供定位差异）

S5

```sql
with fields as (
    select *
    from raw.task
), 

final as (
    select
        cast(id as varchar) as task_id,
        cast(activity_date as date) as activity_date,
        cast(call_disposition as varchar) as call_disposition,
        cast(call_duration_in_seconds as integer) as call_duration_in_seconds,
        cast(call_object as varchar) as call_object,
        cast(call_type as varchar) as call_type,
        cast(created_date as timestamp) as created_date,
        cast(description as varchar) as task_description,
        cast(coalesce(is_closed, false) as boolean) as is_closed,
        cast(coalesce(is_deleted, false) as boolean) as is_deleted,
        cast(coalesce(is_high_priority, false) as boolean) as is_high_priority,
        cast(owner_id as varchar) as owner_id,
        cast(priority as varchar) as priority,
        cast(status as varchar) as status,
        cast(subject as varchar) as subject,
        cast(type as varchar) as type,
        cast(what_id as varchar) as what_id,
        cast(who_id as varchar) as who_id
    from fields
)

select *
from final
where not coalesce(is_deleted, false)
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2998 | 3000 | 0 | 2 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| activity_date | 0 | 0 | 0 | DATE | DATE |
| call_disposition | 0 | 0 | 0 | VARCHAR | VARCHAR |
| call_duration_in_seconds | 0 | 0 | 0 | INTEGER | INTEGER |
| call_object | 0 | 0 | 0 | VARCHAR | VARCHAR |
| call_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_closed | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_high_priority | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| owner_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| priority | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subject | 0 | 0 | 0 | VARCHAR | VARCHAR |
| type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| what_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| who_id | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"task_id":"00T84b793UolT5X"},{"task_id":"00ToDfyDWQolm8g"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"call_object","table_rows":2998}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"is_deleted","value":"false"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=5；assistant_trajectory  select activity_date::date as date_day,count(*) as tasks_completed from staging.stg_salesforce__task where activity_date is not null group by 1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：101；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,220p' run.py</code> | 11932 | true | false |
| 13 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>s=yaml.safe_load(open('salesforce_start.yaml'))<br>for t,c in s.items(): print(t,', '.join(c))<br>PY</code> | 8872 | false | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print([t['name'] for t in x['staging_contract']['tables']])<br>for t in x['staging_contract']['tables']:<br> print(t['name'], [c</code> | 6786 | true | false |
| 17 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce_start.duckdb',read_only=True)<br>for t in ['account','contact','opportunity','user','lead','task','event','user_role','product_2','opportunity_l</code> | 31400 | false | false |
| 19 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts; cat &gt; /tmp/build.py &lt;&lt;'PY'<br>import yaml, pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>source=yaml.safe_load(open('salesforce_start.y</code> | 0 | false | false |
| 21 | run | <code>cat &gt; sql/intermediate/int_salesforce__account_enhanced.sql &lt;&lt;'SQL'<br>with account_base as (<br>    select *<br>    from staging.stg_salesforce__account<br>    where not coalesce(is_deleted, false)<br>),<br>account_de</code> | 0 | false | false |
| 31 | run | <code>cat &gt; sql/marts/salesforce__opportunity_line_item_enhanced.sql &lt;&lt;'SQL'<br>with line_items as (<br> select oli.*,opp.opportunity_name,opp.account_id,opp.owner_id as opportunity_owner_id,opp.stage_name,opp.cl</code> | 0 | false | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>src=yaml.safe_load(open('salesforce_start.yaml')); co=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br>mp={'account_id':'id','account_name':'na</code> | 847 | true | false |
| 43 | run | <code>tail -180 /tmp/run2.log; grep -E '✗&#124;ERROR&#124;layer complete' /tmp/run2.log</code> | 15611 | true | false |
| 49 | run | <code>for f in sql/staging/*.sql; do echo ==== $f; grep -E 'md5&#124;history_unique_key&#124;created_date as&#124;last_modified_date' $f; done; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=</code> | 14873 | true | false |
| 53 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_salesforce__contact_history.sql');s=p.read_text().replace('id as account_id,','account_id as account_id,');p.write_text(s)<br>p=Path('sql/</code> | 331 | false | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml,pathlib<br>c=duckdb.connect('salesforce.duckdb',read_only=True)<br>con=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer, schema, key in [('staging_contract','stag</code> | 589 | true | false |
| 67 | run | <code>for f in sql/staging/*.sql; do printf '%-55s ' "$(basename "$f")"; sed -n '2p' "$f"; done</code> | 1156 | true | false |
| 83 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('salesforce.duckdb',read_only=True)<br>for layer,sch in [('staging_contract','staging</code> | 225 | false | false |
| 85 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('salesforce.duckdb',read_only=True)<br>for layer,sch in [('staging_contract','staging</code> | 295 | true | false |
| 89 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=True); spec=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in spec['staging_contract']['tables']:<br> name=t['name</code> | 1149 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
 if n=='stg_salesforce__task': filters=['id is not null','is_closed is not null','owner_id is not null','status in (\'Not Started\', \'In Progress\', \'Completed\', \'Waiting on someone else\', \'Deferred\')']
```
event 21 / message

```text
    from staging.stg_salesforce__task
```
event 31 / message

```text
 select activity_date::date as date_day,count(*) as tasks_completed from staging.stg_salesforce__task where activity_date is not null group by 1
```
event 83 / message

```text
for t,col in [('stg_salesforce__contact','contact_id'),('stg_salesforce__opportunity','opportunity_id'),('stg_salesforce__user','user_id'),('stg_salesforce__lead','lead_id'),('stg_salesforce__event','event_id'),('stg_salesforce__task','task_id')]:
```
event 85 / message

```text
for t,col in [('stg_salesforce__contact','contact_id'),('stg_salesforce__opportunity','opportunity_id'),('stg_salesforce__user','user_id'),('stg_salesforce__lead','lead_id'),('stg_salesforce__event','event_id'),('stg_salesforce__task','task_id')]:
```
event 89 / message

```text
for sch,tbl,key in [('staging','stg_salesforce__account','account_id'),('staging','stg_salesforce__contact','contact_id'),('staging','stg_salesforce__opportunity','opportunity_id'),('staging','stg_salesforce__user','user_id'),('staging','stg_salesforce__lead','lead_id'),('staging','stg_salesforce__task','task_id'),('staging','stg_salesforce__event','event_id'),('staging','stg_salesforce__account_history','history_unique_key'),('staging','stg_salesforce__contact_history','history_unique_key'),('staging','stg_salesforce__opportunity_history','history_unique_key')]:
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-018.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__task.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__task.sql`
- S6: `records/006_contract_impl-018.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/.tmp/result.md`
- S10: `data/023_packages_work/023_impl-018_stg_salesforce__task/023_impl-018_stg_salesforce__task.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions`
