# impl-024 | marts | tiktok_ads__ad_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1178–1305

```yaml
    - name: tiktok_ads__ad_report
      description: Daily ad performance aggregated from hourly with latest ad/ad group/campaign/advertiser attributes (no URL breakdown)
      grain: One row per source_relation, date_day, ad_id
      source_models:
      - intermediate.int_tiktok_ads__ad_report_hourly (stat_time_hour, source_relation, ad_id, impressions, clicks, spend, reach, conversion, likes, comments, shares, profile_visits, follows, video_watched_2_s, video_watched_6_s, video_views_p_25, video_views_p_50, video_views_p_75, real_time_conversion, total_purchase_value, total_sales_lead_value)
      - intermediate.int_tiktok_ads__ad_history_latest (ad_id, ad_name, ad_group_id, advertiser_id, campaign_id, source_relation)
      - intermediate.int_tiktok_ads__ad_group_history_latest (ad_group_id, ad_group_name, advertiser_id, interest_category, gender, audience_type, budget, source_relation)
      - intermediate.int_tiktok_ads__advertiser (advertiser_id, advertiser_name, currency)
      - intermediate.int_tiktok_ads__campaign_history_latest (campaign_id, campaign_name, source_relation)
      business_logic: '- Start from hourly facts; derive date_day by converting the hourly timestamp to its calendar date. - Join latest dimensions: - ads on matching ad_id - ad_groups on matching ad_group_id and source_relation - advertiser on matching advertiser_id - campaigns on matching campaign_id and source_relation - Group by source_relation, date_day, advertiser_id, advertiser_name, campaign_id, campaign_name, ad_group_id, ad_group_name, ad_id, ad_name, currency, interest_category, gender, audience_type, budget. - For each group, aggregate all hourly metrics by summing; sums ignore NULL inputs and return NULL if all inputs are NULL; no additional casting or rounding. - Compute rate metrics from the aggregated sums with zero-safe division: - daily_cpc: total spend divided by total clicks - daily_cpm: total spend divided by total impressions, scaled per 1,000 impressions - daily_ctr: total clicks divided by total impressions, expressed as a percentage If a denominator is zero or NULL, the result is NULL; no rounding is applied. - total_conversion_value is the daily sum of each hour’s (purchase value + sales lead value), equivalent to summing both components separately. - Dimension attributes come from the latest snapshots; if a joined record is missing, the attribute is NULL. All such attributes are included in the GROUP BY.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Identifier of the data source; grouping key
        tests:
        - not_null
      - name: date_day
        data_type: DATE
        description: Calendar date derived from stat_time_hour
        tests:
        - not_null
      - name: advertiser_id
        data_type: VARCHAR
        description: Advertiser ID from the latest ad group record; NULL if ad group is missing
      - name: advertiser_name
        data_type: VARCHAR
        description: Advertiser name from the latest advertiser record; NULL if advertiser is missing
      - name: campaign_id
        data_type: VARCHAR
        description: Campaign ID from the latest campaign record joined on source_relation; NULL if missing
      - name: campaign_name
        data_type: VARCHAR
        description: Campaign name from the latest campaign record; NULL if missing
      - name: ad_group_id
        data_type: VARCHAR
        description: Ad group ID from the latest ad group record joined on source_relation; NULL if missing
      - name: ad_group_name
        data_type: VARCHAR
        description: Ad group name from the latest ad group record; NULL if missing
      - name: ad_id
        data_type: VARCHAR
        description: Ad ID from hourly facts; grouping key
        tests:
        - not_null
      - name: ad_name
        data_type: VARCHAR
        description: Ad name from the latest ad record; NULL if missing
      - name: currency
        data_type: VARCHAR
        description: Advertiser currency code used for spend-derived metrics
      - name: interest_category
        data_type: VARCHAR
        description: Interest category from the latest ad group record
      - name: gender
        data_type: VARCHAR
        description: Target gender from the latest ad group record
      - name: audience_type
        data_type: VARCHAR
        description: Audience type from the latest ad group record
      - name: budget
        data_type: DOUBLE
        description: Ad group budget from the latest snapshot; included in grouping without aggregation
      - name: impressions
        data_type: HUGEINT
        description: Daily sum of hourly impressions
      - name: clicks
        data_type: HUGEINT
        description: Daily sum of hourly clicks
      - name: spend
        data_type: DOUBLE
        description: Daily sum of hourly spend in advertiser currency
      - name: reach
        data_type: HUGEINT
        description: Daily sum of hourly reach
      - name: conversion
        data_type: HUGEINT
        description: Daily sum of hourly conversions
      - name: likes
        data_type: HUGEINT
        description: Daily sum of hourly likes
      - name: comments
        data_type: HUGEINT
        description: Daily sum of hourly comments
      - name: shares
        data_type: HUGEINT
        description: Daily sum of hourly shares
      - name: profile_visits
        data_type: HUGEINT
        description: Daily sum of hourly profile visits
      - name: follows
        data_type: HUGEINT
        description: Daily sum of hourly follows
      - name: video_watched_2_s
        data_type: HUGEINT
        description: Daily sum of hourly 2-second video plays
      - name: video_watched_6_s
        data_type: HUGEINT
        description: Daily sum of hourly 6-second video plays
      - name: video_views_p_25
        data_type: HUGEINT
        description: Daily sum of hourly 25% video views
      - name: video_views_p_50
        data_type: HUGEINT
        description: Daily sum of hourly 50% video views
      - name: video_views_p_75
        data_type: HUGEINT
        description: Daily sum of hourly 75% video views
      - name: real_time_conversion
        data_type: HUGEINT
        description: Daily sum of hourly real-time conversions
      - name: total_purchase_value
        data_type: DOUBLE
        description: Daily sum of hourly purchase value
      - name: total_sales_lead_value
        data_type: DOUBLE
        description: Daily sum of hourly sales lead value
      - name: total_conversion_value
        data_type: DOUBLE
        description: Daily sum of each hour’s purchase value plus sales lead value
      - name: daily_cpc
        data_type: DOUBLE
        description: Total spend divided by total clicks; NULL if clicks are zero or NULL; no rounding
      - name: daily_cpm
        data_type: DOUBLE
        description: Total spend per 1,000 impressions; NULL if impressions are zero or NULL; no rounding
      - name: daily_ctr
        data_type: DOUBLE
        description: Click-through rate as clicks divided by impressions times 100; NULL if impressions are zero or NULL; no rounding
```

