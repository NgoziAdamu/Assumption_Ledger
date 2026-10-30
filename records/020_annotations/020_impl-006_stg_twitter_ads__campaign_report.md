# impl-006 / stg_twitter_ads__campaign_report（全量）

## 结论

主要原因：**多因并列（A、D）**；把握：高。Twitter可计算金额/率指标占位，与无源app指标默认值并列。

参与因素：A：follows（减0行/453格）；A：likes（减0行/457格）。标记：已披露（D占位部分）。

## 差异与归因依据

已有billed_charge_local_micro、clicks/impressions/engagements却不计算，D；没有app_installs/app_opens，默认0或NULL属A；likes/follows的布尔文本数值化未规定，为A参与因素。

层：staging；比较库schema：staging；评测键：campaign_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:1263–1336`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql:1–41`；SHA-256 `14d17488aa9130efab15777959fef9358f713b2f255a0903298bc3e1c1f4be0e`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql:1–74`；SHA-256 `43d8d54225bcb177a89348c16be5ac92a471805bc47e99f5426fe731b83d61a7`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- app_installs（agent SQL 第31行起）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS app_installs
```
→
```sql
CAST(0 AS INT) AS app_installs
```

- app_opens（agent SQL 第32行起）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS app_opens
```
→
```sql
CAST(0 AS INT) AS app_opens
```

- click_through_rate（agent SQL 第33行起）：
```sql
CAST(NULL::DECIMAL(10,4) AS DECIMAL(10,4)) AS click_through_rate
```
→
```sql
CASE WHEN impressions > 0 THEN CAST((clicks * 100.0 / impressions) AS DECIMAL(10, 4)) ELSE 0.0 END AS click_through_rate
```

- cost_per_click（agent SQL 第35行起）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS cost_per_click
```
→
```sql
CASE WHEN clicks > 0 THEN CAST((billed_charge_local_micro / 1000000.0 / clicks) AS DECIMAL(18, 2)) ELSE 0.0 END AS cost_per_click
```

- cost_per_engagement（agent SQL 第36行起）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS cost_per_engagement
```
→
```sql
CASE WHEN engagements > 0 THEN CAST((billed_charge_local_micro / 1000000.0 / engagements) AS DECIMAL(18, 2)) ELSE 0.0 END AS cost_per_engagement
```

- cost_per_thousand_impressions（agent SQL 第37行起）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS cost_per_thousand_impressions
```
→
```sql
CASE WHEN impressions > 0 THEN CAST((billed_charge_local_micro / 1000000.0 / impressions * 1000) AS DECIMAL(18, 2)) ELSE 0.0 END AS cost_per_thousand_impressions
```

- engagement_rate（agent SQL 第34行起）：
```sql
CAST(NULL::DECIMAL(10,4) AS DECIMAL(10,4)) AS engagement_rate
```
→
```sql
CASE WHEN impressions > 0 THEN CAST((engagements * 100.0 / impressions) AS DECIMAL(10, 4)) ELSE 0.0 END AS engagement_rate
```

- follows（agent SQL 第19行起）：
```sql
TRY_CAST("follows" AS INTEGER) AS follows
```
→
```sql
CASE WHEN follows = 'true' THEN 1 WHEN follows = 'false' THEN 0 ELSE CAST(follows AS INT) END AS follows
```

- likes（agent SQL 第18行起）：
```sql
TRY_CAST("likes" AS INTEGER) AS likes
```
→
```sql
CASE WHEN likes = 'true' THEN 1 WHEN likes = 'false' THEN 0 ELSE CAST(likes AS INT) END AS likes
```

- spend（agent SQL 第14行起）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
→
```sql
CAST(billed_charge_local_micro / 1000000.0 AS DECIMAL(18, 2)) AS spend
```

## agent可见证据与不确定性

