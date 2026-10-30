# impl-019 | marts | apple_store__territory_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1949–2021

```yaml
    - name: apple_store__territory_report
      description: Daily territory/source metrics per app, built from reporting grain with left-joined measures and country metadata, zero-filled for missing measures.
      grain: One row per (source_relation, date_day, app_id, source_type, territory) from intermediate.int_apple_store__territory_report
      source_models:
      - intermediate.int_apple_store__territory_report
      - intermediate.int_apple_store__app_dim
      - intermediate.int_apple_store__territory_impressions_page_views
      - intermediate.int_apple_store__territory_downloads_daily
      - intermediate.int_apple_store__territory_install_deletions
      - intermediate.int_apple_store__territory_sessions_activity
      - intermediate.int_apple_store__country_codes
      business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory). - LEFT JOIN app_dim on app_id and source_relation to add app_name; if no match, app_name is NULL. - LEFT JOIN territory_impressions_page_views on app_id, date_day, source_type, territory, and source_relation; set impressions, impressions_unique_device, page_views, and page_views_unique_device to 0 when missing. - LEFT JOIN territory_downloads_daily on the same keys; set first_time_downloads, redownloads, and total_downloads to 0 when missing. - LEFT JOIN territory_install_deletions on the same keys; set deletions and installations to 0 when missing. - LEFT JOIN territory_sessions_activity on the same keys; set active_devices and sessions to 0 when missing. - LEFT JOIN country_codes on territory equals the two-letter country code; set territory_long to the alternative country name when available, otherwise the standard country name; territory_short mirrors the source territory code and is NULL only when the source territory is NULL; region and sub_region come from country_codes and are NULL when no match. - No aggregation or sorting is applied; base rows are preserved and any duplicates in joined sources will propagate. String casing and spacing are unchanged, and date_day is not truncated or timezone-adjusted.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Source system identifier from the reporting grain, also used in all joins.
      - name: date_day
        data_type: TIMESTAMP
        description: Timestamp from the reporting grain; intended as a day but any time component is preserved.
      - name: app_id
        data_type: BIGINT
        description: Application identifier from the reporting grain and the join key to all metric tables and app_dim.
      - name: app_name
        data_type: VARCHAR
        description: Application name from app_dim joined on app_id and source_relation; NULL when no match.
      - name: source_type
        data_type: VARCHAR
        description: Traffic source category from the reporting grain; passed through unchanged.
      - name: territory_long
        data_type: VARCHAR
        description: Country long name from country_codes, preferring the alternative name when present; NULL when no country_codes match.
      - name: territory_short
        data_type: VARCHAR
        description: Two-letter country code from the reporting grain; NULL only when the source territory is NULL.
      - name: region
        data_type: VARCHAR
        description: Region from country_codes for the matched territory; NULL when no country_codes match.
      - name: sub_region
        data_type: VARCHAR
        description: Sub-region from country_codes for the matched territory; NULL when no country_codes match.
      - name: impressions
        data_type: HUGEINT
        description: Impressions from territory_impressions_page_views at the full grain; missing values output as 0.
      - name: impressions_unique_device
        data_type: HUGEINT
        description: Unique-device impressions from territory_impressions_page_views; missing values output as 0.
      - name: page_views
        data_type: HUGEINT
        description: Page views from territory_impressions_page_views; missing values output as 0.
      - name: page_views_unique_device
        data_type: HUGEINT
        description: Unique-device page views from territory_impressions_page_views; missing values output as 0.
      - name: first_time_downloads
        data_type: HUGEINT
        description: First-time downloads from territory_downloads_daily; missing values output as 0.
      - name: redownloads
        data_type: HUGEINT
        description: Redownloads from territory_downloads_daily; missing values output as 0.
      - name: total_downloads
        data_type: HUGEINT
        description: Total downloads from territory_downloads_daily; missing values output as 0.
      - name: active_devices
        data_type: HUGEINT
        description: Active devices from territory_sessions_activity; missing values output as 0.
      - name: deletions
        data_type: HUGEINT
        description: App deletions from territory_install_deletions; missing values output as 0.
      - name: installations
        data_type: HUGEINT
        description: App installations from territory_install_deletions; missing values output as 0.
      - name: sessions
        data_type: HUGEINT
        description: Sessions from territory_sessions_activity; missing values output as 0.
```

