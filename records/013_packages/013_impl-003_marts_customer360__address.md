# impl-003 | marts | customer360__address | 差异：S1；日期 原记录

## 契约完整原文

S3:1204–1256

```yaml
    - name: customer360__address
      description: Consolidated customer addresses from Marketo and Stripe enriched with standardized country/state names and priority-based ranking
      grain: One row per sourced address per customer360_id (duplicates preserved)
      source_models:
      - marts.customer360__mapping
      - intermediate.int_customer360__marketo
      - intermediate.int_customer360__stripe
      - staging.stg_customer360__country_codes
      - staging.stg_customer360__state_territory_codes
      business_logic: '- Read pass-through datasets: - marts.customer360__mapping as mapping (provides marketo_lead_id and stripe_customer_id per customer360_id) - staging.stg_customer360__country_codes as country_codes - staging.stg_customer360__state_territory_codes as state_codes - Build Marketo addresses (inner join mapping.marketo_lead_id = int_customer360__marketo.lead_id): - Primary address: include rows where address_line_1 is not NULL; set source_system = "marketo", address_type = "primary", priority = 1; select address_line_1, address_line_2, city, state_code, country_code, postal_code - Billing address: include rows where billing_address_line_1 is not NULL; set source_system = "marketo", address_type = "billing", priority = 2; map billing_* fields to output columns - Build Stripe addresses (inner join mapping.stripe_customer_id = int_customer360__stripe.customer_id): - Customer address: include rows where customer_address_line_1 is not NULL; set source_system = "stripe", address_type = "customer", priority = 1; map customer_* fields - Shipping address: include rows where shipping_address_line_1 is not NULL; set source_system = "stripe", address_type = "shipping", priority = 2; map shipping_* fields - Union all Marketo and Stripe address rows; no de-duplication; only addresses with non-NULL address_line_1 are included. - Enrich with geographic names via left joins: - state: join state_codes on (state_code AND country_code) to derive state_territory; unmatched → NULL - country and country_alt_name: join country_codes on alpha-2 country code; unmatched → NULL - Compute rank: per customer360_id, assign row numbers ordered by priority ascending; within the same priority, order is unspecified and non-deterministic. - Output passes through source text as-is (casing/whitespace preserved); no normalization beyond the joins.'
      columns:
      - name: customer360_id
        data_type: VARCHAR
        description: Customer key from mapping used to group and rank addresses; multiple rows per customer360_id
      - name: source_system
        data_type: VARCHAR
        description: Origin system literal ('marketo' or 'stripe'); set per source and always non-null
      - name: address_type
        data_type: VARCHAR
        description: 'Address category set per source: Marketo → ''primary'' or ''billing''; Stripe → ''customer'' or ''shipping'''
      - name: address_line_1
        data_type: VARCHAR
        description: Primary address line; rows are included only when this is non-null; text is passed through without trimming or case changes
      - name: address_line_2
        data_type: VARCHAR
        description: Secondary address line from source; may be null; text is passed through without trimming or case changes
      - name: city
        data_type: VARCHAR
        description: City from source; may be null; no transformation
      - name: state_code
        data_type: VARCHAR
        description: State/province code from source used for state name enrichment; may be null; case preserved
      - name: state
        data_type: VARCHAR
        description: Resolved state/territory name from stg_customer360__state_territory_codes via (state_code,country_code) match; null if no match
      - name: country_code
        data_type: VARCHAR
        description: ISO alpha-2 country code from source used for joins; may be null; case preserved
      - name: country
        data_type: VARCHAR
        description: Resolved country name from stg_customer360__country_codes via country_code_alpha_2; null if no match
      - name: country_alt_name
        data_type: VARCHAR
        description: Alternative country name from stg_customer360__country_codes; null if no match
      - name: postal_code
        data_type: BIGINT
        description: Postal code from source stored as BIGINT; may be null; numeric-only storage means leading zeros are not preserved
      - name: priority
        data_type: INTEGER
        description: Address priority set by source (1 for primary/customer, 2 for billing/shipping); lower number indicates higher priority
      - name: rank
        data_type: BIGINT
        description: Row number per customer360_id ordered by priority ascending; ties within the same priority have arbitrary order
```

