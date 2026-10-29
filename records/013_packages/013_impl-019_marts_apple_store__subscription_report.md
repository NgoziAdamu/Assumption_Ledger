# impl-019 | marts | apple_store__subscription_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1861–1948

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

## agent 最终 SQL

S4

```sql
WITH g AS (SELECT date_day, vendor_number, app_apple_id, app_name, subscription_name, country, state, source_relation FROM intermediate.int_apple_store__subscription_report),
s AS (SELECT vendor_number, app_apple_id, date_day, subscription_name, country, state, source_relation, active_free_trial_introductory_offer_subscriptions, active_pay_as_you_go_introductory_offer_subscriptions, active_pay_up_front_introductory_offer_subscriptions, active_standard_price_subscriptions FROM intermediate.int_apple_store__subscription_summary),
e AS (SELECT vendor_number, app_apple_id, date_day, subscription_name, country, state, source_relation, event_renew, event_cancel, event_subscribe FROM intermediate.int_apple_store__subscription_events),
cc AS (SELECT country_code_alpha_2, alternative_country_name, country_name, region, sub_region FROM intermediate.int_apple_store__country_codes)
SELECT g.date_day,
       g.vendor_number,
       g.app_apple_id,
       g.app_name,
       g.subscription_name,
       COALESCE(cc.alternative_country_name, cc.country_name) AS territory_long,
       g.country AS territory_short,
       g.state,
       cc.region,
       cc.sub_region,
       g.source_relation,
       COALESCE(s.active_free_trial_introductory_offer_subscriptions, 0) AS active_free_trial_introductory_offer_subscriptions,
       COALESCE(s.active_pay_as_you_go_introductory_offer_subscriptions, 0) AS active_pay_as_you_go_introductory_offer_subscriptions,
       COALESCE(s.active_pay_up_front_introductory_offer_subscriptions, 0) AS active_pay_up_front_introductory_offer_subscriptions,
       COALESCE(s.active_standard_price_subscriptions, 0) AS active_standard_price_subscriptions,
       COALESCE(e.event_renew, 0) AS event_renew,
       COALESCE(e.event_cancel, 0) AS event_cancel,
       COALESCE(e.event_subscribe, 0) AS event_subscribe
FROM g
LEFT JOIN s ON g.vendor_number IS NOT DISTINCT FROM s.vendor_number AND g.app_apple_id IS NOT DISTINCT FROM s.app_apple_id AND g.date_day IS NOT DISTINCT FROM s.date_day AND g.subscription_name IS NOT DISTINCT FROM s.subscription_name AND g.country IS NOT DISTINCT FROM s.country AND g.state IS NOT DISTINCT FROM s.state AND g.source_relation IS NOT DISTINCT FROM s.source_relation
LEFT JOIN e ON g.vendor_number IS NOT DISTINCT FROM e.vendor_number AND g.app_apple_id IS NOT DISTINCT FROM e.app_apple_id AND g.date_day IS NOT DISTINCT FROM e.date_day AND g.subscription_name IS NOT DISTINCT FROM e.subscription_name AND g.country IS NOT DISTINCT FROM e.country AND g.state IS NOT DISTINCT FROM e.state AND g.source_relation IS NOT DISTINCT FROM e.source_relation
LEFT JOIN cc ON g.country = cc.country_code_alpha_2
```

## gold SQL（仅供定位差异）

S5

