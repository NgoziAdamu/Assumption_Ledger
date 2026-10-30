# impl-011 / int_jira__issue_calendar_spine（全量）

## 结论

主要原因：**C**；把握：高。未按resolved_at区分open_until，导致大规模日期窗口差异。

参与因素：A：history_driver（减1482146行/4446438格）。标记：无。

## 差异与归因依据

契约明确未解决issue的open_until为今天；agent不看resolved_at，直接coalesce(valid_starting_on,today)。单改CASE显著减少行规模。另一个history驱动与issue驱动的范围选择独立诊断，按其实际改善记录；不把两项合成一次U实验。

层：intermediate；实际schema：intermediate；评测键：issue_day_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml:1415–1444`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_calendar_spine.sql:1–1`，SHA-256 `0abbf26265983866f09b8f7074bd88466f2ef76e7c7ec0f048fc9bb585dfc387`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/intermediate/field_history/int_jira__issue_calendar_spine.sql:1–70`，SHA-256 `cb3b3ff1a837803d916c3aeac3873d9d1271495ab6b830acd26a541388b3cdd3`。

- unresolved_open_until：agent SQL第1行起：
```sql
coalesce(cast(valid_starting_on as date),DATE '2025-10-13')
```
替换为：
```sql
case when i.resolved_at is null then DATE '2025-10-13' else cast(valid_starting_on as date) end
```

- history_driver：agent SQL第1行起：
```sql
from staging.stg_jira__issue i left join intermediate.int_jira__field_history_scd f using(issue_id)
```
替换为：
```sql
from intermediate.int_jira__field_history_scd f left join staging.stg_jira__issue i using(issue_id)
```

## agent可见证据与不确定性

**看到了但没提**。

event43→44展示本表SQL与issue_users；event9→10显示raw issue含resolved列。event55只报告calendar为空，未说明open_until的分支选择。

扫描57个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=29。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
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

核实查询条数（含失败尝试）：1；核实代价档：一条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE resolved_at IS NULL) unresolved FROM staging.stg_jira__issue
```

结果（列顺序["n", "unresolved"]）：`[[8000, 3205]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：4715176行/12116456格；选定基线：4715176行/12116456格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 2}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 4715176行/12116456格；L1 4715176行/12116456格；L2 4715176行/12116456格；L3 4715176行/12116456格 | 均未整表匹配 |
| unresolved_open_until | L0 620610行/1861830格；L1 620610行/1861830格；L2 620610行/1861830格；L3 620610行/1861830格 | 均未整表匹配 |
| history_driver | L0 3233030行/7670018格；L1 3233030行/7670018格；L2 3233030行/7670018格；L3 3233030行/7670018格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"earliest_open_until_week": 1014536} |
| unresolved_open_until | {} |
| history_driver | {"earliest_open_until_week": 1014536} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

契约写每个issue的open窗口，却未明确无history issue的驱动关系。按A独立测试history驱动；主因C不依赖这一读法。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-011_int_jira__issue_calendar_spine.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-011_int_jira__issue_calendar_spine/021_impl-011_int_jira__issue_calendar_spine.json`。
- 重跑：`records/021_fast_reruns_impl-011_int_jira__issue_calendar_spine.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
