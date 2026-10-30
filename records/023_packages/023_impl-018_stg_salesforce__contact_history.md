# impl-018 | staging | stg_salesforce__contact_history | 差异：S1；日期 原记录

## 契约完整原文

S3:917–966

```yaml
    - name: stg_salesforce__contact_history
      description: "Cleaned contact history records tracking changes to contact data over time"
      source_table: raw.contact_history
      columns:
        - name: contact_id
          data_type: VARCHAR
        - name: account_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: contact_description
          data_type: VARCHAR
        - name: email
          data_type: VARCHAR
        - name: first_name
          data_type: VARCHAR
        - name: is_deleted
          data_type: BOOLEAN
        - name: last_activity_date
          data_type: DATE
        - name: last_modified_date
          data_type: TIMESTAMP
        - name: last_name
          data_type: VARCHAR
        - name: lead_source
          data_type: VARCHAR
        - name: mailing_city
          data_type: VARCHAR
        - name: mailing_country
          data_type: VARCHAR
        - name: mailing_postal_code
          data_type: VARCHAR
        - name: mailing_state
          data_type: VARCHAR
        - name: mailing_street
          data_type: VARCHAR
        - name: mobile_phone
          data_type: VARCHAR
        - name: contact_name
          data_type: VARCHAR
        - name: owner_id
          data_type: VARCHAR
        - name: phone
          data_type: VARCHAR
        - name: title
          data_type: VARCHAR
        - name: history_unique_key
          data_type: VARCHAR
          constraints: [not_null, unique]

```

## agent 最终 SQL

S4

```sql
select
      id as contact_id,
      account_id as account_id,
      try_cast(_fivetran_start as TIMESTAMP) as created_date,
      description as contact_description,
      email as email,
      first_name as first_name,
      is_deleted as is_deleted,
      try_cast(last_activity_date as DATE) as last_activity_date,
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
      last_name as last_name,
      lead_source as lead_source,
      mailing_city as mailing_city,
      mailing_country as mailing_country,
      mailing_postal_code as mailing_postal_code,
      mailing_state as mailing_state,
      mailing_street as mailing_street,
      mobile_phone as mobile_phone,
      name as contact_name,
      owner_id as owner_id,
      phone as phone,
      title as title,
      md5(concat_ws('|', coalesce(cast(contact_id as varchar), ''), coalesce(cast(_fivetran_start as varchar), ''), coalesce(cast(_fivetran_end as varchar), ''))) as history_unique_key
from raw.contact_history
where id is not null
qualify row_number() over (partition by id order by id) = 1
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *   
    from raw.contact_history
),

final as (
    select 
        cast(id as varchar) as contact_id,
        cast(account_id as varchar) as account_id,
        cast(current_timestamp as timestamp) as created_date,
        cast(description as varchar) as contact_description,
        cast(email as varchar) as email,
        cast(first_name as varchar) as first_name,
        cast(coalesce(is_deleted, false) as boolean) as is_deleted,
        cast(last_activity_date as date) as last_activity_date,
        cast(last_modified_date as timestamp) as last_modified_date,
        cast(last_name as varchar) as last_name,
        cast(lead_source as varchar) as lead_source,
        cast(mailing_city as varchar) as mailing_city,
        cast(mailing_country as varchar) as mailing_country,
        cast(mailing_postal_code as varchar) as mailing_postal_code,
        cast(mailing_state as varchar) as mailing_state,
        cast(mailing_street as varchar) as mailing_street,
        cast(mobile_phone as varchar) as mobile_phone,
        cast(name as varchar) as contact_name,
        cast(owner_id as varchar) as owner_id,
        cast(phone as varchar) as phone,
        cast(title as varchar) as title,
        -- Generate unique key for history tracking
        concat(id, '_', created_date::varchar) as history_unique_key
    from base
)

select *
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2434 | 3000 | 2434 | 2434 | 0 | 517 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| first_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| last_modified_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| last_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| lead_source | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_postal_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_street | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mobile_phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| title | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"history_unique_key":"002399127cd2581298608cb8318486b4"},{"history_unique_key":"003bc774cae10a911899b18bd801cda9"},{"history_unique_key":"00b13c71b6612a4c1f52b1061d823522"},{"history_unique_key":"00be14b960f6c756c7cfb336f0fbf770"},{"history_unique_key":"00ca4cfbf5f6be660631e51328c144f2"}]</code> | <code>[{"history_unique_key":"00301oeYPsRAbxH_2025-10-24 15:24:19.642344"},{"history_unique_key":"00302EQ38cvTeOD_2025-10-24 15:24:19.642344"},{"history_unique_key":"00302XSINEEu7pO_2025-10-24 15:24:19.642344"},{"history_unique_key":"00306XQXXhoKuF1_2025-10-24 15:24:19.642344"},{"history_unique_key":"0030A7Jvr5HKj2V_2025-10-24 15:24:19.642344"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"is_deleted","value":"false"}]</code> |
| C9_gold_runtime_text | <code>S5:10 current_timestamp；命中数=1</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory  if n=='stg_salesforce__contact_history': filters=['id is not null']</code> |

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
| 29 | run | <code>cat &gt; sql/marts/dim_salesforce__user.sql &lt;&lt;'SQL'<br>with user_base as (<br> select u.*,ur.user_role_name,ur.developer_name,ur.parent_role_id,ur.rollup_description,<br> m.user_id as matched_manager_id,m.first_n</code> | 0 | false | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>src=yaml.safe_load(open('salesforce_start.yaml')); co=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br>mp={'account_id':'id','account_name':'na</code> | 847 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_salesforce__contact.sql'<br>s=open(p).read().replace('try_cast(created_date as TIMESTAMP) as created_date','cast(null as TIMESTAMP) as created_date')<br>open(p,'w').write(</code> | 0 | false | false |
| 39 | run | <code>tail -120 /tmp/run.log &amp;&amp; ls -lh salesforce.duckdb</code> | 1338 | false | false |
| 43 | run | <code>tail -180 /tmp/run2.log; grep -E '✗&#124;ERROR&#124;layer complete' /tmp/run2.log</code> | 15611 | true | false |
| 49 | run | <code>for f in sql/staging/*.sql; do echo ==== $f; grep -E 'md5&#124;history_unique_key&#124;created_date as&#124;last_modified_date' $f; done; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=</code> | 14873 | true | false |
| 53 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_salesforce__contact_history.sql');s=p.read_text().replace('id as account_id,','account_id as account_id,');p.write_text(s)<br>p=Path('sql/</code> | 331 | false | false |
| 57 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br># Correct field source mapping; canonical foreign keys should remain FK columns, not the row's own id.<br>fixes={<br>'stg_salesforce__contact':'id as account_id','st</code> | 3263 | true | false |
| 59 | run | <code>grep -n account_ sql/staging/stg_salesforce__{opportunity,contact_history,opportunity_history}.sql</code> | 270 | true | false |
| 61 | run | <code>sed -i 's/account_account_id/account_id/g' sql/staging/stg_salesforce__opportunity.sql sql/staging/stg_salesforce__contact_history.sql sql/staging/stg_salesforce__opportunity_history.sql; python run.p</code> | 331 | false | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml,pathlib<br>c=duckdb.connect('salesforce.duckdb',read_only=True)<br>con=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer, schema, key in [('staging_contract','stag</code> | 589 | true | false |
| 67 | run | <code>for f in sql/staging/*.sql; do printf '%-55s ' "$(basename "$f")"; sed -n '2p' "$f"; done</code> | 1156 | true | false |
| 69 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>fix={'stg_salesforce__account_history.sql':('id as account_id','account_id as account_id'), 'stg_salesforce__contact_history.sql':('id as contact_id','id as co</code> | 997 | true | false |
| 71 | run | <code>sed -i 's/account_account_id/account_id/g' sql/staging/stg_salesforce__account_history.sql sql/staging/stg_salesforce__opportunity_history.sql; python run.py &gt; /tmp/run7.log 2&gt;&amp;1; grep -E '✗&#124;ERROR&#124;lay</code> | 1397 | true | false |
| 79 | run | <code>grep -A8 -B3 'stg_salesforce__account_history:' /tmp/run8.log; cat sql/staging/stg_salesforce__account_history.sql</code> | 2395 | true | false |
| 89 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=True); spec=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in spec['staging_contract']['tables']:<br> name=t['name</code> | 1149 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
   keyid={'stg_salesforce__account_history':'account_id','stg_salesforce__contact_history':'contact_id','stg_salesforce__opportunity_history':'opportunity_id'}.get(n,'id')
```
event 19 / message

