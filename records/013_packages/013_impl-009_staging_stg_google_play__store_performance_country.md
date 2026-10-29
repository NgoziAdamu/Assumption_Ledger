# impl-009 | staging | stg_google_play__store_performance_country | 差异：S1；日期 原记录

## 契约完整原文

S3:360–381

```yaml
    - name: stg_google_play__store_performance_country
      description: "Store performance metrics by country"
      source_table: "raw.stats_store_performance_country"
      columns:
        - name: date_day
          data_type: DATE
          constraints: [not_null]
        - name: package_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: country
          data_type: VARCHAR
          constraints: [not_null]
        - name: store_listing_visitors
          data_type: INTEGER
        - name: store_listing_conversion_rate
          data_type: DECIMAL(18,3)
        - name: store_listing_installers
          data_type: INTEGER
        - name: _fivetran_synced
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
SELECT
    try_cast(substr(date, 1, 10) AS DATE) AS date_day,
    CAST(package_name AS VARCHAR) AS package_name,
    CAST(cc.country_code_alpha_2 AS VARCHAR) AS country,
    try_cast(store_listing_visitors AS INTEGER) AS store_listing_visitors,
    try_cast(store_listing_conversion_rate AS DECIMAL(18,3)) AS store_listing_conversion_rate,
    try_cast(store_listing_acquisitions AS INTEGER) AS store_listing_installers,
    CAST(_modified AS VARCHAR) AS _fivetran_synced
FROM raw.stats_store_performance_country
LEFT JOIN raw.google_play__country_codes AS cc ON cc.country_code_numeric = country_region
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *
    from raw.stats_store_performance_country
),

validated as (
    select
        -- date_day: DATE with not null constraint
        case
            when date is not null then cast(date as date)
            else null
        end as date_day,

        -- package_name: VARCHAR with not null constraint
        case
            when package_name is not null then cast(package_name as varchar)
            else null
        end as package_name,

        -- country: VARCHAR with not null constraint (mapped from country_region)
        case
            when country_region is not null then cast(country_region as varchar)
            else null
        end as country,

        -- store_listing_visitors: INTEGER (no specific validation)
        cast(store_listing_visitors as integer) as store_listing_visitors,

        -- store_listing_conversion_rate: DECIMAL(18,3) (no specific validation)
        cast(store_listing_conversion_rate as decimal(18,3)) as store_listing_conversion_rate,

        -- store_listing_installers: INTEGER (mapped from store_listing_acquisitions)
        cast(store_listing_acquisitions as integer) as store_listing_installers,

        _modified as _fivetran_synced

    from base
),

final as (
    select
        date_day,
        package_name,
        country,
        store_listing_visitors,
        store_listing_conversion_rate,
        store_listing_installers,
        _fivetran_synced
    from validated
    where
        -- Enforce not null constraints by deleting rows with null values
        date_day is not null
        and package_name is not null
        and country is not null
)

select *
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 8800 | 6400 | 8800 | 6400 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| package_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| store_listing_visitors | 0 | 0 | 0 | INTEGER | INTEGER |
| store_listing_conversion_rate | 0 | 0 | 0 | DECIMAL(18,3) | DECIMAL(18,3) |
| store_listing_installers | 0 | 0 | 0 | INTEGER | INTEGER |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"date_day":"2020-01-01","package_name":"com.app.musicplayer","country":"BR"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","country":"CN"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","country":"DE"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","country":"FQ"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","country":"FR"}]</code> | <code>[{"date_day":"2020-01-01","package_name":"com.app.musicplayer","country":"156"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","country":"250"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","country":"276"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","country":"356"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","country":"392"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| B7_read_not_specified | <code>["raw.google_play__country_codes"]</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory w(I/'int_google_play__store_performance.sql',"""SELECT date_day, package_name, country, NULL::VARCHAR AS traffic_source, store_listing_visitors, store_listing_conversion_rate, store_listing_installers, 'country' AS performance_type FROM staging.stg_google_play__store_performance_country UNION ALL SELECT date_day, package_name, NULL::VARCHAR AS country, traffic_source, store_listing_visitors, store_listing_conversion_rate, store_listing_installers, 'source' AS performance_type FROM staging.stg_google_play__store_performance_source""")</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -exec sh -c 'echo ===$1; wc -c "$1"' _ {} \;</code> | 3902 | true | false |
| 11 | run | <code>sed -n '1,240p' google_play_start.yaml</code> | 5914 | false | false |
| 13 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('google_play_start.duckdb',read_only=True)<br>for t in c.execute("select table_name from information_schema.tables where table_schema='raw'").fetchall():<br> n</code> | 16300 | false | false |
| 15 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml, pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br>maptbl={'stg_goo</code> | 0 | false | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob<br>c=duckdb.connect()<br>c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>c.execute('CREATE SCHEMA raw');<br>for (t,) in c.execute("select table_name from in</code> | 1639 | true | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>p='/tmp/gen.py'<br>s=open(p).read().replace("'transaction_date':'transaction_date'", "'transaction_date':'transaction_date','package_name':'base_plan_id','total_active_subscriptions':'act</code> | 5282 | true | false |
| 33 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>I=Path('sql/intermediate'); M=Path('sql/marts')<br>def w(path,s): Path(path).write_text(s.strip()+'\n')<br>w(I/'int_google_play__latest_product_info.sql'</code> | 0 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob,os<br>c=duckdb.connect(); c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>for s in ['raw','staging','intermediate','mart']: c.execute(f'create schema </code> | 4516 | true | false |
| 43 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; code=$?; tail -60 /tmp/runlog; exit $code</code> | 4495 | true | false |
| 53 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_google_play__earnings.sql'); s=p.read_text().replace('CAST(sku_id AS VARCHAR) AS sku_id','CAST(coalesce(sku_id, product_id, base_plan_i</code> | 2857 | true | false |

### agent action 的 thought/message 命中原句

event 15 / message

```text
maptbl={'stg_google_play__earnings':'earnings','stg_google_play__subscriptions_country':'financial_stats_subscriptions_country','stg_google_play__country_codes':'google_play__country_codes','stg_google_play__store_performance_country':'stats_store_performance_country','stg_google_play__store_performance_source':'stats_store_performance_traffic_source'}
```
event 15 / message

```text
  elif n=='country' and name=='stg_google_play__store_performance_country': expr='cc.country_code_alpha_2'
```
event 15 / message

```text
 if name=='stg_google_play__store_performance_country': joins='\nLEFT JOIN raw.google_play__country_codes AS cc ON cc.country_code_numeric = country_region'
```
event 33 / message

```text
w(I/'int_google_play__store_performance.sql',"""SELECT date_day, package_name, country, NULL::VARCHAR AS traffic_source, store_listing_visitors, store_listing_conversion_rate, store_listing_installers, 'country' AS performance_type FROM staging.stg_google_play__store_performance_country UNION ALL SELECT date_day, package_name, NULL::VARCHAR AS country, traffic_source, store_listing_visitors, store_listing_conversion_rate, store_listing_installers, 'source' AS performance_type FROM staging.stg_google_play__store_performance_source""")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-009.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`
- S6: `records/006_contract_impl-009.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/result.md`
- S10: `records/012_packages/012_impl-009_staging_stg_google_play__store_performance_country.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/google_play.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions`
