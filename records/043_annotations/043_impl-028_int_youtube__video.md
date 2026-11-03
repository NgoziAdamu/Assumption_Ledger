# 043：impl-028_int_youtube__video

## 结论

主要原因：**代码写错**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为0行/5格。行增多时即使格减少也不作为改善。

层：intermediate。024旧主要原因原样保留：`I`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/sql/intermediate/int_youtube__video.sql`；无SQL注释。材料包：`records/024_packages/024_impl-028_int_youtube__video.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-028.json`；与gold关系见 `records/015_raw_impl-028.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 29，`event29 shell heredoc批量写SQL`：同一命令写int_youtube__video及本批范围外marts；本批三段缩略图正则复制了相同转义写法。 目录编号：`028-video-command`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 29，三种缩略图URL正则复制同一quoted heredoc中的双反斜杠写法。 本表点：default_regex, medium_regex, high_regex；编号 `028-thumbnail-escaping`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共1条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `agent可见thumbnail非空`：`records/024_queries.json` 数组索引28（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 诊断 `CS gold thumbnail解析输入`：`records/024_queries.json` 数组索引29（从0开始）。

## 点：default_regex

类别：**代码写错**；角色：并列；把握：高。

SQL意图匹配JSON-like的default.url和空白/花括号，但quoted heredoc中双反斜杠使正则匹配字面反斜杠；是实现转义错误。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-028_int_youtube__video.json`，条目 `default_regex`。

基线：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。

单改后：L0=5行/10格; L1=5行/10格; L2=5行/10格; L3=5行/10格。L0减量（先行后格）：0行/5格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "regexp_extract(video_thumbnails, '\"default\"\\\\s*:\\\\s*\\\\{[^}]*\"url\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) as default_thumbnail_url",
    "new": "regexp_extract(video_thumbnails, '\"default\"\\s*:\\s*\\{[^}]*\"url\"\\s*:\\s*\"([^\"]*)\"', 1) as default_thumbnail_url",
    "offset": 463
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/output.jsonl`：

```text
      source_models:
      - staging.stg_youtube__video
      business_logic: '- Start with all rows from staging.stg_youtube__video. - Thumbnail URL parsing: - Treat video_thumbnails as a JSON-like string that may contain sections labeled default, medium, and high. - For each section (default/medium/high), locate the first occurrence of that section; within it, if a url field exists, extract the exact string value of url up to the next quote; if the section or url is missing, return NULL. - Do not trim, decode, unescape, or alter case or spacing of the extracted URL. - Published timestamps: - published_at_ts: attempt to parse snippet_published_at as a timestamp; if parsing fails, set to NULL. If the input is a date, the time is 00:00:00. - published_at_date: take the calendar date (day-level) from published_at_ts; if published_at_ts is NULL, this is NULL. - All other columns are carried through exactly from staging with no transformations; NULLs and original formatting are preserved. - No deduplication, aggregation, or ordering is applied; output preserves one row per input record.'
      columns:
      - name: video_id
        data_type: VARCHAR
        description: YouTube video identifier from the source.
        tests:
        - not_null
        - unique
      - name: channel_id
        data_type: VARCHAR
        description: Owning YouTube channel identifier from the source.
        tests: []
      - name: video_title
```

契约／过程证据（与上段重复的引句略）：