## agent 最终 SQL

S4

```sql
with mapping as (select * from marts.customer360__mapping), addresses as (
 select m.customer360_id,'marketo' as source_system,'primary' as address_type,s.address_line_1,s.address_line_2,s.city,s.state_code,s.country_code,s.postal_code,1 as priority
 from mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.address_line_1 is not null
 union all select m.customer360_id,'marketo','billing',s.billing_address_line_1,s.billing_address_line_2,s.billing_city,s.billing_state_code,s.billing_country_code,s.billing_postal_code,2
 from mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.billing_address_line_1 is not null
 union all select m.customer360_id,'stripe','customer',s.customer_address_line_1,s.customer_address_line_2,s.customer_city,s.customer_state_code,s.customer_country_code,s.customer_postal_code,1
 from mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.customer_address_line_1 is not null
 union all select m.customer360_id,'stripe','shipping',s.shipping_address_line_1,s.shipping_address_line_2,s.shipping_city,s.shipping_state_code,s.shipping_country_code,s.shipping_postal_code,2
 from mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.shipping_address_line_1 is not null
), enriched as (
 select a.*, st.state_territory as state,cc.country_name as country,cc.alternative_country_name as country_alt_name
 from addresses a left join staging.stg_customer360__state_territory_codes st on a.state_code=st.state_code and a.country_code=st.alpha2_country_code
 left join staging.stg_customer360__country_codes cc on a.country_code=cc.country_code_alpha_2
)
select customer360_id,source_system,address_type,address_line_1,address_line_2,city,state_code,state,country_code,country,country_alt_name,postal_code,priority,
 row_number() over(partition by customer360_id order by priority) as rank from enriched
```

## gold SQL（仅供定位差异）

S5

