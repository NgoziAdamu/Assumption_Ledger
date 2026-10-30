# impl-011 / jira__stakeholder_engagement_insights（全量）

## 结论

主要原因：**多因并列（D、O）**；把握：中。分析分类占位与gold违反NULL/标签约定的差异并列。

参与因素：O：total_comments_authored（减0行/1633格）；O：total_projects_involved（减0行/2418格）；A：cross_functional_projects（减0行/356格）；C：engagement_breadth_score（减0行/1579格）；D：engagement_quality_score（减0行/1309格）；D：engagement_impact_score（减0行/12格）；D：engagement_risk_status（减0行/2231格）；D：strategic_value_score（减0行/3999格）；D：recommended_engagement_strategy（减0行/2441格）。标记：已披露。

## 差异与归因依据

gold4524行均无avg_outbound_influence_strength，却全部depth和total非NULL；契约明确NULL，故这两项O。influence_level契约Minimal而gold Minimal Influence，同为O。archetype/development_opportunity固定占位为D；上述各单修减少4524格、行数不变并列。response_pattern同时含速度计算缺失及标签后缀差异，不把整列联合修正当单一D证据。另诊断gold评论计数被关联放大、项目数使用coalesce漏掉另一角色，不能将agent符合文字计数的部分归错。

层：marts；实际schema：marts；评测键：stakeholder_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml:2913–3015`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql:1–1`，SHA-256 `1000170045dc47269013cfe3b754873bff7ca78237e23dcdfe658086d7662d12`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/marts/jira__stakeholder_engagement_insights.sql:1–236`，SHA-256 `a79e77163e26e9ea7a8c3834dc35c43fcee6bf2bbd14580efc3445287c5b6519`。

- whole_implementation_diagnostic：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- response_pattern_type：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- engagement_depth_score：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- total_engagement_score：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- stakeholder_archetype：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- influence_level：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- development_opportunity：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- total_comments_authored：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- total_projects_involved：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- cross_functional_projects：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- engagement_breadth_score：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- engagement_quality_score：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- engagement_impact_score：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- engagement_risk_status：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- strategic_value_score：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

- recommended_engagement_strategy：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json`。

## agent可见证据与不确定性

**engagement_depth_score=没有迹象；total_engagement_score=没有迹象；stakeholder_archetype=针对本表的具体说明；influence_level=没有迹象；development_opportunity=针对本表的具体说明**。

event55明确列举stakeholder详细业务计算简化/默认；这覆盖D分类占位。对于O的NULL规则/标签差异，全部57事件及报告没有具体说明，按各并列项分别填四档。

最终报告原句（其适用范围按上文判定）：

> 合同非常广泛，本实现优先保证所有配置模型可执行；少数复杂分析并未完整实现合同中的每个指标/分支。尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。

扫描57个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=38。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 20 | 19 | False |
| 22 | 21 | False |
| 24 | 23 | False |
| 32 | 31 | False |
| 36 | 35 | False |
| 38 | 37 | False |
| 42 | 41 | False |
| 44 | 43 | False |
| 46 | 45 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'staging.stg_jira__comment' source,count(*) n FROM staging.stg_jira__comment UNION ALL SELECT 'staging.stg_jira__issue' source,count(*) n FROM staging.stg_jira__issue UNION ALL SELECT 'staging.stg_jira__user' source,count(*) n FROM staging.stg_jira__user
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'staging.stg_jira__comment' source,count(*) n FROM staging.stg_jira__comment UNION ALL...
                                           ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'staging.stg_jira__comment' source_name,count(*) n FROM staging.stg_jira__comment UNION ALL SELECT 'staging.stg_jira__issue' source_name,count(*) n FROM staging.stg_jira__issue UNION ALL SELECT 'staging.stg_jira__user' source_name,count(*) n FROM staging.stg_jira__user
