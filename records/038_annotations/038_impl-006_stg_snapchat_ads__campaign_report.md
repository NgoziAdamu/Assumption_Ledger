# impl-006_stg_snapchat_ads__campaign_report（038 正式表）

主要原因：**多因并列**；把握：中。020定稿旧主要原因：`多因并列（A、D、I）`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[1149, 1203]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### ad_account_id

- 类别：Unstated Choice；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

raw没有账户ID候选；契约未指定unknown或NULL。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "ad_account_id"
>           data_type: VARCHAR

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::VARCHAR AS VARCHAR) AS ad_account_id

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#ad_account_id`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### spend_mapping_restore

- 类别：代码写错；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

event19的special字典同键先写正确候选、后写同键覆盖，导致正确候选消失；这是代码自身可证明的正确意图未实现，归代码写错。020_resume恢复原候选实验复用。

判定顺序：第3节第1步由正确映射被覆盖的代码证据排除前提类。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "spend"
>           data_type: DECIMAL(18,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

代码正确意图证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/19.json`，`19.args.command`：

>    'date_day':['date','day','stat_time_hour'],'cost':['cost','spend','local_spend_amount','cost_in_usd'],'spend':['spend','local_spend_amount'],'impressions':['impressions','impression_1'],'clicks':['clicks','inline_link_clicks','taps'],'ad_group_id':['ad_group_id','base_ad_group'],'campaign_id':['campaign_id','id'],'account_id':['customer_id','account_id'],

代码正确意图证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/19.json`，`19.args.command`：

>    'spend_currency':['local_spend_currency'],'avg_cost_per_tap':['avg_cpt_amount'],'avg_cost_per_acquisition':['avg_cpa_amount'],'avg_cpt_currency':['avg_cpt_currency'],'avg_cpa_currency':['avg_cpa_currency'],'spend':['local_spend_amount'],

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_resume_reruns_impl-006_stg_snapchat_ads__campaign_report.json#spend_restore_overwritten_mapping`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### cost_per_install

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_install整列NULL，raw有spend/swipes/impressions/video_views/conversion_app_installs等候选，不能视作缺源。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_install"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_install

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#cost_per_install`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### cost_per_swipe

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_swipe整列NULL，raw有spend/swipes/impressions/video_views/conversion_app_installs等候选，不能视作缺源。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_swipe"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_swipe

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#cost_per_swipe`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### cost_per_thousand_impressions

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_thousand_impressions整列NULL，raw有spend/swipes/impressions/video_views/conversion_app_installs等候选，不能视作缺源。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_thousand_impressions"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#cost_per_thousand_impressions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### cost_per_video_view

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_video_view整列NULL，raw有spend/swipes/impressions/video_views/conversion_app_installs等候选，不能视作缺源。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_video_view"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_video_view

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#cost_per_video_view`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### swipe_up_rate

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

swipe_up_rate整列NULL，raw有spend/swipes/impressions/video_views/conversion_app_installs等候选，不能视作缺源。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "swipe_up_rate"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS swipe_up_rate

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#swipe_up_rate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### conversion_purchases

- 类别：Unstated Choice；角色：并列；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

conversion_purchases同名raw列被TRY_CAST处理；差异来自缺失/不可转文本是否补0，契约未定。0不是由原数据唯一恢复的数值，不成立可被证伪的数据前提P。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "conversion_purchases"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("conversion_purchases" AS INTEGER) AS conversion_purchases

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#conversion_purchases`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### quartile_1

- 类别：Unstated Choice；角色：并列；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

quartile_1同名raw列被TRY_CAST处理；差异来自缺失/不可转文本是否补0，契约未定。0不是由原数据唯一恢复的数值，不成立可被证伪的数据前提P。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "quartile_1"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("quartile_1" AS INTEGER) AS quartile_1

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#quartile_1`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### quartile_2

- 类别：Unstated Choice；角色：并列；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

quartile_2同名raw列被TRY_CAST处理；差异来自缺失/不可转文本是否补0，契约未定。0不是由原数据唯一恢复的数值，不成立可被证伪的数据前提P。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "quartile_2"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("quartile_2" AS INTEGER) AS quartile_2

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#quartile_2`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### quartile_3

- 类别：Unstated Choice；角色：并列；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

quartile_3同名raw列被TRY_CAST处理；差异来自缺失/不可转文本是否补0，契约未定。0不是由原数据唯一恢复的数值，不成立可被证伪的数据前提P。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "quartile_3"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("quartile_3" AS INTEGER) AS quartile_3

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#quartile_3`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### screen_time_millis

- 类别：Unstated Choice；角色：并列；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

screen_time_millis同名raw列被TRY_CAST处理；差异来自缺失/不可转文本是否补0，契约未定。0不是由原数据唯一恢复的数值，不成立可被证伪的数据前提P。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "screen_time_millis"
>           data_type: BIGINT

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("screen_time_millis" AS BIGINT) AS screen_time_millis

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#screen_time_millis`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### shares

- 类别：Unstated Choice；角色：参与；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

shares同名raw列被TRY_CAST处理；差异来自缺失/不可转文本是否补0，契约未定。0不是由原数据唯一恢复的数值，不成立可被证伪的数据前提P。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "shares"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("shares" AS INTEGER) AS shares

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#shares`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13285 | 0/673 |
| L1 | 900/13958 | 900/13285 | 0/673 |
| L2 | 900/13958 | 900/13285 | 0/673 |
| L3 | 900/13958 | 900/13285 | 0/673 |

### story_completes

- 类别：Unstated Choice；角色：并列；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

story_completes同名raw列被TRY_CAST处理；差异来自缺失/不可转文本是否补0，契约未定。0不是由原数据唯一恢复的数值，不成立可被证伪的数据前提P。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "story_completes"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("story_completes" AS INTEGER) AS story_completes

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#story_completes`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

### video_views

- 类别：Unstated Choice；角色：参与；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

video_views同名raw列被TRY_CAST处理；差异来自缺失/不可转文本是否补0，契约未定。0不是由原数据唯一恢复的数值，不成立可被证伪的数据前提P。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "video_views"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> CAST(TRY_CAST("video_views" AS BIGINT) AS INTEGER) AS video_views

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#video_views`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13273 | 0/685 |
| L1 | 900/13958 | 900/13273 | 0/685 |
| L2 | 900/13958 | 900/13273 | 0/685 |
| L3 | 900/13958 | 900/13273 | 0/685 |

### view_completion

- 类别：Unstated Choice；角色：并列；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

view_completion同名raw列被TRY_CAST处理；差异来自缺失/不可转文本是否补0，契约未定。0不是由原数据唯一恢复的数值，不成立可被证伪的数据前提P。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "view_completion"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("view_completion" AS INTEGER) AS view_completion

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json#view_completion`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/13958 | 900/13058 | 0/900 |
| L1 | 900/13958 | 900/13058 | 0/900 |
| L2 | 900/13958 | 900/13058 | 0/900 |
| L3 | 900/13958 | 900/13058 | 0/900 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[44]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='snapchat_campaign_hourly_report_data') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[45]`：`SELECT count(*) n,count(*) FILTER(WHERE "conversion_purchases" IS NULL) AS c0_null,count(*) FILTER(WHERE "conversion_purchases" IS NOT NULL AND TRY_CAST("conversion_purchases" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "impressions" IS NULL) AS c2_null,count(*) FILTER(WHERE "impressions" IS NOT NULL AND TRY_CAST("impressions" AS DOUBLE) IS NULL) AS c3_not_numeric,count(*) FILTER(WHERE "quartile_1" IS NULL) AS c4_null,count(*) FILTER(WHERE "quartile_1" IS NOT NULL AND TRY_CAST("quartile_1" AS DOUBLE) IS NULL) AS c5_not_numeric,count(*) FILTER(WHERE "quartile_2" IS NULL) AS c6_null,count(*) FILTER(WHERE "quartile_2" IS NOT NULL AND TRY_CAST("quartile_2" AS DOUBLE) IS NULL) AS c7_not_numeric,count(*) FILTER(WHERE "quartile_3" IS NULL) AS c8_null,count(*) FILTER(WHERE "quartile_3" IS NOT NULL AND TRY_CAST("quartile_3" AS DOUBLE) IS NULL) AS c9_not_numeric,count(*) FILTER(WHERE "screen_time_millis" IS NULL) AS c10_null,count(*) FILTER(WHERE "screen_time_millis" IS NOT NULL AND TRY_CAST("screen_time_millis" AS DOUBLE) IS NULL) AS c11_not_numeric,count(*) FILTER(WHERE "shares" IS NULL) AS c12_null,count(*) FILTER(WHERE "shares" IS NOT NULL AND TRY_CAST("shares" AS DOUBLE) IS NULL) AS c13_not_numeric,count(*) FILTER(WHERE "spend" IS NULL) AS c14_null,count(*) FILTER(WHERE "spend" IS NOT NULL AND TRY_CAST("spend" AS DOUBLE) IS NULL) AS c15_not_numeric,count(*) FILTER(WHERE "story_completes" IS NULL) AS c16_null,count(*) FILTER(WHERE "story_completes" IS NOT NULL AND TRY_CAST("story_completes" AS DOUBLE) IS NULL) AS c17_not_numeric,count(*) FILTER(WHERE "video_views" IS NULL) AS c18_null,count(*) FILTER(WHERE "video_views" IS NOT NULL AND TRY_CAST("video_views" AS DOUBLE) IS NULL) AS c19_not_numeric,count(*) FILTER(WHERE "view_completion" IS NULL) AS c20_null,count(*) FILTER(WHERE "view_completion" IS NOT NULL AND TRY_CAST("view_completion" AS DOUBLE) IS NULL) AS c21_not_numeric FROM raw.snapchat_campaign_hourly_report_data`。

规则问题：Boolean文本/脏文本补0与Data边界见完整038报告。当前Choice不否认存在大量NULL；缺的是证明这些值可唯一恢复为某个数值的证据，不用gold反证。
