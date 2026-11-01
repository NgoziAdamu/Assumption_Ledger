# impl-008_int_asana__task_projects（037 校准；解盲后工作结果）

主要原因：**Data Misconception**；把握：高。本表不属于43张正式批次。

## 盲标与对比

盲标原件：`records/037_calibration_blind_sealed.json`，SHA-256 `b74b140d740d21b5aaab3febba23d1e6295bffce5b5759b906b15747ff97b6bf`。封存后不改。

盲标主因：Data Misconception；主点第 4 档。036：Data Misconception，第 4 档。

明确缺失项目的材料和 agent staging 反例支持 Data；第4档一致。把握差异保留：本次主因采用高。

019旧主要原因原样保留：`U`；不以旧类别推导新类别。

## 逐点依据

### project_id 取右侧 project，缺失项目关系丢失

- 类别：Data Misconception；角色：主要；把握：高。
- SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`，第 2；聚合 8–12 行。
- 规模：016/019 同次重跑 L0–L3 均为行 187→71、格 237→71，行减少 116。
- 是否说出：第 4 档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确允许 project 缺失；014 V1 在 agent 留存 staging 中查得 44 个关系/任务匹配不到。SQL 第 2 行选择 p.project_id。单改为 pt.project_id 同时恢复 ID 并恢复源 ID 类型对应的排序；不把这一类型副作用重复计为独立错误点。

P：每个 project_task.project_id 都能匹配 project，取右侧 ID 不会丢失原关系 ID。

证据文件：

- `records/014_queries_impl-008.json#V1`
- `records/016_reruns_impl-008.json#project_source`
- `records/019_reruns_impl-008_int_asana__task_projects.json#project_source`

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`，event 1 / `message`：

> retain rows when the project is missing.

证据在场：契约全文随初始 user message（event 1）直接送入，相关原句完整存在；不是被截断的读文件输出。没有另行读取契约的 run 事件。

event 1 / `message`：

> retain rows when the project is missing.

明确缺失项目的材料和 agent staging 反例支持 Data；第4档一致。把握差异保留：本次主因采用高。

### projects_sections 同名 project 内的 section 并列顺序

- 类别：其他；角色：参与；把握：高。
- SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`，第 10 行。
- 规模：留存结果诊断的基线行 195，单独归一化本列后 122，减少 73；格 245→166。与 016 重跑的 187/237 是不同运行，不混用其基线；同次重跑若消除全部剩余 section 差异最多减少 71 行，小于主点 116。
- 是否说出：第 4 档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约只规定按 project_name 排序，没有规定同名内 section 的次序。037 诊断确认 79 处字符串差异的 project_name 序列及每个名称内完整项 multiset 全相同，属形式未规定。不是 agent 未遵循已规定的排序。

证据文件：

- `records/037_checks/calibration_diagnostic.json`
- `records/013_packages/013_impl-008_intermediate_int_asana__task_projects.md`

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`，event 1 / `message`：

> ordered ascending by project_name; duplicates are kept;

初始契约提供了相关内容；中间 SQL 只写出实际做法，未显示疑问、候选比较或冲突意识，依 v3.2 记第 4 档。

## 交付物核对

最终报告取 finish event 53 的 `args.final_thought`。本表最终 SQL 无注释，临时脚本不作交付物；扫描相关其他交付 SQL 注释未发现本处说明。

## 不确定与规则问题

project_source 的类型/排序副作用不拆成独立重复点；其他顺序因素仍单列。

037 另外列出 projects_sections 同名内并列顺序（其他，参与）；036 points.csv 未单列此点。037 新诊断确认 79/79 字符串差异仅同名组内次序。该点不改变主要原因。

Asana 的历史留存与单改重跑允许并列排序不同；不可把195行的留存基线与187行的重跑基线混算。校准表的最终类别与披露如经解盲修订，不能计入盲标一致率。
