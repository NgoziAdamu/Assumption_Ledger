# impl-030 · stg_zuora__credit_balance_adjustment

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**U**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：无。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__credit_balance_adjustment.md](../024_packages/024_impl-030_stg_zuora__credit_balance_adjustment.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
1094:     - name: stg_zuora__credit_balance_adjustment
1095:       description: "Cleaned credit balance adjustments; latest snapshot indicator."
1096:       source_table: raw.zuora_credit_balance_adjustment_data
1097:       columns:
1098:         - name: credit_balance_adjustment_id
1099:           data_type: VARCHAR
1100:         - name: account_id
1101:           data_type: VARCHAR
1102:         - name: account_receivable_accounting_code_id
1103:           data_type: VARCHAR
1104:         - name: accounting_code
1105:           data_type: VARCHAR
1106:         - name: adjustment_date
1107:           data_type: DATE
1108:         - name: amount
1109:           data_type: DOUBLE
1110:         - name: amount_home_currency
1111:           data_type: VARCHAR
1112:         - name: bill_to_contact_id
1113:           data_type: VARCHAR
1114:         - name: cancelled_on
1115:           data_type: TIMESTAMP
1116:         - name: comment
1117:           data_type: VARCHAR
1118:         - name: created_by_id
1119:           data_type: VARCHAR
1120:         - name: created_date
1121:           data_type: TIMESTAMP
1122:         - name: default_payment_method_id
1123:           data_type: VARCHAR
1124:         - name: exchange_rate
1125:           data_type: VARCHAR
1126:         - name: exchange_rate_date
1127:           data_type: DATE
1128:         - name: home_currency
1129:           data_type: VARCHAR
1130:         - name: invoice_id
1131:           data_type: VARCHAR
1132:         - name: journal_entry_id
1133:           data_type: VARCHAR
1134:         - name: number
1135:           data_type: VARCHAR
1136:         - name: parent_account_id
1137:           data_type: VARCHAR
1138:         - name: reason_code
1139:           data_type: VARCHAR
1140:         - name: reference_id
1141:           data_type: VARCHAR
1142:         - name: sold_to_contact_id
1143:           data_type: VARCHAR
1144:         - name: source_transaction_id
1145:           data_type: VARCHAR
1146:         - name: source_transaction_number
1147:           data_type: VARCHAR
1148:         - name: source_transaction_type
1149:           data_type: VARCHAR
1150:         - name: status
1151:           data_type: VARCHAR
1152:         - name: transaction_currency
1153:           data_type: VARCHAR
1154:         - name: transferred_to_accounting
1155:           data_type: VARCHAR
1156:         - name: type
1157:           data_type: VARCHAR
1158:         - name: updated_by_id
1159:           data_type: VARCHAR
1160:         - name: updated_date
1161:           data_type: TIMESTAMP
1162:         - name: is_most_recent_record
1163:           data_type: BOOLEAN
1164:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__credit_balance_adjustment.sql`；SHA-256 `1aae0f429afe0f86abb65b15408fbf357c1e0186f8ae84e9c72ee1f825707ce1`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_credit_balance_adjustment_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         try_cast("id" AS VARCHAR) AS credit_balance_adjustment_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("account_receivable_accounting_code_id" AS VARCHAR) AS account_receivable_accounting_code_id,
9:         try_cast("accounting_code" AS VARCHAR) AS accounting_code,
10:         try_cast("adjustment_date" AS DATE) AS adjustment_date,
11:         try_cast("amount" AS DOUBLE) AS amount,
12:         try_cast("amount_home_currency" AS VARCHAR) AS amount_home_currency,
13:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
14:         try_cast("cancelled_on" AS TIMESTAMP) AS cancelled_on,
15:         try_cast("comment" AS VARCHAR) AS comment,
16:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
17:         try_cast("created_date" AS TIMESTAMP) AS created_date,
18:         try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
19:         try_cast("exchange_rate" AS VARCHAR) AS exchange_rate,
20:         try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date,
21:         try_cast("home_currency" AS VARCHAR) AS home_currency,
22:         try_cast("id" AS VARCHAR) AS invoice_id,
23:         try_cast("journal_entry_id" AS VARCHAR) AS journal_entry_id,
24:         try_cast("number" AS VARCHAR) AS number,
25:         try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
26:         try_cast("reason_code" AS VARCHAR) AS reason_code,
27:         try_cast("reference_id" AS VARCHAR) AS reference_id,
28:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
29:         try_cast("source_transaction_id" AS VARCHAR) AS source_transaction_id,
30:         try_cast("source_transaction_number" AS VARCHAR) AS source_transaction_number,
31:         try_cast("source_transaction_type" AS VARCHAR) AS source_transaction_type,
32:         try_cast("status" AS VARCHAR) AS status,
33:         try_cast("transaction_currency" AS VARCHAR) AS transaction_currency,
34:         try_cast("transferred_to_accounting" AS VARCHAR) AS transferred_to_accounting,
35:         try_cast("type" AS VARCHAR) AS type,
36:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
37:         try_cast("updated_date" AS TIMESTAMP) AS updated_date,
38:         row_number() over (partition by id order by try_cast(updated_date as timestamp) desc NULLS LAST) = 1 AS is_most_recent_record
39: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__credit_balance_adjustment.sql`；SHA-256 `07d036620ce00b912b6c8d9064a19f03c49f908d9ad6d5fa69c05a918bb98260`。

```text
1: with base as (
2:     select * from raw.zuora_credit_balance_adjustment_data
3:     where _fivetran_deleted is null or _fivetran_deleted = false
4: ),
5: final as (
6:     select
7:         id as credit_balance_adjustment_id,
8:         account_id,
9:         account_receivable_accounting_code_id,
10:         accounting_code,
11:         adjustment_date,
12:         amount,
13:         amount_home_currency,
14:         bill_to_contact_id,
15:         cast(cancelled_on as TIMESTAMP) as cancelled_on,
16:         comment,
17:         created_by_id,
18:         cast(created_date as TIMESTAMP) as created_date,
19:         default_payment_method_id,
20:         exchange_rate,
21:         exchange_rate_date,
22:         home_currency,
23:         invoice_id,
24:         journal_entry_id,
25:         number,
26:         parent_account_id,
27:         reason_code,
28:         reference_id,
29:         sold_to_contact_id,
30:         source_transaction_id,
31:         source_transaction_number,
32:         source_transaction_type,
33:         status,
34:         transaction_currency,
35:         transferred_to_accounting,
36:         type,
37:         updated_by_id,
38:         cast(updated_date as TIMESTAMP) as updated_date,
39:         row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
40:     from base
41: )
42: select * from final
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

- source_invoice_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 invoice_id。
P：本实体id可替代invoice_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_credit_balance_adjustment_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_credit_balance_adjustment_data","id","VARCHAR"],["zuora_credit_balance_adjustment_data","_fivetran_deleted","BOOLEAN"],["zuora_credit_balance_adjustment_data","_fivetran_synced","TIMESTAMP"],["zuora_credit_balance_adjustment_data","account_id","VARCHAR"],["zuora_credit_balance_adjustment_data","account_receivable_accounting_code_id","VARCHAR"],["zuora_credit_balance_adjustment_data","accounting_code","VARCHAR"],["zuora_credit_balance_adjustment_data","accounting_period_id","VARCHAR"],["zuora_credit_balance_adjustment_data","adjustment_date","DATE"],["zuora_credit_balance_adjustment_data","amount","DOUBLE"],["zuora_credit_balance_adjustment_data","amount_currency_rounding","VARCHAR"],["zuora_credit_balance_adjustment_data","amount_home_currency","VARCHAR"],["zuora_credit_balance_adjustment_data","bill_to_contact_id","VARCHAR"],["zuora_credit_balance_adjustment_data","cancelled_on","VARCHAR"],["zuora_credit_balance_adjustment_data","comment","VARCHAR"],["zuora_credit_balance_adjustment_data","created_by_id","VARCHAR"],["zuora_credit_balance_adjustment_data","created_date","TIMESTAMP"],["zuora_credit_balance_adjustment_data","customer_cash_on_account_accounting_code_id","VARCHAR"],["zuora_credit_balance_adjustment_data","default_payment_method_id","VARCHAR"],["zuora_credit_balance_adjustment_data","exchange_rate","VARCHAR"],["zuora_credit_balance_adjustment_data","exchange_rate_date","DATE"],["zuora_credit_balance_adjustment_data","home_currency","VARCHAR"],["zuora_credit_balance_adjustment_data","invoice_id","VARCHAR"],["zuora_credit_balance_adjustment_data","journal_entry_id","VARCHAR"],["zuora_credit_balance_adjustment_data","journal_run_id","VARCHAR"],["zuora_credit_balance_adjustment_data","number","VARCHAR"],["zuora_credit_balance_adjustment_data","parent_account_id","VARCHAR"],["zuora_credit_balance_adjustment_data","provider_exchange_rate_date","DATE"],["zuora_credit_balance_adjustment_data","reason_code","VARCHAR"],["zuora_credit_balance_adjustment_data","reference_id","VARCHAR"],["zuora_credit_balance_adjustment_data","sold_to_contact_id","VARCHAR"],["zuora_credit_balance_adjustment_data","source_transaction_id","VARCHAR"],["zuora_credit_balance_adjustment_data","source_transaction_number","VARCHAR"],["zuora_credit_balance_adjustment_data","source_transaction_type","VARCHAR"],["zuora_credit_balance_adjustment_data","status","VARCHAR"],["zuora_credit_balance_adjustment_data","transaction_currency","VARCHAR"],["zuora_credit_balance_adjustment_data","transferred_to_accounting","VARCHAR"],["zuora_credit_balance_adjustment_data","type","VARCHAR"],["zuora_credit_balance_adjustment_data","updated_by_id","VARCHAR"],["zuora_credit_balance_adjustment_data","updated_date","TIMESTAMP"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_credit_balance_adjustment_data UNION ALL SELECT 'invoice_id' col,count(*) n,count(invoice_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(invoice_id as varchar)) same_as_id FROM raw.zuora_credit_balance_adjustment_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",6,6,0],["invoice_id",6,6,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_credit_balance_adjustment_data s UNION ALL SELECT 'invoice_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.invoice_id as varchar))) named_col_matches FROM raw.zuora_credit_balance_adjustment_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",6,0,2],["invoice_id",6,0,6]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_credit_balance_adjustment_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'invoice_id' col,count(*) n,count(s.invoice_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_invoice_data t WHERE cast(t.id as varchar)=cast(s.invoice_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",6,6,0,2],["invoice_id",6,6,0,6]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_credit_balance_adjustment_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'invoice_id' col,count(*) n,count(invoice_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(invoice_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(invoice_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",6,6,6,0],["invoice_id",6,6,6,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__credit_balance_adjustment.json
[024_reruns_impl-030_stg_zuora__credit_balance_adjustment.json](../024_reruns_impl-030_stg_zuora__credit_balance_adjustment.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|6|12|否|
|L1|6|6|6|12|否|
|L2|6|6|6|12|否|
|L3|6|6|6|12|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":6,"invoice_id":6}`
- L1：`{"account_id":6,"invoice_id":6}`
- L2：`{"account_id":6,"invoice_id":6}`
- L3：`{"account_id":6,"invoice_id":6}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__credit_balance_adjustment/baseline.sql`；SHA-256 `1aae0f429afe0f86abb65b15408fbf357c1e0186f8ae84e9c72ee1f825707ce1`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|6|12|否|
|L1|6|6|6|12|否|
|L2|6|6|6|12|否|
|L3|6|6|6|12|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":6,"invoice_id":6}`
- L1：`{"account_id":6,"invoice_id":6}`
- L2：`{"account_id":6,"invoice_id":6}`
- L3：`{"account_id":6,"invoice_id":6}`

#### source_account_id
主因；类别候选U。P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少6。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第7行、offset 265起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__credit_balance_adjustment/source_account_id.sql`；SHA-256 `90a5f60f22a92a81bfc7248ff4819808a63247fbb42b6e5eca36821ef1efd1fb`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|6|6|否|
|L1|6|6|6|6|否|
|L2|6|6|6|6|否|
|L3|6|6|6|6|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"invoice_id":6}`
- L1：`{"invoice_id":6}`
- L2：`{"invoice_id":6}`
- L3：`{"invoice_id":6}`

#### source_invoice_id
主因；类别候选U。P：本实体id可替代invoice_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少6。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第22行、offset 1277起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS invoice_id
```

修改后：
```sql
try_cast("invoice_id" AS VARCHAR) AS invoice_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__credit_balance_adjustment/source_invoice_id.sql`；SHA-256 `aad7f9aab82a2c5c78c2faa546f96d8b6a124a5701d57c3190a1002ed8f8856c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|6|6|否|
|L1|6|6|6|6|否|
|L2|6|6|6|6|否|
|L3|6|6|6|6|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":6}`
- L1：`{"account_id":6}`
- L2：`{"account_id":6}`
- L3：`{"account_id":6}`
## 规则问题

无。

