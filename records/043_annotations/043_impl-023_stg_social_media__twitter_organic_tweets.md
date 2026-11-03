# 043：impl-023_stg_social_media__twitter_organic_tweets

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为258行/7740格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`O`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__twitter_organic_tweets.sql`；无SQL注释。材料包：`records/024_packages/024_impl-023_stg_social_media__twitter_organic_tweets.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-023.json`；与gold关系见 `records/015_raw_impl-023.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.organic_tweet_report`：initial 2500行/30列；agent留存 2500行/30列；013差异=False。

- `raw.tweet`：initial 2500行/10列；agent留存 2500行/10列；013差异=False。

- `raw.twitter_user_history`：initial 2500行/31列；agent留存 2500行/31列；013差异=False。

## 同源决定

同源决定：event 29,31,33，`/tmp/write_sql.py`：同一files字典脚本分三次写入staging、中间层、marts；各表表达式分别定义。 目录编号：`023-write-sql`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共2条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引4（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `tweet关联/账户与用户ID差异`：`records/024_queries.json` 数组索引5（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 诊断 `agent实际类型`：`records/024_diagnostics.json` 数组索引4（从0开始）。

- 诊断 `agent有限差异样例`：`records/024_diagnostics.json` 数组索引5（从0开始）。

- 诊断 `gold实际类型`：`records/024_diagnostics.json` 数组索引6（从0开始）。

- 诊断 `gold有限差异样例`：`records/024_diagnostics.json` 数组索引7（从0开始）。

涉及运行时间的基线与单改沿用同一固定时刻：`[{"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-17'", "count": 1}]`；完整控制记录见复用重跑JSON。

## 点：tweet_join_account

类别：**Unstated Choice**；角色：非原因；把握：中。

契约未指定完整联接条件；是否附带account_id限制未定，单改未改善。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__twitter_organic_tweets.json`，条目 `tweet_join_account`。

基线：L0=258行/7740格; L1=258行/7740格; L2=258行/7740格; L3=258行/7740格。

单改后：L0=258行/7740格; L1=258行/7740格; L2=258行/7740格; L3=258行/7740格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "t.tweet_id\n",
    "new": "t.tweet_id and o.account_id = (select any_value(account_id) from raw.tweet tx where try_cast(tx.id as bigint)=t.tweet_id)\n",
    "offset": 2640
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
    - name: stg_social_media__twitter_organic_tweets
      description: "Tweet-level organic performance records enriched with tweet text and user attributes; recent 2-year window."
      source_table: raw.organic_tweet_report
      notes:
        - "Rows restricted to last 2 years via: date >= CURRENT_DATE - INTERVAL '2 years'."
        - "Tweet text joined from raw.tweet.full_text; user attributes joined from raw.twitter_user_history."
        - "All metrics default to 0 when NULL."
        - "engagement_rate guarded against division by zero."
      columns:
        - name: account_id
          data_type: VARCHAR
        - name: date
          data_type: DATE
        - name: organic_tweet_id
          data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_organic_tweets:tweet_join_account`。

## 点：user_join_source

类别：**Unstated Choice**；角色：非原因；把握：中。

source列表不足以确定由account_id还是tweet.user_id关联用户，现有核实未证明唯一正确对应；保留Choice。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__twitter_organic_tweets.json`，条目 `user_join_source`。

基线：L0=258行/7740格; L1=258行/7740格; L2=258行/7740格; L3=258行/7740格。

