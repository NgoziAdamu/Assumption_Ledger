# impl-003 | marts | customer360__updates | 差异：S1；日期 原记录

## 契约完整原文

S3:2187–2217

```yaml
    - name: customer360__updates
      description: Per-customer summary of updates from Marketo, Stripe, and Zendesk, showing latest and earliest timestamps, total updates, and distinct source/type lists.
      grain: One row per customer360_id that has at least one joined update from any source
      source_models:
      - marts.customer360__mapping
      - intermediate.int_customer360__marketo
      - intermediate.int_customer360__stripe
      - intermediate.int_customer360__zendesk
      business_logic: '- Read customer-to-source IDs from marts.customer360__mapping (customer360_id, marketo_lead_id, stripe_customer_id, zendesk_user_id). - Create update rows via inner joins: - Marketo: join mapping.marketo_lead_id to intermediate.int_customer360__marketo.lead_id; take updated_at as last_updated and created_at as first_seen; set source_system=''marketo'' and update_type=''lead_update''. - Stripe: join mapping.stripe_customer_id to intermediate.int_customer360__stripe.customer_id; take updated_at as last_updated and created_at as first_seen; set source_system=''stripe'' and update_type=''customer_update''. - Zendesk: join mapping.zendesk_user_id to intermediate.int_customer360__zendesk.user_id; take updated_at as last_updated and created_at as first_seen; set source_system=''zendesk'' and update_type=''user_update''. - Union all per-source rows; duplicates are preserved. - Aggregate by customer360_id: - last_updated: the latest non-null last_updated across all rows; returns null if all are null. - first_seen: the earliest non-null first_seen across all rows; returns null if all are null. - total_updates: the count of all joined rows across sources; includes duplicates and rows with null timestamps. - updated_by_systems: concatenate distinct source_system values with ", "; case preserved; nulls excluded; no guaranteed ordering. - update_types: concatenate distinct update_type values with ", "; case preserved; nulls excluded; no guaranteed ordering. - Output includes only customers with at least one joined update row.'
      columns:
      - name: customer360_id
        data_type: VARCHAR
        description: Unique customer identifier; one row per value.
        tests:
        - not_null
        - unique
      - name: last_updated
        data_type: TIMESTAMP
        description: Latest non-null update timestamp across sources; null if none.
      - name: first_seen
        data_type: TIMESTAMP
        description: Earliest non-null creation timestamp across sources; null if none.
      - name: total_updates
        data_type: BIGINT
        description: Count of joined update rows across sources; includes duplicates and rows with null timestamps.
      - name: updated_by_systems
        data_type: VARCHAR
        description: Distinct source systems concatenated with ', '; order not guaranteed; case preserved; nulls excluded.
      - name: update_types
        data_type: VARCHAR
        description: Distinct update types concatenated with ', '; order not guaranteed; case preserved; nulls excluded.
```

## agent 最终 SQL

S4

```sql
with update_rows as (
 select m.customer360_id,k.updated_at as last_updated,k.created_at as first_seen,'marketo' as source_system,'lead_update' as update_type from marts.customer360__mapping m join intermediate.int_customer360__marketo k on m.marketo_lead_id=k.lead_id
 union all select m.customer360_id,s.updated_at,s.created_at,'stripe','customer_update' from marts.customer360__mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id
 union all select m.customer360_id,z.updated_at,z.created_at,'zendesk','user_update' from marts.customer360__mapping m join intermediate.int_customer360__zendesk z on m.zendesk_user_id=z.user_id
)
select customer360_id,max(last_updated) as last_updated,min(first_seen) as first_seen,count(*)::bigint as total_updates,
 string_agg(distinct source_system,', ') as updated_by_systems,string_agg(distinct update_type,', ') as update_types
from update_rows group by customer360_id
```

## gold SQL（仅供定位差异）

S5

```sql
-- Extract update time information from the actual source data
with mapping as (
    select * from marts.customer360__mapping
),

-- Extract update time from Marketo data
marketo_updates as (
    select 
        m.customer360_id,
        mk.updated_at as last_updated,
        mk.created_at as first_seen,
        'marketo' as source_system,
        'lead_update' as update_type
    from mapping m
    inner join intermediate.int_customer360__marketo mk 
        on m.marketo_lead_id = mk.lead_id
),

-- Extract update time from Stripe data
stripe_updates as (
    select 
        m.customer360_id,
        sc.updated_at as last_updated,
        sc.created_at as first_seen,
        'stripe' as source_system,
        'customer_update' as update_type
    from mapping m
    inner join intermediate.int_customer360__stripe sc 
        on m.stripe_customer_id = sc.customer_id
),

-- Extract update time from Zendesk data
zendesk_updates as (
    select 
        m.customer360_id,
        zu.updated_at as last_updated,
        zu.created_at as first_seen,
        'zendesk' as source_system,
        'user_update' as update_type
    from mapping m
    inner join intermediate.int_customer360__zendesk zu 
        on m.zendesk_user_id = zu.user_id
),

-- Merge update times for all systems
all_updates as (
    select * from marketo_updates
    union all 
    select * from stripe_updates
    union all
    select * from zendesk_updates
),

-- Aggregate last update time for each customer
final_updates as (
    select 
        customer360_id,
        max(last_updated) as last_updated,
        min(first_seen) as first_seen,
        count(*) as total_updates,
        string_agg(distinct source_system, ', ') as updated_by_systems,
        string_agg(distinct update_type, ', ') as update_types
    from all_updates
    group by customer360_id
)

select * from final_updates
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 10783 | 10783 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"customer360_id":"00401ba8139a643bf7f8963596d63e9f"}</code> |
| K2 | <code>{"customer360_id":"0043c219a168bde09bdc7a91e666c651"}</code> |
| K3 | <code>{"customer360_id":"0069d2da906bbb51c1406cd5d0173d36"}</code> |
| K4 | <code>{"customer360_id":"006de81d1fb1a18e9c15c3a3662e0c64"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| customer360_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_updated | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| first_seen | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| total_updates | 0 | 0 | 0 | BIGINT | BIGINT |
| updated_by_systems | 2827 | 2827 | 2827 | VARCHAR | VARCHAR |
| update_types | 1234 | 1234 | 1234 | VARCHAR | VARCHAR |

updated_by_systems 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | stripe, zendesk, marketo | stripe, marketo, zendesk |
| K2 | zendesk, marketo | marketo, zendesk |
| K3 | zendesk, marketo | marketo, zendesk |

update_types 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | lead_update, user_update | user_update, lead_update |
| K3 | user_update, lead_update | lead_update, user_update |
| K4 | user_update, lead_update, customer_update | lead_update, user_update, customer_update |

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
put('marts','customer360__updates', '''
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__updates.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__updates.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `data/019_packages_work/019_impl-003_customer360__updates/019_impl-003_customer360__updates.json`
- S11: `data/005_cs_work/impl-003/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
