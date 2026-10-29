# impl-003 | marts | customer360__mapping | 差异：S1；日期 原记录

## 契约完整原文

S3:1820–1874

```yaml
    - name: customer360__mapping
      description: Customer identity mapping linking unified and organizational hashes to source system records and an organization-level header row with aggregated metadata
      grain: 'Mixed: individual rows per combined source record (is_organization_header=false) and one header row per customer360_organization_id (is_organization_header=true)'
      source_models:
      - intermediate.int_customer360__source_matches
      - intermediate.int_customer360__marketo
      - intermediate.int_customer360__stripe
      - intermediate.int_customer360__zendesk
      business_logic: '1) Load four inputs: source_matches, marketo, stripe, zendesk. 2) Build combine_all_results: - Chain full outer joins: source_matches to marketo on lead_id, then to stripe on customer_id from source_matches, then to zendesk on user_id from source_matches, retaining all records from every source. - For IDs, prefer the value from source_matches when present; otherwise use the corresponding source table value. - Per-row timestamps: - marketo_updated_at = the most recent non-null updated_at among marketo/stripe/zendesk for that row, taking source_matches timestamps when available, else the source table’s. - marketo_created_at = the earliest non-null created_at among marketo/stripe/zendesk for that row, taking source_matches timestamps when available, else the source table’s. - stripe_updated_at / stripe_created_at = the stripe timestamp from source_matches when present, otherwise from stripe. - zendesk_updated_at / zendesk_created_at = the zendesk timestamp from source_matches when present, otherwise from zendesk. - zendesk_organization_* = the zendesk organization timestamps from source_matches when present, otherwise from zendesk.organization_*. - Union in three additional sets to also include any marketo/stripe/zendesk records whose IDs are not present in source_matches; these rows carry only their own system fields, others null. This can yield duplicates relative to the full outer joins. 3) For each row, derive customer360_organization_id by hashing the pipe-joined values (marketo org name without suffix, marketo inferred org name without suffix, stripe customer org name without suffix, stripe shipping org name without suffix, zendesk organization_id), treating nulls as empty strings. 4) Emit two row types: - Individual rows (is_organization_header=false): include the three source IDs; source_ids is a compact JSON-like object {"marketo":"...","stripe":"...","zendesk":"..."} where null IDs are rendered as empty strings; timestamps are the per-row values from step 2. - One organization header row per customer360_organization_id (is_organization_header=true): source IDs are null; source_ids is a JSON-like object with arrays per system containing distinct quoted IDs for that organization (comma-delimited, no spaces), with nulls rendered as empty strings; timestamps aggregated per organization as latest updated_at and earliest created_at for each system; zendesk organization timestamps use latest for updated and earliest for created. 5) Assign customer360_id by hashing the pipe-joined values (marketo_lead_id, stripe_customer_id, zendesk_user_id, is_organization_header, customer360_organization_id), treating nulls as empty strings and using the engine’s string form of the boolean.'
      columns:
      - name: customer360_id
        data_type: VARCHAR
        description: Deterministic 32-character hex md5 of marketo_lead_id|stripe_customer_id|zendesk_user_id|is_organization_header|customer360_organization_id with nulls as empty strings and the engine’s string form of the boolean.
      - name: customer360_organization_id
        data_type: VARCHAR
        description: Deterministic 32-character hex md5 of marketo_org_name_no_suffix|marketo_inferred_org_name_no_suffix|stripe_customer_org_name_no_suffix|stripe_shipping_org_name_no_suffix|zendesk_organization_id with nulls as empty strings.
      - name: marketo_lead_id
        data_type: BIGINT
        description: Marketo lead ID; on individual rows prefer source_matches, else marketo; null on organization header rows.
      - name: stripe_customer_id
        data_type: VARCHAR
        description: Stripe customer ID; on individual rows prefer source_matches, else stripe; null on organization header rows.
      - name: zendesk_user_id
        data_type: BIGINT
        description: Zendesk user ID; on individual rows prefer source_matches, else zendesk; null on organization header rows.
      - name: is_organization_header
        data_type: BOOLEAN
        description: 'Row type flag: false for individual rows; true for the single aggregated header row per customer360_organization_id.'
      - name: source_ids
        data_type: VARCHAR
        description: 'JSON-like string; individual rows: {"marketo":"...","stripe":"...","zendesk":"..."} with nulls as empty strings; header rows: arrays per system of distinct quoted IDs joined by commas (no spaces), nulls as empty strings, order not enforced.'
      - name: marketo_updated_at
        data_type: TIMESTAMP
        description: 'Individual rows: latest non-null updated_at across marketo, stripe, and zendesk after preferring source_matches timestamps; header rows: latest marketo_updated_at in the organization; null if none.'
      - name: marketo_created_at
        data_type: TIMESTAMP
        description: 'Individual rows: earliest non-null created_at across marketo, stripe, and zendesk after preferring source_matches timestamps; header rows: earliest marketo_created_at in the organization; null if none.'
      - name: stripe_updated_at
        data_type: TIMESTAMP
        description: 'Individual rows: stripe updated_at from source_matches when available, otherwise from stripe; header rows: latest stripe_updated_at in the organization; null if none.'
      - name: stripe_created_at
        data_type: TIMESTAMP
        description: 'Individual rows: stripe created_at from source_matches when available, otherwise from stripe; header rows: earliest stripe_created_at in the organization; null if none.'
      - name: zendesk_updated_at
        data_type: TIMESTAMP
        description: 'Individual rows: zendesk updated_at from source_matches when available, otherwise from zendesk; header rows: latest zendesk_updated_at in the organization; null if none.'
      - name: zendesk_organization_updated_at
        data_type: TIMESTAMP
        description: 'Individual rows: zendesk organization_updated_at from source_matches when available, otherwise from zendesk; header rows: latest org updated_at in the organization; null if none.'
      - name: zendesk_created_at
        data_type: TIMESTAMP
        description: 'Individual rows: zendesk created_at from source_matches when available, otherwise from zendesk; header rows: earliest zendesk_created_at in the organization; null if none.'
      - name: zendesk_organization_created_at
        data_type: TIMESTAMP
        description: 'Individual rows: zendesk organization_created_at from source_matches when available, otherwise from zendesk; header rows: earliest org created_at in the organization; null if none.'
```

