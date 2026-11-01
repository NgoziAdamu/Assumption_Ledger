# 040 正式标注：impl-012_stg_marketo__activity_send_email

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。022旧主要原因仅原样存档为 `A`，不作为新类别依据。

## 结论

主要原因：**已说出的选择**；把握高；共1个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### send_id

主要；**已说出的选择**；把握高。

email_send_id生成法未规定，源活动id与四列MD5的差异是材料没定的选择。finish明确说明发送表id映射及跨事件键局限。

是否说出：第1档——交付物里针对本处说明了。交付物以表名或一一对应功能点明本处处理。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 15000 | 0 | 15000 | 0 |
| L1 | 15000 | 0 | 15000 | 0 |
| L2 | 15000 | 0 | 15000 | 0 |
| L3 | 15000 | 0 | 15000 | 0 |



来源：`records/022_reruns_impl-012_stg_marketo__activity_send_email.json` / `send_id`。L0减少15000行、15000格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: email_send_id
          data_type: VARCHAR



```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: email_send_id
          data_type: VARCHAR



```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/55.json` / `args.final_thought` / event 55（delivery；普通SQL表达式不是披露）

```text

原始活动表没有独立 `email_send_id`，发送表使用 `id` 映射；其他活动表也按原始活动 ID 输出 `email_send_id`。源数据未提供可确认的跨活动发送键，因此打开、点击、投递等跨事件连接存在来源标识的局限，计数仍按 contract 在各活动自身分组。

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/staging/stg_marketo__activity_send_email.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(id AS VARCHAR) AS email_send_id

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`；行段[[316, 345]]；SHA-256 `9162d6f365aa651428fe0b03f4854de1e85296668fc5edaf34e599c15b3ac1a4`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/staging/stg_marketo__activity_send_email.sql`；SHA-256 `7fdf3f17d68fa72409b8afe92c0b22084d99ba91f9f7b21bc33d1f3e0d660867`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json`；材料包：`records/022_packages/022_impl-012_stg_marketo__activity_send_email.md`。

- 基线源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共3条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 6；上游可见行数；失败=True。

  - `records/022_queries.json` / index 7；send_id源列核实；失败=False。

  - `records/022_queries_retry.json` / index 4；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
