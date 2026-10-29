# impl-021 / int_klaviyo__person_metrics

## 1. 错在哪里

date spine连接同一天多条事件后被放大，count(*)减去去重事件日数把两个本应为0的missing_day_count算成1。

已核实：CS上游gold中LRqEsZ与MCX88q各有同日2个事件、活动区间仅1天，gold缺失天数均0，agent均1。agent用连接后的count(*)减count(distinct e.occurred_on)，前者为2而后者为1。只把前项改为count(distinct d.day)，或只把后项改为count(e.occurred_on)，两种独立替代修法都L0匹配；主因是依赖连接不扩行的未核实假设。标注者核实agent实际staging中这两个人也各有同日2事件；不是拿CS gold数据反证agent可见的P。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-021_intermediate_int_klaviyo__person_metrics.md)；不修改既有官方判错状态。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml` 第820–920行。
- [完整轨迹](../017_trace_impl-021.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。
- [查询原文及结果](../017_queries_impl-021.json)、[重跑完整记录](../017_reruns_impl-021.json)、[原始表库存](../015_raw_impl-021.json)。
- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。
- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。

### 契约原文

```yaml
    - name: int_klaviyo__person_metrics
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

### SQL定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/intermediate/int_klaviyo__person_metrics.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: with events as (select *, cast(occurred_at as date) occurred_on_calc from staging.stg_klaviyo__event), grouped as (
   2:  select person_id,source_relation,min(coalesce(occurred_on,occurred_on_calc)) first_event_on,max(coalesce(occurred_on,occurred_on_calc)) last_event_on,
   3:  sum(case when lower(type)='refunded order' then coalesce(numeric_value,0) else 0 end)::double as sum_revenue_refunded_order, sum(case when lower(type)='placed order' then coalesce(numeric_value,0) else 0 end)::double as sum_revenue_placed_order, sum(case when lower(type)='ordered product' then coalesce(numeric_value,0) else 0 end)::double as sum_revenue_ordered_product, sum(case when lower(type)='cancelled order' then coalesce(numeric_value,0) else 0 end)::double as sum_revenue_cancelled_order, count(*) filter(where lower(type)='active on site') as count_active_on_site, count(*) filter(where lower(type)='viewed product') as count_viewed_product, count(*) filter(where lower(type)='ordered product') as count_ordered_product, count(*) filter(where lower(type)='placed order') as count_placed_order, count(*) filter(where lower(type)='refunded order') as count_refunded_order, count(*) filter(where lower(type)='received email') as count_received_email, count(*) filter(where lower(type)='clicked email') as count_clicked_email, count(*) filter(where lower(type)='opened email') as count_opened_email, count(*) filter(where lower(type)='marked email as spam') as count_marked_email_as_spam, count(*) filter(where lower(type)='unsubscribed') as count_unsubscribed, count(*) filter(where lower(type)='received sms') as count_received_sms, count(*) filter(where lower(type)='clicked sms') as count_clicked_sms, count(*) filter(where lower(type)='sent sms') as count_sent_sms, count(*) filter(where lower(type)='unsubscribed from sms') as count_unsubscribed_from_sms, count(distinct occurred_on)::bigint as active_days, count(distinct date_trunc('week',occurred_on))::bigint as active_weeks, count(distinct date_trunc('month',occurred_on))::bigint as active_months,
   4:  count(distinct occurred_on) as _active_days, count(distinct date_trunc('week',occurred_on)) as _active_weeks,count(distinct date_trunc('month',occurred_on)) as _active_months
   5:  from events group by person_id,source_relation
   6: ), spine as (
   7:  select g.person_id,g.source_relation,count(*)-count(distinct e.occurred_on) as missing_day_count
   8:  from grouped g cross join lateral generate_series(g.first_event_on,g.last_event_on,interval '1 day') d(day)
   9:  left join events e on e.person_id=g.person_id and e.source_relation=g.source_relation and e.occurred_on=d.day
  10:  group by g.person_id,g.source_relation
  11: )
  12: select g.person_id,g.source_relation,g.first_event_on,g.last_event_on,
  13:  g.sum_revenue_refunded_order, g.sum_revenue_placed_order, g.sum_revenue_ordered_product, g.sum_revenue_cancelled_order, g.count_active_on_site, g.count_viewed_product, g.count_ordered_product, g.count_placed_order, g.count_refunded_order, g.count_received_email, g.count_clicked_email, g.count_opened_email, g.count_marked_email_as_spam, g.count_unsubscribed, g.count_received_sms, g.count_clicked_sms, g.count_sent_sms, g.count_unsubscribed_from_sms,
  14:  g._active_days::bigint active_days,g._active_weeks::bigint active_weeks,g._active_months::bigint active_months,
  15:  s.missing_day_count,
  16:  g.count_opened_email::double/nullif(g.count_received_email,0) email_open_rate,
  17:  g.count_clicked_email::double/nullif(g.count_opened_email,0) email_click_to_open_rate,
  18:  g.count_ordered_product::double/nullif(g.count_viewed_product,0) product_view_to_order_rate,
  19:  g.count_placed_order::double/nullif(g.count_active_on_site,0) site_to_order_rate
  20: from grouped g left join spine s using(person_id,source_relation)
