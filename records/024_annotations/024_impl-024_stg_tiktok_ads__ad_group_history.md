# impl-024 · stg_tiktok_ads__ad_group_history

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**多因并列（A、O）**；把握：中。

source_relation字面量未规定；agent按header解析完整age_groups和budget，gold取截断数组/前一位置。三处各减少2504格。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-024_stg_tiktok_ads__ad_group_history.md](../024_packages/024_impl-024_stg_tiktok_ads__ad_group_history.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`。

```text
140:     - name: stg_tiktok_ads__ad_group_history
141:       description: "Typed ad group attributes with selected targeting fields and recency flag."
142:       source_table: raw.tiktok_adgroup_history_data
143:       columns:
144:         - name: source_relation
145:           data_type: VARCHAR
146:         - name: ad_group_id
147:           data_type: VARCHAR
148:         - name: updated_at
149:           data_type: TIMESTAMP
150:           validation_rules:
151:             - rule: "updated_at is a valid timestamp"
152:               on_failure: nullify_field
153:         - name: advertiser_id
154:           data_type: VARCHAR
155:         - name: campaign_id
156:           data_type: VARCHAR
157:         - name: interest_category
158:           data_type: VARCHAR
159:         - name: ad_group_name
160:           data_type: VARCHAR
161:         - name: frequency
162:           data_type: VARCHAR
163:         - name: frequency_schedule
164:           data_type: VARCHAR
165:         - name: age_groups
166:           data_type: VARCHAR
167:         - name: languages
168:           data_type: VARCHAR
169:         - name: gender
170:           data_type: VARCHAR
171:         - name: budget_mode
172:           data_type: VARCHAR
173:         - name: budget
174:           data_type: DOUBLE
175:           validation_rules:
176:             - rule: "budget is numeric"
177:               on_failure: nullify_field
178:         - name: landing_page_url
179:           data_type: VARCHAR
180:         - name: secondary_optimization_event
181:           data_type: VARCHAR
182:         - name: creative_material_mode
183:           data_type: VARCHAR
184:         - name: audience_type
185:           data_type: VARCHAR
186:         - name: is_most_recent_record
187:           data_type: BOOLEAN
188:           validation_rules:
189:             - rule: "true only for the row with maximal updated_at per ad_group_id and source system"
190:               on_failure: correct
191:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__ad_group_history.sql`；SHA-256 `e8c11c44d1d1e2b9479b8cf0957ee6485fdfa764b21a2923a58d1ce05c1bc6c5`。

```text
1: with staged as (
2: with source_data as (
3:     select "ADGROUP_ID,UPDATED_AT,ADVERTISER_ID,CAMPAIGN_ID,CREATE_TIME,ADGROUP_NAME,PLACEMENT_TYPE,PROFILE_IMAGE,LANDING_PAGE_URL,DISPLAY_NAME,APP_TYPE,APP_DOWNLOAD_URL,APP_NAME,OPTIMIZATION_EVENT,SECONDARY_OPTIMIZATION_EVENT,CREATIVE_MATERIAL_MODE,AUDIENCE_TYPE,GENDER,MIN_ANDROID_VERSION,MIN_IOS_VERSION,BUDGET_MODE,SCHEDULE_TYPE,DAYPARTING,OPTIMIZATION_GOAL,CPV_VIDEO_DURATION,PACING,BILLING_EVENT,BID_TYPE,DEEP_BID_TYPE,IMPRESSION_TRACKING_URL,CLICK_TRACKING_URL,SECONDARY_STATUS,OPERATION_STATUS,STATISTIC_TYPE,VIDEO_DOWNLOAD,OPEN_URL,OPEN_URL_TYPE,FALLBACK_TYPE,BUDGET,BID_PRICE,CONVERSION_BID_PRICE,DEEP_CPA_BID,SCHEDULE_START_TIME,SCHEDULE_END_TIME,APP_ID,PIXEL_ID,INVENTORY_FILTER_ENABLED,IS_HFSS,IS_NEW_STRUCTURE,CATEGORY,IS_COMMENT_DISABLE,SKIP_LEARNING_PHASE,FREQUENCY,FREQUENCY_SCHEDULE,ACTION_DAYS,AUDIENCE,EXCLUDED_AUDIENCE,LOCATION,INTEREST_CATEGORY_V_2,PANGLE_BLOCK_APP_LIST_ID,ACTION_CATEGORIES,PLACEMENTS,KEYWORDS,AGE_GROUPS,LANGUAGES,OPERATING_SYSTEMS,NETWORK_TYPES,CARRIERS,VIDEO_ACTIONS,PACKAGE,_FIVETRAN_SYNCED" as record from raw.tiktok_adgroup_history_data
4: )
5: select
6:         'tiktok_ads' as source_relation,
7:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 1), '""', '"')) as VARCHAR) as ad_group_id,
8:         try_cast(nullif(trim(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 2), '""', '"'))), '') as TIMESTAMP) as updated_at,
9:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 3), '""', '"')) as VARCHAR) as advertiser_id,
10:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 4), '""', '"')) as VARCHAR) as campaign_id,
11:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 59), '""', '"')) as VARCHAR) as interest_category,
12:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 6), '""', '"')) as VARCHAR) as ad_group_name,
13:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 53), '""', '"')) as VARCHAR) as frequency,
14:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 54), '""', '"')) as VARCHAR) as frequency_schedule,
15:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 64), '""', '"')) as VARCHAR) as age_groups,
16:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 65), '""', '"')) as VARCHAR) as languages,
17:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 18), '""', '"')) as VARCHAR) as gender,
18:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 21), '""', '"')) as VARCHAR) as budget_mode,
19:         try_cast(nullif(trim(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 39), '""', '"'))), '') as DOUBLE) as budget,
20:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 9), '""', '"')) as VARCHAR) as landing_page_url,
21:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 15), '""', '"')) as VARCHAR) as secondary_optimization_event,
22:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 16), '""', '"')) as VARCHAR) as creative_material_mode,
23:         cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 17), '""', '"')) as VARCHAR) as audience_type
24: from source_data
25: ), ranked as (
26:     select *, max(updated_at) over (partition by source_relation, ad_group_id) as max_updated_at
27:     from staged
28: )
29: select
30:     source_relation,
31:     ad_group_id,
32:     updated_at,
33:     advertiser_id,
34:     campaign_id,
35:     interest_category,
36:     ad_group_name,
37:     frequency,
38:     frequency_schedule,
39:     age_groups,
40:     languages,
41:     gender,
42:     budget_mode,
43:     budget,
44:     landing_page_url,
45:     secondary_optimization_event,
46:     creative_material_mode,
47:     audience_type,
48:     (updated_at is not distinct from max_updated_at) as is_most_recent_record
49: from ranked
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__ad_group_history.sql`；SHA-256 `b97d701cccb8e724097abc681fea4b283000d14b2b2242d6e0baa6e122f455ab`。

```text
1: with rows as (
2:   select "ADGROUP_ID,UPDATED_AT,ADVERTISER_ID,CAMPAIGN_ID,CREATE_TIME,ADGROUP_NAME,PLACEMENT_TYPE,PROFILE_IMAGE,LANDING_PAGE_URL,DISPLAY_NAME,APP_TYPE,APP_DOWNLOAD_URL,APP_NAME,OPTIMIZATION_EVENT,SECONDARY_OPTIMIZATION_EVENT,CREATIVE_MATERIAL_MODE,AUDIENCE_TYPE,GENDER,MIN_ANDROID_VERSION,MIN_IOS_VERSION,BUDGET_MODE,SCHEDULE_TYPE,DAYPARTING,OPTIMIZATION_GOAL,CPV_VIDEO_DURATION,PACING,BILLING_EVENT,BID_TYPE,DEEP_BID_TYPE,IMPRESSION_TRACKING_URL,CLICK_TRACKING_URL,SECONDARY_STATUS,OPERATION_STATUS,STATISTIC_TYPE,VIDEO_DOWNLOAD,OPEN_URL,OPEN_URL_TYPE,FALLBACK_TYPE,BUDGET,BID_PRICE,CONVERSION_BID_PRICE,DEEP_CPA_BID,SCHEDULE_START_TIME,SCHEDULE_END_TIME,APP_ID,PIXEL_ID,INVENTORY_FILTER_ENABLED,IS_HFSS,IS_NEW_STRUCTURE,CATEGORY,IS_COMMENT_DISABLE,SKIP_LEARNING_PHASE,FREQUENCY,FREQUENCY_SCHEDULE,ACTION_DAYS,AUDIENCE,EXCLUDED_AUDIENCE,LOCATION,INTEREST_CATEGORY_V_2,PANGLE_BLOCK_APP_LIST_ID,ACTION_CATEGORIES,PLACEMENTS,KEYWORDS,AGE_GROUPS,LANGUAGES,OPERATING_SYSTEMS,NETWORK_TYPES,CARRIERS,VIDEO_ACTIONS,PACKAGE,_FIVETRAN_SYNCED" as row_str
3:   from raw.tiktok_adgroup_history_data
4: ), fields as (
5:   select
6:     'raw.tiktok_adgroup_history_data' as source_relation,
7:     split_part(row_str, ',', 1) as ad_group_id,
8:     try_cast(split_part(row_str, ',', 2) as timestamp) as updated_at,
9:     split_part(row_str, ',', 3) as advertiser_id,
10:     split_part(row_str, ',', 4) as campaign_id,
11:     split_part(row_str, ',', 56) as interest_category,
12:     split_part(row_str, ',', 6) as ad_group_name,
13:     split_part(row_str, ',', 53) as frequency,
14:     split_part(row_str, ',', 54) as frequency_schedule,
15:     split_part(row_str, ',', 64) as age_groups,
16:     split_part(row_str, ',', 67) as languages,
17:     split_part(row_str, ',', 18) as gender,
18:     split_part(row_str, ',', 21) as budget_mode,
19:     try_cast(split_part(row_str, ',', 38) as double) as budget,
20:     split_part(row_str, ',', 9) as landing_page_url,
21:     split_part(row_str, ',', 15) as secondary_optimization_event,
22:     split_part(row_str, ',', 16) as creative_material_mode,
23:     split_part(row_str, ',', 17) as audience_type
24:   from rows
25: ), final as (
26:   select
27:     *,
28:     row_number() over (partition by source_relation, ad_group_id order by updated_at desc) = 1 as is_most_recent_record
29:   from fields
30: )
31: select *
32: from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- source_relation（A）：**看到了但没提**；事件 11、12、15、16、41、42。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。

