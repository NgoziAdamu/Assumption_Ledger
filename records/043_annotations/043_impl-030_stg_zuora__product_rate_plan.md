# 043：impl-030_stg_zuora__product_rate_plan

## 结论

主要原因：**Data Misconception**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为4行/505格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`A`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__product_rate_plan.sql`；无SQL注释。材料包：`records/024_packages/024_impl-030_stg_zuora__product_rate_plan.md`。

本表直接raw源初始就为正常多列结构，最终执行仍为正常多列结构。 event19生成SQL时已见初始结构；event31运行原版run.py导入raw，event40确认展开后的列清单，event45的最终映射生成发生在此后。 初始与agent的run.py SHA-256相同，event10已展示单列按逗号拆分导入逻辑；不是agent另写修复原库。015确认gold与agent raw一致。正常结构不代表所有字段内容位置都符合语义，需逐列核实。

已逐张读取 `records/013_raw_impl-030.json`；与gold关系见 `records/015_raw_impl-030.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.zuora_product_rate_plan_data`：initial 1003行/14列；agent留存 1003行/14列；013差异=False。

## 同源决定

同源决定：event 19，`/tmp/gen_stage.py`：统一按契约生成staging类型与表达式，event21/25修订，event45将pk_alias集合统一映射为本表id。 目录编号：`030-gen-stage`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 19，staging统一按契约的type处理source_expression或同名源列，生成安全类型转换。 本表点：type_effective_end_date, type_effective_start_date；编号 `030-contract-types`。

同源决定：event 45，pk_alias集合中的外键名一律改取本表id；event19原先按正确同名列生成。 本表点：source_product_id；编号 `impl-030-event45-pk_alias`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共5条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引68（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `本实体id与各外键是否相同`：`records/024_queries.json` 数组索引69（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `候选外键匹配对照`：`records/024_queries.json` 数组索引70（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `外键字段格式诊断（原可见数据）`：`records/024_mapping_queries.json` 数组索引8（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `实际纳入行的候选映射`：`records/024_extra_diagnostics.json` 数组索引11（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：type_effective_end_date

类别：**其他**；角色：参与；把握：高。

effective_end_date在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__product_rate_plan.json`，条目 `type_effective_end_date`。

基线：L0=505行/1507格; L1=505行/1507格; L2=505行/1507格; L3=505行/505格。

单改后：L0=505行/1006格; L1=505行/1006格; L2=505行/1006格; L3=505行/505格。L0减量（先行后格）：0行/501格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"effective_end_date\" AS DATE) AS effective_end_date",
    "new": "\"effective_end_date\" AS effective_end_date",
    "offset": 409
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
        - name: description
          data_type: VARCHAR
        - name: effective_end_date
          data_type: DATE
        - name: effective_start_date
          data_type: DATE
        - name: name
          data_type: VARCHAR
        - name: product_id
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
          source_expression: "cast(updated_date as TIMESTAMP)"
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：type_effective_start_date

类别：**其他**；角色：参与；把握：高。

effective_start_date在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__product_rate_plan.json`，条目 `type_effective_start_date`。

基线：L0=505行/1507格; L1=505行/1507格; L2=505行/1507格; L3=505行/505格。

单改后：L0=505行/1006格; L1=505行/1006格; L2=505行/1006格; L3=505行/505格。L0减量（先行后格）：0行/501格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"effective_start_date\" AS DATE) AS effective_start_date",
    "new": "\"effective_start_date\" AS effective_start_date",
    "offset": 479
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
        - name: effective_end_date
          data_type: DATE
        - name: effective_start_date
          data_type: DATE
        - name: name
          data_type: VARCHAR
        - name: product_id
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
          source_expression: "cast(updated_date as TIMESTAMP)"
        - name: is_most_recent_record
          data_type: BOOLEAN
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：source_product_id

类别：**Data Misconception**；角色：主要；把握：中。

P：本表实体id可作为product_id对应目标实体的关系键。实际纳入505行，所选id匹配0，具名product_id匹配2；非空候选505个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。 目标覆盖仅2/505，支持该关系的匹配样本稀疏，因此把握为中；不另设类别最低匹配率门槛。

证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。

P：本表实体id可作为product_id对应目标实体的关系键。

agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。

反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 8, "result": {"col": "product_id", "n": 505, "nonnull": 505, "hex32": 505, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 11, "result": {"col": "product_id", "n": 505, "nonnull": 505, "chosen_matches": 0, "named_matches": 2}}}`。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__product_rate_plan.json`，条目 `source_product_id`。

基线：L0=505行/1507格; L1=505行/1507格; L2=505行/1507格; L3=505行/505格。

单改后：L0=501行/1002格; L1=501行/1002格; L2=501行/1002格; L3=0行/0格。L0减量（先行后格）：4行/505格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_id",
    "new": "try_cast(\"product_id\" AS VARCHAR) AS product_id",
    "offset": 598
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
        - name: name
          data_type: VARCHAR
        - name: product_id
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
          source_expression: "cast(updated_date as TIMESTAMP)"
        - name: is_most_recent_record
          data_type: BOOLEAN
          source_expression: "row_number() over (partition by id order by updated_date desc) = 1"
      row_filters:
        - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
          on_failure: delete_row
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