## agent 最终 SQL

S4

```sql
with source_rows as (
 select sm.marketo_lead_id, sm.stripe_customer_id, sm.zendesk_user_id,
        m.organization_name_no_suffix as m_org, m.inferred_organization_name_no_suffix as mi_org,
        s.customer_organization_name_no_suffix as s_org, s.shipping_organization_name_no_suffix as ss_org,
        z.organization_id, sm.marketo_updated_at, sm.marketo_created_at, sm.stripe_updated_at, sm.stripe_created_at,
        sm.zendesk_updated_at, sm.zendesk_organization_updated_at, sm.zendesk_created_at, sm.zendesk_organization_created_at
 from intermediate.int_customer360__source_matches sm
 left join intermediate.int_customer360__marketo m on sm.marketo_lead_id=m.lead_id
 left join intermediate.int_customer360__stripe s on sm.stripe_customer_id=s.customer_id
 left join intermediate.int_customer360__zendesk z on sm.zendesk_user_id=z.user_id
 union all
 select m.lead_id,null::varchar,null::bigint,m.organization_name_no_suffix,m.inferred_organization_name_no_suffix,null,null,null,m.updated_at,m.created_at,null,null,null,null,null,null
 from intermediate.int_customer360__marketo m where not exists (select 1 from intermediate.int_customer360__source_matches sm where sm.marketo_lead_id=m.lead_id)
 union all
 select null,s.customer_id,null,null,null,s.customer_organization_name_no_suffix,s.shipping_organization_name_no_suffix,null,s.updated_at,s.created_at,s.updated_at,s.created_at,null,null,null,null
 from intermediate.int_customer360__stripe s where not exists (select 1 from intermediate.int_customer360__source_matches sm where sm.stripe_customer_id=s.customer_id)
 union all
 select null,null,z.user_id,null,null,null,null,z.organization_id,z.updated_at,z.created_at,null,null,z.updated_at,z.organization_updated_at,z.created_at,z.organization_created_at
 from intermediate.int_customer360__zendesk z where not exists (select 1 from intermediate.int_customer360__source_matches sm where sm.zendesk_user_id=z.user_id)
), organization_keys as (
 select *, md5(coalesce(m_org,'')||'|'||coalesce(mi_org,'')||'|'||coalesce(s_org,'')||'|'||coalesce(ss_org,'')||'|'||coalesce(organization_id::varchar,'')) as customer360_organization_id
 from source_rows
), individuals as (
 select md5(coalesce(marketo_lead_id::varchar,'')||'|'||coalesce(stripe_customer_id,'')||'|'||coalesce(zendesk_user_id::varchar,'')||'|false|'||customer360_organization_id) as customer360_id,
 customer360_organization_id, marketo_lead_id, stripe_customer_id, zendesk_user_id, false as is_organization_header,
 '{"marketo":"'||coalesce(marketo_lead_id::varchar,'')||'","stripe":"'||coalesce(stripe_customer_id,'')||'","zendesk":"'||coalesce(zendesk_user_id::varchar,'')||'"}' as source_ids,
 greatest(marketo_updated_at, stripe_updated_at, zendesk_updated_at) as marketo_updated_at,
 least(marketo_created_at, stripe_created_at, zendesk_created_at) as marketo_created_at,
 stripe_updated_at, stripe_created_at, zendesk_updated_at, zendesk_organization_updated_at,zendesk_created_at,zendesk_organization_created_at
 from organization_keys
), headers as (
 select md5('|||'||'true|'||customer360_organization_id) as customer360_id, customer360_organization_id,
 null::bigint as marketo_lead_id,null::varchar as stripe_customer_id,null::bigint as zendesk_user_id,true as is_organization_header,
 '{"marketo":['||coalesce(string_agg(distinct '"'||coalesce(marketo_lead_id::varchar,'')||'"',','),'')||'],"stripe":['||coalesce(string_agg(distinct '"'||coalesce(stripe_customer_id,'')||'"',','),'')||'],"zendesk":['||coalesce(string_agg(distinct '"'||coalesce(zendesk_user_id::varchar,'')||'"',','),'')||']}' as source_ids,
 max(marketo_updated_at) as marketo_updated_at,min(marketo_created_at) as marketo_created_at,max(stripe_updated_at) as stripe_updated_at,min(stripe_created_at) as stripe_created_at,
 max(zendesk_updated_at) as zendesk_updated_at,max(zendesk_organization_updated_at) as zendesk_organization_updated_at,min(zendesk_created_at) as zendesk_created_at,min(zendesk_organization_created_at) as zendesk_organization_created_at
 from organization_keys group by customer360_organization_id
)
select * from individuals union all select * from headers
```

