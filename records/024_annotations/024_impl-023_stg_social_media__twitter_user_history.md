# impl-023 · stg_social_media__twitter_user_history

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

agent输出契约BIGINT id及计数，gold保留非数值VARCHAR id和DOUBLE计数；11行因此过滤，另有4格类型表示差异。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-023_stg_social_media__twitter_user_history.md](../024_packages/024_impl-023_stg_social_media__twitter_user_history.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。

```text
58:     - name: stg_social_media__twitter_user_history
59:       description: "Cleaned and standardized Twitter user profile attributes for safe downstream joins and reporting."
60:       source_table: raw.twitter_user_history
61:       columns:
62:         - name: id
63:           data_type: BIGINT
64:           constraints: [not_null]
65:         - name: _fivetran_synced
66:           data_type: TIMESTAMP
67:         - name: screen_name
68:           data_type: VARCHAR
69:           constraints: [not_null]
70:           description: >
71:             Best-effort cleaning to keep only [A-Za-z0-9_]; rows with NULL/blank or harmful characters are removed.
72:           validation_rules:
73:             - rule: "screen_name = CASE WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '') END"
74:               on_failure: correct
75:             - rule: "screen_name IS NOT NULL AND NOT (screen_name RLIKE '[!@#$%^&*()+=<>?}{|,]')"
76:               on_failure: delete_row
77:         - name: url
78:           data_type: VARCHAR
79:           validation_rules:
80:             - rule: "url IS NULL OR url RLIKE '^https?://[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?'"
81:               on_failure: nullify_field
82:             - rule: "url IS NULL OR (url RLIKE '^(https?://)?[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?' AND url RLIKE '^https?://')"
83:               on_failure: correct
84:         - name: created_at
85:           data_type: TIMESTAMP
86:         - name: followers_count
87:           data_type: BIGINT
88:         - name: following_count
89:           data_type: BIGINT
90:           description: "Renamed from friends_count."
91:         - name: listed_count
92:           data_type: BIGINT
93:         - name: favourites_count
94:           data_type: BIGINT
95:         - name: statuses_count
96:           data_type: BIGINT
97:         - name: verified
98:           data_type: BOOLEAN
99:         - name: protected
100:           data_type: BOOLEAN
101:           description: "Derived from protected_user: TRUE if protected_user=TRUE else FALSE."
102:         - name: default_profile
103:           data_type: BOOLEAN
104:         - name: default_profile_image
105:           data_type: BOOLEAN
106:         - name: location
107:           data_type: VARCHAR
108:         - name: description
109:           data_type: VARCHAR
110:         - name: time_zone
111:           data_type: VARCHAR
112:         - name: lang
113:           data_type: VARCHAR
114:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__twitter_user_history.sql`；SHA-256 `84b7b49c6e5b15f8812c8770f4c02c296f3e6f85985b5a9ac0218856e79acf1a`。

```text
1: with user_cleaned as (
2:     select
3:         try_cast(id as bigint) as id,
4:         _fivetran_synced::timestamp as _fivetran_synced,
5:         case when screen_name is null or trim(screen_name) = '' then null
6:              else regexp_replace(screen_name, '[^A-Za-z0-9_]', '', 'g') end as screen_name,
7:         case
8:             when url is null then null
9:             when regexp_matches(url, '^(https?://)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?')
10:                 then case when regexp_matches(url, '^https?://') then url else 'https://' || url end
11:             else null
12:         end as url,
13:         created_at::timestamp as created_at,
14:         try_cast(followers_count as bigint) as followers_count,
15:         try_cast(friends_count as bigint) as following_count,
16:         try_cast(listed_count as bigint) as listed_count,
17:         try_cast(favourites_count as bigint) as favourites_count,
18:         try_cast(statuses_count as bigint) as statuses_count,
19:         verified::boolean as verified,
20:         coalesce(protected_user, false)::boolean as protected,
21:         default_profile::boolean as default_profile,
22:         default_profile_image::boolean as default_profile_image,
23:         location::varchar as location,
24:         description::varchar as description,
25:         time_zone::varchar as time_zone,
26:         lang::varchar as lang
27:     from raw.twitter_user_history
28: )
29: select *
30: from user_cleaned
31: where id is not null
32:   and screen_name is not null
33:   and screen_name <> ''
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__twitter_user_history.sql`；SHA-256 `392ac93ebc49fa216f158692d5fd0490d69f06f3b217a9e5a63c05e0079e767f`。

```text
1: -- Twitter user history staging table
2: -- Applies data validation and cleaning rules
3: 
4: WITH source_data AS (
5:     SELECT
6:         id,
7:         _fivetran_synced,
8:         screen_name,
9:         url,
10:         created_at,
11:         followers_count,
12:         friends_count,
13:         listed_count,
14:         favourites_count,
15:         statuses_count,
16:         verified,
17:         CASE WHEN protected_user = TRUE THEN TRUE ELSE FALSE END AS protected,
18:         default_profile,
19:         default_profile_image,
20:         location,
21:         description,
22:         time_zone,
23:         lang
24:     FROM raw.twitter_user_history
25: ),
26: 
27: cleaned_data AS (
28:     SELECT
29:         id,
30:         _fivetran_synced,
31:         -- Apply screen_name validation and cleaning
32:         CASE
33:             WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL
34:             WHEN REGEXP_MATCHES(screen_name, '^[A-Za-z0-9_]{3,15}$') THEN screen_name
35:             ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '')
36:         END AS screen_name,
37:         -- Apply URL validation and cleaning
38:         CASE
39:             WHEN url IS NULL THEN NULL
40:             WHEN REGEXP_MATCHES(url, '^https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?') THEN url
41:             WHEN REGEXP_MATCHES(url, '^(https?://)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?') THEN 'https://' || REGEXP_REPLACE(url, '^https?://', '')
42:             ELSE NULL
43:         END AS url,
44:         created_at,
45:         followers_count,
46:         friends_count AS following_count,
47:         listed_count,
48:         favourites_count,
49:         statuses_count,
50:         verified,
51:         protected,
52:         default_profile,
53:         default_profile_image,
54:         location,
55:         description,
56:         time_zone,
57:         lang
58:     FROM source_data
59:     WHERE screen_name IS NOT NULL -- Remove invalid entries
60:     AND NOT REGEXP_MATCHES(screen_name, '[!@#$%^&*()+=<>?}{|,]') -- Remove rows with harmful characters
61: )
62: 
63: SELECT *
64: FROM cleaned_data
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- 本表主要差异（O）：**看到了但没提**；事件 15、16、23、24、29。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/15.json`；命令首行：`sed -n '220,520p' docs/data_contract.yaml`。
event 16：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/16.json`；原始观察输出。
event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/23.json`；命令首行：`python - <<'PY'`。
event 24：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/24.json`；原始观察输出。
event 29：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/29.json`；命令首行：`mkdir -p sql/staging sql/intermediate sql/marts && cat > /tmp/write_sql.py <<'PY'`。

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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('twitter_user_history') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["twitter_user_history","id","VARCHAR"],["twitter_user_history","_fivetran_synced","TIMESTAMP"],["twitter_user_history","contributors_enabled","BOOLEAN"],["twitter_user_history","created_at","TIMESTAMP"],["twitter_user_history","default_profile","BOOLEAN"],["twitter_user_history","default_profile_image","BOOLEAN"],["twitter_user_history","description","VARCHAR"],["twitter_user_history","favourites_count","DOUBLE"],["twitter_user_history","followers_count","DOUBLE"],["twitter_user_history","friends_count","DOUBLE"],["twitter_user_history","geo_enabled","BOOLEAN"],["twitter_user_history","is_translation_enabled","BOOLEAN"],["twitter_user_history","is_translator","BOOLEAN"],["twitter_user_history","lang","VARCHAR"],["twitter_user_history","listed_count","DOUBLE"],["twitter_user_history","location","VARCHAR"],["twitter_user_history","name","VARCHAR"],["twitter_user_history","profile_background_image_url","VARCHAR"],["twitter_user_history","profile_background_image_url_https","VARCHAR"],["twitter_user_history","profile_background_tile","BOOLEAN"],["twitter_user_history","profile_banner_url","VARCHAR"],["twitter_user_history","profile_image_url","VARCHAR"],["twitter_user_history","profile_image_url_https","VARCHAR"],["twitter_user_history","profile_use_background_image","BOOLEAN"],["twitter_user_history","protected_user","BOOLEAN"],["twitter_user_history","screen_name","VARCHAR"],["twitter_user_history","statuses_count","DOUBLE"],["twitter_user_history","time_zone","VARCHAR"],["twitter_user_history","url","VARCHAR"],["twitter_user_history","utc_offset","DOUBLE"],["twitter_user_history","verified","BOOLEAN"]]}
```


### 核实：有害字符与全局替换差异
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE regexp_matches(screen_name,'[!@#$%^&*()+=<>?}{|,]')) harmful,count(*) FILTER(WHERE regexp_replace(screen_name,'[^A-Za-z0-9_]','')<>regexp_replace(screen_name,'[^A-Za-z0-9_]','','g')) multi_invalid FROM raw.twitter_user_history
```


