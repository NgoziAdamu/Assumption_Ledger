# 043：impl-026_stg_twitter_ads__line_item_keywords_report

## 结论

主要原因：**多因并列**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为0行/1500格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`多因并列（A、O）`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__line_item_keywords_report.sql`；无SQL注释。材料包：`records/024_packages/024_impl-026_stg_twitter_ads__line_item_keywords_report.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-026.json`；与gold关系见 `records/015_raw_impl-026.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.twitter_line_item_keywords_report_data`：initial 1500行/26列；agent留存 1500行/26列；013差异=False。

## 同源决定

同源决定：event 13,17,19，`/tmp/gen.py`：report辅助函数批量生成report staging；同一脚本追加agg_model和marts，keyword在event21修正。 目录编号：`026-gen`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 13，report辅助函数把date统一转TIMESTAMP。 本表点：date_type；编号 `026-report-date`。

同源决定：event 13，report辅助函数对raw中缺失的四种conversion字段统一输出类型化NULL。 本表点：conversion_purchases_metric, conversion_custom_metric, conversion_purchases_sale_amount, conversion_custom_sale_amount；编号 `026-report-null-conversions`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共1条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引21（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：date_type

类别：**其他**；角色：并列；把握：高。

本表date_day契约明确TIMESTAMP，agent照做；gold为DATE。评测键不做日期容差，不能把符合契约的timestamp当作形式错误。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-026_stg_twitter_ads__line_item_keywords_report.json`，条目 `date_type`。

基线：L0=1500行/3000格; L1=1500行/3000格; L2=1500行/3000格; L3=1500行/1500格。

单改后：L0=1500行/1500格; L1=1500行/1500格; L2=1500行/1500格; L3=1500行/1500格。L0减量（先行后格）：0行/1500格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(date as timestamp) as date_day",
    "new": "cast(date as date) as date_day",
    "offset": 11
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
      source_table: raw.twitter_line_item_keywords_report_data
      columns:
        - name: date_day
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: account_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: line_item_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: keyword
          data_type: VARCHAR
        - name: keyword_id
          data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `026-gen`；根源决定单元 `026-report-date`。

## 点：conversion_purchases_metric

类别：**Unstated Choice**；角色：非原因；把握：中。

raw列清单没有conversion_purchases_metric对应列；契约未指定缺失填0还是NULL，agent留类型化NULL，不能归Quiet Downgrade。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-026_stg_twitter_ads__line_item_keywords_report.json`，条目 `conversion_purchases_metric`。

基线：L0=1500行/3000格; L1=1500行/3000格; L2=1500行/3000格; L3=1500行/1500格。

单改后：L0=1500行/3000格; L1=1500行/3000格; L2=1500行/3000格; L3=1500行/1500格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "cast(null as bigint) as conversion_purchases_metric",
    "new": "cast(0 as bigint) as conversion_purchases_metric",
    "offset": 298
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第2档——交付物里只有通用说明**。raw Twitter report tables是多表概括，没有点名本表或一一对应名称；第2档。

event 37 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
The raw Twitter report tables do not contain the contract’s conversion metric or conversion sale amount columns. Staging emits typed NULLs for these unavailable values;
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
        - name: url_clicks
          data_type: BIGINT
        - name: conversion_purchases_metric
          data_type: BIGINT
        - name: conversion_custom_metric
          data_type: BIGINT
        - name: conversion_purchases_sale_amount
          data_type: DOUBLE
        - name: conversion_custom_sale_amount
          data_type: DOUBLE
```


共同生成动作 `026-gen`；根源决定单元 `026-report-null-conversions`。

## 点：conversion_custom_metric

类别：**Unstated Choice**；角色：非原因；把握：中。

raw列清单没有conversion_custom_metric对应列；契约未指定缺失填0还是NULL，agent留类型化NULL，不能归Quiet Downgrade。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-026_stg_twitter_ads__line_item_keywords_report.json`，条目 `conversion_custom_metric`。

基线：L0=1500行/3000格; L1=1500行/3000格; L2=1500行/3000格; L3=1500行/1500格。

单改后：L0=1500行/3000格; L1=1500行/3000格; L2=1500行/3000格; L3=1500行/1500格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "cast(null as bigint) as conversion_custom_metric",
    "new": "cast(0 as bigint) as conversion_custom_metric",
    "offset": 355
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第2档——交付物里只有通用说明**。raw Twitter report tables是多表概括，没有点名本表或一一对应名称；第2档。

event 37 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
The raw Twitter report tables do not contain the contract’s conversion metric or conversion sale amount columns. Staging emits typed NULLs for these unavailable values;
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
        - name: conversion_purchases_metric
          data_type: BIGINT
        - name: conversion_custom_metric
          data_type: BIGINT
        - name: conversion_purchases_sale_amount
          data_type: DOUBLE
        - name: conversion_custom_sale_amount
          data_type: DOUBLE
```


