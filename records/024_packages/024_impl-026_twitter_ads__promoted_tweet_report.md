# impl-026 | marts | twitter_ads__promoted_tweet_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1678–1776

```yaml
    - name: twitter_ads__promoted_tweet_report
      description: Daily promoted tweet performance aggregated by placement and enriched with tweet, line item, campaign, and account attributes via left joins.
      grain: One row per unique combination of date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, currency, is_deleted, promoted_tweet_status, campaign_status, line_item_status, approval_status, created_timestamp, updated_timestamp
      source_models:
      - intermediate.int_twitter_ads__promoted_tweet_report_base
      - intermediate.int_twitter_ads__promoted_tweets
      - intermediate.int_twitter_ads__tweets
      - intermediate.int_twitter_ads__line_items
      - intermediate.int_twitter_ads__campaigns
      - intermediate.int_twitter_ads__accounts
      business_logic: '- Start from the daily promoted tweet metrics base. - Left join promoted tweets by promoted_tweet_id. - Left join tweets by tweet_id from promoted tweets. - Left join line items by line_item_id from promoted tweets. - Left join campaigns by campaign_id from line items. - Left join accounts by account_id from the base. - Aggregate by these attributes: date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, currency, is_deleted, promoted_tweet_status, campaign_status, line_item_status, approval_status, created_timestamp, updated_timestamp. - For clicks, impressions, spend, spend_micro, url_clicks, total_conversions, and total_conversions_sale_amount: sum base values within each group; NULL inputs are ignored and a group of all NULLs yields NULL; numeric types are preserved with no rounding. - Left join behavior: if no match, the joined attributes are NULL; if multiple matches occur in a joined table, base rows are duplicated before aggregation, increasing summed metrics. - No explicit ordering is applied to the result.'
      columns:
      - name: date_day
        data_type: DATE
        description: Calendar date from the base metrics; grouping key.
        tests:
        - not_null
      - name: placement
        data_type: VARCHAR
        description: Inventory placement from the base metrics; grouping key.
      - name: account_id
        data_type: VARCHAR
        description: Ads account ID from the base metrics; grouping key.
        tests:
        - not_null
      - name: account_name
        data_type: VARCHAR
        description: Account name from accounts; NULL if no match.
      - name: campaign_id
        data_type: VARCHAR
        description: Campaign ID from campaigns; NULL if no match.
      - name: campaign_name
        data_type: VARCHAR
        description: Campaign name from campaigns; NULL if no match.
      - name: line_item_id
        data_type: VARCHAR
        description: Line item ID from line items; NULL if no match.
      - name: line_item_name
        data_type: VARCHAR
        description: Line item name from line items; NULL if no match.
      - name: promoted_tweet_id
        data_type: VARCHAR
        description: Promoted tweet ID from the base metrics; grouping key.
        tests:
        - not_null
      - name: tweet_id
        data_type: BIGINT
        description: Tweet ID from promoted tweets; NULL if no match.
      - name: tweet_name
        data_type: VARCHAR
        description: Tweet name from tweets; NULL if no match.
      - name: tweet_full_text
        data_type: VARCHAR
        description: Tweet full text from tweets; NULL if no match.
      - name: currency
        data_type: VARCHAR
        description: ISO currency from campaigns; NULL if no match; unit for spend.
      - name: is_deleted
        data_type: BOOLEAN
        description: Soft-delete flag from promoted tweets; NULL if no match.
      - name: promoted_tweet_status
        data_type: VARCHAR
        description: Lifecycle status from promoted tweets; NULL if no match.
      - name: campaign_status
        data_type: VARCHAR
        description: Lifecycle status from campaigns; NULL if no match.
      - name: line_item_status
        data_type: VARCHAR
        description: Lifecycle status from line items; NULL if no match.
      - name: approval_status
        data_type: VARCHAR
        description: Approval status from promoted tweets; NULL if no match.
      - name: created_timestamp
        data_type: TIMESTAMP
        description: Creation timestamp from promoted tweets; NULL if no match.
      - name: updated_timestamp
        data_type: TIMESTAMP
        description: Last update timestamp from promoted tweets; NULL if no match.
      - name: clicks
        data_type: HUGEINT
        description: Sum of clicks within each group; ignores NULLs; NULL if all inputs are NULL.
      - name: impressions
        data_type: HUGEINT
        description: Sum of impressions within each group; ignores NULLs; NULL if all inputs are NULL.
      - name: spend
        data_type: DOUBLE
        description: Sum of spend within each group in currency units; ignores NULLs; NULL if all inputs are NULL; no rounding.
      - name: spend_micro
        data_type: HUGEINT
        description: Sum of spend_micro within each group; ignores NULLs; NULL if all inputs are NULL.
      - name: url_clicks
        data_type: HUGEINT
        description: Sum of URL clicks within each group; ignores NULLs; NULL if all inputs are NULL.
      - name: total_conversions
        data_type: HUGEINT
        description: Sum of total conversions within each group; ignores NULLs; NULL if all inputs are NULL.
      - name: total_conversions_sale_amount
        data_type: DOUBLE
        description: Sum of conversion sale amount within each group; ignores NULLs; NULL if all inputs are NULL; no rounding.
```

