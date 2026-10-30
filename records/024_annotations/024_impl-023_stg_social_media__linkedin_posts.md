# impl-023 · stg_social_media__linkedin_posts

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**A**；把握：中。

created_timestamp采用历史created_time；该关联全不匹配，gold采用同步时间。契约未指定该时间源；同步时间可用不等于业务创建时间正确。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-023_stg_social_media__linkedin_posts.md](../024_packages/024_impl-023_stg_social_media__linkedin_posts.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。

```text
331:     - name: stg_social_media__linkedin_posts
332:       description: "Minimal staging representation of LinkedIn organization UGC posts with standardized identifiers and URL."
333:       source_table: raw.linkedin_pages_organization_ugc_post
334:       columns:
335:         - name: organization_id
336:           data_type: VARCHAR
337:         - name: post_id
338:           data_type: VARCHAR
339:         - name: created_timestamp
340:           data_type: TIMESTAMP
341:         - name: platform
342:           data_type: VARCHAR
343:         - name: post_message
344:           data_type: VARCHAR
345:         - name: content_type
346:           data_type: VARCHAR
347:         - name: post_url
348:           data_type: VARCHAR
349:           validation_rules:
350:             - rule: "post_url RLIKE '^https://www.linkedin.com/feed/update/.+'"
351:               on_failure: correct
352:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__linkedin_posts.sql`；SHA-256 `9755294250d07ac813190a0347b8b26207e7c198621cb24997410d7d8aa69452`。

```text
1: with post_metrics as (
2:     select
3:         _share_entity_urn,
4:         max(click_count) as click_count,
5:         max(impression_count) as impression_count,
6:         max(like_count) as like_count,
7:         max(share_count) as share_count,
8:         max(comment_count) as comment_count,
9:         max(engagement) as engagement
10:     from raw.linkedin_pages_share_statistic
11:     group by _share_entity_urn
12: )
13: select
14:     cast(o.organiation_id as varchar) as organization_id,
15:     o.ugc_post_id::varchar as post_id,
16:     h.created_time::timestamp as created_timestamp,
17:     'linkedin'::varchar as platform,
18:     coalesce(pc.article_title, pc.media_title, h.commentary)::varchar as post_message,
19:     pc.type::varchar as content_type,
20:     ('https://www.linkedin.com/feed/update/' || o.ugc_post_id)::varchar as post_url
21: from raw.linkedin_pages_organization_ugc_post o
22: left join raw.linkedin_pages_ugc_post_history h on h.id = o.ugc_post_id
23: left join raw.linkedin_pages_post_content pc on pc.post_id = regexp_replace(o.ugc_post_id, '^urn:li:share:', 'urn:li:share:')
24: left join post_metrics pm on pm._share_entity_urn = o.ugc_post_id
25: where o.organiation_id is not null
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__linkedin_posts.sql`；SHA-256 `3dfb4bb0c0e85b7feac2c4f45f622ed664879d313ff26ea024c9930112196909`。

```text
1: -- LinkedIn posts staging table - Simplified version
2: -- Based on actual table structure
3: 
4: -- Source posts from organization UGC posts
5: SELECT
6:     CAST(organiation_id AS VARCHAR) AS organization_id,
7:     CAST(ugc_post_id AS VARCHAR) AS post_id,
8:     _fivetran_synced AS created_timestamp,
9:     'linkedin' AS platform,
10:     CONCAT('LinkedIn Post ', ugc_post_id) AS post_message,
11:     'text' AS content_type,
12:     CONCAT('https://www.linkedin.com/feed/update/', ugc_post_id) AS post_url
13: FROM raw.linkedin_pages_organization_ugc_post
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- created_source（A）：**针对本表的具体说明**；事件 53。
原句：

```
LinkedIn staging 契约指定的关联源表缺少可直接匹配的 UGC 历史主键，关联历史中的 `created_time` 无匹配时为空
```

event 53：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/53.json`；命令首行：`ls -ld /workspace /tmp; id; cat > result.md <<'EOF'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】
已按配置顺序完成并写入 `sql/staging/`、`sql/intermediate/` 和 `sql/marts/` 下的 16 个 DuckDB SQL 模型。SQL 使用直接的 `schema.table` 上游引用，无 dbt `ref()`，且文件末尾均无分号。

实现覆盖：
- Staging：7 个合同表，包含字段映射、类型转换、数据清洗、无效键/时区行过滤、指标空值处理及平台相关源表连接。
- Intermediate：5 个平台报告模型，包含合同规定的过滤、指标标准化、聚合、内容分类、比率、时间桶及窗口逻辑。
- Marts：4 个模型，包含平台统一 rollup、每日 KPI 日期 spine、周留存 cohort 及月度 CTR/KPI 聚合。

**验证结果**
- `python run.py` 执行成功，第二次复跑也成功。
- Staging：7/7；Intermediate：5/5；Marts：4/4 模型创建成功。
- 文件检查确认无末尾分号及 `ref()` 引用。
- 无 SQL 执行失败，因此没有失败语句或修复项。

**数据质量及残余影响**
运行环境日期为 2026-10-25，而原始 Facebook、Instagram、Twitter、YouTube 数据最大日期约在 2023 年，LinkedIn 关联历史资料也主要在 2021—2023 年。按合同中相对于 `CURRENT_DATE` 的最近 2 年/4 年过滤要求，记录不在窗口内；本次中间层及 marts 因此为空。这是合同时间窗与源数据时效共同导致的结果，不是 SQL 执行错误；补充时间窗内源数据后，重新执行即可纳入。

合同与源结构存在的缺口：LinkedIn staging 契约指定的关联源表缺少可直接匹配的 UGC 历史主键，关联历史中的 `created_time` 无匹配时为空，此类记录随后按中间层的非空时间要求排除。LinkedIn staging 契约也未提供中间层逻辑所需的互动指标/源 engagement rate，因此缺失指标按模型逻辑默认 0。`account_history.id` 在源中为 VARCHAR，但契约要求 BIGINT；不可转换的键按无效主键处理并删除。上述处理不伪造时间或指标，残余影响是相关记录被排除或其互动量无法体现。

过滤遵循 YAML 的时间窗口及关键字段要求；来源重复按合同保留，未额外去重。
```

## 查询

核实查询 **2** 条；代价档：**多条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('linkedin_pages_organization_ugc_post','linkedin_pages_post_content','linkedin_pages_share_statistic','linkedin_pages_ugc_post_history') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["linkedin_pages_organization_ugc_post","organiation_id","BIGINT"],["linkedin_pages_organization_ugc_post","ugc_post_id","VARCHAR"],["linkedin_pages_organization_ugc_post","_fivetran_synced","TIMESTAMP"],["linkedin_pages_post_content","_fivetran_synced","TIMESTAMP"],["linkedin_pages_post_content","_fivetran_id","VARCHAR"],["linkedin_pages_post_content","post_id","VARCHAR"],["linkedin_pages_post_content","type","VARCHAR"],["linkedin_pages_post_content","article_title","VARCHAR"],["linkedin_pages_post_content","media_id","VARCHAR"],["linkedin_pages_post_content","media_title","VARCHAR"],["linkedin_pages_post_content","media_alt_text","VARCHAR"],["linkedin_pages_share_statistic","_fivetran_id","VARCHAR"],["linkedin_pages_share_statistic","_fivetran_synced","TIMESTAMP"],["linkedin_pages_share_statistic","_organization_entity_urn","VARCHAR"],["linkedin_pages_share_statistic","_share_entity_urn","VARCHAR"],["linkedin_pages_share_statistic","click_count","BIGINT"],["linkedin_pages_share_statistic","comment_count","BIGINT"],["linkedin_pages_share_statistic","engagement","DOUBLE"],["linkedin_pages_share_statistic","impression_count","BIGINT"],["linkedin_pages_share_statistic","like_count","BIGINT"],["linkedin_pages_share_statistic","share_count","BIGINT"],["linkedin_pages_ugc_post_history","_fivetran_synced","TIMESTAMP"],["linkedin_pages_ugc_post_history","author","VARCHAR"],["linkedin_pages_ugc_post_history","commentary","VARCHAR"],["linkedin_pages_ugc_post_history","container_entity","VARCHAR"],["linkedin_pages_ugc_post_history","created_actor","VARCHAR"],["linkedin_pages_ugc_post_history","created_time","TIMESTAMP"],["linkedin_pages_ugc_post_history","distribution_external_distribution_channels","VARCHAR"],["linkedin_pages_ugc_post_history","distribution_feed_distribution","VARCHAR"],["linkedin_pages_ugc_post_history","first_published_at","TIMESTAMP"],["linkedin_pages_ugc_post_history","id","VARCHAR"],["linkedin_pages_ugc_post_history","last_modified_actor","VARCHAR"],["linkedin_pages_ugc_post_history","last_modified_time","TIMESTAMP"],["linkedin_pages_ugc_post_history","lifecycle_state","VARCHAR"],["linkedin_pages_ugc_post_history","response_context_parent","VARCHAR"],["linkedin_pages_ugc_post_history","response_context_root","VARCHAR"],["linkedin_pages_ugc_post_history","visibility","VARCHAR"]]}
```


### 核实：UGC历史关联覆盖
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT count(*) n,count(h.id) history_match,count(h.created_time) creation_available,count(o._fivetran_synced) sync_available FROM raw.linkedin_pages_organization_ugc_post o LEFT JOIN raw.linkedin_pages_ugc_post_history h ON o.ugc_post_id=h.id
```


