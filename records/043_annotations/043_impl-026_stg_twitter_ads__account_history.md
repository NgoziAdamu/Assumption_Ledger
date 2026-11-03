# 043：impl-026_stg_twitter_ads__account_history

## 结论

主要原因：**已说出的选择**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为1行/1格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`A`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__account_history.sql`；无SQL注释。材料包：`records/024_packages/024_impl-026_stg_twitter_ads__account_history.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-026.json`；与gold关系见 `records/015_raw_impl-026.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.twitter_account_history_data`：initial 2500行/13列；agent留存 2500行/13列；013差异=False。

## 同源决定

同源决定：event 13,17,19，`/tmp/gen.py`：report辅助函数批量生成report staging；同一脚本追加agg_model和marts，keyword在event21修正。 目录编号：`026-gen`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共3条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引16（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `timezone空白`：`records/024_queries.json` 数组索引17（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `timezone空白重试`：`records/024_extra_diagnostics.json` 数组索引0（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：timezone_trim

类别：**已说出的选择**；角色：主要；把握：中。

契约要求correct不支持的时区，未定trim还是UTC兜底；agent说明了UTC处理。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-026_stg_twitter_ads__account_history.json`，条目 `timezone_trim`。

基线：L0=1行/1格; L1=1行/1格; L2=1行/1格; L3=1行/1格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：1行/1格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "case when timezone in ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC') then timezone else 'UTC' end as timezone",
    "new": "case when trim(timezone) in ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC') then trim(timezone) else 'UTC' end as timezone",
    "offset": 317
  }
]
```

是否说出：**第1档——交付物里针对本处说明了**。时区纠正功能只对应account_history，明确指出未定fallback并说明UTC选择。

event 37 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
The contract requests correction of unsupported timezones without specifying a fallback; invalid timezone values are set to `UTC`.
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
        - name: name
          data_type: VARCHAR
        - name: timezone
          data_type: VARCHAR
          validation_rules:
            - rule: "timezone IN ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC')"
              on_failure: correct
        - name: timezone_switched_timestamp
          data_type: TIMESTAMP
        - name: updated_timestamp
          data_type: TIMESTAMP
        - name: is_latest_version
          data_type: BOOLEAN
          constraints: [not_null]
```


共同生成动作 `026-gen`；根源决定单元 `impl-026_stg_twitter_ads__account_history:timezone_trim`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
