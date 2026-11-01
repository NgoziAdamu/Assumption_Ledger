# impl-006_stg_google_ads__ad_group_report（038 正式表）

主要原因：**Unstated Choice**；把握：中。020定稿旧主要原因：`A`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[733, 769]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_google_ads__ad_group_report.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### ad_group_id

- 类别：Unstated Choice；角色：主要；把握：中。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约没有源列映射。raw.id仅15/715匹配history，base_ad_group原字符串0匹配、提取末段却715/715匹配；不足以唯一确立raw.id。gold选择id只是选择证据，不能定Data。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "ad_group_id"
>           data_type: VARCHAR(20)
>           constraints: [not_null]

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_google_ads__ad_group_report.sql`，`delivered SQL`：

> CAST(TRY_CAST("base_ad_group" AS VARCHAR) AS VARCHAR(20)) AS ad_group_id

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "ad_group_id"
>           data_type: VARCHAR(20)
>           constraints: [not_null]

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-006_stg_google_ads__ad_group_report.json#ad_group_id`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1430/14300 | 705/2099 | 725/12201 |
| L1 | 1430/14300 | 705/2099 | 725/12201 |
| L2 | 1430/14300 | 705/2099 | 725/12201 |
| L3 | 1430/14300 | 705/2099 | 725/12201 |

### conversions_value

- 类别：Unstated Choice；角色：非原因；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约只给数值类型，raw却使用true/false文本。NULL和映射1/0是不同的类型修复政策；布尔值不唯一确定金额/次数，不能只凭gold的1/0证明某个数值前提P。即使直接TRY_CAST大量失败，也不能从“有布尔值”推出“有可唯一恢复的金额/次数”；按第11节记Choice（中），详见规则问题。此表5条复用核实预算已用完，没有新增核实；038单改仅量化被键选择掩盖的差异。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "conversions_value"
>           data_type: DECIMAL(15,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_google_ads__ad_group_report.sql`，`delivered SQL`：

> TRY_CAST("conversions_value" AS DECIMAL(15,2)) AS conversions_value

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/038_checks/rerun_impl-006_stg_google_ads__ad_group_report.json#conversions_value`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1430/14300 | 1430/14300 | 0/0 |
| L1 | 1430/14300 | 1430/14300 | 0/0 |
| L2 | 1430/14300 | 1430/14300 | 0/0 |
| L3 | 1430/14300 | 1430/14300 | 0/0 |

### view_through_conversions

- 类别：Unstated Choice；角色：非原因；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约只给数值类型，raw却使用true/false文本。NULL和映射1/0是不同的类型修复政策；布尔值不唯一确定金额/次数，不能只凭gold的1/0证明某个数值前提P。即使直接TRY_CAST大量失败，也不能从“有布尔值”推出“有可唯一恢复的金额/次数”；按第11节记Choice（中），详见规则问题。此表5条复用核实预算已用完，没有新增核实；038单改仅量化被键选择掩盖的差异。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "view_through_conversions"
>           data_type: BIGINT

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_google_ads__ad_group_report.sql`，`delivered SQL`：

> TRY_CAST("view_through_conversions" AS BIGINT) AS view_through_conversions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/038_checks/rerun_impl-006_stg_google_ads__ad_group_report.json#view_through_conversions`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1430/14300 | 1430/14300 | 0/0 |
| L1 | 1430/14300 | 1430/14300 | 0/0 |
| L2 | 1430/14300 | 1430/14300 | 0/0 |
| L3 | 1430/14300 | 1430/14300 | 0/0 |

### conversions_decimal

- 类别：Intent Misreading；角色：非原因；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约要求DECIMAL(10,2)，SQL先BIGINT后DECIMAL使小数转换数被舍去；移除中途整数化是落实数值规格，不是只换输出类型标签。

判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。

存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "conversions"
>           data_type: DECIMAL(10,2)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_google_ads__ad_group_report.sql`，`delivered SQL`：

> CAST(TRY_CAST("conversions" AS BIGINT) AS DECIMAL(10,2)) AS conversions

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> - name: "conversions"
>           data_type: DECIMAL(10,2)

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/038_checks/rerun_impl-006_stg_google_ads__ad_group_report.json#conversions_decimal`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1430/14300 | 1430/14300 | 0/0 |
| L1 | 1430/14300 | 1430/14300 | 0/0 |
| L2 | 1430/14300 | 1430/14300 | 0/0 |
| L3 | 1430/14300 | 1430/14300 | 0/0 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[34]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='google_ads_ad_group_stats_data') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[35]`：`SELECT count(*) n,count(*) FILTER(WHERE "base_ad_group" IS NULL) AS c0_null,count(*) FILTER(WHERE "base_ad_group" IS NOT NULL AND TRY_CAST("base_ad_group" AS DOUBLE) IS NULL) AS c1_not_numeric FROM raw.google_ads_ad_group_stats_data`。

- `records/020_diagnostics.json[0]`：`SELECT count(*) n, count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=s.id)) id_matches_history, count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=s.base_ad_group)) base_matches_history,count(DISTINCT id) ids,count(DISTINCT base_ad_group) bases FROM raw.google_ads_ad_group_stats_data s`。

- `records/020_diagnostics.json[1]`：`SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name='google_ads_ad_group_history_data' ORDER BY ordinal_position`。

- `records/020_final_diagnostics.json[0]`：`SELECT count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=regexp_extract(s.base_ad_group,'[^/]+$',0))) base_suffix_matches, count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=s.id)) id_matches FROM raw.google_ads_ad_group_stats_data s`。

规则问题：Boolean文本/脏文本补0与Data边界见完整038报告。当前Choice不否认存在大量NULL；缺的是证明这些值可唯一恢复为某个数值的证据，不用gold反证。