## agent 最终 SQL

S4

```sql
select
    r.date_day, r.placement, r.account_id, a.account_name, li.campaign_id, c.campaign_name, pt.line_item_id, li.line_item_name, r.promoted_tweet_id, pt.tweet_id, t.tweet_name, t.tweet_full_text, li.currency, pt.is_deleted, pt.promoted_tweet_status, c.entity_status as campaign_status, li.entity_status as line_item_status, pt.approval_status, pt.created_timestamp, pt.updated_timestamp,
    sum(r.clicks) as clicks, sum(r.impressions) as impressions, sum(r.spend) as spend,
    sum(r.spend_micro) as spend_micro, sum(r.url_clicks) as url_clicks,
    sum(r.total_conversions) as total_conversions,
    sum(r.total_conversions_sale_amount) as total_conversions_sale_amount
from intermediate.int_twitter_ads__promoted_tweet_report_base r
left join intermediate.int_twitter_ads__promoted_tweets pt on r.promoted_tweet_id = pt.promoted_tweet_id
left join intermediate.int_twitter_ads__tweets t on pt.tweet_id = t.tweet_id
left join intermediate.int_twitter_ads__line_items li on pt.line_item_id = li.line_item_id
left join intermediate.int_twitter_ads__campaigns c on li.campaign_id = c.campaign_id
left join intermediate.int_twitter_ads__accounts a on r.account_id = a.account_id
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
```

## gold SQL（仅供定位差异）

S5

