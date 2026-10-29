# impl-003 | marts | customer360__status | 差异：S1；日期 原记录

## 契约完整原文

S3:2091–2125

```yaml
    - name: customer360__status
      description: Unified customer communication preferences and account status aggregated across Marketo, Stripe, and Zendesk
      grain: One row per customer360_id
      source_models:
      - marts.customer360__mapping
      - intermediate.int_customer360__marketo
      - intermediate.int_customer360__stripe
      - intermediate.int_customer360__zendesk
      business_logic: '- Start from marts.customer360__mapping to relate customer360_id to source IDs (marketo_lead_id, stripe_customer_id, zendesk_user_id). - Marketo: - Inner join mapping → intermediate.int_customer360__marketo on marketo_lead_id = lead_id. - Carry is_unsubscribed, is_email_invalid, do_not_call from Marketo as-is. - Derive per-row source_system = ''marketo'' and status: unsubscribed if is_unsubscribed is TRUE; else email_invalid if is_email_invalid is TRUE; else do_not_call if do_not_call is TRUE; else active. - Stripe: - Inner join mapping → intermediate.int_customer360__stripe on stripe_customer_id = customer_id. - Set is_unsubscribed, is_email_invalid, do_not_call to FALSE. - Derive per-row source_system = ''stripe'' and status: delinquent if is_delinquent is TRUE; else deleted if is_deleted is TRUE; else active. - Zendesk: - Inner join mapping → intermediate.int_customer360__zendesk on zendesk_user_id = user_id. - Set is_unsubscribed, is_email_invalid, do_not_call to FALSE. - Derive per-row source_system = ''zendesk'' and status: suspended if is_suspended is TRUE; else deleted if is_deleted is TRUE; else inactive if is_active is FALSE; else active. - Union all rows from the three systems. - Aggregate by customer360_id: - For each of is_unsubscribed, is_email_invalid, and do_not_call: take the logical OR across all rows (TRUE if any TRUE; FALSE if none TRUE and at least one FALSE; NULL only if all inputs are NULL). Stripe and Zendesk always contribute FALSE. - overall_status precedence: 1) unsubscribed if the aggregated unsubscribe flag is TRUE; 2) email_invalid if the aggregated email_invalid flag is TRUE; 3) active if any per-row status is active; 4) suspended if any per-row status is suspended; 5) delinquent if any per-row status is delinquent; 6) otherwise inactive. Note: per-row statuses deleted and do_not_call never map directly to the final status. - source_systems: concatenate the distinct source_system values present using ", " as the delimiter; remove duplicates; do not enforce ordering. - Output one row per customer360_id that appears in at least one of the three joined systems.'
      columns:
      - name: customer360_id
        data_type: VARCHAR
        description: Customer surrogate key; exactly one output row per customer360_id
        tests:
        - not_null
        - unique
      - name: is_unsubscribed
        data_type: BOOLEAN
        description: TRUE if any contributing row is TRUE; FALSE if none TRUE and at least one FALSE (Stripe/Zendesk contribute FALSE); NULL only if all inputs are NULL
      - name: is_email_invalid
        data_type: BOOLEAN
        description: TRUE if any contributing row is TRUE; FALSE if none TRUE and at least one FALSE (Stripe/Zendesk contribute FALSE); NULL only if all inputs are NULL
      - name: do_not_call
        data_type: BOOLEAN
        description: TRUE if any contributing row is TRUE; FALSE if none TRUE and at least one FALSE (Stripe/Zendesk contribute FALSE); NULL only if all inputs are NULL
      - name: overall_status
        data_type: VARCHAR
        description: 'Final status with precedence: unsubscribed > email_invalid > active (if any) > suspended (if any) > delinquent (if any) > inactive; values limited to {unsubscribed, email_invalid, active, suspended, delinquent, inactive}'
        tests:
        - not_null
      - name: source_systems
        data_type: VARCHAR
        description: Comma+space separated distinct list of contributing systems; duplicates removed; ordering unspecified; never NULL
        tests:
        - not_null
```

## agent 最终 SQL

S4

```sql
with status_rows as (
 select m.customer360_id,k.is_unsubscribed,k.is_email_invalid,k.do_not_call,
 case when k.is_unsubscribed then 'unsubscribed' when k.is_email_invalid then 'email_invalid' when k.do_not_call then 'do_not_call' else 'active' end as status,'marketo' as source_system
 from marts.customer360__mapping m join intermediate.int_customer360__marketo k on m.marketo_lead_id=k.lead_id
 union all select m.customer360_id,false,false,false,case when s.is_delinquent then 'delinquent' when s.is_deleted then 'deleted' else 'active' end,'stripe'
 from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id
 union all select m.customer360_id,false,false,false,case when z.is_suspended then 'suspended' when z.is_deleted then 'deleted' when z.is_active=false then 'inactive' else 'active' end,'zendesk'
 from marts.customer360__mapping m join intermediate.int_customer360__zendesk z on m.zendesk_user_id=z.user_id
), aggregated as (
 select customer360_id,bool_or(is_unsubscribed) as is_unsubscribed,bool_or(is_email_invalid) as is_email_invalid,bool_or(do_not_call) as do_not_call,
 bool_or(status='active') as any_active,bool_or(status='suspended') as any_suspended,bool_or(status='delinquent') as any_delinquent,
 string_agg(distinct source_system,', ') as source_systems from status_rows group by customer360_id
)
select customer360_id,is_unsubscribed,is_email_invalid,do_not_call,
 case when is_unsubscribed then 'unsubscribed' when is_email_invalid then 'email_invalid' when any_active then 'active' when any_suspended then 'suspended' when any_delinquent then 'delinquent' else 'inactive' end as overall_status,source_systems
from aggregated
```