## agent 最终 SQL

S4

```sql
with joined_data as (
    select
        h.source_relation,
        cast(h.stat_time_hour as date) as date_day,
        ag.advertiser_id,
        a.advertiser_name,
        ad.campaign_id,
        c.campaign_name,
        ad.ad_group_id,
        ag.ad_group_name,
        h.ad_id,
        ad.ad_name,
        a.currency,
        ag.interest_category,
        ag.gender,
        ag.audience_type,
        ag.budget,
                h.impressions,
                h.clicks,
                h.spend,
                h.reach,
                h.conversion,
                h.likes,
                h.comments,
                h.shares,
                h.profile_visits,
                h.follows,
                h.video_watched_2_s,
                h.video_watched_6_s,
                h.video_views_p_25,
                h.video_views_p_50,
                h.video_views_p_75,
                h.real_time_conversion,
                h.total_purchase_value,
                h.total_sales_lead_value,
                (h.total_purchase_value + h.total_sales_lead_value) as total_conversion_value_row
    from intermediate.int_tiktok_ads__ad_report_hourly as h
    left join intermediate.int_tiktok_ads__ad_history_latest as ad on h.ad_id = ad.ad_id and h.source_relation = ad.source_relation left join intermediate.int_tiktok_ads__ad_group_history_latest as ag on ad.ad_group_id = ag.ad_group_id and ad.source_relation = ag.source_relation left join intermediate.int_tiktok_ads__advertiser as a on ag.advertiser_id = a.advertiser_id left join intermediate.int_tiktok_ads__campaign_history_latest as c on ad.campaign_id = c.campaign_id and ad.source_relation = c.source_relation
    
), aggregated as (
    select
        source_relation,
        date_day,
        advertiser_id,
        advertiser_name,
        campaign_id,
        campaign_name,
        ad_group_id,
        ad_group_name,
        ad_id,
        ad_name,
        currency,
        interest_category,
        gender,
        audience_type,
        budget,
        sum(impressions) as impressions,
        sum(clicks) as clicks,
        sum(spend) as spend,
        sum(reach) as reach,
        sum(conversion) as conversion,
        sum(likes) as likes,
        sum(comments) as comments,
        sum(shares) as shares,
        sum(profile_visits) as profile_visits,
        sum(follows) as follows,
        sum(video_watched_2_s) as video_watched_2_s,
        sum(video_watched_6_s) as video_watched_6_s,
        sum(video_views_p_25) as video_views_p_25,
        sum(video_views_p_50) as video_views_p_50,
        sum(video_views_p_75) as video_views_p_75,
        sum(real_time_conversion) as real_time_conversion,
        sum(total_purchase_value) as total_purchase_value,
        sum(total_sales_lead_value) as total_sales_lead_value,
        sum(total_conversion_value_row) as total_conversion_value
    from joined_data
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
)
select
    *,
    spend / nullif(clicks, 0) as daily_cpc,
    spend / nullif(impressions, 0) * 1000 as daily_cpm,
    clicks / nullif(impressions, 0) * 100 as daily_ctr
from aggregated
```

