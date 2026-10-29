# impl-008 / int_asana__task_projects

## 1. 错在哪里

使用右表project_id丢失未匹配项目并改变排序类型；改回左表project_id使不一致行减少超过一半。

已核实：agent可见staging有44条project_task找不到project，对应44个task。CS重跑中p.project_id为VARCHAR，pt.project_id保留原数值类型：同一处来源选择既影响缺失项目，又影响字符串/数值排序。新基线187行不同；只把SELECT中的p.project_id换成pt.project_id后剩71行，减少62.0%，不一致列值237降71。单独数字排序干预也减少差异，但不能恢复缺失项目。留存projects_sections有79个不同字符串，79个均拥有相同条目多重集合。归因判断：U；剩余同名项目的section顺序未规定，列O。

## 2. 依据

- 起点：[013精简包](../013_packages/013_impl-008_intermediate_int_asana__task_projects.md)。原013状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`，第775–799行。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`；gold SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`。精简包完整收录；下列补丁逐字给出定位原文。
- [完整事件记录](../014_trace_impl-008.json)；事件文件在该JSON的path中，可回查traces/dacomp_deimpl_prev.tar.gz。
- [查询原文与结果](../014_queries_impl-008.json)、[全部重跑记录](../014_reruns_impl-008.json)。

### SQL行号定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`
```text
2:  SELECT pt.task_id, p.project_id, p.project_name, COALESCE(s.section_name, '(no section)') AS section_name
4:  LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR = p.project_id
8: SELECT task_id, STRING_AGG(project_id, ', ' ORDER BY project_id) AS project_ids,
9:        STRING_AGG(project_name, ', ' ORDER BY project_name) AS project_names,
10:        STRING_AGG(project_name || ' (' || section_name || ')', ', ' ORDER BY project_name) FILTER (WHERE project_name IS NOT NULL) AS projects_sections,
11:        COUNT(DISTINCT project_id)::BIGINT AS number_of_projects
```

gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`
```text
24:         project_task.project_id,
29:         on cast(project_task.project_id as varchar) = project.project_id
39:         string_agg(project_id, ', ' order by project_id) as project_ids,
40:         string_agg(project_name, ', ' order by project_name) as project_names,
41:         string_agg(project_name || ' (' || section_name || ')', ', ' order by project_name) as projects_sections,
42:         count(distinct project_id) as number_of_projects
```

## 3. agent看过什么

event 1完整契约明确retain rows when project missing、重复保留、只按project_name排序；event 13→14显示部分源结构，event 17选择右表project_id。全部55事件未找到反连接或project完整性核实。契约对缺失项目给过提醒，故加“证据曾出现但被忽略”，不把可能未展示的全库内容算成看过。

已逐题核对event 1 message，包含本表契约完整原文；这不是把磁盘上存在的文档等同于agent已经阅读。schema输出、源数据值、运行日志分别处理。轨迹全量转录未删去截断标记；被截断的未显示部分不作为看到的证据。

## 4. 查询与重跑

核实查询实际执行 **1条**；核实代价：**一条查询**。诊断查询不计入5条限制。重复执行的查询仍计数。

### V1：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE p.project_id IS NULL) missing_projects,count(distinct pt.task_id) FILTER(WHERE p.project_id IS NULL) affected_tasks FROM staging.stg_asana__project_task pt LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR=p.project_id
```

结果：
```json
{
  "columns": [
    "n",
    "missing_projects",
    "affected_tasks"
  ],
  "rows": [
    [
      3995,
      44,
      44
    ]
  ]
}
```

