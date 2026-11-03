# 043：impl-030_stg_zuora__invoice_item

## 结论

主要原因：**多因并列**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为0行/1495格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`多因并列（A、O）`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice_item.sql`；无SQL注释。材料包：`records/024_packages/024_impl-030_stg_zuora__invoice_item.md`。

本表直接raw源初始就为正常多列结构，最终执行仍为正常多列结构。 event19生成SQL时已见初始结构；event31运行原版run.py导入raw，event40确认展开后的列清单，event45的最终映射生成发生在此后。 初始与agent的run.py SHA-256相同，event10已展示单列按逗号拆分导入逻辑；不是agent另写修复原库。015确认gold与agent raw一致。正常结构不代表所有字段内容位置都符合语义，需逐列核实。

已逐张读取 `records/013_raw_impl-030.json`；与gold关系见 `records/015_raw_impl-030.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.zuora_invoice_item_data`：initial 3004行/54列；agent留存 3004行/54列；013差异=False。

## 同源决定

同源决定：event 19，`/tmp/gen_stage.py`：统一按契约生成staging类型与表达式，event21/25修订，event45将pk_alias集合统一映射为本表id。 目录编号：`030-gen-stage`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 45，pk_alias集合中的外键名一律改取本表id；event19原先按正确同名列生成。 本表点：source_account_id, source_amendment_id, source_invoice_id, source_product_id, source_product_rate_plan_id, source_rate_plan_charge_id, source_rate_plan_id, source_subscription_id；编号 `impl-030-event45-pk_alias`。

同源决定：event 19，staging统一按契约的type处理source_expression或同名源列，生成安全类型转换。 本表点：type_balance, type_exchange_rate_date, type_processing_type；编号 `030-contract-types`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共5条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引52（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `本实体id与各外键是否相同`：`records/024_queries.json` 数组索引53（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `候选外键匹配对照`：`records/024_queries.json` 数组索引54（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `外键字段格式诊断（原可见数据）`：`records/024_mapping_queries.json` 数组索引3（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `实际纳入行的候选映射`：`records/024_extra_diagnostics.json` 数组索引6（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：source_account_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给account_id来源映射；实际纳入1495行，所选id匹配0、具名列匹配5，非空1495中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `source_account_id`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14940格; L1=1495行/14935格; L2=1495行/14935格; L3=1495行/14935格。L0减量（先行后格）：0行/1495格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 216
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
        - name: applied_to_invoice_item_id
          data_type: VARCHAR
        - name: balance
          data_type: BIGINT
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

## 点：source_amendment_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给amendment_id来源映射；实际纳入1495行，所选id匹配0、具名列匹配0，非空1495中ID格式5、时间文本1490。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `source_amendment_id`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14940格; L1=1495行/14935格; L2=1495行/14935格; L3=1495行/14935格。L0减量（先行后格）：0行/1495格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS amendment_id",
    "new": "try_cast(\"amendment_id\" AS VARCHAR) AS amendment_id",
    "offset": 443
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
        - name: applied_to_invoice_item_id
          data_type: VARCHAR
        - name: balance
          data_type: BIGINT
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: charge_amount
          data_type: BIGINT
        - name: charge_amount_home_currency
          data_type: VARCHAR
        - name: charge_date
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

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `type_balance`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14945格; L1=1495行/14940格; L2=1495行/14940格; L3=1495行/14940格。L0减量（先行后格）：0行/1490格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"balance\" AS BIGINT) AS balance",
    "new": "\"balance\" AS balance",
    "offset": 583
  }
]
```

是否说出：**第1档——交付物里针对本处说明了**。invoice-item一一对应本表，并具体说明processing_type/金额字段类型冲突，覆盖这两点。

event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
        - name: applied_to_invoice_item_id
          data_type: VARCHAR
        - name: balance
          data_type: BIGINT
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: charge_amount
          data_type: BIGINT
        - name: charge_amount_home_currency
          data_type: VARCHAR
        - name: charge_date
          data_type: TIMESTAMP
          source_expression: "try_cast(charge_date as TIMESTAMP)"
        - name: charge_name
          data_type: VARCHAR
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：type_exchange_rate_date

类别：**其他**；角色：参与；把握：高。

exchange_rate_date在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `type_exchange_rate_date`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14945格; L1=1495行/14940格; L2=1495行/14940格; L3=1495行/14940格。L0减量（先行后格）：0行/1490格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"exchange_rate_date\" AS DATE) AS exchange_rate_date",
    "new": "\"exchange_rate_date\" AS exchange_rate_date",
    "offset": 1271
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
        - name: exchange_rate
          data_type: VARCHAR
        - name: exchange_rate_date
          data_type: DATE
        - name: home_currency
          data_type: VARCHAR
        - name: invoice_id
          data_type: VARCHAR
        - name: journal_entry_id
          data_type: VARCHAR
        - name: parent_account_id
          data_type: VARCHAR
        - name: processing_type
          data_type: BOOLEAN
        - name: product_id
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：source_invoice_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给invoice_id来源映射；实际纳入1495行，所选id匹配0、具名列匹配5，非空1495中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `source_invoice_id`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14940格; L1=1495行/14935格; L2=1495行/14935格; L3=1495行/14935格。L0减量（先行后格）：0行/1495格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS invoice_id",
    "new": "try_cast(\"invoice_id\" AS VARCHAR) AS invoice_id",
    "offset": 1404
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
        - name: parent_account_id
          data_type: VARCHAR
        - name: processing_type
          data_type: BOOLEAN
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

