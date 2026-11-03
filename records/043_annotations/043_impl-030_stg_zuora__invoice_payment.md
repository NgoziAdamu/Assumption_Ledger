# 043：impl-030_stg_zuora__invoice_payment

## 结论

主要原因：**多因并列**；把握：中；只能组合修复：是。

所有逐点单改均不减少行或格，组合减少；不将零改善点记为参与因素。

层：staging。024旧主要原因原样保留：`多因并列（A、U）`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice_payment.sql`；无SQL注释。材料包：`records/024_packages/024_impl-030_stg_zuora__invoice_payment.md`。

本表直接raw源初始就为正常多列结构，最终执行仍为正常多列结构。 event19生成SQL时已见初始结构；event31运行原版run.py导入raw，event40确认展开后的列清单，event45的最终映射生成发生在此后。 初始与agent的run.py SHA-256相同，event10已展示单列按逗号拆分导入逻辑；不是agent另写修复原库。015确认gold与agent raw一致。正常结构不代表所有字段内容位置都符合语义，需逐列核实。

已逐张读取 `records/013_raw_impl-030.json`；与gold关系见 `records/015_raw_impl-030.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.zuora_invoice_payment_data`：initial 6行/29列；agent留存 6行/29列；013差异=False。

## 同源决定

同源决定：event 19，`/tmp/gen_stage.py`：统一按契约生成staging类型与表达式，event21/25修订，event45将pk_alias集合统一映射为本表id。 目录编号：`030-gen-stage`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 45，pk_alias集合中的外键名一律改取本表id；event19原先按正确同名列生成。 本表点：source_account_id, source_invoice_id, source_payment_id, source_payment_method_id；编号 `impl-030-event45-pk_alias`。

同源决定：event 19，staging统一按契约的type处理source_expression或同名源列，生成安全类型转换。 本表点：refund_type；编号 `030-contract-types`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共5条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引55（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `本实体id与各外键是否相同`：`records/024_queries.json` 数组索引56（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `候选外键匹配对照`：`records/024_queries.json` 数组索引57（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `外键字段格式诊断（原可见数据）`：`records/024_mapping_queries.json` 数组索引4（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `实际纳入行的候选映射`：`records/024_extra_diagnostics.json` 数组索引7（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 诊断 `多处组合仅诊断（不用于单点原因排名）`：`records/024_extra_diagnostics.json` 数组索引23（从0开始）。

- 诊断 `agent实际类型`：`records/024_diagnostics.json` 数组索引24（从0开始）。

- 诊断 `agent有限差异样例`：`records/024_diagnostics.json` 数组索引25（从0开始）。

- 诊断 `gold实际类型`：`records/024_diagnostics.json` 数组索引26（从0开始）。

- 诊断 `gold有限差异样例`：`records/024_diagnostics.json` 数组索引27（从0开始）。

组合诊断：`records/024_extra_diagnostics.json` 索引23，只改['source_account_id', 'source_invoice_id', 'source_payment_id', 'source_payment_method_id']；L0=6行/6格; L1=0行/0格; L2=0行/0格; L3=0行/0格。只用于确认组合改善，不冒充任何单点的收益。

## 点：source_account_id

类别：**Data Misconception**；角色：组合项；把握：高。

P：本表实体id可作为account_id对应目标实体的关系键。实际纳入6行，所选id匹配0，具名account_id匹配2；非空候选6个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。

证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。

P：本表实体id可作为account_id对应目标实体的关系键。

agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。

反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 4, "result": {"col": "account_id", "n": 6, "nonnull": 6, "hex32": 6, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 7, "result": {"col": "account_id", "n": 6, "nonnull": 6, "chosen_matches": 0, "named_matches": 2}}}`。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_payment.json`，条目 `source_account_id`。

基线：L0=12行/324格; L1=12行/324格; L2=12行/324格; L3=12行/324格。

单改后：L0=12行/324格; L1=12行/324格; L2=12行/324格; L3=12行/324格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 245
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
        - name: invoice_payment_id
          data_type: VARCHAR
        - name: account_id
          data_type: VARCHAR
        - name: account_receivable_accounting_code_id
          data_type: VARCHAR
        - name: accounting_period_id
          data_type: VARCHAR
        - name: amount
          data_type: DOUBLE
        - name: amount_currency_rounding
          data_type: BIGINT
        - name: amount_home_currency
          data_type: DOUBLE
        - name: bill_to_contact_id
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

## 点：source_invoice_id

类别：**Unstated Choice**；角色：组合项；把握：中。

契约未给invoice_id来源映射；实际纳入6行，所选id匹配6、具名列匹配0，非空6中ID格式6、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_payment.json`，条目 `source_invoice_id`。

