# 040 正式标注：impl-014_stg_qualtrics__user

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。022旧主要原因仅原样存档为 `O`，不作为新类别依据。

## 结论

主要原因：**其他**；把握高；共1个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### email_validation_order

主要；**其他**；把握高。

契约先LOWER(TRIM)再验证，agent遵从；gold验证未trim的原邮箱，额外排掉5行。只改验证对象后与gold一致证明差异来源。

是否说出：第2档——交付物里只有通用说明。交付物有适用于本类处理的通用说明，没有针对本表本处逐项说明。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 5 | 0 | 70 | 0 |
| L1 | 5 | 0 | 70 | 0 |
| L2 | 5 | 0 | 70 | 0 |
| L3 | 5 | 0 | 70 | 0 |



来源：`records/022_reruns_impl-014_stg_qualtrics__user.json` / `email_validation_order`。L0减少5行、70格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

rule: "email = LOWER(TRIM(email))"

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

rule: "email = LOWER(TRIM(email))"

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/79.json` / `args.final_thought` / event 79（delivery；普通SQL表达式不是披露）

```text

缺失/无效关键 ID 及合同要求删除的非法状态、邮箱或必需字段记录予以剔除；非关键无效值置 NULL。

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__user.sql` / `text`（sql；普通SQL表达式不是披露）

```text

regexp_matches(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

```

### 排除的旧候选/无差异诊断

- `preserve_duplicates`：原raw重复键查询为0组/没有本次去重差异；这是正确主键实现的无变化诊断，不虚构错误点。

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`；行段[[31, 90]]；SHA-256 `d56eb3bfab06ffaa8a87111ed860c4459739af5988d23d36738d925721df08eb`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__user.sql`；SHA-256 `2ed68458f8b97928946059f5874d448f910b979d6bcb0ff77f818060fa9382e2`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/1.json`；材料包：`records/022_packages/022_impl-014_stg_qualtrics__user.md`。

- 基线源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共5条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 65；上游可见行数；失败=True。

  - `records/022_queries.json` / index 66；原始重复键；失败=True。

  - `records/022_queries.json` / index 67；两种时间解析；失败=False。

  - `records/022_queries_retry.json` / index 48；上游可见行数；失败=False。

  - `records/022_queries_retry.json` / index 49；原始重复键；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
