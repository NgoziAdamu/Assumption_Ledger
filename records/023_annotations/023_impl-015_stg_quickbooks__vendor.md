# impl-015 · stg_quickbooks__vendor

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**D**；把握：高；主要错误点：vendor_name。

存在 display_name 等名称候选列，却将 name 整列置 NULL。

参与因素：无。

标记：已披露。



## 材料与比较口径

精简材料包：[023_impl-015_stg_quickbooks__vendor.md](../023_packages/023_impl-015_stg_quickbooks__vendor.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml`；SHA-256 `c7c31842035fff7336164f7713a735dde48f8f77e19e992d2dae072b0144c51a`。
契约行 606–652：

```
606:     - name: stg_quickbooks__vendor
607:       description: "Cleaned vendor information with standardized contact details and payment terms"
608:       source_table: "raw.vendor_data"
609:       columns:
610:         - name: vendor_id
611:           data_type: VARCHAR
612:           constraints: [not_null]
613:         - name: currency_id
614:           data_type: VARCHAR
615:         - name: sales_term_id
616:           data_type: VARCHAR
617:         - name: tax_code_id
618:           data_type: VARCHAR
619:         - name: name
620:           data_type: VARCHAR
621:           constraints: [not_null]
622:         - name: display_name
623:           data_type: VARCHAR
624:           constraints: [not_null]
625:         - name: company_name
626:           data_type: VARCHAR
627:         - name: print_on_check_name
628:           data_type: VARCHAR
629:         - name: vendor_1099
630:           data_type: VARCHAR
631:         - name: balance
632:           data_type: DECIMAL(28,6)
633:         - name: acct_num
634:           data_type: VARCHAR
635:         - name: is_active
636:           data_type: BOOLEAN
637:           constraints: [not_null]
638:         - name: is_taxable
639:           data_type: BOOLEAN
640:         - name: created_at
641:           data_type: TIMESTAMP
642:         - name: updated_at
643:           data_type: TIMESTAMP
644:         - name: sync_token
645:           data_type: VARCHAR
646:         - name: source_relation
647:           data_type: VARCHAR
648: 
649:           
650: # --------------------------------------------------------------------------- #
651: # PHASE 2: Defines the business logic from staging tables to analytical models. #
652: # --------------------------------------------------------------------------- #
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/staging/stg_quickbooks__vendor.sql`，SHA-256 `9ddbba48c468abc9ea4e6b27c803eea775129be053fe2e4cea53d8b65d230590`，行 1–22。

```
1: WITH typed AS (
2:     SELECT
3:         CAST(r.id AS VARCHAR) AS "vendor_id",
4:         CAST(r.currency_id AS VARCHAR) AS "currency_id",
5:         CAST(r.term_id AS VARCHAR) AS "sales_term_id",
6:         CAST(NULL AS VARCHAR) AS "tax_code_id",
7:         CAST(NULL AS VARCHAR) AS "name",
8:         CAST(r.display_name AS VARCHAR) AS "display_name",
9:         CAST(r.company_name AS VARCHAR) AS "company_name",
10:         CAST(r.print_on_check_name AS VARCHAR) AS "print_on_check_name",
11:         CAST(r.vendor_1099 AS VARCHAR) AS "vendor_1099",
12:         TRY_CAST(r.balance AS DECIMAL(28,6)) AS "balance",
13:         CAST(r.account_number AS VARCHAR) AS "acct_num",
14:         TRY_CAST(r.active AS BOOLEAN) AS "is_active",
15:         CAST(NULL AS BOOLEAN) AS "is_taxable",
16:         TRY_CAST(r.created_at AS TIMESTAMP) AS "created_at",
17:         TRY_CAST(r.updated_at AS TIMESTAMP) AS "updated_at",
18:         CAST(r.sync_token AS VARCHAR) AS "sync_token",
19:         'quickbooks' AS "source_relation"
20:     FROM raw.vendor_data AS r
21: )
22: SELECT * FROM typed
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/sql/staging/stg_quickbooks__vendor.sql`，SHA-256 `5f6c91cecef8011f822daf02270d36a5402665a41e274b9dc1dafef86d3fdc56`，行 1–63。

```
1: with source as (
2:     select *
3:     from raw.vendor_data
4: ),
5: 
6: renamed as (
7:     select
8:         -- IDs
9:         cast(id as varchar) as vendor_id,
10:         cast(currency_id as varchar) as currency_id,
11:         cast(term_id as varchar) as sales_term_id,
12:         cast(null as varchar) as tax_code_id,
13: 
14:         -- Vendor details
15:         cast(display_name as varchar) as name_raw,
16:         cast(display_name as varchar) as display_name_raw,
17:         cast(company_name as varchar) as company_name,
18:         cast(print_on_check_name as varchar) as print_on_check_name,
19:         cast(vendor_1099 as varchar) as vendor_1099,
20: 
21:         -- Financial data
22:         cast(balance as decimal(28,6)) as balance,
23:         cast(account_number as varchar) as acct_num,
24: 
25:         -- Flags
26:         cast(active as boolean) as is_active,
27:         cast(null as boolean) as is_taxable,
28: 
29:         -- Dates
30:         strptime(created_at, '%Y-%m-%d %H:%M:%S.%f %z') as created_at,
31:         strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f %z') as updated_at,
32: 
33:         -- System fields
34:         cast(sync_token as varchar) as sync_token,
35:         'main' as source_relation
36: 
37:     from source
38: )
39: 
40: select
41:     vendor_id,
42:     currency_id,
43:     sales_term_id,
44:     tax_code_id,
45:     case when name_raw is null then '' else name_raw end as name,
46:     case when display_name_raw is null then '' else display_name_raw end as display_name,
47:     company_name,
48:     print_on_check_name,
49:     vendor_1099,
50:     case
51:         when balance is not null and (balance < -999999.99 or balance > 999999.99)
52:         then null
53:         else balance
54:     end as balance,
55:     acct_num,
56:     case when is_active is null then false else is_active end as is_active,
57:     case when is_taxable is null then false else is_taxable end as is_taxable,
58:     created_at,
59:     updated_at,
60:     sync_token,
61:     source_relation
62: from renamed
63: where vendor_id is not null and name_raw is not null and display_name_raw is not null and is_active is not null
```

## 轨迹可见性与不确定性

**四档：只有通用策略说明**。

event 15/16 已看到源列清单；event 21 仅按原同名列是否存在走 NULL fallback，未判断候选映射。event 73：「对原始字段中不存在的合同字段采用类型化 NULL」。这是跨表占位策略，非本表映射理由。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/15.json`。
- event 16：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/16.json`。
- event 21：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/21.json`。
- event 73：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/73.json`。

event 73 最终报告原文（用于检查说明是否超出工作清单）：

```
【回复用户】

已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 QuickBooks SQL 流水线，文件按要求保存在 `sql/staging/`、`sql/intermediate/`、`sql/marts/`，共 29 个 SQL 文件。SQL 使用 DuckDB 语法、显式 schema.table 上游引用，不含 dbt `ref()`，文件末尾不含分号。

**验证结果**
- 执行 `python run.py` 成功，三个层均全部构建：staging 13/13、intermediate 9/9、marts 7/7。
- 输出数据库 `quickbooks.duckdb` 已成功生成。
- 基础数据检查通过：关键 staging 主键及收入分析 invoice_id 无 NULL；收入分析 invoice_id 唯一；cashflow 预期日期无 NULL。
- 观测行数：staging 包含 account 449、bill 5,000、bill line 12,000、customer 3,000、invoice 8,000、invoice line 20,000、payment 6,000 等记录；intermediate 和 marts 均成功产出。

**质量处理及说明**
- Staging 使用 `TRY_CAST` 转换源字段，无法转换的值变为 NULL；按合同过滤无效关键记录及非法账户类型。按模型粒度保留源重复记录，不擅自去重；重复源数据可能使下游连接产生重复行。
- 对原始字段中不存在的合同字段采用类型化 NULL；对 `source_relation` 使用常量 `quickbooks`，因为原始 QuickBooks 表没有该字段。这是适配现有源结构的最小安全假设。
- `quickbooks__cashflow_forecast` 本次运行结果为 0 行，因为未来 12 个月内没有符合合同筛选条件的正数未结余额；这是筛选结果，不是构建失败。
- 为使指定的 `run.py` 成功加载 raw 数据，修复了对同一 DuckDB 文件重复 ATTACH 导致的 `Unique file handle conflict`：改为从已打开的源连接读取并复制至目标库。此执行器兼容修正未改变 SQL 模型逻辑。

本次最终运行无失败 SQL；运行日志显示流水线成功完成。
```

## 查询

核实查询 **3** 条；核实代价档：**多条查询**。诊断查询不计入 5 条上限。

计数保守包含最初额外 2 条结构/少量样例查看。该探索未保留完整返回，不作为分类证据；下列聚合查询独立给出判断所需证据。

### 核实：候选名称

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/quickbooks.duckdb`。

```sql
SELECT count(*) n,count(display_name) display_name_nonnull,count(company_name) company_name_nonnull FROM raw.vendor_data
```


```json
{"columns":["n","display_name_nonnull","company_name_nonnull"],"rows":[[1500,1500,1500]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-015_stg_quickbooks__vendor.json](../023_reruns_impl-015_stg_quickbooks__vendor.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/quickbooks.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|1500|1500|否|
|L1|1500|1500|1500|1500|否|
|L2|1500|1500|1500|1500|否|
|L3|1500|1500|1500|1500|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"name":1500}`
- L1：`{"name":1500}`
- L2：`{"name":1500}`
- L3：`{"name":1500}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-015_stg_quickbooks__vendor/baseline.sql`；SHA-256 `9ddbba48c468abc9ea4e6b27c803eea775129be053fe2e4cea53d8b65d230590`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|1500|1500|否|
|L1|1500|1500|1500|1500|否|
|L2|1500|1500|1500|1500|否|
|L3|1500|1500|1500|1500|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"name":1500}`
- L1：`{"name":1500}`
- L2：`{"name":1500}`
- L3：`{"name":1500}`

#### vendor_name

判定：主因；类别候选 D。存在 display_name 候选，name 整列占位。

相对本轮基线减少行 1500、格 1500；按行优先、格次之排序。
共同控制后 SQL 第 7 行起、字符 offset 241 的唯一连续替换；其余字节不动。
替换前：
```sql
CAST(NULL AS VARCHAR) AS "name"
```

替换后：
```sql
CAST(r.display_name AS VARCHAR) AS "name"
```

私有 SQL：`data/023_work/impl-015_stg_quickbooks__vendor/vendor_name.sql`；SHA-256 `8c47679947b95a48cd3fc4ba4dc92f91602f21ad8ca063d2e11f3cb9347d677d`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1500|1500|0|0|是|
|L1|1500|1500|0|0|是|
|L2|1500|1500|0|0|是|
|L3|1500|1500|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 原始表改动核对

event 39/40、43/44 报告 Unique file handle conflict；event45 改为 fetchdf/register/CREATE TABLE 导入，event46 成功。raw 类型改变但本次相关 invoice/vendor 表内容哈希相同。

初始/gold 一致而 agent 有变化，依第 3 节照常标注，不标不可评估。完整表清单见 [023_raw_trace_review.json](../023_raw_trace_review.json)；输入不变性另由前后指纹验证。

## 规则问题

无