```

gold（仅用于定位差异）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/sql/intermediate/int_klaviyo__person_metrics.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: -- Intermediate: Person-level holistic metrics derived from staging events
   2: -- Adds activity windows and date continuity diagnostics
   3:
   4: with events as (
   5:     select
   6:         e.person_id,
   7:         e.source_relation,
   8:         cast(date_trunc('day', e.occurred_at) as date) as occurred_on,
   9:         e.type,
  10:         e.numeric_value
  11:     from staging.stg_klaviyo__event e
  12: ),
  13: spans as (
  14:     select
  15:         person_id,
  16:         source_relation,
  17:         min(occurred_on) as first_event_on,
  18:         max(occurred_on) as last_event_on
  19:     from events
  20:     group by person_id, source_relation
  21: ),
  22: -- date spine per person to check continuity
  23: spine as (
  24:     select
  25:         s.person_id,
  26:         s.source_relation,
  27:         gs.day::date as day
  28:     from spans s,
  29:     generate_series(s.first_event_on, s.last_event_on, interval 1 day) as gs(day)
  30: ),
  31: missing as (
  32:     select
  33:         sp.person_id,
  34:         sp.source_relation,
  35:         count(*) - count(e.occurred_on) as missing_day_count
  36:     from spine sp
  37:     left join events e
  38:       on sp.person_id = e.person_id and sp.source_relation = e.source_relation and sp.day = e.occurred_on
  39:     group by sp.person_id, sp.source_relation
  40: ),
  41: agg as (
  42:     select
  43:         e.person_id,
  44:         e.source_relation,
  45:         min(e.occurred_on) as first_event_on,
  46:         max(e.occurred_on) as last_event_on,
  47:         -- revenue sums
  48:         sum(case when lower(e.type) = 'refunded order' then coalesce(e.numeric_value,0) else 0 end) as sum_revenue_refunded_order,
  49:         sum(case when lower(e.type) = 'placed order' then coalesce(e.numeric_value,0) else 0 end) as sum_revenue_placed_order,
  50:         sum(case when lower(e.type) = 'ordered product' then coalesce(e.numeric_value,0) else 0 end) as sum_revenue_ordered_product,
  51:         sum(case when lower(e.type) = 'cancelled order' then coalesce(e.numeric_value,0) else 0 end) as sum_revenue_cancelled_order,
  52:         -- counts
  53:         sum(case when lower(e.type) = 'active on site' then 1 else 0 end) as count_active_on_site,
  54:         sum(case when lower(e.type) = 'viewed product' then 1 else 0 end) as count_viewed_product,
  55:         sum(case when lower(e.type) = 'ordered product' then 1 else 0 end) as count_ordered_product,
  56:         sum(case when lower(e.type) = 'placed order' then 1 else 0 end) as count_placed_order,
  57:         sum(case when lower(e.type) = 'refunded order' then 1 else 0 end) as count_refunded_order,
  58:         sum(case when lower(e.type) = 'received email' then 1 else 0 end) as count_received_email,
  59:         sum(case when lower(e.type) = 'clicked email' then 1 else 0 end) as count_clicked_email,
  60:         sum(case when lower(e.type) = 'opened email' then 1 else 0 end) as count_opened_email,
  61:         sum(case when lower(e.type) = 'marked email as spam' then 1 else 0 end) as count_marked_email_as_spam,
  62:         sum(case when lower(e.type) = 'unsubscribed' then 1 else 0 end) as count_unsubscribed,
  63:         sum(case when lower(e.type) = 'received sms' then 1 else 0 end) as count_received_sms,
  64:         sum(case when lower(e.type) = 'clicked sms' then 1 else 0 end) as count_clicked_sms,
  65:         sum(case when lower(e.type) = 'sent sms' then 1 else 0 end) as count_sent_sms,
  66:         sum(case when lower(e.type) = 'unsubscribed from sms' then 1 else 0 end) as count_unsubscribed_from_sms,
  67:         -- distinct active periods
  68:         count(distinct e.occurred_on) as active_days,
  69:         count(distinct date_trunc('week', e.occurred_on)) as active_weeks,
  70:         count(distinct date_trunc('month', e.occurred_on)) as active_months
  71:     from events e
  72:     group by e.person_id, e.source_relation
  73: ),
  74: final as (
  75:     select
  76:         a.*,
  77:         m.missing_day_count,
  78:         -- conversion rates with denominators > 0
  79:         case when a.count_received_email > 0 then a.count_opened_email::double / a.count_received_email else null end as email_open_rate,
  80:         case when a.count_opened_email > 0 then a.count_clicked_email::double / a.count_opened_email else null end as email_click_to_open_rate,
  81:         case when a.count_viewed_product > 0 then a.count_ordered_product::double / a.count_viewed_product else null end as product_view_to_order_rate,
  82:         case when a.count_active_on_site > 0 then a.count_placed_order::double / a.count_active_on_site else null end as site_to_order_rate
  83:     from agg a
  84:     left join missing m on a.person_id = m.person_id and a.source_relation = m.source_relation
  85: )
  86: select * from final
```

