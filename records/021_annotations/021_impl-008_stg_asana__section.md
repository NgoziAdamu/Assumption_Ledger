# impl-008 / stg_asana__section（全量）

## 结论

主要原因：**C**；把握：高。项目ID转换后为NULL仍保留，违反必填约束。

参与因素：无经单修确认的其他参与因素。标记：无。

## 差异与归因依据

契约project_id为BIGINT且not_null。raw.project_id非NULL不保证TRY_CAST后非NULL；agent只过滤原字符串。目标结果增加project_id IS NOT NULL后7行/14格→0。

层：staging；实际schema：staging；评测键：section_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml:215–238`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/staging/stg_asana__section.sql:1–8`，SHA-256 `556bdc2761a6469a5bf32724442f8eb5630d49f79182b47a9938a3dfaeb71c6c`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/staging/stg_asana__section.sql:1–37`，SHA-256 `b200fedb21f7ecd314f116e1e2c2433ddd6c2771213a3fa5ec9391e55ed364b8`。

- required_project_id：agent SQL第8行起：
```sql
WHERE _rn = 1
```
替换为：
```sql
WHERE _rn = 1 AND project_id IS NOT NULL
```

## agent可见证据与不确定性

**只有通用策略说明**。

event53：staging 中对必需键为空或严重无效的记录进行过滤；实体表对主键重复按键去重，关系表不额外去重。未点名section.project_id转换失败。

最终报告原句（其适用范围按上文判定）：

> - 日期文本使用 `TRY_STRPTIME` 处理源数据中 `+0800` 时区格式，无法解析的可选日期会转为 NULL。

> - staging 中对必需键为空或严重无效的记录进行过滤；实体表对主键重复按键去重，关系表不额外去重。日期字段按可解析性进行清洗，任务 `modified_at` 的非日期污染行被排除。

> - 合同内部对 story 类型存在不一致：staging 允许的枚举不包含 `system`，但 task-story 逻辑要求 `story_type='system'` 才识别 assigned/completed 等系统动作。严格按 staging 合同清洗后，`system` 类型不能通过该枚举验证，故事动作因而归为 `other`，依赖系统动作的下游指标会受到影响；本实现未擅自扩充允许值。

扫描55个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=6。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 12 | 11 | False |
| 14 | 13 | False |
| 28 | 27 | False |
| 30 | 29 | False |
| 38 | 37 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：1；核实代价档：一条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE project_id IS NOT NULL AND try_cast(project_id AS BIGINT) IS NULL) invalid_numeric_project FROM raw.section_data
```

结果（列顺序["n", "invalid_numeric_project"]）：`[[200, 10]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：7行/14格；选定基线：7行/14格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 7行/14格；L1 7行/14格；L2 7行/14格；L3 7行/14格 | 均未整表匹配 |
| required_project_id | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {} |
| required_project_id | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-008_stg_asana__section.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-008_stg_asana__section/021_impl-008_stg_asana__section.json`。
- 重跑：`records/021_reruns_impl-008_stg_asana__section.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
