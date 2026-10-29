# impl-008 / int_asana__task_projects（v2定稿）

## 1. 差异描述与判定

使用右表project_id丢失未匹配项目并改变排序类型；改回左表project_id使不一致行减少超过一半。

已核实：agent可见数据有44条project_task找不到project。CS基线187行/237格；单换SELECT p.project_id为pt.project_id，剩71行/71格，行数减少62.0%。同一来源选择既丢失缺项目的id又带入VARCHAR排序；数字排序独立对照114行/159格，是同一机制的部分修复，不重复列参与因素。旧014双侧拆分projects_sections诊断79个不同字符串条目多重集合一致；本次单增section_name作为并列排序键却变596行/661格，未减少规模，不列O参与因素。

主要原因：**U**；把握：**中**。
参与因素：无：numeric_order与主因同源；section_tie_order单改反而增大差异。标记：证据曾出现但被忽略。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-008_int_asana__task_projects.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-008_intermediate_int_asana__task_projects.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml` 第775–799行。
- [原始轨迹转录](../014_trace_impl-008.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-008.json)；[015三方raw核对](../015_raw_impl-008.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: int_asana__task_projects
      description: Task-project relationships with aggregated project IDs, names, and sections
      grain: One row per task_id
      source_models:
      - staging.stg_asana__project_task
      - staging.stg_asana__project
      - staging.stg_asana__task_section
      - staging.stg_asana__section
      business_logic: 'Build task-project relationships and aggregates: - Start from staging.stg_asana__project_task (project_task). - Left join staging.stg_asana__project (project) on project_id after casting project_task.project_id to VARCHAR to match project.project_id; retain rows when the project is missing. - Left join staging.stg_asana__task_section (task_section) on task_id after casting both sides to VARCHAR; this can multiply project rows for tasks with multiple sections. - Left join staging.stg_asana__section (section) on section_id after casting task_section.section_id to VARCHAR; set section_name to "(no section)" when missing. - Produce task_projects_base with task_id, project_id, project_name, section_name. - Aggregate by task_id to form the output: - project_ids: concatenate all non-NULL project_id values using ", ", ordered ascending by project_id; duplicates are kept; if there are no non-NULL values the result is NULL; casing and whitespace are preserved. - project_names: concatenate all non-NULL project_name values using ", ", ordered ascending by project_name; duplicates are kept; if there are no non-NULL values the result is NULL; casing and whitespace are preserved. - projects_sections: for each row, create "project_name (section_name)" using "(no section)" when section is missing; exclude rows where project_name is NULL; concatenate using ", ", ordered ascending by project_name; duplicates are kept; if there are no non-NULL pairs the result is NULL; casing and whitespace are preserved. - number_of_projects: count distinct project_id values per task_id; NULL project_id is excluded; duplicates caused by multiple sections do not increase the count. - Output includes only task_ids present in project_task.'
      columns:
      - name: task_id
        data_type: BIGINT
        description: Unique task identifier; exactly one output row per task_id
      - name: project_ids
        data_type: VARCHAR
        description: Comma + space separated project_id values ordered ascending by project_id; duplicates kept; NULL project_id excluded; if none → NULL; casing/whitespace preserved
      - name: project_names
        data_type: VARCHAR
        description: Comma + space separated project_name values ordered ascending by project_name; duplicates kept; NULL names excluded; if none → NULL; casing/whitespace preserved
      - name: projects_sections
        data_type: VARCHAR
        description: Comma + space separated 'project_name (section_name)' pairs ordered ascending by project_name; section_name uses '(no section)' when missing; pairs with NULL project_name excluded; duplicates kept; if none → NULL; casing/whitespace preserved
      - name: number_of_projects
        data_type: BIGINT
        description: Distinct count of project_id per task_id; NULL project_id excluded; duplicates from multiple sections do not increase the count
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`
```sql
   1: WITH task_projects_base AS (
   2:  SELECT pt.task_id, p.project_id, p.project_name, COALESCE(s.section_name, '(no section)') AS section_name
   3:  FROM staging.stg_asana__project_task pt
   4:  LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR = p.project_id
   5:  LEFT JOIN staging.stg_asana__task_section ts ON pt.task_id::VARCHAR = ts.task_id::VARCHAR
   6:  LEFT JOIN staging.stg_asana__section s ON ts.section_id::VARCHAR = s.section_id
   7: )
   8: SELECT task_id, STRING_AGG(project_id, ', ' ORDER BY project_id) AS project_ids,
   9:        STRING_AGG(project_name, ', ' ORDER BY project_name) AS project_names,
  10:        STRING_AGG(project_name || ' (' || section_name || ')', ', ' ORDER BY project_name) FILTER (WHERE project_name IS NOT NULL) AS projects_sections,
  11:        COUNT(DISTINCT project_id)::BIGINT AS number_of_projects
  12: FROM task_projects_base GROUP BY task_id
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/intermediate/int_asana__task_projects.sql`
```sql
   1: with project_task as (
   2:     select * 
   3:     from staging.stg_asana__project_task
   4: ),
   5: 
   6: project as (
   7:     select *
   8:     from staging.stg_asana__project
   9: ),
  10: 
  11: task_section as (
  12:     select * 
  13:     from staging.stg_asana__task_section
  14: ),
  15: 
  16: section as (
  17:     select *
  18:     from staging.stg_asana__section
  19: ),
  20: 
  21: task_projects_base as (
  22:     select
  23:         project_task.task_id,
  24:         project_task.project_id,
  25:         project.project_name,
  26:         coalesce(section.section_name, '(no section)') as section_name
  27:     from project_task
  28:     left join project 
  29:         on cast(project_task.project_id as varchar) = project.project_id
  30:     left join task_section 
  31:         on cast(project_task.task_id as varchar) = cast(task_section.task_id as varchar)
  32:     left join section 
  33:         on cast(task_section.section_id as varchar) = section.section_id
  34: ),
  35: 
  36: task_projects as (
  37:     select
  38:         task_id,
  39:         string_agg(project_id, ', ' order by project_id) as project_ids,
  40:         string_agg(project_name, ', ' order by project_name) as project_names,
  41:         string_agg(project_name || ' (' || section_name || ')', ', ' order by project_name) as projects_sections,
  42:         count(distinct project_id) as number_of_projects
  43:     from task_projects_base
  44:     group by 1
  45: )
  46: 
  47: select * from task_projects
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.project_data|gold_vs_initial|True|True|True||
|raw.project_task_data|gold_vs_initial|True|True|True||
|raw.section_data|gold_vs_initial|True|True|True||
|raw.task_section_data|gold_vs_initial|True|True|True||
|raw.project_data|gold_vs_agent|True|True|True||
|raw.project_task_data|gold_vs_agent|True|True|True||
|raw.section_data|gold_vs_agent|True|True|True||
|raw.task_section_data|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event 1完整契约明确retain rows when project missing、重复保留、只按project_name排序；event 13→14显示部分源结构，event 17选择右表project_id。全部55事件未找到反连接或project完整性核实。契约对缺失项目给过提醒，故加“证据曾出现但被忽略”，不把可能未展示的全库内容算成看过。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|project_source|U|看到了但没提|1|

### project_source：看到了但没提

契约已提供项目可缺失信息；最终报告没有说明为什么用右表project_id替代左表。

事件 **1**，字段`args.content`；[轨迹原文](../014_trace_impl-008.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`。
```text
int_asana__task_projects
      description: Task-project relationships with aggregated project IDs, names, and sections
      grain: One row per task_id
      source_models:
      - staging.stg_asana__project_task
      - staging.stg_asana__project
      - staging.stg_asana__task_section
      - staging.stg_asana__section
      business_logic: 'Build task-project relationships and aggregates: - Start from staging.stg_asana__project_task (project_task). - Left join staging.stg_asana__project (project) on project_id after casting project_task.project_id to VARCHAR to match project.project_id; retain rows when the project is missing. - Left join staging.stg_asana__task_section (task_section) on task_id after casting both sides to VARCHAR; this can multiply project rows for tasks with multiple sections. - Left join staging.stg_asana__section (section) on sec
```