```

结果（列顺序["source_name", "n"]）：`[["staging.stg_jira__comment", 5000], ["staging.stg_jira__issue", 8000], ["staging.stg_jira__user", 6000]]`

诊断来源：`records/021_final_diagnostics.json`；SQL：
```sql
SELECT count(*) n,count(*) FILTER(WHERE avg_outbound_influence_strength IS NULL) missing_strength,count(*) FILTER(WHERE avg_outbound_influence_strength IS NULL AND engagement_depth_score IS NOT NULL) null_policy_conflict,count(*) FILTER(WHERE total_engagement_score IS NOT NULL) scored,string_agg(DISTINCT response_pattern_type,',') response_labels,string_agg(DISTINCT influence_level,',') influence_labels FROM marts.jira__stakeholder_engagement_insights
```
结果：`[[4524, 4524, 4524, 4524, "Timely Responder,Slow Responder,Rapid Responder,Standard Responder", "Minimal Influence"]]`。

诊断来源：`records/021_final_diagnostics.json`；SQL：
```sql
SELECT count(*) mismatched_users,sum(g.total_comments_authored-coalesce(c.n,0)) excess_comments FROM marts.jira__stakeholder_engagement_insights g LEFT JOIN (SELECT author_user_id,count(*) n FROM staging.stg_jira__comment GROUP BY author_user_id) c ON g.stakeholder_id=c.author_user_id WHERE g.total_comments_authored IS DISTINCT FROM coalesce(c.n,0)
```
结果：`[[1633, 5921]]`。


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：4524行/43122格；选定基线：4524行/43122格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 4524行/43122格；L1 4524行/43122格；L2 4524行/43122格；L3 4524行/43122格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |
| response_pattern_type | L0 4524行/38598格；L1 4524行/38598格；L2 4524行/38598格；L3 4524行/38598格 | 均未整表匹配 |
| engagement_depth_score | L0 4524行/38598格；L1 4524行/38598格；L2 4524行/38598格；L3 4524行/38598格 | 均未整表匹配 |
| total_engagement_score | L0 4524行/38598格；L1 4524行/38598格；L2 4524行/38598格；L3 4524行/38598格 | 均未整表匹配 |
| stakeholder_archetype | L0 4524行/38598格；L1 4524行/38598格；L2 4524行/38598格；L3 4524行/38598格 | 均未整表匹配 |
| influence_level | L0 4524行/38598格；L1 4524行/38598格；L2 4524行/38598格；L3 4524行/38598格 | 均未整表匹配 |
| development_opportunity | L0 4524行/38598格；L1 4524行/38598格；L2 4524行/38598格；L3 4524行/38598格 | 均未整表匹配 |
| total_comments_authored | L0 4524行/41489格；L1 4524行/41489格；L2 4524行/41489格；L3 4524行/41489格 | 均未整表匹配 |
| total_projects_involved | L0 4524行/40704格；L1 4524行/40704格；L2 4524行/40704格；L3 4524行/40704格 | 均未整表匹配 |
| cross_functional_projects | L0 4524行/42766格；L1 4524行/42766格；L2 4524行/42766格；L3 4524行/42766格 | 均未整表匹配 |
| engagement_breadth_score | L0 4524行/41543格；L1 4524行/41543格；L2 4524行/41543格；L3 4524行/41543格 | 均未整表匹配 |
| engagement_quality_score | L0 4524行/41813格；L1 4524行/41813格；L2 4524行/41813格；L3 4524行/41813格 | 均未整表匹配 |
| engagement_impact_score | L0 4524行/43110格；L1 4524行/43110格；L2 4524行/43110格；L3 4524行/43110格 | 均未整表匹配 |
| engagement_risk_status | L0 4524行/40891格；L1 4524行/40891格；L2 4524行/40891格；L3 4524行/40891格 | 均未整表匹配 |
| strategic_value_score | L0 4524行/39123格；L1 4524行/39123格；L2 4524行/39123格；L3 4524行/39123格 | 均未整表匹配 |
| recommended_engagement_strategy | L0 4524行/40681格；L1 4524行/40681格；L2 4524行/40681格；L3 4524行/40681格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| whole_implementation_diagnostic | {} |
| response_pattern_type | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| engagement_depth_score | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| total_engagement_score | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_projects_involved": 2418} |
| stakeholder_archetype | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| influence_level | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| development_opportunity | {"cross_functional_projects": 356, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| total_comments_authored | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| total_projects_involved | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524} |
| cross_functional_projects | {"development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| engagement_breadth_score | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| engagement_quality_score | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| engagement_impact_score | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| engagement_risk_status | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| strategic_value_score | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "recommended_engagement_strategy": 2441, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |
| recommended_engagement_strategy | {"cross_functional_projects": 356, "development_opportunity": 4524, "engagement_breadth_score": 1579, "engagement_depth_score": 4524, "engagement_impact_score": 12, "engagement_quality_score": 1309, "engagement_risk_status": 2231, "influence_level": 4524, "response_pattern_type": 4524, "stakeholder_archetype": 4524, "strategic_value_score": 3999, "total_comments_authored": 1633, "total_engagement_score": 4524, "total_projects_involved": 2418} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

一列response_pattern同时有默认Slow与gold额外Responder后缀两种差异；整列gold表达式替换不当单一原因参与排序。按列验证的depth/total NULL及influence标签O与分类占位D并列。对于gold评论放大/项目coalesce差异，只记O诊断；不将gold数值当业务真值。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-011_jira__stakeholder_engagement_insights.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-011_jira__stakeholder_engagement_insights/021_impl-011_jira__stakeholder_engagement_insights.json`。
- 重跑：`records/021_reruns_impl-011_jira__stakeholder_engagement_insights.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_detailed_reruns_impl-011_jira__stakeholder_engagement_insights.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_extra_reruns_impl-011_jira__stakeholder_engagement_insights.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
