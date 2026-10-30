# impl-019 | marts | apple_store__app_version_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1807–1860

```yaml
    - name: apple_store__app_version_report
      description: Daily app-version metrics by source_type per app and source_relation; rows follow reporting_grain and missing metrics are output as 0
      grain: One row per source_relation, date_day, app_id, source_type, app_version
      source_models:
      - intermediate.int_apple_store__app_version_report
      - intermediate.int_apple_store__app_dim
      - intermediate.int_apple_store__app_version_app_crashes
      - intermediate.int_apple_store__app_version_install_deletions
      - intermediate.int_apple_store__app_version_sessions_activity
      business_logic: '- Drive the output from intermediate.int_apple_store__app_version_report (reporting_grain), emitting exactly one row per (source_relation, date_day, app_id, source_type, app_version). - Crashes: join intermediate.int_apple_store__app_version_app_crashes at the same grain without further aggregation. - Installations and deletions: sum per (app_id, date_day, app_version, source_type, source_relation) in intermediate.int_apple_store__app_version_install_deletions before joining. - Sessions and active_devices: sum per (app_id, date_day, app_version, source_type, source_relation) in intermediate.int_apple_store__app_version_sessions_activity before joining. - Left join each metric set to reporting_grain on (app_id, date_day, app_version, source_type, source_relation). - Left join app_name from intermediate.int_apple_store__app_dim on (app_id, source_relation). - Convert NULL metric values to 0; preserve original values otherwise. No sorting or rounding is applied.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Source system identifier from reporting_grain; part of the grain
        tests:
        - not_null
      - name: date_day
        data_type: TIMESTAMP
        description: Reporting day from reporting_grain; matched on exact equality
        tests:
        - not_null
      - name: app_id
        data_type: BIGINT
        description: App identifier from reporting_grain; part of the grain
        tests:
        - not_null
      - name: app_name
        data_type: VARCHAR
        description: App name joined from app_dim by (app_id, source_relation); NULL if no match
      - name: source_type
        data_type: VARCHAR
        description: Traffic/source category from reporting_grain; part of the grain
        tests:
        - not_null
      - name: app_version
        data_type: VARCHAR
        description: App version from reporting_grain; part of the grain
        tests:
        - not_null
      - name: crashes
        data_type: HUGEINT
        description: Crash count taken at the reporting grain; NULLs replaced with 0
      - name: deletions
        data_type: HUGEINT
        description: Deletion count summed per grain from install_deletions; NULLs replaced with 0
      - name: installations
        data_type: HUGEINT
        description: Installation count summed per grain from install_deletions; NULLs replaced with 0
      - name: active_devices
        data_type: HUGEINT
        description: Active device count summed per grain from sessions_activity; NULLs replaced with 0
      - name: sessions
        data_type: HUGEINT
        description: Session count summed per grain from sessions_activity; NULLs replaced with 0
```

## agent 最终 SQL

S4

```sql
WITH g AS (SELECT source_relation, CAST(date_day AS TIMESTAMP) AS date_day, app_id, source_type, app_version FROM intermediate.int_apple_store__app_version_report),
cr AS (SELECT source_relation, date_day, app_id, source_type, app_version, crashes FROM intermediate.int_apple_store__app_version_app_crashes),
inst AS (SELECT source_relation, date_day, app_id, source_type, app_version, SUM(installations) AS installations, SUM(deletions) AS deletions FROM intermediate.int_apple_store__app_version_install_deletions GROUP BY source_relation, date_day, app_id, source_type, app_version),
ses AS (SELECT source_relation, date_day, app_id, source_type, app_version, SUM(sessions) AS sessions, SUM(active_devices) AS active_devices FROM intermediate.int_apple_store__app_version_sessions_activity GROUP BY source_relation, date_day, app_id, source_type, app_version),
app AS (SELECT source_relation, app_id, app_name FROM intermediate.int_apple_store__app_dim)
SELECT g.source_relation,
       g.date_day,
       g.app_id,
       app.app_name,
       g.source_type,
       g.app_version,
       COALESCE(cr.crashes, 0) AS crashes,
       COALESCE(inst.installations, 0) AS installations,
       COALESCE(inst.deletions, 0) AS deletions,
       COALESCE(ses.sessions, 0) AS sessions,
       COALESCE(ses.active_devices, 0) AS active_devices
FROM g
LEFT JOIN cr ON g.source_relation IS NOT DISTINCT FROM cr.source_relation AND g.date_day IS NOT DISTINCT FROM cr.date_day AND g.app_id IS NOT DISTINCT FROM cr.app_id AND g.source_type IS NOT DISTINCT FROM cr.source_type AND g.app_version IS NOT DISTINCT FROM cr.app_version
LEFT JOIN inst ON g.source_relation IS NOT DISTINCT FROM inst.source_relation AND g.date_day IS NOT DISTINCT FROM inst.date_day AND g.app_id IS NOT DISTINCT FROM inst.app_id AND g.source_type IS NOT DISTINCT FROM inst.source_type AND g.app_version IS NOT DISTINCT FROM inst.app_version
LEFT JOIN ses ON g.source_relation IS NOT DISTINCT FROM ses.source_relation AND g.date_day IS NOT DISTINCT FROM ses.date_day AND g.app_id IS NOT DISTINCT FROM ses.app_id AND g.source_type IS NOT DISTINCT FROM ses.source_type AND g.app_version IS NOT DISTINCT FROM ses.app_version
LEFT JOIN app ON g.source_relation IS NOT DISTINCT FROM app.source_relation AND g.app_id IS NOT DISTINCT FROM app.app_id
```

