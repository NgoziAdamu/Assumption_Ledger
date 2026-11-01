# impl-006_ad_reporting__monthly_campaign_country_report（038 正式表）

主要原因：**Quiet Downgrade**；把握：高。020定稿旧主要原因：`D`，仅原样保留。

## 范围与材料

- 层：marts。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[3798, 3909]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql`。

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
>         description: Monthly aggregated total cost.

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql`，`delivered SQL`：

> NULL::DECIMAL(38,2) AS "spend"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_country_report.json#spend`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/79205 | 4236/78117 | 0/1088 |
| L1 | 4236/79172 | 4236/78082 | 0/1090 |
| L2 | 4236/79134 | 4236/78044 | 0/1090 |
| L3 | 4236/79134 | 4236/78044 | 0/1090 |

### attributed_sales_14_day

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约已给attributed_sales_14_day的total_*透传来源，原始上游有对应列；fallback未正确使用映射而整列NULL。未见代码先明确写对该total_*映射后被覆盖的证据，不能套用staging的代码错误。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: attributed_sales_14_day
>         data_type: DECIMAL(38,2)
>         description: Monthly Amazon Ads 14-day attributed sales.

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql`，`delivered SQL`：

> NULL::DECIMAL(38,2) AS "attributed_sales_14_day"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_country_report.json#attributed_sales_14_day`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/79205 | 4236/77303 | 0/1902 |
| L1 | 4236/79172 | 4236/77824 | 0/1348 |
| L2 | 4236/79134 | 4236/77770 | 0/1364 |
| L3 | 4236/79134 | 4236/77770 | 0/1364 |

### attributed_sales_30_day

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约已给attributed_sales_30_day的total_*透传来源，原始上游有对应列；fallback未正确使用映射而整列NULL。未见代码先明确写对该total_*映射后被覆盖的证据，不能套用staging的代码错误。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: attributed_sales_30_day
>         data_type: DECIMAL(38,2)
>         description: Monthly Amazon Ads 30-day attributed sales.

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql`，`delivered SQL`：

> NULL::DECIMAL(38,2) AS "attributed_sales_30_day"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_country_report.json#attributed_sales_30_day`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/79205 | 4236/77777 | 0/1428 |
| L1 | 4236/79172 | 4236/77939 | 0/1233 |
| L2 | 4236/79134 | 4236/77887 | 0/1247 |
| L3 | 4236/79134 | 4236/77887 | 0/1247 |

### attributed_conversions_14_day

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约已给attributed_conversions_14_day的total_*透传来源，原始上游有对应列；fallback未正确使用映射而整列NULL。未见代码先明确写对该total_*映射后被覆盖的证据，不能套用staging的代码错误。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: attributed_conversions_14_day
>         data_type: HUGEINT
>         description: Monthly Amazon Ads 14-day attributed conversions.

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql`，`delivered SQL`：

> NULL::HUGEINT AS "attributed_conversions_14_day"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_country_report.json#attributed_conversions_14_day`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/79205 | 4236/43086 | 0/36119 |
| L1 | 4236/79172 | 4236/43275 | 0/35897 |
| L2 | 4236/79134 | 4236/43254 | 0/35880 |
| L3 | 4236/79134 | 4236/43254 | 0/35880 |

### attributed_conversions_30_day

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约已给attributed_conversions_30_day的total_*透传来源，原始上游有对应列；fallback未正确使用映射而整列NULL。未见代码先明确写对该total_*映射后被覆盖的证据，不能套用staging的代码错误。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: attributed_conversions_30_day
>         data_type: HUGEINT
>         description: Monthly Amazon Ads 30-day attributed conversions.

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql`，`delivered SQL`：

> NULL::HUGEINT AS "attributed_conversions_30_day"

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_country_report.json#attributed_conversions_30_day`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/79205 | 4236/43086 | 0/36119 |
| L1 | 4236/79172 | 4236/43275 | 0/35897 |
| L2 | 4236/79134 | 4236/43254 | 0/35880 |
| L3 | 4236/79134 | 4236/43254 | 0/35880 |

