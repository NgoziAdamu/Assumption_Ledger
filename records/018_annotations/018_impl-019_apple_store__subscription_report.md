# impl-019 / apple_store__subscription_report（v2定稿）

## 1. 差异描述与判定

summary/event两个连接用NULL安全等值，gold用普通等值；summary连接是主要差异。

已核实：CS上游gold，双方1548180行，基线1600行/8855格；只把summary连接的IS NOT DISTINCT FROM改为=后346行/892格，只改event连接后1295行/7538格。契约列出连接键和指标空值补0，但未规定NULL键彼此是否匹配，也没提供可执行等号表达式。此选择不能由NULL存在本身决定，主要A与A参与因素。015显示相关gold/agent raw一致，初始库schema/表示不同，不属于agent=初始≠gold的不可评估情况。 A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。

主要原因：**A**；把握：**中**。
参与因素：A：event连接的NULL相等策略（1600→1295行）。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-019_apple_store__subscription_report.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-019_marts_apple_store__subscription_report.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` 第1861–1948行。
- [原始轨迹转录](../016_trace_impl-019.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-019.json)；[015三方raw核对](../015_raw_impl-019.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: apple_store__subscription_report
      description: Daily subscription KPIs per product and territory; joins summary and events to the reporting grain and enriches with country names/regions; missing measures are zero-filled.
      grain: One row per date_day × vendor_number × app_apple_id × subscription_name × territory_short × state × source_relation
      source_models:
      - intermediate.int_apple_store__subscription_report
      - intermediate.int_apple_store__subscription_summary
      - intermediate.int_apple_store__subscription_events
      - intermediate.int_apple_store__country_codes
      business_logic: '- Use intermediate.int_apple_store__subscription_report as the driver; output one row per key: date_day, vendor_number, app_apple_id, subscription_name, country (as territory_short), state, source_relation. - Left join intermediate.int_apple_store__subscription_summary on vendor_number, app_apple_id, date_day, subscription_name, country, state, and source_relation to bring active_* measures. - Left join intermediate.int_apple_store__subscription_events on the same keys to bring event_* measures. - Left join intermediate.int_apple_store__country_codes on country_code_alpha_2 = reporting country; set territory_long to alternative country name when available, otherwise the standard country name; set region and sub_region from the match. - Pass through app_name and source_relation from the reporting grain; set territory_short from the reporting country and state from the reporting state. - Null handling: replace missing active_* and event_* measures with 0; geography fields from country_codes are null when no country match; other string fields are passed through unchanged. - No aggregation, sorting, or filtering is applied; row multiplicity follows the joins and assumes uniqueness of joined sources on the stated keys.'
      columns:
      - name: date_day
        data_type: TIMESTAMP
        description: Day timestamp from the reporting grain; used in joins; no timezone conversion.
        tests:
        - not_null
      - name: vendor_number
        data_type: INTEGER
        description: Vendor identifier from the reporting grain; part of the join keys.
        tests:
        - not_null
      - name: app_apple_id
        data_type: INTEGER
        description: Application Apple ID from the reporting grain; part of the join keys.
        tests:
        - not_null
      - name: app_name
        data_type: VARCHAR
        description: Application name passed through from the reporting grain.
      - name: subscription_name
        data_type: VARCHAR
        description: Subscription product name from the reporting grain; part of the join keys.
        tests:
        - not_null
      - name: territory_long
        data_type: VARCHAR
        description: 'Country name from country_codes: use alternative name when available, otherwise the standard country name; null if no country match.'
      - name: territory_short
        data_type: VARCHAR
        description: Two-letter ISO alpha-2 country code from the reporting grain; preserved as stored.
        tests:
        - not_null
      - name: state
        data_type: VARCHAR
        description: State/province code from the reporting grain; may be null.
      - name: region
        data_type: VARCHAR
        description: Region from country_codes for the matched country; null if not found.
      - name: sub_region
        data_type: VARCHAR
        description: Sub-region from country_codes for the matched country; null if not found.
      - name: source_relation
        data_type: VARCHAR
        description: Source system identifier from the reporting grain; part of the join keys.
      - name: active_free_trial_introductory_offer_subscriptions
        data_type: HUGEINT
        description: Count of active subscriptions on introductory free trials from subscription_summary; zero when missing.
        tests:
        - active_free_trial_introductory_offer_subscriptions >= 0
      - name: active_pay_as_you_go_introductory_offer_subscriptions
        data_type: HUGEINT
        description: Count of active subscriptions on pay-as-you-go introductory offers from subscription_summary; zero when missing.
        tests:
        - active_pay_as_you_go_introductory_offer_subscriptions >= 0
      - name: active_pay_up_front_introductory_offer_subscriptions
        data_type: HUGEINT
        description: Count of active subscriptions on pay-up-front introductory offers from subscription_summary; zero when missing.
        tests:
        - active_pay_up_front_introductory_offer_subscriptions >= 0
      - name: active_standard_price_subscriptions
        data_type: HUGEINT
        description: Count of active subscriptions at standard price from subscription_summary; zero when missing.
        tests:
        - active_standard_price_subscriptions >= 0
      - name: event_renew
        data_type: HUGEINT
        description: Renewal event count from subscription_events; zero when missing.
        tests:
        - event_renew >= 0
      - name: event_cancel
        data_type: HUGEINT
        description: Cancel event count from subscription_events; zero when missing.
        tests:
        - event_cancel >= 0
      - name: event_subscribe
        data_type: HUGEINT
        description: Subscribe event count from subscription_events; zero when missing.
        tests:
        - event_subscribe >= 0
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__subscription_report.sql`
```sql
   1: WITH g AS (SELECT date_day, vendor_number, app_apple_id, app_name, subscription_name, country, state, source_relation FROM intermediate.int_apple_store__subscription_report),
   2: s AS (SELECT vendor_number, app_apple_id, date_day, subscription_name, country, state, source_relation, active_free_trial_introductory_offer_subscriptions, active_pay_as_you_go_introductory_offer_subscriptions, active_pay_up_front_introductory_offer_subscriptions, active_standard_price_subscriptions FROM intermediate.int_apple_store__subscription_summary),
   3: e AS (SELECT vendor_number, app_apple_id, date_day, subscription_name, country, state, source_relation, event_renew, event_cancel, event_subscribe FROM intermediate.int_apple_store__subscription_events),
   4: cc AS (SELECT country_code_alpha_2, alternative_country_name, country_name, region, sub_region FROM intermediate.int_apple_store__country_codes)
   5: SELECT g.date_day,
   6:        g.vendor_number,
   7:        g.app_apple_id,
   8:        g.app_name,
   9:        g.subscription_name,
  10:        COALESCE(cc.alternative_country_name, cc.country_name) AS territory_long,
  11:        g.country AS territory_short,
  12:        g.state,
  13:        cc.region,
  14:        cc.sub_region,
  15:        g.source_relation,
  16:        COALESCE(s.active_free_trial_introductory_offer_subscriptions, 0) AS active_free_trial_introductory_offer_subscriptions,
  17:        COALESCE(s.active_pay_as_you_go_introductory_offer_subscriptions, 0) AS active_pay_as_you_go_introductory_offer_subscriptions,
  18:        COALESCE(s.active_pay_up_front_introductory_offer_subscriptions, 0) AS active_pay_up_front_introductory_offer_subscriptions,
  19:        COALESCE(s.active_standard_price_subscriptions, 0) AS active_standard_price_subscriptions,
  20:        COALESCE(e.event_renew, 0) AS event_renew,
  21:        COALESCE(e.event_cancel, 0) AS event_cancel,
  22:        COALESCE(e.event_subscribe, 0) AS event_subscribe
  23: FROM g
  24: LEFT JOIN s ON g.vendor_number IS NOT DISTINCT FROM s.vendor_number AND g.app_apple_id IS NOT DISTINCT FROM s.app_apple_id AND g.date_day IS NOT DISTINCT FROM s.date_day AND g.subscription_name IS NOT DISTINCT FROM s.subscription_name AND g.country IS NOT DISTINCT FROM s.country AND g.state IS NOT DISTINCT FROM s.state AND g.source_relation IS NOT DISTINCT FROM s.source_relation
  25: LEFT JOIN e ON g.vendor_number IS NOT DISTINCT FROM e.vendor_number AND g.app_apple_id IS NOT DISTINCT FROM e.app_apple_id AND g.date_day IS NOT DISTINCT FROM e.date_day AND g.subscription_name IS NOT DISTINCT FROM e.subscription_name AND g.country IS NOT DISTINCT FROM e.country AND g.state IS NOT DISTINCT FROM e.state AND g.source_relation IS NOT DISTINCT FROM e.source_relation
  26: LEFT JOIN cc ON g.country = cc.country_code_alpha_2
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/sql/marts/apple_store__subscription_report.sql`
```sql
   1: -- Marts: Subscription report
   2: 
   3: WITH subscription_summary AS (
   4:   SELECT * FROM intermediate.int_apple_store__subscription_summary
   5: ),
   6: subscription_events AS (
   7:   SELECT * FROM intermediate.int_apple_store__subscription_events
   8: ),
   9: country_codes AS (
  10:   SELECT * FROM intermediate.int_apple_store__country_codes
  11: ),
  12: reporting_grain AS (
  13:   SELECT * FROM intermediate.int_apple_store__subscription_report
  14: ),
  15: final AS (
  16:   SELECT
  17:     rg.date_day,
  18:     rg.vendor_number,
  19:     rg.app_apple_id,
  20:     rg.app_name,
  21:     rg.subscription_name,
  22:     COALESCE(country_codes.alternative_country_name, country_codes.country_name) AS territory_long,
  23:     rg.country AS territory_short,
  24:     rg.state,
  25:     country_codes.region,
  26:     country_codes.sub_region,
  27:     rg.source_relation,
  28:     COALESCE(ss.active_free_trial_introductory_offer_subscriptions, 0) AS active_free_trial_introductory_offer_subscriptions,
  29:     COALESCE(ss.active_pay_as_you_go_introductory_offer_subscriptions, 0) AS active_pay_as_you_go_introductory_offer_subscriptions,
  30:     COALESCE(ss.active_pay_up_front_introductory_offer_subscriptions, 0) AS active_pay_up_front_introductory_offer_subscriptions,
  31:     COALESCE(ss.active_standard_price_subscriptions, 0) AS active_standard_price_subscriptions,
  32:     COALESCE(se.event_renew, 0) AS event_renew,
  33:     COALESCE(se.event_cancel, 0) AS event_cancel,
  34:     COALESCE(se.event_subscribe, 0) AS event_subscribe
  35:   FROM reporting_grain rg
  36:   LEFT JOIN subscription_summary ss
  37:     ON rg.vendor_number = ss.vendor_number
  38:    AND rg.app_apple_id = ss.app_apple_id
  39:    AND rg.date_day = ss.date_day
  40:    AND rg.subscription_name = ss.subscription_name
  41:    AND rg.country = ss.country
  42:    AND rg.state = ss.state
  43:    AND rg.source_relation = ss.source_relation
  44:   LEFT JOIN subscription_events se
  45:     ON rg.vendor_number = se.vendor_number
  46:    AND rg.app_apple_id = se.app_apple_id
  47:    AND rg.date_day = se.date_day
  48:    AND rg.subscription_name = se.subscription_name
  49:    AND rg.country = se.country
  50:    AND rg.state = se.state
  51:    AND rg.source_relation = se.source_relation
  52:   LEFT JOIN country_codes
  53:     ON rg.country = country_codes.country_code_alpha_2
  54: )
  55: SELECT *
  56: FROM final
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.apple_store_country_codes|gold_vs_initial|None|None|None|initial_missing_table|
|raw.sales_subscription_event_summary|gold_vs_initial|False|True|False|ordered_columns_or_types_differ,sorted_content_hash_differ|
|raw.sales_subscription_summary|gold_vs_initial|False|True|False|ordered_columns_or_types_differ,sorted_content_hash_differ|
|raw.apple_store_country_codes|gold_vs_agent|True|True|True||
|raw.sales_subscription_event_summary|gold_vs_agent|True|True|True||
|raw.sales_subscription_summary|gold_vs_agent|True|True|True||

补充诊断与原始事件见[016_raw_diagnostics.json](../016_raw_diagnostics.json)。

## 3. agent实际看到的信息与不确定性四档

event1包含连接业务说明；event19生成两个NULL安全连接，代码明确选择了NULL匹配策略，不是因为不知道表里可能有NULL才误用普通等号。不存在足以唯一规定NULL业务含义的可见文档。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|summary_null_join|A|看到了但没提|1|

### summary_null_join：看到了但没提

契约连接键和NULL可见；报告的SQL聚合保留NULL、marts缺指标补零指聚合/输出策略，不说明连接键的NULL是否彼此相等。

事件 **1**，字段`args.content`；[轨迹原文](../016_trace_impl-019.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json`。
```text
description: Daily subscription KPIs per product and territory; joins summary and events to the reporting grain and enriches with country names/regions; missing measures are zero-filled.
      grain: One row per date_day × vendor_number × app_apple_id × subscription_name × territory_short × state × source_relation
      source_models:
      - intermediate.int_apple_store__subscription_report
      - intermediate.int_apple_store__subscription_summary
      - intermediate.int_apple_store__subscription_events
      - intermediate.int_apple_store__country_codes
      business_logic: '- Use intermediate.int_apple_store__subscription_report as the driver; output one row per key: date_day, vendor_number, app_apple_id, subscription_name, country (as territory_short), state, source_relation. - Left join intermediate.int_apple_store__subscription_summary on vendor_number, app_apple_id, date_day, subscription_name, co
```

