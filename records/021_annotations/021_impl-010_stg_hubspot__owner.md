# impl-010 / stg_hubspot__owner（全量）

## 结论

主要原因：**O**；把握：高。gold把所有owner时间戳置NULL，created_timestamp违反契约not_null。

参与因素：无经单修确认的其他参与因素。标记：无。

## 差异与归因依据

两列原始值均可按前19位解析200行，agent按契约TIMESTAMP输出；gold用完整匹配正则 ^\d{4}-\d{2}-\d{2} 检查含时间后缀字符串，200行均不匹配。单列采用gold规则各减200格，行数不变；仅为诊断，不把NULL改写当正确修复。

层：staging；实际schema：staging；评测键：owner_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml:193–223`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__owner.sql:1–14`，SHA-256 `39af2a049c430bec09a60fc7032c24c4610309b3f303bef308d656c8595d2ded`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/staging/stg_hubspot__owner.sql:1–62`，SHA-256 `cec3fef2891e1a41bcfa170150ca9d02be66f6963ee40679fc44ebbfc0ec74fc`。

- created_timestamp：agent SQL第10行起：
```sql
try_strptime(substr(created_at, 1, 19), '%Y-%m-%d %H:%M:%S')
```
替换为：
```sql
CASE WHEN created_at IS NOT NULL AND CAST(created_at AS VARCHAR) ~ '^\d{4}-\d{2}-\d{2}' THEN CAST(created_at AS TIMESTAMP) ELSE NULL END
```

- updated_timestamp：agent SQL第11行起：
```sql
try_strptime(substr(updated_at, 1, 19), '%Y-%m-%d %H:%M:%S')
```
替换为：
```sql
CASE WHEN updated_at IS NOT NULL AND CAST(updated_at AS VARCHAR) ~ '^\d{4}-\d{2}-\d{2}' THEN CAST(updated_at AS TIMESTAMP) ELSE NULL END
```

## agent可见证据与不确定性

**只有通用策略说明**。

event73：原始 HubSpot 时间字符串按日期时间前 19 位解析，以支持时区偏移和小数秒，同时输出合同指定的无时区 `TIMESTAMP`。空值或无法解析的时间转换为 NULL。该策略未点名owner。

最终报告原句（其适用范围按上文判定）：

> - 原始 HubSpot 时间字符串按日期时间前 19 位解析，以支持时区偏移和小数秒，同时输出合同指定的无时区 `TIMESTAMP`。空值或无法解析的时间转换为 NULL；必需创建日期无效的行按合同要求排除。

> - 未对合同要求保留的重复行额外去重。源数据缺失/无效属性或关联缺失会造成输出 NULL、约定的默认值或零值；源端重复及多重关联可能按合同连接规则传播至下游。

扫描75个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=25。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 10 | 9 | False |
| 14 | 13 | False |
| 34 | 33 | False |
| 36 | 35 | False |
| 40 | 39 | False |
| 50 | 49 | False |
| 52 | 51 | False |
| 64 | 63 | False |
| 66 | 65 | False |

## 原始数据一致性与查询

| raw | 依赖链 | initial=agent | gold=initial |
|---|---|---|---|
| raw.owner_data | raw.owner_data → staging.stg_hubspot__owner | True | True |
三侧每表结构、行数、SHA-256及实际只读查询记录在 `records/021_raw_diagnosis.json`，不是按题目推断。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/hubspot.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE try_cast(created_at AS TIMESTAMP) IS NOT NULL) created_parseable,count(*) FILTER(WHERE created_at ~ '^\d{4}-\d{2}-\d{2}') created_regex_full_matches,count(*) FILTER(WHERE try_cast(updated_at AS TIMESTAMP) IS NOT NULL) updated_parseable FROM raw.owner_data
```

结果（列顺序["n", "created_parseable", "created_regex_full_matches", "updated_parseable"]）：`[[200, 0, 0, 0]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/hubspot.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE try_strptime(substr(created_at,1,19),'%Y-%m-%d %H:%M:%S') IS NOT NULL) created_prefix_parseable,count(*) FILTER(WHERE try_strptime(substr(updated_at,1,19),'%Y-%m-%d %H:%M:%S') IS NOT NULL) updated_prefix_parseable FROM raw.owner_data
```

结果（列顺序["n", "created_prefix_parseable", "updated_prefix_parseable"]）：`[[200, 200, 200]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：200行/400格；选定基线：200行/400格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 200行/400格；L1 200行/400格；L2 200行/400格；L3 200行/400格 | 均未整表匹配 |
| created_timestamp | L0 200行/200格；L1 200行/200格；L2 200行/200格；L3 200行/200格 | 均未整表匹配 |
| updated_timestamp | L0 200行/200格；L1 200行/200格；L2 200行/200格；L3 200行/200格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"created_timestamp": 200, "updated_timestamp": 200} |
| created_timestamp | {"updated_timestamp": 200} |
| updated_timestamp | {"created_timestamp": 200} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

updated_timestamp没有not_null，但与created_timestamp使用同一gold正则全串匹配机制。按O并列的同一解析差异处理；明确not_null矛盾只在created列。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-010_stg_hubspot__owner.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-010_stg_hubspot__owner/021_impl-010_stg_hubspot__owner.json`。
- 重跑：`records/021_reruns_impl-010_stg_hubspot__owner.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
