# 043：impl-024_tiktok_ads__url_report

## 结论

主要原因：**Intent Misreading**；把握：中；只能组合修复：是。

所有逐点单改均不减少行或格，组合减少；不将零改善点记为参与因素。

层：marts。024旧主要原因原样保留：`C`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/marts/tiktok_ads__url_report.sql`；无SQL注释。材料包：`records/024_packages/024_impl-024_tiktok_ads__url_report.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-024.json`；与gold关系见 `records/015_raw_impl-024.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 33，`/tmp/models.py`：agg_model批量生成marts；复制source_relation联接条件到多个模型。 目录编号：`024-models`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 33，marts生成时重复附加source_relation相等联接条件。 本表点：adgroup_source_join, campaign_source_join, ads_source_join；编号 `024-extra-source-joins`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共0条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 诊断 `gold连接字段非空`：`records/024_extra_diagnostics.json` 数组索引2（从0开始）。

- 诊断 `多处组合仅诊断（不用于单点原因排名）`：`records/024_extra_diagnostics.json` 数组索引22（从0开始）。

- 诊断 `gold各上游source_relation`：`records/024_diagnostics.json` 数组索引2（从0开始）。

- 诊断 `gold输出连接字段非空`：`records/024_diagnostics.json` 数组索引3（从0开始）。

- 诊断 `gold SQL同gold输入重跑`：`records/024_diagnostics.json` 数组索引29（从0开始）。

组合诊断：`records/024_extra_diagnostics.json` 索引22，只改['adgroup_source_join', 'campaign_source_join', 'ads_source_join']；L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。只用于确认组合改善，不冒充任何单点的收益。

## 点：adgroup_source_join

类别：**Intent Misreading**；角色：组合项；把握：高。

契约列出ads.ad_group_id对应维表，未要求附加source_relation；附加条件使CS中来源名不同的维度无法匹配。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-024_tiktok_ads__url_report.json`，条目 `adgroup_source_join`。

基线：L0=2499行/109956格; L1=2499行/109956格; L2=2499行/109956格; L3=2499行/109956格。

单改后：L0=2499行/109956格; L1=2499行/109956格; L2=2499行/109956格; L3=2499行/109956格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": " and ad.source_relation = ag.source_relation",
    "new": "",
    "offset": 1567
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
      - intermediate.int_tiktok_ads__advertiser
      - intermediate.int_tiktok_ads__campaign_history_latest
      business_logic: '1) Start from intermediate.int_tiktok_ads__ad_report_hourly (hourly). 2) Left join latest dimension snapshots: - hourly.ad_id → intermediate.int_tiktok_ads__ad_history_latest (ads) - ads.ad_group_id → intermediate.int_tiktok_ads__ad_group_history_latest (ad_groups) - ads.advertiser_id → intermediate.int_tiktok_ads__advertiser (advertiser) - ads.campaign_id → intermediate.int_tiktok_ads__campaign_history_latest (campaigns) 3) Keep only rows where ads.landing_page_url is present (non-null). 4) Derive date_day by casting hourly.stat_time_hour to a date (no timezone adjustments). 5) Group by all selected dimensions: source_relation, date_day, advertiser_id/name, campaign_id/name, ad_group_id/name, ad_id, ad_name, base_url, url_host, url_path, utm_source/medium/campaign/content/term, currency, interest_category, gender, audience_type, budget. 6) For each group, add up all hourly numeric metrics; null inputs are ignored in the addition, and if all inputs are null the result is null. For total_conversion_value, first compute purchase value plus sales lead value per row, then add those row results across the group; if either component is missing on a row, that row contributes nothing. 7) Compute rate metrics from the aggregated totals: - daily_cpc: total spend divided by total clicks; if total clicks is zero or null, return null; no rounding. - daily_cpm: total spend divided by total impressions, multiplied by 1000; if total impressions is zero or null, return null; no rounding. - daily_ctr: total clicks divided by total impressions, multiplied by 100; if total impressions is zero or null, return null; no rounding. 8) URL and UTM fields are taken directly from ads without parsing, normalization, trimming, or case changes. 9) Context fields (currency, interest_category, gender, audience_type, budget) are grouping keys; differences create separate rows.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Source relation identifier from hourly input; included in the grouping key
      - name: date_day
        data_type: DATE
        description: Date derived by casting stat_time_hour to date; part of the grouping key
      - name: advertiser_id
        data_type: VARCHAR
        description: Advertiser ID from ad_groups; may be NULL if ad_group not found; part of the grouping key
      - name: advertiser_name
        data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-models`；根源决定单元 `024-extra-source-joins`。

## 点：campaign_source_join

类别：**Intent Misreading**；角色：组合项；把握：高。

