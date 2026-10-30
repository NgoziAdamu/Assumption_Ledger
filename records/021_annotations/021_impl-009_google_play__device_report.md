# impl-009 / google_play__device_report（全量）

## 结论

主要原因：**D**；把握：高。device mart的日指标和累计值全被0/NULL占位。

参与因素：无经单修确认的其他参与因素。标记：已披露。

## 差异与归因依据

已有daily_device/user/event/active_device指标却未映射；遗漏ratings连接、累计和前向填充。独立日指标修复有格子改善；完整实现诊断L0一致。

层：marts；实际schema：mart；评测键：date_day, device, package_name。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml:1640–1722`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql:1–20`，SHA-256 `c68500309e0c2e4e3a7c135b70dab7419c8500627c18814f287b7ea41e7acea8`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/marts/google_play__device_report.sql:1–141`，SHA-256 `f8440e795e89e62d3d13e346e49afd6ed4012ad82122ff1547c8d1df012d0700`。

- whole_implementation_diagnostic：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_reruns_impl-009_google_play__device_report.json`。

- device_installs：agent SQL第5行起：
```sql
cast(0 as BIGINT) AS device_installs
```
替换为：
```sql
cast(coalesce(src.daily_device_installs,0) as BIGINT) AS device_installs
```

- device_uninstalls：agent SQL第6行起：
```sql
cast(0 as BIGINT) AS device_uninstalls
```
替换为：
```sql
cast(coalesce(src.daily_device_uninstalls,0) as BIGINT) AS device_uninstalls
```

- device_upgrades：agent SQL第7行起：
```sql
cast(NULL as BIGINT) AS device_upgrades
```
替换为：
```sql
cast(coalesce(src.daily_device_upgrades,0) as BIGINT) AS device_upgrades
```

- user_installs：agent SQL第8行起：
```sql
cast(NULL as BIGINT) AS user_installs
```
替换为：
```sql
cast(coalesce(src.daily_user_installs,0) as BIGINT) AS user_installs
```

- user_uninstalls：agent SQL第9行起：
```sql
cast(NULL as BIGINT) AS user_uninstalls
```
替换为：
```sql
cast(coalesce(src.daily_user_uninstalls,0) as BIGINT) AS user_uninstalls
```

- install_events：agent SQL第10行起：
```sql
cast(NULL as BIGINT) AS install_events
```
替换为：
```sql
cast(src.install_events as BIGINT) AS install_events
```

- uninstall_events：agent SQL第11行起：
```sql
cast(NULL as BIGINT) AS uninstall_events
```
替换为：
```sql
cast(src.uninstall_events as BIGINT) AS uninstall_events
```

- update_events：agent SQL第12行起：
```sql
cast(NULL as BIGINT) AS update_events
```
替换为：
```sql
cast(src.update_events as BIGINT) AS update_events
```

- active_devices_last_30_days：agent SQL第13行起：
```sql
cast(NULL as BIGINT) AS active_devices_last_30_days
```
替换为：
```sql
cast(coalesce(src.active_device_installs,0) as BIGINT) AS active_devices_last_30_days
```

## agent可见证据与不确定性

**只有通用策略说明**。

event35批量单源投影；event67泛称“多项 marts”的完整join/窗口未实现。

最终报告原句（其适用范围按上文判定）：

> 本次交付**未完整实现数据合同中的全部业务逻辑**。留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。`run.py` 成功只能证明 SQL 可执行，不能证明输出满足全部业务定义或可用于生产分析。

> - Earnings 源数据 `transaction_date` 为空而 `transaction_time` 有值；为提供可用日期，暂用 `transaction_time` 日期部分回填。源 SKU 为空时用可用的 product/base-plan 值兜底。

扫描69个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=12。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 20 | 19 | False |
| 24 | 23 | False |
| 38 | 37 | False |
| 42 | 41 | False |
| 44 | 43 | False |
| 54 | 53 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'staging.stg_google_play__stats_installs_device' source,count(*) n FROM staging.stg_google_play__stats_installs_device
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'staging.stg_google_play__stats_installs_device' source,count(*) n FROM staging.stg_google_play__stats_insta...
                                                                ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'staging.stg_google_play__stats_installs_device' source_name,count(*) n FROM staging.stg_google_play__stats_installs_device
