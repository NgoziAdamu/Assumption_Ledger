# impl-026 · stg_twitter_ads__campaign_regions_report

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

契约date_day为TIMESTAMP，gold实际为DATE；键中含日期时格式差异造成独有行。未提供的conversion指标0/NULL另逐列检验，未命中评测列或被键遮蔽的不算因素。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-026_stg_twitter_ads__campaign_regions_report.md](../024_packages/024_impl-026_stg_twitter_ads__campaign_regions_report.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。

```text
155:     - name: stg_twitter_ads__campaign_regions_report
156:       description: "Daily campaign performance by region within country and placement with normalized spend."
157:       source_table: raw.twitter_campaign_regions_report_data
158:       columns:
159:         - name: date_day
160:           data_type: TIMESTAMP
161:           constraints: [not_null]
162:         - name: region
163:           data_type: VARCHAR
164:         - name: country
165:           data_type: VARCHAR
166:         - name: account_id
167:           data_type: VARCHAR
168:           constraints: [not_null]
169:         - name: campaign_id
170:           data_type: VARCHAR
171:           constraints: [not_null]
172:         - name: placement
173:           data_type: VARCHAR
174:         - name: clicks
175:           data_type: BIGINT
176:         - name: impressions
177:           data_type: BIGINT
178:         - name: spend_micro
179:           data_type: BIGINT
180:         - name: spend
181:           data_type: DOUBLE
182:           description: "Spend amount rounded to 2 decimal places in SQL."
183:         - name: url_clicks
184:           data_type: BIGINT
185:         - name: conversion_purchases_metric
186:           data_type: BIGINT
187:         - name: conversion_custom_metric
188:           data_type: BIGINT
189:         - name: conversion_purchases_sale_amount
190:           data_type: DOUBLE
191:         - name: conversion_custom_sale_amount
192:           data_type: DOUBLE
193:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__campaign_regions_report.sql`；SHA-256 `4033d459e1f6925b540e2a7467e1bd8547bb627ad3a4a13aec69fe64069d1519`。

```text
1: select
2:     try_cast(date as timestamp) as date_day,
3:     region,
4:     country_region as country,
5:     account_id,
6:     campaign_id,
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
17: from raw.twitter_campaign_regions_report_data
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__campaign_regions_report.sql`；SHA-256 `8dfbf6bafd7a85f6b87a59f50198bbd6b49e39a63ec92d6e43521fd5cc0f2ce1`。

```text
1: select
2:   date_trunc('day', try_cast(date as timestamp)) as date_day,
3:   region as region,
4:   country_region as country,
5:   account_id,
6:   campaign_id,
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
17: from raw.twitter_campaign_regions_report_data
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('twitter_campaign_regions_report_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["twitter_campaign_regions_report_data","account_id","VARCHAR"],["twitter_campaign_regions_report_data","campaign_id","VARCHAR"],["twitter_campaign_regions_report_data","country_region","VARCHAR"],["twitter_campaign_regions_report_data","date","VARCHAR"],["twitter_campaign_regions_report_data","placement","VARCHAR"],["twitter_campaign_regions_report_data","_fivetran_synced","VARCHAR"],["twitter_campaign_regions_report_data","app_clicks","BIGINT"],["twitter_campaign_regions_report_data","billed_charge_local_micro","BIGINT"],["twitter_campaign_regions_report_data","billed_engagements","BIGINT"],["twitter_campaign_regions_report_data","card_engagements","BIGINT"],["twitter_campaign_regions_report_data","carousel_swipes","BIGINT"],["twitter_campaign_regions_report_data","clicks","BIGINT"],["twitter_campaign_regions_report_data","engagements","BIGINT"],["twitter_campaign_regions_report_data","follows","BIGINT"],["twitter_campaign_regions_report_data","impressions","BIGINT"],["twitter_campaign_regions_report_data","likes","BIGINT"],["twitter_campaign_regions_report_data","media_engagements","BIGINT"],["twitter_campaign_regions_report_data","media_views","BIGINT"],["twitter_campaign_regions_report_data","poll_card_vote","BIGINT"],["twitter_campaign_regions_report_data","qualified_impressions","BIGINT"],["twitter_campaign_regions_report_data","replies","BIGINT"],["twitter_campaign_regions_report_data","retweets","BIGINT"],["twitter_campaign_regions_report_data","tweets_send","BIGINT"],["twitter_campaign_regions_report_data","unfollows","BIGINT"],["twitter_campaign_regions_report_data","url_clicks","BIGINT"],["twitter_campaign_regions_report_data","region","VARCHAR"]]}
```

## 独立单点重跑

### 024_reruns_impl-026_stg_twitter_ads__campaign_regions_report.json
[024_reruns_impl-026_stg_twitter_ads__campaign_regions_report.json](../024_reruns_impl-026_stg_twitter_ads__campaign_regions_report.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|3000|33000|否|
|L1|1500|1500|3000|33000|否|
|L2|1500|1500|3000|33000|否|
|L3|1500|1500|3000|33000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L1：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L2：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L3：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`

#### baseline
私有SQL：`data/024_work/impl-026_stg_twitter_ads__campaign_regions_report/baseline.sql`；SHA-256 `4033d459e1f6925b540e2a7467e1bd8547bb627ad3a4a13aec69fe64069d1519`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|3000|33000|否|
|L1|1500|1500|3000|33000|否|
|L2|1500|1500|3000|33000|否|
|L3|1500|1500|3000|33000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L1：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L2：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L3：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`

#### date_type
主因；类别候选O。契约TIMESTAMP，留存gold为DATE；键列日期/午夜时间字符串也按评测键原样比较。
相对本轮基线：行减少3000，格减少33000。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第2行、offset 11起替换；其他字节相同。
原表达式：
```sql
try_cast(date as timestamp) as date_day
```

修改后：
```sql
cast(date as date) as date_day
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__campaign_regions_report/date_type.sql`；SHA-256 `4b84a5f0ab15245892e3b018c75cbbb0674556673fed28e65bdd2874126ca2cc`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|0|0|是|
|L1|1500|1500|0|0|是|
|L2|1500|1500|0|0|是|
|L3|1500|1500|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

#### conversion_purchases_metric
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第13行、offset 300起替换；其他字节相同。
原表达式：
```sql
cast(null as bigint) as conversion_purchases_metric
```

修改后：
```sql
cast(0 as bigint) as conversion_purchases_metric
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__campaign_regions_report/conversion_purchases_metric.sql`；SHA-256 `46f1e97e0abbdf4fc41003ebdd75d4a683570360637f8f9aad047ed795fa3496`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|3000|33000|否|
|L1|1500|1500|3000|33000|否|
|L2|1500|1500|3000|33000|否|
|L3|1500|1500|3000|33000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L1：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L2：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L3：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`

#### conversion_custom_metric
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第14行、offset 357起替换；其他字节相同。
原表达式：
```sql
cast(null as bigint) as conversion_custom_metric
```

修改后：
```sql
cast(0 as bigint) as conversion_custom_metric
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__campaign_regions_report/conversion_custom_metric.sql`；SHA-256 `3fafd648a1cac550cf1a09505f92328694886dc69cdedcd28b59e2a9ee14711c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|3000|33000|否|
|L1|1500|1500|3000|33000|否|
|L2|1500|1500|3000|33000|否|
|L3|1500|1500|3000|33000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L1：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L2：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L3：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`

#### conversion_purchases_sale_amount
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第15行、offset 411起替换；其他字节相同。
原表达式：
```sql
cast(null as double) as conversion_purchases_sale_amount
```

修改后：
```sql
cast(0 as double) as conversion_purchases_sale_amount
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__campaign_regions_report/conversion_purchases_sale_amount.sql`；SHA-256 `9d7e3238f1ffd1bbe9e33081df0f6b0116638891b030c5b794d9573ed09b9a24`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|3000|33000|否|
|L1|1500|1500|3000|33000|否|
|L2|1500|1500|3000|33000|否|
|L3|1500|1500|3000|33000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L1：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L2：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L3：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`

#### conversion_custom_sale_amount
不计参与因素；类别候选A。原始源没有该指标，契约未规定0或NULL。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第16行、offset 473起替换；其他字节相同。
原表达式：
```sql
cast(null as double) as conversion_custom_sale_amount
```

修改后：
```sql
cast(0 as double) as conversion_custom_sale_amount
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__campaign_regions_report/conversion_custom_sale_amount.sql`；SHA-256 `604221f24198c1070725767d723bed31d424d11445e23dd031cc3ba7c67efd61`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|3000|33000|否|
|L1|1500|1500|3000|33000|否|
|L2|1500|1500|3000|33000|否|
|L3|1500|1500|3000|33000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L1：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L2：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
- L3：`{"account_id":3000,"campaign_id":3000,"date_day":3000,"region":3000,"country":3000,"placement":3000,"clicks":3000,"impressions":3000,"spend":3000,"spend_micro":3000,"url_clicks":3000}`
## 规则问题

无。

