# impl-008 / int_asana__task_projects（校准，盲标封存）

## 结论

主要原因：**U**；把握：中；标记：证据曾出现但被忽略。

P：从 project 维表取 project_id 可替代关系表原值而不影响聚合。契约说明 project 可缺失；代码却依赖匹配及类型排序等价。只换 pt.project_id，行规模187→71，格237→71。剩余 sections 只有并列顺序差异（诊断多重集一致），单独作为 O 残余。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/013_packages/013_impl-008_intermediate_int_asana__task_projects.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：3000/3000。本次固定控制下 baseline 行/格规模：187/237。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`；原文行段 775–799。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`，L1–12；SHA-256 `cafca1b970c267d89c26552130a99965a4244b448688c350f2954b45367460c7`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`，L1–47；SHA-256 `fd3605e7a0adc9a4a349b78b413d087a5b03394565226c8fa3ee3a15202354e8`。

project_source：agent SQL L2，盲标单处改动。
```sql
pt.task_id, p.project_id,
```
替换为：
```sql
pt.task_id, pt.project_id,
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-008_int_asana__task_projects.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 2 条（上限5）；代价档：多条查询。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

核实：
```sql
SELECT count(*) n, count(*) FILTER(WHERE p.id IS NULL) missing FROM raw.project_task_data pt LEFT JOIN raw.project_data p ON pt.project_id=p.id
```
结果（仅统计/类型）：`[[3995, 0]]`

核实：
```sql
SELECT count(*) n,count(*) FILTER(WHERE p.project_id IS NULL) missing FROM staging.stg_asana__project_task pt LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR=p.project_id
```
结果（仅统计/类型）：`[[3995, 44]]`

诊断：
```sql
SELECT count(*) FROM intermediate.int_asana__task_projects a JOIN gold.intermediate.int_asana__task_projects g USING(task_id) WHERE list_sort(string_split(a.projects_sections, ', ')) IS DISTINCT FROM list_sort(string_split(g.projects_sections, ', '))
```
结果（仅统计/类型）：`[[0]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 187 | 237 | {"number_of_projects": 44, "project_ids": 122, "projects_sections": 71} | L0–L3均不匹配 |
| baseline | L1 | 187 | 237 | {"number_of_projects": 44, "project_ids": 122, "projects_sections": 71} | L0–L3均不匹配 |
| baseline | L2 | 187 | 237 | {"number_of_projects": 44, "project_ids": 122, "projects_sections": 71} | L0–L3均不匹配 |
| baseline | L3 | 187 | 237 | {"number_of_projects": 44, "project_ids": 122, "projects_sections": 71} | L0–L3均不匹配 |
| project_source | L0 | 71 | 71 | {"projects_sections": 71} | L0–L3均不匹配 |
| project_source | L1 | 71 | 71 | {"projects_sections": 71} | L0–L3均不匹配 |
| project_source | L2 | 71 | 71 | {"projects_sections": 71} | L0–L3均不匹配 |
| project_source | L3 | 71 | 71 | {"projects_sections": 71} | L0–L3均不匹配 |

U 条件：P 及反例见结论和核实查询；实际可见材料见下一节；仅指定取列/解析/同键结合的改动达到第4条件。对重复/缺失的已有提示不等于验证了代码依赖的等价性，按手册保留“证据曾出现但被忽略”（适用时）。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`，字段字符偏移 54495。

> int_asana__task_projects
>       description: Task-project relationships with aggregated project IDs, names, and sections
>       grain: One row per task_id
>       source_models:
>       - staging.stg_asana__project_task
>       - staging.stg_asana__project
>       - staging.stg_asana__task_section
>       - staging.stg_asana__section
>       business_logic: 'Build task-project relationships and aggregates: - Start from staging.stg_asana__project_task (project_task). - Left join staging.stg_asana__project (pro

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

同一次取列替换同时修复缺失关联和数字/文本排序；作为同一个取列假设处理。契约仅要求按 project_name 排序，未明确写任意同名顺序；同名键排序自由解释为 O。

盲标封存：`records/019_calibration_blind_sealed.json`，时间 2026-10-29T13:45:23.213382+00:00。封存前未读取014–018标注；封存后比较只报告分歧，不回写本表盲标结论。
