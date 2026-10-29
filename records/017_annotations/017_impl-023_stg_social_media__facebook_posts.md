# impl-023 / stg_social_media__facebook_posts

## 1. 错在哪里

两种未指定的Facebook URL路由不同，另有契约BIGINT与gold DOUBLE表示差异，各138格并列。

已核实：固定2025-10-17共同日期，双方138行，URL与page_followers各138格不同。契约URL仅要求https://facebook.com/前缀模式，没有规定/page/posts/id路径；agent与gold构造均符合此前缀，归A。page_followers明定BIGINT，agent遵守，gold输出DOUBLE；raw fan_count无小数，L1格式归一后这138格消失，归O。两项单修L0行数均138、格子276→138，按v1并列。URL单改在L1整表匹配；另改impressions为契约默认0不改变结果，不列参与因素。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-023_staging_stg_social_media__facebook_posts.md)；不修改既有官方判错状态。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml` 第205–255行。
- [完整轨迹](../017_trace_impl-023.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。
- [查询原文及结果](../017_queries_impl-023.json)、[重跑完整记录](../017_reruns_impl-023.json)、[原始表库存](../015_raw_impl-023.json)。
- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。
- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。

### 契约原文

```yaml
    - name: stg_social_media__facebook_posts
      description: "Published, visible Facebook posts joined to page info, standardized fields for analysis; recent 2-year window."
      source_table: 
        - raw.facebook_pages_post_history
        - raw.facebook_pages_page_data
      columns:
        - name: id
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
          description: "From created_time."
        - name: post_id
          data_type: VARCHAR
          description: "CAST(id)."
        - name: post_message
          data_type: VARCHAR
          description: "COALESCE(message, '')."
        - name: page_id
          data_type: VARCHAR
          description: "CAST(page_id)."
        - name: page_name
          data_type: VARCHAR
          validation_rules:
            - rule: "page_name IS NOT NULL AND page_name <> ''"
              on_failure: correct  
          description: "Defaults to 'Unknown Page' when page name is missing."
        - name: page_username
          data_type: VARCHAR
        - name: page_category
          data_type: VARCHAR
        - name: page_followers
          data_type: BIGINT
        - name: shares
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
          description: "Default 0 in staging."
        - name: status_type
          data_type: VARCHAR
        - name: privacy_value
          data_type: VARCHAR
        - name: is_eligible_for_promotion
          data_type: BOOLEAN
        - name: is_instagram_eligible
          data_type: BOOLEAN
        - name: post_url
          data_type: VARCHAR
          validation_rules:
            - rule: "post_url ~ '^https://facebook\\.com/.+'"
              on_failure: correct
```

### SQL定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: with post_metrics as (
   2:     select post_id, max(post_impressions) as impressions
   3:     from raw.facebook_pages_lifetime_post_metrics
   4:     group by post_id
   5: ), pages as (
   6:     select *, row_number() over (partition by id order by _fivetran_synced desc nulls last) as row_num
   7:     from raw.facebook_pages_page_data
   8: )
   9: select
  10:     p.id::varchar as id,
  11:     p.created_time::timestamp as created_timestamp,
  12:     p.id::varchar as post_id,
  13:     coalesce(p.message, '')::varchar as post_message,
  14:     cast(p.page_id as varchar) as page_id,
  15:     coalesce(nullif(pg.name, ''), 'Unknown Page')::varchar as page_name,
  16:     pg.username::varchar as page_username,
  17:     pg.category::varchar as page_category,
  18:     coalesce(try_cast(pg.fan_count as bigint), 0)::bigint as page_followers,
  19:     coalesce(p.share_count, 0)::bigint as shares,
  20:     coalesce(pm.impressions, 0)::bigint as impressions,
  21:     p.status_type::varchar as status_type,
  22:     p.privacy_value::varchar as privacy_value,
  23:     p.is_eligible_for_promotion::boolean as is_eligible_for_promotion,
  24:     p.is_instagram_eligible::boolean as is_instagram_eligible,
  25:     ('https://facebook.com/' || p.id)::varchar as post_url
  26: from raw.facebook_pages_post_history p
  27: left join pages pg on p.page_id = pg.id and pg.row_num = 1
  28: left join post_metrics pm on pm.post_id = p.id
  29: where coalesce(p.is_published, false)
  30:   and not coalesce(p.is_hidden, false)
  31:   and p.created_time >= current_date - interval '2 years'
  32:   and p.created_time is not null
