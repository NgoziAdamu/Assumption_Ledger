# impl-009 / stg_google_play__store_performance_country

## 1. 错在哪里

把数值country_region翻译为alpha-2且lookup非唯一，将6400行扩成8800行；契约未规定country编码体系。

已核实：raw6400行、lookup250行但数值码246个，4个码各映射两种alpha-2，JOIN多出2400行。country只声明VARCHAR，agent翻成alpha-2而gold保留数值码，主因A。只改输出country表达式保留JOIN，15200→2400行；只去重lookup，15200→12800行，按v1参与因素不要求一半，记U。组合移除翻译表达式及专用JOIN为0，仅用作额外对照，不拿它证明lookup这个P的U4。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-009_staging_stg_google_play__store_performance_country.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml` 第360–381行。
- [原始轨迹转录](../014_trace_impl-009.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-009.json)；[015三方raw核对](../015_raw_impl-009.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_google_play__store_performance_country
      description: "Store performance metrics by country"
      source_table: "raw.stats_store_performance_country"
      columns:
        - name: date_day
          data_type: DATE
          constraints: [not_null]
        - name: package_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: country
          data_type: VARCHAR
          constraints: [not_null]
        - name: store_listing_visitors
          data_type: INTEGER
        - name: store_listing_conversion_rate
          data_type: DECIMAL(18,3)
        - name: store_listing_installers
          data_type: INTEGER
        - name: _fivetran_synced
          data_type: VARCHAR
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`
```sql
   1: SELECT
   2:     try_cast(substr(date, 1, 10) AS DATE) AS date_day,
   3:     CAST(package_name AS VARCHAR) AS package_name,
   4:     CAST(cc.country_code_alpha_2 AS VARCHAR) AS country,
   5:     try_cast(store_listing_visitors AS INTEGER) AS store_listing_visitors,
   6:     try_cast(store_listing_conversion_rate AS DECIMAL(18,3)) AS store_listing_conversion_rate,
   7:     try_cast(store_listing_acquisitions AS INTEGER) AS store_listing_installers,
   8:     CAST(_modified AS VARCHAR) AS _fivetran_synced
   9: FROM raw.stats_store_performance_country
  10: LEFT JOIN raw.google_play__country_codes AS cc ON cc.country_code_numeric = country_region
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`
```sql
   1: with base as (
   2:     select *
   3:     from raw.stats_store_performance_country
   4: ),
   5: 
   6: validated as (
   7:     select
   8:         -- date_day: DATE with not null constraint
   9:         case
  10:             when date is not null then cast(date as date)
  11:             else null
  12:         end as date_day,
  13: 
  14:         -- package_name: VARCHAR with not null constraint
  15:         case
  16:             when package_name is not null then cast(package_name as varchar)
  17:             else null
  18:         end as package_name,
  19: 
  20:         -- country: VARCHAR with not null constraint (mapped from country_region)
  21:         case
  22:             when country_region is not null then cast(country_region as varchar)
  23:             else null
  24:         end as country,
  25: 
  26:         -- store_listing_visitors: INTEGER (no specific validation)
  27:         cast(store_listing_visitors as integer) as store_listing_visitors,
  28: 
  29:         -- store_listing_conversion_rate: DECIMAL(18,3) (no specific validation)
  30:         cast(store_listing_conversion_rate as decimal(18,3)) as store_listing_conversion_rate,
  31: 
  32:         -- store_listing_installers: INTEGER (mapped from store_listing_acquisitions)
  33:         cast(store_listing_acquisitions as integer) as store_listing_installers,
  34: 
  35:         _modified as _fivetran_synced
  36: 
  37:     from base
  38: ),
  39: 
  40: final as (
  41:     select
  42:         date_day,
  43:         package_name,
  44:         country,
  45:         store_listing_visitors,
  46:         store_listing_conversion_rate,
  47:         store_listing_installers,
  48:         _fivetran_synced
  49:     from validated
  50:     where
  51:         -- Enforce not null constraints by deleting rows with null values
  52:         date_day is not null
  53:         and package_name is not null
  54:         and country is not null
  55: )
  56: 
  57: select *
  58: from final
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.google_play__country_codes|gold_vs_initial|True|True|True||
|raw.stats_store_performance_country|gold_vs_initial|True|True|True||
|raw.google_play__country_codes|gold_vs_agent|True|True|True||
|raw.stats_store_performance_country|gold_vs_agent|True|True|True||

## 3. agent看过什么

event 1契约没有country编码说明；event 13→14看过raw schema；event 15添加国家码翻译；没有找到lookup重复键查询。后续event51查看的是stats_installs_country，不是本表lookup唯一性，不算核实。

区分event实际展示的契约/数据与磁盘上存在的资料；截断输出中未出现的部分不算agent已经看到。核实查询是标注者新增查询，不冒充agent执行过。

## 4. 查询与重跑

核实查询合计 **3条**（含014复用；本轮新增0条）；核实代价档：**多条查询**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 014-V1 / 核实查询

来源：`records/014_queries_impl-009.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`。

```sql
SELECT count(*) n,count(country_region) nonnull_country,count(distinct country_region) countries,(SELECT count(*) FROM raw.google_play__country_codes) code_rows,(SELECT count(distinct country_code_numeric) FROM raw.google_play__country_codes) distinct_codes FROM raw.stats_store_performance_country
```
结果原文：
```json
{
  "columns": [
    "n",
    "nonnull_country",
    "countries",
    "code_rows",
    "distinct_codes"
  ],
  "rows": [
    [
      6400,
      6400,
      8,
      250,
      246
    ]
  ]
}
```

### 014-D1 / 诊断查询

来源：`records/014_queries_impl-009.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/google_play.duckdb`。

```sql
SELECT count(*) n,count(country_region) nonnull_country,count(distinct country_region) countries,(SELECT count(*) FROM raw.google_play__country_codes) code_rows,(SELECT count(distinct country_code_numeric) FROM raw.google_play__country_codes) distinct_codes FROM raw.stats_store_performance_country
```
结果原文：
```json
{
  "columns": [
    "n",
    "nonnull_country",
    "countries",
    "code_rows",
    "distinct_codes"
  ],
  "rows": [
    [
      6400,
      6400,
      8,
      250,
      246
    ]
  ]
}
```

### 014-D_raw / 诊断查询

来源：`records/014_queries_impl-009.json`；数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/google_play.duckdb']`。