### 原始数据可评估性

下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。

|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|
|---|---|---|---|---|---|
|raw.event|gold_vs_initial|False|False|None|ordered_columns_or_types_differ,row_counts_differ|
|raw.event|gold_vs_agent|True|True|True||

## 3. agent看过什么

event1完整契约明确multiple events on a day do not change this count；event11→12看raw schema及每表1行样例，event31→32只DESCRIBE本表和event表；event15写出COUNT表达式。全部43事件未找到(person_id,source_relation,day)重复频数核实。最终event41提过事件重复保留/计数，但未核实或处理本表连接的日粒度放大。

只把归档实际展示的内容视为已看到；磁盘有文件、命令包含表名或截断掉的部分，不等于看到相应数据值。

### 新增字段：是否意识到或提到相关不确定性

**已提到**。只记录可见表述/信息，不由该档位推定错误类别。

提到了共享事件数据的重复保留/计数策略；未讨论本表date spine连接扩行或同人同日多事件如何计算missing_day_count。

event **41**，字段`args.final_thought`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/41.json`。
```text
事件 attribution 解析按契约优先级提取 JSON 子事件 ID，查找限定同一 `source_relation`；事件重复保留且照常计数。
```

event **32**，字段`content`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/32.json`。
```text
staging stg_klaviyo__event [('campaign_id', 'VARCHAR', 'YES', None, None, None), ('flow_id', 'VARCHAR', 'YES', None, None, None), ('variation_id', 'VARCHAR', 'YES', None, None, None), ('flow_message_id', 'VARCHAR', 'YES', None, None, None), ('event_id', 'VARCHAR', 'YES', None, None, None), ('metric_id', 'VARCHAR', 'YES', None, None, None), ('person_id', 'VARCHAR', 'YES', None, None, None), ('type', 'VARCHAR', 'YES', None, None, None), ('uuid', 'VARCHAR', 'YES', None, None, None), ('numeric_value', 'DOUBLE', 'YES', None, None, None), ('event_attribution', 'VARCHAR', 'YES', None, None, None), ('occurred_at', 'TIMESTAMP', 'YES', None, None, None), ('occurred_on', 'DATE', 'YES', None, None, None), ('source_relation', 'VARCHAR', 'YES', None, None, None), ('property_price', 'DOUBLE', 'YES', None, None, None), ('property_compare_at_price', 'DOUBLE', 'YES', None, None, None)]

 staging stg_klaviyo__person [('person_id', 'VARCHAR', 'YES', None, None, None), ('address_1', 'VARCHAR', 'YES', None, None, None), ('address_2', 'VARCHAR', 'YES', None, None, None), ('city', 'VARCHAR', 'YES', None, None, None), ('country', 'VARCHAR', 'YES', None, None, None), ('zip', 'VARCHAR', 'YES', None, None, None), ('created_at', 'TIMESTAMP', 'YES', None, None, None), ('email', 'VARCHAR', 'YES', None, None, None), ('full_name', 'VARCHAR', 'YES', None, None, None), ('latitude', 'DOUBLE', 'YES', None, None, None), ('longitude', 'DOUBLE', 'YES', None, None, None), ('organization', 'VARCHAR', 'YES', None, None, None), ('phone_number', 'VARCHAR', 'YES', None, None, None), ('region', 'VARCHAR', 'YES', None, None, None), ('timezone', 'VARCHAR', 'YES', None, None, None), ('title', 'VARCHAR', 'YES', None, None, None), ('updated_at', 'TIMESTAMP', 'YES', None, None, None), ('last_event_date', 'TIMESTAMP', 'YES', None, None, None), ('source_relation', 'VARCHAR', 'YES', None, None, None)]

 staging stg_klaviyo
```