```

结果（列顺序["source_name", "n"]）：`[["staging.stg_google_play__stats_installs_device", 1360]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：1360行/19040格；选定基线：1360行/19040格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 1360行/19040格；L1 1360行/19040格；L2 1360行/19040格；L3 1360行/19040格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |
| device_installs | L0 1360行/17680格；L1 1360行/17680格；L2 1360行/17680格；L3 1360行/17680格 | 均未整表匹配 |
| device_uninstalls | L0 1360行/17680格；L1 1360行/17680格；L2 1360行/17680格；L3 1360行/17680格 | 均未整表匹配 |
| device_upgrades | L0 1360行/17680格；L1 1360行/17680格；L2 1360行/17680格；L3 1360行/17680格 | 均未整表匹配 |
| user_installs | L0 1360行/17680格；L1 1360行/17680格；L2 1360行/17680格；L3 1360行/17680格 | 均未整表匹配 |
| user_uninstalls | L0 1360行/17680格；L1 1360行/17680格；L2 1360行/17680格；L3 1360行/17680格 | 均未整表匹配 |
| install_events | L0 1360行/17680格；L1 1360行/17680格；L2 1360行/17680格；L3 1360行/17680格 | 均未整表匹配 |
| uninstall_events | L0 1360行/17680格；L1 1360行/17680格；L2 1360行/17680格；L3 1360行/17680格 | 均未整表匹配 |
| update_events | L0 1360行/17680格；L1 1360行/17680格；L2 1360行/17680格；L3 1360行/17680格 | 均未整表匹配 |
| active_devices_last_30_days | L0 1360行/17680格；L1 1360行/17680格；L2 1360行/17680格；L3 1360行/17680格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"active_devices_last_30_days": 1360, "average_rating": 1360, "device_installs": 1360, "device_uninstalls": 1360, "device_upgrades": 1360, "install_events": 1360, "net_device_installs": 1360, "rolling_total_average_rating": 1360, "total_device_installs": 1360, "total_device_uninstalls": 1360, "uninstall_events": 1360, "update_events": 1360, "user_installs": 1360, "user_uninstalls": 1360} |
| whole_implementation_diagnostic | {} |
| device_installs | {"active_devices_last_30_days": 1360, "average_rating": 1360, "device_uninstalls": 1360, "device_upgrades": 1360, "install_events": 1360, "net_device_installs": 1360, "rolling_total_average_rating": 1360, "total_device_installs": 1360, "total_device_uninstalls": 1360, "uninstall_events": 1360, "update_events": 1360, "user_installs": 1360, "user_uninstalls": 1360} |
| device_uninstalls | {"active_devices_last_30_days": 1360, "average_rating": 1360, "device_installs": 1360, "device_upgrades": 1360, "install_events": 1360, "net_device_installs": 1360, "rolling_total_average_rating": 1360, "total_device_installs": 1360, "total_device_uninstalls": 1360, "uninstall_events": 1360, "update_events": 1360, "user_installs": 1360, "user_uninstalls": 1360} |
| device_upgrades | {"active_devices_last_30_days": 1360, "average_rating": 1360, "device_installs": 1360, "device_uninstalls": 1360, "install_events": 1360, "net_device_installs": 1360, "rolling_total_average_rating": 1360, "total_device_installs": 1360, "total_device_uninstalls": 1360, "uninstall_events": 1360, "update_events": 1360, "user_installs": 1360, "user_uninstalls": 1360} |
| user_installs | {"active_devices_last_30_days": 1360, "average_rating": 1360, "device_installs": 1360, "device_uninstalls": 1360, "device_upgrades": 1360, "install_events": 1360, "net_device_installs": 1360, "rolling_total_average_rating": 1360, "total_device_installs": 1360, "total_device_uninstalls": 1360, "uninstall_events": 1360, "update_events": 1360, "user_uninstalls": 1360} |
| user_uninstalls | {"active_devices_last_30_days": 1360, "average_rating": 1360, "device_installs": 1360, "device_uninstalls": 1360, "device_upgrades": 1360, "install_events": 1360, "net_device_installs": 1360, "rolling_total_average_rating": 1360, "total_device_installs": 1360, "total_device_uninstalls": 1360, "uninstall_events": 1360, "update_events": 1360, "user_installs": 1360} |
| install_events | {"active_devices_last_30_days": 1360, "average_rating": 1360, "device_installs": 1360, "device_uninstalls": 1360, "device_upgrades": 1360, "net_device_installs": 1360, "rolling_total_average_rating": 1360, "total_device_installs": 1360, "total_device_uninstalls": 1360, "uninstall_events": 1360, "update_events": 1360, "user_installs": 1360, "user_uninstalls": 1360} |
| uninstall_events | {"active_devices_last_30_days": 1360, "average_rating": 1360, "device_installs": 1360, "device_uninstalls": 1360, "device_upgrades": 1360, "install_events": 1360, "net_device_installs": 1360, "rolling_total_average_rating": 1360, "total_device_installs": 1360, "total_device_uninstalls": 1360, "update_events": 1360, "user_installs": 1360, "user_uninstalls": 1360} |
| update_events | {"active_devices_last_30_days": 1360, "average_rating": 1360, "device_installs": 1360, "device_uninstalls": 1360, "device_upgrades": 1360, "install_events": 1360, "net_device_installs": 1360, "rolling_total_average_rating": 1360, "total_device_installs": 1360, "total_device_uninstalls": 1360, "uninstall_events": 1360, "user_installs": 1360, "user_uninstalls": 1360} |
| active_devices_last_30_days | {"average_rating": 1360, "device_installs": 1360, "device_uninstalls": 1360, "device_upgrades": 1360, "install_events": 1360, "net_device_installs": 1360, "rolling_total_average_rating": 1360, "total_device_installs": 1360, "total_device_uninstalls": 1360, "uninstall_events": 1360, "update_events": 1360, "user_installs": 1360, "user_uninstalls": 1360} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-009_google_play__device_report.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-009_google_play__device_report/021_impl-009_google_play__device_report.json`。
- 重跑：`records/021_reruns_impl-009_google_play__device_report.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_supplement_reruns_impl-009_google_play__device_report.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