```sql
SELECT * FROM raw.stats_store_performance_country
```
结果原文：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 6400,
    "gold_rows": 6400,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 014-V2 / 核实查询

来源：`records/014_queries_impl-009.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`。

```sql
SELECT country_code_numeric,count(*) n,list(country_code_alpha_2 ORDER BY country_code_alpha_2) codes FROM raw.google_play__country_codes GROUP BY 1 HAVING count(*)>1 ORDER BY 1
```
结果原文：
```json
{
  "columns": [
    "country_code_numeric",
    "n",
    "codes"
  ],
  "rows": [
    [
      124,
      2,
      [
        "CA",
        "RQ"
      ]
    ],
    [
      156,
      2,
      [
        "CN",
        "ML"
      ]
    ],
    [
      250,
      2,
      [
        "FQ",
        "FR"
      ]
    ],
    [
      276,
      2,
      [
        "DE",
        "LK"
      ]
    ]
  ]
}
```

### 014-V3 / 核实查询

来源：`records/014_queries_impl-009.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`。

```sql
SELECT country_code_numeric,count(*) n,list(country_code_alpha_2 ORDER BY country_code_alpha_2) codes FROM raw.google_play__country_codes GROUP BY 1 HAVING count(*)>1 ORDER BY 1
```
结果原文：
```json
{
  "columns": [
    "country_code_numeric",
    "n",
    "codes"
  ],
  "rows": [
    [
      124,
      2,
      [
        "CA",
        "RQ"
      ]
    ],
    [
      156,
      2,
      [
        "CN",
        "ML"
      ]
    ],
    [
      250,
      2,
      [
        "FQ",
        "FR"
      ]
    ],
    [
      276,
      2,
      [
        "DE",
        "LK"
      ]
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['date_day', 'package_name', 'country']`；比较列（与键取并集）：`['date_day', 'package_name', 'store_listing_conversion_rate', 'store_listing_installers', 'store_listing_visitors']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：records/014_reruns_impl-009.json

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|remove_country_translation|15200→0|91200→0|L0|
|country_value_only|15200→2400|91200→14400|无|
|unique_lookup|15200→12800|91200→76800|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|8800|6400|8800|6400|0/0|0|15200|91200|False|
|L1|8800|6400|8800|6400|0/0|0|15200|91200|False|
|L2|8800|6400|8800|6400|0/0|0|15200|91200|False|
|L3|8800|6400|8800|6400|0/0|0|15200|91200|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

### 重跑 baseline

SQL：`data/014_work/impl-009/baseline.sql`；SHA-256：`52c299334f985027ac5c9f9bbc0be0f8f76f78b2da858fe65f68521477775ec5`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|8800|6400|8800|6400|0/0|0|15200|91200|False|
|L1|8800|6400|8800|6400|0/0|0|15200|91200|False|
|L2|8800|6400|8800|6400|0/0|0|15200|91200|False|
|L3|8800|6400|8800|6400|0/0|0|15200|91200|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

### 重跑 remove_country_translation

SQL：`data/014_work/impl-009/remove_country_translation.sql`；SHA-256：`8b5c6f5ff75124eef0f3cf7a2160b34d92fdbbbc8b5d02f642b9d189339af1b2`。

唯一原文位置offset=117，替换前：
```sql
CAST(cc.country_code_alpha_2 AS VARCHAR)
```
替换后：
```sql
CAST(country_region AS VARCHAR)
```

唯一原文位置offset=503，替换前：
```sql

