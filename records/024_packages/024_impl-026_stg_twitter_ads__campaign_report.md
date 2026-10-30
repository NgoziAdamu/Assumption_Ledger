# impl-026 | staging | stg_twitter_ads__campaign_report | 差异：S1；日期 原记录

## 契约完整原文

S3:194–228

```yaml
    - name: stg_twitter_ads__campaign_report
      description: "Daily campaign performance aggregated by placement with normalized spend."
      source_table: raw.twitter_campaign_report_data
      columns:
        - name: date_day
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: account_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: campaign_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: placement
          data_type: VARCHAR
        - name: clicks
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
        - name: spend_micro
          data_type: BIGINT
        - name: spend
          data_type: DOUBLE
          description: "Spend amount rounded to 2 decimal places in SQL."
        - name: url_clicks
          data_type: BIGINT
        - name: conversion_purchases_metric
          data_type: BIGINT
        - name: conversion_custom_metric
          data_type: BIGINT
        - name: conversion_purchases_sale_amount
          data_type: DOUBLE
        - name: conversion_custom_sale_amount
          data_type: DOUBLE

```

## agent 最终 SQL

S4

```sql
select
    try_cast(date as timestamp) as date_day,
    account_id,
    campaign_id,
    placement,
    clicks,
    impressions,
    billed_charge_local_micro as spend_micro,
    round(billed_charge_local_micro / 1000000.0, 2) as spend,
    url_clicks,
    cast(null as bigint) as conversion_purchases_metric,
    cast(null as bigint) as conversion_custom_metric,
    cast(null as double) as conversion_purchases_sale_amount,
    cast(null as double) as conversion_custom_sale_amount
from raw.twitter_campaign_report_data
```

## gold SQL（仅供定位差异）

S5

```sql
select
  date_trunc('day', try_cast(date as timestamp)) as date_day,
  account_id,
  campaign_id,
  placement,
  clicks,
  impressions,
  billed_charge_local_micro as spend_micro,
  round(billed_charge_local_micro/1000000.0, 2) as spend,
  url_clicks,
  0::BIGINT as conversion_purchases_metric,
  0::BIGINT as conversion_custom_metric,
  0.0::DOUBLE as conversion_purchases_sale_amount,
  0.0::DOUBLE as conversion_custom_sale_amount
from raw.twitter_campaign_report_data
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2000 | 2000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"account_id":"18ce00eyxqxg0gi","campaign_id":"wfzu8y"}</code> |
| K2 | <code>{"account_id":"18ce02am0yhscjf","campaign_id":"c816a1"}</code> |
| K3 | <code>{"account_id":"18ce02am0yhscjf","campaign_id":"pkap86"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 2000 | 2000 | 2000 | TIMESTAMP | DATE |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| placement | 0 | 0 | 0 | VARCHAR | VARCHAR |
| clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| spend_micro | 0 | 0 | 0 | BIGINT | BIGINT |
| spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| url_clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| conversion_purchases_metric | 2000 | 2000 | 2000 | BIGINT | BIGINT |
| conversion_custom_metric | 2000 | 2000 | 2000 | BIGINT | BIGINT |

date_day 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2020-05-07 00:00:00 | 2020-05-07 |
| K2 | 2023-07-01 00:00:00 | 2023-07-01 |
| K3 | 2020-06-06 00:00:00 | 2020-06-06 |

conversion_purchases_metric 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

conversion_custom_metric 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>4列；[{"column":"conversion_purchases_metric","table_rows":2000},{"column":"conversion_custom_metric","table_rows":2000},{"column":"conversion_purchases_sale_amount","table_rows":2000}]</code> |
| B5_null_literal_output | <code>4输出列；[{"column":"conversion_purchases_metric","expression":["CAST(NULL AS BIGINT)"]},{"column":"conversion_custom_metric","expression":["CAST(NULL AS BIGINT)"]},{"column":"conversion_purchases_sale_amount","expression":["CAST(NULL AS DOUBLE)"]}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：39；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print; cat config/layer_dependencies.yaml; sed -n '1,220p' run.py; cat twitter_start.yaml</code> | 15102 | true | false |
| 9 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('twitter_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw' order by 1").fetcha</code> | 20910 | false | false |
| 13 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging'); I=Path('sql/intermediate'); M=Path('sql/marts')<br>def put(d,n,s): (d/f'{n}.sql')</code> | 0 | false | false |
| 15 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br># Intermediate projection models<br>put(I,'int_twitter_ads__accounts',"""select account_id, approval_status, business_id, business_name, created_timestamp, is_deleted,<br>    indus</code> | 0 | false | false |
| 19 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br>ptdims=['r.date_day','r.placement','r.account_id','a.account_name','li.campaign_id','c.campaign_name','pt.line_item_id','li.line_item_name','r.promoted_tweet_id','pt.tweet_id</code> | 4754 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_twitter_ads__line_item_keywords_report.sql'<br>s=open(p).read().replace('    placement,\n    clicks,', '    placement,\n    clicks,')<br># add keyword_id projection next t</code> | 4229 | true | false |
| 23 | run | <code>sed -n '1,50p' sql/staging/stg_twitter_ads__line_item_keywords_report.sql; sed -n '1,35p' sql/intermediate/int_twitter_ads__campaign_report_base.sql; ls sql/{staging,intermediate,marts} &#124; wc -l</code> | 1211 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/intermediate').glob('*_report_base.sql'):<br> s=p.read_text().replace('select date_day, ', 'select cast(date_day as date) as date_day, ')<br> p.wr</code> | 2974 | true | false |

### agent action 的 thought/message 命中原句

event 13 / message

```text
for name,src in [('stg_twitter_ads__campaign_report','twitter_campaign_report_data'),('stg_twitter_ads__line_item_report','twitter_line_item_report_data'),('stg_twitter_ads__line_item_keywords_report','twitter_line_item_keywords_report_data'),('stg_twitter_ads__promoted_tweet_report','twitter_promoted_tweet_report_data'),('stg_twitter_ads__campaign_locations_report','twitter_campaign_locations_report_data'),('stg_twitter_ads__campaign_regions_report','twitter_campaign_regions_report_data')]: put(S,name,report(name,src))
```
event 15 / message

```text
factdefs=[('campaign_report_base','stg_twitter_ads__campaign_report',['date_day','account_id','campaign_id','placement']),('campaign_locations_report_base','stg_twitter_ads__campaign_locations_report',['date_day','country','account_id','campaign_id','placement']),('campaign_regions_report_base','stg_twitter_ads__campaign_regions_report',['date_day','region','country','account_id','campaign_id','placement']),('line_item_report_base','stg_twitter_ads__line_item_report',['date_day','account_id','line_item_id','placement']),('keyword_report_base','stg_twitter_ads__line_item_keywords_report',['date_day','account_id','line_item_id','keyword_id','keyword','placement']),('promoted_tweet_report_base','stg_twitter_ads__promoted_tweet_report',['date_day','account_id','promoted_tweet_id','placement'])]
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-026.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__campaign_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__campaign_report.sql`
- S6: `records/006_contract_impl-026.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/result.md`
- S10: `data/024_packages_work/024_impl-026_stg_twitter_ads__campaign_report/024_impl-026_stg_twitter_ads__campaign_report.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/twitter.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions`
