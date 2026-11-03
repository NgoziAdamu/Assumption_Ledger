# 043：impl-024_tiktok_ads__ad_report

## 结论

主要原因：**多因并列**；把握：中；只能组合修复：是。

所有逐点单改均不减少行或格，组合减少；不将零改善点记为参与因素。

层：marts。024旧主要原因原样保留：`C`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/marts/tiktok_ads__ad_report.sql`；无SQL注释。材料包：`records/024_packages/024_impl-024_tiktok_ads__ad_report.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-024.json`；与gold关系见 `records/015_raw_impl-024.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 33，`/tmp/models.py`：agg_model批量生成marts；复制source_relation联接条件到多个模型。 目录编号：`024-models`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 33，marts生成时重复附加source_relation相等联接条件。 本表点：ads_source_join；编号 `024-extra-source-joins`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共0条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 诊断 `gold连接字段非空`：`records/024_extra_diagnostics.json` 数组索引1（从0开始）。

- 诊断 `多处组合仅诊断（不用于单点原因排名）`：`records/024_extra_diagnostics.json` 数组索引21（从0开始）。

- 诊断 `gold各上游source_relation`：`records/024_diagnostics.json` 数组索引0（从0开始）。

- 诊断 `gold输出连接字段非空`：`records/024_diagnostics.json` 数组索引1（从0开始）。

- 诊断 `gold SQL同gold输入重跑`：`records/024_diagnostics.json` 数组索引28（从0开始）。

组合诊断：`records/024_extra_diagnostics.json` 索引21，只改['campaign_projection', 'ad_group_projection', 'advertiser_join', 'ads_source_join']；L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。只用于确认组合改善，不冒充任何单点的收益。

## 点：campaign_projection

类别：**Intent Misreading**；角色：组合项；把握：高。

维度属性来自最新匹配维表，缺匹配应NULL；直接投影ads外键保留孤儿值违背规定。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-024_tiktok_ads__ad_report.json`，条目 `campaign_projection`。

基线：L0=2499行/7484格; L1=2499行/7484格; L2=2499行/7484格; L3=2499行/7484格。

单改后：L0=2499行/7484格; L1=2499行/7484格; L2=2499行/7484格; L3=2499行/7484格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "ad.campaign_id,",
    "new": "c.campaign_id,",
    "offset": 173
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
      - intermediate.int_tiktok_ads__advertiser (advertiser_id, advertiser_name, currency)
      - intermediate.int_tiktok_ads__campaign_history_latest (campaign_id, campaign_name, source_relation)
      business_logic: '- Start from hourly facts; derive date_day by converting the hourly timestamp to its calendar date. - Join latest dimensions: - ads on matching ad_id - ad_groups on matching ad_group_id and source_relation - advertiser on matching advertiser_id - campaigns on matching campaign_id and source_relation - Group by source_relation, date_day, advertiser_id, advertiser_name, campaign_id, campaign_name, ad_group_id, ad_group_name, ad_id, ad_name, currency, interest_category, gender, audience_type, budget. - For each group, aggregate all hourly metrics by summing; sums ignore NULL inputs and return NULL if all inputs are NULL; no additional casting or rounding. - Compute rate metrics from the aggregated sums with zero-safe division: - daily_cpc: total spend divided by total clicks - daily_cpm: total spend divided by total impressions, scaled per 1,000 impressions - daily_ctr: total clicks divided by total impressions, expressed as a percentage If a denominator is zero or NULL, the result is NULL; no rounding is applied. - total_conversion_value is the daily sum of each hour’s (purchase value + sales lead value), equivalent to summing both components separately. - Dimension attributes come from the latest snapshots; if a joined record is missing, the attribute is NULL. All such attributes are included in the GROUP BY.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Identifier of the data source; grouping key
        tests:
        - not_null
      - name: date_day
        data_type: DATE
        description: Calendar date derived from stat_time_hour
        tests:
        - not_null
      - name: advertiser_id
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-models`；根源决定单元 `impl-024_tiktok_ads__ad_report:campaign_projection`。

## 点：ad_group_projection

类别：**Intent Misreading**；角色：组合项；把握：高。

输出ad_group维度属性应来自匹配维表；直接投影ads外键改变缺失时行为。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-024_tiktok_ads__ad_report.json`，条目 `ad_group_projection`。

基线：L0=2499行/7484格; L1=2499行/7484格; L2=2499行/7484格; L3=2499行/7484格。

单改后：L0=2499行/7484格; L1=2499行/7484格; L2=2499行/7484格; L3=2499行/7484格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "ad.ad_group_id,",
    "new": "ag.ad_group_id,",
    "offset": 222
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
      - intermediate.int_tiktok_ads__advertiser (advertiser_id, advertiser_name, currency)
      - intermediate.int_tiktok_ads__campaign_history_latest (campaign_id, campaign_name, source_relation)
      business_logic: '- Start from hourly facts; derive date_day by converting the hourly timestamp to its calendar date. - Join latest dimensions: - ads on matching ad_id - ad_groups on matching ad_group_id and source_relation - advertiser on matching advertiser_id - campaigns on matching campaign_id and source_relation - Group by source_relation, date_day, advertiser_id, advertiser_name, campaign_id, campaign_name, ad_group_id, ad_group_name, ad_id, ad_name, currency, interest_category, gender, audience_type, budget. - For each group, aggregate all hourly metrics by summing; sums ignore NULL inputs and return NULL if all inputs are NULL; no additional casting or rounding. - Compute rate metrics from the aggregated sums with zero-safe division: - daily_cpc: total spend divided by total clicks - daily_cpm: total spend divided by total impressions, scaled per 1,000 impressions - daily_ctr: total clicks divided by total impressions, expressed as a percentage If a denominator is zero or NULL, the result is NULL; no rounding is applied. - total_conversion_value is the daily sum of each hour’s (purchase value + sales lead value), equivalent to summing both components separately. - Dimension attributes come from the latest snapshots; if a joined record is missing, the attribute is NULL. All such attributes are included in the GROUP BY.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Identifier of the data source; grouping key
        tests:
        - not_null
      - name: date_day
        data_type: DATE
        description: Calendar date derived from stat_time_hour
        tests:
        - not_null
      - name: advertiser_id
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-models`；根源决定单元 `impl-024_tiktok_ads__ad_report:ad_group_projection`。

