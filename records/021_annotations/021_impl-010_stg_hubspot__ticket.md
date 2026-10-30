# impl-010 / stg_hubspot__ticket（全量）

## 结论

主要原因：**不可评估**；把握：高。本表存在gold与initial/agent不同的原始依赖，三侧逐表诊断满足不可评估条件。

参与因素：不适用。标记：无。

## 差异与归因依据

逐张沿008依赖边回溯，并重新只读核对初始库、agent留存库与gold的结构、行数、内容哈希。以下原始依赖initial=agent且gold不同；不对其SQL差异归U/D/C/A/I/O/X。保留基线仅为机械诊断。

层：staging；实际schema：staging；评测键：ticket_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml:160–192`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__ticket.sql:1–16`，SHA-256 `5c910343cec54f41bceb2552876310c9a3f1cb2b9e066d796f790deb58103cbc`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/staging/stg_hubspot__ticket.sql:1–91`，SHA-256 `cc093363468c954b94f0a24707186bdb0007428bb16786a3c8221952b3657305`。



## agent可见证据与不确定性

**没有迹象**。

检查本题全部75个事件和event73最终报告，没有关于gold使用另一版raw的迹象；agent无法访问gold。不把一般解析说明当成知道评测输入不一致。

扫描75个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=26。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 10 | 9 | False |
| 14 | 13 | False |
| 32 | 31 | False |
| 34 | 33 | False |
| 36 | 35 | False |
| 40 | 39 | False |
| 50 | 49 | False |
| 52 | 51 | False |
| 62 | 61 | False |
| 64 | 63 | False |
| 66 | 65 | False |

## 原始数据一致性与查询

| raw | 依赖链 | initial=agent | gold=initial |
|---|---|---|---|
| raw.ticket_data | raw.ticket_data → staging.stg_hubspot__ticket | True | False |
三侧每表结构、行数、SHA-256及实际只读查询记录在 `records/021_raw_diagnosis.json`，不是按题目推断。

核实查询条数（含失败尝试）：0；核实代价档：判断不了。每张不超过5条。

无独立核实查询；本表三侧raw比较为允许读取gold的诊断，不计核实限额。

## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：117行/117格；选定基线：117行/117格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 117行/117格；L1 117行/117格；L2 117行/117格；L3 117行/117格 | 均未整表匹配 |

不适用：不可评估。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"is_ticket_deleted": 117} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

不可评估按逐表raw依赖判定，包括后续CS层沿来源链的原始依赖；不把整题一概跳过。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-010_stg_hubspot__ticket.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-010_stg_hubspot__ticket/021_impl-010_stg_hubspot__ticket.json`。
- 重跑：`records/021_reruns_impl-010_stg_hubspot__ticket.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
