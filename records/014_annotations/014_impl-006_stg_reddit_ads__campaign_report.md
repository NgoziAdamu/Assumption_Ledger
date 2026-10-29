# impl-006 / stg_reddit_ads__campaign_report

## 1. 错在哪里

1200行中20个指标均不一致；多列直接填NULL，spend映射候选被重复字典键覆盖，单项原因并列且类别边界未明确。

已核实：1200行、20个比较指标不一致，总计24000个列差异。17个表达式为NULL占位，3个取raw预计算ctr/cpc/ecpm；每个表达式单独修复，均减少1200个列差异，仍有1200整行不同。event 19的special字典先写spend候选[spend,local_spend_amount]、后又以同名键覆盖为[local_spend_amount]，最终漏掉实际存在且1200行非空的spend。归因判断：主要X。D是多列占位的强候选；但此轨迹同时存在字段查找/误判机制，不能证明所有NULL都属于“没有误解数据”。spend可能是I，但手册要求从思考/报告看出正确想法，不能仅靠重复字典键推断。U即使满足前三项，单项修复也达不到第4项。

## 2. 依据

- 起点：[013精简包](../013_packages/013_impl-006_staging_stg_reddit_ads__campaign_report.md)。原013状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，第1092–1148行。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_reddit_ads__campaign_report.sql`；gold SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_reddit_ads__campaign_report.sql`。精简包完整收录；下列补丁逐字给出定位原文。
- [完整事件记录](../014_trace_impl-006.json)；事件文件在该JSON的path中，可回查traces/dacomp_deimpl_prev.tar.gz。
- [查询原文与结果](../014_queries_impl-006.json)、[全部重跑记录](../014_reruns_impl-006.json)。

### SQL行号定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_reddit_ads__campaign_report.sql`
```text
12:         CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend,
13:         CAST(NULL::INTEGER AS INTEGER) AS video_views,
14:         CAST(NULL::DECIMAL(8,4) AS DECIMAL(8,4)) AS video_view_rate,
15:         CAST(NULL::INTEGER AS INTEGER) AS upvotes,
16:         CAST(NULL::INTEGER AS INTEGER) AS downvotes,
17:         CAST(NULL::INTEGER AS INTEGER) AS comments,
18:         CAST(NULL::INTEGER AS INTEGER) AS shares,
19:         CAST(NULL::INTEGER AS INTEGER) AS saves,
20:         CAST(NULL::INTEGER AS INTEGER) AS post_visits,
21:         CAST(NULL::INTEGER AS INTEGER) AS profile_visits,
22:         CAST(NULL::INTEGER AS INTEGER) AS community_joins,
23:         CAST(NULL::INTEGER AS INTEGER) AS conversions,
24:         CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS conversion_value,
25:         TRY_CAST("ctr" AS DOUBLE) AS click_through_rate,
26:         TRY_CAST("cpc" AS DOUBLE) AS cost_per_click,
27:         TRY_CAST("ecpm" AS DOUBLE) AS cost_per_thousand_impressions,
28:         CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_video_view,
29:         CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion,
30:         CAST(NULL::INTEGER AS INTEGER) AS total_engagements,
31:         CAST(NULL::DOUBLE AS DOUBLE) AS engagement_rate,
```

gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_reddit_ads__campaign_report.sql`
```text
19:     CAST(spend AS DECIMAL(18,2)) AS spend,
22:     CAST(COALESCE(video_started, '0') AS INTEGER) AS video_views,
24:     CAST(COALESCE(comment_upvotes, '0') AS INTEGER) AS upvotes,
25:     CAST(COALESCE(comment_downvotes, '0') AS INTEGER) AS downvotes,
26:     CAST(COALESCE(viewer_comments, '0') AS INTEGER) AS comments,
44:         WHEN clicks > 0 THEN ROUND(spend / clicks, 2)
49:         WHEN impressions > 0 THEN ROUND((spend / impressions) * 1000, 2)
54:         WHEN CAST(COALESCE(video_started, '0') AS INTEGER) > 0 THEN ROUND(spend / CAST(COALESCE(video_started, '0') AS INTEGER), 2)
59:         WHEN 0 > 0 THEN ROUND(spend / 0, 2)
64:     (CAST(COALESCE(comment_upvotes, '0') AS INTEGER) + CAST(COALESCE(comment_downvotes, '0') AS INTEGER) + CAST(COALESCE(viewer_comments, '0') AS INTEGER) + 0) AS total_engagements,
67:         WHEN impressions > 0 THEN ROUND((CAST((CAST(COALESCE(comment_upvotes, '0') AS INTEGER) + CAST(COALESCE(comment_downvotes, '0') AS INTEGER) + CAST(COALESCE(viewer_comments, '0') AS INTEGER) + 0) AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
```

## 3. agent看过什么

event 17→18输出raw列信息；event 19程序读取所有raw schema后生成表达式；event 95报告明确披露缺源字段采用类型化NULL及非完整业务实现。V1证明spend/video_started/comment_upvotes可用。未找到逐指标的明确业务口径说明或正确意图陈述。

已逐题核对event 1 message，包含本表契约完整原文；这不是把磁盘上存在的文档等同于agent已经阅读。schema输出、源数据值、运行日志分别处理。轨迹全量转录未删去截断标记；被截断的未显示部分不作为看到的证据。

## 4. 查询与重跑

核实查询实际执行 **1条**；核实代价：**一条查询**。诊断查询不计入5条限制。重复执行的查询仍计数。

### V1：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(spend) spend_present,count(video_started) video_present,count(comment_upvotes) upvotes_present,count(*) FILTER(WHERE try_cast(ctr AS DOUBLE) IS DISTINCT FROM round(100.0*clicks/nullif(impressions,0),4)) ctr_different FROM raw.reddit_ads_campaign_report_data
```

结果：
```json
{
  "columns": [
    "n",
    "spend_present",
    "video_present",
    "upvotes_present",
    "ctr_different"
  ],
  "rows": [
    [
      1200,
      1200,
      1200,
      1200,
      1200
    ]
  ]
}
```

### D1：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(spend) spend_present,count(video_started) video_present,count(comment_upvotes) upvotes_present,count(*) FILTER(WHERE try_cast(ctr AS DOUBLE) IS DISTINCT FROM round(100.0*clicks/nullif(impressions,0),4)) ctr_different FROM raw.reddit_ads_campaign_report_data
```

结果：
```json
{
  "columns": [
    "n",
    "spend_present",
    "video_present",
    "upvotes_present",
    "ctr_different"
  ],
  "rows": [
    [
      1200,
      1200,
      1200,
      1200,
      1200
    ]
  ]
}
```

### D_raw：诊断查询

数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb']`

```sql
SELECT * FROM raw.reddit_ads_campaign_report_data
```

结果：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 1200,
    "gold_rows": 1200,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 比较口径

原件均READ_ONLY；只把本节点引用表复制到data/014_work私有DuckDB后执行。staging输入来自agent留存库raw；003/008上游直接复制gold，实现CS。固定原评分的comparison_columns与key_columns；L0为lower/trim/NULL规范化，L1数字及布尔归一，L2数值两位小数，L3再放宽日期时间到日期。键始终固定L0，不在宽松档位重新归一。

无共同键时逐列0表示无可比较行，不表示一致。重复键按值/行多重集合抵消，报告最少不一致对数；同时公开额外行次数。为避免键被漏出整表判断，含键整表匹配用于本次U4；旧007式仅值列整表匹配并列展示。这里没有重定义原官方对错或修改旧状态。

比较列：`['account_id', 'campaign_id', 'click_through_rate', 'clicks', 'comments', 'community_joins', 'conversion_value', 'conversions', 'cost_per_click', 'cost_per_conversion', 'cost_per_thousand_impressions', 'cost_per_video_view', 'date_day', 'downvotes', 'engagement_rate', 'impressions', 'platform', 'post_visits', 'profile_visits', 'saves', 'shares', 'spend', 'total_engagements', 'upvotes', 'video_view_rate', 'video_views']`；键：`['campaign_id']`。

### 留存基线（013材料来源）

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：baseline

不改SQL；建立本轮相同引擎、相同输入的比较基线。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：spend

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
替换为：
```sql
CAST(spend AS DECIMAL(18,2)) AS spend
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|0|0|0|0|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：video_views

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS video_views
```
替换为：
```sql
CAST(COALESCE(video_started, '0') AS INTEGER) AS video_views
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|0|0|0|0|

### 重跑：video_view_rate

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::DECIMAL(8,4) AS DECIMAL(8,4)) AS video_view_rate
```
替换为：
```sql
CAST(0 AS DECIMAL(8,4)) AS video_view_rate
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|0|0|0|0|
|video_views|1200|1200|1200|1200|

### 重跑：upvotes

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS upvotes
```
替换为：
```sql
CAST(COALESCE(comment_upvotes, '0') AS INTEGER) AS upvotes
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|0|0|0|0|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：downvotes

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS downvotes
```
替换为：
```sql
CAST(COALESCE(comment_downvotes, '0') AS INTEGER) AS downvotes
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|0|0|0|0|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：comments

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS comments
```
替换为：
```sql
CAST(COALESCE(viewer_comments, '0') AS INTEGER) AS comments
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|0|0|0|0|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：shares

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS shares
```
替换为：
```sql
CAST(0 AS INTEGER) AS shares
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|0|0|0|0|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：saves

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS saves
```
替换为：
```sql
CAST(0 AS INTEGER) AS saves
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|0|0|0|0|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：post_visits

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS post_visits
```
替换为：
```sql
CAST(0 AS INTEGER) AS post_visits
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|0|0|0|0|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：profile_visits

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS profile_visits
```
替换为：
```sql
CAST(0 AS INTEGER) AS profile_visits
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|0|0|0|0|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：community_joins

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS community_joins
```
替换为：
```sql
CAST(0 AS INTEGER) AS community_joins
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|0|0|0|0|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：conversions

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS conversions
```
替换为：
```sql
CAST(0 AS INTEGER) AS conversions
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|0|0|0|0|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：conversion_value

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS conversion_value
```
替换为：
```sql
CAST(0 AS DECIMAL(18,2)) AS conversion_value
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|0|0|0|0|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：cost_per_video_view

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_video_view
```
替换为：
```sql
CASE WHEN CAST(COALESCE(video_started, '0') AS INTEGER)>0 THEN ROUND(spend/CAST(COALESCE(video_started, '0') AS INTEGER),2) ELSE 0 END AS cost_per_video_view
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|0|0|0|0|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：cost_per_conversion

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion
```
替换为：
```sql
0::DOUBLE AS cost_per_conversion
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|0|0|0|0|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：total_engagements

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS total_engagements
```
替换为：
```sql
(CAST(COALESCE(comment_upvotes, '0') AS INTEGER)+CAST(COALESCE(comment_downvotes, '0') AS INTEGER)+CAST(COALESCE(viewer_comments, '0') AS INTEGER)) AS total_engagements
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|0|0|0|0|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：engagement_rate

只替换以下原文（其余字节经验证不变）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS engagement_rate
```
替换为：
```sql
CASE WHEN impressions>0 THEN ROUND(CAST((CAST(COALESCE(comment_upvotes, '0') AS INTEGER)+CAST(COALESCE(comment_downvotes, '0') AS INTEGER)+CAST(COALESCE(viewer_comments, '0') AS INTEGER)) AS DECIMAL)/CAST(impressions AS DECIMAL)*100,4) ELSE 0 END AS engagement_rate
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|0|0|0|0|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：click_through_rate

只替换以下原文（其余字节经验证不变）：
```sql
TRY_CAST("ctr" AS DOUBLE)
```
替换为：
```sql
CASE WHEN impressions>0 THEN ROUND(CAST(clicks AS DECIMAL)/CAST(impressions AS DECIMAL)*100,4) ELSE 0 END
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|0|0|0|0|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：cost_per_click

只替换以下原文（其余字节经验证不变）：
```sql
TRY_CAST("cpc" AS DOUBLE)
```
替换为：
```sql
CASE WHEN clicks>0 THEN ROUND(spend/clicks,2) ELSE 0 END
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|0|0|0|0|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑：cost_per_thousand_impressions

只替换以下原文（其余字节经验证不变）：
```sql
TRY_CAST("ecpm" AS DOUBLE)
```
替换为：
```sql
CASE WHEN impressions>0 THEN ROUND(spend/impressions*1000,2) ELSE 0 END
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L1|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L2|1200|1200|0|0|1200|0/0|1200/1200|False|False|
|L3|1200|1200|0|0|1200|0/0|1200/1200|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|0|0|0|0|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### gold SQL在同一私有输入上的诊断

这是诊断，不是局部修复，也不用于证明U4。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1200|1200|0|0|0|0/0|0/0|True|True|
|L1|1200|1200|0|0|0|0/0|0/0|True|True|
|L2|1200|1200|0|0|0|0/0|0/0|True|True|
|L3|1200|1200|0|0|0|0/0|0/0|True|True|

含键整表首次匹配档位：**L0**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|0|0|0|0|
|clicks|0|0|0|0|
|comments|0|0|0|0|
|community_joins|0|0|0|0|
|conversion_value|0|0|0|0|
|conversions|0|0|0|0|
|cost_per_click|0|0|0|0|
|cost_per_conversion|0|0|0|0|
|cost_per_thousand_impressions|0|0|0|0|
|cost_per_video_view|0|0|0|0|
|date_day|0|0|0|0|
|downvotes|0|0|0|0|
|engagement_rate|0|0|0|0|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|0|0|0|0|
|profile_visits|0|0|0|0|
|saves|0|0|0|0|
|shares|0|0|0|0|
|spend|0|0|0|0|
|total_engagements|0|0|0|0|
|upvotes|0|0|0|0|
|video_view_rate|0|0|0|0|
|video_views|0|0|0|0|

## 5. 类别和把握

- 主要原因：**X**（归因判断）。
- 参与因素：D候选（NULL占位）；X（spend候选覆盖与指标口径）。
- 标记：已披露。
- 把握：**低**。
- 重跑是否满足U第4条件：否（每次单列修复仅减少1/20列差异，整行不变）。

候选P：spend没有可用来源。V1反证；相关schema已出现。只修spend不满足U4。其他别名是否应映射及预计算指标是否应重算，契约只列输出类型，不能仅靠gold确定业务含义。

## 规则问题

本表20个单项修复在列差异减少上完全并列、在整行差异减少上全为0；手册没有并列规则。可读为D主因（占位最多）、I主因（重复字典键）、或U（误判字段不可用但U4不满足）。暂选X，不合并20处修改去人为满足U4；D/其他均是候选而非已定参与类别。“已披露”只表示event95确有披露，不意味着D已定。

共同问题：手册第1节“不预设类别分布”与末句“希望未核实假设多”存在张力；本次以逐条证据条件为准，不按期望调整分布。U3“没看过任何足以判断P的东西”与“证据曾出现但被忽略仍归U”按后者作为例外解释。
