# impl-027 · stg_xero__journal

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

两个时间字段依契约转TIMESTAMP，gold保留原文本；另INVALID/BAD前缀数字契约允许清洗，gold置NULL。

参与因素：O：invalid_prefix（行减0，格减2）。
标记：无。

## 材料与比较口径

[024_impl-027_stg_xero__journal.md](../024_packages/024_impl-027_stg_xero__journal.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`。

```text
192:     - name: stg_xero__journal
193:       description: "Journal header with sanitized journal number."
194:       source_table: raw.xero_journal_data
195:       columns:
196:         - name: journal_id
197:           data_type: VARCHAR
198:           constraints: [not_null]
199:           validation_rules:
200:             - rule: "journal_id is present"
201:               on_failure: delete_row
202:         - name: created_date_utc
203:           data_type: TIMESTAMP
204:         - name: journal_date
205:           data_type: TIMESTAMP
206:         - name: journal_number
207:           data_type: INT
208:           validation_rules:
209:             - rule: "Remove alphabetic and special characters; if result empty or > 9,999,999, set to NULL"
210:               on_failure: nullify_field
211:         - name: reference
212:           data_type: VARCHAR
213:         - name: source_id
214:           data_type: VARCHAR
215:         - name: source_type
216:           data_type: VARCHAR
217:         - name: processed_at
218:           data_type: TIMESTAMP
219:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/staging/stg_xero__journal.sql`；SHA-256 `de26d5a5354e13ff665d419d27c2bd7fb8d6ddca9c78eeb939cd2c385ea38a52`。

```text
1: SELECT
2:     journal_id::VARCHAR AS journal_id,
3:     TRY_CAST(created_date_utc AS TIMESTAMP) AS created_date_utc,
4:     TRY_CAST(journal_date AS TIMESTAMP) AS journal_date,
5:     CASE
6:         WHEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS BIGINT) <= 9999999
7:             THEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS INTEGER)
8:         ELSE NULL
9:     END AS journal_number,
10:     reference::VARCHAR AS reference,
11:     source_id::VARCHAR AS source_id,
12:     source_type::VARCHAR AS source_type,
13:     NULL::TIMESTAMP AS processed_at
14: FROM raw.xero_journal_data
15: WHERE NULLIF(trim(journal_id), '') IS NOT NULL
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/staging/stg_xero__journal.sql`；SHA-256 `6a12bdeaa52622534cb3c49dfcf5684c30fbfabf986b3fede7f9ed906ee380bb`。

```text
1: -- Staging table for xero journal data with validation rules applied
2: 
3: WITH raw_data AS (
4:     SELECT
5:         journal_id,
6:         created_date_utc,
7:         journal_date,
8:         journal_number,
9:         reference,
10:         source_id,
11:         source_type
12:     FROM raw.xero_journal_data
13: ),
14: 
15: cleaned_data AS (
16:     SELECT
17:         journal_id,
18:         created_date_utc,
19:         journal_date,
20: 
21:         -- Apply validation rules for journal_number
22:         CASE
23:             -- Check if journal_number contains alphabetic characters or special chars
24:             WHEN journal_number ~ '[A-Za-z]' OR journal_number ~ '[!@#$%^&*()]'
25:             THEN REGEXP_REPLACE(journal_number, '[A-Za-z!@#$%^&*()]', '', 'g')
26:             -- Check if journal_number is NULL, empty, or invalid
27:             WHEN journal_number IS NULL OR TRIM(journal_number) = '' OR journal_number LIKE 'INVALID%'
28:                  OR journal_number LIKE 'BAD%'
29:             THEN NULL
30:             -- Try to extract only numeric part if mixed content
31:             WHEN journal_number ~ '\d+'
32:             THEN REGEXP_REPLACE(journal_number, '[^0-9]', '', 'g')
33:             -- Range check: ensure reasonable journal number range
34:             WHEN REGEXP_REPLACE(COALESCE(journal_number, ''), '[^0-9]', '', 'g')::INT > 9999999
35:             THEN NULL
36:             ELSE REGEXP_REPLACE(COALESCE(journal_number, ''), '[^0-9]', '', 'g')
37:         END AS journal_number,
38: 
39:         reference,
40:         source_id,
41:         source_type,
42:         CURRENT_TIMESTAMP AS processed_at
43: 
44:     FROM raw_data
45: )
46: 
47: SELECT
48:     journal_id,
49:     created_date_utc,
50:     journal_date,
51:     journal_number::INT AS journal_number,
52:     reference,
53:     source_id,
54:     source_type,
55:     processed_at
56: FROM cleaned_data
57: WHERE journal_id IS NOT NULL
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- created_date_type（O）：**看到了但没提**；事件 17、18、19。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。