## gold SQL（仅供定位差异）

S5

```sql
-- Customer mapping table based on original DBT logic, using real source matches data
with source_matches as (
    select * from intermediate.int_customer360__source_matches
),

marketo as (
    select * from intermediate.int_customer360__marketo
),

stripe as (
    select * from intermediate.int_customer360__stripe
),

zendesk as (
    select * from intermediate.int_customer360__zendesk
),

-- Merge all source system data and generate customer360_id
combine_all_results as (
    select
        coalesce(source_matches.marketo_lead_id, marketo.lead_id) as marketo_lead_id,
        marketo.organization_name_no_suffix as marketo_organization_name,
        marketo.inferred_organization_name_no_suffix as marketo_inferred_organization_name,
        
        coalesce(source_matches.stripe_customer_id, stripe.customer_id) as stripe_customer_id,
        stripe.customer_organization_name_no_suffix as stripe_customer_organization_name,
        stripe.shipping_organization_name_no_suffix as stripe_shipping_organization_name,
        
        coalesce(source_matches.zendesk_user_id, zendesk.user_id) as zendesk_user_id,
        zendesk.organization_id as zendesk_organization_id,
        zendesk.organization_name as zendesk_organization_name,
        
        greatest(
            coalesce(source_matches.marketo_updated_at, marketo.updated_at),
            coalesce(source_matches.stripe_updated_at, stripe.updated_at),
            coalesce(source_matches.zendesk_updated_at, zendesk.updated_at)
        ) as marketo_updated_at,
        greatest(
            coalesce(source_matches.stripe_updated_at, stripe.updated_at)
        ) as stripe_updated_at,
        greatest(
            coalesce(source_matches.zendesk_updated_at, zendesk.updated_at)
        ) as zendesk_updated_at,
        coalesce(source_matches.zendesk_organization_updated_at, zendesk.organization_updated_at) as zendesk_organization_updated_at,
        least(
            coalesce(source_matches.marketo_created_at, marketo.created_at),
            coalesce(source_matches.stripe_created_at, stripe.created_at),
            coalesce(source_matches.zendesk_created_at, zendesk.created_at)
        ) as marketo_created_at,
        least(
            coalesce(source_matches.stripe_created_at, stripe.created_at)
        ) as stripe_created_at,
        least(
            coalesce(source_matches.zendesk_created_at, zendesk.created_at)
        ) as zendesk_created_at,
        coalesce(source_matches.zendesk_organization_created_at, zendesk.organization_created_at) as zendesk_organization_created_at

    from source_matches
    full outer join marketo 
        on marketo.lead_id = source_matches.marketo_lead_id
    full outer join stripe
        on stripe.customer_id = source_matches.stripe_customer_id
    full outer join zendesk
        on zendesk.user_id = source_matches.zendesk_user_id
    
    -- Also includes unmatched records
    union all
    
    select
        marketo.lead_id as marketo_lead_id,
        marketo.organization_name_no_suffix as marketo_organization_name,
        marketo.inferred_organization_name_no_suffix as marketo_inferred_organization_name,
        null as stripe_customer_id,
        null as stripe_customer_organization_name,
        null as stripe_shipping_organization_name,
        null as zendesk_user_id,
        null as zendesk_organization_id,
        null as zendesk_organization_name,
        marketo.updated_at as marketo_updated_at,
        null as stripe_updated_at,
        null as zendesk_updated_at,
        null as zendesk_organization_updated_at,
        marketo.created_at as marketo_created_at,
        null as stripe_created_at,
        null as zendesk_created_at,
        null as zendesk_organization_created_at
    from marketo
    where marketo.lead_id not in (select marketo_lead_id from source_matches where marketo_lead_id is not null)
    
    union all
    
    select
        null as marketo_lead_id,
        null as marketo_organization_name,
        null as marketo_inferred_organization_name,
        stripe.customer_id as stripe_customer_id,
        stripe.customer_organization_name_no_suffix as stripe_customer_organization_name,
        stripe.shipping_organization_name_no_suffix as stripe_shipping_organization_name,
        null as zendesk_user_id,
        null as zendesk_organization_id,
        null as zendesk_organization_name,
        null as marketo_updated_at,
        stripe.updated_at as stripe_updated_at,
        null as zendesk_updated_at,
        null as zendesk_organization_updated_at,
        null as marketo_created_at,
        stripe.created_at as stripe_created_at,
        null as zendesk_created_at,
        null as zendesk_organization_created_at
    from stripe
    where stripe.customer_id not in (select stripe_customer_id from source_matches where stripe_customer_id is not null)
    
    union all
    
    select
        null as marketo_lead_id,
        null as marketo_organization_name,
        null as marketo_inferred_organization_name,
        null as stripe_customer_id,
        null as stripe_customer_organization_name,
        null as stripe_shipping_organization_name,
        zendesk.user_id as zendesk_user_id,
        zendesk.organization_id as zendesk_organization_id,
        zendesk.organization_name as zendesk_organization_name,
        null as marketo_updated_at,
        null as stripe_updated_at,
        zendesk.updated_at as zendesk_updated_at,
        zendesk.organization_updated_at as zendesk_organization_updated_at,
        null as marketo_created_at,
        null as stripe_created_at,
        zendesk.created_at as zendesk_created_at,
        zendesk.organization_created_at as zendesk_organization_created_at
    from zendesk
    where zendesk.user_id not in (select zendesk_user_id from source_matches where zendesk_user_id is not null)
), 

-- Group by organization and generate organization_id
batch_organizations as (
    select
        *,
        -- Simplified organization ID generation logic, based on organization name, ensuring correct type
        md5(
            coalesce(marketo_organization_name, '') || '|' ||
            coalesce(marketo_inferred_organization_name, '') || '|' ||
            coalesce(stripe_customer_organization_name, '') || '|' ||
            coalesce(stripe_shipping_organization_name, '') || '|' ||
            coalesce(cast(zendesk_organization_id as varchar), '')
        ) as customer360_organization_id
    from combine_all_results
),

-- Create person records and organization header records
create_org_header_row as (
    select 
        customer360_organization_id,
        marketo_lead_id,
        stripe_customer_id,
        zendesk_user_id,
        false as is_organization_header,
        '{' ||
            '"marketo":"' || coalesce(cast(marketo_lead_id as varchar), '') || '",' ||
            '"stripe":"' || coalesce(stripe_customer_id, '') || '",' ||
            '"zendesk":"' || coalesce(cast(zendesk_user_id as varchar), '') || '"' ||
        '}' as source_ids,
        marketo_updated_at,
        marketo_created_at,
        stripe_updated_at,
        stripe_created_at,
        zendesk_updated_at,
        zendesk_organization_updated_at,
        zendesk_created_at,
        zendesk_organization_created_at
    from batch_organizations

    union all

    select 
        customer360_organization_id,
        null as marketo_lead_id,
        null as stripe_customer_id,
        null as zendesk_user_id,
        true as is_organization_header,
        '{' ||
            '"marketo":[' || string_agg(distinct '"' || coalesce(cast(marketo_lead_id as varchar), '') || '"', ',') || '],' ||
            '"stripe":[' || string_agg(distinct '"' || coalesce(stripe_customer_id, '') || '"', ',') || '],' ||
            '"zendesk":[' || string_agg(distinct '"' || coalesce(cast(zendesk_user_id as varchar), '') || '"', ',') || ']' ||
        '}' as source_ids,
        max(marketo_updated_at) as marketo_updated_at,
        min(marketo_created_at) as marketo_created_at,
        max(stripe_updated_at) as stripe_updated_at,
        min(stripe_created_at) as stripe_created_at,
        min(zendesk_created_at) as zendesk_created_at,
        max(zendesk_updated_at) as zendesk_updated_at,
        max(zendesk_organization_updated_at) as zendesk_organization_updated_at,
        min(zendesk_organization_created_at) as zendesk_organization_created_at
    from batch_organizations
    group by customer360_organization_id
),

-- Generate final customer360_id
final as (
    select 
        md5(
            coalesce(cast(marketo_lead_id as varchar), '') || '|' ||
            coalesce(stripe_customer_id, '') || '|' ||
            coalesce(cast(zendesk_user_id as varchar), '') || '|' ||
            cast(is_organization_header as varchar) || '|' ||
            customer360_organization_id
        ) as customer360_id,
        *
    from create_org_header_row
)

select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 12160 | 18036 | 0 | 0 | 78 | 5954 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"customer360_id":"000bd038cf03e102299f66d23ccfea08","customer360_organization_id":"9a41c3efc461aa5c412ecc525a5af14e","marketo_lead_id":"3088","stripe_customer_id":"null","zendesk_user_id":"null"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| customer360_id | 0 | 0 | 5876 | VARCHAR | VARCHAR |
| customer360_organization_id | 0 | 0 | 5876 | VARCHAR | VARCHAR |
| marketo_lead_id | 0 | 0 | 5876 | BIGINT | BIGINT |
| stripe_customer_id | 0 | 0 | 5876 | VARCHAR | VARCHAR |
| zendesk_user_id | 0 | 0 | 5876 | BIGINT | BIGINT |
| is_organization_header | 0 | 0 | 5876 | BOOLEAN | BOOLEAN |
| source_ids | 648 | 648 | 6524 | VARCHAR | VARCHAR |

customer360_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"000bd038cf03e102299f66d23ccfea08","rows":1}]</code> | <code>[{"value":"000bd038cf03e102299f66d23ccfea08","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

customer360_organization_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"9a41c3efc461aa5c412ecc525a5af14e","rows":1}]</code> | <code>[{"value":"9a41c3efc461aa5c412ecc525a5af14e","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

marketo_lead_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"3088","rows":1}]</code> | <code>[{"value":"3088","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

stripe_customer_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

zendesk_user_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

is_organization_header 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"false","rows":1}]</code> | <code>[{"value":"false","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

source_ids 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"{\"marketo\":\"3088\",\"stripe\":\"\",\"zendesk\":\"\"}","rows":1}]</code> | <code>[{"value":"{\"marketo\":\"3088\",\"stripe\":\"\",\"zendesk\":\"\"}","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| B5_null_literal_output | <code>9输出列；[{"column":"marketo_lead_id","expression":["sm.marketo_lead_id"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"is_organization_header","expression":["FALSE"]}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=40；assistant_trajectory  select m.customer360_id, s.email from marts.customer360__mapping m inner join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.email is not null</code> |

## 轨迹索引（不放输出原文）

本题事件总数：53；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 3128 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 11047 | true | false |
| 17 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>P=Path('sql')<br>def put(layer,name,sql):<br>    (P/layer/f'{name}.sql').write_text(sql.strip()+"\n")<br># STAGING</code> | 0 | false | false |
| 19 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('intermediate','int_customer360__customer_behavior_analysis', '''<br>with matches as (<br>    select * from intermediate.int_customer360__source_matches<br>), joined as (<br>    sel</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('intermediate','int_customer360__risk_assessment', '''<br>with behavior as (<br> select ba.*, lm.customer_health_score, lm.lifecycle_stage, lm.active_30_days, lm.active_90_day</code> | 0 | false | false |
| 23 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br># Generic distinct/index profile marts<br>put('marts','customer360__email', '''<br>with email_rows as (<br> select m.customer360_id, s.email from marts.customer360__mapping m inner j</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('marts','customer360__customer_value_analysis', '''<br>with base as (<br> select *,case when estimated_customer_value&gt;=5000 then 5 when estimated_customer_value&gt;=3000 then 4 w</code> | 0 | false | false |
| 29 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7140 | true | false |
| 33 | run | <code>grep -n ' m\.' sql/intermediate/int_customer360__customer_behavior_analysis.sql; grep -n -A6 -B4 'ERROR - ✗ intermediate.int_customer360__customer_behavior_analysis' /tmp/runlog</code> | 1764 | false | false |
| 37 | run | <code>grep -nE 's\.&#124;z\.' sql/intermediate/int_customer360__customer_behavior_analysis.sql</code> | 1249 | false | false |
| 43 | run | <code>cat &gt; sql/intermediate/int_customer360__source_matches.sql &lt;&lt;'SQL'<br>with marketo_stripe as (<br>    select<br>        m.lead_id as marketo_id,<br>        s.customer_id as stripe_id,<br>        m.updated_at as mark</code> | 394 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('customer360.duckdb',read_only=True)<br>checks={<br>'status_key_dups':"select count(*) from (select customer360_id from marts.customer360__status group by 1 ha</code> | 616 | true | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
put('marts','customer360__mapping', '''
```
event 23 / message

