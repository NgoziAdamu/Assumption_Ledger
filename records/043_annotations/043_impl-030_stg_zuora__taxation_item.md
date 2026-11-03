# 043：impl-030_stg_zuora__taxation_item

## 结论

主要原因：**多因并列**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为0行/534格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`多因并列（A、O、U）`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__taxation_item.sql`；无SQL注释。材料包：`records/024_packages/024_impl-030_stg_zuora__taxation_item.md`。

本表早期源检查处于坏结构（原始单列、header挤在列名中）；最终执行用正常展开结构。 event19生成SQL时已见初始结构；event31运行原版run.py导入raw，event40确认展开后的列清单，event45的最终映射生成发生在此后。本表展开列数见直接源对照。 初始与agent的run.py SHA-256相同，event10已展示单列按逗号拆分导入逻辑；不是agent另写修复原库。015确认gold与agent raw一致。正常结构不代表所有字段内容位置都符合语义，需逐列核实。

已逐张读取 `records/013_raw_impl-030.json`；与gold关系见 `records/015_raw_impl-030.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.zuora_taxation_item_data`：initial 1005行/1列；agent留存 1005行/56列；013差异=True。

## 同源决定

同源决定：event 19，`/tmp/gen_stage.py`：统一按契约生成staging类型与表达式，event21/25修订，event45将pk_alias集合统一映射为本表id。 目录编号：`030-gen-stage`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 45，pk_alias集合中的外键名一律改取本表id；event19原先按正确同名列生成。 本表点：source_account_id, source_amendment_id, source_invoice_id, source_invoice_item_id, source_product_id, source_product_rate_plan_id, source_rate_plan_charge_id, source_rate_plan_id, source_subscription_id；编号 `impl-030-event45-pk_alias`。

同源决定：event 19，staging统一按契约的type处理source_expression或同名源列，生成安全类型转换。 本表点：type_balance, type_credit_amount, type_exempt_amount, type_payment_amount, type_tax_rate；编号 `030-contract-types`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共5条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引83（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `本实体id与各外键是否相同`：`records/024_queries.json` 数组索引84（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `候选外键匹配对照`：`records/024_queries.json` 数组索引85（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `外键字段格式诊断（原可见数据）`：`records/024_mapping_queries.json` 数组索引13（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `实际纳入行的候选映射`：`records/024_extra_diagnostics.json` 数组索引16（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：source_account_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给account_id来源映射；实际纳入534行，所选id匹配0、具名列匹配0，非空534中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `source_account_id`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5350格; L1=534行/5330格; L2=534行/5330格; L3=534行/5330格。L0减量（先行后格）：0行/534格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 218
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
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: account_receivable_accounting_code_id
          data_type: VARCHAR
        - name: accounting_code
          data_type: VARCHAR
        - name: amendment_id
          data_type: VARCHAR
        - name: balance
          data_type: BIGINT
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: created_by_id
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

## 点：source_amendment_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给amendment_id来源映射；实际纳入534行，所选id匹配0、具名列匹配0，非空534中ID格式529、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `source_amendment_id`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5350格; L1=534行/5330格; L2=534行/5330格; L3=534行/5330格。L0减量（先行后格）：0行/534格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS amendment_id",
    "new": "try_cast(\"amendment_id\" AS VARCHAR) AS amendment_id",
    "offset": 445
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
        - name: accounting_code
          data_type: VARCHAR
        - name: amendment_id
          data_type: VARCHAR
        - name: balance
          data_type: BIGINT
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
          source_expression: "try_cast(created_date as TIMESTAMP)"
        - name: credit_amount
          data_type: DOUBLE
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

## 点：type_balance

类别：**其他**；角色：参与；把握：高。

balance在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `type_balance`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5355格; L1=534行/5335格; L2=534行/5335格; L3=534行/5335格。L0减量（先行后格）：0行/529格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"balance\" AS BIGINT) AS balance",
    "new": "\"balance\" AS balance",
    "offset": 496
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
        - name: amendment_id
          data_type: VARCHAR
        - name: balance
          data_type: BIGINT
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
          source_expression: "try_cast(created_date as TIMESTAMP)"
        - name: credit_amount
          data_type: DOUBLE
        - name: exchange_rate
          data_type: VARCHAR
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：type_credit_amount

类别：**其他**；角色：参与；把握：高。

credit_amount在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `type_credit_amount`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5879格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。L0减量（先行后格）：0行/5格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"credit_amount\" AS DOUBLE) AS credit_amount",
    "new": "\"credit_amount\" AS credit_amount",
    "offset": 743
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
          data_type: TIMESTAMP
          source_expression: "try_cast(created_date as TIMESTAMP)"
        - name: credit_amount
          data_type: DOUBLE
        - name: exchange_rate
          data_type: VARCHAR
        - name: exchange_rate_date
          data_type: TIMESTAMP
          source_expression: "try_cast(exchange_rate_date as TIMESTAMP)"
        - name: exempt_amount
          data_type: DOUBLE
        - name: exempt_amount_home_currency
          data_type: VARCHAR
        - name: home_currency
          data_type: VARCHAR
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：type_exempt_amount

类别：**其他**；角色：并列；把握：高。

exempt_amount在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `type_exempt_amount`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5350格; L1=534行/5335格; L2=534行/5335格; L3=534行/5335格。L0减量（先行后格）：0行/534格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"exempt_amount\" AS DOUBLE) AS exempt_amount",
    "new": "\"exempt_amount\" AS exempt_amount",
    "offset": 941
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
          data_type: TIMESTAMP
          source_expression: "try_cast(exchange_rate_date as TIMESTAMP)"
        - name: exempt_amount
          data_type: DOUBLE
        - name: exempt_amount_home_currency
          data_type: VARCHAR
        - name: home_currency
          data_type: VARCHAR
        - name: invoice_id
          data_type: VARCHAR
        - name: invoice_item_id
          data_type: VARCHAR
        - name: journal_entry_id
          data_type: VARCHAR
        - name: name
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：source_invoice_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给invoice_id来源映射；实际纳入534行，所选id匹配0、具名列匹配0，非空534中ID格式534、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `source_invoice_id`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5350格; L1=534行/5330格; L2=534行/5330格; L3=534行/5330格。L0减量（先行后格）：0行/534格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS invoice_id",
    "new": "try_cast(\"invoice_id\" AS VARCHAR) AS invoice_id",
    "offset": 1157
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
        - name: invoice_item_id
          data_type: VARCHAR
        - name: journal_entry_id
          data_type: VARCHAR
        - name: name
          data_type: VARCHAR
        - name: payment_amount
          data_type: DOUBLE
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_charge_id
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

## 点：source_invoice_item_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给invoice_item_id来源映射；实际纳入534行，所选id匹配0、具名列匹配2，非空534中ID格式5、时间文本529。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `source_invoice_item_id`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5350格; L1=534行/5330格; L2=534行/5330格; L3=534行/5330格。L0减量（先行后格）：0行/534格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS invoice_item_id",
    "new": "try_cast(\"invoice_item_id\" AS VARCHAR) AS invoice_item_id",
    "offset": 1206
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
        - name: invoice_id
          data_type: VARCHAR
        - name: invoice_item_id
          data_type: VARCHAR
        - name: journal_entry_id
          data_type: VARCHAR
        - name: name
          data_type: VARCHAR
        - name: payment_amount
          data_type: DOUBLE
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_charge_id
          data_type: VARCHAR
        - name: product_rate_plan_id
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

## 点：type_payment_amount

类别：**其他**；角色：参与；把握：高。

payment_amount在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `type_payment_amount`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5879格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。L0减量（先行后格）：0行/5格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"payment_amount\" AS DOUBLE) AS payment_amount",
    "new": "\"payment_amount\" AS payment_amount",
    "offset": 1374
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
        - name: name
          data_type: VARCHAR
        - name: payment_amount
          data_type: DOUBLE
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_charge_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
          data_type: VARCHAR
        - name: sales_tax_payable_accounting_code_id
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：source_product_id

类别：**Data Misconception**；角色：并列；把握：高。

P：本表实体id可作为product_id对应目标实体的关系键。实际纳入534行，所选id匹配0，具名product_id匹配5；非空候选5个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。

证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。

P：本表实体id可作为product_id对应目标实体的关系键。

agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。

反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 13, "result": {"col": "product_id", "n": 534, "nonnull": 5, "hex32": 5, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 16, "result": {"col": "product_id", "n": 534, "nonnull": 5, "chosen_matches": 0, "named_matches": 5}}}`。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `source_product_id`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5350格; L1=534行/5330格; L2=534行/5330格; L3=534行/5330格。L0减量（先行后格）：0行/534格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_id",
    "new": "try_cast(\"product_id\" AS VARCHAR) AS product_id",
    "offset": 1438
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
        - name: payment_amount
          data_type: DOUBLE
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_charge_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
          data_type: VARCHAR
        - name: sales_tax_payable_accounting_code_id
          data_type: VARCHAR
        - name: sold_to_contact_id
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