## agent 最终 SQL

S4

```sql
WITH g AS (SELECT source_relation, CAST(date_day AS TIMESTAMP) AS date_day, app_id, source_type, territory FROM intermediate.int_apple_store__territory_report),
app AS (SELECT source_relation, app_id, app_name FROM intermediate.int_apple_store__app_dim),
ip AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(impressions) AS impressions, SUM(impressions_unique_device) AS impressions_unique_device, SUM(page_views) AS page_views, SUM(page_views_unique_device) AS page_views_unique_device FROM intermediate.int_apple_store__territory_impressions_page_views GROUP BY source_relation, date_day, app_id, source_type, territory),
dl AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(first_time_downloads) AS first_time_downloads, SUM(redownloads) AS redownloads, SUM(total_downloads) AS total_downloads FROM intermediate.int_apple_store__territory_downloads_daily GROUP BY source_relation, date_day, app_id, source_type, territory),
ins AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(deletions) AS deletions, SUM(installations) AS installations FROM intermediate.int_apple_store__territory_install_deletions GROUP BY source_relation, date_day, app_id, source_type, territory),
ses AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(active_devices) AS active_devices, SUM(sessions) AS sessions FROM intermediate.int_apple_store__territory_sessions_activity GROUP BY source_relation, date_day, app_id, source_type, territory),
cc AS (SELECT country_code_alpha_2, alternative_country_name, country_name, region, sub_region FROM intermediate.int_apple_store__country_codes)
SELECT g.source_relation,
       g.date_day,
       g.app_id,
       app.app_name,
       COALESCE(cc.alternative_country_name, cc.country_name) AS territory_long,
       g.territory AS territory_short,
       cc.region,
       cc.sub_region,
       g.source_type,
       COALESCE(ip.impressions, 0) AS impressions,
       COALESCE(ip.impressions_unique_device, 0) AS impressions_unique_device,
       COALESCE(ip.page_views, 0) AS page_views,
       COALESCE(ip.page_views_unique_device, 0) AS page_views_unique_device,
       COALESCE(dl.first_time_downloads, 0) AS first_time_downloads,
       COALESCE(dl.redownloads, 0) AS redownloads,
       COALESCE(dl.total_downloads, 0) AS total_downloads,
       COALESCE(ins.deletions, 0) AS deletions,
       COALESCE(ins.installations, 0) AS installations,
       COALESCE(ses.active_devices, 0) AS active_devices,
       COALESCE(ses.sessions, 0) AS sessions
FROM g
LEFT JOIN ip ON g.source_relation IS NOT DISTINCT FROM ip.source_relation AND g.date_day IS NOT DISTINCT FROM ip.date_day AND g.app_id IS NOT DISTINCT FROM ip.app_id AND g.source_type IS NOT DISTINCT FROM ip.source_type AND g.territory IS NOT DISTINCT FROM ip.territory
LEFT JOIN dl ON g.source_relation IS NOT DISTINCT FROM dl.source_relation AND g.date_day IS NOT DISTINCT FROM dl.date_day AND g.app_id IS NOT DISTINCT FROM dl.app_id AND g.source_type IS NOT DISTINCT FROM dl.source_type AND g.territory IS NOT DISTINCT FROM dl.territory
LEFT JOIN ins ON g.source_relation IS NOT DISTINCT FROM ins.source_relation AND g.date_day IS NOT DISTINCT FROM ins.date_day AND g.app_id IS NOT DISTINCT FROM ins.app_id AND g.source_type IS NOT DISTINCT FROM ins.source_type AND g.territory IS NOT DISTINCT FROM ins.territory
LEFT JOIN ses ON g.source_relation IS NOT DISTINCT FROM ses.source_relation AND g.date_day IS NOT DISTINCT FROM ses.date_day AND g.app_id IS NOT DISTINCT FROM ses.app_id AND g.source_type IS NOT DISTINCT FROM ses.source_type AND g.territory IS NOT DISTINCT FROM ses.territory
LEFT JOIN app ON g.source_relation IS NOT DISTINCT FROM app.source_relation AND g.app_id IS NOT DISTINCT FROM app.app_id
LEFT JOIN cc ON g.territory = cc.country_code_alpha_2
```

## gold SQL（仅供定位差异）

S5

