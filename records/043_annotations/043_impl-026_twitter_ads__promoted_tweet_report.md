# 043：impl-026_twitter_ads__promoted_tweet_report

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为2012行/2012格。行增多时即使格减少也不作为改善。

层：marts。024旧主要原因原样保留：`C`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/marts/twitter_ads__promoted_tweet_report.sql`；无SQL注释。材料包：`records/024_packages/024_impl-026_twitter_ads__promoted_tweet_report.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-026.json`；与gold关系见 `records/015_raw_impl-026.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 13,17,19，`/tmp/gen.py`：report辅助函数批量生成report staging；同一脚本追加agg_model和marts，keyword在event21修正。 目录编号：`026-gen`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 19，两个marts维度投影都取li.campaign_id而非已匹配campaigns的campaign_id。 本表点：campaign_projection；编号 `026-mart-campaign-projection`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共0条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

## 点：currency_source

类别：**Intent Misreading**；角色：主要；把握：高。

currency的来源明确是campaigns，agent改取line_items。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-026_twitter_ads__promoted_tweet_report.json`，条目 `currency_source`。

基线：L0=2032行/2532格; L1=2032行/2532格; L2=2032行/2532格; L3=2032行/2532格。

单改后：L0=20行/520格; L1=20行/520格; L2=20行/520格; L3=20行/520格。L0减量（先行后格）：2012行/2012格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "li.currency",
    "new": "c.currency",
    "offset": 202
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
    - name: twitter_ads__promoted_tweet_report
      description: Daily promoted tweet performance aggregated by placement and enriched with tweet, line item, campaign, and account attributes via left joins.
      grain: One row per unique combination of date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, currency, is_deleted, promoted_tweet_status, campaign_status, line_item_status, approval_status, created_timestamp, updated_timestamp
      source_models:
      - intermediate.int_twitter_ads__promoted_tweet_report_base
      - intermediate.int_twitter_ads__promoted_tweets
      - intermediate.int_twitter_ads__tweets
      - intermediate.int_twitter_ads__line_items
      - intermediate.int_twitter_ads__campaigns
      - intermediate.int_twitter_ads__accounts
      business_logic: '- Start from the daily promoted tweet metrics base. - Left join promoted tweets by promoted_tweet_id. - Left join tweets by tweet_id from promoted tweets. - Left join line items by line_item_id from promoted tweets. - Left join campaigns by campaign_id from line items. - Left join accounts by account_id from the base. - Aggregate by these attributes: date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, currency, is_deleted, promoted_tweet_status, campaign_status, line_item_status, approval_status, created_timestamp, updated_timestamp. - For clicks, impressions, spend, spend_micro, url_clicks, total_conversions, and total_conversions_sale_amount: sum base values within each group; NULL inputs are ignored and a group of all NULLs yields NULL; numeric types are preserved with no rounding. - Left join behavior: if no match, the joined attributes are NULL; if multiple matches occur in a joined table, base rows are duplicated before aggregation, increasing summed metrics. - No explicit ordering is applied to the result.'
      columns:
      - name: date_day
        data_type: DATE
        description: Calendar date from the base metrics; grouping key.
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `026-gen`；根源决定单元 `impl-026_twitter_ads__promoted_tweet_report:currency_source`。

## 点：campaign_projection

类别：**Intent Misreading**；角色：参与；把握：高。

campaign_id应来自匹配后的campaigns；直接用line_items外键保留了无对应维度的值。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_supplement_reruns_impl-026_twitter_ads__promoted_tweet_report.json`，条目 `campaign_projection`。

基线：L0=2032行/2532格; L1=2032行/2532格; L2=2032行/2532格; L3=2032行/2532格。

