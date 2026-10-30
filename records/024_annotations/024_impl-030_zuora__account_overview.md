# impl-030 · zuora__account_overview

用途：**全量**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**C**；把握：高。

items_by_account使用INNER JOIN，遗漏有invoice但无item的账户0计数；契约明确应0，454行单改L0全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-030_zuora__account_overview.md](../024_packages/024_impl-030_zuora__account_overview.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
3152:     - name: zuora__account_overview
3153:       description: Account-level overview combining current account fields, current contact fields, invoice aggregates, and invoice item counts
3154:       grain: One row per account_id present in int_zuora__account_current
3155:       source_models:
3156:       - intermediate.int_zuora__account_current
3157:       - intermediate.int_zuora__contact_current
3158:       - intermediate.int_zuora__invoice_base
3159:       - intermediate.int_zuora__invoice_item_base
3160:       - intermediate.int_zuora__billing_enriched
3161:       business_logic: '- Base: Start from intermediate.int_zuora__account_current (assumed one current row per account_id). - Contact: Left join intermediate.int_zuora__contact_current on account_id; if no contact row, all contact fields are NULL. - Invoice item count: - Build items_by_account by joining intermediate.int_zuora__invoice_base to intermediate.int_zuora__invoice_item_base on invoice_id, then counting distinct invoice_item_id per account_id. - Left join items_by_account to accounts. The count reflects distinct item IDs across all invoices of the account. If an account has invoices but none have items, the count is 0. If an account has no invoices, there is no items_by_account row and the joined count is NULL. - Invoice aggregates: - Build per_invoice by left joining intermediate.int_zuora__billing_enriched to intermediate.int_zuora__invoice_base on invoice_id, then grouping by account_id to compute: - first_charge_date: earliest non-NULL first_charge_date across the account’s invoices. - total_amount_paid: sum of invoice_amount_paid. - total_amount_not_paid: sum of invoice_amount_unpaid. - total_taxes: sum of tax_amount. - total_invoice_amount: sum of invoice_amount. - Summations skip NULL inputs per row; if an account has invoices but all values for a summed field are NULL, the result is NULL. If an account has no invoices, no per_invoice row exists and all joined aggregates are NULL. - Invoice count: - Compute per account_id using a correlated subquery over intermediate.int_zuora__invoice_base that counts distinct invoices; returns 0 when no invoices exist. - Output: - Select pass-through account fields, joined contact fields, per_invoice.first_charge_date as first_charge_processed_at, items_by_account.invoice_item_count, the scalar invoice_count, and the per_invoice totals. No zero-coalescing, rounding, or casting; all joins from accounts are left joins.'
3162:       columns:
3163:       - name: account_id
3164:         data_type: VARCHAR
3165:         description: Account identifier from int_zuora__account_current; exactly one output row per account_id
3166:         tests:
3167:         - not_null
3168:         - unique
3169:       - name: account_created_at
3170:         data_type: TIMESTAMP
3171:         description: Account created_date from int_zuora__account_current
3172:       - name: account_name
3173:         data_type: VARCHAR
3174:         description: Account name from int_zuora__account_current
3175:       - name: account_number
3176:         data_type: VARCHAR
3177:         description: Account number from int_zuora__account_current
3178:       - name: account_credit_balance
3179:         data_type: VARCHAR
3180:         description: Raw credit_balance from int_zuora__account_current (string as stored; no casting)
3181:       - name: account_zuora_calculated_mrr
3182:         data_type: VARCHAR
3183:         description: Raw mrr from int_zuora__account_current (Zuora-calculated MRR; string as stored)
3184:       - name: account_status
3185:         data_type: VARCHAR
3186:         description: Account status from int_zuora__account_current
3187:       - name: is_auto_pay
3188:         data_type: VARCHAR
3189:         description: Raw auto_pay flag from int_zuora__account_current (string as stored)
3190:       - name: account_country
3191:         data_type: VARCHAR
3192:         description: Country from int_zuora__contact_current.country (NULL if no contact)
3193:       - name: account_city
3194:         data_type: VARCHAR
3195:         description: City from int_zuora__contact_current.city (NULL if no contact)
3196:       - name: account_email
3197:         data_type: VARCHAR
3198:         description: Work email from int_zuora__contact_current.work_email (NULL if no contact)
3199:       - name: account_first_name
3200:         data_type: VARCHAR
3201:         description: First name from int_zuora__contact_current.first_name (NULL if no contact)
3202:       - name: account_last_name
3203:         data_type: VARCHAR
3204:         description: Last name from int_zuora__contact_current.last_name (NULL if no contact)
3205:       - name: account_postal_code
3206:         data_type: VARCHAR
3207:         description: Postal code from int_zuora__contact_current.postal_code (NULL if no contact)
3208:       - name: account_state
3209:         data_type: VARCHAR
3210:         description: State from int_zuora__contact_current.state (NULL if no contact)
3211:       - name: first_charge_processed_at
3212:         data_type: TIMESTAMP
3213:         description: Earliest non-NULL first_charge_date from billing_enriched across all invoices for the account; NULL if no invoices or all values NULL
3214:       - name: invoice_item_count
3215:         data_type: BIGINT
3216:         description: Distinct count of invoice_item_id across all invoices for the account; 0 if invoices exist but no items; NULL if the account has no invoices
3217:       - name: invoice_count
3218:         data_type: BIGINT
3219:         description: Distinct count of invoices for the account; returns 0 when no invoices exist
3220:       - name: total_taxes
3221:         data_type: DOUBLE
3222:         description: Sum of tax_amount across all invoices for the account; NULL if no invoices or if all values are NULL
3223:       - name: total_invoice_amount
3224:         data_type: DOUBLE
3225:         description: Sum of invoice_amount across all invoices for the account; NULL if no invoices or if all values are NULL
3226:       - name: total_amount_paid
3227:         data_type: DOUBLE
3228:         description: Sum of invoice_amount_paid across all invoices for the account; NULL if no invoices or if all values are NULL
3229:       - name: total_amount_not_paid
3230:         data_type: DOUBLE
3231:         description: Sum of invoice_amount_unpaid across all invoices for the account; NULL if no invoices or if all values are NULL
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/marts/zuora__account_overview.sql`；SHA-256 `1b25cc4ed2440a2216bd59f2cb0c54dc3bb756994096cbcc54836f6aca34a043`。

```text
1: WITH items_by_account AS (
2:     SELECT inv.account_id, count(DISTINCT ii.invoice_item_id) AS invoice_item_count
3:     FROM intermediate.int_zuora__invoice_base AS inv
4:     JOIN intermediate.int_zuora__invoice_item_base AS ii ON inv.invoice_id = ii.invoice_id
5:     GROUP BY inv.account_id
6: ),
7: per_invoice AS (
8:     SELECT inv.account_id,
9:            min(be.first_charge_date) AS first_charge_processed_at,
10:            sum(inv.invoice_amount_paid) AS total_amount_paid,
11:            sum(inv.invoice_amount_unpaid) AS total_amount_not_paid,
12:            sum(inv.tax_amount) AS total_taxes,
13:            sum(inv.invoice_amount) AS total_invoice_amount
14:     FROM intermediate.int_zuora__invoice_base AS inv
15:     LEFT JOIN intermediate.int_zuora__billing_enriched AS be ON inv.invoice_id = be.invoice_id
16:     GROUP BY inv.account_id
17: )
18: SELECT a.account_id,
19:        a.created_date AS account_created_at,
20:        a.name AS account_name,
21:        a.account_number,
22:        CAST(a.credit_balance AS VARCHAR) AS account_credit_balance,
23:        CAST(a.mrr AS VARCHAR) AS account_zuora_calculated_mrr,
24:        a.status AS account_status,
25:        CAST(a.auto_pay AS VARCHAR) AS is_auto_pay,
26:        c.country AS account_country,
27:        c.city AS account_city,
28:        c.work_email AS account_email,
29:        c.first_name AS account_first_name,
30:        c.last_name AS account_last_name,
31:        c.postal_code AS account_postal_code,
32:        c.state AS account_state,
33:        pi.first_charge_processed_at,
34:        iba.invoice_item_count,
35:        (SELECT count(DISTINCT i.invoice_id)
36:         FROM intermediate.int_zuora__invoice_base AS i
37:         WHERE i.account_id = a.account_id) AS invoice_count,
38:        pi.total_taxes,
39:        pi.total_invoice_amount,
40:        pi.total_amount_paid,
41:        pi.total_amount_not_paid
42: FROM intermediate.int_zuora__account_current AS a
43: LEFT JOIN intermediate.int_zuora__contact_current AS c ON a.account_id = c.account_id
44: LEFT JOIN items_by_account AS iba ON a.account_id = iba.account_id
45: LEFT JOIN per_invoice AS pi ON a.account_id = pi.account_id
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/marts/zuora__account_overview.sql`；SHA-256 `bab49951252a846c55edcd8ee12da449f28435afae9461d4659394bd03c7cdfd`。

```text
1: with account as (
2:     select * from intermediate.int_zuora__account_current
3: ),
4: contact as (
5:     select * from intermediate.int_zuora__contact_current
6: ),
7: inv as (
8:     select * from intermediate.int_zuora__invoice_base
9: ),
10: items_by_account as (
11:     select i.account_id, count(distinct iib.invoice_item_id) as invoice_item_count
12:     from inv i
13:     left join intermediate.int_zuora__invoice_item_base iib on i.invoice_id = iib.invoice_id
14:     group by i.account_id
15: ),
16: per_invoice as (
17:     select inv.account_id,
18:            min(ii.first_charge_date) as first_charge_date,
19:            max(ii.most_recent_charge_date) as most_recent_charge_date,
20:            sum(inv.invoice_amount_paid) as total_amount_paid,
21:            sum(inv.invoice_amount_unpaid) as total_amount_not_paid,
22:            sum(inv.tax_amount) as total_taxes,
23:            sum(inv.invoice_amount) as total_invoice_amount
24:     from inv
25:     left join intermediate.int_zuora__billing_enriched ii on inv.invoice_id = ii.invoice_id
26:     group by inv.account_id
27: )
28: select
29:     a.account_id as account_id,
30:     a.created_date as account_created_at,
31:     a.name as account_name,
32:     a.account_number,
33:     a.credit_balance as account_credit_balance,
34:     a.mrr as account_zuora_calculated_mrr,
35:     a.status as account_status,
36:     a.auto_pay as is_auto_pay,
37:     c.country as account_country,
38:     c.city as account_city,
39:     c.work_email as account_email,
40:     c.first_name as account_first_name,
41:     c.last_name as account_last_name,
42:     c.postal_code as account_postal_code,
43:     c.state as account_state,
44:     per_invoice.first_charge_date as first_charge_processed_at,
45:     items_by_account.invoice_item_count,
46:     (select count(distinct i2.invoice_id) from inv i2 where i2.account_id = a.account_id) as invoice_count,
47:     per_invoice.total_taxes,
48:     per_invoice.total_invoice_amount,
49:     per_invoice.total_amount_paid,
50:     per_invoice.total_amount_not_paid
51: from account a
52: left join contact c on a.account_id = c.account_id
53: left join per_invoice on a.account_id = per_invoice.account_id
54: left join items_by_account on items_by_account.account_id = a.account_id
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- invoice_items_left（C）：**看到了但没提**；事件 47、59、60。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 47：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/47.json`；命令首行：`cat > sql/marts/zuora__account_overview.sql <<'SQL'`。
event 59：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/59.json`；命令首行：`sed -i 's/ip.payment_method_id AS invoice_payment_method_id,/-- invoice payment method is not projected; method is taken from the matched payment\n           /' sql/marts/zuora__line_item_enhanced.sql`。
event 60：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/60.json`；原始观察输出。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

已基于 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 Zuora SQL pipeline，按 staging → intermediate → marts 顺序写入 `sql/`，共 42 个 SQL 文件（18 staging、17 intermediate、7 marts）。SQL 使用 DuckDB 语法和直接的 `schema.table` 上游引用，不含 dbt `ref()`，文件末尾均无分号。

**验证结果**
- `python3 run.py` 成功，构建 `zuora.duckdb`；三个层级所有模型均成功执行。
- 数据质量抽查：staging account 的状态均在 Active/Draft/Cancelled 内，account_id 无重复；invoice_base 的 invoice_id 无重复；line_item_history 的 invoice_item_id 无 NULL。
- 生成 SQL 文件未以分号结束。

**契约说明**
- Staging 采用安全类型转换、删除标记过滤、更新时间驱动的最新记录标记；账户状态按契约规范化/过滤，invoice 创建日期按契约限制时间范围。
- Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。
- 合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
- 最新记录出现并列时按源更新时间标记，不额外去重；上游重复最新记录可能导致下游一对多连接放大，符合模型保留重复记录的合同语义。

开发期间修复了标识字段映射和 processing_type 比较问题；最终运行无失败 SQL。
```

## 查询

核实查询 **1** 条；代价档：**一条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：agent可见有invoice无item的账户
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT count(DISTINCT inv.account_id) accounts FROM intermediate.int_zuora__invoice_base inv LEFT JOIN intermediate.int_zuora__invoice_item_base ii ON inv.invoice_id=ii.invoice_id WHERE ii.invoice_item_id IS NULL
```


```json
{"columns":["accounts"],"rows":[[1041]]}
```

## 独立单点重跑

### 024_reruns_impl-030_zuora__account_overview.json
[024_reruns_impl-030_zuora__account_overview.json](../024_reruns_impl-030_zuora__account_overview.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3791|3791|454|454|否|
|L1|3791|3791|454|454|否|
|L2|3791|3791|454|454|否|
|L3|3791|3791|454|454|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_item_count":454}`
- L1：`{"invoice_item_count":454}`
- L2：`{"invoice_item_count":454}`
- L3：`{"invoice_item_count":454}`

#### baseline
私有SQL：`data/024_work/impl-030_zuora__account_overview/baseline.sql`；SHA-256 `1b25cc4ed2440a2216bd59f2cb0c54dc3bb756994096cbcc54836f6aca34a043`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3791|3791|454|454|否|
|L1|3791|3791|454|454|否|
|L2|3791|3791|454|454|否|
|L3|3791|3791|454|454|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_item_count":454}`
- L1：`{"invoice_item_count":454}`
- L2：`{"invoice_item_count":454}`
- L3：`{"invoice_item_count":454}`

#### invoice_items_left
主因；类别候选C。契约明确有invoice但无item时计数0；INNER JOIN删掉该账户分组。
相对本轮基线：行减少454，格减少454。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第4行、offset 168起替换；其他字节相同。
原表达式：
```sql
JOIN intermediate.int_zuora__invoice_item_base AS ii
```

修改后：
```sql
LEFT JOIN intermediate.int_zuora__invoice_item_base AS ii
```

私有SQL：`data/024_work/impl-030_zuora__account_overview/invoice_items_left.sql`；SHA-256 `fd12f1c1f4dc97d5dba3ebf19cfeaae7037cd913620209efd9fdc1682032309c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3791|3791|0|0|是|
|L1|3791|3791|0|0|是|
|L2|3791|3791|0|0|是|
|L3|3791|3791|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

