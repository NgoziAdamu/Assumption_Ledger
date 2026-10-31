# DAComp / impl-006_stg_reddit_ads__campaign_report（v3）

## 错在哪里
20个指标各造成1200格差异：spend候选被覆盖、四个可映射指标直接填NULL，其余为未规定指标口径。

证据复用入口：[018_impl-006_stg_reddit_ads__campaign_report.md](../018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## spend
- 角色：并列；类别：**代码写错**；把握：中。
- 依据：同一映射先含spend候选，后重复键覆盖，已有正确实现意图。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## video_views
- 角色：并列；类别：**Quiet Downgrade**；把握：中。
- 依据：raw有明确候选video_started/comment_upvotes/comment_downvotes/viewer_comments，未逐项判断即填NULL。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## video_view_rate
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## upvotes
- 角色：并列；类别：**Quiet Downgrade**；把握：中。
- 依据：raw有明确候选video_started/comment_upvotes/comment_downvotes/viewer_comments，未逐项判断即填NULL。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## downvotes
- 角色：并列；类别：**Quiet Downgrade**；把握：中。
- 依据：raw有明确候选video_started/comment_upvotes/comment_downvotes/viewer_comments，未逐项判断即填NULL。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## comments
- 角色：并列；类别：**Quiet Downgrade**；把握：中。
- 依据：raw有明确候选video_started/comment_upvotes/comment_downvotes/viewer_comments，未逐项判断即填NULL。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## shares
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## saves
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## post_visits
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## profile_visits
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## community_joins
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## conversions
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## conversion_value
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## cost_per_video_view
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## cost_per_conversion
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## total_engagements
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## engagement_rate
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 97 / args.final_thought：
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```
## click_through_rate
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 18 / content：
```text
, 'comment_upvotes', 'comments_page_views', 'conversion_roas', 'cpc', 'ctr', 'ecpm', 'gallery_item_caption', 'gallery_item_id', 'impressions', 'legacy_click_conversions_attribution_window_day', 'legacy_click_conversions_attribution_window_month', 'legacy_click_conversions_attribution_window_week', 'legacy_view_conversions_attribution_window_day', 'legacy_view_conversions_attribution_window_month', 'legacy_view_conversions_attribution_window_week', 'priority', 'region', 'spend', 'video_fully_viewable_impressions', 'video_plays_expanded', 'video_plays_with_sound', 'video_started', 'video_viewable_impressions', 'video_watched_100_percent', 'video_watched_10_seconds', 'video_watched_25_percent', 'video_watched_3_seconds', 'video_watched_50_percent', 'video_watched_5_seconds', 'video_watched_75_percent', 'video_watched_95_percent', 'viewable_impressions', 'viewer_comments']
snapchat_campaign_hourly_report_data [
```
## cost_per_click
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 18 / content：
```text
nvotes', 'comment_upvotes', 'comments_page_views', 'conversion_roas', 'cpc', 'ctr', 'ecpm', 'gallery_item_caption', 'gallery_item_id', 'impressions', 'legacy_click_conversions_attribution_window_day', 'legacy_click_conversions_attribution_window_month', 'legacy_click_conversions_attribution_window_week', 'legacy_view_conversions_attribution_window_day', 'legacy_view_conversions_attribution_window_month', 'legacy_view_conversions_attribution_window_week', 'priority', 'region', 'spend', 'video_fully_viewable_impressions', 'video_plays_expanded', 'video_plays_with_sound', 'video_started', 'video_viewable_impressions', 'video_watched_100_percent', 'video_watched_10_seconds', 'video_watched_25_percent', 'video_watched_3_seconds', 'video_watched_50_percent', 'video_watched_5_seconds', 'video_watched_75_percent', 'video_watched_95_percent', 'viewable_impressions', 'viewer_comments']
snapchat_campaign_hourly_report
```
## cost_per_thousand_impressions
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。单改行均不降，24000格各减少1200。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 18 / content：
```text
ent_upvotes', 'comments_page_views', 'conversion_roas', 'cpc', 'ctr', 'ecpm', 'gallery_item_caption', 'gallery_item_id', 'impressions', 'legacy_click_conversions_attribution_window_day', 'legacy_click_conversions_attribution_window_month', 'legacy_click_conversions_attribution_window_week', 'legacy_view_conversions_attribution_window_day', 'legacy_view_conversions_attribution_window_month', 'legacy_view_conversions_attribution_window_week', 'priority', 'region', 'spend', 'video_fully_viewable_impressions', 'video_plays_expanded', 'video_plays_with_sound', 'video_started', 'video_viewable_impressions', 'video_watched_100_percent', 'video_watched_10_seconds', 'video_watched_25_percent', 'video_watched_3_seconds', 'video_watched_50_percent', 'video_watched_5_seconds', 'video_watched_75_percent', 'video_watched_95_percent', 'viewable_impressions', 'viewer_comments']
snapchat_campaign_hourly_report_data ['campai
```

## 规模、证据复用与新做
主要原因：多因并列。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-006_stg_reddit_ads__campaign_report.md](../018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（复用）

```yaml
    - name: "stg_reddit_ads__campaign_report"
      description: "Staging table for Reddit Ads  Campaign Report"
      columns:
        - name: "platform"
          data_type: VARCHAR
        - name: "campaign_id"
          data_type: VARCHAR
        - name: "date_day"
          data_type: DATE
        - name: "account_id"
          data_type: VARCHAR
        - name: "impressions"
          data_type: INTEGER
        - name: "clicks"
          data_type: INTEGER
        - name: "spend"
          data_type: DECIMAL(18,2)
        - name: "video_views"
          data_type: INTEGER
        - name: "video_view_rate"
          data_type: DECIMAL(8,4)
        - name: "upvotes"
          data_type: INTEGER
        - name: "downvotes"
          data_type: INTEGER
        - name: "comments"
          data_type: INTEGER
        - name: "shares"
          data_type: INTEGER
        - name: "saves"
          data_type: INTEGER
        - name: "post_visits"
          data_type: INTEGER
        - name: "profile_visits"
          data_type: INTEGER
        - name: "community_joins"
          data_type: INTEGER
        - name: "conversions"
          data_type: INTEGER
        - name: "conversion_value"
          data_type: DECIMAL(18,2)
        - name: "click_through_rate"
          data_type: DOUBLE
        - name: "cost_per_click"
          data_type: DOUBLE
        - name: "cost_per_thousand_impressions"
          data_type: DOUBLE
        - name: "cost_per_video_view"
          data_type: DOUBLE
        - name: "cost_per_conversion"
          data_type: DOUBLE
        - name: "total_engagements"
          data_type: INTEGER
        - name: "engagement_rate"
          data_type: DOUBLE
        - name: "_dbt_loaded_at"
          data_type: TIMESTAMP WITH TIME ZONE
```

## 规则问题

总报告typed NULL是通用策略，未点明本指标缺口；不把旧标记已披露自动变成已说出的降级。spend有重复映射覆盖的明确正确意图，先归代码写错。

## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:90)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:529)
- [重跑 spend](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:571)
- [重跑 video_views](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:622)
- [重跑 video_view_rate](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:673)
- [重跑 upvotes](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:724)
- [重跑 downvotes](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:775)
- [重跑 comments](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:826)
- [重跑 shares](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:877)
- [重跑 saves](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:928)
- [重跑 post_visits](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:979)
- [重跑 profile_visits](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1030)
- [重跑 community_joins](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1081)
- [重跑 conversions](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1132)
- [重跑 conversion_value](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1183)
- [重跑 cost_per_video_view](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1234)
- [重跑 cost_per_conversion](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1285)
- [重跑 total_engagements](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1336)
- [重跑 engagement_rate](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1387)
- [重跑 click_through_rate](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1438)
- [重跑 cost_per_click](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1489)
- [重跑 cost_per_thousand_impressions](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-006_stg_reddit_ads__campaign_report.md:1540)
