# impl-006_stg_linkedin_ads__campaign_report（038 正式表）

主要原因：**多因并列**；把握：高。020定稿旧主要原因：`多因并列（A、D）`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[963, 1001]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### click_through_rate

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

click_through_rate整列NULL，raw有clicks/impressions/cost_in_usd可计算。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "click_through_rate"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json#click_through_rate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/12765 | 1500/11265 | 0/1500 |
| L1 | 1500/12765 | 1500/11265 | 0/1500 |
| L2 | 1500/12765 | 1500/11265 | 0/1500 |
| L3 | 1500/12765 | 1500/11265 | 0/1500 |

### cost_per_click

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_click整列NULL，raw有clicks/impressions/cost_in_usd可计算。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_click"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json#cost_per_click`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/12765 | 1500/11265 | 0/1500 |
| L1 | 1500/12765 | 1500/11265 | 0/1500 |
| L2 | 1500/12765 | 1500/11265 | 0/1500 |
| L3 | 1500/12765 | 1500/11265 | 0/1500 |

### cost_per_thousand_impressions

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_thousand_impressions整列NULL，raw有clicks/impressions/cost_in_usd可计算。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_thousand_impressions"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json#cost_per_thousand_impressions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/12765 | 1500/11265 | 0/1500 |
| L1 | 1500/12765 | 1500/11265 | 0/1500 |
| L2 | 1500/12765 | 1500/11265 | 0/1500 |
| L3 | 1500/12765 | 1500/11265 | 0/1500 |

### sends

- 类别：Unstated Choice；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

raw无sends对应列，契约未规定缺源补0或NULL。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "sends"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`，`delivered SQL`：

> CAST(NULL::INTEGER AS INTEGER) AS sends

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json#sends`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/12765 | 1500/11265 | 0/1500 |
| L1 | 1500/12765 | 1500/11265 | 0/1500 |
| L2 | 1500/12765 | 1500/11265 | 0/1500 |
| L3 | 1500/12765 | 1500/11265 | 0/1500 |

### comments

- 类别：Unstated Choice；角色：参与；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

comments已有同名raw列，SQL确实尝试转换，没有整列直接填NULL；差异来自NULL/不可转文本补0还是保留NULL，契约未定政策。不能以gold补0证明原始缺失实际上为0。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "comments"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("comments" AS INTEGER) AS comments

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json#comments`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/12765 | 1500/11621 | 0/1144 |
| L1 | 1500/12765 | 1500/11621 | 0/1144 |
| L2 | 1500/12765 | 1500/11621 | 0/1144 |
| L3 | 1500/12765 | 1500/11621 | 0/1144 |

### follows

- 类别：Unstated Choice；角色：参与；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

follows已有同名raw列，SQL确实尝试转换，没有整列直接填NULL；差异来自NULL/不可转文本补0还是保留NULL，契约未定政策。不能以gold补0证明原始缺失实际上为0。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "follows"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("follows" AS INTEGER) AS follows

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json#follows`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/12765 | 1500/11658 | 0/1107 |
| L1 | 1500/12765 | 1500/11658 | 0/1107 |
| L2 | 1500/12765 | 1500/11658 | 0/1107 |
| L3 | 1500/12765 | 1500/11658 | 0/1107 |

### likes

- 类别：Unstated Choice；角色：参与；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

likes已有同名raw列，SQL确实尝试转换，没有整列直接填NULL；差异来自NULL/不可转文本补0还是保留NULL，契约未定政策。不能以gold补0证明原始缺失实际上为0。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "likes"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("likes" AS INTEGER) AS likes

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json#likes`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/12765 | 1500/11653 | 0/1112 |
| L1 | 1500/12765 | 1500/11653 | 0/1112 |
| L2 | 1500/12765 | 1500/11653 | 0/1112 |
| L3 | 1500/12765 | 1500/11653 | 0/1112 |

### shares

- 类别：Unstated Choice；角色：参与；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

