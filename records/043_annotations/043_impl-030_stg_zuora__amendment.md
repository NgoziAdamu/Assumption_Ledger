# 043：impl-030_stg_zuora__amendment

## 结论

主要原因：**Unstated Choice**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为6行/267格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`A`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__amendment.sql`；无SQL注释。材料包：`records/024_packages/024_impl-030_stg_zuora__amendment.md`。

本表早期源检查处于坏结构（原始单列、header挤在列名中）；最终执行用正常展开结构。 event19生成SQL时已见初始结构；event31运行原版run.py导入raw，event40确认展开后的列清单，event45的最终映射生成发生在此后。本表展开列数见直接源对照。 初始与agent的run.py SHA-256相同，event10已展示单列按逗号拆分导入逻辑；不是agent另写修复原库。015确认gold与agent raw一致。正常结构不代表所有字段内容位置都符合语义，需逐列核实。

已逐张读取 `records/013_raw_impl-030.json`；与gold关系见 `records/015_raw_impl-030.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.zuora_amendment_data`：initial 505行/1列；agent留存 505行/33列；013差异=True。

## 同源决定

同源决定：event 19，`/tmp/gen_stage.py`：统一按契约生成staging类型与表达式，event21/25修订，event45将pk_alias集合统一映射为本表id。 目录编号：`030-gen-stage`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 19，staging统一按契约的type处理source_expression或同名源列，生成安全类型转换。 本表点：type_created_by_id；编号 `030-contract-types`。

同源决定：event 45，pk_alias集合中的外键名一律改取本表id；event19原先按正确同名列生成。 本表点：source_subscription_id；编号 `impl-030-event45-pk_alias`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共5条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引43（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `本实体id与各外键是否相同`：`records/024_queries.json` 数组索引44（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `候选外键匹配对照`：`records/024_queries.json` 数组索引45（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `外键字段格式诊断（原可见数据）`：`records/024_mapping_queries.json` 数组索引0（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `实际纳入行的候选映射`：`records/024_extra_diagnostics.json` 数组索引3（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：type_created_by_id

类别：**其他**；角色：参与；把握：高。

created_by_id在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__amendment.json`，条目 `type_created_by_id`。

基线：L0=267行/528格; L1=267行/528格; L2=267行/528格; L3=267行/528格。

单改后：L0=267行/267格; L1=267行/267格; L2=267行/267格; L3=267行/267格。L0减量（先行后格）：0行/261格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"created_by_id\" AS BIGINT) AS created_by_id",
    "new": "\"created_by_id\" AS created_by_id",
    "offset": 450
  }
]
```

是否说出：**第2档——交付物里只有通用说明**。类型冲突/安全转换只有通用说明，不能把invoice-item例子推广至本表/其他字段。

event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
        - name: contract_effective_date
          data_type: DATE
        - name: created_by_id
          data_type: BIGINT
        - name: created_date
          data_type: TIMESTAMP
          source_expression: "try_cast(created_date as TIMESTAMP)"
        - name: current_term
          data_type: VARCHAR
        - name: current_term_period_type
          data_type: VARCHAR
        - name: customer_acceptance_date
          data_type: DATE
        - name: description
          data_type: VARCHAR
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：source_subscription_id

类别：**Unstated Choice**；角色：主要；把握：中。

契约未给subscription_id来源映射；实际纳入267行，所选id匹配0、具名列匹配2，非空267中ID格式6、时间文本261。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__amendment.json`，条目 `source_subscription_id`。

基线：L0=267行/528格; L1=267行/528格; L2=267行/528格; L3=267行/528格。

单改后：L0=261行/261格; L1=261行/261格; L2=261行/261格; L3=261行/261格。L0减量（先行后格）：6行/267格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS subscription_id",
    "new": "try_cast(\"subscription_id\" AS VARCHAR) AS subscription_id",
    "offset": 1591
  }
]
```

是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。

event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
        - name: status
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: suspend_date
          data_type: VARCHAR
        - name: term_start_date
          data_type: VARCHAR
        - name: term_type
          data_type: VARCHAR
        - name: type
          data_type: VARCHAR
        - name: updated_by_id
          data_type: BIGINT
        - name: updated_date
```

event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```

event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
if n in pk_alias: srcname='id'
```


共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
