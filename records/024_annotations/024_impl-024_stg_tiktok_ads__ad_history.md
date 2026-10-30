# impl-024 · stg_tiktok_ads__ad_history

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**A**；把握：中。

base_url在landing_page无http scheme时为NULL，gold直接保留原文本；契约没有规定base_url构造法，单改此处L0全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-024_stg_tiktok_ads__ad_history.md](../024_packages/024_impl-024_stg_tiktok_ads__ad_history.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`。

```text
192:     - name: stg_tiktok_ads__ad_history
193:       description: "Ad-level attributes with URL enrichment and recency flag."
194:       source_table: raw.tiktok_ad_history_data
195:       columns:
196:         - name: source_relation
197:           data_type: VARCHAR
198:         - name: ad_id
199:           data_type: VARCHAR
200:         - name: updated_at
201:           data_type: TIMESTAMP
202:           validation_rules:
203:             - rule: "updated_at is a valid timestamp"
204:               on_failure: nullify_field
205:         - name: ad_group_id
206:           data_type: VARCHAR
207:         - name: advertiser_id
208:           data_type: VARCHAR
209:         - name: campaign_id
210:           data_type: VARCHAR
211:         - name: ad_name
212:           data_type: VARCHAR
213:         - name: call_to_action
214:           data_type: VARCHAR
215:         - name: click_tracking_url
216:           data_type: VARCHAR
217:         - name: impression_tracking_url
218:           data_type: VARCHAR
219:         - name: base_url
220:           data_type: VARCHAR
221:         - name: url_host
222:           data_type: VARCHAR
223:         - name: url_path
224:           data_type: VARCHAR
225:         - name: utm_source
226:           data_type: VARCHAR
227:         - name: utm_medium
228:           data_type: VARCHAR
229:         - name: utm_campaign
230:           data_type: VARCHAR
231:         - name: utm_content
232:           data_type: VARCHAR
233:         - name: utm_term
234:           data_type: VARCHAR
235:         - name: landing_page_url
236:           data_type: VARCHAR
237:           validation_rules:
238:             - rule: "if missing, derived URL fields may be NULL"
239:               on_failure: nullify_field
240:         - name: is_most_recent_record
241:           data_type: BOOLEAN
242:           validation_rules:
243:             - rule: "true only for the row with maximal updated_at per ad_id and source system"
244:               on_failure: correct
245:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__ad_history.sql`；SHA-256 `3197b579522fc119f9956a96d66e5da23ebbd85b5eef126924395ad2df8f679f`。

```text
1: with staged as (
2: with source_data as (
3:     select "AD_ID,UPDATED_AT,ADVERTISER_ID,ADGROUP_ID,CAMPAIGN_ID,CREATE_TIME,AD_NAME,CALL_TO_ACTION,SECONDARY_STATUS,OPERATION_STATUS,AD_TEXT,VIDEO_ID,APP_NAME,DEEPLINK,LANDING_PAGE_URL,DISPLAY_NAME,PROFILE_IMAGE_URL,IMPRESSION_TRACKING_URL,CLICK_TRACKING_URL,PLAYABLE_URL,IS_ACO,CREATIVE_AUTHORIZED,IS_NEW_STRUCTURE,IMAGE_IDS,_FIVETRAN_SYNCED" as record from raw.tiktok_ad_history_data
4: )
5: select
6:         'tiktok_ads' as source_relation,
7:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 1), '""', '"')) as VARCHAR) as ad_id,
8:         try_cast(nullif(trim(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 2), '""', '"'))), '') as TIMESTAMP) as updated_at,
9:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 4), '""', '"')) as VARCHAR) as ad_group_id,
10:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 3), '""', '"')) as VARCHAR) as advertiser_id,
11:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 5), '""', '"')) as VARCHAR) as campaign_id,
12:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 7), '""', '"')) as VARCHAR) as ad_name,
13:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 8), '""', '"')) as VARCHAR) as call_to_action,
14:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 19), '""', '"')) as VARCHAR) as click_tracking_url,
15:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 18), '""', '"')) as VARCHAR) as impression_tracking_url,
16:         case when regexp_matches(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '^https?://') then regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '^(https?://[^/?#]+)', 1) || coalesce(regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '^[^?#]*?(/[^?#]*)', 1), '') else null end as base_url,
17:         regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '^https?://([^/?#]+)', 1) as url_host,
18:         regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '^https?://[^/?#]+(/[^?#]*)', 1) as url_path,
19:         regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '[?&]utm_source=([^&#]*)', 1) as utm_source,
20:         regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '[?&]utm_medium=([^&#]*)', 1) as utm_medium,
21:         regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '[?&]utm_campaign=([^&#]*)', 1) as utm_campaign,
22:         regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '[?&]utm_content=([^&#]*)', 1) as utm_content,
23:         regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '[?&]utm_term=([^&#]*)', 1) as utm_term,
24:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15), '""', '"')) as VARCHAR) as landing_page_url
25: from source_data
26: ), ranked as (
27:     select *, max(updated_at) over (partition by source_relation, ad_id) as max_updated_at
28:     from staged
29: )
30: select
31:     source_relation,
32:     ad_id,
33:     updated_at,
34:     ad_group_id,
35:     advertiser_id,
36:     campaign_id,
37:     ad_name,
38:     call_to_action,
39:     click_tracking_url,
40:     impression_tracking_url,
41:     base_url,
42:     url_host,
43:     url_path,
44:     utm_source,
45:     utm_medium,
46:     utm_campaign,
47:     utm_content,
48:     utm_term,
49:     landing_page_url,
50:     (updated_at is not distinct from max_updated_at) as is_most_recent_record
51: from ranked
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__ad_history.sql`；SHA-256 `cfaee865be3cf596089bec09bd346a6c5aae75a4148a9da3b7f44e9b3e2e9a24`。

```text
1: with rows as (
2:   select "AD_ID,UPDATED_AT,ADVERTISER_ID,ADGROUP_ID,CAMPAIGN_ID,CREATE_TIME,AD_NAME,CALL_TO_ACTION,SECONDARY_STATUS,OPERATION_STATUS,AD_TEXT,VIDEO_ID,APP_NAME,DEEPLINK,LANDING_PAGE_URL,DISPLAY_NAME,PROFILE_IMAGE_URL,IMPRESSION_TRACKING_URL,CLICK_TRACKING_URL,PLAYABLE_URL,IS_ACO,CREATIVE_AUTHORIZED,IS_NEW_STRUCTURE,IMAGE_IDS,_FIVETRAN_SYNCED" as row_str
3:   from raw.tiktok_ad_history_data
4: ), enriched as (
5:   select
6:     'raw.tiktok_ad_history_data' as source_relation,
7:     split_part(row_str, ',', 1) as ad_id,
8:     try_cast(split_part(row_str, ',', 2) as timestamp) as updated_at,
9:     split_part(row_str, ',', 4) as ad_group_id,
10:     split_part(row_str, ',', 3) as advertiser_id,
11:     split_part(row_str, ',', 5) as campaign_id,
12:     split_part(row_str, ',', 7) as ad_name,
13:     split_part(row_str, ',', 8) as call_to_action,
14:     split_part(row_str, ',', 19) as click_tracking_url,
15:     split_part(row_str, ',', 18) as impression_tracking_url,
16:     split_part(row_str, ',', 15) as base_url,
17:     -- DuckDB doesn't have url_extract/url_extract_parameter by default; use regex
18:     regexp_extract(split_part(row_str, ',', 15), '^[a-zA-Z]+://([^/]+)', 1) as url_host,
19:     '/' || coalesce(regexp_extract(split_part(row_str, ',', 15), '^[a-zA-Z]+://[^/]+(/[^?#]*)', 1), '') as url_path,
20:     regexp_extract(split_part(row_str, ',', 15), '[?&]utm_source=([^&#]+)', 1) as utm_source,
21:     regexp_extract(split_part(row_str, ',', 15), '[?&]utm_medium=([^&#]+)', 1) as utm_medium,
22:     regexp_extract(split_part(row_str, ',', 15), '[?&]utm_campaign=([^&#]+)', 1) as utm_campaign,
23:     regexp_extract(split_part(row_str, ',', 15), '[?&]utm_content=([^&#]+)', 1) as utm_content,
24:     regexp_extract(split_part(row_str, ',', 15), '[?&]utm_term=([^&#]+)', 1) as utm_term,
25:     split_part(row_str, ',', 15) as landing_page_url
26:   from rows
27: ), final as (
28:   select
29:     *,
30:     row_number() over (partition by source_relation, ad_id order by updated_at desc) = 1 as is_most_recent_record
31:   from enriched
32: )
33: select *
34: from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- base_url（A）：**看到了但没提**；事件 41、42、45、46。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 41：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/41.json`；命令首行：`python - <<'PY'`。
event 42：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/42.json`；原始观察输出。
event 45：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/45.json`；命令首行：`grep -n 'landing_page_url\|base_url\|utm_source' sql/staging/stg_tiktok_ads__ad_history.sql`。
event 46：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/46.json`；原始观察输出。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