## 点：source_product_rate_plan_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给product_rate_plan_id来源映射；实际纳入534行，所选id匹配0、具名列匹配0，非空5中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `source_product_rate_plan_id`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5350格; L1=534行/5330格; L2=534行/5330格; L3=534行/5330格。L0减量（先行后格）：0行/534格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_rate_plan_id",
    "new": "try_cast(\"product_rate_plan_id\" AS VARCHAR) AS product_rate_plan_id",
    "offset": 1578
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
        - name: product_rate_plan_charge_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
          data_type: VARCHAR
        - name: sales_tax_payable_accounting_code_id
          data_type: VARCHAR
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: tax_amount
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

## 点：source_rate_plan_charge_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给rate_plan_charge_id来源映射；实际纳入534行，所选id匹配0、具名列匹配0，非空5中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `source_rate_plan_charge_id`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5350格; L1=534行/5330格; L2=534行/5330格; L3=534行/5330格。L0减量（先行后格）：0行/534格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS rate_plan_charge_id",
    "new": "try_cast(\"rate_plan_charge_id\" AS VARCHAR) AS rate_plan_charge_id",
    "offset": 1637
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
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
          data_type: VARCHAR
        - name: sales_tax_payable_accounting_code_id
          data_type: VARCHAR
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: tax_amount
          data_type: BIGINT
        - name: tax_amount_home_currency
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

