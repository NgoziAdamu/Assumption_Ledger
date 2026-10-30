# impl-008 / asana__team_efficiency_metrics（全量）

## 结论

主要原因：**多因并列（C、D）**；把握：中。项目规模偏离默认medium规则，多个成员指标及评分被占位。

参与因素：无经单修确认的其他参与因素。标记：无。

## 差异与归因依据

契约明确project_size_category固定medium_project；agent按真实任务数量重新分桶，medium/small各差44格，归C。developing_performers、avg_tasks_per_member、协作/资源评分、总分及建议文本未按可用关联和规则计算，直接0/NULL/固定简式，归D。逐输出表达式单修均减44格、行数不变，C与D并列。

层：marts；实际schema：mart；评测键：team_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml:1547–1717`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql:1–17`，SHA-256 `7d2e37f9ba8f26446f850760f2eed58ec9650c52a8a3620b982c3d05249614d9`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql:1–339`，SHA-256 `2404d03fa3a4a91803ded4dabd273d8588d785724778f9337199438472517a1c`。

- whole_implementation_diagnostic：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_reruns_impl-008_asana__team_efficiency_metrics.json`。

- medium_projects：agent SQL第6行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json`。

- small_projects：agent SQL第6行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json`。

- developing_performers：agent SQL第8行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json`。

- avg_tasks_per_member：agent SQL第8行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json`。

- collaboration_efficiency_score：agent SQL第11行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json`。

- resource_optimization_score：agent SQL第11行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json`。

- overall_team_efficiency_score：agent SQL第12行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json`。

- improvement_recommendations：agent SQL第13行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json`。

- team_strengths：agent SQL第13行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json`。

## agent可见证据与不确定性

**medium_projects=没有迹象；small_projects=没有迹象；developing_performers=没有迹象；avg_tasks_per_member=没有迹象；collaboration_efficiency_score=没有迹象；resource_optimization_score=没有迹象；overall_team_efficiency_score=没有迹象；improvement_recommendations=没有迹象；team_strengths=没有迹象**。

event25写本表简化实现；event38只展示44行，event53宣称完成未披露这些指标占位。没有找到针对本表这些差异的可见数据诊断或选择理由。

扫描55个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=5。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 28 | 27 | False |
| 38 | 37 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'intermediate.int_asana__project_health_indicators' source,count(*) n FROM intermediate.int_asana__project_health_indicators UNION ALL SELECT 'staging.stg_asana__project' source,count(*) n FROM staging.stg_asana__project UNION ALL SELECT 'staging.stg_asana__project_task' source,count(*) n FROM staging.stg_asana__project_task UNION ALL SELECT 'staging.stg_asana__task' source,count(*) n FROM staging.stg_asana__task UNION ALL SELECT 'staging.stg_asana__team' source,count(*) n FROM staging.stg_asana__team
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'intermediate.int_asana__project_health_indicators' source,count(*) n FROM intermediate.int_asana__project_heal...
                                                                   ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'intermediate.int_asana__project_health_indicators' source_name,count(*) n FROM intermediate.int_asana__project_health_indicators UNION ALL SELECT 'staging.stg_asana__project' source_name,count(*) n FROM staging.stg_asana__project UNION ALL SELECT 'staging.stg_asana__project_task' source_name,count(*) n FROM staging.stg_asana__project_task UNION ALL SELECT 'staging.stg_asana__task' source_name,count(*) n FROM staging.stg_asana__task UNION ALL SELECT 'staging.stg_asana__team' source_name,count(*) n FROM staging.stg_asana__team
```

