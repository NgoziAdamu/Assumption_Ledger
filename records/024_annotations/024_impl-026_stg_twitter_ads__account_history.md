# impl-026 · stg_twitter_ads__account_history

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**A**；把握：中。

一条带空白timezone，agent直接fallback UTC；gold先trim。契约correct未指定策略。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-026_stg_twitter_ads__account_history.md](../024_packages/024_impl-026_stg_twitter_ads__account_history.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。

```text
24:     - name: stg_twitter_ads__account_history
25:       description: "Cleaned and standardized Twitter Ads account attributes with latest-version flag."
26:       source_table: raw.twitter_account_history_data
27:       columns:
28:         - name: account_id
29:           data_type: VARCHAR
30:           constraints: [not_null]
31:         - name: approval_status
32:           data_type: VARCHAR
33:           validation_rules:
34:             - rule: "approval_status IN ('ACCEPTED','PENDING','REJECTED')"
35:               on_failure: delete_row
36:         - name: business_id
37:           data_type: VARCHAR
38:         - name: business_name
39:           data_type: VARCHAR
40:         - name: created_timestamp
41:           data_type: TIMESTAMP
42:         - name: is_deleted
43:           data_type: BOOLEAN
44:         - name: industry_type
45:           data_type: VARCHAR
46:         - name: name
47:           data_type: VARCHAR
48:         - name: timezone
49:           data_type: VARCHAR
50:           validation_rules:
51:             - rule: "timezone IN ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC')"
52:               on_failure: correct
53:         - name: timezone_switched_timestamp
54:           data_type: TIMESTAMP
55:         - name: updated_timestamp
56:           data_type: TIMESTAMP
57:         - name: is_latest_version
58:           data_type: BOOLEAN
59:           constraints: [not_null]
60:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__account_history.sql`；SHA-256 `0d26db07760a4b7d0e07b7446ddd9850afa958451c942e37bf4d4b820d8246aa`。

```text
1: with cleaned as (
2:     select
3:         id as account_id,
4:         upper(trim(approval_status)) as approval_status,
5:         business_id,
6:         business_name,
7:         try_cast(replace(created_at, ' UTC', '') as timestamp) as created_timestamp,
8:         deleted as is_deleted,
9:         industry_type,
10:         name,
11:         case when timezone in ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC') then timezone else 'UTC' end as timezone,
12:         try_cast(replace(timezone_switch_at, ' UTC', '') as timestamp) as timezone_switched_timestamp,
13:         try_cast(replace(updated_at, ' UTC', '') as timestamp) as updated_timestamp
14:     from raw.twitter_account_history_data
15:     where id is not null
16: ), valid_rows as (
17:     select * from cleaned where approval_status in ('ACCEPTED','PENDING','REJECTED')
18: ), versioned as (
19:     select *, row_number() over (partition by account_id order by updated_timestamp desc nulls last) = 1 as is_latest_version from valid_rows
20: )
21: select * from versioned
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__account_history.sql`；SHA-256 `588dd31898541558b717b3c5cd32df8e9a8cccfd89d5fe3459339b35f23799a4`。

```text
1: with src as (
2:   select
3:     id as account_id,
4:     upper(trim(approval_status)) as approval_status_raw,
5:     business_id,
6:     business_name,
7:     try_cast(created_at as timestamp) as created_timestamp,
8:     coalesce(cast(deleted as boolean), false) as is_deleted,
9:     industry_type,
10:     name,
11:     trim(timezone) as timezone_raw,
12:     try_cast(timezone_switch_at as timestamp) as timezone_switched_timestamp,
13:     try_cast(updated_at as timestamp) as updated_timestamp,
14:     salt
15:   from raw.twitter_account_history_data
16: ), cleaned as (
17:   select
18:     account_id,
19:     case
20:       when approval_status_raw in ('ACCEPTED','PENDING','REJECTED') then approval_status_raw
21:       when approval_status_raw in ('accepted','pending','rejected') then upper(approval_status_raw)
22:       else null
23:     end as approval_status,
24:     business_id,
25:     business_name,
26:     created_timestamp,
27:     is_deleted,
28:     account_id as id_for_version,
29:     industry_type,
30:     name,
31:     case when timezone_raw in ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC') then timezone_raw else 'UTC' end as timezone,
32:     timezone_switched_timestamp,
33:     updated_timestamp
34:   from src
35:   where approval_status_raw is not null
36: ), latest as (
37:   select *, row_number() over(partition by id_for_version order by updated_timestamp desc nulls last) as rn
38:   from cleaned
39: )
40: select
41:   account_id,
42:   approval_status,
43:   business_id,
44:   business_name,
45:   created_timestamp,
46:   is_deleted,
47:   industry_type,
48:   name,
49:   timezone,
50:   timezone_switched_timestamp,
51:   updated_timestamp,
52:   (rn = 1) as is_latest_version
53: from latest
54: where approval_status is not null
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- timezone_trim（A）：**针对本表的具体说明**；事件 35。
原句：

```
The contract requests correction of unsupported timezones without specifying a fallback; invalid timezone values are set to `UTC`.
```

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

核实查询 **3** 条；代价档：**多条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('twitter_account_history_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["twitter_account_history_data","_fivetran_synced","VARCHAR"],["twitter_account_history_data","approval_status","VARCHAR"],["twitter_account_history_data","business_id","VARCHAR"],["twitter_account_history_data","business_name","VARCHAR"],["twitter_account_history_data","created_at","VARCHAR"],["twitter_account_history_data","deleted","BOOLEAN"],["twitter_account_history_data","id","VARCHAR"],["twitter_account_history_data","industry_type","VARCHAR"],["twitter_account_history_data","name","VARCHAR"],["twitter_account_history_data","salt","VARCHAR"],["twitter_account_history_data","timezone","VARCHAR"],["twitter_account_history_data","timezone_switch_at","VARCHAR"],["twitter_account_history_data","updated_at","VARCHAR"]]}
```


### 核实：timezone空白
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE timezone<>trim(timezone)) whitespace FROM raw.twitter_account_history_data
```

查询未完成，错误原文：

```
Parser Error: syntax error at or near "whitespace"

