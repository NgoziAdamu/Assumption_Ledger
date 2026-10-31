# DAComp / impl-021_int_klaviyo__person_metrics（v3）

## 错在哪里
date spine连接同一天多条事件后被放大，count(*)减去去重事件日数把两个本应为0的missing_day_count算成1。

证据复用入口：[018_impl-021_int_klaviyo__person_metrics.md](../018_annotations/018_impl-021_int_klaviyo__person_metrics.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## spine_days_count
- 角色：主要；类别：**Intent Misreading**；把握：中。
- 依据：规格明确missing_day_count equals the number of spine days that have no events on that exact date; multiple events on a day do not change this count。count(*)减distinct事件日违背指标定义；SQL第7行，2行2格→0。
- 是否说出：只有通用策略说明。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/017_trace_impl-021.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 41 / args.final_thought：
```text
事件 attribution 解析按契约优先级提取 JSON 子事件 ID，查找限定同一 `source_relation`；事件重复保留且照常计数。
```

## 规模、证据复用与新做
主要原因：Intent Misreading。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-021_int_klaviyo__person_metrics.md](../018_annotations/018_impl-021_int_klaviyo__person_metrics.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: int_klaviyo__person_metrics
      description: Per-person metrics from Klaviyo events including activity windows, continuity diagnostics, event counts, revenue sums, and conversion rates
      grain: One row per person_id per source_relation
      source_models:
      - staging.stg_klaviyo__event
      business_logic: '- Inputs: person_id, source_relation, occurred_at (timestamp), type (event name), numeric_value. - Event normalization: - occurred_on is the calendar date of occurred_at (time removed). If occurred_at is NULL, occurred_on is NULL. - Event type matching is case-insensitive exact string comparison; spacing and punctuation are not altered. - Activity span per person_id + source_relation: - first_event_on is the earliest occurred_on date; last_event_on is the latest. Both are NULL when all occurred_on are NULL. - Date spine and continuity: - Build an inclusive list of every calendar day from first_event_on through last_event_on for each person_id + source_relation. - missing_day_count equals the number of spine days that have no events on that exact date; multiple events on a day do not change this count; set to NULL when the span is undefined. - Aggregations per person_id + source_relation: - Revenue sums: For the listed revenue types, sum numeric_value; treat NULL numeric_value as 0; retain negative values. - Event counts: Count every event whose type matches the listed name; events with NULL type do not match. - Active periods: Count distinct calendar days, distinct Monday-based calendar weeks, and distinct calendar months with at least one event; NULL dates are ignored. - Conversion rates: - Divide the specified numerator by its denominator; return NULL when the denominator is zero; computed with floating-point division and not rounded. - Output includes one row for each (person_id, source_relation) present in the events.'
      columns:
      - name: person_id
        data_type: VARCHAR
        description: Unique person identifier
        tests:
        - not_null
      - name: source_relation
        data_type: VARCHAR
        description: Event source identifier; with person_id defines the row
        tests:
        - not_null
      - name: first_event_on
        data_type: DATE
        description: Earliest event date for the person and source; NULL when no dated events
      - name: last_event_on
        data_type: DATE
        description: Latest event date for the person and source; NULL when no dated events
      - name: sum_revenue_refunded_order
        data_type: DOUBLE
        description: Total numeric_value for 'refunded order' events; NULL numeric_value counts as 0; negatives kept
      - name: sum_revenue_placed_order
        data_type: DOUBLE
        description: Total numeric_value for 'placed order' events; NULL numeric_value counts as 0; negatives kept
      - name: sum_revenue_ordered_product
        data_type: DOUBLE
        description: Total numeric_value for 'ordered product' events; NULL numeric_value counts as 0; negatives kept
      - name: sum_revenue_cancelled_order
        data_type: DOUBLE
        description: Total numeric_value for 'cancelled order' events; NULL numeric_value counts as 0; negatives kept
      - name: count_active_on_site
        data_type: HUGEINT
        description: Number of 'active on site' events
      - name: count_viewed_product
        data_type: HUGEINT
        description: Number of 'viewed product' events
      - name: count_ordered_product
        data_type: HUGEINT
        description: Number of 'ordered product' events
      - name: count_placed_order
        data_type: HUGEINT
        description: Number of 'placed order' events
      - name: count_refunded_order
        data_type: HUGEINT
        description: Number of 'refunded order' events
      - name: count_received_email
        data_type: HUGEINT
        description: Number of 'received email' events
      - name: count_clicked_email
        data_type: HUGEINT
        description: Number of 'clicked email' events
      - name: count_opened_email
        data_type: HUGEINT
        description: Number of 'opened email' events
      - name: count_marked_email_as_spam
        data_type: HUGEINT
        description: Number of 'marked email as spam' events
      - name: count_unsubscribed
        data_type: HUGEINT
        description: Number of 'unsubscribed' events
      - name: count_received_sms
        data_type: HUGEINT
        description: Number of 'received sms' events
      - name: count_clicked_sms
        data_type: HUGEINT
        description: Number of 'clicked sms' events
      - name: count_sent_sms
        data_type: HUGEINT
        description: Number of 'sent sms' events
      - name: count_unsubscribed_from_sms
        data_type: HUGEINT
        description: Number of 'unsubscribed from sms' events
      - name: active_days
        data_type: BIGINT
        description: Distinct calendar days with at least one event
      - name: active_weeks
        data_type: BIGINT
        description: Distinct Monday-based calendar weeks with at least one event
      - name: active_months
        data_type: BIGINT
        description: Distinct calendar months with at least one event
      - name: missing_day_count
        data_type: BIGINT
        description: Number of inclusive-span days with zero events; NULL when the span is undefined
      - name: email_open_rate
        data_type: DOUBLE
        description: Opens divided by received emails; NULL when denominator is 0; floating-point, not rounded
      - name: email_click_to_open_rate
        data_type: DOUBLE
        description: Clicks divided by opens; NULL when denominator is 0; floating-point, not rounded
      - name: product_view_to_order_rate
        data_type: DOUBLE
        description: Orders divided by product views; NULL when denominator is 0; floating-point, not rounded
      - name: site_to_order_rate
        data_type: DOUBLE
        description: Placed orders divided by site activity events; NULL when denominator is 0; floating-point, not rounded
```

## 规则问题

旧U可读为连接不扩行的数据前提；但契约明确规定missing_day_count怎么算以及multiple events do not change this count。依v3规定做法优先，选Intent，而非机械U→Data。

## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-021_int_klaviyo__person_metrics.md:29)
- [SQL定位](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-021_int_klaviyo__person_metrics.md:135)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-021_int_klaviyo__person_metrics.md:518)
- [重跑 missing_count](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-021_int_klaviyo__person_metrics.md:559)
- [重跑 spine_days_count](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-021_int_klaviyo__person_metrics.md:607)
