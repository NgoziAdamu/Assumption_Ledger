# DAComp / impl-005_stg_google_ads__ad_group_stats（v3）

## 错在哪里
campaign来源列选择导致9985行键不同；契约和可见关联数据均未明确应选base还是直接campaign。

证据复用入口：[018_impl-005_stg_google_ads__ad_group_stats.md](../018_annotations/018_impl-005_stg_google_ads__ad_group_stats.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## campaign_source
- 角色：主要；类别：**Unstated Choice**；把握：中。
- 依据：两个候选均关联campaign_history各10000行；父表一致仅11/14对，不能据gold选择确立映射。19985→10000行，L2匹配。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 14 / content：
```text
None, None), ('base_ad_group', 'VARCHAR', 'YES', None, None, None), ('campaign_base_campaign', 'VARCHAR', 'YES', None, None, None), ('campaign_id', 'VARCHAR', 'YES', None, None, None), ('clicks', 'BIGINT', 'YES', None, None, None), ('conversions', 'DOUBLE', 'YES', None, None, None), ('conversions_value', 'DOUBLE', 'YES', None, None, None), ('cost_micros', 'BIGINT', 'YES', None, None, None), ('device', 'VARCHAR', 'YES', None, None, None), ('id', 'BIGINT', 'YES', None, None, None), ('impressions', 'BIGINT', 'YES', None, None, None), ('interaction_event_types', 'VARCHAR', 'YES', None, None, None), ('interactions', 'BIGINT', 'YES', None, None, None), ('view_through_conversions', 'BIGINT', 'YES', None, None, None)]
[('ACC61393167557', '2022-04-23 00:00:00.000 +0800', 199, 0.829, 11046500, 239, 0.377, 'MIXED', 'AD_96523691001', 'CAM94269068771', 'CAM15753005768', 5, 0.4, 52.66, 21330460, 'TABLET', 9860686206, 532
```

## 规模、证据复用与新做
主要原因：Unstated Choice。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-005_stg_google_ads__ad_group_stats.md](../018_annotations/018_impl-005_stg_google_ads__ad_group_stats.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_google_ads__ad_group_stats
      description: "Cleaned and validated ad group performance statistics"
      source_table: "raw.ad_group_stats_data"
      columns:
        - name: source_relation
          data_type: VARCHAR(100)
        - name: account_id
          data_type: VARCHAR(20)
          constraints: [not_null]
        - name: date_day
          data_type: DATE
          constraints: [not_null]
        - name: ad_group_id
          data_type: VARCHAR(20)
          constraints: [not_null]
        - name: campaign_id
          data_type: VARCHAR(20)
          constraints: [not_null]
        - name: ad_network_type
          data_type: VARCHAR(20)
          validation_rules:
            - rule: "ad_network_type IN ('SEARCH', 'DISPLAY', 'MIXED', 'YOUTUBE')"
              on_failure: nullify_field
        - name: device
          data_type: VARCHAR(20)
        - name: clicks
          data_type: BIGINT
        - name: spend
          data_type: DECIMAL(15,2)
        - name: impressions
          data_type: BIGINT
        - name: conversions
          data_type: DECIMAL(10,2)
        - name: conversions_value
          data_type: DECIMAL(15,2)
        - name: view_through_conversions
          data_type: BIGINT

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-005_stg_google_ads__ad_group_stats.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-005_stg_google_ads__ad_group_stats.md:70)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-005_stg_google_ads__ad_group_stats.md:416)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-005_stg_google_ads__ad_group_stats.md:451)
- [重跑 campaign_source](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-005_stg_google_ads__ad_group_stats.md:481)
- [重跑 spend_type](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-005_stg_google_ads__ad_group_stats.md:518)
- [重跑 conversions_type](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-005_stg_google_ads__ad_group_stats.md:555)
- [重跑 value_type](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-005_stg_google_ads__ad_group_stats.md:592)
