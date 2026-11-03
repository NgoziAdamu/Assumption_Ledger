# 043：impl-023_social_media_reporting__rollup_report

## 结论

主要原因：**其他**；把握：中；只能组合修复：否。

手册第7节同类候选例外：全部候选均其他，但并列顺序点只有组级诊断，未逐项排序。旧数值单改列原数字，不能与没有单改的点伪造完整名次。

层：marts。024旧主要原因原样保留：`O`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/marts/social_media_reporting__rollup_report.sql`；无SQL注释。材料包：`records/024_packages/024_impl-023_social_media_reporting__rollup_report.md`。

CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。

已逐张读取 `records/013_raw_impl-023.json`；与gold关系见 `records/015_raw_impl-023.json`、`records/043_checks/raw_integrity_review.json`。

## 同源决定

同源决定：event 29,31,33，`/tmp/write_sql.py`：同一files字典脚本分三次写入staging、中间层、marts；各表表达式分别定义。 目录编号：`023-write-sql`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共0条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 诊断 `排除并列顺序派生列后的整表诊断`：`records/024_extra_diagnostics.json` 数组索引17（从0开始）。

## 点：daily_platform_rank

类别：**其他**；角色：同类候选；把握：中。

契约允许并列键的任意行次序；024诊断核对并列组及排除相应派生列后的其他内容。该列单独列点，但没有独立单改收益，不用成组清零冒充该列清零。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_extra_diagnostics.json`，条目 `排除并列顺序派生列后的整表诊断`。

基线：L0=260行/307格; L1=260行/307格; L2=260行/307格; L3=260行/307格。

只有成组诊断：排除 ['daily_platform_rank', 'platform_lifetime_rank'] 后 L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格；没有该列独立单改收益。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。event1完整看到允许并列规则；交付报告没交代本处，写窗口实现不等于意识到另一个合法顺序。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
      - intermediate.social_media_reporting__twitter_posts_reporting
      - intermediate.social_media_reporting__youtube_videos_reporting
      business_logic: '- Union all five platform models with a platform label: facebook, instagram, linkedin, twitter, youtube; select page_id, page_name, post_id, post_message, created_timestamp, clicks, impressions, likes, shares, comments, post_url. For YouTube, the upstream shares value maps to the unified shares position. - Filter out rows with NULL created_timestamp. - Apply recent data windows relative to the current date: - LinkedIn: keep the last 4 years. - All other platforms: keep the last 2 years. - Standardize content fields: - post_message: default NULL to empty string "". - post_url: default NULL to empty string "". - Standardize metric fields (clicks, impressions, likes, shares, comments): default NULL to 0; no aggregation or deduplication is performed. - Compute engagement_rate: - If impressions > 0: (clicks + likes + shares + comments) / impressions. - Otherwise: 0.0. - No rounding or capping; always non-null and may exceed 1.0. - Compute content_quality_score by platform: - facebook: 75 if impressions > 0, else 50. - instagram: 90 if impressions > 0, else 50. - twitter: 80 if impressions > 0, else 50. - youtube: 95 if clicks > 0, else 50. - linkedin: 70 if impressions > 0, else 50. - Rankings (computed after the above filtering): - daily_platform_rank: within each platform and calendar day of created_timestamp, assign a 1-based rank by sorting impressions descending; ties get arbitrary order. - platform_lifetime_rank: within each platform across the filtered dataset, assign a 1-based rank by sorting impressions descending; ties get arbitrary order. - Final result ordering for display: created_timestamp descending, then engagement_rate descending.'
      columns:
      - name: page_id
        data_type: VARCHAR
        description: Source page/account identifier within a platform
        tests:
        - not_null
      - name: page_name
        data_type: VARCHAR
        description: Source page/account display name; may be null
      - name: post_id
        data_type: VARCHAR
        description: Source post/media identifier within platform and page
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_social_media_reporting__rollup_report:daily_platform_rank`。

## 点：platform_lifetime_rank

类别：**其他**；角色：同类候选；把握：中。

契约允许并列键的任意行次序；024诊断核对并列组及排除相应派生列后的其他内容。该列单独列点，但没有独立单改收益，不用成组清零冒充该列清零。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_extra_diagnostics.json`，条目 `排除并列顺序派生列后的整表诊断`。

基线：L0=260行/307格; L1=260行/307格; L2=260行/307格; L3=260行/307格。

只有成组诊断：排除 ['daily_platform_rank', 'platform_lifetime_rank'] 后 L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格；没有该列独立单改收益。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。event1完整看到允许并列规则；交付报告没交代本处，写窗口实现不等于意识到另一个合法顺序。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
      - intermediate.social_media_reporting__twitter_posts_reporting
      - intermediate.social_media_reporting__youtube_videos_reporting
      business_logic: '- Union all five platform models with a platform label: facebook, instagram, linkedin, twitter, youtube; select page_id, page_name, post_id, post_message, created_timestamp, clicks, impressions, likes, shares, comments, post_url. For YouTube, the upstream shares value maps to the unified shares position. - Filter out rows with NULL created_timestamp. - Apply recent data windows relative to the current date: - LinkedIn: keep the last 4 years. - All other platforms: keep the last 2 years. - Standardize content fields: - post_message: default NULL to empty string "". - post_url: default NULL to empty string "". - Standardize metric fields (clicks, impressions, likes, shares, comments): default NULL to 0; no aggregation or deduplication is performed. - Compute engagement_rate: - If impressions > 0: (clicks + likes + shares + comments) / impressions. - Otherwise: 0.0. - No rounding or capping; always non-null and may exceed 1.0. - Compute content_quality_score by platform: - facebook: 75 if impressions > 0, else 50. - instagram: 90 if impressions > 0, else 50. - twitter: 80 if impressions > 0, else 50. - youtube: 95 if clicks > 0, else 50. - linkedin: 70 if impressions > 0, else 50. - Rankings (computed after the above filtering): - daily_platform_rank: within each platform and calendar day of created_timestamp, assign a 1-based rank by sorting impressions descending; ties get arbitrary order. - platform_lifetime_rank: within each platform across the filtered dataset, assign a 1-based rank by sorting impressions descending; ties get arbitrary order. - Final result ordering for display: created_timestamp descending, then engagement_rate descending.'
      columns:
      - name: page_id
        data_type: VARCHAR
        description: Source page/account identifier within a platform
        tests:
        - not_null
      - name: page_name
        data_type: VARCHAR
        description: Source page/account display name; may be null
      - name: post_id
        data_type: VARCHAR
        description: Source post/media identifier within platform and page
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_social_media_reporting__rollup_report:platform_lifetime_rank`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。

只可定同类主因，不能报告这几列的完整单改名次；采用手册第7节同类候选例外。