```text
 select m.customer360_id, s.email from marts.customer360__mapping m inner join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.email is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.email from marts.customer360__mapping m inner join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.email is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.email from marts.customer360__mapping m inner join intermediate.int_customer360__zendesk s on m.zendesk_user_id=s.user_id where s.email is not null
```
event 23 / message

```text
 select m.customer360_id,s.full_name_clean as full_name from marts.customer360__mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.full_name_clean is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.customer_name_clean from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.customer_name_clean is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.shipping_name_clean from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.shipping_name_clean is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.full_name_clean from marts.customer360__mapping m join intermediate.int_customer360__zendesk s on m.zendesk_user_id=s.user_id where s.full_name_clean is not null
```
event 23 / message

```text
 select m.customer360_id,s.organization_name_no_suffix as organization_name from marts.customer360__mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.organization_name_no_suffix is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.inferred_organization_name_no_suffix from marts.customer360__mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.inferred_organization_name_no_suffix is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.customer_organization_name_no_suffix from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.customer_organization_name_no_suffix is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.shipping_organization_name_no_suffix from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.shipping_organization_name_no_suffix is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.organization_name from marts.customer360__mapping m join intermediate.int_customer360__zendesk s on m.zendesk_user_id=s.user_id where s.organization_name is not null
```
event 23 / message

