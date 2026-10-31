# DAComp / impl-002_stg_pendo__guide_event（v3）

## 错在哪里
URL校验遗漏与未规定的hash公式各造成15000格差异，并列主因；另有13655个超界纬度。

证据复用入口：[018_impl-002_stg_pendo__guide_event.md](../018_annotations/018_impl-002_stg_pendo__guide_event.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## key_formula
- 角色：并列；类别：**Unstated Choice**；把握：中。
- 依据：Generated surrogate key 未规定拼接算法；15000行不降，格子43655→28655。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 14 / content：
```text
', None, None, None), ('name', 'VARCHAR', 'YES', None, None, None)]

 guide_event [('account_id', 'VARCHAR', 'YES', None, None, None), ('guide_id', 'VARCHAR', 'YES', None, None, None), ('remote_ip', 'VARCHAR', 'YES', None, None, None), ('server_name', 'VARCHAR', 'YES', None, None, None), ('timestamp', 'VARCHAR', 'YES', None, None, None), ('user_agent', 'VARCHAR', 'YES', None, None, None), ('visitor_id', 'VARCHAR', 'YES', None, None, None), ('app_id', 'VARCHAR', 'YES', None, None, None), ('country', 'VARCHAR', 'YES', None, None, None), ('element_path', 'VARCHAR', 'YES', None, None, None), ('event_id', 'BIGINT', 'YES', None, None, None), ('guide_step_id', 'BIGINT', 'YES', None, None, None), ('latitude', 'DOUBLE', 'YES', None, None, None), ('load_time', 'VARCHAR', 'YES', None, None, None), ('longitude', 'DOUBLE', 'YES', None, None, None), ('region', 'VARCHAR', 'YES', None, None, None), ('type', 'VARCHAR', 'YES
```
## url_rule
- 角色：并列；类别：**Intent Misreading**；把握：中。
- 依据：规格 url IS NULL OR url ~ '^https?://' 可执行；agent只trim，15000格差异。不是对现实URL有效性的判断。
- 是否说出：只有通用策略说明。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/014_trace_impl-002.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 59 / args.final_thought：
```text
Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.
```
## latitude_range
- 角色：参与；类别：**Data Misconception**；把握：中。
- 依据：P：latitude均在±90内。已有核实查询反证13655个超界值；单改减少13655格。
- 是否说出：看到了但没提。
- 证据在场：否；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/014_trace_impl-002.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
实际可见列名/通用输出不能单凭它确定匹配或唯一性；核实查询为标注者事后执行。
event 14 / content：
```text
', None, None, None), ('name', 'VARCHAR', 'YES', None, None, None)]

 guide_event [('account_id', 'VARCHAR', 'YES', None, None, None), ('guide_id', 'VARCHAR', 'YES', None, None, None), ('remote_ip', 'VARCHAR', 'YES', None, None, None), ('server_name', 'VARCHAR', 'YES', None, None, None), ('timestamp', 'VARCHAR', 'YES', None, None, None), ('user_agent', 'VARCHAR', 'YES', None, None, None), ('visitor_id', 'VARCHAR', 'YES', None, None, None), ('app_id', 'VARCHAR', 'YES', None, None, None), ('country', 'VARCHAR', 'YES', None, None, None), ('element_path', 'VARCHAR', 'YES', None, None, None), ('event_id', 'BIGINT', 'YES', None, None, None), ('guide_step_id', 'BIGINT', 'YES', None, None, None), ('latitude', 'DOUBLE', 'YES', None, None, None), ('load_time', 'VARCHAR', 'YES', None, None, None), ('longitude', 'DOUBLE', 'YES', None, None, None), ('region', 'VARCHAR', 'YES', None, None, None), ('type', 'VARCHAR', 'YES
```
四档引句为关联证据；本处可见性另按在场栏判断，未将通用策略算成具体披露。

## 规模、证据复用与新做
主要原因：多因并列。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-002_stg_pendo__guide_event.md](../018_annotations/018_impl-002_stg_pendo__guide_event.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_pendo__guide_event
      description: "Cleaned guide interaction events with validated guide steps and timing"
      source_table: "raw.guide_event"
      columns:
        - name: account_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: guide_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: remote_ip
          data_type: VARCHAR(255)
          validation_rules:
            - rule: "remote_ip IS NULL OR remote_ip ~ '^([0-9]{1,3}){3}[0-9]{1,3}$' OR remote_ip ~ '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'"
              on_failure: nullify_field
        - name: server_name
          data_type: VARCHAR(255)
        - name: occurred_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: user_agent
          data_type: VARCHAR(255)
        - name: visitor_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: app_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: country
          data_type: VARCHAR(255)
        - name: guide_step_id
          data_type: BIGINT
        - name: latitude
          data_type: DOUBLE
        - name: longitude
          data_type: DOUBLE
          validation_rules:
            - rule: "longitude BETWEEN -180 AND 180 OR longitude IS NULL"
              on_failure: nullify_field
        - name: region
          data_type: VARCHAR(255)
        - name: type
          data_type: VARCHAR(255)
        - name: url
          data_type: VARCHAR(255)
          validation_rules:
            - rule: "url = NULLIF(TRIM(url), '')"
              on_failure: correct
            - rule: "url IS NULL OR url ~ '^https?://'"
              on_failure: nullify_field
        - name: guide_event_key
          data_type: VARCHAR(255)
          description: "Generated surrogate key"

```

## 规则问题

hash改值按Choice，URL可执行正则按Intent，latitude硬约束按Data；单改行都不下降时沿用格子区分，不把全匹配正则失败说成现实URL无效。

## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-002_stg_pendo__guide_event.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-002_stg_pendo__guide_event.md:86)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-002_stg_pendo__guide_event.md:342)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-002_stg_pendo__guide_event.md:379)
- [重跑 key_formula](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-002_stg_pendo__guide_event.md:412)
- [重跑 url_rule](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-002_stg_pendo__guide_event.md:452)
- [重跑 latitude_range](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-002_stg_pendo__guide_event.md:492)
