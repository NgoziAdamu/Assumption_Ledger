# impl-009 | marts | google_play__app_version_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1476–1551

```yaml
    - name: google_play__app_version_report
      description: App version performance by date with installs, uninstalls, crashes/ANRs, ratings, and cumulative metrics per OS version and device
      grain: One row per date_day, package_name, app_version_code, android_os_version, device
      source_models:
      - staging.stg_google_play__stats_installs_app_version
      - staging.stg_google_play__stats_crashes_app_version
      - staging.stg_google_play__stats_ratings_app_version
      business_logic: '- Inputs: - Installs: per date, package, app_version_code, android_os_version, device - Ratings: per date, package, app_version_code - Crashes: per date, package, app_version_code, android_os_version - Compute cumulative install totals on the installs input: - total_device_installs: cumulative sum of daily_device_installs by date_day ascending within (package_name, app_version_code) - total_device_uninstalls: cumulative sum of daily_device_uninstalls by date_day ascending within (package_name, app_version_code) - Note: ordering is by date_day only; if multiple rows share the same date_day, the physical/source row order determines evaluation within that day; device and android_os_version are not included in the partition. - Full outer join to unify datasets: - First join installs with ratings on (date_day, package_name, app_version_code) using null-safe comparison by substituting NULL app_version_code with ''null_version'' - Then join crashes on the available date from installs or ratings, plus (package_name, app_version_code, android_os_version), using null-safe comparison by substituting NULL app_version_code with ''null_version'' and NULL android_os_version with ''null_os''; android_os_version is compared as a string; device is not part of any join key. - Output dimensions: - date_day, app_version_code, package_name selected from installs if present, else ratings, else crashes - android_os_version from installs if present else crashes (as string) - device from installs only (NULL if the row originates only from ratings/crashes) - Populate metrics with deterministic null handling: - From installs: active_device_installs → active_devices_last_30_days; all daily device/user/event metrics treat missing values as 0 - From crashes: crashes and anrs treat missing values as 0; values repeat across devices because device is not joined - From ratings: average_rating is the daily average rating (NULL if missing); rolling_total_average_rating is the total-average rating (may be NULL) - Forward-fill selected metrics across dates within (package_name, app_version_code): - For rolling_total_average_rating and each cumulative total, create a segment identifier as the running count of non-NULL values by date_day ascending - Within each segment, carry forward the first observed non-NULL value to subsequent rows; values remain NULL until the first non-NULL appears - Finalize outputs: - total_device_installs and total_device_uninstalls are treated as 0 when still missing after forward-fill - net_device_installs = total_device_installs − total_device_uninstalls - No aggregation or de-duplication beyond the joins; duplicates from sources are preserved; original string casing and spacing are preserved'
      columns:
      - name: date_day
        data_type: DATE
        description: Selected from installs if present, else ratings, else crashes
        tests:
        - not_null
      - name: app_version_code
        data_type: VARCHAR
        description: Taken from whichever source is present; may be NULL; joins substitute NULL with 'null_version'
      - name: package_name
        data_type: VARCHAR
        description: Google Play package identifier selected from the available source
        tests:
        - not_null
      - name: android_os_version
        data_type: VARCHAR
        description: Android OS version from installs else crashes, compared as strings with 'null_os' used when missing
      - name: device
        data_type: VARCHAR
        description: Device identifier from installs; NULL when only ratings/crashes data exists
      - name: device_installs
        data_type: BIGINT
        description: Daily device installs from installs; missing values become 0
      - name: device_uninstalls
        data_type: BIGINT
        description: Daily device uninstalls from installs; missing values become 0
      - name: device_upgrades
        data_type: BIGINT
        description: Daily device upgrades from installs; missing values become 0
      - name: user_installs
        data_type: BIGINT
        description: Daily user installs from installs; missing values become 0
      - name: user_uninstalls
        data_type: BIGINT
        description: Daily user uninstalls from installs; missing values become 0
      - name: install_events
        data_type: BIGINT
        description: Daily install event count from installs; missing values become 0
      - name: uninstall_events
        data_type: BIGINT
        description: Daily uninstall event count from installs; missing values become 0
      - name: update_events
        data_type: BIGINT
        description: Daily update event count from installs; missing values become 0
      - name: crashes
        data_type: BIGINT
        description: Daily crash count joined by date/package/version/OS; missing values become 0 and values repeat across devices
      - name: anrs
        data_type: BIGINT
        description: Daily ANR count joined by date/package/version/OS; missing values become 0 and values repeat across devices
      - name: active_devices_last_30_days
        data_type: BIGINT
        description: Active devices in the last 30 days from installs; missing values become 0
      - name: average_rating
        data_type: DECIMAL(18,3)
        description: Daily average rating from ratings; NULL if unavailable; range 1–5 when present
      - name: rolling_total_average_rating
        data_type: DECIMAL(18,3)
        description: Total-average rating forward-filled by date within (package_name, app_version_code); NULL until the first non-NULL appears
      - name: total_device_installs
        data_type: HUGEINT
        description: Cumulative device installs by date within (package_name, app_version_code), forward-filled across gaps; missing values become 0; same-day tie order follows source row order
      - name: total_device_uninstalls
        data_type: HUGEINT
        description: Cumulative device uninstalls by date within (package_name, app_version_code), forward-filled across gaps; missing values become 0; same-day tie order follows source row order
      - name: net_device_installs
        data_type: HUGEINT
        description: Total device installs minus total device uninstalls; may be negative; never NULL
```

