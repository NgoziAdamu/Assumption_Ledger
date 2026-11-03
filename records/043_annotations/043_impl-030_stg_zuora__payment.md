# 043：impl-030_stg_zuora__payment

## 结论

主要原因：**多因并列**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为0行/722格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`多因并列（O、U）`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__payment.sql`；无SQL注释。材料包：`records/024_packages/024_impl-030_stg_zuora__payment.md`。

本表直接raw源初始就为正常多列结构，最终执行仍为正常多列结构。 event19生成SQL时已见初始结构；event31运行原版run.py导入raw，event40确认展开后的列清单，event45的最终映射生成发生在此后。 初始与agent的run.py SHA-256相同，event10已展示单列按逗号拆分导入逻辑；不是agent另写修复原库。015确认gold与agent raw一致。正常结构不代表所有字段内容位置都符合语义，需逐列核实。

已逐张读取 `records/013_raw_impl-030.json`；与gold关系见 `records/015_raw_impl-030.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.zuora_payment_data`：initial 1503行/55列；agent留存 1503行/55列；013差异=False。

## 同源决定

同源决定：event 19，`/tmp/gen_stage.py`：统一按契约生成staging类型与表达式，event21/25修订，event45将pk_alias集合统一映射为本表id。 目录编号：`030-gen-stage`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 45，pk_alias集合中的外键名一律改取本表id；event19原先按正确同名列生成。 本表点：source_account_id, source_payment_method_id；编号 `impl-030-event45-pk_alias`。

同源决定：event 19，staging统一按契约的type处理source_expression或同名源列，生成安全类型转换。 本表点：type_amount, type_amount_home_currency, type_applied_amount, type_applied_credit_balance_amount, type_effective_date, type_exchange_rate_date, type_refund_amount, type_unapplied_amount；编号 `030-contract-types`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共5条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引61（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `本实体id与各外键是否相同`：`records/024_queries.json` 数组索引62（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `候选外键匹配对照`：`records/024_queries.json` 数组索引63（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `外键字段格式诊断（原可见数据）`：`records/024_mapping_queries.json` 数组索引6（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `实际纳入行的候选映射`：`records/024_extra_diagnostics.json` 数组索引9（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：source_account_id

类别：**Data Misconception**；角色：并列；把握：高。

P：本表实体id可作为account_id对应目标实体的关系键。实际纳入722行，所选id匹配0，具名account_id匹配718；非空候选722个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。

证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。

P：本表实体id可作为account_id对应目标实体的关系键。

agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。

反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 6, "result": {"col": "account_id", "n": 722, "nonnull": 722, "hex32": 722, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 9, "result": {"col": "account_id", "n": 722, "nonnull": 722, "chosen_matches": 0, "named_matches": 718}}}`。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `source_account_id`。

基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。

单改后：L0=722行/3615格; L1=722行/2162格; L2=722行/2162格; L3=722行/726格。L0减量（先行后格）：0行/722格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 206
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
        - name: accounting_code
          data_type: VARCHAR
        - name: amount
          data_type: DOUBLE
        - name: amount_home_currency
          data_type: DOUBLE
        - name: applied_amount
          data_type: DOUBLE
        - name: applied_credit_balance_amount
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

## 点：type_amount

类别：**其他**；角色：参与；把握：高。

amount在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `type_amount`。

基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。

单改后：L0=722行/4336格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。L0减量（先行后格）：0行/1格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"amount\" AS DOUBLE) AS amount",
    "new": "\"amount\" AS amount",
    "offset": 322
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
        - name: accounting_code
          data_type: VARCHAR
        - name: amount
          data_type: DOUBLE
        - name: amount_home_currency
          data_type: DOUBLE
        - name: applied_amount
          data_type: DOUBLE
        - name: applied_credit_balance_amount
          data_type: DOUBLE
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: cancelled_on
          data_type: TIMESTAMP
          source_expression: "try_cast(cancelled_on as TIMESTAMP)"
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：type_amount_home_currency

类别：**其他**；角色：参与；把握：高。

amount_home_currency在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `type_amount_home_currency`。

基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。

单改后：L0=722行/4333格; L1=722行/2880格; L2=722行/2880格; L3=722行/1444格。L0减量（先行后格）：0行/4格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"amount_home_currency\" AS DOUBLE) AS amount_home_currency",
    "new": "\"amount_home_currency\" AS amount_home_currency",
    "offset": 370
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
        - name: amount
          data_type: DOUBLE
        - name: amount_home_currency
          data_type: DOUBLE
        - name: applied_amount
          data_type: DOUBLE
        - name: applied_credit_balance_amount
          data_type: DOUBLE
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: cancelled_on
          data_type: TIMESTAMP
          source_expression: "try_cast(cancelled_on as TIMESTAMP)"
        - name: comment
          data_type: VARCHAR
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：type_applied_amount

类别：**其他**；角色：参与；把握：高。

applied_amount在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `type_applied_amount`。

基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。

