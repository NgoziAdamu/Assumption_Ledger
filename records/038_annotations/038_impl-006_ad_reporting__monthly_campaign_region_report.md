# impl-006_ad_reporting__monthly_campaign_region_report（038 正式表）

主要原因：**Quiet Downgrade**；把握：高。020定稿旧主要原因：`D`，仅原样保留。

## 范围与材料

- 层：marts。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[3910, 4039]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`。

- 对比执行输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### spend

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约已给spend的total_*透传来源，原始上游有对应列；fallback未正确使用映射而整列NULL。未见代码先明确写对该total_*映射后被覆盖的证据，不能套用staging的代码错误。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: spend
>         data_type: DECIMAL(38,2)
>         description: Monthly total cost passed through from total_cost; scale 2 preserved; currency as per source

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::DECIMAL(38,2) AS "spend"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#spend`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/116601 | 0/136 |
| L1 | 4236/116952 | 4236/116811 | 0/141 |
| L2 | 4236/114023 | 4236/113882 | 0/141 |
| L3 | 4236/114023 | 4236/113882 | 0/141 |

### attributed_sales_14_day

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约已给attributed_sales_14_day的total_*透传来源，原始上游有对应列；fallback未正确使用映射而整列NULL。未见代码先明确写对该total_*映射后被覆盖的证据，不能套用staging的代码错误。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: attributed_sales_14_day
>         data_type: DECIMAL(38,2)
>         description: Monthly total attributed sales with 14-day window from total_attributed_sales_14_d; scale 2 preserved

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::DECIMAL(38,2) AS "attributed_sales_14_day"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#attributed_sales_14_day`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/110952 | 0/5785 |
| L1 | 4236/116952 | 4236/111480 | 0/5472 |
| L2 | 4236/114023 | 4236/108775 | 0/5248 |
| L3 | 4236/114023 | 4236/108775 | 0/5248 |

### attributed_sales_30_day

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约已给attributed_sales_30_day的total_*透传来源，原始上游有对应列；fallback未正确使用映射而整列NULL。未见代码先明确写对该total_*映射后被覆盖的证据，不能套用staging的代码错误。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: attributed_sales_30_day
>         data_type: DECIMAL(38,2)
>         description: Monthly total attributed sales with 30-day window from total_attributed_sales_30_d; scale 2 preserved

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::DECIMAL(38,2) AS "attributed_sales_30_day"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#attributed_sales_30_day`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/111419 | 0/5318 |
| L1 | 4236/116952 | 4236/111607 | 0/5345 |
| L2 | 4236/114023 | 4236/108908 | 0/5115 |
| L3 | 4236/114023 | 4236/108908 | 0/5115 |

### attributed_conversions_14_day

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约已给attributed_conversions_14_day的total_*透传来源，原始上游有对应列；fallback未正确使用映射而整列NULL。未见代码先明确写对该total_*映射后被覆盖的证据，不能套用staging的代码错误。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: attributed_conversions_14_day
>         data_type: HUGEINT
>         description: Monthly total attributed conversions with 14-day window from total_attributed_conversions_14_d

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::HUGEINT AS "attributed_conversions_14_day"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#attributed_conversions_14_day`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/78279 | 0/38458 |
| L1 | 4236/116952 | 4236/78291 | 0/38661 |
| L2 | 4236/114023 | 4236/75455 | 0/38568 |
| L3 | 4236/114023 | 4236/75455 | 0/38568 |

### attributed_conversions_30_day

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约已给attributed_conversions_30_day的total_*透传来源，原始上游有对应列；fallback未正确使用映射而整列NULL。未见代码先明确写对该total_*映射后被覆盖的证据，不能套用staging的代码错误。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: attributed_conversions_30_day
>         data_type: HUGEINT
>         description: Monthly total attributed conversions with 30-day window from total_attributed_conversions_30_d

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::HUGEINT AS "attributed_conversions_30_day"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#attributed_conversions_30_day`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/78279 | 0/38458 |
| L1 | 4236/116952 | 4236/78291 | 0/38661 |
| L2 | 4236/114023 | 4236/75455 | 0/38568 |
| L3 | 4236/114023 | 4236/75455 | 0/38568 |

