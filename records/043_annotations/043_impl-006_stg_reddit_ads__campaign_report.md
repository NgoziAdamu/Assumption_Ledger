# 043 校准定稿：impl-006_stg_reddit_ads__campaign_report

## 任务

按冻结v3.2第3～8节盲标，封存后解盲。此件是解盲后的定稿，封存件不改。

## 结论

主要原因：多因并列；并列类别：代码写错、Quiet Downgrade、Unstated Choice。不是只能组合修复。

20处单改均为(1200行,24000格)→(1200行,22800格)，全部并列；不把多个独立可改单列合并成一个点。

024旧主要原因：`多因并列（A、D、I）`，仅存档。

## 详细发现

### spend

并列主要原因；代码写错；把握高。

同一个 event 19 字典先将 spend 映射到原始 spend，后一个同名键仅留下 local_spend_amount；正确映射被覆盖。按第6节代码自身明确证据排除前提类。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `spend`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 19 / `args.command`：

```text
'spend':['spend','local_spend_amount']
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 19 / `args.command`：

```text
'spend':['local_spend_amount']
```

### video_views

并列主要原因；Quiet Downgrade；把握高。

原始 video_started 非空1200行，是可判断的视频观看候选列；直接整列 NULL，没有作映射判断。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `video_views`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### video_view_rate

并列主要原因；Unstated Choice；把握中。

没有对应的 video_view_rate 源列，契约没有规定由哪种观看量、哪个分母计算；gold 取常量0，agent 留 NULL。材料没定的选择。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `video_view_rate`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### upvotes

并列主要原因；Quiet Downgrade；把握高。

原始 comment_upvotes 非空1200行，存在明确候选，直接整列 NULL。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `upvotes`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### downvotes

并列主要原因；Quiet Downgrade；把握高。

原始 comment_downvotes 非空1200行，存在明确候选，直接整列 NULL。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `downvotes`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### comments

并列主要原因；Quiet Downgrade；把握高。

原始 viewer_comments 非空1200行，存在明确候选，直接整列 NULL。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `comments`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### shares

并列主要原因；Unstated Choice；把握高。

原始列清单无 shares 对应列；契约未规定缺失填0或NULL。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `shares`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### saves

并列主要原因；Unstated Choice；把握高。

原始列清单无 saves 对应列；契约未规定缺失填0或NULL。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `saves`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### post_visits

并列主要原因；Unstated Choice；把握中。

复核列清单和契约：comments_page_views是评论页面浏览量，是否等同post_visits没有说明，不能仅凭相近名称确立目标含义；gold也未使用该候选而取0。按缺少明确对应列、默认值未规定处理为Unstated Choice。保留有候选即降级的另一读法。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `post_visits`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

解盲后复核：复核列清单和契约：comments_page_views是评论页面浏览量，是否等同post_visits没有说明，不能仅凭相近名称确立目标含义；gold也未使用该候选而取0。按缺少明确对应列、默认值未规定处理为Unstated Choice。保留有候选即降级的另一读法。

### profile_visits

并列主要原因；Unstated Choice；把握高。

原始列清单无 profile_visits 对应列；契约未规定缺失默认值。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `profile_visits`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### community_joins

并列主要原因；Unstated Choice；把握高。

原始列清单无 community_joins 对应列；契约未规定缺失默认值。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `community_joins`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### conversions

并列主要原因；Unstated Choice；把握中。

有若干 app_install 事件列，但契约没有规定总转化范围或聚合方式，不能从 gold 的常量0确定定义。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `conversions`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### conversion_value

并列主要原因；Unstated Choice；把握中。

契约没有确定哪些事件或支出代表转化价值；不能把 spend 直接当转化价值。NULL与gold的0属于材料没定的缺失处理。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `conversion_value`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### click_through_rate

并列主要原因；Unstated Choice；把握中。

从原始ctr转换还是从clicks/impressions重算，契约只给类型，没有规定算法。原始是mock_ctr文本而非可确定的数字；TRY_CAST全失败不能单独证明本应有哪个数值，不将gold重算选择作为数据事实。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `click_through_rate`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

解盲后复核：类别不变；第2档与036第4档存在差异。本次保留第2档：finish event97明确说明TRY_CAST不可解析值转NULL，正是本处处理类别；未点名Reddit，不升级第1档。

### cost_per_click

并列主要原因；Unstated Choice；把握中。

原始cpc为mock_cpc文本，转换留NULL与用spend/clicks重算的差异取决于未规定的取数/重算选择；没有把mock编号解释成金额。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `cost_per_click`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

解盲后复核：类别不变；第2档与036第4档存在差异。本次保留第2档：finish event97明确说明TRY_CAST不可解析值转NULL，正是本处处理类别；未点名Reddit，不升级第1档。

### cost_per_thousand_impressions

并列主要原因；Unstated Choice；把握中。

原始ecpm为mock_ecpm文本；契约没有规定使用原始指标还是重算。不能从全部TRY_CAST失败直接推出可确定的原始金额。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `cost_per_thousand_impressions`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

解盲后复核：类别不变；第2档与036第4档存在差异。本次保留第2档：finish event97明确说明TRY_CAST不可解析值转NULL，正是本处处理类别；未点名Reddit，不升级第1档。

### cost_per_video_view

并列主要原因；Unstated Choice；把握中。

原始没有单位观看成本列，video_started、完整可见播放、不同观看时长等不是同一计数；契约未定成本分母，不能以gold选video_started证明本处是省略已定义指标。按未定定义/缺失处理归Unstated Choice。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `cost_per_video_view`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

解盲后复核：原始没有单位观看成本列，video_started、完整可见播放、不同观看时长等不是同一计数；契约未定成本分母，不能以gold选video_started证明本处是省略已定义指标。按未定定义/缺失处理归Unstated Choice。

### cost_per_conversion

并列主要原因；Unstated Choice；把握中。

转化量定义及缺失时的默认值未规定，不能用gold常量0证明agent的NULL不合理。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `cost_per_conversion`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

### total_engagements

并列主要原因；Unstated Choice；把握中。

契约未规定互动事件集合、是否纳入downvotes、是否将评论页访问纳入；原始没有该总量列。盲标把存在分项等同已明确的目标指标，证据不足；改Unstated Choice。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `total_engagements`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

解盲后复核：契约未规定互动事件集合、是否纳入downvotes、是否将评论页访问纳入；原始没有该总量列。盲标把存在分项等同已明确的目标指标，证据不足；改Unstated Choice。

### engagement_rate

并列主要原因；Unstated Choice；把握中。

互动事件集合和分母均未规定，原始无此比率列；能构造一种公式不足以证明该公式就是要求的量。按未定选择归Unstated Choice。

是否说出：第2档，交付物里只有通用说明。event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-006_stg_reddit_ads__campaign_report.json` / `engagement_rate`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1200 | 1200 | 24000 | 22800 |

