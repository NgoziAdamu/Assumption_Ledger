> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-006 / int_ad_reporting__country_mapping（全量）

## 结论

主要原因：**A**；把握：中。国家静态枚举未给完整清单；agent 单行占位与 gold 的45行枚举不同。

参与因素：无。标记：无。

## 差异与归因依据

契约指向 inline VALUES dataset in SQL，但所读契约没有国家逐行数值清单。event23只写US，event97具体说明缺少完整静态列举值。差异取决于未给定的枚举内容，不能用gold的国家人口/地区值反推必然正确值。

层：intermediate；比较库schema：intermediate；评测键：country_code, region, iso_alpha_3_code, currency_code。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:1721–1775`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__country_mapping.sql:1–1`；SHA-256 `2238a859f4954df4811789d117a29e6a674699cdd120af5688093d762f8869fa`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__country_mapping.sql:1–87`；SHA-256 `e72f30fdc6a62ccd8b7e3f9da2497f33f36ab531e1d229090b3d3fa1cb506a61`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- whole_implementation_diagnostic：替换指定完整实现块（诊断）；old/new完整字节见重跑JSON，私有SQL `data/020_work/impl-006_int_ad_reporting__country_mapping/whole_implementation_diagnostic.sql`。

## agent可见证据与不确定性

不确定性四档：**针对本表的具体说明**。

event 97：`int_ad_reporting__country_mapping` 由于契约没有给出完整静态列举值，目前为单行静态占位映射，不能代表全量国家覆盖。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | int_ad_reporting__country_mapping | False |
| 26 | 25 | int_ad_reporting__country_mapping | False |
| 48 | 47 | int_ad_reporting__country_mapping | False |
| 84 | 83 | int_ad_reporting__country_mapping | False |
| 96 | 95 | int_ad_reporting__country_mapping | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：0；核实代价档：需要查业务说明。全部连接原件read_only=True，查询只用agent当时可见库。

无数据核实查询；静态枚举问题需缺失的业务清单，来源搜索范围见归因说明。
诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=2 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_int_ad_reporting__country_mapping/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：45行 / 665格；重跑基线：45行 / 665格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:45行/665格 / L1:45行/665格 / L2:45行/665格 / L3:45行/665格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0:0行/0格 / L1:0行/0格 / L2:0行/0格 / L3:0行/0格 | L0 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"continent": 1, "gdp_per_capita_usd": 1, "internet_penetration_pct": 1, "mobile_penetration_pct": 1, "sub_region": 1} |
| whole_implementation_diagnostic | {} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

本表两种读法：已披露单行占位可读作D；契约引用的枚举表未提供可读作A。本次选A，因为缺失的是应输出的具体静态内容，不能从数据恢复gold的45行及数值；单行覆盖不足事实保留。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_int_ad_reporting__country_mapping.md`。
- 重跑：`records/020_reruns_impl-006_int_ad_reporting__country_mapping.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
