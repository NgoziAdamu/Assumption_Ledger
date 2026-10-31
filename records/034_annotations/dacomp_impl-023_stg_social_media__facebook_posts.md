# DAComp / impl-023_stg_social_media__facebook_posts（v3）

## 错在哪里
两种未指定的Facebook URL路由不同，另有契约BIGINT与gold DOUBLE表示差异，各138格并列。

证据复用入口：[018_impl-023_stg_social_media__facebook_posts.md](../018_annotations/018_impl-023_stg_social_media__facebook_posts.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## url_route
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：URL只规定前缀，两种路由都满足；单改276→138格。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 24 / content：
```text
one), ('post_video_views_15_s', 'BIGINT', 'YES', None, None, None)]

 facebook_pages_page_data
[('id', 'BIGINT', 'YES', None, None, None), ('_fivetran_deleted', 'BOOLEAN', 'YES', None, None, None), ('_fivetran_synced', 'TIMESTAMP', 'YES', None, None, None), ('affiliation', 'VARCHAR', 'YES', None, None, None), ('app_id', 'VARCHAR', 'YES', None, None, None), ('artists_we_like', 'VARCHAR', 'YES', None, None, None), ('attire', 'VARCHAR', 'YES', None, None, None), ('awards', 'VARCHAR', 'YES', None, None, None), ('band_interests', 'VARCHAR', 'YES', None, None, None), ('band_members', 'VARCHAR', 'YES', None, None, None), ('bio', 'VARCHAR', 'YES', None, None, None), ('birthday', 'VARCHAR', 'YES', None, None, None), ('booking_agent', 'VARCHAR', 'YES', None, None, None), ('built', 'VARCHAR', 'YES', None, None, None), ('can_checkin', 'BOOLEAN', 'YES', None, None, None), ('can_post', 'BOOLEAN', 'YES', None, None, None)
```
## followers_representation
- 角色：并列；类别：**其他**；把握：中。
- 依据：规格BIGINT，agent遵守，gold DOUBLE；单改276→138格，L1表示归一已消除。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 24 / content：
```text
, None, None, None), ('emails', 'VARCHAR', 'YES', None, None, None), ('fan_count', 'DOUBLE', 'YES', None, None, None), ('features', 'VARCHAR', 'YES', None, None, None), ('food_styles', 'VARCHAR', 'YES', None, None, None), ('founded', 'VARCHAR', 'YES', None, None, None), ('general_info', 'VARCHAR', 'YES', None, None, None), ('general_manager', 'VARCHAR', 'YES', None, None, None), ('genre', 'VARCHAR', 'YES', None, None, None), ('global_brand_page_name', 'VARCHAR', 'YES', None, None, None), ('has_added_app', 'VARCHAR', 'YES', None, None, None), ('has_whatsapp_number', 'VARCHAR', 'YES', None, None, None), ('hometown', 'VARCHAR', 'YES', None, None, None), ('impressum', 'VARCHAR', 'YES', None, None, None), ('influences', 'VARCHAR', 'YES', None, None, None), ('is_always_open', 'BOOLEAN', 'YES', None, None, None), ('is_chain', 'VARCHAR', 'YES', None, None, None), ('is_community_page', 'BOOLEAN', 'YES', None, None,
```

## 规模、证据复用与新做
主要原因：多因并列。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-023_stg_social_media__facebook_posts.md](../018_annotations/018_impl-023_stg_social_media__facebook_posts.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_social_media__facebook_posts
      description: "Published, visible Facebook posts joined to page info, standardized fields for analysis; recent 2-year window."
      source_table:
        - raw.facebook_pages_post_history
        - raw.facebook_pages_page_data
      columns:
        - name: id
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
          description: "From created_time."
        - name: post_id
          data_type: VARCHAR
          description: "CAST(id)."
        - name: post_message
          data_type: VARCHAR
          description: "COALESCE(message, '')."
        - name: page_id
          data_type: VARCHAR
          description: "CAST(page_id)."
        - name: page_name
          data_type: VARCHAR
          validation_rules:
            - rule: "page_name IS NOT NULL AND page_name <> ''"
              on_failure: correct
          description: "Defaults to 'Unknown Page' when page name is missing."
        - name: page_username
          data_type: VARCHAR
        - name: page_category
          data_type: VARCHAR
        - name: page_followers
          data_type: BIGINT
        - name: shares
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
          description: "Default 0 in staging."
        - name: status_type
          data_type: VARCHAR
        - name: privacy_value
          data_type: VARCHAR
        - name: is_eligible_for_promotion
          data_type: BOOLEAN
        - name: is_instagram_eligible
          data_type: BOOLEAN
        - name: post_url
          data_type: VARCHAR
          validation_rules:
            - rule: "post_url ~ '^https://facebook\\.com/.+'"
              on_failure: correct

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-023_stg_social_media__facebook_posts.md:29)
- [SQL定位](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-023_stg_social_media__facebook_posts.md:84)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-023_stg_social_media__facebook_posts.md:310)
- [重跑 url_route](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-023_stg_social_media__facebook_posts.md:344)
- [重跑 followers_representation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-023_stg_social_media__facebook_posts.md:385)
- [重跑 impressions_default](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-023_stg_social_media__facebook_posts.md:426)
