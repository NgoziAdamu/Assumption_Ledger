# impl-030 · stg_zuora__refund

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**U**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：无。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__refund.md](../024_packages/024_impl-030_stg_zuora__refund.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
1165:     - name: stg_zuora__refund
1166:       description: "Cleaned refunds with timing metadata; latest snapshot indicator."
1167:       source_table: raw.zuora_refund_data
1168:       columns:
1169:         - name: refund_id
1170:           data_type: VARCHAR
1171:           source_expression: "id"
1172:         - name: accounting_code
1173:           data_type: VARCHAR
1174:         - name: amount
1175:           data_type: DOUBLE
1176:         - name: cancelled_on
1177:           data_type: TIMESTAMP
1178:           source_expression: "cast(cancelled_on as TIMESTAMP)"
1179:         - name: comment
1180:           data_type: VARCHAR
1181:         - name: created_by_id
1182:           data_type: VARCHAR
1183:         - name: created_date
1184:           data_type: TIMESTAMP
1185:           source_expression: "cast(created_date as TIMESTAMP)"
1186:         - name: method_type
1187:           data_type: VARCHAR
1188:         - name: payment_method_id
1189:           data_type: VARCHAR
1190:         - name: refund_date
1191:           data_type: VARCHAR
1192:         - name: refund_number
1193:           data_type: VARCHAR
1194:         - name: refund_transaction_time
1195:           data_type: TIMESTAMP
1196:           source_expression: "cast(refund_transaction_time as TIMESTAMP)"
1197:         - name: source_type
1198:           data_type: VARCHAR
1199:         - name: status
1200:           data_type: VARCHAR
1201:         - name: submitted_on
1202:           data_type: TIMESTAMP
1203:           source_expression: "cast(submitted_on as TIMESTAMP)"
1204:         - name: transferred_to_accounting
1205:           data_type: VARCHAR
1206:         - name: type
1207:           data_type: VARCHAR
1208:         - name: updated_by_id
1209:           data_type: VARCHAR
1210:         - name: updated_date
1211:           data_type: TIMESTAMP
1212:           source_expression: "cast(updated_date as TIMESTAMP)"
1213:         - name: is_most_recent_record
1214:           data_type: BOOLEAN
1215:           source_expression: "row_number() over (partition by id order by updated_date desc) = 1"
1216:       row_filters:
1217:         - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
1218:           on_failure: delete_row
1219:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__refund.sql`；SHA-256 `aa3c7b987e617f39135b94092381f3eeabfe8bf25074cfc097a30f17a4d5931f`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_refund_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS refund_id,
7:         try_cast("accounting_code" AS VARCHAR) AS accounting_code,
8:         try_cast("amount" AS DOUBLE) AS amount,
9:         try_cast(cancelled_on as TIMESTAMP) AS cancelled_on,
10:         try_cast("comment" AS VARCHAR) AS comment,
11:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
12:         try_cast(created_date as TIMESTAMP) AS created_date,
13:         try_cast("method_type" AS VARCHAR) AS method_type,
14:         try_cast("id" AS VARCHAR) AS payment_method_id,
15:         try_cast("refund_date" AS VARCHAR) AS refund_date,
16:         try_cast("refund_number" AS VARCHAR) AS refund_number,
17:         try_cast(refund_transaction_time as TIMESTAMP) AS refund_transaction_time,
18:         try_cast("source_type" AS VARCHAR) AS source_type,
19:         try_cast("status" AS VARCHAR) AS status,
20:         try_cast(submitted_on as TIMESTAMP) AS submitted_on,
21:         try_cast("transferred_to_accounting" AS VARCHAR) AS transferred_to_accounting,
22:         try_cast("type" AS VARCHAR) AS type,
23:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
24:         try_cast(updated_date as TIMESTAMP) AS updated_date,
25:         row_number() over (partition by id order by updated_date desc) = 1 AS is_most_recent_record
26: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__refund.sql`；SHA-256 `4a3fc05ee6a4f133d424e9175c27f31b20e8ff8fbdcb32d2485acfe222a44ef0`。

```text
1: with base as (
2:     select * from raw.zuora_refund_data
3:     where _fivetran_deleted is null or _fivetran_deleted = false
4: ),
5: final as (
6:     select
7:         id as refund_id,
8:         accounting_code,
9:         amount,
10:         cast(cancelled_on as TIMESTAMP) as cancelled_on,
11:         comment,
12:         created_by_id,
13:         cast(created_date as TIMESTAMP) as created_date,
14:         method_type,
15:         payment_method_id,
16:         refund_date,
17:         refund_number,
18:         cast(refund_transaction_time as TIMESTAMP) as refund_transaction_time,
19:         source_type,
20:         status,
21:         cast(submitted_on as TIMESTAMP) as submitted_on,
22:         transferred_to_accounting,
23:         type,
24:         updated_by_id,
25:         cast(updated_date as TIMESTAMP) as updated_date,
26:         row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
27:     from base
28: )
29: select * from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_refund_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_refund_data","id","VARCHAR"],["zuora_refund_data","_fivetran_deleted","BOOLEAN"],["zuora_refund_data","_fivetran_synced","TIMESTAMP"],["zuora_refund_data","accounting_code","VARCHAR"],["zuora_refund_data","amount","DOUBLE"],["zuora_refund_data","cancelled_on","VARCHAR"],["zuora_refund_data","comment","VARCHAR"],["zuora_refund_data","created_by_id","VARCHAR"],["zuora_refund_data","created_date","TIMESTAMP"],["zuora_refund_data","gateway","VARCHAR"],["zuora_refund_data","gateway_reconciliation_reason","VARCHAR"],["zuora_refund_data","gateway_reconciliation_status","VARCHAR"],["zuora_refund_data","gateway_response","VARCHAR"],["zuora_refund_data","gateway_response_code","VARCHAR"],["zuora_refund_data","gateway_state","VARCHAR"],["zuora_refund_data","marked_for_submission_on","TIMESTAMP"],["zuora_refund_data","method_type","VARCHAR"],["zuora_refund_data","payment_method_id","VARCHAR"],["zuora_refund_data","payout_id","VARCHAR"],["zuora_refund_data","reason_code","VARCHAR"],["zuora_refund_data","reference_id","VARCHAR"],["zuora_refund_data","refund_date","VARCHAR"],["zuora_refund_data","refund_number","VARCHAR"],["zuora_refund_data","refund_transaction_time","VARCHAR"],["zuora_refund_data","second_refund_reference_id","VARCHAR"],["zuora_refund_data","soft_descriptor","VARCHAR"],["zuora_refund_data","soft_descriptor_phone","VARCHAR"],["zuora_refund_data","source_type","VARCHAR"],["zuora_refund_data","status","VARCHAR"],["zuora_refund_data","submitted_on","VARCHAR"],["zuora_refund_data","transferred_to_accounting","BOOLEAN"],["zuora_refund_data","type","VARCHAR"],["zuora_refund_data","updated_by_id","VARCHAR"],["zuora_refund_data","updated_date","TIMESTAMP"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'payment_method_id' col,count(*) n,count(payment_method_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(payment_method_id as varchar)) same_as_id FROM raw.zuora_refund_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["payment_method_id",5,5,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'payment_method_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.payment_method_id as varchar))) named_col_matches FROM raw.zuora_refund_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["payment_method_id",5,0,5]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_refund_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'payment_method_id' col,count(*) n,count(s.payment_method_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_payment_method_data t WHERE cast(t.id as varchar)=cast(s.payment_method_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["payment_method_id",3,3,0,3]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_refund_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'payment_method_id' col,count(*) n,count(payment_method_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(payment_method_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(payment_method_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["payment_method_id",3,3,3,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__refund.json
[024_reruns_impl-030_stg_zuora__refund.json](../024_reruns_impl-030_stg_zuora__refund.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3|3|3|3|否|
|L1|3|3|3|3|否|
|L2|3|3|3|3|否|
|L3|3|3|3|3|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"payment_method_id":3}`
- L1：`{"payment_method_id":3}`
- L2：`{"payment_method_id":3}`
- L3：`{"payment_method_id":3}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__refund/baseline.sql`；SHA-256 `aa3c7b987e617f39135b94092381f3eeabfe8bf25074cfc097a30f17a4d5931f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3|3|3|3|否|
|L1|3|3|3|3|否|
|L2|3|3|3|3|否|
|L3|3|3|3|3|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"payment_method_id":3}`
- L1：`{"payment_method_id":3}`
- L2：`{"payment_method_id":3}`
- L3：`{"payment_method_id":3}`

#### source_payment_method_id
主因；类别候选U。P：本实体id可替代payment_method_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少3，格减少3。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第14行、offset 614起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS payment_method_id
```

修改后：
```sql
try_cast("payment_method_id" AS VARCHAR) AS payment_method_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__refund/source_payment_method_id.sql`；SHA-256 `abcd18a7d7d8b6358939c740e41ebb23753e68cf4b488df8af38d0ded9771e69`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3|3|0|0|是|
|L1|3|3|0|0|是|
|L2|3|3|0|0|是|
|L3|3|3|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

