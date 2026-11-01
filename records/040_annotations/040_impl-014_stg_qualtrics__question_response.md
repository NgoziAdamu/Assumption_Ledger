# 040 正式标注：impl-014_stg_qualtrics__question_response

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。022旧主要原因仅原样存档为 `O`，不作为新类别依据。

## 结论

主要原因：**其他**；把握高；共1个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### preserve_duplicates

主要；**其他**；把握高。

契约明确primary_key；agent按主键唯一化，gold保留重复行。去掉QUALIFY用于诊断，不表示应违反唯一性。若仅减格仍计参与。

是否说出：第2档——交付物里只有通用说明。交付物有适用于本类处理的通用说明，没有针对本表本处逐项说明。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 11 | 0 | 99 | 0 |
| L1 | 11 | 0 | 99 | 0 |
| L2 | 11 | 0 | 99 | 0 |
| L3 | 11 | 0 | 99 | 0 |



来源：`records/022_reruns_impl-014_stg_qualtrics__question_response.json` / `preserve_duplicates`。L0减少11行、99格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

      primary_key: ["response_id", "question_id"]

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

      primary_key: ["response_id", "question_id"]

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/79.json` / `args.final_thought` / event 79（delivery；普通SQL表达式不是披露）

```text

重复主键记录按主键仅保留一条；合同未指定冲突记录排序规则，因此非主键字段冲突时，具体保留行不保证业务优先级，可能丢失冲突值。

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__question_response.sql` / `text`（sql；普通SQL表达式不是披露）

```text

    QUALIFY row_number() OVER (PARTITION BY response_id, question_id ORDER BY response_id, question_id) = 1

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`；行段[[258, 287]]；SHA-256 `d56eb3bfab06ffaa8a87111ed860c4459739af5988d23d36738d925721df08eb`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__question_response.sql`；SHA-256 `8b690f0dd06012c21aa8a99a3f8f24704f5f03a8728f5d9afc0c4fc6df36515b`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/1.json`；材料包：`records/022_packages/022_impl-014_stg_qualtrics__question_response.md`。

- 基线源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共4条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 56；上游可见行数；失败=True。

  - `records/022_queries.json` / index 57；原始重复键；失败=True。

  - `records/022_queries_retry.json` / index 40；上游可见行数；失败=False。

  - `records/022_queries_retry.json` / index 41；原始重复键；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