已按 staging → intermediate → marts 顺序实现 SQL，文件均位于要求的 `sql/<layer>/<model_name>.sql` 路径下，共 22 个模型文件。

### 实施内容
- **Staging（8 张表）**：按契约投影字段并进行安全类型转换；数值指标按约定缺失时默认 0；清理 advertiser 邮箱、名称及手机号；生成 URL/UTM 字段；通过 `updated_at` 为历史数据标记最新记录。
- **Intermediate（8 个模型）**：按契约实现字段直通和最新记录筛选，来源仅引用 staging。
- **Marts（6 个模型）**：实现小时指标按日汇总、维度左连接、conversion value 汇总及零安全的 CPC/CPM/CTR 计算。来源仅引用 intermediate。

### 验证结果
- 执行 `python run.py` 成功，最终日志显示 staging `8/8`、intermediate `8/8`、marts `6/6` 模型创建成功。
- 各模型行数与源记录规模相符；ad report、campaign-country report 的分组主键未检测到重复。
- 最新 campaign 标记检查无异常；ad report 和 campaign-country report 的契约必填字段无 NULL；advertiser report 核心指标未发现负数。
- 检查确认 SQL 文件无文件末尾分号，也未使用 dbt `ref()`。

### 数据质量处理与残余影响
- 数值与日期采用 DuckDB `try_cast`，不可解析值置 NULL；报表数值列按 staging 合约对转换后的 NULL 默认 0。可选邮箱/名称/手机号字段验证失败时置 NULL，记录仍保留。
- 历史模型按 source relation 和实体 ID 标记最大更新时间；并列最大时间可能保留多行，符合契约保留重复记录的行为。
- 中间层与模型合约要求保留重复和 NULL，因此未做去重；原始重复可能继续影响下游汇总，属于配置明确要求的保留行为。

