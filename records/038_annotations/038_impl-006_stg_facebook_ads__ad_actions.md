# impl-006_stg_facebook_ads__ad_actions（038 正式表）

主要原因：**Quiet Downgrade**；把握：高。020定稿旧主要原因：`D`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[581, 647]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_actions.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### action_1_d_view

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

action_1_d_view的raw候选分别为_1_d_view/_7_d_click/value/inline/index；候选存在却整列NULL。字段自身清理要求不能替整列放弃开脱。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "action_1_d_view"
>           data_type: DECIMAL(18,2)
>           validation_rules:
>             - rule: "action_1_d_view >= 0"
>               on_failure: correct
>             - rule: "action_1_d_view = ROUND(action_1_d_view, 2)"
>               on_failure: correct
>             - rule: "action_1_d_view IS NOT NULL OR action_1_d_view = 0"
>               on_failure: correct

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_actions.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS action_1_d_view

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_facebook_ads__ad_actions.json#action_1_d_view`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 700/3500 | 700/2800 | 0/700 |
| L1 | 700/3500 | 700/2800 | 0/700 |
| L2 | 700/3500 | 700/2800 | 0/700 |
| L3 | 700/3500 | 700/2800 | 0/700 |

### action_7_d_click

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

action_7_d_click的raw候选分别为_1_d_view/_7_d_click/value/inline/index；候选存在却整列NULL。字段自身清理要求不能替整列放弃开脱。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "action_7_d_click"
>           data_type: DECIMAL(18,2)
>           validation_rules:
>             - rule: "action_7_d_click >= 0"
>               on_failure: correct
>             - rule: "action_7_d_click = ROUND(action_7_d_click, 2)"
>               on_failure: correct
>             - rule: "action_7_d_click IS NOT NULL OR action_7_d_click = 0"
>               on_failure: correct

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_actions.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS action_7_d_click

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_facebook_ads__ad_actions.json#action_7_d_click`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 700/3500 | 700/2800 | 0/700 |
| L1 | 700/3500 | 700/2800 | 0/700 |
| L2 | 700/3500 | 700/2800 | 0/700 |
| L3 | 700/3500 | 700/2800 | 0/700 |

### action_value

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

action_value的raw候选分别为_1_d_view/_7_d_click/value/inline/index；候选存在却整列NULL。字段自身清理要求不能替整列放弃开脱。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "action_value"
>           data_type: DECIMAL(18,2)
>           validation_rules:
>             - rule: "action_value >= 0"
>               on_failure: correct
>             - rule: "action_value = ROUND(action_value, 2)"
>               on_failure: correct
>             - rule: "action_value IS NOT NULL OR action_value = 0"
>               on_failure: correct

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_actions.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS action_value

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_facebook_ads__ad_actions.json#action_value`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 700/3500 | 700/2800 | 0/700 |
| L1 | 700/3500 | 700/2800 | 0/700 |
| L2 | 700/3500 | 700/2800 | 0/700 |
| L3 | 700/3500 | 700/2800 | 0/700 |

### inline_value

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

inline_value的raw候选分别为_1_d_view/_7_d_click/value/inline/index；候选存在却整列NULL。字段自身清理要求不能替整列放弃开脱。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "inline_value"
>           data_type: DECIMAL(18,2)
>           validation_rules:
>             - rule: "inline_value >= 0"
>               on_failure: correct
>             - rule: "inline_value = ROUND(inline_value, 2)"
>               on_failure: correct
>             - rule: "inline_value IS NOT NULL OR inline_value = 0"
>               on_failure: correct

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_actions.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS inline_value

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_facebook_ads__ad_actions.json#inline_value`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 700/3500 | 700/2800 | 0/700 |
| L1 | 700/3500 | 700/2800 | 0/700 |
| L2 | 700/3500 | 700/2800 | 0/700 |
| L3 | 700/3500 | 700/2800 | 0/700 |

### is_index_action

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

is_index_action的raw候选分别为_1_d_view/_7_d_click/value/inline/index；候选存在却整列NULL。字段自身清理要求不能替整列放弃开脱。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "is_index_action"
>           data_type: BOOLEAN

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_actions.sql`，`delivered SQL`：

> CAST(NULL::BOOLEAN AS BOOLEAN) AS is_index_action

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_facebook_ads__ad_actions.json#is_index_action`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 700/3500 | 700/2800 | 0/700 |
| L1 | 700/3500 | 700/2800 | 0/700 |
| L2 | 700/3500 | 700/2800 | 0/700 |
| L3 | 700/3500 | 700/2800 | 0/700 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[28]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='facebook_ads_basic_ad_actions_data') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[29]`：`SELECT count(*) n,count(*) FILTER(WHERE "index" IS NULL) AS c0_null,count(*) FILTER(WHERE "index" IS NOT NULL AND TRY_CAST("index" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "_1_d_view" IS NULL) AS c2_null,count(*) FILTER(WHERE "_1_d_view" IS NOT NULL AND TRY_CAST("_1_d_view" AS DOUBLE) IS NULL) AS c3_not_numeric,count(*) FILTER(WHERE "_7_d_click" IS NULL) AS c4_null,count(*) FILTER(WHERE "_7_d_click" IS NOT NULL AND TRY_CAST("_7_d_click" AS DOUBLE) IS NULL) AS c5_not_numeric,count(*) FILTER(WHERE "inline" IS NULL) AS c6_null,count(*) FILTER(WHERE "inline" IS NOT NULL AND TRY_CAST("inline" AS DOUBLE) IS NULL) AS c7_not_numeric,count(*) FILTER(WHERE "value" IS NULL) AS c8_null,count(*) FILTER(WHERE "value" IS NOT NULL AND TRY_CAST("value" AS DOUBLE) IS NULL) AS c9_not_numeric FROM raw.facebook_ads_basic_ad_actions_data`。
