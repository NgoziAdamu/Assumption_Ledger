# impl-018 | staging | stg_salesforce__user | 差异：S1；日期 原记录

## 契约完整原文

S3:406–481

```yaml
    - name: stg_salesforce__user
      description: "Cleaned user/employee records with validated authentication and profile information"
      source_table: raw.user
      columns:
        - name: account_id
          data_type: VARCHAR
        - name: alias
          data_type: VARCHAR
        - name: city
          data_type: VARCHAR
        - name: company_name
          data_type: VARCHAR
        - name: contact_id
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: country_code
          data_type: VARCHAR
        - name: department
          data_type: VARCHAR
        - name: email
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "email IS NOT NULL"
              on_failure: delete_row
            - rule: "email = LOWER(TRIM(email))"
              on_failure: correct
            - rule: "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
              on_failure: delete_row
            - rule: "LENGTH(email) <= 255"
              on_failure: delete_row
        - name: first_name
          data_type: VARCHAR
        - name: user_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: individual_id
          data_type: VARCHAR
        - name: is_active
          data_type: BOOLEAN
          constraints: [not_null]
        - name: last_login_date
          data_type: TIMESTAMP
        - name: last_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: last_referenced_date
          data_type: TIMESTAMP
        - name: last_viewed_date
          data_type: TIMESTAMP
        - name: manager_id
          data_type: VARCHAR
        - name: user_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: postal_code
          data_type: VARCHAR
        - name: profile_id
          data_type: VARCHAR
        - name: state
          data_type: VARCHAR
        - name: state_code
          data_type: VARCHAR
        - name: street
          data_type: VARCHAR
        - name: title
          data_type: VARCHAR
        - name: user_role_id
          data_type: VARCHAR
        - name: user_type
          data_type: VARCHAR
        - name: username
          data_type: VARCHAR
          constraints: [not_null, unique]

```

## agent 最终 SQL

S4

```sql
select
      account_id as account_id,
      alias as alias,
      city as city,
      company_name as company_name,
      contact_id as contact_id,
      country as country,
      country_code as country_code,
      department as department,
      lower(trim(email)) as email,
      first_name as first_name,
      id as user_id,
      individual_id as individual_id,
      is_active as is_active,
      try_cast(last_login_date as TIMESTAMP) as last_login_date,
      last_name as last_name,
      try_cast(last_referenced_date as TIMESTAMP) as last_referenced_date,
      try_cast(last_viewed_date as TIMESTAMP) as last_viewed_date,
      manager_id as manager_id,
      name as user_name,
      postal_code as postal_code,
      profile_id as profile_id,
      state as state,
      state_code as state_code,
      street as street,
      title as title,
      user_role_id as user_role_id,
      user_type as user_type,
      username as username
from raw.user
where id is not null
  and email is not null
  and regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
  and length(lower(trim(email))) <= 255
  and is_active is not null
  and last_name is not null
  and name is not null
  and username is not null
qualify row_number() over (partition by id order by id) = 1
```

## gold SQL（仅供定位差异）

S5