## gold SQL（仅供定位差异）

S5

```sql
-- Extract state information from actual source data
with mapping as (
    select * from marts.customer360__mapping
),

-- Extract status from Marketo data
marketo_status as (
    select 
        m.customer360_id,
        mk.is_unsubscribed,
        mk.is_email_invalid,
        mk.do_not_call,
        'marketo' as source_system,
        case 
            when mk.is_unsubscribed = true then 'unsubscribed'
            when mk.is_email_invalid = true then 'email_invalid'
            when mk.do_not_call = true then 'do_not_call'
            else 'active'
        end as status
    from mapping m
    inner join intermediate.int_customer360__marketo mk 
        on m.marketo_lead_id = mk.lead_id
),

-- Extract status from Stripe data
stripe_status as (
    select 
        m.customer360_id,
        false as is_unsubscribed,  -- Stripe doesn't have unsubscribe
        false as is_email_invalid, -- Assume valid if in Stripe
        false as do_not_call,      -- Stripe doesn't track this
        'stripe' as source_system,
        case 
            when sc.is_delinquent = true then 'delinquent'
            when sc.is_deleted = true then 'deleted'
            else 'active'
        end as status
    from mapping m
    inner join intermediate.int_customer360__stripe sc 
        on m.stripe_customer_id = sc.customer_id
),

-- Extract status from Zendesk data
zendesk_status as (
    select 
        m.customer360_id,
        false as is_unsubscribed,  -- Zendesk doesn't have unsubscribe
        false as is_email_invalid, -- Assume valid if in Zendesk
        false as do_not_call,      -- Zendesk doesn't track this
        'zendesk' as source_system,
        case 
            when zu.is_suspended = true then 'suspended'
            when zu.is_deleted = true then 'deleted'
            when zu.is_active = false then 'inactive'
            else 'active'
        end as status
    from mapping m
    inner join intermediate.int_customer360__zendesk zu 
        on m.zendesk_user_id = zu.user_id
),

-- Merge the status of all systems
all_status as (
    select * from marketo_status
    union all 
    select * from stripe_status
    union all
    select * from zendesk_status
),

-- Summarize the final status of each customer
final_status as (
    select 
        customer360_id,
        bool_or(is_unsubscribed) as is_unsubscribed,
        bool_or(is_email_invalid) as is_email_invalid,
        bool_or(do_not_call) as do_not_call,
        case 
            when bool_or(is_unsubscribed) then 'unsubscribed'
            when bool_or(is_email_invalid) then 'email_invalid'
            when count(case when status = 'active' then 1 end) > 0 then 'active'
            when count(case when status = 'suspended' then 1 end) > 0 then 'suspended'
            when count(case when status = 'delinquent' then 1 end) > 0 then 'delinquent'
            else 'inactive'
        end as overall_status,
        string_agg(distinct source_system, ', ') as source_systems
    from all_status
    group by customer360_id
)

select * from final_status
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 10783 | 10783 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"customer360_id":"001384d9022ccc6b2fd0846094ee3c57"}</code> |
| K2 | <code>{"customer360_id":"00317c8a42954ca5a75f02e430ccf785"}</code> |
| K3 | <code>{"customer360_id":"006de81d1fb1a18e9c15c3a3662e0c64"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| customer360_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_unsubscribed | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_email_invalid | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| do_not_call | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| overall_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| source_systems | 1235 | 1235 | 1235 | VARCHAR | VARCHAR |

source_systems 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | stripe, marketo | marketo, stripe |
| K2 | marketo, stripe | stripe, marketo |
| K3 | zendesk, marketo, stripe | stripe, zendesk, marketo |

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
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('customer360.duckdb',read_only=True)<br>checks={<br>'status_key_dups':"select count(*) from (select customer360_id from marts.customer360__status group by 1 ha</code> | 616 | true | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
put('marts','customer360__status', '''
```
event 45 / message

```text
'status_key_dups':"select count(*) from (select customer360_id from marts.customer360__status group by 1 having count(*)>1)",
```
event 45 / message

```text
'customer_status_enum':"select count(*) from marts.customer360__status where overall_status not in ('unsubscribed','email_invalid','active','suspended','delinquent','inactive')",
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__status.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__status.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `data/019_packages_work/019_impl-003_customer360__status/019_impl-003_customer360__status.json`
- S11: `data/005_cs_work/impl-003/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
