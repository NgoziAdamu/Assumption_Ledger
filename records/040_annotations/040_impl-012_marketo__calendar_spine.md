# 040 正式标注：impl-012_marketo__calendar_spine

## 任务

按冻结v3.2第3～8节逐点重标；层：utils。022旧主要原因仅原样存档为 `A`，不作为新类别依据。

## 结论

主要原因：**Unstated Choice**；把握中；共1个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

完整 `data_contract.yaml` 已搜索：没有 `name: marketo__calendar_spine` 定义，只有下游引用；依赖配置也未给出该表定义。下游写“The upper bound of dates is defined only by the calendar spine; no additional end-date filter is applied.”，没有决定工具表终点。证据：`records/040_checks/calendar_contract_search.json`。

### calendar_end

主要；**Unstated Choice**；把握中。

完整data_contract.yaml没有工具表的name定义，只在下游lead_calendar_spine引用且上界由工具表提供；没有写截止今天或下周，差异取决于材料没定的选择。

是否说出：第2档——交付物里只有通用说明。句子混合工具日历终点与逐lead日历起点，没有点名utils表，按一一对应覆盖要求记通用说明；不使用附带测试脚本。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 0 | 7 | 0 |
| L1 | 7 | 0 | 7 | 0 |
| L2 | 7 | 0 | 7 | 0 |
| L3 | 7 | 0 | 7 | 0 |



来源：`records/022_reruns_impl-012_marketo__calendar_spine.json` / `calendar_end`。L0减少7行、7格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml` / `text`（contract_context；普通SQL表达式不是披露）

```text

The upper bound of dates is defined only by the calendar spine; no additional end-date filter is applied.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/55.json` / `args.final_thought` / event 55（delivery；普通SQL表达式不是披露）

```text

日历延伸至当前日期，并按 lead created date 起算。

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`；行段[]；SHA-256 `9162d6f365aa651428fe0b03f4854de1e85296668fc5edaf34e599c15b3ac1a4`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/utils/marketo__calendar_spine.sql`；SHA-256 `a3e7054ab61abe240952e88294de04d2cfefd4f0dd70de92318b8336176100e8`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json`；材料包：`records/022_packages/022_impl-012_marketo__calendar_spine.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 2}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共2条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 10；上游可见行数；失败=True。

  - `records/022_queries_retry.json` / index 6；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

- 报告“日历延伸至当前日期，并按lead created date起算”可被读成utils终点的具体说明，也可读成逐lead日历的组合说明；没有点名工具表且混合两张表，按用户一一对应要求保守记第2档。契约完整搜索无工具表定义，类别为未规定选择。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