共同生成动作 `026-gen`；根源决定单元 `026-report-null-conversions`。

## 点：conversion_purchases_sale_amount

类别：**Unstated Choice**；角色：非原因；把握：中。

raw列清单没有conversion_purchases_sale_amount对应列；契约未指定缺失填0还是NULL，agent留类型化NULL，不能归Quiet Downgrade。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-026_stg_twitter_ads__line_item_keywords_report.json`，条目 `conversion_purchases_sale_amount`。

基线：L0=1500行/3000格; L1=1500行/3000格; L2=1500行/3000格; L3=1500行/1500格。

单改后：L0=1500行/3000格; L1=1500行/3000格; L2=1500行/3000格; L3=1500行/1500格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "cast(null as double) as conversion_purchases_sale_amount",
    "new": "cast(0 as double) as conversion_purchases_sale_amount",
    "offset": 409
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第2档——交付物里只有通用说明**。raw Twitter report tables是多表概括，没有点名本表或一一对应名称；第2档。

event 37 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
The raw Twitter report tables do not contain the contract’s conversion metric or conversion sale amount columns. Staging emits typed NULLs for these unavailable values;
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
        - name: conversion_custom_metric
          data_type: BIGINT
        - name: conversion_purchases_sale_amount
          data_type: DOUBLE
        - name: conversion_custom_sale_amount
          data_type: DOUBLE
```


共同生成动作 `026-gen`；根源决定单元 `026-report-null-conversions`。

## 点：conversion_custom_sale_amount

类别：**Unstated Choice**；角色：非原因；把握：中。

raw列清单没有conversion_custom_sale_amount对应列；契约未指定缺失填0还是NULL，agent留类型化NULL，不能归Quiet Downgrade。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-026_stg_twitter_ads__line_item_keywords_report.json`，条目 `conversion_custom_sale_amount`。

基线：L0=1500行/3000格; L1=1500行/3000格; L2=1500行/3000格; L3=1500行/1500格。

单改后：L0=1500行/3000格; L1=1500行/3000格; L2=1500行/3000格; L3=1500行/1500格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "cast(null as double) as conversion_custom_sale_amount",
    "new": "cast(0 as double) as conversion_custom_sale_amount",
    "offset": 471
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第2档——交付物里只有通用说明**。raw Twitter report tables是多表概括，没有点名本表或一一对应名称；第2档。

event 37 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
The raw Twitter report tables do not contain the contract’s conversion metric or conversion sale amount columns. Staging emits typed NULLs for these unavailable values;
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
        - name: conversion_purchases_sale_amount
          data_type: DOUBLE
        - name: conversion_custom_sale_amount
          data_type: DOUBLE
```


共同生成动作 `026-gen`；根源决定单元 `026-report-null-conversions`。

## 点：keyword_id

类别：**已说出的选择**；角色：并列；把握：中。

raw无keyword_id，契约没定生成公式；keyword文本与gold组合MD5是键值生成选择，不是纯形式。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-026_stg_twitter_ads__line_item_keywords_report.json`，条目 `keyword_id`。

基线：L0=1500行/3000格; L1=1500行/3000格; L2=1500行/3000格; L3=1500行/1500格。

单改后：L0=1500行/1500格; L1=1500行/1500格; L2=1500行/1500格; L3=0行/0格。L0减量（先行后格）：0行/1500格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "keyword as keyword_id",
    "new": "md5(account_id || '-' || line_item_id || '-' || coalesce(keyword,'') || '-' || coalesce(placement,'')) as keyword_id",
    "offset": 90
  }
]
```

是否说出：**第1档——交付物里针对本处说明了**。keyword report唯一对应本表，明确说明keyword文本生成id及唯一性限制。

event 37 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
The raw keyword report does not contain `keyword_id`; that field is derived from available `keyword` text, so uniqueness beyond keyword text is not guaranteed.
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
    - name: stg_twitter_ads__line_item_keywords_report
      description: "Daily keyword performance per line item and placement with normalized spend and derived keyword_id."
      source_table: raw.twitter_line_item_keywords_report_data
      columns:
        - name: date_day
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: account_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: line_item_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: keyword
```


共同生成动作 `026-gen`；根源决定单元 `impl-026_stg_twitter_ads__line_item_keywords_report:keyword_id`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