已检视65个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **0条**；018新增核实查询 **0条**。核实代价：需要查业务说明。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-019.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **0条**（含014复用；本轮新增0条）；核实代价档：**需要查业务说明**。诊断不计入5条上限。查询失败与重复执行如实保留。

无新增数据核实查询；本表依据契约/SQL和只读诊断或重跑判断。

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['app_apple_id', 'date_day', 'state', 'region']`；比较列（与键取并集）：`['active_free_trial_introductory_offer_subscriptions', 'active_pay_as_you_go_introductory_offer_subscriptions', 'active_pay_up_front_introductory_offer_subscriptions', 'active_standard_price_subscriptions', 'app_apple_id', 'app_name', 'date_day', 'event_cancel', 'event_renew', 'event_subscribe', 'region', 'state', 'sub_region', 'subscription_name', 'territory_long', 'territory_short', 'vendor_number']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|summary_null_join|1600→346|8855→892|无|
|event_null_join|1600→1295|8855→7538|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1548180|1548180|0|0|0/0|1600|1600|8855|False|
|L1|1548180|1548180|0|0|0/0|1600|1600|8855|False|
|L2|1548180|1548180|0|0|0/0|1600|1600|8855|False|
|L3|1548180|1548180|0|0|0/0|1600|1600|8855|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|app_apple_id|0|0|0|0|
|date_day|0|0|0|0|
|state|0|0|0|0|
|region|0|0|0|0|
|active_free_trial_introductory_offer_subscriptions|953|953|953|953|
|active_pay_as_you_go_introductory_offer_subscriptions|873|873|873|873|
|active_pay_up_front_introductory_offer_subscriptions|912|912|912|912|
|active_standard_price_subscriptions|1110|1110|1110|1110|
|app_name|0|0|0|0|
|event_cancel|184|184|184|184|
|event_renew|162|162|162|162|
|event_subscribe|0|0|0|0|
|sub_region|710|710|710|710|
|subscription_name|1018|1018|1018|1018|
|territory_long|1027|1027|1027|1027|
|territory_short|1027|1027|1027|1027|
|vendor_number|879|879|879|879|