单改后：L0=2022行/2022格; L1=2022行/2022格; L2=2022行/2022格; L3=2022行/2022格。L0减量（先行后格）：10行/510格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "a.account_name, li.campaign_id",
    "new": "a.account_name, c.campaign_id",
    "offset": 50
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
    - name: twitter_ads__promoted_tweet_report
      description: Daily promoted tweet performance aggregated by placement and enriched with tweet, line item, campaign, and account attributes via left joins.
      grain: One row per unique combination of date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, currency, is_deleted, promoted_tweet_status, campaign_status, line_item_status, approval_status, created_timestamp, updated_timestamp
      source_models:
      - intermediate.int_twitter_ads__promoted_tweet_report_base
      - intermediate.int_twitter_ads__promoted_tweets
      - intermediate.int_twitter_ads__tweets
      - intermediate.int_twitter_ads__line_items
      - intermediate.int_twitter_ads__campaigns
      - intermediate.int_twitter_ads__accounts
      business_logic: '- Start from the daily promoted tweet metrics base. - Left join promoted tweets by promoted_tweet_id. - Left join tweets by tweet_id from promoted tweets. - Left join line items by line_item_id from promoted tweets. - Left join campaigns by campaign_id from line items. - Left join accounts by account_id from the base. - Aggregate by these attributes: date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, currency, is_deleted, promoted_tweet_status, campaign_status, line_item_status, approval_status, created_timestamp, updated_timestamp. - For clicks, impressions, spend, spend_micro, url_clicks, total_conversions, and total_conversions_sale_amount: sum base values within each group; NULL inputs are ignored and a group of all NULLs yields NULL; numeric types are preserved with no rounding. - Left join behavior: if no match, the joined attributes are NULL; if multiple matches occur in a joined table, base rows are duplicated before aggregation, increasing summed metrics. - No explicit ordering is applied to the result.'
      columns:
      - name: date_day
        data_type: DATE
        description: Calendar date from the base metrics; grouping key.
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `026-gen`；根源决定单元 `026-mart-campaign-projection`。

## 点：line_item_projection

类别：**Intent Misreading**；角色：非原因；把握：高。

line_item_id应来自匹配line_items，直接用promoted_tweets外键；单改不改善。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_supplement_reruns_impl-026_twitter_ads__promoted_tweet_report.json`，条目 `line_item_projection`。

基线：L0=2032行/2532格; L1=2032行/2532格; L2=2032行/2532格; L3=2032行/2532格。

单改后：L0=2032行/2532格; L1=2032行/2532格; L2=2032行/2532格; L3=2032行/2532格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "c.campaign_name, pt.line_item_id",
    "new": "c.campaign_name, li.line_item_id",
    "offset": 82
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
    - name: twitter_ads__promoted_tweet_report
      description: Daily promoted tweet performance aggregated by placement and enriched with tweet, line item, campaign, and account attributes via left joins.
      grain: One row per unique combination of date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, currency, is_deleted, promoted_tweet_status, campaign_status, line_item_status, approval_status, created_timestamp, updated_timestamp
      source_models:
      - intermediate.int_twitter_ads__promoted_tweet_report_base
      - intermediate.int_twitter_ads__promoted_tweets
      - intermediate.int_twitter_ads__tweets
      - intermediate.int_twitter_ads__line_items
      - intermediate.int_twitter_ads__campaigns
      - intermediate.int_twitter_ads__accounts
      business_logic: '- Start from the daily promoted tweet metrics base. - Left join promoted tweets by promoted_tweet_id. - Left join tweets by tweet_id from promoted tweets. - Left join line items by line_item_id from promoted tweets. - Left join campaigns by campaign_id from line items. - Left join accounts by account_id from the base. - Aggregate by these attributes: date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, currency, is_deleted, promoted_tweet_status, campaign_status, line_item_status, approval_status, created_timestamp, updated_timestamp. - For clicks, impressions, spend, spend_micro, url_clicks, total_conversions, and total_conversions_sale_amount: sum base values within each group; NULL inputs are ignored and a group of all NULLs yields NULL; numeric types are preserved with no rounding. - Left join behavior: if no match, the joined attributes are NULL; if multiple matches occur in a joined table, base rows are duplicated before aggregation, increasing summed metrics. - No explicit ordering is applied to the result.'
      columns:
      - name: date_day
        data_type: DATE
        description: Calendar date from the base metrics; grouping key.
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `026-gen`；根源决定单元 `impl-026_twitter_ads__promoted_tweet_report:line_item_projection`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
