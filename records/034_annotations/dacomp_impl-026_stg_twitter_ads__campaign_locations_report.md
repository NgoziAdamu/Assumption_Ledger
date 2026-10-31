# DAComp / impl-026_stg_twitter_ads__campaign_locations_report（v3）

## 错在哪里
1500行date_day只差TIMESTAMP午夜与DATE表示；agent遵守契约TIMESTAMP，留存gold是DATE。

证据复用入口：[018_impl-026_stg_twitter_ads__campaign_locations_report.md](../018_annotations/018_impl-026_stg_twitter_ads__campaign_locations_report.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## date_cast
- 角色：主要；类别：**其他**；把握：中。
- 依据：规格TIMESTAMP，gold留存DATE；午夜值L3相等，改DATE后L0相等；不反判遵约输出。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 10 / content：
```text
 True, '2018-10-05 15:13:11 UTC', None, '2018-10-08 17:32:52 UTC')]

 twitter_campaign_locations_report_data
[('account_id', 'VARCHAR', 'YES', None, None, None), ('campaign_id', 'VARCHAR', 'YES', None, None, None), ('country_region', 'VARCHAR', 'YES', None, None, None), ('date', 'VARCHAR', 'YES', None, None, None), ('placement', 'VARCHAR', 'YES', None, None, None), ('_fivetran_synced', 'VARCHAR', 'YES', None, None, None), ('app_clicks', 'BIGINT', 'YES', None, None, None), ('billed_charge_local_micro', 'BIGINT', 'YES', None, None, None), ('billed_engagements', 'BIGINT', 'YES', None, None, None), ('card_engagements', 'BIGINT', 'YES', None, None, None), ('carousel_swipes', 'BIGINT', 'YES', None, None, None), ('clicks', 'BIGINT', 'YES', None, None, None), ('engagements', 'BIGINT', 'YES', None, None, None), ('follows', 'BIGINT', 'YES', None, None, None), ('impressions', 'BIGINT', 'YES', None, None, None), ('like
```

## 规模、证据复用与新做
主要原因：其他。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-026_stg_twitter_ads__campaign_locations_report.md](../018_annotations/018_impl-026_stg_twitter_ads__campaign_locations_report.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_twitter_ads__campaign_locations_report
      description: "Daily campaign performance by country and placement with spend normalized from micro-units."
      source_table: raw.twitter_campaign_locations_report_data
      columns:
        - name: date_day
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: country
          data_type: VARCHAR
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

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-026_stg_twitter_ads__campaign_locations_report.md:29)
- [SQL定位](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-026_stg_twitter_ads__campaign_locations_report.md:70)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-026_stg_twitter_ads__campaign_locations_report.md:246)
- [重跑 date_day_type](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-026_stg_twitter_ads__campaign_locations_report.md:274)
- [重跑 date_cast](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-026_stg_twitter_ads__campaign_locations_report.md:309)