### 重跑 baseline

SQL：`data/016_work/impl-019/baseline.sql`；SHA-256：`3bc0c1685053c8ce8e361bcb46cdef2321fa9d3ef1f96819f505e163164be49b`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1548180|1548180|0|0|0/0|1600|1600|8855|False|
|L1|1548180|1548180|0|0|0/0|1600|1600|8855|False|
|L2|1548180|1548180|0|0|0/0|1600|1600|8855|False|
|L3|1548180|1548180|0|0|0/0|1600|1600|8855|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|app_apple_id|0|0|0|0|
|date_day|0|0|0|0|
|state|0|0|0|0|
|region|0|0|0|0|
|active_free_trial_introductory_offer_subscriptions|953|953|953|953|
|active_pay_as_you_go_introductory_offer_subscriptions|873|873|873|873|
|active_pay_up_front_introductory_offer_subscriptions|912|912|912|912|
|active_standard_price_subscriptions|1110|1110|1110|1110|
|app_name|0|0|0|0|
|event_cancel|184|184|184|184|
|event_renew|162|162|162|162|
|event_subscribe|0|0|0|0|
|sub_region|710|710|710|710|
|subscription_name|1018|1018|1018|1018|
|territory_long|1027|1027|1027|1027|
|territory_short|1027|1027|1027|1027|
|vendor_number|879|879|879|879|

