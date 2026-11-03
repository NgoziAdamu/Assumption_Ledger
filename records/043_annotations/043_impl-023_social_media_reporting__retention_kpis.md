# 043：impl-023_social_media_reporting__retention_kpis

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为13行/91格。行增多时即使格减少也不作为改善。

层：marts。024旧主要原因原样保留：`C`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/marts/social_media_reporting__retention_kpis.sql`；无SQL注释。材料包：`records/024_packages/024_impl-023_social_media_reporting__retention_kpis.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-023.json`；与gold关系见 `records/015_raw_impl-023.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 29,31,33，`/tmp/write_sql.py`：同一files字典脚本分三次写入staging、中间层、marts；各表表达式分别定义。 目录编号：`023-write-sql`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共0条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

## 点：cohort_date_type

类别：**其他**；角色：非原因；把握：高。

cohort_week契约为DATE；agent显式DATE符合要求，改成gold的时间类型反而增加差异。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_social_media_reporting__retention_kpis.json`，条目 `cohort_date_type`。

基线：L0=13行/91格; L1=13行/91格; L2=13行/91格; L3=13行/91格。

单改后：L0=637行/4459格; L1=637行/4459格; L2=637行/4459格; L3=637行/4459格。L0减量（先行后格）：-624行/-4368格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "date_trunc('week', created_timestamp)::date as activity_week",
    "new": "date_trunc('week', created_timestamp) as activity_week",
    "offset": 77
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
    - name: social_media_reporting__retention_kpis
      description: Weekly retention KPIs by platform using posting-activity cohorts over a fixed 13-week window
      grain: One row per platform per cohort_week per week_offset
      source_models:
      - intermediate.social_media_reporting__facebook_posts_reporting
      - intermediate.social_media_reporting__instagram_posts_reporting
      - intermediate.social_media_reporting__linkedin_posts_reporting
      - intermediate.social_media_reporting__twitter_posts_reporting
      - intermediate.social_media_reporting__youtube_videos_reporting
      business_logic: '- Inputs: - Union page activity from the five source models; only keep rows where created_timestamp is present. - Assign platform as one of: "facebook", "instagram", "linkedin", "twitter", "youtube". - Weekly normalization: - Bucket activity into ISO weeks starting Monday 00:00. - A page is considered active in a week if it posts at least once; multiple posts in the same week do not increase the activity count. - Cohorts: - For each (page_id, platform), set cohort_week to the earliest week with activity. - For each (platform, cohort_week), cohort_pages is the number of unique pages in that cohort. - Observation spine: - Generate week_offset values from 0 to 12 inclusive. - For each cohort, create 13 rows and set target_week to the start of the week that is week_offset weeks after cohort_week; when week_offset = 0, target_week equals cohort_week. - Activity presence: - Build distinct (platform, week, page_id) combinations so each active page-week is counted once. - Retention: - For each spine row, retained_pages is the number of unique pages active on the platform in target_week; this is not limited to members of the cohort. - KPI: - retention_rate = retained_pages divided by cohort_pages when cohort_pages > 0; otherwise 0.0. - No rounding; stored as double precision; values may exceed 1.0 due to the numerator scope. - Output: - Emit platform, cohort_week, week_offset, target_week, cohort_pages, retained_pages, retention_rate. - No explicit ordering is applied.'
      columns:
      - name: platform
        data_type: VARCHAR
        description: 'Platform name in lowercase: facebook, instagram, linkedin, twitter, or youtube'
        tests:
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_social_media_reporting__retention_kpis:cohort_date_type`。

## 点：null_page

类别：**Intent Misreading**；角色：主要；把握：高。

输入规则只按created_timestamp是否存在过滤，随后为每个page/platform建立cohort；额外排除NULL page_id丢失13个spine行。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-023_social_media_reporting__retention_kpis.json`，条目 `null_page`。

基线：L0=13行/91格; L1=13行/91格; L2=13行/91格; L3=13行/91格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：13行/91格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "    where page_id is not null",
    "new": "    where true",
    "offset": 1134
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
      - intermediate.social_media_reporting__twitter_posts_reporting
      - intermediate.social_media_reporting__youtube_videos_reporting
      business_logic: '- Inputs: - Union page activity from the five source models; only keep rows where created_timestamp is present. - Assign platform as one of: "facebook", "instagram", "linkedin", "twitter", "youtube". - Weekly normalization: - Bucket activity into ISO weeks starting Monday 00:00. - A page is considered active in a week if it posts at least once; multiple posts in the same week do not increase the activity count. - Cohorts: - For each (page_id, platform), set cohort_week to the earliest week with activity. - For each (platform, cohort_week), cohort_pages is the number of unique pages in that cohort. - Observation spine: - Generate week_offset values from 0 to 12 inclusive. - For each cohort, create 13 rows and set target_week to the start of the week that is week_offset weeks after cohort_week; when week_offset = 0, target_week equals cohort_week. - Activity presence: - Build distinct (platform, week, page_id) combinations so each active page-week is counted once. - Retention: - For each spine row, retained_pages is the number of unique pages active on the platform in target_week; this is not limited to members of the cohort. - KPI: - retention_rate = retained_pages divided by cohort_pages when cohort_pages > 0; otherwise 0.0. - No rounding; stored as double precision; values may exceed 1.0 due to the numerator scope. - Output: - Emit platform, cohort_week, week_offset, target_week, cohort_pages, retained_pages, retention_rate. - No explicit ordering is applied.'
      columns:
      - name: platform
        data_type: VARCHAR
        description: 'Platform name in lowercase: facebook, instagram, linkedin, twitter, or youtube'
        tests:
        - not_null
      - name: cohort_week
        data_type: DATE
        description: Start date (Monday) of the first week the page is active for the platform
        tests:
        - not_null
      - name: week_offset
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_social_media_reporting__retention_kpis:null_page`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