```json
{"columns":["n","harmful","multi_invalid"],"rows":[[2500,6,7]]}
```


### 诊断：agent实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_social_media__twitter_user_history'
```


```json
{"columns":["column_name","data_type"],"rows":[["id","BIGINT"],["_fivetran_synced","TIMESTAMP"],["screen_name","VARCHAR"],["url","VARCHAR"],["created_at","TIMESTAMP"],["followers_count","BIGINT"],["following_count","BIGINT"],["listed_count","BIGINT"],["favourites_count","BIGINT"],["statuses_count","BIGINT"],["verified","BOOLEAN"],["protected","BOOLEAN"],["default_profile","BOOLEAN"],["default_profile_image","BOOLEAN"],["location","VARCHAR"],["description","VARCHAR"],["time_zone","VARCHAR"],["lang","VARCHAR"]]}
```


### 诊断：agent有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT id,followers_count,following_count FROM staging.stg_social_media__twitter_user_history LIMIT 3
```


```json
{"columns":["id","followers_count","following_count"],"rows":[[100071333,43200,11233]]}
```


### 诊断：gold实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_social_media__twitter_user_history'
```


```json
{"columns":["column_name","data_type"],"rows":[["id","VARCHAR"],["_fivetran_synced","TIMESTAMP"],["screen_name","VARCHAR"],["url","VARCHAR"],["created_at","TIMESTAMP"],["followers_count","DOUBLE"],["following_count","DOUBLE"],["listed_count","DOUBLE"],["favourites_count","DOUBLE"],["statuses_count","DOUBLE"],["verified","BOOLEAN"],["protected","BOOLEAN"],["default_profile","BOOLEAN"],["default_profile_image","BOOLEAN"],["location","VARCHAR"],["description","VARCHAR"],["time_zone","VARCHAR"],["lang","VARCHAR"]]}
```


### 诊断：gold有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT id,followers_count,following_count FROM staging.stg_social_media__twitter_user_history LIMIT 3
```


