# impl-006_stg_amazon_ads__search_report（038 正式表）

主要原因：**多因并列**；把握：高。020定稿旧主要原因：`多因并列（A、D）`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[300, 350]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__search_report.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### attributed_conversions_14_d

- 类别：Unstated Choice；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

attributed_conversions_14_d没有相应raw候选（ROAS所需归因收入也不存在）；契约未规定无源时补0还是NULL。对schema逐列核查后归Choice，不因整列NULL一律归降级。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "attributed_conversions_14_d"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__search_report.sql`，`delivered SQL`：

> CAST(NULL::INTEGER AS INTEGER) AS attributed_conversions_14_d

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__search_report.json#attributed_conversions_14_d`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 710/5680 | 710/4970 | 0/710 |
| L1 | 710/5680 | 710/4970 | 0/710 |
| L2 | 710/5680 | 710/4970 | 0/710 |
| L3 | 710/5680 | 710/4970 | 0/710 |

### attributed_conversions_30_d

- 类别：Unstated Choice；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

attributed_conversions_30_d没有相应raw候选（ROAS所需归因收入也不存在）；契约未规定无源时补0还是NULL。对schema逐列核查后归Choice，不因整列NULL一律归降级。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "attributed_conversions_30_d"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__search_report.sql`，`delivered SQL`：

> CAST(NULL::INTEGER AS INTEGER) AS attributed_conversions_30_d

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__search_report.json#attributed_conversions_30_d`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 710/5680 | 710/4970 | 0/710 |
| L1 | 710/5680 | 710/4970 | 0/710 |
| L2 | 710/5680 | 710/4970 | 0/710 |
| L3 | 710/5680 | 710/4970 | 0/710 |

### attributed_sales_14_d

- 类别：Unstated Choice；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

attributed_sales_14_d没有相应raw候选（ROAS所需归因收入也不存在）；契约未规定无源时补0还是NULL。对schema逐列核查后归Choice，不因整列NULL一律归降级。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "attributed_sales_14_d"
>           data_type: DECIMAL(18,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__search_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS attributed_sales_14_d

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__search_report.json#attributed_sales_14_d`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 710/5680 | 710/4970 | 0/710 |
| L1 | 710/5680 | 710/4970 | 0/710 |
| L2 | 710/5680 | 710/4970 | 0/710 |
| L3 | 710/5680 | 710/4970 | 0/710 |

### attributed_sales_30_d

- 类别：Unstated Choice；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

attributed_sales_30_d没有相应raw候选（ROAS所需归因收入也不存在）；契约未规定无源时补0还是NULL。对schema逐列核查后归Choice，不因整列NULL一律归降级。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "attributed_sales_30_d"
>           data_type: DECIMAL(18,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__search_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS attributed_sales_30_d

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__search_report.json#attributed_sales_30_d`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 710/5680 | 710/4970 | 0/710 |
| L1 | 710/5680 | 710/4970 | 0/710 |
| L2 | 710/5680 | 710/4970 | 0/710 |
| L3 | 710/5680 | 710/4970 | 0/710 |

### match_type

- 类别：Unstated Choice；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

match_type没有相应raw候选（ROAS所需归因收入也不存在）；契约未规定无源时补0还是NULL。对schema逐列核查后归Choice，不因整列NULL一律归降级。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "match_type"
>           data_type: VARCHAR

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__search_report.sql`，`delivered SQL`：

> CAST(NULL::VARCHAR AS VARCHAR) AS match_type

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__search_report.json#match_type`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 710/5680 | 710/4970 | 0/710 |
| L1 | 710/5680 | 710/4970 | 0/710 |
| L2 | 710/5680 | 710/4970 | 0/710 |
| L3 | 710/5680 | 710/4970 | 0/710 |

### return_on_ad_spend

- 类别：Unstated Choice；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

return_on_ad_spend没有相应raw候选（ROAS所需归因收入也不存在）；契约未规定无源时补0还是NULL。对schema逐列核查后归Choice，不因整列NULL一律归降级。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "return_on_ad_spend"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__search_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS return_on_ad_spend

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__search_report.json#return_on_ad_spend`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 710/5680 | 710/4970 | 0/710 |
| L1 | 710/5680 | 710/4970 | 0/710 |
| L2 | 710/5680 | 710/4970 | 0/710 |
| L3 | 710/5680 | 710/4970 | 0/710 |

### click_through_rate

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

click_through_rate虽与无源归因列同表，但raw有clicks/impressions/cost，NULL放弃可算指标，独立归降级。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "click_through_rate"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__search_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__search_report.json#click_through_rate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 710/5680 | 710/4970 | 0/710 |
| L1 | 710/5680 | 710/4970 | 0/710 |
| L2 | 710/5680 | 710/4970 | 0/710 |
| L3 | 710/5680 | 710/4970 | 0/710 |

### cost_per_click

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_click虽与无源归因列同表，但raw有clicks/impressions/cost，NULL放弃可算指标，独立归降级。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_click"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__search_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__search_report.json#cost_per_click`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 710/5680 | 710/4970 | 0/710 |
| L1 | 710/5680 | 710/4970 | 0/710 |
| L2 | 710/5680 | 710/4970 | 0/710 |
| L3 | 710/5680 | 710/4970 | 0/710 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[20]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='amazon_ads_search_term_ad_keyword_report_data') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[21]`：`SELECT count(*) n,count(*) FILTER(WHERE "cost" IS NULL) AS c0_null,count(*) FILTER(WHERE "cost" IS NOT NULL AND TRY_CAST("cost" AS DOUBLE) IS NULL) AS c1_not_numeric FROM raw.amazon_ads_search_term_ad_keyword_report_data`。