不确定性四档：**app_installs=只有通用策略说明；app_opens=只有通用策略说明；click_through_rate=只有通用策略说明；cost_per_click=只有通用策略说明；cost_per_engagement=只有通用策略说明；cost_per_thousand_impressions=只有通用策略说明；engagement_rate=只有通用策略说明；spend=只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。 event 97（args.final_thought）：脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_twitter_ads__campaign_report | False |
| 16 | 15 | twitter_campaign_report_data | False |
| 18 | 17 | twitter_campaign_report_data | False |
| 30 | 29 | stg_twitter_ads__campaign_report | False |
| 38 | 37 | stg_twitter_ads__campaign_report | False |
| 82 | 81 | stg_twitter_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='twitter_campaign_report_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "twitter_campaign_report_data", "account_id", "VARCHAR"], ["raw", "twitter_campaign_report_data", "campaign_id", "VARCHAR"], ["raw", "twitter_campaign_report_data", "date", "VARCHAR"], ["raw", "twitter_campaign_report_data", "placement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "app_clicks", "BIGINT"], ["raw", "twitter_campaign_report_data", "billed_charge_local_micro", "BIGINT"], ["raw", "twitter_campaign_report_data", "billed_engagements", "BIGINT"], ["raw", "twitter_campaign_report_data", "card_engagements", "BIGINT"], ["raw", "twitter_campaign_report_data", "carousel_swipes", "BIGINT"], ["raw", "twitter_campaign_report_data", "clicks", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_custom_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_custom_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_custom_order_quantity_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_custom_order_quantity_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_custom_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_custom_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_custom_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_custom_sale_amount_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_custom_sale_amount_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_downloads_metric", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_downloads_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_downloads_order_quantity_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_downloads_order_quantity_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_downloads_post_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_downloads_post_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_downloads_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_downloads_sale_amount_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_downloads_sale_amount_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_purchases_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_purchases_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_purchases_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_purchases_order_quantity_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_purchases_order_quantity_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_purchases_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_purchases_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_purchases_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_purchases_sale_amount_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_purchases_sale_amount_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_sign_ups_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_sign_ups_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_sign_ups_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_sign_ups_order_quantity_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_sign_ups_order_quantity_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_sign_ups_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_sign_ups_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_sign_ups_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_sign_ups_sale_amount_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_sign_ups_sale_amount_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_site_visits_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_site_visits_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_site_visits_order_quantity_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_site_visits_order_quantity_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_site_visits_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_site_visits_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "conversion_site_visits_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_site_visits_sale_amount_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "conversion_site_visits_sale_amount_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "engagements", "BIGINT"], ["raw", "twitter_campaign_report_data", "follows", "VARCHAR"], ["raw", "twitter_campaign_report_data", "impressions", "BIGINT"], ["raw", "twitter_campaign_report_data", "likes", "VARCHAR"], ["raw", "twitter_campaign_report_data", "media_engagements", "BIGINT"], ["raw", "twitter_campaign_report_data", "media_views", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_achievements_unlocked_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_achievements_unlocked_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_achievements_unlocked_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_achievements_unlocked_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_achievements_unlocked_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_add_to_carts_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_add_to_carts_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_add_to_carts_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_add_to_carts_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_add_to_carts_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_add_to_wishlists_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_add_to_wishlists_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_add_to_wishlists_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_add_to_wishlists_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_add_to_wishlists_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_checkouts_initiated_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_checkouts_initiated_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_checkouts_initiated_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_checkouts_initiated_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_checkouts_initiated_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_content_views_assisted", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_content_views_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_content_views_post_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_content_views_post_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_content_views_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_downloads_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_downloads_post_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_downloads_post_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_downloads_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_installs_assisted", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_installs_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_installs_post_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_installs_post_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_installs_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_invites_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_invites_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_invites_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_invites_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_invites_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_key_page_views_post_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_key_page_views_post_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_levels_achieved_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_levels_achieved_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_levels_achieved_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_levels_achieved_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_levels_achieved_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_achievements_unlocked_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_achievements_unlocked_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_achievements_unlocked_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_add_to_carts_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_add_to_carts_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_add_to_carts_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_add_to_wishlists_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_add_to_wishlists_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_add_to_wishlists_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_checkouts_initiated_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_checkouts_initiated_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_checkouts_initiated_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_content_views_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_content_views_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_content_views_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_invites_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_invites_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_invites_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_levels_achieved_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_levels_achieved_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_levels_achieved_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_logins_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_logins_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_logins_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_payment_info_additions_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_payment_info_additions_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_payment_info_additions_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_purchases_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_purchases_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_purchases_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_rates_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_rates_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_rates_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_reservations_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_reservations_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_reservations_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_searches_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_searches_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_searches_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_shares_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_shares_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_shares_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_sign_ups_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_sign_ups_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_sign_ups_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_spent_credits_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_spent_credits_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_spent_credits_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_tutorials_completed_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_tutorials_completed_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_tutorials_completed_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_updates_metric", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_updates_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_lifetime_value_updates_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_logins_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_logins_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_logins_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_logins_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_logins_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_payment_info_additions_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_payment_info_additions_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_payment_info_additions_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_payment_info_additions_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_payment_info_additions_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_purchases_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_purchases_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_purchases_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_purchases_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_purchases_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_rates_assisted", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_rates_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_rates_post_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_rates_post_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_rates_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_re_engages_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_re_engages_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_re_engages_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_re_engages_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_re_engages_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_reservations_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_reservations_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_reservations_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_reservations_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_reservations_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_searches_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_searches_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_searches_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_searches_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_searches_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_shares_assisted", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_shares_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_shares_post_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_shares_post_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_shares_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_sign_ups_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_sign_ups_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_sign_ups_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_sign_ups_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_sign_ups_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_site_visits_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_site_visits_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_site_visits_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_site_visits_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_spent_credits_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_spent_credits_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_spent_credits_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_spent_credits_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_spent_credits_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_tutorials_completed_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_tutorials_completed_order_quantity", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_tutorials_completed_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_tutorials_completed_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_tutorials_completed_sale_amount", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_updates_assisted", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_updates_order_quantity", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_updates_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_updates_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_updates_sale_amount", "VARCHAR"], ["raw", "twitter_campaign_report_data", "poll_card_vote", "BIGINT"], ["raw", "twitter_campaign_report_data", "qualified_impressions", "VARCHAR"], ["raw", "twitter_campaign_report_data", "replies", "BIGINT"], ["raw", "twitter_campaign_report_data", "retweets", "BIGINT"], ["raw", "twitter_campaign_report_data", "tweets_send", "VARCHAR"], ["raw", "twitter_campaign_report_data", "unfollows", "BIGINT"], ["raw", "twitter_campaign_report_data", "url_clicks", "BIGINT"], ["raw", "twitter_campaign_report_data", "video_3_s_100_pct_views", "BIGINT"], ["raw", "twitter_campaign_report_data", "video_6_s_views", "BIGINT"], ["raw", "twitter_campaign_report_data", "video_content_starts", "VARCHAR"], ["raw", "twitter_campaign_report_data", "video_cta_clicks", "VARCHAR"], ["raw", "twitter_campaign_report_data", "video_mrc_views", "BIGINT"], ["raw", "twitter_campaign_report_data", "video_total_views", "BIGINT"], ["raw", "twitter_campaign_report_data", "video_views_100", "BIGINT"], ["raw", "twitter_campaign_report_data", "video_views_25", "BIGINT"], ["raw", "twitter_campaign_report_data", "video_views_50", "BIGINT"], ["raw", "twitter_campaign_report_data", "video_views_75", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_installs_skan_post_engagement", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_installs_skan_post_view", "BIGINT"], ["raw", "twitter_campaign_report_data", "mobile_conversion_purchases_skan_post_engagement", "VARCHAR"], ["raw", "twitter_campaign_report_data", "mobile_conversion_purchases_skan_post_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "video_15_s_views", "BIGINT"], ["raw", "twitter_campaign_report_data", "auto_created_conversion_landing_page_view", "VARCHAR"], ["raw", "twitter_campaign_report_data", "auto_created_conversion_session", "VARCHAR"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "follows" IS NULL) AS c0_null,count(*) FILTER(WHERE "follows" IS NOT NULL AND TRY_CAST("follows" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "impressions" IS NULL) AS c2_null,count(*) FILTER(WHERE "impressions" IS NOT NULL AND TRY_CAST("impressions" AS DOUBLE) IS NULL) AS c3_not_numeric,count(*) FILTER(WHERE "likes" IS NULL) AS c4_null,count(*) FILTER(WHERE "likes" IS NOT NULL AND TRY_CAST("likes" AS DOUBLE) IS NULL) AS c5_not_numeric FROM raw.twitter_campaign_report_data
```

结果：`[[900, 215, 453, 0, 0, 209, 457]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=31 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_twitter_ads__campaign_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：900行 / 8110格；重跑基线：900行 / 8110格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:900行/8110格 / L1:900行/8110格 / L2:900行/8110格 / L3:900行/8110格 | 均未整表匹配 |
| app_installs | L0:900行/7210格 / L1:900行/7210格 / L2:900行/7210格 / L3:900行/7210格 | 均未整表匹配 |
| app_opens | L0:900行/7210格 / L1:900行/7210格 / L2:900行/7210格 / L3:900行/7210格 | 均未整表匹配 |
| click_through_rate | L0:900行/7210格 / L1:900行/7210格 / L2:900行/7210格 / L3:900行/7210格 | 均未整表匹配 |
| cost_per_click | L0:900行/7210格 / L1:900行/7210格 / L2:900行/7210格 / L3:900行/7210格 | 均未整表匹配 |
| cost_per_engagement | L0:900行/7210格 / L1:900行/7210格 / L2:900行/7210格 / L3:900行/7210格 | 均未整表匹配 |
| cost_per_thousand_impressions | L0:900行/7210格 / L1:900行/7210格 / L2:900行/7210格 / L3:900行/7210格 | 均未整表匹配 |
| engagement_rate | L0:900行/7210格 / L1:900行/7210格 / L2:900行/7210格 / L3:900行/7210格 | 均未整表匹配 |
| follows | L0:900行/7657格 / L1:900行/7657格 / L2:900行/7657格 / L3:900行/7657格 | 均未整表匹配 |
| likes | L0:900行/7653格 / L1:900行/7653格 / L2:900行/7653格 / L3:900行/7653格 | 均未整表匹配 |
| spend | L0:900行/7210格 / L1:900行/7210格 / L2:900行/7210格 / L3:900行/7210格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"app_installs": 900, "app_opens": 900, "click_through_rate": 900, "cost_per_click": 900, "cost_per_engagement": 900, "cost_per_thousand_impressions": 900, "engagement_rate": 900, "follows": 453, "likes": 457, "spend": 900} |
| app_installs | {"app_opens": 900, "click_through_rate": 900, "cost_per_click": 900, "cost_per_engagement": 900, "cost_per_thousand_impressions": 900, "engagement_rate": 900, "follows": 453, "likes": 457, "spend": 900} |
| app_opens | {"app_installs": 900, "click_through_rate": 900, "cost_per_click": 900, "cost_per_engagement": 900, "cost_per_thousand_impressions": 900, "engagement_rate": 900, "follows": 453, "likes": 457, "spend": 900} |
| click_through_rate | {"app_installs": 900, "app_opens": 900, "cost_per_click": 900, "cost_per_engagement": 900, "cost_per_thousand_impressions": 900, "engagement_rate": 900, "follows": 453, "likes": 457, "spend": 900} |
| cost_per_click | {"app_installs": 900, "app_opens": 900, "click_through_rate": 900, "cost_per_engagement": 900, "cost_per_thousand_impressions": 900, "engagement_rate": 900, "follows": 453, "likes": 457, "spend": 900} |
| cost_per_engagement | {"app_installs": 900, "app_opens": 900, "click_through_rate": 900, "cost_per_click": 900, "cost_per_thousand_impressions": 900, "engagement_rate": 900, "follows": 453, "likes": 457, "spend": 900} |
| cost_per_thousand_impressions | {"app_installs": 900, "app_opens": 900, "click_through_rate": 900, "cost_per_click": 900, "cost_per_engagement": 900, "engagement_rate": 900, "follows": 453, "likes": 457, "spend": 900} |
| engagement_rate | {"app_installs": 900, "app_opens": 900, "click_through_rate": 900, "cost_per_click": 900, "cost_per_engagement": 900, "cost_per_thousand_impressions": 900, "follows": 453, "likes": 457, "spend": 900} |
| follows | {"app_installs": 900, "app_opens": 900, "click_through_rate": 900, "cost_per_click": 900, "cost_per_engagement": 900, "cost_per_thousand_impressions": 900, "engagement_rate": 900, "likes": 457, "spend": 900} |
| likes | {"app_installs": 900, "app_opens": 900, "click_through_rate": 900, "cost_per_click": 900, "cost_per_engagement": 900, "cost_per_thousand_impressions": 900, "engagement_rate": 900, "follows": 453, "spend": 900} |
| spend | {"app_installs": 900, "app_opens": 900, "click_through_rate": 900, "cost_per_click": 900, "cost_per_engagement": 900, "cost_per_thousand_impressions": 900, "engagement_rate": 900, "follows": 453, "likes": 457} |

本表全部重跑证据文件：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_twitter_ads__campaign_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