结果（列顺序["source_name", "n"]）：`[["intermediate.int_asana__project_health_indicators", 472], ["staging.stg_asana__project", 495], ["staging.stg_asana__project_task", 3995], ["staging.stg_asana__task", 2986], ["staging.stg_asana__team", 44]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：44行/396格；选定基线：44行/396格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 44行/396格；L1 44行/396格；L2 44行/396格；L3 44行/396格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |
| medium_projects | L0 44行/352格；L1 44行/352格；L2 44行/352格；L3 44行/352格 | 均未整表匹配 |
| small_projects | L0 44行/352格；L1 44行/352格；L2 44行/352格；L3 44行/352格 | 均未整表匹配 |
| developing_performers | L0 44行/352格；L1 44行/352格；L2 44行/352格；L3 44行/352格 | 均未整表匹配 |
| avg_tasks_per_member | L0 44行/352格；L1 44行/352格；L2 44行/352格；L3 44行/352格 | 均未整表匹配 |
| collaboration_efficiency_score | L0 44行/352格；L1 44行/352格；L2 44行/352格；L3 44行/352格 | 均未整表匹配 |
| resource_optimization_score | L0 44行/352格；L1 44行/352格；L2 44行/352格；L3 44行/352格 | 均未整表匹配 |
| overall_team_efficiency_score | L0 44行/352格；L1 44行/352格；L2 44行/352格；L3 44行/352格 | 均未整表匹配 |
| improvement_recommendations | L0 44行/352格；L1 44行/352格；L2 44行/352格；L3 44行/352格 | 均未整表匹配 |
| team_strengths | L0 44行/352格；L1 44行/352格；L2 44行/352格；L3 44行/352格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"avg_tasks_per_member": 44, "collaboration_efficiency_score": 44, "developing_performers": 44, "improvement_recommendations": 44, "medium_projects": 44, "overall_team_efficiency_score": 44, "resource_optimization_score": 44, "small_projects": 44, "team_strengths": 44} |
| whole_implementation_diagnostic | {} |
| medium_projects | {"avg_tasks_per_member": 44, "collaboration_efficiency_score": 44, "developing_performers": 44, "improvement_recommendations": 44, "overall_team_efficiency_score": 44, "resource_optimization_score": 44, "small_projects": 44, "team_strengths": 44} |
| small_projects | {"avg_tasks_per_member": 44, "collaboration_efficiency_score": 44, "developing_performers": 44, "improvement_recommendations": 44, "medium_projects": 44, "overall_team_efficiency_score": 44, "resource_optimization_score": 44, "team_strengths": 44} |
| developing_performers | {"avg_tasks_per_member": 44, "collaboration_efficiency_score": 44, "improvement_recommendations": 44, "medium_projects": 44, "overall_team_efficiency_score": 44, "resource_optimization_score": 44, "small_projects": 44, "team_strengths": 44} |
| avg_tasks_per_member | {"collaboration_efficiency_score": 44, "developing_performers": 44, "improvement_recommendations": 44, "medium_projects": 44, "overall_team_efficiency_score": 44, "resource_optimization_score": 44, "small_projects": 44, "team_strengths": 44} |
| collaboration_efficiency_score | {"avg_tasks_per_member": 44, "developing_performers": 44, "improvement_recommendations": 44, "medium_projects": 44, "overall_team_efficiency_score": 44, "resource_optimization_score": 44, "small_projects": 44, "team_strengths": 44} |
| resource_optimization_score | {"avg_tasks_per_member": 44, "collaboration_efficiency_score": 44, "developing_performers": 44, "improvement_recommendations": 44, "medium_projects": 44, "overall_team_efficiency_score": 44, "small_projects": 44, "team_strengths": 44} |
| overall_team_efficiency_score | {"avg_tasks_per_member": 44, "collaboration_efficiency_score": 44, "developing_performers": 44, "improvement_recommendations": 44, "medium_projects": 44, "resource_optimization_score": 44, "small_projects": 44, "team_strengths": 44} |
| improvement_recommendations | {"avg_tasks_per_member": 44, "collaboration_efficiency_score": 44, "developing_performers": 44, "medium_projects": 44, "overall_team_efficiency_score": 44, "resource_optimization_score": 44, "small_projects": 44, "team_strengths": 44} |
| team_strengths | {"avg_tasks_per_member": 44, "collaboration_efficiency_score": 44, "developing_performers": 44, "improvement_recommendations": 44, "medium_projects": 44, "overall_team_efficiency_score": 44, "resource_optimization_score": 44, "small_projects": 44} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

同一简化实现包含多项输出；本次逐输出表达式单修，所有有效项行数均不变且减44格，C/D并列。若把整个协作评分链视为一项会改变粒度；不据此合并成一个无证据的原因。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-008_asana__team_efficiency_metrics.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-008_asana__team_efficiency_metrics/021_impl-008_asana__team_efficiency_metrics.json`。
- 重跑：`records/021_reruns_impl-008_asana__team_efficiency_metrics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