```

gold（仅用于定位差异）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: -- Facebook posts staging table - Simplified version based on actual columns
   2: -- Created based on real table structure analysis
   3:
   4: WITH source_posts AS (
   5:     SELECT
   6:         id,
   7:         created_time,
   8:         page_id,
   9:         status_type,
  10:         message,
  11:         share_count,
  12:         is_published,
  13:         privacy_value,
  14:         is_hidden,
  15:         is_eligible_for_promotion,
  16:         is_instagram_eligible
  17:     FROM raw.facebook_pages_post_history
  18:     WHERE is_published = TRUE -- Only published posts
  19:     AND is_hidden = FALSE -- Not hidden
  20:     AND created_time >= CURRENT_DATE - INTERVAL '2 years' -- Recent posts only
  21: ),
  22:
  23: -- Get page information
  24: page_info AS (
  25:     SELECT
  26:         id AS page_id,
  27:         name AS page_name,
  28:         username,
  29:         website,
  30:         category,
  31:         fan_count,
  32:         talking_about_count,
  33:         created_time AS page_created_time
  34:     FROM raw.facebook_pages_page_data
  35:     WHERE (_fivetran_deleted = FALSE OR _fivetran_deleted IS NULL)
  36:         AND name IS NOT NULL -- Ensure page has a name
  37: )
  38:
  39: -- Simplified join just to get basic page info
  40: SELECT
  41:     sp.id,
  42:     sp.created_time AS created_timestamp,
  43:     CAST(sp.id AS VARCHAR) AS post_id,
  44:     COALESCE(sp.message, '') AS post_message,
  45:     CAST(sp.page_id AS VARCHAR) AS page_id,
  46:     COALESCE(pi.page_name, 'Unknown Page') AS page_name,
  47:     pi.username AS page_username,
  48:     pi.category AS page_category,
  49:     COALESCE(pi.fan_count, 0) AS page_followers,
  50:     COALESCE(sp.share_count, 0) AS shares,
  51:     0 AS impressions,
  52:     sp.status_type,
  53:     sp.privacy_value,
  54:     sp.is_eligible_for_promotion,
  55:     sp.is_instagram_eligible,
  56:     CONCAT('https://facebook.com/', COALESCE(pi.page_id, sp.page_id), '/posts/', sp.id) AS post_url
  57: FROM source_posts sp
  58: LEFT JOIN page_info pi ON sp.page_id = pi.page_id
```

### 原始数据可评估性

下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。

|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|
|---|---|---|---|---|---|
|raw.facebook_pages_lifetime_post_metrics|gold_vs_initial|True|True|True||
|raw.facebook_pages_page_data|gold_vs_initial|True|True|True||
|raw.facebook_pages_post_history|gold_vs_initial|True|True|True||
|raw.facebook_pages_lifetime_post_metrics|gold_vs_agent|True|True|True||
|raw.facebook_pages_page_data|gold_vs_agent|True|True|True||
|raw.facebook_pages_post_history|gold_vs_agent|True|True|True||

## 3. agent看过什么

event13→14、15→16读契约；event23→24查全部raw schema及样例（未截断），包括page id/fan_count；event29生成URL简写和BIGINT转换。event55最终报告讨论时间窗造成空表，但没有讨论本次日期控制后的URL路由或page_followers类型差异。