单改后：L0=722行/4333格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。L0减量（先行后格）：0行/4格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"applied_amount\" AS DOUBLE) AS applied_amount",
    "new": "\"applied_amount\" AS applied_amount",
    "offset": 446
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
        - name: amount_home_currency
          data_type: DOUBLE
        - name: applied_amount
          data_type: DOUBLE
        - name: applied_credit_balance_amount
          data_type: DOUBLE
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: cancelled_on
          data_type: TIMESTAMP
          source_expression: "try_cast(cancelled_on as TIMESTAMP)"
        - name: comment
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：type_applied_credit_balance_amount

类别：**其他**；角色：并列；把握：高。

applied_credit_balance_amount在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `type_applied_credit_balance_amount`。

基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。

单改后：L0=722行/3615格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。L0减量（先行后格）：0行/722格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"applied_credit_balance_amount\" AS DOUBLE) AS applied_credit_balance_amount",
    "new": "\"applied_credit_balance_amount\" AS applied_credit_balance_amount",
    "offset": 510
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
        - name: applied_amount
          data_type: DOUBLE
        - name: applied_credit_balance_amount
          data_type: DOUBLE
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: cancelled_on
          data_type: TIMESTAMP
          source_expression: "try_cast(cancelled_on as TIMESTAMP)"
        - name: comment
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：type_effective_date

类别：**其他**；角色：参与；把握：高。

effective_date在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `type_effective_date`。

基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。

单改后：L0=722行/3619格; L1=722行/2166格; L2=722行/2166格; L3=722行/1448格。L0减量（先行后格）：0行/718格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"effective_date\" AS DATE) AS effective_date",
    "new": "\"effective_date\" AS effective_date",
    "offset": 966
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
        - name: currency
          data_type: VARCHAR
        - name: effective_date
          data_type: DATE
        - name: exchange_rate
          data_type: VARCHAR
        - name: exchange_rate_date
          data_type: DATE
        - name: home_currency
          data_type: VARCHAR
        - name: parent_account_id
          data_type: VARCHAR
        - name: payment_method_id
          data_type: VARCHAR
        - name: payment_number
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：type_exchange_rate_date

类别：**其他**；角色：参与；把握：高。

exchange_rate_date在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `type_exchange_rate_date`。

基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。

单改后：L0=722行/3619格; L1=722行/2166格; L2=722行/2166格; L3=722行/1448格。L0减量（先行后格）：0行/718格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"exchange_rate_date\" AS DATE) AS exchange_rate_date",
    "new": "\"exchange_rate_date\" AS exchange_rate_date",
    "offset": 1091
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
        - name: parent_account_id
          data_type: VARCHAR
        - name: payment_method_id
          data_type: VARCHAR
        - name: payment_number
          data_type: VARCHAR
        - name: refund_amount
          data_type: DOUBLE
        - name: settled_on
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：source_payment_method_id

类别：**Data Misconception**；角色：并列；把握：高。

P：本表实体id可作为payment_method_id对应目标实体的关系键。实际纳入722行，所选id匹配0，具名payment_method_id匹配718；非空候选722个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。

证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。

P：本表实体id可作为payment_method_id对应目标实体的关系键。

agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。

反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 6, "result": {"col": "payment_method_id", "n": 722, "nonnull": 722, "hex32": 722, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 9, "result": {"col": "payment_method_id", "n": 722, "nonnull": 722, "chosen_matches": 0, "named_matches": 718}}}`。

同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。

证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `source_payment_method_id`。

基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。

单改后：L0=722行/3615格; L1=722行/2162格; L2=722行/2162格; L3=722行/726格。L0减量（先行后格）：0行/722格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS payment_method_id",
    "new": "try_cast(\"payment_method_id\" AS VARCHAR) AS payment_method_id",
    "offset": 1295
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
        - name: payment_method_id
          data_type: VARCHAR
        - name: payment_number
          data_type: VARCHAR
        - name: refund_amount
          data_type: DOUBLE
        - name: settled_on
          data_type: TIMESTAMP
          source_expression: "try_cast(settled_on as TIMESTAMP)"
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
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

## 点：type_refund_amount

类别：**其他**；角色：并列；把握：高。

refund_amount在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `type_refund_amount`。

基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。

单改后：L0=722行/3615格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。L0减量（先行后格）：0行/722格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"refund_amount\" AS DOUBLE) AS refund_amount",
    "new": "\"refund_amount\" AS refund_amount",
    "offset": 1416
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
        - name: payment_number
          data_type: VARCHAR
        - name: refund_amount
          data_type: DOUBLE
        - name: settled_on
          data_type: TIMESTAMP
          source_expression: "try_cast(settled_on as TIMESTAMP)"
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
        - name: submitted_on
          data_type: TIMESTAMP
          source_expression: "try_cast(submitted_on as TIMESTAMP)"
        - name: transaction_currency
```


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 点：type_unapplied_amount

类别：**其他**；角色：参与；把握：高。

unapplied_amount在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `type_unapplied_amount`。

基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。

单改后：L0=722行/4333格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。L0减量（先行后格）：0行/4格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(\"unapplied_amount\" AS DOUBLE) AS unapplied_amount",
    "new": "\"unapplied_amount\" AS unapplied_amount",
    "offset": 1927
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
        - name: type
          data_type: VARCHAR
        - name: unapplied_amount
          data_type: DOUBLE
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


共同生成动作 `030-gen-stage`；根源决定单元 `030-contract-types`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