### placeholder_filter

- 类别：Intent Misreading；角色：非原因；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确排除platform=placeholder，SQL无该WHERE；新单改无改善，因此只是未落实的前提，不是本次判错原因。

判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: '- Select a monthly, region-level campaign record from intermediate.int_ad_reporting__monthly_campaign_region_report and rename columns as follows: - month_year → report_month - total_impressions → impressions - total_clicks → clicks - total_interactions → interactions - total_cost → spend - total_conversions → conversions - total_conversions_value → conversions_value - total_view_through_conversions → view_through_conversions - total_attributed_sales_14_d → attributed_sales_14_day - total_attributed_sales_30_d → attributed_sales_30_day - total_attributed_conversions_14_d → attributed_conversions_14_day - total_attributed_conversions_30_d → attributed_conversions_30_day - total_active_view_impressions → active_view_impressions - total_active_view_measurable_impressions → active_view_measurable_impressions - monthly_regional_click_through_rate → avg_ctr_percent - monthly_regional_cost_per_click → avg_cpc - monthly_regional_cost_per_thousand_impressions → avg_cpm - monthly_regional_cost_per_conversion → avg_cpa - monthly_regional_return_on_ad_spend → avg_roas - _dbt_loaded_at → data_last_updated - Pass through all other selected fields without transformation; no joins, deduplication, or additional aggregation are performed. - Filter: exclude rows where platform = ''placeholder''. - Add governance timestamp: mart_created_at = CURRENT_TIMESTAMP at query execution time (TIMESTAMP WITH TIME ZONE). - Order the final result by platform, account_id, campaign_id, report_month DESC, spend DESC; ordering affects presentation only and does not alter row values.'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> FROM intermediate.int_ad_reporting__monthly_campaign_region_report

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: '- Select a monthly, region-level campaign record from intermediate.int_ad_reporting__monthly_campaign_region_report and rename columns as follows: - month_year → report_month - total_impressions → impressions - total_clicks → clicks - total_interactions → interactions - total_cost → spend - total_conversions → conversions - total_conversions_value → conversions_value - total_view_through_conversions → view_through_conversions - total_attributed_sales_14_d → attributed_sales_14_day - total_attributed_sales_30_d → attributed_sales_30_day - total_attributed_conversions_14_d → attributed_conversions_14_day - total_attributed_conversions_30_d → attributed_conversions_30_day - total_active_view_impressions → active_view_impressions - total_active_view_measurable_impressions → active_view_measurable_impressions - monthly_regional_click_through_rate → avg_ctr_percent - monthly_regional_cost_per_click → avg_cpc - monthly_regional_cost_per_thousand_impressions → avg_cpm - monthly_regional_cost_per_conversion → avg_cpa - monthly_regional_return_on_ad_spend → avg_roas - _dbt_loaded_at → data_last_updated - Pass through all other selected fields without transformation; no joins, deduplication, or additional aggregation are performed. - Filter: exclude rows where platform = ''placeholder''. - Add governance timestamp: mart_created_at = CURRENT_TIMESTAMP at query execution time (TIMESTAMP WITH TIME ZONE). - Order the final result by platform, account_id, campaign_id, report_month DESC, spend DESC; ordering affects presentation only and does not alter row values.'

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/038_checks/rerun_impl-006_ad_reporting__monthly_campaign_region_report.json#placeholder_filter`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/116737 | 0/0 |
| L1 | 4236/116952 | 4236/116952 | 0/0 |
| L2 | 4236/114023 | 4236/114023 | 0/0 |
| L3 | 4236/114023 | 4236/114023 | 0/0 |

### avg_ctr_percent

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

