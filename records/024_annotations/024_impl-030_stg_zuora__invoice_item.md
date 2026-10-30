# impl-030 · stg_zuora__invoice_item

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**多因并列（A、O）**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：O：type_balance（行减0，格减1490）；O：type_exchange_rate_date（行减0，格减1490）。
标记：无。

## 材料与比较口径

[024_impl-030_stg_zuora__invoice_item.md](../024_packages/024_impl-030_stg_zuora__invoice_item.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
282:     - name: stg_zuora__invoice_item
283:       description: "Cleaned invoice line items with safe casting of dates and derived service period buckets; latest snapshot indicator provided."
284:       source_table: raw.zuora_invoice_item_data
285:       columns:
286:         - name: invoice_item_id
287:           data_type: VARCHAR
288:           source_expression: "id"
289:         - name: account_id
290:           data_type: VARCHAR
291:         - name: account_receivable_accounting_code_id
292:           data_type: VARCHAR
293:         - name: accounting_code
294:           data_type: VARCHAR
295:         - name: amendment_id
296:           data_type: VARCHAR
297:         - name: applied_to_invoice_item_id
298:           data_type: VARCHAR
299:         - name: balance
300:           data_type: BIGINT
301:         - name: bill_to_contact_id
302:           data_type: VARCHAR
303:         - name: charge_amount
304:           data_type: BIGINT
305:         - name: charge_amount_home_currency
306:           data_type: VARCHAR
307:         - name: charge_date
308:           data_type: TIMESTAMP
309:           source_expression: "try_cast(charge_date as TIMESTAMP)"
310:         - name: charge_name
311:           data_type: VARCHAR
312:         - name: created_by_id
313:           data_type: VARCHAR
314:         - name: created_date
315:           data_type: TIMESTAMP
316:           source_expression: "try_cast(created_date as TIMESTAMP)"
317:         - name: deferred_revenue_accounting_code_id
318:           data_type: VARCHAR
319:         - name: exchange_rate
320:           data_type: VARCHAR
321:         - name: exchange_rate_date
322:           data_type: DATE
323:         - name: home_currency
324:           data_type: VARCHAR
325:         - name: invoice_id
326:           data_type: VARCHAR
327:         - name: journal_entry_id
328:           data_type: VARCHAR
329:         - name: parent_account_id
330:           data_type: VARCHAR
331:         - name: processing_type
332:           data_type: BOOLEAN
333:         - name: product_id
334:           data_type: VARCHAR
335:         - name: product_rate_plan_charge_id
336:           data_type: VARCHAR
337:         - name: product_rate_plan_id
338:           data_type: VARCHAR
339:         - name: quantity
340:           data_type: BIGINT
341:         - name: rate_plan_charge_id
342:           data_type: VARCHAR
343:         - name: rate_plan_id
344:           data_type: VARCHAR
345:         - name: recognized_revenue_accounting_code_id
346:           data_type: VARCHAR
347:         - name: rev_rec_start_date
348:           data_type: TIMESTAMP
349:           source_expression: "try_cast(rev_rec_start_date as TIMESTAMP)"
350:         - name: service_end_date
351:           data_type: DATE
352:           source_expression: "try_cast(service_end_date as DATE)"
353:         - name: service_start_date
354:           data_type: DATE
355:           source_expression: "try_cast(service_start_date as DATE)"
356:         - name: sku
357:           data_type: VARCHAR
358:         - name: sold_to_contact_id
359:           data_type: VARCHAR
360:         - name: source_item_type
361:           data_type: VARCHAR
362:         - name: subscription_id
363:           data_type: VARCHAR
364:         - name: tax_amount
365:           data_type: BIGINT
366:         - name: tax_mode
367:           data_type: VARCHAR
368:         - name: transaction_currency
369:           data_type: VARCHAR
370:         - name: unit_price
371:           data_type: BIGINT
372:         - name: uom
373:           data_type: VARCHAR
374:         - name: updated_by_id
375:           data_type: VARCHAR
376:         - name: updated_date
377:           data_type: TIMESTAMP
378:           source_expression: "cast(updated_date as TIMESTAMP)"
379:         - name: is_most_recent_record
380:           data_type: BOOLEAN
381:           source_expression: "row_number() over (partition by id order by updated_date desc) = 1"
382:       row_filters:
383:         - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
384:           on_failure: delete_row
385:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice_item.sql`；SHA-256 `299d1eda1cae730f7257fc892e3e725b1e3e301008f6f69581f72b2ef9eefdd3`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_invoice_item_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS invoice_item_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("account_receivable_accounting_code_id" AS VARCHAR) AS account_receivable_accounting_code_id,
9:         try_cast("accounting_code" AS VARCHAR) AS accounting_code,
10:         try_cast("id" AS VARCHAR) AS amendment_id,
11:         try_cast("applied_to_invoice_item_id" AS VARCHAR) AS applied_to_invoice_item_id,
12:         try_cast("balance" AS BIGINT) AS balance,
13:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
14:         try_cast("charge_amount" AS BIGINT) AS charge_amount,
15:         try_cast("charge_amount_home_currency" AS VARCHAR) AS charge_amount_home_currency,
16:         try_cast(charge_date as TIMESTAMP) AS charge_date,
17:         try_cast("charge_name" AS VARCHAR) AS charge_name,
18:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
19:         try_cast(created_date as TIMESTAMP) AS created_date,
20:         try_cast("deferred_revenue_accounting_code_id" AS VARCHAR) AS deferred_revenue_accounting_code_id,
21:         try_cast("exchange_rate" AS VARCHAR) AS exchange_rate,
22:         try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date,
23:         try_cast("home_currency" AS VARCHAR) AS home_currency,
24:         try_cast("id" AS VARCHAR) AS invoice_id,
25:         try_cast("journal_entry_id" AS VARCHAR) AS journal_entry_id,
26:         try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
27:         try_cast("processing_type" AS BOOLEAN) AS processing_type,
28:         try_cast("id" AS VARCHAR) AS product_id,
29:         try_cast("product_rate_plan_charge_id" AS VARCHAR) AS product_rate_plan_charge_id,
30:         try_cast("id" AS VARCHAR) AS product_rate_plan_id,
31:         try_cast("quantity" AS BIGINT) AS quantity,
32:         try_cast("id" AS VARCHAR) AS rate_plan_charge_id,
33:         try_cast("id" AS VARCHAR) AS rate_plan_id,
34:         try_cast("recognized_revenue_accounting_code_id" AS VARCHAR) AS recognized_revenue_accounting_code_id,
35:         try_cast(rev_rec_start_date as TIMESTAMP) AS rev_rec_start_date,
36:         try_cast(service_end_date as DATE) AS service_end_date,
37:         try_cast(service_start_date as DATE) AS service_start_date,
38:         try_cast("sku" AS VARCHAR) AS sku,
39:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
40:         try_cast("source_item_type" AS VARCHAR) AS source_item_type,
41:         try_cast("id" AS VARCHAR) AS subscription_id,
42:         try_cast("tax_amount" AS BIGINT) AS tax_amount,
43:         try_cast("tax_mode" AS VARCHAR) AS tax_mode,
44:         try_cast("transaction_currency" AS VARCHAR) AS transaction_currency,
45:         try_cast("unit_price" AS BIGINT) AS unit_price,
46:         try_cast("uom" AS VARCHAR) AS uom,
47:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
48:         try_cast(updated_date as TIMESTAMP) AS updated_date,
49:         row_number() over (partition by id order by updated_date desc) = 1 AS is_most_recent_record
50: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__invoice_item.sql`；SHA-256 `04c36166e85200225d3c878eb0bc85ff88f8dbf78ccc93831dc21eeef997a1dc`。

```text
1: with base as (
2:     select * from raw.zuora_invoice_item_data
3:     where _fivetran_deleted is null or _fivetran_deleted = false
4: ),
5: final as (
6:     select
7:         id as invoice_item_id,
8:         account_id,
9:         account_receivable_accounting_code_id,
10:         accounting_code,
11:         amendment_id,
12:         applied_to_invoice_item_id,
13:         balance,
14:         bill_to_contact_id,
15:         charge_amount,
16:         charge_amount_home_currency,
17:         try_cast(charge_date as TIMESTAMP) as charge_date,
18:         charge_name,
19:         created_by_id,
20:         try_cast(created_date as TIMESTAMP) as created_date,
21:         deferred_revenue_accounting_code_id,
22:         exchange_rate,
23:         exchange_rate_date,
24:         home_currency,
25:         invoice_id,
26:         journal_entry_id,
27:         parent_account_id,
28:         processing_type,
29:         product_id,
30:         product_rate_plan_charge_id,
31:         product_rate_plan_id,
32:         quantity,
33:         rate_plan_charge_id,
34:         rate_plan_id,
35:         recognized_revenue_accounting_code_id,
36:         try_cast(rev_rec_start_date as TIMESTAMP) as rev_rec_start_date,
37:         try_cast(service_end_date as DATE) as service_end_date,
38:         try_cast(service_start_date as DATE) as service_start_date,
39:         sku,
40:         sold_to_contact_id,
41:         source_item_type,
42:         subscription_id,
43:         tax_amount,
44:         tax_mode,
45:         transaction_currency,
46:         unit_price,
47:         uom,
48:         updated_by_id,
49:         cast(updated_date as TIMESTAMP) as updated_date,
50:         row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
51:     from base
52: )
53: select * from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- source_account_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_amendment_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_invoice_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- type_processing_type（O）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_product_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_product_rate_plan_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_rate_plan_charge_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_rate_plan_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_subscription_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

event 13：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/13.json`；命令首行：`python3 - <<'PY'`。
event 14：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/14.json`；原始观察输出。
event 39：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/39.json`；命令首行：`python3 - <<'PY'`。
event 40：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/40.json`；原始观察输出。
event 45：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/45.json`；命令首行：`python3 - <<'PY'`。
event 69：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/69.json`；命令首行：`find / -maxdepth 3 -type d -name workspace 2>/dev/null | head; cat > result.md <<'EOF'`。

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

核实查询 **5** 条；代价档：**多条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_invoice_item_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_invoice_item_data","id","VARCHAR"],["zuora_invoice_item_data","_fivetran_deleted","VARCHAR"],["zuora_invoice_item_data","_fivetran_synced","VARCHAR"],["zuora_invoice_item_data","account_id","VARCHAR"],["zuora_invoice_item_data","account_receivable_accounting_code_id","VARCHAR"],["zuora_invoice_item_data","accounting_code","VARCHAR"],["zuora_invoice_item_data","accounting_period_id","VARCHAR"],["zuora_invoice_item_data","amendment_id","VARCHAR"],["zuora_invoice_item_data","applied_to_invoice_item_id","VARCHAR"],["zuora_invoice_item_data","balance","VARCHAR"],["zuora_invoice_item_data","bill_to_contact_id","VARCHAR"],["zuora_invoice_item_data","booking_reference","VARCHAR"],["zuora_invoice_item_data","charge_amount","VARCHAR"],["zuora_invoice_item_data","charge_amount_currency_rounding","VARCHAR"],["zuora_invoice_item_data","charge_amount_home_currency","VARCHAR"],["zuora_invoice_item_data","charge_date","VARCHAR"],["zuora_invoice_item_data","charge_name","VARCHAR"],["zuora_invoice_item_data","created_by_id","VARCHAR"],["zuora_invoice_item_data","created_date","VARCHAR"],["zuora_invoice_item_data","default_payment_method_id","VARCHAR"],["zuora_invoice_item_data","deferred_revenue_accounting_code_id","VARCHAR"],["zuora_invoice_item_data","exchange_rate","VARCHAR"],["zuora_invoice_item_data","exchange_rate_date","VARCHAR"],["zuora_invoice_item_data","exclude_item_billing_from_revenue_accounting","VARCHAR"],["zuora_invoice_item_data","home_currency","VARCHAR"],["zuora_invoice_item_data","invoice_id","VARCHAR"],["zuora_invoice_item_data","journal_entry_id","VARCHAR"],["zuora_invoice_item_data","journal_run_id","VARCHAR"],["zuora_invoice_item_data","parent_account_id","VARCHAR"],["zuora_invoice_item_data","processing_type","VARCHAR"],["zuora_invoice_item_data","product_id","VARCHAR"],["zuora_invoice_item_data","product_rate_plan_charge_id","VARCHAR"],["zuora_invoice_item_data","product_rate_plan_id","VARCHAR"],["zuora_invoice_item_data","provider_exchange_rate_date","VARCHAR"],["zuora_invoice_item_data","quantity","VARCHAR"],["zuora_invoice_item_data","rate_plan_charge_id","VARCHAR"],["zuora_invoice_item_data","rate_plan_id","VARCHAR"],["zuora_invoice_item_data","recognized_revenue_accounting_code_id","VARCHAR"],["zuora_invoice_item_data","rev_rec_start_date","VARCHAR"],["zuora_invoice_item_data","service_end_date","VARCHAR"],["zuora_invoice_item_data","service_start_date","VARCHAR"],["zuora_invoice_item_data","sku","VARCHAR"],["zuora_invoice_item_data","sold_to_contact_id","VARCHAR"],["zuora_invoice_item_data","source_item_type","VARCHAR"],["zuora_invoice_item_data","subscription_id","VARCHAR"],["zuora_invoice_item_data","tax_amount","VARCHAR"],["zuora_invoice_item_data","tax_code","VARCHAR"],["zuora_invoice_item_data","tax_exempt_amount","VARCHAR"],["zuora_invoice_item_data","tax_mode","VARCHAR"],["zuora_invoice_item_data","transaction_currency","VARCHAR"],["zuora_invoice_item_data","unit_price","VARCHAR"],["zuora_invoice_item_data","uom","VARCHAR"],["zuora_invoice_item_data","updated_by_id","VARCHAR"],["zuora_invoice_item_data","updated_date","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_invoice_item_data UNION ALL SELECT 'amendment_id' col,count(*) n,count(amendment_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(amendment_id as varchar)) same_as_id FROM raw.zuora_invoice_item_data UNION ALL SELECT 'invoice_id' col,count(*) n,count(invoice_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(invoice_id as varchar)) same_as_id FROM raw.zuora_invoice_item_data UNION ALL SELECT 'product_id' col,count(*) n,count(product_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(product_id as varchar)) same_as_id FROM raw.zuora_invoice_item_data UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(product_rate_plan_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(product_rate_plan_id as varchar)) same_as_id FROM raw.zuora_invoice_item_data UNION ALL SELECT 'rate_plan_charge_id' col,count(*) n,count(rate_plan_charge_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(rate_plan_charge_id as varchar)) same_as_id FROM raw.zuora_invoice_item_data UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(rate_plan_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(rate_plan_id as varchar)) same_as_id FROM raw.zuora_invoice_item_data UNION ALL SELECT 'subscription_id' col,count(*) n,count(subscription_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(subscription_id as varchar)) same_as_id FROM raw.zuora_invoice_item_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",3004,3004,0],["amendment_id",3004,3004,0],["invoice_id",3004,3004,0],["product_id",3004,3004,0],["product_rate_plan_id",3004,5,0],["rate_plan_charge_id",3004,5,0],["rate_plan_id",3004,5,0],["subscription_id",3004,5,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_invoice_item_data s UNION ALL SELECT 'amendment_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.amendment_id as varchar))) named_col_matches FROM raw.zuora_invoice_item_data s UNION ALL SELECT 'invoice_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.invoice_id as varchar))) named_col_matches FROM raw.zuora_invoice_item_data s UNION ALL SELECT 'product_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.product_id as varchar))) named_col_matches FROM raw.zuora_invoice_item_data s UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.product_rate_plan_id as varchar))) named_col_matches FROM raw.zuora_invoice_item_data s UNION ALL SELECT 'rate_plan_charge_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_charge_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_charge_data t WHERE cast(t.id as varchar)=cast(s.rate_plan_charge_id as varchar))) named_col_matches FROM raw.zuora_invoice_item_data s UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.rate_plan_id as varchar))) named_col_matches FROM raw.zuora_invoice_item_data s UNION ALL SELECT 'subscription_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.subscription_id as varchar))) named_col_matches FROM raw.zuora_invoice_item_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",3004,0,5],["amendment_id",3004,0,0],["invoice_id",3004,0,5],["product_id",3004,0,5],["product_rate_plan_id",3004,0,0],["rate_plan_charge_id",3004,0,0],["rate_plan_id",3004,0,0],["subscription_id",3004,0,0]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_invoice_item_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'amendment_id' col,count(*) n,count(s.amendment_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.amendment_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'invoice_id' col,count(*) n,count(s.invoice_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.invoice_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'product_id' col,count(*) n,count(s.product_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.product_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(s.product_rate_plan_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.product_rate_plan_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'rate_plan_charge_id' col,count(*) n,count(s.rate_plan_charge_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_charge_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_charge_data t WHERE cast(t.id as varchar)=cast(s.rate_plan_charge_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(s.rate_plan_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.rate_plan_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'subscription_id' col,count(*) n,count(s.subscription_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.subscription_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",1495,1495,0,5],["amendment_id",1495,1495,0,0],["invoice_id",1495,1495,0,5],["product_id",1495,1495,0,5],["product_rate_plan_id",1495,5,0,0],["rate_plan_charge_id",1495,5,0,0],["rate_plan_id",1495,5,0,0],["subscription_id",1495,5,0,0]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_invoice_item_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'amendment_id' col,count(*) n,count(amendment_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(amendment_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(amendment_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'invoice_id' col,count(*) n,count(invoice_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(invoice_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(invoice_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'product_id' col,count(*) n,count(product_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(product_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(product_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(product_rate_plan_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(product_rate_plan_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(product_rate_plan_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'rate_plan_charge_id' col,count(*) n,count(rate_plan_charge_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(rate_plan_charge_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(rate_plan_charge_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(rate_plan_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(rate_plan_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(rate_plan_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'subscription_id' col,count(*) n,count(subscription_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(subscription_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(subscription_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",1495,1495,5,0],["amendment_id",1495,1495,5,1490],["invoice_id",1495,1495,5,0],["product_id",1495,1495,5,1490],["product_rate_plan_id",1495,5,5,0],["rate_plan_charge_id",1495,5,5,0],["rate_plan_id",1495,5,5,0],["subscription_id",1495,5,5,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__invoice_item.json
[024_reruns_impl-030_stg_zuora__invoice_item.json](../024_reruns_impl-030_stg_zuora__invoice_item.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|16435|否|
|L1|1495|1495|1495|16430|否|
|L2|1495|1495|1495|16430|否|
|L3|1495|1495|1495|16430|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/baseline.sql`；SHA-256 `299d1eda1cae730f7257fc892e3e725b1e3e301008f6f69581f72b2ef9eefdd3`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|16435|否|
|L1|1495|1495|1495|16430|否|
|L2|1495|1495|1495|16430|否|
|L3|1495|1495|1495|16430|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### source_account_id
主因；类别候选A。把本实体 id 当作 account_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少1495。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第7行、offset 216起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/source_account_id.sql`；SHA-256 `bf7680bc9b043c0659e0d1bdd9143505640fbe1819948efe13ebfe2e2ce5bde4`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14940|否|
|L1|1495|1495|1495|14935|否|
|L2|1495|1495|1495|14935|否|
|L3|1495|1495|1495|14935|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### source_amendment_id
主因；类别候选A。把本实体 id 当作 amendment_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少1495。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第10行、offset 443起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS amendment_id
```

修改后：
```sql
try_cast("amendment_id" AS VARCHAR) AS amendment_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/source_amendment_id.sql`；SHA-256 `82767fb5e4b879634b8345a1535fcc74c7d6acafd64cb276a5a932427f631c18`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14940|否|
|L1|1495|1495|1495|14935|否|
|L2|1495|1495|1495|14935|否|
|L3|1495|1495|1495|14935|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### type_balance
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少1490。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第12行、offset 583起替换；其他字节相同。
原表达式：
```sql
try_cast("balance" AS BIGINT) AS balance
```

修改后：
```sql
"balance" AS balance
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/type_balance.sql`；SHA-256 `62757f7fd23d905615240e88986f4a0096ceb9eceed237049d0301fb6ec228a3`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14945|否|
|L1|1495|1495|1495|14940|否|
|L2|1495|1495|1495|14940|否|
|L3|1495|1495|1495|14940|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### type_exchange_rate_date
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少1490。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第22行、offset 1271起替换；其他字节相同。
原表达式：
```sql
try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date
```

修改后：
```sql
"exchange_rate_date" AS exchange_rate_date
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/type_exchange_rate_date.sql`；SHA-256 `e2fb188da15237902e3465dcd67566461a070176fa4a224ff024f20dee4ac7ab`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14945|否|
|L1|1495|1495|1495|14940|否|
|L2|1495|1495|1495|14940|否|
|L3|1495|1495|1495|14940|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"balance":1490,"invoice_id":1495,"processing_type":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"balance":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"balance":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"balance":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### source_invoice_id
主因；类别候选A。把本实体 id 当作 invoice_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少1495。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第24行、offset 1404起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS invoice_id
```

修改后：
```sql
try_cast("invoice_id" AS VARCHAR) AS invoice_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/source_invoice_id.sql`；SHA-256 `f381717665caf324a7db059b4d82479724a76557e26ca70a8bd1edd5de27a861`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14940|否|
|L1|1495|1495|1495|14935|否|
|L2|1495|1495|1495|14935|否|
|L3|1495|1495|1495|14935|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"processing_type":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### type_processing_type
主因；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少1495。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第27行、offset 1593起替换；其他字节相同。
原表达式：
```sql
try_cast("processing_type" AS BOOLEAN) AS processing_type
```

修改后：
```sql
"processing_type" AS processing_type
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/type_processing_type.sql`；SHA-256 `f8fadc8b73f172d304b65d7a043e45288cf3277fc2d209125ac3c77b77777195`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14940|否|
|L1|1495|1495|1495|14940|否|
|L2|1495|1495|1495|14940|否|
|L3|1495|1495|1495|14940|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### source_product_id
主因；类别候选A。把本实体 id 当作 product_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少1495。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第28行、offset 1660起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS product_id
```

修改后：
```sql
try_cast("product_id" AS VARCHAR) AS product_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/source_product_id.sql`；SHA-256 `54ddc34de860e2b04c85125a4d0cfdc129079b66ab1d441582378f8b772628b8`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14940|否|
|L1|1495|1495|1495|14935|否|
|L2|1495|1495|1495|14935|否|
|L3|1495|1495|1495|14935|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### source_product_rate_plan_id
主因；类别候选A。把本实体 id 当作 product_rate_plan_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少1495。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第30行、offset 1800起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS product_rate_plan_id
```

修改后：
```sql
try_cast("product_rate_plan_id" AS VARCHAR) AS product_rate_plan_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/source_product_rate_plan_id.sql`；SHA-256 `eca3c2a9a74274036ca1afb4d0728a1437e63b0741ed2ee6d3711aa370ee86e6`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14940|否|
|L1|1495|1495|1495|14935|否|
|L2|1495|1495|1495|14935|否|
|L3|1495|1495|1495|14935|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1495,"product_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### source_rate_plan_charge_id
主因；类别候选A。把本实体 id 当作 rate_plan_charge_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少1495。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第32行、offset 1911起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS rate_plan_charge_id
```

修改后：
```sql
try_cast("rate_plan_charge_id" AS VARCHAR) AS rate_plan_charge_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/source_rate_plan_charge_id.sql`；SHA-256 `dc0c65a863182a3c2aced439247da2c5e96809feb9d28bddef1e8636643a5579`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14940|否|
|L1|1495|1495|1495|14935|否|
|L2|1495|1495|1495|14935|否|
|L3|1495|1495|1495|14935|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_id":1495,"subscription_id":1495}`

#### source_rate_plan_id
主因；类别候选A。把本实体 id 当作 rate_plan_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少1495。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第33行、offset 1969起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS rate_plan_id
```

修改后：
```sql
try_cast("rate_plan_id" AS VARCHAR) AS rate_plan_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/source_rate_plan_id.sql`；SHA-256 `ca7b8ebeb30c788644b4750b1d69d6fd9013e9bb8e90a5aea1182adcb480de2c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14940|否|
|L1|1495|1495|1495|14935|否|
|L2|1495|1495|1495|14935|否|
|L3|1495|1495|1495|14935|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"subscription_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"subscription_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"subscription_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"subscription_id":1495}`

#### source_subscription_id
主因；类别候选A。把本实体 id 当作 subscription_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少1495。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第41行、offset 2521起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS subscription_id
```

修改后：
```sql
try_cast("subscription_id" AS VARCHAR) AS subscription_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_item/source_subscription_id.sql`；SHA-256 `0a9a438d65994f24b59940cd16edc726c1471e81922c7d67b37c0e70d986877c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1495|14940|否|
|L1|1495|1495|1495|14935|否|
|L2|1495|1495|1495|14935|否|
|L3|1495|1495|1495|14935|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1495,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495}`
- L1：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495}`
- L2：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495}`
- L3：`{"account_id":1495,"amendment_id":1495,"balance":1490,"exchange_rate_date":1490,"invoice_id":1495,"processing_type":1490,"product_id":1495,"product_rate_plan_id":1495,"rate_plan_charge_id":1495,"rate_plan_id":1495}`
## 规则问题

多数具名候选呈错位文本/时间或NULL，不能只因gold选同名列就归U；选择A。processing_type等显式类型冲突为O；互相并列按格子比较。