### placeholder_filter

- 类别：Intent Misreading；角色：非原因；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确排除platform=placeholder，SQL无该WHERE；新单改无改善，因此只是未落实的前提，不是本次判错原因。

判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: '- Read from intermediate.int_ad_reporting__monthly_campaign_country_report. - Column mappings (passthrough unless renamed): * month_year → report_month * total_impressions → impressions * total_clicks → clicks * total_interactions → interactions * total_cost → spend * total_conversions → conversions * total_conversions_value → conversions_value * total_view_through_conversions → view_through_conversions * total_attributed_sales_14_d → attributed_sales_14_day * total_attributed_sales_30_d → attributed_sales_30_day * total_attributed_conversions_14_d → attributed_conversions_14_day * total_attributed_conversions_30_d → attributed_conversions_30_day * total_active_view_impressions → active_view_impressions * total_active_view_measurable_impressions → active_view_measurable_impressions * monthly_click_through_rate → avg_ctr_percent * monthly_cost_per_click → avg_cpc * monthly_cost_per_thousand_impressions → avg_cpm * monthly_cost_per_conversion → avg_cpa * monthly_return_on_ad_spend → avg_roas * monthly_amazon_roas_30d → monthly_amazon_roas_30d * _dbt_loaded_at → data_last_updated - Compute mart_created_at using CURRENT_TIMESTAMP at execution time; identical across all rows within a single run. - Exclude rows where platform = ''placeholder''. - No additional aggregation, de-duplication, or transformations; all values and NULLs are passed through from the source. - Output ordering: platform ASC, account_id ASC, campaign_id ASC, report_month DESC, spend DESC.'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql`，`delivered SQL`：

> FROM intermediate.int_ad_reporting__monthly_campaign_country_report

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: '- Read from intermediate.int_ad_reporting__monthly_campaign_country_report. - Column mappings (passthrough unless renamed): * month_year → report_month * total_impressions → impressions * total_clicks → clicks * total_interactions → interactions * total_cost → spend * total_conversions → conversions * total_conversions_value → conversions_value * total_view_through_conversions → view_through_conversions * total_attributed_sales_14_d → attributed_sales_14_day * total_attributed_sales_30_d → attributed_sales_30_day * total_attributed_conversions_14_d → attributed_conversions_14_day * total_attributed_conversions_30_d → attributed_conversions_30_day * total_active_view_impressions → active_view_impressions * total_active_view_measurable_impressions → active_view_measurable_impressions * monthly_click_through_rate → avg_ctr_percent * monthly_cost_per_click → avg_cpc * monthly_cost_per_thousand_impressions → avg_cpm * monthly_cost_per_conversion → avg_cpa * monthly_return_on_ad_spend → avg_roas * monthly_amazon_roas_30d → monthly_amazon_roas_30d * _dbt_loaded_at → data_last_updated - Compute mart_created_at using CURRENT_TIMESTAMP at execution time; identical across all rows within a single run. - Exclude rows where platform = ''placeholder''. - No additional aggregation, de-duplication, or transformations; all values and NULLs are passed through from the source. - Output ordering: platform ASC, account_id ASC, campaign_id ASC, report_month DESC, spend DESC.'

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/038_checks/rerun_impl-006_ad_reporting__monthly_campaign_country_report.json#placeholder_filter`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4236/79205 | 4236/79205 | 0/0 |
| L1 | 4236/79172 | 4236/79172 | 0/0 |
| L2 | 4236/79134 | 4236/79134 | 0/0 |
| L3 | 4236/79134 | 4236/79134 | 0/0 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[9]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='intermediate' AND table_name='int_ad_reporting__monthly_campaign_country_report') ORDER BY table_schema,table_name,ordinal_position`。
