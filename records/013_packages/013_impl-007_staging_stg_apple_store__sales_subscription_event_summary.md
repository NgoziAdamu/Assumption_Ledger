# impl-007 | staging | stg_apple_store__sales_subscription_event_summary | 差异：S1；日期 原记录

## 契约完整原文

S3:462–494

```yaml
    - name: stg_apple_store__sales_subscription_event_summary
      description: "Subscription event summary from Apple Store Connect"
      source_table: "raw.sales_subscription_event_summary"
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: date_day
          data_type: DATE
        - name: app_id
          data_type: VARCHAR
        - name: app_name
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: subscription_name
          data_type: VARCHAR
        - name: event_type
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: subscriber_id
          data_type: VARCHAR
        - name: standard_subscription_duration
          data_type: VARCHAR
        - name: proceeds_reason
          data_type: VARCHAR
        - name: marketing_opt_in_duration
          data_type: VARCHAR
        - name: consecutive_paid_periods
          data_type: BIGINT
        - name: quantity
          data_type: BIGINT

```

## agent 最终 SQL

S4

```sql
SELECT
    CAST(app_apple_id AS VARCHAR) AS source_relation,
    TRY_CAST(SUBSTR(CAST(event_date AS VARCHAR), 1, 10) AS DATE) AS date_day,
    CAST(app_apple_id AS VARCHAR) AS app_id,
    CAST(app_name AS VARCHAR) AS app_name,
    subscription_apple_id AS subscription_id,
    CAST(subscription_name AS VARCHAR) AS subscription_name,
    CAST(event AS VARCHAR) AS event_type,
    CAST(country AS VARCHAR) AS country,
    CAST(subscriber_id_vendor AS VARCHAR) AS subscriber_id,
    subscription_duration AS standard_subscription_duration,
    CAST(proceeds_reason AS VARCHAR) AS proceeds_reason,
    CAST(subscription_offer_duration AS VARCHAR) AS marketing_opt_in_duration,
    TRY_CAST(consecutive_paid_periods AS BIGINT) AS consecutive_paid_periods,
    CAST(quantity AS BIGINT) AS quantity
FROM raw.sales_subscription_event_summary
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *
    from raw.sales_subscription_event_summary
),

final as (
    select
        'apple_store' as source_relation,
        cast(event_date as date) as date_day,
        cast(app_name as varchar) as app_name,
        cast(app_apple_id as varchar) as app_id,
        cast(subscription_name as varchar) as subscription_name,
        cast(subscription_apple_id as varchar) as subscription_id,
        cast(subscription_duration as varchar) as standard_subscription_duration,
        cast(marketing_opt_in_duration as varchar) as marketing_opt_in_duration,
        cast(promotional_offer_id as varchar) as subscriber_id,
        cast(event as varchar) as event_type,
        cast(country as varchar) as country,
        cast(quantity as bigint) as quantity,
        cast(proceeds_reason as varchar) as proceeds_reason,
        cast(consecutive_paid_periods as bigint) as consecutive_paid_periods
    from base
)

select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 700 | 700 | 700 | 700 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| app_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| app_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subscription_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subscription_id | 0 | 0 | 0 | BIGINT | VARCHAR |
| standard_subscription_duration | 0 | 0 | 0 | VARCHAR | VARCHAR |
| marketing_opt_in_duration | 0 | 0 | 0 | VARCHAR | VARCHAR |
| event_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| quantity | 0 | 0 | 0 | BIGINT | BIGINT |
| proceeds_reason | 0 | 0 | 0 | VARCHAR | VARCHAR |
| consecutive_paid_periods | 0 | 0 | 0 | BIGINT | BIGINT |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"date_day":"2024-09-05","app_id":"APP40831872829","subscription_id":"39923355116","subscriber_id":"b89d635f-b0ab-40b4-9395-4f365e06cadb","country":"RO"},{"date_day":"2024-09-06","app_id":"APP13018617353","subscription_id":"65284131421","subscriber_id":"28010786-81cf-43f0-80b6-e4497ed8abe3","country":"EE"},{"date_day":"2024-09-06","app_id":"APP34146276349","subscription_id":"43789889991","subscriber_id":"7edc9b57-334d-4b9b-9aa0-cdae49c2b66f","country":"CZ"},{"date_day":"2024-09-06","app_id":"APP44189195532","subscription_id":"52393027033","subscriber_id":"592c3996-f502-4f03-99d4-65c68eefd32e","country":"MX"},{"date_day":"2024-09-06","app_id":"APP82850229000","subscription_id":"63748102251","subscriber_id":"54674e83-bade-42a0-97f0-f817c9597339","country":"CA"}]</code> | <code>[{"date_day":"2024-09-05","app_id":"APP40831872829","subscription_id":"39923355116","subscriber_id":"14509214989","country":"RO"},{"date_day":"2024-09-06","app_id":"APP13018617353","subscription_id":"65284131421","subscriber_id":"31400519185","country":"EE"},{"date_day":"2024-09-06","app_id":"APP34146276349","subscription_id":"43789889991","subscriber_id":"93291025984","country":"CZ"},{"date_day":"2024-09-06","app_id":"APP44189195532","subscription_id":"52393027033","subscriber_id":"55491808282","country":"MX"},{"date_day":"2024-09-06","app_id":"APP82850229000","subscription_id":"63748102251","subscriber_id":"84233838947","country":"CA"}]</code> |

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
| 45 | run | <code>grep -E 'staging\.&#124;ERROR&#124;WARNING' /tmp/pipeline.log &#124; head -100</code> | 18912 | true | false |
| 47 | run | <code>rm -f app_reporting.duckdb; python - &lt;&lt;'PY'<br>import duckdb<br>src=duckdb.connect('app_reporting_start.duckdb',read_only=True); out=duckdb.connect('app_reporting.duckdb'); out.execute('create schema raw')<br></code> | 8738 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,glob,os<br>cfg=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('app_reporting.duckdb',read_only=True)<br>for layer,schema,models in [('staging','staging'</code> | 5387 | true | false |

### agent action 的 thought/message 命中原句

未找到命中原句。

## result.md 本表名原句

未找到 result.md。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-007.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_event_summary.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_event_summary.sql`
- S6: `records/006_contract_impl-007.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `records/012_packages/012_impl-007_staging_stg_apple_store__sales_subscription_event_summary.json`
- S10: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`
- S11: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`
- S12: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions`