### 重跑 summary_null_join

SQL：`data/016_work/impl-019/summary_null_join.sql`；SHA-256：`6bb12c832dda1313950a2becbcc31860c5a4305cc20247502cb3a4212fb8dd34`。

唯一原文位置offset=1854，替换前：
```sql
LEFT JOIN s ON g.vendor_number IS NOT DISTINCT FROM s.vendor_number AND g.app_apple_id IS NOT DISTINCT FROM s.app_apple_id AND g.date_day IS NOT DISTINCT FROM s.date_day AND g.subscription_name IS NOT DISTINCT FROM s.subscription_name AND g.country IS NOT DISTINCT FROM s.country AND g.state IS NOT DISTINCT FROM s.state AND g.source_relation IS NOT DISTINCT FROM s.source_relation
```
替换后：
```sql
LEFT JOIN s ON g.vendor_number = s.vendor_number AND g.app_apple_id = s.app_apple_id AND g.date_day = s.date_day AND g.subscription_name = s.subscription_name AND g.country = s.country AND g.state = s.state AND g.source_relation = s.source_relation
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1548180|1548180|0|0|0/0|346|346|892|False|
|L1|1548180|1548180|0|0|0/0|346|346|892|False|
|L2|1548180|1548180|0|0|0/0|346|346|892|False|
|L3|1548180|1548180|0|0|0/0|346|346|892|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|app_apple_id|0|0|0|0|
|date_day|0|0|0|0|
|state|0|0|0|0|
|region|0|0|0|0|
|active_free_trial_introductory_offer_subscriptions|0|0|0|0|
|active_pay_as_you_go_introductory_offer_subscriptions|0|0|0|0|
|active_pay_up_front_introductory_offer_subscriptions|0|0|0|0|
|active_standard_price_subscriptions|0|0|0|0|
|app_name|0|0|0|0|
|event_cancel|184|184|184|184|
|event_renew|162|162|162|162|
|event_subscribe|0|0|0|0|
|sub_region|88|88|88|88|
|subscription_name|118|118|118|118|
|territory_long|120|120|120|120|
|territory_short|120|120|120|120|
|vendor_number|100|100|100|100|

### 重跑 event_null_join

SQL：`data/016_work/impl-019/event_null_join.sql`；SHA-256：`f99e6f9d1484f961d1f71db53d6f34024b3b594871255175edec93fe338ec869`。

唯一原文位置offset=2236，替换前：
```sql
LEFT JOIN e ON g.vendor_number IS NOT DISTINCT FROM e.vendor_number AND g.app_apple_id IS NOT DISTINCT FROM e.app_apple_id AND g.date_day IS NOT DISTINCT FROM e.date_day AND g.subscription_name IS NOT DISTINCT FROM e.subscription_name AND g.country IS NOT DISTINCT FROM e.country AND g.state IS NOT DISTINCT FROM e.state AND g.source_relation IS NOT DISTINCT FROM e.source_relation
```
替换后：
```sql
LEFT JOIN e ON g.vendor_number = e.vendor_number AND g.app_apple_id = e.app_apple_id AND g.date_day = e.date_day AND g.subscription_name = e.subscription_name AND g.country = e.country AND g.state = e.state AND g.source_relation = e.source_relation
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1548180|1548180|0|0|0/0|1295|1295|7538|False|
|L1|1548180|1548180|0|0|0/0|1295|1295|7538|False|
|L2|1548180|1548180|0|0|0/0|1295|1295|7538|False|
|L3|1548180|1548180|0|0|0/0|1295|1295|7538|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|app_apple_id|0|0|0|0|
|date_day|0|0|0|0|
|state|0|0|0|0|
|region|0|0|0|0|
|active_free_trial_introductory_offer_subscriptions|953|953|953|953|
|active_pay_as_you_go_introductory_offer_subscriptions|873|873|873|873|
|active_pay_up_front_introductory_offer_subscriptions|912|912|912|912|
|active_standard_price_subscriptions|1110|1110|1110|1110|
|app_name|0|0|0|0|
|event_cancel|0|0|0|0|
|event_renew|0|0|0|0|
|event_subscribe|0|0|0|0|
|sub_region|568|568|568|568|
|subscription_name|800|800|800|800|
|territory_long|812|812|812|812|
|territory_short|812|812|812|812|
|vendor_number|698|698|698|698|

## 5. 逐项类别及U门槛

表级主要原因：**A**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|summary_null_join|A|1600→346|8855→892|无|

重跑是否满足U第4条件：**是（summary_null_join单改1600→346行；非U）**。

“NULL应互相匹配”是缺业务定义的决策，不是查询NULL计数即可证伪的数据性质命题；不用gold等号作为U真值。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：不适用：第二批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

报告提到聚合NULL语义及输出补零，没有说明连接中NULL键是否彼此匹配；不以无关NULL文字提升四档。NULL等值仍是契约未定选择A；同一固定配对口径不变。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
