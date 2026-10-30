# impl-030 · stg_zuora__payment_method

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**U**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：无。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__payment_method.md](../024_packages/024_impl-030_stg_zuora__payment_method.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
526:     - name: stg_zuora__payment_method
527:       description: "Cleaned payment methods with status and last transaction metadata; latest snapshot indicator."
528:       source_table: raw.zuora_payment_method_data
529:       columns:
530:         - name: payment_method_id
531:           data_type: VARCHAR
532:           source_expression: "id"
533:         - name: account_id
534:           data_type: VARCHAR
535:         - name: ach_account_type
536:           data_type: VARCHAR
537:         - name: active
538:           data_type: BOOLEAN
539:         - name: bank_transfer_account_type
540:           data_type: VARCHAR
541:         - name: created_by_id
542:           data_type: VARCHAR
543:         - name: created_date
544:           data_type: TIMESTAMP
545:           source_expression: "cast(created_date as TIMESTAMP)"
546:         - name: credit_card_type
547:           data_type: VARCHAR
548:         - name: last_failed_sale_transaction_date
549:           data_type: TIMESTAMP
550:           source_expression: "cast(last_failed_sale_transaction_date as TIMESTAMP)"
551:         - name: last_transaction_date_time
552:           data_type: TIMESTAMP
553:           source_expression: "cast(last_transaction_date_time as TIMESTAMP)"
554:         - name: last_transaction_status
555:           data_type: VARCHAR
556:         - name: max_consecutive_payment_failures
557:           data_type: BIGINT
558:         - name: payment_method_name
559:           data_type: VARCHAR
560:           source_expression: "_name"
561:         - name: num_consecutive_failures
562:           data_type: BIGINT
563:         - name: payment_method_status
564:           data_type: VARCHAR
565:         - name: paypal_type
566:           data_type: VARCHAR
567:         - name: sub_type
568:           data_type: VARCHAR
569:         - name: total_number_of_error_payments
570:           data_type: BIGINT
571:         - name: total_number_of_processed_payments
572:           data_type: BIGINT
573:         - name: payment_method_type
574:           data_type: VARCHAR
575:           source_expression: "_type"
576:         - name: updated_by_id
577:           data_type: VARCHAR
578:         - name: updated_date
579:           data_type: TIMESTAMP
580:           source_expression: "cast(updated_date as TIMESTAMP)"
581:         - name: is_most_recent_record
582:           data_type: BOOLEAN
583:           source_expression: "row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1"
584:       row_filters:
585:         - rule: "coalesce(lower(cast(\"_fivetran_deleted\" as varchar)),'false') = 'false'"
586:           on_failure: delete_row
587:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__payment_method.sql`；SHA-256 `3fcb9b00e60172fd9440e96d81515c91f78a802cc75cc86d30844a6252033d33`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_payment_method_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS payment_method_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("ach_account_type" AS VARCHAR) AS ach_account_type,
9:         try_cast("active" AS BOOLEAN) AS active,
10:         try_cast("bank_transfer_account_type" AS VARCHAR) AS bank_transfer_account_type,
11:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
12:         try_cast(created_date as TIMESTAMP) AS created_date,
13:         try_cast("credit_card_type" AS VARCHAR) AS credit_card_type,
14:         try_cast(last_failed_sale_transaction_date as TIMESTAMP) AS last_failed_sale_transaction_date,
15:         try_cast(last_transaction_date_time as TIMESTAMP) AS last_transaction_date_time,
16:         try_cast("last_transaction_status" AS VARCHAR) AS last_transaction_status,
17:         try_cast("max_consecutive_payment_failures" AS BIGINT) AS max_consecutive_payment_failures,
18:         _name AS payment_method_name,
19:         try_cast("num_consecutive_failures" AS BIGINT) AS num_consecutive_failures,
20:         try_cast("payment_method_status" AS VARCHAR) AS payment_method_status,
21:         try_cast("paypal_type" AS VARCHAR) AS paypal_type,
22:         try_cast("sub_type" AS VARCHAR) AS sub_type,
23:         try_cast("total_number_of_error_payments" AS BIGINT) AS total_number_of_error_payments,
24:         try_cast("total_number_of_processed_payments" AS BIGINT) AS total_number_of_processed_payments,
25:         _type AS payment_method_type,
26:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
27:         try_cast(updated_date as TIMESTAMP) AS updated_date,
28:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 AS is_most_recent_record
29: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__payment_method.sql`；SHA-256 `e8a820b866e6051cc0c0dc8795ac44801c158f7e9774ea6ff7dee3fc23813320`。

```text
1: with base as (
2:     select * from raw.zuora_payment_method_data p
3:     where coalesce(lower(cast(p."_fivetran_deleted" as varchar)),'false') = 'false'
4: ),
5: final as (
6:     select
7:         id as payment_method_id,
8:         account_id,
9:         ach_account_type,
10:         active,
11:         bank_transfer_account_type,
12:         created_by_id,
13:         cast(created_date as TIMESTAMP) as created_date,
14:         credit_card_type,
15:         cast(last_failed_sale_transaction_date as TIMESTAMP) as last_failed_sale_transaction_date,
16:         cast(last_transaction_date_time as TIMESTAMP) as last_transaction_date_time,
17:         last_transaction_status,
18:         max_consecutive_payment_failures,
19:         _name as payment_method_name,
20:         num_consecutive_failures,
21:         payment_method_status,
22:         paypal_type,
23:         sub_type,
24:         total_number_of_error_payments,
25:         total_number_of_processed_payments,
26:         _type as payment_method_type,
27:         updated_by_id,
28:         cast(updated_date as TIMESTAMP) as updated_date,
29:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 as is_most_recent_record
30:     from base
31: )
32: select * from final
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_payment_method_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_payment_method_data","id","VARCHAR"],["zuora_payment_method_data","_fivetran_deleted","VARCHAR"],["zuora_payment_method_data","_fivetran_synced","VARCHAR"],["zuora_payment_method_data","account_id","VARCHAR"],["zuora_payment_method_data","ach_aba_code","VARCHAR"],["zuora_payment_method_data","ach_account_name","VARCHAR"],["zuora_payment_method_data","ach_account_number_mask","VARCHAR"],["zuora_payment_method_data","ach_account_type","VARCHAR"],["zuora_payment_method_data","ach_address_1","VARCHAR"],["zuora_payment_method_data","ach_address_2","VARCHAR"],["zuora_payment_method_data","ach_bank_name","VARCHAR"],["zuora_payment_method_data","ach_city","VARCHAR"],["zuora_payment_method_data","ach_country","VARCHAR"],["zuora_payment_method_data","ach_postal_code","VARCHAR"],["zuora_payment_method_data","ach_state","VARCHAR"],["zuora_payment_method_data","active","VARCHAR"],["zuora_payment_method_data","bank_branch_code","VARCHAR"],["zuora_payment_method_data","bank_check_digit","VARCHAR"],["zuora_payment_method_data","bank_city","VARCHAR"],["zuora_payment_method_data","bank_code","VARCHAR"],["zuora_payment_method_data","bank_identification_number","VARCHAR"],["zuora_payment_method_data","bank_name","VARCHAR"],["zuora_payment_method_data","bank_postal_code","VARCHAR"],["zuora_payment_method_data","bank_street_name","VARCHAR"],["zuora_payment_method_data","bank_street_number","VARCHAR"],["zuora_payment_method_data","bank_transfer_account_name","VARCHAR"],["zuora_payment_method_data","bank_transfer_account_number_mask","VARCHAR"],["zuora_payment_method_data","bank_transfer_account_type","VARCHAR"],["zuora_payment_method_data","bank_transfer_type","VARCHAR"],["zuora_payment_method_data","business_identification_code","VARCHAR"],["zuora_payment_method_data","city","VARCHAR"],["zuora_payment_method_data","company_name","VARCHAR"],["zuora_payment_method_data","country","VARCHAR"],["zuora_payment_method_data","created_by_id","VARCHAR"],["zuora_payment_method_data","created_date","VARCHAR"],["zuora_payment_method_data","credit_card_address_1","VARCHAR"],["zuora_payment_method_data","credit_card_address_2","VARCHAR"],["zuora_payment_method_data","credit_card_city","VARCHAR"],["zuora_payment_method_data","credit_card_country","VARCHAR"],["zuora_payment_method_data","credit_card_expiration_month","VARCHAR"],["zuora_payment_method_data","credit_card_expiration_year","VARCHAR"],["zuora_payment_method_data","credit_card_holder_name","VARCHAR"],["zuora_payment_method_data","credit_card_mask_number","VARCHAR"],["zuora_payment_method_data","credit_card_postal_code","VARCHAR"],["zuora_payment_method_data","credit_card_state","VARCHAR"],["zuora_payment_method_data","credit_card_type","VARCHAR"],["zuora_payment_method_data","device_session_id","VARCHAR"],["zuora_payment_method_data","email","VARCHAR"],["zuora_payment_method_data","existing_mandate","VARCHAR"],["zuora_payment_method_data","first_name","VARCHAR"],["zuora_payment_method_data","iban","VARCHAR"],["zuora_payment_method_data","identity_number","VARCHAR"],["zuora_payment_method_data","ipaddress","VARCHAR"],["zuora_payment_method_data","is_company","VARCHAR"],["zuora_payment_method_data","last_failed_sale_transaction_date","VARCHAR"],["zuora_payment_method_data","last_name","VARCHAR"],["zuora_payment_method_data","last_transaction_date_time","VARCHAR"],["zuora_payment_method_data","last_transaction_status","VARCHAR"],["zuora_payment_method_data","mandate_creation_date","VARCHAR"],["zuora_payment_method_data","mandate_id","VARCHAR"],["zuora_payment_method_data","mandate_reason","VARCHAR"],["zuora_payment_method_data","mandate_received","VARCHAR"],["zuora_payment_method_data","mandate_status","VARCHAR"],["zuora_payment_method_data","mandate_update_date","VARCHAR"],["zuora_payment_method_data","max_consecutive_payment_failures","VARCHAR"],["zuora_payment_method_data","method_reference_id","VARCHAR"],["zuora_payment_method_data","method_specific_data","VARCHAR"],["zuora_payment_method_data","_name","VARCHAR"],["zuora_payment_method_data","num_consecutive_failures","VARCHAR"],["zuora_payment_method_data","payment_method_status","VARCHAR"],["zuora_payment_method_data","payment_retry_window","VARCHAR"],["zuora_payment_method_data","paypal_baid","VARCHAR"],["zuora_payment_method_data","paypal_email","VARCHAR"],["zuora_payment_method_data","paypal_preapproval_key","VARCHAR"],["zuora_payment_method_data","paypal_type","VARCHAR"],["zuora_payment_method_data","phone","VARCHAR"],["zuora_payment_method_data","postal_code","VARCHAR"],["zuora_payment_method_data","second_token_id","VARCHAR"],["zuora_payment_method_data","state","VARCHAR"],["zuora_payment_method_data","street_name","VARCHAR"],["zuora_payment_method_data","street_number","VARCHAR"],["zuora_payment_method_data","sub_type","VARCHAR"],["zuora_payment_method_data","token_id","VARCHAR"],["zuora_payment_method_data","total_number_of_error_payments","VARCHAR"],["zuora_payment_method_data","total_number_of_processed_payments","VARCHAR"],["zuora_payment_method_data","_type","VARCHAR"],["zuora_payment_method_data","updated_by_id","VARCHAR"],["zuora_payment_method_data","updated_date","VARCHAR"],["zuora_payment_method_data","use_default_retry_rule","VARCHAR"],["zuora_payment_method_data","user_reference_id","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_payment_method_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",2008,2001,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_payment_method_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",2008,0,2001]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_payment_method_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",1037,1030,0,1030]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_payment_method_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",1037,1030,1030,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__payment_method.json
[024_reruns_impl-030_stg_zuora__payment_method.json](../024_reruns_impl-030_stg_zuora__payment_method.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1037|1037|1037|1037|否|
|L1|1037|1037|1037|1037|否|
|L2|1037|1037|1037|1037|否|
|L3|1037|1037|1037|1037|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1037}`
- L1：`{"account_id":1037}`
- L2：`{"account_id":1037}`
- L3：`{"account_id":1037}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__payment_method/baseline.sql`；SHA-256 `3fcb9b00e60172fd9440e96d81515c91f78a802cc75cc86d30844a6252033d33`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1037|1037|1037|1037|否|
|L1|1037|1037|1037|1037|否|
|L2|1037|1037|1037|1037|否|
|L3|1037|1037|1037|1037|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1037}`
- L1：`{"account_id":1037}`
- L2：`{"account_id":1037}`
- L3：`{"account_id":1037}`

#### source_account_id
主因；类别候选U。P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少1037，格减少1037。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第7行、offset 220起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__payment_method/source_account_id.sql`；SHA-256 `7131b6afe6f9c1ffa3a1b949d651c5dda245a2c0c7c3bf24086c5b578e1bbc5e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1037|1037|0|0|是|
|L1|1037|1037|0|0|是|
|L2|1037|1037|0|0|是|
|L3|1037|1037|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

