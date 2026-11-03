# 043：impl-023_social_media_reporting__youtube_videos_reporting

## 结论

主要原因：**Unstated Choice**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为152行/152格。行增多时即使格减少也不作为改善。

层：intermediate。024旧主要原因原样保留：`A`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/intermediate/social_media_reporting__youtube_videos_reporting.sql`；无SQL注释。材料包：`records/024_packages/024_impl-023_social_media_reporting__youtube_videos_reporting.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-023.json`；与gold关系见 `records/015_raw_impl-023.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 29,31,33，`/tmp/write_sql.py`：同一files字典脚本分三次写入staging、中间层、marts；各表表达式分别定义。 目录编号：`023-write-sql`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共0条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

涉及运行时间的基线与单改沿用同一固定时刻：`[{"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-17'", "count": 1}]`；完整控制记录见复用重跑JSON。

## 点：page_name

类别：**Unstated Choice**；角色：主要；把握：中。

契约称channel title，但上游channel_title与page_name两列并存，没有指定源列；不以gold选择page_name作为映射事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_social_media_reporting__youtube_videos_reporting.json`，条目 `page_name`。

基线：L0=152行/152格; L1=152行/152格; L2=152行/152格; L3=152行/152格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：152行/152格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "coalesce(channel_title,",
    "new": "coalesce(page_name,",
    "offset": 319
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
      source_models:
      - staging.stg_social_media__youtube_videos
      business_logic: '- Source and filter: use staging.stg_social_media__youtube_videos rows where video_id is present and video_published_at is within the last two years. - Mapping: - page_id: channel_id cast to text; nulls remain null. - page_name: channel title; if missing, set to ''Unknown Channel''. - post_id: video_id cast to text (always present due to filter). - created_timestamp: video_published_at (always present due to filter). - platform: constant ''youtube''. - post_message: video_description cast to text; original casing and spacing preserved. - clicks and impressions: both set to the video''s views; views come from the source clicks field; default to 0 when missing. - likes, comments, shares: interactions default to 0 when missing; shares use the source estimated_shares. - post_url: passed through from source; may represent a thumbnail URL; may be null. - privacy_status: passed through. - channel_subscribers and channel_total_videos: default to 0; total_videos is 0 in the current SQL. - calculated_engagement_rate: - Use the provided engagement_rate when it is positive; otherwise, if views > 0, compute (likes + comments + shares) divided by views; else 0.0; no rounding or capping. - Derived ratios: - views_per_subscriber: clicks divided by channel_subscribers when subscribers > 0, else 0.0. - likes_per_view_ratio: likes divided by clicks when clicks > 0, else 0.0. - No aggregation, de-duplication, or ordering; rows mirror the filtered source.'
      columns:
      - name: page_id
        data_type: VARCHAR
        description: Channel identifier cast to text; nulls preserved
      - name: page_name
        data_type: VARCHAR
        description: Channel title with fallback to 'Unknown Channel' when missing
      - name: post_id
        data_type: VARCHAR
        description: YouTube video identifier cast to text; non-null due to the source filter on video_id
        tests:
        - not_null
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_social_media_reporting__youtube_videos_reporting:page_name`。

## 点：impressions

类别：**Intent Misreading**；角色：非原因；把握：高。

契约明确views来自source clicks，agent使用impressions；本数据单改无改善，仍记录未落实的规格前提。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-023_social_media_reporting__youtube_videos_reporting.json`，条目 `impressions`。

基线：L0=152行/152格; L1=152行/152格; L2=152行/152格; L3=152行/152格。

单改后：L0=152行/152格; L1=152行/152格; L2=152行/152格; L3=152行/152格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "coalesce(impressions, 0)::bigint as impressions",
    "new": "coalesce(clicks, 0)::bigint as impressions",
    "offset": 587
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
      source_models:
      - staging.stg_social_media__youtube_videos
      business_logic: '- Source and filter: use staging.stg_social_media__youtube_videos rows where video_id is present and video_published_at is within the last two years. - Mapping: - page_id: channel_id cast to text; nulls remain null. - page_name: channel title; if missing, set to ''Unknown Channel''. - post_id: video_id cast to text (always present due to filter). - created_timestamp: video_published_at (always present due to filter). - platform: constant ''youtube''. - post_message: video_description cast to text; original casing and spacing preserved. - clicks and impressions: both set to the video''s views; views come from the source clicks field; default to 0 when missing. - likes, comments, shares: interactions default to 0 when missing; shares use the source estimated_shares. - post_url: passed through from source; may represent a thumbnail URL; may be null. - privacy_status: passed through. - channel_subscribers and channel_total_videos: default to 0; total_videos is 0 in the current SQL. - calculated_engagement_rate: - Use the provided engagement_rate when it is positive; otherwise, if views > 0, compute (likes + comments + shares) divided by views; else 0.0; no rounding or capping. - Derived ratios: - views_per_subscriber: clicks divided by channel_subscribers when subscribers > 0, else 0.0. - likes_per_view_ratio: likes divided by clicks when clicks > 0, else 0.0. - No aggregation, de-duplication, or ordering; rows mirror the filtered source.'
      columns:
      - name: page_id
        data_type: VARCHAR
        description: Channel identifier cast to text; nulls preserved
      - name: page_name
        data_type: VARCHAR
        description: Channel title with fallback to 'Unknown Channel' when missing
      - name: post_id
        data_type: VARCHAR
        description: YouTube video identifier cast to text; non-null due to the source filter on video_id
        tests:
        - not_null
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_social_media_reporting__youtube_videos_reporting:impressions`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
