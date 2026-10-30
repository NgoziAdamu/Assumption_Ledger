# impl-030 · stg_zuora__amendment

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**A**；把握：中。

subscription_id的具名源267条中261条是时间文本，仅2条匹配subscription；数据不足以确定业务映射，归A。created_by_id按契约BIGINT但gold透传文本，另为O因素。

参与因素：O：type_created_by_id（行减0，格减261）。
标记：无。

## 材料与比较口径

[024_impl-030_stg_zuora__amendment.md](../024_packages/024_impl-030_stg_zuora__amendment.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
1239:     - name: stg_zuora__amendment
1240:       description: "Cleaned amendments with key dates and status; latest snapshot indicator."
1241:       source_table: raw.zuora_amendment_data
1242:       columns:
1243:         - name: amendment_id
1244:           data_type: VARCHAR
1245:           source_expression: "id"
1246:         - name: auto_renew
1247:           data_type: VARCHAR
1248:         - name: booking_date
1249:           data_type: DATE
1250:         - name: code
1251:           data_type: VARCHAR
1252:         - name: contract_effective_date
1253:           data_type: DATE
1254:         - name: created_by_id
1255:           data_type: BIGINT
1256:         - name: created_date
1257:           data_type: TIMESTAMP
1258:           source_expression: "try_cast(created_date as TIMESTAMP)"
1259:         - name: current_term
1260:           data_type: VARCHAR
1261:         - name: current_term_period_type
1262:           data_type: VARCHAR
1263:         - name: customer_acceptance_date
1264:           data_type: DATE
1265:         - name: description
1266:           data_type: VARCHAR
1267:         - name: effective_date
1268:           data_type: DATE
1269:         - name: name
1270:           data_type: VARCHAR
1271:         - name: new_rate_plan_id
1272:           data_type: VARCHAR
1273:         - name: removed_rate_plan_id
1274:           data_type: VARCHAR
1275:         - name: renewal_setting
1276:           data_type: VARCHAR
1277:         - name: renewal_term
1278:           data_type: VARCHAR
1279:         - name: renewal_term_period_type
1280:           data_type: VARCHAR
1281:         - name: resume_date
1282:           data_type: VARCHAR
1283:         - name: service_activation_date
1284:           data_type: DATE
1285:         - name: specific_update_date
1286:           data_type: VARCHAR
1287:         - name: status
1288:           data_type: VARCHAR
1289:         - name: subscription_id
1290:           data_type: VARCHAR
1291:         - name: suspend_date
1292:           data_type: VARCHAR
1293:         - name: term_start_date
1294:           data_type: VARCHAR
1295:         - name: term_type
1296:           data_type: VARCHAR
1297:         - name: type
1298:           data_type: VARCHAR
1299:         - name: updated_by_id
1300:           data_type: BIGINT
1301:         - name: updated_date
1302:           data_type: TIMESTAMP
1303:           source_expression: "try_cast(updated_date as TIMESTAMP)"
1304:         - name: is_most_recent_record
1305:           data_type: BOOLEAN
1306:           source_expression: "row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1"
1307:       row_filters:
1308:         - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
1309:           on_failure: delete_row
1310: 
1311: # --------------------------------------------------------------------------- #
1312: # PHASE 2: Defines the business logic from staging tables to analytical models.#
1313: # --------------------------------------------------------------------------- #
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__amendment.sql`；SHA-256 `124010a783c24801b2c595d93661e06ca2ba6c1e5744008e3d1dc2a13ca4a08e`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_amendment_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS amendment_id,
7:         try_cast("auto_renew" AS VARCHAR) AS auto_renew,
8:         try_cast("booking_date" AS DATE) AS booking_date,
9:         try_cast("code" AS VARCHAR) AS code,
10:         try_cast("contract_effective_date" AS DATE) AS contract_effective_date,
11:         try_cast("created_by_id" AS BIGINT) AS created_by_id,
12:         try_cast(created_date as TIMESTAMP) AS created_date,
13:         try_cast("current_term" AS VARCHAR) AS current_term,
14:         try_cast("current_term_period_type" AS VARCHAR) AS current_term_period_type,
15:         try_cast("customer_acceptance_date" AS DATE) AS customer_acceptance_date,
16:         try_cast("description" AS VARCHAR) AS description,
17:         try_cast("effective_date" AS DATE) AS effective_date,
18:         try_cast("name" AS VARCHAR) AS name,
19:         try_cast("new_rate_plan_id" AS VARCHAR) AS new_rate_plan_id,
20:         try_cast("removed_rate_plan_id" AS VARCHAR) AS removed_rate_plan_id,
21:         try_cast("renewal_setting" AS VARCHAR) AS renewal_setting,
22:         try_cast("renewal_term" AS VARCHAR) AS renewal_term,
23:         try_cast("renewal_term_period_type" AS VARCHAR) AS renewal_term_period_type,
24:         try_cast("resume_date" AS VARCHAR) AS resume_date,
25:         try_cast("service_activation_date" AS DATE) AS service_activation_date,
26:         try_cast("specific_update_date" AS VARCHAR) AS specific_update_date,
27:         try_cast("status" AS VARCHAR) AS status,
28:         try_cast("id" AS VARCHAR) AS subscription_id,
29:         try_cast("suspend_date" AS VARCHAR) AS suspend_date,
30:         try_cast("term_start_date" AS VARCHAR) AS term_start_date,
31:         try_cast("term_type" AS VARCHAR) AS term_type,
32:         try_cast("type" AS VARCHAR) AS type,
33:         try_cast("updated_by_id" AS BIGINT) AS updated_by_id,
34:         try_cast(updated_date as TIMESTAMP) AS updated_date,
35:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 AS is_most_recent_record
36: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__amendment.sql`；SHA-256 `3298c94b25033e6fb14f887045988f7ef3014f23fdb5eca44552dd22d785f5bf`。

```text
1: with base as (
2:     select * from raw.zuora_amendment_data where _fivetran_deleted is null or _fivetran_deleted = false
3: ),
4: final as (
5:     select
6:         id as amendment_id,
7:         auto_renew,
8:         booking_date,
9:         code,
10:         contract_effective_date,
11:         created_by_id,
12:         try_cast(created_date as TIMESTAMP) as created_date,
13:         current_term,
14:         current_term_period_type,
15:         customer_acceptance_date,
16:         description,
17:         effective_date,
18:         name,
19:         new_rate_plan_id,
20:         removed_rate_plan_id,
21:         renewal_setting,
22:         renewal_term,
23:         renewal_term_period_type,
24:         resume_date,
25:         service_activation_date,
26:         specific_update_date,
27:         status,
28:         subscription_id,
29:         suspend_date,
30:         term_start_date,
31:         term_type,
32:         type,
33:         updated_by_id,
34:         try_cast(updated_date as TIMESTAMP) as updated_date,
35:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 as is_most_recent_record
36:     from base
37: )
38: select * from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_amendment_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_amendment_data","id","VARCHAR"],["zuora_amendment_data","_fivetran_deleted","VARCHAR"],["zuora_amendment_data","_fivetran_synced","VARCHAR"],["zuora_amendment_data","auto_renew","VARCHAR"],["zuora_amendment_data","booking_date","VARCHAR"],["zuora_amendment_data","code","VARCHAR"],["zuora_amendment_data","contract_effective_date","VARCHAR"],["zuora_amendment_data","created_by_id","VARCHAR"],["zuora_amendment_data","created_date","VARCHAR"],["zuora_amendment_data","current_term","VARCHAR"],["zuora_amendment_data","current_term_period_type","VARCHAR"],["zuora_amendment_data","customer_acceptance_date","VARCHAR"],["zuora_amendment_data","description","VARCHAR"],["zuora_amendment_data","effective_date","VARCHAR"],["zuora_amendment_data","effective_policy","VARCHAR"],["zuora_amendment_data","name","VARCHAR"],["zuora_amendment_data","new_rate_plan_id","VARCHAR"],["zuora_amendment_data","removed_rate_plan_id","VARCHAR"],["zuora_amendment_data","renewal_setting","VARCHAR"],["zuora_amendment_data","renewal_term","VARCHAR"],["zuora_amendment_data","renewal_term_period_type","VARCHAR"],["zuora_amendment_data","resume_date","VARCHAR"],["zuora_amendment_data","service_activation_date","VARCHAR"],["zuora_amendment_data","specific_update_date","VARCHAR"],["zuora_amendment_data","status","VARCHAR"],["zuora_amendment_data","sub_type","VARCHAR"],["zuora_amendment_data","subscription_id","VARCHAR"],["zuora_amendment_data","suspend_date","VARCHAR"],["zuora_amendment_data","term_start_date","VARCHAR"],["zuora_amendment_data","term_type","VARCHAR"],["zuora_amendment_data","type","VARCHAR"],["zuora_amendment_data","updated_by_id","VARCHAR"],["zuora_amendment_data","updated_date","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'subscription_id' col,count(*) n,count(subscription_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(subscription_id as varchar)) same_as_id FROM raw.zuora_amendment_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["subscription_id",505,505,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'subscription_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.subscription_id as varchar))) named_col_matches FROM raw.zuora_amendment_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["subscription_id",505,0,2]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_amendment_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'subscription_id' col,count(*) n,count(s.subscription_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.subscription_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["subscription_id",267,267,0,2]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_amendment_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'subscription_id' col,count(*) n,count(subscription_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(subscription_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(subscription_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["subscription_id",267,267,6,261]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__amendment.json
[024_reruns_impl-030_stg_zuora__amendment.json](../024_reruns_impl-030_stg_zuora__amendment.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|267|267|267|528|否|
|L1|267|267|267|528|否|
|L2|267|267|267|528|否|
|L3|267|267|267|528|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_by_id":261,"subscription_id":267}`
- L1：`{"created_by_id":261,"subscription_id":267}`
- L2：`{"created_by_id":261,"subscription_id":267}`
- L3：`{"created_by_id":261,"subscription_id":267}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__amendment/baseline.sql`；SHA-256 `124010a783c24801b2c595d93661e06ca2ba6c1e5744008e3d1dc2a13ca4a08e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|267|267|267|528|否|
|L1|267|267|267|528|否|
|L2|267|267|267|528|否|
|L3|267|267|267|528|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_by_id":261,"subscription_id":267}`
- L1：`{"created_by_id":261,"subscription_id":267}`
- L2：`{"created_by_id":261,"subscription_id":267}`
- L3：`{"created_by_id":261,"subscription_id":267}`

#### type_created_by_id
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少261。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 450起替换；其他字节相同。
原表达式：
```sql
try_cast("created_by_id" AS BIGINT) AS created_by_id
```

修改后：
```sql
"created_by_id" AS created_by_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__amendment/type_created_by_id.sql`；SHA-256 `f14760c1a2d226142227a4c0e85523160d596d7f6cb7af137bb827e6d1404269`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|267|267|267|267|否|
|L1|267|267|267|267|否|
|L2|267|267|267|267|否|
|L3|267|267|267|267|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"subscription_id":267}`
- L1：`{"subscription_id":267}`
- L2：`{"subscription_id":267}`
- L3：`{"subscription_id":267}`

#### source_subscription_id
主因；类别候选A。把本实体 id 当作 subscription_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少6，格减少267。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第28行、offset 1591起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS subscription_id
```

修改后：
```sql
try_cast("subscription_id" AS VARCHAR) AS subscription_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__amendment/source_subscription_id.sql`；SHA-256 `a7d5f4e6d10c6abcf19a649fe2729c5022b99301ab499b9da6b20d56741e2775`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|267|267|261|261|否|
|L1|267|267|261|261|否|
|L2|267|267|261|261|否|
|L3|267|267|261|261|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_by_id":261}`
- L1：`{"created_by_id":261}`
- L2：`{"created_by_id":261}`
- L3：`{"created_by_id":261}`
## 规则问题

无。