## 点：source_rate_plan_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给rate_plan_id来源映射；实际纳入534行，所选id匹配0、具名列匹配0，非空5中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `source_rate_plan_id`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5350格; L1=534行/5330格; L2=534行/5330格; L3=534行/5330格。L0减量（先行后格）：0行/534格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS rate_plan_id",
    "new": "try_cast(\"rate_plan_id\" AS VARCHAR) AS rate_plan_id",
    "offset": 1695
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
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
          data_type: VARCHAR
        - name: sales_tax_payable_accounting_code_id
          data_type: VARCHAR
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: tax_amount
          data_type: BIGINT
        - name: tax_amount_home_currency
          data_type: DOUBLE
          source_expression: "case when nullif(tax_amount_home_currency,'') is null then null else cast(tax_amount_home_currency as double) end"
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

## 点：source_subscription_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给subscription_id来源映射；实际纳入534行，所选id匹配0、具名列匹配0，非空5中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `source_subscription_id`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5350格; L1=534行/5330格; L2=534行/5330格; L3=534行/5330格。L0减量（先行后格）：0行/534格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS subscription_id",
    "new": "try_cast(\"subscription_id\" AS VARCHAR) AS subscription_id",
    "offset": 1928
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
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: tax_amount
          data_type: BIGINT
        - name: tax_amount_home_currency
          data_type: DOUBLE
          source_expression: "case when nullif(tax_amount_home_currency,'') is null then null else cast(tax_amount_home_currency as double) end"
        - name: tax_date
          data_type: TIMESTAMP
          source_expression: "try_cast(tax_date as TIMESTAMP)"
        - name: tax_description
          data_type: VARCHAR
        - name: tax_mode
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

## 点：type_tax_rate

类别：**其他**；角色：参与；把握：高。

tax_rate在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `type_tax_rate`。

基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。

单改后：L0=534行/5879格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。L0减量（先行后格）：0行/5格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"tax_rate\" AS DOUBLE) AS tax_rate",
    "new": "\"tax_rate\" AS tax_rate",
    "offset": 2305
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
        - name: tax_mode
          data_type: VARCHAR
        - name: tax_rate
          data_type: DOUBLE
        - name: tax_rate_type
          data_type: VARCHAR
        - name: transaction_currency
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

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