基线：L0=12行/324格; L1=12行/324格; L2=12行/324格; L3=12行/324格。

单改后：L0=12行/324格; L1=12行/324格; L2=12行/324格; L3=12行/324格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS invoice_id",
    "new": "try_cast(\"invoice_id\" AS VARCHAR) AS invoice_id",
    "offset": 1254
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
        - name: home_currency
          data_type: VARCHAR
        - name: invoice_id
          data_type: VARCHAR
        - name: journal_entry_id
          data_type: VARCHAR
        - name: journal_run_id
          data_type: VARCHAR
        - name: parent_account_id
          data_type: VARCHAR
        - name: payment_id
          data_type: VARCHAR
        - name: payment_method_id
          data_type: VARCHAR
        - name: provider_exchange_rate_date
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

## 点：source_payment_id

类别：**Data Misconception**；角色：组合项；把握：高。

P：本表实体id可作为payment_id对应目标实体的关系键。实际纳入6行，所选id匹配0，具名payment_id匹配3；非空候选6个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。

证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。

P：本表实体id可作为payment_id对应目标实体的关系键。

agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。

反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 4, "result": {"col": "payment_id", "n": 6, "nonnull": 6, "hex32": 6, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 7, "result": {"col": "payment_id", "n": 6, "nonnull": 6, "chosen_matches": 0, "named_matches": 3}}}`。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_payment.json`，条目 `source_payment_id`。

基线：L0=12行/324格; L1=12行/324格; L2=12行/324格; L3=12行/324格。

单改后：L0=12行/324格; L1=12行/324格; L2=12行/324格; L3=12行/324格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS payment_id",
    "new": "try_cast(\"payment_id\" AS VARCHAR) AS payment_id",
    "offset": 1508
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
        - name: parent_account_id
          data_type: VARCHAR
        - name: payment_id
          data_type: VARCHAR
        - name: payment_method_id
          data_type: VARCHAR
        - name: provider_exchange_rate_date
          data_type: DATE
        - name: refund_amount
          data_type: BOOLEAN
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: transaction_currency
          data_type: VARCHAR
        - name: updated_by_id
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

## 点：source_payment_method_id

类别：**Data Misconception**；角色：组合项；把握：高。

P：本表实体id可作为payment_method_id对应目标实体的关系键。实际纳入6行，所选id匹配0，具名payment_method_id匹配4；非空候选6个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。

证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。

P：本表实体id可作为payment_method_id对应目标实体的关系键。

agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。

反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 4, "result": {"col": "payment_method_id", "n": 6, "nonnull": 6, "hex32": 6, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 7, "result": {"col": "payment_method_id", "n": 6, "nonnull": 6, "chosen_matches": 0, "named_matches": 4}}}`。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_payment.json`，条目 `source_payment_method_id`。

基线：L0=12行/324格; L1=12行/324格; L2=12行/324格; L3=12行/324格。

单改后：L0=12行/324格; L1=12行/324格; L2=12行/324格; L3=12行/324格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS payment_method_id",
    "new": "try_cast(\"payment_method_id\" AS VARCHAR) AS payment_method_id",
    "offset": 1557
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
        - name: payment_id
          data_type: VARCHAR
        - name: payment_method_id
          data_type: VARCHAR
        - name: provider_exchange_rate_date
          data_type: DATE
        - name: refund_amount
          data_type: BOOLEAN
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: transaction_currency
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
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

## 点：refund_type

类别：**其他**；角色：非原因；把握：高。

refund在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-030_stg_zuora__invoice_payment.json`，条目 `refund_type`。

基线：L0=12行/324格; L1=12行/324格; L2=12行/324格; L3=12行/324格。

单改后：L0=12行/324格; L1=12行/324格; L2=12行/324格; L3=12行/324格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"refund_amount\" AS BOOLEAN) AS refund_amount",
    "new": "refund_amount AS refund_amount",
    "offset": 1701
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第2档——交付物里只有通用说明**。类型冲突/安全转换只有通用说明，不能把invoice-item例子推广至本表/其他字段。

event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
        - name: provider_exchange_rate_date
          data_type: DATE
        - name: refund_amount
          data_type: BOOLEAN
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: transaction_currency
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
        - name: is_most_recent_record
          data_type: BOOLEAN
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