归档逐项扫描43个事件；本批thought/args.thought字段均为空，不能由此推断agent没有内部思考。“已提到”的原句来自final_thought中的最终报告；“看到了但没提”依据可见工具返回，不把SQL代码本身当口头说明。长工具输出仅摘录连续原文，截取范围见JSON；不是说agent只看到了这个摘录。

## 4. 查询与重跑

核实查询执行 **3条**（失败尝试也计入）；核实代价档：**多条查询**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。

### V1 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。
```sql
SELECT person_id,source_relation,cast(occurred_at AS DATE) day,count(*) n FROM staging.stg_klaviyo__event GROUP BY ALL HAVING count(*)>1 ORDER BY n DESC LIMIT 10
```
结果原文：
```json
{
  "executed_utc": "2026-10-29T11:33:05.644247+00:00",
  "error": "Parser Error: syntax error at or near \"day\"\n\nLINE 1: SELECT person_id,source_relation,cast(occurred_at AS DATE) day,count(*) n FROM staging.stg_klaviyo__event GROUP BY...\n                                                                   ^"
}
```

### V2 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。
```sql
SELECT person_id,source_relation,cast(occurred_at AS DATE) event_day,count(*) n FROM staging.stg_klaviyo__event GROUP BY ALL HAVING count(*)>1 ORDER BY n DESC LIMIT 10
```
结果原文：
```json
{
  "columns": [
    "person_id",
    "source_relation",
    "event_day",
    "n"
  ],
  "rows": [
    [
      null,
      "klaviyo",
      "2023-11-14",
      7
    ],
    [
      null,
      "klaviyo",
      "2022-02-28",
      6
    ],
    [
      null,
      "klaviyo",
      "2024-01-31",
      5
    ],
    [
      null,
      "klaviyo",
      "2019-04-15",
      5
    ],
    [
      null,
      "klaviyo",
      "2020-07-10",
      5
    ],
    [
      null,
      "klaviyo",
      "2021-12-30",
      5
    ],
    [
      null,
      "klaviyo",
      "2024-08-15",
      5
    ],
    [
      null,
      "klaviyo",
      "2021-09-11",
      5
    ],
    [
      null,
      "klaviyo",
      "2022-12-29",
      5
    ],
    [
      null,
      "klaviyo",
      "2023-09-23",
      5
    ]
  ],
  "executed_utc": "2026-10-29T11:34:22.508863+00:00"
}
```

