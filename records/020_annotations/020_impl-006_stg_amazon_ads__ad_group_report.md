> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-006 / stg_amazon_ads__ad_group_report（全量）

## 结论

主要原因：**C**；把握：高。未按契约删除非法 ad_group_id；同时遗漏CTR/CPC，并有策略清洗歧义。

参与因素：A：campaign_bidding_strategy（减0行/17987格）；D：click_through_rate（减0行/18347格）；D：cost_per_click（减0行/17251格）。标记：无。

## 差异与归因依据

契约明确ID正则失败delete_row。16条非法ID被agent原样保留；单修过滤减少16行，是有效契约修复中最大的行数改善。gold也把这些ID置NULL并保留行，违反delete_row；其置NULL只作诊断，不冒充C修复。campaign_bidding_strategy契约仅VARCHAR，gold额外白名单/大写化，A；CTR/CPC有可用输入却直接NULL，D。

层：staging；比较库schema：staging；评测键：ad_group_id, date_day。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:70–111`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__ad_group_report.sql:1–18`；SHA-256 `aafca6bd1117f6ec8d1d0c7f71c81a94443ff026579c90ae8d186532e6caf80d`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_amazon_ads__ad_group_report.sql:1–97`；SHA-256 `112bae7ea66f893aa7d5e242946c682667d27d03aeac4ba2080fa25db190afe4`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- campaign_bidding_strategy：
```sql
TRY_CAST("campaign_bidding_strategy" AS VARCHAR) AS campaign_bidding_strategy
```
→
```sql
CAST(CASE WHEN LOWER(TRIM(campaign_bidding_strategy)) IN ('advanced cpc', 'enhanced cpc', 'manual cpc', 'manual cpm', 'target impression share bids', 'maximize conversions', 'maximize conversion value', 'target cpa', 'target roas', 'viewable cpm', 'target cpm', 'commission', 'percent cpc') THEN UPPER(TRIM(campaign_bidding_strategy)) ELSE NULL END AS TEXT) AS campaign_bidding_strategy
```

- click_through_rate：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate
```
→
```sql
CAST(CASE WHEN impressions IS NULL OR impressions < 0 THEN 0.0 WHEN clicks IS NULL OR clicks < 0 THEN 0.0 WHEN impressions > 0 THEN ROUND((CAST(clicks AS DECIMAL(18, 3)) / CAST(impressions AS DECIMAL(18, 3))) * 100, 4) ELSE 0.0 END AS DOUBLE) AS click_through_rate
```