| L1 | 1200 | 1200 | 24000 | 22800 |

| L2 | 1200 | 1200 | 24000 | 22800 |

| L3 | 1200 | 1200 | 24000 | 22800 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 97 / `args.final_thought`：

```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/output.jsonl` / event 18 / `content`：

```text
'priority', 'region', 'spend', 'video_fully_viewable_impressions'
```

解盲后复核：互动事件集合和分母均未规定，原始无此比率列；能构造一种公式不足以证明该公式就是要求的量。按未定选择归Unstated Choice。

## 证据来源

- 契约 `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`；SHA-256 `fe80055f9d2c7c6799385cce0e0d788bd4a513f8998eb3b2897937e8c2bf90c4`。

- 交付SQL `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_reddit_ads__campaign_report.sql`；SHA-256 `5f29b62488b3998f55c87dc9ebcefa3057672fed9544e110f91ffc29094c7cd2`。

- 013材料包、024核实查询/单改/补充单改、原始output.jsonl；043新增1条Reddit原始指标文本范围核实查询（只读）。

- 封存、对比与结构化定稿：`records/043_calibration_blind_sealed.json`、`records/043_calibration_comparison.json`、`records/043_checks/calibration_working.json`。

## 不确定或没查到的（含规则问题）

Reddit的派生指标NULL与降级边界、mock_*源指标取数与重算的边界保留在封存/比较件中；不能由gold的公式倒推规格。

## 建议的下一步

同一会话继续50张正式表。校准定稿与盲标一致率分开保存。
