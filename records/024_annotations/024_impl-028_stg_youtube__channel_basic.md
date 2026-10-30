# impl-028 · stg_youtube__channel_basic

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**不可评估**；把握：高。

逐张确认直接读取agent/initial同一raw表且内容差集为0；gold读取另一组名称、schema和行数均不同的raw表，满足不可评估。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-028_stg_youtube__channel_basic.md](../024_packages/024_impl-028_stg_youtube__channel_basic.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/docs/data_contract.yaml`。

```text
34:     - name: stg_youtube__channel_basic
35:       description: "Cleaned daily per-video channel performance metrics (views, engagement, subscribers, annotations). Percentages are normalized to [0,1]."
36:       source_table: raw.channel_basic_a_2
37:       columns:
38:         - name: date_day
39:           data_type: DATE
40:           validation_rules:
41:             - rule: "date_day IS NOT NULL AND date_day <= CURRENT_DATE AND date_day >= '2020-01-01'"
42:               on_failure: delete_row
43:         - name: channel_id
44:           data_type: VARCHAR
45:           validation_rules:
46:             - rule: "channel_id IS NULL OR LENGTH(TRIM(channel_id)) = 24"
47:               on_failure: nullify_field
48:             - rule: "channel_id = TRIM(channel_id)"
49:               on_failure: correct
50:         - name: video_id
51:           data_type: VARCHAR
52:           validation_rules:
53:             - rule: "video_id IS NULL OR LENGTH(TRIM(video_id)) = 11"
54:               on_failure: nullify_field
55:             - rule: "video_id = TRIM(video_id)"
56:               on_failure: correct
57:         - name: channel_title
58:           data_type: VARCHAR
59:         - name: video_title
60:           data_type: VARCHAR
61:         - name: deleted
62:           data_type: BOOLEAN
63:         - name: _fivetran_synced
64:           data_type: TIMESTAMP
65:           validation_rules:
66:             - rule: "_fivetran_synced IS NULL OR _fivetran_synced <= CURRENT_TIMESTAMP"
67:               on_failure: nullify_field
68:         - name: average_view_duration_seconds
69:           data_type: BIGINT
70:         - name: average_view_duration_percentage
71:           data_type: DECIMAL(5,4)
72:           validation_rules:
73:             - rule: "average_view_duration_percentage BETWEEN 0 AND 1"
74:               on_failure: nullify_field
75:         - name: views
76:           data_type: BIGINT
77:           validation_rules:
78:             - rule: "views BETWEEN 0 AND 1000000000"
79:               on_failure: nullify_field
80:         - name: likes
81:           data_type: BIGINT
82:           validation_rules:
83:             - rule: "likes BETWEEN 0 AND 10000000"
84:               on_failure: nullify_field
85:         - name: dislikes
86:           data_type: BIGINT
87:           validation_rules:
88:             - rule: "dislikes BETWEEN 0 AND 1000000"
89:               on_failure: nullify_field
90:         - name: shares
91:           data_type: BIGINT
92:           validation_rules:
93:             - rule: "shares >= 0"
94:               on_failure: nullify_field
95:         - name: subscribers_gained
96:           data_type: BIGINT
97:           validation_rules:
98:             - rule: "subscribers_gained BETWEEN -50000 AND 50000"
99:               on_failure: nullify_field
100:         - name: subscribers_lost
101:           data_type: BIGINT
102:           validation_rules:
103:             - rule: "subscribers_lost BETWEEN 0 AND 10000"
104:               on_failure: nullify_field
105:         - name: estimated_minutes_watched
106:           data_type: DECIMAL(18,4)
107:           validation_rules:
108:             - rule: "estimated_minutes_watched >= 0"
109:               on_failure: nullify_field
110:         - name: estimated_red_minutes_watched
111:           data_type: DECIMAL(18,4)
112:           validation_rules:
113:             - rule: "estimated_red_minutes_watched >= 0"
114:               on_failure: nullify_field
115:         - name: annotation_click_through_rate
116:           data_type: DECIMAL(18,4)
117:         - name: annotation_close_rate
118:           data_type: DECIMAL(18,4)
119:         - name: annotation_impressions
120:           data_type: BIGINT
121:         - name: annotation_clickable_impressions
122:           data_type: BIGINT
123:         - name: annotation_closable_impressions
124:           data_type: BIGINT
125:         - name: annotation_clicks
126:           data_type: BIGINT
127:         - name: annotation_closes
128:           data_type: BIGINT
129:         - name: viewers
130:           data_type: BIGINT
131:         - name: views_percentage
132:           data_type: DECIMAL(5,4)
133:           validation_rules:
134:             - rule: "views_percentage BETWEEN 0 AND 1"
135:               on_failure: nullify_field
136:         - name: average_time_in_video
137:           data_type: DECIMAL(18,4)
138:         - name: card_click_rate
139:           data_type: DECIMAL(18,4)
140:         - name: card_impressions
141:           data_type: BIGINT
142:         - name: card_clickable_impressions
143:           data_type: BIGINT
144:         - name: card_clicks
145:           data_type: BIGINT
146:         - name: playlist_starts
147:           data_type: BIGINT
148:         - name: estimated_minutes_watched_from_playlists
149:           data_type: DECIMAL(18,4)
150:         - name: average_time_in_playlist
151:           data_type: DECIMAL(18,4)
152:         - name: source_relation
153:           data_type: VARCHAR
154:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/sql/staging/stg_youtube__channel_basic.sql`；SHA-256 `51131a49dec75291bb4664105095d6d8e3b5b1fc3c8e6876dadf433c439f4a3d`。

```text
1: with source_rows as (
2:     select
3:         try_cast("date" as date) as date_day,
4:         channel_id,
5:         video_id,
6:         cast(null as varchar) as channel_title,
7:         cast(null as varchar) as video_title,
8:         cast(null as boolean) as deleted,
9:         try_cast(replace("_fivetran_synced", ' UTC', '') as timestamp) as _fivetran_synced,
10:         try_cast(average_view_duration_seconds as bigint) as average_view_duration_seconds,
11:         try_cast(average_view_duration_percentage as decimal(5, 4)) as average_view_duration_percentage,
12:         views,
13:         likes,
14:         dislikes,
15:         shares,
16:         subscribers_gained,
17:         subscribers_lost,
18:         try_cast(watch_time_minutes as decimal(18, 4)) as estimated_minutes_watched,
19:         try_cast(red_watch_time_minutes as decimal(18, 4)) as estimated_red_minutes_watched,
20:         try_cast(annotation_click_through_rate as decimal(18, 4)) as annotation_click_through_rate,
21:         try_cast(annotation_close_rate as decimal(18, 4)) as annotation_close_rate,
22:         annotation_impressions,
23:         annotation_clickable_impressions,
24:         annotation_closable_impressions,
25:         annotation_clicks,
26:         annotation_closes,
27:         cast(null as bigint) as viewers,
28:         cast(null as decimal(5, 4)) as views_percentage,
29:         cast(null as decimal(18, 4)) as average_time_in_video,
30:         try_cast(card_click_rate as decimal(18, 4)) as card_click_rate,
31:         card_impressions,
32:         cast(null as bigint) as card_clickable_impressions,
33:         card_clicks,
34:         cast(null as bigint) as playlist_starts,
35:         cast(null as decimal(18, 4)) as estimated_minutes_watched_from_playlists,
36:         cast(null as decimal(18, 4)) as average_time_in_playlist,
37:         'youtube_channel_basic_data' as source_relation
38:     from raw.youtube_channel_basic_data
39: ),
40: validated_rows as (
41:     select
42:         date_day,
43:         case when channel_id is null or length(trim(channel_id)) = 24 then trim(channel_id) else null end as channel_id,
44:         case when video_id is null or length(trim(video_id)) = 11 then trim(video_id) else null end as video_id,
45:         channel_title,
46:         video_title,
47:         deleted,
48:         case when _fivetran_synced is null or _fivetran_synced <= current_timestamp then _fivetran_synced else null end as _fivetran_synced,
49:         average_view_duration_seconds,
50:         case when average_view_duration_percentage between 0 and 1 then average_view_duration_percentage else null end as average_view_duration_percentage,
51:         case when views between 0 and 1000000000 then views else null end as views,
52:         case when likes between 0 and 10000000 then likes else null end as likes,
53:         case when dislikes between 0 and 1000000 then dislikes else null end as dislikes,
54:         case when shares >= 0 then shares else null end as shares,
55:         case when subscribers_gained between -50000 and 50000 then subscribers_gained else null end as subscribers_gained,
56:         case when subscribers_lost between 0 and 10000 then subscribers_lost else null end as subscribers_lost,
57:         case when estimated_minutes_watched >= 0 then estimated_minutes_watched else null end as estimated_minutes_watched,
58:         case when estimated_red_minutes_watched >= 0 then estimated_red_minutes_watched else null end as estimated_red_minutes_watched,
59:         annotation_click_through_rate,
60:         annotation_close_rate,
61:         annotation_impressions,
62:         annotation_clickable_impressions,
63:         annotation_closable_impressions,
64:         annotation_clicks,
65:         annotation_closes,
66:         viewers,
67:         case when views_percentage between 0 and 1 then views_percentage else null end as views_percentage,
68:         average_time_in_video,
69:         card_click_rate,
70:         card_impressions,
71:         cast(null as bigint) as card_clickable_impressions,
72:         card_clicks,
73:         playlist_starts,
74:         estimated_minutes_watched_from_playlists,
75:         average_time_in_playlist,
76:         source_relation
77:     from source_rows
78:     where date_day is not null
79:       and date_day <= current_date
80:       and date_day >= date '2020-01-01'
81: )
82: select *
83: from validated_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/sql/staging/stg_youtube__channel_basic.sql`；SHA-256 `8d631865d2bccdeab21f75a099d8959f90303e43ab2875c781221ed0f221a26d`。

```text
1: with source_data as (
2:     select * from raw.channel_basic_a_2
3: ),
4: 
5: renamed as (
6:     select
7:         date as date_day,
8:         channel_id,
9:         video_id,
10:         channel_title,
11:         video_title,
12:         deleted,
13:         _fivetran_synced,
14:         average_view_duration_seconds,
15:         average_view_duration_percentage / 100.0 as average_view_duration_percentage,
16:         views,
17:         likes,
18:         dislikes,
19:         shares,
20:         subscribers_gained,
21:         subscribers_lost,
22:         estimated_minutes_watched,
23:         estimated_red_minutes_watched,
24:         annotation_click_through_rate,
25:         annotation_close_rate,
26:         annotation_impressions,
27:         annotation_clickable_impressions,
28:         annotation_closable_impressions,
29:         annotation_clicks,
30:         annotation_closes,
31:         viewers,
32:         views_percentage / 100.0 as views_percentage,
33:         average_time_in_video,
34:         card_click_rate,
35:         card_impressions,
36:         card_clickable_impressions,
37:         card_clicks,
38:         playlist_starts,
39:         estimated_minutes_watched_from_playlists,
40:         average_time_in_playlist,
41:         'youtube_source' as source_relation
42:     from source_data
43: ),
44: 
45: validated as (
46:     select
47:         -- enforce temporal validity of dates
48:         date_day,
49:         -- identifiers cleaning/validation
50:         case when channel_id IS NOT NULL AND length(trim(channel_id)) = 24 then trim(channel_id) else NULL end as channel_id,
51:         case when video_id IS NULL OR length(trim(video_id)) = 11 then trim(video_id) else NULL end as video_id,
52:         channel_title,
53:         video_title,
54:         deleted,
55:         case when _fivetran_synced <= current_timestamp then _fivetran_synced else NULL end as _fivetran_synced,
56:         -- percentage already normalized to [0,1]; enforce bounds
57:         average_view_duration_seconds,
58:         case when average_view_duration_percentage >= 0 and average_view_duration_percentage <= 1 then average_view_duration_percentage else NULL end as average_view_duration_percentage,
59:         -- non-negative metrics and sensible ranges
60:         case when views >= 0 and views <= 1000000000 then views else NULL end as views,
61:         case when likes >= 0 and likes <= 10000000 then likes else NULL end as likes,
62:         case when dislikes >= 0 and dislikes <= 1000000 then dislikes else NULL end as dislikes,
63:         case when shares >= 0 then shares else NULL end as shares,
64:         case when subscribers_gained >= -50000 and subscribers_gained <= 50000 then subscribers_gained else NULL end as subscribers_gained,
65:         case when subscribers_lost >= 0 and subscribers_lost <= 10000 then subscribers_lost else NULL end as subscribers_lost,
66:         case when estimated_minutes_watched >= 0 then estimated_minutes_watched else NULL end as estimated_minutes_watched,
67:         case when estimated_red_minutes_watched >= 0 then estimated_red_minutes_watched else NULL end as estimated_red_minutes_watched,
68:         annotation_click_through_rate,
69:         annotation_close_rate,
70:         annotation_impressions,
71:         annotation_clickable_impressions,
72:         annotation_closable_impressions,
73:         annotation_clicks,
74:         annotation_closes,
75:         viewers,
76:         case when views_percentage >= 0 and views_percentage <= 1 then views_percentage else NULL end as views_percentage,
77:         average_time_in_video,
78:         card_click_rate,
79:         card_impressions,
80:         card_clickable_impressions,
81:         card_clicks,
82:         playlist_starts,
83:         estimated_minutes_watched_from_playlists,
84:         average_time_in_playlist,
85:         source_relation
86:     from renamed
87:     where date_day is not null
88:       and date_day >= '2020-01-01' and date_day <= current_date
89: )
90: 
91: select * from validated
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- 本表主要差异（不可评估）：**针对本表的具体说明**；事件 23、24、55。
原句：

```
原始数据的 `channel_basic` 缺少 contract 字段 `channel_title`、`video_title`、`deleted`、`viewers`、`views_percentage`、部分 card/playlist 字段等；`video` 源缺少或类型与 contract 不同的缩略图、标签、语言、区域限制等字段。
```

event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/23.json`；命令首行：`python - <<'PY'`。
event 24：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/24.json`；原始观察输出。
event 55：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/55.json`；命令首行：`cat > result.md <<'MD'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上游引用，没有 dbt `ref()`，SQL 文件末尾未添加分号。

## 交付文件

- **Staging:** `stg_youtube__channel_basic.sql`、`stg_youtube__channel_demographics.sql`、`stg_youtube__video.sql`
- **Intermediate:** `int_youtube__channel_basic.sql`、`int_youtube__channel_demographics.sql`、`int_youtube__age_pivot.sql`、`int_youtube__gender_pivot.sql`、`int_youtube__video.sql`
- **Marts:** `youtube__video_metadata.sql`、`youtube__video_report.sql`、`youtube__demographics_report.sql`、`youtube__age_demographics_pivot.sql`、`youtube__gender_demographics_pivot.sql`

## 实现和验证

- Staging 实现字段转换、验证、修正/置空和无效日期/视频记录的行级删除；Intermediate 实现逐行/窗口指标、人口统计透视与视频元数据解析；Marts 实现报表聚合、关联和指定输出字段。
- `python run.py` 成功完成所有模型：3 个 staging、5 个 intermediate、5 个 marts 均执行成功。输出行数依次为 **3,500 / 2,509 / 2,501**；intermediate 为 **3,500 / 2,509 / 2,504 / 1,671 / 2,501**；marts 为 **2,501 / 2,951 / 2,504 / 1,671 / 2,504**。
- 已检查 staging 行数及日期质量、透视占比上下界、非负报表总观看量、报表记录数等；所有执行检查均符合预期。非空 `video_report_id` 唯一。
- 运行时发现 `run.py` 从源数据库读取 `SHOW TABLES`、未限定 `raw` schema，因此对按 `raw` schema 存放的源表得到空表列表。已修正导入逻辑，从 `information_schema.tables` 读取 raw 表并通过 `raw.<table>` 读取，之后全流程通过。

## 合约数据不匹配及残余影响

1. 原始数据的 `channel_basic` 缺少 contract 字段 `channel_title`、`video_title`、`deleted`、`viewers`、`views_percentage`、部分 card/playlist 字段等；`video` 源缺少或类型与 contract 不同的缩略图、标签、语言、区域限制等字段。无法从源端恢复的 staging 字段填为类型正确的 NULL；这部分字段以及相应派生信息不可用，其余记录保留。
2. 数据中有 **2 条** channel_basic 记录的 `video_id` 为空。staging 契约允许该字段为空，且 intermediate 与报表业务逻辑要求保留源记录/分组，因此按要求保留；报表中对应 `video_report_id` 也为空（MD5 输入字符串因 `video_id` 为 NULL 而为空）。因此报表键的 not-null 契约测试对这两行不成立；非空 ID 的键唯一性通过。未自行过滤这些行或伪造替代键，以免改变既定粒度和业务逻辑。
3. 视频表 `snippet_thumbnails`、`snippet_tags` 等原始字段类型为 DOUBLE 且样例中为空，不能提供 YAML 描述的 URL/标签字符串；视频 thumbnail URLs 因而为空，marts 按契约将 NULL 缩略图转换为空字符串。源字段的限制使 URL 解析无实际输入可验证。

上述边界按最小安全假设实施：源 schema 不存在的字段映射成类型化 NULL，不引入虚构信息；重复记录予以保留，未增加契约未要求的去重或排除规则。
```

## 查询

核实查询 **1** 条；代价档：**一条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('youtube_channel_basic_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["youtube_channel_basic_data","_fivetran_id","VARCHAR"],["youtube_channel_basic_data","date","VARCHAR"],["youtube_channel_basic_data","_fivetran_synced","VARCHAR"],["youtube_channel_basic_data","annotation_click_through_rate","DOUBLE"],["youtube_channel_basic_data","annotation_clickable_impressions","BIGINT"],["youtube_channel_basic_data","annotation_clicks","BIGINT"],["youtube_channel_basic_data","annotation_closable_impressions","BIGINT"],["youtube_channel_basic_data","annotation_close_rate","DOUBLE"],["youtube_channel_basic_data","annotation_closes","BIGINT"],["youtube_channel_basic_data","annotation_impressions","BIGINT"],["youtube_channel_basic_data","average_view_duration_percentage","DOUBLE"],["youtube_channel_basic_data","average_view_duration_seconds","DOUBLE"],["youtube_channel_basic_data","card_click_rate","DOUBLE"],["youtube_channel_basic_data","card_clicks","BIGINT"],["youtube_channel_basic_data","card_impressions","BIGINT"],["youtube_channel_basic_data","card_teaser_click_rate","DOUBLE"],["youtube_channel_basic_data","card_teaser_clicks","BIGINT"],["youtube_channel_basic_data","card_teaser_impressions","BIGINT"],["youtube_channel_basic_data","channel_id","VARCHAR"],["youtube_channel_basic_data","comments","BIGINT"],["youtube_channel_basic_data","country_code","VARCHAR"],["youtube_channel_basic_data","dislikes","BIGINT"],["youtube_channel_basic_data","likes","BIGINT"],["youtube_channel_basic_data","live_or_on_demand","VARCHAR"],["youtube_channel_basic_data","red_views","BIGINT"],["youtube_channel_basic_data","red_watch_time_minutes","DOUBLE"],["youtube_channel_basic_data","shares","BIGINT"],["youtube_channel_basic_data","subscribed_status","VARCHAR"],["youtube_channel_basic_data","subscribers_gained","BIGINT"],["youtube_channel_basic_data","subscribers_lost","BIGINT"],["youtube_channel_basic_data","video_id","VARCHAR"],["youtube_channel_basic_data","videos_added_to_playlists","BIGINT"],["youtube_channel_basic_data","videos_removed_from_playlists","BIGINT"],["youtube_channel_basic_data","views","BIGINT"],["youtube_channel_basic_data","watch_time_minutes","DOUBLE"]]}
```


### 诊断：initial_database直接原始表规模
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/youtube_analytics_start.duckdb`。

```sql
SELECT 'raw.youtube_channel_basic_data' relation,count(*) n FROM raw.youtube_channel_basic_data
```


```json
{"columns":["relation","n"],"rows":[["raw.youtube_channel_basic_data",3500]]}
```


### 诊断：agent_database直接原始表规模
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb`。

```sql
SELECT 'raw.youtube_channel_basic_data' relation,count(*) n FROM raw.youtube_channel_basic_data
```


```json
{"columns":["relation","n"],"rows":[["raw.youtube_channel_basic_data",3500]]}
```


### 诊断：gold实际raw表清单
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb`。

```sql
SELECT table_name FROM information_schema.tables WHERE table_schema='raw' ORDER BY table_name
```


```json
{"columns":["table_name"],"rows":[["channel_basic_a_2"],["channel_demographics_a_1"],["video"]]}
```


### 诊断：initial-agent逐值差集
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/youtube_analytics_start.duckdb`。

```sql
SELECT count(*) FROM ((SELECT * FROM raw.youtube_channel_basic_data EXCEPT ALL SELECT * FROM retained.raw.youtube_channel_basic_data) UNION ALL (SELECT * FROM retained.raw.youtube_channel_basic_data EXCEPT ALL SELECT * FROM raw.youtube_channel_basic_data))
```


```json
{"rows":[[0]]}
```

attached_read_only：`"/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb"`
## 独立单点重跑

### 024_reruns_impl-028_stg_youtube__channel_basic.json
[024_reruns_impl-028_stg_youtube__channel_basic.json](../024_reruns_impl-028_stg_youtube__channel_basic.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2024-01-30 00:00:00+00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2024-01-30'","count":1}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1340|150|1490|38740|否|
|L1|1340|150|1490|38740|否|
|L2|1340|150|1490|38740|否|
|L3|1340|150|1490|38740|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":1490,"channel_id":1490,"video_id":1490,"annotation_click_through_rate":1490,"annotation_clickable_impressions":1490,"annotation_clicks":1490,"annotation_closable_impressions":1490,"annotation_close_rate":1490,"annotation_closes":1490,"annotation_impressions":1490,"average_view_duration_percentage":1490,"average_view_duration_seconds":1490,"card_click_rate":1490,"card_clicks":1490,"card_impressions":1490,"channel_title":1490,"deleted":1490,"dislikes":1490,"estimated_minutes_watched":1490,"estimated_red_minutes_watched":1490,"likes":1490,"shares":1490,"subscribers_gained":1490,"subscribers_lost":1490,"video_title":1490,"views":1490}`
- L1：`{"date_day":1490,"channel_id":1490,"video_id":1490,"annotation_click_through_rate":1490,"annotation_clickable_impressions":1490,"annotation_clicks":1490,"annotation_closable_impressions":1490,"annotation_close_rate":1490,"annotation_closes":1490,"annotation_impressions":1490,"average_view_duration_percentage":1490,"average_view_duration_seconds":1490,"card_click_rate":1490,"card_clicks":1490,"card_impressions":1490,"channel_title":1490,"deleted":1490,"dislikes":1490,"estimated_minutes_watched":1490,"estimated_red_minutes_watched":1490,"likes":1490,"shares":1490,"subscribers_gained":1490,"subscribers_lost":1490,"video_title":1490,"views":1490}`
- L2：`{"date_day":1490,"channel_id":1490,"video_id":1490,"annotation_click_through_rate":1490,"annotation_clickable_impressions":1490,"annotation_clicks":1490,"annotation_closable_impressions":1490,"annotation_close_rate":1490,"annotation_closes":1490,"annotation_impressions":1490,"average_view_duration_percentage":1490,"average_view_duration_seconds":1490,"card_click_rate":1490,"card_clicks":1490,"card_impressions":1490,"channel_title":1490,"deleted":1490,"dislikes":1490,"estimated_minutes_watched":1490,"estimated_red_minutes_watched":1490,"likes":1490,"shares":1490,"subscribers_gained":1490,"subscribers_lost":1490,"video_title":1490,"views":1490}`
- L3：`{"date_day":1490,"channel_id":1490,"video_id":1490,"annotation_click_through_rate":1490,"annotation_clickable_impressions":1490,"annotation_clicks":1490,"annotation_closable_impressions":1490,"annotation_close_rate":1490,"annotation_closes":1490,"annotation_impressions":1490,"average_view_duration_percentage":1490,"average_view_duration_seconds":1490,"card_click_rate":1490,"card_clicks":1490,"card_impressions":1490,"channel_title":1490,"deleted":1490,"dislikes":1490,"estimated_minutes_watched":1490,"estimated_red_minutes_watched":1490,"likes":1490,"shares":1490,"subscribers_gained":1490,"subscribers_lost":1490,"video_title":1490,"views":1490}`

#### baseline
私有SQL：`data/024_work/impl-028_stg_youtube__channel_basic/baseline.sql`；SHA-256 `17bbe9c08873eb3780b8a206161b6d9871cd1b2fad3e9711de01265bd3191f73`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1340|150|1490|38740|否|
|L1|1340|150|1490|38740|否|
|L2|1340|150|1490|38740|否|
|L3|1340|150|1490|38740|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"date_day":1490,"channel_id":1490,"video_id":1490,"annotation_click_through_rate":1490,"annotation_clickable_impressions":1490,"annotation_clicks":1490,"annotation_closable_impressions":1490,"annotation_close_rate":1490,"annotation_closes":1490,"annotation_impressions":1490,"average_view_duration_percentage":1490,"average_view_duration_seconds":1490,"card_click_rate":1490,"card_clicks":1490,"card_impressions":1490,"channel_title":1490,"deleted":1490,"dislikes":1490,"estimated_minutes_watched":1490,"estimated_red_minutes_watched":1490,"likes":1490,"shares":1490,"subscribers_gained":1490,"subscribers_lost":1490,"video_title":1490,"views":1490}`
- L1：`{"date_day":1490,"channel_id":1490,"video_id":1490,"annotation_click_through_rate":1490,"annotation_clickable_impressions":1490,"annotation_clicks":1490,"annotation_closable_impressions":1490,"annotation_close_rate":1490,"annotation_closes":1490,"annotation_impressions":1490,"average_view_duration_percentage":1490,"average_view_duration_seconds":1490,"card_click_rate":1490,"card_clicks":1490,"card_impressions":1490,"channel_title":1490,"deleted":1490,"dislikes":1490,"estimated_minutes_watched":1490,"estimated_red_minutes_watched":1490,"likes":1490,"shares":1490,"subscribers_gained":1490,"subscribers_lost":1490,"video_title":1490,"views":1490}`
- L2：`{"date_day":1490,"channel_id":1490,"video_id":1490,"annotation_click_through_rate":1490,"annotation_clickable_impressions":1490,"annotation_clicks":1490,"annotation_closable_impressions":1490,"annotation_close_rate":1490,"annotation_closes":1490,"annotation_impressions":1490,"average_view_duration_percentage":1490,"average_view_duration_seconds":1490,"card_click_rate":1490,"card_clicks":1490,"card_impressions":1490,"channel_title":1490,"deleted":1490,"dislikes":1490,"estimated_minutes_watched":1490,"estimated_red_minutes_watched":1490,"likes":1490,"shares":1490,"subscribers_gained":1490,"subscribers_lost":1490,"video_title":1490,"views":1490}`
- L3：`{"date_day":1490,"channel_id":1490,"video_id":1490,"annotation_click_through_rate":1490,"annotation_clickable_impressions":1490,"annotation_clicks":1490,"annotation_closable_impressions":1490,"annotation_close_rate":1490,"annotation_closes":1490,"annotation_impressions":1490,"average_view_duration_percentage":1490,"average_view_duration_seconds":1490,"card_click_rate":1490,"card_clicks":1490,"card_impressions":1490,"channel_title":1490,"deleted":1490,"dislikes":1490,"estimated_minutes_watched":1490,"estimated_red_minutes_watched":1490,"likes":1490,"shares":1490,"subscribers_gained":1490,"subscribers_lost":1490,"video_title":1490,"views":1490}`
## 规则问题

无。