```sql
-- Marts: Territory report

WITH app AS (
  SELECT app_id, app_name, source_relation
  FROM intermediate.int_apple_store__app_dim
),
impressions_and_page_views AS (
  SELECT * FROM intermediate.int_apple_store__territory_impressions_page_views
),
downloads_daily AS (
  SELECT * FROM intermediate.int_apple_store__territory_downloads_daily
),
install_deletions AS (
  SELECT * FROM intermediate.int_apple_store__territory_install_deletions
),
sessions_activity AS (
  SELECT * FROM intermediate.int_apple_store__territory_sessions_activity
),
country_codes AS (
  SELECT * FROM intermediate.int_apple_store__country_codes
),
reporting_grain AS (
  SELECT * FROM intermediate.int_apple_store__territory_report
),
final AS (
  SELECT
    rg.source_relation,
    rg.date_day,
    rg.app_id,
    a.app_name,
    rg.source_type,
    COALESCE(country_codes.alternative_country_name, country_codes.country_name) AS territory_long,
    COALESCE(rg.territory, country_codes.country_code_alpha_2) AS territory_short,
    country_codes.region AS region,
    country_codes.sub_region AS sub_region,
    COALESCE(ip.impressions, 0) AS impressions,
    COALESCE(ip.impressions_unique_device, 0) AS impressions_unique_device,
    COALESCE(ip.page_views, 0) AS page_views,
    COALESCE(ip.page_views_unique_device, 0) AS page_views_unique_device,
    COALESCE(dd.first_time_downloads, 0) AS first_time_downloads,
    COALESCE(dd.redownloads, 0) AS redownloads,
    COALESCE(dd.total_downloads, 0) AS total_downloads,
    COALESCE(sa.active_devices, 0) AS active_devices,
    COALESCE(id.deletions, 0) AS deletions,
    COALESCE(id.installations, 0) AS installations,
    COALESCE(sa.sessions, 0) AS sessions
  FROM reporting_grain rg
  LEFT JOIN app a
    ON rg.app_id = a.app_id AND rg.source_relation = a.source_relation
  LEFT JOIN impressions_and_page_views ip
    ON rg.app_id = ip.app_id AND rg.date_day = ip.date_day
   AND rg.source_type = ip.source_type AND rg.territory = ip.territory
   AND rg.source_relation = ip.source_relation
  LEFT JOIN downloads_daily dd
    ON rg.app_id = dd.app_id AND rg.date_day = dd.date_day
   AND rg.source_type = dd.source_type AND rg.territory = dd.territory
   AND rg.source_relation = dd.source_relation
  LEFT JOIN install_deletions id
    ON rg.app_id = id.app_id AND rg.date_day = id.date_day
   AND rg.source_type = id.source_type AND rg.territory = id.territory
   AND rg.source_relation = id.source_relation
  LEFT JOIN sessions_activity sa
    ON rg.app_id = sa.app_id AND rg.date_day = sa.date_day
   AND rg.source_type = sa.source_type AND rg.territory = sa.territory
   AND rg.source_relation = sa.source_relation
  LEFT JOIN country_codes
    ON rg.territory = country_codes.country_code_alpha_2
)
SELECT *
FROM final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 219960 | 219960 | 0 | 0 | 10575 | 10575 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"date_day":"2024-12-05 00:00:00","app_id":"239587236","region":"null"}</code> |
| K2 | <code>{"date_day":"2024-10-07 00:00:00","app_id":"239587236","region":"null"}</code> |
| K3 | <code>{"date_day":"2024-10-18 00:00:00","app_id":"239587236","region":"null"}</code> |
| K4 | <code>{"date_day":"2024-10-24 00:00:00","app_id":"239587236","region":"null"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| app_id | 0 | 0 | 0 | BIGINT | BIGINT |
| app_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| territory_long | 0 | 0 | 0 | VARCHAR | VARCHAR |
| territory_short | 0 | 0 | 0 | VARCHAR | VARCHAR |
| region | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sub_region | 0 | 0 | 0 | VARCHAR | VARCHAR |
| impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| impressions_unique_device | 0 | 0 | 0 | HUGEINT | HUGEINT |
| page_views | 0 | 0 | 0 | HUGEINT | HUGEINT |
| page_views_unique_device | 0 | 0 | 0 | HUGEINT | HUGEINT |
| first_time_downloads | 0 | 0 | 0 | HUGEINT | HUGEINT |
| redownloads | 1 | 1 | 1 | HUGEINT | HUGEINT |
| total_downloads | 1 | 1 | 1 | HUGEINT | HUGEINT |
| active_devices | 11 | 11 | 11 | HUGEINT | HUGEINT |
| deletions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| installations | 0 | 0 | 0 | HUGEINT | HUGEINT |
| sessions | 11 | 11 | 11 | HUGEINT | HUGEINT |

redownloads 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":14},{"value":"80","rows":1}]</code> | <code>[{"value":"0","rows":15}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

total_downloads 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":14},{"value":"80","rows":1}]</code> | <code>[{"value":"0","rows":15}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

active_devices 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":"0","rows":14},{"value":"14","rows":1}]</code> | <code>[{"value":"0","rows":15}]</code> |
| K3 | <code>[{"value":"0","rows":14},{"value":"80","rows":1}]</code> | <code>[{"value":"0","rows":15}]</code> |
| K4 | <code>[{"value":"0","rows":14},{"value":"54","rows":1}]</code> | <code>[{"value":"0","rows":15}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

sessions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":"0","rows":14},{"value":"41","rows":1}]</code> | <code>[{"value":"0","rows":15}]</code> |
| K3 | <code>[{"value":"0","rows":14},{"value":"146","rows":1}]</code> | <code>[{"value":"0","rows":15}]</code> |
| K4 | <code>[{"value":"0","rows":14},{"value":"64","rows":1}]</code> | <code>[{"value":"0","rows":15}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"app_name","table_rows":831660}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"app_id","value":"239587236"},{"column":"first_time_downloads","value":"0"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["redownloads","total_downloads"],"nonnull_equal_rows":831660,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["redownloads","total_downloads"],"nonnull_equal_rows":831660,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |

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
| 33 | run | <code>cat sql/staging/stg_apple_store__app_crash_daily.sql; cat sql/staging/stg_apple_store__sales_subscription_summary.sql &#124; tail -10; cat sql/intermediate/overview/int_apple_store__app.sql; cat sql/interm</code> | 2239 | false | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br># Missing raw fields called for in staging contract are represented as typed NULLs; source relation remains feed label.<br>for name in ['stg_apple_store__app_cras</code> | 2256 | true | false |
| 37 | run | <code>mkdir -p sql/intermediate/reporting_grain; cp sql/intermediate/territory/reporting_grain/int_apple_store__territory_report.sql sql/intermediate/reporting_grain/; cp sql/intermediate/device_report/repo</code> | 4344 | true | false |
| 41 | run | <code>cat &gt; sql/intermediate/int_apple_store__installation_and_deletion_daily.sql &lt;&lt;'SQL'<br>SELECT<br>    date_day,<br>    app_id,<br>    download_type,<br>    app_version,<br>    device,<br>    platform_version,<br>    source_ty</code> | 3169 | true | false |
| 43 | run | <code>grep -R 'source_type' -n sql/staging; grep -R 'int_apple_store__date_spine' -n sql/intermediate &#124; head; grep -R ';' -n sql &#124; head; grep -R 'FROM int_\&#124;JOIN int_\&#124;FROM staging\&#124;JOIN staging\&#124;FROM inter</code> | 4805 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('apple_store.duckdb',read_only=True)<br>checks=[('staging','stg_apple_store__app_session_daily','date_day'),('intermediate','int_apple_store__date_spine','d</code> | 550 | true | false |
| 47 | run | <code>cat &gt; sql/intermediate/int_apple_store__installation_and_deletion_daily.sql &lt;&lt;'SQL'<br>SELECT<br>    date_day,<br>    app_id,<br>    download_type,<br>    app_version,<br>    device,<br>    platform_version,<br>    source_ty</code> | 640 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
put('apple_store__territory_report','WITH '+',\n'.join(ctes)+'\nSELECT '+',\n       '.join(sel)+'\nFROM g\n'+'\n'.join(joins))
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-019.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql`
- S6: `records/006_contract_impl-019.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/result.md`
- S10: `data/023_packages_work/023_impl-019_apple_store__territory_report/023_impl-019_apple_store__territory_report.json`
- S11: `data/005_cs_work/impl-019_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/apple_store.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions`
