# impl-026 · stg_twitter_ads__promoted_tweet_report

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

契约date_day为TIMESTAMP，gold实际为DATE；键中含日期时格式差异造成独有行。未提供的conversion指标0/NULL另逐列检验，未命中评测列或被键遮蔽的不算因素。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-026_stg_twitter_ads__promoted_tweet_report.md](../024_packages/024_impl-026_stg_twitter_ads__promoted_tweet_report.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。

```text
392:     - name: stg_twitter_ads__promoted_tweet_report
393:       description: "Daily promoted tweet performance per placement with normalized spend."
394:       source_table: raw.twitter_promoted_tweet_report_data
395:       columns:
396:         - name: date_ts
397:           data_type: TIMESTAMP
398:         - name: date_day
399:           data_type: TIMESTAMP
400:           constraints: [not_null]
401:         - name: account_id
402:           data_type: VARCHAR
403:           constraints: [not_null]
404:         - name: promoted_tweet_id
405:           data_type: VARCHAR
406:           constraints: [not_null]
407:         - name: placement
408:           data_type: VARCHAR
409:         - name: clicks
410:           data_type: BIGINT
411:         - name: impressions
412:           data_type: BIGINT
413:         - name: spend_micro
414:           data_type: BIGINT
415:         - name: spend
416:           data_type: DOUBLE
417:           description: "Spend amount rounded to 2 decimal places in SQL."
418:         - name: url_clicks
419:           data_type: BIGINT
420:         - name: conversion_purchases_metric
421:           data_type: BIGINT
422:         - name: conversion_custom_metric
423:           data_type: BIGINT
424:         - name: conversion_purchases_sale_amount
425:           data_type: DOUBLE
426:         - name: conversion_custom_sale_amount
427:           data_type: DOUBLE
428:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__promoted_tweet_report.sql`；SHA-256 `139243fcb6aa16e7642d484ba06ee29639f3e6087f76f1a0b3eea69fcd9cf11a`。

```text
1: select
2:     try_cast(date as timestamp) as date_day,
3:     account_id,
4:     promoted_tweet_id,
5:     placement,
6:     clicks,
7:     impressions,
8:     billed_charge_local_micro as spend_micro,
9:     round(billed_charge_local_micro / 1000000.0, 2) as spend,
10:     url_clicks,
11:     cast(null as bigint) as conversion_purchases_metric,
12:     cast(null as bigint) as conversion_custom_metric,
13:     cast(null as double) as conversion_purchases_sale_amount,
14:     cast(null as double) as conversion_custom_sale_amount
15: from raw.twitter_promoted_tweet_report_data
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__promoted_tweet_report.sql`；SHA-256 `6aae291f86aecb7e80a901b36c6d7026243123d76aeb4268a135d2c81fc4cf4c`。

```text
1: select
2:   try_cast(date as timestamp) as date_ts,
3:   date_trunc('day', try_cast(date as timestamp)) as date_day,
4:   account_id,
5:   promoted_tweet_id,
6:   placement,
7:   clicks,
8:   impressions,
9:   billed_charge_local_micro as spend_micro,
10:   round(billed_charge_local_micro/1000000.0, 2) as spend,
11:   url_clicks,
12:   0::BIGINT as conversion_purchases_metric,
13:   0::BIGINT as conversion_custom_metric,
14:   0.0::DOUBLE as conversion_purchases_sale_amount,
15:   0.0::DOUBLE as conversion_custom_sale_amount
16: from raw.twitter_promoted_tweet_report_data
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- date_type（O）：**看到了但没提**；事件 9、10、13、21、22、35。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 9：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/9.json`；命令首行：`python - <<'PY'`。
event 10：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/10.json`；原始观察输出。
event 13：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/13.json`；命令首行：`mkdir -p sql/staging sql/intermediate sql/marts; cat > /tmp/gen.py <<'PY'`。
event 21：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/21.json`；命令首行：`python - <<'PY'`。
event 22：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/22.json`；原始观察输出。
event 35：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/35.json`；命令首行：`cat > result.md <<'EOF'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

Implemented the Twitter Ads SQL pipeline in `sql/staging/`, `sql/intermediate/`, and `sql/marts/` (12 staging, 12 intermediate, and 8 marts models). SQL uses DuckDB syntax, direct `schema.table` references, and no trailing semicolons.

**Verification:** Ran `python run.py` successfully. All configured models were created in their expected schemas, and the final run completed with `✅ Success` and no SQL errors.

**Implementation and data quality notes:**
- Staging applies field renames, timestamp/date parsing, status normalization and filtering, latest-version flags, spend conversions from micro-units, URL parsing, and tweet language validation.
- Intermediate models preserve configured source grains and derive conversion totals. Marts use left joins and aggregate metrics at configured dimensions, retaining unmatched dimension rows and SQL `SUM` NULL behavior.
- The raw Twitter report tables do not contain the contract’s conversion metric or conversion sale amount columns. Staging emits typed NULLs for these unavailable values; the intermediate logic treats them as zero per contract. The calculated totals consequently cannot represent actual conversions from this raw extract.
- The raw keyword report does not contain `keyword_id`; that field is derived from available `keyword` text, so uniqueness beyond keyword text is not guaranteed.
- The contract requests correction of unsupported timezones without specifying a fallback; invalid timezone values are set to `UTC`. UTC markers are removed before timestamp parsing. Tweet timestamps use a broad 2006–2100 bound because exact limits are unspecified.
- URL source `index` values are NULL in this extract. The first-URL model applies NULL-as-999999 ordering as specified; tied rows remain nondeterministic per the contract.

An initial test run exposed an unavailable source `keyword_id`, which caused the keyword intermediate and mart to fail. The staging projection was adjusted to derive it from `keyword`. The subsequent full run succeeded. The only unresolved contract/data limitation is the unavailable conversion fields in raw report sources.
```

## 查询

核实查询 **1** 条；代价档：**一条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('twitter_promoted_tweet_report_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["twitter_promoted_tweet_report_data","account_id","VARCHAR"],["twitter_promoted_tweet_report_data","campaign_id","VARCHAR"],["twitter_promoted_tweet_report_data","line_item_id","VARCHAR"],["twitter_promoted_tweet_report_data","promoted_tweet_id","VARCHAR"],["twitter_promoted_tweet_report_data","date","VARCHAR"],["twitter_promoted_tweet_report_data","placement","VARCHAR"],["twitter_promoted_tweet_report_data","_fivetran_synced","VARCHAR"],["twitter_promoted_tweet_report_data","app_clicks","BIGINT"],["twitter_promoted_tweet_report_data","billed_charge_local_micro","BIGINT"],["twitter_promoted_tweet_report_data","billed_engagements","BIGINT"],["twitter_promoted_tweet_report_data","card_engagements","BIGINT"],["twitter_promoted_tweet_report_data","carousel_swipes","BIGINT"],["twitter_promoted_tweet_report_data","clicks","BIGINT"],["twitter_promoted_tweet_report_data","engagements","BIGINT"],["twitter_promoted_tweet_report_data","follows","BIGINT"],["twitter_promoted_tweet_report_data","impressions","BIGINT"],["twitter_promoted_tweet_report_data","likes","BIGINT"],["twitter_promoted_tweet_report_data","media_engagements","BIGINT"],["twitter_promoted_tweet_report_data","media_views","BIGINT"],["twitter_promoted_tweet_report_data","poll_card_vote","BIGINT"],["twitter_promoted_tweet_report_data","qualified_impressions","BIGINT"],["twitter_promoted_tweet_report_data","replies","BIGINT"],["twitter_promoted_tweet_report_data","retweets","BIGINT"],["twitter_promoted_tweet_report_data","tweets_send","BIGINT"],["twitter_promoted_tweet_report_data","unfollows","BIGINT"],["twitter_promoted_tweet_report_data","url_clicks","BIGINT"]]}
```

## 独立单点重跑

### 024_reruns_impl-026_stg_twitter_ads__promoted_tweet_report.json
[024_reruns_impl-026_stg_twitter_ads__promoted_tweet_report.json](../024_reruns_impl-026_stg_twitter_ads__promoted_tweet_report.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|5000|55000|否|
|L1|2500|2500|5000|55000|否|
|L2|2500|2500|5000|55000|否|
|L3|2500|2500|5000|55000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L1：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L2：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L3：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`

#### baseline
私有SQL：`data/024_work/impl-026_stg_twitter_ads__promoted_tweet_report/baseline.sql`；SHA-256 `139243fcb6aa16e7642d484ba06ee29639f3e6087f76f1a0b3eea69fcd9cf11a`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|5000|55000|否|
|L1|2500|2500|5000|55000|否|
|L2|2500|2500|5000|55000|否|
|L3|2500|2500|5000|55000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L1：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L2：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L3：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`

#### date_type
主因；类别候选O。契约TIMESTAMP，留存gold为DATE；键列日期/午夜时间字符串也按评测键原样比较。
相对本轮基线：行减少2500，格减少50000。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第2行、offset 11起替换；其他字节相同。
原表达式：
```sql
try_cast(date as timestamp) as date_day
```

修改后：
```sql
cast(date as date) as date_day
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__promoted_tweet_report/date_type.sql`；SHA-256 `a01fdbf5c12a81574ef7cf7a8e339728a34e3e4ed3411c3a947470b47ec48393`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2500|5000|否|
|L1|2500|2500|2500|5000|否|
|L2|2500|2500|2500|5000|否|
|L3|2500|2500|2500|5000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"conversion_custom_metric":2500,"conversion_purchases_metric":2500}`
- L1：`{"conversion_custom_metric":2500,"conversion_purchases_metric":2500}`
- L2：`{"conversion_custom_metric":2500,"conversion_purchases_metric":2500}`
- L3：`{"conversion_custom_metric":2500,"conversion_purchases_metric":2500}`

#### conversion_purchases_metric
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 263起替换；其他字节相同。
原表达式：
```sql
cast(null as bigint) as conversion_purchases_metric
```

修改后：
```sql
cast(0 as bigint) as conversion_purchases_metric
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__promoted_tweet_report/conversion_purchases_metric.sql`；SHA-256 `5d6da3ed554534a599bf1a9fe4077eed3e1f8314bbbee334b00d862e29d441af`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|5000|55000|否|
|L1|2500|2500|5000|55000|否|
|L2|2500|2500|5000|55000|否|
|L3|2500|2500|5000|55000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L1：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L2：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L3：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`

#### conversion_custom_metric
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第12行、offset 320起替换；其他字节相同。
原表达式：
```sql
cast(null as bigint) as conversion_custom_metric
```

修改后：
```sql
cast(0 as bigint) as conversion_custom_metric
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__promoted_tweet_report/conversion_custom_metric.sql`；SHA-256 `85cb614b31e034b1f78f61836ac8d6e0caaa8076cc21559829b559c87b4e7bed`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|5000|55000|否|
|L1|2500|2500|5000|55000|否|
|L2|2500|2500|5000|55000|否|
|L3|2500|2500|5000|55000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L1：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L2：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L3：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`

#### conversion_purchases_sale_amount
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第13行、offset 374起替换；其他字节相同。
原表达式：
```sql
cast(null as double) as conversion_purchases_sale_amount
```

修改后：
```sql
cast(0 as double) as conversion_purchases_sale_amount
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__promoted_tweet_report/conversion_purchases_sale_amount.sql`；SHA-256 `c06f504e539ce54b3bad0cafd5bfc378a9869b51029955882a3156add3a88d39`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|5000|55000|否|
|L1|2500|2500|5000|55000|否|
|L2|2500|2500|5000|55000|否|
|L3|2500|2500|5000|55000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L1：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L2：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L3：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`

#### conversion_custom_sale_amount
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第14行、offset 436起替换；其他字节相同。
原表达式：
```sql
cast(null as double) as conversion_custom_sale_amount
```

修改后：
```sql
cast(0 as double) as conversion_custom_sale_amount
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__promoted_tweet_report/conversion_custom_sale_amount.sql`；SHA-256 `3a09fab96c8cd0845d723a2fc7027546e045f38639c71c2d19f9d9d216c202c8`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|5000|55000|否|
|L1|2500|2500|5000|55000|否|
|L2|2500|2500|5000|55000|否|
|L3|2500|2500|5000|55000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L1：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L2：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
- L3：`{"account_id":5000,"promoted_tweet_id":5000,"date_day":5000,"placement":5000,"clicks":5000,"conversion_custom_metric":5000,"conversion_purchases_metric":5000,"impressions":5000,"spend":5000,"spend_micro":5000,"url_clicks":5000}`
## 规则问题

无。

