# 040 校准：impl-005_stg_google_ads__ad_group_stats

## 任务

按冻结v3.2第3～8节盲标；层：staging。本说明来自封存结果，没有用036改写结论。

## 结论

主要原因：**Unstated Choice**；把握高；共4点；不是只能组合修复。

## 详细发现

### 判断顺序与范围

先检查契约、交付SQL及单改结果，排除代码意图错误、raw版本差异及gold与契约不一致。未采用领域惯例补出未写明的规则。主因按L0含评测键全表行规模优先、格子规模次之；L1～L3仅辅助定位，不跨口径排序。

### campaign_id源列选择

主要；**Unstated Choice**；把握高。

契约仅规定campaign_id的类型和非空，未指定源列。014 V1两列9985/10000不同；016 V1两列均10000/10000匹配campaign history，V2匹配ad-group父键分别11/10000、14/10000，不能定下唯一映射；差异取决于材料没定的选择。不能据gold选列判Data Misconception。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。交付报告和交付SQL未针对campaign映射说明；event 14看到两列，event 15直接选用base列，未见比较或疑问。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 19985 | 10000 | 239672 | 21395 |
| L1 | 19985 | 9999 | 239655 | 9999 |
| L2 | 19970 | 0 | 239640 | 0 |
| L3 | 19970 | 0 | 239640 | 0 |



单改来源：`records/022_reruns_impl-005_stg_google_ads__ad_group_stats.json` / `campaign_column`。L0减少9985行、218277格；不同单改收益不相加。

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/14.json` / `content` / event 14

```text

('campaign_base_campaign', 'VARCHAR', 'YES', None, None, None), ('campaign_id', 'VARCHAR', 'YES', None, None, None)

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql` / `text`

```text

CAST(campaign_base_campaign AS VARCHAR(20)) campaign_id

```

核实证据：`records/014_queries_impl-005.json#V1`；`records/016_queries_impl-005.json#V1`；`records/016_queries_impl-005.json#V2`。

### spend两位小数

参与；**其他**；把握高。

契约明确要求DECIMAL(15,2)，agent遵从；gold采用DOUBLE。spend有舍入数值差异，另两列主要为类型文本表示差异。均属于gold与契约类型不一致，不归Form Mismatch。单改行数不降但格子数减少，计参与因素。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。交付报告未针对本处精度说明；event 1直接提供类型规定，执行代码遵从该规定；不把写出CAST本身视为意识到差异。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 19985 | 19985 | 239672 | 239657 |
| L1 | 19985 | 19970 | 239655 | 239640 |
| L2 | 19970 | 19970 | 239640 | 239640 |
| L3 | 19970 | 19970 | 239640 | 239640 |



单改来源：`records/022_calibration_supplement_reruns_impl-005_stg_google_ads__ad_group_stats.json` / `spend`。L0减少0行、15格；不同单改收益不相加。

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json` / `message` / event 1

```text

- name: spend
          data_type: DECIMAL(15,2)

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql` / `text`

```text

CAST(cost_micros / 1000000.0 AS DECIMAL(15,2)) spend

```

### conversions类型表示

参与；**其他**；把握高。

契约明确要求DECIMAL(10,2)，agent遵从；gold采用DOUBLE。spend有舍入数值差异，另两列主要为类型文本表示差异。均属于gold与契约类型不一致，不归Form Mismatch。单改行数不降但格子数减少，计参与因素。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。交付报告未针对本处精度说明；event 1直接提供类型规定，执行代码遵从该规定；不把写出CAST本身视为意识到差异。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 19985 | 19985 | 239672 | 239657 |
| L1 | 19985 | 19985 | 239655 | 239655 |
| L2 | 19970 | 19970 | 239640 | 239640 |
| L3 | 19970 | 19970 | 239640 | 239640 |



单改来源：`records/022_calibration_supplement_reruns_impl-005_stg_google_ads__ad_group_stats.json` / `conversions`。L0减少0行、15格；不同单改收益不相加。

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json` / `message` / event 1

```text

- name: conversions
          data_type: DECIMAL(10,2)

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql` / `text`

```text

CAST(conversions AS DECIMAL(10,2)) conversions

```

### conversions_value类型表示

参与；**其他**；把握高。

契约明确要求DECIMAL(15,2)，agent遵从；gold采用DOUBLE。spend有舍入数值差异，另两列主要为类型文本表示差异。均属于gold与契约类型不一致，不归Form Mismatch。单改行数不降但格子数减少，计参与因素。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。交付报告未针对本处精度说明；event 1直接提供类型规定，执行代码遵从该规定；不把写出CAST本身视为意识到差异。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 19985 | 19985 | 239672 | 239670 |
| L1 | 19985 | 19985 | 239655 | 239655 |
| L2 | 19970 | 19970 | 239640 | 239640 |
| L3 | 19970 | 19970 | 239640 | 239640 |



单改来源：`records/022_calibration_supplement_reruns_impl-005_stg_google_ads__ad_group_stats.json` / `conversion_value`。L0减少0行、2格；不同单改收益不相加。

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json` / `message` / event 1

```text

- name: conversions_value
          data_type: DECIMAL(15,2)

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql` / `text`

```text

CAST(conversions_value AS DECIMAL(15,2)) conversions_value

```

### 契约依据

完整契约原文已在`records/012_packages/012_impl-005_staging_stg_google_ads__ad_group_stats.json`核对到`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`；SHA-256 `cab7283dc557ddcb42fcdbec4342ce63504f8e9e4aee0cc3d38c262e5387c693`。

契约campaign_id只有VARCHAR(20)和not_null，没有源列映射；spend/conversions/conversions_value分别规定DECIMAL(15,2)、DECIMAL(10,2)、DECIMAL(15,2)。

## 证据来源

- 材料包：`records/012_packages/012_impl-005_staging_stg_google_ads__ad_group_stats.json`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`；SHA-256 `35b7d35bac34f4628dd8b6db13330fb6947104ba63011b39e922026d5279166d`。

- `records/040_calibration_blind_sealed.json`、`records/040_calibration_comparison.json`、`records/040_checks/quote_checks.json`。

- Google Ads复用014 V1及016 V1/V2共3条；Xero实际证据用017 V2，保守把已读V1失败也算入为2条。封存件verification_query_count记录成功采用数，原件不改。

- 本阶段没有新执行数据库查询或重跑；Google Ads复用022的agent留存raw，Xero复用CS gold上游；执行路径与clock_control见各重跑JSON。

## 不确定或没查到的（含规则问题）

- 未发现需要修改手册的规则问题；没有因为gold结果不同而补出唯一业务规则。

- 036只列Google Ads的campaign主因点，未列三项类型参与；本次保留独立单改减少格子的三项，校准一致率只按两个对应点计算。

## 建议的下一步

保留该校准结果和封存hash，在同一会话继续38张正式表；不把本阶段2张校准误作40张完成。