只把归档实际展示的内容视为已看到；磁盘有文件、命令包含表名或截断掉的部分，不等于看到相应数据值。

### 新增字段：是否意识到或提到相关不确定性

**看到了但没提**。只记录可见表述/信息，不由该档位推定错误类别。

event55说明时间窗造成空表以及其他平台字段缺口，但当前选表差异已按共同日期控制，剩余URL路由/粉丝数类型未被单独讨论。

event **24**，字段`content`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/24.json`。
```text
facebook_pages_page_data
[('id', 'BIGINT', 'YES', None, None, None), ('_fivetran_deleted', 'BOOLEAN', 'YES', None, None, None), ('_fivetran_synced', 'TIMESTAMP', 'YES', None, None, None), ('affiliation', 'VARCHAR', 'YES', None, None, None), ('app_id', 'VARCHAR', 'YES', None, None, None), ('artists_we_like', 'VARCHAR', 'YES', None, None, None), ('attire', 'VARCHAR', 'YES', None, None, None), ('awards', 'VARCHAR', 'YES', None, None, None), ('band_interests', 'VARCHAR', 'YES', None, None, None), ('band_members', 'VARCHAR', 'YES', None, None, None), ('bio', 'VARCHAR', 'YES', None, None, None), ('birthday', 'VARCHAR', 'YES', None, None, None), ('booking_agent', 'VARCHAR', 'YES', None, None, None), ('built', 'VARCHAR', 'YES', None, None, None), ('can_checkin', 'BOOLEAN', 'YES', None, None, None), ('can_post', 'BOOLEAN', 'YES', None, None, None), ('category', 'VARCHAR', 'YES', None, None, None), ('category_list', 'VARCHAR', 'YES', None, None, None), ('checkins', 'DOUBLE', 'YES', None, None, None), ('company_overview', 'VARCHAR', 'YES', None, None, None), ('culinary_team', 'VARCHAR', 'YES', None, None, None), ('current_location', 'VARCHAR', 'YES', None, None, None), ('description', 'VARCHAR', 'YES', None, None, None), ('directed_by', 'VARCHAR', 'YES', None, None, None), ('display_subtext', 'VARCHAR', 'YES', None, None, None), ('emails', 'VARCHAR', 'YES', None, None, None), ('fan_count', 'DOUBLE', 'YES', None, None, None), ('features', 'VARCHAR', 'YES', None, None, None), ('food_styles', 'VARCHAR', 'YES', None, None, None), ('founded', 'VARCHAR', 'YES', None, None, None), ('general_info', 'VARCHAR', 'YES', None, None, None), ('general_manager', 'VARCHAR', 'YES', None, None, None), ('genre', 'VARCHAR', 'YES', None, None, None), ('global_brand_page_name', 'VARCHAR', 'YES', None, None, None), ('has_added_app', 'VARCHAR', 'YES', None, None, None), ('has_whatsapp_number', 'VARCHAR'
```

归档逐项扫描57个事件；本批thought/args.thought字段均为空，不能由此推断agent没有内部思考。“已提到”的原句来自final_thought中的最终报告；“看到了但没提”依据可见工具返回，不把SQL代码本身当口头说明。长工具输出仅摘录连续原文，截取范围见JSON；不是说agent只看到了这个摘录。

## 4. 查询与重跑

核实查询执行 **1条**（失败尝试也计入）；核实代价档：**需要查业务说明**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。

### V1 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。
```sql
SELECT count(*) n,count(*) FILTER(WHERE fan_count IS DISTINCT FROM try_cast(fan_count AS BIGINT)) fractional_fan_count,count(*) FILTER(WHERE _fivetran_deleted) deleted FROM raw.facebook_pages_page_data
```
结果原文：
```json
{
  "executed_utc": "2026-10-29T11:33:05.695019+00:00",
  "columns": [
    "n",
    "fractional_fan_count",
    "deleted"
  ],
  "rows": [
    [
      2500,
      0,
      0
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['id']`；原评分比较列：`['created_timestamp', 'id', 'impressions', 'is_eligible_for_promotion', 'is_instagram_eligible', 'page_category', 'page_followers', 'page_id', 'page_name', 'page_username', 'post_id', 'post_message', 'post_url', 'privacy_value', 'shares', 'status_type']`。与键取并集，不自行纳入原评分排除列。

全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。

共同时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-17 12:00:00+08'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-17'", "count": 1}]`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|url_route|138→138|276→138|L1|
|followers_representation|138→138|276→138|无|
|impressions_default|138→138|276→276|无|

### 原留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|138|138|0|0|0/0|138|138|276|False|
|L1|138|138|0|0|0/0|138|138|138|False|
|L2|138|138|0|0|0/0|138|138|138|False|
|L3|138|138|0|0|0/0|138|138|138|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|id|0|0|0|0|
|created_timestamp|0|0|0|0|
|impressions|0|0|0|0|
|is_eligible_for_promotion|0|0|0|0|
|is_instagram_eligible|0|0|0|0|
|page_category|0|0|0|0|
|page_followers|138|0|0|0|
|page_id|0|0|0|0|
|page_name|0|0|0|0|
|page_username|0|0|0|0|
|post_id|0|0|0|0|
|post_message|0|0|0|0|
|post_url|138|138|138|138|
|privacy_value|0|0|0|0|
|shares|0|0|0|0|
|status_type|0|0|0|0|

### 重跑 baseline

SQL：`data/017_work/impl-023/baseline.sql`；SHA-256：`ddaed6784fa59540693045b698dc39121102ebdf42b9ecc168ad4cd971fb272a`。

同输入、同时间控制、不增加因果改动的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|138|138|0|0|0/0|138|138|276|False|
|L1|138|138|0|0|0/0|138|138|138|False|
|L2|138|138|0|0|0/0|138|138|138|False|
|L3|138|138|0|0|0/0|138|138|138|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|id|0|0|0|0|
|created_timestamp|0|0|0|0|
|impressions|0|0|0|0|
|is_eligible_for_promotion|0|0|0|0|
|is_instagram_eligible|0|0|0|0|
|page_category|0|0|0|0|
|page_followers|138|0|0|0|
|page_id|0|0|0|0|
|page_name|0|0|0|0|
|page_username|0|0|0|0|
|post_id|0|0|0|0|
|post_message|0|0|0|0|
|post_url|138|138|138|138|
|privacy_value|0|0|0|0|
|shares|0|0|0|0|
|status_type|0|0|0|0|

### 重跑 url_route

SQL：`data/017_work/impl-023/url_route.sql`；SHA-256：`e29eb583fb1ec2702239798a60fae4fec3cc9fa1871808edc171ac380c6e521a`。

唯一替换位置offset=1089；原文：
```sql
('https://facebook.com/' || p.id)
```
新文：
```sql
('https://facebook.com/' || coalesce(pg.id,p.page_id) || '/posts/' || p.id)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|138|138|0|0|0/0|138|138|138|False|
|L1|138|138|0|0|0/0|0|0|0|True|
|L2|138|138|0|0|0/0|0|0|0|True|
|L3|138|138|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L1**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|id|0|0|0|0|
|created_timestamp|0|0|0|0|
|impressions|0|0|0|0|
|is_eligible_for_promotion|0|0|0|0|
|is_instagram_eligible|0|0|0|0|
|page_category|0|0|0|0|
|page_followers|138|0|0|0|
|page_id|0|0|0|0|
|page_name|0|0|0|0|
|page_username|0|0|0|0|
|post_id|0|0|0|0|
|post_message|0|0|0|0|
|post_url|0|0|0|0|
|privacy_value|0|0|0|0|
|shares|0|0|0|0|
|status_type|0|0|0|0|

### 重跑 followers_representation

SQL：`data/017_work/impl-023/followers_representation.sql`；SHA-256：`05e6e5ee3e49059a80f51fc525494b6ff61ff832521cf280134c355b729141bc`。

唯一替换位置offset=682；原文：
```sql
coalesce(try_cast(pg.fan_count as bigint), 0)::bigint
```
新文：
```sql
coalesce(pg.fan_count, 0)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|138|138|0|0|0/0|138|138|138|False|
|L1|138|138|0|0|0/0|138|138|138|False|
|L2|138|138|0|0|0/0|138|138|138|False|
|L3|138|138|0|0|0/0|138|138|138|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|id|0|0|0|0|
|created_timestamp|0|0|0|0|
|impressions|0|0|0|0|
|is_eligible_for_promotion|0|0|0|0|
|is_instagram_eligible|0|0|0|0|
|page_category|0|0|0|0|
|page_followers|0|0|0|0|
|page_id|0|0|0|0|
|page_name|0|0|0|0|
|page_username|0|0|0|0|
|post_id|0|0|0|0|
|post_message|0|0|0|0|
|post_url|138|138|138|138|
|privacy_value|0|0|0|0|
|shares|0|0|0|0|
|status_type|0|0|0|0|

### 重跑 impressions_default

SQL：`data/017_work/impl-023/impressions_default.sql`；SHA-256：`142158fdf64319f6abd26a1dea9c8d1b43847ee36bbcb8c819c6ccbf6e8b2f9b`。

唯一替换位置offset=809；原文：
```sql
coalesce(pm.impressions, 0)::bigint as impressions
```
新文：
```sql
0::bigint as impressions
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|138|138|0|0|0/0|138|138|276|False|
|L1|138|138|0|0|0/0|138|138|138|False|
|L2|138|138|0|0|0/0|138|138|138|False|
|L3|138|138|0|0|0/0|138|138|138|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|id|0|0|0|0|
|created_timestamp|0|0|0|0|
|impressions|0|0|0|0|
|is_eligible_for_promotion|0|0|0|0|
|is_instagram_eligible|0|0|0|0|
|page_category|0|0|0|0|
|page_followers|138|0|0|0|
|page_id|0|0|0|0|
|page_name|0|0|0|0|
|page_username|0|0|0|0|
|post_id|0|0|0|0|
|post_message|0|0|0|0|
|post_url|138|138|138|138|
|privacy_value|0|0|0|0|
|shares|0|0|0|0|
|status_type|0|0|0|0|

## 5. 类别、把握和对比

- 主要原因：**多因并列（A、O）**（归因判断）。
- 主因单项：url_route, followers_representation。
- 参与因素：无；impressions默认值控制无改善。
- 标记：无。
- 把握：**高**。
- 重跑是否满足U第4条件：是：各减少138/276格；url_route首次整表匹配L1，非U。

URL路径选择无法由raw列数值决定；整数粉丝数转换遵守类型要求。不存在满足U条件的错误数据假设。

与014相比是否变化：不适用（第三批首次标注）；也未修改016任何结论。

## 规则问题

主因比较沿016使用L0规模，故A与表示层O并列；若先在L1归一后再挑主因会只剩A，手册未指明主因层级，本次公开L0–L3而不暗换尺度。时间窗已共同固定，不把原运行时空表再算作本表剩余错误。

2026-10-29用户确认补充：本表依赖原始表若agent留存与初始一致而gold不同，先诊断再标不可评估；若gold与初始一致而agent不同，则正常标注并追踪agent运行中的改动。不能把两种情况混淆。raw差异须限定到本表依赖；CS上游用gold。

新增字段统一口径：记录与实际差异机制相关的明确选择/可疑数据表述；不要求agent预知gold，也不把泛称“完成清洗”算作识别具体边界。021关于重复计数、029关于可选字段失败置NULL为适用范围较广的声明，单独注明并未点名本表异常；可见证据只能支持这一有限范围。该字段不增减U/C/D/I/A/O/X条件。
