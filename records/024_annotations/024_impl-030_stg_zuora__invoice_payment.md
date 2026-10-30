# impl-030 · stg_zuora__invoice_payment

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**多因并列（A、U）**；把握：低。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：无。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__invoice_payment.md](../024_packages/024_impl-030_stg_zuora__invoice_payment.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
386:     - name: stg_zuora__invoice_payment
387:       description: "Cleaned invoice payment join table; latest snapshot indicator provided."
388:       source_table: raw.zuora_invoice_payment_data
389:       columns:
390:         - name: invoice_payment_id
391:           data_type: VARCHAR
392:         - name: account_id
393:           data_type: VARCHAR
394:         - name: account_receivable_accounting_code_id
395:           data_type: VARCHAR
396:         - name: accounting_period_id
397:           data_type: VARCHAR
398:         - name: amount
399:           data_type: DOUBLE
400:         - name: amount_currency_rounding
401:           data_type: BIGINT
402:         - name: amount_home_currency
403:           data_type: DOUBLE
404:         - name: bill_to_contact_id
405:           data_type: VARCHAR
406:         - name: cash_accounting_code_id
407:           data_type: VARCHAR
408:         - name: created_by_id
409:           data_type: VARCHAR
410:         - name: created_date
411:           data_type: TIMESTAMP
412:         - name: default_payment_method_id
413:           data_type: VARCHAR
414:         - name: exchange_rate
415:           data_type: BIGINT
416:         - name: exchange_rate_date
417:           data_type: DATE
418:         - name: home_currency
419:           data_type: VARCHAR
420:         - name: invoice_id
421:           data_type: VARCHAR
422:         - name: journal_entry_id
423:           data_type: VARCHAR
424:         - name: journal_run_id
425:           data_type: VARCHAR
426:         - name: parent_account_id
427:           data_type: VARCHAR
428:         - name: payment_id
429:           data_type: VARCHAR
430:         - name: payment_method_id
431:           data_type: VARCHAR
432:         - name: provider_exchange_rate_date
433:           data_type: DATE
434:         - name: refund_amount
435:           data_type: BOOLEAN
436:         - name: sold_to_contact_id
437:           data_type: VARCHAR
438:         - name: transaction_currency
439:           data_type: VARCHAR
440:         - name: updated_by_id
441:           data_type: VARCHAR
442:         - name: updated_date
443:           data_type: TIMESTAMP
444:         - name: is_most_recent_record
445:           data_type: BOOLEAN
446:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice_payment.sql`；SHA-256 `2f505773c65231ab0a2911415ac639f03743a81e37a8088c2a590ebf0c799ec9`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_invoice_payment_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         try_cast("id" AS VARCHAR) AS invoice_payment_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("account_receivable_accounting_code_id" AS VARCHAR) AS account_receivable_accounting_code_id,
9:         try_cast("accounting_period_id" AS VARCHAR) AS accounting_period_id,
10:         try_cast("amount" AS DOUBLE) AS amount,
11:         try_cast("amount_currency_rounding" AS BIGINT) AS amount_currency_rounding,
12:         try_cast("amount_home_currency" AS DOUBLE) AS amount_home_currency,
13:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
14:         try_cast("cash_accounting_code_id" AS VARCHAR) AS cash_accounting_code_id,
15:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
16:         try_cast("created_date" AS TIMESTAMP) AS created_date,
17:         try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
18:         try_cast("exchange_rate" AS BIGINT) AS exchange_rate,
19:         try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date,
20:         try_cast("home_currency" AS VARCHAR) AS home_currency,
21:         try_cast("id" AS VARCHAR) AS invoice_id,
22:         try_cast("journal_entry_id" AS VARCHAR) AS journal_entry_id,
23:         try_cast("journal_run_id" AS VARCHAR) AS journal_run_id,
24:         try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
25:         try_cast("id" AS VARCHAR) AS payment_id,
26:         try_cast("id" AS VARCHAR) AS payment_method_id,
27:         try_cast("provider_exchange_rate_date" AS DATE) AS provider_exchange_rate_date,
28:         try_cast("refund_amount" AS BOOLEAN) AS refund_amount,
29:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
30:         try_cast("transaction_currency" AS VARCHAR) AS transaction_currency,
31:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
32:         try_cast("updated_date" AS TIMESTAMP) AS updated_date,
33:         row_number() over (partition by id order by try_cast(updated_date as timestamp) desc NULLS LAST) = 1 AS is_most_recent_record
34: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__invoice_payment.sql`；SHA-256 `84efbed0db65a4fdd07b0105880f1de73e93b03190afbe69155a97364d539354`。

```text
1: with base as (
2:     select * from raw.zuora_invoice_payment_data
3:     where _fivetran_deleted is null or _fivetran_deleted = false
4: ),
5: final as (
6:     select
7:         id as invoice_payment_id,
8:         account_id,
9:         account_receivable_accounting_code_id,
10:         accounting_period_id,
11:         amount,
12:         amount_currency_rounding,
13:         amount_home_currency,
14:         bill_to_contact_id,
15:         cash_accounting_code_id,
16:         created_by_id,
17:         cast(created_date as TIMESTAMP) as created_date,
18:         default_payment_method_id,
19:         exchange_rate,
20:         exchange_rate_date,
21:         home_currency,
22:         invoice_id,
23:         journal_entry_id,
24:         journal_run_id,
25:         parent_account_id,
26:         payment_id,
27:         payment_method_id,
28:         provider_exchange_rate_date,
29:         refund_amount,
30:         sold_to_contact_id,
31:         transaction_currency,
32:         updated_by_id,
33:         cast(updated_date as TIMESTAMP) as updated_date,
34:         row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
35:     from base
36: )
37: select * from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- source_account_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 account_id。
P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。

- source_invoice_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_payment_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 payment_id。
P：本实体id可替代payment_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。

- source_payment_method_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 payment_method_id。
P：本实体id可替代payment_method_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_invoice_payment_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_invoice_payment_data","id","VARCHAR"],["zuora_invoice_payment_data","_fivetran_deleted","BOOLEAN"],["zuora_invoice_payment_data","_fivetran_synced","TIMESTAMP"],["zuora_invoice_payment_data","account_id","VARCHAR"],["zuora_invoice_payment_data","account_receivable_accounting_code_id","VARCHAR"],["zuora_invoice_payment_data","accounting_period_id","VARCHAR"],["zuora_invoice_payment_data","amount","DOUBLE"],["zuora_invoice_payment_data","amount_currency_rounding","BIGINT"],["zuora_invoice_payment_data","amount_home_currency","DOUBLE"],["zuora_invoice_payment_data","bill_to_contact_id","VARCHAR"],["zuora_invoice_payment_data","cash_accounting_code_id","VARCHAR"],["zuora_invoice_payment_data","created_by_id","VARCHAR"],["zuora_invoice_payment_data","created_date","TIMESTAMP"],["zuora_invoice_payment_data","default_payment_method_id","VARCHAR"],["zuora_invoice_payment_data","exchange_rate","BIGINT"],["zuora_invoice_payment_data","exchange_rate_date","DATE"],["zuora_invoice_payment_data","home_currency","VARCHAR"],["zuora_invoice_payment_data","invoice_id","VARCHAR"],["zuora_invoice_payment_data","journal_entry_id","VARCHAR"],["zuora_invoice_payment_data","journal_run_id","VARCHAR"],["zuora_invoice_payment_data","parent_account_id","VARCHAR"],["zuora_invoice_payment_data","payment_id","VARCHAR"],["zuora_invoice_payment_data","payment_method_id","VARCHAR"],["zuora_invoice_payment_data","provider_exchange_rate_date","DATE"],["zuora_invoice_payment_data","refund_amount","BIGINT"],["zuora_invoice_payment_data","sold_to_contact_id","VARCHAR"],["zuora_invoice_payment_data","transaction_currency","VARCHAR"],["zuora_invoice_payment_data","updated_by_id","VARCHAR"],["zuora_invoice_payment_data","updated_date","TIMESTAMP"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_invoice_payment_data UNION ALL SELECT 'invoice_id' col,count(*) n,count(invoice_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(invoice_id as varchar)) same_as_id FROM raw.zuora_invoice_payment_data UNION ALL SELECT 'payment_id' col,count(*) n,count(payment_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(payment_id as varchar)) same_as_id FROM raw.zuora_invoice_payment_data UNION ALL SELECT 'payment_method_id' col,count(*) n,count(payment_method_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(payment_method_id as varchar)) same_as_id FROM raw.zuora_invoice_payment_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",6,6,0],["invoice_id",6,6,0],["payment_id",6,6,0],["payment_method_id",6,6,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_invoice_payment_data s UNION ALL SELECT 'invoice_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.invoice_id as varchar))) named_col_matches FROM raw.zuora_invoice_payment_data s UNION ALL SELECT 'payment_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_data t WHERE cast(t.id as varchar)=cast(s.payment_id as varchar))) named_col_matches FROM raw.zuora_invoice_payment_data s UNION ALL SELECT 'payment_method_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.payment_method_id as varchar))) named_col_matches FROM raw.zuora_invoice_payment_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",6,0,2],["invoice_id",6,6,0],["payment_id",6,0,3],["payment_method_id",6,0,4]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_invoice_payment_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'invoice_id' col,count(*) n,count(s.invoice_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.invoice_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'payment_id' col,count(*) n,count(s.payment_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_data t WHERE cast(t.id as varchar)=cast(s.payment_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'payment_method_id' col,count(*) n,count(s.payment_method_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.payment_method_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",6,6,0,2],["invoice_id",6,6,6,0],["payment_id",6,6,0,3],["payment_method_id",6,6,0,4]]}
```


### 诊断：多处组合仅诊断（不用于单点原因排名）
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_invoice_payment_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT
        try_cast("id" AS VARCHAR) AS invoice_payment_id,
        try_cast("account_id" AS VARCHAR) AS account_id,
        try_cast("account_receivable_accounting_code_id" AS VARCHAR) AS account_receivable_accounting_code_id,
        try_cast("accounting_period_id" AS VARCHAR) AS accounting_period_id,
        try_cast("amount" AS DOUBLE) AS amount,
        try_cast("amount_currency_rounding" AS BIGINT) AS amount_currency_rounding,
        try_cast("amount_home_currency" AS DOUBLE) AS amount_home_currency,
        try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
        try_cast("cash_accounting_code_id" AS VARCHAR) AS cash_accounting_code_id,
        try_cast("created_by_id" AS VARCHAR) AS created_by_id,
        try_cast("created_date" AS TIMESTAMP) AS created_date,
        try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
        try_cast("exchange_rate" AS BIGINT) AS exchange_rate,
        try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date,
        try_cast("home_currency" AS VARCHAR) AS home_currency,
        try_cast("invoice_id" AS VARCHAR) AS invoice_id,
        try_cast("journal_entry_id" AS VARCHAR) AS journal_entry_id,
        try_cast("journal_run_id" AS VARCHAR) AS journal_run_id,
        try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
        try_cast("payment_id" AS VARCHAR) AS payment_id,
        try_cast("payment_method_id" AS VARCHAR) AS payment_method_id,
        try_cast("provider_exchange_rate_date" AS DATE) AS provider_exchange_rate_date,
        try_cast("refund_amount" AS BOOLEAN) AS refund_amount,
        try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
        try_cast("transaction_currency" AS VARCHAR) AS transaction_currency,
        try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
        try_cast("updated_date" AS TIMESTAMP) AS updated_date,
        row_number() over (partition by id order by try_cast(updated_date as timestamp) desc NULLS LAST) = 1 AS is_most_recent_record
FROM source_rows
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|6|6|否|
|L1|6|6|0|0|是|
|L2|6|6|0|0|是|
|L3|6|6|0|0|是|

首次整表匹配：**L1**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"refund_amount":6}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
labels：`["source_account_id","source_invoice_id","source_payment_id","source_payment_method_id"]`

### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_invoice_payment_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'invoice_id' col,count(*) n,count(invoice_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(invoice_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(invoice_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'payment_id' col,count(*) n,count(payment_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(payment_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(payment_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'payment_method_id' col,count(*) n,count(payment_method_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(payment_method_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(payment_method_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",6,6,6,0],["invoice_id",6,6,6,0],["payment_id",6,6,6,0],["payment_method_id",6,6,6,0]]}
```


### 诊断：agent实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_zuora__invoice_payment'
```


```json
{"columns":["column_name","data_type"],"rows":[["invoice_payment_id","VARCHAR"],["account_id","VARCHAR"],["account_receivable_accounting_code_id","VARCHAR"],["accounting_period_id","VARCHAR"],["amount","DOUBLE"],["amount_currency_rounding","BIGINT"],["amount_home_currency","DOUBLE"],["bill_to_contact_id","VARCHAR"],["cash_accounting_code_id","VARCHAR"],["created_by_id","VARCHAR"],["created_date","TIMESTAMP"],["default_payment_method_id","VARCHAR"],["exchange_rate","BIGINT"],["exchange_rate_date","DATE"],["home_currency","VARCHAR"],["invoice_id","VARCHAR"],["journal_entry_id","VARCHAR"],["journal_run_id","VARCHAR"],["parent_account_id","VARCHAR"],["payment_id","VARCHAR"],["payment_method_id","VARCHAR"],["provider_exchange_rate_date","DATE"],["refund_amount","BOOLEAN"],["sold_to_contact_id","VARCHAR"],["transaction_currency","VARCHAR"],["updated_by_id","VARCHAR"],["updated_date","TIMESTAMP"],["is_most_recent_record","BOOLEAN"]]}
```


