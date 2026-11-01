# impl-006_stg_apple_search_ads__ad_group_report（038 正式表）

主要原因：**多因并列**；把握：高。020定稿旧主要原因：`多因并列（C、D）`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[351, 447]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### avg_cpa_currency

- 类别：Intent Misreading；角色：并列；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约规定avg_cpa_currency须trim/upper后在USD/EUR/GBP/JPY/AUD/CAD中且长度3，否则nullify。038核实1500行均不在允许集，差异是非法值清理，不仅大小写呈现；按契约算法归Intent。

判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "avg_cpa_currency"
>           data_type: VARCHAR
>           validation_rules:
>             - rule: "avg_cpa_currency IS NULL OR avg_cpa_currency IN ('USD','EUR','GBP','JPY','AUD','CAD')"
>               on_failure: nullify_field
>             - rule: "LENGTH(avg_cpa_currency) <= 3"
>               on_failure: nullify_field
>             - rule: "avg_cpa_currency = UPPER(TRIM(avg_cpa_currency))"
>               on_failure: correct

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`，`delivered SQL`：

> TRY_CAST("avg_cpa_currency" AS VARCHAR) AS avg_cpa_currency

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "avg_cpa_currency"
>           data_type: VARCHAR
>           validation_rules:
>             - rule: "avg_cpa_currency IS NULL OR avg_cpa_currency IN ('USD','EUR','GBP','JPY','AUD','CAD')"
>               on_failure: nullify_field
>             - rule: "LENGTH(avg_cpa_currency) <= 3"
>               on_failure: nullify_field
>             - rule: "avg_cpa_currency = UPPER(TRIM(avg_cpa_currency))"
>               on_failure: correct

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json#avg_cpa_currency`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/8969 | 1500/7469 | 0/1500 |
| L1 | 1500/8969 | 1500/7469 | 0/1500 |
| L2 | 1500/8969 | 1500/7469 | 0/1500 |
| L3 | 1500/8969 | 1500/7469 | 0/1500 |

### avg_cpt_currency

- 类别：Intent Misreading；角色：并列；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约规定avg_cpt_currency须trim/upper后在USD/EUR/GBP/JPY/AUD/CAD中且长度3，否则nullify。038核实1500行均不在允许集，差异是非法值清理，不仅大小写呈现；按契约算法归Intent。

判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "avg_cpt_currency"
>           data_type: VARCHAR
>           validation_rules:
>             - rule: "avg_cpt_currency IS NULL OR avg_cpt_currency IN ('USD','EUR','GBP','JPY','AUD','CAD')"
>               on_failure: nullify_field
>             - rule: "LENGTH(avg_cpt_currency) <= 3"
>               on_failure: nullify_field
>             - rule: "avg_cpt_currency = UPPER(TRIM(avg_cpt_currency))"
>               on_failure: correct

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`，`delivered SQL`：

> TRY_CAST("avg_cpt_currency" AS VARCHAR) AS avg_cpt_currency

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "avg_cpt_currency"
>           data_type: VARCHAR
>           validation_rules:
>             - rule: "avg_cpt_currency IS NULL OR avg_cpt_currency IN ('USD','EUR','GBP','JPY','AUD','CAD')"
>               on_failure: nullify_field
>             - rule: "LENGTH(avg_cpt_currency) <= 3"
>               on_failure: nullify_field
>             - rule: "avg_cpt_currency = UPPER(TRIM(avg_cpt_currency))"
>               on_failure: correct

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json#avg_cpt_currency`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/8969 | 1500/7469 | 0/1500 |
| L1 | 1500/8969 | 1500/7469 | 0/1500 |
| L2 | 1500/8969 | 1500/7469 | 0/1500 |
| L3 | 1500/8969 | 1500/7469 | 0/1500 |

### conversion_rate

- 类别：Intent Misreading；角色：参与；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确0–1范围及nullify；未检查范围导致1469格差异。先适用契约算法，不因比例硬约束再记Data。

