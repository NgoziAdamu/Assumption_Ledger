# impl-006_stg_twitter_ads__campaign_report（038 正式表）

主要原因：**多因并列**；把握：高。020定稿旧主要原因：`多因并列（A、D）`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[1263, 1336]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### app_installs_candidate

- 类别：Quiet Downgrade；角色：参与；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

raw确有mobile_conversion_installs_order_quantity及相关安装候选，agent不作判断就NULL，归降级。038只恢复该候选改善21格；020补0改善900格只是gold默认值诊断，不用于本点排序。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "app_installs"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::INTEGER AS INTEGER) AS app_installs

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/038_checks/rerun_impl-006_stg_twitter_ads__campaign_report.json#app_installs_candidate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/8110 | 900/8089 | 0/21 |
| L1 | 900/8110 | 900/8089 | 0/21 |
| L2 | 900/8110 | 900/8089 | 0/21 |
| L3 | 900/8110 | 900/8089 | 0/21 |

### app_opens

- 类别：Unstated Choice；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

完整raw列清单没有app_opens/open候选；安装/下载不等于打开，缺源填法未定。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "app_opens"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::INTEGER AS INTEGER) AS app_opens

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json#app_opens`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/8110 | 900/7210 | 0/900 |
| L1 | 900/8110 | 900/7210 | 0/900 |
| L2 | 900/8110 | 900/7210 | 0/900 |
| L3 | 900/8110 | 900/7210 | 0/900 |

### click_through_rate

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

click_through_rate整列NULL；raw有clicks/engagements/impressions/billed_charge_local_micro，候选和计算输入在场。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "click_through_rate"
>           data_type: DECIMAL(10,4)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(10,4) AS DECIMAL(10,4)) AS click_through_rate

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json#click_through_rate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/8110 | 900/7210 | 0/900 |
| L1 | 900/8110 | 900/7210 | 0/900 |
| L2 | 900/8110 | 900/7210 | 0/900 |
| L3 | 900/8110 | 900/7210 | 0/900 |

### cost_per_click

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_click整列NULL；raw有clicks/engagements/impressions/billed_charge_local_micro，候选和计算输入在场。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_click"
>           data_type: DECIMAL(18,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS cost_per_click

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json#cost_per_click`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/8110 | 900/7210 | 0/900 |
| L1 | 900/8110 | 900/7210 | 0/900 |
| L2 | 900/8110 | 900/7210 | 0/900 |
| L3 | 900/8110 | 900/7210 | 0/900 |

### cost_per_engagement

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_engagement整列NULL；raw有clicks/engagements/impressions/billed_charge_local_micro，候选和计算输入在场。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_engagement"
>           data_type: DECIMAL(18,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS cost_per_engagement

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json#cost_per_engagement`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/8110 | 900/7210 | 0/900 |
| L1 | 900/8110 | 900/7210 | 0/900 |
| L2 | 900/8110 | 900/7210 | 0/900 |
| L3 | 900/8110 | 900/7210 | 0/900 |

### cost_per_thousand_impressions

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_thousand_impressions整列NULL；raw有clicks/engagements/impressions/billed_charge_local_micro，候选和计算输入在场。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_thousand_impressions"
>           data_type: DECIMAL(18,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS cost_per_thousand_impressions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json#cost_per_thousand_impressions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/8110 | 900/7210 | 0/900 |
| L1 | 900/8110 | 900/7210 | 0/900 |
| L2 | 900/8110 | 900/7210 | 0/900 |
| L3 | 900/8110 | 900/7210 | 0/900 |

### engagement_rate

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

engagement_rate整列NULL；raw有clicks/engagements/impressions/billed_charge_local_micro，候选和计算输入在场。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "engagement_rate"
>           data_type: DECIMAL(10,4)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(10,4) AS DECIMAL(10,4)) AS engagement_rate

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json#engagement_rate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/8110 | 900/7210 | 0/900 |
| L1 | 900/8110 | 900/7210 | 0/900 |
| L2 | 900/8110 | 900/7210 | 0/900 |
| L3 | 900/8110 | 900/7210 | 0/900 |

### spend

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

spend整列NULL；raw有clicks/engagements/impressions/billed_charge_local_micro，候选和计算输入在场。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "spend"
>           data_type: DECIMAL(18,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json#spend`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/8110 | 900/7210 | 0/900 |
| L1 | 900/8110 | 900/7210 | 0/900 |
| L2 | 900/8110 | 900/7210 | 0/900 |
| L3 | 900/8110 | 900/7210 | 0/900 |

### follows

- 类别：Unstated Choice；角色：参与；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约只给数值类型，raw却使用true/false文本。NULL和映射1/0是不同的类型修复政策；布尔值不唯一确定金额/次数，不能只凭gold的1/0证明某个数值前提P。即使直接TRY_CAST大量失败，也不能从“有布尔值”推出“有可唯一恢复的金额/次数”；按第11节记Choice（中），详见规则问题。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "follows"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("follows" AS INTEGER) AS follows

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json#follows`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/8110 | 900/7657 | 0/453 |
| L1 | 900/8110 | 900/7657 | 0/453 |
| L2 | 900/8110 | 900/7657 | 0/453 |
| L3 | 900/8110 | 900/7657 | 0/453 |

### likes

- 类别：Unstated Choice；角色：参与；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约只给数值类型，raw却使用true/false文本。NULL和映射1/0是不同的类型修复政策；布尔值不唯一确定金额/次数，不能只凭gold的1/0证明某个数值前提P。即使直接TRY_CAST大量失败，也不能从“有布尔值”推出“有可唯一恢复的金额/次数”；按第11节记Choice（中），详见规则问题。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "likes"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_twitter_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("likes" AS INTEGER) AS likes

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_twitter_ads__campaign_report.json#likes`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 900/8110 | 900/7653 | 0/457 |
| L1 | 900/8110 | 900/7653 | 0/457 |
| L2 | 900/8110 | 900/7653 | 0/457 |
| L3 | 900/8110 | 900/7653 | 0/457 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[48]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='twitter_campaign_report_data') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[49]`：`SELECT count(*) n,count(*) FILTER(WHERE "follows" IS NULL) AS c0_null,count(*) FILTER(WHERE "follows" IS NOT NULL AND TRY_CAST("follows" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "impressions" IS NULL) AS c2_null,count(*) FILTER(WHERE "impressions" IS NOT NULL AND TRY_CAST("impressions" AS DOUBLE) IS NULL) AS c3_not_numeric,count(*) FILTER(WHERE "likes" IS NULL) AS c4_null,count(*) FILTER(WHERE "likes" IS NOT NULL AND TRY_CAST("likes" AS DOUBLE) IS NULL) AS c5_not_numeric FROM raw.twitter_campaign_report_data`。

- 新核实 `records/038_checks/new_verification.json`：`SELECT count(*) n, count(*) FILTER(WHERE mobile_conversion_installs_order_quantity IS NOT NULL) candidate_present, count(*) FILTER(WHERE try_cast(mobile_conversion_installs_order_quantity AS BIGINT)=0) candidate_zero FROM raw.twitter_campaign_report_data`；结果 `[[900, 900, 21]]`。累计3/5。

规则问题：Boolean文本/脏文本补0与Data边界见完整038报告。当前Choice不否认存在大量NULL；缺的是证明这些值可唯一恢复为某个数值的证据，不用gold反证。