shares已有同名raw列，SQL确实尝试转换，没有整列直接填NULL；差异来自NULL/不可转文本补0还是保留NULL，契约未定政策。不能以gold补0证明原始缺失实际上为0。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "shares"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("shares" AS INTEGER) AS shares

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json#shares`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/12765 | 1500/11650 | 0/1115 |
| L1 | 1500/12765 | 1500/11650 | 0/1115 |
| L2 | 1500/12765 | 1500/11650 | 0/1115 |
| L3 | 1500/12765 | 1500/11650 | 0/1115 |

### video_completions

- 类别：Unstated Choice；角色：参与；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

video_completions已有同名raw列，SQL确实尝试转换，没有整列直接填NULL；差异来自NULL/不可转文本补0还是保留NULL，契约未定政策。不能以gold补0证明原始缺失实际上为0。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "video_completions"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`，`delivered SQL`：

> TRY_CAST("video_completions" AS INTEGER) AS video_completions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json#video_completions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/12765 | 1500/11599 | 0/1166 |
| L1 | 1500/12765 | 1500/11599 | 0/1166 |
| L2 | 1500/12765 | 1500/11599 | 0/1166 |
| L3 | 1500/12765 | 1500/11599 | 0/1166 |

### video_views

- 类别：Unstated Choice；角色：参与；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

video_views已有同名raw列，SQL确实尝试转换，没有整列直接填NULL；差异来自NULL/不可转文本补0还是保留NULL，契约未定政策。不能以gold补0证明原始缺失实际上为0。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "video_views"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql`，`delivered SQL`：

> CAST(TRY_CAST("video_views" AS BIGINT) AS INTEGER) AS video_views

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json#video_views`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/12765 | 1500/11644 | 0/1121 |
| L1 | 1500/12765 | 1500/11644 | 0/1121 |
| L2 | 1500/12765 | 1500/11644 | 0/1121 |
| L3 | 1500/12765 | 1500/11644 | 0/1121 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[38]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='linkedin_ad_analytics_by_campaign_data') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[39]`：`SELECT count(*) n,count(*) FILTER(WHERE "comments" IS NULL) AS c0_null,count(*) FILTER(WHERE "comments" IS NOT NULL AND TRY_CAST("comments" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "follows" IS NULL) AS c2_null,count(*) FILTER(WHERE "follows" IS NOT NULL AND TRY_CAST("follows" AS DOUBLE) IS NULL) AS c3_not_numeric,count(*) FILTER(WHERE "impressions" IS NULL) AS c4_null,count(*) FILTER(WHERE "impressions" IS NOT NULL AND TRY_CAST("impressions" AS DOUBLE) IS NULL) AS c5_not_numeric,count(*) FILTER(WHERE "likes" IS NULL) AS c6_null,count(*) FILTER(WHERE "likes" IS NOT NULL AND TRY_CAST("likes" AS DOUBLE) IS NULL) AS c7_not_numeric,count(*) FILTER(WHERE "shares" IS NULL) AS c8_null,count(*) FILTER(WHERE "shares" IS NOT NULL AND TRY_CAST("shares" AS DOUBLE) IS NULL) AS c9_not_numeric,count(*) FILTER(WHERE "video_completions" IS NULL) AS c10_null,count(*) FILTER(WHERE "video_completions" IS NOT NULL AND TRY_CAST("video_completions" AS DOUBLE) IS NULL) AS c11_not_numeric,count(*) FILTER(WHERE "video_views" IS NULL) AS c12_null,count(*) FILTER(WHERE "video_views" IS NOT NULL AND TRY_CAST("video_views" AS DOUBLE) IS NULL) AS c13_not_numeric FROM raw.linkedin_ad_analytics_by_campaign_data`。

规则问题：Boolean文本/脏文本补0与Data边界见完整038报告。当前Choice不否认存在大量NULL；缺的是证明这些值可唯一恢复为某个数值的证据，不用gold反证。