### V3 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。
```sql
SELECT person_id,source_relation,cast(occurred_at AS DATE) AS event_day,count(*) AS event_count FROM staging.stg_klaviyo__event WHERE person_id IS NOT NULL GROUP BY ALL HAVING count(*)>1 ORDER BY person_id,event_day
```
结果原文：
```json
{
  "columns": [
    "person_id",
    "source_relation",
    "event_day",
    "event_count"
  ],
  "rows": [
    [
      "LRqEsZ",
      "klaviyo",
      "2020-04-05",
      2
    ],
    [
      "MCX88q",
      "klaviyo",
      "2020-04-05",
      2
    ]
  ],
  "executed_utc": "2026-10-29T11:36:33.371910+00:00"
}
```

### D1 / 诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/klaviyo.duckdb`。
```sql
SELECT person_id,source_relation,count(*) n,count(distinct cast(occurred_at AS DATE)) days,min(cast(occurred_at AS DATE)) first_day,max(cast(occurred_at AS DATE)) last_day FROM staging.stg_klaviyo__event GROUP BY 1,2 ORDER BY 1,2
```
```json
{
  "error": "Parser Error: syntax error at or near \"days\"\n\nLINE 1: ...ation,count(*) n,count(distinct cast(occurred_at AS DATE)) days,min(cast(occurred_at AS DATE)) first_day,max(cast(occu...\n                                                                      ^"
}
```

### D2 / 诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/klaviyo.duckdb`。
```sql
SELECT person_id,source_relation,count(*) n,count(distinct cast(occurred_at AS DATE)) AS day_count,min(cast(occurred_at AS DATE)) first_day,max(cast(occurred_at AS DATE)) last_day FROM staging.stg_klaviyo__event GROUP BY 1,2 ORDER BY 1,2
```
```json
{
  "columns": [
    "person_id",
    "source_relation",
    "n",
    "day_count",
    "first_day",
    "last_day"
  ],
  "rows": [
    [
      "LRqEsZ",
      "klaviyo",
      2,
      1,
      "2020-04-05",
      "2020-04-05"
    ],
    [
      "MCX88q",
      "klaviyo",
      2,
      1,
      "2020-04-05",
      "2020-04-05"
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['person_id']`；原评分比较列：`['active_days', 'active_months', 'active_weeks', 'count_active_on_site', 'count_clicked_email', 'count_opened_email', 'count_ordered_product', 'count_placed_order', 'count_received_email', 'count_refunded_order', 'count_viewed_product', 'email_click_to_open_rate', 'email_open_rate', 'first_event_on', 'last_event_on', 'missing_day_count', 'person_id', 'product_view_to_order_rate', 'site_to_order_rate', 'sum_revenue_cancelled_order', 'sum_revenue_ordered_product', 'sum_revenue_placed_order', 'sum_revenue_refunded_order']`。与键取并集，不自行纳入原评分排除列。

全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。

共同时间控制：`[]`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|missing_count|2→0|2→0|L0|
|spine_days_count|2→0|2→0|L0|

