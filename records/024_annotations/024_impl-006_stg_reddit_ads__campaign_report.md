# impl-006 · stg_reddit_ads__campaign_report

用途：**校准**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**多因并列（A、D、I）**；把握：中。

20处各减少1200格；spend字典被覆盖I，四个可映射原指标直接NULL为D，其余未定口径/默认值为A。

参与因素：无。
标记：已披露。

## 材料与比较口径

[013_impl-006_staging_stg_reddit_ads__campaign_report.md](../013_packages/013_impl-006_staging_stg_reddit_ads__campaign_report.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`。

```text
1092:     - name: "stg_reddit_ads__campaign_report"
1093:       description: "Staging table for Reddit Ads  Campaign Report"
1094:       columns:
1095:         - name: "platform"
1096:           data_type: VARCHAR
1097:         - name: "campaign_id"
1098:           data_type: VARCHAR
1099:         - name: "date_day"
1100:           data_type: DATE
1101:         - name: "account_id"
1102:           data_type: VARCHAR
1103:         - name: "impressions"
1104:           data_type: INTEGER
1105:         - name: "clicks"
1106:           data_type: INTEGER
1107:         - name: "spend"
1108:           data_type: DECIMAL(18,2)
1109:         - name: "video_views"
1110:           data_type: INTEGER
1111:         - name: "video_view_rate"
1112:           data_type: DECIMAL(8,4)
1113:         - name: "upvotes"
1114:           data_type: INTEGER
1115:         - name: "downvotes"
1116:           data_type: INTEGER
1117:         - name: "comments"
1118:           data_type: INTEGER
1119:         - name: "shares"
1120:           data_type: INTEGER
1121:         - name: "saves"
1122:           data_type: INTEGER
1123:         - name: "post_visits"
1124:           data_type: INTEGER
1125:         - name: "profile_visits"
1126:           data_type: INTEGER
1127:         - name: "community_joins"
1128:           data_type: INTEGER
1129:         - name: "conversions"
1130:           data_type: INTEGER
1131:         - name: "conversion_value"
1132:           data_type: DECIMAL(18,2)
1133:         - name: "click_through_rate"
1134:           data_type: DOUBLE
1135:         - name: "cost_per_click"
1136:           data_type: DOUBLE
1137:         - name: "cost_per_thousand_impressions"
1138:           data_type: DOUBLE
1139:         - name: "cost_per_video_view"
1140:           data_type: DOUBLE
1141:         - name: "cost_per_conversion"
1142:           data_type: DOUBLE
1143:         - name: "total_engagements"
1144:           data_type: INTEGER
1145:         - name: "engagement_rate"
1146:           data_type: DOUBLE
1147:         - name: "_dbt_loaded_at"
1148:           data_type: TIMESTAMP WITH TIME ZONE
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_reddit_ads__campaign_report.sql`；SHA-256 `5f29b62488b3998f55c87dc9ebcefa3057672fed9544e110f91ffc29094c7cd2`。

```text
1: WITH source_rows AS (
2:     SELECT * FROM raw.reddit_ads_campaign_report_data
3: ),
4: cleaned AS (
5:     SELECT
6:         'REDDIT_ADS' AS platform,
7:         CAST(TRY_CAST("campaign_id" AS VARCHAR) AS VARCHAR) AS campaign_id,
8:         CAST(TRY_CAST(date AS DATE) AS DATE) AS date_day,
9:         TRY_CAST("account_id" AS VARCHAR) AS account_id,
10:         CAST(TRY_CAST("impressions" AS BIGINT) AS INTEGER) AS impressions,
11:         CAST(TRY_CAST("clicks" AS BIGINT) AS INTEGER) AS clicks,
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
32:         CURRENT_TIMESTAMP AS _dbt_loaded_at
33:     FROM source_rows
34: )
35: SELECT * FROM cleaned
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_reddit_ads__campaign_report.sql`；SHA-256 `9225c02d25f83666be8da2b9240a040768f78877f2106942b5c5e32cf9305161`。

```text
1: -- Reddit Ads Campaign Report Staging Model
2: -- Standardizes raw Reddit Ads campaign-level data for downstream consumption
3: -- Removes Fivetran-specific logic and converts to DuckDB-compatible SQL
4: 
5: SELECT 
6:     -- Platform Identifier
7:     'reddit_ads' AS platform,
8:     
9:     -- Primary Keys
10:     CAST(campaign_id AS VARCHAR) AS campaign_id,
11:     CAST(date AS DATE) AS date_day,
12:     
13:     -- Campaign Attributes
14:     CAST(account_id AS VARCHAR) AS account_id,
15:     
16:     -- Performance Metrics
17:     CAST(impressions AS INTEGER) AS impressions,
18:     CAST(clicks AS INTEGER) AS clicks,
19:     CAST(spend AS DECIMAL(18,2)) AS spend,
20:     
21:     -- Reddit-specific Metrics (using available columns)
22:     CAST(COALESCE(video_started, '0') AS INTEGER) AS video_views,
23:     CAST(0 AS DECIMAL(8,4)) AS video_view_rate,
24:     CAST(COALESCE(comment_upvotes, '0') AS INTEGER) AS upvotes,
25:     CAST(COALESCE(comment_downvotes, '0') AS INTEGER) AS downvotes,
26:     CAST(COALESCE(viewer_comments, '0') AS INTEGER) AS comments,
27:     CAST(0 AS INTEGER) AS shares,
28:     CAST(0 AS INTEGER) AS saves,
29:     CAST(0 AS INTEGER) AS post_visits,
30:     CAST(0 AS INTEGER) AS profile_visits,
31:     CAST(0 AS INTEGER) AS community_joins,
32:     
33:     -- Conversion Metrics (using available columns)
34:     CAST(0 AS INTEGER) AS conversions,
35:     CAST(0 AS DECIMAL(18,2)) AS conversion_value,
36:     
37:     -- Calculated Metrics
38:     CASE 
39:         WHEN impressions > 0 THEN ROUND((CAST(clicks AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
40:         ELSE 0 
41:     END AS click_through_rate,
42:     
43:     CASE 
44:         WHEN clicks > 0 THEN ROUND(spend / clicks, 2)
45:         ELSE 0 
46:     END AS cost_per_click,
47:     
48:     CASE 
49:         WHEN impressions > 0 THEN ROUND((spend / impressions) * 1000, 2)
50:         ELSE 0 
51:     END AS cost_per_thousand_impressions,
52:     
53:     CASE 
54:         WHEN CAST(COALESCE(video_started, '0') AS INTEGER) > 0 THEN ROUND(spend / CAST(COALESCE(video_started, '0') AS INTEGER), 2)
55:         ELSE 0 
56:     END AS cost_per_video_view,
57:     
58:     CASE 
59:         WHEN 0 > 0 THEN ROUND(spend / 0, 2)
60:         ELSE 0 
61:     END AS cost_per_conversion,
62:     
63:     -- Engagement Metrics
64:     (CAST(COALESCE(comment_upvotes, '0') AS INTEGER) + CAST(COALESCE(comment_downvotes, '0') AS INTEGER) + CAST(COALESCE(viewer_comments, '0') AS INTEGER) + 0) AS total_engagements,
65:     
66:     CASE 
67:         WHEN impressions > 0 THEN ROUND((CAST((CAST(COALESCE(comment_upvotes, '0') AS INTEGER) + CAST(COALESCE(comment_downvotes, '0') AS INTEGER) + CAST(COALESCE(viewer_comments, '0') AS INTEGER) + 0) AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
68:         ELSE 0 
69:     END AS engagement_rate,
70:     
71:     -- Data Quality
72:     CURRENT_TIMESTAMP AS _dbt_loaded_at
73: 
74: FROM raw.reddit_ads_campaign_report_data
75: 
76: WHERE date IS NOT NULL
77:     AND campaign_id IS NOT NULL
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- spend（I）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- video_views（D）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- video_view_rate（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- upvotes（D）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- downvotes（D）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- comments（D）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- shares（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- saves（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- post_visits（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- profile_visits（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- community_joins（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- conversions（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- conversion_value（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- click_through_rate（A）：**看到了但没提**；事件 18、30。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。

- cost_per_click（A）：**看到了但没提**；事件 18、30。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。

- cost_per_thousand_impressions（A）：**看到了但没提**；事件 18、30。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。

- cost_per_video_view（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- cost_per_conversion（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- total_engagements（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```


- engagement_rate（A）：**只有通用策略说明**；事件 18、19、30、95。
原句：

```
对缺失源字段采用类型明确的 NULL
```

event 18：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/18.json`；原始观察输出。
event 19：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/19.json`；命令首行：`mkdir -p sql/{staging,intermediate,marts} && cat > /tmp/gen.py <<'PY'`。
event 30：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/30.json`；原始观察输出。
event 95：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/95.json`；命令首行：`cat > result.md <<'EOF'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

已创建 `sql/staging/`、`sql/intermediate/` 和 `sql/marts/` 中的 SQL 文件，文件名与 contract / layer dependency 配置一致，共 53 个 SQL 文件（26 staging、14 intermediate、13 marts）。所有配置执行的模型均通过 `run.py` 的 DuckDB 执行，输出表列名逐项与 YAML 列定义比对一致。

验证结果：
- `python run.py` 成功：staging 20/20、intermediate 14/14、marts 13/13。
- `layer_dependencies.yaml` 执行清单中的所有模型均已生成。文档列出的 Google Ads stats staging 表未列入运行依赖清单，因此未配置为 pipeline 执行模型。
- 所有 SQL 文件不以分号结束，且无 dbt `ref()`。
- 脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。没有统一去重，以保留契约要求的重复行。

契约边界和限制：合同中部分字段与原始来源列类型/名称不匹配，或来源不可用（例如加载时间字段、部分跨平台字段）。对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。`int_ad_reporting__country_mapping` 由于契约没有给出完整静态列举值，目前为单行静态占位映射，不能代表全量国家覆盖。

重要限制：虽然 SQL 完整可执行且列结构匹配，若干大型 intermediate/marts 复杂模型因源字段缺失或合同映射歧义，当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。运行验证证明 SQL 和结构有效，不应视为这些复杂分析结果已通过业务准确性验证。

曾遇到的问题及修复：原始字符串转 DECIMAL/INTEGER 报错，已使用 `TRY_CAST`；SQL 尾随分号及原始依赖列表解析问题已修正；统一指标模型对 LinkedIn 原始列映射不匹配已调整。最终 `run.py` 无失败 SQL。
```

## 查询

核实查询 **2** 条；代价档：**多条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：Reddit 原始列
[024_calibration_queries.json](../024_calibration_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name='reddit_ads_campaign_report_data' ORDER BY ordinal_position
```


```json
{"columns":["column_name","data_type"],"rows":[["account_id","VARCHAR"],["campaign_id","VARCHAR"],["date","VARCHAR"],["app_install_metrics_add_payment_info","VARCHAR"],["app_install_metrics_add_to_cart","VARCHAR"],["app_install_metrics_app_launch","VARCHAR"],["app_install_metrics_completed_tutorial","VARCHAR"],["app_install_metrics_install","VARCHAR"],["app_install_metrics_level_achieved","VARCHAR"],["app_install_metrics_purchase","VARCHAR"],["app_install_metrics_search","VARCHAR"],["app_install_metrics_sign_up","VARCHAR"],["app_install_metrics_spend","DOUBLE"],["app_install_metrics_spend_credits","DOUBLE"],["app_install_metrics_view_content","VARCHAR"],["clicks","BIGINT"],["comment_downvotes","BIGINT"],["comment_upvotes","BIGINT"],["comments_page_views","BIGINT"],["conversion_roas","VARCHAR"],["cpc","VARCHAR"],["ctr","VARCHAR"],["ecpm","VARCHAR"],["gallery_item_caption","VARCHAR"],["gallery_item_id","VARCHAR"],["impressions","BIGINT"],["legacy_click_conversions_attribution_window_day","VARCHAR"],["legacy_click_conversions_attribution_window_month","VARCHAR"],["legacy_click_conversions_attribution_window_week","VARCHAR"],["legacy_view_conversions_attribution_window_day","VARCHAR"],["legacy_view_conversions_attribution_window_month","VARCHAR"],["legacy_view_conversions_attribution_window_week","VARCHAR"],["priority","VARCHAR"],["region","VARCHAR"],["spend","DOUBLE"],["video_fully_viewable_impressions","VARCHAR"],["video_plays_expanded","VARCHAR"],["video_plays_with_sound","VARCHAR"],["video_started","BIGINT"],["video_viewable_impressions","VARCHAR"],["video_watched_100_percent","VARCHAR"],["video_watched_10_seconds","VARCHAR"],["video_watched_25_percent","VARCHAR"],["video_watched_3_seconds","VARCHAR"],["video_watched_50_percent","VARCHAR"],["video_watched_5_seconds","VARCHAR"],["video_watched_75_percent","VARCHAR"],["video_watched_95_percent","VARCHAR"],["viewable_impressions","VARCHAR"],["viewer_comments","BIGINT"]]}
```


### 核实：候选指标可用性
[024_calibration_queries.json](../024_calibration_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`。

```sql
SELECT count(*) n,count(spend) spend_n,count(video_started) video_n,count(comment_upvotes) up_n,count(comment_downvotes) down_n,count(viewer_comments) comments_n,count(try_cast(ctr AS DOUBLE)) ctr_numeric,count(try_cast(cpc AS DOUBLE)) cpc_numeric,count(try_cast(ecpm AS DOUBLE)) ecpm_numeric,count(*) FILTER(WHERE date IS NULL OR campaign_id IS NULL) missing_keys FROM raw.reddit_ads_campaign_report_data
```


```json
{"columns":["n","spend_n","video_n","up_n","down_n","comments_n","ctr_numeric","cpc_numeric","ecpm_numeric","missing_keys"],"rows":[[1200,1200,1200,1200,1200,1200,0,0,0,0]]}
```

## 独立单点重跑

### 024_reruns_impl-006_stg_reddit_ads__campaign_report.json
[024_reruns_impl-006_stg_reddit_ads__campaign_report.json](../024_reruns_impl-006_stg_reddit_ads__campaign_report.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-12 00:00:00+00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-12'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|24000|否|
|L1|1200|1200|1200|24000|否|
|L2|1200|1200|1200|24000|否|
|L3|1200|1200|1200|24000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### baseline
私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/baseline.sql`；SHA-256 `9491f353d07ae37babf57470211e9375ea02233e40cf84d1734fffec1c82b2bc`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|24000|否|
|L1|1200|1200|1200|24000|否|
|L2|1200|1200|1200|24000|否|
|L3|1200|1200|1200|24000|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### spend
主因；类别候选I。生成字典先正确映射spend后被重复key覆盖
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第12行、offset 476起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```

修改后：
```sql
CAST(spend AS DECIMAL(18, 2)) AS spend
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/spend.sql`；SHA-256 `048244946dda63fc69c87c57f73e279efe62f9e340574f0bca145f011cd3a289`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### video_views
主因；类别候选D。有明确可用原始候选列却直接NULL
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第13行、offset 537起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS video_views
```

修改后：
```sql
CAST(COALESCE(video_started, '0') AS INT) AS video_views
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/video_views.sql`；SHA-256 `5b0b19e1e49f4d7b42ade6eedc15494cc3ae610e99404b49fbc330e8bfa16bdf`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200}`

#### video_view_rate
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第14行、offset 592起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::DECIMAL(8,4) AS DECIMAL(8,4)) AS video_view_rate
```

修改后：
```sql
CAST(0 AS DECIMAL(8, 4)) AS video_view_rate
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/video_view_rate.sql`；SHA-256 `e4fe09e02ac2c4553f430c0d82a75302b4f2f761eccd0e7d125ab4a8f7c3bbc7`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_views":1200}`

#### upvotes
主因；类别候选D。有明确可用原始候选列却直接NULL
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第15行、offset 661起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS upvotes
```

修改后：
```sql
CAST(COALESCE(comment_upvotes, '0') AS INT) AS upvotes
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/upvotes.sql`；SHA-256 `385c3f6d2f4c598301472f6268a57639fa046d622a3faad6d55d0a3d0b7880b4`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"video_view_rate":1200,"video_views":1200}`

#### downvotes
主因；类别候选D。有明确可用原始候选列却直接NULL
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第16行、offset 712起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS downvotes
```

修改后：
```sql
CAST(COALESCE(comment_downvotes, '0') AS INT) AS downvotes
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/downvotes.sql`；SHA-256 `7da0dc691f298746c433d27685c1940156b6e92386eb3ae78af354f824fdabe6`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### comments
主因；类别候选D。有明确可用原始候选列却直接NULL
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第17行、offset 765起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS comments
```

修改后：
```sql
CAST(COALESCE(viewer_comments, '0') AS INT) AS comments
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/comments.sql`；SHA-256 `d50a46d3343627af783d0d3d2b3149c2c78a8e5a70fe272191972190fb593540`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### shares
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第18行、offset 817起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS shares
```

修改后：
```sql
CAST(0 AS INT) AS shares
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/shares.sql`；SHA-256 `8c27bb4244c547a44ba3994d3abd52e776e7e10987960bcb0a49a3ea937f777b`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### saves
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第19行、offset 867起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS saves
```

修改后：
```sql
CAST(0 AS INT) AS saves
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/saves.sql`；SHA-256 `93758d4680a27f080a0b1a5025dc26b564a8b8e5629ba637b4bf5d183aa18433`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### post_visits
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第20行、offset 916起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS post_visits
```

修改后：
```sql
CAST(0 AS INT) AS post_visits
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/post_visits.sql`；SHA-256 `9f5c67113c56bb073c268e0f8362aa11c1963893457ee481f6c6328a27168f2b`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### profile_visits
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第21行、offset 971起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS profile_visits
```

修改后：
```sql
CAST(0 AS INT) AS profile_visits
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/profile_visits.sql`；SHA-256 `ed59a76a0aca63209a09cfae97e6f612cee2fe17e732fcd5aa3880f66c41b437`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### community_joins
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第22行、offset 1029起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS community_joins
```

修改后：
```sql
CAST(0 AS INT) AS community_joins
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/community_joins.sql`；SHA-256 `0a472b94e391dbb027ee3a16ea8814b89c3ce345ad750176931c22d40edc70c6`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### conversions
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第23行、offset 1088起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS conversions
```

修改后：
```sql
CAST(0 AS INT) AS conversions
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/conversions.sql`；SHA-256 `aded06c797187989e6b94472777bf30ec17e6c7a4dd4e3b38617767f1d48f670`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### conversion_value
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第24行、offset 1143起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS conversion_value
```

修改后：
```sql
CAST(0 AS DECIMAL(18, 2)) AS conversion_value
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/conversion_value.sql`；SHA-256 `8fd73157c761bec2c2ac9b78961631b3f22ab1e5c585945e2458effe85891c5e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### click_through_rate
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第25行、offset 1215起替换；其他字节相同。
原表达式：
```sql
TRY_CAST("ctr" AS DOUBLE) AS click_through_rate
```

修改后：
```sql
CASE WHEN impressions > 0 THEN ROUND((CAST(clicks AS DECIMAL(18, 3)) / CAST(impressions AS DECIMAL(18, 3))) * 100, 4) ELSE 0 END AS click_through_rate
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/click_through_rate.sql`；SHA-256 `5a524dcba0035673cb6c7f946c0aa3da7354e5bb543e4861618901fab40dd31f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### cost_per_click
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第26行、offset 1272起替换；其他字节相同。
原表达式：
```sql
TRY_CAST("cpc" AS DOUBLE) AS cost_per_click
```

修改后：
```sql
CASE WHEN clicks > 0 THEN ROUND(spend / clicks, 2) ELSE 0 END AS cost_per_click
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/cost_per_click.sql`；SHA-256 `ddd37620a402d589bd5a1e5044451f88dd0ac53f1b94cf3f928c66fa2973b222`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### cost_per_thousand_impressions
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第27行、offset 1325起替换；其他字节相同。
原表达式：
```sql
TRY_CAST("ecpm" AS DOUBLE) AS cost_per_thousand_impressions
```

修改后：
```sql
CASE WHEN impressions > 0 THEN ROUND((spend / impressions) * 1000, 2) ELSE 0 END AS cost_per_thousand_impressions
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/cost_per_thousand_impressions.sql`；SHA-256 `037768242ecd30b10f49bb0b3aea42e85a674bceb0093a73780f12c46d3a8073`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### cost_per_video_view
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第28行、offset 1394起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_video_view
```

修改后：
```sql
CASE WHEN CAST(COALESCE(video_started, '0') AS INT) > 0 THEN ROUND(spend / CAST(COALESCE(video_started, '0') AS INT), 2) ELSE 0 END AS cost_per_video_view
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/cost_per_video_view.sql`；SHA-256 `5f2b929ba7c432a9ee521acf0c51c8067cf5cf7681a34e8ee5d487d9ebb963f0`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### cost_per_conversion
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第29行、offset 1455起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion
```

修改后：
```sql
CASE WHEN 0 > 0 THEN ROUND(spend / 0, 2) ELSE 0 END AS cost_per_conversion
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/cost_per_conversion.sql`；SHA-256 `8026921050eae7497c0da3035efe6fd51ccbebd6f842dad03e90e1879cd2df10`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### total_engagements
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第30行、offset 1516起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::INTEGER AS INTEGER) AS total_engagements
```

修改后：
```sql
(CAST(COALESCE(comment_upvotes, '0') AS INT) + CAST(COALESCE(comment_downvotes, '0') AS INT) + CAST(COALESCE(viewer_comments, '0') AS INT) + 0) AS total_engagements
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/total_engagements.sql`；SHA-256 `9888bc56ebffb4bffb3edfd659a17753b8b0d927563404e09cb1cf8394aeb4ce`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"engagement_rate":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`

#### engagement_rate
主因；类别候选A。契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义
相对本轮基线：行减少0，格减少1200。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第31行、offset 1577起替换；其他字节相同。
原表达式：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS engagement_rate
```

修改后：
```sql
CASE WHEN impressions > 0 THEN ROUND((CAST((CAST(COALESCE(comment_upvotes, '0') AS INT) + CAST(COALESCE(comment_downvotes, '0') AS INT) + CAST(COALESCE(viewer_comments, '0') AS INT) + 0) AS DECIMAL(18, 3)) / CAST(impressions AS DECIMAL(18, 3))) * 100, 4) ELSE 0 END AS engagement_rate
```

私有SQL：`data/024_work/impl-006_stg_reddit_ads__campaign_report/engagement_rate.sql`；SHA-256 `475455e5fc749f1ef46fccefdb495b634e35859c61b8aeb92df0e701f6370a80`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1200|1200|1200|22800|否|
|L1|1200|1200|1200|22800|否|
|L2|1200|1200|1200|22800|否|
|L3|1200|1200|1200|22800|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L1：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L2：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
- L3：`{"click_through_rate":1200,"comments":1200,"community_joins":1200,"conversion_value":1200,"conversions":1200,"cost_per_click":1200,"cost_per_conversion":1200,"cost_per_thousand_impressions":1200,"cost_per_video_view":1200,"downvotes":1200,"post_visits":1200,"profile_visits":1200,"saves":1200,"shares":1200,"spend":1200,"total_engagements":1200,"upvotes":1200,"video_view_rate":1200,"video_views":1200}`
## 规则问题

盲标把三处直接TRY_CAST不可解析指标记U、部分派生NULL记D；复核契约未给公式，观察到不可解析也不能证明agent假设可解析，撤回U。派生口径亦未规定，改A。本修订发生在解盲后，不计作盲标一致。

## 盲标锁定与解盲复核

[024_blind_lock.json](../024_blind_lock.json)锁定原始盲标，后读取018；盲标与最终修订分别保存。

```json
{"task":"impl-006","table":"stg_reddit_ads__campaign_report","blind_category":"多因并列（I、D、A、U）","category_018":"多因并列（I、D、A）","blind_category_agrees":false,"blind_uncertainty":"只有通用策略说明","blind_uncertainty_agrees":false,"final_category":"多因并列（A、D、I）","final_category_agrees":true,"final_uncertainty_agrees":true,"final_factors_agree":true,"factor_comparison_note":"两版均无参与因素","post_blind_revision":"盲标把三处直接TRY_CAST不可解析指标记U、部分派生NULL记D；复核契约未给公式，观察到不可解析也不能证明agent假设可解析，撤回U。派生口径亦未规定，改A。本修订发生在解盲后，不计作盲标一致。"}
```