### 诊断：agent有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT invoice_payment_id,account_id,invoice_id,payment_id,payment_method_id FROM staging.stg_zuora__invoice_payment LIMIT 3
```


```json
{"columns":["invoice_payment_id","account_id","invoice_id","payment_id","payment_method_id"],"rows":[["dff38ac0ea5bbc65bce34ebdb935e174","dff38ac0ea5bbc65bce34ebdb935e174","dff38ac0ea5bbc65bce34ebdb935e174","dff38ac0ea5bbc65bce34ebdb935e174","dff38ac0ea5bbc65bce34ebdb935e174"],["dff38ac0f3f8366b90ae206d1d20ab4e","dff38ac0f3f8366b90ae206d1d20ab4e","dff38ac0f3f8366b90ae206d1d20ab4e","dff38ac0f3f8366b90ae206d1d20ab4e","dff38ac0f3f8366b90ae206d1d20ab4e"],["dff38ac0a531a01100012160a3061ef6","dff38ac0a531a01100012160a3061ef6","dff38ac0a531a01100012160a3061ef6","dff38ac0a531a01100012160a3061ef6","dff38ac0a531a01100012160a3061ef6"]]}
```


### 诊断：gold实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_zuora__invoice_payment'
```


```json
{"columns":["column_name","data_type"],"rows":[["invoice_payment_id","VARCHAR"],["account_id","VARCHAR"],["account_receivable_accounting_code_id","VARCHAR"],["accounting_period_id","VARCHAR"],["amount","DOUBLE"],["amount_currency_rounding","BIGINT"],["amount_home_currency","DOUBLE"],["bill_to_contact_id","VARCHAR"],["cash_accounting_code_id","VARCHAR"],["created_by_id","VARCHAR"],["created_date","TIMESTAMP"],["default_payment_method_id","VARCHAR"],["exchange_rate","BIGINT"],["exchange_rate_date","DATE"],["home_currency","VARCHAR"],["invoice_id","VARCHAR"],["journal_entry_id","VARCHAR"],["journal_run_id","VARCHAR"],["parent_account_id","VARCHAR"],["payment_id","VARCHAR"],["payment_method_id","VARCHAR"],["provider_exchange_rate_date","DATE"],["refund_amount","BIGINT"],["sold_to_contact_id","VARCHAR"],["transaction_currency","VARCHAR"],["updated_by_id","VARCHAR"],["updated_date","TIMESTAMP"],["is_most_recent_record","BOOLEAN"]]}
```


