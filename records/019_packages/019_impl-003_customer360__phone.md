# impl-003 | marts | customer360__phone | 差异：S1；日期 原记录

## 契约完整原文

S3:2069–2090

```yaml
    - name: customer360__phone
      description: Distinct phones with extensions collected from Marketo, Stripe, and Zendesk, deduplicated per customer and assigned a per-customer index ordered by phone ascending.
      grain: One row per (customer360_id, phone, extension)
      source_models:
      - marts.customer360__mapping
      - intermediate.int_customer360__marketo
      - intermediate.int_customer360__stripe
      - intermediate.int_customer360__zendesk
      business_logic: '- Use marts.customer360__mapping to link each customer360_id to source records. - For each source, inner join via mapped IDs and collect phone fields only when the phone is not NULL; keep values as-is (no trimming or normalization): - Marketo: phone/phone_extension, company_phone/company_phone_extension, mobile_phone/mobile_phone_extension via mapping.marketo_lead_id = marketo.lead_id. - Stripe: phone/phone_extension, shipping_phone/shipping_phone_extension via mapping.stripe_customer_id = stripe.customer_id. - Zendesk: phone/phone_extension via mapping.zendesk_user_id = zendesk.user_id. - Combine all collected phones across sources without altering values; any per-source index or source label is not retained. - Remove duplicates by exact match of (customer360_id, phone, extension); NULL extensions are allowed and treated as equal for duplicate checking. - Per customer360_id, assign a sequential index starting at 1 based on phone sorted ascending; extension does not affect sort; ties where phone strings are identical (with different extensions) have unspecified order; indices are contiguous with no gaps. - Output columns: customer360_id, phone, extension, index.'
      columns:
      - name: customer360_id
        data_type: VARCHAR
        description: Customer 360 identifier; phones are grouped and indexed per customer.
      - name: phone
        data_type: VARCHAR
        description: Phone string from sources; NULL phones are excluded; value is preserved; used for deduplication and ascending sort for indexing.
      - name: extension
        data_type: VARCHAR
        description: Optional phone extension; included in deduplication; not used for sorting.
      - name: index
        data_type: BIGINT
        description: Per-customer sequential index starting at 1 after deduplication, ordered by phone ascending; tie order for identical phone strings is unspecified; no gaps.
```

## agent 最终 SQL

S4

```sql
with phone_rows as (
 select m.customer360_id,s.phone,s.phone_extension::varchar as extension from marts.customer360__mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.phone is not null
 union all select m.customer360_id,s.company_phone,s.company_phone_extension::varchar from marts.customer360__mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.company_phone is not null
 union all select m.customer360_id,s.mobile_phone,s.mobile_phone_extension from marts.customer360__mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.mobile_phone is not null
 union all select m.customer360_id,s.phone,s.phone_extension::varchar from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.phone is not null
 union all select m.customer360_id,s.shipping_phone,s.shipping_phone_extension::varchar from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.shipping_phone is not null
 union all select m.customer360_id,s.phone,s.phone_extension::varchar from marts.customer360__mapping m join intermediate.int_customer360__zendesk s on m.zendesk_user_id=s.user_id where s.phone is not null
), unique_phones as (select distinct customer360_id,phone,extension from phone_rows)
select customer360_id,phone,extension,row_number() over(partition by customer360_id order by phone) as index from unique_phones
```

## gold SQL（仅供定位差异）

S5

```sql
-- Phone information based on real source system data
with mapping as (
    select * from marts.customer360__mapping
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

-- Collect phone information for all source systems
all_phones as (
    -- Marketo Phone
    select 
        mapping.customer360_id,
        marketo.phone,
        marketo.phone_extension as extension,
        1 as index,
        'marketo' as source
    from mapping
    inner join marketo on mapping.marketo_lead_id = marketo.lead_id
    where marketo.phone is not null

    union all

    -- Marketo company phone number
    select 
        mapping.customer360_id,
        marketo.company_phone as phone,
        marketo.company_phone_extension as extension,
        2 as index,
        'marketo_company' as source
    from mapping
    inner join marketo on mapping.marketo_lead_id = marketo.lead_id
    where marketo.company_phone is not null

    union all

    -- Marketo mobilephone
    select 
        mapping.customer360_id,
        marketo.mobile_phone as phone,
        marketo.mobile_phone_extension as extension,
        3 as index,
        'marketo_mobile' as source
    from mapping
    inner join marketo on mapping.marketo_lead_id = marketo.lead_id
    where marketo.mobile_phone is not null

    union all

    -- Stripe phone
    select 
        mapping.customer360_id,
        stripe.phone,
        stripe.phone_extension as extension,
        1 as index,
        'stripe' as source
    from mapping
    inner join stripe on mapping.stripe_customer_id = stripe.customer_id
    where stripe.phone is not null

    union all

    -- Stripe shipping phone number
    select 
        mapping.customer360_id,
        stripe.shipping_phone as phone,
        stripe.shipping_phone_extension as extension,
        2 as index,
        'stripe_shipping' as source
    from mapping
    inner join stripe on mapping.stripe_customer_id = stripe.customer_id
    where stripe.shipping_phone is not null

    union all

    -- ZendeskPhone
    select 
        mapping.customer360_id,
        zendesk.phone,
        zendesk.phone_extension as extension,
        1 as index,
        'zendesk' as source
    from mapping
    inner join zendesk on mapping.zendesk_user_id = zendesk.user_id
    where zendesk.phone is not null
),

-- Remove duplicates and sort
deduplicated_phones as (
    select 
        customer360_id,
        phone,
        extension,
        row_number() over (partition by customer360_id order by phone) as index
    from (
        select distinct customer360_id, phone, extension
        from all_phones
    ) ranked
)

select 
    customer360_id,
    phone,
    extension,
    index
from deduplicated_phones
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 25986 | 25986 | 0 | 0 | 8660 | 8660 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| customer360_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| extension | 0 | 0 | 0 | VARCHAR | VARCHAR |
| index | 0 | 0 | 0 | BIGINT | BIGINT |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

没有 True 痕迹。

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
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('customer360.duckdb',read_only=True)<br>checks={<br>'status_key_dups':"select count(*) from (select customer360_id from marts.customer360__status group by 1 ha</code> | 616 | false | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
put('marts','customer360__phone', '''
```
event 23 / message

```text
with email_first as(select * from marts.customer360__email where index=1), phone_first as(select * from marts.customer360__phone where index=1),
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-003.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__phone.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__phone.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `data/019_packages_work/019_impl-003_customer360__phone/019_impl-003_customer360__phone.json`
- S11: `data/005_cs_work/impl-003/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