已检视55个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：一条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-008.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **1条**（含014复用；本轮新增0条）；核实代价档：**一条查询**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 014-V1 / 核实查询

来源：`records/014_queries_impl-008.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE p.project_id IS NULL) missing_projects,count(distinct pt.task_id) FILTER(WHERE p.project_id IS NULL) affected_tasks FROM staging.stg_asana__project_task pt LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR=p.project_id
```
结果原文：
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

### 014-D1 / 诊断查询

来源：`records/014_queries_impl-008.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/asana.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE p.project_id IS NULL) missing_projects,count(distinct pt.task_id) FILTER(WHERE p.project_id IS NULL) affected_tasks FROM staging.stg_asana__project_task pt LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR=p.project_id
```
结果原文：
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

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['task_id']`；比较列（与键取并集）：`['number_of_projects', 'project_ids', 'project_names', 'projects_sections', 'task_id']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|project_source|187→71|237→71|无|
|id_numeric_order|187→114|237→159|无|
|section_tie_order|187→596|237→661|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|195|195|245|False|
|L1|3000|3000|0|0|0/0|195|195|245|False|
|L2|3000|3000|0|0|0/0|195|195|245|False|
|L3|3000|3000|0|0|0/0|195|195|245|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|task_id|0|0|0|0|
|number_of_projects|44|44|44|44|
|project_ids|122|122|122|122|
|project_names|0|0|0|0|
|projects_sections|79|79|79|79|

