# impl-009 | marts | google_play__device_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1640–1722

```yaml
    - name: google_play__device_report
      description: Device-level daily performance joined from installs and ratings with forward-filled cumulative totals.
      grain: Rows per package_name, device, date_day from the full outer join; duplicates may exist if sources contain duplicates.
      source_models:
      - staging.stg_google_play__stats_installs_device
      - staging.stg_google_play__stats_ratings_device
      business_logic: '- Read installs and ratings from their staging sources. - In installs, compute running totals by device and package_name ordered by date_day ascending: - total_device_installs accumulates daily_device_installs. - total_device_uninstalls accumulates daily_device_uninstalls. - Full outer join installs and ratings on date_day and package_name, and match device values treating NULLs as equal; choose date_day, device, and package_name from the non-NULL side. - Set daily install/user/event metrics and active_devices_last_30_days to 0 when missing; keep ratings as provided: - average_rating comes from the daily rating. - rolling_total_average_rating comes from the life-to-date rating on that day. - Forward-fill within each device and package_name over ascending date_day: - Carry the latest non-NULL rolling_total_average_rating forward; it remains NULL until the first non-NULL appears. - Carry the latest non-NULL total_device_installs and total_device_uninstalls forward. - Finalize: - Replace remaining NULLs in total_device_installs and total_device_uninstalls with 0. - Compute net_device_installs as total_device_installs minus total_device_uninstalls. - Notes: - All running and forward-fill operations are ordered by date_day ascending. - No de-duplication is performed; if sources contain multiple rows for the same keys and date, all are retained.'
      columns:
      - name: date_day
        data_type: DATE
        description: Calendar date used to align and order metrics.
        tests:
        - not_null
      - name: device
        data_type: VARCHAR
        description: Device identifier chosen from installs or ratings; may be NULL only if missing in both sources.
      - name: package_name
        data_type: VARCHAR
        description: Google Play package identifier chosen from installs or ratings.
      - name: device_installs
        data_type: BIGINT
        description: Daily device installs from installs; NULLs are set to 0.
        tests:
        - device_installs >= 0
      - name: device_uninstalls
        data_type: BIGINT
        description: Daily device uninstalls from installs; NULLs are set to 0.
        tests:
        - device_uninstalls >= 0
      - name: device_upgrades
        data_type: BIGINT
        description: Daily device upgrades from installs; NULLs are set to 0.
        tests:
        - device_upgrades >= 0
      - name: user_installs
        data_type: BIGINT
        description: Daily user installs from installs; NULLs are set to 0.
        tests:
        - user_installs >= 0
      - name: user_uninstalls
        data_type: BIGINT
        description: Daily user uninstalls from installs; NULLs are set to 0.
        tests:
        - user_uninstalls >= 0
      - name: install_events
        data_type: BIGINT
        description: Daily install events from installs; NULLs are set to 0.
        tests:
        - install_events >= 0
      - name: uninstall_events
        data_type: BIGINT
        description: Daily uninstall events from installs; NULLs are set to 0.
        tests:
        - uninstall_events >= 0
      - name: update_events
        data_type: BIGINT
        description: Daily update events from installs; NULLs are set to 0.
        tests:
        - update_events >= 0
      - name: active_devices_last_30_days
        data_type: BIGINT
        description: Active devices in the last 30 days from installs; NULLs are set to 0.
        tests:
        - active_devices_last_30_days >= 0
      - name: average_rating
        data_type: DECIMAL(18,3)
        description: Daily average rating from ratings; may be NULL when no rating is reported.
      - name: rolling_total_average_rating
        data_type: DECIMAL(18,3)
        description: Life-to-date average rating forward-filled within device+package by ascending date; NULL until the first non-NULL.
      - name: total_device_installs
        data_type: HUGEINT
        description: Cumulative device installs within device+package ordered by date, forward-filled, then set to 0 when still missing.
        tests:
        - total_device_installs >= 0
      - name: total_device_uninstalls
        data_type: HUGEINT
        description: Cumulative device uninstalls within device+package ordered by date, forward-filled, then set to 0 when still missing.
        tests:
        - total_device_uninstalls >= 0
      - name: net_device_installs
        data_type: HUGEINT
        description: Difference of cumulative installs and uninstalls after null-to-zero handling; may be negative.
```

## agent 最终 SQL

S4

```sql
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.device as VARCHAR) AS device,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_device AS src
WHERE src.date_day IS NOT NULL
```

## gold SQL（仅供定位差异）

S5