- journal_date_type（O）：**看到了但没提**；事件 17、18、19。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/17.json`；命令首行：`sed -n '1,220p' test_single_sql.py && python - <<'PY'`。
event 18：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/18.json`；原始观察输出。
event 19：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/19.json`；命令首行：`mkdir -p sql/staging sql/intermediate sql/marts && cat > /tmp/gen.py <<'PY'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

Implemented the Xero SQL pipeline in `sql/`, following the staging → intermediate → marts order and the provided data contract.

- Created 14 staging models, 5 intermediate models, and 4 marts models with DuckDB SQL, fully qualified upstream references, and no trailing semicolons.
- Applied contract-driven field cleaning, casting, and row filters; active-option matching and tracking pivots; invoice and general-ledger enrichment; and financial reporting calculations.
- Avoided duplicate account-code join expansion by selecting one account row per code. Duplicate source relationships remain preserved in the relationship model as contracted; pivots collapse repeated assignments and select the lexicographically greatest valid option.
- Validation results: invoice-line enriched and mart models each have 5,000 rows and 5,000 unique line-item IDs; the general ledger has 8,000 unique journal/journal-line combinations; staged invoices have 3,489 valid dates and no dates beyond the allowed horizon; no staged invoice unit amounts violate the defined range; and two of 22 tracking categories normalize to `UNKNOWN`.

Validation: `python run.py` completed successfully with all 14 staging, 5 intermediate, and 4 marts models created. Sanity checks verified unique IDs/keys and nonnegative invoice-level aggregates. No SQL execution failures remained.

Contract assumptions: Raw data does not provide a processing timestamp for some entities, so `processed_at` is NULL where unavailable. Available source timestamp strings are parsed with DuckDB `TRY_CAST`; invalid timestamps become NULL. General-ledger fact and report timestamps use `current_timestamp`. Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.
```

## 查询

核实查询 **1** 条；代价档：**一条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('xero_journal_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["xero_journal_data","journal_id","VARCHAR"],["xero_journal_data","created_date_utc","VARCHAR"],["xero_journal_data","journal_date","VARCHAR"],["xero_journal_data","journal_number","VARCHAR"],["xero_journal_data","reference","VARCHAR"],["xero_journal_data","source_id","VARCHAR"],["xero_journal_data","source_type","VARCHAR"]]}
```


### 诊断：agent实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_xero__journal'
```


```json
{"columns":["column_name","data_type"],"rows":[["journal_id","VARCHAR"],["created_date_utc","TIMESTAMP"],["journal_date","TIMESTAMP"],["journal_number","INTEGER"],["reference","VARCHAR"],["source_id","VARCHAR"],["source_type","VARCHAR"],["processed_at","TIMESTAMP"]]}
```


### 诊断：agent有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb`。

```sql
SELECT created_date_utc,journal_date,journal_number FROM staging.stg_xero__journal LIMIT 3
```


```json
{"columns":["created_date_utc","journal_date","journal_number"],"rows":[["2020-02-10 18:42:07.587000","2019-11-01 00:00:00",1],["2019-12-03 20:41:42.010000","2019-11-01 00:00:00",2020],["2019-12-03 20:41:41.963000","2019-11-01 00:00:00",null]]}
```


### 诊断：gold实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_xero__journal'
```


```json
{"columns":["column_name","data_type"],"rows":[["journal_id","VARCHAR"],["created_date_utc","VARCHAR"],["journal_date","VARCHAR"],["journal_number","INTEGER"],["reference","VARCHAR"],["source_id","VARCHAR"],["source_type","VARCHAR"],["processed_at","TIMESTAMP WITH TIME ZONE"]]}
```


### 诊断：gold有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

```sql
SELECT created_date_utc,journal_date,journal_number FROM staging.stg_xero__journal LIMIT 3
```


```json
{"columns":["created_date_utc","journal_date","journal_number"],"rows":[["2020-02-10 18:42:07.587 UTC","2019-11-01",null],["2019-12-03 20:41:42.010 UTC","2019-11-01",null],["2019-12-03 20:41:41.963 UTC","2019-11-01",null]]}
```


### 诊断：gold SQL同gold输入重跑
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

```sql
-- Staging table for xero journal data with validation rules applied