判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "conversion_rate"
>           data_type: DECIMAL(10,6)
>           validation_rules:
>             - rule: "conversion_rate BETWEEN 0 AND 1"
>               on_failure: nullify_field

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`，`delivered SQL`：

> TRY_CAST("conversion_rate" AS DECIMAL(10,6)) AS conversion_rate

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "conversion_rate"
>           data_type: DECIMAL(10,6)
>           validation_rules:
>             - rule: "conversion_rate BETWEEN 0 AND 1"
>               on_failure: nullify_field

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json#conversion_rate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/8969 | 1500/7500 | 0/1469 |
| L1 | 1500/8969 | 1500/7500 | 0/1469 |
| L2 | 1500/8969 | 1500/7500 | 0/1469 |
| L3 | 1500/8969 | 1500/7500 | 0/1469 |

### calculated_tap_through_rate

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

calculated_tap_through_rate整列NULL，raw有taps/impressions/conversions/local_spend_amount所需候选。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "calculated_tap_through_rate"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS calculated_tap_through_rate

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json#calculated_tap_through_rate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/8969 | 1500/7469 | 0/1500 |
| L1 | 1500/8969 | 1500/7469 | 0/1500 |
| L2 | 1500/8969 | 1500/7469 | 0/1500 |
| L3 | 1500/8969 | 1500/7469 | 0/1500 |

### cost_per_conversion

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_conversion整列NULL，raw有taps/impressions/conversions/local_spend_amount所需候选。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_conversion"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json#cost_per_conversion`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/8969 | 1500/7469 | 0/1500 |
| L1 | 1500/8969 | 1500/7469 | 0/1500 |
| L2 | 1500/8969 | 1500/7469 | 0/1500 |
| L3 | 1500/8969 | 1500/7469 | 0/1500 |

### cost_per_tap

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_tap整列NULL，raw有taps/impressions/conversions/local_spend_amount所需候选。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_tap"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_tap

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json#cost_per_tap`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1500/8969 | 1500/7469 | 0/1500 |
| L1 | 1500/8969 | 1500/7469 | 0/1500 |
| L2 | 1500/8969 | 1500/7469 | 0/1500 |
| L3 | 1500/8969 | 1500/7469 | 0/1500 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[22]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='apple_search_ad_group_report_data') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[23]`：`SELECT count(*) n,count(*) FILTER(WHERE "avg_cpa_currency" IS NULL) AS c0_null,count(*) FILTER(WHERE "avg_cpa_currency" IS NOT NULL AND TRY_CAST("avg_cpa_currency" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "avg_cpt_currency" IS NULL) AS c2_null,count(*) FILTER(WHERE "avg_cpt_currency" IS NOT NULL AND TRY_CAST("avg_cpt_currency" AS DOUBLE) IS NULL) AS c3_not_numeric,count(*) FILTER(WHERE "conversion_rate" IS NULL) AS c4_null,count(*) FILTER(WHERE "conversion_rate" IS NOT NULL AND TRY_CAST("conversion_rate" AS DOUBLE) IS NULL) AS c5_not_numeric,count(*) FILTER(WHERE "tap_through_rate" IS NULL) AS c6_null,count(*) FILTER(WHERE "tap_through_rate" IS NOT NULL AND TRY_CAST("tap_through_rate" AS DOUBLE) IS NULL) AS c7_not_numeric FROM raw.apple_search_ad_group_report_data`。

- 新核实 `records/038_checks/new_verification.json`：`SELECT count(*) n, count(*) FILTER(WHERE upper(trim(avg_cpa_currency)) IN ('USD','EUR','GBP','JPY','AUD','CAD')) valid_cpa, count(*) FILTER(WHERE upper(trim(avg_cpt_currency)) IN ('USD','EUR','GBP','JPY','AUD','CAD')) valid_cpt FROM raw.apple_search_ad_group_report_data`；结果 `[[1500, 0, 0]]`。累计3/5。
