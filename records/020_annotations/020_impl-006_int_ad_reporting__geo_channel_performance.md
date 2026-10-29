> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-006 / int_ad_reporting__geo_channel_performance（全量）

## 结论

主要原因：**D**；把握：中。地理渠道分析全列 NULL，未实现地域、月份聚合及渠道指标。

参与因素：无。标记：已披露。

## 差异与归因依据

契约要求按地理渠道粒度汇总与分档；最终SQL仅从Google staging逐行输出NULL。与gold空结果的差异是实际输出了26031条占位行。

层：intermediate；比较库schema：intermediate；评测键：country_code, region。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:1890–1988`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__geo_channel_performance.sql:1–32`；SHA-256 `952b30ade28995da20c29e606551d108980eaa8b7044079984e9074a8b696db3`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__geo_channel_performance.sql:1–198`；SHA-256 `f552354264d8ce1f5c9ae05c66df0d1ef686ef41cc2a64ced416815438b9ecbc`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- whole_implementation_diagnostic：替换指定完整实现块（诊断）；old/new完整字节见重跑JSON，私有SQL `data/020_work/impl-006_int_ad_reporting__geo_channel_performance/whole_implementation_diagnostic.sql`。

## agent可见证据与不确定性

不确定性四档：**针对本表的具体说明**。

event 97：当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | int_ad_reporting__geo_channel_performance,stg_google_ads__campaign_report | False |
| 26 | 25 | int_ad_reporting__geo_channel_performance | False |
| 30 | 29 | stg_google_ads__campaign_report | False |
| 34 | 33 | stg_google_ads__campaign_report | False |
| 38 | 37 | int_ad_reporting__geo_channel_performance,stg_google_ads__campaign_report | False |
| 48 | 47 | int_ad_reporting__geo_channel_performance | False |
| 82 | 81 | stg_google_ads__campaign_report | False |
| 84 | 83 | int_ad_reporting__geo_channel_performance | False |
| 86 | 85 | stg_google_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：1；核实代价档：一条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='staging' AND table_name='stg_google_ads__campaign_report') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["staging", "stg_google_ads__campaign_report", "source_relation", "VARCHAR"], ["staging", "stg_google_ads__campaign_report", "account_id", "VARCHAR"], ["staging", "stg_google_ads__campaign_report", "date_day", "DATE"], ["staging", "stg_google_ads__campaign_report", "campaign_id", "VARCHAR"], ["staging", "stg_google_ads__campaign_report", "ad_network_type", "VARCHAR"], ["staging", "stg_google_ads__campaign_report", "device", "VARCHAR"], ["staging", "stg_google_ads__campaign_report", "clicks", "BIGINT"], ["staging", "stg_google_ads__campaign_report", "spend", "DECIMAL(18,2)"], ["staging", "stg_google_ads__campaign_report", "impressions", "BIGINT"], ["staging", "stg_google_ads__campaign_report", "conversions", "DECIMAL(10,2)"], ["staging", "stg_google_ads__campaign_report", "conversions_value", "DECIMAL(15,2)"], ["staging", "stg_google_ads__campaign_report", "view_through_conversions", "BIGINT"]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=4 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_int_ad_reporting__geo_channel_performance/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：26031行 / 780930格；重跑基线：26031行 / 780930格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:26031行/780930格 / L1:26031行/780930格 / L2:26031行/780930格 / L3:26031行/780930格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0:0行/0格 / L1:0行/0格 / L2:0行/0格 / L3:0行/0格 | L0 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {} |
| whole_implementation_diagnostic | {} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

此表缺失的是整段聚合/分析实现，原SQL由同一个fallback生成块代替。两种读法：按每个输出列拆成多个错误点；或按整体降级/缺失聚合这一块记录。本次按后一种记录。完整gold实现替换只作诊断，不声称它是满足U第4条件的局部修复；类别依据契约和轨迹直接证据。无法从整段替换推定各未实现子计算的相对贡献。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_int_ad_reporting__geo_channel_performance.md`。
- 重跑：`records/020_reruns_impl-006_int_ad_reporting__geo_channel_performance.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