### 合约歧义及环境说明
- `stg_tiktok_ads__campaign_history.is_new_structure` 声明为 BOOLEAN，而 intermediate 列定义为 VARCHAR；intermediate 同时要求不转换、逐值透传。本实现遵守透传要求，因此输出保留 staging 的 BOOLEAN 类型。
- 运行环境根目录挂载为只读，无法创建 `/workspace/result.md`；完整报告保存在项目目录 `result.md`，内容亦包含于最终提交。
```

## 查询

核实查询 **1** 条；代价档：**一条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('tiktok_ad_history_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["tiktok_ad_history_data","AD_ID,UPDATED_AT,ADVERTISER_ID,ADGROUP_ID,CAMPAIGN_ID,CREATE_TIME,AD_NAME,CALL_TO_ACTION,SECONDARY_STATUS,OPERATION_STATUS,AD_TEXT,VIDEO_ID,APP_NAME,DEEPLINK,LANDING_PAGE_URL,DISPLAY_NAME,PROFILE_IMAGE_URL,IMPRESSION_TRACKING_URL,CLICK_TRACKING_URL,PLAYABLE_URL,IS_ACO,CREATIVE_AUTHORIZED,IS_NEW_STRUCTURE,IMAGE_IDS,_FIVETRAN_SYNCED","VARCHAR"]]}
```

