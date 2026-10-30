# impl-030 · stg_zuora__rate_plan

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**多因并列（A、U）**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：无。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__rate_plan.md](../024_packages/024_impl-030_stg_zuora__rate_plan.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
658:     - name: stg_zuora__rate_plan
659:       description: "Cleaned rate plans; latest snapshot indicator."
660:       source_table: raw.zuora_rate_plan_data
661:       columns:
662:         - name: rate_plan_id
663:           data_type: VARCHAR
664:         - name: account_id
665:           data_type: VARCHAR
666:         - name: amendment_id
667:           data_type: VARCHAR
668:         - name: bill_to_contact_id
669:           data_type: VARCHAR
670:         - name: created_by_id
671:           data_type: VARCHAR
672:         - name: created_date
673:           data_type: TIMESTAMP
674:         - name: default_payment_method_id
675:           data_type: VARCHAR
676:         - name: name
677:           data_type: VARCHAR
678:         - name: original_rate_plan_id
679:           data_type: VARCHAR
680:         - name: product_id
681:           data_type: VARCHAR
682:         - name: product_rate_plan_id
683:           data_type: VARCHAR
684:         - name: sold_to_contact_id
685:           data_type: VARCHAR
686:         - name: subscription_id
687:           data_type: VARCHAR
688:         - name: updated_by_id
689:           data_type: VARCHAR
690:         - name: updated_date
691:           data_type: TIMESTAMP
692:         - name: is_most_recent_record
693:           data_type: BOOLEAN
694:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__rate_plan.sql`；SHA-256 `37fdd2e4e4c0f027edfb1b1a22b3685c6042e16e1973b2c8ded56675fce94f1e`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_rate_plan_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         try_cast("id" AS VARCHAR) AS rate_plan_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("id" AS VARCHAR) AS amendment_id,
9:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
10:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
11:         try_cast("created_date" AS TIMESTAMP) AS created_date,
12:         try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
13:         try_cast("name" AS VARCHAR) AS name,
14:         try_cast("original_rate_plan_id" AS VARCHAR) AS original_rate_plan_id,
15:         try_cast("id" AS VARCHAR) AS product_id,
16:         try_cast("id" AS VARCHAR) AS product_rate_plan_id,
17:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
18:         try_cast("id" AS VARCHAR) AS subscription_id,
19:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
20:         try_cast("updated_date" AS TIMESTAMP) AS updated_date,
21:         row_number() over (partition by id order by try_cast(updated_date as timestamp) desc NULLS LAST) = 1 AS is_most_recent_record
22: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__rate_plan.sql`；SHA-256 `c294ef739787de5121517b157bed428d9a4d98d46f82f06ba0252aff0ab956c4`。

```text
1: with base as (
2:     select * from raw.zuora_rate_plan_data
3:     where _fivetran_deleted is null or _fivetran_deleted = false
4: ),
5: final as (
6:     select
7:         id as rate_plan_id,
8:         account_id,
9:         amendment_id,
10:         bill_to_contact_id,
11:         created_by_id,
12:         cast(created_date as TIMESTAMP) as created_date,
13:         default_payment_method_id,
14:         name,
15:         original_rate_plan_id,
16:         product_id,
17:         product_rate_plan_id,
18:         sold_to_contact_id,
19:         subscription_id,
20:         updated_by_id,
21:         cast(updated_date as TIMESTAMP) as updated_date,
22:         row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
23:     from base
24: )
25: select * from final
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

- source_amendment_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
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

- source_product_rate_plan_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 product_rate_plan_id。
P：本实体id可替代product_rate_plan_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。

- source_subscription_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 subscription_id。
P：本实体id可替代subscription_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_rate_plan_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_rate_plan_data","id","VARCHAR"],["zuora_rate_plan_data","_fivetran_deleted","BOOLEAN"],["zuora_rate_plan_data","_fivetran_synced","TIMESTAMP"],["zuora_rate_plan_data","account_id","VARCHAR"],["zuora_rate_plan_data","amendment_id","VARCHAR"],["zuora_rate_plan_data","amendment_type","VARCHAR"],["zuora_rate_plan_data","bill_to_contact_id","VARCHAR"],["zuora_rate_plan_data","created_by_id","VARCHAR"],["zuora_rate_plan_data","created_date","TIMESTAMP"],["zuora_rate_plan_data","default_payment_method_id","VARCHAR"],["zuora_rate_plan_data","externally_managed_plan_id","VARCHAR"],["zuora_rate_plan_data","invoice_owner_id","VARCHAR"],["zuora_rate_plan_data","name","VARCHAR"],["zuora_rate_plan_data","parent_account_id","VARCHAR"],["zuora_rate_plan_data","product_id","VARCHAR"],["zuora_rate_plan_data","product_rate_plan_id","VARCHAR"],["zuora_rate_plan_data","sold_to_contact_id","VARCHAR"],["zuora_rate_plan_data","subscription_id","VARCHAR"],["zuora_rate_plan_data","subscription_owner_id","VARCHAR"],["zuora_rate_plan_data","subscription_version_amendment_id","VARCHAR"],["zuora_rate_plan_data","updated_by_id","VARCHAR"],["zuora_rate_plan_data","updated_date","TIMESTAMP"],["zuora_rate_plan_data","original_rate_plan_id","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_rate_plan_data UNION ALL SELECT 'amendment_id' col,count(*) n,count(amendment_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(amendment_id as varchar)) same_as_id FROM raw.zuora_rate_plan_data UNION ALL SELECT 'product_id' col,count(*) n,count(product_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(product_id as varchar)) same_as_id FROM raw.zuora_rate_plan_data UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(product_rate_plan_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(product_rate_plan_id as varchar)) same_as_id FROM raw.zuora_rate_plan_data UNION ALL SELECT 'subscription_id' col,count(*) n,count(subscription_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(subscription_id as varchar)) same_as_id FROM raw.zuora_rate_plan_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",5,5,0],["amendment_id",5,2,0],["product_id",5,5,0],["product_rate_plan_id",5,5,0],["subscription_id",5,5,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_data s UNION ALL SELECT 'amendment_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.amendment_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_data s UNION ALL SELECT 'product_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.product_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_data s UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.product_rate_plan_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_data s UNION ALL SELECT 'subscription_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.subscription_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",5,0,1],["amendment_id",5,0,0],["product_id",5,0,5],["product_rate_plan_id",5,0,1],["subscription_id",5,0,1]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_rate_plan_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'amendment_id' col,count(*) n,count(s.amendment_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.amendment_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'product_id' col,count(*) n,count(s.product_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.product_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(s.product_rate_plan_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.product_rate_plan_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'subscription_id' col,count(*) n,count(s.subscription_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.subscription_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",5,5,0,1],["amendment_id",5,2,0,0],["product_id",5,5,0,5],["product_rate_plan_id",5,5,0,1],["subscription_id",5,5,0,1]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_rate_plan_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'amendment_id' col,count(*) n,count(amendment_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(amendment_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(amendment_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'product_id' col,count(*) n,count(product_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(product_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(product_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(product_rate_plan_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(product_rate_plan_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(product_rate_plan_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'subscription_id' col,count(*) n,count(subscription_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(subscription_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(subscription_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",5,5,5,0],["amendment_id",5,2,2,0],["product_id",5,5,5,0],["product_rate_plan_id",5,5,5,0],["subscription_id",5,5,5,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__rate_plan.json
[024_reruns_impl-030_stg_zuora__rate_plan.json](../024_reruns_impl-030_stg_zuora__rate_plan.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|25|否|
|L1|5|5|5|25|否|
|L2|5|5|5|25|否|
|L3|5|5|5|25|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L1：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L2：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L3：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan/baseline.sql`；SHA-256 `37fdd2e4e4c0f027edfb1b1a22b3685c6042e16e1973b2c8ded56675fce94f1e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|25|否|
|L1|5|5|5|25|否|
|L2|5|5|5|25|否|
|L3|5|5|5|25|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L1：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L2：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L3：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`

#### source_account_id
主因；类别候选U。P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第7行、offset 233起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan/source_account_id.sql`；SHA-256 `f312df5877f8df59b4b758f4633e7d60f687ba157944be4a69e56227b3a6924e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|20|否|
|L1|5|5|5|20|否|
|L2|5|5|5|20|否|
|L3|5|5|5|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L1：`{"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L2：`{"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L3：`{"amendment_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`

#### source_amendment_id
主因；类别候选A。把本实体 id 当作 amendment_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第8行、offset 282起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS amendment_id
```

修改后：
```sql
try_cast("amendment_id" AS VARCHAR) AS amendment_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan/source_amendment_id.sql`；SHA-256 `51b42e8126fa1c39cf85ced4be0e2f30013f89b78ff4162f15e686e47d703426`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|20|否|
|L1|5|5|5|20|否|
|L2|5|5|5|20|否|
|L3|5|5|5|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L1：`{"account_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L2：`{"account_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L3：`{"account_id":5,"product_id":5,"product_rate_plan_id":5,"subscription_id":5}`

#### source_product_id
主因；类别候选U。P：本实体id可替代product_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第15行、offset 743起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS product_id
```

修改后：
```sql
try_cast("product_id" AS VARCHAR) AS product_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan/source_product_id.sql`；SHA-256 `2db295794513fa5c5b94a04482c7a0cb2dff51abe07a8c7975f23b522105a16e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|20|否|
|L1|5|5|5|20|否|
|L2|5|5|5|20|否|
|L3|5|5|5|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5,"amendment_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L1：`{"account_id":5,"amendment_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L2：`{"account_id":5,"amendment_id":5,"product_rate_plan_id":5,"subscription_id":5}`
- L3：`{"account_id":5,"amendment_id":5,"product_rate_plan_id":5,"subscription_id":5}`

#### source_product_rate_plan_id
主因；类别候选U。P：本实体id可替代product_rate_plan_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第16行、offset 792起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS product_rate_plan_id
```

修改后：
```sql
try_cast("product_rate_plan_id" AS VARCHAR) AS product_rate_plan_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan/source_product_rate_plan_id.sql`；SHA-256 `7830bc06cdc3c55a3ff77c19ae5965f7c60ee27054423d545a2d8adc76edbb01`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|20|否|
|L1|5|5|5|20|否|
|L2|5|5|5|20|否|
|L3|5|5|5|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5,"amendment_id":5,"product_id":5,"subscription_id":5}`
- L1：`{"account_id":5,"amendment_id":5,"product_id":5,"subscription_id":5}`
- L2：`{"account_id":5,"amendment_id":5,"product_id":5,"subscription_id":5}`
- L3：`{"account_id":5,"amendment_id":5,"product_id":5,"subscription_id":5}`

#### source_subscription_id
主因；类别候选U。P：本实体id可替代subscription_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第18行、offset 924起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS subscription_id
```

修改后：
```sql
try_cast("subscription_id" AS VARCHAR) AS subscription_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan/source_subscription_id.sql`；SHA-256 `bb6da91d461b7b728d09fe8add360c9eae84ed0b20a02fad5b6f8e14d1e50ecc`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|20|否|
|L1|5|5|5|20|否|
|L2|5|5|5|20|否|
|L3|5|5|5|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5}`
- L1：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5}`
- L2：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5}`
- L3：`{"account_id":5,"amendment_id":5,"product_id":5,"product_rate_plan_id":5}`
## 规则问题

无。

