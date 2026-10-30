# impl-015 · stg_quickbooks__payment_line

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**D**；把握：高；主要错误点：linked_id。

存在 invoice_id 候选列，却将 linked_txn_payment_id 整列置 NULL。

参与因素：无。

标记：已披露。



## 材料与比较口径

精简材料包：[023_impl-015_stg_quickbooks__payment_line.md](../023_packages/023_impl-015_stg_quickbooks__payment_line.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml`；SHA-256 `c7c31842035fff7336164f7713a735dde48f8f77e19e992d2dae072b0144c51a`。
契约行 587–605：

```
587:     - name: stg_quickbooks__payment_line
588:       description: "Cleaned payment line items showing payment applications"
589:       source_table: "raw.payment_line_data"
590:       columns:
591:         - name: payment_id
592:           data_type: VARCHAR
593:           constraints: [not_null]
594:         - name: index
595:           data_type: INTEGER
596:           constraints: [not_null]
597:         - name: linked_txn_payment_id
598:           data_type: VARCHAR
599:         - name: amount
600:           data_type: DECIMAL(28,6)
601:         - name: source_relation
602:           data_type: VARCHAR
603:       filter_conditions:
604:         - "payment_id is not null and index is not null"
605:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/staging/stg_quickbooks__payment_line.sql`，SHA-256 `6d4d81039bb6df280d14d0f934b9481468fba77ec79e8efc286cf472755be841`，行 1–11。

```
1: WITH typed AS (
2:     SELECT
3:         CAST(r.payment_id AS VARCHAR) AS "payment_id",
4:         TRY_CAST(r.index AS INTEGER) AS "index",
5:         CAST(NULL AS VARCHAR) AS "linked_txn_payment_id",
6:         TRY_CAST(r.amount AS DECIMAL(28,6)) AS "amount",
7:         'quickbooks' AS "source_relation"
8:     FROM raw.payment_line_data AS r
9: )
10: SELECT * FROM typed
11: WHERE (payment_id IS NOT NULL AND index IS NOT NULL)
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/sql/staging/stg_quickbooks__payment_line.sql`，SHA-256 `a4e8ac66f3dcc79c155414891e68767225cd280333b0e7fcf2edd8defa78d100`，行 1–33。

```
1: with source as (
2:     select *
3:     from raw.payment_line_data
4: ),
5: 
6: renamed as (
7:     select
8:         -- IDs
9:         cast(payment_id as varchar) as payment_id,
10:         cast(index as integer) as index,
11:         cast(invoice_id as varchar) as linked_txn_payment_id,
12: 
13:         -- Financial data
14:         cast(amount as decimal(28,6)) as amount,
15: 
16:         -- System fields
17:         'main' as source_relation
18: 
19:     from source
20: )
21: 
22: select
23:     case when payment_id is null then '' else payment_id end as payment_id,
24:     index,
25:     linked_txn_payment_id,
26:     case
27:         when amount is not null and (amount < -999999.99 or amount > 999999.99)
28:         then null
29:         else amount
30:     end as amount,
31:     source_relation
32: from renamed
33: where payment_id is not null and index is not null
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

### 核实：候选 linked ID

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/quickbooks.duckdb`。

```sql
SELECT count(*) n,count(invoice_id) invoice_id_nonnull,count(distinct invoice_id) invoice_ids FROM raw.payment_line_data
```


```json
{"columns":["n","invoice_id_nonnull","invoice_ids"],"rows":[[6000,6000,6000]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-015_stg_quickbooks__payment_line.json](../023_reruns_impl-015_stg_quickbooks__payment_line.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/quickbooks.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6000|6000|12000|48000|否|
|L1|6000|6000|12000|48000|否|
|L2|6000|6000|12000|48000|否|
|L3|6000|6000|12000|48000|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"payment_id":12000,"linked_txn_payment_id":12000,"amount":12000,"index":12000}`
- L1：`{"payment_id":12000,"linked_txn_payment_id":12000,"amount":12000,"index":12000}`
- L2：`{"payment_id":12000,"linked_txn_payment_id":12000,"amount":12000,"index":12000}`
- L3：`{"payment_id":12000,"linked_txn_payment_id":12000,"amount":12000,"index":12000}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-015_stg_quickbooks__payment_line/baseline.sql`；SHA-256 `6d4d81039bb6df280d14d0f934b9481468fba77ec79e8efc286cf472755be841`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6000|6000|12000|48000|否|
|L1|6000|6000|12000|48000|否|
|L2|6000|6000|12000|48000|否|
|L3|6000|6000|12000|48000|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"payment_id":12000,"linked_txn_payment_id":12000,"amount":12000,"index":12000}`
- L1：`{"payment_id":12000,"linked_txn_payment_id":12000,"amount":12000,"index":12000}`
- L2：`{"payment_id":12000,"linked_txn_payment_id":12000,"amount":12000,"index":12000}`
- L3：`{"payment_id":12000,"linked_txn_payment_id":12000,"amount":12000,"index":12000}`

#### linked_id

判定：主因；类别候选 D。有 invoice_id 候选但直接整列占位。

相对本轮基线减少行 12000、格 48000；按行优先、格次之排序。
共同控制后 SQL 第 5 行起、字符 offset 139 的唯一连续替换；其余字节不动。
替换前：
```sql
CAST(NULL AS VARCHAR) AS "linked_txn_payment_id"
```

替换后：
```sql
CAST(r.invoice_id AS VARCHAR) AS "linked_txn_payment_id"
```

私有 SQL：`data/023_work/impl-015_stg_quickbooks__payment_line/linked_id.sql`；SHA-256 `0311d57e630a60b0120ffe24c6144a4fc54755b0de37f48922b2d65751484ab9`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6000|6000|0|0|是|
|L1|6000|6000|0|0|是|
|L2|6000|6000|0|0|是|
|L3|6000|6000|0|0|是|

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
