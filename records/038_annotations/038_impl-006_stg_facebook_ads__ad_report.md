# impl-006_stg_facebook_ads__ad_report（038 正式表）

主要原因：**多因并列**；把握：高。020定稿旧主要原因：`多因并列（D、I）`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[648, 698]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_report.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### click_through_rate

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

click_through_rate有clicks/impressions/spend候选而整列NULL。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "click_through_rate"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_report.sql`，`delivered SQL`：

> CAST(NULL::INTEGER AS INTEGER) AS click_through_rate

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_facebook_ads__ad_report.json#click_through_rate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1000/4000 | 1000/3000 | 0/1000 |
| L1 | 1000/4000 | 1000/3000 | 0/1000 |
| L2 | 1000/4000 | 1000/3000 | 0/1000 |
| L3 | 1000/4000 | 1000/3000 | 0/1000 |

### cost_per_click

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_click有clicks/impressions/spend候选而整列NULL。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_click"
>           data_type: INTEGER

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_report.sql`，`delivered SQL`：

> CAST(NULL::INTEGER AS INTEGER) AS cost_per_click

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_facebook_ads__ad_report.json#cost_per_click`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1000/4000 | 1000/3000 | 0/1000 |
| L1 | 1000/4000 | 1000/3000 | 0/1000 |
| L2 | 1000/4000 | 1000/3000 | 0/1000 |
| L3 | 1000/4000 | 1000/3000 | 0/1000 |

### cost_per_thousand_impressions

- 类别：Quiet Downgrade；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

cost_per_thousand_impressions有clicks/impressions/spend候选而整列NULL。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "cost_per_thousand_impressions"
>           data_type: DOUBLE

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_report.sql`，`delivered SQL`：

> CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_stg_facebook_ads__ad_report.json#cost_per_thousand_impressions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1000/4000 | 1000/3000 | 0/1000 |
| L1 | 1000/4000 | 1000/3000 | 0/1000 |
| L2 | 1000/4000 | 1000/3000 | 0/1000 |
| L3 | 1000/4000 | 1000/3000 | 0/1000 |

### spend_mapping_restore

- 类别：代码写错；角色：并列；把握：高。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

event19的special字典同键先写正确候选、后写同键覆盖，导致正确候选消失；这是代码自身可证明的正确意图未实现，归代码写错。020_resume恢复原候选实验复用。

判定顺序：第3节第1步由正确映射被覆盖的代码证据排除前提类。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "spend"
>           data_type: DECIMAL(18,2)
>           validation_rules:
>             - rule: "spend >= 0 AND spend <= 999999999999.99"
>               on_failure: correct
>             - rule: "spend = ROUND(spend, 2)"
>               on_failure: correct

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_report.sql`，`delivered SQL`：

> CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

代码正确意图证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/19.json`，`19.args.command`：

>    'date_day':['date','day','stat_time_hour'],'cost':['cost','spend','local_spend_amount','cost_in_usd'],'spend':['spend','local_spend_amount'],'impressions':['impressions','impression_1'],'clicks':['clicks','inline_link_clicks','taps'],'ad_group_id':['ad_group_id','base_ad_group'],'campaign_id':['campaign_id','id'],'account_id':['customer_id','account_id'],

代码正确意图证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/19.json`，`19.args.command`：

>    'spend_currency':['local_spend_currency'],'avg_cost_per_tap':['avg_cpt_amount'],'avg_cost_per_acquisition':['avg_cpa_amount'],'avg_cpt_currency':['avg_cpt_currency'],'avg_cpa_currency':['avg_cpa_currency'],'spend':['local_spend_amount'],

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_resume_reruns_impl-006_stg_facebook_ads__ad_report.json#spend_restore_overwritten_mapping`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1000/4000 | 1000/3000 | 0/1000 |
| L1 | 1000/4000 | 1000/3000 | 0/1000 |
| L2 | 1000/4000 | 1000/3000 | 0/1000 |
| L3 | 1000/4000 | 1000/3000 | 0/1000 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[30]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='facebook_ads_basic_ad_data') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[31]`：`SELECT count(*) n,count(*) FILTER(WHERE "impressions" IS NULL) AS c0_null,count(*) FILTER(WHERE "impressions" IS NOT NULL AND TRY_CAST("impressions" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "spend" IS NULL) AS c2_null,count(*) FILTER(WHERE "spend" IS NOT NULL AND TRY_CAST("spend" AS DOUBLE) IS NULL) AS c3_not_numeric FROM raw.facebook_ads_basic_ad_data`。
