# impl-020 | staging | stg_intercom__contact_history | 差异：S1；日期 原记录

## 契约完整原文

S3:94–140

```yaml
    - name: stg_intercom__contact_history
      description: "Contact attributes over time with standardized identifiers, email, and phone normalization."
      source_table: raw.contact_history_data
      columns:
        - name: contact_id
          data_type: VARCHAR
        - name: admin_id
          data_type: BIGINT
        - name: created_at
          data_type: TIMESTAMP
        - name: updated_at
          data_type: TIMESTAMP
        - name: signed_up_at
          data_type: TIMESTAMP
        - name: contact_name
          data_type: VARCHAR
          validation_rules:
            - rule: "contact_name = TRIM(contact_name)"
              on_failure: correct
        - name: contact_role
          data_type: VARCHAR
        - name: contact_email
          data_type: VARCHAR
          validation_rules:
            - rule: "contact_email = LOWER(TRIM(contact_email))"
              on_failure: correct
        - name: last_replied_at
          data_type: TIMESTAMP
        - name: last_email_clicked_at
          data_type: TIMESTAMP
        - name: last_email_opened_at
          data_type: TIMESTAMP
        - name: last_contacted_at
          data_type: TIMESTAMP
        - name: is_unsubscribed_from_emails
          data_type: BOOLEAN
        - name: phone
          data_type: VARCHAR
          validation_rules:
            - rule: "Normalize to E.164 where deterministically possible"
              on_failure: correct
            - rule: "phone IS NULL OR phone matches E.164 (^[+][1-9][0-9]{1,14}$)"
              on_failure: nullify_field
      row_filters:
        - rule: "Retain record unless _fivetran_active is explicitly false after type coercion (null or missing treated as active)"
          on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
with typed as (
    select
        try_cast(id as varchar) as contact_id,
        try_cast(admin_id as bigint) as admin_id,
        try_cast(created_at as timestamp) as created_at,
        try_cast(updated_at as timestamp) as updated_at,
        try_cast(signed_up_at as timestamp) as signed_up_at,
        trim(try_cast(name as varchar)) as contact_name,
        try_cast(role as varchar) as contact_role,
        lower(trim(try_cast(email as varchar))) as contact_email,
        try_cast(last_replied_at as timestamp) as last_replied_at,
        try_cast(last_email_clicked_at as timestamp) as last_email_clicked_at,
        try_cast(last_email_opened_at as timestamp) as last_email_opened_at,
        try_cast(last_contacted_at as timestamp) as last_contacted_at,
        coalesce(try_cast(unsubscribed_from_emails as boolean), false) as is_unsubscribed_from_emails,
        nullif(regexp_replace(trim(try_cast(phone as varchar)), '[^0-9+]', '', 'g'), '') as normalized_phone,
        coalesce(try_cast(_fivetran_active as boolean), true) as is_active
    from raw.contact_history_data
), normalized as (
    select *,
        case
            when normalized_phone is null then null
            when regexp_matches(normalized_phone, '^\+[1-9][0-9]{1,14}$') then normalized_phone
            else null
        end as phone_e164
    from typed
)
select contact_id, admin_id, created_at, updated_at, signed_up_at, contact_name, contact_role,
       contact_email, last_replied_at, last_email_clicked_at, last_email_opened_at, last_contacted_at,
       is_unsubscribed_from_emails, phone_e164 as phone
from normalized
where is_active
```

## gold SQL（仅供定位差异）

S5

