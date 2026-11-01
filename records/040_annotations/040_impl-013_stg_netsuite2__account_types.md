# 040 正式标注：impl-013_stg_netsuite2__account_types

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。022旧主要原因仅原样存档为 `A`，不作为新类别依据。

## 结论

主要原因：**Unstated Choice**；把握中；共1个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### type_key

主要；**Unstated Choice**；把握中。

契约给BIGINT、unique而未给ID算法；raw internalid与按longname排序row_number均唯一，查询不能否定前者。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 6 | 0 | 12 | 0 |
| L1 | 6 | 0 | 12 | 0 |
| L2 | 6 | 0 | 12 | 0 |
| L3 | 6 | 0 | 12 | 0 |



来源：`records/022_reruns_impl-013_stg_netsuite2__account_types.json` / `type_key`。L0减少6行、12格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: account_type_id
          data_type: BIGINT
          constraints: [not_null, unique]

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: account_type_id
          data_type: BIGINT
          constraints: [not_null, unique]

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__account_types.sql` / `text`（sql；普通SQL表达式不是披露）

```text

TRY_CAST(r."internalid" AS BIGINT)

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`；行段[[443, 455]]；SHA-256 `c152a30bcad4df785d3f0ea461101eb8a4b36e4fa06059739a80e04998c4150f`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__account_types.sql`；SHA-256 `63dc63092a2f91a2b467aa4316947b2767d9b921f09d02b49d21fe34a1eb62b4`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`；材料包：`records/022_packages/022_impl-013_stg_netsuite2__account_types.md`。

- 基线源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共3条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 25；上游可见行数；失败=True。

  - `records/022_queries.json` / index 26；两种type标识；失败=False。

  - `records/022_queries_retry.json` / index 19；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
