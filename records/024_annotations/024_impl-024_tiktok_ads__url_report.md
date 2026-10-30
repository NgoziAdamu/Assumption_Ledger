# impl-024 · tiktok_ads__url_report

用途：**全量**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**C**；把握：中。

CS各上游source_relation是不同raw表名。agent额外要求相等，使ads/维度连接失配；多处连接和投影叠加，单改均未减少规模，组合诊断L0全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-024_tiktok_ads__url_report.md](../024_packages/024_impl-024_tiktok_ads__url_report.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`。

```text
1624:     - name: tiktok_ads__url_report
1625:       description: Daily ad performance with URL breakdown; includes only ads whose landing_page_url is non-null
1626:       grain: One row per unique combination of date_day, source_relation, ad_id, ad_group_id, campaign_id, and grouped context fields (advertiser_id/name, campaign_name, ad_group_name, ad_name, currency, interest_category, gender, audience_type, budget, base_url, url_host, url_path, utm_source/medium/campaign/content/term)
1627:       source_models:
1628:       - intermediate.int_tiktok_ads__ad_report_hourly
1629:       - intermediate.int_tiktok_ads__ad_history_latest
1630:       - intermediate.int_tiktok_ads__ad_group_history_latest
1631:       - intermediate.int_tiktok_ads__advertiser
1632:       - intermediate.int_tiktok_ads__campaign_history_latest
1633:       business_logic: '1) Start from intermediate.int_tiktok_ads__ad_report_hourly (hourly). 2) Left join latest dimension snapshots: - hourly.ad_id → intermediate.int_tiktok_ads__ad_history_latest (ads) - ads.ad_group_id → intermediate.int_tiktok_ads__ad_group_history_latest (ad_groups) - ads.advertiser_id → intermediate.int_tiktok_ads__advertiser (advertiser) - ads.campaign_id → intermediate.int_tiktok_ads__campaign_history_latest (campaigns) 3) Keep only rows where ads.landing_page_url is present (non-null). 4) Derive date_day by casting hourly.stat_time_hour to a date (no timezone adjustments). 5) Group by all selected dimensions: source_relation, date_day, advertiser_id/name, campaign_id/name, ad_group_id/name, ad_id, ad_name, base_url, url_host, url_path, utm_source/medium/campaign/content/term, currency, interest_category, gender, audience_type, budget. 6) For each group, add up all hourly numeric metrics; null inputs are ignored in the addition, and if all inputs are null the result is null. For total_conversion_value, first compute purchase value plus sales lead value per row, then add those row results across the group; if either component is missing on a row, that row contributes nothing. 7) Compute rate metrics from the aggregated totals: - daily_cpc: total spend divided by total clicks; if total clicks is zero or null, return null; no rounding. - daily_cpm: total spend divided by total impressions, multiplied by 1000; if total impressions is zero or null, return null; no rounding. - daily_ctr: total clicks divided by total impressions, multiplied by 100; if total impressions is zero or null, return null; no rounding. 8) URL and UTM fields are taken directly from ads without parsing, normalization, trimming, or case changes. 9) Context fields (currency, interest_category, gender, audience_type, budget) are grouping keys; differences create separate rows.'
1634:       columns:
1635:       - name: source_relation
1636:         data_type: VARCHAR
1637:         description: Source relation identifier from hourly input; included in the grouping key
1638:       - name: date_day
1639:         data_type: DATE
1640:         description: Date derived by casting stat_time_hour to date; part of the grouping key
1641:       - name: advertiser_id
1642:         data_type: VARCHAR
1643:         description: Advertiser ID from ad_groups; may be NULL if ad_group not found; part of the grouping key
1644:       - name: advertiser_name
1645:         data_type: VARCHAR
1646:         description: Advertiser name from advertiser; may be NULL if advertiser not found; part of the grouping key
1647:       - name: campaign_id
1648:         data_type: VARCHAR
1649:         description: Campaign ID from campaigns; may be NULL if campaign not found; part of the grouping key
1650:       - name: campaign_name
1651:         data_type: VARCHAR
1652:         description: Campaign name from campaigns; may be NULL if campaign not found; part of the grouping key
1653:       - name: ad_group_id
1654:         data_type: VARCHAR
1655:         description: Ad group ID from ad_groups; may be NULL if ad_group not found; part of the grouping key
1656:       - name: ad_group_name
1657:         data_type: VARCHAR
1658:         description: Ad group name from ad_groups; may be NULL if ad_group not found; part of the grouping key
1659:       - name: ad_id
1660:         data_type: VARCHAR
1661:         description: Ad ID from hourly; part of the grouping key
1662:       - name: ad_name
1663:         data_type: VARCHAR
1664:         description: Ad name from ads; part of the grouping key
1665:       - name: base_url
1666:         data_type: VARCHAR
1667:         description: Landing page base URL from ads; taken as stored; part of the grouping key
1668:       - name: url_host
1669:         data_type: VARCHAR
1670:         description: URL host from ads; taken as stored; part of the grouping key
1671:       - name: url_path
1672:         data_type: VARCHAR
1673:         description: URL path from ads; taken as stored; part of the grouping key
1674:       - name: utm_source
1675:         data_type: VARCHAR
1676:         description: UTM source from ads; taken as stored; part of the grouping key
1677:       - name: utm_medium
1678:         data_type: VARCHAR
1679:         description: UTM medium from ads; taken as stored; part of the grouping key
1680:       - name: utm_campaign
1681:         data_type: VARCHAR
1682:         description: UTM campaign from ads; taken as stored; part of the grouping key
1683:       - name: utm_content
1684:         data_type: VARCHAR
1685:         description: UTM content from ads; taken as stored; part of the grouping key
1686:       - name: utm_term
1687:         data_type: VARCHAR
1688:         description: UTM term from ads; taken as stored; part of the grouping key
1689:       - name: currency
1690:         data_type: VARCHAR
1691:         description: Advertiser currency code from advertiser; may be NULL if advertiser not found; part of the grouping key
1692:       - name: interest_category
1693:         data_type: VARCHAR
1694:         description: Interest category from ad_groups; may be NULL if ad_group not found; part of the grouping key
1695:       - name: gender
1696:         data_type: VARCHAR
1697:         description: Target gender from ad_groups; may be NULL if ad_group not found; part of the grouping key
1698:       - name: audience_type
1699:         data_type: VARCHAR
1700:         description: Audience type from ad_groups; may be NULL if ad_group not found; part of the grouping key
1701:       - name: budget
1702:         data_type: DOUBLE
1703:         description: Ad group budget from ad_groups; may be NULL if ad_group not found; part of the grouping key; not aggregated
1704:       - name: impressions
1705:         data_type: HUGEINT
1706:         description: Total impressions per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1707:       - name: clicks
1708:         data_type: HUGEINT
1709:         description: Total clicks per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1710:       - name: spend
1711:         data_type: DOUBLE
1712:         description: Total spend per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1713:       - name: reach
1714:         data_type: HUGEINT
1715:         description: Total reach per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1716:       - name: conversion
1717:         data_type: HUGEINT
1718:         description: Total conversions per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1719:       - name: likes
1720:         data_type: HUGEINT
1721:         description: Total likes per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1722:       - name: comments
1723:         data_type: HUGEINT
1724:         description: Total comments per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1725:       - name: shares
1726:         data_type: HUGEINT
1727:         description: Total shares per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1728:       - name: profile_visits
1729:         data_type: HUGEINT
1730:         description: Total profile visits per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1731:       - name: follows
1732:         data_type: HUGEINT
1733:         description: Total follows per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1734:       - name: video_watched_2_s
1735:         data_type: HUGEINT
1736:         description: Total 2s video views per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1737:       - name: video_watched_6_s
1738:         data_type: HUGEINT
1739:         description: Total 6s video views per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1740:       - name: video_views_p_25
1741:         data_type: HUGEINT
1742:         description: Total 25% video views per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1743:       - name: video_views_p_50
1744:         data_type: HUGEINT
1745:         description: Total 50% video views per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1746:       - name: video_views_p_75
1747:         data_type: HUGEINT
1748:         description: Total 75% video views per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1749:       - name: real_time_conversion
1750:         data_type: HUGEINT
1751:         description: Total real-time conversions per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1752:       - name: total_purchase_value
1753:         data_type: DOUBLE
1754:         description: Total purchase value per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1755:       - name: total_sales_lead_value
1756:         data_type: DOUBLE
1757:         description: Total sales lead value per group by adding hourly values; NULLs ignored; NULL if all inputs are NULL
1758:       - name: total_conversion_value
1759:         data_type: DOUBLE
1760:         description: Group total of per-row purchase value plus sales lead value; rows missing either component contribute nothing; NULL if all row-level sums are NULL
1761:       - name: daily_cpc
1762:         data_type: DOUBLE
1763:         description: Average cost per click computed as total spend divided by total clicks; NULL if clicks are zero or NULL; no rounding
1764:       - name: daily_cpm
1765:         data_type: DOUBLE
1766:         description: Cost per mille computed as total spend divided by total impressions then multiplied by 1000; NULL if impressions are zero or NULL; no rounding
1767:       - name: daily_ctr
1768:         data_type: DOUBLE
1769:         description: Click-through rate percentage computed as total clicks divided by total impressions then multiplied by 100; NULL if impressions are zero or NULL; no rounding
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/marts/tiktok_ads__url_report.sql`；SHA-256 `1ae195a199266db987ee17f17ad318928fce59750677cc1100e89961a9eef88d`。

```text
1: with joined_data as (
2:     select
3:         h.source_relation,
4:         cast(h.stat_time_hour as date) as date_day,
5:         ag.advertiser_id,
6:         a.advertiser_name,
7:         c.campaign_id,
8:         c.campaign_name,
9:         ag.ad_group_id,
10:         ag.ad_group_name,
11:         h.ad_id,
12:         ad.ad_name,
13:         ad.base_url,
14:         ad.url_host,
15:         ad.url_path,
16:         ad.utm_source,
17:         ad.utm_medium,
18:         ad.utm_campaign,
19:         ad.utm_content,
20:         ad.utm_term,
21:         a.currency,
22:         ag.interest_category,
23:         ag.gender,
24:         ag.audience_type,
25:         ag.budget,
26:                 h.impressions,
27:                 h.clicks,
28:                 h.spend,
29:                 h.reach,
30:                 h.conversion,
31:                 h.likes,
32:                 h.comments,
33:                 h.shares,
34:                 h.profile_visits,
35:                 h.follows,
36:                 h.video_watched_2_s,
37:                 h.video_watched_6_s,
38:                 h.video_views_p_25,
39:                 h.video_views_p_50,
40:                 h.video_views_p_75,
41:                 h.real_time_conversion,
42:                 h.total_purchase_value,
43:                 h.total_sales_lead_value,
44:                 (h.total_purchase_value + h.total_sales_lead_value) as total_conversion_value_row
45:     from intermediate.int_tiktok_ads__ad_report_hourly as h
46:     left join intermediate.int_tiktok_ads__ad_history_latest as ad on h.ad_id = ad.ad_id and h.source_relation = ad.source_relation left join intermediate.int_tiktok_ads__ad_group_history_latest as ag on ad.ad_group_id = ag.ad_group_id and ad.source_relation = ag.source_relation left join intermediate.int_tiktok_ads__advertiser as a on ad.advertiser_id = a.advertiser_id left join intermediate.int_tiktok_ads__campaign_history_latest as c on ad.campaign_id = c.campaign_id and ad.source_relation = c.source_relation
47:     where ad.landing_page_url is not null
48: ), aggregated as (
49:     select
50:         source_relation,
51:         date_day,
52:         advertiser_id,
53:         advertiser_name,
54:         campaign_id,
55:         campaign_name,
56:         ad_group_id,
57:         ad_group_name,
58:         ad_id,
59:         ad_name,
60:         base_url,
61:         url_host,
62:         url_path,
63:         utm_source,
64:         utm_medium,
65:         utm_campaign,
66:         utm_content,
67:         utm_term,
68:         currency,
69:         interest_category,
70:         gender,
71:         audience_type,
72:         budget,
73:         sum(impressions) as impressions,
74:         sum(clicks) as clicks,
75:         sum(spend) as spend,
76:         sum(reach) as reach,
77:         sum(conversion) as conversion,
78:         sum(likes) as likes,
79:         sum(comments) as comments,
80:         sum(shares) as shares,
81:         sum(profile_visits) as profile_visits,
82:         sum(follows) as follows,
83:         sum(video_watched_2_s) as video_watched_2_s,
84:         sum(video_watched_6_s) as video_watched_6_s,
85:         sum(video_views_p_25) as video_views_p_25,
86:         sum(video_views_p_50) as video_views_p_50,
87:         sum(video_views_p_75) as video_views_p_75,
88:         sum(real_time_conversion) as real_time_conversion,
89:         sum(total_purchase_value) as total_purchase_value,
90:         sum(total_sales_lead_value) as total_sales_lead_value,
91:         sum(total_conversion_value_row) as total_conversion_value
92:     from joined_data
93:     group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23
94: )
95: select
96:     *,
97:     spend / nullif(clicks, 0) as daily_cpc,
98:     spend / nullif(impressions, 0) * 1000 as daily_cpm,
99:     clicks / nullif(impressions, 0) * 100 as daily_ctr
100: from aggregated
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/sql/marts/tiktok_ads__url_report.sql`；SHA-256 `26be67eb8ff2c645d4c83d5a53d0c13441a4f65a34778eb0a34a17a5beb1e8fd`。

```text
1: with hourly as (
2:   select * from intermediate.int_tiktok_ads__ad_report_hourly
3: ), ads as (
4:   select * from intermediate.int_tiktok_ads__ad_history_latest
5: ), ad_groups as (
6:   select * from intermediate.int_tiktok_ads__ad_group_history_latest
7: ), advertiser as (
8:   select * from intermediate.int_tiktok_ads__advertiser
9: ), campaigns as (
10:   select * from intermediate.int_tiktok_ads__campaign_history_latest
11: ), aggregated as (
12:   select
13:     hourly.source_relation,
14:     cast(hourly.stat_time_hour as date) as date_day,
15:     ad_groups.advertiser_id,
16:     advertiser.advertiser_name,
17:     campaigns.campaign_id,
18:     campaigns.campaign_name,
19:     ad_groups.ad_group_id,
20:     ad_groups.ad_group_name,
21:     hourly.ad_id,
22:     ads.ad_name,
23:     ads.base_url,
24:     ads.url_host,
25:     ads.url_path,
26:     ads.utm_source,
27:     ads.utm_medium,
28:     ads.utm_campaign,
29:     ads.utm_content,
30:     ads.utm_term,
31:     advertiser.currency,
32:     ad_groups.interest_category,
33:     ad_groups.gender,
34:     ad_groups.audience_type,
35:     ad_groups.budget,
36:     sum(hourly.impressions) as impressions,
37:     sum(hourly.clicks) as clicks,
38:     sum(hourly.spend) as spend,
39:     sum(hourly.reach) as reach,
40:     sum(hourly.conversion) as conversion,
41:     sum(hourly.likes) as likes,
42:     sum(hourly.comments) as comments,
43:     sum(hourly.shares) as shares,
44:     sum(hourly.profile_visits) as profile_visits,
45:     sum(hourly.follows) as follows,
46:     sum(hourly.video_watched_2_s) as video_watched_2_s,
47:     sum(hourly.video_watched_6_s) as video_watched_6_s,
48:     sum(hourly.video_views_p_25) as video_views_p_25,
49:     sum(hourly.video_views_p_50) as video_views_p_50,
50:     sum(hourly.video_views_p_75) as video_views_p_75,
51:     sum(hourly.real_time_conversion) as real_time_conversion,
52:     sum(hourly.total_purchase_value) as total_purchase_value,
53:     sum(hourly.total_sales_lead_value) as total_sales_lead_value,
54:     sum(hourly.total_purchase_value + hourly.total_sales_lead_value) as total_conversion_value,
55:     sum(hourly.spend)/nullif(sum(hourly.clicks),0) as daily_cpc,
56:     (sum(hourly.spend)/nullif(sum(hourly.impressions),0))*1000 as daily_cpm,
57:     (sum(hourly.clicks)/nullif(sum(hourly.impressions),0))*100 as daily_ctr
58:   from hourly
59:   left join ads
60:     on hourly.ad_id = ads.ad_id
61:       left join ad_groups
62:     on ads.ad_group_id = ad_groups.ad_group_id
63:       left join advertiser
64:     on ads.advertiser_id = advertiser.advertiser_id
65:       left join campaigns
66:     on ads.campaign_id = campaigns.campaign_id
67:       where ads.landing_page_url is not null
68:   group by
69:     hourly.source_relation,
70:     cast(hourly.stat_time_hour as date),
71:     ad_groups.advertiser_id,
72:     advertiser.advertiser_name,
73:     campaigns.campaign_id,
74:     campaigns.campaign_name,
75:     ad_groups.ad_group_id,
76:     ad_groups.ad_group_name,
77:     hourly.ad_id,
78:     ads.ad_name,
79:     ads.base_url,
80:     ads.url_host,
81:     ads.url_path,
82:     ads.utm_source,
83:     ads.utm_medium,
84:     ads.utm_campaign,
85:     ads.utm_content,
86:     ads.utm_term,
87:     advertiser.currency,
88:     ad_groups.interest_category,
89:     ad_groups.gender,
90:     ad_groups.audience_type,
91:     ad_groups.budget
92: )
93: select * from aggregated
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- 本表主要差异（C）：**看到了但没提**；事件 33、41、42。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 33：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/33.json`；命令首行：`cat > /tmp/models.py <<'PY'`。
event 41：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/41.json`；命令首行：`python - <<'PY'`。
event 42：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/42.json`；原始观察输出。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

已按 staging → intermediate → marts 顺序实现 SQL，文件均位于要求的 `sql/<layer>/<model_name>.sql` 路径下，共 22 个模型文件。

### 实施内容
- **Staging（8 张表）**：按契约投影字段并进行安全类型转换；数值指标按约定缺失时默认 0；清理 advertiser 邮箱、名称及手机号；生成 URL/UTM 字段；通过 `updated_at` 为历史数据标记最新记录。
- **Intermediate（8 个模型）**：按契约实现字段直通和最新记录筛选，来源仅引用 staging。
- **Marts（6 个模型）**：实现小时指标按日汇总、维度左连接、conversion value 汇总及零安全的 CPC/CPM/CTR 计算。来源仅引用 intermediate。

### 验证结果
- 执行 `python run.py` 成功，最终日志显示 staging `8/8`、intermediate `8/8`、marts `6/6` 模型创建成功。
- 各模型行数与源记录规模相符；ad report、campaign-country report 的分组主键未检测到重复。
- 最新 campaign 标记检查无异常；ad report 和 campaign-country report 的契约必填字段无 NULL；advertiser report 核心指标未发现负数。
- 检查确认 SQL 文件无文件末尾分号，也未使用 dbt `ref()`。

### 数据质量处理与残余影响
- 数值与日期采用 DuckDB `try_cast`，不可解析值置 NULL；报表数值列按 staging 合约对转换后的 NULL 默认 0。可选邮箱/名称/手机号字段验证失败时置 NULL，记录仍保留。
- 历史模型按 source relation 和实体 ID 标记最大更新时间；并列最大时间可能保留多行，符合契约保留重复记录的行为。
- 中间层与模型合约要求保留重复和 NULL，因此未做去重；原始重复可能继续影响下游汇总，属于配置明确要求的保留行为。

### 合约歧义及环境说明
- `stg_tiktok_ads__campaign_history.is_new_structure` 声明为 BOOLEAN，而 intermediate 列定义为 VARCHAR；intermediate 同时要求不转换、逐值透传。本实现遵守透传要求，因此输出保留 staging 的 BOOLEAN 类型。
- 运行环境根目录挂载为只读，无法创建 `/workspace/result.md`；完整报告保存在项目目录 `result.md`，内容亦包含于最终提交。
```

## 查询

核实查询 **0** 条；代价档：**需要查业务说明**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 诊断：gold连接字段非空
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
SELECT count(*) n,count(ad_name) ads_n,count(advertiser_name) advertisers_n,count(ad_group_id) groups_n,count(campaign_id) campaigns_n FROM marts.tiktok_ads__url_report
```


```json
{"columns":["n","ads_n","advertisers_n","groups_n","campaigns_n"],"rows":[[2499,2499,2486,2499,2499]]}
```


### 诊断：多处组合仅诊断（不用于单点原因排名）
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
with joined_data as (
    select
        h.source_relation,
        cast(h.stat_time_hour as date) as date_day,
        ag.advertiser_id,
        a.advertiser_name,
        c.campaign_id,
        c.campaign_name,
        ag.ad_group_id,
        ag.ad_group_name,
        h.ad_id,
        ad.ad_name,
        ad.base_url,
        ad.url_host,
        ad.url_path,
        ad.utm_source,
        ad.utm_medium,
        ad.utm_campaign,
        ad.utm_content,
        ad.utm_term,
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
    left join intermediate.int_tiktok_ads__ad_history_latest as ad on h.ad_id = ad.ad_id left join intermediate.int_tiktok_ads__ad_group_history_latest as ag on ad.ad_group_id = ag.ad_group_id left join intermediate.int_tiktok_ads__advertiser as a on ad.advertiser_id = a.advertiser_id left join intermediate.int_tiktok_ads__campaign_history_latest as c on ad.campaign_id = c.campaign_id
    where ad.landing_page_url is not null
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
        base_url,
        url_host,
        url_path,
        utm_source,
        utm_medium,
        utm_campaign,
        utm_content,
        utm_term,
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
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23
)
select
    *,
    spend / nullif(clicks, 0) as daily_cpc,
    spend / nullif(impressions, 0) * 1000 as daily_cpm,
    clicks / nullif(impressions, 0) * 100 as daily_ctr
from aggregated
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2499|2499|0|0|是|
|L1|2499|2499|0|0|是|
|L2|2499|2499|0|0|是|
|L3|2499|2499|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
labels：`["adgroup_source_join","campaign_source_join","ads_source_join"]`

### 诊断：gold各上游source_relation
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
SELECT 'hourly' relation,source_relation,count(*) n FROM intermediate.int_tiktok_ads__ad_report_hourly GROUP BY 2 UNION ALL SELECT 'ads',source_relation,count(*) FROM intermediate.int_tiktok_ads__ad_history_latest GROUP BY 2 UNION ALL SELECT 'ad_groups',source_relation,count(*) FROM intermediate.int_tiktok_ads__ad_group_history_latest GROUP BY 2 UNION ALL SELECT 'campaigns',source_relation,count(*) FROM intermediate.int_tiktok_ads__campaign_history_latest GROUP BY 2
```


```json
{"columns":["relation","source_relation","n"],"rows":[["hourly","raw.tiktok_ad_report_hourly_data",2499],["ads","raw.tiktok_ad_history_data",2509],["ad_groups","raw.tiktok_adgroup_history_data",2504],["campaigns","raw.tiktok_campaign_history_data",2600]]}
```


### 诊断：gold输出连接字段非空
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
SELECT count(*) n,count(ad_name) ads,count(advertiser_name) advertisers,count(ad_group_id) groups,count(campaign_id) campaigns FROM marts.tiktok_ads__url_report
```

查询未完成，错误原文：

```
Parser Error: syntax error at or near "groups"

LINE 1: ...) ads,count(advertiser_name) advertisers,count(ad_group_id) groups,count(campaign_id) campaigns FROM marts.tiktok_ads__...
                                                                       ^