avg_ctr_percent整列NULL，契约给定monthly_regional_*映射或执行时间来源；属于可提供而未提供。avg_cpm单改格子差异反增，不能据此记参与。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: avg_ctr_percent
>         data_type: DOUBLE
>         description: Monthly regional click-through rate from source; unit/scale preserved; no re-scaling or rounding applied

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::DOUBLE AS "avg_ctr_percent"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#avg_ctr_percent`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/116682 | 0/55 |
| L1 | 4236/116952 | 4236/117135 | 0/-183 |
| L2 | 4236/114023 | 4236/114075 | 0/-52 |
| L3 | 4236/114023 | 4236/114075 | 0/-52 |

### avg_cpc

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

avg_cpc整列NULL，契约给定monthly_regional_*映射或执行时间来源；属于可提供而未提供。avg_cpm单改格子差异反增，不能据此记参与。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: avg_cpc
>         data_type: DOUBLE
>         description: Monthly regional average cost per click from source; unit/scale preserved

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::DOUBLE AS "avg_cpc"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#avg_cpc`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/116512 | 0/225 |
| L1 | 4236/116952 | 4236/116764 | 0/188 |
| L2 | 4236/114023 | 4236/113846 | 0/177 |
| L3 | 4236/114023 | 4236/113846 | 0/177 |

### avg_cpm

- 类别：Quiet Downgrade；角色：非原因；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

avg_cpm整列NULL，契约给定monthly_regional_*映射或执行时间来源；属于可提供而未提供。avg_cpm单改格子差异反增，不能据此记参与。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: avg_cpm
>         data_type: DOUBLE
>         description: Monthly regional average cost per thousand impressions from source; unit/scale preserved

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::DOUBLE AS "avg_cpm"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#avg_cpm`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/117148 | 0/-411 |
| L1 | 4236/116952 | 4236/116887 | 0/65 |
| L2 | 4236/114023 | 4236/113960 | 0/63 |
| L3 | 4236/114023 | 4236/113960 | 0/63 |

### avg_cpa

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

avg_cpa整列NULL，契约给定monthly_regional_*映射或执行时间来源；属于可提供而未提供。avg_cpm单改格子差异反增，不能据此记参与。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: avg_cpa
>         data_type: DOUBLE
>         description: Monthly regional average cost per conversion from source; unit/scale preserved

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::DOUBLE AS "avg_cpa"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#avg_cpa`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/111743 | 0/4994 |
| L1 | 4236/116952 | 4236/111730 | 0/5222 |
| L2 | 4236/114023 | 4236/108918 | 0/5105 |
| L3 | 4236/114023 | 4236/108918 | 0/5105 |

### avg_roas

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

avg_roas整列NULL，契约给定monthly_regional_*映射或执行时间来源；属于可提供而未提供。avg_cpm单改格子差异反增，不能据此记参与。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: avg_roas
>         data_type: DOUBLE
>         description: Monthly regional return on ad spend from source; unit/scale preserved

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::DOUBLE AS "avg_roas"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#avg_roas`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/116302 | 0/435 |
| L1 | 4236/116952 | 4236/116568 | 0/384 |
| L2 | 4236/114023 | 4236/113609 | 0/414 |
| L3 | 4236/114023 | 4236/113609 | 0/414 |

### mart_created_at

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

mart_created_at整列NULL，契约给定monthly_regional_*映射或执行时间来源；属于可提供而未提供。avg_cpm单改格子差异反增，不能据此记参与。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: mart_created_at
>         data_type: TIMESTAMP WITH TIME ZONE
>         description: Model execution timestamp (CURRENT_TIMESTAMP) at build time; time zone preserved; non-deterministic across runs

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> NULL::TIMESTAMP WITH TIME ZONE AS "mart_created_at"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_region_report.json#mart_created_at`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/116737 | 4236/112501 | 0/4236 |
| L1 | 4236/116952 | 4236/112716 | 0/4236 |
| L2 | 4236/114023 | 4236/109787 | 0/4236 |
| L3 | 4236/114023 | 4236/109787 | 0/4236 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[10]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='intermediate' AND table_name='int_ad_reporting__monthly_campaign_region_report') ORDER BY table_schema,table_name,ordinal_position`。