```sql
-- Marts: Subscription report

WITH subscription_summary AS (
  SELECT * FROM intermediate.int_apple_store__subscription_summary
),
subscription_events AS (
  SELECT * FROM intermediate.int_apple_store__subscription_events
),
country_codes AS (
  SELECT * FROM intermediate.int_apple_store__country_codes
),
reporting_grain AS (
  SELECT * FROM intermediate.int_apple_store__subscription_report
),
final AS (
  SELECT
    rg.date_day,
    rg.vendor_number,
    rg.app_apple_id,
    rg.app_name,
    rg.subscription_name,
    COALESCE(country_codes.alternative_country_name, country_codes.country_name) AS territory_long,
    rg.country AS territory_short,
    rg.state,
    country_codes.region,
    country_codes.sub_region,
    rg.source_relation,
    COALESCE(ss.active_free_trial_introductory_offer_subscriptions, 0) AS active_free_trial_introductory_offer_subscriptions,
    COALESCE(ss.active_pay_as_you_go_introductory_offer_subscriptions, 0) AS active_pay_as_you_go_introductory_offer_subscriptions,
    COALESCE(ss.active_pay_up_front_introductory_offer_subscriptions, 0) AS active_pay_up_front_introductory_offer_subscriptions,
    COALESCE(ss.active_standard_price_subscriptions, 0) AS active_standard_price_subscriptions,
    COALESCE(se.event_renew, 0) AS event_renew,
    COALESCE(se.event_cancel, 0) AS event_cancel,
    COALESCE(se.event_subscribe, 0) AS event_subscribe
  FROM reporting_grain rg
  LEFT JOIN subscription_summary ss
    ON rg.vendor_number = ss.vendor_number
   AND rg.app_apple_id = ss.app_apple_id
   AND rg.date_day = ss.date_day
   AND rg.subscription_name = ss.subscription_name
   AND rg.country = ss.country
   AND rg.state = ss.state
   AND rg.source_relation = ss.source_relation
  LEFT JOIN subscription_events se
    ON rg.vendor_number = se.vendor_number
   AND rg.app_apple_id = se.app_apple_id
   AND rg.date_day = se.date_day
   AND rg.subscription_name = se.subscription_name
   AND rg.country = se.country
   AND rg.state = se.state
   AND rg.source_relation = se.source_relation
  LEFT JOIN country_codes
    ON rg.country = country_codes.country_code_alpha_2
)
SELECT *
FROM final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1548180 | 1548180 | 0 | 0 | 35955 | 35955 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"app_apple_id":"239587236","date_day":"2024-10-01 00:00:00","state":"null","region":"americas"}</code> |
| K2 | <code>{"app_apple_id":"239587236","date_day":"2024-10-01 00:00:00","state":"null","region":"asia"}</code> |
| K3 | <code>{"app_apple_id":"239587236","date_day":"2024-10-01 00:00:00","state":"null","region":"europe"}</code> |
| K4 | <code>{"app_apple_id":"239587236","date_day":"2024-10-01 00:00:00","state":"null","region":"oceania"}</code> |
| K5 | <code>{"app_apple_id":"239587236","date_day":"2024-10-02 00:00:00","state":"null","region":"americas"}</code> |
| K6 | <code>{"app_apple_id":"239587236","date_day":"2024-10-02 00:00:00","state":"null","region":"asia"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| vendor_number | 0 | 0 | 0 | INTEGER | INTEGER |
| app_apple_id | 0 | 0 | 0 | INTEGER | INTEGER |
| app_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subscription_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| territory_long | 0 | 0 | 0 | VARCHAR | VARCHAR |
| territory_short | 0 | 0 | 0 | VARCHAR | VARCHAR |
| state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| region | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sub_region | 0 | 0 | 0 | VARCHAR | VARCHAR |
| active_free_trial_introductory_offer_subscriptions | 953 | 953 | 953 | HUGEINT | HUGEINT |
| active_pay_as_you_go_introductory_offer_subscriptions | 873 | 873 | 873 | HUGEINT | HUGEINT |
| active_pay_up_front_introductory_offer_subscriptions | 912 | 912 | 912 | HUGEINT | HUGEINT |
| active_standard_price_subscriptions | 1110 | 1110 | 1110 | HUGEINT | HUGEINT |
| event_renew | 162 | 162 | 162 | HUGEINT | HUGEINT |
| event_cancel | 184 | 184 | 184 | HUGEINT | HUGEINT |
| event_subscribe | 0 | 0 | 0 | HUGEINT | HUGEINT |

active_free_trial_introductory_offer_subscriptions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":44},{"value":"1","rows":1},{"value":"2","rows":2},{"value":"3","rows":1}]</code> | <code>[{"value":"0","rows":48}]</code> |
| K2 | <code>[{"value":"0","rows":47},{"value":"1","rows":1},{"value":"3","rows":1}]</code> | <code>[{"value":"0","rows":49}]</code> |
| K3 | <code>[{"value":"0","rows":71},{"value":"1","rows":1},{"value":"2","rows":2},{"value":"3","rows":2}]</code> | <code>[{"value":"0","rows":76}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

active_pay_as_you_go_introductory_offer_subscriptions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":44},{"value":"1","rows":3},{"value":"2","rows":1}]</code> | <code>[{"value":"0","rows":48}]</code> |
| K2 | <code>[{"value":"0","rows":46},{"value":"1","rows":2},{"value":"2","rows":1}]</code> | <code>[{"value":"0","rows":49}]</code> |
| K3 | <code>[{"value":"0","rows":71},{"value":"1","rows":4},{"value":"2","rows":1}]</code> | <code>[{"value":"0","rows":76}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

active_pay_up_front_introductory_offer_subscriptions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":45},{"value":"1","rows":2},{"value":"2","rows":1}]</code> | <code>[{"value":"0","rows":48}]</code> |
| K2 | <code>[{"value":"0","rows":48},{"value":"1","rows":1}]</code> | <code>[{"value":"0","rows":49}]</code> |
| K3 | <code>[{"value":"0","rows":71},{"value":"1","rows":1},{"value":"2","rows":3},{"value":"3","rows":1}]</code> | <code>[{"value":"0","rows":76}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

active_standard_price_subscriptions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":44},{"value":"1","rows":3},{"value":"3","rows":1}]</code> | <code>[{"value":"0","rows":48}]</code> |
| K2 | <code>[{"value":"0","rows":48},{"value":"3","rows":1}]</code> | <code>[{"value":"0","rows":49}]</code> |
| K3 | <code>[{"value":"0","rows":68},{"value":"1","rows":1},{"value":"2","rows":2},{"value":"3","rows":2},{"value":"4","rows":1}]</code> | <code>[{"value":"0","rows":76}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

event_renew 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":"0","rows":47},{"value":"2","rows":1},{"value":"3","rows":1}]</code> | <code>[{"value":"0","rows":49}]</code> |
| K3 | <code>[{"value":"0","rows":74},{"value":"1","rows":1},{"value":"3","rows":1}]</code> | <code>[{"value":"0","rows":76}]</code> |
| K4 | <code>[{"value":"0","rows":10},{"value":"1","rows":1},{"value":"3","rows":1}]</code> | <code>[{"value":"0","rows":12}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

event_cancel 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | <code>[{"value":"0","rows":75},{"value":"1","rows":1}]</code> | <code>[{"value":"0","rows":76}]</code> |
| K5 | <code>[{"value":"0","rows":47},{"value":"3","rows":1}]</code> | <code>[{"value":"0","rows":48}]</code> |
| K6 | <code>[{"value":"0","rows":48},{"value":"3","rows":1}]</code> | <code>[{"value":"0","rows":49}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>3列；[{"column":"app_apple_id","value":"239587236"},{"column":"app_name","value":"Sample"},{"column":"event_subscribe","value":"0"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：65；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,240p' run.py</code> | 11139 | true | false |
| 15 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>base=Path('sql/intermediate')<br>def put(name,sql):<br> p=base/(name+'.sql'); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(sql.strip()+'\n')<br></code> | 0 | false | false |
| 17 | run | <code>python - &lt;&lt;'PY'<br>import yaml,glob,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer,folder in [('intermediate','intermediate'),('marts','marts')]:<br> for m in c['modeling_spec'][layer+'_mode</code> | 370 | true | false |
| 19 | run | <code>cat &gt;&gt; /tmp/models.py &lt;&lt;'PY'<br># Correct report field order and qualify same-layer references explicitly.<br>for fam,info in families.items():<br> p=base/fam/'reporting_grain'/f'int_apple_store__{fam}_report.</code> | 987 | false | false |
| 21 | run | <code>find sql -type f &#124; wc -l; ls sql/marts; sed -i "/p=base\/\'device_report\/reporting_grain\/int_apple_store__device_report.sql\'/,+2d" /tmp/models.py; tail -35 /tmp/models.py; python /tmp/models.py; py</code> | 4287 | true | false |
| 23 | run | <code>find sql/intermediate -type f &#124; sort</code> | 2773 | false | false |
| 27 | run | <code>python run.py &gt; /tmp/run.log 2&gt;&amp;1; tail -80 /tmp/run.log</code> | 8841 | true | false |
| 29 | run | <code>find sql/staging -type f -printf '%f\n'; grep -E 'Failed&#124;Created&#124;Skip' /tmp/run.log &#124; head -80</code> | 7551 | true | false |
| 31 | run | <code>find sql/intermediate -path '*reporting_grain*' -type f -printf '%p\n'; grep -R 'FROM int_apple_store__\&#124;stg_apple_store__' -n sql/intermediate &#124; grep -v 'staging\.' &#124; head</code> | 751 | false | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br># Missing raw fields called for in staging contract are represented as typed NULLs; source relation remains feed label.<br>for name in ['stg_apple_store__app_cras</code> | 2256 | true | false |
| 37 | run | <code>mkdir -p sql/intermediate/reporting_grain; cp sql/intermediate/territory/reporting_grain/int_apple_store__territory_report.sql sql/intermediate/reporting_grain/; cp sql/intermediate/device_report/repo</code> | 4344 | true | false |
| 41 | run | <code>cat &gt; sql/intermediate/int_apple_store__installation_and_deletion_daily.sql &lt;&lt;'SQL'<br>SELECT<br>    date_day,<br>    app_id,<br>    download_type,<br>    app_version,<br>    device,<br>    platform_version,<br>    source_ty</code> | 3169 | true | false |
| 43 | run | <code>grep -R 'source_type' -n sql/staging; grep -R 'int_apple_store__date_spine' -n sql/intermediate &#124; head; grep -R ';' -n sql &#124; head; grep -R 'FROM int_\&#124;JOIN int_\&#124;FROM staging\&#124;JOIN staging\&#124;FROM inter</code> | 4805 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('apple_store.duckdb',read_only=True)<br>checks=[('staging','stg_apple_store__app_session_daily','date_day'),('intermediate','int_apple_store__date_spine','d</code> | 550 | true | false |
| 47 | run | <code>cat &gt; sql/intermediate/int_apple_store__installation_and_deletion_daily.sql &lt;&lt;'SQL'<br>SELECT<br>    date_day,<br>    app_id,<br>    download_type,<br>    app_version,<br>    device,<br>    platform_version,<br>    source_ty</code> | 640 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
put('apple_store__subscription_report','WITH '+',\n'.join(ctes)+'\nSELECT '+',\n       '.join(sel)+'\nFROM g\n'+joins)
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-019.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__subscription_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/sql/marts/apple_store__subscription_report.sql`
- S6: `records/006_contract_impl-019.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/result.md`
- S10: `records/012_packages/012_impl-019_marts_apple_store__subscription_report.json`
- S11: `data/005_cs_work/impl-019_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/apple_store.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions`