```json
{"columns":["id","followers_count","following_count"],"rows":[["false853637124",33559.0,289.0],["True",null,null],["True",null,null]]}
```


### 诊断：gold SQL同gold输入重跑
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
-- Twitter user history staging table
-- Applies data validation and cleaning rules

WITH source_data AS (
    SELECT
        id,
        _fivetran_synced,
        screen_name,
        url,
        created_at,
        followers_count,
        friends_count,
        listed_count,
        favourites_count,
        statuses_count,
        verified,
        CASE WHEN protected_user = TRUE THEN TRUE ELSE FALSE END AS protected,
        default_profile,
        default_profile_image,
        location,
        description,
        time_zone,
        lang
    FROM raw.twitter_user_history
),

cleaned_data AS (
    SELECT
        id,
        _fivetran_synced,
        -- Apply screen_name validation and cleaning
        CASE
            WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL
            WHEN REGEXP_MATCHES(screen_name, '^[A-Za-z0-9_]{3,15}$') THEN screen_name
            ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '')
        END AS screen_name,
        -- Apply URL validation and cleaning
        CASE
            WHEN url IS NULL THEN NULL
            WHEN REGEXP_MATCHES(url, '^https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?') THEN url
            WHEN REGEXP_MATCHES(url, '^(https?://)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?') THEN 'https://' || REGEXP_REPLACE(url, '^https?://', '')
            ELSE NULL
        END AS url,
        created_at,
        followers_count,
        friends_count AS following_count,
        listed_count,
        favourites_count,
        statuses_count,
        verified,
        protected,
        default_profile,
        default_profile_image,
        location,
        description,
        time_zone,
        lang
    FROM source_data
    WHERE screen_name IS NOT NULL -- Remove invalid entries
    AND NOT REGEXP_MATCHES(screen_name, '[!@#$%^&*()+=<>?}{|,]') -- Remove rows with harmful characters
)

