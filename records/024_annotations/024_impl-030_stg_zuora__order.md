# impl-030 · stg_zuora__order

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**U**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：无。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__order.md](../024_packages/024_impl-030_stg_zuora__order.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
1049:     - name: stg_zuora__order
1050:       description: "Cleaned orders including scheduling and error metadata; latest snapshot indicator."
1051:       source_table: raw.zuora_order_data
1052:       columns:
1053:         - name: order_id
1054:           data_type: VARCHAR
1055:         - name: account_id
1056:           data_type: VARCHAR
1057:         - name: bill_to_contact_id
1058:           data_type: VARCHAR
1059:         - name: category
1060:           data_type: VARCHAR
1061:         - name: created_by_id
1062:           data_type: BIGINT
1063:         - name: created_date
1064:           data_type: TIMESTAMP
1065:         - name: default_payment_method_id
1066:           data_type: VARCHAR
1067:         - name: description
1068:           data_type: VARCHAR
1069:         - name: error_code
1070:           data_type: VARCHAR
1071:         - name: error_message
1072:           data_type: VARCHAR
1073:         - name: order_date
1074:           data_type: DATE
1075:         - name: order_number
1076:           data_type: VARCHAR
1077:         - name: response
1078:           data_type: VARCHAR
1079:         - name: scheduled_date
1080:           data_type: VARCHAR
1081:         - name: sold_to_contact_id
1082:           data_type: VARCHAR
1083:         - name: state
1084:           data_type: VARCHAR
1085:         - name: status
1086:           data_type: VARCHAR
1087:         - name: updated_by_id
1088:           data_type: BIGINT
1089:         - name: updated_date
1090:           data_type: TIMESTAMP
1091:         - name: is_most_recent_record
1092:           data_type: BOOLEAN
1093:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__order.sql`；SHA-256 `ee89858827b41cfe1d11a19e56874748ee91d5e2d4d9fc79f4bc347a41b882e9`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_order_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         try_cast("id" AS VARCHAR) AS order_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
9:         try_cast("category" AS VARCHAR) AS category,
10:         try_cast("created_by_id" AS BIGINT) AS created_by_id,
11:         try_cast("created_date" AS TIMESTAMP) AS created_date,
12:         try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
13:         try_cast("description" AS VARCHAR) AS description,
14:         try_cast("error_code" AS VARCHAR) AS error_code,
15:         try_cast("error_message" AS VARCHAR) AS error_message,
16:         try_cast("order_date" AS DATE) AS order_date,
17:         try_cast("order_number" AS VARCHAR) AS order_number,
18:         try_cast("response" AS VARCHAR) AS response,
19:         try_cast("scheduled_date" AS VARCHAR) AS scheduled_date,
20:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
21:         try_cast("state" AS VARCHAR) AS state,
22:         try_cast("status" AS VARCHAR) AS status,
23:         try_cast("updated_by_id" AS BIGINT) AS updated_by_id,
24:         try_cast("updated_date" AS TIMESTAMP) AS updated_date,
25:         row_number() over (partition by id order by try_cast(updated_date as timestamp) desc NULLS LAST) = 1 AS is_most_recent_record
26: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__order.sql`；SHA-256 `c4962b0495c46d2fc7ce31775d0fc559f2121961f015e9d5702272061e14f779`。

```text
1: with base as (
2:     select * from raw.zuora_order_data
3:     where _fivetran_deleted is null or _fivetran_deleted = false
4: ),
5: final as (
6:     select
7:         id as order_id,
8:         account_id,
9:         bill_to_contact_id,
10:         category,
11:         created_by_id,
12:         cast(created_date as TIMESTAMP) as created_date,
13:         default_payment_method_id,
14:         description,
15:         error_code,
16:         error_message,
17:         order_date,
18:         order_number,
19:         response,
20:         scheduled_date,
21:         sold_to_contact_id,
22:         state,
23:         status,
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_order_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_order_data","id","VARCHAR"],["zuora_order_data","_fivetran_deleted","BOOLEAN"],["zuora_order_data","_fivetran_synced","TIMESTAMP"],["zuora_order_data","account_id","VARCHAR"],["zuora_order_data","bill_to_contact_id","VARCHAR"],["zuora_order_data","created_by_id","BIGINT"],["zuora_order_data","created_by_migration","BOOLEAN"],["zuora_order_data","created_date","TIMESTAMP"],["zuora_order_data","default_payment_method_id","VARCHAR"],["zuora_order_data","description","VARCHAR"],["zuora_order_data","order_date","DATE"],["zuora_order_data","order_number","VARCHAR"],["zuora_order_data","parent_account_id","VARCHAR"],["zuora_order_data","sold_to_contact_id","VARCHAR"],["zuora_order_data","state","VARCHAR"],["zuora_order_data","status","VARCHAR"],["zuora_order_data","updated_by_id","BIGINT"],["zuora_order_data","updated_date","TIMESTAMP"],["zuora_order_data","category","VARCHAR"],["zuora_order_data","error_message","VARCHAR"],["zuora_order_data","scheduled_date_policy","VARCHAR"],["zuora_order_data","response","VARCHAR"],["zuora_order_data","error_code","VARCHAR"],["zuora_order_data","scheduled_date","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_order_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",5,5,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_order_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",5,0,2]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_order_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",5,5,0,2]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_order_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",5,5,5,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__order.json
[024_reruns_impl-030_stg_zuora__order.json](../024_reruns_impl-030_stg_zuora__order.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|5|否|
|L1|5|5|5|5|否|
|L2|5|5|5|5|否|
|L3|5|5|5|5|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5}`
- L1：`{"account_id":5}`
- L2：`{"account_id":5}`
- L3：`{"account_id":5}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__order/baseline.sql`；SHA-256 `ee89858827b41cfe1d11a19e56874748ee91d5e2d4d9fc79f4bc347a41b882e9`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|5|否|
|L1|5|5|5|5|否|
|L2|5|5|5|5|否|
|L3|5|5|5|5|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5}`
- L1：`{"account_id":5}`
- L2：`{"account_id":5}`
- L3：`{"account_id":5}`

#### source_account_id
主因；类别候选U。P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少5，格减少5。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第7行、offset 225起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__order/source_account_id.sql`；SHA-256 `e5ee26a3726fab5ef9e05decb3c9a76b4828ef0d314a0a7934eddf2adb04303e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|0|0|是|
|L1|5|5|0|0|是|
|L2|5|5|0|0|是|
|L3|5|5|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