LINE 1: ... count(*) n,count(*) FILTER(WHERE timezone<>trim(timezone)) whitespace FROM raw.twitter_account_history_data
                                                                       ^
```


### 核实：timezone空白重试
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE timezone<>trim(timezone)) whitespace_n FROM raw.twitter_account_history_data
```


```json
{"columns":["n","whitespace_n"],"rows":[[2500,1]]}
```

## 独立单点重跑

### 024_reruns_impl-026_stg_twitter_ads__account_history.json
[024_reruns_impl-026_stg_twitter_ads__account_history.json](../024_reruns_impl-026_stg_twitter_ads__account_history.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2487|2487|1|1|否|
|L1|2487|2487|1|1|否|
|L2|2487|2487|1|1|否|
|L3|2487|2487|1|1|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"timezone":1}`
- L1：`{"timezone":1}`
- L2：`{"timezone":1}`
- L3：`{"timezone":1}`

#### baseline
私有SQL：`data/024_work/impl-026_stg_twitter_ads__account_history/baseline.sql`；SHA-256 `0d26db07760a4b7d0e07b7446ddd9850afa958451c942e37bf4d4b820d8246aa`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2487|2487|1|1|否|
|L1|2487|2487|1|1|否|
|L2|2487|2487|1|1|否|
|L3|2487|2487|1|1|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"timezone":1}`
- L1：`{"timezone":1}`
- L2：`{"timezone":1}`
- L3：`{"timezone":1}`

#### timezone_trim
主因；类别候选A。无效timezone的correct未定义trim还是fallback UTC；合法原值带空白。
相对本轮基线：行减少1，格减少1。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第11行、offset 317起替换；其他字节相同。
原表达式：
```sql
case when timezone in ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC') then timezone else 'UTC' end as timezone
```

修改后：
```sql
case when trim(timezone) in ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC') then trim(timezone) else 'UTC' end as timezone
```

私有SQL：`data/024_work/impl-026_stg_twitter_ads__account_history/timezone_trim.sql`；SHA-256 `9ec078ea9a1421185a2ea75123c3dbc25613ec51fbe8af611707e15aa9deb767`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2487|2487|0|0|是|
|L1|2487|2487|0|0|是|
|L2|2487|2487|0|0|是|
|L3|2487|2487|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