## gold SQL（仅供定位差异）

S5

```sql
-- Marts: App Version report
-- Depends only on intermediate layer

WITH app AS (
    SELECT app_id, app_name, source_relation
    FROM intermediate.int_apple_store__app_dim
),
app_crashes AS (
    SELECT app_id, date_day, app_version, source_type, source_relation,
           crashes
    FROM intermediate.int_apple_store__app_version_app_crashes
),
install_deletions AS (
    SELECT app_id, date_day, app_version, source_type, source_relation,
           SUM(installations) AS installations,
           SUM(deletions) AS deletions
    FROM intermediate.int_apple_store__app_version_install_deletions
    GROUP BY app_id, date_day, app_version, source_type, source_relation
),
sessions_activity AS (
    SELECT app_id, date_day, app_version, source_type, source_relation,
           SUM(sessions) AS sessions,
           SUM(active_devices) AS active_devices
    FROM intermediate.int_apple_store__app_version_sessions_activity
    GROUP BY app_id, date_day, app_version, source_type, source_relation
),
reporting_grain AS (
    SELECT * FROM intermediate.int_apple_store__app_version_report
),
final AS (
    SELECT
        rg.source_relation,
        rg.date_day,
        rg.app_id,
        a.app_name,
        rg.source_type,
        rg.app_version,
        COALESCE(ac.crashes, 0) AS crashes,
        COALESCE(id.deletions, 0) AS deletions,
        COALESCE(id.installations, 0) AS installations,
        COALESCE(sa.active_devices, 0) AS active_devices,
        COALESCE(sa.sessions, 0) AS sessions
    FROM reporting_grain AS rg
    LEFT JOIN app_crashes AS ac
        ON rg.app_id = ac.app_id
        AND rg.date_day = ac.date_day
        AND rg.source_type = ac.source_type
        AND rg.app_version = ac.app_version
        AND rg.source_relation = ac.source_relation
    LEFT JOIN install_deletions AS id
        ON rg.app_id = id.app_id
        AND rg.date_day = id.date_day
        AND rg.source_type = id.source_type
        AND rg.app_version = id.app_version
        AND rg.source_relation = id.source_relation
    LEFT JOIN sessions_activity AS sa
        ON rg.app_id = sa.app_id
        AND rg.date_day = sa.date_day
        AND rg.source_type = sa.source_type
        AND rg.app_version = sa.app_version
        AND rg.source_relation = sa.source_relation
    LEFT JOIN app AS a
        ON rg.app_id = a.app_id
        AND rg.source_relation = a.source_relation
)
SELECT *
FROM final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 82485 | 82485 | 0 | 0 | 12690 | 12690 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"app_id":"239587236","date_day":"2024-10-01 00:00:00","app_version":"null"}</code> |
| K2 | <code>{"app_id":"239587236","date_day":"2024-10-02 00:00:00","app_version":"null"}</code> |
| K3 | <code>{"app_id":"239587236","date_day":"2024-10-03 00:00:00","app_version":"null"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| app_id | 0 | 0 | 0 | BIGINT | BIGINT |
| app_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| source_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| app_version | 0 | 0 | 0 | VARCHAR | VARCHAR |
| crashes | 0 | 0 | 0 | HUGEINT | HUGEINT |
| deletions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| installations | 0 | 0 | 0 | HUGEINT | HUGEINT |
| active_devices | 342 | 342 | 342 | HUGEINT | HUGEINT |
| sessions | 342 | 342 | 342 | HUGEINT | HUGEINT |

active_devices 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"181","rows":1},{"value":"259","rows":1},{"value":"409","rows":1},{"value":"505","rows":1},{"value":"553","rows":1}]</code> | <code>[{"value":"0","rows":5}]</code> |
| K2 | <code>[{"value":"115","rows":1},{"value":"295","rows":1},{"value":"340","rows":1},{"value":"498","rows":1},{"value":"541","rows":1}]</code> | <code>[{"value":"0","rows":5}]</code> |
| K3 | <code>[{"value":"274","rows":1},{"value":"328","rows":1},{"value":"488","rows":1},{"value":"489","rows":1},{"value":"601","rows":1}]</code> | <code>[{"value":"0","rows":5}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

sessions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"429","rows":1},{"value":"550","rows":1},{"value":"678","rows":1},{"value":"779","rows":1},{"value":"937","rows":1}]</code> | <code>[{"value":"0","rows":5}]</code> |
| K2 | <code>[{"value":"202","rows":1},{"value":"530","rows":1},{"value":"641","rows":1},{"value":"748","rows":1},{"value":"811","rows":1}]</code> | <code>[{"value":"0","rows":5}]</code> |
| K3 | <code>[{"value":"455","rows":1},{"value":"618","rows":1},{"value":"754","rows":1},{"value":"849","rows":1},{"value":"950","rows":1}]</code> | <code>[{"value":"0","rows":5}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

| 约束 | 列 | 违反计数 |
|---|---|---|
| not_null | source_type | <code>{"sql_null_rows":34860}</code> |
| not_null | app_version | <code>{"sql_null_rows":12450}</code> |

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"app_name","table_rows":102090}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"app_id","value":"239587236"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：65；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,240p' run.py</code> | 11139 | true | false |
| 15 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>base=Path('sql/intermediate')<br>def put(name,sql):<br> p=base/(name+'.sql'); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(sql.strip()+'\n')<br></code> | 0 | false | false |
| 17 | run | <code>python - &lt;&lt;'PY'<br>import yaml,glob,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer,folder in [('intermediate','intermediate'),('marts','marts')]:<br> for m in c['modeling_spec'][layer+'_mode</code> | 370 | true | false |
| 19 | run | <code>cat &gt;&gt; /tmp/models.py &lt;&lt;'PY'<br># Correct report field order and qualify same-layer references explicitly.<br>for fam,info in families.items():<br> p=base/fam/'reporting_grain'/f'int_apple_store__{fam}_report.</code> | 987 | false | false |
| 21 | run | <code>find sql -type f &#124; wc -l; ls sql/marts; sed -i "/p=base\/\'device_report\/reporting_grain\/int_apple_store__device_report.sql\'/,+2d" /tmp/models.py; tail -35 /tmp/models.py; python /tmp/models.py; py</code> | 4287 | true | false |
| 23 | run | <code>find sql/intermediate -type f &#124; sort</code> | 2773 | false | false |
| 27 | run | <code>python run.py &gt; /tmp/run.log 2&gt;&amp;1; tail -80 /tmp/run.log</code> | 8841 | true | false |
| 29 | run | <code>find sql/staging -type f -printf '%f\n'; grep -E 'Failed&#124;Created&#124;Skip' /tmp/run.log &#124; head -80</code> | 7551 | true | false |
| 31 | run | <code>find sql/intermediate -path '*reporting_grain*' -type f -printf '%p\n'; grep -R 'FROM int_apple_store__\&#124;stg_apple_store__' -n sql/intermediate &#124; grep -v 'staging\.' &#124; head</code> | 751 | false | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br># Missing raw fields called for in staging contract are represented as typed NULLs; source relation remains feed label.<br>for name in ['stg_apple_store__app_cras</code> | 2256 | true | false |
| 37 | run | <code>mkdir -p sql/intermediate/reporting_grain; cp sql/intermediate/territory/reporting_grain/int_apple_store__territory_report.sql sql/intermediate/reporting_grain/; cp sql/intermediate/device_report/repo</code> | 4344 | true | false |
| 41 | run | <code>cat &gt; sql/intermediate/int_apple_store__installation_and_deletion_daily.sql &lt;&lt;'SQL'<br>SELECT<br>    date_day,<br>    app_id,<br>    download_type,<br>    app_version,<br>    device,<br>    platform_version,<br>    source_ty</code> | 3169 | true | false |
| 43 | run | <code>grep -R 'source_type' -n sql/staging; grep -R 'int_apple_store__date_spine' -n sql/intermediate &#124; head; grep -R ';' -n sql &#124; head; grep -R 'FROM int_\&#124;JOIN int_\&#124;FROM staging\&#124;JOIN staging\&#124;FROM inter</code> | 4805 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('apple_store.duckdb',read_only=True)<br>checks=[('staging','stg_apple_store__app_session_daily','date_day'),('intermediate','int_apple_store__date_spine','d</code> | 550 | true | false |
| 47 | run | <code>cat &gt; sql/intermediate/int_apple_store__installation_and_deletion_daily.sql &lt;&lt;'SQL'<br>SELECT<br>    date_day,<br>    app_id,<br>    download_type,<br>    app_version,<br>    device,<br>    platform_version,<br>    source_ty</code> | 640 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
 ('apple_store__app_version_report','app_version','app_version',['source_relation','date_day','app_id','source_type','app_version'], [('cr','int_apple_store__app_version_app_crashes',['crashes'],'direct'),('inst','int_apple_store__app_version_install_deletions',['installations','deletions'],'agg'),('ses','int_apple_store__app_version_sessions_activity',['sessions','active_devices'],'agg')])]
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-019.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__app_version_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/sql/marts/apple_store__app_version_report.sql`
- S6: `records/006_contract_impl-019.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/result.md`
- S10: `data/023_packages_work/023_impl-019_apple_store__app_version_report/023_impl-019_apple_store__app_version_report.json`
- S11: `data/005_cs_work/impl-019_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/apple_store.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions`