```sql
-- Extract address information from the actual source data
with mapping as (
    select * from marts.customer360__mapping
),

country_codes as (
    select * from staging.stg_customer360__country_codes
),

state_codes as (
    select * from staging.stg_customer360__state_territory_codes
),

-- Extract addresses from Marketo data
marketo_addresses as (
    select 
        m.customer360_id,
        'marketo' as source_system,
        mk.address_line_1,
        mk.address_line_2,
        mk.city,
        mk.state_code,
        mk.country_code,
        mk.postal_code,
        1 as priority,
        'primary' as address_type
    from mapping m
    inner join intermediate.int_customer360__marketo mk 
        on m.marketo_lead_id = mk.lead_id
    where mk.address_line_1 is not null
    
    union all
    
    -- Marketo billing addresses
    select 
        m.customer360_id,
        'marketo' as source_system,
        mk.billing_address_line_1 as address_line_1,
        mk.billing_address_line_2 as address_line_2,
        mk.billing_city as city,
        mk.billing_state_code as state_code,
        mk.billing_country_code as country_code,
        mk.billing_postal_code as postal_code,
        2 as priority,
        'billing' as address_type
    from mapping m
    inner join intermediate.int_customer360__marketo mk 
        on m.marketo_lead_id = mk.lead_id
    where mk.billing_address_line_1 is not null
),

-- Extract addresses from Stripe data
stripe_addresses as (
    select 
        m.customer360_id,
        'stripe' as source_system,
        sc.customer_address_line_1 as address_line_1,
        sc.customer_address_line_2 as address_line_2,
        sc.customer_city as city,
        sc.customer_state_code as state_code,
        sc.customer_country_code as country_code,
        sc.customer_postal_code as postal_code,
        1 as priority,
        'customer' as address_type
    from mapping m
    inner join intermediate.int_customer360__stripe sc 
        on m.stripe_customer_id = sc.customer_id
    where sc.customer_address_line_1 is not null
    
    union all
    
    -- Stripe shipping addresses
    select 
        m.customer360_id,
        'stripe' as source_system,
        sc.shipping_address_line_1 as address_line_1,
        sc.shipping_address_line_2 as address_line_2,
        sc.shipping_city as city,
        sc.shipping_state_code as state_code,
        sc.shipping_country_code as country_code,
        sc.shipping_postal_code as postal_code,
        2 as priority,
        'shipping' as address_type
    from mapping m
    inner join intermediate.int_customer360__stripe sc 
        on m.stripe_customer_id = sc.customer_id
    where sc.shipping_address_line_1 is not null
),

-- Merge all addresses and enhance
all_addresses as (
    select * from marketo_addresses
    union all 
    select * from stripe_addresses
),

enhanced_addresses as (
    select 
        all_addresses.customer360_id,
        all_addresses.source_system,
        all_addresses.address_type,
        all_addresses.address_line_1,
        all_addresses.address_line_2,
        all_addresses.city,
        all_addresses.state_code,
        state_codes.state_territory as state,
        all_addresses.country_code,
        country_codes.country_name as country,
        country_codes.alternative_country_name as country_alt_name,
        all_addresses.postal_code,
        all_addresses.priority,
        row_number() over (partition by all_addresses.customer360_id order by all_addresses.priority) as rank
    from all_addresses
    left join state_codes 
        on all_addresses.state_code = state_codes.state_code 
        and all_addresses.country_code = state_codes.alpha2_country_code
    left join country_codes 
        on all_addresses.country_code = country_codes.country_code_alpha_2
)

select * from enhanced_addresses
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 38482 | 38482 | 0 | 0 | 12349 | 12349 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"customer360_id":"00401ba8139a643bf7f8963596d63e9f","state_code":"null","state":"null","country_code":"null","country":"null","postal_code":"59079"}</code> |
| K2 | <code>{"customer360_id":"00401ba8139a643bf7f8963596d63e9f","state_code":"null","state":"null","country_code":"null","country":"null","postal_code":"89393"}</code> |
| K3 | <code>{"customer360_id":"0074e2118042ee2db487478d36359273","state_code":"12","state":"null","country_code":"french southern territories","country":"null","postal_code":"62138"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| customer360_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| source_system | 0 | 0 | 0 | VARCHAR | VARCHAR |
| address_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| address_line_1 | 0 | 0 | 0 | VARCHAR | VARCHAR |
| address_line_2 | 0 | 0 | 0 | VARCHAR | VARCHAR |
| city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| state_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country_alt_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| postal_code | 0 | 0 | 0 | BIGINT | BIGINT |
| priority | 0 | 0 | 0 | INTEGER | INTEGER |
| rank | 3192 | 3192 | 3192 | BIGINT | BIGINT |

rank 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 4 | 3 |
| K2 | 3 | 4 |
| K3 | <code>[{"value":"1","rows":1},{"value":"2","rows":1},{"value":"3","rows":1},{"value":"4","rows":1},{"value":"7","rows":1}]</code> | <code>[{"value":"1","rows":1},{"value":"2","rows":1},{"value":"3","rows":1},{"value":"4","rows":1},{"value":"5","rows":1}]</code> |
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
| B6_constant_literal_output | <code>3输出列；[{"column":"source_system","expression":["'marketo'"]},{"column":"address_type","expression":["'primary'"]},{"column":"priority","expression":["1"]}]</code> |

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
put('marts','customer360__address', '''
```
event 23 / message

```text
name_first as(select * from marts.customer360__name where index=1),org_first as(select * from marts.customer360__organization where index=1),address_first as(select * from marts.customer360__address where rank=1)
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-003.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__address.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__address.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `records/012_packages/012_impl-003_marts_customer360__address.json`
- S11: `data/005_cs_work/impl-003/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