```sql
with src as (
  select
    id as contact_id,
    admin_id,
    created_at,
    updated_at,
    signed_up_at,
    trim(name) as contact_name,
    role as contact_role,
    lower(trim(email)) as contact_email,
    last_replied_at,
    last_email_clicked_at,
    last_email_opened_at,
    last_contacted_at,
    unsubscribed_from_emails as is_unsubscribed_from_emails,
    phone
  from raw.contact_history_data
  where coalesce(try_cast(_fivetran_active as BOOLEAN), true)
),
phone_clean as (
  select
    *,
    -- normalize phone by stripping non-digits and enforcing + prefix if possible
    case
      when phone is null then null
      else regexp_replace(phone, '[^0-9+]', '', 'g')
    end as phone_norm1
  from src
),
phone_fix as (
  select
    contact_id,
    admin_id,
    created_at,
    updated_at,
    signed_up_at,
    contact_name,
    contact_role,
    contact_email,
    last_replied_at,
    last_email_clicked_at,
    last_email_opened_at,
    last_contacted_at,
    is_unsubscribed_from_emails,
    case
      when phone_norm1 ~ '^\\+[1-9]\\d{1,14}$' then phone_norm1
      when phone_norm1 ~ '^[1-9]\\d{1,14}$' then '+' || phone_norm1
      else null
    end as phone
  from phone_clean
)
select *
from phone_fix
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2707 | 2707 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"contact_id":"00cb8207379143a491a66007"}</code> |
| K2 | <code>{"contact_id":"00cdd4a36b6d4928be88fb45"}</code> |
| K3 | <code>{"contact_id":"00f3fdb6b6154ab583f65df0"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| admin_id | 0 | 0 | 0 | BIGINT | VARCHAR |
| contact_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| contact_role | 0 | 0 | 0 | VARCHAR | VARCHAR |
| contact_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| phone | 1079 | 1079 | 1079 | VARCHAR | VARCHAR |

phone 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | +14483208958 | null |
| K2 | +17318302205 | null |
| K3 | +16866283958 | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"is_unsubscribed_from_emails","value":"false"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory print('null email fields etc',c.execute('select count(*) from staging.stg_intercom__contact_history where phone is not null and not regexp_matches(phone, \'^\\+[1-9][0-9]{1,14}$\')').fetchone())</code> |

## 轨迹索引（不放输出原文）

本题事件总数：63；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 7463 | true | false |
| 11 | run | <code>cat intercom_start.yaml &amp;&amp; sed -n '1,240p' test_single_sql.py</code> | 8424 | false | false |
| 13 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,260p' docs/data_contract.yaml</code> | 9929 | true | false |
| 17 | run | <code>sed -n '560,930p' docs/data_contract.yaml</code> | 15887 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('intercom_start.duckdb',read_only=True)<br>for t in c.execute('show tables').fetchall():<br> n=t[0]<br> print('\n',n,c.execute(f'select count(*) from "{n}"').fetc</code> | 14942 | false | false |
| 25 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/build.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging'); I=Path('sql/intermediate'); M=Path('sql/marts')<br>def put(path,sql): path.wr</code> | 0 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/build.py &lt;&lt;'PY'<br># Marts<br>put(M/'intercom__company_enhanced.sql', '''select h.company_id, h.company_name, h.website, h.website_domain, h.industry, h.created_at, h.updated_at,<br>       h.user_c</code> | 1467 | true | false |
| 29 | run | python run.py | 4056 | true | false |
| 37 | run | <code>cat &gt; sql/staging/stg_intercom__conversation_part_history.sql &lt;&lt;'SQL'<br>with source_rows as (<br>    select<br>        try_cast(id as varchar) as conversation_part_id,<br>        coalesce(try_cast(part_type as v</code> | 1094 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('intercom.duckdb',read_only=True)<br>for schema,table,key in [('staging','stg_intercom__conversation_history','conversation_id'),('intermediate','int_interc</code> | 408 | false | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>p='sql/marts/intercom__company_metrics.sql'<br>s=open(p).read()<br>s=s.replace("""convo_time_metrics as (<br>    select cc.company_id,<br>           median(cm.time_to_first_response_minutes)::doub</code> | 4130 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_intercom__contact_history.sql'<br>s=open(p).read()<br>s=s.replace("            when regexp_matches(normalized_phone, '^[1-9][0-9]{1,14}$') then '+' &#124;&#124; normalized_phone\n",</code> | 5905 | false | false |

### agent action 的 thought/message 命中原句

event 25 / message

```text
put(S/'stg_intercom__contact_history.sql', '''
```
event 25 / message

```text
    from staging.stg_intercom__contact_history
```
event 39 / message

```text
print('null email fields etc',c.execute('select count(*) from staging.stg_intercom__contact_history where phone is not null and not regexp_matches(phone, \'^\\+[1-9][0-9]{1,14}$\')').fetchone())
```
event 45 / message

```text
p='sql/staging/stg_intercom__contact_history.sql'
```
event 45 / message

```text
p=Path('sql/staging/stg_intercom__contact_history.sql')
```
event 45 / message

```text
c.execute(f'create or replace table staging.stg_intercom__contact_history as ({p.read_text()})')
```
event 45 / message

```text
print('staging contact rows',c.execute('select count(*) from staging.stg_intercom__contact_history').fetchone()[0])
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-020.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/staging/stg_intercom__contact_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/sql/staging/stg_intercom__contact_history.sql`
- S6: `records/006_contract_impl-020.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/result.md`
- S10: `data/023_packages_work/023_impl-020_stg_intercom__contact_history/023_impl-020_stg_intercom__contact_history.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions`
