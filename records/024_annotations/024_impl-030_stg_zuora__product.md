# impl-030 · stg_zuora__product

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

契约两个有效日期为DATE，gold保留含时刻VARCHAR；两处各减少160格且L3消失。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-030_stg_zuora__product.md](../024_packages/024_impl-030_stg_zuora__product.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
588:     - name: stg_zuora__product
589:       description: "Cleaned products; latest snapshot indicator provided."
590:       source_table: raw.zuora_product_data
591:       columns:
592:         - name: product_id
593:           data_type: VARCHAR
594:           source_expression: "id"
595:         - name: category
596:           data_type: VARCHAR
597:         - name: created_by_id
598:           data_type: VARCHAR
599:         - name: created_date
600:           data_type: TIMESTAMP
601:           source_expression: "cast(created_date as TIMESTAMP)"
602:         - name: description
603:           data_type: VARCHAR
604:         - name: effective_end_date
605:           data_type: DATE
606:         - name: effective_start_date
607:           data_type: DATE
608:         - name: name
609:           data_type: VARCHAR
610:         - name: sku
611:           data_type: VARCHAR
612:         - name: updated_by_id
613:           data_type: VARCHAR
614:         - name: updated_date
615:           data_type: TIMESTAMP
616:           source_expression: "cast(updated_date as TIMESTAMP)"
617:         - name: is_most_recent_record
618:           data_type: BOOLEAN
619:           source_expression: "row_number() over (partition by id order by updated_date desc) = 1"
620:       row_filters:
621:         - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
622:           on_failure: delete_row
623:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__product.sql`；SHA-256 `bcbd5baa6966face41e3c2096e9092d75fc5332df949d71bf0712cd0f60dcb13`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_product_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS product_id,
7:         try_cast("category" AS VARCHAR) AS category,
8:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
9:         try_cast(created_date as TIMESTAMP) AS created_date,
10:         try_cast("description" AS VARCHAR) AS description,
11:         try_cast("effective_end_date" AS DATE) AS effective_end_date,
12:         try_cast("effective_start_date" AS DATE) AS effective_start_date,
13:         try_cast("name" AS VARCHAR) AS name,
14:         try_cast("sku" AS VARCHAR) AS sku,
15:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
16:         try_cast(updated_date as TIMESTAMP) AS updated_date,
17:         row_number() over (partition by id order by updated_date desc) = 1 AS is_most_recent_record
18: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__product.sql`；SHA-256 `ec805281f536a9df3875e2bd37658c7b6bf1178ab63ee6bddc91a10800a2a6e7`。

```text
1: with base as (
2:     select * from raw.zuora_product_data
3:     where _fivetran_deleted is null or _fivetran_deleted = false
4: ),
5: final as (
6:     select
7:         id as product_id,
8:         category,
9:         created_by_id,
10:         cast(created_date as TIMESTAMP) as created_date,
11:         description,
12:         effective_end_date,
13:         effective_start_date,
14:         name,
15:         sku,
16:         updated_by_id,
17:         cast(updated_date as TIMESTAMP) as updated_date,
18:         row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
19:     from base
20: )
21: select * from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- type_effective_end_date（O）：**只有通用策略说明**；事件 69。
原句：

```
非关键不可解析值转为 NULL。
```


- type_effective_start_date（O）：**只有通用策略说明**；事件 69。
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_product_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_product_data","id","VARCHAR"],["zuora_product_data","_fivetran_deleted","VARCHAR"],["zuora_product_data","_fivetran_synced","VARCHAR"],["zuora_product_data","allow_feature_changes","VARCHAR"],["zuora_product_data","category","VARCHAR"],["zuora_product_data","created_by_id","VARCHAR"],["zuora_product_data","created_date","VARCHAR"],["zuora_product_data","description","VARCHAR"],["zuora_product_data","effective_end_date","VARCHAR"],["zuora_product_data","effective_start_date","VARCHAR"],["zuora_product_data","name","VARCHAR"],["zuora_product_data","sku","VARCHAR"],["zuora_product_data","updated_by_id","VARCHAR"],["zuora_product_data","updated_date","VARCHAR"]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__product.json
[024_reruns_impl-030_stg_zuora__product.json](../024_reruns_impl-030_stg_zuora__product.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|164|164|160|320|否|
|L1|164|164|160|320|否|
|L2|164|164|160|320|否|
|L3|164|164|0|0|是|

首次整表匹配：**L3**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"effective_end_date":160,"effective_start_date":160}`
- L1：`{"effective_end_date":160,"effective_start_date":160}`
- L2：`{"effective_end_date":160,"effective_start_date":160}`
- L3：`{}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__product/baseline.sql`；SHA-256 `bcbd5baa6966face41e3c2096e9092d75fc5332df949d71bf0712cd0f60dcb13`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|164|164|160|320|否|
|L1|164|164|160|320|否|
|L2|164|164|160|320|否|
|L3|164|164|0|0|是|

首次整表匹配：**L3**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"effective_end_date":160,"effective_start_date":160}`
- L1：`{"effective_end_date":160,"effective_start_date":160}`
- L2：`{"effective_end_date":160,"effective_start_date":160}`
- L3：`{}`

#### type_effective_end_date
主因；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少160。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第11行、offset 442起替换；其他字节相同。
原表达式：
```sql
try_cast("effective_end_date" AS DATE) AS effective_end_date
```

修改后：
```sql
"effective_end_date" AS effective_end_date
```

私有SQL：`data/024_work/impl-030_stg_zuora__product/type_effective_end_date.sql`；SHA-256 `e98ce4fe990d89b928504483d765cce4a27a07e318cfc1e7802a288ab13ad1b4`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|164|164|160|160|否|
|L1|164|164|160|160|否|
|L2|164|164|160|160|否|
|L3|164|164|0|0|是|

首次整表匹配：**L3**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"effective_start_date":160}`
- L1：`{"effective_start_date":160}`
- L2：`{"effective_start_date":160}`
- L3：`{}`

#### type_effective_start_date
主因；类别候选O。agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。
相对本轮基线：行减少0，格减少160。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第12行、offset 512起替换；其他字节相同。
原表达式：
```sql
try_cast("effective_start_date" AS DATE) AS effective_start_date
```

修改后：
```sql
"effective_start_date" AS effective_start_date
```

私有SQL：`data/024_work/impl-030_stg_zuora__product/type_effective_start_date.sql`；SHA-256 `0d7e80111d579fbaecebf8ff61023563348ae1ce0ca256eaf3ae52490241f728`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|164|164|160|160|否|
|L1|164|164|160|160|否|
|L2|164|164|160|160|否|
|L3|164|164|0|0|是|

首次整表匹配：**L3**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"effective_end_date":160}`
- L1：`{"effective_end_date":160}`
- L2：`{"effective_end_date":160}`
- L3：`{}`
## 规则问题

无。