event 29 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/output.jsonl`：

```text
regexp_extract(video_thumbnails, '"default"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as default_thumbnail_url
```


共同生成动作 `028-video-command`；根源决定单元 `028-thumbnail-escaping`。

## 点：default_missing

类别：**其他**；角色：非原因；把握：高。

缺section/url返回NULL在契约写明；agent NULLIF符合要求，gold返回空串。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-028_int_youtube__video.json`，条目 `default_missing`。

基线：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。

单改后：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "nullif(default_thumbnail_url, '') as default_thumbnail_url",
    "new": "default_thumbnail_url as default_thumbnail_url",
    "offset": 1904
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/output.jsonl`：

```text
      source_models:
      - staging.stg_youtube__video
      business_logic: '- Start with all rows from staging.stg_youtube__video. - Thumbnail URL parsing: - Treat video_thumbnails as a JSON-like string that may contain sections labeled default, medium, and high. - For each section (default/medium/high), locate the first occurrence of that section; within it, if a url field exists, extract the exact string value of url up to the next quote; if the section or url is missing, return NULL. - Do not trim, decode, unescape, or alter case or spacing of the extracted URL. - Published timestamps: - published_at_ts: attempt to parse snippet_published_at as a timestamp; if parsing fails, set to NULL. If the input is a date, the time is 00:00:00. - published_at_date: take the calendar date (day-level) from published_at_ts; if published_at_ts is NULL, this is NULL. - All other columns are carried through exactly from staging with no transformations; NULLs and original formatting are preserved. - No deduplication, aggregation, or ordering is applied; output preserves one row per input record.'
      columns:
      - name: video_id
        data_type: VARCHAR
        description: YouTube video identifier from the source.
        tests:
        - not_null
        - unique
      - name: channel_id
        data_type: VARCHAR
        description: Owning YouTube channel identifier from the source.
        tests: []
      - name: video_title
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `028-video-command`；根源决定单元 `impl-028_int_youtube__video:default_missing`。

## 点：medium_regex

类别：**代码写错**；角色：并列；把握：高。

同一JSON-like提取写法的medium表达式多一层转义；逐列单改可复原值，不以原始NULL推断CS不可评估。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-028_int_youtube__video.json`，条目 `medium_regex`。

基线：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。

单改后：L0=5行/10格; L1=5行/10格; L2=5行/10格; L3=5行/10格。L0减量（先行后格）：0行/5格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "regexp_extract(video_thumbnails, '\"medium\"\\\\s*:\\\\s*\\\\{[^}]*\"url\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) as medium_thumbnail_url",
    "new": "regexp_extract(video_thumbnails, '\"medium\"\\s*:\\s*\\{[^}]*\"url\"\\s*:\\s*\"([^\"]*)\"', 1) as medium_thumbnail_url",
    "offset": 586
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/output.jsonl`：

```text
      source_models:
      - staging.stg_youtube__video
      business_logic: '- Start with all rows from staging.stg_youtube__video. - Thumbnail URL parsing: - Treat video_thumbnails as a JSON-like string that may contain sections labeled default, medium, and high. - For each section (default/medium/high), locate the first occurrence of that section; within it, if a url field exists, extract the exact string value of url up to the next quote; if the section or url is missing, return NULL. - Do not trim, decode, unescape, or alter case or spacing of the extracted URL. - Published timestamps: - published_at_ts: attempt to parse snippet_published_at as a timestamp; if parsing fails, set to NULL. If the input is a date, the time is 00:00:00. - published_at_date: take the calendar date (day-level) from published_at_ts; if published_at_ts is NULL, this is NULL. - All other columns are carried through exactly from staging with no transformations; NULLs and original formatting are preserved. - No deduplication, aggregation, or ordering is applied; output preserves one row per input record.'
      columns:
      - name: video_id
        data_type: VARCHAR
        description: YouTube video identifier from the source.
        tests:
        - not_null
        - unique
      - name: channel_id
        data_type: VARCHAR
        description: Owning YouTube channel identifier from the source.
        tests: []
      - name: video_title
```

契约／过程证据（与上段重复的引句略）：

event 29 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/output.jsonl`：

```text
regexp_extract(video_thumbnails, '"medium"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as medium_thumbnail_url
```


共同生成动作 `028-video-command`；根源决定单元 `028-thumbnail-escaping`。

## 点：medium_missing

类别：**其他**；角色：非原因；把握：高。

缺section/url返回NULL符合契约；gold空串。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-028_int_youtube__video.json`，条目 `medium_missing`。

基线：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。

单改后：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "nullif(medium_thumbnail_url, '') as medium_thumbnail_url",
    "new": "medium_thumbnail_url as medium_thumbnail_url",
    "offset": 1968
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/output.jsonl`：

```text
      source_models:
      - staging.stg_youtube__video
      business_logic: '- Start with all rows from staging.stg_youtube__video. - Thumbnail URL parsing: - Treat video_thumbnails as a JSON-like string that may contain sections labeled default, medium, and high. - For each section (default/medium/high), locate the first occurrence of that section; within it, if a url field exists, extract the exact string value of url up to the next quote; if the section or url is missing, return NULL. - Do not trim, decode, unescape, or alter case or spacing of the extracted URL. - Published timestamps: - published_at_ts: attempt to parse snippet_published_at as a timestamp; if parsing fails, set to NULL. If the input is a date, the time is 00:00:00. - published_at_date: take the calendar date (day-level) from published_at_ts; if published_at_ts is NULL, this is NULL. - All other columns are carried through exactly from staging with no transformations; NULLs and original formatting are preserved. - No deduplication, aggregation, or ordering is applied; output preserves one row per input record.'
      columns:
      - name: video_id
        data_type: VARCHAR
        description: YouTube video identifier from the source.
        tests:
        - not_null
        - unique
      - name: channel_id
        data_type: VARCHAR
        description: Owning YouTube channel identifier from the source.
        tests: []
      - name: video_title
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `028-video-command`；根源决定单元 `impl-028_int_youtube__video:medium_missing`。

## 点：high_regex

类别：**代码写错**；角色：并列；把握：高。

同一JSON-like提取写法的high表达式多一层转义。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-028_int_youtube__video.json`，条目 `high_regex`。

基线：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。

单改后：L0=5行/10格; L1=5行/10格; L2=5行/10格; L3=5行/10格。L0减量（先行后格）：0行/5格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "regexp_extract(video_thumbnails, '\"high\"\\\\s*:\\\\s*\\\\{[^}]*\"url\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) as high_thumbnail_url",
    "new": "regexp_extract(video_thumbnails, '\"high\"\\s*:\\s*\\{[^}]*\"url\"\\s*:\\s*\"([^\"]*)\"', 1) as high_thumbnail_url",
    "offset": 707
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/output.jsonl`：

```text
      source_models:
      - staging.stg_youtube__video
      business_logic: '- Start with all rows from staging.stg_youtube__video. - Thumbnail URL parsing: - Treat video_thumbnails as a JSON-like string that may contain sections labeled default, medium, and high. - For each section (default/medium/high), locate the first occurrence of that section; within it, if a url field exists, extract the exact string value of url up to the next quote; if the section or url is missing, return NULL. - Do not trim, decode, unescape, or alter case or spacing of the extracted URL. - Published timestamps: - published_at_ts: attempt to parse snippet_published_at as a timestamp; if parsing fails, set to NULL. If the input is a date, the time is 00:00:00. - published_at_date: take the calendar date (day-level) from published_at_ts; if published_at_ts is NULL, this is NULL. - All other columns are carried through exactly from staging with no transformations; NULLs and original formatting are preserved. - No deduplication, aggregation, or ordering is applied; output preserves one row per input record.'
      columns:
      - name: video_id
        data_type: VARCHAR
        description: YouTube video identifier from the source.
        tests:
        - not_null
        - unique
      - name: channel_id
        data_type: VARCHAR
        description: Owning YouTube channel identifier from the source.
        tests: []
      - name: video_title
```

契约／过程证据（与上段重复的引句略）：

event 29 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/output.jsonl`：

```text
regexp_extract(video_thumbnails, '"high"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as high_thumbnail_url
```


共同生成动作 `028-video-command`；根源决定单元 `028-thumbnail-escaping`。

## 点：high_missing

类别：**其他**；角色：非原因；把握：高。

缺section/url返回NULL符合契约；gold空串。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-028_int_youtube__video.json`，条目 `high_missing`。

基线：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。

单改后：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "nullif(high_thumbnail_url, '') as high_thumbnail_url",
    "new": "high_thumbnail_url as high_thumbnail_url",
    "offset": 2030
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/output.jsonl`：

```text
      source_models:
      - staging.stg_youtube__video
      business_logic: '- Start with all rows from staging.stg_youtube__video. - Thumbnail URL parsing: - Treat video_thumbnails as a JSON-like string that may contain sections labeled default, medium, and high. - For each section (default/medium/high), locate the first occurrence of that section; within it, if a url field exists, extract the exact string value of url up to the next quote; if the section or url is missing, return NULL. - Do not trim, decode, unescape, or alter case or spacing of the extracted URL. - Published timestamps: - published_at_ts: attempt to parse snippet_published_at as a timestamp; if parsing fails, set to NULL. If the input is a date, the time is 00:00:00. - published_at_date: take the calendar date (day-level) from published_at_ts; if published_at_ts is NULL, this is NULL. - All other columns are carried through exactly from staging with no transformations; NULLs and original formatting are preserved. - No deduplication, aggregation, or ordering is applied; output preserves one row per input record.'
      columns:
      - name: video_id
        data_type: VARCHAR
        description: YouTube video identifier from the source.
        tests:
        - not_null
        - unique
      - name: channel_id
        data_type: VARCHAR
        description: Owning YouTube channel identifier from the source.
        tests: []
      - name: video_title
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `028-video-command`；根源决定单元 `impl-028_int_youtube__video:high_missing`。

## 点：published_type

类别：**其他**；角色：非原因；把握：中。

契约列声明DATE但又要求原样透传；agent用DATE符合显式列类型，当前单改无改善。两条规格的张力单列规则问题。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-028_int_youtube__video.json`，条目 `published_type`。

基线：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。

单改后：L0=5行/15格; L1=5行/15格; L2=5行/15格; L3=5行/15格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "snippet_published_at::date as snippet_published_at",
    "new": "snippet_published_at as snippet_published_at",
    "offset": 243
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/output.jsonl`：

```text
      source_models:
      - staging.stg_youtube__video
      business_logic: '- Start with all rows from staging.stg_youtube__video. - Thumbnail URL parsing: - Treat video_thumbnails as a JSON-like string that may contain sections labeled default, medium, and high. - For each section (default/medium/high), locate the first occurrence of that section; within it, if a url field exists, extract the exact string value of url up to the next quote; if the section or url is missing, return NULL. - Do not trim, decode, unescape, or alter case or spacing of the extracted URL. - Published timestamps: - published_at_ts: attempt to parse snippet_published_at as a timestamp; if parsing fails, set to NULL. If the input is a date, the time is 00:00:00. - published_at_date: take the calendar date (day-level) from published_at_ts; if published_at_ts is NULL, this is NULL. - All other columns are carried through exactly from staging with no transformations; NULLs and original formatting are preserved. - No deduplication, aggregation, or ordering is applied; output preserves one row per input record.'
      columns:
      - name: video_id
        data_type: VARCHAR
        description: YouTube video identifier from the source.
        tests:
        - not_null
        - unique
      - name: channel_id
        data_type: VARCHAR
        description: Owning YouTube channel identifier from the source.
        tests: []
      - name: video_title
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `028-video-command`；根源决定单元 `impl-028_int_youtube__video:published_type`。

## 规则问题与限制

- published_type：契约列声明DATE但又要求原样透传；agent用DATE符合显式列类型，当前单改无改善。两条规格的张力单列规则问题。
