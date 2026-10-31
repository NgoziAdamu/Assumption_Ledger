# DAComp / impl-019_apple_store__subscription_report（v3）

## 错在哪里
summary/event两个连接用NULL安全等值，gold用普通等值；summary连接是主要差异。

证据复用入口：[018_impl-019_apple_store__subscription_report.md](../018_annotations/018_impl-019_apple_store__subscription_report.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## summary_null_join
- 角色：主要；类别：**Unstated Choice**；把握：中。
- 依据：规格未规定NULL键相等；IS NOT DISTINCT FROM与=差异，1600→346行。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 1 / args.content：
```text
description: Daily subscription KPIs per product and territory; joins summary and events to the reporting grain and enriches with country names/regions; missing measures are zero-filled.
      grain: One row per date_day × vendor_number × app_apple_id × subscription_name × territory_short × state × source_relation
      source_models:
      - intermediate.int_apple_store__subscription_report
      - intermediate.int_apple_store__subscription_summary
      - intermediate.int_apple_store__subscription_events
      - intermediate.int_apple_store__country_codes
      business_logic: '- Use intermediate.int_apple_store__subscription_report as the driver; output one row per key: date_day, vendor_number, app_apple_id, subscription_name, country (as territory_short), state, source_relation. - Left join intermediate.int_apple_store__subscription_summary on vendor_number, app_apple_id, date_day, subscription_name, co
```
## event_null_join
- 角色：参与；类别：**Unstated Choice**；把握：中。
- 依据：同样NULL匹配约定未定，1600→1295行。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 1 / args.content：
```text
description: Daily subscription KPIs per product and territory; joins summary and events to the reporting grain and enriches with country names/regions; missing measures are zero-filled.
      grain: One row per date_day × vendor_number × app_apple_id × subscription_name × territory_short × state × source_relation
      source_models:
      - intermediate.int_apple_store__subscription_report
      - intermediate.int_apple_store__subscription_summary
      - intermediate.int_apple_store__subscription_events
      - intermediate.int_apple_store__country_codes
      business_logic: '- Use intermediate.int_apple_store__subscription_report as the driver; output one row per key: date_day, vendor_number, app_apple_id, subscription_name, country (as territory_short), state, source_relation. - Left join intermediate.int_apple_store__subscription_summary on vendor_number, app_apple_id, date_day, subscription_name, co
```

## 规模、证据复用与新做
主要原因：Unstated Choice。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-019_apple_store__subscription_report.md](../018_annotations/018_impl-019_apple_store__subscription_report.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: apple_store__subscription_report
      description: Daily subscription KPIs per product and territory; joins summary and events to the reporting grain and enriches with country names/regions; missing measures are zero-filled.
      grain: One row per date_day × vendor_number × app_apple_id × subscription_name × territory_short × state × source_relation
      source_models:
      - intermediate.int_apple_store__subscription_report
      - intermediate.int_apple_store__subscription_summary
      - intermediate.int_apple_store__subscription_events
      - intermediate.int_apple_store__country_codes
      business_logic: '- Use intermediate.int_apple_store__subscription_report as the driver; output one row per key: date_day, vendor_number, app_apple_id, subscription_name, country (as territory_short), state, source_relation. - Left join intermediate.int_apple_store__subscription_summary on vendor_number, app_apple_id, date_day, subscription_name, country, state, and source_relation to bring active_* measures. - Left join intermediate.int_apple_store__subscription_events on the same keys to bring event_* measures. - Left join intermediate.int_apple_store__country_codes on country_code_alpha_2 = reporting country; set territory_long to alternative country name when available, otherwise the standard country name; set region and sub_region from the match. - Pass through app_name and source_relation from the reporting grain; set territory_short from the reporting country and state from the reporting state. - Null handling: replace missing active_* and event_* measures with 0; geography fields from country_codes are null when no country match; other string fields are passed through unchanged. - No aggregation, sorting, or filtering is applied; row multiplicity follows the joins and assumes uniqueness of joined sources on the stated keys.'
      columns:
      - name: date_day
        data_type: TIMESTAMP
        description: Day timestamp from the reporting grain; used in joins; no timezone conversion.
        tests:
        - not_null
      - name: vendor_number
        data_type: INTEGER
        description: Vendor identifier from the reporting grain; part of the join keys.
        tests:
        - not_null
      - name: app_apple_id
        data_type: INTEGER
        description: Application Apple ID from the reporting grain; part of the join keys.
        tests:
        - not_null
      - name: app_name
        data_type: VARCHAR
        description: Application name passed through from the reporting grain.
      - name: subscription_name
        data_type: VARCHAR
        description: Subscription product name from the reporting grain; part of the join keys.
        tests:
        - not_null
      - name: territory_long
        data_type: VARCHAR
        description: 'Country name from country_codes: use alternative name when available, otherwise the standard country name; null if no country match.'
      - name: territory_short
        data_type: VARCHAR
        description: Two-letter ISO alpha-2 country code from the reporting grain; preserved as stored.
        tests:
        - not_null
      - name: state
        data_type: VARCHAR
        description: State/province code from the reporting grain; may be null.
      - name: region
        data_type: VARCHAR
        description: Region from country_codes for the matched country; null if not found.
      - name: sub_region
        data_type: VARCHAR
        description: Sub-region from country_codes for the matched country; null if not found.
      - name: source_relation
        data_type: VARCHAR
        description: Source system identifier from the reporting grain; part of the join keys.
      - name: active_free_trial_introductory_offer_subscriptions
        data_type: HUGEINT
        description: Count of active subscriptions on introductory free trials from subscription_summary; zero when missing.
        tests:
        - active_free_trial_introductory_offer_subscriptions >= 0
      - name: active_pay_as_you_go_introductory_offer_subscriptions
        data_type: HUGEINT
        description: Count of active subscriptions on pay-as-you-go introductory offers from subscription_summary; zero when missing.
        tests:
        - active_pay_as_you_go_introductory_offer_subscriptions >= 0
      - name: active_pay_up_front_introductory_offer_subscriptions
        data_type: HUGEINT
        description: Count of active subscriptions on pay-up-front introductory offers from subscription_summary; zero when missing.
        tests:
        - active_pay_up_front_introductory_offer_subscriptions >= 0
      - name: active_standard_price_subscriptions
        data_type: HUGEINT
        description: Count of active subscriptions at standard price from subscription_summary; zero when missing.
        tests:
        - active_standard_price_subscriptions >= 0
      - name: event_renew
        data_type: HUGEINT
        description: Renewal event count from subscription_events; zero when missing.
        tests:
        - event_renew >= 0
      - name: event_cancel
        data_type: HUGEINT
        description: Cancel event count from subscription_events; zero when missing.
        tests:
        - event_cancel >= 0
      - name: event_subscribe
        data_type: HUGEINT
        description: Subscribe event count from subscription_events; zero when missing.
        tests:
        - event_subscribe >= 0
```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-019_apple_store__subscription_report.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-019_apple_store__subscription_report.md:121)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-019_apple_store__subscription_report.md:278)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-019_apple_store__subscription_report.md:316)
- [重跑 summary_null_join](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-019_apple_store__subscription_report.md:351)
- [重跑 event_null_join](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-019_apple_store__subscription_report.md:393)
