# impl-006_stg_amazon_ads__ad_group_report（038 正式表）

主要原因：**Intent Misreading**；把握：高。020定稿旧主要原因：`C`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[70, 111]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__ad_group_report.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### invalid_id_contract_delete

- 类别：Intent Misreading；角色：主要；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：是；曾经理解对过：否；系统提示：不适用。

ad_group_id的正则与delete_row动作均在契约写明；agent未过滤非法ID。采用契约删除实验，拒绝把gold置NULL诊断当作契约修复。

判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "ad_group_id"
>           data_type: VARCHAR
>           constraints: [not_null]
>           validation_rules:
>             - rule: "ad_group_id IS NOT NULL AND TRIM(ad_group_id) != ''"
>               on_failure: delete_row
>             - rule: "REGEXP_LIKE(ad_group_id, '^[A-Za-z0-9_-]{1,128}$')"
>               on_failure: delete_row

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__ad_group_report.sql`，`delivered SQL`：

> SELECT * FROM cleaned

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "ad_group_id"
>           data_type: VARCHAR
>           constraints: [not_null]
>           validation_rules:
>             - rule: "ad_group_id IS NOT NULL AND TRIM(ad_group_id) != ''"
>               on_failure: delete_row
>             - rule: "REGEXP_LIKE(ad_group_id, '^[A-Za-z0-9_-]{1,128}$')"
>               on_failure: delete_row

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__ad_group_report.json#invalid_id_contract_delete`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 17884/55655 | 17868/55511 | 16/144 |
| L1 | 17884/55649 | 17868/55505 | 16/144 |
| L2 | 17884/55649 | 17868/55505 | 16/144 |
| L3 | 17884/55649 | 17868/55505 | 16/144 |

### campaign_bidding_strategy

- 类别：Unstated Choice；角色：参与；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约只要求VARCHAR，未规定合法枚举、清理或同义词策略；gold白名单/大写/置空与agent透传不同，不能把gold枚举当作约定。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "campaign_bidding_strategy"
>           data_type: VARCHAR

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__ad_group_report.sql`，`delivered SQL`：

> TRY_CAST("campaign_bidding_strategy" AS VARCHAR) AS campaign_bidding_strategy

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "campaign_bidding_strategy"
>           data_type: VARCHAR

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__ad_group_report.json#campaign_bidding_strategy`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 17884/55655 | 17884/37668 | 0/17987 |
| L1 | 17884/55649 | 17884/37683 | 0/17966 |
| L2 | 17884/55649 | 17884/37683 | 0/17966 |
| L3 | 17884/55649 | 17884/37683 | 0/17966 |

### click_through_rate

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

click_through_rate整列NULL；raw已有clicks/impressions/cost及（campaign ROAS）sales_30_d候选，可计算。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "click_through_rate"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__ad_group_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__ad_group_report.json#click_through_rate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 17884/55655 | 17884/37308 | 0/18347 |
| L1 | 17884/55649 | 17884/37300 | 0/18349 |
| L2 | 17884/55649 | 17884/37300 | 0/18349 |
| L3 | 17884/55649 | 17884/37300 | 0/18349 |

### cost_per_click

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_click整列NULL；raw已有clicks/impressions/cost及（campaign ROAS）sales_30_d候选，可计算。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_click"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__ad_group_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__ad_group_report.json#cost_per_click`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 17884/55655 | 17884/38404 | 0/17251 |
| L1 | 17884/55649 | 17884/38396 | 0/17253 |
| L2 | 17884/55649 | 17884/38396 | 0/17253 |
| L3 | 17884/55649 | 17884/38396 | 0/17253 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[12]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='amazon_ads_ad_group_level_report_data') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[13]`：`SELECT count(*) n,count(*) FILTER(WHERE "campaign_bidding_strategy" IS NULL) AS c0_null,count(*) FILTER(WHERE "campaign_bidding_strategy" IS NOT NULL AND TRY_CAST("campaign_bidding_strategy" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "cost" IS NULL) AS c2_null,count(*) FILTER(WHERE "cost" IS NOT NULL AND TRY_CAST("cost" AS DOUBLE) IS NULL) AS c3_not_numeric FROM raw.amazon_ads_ad_group_level_report_data`。
