# 040 正式标注：impl-014_qualtrics__user_cohort_analysis

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。022旧主要原因仅原样存档为 `O`，不作为新类别依据。

## 结论

主要原因：**Unstated Choice**；把握中；共3个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### parse_timestamp

主要；**Unstated Choice**；把握中。

契约未写解析表达式；agent格式解析17995/17995成功，gold直接TRY_CAST为0/17995。按照用户澄清这是材料没定的选择，不把gold失败当数据事实或agent误解。

是否说出：第2档——交付物里只有通用说明。交付物有适用于本类处理的通用说明，没有针对本表本处逐项说明。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 5 | 1 | 40 | 8 |
| L1 | 5 | 1 | 40 | 8 |
| L2 | 5 | 1 | 40 | 8 |
| L3 | 5 | 1 | 40 | 8 |



来源：`records/022_reruns_impl-014_qualtrics__user_cohort_analysis.json` / `parse_timestamp`。L0减少4行、32格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

first_response_date: the earliest timestamp parsed from recorded_date.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

first_response_date: the earliest timestamp parsed from recorded_date.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/79.json` / `args.final_thought` / event 79（delivery；普通SQL表达式不是披露）

```text

原始 Qualtrics 时间文本带时区后缀（例如 `+0800`），DuckDB 直接 `try_cast(... AS TIMESTAMP)` 无法解析。日期相关 SQL 改用 `try_strptime(..., '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP`；不可解析日期在日期计算中排除。

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/marts/qualtrics__user_cohort_analysis.sql` / `text`（sql；普通SQL表达式不是披露）

```text

try_strptime(recorded_date, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP

```

### keep_null_dates

非原因；**Intent Misreading**；把握高。

契约以原recorded_date存在作为输入过滤，agent又加解析成功过滤；当前所有非空时间均可解析，单改完全不改善，记非原因。

是否说出：第1档——交付物里针对本处说明了。交付物以表名或一一对应功能点明本处处理。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 5 | 5 | 40 | 40 |
| L1 | 5 | 5 | 40 | 40 |
| L2 | 5 | 5 | 40 | 40 |
| L3 | 5 | 5 | 40 | 40 |



来源：`records/022_reruns_impl-014_qualtrics__user_cohort_analysis.json` / `keep_null_dates`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

Keep only records with recorded_date present.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

Keep only records with recorded_date present.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/79.json` / `args.final_thought` / event 79（delivery；普通SQL表达式不是披露）

```text

无法按已观察到的带时区格式解析的日期仍保留在原文本字段，但不进入 cohort、30 日窗口及按日统计，可能造成日期类指标低估。

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/marts/qualtrics__user_cohort_analysis.sql` / `text`（sql；普通SQL表达式不是披露）

```text

    WHERE recorded_at IS NOT NULL


```

### cohort_month_gold_type

非原因；**其他**；把握高。

契约cohort_month为DATE，agent遵从，gold为TIMESTAMP。单改类型在解析差异下无改善；022修gold解析并转DATE后全匹配证明类型残差，不能将两项组合收益冒充单改。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 5 | 5 | 40 | 40 |
| L1 | 5 | 5 | 40 | 40 |
| L2 | 5 | 5 | 40 | 40 |
| L3 | 5 | 5 | 40 | 40 |



来源：`records/040_checks/supplement_impl-014_qualtrics__user_cohort_analysis.json` / `cohort_month_gold_type`。L0减少0行、0格。

非原因说明：此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: cohort_month
        data_type: DATE
        description: First day of the month of each user's first response; cohort grouping key.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: cohort_month
        data_type: DATE
        description: First day of the month of each user's first response; cohort grouping key.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/marts/qualtrics__user_cohort_analysis.sql` / `text`（sql；普通SQL表达式不是披露）

```text

date_trunc('month', min(recorded_at))::DATE AS cohort_month

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`；行段[[1206, 1242]]；SHA-256 `d56eb3bfab06ffaa8a87111ed860c4459739af5988d23d36738d925721df08eb`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/marts/qualtrics__user_cohort_analysis.sql`；SHA-256 `195536d0a23ffdb981fa28b5f9d7f29a32cb5b3b1dbb3af11b10e4265a5dc36f`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/1.json`；材料包：`records/022_packages/022_impl-014_qualtrics__user_cohort_analysis.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共3条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 37；上游可见行数；失败=True。

  - `records/022_queries.json` / index 38；cohort时间解析；失败=False。

  - `records/022_queries_retry.json` / index 25；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
