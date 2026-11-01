# impl-007_stg_apple_store__sales_subscription_summary（038 正式表）

主要原因：**Unstated Choice**；把握：高。020定稿旧主要原因：`A`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`，[211, 239]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_summary.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### active_subscriptions

- 类别：Unstated Choice；角色：主要；把握：高。

- 是否说出：第3档（过程中意识到了，交付物里没提）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约只给active_subscriptions名称/类型，没有源映射与计数方式；subscribers人数与active_standard_price/free_trial布尔状态解释均需选择，不能由gold唯一决定。失败报告草稿明确指出Apple订阅summary/event字段语义不一致、需源端定义进一步确认，属于同组意识。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: active_subscriptions
>           data_type: BIGINT

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_summary.sql`，`delivered SQL`：

> TRY_CAST(subscribers AS BIGINT) AS active_subscriptions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/65.json`，`65.args.command`：

> Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。若这类字段用于正式订阅财务决策，应以源端字段定义进一步确认。

同组意识：明确说订阅summary/event语义不一致且需进一步确认。event65写result.md失败，不是交付物，只有第3档。

重跑/诊断：`records/020_reruns_impl-007_stg_apple_store__sales_subscription_summary.json#active_subscriptions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 700/1047 | 347/347 | 353/700 |
| L1 | 700/1047 | 347/347 | 353/700 |
| L2 | 700/1047 | 347/347 | 353/700 |
| L3 | 700/1047 | 347/347 | 353/700 |

### free_trial_subscriptions

- 类别：Unstated Choice；角色：参与；把握：高。

- 是否说出：第3档（过程中意识到了，交付物里没提）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约只给free_trial_subscriptions名称/类型，没有源映射与计数方式；subscribers人数与active_standard_price/free_trial布尔状态解释均需选择，不能由gold唯一决定。失败报告草稿明确指出Apple订阅summary/event字段语义不一致、需源端定义进一步确认，属于同组意识。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: free_trial_subscriptions
>           data_type: BIGINT

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_summary.sql`，`delivered SQL`：

> CASE WHEN active_free_trial_introductory_offer_subscriptions THEN TRY_CAST(subscribers AS BIGINT) ELSE 0 END AS free_trial_subscriptions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/65.json`，`65.args.command`：

> Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。若这类字段用于正式订阅财务决策，应以源端字段定义进一步确认。

同组意识：明确说订阅summary/event语义不一致且需进一步确认。event65写result.md失败，不是交付物，只有第3档。

重跑/诊断：`records/020_reruns_impl-007_stg_apple_store__sales_subscription_summary.json#free_trial_subscriptions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 700/1047 | 700/700 | 0/347 |
| L1 | 700/1047 | 700/700 | 0/347 |
| L2 | 700/1047 | 700/700 | 0/347 |
| L3 | 700/1047 | 700/700 | 0/347 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[56]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='sales_subscription_summary') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[57]`：`SELECT count(*) n,count(*) FILTER(WHERE subscribers<0) negative_subscribers,count(*) FILTER(WHERE subscribers<>cast(active_standard_price_subscriptions AS BIGINT)) different_active,count(*) FILTER(WHERE active_free_trial_introductory_offer_subscriptions AND subscribers<>1) different_free FROM raw.sales_subscription_summary`。
