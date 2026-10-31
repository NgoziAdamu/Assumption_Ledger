# DAComp / impl-028_stg_youtube__channel_demographics（v3）

## 错在哪里
agent/初始只有youtube_channel_demographics_data的2509行，gold另用channel_demographics_a_1的9450行，原始内容不相交。

证据复用入口：[018_impl-028_stg_youtube__channel_demographics.md](../018_annotations/018_impl-028_stg_youtube__channel_demographics.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## raw_input_mismatch
- 角色：主要；类别：**不可评估**；把握：中。
- 依据：agent=初始2509行，gold另表9450行；7业务列多重集合完全不相交。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 22 / content：
```text
, None, 'YES', 'NO', None, None), ('youtube_analytics_start', 'raw', 'youtube_channel_demographics_data', 'BASE TABLE', None, None, None, None, None, 'YES', 'NO', None, None), ('youtube_analytics_start', 'raw', 'youtube_video_data', 'BASE TABLE', None, None, None, None, None, 'YES', 'NO', None, None)]
[('youtube_analytics_start', 20645, '/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics_start.duckdb', None, {'storage_version': 'v1.0.0+'}, False, 'duckdb', True, False, None, {}), ('system', 0, None, None, {}, True, 'duckdb', False, False, None, {}), ('temp', 22065, None, None, {}, True, 'duckdb', False, False, None, {})]
sql:
total 20
drwxr-xr-x 5 katherine katherine 4096 Oct 17 17:41 .
drwxr-xr-x 8 katherine katherine 4096 Oct 25 05:53 ..
drwxr-xr-x 2 katherine katherine 4096 Oct 17 17:41 intermediate
drwxr-xr-x 2 katherine katherine 4096 Oct 17 17:41
```

## 规模、证据复用与新做
主要原因：不可评估。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-028_stg_youtube__channel_demographics.md](../018_annotations/018_impl-028_stg_youtube__channel_demographics.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_youtube__channel_demographics
      description: "Cleaned per-video demographics (age, gender, geography). Percentages normalized to [0,1]; identifiers validated; categories enforced."
      source_table: raw.channel_demographics_a_1
      columns:
        - name: date_day
          data_type: DATE
          validation_rules:
            - rule: "date_day IS NOT NULL"
              on_failure: delete_row
        - name: channel_id
          data_type: VARCHAR
          validation_rules:
            - rule: "channel_id IS NULL OR (LENGTH(TRIM(channel_id)) BETWEEN 12 AND 40)"
              on_failure: nullify_field
            - rule: "channel_id = TRIM(channel_id)"
              on_failure: correct
        - name: video_id
          data_type: VARCHAR
          validation_rules:
            - rule: "video_id IS NULL OR (LENGTH(TRIM(video_id)) BETWEEN 8 AND 20)"
              on_failure: nullify_field
            - rule: "video_id = TRIM(video_id)"
              on_failure: correct
        - name: country_code
          data_type: VARCHAR
          validation_rules:
            - rule: "country_code IS NULL OR country_code = UPPER(TRIM(country_code))"
              on_failure: correct
        - name: age_group
          data_type: VARCHAR
          validation_rules:
            - rule: "age_group IN ('13-17','18-24','25-34','35-44','45-54','55-64','65-')"
              on_failure: nullify_field
        - name: gender
          data_type: VARCHAR
          validation_rules:
            - rule: "gender IN ('female','male','user_specified')"
              on_failure: nullify_field
        - name: views_percentage
          data_type: DECIMAL(5,4)
          validation_rules:
            - rule: "views_percentage BETWEEN 0 AND 1"
              on_failure: nullify_field
        - name: _fivetran_synced
          data_type: TIMESTAMP
          validation_rules:
            - rule: "_fivetran_synced IS NULL OR _fivetran_synced <= CURRENT_TIMESTAMP"
              on_failure: nullify_field
        - name: source_relation
          data_type: VARCHAR

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-028_stg_youtube__channel_demographics.md:29)
- [SQL定位](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-028_stg_youtube__channel_demographics.md:84)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-028_stg_youtube__channel_demographics.md:525)