- cost_per_click：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click
```
→
```sql
CAST(CASE WHEN clicks IS NULL OR clicks <= 0 THEN 0.0 ELSE ROUND(ROUND(CASE WHEN cost IS NULL THEN 0.0 WHEN cost < 0 THEN 0.0 ELSE cost END, 2) / clicks, 2) END AS DOUBLE) AS cost_per_click
```

- ad_group_id_gold_diagnostic：
```sql
CAST(TRY_CAST("ad_group_id" AS VARCHAR) AS VARCHAR) AS ad_group_id
```
→
```sql
CAST(CASE WHEN TRIM(CAST(ad_group_id AS TEXT)) = '' OR ad_group_id IS NULL THEN NULL WHEN NOT REGEXP_MATCHES(TRIM(CAST(ad_group_id AS TEXT)), '^[A-Za-z0-9_-]{1,128}$') THEN NULL ELSE TRIM(CAST(ad_group_id AS TEXT)) END AS TEXT) AS ad_group_id
```

- invalid_id_contract_delete：
```sql
SELECT * FROM cleaned
```
→
```sql
SELECT * FROM cleaned WHERE ad_group_id IS NOT NULL AND TRIM(ad_group_id) != '' AND regexp_matches(ad_group_id, '^[A-Za-z0-9_-]{1,128}$')
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。 event 97（args.final_thought）：脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_amazon_ads__ad_group_report | False |
| 12 | 11 | amazon_ads_ad_group_level_report_data | False |
| 16 | 15 | amazon_ads_ad_group_level_report_data | False |
| 18 | 17 | amazon_ads_ad_group_level_report_data | False |
| 38 | 37 | stg_amazon_ads__ad_group_report | False |
| 82 | 81 | stg_amazon_ads__ad_group_report | False |
| 86 | 85 | stg_amazon_ads__ad_group_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='amazon_ads_ad_group_level_report_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "amazon_ads_ad_group_level_report_data", "ad_group_id", "VARCHAR"], ["raw", "amazon_ads_ad_group_level_report_data", "date", "VARCHAR"], ["raw", "amazon_ads_ad_group_level_report_data", "campaign_bidding_strategy", "VARCHAR"], ["raw", "amazon_ads_ad_group_level_report_data", "clicks", "BIGINT"], ["raw", "amazon_ads_ad_group_level_report_data", "cost", "DOUBLE"], ["raw", "amazon_ads_ad_group_level_report_data", "impressions", "BIGINT"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "campaign_bidding_strategy" IS NULL) AS c0_null,count(*) FILTER(WHERE "campaign_bidding_strategy" IS NOT NULL AND TRY_CAST("campaign_bidding_strategy" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "cost" IS NULL) AS c2_null,count(*) FILTER(WHERE "cost" IS NOT NULL AND TRY_CAST("cost" AS DOUBLE) IS NULL) AS c3_not_numeric FROM raw.amazon_ads_ad_group_level_report_data
```

结果：`[[17868, 0, 17868, 0, 0]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=13 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_amazon_ads__ad_group_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：17884行 / 55655格；重跑基线：17884行 / 55655格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:17884行/55655格 / L1:17884行/55649格 / L2:17884行/55649格 / L3:17884行/55649格 | 均未整表匹配 |
| campaign_bidding_strategy | L0:17884行/37668格 / L1:17884行/37683格 / L2:17884行/37683格 / L3:17884行/37683格 | 均未整表匹配 |
| click_through_rate | L0:17884行/37308格 / L1:17884行/37300格 / L2:17884行/37300格 / L3:17884行/37300格 | 均未整表匹配 |
| cost_per_click | L0:17884行/38404格 / L1:17884行/38396格 / L2:17884行/38396格 / L3:17884行/38396格 | 均未整表匹配 |
| ad_group_id_gold_diagnostic | L0:17868行/55454格 / L1:17868行/55457格 / L2:17868行/55457格 / L3:17868行/55457格 | 均未整表匹配 |
| invalid_id_contract_delete | L0:17868行/55511格 / L1:17868行/55505格 / L2:17868行/55505格 / L3:17868行/55505格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"campaign_bidding_strategy": 17852, "click_through_rate": 17852, "clicks": 601, "cost": 605, "cost_per_click": 17852, "impressions": 605} |
| campaign_bidding_strategy | {"click_through_rate": 17852, "clicks": 556, "cost": 560, "cost_per_click": 17852, "impressions": 560} |
| click_through_rate | {"campaign_bidding_strategy": 17852, "click_through_rate": 329, "clicks": 329, "cost": 329, "cost_per_click": 17852, "impressions": 329} |
| cost_per_click | {"campaign_bidding_strategy": 17852, "click_through_rate": 17852, "clicks": 601, "cost": 605, "cost_per_click": 601, "impressions": 605} |
| ad_group_id_gold_diagnostic | {"campaign_bidding_strategy": 17868, "click_through_rate": 17868, "clicks": 614, "cost": 618, "cost_per_click": 17868, "impressions": 618} |
| invalid_id_contract_delete | {"campaign_bidding_strategy": 17852, "click_through_rate": 17852, "clicks": 601, "cost": 605, "cost_per_click": 17852, "impressions": 605} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

本表agent和gold都没有执行delete_row。两种读法：用gold置NULL作为“修复”排序；或只让真正契约修复参加C排序。本次选后者，gold置NULL重跑仅诊断。gold保留非法ID为契约矛盾，不能把置NULL当正确修复。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_amazon_ads__ad_group_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_amazon_ads__ad_group_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