```sql
with installs as (
    select *
    from staging.stg_google_play__stats_installs_device
), 

ratings as (
    select *
    from staging.stg_google_play__stats_ratings_device
), 

install_metrics as (
    select
        *,
        sum(daily_device_installs) over (
            partition by device, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_installs,
        sum(daily_device_uninstalls) over (
            partition by device, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_uninstalls
    from installs 
), 

device_join as (
    select 
        coalesce(install_metrics.date_day, ratings.date_day) as date_day,
        coalesce(install_metrics.device, ratings.device) as device,
        coalesce(install_metrics.package_name, ratings.package_name) as package_name,

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

        -- Cumulative indicator
        install_metrics.total_device_installs,
        install_metrics.total_device_uninstalls,
        ratings.daily_average_rating as average_rating,
        ratings.total_average_rating as rolling_total_average_rating
        
    from install_metrics
    full outer join ratings
        on install_metrics.date_day = ratings.date_day
        and install_metrics.package_name = ratings.package_name
        and coalesce(install_metrics.device, 'null_device') = coalesce(ratings.device, 'null_device')
), 

create_partitions as (
    select
        *,
        sum(case when rolling_total_average_rating is null then 0 else 1 end) over (
            partition by device, package_name 
            order by date_day asc 
            rows unbounded preceding
        ) as rolling_total_average_rating_partition,
        sum(case when total_device_installs is null then 0 else 1 end) over (
            partition by device, package_name 
            order by date_day asc 
            rows unbounded preceding
        ) as total_device_installs_partition,
        sum(case when total_device_uninstalls is null then 0 else 1 end) over (
            partition by device, package_name 
            order by date_day asc 
            rows unbounded preceding
        ) as total_device_uninstalls_partition
    from device_join
), 

fill_values as (
    select 
        date_day,
        device,
        package_name,
        active_devices_last_30_days,
        device_installs,
        device_uninstalls,
        device_upgrades,
        user_installs,
        user_uninstalls,
        install_events,
        uninstall_events,
        update_events,
        average_rating,

        first_value(rolling_total_average_rating) over (
            partition by rolling_total_average_rating_partition, device, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as rolling_total_average_rating,

        first_value(total_device_installs) over (
            partition by total_device_installs_partition, device, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_installs,

        first_value(total_device_uninstalls) over (
            partition by total_device_uninstalls_partition, device, package_name 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_device_uninstalls
    from create_partitions
), 

final as (
    select 
        date_day,
        device,
        package_name,
        device_installs,
        device_uninstalls,
        device_upgrades,
        user_installs,
        user_uninstalls,
        install_events,
        uninstall_events,
        update_events,
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
| K1 | <code>{"date_day":"2020-01-01","device":"huawei p40","package_name":"com.app.musicplayer"}</code> |
| K2 | <code>{"date_day":"2020-01-01","device":"huawei p40","package_name":"com.demo.socialmedia"}</code> |
| K3 | <code>{"date_day":"2020-01-01","device":"huawei p40","package_name":"com.dev.photoeditor"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| device | 0 | 0 | 0 | VARCHAR | VARCHAR |
| package_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| device_installs | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| device_uninstalls | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| device_upgrades | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| user_installs | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| user_uninstalls | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| install_events | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| uninstall_events | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| update_events | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| active_devices_last_30_days | 1360 | 1360 | 1360 | BIGINT | BIGINT |
| average_rating | 1360 | 1360 | 1360 | DECIMAL(18,3) | DECIMAL(18,3) |
| rolling_total_average_rating | 1360 | 1360 | 1360 | DECIMAL(18,3) | DECIMAL(18,3) |
| total_device_installs | 1360 | 1360 | 1360 | HUGEINT | HUGEINT |
| total_device_uninstalls | 1360 | 1360 | 1360 | HUGEINT | HUGEINT |
| net_device_installs | 1360 | 1360 | 1360 | HUGEINT | HUGEINT |

device_installs 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 83 |
| K2 | 0 | 137 |
| K3 | 0 | 106 |

device_uninstalls 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 16 |
| K2 | 0 | 27 |
| K3 | 0 | 21 |

device_upgrades 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 66 |
| K2 | null | 109 |
| K3 | null | 85 |

user_installs 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 74 |
| K2 | null | 123 |
| K3 | null | 95 |

user_uninstalls 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 16 |
| K2 | null | 27 |
| K3 | null | 21 |

install_events 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 99 |
| K2 | null | 137 |
| K3 | null | 118 |

uninstall_events 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 16 |
| K2 | null | 29 |
| K3 | null | 26 |

update_events 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 71 |
| K2 | null | 118 |
| K3 | null | 90 |

active_devices_last_30_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 581 |
| K2 | null | 961 |
| K3 | null | 746 |

average_rating 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 4.290 |
| K2 | null | 4.160 |
| K3 | null | 4.040 |

rolling_total_average_rating 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 4.180 |
| K2 | null | 4.030 |
| K3 | null | 3.860 |

total_device_installs 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 83 |
| K2 | null | 137 |
| K3 | null | 106 |

total_device_uninstalls 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 16 |
| K2 | null | 27 |
| K3 | null | 21 |

net_device_installs 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 67 |
| K2 | null | 110 |
| K3 | null | 85 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>12列；[{"column":"device_upgrades","table_rows":1360},{"column":"user_installs","table_rows":1360},{"column":"user_uninstalls","table_rows":1360}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"device_installs","value":"0"},{"column":"device_uninstalls","value":"0"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["device_installs","device_uninstalls"],"nonnull_equal_rows":1360,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["device_installs","device_uninstalls"],"nonnull_equal_rows":1360,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>12输出列；[{"column":"device_upgrades","expression":["CAST(NULL AS BIGINT)"]},{"column":"user_installs","expression":["CAST(NULL AS BIGINT)"]},{"column":"user_uninstalls","expression":["CAST(NULL AS BIGINT)"]}]</code> |
| B6_constant_literal_output | <code>2输出列；[{"column":"device_installs","expression":["CAST(0 AS BIGINT)"]},{"column":"device_uninstalls","expression":["CAST(0 AS BIGINT)"]}]</code> |
| B7_specified_not_read | <code>["staging.stg_google_play__stats_ratings_device"]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -exec sh -c 'echo ===$1; wc -c "$1"' _ {} \;</code> | 3902 | true | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob<br>c=duckdb.connect()<br>c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>c.execute('CREATE SCHEMA raw');<br>for (t,) in c.execute("select table_name from in</code> | 1639 | false | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>p='/tmp/gen.py'<br>s=open(p).read().replace("'transaction_date':'transaction_date'", "'transaction_date':'transaction_date','package_name':'base_plan_id','total_active_subscriptions':'act</code> | 5282 | false | false |
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/marts/google_play__device_report.sql`
- S6: `records/006_contract_impl-009.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/result.md`
- S10: `data/021_packages_work/021_impl-009_google_play__device_report/021_impl-009_google_play__device_report.json`
- S11: `data/005_cs_work/impl-009/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/google_play.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions`
