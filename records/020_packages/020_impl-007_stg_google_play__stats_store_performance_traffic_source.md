# impl-007 | staging | stg_google_play__stats_store_performance_traffic_source | 差异：S1；日期 原记录

## 契约完整原文

S3:114–135

```yaml
    - name: stg_google_play__stats_store_performance_traffic_source
      description: "Store performance metrics by traffic source from Google Play Console"
      source_table: "raw.stats_store_performance_traffic_source"
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: date_day
          data_type: DATE
        - name: package_name
          data_type: VARCHAR
        - name: traffic_source
          data_type: VARCHAR
        - name: store_listing_acquisitions
          data_type: BIGINT
        - name: store_listing_visitors
          data_type: BIGINT
        - name: store_listing_conversion_rate
          data_type: DECIMAL(10,4)
          validation_rules:
            - rule: "store_listing_conversion_rate >= 0 AND store_listing_conversion_rate <= 1"
              on_failure: nullify_field

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
SELECT
    CAST(_file AS VARCHAR) AS source_relation,
    TRY_CAST(SUBSTR(CAST(date AS VARCHAR), 1, 10) AS DATE) AS date_day,
    CAST(package_name AS VARCHAR) AS package_name,
    CAST(traffic_source AS VARCHAR) AS traffic_source,
    TRY_CAST(store_listing_acquisitions AS BIGINT) AS store_listing_acquisitions,
    TRY_CAST(store_listing_visitors AS BIGINT) AS store_listing_visitors,
    TRY_CAST(store_listing_conversion_rate AS DECIMAL(10,4)) AS store_listing_conversion_rate
FROM raw.stats_store_performance_traffic_source
)
SELECT source_relation, date_day, package_name, traffic_source, store_listing_acquisitions, store_listing_visitors, CASE WHEN store_listing_conversion_rate BETWEEN 0 AND 1 THEN store_listing_conversion_rate ELSE NULL END AS store_listing_conversion_rate FROM source_rows
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *
    from raw.stats_store_performance_traffic_source
),

final as (
    select
        'google_play' as source_relation,
        cast(date as date) as date_day,
        cast(package_name as varchar) as package_name,
        cast(traffic_source as varchar) as traffic_source,
        cast(store_listing_acquisitions as bigint) as store_listing_acquisitions,
        cast(store_listing_visitors as bigint) as store_listing_visitors,
        cast(
            case
                when store_listing_visitors > 0
                then cast(store_listing_acquisitions as decimal) / cast(store_listing_visitors as decimal)
                when store_listing_visitors is null
                then null
                else 0.0  -- on_failure: correct to zero for invalid calculation
            end as decimal(10,4)
        ) as store_listing_conversion_rate
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
| K1 | <code>{"date_day":"2024-10-24","package_name":"com.software.business","traffic_source":"advertisement"}</code> |
| K2 | <code>{"date_day":"2024-11-06","package_name":"com.software.business","traffic_source":"advertisement"}</code> |
| K3 | <code>{"date_day":"2025-02-07","package_name":"com.solutions.books","traffic_source":"google play search"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| package_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| traffic_source | 0 | 0 | 0 | VARCHAR | VARCHAR |
| store_listing_acquisitions | 0 | 0 | 0 | BIGINT | BIGINT |
| store_listing_visitors | 0 | 0 | 0 | BIGINT | BIGINT |
| store_listing_conversion_rate | 4 | 4 | 4 | DECIMAL(10,4) | DECIMAL(10,4) |

store_listing_conversion_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.2622 |
| K2 | null | 0.2759 |
| K3 | 0.2812 | 0.2813 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

没有 True 痕迹。

## 轨迹索引（不放输出原文）

本题事件总数：70；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 6041 | true | false |
| 13 | run | <code>find sql -type f -print; sed -n '220,520p' run.py; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('app_reporting_start.duckdb',read_only=True)<br>for t in c.execute("select table_name from information_sc</code> | 24579 | false | false |
| 17 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,160p' docs/data_contract.yaml</code> | 6299 | true | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> print(t['name'],t['source_table'],','.join(x['name'] for x in t['columns']))<br>pr</code> | 5964 | true | false |
| 23 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br># source contract field to raw source field aliases<br>maps={<br>'r</code> | 0 | false | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> f='sql/staging/'+t['name']+'.sql'<br> s=open(f).read()<br> print(t['name'],s.replace(</code> | 8133 | true | false |
| 27 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>out=Path('sql/intermediate')<br>queries={<br>'int_google_play__overview':"""WITH installs AS (SELECT * FROM staging.stg_google_play__stats_installs_overvi</code> | 0 | false | false |
| 31 | run | <code>cat &gt; /tmp/channel.py &lt;&lt;'PY'<br>from pathlib import Path<br>Path('sql/intermediate/int_channel_performance.sql').write_text('''WITH source_rows AS (<br> SELECT date_day,package_name app_name,'google_play' plat</code> | 0 | false | false |
| 43 | run | <code>python run.py &gt; /tmp/pipeline.log 2&gt;&amp;1; echo EXIT:$?; tail -100 /tmp/pipeline.log</code> | 7846 | true | false |
| 45 | run | <code>grep -E 'staging\.&#124;ERROR&#124;WARNING' /tmp/pipeline.log &#124; head -100</code> | 18912 | true | false |
| 47 | run | <code>rm -f app_reporting.duckdb; python - &lt;&lt;'PY'<br>import duckdb<br>src=duckdb.connect('app_reporting_start.duckdb',read_only=True); out=duckdb.connect('app_reporting.duckdb'); out.execute('create schema raw')<br></code> | 8738 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,glob,os<br>cfg=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('app_reporting.duckdb',read_only=True)<br>for layer,schema,models in [('staging','staging'</code> | 5387 | true | false |

### agent action 的 thought/message 命中原句

event 27 / message

```text
'int_google_play__traffic_source':"""SELECT source_relation,date_day,'google_play' app_platform,package_name app_name,traffic_source,sum(store_listing_acquisitions) acquisitions,sum(store_listing_visitors) visitors FROM staging.stg_google_play__stats_store_performance_traffic_source GROUP BY source_relation,date_day,package_name,traffic_source""",
```
event 31 / message

```text
 SELECT date_day,package_name app_name,'google_play' platform,traffic_source,coalesce(store_listing_acquisitions,0)::BIGINT conversions,coalesce(store_listing_visitors,0)::BIGINT store_visitors,coalesce(store_listing_acquisitions,0)::BIGINT installers FROM staging.stg_google_play__stats_store_performance_traffic_source
```

## result.md 本表名原句

未找到 result.md。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-007.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_store_performance_traffic_source.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_google_play__stats_store_performance_traffic_source.sql`
- S6: `records/006_contract_impl-007.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/020_packages_work/020_impl-007_stg_google_play__stats_store_performance_traffic_source/020_impl-007_stg_google_play__stats_store_performance_traffic_source.json`
- S10: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`
- S11: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`
- S12: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions`