### 原留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2|2|0|0|0/0|2|2|2|False|
|L1|2|2|0|0|0/0|2|2|2|False|
|L2|2|2|0|0|0/0|2|2|2|False|
|L3|2|2|0|0|0/0|2|2|2|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|person_id|0|0|0|0|
|active_days|0|0|0|0|
|active_months|0|0|0|0|
|active_weeks|0|0|0|0|
|count_active_on_site|0|0|0|0|
|count_clicked_email|0|0|0|0|
|count_opened_email|0|0|0|0|
|count_ordered_product|0|0|0|0|
|count_placed_order|0|0|0|0|
|count_received_email|0|0|0|0|
|count_refunded_order|0|0|0|0|
|count_viewed_product|0|0|0|0|
|email_click_to_open_rate|0|0|0|0|
|email_open_rate|0|0|0|0|
|first_event_on|0|0|0|0|
|last_event_on|0|0|0|0|
|missing_day_count|2|2|2|2|
|product_view_to_order_rate|0|0|0|0|
|site_to_order_rate|0|0|0|0|
|sum_revenue_cancelled_order|0|0|0|0|
|sum_revenue_ordered_product|0|0|0|0|
|sum_revenue_placed_order|0|0|0|0|
|sum_revenue_refunded_order|0|0|0|0|

### 重跑 baseline

SQL：`data/017_work/impl-021/baseline.sql`；SHA-256：`5ecf0dcb9d3310d0cd3e40454bc70b560efc4a78b8877ee672f15ed1853d7e9c`。

同输入、同时间控制、不增加因果改动的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2|2|0|0|0/0|2|2|2|False|
|L1|2|2|0|0|0/0|2|2|2|False|
|L2|2|2|0|0|0/0|2|2|2|False|
|L3|2|2|0|0|0/0|2|2|2|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|person_id|0|0|0|0|
|active_days|0|0|0|0|
|active_months|0|0|0|0|
|active_weeks|0|0|0|0|
|count_active_on_site|0|0|0|0|
|count_clicked_email|0|0|0|0|
|count_opened_email|0|0|0|0|
|count_ordered_product|0|0|0|0|
|count_placed_order|0|0|0|0|
|count_received_email|0|0|0|0|
|count_refunded_order|0|0|0|0|
|count_viewed_product|0|0|0|0|
|email_click_to_open_rate|0|0|0|0|
|email_open_rate|0|0|0|0|
|first_event_on|0|0|0|0|
|last_event_on|0|0|0|0|
|missing_day_count|2|2|2|2|
|product_view_to_order_rate|0|0|0|0|
|site_to_order_rate|0|0|0|0|
|sum_revenue_cancelled_order|0|0|0|0|
|sum_revenue_ordered_product|0|0|0|0|
|sum_revenue_placed_order|0|0|0|0|
|sum_revenue_refunded_order|0|0|0|0|

### 重跑 missing_count

SQL：`data/017_work/impl-021/missing_count.sql`；SHA-256：`3696f0e64883dd0fd857dd96342e6cfabd00cbff1cb02f86b89481f87b233b7b`。