## 独立单点重跑

### 024_reruns_impl-024_stg_tiktok_ads__ad_history.json
[024_reruns_impl-024_stg_tiktok_ads__ad_history.json](../024_reruns_impl-024_stg_tiktok_ads__ad_history.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/tiktok_ads.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2509|2509|2509|2509|否|
|L1|2509|2509|2509|2509|否|
|L2|2509|2509|2509|2509|否|
|L3|2509|2509|2509|2509|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"base_url":2509}`
- L1：`{"base_url":2509}`
- L2：`{"base_url":2509}`
- L3：`{"base_url":2509}`

#### baseline
私有SQL：`data/024_work/impl-024_stg_tiktok_ads__ad_history/baseline.sql`；SHA-256 `3197b579522fc119f9956a96d66e5da23ebbd85b5eef126924395ad2df8f679f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2509|2509|2509|2509|否|
|L1|2509|2509|2509|2509|否|
|L2|2509|2509|2509|2509|否|
|L3|2509|2509|2509|2509|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"base_url":2509}`
- L1：`{"base_url":2509}`
- L2：`{"base_url":2509}`
- L3：`{"base_url":2509}`

#### source_relation
不计参与因素；类别候选A。契约未规定source_relation常量字面量；gold使用raw表名。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第6行、offset 444起替换；其他字节相同。
原表达式：
```sql
'tiktok_ads' as source_relation
```

修改后：
```sql
'raw.tiktok_ad_history_data' as source_relation
```

私有SQL：`data/024_work/impl-024_stg_tiktok_ads__ad_history/source_relation.sql`；SHA-256 `779eccf66412fb463435bd94a8a33a6b3852a13251eff298c9183dfac1e4dc05`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2509|2509|2509|2509|否|
|L1|2509|2509|2509|2509|否|
|L2|2509|2509|2509|2509|否|
|L3|2509|2509|2509|2509|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"base_url":2509}`
- L1：`{"base_url":2509}`
- L2：`{"base_url":2509}`
- L3：`{"base_url":2509}`

#### base_url
主因；类别候选A。契约未规定URL拆解算法与缺失值表示；gold的base_url保留query且path额外前缀/。
相对本轮基线：行减少2509，格减少2509。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第16行、offset 2054起替换；其他字节相同。
原表达式：
```sql
case when regexp_matches(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '^https?://') then regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '^(https?://[^/?#]+)', 1) || coalesce(regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '^[^?#]*?(/[^?#]*)', 1), '') else null end as base_url
```

修改后：
```sql
trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)) as base_url
```

私有SQL：`data/024_work/impl-024_stg_tiktok_ads__ad_history/base_url.sql`；SHA-256 `2ae647fc4a0d0e13e7963c36509403b07f560b01a0d8debc8110465558da94fd`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2509|2509|0|0|是|
|L1|2509|2509|0|0|是|
|L2|2509|2509|0|0|是|
|L3|2509|2509|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

#### url_path
不计参与因素；类别候选A。契约未规定URL拆解算法与缺失值表示；gold的base_url保留query且path额外前缀/。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第18行、offset 2736起替换；其他字节相同。
原表达式：
```sql
regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '^https?://[^/?#]+(/[^?#]*)', 1) as url_path
```

修改后：
```sql
'/' || coalesce(regexp_extract(trim(both '"' from list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15)), '^[a-zA-Z]+://[^/]+(/[^?#]*)', 1), '') as url_path
```

私有SQL：`data/024_work/impl-024_stg_tiktok_ads__ad_history/url_path.sql`；SHA-256 `c676140a802213ef92b03f66eecc33c41896076029037dc1c84fe84d4645c6f5`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2509|2509|2509|2509|否|
|L1|2509|2509|2509|2509|否|
|L2|2509|2509|2509|2509|否|
|L3|2509|2509|2509|2509|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"base_url":2509}`
- L1：`{"base_url":2509}`
- L2：`{"base_url":2509}`
- L3：`{"base_url":2509}`
## 规则问题

无。

