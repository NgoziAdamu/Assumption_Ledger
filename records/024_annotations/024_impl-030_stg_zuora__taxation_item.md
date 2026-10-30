# impl-030 · stg_zuora__taxation_item

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**多因并列（A、O、U）**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：O：type_balance（行减0，格减529）；O：type_credit_amount（行减0，格减5）；O：type_payment_amount（行减0，格减5）；O：type_tax_rate（行减0，格减5）。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__taxation_item.md](../024_packages/024_impl-030_stg_zuora__taxation_item.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
956:     - name: stg_zuora__taxation_item
957:       description: "Cleaned taxation items with safe casting and monetary normalization; latest snapshot indicator."
958:       source_table: raw.zuora_taxation_item_data
959:       columns:
960:         - name: taxation_item_id
961:           data_type: VARCHAR
962:           source_expression: "id"
963:         - name: account_id
964:           data_type: VARCHAR
965:         - name: account_receivable_accounting_code_id
966:           data_type: VARCHAR
967:         - name: accounting_code
968:           data_type: VARCHAR
969:         - name: amendment_id
970:           data_type: VARCHAR
971:         - name: balance
972:           data_type: BIGINT
973:         - name: bill_to_contact_id
974:           data_type: VARCHAR
975:         - name: created_by_id
976:           data_type: VARCHAR
977:         - name: created_date
978:           data_type: TIMESTAMP
979:           source_expression: "try_cast(created_date as TIMESTAMP)"
980:         - name: credit_amount
981:           data_type: DOUBLE
982:         - name: exchange_rate
983:           data_type: VARCHAR
984:         - name: exchange_rate_date
985:           data_type: TIMESTAMP
986:           source_expression: "try_cast(exchange_rate_date as TIMESTAMP)"
987:         - name: exempt_amount
988:           data_type: DOUBLE
989:         - name: exempt_amount_home_currency
990:           data_type: VARCHAR
991:         - name: home_currency
992:           data_type: VARCHAR
993:         - name: invoice_id
994:           data_type: VARCHAR
995:         - name: invoice_item_id
996:           data_type: VARCHAR
997:         - name: journal_entry_id
998:           data_type: VARCHAR
999:         - name: name
1000:           data_type: VARCHAR
1001:         - name: payment_amount
1002:           data_type: DOUBLE
1003:         - name: product_id
1004:           data_type: VARCHAR
1005:         - name: product_rate_plan_charge_id
1006:           data_type: VARCHAR
1007:         - name: product_rate_plan_id
1008:           data_type: VARCHAR
1009:         - name: rate_plan_charge_id
1010:           data_type: VARCHAR
1011:         - name: rate_plan_id
1012:           data_type: VARCHAR
1013:         - name: sales_tax_payable_accounting_code_id
1014:           data_type: VARCHAR
1015:         - name: sold_to_contact_id
1016:           data_type: VARCHAR
1017:         - name: subscription_id
1018:           data_type: VARCHAR
1019:         - name: tax_amount
1020:           data_type: BIGINT
1021:         - name: tax_amount_home_currency
1022:           data_type: DOUBLE
1023:           source_expression: "case when nullif(tax_amount_home_currency,'') is null then null else cast(tax_amount_home_currency as double) end"
1024:         - name: tax_date
1025:           data_type: TIMESTAMP
1026:           source_expression: "try_cast(tax_date as TIMESTAMP)"
1027:         - name: tax_description
1028:           data_type: VARCHAR
1029:         - name: tax_mode
1030:           data_type: VARCHAR
1031:         - name: tax_rate
1032:           data_type: DOUBLE
1033:         - name: tax_rate_type
1034:           data_type: VARCHAR
1035:         - name: transaction_currency
1036:           data_type: VARCHAR
1037:         - name: updated_by_id
1038:           data_type: VARCHAR
1039:         - name: updated_date
1040:           data_type: TIMESTAMP
1041:           source_expression: "cast(updated_date as TIMESTAMP)"
1042:         - name: is_most_recent_record
1043:           data_type: BOOLEAN
1044:           source_expression: "row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1"
1045:       row_filters:
1046:         - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
1047:           on_failure: delete_row
1048:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__taxation_item.sql`；SHA-256 `57b246d14cc8c4a8f8e82da16556cfb40a96b7a916f6cdbec7d7a76302dd2eb7`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_taxation_item_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS taxation_item_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("account_receivable_accounting_code_id" AS VARCHAR) AS account_receivable_accounting_code_id,
9:         try_cast("accounting_code" AS VARCHAR) AS accounting_code,
10:         try_cast("id" AS VARCHAR) AS amendment_id,
11:         try_cast("balance" AS BIGINT) AS balance,
12:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
13:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
14:         try_cast(created_date as TIMESTAMP) AS created_date,
15:         try_cast("credit_amount" AS DOUBLE) AS credit_amount,
16:         try_cast("exchange_rate" AS VARCHAR) AS exchange_rate,
17:         try_cast(exchange_rate_date as TIMESTAMP) AS exchange_rate_date,
18:         try_cast("exempt_amount" AS DOUBLE) AS exempt_amount,
19:         try_cast("exempt_amount_home_currency" AS VARCHAR) AS exempt_amount_home_currency,
20:         try_cast("home_currency" AS VARCHAR) AS home_currency,
21:         try_cast("id" AS VARCHAR) AS invoice_id,
22:         try_cast("id" AS VARCHAR) AS invoice_item_id,
23:         try_cast("journal_entry_id" AS VARCHAR) AS journal_entry_id,
24:         try_cast("name" AS VARCHAR) AS name,
25:         try_cast("payment_amount" AS DOUBLE) AS payment_amount,
26:         try_cast("id" AS VARCHAR) AS product_id,
27:         try_cast("product_rate_plan_charge_id" AS VARCHAR) AS product_rate_plan_charge_id,
28:         try_cast("id" AS VARCHAR) AS product_rate_plan_id,
29:         try_cast("id" AS VARCHAR) AS rate_plan_charge_id,
30:         try_cast("id" AS VARCHAR) AS rate_plan_id,
31:         try_cast("sales_tax_payable_accounting_code_id" AS VARCHAR) AS sales_tax_payable_accounting_code_id,
32:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
33:         try_cast("id" AS VARCHAR) AS subscription_id,
34:         try_cast("tax_amount" AS BIGINT) AS tax_amount,
35:         try_cast(nullif(tax_amount_home_currency, '') AS DOUBLE) AS tax_amount_home_currency,
36:         try_cast(tax_date as TIMESTAMP) AS tax_date,
37:         try_cast("tax_description" AS VARCHAR) AS tax_description,
38:         try_cast("tax_mode" AS VARCHAR) AS tax_mode,
39:         try_cast("tax_rate" AS DOUBLE) AS tax_rate,
40:         try_cast("tax_rate_type" AS VARCHAR) AS tax_rate_type,
41:         try_cast("transaction_currency" AS VARCHAR) AS transaction_currency,
42:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
43:         try_cast(updated_date as TIMESTAMP) AS updated_date,
44:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 AS is_most_recent_record
45: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__taxation_item.sql`；SHA-256 `4dbb6d30e5eb9a5e020a26f8118b5cbe51520798bb73b3eb5837736803553219`。

```text
1: with base as (
2:     select * from raw.zuora_taxation_item_data where _fivetran_deleted is null or _fivetran_deleted = false
3: ),
4: final as (
5:     select
6:         id as taxation_item_id,
7:         account_id,
8:         account_receivable_accounting_code_id,
9:         accounting_code,
10:         amendment_id,
11:         balance,
12:         bill_to_contact_id,
13:         created_by_id,
14:         try_cast(created_date as TIMESTAMP) as created_date,
15:         credit_amount,
16:         exchange_rate,
17:         try_cast(exchange_rate_date as TIMESTAMP) as exchange_rate_date,
18:         exempt_amount,
19:         exempt_amount_home_currency,
20:         home_currency,
21:         invoice_id,
22:         invoice_item_id,
23:         journal_entry_id,
24:         name,
25:         payment_amount,
26:         product_id,
27:         product_rate_plan_charge_id,
28:         product_rate_plan_id,
29:         rate_plan_charge_id,
30:         rate_plan_id,
31:         sales_tax_payable_accounting_code_id,
32:         sold_to_contact_id,
33:         subscription_id,
34:         tax_amount,
35:         case when nullif(tax_amount_home_currency,'') is null then null else cast(tax_amount_home_currency as double) end as tax_amount_home_currency,
36:         try_cast(tax_date as TIMESTAMP) as tax_date,
37:         tax_description,
38:         tax_mode,
39:         tax_rate,
40:         tax_rate_type,
41:         transaction_currency,
42:         updated_by_id,
43:         cast(updated_date as TIMESTAMP) as updated_date,
44:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 as is_most_recent_record
45:     from base
46: )
47: select * from final
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


- type_exempt_amount（O）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_invoice_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_invoice_item_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_product_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 product_id。
P：本实体id可替代product_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。

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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_taxation_item_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_taxation_item_data","id","VARCHAR"],["zuora_taxation_item_data","_fivetran_deleted","VARCHAR"],["zuora_taxation_item_data","_fivetran_synced","VARCHAR"],["zuora_taxation_item_data","account_id","VARCHAR"],["zuora_taxation_item_data","account_receivable_accounting_code_id","VARCHAR"],["zuora_taxation_item_data","accounting_code","VARCHAR"],["zuora_taxation_item_data","accounting_period_id","VARCHAR"],["zuora_taxation_item_data","amendment_id","VARCHAR"],["zuora_taxation_item_data","balance","VARCHAR"],["zuora_taxation_item_data","bill_to_contact_id","VARCHAR"],["zuora_taxation_item_data","created_by_id","VARCHAR"],["zuora_taxation_item_data","created_date","VARCHAR"],["zuora_taxation_item_data","credit_amount","VARCHAR"],["zuora_taxation_item_data","default_payment_method_id","VARCHAR"],["zuora_taxation_item_data","exchange_rate","VARCHAR"],["zuora_taxation_item_data","exchange_rate_date","VARCHAR"],["zuora_taxation_item_data","exempt_amount","VARCHAR"],["zuora_taxation_item_data","exempt_amount_currency_rounding","VARCHAR"],["zuora_taxation_item_data","exempt_amount_home_currency","VARCHAR"],["zuora_taxation_item_data","home_currency","VARCHAR"],["zuora_taxation_item_data","invoice_id","VARCHAR"],["zuora_taxation_item_data","invoice_item_id","VARCHAR"],["zuora_taxation_item_data","journal_entry_id","VARCHAR"],["zuora_taxation_item_data","journal_run_id","VARCHAR"],["zuora_taxation_item_data","jurisdiction","VARCHAR"],["zuora_taxation_item_data","location_code","VARCHAR"],["zuora_taxation_item_data","name","VARCHAR"],["zuora_taxation_item_data","payment_amount","VARCHAR"],["zuora_taxation_item_data","product_id","VARCHAR"],["zuora_taxation_item_data","product_rate_plan_charge_id","VARCHAR"],["zuora_taxation_item_data","product_rate_plan_id","VARCHAR"],["zuora_taxation_item_data","provider_exchange_rate_date","VARCHAR"],["zuora_taxation_item_data","rate_plan_charge_id","VARCHAR"],["zuora_taxation_item_data","rate_plan_id","VARCHAR"],["zuora_taxation_item_data","sales_tax_payable_accounting_code_id","VARCHAR"],["zuora_taxation_item_data","sold_to_contact_id","VARCHAR"],["zuora_taxation_item_data","subscription_id","VARCHAR"],["zuora_taxation_item_data","tax_amount","VARCHAR"],["zuora_taxation_item_data","tax_amount_currency_rounding","VARCHAR"],["zuora_taxation_item_data","tax_amount_home_currency","VARCHAR"],["zuora_taxation_item_data","tax_code","VARCHAR"],["zuora_taxation_item_data","tax_code_description","VARCHAR"],["zuora_taxation_item_data","tax_date","VARCHAR"],["zuora_taxation_item_data","tax_mode","VARCHAR"],["zuora_taxation_item_data","tax_rate","VARCHAR"],["zuora_taxation_item_data","tax_rate_description","VARCHAR"],["zuora_taxation_item_data","tax_rate_type","VARCHAR"],["zuora_taxation_item_data","transaction_currency","VARCHAR"],["zuora_taxation_item_data","updated_by_id","VARCHAR"],["zuora_taxation_item_data","updated_date","VARCHAR"],["zuora_taxation_item_data","parent_account_id","VARCHAR"],["zuora_taxation_item_data","seller_registration","VARCHAR"],["zuora_taxation_item_data","tax_description","VARCHAR"],["zuora_taxation_item_data","customer_code","VARCHAR"],["zuora_taxation_item_data","tax_rule_id","VARCHAR"],["zuora_taxation_item_data","exempt_certificate","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_taxation_item_data UNION ALL SELECT 'amendment_id' col,count(*) n,count(amendment_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(amendment_id as varchar)) same_as_id FROM raw.zuora_taxation_item_data UNION ALL SELECT 'invoice_id' col,count(*) n,count(invoice_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(invoice_id as varchar)) same_as_id FROM raw.zuora_taxation_item_data UNION ALL SELECT 'invoice_item_id' col,count(*) n,count(invoice_item_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(invoice_item_id as varchar)) same_as_id FROM raw.zuora_taxation_item_data UNION ALL SELECT 'product_id' col,count(*) n,count(product_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(product_id as varchar)) same_as_id FROM raw.zuora_taxation_item_data UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(product_rate_plan_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(product_rate_plan_id as varchar)) same_as_id FROM raw.zuora_taxation_item_data UNION ALL SELECT 'rate_plan_charge_id' col,count(*) n,count(rate_plan_charge_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(rate_plan_charge_id as varchar)) same_as_id FROM raw.zuora_taxation_item_data UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(rate_plan_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(rate_plan_id as varchar)) same_as_id FROM raw.zuora_taxation_item_data UNION ALL SELECT 'subscription_id' col,count(*) n,count(subscription_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(subscription_id as varchar)) same_as_id FROM raw.zuora_taxation_item_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",1005,1005,0],["amendment_id",1005,1005,0],["invoice_id",1005,1005,0],["invoice_item_id",1005,1005,0],["product_id",1005,6,0],["product_rate_plan_id",1005,6,0],["rate_plan_charge_id",1005,6,0],["rate_plan_id",1005,6,0],["subscription_id",1005,6,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_taxation_item_data s UNION ALL SELECT 'amendment_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.amendment_id as varchar))) named_col_matches FROM raw.zuora_taxation_item_data s UNION ALL SELECT 'invoice_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.invoice_id as varchar))) named_col_matches FROM raw.zuora_taxation_item_data s UNION ALL SELECT 'invoice_item_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_item_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_item_data t WHERE cast(t.id as varchar)=cast(s.invoice_item_id as varchar))) named_col_matches FROM raw.zuora_taxation_item_data s UNION ALL SELECT 'product_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.product_id as varchar))) named_col_matches FROM raw.zuora_taxation_item_data s UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.product_rate_plan_id as varchar))) named_col_matches FROM raw.zuora_taxation_item_data s UNION ALL SELECT 'rate_plan_charge_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_charge_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_charge_data t WHERE cast(t.id as varchar)=cast(s.rate_plan_charge_id as varchar))) named_col_matches FROM raw.zuora_taxation_item_data s UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.rate_plan_id as varchar))) named_col_matches FROM raw.zuora_taxation_item_data s UNION ALL SELECT 'subscription_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.subscription_id as varchar))) named_col_matches FROM raw.zuora_taxation_item_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",1005,0,0],["amendment_id",1005,0,0],["invoice_id",1005,0,0],["invoice_item_id",1005,0,2],["product_id",1005,0,5],["product_rate_plan_id",1005,0,0],["rate_plan_charge_id",1005,0,0],["rate_plan_id",1005,0,0],["subscription_id",1005,0,0]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_taxation_item_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'amendment_id' col,count(*) n,count(s.amendment_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.amendment_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'invoice_id' col,count(*) n,count(s.invoice_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.invoice_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'invoice_item_id' col,count(*) n,count(s.invoice_item_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_item_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_item_data t WHERE cast(t.id as varchar)=cast(s.invoice_item_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'product_id' col,count(*) n,count(s.product_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.product_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(s.product_rate_plan_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.product_rate_plan_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'rate_plan_charge_id' col,count(*) n,count(s.rate_plan_charge_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_charge_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_charge_data t WHERE cast(t.id as varchar)=cast(s.rate_plan_charge_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(s.rate_plan_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.rate_plan_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'subscription_id' col,count(*) n,count(s.subscription_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.subscription_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",534,534,0,0],["amendment_id",534,534,0,0],["invoice_id",534,534,0,0],["invoice_item_id",534,534,0,2],["product_id",534,5,0,5],["product_rate_plan_id",534,5,0,0],["rate_plan_charge_id",534,5,0,0],["rate_plan_id",534,5,0,0],["subscription_id",534,5,0,0]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_taxation_item_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'amendment_id' col,count(*) n,count(amendment_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(amendment_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(amendment_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'invoice_id' col,count(*) n,count(invoice_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(invoice_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(invoice_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'invoice_item_id' col,count(*) n,count(invoice_item_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(invoice_item_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(invoice_item_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'product_id' col,count(*) n,count(product_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(product_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(product_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(product_rate_plan_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(product_rate_plan_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(product_rate_plan_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'rate_plan_charge_id' col,count(*) n,count(rate_plan_charge_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(rate_plan_charge_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(rate_plan_charge_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(rate_plan_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(rate_plan_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(rate_plan_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'subscription_id' col,count(*) n,count(subscription_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(subscription_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(subscription_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",534,534,5,0],["amendment_id",534,534,529,0],["invoice_id",534,534,534,0],["invoice_item_id",534,534,5,529],["product_id",534,5,5,0],["product_rate_plan_id",534,5,5,0],["rate_plan_charge_id",534,5,5,0],["rate_plan_id",534,5,5,0],["subscription_id",534,5,5,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__taxation_item.json
[024_reruns_impl-030_stg_zuora__taxation_item.json](../024_reruns_impl-030_stg_zuora__taxation_item.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5884|否|
|L1|534|534|534|5864|否|
|L2|534|534|534|5864|否|
|L3|534|534|534|5864|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/baseline.sql`；SHA-256 `57b246d14cc8c4a8f8e82da16556cfb40a96b7a916f6cdbec7d7a76302dd2eb7`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5884|否|
|L1|534|534|534|5864|否|
|L2|534|534|534|5864|否|
|L3|534|534|534|5864|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### source_account_id
主因；类别候选A。把本实体 id 当作 account_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少534。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第7行、offset 218起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/source_account_id.sql`；SHA-256 `e8b133dcddb9ad298081386168ce0270ac84928fc95f7bf8a0d2f4a7c2fddbed`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5350|否|
|L1|534|534|534|5330|否|
|L2|534|534|534|5330|否|
|L3|534|534|534|5330|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### source_amendment_id
主因；类别候选A。把本实体 id 当作 amendment_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少534。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第10行、offset 445起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS amendment_id
```

修改后：
```sql
try_cast("amendment_id" AS VARCHAR) AS amendment_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/source_amendment_id.sql`；SHA-256 `867cd34d5d1fce0ba957ac23e14800c0aae441ebef82e461ceb8ecd3aa1ac674`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5350|否|
|L1|534|534|534|5330|否|
|L2|534|534|534|5330|否|
|L3|534|534|534|5330|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### type_balance
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少529。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 496起替换；其他字节相同。
原表达式：
```sql
try_cast("balance" AS BIGINT) AS balance
```

修改后：
```sql
"balance" AS balance
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/type_balance.sql`；SHA-256 `72cb28b084e293058c2cd50241f0dfa5b1b80d25e66a1247c84b7689d640db21`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5355|否|
|L1|534|534|534|5335|否|
|L2|534|534|534|5335|否|
|L3|534|534|534|5335|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### type_credit_amount
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第15行、offset 743起替换；其他字节相同。
原表达式：
```sql
try_cast("credit_amount" AS DOUBLE) AS credit_amount
```

修改后：
```sql
"credit_amount" AS credit_amount
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/type_credit_amount.sql`；SHA-256 `834b45d17a0b131c18ce5e5a9d573670a3b53908c50ade433a82c4d50926fdfc`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5879|否|
|L1|534|534|534|5864|否|
|L2|534|534|534|5864|否|
|L3|534|534|534|5864|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### type_exempt_amount
主因；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少534。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第18行、offset 941起替换；其他字节相同。
原表达式：
```sql
try_cast("exempt_amount" AS DOUBLE) AS exempt_amount
```

修改后：
```sql
"exempt_amount" AS exempt_amount
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/type_exempt_amount.sql`；SHA-256 `d2337e088776337b354d2fbb0cc6f5222cff2dae173566259c6919228d232008`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5350|否|
|L1|534|534|534|5335|否|
|L2|534|534|534|5335|否|
|L3|534|534|534|5335|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### source_invoice_id
主因；类别候选A。把本实体 id 当作 invoice_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少534。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第21行、offset 1157起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS invoice_id
```

修改后：
```sql
try_cast("invoice_id" AS VARCHAR) AS invoice_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/source_invoice_id.sql`；SHA-256 `d058c119dd3b2db0ab8ca1b6ed541f4dc0e86138dc2793d2ec63efa530473243`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5350|否|
|L1|534|534|534|5330|否|
|L2|534|534|534|5330|否|
|L3|534|534|534|5330|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### source_invoice_item_id
主因；类别候选A。把本实体 id 当作 invoice_item_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少534。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第22行、offset 1206起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS invoice_item_id
```

修改后：
```sql
try_cast("invoice_item_id" AS VARCHAR) AS invoice_item_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/source_invoice_item_id.sql`；SHA-256 `76015d83dd98ebe397e435efc79c6150e37b0a7ada5d616ee2e59ad0fc44c720`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5350|否|
|L1|534|534|534|5330|否|
|L2|534|534|534|5330|否|
|L3|534|534|534|5330|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### type_payment_amount
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第25行、offset 1374起替换；其他字节相同。
原表达式：
```sql
try_cast("payment_amount" AS DOUBLE) AS payment_amount
```

修改后：
```sql
"payment_amount" AS payment_amount
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/type_payment_amount.sql`；SHA-256 `222305d3475cd0018f6565b429a012a314f86c5919b0170c540fe52875fdf2f0`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5879|否|
|L1|534|534|534|5864|否|
|L2|534|534|534|5864|否|
|L3|534|534|534|5864|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### source_product_id
主因；类别候选U。P：本实体id可替代product_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少534。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第26行、offset 1438起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS product_id
```

修改后：
```sql
try_cast("product_id" AS VARCHAR) AS product_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/source_product_id.sql`；SHA-256 `acc316da47b99a3123697e4393516711fc1b39248214cca1f5ae384791f175a8`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5350|否|
|L1|534|534|534|5330|否|
|L2|534|534|534|5330|否|
|L3|534|534|534|5330|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### source_product_rate_plan_id
主因；类别候选A。把本实体 id 当作 product_rate_plan_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少534。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第28行、offset 1578起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS product_rate_plan_id
```

修改后：
```sql
try_cast("product_rate_plan_id" AS VARCHAR) AS product_rate_plan_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/source_product_rate_plan_id.sql`；SHA-256 `52db47a04394075d0be73a21a86e154b8aad5c40f855c07e3f29bd884d14bb62`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5350|否|
|L1|534|534|534|5330|否|
|L2|534|534|534|5330|否|
|L3|534|534|534|5330|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`

#### source_rate_plan_charge_id
主因；类别候选A。把本实体 id 当作 rate_plan_charge_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少534。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第29行、offset 1637起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS rate_plan_charge_id
```

修改后：
```sql
try_cast("rate_plan_charge_id" AS VARCHAR) AS rate_plan_charge_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/source_rate_plan_charge_id.sql`；SHA-256 `fbeeed1e04ade051c1a3866627484d0ee380151ae056ba35290efc131fe803af`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5350|否|
|L1|534|534|534|5330|否|
|L2|534|534|534|5330|否|
|L3|534|534|534|5330|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_id":534,"subscription_id":534}`

#### source_rate_plan_id
主因；类别候选A。把本实体 id 当作 rate_plan_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少534。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第30行、offset 1695起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS rate_plan_id
```

修改后：
```sql
try_cast("rate_plan_id" AS VARCHAR) AS rate_plan_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/source_rate_plan_id.sql`；SHA-256 `d14d0f76e75a0b582459c1f4639abbaa70f2e503a128598bfdbb3c1255692167`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5350|否|
|L1|534|534|534|5330|否|
|L2|534|534|534|5330|否|
|L3|534|534|534|5330|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"subscription_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"subscription_id":534}`

#### source_subscription_id
主因；类别候选A。把本实体 id 当作 subscription_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少534。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第33行、offset 1928起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS subscription_id
```

修改后：
```sql
try_cast("subscription_id" AS VARCHAR) AS subscription_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/source_subscription_id.sql`；SHA-256 `8387c8cf0d46b99dfded7a4e3adde516d0b6930245fb134d5f8e5d8d582482a5`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5350|否|
|L1|534|534|534|5330|否|
|L2|534|534|534|5330|否|
|L3|534|534|534|5330|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"tax_rate":5}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534}`

#### type_tax_rate
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第39行、offset 2305起替换；其他字节相同。
原表达式：
```sql
try_cast("tax_rate" AS DOUBLE) AS tax_rate
```

修改后：
```sql
"tax_rate" AS tax_rate
```

私有SQL：`data/024_work/impl-030_stg_zuora__taxation_item/type_tax_rate.sql`；SHA-256 `b111bbab4a606b50b2272d0fb3d663df8f8c24578512fea6ec9ed6f9e98b9b22`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|534|534|534|5879|否|
|L1|534|534|534|5864|否|
|L2|534|534|534|5864|否|
|L3|534|534|534|5864|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":534,"amendment_id":534,"balance":529,"credit_amount":5,"exempt_amount":534,"invoice_id":534,"invoice_item_id":534,"payment_amount":5,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L1：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L2：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
- L3：`{"account_id":534,"amendment_id":534,"balance":529,"exempt_amount":529,"invoice_id":534,"invoice_item_id":534,"product_id":534,"product_rate_plan_id":534,"rate_plan_charge_id":534,"rate_plan_id":534,"subscription_id":534}`
## 规则问题

多数ID候选和主表均不匹配，按A；只有product_id的5个非空值全部匹配product而本实体id零匹配，按U。不把完整表大部分NULL当成有匹配证据。

