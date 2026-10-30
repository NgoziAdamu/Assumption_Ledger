# impl-030 · stg_zuora__account

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

gold未按契约类型转换tax_exempt_status、余额等字段；agent BOOLEAN/BIGINT/DOUBLE符合契约，主要是tax_exempt_status。

参与因素：O：type_credit_balance（行减0，格减3）；O：type_mrr（行减0，格减2）；O：type_total_debit_memo_balance（行减0，格减3788）；O：type_total_invoice_balance（行减0，格减3）。
标记：无。

## 材料与比较口径

[024_impl-030_stg_zuora__account.md](../024_packages/024_impl-030_stg_zuora__account.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
26:     - name: stg_zuora__account
27:       description: "Cleaned and normalized account records; latest snapshot indicator provided."
28:       source_table: raw.zuora_account_data
29:       columns:
30:         - name: account_id
31:           data_type: VARCHAR
32:         - name: account_number
33:           data_type: VARCHAR
34:         - name: auto_pay
35:           data_type: BOOLEAN
36:         - name: balance
37:           data_type: DECIMAL(18,2)
38:           validation_rules:
39:             - rule: "try_cast(balance as DECIMAL(18,2)) IS NOT NULL"
40:               on_failure: nullify_field
41:             - rule: "try_cast(balance as DECIMAL(18,2)) BETWEEN -1000000 AND 1000000"
42:               on_failure: nullify_field
43:             - rule: "balance = ROUND(CAST(balance AS DECIMAL(18,2)), 2)"
44:               on_failure: correct
45:         - name: batch
46:           data_type: VARCHAR
47:         - name: bill_cycle_day
48:           data_type: INTEGER
49:         - name: bill_to_contact_id
50:           data_type: VARCHAR
51:         - name: created_by_id
52:           data_type: VARCHAR
53:         - name: created_date
54:           data_type: TIMESTAMP
55:         - name: credit_balance
56:           data_type: DOUBLE
57:         - name: crm_id
58:           data_type: VARCHAR
59:         - name: currency
60:           data_type: VARCHAR
61:         - name: default_payment_method_id
62:           data_type: VARCHAR
63:         - name: last_invoice_date
64:           data_type: TIMESTAMP
65:           validation_rules:
66:             - rule: "NULLIF(last_invoice_date,'') IS NULL OR try_cast(last_invoice_date as TIMESTAMP) IS NOT NULL"
67:               on_failure: nullify_field
68:         - name: mrr
69:           data_type: DOUBLE
70:         - name: name
71:           data_type: VARCHAR
72:         - name: notes
73:           data_type: VARCHAR
74:         - name: parent_account_id
75:           data_type: VARCHAR
76:         - name: payment_term
77:           data_type: VARCHAR
78:         - name: sold_to_contact_id
79:           data_type: VARCHAR
80:         - name: status
81:           data_type: VARCHAR
82:           validation_rules:
83:             - rule: "lower(status) IN ('active','draft','cancelled')"
84:               on_failure: delete_row
85:             - rule: "status = CASE WHEN lower(status)='active' THEN 'Active' WHEN lower(status)='draft' THEN 'Draft' WHEN lower(status)='cancelled' THEN 'Cancelled' ELSE status END"
86:               on_failure: correct
87:             - rule: "status IS NOT NULL"
88:               on_failure: delete_row
89:         - name: tax_exempt_effective_date
90:           data_type: TIMESTAMP
91:         - name: tax_exempt_expiration_date
92:           data_type: TIMESTAMP
93:         - name: tax_exempt_status
94:           data_type: BOOLEAN
95:         - name: total_debit_memo_balance
96:           data_type: BIGINT
97:         - name: total_invoice_balance
98:           data_type: DOUBLE
99:         - name: updated_by_id
100:           data_type: VARCHAR
101:         - name: updated_date
102:           data_type: TIMESTAMP
103:         - name: vatid
104:           data_type: VARCHAR
105:         - name: is_most_recent_record
106:           data_type: BOOLEAN
107:       row_filters:
108:         - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
109:           on_failure: delete_row
110:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__account.sql`；SHA-256 `9828a58e98ffc545df678ce7e943c5a7b4da5fe476055be45201b5c6bb82440c`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_account_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't') AND status IS NOT NULL AND lower(status) IN ('active', 'draft', 'cancelled'))
5: SELECT
6:         try_cast("id" AS VARCHAR) AS account_id,
7:         try_cast("account_number" AS VARCHAR) AS account_number,
8:         try_cast("auto_pay" AS BOOLEAN) AS auto_pay,
9:         CASE WHEN try_cast("balance" AS DECIMAL(18,2)) BETWEEN -1000000 AND 1000000 THEN round(try_cast("balance" AS DECIMAL(18,2)), 2)::DECIMAL(18,2) ELSE NULL END AS balance,
10:         try_cast("batch" AS VARCHAR) AS batch,
11:         try_cast("bill_cycle_day" AS INTEGER) AS bill_cycle_day,
12:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
13:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
14:         try_cast("created_date" AS TIMESTAMP) AS created_date,
15:         try_cast("credit_balance" AS DOUBLE) AS credit_balance,
16:         try_cast("crm_id" AS VARCHAR) AS crm_id,
17:         try_cast("currency" AS VARCHAR) AS currency,
18:         try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
19:         try_cast("last_invoice_date" AS TIMESTAMP) AS last_invoice_date,
20:         try_cast("mrr" AS DOUBLE) AS mrr,
21:         try_cast("name" AS VARCHAR) AS name,
22:         try_cast("notes" AS VARCHAR) AS notes,
23:         try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
24:         try_cast("payment_term" AS VARCHAR) AS payment_term,
25:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
26:         CASE lower(status) WHEN 'active' THEN 'Active' WHEN 'draft' THEN 'Draft' WHEN 'cancelled' THEN 'Cancelled' ELSE NULL END AS status,
27:         try_cast("tax_exempt_effective_date" AS TIMESTAMP) AS tax_exempt_effective_date,
28:         try_cast("tax_exempt_expiration_date" AS TIMESTAMP) AS tax_exempt_expiration_date,
29:         try_cast("tax_exempt_status" AS BOOLEAN) AS tax_exempt_status,
30:         try_cast("total_debit_memo_balance" AS BIGINT) AS total_debit_memo_balance,
31:         try_cast("total_invoice_balance" AS DOUBLE) AS total_invoice_balance,
32:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
33:         try_cast("updated_date" AS TIMESTAMP) AS updated_date,
34:         try_cast("vatid" AS VARCHAR) AS vatid,
35:         row_number() over (partition by id order by try_cast(updated_date as timestamp) desc NULLS LAST) = 1 AS is_most_recent_record
36: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__account.sql`；SHA-256 `38edafea6622ae1dab5afc846c242716af2026205d02f184e5af0ffda0b94d48`。

```text
1: with base as (
2:     select * from raw.zuora_account_data where _fivetran_deleted is null or _fivetran_deleted = false
3: ),
4: cleaned as (
5:     select
6:         id as account_id,
7:         account_number,
8:         auto_pay,
9:         -- balance cleaning: try cast to numeric and clamp range, 2-decimal precision
10:         case
11:             when try_cast(balance as DECIMAL(18,2)) is null then null
12:             when try_cast(balance as DECIMAL(18,2)) < -1000000 or try_cast(balance as DECIMAL(18,2)) > 1000000 then null
13:             else round(cast(balance as DECIMAL(18,2)), 2)
14:         end as balance,
15:         batch,
16:         bill_cycle_day,
17:         bill_to_contact_id,
18:         created_by_id,
19:         cast(created_date as TIMESTAMP) as created_date,
20:         credit_balance,
21:         crm_id,
22:         currency,
23:         default_payment_method_id,
24:         case when nullif(last_invoice_date,'') is null then null else cast(last_invoice_date as TIMESTAMP) end as last_invoice_date,
25:         mrr,
26:         name,
27:         notes,
28:         parent_account_id,
29:         payment_term,
30:         sold_to_contact_id,
31:         -- status normalization and validation
32:         case
33:             when lower(status) = 'active' then 'Active'
34:             when lower(status) = 'draft' then 'Draft'
35:             when lower(status) = 'cancelled' then 'Cancelled'
36:             else status
37:         end as status,
38:         case when nullif(tax_exempt_effective_date,'') is null then null else cast(tax_exempt_effective_date as TIMESTAMP) end as tax_exempt_effective_date,
39:         case when nullif(tax_exempt_expiration_date,'') is null then null else cast(tax_exempt_expiration_date as TIMESTAMP) end as tax_exempt_expiration_date,
40:         tax_exempt_status,
41:         total_debit_memo_balance,
42:         total_invoice_balance,
43:         updated_by_id,
44:         cast(updated_date as TIMESTAMP) as updated_date,
45:         vatid,
46:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 as is_most_recent_record
47:     from base
48: ),
49: final as (
50:     select * from cleaned
51:     where status is not null and status in ('Active','Draft','Cancelled')
52: )
53: select * from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- type_tax_exempt_status（O）：**只有通用策略说明**；事件 69。
原句：

```
非关键不可解析值转为 NULL。
```

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

核实查询 **1** 条；代价档：**一条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_account_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_account_data","id","VARCHAR"],["zuora_account_data","_fivetran_deleted","VARCHAR"],["zuora_account_data","_fivetran_synced","VARCHAR"],["zuora_account_data","account_number","VARCHAR"],["zuora_account_data","additional_email_addresses","VARCHAR"],["zuora_account_data","allow_invoice_edit","VARCHAR"],["zuora_account_data","auto_pay","VARCHAR"],["zuora_account_data","balance","VARCHAR"],["zuora_account_data","bcd_setting_option","VARCHAR"],["zuora_account_data","bill_cycle_day","VARCHAR"],["zuora_account_data","bill_to_contact_id","VARCHAR"],["zuora_account_data","bill_to_id","VARCHAR"],["zuora_account_data","communication_profile_id","VARCHAR"],["zuora_account_data","created_by_id","VARCHAR"],["zuora_account_data","created_date","VARCHAR"],["zuora_account_data","credit_balance","VARCHAR"],["zuora_account_data","crm_id","VARCHAR"],["zuora_account_data","currency","VARCHAR"],["zuora_account_data","customer_service_rep_name","VARCHAR"],["zuora_account_data","default_payment_method_id","VARCHAR"],["zuora_account_data","invoice_delivery_prefs_email","VARCHAR"],["zuora_account_data","invoice_delivery_prefs_print","VARCHAR"],["zuora_account_data","invoice_template_id","VARCHAR"],["zuora_account_data","last_invoice_date","VARCHAR"],["zuora_account_data","mrr","VARCHAR"],["zuora_account_data","name","VARCHAR"],["zuora_account_data","notes","VARCHAR"],["zuora_account_data","parent_account_id","VARCHAR"],["zuora_account_data","parent_id","VARCHAR"],["zuora_account_data","payment_gateway","VARCHAR"],["zuora_account_data","payment_term","VARCHAR"],["zuora_account_data","purchase_order_number","VARCHAR"],["zuora_account_data","sales_rep_name","VARCHAR"],["zuora_account_data","sequence_set_id","VARCHAR"],["zuora_account_data","sold_to_contact_id","VARCHAR"],["zuora_account_data","sold_to_id","VARCHAR"],["zuora_account_data","status","VARCHAR"],["zuora_account_data","tax_company_code","VARCHAR"],["zuora_account_data","tax_exempt_certificate_id","VARCHAR"],["zuora_account_data","tax_exempt_certificate_type","VARCHAR"],["zuora_account_data","tax_exempt_description","VARCHAR"],["zuora_account_data","tax_exempt_effective_date","VARCHAR"],["zuora_account_data","tax_exempt_entity_use_code","VARCHAR"],["zuora_account_data","tax_exempt_expiration_date","VARCHAR"],["zuora_account_data","tax_exempt_issuing_jurisdiction","VARCHAR"],["zuora_account_data","tax_exempt_status","VARCHAR"],["zuora_account_data","testcustom_1_c","VARCHAR"],["zuora_account_data","testcustom_2_c","VARCHAR"],["zuora_account_data","total_debit_memo_balance","VARCHAR"],["zuora_account_data","total_invoice_balance","VARCHAR"],["zuora_account_data","unapplied_balance","VARCHAR"],["zuora_account_data","unapplied_credit_memo_amount","VARCHAR"],["zuora_account_data","updated_by_id","VARCHAR"],["zuora_account_data","updated_date","VARCHAR"],["zuora_account_data","vatid","VARCHAR"],["zuora_account_data","batch","VARCHAR"]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__account.json
[024_reruns_impl-030_stg_zuora__account.json](../024_reruns_impl-030_stg_zuora__account.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3791|3791|3791|7587|否|
|L1|3791|3791|3791|7541|否|
|L2|3791|3791|3791|7541|否|
|L3|3791|3791|3791|7541|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"credit_balance":3,"mrr":2,"tax_exempt_status":3791,"total_debit_memo_balance":3788,"total_invoice_balance":3}`
- L1：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
- L2：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
- L3：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__account/baseline.sql`；SHA-256 `9828a58e98ffc545df678ce7e943c5a7b4da5fe476055be45201b5c6bb82440c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3791|3791|3791|7587|否|
|L1|3791|3791|3791|7541|否|
|L2|3791|3791|3791|7541|否|
|L3|3791|3791|3791|7541|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"credit_balance":3,"mrr":2,"tax_exempt_status":3791,"total_debit_memo_balance":3788,"total_invoice_balance":3}`
- L1：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
- L2：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
- L3：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`

