# impl-006_int_ad_reporting__ad_report（038 正式表）

主要原因：**Quiet Downgrade**；把握：高。020定稿旧主要原因：`D`，仅原样保留。

## 范围与材料

- 层：intermediate。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[1517, 1623]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`。

- 对比执行输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### missing_apple_branch

- 类别：Quiet Downgrade；角色：主要；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约明确Facebook+Apple UNION ALL；fallback仅取Facebook，完全漏掉Apple输入。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: '- Build a standardized ad report by stacking rows from the two source models; no aggregation, filtering, or reordering; original row multiplicity is preserved. - Facebook Ads mapping: - account_id from source; campaign_id NULL; ad_group_id NULL; ad_network_type NULL; device NULL. - impressions from source; clicks from inline_link_clicks; interactions set to 0. - cost from spend. - conversions set to 0; conversions_value set to 0.0; view_through_conversions set to 0. - active_view_* fields NULL. - attributed_* fields NULL. - installs NULL; taps NULL. - click_through_rate from source; cost_per_click from source; cost_per_thousand_impressions from source; cost_per_conversion set to 0.0; return_on_ad_spend set to 0.0. - interaction_event_types NULL; _dbt_loaded_at passed through. - Apple Search Ads mapping: - account_id NULL; campaign_id from source; ad_group_id from source; ad_network_type NULL; device NULL. - impressions converted to integer; clicks from taps converted to integer; interactions set to 0. - cost from spend. - conversions from source; conversions_value set to 0.0; view_through_conversions set to 0. - active_view_* fields NULL. - attributed_* fields NULL. - installs from new_downloads converted to integer; taps converted to integer. - click_through_rate from tap_through_rate; cost_per_click from cost_per_tap; cost_per_thousand_impressions set to 0.0; cost_per_conversion from source; return_on_ad_spend set to 0.0. - interaction_event_types NULL; _dbt_loaded_at passed through. - Numeric constants: 0 is used for integer columns; 0.0 is used for decimal/double columns. Conversions to integer are performed where noted; no other rounding is applied. NULLs are set exactly as indicated.'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`，`delivered SQL`：

> FROM staging.stg_facebook_ads__ad_report

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__ad_report.json#missing_apple_branch`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2500/56000 | 1000/8000 | 1500/48000 |
| L1 | 2500/56000 | 1000/8000 | 1500/48000 |
| L2 | 2500/56000 | 1000/8000 | 1500/48000 |
| L3 | 2500/56000 | 1000/8000 | 1500/48000 |

### clicks

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

clicks整列NULL；契约规定的源映射/默认0/公式均可用。此处是整列占位，按第3节先判降级。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: clicks
>         data_type: INTEGER
>         description: 'Facebook: inline_link_clicks; Apple: taps converted to integer'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`，`delivered SQL`：

> NULL::INTEGER AS "clicks"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__ad_report.json#clicks`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2500/56000 | 2500/55000 | 0/1000 |
| L1 | 2500/56000 | 2500/55000 | 0/1000 |
| L2 | 2500/56000 | 2500/55000 | 0/1000 |
| L3 | 2500/56000 | 2500/55000 | 0/1000 |

