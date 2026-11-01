# impl-006_stg_tiktok_ads__campaign_report（038 正式表）

主要原因：**Unstated Choice**；把握：高。020定稿旧主要原因：`A`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[1204, 1262]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### advertiser_id

- 类别：Unstated Choice；角色：主要；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

raw没有advertiser_id候选；NULL还是unknown未规定。该列参与评测键，补默认值可大幅改变差异规模，但这不证明unknown是唯一正确值。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "advertiser_id"
>           data_type: VARCHAR

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::VARCHAR AS VARCHAR) AS advertiser_id

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_tiktok_ads__campaign_report.json#advertiser_id`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 900/9009 | 900/39591 |
| L1 | 1800/48600 | 900/9009 | 900/39591 |
| L2 | 1800/48600 | 900/9009 | 900/39591 |
| L3 | 1800/48600 | 900/9009 | 900/39591 |

### spend_mapping_restore

- 类别：代码写错；角色：非原因；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

event19的special字典同键先写正确候选、后写同键覆盖，导致正确候选消失；这是代码自身可证明的正确意图未实现，归代码写错。020_resume恢复原候选实验复用。

判定顺序：第3节第1步由正确映射被覆盖的代码证据排除前提类。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "spend"
>           data_type: DECIMAL(18,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

代码正确意图证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/19.json`，`19.args.command`：

>    'date_day':['date','day','stat_time_hour'],'cost':['cost','spend','local_spend_amount','cost_in_usd'],'spend':['spend','local_spend_amount'],'impressions':['impressions','impression_1'],'clicks':['clicks','inline_link_clicks','taps'],'ad_group_id':['ad_group_id','base_ad_group'],'campaign_id':['campaign_id','id'],'account_id':['customer_id','account_id'],

代码正确意图证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/19.json`，`19.args.command`：

>    'spend_currency':['local_spend_currency'],'avg_cost_per_tap':['avg_cpt_amount'],'avg_cost_per_acquisition':['avg_cpa_amount'],'avg_cpt_currency':['avg_cpt_currency'],'avg_cpa_currency':['avg_cpa_currency'],'spend':['local_spend_amount'],

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_resume_reruns_impl-006_stg_tiktok_ads__campaign_report.json#spend_restore_overwritten_mapping`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

### conversions

- 类别：Quiet Downgrade；角色：非原因；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

conversions整列NULL，raw有CONVERSION或SPEND/CLICKS/IMPRESSIONS/REACH候选；单改无改善，键差异掩盖，非参与。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "conversions"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::INTEGER AS INTEGER) AS conversions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_tiktok_ads__campaign_report.json#conversions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

### calculated_cost_per_click

- 类别：Quiet Downgrade；角色：非原因；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

calculated_cost_per_click整列NULL，raw有CONVERSION或SPEND/CLICKS/IMPRESSIONS/REACH候选；单改无改善，键差异掩盖，非参与。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "calculated_cost_per_click"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS calculated_cost_per_click

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_tiktok_ads__campaign_report.json#calculated_cost_per_click`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

### cost_per_thousand_impressions

- 类别：Quiet Downgrade；角色：非原因；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_thousand_impressions整列NULL，raw有CONVERSION或SPEND/CLICKS/IMPRESSIONS/REACH候选；单改无改善，键差异掩盖，非参与。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_thousand_impressions"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_tiktok_ads__campaign_report.json#cost_per_thousand_impressions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

### cost_per_thousand_reached

- 类别：Quiet Downgrade；角色：非原因；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_thousand_reached整列NULL，raw有CONVERSION或SPEND/CLICKS/IMPRESSIONS/REACH候选；单改无改善，键差异掩盖，非参与。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_thousand_reached"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_reached

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_tiktok_ads__campaign_report.json#cost_per_thousand_reached`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

### follows_invalid_policy

- 类别：Unstated Choice；角色：非原因；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

follows已有raw列且执行TRY_CAST，差异是不可转文本或NULL补0政策。038核实CTR和COST_PER_CONVERSION均900个非数值且非布尔文本，其他四列有布尔文本和缺失；无法从这些文本唯一恢复真实数值。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "follows"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("FOLLOWS" AS INTEGER) AS follows

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/038_checks/rerun_impl-006_stg_tiktok_ads__campaign_report.json#follows_invalid_policy`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

### likes_invalid_policy

- 类别：Unstated Choice；角色：非原因；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

likes已有raw列且执行TRY_CAST，差异是不可转文本或NULL补0政策。038核实CTR和COST_PER_CONVERSION均900个非数值且非布尔文本，其他四列有布尔文本和缺失；无法从这些文本唯一恢复真实数值。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "likes"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("LIKES" AS INTEGER) AS likes

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/038_checks/rerun_impl-006_stg_tiktok_ads__campaign_report.json#likes_invalid_policy`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

### comments_invalid_policy

- 类别：Unstated Choice；角色：非原因；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

comments已有raw列且执行TRY_CAST，差异是不可转文本或NULL补0政策。038核实CTR和COST_PER_CONVERSION均900个非数值且非布尔文本，其他四列有布尔文本和缺失；无法从这些文本唯一恢复真实数值。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "comments"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("COMMENTS" AS INTEGER) AS comments

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/038_checks/rerun_impl-006_stg_tiktok_ads__campaign_report.json#comments_invalid_policy`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

