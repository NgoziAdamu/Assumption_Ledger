# impl-011 / int_jira__issue_users（全量）

## 结论

主要原因：**I**；把握：中。正确计算了修订parent，却命名为parent_issue_id_derived，评测列仍是原值。

参与因素：无经单修确认的其他参与因素。标记：无。

## 差异与归因依据

代码自身含正确coalesce(revised_parent_issue_id,parent_issue_id)，但i.*先保留原parent_issue_id，派生值另起名字。仅把正确表达式放到契约输出名并保留原始列，13行/格→0。按手册允许的代码自身正确意图证据归I。

层：intermediate；实际schema：intermediate；评测键：issue_id, project_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml:1559–1695`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_users.sql:1–1`，SHA-256 `d534cb67aa6c25fae9fc4c847d6673474758c223963d94d8ae3ca67f8ff00972`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/intermediate/int_jira__issue_users.sql:1–39`，SHA-256 `5c71d94370a70b344764f648bd05c6e8068fd71e0c46b5e76ec423698c11b947`。

- derived_parent_name：agent SQL第1行起：
```sql
i.*,coalesce(i.revised_parent_issue_id,i.parent_issue_id) parent_issue_id_derived
```
替换为：
```sql
i.issue_id,coalesce(cast(i.revised_parent_issue_id as varchar),cast(i.parent_issue_id as varchar)) parent_issue_id,i.*
```

## agent可见证据与不确定性

**看到了但没提**。

event41→42、43→44直接展示含正确coalesce和错误输出别名的SQL；event55仅笼统说修复别名/窗口问题，未点名本处。

扫描57个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=31。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 22 | 21 | False |
| 24 | 23 | False |
| 32 | 31 | False |
| 38 | 37 | False |
| 42 | 41 | False |
| 44 | 43 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：1；核实代价档：一条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE revised_parent_issue_id IS NOT NULL AND revised_parent_issue_id::VARCHAR IS DISTINCT FROM parent_issue_id::VARCHAR) revised_diff FROM intermediate.int_jira__issue_type_parents
```

结果（列顺序["n", "revised_diff"]）：`[[8000, 13]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：13行/13格；选定基线：13行/13格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 13行/13格；L1 13行/13格；L2 13行/13格；L3 13行/13格 | 均未整表匹配 |
| derived_parent_name | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"parent_issue_id": 13} |
| derived_parent_name | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

C/I边界：也可把输出名不符看成C；本次代码已明确实现正确coalesce，仅列名/投影位置错，采用第3节代码自身正确意图的I条款。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-011_int_jira__issue_users.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-011_int_jira__issue_users/021_impl-011_int_jira__issue_users.json`。
- 重跑：`records/021_reruns_impl-011_int_jira__issue_users.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