LEFT JOIN raw.google_play__country_codes AS cc ON cc.country_code_numeric = country_region
```
替换后：
```sql

```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|6400|6400|0|0|0/0|0|0|0|True|
|L1|6400|6400|0|0|0/0|0|0|0|True|
|L2|6400|6400|0|0|0/0|0|0|0|True|
|L3|6400|6400|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

### 重跑 country_value_only

SQL：`data/014_work/impl-009/country_value_only.sql`；SHA-256：`246c0b119300cefbd415ad498a508a1e7ed05ed94c2263004597a7a977659e95`。

唯一原文位置offset=117，替换前：
```sql
CAST(cc.country_code_alpha_2 AS VARCHAR)
```
替换后：
```sql
CAST(country_region AS VARCHAR)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|8800|6400|0|0|2400/0|0|2400|14400|False|
|L1|8800|6400|0|0|2400/0|0|2400|14400|False|
|L2|8800|6400|0|0|2400/0|0|2400|14400|False|
|L3|8800|6400|0|0|2400/0|0|2400|14400|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

### 重跑 unique_lookup

SQL：`data/014_work/impl-009/unique_lookup.sql`；SHA-256：`df64fc34bfd80ec69e0dde34b2ba266b5d3cb9554bce1b39994cafffd8292ea6`。

唯一原文位置offset=513，替换前：
```sql
LEFT JOIN raw.google_play__country_codes AS cc
```
替换后：
```sql
LEFT JOIN (SELECT country_code_numeric,min(country_code_alpha_2) AS country_code_alpha_2 FROM raw.google_play__country_codes GROUP BY country_code_numeric) AS cc
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|6400|6400|6400|6400|0/0|0|12800|76800|False|
|L1|6400|6400|6400|6400|0/0|0|12800|76800|False|
|L2|6400|6400|6400|6400|0/0|0|12800|76800|False|
|L3|6400|6400|6400|6400|0/0|0|12800|76800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

### 复用gold SQL同输入诊断

用于诊断，不是单点修复证据。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|6400|6400|0|0|0/0|0|0|0|True|
|L1|6400|6400|0|0|0/0|0|0|0|True|
|L2|6400|6400|0|0|0/0|0|0|0|True|
|L3|6400|6400|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

## 5. 类别、把握及与014对比

- 主要原因：**A**。
- 主因对应单项：country_value_only。
- 参与因素：U：lookup数值码非唯一，独立去重使15200→12800行。
- 标记：无。
- 把握：**中**。
- 重跑是否满足U第4条件：主因单改是（country_value_only 15200→2400）；lookup这个U参与因素否（15200→12800）。

P（参与因素）：lookup.country_code_numeric唯一。014-V2及重复V3反证；轨迹未查重复。unique_lookup单独减少2400行，但不达一半，U4对这个P写否；按第4节参与因素例外记U。

与014相比：**是：主要A不变；lookup从X参与因素改为U参与因素。**

## 规则问题

U参与因素采用第4节“不要求一半”的例外解释；U4保留逐命题结论。组合remove_country_translation包含两段替换，不替代两项独立对照。

2026-10-29用户确认的第3节补充：仅当本表依赖raw满足agent留存=初始、gold不同，且诊断确认影响可评估性时标“不可评估”；gold=初始、agent不同则照常标注，查轨迹改动。不能把两类混为一谈。若gold与agent一致但二者不同于初始（019/020），当前本节点仍可比较；初始差异另记。

共同执行例外：最初指纹快照因外部v0附件已不在原桌面路径而失败；成功的016快照晚于首批私有重跑。已逐文件与015任务前的大小、mtime、SHA-256比较，覆盖原始库的历史指纹无变化；不把晚快照伪称执行前快照。仓库v0与004–015记录保留。
