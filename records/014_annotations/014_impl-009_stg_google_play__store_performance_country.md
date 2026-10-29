# impl-009 / stg_google_play__store_performance_country

## 1. 错在哪里

把数值country_region翻译为alpha-2且lookup非唯一，将6400行扩成8800行；契约未规定country编码体系。

已核实：raw6400行、8个非空country值，lookup250行但数值码仅246个；124/156/250/276各有两个alpha-2映射，JOIN增加2400行。agent输出alpha-2，gold输出数值码文本。只改country表达式保留JOIN后剩2400条额外行；只使lookup每码一行后变6400行，但键仍全不同；去掉整个翻译操作（表达式及其专用JOIN）L0完全匹配。归因判断：主要A，因为country只声明VARCHAR/not_null，数据不能决定输出编码体系。lookup唯一性是已证伪的候选U，但单独修复未减少一半键相关差异，严格按手册记X参与因素。

## 2. 依据

- 起点：[013精简包](../013_packages/013_impl-009_staging_stg_google_play__store_performance_country.md)。原013状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，第360–381行。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`；gold SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`。精简包完整收录；下列补丁逐字给出定位原文。
- [完整事件记录](../014_trace_impl-009.json)；事件文件在该JSON的path中，可回查traces/dacomp_deimpl_prev.tar.gz。
- [查询原文与结果](../014_queries_impl-009.json)、[全部重跑记录](../014_reruns_impl-009.json)。

### SQL行号定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`
```text
4:     CAST(cc.country_code_alpha_2 AS VARCHAR) AS country,
9: FROM raw.stats_store_performance_country
10: LEFT JOIN raw.google_play__country_codes AS cc ON cc.country_code_numeric = country_region
```

gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`
```text
3:     from raw.stats_store_performance_country
20:         -- country: VARCHAR with not null constraint (mapped from country_region)
22:             when country_region is not null then cast(country_region as varchar)
24:         end as country,
44:         country,
54:         and country is not null
```

## 3. agent看过什么

event 1契约没有country编码说明；event 13→14看过raw schema；event 15添加国家码翻译；没有找到lookup重复键查询。后续event51查看的是stats_installs_country，不是本表lookup唯一性，不算核实。

已逐题核对event 1 message，包含本表契约完整原文；这不是把磁盘上存在的文档等同于agent已经阅读。schema输出、源数据值、运行日志分别处理。轨迹全量转录未删去截断标记；被截断的未显示部分不作为看到的证据。

## 4. 查询与重跑

核实查询实际执行 **3条**；核实代价：**多条查询**。诊断查询不计入5条限制。重复执行的查询仍计数。

### V1：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`

```sql
SELECT count(*) n,count(country_region) nonnull_country,count(distinct country_region) countries,(SELECT count(*) FROM raw.google_play__country_codes) code_rows,(SELECT count(distinct country_code_numeric) FROM raw.google_play__country_codes) distinct_codes FROM raw.stats_store_performance_country
```

结果：
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

### D1：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/google_play.duckdb`

```sql
SELECT count(*) n,count(country_region) nonnull_country,count(distinct country_region) countries,(SELECT count(*) FROM raw.google_play__country_codes) code_rows,(SELECT count(distinct country_code_numeric) FROM raw.google_play__country_codes) distinct_codes FROM raw.stats_store_performance_country
```

结果：
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

### D_raw：诊断查询

数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/google_play.duckdb']`

```sql
SELECT * FROM raw.stats_store_performance_country
```

结果：
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

### V2：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`

```sql
SELECT country_code_numeric,count(*) n,list(country_code_alpha_2 ORDER BY country_code_alpha_2) codes FROM raw.google_play__country_codes GROUP BY 1 HAVING count(*)>1 ORDER BY 1
```

结果：
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

### V3：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`

```sql
SELECT country_code_numeric,count(*) n,list(country_code_alpha_2 ORDER BY country_code_alpha_2) codes FROM raw.google_play__country_codes GROUP BY 1 HAVING count(*)>1 ORDER BY 1
```

结果：
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

原件均READ_ONLY；只把本节点引用表复制到data/014_work私有DuckDB后执行。staging输入来自agent留存库raw；003/008上游直接复制gold，实现CS。固定原评分的comparison_columns与key_columns；L0为lower/trim/NULL规范化，L1数字及布尔归一，L2数值两位小数，L3再放宽日期时间到日期。键始终固定L0，不在宽松档位重新归一。

无共同键时逐列0表示无可比较行，不表示一致。重复键按值/行多重集合抵消，报告最少不一致对数；同时公开额外行次数。为避免键被漏出整表判断，含键整表匹配用于本次U4；旧007式仅值列整表匹配并列展示。这里没有重定义原官方对错或修改旧状态。