唯一替换位置offset=2313；原文：
```sql
count(*)-count(distinct e.occurred_on)
```
新文：
```sql
count(*)-count(e.occurred_on)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2|2|0|0|0/0|0|0|0|True|
|L1|2|2|0|0|0/0|0|0|0|True|
|L2|2|2|0|0|0/0|0|0|0|True|
|L3|2|2|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|person_id|0|0|0|0|
|active_days|0|0|0|0|
|active_months|0|0|0|0|
|active_weeks|0|0|0|0|
|count_active_on_site|0|0|0|0|
|count_clicked_email|0|0|0|0|
|count_opened_email|0|0|0|0|
|count_ordered_product|0|0|0|0|
|count_placed_order|0|0|0|0|
|count_received_email|0|0|0|0|
|count_refunded_order|0|0|0|0|
|count_viewed_product|0|0|0|0|
|email_click_to_open_rate|0|0|0|0|
|email_open_rate|0|0|0|0|
|first_event_on|0|0|0|0|
|last_event_on|0|0|0|0|
|missing_day_count|0|0|0|0|
|product_view_to_order_rate|0|0|0|0|
|site_to_order_rate|0|0|0|0|
|sum_revenue_cancelled_order|0|0|0|0|
|sum_revenue_ordered_product|0|0|0|0|
|sum_revenue_placed_order|0|0|0|0|
|sum_revenue_refunded_order|0|0|0|0|

### 重跑 spine_days_count

SQL：`data/017_work/impl-021/spine_days_count.sql`；SHA-256：`f86bb66dde94524fe481f07f572ab6c43f7f139500bb11b829bc38dcccb49823`。

唯一替换位置offset=2313；原文：
```sql
count(*)-count(distinct e.occurred_on)
```
新文：
```sql
count(distinct d.day)-count(distinct e.occurred_on)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2|2|0|0|0/0|0|0|0|True|
|L1|2|2|0|0|0/0|0|0|0|True|
|L2|2|2|0|0|0/0|0|0|0|True|
|L3|2|2|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|person_id|0|0|0|0|
|active_days|0|0|0|0|
|active_months|0|0|0|0|
|active_weeks|0|0|0|0|
|count_active_on_site|0|0|0|0|
|count_clicked_email|0|0|0|0|
|count_opened_email|0|0|0|0|
|count_ordered_product|0|0|0|0|
|count_placed_order|0|0|0|0|
|count_received_email|0|0|0|0|
|count_refunded_order|0|0|0|0|
|count_viewed_product|0|0|0|0|
|email_click_to_open_rate|0|0|0|0|
|email_open_rate|0|0|0|0|
|first_event_on|0|0|0|0|
|last_event_on|0|0|0|0|
|missing_day_count|0|0|0|0|
|product_view_to_order_rate|0|0|0|0|
|site_to_order_rate|0|0|0|0|
|sum_revenue_cancelled_order|0|0|0|0|
|sum_revenue_ordered_product|0|0|0|0|
|sum_revenue_placed_order|0|0|0|0|
|sum_revenue_refunded_order|0|0|0|0|

## 5. 类别、把握和对比

- 主要原因：**U**（归因判断）。
- 主因单项：spine_days_count。
- 参与因素：无；两种计数替换是同一错误点的替代修法。
- 标记：证据曾出现但被忽略。
- 把握：**中**。
- 重跑是否满足U第4条件：是：仅修spine计数，2行/2格→0，L0整表一致。

P：按(person_id,source_relation,occurred_on)连接事件后，date spine每一天最多得到一行，因而连接后count(*)仍是天数。017-V3在agent留存staging反证两组各2行；原契约也提醒同日可能多事件。U3按手册“证据曾出现但被忽略”例外处理；U4由单项计数修正L0全匹配满足。

与014相比是否变化：不适用（第三批首次标注）；也未修改016任何结论。

## 规则问题

也可读为C（没有算对缺失天数）或I（COUNT写错）；本次选U，因为契约给的是指标性质和多事件提醒，没有指定COUNT表达式，错误成立依赖可直接核实的连接基数。没有明确的正确COUNT实现意图，不仅凭想算missing_day_count就归I。新增字段记“已提到”只表示确有重复处理声明，不等于核实过P。

2026-10-29用户确认补充：本表依赖原始表若agent留存与初始一致而gold不同，先诊断再标不可评估；若gold与初始一致而agent不同，则正常标注并追踪agent运行中的改动。不能把两种情况混淆。raw差异须限定到本表依赖；CS上游用gold。

新增字段统一口径：记录与实际差异机制相关的明确选择/可疑数据表述；不要求agent预知gold，也不把泛称“完成清洗”算作识别具体边界。021关于重复计数、029关于可选字段失败置NULL为适用范围较广的声明，单独注明并未点名本表异常；可见证据只能支持这一有限范围。该字段不增减U/C/D/I/A/O/X条件。
