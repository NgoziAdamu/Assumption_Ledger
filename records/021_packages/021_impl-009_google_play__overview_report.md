# impl-009 | marts | google_play__overview_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1889–1968

```yaml
    - name: google_play__overview_report
      description: Daily Google Play performance overview per app combining installs, events, store listing, crashes/ANRs, and ratings
      grain: One row per package_name per date_day present in any source
      source_models:
      - staging.stg_google_play__stats_installs_overview
      - staging.stg_google_play__stats_ratings_overview
      - staging.stg_google_play__stats_crashes_overview
      - intermediate.int_google_play__store_performance
      business_logic: '- Aggregate store performance: - Filter intermediate.int_google_play__store_performance to performance_type = ''country''. - For each (date_day, package_name), sum visitors and installers; take the simple (unweighted) average of conversion rate, ignoring missing values. - Compute running totals for installs: - For each package_name ordered by date_day ascending, compute cumulative totals of daily_device_installs and daily_device_uninstalls. - Combine sources: - Full outer join installs (with running totals), ratings, store_performance (aggregated), and crashes on (date_day, package_name). - When date or package is missing in a source, choose the first available from installs, then ratings, then store_performance, then crashes. - Set missing counts to 0 for device/user installs, uninstalls, upgrades; install/uninstall/update events; crashes; ANRs; active devices; store installers and visitors. Leave store listing conversion rate and daily average rating as NULL if absent. - Forward-fill selected metrics by app: - Within each package_name ordered by date_day, carry forward the latest non-null values for total average rating, cumulative device installs, and cumulative device uninstalls; before the first non-null appears, these remain NULL. - Final calculations: - Default total_device_installs and total_device_uninstalls to 0 in the output. - rolling_store_conversion_rate = acquisitions divided by visitors, rounded to 4 decimals; return NULL when visitors is 0. - net_device_installs = total_device_installs minus total_device_uninstalls. - Output one row per (package_name, date_day).'
      columns:
      - name: date_day
        data_type: DATE
        description: Date chosen from the first available among installs, ratings, store performance, and crashes in that order
        tests:
        - not_null
      - name: package_name
        data_type: VARCHAR
        description: App package identifier chosen from the first available among installs, ratings, store performance, and crashes in that order
        tests:
        - not_null
      - name: device_installs
        data_type: BIGINT
        description: Daily device installs; missing values set to 0; no smoothing or rounding
      - name: device_uninstalls
        data_type: BIGINT
        description: Daily device uninstalls; missing values set to 0; no smoothing or rounding
      - name: device_upgrades
        data_type: BIGINT
        description: Daily device upgrades; missing values set to 0; no smoothing or rounding
      - name: user_installs
        data_type: BIGINT
        description: Daily user installs; missing values set to 0; no smoothing or rounding
      - name: user_uninstalls
        data_type: BIGINT
        description: Daily user uninstalls; missing values set to 0; no smoothing or rounding
      - name: crashes
        data_type: BIGINT
        description: Daily crash events; missing values set to 0; per app per day
      - name: anrs
        data_type: BIGINT
        description: Daily ANR events; missing values set to 0; per app per day
      - name: install_events
        data_type: BIGINT
        description: Daily install events; missing values set to 0; event counts unchanged
      - name: uninstall_events
        data_type: BIGINT
        description: Daily uninstall events; missing values set to 0; event counts unchanged
      - name: update_events
        data_type: BIGINT
        description: Daily update events; missing values set to 0; event counts unchanged
      - name: store_listing_acquisitions
        data_type: HUGEINT
        description: Sum of store installers across country rows per day and app; defaults to 0 when store performance is absent
      - name: store_listing_visitors
        data_type: HUGEINT
        description: Sum of store visitors across country rows per day and app; defaults to 0 when store performance is absent
      - name: store_listing_conversion_rate
        data_type: DOUBLE
        description: Unweighted average of store listing conversion rate across country rows per day and app; NULL when no rows; no rounding applied
      - name: active_devices_last_30_days
        data_type: BIGINT
        description: Active devices in the last 30 days from installs; missing values set to 0
      - name: average_rating
        data_type: DECIMAL(18,3)
        description: Daily average rating; may be NULL; three-decimal precision
      - name: rolling_total_average_rating
        data_type: DECIMAL(18,3)
        description: Forward-filled total average rating per app ordered by date; remains NULL until the first non-null appears
      - name: total_device_installs
        data_type: HUGEINT
        description: Cumulative device installs per app ordered by date; forward-filled across days without install data; defaults to 0 in output
      - name: total_device_uninstalls
        data_type: HUGEINT
        description: Cumulative device uninstalls per app ordered by date; forward-filled across days without install data; defaults to 0 in output
      - name: rolling_store_conversion_rate
        data_type: DOUBLE
        description: Acquisitions divided by visitors, rounded to 4 decimals; returns NULL when visitors equals 0
      - name: net_device_installs
        data_type: HUGEINT
        description: Total device installs minus total device uninstalls after defaulting NULLs to 0
```

