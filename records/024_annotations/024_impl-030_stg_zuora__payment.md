# impl-030 · stg_zuora__payment

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**多因并列（O、U）**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：O：type_amount（行减0，格减1）；O：type_amount_home_currency（行减0，格减4）；O：type_applied_amount（行减0，格减4）；O：type_effective_date（行减0，格减718）；O：type_exchange_rate_date（行减0，格减718）；O：type_unapplied_amount（行减0，格减4）。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__payment.md](../024_packages/024_impl-030_stg_zuora__payment.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
447:     - name: stg_zuora__payment
448:       description: "Cleaned payments with safe timestamp casting and latest snapshot indicator."
449:       source_table: raw.zuora_payment_data
450:       columns:
451:         - name: payment_id
452:           data_type: VARCHAR
453:           source_expression: "id"
454:         - name: account_id
455:           data_type: VARCHAR
456:         - name: accounting_code
457:           data_type: VARCHAR
458:         - name: amount
459:           data_type: DOUBLE
460:         - name: amount_home_currency
461:           data_type: DOUBLE
462:         - name: applied_amount
463:           data_type: DOUBLE
464:         - name: applied_credit_balance_amount
465:           data_type: DOUBLE
466:         - name: bill_to_contact_id
467:           data_type: VARCHAR
468:         - name: cancelled_on
469:           data_type: TIMESTAMP
470:           source_expression: "try_cast(cancelled_on as TIMESTAMP)"
471:         - name: comment
472:           data_type: VARCHAR
473:         - name: created_by_id
474:           data_type: VARCHAR
475:         - name: created_date
476:           data_type: TIMESTAMP
477:           source_expression: "cast(created_date as TIMESTAMP)"
478:         - name: currency
479:           data_type: VARCHAR
480:         - name: effective_date
481:           data_type: DATE
482:         - name: exchange_rate
483:           data_type: VARCHAR
484:         - name: exchange_rate_date
485:           data_type: DATE
486:         - name: home_currency
487:           data_type: VARCHAR
488:         - name: parent_account_id
489:           data_type: VARCHAR
490:         - name: payment_method_id
491:           data_type: VARCHAR
492:         - name: payment_number
493:           data_type: VARCHAR
494:         - name: refund_amount
495:           data_type: DOUBLE
496:         - name: settled_on
497:           data_type: TIMESTAMP
498:           source_expression: "try_cast(settled_on as TIMESTAMP)"
499:         - name: sold_to_contact_id
500:           data_type: VARCHAR
501:         - name: status
502:           data_type: VARCHAR
503:         - name: submitted_on
504:           data_type: TIMESTAMP
505:           source_expression: "try_cast(submitted_on as TIMESTAMP)"
506:         - name: transaction_currency
507:           data_type: VARCHAR
508:         - name: transferred_to_accounting
509:           data_type: VARCHAR
510:         - name: type
511:           data_type: VARCHAR
512:         - name: unapplied_amount
513:           data_type: DOUBLE
514:         - name: updated_by_id
515:           data_type: VARCHAR
516:         - name: updated_date
517:           data_type: TIMESTAMP
518:           source_expression: "cast(updated_date as TIMESTAMP)"
519:         - name: is_most_recent_record
520:           data_type: BOOLEAN
521:           source_expression: "row_number() over (partition by id order by updated_date desc) = 1"
522:       row_filters:
523:         - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
524:           on_failure: delete_row
525:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__payment.sql`；SHA-256 `813d0dda480cefe9d074047be69cd2a4999c9b1d6b9b8c4568e64f84729340f3`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_payment_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS payment_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("accounting_code" AS VARCHAR) AS accounting_code,
9:         try_cast("amount" AS DOUBLE) AS amount,
10:         try_cast("amount_home_currency" AS DOUBLE) AS amount_home_currency,
11:         try_cast("applied_amount" AS DOUBLE) AS applied_amount,
12:         try_cast("applied_credit_balance_amount" AS DOUBLE) AS applied_credit_balance_amount,
13:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
14:         try_cast(cancelled_on as TIMESTAMP) AS cancelled_on,
15:         try_cast("comment" AS VARCHAR) AS comment,
16:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
17:         try_cast(created_date as TIMESTAMP) AS created_date,
18:         try_cast("currency" AS VARCHAR) AS currency,
19:         try_cast("effective_date" AS DATE) AS effective_date,
20:         try_cast("exchange_rate" AS VARCHAR) AS exchange_rate,
21:         try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date,
22:         try_cast("home_currency" AS VARCHAR) AS home_currency,
23:         try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
24:         try_cast("id" AS VARCHAR) AS payment_method_id,
25:         try_cast("payment_number" AS VARCHAR) AS payment_number,
26:         try_cast("refund_amount" AS DOUBLE) AS refund_amount,
27:         try_cast(settled_on as TIMESTAMP) AS settled_on,
28:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
29:         try_cast("status" AS VARCHAR) AS status,
30:         try_cast(submitted_on as TIMESTAMP) AS submitted_on,
31:         try_cast("transaction_currency" AS VARCHAR) AS transaction_currency,
32:         try_cast("transferred_to_accounting" AS VARCHAR) AS transferred_to_accounting,
33:         try_cast("type" AS VARCHAR) AS type,
34:         try_cast("unapplied_amount" AS DOUBLE) AS unapplied_amount,
35:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
36:         try_cast(updated_date as TIMESTAMP) AS updated_date,
37:         row_number() over (partition by id order by updated_date desc) = 1 AS is_most_recent_record
38: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__payment.sql`；SHA-256 `4bacc3c374a194c0b67e753ccc4bb20dbe41a85fdc01d3ab10436356b424a1ce`。

```text
1: with base as (
2:     select * from raw.zuora_payment_data
3:     where _fivetran_deleted is null or _fivetran_deleted = false
4: ),
5: final as (
6:     select
7:         id as payment_id,
8:         account_id,
9:         accounting_code,
10:         amount,
11:         amount_home_currency,
12:         applied_amount,
13:         applied_credit_balance_amount,
14:         bill_to_contact_id,
15:         try_cast(cancelled_on as TIMESTAMP) as cancelled_on,
16:         comment,
17:         created_by_id,
18:         cast(created_date as TIMESTAMP) as created_date,
19:         currency,
20:         effective_date,
21:         exchange_rate,
22:         exchange_rate_date,
23:         home_currency,
24:         parent_account_id,
25:         payment_method_id,
26:         payment_number,
27:         refund_amount,
28:         try_cast(settled_on as TIMESTAMP) as settled_on,
29:         sold_to_contact_id,
30:         status,
31:         try_cast(submitted_on as TIMESTAMP) as submitted_on,
32:         transaction_currency,
33:         transferred_to_accounting,
34:         type,
35:         unapplied_amount,
36:         updated_by_id,
37:         cast(updated_date as TIMESTAMP) as updated_date,
38:         row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
39:     from base
40: )
41: select * from final
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

- type_applied_credit_balance_amount（O）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_payment_method_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 payment_method_id。
P：本实体id可替代payment_method_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。

- type_refund_amount（O）：**只有通用策略说明**；事件 13、14、39、40、45、69。
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_payment_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_payment_data","id","VARCHAR"],["zuora_payment_data","_fivetran_deleted","VARCHAR"],["zuora_payment_data","_fivetran_synced","VARCHAR"],["zuora_payment_data","account_id","VARCHAR"],["zuora_payment_data","accounting_code","VARCHAR"],["zuora_payment_data","amount","VARCHAR"],["zuora_payment_data","amount_currency_rounding","VARCHAR"],["zuora_payment_data","amount_home_currency","VARCHAR"],["zuora_payment_data","applied_amount","VARCHAR"],["zuora_payment_data","applied_credit_balance_amount","VARCHAR"],["zuora_payment_data","auth_transaction_id","VARCHAR"],["zuora_payment_data","bank_identification_number","VARCHAR"],["zuora_payment_data","bill_to_contact_id","VARCHAR"],["zuora_payment_data","cancelled_on","VARCHAR"],["zuora_payment_data","comment","VARCHAR"],["zuora_payment_data","created_by_id","VARCHAR"],["zuora_payment_data","created_date","VARCHAR"],["zuora_payment_data","currency","VARCHAR"],["zuora_payment_data","default_payment_method_id","VARCHAR"],["zuora_payment_data","effective_date","VARCHAR"],["zuora_payment_data","exchange_rate","VARCHAR"],["zuora_payment_data","exchange_rate_date","VARCHAR"],["zuora_payment_data","gateway","VARCHAR"],["zuora_payment_data","gateway_order_id","VARCHAR"],["zuora_payment_data","gateway_reconciliation_reason","VARCHAR"],["zuora_payment_data","gateway_reconciliation_status","VARCHAR"],["zuora_payment_data","gateway_response","VARCHAR"],["zuora_payment_data","gateway_response_code","VARCHAR"],["zuora_payment_data","gateway_state","VARCHAR"],["zuora_payment_data","home_currency","VARCHAR"],["zuora_payment_data","is_standalone","VARCHAR"],["zuora_payment_data","marked_for_submission_on","VARCHAR"],["zuora_payment_data","parent_account_id","VARCHAR"],["zuora_payment_data","payment_method_id","VARCHAR"],["zuora_payment_data","payment_number","VARCHAR"],["zuora_payment_data","payout_id","VARCHAR"],["zuora_payment_data","provider_exchange_rate_date","VARCHAR"],["zuora_payment_data","reference_id","VARCHAR"],["zuora_payment_data","referenced_payment_id","VARCHAR"],["zuora_payment_data","refund_amount","VARCHAR"],["zuora_payment_data","second_payment_reference_id","VARCHAR"],["zuora_payment_data","settled_on","VARCHAR"],["zuora_payment_data","soft_descriptor","VARCHAR"],["zuora_payment_data","soft_descriptor_phone","VARCHAR"],["zuora_payment_data","sold_to_contact_id","VARCHAR"],["zuora_payment_data","source","VARCHAR"],["zuora_payment_data","source_name","VARCHAR"],["zuora_payment_data","status","VARCHAR"],["zuora_payment_data","submitted_on","VARCHAR"],["zuora_payment_data","transaction_currency","VARCHAR"],["zuora_payment_data","transferred_to_accounting","VARCHAR"],["zuora_payment_data","type","VARCHAR"],["zuora_payment_data","unapplied_amount","VARCHAR"],["zuora_payment_data","updated_by_id","VARCHAR"],["zuora_payment_data","updated_date","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_payment_data UNION ALL SELECT 'payment_method_id' col,count(*) n,count(payment_method_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(payment_method_id as varchar)) same_as_id FROM raw.zuora_payment_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",1503,1503,0],["payment_method_id",1503,1503,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_payment_data s UNION ALL SELECT 'payment_method_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.payment_method_id as varchar))) named_col_matches FROM raw.zuora_payment_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",1503,0,1499],["payment_method_id",1503,0,1499]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_payment_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'payment_method_id' col,count(*) n,count(s.payment_method_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.payment_method_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",722,722,0,718],["payment_method_id",722,722,0,718]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_payment_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'payment_method_id' col,count(*) n,count(payment_method_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(payment_method_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(payment_method_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",722,722,722,0],["payment_method_id",722,722,722,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__payment.json
[024_reruns_impl-030_stg_zuora__payment.json](../024_reruns_impl-030_stg_zuora__payment.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|4337|否|
|L1|722|722|722|2884|否|
|L2|722|722|722|2884|否|
|L3|722|722|722|1448|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount":1,"amount_home_currency":4,"applied_amount":4,"applied_credit_balance_amount":722,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722,"refund_amount":722,"unapplied_amount":4}`
- L1：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L2：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L3：`{"account_id":722,"amount_home_currency":4,"payment_method_id":722}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__payment/baseline.sql`；SHA-256 `813d0dda480cefe9d074047be69cd2a4999c9b1d6b9b8c4568e64f84729340f3`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|4337|否|
|L1|722|722|722|2884|否|
|L2|722|722|722|2884|否|
|L3|722|722|722|1448|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount":1,"amount_home_currency":4,"applied_amount":4,"applied_credit_balance_amount":722,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722,"refund_amount":722,"unapplied_amount":4}`
- L1：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L2：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L3：`{"account_id":722,"amount_home_currency":4,"payment_method_id":722}`

#### source_account_id
主因；类别候选U。P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少722。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第7行、offset 206起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment/source_account_id.sql`；SHA-256 `39b6c8ae8b0ca79e3b6c5fd3903798f07f227519b4f2782ff85ce4aeba6032cd`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|3615|否|
|L1|722|722|722|2162|否|
|L2|722|722|722|2162|否|
|L3|722|722|722|726|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"amount":1,"amount_home_currency":4,"applied_amount":4,"applied_credit_balance_amount":722,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722,"refund_amount":722,"unapplied_amount":4}`
- L1：`{"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L2：`{"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L3：`{"amount_home_currency":4,"payment_method_id":722}`

#### type_amount
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少1。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第9行、offset 322起替换；其他字节相同。
原表达式：
```sql
try_cast("amount" AS DOUBLE) AS amount
```

修改后：
```sql
"amount" AS amount
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment/type_amount.sql`；SHA-256 `6b00fd79a36d4edb6a2b22fa41dff7b56635329272ed7555b2a260c0e0f2275e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|4336|否|
|L1|722|722|722|2884|否|
|L2|722|722|722|2884|否|
|L3|722|722|722|1448|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount_home_currency":4,"applied_amount":4,"applied_credit_balance_amount":722,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722,"refund_amount":722,"unapplied_amount":4}`
- L1：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L2：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L3：`{"account_id":722,"amount_home_currency":4,"payment_method_id":722}`

#### type_amount_home_currency
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少4。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第10行、offset 370起替换；其他字节相同。
原表达式：
```sql
try_cast("amount_home_currency" AS DOUBLE) AS amount_home_currency
```

修改后：
```sql
"amount_home_currency" AS amount_home_currency
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment/type_amount_home_currency.sql`；SHA-256 `a053818857e8692fd6c4242a52ddda2f301430fe9f92c574c6f023ac3de3c9a3`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|4333|否|
|L1|722|722|722|2880|否|
|L2|722|722|722|2880|否|
|L3|722|722|722|1444|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount":1,"applied_amount":4,"applied_credit_balance_amount":722,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722,"refund_amount":722,"unapplied_amount":4}`
- L1：`{"account_id":722,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L2：`{"account_id":722,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L3：`{"account_id":722,"payment_method_id":722}`

#### type_applied_amount
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少4。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 446起替换；其他字节相同。
原表达式：
```sql
try_cast("applied_amount" AS DOUBLE) AS applied_amount
```

修改后：
```sql
"applied_amount" AS applied_amount
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment/type_applied_amount.sql`；SHA-256 `2afc2b50a7be6c717b4b037772a873e9dffaa4caa18022ac0607120cb5c6f7fe`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|4333|否|
|L1|722|722|722|2884|否|
|L2|722|722|722|2884|否|
|L3|722|722|722|1448|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount":1,"amount_home_currency":4,"applied_credit_balance_amount":722,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722,"refund_amount":722,"unapplied_amount":4}`
- L1：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L2：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L3：`{"account_id":722,"amount_home_currency":4,"payment_method_id":722}`

#### type_applied_credit_balance_amount
主因；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少722。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第12行、offset 510起替换；其他字节相同。
原表达式：
```sql
try_cast("applied_credit_balance_amount" AS DOUBLE) AS applied_credit_balance_amount
```

修改后：
```sql
"applied_credit_balance_amount" AS applied_credit_balance_amount
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment/type_applied_credit_balance_amount.sql`；SHA-256 `d8535e7423e123c722a4b2629dca9040fa9ee44f8b761eefc5dd1a4430b9dac7`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|3615|否|
|L1|722|722|722|2884|否|
|L2|722|722|722|2884|否|
|L3|722|722|722|1448|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount":1,"amount_home_currency":4,"applied_amount":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722,"refund_amount":722,"unapplied_amount":4}`
- L1：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L2：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L3：`{"account_id":722,"amount_home_currency":4,"payment_method_id":722}`

#### type_effective_date
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少718。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第19行、offset 966起替换；其他字节相同。
原表达式：
```sql
try_cast("effective_date" AS DATE) AS effective_date
```

修改后：
```sql
"effective_date" AS effective_date
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment/type_effective_date.sql`；SHA-256 `e6b09da44ff62fa217d86ebb90794c3702c46c34a154cece88db215dfab3ff16`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|3619|否|
|L1|722|722|722|2166|否|
|L2|722|722|722|2166|否|
|L3|722|722|722|1448|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount":1,"amount_home_currency":4,"applied_amount":4,"applied_credit_balance_amount":722,"exchange_rate_date":718,"payment_method_id":722,"refund_amount":722,"unapplied_amount":4}`
- L1：`{"account_id":722,"amount_home_currency":4,"exchange_rate_date":718,"payment_method_id":722}`
- L2：`{"account_id":722,"amount_home_currency":4,"exchange_rate_date":718,"payment_method_id":722}`
- L3：`{"account_id":722,"amount_home_currency":4,"payment_method_id":722}`

#### type_exchange_rate_date
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少718。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第21行、offset 1091起替换；其他字节相同。
原表达式：
```sql
try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date
```

修改后：
```sql
"exchange_rate_date" AS exchange_rate_date
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment/type_exchange_rate_date.sql`；SHA-256 `88f3ea9b03182e5652930fbb98a66e4d217a45eb243083d69cabdbbac5225a31`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|3619|否|
|L1|722|722|722|2166|否|
|L2|722|722|722|2166|否|
|L3|722|722|722|1448|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount":1,"amount_home_currency":4,"applied_amount":4,"applied_credit_balance_amount":722,"effective_date":718,"payment_method_id":722,"refund_amount":722,"unapplied_amount":4}`
- L1：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"payment_method_id":722}`
- L2：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"payment_method_id":722}`
- L3：`{"account_id":722,"amount_home_currency":4,"payment_method_id":722}`

#### source_payment_method_id
主因；类别候选U。P：本实体id可替代payment_method_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少722。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第24行、offset 1295起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS payment_method_id
```

修改后：
```sql
try_cast("payment_method_id" AS VARCHAR) AS payment_method_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment/source_payment_method_id.sql`；SHA-256 `3a28d1f058923e6f19cb89bb49bed2a6445a2bc19c57548032d6effadadb5d6b`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|3615|否|
|L1|722|722|722|2162|否|
|L2|722|722|722|2162|否|
|L3|722|722|722|726|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount":1,"amount_home_currency":4,"applied_amount":4,"applied_credit_balance_amount":722,"effective_date":718,"exchange_rate_date":718,"refund_amount":722,"unapplied_amount":4}`
- L1：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718}`
- L2：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718}`
- L3：`{"account_id":722,"amount_home_currency":4}`

#### type_refund_amount
主因；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少722。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第26行、offset 1416起替换；其他字节相同。
原表达式：
```sql
try_cast("refund_amount" AS DOUBLE) AS refund_amount
```

修改后：
```sql
"refund_amount" AS refund_amount
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment/type_refund_amount.sql`；SHA-256 `b03e1a958be432d72930d828295545de68415412046f1c07fdfb212ef0a25560`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|3615|否|
|L1|722|722|722|2884|否|
|L2|722|722|722|2884|否|
|L3|722|722|722|1448|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount":1,"amount_home_currency":4,"applied_amount":4,"applied_credit_balance_amount":722,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722,"unapplied_amount":4}`
- L1：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L2：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L3：`{"account_id":722,"amount_home_currency":4,"payment_method_id":722}`

#### type_unapplied_amount
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少4。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第34行、offset 1927起替换；其他字节相同。
原表达式：
```sql
try_cast("unapplied_amount" AS DOUBLE) AS unapplied_amount
```

修改后：
```sql
"unapplied_amount" AS unapplied_amount
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment/type_unapplied_amount.sql`；SHA-256 `7cec0b91e0c3fac15fcee50c7ef91df8bc387c7904ad56fc6acfd9e9c6daeefc`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|722|722|722|4333|否|
|L1|722|722|722|2884|否|
|L2|722|722|722|2884|否|
|L3|722|722|722|1448|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":722,"amount":1,"amount_home_currency":4,"applied_amount":4,"applied_credit_balance_amount":722,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722,"refund_amount":722}`
- L1：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L2：`{"account_id":722,"amount_home_currency":4,"effective_date":718,"exchange_rate_date":718,"payment_method_id":722}`
- L3：`{"account_id":722,"amount_home_currency":4,"payment_method_id":722}`
## 规则问题

无。

