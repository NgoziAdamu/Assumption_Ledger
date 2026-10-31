# DAComp / impl-025_stg_twilio__call（v3）

## 错在哪里
电话格式失败本应置NULL，agent先去符号并补+1再验证，两个电话列保留了gold置空的值。

证据复用入口：[018_impl-025_stg_twilio__call.md](../018_annotations/018_impl-025_stg_twilio__call.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## contact_phone_no_repair
- 角色：主要；类别：**Intent Misreading**；把握：中。
- 依据：明确格式失败nullify_field，agent先去符号补国家码；2492→2482行。
- 是否说出：只有通用策略说明。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/017_trace_impl-025.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 41 / args.final_thought：
```text
依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。
```
## user_phone_no_repair
- 角色：参与；类别：**Intent Misreading**；把握：中。
- 依据：同一策略用于另一独立列；2492→2483行。
- 是否说出：只有通用策略说明。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/017_trace_impl-025.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 41 / args.final_thought：
```text
依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。
```

## 规模、证据复用与新做
主要原因：Intent Misreading。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-025_stg_twilio__call.md](../018_annotations/018_impl-025_stg_twilio__call.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_twilio__call
      description: "Validated call records with standardized phone fields, temporal integrity, and derived metrics (types per current implementation)."
      source_table: raw.twilio_call_data
      columns:
        - name: account_id
          data_type: VARCHAR
        - name: annotation
          data_type: VARCHAR
        - name: answered_by
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]
          validation_rules:
            - rule: "created_at <= CURRENT_TIMESTAMP"
              on_failure: delete_row
        - name: direction
          data_type: VARCHAR
        - name: call_duration_s
          data_type: INTEGER
          description: "Derived from raw duration in seconds; NULL when missing."
        - name: call_ended_at
          data_type: TIMESTAMP
        - name: call_started_at
          data_type: TIMESTAMP
        - name: call_id
          data_type: VARCHAR
        - name: caller_name
          data_type: VARCHAR
          validation_rules:
            - rule: "caller_name = TRIM(caller_name)"
              on_failure: correct
            - rule: "caller_name RLIKE '^[A-Za-z0-9\\s._-]*$'"
              on_failure: nullify_field
            - rule: "LENGTH(caller_name) <= 50"
              on_failure: nullify_field
        - name: forwarded_from
          data_type: VARCHAR
        - name: group_id
          data_type: VARCHAR
        - name: parent_call_id
          data_type: VARCHAR
        - name: raw_price
          data_type: DOUBLE
          description: "Raw price as floating-point per current implementation."
        - name: price_unit
          data_type: VARCHAR
        - name: user_phone_number
          data_type: VARCHAR
          validation_rules:
            - rule: "user_phone_number RLIKE '^\\+1[0-9]{10}$'"
              on_failure: nullify_field
        - name: contact_phone_number
          data_type: VARCHAR
          validation_rules:
            - rule: "contact_phone_number RLIKE '^\\+1[0-9]{10}$'"
              on_failure: nullify_field
        - name: status
          data_type: VARCHAR
          validation_rules:
            - rule: "status IN ('queued','ringing','in-progress','completed','failed','busy','no-answer','canceled')"
              on_failure: nullify_field
        - name: updated_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "updated_at IS NULL OR updated_at >= created_at"
              on_failure: delete_row
        - name: price_in_usd
          data_type: DOUBLE
          description: "Normalized USD price computed as floating-point per current implementation."
        - name: start_date
          data_type: DATE
        - name: has_talked
          data_type: BOOLEAN
          description: "True when duration indicates any talk time; otherwise NULL."

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-025_stg_twilio__call.md:31)
- [SQL定位](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-025_stg_twilio__call.md:111)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-025_stg_twilio__call.md:354)
- [重跑 user_phone_no_repair](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-025_stg_twilio__call.md:389)
- [重跑 contact_phone_no_repair](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-025_stg_twilio__call.md:431)