### D1：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/asana.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE p.project_id IS NULL) missing_projects,count(distinct pt.task_id) FILTER(WHERE p.project_id IS NULL) affected_tasks FROM staging.stg_asana__project_task pt LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR=p.project_id
```

结果：
```json
{
  "columns": [
    "n",
    "missing_projects",
    "affected_tasks"
  ],
  "rows": [
    [
      3995,
      44,
      44
    ]
  ]
}
```

### 比较口径

原件均READ_ONLY；只把本节点引用表复制到data/014_work私有DuckDB后执行。staging输入来自agent留存库raw；003/008上游直接复制gold，实现CS。固定原评分的comparison_columns与key_columns；L0为lower/trim/NULL规范化，L1数字及布尔归一，L2数值两位小数，L3再放宽日期时间到日期。键始终固定L0，不在宽松档位重新归一。

无共同键时逐列0表示无可比较行，不表示一致。重复键按值/行多重集合抵消，报告最少不一致对数；同时公开额外行次数。为避免键被漏出整表判断，含键整表匹配用于本次U4；旧007式仅值列整表匹配并列展示。这里没有重定义原官方对错或修改旧状态。

比较列：`['number_of_projects', 'project_ids', 'project_names', 'projects_sections', 'task_id']`；键：`['task_id']`。

### 留存基线（013材料来源）

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|0|0|195|0/0|195/195|False|False|
|L1|3000|3000|0|0|195|0/0|195/195|False|False|
|L2|3000|3000|0|0|195|0/0|195/195|False|False|
|L3|3000|3000|0|0|195|0/0|195/195|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|number_of_projects|44|44|44|44|
|project_ids|122|122|122|122|
|project_names|0|0|0|0|
|projects_sections|79|79|79|79|
|task_id|0|0|0|0|

### 重跑：baseline

不改SQL；建立本轮相同引擎、相同输入的比较基线。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|0|0|187|0/0|187/187|False|False|
|L1|3000|3000|0|0|187|0/0|187/187|False|False|
|L2|3000|3000|0|0|187|0/0|187/187|False|False|
|L3|3000|3000|0|0|187|0/0|187/187|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|number_of_projects|44|44|44|44|
|project_ids|122|122|122|122|
|project_names|0|0|0|0|
|projects_sections|71|71|71|71|
|task_id|0|0|0|0|

### 重跑：project_source

只替换以下原文（其余字节经验证不变）：
```sql
SELECT pt.task_id, p.project_id,
```
替换为：
```sql
SELECT pt.task_id, pt.project_id,
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|0|0|71|0/0|71/71|False|False|
|L1|3000|3000|0|0|71|0/0|71/71|False|False|
|L2|3000|3000|0|0|71|0/0|71/71|False|False|
|L3|3000|3000|0|0|71|0/0|71/71|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|number_of_projects|0|0|0|0|
|project_ids|0|0|0|0|
|project_names|0|0|0|0|
|projects_sections|71|71|71|71|
|task_id|0|0|0|0|

### 重跑：id_numeric_order

只替换以下原文（其余字节经验证不变）：
```sql
STRING_AGG(project_id, ', ' ORDER BY project_id)
```
替换为：
```sql
STRING_AGG(project_id, ', ' ORDER BY TRY_CAST(project_id AS BIGINT))
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|0|0|114|0/0|114/114|False|False|
|L1|3000|3000|0|0|114|0/0|114/114|False|False|
|L2|3000|3000|0|0|114|0/0|114/114|False|False|
|L3|3000|3000|0|0|114|0/0|114/114|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|number_of_projects|44|44|44|44|
|project_ids|44|44|44|44|
|project_names|0|0|0|0|
|projects_sections|71|71|71|71|
|task_id|0|0|0|0|

### gold SQL在同一私有输入上的诊断

这是诊断，不是局部修复，也不用于证明U4。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|0|0|71|0/0|71/71|False|False|
|L1|3000|3000|0|0|71|0/0|71/71|False|False|
|L2|3000|3000|0|0|71|0/0|71/71|False|False|
|L3|3000|3000|0|0|71|0/0|71/71|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|number_of_projects|0|0|0|0|
|project_ids|0|0|0|0|
|project_names|0|0|0|0|
|projects_sections|71|71|71|71|
|task_id|0|0|0|0|

## 5. 类别和把握

- 主要原因：**U**（归因判断）。
- 参与因素：O（project_name并列时section字符串次序）。
- 标记：证据曾出现但被忽略。
- 把握：**中**。
- 重跑是否满足U第4条件：是（单改project_id来源，187行降至71行）。

P：右表p.project_id可无损替代左表pt.project_id来列举、排序和计数项目。V1反证关联完整性；SQL类型与两种排序干预验证排序影响。只改这一个投影后行差异降低至少一半，满足U4。

## 规则问题

也可读为C（契约要求保留缺失项目）或I（别名选错）。本次选U：契约没有直接写SELECT必须取哪侧列，且未找到正确意图文本；投影依赖可检验的关联完整性。契约提醒是否足以视为“已经核实”与U3后半句存在冲突，按“被忽略”例外处理。并列排序导致新基线187行不同于旧包统计，所有修复效果只与同次新基线比较。

共同问题：手册第1节“不预设类别分布”与末句“希望未核实假设多”存在张力；本次以逐条证据条件为准，不按期望调整分布。U3“没看过任何足以判断P的东西”与“证据曾出现但被忽略仍归U”按后者作为例外解释。