契约明确ads.campaign_id对应维表；额外source_relation条件改变规则。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-024_tiktok_ads__url_report.json`，条目 `campaign_source_join`。

基线：L0=2499行/109956格; L1=2499行/109956格; L2=2499行/109956格; L3=2499行/109956格。

单改后：L0=2499行/109956格; L1=2499行/109956格; L2=2499行/109956格; L3=2499行/109956格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": " and ad.source_relation = c.source_relation",
    "new": "",
    "offset": 1806
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
      - intermediate.int_tiktok_ads__advertiser
      - intermediate.int_tiktok_ads__campaign_history_latest
      business_logic: '1) Start from intermediate.int_tiktok_ads__ad_report_hourly (hourly). 2) Left join latest dimension snapshots: - hourly.ad_id → intermediate.int_tiktok_ads__ad_history_latest (ads) - ads.ad_group_id → intermediate.int_tiktok_ads__ad_group_history_latest (ad_groups) - ads.advertiser_id → intermediate.int_tiktok_ads__advertiser (advertiser) - ads.campaign_id → intermediate.int_tiktok_ads__campaign_history_latest (campaigns) 3) Keep only rows where ads.landing_page_url is present (non-null). 4) Derive date_day by casting hourly.stat_time_hour to a date (no timezone adjustments). 5) Group by all selected dimensions: source_relation, date_day, advertiser_id/name, campaign_id/name, ad_group_id/name, ad_id, ad_name, base_url, url_host, url_path, utm_source/medium/campaign/content/term, currency, interest_category, gender, audience_type, budget. 6) For each group, add up all hourly numeric metrics; null inputs are ignored in the addition, and if all inputs are null the result is null. For total_conversion_value, first compute purchase value plus sales lead value per row, then add those row results across the group; if either component is missing on a row, that row contributes nothing. 7) Compute rate metrics from the aggregated totals: - daily_cpc: total spend divided by total clicks; if total clicks is zero or null, return null; no rounding. - daily_cpm: total spend divided by total impressions, multiplied by 1000; if total impressions is zero or null, return null; no rounding. - daily_ctr: total clicks divided by total impressions, multiplied by 100; if total impressions is zero or null, return null; no rounding. 8) URL and UTM fields are taken directly from ads without parsing, normalization, trimming, or case changes. 9) Context fields (currency, interest_category, gender, audience_type, budget) are grouping keys; differences create separate rows.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Source relation identifier from hourly input; included in the grouping key
      - name: date_day
        data_type: DATE
        description: Date derived by casting stat_time_hour to date; part of the grouping key
      - name: advertiser_id
        data_type: VARCHAR
        description: Advertiser ID from ad_groups; may be NULL if ad_group not found; part of the grouping key
      - name: advertiser_name
        data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-models`；根源决定单元 `024-extra-source-joins`。

## 点：ads_source_join

类别：**Intent Misreading**；角色：组合项；把握：高。

契约明确hourly.ad_id对应ads；额外source_relation条件改变规则。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-024_tiktok_ads__url_report.json`，条目 `ads_source_join`。

基线：L0=2499行/109956格; L1=2499行/109956格; L2=2499行/109956格; L3=2499行/109956格。

单改后：L0=4998行/219912格; L1=4998行/219912格; L2=4998行/219912格; L3=4998行/219912格。L0减量（先行后格）：-2499行/-109956格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": " and h.source_relation = ad.source_relation",
    "new": "",
    "offset": 1420
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
      - intermediate.int_tiktok_ads__advertiser
      - intermediate.int_tiktok_ads__campaign_history_latest
      business_logic: '1) Start from intermediate.int_tiktok_ads__ad_report_hourly (hourly). 2) Left join latest dimension snapshots: - hourly.ad_id → intermediate.int_tiktok_ads__ad_history_latest (ads) - ads.ad_group_id → intermediate.int_tiktok_ads__ad_group_history_latest (ad_groups) - ads.advertiser_id → intermediate.int_tiktok_ads__advertiser (advertiser) - ads.campaign_id → intermediate.int_tiktok_ads__campaign_history_latest (campaigns) 3) Keep only rows where ads.landing_page_url is present (non-null). 4) Derive date_day by casting hourly.stat_time_hour to a date (no timezone adjustments). 5) Group by all selected dimensions: source_relation, date_day, advertiser_id/name, campaign_id/name, ad_group_id/name, ad_id, ad_name, base_url, url_host, url_path, utm_source/medium/campaign/content/term, currency, interest_category, gender, audience_type, budget. 6) For each group, add up all hourly numeric metrics; null inputs are ignored in the addition, and if all inputs are null the result is null. For total_conversion_value, first compute purchase value plus sales lead value per row, then add those row results across the group; if either component is missing on a row, that row contributes nothing. 7) Compute rate metrics from the aggregated totals: - daily_cpc: total spend divided by total clicks; if total clicks is zero or null, return null; no rounding. - daily_cpm: total spend divided by total impressions, multiplied by 1000; if total impressions is zero or null, return null; no rounding. - daily_ctr: total clicks divided by total impressions, multiplied by 100; if total impressions is zero or null, return null; no rounding. 8) URL and UTM fields are taken directly from ads without parsing, normalization, trimming, or case changes. 9) Context fields (currency, interest_category, gender, audience_type, budget) are grouping keys; differences create separate rows.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Source relation identifier from hourly input; included in the grouping key
      - name: date_day
        data_type: DATE
        description: Date derived by casting stat_time_hour to date; part of the grouping key
      - name: advertiser_id
        data_type: VARCHAR
        description: Advertiser ID from ad_groups; may be NULL if ad_group not found; part of the grouping key
      - name: advertiser_name
        data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-models`；根源决定单元 `024-extra-source-joins`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