## gold SQL（仅供定位差异）

S5

```sql
with hourly as (
  select * from intermediate.int_tiktok_ads__ad_report_hourly
), ads as (
  select * from intermediate.int_tiktok_ads__ad_history_latest
), ad_groups as (
  select * from intermediate.int_tiktok_ads__ad_group_history_latest
), advertiser as (
  select * from intermediate.int_tiktok_ads__advertiser
), campaigns as (
  select * from intermediate.int_tiktok_ads__campaign_history_latest
), aggregated as (
  select
    hourly.source_relation,
    cast(hourly.stat_time_hour as date) as date_day,
    ad_groups.advertiser_id,
    advertiser.advertiser_name,
    campaigns.campaign_id,
    campaigns.campaign_name,
    ad_groups.ad_group_id,
    ad_groups.ad_group_name,
    hourly.ad_id,
    ads.ad_name,
    advertiser.currency,
    ad_groups.interest_category,
    ad_groups.gender,
    ad_groups.audience_type,
    ad_groups.budget,
    sum(hourly.impressions) as impressions,
    sum(hourly.clicks) as clicks,
    sum(hourly.spend) as spend,
    sum(hourly.reach) as reach,
    sum(hourly.conversion) as conversion,
    sum(hourly.likes) as likes,
    sum(hourly.comments) as comments,
    sum(hourly.shares) as shares,
    sum(hourly.profile_visits) as profile_visits,
    sum(hourly.follows) as follows,
    sum(hourly.video_watched_2_s) as video_watched_2_s,
    sum(hourly.video_watched_6_s) as video_watched_6_s,
    sum(hourly.video_views_p_25) as video_views_p_25,
    sum(hourly.video_views_p_50) as video_views_p_50,
    sum(hourly.video_views_p_75) as video_views_p_75,
    sum(hourly.real_time_conversion) as real_time_conversion,
    sum(hourly.total_purchase_value) as total_purchase_value,
    sum(hourly.total_sales_lead_value) as total_sales_lead_value,
    sum(hourly.total_purchase_value + hourly.total_sales_lead_value) as total_conversion_value,
    sum(hourly.spend)/nullif(sum(hourly.clicks),0) as daily_cpc,
    (sum(hourly.spend)/nullif(sum(hourly.impressions),0))*1000 as daily_cpm,
    (sum(hourly.clicks)/nullif(sum(hourly.impressions),0))*100 as daily_ctr
  from hourly
  left join ads
    on hourly.ad_id = ads.ad_id
      left join ad_groups
    on ads.ad_group_id = ad_groups.ad_group_id
    and ads.source_relation = ad_groups.source_relation
  left join advertiser
    on ads.advertiser_id = advertiser.advertiser_id
      left join campaigns
    on ads.campaign_id = campaigns.campaign_id
    and ads.source_relation = campaigns.source_relation
  group by
    hourly.source_relation,
    cast(hourly.stat_time_hour as date),
    ad_groups.advertiser_id,
    advertiser.advertiser_name,
    campaigns.campaign_id,
    campaigns.campaign_name,
    ad_groups.ad_group_id,
    ad_groups.ad_group_name,
    hourly.ad_id,
    ads.ad_name,
    advertiser.currency,
    ad_groups.interest_category,
    ad_groups.gender,
    ad_groups.audience_type,
    ad_groups.budget
)
select * from aggregated
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2499 | 2499 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"ad_id":"10"}</code> |
| K2 | <code>{"ad_id":"100"}</code> |
| K3 | <code>{"ad_id":"1000"}</code> |
| K4 | <code>{"ad_id":"1"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| advertiser_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| advertiser_name | 2486 | 2486 | 2486 | VARCHAR | VARCHAR |
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ad_group_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ad_group_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ad_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ad_name | 2499 | 2499 | 2499 | VARCHAR | VARCHAR |
| currency | 2499 | 2499 | 2499 | VARCHAR | VARCHAR |
| interest_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| gender | 0 | 0 | 0 | VARCHAR | VARCHAR |
| audience_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| budget | 0 | 0 | 0 | DOUBLE | DOUBLE |
| impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| clicks | 0 | 0 | 0 | HUGEINT | HUGEINT |
| spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| reach | 0 | 0 | 0 | HUGEINT | HUGEINT |
| conversion | 0 | 0 | 0 | HUGEINT | HUGEINT |
| likes | 0 | 0 | 0 | HUGEINT | HUGEINT |
| comments | 0 | 0 | 0 | HUGEINT | HUGEINT |
| shares | 0 | 0 | 0 | HUGEINT | HUGEINT |
| profile_visits | 0 | 0 | 0 | HUGEINT | HUGEINT |
| follows | 0 | 0 | 0 | HUGEINT | HUGEINT |
| video_watched_2_s | 0 | 0 | 0 | HUGEINT | HUGEINT |
| video_watched_6_s | 0 | 0 | 0 | HUGEINT | HUGEINT |
| video_views_p_25 | 0 | 0 | 0 | HUGEINT | HUGEINT |
| video_views_p_50 | 0 | 0 | 0 | HUGEINT | HUGEINT |
| video_views_p_75 | 0 | 0 | 0 | HUGEINT | HUGEINT |
| real_time_conversion | 0 | 0 | 0 | HUGEINT | HUGEINT |
| total_purchase_value | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_sales_lead_value | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_conversion_value | 0 | 0 | 0 | DOUBLE | DOUBLE |
| daily_cpc | 0 | 0 | 0 | DOUBLE | DOUBLE |
| daily_cpm | 0 | 0 | 0 | DOUBLE | DOUBLE |
| daily_ctr | 0 | 0 | 0 | DOUBLE | DOUBLE |

advertiser_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | Advertiser 10 CA |
| K2 | null | Advertiser 100 AU |
| K3 | null | Advertiser 200 SG |

ad_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | null | ad name one |
| K1 | null | ad name 10 |
| K2 | null | ad name 100 |

currency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | null | USD |
| K1 | null | CAN |
| K2 | null | AUD |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>8列；[{"column":"source_relation","value":"tiktok_ads"},{"column":"interest_category","value":"[ 124938917 ]"},{"column":"gender","value":"GENDER_UNLIMITED"}]</code> |
| A4_equal_columns | <code>5组；[{"columns":["campaign_id","ad_group_id","ad_id"],"nonnull_equal_rows":2499,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["conversion","real_time_conversion"],"nonnull_equal_rows":2499,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["comments","shares","profile_visits","follows"],"nonnull_equal_rows":2499,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>5组；[{"columns":["campaign_id","ad_group_id","ad_id"],"nonnull_equal_rows":2499,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["conversion","real_time_conversion"],"nonnull_equal_rows":2499,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["comments","shares","profile_visits","follows"],"nonnull_equal_rows":2499,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B7_specified_not_read | <code>["intermediate.int_tiktok_ads__ad_group_history_latest (ad_group_id, ad_group_name, advertiser_id, interest_category, gender, audience_type, budget, source_relation)","intermediate.int_tiktok_ads__ad_history_latest (ad_id, ad_name, ad_group_id, advertiser_id, campaign_id, source_relation)","intermediate.int_tiktok_ads__ad_report_hourly (stat_time_hour, source_relation, ad_id, impressions, clicks, spend, reach, conversion, likes, comments, shares, profile_visits, follows, video_watched_2_s, video_watched_6_s, video_views_p_25, video_views_p_50, video_views_p_75, real_time_conversion, total_purchase_value, total_sales_lead_value)"]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory mart null required tiktok_ads__ad_report (0, 0, 0)</code> |

## 轨迹索引（不放输出原文）

本题事件总数：65；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find sql -maxdepth 3 -type f -print &#124; sort &amp;&amp; echo '--- config ---' &amp;&amp; cat config/layer_dependencies.yaml</code> | 3033 | true | false |
| 33 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>import yaml<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))['modeling_spec']<br>for m in contract['intermediate_models']:<br> src=m['source_mode</code> | 0 | false | false |
| 35 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; echo EXIT:$?; tail -80 /tmp/runlog</code> | 6115 | true | false |
| 37 | run | <code>cat &gt; /tmp/fixcampaign.py &lt;&lt;'PY'<br>from pathlib import Path<br>fields=[('source_relation',"'tiktok_ads'"),('campaign_id','CAMPAIGN_ID'),('updated_at','try_cast(nullif(trim(UPDATED_AT), \'\') as TIMESTAMP)'</code> | 3378 | true | false |
| 43 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('tiktok_ads.duckdb',read_only=True)<br>for schema,t in [('staging','stg_tiktok_ads__advertiser'),('staging','stg_tiktok_ads__campaign_history'),('staging','</code> | 457 | true | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>from pathlib import Path<br>c=duckdb.connect('tiktok_ads.duckdb',read_only=True)<br>for layer, pref in [('staging','stg_'),('intermediate','int_'),('marts','tiktok_ads__')]:<br> p</code> | 1078 | true | false |

### agent action 的 thought/message 命中原句

event 33 / message

```text
agg_model('tiktok_ads__ad_report',from_sql,joins,dims,groups,metric_select)
```
event 43 / message

```text
for schema,t in [('staging','stg_tiktok_ads__advertiser'),('staging','stg_tiktok_ads__campaign_history'),('staging','stg_tiktok_ads__ad_group_history'),('staging','stg_tiktok_ads__ad_history'),('marts','tiktok_ads__ad_report'),('marts','tiktok_ads__campaign_country_report')]:
```
event 43 / message

```text
for t in ['tiktok_ads__ad_report','tiktok_ads__campaign_country_report']:
```
event 49 / message

```text
print('ad daily keys duplicate rows:',c.execute('''select count(*) from (select source_relation,date_day,ad_id,count(*) n from marts.tiktok_ads__ad_report group by all having n>1)''').fetchone()[0])
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-024.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/marts/tiktok_ads__ad_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/sql/marts/tiktok_ads__ad_report.sql`
- S6: `records/006_contract_impl-024.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/result.md`
- S10: `data/024_packages_work/024_impl-024_tiktok_ads__ad_report/024_impl-024_tiktok_ads__ad_report.json`
- S11: `data/005_cs_work/impl-024_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions`