### shares_invalid_policy

- 类别：Unstated Choice；角色：非原因；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

shares已有raw列且执行TRY_CAST，差异是不可转文本或NULL补0政策。038核实CTR和COST_PER_CONVERSION均900个非数值且非布尔文本，其他四列有布尔文本和缺失；无法从这些文本唯一恢复真实数值。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "shares"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("SHARES" AS INTEGER) AS shares

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/038_checks/rerun_impl-006_stg_tiktok_ads__campaign_report.json#shares_invalid_policy`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

### click_through_rate_invalid_policy

- 类别：Unstated Choice；角色：非原因；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

click_through_rate已有raw列且执行TRY_CAST，差异是不可转文本或NULL补0政策。038核实CTR和COST_PER_CONVERSION均900个非数值且非布尔文本，其他四列有布尔文本和缺失；无法从这些文本唯一恢复真实数值。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "click_through_rate"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("CTR" AS DOUBLE) AS click_through_rate

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/038_checks/rerun_impl-006_stg_tiktok_ads__campaign_report.json#click_through_rate_invalid_policy`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

### cost_per_conversion_invalid_policy

- 类别：Unstated Choice；角色：非原因；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_conversion已有raw列且执行TRY_CAST，差异是不可转文本或NULL补0政策。038核实CTR和COST_PER_CONVERSION均900个非数值且非布尔文本，其他四列有布尔文本和缺失；无法从这些文本唯一恢复真实数值。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_conversion"
>           data_type: DECIMAL(18,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("COST_PER_CONVERSION" AS DECIMAL(18,2)) AS cost_per_conversion

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/038_checks/rerun_impl-006_stg_tiktok_ads__campaign_report.json#cost_per_conversion_invalid_policy`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1800/48600 | 1800/48600 | 0/0 |
| L1 | 1800/48600 | 1800/48600 | 0/0 |
| L2 | 1800/48600 | 1800/48600 | 0/0 |
| L3 | 1800/48600 | 1800/48600 | 0/0 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[46]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='tiktok_campaign_report_hourly_data') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[47]`：`SELECT count(*) n,count(*) FILTER(WHERE "STAT_TIME_HOUR" IS NULL) AS c0_null,count(*) FILTER(WHERE "STAT_TIME_HOUR" IS NOT NULL AND TRY_CAST("STAT_TIME_HOUR" AS DOUBLE) IS NULL) AS c1_not_numeric FROM raw.tiktok_campaign_report_hourly_data`。

- 新核实 `records/038_checks/new_verification.json`：`SELECT count(*) n,count(*) FILTER(WHERE "FOLLOWS" IS NULL) "FOLLOWS_null", count(*) FILTER(WHERE "FOLLOWS" IS NOT NULL AND try_cast("FOLLOWS" AS DOUBLE) IS NULL) "FOLLOWS_invalid_numeric", count(*) FILTER(WHERE "FOLLOWS" IN ('true','false')) "FOLLOWS_bool",count(*) FILTER(WHERE "LIKES" IS NULL) "LIKES_null", count(*) FILTER(WHERE "LIKES" IS NOT NULL AND try_cast("LIKES" AS DOUBLE) IS NULL) "LIKES_invalid_numeric", count(*) FILTER(WHERE "LIKES" IN ('true','false')) "LIKES_bool",count(*) FILTER(WHERE "COMMENTS" IS NULL) "COMMENTS_null", count(*) FILTER(WHERE "COMMENTS" IS NOT NULL AND try_cast("COMMENTS" AS DOUBLE) IS NULL) "COMMENTS_invalid_numeric", count(*) FILTER(WHERE "COMMENTS" IN ('true','false')) "COMMENTS_bool",count(*) FILTER(WHERE "SHARES" IS NULL) "SHARES_null", count(*) FILTER(WHERE "SHARES" IS NOT NULL AND try_cast("SHARES" AS DOUBLE) IS NULL) "SHARES_invalid_numeric", count(*) FILTER(WHERE "SHARES" IN ('true','false')) "SHARES_bool",count(*) FILTER(WHERE "CTR" IS NULL) "CTR_null", count(*) FILTER(WHERE "CTR" IS NOT NULL AND try_cast("CTR" AS DOUBLE) IS NULL) "CTR_invalid_numeric", count(*) FILTER(WHERE "CTR" IN ('true','false')) "CTR_bool",count(*) FILTER(WHERE "COST_PER_CONVERSION" IS NULL) "COST_PER_CONVERSION_null", count(*) FILTER(WHERE "COST_PER_CONVERSION" IS NOT NULL AND try_cast("COST_PER_CONVERSION" AS DOUBLE) IS NULL) "COST_PER_CONVERSION_invalid_numeric", count(*) FILTER(WHERE "COST_PER_CONVERSION" IN ('true','false')) "COST_PER_CONVERSION_bool" FROM raw.tiktok_campaign_report_hourly_data`；结果 `[[900, 216, 447, 447, 202, 479, 479, 234, 452, 452, 242, 437, 437, 0, 900, 0, 0, 900, 0]]`。累计3/5。

规则问题：Boolean文本/脏文本补0与Data边界见完整038报告。当前Choice不否认存在大量NULL；缺的是证明这些值可唯一恢复为某个数值的证据，不用gold反证。
