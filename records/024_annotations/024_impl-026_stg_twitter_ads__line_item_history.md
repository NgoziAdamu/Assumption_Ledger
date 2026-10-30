# impl-026 · stg_twitter_ads__line_item_history

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

agent按契约BIGINT、DECIMAL(18,2)/(18,1)输出，gold为DOUBLE且budget两位小数。四个位置分别诊断，主要类型差异按行排序。

参与因素：O：bid_amount（行减0，格减1375）；O：total_budget_amount_local_micro（行减0，格减2487）；O：total_budget_amount（行减0，格减2240）。
标记：无。

## 材料与比较口径

[024_impl-026_stg_twitter_ads__line_item_history.md](../024_packages/024_impl-026_stg_twitter_ads__line_item_history.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。

```text
229:     - name: stg_twitter_ads__line_item_history
230:       description: "Cleaned line item attributes with monetary conversions and latest-version flag."
231:       source_table: raw.twitter_line_item_history_data
232:       columns:
233:         - name: advertiser_domain
234:           data_type: VARCHAR
235:         - name: advertiser_user_id
236:           data_type: BIGINT
237:         - name: automatically_select_bid
238:           data_type: BOOLEAN
239:         - name: bid_amount_local_micro
240:           data_type: BIGINT
241:         - name: bid_amount
242:           data_type: DECIMAL(18,2)
243:         - name: bid_type
244:           data_type: VARCHAR
245:         - name: bid_unit
246:           data_type: VARCHAR
247:         - name: campaign_id
248:           data_type: VARCHAR
249:           constraints: [not_null]
250:         - name: charge_by
251:           data_type: VARCHAR
252:         - name: created_timestamp
253:           data_type: TIMESTAMP
254:         - name: creative_source
255:           data_type: VARCHAR
256:         - name: currency
257:           data_type: VARCHAR
258:         - name: is_deleted
259:           data_type: BOOLEAN
260:         - name: end_timestamp
261:           data_type: TIMESTAMP
262:         - name: entity_status
263:           data_type: VARCHAR
264:         - name: line_item_id
265:           data_type: VARCHAR
266:           constraints: [not_null]
267:         - name: name
268:           data_type: VARCHAR
269:         - name: objective
270:           data_type: VARCHAR
271:         - name: optimization
272:           data_type: VARCHAR
273:         - name: primary_web_event_tag
274:           data_type: VARCHAR
275:         - name: product_type
276:           data_type: VARCHAR
277:         - name: start_timestamp
278:           data_type: TIMESTAMP
279:         - name: target_cpa_local_micro
280:           data_type: BIGINT
281:         - name: target_cpa
282:           data_type: DOUBLE
283:         - name: total_budget_amount_local_micro
284:           data_type: BIGINT
285:         - name: total_budget_amount
286:           data_type: DECIMAL(18,1)
287:         - name: updated_timestamp
288:           data_type: TIMESTAMP
289:         - name: is_latest_version
290:           data_type: BOOLEAN
291:           constraints: [not_null]
292:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__line_item_history.sql`；SHA-256 `e7878e8d0c56f1f16eb4b5dd717ef8a4501fd2760c99d9d9cd8d1ab845d3e3c1`。

```text
1: with cleaned as (
2:     select advertiser_domain, advertiser_user_id, automatically_select_bid,
3:         cast(bid_amount_local_micro as bigint) as bid_amount_local_micro,
4:         cast(round(bid_amount_local_micro / 1000000.0, 2) as decimal(18,2)) as bid_amount,
5:         bid_type, bid_unit, campaign_id, charge_by,
6:         try_cast(replace(created_at, ' UTC', '') as timestamp) as created_timestamp,
7:         creative_source, currency, deleted as is_deleted,
8:         try_cast(replace(cast(end_time as varchar), ' UTC', '') as timestamp) as end_timestamp,
9:         entity_status, id as line_item_id, name,
10:         objective, optimization, cast(primary_web_event_tag as varchar) as primary_web_event_tag,
11:         product_type, try_cast(replace(start_time, ' UTC', '') as timestamp) as start_timestamp,
12:         cast(target_cpa_local_micro as bigint) as target_cpa_local_micro,
13:         target_cpa_local_micro / 1000000.0 as target_cpa,
14:         cast(total_budget_amount_local_micro as bigint) as total_budget_amount_local_micro,
15:         cast(round(total_budget_amount_local_micro / 1000000.0, 1) as decimal(18,1)) as total_budget_amount,
16:         try_cast(replace(updated_at, ' UTC', '') as timestamp) as updated_timestamp
17:     from raw.twitter_line_item_history_data where id is not null and campaign_id is not null
18: ), versioned as (
19:     select *, row_number() over (partition by line_item_id order by updated_timestamp desc nulls last) = 1 as is_latest_version from cleaned
20: )
21: select * from versioned
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__line_item_history.sql`；SHA-256 `bca1271b4ce692996819a732fecca80c66e5c67de801b7afefae3db30ec1daec`。

```text
1: with src as (
2:   select
3:     advertiser_domain,
4:     advertiser_user_id,
5:     automatically_select_bid,
6:     bid_amount_local_micro,
7:     bid_type,
8:     bid_unit,
9:     campaign_id,
10:     charge_by,
11:     try_cast(created_at as timestamp) as created_timestamp,
12:     creative_source,
13:     currency,
14:     coalesce(cast(deleted as boolean), false) as is_deleted,
15:     try_cast(end_time as timestamp) as end_timestamp,
16:     upper(trim(entity_status)) as entity_status,
17:     id as line_item_id,
18:     name,
19:     objective,
20:     optimization,
21:     primary_web_event_tag,
22:     product_type,
23:     try_cast(start_time as timestamp) as start_timestamp,
24:     target_cpa_local_micro,
25:     total_budget_amount_local_micro,
26:     try_cast(updated_at as timestamp) as updated_timestamp
27:   from raw.twitter_line_item_history_data
28: ), latest as (
29:   select *, row_number() over(partition by line_item_id order by updated_timestamp desc nulls last) as rn
30:   from src
31: )
32: select
33:   advertiser_domain,
34:   advertiser_user_id,
35:   automatically_select_bid,
36:   bid_amount_local_micro,
37:   round(bid_amount_local_micro/1000000.0, 2) as bid_amount,
38:   bid_type,
39:   bid_unit,
40:   campaign_id,
41:   charge_by,
42:   created_timestamp,
43:   creative_source,
44:   currency,
45:   is_deleted,
46:   end_timestamp,
47:   entity_status,
48:   line_item_id,
49:   name,
50:   objective,
51:   optimization,
52:   primary_web_event_tag,
53:   product_type,
54:   start_timestamp,
55:   target_cpa_local_micro,
56:   round(target_cpa_local_micro/1000000.0, 2) as target_cpa,
57:   total_budget_amount_local_micro,
58:   round(total_budget_amount_local_micro/1000000.0, 2) as total_budget_amount,
59:   updated_timestamp,
60:   (rn = 1) as is_latest_version
61: from latest
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- bid_amount_local_micro（O）：**看到了但没提**；事件 9、10、13。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 9：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/9.json`；命令首行：`python - <<'PY'`。
event 10：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/10.json`；原始观察输出。
event 13：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/13.json`；命令首行：`mkdir -p sql/staging sql/intermediate sql/marts; cat > /tmp/gen.py <<'PY'`。

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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('twitter_line_item_history_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["twitter_line_item_history_data","advertiser_domain","VARCHAR"],["twitter_line_item_history_data","advertiser_user_id","BIGINT"],["twitter_line_item_history_data","automatically_select_bid","BOOLEAN"],["twitter_line_item_history_data","bid_amount_local_micro","DOUBLE"],["twitter_line_item_history_data","bid_type","VARCHAR"],["twitter_line_item_history_data","bid_unit","VARCHAR"],["twitter_line_item_history_data","campaign_id","VARCHAR"],["twitter_line_item_history_data","charge_by","VARCHAR"],["twitter_line_item_history_data","created_at","VARCHAR"],["twitter_line_item_history_data","creative_source","VARCHAR"],["twitter_line_item_history_data","currency","VARCHAR"],["twitter_line_item_history_data","deleted","BOOLEAN"],["twitter_line_item_history_data","end_time","DOUBLE"],["twitter_line_item_history_data","entity_status","VARCHAR"],["twitter_line_item_history_data","id","VARCHAR"],["twitter_line_item_history_data","name","VARCHAR"],["twitter_line_item_history_data","objective","VARCHAR"],["twitter_line_item_history_data","optimization","VARCHAR"],["twitter_line_item_history_data","primary_web_event_tag","DOUBLE"],["twitter_line_item_history_data","product_type","VARCHAR"],["twitter_line_item_history_data","start_time","VARCHAR"],["twitter_line_item_history_data","target_cpa_local_micro","DOUBLE"],["twitter_line_item_history_data","total_budget_amount_local_micro","DOUBLE"],["twitter_line_item_history_data","updated_at","VARCHAR"]]}
```

## 独立单点重跑

### 024_reruns_impl-026_stg_twitter_ads__line_item_history.json
[024_reruns_impl-026_stg_twitter_ads__line_item_history.json](../024_reruns_impl-026_stg_twitter_ads__line_item_history.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2499|8601|否|
|L1|2500|2500|2240|2240|否|
|L2|2500|2500|2240|2240|否|
|L3|2500|2500|2240|2240|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"bid_amount":1375,"bid_amount_local_micro":2499,"total_budget_amount":2240,"total_budget_amount_local_micro":2487}`
- L1：`{"total_budget_amount":2240}`
- L2：`{"total_budget_amount":2240}`
- L3：`{"total_budget_amount":2240}`

#### baseline
私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_history/baseline.sql`；SHA-256 `e7878e8d0c56f1f16eb4b5dd717ef8a4501fd2760c99d9d9cd8d1ab845d3e3c1`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2499|8601|否|
|L1|2500|2500|2240|2240|否|
|L2|2500|2500|2240|2240|否|
|L3|2500|2500|2240|2240|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"bid_amount":1375,"bid_amount_local_micro":2499,"total_budget_amount":2240,"total_budget_amount_local_micro":2487}`
- L1：`{"total_budget_amount":2240}`
- L2：`{"total_budget_amount":2240}`
- L3：`{"total_budget_amount":2240}`

#### bid_amount_local_micro
主因；类别候选O。agent遵守契约类型，gold使用DOUBLE/两位小数。
相对本轮基线：行减少1，格减少2499。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第3行、offset 102起替换；其他字节相同。
原表达式：
```sql
cast(bid_amount_local_micro as bigint) as bid_amount_local_micro
```

修改后：
```sql
bid_amount_local_micro as bid_amount_local_micro
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_history/bid_amount_local_micro.sql`；SHA-256 `bfed9f8996de510dff729bff88cf46c1615af95d5045c94a8a51461c359f9aa6`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2498|6102|否|
|L1|2500|2500|2240|2240|否|
|L2|2500|2500|2240|2240|否|
|L3|2500|2500|2240|2240|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"bid_amount":1375,"total_budget_amount":2240,"total_budget_amount_local_micro":2487}`
- L1：`{"total_budget_amount":2240}`
- L2：`{"total_budget_amount":2240}`
- L3：`{"total_budget_amount":2240}`

#### bid_amount
参与因素；类别候选O。agent遵守契约类型，gold使用DOUBLE/两位小数。
相对本轮基线：行减少0，格减少1375。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第4行、offset 176起替换；其他字节相同。
原表达式：
```sql
cast(round(bid_amount_local_micro / 1000000.0, 2) as decimal(18,2)) as bid_amount
```

修改后：
```sql
round(bid_amount_local_micro / 1000000.0, 2) as bid_amount
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_history/bid_amount.sql`；SHA-256 `d79c370d081127006615b80b588427d8983e5bdb3aad718551d3c7339619bb44`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2499|7226|否|
|L1|2500|2500|2240|2240|否|
|L2|2500|2500|2240|2240|否|
|L3|2500|2500|2240|2240|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"bid_amount_local_micro":2499,"total_budget_amount":2240,"total_budget_amount_local_micro":2487}`
- L1：`{"total_budget_amount":2240}`
- L2：`{"total_budget_amount":2240}`
- L3：`{"total_budget_amount":2240}`

#### total_budget_amount_local_micro
参与因素；类别候选O。agent遵守契约类型，gold使用DOUBLE/两位小数。
相对本轮基线：行减少0，格减少2487。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第14行、offset 934起替换；其他字节相同。
原表达式：
```sql
cast(total_budget_amount_local_micro as bigint) as total_budget_amount_local_micro
```

修改后：
```sql
total_budget_amount_local_micro as total_budget_amount_local_micro
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_history/total_budget_amount_local_micro.sql`；SHA-256 `236f809995b5d7689c6ae99806b11e3fbc618c5567c00ffc9a57355414912517`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2499|6114|否|
|L1|2500|2500|2240|2240|否|
|L2|2500|2500|2240|2240|否|
|L3|2500|2500|2240|2240|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"bid_amount":1375,"bid_amount_local_micro":2499,"total_budget_amount":2240}`
- L1：`{"total_budget_amount":2240}`
- L2：`{"total_budget_amount":2240}`
- L3：`{"total_budget_amount":2240}`

#### total_budget_amount
参与因素；类别候选O。agent遵守契约类型，gold使用DOUBLE/两位小数。
相对本轮基线：行减少0，格减少2240。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第15行、offset 1026起替换；其他字节相同。
原表达式：
```sql
cast(round(total_budget_amount_local_micro / 1000000.0, 1) as decimal(18,1)) as total_budget_amount
```

修改后：
```sql
round(total_budget_amount_local_micro / 1000000.0, 2) as total_budget_amount
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__line_item_history/total_budget_amount.sql`；SHA-256 `ec24c916f46213895042f1ae7955217c221afe83705abdfe203488335176eabf`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2499|6361|否|
|L1|2500|2500|0|0|是|
|L2|2500|2500|0|0|是|
|L3|2500|2500|0|0|是|

首次整表匹配：**L1**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"bid_amount":1375,"bid_amount_local_micro":2499,"total_budget_amount_local_micro":2487}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