### cost

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost整列NULL；契约规定的源映射/默认0/公式均可用。此处是整列占位，按第3节先判降级。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: cost
>         data_type: DECIMAL(18,2)
>         description: Spend from source; typed as DECIMAL(18,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`，`delivered SQL`：

> NULL::DECIMAL(18,2) AS "cost"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__ad_report.json#cost`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2500/56000 | 2500/55000 | 0/1000 |
| L1 | 2500/56000 | 2500/55000 | 0/1000 |
| L2 | 2500/56000 | 2500/55000 | 0/1000 |
| L3 | 2500/56000 | 2500/55000 | 0/1000 |

### interactions

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

interactions整列NULL；契约规定的源映射/默认0/公式均可用。此处是整列占位，按第3节先判降级。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: interactions
>         data_type: INTEGER
>         description: Constant 0 in both branches

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`，`delivered SQL`：

> NULL::INTEGER AS "interactions"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__ad_report.json#interactions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2500/56000 | 2500/55000 | 0/1000 |
| L1 | 2500/56000 | 2500/55000 | 0/1000 |
| L2 | 2500/56000 | 2500/55000 | 0/1000 |
| L3 | 2500/56000 | 2500/55000 | 0/1000 |

### conversions

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

conversions整列NULL；契约规定的源映射/默认0/公式均可用。此处是整列占位，按第3节先判降级。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: conversions
>         data_type: INTEGER
>         description: 'Facebook: 0; Apple: conversions'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`，`delivered SQL`：

> NULL::INTEGER AS "conversions"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__ad_report.json#conversions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2500/56000 | 2500/55000 | 0/1000 |
| L1 | 2500/56000 | 2500/55000 | 0/1000 |
| L2 | 2500/56000 | 2500/55000 | 0/1000 |
| L3 | 2500/56000 | 2500/55000 | 0/1000 |

### conversions_value

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

conversions_value整列NULL；契约规定的源映射/默认0/公式均可用。此处是整列占位，按第3节先判降级。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: conversions_value
>         data_type: DECIMAL(2,1)
>         description: Constant 0.0 in both branches

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`，`delivered SQL`：

> NULL::DECIMAL(2,1) AS "conversions_value"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__ad_report.json#conversions_value`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2500/56000 | 2500/55000 | 0/1000 |
| L1 | 2500/56000 | 2500/55000 | 0/1000 |
| L2 | 2500/56000 | 2500/55000 | 0/1000 |
| L3 | 2500/56000 | 2500/55000 | 0/1000 |

### view_through_conversions

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

view_through_conversions整列NULL；契约规定的源映射/默认0/公式均可用。此处是整列占位，按第3节先判降级。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: view_through_conversions
>         data_type: INTEGER
>         description: Constant 0 in both branches

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`，`delivered SQL`：

> NULL::INTEGER AS "view_through_conversions"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__ad_report.json#view_through_conversions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2500/56000 | 2500/55000 | 0/1000 |
| L1 | 2500/56000 | 2500/55000 | 0/1000 |
| L2 | 2500/56000 | 2500/55000 | 0/1000 |
| L3 | 2500/56000 | 2500/55000 | 0/1000 |

### cost_per_conversion

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_conversion整列NULL；契约规定的源映射/默认0/公式均可用。此处是整列占位，按第3节先判降级。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: cost_per_conversion
>         data_type: DOUBLE
>         description: 'Facebook: 0.0; Apple: cost_per_conversion'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`，`delivered SQL`：

> NULL::DOUBLE AS "cost_per_conversion"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__ad_report.json#cost_per_conversion`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2500/56000 | 2500/55000 | 0/1000 |
| L1 | 2500/56000 | 2500/55000 | 0/1000 |
| L2 | 2500/56000 | 2500/55000 | 0/1000 |
| L3 | 2500/56000 | 2500/55000 | 0/1000 |

### return_on_ad_spend

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

return_on_ad_spend整列NULL；契约规定的源映射/默认0/公式均可用。此处是整列占位，按第3节先判降级。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: return_on_ad_spend
>         data_type: DECIMAL(2,1)
>         description: Constant 0.0 in both branches

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`，`delivered SQL`：

> NULL::DECIMAL(2,1) AS "return_on_ad_spend"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__ad_report.json#return_on_ad_spend`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 2500/56000 | 2500/55000 | 0/1000 |
| L1 | 2500/56000 | 2500/55000 | 0/1000 |
| L2 | 2500/56000 | 2500/55000 | 0/1000 |
| L3 | 2500/56000 | 2500/55000 | 0/1000 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[1]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='staging' AND table_name='stg_facebook_ads__ad_report') ORDER BY table_schema,table_name,ordinal_position`。
