# impl-026 · stg_twitter_ads__line_item_keywords_report

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**多因并列（A、O）**；把握：中。

契约date_day为TIMESTAMP，gold实际为DATE；键中含日期时格式差异造成独有行。未提供的conversion指标0/NULL另逐列检验，未命中评测列或被键遮蔽的不算因素。 keyword_id文本或组合MD5也未在契约定义，单改与日期改动各减少1500格。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-026_stg_twitter_ads__line_item_keywords_report.md](../024_packages/024_impl-026_stg_twitter_ads__line_item_keywords_report.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。

```text
293:     - name: stg_twitter_ads__line_item_keywords_report
294:       description: "Daily keyword performance per line item and placement with normalized spend and derived keyword_id."
295:       source_table: raw.twitter_line_item_keywords_report_data
296:       columns:
297:         - name: date_day
298:           data_type: TIMESTAMP
299:           constraints: [not_null]
300:         - name: account_id
301:           data_type: VARCHAR
302:           constraints: [not_null]
303:         - name: line_item_id
304:           data_type: VARCHAR
305:           constraints: [not_null]
306:         - name: keyword
307:           data_type: VARCHAR
308:         - name: keyword_id
309:           data_type: VARCHAR
310:         - name: placement
311:           data_type: VARCHAR
312:         - name: clicks
313:           data_type: BIGINT
314:         - name: impressions
315:           data_type: BIGINT
316:         - name: spend_micro
317:           data_type: BIGINT
318:         - name: spend
319:           data_type: DOUBLE
320:           description: "Spend amount rounded to 2 decimal places in SQL."
321:         - name: url_clicks
322:           data_type: BIGINT
323:         - name: conversion_purchases_metric
324:           data_type: BIGINT
325:         - name: conversion_custom_metric
326:           data_type: BIGINT
327:         - name: conversion_purchases_sale_amount
328:           data_type: DOUBLE
329:         - name: conversion_custom_sale_amount
330:           data_type: DOUBLE
331:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__line_item_keywords_report.sql`；SHA-256 `511496473e5d0c72ba5ae5fa4c09aae0b6bdb19765a34cbc11d9d30725b30124`。

```text
1: select
2:     try_cast(date as timestamp) as date_day,
3:     account_id,
4:     line_item_id,
5:     keyword as keyword_id,
6:     keyword,
7:     placement,
8:     clicks,
9:     impressions,
10:     billed_charge_local_micro as spend_micro,
11:     round(billed_charge_local_micro / 1000000.0, 2) as spend,
12:     url_clicks,
13:     cast(null as bigint) as conversion_purchases_metric,
14:     cast(null as bigint) as conversion_custom_metric,
15:     cast(null as double) as conversion_purchases_sale_amount,
16:     cast(null as double) as conversion_custom_sale_amount
17: from raw.twitter_line_item_keywords_report_data
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__line_item_keywords_report.sql`；SHA-256 `a9a95a81a5075742610ce335277f6191a674c2c855a9bb9a186fa4fcdd9ccc11`。

```text
1: select
2:   date_trunc('day', try_cast(date as timestamp)) as date_day,
3:   account_id,
4:   line_item_id,
5:   keyword as keyword,
6:   md5(account_id || '-' || line_item_id || '-' || coalesce(keyword,'') || '-' || coalesce(placement,'')) as keyword_id,
7:   placement,
8:   clicks,
9:   impressions,
10:   billed_charge_local_micro as spend_micro,
11:   round(billed_charge_local_micro/1000000.0, 2) as spend,
12:   url_clicks,
13:   0::BIGINT as conversion_purchases_metric,
14:   0::BIGINT as conversion_custom_metric,
15:   0.0::DOUBLE as conversion_purchases_sale_amount,
16:   0.0::DOUBLE as conversion_custom_sale_amount
17: from raw.twitter_line_item_keywords_report_data
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- date_type（O）：**看到了但没提**；事件 9、10、13、21、22、35。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。

- keyword_id（A）：**针对本表的具体说明**；事件 35。
原句：

```
The raw keyword report does not contain `keyword_id`; that field is derived from available `keyword` text, so uniqueness beyond keyword text is not guaranteed.
```

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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('twitter_line_item_keywords_report_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["twitter_line_item_keywords_report_data","account_id","VARCHAR"],["twitter_line_item_keywords_report_data","campaign_id","VARCHAR"],["twitter_line_item_keywords_report_data","line_item_id","VARCHAR"],["twitter_line_item_keywords_report_data","date","VARCHAR"],["twitter_line_item_keywords_report_data","placement","VARCHAR"],["twitter_line_item_keywords_report_data","_fivetran_synced","VARCHAR"],["twitter_line_item_keywords_report_data","app_clicks","BIGINT"],["twitter_line_item_keywords_report_data","billed_charge_local_micro","BIGINT"],["twitter_line_item_keywords_report_data","billed_engagements","BIGINT"],["twitter_line_item_keywords_report_data","card_engagements","BIGINT"],["twitter_line_item_keywords_report_data","carousel_swipes","BIGINT"],["twitter_line_item_keywords_report_data","clicks","BIGINT"],["twitter_line_item_keywords_report_data","engagements","BIGINT"],["twitter_line_item_keywords_report_data","follows","BIGINT"],["twitter_line_item_keywords_report_data","impressions","BIGINT"],["twitter_line_item_keywords_report_data","likes","BIGINT"],["twitter_line_item_keywords_report_data","media_engagements","BIGINT"],["twitter_line_item_keywords_report_data","media_views","BIGINT"],["twitter_line_item_keywords_report_data","poll_card_vote","BIGINT"],["twitter_line_item_keywords_report_data","qualified_impressions","BIGINT"],["twitter_line_item_keywords_report_data","replies","BIGINT"],["twitter_line_item_keywords_report_data","retweets","BIGINT"],["twitter_line_item_keywords_report_data","tweets_send","BIGINT"],["twitter_line_item_keywords_report_data","unfollows","BIGINT"],["twitter_line_item_keywords_report_data","url_clicks","BIGINT"],["twitter_line_item_keywords_report_data","keyword","VARCHAR"]]}
```

## 独立单点重跑

### 024_reruns_impl-026_stg_twitter_ads__line_item_keywords_report.json
[024_reruns_impl-026_stg_twitter_ads__line_item_keywords_report.json](../024_reruns_impl-026_stg_twitter_ads__line_item_keywords_report.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|1500|3000|否|
|L1|1500|1500|1500|3000|否|
|L2|1500|1500|1500|3000|否|
|L3|1500|1500|1500|1500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":1500,"keyword_id":1500}`
- L1：`{"date_day":1500,"keyword_id":1500}`
- L2：`{"date_day":1500,"keyword_id":1500}`
- L3：`{"keyword_id":1500}`

#### baseline
私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_keywords_report/baseline.sql`；SHA-256 `511496473e5d0c72ba5ae5fa4c09aae0b6bdb19765a34cbc11d9d30725b30124`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|1500|3000|否|
|L1|1500|1500|1500|3000|否|
|L2|1500|1500|1500|3000|否|
|L3|1500|1500|1500|1500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":1500,"keyword_id":1500}`
- L1：`{"date_day":1500,"keyword_id":1500}`
- L2：`{"date_day":1500,"keyword_id":1500}`
- L3：`{"keyword_id":1500}`

#### date_type
主因；类别候选O。契约TIMESTAMP，留存gold为DATE；键列日期/午夜时间字符串也按评测键原样比较。
相对本轮基线：行减少0，格减少1500。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第2行、offset 11起替换；其他字节相同。
原表达式：
```sql
try_cast(date as timestamp) as date_day
```

修改后：
```sql
cast(date as date) as date_day
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_keywords_report/date_type.sql`；SHA-256 `be60b477f573b7d2ed8a740192655039038d0e695a728213efcb0fe94dae1948`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|1500|1500|否|
|L1|1500|1500|1500|1500|否|
|L2|1500|1500|1500|1500|否|
|L3|1500|1500|1500|1500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"keyword_id":1500}`
- L1：`{"keyword_id":1500}`
- L2：`{"keyword_id":1500}`
- L3：`{"keyword_id":1500}`

#### conversion_purchases_metric
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第13行、offset 298起替换；其他字节相同。
原表达式：
```sql
cast(null as bigint) as conversion_purchases_metric
```

修改后：
```sql
cast(0 as bigint) as conversion_purchases_metric
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_keywords_report/conversion_purchases_metric.sql`；SHA-256 `101b931157c254233764228cb5bcfb474501ff662c09040fc5fc0e598fa6918f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|1500|3000|否|
|L1|1500|1500|1500|3000|否|
|L2|1500|1500|1500|3000|否|
|L3|1500|1500|1500|1500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":1500,"keyword_id":1500}`
- L1：`{"date_day":1500,"keyword_id":1500}`
- L2：`{"date_day":1500,"keyword_id":1500}`
- L3：`{"keyword_id":1500}`

#### conversion_custom_metric
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第14行、offset 355起替换；其他字节相同。
原表达式：
```sql
cast(null as bigint) as conversion_custom_metric
```

修改后：
```sql
cast(0 as bigint) as conversion_custom_metric
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_keywords_report/conversion_custom_metric.sql`；SHA-256 `dc0c7b51d222b65bd15d83e5fe58ef234690fa8cb976a4653366ca992c1791c8`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|1500|3000|否|
|L1|1500|1500|1500|3000|否|
|L2|1500|1500|1500|3000|否|
|L3|1500|1500|1500|1500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":1500,"keyword_id":1500}`
- L1：`{"date_day":1500,"keyword_id":1500}`
- L2：`{"date_day":1500,"keyword_id":1500}`
- L3：`{"keyword_id":1500}`

#### conversion_purchases_sale_amount
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第15行、offset 409起替换；其他字节相同。
原表达式：
```sql
cast(null as double) as conversion_purchases_sale_amount
```

修改后：
```sql
cast(0 as double) as conversion_purchases_sale_amount
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_keywords_report/conversion_purchases_sale_amount.sql`；SHA-256 `f5628fa71dfc6a85f6e8cce271c4094d6285c9249d4d9531021e974b3a550a43`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|1500|3000|否|
|L1|1500|1500|1500|3000|否|
|L2|1500|1500|1500|3000|否|
|L3|1500|1500|1500|1500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":1500,"keyword_id":1500}`
- L1：`{"date_day":1500,"keyword_id":1500}`
- L2：`{"date_day":1500,"keyword_id":1500}`
- L3：`{"keyword_id":1500}`

#### conversion_custom_sale_amount
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第16行、offset 471起替换；其他字节相同。
原表达式：
```sql
cast(null as double) as conversion_custom_sale_amount
```

修改后：
```sql
cast(0 as double) as conversion_custom_sale_amount
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_keywords_report/conversion_custom_sale_amount.sql`；SHA-256 `d3e9dd3fa5afbb65f44cc4c7c5a4d853d7dd28cb681c48f2d0d5aaa7d87df8e1`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|1500|3000|否|
|L1|1500|1500|1500|3000|否|
|L2|1500|1500|1500|3000|否|
|L3|1500|1500|1500|1500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":1500,"keyword_id":1500}`
- L1：`{"date_day":1500,"keyword_id":1500}`
- L2：`{"date_day":1500,"keyword_id":1500}`
- L3：`{"keyword_id":1500}`

#### keyword_id
主因；类别候选A。契约未规定 keyword_id 推导规则，raw无该列；keyword文本与组合MD5是未定选择。
相对本轮基线：行减少0，格减少1500。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第5行、offset 90起替换；其他字节相同。
原表达式：
```sql
keyword as keyword_id
```

修改后：
```sql
md5(account_id || '-' || line_item_id || '-' || coalesce(keyword,'') || '-' || coalesce(placement,'')) as keyword_id
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_keywords_report/keyword_id.sql`；SHA-256 `c1619ad99b0b1121c89c21dd27d7a4c3578015f1815220354627be4944cf3b37`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|1500|1500|否|
|L1|1500|1500|1500|1500|否|
|L2|1500|1500|1500|1500|否|
|L3|1500|1500|0|0|是|

首次整表匹配：**L3**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":1500}`
- L1：`{"date_day":1500}`
- L2：`{"date_day":1500}`
- L3：`{}`
## 规则问题

无。

