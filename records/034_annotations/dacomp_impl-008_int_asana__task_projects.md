# DAComp / impl-008_int_asana__task_projects（v3）

## 错在哪里
使用右表project_id丢失未匹配项目并改变排序类型；改回左表project_id使不一致行减少超过一半。

证据复用入口：[018_impl-008_int_asana__task_projects.md](../018_annotations/018_impl-008_int_asana__task_projects.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## project_source
- 角色：主要；类别：**Data Misconception**；把握：中。
- 依据：P：project_task中的project_id都能在project找到。可见上游查询44条不能匹配；只改p.project_id为pt.project_id，187→71行；同一来源也改变排序类型，不重复计算。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/014_trace_impl-008.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
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

## 规模、证据复用与新做
主要原因：Data Misconception。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-008_int_asana__task_projects.md](../018_annotations/018_impl-008_int_asana__task_projects.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: int_asana__task_projects
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

## 规则问题

契约retain rows可读为规定保留左id，也可只说明项目可能缺失。选后者：没有明确投影表达式，用44条未匹配事实反证P，归Data。

## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-008_int_asana__task_projects.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-008_int_asana__task_projects.md:58)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-008_int_asana__task_projects.md:241)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-008_int_asana__task_projects.md:268)
- [重跑 project_source](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-008_int_asana__task_projects.md:291)
- [重跑 id_numeric_order](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-008_int_asana__task_projects.md:321)
- [重跑 section_tie_order](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-008_int_asana__task_projects.md:351)
