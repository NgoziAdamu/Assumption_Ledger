# impl-030 · stg_zuora__product_rate_plan

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**A**；把握：中。

product_id具名候选仅2/505匹配product，其余与所选id均无关系证据；契约未给映射，保守A。两处DATE与gold文本的O因素独立列出。

参与因素：O：type_effective_end_date（行减0，格减501）；O：type_effective_start_date（行减0，格减501）。
标记：无。

## 材料与比较口径

[024_impl-030_stg_zuora__product_rate_plan.md](../024_packages/024_impl-030_stg_zuora__product_rate_plan.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
624:     - name: stg_zuora__product_rate_plan
625:       description: "Cleaned product rate plans; latest snapshot indicator."
626:       source_table: raw.zuora_product_rate_plan_data
627:       columns:
628:         - name: product_rate_plan_id
629:           data_type: VARCHAR
630:           source_expression: "id"
631:         - name: created_by_id
632:           data_type: VARCHAR
633:         - name: created_date
634:           data_type: TIMESTAMP
635:           source_expression: "cast(created_date as TIMESTAMP)"
636:         - name: description
637:           data_type: VARCHAR
638:         - name: effective_end_date
639:           data_type: DATE
640:         - name: effective_start_date
641:           data_type: DATE
642:         - name: name
643:           data_type: VARCHAR
644:         - name: product_id
645:           data_type: VARCHAR
646:         - name: updated_by_id
647:           data_type: VARCHAR
648:         - name: updated_date
649:           data_type: TIMESTAMP
650:           source_expression: "cast(updated_date as TIMESTAMP)"
651:         - name: is_most_recent_record
652:           data_type: BOOLEAN
653:           source_expression: "row_number() over (partition by id order by updated_date desc) = 1"
654:       row_filters:
655:         - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
656:           on_failure: delete_row
657:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__product_rate_plan.sql`；SHA-256 `245c3885593c9c1c7af05170a6e75a7edb73d9dfcdef15fe7d174da674abfb89`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_product_rate_plan_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS product_rate_plan_id,
7:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
8:         try_cast(created_date as TIMESTAMP) AS created_date,
9:         try_cast("description" AS VARCHAR) AS description,
10:         try_cast("effective_end_date" AS DATE) AS effective_end_date,
11:         try_cast("effective_start_date" AS DATE) AS effective_start_date,
12:         try_cast("name" AS VARCHAR) AS name,
13:         try_cast("id" AS VARCHAR) AS product_id,
14:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
15:         try_cast(updated_date as TIMESTAMP) AS updated_date,
16:         row_number() over (partition by id order by updated_date desc) = 1 AS is_most_recent_record
17: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__product_rate_plan.sql`；SHA-256 `c1a842bce3547e377e50fb947e8ff4fd60f3cedcbdc84ec149712f72a2344955`。

```text
1: with base as (
2:     select * from raw.zuora_product_rate_plan_data
3:     where _fivetran_deleted is null or _fivetran_deleted = false
4: ),
5: final as (
6:     select
7:         id as product_rate_plan_id,
8:         created_by_id,
9:         cast(created_date as TIMESTAMP) as created_date,
10:         description,
11:         effective_end_date,
12:         effective_start_date,
13:         name,
14:         product_id,
15:         updated_by_id,
16:         cast(updated_date as TIMESTAMP) as updated_date,
17:         row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
18:     from base
19: )
20: select * from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- source_product_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_product_rate_plan_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_product_rate_plan_data","id","VARCHAR"],["zuora_product_rate_plan_data","_fivetran_deleted","VARCHAR"],["zuora_product_rate_plan_data","_fivetran_synced","VARCHAR"],["zuora_product_rate_plan_data","created_by_id","VARCHAR"],["zuora_product_rate_plan_data","created_date","VARCHAR"],["zuora_product_rate_plan_data","description","VARCHAR"],["zuora_product_rate_plan_data","effective_end_date","VARCHAR"],["zuora_product_rate_plan_data","effective_start_date","VARCHAR"],["zuora_product_rate_plan_data","external_id_source_system","VARCHAR"],["zuora_product_rate_plan_data","name","VARCHAR"],["zuora_product_rate_plan_data","product_id","VARCHAR"],["zuora_product_rate_plan_data","promotion_code_c","VARCHAR"],["zuora_product_rate_plan_data","updated_by_id","VARCHAR"],["zuora_product_rate_plan_data","updated_date","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'product_id' col,count(*) n,count(product_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(product_id as varchar)) same_as_id FROM raw.zuora_product_rate_plan_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["product_id",1003,1003,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'product_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.product_id as varchar))) named_col_matches FROM raw.zuora_product_rate_plan_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["product_id",1003,0,2]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_product_rate_plan_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'product_id' col,count(*) n,count(s.product_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.product_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["product_id",505,505,0,2]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_product_rate_plan_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'product_id' col,count(*) n,count(product_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(product_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(product_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["product_id",505,505,505,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__product_rate_plan.json
[024_reruns_impl-030_stg_zuora__product_rate_plan.json](../024_reruns_impl-030_stg_zuora__product_rate_plan.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|505|505|505|1507|否|
|L1|505|505|505|1507|否|
|L2|505|505|505|1507|否|
|L3|505|505|505|505|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"effective_end_date":501,"effective_start_date":501,"product_id":505}`
- L1：`{"effective_end_date":501,"effective_start_date":501,"product_id":505}`
- L2：`{"effective_end_date":501,"effective_start_date":501,"product_id":505}`
- L3：`{"product_id":505}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__product_rate_plan/baseline.sql`；SHA-256 `245c3885593c9c1c7af05170a6e75a7edb73d9dfcdef15fe7d174da674abfb89`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|505|505|505|1507|否|
|L1|505|505|505|1507|否|
|L2|505|505|505|1507|否|
|L3|505|505|505|505|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"effective_end_date":501,"effective_start_date":501,"product_id":505}`
- L1：`{"effective_end_date":501,"effective_start_date":501,"product_id":505}`
- L2：`{"effective_end_date":501,"effective_start_date":501,"product_id":505}`
- L3：`{"product_id":505}`

#### type_effective_end_date
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少501。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第10行、offset 409起替换；其他字节相同。
原表达式：
```sql
try_cast("effective_end_date" AS DATE) AS effective_end_date
```

修改后：
```sql
"effective_end_date" AS effective_end_date
```

私有SQL：`data/024_work/impl-030_stg_zuora__product_rate_plan/type_effective_end_date.sql`；SHA-256 `1433b1a521a3abefad97d1204e86a9f721b52896afc13ec160df6c8fd30f469c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|505|505|505|1006|否|
|L1|505|505|505|1006|否|
|L2|505|505|505|1006|否|
|L3|505|505|505|505|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"effective_start_date":501,"product_id":505}`
- L1：`{"effective_start_date":501,"product_id":505}`
- L2：`{"effective_start_date":501,"product_id":505}`
- L3：`{"product_id":505}`

#### type_effective_start_date
参与因素；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少501。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 479起替换；其他字节相同。
原表达式：
```sql
try_cast("effective_start_date" AS DATE) AS effective_start_date
```

修改后：
```sql
"effective_start_date" AS effective_start_date
```

私有SQL：`data/024_work/impl-030_stg_zuora__product_rate_plan/type_effective_start_date.sql`；SHA-256 `7e278f7f5f258e6faee2bcece311e0472dd83599b58aa57a4c23e6a45d079d25`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|505|505|505|1006|否|
|L1|505|505|505|1006|否|
|L2|505|505|505|1006|否|
|L3|505|505|505|505|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"effective_end_date":501,"product_id":505}`
- L1：`{"effective_end_date":501,"product_id":505}`
- L2：`{"effective_end_date":501,"product_id":505}`
- L3：`{"product_id":505}`

#### source_product_id
主因；类别候选A。把本实体 id 当作 product_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少4，格减少505。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第13行、offset 598起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS product_id
```

修改后：
```sql
try_cast("product_id" AS VARCHAR) AS product_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__product_rate_plan/source_product_id.sql`；SHA-256 `c26cb0ad2976e918548004cc2f1e1ad384b0ae0e7fcd6b6c68dfd8ecda1beadc`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|505|505|501|1002|否|
|L1|505|505|501|1002|否|
|L2|505|505|501|1002|否|
|L3|505|505|0|0|是|

首次整表匹配：**L3**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"effective_end_date":501,"effective_start_date":501}`
- L1：`{"effective_end_date":501,"effective_start_date":501}`
- L2：`{"effective_end_date":501,"effective_start_date":501}`
- L3：`{}`
## 规则问题

无。