```text
 if n=='stg_salesforce__contact_history': filters=['id is not null']
```
event 29 / message

```text
 from staging.stg_salesforce__contact_history where is_deleted is false
```
event 53 / message

```text
p=Path('sql/staging/stg_salesforce__contact_history.sql');s=p.read_text().replace('id as account_id,','account_id as account_id,');p.write_text(s)
```
event 57 / message

```text
'stg_salesforce__contact_history':'id as account_id,'
```
event 61 / message

```text
Running command: sed -i 's/account_account_id/account_id/g' sql/staging/stg_salesforce__opportunity.sql sql/staging/stg_salesforce__contact_history.sql sql/staging/stg_salesforce__opportunity_history.sql; python run.py > /tmp/run6.log 2>&1; grep -E '✗|ERROR|layer complete|completed successfully' /tmp/run6.log
```
event 69 / message

```text
fix={'stg_salesforce__account_history.sql':('id as account_id','account_id as account_id'), 'stg_salesforce__contact_history.sql':('id as contact_id','id as contact_id'), 'stg_salesforce__opportunity_history.sql':('id as account_id','account_id as account_id')}
```
event 69 / message

```text
p=Path('sql/staging/stg_salesforce__contact_history.sql');s=p.read_text();
```
event 71 / message

```text
for t,cols in [('stg_salesforce__contact',['account_id','contact_id']),('stg_salesforce__user',['user_id','account_id','contact_id','user_role_id']),('stg_salesforce__opportunity',['opportunity_id','account_id']),('stg_salesforce__account_history',['account_id','history_unique_key']),('stg_salesforce__contact_history',['contact_id','account_id']),('stg_salesforce__opportunity_history',['opportunity_id','account_id'])]:
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__contact_history.sql`
- S6: `records/006_contract_impl-018.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/.tmp/result.md`
- S10: `data/023_packages_work/023_impl-018_stg_salesforce__contact_history/023_impl-018_stg_salesforce__contact_history.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions`
