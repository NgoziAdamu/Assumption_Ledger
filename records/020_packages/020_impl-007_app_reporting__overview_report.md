# impl-007 | marts | app_reporting__overview_report | 差异：S1；日期 原记录

## 契约完整原文

S3:2421–2452

```yaml
    - name: app_reporting__overview_report
      description: Union-all of Google Play and Apple Store overview rows; passes through daily app KPIs without transformation
      grain: One row per input source row across both sources; duplicates preserved
      source_models:
      - intermediate.int_google_play__overview
      - intermediate.int_apple_store__overview
      business_logic: '- Read all rows from intermediate.int_google_play__overview and intermediate.int_apple_store__overview. - Union ALL the two datasets; no de-duplication and no ordering is enforced. - Select only: source_relation, date_day, app_platform, app_name, downloads, deletions, page_views, crashes. - No filtering, joins, casting, or aggregation; values are passed through exactly as in the sources. - Null policy: NULLs from source are preserved; no defaulting. - Text policy: case and whitespace are preserved. - Numeric policy: integers are passed through without rounding or bounding; negatives are preserved if present.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Identifier of the originating source relation passed through unchanged; NULLs preserved
      - name: date_day
        data_type: DATE
        description: Calendar date from source with no time component; NULLs preserved
      - name: app_platform
        data_type: VARCHAR
        description: Application platform label from source (e.g., android, ios) passed through unchanged; NULLs preserved
      - name: app_name
        data_type: VARCHAR
        description: Application name or identifier passed through unchanged; NULLs preserved
      - name: downloads
        data_type: HUGEINT
        description: Download count passed through unchanged; no aggregation or bounds applied; NULLs and negatives preserved if present
      - name: deletions
        data_type: HUGEINT
        description: Uninstall/deletion count passed through unchanged; no aggregation or bounds applied; NULLs and negatives preserved if present
      - name: page_views
        data_type: HUGEINT
        description: Page view count passed through unchanged; no aggregation or bounds applied; NULLs and negatives preserved if present
      - name: crashes
        data_type: BIGINT
        description: Crash count passed through unchanged; no aggregation or bounds applied; NULLs and negatives preserved if present
```

## agent 最终 SQL

S4

```sql
SELECT source_relation,date_day,app_platform,app_name,downloads,deletions,page_views,crashes FROM intermediate.int_google_play__overview UNION ALL SELECT source_relation,date_day,app_platform,app_name,downloads,deletions,page_views,crashes FROM intermediate.int_apple_store__overview
```

## gold SQL（仅供定位差异）

S5