#### type_credit_balance
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少3。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第15行、offset 912起替换；其他字节相同。
原表达式：
```sql
try_cast("credit_balance" AS DOUBLE) AS credit_balance
```

修改后：
```sql
"credit_balance" AS credit_balance
```

私有SQL：`data/024_work/impl-030_stg_zuora__account/type_credit_balance.sql`；SHA-256 `a0d1ab387abd715d154393308c9ff892c043668dae8e6605d1f6dba592ab1538`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3791|3791|3791|7584|否|
|L1|3791|3791|3791|7541|否|
|L2|3791|3791|3791|7541|否|
|L3|3791|3791|3791|7541|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"mrr":2,"tax_exempt_status":3791,"total_debit_memo_balance":3788,"total_invoice_balance":3}`
- L1：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
- L2：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
- L3：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`

#### type_mrr
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少2。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第20行、offset 1238起替换；其他字节相同。
原表达式：
```sql
try_cast("mrr" AS DOUBLE) AS mrr
```

修改后：
```sql
"mrr" AS mrr
```

私有SQL：`data/024_work/impl-030_stg_zuora__account/type_mrr.sql`；SHA-256 `da42e41beed824a9e31672d06e4bfca9fe680a07713b415e582401fc94eaf0b3`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3791|3791|3791|7585|否|
|L1|3791|3791|3791|7540|否|
|L2|3791|3791|3791|7540|否|
|L3|3791|3791|3791|7540|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"credit_balance":3,"tax_exempt_status":3791,"total_debit_memo_balance":3788,"total_invoice_balance":3}`
- L1：`{"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
- L2：`{"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
- L3：`{"tax_exempt_status":3791,"total_debit_memo_balance":3749}`

#### type_tax_exempt_status
主因；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少1，格减少3791。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第29行、offset 1897起替换；其他字节相同。
原表达式：
```sql
try_cast("tax_exempt_status" AS BOOLEAN) AS tax_exempt_status
```

修改后：
```sql
"tax_exempt_status" AS tax_exempt_status
```

私有SQL：`data/024_work/impl-030_stg_zuora__account/type_tax_exempt_status.sql`；SHA-256 `b5a255b07179c5ee1e11768011019f8a60eda4eccb306e06c6af82516b49925a`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3791|3791|3790|3796|否|
|L1|3791|3791|3749|3750|否|
|L2|3791|3791|3749|3750|否|
|L3|3791|3791|3749|3750|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"credit_balance":3,"mrr":2,"total_debit_memo_balance":3788,"total_invoice_balance":3}`
- L1：`{"mrr":1,"total_debit_memo_balance":3749}`
- L2：`{"mrr":1,"total_debit_memo_balance":3749}`
- L3：`{"mrr":1,"total_debit_memo_balance":3749}`

#### type_total_debit_memo_balance
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少3788。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第30行、offset 1968起替换；其他字节相同。
原表达式：
```sql
try_cast("total_debit_memo_balance" AS BIGINT) AS total_debit_memo_balance
```

修改后：
```sql
"total_debit_memo_balance" AS total_debit_memo_balance
```

私有SQL：`data/024_work/impl-030_stg_zuora__account/type_total_debit_memo_balance.sql`；SHA-256 `b0a8014a2c19f128563c06f2b8b5fb4d4d3ee7f3a5e87be3cace609538cfe0bc`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3791|3791|3791|3799|否|
|L1|3791|3791|3791|3792|否|
|L2|3791|3791|3791|3792|否|
|L3|3791|3791|3791|3792|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"credit_balance":3,"mrr":2,"tax_exempt_status":3791,"total_invoice_balance":3}`
- L1：`{"mrr":1,"tax_exempt_status":3791}`
- L2：`{"mrr":1,"tax_exempt_status":3791}`
- L3：`{"mrr":1,"tax_exempt_status":3791}`

#### type_total_invoice_balance
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少3。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第31行、offset 2052起替换；其他字节相同。
原表达式：
```sql
try_cast("total_invoice_balance" AS DOUBLE) AS total_invoice_balance
```

修改后：
```sql
"total_invoice_balance" AS total_invoice_balance
```

私有SQL：`data/024_work/impl-030_stg_zuora__account/type_total_invoice_balance.sql`；SHA-256 `ff789276d42d1c9e2531a3d15cd82e43b84b5f9f3b5ca5f19743b1ac65374034`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3791|3791|3791|7584|否|
|L1|3791|3791|3791|7541|否|
|L2|3791|3791|3791|7541|否|
|L3|3791|3791|3791|7541|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"credit_balance":3,"mrr":2,"tax_exempt_status":3791,"total_debit_memo_balance":3788}`
- L1：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
- L2：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
- L3：`{"mrr":1,"tax_exempt_status":3791,"total_debit_memo_balance":3749}`
## 规则问题

无。