WITH raw_data AS (
    SELECT
        journal_id,
        created_date_utc,
        journal_date,
        journal_number,
        reference,
        source_id,
        source_type
    FROM raw.xero_journal_data
),

cleaned_data AS (
    SELECT
        journal_id,
        created_date_utc,
        journal_date,

        -- Apply validation rules for journal_number
        CASE
            -- Check if journal_number contains alphabetic characters or special chars
            WHEN journal_number ~ '[A-Za-z]' OR journal_number ~ '[!@#$%^&*()]'
            THEN REGEXP_REPLACE(journal_number, '[A-Za-z!@#$%^&*()]', '', 'g')
            -- Check if journal_number is NULL, empty, or invalid
            WHEN journal_number IS NULL OR TRIM(journal_number) = '' OR journal_number LIKE 'INVALID%'
                 OR journal_number LIKE 'BAD%'
            THEN NULL
            -- Try to extract only numeric part if mixed content
            WHEN journal_number ~ '\d+'
            THEN REGEXP_REPLACE(journal_number, '[^0-9]', '', 'g')
            -- Range check: ensure reasonable journal number range
            WHEN REGEXP_REPLACE(COALESCE(journal_number, ''), '[^0-9]', '', 'g')::INT > 9999999
            THEN NULL
            ELSE REGEXP_REPLACE(COALESCE(journal_number, ''), '[^0-9]', '', 'g')
        END AS journal_number,

        reference,
        source_id,
        source_type,
        TIMESTAMPTZ '2025-10-17 11:30:22.865253+08:00' AS processed_at

    FROM raw_data
)

SELECT
    journal_id,
    created_date_utc,
    journal_date,
    journal_number::INT AS journal_number,
    reference,
    source_id,
    source_type,
    processed_at
FROM cleaned_data
WHERE journal_id IS NOT NULL
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3500|3500|0|0|是|
|L1|3500|3500|0|0|是|
|L2|3500|3500|0|0|是|
|L3|3500|3500|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