```text
 select m.customer360_id,s.phone,s.phone_extension::varchar as extension from marts.customer360__mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.phone is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.company_phone,s.company_phone_extension::varchar from marts.customer360__mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.company_phone is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.mobile_phone,s.mobile_phone_extension from marts.customer360__mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.mobile_phone is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.phone,s.phone_extension::varchar from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.phone is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.shipping_phone,s.shipping_phone_extension::varchar from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.shipping_phone is not null
```
event 23 / message

```text
 union all select m.customer360_id,s.phone,s.phone_extension::varchar from marts.customer360__mapping m join intermediate.int_customer360__zendesk s on m.zendesk_user_id=s.user_id where s.phone is not null
```
event 23 / message

```text
with mapping as (select * from marts.customer360__mapping), addresses as (
```
event 23 / message

```text
 select m.customer360_id,k.ip_address,k.updated_at from marts.customer360__mapping m join intermediate.int_customer360__marketo k on m.marketo_lead_id=k.lead_id where k.ip_address is not null
```
event 23 / message

```text
from marts.customer360__mapping m left join email_first e using(customer360_id) left join phone_first p using(customer360_id)
```
event 23 / message

```text
 from marts.customer360__mapping m inner join marts.customer360__summary s using(customer360_id)
```
event 23 / message

