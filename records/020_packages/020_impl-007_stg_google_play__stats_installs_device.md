# impl-007 | staging | stg_google_play__stats_installs_device | 差异：S1；日期 原记录

## 契约完整原文

S3:383–413

```yaml
    - name: stg_google_play__stats_installs_device
      description: "Install statistics by device from Google Play Console"
      source_table: "raw.stats_installs_device"
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: date_day
          data_type: DATE
        - name: package_name
          data_type: VARCHAR
        - name: device
          data_type: VARCHAR
        - name: active_devices_last_30_days
          data_type: BIGINT
        - name: device_installs
          data_type: BIGINT
        - name: device_uninstalls
          data_type: BIGINT
        - name: device_upgrades
          data_type: BIGINT
        - name: user_installs
          data_type: BIGINT
        - name: user_uninstalls
          data_type: BIGINT
        - name: install_events
          data_type: BIGINT
        - name: uninstall_events
          data_type: BIGINT
        - name: update_events
          data_type: BIGINT

```

## agent 最终 SQL

S4

```sql
SELECT
    CAST(_file AS VARCHAR) AS source_relation,
    TRY_CAST(SUBSTR(CAST(date AS VARCHAR), 1, 10) AS DATE) AS date_day,
    CAST(package_name AS VARCHAR) AS package_name,
    CAST(device AS VARCHAR) AS device,
    TRY_CAST(active_device_installs AS BIGINT) AS active_devices_last_30_days,
    TRY_CAST(daily_device_installs AS BIGINT) AS device_installs,
    TRY_CAST(daily_device_uninstalls AS BIGINT) AS device_uninstalls,
    TRY_CAST(daily_device_upgrades AS BIGINT) AS device_upgrades,
    TRY_CAST(daily_user_installs AS BIGINT) AS user_installs,
    TRY_CAST(daily_user_uninstalls AS BIGINT) AS user_uninstalls,
    TRY_CAST(install_events AS BIGINT) AS install_events,
    TRY_CAST(uninstall_events AS BIGINT) AS uninstall_events,
    TRY_CAST(update_events AS BIGINT) AS update_events
FROM raw.stats_installs_device
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *
    from raw.stats_installs_device
),

final as (
    select
        'google_play' as source_relation,
        cast(date as date) as date_day,
        cast(package_name as varchar) as package_name,
        cast(device as varchar) as device,
        cast(current_device_installs as bigint) as active_devices_last_30_days,
        cast(daily_device_installs as bigint) as device_installs,
        cast(case when daily_device_uninstalls then 1 else 0 end as bigint) as device_uninstalls,
        cast(case when daily_device_upgrades then 1 else 0 end as bigint) as device_upgrades,
        cast(daily_user_installs as bigint) as user_installs,
        cast(case when daily_user_uninstalls then 1 else 0 end as bigint) as user_uninstalls,
        cast(install_events as bigint) as install_events,
        cast(uninstall_events as bigint) as uninstall_events,
        cast(update_events as bigint) as update_events
    from base
)

select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 6000 | 6000 | 0 | 0 | 26 | 26 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"date_day":"2024-09-05","package_name":"com.apps.social","device":"samsung galaxy s23"}</code> |
| K2 | <code>{"date_day":"2024-09-05","package_name":"com.corp.education","device":"samsung galaxy s23"}</code> |
| K3 | <code>{"date_day":"2024-09-05","package_name":"com.creative.photo","device":"vivo x100"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| package_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| device | 0 | 0 | 0 | VARCHAR | VARCHAR |
| active_devices_last_30_days | 5994 | 5994 | 5994 | BIGINT | BIGINT |
| device_installs | 0 | 0 | 0 | BIGINT | BIGINT |
| device_uninstalls | 0 | 0 | 0 | BIGINT | BIGINT |
| device_upgrades | 0 | 0 | 0 | BIGINT | BIGINT |
| user_installs | 0 | 0 | 0 | BIGINT | BIGINT |
| user_uninstalls | 0 | 0 | 0 | BIGINT | BIGINT |
| install_events | 0 | 0 | 0 | BIGINT | BIGINT |
| uninstall_events | 0 | 0 | 0 | BIGINT | BIGINT |
| update_events | 0 | 0 | 0 | BIGINT | BIGINT |

active_devices_last_30_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 5687 | 4560 |
| K2 | 4904 | 3802 |
| K3 | 1957 | 1814 |

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
| 19 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> print(t['name'],t['source_table'],','.join(x['name'] for x in t['columns']))<br>pr</code> | 5964 | true | false |
| 23 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br># source contract field to raw source field aliases<br>maps={<br>'r</code> | 0 | false | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> f='sql/staging/'+t['name']+'.sql'<br> s=open(f).read()<br> print(t['name'],s.replace(</code> | 8133 | true | false |
| 27 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>out=Path('sql/intermediate')<br>queries={<br>'int_google_play__overview':"""WITH installs AS (SELECT * FROM staging.stg_google_play__stats_installs_overvi</code> | 0 | false | false |
| 45 | run | <code>grep -E 'staging\.&#124;ERROR&#124;WARNING' /tmp/pipeline.log &#124; head -100</code> | 18912 | true | false |
| 47 | run | <code>rm -f app_reporting.duckdb; python - &lt;&lt;'PY'<br>import duckdb<br>src=duckdb.connect('app_reporting_start.duckdb',read_only=True); out=duckdb.connect('app_reporting.duckdb'); out.execute('create schema raw')<br></code> | 8738 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,glob,os<br>cfg=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('app_reporting.duckdb',read_only=True)<br>for layer,schema,models in [('staging','staging'</code> | 5387 | true | false |

### agent action 的 thought/message 命中原句

event 27 / message

```text
'int_google_play__device':"""SELECT source_relation,date_day,'google_play' app_platform,package_name app_name,device,device_installs downloads,device_uninstalls deletions FROM staging.stg_google_play__stats_installs_device""",
```

## result.md 本表名原句

未找到 result.md。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-007.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_installs_device.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_google_play__stats_installs_device.sql`
- S6: `records/006_contract_impl-007.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/020_packages_work/020_impl-007_stg_google_play__stats_installs_device/020_impl-007_stg_google_play__stats_installs_device.json`
- S10: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`
- S11: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`
- S12: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions`
