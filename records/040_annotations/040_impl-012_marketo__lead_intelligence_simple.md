# 040 正式标注：impl-012_marketo__lead_intelligence_simple

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。022旧主要原因仅原样存档为 `多因并列`，不作为新类别依据。

## 结论

主要原因：**多因并列**；把握高；共2个点。不是只能组合修复。

并列项：missing_segment（Intent Misreading）；missing_action（其他）

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### missing_segment

并列；**Intent Misreading**；把握高。

没有engagement时应默认Unknown，agent先把次数补0再分段得到Inactive；这是默认业务规则未应用，不是数据事实误解。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 376 | 376 | 752 | 376 |
| L1 | 376 | 376 | 752 | 376 |
| L2 | 376 | 376 | 752 | 376 |
| L3 | 376 | 376 | 752 | 376 |



来源：`records/022_reruns_impl-012_marketo__lead_intelligence_simple.json` / `missing_segment`。L0减少0行、376格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

rfm_segment defaults to "Unknown", value_tier to "Basic", and lead_quality_tier to "Unqualified" when segmentation is missing.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

rfm_segment defaults to "Unknown", value_tier to "Basic", and lead_quality_tier to "Unqualified" when segmentation is missing.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/marts/marketo__lead_intelligence_simple.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CASE WHEN total_lead_score>=100

```

### missing_action

并列；**其他**；把握高。

契约无打开应Welcome Series；agent先补零后匹配该分支，gold缺失聚合为NULL而落到Standard Campaign Flow。单改仅模拟gold分支，不称agent应改成gold。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 376 | 376 | 752 | 376 |
| L1 | 376 | 376 | 752 | 376 |
| L2 | 376 | 376 | 752 | 376 |
| L3 | 376 | 376 | 752 | 376 |



来源：`records/022_reruns_impl-012_marketo__lead_intelligence_simple.json` / `missing_action`。L0减少0行、376格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

next_best_action (in order): Schedule Sales Call if click rate>=10 and last click within 7 days; Send Product Demo if open rate>=30; Re-engagement Campaign if last open is over 60 days ago and there has been at least one open; Welcome Series if there have been no opens; else Standard Campaign Flow.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

next_best_action (in order): Schedule Sales Call if click rate>=10 and last click within 7 days; Send Product Demo if open rate>=30; Re-engagement Campaign if last open is over 60 days ago and there has been at least one open; Welcome Series if there have been no opens; else Standard Campaign Flow.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/marts/marketo__lead_intelligence_simple.sql` / `text`（sql；普通SQL表达式不是披露）

```text

WHEN total_emails_opened=0 THEN 'Welcome Series'

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`；行段[[1457, 1579]]；SHA-256 `9162d6f365aa651428fe0b03f4854de1e85296668fc5edaf34e599c15b3ac1a4`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/marts/marketo__lead_intelligence_simple.sql`；SHA-256 `021a55715f55db90fd24b19951fc56f1fae64d6cc3bf4537f14c0023854bb8e5`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json`；材料包：`records/022_packages/022_impl-012_marketo__lead_intelligence_simple.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 9}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共2条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 2；上游可见行数；失败=True。

  - `records/022_queries_retry.json` / index 1；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