## agent 最终 SQL

S4

```sql
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.app_version_code as VARCHAR) AS app_version_code,
cast(src.package_name as VARCHAR) AS package_name,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.device as VARCHAR) AS device,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as BIGINT) AS crashes,
cast(0 as BIGINT) AS anrs,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_app_version AS src
WHERE src.date_day IS NOT NULL
```

## gold SQL（仅供定位差异）

S5

```sql
with installs as (
    select *
    from staging.stg_google_play__stats_installs_app_version
), 

ratings as (
    select *
    from staging.stg_google_play__stats_ratings_app_version
), 

crashes as (
    select *
    from staging.stg_google_play__stats_crashes_app_version
),

install_metrics as (
    select
        *,
        sum(daily_device_installs) over (
            partition by app_version_code, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_installs,
        sum(daily_device_uninstalls) over (
            partition by app_version_code, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_uninstalls
    from installs 
), 

app_version_join as (
    select 
        coalesce(install_metrics.date_day, ratings.date_day, crashes.date_day) as date_day,
        coalesce(install_metrics.app_version_code, ratings.app_version_code, crashes.app_version_code) as app_version_code,
        coalesce(install_metrics.package_name, ratings.package_name, crashes.package_name) as package_name,
        coalesce(install_metrics.android_os_version, crashes.android_os_version) as android_os_version,
        install_metrics.device,

        -- Device and user metrics
        coalesce(install_metrics.active_device_installs, 0) as active_devices_last_30_days,
        coalesce(install_metrics.daily_device_installs, 0) as device_installs,
        coalesce(install_metrics.daily_device_uninstalls, 0) as device_uninstalls,
        coalesce(install_metrics.daily_device_upgrades, 0) as device_upgrades,
        coalesce(install_metrics.daily_user_installs, 0) as user_installs,
        coalesce(install_metrics.daily_user_uninstalls, 0) as user_uninstalls,
        
        -- event indicators
        coalesce(install_metrics.install_events, 0) as install_events,
        coalesce(install_metrics.uninstall_events, 0) as uninstall_events,
        coalesce(install_metrics.update_events, 0) as update_events,
        coalesce(crashes.crashes, 0) as crashes,
        coalesce(crashes.anrs, 0) as anrs,

        -- Cumulative indicator
        install_metrics.total_device_installs,
        install_metrics.total_device_uninstalls,
        ratings.daily_average_rating as average_rating,
        ratings.total_average_rating as rolling_total_average_rating
        
    from install_metrics
    full outer join ratings
        on install_metrics.date_day = ratings.date_day
        and install_metrics.package_name = ratings.package_name
        and coalesce(install_metrics.app_version_code, 'null_version') = coalesce(ratings.app_version_code, 'null_version')
    full outer join crashes
        on coalesce(install_metrics.date_day, ratings.date_day) = crashes.date_day
        and coalesce(install_metrics.package_name, ratings.package_name) = crashes.package_name
        and coalesce(install_metrics.app_version_code, ratings.app_version_code, 'null_version') = coalesce(crashes.app_version_code, 'null_version')
        and coalesce(cast(install_metrics.android_os_version as varchar), 'null_os') = coalesce(cast(crashes.android_os_version as varchar), 'null_os')
), 

create_partitions as (
    select
        *,
        sum(case when rolling_total_average_rating is null then 0 else 1 end) over (
            partition by app_version_code, package_name 
            order by date_day asc 
            rows unbounded preceding
        ) as rolling_total_average_rating_partition,
        sum(case when total_device_installs is null then 0 else 1 end) over (
            partition by app_version_code, package_name 
            order by date_day asc 
            rows unbounded preceding
        ) as total_device_installs_partition,
        sum(case when total_device_uninstalls is null then 0 else 1 end) over (
            partition by app_version_code, package_name 
            order by date_day asc 
            rows unbounded preceding
        ) as total_device_uninstalls_partition
    from app_version_join
), 

fill_values as (
    select 
        date_day,
        app_version_code,
        package_name,
        android_os_version,
        device,
        active_devices_last_30_days,
        device_installs,
        device_uninstalls,
        device_upgrades,
        user_installs,
        user_uninstalls,
        install_events,
        uninstall_events,
        update_events,
        crashes,
        anrs,
        average_rating,

        first_value(rolling_total_average_rating) over (
            partition by rolling_total_average_rating_partition, app_version_code, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as rolling_total_average_rating,

        first_value(total_device_installs) over (
            partition by total_device_installs_partition, app_version_code, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_installs,

        first_value(total_device_uninstalls) over (
            partition by total_device_uninstalls_partition, app_version_code, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_uninstalls
    from create_partitions
), 

final as (
    select 
        date_day,
        app_version_code,
        package_name,
        android_os_version,
        device,
        device_installs,
        device_uninstalls,
        device_upgrades,
        user_installs,
        user_uninstalls,
        install_events,
        uninstall_events,
        update_events,
        crashes,
        anrs,
        active_devices_last_30_days,
        average_rating,
        rolling_total_average_rating, 
        coalesce(total_device_installs, 0) as total_device_installs,
        coalesce(total_device_uninstalls, 0) as total_device_uninstalls,

        -- Calculate net installs
        coalesce(total_device_installs, 0) - coalesce(total_device_uninstalls, 0) as net_device_installs
    from fill_values
)

select *
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1360 | 1360 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"date_day":"2020-01-01","app_version_code":"1.0.0","package_name":"com.app.musicplayer","device":"null"}</code> |
| K2 | <code>{"date_day":"2020-01-01","app_version_code":"1.0.0","package_name":"com.demo.socialmedia","device":"null"}</code> |
| K3 | <code>{"date_day":"2020-01-01","app_version_code":"1.0.0","package_name":"com.dev.photoeditor","device":"null"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| app_version_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| package_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| android_os_version | 0 | 0 | 0 | VARCHAR | VARCHAR |
| device | 0 | 0 | 0 | VARCHAR | VARCHAR |
| device_installs | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| device_uninstalls | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| device_upgrades | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| user_installs | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| user_uninstalls | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| install_events | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| uninstall_events | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| update_events | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| crashes | 1318 | 1318 | 1318 | BIGINT | BIGINT |
| anrs | 1277 | 1277 | 1277 | BIGINT | BIGINT |
| active_devices_last_30_days | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| average_rating | 1360 | 1360 | 1360 | DECIMAL(18,3) | DECIMAL(18,3) |
| rolling_total_average_rating | 1360 | 1360 | 1360 | DECIMAL(18,3) | DECIMAL(18,3) |
| total_device_installs | 1360 | 1360 | 1360 | HUGEINT | HUGEINT |
| total_device_uninstalls | 1360 | 1360 | 1360 | HUGEINT | HUGEINT |
| net_device_installs | 1360 | 1360 | 1360 | HUGEINT | HUGEINT |

device_installs 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 5 |
| K2 | 0 | 142 |
| K3 | 0 | 117 |

device_uninstalls 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 1 |
| K2 | 0 | 28 |
| K3 | 0 | 23 |

device_upgrades 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 4 |
| K2 | null | 113 |
| K3 | null | 94 |

user_installs 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 4 |
| K2 | null | 127 |
| K3 | null | 106 |

user_uninstalls 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 1 |
| K2 | null | 28 |
| K3 | null | 23 |

install_events 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 10 |
| K2 | null | 161 |
| K3 | null | 119 |

uninstall_events 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 4 |
| K2 | null | 33 |
| K3 | null | 27 |

update_events 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 7 |
| K2 | null | 117 |
| K3 | null | 99 |

crashes 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 36 |
| K2 | 0 | 3 |
| K3 | 0 | 31 |

anrs 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 18 |
| K2 | 0 | 9 |
| K3 | 0 | 13 |

active_devices_last_30_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 35 |
| K2 | null | 995 |
| K3 | null | 825 |

average_rating 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 4.550 |
| K2 | null | 3.300 |
| K3 | null | 4.110 |

rolling_total_average_rating 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 4.300 |
| K2 | null | 3.890 |
| K3 | null | 3.730 |

total_device_installs 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 5 |
| K2 | null | 142 |
| K3 | null | 117 |

total_device_uninstalls 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 1 |
| K2 | null | 28 |
| K3 | null | 23 |

net_device_installs 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 4 |
| K2 | null | 114 |
| K3 | null | 94 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>14列；[{"column":"android_os_version","table_rows":1360},{"column":"device","table_rows":1360},{"column":"device_upgrades","table_rows":1360}]</code> |
| A3_constant_nonnull_column | <code>4列；[{"column":"device_installs","value":"0"},{"column":"device_uninstalls","value":"0"},{"column":"crashes","value":"0"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["device_installs","device_uninstalls","crashes","anrs"],"nonnull_equal_rows":1360,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["device_installs","device_uninstalls","crashes","anrs"],"nonnull_equal_rows":1360,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>12输出列；[{"column":"device_upgrades","expression":["CAST(NULL AS BIGINT)"]},{"column":"user_installs","expression":["CAST(NULL AS BIGINT)"]},{"column":"user_uninstalls","expression":["CAST(NULL AS BIGINT)"]}]</code> |
| B6_constant_literal_output | <code>4输出列；[{"column":"device_installs","expression":["CAST(0 AS BIGINT)"]},{"column":"device_uninstalls","expression":["CAST(0 AS BIGINT)"]},{"column":"crashes","expression":["CAST(0 AS BIGINT)"]}]</code> |
| B7_specified_not_read | <code>["staging.stg_google_play__stats_crashes_app_version","staging.stg_google_play__stats_ratings_app_version"]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -exec sh -c 'echo ===$1; wc -c "$1"' _ {} \;</code> | 3902 | true | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob<br>c=duckdb.connect()<br>c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>c.execute('CREATE SCHEMA raw');<br>for (t,) in c.execute("select table_name from in</code> | 1639 | false | false |
| 21 | run | <code>cat sql/staging/stg_google_play__earnings.sql &#124; head -40; cat sql/staging/stg_google_play__stats_installs_app_version.sql &#124; head -30</code> | 3130 | false | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>p='/tmp/gen.py'<br>s=open(p).read().replace("'transaction_date':'transaction_date'", "'transaction_date':'transaction_date','package_name':'base_plan_id','total_active_subscriptions':'act</code> | 5282 | false | false |
| 27 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob<br>c=duckdb.connect();c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)");c.execute('create schema raw');<br>for (t,) in c.execute("select table_name from in</code> | 596 | false | false |
| 29 | run | <code>python - &lt;&lt;'PY'<br>p='/tmp/gen.py';s=open(p).read();s=s.replace("'total_active_subscriptions':'active_subscriptions'", "'total_active_subscriptions':'active_subscriptions','package_name':'package_name'")</code> | 423 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob,os<br>c=duckdb.connect(); c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>for s in ['raw','staging','intermediate','mart']: c.execute(f'create schema </code> | 4516 | true | false |
| 39 | run | <code>sed -i 's/) prior,/) prior_value,/g;s/ prior, / prior_value, /g;s/(daily_device_installs-prior)::DOUBLE/(daily_device_installs-prior_value)::DOUBLE/g;s/nullif(prior,0)/nullif(prior_value,0)/g' sql/int</code> | 0 | false | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob,os<br>c=duckdb.connect(); c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>for s in ['raw','staging','intermediate','mart']:c.execute(f'create schema {</code> | 967 | true | false |
| 43 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; code=$?; tail -60 /tmp/runlog; exit $code</code> | 4495 | true | false |
| 53 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_google_play__earnings.sql'); s=p.read_text().replace('CAST(sku_id AS VARCHAR) AS sku_id','CAST(coalesce(sku_id, product_id, base_plan_i</code> | 2857 | true | false |

### agent action 的 thought/message 命中原句

未找到命中原句。

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-009.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql`
- S6: `records/006_contract_impl-009.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/result.md`
- S10: `data/021_packages_work/021_impl-009_google_play__app_version_report/021_impl-009_google_play__app_version_report.json`
- S11: `data/005_cs_work/impl-009/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/google_play.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions`