- budget（O）：**看到了但没提**；事件 11、12、15、16、41、42。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。

- age_groups_parser（O）：**看到了但没提**；事件 11、12、15、16、41、42。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 11：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/11.json`；命令首行：`cat tiktok_ads_start.yaml`。
event 12：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/12.json`；原始观察输出。
event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/15.json`；命令首行：`python - <<'PY'`。
event 16：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/16.json`；原始观察输出。
event 41：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/41.json`；命令首行：`python - <<'PY'`。
event 42：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/42.json`；原始观察输出。

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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('tiktok_adgroup_history_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["tiktok_adgroup_history_data","ADGROUP_ID,UPDATED_AT,ADVERTISER_ID,CAMPAIGN_ID,CREATE_TIME,ADGROUP_NAME,PLACEMENT_TYPE,PROFILE_IMAGE,LANDING_PAGE_URL,DISPLAY_NAME,APP_TYPE,APP_DOWNLOAD_URL,APP_NAME,OPTIMIZATION_EVENT,SECONDARY_OPTIMIZATION_EVENT,CREATIVE_MATERIAL_MODE,AUDIENCE_TYPE,GENDER,MIN_ANDROID_VERSION,MIN_IOS_VERSION,BUDGET_MODE,SCHEDULE_TYPE,DAYPARTING,OPTIMIZATION_GOAL,CPV_VIDEO_DURATION,PACING,BILLING_EVENT,BID_TYPE,DEEP_BID_TYPE,IMPRESSION_TRACKING_URL,CLICK_TRACKING_URL,SECONDARY_STATUS,OPERATION_STATUS,STATISTIC_TYPE,VIDEO_DOWNLOAD,OPEN_URL,OPEN_URL_TYPE,FALLBACK_TYPE,BUDGET,BID_PRICE,CONVERSION_BID_PRICE,DEEP_CPA_BID,SCHEDULE_START_TIME,SCHEDULE_END_TIME,APP_ID,PIXEL_ID,INVENTORY_FILTER_ENABLED,IS_HFSS,IS_NEW_STRUCTURE,CATEGORY,IS_COMMENT_DISABLE,SKIP_LEARNING_PHASE,FREQUENCY,FREQUENCY_SCHEDULE,ACTION_DAYS,AUDIENCE,EXCLUDED_AUDIENCE,LOCATION,INTEREST_CATEGORY_V_2,PANGLE_BLOCK_APP_LIST_ID,ACTION_CATEGORIES,PLACEMENTS,KEYWORDS,AGE_GROUPS,LANGUAGES,OPERATING_SYSTEMS,NETWORK_TYPES,CARRIERS,VIDEO_ACTIONS,PACKAGE,_FIVETRAN_SYNCED","VARCHAR"]]}
```


### 诊断：agent实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_tiktok_ads__ad_group_history'
```


```json
{"columns":["column_name","data_type"],"rows":[["source_relation","VARCHAR"],["ad_group_id","VARCHAR"],["updated_at","TIMESTAMP"],["advertiser_id","VARCHAR"],["campaign_id","VARCHAR"],["interest_category","VARCHAR"],["ad_group_name","VARCHAR"],["frequency","VARCHAR"],["frequency_schedule","VARCHAR"],["age_groups","VARCHAR"],["languages","VARCHAR"],["gender","VARCHAR"],["budget_mode","VARCHAR"],["budget","DOUBLE"],["landing_page_url","VARCHAR"],["secondary_optimization_event","VARCHAR"],["creative_material_mode","VARCHAR"],["audience_type","VARCHAR"],["is_most_recent_record","BOOLEAN"]]}
```


### 诊断：agent有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
SELECT age_groups,budget,source_relation FROM staging.stg_tiktok_ads__ad_group_history LIMIT 3
```


```json
{"columns":["age_groups","budget","source_relation"],"rows":[["[ \"AGE_25_34\", \"AGE_35_44\", \"AGE_45_54\", \"AGE_55_100\", \"AGE_18_24\" ]",500.0,"tiktok_ads"],["[ \"AGE_25_34\", \"AGE_35_44\", \"AGE_45_54\", \"AGE_55_100\", \"AGE_18_24\" ]",0.0,"tiktok_ads"],["[ \"AGE_25_34\", \"AGE_35_44\", \"AGE_45_54\", \"AGE_55_100\", \"AGE_18_24\" ]",900.0,"tiktok_ads"]]}
```


### 诊断：gold实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_tiktok_ads__ad_group_history'
```


```json
{"columns":["column_name","data_type"],"rows":[["source_relation","VARCHAR"],["ad_group_id","VARCHAR"],["updated_at","TIMESTAMP"],["advertiser_id","VARCHAR"],["campaign_id","VARCHAR"],["interest_category","VARCHAR"],["ad_group_name","VARCHAR"],["frequency","VARCHAR"],["frequency_schedule","VARCHAR"],["age_groups","VARCHAR"],["languages","VARCHAR"],["gender","VARCHAR"],["budget_mode","VARCHAR"],["budget","DOUBLE"],["landing_page_url","VARCHAR"],["secondary_optimization_event","VARCHAR"],["creative_material_mode","VARCHAR"],["audience_type","VARCHAR"],["is_most_recent_record","BOOLEAN"]]}
```


### 诊断：gold有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
SELECT age_groups,budget,source_relation FROM staging.stg_tiktok_ads__ad_group_history LIMIT 3
```


```json
{"columns":["age_groups","budget","source_relation"],"rows":[["\"[ \"\"AGE_25_34\"\"",null,"raw.tiktok_adgroup_history_data"],["\"[ \"\"AGE_25_34\"\"",null,"raw.tiktok_adgroup_history_data"],["\"[ \"\"AGE_25_34\"\"",null,"raw.tiktok_adgroup_history_data"]]}
```


### 诊断：gold SQL同gold输入重跑
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
with rows as (
  select "ADGROUP_ID,UPDATED_AT,ADVERTISER_ID,CAMPAIGN_ID,CREATE_TIME,ADGROUP_NAME,PLACEMENT_TYPE,PROFILE_IMAGE,LANDING_PAGE_URL,DISPLAY_NAME,APP_TYPE,APP_DOWNLOAD_URL,APP_NAME,OPTIMIZATION_EVENT,SECONDARY_OPTIMIZATION_EVENT,CREATIVE_MATERIAL_MODE,AUDIENCE_TYPE,GENDER,MIN_ANDROID_VERSION,MIN_IOS_VERSION,BUDGET_MODE,SCHEDULE_TYPE,DAYPARTING,OPTIMIZATION_GOAL,CPV_VIDEO_DURATION,PACING,BILLING_EVENT,BID_TYPE,DEEP_BID_TYPE,IMPRESSION_TRACKING_URL,CLICK_TRACKING_URL,SECONDARY_STATUS,OPERATION_STATUS,STATISTIC_TYPE,VIDEO_DOWNLOAD,OPEN_URL,OPEN_URL_TYPE,FALLBACK_TYPE,BUDGET,BID_PRICE,CONVERSION_BID_PRICE,DEEP_CPA_BID,SCHEDULE_START_TIME,SCHEDULE_END_TIME,APP_ID,PIXEL_ID,INVENTORY_FILTER_ENABLED,IS_HFSS,IS_NEW_STRUCTURE,CATEGORY,IS_COMMENT_DISABLE,SKIP_LEARNING_PHASE,FREQUENCY,FREQUENCY_SCHEDULE,ACTION_DAYS,AUDIENCE,EXCLUDED_AUDIENCE,LOCATION,INTEREST_CATEGORY_V_2,PANGLE_BLOCK_APP_LIST_ID,ACTION_CATEGORIES,PLACEMENTS,KEYWORDS,AGE_GROUPS,LANGUAGES,OPERATING_SYSTEMS,NETWORK_TYPES,CARRIERS,VIDEO_ACTIONS,PACKAGE,_FIVETRAN_SYNCED" as row_str
  from raw.tiktok_adgroup_history_data
), fields as (
  select
    'raw.tiktok_adgroup_history_data' as source_relation,
    split_part(row_str, ',', 1) as ad_group_id,
    try_cast(split_part(row_str, ',', 2) as timestamp) as updated_at,
    split_part(row_str, ',', 3) as advertiser_id,
    split_part(row_str, ',', 4) as campaign_id,
    split_part(row_str, ',', 56) as interest_category,
    split_part(row_str, ',', 6) as ad_group_name,
    split_part(row_str, ',', 53) as frequency,
    split_part(row_str, ',', 54) as frequency_schedule,
    split_part(row_str, ',', 64) as age_groups,
    split_part(row_str, ',', 67) as languages,
    split_part(row_str, ',', 18) as gender,
    split_part(row_str, ',', 21) as budget_mode,
    try_cast(split_part(row_str, ',', 38) as double) as budget,
    split_part(row_str, ',', 9) as landing_page_url,
    split_part(row_str, ',', 15) as secondary_optimization_event,
    split_part(row_str, ',', 16) as creative_material_mode,
    split_part(row_str, ',', 17) as audience_type
  from rows
), final as (
  select
    *,
    row_number() over (partition by source_relation, ad_group_id order by updated_at desc) = 1 as is_most_recent_record
  from fields
)
select *
from final
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2504|2504|0|0|是|
|L1|2504|2504|0|0|是|
|L2|2504|2504|0|0|是|
|L3|2504|2504|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 独立单点重跑

### 024_reruns_impl-024_stg_tiktok_ads__ad_group_history.json
[024_reruns_impl-024_stg_tiktok_ads__ad_group_history.json](../024_reruns_impl-024_stg_tiktok_ads__ad_group_history.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/tiktok_ads.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2504|2504|2504|7512|否|
|L1|2504|2504|2504|7512|否|
|L2|2504|2504|2504|7512|否|
|L3|2504|2504|2504|7512|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L1：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L2：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L3：`{"age_groups":2504,"budget":2504,"source_relation":2504}`

#### baseline
私有SQL：`data/024_work/impl-024_stg_tiktok_ads__ad_group_history/baseline.sql`；SHA-256 `e8c11c44d1d1e2b9479b8cf0957ee6485fdfa764b21a2923a58d1ce05c1bc6c5`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2504|2504|2504|7512|否|
|L1|2504|2504|2504|7512|否|
|L2|2504|2504|2504|7512|否|
|L3|2504|2504|2504|7512|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L1：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L2：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L3：`{"age_groups":2504,"budget":2504,"source_relation":2504}`

#### source_relation
主因；类别候选A。契约未规定source_relation常量字面量；gold使用raw表名。
相对本轮基线：行减少0，格减少2504。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第6行、offset 1139起替换；其他字节相同。
原表达式：
```sql
'tiktok_ads' as source_relation
```

修改后：
```sql
'raw.tiktok_adgroup_history_data' as source_relation
```

私有SQL：`data/024_work/impl-024_stg_tiktok_ads__ad_group_history/source_relation.sql`；SHA-256 `3c69b72203a5195da754bd4adbbbf4efd1d43a8f2f23b1ebf50f3b091f72b83d`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2504|2504|2504|5008|否|
|L1|2504|2504|2504|5008|否|
|L2|2504|2504|2504|5008|否|
|L3|2504|2504|2504|5008|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"age_groups":2504,"budget":2504}`
- L1：`{"age_groups":2504,"budget":2504}`
- L2：`{"age_groups":2504,"budget":2504}`
- L3：`{"age_groups":2504,"budget":2504}`

#### interest_category
不计参与因素；类别候选O。agent按原始header位置取对应字段；gold取其他位置。需数据与header诊断，不把gold位置当作业务真值。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 1885起替换；其他字节相同。
原表达式：
```sql
cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 59), '""', '"')) as VARCHAR) as interest_category
```

修改后：
```sql
split_part(record, ',', 56) as interest_category
```

私有SQL：`data/024_work/impl-024_stg_tiktok_ads__ad_group_history/interest_category.sql`；SHA-256 `dc62e59f59c164263f5049d3c5687864b0b5f7bd43287e7e62eacf393d592542`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2504|2504|2504|7512|否|
|L1|2504|2504|2504|7512|否|
|L2|2504|2504|2504|7512|否|
|L3|2504|2504|2504|7512|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L1：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L2：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L3：`{"age_groups":2504,"budget":2504,"source_relation":2504}`

#### languages
不计参与因素；类别候选O。agent按原始header位置取对应字段；gold取其他位置。需数据与header诊断，不把gold位置当作业务真值。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第16行、offset 2751起替换；其他字节相同。
原表达式：
```sql
cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 65), '""', '"')) as VARCHAR) as languages
```

修改后：
```sql
split_part(record, ',', 67) as languages
```

私有SQL：`data/024_work/impl-024_stg_tiktok_ads__ad_group_history/languages.sql`；SHA-256 `a42a3e9f904acc0e179ba7db54050c18d72cac27d3f47cf4d2b259e29e87bcc0`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2504|2504|2504|7512|否|
|L1|2504|2504|2504|7512|否|
|L2|2504|2504|2504|7512|否|
|L3|2504|2504|2504|7512|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L1：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L2：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L3：`{"age_groups":2504,"budget":2504,"source_relation":2504}`

#### budget
主因；类别候选O。agent按原始header位置取对应字段；gold取其他位置。需数据与header诊断，不把gold位置当作业务真值。
相对本轮基线：行减少0，格减少2504。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第19行、offset 3257起替换；其他字节相同。
原表达式：
```sql
try_cast(nullif(trim(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 39), '""', '"'))), '') as DOUBLE) as budget
```

修改后：
```sql
try_cast(split_part(record, ',', 38) as DOUBLE) as budget
```

私有SQL：`data/024_work/impl-024_stg_tiktok_ads__ad_group_history/budget.sql`；SHA-256 `8b60645cbb5f818aca3c60424a0aa7756c9bc3789a0e474f3e7952b31f99e1ff`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2504|2504|2504|5008|否|
|L1|2504|2504|2504|5008|否|
|L2|2504|2504|2504|5008|否|
|L3|2504|2504|2504|5008|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"age_groups":2504,"source_relation":2504}`
- L1：`{"age_groups":2504,"source_relation":2504}`
- L2：`{"age_groups":2504,"source_relation":2504}`
- L3：`{"age_groups":2504,"source_relation":2504}`
### 024_supplement_reruns_impl-024_stg_tiktok_ads__ad_group_history.json
[024_supplement_reruns_impl-024_stg_tiktok_ads__ad_group_history.json](../024_supplement_reruns_impl-024_stg_tiktok_ads__ad_group_history.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/tiktok_ads.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2504|2504|2504|7512|否|
|L1|2504|2504|2504|7512|否|
|L2|2504|2504|2504|7512|否|
|L3|2504|2504|2504|7512|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L1：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L2：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L3：`{"age_groups":2504,"budget":2504,"source_relation":2504}`

#### baseline
私有SQL：`data/024_supplement_work/impl-024_stg_tiktok_ads__ad_group_history/baseline.sql`；SHA-256 `e8c11c44d1d1e2b9479b8cf0957ee6485fdfa764b21a2923a58d1ce05c1bc6c5`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2504|2504|2504|7512|否|
|L1|2504|2504|2504|7512|否|
|L2|2504|2504|2504|7512|否|
|L3|2504|2504|2504|7512|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L1：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L2：`{"age_groups":2504,"budget":2504,"source_relation":2504}`
- L3：`{"age_groups":2504,"budget":2504,"source_relation":2504}`

#### age_groups_parser
主因；类别候选O。agent正确保留quoted array完整字段，gold简单按逗号分割截断；以header和CSV诊断为证。
相对本轮基线：行减少0，格减少2504。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第15行、offset 2581起替换；其他字节相同。
原表达式：
```sql
cast(trim(both '"' from replace(list_extract(regexp_extract_all(record, '(^|,)("(?:[^"]|"")*"|\[[^\]]*\]|[^,]*)', 2), 64), '""', '"')) as VARCHAR) as age_groups
```

修改后：
```sql
split_part(record, ',', 64) as age_groups
```

私有SQL：`data/024_supplement_work/impl-024_stg_tiktok_ads__ad_group_history/age_groups_parser.sql`；SHA-256 `d243af28b94c01f6eeca122b0b793014e47f55cfd29a368987eae0c8f2cdd099`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2504|2504|2504|5008|否|
|L1|2504|2504|2504|5008|否|
|L2|2504|2504|2504|5008|否|
|L3|2504|2504|2504|5008|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"budget":2504,"source_relation":2504}`
- L1：`{"budget":2504,"source_relation":2504}`
- L2：`{"budget":2504,"source_relation":2504}`
- L3：`{"budget":2504,"source_relation":2504}`
## 规则问题

CSV header提供字段定位，agent完整解析和gold简单split不同；按字段含义/原值冲突归O，未规定source_relation常量归A。若将字段含义也视作不够明确，可读A；保留该边界供审阅。