比较列：`['date_day', 'package_name', 'store_listing_conversion_rate', 'store_listing_installers', 'store_listing_visitors']`；键：`['date_day', 'package_name', 'country']`。

### 留存基线（013材料来源）

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|8800|6400|8800|6400|0|0/0|8800/6400|False|False|
|L1|8800|6400|8800|6400|0|0/0|8800/6400|False|False|
|L2|8800|6400|8800|6400|0|0/0|8800/6400|False|False|
|L3|8800|6400|8800|6400|0|0/0|8800/6400|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

### 重跑：baseline

不改SQL；建立本轮相同引擎、相同输入的比较基线。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|8800|6400|8800|6400|0|0/0|8800/6400|False|False|
|L1|8800|6400|8800|6400|0|0/0|8800/6400|False|False|
|L2|8800|6400|8800|6400|0|0/0|8800/6400|False|False|
|L3|8800|6400|8800|6400|0|0/0|8800/6400|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

### 重跑：remove_country_translation

只替换以下原文（其余字节经验证不变）：
```sql
CAST(cc.country_code_alpha_2 AS VARCHAR)
```
替换为：
```sql
CAST(country_region AS VARCHAR)
```

只替换以下原文（其余字节经验证不变）：
```sql

LEFT JOIN raw.google_play__country_codes AS cc ON cc.country_code_numeric = country_region
```
替换为：
```sql

```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|6400|6400|0|0|0|0/0|0/0|True|True|
|L1|6400|6400|0|0|0|0/0|0/0|True|True|
|L2|6400|6400|0|0|0|0/0|0/0|True|True|
|L3|6400|6400|0|0|0|0/0|0/0|True|True|

含键整表首次匹配档位：**L0**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

### 重跑：country_value_only

只替换以下原文（其余字节经验证不变）：
```sql
CAST(cc.country_code_alpha_2 AS VARCHAR)
```
替换为：
```sql
CAST(country_region AS VARCHAR)
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|8800|6400|0|0|0|2400/0|2400/0|False|False|
|L1|8800|6400|0|0|0|2400/0|2400/0|False|False|
|L2|8800|6400|0|0|0|2400/0|2400/0|False|False|
|L3|8800|6400|0|0|0|2400/0|2400/0|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

### 重跑：unique_lookup

只替换以下原文（其余字节经验证不变）：
```sql
LEFT JOIN raw.google_play__country_codes AS cc
```
替换为：
```sql
LEFT JOIN (SELECT country_code_numeric,min(country_code_alpha_2) AS country_code_alpha_2 FROM raw.google_play__country_codes GROUP BY country_code_numeric) AS cc
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|6400|6400|6400|6400|0|0/0|6400/6400|False|True|
|L1|6400|6400|6400|6400|0|0/0|6400/6400|False|True|
|L2|6400|6400|6400|6400|0|0/0|6400/6400|False|True|
|L3|6400|6400|6400|6400|0|0/0|6400/6400|False|True|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

### gold SQL在同一私有输入上的诊断

这是诊断，不是局部修复，也不用于证明U4。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|6400|6400|0|0|0|0/0|0/0|True|True|
|L1|6400|6400|0|0|0|0/0|0/0|True|True|
|L2|6400|6400|0|0|0|0/0|0/0|True|True|
|L3|6400|6400|0|0|0|0/0|0/0|True|True|

含键整表首次匹配档位：**L0**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|date_day|0|0|0|0|
|package_name|0|0|0|0|
|store_listing_conversion_rate|0|0|0|0|
|store_listing_installers|0|0|0|0|
|store_listing_visitors|0|0|0|0|

## 5. 类别和把握

- 主要原因：**A**（归因判断）。
- 参与因素：X（lookup非唯一，独立修复未达到U4）。
- 标记：无。
- 把握：**中**。
- 重跑是否满足U第4条件：是（移除整项国家码翻译后L0匹配；A不因此变U）。

P：google_play__country_codes.country_code_numeric唯一。V2（复跑同一SQL另记V3）反证4个重复码。独立unique_lookup干预仅把不匹配行出现次数15200降12800，未达一半；不能利用同时取消编码翻译的组合干预证明这一P满足U4。

## 规则问题

“只改指定一处”可以指一个语义操作或一个连续字节片段。remove_country_translation的两个替换共同移除一次翻译操作，明确公开两段；另有两个独立单项对照，故不会把组合改善冒充lookup唯一性U4。手册未定义满足U前三项但第四项不足、却确实贡献错误时应归何类，暂记X。

共同问题：手册第1节“不预设类别分布”与末句“希望未核实假设多”存在张力；本次以逐条证据条件为准，不按期望调整分布。U3“没看过任何足以判断P的东西”与“证据曾出现但被忽略仍归U”按后者作为例外解释。
