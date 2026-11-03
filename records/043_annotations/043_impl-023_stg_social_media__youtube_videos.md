# 043：impl-023_stg_social_media__youtube_videos

## 结论

主要原因：**Unstated Choice**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为0行/152格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`A`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__youtube_videos.sql`；无SQL注释。材料包：`records/024_packages/024_impl-023_stg_social_media__youtube_videos.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-023.json`；与gold关系见 `records/015_raw_impl-023.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.youtube_channel_basic`：initial 2500行/41列；agent留存 2500行/41列；013差异=False。

- `raw.youtube_video`：initial 2500行/42列；agent留存 2500行/42列；013差异=False。

## 同源决定

同源决定：event 29,31,33，`/tmp/write_sql.py`：同一files字典脚本分三次写入staging、中间层、marts；各表表达式分别定义。 目录编号：`023-write-sql`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共2条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引8（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `频道多版本与两个标题`：`records/024_queries.json` 数组索引9（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

涉及运行时间的基线与单改沿用同一固定时刻：`[{"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-17'", "count": 1}]`；完整控制记录见复用重跑JSON。

## 点：channel_relation

类别：**Unstated Choice**；角色：非原因；把握：中。

契约未规定同channel资料多版本如何选；max与保留distinct资料属于未定选择。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__youtube_videos.json`，条目 `channel_relation`。

基线：L0=152行/503格; L1=152行/351格; L2=152行/218格; L3=152行/218格。

单改后：L0=152行/503格; L1=152行/351格; L2=152行/218格; L3=152行/218格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "select channel_id, max(channel_subscribers) as channel_subscribers\n    from raw.youtube_channel_basic\n    group by channel_id",
    "new": "select distinct channel_id, channel_display_name, channel_subscribers\n    from raw.youtube_channel_basic",
    "offset": 27
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: subscribers
          data_type: BIGINT
          description: "COALESCE(channel_info.channel_subscribers, 0)."
        - name: engagement_rate
          data_type: DOUBLE
          description: "CASE WHEN impressions > 0 THEN (likes + comments + estimated_shares)::DOUBLE / impressions ELSE 0.0 END."
        - name: _fivetran_synced
          data_type: TIMESTAMP
          description: "_fivetran_synced from raw.youtube_video."


# --------------------------------------------------------------------------- #
# PHASE 2: Defines the business logic from staging to analytical models.      #
# --------------------------------------------------------------------------- #
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__youtube_videos:channel_relation`。

## 点：channel_title

类别：**Unstated Choice**；角色：非原因；把握：中。

channel_title没有Unknown默认值规则；NULL与占位字符串未定。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__youtube_videos.json`，条目 `channel_title`。

基线：L0=152行/503格; L1=152行/351格; L2=152行/218格; L3=152行/218格。

单改后：L0=152行/503格; L1=152行/351格; L2=152行/218格; L3=152行/218格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "v.snippet_channel_title::varchar as channel_title",
    "new": "coalesce(v.snippet_channel_title, 'Unknown Channel')::varchar as channel_title",
    "offset": 417
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: channel_id
          data_type: VARCHAR
        - name: channel_title
          data_type: VARCHAR
        - name: page_name
          data_type: VARCHAR
        - name: post_url
          data_type: VARCHAR
          description: "Thumbnail URL used as post URL: https://img.youtube.com/vi/{video_id}/default.jpg."
          validation_rules:
            - rule: "post_url RLIKE '^https://img.youtube.com/vi/.+/default.jpg'"
              on_failure: correct
        - name: privacy_status
          data_type: VARCHAR
        - name: clicks
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__youtube_videos:channel_title`。

## 点：page_name

类别：**Unstated Choice**；角色：主要；把握：中。

page_name未指定视频snippet标题或channel_display_name，属于源字段选择。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__youtube_videos.json`，条目 `page_name`。

基线：L0=152行/503格; L1=152行/351格; L2=152行/218格; L3=152行/218格。

单改后：L0=152行/351格; L1=133行/199格; L2=66行/66格; L3=66行/66格。L0减量（先行后格）：0行/152格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "coalesce(v.snippet_channel_title, 'Unknown Channel')::varchar as page_name",
    "new": "(select max(channel_display_name) from raw.youtube_channel_basic cb where cb.channel_id=v.snippet_channel_id)::varchar as page_name",
    "offset": 472
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: channel_title
          data_type: VARCHAR
        - name: page_name
          data_type: VARCHAR
        - name: post_url
          data_type: VARCHAR
          description: "Thumbnail URL used as post URL: https://img.youtube.com/vi/{video_id}/default.jpg."
          validation_rules:
            - rule: "post_url RLIKE '^https://img.youtube.com/vi/.+/default.jpg'"
              on_failure: correct
        - name: privacy_status
          data_type: VARCHAR
        - name: clicks
          data_type: BIGINT
        - name: impressions
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__youtube_videos:page_name`。

## 点：estimated_shares

类别：**其他**；角色：参与；把握：高。

契约明确FLOOR(likes/10)，agent照做；gold的整数CAST采用不同取整。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__youtube_videos.json`，条目 `estimated_shares`。

基线：L0=152行/503格; L1=152行/351格; L2=152行/218格; L3=152行/218格。

单改后：L0=152行/437格; L1=152行/285格; L2=152行/152格; L3=152行/152格。L0减量（先行后格）：0行/66格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "floor(v.statistics_like_count / 10.0)::bigint",
    "new": "cast(v.statistics_like_count / 10.0 as bigint)",
    "offset": 978
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
          data_type: BIGINT
          description: >
            CASE WHEN statistics_like_count > 10 THEN FLOOR(statistics_like_count / 10) ELSE 0 END.
        - name: subscribers
          data_type: BIGINT
          description: "COALESCE(channel_info.channel_subscribers, 0)."
        - name: engagement_rate
          data_type: DOUBLE
          description: "CASE WHEN impressions > 0 THEN (likes + comments + estimated_shares)::DOUBLE / impressions ELSE 0.0 END."
        - name: _fivetran_synced
          data_type: TIMESTAMP
          description: "_fivetran_synced from raw.youtube_video."


# --------------------------------------------------------------------------- #
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__youtube_videos:estimated_shares`。

## 点：engagement_shares

类别：**其他**；角色：参与；把握：高。

契约明确engagement使用estimated_shares，agent使用其FLOOR值；gold分子用未FLOOR值。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__youtube_videos.json`，条目 `engagement_shares`。

基线：L0=152行/503格; L1=152行/351格; L2=152行/218格; L3=152行/218格。

单改后：L0=152行/370格; L1=152行/218格; L2=152行/218格; L3=152行/218格。L0减量（先行后格）：0行/133格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "floor(v.statistics_like_count / 10.0) else 0 end",
    "new": "v.statistics_like_count / 10.0 else 0 end",
    "offset": 1350
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: engagement_rate
          data_type: DOUBLE
          description: "CASE WHEN impressions > 0 THEN (likes + comments + estimated_shares)::DOUBLE / impressions ELSE 0.0 END."
        - name: _fivetran_synced
          data_type: TIMESTAMP
          description: "_fivetran_synced from raw.youtube_video."


# --------------------------------------------------------------------------- #
# PHASE 2: Defines the business logic from staging to analytical models.      #
# --------------------------------------------------------------------------- #
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__youtube_videos:engagement_shares`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