```sql
with fields as (
    select
        account_id,
        alias,
        city,
        company_name,
        contact_id,
        country,
        country_code,
        department,
        email,
        first_name,
        id,
        individual_id,
        is_active,
        last_login_date,
        last_name,
        last_referenced_date,
        last_viewed_date,
        manager_id,
        name,
        postal_code,
        profile_id,
        state,
        state_code,
        street,
        title,
        user_role_id,
        user_type,
        username
    from raw."user"
), 

final as (
    select 
        cast(account_id as varchar) as account_id,
        cast(alias as varchar) as alias,
        cast(city as varchar) as city,
        cast(company_name as varchar) as company_name,
        cast(contact_id as varchar) as contact_id,
        cast(country as varchar) as country,
        cast(country_code as varchar) as country_code,
        cast(department as varchar) as department,
        cast(email as varchar) as email,
        cast(first_name as varchar) as first_name,
        cast(id as varchar) as user_id,
        cast(individual_id as varchar) as individual_id,
        cast(coalesce(is_active, false) as boolean) as is_active,
        cast(last_login_date as timestamp) as last_login_date,
        cast(last_name as varchar) as last_name,
        cast(last_referenced_date as timestamp) as last_referenced_date,
        cast(last_viewed_date as timestamp) as last_viewed_date,
        cast(manager_id as varchar) as manager_id,
        cast(name as varchar) as user_name,
        cast(postal_code as varchar) as postal_code,
        cast(profile_id as varchar) as profile_id,
        cast(state as varchar) as state,
        cast(state_code as varchar) as state_code,
        cast(street as varchar) as street,
        cast(title as varchar) as title,
        cast(user_role_id as varchar) as user_role_id,
        cast(user_type as varchar) as user_type,
        cast(username as varchar) as username
    from fields
)

select * 
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 993 | 1000 | 0 | 7 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| alias | 0 | 0 | 0 | VARCHAR | VARCHAR |
| city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| company_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| department | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| first_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| individual_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_active | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| last_login_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| last_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_referenced_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| last_viewed_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| manager_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| postal_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| profile_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| state_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| street | 0 | 0 | 0 | VARCHAR | VARCHAR |
| title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| user_role_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| user_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| username | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"user_id":"0059C2EfyCoKdrL"},{"user_id":"005BJTfsUkiH8G4"},{"user_id":"005CNG3iFqYuTOS"},{"user_id":"005FFEIDbugzt32"},{"user_id":"005I5SrJH3yvVjc"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>3列；[{"column":"account_id","table_rows":993},{"column":"contact_id","table_rows":993},{"column":"individual_id","table_rows":993}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=21；task_instruction_not_agent_report         description: Manager city from stg_salesforce__user.city; null if no user match</code> |

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
| 23 | run | <code>cat &gt; sql/intermediate/int_salesforce__lead_conversion_funnel.sql &lt;&lt;'SQL'<br>with lead_base as (<br>    select * from staging.stg_salesforce__lead where not coalesce(is_deleted, false)<br>),<br>scored as (<br>    se</code> | 0 | false | false |
| 25 | run | <code>cat &gt; sql/intermediate/int_salesforce__opportunity_aggregation_by_owner.sql &lt;&lt;'SQL'<br>with enhanced_opportunity as (<br>    select o.*, u.manager_id,<br>        case when o.is_won then 'Won' when o.is_won = f</code> | 0 | false | false |
| 27 | run | <code>cat &gt; sql/marts/fct_salesforce__lead_performance.sql &lt;&lt;'SQL'<br>with active_users as (<br> select user_id, trim(concat(coalesce(first_name,''),' ',coalesce(last_name,''))) as owner_name<br> from staging.stg_sa</code> | 0 | false | false |
| 29 | run | <code>cat &gt; sql/marts/dim_salesforce__user.sql &lt;&lt;'SQL'<br>with user_base as (<br> select u.*,ur.user_role_name,ur.developer_name,ur.parent_role_id,ur.rollup_description,<br> m.user_id as matched_manager_id,m.first_n</code> | 0 | false | false |
| 31 | run | <code>cat &gt; sql/marts/salesforce__opportunity_line_item_enhanced.sql &lt;&lt;'SQL'<br>with line_items as (<br> select oli.*,opp.opportunity_name,opp.account_id,opp.owner_id as opportunity_owner_id,opp.stage_name,opp.cl</code> | 0 | false | false |
| 33 | run | <code>cat &gt; sql/marts/salesforce__revenue_analytics.sql &lt;&lt;'SQL'<br>with closed_opportunities as (<br> select * from intermediate.int_salesforce__opportunity_pipeline where is_closed is true<br>),<br>enriched as (<br> sele</code> | 0 | false | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>src=yaml.safe_load(open('salesforce_start.yaml')); co=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br>mp={'account_id':'id','account_name':'na</code> | 847 | true | false |
| 43 | run | <code>tail -180 /tmp/run2.log; grep -E '✗&#124;ERROR&#124;layer complete' /tmp/run2.log</code> | 15611 | true | false |
| 49 | run | <code>for f in sql/staging/*.sql; do echo ==== $f; grep -E 'md5&#124;history_unique_key&#124;created_date as&#124;last_modified_date' $f; done; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=</code> | 14873 | true | false |
| 55 | run | <code>cat sql/staging/stg_salesforce__contact.sql; cat sql/staging/stg_salesforce__user.sql; cat sql/staging/stg_salesforce__event.sql</code> | 4202 | false | false |
| 57 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br># Correct field source mapping; canonical foreign keys should remain FK columns, not the row's own id.<br>fixes={<br>'stg_salesforce__contact':'id as account_id','st</code> | 3263 | false | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml,pathlib<br>c=duckdb.connect('salesforce.duckdb',read_only=True)<br>con=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer, schema, key in [('staging_contract','stag</code> | 589 | true | false |
| 65 | run | <code>head -10 sql/staging/stg_salesforce__user.sql &amp;&amp; head -8 sql/staging/stg_salesforce__contact.sql &amp;&amp; head -5 sql/staging/stg_salesforce__opportunity.sql; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect(</code> | 1340 | false | false |
| 67 | run | <code>for f in sql/staging/*.sql; do printf '%-55s ' "$(basename "$f")"; sed -n '2p' "$f"; done</code> | 1156 | true | false |
| 69 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>fix={'stg_salesforce__account_history.sql':('id as account_id','account_id as account_id'), 'stg_salesforce__contact_history.sql':('id as contact_id','id as co</code> | 997 | true | false |
| 71 | run | <code>sed -i 's/account_account_id/account_id/g' sql/staging/stg_salesforce__account_history.sql sql/staging/stg_salesforce__opportunity_history.sql; python run.py &gt; /tmp/run7.log 2&gt;&amp;1; grep -E '✗&#124;ERROR&#124;lay</code> | 1397 | true | false |
| 83 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('salesforce.duckdb',read_only=True)<br>for layer,sch in [('staging_contract','staging</code> | 225 | false | false |
| 85 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('salesforce.duckdb',read_only=True)<br>for layer,sch in [('staging_contract','staging</code> | 295 | true | false |
| 87 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_salesforce__contact.sql');s=p.read_text()<br>s=s.replace('      account_id as account_id,',"      case when account_id is null or (regexp_</code> | 331 | false | false |
| 89 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=True); spec=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in spec['staging_contract']['tables']:<br> name=t['name</code> | 1149 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
   if name=='email' and n in ('stg_salesforce__contact','stg_salesforce__user'): expr='lower(trim(email))'
```
event 19 / message

