# impl-011 / int_jira__pivot_daily_field_history（全量）

## 结论

主要原因：**C**；把握：高。在pivot后把未更新字段也填is_null，混淆未变化与真实NULL更新。

参与因素：C：status（减0行/9738格）；C：sprint（减0行/2025格）；C：story_points（减0行/7746格）。标记：无。

## 差异与归因依据

契约明确仅真实NULL field_value变为is_null，未更新字段仍NULL。agent对pivot后的四列统一COALESCE。四个输出各单独把NULL处理移到聚合前；story_point_estimate减少9755格最多，为主因，其余同类C参与因素。

层：intermediate；实际schema：intermediate；评测键：issue_id, issue_day_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml:1716–1753`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql:1–1`，SHA-256 `60a973a17bdc42d140f9f9825153e8ddc47acf1c9fb996dc4ccebc3d143adf67`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/intermediate/field_history/int_jira__pivot_daily_field_history.sql:1–156`，SHA-256 `16c712c62beb72b0a985565ffdac85b0416d678fbd91493c9b0a0c1cd7dbdbea`。

- status：agent SQL第1行起：
```sql
max(field_value) filter(where lower(field_id)='status') status
```
替换为：
```sql
max(coalesce(field_value,'is_null')) filter(where lower(field_id)='status') status
```

- status：agent SQL第1行起：
```sql
coalesce(status,'is_null') status
```
替换为：
```sql
status
```

- sprint：agent SQL第1行起：
```sql
max(field_value) filter(where lower(field_name)='sprint') sprint
```
替换为：
```sql
max(coalesce(field_value,'is_null')) filter(where lower(field_name)='sprint') sprint
```

- sprint：agent SQL第1行起：
```sql
coalesce(sprint,'is_null') sprint
```
替换为：
```sql
sprint
```

- story_points：agent SQL第1行起：
```sql
max(field_value) filter(where lower(field_name)='story points') story_points
```
替换为：
```sql
max(coalesce(field_value,'is_null')) filter(where lower(field_name)='story points') story_points
```

- story_points：agent SQL第1行起：
```sql
coalesce(story_points,'is_null') story_points
```
替换为：
```sql
story_points
```

- story_point_estimate：agent SQL第1行起：
```sql
max(field_value) filter(where lower(field_name)='story point estimate') story_point_estimate
```
替换为：
```sql
max(coalesce(field_value,'is_null')) filter(where lower(field_name)='story point estimate') story_point_estimate
```

- story_point_estimate：agent SQL第1行起：
```sql
coalesce(story_point_estimate,'is_null') story_point_estimate
```
替换为：
```sql
story_point_estimate
```

## agent可见证据与不确定性

**看到了但没提**。

event9→10已见field_history字段；event15写pivot；event26/32/38包含模型列/执行信息，未说明未更新与NULL更新的区分。

扫描57个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=32。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 22 | 21 | False |
| 24 | 23 | False |
| 26 | 25 | False |
| 32 | 31 | False |
| 38 | 37 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：1；核实代价档：一条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE field_value IS NULL) null_updates,count(distinct field_id) fields FROM intermediate.int_jira__issue_field_history
```

结果（列顺序["n", "null_updates", "fields"]）：`[[12000, 0, 700]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：9755行/29264格；选定基线：9755行/29264格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 9755行/29264格；L1 9755行/29264格；L2 9755行/29264格；L3 9755行/29264格 | 均未整表匹配 |
| status | L0 9755行/19526格；L1 9755行/19526格；L2 9755行/19526格；L3 9755行/19526格 | 均未整表匹配 |
| sprint | L0 9755行/27239格；L1 9755行/27239格；L2 9755行/27239格；L3 9755行/27239格 | 均未整表匹配 |
| story_points | L0 9755行/21518格；L1 9755行/21518格；L2 9755行/21518格；L3 9755行/21518格 | 均未整表匹配 |
| story_point_estimate | L0 9755行/19509格；L1 9755行/19509格；L2 9755行/19509格；L3 9755行/19509格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"sprint": 2025, "status": 9738, "story_point_estimate": 9755, "story_points": 7746} |
| status | {"sprint": 2025, "story_point_estimate": 9755, "story_points": 7746} |
| sprint | {"status": 9738, "story_point_estimate": 9755, "story_points": 7746} |
| story_points | {"sprint": 2025, "status": 9738, "story_point_estimate": 9755} |
| story_point_estimate | {"sprint": 2025, "status": 9738, "story_points": 7746} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-011_int_jira__pivot_daily_field_history.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-011_int_jira__pivot_daily_field_history/021_impl-011_int_jira__pivot_daily_field_history.json`。
- 重跑：`records/021_reruns_impl-011_int_jira__pivot_daily_field_history.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