### 重跑 baseline

SQL：`data/016_work/impl-008/baseline.sql`；SHA-256：`cafca1b970c267d89c26552130a99965a4244b448688c350f2954b45367460c7`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|187|187|237|False|
|L1|3000|3000|0|0|0/0|187|187|237|False|
|L2|3000|3000|0|0|0/0|187|187|237|False|
|L3|3000|3000|0|0|0/0|187|187|237|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|task_id|0|0|0|0|
|number_of_projects|44|44|44|44|
|project_ids|122|122|122|122|
|project_names|0|0|0|0|
|projects_sections|71|71|71|71|

### 重跑 project_source

SQL：`data/016_work/impl-008/project_source.sql`；SHA-256：`2252dfea0acb0d346d33de5a90204dd6dad880f6269f34051bbcfef50d0585a6`。

唯一原文位置offset=30，替换前：
```sql
SELECT pt.task_id, p.project_id,
```
替换后：
```sql
SELECT pt.task_id, pt.project_id,
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|71|71|71|False|
|L1|3000|3000|0|0|0/0|71|71|71|False|
|L2|3000|3000|0|0|0/0|71|71|71|False|
|L3|3000|3000|0|0|0/0|71|71|71|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|task_id|0|0|0|0|
|number_of_projects|0|0|0|0|
|project_ids|0|0|0|0|
|project_names|0|0|0|0|
|projects_sections|71|71|71|71|

### 重跑 id_numeric_order

SQL：`data/016_work/impl-008/id_numeric_order.sql`；SHA-256：`3ab2a0e4a22070f3e3563014ce31b4aad9460bc9d70e7d92bdee664638b9b36d`。

唯一原文位置offset=448，替换前：
```sql
STRING_AGG(project_id, ', ' ORDER BY project_id)
```
替换后：
```sql
STRING_AGG(project_id, ', ' ORDER BY TRY_CAST(project_id AS BIGINT))
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|114|114|159|False|
|L1|3000|3000|0|0|0/0|114|114|159|False|
|L2|3000|3000|0|0|0/0|114|114|159|False|
|L3|3000|3000|0|0|0/0|114|114|159|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|task_id|0|0|0|0|
|number_of_projects|44|44|44|44|
|project_ids|44|44|44|44|
|project_names|0|0|0|0|
|projects_sections|71|71|71|71|

### 重跑 section_tie_order

SQL：`data/016_work/impl-008/section_tie_order.sql`；SHA-256：`eaba270563c4f613f84dd92af14bc396c66b04534f64d0b0b548e92006d0f9a8`。

唯一原文位置offset=598，替换前：
```sql
STRING_AGG(project_name || ' (' || section_name || ')', ', ' ORDER BY project_name)
```
替换后：
```sql
STRING_AGG(project_name || ' (' || section_name || ')', ', ' ORDER BY project_name,section_name)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|596|596|661|False|
|L1|3000|3000|0|0|0/0|596|596|661|False|
|L2|3000|3000|0|0|0/0|596|596|661|False|
|L3|3000|3000|0|0|0/0|596|596|661|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|task_id|0|0|0|0|
|number_of_projects|44|44|44|44|
|project_ids|122|122|122|122|
|project_names|0|0|0|0|
|projects_sections|495|495|495|495|

排序内容诊断复用：[014_relaxed_impl-008.json](../014_relaxed_impl-008.json)，查询原文及双侧放宽结果在该记录；不把放宽评测叫作单侧修复。

## 5. 逐项类别及U门槛

表级主要原因：**U**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|project_source|U|187→71|237→71|无|

重跑是否满足U第4条件：**是（单改project_id来源，187行降至71行）**。

P：右表p.project_id可无损替代左表pt.project_id来列举、排序和计数项目。V1反证关联完整性；SQL类型与两种排序干预验证排序影响。只改这一个投影后行差异降低至少一半，满足U4。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：是：主要U不变；新增并列section顺序单改无改善，移除014的O参与因素。。此字段不代替本次与016/017的对比。

## 规则问题

“项目可能缺失”是数据性质而非指定SELECT表达式，v2 C/U边界支持U；轨迹契约提醒被忽略。O诊断可说明残差来源，但v2参与因素仍要求单改改善，不能以双侧放宽比较替代该要求。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