```text
 if n=='stg_salesforce__user': filters=['id is not null','email is not null',"regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')",'length(lower(trim(email))) <= 255','is_active is not null','last_name is not null','name is not null','username is not null']
```
event 23 / message

```text
    from staging.stg_salesforce__user where is_active = true
```
event 25 / message

```text
    left join staging.stg_salesforce__user u on o.owner_id=u.user_id
```
event 25 / message

```text
from staging.stg_salesforce__user u
```
event 27 / message

```text
 from staging.stg_salesforce__user where is_active=true
```
event 27 / message

```text
 from staging.stg_salesforce__user where is_active=true
```
event 27 / message

```text
 left join staging.stg_salesforce__user u on ae.owner_id=u.user_id and u.is_active=true
```
event 29 / message

```text
 from staging.stg_salesforce__user u
```
event 29 / message

```text
 left join staging.stg_salesforce__user m on u.manager_id=m.user_id
```
event 29 / message

```text
left join staging.stg_salesforce__user u on c.owner_id=u.user_id
```
event 29 / message

```text
 left join staging.stg_salesforce__user ou on o.owner_id=ou.user_id
```
event 29 / message

```text
 left join staging.stg_salesforce__user mu on ou.manager_id=mu.user_id
```
event 31 / message

```text
 left join staging.stg_salesforce__user u on opp.owner_id=u.user_id
```
event 31 / message

```text
 select count(*) as total_users,count(*) filter(where is_active is true) as active_users from staging.stg_salesforce__user
```
event 33 / message

```text
from manager_rollup r left join staging.stg_salesforce__user u on r.manager_id=u.user_id
```
event 49 / message

```text
for t in ['stg_salesforce__account','stg_salesforce__contact','stg_salesforce__opportunity','stg_salesforce__user','stg_salesforce__lead','stg_salesforce__event']:
```
event 55 / message

```text
Running command: cat sql/staging/stg_salesforce__contact.sql; cat sql/staging/stg_salesforce__user.sql; cat sql/staging/stg_salesforce__event.sql
```
event 57 / message

```text
'stg_salesforce__contact':'id as account_id','stg_salesforce__user':'id as account_id,',
```
event 57 / message

```text
 if table=='stg_salesforce__user':
```
event 65 / message

```text
Running command: head -10 sql/staging/stg_salesforce__user.sql && head -8 sql/staging/stg_salesforce__contact.sql && head -5 sql/staging/stg_salesforce__opportunity.sql; python - <<'PY'
```
event 71 / message

```text
for t,cols in [('stg_salesforce__contact',['account_id','contact_id']),('stg_salesforce__user',['user_id','account_id','contact_id','user_role_id']),('stg_salesforce__opportunity',['opportunity_id','account_id']),('stg_salesforce__account_history',['account_id','history_unique_key']),('stg_salesforce__contact_history',['contact_id','account_id']),('stg_salesforce__opportunity_history',['opportunity_id','account_id'])]:
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__user.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__user.sql`
- S6: `records/006_contract_impl-018.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/.tmp/result.md`
- S10: `data/023_packages_work/023_impl-018_stg_salesforce__user/023_impl-018_stg_salesforce__user.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions`
