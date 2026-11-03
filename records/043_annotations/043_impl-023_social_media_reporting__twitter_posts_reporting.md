# 043：impl-023_social_media_reporting__twitter_posts_reporting

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为75行/75格。行增多时即使格减少也不作为改善。

层：intermediate。024旧主要原因原样保留：`C`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/intermediate/social_media_reporting__twitter_posts_reporting.sql`；无SQL注释。材料包：`records/024_packages/024_impl-023_social_media_reporting__twitter_posts_reporting.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-023.json`；与gold关系见 `records/015_raw_impl-023.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 29,31,33，`/tmp/write_sql.py`：同一files字典脚本分三次写入staging、中间层、marts；各表表达式分别定义。 目录编号：`023-write-sql`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共0条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

## 点：created_timestamp

类别：**Intent Misreading**；角色：主要；把握：高。

契约明确取组内earliest date；实现改取tweet_created_at，改变时间值，是算法理解而非形式。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-023_social_media_reporting__twitter_posts_reporting.json`，条目 `created_timestamp`。

基线：L0=75行/75格; L1=75行/75格; L2=75行/75格; L3=75行/75格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：75行/75格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "min(tweet_created_at)",
    "new": "min(date)",
    "offset": 536
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
      source_models:
      - staging.stg_social_media__twitter_organic_tweets
      business_logic: '- Input: include only records where organic_tweet_id is present. - Grouping: aggregate by organic_tweet_id and account_id to form post-level groups. - created_timestamp: earliest date in the group; null if all dates are missing. - post_message: the lexicographically last non-null tweet_text in the group; if all are missing, result is null; original casing and whitespace are preserved. - page_name: for each row, choose the first non-blank among screen_name, user_name, then account_id as text (blank strings treated as missing); from these per-row candidates, select the lexicographically last value in the group; may be null; original casing and whitespace are preserved. - platform: set to the literal value twitter. - Metrics aggregation: clicks, impressions, likes, retweets, replies, app_clicks, url_clicks, and qualified_impressions are summed per group, ignoring missing values. If a metric has no values in a group, it remains null at this stage. - Renames: shares is the sum of retweets; comments is the sum of replies. - engagement_rate: average of engagement_rate within the group, ignoring missing values; remains null if no values exist. - Final outputs: - page_id is account_id. - post_id is the text form of organic_tweet_id. - clicks, impressions, likes, shares, comments, app_clicks, url_clicks, and qualified_impressions default to 0 when null. - engagement_rate defaults to 0.0 when null. - post_url is built as https://twitter.com/{page_name}/status/{post_id}; if page_name is null, post_url is null; no URL encoding; casing preserved. - calculated_engagement_rate: if impressions (after defaulting) is greater than 0, compute (likes + shares + comments) divided by impressions using the zero-defaulted values; otherwise return 0.0; result is floating point. - Output: one row per (account_id, organic_tweet_id).'
      columns:
      - name: page_id
        data_type: VARCHAR
        description: Twitter account_id for the group; may be null
      - name: page_name
        data_type: VARCHAR
        description: Chosen as the lexicographically last per-row candidate (screen_name, else user_name, else account_id as text); may be null
      - name: post_id
        data_type: VARCHAR
        description: Organic tweet identifier as text; not null
        tests:
        - not_null
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_social_media_reporting__twitter_posts_reporting:created_timestamp`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
