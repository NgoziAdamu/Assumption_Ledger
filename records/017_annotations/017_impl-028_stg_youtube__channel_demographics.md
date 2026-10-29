# impl-028 / stg_youtube__channel_demographics

## 1. 错在哪里

agent/初始只有youtube_channel_demographics_data的2509行，gold另用channel_demographics_a_1的9450行，原始内容不相交。

已核实：015三方库存显示agent与初始同名raw一致，二者没有契约/gold引用的channel_demographics_a_1；gold反而没有agent那张youtube_channel_demographics_data。017诊断按相同7个业务列对齐比较，agent/初始多重集合一致，agent2509行与gold9450行完全不相交。输出基线行规模11959、格子83713。符合2026-10-29用户补充第一种情况，标不可评估；不把输入缺失判C/U，也不用改百分比或年龄映射来掩盖输入差异。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-028_staging_stg_youtube__channel_demographics.md)；不修改既有官方判错状态。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/docs/data_contract.yaml` 第155–205行。
- [完整轨迹](../017_trace_impl-028.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。
- [查询原文及结果](../017_queries_impl-028.json)、[重跑完整记录](../017_reruns_impl-028.json)、[原始表库存](../015_raw_impl-028.json)。
- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。
- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。

### 契约原文

```yaml
    - name: stg_youtube__channel_demographics
      description: "Cleaned per-video demographics (age, gender, geography). Percentages normalized to [0,1]; identifiers validated; categories enforced."
      source_table: raw.channel_demographics_a_1
      columns:
        - name: date_day
          data_type: DATE
          validation_rules:
            - rule: "date_day IS NOT NULL"
              on_failure: delete_row
        - name: channel_id
          data_type: VARCHAR
          validation_rules:
            - rule: "channel_id IS NULL OR (LENGTH(TRIM(channel_id)) BETWEEN 12 AND 40)"
              on_failure: nullify_field
            - rule: "channel_id = TRIM(channel_id)"
              on_failure: correct
        - name: video_id
          data_type: VARCHAR
          validation_rules:
            - rule: "video_id IS NULL OR (LENGTH(TRIM(video_id)) BETWEEN 8 AND 20)"
              on_failure: nullify_field
            - rule: "video_id = TRIM(video_id)"
              on_failure: correct
        - name: country_code
          data_type: VARCHAR
          validation_rules:
            - rule: "country_code IS NULL OR country_code = UPPER(TRIM(country_code))"
              on_failure: correct
        - name: age_group
          data_type: VARCHAR
          validation_rules:
            - rule: "age_group IN ('13-17','18-24','25-34','35-44','45-54','55-64','65-')"
              on_failure: nullify_field
        - name: gender
          data_type: VARCHAR
          validation_rules:
            - rule: "gender IN ('female','male','user_specified')"
              on_failure: nullify_field
        - name: views_percentage
          data_type: DECIMAL(5,4)
          validation_rules:
            - rule: "views_percentage BETWEEN 0 AND 1"
              on_failure: nullify_field
        - name: _fivetran_synced
          data_type: TIMESTAMP
          validation_rules:
            - rule: "_fivetran_synced IS NULL OR _fivetran_synced <= CURRENT_TIMESTAMP"
              on_failure: nullify_field
        - name: source_relation
          data_type: VARCHAR
```

### SQL定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/sql/staging/stg_youtube__channel_demographics.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: with source_rows as (
   2:     select
   3:         try_cast("date" as date) as date_day,
   4:         channel_id,
   5:         video_id,
   6:         country_code,
   7:         case
   8:             when age_group = 'AGE_13_17' then '13-17'
   9:             when age_group = 'AGE_18_24' then '18-24'
  10:             when age_group = 'AGE_25_34' then '25-34'
  11:             when age_group = 'AGE_35_44' then '35-44'
  12:             when age_group = 'AGE_45_54' then '45-54'
  13:             when age_group = 'AGE_55_64' then '55-64'
  14:             when age_group = 'AGE_65_' then '65-'
  15:             else age_group
  16:         end as age_group,
  17:         lower(gender) as gender,
  18:         try_cast(views_percentage as decimal(5, 4)) as views_percentage,
  19:         try_cast(replace("_fivetran_synced", ' UTC', '') as timestamp) as _fivetran_synced,
  20:         'youtube_channel_demographics_data' as source_relation
  21:     from raw.youtube_channel_demographics_data
  22: ),
  23: validated_rows as (
  24:     select
  25:         date_day,
  26:         case when channel_id is null or length(trim(channel_id)) between 12 and 40 then trim(channel_id) else null end as channel_id,
  27:         case when video_id is null or length(trim(video_id)) between 8 and 20 then trim(video_id) else null end as video_id,
  28:         case when country_code is null then null else upper(trim(country_code)) end as country_code,
  29:         case when age_group in ('13-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65-') then age_group else null end as age_group,
  30:         case when gender in ('female', 'male', 'user_specified') then gender else null end as gender,
  31:         case when views_percentage between 0 and 1 then views_percentage else null end as views_percentage,
  32:         case when _fivetran_synced is null or _fivetran_synced <= current_timestamp then _fivetran_synced else null end as _fivetran_synced,
  33:         source_relation
  34:     from source_rows
  35:     where date_day is not null
  36: )
  37: select *
  38: from validated_rows
```