## 点：advertiser_join

类别：**Unstated Choice**；角色：组合项；把握：中。

本表仅写matching advertiser_id，没有指定从ads还是ad_groups取；不能借url_report的更具体规则推断本表。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-024_tiktok_ads__ad_report.json`，条目 `advertiser_join`。

基线：L0=2499行/7484格; L1=2499行/7484格; L2=2499行/7484格; L3=2499行/7484格。

单改后：L0=2499行/7484格; L1=2499行/7484格; L2=2499行/7484格; L3=2499行/7484格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "on ag.advertiser_id = a.advertiser_id",
    "new": "on ad.advertiser_id = a.advertiser_id",
    "offset": 1489
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
      - intermediate.int_tiktok_ads__advertiser (advertiser_id, advertiser_name, currency)
      - intermediate.int_tiktok_ads__campaign_history_latest (campaign_id, campaign_name, source_relation)
      business_logic: '- Start from hourly facts; derive date_day by converting the hourly timestamp to its calendar date. - Join latest dimensions: - ads on matching ad_id - ad_groups on matching ad_group_id and source_relation - advertiser on matching advertiser_id - campaigns on matching campaign_id and source_relation - Group by source_relation, date_day, advertiser_id, advertiser_name, campaign_id, campaign_name, ad_group_id, ad_group_name, ad_id, ad_name, currency, interest_category, gender, audience_type, budget. - For each group, aggregate all hourly metrics by summing; sums ignore NULL inputs and return NULL if all inputs are NULL; no additional casting or rounding. - Compute rate metrics from the aggregated sums with zero-safe division: - daily_cpc: total spend divided by total clicks - daily_cpm: total spend divided by total impressions, scaled per 1,000 impressions - daily_ctr: total clicks divided by total impressions, expressed as a percentage If a denominator is zero or NULL, the result is NULL; no rounding is applied. - total_conversion_value is the daily sum of each hour’s (purchase value + sales lead value), equivalent to summing both components separately. - Dimension attributes come from the latest snapshots; if a joined record is missing, the attribute is NULL. All such attributes are included in the GROUP BY.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Identifier of the data source; grouping key
        tests:
        - not_null
      - name: date_day
        data_type: DATE
        description: Calendar date derived from stat_time_hour
        tests:
        - not_null
      - name: advertiser_id
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-models`；根源决定单元 `impl-024_tiktok_ads__ad_report:advertiser_join`。

## 点：ads_source_join

类别：**Intent Misreading**；角色：组合项；把握：高。

契约首个ads联接只写ad_id，后两个联接明确另列source_relation；统一补source条件改变给定联接。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-024_tiktok_ads__ad_report.json`，条目 `ads_source_join`。

基线：L0=2499行/7484格; L1=2499行/7484格; L2=2499行/7484格; L3=2499行/7484格。

单改后：L0=2499行/9983格; L1=2499行/9983格; L2=2499行/9983格; L3=2499行/9983格。L0减量（先行后格）：0行/-2499格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": " and h.source_relation = ad.source_relation",
    "new": "",
    "offset": 1242
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
      - intermediate.int_tiktok_ads__advertiser (advertiser_id, advertiser_name, currency)
      - intermediate.int_tiktok_ads__campaign_history_latest (campaign_id, campaign_name, source_relation)
      business_logic: '- Start from hourly facts; derive date_day by converting the hourly timestamp to its calendar date. - Join latest dimensions: - ads on matching ad_id - ad_groups on matching ad_group_id and source_relation - advertiser on matching advertiser_id - campaigns on matching campaign_id and source_relation - Group by source_relation, date_day, advertiser_id, advertiser_name, campaign_id, campaign_name, ad_group_id, ad_group_name, ad_id, ad_name, currency, interest_category, gender, audience_type, budget. - For each group, aggregate all hourly metrics by summing; sums ignore NULL inputs and return NULL if all inputs are NULL; no additional casting or rounding. - Compute rate metrics from the aggregated sums with zero-safe division: - daily_cpc: total spend divided by total clicks - daily_cpm: total spend divided by total impressions, scaled per 1,000 impressions - daily_ctr: total clicks divided by total impressions, expressed as a percentage If a denominator is zero or NULL, the result is NULL; no rounding is applied. - total_conversion_value is the daily sum of each hour’s (purchase value + sales lead value), equivalent to summing both components separately. - Dimension attributes come from the latest snapshots; if a joined record is missing, the attribute is NULL. All such attributes are included in the GROUP BY.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Identifier of the data source; grouping key
        tests:
        - not_null
      - name: date_day
        data_type: DATE
        description: Calendar date derived from stat_time_hour
        tests:
        - not_null
      - name: advertiser_id
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-models`；根源决定单元 `024-extra-source-joins`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
