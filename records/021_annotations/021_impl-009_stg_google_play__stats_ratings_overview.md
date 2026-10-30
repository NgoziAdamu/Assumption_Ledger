# impl-009 / stg_google_play__stats_ratings_overview（全量）

## 结论

主要原因：**C**；把握：高。缺少date_day必填过滤，保留2928条NULL日期行。

参与因素：无经单修确认的其他参与因素。标记：无。

## 差异与归因依据

raw.date全部NULL；契约date_day not_null，agent只TRY_CAST不删行。追加输出必填过滤后2928行→0，与gold L0一致。

层：staging；实际schema：staging；评测键：date_day, package_name。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml:185–201`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__stats_ratings_overview.sql:1–7`，SHA-256 `d267487bcded89f289b35404826b9afe9a48dd17f24282cf5cc31ca62a043504`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/staging/stg_google_play__stats_ratings_overview.sql:1–46`，SHA-256 `9b6801c18bec9a91fe5e463835b36500e5564eadd64d8ab1c3be19bfde8ea8f0`。

- required_fields：agent SQL第7行起：
```sql
FROM raw.stats_ratings_overview
```
替换为：
```sql
FROM raw.stats_ratings_overview WHERE date_day IS NOT NULL AND package_name IS NOT NULL
```

## agent可见证据与不确定性

**看到了但没提**。

event13→14和23→24呈现原始/输出信息，event54仍显示本表2928行；event67提到的是installs_overview.date为空，没有针对ratings_overview的遗漏说明。

扫描69个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=17。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 12 | 11 | False |
| 14 | 13 | False |
| 20 | 19 | False |
| 24 | 23 | False |
| 38 | 37 | False |
| 44 | 43 | False |
| 54 | 53 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：1；核实代价档：一条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE date IS NULL) null_date,count(*) FILTER(WHERE package_name IS NULL) null_package FROM raw.stats_ratings_overview
```

结果（列顺序["n", "null_date", "null_package"]）：`[[2928, 2928, 0]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：2928行/11712格；选定基线：2928行/11712格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 2928行/11712格；L1 2928行/11712格；L2 2928行/11712格；L3 2928行/11712格 | 均未整表匹配 |
| required_fields | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {} |
| required_fields | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-009_stg_google_play__stats_ratings_overview.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-009_stg_google_play__stats_ratings_overview/021_impl-009_stg_google_play__stats_ratings_overview.json`。
- 重跑：`records/021_reruns_impl-009_stg_google_play__stats_ratings_overview.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