gold（仅用于定位差异）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/sql/staging/stg_youtube__channel_demographics.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: -- Staging: YouTube channel demographics metrics
   2: -- Source: raw.youtube_channel_demographics_data (information_schema verified)
   3: -- Purpose: Normalize percentages, validate categories and identifiers
   4:
   5: with source_data as (
   6:     select * from raw.channel_demographics_a_1
   7: ),
   8:
   9: renamed as (
  10:     select
  11:         date as date_day,
  12:         channel_id,
  13:         video_id,
  14:         upper(trim(country_code)) as country_code,
  15:         age_group,
  16:         gender,
  17:         views_percentage / 100.0 as views_percentage,
  18:         _fivetran_synced,
  19:         'youtube_source' as source_relation
  20:     from source_data
  21: ),
  22:
  23: validated as (
  24:     select
  25:         date_day,
  26:         case when channel_id IS NOT NULL AND length(trim(channel_id)) between 12 and 40 then trim(channel_id) else NULL end as channel_id,
  27:         case when video_id IS NULL OR length(trim(video_id)) between 8 and 20 then trim(video_id) else NULL end as video_id,
  28:         country_code,
  29:         case when age_group in ('13-17','18-24','25-34','35-44','45-54','55-64','65-') then age_group else NULL end as age_group,
  30:         case when gender in ('female','male','user_specified') then gender else NULL end as gender,
  31:         case when views_percentage >= 0 and views_percentage <= 1 then views_percentage else NULL end as views_percentage,
  32:         case when _fivetran_synced <= current_timestamp then _fivetran_synced else NULL end as _fivetran_synced,
  33:         source_relation
  34:     from renamed
  35:     where date_day is not null
  36: )
  37:
  38: select * from validated
```

### 原始数据可评估性

下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。

|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|
|---|---|---|---|---|---|
|raw.channel_demographics_a_1|gold_vs_initial|None|None|None|initial_missing_table|
|raw.youtube_channel_demographics_data|gold_vs_initial|None|None|None|gold_missing_table|
|raw.channel_demographics_a_1|gold_vs_agent|None|None|None|agent_missing_table|
|raw.youtube_channel_demographics_data|gold_vs_agent|None|None|None|gold_missing_table|

[028输入诊断SQL及结果](../017_ineligible_diagnostic_impl-028.json)：同名表存在性、日期范围、完整表哈希复核、语义列多重集合对比。

## 3. agent看过什么

event21→22列出实际raw表，仅有youtube_channel_*_data等；event23→24看schema与样例；event25选择可用的demographics表；event33修run.py raw-schema导入；event37→38和45→46查看结果行数。event57最终报告讨论channel_basic/video缺失字段，但未明确解释本表替代源名或与gold输入差异。

只把归档实际展示的内容视为已看到；磁盘有文件、命令包含表名或截断掉的部分，不等于看到相应数据值。

### 新增字段：是否意识到或提到相关不确定性

**看到了但没提**。只记录可见表述/信息，不由该档位推定错误类别。

event57说明channel_basic/video缺失字段、空video_id与run.py导入修复；没有明确讨论demographics原始表名替换或其输入与gold的差异。

event **22**，字段`content`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/22.json`。
```text
youtube_channel_demographics_data', 'BASE TABLE', None, None, None, None, None, 'YES', 'NO', None, None), ('youtube_analytics_start', 'raw', 'youtube_video_data', 'BASE TABLE', None, None, None, None, None, 'YES', 'NO', None, None)]
[('youtube_analytics_start', 20645, '/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics_start.duckdb', None, {'storage_version': 'v1.0.0+'}, False, 'duckdb', True, False, None, {}), ('system', 0, None, None, {}, True, 'duckdb', False, False, None, {}), ('temp', 22065, None, None, {}, True, 'duckdb', False, False, None, {})]
sql:
total 20
drwxr-xr-x 5 katherine katherine 4096 Oct 17 17:41 .
drwxr-xr-x 8 katherine katherine 4096 Oct 25 05:53 ..
drwxr-xr-x 2 katherine katherine 4096 Oct 17 17:41 intermediate
drwxr-xr-x 2 katherine katherine 4096 Oct 17 17:41 marts
drwxr-xr-x 2 katherine katherine 4096 Oct 17 17:41 staging

sql/intermediate:
total 8
drwxr-xr-x 2 katherine katherine 4096 Oct 17 17:41 .
drwxr-xr-x 5 katherine katherine 4096 Oct 17 17:41 ..

sql/marts:
total 8
drwxr-xr-x 2 katherine katherine 4096 Oct 17 17:41 .
drwxr-xr-x 5 katherine katherine 4096 Oct 17 17:41 ..

sql/staging:
total 8
drwxr-xr-x 2 katherine katherine 4096 Oct 17 17:41 .
drwxr-xr-x 5 katherine katherine 4096 Oct 17 17:41 ..

```

