# DAComp / impl-007_stg_apple_store__sales_subscription_event_summary（v3）

## 错在哪里
subscriber_id选vendor ID而gold选促销ID，700行键全不同；另有568行marketing duration选了另一字段。

证据复用入口：[018_impl-007_stg_apple_store__sales_subscription_event_summary.md](../018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## subscriber_source
- 角色：主要；类别：**Unstated Choice**；把握：中。
- 依据：subscriber_id未规定vendor或促销来源，1400键不相交；单改剩568行。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 65 / args.command：
```text
Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。若这类字段用于正式订阅财务决策，应以源端字段定义进一步确认。
```
## marketing_source
- 角色：非原因；类别：**Unstated Choice**；把握：中。
- 依据：marketing字段来源未定；单改键仍不相交，行规模不减。存在未确立的前提，但不是判错原因。
- 是否说出：没有迹象。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。

## 规模、证据复用与新做
主要原因：Unstated Choice。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-007_stg_apple_store__sales_subscription_event_summary.md](../018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_apple_store__sales_subscription_event_summary
      description: "Subscription event summary from Apple Store Connect"
      source_table: "raw.sales_subscription_event_summary"
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: date_day
          data_type: DATE
        - name: app_id
          data_type: VARCHAR
        - name: app_name
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: subscription_name
          data_type: VARCHAR
        - name: event_type
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: subscriber_id
          data_type: VARCHAR
        - name: standard_subscription_duration
          data_type: VARCHAR
        - name: proceeds_reason
          data_type: VARCHAR
        - name: marketing_opt_in_duration
          data_type: VARCHAR
        - name: consecutive_paid_periods
          data_type: BIGINT
        - name: quantity
          data_type: BIGINT

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md:65)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md:266)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md:300)
- [重跑 subscriber_source](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md:330)
- [重跑 marketing_source](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md:367)
- [重跑 source_relation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-007_stg_apple_store__sales_subscription_event_summary.md:404)
