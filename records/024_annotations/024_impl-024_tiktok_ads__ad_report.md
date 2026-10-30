# impl-024 · tiktok_ads__ad_report

用途：**全量**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**C**；把握：中。

CS各上游source_relation是不同raw表名。agent额外要求相等，使ads/维度连接失配；多处连接和投影叠加，单改均未减少规模，组合诊断L0全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-024_tiktok_ads__ad_report.md](../024_packages/024_impl-024_tiktok_ads__ad_report.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`。

```text
1178:     - name: tiktok_ads__ad_report
1179:       description: Daily ad performance aggregated from hourly with latest ad/ad group/campaign/advertiser attributes (no URL breakdown)
1180:       grain: One row per source_relation, date_day, ad_id
1181:       source_models:
1182:       - intermediate.int_tiktok_ads__ad_report_hourly (stat_time_hour, source_relation, ad_id, impressions, clicks, spend, reach, conversion, likes, comments, shares, profile_visits, follows, video_watched_2_s, video_watched_6_s, video_views_p_25, video_views_p_50, video_views_p_75, real_time_conversion, total_purchase_value, total_sales_lead_value)
1183:       - intermediate.int_tiktok_ads__ad_history_latest (ad_id, ad_name, ad_group_id, advertiser_id, campaign_id, source_relation)
1184:       - intermediate.int_tiktok_ads__ad_group_history_latest (ad_group_id, ad_group_name, advertiser_id, interest_category, gender, audience_type, budget, source_relation)
1185:       - intermediate.int_tiktok_ads__advertiser (advertiser_id, advertiser_name, currency)
1186:       - intermediate.int_tiktok_ads__campaign_history_latest (campaign_id, campaign_name, source_relation)
1187:       business_logic: '- Start from hourly facts; derive date_day by converting the hourly timestamp to its calendar date. - Join latest dimensions: - ads on matching ad_id - ad_groups on matching ad_group_id and source_relation - advertiser on matching advertiser_id - campaigns on matching campaign_id and source_relation - Group by source_relation, date_day, advertiser_id, advertiser_name, campaign_id, campaign_name, ad_group_id, ad_group_name, ad_id, ad_name, currency, interest_category, gender, audience_type, budget. - For each group, aggregate all hourly metrics by summing; sums ignore NULL inputs and return NULL if all inputs are NULL; no additional casting or rounding. - Compute rate metrics from the aggregated sums with zero-safe division: - daily_cpc: total spend divided by total clicks - daily_cpm: total spend divided by total impressions, scaled per 1,000 impressions - daily_ctr: total clicks divided by total impressions, expressed as a percentage If a denominator is zero or NULL, the result is NULL; no rounding is applied. - total_conversion_value is the daily sum of each hour’s (purchase value + sales lead value), equivalent to summing both components separately. - Dimension attributes come from the latest snapshots; if a joined record is missing, the attribute is NULL. All such attributes are included in the GROUP BY.'
1188:       columns:
1189:       - name: source_relation
1190:         data_type: VARCHAR
1191:         description: Identifier of the data source; grouping key
1192:         tests:
1193:         - not_null
1194:       - name: date_day
1195:         data_type: DATE
1196:         description: Calendar date derived from stat_time_hour
1197:         tests:
1198:         - not_null
1199:       - name: advertiser_id
1200:         data_type: VARCHAR
1201:         description: Advertiser ID from the latest ad group record; NULL if ad group is missing
1202:       - name: advertiser_name
1203:         data_type: VARCHAR
1204:         description: Advertiser name from the latest advertiser record; NULL if advertiser is missing
1205:       - name: campaign_id
1206:         data_type: VARCHAR
1207:         description: Campaign ID from the latest campaign record joined on source_relation; NULL if missing
1208:       - name: campaign_name
1209:         data_type: VARCHAR
1210:         description: Campaign name from the latest campaign record; NULL if missing
1211:       - name: ad_group_id
1212:         data_type: VARCHAR
1213:         description: Ad group ID from the latest ad group record joined on source_relation; NULL if missing
1214:       - name: ad_group_name
1215:         data_type: VARCHAR
1216:         description: Ad group name from the latest ad group record; NULL if missing
1217:       - name: ad_id
1218:         data_type: VARCHAR
1219:         description: Ad ID from hourly facts; grouping key
1220:         tests:
1221:         - not_null
1222:       - name: ad_name
1223:         data_type: VARCHAR
1224:         description: Ad name from the latest ad record; NULL if missing
1225:       - name: currency
1226:         data_type: VARCHAR
1227:         description: Advertiser currency code used for spend-derived metrics
1228:       - name: interest_category
1229:         data_type: VARCHAR
1230:         description: Interest category from the latest ad group record
1231:       - name: gender
1232:         data_type: VARCHAR
1233:         description: Target gender from the latest ad group record
1234:       - name: audience_type
1235:         data_type: VARCHAR
1236:         description: Audience type from the latest ad group record
1237:       - name: budget
1238:         data_type: DOUBLE
1239:         description: Ad group budget from the latest snapshot; included in grouping without aggregation
1240:       - name: impressions
1241:         data_type: HUGEINT
1242:         description: Daily sum of hourly impressions
1243:       - name: clicks
1244:         data_type: HUGEINT
1245:         description: Daily sum of hourly clicks
1246:       - name: spend
1247:         data_type: DOUBLE
1248:         description: Daily sum of hourly spend in advertiser currency
1249:       - name: reach
1250:         data_type: HUGEINT
1251:         description: Daily sum of hourly reach
1252:       - name: conversion
1253:         data_type: HUGEINT
1254:         description: Daily sum of hourly conversions
1255:       - name: likes
1256:         data_type: HUGEINT
1257:         description: Daily sum of hourly likes
1258:       - name: comments
1259:         data_type: HUGEINT
1260:         description: Daily sum of hourly comments
1261:       - name: shares
1262:         data_type: HUGEINT
1263:         description: Daily sum of hourly shares
1264:       - name: profile_visits
1265:         data_type: HUGEINT
1266:         description: Daily sum of hourly profile visits
1267:       - name: follows
1268:         data_type: HUGEINT
1269:         description: Daily sum of hourly follows
1270:       - name: video_watched_2_s
1271:         data_type: HUGEINT
1272:         description: Daily sum of hourly 2-second video plays
1273:       - name: video_watched_6_s
1274:         data_type: HUGEINT
1275:         description: Daily sum of hourly 6-second video plays
1276:       - name: video_views_p_25
1277:         data_type: HUGEINT
1278:         description: Daily sum of hourly 25% video views
1279:       - name: video_views_p_50
1280:         data_type: HUGEINT
1281:         description: Daily sum of hourly 50% video views
1282:       - name: video_views_p_75
1283:         data_type: HUGEINT
1284:         description: Daily sum of hourly 75% video views
1285:       - name: real_time_conversion
1286:         data_type: HUGEINT
1287:         description: Daily sum of hourly real-time conversions
1288:       - name: total_purchase_value
1289:         data_type: DOUBLE
1290:         description: Daily sum of hourly purchase value
1291:       - name: total_sales_lead_value
1292:         data_type: DOUBLE
1293:         description: Daily sum of hourly sales lead value
1294:       - name: total_conversion_value
1295:         data_type: DOUBLE
1296:         description: Daily sum of each hour’s purchase value plus sales lead value
1297:       - name: daily_cpc
1298:         data_type: DOUBLE
1299:         description: Total spend divided by total clicks; NULL if clicks are zero or NULL; no rounding
1300:       - name: daily_cpm
1301:         data_type: DOUBLE
1302:         description: Total spend per 1,000 impressions; NULL if impressions are zero or NULL; no rounding
1303:       - name: daily_ctr
1304:         data_type: DOUBLE
1305:         description: Click-through rate as clicks divided by impressions times 100; NULL if impressions are zero or NULL; no rounding
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/marts/tiktok_ads__ad_report.sql`；SHA-256 `a818f4eedac9a8ab022d1464a40933fc7e45399f7acd47e00675cbecf7832140`。

```text
1: with joined_data as (
2:     select
3:         h.source_relation,
4:         cast(h.stat_time_hour as date) as date_day,
5:         ag.advertiser_id,
6:         a.advertiser_name,
7:         ad.campaign_id,
8:         c.campaign_name,
9:         ad.ad_group_id,
10:         ag.ad_group_name,
11:         h.ad_id,
12:         ad.ad_name,
13:         a.currency,
14:         ag.interest_category,
15:         ag.gender,
16:         ag.audience_type,
17:         ag.budget,
18:                 h.impressions,
19:                 h.clicks,
20:                 h.spend,
21:                 h.reach,
22:                 h.conversion,
23:                 h.likes,
24:                 h.comments,
25:                 h.shares,
26:                 h.profile_visits,
27:                 h.follows,
28:                 h.video_watched_2_s,
29:                 h.video_watched_6_s,
30:                 h.video_views_p_25,
31:                 h.video_views_p_50,
32:                 h.video_views_p_75,
33:                 h.real_time_conversion,
34:                 h.total_purchase_value,
35:                 h.total_sales_lead_value,
36:                 (h.total_purchase_value + h.total_sales_lead_value) as total_conversion_value_row
37:     from intermediate.int_tiktok_ads__ad_report_hourly as h
38:     left join intermediate.int_tiktok_ads__ad_history_latest as ad on h.ad_id = ad.ad_id and h.source_relation = ad.source_relation left join intermediate.int_tiktok_ads__ad_group_history_latest as ag on ad.ad_group_id = ag.ad_group_id and ad.source_relation = ag.source_relation left join intermediate.int_tiktok_ads__advertiser as a on ag.advertiser_id = a.advertiser_id left join intermediate.int_tiktok_ads__campaign_history_latest as c on ad.campaign_id = c.campaign_id and ad.source_relation = c.source_relation
39:     
40: ), aggregated as (
41:     select
42:         source_relation,
43:         date_day,
44:         advertiser_id,
45:         advertiser_name,
46:         campaign_id,
47:         campaign_name,
48:         ad_group_id,
49:         ad_group_name,
50:         ad_id,
51:         ad_name,
52:         currency,
53:         interest_category,
54:         gender,
55:         audience_type,
56:         budget,
57:         sum(impressions) as impressions,
58:         sum(clicks) as clicks,
59:         sum(spend) as spend,
60:         sum(reach) as reach,
61:         sum(conversion) as conversion,
62:         sum(likes) as likes,
63:         sum(comments) as comments,
64:         sum(shares) as shares,
65:         sum(profile_visits) as profile_visits,
66:         sum(follows) as follows,
67:         sum(video_watched_2_s) as video_watched_2_s,
68:         sum(video_watched_6_s) as video_watched_6_s,
69:         sum(video_views_p_25) as video_views_p_25,
70:         sum(video_views_p_50) as video_views_p_50,
71:         sum(video_views_p_75) as video_views_p_75,
72:         sum(real_time_conversion) as real_time_conversion,
73:         sum(total_purchase_value) as total_purchase_value,
74:         sum(total_sales_lead_value) as total_sales_lead_value,
75:         sum(total_conversion_value_row) as total_conversion_value
76:     from joined_data
77:     group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
78: )
79: select
80:     *,
81:     spend / nullif(clicks, 0) as daily_cpc,
82:     spend / nullif(impressions, 0) * 1000 as daily_cpm,
83:     clicks / nullif(impressions, 0) * 100 as daily_ctr
84: from aggregated
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/sql/marts/tiktok_ads__ad_report.sql`；SHA-256 `b583f22e97330a2df3e5b35562a87fd2dff70b050d1e558ea25ddbcd9be12d54`。

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
23:     advertiser.currency,
24:     ad_groups.interest_category,
25:     ad_groups.gender,
26:     ad_groups.audience_type,
27:     ad_groups.budget,
28:     sum(hourly.impressions) as impressions,
29:     sum(hourly.clicks) as clicks,
30:     sum(hourly.spend) as spend,
31:     sum(hourly.reach) as reach,
32:     sum(hourly.conversion) as conversion,
33:     sum(hourly.likes) as likes,
34:     sum(hourly.comments) as comments,
35:     sum(hourly.shares) as shares,
36:     sum(hourly.profile_visits) as profile_visits,
37:     sum(hourly.follows) as follows,
38:     sum(hourly.video_watched_2_s) as video_watched_2_s,
39:     sum(hourly.video_watched_6_s) as video_watched_6_s,
40:     sum(hourly.video_views_p_25) as video_views_p_25,
41:     sum(hourly.video_views_p_50) as video_views_p_50,
42:     sum(hourly.video_views_p_75) as video_views_p_75,
43:     sum(hourly.real_time_conversion) as real_time_conversion,
44:     sum(hourly.total_purchase_value) as total_purchase_value,
45:     sum(hourly.total_sales_lead_value) as total_sales_lead_value,
46:     sum(hourly.total_purchase_value + hourly.total_sales_lead_value) as total_conversion_value,
47:     sum(hourly.spend)/nullif(sum(hourly.clicks),0) as daily_cpc,
48:     (sum(hourly.spend)/nullif(sum(hourly.impressions),0))*1000 as daily_cpm,
49:     (sum(hourly.clicks)/nullif(sum(hourly.impressions),0))*100 as daily_ctr
50:   from hourly
51:   left join ads
52:     on hourly.ad_id = ads.ad_id
53:       left join ad_groups
54:     on ads.ad_group_id = ad_groups.ad_group_id
55:     and ads.source_relation = ad_groups.source_relation
56:   left join advertiser
57:     on ads.advertiser_id = advertiser.advertiser_id
58:       left join campaigns
59:     on ads.campaign_id = campaigns.campaign_id
60:     and ads.source_relation = campaigns.source_relation
61:   group by
62:     hourly.source_relation,
63:     cast(hourly.stat_time_hour as date),
64:     ad_groups.advertiser_id,
65:     advertiser.advertiser_name,
66:     campaigns.campaign_id,
67:     campaigns.campaign_name,
68:     ad_groups.ad_group_id,
69:     ad_groups.ad_group_name,
70:     hourly.ad_id,
71:     ads.ad_name,
72:     advertiser.currency,
73:     ad_groups.interest_category,
74:     ad_groups.gender,
75:     ad_groups.audience_type,
76:     ad_groups.budget
77: )
78: select * from aggregated
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
SELECT count(*) n,count(ad_name) ads_n,count(advertiser_name) advertisers_n,count(ad_group_id) groups_n,count(campaign_id) campaigns_n FROM marts.tiktok_ads__ad_report
```


```json
{"columns":["n","ads_n","advertisers_n","groups_n","campaigns_n"],"rows":[[2499,2499,2486,0,0]]}
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
    left join intermediate.int_tiktok_ads__ad_history_latest as ad on h.ad_id = ad.ad_id left join intermediate.int_tiktok_ads__ad_group_history_latest as ag on ad.ad_group_id = ag.ad_group_id and ad.source_relation = ag.source_relation left join intermediate.int_tiktok_ads__advertiser as a on ad.advertiser_id = a.advertiser_id left join intermediate.int_tiktok_ads__campaign_history_latest as c on ad.campaign_id = c.campaign_id and ad.source_relation = c.source_relation
    
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
labels：`["campaign_projection","ad_group_projection","advertiser_join","ads_source_join"]`

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
SELECT count(*) n,count(ad_name) ads,count(advertiser_name) advertisers,count(ad_group_id) groups,count(campaign_id) campaigns FROM marts.tiktok_ads__ad_report
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

### 024_reruns_impl-024_tiktok_ads__ad_report.json
[024_reruns_impl-024_tiktok_ads__ad_report.json](../024_reruns_impl-024_tiktok_ads__ad_report.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2499|2499|2499|7484|否|
|L1|2499|2499|2499|7484|否|
|L2|2499|2499|2499|7484|否|
|L3|2499|2499|2499|7484|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L1：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L2：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L3：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`

#### baseline
私有SQL：`data/024_work/impl-024_tiktok_ads__ad_report/baseline.sql`；SHA-256 `a818f4eedac9a8ab022d1464a40933fc7e45399f7acd47e00675cbecf7832140`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2499|2499|2499|7484|否|
|L1|2499|2499|2499|7484|否|
|L2|2499|2499|2499|7484|否|
|L3|2499|2499|2499|7484|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L1：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L2：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L3：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`

#### campaign_projection
不计参与因素；类别候选C。契约输出campaign_id来自匹配campaigns，非ads外键。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第7行、offset 173起替换；其他字节相同。
原表达式：
```sql
ad.campaign_id,
```

修改后：
```sql
c.campaign_id,
```

私有SQL：`data/024_work/impl-024_tiktok_ads__ad_report/campaign_projection.sql`；SHA-256 `1655fd357f48d98ca7785614ba028b8c762086e55265d37049b745acb7d8088a`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2499|2499|2499|7484|否|
|L1|2499|2499|2499|7484|否|
|L2|2499|2499|2499|7484|否|
|L3|2499|2499|2499|7484|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L1：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L2：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L3：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`

#### ad_group_projection
不计参与因素；类别候选C。契约输出ad_group_id来自匹配ad_groups。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第9行、offset 222起替换；其他字节相同。
原表达式：
```sql
ad.ad_group_id,
```

修改后：
```sql
ag.ad_group_id,
```

私有SQL：`data/024_work/impl-024_tiktok_ads__ad_report/ad_group_projection.sql`；SHA-256 `c131d517f757ca1a8bb3f02296b7ba7c79e34faf1b3ac59f1fb0cbdf9eb3b1ee`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2499|2499|2499|7484|否|
|L1|2499|2499|2499|7484|否|
|L2|2499|2499|2499|7484|否|
|L3|2499|2499|2499|7484|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L1：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L2：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L3：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`

#### advertiser_join
不计参与因素；类别候选A。URL契约规定ads.advertiser_id；ad_report契约只说匹配advertiser_id未明确来源。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第38行、offset 1489起替换；其他字节相同。
原表达式：
```sql
on ag.advertiser_id = a.advertiser_id
```

修改后：
```sql
on ad.advertiser_id = a.advertiser_id
```

私有SQL：`data/024_work/impl-024_tiktok_ads__ad_report/advertiser_join.sql`；SHA-256 `d89a8a8ffdc21fa100c78ea0c8ce6fe7c4f88c1db47afa2a85ecec1e46fe379e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2499|2499|2499|7484|否|
|L1|2499|2499|2499|7484|否|
|L2|2499|2499|2499|7484|否|
|L3|2499|2499|2499|7484|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L1：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L2：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`
- L3：`{"ad_name":2499,"advertiser_name":2486,"currency":2499}`

#### ads_source_join
不计参与因素；类别候选C。契约首个ads连接仅ad_id；额外source_relation条件单独检验。
相对本轮基线：行减少0，格减少-2499。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第38行、offset 1242起替换；其他字节相同。
原表达式：
```sql
 and h.source_relation = ad.source_relation
```

修改后：
```sql

```

私有SQL：`data/024_work/impl-024_tiktok_ads__ad_report/ads_source_join.sql`；SHA-256 `247e039b8ac78dbebcba46b95b715490c28fcab30bf7cad134ef97153cb21d8f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2499|2499|2499|9983|否|
|L1|2499|2499|2499|9983|否|
|L2|2499|2499|2499|9983|否|
|L3|2499|2499|2499|9983|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"ad_group_id":2499,"advertiser_name":2486,"campaign_id":2499,"currency":2499}`
- L1：`{"ad_group_id":2499,"advertiser_name":2486,"campaign_id":2499,"currency":2499}`
- L2：`{"ad_group_id":2499,"advertiser_name":2486,"campaign_id":2499,"currency":2499}`
- L3：`{"ad_group_id":2499,"advertiser_name":2486,"campaign_id":2499,"currency":2499}`
## 规则问题

多处C互相遮蔽，最大单项改善为0或负数，§5未规定这种已定位交互如何排序。依§9主要类别记C（直接契约诊断），不选虚构的唯一主因，不把联改记为单改，也不将零改善项列参与因素。ad_report另有advertiser_id来源未明A选择；单改无贡献。