```text
 from marts.customer360__mapping m join intermediate.int_customer360__marketo k on m.marketo_lead_id=k.lead_id
```
event 23 / message

```text
 from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id
```
event 23 / message

```text
 from marts.customer360__mapping m join intermediate.int_customer360__zendesk z on m.zendesk_user_id=z.user_id
```
event 23 / message

```text
 select m.customer360_id,k.updated_at as last_updated,k.created_at as first_seen,'marketo' as source_system,'lead_update' as update_type from marts.customer360__mapping m join intermediate.int_customer360__marketo k on m.marketo_lead_id=k.lead_id
```
event 23 / message

```text
 union all select m.customer360_id,s.updated_at,s.created_at,'stripe','customer_update' from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id
```
event 23 / message

```text
 union all select m.customer360_id,z.updated_at,z.created_at,'zendesk','user_update' from marts.customer360__mapping m join intermediate.int_customer360__zendesk z on m.zendesk_user_id=z.user_id
```
event 45 / message

```text
'mapping_md5_invalid':"select count(*) from marts.customer360__mapping where length(customer360_id)<>32 or length(customer360_organization_id)<>32",
```
event 45 / message

```text
for s,t in [('intermediate','int_customer360__marketo'),('intermediate','int_customer360__stripe'),('intermediate','int_customer360__zendesk'),('intermediate','int_customer360__source_matches'),('intermediate','int_customer360__customer_behavior_analysis'),('intermediate','int_customer360__customer_lifecycle_metrics'),('intermediate','int_customer360__risk_assessment'),('marts','customer360__mapping'),('marts','customer360__status'),('marts','customer360__updates')]: print(s+'.'+t,c.execute(f'select count(*) from {s}.{t}').fetchone()[0])
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-003.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__mapping.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__mapping.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `data/019_packages_work/019_impl-003_customer360__mapping/019_impl-003_customer360__mapping.json`
- S11: `data/005_cs_work/impl-003/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
