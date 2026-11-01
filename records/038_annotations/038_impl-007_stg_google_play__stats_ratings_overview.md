# impl-007_stg_google_play__stats_ratings_overview（038 正式表）

主要原因：**其他**；把握：中。020定稿旧主要原因：`O`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`，[59, 79]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_ratings_overview.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### gold_rating_policy_diagnostic

- 类别：其他；角色：主要；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约明确非法必需评级delete_row；raw有9条越界，agent删除，gold将越界填3保留。按契约agent处理正确。event61修正其他评级规则未比较本处删除与填3，不据此记意识到本差异。

判定顺序：第3节第1步及第6节；以契约/呈现条件定位差异。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: average_rating
>           data_type: DECIMAL(10,2)
>           validation_rules:
>             - rule: "average_rating >= 1.0 AND average_rating <= 5.0"
>               on_failure: delete_row

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_ratings_overview.sql`，`delivered SQL`：

> WITH source_rows AS (
> SELECT
>     CAST(_file AS VARCHAR) AS source_relation,
>     TRY_CAST(SUBSTR(CAST(date AS VARCHAR), 1, 10) AS DATE) AS date_day,
>     CAST(package_name AS VARCHAR) AS package_name,
>     TRY_CAST(daily_average_rating AS DECIMAL(10,2)) AS average_rating,
>     TRY_CAST(total_average_rating AS DECIMAL(10,2)) AS rolling_total_average_rating
> FROM raw.stats_ratings_overview
> )
> SELECT * FROM source_rows WHERE (average_rating >= 1 AND average_rating <= 5) AND (rolling_total_average_rating IS NULL OR (rolling_total_average_rating >= 1 AND rolling_total_average_rating <= 5))
>

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: average_rating
>           data_type: DECIMAL(10,2)
>           validation_rules:
>             - rule: "average_rating >= 1.0 AND average_rating <= 5.0"
>               on_failure: delete_row

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-007_stg_google_play__stats_ratings_overview.json#gold_rating_policy_diagnostic`。仅为整体/共享前提诊断，不据此宣称单点贡献。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 9/36 | 0/0 | 9/36 |
| L1 | 9/36 | 0/0 | 9/36 |
| L2 | 9/36 | 0/0 | 9/36 |
| L3 | 9/36 | 0/0 | 9/36 |

## 规模、覆盖和不确定

同类候选/共享前提无法逐项排序，按手册第7节以中把握记该类。整段替换或多位置诊断的差异仅定位，不声称为单点修复贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[66]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='stats_ratings_overview') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[67]`：`SELECT count(*) n,count(*) FILTER(WHERE daily_average_rating IS NULL) null_daily,count(*) FILTER(WHERE daily_average_rating NOT BETWEEN 1 AND 5) invalid_daily,count(*) FILTER(WHERE total_average_rating NOT BETWEEN 1 AND 5) invalid_total FROM raw.stats_ratings_overview`。
