# impl-019 · stg_apple_store__app_session_daily

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：semver_regex。

gold 双反斜杠版本正则拒绝契约允许的三段数字版本；另有日期解析格式范围 A 因素。

参与因素：A：date_filter_null（行减少1，格减少2）；A：date_filter_upper（行减少1，格减少2）；A：date_filter_lower（行减少1，格减少2）。

标记：无。

固定同一时间后基线7行/68格；版本单处改为gold行为降为3行/24格。日期三处过滤各自单改均降1行/2格；不能把它们打包算一个错误点。

## 材料与比较口径

精简材料包：[023_impl-019_stg_apple_store__app_session_daily.md](../023_packages/023_impl-019_stg_apple_store__app_session_daily.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml`；SHA-256 `0546320393fa39035bd8afc85a91a28a2aedccc8bcd9f41662f8fb862b7f5be2`。
契约行 24–74：

```
24:     - name: stg_apple_store__app_session_daily
25:       description: "Daily app session activity standardized from raw sessions feed."
26:       source_table: raw.app_session_standard_daily
27:       columns:
28:         - name: date_day
29:           data_type: DATE
30:           constraints: [not_null]
31:           validation_rules:
32:             - rule: "date_day IS NOT NULL AND date_day <= CURRENT_DATE AND date_day >= '2020-01-01'"
33:               on_failure: delete_row
34:         - name: app_id
35:           data_type: BIGINT
36:         - name: app_version
37:           data_type: VARCHAR
38:           validation_rules:
39:             - rule: "(app_version RLIKE '^[0-9]+\\.[0-9]+\\.[0-9]+$' OR app_version RLIKE '^[0-9]+$') AND NOT (app_version RLIKE '[A-Za-z]')"
40:               on_failure: nullify_field
41:             - rule: "NOT (app_version RLIKE '[A-Za-z]')"
42:               on_failure: delete_row
43:         - name: device
44:           data_type: VARCHAR
45:           constraints: [not_null]
46:           validation_rules:
47:             - rule: "device IS NOT NULL AND TRIM(device) <> ''"
48:               on_failure: delete_row
49:             - rule: "device NOT LIKE '%Android%' AND device NOT LIKE '%Samsung%' AND device NOT LIKE '%HUAWEI%'"
50:               on_failure: delete_row
51:         - name: platform_version
52:           data_type: VARCHAR
53:         - name: source_type
54:           data_type: VARCHAR
55:         - name: page_type
56:           data_type: VARCHAR
57:         - name: app_download_date
58:           data_type: DATE
59:         - name: territory
60:           data_type: VARCHAR
61:           validation_rules:
62:             - rule: "territory = UPPER(TRIM(territory))"
63:               on_failure: correct
64:             - rule: "LENGTH(TRIM(territory)) = 2"
65:               on_failure: nullify_field
66:         - name: sessions
67:           data_type: BIGINT
68:         - name: total_session_duration
69:           data_type: BIGINT
70:         - name: unique_devices
71:           data_type: BIGINT
72:         - name: source_relation
73:           data_type: VARCHAR
74:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/staging/stg_apple_store__app_session_daily.sql`，SHA-256 `75d005836cef1cd433a64c33eff3de8f34e3c0b50a37d84b624d0b6cddb1bafc`，行 1–24。

```
1: SELECT
2:         try_cast(r.date AS DATE) AS date_day,
3:         cast(r.app_id AS BIGINT) AS app_id,
4:         CASE WHEN r.app_version IS NULL THEN NULL WHEN regexp_matches(trim(cast(r.app_version AS VARCHAR)), '^[0-9]+(\.[0-9]+\.[0-9]+|)$') THEN trim(cast(r.app_version AS VARCHAR)) ELSE NULL END AS app_version,
5:         cast(r.device AS VARCHAR) AS device,
6:         cast(r.platform_version AS VARCHAR) AS platform_version,
7:         cast(r.source_type AS VARCHAR) AS source_type,
8:         cast(r.page_type AS VARCHAR) AS page_type,
9:         try_cast(r.app_downloa1d_date AS DATE) AS app_download_date,
10:         CASE WHEN length(trim(cast(r.territory AS VARCHAR))) = 2 THEN upper(trim(cast(r.territory AS VARCHAR))) ELSE NULL END AS territory,
11:         cast(r.sessions AS BIGINT) AS sessions,
12:         cast(r.total_session_duration AS BIGINT) AS total_session_duration,
13:         cast(r.unique_devices AS BIGINT) AS unique_devices,
14:         'app_session_standard_daily' AS source_relation
15: FROM raw.app_session_standard_daily AS r
16: WHERE try_cast(r.date AS DATE) IS NOT NULL
17:   AND try_cast(r.date AS DATE) <= CURRENT_DATE
18:   AND try_cast(r.date AS DATE) >= DATE '2020-01-01'
19:   AND r.device IS NOT NULL
20:   AND trim(r.device) <> ''
21:   AND r.device NOT LIKE '%Android%'
22:   AND r.device NOT LIKE '%Samsung%'
23:   AND r.device NOT LIKE '%HUAWEI%'
24:   AND NOT regexp_matches(coalesce(cast(r.app_version AS VARCHAR), ''), '[A-Za-z]')
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/sql/staging/stg_apple_store__app_session_daily.sql`，SHA-256 `197107c56ec60a1d3c73f2e6c7d72972b2866f97d7e773ace8a80c4013eadf83`，行 1–93。

```
1: -- Staging: App Session Daily with validation rules applied
2: -- Source: raw.app_session_standard_daily
3: 
4: WITH raw_base AS (
5:     SELECT
6:         CAST(COALESCE(
7:             TRY_STRPTIME(date, '%Y-%m-%d'),
8:             TRY_STRPTIME(date, '%d-%m-%Y'),
9:             TRY_STRPTIME(date, '%b %d, %Y')
10:         ) AS DATE) AS date_day,
11:         CAST(app_id AS BIGINT) AS app_id,
12:         CAST(app_version AS VARCHAR) AS app_version_raw,
13:         TRIM(CAST(device AS VARCHAR)) AS device_raw,
14:         CAST(platform_version AS VARCHAR) AS platform_version,
15:         CAST(source_type AS VARCHAR) AS source_type,
16:         CAST(page_type AS VARCHAR) AS page_type,
17:         CAST(COALESCE(
18:             TRY_STRPTIME(app_downloa1d_date, '%Y-%m-%d'),
19:             TRY_STRPTIME(app_downloa1d_date, '%d-%m-%Y'),
20:             TRY_STRPTIME(app_downloa1d_date, '%b %d, %Y')
21:         ) AS DATE) AS app_download_date_raw,
22:         TRIM(CAST(territory AS VARCHAR)) AS territory_raw,
23:         CAST(sessions AS BIGINT) AS sessions,
24:         CAST(total_session_duration AS BIGINT) AS total_session_duration,
25:         CAST(unique_devices AS BIGINT) AS unique_devices
26:     FROM raw.app_session_standard_daily
27: ),
28: validated AS (
29:     SELECT
30:         date_day,
31:         app_id,
32:         CASE
33:             WHEN regexp_matches(app_version_raw, '[A-Za-z]')
34:                 THEN NULL  -- will be dropped later via filter
35:             WHEN regexp_matches(app_version_raw, '^[0-9]+\\.[0-9]+\\.[0-9]+$')
36:                 OR regexp_matches(app_version_raw, '^[0-9]+$')
37:                 THEN app_version_raw
38:             ELSE NULL
39:         END AS app_version,
40:         device_clean AS device,
41:         platform_version,
42:         source_type,
43:         page_type,
44:         t.app_download_date_raw AS app_download_date,
45:         territory_clean AS territory,
46:         sessions,
47:         total_session_duration,
48:         unique_devices
49:     FROM (
50:         SELECT
51:             *,
52:             UPPER(TRIM(territory_raw)) AS territory_upper,
53:             TRIM(device_raw) AS device_trim,
54:             CASE
55:                 WHEN TRIM(device_raw) IN ('iPhone','iPad','Apple TV','Apple Vision','Mac') THEN TRIM(device_raw)
56:                 ELSE TRIM(device_raw)
57:             END AS device_clean,
58:             CASE
59:                 WHEN UPPER(TRIM(territory_raw)) IN ('US','CN','JP','GB','DE','FR','IT','ES','AU','CA','KR','IN','BR','MX','RU')
60:                     THEN UPPER(TRIM(territory_raw))
61:                 WHEN LENGTH(UPPER(TRIM(territory_raw))) = 2 THEN UPPER(TRIM(territory_raw))
62:                 ELSE NULL
63:             END AS territory_clean
64:         FROM raw_base
65:     ) t
66:     WHERE date_day IS NOT NULL
67:       AND date_day >= DATE '2020-01-01'
68:       AND date_day <= CURRENT_DATE
69:       AND device_trim IS NOT NULL AND device_trim <> ''
70:       AND device_trim NOT LIKE '%Android%'
71:       AND device_trim NOT LIKE '%Samsung%'
72:       AND device_trim NOT LIKE '%HUAWEI%'
73:       AND NOT regexp_matches(app_version_raw, '[A-Za-z]')
74: ),
75: final AS (
76:     SELECT
77:         date_day,
78:         app_id,
79:         app_version,
80:         device,
81:         platform_version,
82:         source_type,
83:         page_type,
84:         app_download_date,
85:         territory,
86:         sessions,
87:         total_session_duration,
88:         unique_devices,
89:         'apple_store' AS source_relation
90:     FROM validated
91: )
92: SELECT *
93: FROM final
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 1 契约给版本正则；event 11/12 读取raw；event 63 会话staging过滤工作清单未解释三段数字正则边界，故不计通用策略。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json`。
- event 11：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/11.json`。
- event 12：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/12.json`。
- event 63：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/63.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：NULL 版本与字母

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/apple_store.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE app_version IS NULL) null_versions FROM raw.app_session_standard_daily
```


```json
{"columns":["n","null_versions"],"rows":[[3000,0]]}
```


### 诊断：格式解析差异

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/apple_store.duckdb`。

```sql
SELECT date,count(*) FROM raw.app_session_standard_daily WHERE try_cast(date AS DATE) IS NOT NULL AND coalesce(try_strptime(date,'%Y-%m-%d'),try_strptime(date,'%d-%m-%Y'),try_strptime(date,'%b %d, %Y')) IS NULL GROUP BY 1
```


```json
{"columns":["date","count_star()"],"rows":[["2024-12-15 12:30:00",1],["2024/12/15",2]]}
```


### 诊断：版本regex效果

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/apple_store.duckdb`。

```sql
SELECT count(*) FILTER(WHERE regexp_matches(app_version,'^[0-9]+\.[0-9]+\.[0-9]+$')) normal_semver,count(*) FILTER(WHERE regexp_matches(app_version,'^[0-9]+\\.[0-9]+\\.[0-9]+$')) gold_semver FROM raw.app_session_standard_daily
```


```json
{"columns":["normal_semver","gold_semver"],"rows":[[2,0]]}
```


### 诊断：补充差异定位


```sql
SELECT date,app_version,device,count(*) FROM g.raw.app_session_standard_daily WHERE try_cast(date AS DATE) IS NULL OR date LIKE '%/%' OR date LIKE '% %' GROUP BY 1,2,3 ORDER BY 1,2,3
```


```json
{"columns":["date","app_version","device","count_star()"],"rows":[["15-12-2024","329372.2","iPhone",1],["2023-02-29","120654.0","iPhone",2],["2023-02-29","120658.0","iPhone",2],["2023-02-29","329372.1","iPhone",1],["2023-02-29","329372.2","iPhone",1],["2024-00-15","329372.1","iPhone",1],["2024-11-31","120654.0","iPhone",1],["2024-11-31","329372.2","iPhone",1],["2024-12-00","120658.0","iPhone",1],["2024-12-00","329372.2","iPhone",1],["2024-12-15 12:30:00","120658.0","iPhone",1],["2024/12/15","120658.0","iPhone",1],["2024/12/15","329372.0","iPhone",1],["2025-01-32","329372.2","iPhone",1],["Dec 15, 2024","329372.2","iPhone",1],[null,"120654.0","iPhone",1],[null,"120658.0","iPhone",1]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-019_stg_apple_store__app_session_daily.json](../023_reruns_impl-019_stg_apple_store__app_session_daily.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/apple_store.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-24 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-24'","count":1}]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2963|2959|10|101|否|
|L1|2963|2959|10|101|否|
|L2|2963|2959|10|101|否|
|L3|2963|2959|10|101|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":8,"app_id":8,"app_version":8,"device":8,"page_type":10,"platform_version":10,"sessions":10,"source_type":9,"territory":10,"total_session_duration":10,"unique_devices":10}`
- L1：`{"date_day":8,"app_id":8,"app_version":8,"device":8,"page_type":10,"platform_version":10,"sessions":10,"source_type":9,"territory":10,"total_session_duration":10,"unique_devices":10}`
- L2：`{"date_day":8,"app_id":8,"app_version":8,"device":8,"page_type":10,"platform_version":10,"sessions":10,"source_type":9,"territory":10,"total_session_duration":10,"unique_devices":10}`
- L3：`{"date_day":8,"app_id":8,"app_version":8,"device":8,"page_type":10,"platform_version":10,"sessions":10,"source_type":9,"territory":10,"total_session_duration":10,"unique_devices":10}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-019_stg_apple_store__app_session_daily/baseline.sql`；SHA-256 `fef2596c26f554a174fe83035167b551020e57b7631a044bf956a8614cd8d825`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2960|2959|7|68|否|
|L1|2960|2959|7|68|否|
|L2|2960|2959|7|68|否|
|L3|2960|2959|7|68|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`
- L1：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`
- L2：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`
- L3：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`

#### null_version_filter

判定：不计参与因素；类别候选 C。契约原式 NOT regexp(NULL) 为 UNKNOWN 而筛除；COALESCE 为空串额外保留。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 24 行起、字符 offset 1347 的唯一连续替换；其余字节不动。
替换前：
```sql
coalesce(cast(r.app_version AS VARCHAR), '')
```

替换后：
```sql
cast(r.app_version AS VARCHAR)
```

私有 SQL：`data/023_work/impl-019_stg_apple_store__app_session_daily/null_version_filter.sql`；SHA-256 `ae9be1d28f235778c0fcaa1b3e47b412de448f50d6b1d79df1fab087a477a978`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2960|2959|7|68|否|
|L1|2960|2959|7|68|否|
|L2|2960|2959|7|68|否|
|L3|2960|2959|7|68|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`
- L1：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`
- L2：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`
- L3：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`
### 补充轮：[023_supplement_reruns_impl-019_stg_apple_store__app_session_daily.json](../023_supplement_reruns_impl-019_stg_apple_store__app_session_daily.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/apple_store.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-24 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-24'","count":1}]`。

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_supplement_work/impl-019_stg_apple_store__app_session_daily/baseline.sql`；SHA-256 `fef2596c26f554a174fe83035167b551020e57b7631a044bf956a8614cd8d825`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2960|2959|7|68|否|
|L1|2960|2959|7|68|否|
|L2|2960|2959|7|68|否|
|L3|2960|2959|7|68|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`
- L1：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`
- L2：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`
- L3：`{"date_day":5,"app_id":5,"app_version":5,"device":5,"page_type":7,"platform_version":7,"sessions":7,"source_type":6,"territory":7,"total_session_duration":7,"unique_devices":7}`

#### semver_regex

判定：主因；类别候选 O。gold 使用双反斜杠而不接受普通三段数字版本；契约 YAML 解析后接受。

相对本轮基线减少行 4、格 44；按行优先、格次之排序。
共同控制后 SQL 第 4 行起、字符 offset 105 的唯一连续替换；其余字节不动。
替换前：
```sql
CASE WHEN r.app_version IS NULL THEN NULL WHEN regexp_matches(trim(cast(r.app_version AS VARCHAR)), '^[0-9]+(\.[0-9]+\.[0-9]+|)$') THEN trim(cast(r.app_version AS VARCHAR)) ELSE NULL END AS app_version
```

替换后：
```sql
CASE WHEN regexp_matches(cast(r.app_version AS VARCHAR), '^[0-9]+\\.[0-9]+\\.[0-9]+$') OR regexp_matches(cast(r.app_version AS VARCHAR), '^[0-9]+$') THEN cast(r.app_version AS VARCHAR) ELSE NULL END AS app_version
```

私有 SQL：`data/023_supplement_work/impl-019_stg_apple_store__app_session_daily/semver_regex.sql`；SHA-256 `02d187d38f2f91098cd05a0ebf5a34b14a591959b0a91654369a2e7187a13939`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2960|2959|3|24|否|
|L1|2960|2959|3|24|否|
|L2|2960|2959|3|24|否|
|L3|2960|2959|3|24|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":1,"app_id":1,"app_version":1,"device":1,"page_type":3,"platform_version":3,"sessions":3,"source_type":2,"territory":3,"total_session_duration":3,"unique_devices":3}`
- L1：`{"date_day":1,"app_id":1,"app_version":1,"device":1,"page_type":3,"platform_version":3,"sessions":3,"source_type":2,"territory":3,"total_session_duration":3,"unique_devices":3}`
- L2：`{"date_day":1,"app_id":1,"app_version":1,"device":1,"page_type":3,"platform_version":3,"sessions":3,"source_type":2,"territory":3,"total_session_duration":3,"unique_devices":3}`
- L3：`{"date_day":1,"app_id":1,"app_version":1,"device":1,"page_type":3,"platform_version":3,"sessions":3,"source_type":2,"territory":3,"total_session_duration":3,"unique_devices":3}`

#### date_filter_null

判定：参与因素；类别候选 A。日期输入格式支持范围未明确；每处过滤表达式分别修改。

相对本轮基线减少行 1、格 2；按行优先、格次之排序。
共同控制后 SQL 第 16 行起、字符 offset 1014 的唯一连续替换；其余字节不动。
替换前：
```sql
WHERE try_cast(r.date AS DATE) IS NOT NULL
```

替换后：
```sql
WHERE cast(coalesce(try_strptime(r.date,'%Y-%m-%d'),try_strptime(r.date,'%d-%m-%Y'),try_strptime(r.date,'%b %d, %Y')) as date) IS NOT NULL
```

私有 SQL：`data/023_supplement_work/impl-019_stg_apple_store__app_session_daily/date_filter_null.sql`；SHA-256 `c0dd3f1bacb796544720025b1e071d8d59456e5f36042992e38386b465d4f246`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2957|2959|6|66|否|
|L1|2957|2959|6|66|否|
|L2|2957|2959|6|66|否|
|L3|2957|2959|6|66|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`
- L1：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`
- L2：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`
- L3：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`

#### date_filter_upper

判定：参与因素；类别候选 A。日期输入格式支持范围未明确；每处过滤表达式分别修改。

相对本轮基线减少行 1、格 2；按行优先、格次之排序。
共同控制后 SQL 第 17 行起、字符 offset 1059 的唯一连续替换；其余字节不动。
替换前：
```sql
AND try_cast(r.date AS DATE) <= DATE '2025-10-24'
```

替换后：
```sql
AND cast(coalesce(try_strptime(r.date,'%Y-%m-%d'),try_strptime(r.date,'%d-%m-%Y'),try_strptime(r.date,'%b %d, %Y')) as date) <= DATE '2025-10-24'
```

私有 SQL：`data/023_supplement_work/impl-019_stg_apple_store__app_session_daily/date_filter_upper.sql`；SHA-256 `8e146b45d829d7126ee6139dddd31c91002e864b6e76691294fd7cc0dd9ae939`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2957|2959|6|66|否|
|L1|2957|2959|6|66|否|
|L2|2957|2959|6|66|否|
|L3|2957|2959|6|66|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`
- L1：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`
- L2：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`
- L3：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`

#### date_filter_lower

判定：参与因素；类别候选 A。日期输入格式支持范围未明确；每处过滤表达式分别修改。

相对本轮基线减少行 1、格 2；按行优先、格次之排序。
共同控制后 SQL 第 18 行起、字符 offset 1111 的唯一连续替换；其余字节不动。
替换前：
```sql
AND try_cast(r.date AS DATE) >= DATE '2020-01-01'
```

替换后：
```sql
AND cast(coalesce(try_strptime(r.date,'%Y-%m-%d'),try_strptime(r.date,'%d-%m-%Y'),try_strptime(r.date,'%b %d, %Y')) as date) >= DATE '2020-01-01'
```

私有 SQL：`data/023_supplement_work/impl-019_stg_apple_store__app_session_daily/date_filter_lower.sql`；SHA-256 `55218b0e9b0f00309e72c5b1830e610e58e38626c7bbc18160de381d543dd182`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2957|2959|6|66|否|
|L1|2957|2959|6|66|否|
|L2|2957|2959|6|66|否|
|L3|2957|2959|6|66|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`
- L1：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`
- L2：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`
- L3：`{"date_day":6,"app_id":6,"app_version":6,"device":6,"page_type":6,"platform_version":6,"sessions":6,"source_type":6,"territory":6,"total_session_duration":6,"unique_devices":6}`

## 规则问题

同一日期解析重复出现在不同代码位置，按用户本轮口径逐处计；它们存在交互，单点结果相同，分别记录。