### 诊断：固定时间
[024_history_clock.json](../024_history_clock.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

```sql
SELECT min(processed_at),max(processed_at) FROM staging.stg_xero__journal
```


```json
{"rows":[["2025-10-17 11:30:22.865253+08:00","2025-10-17 11:30:22.865253+08:00"]]}
```

## 独立单点重跑

### 024_reruns_impl-027_stg_xero__journal.json
[024_reruns_impl-027_stg_xero__journal.json](../024_reruns_impl-027_stg_xero__journal.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-17 11:30:22.865253+08:00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-17'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3500|3500|3500|7002|否|
|L1|3500|3500|3500|7002|否|
|L2|3500|3500|3500|7002|否|
|L3|3500|3500|3500|3502|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L1：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L2：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L3：`{"created_date_utc":3500,"journal_number":2}`

#### baseline
私有SQL：`data/024_work/impl-027_stg_xero__journal/baseline.sql`；SHA-256 `de26d5a5354e13ff665d419d27c2bd7fb8d6ddca9c78eeb939cd2c385ea38a52`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3500|3500|3500|7002|否|
|L1|3500|3500|3500|7002|否|
|L2|3500|3500|3500|7002|否|
|L3|3500|3500|3500|3502|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L1：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L2：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L3：`{"created_date_utc":3500,"journal_number":2}`

#### processed_at
不计参与因素；类别候选A。raw无processed_at，契约只声明TIMESTAMP；NULL或执行时间未规定。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第13行、offset 575起替换；其他字节相同。
原表达式：
```sql
NULL::TIMESTAMP AS processed_at
```

修改后：
```sql
TIMESTAMPTZ '2025-10-17 11:30:22.865253+08:00' AS processed_at
```

私有SQL：`data/024_work/impl-027_stg_xero__journal/processed_at.sql`；SHA-256 `9d1b633cc57fe2784b61afab1826eef52dea375841f3d6f0da9f7c3880df4182`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3500|3500|3500|7002|否|
|L1|3500|3500|3500|7002|否|
|L2|3500|3500|3500|7002|否|
|L3|3500|3500|3500|3502|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L1：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L2：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L3：`{"created_date_utc":3500,"journal_number":2}`

#### created_date_type
主因；类别候选O。契约TIMESTAMP，gold原样VARCHAR。
相对本轮基线：行减少0，格减少3500。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第3行、offset 50起替换；其他字节相同。
原表达式：
```sql
TRY_CAST(created_date_utc AS TIMESTAMP) AS created_date_utc
```

修改后：
```sql
created_date_utc AS created_date_utc
```

私有SQL：`data/024_work/impl-027_stg_xero__journal/created_date_type.sql`；SHA-256 `18fc25c23c77441a4e8dac3a3fbfce5f765e30c7395448e2b20a4ef22d0b8626`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3500|3500|3500|3502|否|
|L1|3500|3500|3500|3502|否|
|L2|3500|3500|3500|3502|否|
|L3|3500|3500|2|2|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"journal_date":3500,"journal_number":2}`
- L1：`{"journal_date":3500,"journal_number":2}`
- L2：`{"journal_date":3500,"journal_number":2}`
- L3：`{"journal_number":2}`

#### journal_date_type
主因；类别候选O。契约TIMESTAMP，gold原样VARCHAR。
相对本轮基线：行减少0，格减少3500。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第4行、offset 115起替换；其他字节相同。
原表达式：
```sql
TRY_CAST(journal_date AS TIMESTAMP) AS journal_date
```

修改后：
```sql
journal_date AS journal_date
```

私有SQL：`data/024_work/impl-027_stg_xero__journal/journal_date_type.sql`；SHA-256 `fd24e2d58c3e4066dc0151d46d6177953f2e3cb77a1a2b5093e718bafd108478`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3500|3500|3500|3502|否|
|L1|3500|3500|3500|3502|否|
|L2|3500|3500|3500|3502|否|
|L3|3500|3500|3500|3502|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_date_utc":3500,"journal_number":2}`
- L1：`{"created_date_utc":3500,"journal_number":2}`
- L2：`{"created_date_utc":3500,"journal_number":2}`
- L3：`{"created_date_utc":3500,"journal_number":2}`
### 024_supplement_reruns_impl-027_stg_xero__journal.json
[024_supplement_reruns_impl-027_stg_xero__journal.json](../024_supplement_reruns_impl-027_stg_xero__journal.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-17 11:30:22.865253+08:00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-17'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3500|3500|3500|7002|否|
|L1|3500|3500|3500|7002|否|
|L2|3500|3500|3500|7002|否|
|L3|3500|3500|3500|3502|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L1：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L2：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L3：`{"created_date_utc":3500,"journal_number":2}`

#### baseline
私有SQL：`data/024_supplement_work/impl-027_stg_xero__journal/baseline.sql`；SHA-256 `de26d5a5354e13ff665d419d27c2bd7fb8d6ddca9c78eeb939cd2c385ea38a52`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3500|3500|3500|7002|否|
|L1|3500|3500|3500|7002|否|
|L2|3500|3500|3500|7002|否|
|L3|3500|3500|3500|3502|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L1：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L2：`{"created_date_utc":3500,"journal_date":3500,"journal_number":2}`
- L3：`{"created_date_utc":3500,"journal_number":2}`

#### invalid_prefix
参与因素；类别候选O。契约要求移除字母/特殊字符后保留有效数字，gold额外将INVALID/BAD前缀置NULL。
相对本轮基线：行减少0，格减少2。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第5行、offset 168起替换；其他字节相同。
原表达式：
```sql
    CASE
        WHEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS BIGINT) <= 9999999
            THEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS INTEGER)
        ELSE NULL
    END
```

修改后：
```sql
    CASE WHEN journal_number LIKE 'INVALID%' OR journal_number LIKE 'BAD%' THEN NULL ELSE CASE
        WHEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS BIGINT) <= 9999999
            THEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS INTEGER)
        ELSE NULL
    END END
```

私有SQL：`data/024_supplement_work/impl-027_stg_xero__journal/invalid_prefix.sql`；SHA-256 `36602b84dcb75602d282354ab4726f15af4c9759d013d92a33e9c4f1c54495f6`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3500|3500|3500|7000|否|
|L1|3500|3500|3500|7000|否|
|L2|3500|3500|3500|7000|否|
|L3|3500|3500|3500|3500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_date_utc":3500,"journal_date":3500}`
- L1：`{"created_date_utc":3500,"journal_date":3500}`
- L2：`{"created_date_utc":3500,"journal_date":3500}`
- L3：`{"created_date_utc":3500}`
## 规则问题

无。

