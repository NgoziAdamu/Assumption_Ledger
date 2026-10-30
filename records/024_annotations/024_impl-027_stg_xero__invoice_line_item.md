# impl-027 · stg_xero__invoice_line_item

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

五个数值表达式按契约DECIMAL(18,2)输出，gold保留DOUBLE；quantity单改减少最多行，其余四处各有较小贡献。

参与因素：O：discount_rate（行减3，格减424）；O：line_amount（行减2，格减834）；O：tax_amount（行减4，格减1611）；O：unit_amount（行减1，格减814）。
标记：无。

## 材料与比较口径

[024_impl-027_stg_xero__invoice_line_item.md](../024_packages/024_impl-027_stg_xero__invoice_line_item.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`。

```text
128:     - name: stg_xero__invoice_line_item
129:       description: "Invoice line items with validated pricing amounts aligned to current SQL behavior."
130:       source_table: raw.xero_invoice_line_item_data
131:       columns:
132:         - name: line_item_id
133:           data_type: VARCHAR
134:           constraints: [not_null]
135:           validation_rules:
136:             - rule: "line_item_id is present"
137:               on_failure: delete_row
138:         - name: invoice_id
139:           data_type: VARCHAR
140:           constraints: [not_null]
141:           validation_rules:
142:             - rule: "invoice_id is present"
143:               on_failure: delete_row
144:         - name: account_code
145:           data_type: VARCHAR
146:         - name: description
147:           data_type: VARCHAR
148:         - name: discount_entered_as_percent
149:           data_type: BOOLEAN
150:         - name: discount_rate
151:           data_type: DECIMAL(18,2)
152:         - name: item_code
153:           data_type: VARCHAR
154:         - name: line_amount
155:           data_type: DECIMAL(18,2)
156:         - name: quantity
157:           data_type: DECIMAL(18,2)
158:         - name: tax_amount
159:           data_type: DECIMAL(18,2)
160:         - name: tax_type
161:           data_type: VARCHAR
162:         - name: unit_amount
163:           data_type: DECIMAL(18,2)
164:           validation_rules:
165:             - rule: "If unit_amount is NULL or not a numeric value with up to 2 decimals, delete row"
166:               on_failure: delete_row
167:             - rule: "If unit_amount outside [-1000000, 1000000], delete row"
168:               on_failure: delete_row
169:         - name: processed_at
170:           data_type: TIMESTAMP
171:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/staging/stg_xero__invoice_line_item.sql`；SHA-256 `f813451f19efb9164f413f77aed26c88eff08e3ee58a39131757a90984a23daa`。

```text
1: SELECT
2:     line_item_id::VARCHAR AS line_item_id,
3:     invoice_id::VARCHAR AS invoice_id,
4:     account_code::VARCHAR AS account_code,
5:     description::VARCHAR AS description,
6:     discount_entered_as_percent::BOOLEAN AS discount_entered_as_percent,
7:     TRY_CAST(discount_rate AS DECIMAL(18, 2)) AS discount_rate,
8:     item_code::VARCHAR AS item_code,
9:     TRY_CAST(line_amount AS DECIMAL(18, 2)) AS line_amount,
10:     TRY_CAST(quantity AS DECIMAL(18, 2)) AS quantity,
11:     TRY_CAST(tax_amount AS DECIMAL(18, 2)) AS tax_amount,
12:     tax_type::VARCHAR AS tax_type,
13:     TRY_CAST(unit_amount AS DECIMAL(18, 2)) AS unit_amount,
14:     TRY_CAST(_fivetran_synced AS TIMESTAMP) AS processed_at
15: FROM raw.xero_invoice_line_item_data
16: WHERE NULLIF(trim(line_item_id), '') IS NOT NULL
17:   AND NULLIF(trim(invoice_id), '') IS NOT NULL
18:   AND unit_amount IS NOT NULL
19:   AND unit_amount = round(unit_amount, 2)
20:   AND unit_amount BETWEEN -1000000 AND 1000000
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/staging/stg_xero__invoice_line_item.sql`；SHA-256 `67c4bf8baa8abdb18319c3904590c57db3b0a3f426639341f46eda70b8b4fcb5`。

```text
1: -- Staging table for xero invoice line item data with unit amount cleaning
2: 
3: WITH raw_data AS (
4:     SELECT
5:         _fivetran_synced,
6:         account_code,
7:         description,
8:         discount_entered_as_percent,
9:         discount_rate,
10:         invoice_id,
11:         item_code,
12:         line_amount,
13:         line_item_id,
14:         quantity,
15:         tax_amount,
16:         tax_type,
17:         unit_amount,
18:         validation_errors
19:     FROM raw.xero_invoice_line_item_data
20: ),
21: 
22: cleaned_data AS (
23:     SELECT
24:         -- Remove fivetran metadata
25:         account_code,
26:         description,
27:         discount_entered_as_percent,
28:         discount_rate,
29:         invoice_id,
30:         item_code,
31:         line_amount,
32:         line_item_id,
33:         quantity,
34:         tax_amount,
35:         tax_type,
36: 
37:         -- Apply validation rules for unit_amount (format -> nullify_field; range -> delete_row; completeness -> delete_row)
38:         CASE
39:             -- Nullify if format invalid (allow optional sign and up to 2 decimals)
40:             WHEN unit_amount IS NOT NULL AND NOT (CAST(unit_amount AS VARCHAR) ~ '^-?\d+(\.\d{1,2})?$') THEN NULL
41:             -- Keep as-is when format valid
42:             ELSE unit_amount
43:         END AS unit_amount,
44: 
45:         CURRENT_TIMESTAMP AS processed_at
46: 
47:     FROM raw_data
48:     WHERE line_item_id IS NOT NULL
49:       AND invoice_id IS NOT NULL
50: )
51: 
52: SELECT
53:     account_code,
54:     description,
55:     discount_entered_as_percent,
56:     discount_rate,
57:     invoice_id,
58:     item_code,
59:     line_amount,
60:     line_item_id,
61:     quantity,
62:     tax_amount,
63:     tax_type,
64:     unit_amount,
65:     processed_at
66: FROM cleaned_data
67: WHERE line_item_id IS NOT NULL
68:   AND invoice_id IS NOT NULL
69:   -- completeness: must have unit_amount
70:   AND unit_amount IS NOT NULL
71:   -- range: delete rows out of range
72:   AND unit_amount >= -1000000 AND unit_amount <= 1000000
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- quantity（O）：**看到了但没提**；事件 17、18、19。
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('xero_invoice_line_item_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["xero_invoice_line_item_data","_fivetran_synced","VARCHAR"],["xero_invoice_line_item_data","account_code","BIGINT"],["xero_invoice_line_item_data","description","VARCHAR"],["xero_invoice_line_item_data","discount_entered_as_percent","BOOLEAN"],["xero_invoice_line_item_data","discount_rate","DOUBLE"],["xero_invoice_line_item_data","invoice_id","VARCHAR"],["xero_invoice_line_item_data","item_code","VARCHAR"],["xero_invoice_line_item_data","line_amount","DOUBLE"],["xero_invoice_line_item_data","line_item_id","VARCHAR"],["xero_invoice_line_item_data","quantity","DOUBLE"],["xero_invoice_line_item_data","tax_amount","DOUBLE"],["xero_invoice_line_item_data","tax_type","VARCHAR"],["xero_invoice_line_item_data","unit_amount","DOUBLE"],["xero_invoice_line_item_data","validation_errors","DOUBLE"]]}
```


### 诊断：固定时间
[024_history_clock.json](../024_history_clock.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

```sql
SELECT min(processed_at),max(processed_at) FROM staging.stg_xero__invoice_line_item
```


```json
{"rows":[["2025-10-17 11:30:22.817389+08:00","2025-10-17 11:30:22.817389+08:00"]]}
```

## 独立单点重跑

### 024_reruns_impl-027_stg_xero__invoice_line_item.json
[024_reruns_impl-027_stg_xero__invoice_line_item.json](../024_reruns_impl-027_stg_xero__invoice_line_item.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-17 11:30:22.817389+08:00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-17'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5000|5000|4984|8620|否|
|L1|5000|5000|4320|4320|否|
|L2|5000|5000|7|7|否|
|L3|5000|5000|7|7|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"discount_rate":424,"line_amount":834,"quantity":4937,"tax_amount":1611,"unit_amount":814}`
- L1：`{"quantity":4320}`
- L2：`{"quantity":7}`
- L3：`{"quantity":7}`

#### baseline
私有SQL：`data/024_work/impl-027_stg_xero__invoice_line_item/baseline.sql`；SHA-256 `f813451f19efb9164f413f77aed26c88eff08e3ee58a39131757a90984a23daa`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5000|5000|4984|8620|否|
|L1|5000|5000|4320|4320|否|
|L2|5000|5000|7|7|否|
|L3|5000|5000|7|7|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"discount_rate":424,"line_amount":834,"quantity":4937,"tax_amount":1611,"unit_amount":814}`
- L1：`{"quantity":4320}`
- L2：`{"quantity":7}`
- L3：`{"quantity":7}`

#### discount_rate
参与因素；类别候选O。契约DECIMAL(18,2)；gold保留DOUBLE，字符串精度表示不同。
相对本轮基线：行减少3，格减少424。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第7行、offset 250起替换；其他字节相同。
原表达式：
```sql
TRY_CAST(discount_rate AS DECIMAL(18, 2)) AS discount_rate
```

修改后：
```sql
discount_rate AS discount_rate
```

私有SQL：`data/024_work/impl-027_stg_xero__invoice_line_item/discount_rate.sql`；SHA-256 `31fb2bc3d2e025630cfe9a75d5979fa1302b82a641cb5d8ae172331561c211c0`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5000|5000|4981|8196|否|
|L1|5000|5000|4320|4320|否|
|L2|5000|5000|7|7|否|
|L3|5000|5000|7|7|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"line_amount":834,"quantity":4937,"tax_amount":1611,"unit_amount":814}`
- L1：`{"quantity":4320}`
- L2：`{"quantity":7}`
- L3：`{"quantity":7}`

#### line_amount
参与因素；类别候选O。契约DECIMAL(18,2)；gold保留DOUBLE，字符串精度表示不同。
相对本轮基线：行减少2，格减少834。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第9行、offset 351起替换；其他字节相同。
原表达式：
```sql
TRY_CAST(line_amount AS DECIMAL(18, 2)) AS line_amount
```

修改后：
```sql
line_amount AS line_amount
```

私有SQL：`data/024_work/impl-027_stg_xero__invoice_line_item/line_amount.sql`；SHA-256 `2716bbbe5ac6ea5c610537fa444006fabe445dc675c85f728b9057356687fc4d`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5000|5000|4982|7786|否|
|L1|5000|5000|4320|4320|否|
|L2|5000|5000|7|7|否|
|L3|5000|5000|7|7|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"discount_rate":424,"quantity":4937,"tax_amount":1611,"unit_amount":814}`
- L1：`{"quantity":4320}`
- L2：`{"quantity":7}`
- L3：`{"quantity":7}`

#### quantity
主因；类别候选O。契约DECIMAL(18,2)；gold保留DOUBLE，字符串精度表示不同。
相对本轮基线：行减少2483，格减少4937。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第10行、offset 411起替换；其他字节相同。
原表达式：
```sql
TRY_CAST(quantity AS DECIMAL(18, 2)) AS quantity
```

修改后：
```sql
quantity AS quantity
```

私有SQL：`data/024_work/impl-027_stg_xero__invoice_line_item/quantity.sql`；SHA-256 `c8292cab830dbfecd71526a05132169c48dcb9fe84821d3dd74adb78b55f9057`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5000|5000|2501|3683|否|
|L1|5000|5000|0|0|是|
|L2|5000|5000|0|0|是|
|L3|5000|5000|0|0|是|

首次整表匹配：**L1**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"discount_rate":424,"line_amount":834,"tax_amount":1611,"unit_amount":814}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

#### tax_amount
参与因素；类别候选O。契约DECIMAL(18,2)；gold保留DOUBLE，字符串精度表示不同。
相对本轮基线：行减少4，格减少1611。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 465起替换；其他字节相同。
原表达式：
```sql
TRY_CAST(tax_amount AS DECIMAL(18, 2)) AS tax_amount
```

修改后：
```sql
tax_amount AS tax_amount
```

私有SQL：`data/024_work/impl-027_stg_xero__invoice_line_item/tax_amount.sql`；SHA-256 `d489b1f947edb94757716445c5d659a0c5b2eca126ac7f1c0f9a6792c17cbfd1`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5000|5000|4980|7009|否|
|L1|5000|5000|4320|4320|否|
|L2|5000|5000|7|7|否|
|L3|5000|5000|7|7|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"discount_rate":424,"line_amount":834,"quantity":4937,"unit_amount":814}`
- L1：`{"quantity":4320}`
- L2：`{"quantity":7}`
- L3：`{"quantity":7}`

#### unit_amount
参与因素；类别候选O。契约DECIMAL(18,2)；gold保留DOUBLE，字符串精度表示不同。
相对本轮基线：行减少1，格减少814。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第13行、offset 558起替换；其他字节相同。
原表达式：
```sql
TRY_CAST(unit_amount AS DECIMAL(18, 2)) AS unit_amount
```

修改后：
```sql
unit_amount AS unit_amount
```

私有SQL：`data/024_work/impl-027_stg_xero__invoice_line_item/unit_amount.sql`；SHA-256 `520db020faba41faf6d4fc41bf69753bcb66392dac2a43650c2487965819846b`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5000|5000|4983|7806|否|
|L1|5000|5000|4320|4320|否|
|L2|5000|5000|7|7|否|
|L3|5000|5000|7|7|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"discount_rate":424,"line_amount":834,"quantity":4937,"tax_amount":1611}`
- L1：`{"quantity":4320}`
- L2：`{"quantity":7}`
- L3：`{"quantity":7}`
## 规则问题

无。