单改后：L0=258行/7740格; L1=258行/7740格; L2=258行/7740格; L3=258行/7740格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "u.id = o.account_id",
    "new": "u.id = (select any_value(user_id) from raw.tweet tx where try_cast(tx.id as bigint)=t.tweet_id)",
    "offset": 2672
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
    - name: stg_social_media__twitter_organic_tweets
      description: "Tweet-level organic performance records enriched with tweet text and user attributes; recent 2-year window."
      source_table: raw.organic_tweet_report
      notes:
        - "Rows restricted to last 2 years via: date >= CURRENT_DATE - INTERVAL '2 years'."
        - "Tweet text joined from raw.tweet.full_text; user attributes joined from raw.twitter_user_history."
        - "All metrics default to 0 when NULL."
        - "engagement_rate guarded against division by zero."
      columns:
        - name: account_id
          data_type: VARCHAR
        - name: date
          data_type: DATE
        - name: organic_tweet_id
          data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_organic_tweets:user_join_source`。

## 点：user_latest

类别：**Unstated Choice**；角色：非原因；把握：中。

契约没有明确用户历史版本选择算法；去掉latest限定单改不改善。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__twitter_organic_tweets.json`，条目 `user_latest`。

基线：L0=258行/7740格; L1=258行/7740格; L2=258行/7740格; L3=258行/7740格。

单改后：L0=258行/7740格; L1=258行/7740格; L2=258行/7740格; L3=258行/7740格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": " and u.row_num = 1",
    "new": "",
    "offset": 2691
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
    - name: stg_social_media__twitter_organic_tweets
      description: "Tweet-level organic performance records enriched with tweet text and user attributes; recent 2-year window."
      source_table: raw.organic_tweet_report
      notes:
        - "Rows restricted to last 2 years via: date >= CURRENT_DATE - INTERVAL '2 years'."
        - "Tweet text joined from raw.tweet.full_text; user attributes joined from raw.twitter_user_history."
        - "All metrics default to 0 when NULL."
        - "engagement_rate guarded against division by zero."
      columns:
        - name: account_id
          data_type: VARCHAR
        - name: date
          data_type: DATE
        - name: organic_tweet_id
          data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_organic_tweets:user_latest`。

## 点：screen_clean

类别：**Unstated Choice**；角色：非原因；把握：中。

此表未给screen_name清洗表达式，不能借另一张user_history契约推广到本表。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__twitter_organic_tweets.json`，条目 `screen_clean`。

基线：L0=258行/7740格; L1=258行/7740格; L2=258行/7740格; L3=258行/7740格。

单改后：L0=258行/7740格; L1=258行/7740格; L2=258行/7740格; L3=258行/7740格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "regexp_replace(u.screen_name, '[^A-Za-z0-9_]', '', 'g')",
    "new": "u.screen_name",
    "offset": 2221
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
          data_type: VARCHAR
          description: "From raw.tweet.full_text."
        - name: screen_name
          data_type: VARCHAR
          description: "From raw.twitter_user_history.screen_name."
        - name: user_name
          data_type: VARCHAR
          description: "From raw.twitter_user_history.name."
        - name: lang
          data_type: VARCHAR
          description: "From raw.tweet.lang."
        - name: tweet_created_at
          data_type: TIMESTAMP
          description: "From raw.tweet.created_at."
        - name: engagement_rate
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_organic_tweets:screen_clean`。

## 点：date_projection

类别：**其他**；角色：主要；把握：高。

本表契约date为DATE，agent据此截为日；gold保留时刻且date在评测键中，差异源于规格与gold类型不同。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-023_stg_social_media__twitter_organic_tweets.json`，条目 `date_projection`。

基线：L0=258行/7740格; L1=258行/7740格; L2=258行/7740格; L3=258行/7740格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：258行/7740格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "cast(o.date as date) as date",
    "new": "o.date as date",
    "offset": 516
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: account_id
          data_type: VARCHAR
        - name: date
          data_type: DATE
        - name: organic_tweet_id
          data_type: VARCHAR
          description: "CAST(o.organic_tweet_id AS VARCHAR)."
        - name: placement
          data_type: VARCHAR
        - name: _fivetran_synced
          data_type: TIMESTAMP
        - name: app_clicks
          data_type: BIGINT
        - name: card_engagements
          data_type: BIGINT
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_organic_tweets:date_projection`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