event **24**，字段`content`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/24.json`。
```text
youtube_channel_demographics_data [('_fivetran_id', 'VARCHAR', 'YES', None, None, None), ('date', 'VARCHAR', 'YES', None, None, None), ('_fivetran_synced', 'VARCHAR', 'YES', None, None, None), ('age_group', 'VARCHAR', 'YES', None, None, None), ('channel_id', 'VARCHAR', 'YES', None, None, None), ('country_code', 'VARCHAR', 'YES', None, None, None), ('gender', 'VARCHAR', 'YES', None, None, None), ('live_or_on_demand', 'VARCHAR', 'YES', None, None, None), ('subscribed_status', 'VARCHAR', 'YES', None, None, None), ('video_id', 'VARCHAR', 'YES', None, None, None), ('views_percentage', 'DOUBLE', 'YES', None, None, None)]
[('8LCQJJcoMWAXaK00n2XIdmDWFc8=', '2021-08-13', '2021-08-15 14:26:38.244 UTC', 'AGE_65_', 'ZZZZZZ', 'GB', 'MALE', 'on_demand', 'not_subscribed', 'THK0DyoSVTs', 0.9009009009)]

 youtube_video_data [('id', 'VARCHAR', 'YES', None, None, None), ('_fivetran_synced', 'VARCHAR', 'YES', None, None, None), ('content_details_caption', 'BOOLEAN', 'YES', None, None, None), ('content_details_definition', 'VARCHAR', 'YES', None, None, None), ('content_details_dimension', 'VARCHAR', 'YES', None, None, None), ('content_details_duration', 'VARCHAR', 'YES', None, None, None), ('content_details_has_custom_thumbnail', 'BOOLEAN', 'YES', None, None, None), ('content_details_licensed_content', 'BOOLEAN', 'YES', None, None, None), ('content_details_projection', 'VARCHAR', 'YES', None, None, None), ('content_details_region_restriction', 'DOUBLE', 'YES', None, None, None), ('etag', 'VARCHAR', 'YES', None, None, None), ('kind', 'VARCHAR', 'YES', None, None, None), ('player_embed_height', 'DOUBLE', 'YES', None, None, None), ('player_embed_html', 'VARCHAR', 'YES', None, None, None), ('player_embed_width', 'DOUBLE', 'YES', None, None, None), ('privacy_status', 'VARCHAR', 'YES', None, None, None), ('snippet_category_id', 'BIGINT', 'YES', None, None, None), ('snippet_channel_id', 'VARCHAR
```

归档逐项扫描59个事件；本批thought/args.thought字段均为空，不能由此推断agent没有内部思考。“已提到”的原句来自final_thought中的最终报告；“看到了但没提”依据可见工具返回，不把SQL代码本身当口头说明。长工具输出仅摘录连续原文，截取范围见JSON；不是说agent只看到了这个摘录。

## 4. 查询与重跑

核实查询执行 **0条**（失败尝试也计入）；核实代价档：**判断不了**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。

本表无核实P的查询；不可评估诊断见下面。核实代价“判断不了”指无法在同输入条件下估计正常核实代价，并非未查到输入差异。

### 不同输入诊断

```json
[
  {
    "side": "initial",
    "kind": "诊断查询",
    "database": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/youtube_analytics_start.duckdb",
    "sql": "SELECT table_name FROM information_schema.tables WHERE table_schema='raw' ORDER BY 1",
    "columns": [
      "table_name"
    ],
    "rows": [
      [
        "youtube_channel_basic_data"
      ],
      [
        "youtube_channel_demographics_data"
      ],
      [
        "youtube_video_data"
      ]
    ]
  },
  {
    "side": "initial",
    "kind": "诊断查询",
    "database": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/youtube_analytics_start.duckdb",
    "sql": "SELECT count(*) n,min(cast(date AS VARCHAR)) first_day,max(cast(date AS VARCHAR)) last_day,count(distinct video_id) videos FROM raw.youtube_channel_demographics_data",
    "columns": [
      "n",
      "first_day",
      "last_day",
      "videos"
    ],
    "rows": [
      [
        2509,
        "2021-08-13",
        "2025-10-16",
        1576
      ]
    ]
  },
  {
    "side": "initial",
    "kind": "诊断查询",
    "database": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/youtube_analytics_start.duckdb",
    "sql": "SELECT date,channel_id,video_id,country_code,age_group,gender,views_percentage FROM raw.youtube_channel_demographics_data",
    "rows": 2509,
    "result_storage": "comparison counts only, not full original rows"
  },
  {
    "side": "agent",
    "kind": "诊断查询",
    "database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb",
    "sql": "SELECT table_name FROM information_schema.tables WHERE table_schema='raw' ORDER BY 1",
    "columns": [
      "table_name"
    ],
    "rows": [
      [
        "youtube_channel_basic_data"
      ],
      [
        "youtube_channel_demographics_data"
      ],
      [
        "youtube_video_data"
      ]
    ]
  },
  {
    "side": "agent",
    "kind": "诊断查询",
    "database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb",
    "sql": "SELECT count(*) n,min(cast(date AS VARCHAR)) first_day,max(cast(date AS VARCHAR)) last_day,count(distinct video_id) videos FROM raw.youtube_channel_demographics_data",
    "columns": [
      "n",
      "first_day",
      "last_day",
      "videos"
    ],
    "rows": [
      [
        2509,
        "2021-08-13",
        "2025-10-16",
        1576
      ]
    ]
  },
  {
    "side": "agent",
    "kind": "诊断查询",
    "database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb",
    "sql": "SELECT date,channel_id,video_id,country_code,age_group,gender,views_percentage FROM raw.youtube_channel_demographics_data",
    "rows": 2509,
    "result_storage": "comparison counts only, not full original rows"
  },
  {
    "side": "gold",
    "kind": "诊断查询",
    "database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb",
    "sql": "SELECT table_name FROM information_schema.tables WHERE table_schema='raw' ORDER BY 1",
    "columns": [
      "table_name"
    ],
    "rows": [
      [
        "channel_basic_a_2"
      ],
      [
        "channel_demographics_a_1"
      ],
      [
        "video"
      ]
    ]
  },
  {
    "side": "gold",
    "kind": "诊断查询",
    "database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb",
    "sql": "SELECT count(*) n,min(cast(date AS VARCHAR)) first_day,max(cast(date AS VARCHAR)) last_day,count(distinct video_id) videos FROM raw.channel_demographics_a_1",
    "columns": [
      "n",
      "first_day",
      "last_day",
      "videos"
    ],
    "rows": [
      [
        9450,
        "2024-01-01",
        "2024-01-30",
        5
      ]
    ]
  },
  {
    "side": "gold",
    "kind": "诊断查询",
    "database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb",
    "sql": "SELECT date,channel_id,video_id,country_code,age_group,gender,views_percentage FROM raw.channel_demographics_a_1",
    "rows": 9450,
    "result_storage": "comparison counts only, not full original rows"
  },
  {
    "initial_agent_same_selected_row_multiset": true,
    "agent_only_vs_gold_rows": 2509,
    "gold_only_vs_agent_rows": 9450,
    "note": "same semantic column names; exact Python scalar text, no invented source-name equivalence"
  },
  {
    "kind": "complete_table_diagnostic",
    "serialization": "Python repr of (type name,value) tuples, SQL ORDER BY ALL NULLS FIRST, newline separator",
    "sides": {
      "initial": {
        "database": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/youtube_analytics_start.duckdb",
        "sql": "SELECT * FROM raw.youtube_channel_demographics_data ORDER BY ALL NULLS FIRST",
        "columns": [
          [
            "_fivetran_id",
            "VARCHAR"
          ],
          [
            "date",
            "VARCHAR"
          ],
          [
            "_fivetran_synced",
            "VARCHAR"
          ],
          [
            "age_group",
            "VARCHAR"
          ],
          [
            "channel_id",
            "VARCHAR"
          ],
          [
            "country_code",
            "VARCHAR"
          ],
          [
            "gender",
            "VARCHAR"
          ],
          [
            "live_or_on_demand",
            "VARCHAR"
          ],
          [
            "subscribed_status",
            "VARCHAR"
          ],
          [
            "video_id",
            "VARCHAR"
          ],
          [
            "views_percentage",
            "DOUBLE"
          ]
        ],
        "row_count": 2509,
        "sha256": "27c5910aefd3898698ef307a1bfdc9b8b2c89de2d10adf0cd1ba0a7b27d141c5"
      },
      "agent": {
        "database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb",
        "sql": "SELECT * FROM raw.youtube_channel_demographics_data ORDER BY ALL NULLS FIRST",
        "columns": [
          [
            "_fivetran_id",
            "VARCHAR"
          ],
          [
            "date",
            "VARCHAR"
          ],
          [
            "_fivetran_synced",
            "VARCHAR"
          ],
          [
            "age_group",
            "VARCHAR"
          ],
          [
            "channel_id",
            "VARCHAR"
          ],
          [
            "country_code",
            "VARCHAR"
          ],
          [
            "gender",
            "VARCHAR"
          ],
          [
            "live_or_on_demand",
            "VARCHAR"
          ],
          [
            "subscribed_status",
            "VARCHAR"
          ],
          [
            "video_id",
            "VARCHAR"
          ],
          [
            "views_percentage",
            "DOUBLE"
          ]
        ],
        "row_count": 2509,
        "sha256": "27c5910aefd3898698ef307a1bfdc9b8b2c89de2d10adf0cd1ba0a7b27d141c5"
      }
    },
    "initial_agent_columns_equal": true,
    "initial_agent_row_counts_equal": true,
    "complete_typed_row_multiset_equal": true
  }
]
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['date_day', 'channel_id', 'video_id', 'country_code']`；原评分比较列：`['age_group', 'channel_id', 'country_code', 'date_day', 'gender', 'video_id', 'views_percentage']`。与键取并集，不自行纳入原评分排除列。

全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。

共同时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2024-01-30 12:00:00+08'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2024-01-30'", "count": 0}]`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|

### 原留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2509|9450|2509|9450|0/0|0|11959|83713|False|
|L1|2509|9450|2509|9450|0/0|0|11959|83713|False|
|L2|2509|9450|2509|9450|0/0|0|11959|83713|False|
|L3|2509|9450|2509|9450|0/0|0|11959|83713|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|channel_id|0|0|0|0|
|video_id|0|0|0|0|
|country_code|0|0|0|0|
|age_group|0|0|0|0|
|gender|0|0|0|0|
|views_percentage|0|0|0|0|

### 重跑 baseline

SQL：`data/017_work/impl-028/baseline.sql`；SHA-256：`9adf94252f2a2fdaba41efb6219ba534873cf97e561f254b265835295e13bf7c`。

同输入、同时间控制、不增加因果改动的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2509|9450|2509|9450|0/0|0|11959|83713|False|
|L1|2509|9450|2509|9450|0/0|0|11959|83713|False|
|L2|2509|9450|2509|9450|0/0|0|11959|83713|False|
|L3|2509|9450|2509|9450|0/0|0|11959|83713|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|channel_id|0|0|0|0|
|video_id|0|0|0|0|
|country_code|0|0|0|0|
|age_group|0|0|0|0|
|gender|0|0|0|0|
|views_percentage|0|0|0|0|

## 5. 类别、把握和对比

- 主要原因：**不可评估**（归因判断）。
- 主因单项：不适用。
- 参与因素：不适用。
- 标记：无。
- 把握：**高**。
- 重跑是否满足U第4条件：不适用：不同原始输入，只有基线诊断，不做U干预判定。

不能用gold的9450行和百分比尺度反证agent所见2509行的P；二者数据源不可比，归因在可评估性步骤停止。

与014相比是否变化：不适用（第三批首次标注）；也未修改016任何结论。

## 规则问题

2026-10-29用户确认：agent=初始≠gold，诊断后不可评估；gold=初始≠agent则照常标注。此表属于前者。契约表在agent/初始缺失而gold存在也属于来源不一致，不只检查双方同名表。新增不确定性字段仍照常记录轨迹事实，不让“不可评估”替代该字段。

2026-10-29用户确认补充：本表依赖原始表若agent留存与初始一致而gold不同，先诊断再标不可评估；若gold与初始一致而agent不同，则正常标注并追踪agent运行中的改动。不能把两种情况混淆。raw差异须限定到本表依赖；CS上游用gold。

新增字段统一口径：记录与实际差异机制相关的明确选择/可疑数据表述；不要求agent预知gold，也不把泛称“完成清洗”算作识别具体边界。021关于重复计数、029关于可选字段失败置NULL为适用范围较广的声明，单独注明并未点名本表异常；可见证据只能支持这一有限范围。该字段不增减U/C/D/I/A/O/X条件。
