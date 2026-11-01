# impl-007_stg_apple_store__financial_stats_subscriptions_country（038 正式表）

主要原因：**其他**；把握：高。020定稿旧主要原因：`O`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`，[300, 322]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__financial_stats_subscriptions_country.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### subscription_name

- 类别：Unstated Choice；角色：参与；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

空名称透传或填Unnamed未规定，gold的默认文案不能确立唯一做法。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: subscription_name
>           data_type: VARCHAR

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__financial_stats_subscriptions_country.sql`，`delivered SQL`：

> CAST(subscription_name AS VARCHAR) AS subscription_name

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: subscription_name
>           data_type: VARCHAR

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-007_stg_apple_store__financial_stats_subscriptions_country.json#subscription_name`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 704/1373 | 704/744 | 0/629 |
| L1 | 704/1369 | 700/740 | 4/629 |
| L2 | 704/1369 | 700/740 | 4/629 |
| L3 | 704/1369 | 700/740 | 4/629 |

### country

- 类别：Unstated Choice；角色：参与；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

country透传或对空/异常文本补US未规定；不能凭gold补US断言真实国家为US。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: country
>           data_type: VARCHAR

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__financial_stats_subscriptions_country.sql`，`delivered SQL`：

> CAST(country AS VARCHAR) AS country

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: country
>           data_type: VARCHAR

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-007_stg_apple_store__financial_stats_subscriptions_country.json#country`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 704/1373 | 700/1332 | 4/41 |
| L1 | 704/1369 | 700/1328 | 4/41 |
| L2 | 704/1369 | 700/1328 | 4/41 |
| L3 | 704/1369 | 700/1328 | 4/41 |

### revenue

- 类别：其他；角色：主要；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约明确BIGINT，agent按该类型输出；gold DECIMAL(15,2)保留小数。换为契约允许的评测条件agent可对上，不归Form或Intent。

判定顺序：第3节第1步及第6节；以契约/呈现条件定位差异。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: revenue
>           data_type: BIGINT

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__financial_stats_subscriptions_country.sql`，`delivered SQL`：

> TRY_CAST(revenue AS BIGINT) AS revenue

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: revenue
>           data_type: BIGINT

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-007_stg_apple_store__financial_stats_subscriptions_country.json#revenue`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 704/1373 | 637/677 | 67/696 |
| L1 | 704/1369 | 637/677 | 67/692 |
| L2 | 704/1369 | 637/677 | 67/692 |
| L3 | 704/1369 | 637/677 | 67/692 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[54]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='financial_stats_subscriptions_country') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[55]`：`SELECT count(*) n,count(*) FILTER(WHERE revenue<0) negative_revenue,count(*) FILTER(WHERE revenue<>round(revenue)) fractional_revenue,count(*) FILTER(WHERE trim(subscription_name)='') blank_name FROM raw.financial_stats_subscriptions_country`。