SELECT *
FROM cleaned_data
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|12|12|0|0|是|
|L1|12|12|0|0|是|
|L2|12|12|0|0|是|
|L3|12|12|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 独立单点重跑

### 024_reruns_impl-023_stg_social_media__twitter_user_history.json
[024_reruns_impl-023_stg_social_media__twitter_user_history.json](../024_reruns_impl-023_stg_social_media__twitter_user_history.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|180|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":12,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`

#### baseline
私有SQL：`data/024_work/impl-023_stg_social_media__twitter_user_history/baseline.sql`；SHA-256 `84b7b49c6e5b15f8812c8770f4c02c296f3e6f85985b5a9ac0218856e79acf1a`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|180|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":12,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`

#### screen_regex
不计参与因素；类别候选C。契约可执行regexp_replace未指定g，agent改为全局。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第6行、offset 221起替换；其他字节相同。
原表达式：
```sql
regexp_replace(screen_name, '[^A-Za-z0-9_]', '', 'g')
```

修改后：
```sql
regexp_replace(screen_name, '[^A-Za-z0-9_]', '')
```

私有SQL：`data/024_work/impl-023_stg_social_media__twitter_user_history/screen_regex.sql`；SHA-256 `7a34aa6837289c32e8ce77d47aeeb107d3d46cb3fcbc83859005d62e2b1f381a`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|180|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":12,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`

#### harmful_filter
不计参与因素；类别候选C。契约要求含有害字符行删除；agent先清洗再保留。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第27行、offset 1314起替换；其他字节相同。
原表达式：
```sql
from raw.twitter_user_history
```

修改后：
```sql
from raw.twitter_user_history where NOT REGEXP_MATCHES(screen_name, '[!@#$%^&*()+=<>?}{|,]')
```

私有SQL：`data/024_work/impl-023_stg_social_media__twitter_user_history/harmful_filter.sql`；SHA-256 `a513c1cd3c182716fdf7baa1690b511b2cc36ce65a71797b262d2a16d2751fa9`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|180|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":12,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`

#### empty_filter
不计参与因素；类别候选A。清洗后空串是否删行与规则先后未明确，gold保留。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第33行、offset 1424起替换；其他字节相同。
原表达式：
```sql
  and screen_name <> ''
```

修改后：
```sql

```

私有SQL：`data/024_work/impl-023_stg_social_media__twitter_user_history/empty_filter.sql`；SHA-256 `fbdaf2b1ecb0ea04feaa5cebf597753718491e4e36f8cadbbe35c64552793f53`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|180|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":12,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
### 024_supplement_reruns_impl-023_stg_social_media__twitter_user_history.json
[024_supplement_reruns_impl-023_stg_social_media__twitter_user_history.json](../024_supplement_reruns_impl-023_stg_social_media__twitter_user_history.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|180|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":12,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`

#### baseline
私有SQL：`data/024_supplement_work/impl-023_stg_social_media__twitter_user_history/baseline.sql`；SHA-256 `84b7b49c6e5b15f8812c8770f4c02c296f3e6f85985b5a9ac0218856e79acf1a`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|180|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":12,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`

#### id_projection
不计参与因素；类别候选O。契约id BIGINT，gold保留非数值VARCHAR。
相对本轮基线：行减少1，格减少87。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第3行、offset 42起替换；其他字节相同。
原表达式：
```sql
try_cast(id as bigint) as id
```

修改后：
```sql
id as id
```

私有SQL：`data/024_supplement_work/impl-023_stg_social_media__twitter_user_history/id_projection.sql`；SHA-256 `19d20b04487b95b703641fe66eadb7dc12ee69aa287a603a11b1e98256ee58c9`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|17|12|11|93|否|
|L1|17|12|9|84|否|
|L2|17|12|9|84|否|
|L3|17|12|9|84|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":5,"default_profile":5,"default_profile_image":5,"description":5,"favourites_count":7,"followers_count":7,"following_count":7,"lang":5,"listed_count":6,"location":5,"protected":5,"screen_name":9,"statuses_count":7,"time_zone":5,"url":5,"verified":5}`
- L1：`{"id":5,"default_profile":5,"default_profile_image":5,"description":5,"favourites_count":5,"followers_count":5,"following_count":5,"lang":5,"listed_count":5,"location":5,"protected":5,"screen_name":9,"statuses_count":5,"time_zone":5,"url":5,"verified":5}`
- L2：`{"id":5,"default_profile":5,"default_profile_image":5,"description":5,"favourites_count":5,"followers_count":5,"following_count":5,"lang":5,"listed_count":5,"location":5,"protected":5,"screen_name":9,"statuses_count":5,"time_zone":5,"url":5,"verified":5}`
- L3：`{"id":5,"default_profile":5,"default_profile_image":5,"description":5,"favourites_count":5,"followers_count":5,"following_count":5,"lang":5,"listed_count":5,"location":5,"protected":5,"screen_name":9,"statuses_count":5,"time_zone":5,"url":5,"verified":5}`

#### id_filter
不计参与因素；类别候选O。转换后NULL键按契约删行，gold留存非数值键。
相对本轮基线：行减少-16，格减少-256。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第31行、offset 1373起替换；其他字节相同。
原表达式：
```sql
where id is not null
```

修改后：
```sql
where true
```

私有SQL：`data/024_supplement_work/impl-023_stg_social_media__twitter_user_history/id_filter.sql`；SHA-256 `4ee4b024eb7ef37986b6632ff4a7ec360c5f5b1507be297c53e426c0e3bda979`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|17|12|28|436|否|
|L1|17|12|27|432|否|
|L2|17|12|27|432|否|
|L3|17|12|27|432|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":27,"default_profile":27,"default_profile_image":27,"description":27,"favourites_count":28,"followers_count":28,"following_count":28,"lang":27,"listed_count":27,"location":27,"protected":27,"screen_name":27,"statuses_count":28,"time_zone":27,"url":27,"verified":27}`
- L1：`{"id":27,"default_profile":27,"default_profile_image":27,"description":27,"favourites_count":27,"followers_count":27,"following_count":27,"lang":27,"listed_count":27,"location":27,"protected":27,"screen_name":27,"statuses_count":27,"time_zone":27,"url":27,"verified":27}`
- L2：`{"id":27,"default_profile":27,"default_profile_image":27,"description":27,"favourites_count":27,"followers_count":27,"following_count":27,"lang":27,"listed_count":27,"location":27,"protected":27,"screen_name":27,"statuses_count":27,"time_zone":27,"url":27,"verified":27}`
- L3：`{"id":27,"default_profile":27,"default_profile_image":27,"description":27,"favourites_count":27,"followers_count":27,"following_count":27,"lang":27,"listed_count":27,"location":27,"protected":27,"screen_name":27,"statuses_count":27,"time_zone":27,"url":27,"verified":27}`

#### type_followers_count
不计参与因素；类别候选O。契约BIGINT，gold保留DOUBLE。
相对本轮基线：行减少0，格减少1。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第14行、offset 631起替换；其他字节相同。
原表达式：
```sql
try_cast(followers_count as bigint) as followers_count
```

修改后：
```sql
followers_count as followers_count
```

私有SQL：`data/024_supplement_work/impl-023_stg_social_media__twitter_user_history/type_followers_count.sql`；SHA-256 `99375ae7a6f6a1bb0a64bac6b276e33312cbf75c94cdbee34cfc760494944086`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|179|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":11,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`

#### type_following_count
不计参与因素；类别候选O。契约BIGINT，gold保留DOUBLE。
相对本轮基线：行减少0，格减少1。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第15行、offset 695起替换；其他字节相同。
原表达式：
```sql
try_cast(friends_count as bigint) as following_count
```

修改后：
```sql
friends_count as following_count
```

私有SQL：`data/024_supplement_work/impl-023_stg_social_media__twitter_user_history/type_following_count.sql`；SHA-256 `41f9e8490258f1e54bca78e49d525acc16340b2a5e4b866d4fc00faa194ea6ac`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|179|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":12,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`

#### type_listed_count
不计参与因素；类别候选O。契约BIGINT，gold保留DOUBLE。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第16行、offset 757起替换；其他字节相同。
原表达式：
```sql
try_cast(listed_count as bigint) as listed_count
```

修改后：
```sql
listed_count as listed_count
```

私有SQL：`data/024_supplement_work/impl-023_stg_social_media__twitter_user_history/type_listed_count.sql`；SHA-256 `8704d8f79d2acb74d470a62d889f0151210271b1979909a48235e310b0396e29`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|180|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":12,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`

#### type_favourites_count
不计参与因素；类别候选O。契约BIGINT，gold保留DOUBLE。
相对本轮基线：行减少0，格减少1。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第17行、offset 815起替换；其他字节相同。
原表达式：
```sql
try_cast(favourites_count as bigint) as favourites_count
```

修改后：
```sql
favourites_count as favourites_count
```

私有SQL：`data/024_supplement_work/impl-023_stg_social_media__twitter_user_history/type_favourites_count.sql`；SHA-256 `7f70093b97adb5953c6c9b3630fbbdf0c73a17c12f5a97422382db5badd5fe1f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|179|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":12,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":12,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`

#### type_statuses_count
不计参与因素；类别候选O。契约BIGINT，gold保留DOUBLE。
相对本轮基线：行减少0，格减少1。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第18行、offset 881起替换；其他字节相同。
原表达式：
```sql
try_cast(statuses_count as bigint) as statuses_count
```

修改后：
```sql
statuses_count as statuses_count
```

私有SQL：`data/024_supplement_work/impl-023_stg_social_media__twitter_user_history/type_statuses_count.sql`；SHA-256 `abc08c852eb2d6b90f7c7eb272a3f0ce5ee92ef64b96759be64e4d5c07346a34`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|12|12|179|否|
|L1|1|12|11|176|否|
|L2|1|12|11|176|否|
|L3|1|12|11|176|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":12,"followers_count":12,"following_count":12,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L1：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L2：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
- L3：`{"id":11,"default_profile":11,"default_profile_image":11,"description":11,"favourites_count":11,"followers_count":11,"following_count":11,"lang":11,"listed_count":11,"location":11,"protected":11,"screen_name":11,"statuses_count":11,"time_zone":11,"url":11,"verified":11}`
## 规则问题

BIGINT投影与非空过滤两处互相遮蔽；分别修不会恢复有正确原键的行，直接类型诊断归O。五个计数字段按五处单改。

