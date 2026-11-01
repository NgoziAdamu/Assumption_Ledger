# impl-007_app_reporting__overview_report（038 正式表）

主要原因：**其他**；把握：中。020定稿旧主要原因：`O`，仅原样保留。

## 范围与材料

- 层：marts。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`，[2421, 2452]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/marts/app_reporting__overview_report.sql`。

- 对比执行输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### gold_positional_union_diagnostic

- 类别：其他；角色：主要；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约要求按字段含义保留downloads/deletions，agent按名UNION正确；gold SELECT *按位置拼接使Apple两列互换。复用定位/条件比较确认其余内容一致，不把错误的gold列序要求强加agent。

判定顺序：第3节第1步及第6节；以契约/呈现条件定位差异。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> business_logic: '- Read all rows from intermediate.int_google_play__overview and intermediate.int_apple_store__overview. - Union ALL the two datasets; no de-duplication and no ordering is enforced. - Select only: source_relation, date_day, app_platform, app_name, downloads, deletions, page_views, crashes. - No filtering, joins, casting, or aggregation; values are passed through exactly as in the sources. - Null policy: NULLs from source are preserved; no defaulting. - Text policy: case and whitespace are preserved. - Numeric policy: integers are passed through without rounding or bounding; negatives are preserved if present.'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/marts/app_reporting__overview_report.sql`，`delivered SQL`：

> SELECT source_relation,date_day,app_platform,app_name,downloads,deletions,page_views,crashes FROM intermediate.int_google_play__overview UNION ALL SELECT source_relation,date_day,app_platform,app_name,downloads,deletions,page_views,crashes FROM intermediate.int_apple_store__overview
>

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> business_logic: '- Read all rows from intermediate.int_google_play__overview and intermediate.int_apple_store__overview. - Union ALL the two datasets; no de-duplication and no ordering is enforced. - Select only: source_relation, date_day, app_platform, app_name, downloads, deletions, page_views, crashes. - No filtering, joins, casting, or aggregation; values are passed through exactly as in the sources. - Null policy: NULLs from source are preserved; no defaulting. - Text policy: case and whitespace are preserved. - Numeric policy: integers are passed through without rounding or bounding; negatives are preserved if present.'

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-007_app_reporting__overview_report.json#gold_positional_union_diagnostic`。仅为整体/共享前提诊断，不据此宣称单点贡献。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 693/1386 | 0/0 | 693/1386 |
| L1 | 693/1386 | 0/0 | 693/1386 |
| L2 | 693/1386 | 0/0 | 693/1386 |
| L3 | 693/1386 | 0/0 | 693/1386 |

## 规模、覆盖和不确定

同类候选/共享前提无法逐项排序，按手册第7节以中把握记该类。整段替换或多位置诊断的差异仅定位，不声称为单点修复贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[52]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='intermediate' AND table_name='int_apple_store__overview') OR (table_schema='intermediate' AND table_name='int_google_play__overview') ORDER BY table_schema,table_name,ordinal_position`。
