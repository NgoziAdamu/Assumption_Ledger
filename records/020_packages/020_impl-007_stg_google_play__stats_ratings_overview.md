# impl-007 | staging | stg_google_play__stats_ratings_overview | 差异：S1；日期 原记录

## 契约完整原文

S3:59–79

```yaml
    - name: stg_google_play__stats_ratings_overview
      description: "Daily and cumulative app rating data from Google Play Console"
      source_table: "raw.stats_ratings_overview"
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: date_day
          data_type: DATE
        - name: package_name
          data_type: VARCHAR
        - name: average_rating
          data_type: DECIMAL(10,2)
          validation_rules:
            - rule: "average_rating >= 1.0 AND average_rating <= 5.0"
              on_failure: delete_row
        - name: rolling_total_average_rating
          data_type: DECIMAL(10,2)
          validation_rules:
            - rule: "rolling_total_average_rating >= 1.0 AND rolling_total_average_rating <= 5.0"
              on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
SELECT
    CAST(_file AS VARCHAR) AS source_relation,
    TRY_CAST(SUBSTR(CAST(date AS VARCHAR), 1, 10) AS DATE) AS date_day,
    CAST(package_name AS VARCHAR) AS package_name,
    TRY_CAST(daily_average_rating AS DECIMAL(10,2)) AS average_rating,
    TRY_CAST(total_average_rating AS DECIMAL(10,2)) AS rolling_total_average_rating
FROM raw.stats_ratings_overview
)
SELECT * FROM source_rows WHERE (average_rating >= 1 AND average_rating <= 5) AND (rolling_total_average_rating IS NULL OR (rolling_total_average_rating >= 1 AND rolling_total_average_rating <= 5))
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *
    from raw.stats_ratings_overview
),

final as (
    select
        'google_play' as source_relation,
        cast(date as date) as date_day,
        cast(package_name as varchar) as package_name,
        cast(
            case
                when daily_average_rating >= 1.0 and daily_average_rating <= 5.0
                then cast(daily_average_rating as decimal(10,2))
                when daily_average_rating is null
                then null -- Keep NULL values
                else 3.0  -- on_failure: correct to middle value
            end as decimal(10,2)
        ) as average_rating,
        cast(
            case
                when total_average_rating >= 1.0 and total_average_rating <= 5.0
                then cast(total_average_rating as decimal(10,2))
                when total_average_rating is null
                then null -- Keep NULL values
                else 3.0  -- on_failure: correct to middle value
            end as decimal(10,2)
        ) as rolling_total_average_rating
    from base
)

select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 691 | 700 | 0 | 9 | 8 | 8 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| package_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| average_rating | 0 | 0 | 0 | DECIMAL(10,2) | DECIMAL(10,2) |
| rolling_total_average_rating | 0 | 0 | 0 | DECIMAL(10,2) | DECIMAL(10,2) |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"date_day":"2024-09-22","package_name":"com.systems.navigation"},{"date_day":"2024-10-04","package_name":"com.systems.navigation"},{"date_day":"2025-03-12","package_name":"com.systems.navigation"},{"date_day":"2025-05-19","package_name":"com.systems.navigation"},{"date_day":"2025-06-30","package_name":"com.systems.navigation"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| D10_keyword_in_any_result_field | <code>命中数=3；assistant_trajectory ), ratings AS (SELECT date_day,package_name app_name,'google_play' platform,average_rating daily_average_rating,rolling_total_average_rating total_average_rating FROM staging.stg_google_play__stats_ratings_overview WHERE average_rating IS NOT NULL),</code> |

## 轨迹索引（不放输出原文）

本题事件总数：70；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 6041 | true | false |
| 13 | run | <code>find sql -type f -print; sed -n '220,520p' run.py; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('app_reporting_start.duckdb',read_only=True)<br>for t in c.execute("select table_name from information_sc</code> | 24579 | false | false |
| 15 | run | <code>find sql -maxdepth 2 -type d -print; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('app_reporting_start.duckdb',read_only=True)<br>for t in ['stats_installs_overview','stats_ratings_overview','earnings'</code> | 4276 | false | false |
| 17 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,160p' docs/data_contract.yaml</code> | 6299 | true | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> print(t['name'],t['source_table'],','.join(x['name'] for x in t['columns']))<br>pr</code> | 5964 | true | false |
| 23 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br># source contract field to raw source field aliases<br>maps={<br>'r</code> | 0 | false | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> f='sql/staging/'+t['name']+'.sql'<br> s=open(f).read()<br> print(t['name'],s.replace(</code> | 8133 | true | false |
| 29 | run | <code>cat &gt; /tmp/advanced.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate')<br>(p/'int_user_lifecycle_analysis.sql').write_text('''WITH first_install AS (<br>    SELECT package_name, min(date_day) AS </code> | 0 | false | false |
| 45 | run | <code>grep -E 'staging\.&#124;ERROR&#124;WARNING' /tmp/pipeline.log &#124; head -100</code> | 18912 | true | false |
| 47 | run | <code>rm -f app_reporting.duckdb; python - &lt;&lt;'PY'<br>import duckdb<br>src=duckdb.connect('app_reporting_start.duckdb',read_only=True); out=duckdb.connect('app_reporting.duckdb'); out.execute('create schema raw')<br></code> | 8738 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,glob,os<br>cfg=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('app_reporting.duckdb',read_only=True)<br>for layer,schema,models in [('staging','staging'</code> | 5387 | true | false |
| 61 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for f in Path('sql/staging').glob('*.sql'):<br> s=f.read_text()<br> if 'CASE WHEN average_rating BETWEEN 0 AND 1' in s:<br>  s=s.replace('CASE WHEN average_rating BETWE</code> | 586 | false | false |
| 63 | run | <code>rm -f app_reporting.duckdb; python run.py &gt;/tmp/finalrun.log 2&gt;&amp;1; grep -E 'layer complete&#124;Errors occurred&#124;completed successfully' /tmp/finalrun.log; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ap</code> | 515 | false | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
), ratings AS (SELECT date_day,package_name app_name,'google_play' platform,average_rating daily_average_rating,rolling_total_average_rating total_average_rating FROM staging.stg_google_play__stats_ratings_overview WHERE average_rating IS NOT NULL),
```
event 61 / message

```text
cat sql/staging/stg_google_play__stats_ratings_overview.sql
```
event 63 / message

```text
checks=[("invalid rating", "select count(*) from staging.stg_google_play__stats_ratings_overview where average_rating not between 1 and 5 or rolling_total_average_rating not between 1 and 5"),("channel conversion outside 0-100", "select count(*) from intermediate.int_channel_performance where conversion_rate_percentage not between 0 and 100"),("lifecycle invalid ages", "select count(*) from intermediate.int_user_lifecycle_analysis where user_age_days<0"),("rfm duplicate grain", "select count(*) from (select app_id,buyer_country,buyer_currency from intermediate.int_user_rfm_analysis group by all having count(*)>1)"),("health score bounds", "select count(*) from intermediate.int_app_health_metrics where health_score not between 0 and 100")]
```

## result.md 本表名原句

未找到 result.md。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-007.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_ratings_overview.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_google_play__stats_ratings_overview.sql`
- S6: `records/006_contract_impl-007.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/020_packages_work/020_impl-007_stg_google_play__stats_ratings_overview/020_impl-007_stg_google_play__stats_ratings_overview.json`
- S10: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`
- S11: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`
- S12: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions`
