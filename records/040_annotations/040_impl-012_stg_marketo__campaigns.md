# 040 正式标注：impl-012_stg_marketo__campaigns

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。022旧主要原因仅原样存档为 `O`，不作为新类别依据。

## 结论

主要原因：**其他**；把握高；共1个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### blank_names

主要；**其他**；把握高。

契约明确空白campaign_name须delete_row；agent按TRIM过滤，gold多保留1行。

是否说出：第2档——交付物里只有通用说明。交付物有适用于本类处理的通用说明，没有针对本表本处逐项说明。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1 | 0 | 28 | 0 |
| L1 | 1 | 0 | 28 | 0 |
| L2 | 1 | 0 | 28 | 0 |
| L3 | 1 | 0 | 28 | 0 |



来源：`records/022_reruns_impl-012_stg_marketo__campaigns.json` / `blank_names`。L0减少1行、28格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

rule: "campaign_name IS NOT NULL AND TRIM(campaign_name) <> ''"

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

rule: "campaign_name IS NOT NULL AND TRIM(campaign_name) <> ''"

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/55.json` / `args.final_thought` / event 55（delivery；普通SQL表达式不是披露）

```text

依据 staging 契约去除缺少关键 ID/时间/必需属性的行，并对重复主键保留更新时间较新的记录（活动重复时保留较早记录）。这保全了声明的唯一粒度，但剔除记录不会进入后续分析。

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/staging/stg_marketo__campaigns.sql` / `text`（sql；普通SQL表达式不是披露）

```text

 AND TRIM(name) <> ''

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`；行段[[82, 209]]；SHA-256 `9162d6f365aa651428fe0b03f4854de1e85296668fc5edaf34e599c15b3ac1a4`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/staging/stg_marketo__campaigns.sql`；SHA-256 `4c117e0580542961ddfe64e6e5939f75d1aa75ce0072d5ac2490a4ecc77c1197`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json`；材料包：`records/022_packages/022_impl-012_stg_marketo__campaigns.md`。

- 基线源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共3条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 8；上游可见行数；失败=True。

  - `records/022_queries.json` / index 9；空白名称；失败=False。

  - `records/022_queries_retry.json` / index 5；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
