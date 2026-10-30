# impl-026 · stg_twitter_ads__tweet

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

一条非规范lang按契约不在枚举置NULL，gold先lower/trim得到en。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-026_stg_twitter_ads__tweet.md](../024_packages/024_impl-026_stg_twitter_ads__tweet.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。

```text
429:     - name: stg_twitter_ads__tweet
430:       description: "Cleaned tweets with validated language and reasonable created_at bounds applied at staging filter."
431:       source_table: raw.twitter_tweet_data
432:       columns:
433:         - name: account_id
434:           data_type: VARCHAR
435:         - name: tweet_id
436:           data_type: VARCHAR
437:         - name: name
438:           data_type: VARCHAR
439:         - name: full_text
440:           data_type: VARCHAR
441:         - name: language
442:           data_type: VARCHAR
443:           validation_rules:
444:             - rule: "language IN ('en','es','fr','de','ja','zh','ar','pt','ru','ko')"
445:               on_failure: nullify_field
446:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__tweet.sql`；SHA-256 `7ac5cb59aa5f8fcc220dca10b4b35edd4f88d9ab367e6bd1f973423535c8f424`。

```text
1: select account_id, cast(id as varchar) as tweet_id, name, full_text,
2:     case when lang in ('en','es','fr','de','ja','zh','ar','pt','ru','ko') then lang else null end as language
3: from raw.twitter_tweet_data
4: where try_cast(replace(created_at, ' UTC', '') as timestamp) between timestamp '2006-01-01' and timestamp '2100-01-01'
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__tweet.sql`；SHA-256 `9accb8f66b12068f83418c73fbf2dcbb7663a38db21502348542b0576864a64f`。

```text
1: with src as (
2:   select
3:     account_id,
4:     id as tweet_id,
5:     name,
6:     full_text,
7:     lower(trim(lang)) as lang_raw,
8:     try_cast(created_at as timestamp) as created_at_ts
9:   from raw.twitter_tweet_data
10: ), cleaned as (
11:   select
12:     account_id,
13:     tweet_id,
14:     name,
15:     full_text,
16:     case when lang_raw ~ '^[a-z]{2}$' and lang_raw in ('en','es','fr','de','ja','zh','ar','pt','ru','ko') then lang_raw else null end as language,
17:     created_at_ts
18:   from src
19: )
20: select
21:   account_id,
22:   tweet_id,
23:   name,
24:   full_text,
25:   language
26: from cleaned
27: where created_at_ts is not null and created_at_ts >= timestamp '2010-01-01' and created_at_ts <= current_localtimestamp()
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- language_normalize（O）：**看到了但没提**；事件 9、10、13。
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

核实查询 **2** 条；代价档：**多条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('twitter_tweet_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["twitter_tweet_data","id","BIGINT"],["twitter_tweet_data","_fivetran_synced","VARCHAR"],["twitter_tweet_data","account_id","VARCHAR"],["twitter_tweet_data","card_uri","DOUBLE"],["twitter_tweet_data","coordinates_coordinates","DOUBLE"],["twitter_tweet_data","coordinates_type","DOUBLE"],["twitter_tweet_data","created_at","VARCHAR"],["twitter_tweet_data","favorite_count","BIGINT"],["twitter_tweet_data","favorited","BOOLEAN"],["twitter_tweet_data","followers","DOUBLE"],["twitter_tweet_data","full_text","VARCHAR"],["twitter_tweet_data","geo_coordinates","DOUBLE"],["twitter_tweet_data","geo_type","DOUBLE"],["twitter_tweet_data","in_reply_to_screen_name","DOUBLE"],["twitter_tweet_data","in_reply_to_status_id","DOUBLE"],["twitter_tweet_data","in_reply_to_user_id","DOUBLE"],["twitter_tweet_data","lang","VARCHAR"],["twitter_tweet_data","media_key","DOUBLE"],["twitter_tweet_data","retweet_count","BIGINT"],["twitter_tweet_data","retweeted","BOOLEAN"],["twitter_tweet_data","source","VARCHAR"],["twitter_tweet_data","truncated","BOOLEAN"],["twitter_tweet_data","tweet_type","VARCHAR"],["twitter_tweet_data","user_id","BIGINT"],["twitter_tweet_data","name","VARCHAR"]]}
```


### 核实：language原值与规范值
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。

```sql
SELECT lang,count(*) n FROM raw.twitter_tweet_data WHERE lang<>lower(trim(lang)) GROUP BY lang
```


```json
{"columns":["lang","n"],"rows":[["En",2],["en_GB",2],["en_US",1]]}
```

## 独立单点重跑

### 024_reruns_impl-026_stg_twitter_ads__tweet.json
[024_reruns_impl-026_stg_twitter_ads__tweet.json](../024_reruns_impl-026_stg_twitter_ads__tweet.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2489|2489|1|1|否|
|L1|2489|2489|1|1|否|
|L2|2489|2489|1|1|否|
|L3|2489|2489|1|1|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"language":1}`
- L1：`{"language":1}`
- L2：`{"language":1}`
- L3：`{"language":1}`

#### baseline
私有SQL：`data/024_work/impl-026_stg_twitter_ads__tweet/baseline.sql`；SHA-256 `7ac5cb59aa5f8fcc220dca10b4b35edd4f88d9ab367e6bd1f973423535c8f424`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2489|2489|1|1|否|
|L1|2489|2489|1|1|否|
|L2|2489|2489|1|1|否|
|L3|2489|2489|1|1|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"language":1}`
- L1：`{"language":1}`
- L2：`{"language":1}`
- L3：`{"language":1}`

#### language_normalize
主因；类别候选O。契约规定不在枚举则null，gold先lower/trim接受本应不合枚举的原值。
相对本轮基线：行减少1，格减少1。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第2行、offset 73起替换；其他字节相同。
原表达式：
```sql
case when lang in ('en','es','fr','de','ja','zh','ar','pt','ru','ko') then lang else null end as language
```

修改后：
```sql
case when lower(trim(lang)) in ('en','es','fr','de','ja','zh','ar','pt','ru','ko') then lower(trim(lang)) else null end as language
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__tweet/language_normalize.sql`；SHA-256 `745b67dd7356f04da8d1dbf794576973f5fbdefd68f1615bc4f8df9cd0a41b26`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2489|2489|0|0|是|
|L1|2489|2489|0|0|是|
|L2|2489|2489|0|0|是|
|L3|2489|2489|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

枚举失败nullify的原式执行支持O；若把标准化视为隐含可读A。本次不新增隐含标准化，选择O。

