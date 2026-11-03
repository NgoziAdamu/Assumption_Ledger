# 043：impl-026_twitter_ads__url_report

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为8行/8格。行增多时即使格减少也不作为改善。

层：marts。024旧主要原因原样保留：`C`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/marts/twitter_ads__url_report.sql`；无SQL注释。材料包：`records/024_packages/024_impl-026_twitter_ads__url_report.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-026.json`；与gold关系见 `records/015_raw_impl-026.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 13,17,19，`/tmp/gen.py`：report辅助函数批量生成report staging；同一脚本追加agg_model和marts，keyword在event21修正。 目录编号：`026-gen`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 19，两个marts维度投影都取li.campaign_id而非已匹配campaigns的campaign_id。 本表点：campaign_projection；编号 `026-mart-campaign-projection`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共0条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

## 点：campaign_projection

类别：**Intent Misreading**；角色：主要；把握：高。

契约明确campaign_id来自campaigns，agent取line_items的外键，缺维度时结果不同。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-026_twitter_ads__url_report.json`，条目 `campaign_projection`。

基线：L0=8行/8格; L1=8行/8格; L2=8行/8格; L3=8行/8格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：8行/8格。

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
    - name: twitter_ads__url_report
      description: Daily placement-level metrics for promoted tweets that have a first expanded URL, enriched with URL components and campaign/account/tweet attributes; metrics are summed across the grouped dimensions.
      grain: One row per unique combination of date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, base_url, url_host, url_path, utm_source, utm_medium, utm_campaign, utm_content, utm_term, expanded_url, display_url, currency
      source_models:
      - intermediate.int_twitter_ads__promoted_tweet_report_base
      - intermediate.int_twitter_ads__promoted_tweets
      - intermediate.int_twitter_ads__tweets
      - intermediate.int_twitter_ads__tweet_url_first
      - intermediate.int_twitter_ads__line_items
      - intermediate.int_twitter_ads__campaigns
      - intermediate.int_twitter_ads__accounts
      business_logic: '- Start from intermediate.int_twitter_ads__promoted_tweet_report_base r (daily metrics by placement). - Join dimensions (LEFT JOINs in the query): • r.promoted_tweet_id → intermediate.int_twitter_ads__promoted_tweets pt • pt.tweet_id → intermediate.int_twitter_ads__tweets t • pt.tweet_id → intermediate.int_twitter_ads__tweet_url_first u (first URL per tweet) • pt.line_item_id → intermediate.int_twitter_ads__line_items li • li.campaign_id → intermediate.int_twitter_ads__campaigns c • r.account_id → intermediate.int_twitter_ads__accounts a - Apply filter: require u.expanded_url to be non-NULL, which effectively makes the join to u (and thus to pt) act as an inner join; other joins remain left and may yield NULL attributes. - Group by all selected dimensions exactly: date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, base_url, url_host, url_path, utm_source, utm_medium, utm_campaign, utm_content, utm_term, expanded_url, display_url, currency. - Aggregate using SUM over r.clicks, r.impressions, r.spend, r.spend_micro, r.url_clicks, r.total_conversions, r.total_conversions_sale_amount. • SUM ignores NULL inputs; if all values in a group are NULL, the result is NULL. • No rounding or unit conversion is applied; spend is in currency units and spend_micro in micro-units of the same currency. - No de-duplication is performed; multiple matches on joins replicate metric rows and are then aggregated within identical dimension sets.'
      columns:
      - name: date_day
        data_type: DATE
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `026-gen`；根源决定单元 `026-mart-campaign-projection`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