### 诊断：gold有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT invoice_payment_id,account_id,invoice_id,payment_id,payment_method_id FROM staging.stg_zuora__invoice_payment LIMIT 3
```


```json
{"columns":["invoice_payment_id","account_id","invoice_id","payment_id","payment_method_id"],"rows":[["dff38ac0dfa53a25cf026658c1631e92","dff38ac0df6edbfb4cb3774f7e21f752","dff38ac0525d25467663ad8f25585b11","dff38ac0af743beba444e05e5e91c181","dff38ac0cedd90b815a1ef1c76bcf96e"],["dff38ac0ea5bbc65bce34ebdb935e174","dff38ac00240057303623f9ba5542afa","dff38ac0750d2cf8e346512ff02a4bf4","dff38ac039e59f89bd904be0ce3c1dfd","dff38ac0f13667e55db35690ddcb8d0a"],["dff38ac0f3f8366b90ae206d1d20ab4e","dff38ac075d55abbfe084047f9668d0a","dff38ac0722b678b635d83c78995f78b","dff38ac08b23c53f8756264bae72ec59","dff38ac0f13667e55db35690ddcb8d0a"]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__invoice_payment.json
[024_reruns_impl-030_stg_zuora__invoice_payment.json](../024_reruns_impl-030_stg_zuora__invoice_payment.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|12|324|否|
|L1|6|6|12|324|否|
|L2|6|6|12|324|否|
|L3|6|6|12|324|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L1：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L2：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L3：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__invoice_payment/baseline.sql`；SHA-256 `2f505773c65231ab0a2911415ac639f03743a81e37a8088c2a590ebf0c799ec9`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|12|324|否|
|L1|6|6|12|324|否|
|L2|6|6|12|324|否|
|L3|6|6|12|324|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L1：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L2：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L3：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`

#### source_account_id
主因；类别候选U。P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第7行、offset 245起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_payment/source_account_id.sql`；SHA-256 `2a9aba684a19d9a4c8de1160ff0aeccb448f3e7d0c524d2700f5c5ba4e1fbf38`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|12|324|否|
|L1|6|6|12|324|否|
|L2|6|6|12|324|否|
|L3|6|6|12|324|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L1：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L2：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L3：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`

#### source_invoice_id
主因；类别候选A。把本实体 id 当作 invoice_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第21行、offset 1254起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS invoice_id
```

修改后：
```sql
try_cast("invoice_id" AS VARCHAR) AS invoice_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_payment/source_invoice_id.sql`；SHA-256 `12a5ac33b5cea336de017aab7ba5638f1e04779f1ff8ce7d2a51802cd9f95535`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|12|324|否|
|L1|6|6|12|324|否|
|L2|6|6|12|324|否|
|L3|6|6|12|324|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L1：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L2：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L3：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`

#### source_payment_id
主因；类别候选U。P：本实体id可替代payment_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第25行、offset 1508起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS payment_id
```

修改后：
```sql
try_cast("payment_id" AS VARCHAR) AS payment_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_payment/source_payment_id.sql`；SHA-256 `ea38e2856e5d16bba62d36238ce3a91d697269759436a30ffce698388d4d4fcd`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|12|324|否|
|L1|6|6|12|324|否|
|L2|6|6|12|324|否|
|L3|6|6|12|324|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L1：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L2：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L3：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`

#### source_payment_method_id
主因；类别候选U。P：本实体id可替代payment_method_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第26行、offset 1557起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS payment_method_id
```

修改后：
```sql
try_cast("payment_method_id" AS VARCHAR) AS payment_method_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__invoice_payment/source_payment_method_id.sql`；SHA-256 `12519e7e303325ab3876bdbe71106fccc77b5c945924806513a06c53f5356ad4`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|12|324|否|
|L1|6|6|12|324|否|
|L2|6|6|12|324|否|
|L3|6|6|12|324|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L1：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L2：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L3：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
### 024_supplement_reruns_impl-030_stg_zuora__invoice_payment.json
[024_supplement_reruns_impl-030_stg_zuora__invoice_payment.json](../024_supplement_reruns_impl-030_stg_zuora__invoice_payment.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|12|324|否|
|L1|6|6|12|324|否|
|L2|6|6|12|324|否|
|L3|6|6|12|324|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L1：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L2：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L3：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`

#### baseline
私有SQL：`data/024_supplement_work/impl-030_stg_zuora__invoice_payment/baseline.sql`；SHA-256 `2f505773c65231ab0a2911415ac639f03743a81e37a8088c2a590ebf0c799ec9`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|12|324|否|
|L1|6|6|12|324|否|
|L2|6|6|12|324|否|
|L3|6|6|12|324|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L1：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L2：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L3：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`

#### refund_type
不计参与因素；类别候选O。契约BOOLEAN，gold BIGINT，单独诊断。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第28行、offset 1701起替换；其他字节相同。
原表达式：
```sql
try_cast("refund_amount" AS BOOLEAN) AS refund_amount
```

修改后：
```sql
refund_amount AS refund_amount
```

私有SQL：`data/024_supplement_work/impl-030_stg_zuora__invoice_payment/refund_type.sql`；SHA-256 `a0197a2f5826c8e89a3c3d6346b7b26db760b313def8fe0f3bc64a3bd79a8cd5`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|12|324|否|
|L1|6|6|12|324|否|
|L2|6|6|12|324|否|
|L3|6|6|12|324|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L1：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L2：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
- L3：`{"invoice_payment_id":12,"account_id":12,"account_receivable_accounting_code_id":12,"accounting_period_id":12,"bill_to_contact_id":12,"cash_accounting_code_id":12,"created_by_id":12,"default_payment_method_id":12,"invoice_id":12,"journal_entry_id":12,"journal_run_id":12,"parent_account_id":12,"payment_id":12,"payment_method_id":12,"sold_to_contact_id":12,"updated_by_id":12,"amount":12,"amount_currency_rounding":12,"amount_home_currency":12,"exchange_rate":12,"exchange_rate_date":12,"home_currency":12,"is_most_recent_record":12,"provider_exchange_rate_date":12,"refund_amount":12,"transaction_currency":12,"updated_date":12}`
## 规则问题

四处关系键互相遮蔽，单改行/格减量全为0。§5所有单项仍并列，§3并列U只需前三条件且减量相等；§4又规定零改善不算因素。按§9选择仅把三个已验证U与未定invoice_id来源A记为零改善多因并列（低把握），不声称U严格第4条件通过；另一读法是只能保留U标记而无法指定主因。组合诊断L1匹配仅定位交互，不作单点证据。

