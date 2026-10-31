# DAComp / impl-009_stg_google_play__store_performance_country（v3）

## 错在哪里
把数值country_region翻译为alpha-2且lookup非唯一，将6400行扩成8800行；契约未规定country编码体系。

证据复用入口：[018_impl-009_stg_google_play__store_performance_country.md](../018_annotations/018_impl-009_stg_google_play__store_performance_country.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## country_value_only
- 角色：主要；类别：**Unstated Choice**；把握：中。
- 依据：country VARCHAR未规定编码；只改输出country保留JOIN，15200→2400行。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 14 / content：
```text
 None, None), ('package_name', 'VARCHAR', 'YES', None, None, None), ('country_region', 'BIGINT', 'YES', None, None, None), ('store_listing_acquisitions', 'BIGINT', 'YES', None, None, None), ('store_listing_visitors', 'BIGINT', 'YES', None, None, None), ('store_listing_conversion_rate', 'DOUBLE', 'YES', None, None, None)]
('store_performance_com.example.gameapp_US_202001_country.csv', 851, '2025-09-05 20:27:58.819 +0800', '2020-01-01 00:00:00.000 +0800', 'com.example.gameapp', 840, 1149, 7515, 0.153)

 stats_store_performance_traffic_source [('_file', 'VARCHAR', 'YES', None, None, None), ('_line', 'DOUBLE', 'YES', None, None, None), ('_modified', 'VARCHAR', 'YES', None, None, None), ('date', 'VARCHAR', 'YES', None, None, None), ('package_name', 'VARCHAR', 'YES', None, None, None), ('traffic_source', 'VARCHAR', 'YES', None, None, None), ('store_listing_acquisitions', 'BIGINT', 'YES', None, None, None), ('stor
```
## lookup_dedup
- 角色：参与；类别：**Data Misconception**；把握：中。
- 依据：P：lookup数值国家码唯一。250行只有246个码，4码各两条；单独去重15200→12800行。
- 是否说出：看到了但没提。
- 证据在场：否；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/014_trace_impl-009.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
实际可见列名/通用输出不能单凭它确定匹配或唯一性；核实查询为标注者事后执行。
event 14 / content：
```text
 None, None), ('package_name', 'VARCHAR', 'YES', None, None, None), ('country_region', 'BIGINT', 'YES', None, None, None), ('store_listing_acquisitions', 'BIGINT', 'YES', None, None, None), ('store_listing_visitors', 'BIGINT', 'YES', None, None, None), ('store_listing_conversion_rate', 'DOUBLE', 'YES', None, None, None)]
('store_performance_com.example.gameapp_US_202001_country.csv', 851, '2025-09-05 20:27:58.819 +0800', '2020-01-01 00:00:00.000 +0800', 'com.example.gameapp', 840, 1149, 7515, 0.153)

 stats_store_performance_traffic_source [('_file', 'VARCHAR', 'YES', None, None, None), ('_line', 'DOUBLE', 'YES', None, None, None), ('_modified', 'VARCHAR', 'YES', None, None, None), ('date', 'VARCHAR', 'YES', None, None, None), ('package_name', 'VARCHAR', 'YES', None, None, None), ('traffic_source', 'VARCHAR', 'YES', None, None, None), ('store_listing_acquisitions', 'BIGINT', 'YES', None, None, None), ('stor
```
四档引句为关联证据；本处可见性另按在场栏判断，未将通用策略算成具体披露。

## 规模、证据复用与新做
主要原因：Unstated Choice。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-009_stg_google_play__store_performance_country.md](../018_annotations/018_impl-009_stg_google_play__store_performance_country.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_google_play__store_performance_country
      description: "Store performance metrics by country"
      source_table: "raw.stats_store_performance_country"
      columns:
        - name: date_day
          data_type: DATE
          constraints: [not_null]
        - name: package_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: country
          data_type: VARCHAR
          constraints: [not_null]
        - name: store_listing_visitors
          data_type: INTEGER
        - name: store_listing_conversion_rate
          data_type: DECIMAL(18,3)
        - name: store_listing_installers
          data_type: INTEGER
        - name: _fivetran_synced
          data_type: VARCHAR

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-009_stg_google_play__store_performance_country.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-009_stg_google_play__store_performance_country.md:54)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-009_stg_google_play__store_performance_country.md:370)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-009_stg_google_play__store_performance_country.md:397)
- [重跑 remove_country_translation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-009_stg_google_play__store_performance_country.md:420)
- [重跑 country_value_only](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-009_stg_google_play__store_performance_country.md:460)
- [重跑 unique_lookup](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-009_stg_google_play__store_performance_country.md:490)
