# impl-025 / stg_twilio__call（校准）

## 结论

主要原因：**C**；把握：高。契约对不满足+1格式的电话规定nullify_field，agent先移除非数字并加+1使不合规值通过。整项电话处理规则单修L0匹配；拆开两列时contact修复减少10行、user减少9行，均同类C。price_in_usd不在官方比较列，不算判错原因。

参与因素：无：两个电话字段在盲标中作为同一预修复策略，另保留逐列测试。。标记：无。

## 差异与归因依据

契约对不满足+1格式的电话规定nullify_field，agent先移除非数字并加+1使不合规值通过。整项电话处理规则单修L0匹配；拆开两列时contact修复减少10行、user减少9行，均同类C。price_in_usd不在官方比较列，不算判错原因。

层：staging；比较库schema：staging；评测键：call_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-025/docs/data_contract.yaml:116–191`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/sql/staging/stg_twilio__call.sql:1–48`；SHA-256 `423cf39d36b0345a8f8e6a484d4f3afadd55f68a2fb4474360c369d8f22f38ae`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-025/sql/staging/stg_twilio__call.sql:1–72`；SHA-256 `2f36433979e9d54a579f472fa207b9f5b2d2c004fed7b2d189ec0e123715f8c4`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- phone_user（agent SQL 第18行起）：
```sql
regexp_replace(regexp_replace(try_cast("from" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as user_phone_number_raw
```
→
```sql
try_cast("from" as varchar) as user_phone_number_raw
```

- phone_contact（agent SQL 第19行起）：
```sql
regexp_replace(regexp_replace(try_cast("to" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as contact_phone_number_raw
```
→
```sql
try_cast("to" as varchar) as contact_phone_number_raw
```

- phone_policy（agent SQL 第18行起）：
```sql
regexp_replace(regexp_replace(try_cast("from" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as user_phone_number_raw
```
→
```sql
try_cast("from" as varchar) as user_phone_number_raw
```

- phone_policy（agent SQL 第18行起）：
```sql
regexp_replace(regexp_replace(try_cast("to" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as contact_phone_number_raw
```
→
```sql
try_cast("to" as varchar) as contact_phone_number_raw
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

020_reruns_impl-025_stg_twilio__call.json；event15/16源schema与样例；event23/24清理后电话分布；event41泛称依契约清理非法日期、枚举、电话和字段值，没有说明本表先补+号的选择。 原句：event41：依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。

完整事件扫描数：43；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 10 | 9 | stg_twilio__call,call_data | False |
| 12 | 11 | stg_twilio__call,call_data | False |
| 16 | 15 | call_data | False |
| 20 | 19 | stg_twilio__call,call_data | False |
| 22 | 21 | stg_twilio__call | False |
| 24 | 23 | stg_twilio__call | False |
| 26 | 25 | stg_twilio__call | False |
| 28 | 27 | stg_twilio__call | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：1；核实代价档：一条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/twilio.duckdb`

```sql
SELECT count(*) n, count(*) FILTER(WHERE regexp_matches("from", '^\+1[0-9]{10}$')) valid_from, count(*) FILTER(WHERE regexp_matches("to", '^\+1[0-9]{10}$')) valid_to FROM raw.call_data
```

结果：`[[2500, 0, 0]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=44 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-025_stg_twilio__call/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：2492行 / 4965格；重跑基线：2492行 / 4965格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:2492行/4965格 / L1:2492行/4965格 / L2:2492行/4965格 / L3:2492行/4965格 | 均未整表匹配 |
| phone_user | L0:2483行/2483格 / L1:2483行/2483格 / L2:2483行/2483格 / L3:2483行/2483格 | 均未整表匹配 |
| phone_contact | L0:2482行/2482格 / L1:2482行/2482格 / L2:2482行/2482格 / L3:2482行/2482格 | 均未整表匹配 |
| phone_policy | L0:0行/0格 / L1:0行/0格 / L2:0行/0格 / L3:0行/0格 | L0 |

不适用：C；整项电话策略改动L0匹配。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"contact_phone_number": 2483, "user_phone_number": 2482} |
| phone_user | {"contact_phone_number": 2483} |
| phone_contact | {"user_phone_number": 2482} |
| phone_policy | {} |

本表全部重跑证据文件：`records/020_reruns_impl-025_stg_twilio__call.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。统一电话规范化策略的两个字段另有单列重跑，避免把整项策略掩盖成两个独立主要原因。 盲标按同一电话预修复策略归一项，018按两列独立排序并将user列记参与因素；盲标保留，单列试验显示contact减10行，user减9行。

## 证据路径

- 精简材料包：`records/013_packages/013_impl-025_staging_stg_twilio__call.md`。
- 重跑：`records/020_reruns_impl-025_stg_twilio__call.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
