# impl-007 | staging | stg_apple_store__sales_subscription_summary | 差异：S1；日期 原记录

## 契约完整原文

S3:211–239

```yaml
    - name: stg_apple_store__sales_subscription_summary
      description: "Subscription sales summary data from Apple Store Connect"
      source_table: "raw.sales_subscription_summary"
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: date_day
          data_type: DATE
        - name: app_id
          data_type: VARCHAR
        - name: app_name
          data_type: VARCHAR
        - name: subscription_name
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: active_subscriptions
          data_type: BIGINT
        - name: free_trial_subscriptions
          data_type: BIGINT
        - name: billing_retry
          data_type: BOOLEAN
        - name: grace_period
          data_type: BOOLEAN
        - name: marketing_opt_ins
          data_type: BOOLEAN
        - name: subscription_duration
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
SELECT
    CAST(app_apple_id AS VARCHAR) AS source_relation,
    TRY_CAST(SUBSTR(CAST(date AS VARCHAR), 1, 10) AS DATE) AS date_day,
    CAST(app_apple_id AS VARCHAR) AS app_id,
    CAST(app_name AS VARCHAR) AS app_name,
    CAST(subscription_name AS VARCHAR) AS subscription_name,
    CAST(country AS VARCHAR) AS country,
    TRY_CAST(subscribers AS BIGINT) AS active_subscriptions,
    CASE WHEN active_free_trial_introductory_offer_subscriptions THEN TRY_CAST(subscribers AS BIGINT) ELSE 0 END AS free_trial_subscriptions,
    billing_retry AS billing_retry,
    grace_period AS grace_period,
    marketing_opt_ins AS marketing_opt_ins,
    CAST(subscription_duration AS VARCHAR) AS subscription_duration
FROM raw.sales_subscription_summary
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *
    from raw.sales_subscription_summary
),

final as (
    select
        'apple_store' as source_relation,
        cast(date as date) as date_day,
        cast(app_apple_id as varchar) as app_id,
        cast(app_name as varchar) as app_name,
        cast(subscription_name as varchar) as subscription_name,
        cast(subscription_duration as varchar) as subscription_duration,
        cast(country as varchar) as country,
        cast(case when active_standard_price_subscriptions then 1 else 0 end as bigint) as active_subscriptions,
        cast(case when active_free_trial_introductory_offer_subscriptions then 1 else 0 end as bigint) as free_trial_subscriptions,
        cast(case when marketing_opt_ins then 1 else 0 end as bigint) as marketing_opt_ins,
        cast(case when billing_retry then 1 else 0 end as bigint) as billing_retry,
        cast(case when grace_period then 1 else 0 end as bigint) as grace_period
    from base
)

select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 700 | 700 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"date_day":"2024-09-05","app_id":"app27634853001","country":"bg"}</code> |
| K2 | <code>{"date_day":"2024-09-05","app_id":"app38154624457","country":"fr"}</code> |
| K3 | <code>{"date_day":"2024-09-07","app_id":"app17920329185","country":"ca"}</code> |
| K4 | <code>{"date_day":"2024-09-07","app_id":"app46421218039","country":"br"}</code> |
| K5 | <code>{"date_day":"2024-09-08","app_id":"app64004775865","country":"lv"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| app_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| app_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subscription_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subscription_duration | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| active_subscriptions | 700 | 700 | 700 | BIGINT | BIGINT |
| free_trial_subscriptions | 347 | 347 | 347 | BIGINT | BIGINT |

active_subscriptions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 5268 | 0 |
| K2 | 7828 | 1 |
| K3 | 9514 | 0 |

free_trial_subscriptions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 5268 | 1 |
| K4 | 6762 | 1 |
| K5 | 1470 | 1 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A4_equal_columns | <code>1组；[{"columns":["source_relation","app_id"],"nonnull_equal_rows":700,"meaning_status":"契约未描述含义差别"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：70；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 6041 | true | false |
| 11 | run | <code>sed -n '1,220p' app_reporting_start.yaml</code> | 5786 | false | false |
| 13 | run | <code>find sql -type f -print; sed -n '220,520p' run.py; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('app_reporting_start.duckdb',read_only=True)<br>for t in c.execute("select table_name from information_sc</code> | 24579 | false | false |
| 15 | run | <code>find sql -maxdepth 2 -type d -print; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('app_reporting_start.duckdb',read_only=True)<br>for t in ['stats_installs_overview','stats_ratings_overview','earnings'</code> | 4276 | false | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> print(t['name'],t['source_table'],','.join(x['name'] for x in t['columns']))<br>pr</code> | 5964 | true | false |
| 23 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br># source contract field to raw source field aliases<br>maps={<br>'r</code> | 0 | false | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> f='sql/staging/'+t['name']+'.sql'<br> s=open(f).read()<br> print(t['name'],s.replace(</code> | 8133 | true | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob,os<br>c=duckdb.connect('app_reporting_start.duckdb',read_only=False); c.execute('create schema if not exists staging')<br>for f in glob.glob('sql/staging/*.sql'):<br> try: c.</code> | 196 | true | false |
| 37 | run | <code>cat sql/staging/stg_apple_store__sales_subscription_summary.sql; python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> if t['name']==</code> | 1489 | true | false |
| 39 | run | <code>sed -i 's/TRY_CAST(active_subscriptions AS BIGINT) AS active_subscriptions/TRY_CAST(subscribers AS BIGINT) AS active_subscriptions/; s/TRY_CAST(subscribers AS BIGINT) AS free_trial_subscriptions/CASE </code> | 0 | false | false |
| 45 | run | <code>grep -E 'staging\.&#124;ERROR&#124;WARNING' /tmp/pipeline.log &#124; head -100</code> | 18912 | true | false |
| 47 | run | <code>rm -f app_reporting.duckdb; python - &lt;&lt;'PY'<br>import duckdb<br>src=duckdb.connect('app_reporting_start.duckdb',read_only=True); out=duckdb.connect('app_reporting.duckdb'); out.execute('create schema raw')<br></code> | 8738 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,glob,os<br>cfg=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('app_reporting.duckdb',read_only=True)<br>for layer,schema,models in [('staging','staging'</code> | 5387 | true | false |

### agent action 的 thought/message 命中原句

event 37 / message

```text
Running command: cat sql/staging/stg_apple_store__sales_subscription_summary.sql; python - <<'PY'
```
event 37 / message

```text
 if t['name']=='stg_apple_store__sales_subscription_summary': print(t)
```
event 39 / message

```text
Running command: sed -i 's/TRY_CAST(active_subscriptions AS BIGINT) AS active_subscriptions/TRY_CAST(subscribers AS BIGINT) AS active_subscriptions/; s/TRY_CAST(subscribers AS BIGINT) AS free_trial_subscriptions/CASE WHEN active_free_trial_introductory_offer_subscriptions THEN TRY_CAST(subscribers AS BIGINT) ELSE 0 END AS free_trial_subscriptions/' sql/staging/stg_apple_store__sales_subscription_summary.sql
```

## result.md 本表名原句

未找到 result.md。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-007.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_summary.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_summary.sql`
- S6: `records/006_contract_impl-007.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/020_packages_work/020_impl-007_stg_apple_store__sales_subscription_summary/020_impl-007_stg_apple_store__sales_subscription_summary.json`
- S10: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`
- S11: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`
- S12: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions`