## agent 最终 SQL

S4

```sql
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(0 as BIGINT) AS crashes,
cast(0 as BIGINT) AS anrs,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as HUGEINT) AS store_listing_acquisitions,
cast(0 as HUGEINT) AS store_listing_visitors,
cast(NULL as DOUBLE) AS store_listing_conversion_rate,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as DOUBLE) AS rolling_store_conversion_rate,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_overview AS src
WHERE src.date_day IS NOT NULL
```

## gold SQL（仅供定位差异）

S5

```sql
with installs as (
    select *
    from staging.stg_google_play__stats_installs_overview
), 

ratings as (
    select *
    from staging.stg_google_play__stats_ratings_overview
), 

crashes as (
    select *
    from staging.stg_google_play__stats_crashes_overview
), 

store_performance as (
    select 
        date_day,
        package_name,
        sum(store_listing_visitors) as store_listing_visitors,
        avg(store_listing_conversion_rate) as store_listing_conversion_rate,
        sum(store_listing_installers) as store_listing_installers
    from intermediate.int_google_play__store_performance
    where performance_type = 'country'
    group by 1, 2
), 

install_metrics as (
    select
        *,
        sum(daily_device_installs) over (
            partition by package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_installs,
        sum(daily_device_uninstalls) over (
            partition by package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_uninstalls
    from installs 
), 

overview_join as (
    select 
        coalesce(install_metrics.date_day, ratings.date_day, store_performance.date_day, crashes.date_day) as date_day,
        coalesce(install_metrics.package_name, ratings.package_name, store_performance.package_name, crashes.package_name) as package_name,

        -- Device and user metrics
        coalesce(install_metrics.active_device_installs, 0) as active_devices_last_30_days,
        coalesce(install_metrics.daily_device_installs, 0) as device_installs,
        coalesce(install_metrics.daily_device_uninstalls, 0) as device_uninstalls,
        coalesce(install_metrics.daily_device_upgrades, 0) as device_upgrades,
        coalesce(install_metrics.daily_user_installs, 0) as user_installs,
        coalesce(install_metrics.daily_user_uninstalls, 0) as user_uninstalls,
        coalesce(store_performance.store_listing_installers, 0) as store_listing_acquisitions,
        coalesce(store_performance.store_listing_visitors, 0) as store_listing_visitors,
        store_performance.store_listing_conversion_rate,

        -- event indicators
        coalesce(crashes.crashes, 0) as crashes,
        coalesce(crashes.anrs, 0) as anrs,
        coalesce(install_metrics.install_events, 0) as install_events,
        coalesce(install_metrics.uninstall_events, 0) as uninstall_events,
        coalesce(install_metrics.update_events, 0) as update_events,    

        -- Cumulative indicator
        install_metrics.total_device_installs,
        install_metrics.total_device_uninstalls,
        ratings.daily_average_rating as average_rating,
        ratings.total_average_rating as rolling_total_average_rating
    from install_metrics
    full outer join ratings
        on install_metrics.date_day = ratings.date_day
        and install_metrics.package_name = ratings.package_name
    full outer join store_performance
        on store_performance.date_day = coalesce(install_metrics.date_day, ratings.date_day)
        and store_performance.package_name = coalesce(install_metrics.package_name, ratings.package_name)
    full outer join crashes
        on coalesce(install_metrics.date_day, ratings.date_day, store_performance.date_day) = crashes.date_day
        and coalesce(install_metrics.package_name, ratings.package_name, store_performance.package_name) = crashes.package_name
),

create_partitions as (
    select
        *,
        sum(case when rolling_total_average_rating is null then 0 else 1 end) over (
            partition by package_name 
            order by date_day asc 
            rows unbounded preceding
        ) as rolling_total_average_rating_partition,
        sum(case when total_device_installs is null then 0 else 1 end) over (
            partition by package_name 
            order by date_day asc 
            rows unbounded preceding
        ) as total_device_installs_partition,
        sum(case when total_device_uninstalls is null then 0 else 1 end) over (
            partition by package_name 
            order by date_day asc 
            rows unbounded preceding
        ) as total_device_uninstalls_partition
    from overview_join
), 

fill_values as (
    select 
        date_day,
        package_name,
        active_devices_last_30_days,
        device_installs,
        device_uninstalls,
        device_upgrades,
        user_installs,
        user_uninstalls,
        crashes,
        anrs,
        install_events,
        uninstall_events,
        update_events,
        store_listing_acquisitions,
        store_listing_visitors,
        store_listing_conversion_rate,
        average_rating,

        first_value(rolling_total_average_rating) over (
            partition by rolling_total_average_rating_partition, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as rolling_total_average_rating,

        first_value(total_device_installs) over (
            partition by total_device_installs_partition, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_installs,

        first_value(total_device_uninstalls) over (
            partition by total_device_uninstalls_partition, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_uninstalls
    from create_partitions
), 

final as (
    select 
        date_day,
        package_name,
        device_installs,
        device_uninstalls,
        device_upgrades,
        user_installs,
        user_uninstalls,
        crashes,
        anrs,
        install_events,
        uninstall_events,
        update_events,
        store_listing_acquisitions,
        store_listing_visitors,
        store_listing_conversion_rate,
        active_devices_last_30_days,
        average_rating,
        rolling_total_average_rating, 
        coalesce(total_device_installs, 0) as total_device_installs,
        coalesce(total_device_uninstalls, 0) as total_device_uninstalls,
        
        -- Calculate rolling indicator
        round(cast(store_listing_acquisitions as numeric) / nullif(store_listing_visitors, 0), 4) as rolling_store_conversion_rate,
        coalesce(total_device_installs, 0) - coalesce(total_device_uninstalls, 0) as net_device_installs
    from fill_values
)

select *
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 0 | 3568 | 0 | 3568 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| package_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| device_installs | 0 | 0 | 0 | BIGINT | BIGINT |
| device_uninstalls | 0 | 0 | 0 | BIGINT | BIGINT |
| device_upgrades | 0 | 0 | 0 | BIGINT | BIGINT |
| user_installs | 0 | 0 | 0 | BIGINT | BIGINT |
| user_uninstalls | 0 | 0 | 0 | BIGINT | BIGINT |
| crashes | 0 | 0 | 0 | BIGINT | BIGINT |
| anrs | 0 | 0 | 0 | BIGINT | BIGINT |
| install_events | 0 | 0 | 0 | BIGINT | BIGINT |
| uninstall_events | 0 | 0 | 0 | BIGINT | BIGINT |
| update_events | 0 | 0 | 0 | BIGINT | BIGINT |
| active_devices_last_30_days | 0 | 0 | 0 | BIGINT | BIGINT |
| average_rating | 0 | 0 | 0 | DECIMAL(18,3) | DECIMAL(18,3) |
| rolling_total_average_rating | 0 | 0 | 0 | DECIMAL(18,3) | DECIMAL(18,3) |
| total_device_installs | 0 | 0 | 0 | HUGEINT | HUGEINT |
| total_device_uninstalls | 0 | 0 | 0 | HUGEINT | HUGEINT |
| rolling_store_conversion_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| net_device_installs | 0 | 0 | 0 | HUGEINT | HUGEINT |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"date_day":"2020-01-01","package_name":"com.app.musicplayer"},{"date_day":"2020-01-01","package_name":"com.demo.socialmedia"},{"date_day":"2020-01-01","package_name":"com.dev.photoeditor"},{"date_day":"2020-01-01","package_name":"com.example.gameapp"},{"date_day":"2020-01-01","package_name":"com.sample.productivity"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| B5_null_literal_output | <code>14输出列；[{"column":"device_upgrades","expression":["CAST(NULL AS BIGINT)"]},{"column":"user_installs","expression":["CAST(NULL AS BIGINT)"]},{"column":"user_uninstalls","expression":["CAST(NULL AS BIGINT)"]}]</code> |
| B6_constant_literal_output | <code>6输出列；[{"column":"device_installs","expression":["CAST(0 AS BIGINT)"]},{"column":"device_uninstalls","expression":["CAST(0 AS BIGINT)"]},{"column":"crashes","expression":["CAST(0 AS BIGINT)"]}]</code> |
| B7_specified_not_read | <code>["intermediate.int_google_play__store_performance","staging.stg_google_play__stats_crashes_overview","staging.stg_google_play__stats_ratings_overview"]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -exec sh -c 'echo ===$1; wc -c "$1"' _ {} \;</code> | 3902 | true | false |
| 15 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml, pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br>maptbl={'stg_goo</code> | 0 | false | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob<br>c=duckdb.connect()<br>c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>c.execute('CREATE SCHEMA raw');<br>for (t,) in c.execute("select table_name from in</code> | 1639 | false | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>p='/tmp/gen.py'<br>s=open(p).read().replace("'transaction_date':'transaction_date'", "'transaction_date':'transaction_date','package_name':'base_plan_id','total_active_subscriptions':'act</code> | 5282 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob,os<br>c=duckdb.connect(); c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>for s in ['raw','staging','intermediate','mart']: c.execute(f'create schema </code> | 4516 | true | false |
| 39 | run | <code>sed -i 's/) prior,/) prior_value,/g;s/ prior, / prior_value, /g;s/(daily_device_installs-prior)::DOUBLE/(daily_device_installs-prior_value)::DOUBLE/g;s/nullif(prior,0)/nullif(prior_value,0)/g' sql/int</code> | 0 | false | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob,os<br>c=duckdb.connect(); c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>for s in ['raw','staging','intermediate','mart']:c.execute(f'create schema {</code> | 967 | true | false |
| 43 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; code=$?; tail -60 /tmp/runlog; exit $code</code> | 4495 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('google_play.duckdb')<br>for t in ['stg_google_play__earnings','stg_google_play__stats_installs_country','stg_google_play__stats_installs_overview']:<br> print</code> | 1107 | false | false |
| 53 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_google_play__earnings.sql'); s=p.read_text().replace('CAST(sku_id AS VARCHAR) AS sku_id','CAST(coalesce(sku_id, product_id, base_plan_i</code> | 2857 | true | false |
| 57 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('google_play.duckdb')<br>for t in ['stg_google_play__earnings','stg_google_play__stats_installs_country','stg_google_play__stats_installs_overview']:<br> print</code> | 3398 | false | false |

### agent action 的 thought/message 命中原句

event 39 / message

```text
 avail={'intermediate.int_google_play__earnings':{'date_day','country_short','sku_id','package_name','merchant_currency'},'intermediate.int_google_play__user_behavior_metrics':{'date_day','package_name','country'},'intermediate.int_google_play__revenue_analytics':{'date_day','package_name','buyer_country','sku_id'},'intermediate.int_google_play__user_retention_analysis':{'install_date','package_name','country'},'intermediate.int_google_play__store_performance':{'date_day','package_name','country','traffic_source'},'staging.stg_google_play__stats_installs_app_version':{'date_day','package_name','app_version_code','android_os_version','device'},'staging.stg_google_play__stats_installs_country':{'date_day','package_name','country'},'staging.stg_google_play__stats_installs_device':{'date_day','package_name','device'},'staging.stg_google_play__stats_installs_os_version':{'date_day','package_name','android_os_version'},'staging.stg_google_play__stats_installs_overview':{'date_day','package_name'},'mart.google_play__overview_report':{'date_day','package_name'}}
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-009.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__overview_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/marts/google_play__overview_report.sql`
- S6: `records/006_contract_impl-009.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/result.md`
- S10: `data/021_packages_work/021_impl-009_google_play__overview_report/021_impl-009_google_play__overview_report.json`
- S11: `data/005_cs_work/impl-009/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/google_play.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions`