```sql
with google_play_overview as (
    select * from intermediate.int_google_play__overview
),

apple_store_overview as (
    select * from intermediate.int_apple_store__overview
),

unioned as (
    select * from google_play_overview
    union all
    select * from apple_store_overview
),

final as (
    select 
        source_relation,
        date_day,
        app_platform,
        app_name, 
        downloads,
        deletions,
        page_views,
        crashes
    from unioned
)

select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 8708 | 8708 | 0 | 0 | 366 | 366 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"date_day":"2024-09-05"}</code> |
| K2 | <code>{"date_day":"2024-09-06"}</code> |
| K3 | <code>{"date_day":"2024-09-07"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| app_platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| app_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| downloads | 693 | 693 | 693 | HUGEINT | HUGEINT |
| deletions | 693 | 693 | 693 | HUGEINT | HUGEINT |
| page_views | 0 | 0 | 0 | HUGEINT | HUGEINT |

downloads 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":8},{"value":"102","rows":1},{"value":"1153","rows":1},{"value":"120","rows":1},{"value":"123","rows":1}]</code> | <code>[{"value":"0","rows":12},{"value":"102","rows":1},{"value":"1153","rows":1},{"value":"120","rows":1},{"value":"123","rows":1}]</code> |
| K2 | <code>[{"value":"0","rows":5},{"value":"1129","rows":1},{"value":"14","rows":1},{"value":"172","rows":1},{"value":"182","rows":1}]</code> | <code>[{"value":"0","rows":8},{"value":"1129","rows":1},{"value":"172","rows":1},{"value":"182","rows":1},{"value":"19","rows":1}]</code> |
| K3 | <code>[{"value":"0","rows":6},{"value":"12","rows":1},{"value":"121","rows":1},{"value":"163","rows":1},{"value":"166","rows":1}]</code> | <code>[{"value":"0","rows":9},{"value":"12","rows":1},{"value":"121","rows":1},{"value":"163","rows":1},{"value":"166","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

deletions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":12},{"value":"1006","rows":1},{"value":"105","rows":1},{"value":"1069","rows":1},{"value":"1108","rows":1}]</code> | <code>[{"value":"0","rows":8},{"value":"1006","rows":1},{"value":"105","rows":1},{"value":"1069","rows":1},{"value":"1108","rows":1}]</code> |
| K2 | <code>[{"value":"0","rows":8},{"value":"1018","rows":1},{"value":"1429","rows":1},{"value":"1543","rows":1},{"value":"1571","rows":1}]</code> | <code>[{"value":"0","rows":5},{"value":"1018","rows":1},{"value":"14","rows":1},{"value":"1429","rows":1},{"value":"1543","rows":1}]</code> |
| K3 | <code>[{"value":"0","rows":9},{"value":"1044","rows":1},{"value":"107","rows":1},{"value":"1074","rows":1},{"value":"1144","rows":1}]</code> | <code>[{"value":"0","rows":6},{"value":"1044","rows":1},{"value":"107","rows":1},{"value":"1074","rows":1},{"value":"1144","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

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
| 19 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> print(t['name'],t['source_table'],','.join(x['name'] for x in t['columns']))<br>pr</code> | 5964 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer in ['intermediate_models','marts_models']:<br> for m in c['modeling_spec'][layer]:<br>  print(m['name'],m['description</code> | 2844 | true | false |
| 27 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>out=Path('sql/intermediate')<br>queries={<br>'int_google_play__overview':"""WITH installs AS (SELECT * FROM staging.stg_google_play__stats_installs_overvi</code> | 0 | false | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/marts')<br>sources={'app_reporting__overview_report':'int_google_play__overview','app_reporting__app_version_report':'int_google_play__app_version','a</code> | 0 | false | false |
| 43 | run | <code>python run.py &gt; /tmp/pipeline.log 2&gt;&amp;1; echo EXIT:$?; tail -100 /tmp/pipeline.log</code> | 7846 | true | false |
| 45 | run | <code>grep -E 'staging\.&#124;ERROR&#124;WARNING' /tmp/pipeline.log &#124; head -100</code> | 18912 | false | false |
| 47 | run | <code>rm -f app_reporting.duckdb; python - &lt;&lt;'PY'<br>import duckdb<br>src=duckdb.connect('app_reporting_start.duckdb',read_only=True); out=duckdb.connect('app_reporting.duckdb'); out.execute('create schema raw')<br></code> | 8738 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,glob,os<br>cfg=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('app_reporting.duckdb',read_only=True)<br>for layer,schema,models in [('staging','staging'</code> | 5387 | true | false |

### agent action 的 thought/message 命中原句

event 33 / message

```text
sources={'app_reporting__overview_report':'int_google_play__overview','app_reporting__app_version_report':'int_google_play__app_version','app_reporting__country_report':'int_google_play__country','app_reporting__device_report':'int_google_play__device','app_reporting__os_version_report':'int_google_play__os_version','app_reporting__traffic_source_report':'int_google_play__traffic_source'}
```

## result.md 本表名原句

未找到 result.md。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-007.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/marts/app_reporting__overview_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/marts/app_reporting__overview_report.sql`
- S6: `records/006_contract_impl-007.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/020_packages_work/020_impl-007_app_reporting__overview_report/020_impl-007_app_reporting__overview_report.json`
- S10: `data/005_cs_work/impl-007/node_results.duckdb`
- S11: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`
- S12: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions`