```


### 诊断：gold SQL同gold输入重跑
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`。

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
    ads.base_url,
    ads.url_host,
    ads.url_path,
    ads.utm_source,
    ads.utm_medium,
    ads.utm_campaign,
    ads.utm_content,
    ads.utm_term,
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
      left join advertiser
    on ads.advertiser_id = advertiser.advertiser_id
      left join campaigns
    on ads.campaign_id = campaigns.campaign_id
      where ads.landing_page_url is not null
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
    ads.base_url,
    ads.url_host,
    ads.url_path,
    ads.utm_source,
    ads.utm_medium,
    ads.utm_campaign,
    ads.utm_content,
    ads.utm_term,
    advertiser.currency,
    ad_groups.interest_category,
    ad_groups.gender,
    ad_groups.audience_type,
    ad_groups.budget
)
select * from aggregated
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2499|2499|0|0|是|
|L1|2499|2499|0|0|是|
|L2|2499|2499|0|0|是|
|L3|2499|2499|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 独立单点重跑

### 024_reruns_impl-024_tiktok_ads__url_report.json
[024_reruns_impl-024_tiktok_ads__url_report.json](../024_reruns_impl-024_tiktok_ads__url_report.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|2499|2499|109956|否|
|L1|0|2499|2499|109956|否|
|L2|0|2499|2499|109956|否|
|L3|0|2499|2499|109956|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L1：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L2：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L3：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`

#### baseline
私有SQL：`data/024_work/impl-024_tiktok_ads__url_report/baseline.sql`；SHA-256 `1ae195a199266db987ee17f17ad318928fce59750677cc1100e89961a9eef88d`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|2499|2499|109956|否|
|L1|0|2499|2499|109956|否|
|L2|0|2499|2499|109956|否|
|L3|0|2499|2499|109956|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L1：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L2：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L3：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`

#### adgroup_source_join
不计参与因素；类别候选C。契约url连接仅ad_group_id；额外source关系限制。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第46行、offset 1567起替换；其他字节相同。
原表达式：
```sql
 and ad.source_relation = ag.source_relation
```

修改后：
```sql

```

私有SQL：`data/024_work/impl-024_tiktok_ads__url_report/adgroup_source_join.sql`；SHA-256 `f1c5cd5f0dfa95b94d95298def8a1894cb8987eef2d2f121ceabfd447a0ed04f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|2499|2499|109956|否|
|L1|0|2499|2499|109956|否|
|L2|0|2499|2499|109956|否|
|L3|0|2499|2499|109956|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L1：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L2：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L3：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`

#### campaign_source_join
不计参与因素；类别候选C。契约url连接仅campaign_id；额外source关系限制。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第46行、offset 1806起替换；其他字节相同。
原表达式：
```sql
 and ad.source_relation = c.source_relation
```

修改后：
```sql

```

私有SQL：`data/024_work/impl-024_tiktok_ads__url_report/campaign_source_join.sql`；SHA-256 `971a1f652634f602f748fd4ee5da9a42be40eb9d4112b807fff71fb7841357b5`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|2499|2499|109956|否|
|L1|0|2499|2499|109956|否|
|L2|0|2499|2499|109956|否|
|L3|0|2499|2499|109956|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L1：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L2：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`
- L3：`{"date_day":2499,"advertiser_id":2499,"campaign_id":2499,"ad_group_id":2499,"ad_id":2499,"ad_group_name":2499,"ad_name":2499,"advertiser_name":2499,"audience_type":2499,"base_url":2499,"budget":2499,"campaign_name":2499,"clicks":2499,"comments":2499,"conversion":2499,"currency":2499,"daily_cpc":2499,"daily_cpm":2499,"daily_ctr":2499,"follows":2499,"gender":2499,"impressions":2499,"interest_category":2499,"likes":2499,"profile_visits":2499,"reach":2499,"real_time_conversion":2499,"shares":2499,"spend":2499,"total_conversion_value":2499,"total_purchase_value":2499,"total_sales_lead_value":2499,"url_host":2499,"url_path":2499,"utm_campaign":2499,"utm_content":2499,"utm_medium":2499,"utm_source":2499,"utm_term":2499,"video_views_p_25":2499,"video_views_p_50":2499,"video_views_p_75":2499,"video_watched_2_s":2499,"video_watched_6_s":2499}`

#### ads_source_join
不计参与因素；类别候选C。契约首个ads连接仅ad_id；额外source_relation条件单独检验。
相对本轮基线：行减少-2499，格减少-109956。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第46行、offset 1420起替换；其他字节相同。
原表达式：
```sql
 and h.source_relation = ad.source_relation
```

修改后：
```sql

```

私有SQL：`data/024_work/impl-024_tiktok_ads__url_report/ads_source_join.sql`；SHA-256 `6357f9ffac894348486c35b2defbae03c2012705b68590eac74f83dfa7b69c8e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2499|2499|4998|219912|否|
|L1|2499|2499|4998|219912|否|
|L2|2499|2499|4998|219912|否|
|L3|2499|2499|4998|219912|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":4998,"advertiser_id":4998,"campaign_id":4998,"ad_group_id":4998,"ad_id":4998,"ad_group_name":4998,"ad_name":4998,"advertiser_name":4998,"audience_type":4998,"base_url":4998,"budget":4998,"campaign_name":4998,"clicks":4998,"comments":4998,"conversion":4998,"currency":4998,"daily_cpc":4998,"daily_cpm":4998,"daily_ctr":4998,"follows":4998,"gender":4998,"impressions":4998,"interest_category":4998,"likes":4998,"profile_visits":4998,"reach":4998,"real_time_conversion":4998,"shares":4998,"spend":4998,"total_conversion_value":4998,"total_purchase_value":4998,"total_sales_lead_value":4998,"url_host":4998,"url_path":4998,"utm_campaign":4998,"utm_content":4998,"utm_medium":4998,"utm_source":4998,"utm_term":4998,"video_views_p_25":4998,"video_views_p_50":4998,"video_views_p_75":4998,"video_watched_2_s":4998,"video_watched_6_s":4998}`
- L1：`{"date_day":4998,"advertiser_id":4998,"campaign_id":4998,"ad_group_id":4998,"ad_id":4998,"ad_group_name":4998,"ad_name":4998,"advertiser_name":4998,"audience_type":4998,"base_url":4998,"budget":4998,"campaign_name":4998,"clicks":4998,"comments":4998,"conversion":4998,"currency":4998,"daily_cpc":4998,"daily_cpm":4998,"daily_ctr":4998,"follows":4998,"gender":4998,"impressions":4998,"interest_category":4998,"likes":4998,"profile_visits":4998,"reach":4998,"real_time_conversion":4998,"shares":4998,"spend":4998,"total_conversion_value":4998,"total_purchase_value":4998,"total_sales_lead_value":4998,"url_host":4998,"url_path":4998,"utm_campaign":4998,"utm_content":4998,"utm_medium":4998,"utm_source":4998,"utm_term":4998,"video_views_p_25":4998,"video_views_p_50":4998,"video_views_p_75":4998,"video_watched_2_s":4998,"video_watched_6_s":4998}`
- L2：`{"date_day":4998,"advertiser_id":4998,"campaign_id":4998,"ad_group_id":4998,"ad_id":4998,"ad_group_name":4998,"ad_name":4998,"advertiser_name":4998,"audience_type":4998,"base_url":4998,"budget":4998,"campaign_name":4998,"clicks":4998,"comments":4998,"conversion":4998,"currency":4998,"daily_cpc":4998,"daily_cpm":4998,"daily_ctr":4998,"follows":4998,"gender":4998,"impressions":4998,"interest_category":4998,"likes":4998,"profile_visits":4998,"reach":4998,"real_time_conversion":4998,"shares":4998,"spend":4998,"total_conversion_value":4998,"total_purchase_value":4998,"total_sales_lead_value":4998,"url_host":4998,"url_path":4998,"utm_campaign":4998,"utm_content":4998,"utm_medium":4998,"utm_source":4998,"utm_term":4998,"video_views_p_25":4998,"video_views_p_50":4998,"video_views_p_75":4998,"video_watched_2_s":4998,"video_watched_6_s":4998}`
- L3：`{"date_day":4998,"advertiser_id":4998,"campaign_id":4998,"ad_group_id":4998,"ad_id":4998,"ad_group_name":4998,"ad_name":4998,"advertiser_name":4998,"audience_type":4998,"base_url":4998,"budget":4998,"campaign_name":4998,"clicks":4998,"comments":4998,"conversion":4998,"currency":4998,"daily_cpc":4998,"daily_cpm":4998,"daily_ctr":4998,"follows":4998,"gender":4998,"impressions":4998,"interest_category":4998,"likes":4998,"profile_visits":4998,"reach":4998,"real_time_conversion":4998,"shares":4998,"spend":4998,"total_conversion_value":4998,"total_purchase_value":4998,"total_sales_lead_value":4998,"url_host":4998,"url_path":4998,"utm_campaign":4998,"utm_content":4998,"utm_medium":4998,"utm_source":4998,"utm_term":4998,"video_views_p_25":4998,"video_views_p_50":4998,"video_views_p_75":4998,"video_watched_2_s":4998,"video_watched_6_s":4998}`
## 规则问题

多处C互相遮蔽，最大单项改善为0或负数，§5未规定这种已定位交互如何排序。依§9主要类别记C（直接契约诊断），不选虚构的唯一主因，不把联改记为单改，也不将零改善项列参与因素。ad_report另有advertiser_id来源未明A选择；单改无贡献。