```json
{"columns":["n","history_match","creation_available","sync_available"],"rows":[[100,0,0,100]]}
```

## 独立单点重跑

### 024_reruns_impl-023_stg_social_media__linkedin_posts.json
[024_reruns_impl-023_stg_social_media__linkedin_posts.json](../024_reruns_impl-023_stg_social_media__linkedin_posts.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|100|100|100|100|否|
|L1|100|100|100|100|否|
|L2|100|100|100|100|否|
|L3|100|100|100|100|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_timestamp":100}`
- L1：`{"created_timestamp":100}`
- L2：`{"created_timestamp":100}`
- L3：`{"created_timestamp":100}`

#### baseline
私有SQL：`data/024_work/impl-023_stg_social_media__linkedin_posts/baseline.sql`；SHA-256 `9755294250d07ac813190a0347b8b26207e7c198621cb24997410d7d8aa69452`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|100|100|100|100|否|
|L1|100|100|100|100|否|
|L2|100|100|100|100|否|
|L3|100|100|100|100|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_timestamp":100}`
- L1：`{"created_timestamp":100}`
- L2：`{"created_timestamp":100}`
- L3：`{"created_timestamp":100}`

#### created_source
主因；类别候选A。契约未定created_timestamp源列；gold同步时间，agent历史created_time。
相对本轮基线：行减少100，格减少100。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第16行、offset 501起替换；其他字节相同。
原表达式：
```sql
h.created_time::timestamp
```

修改后：
```sql
o._fivetran_synced::timestamp
```

私有SQL：`data/024_work/impl-023_stg_social_media__linkedin_posts/created_source.sql`；SHA-256 `9f0dcee0cc2b76c3fa7100fe7f1067ff7aa285bedc2c6f0ab1a3c924a3d5d401`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|100|100|0|0|是|
|L1|100|100|0|0|是|
|L2|100|100|0|0|是|
|L3|100|100|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

#### message_source
不计参与因素；类别候选A。契约未规定post_message内容来源。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第18行、offset 590起替换；其他字节相同。
原表达式：
```sql
coalesce(pc.article_title, pc.media_title, h.commentary)::varchar
```

修改后：
```sql
concat('LinkedIn Post ',o.ugc_post_id)::varchar
```

私有SQL：`data/024_work/impl-023_stg_social_media__linkedin_posts/message_source.sql`；SHA-256 `8feab590d45bfb2b259564dbf198188dae87a5c2cfa54cfaa705d0038b63b81b`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|100|100|100|100|否|
|L1|100|100|100|100|否|
|L2|100|100|100|100|否|
|L3|100|100|100|100|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_timestamp":100}`
- L1：`{"created_timestamp":100}`
- L2：`{"created_timestamp":100}`
- L3：`{"created_timestamp":100}`

#### content_type
不计参与因素；类别候选A。契约未规定content_type常量或内容表来源。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第19行、offset 677起替换；其他字节相同。
原表达式：
```sql
pc.type::varchar
```

修改后：
```sql
'text'::varchar
```

私有SQL：`data/024_work/impl-023_stg_social_media__linkedin_posts/content_type.sql`；SHA-256 `6fbd39fe971b0ed1e7bab1231ba053d81bbd92af19ecdd0b076e058d078dbde3`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|100|100|100|100|否|
|L1|100|100|100|100|否|
|L2|100|100|100|100|否|
|L3|100|100|100|100|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_timestamp":100}`
- L1：`{"created_timestamp":100}`
- L2：`{"created_timestamp":100}`
- L3：`{"created_timestamp":100}`
## 规则问题

历史关联零匹配可读为U，但同步时间不证明创建时间语义，选择A。