```sql
select
  r.date_day,
  r.placement,
  r.account_id,
  a.account_name,
  c.campaign_id,
  c.campaign_name,
  li.line_item_id,
  li.line_item_name,
  r.promoted_tweet_id,
  pt.tweet_id,
  t.tweet_name,
  t.tweet_full_text,
  c.currency,
  pt.is_deleted,
  pt.promoted_tweet_status,
  c.entity_status as campaign_status,
  li.entity_status as line_item_status,
  pt.approval_status,
  pt.created_timestamp,
  pt.updated_timestamp,
  sum(r.clicks) as clicks,
  sum(r.impressions) as impressions,
  sum(r.spend) as spend,
  sum(r.spend_micro) as spend_micro,
  sum(r.url_clicks) as url_clicks,
  sum(r.total_conversions) as total_conversions,
  sum(r.total_conversions_sale_amount) as total_conversions_sale_amount
from intermediate.int_twitter_ads__promoted_tweet_report_base r
left join intermediate.int_twitter_ads__promoted_tweets pt on r.promoted_tweet_id = pt.promoted_tweet_id
left join intermediate.int_twitter_ads__tweets t on pt.tweet_id = t.tweet_id
left join intermediate.int_twitter_ads__line_items li on pt.line_item_id = li.line_item_id
left join intermediate.int_twitter_ads__campaigns c on li.campaign_id = c.campaign_id
left join intermediate.int_twitter_ads__accounts a on r.account_id = a.account_id
group by
  r.date_day, r.placement, r.account_id, a.account_name, c.campaign_id, c.campaign_name, li.line_item_id, li.line_item_name,
  r.promoted_tweet_id, pt.tweet_id, t.tweet_name, t.tweet_full_text, c.currency, pt.is_deleted, pt.promoted_tweet_status,
  c.entity_status, li.entity_status, pt.approval_status, pt.created_timestamp, pt.updated_timestamp
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2500 | 2500 | 10 | 10 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"account_id":"18ce00eyxqxg0gi","promoted_tweet_id":"tpqopt1z","date_day":"2020-07-04","placement":"publisher_network","campaign_id":"qevz9c","line_item_id":"co9ee1","tweet_id":"1461822136853196175"}</code> |
| K2 | <code>{"account_id":"18ce01x86g1c54w","promoted_tweet_id":"f3k4m107","date_day":"2023-04-17","placement":"all_on_twitter","campaign_id":"6fvng7","line_item_id":"qcylxd","tweet_id":"1236103267371359741"}</code> |
| K3 | <code>{"account_id":"18ce01x86g1c54w","promoted_tweet_id":"jd1760uc","date_day":"2020-01-14","placement":"publisher_network","campaign_id":"spr8rw","line_item_id":"ui2u7q","tweet_id":"1717477517611653164"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| placement | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| line_item_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| line_item_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| promoted_tweet_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| tweet_id | 0 | 0 | 0 | BIGINT | BIGINT |
| tweet_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| currency | 2012 | 2012 | 2012 | VARCHAR | VARCHAR |
| is_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| promoted_tweet_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| line_item_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| approval_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| updated_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| clicks | 0 | 0 | 0 | HUGEINT | HUGEINT |
| impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| spend_micro | 0 | 0 | 0 | HUGEINT | HUGEINT |
| url_clicks | 0 | 0 | 0 | HUGEINT | HUGEINT |
| total_conversions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| total_conversions_sale_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |

currency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | EUR | JPY |
| K2 | GBP | JPY |
| K3 | GBP | CAD |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"account_id":"18ce0nj1el178vs","promoted_tweet_id":"jexe6bxb","date_day":"2020-10-09","placement":"PUBLISHER_NETWORK","campaign_id":"y929p2","line_item_id":"hnoc05","tweet_id":"1079898820183637319"},{"account_id":"18ce6b9wduqn5rw","promoted_tweet_id":"t4padadx","date_day":"2022-06-15","placement":"PUBLISHER_NETWORK","campaign_id":"2bqzz4","line_item_id":"jagver","tweet_id":"1142260991448454867"},{"account_id":"18cebqg9tp0fr4c","promoted_tweet_id":"t4padadx","date_day":"2021-12-26","placement":"ALL_ON_TWITTER","campaign_id":"2bqzz4","line_item_id":"jagver","tweet_id":"1142260991448454867"},{"account_id":"18cedogzm2ogb02","promoted_tweet_id":"d24bbx9t","date_day":"2023-10-26","placement":"ALL_ON_TWITTER","campaign_id":"2bqzz4","line_item_id":"etci35","tweet_id":"1967062411030397457"},{"account_id":"18ceez2z609qg2s","promoted_tweet_id":"d24bbx9t","date_day":"2020-05-15","placement":"ALL_ON_TWITTER","campaign_id":"2bqzz4","line_item_id":"etci35","tweet_id":"1967062411030397457"}]</code> | <code>[{"account_id":"18ce0nj1el178vs","promoted_tweet_id":"jexe6bxb","date_day":"2020-10-09","placement":"PUBLISHER_NETWORK","campaign_id":null,"line_item_id":"hnoc05","tweet_id":"1079898820183637319"},{"account_id":"18ce6b9wduqn5rw","promoted_tweet_id":"t4padadx","date_day":"2022-06-15","placement":"PUBLISHER_NETWORK","campaign_id":null,"line_item_id":"jagver","tweet_id":"1142260991448454867"},{"account_id":"18cebqg9tp0fr4c","promoted_tweet_id":"t4padadx","date_day":"2021-12-26","placement":"ALL_ON_TWITTER","campaign_id":null,"line_item_id":"jagver","tweet_id":"1142260991448454867"},{"account_id":"18cedogzm2ogb02","promoted_tweet_id":"d24bbx9t","date_day":"2023-10-26","placement":"ALL_ON_TWITTER","campaign_id":null,"line_item_id":"etci35","tweet_id":"1967062411030397457"},{"account_id":"18ceez2z609qg2s","promoted_tweet_id":"d24bbx9t","date_day":"2020-05-15","placement":"ALL_ON_TWITTER","campaign_id":null,"line_item_id":"etci35","tweet_id":"1967062411030397457"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>2列；[{"column":"total_conversions","value":"0"},{"column":"total_conversions_sale_amount","value":"0.0"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：39；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print; cat config/layer_dependencies.yaml; sed -n '1,220p' run.py; cat twitter_start.yaml</code> | 15102 | true | false |
| 15 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br># Intermediate projection models<br>put(I,'int_twitter_ads__accounts',"""select account_id, approval_status, business_id, business_name, created_timestamp, is_deleted,<br>    indus</code> | 0 | false | false |
| 17 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br># Mart aggregate helpers<br>def agg_model(name, source, dims, fromjoins, measures):<br>    select_dims=',\n    '.join(dims)<br>    aggs=',\n    '.join(f'sum({x}) as {x}' for x in meas</code> | 0 | false | false |
| 19 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br>ptdims=['r.date_day','r.placement','r.account_id','a.account_name','li.campaign_id','c.campaign_name','pt.line_item_id','li.line_item_name','r.promoted_tweet_id','pt.tweet_id</code> | 4754 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_twitter_ads__line_item_keywords_report.sql'<br>s=open(p).read().replace('    placement,\n    clicks,', '    placement,\n    clicks,')<br># add keyword_id projection next t</code> | 4229 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/intermediate').glob('*_report_base.sql'):<br> s=p.read_text().replace('select date_day, ', 'select cast(date_day as date) as date_day, ')<br> p.wr</code> | 2974 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
put(M,'twitter_ads__promoted_tweet_report',f"""select
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-026.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/marts/twitter_ads__promoted_tweet_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/marts/twitter_ads__promoted_tweet_report.sql`
- S6: `records/006_contract_impl-026.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/result.md`
- S10: `data/024_packages_work/024_impl-026_twitter_ads__promoted_tweet_report/024_impl-026_twitter_ads__promoted_tweet_report.json`
- S11: `data/005_cs_work/impl-026_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/twitter.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions`