## 点：type_processing_type

类别：**其他**；角色：并列；把握：高。

processing_type在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `type_processing_type`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14940格; L1=1495行/14940格; L2=1495行/14940格; L3=1495行/14940格。L0减量（先行后格）：0行/1495格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"processing_type\" AS BOOLEAN) AS processing_type",
    "new": "\"processing_type\" AS processing_type",
    "offset": 1593
  }
]
```

是否说出：**第1档——交付物里针对本处说明了**。invoice-item一一对应本表，并具体说明processing_type/金额字段类型冲突，覆盖这两点。

event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：

```text
        - name: parent_account_id
          data_type: VARCHAR
        - name: processing_type
          data_type: BOOLEAN
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_charge_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: quantity
          data_type: BIGINT
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：source_product_id

类别：**Unstated Choice**；角色：并列；把握：中。

契约未给product_id来源映射；实际纳入1495行，所选id匹配0、具名列匹配5，非空1495中ID格式5、时间文本1490。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `source_product_id`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14940格; L1=1495行/14935格; L2=1495行/14935格; L3=1495行/14935格。L0减量（先行后格）：0行/1495格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_id",
    "new": "try_cast(\"product_id\" AS VARCHAR) AS product_id",
    "offset": 1660
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
        - name: processing_type
          data_type: BOOLEAN
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_charge_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: quantity
          data_type: BIGINT
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
          data_type: VARCHAR
        - name: recognized_revenue_accounting_code_id
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

契约未给product_rate_plan_id来源映射；实际纳入1495行，所选id匹配0、具名列匹配0，非空5中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `source_product_rate_plan_id`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14940格; L1=1495行/14935格; L2=1495行/14935格; L3=1495行/14935格。L0减量（先行后格）：0行/1495格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_rate_plan_id",
    "new": "try_cast(\"product_rate_plan_id\" AS VARCHAR) AS product_rate_plan_id",
    "offset": 1800
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
        - name: quantity
          data_type: BIGINT
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
          data_type: VARCHAR
        - name: recognized_revenue_accounting_code_id
          data_type: VARCHAR
        - name: rev_rec_start_date
          data_type: TIMESTAMP
          source_expression: "try_cast(rev_rec_start_date as TIMESTAMP)"
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

契约未给rate_plan_charge_id来源映射；实际纳入1495行，所选id匹配0、具名列匹配0，非空5中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `source_rate_plan_charge_id`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14940格; L1=1495行/14935格; L2=1495行/14935格; L3=1495行/14935格。L0减量（先行后格）：0行/1495格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS rate_plan_charge_id",
    "new": "try_cast(\"rate_plan_charge_id\" AS VARCHAR) AS rate_plan_charge_id",
    "offset": 1911
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
        - name: quantity
          data_type: BIGINT
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
          data_type: VARCHAR
        - name: recognized_revenue_accounting_code_id
          data_type: VARCHAR
        - name: rev_rec_start_date
          data_type: TIMESTAMP
          source_expression: "try_cast(rev_rec_start_date as TIMESTAMP)"
        - name: service_end_date
          data_type: DATE
          source_expression: "try_cast(service_end_date as DATE)"
        - name: service_start_date
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

契约未给rate_plan_id来源映射；实际纳入1495行，所选id匹配0、具名列匹配0，非空5中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `source_rate_plan_id`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14940格; L1=1495行/14935格; L2=1495行/14935格; L3=1495行/14935格。L0减量（先行后格）：0行/1495格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS rate_plan_id",
    "new": "try_cast(\"rate_plan_id\" AS VARCHAR) AS rate_plan_id",
    "offset": 1969
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
        - name: recognized_revenue_accounting_code_id
          data_type: VARCHAR
        - name: rev_rec_start_date
          data_type: TIMESTAMP
          source_expression: "try_cast(rev_rec_start_date as TIMESTAMP)"
        - name: service_end_date
          data_type: DATE
          source_expression: "try_cast(service_end_date as DATE)"
        - name: service_start_date
          data_type: DATE
          source_expression: "try_cast(service_start_date as DATE)"
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

契约未给subscription_id来源映射；实际纳入1495行，所选id匹配0、具名列匹配0，非空5中ID格式5、时间文本0。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__invoice_item.json`，条目 `source_subscription_id`。

基线：L0=1495行/16435格; L1=1495行/16430格; L2=1495行/16430格; L3=1495行/16430格。

单改后：L0=1495行/14940格; L1=1495行/14935格; L2=1495行/14935格; L3=1495行/14935格。L0减量（先行后格）：0行/1495格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS subscription_id",
    "new": "try_cast(\"subscription_id\" AS VARCHAR) AS subscription_id",
    "offset": 2521
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
        - name: source_item_type
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: tax_amount
          data_type: BIGINT
        - name: tax_mode
          data_type: VARCHAR
        - name: transaction_currency
          data_type: VARCHAR
        - name: unit_price
          data_type: BIGINT
        - name: uom
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

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
