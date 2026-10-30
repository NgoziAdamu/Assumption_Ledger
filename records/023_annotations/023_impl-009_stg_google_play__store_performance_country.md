# impl-009 · stg_google_play__store_performance_country

用途：**校准**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**A**；把握：高；主要错误点：country_projection。

country 的编码制式及映射未由本表契约规定；数据支持 numeric 和 alpha_2 之间的关系，不能据 gold 选择推断应输出哪一种。单改 country 投影后行规模 15200→2400，格规模 91200→14400；主要差异取决于契约没定的选择。

参与因素：U：join_cardinality（行减少2400，格减少14400）。

标记：无。

盲标冻结文件023_calibration_blind_decisions.json；018仅在锁定后读取比较。

## 材料与比较口径

精简材料包：[013_impl-009_staging_stg_google_play__store_performance_country.md](../013_packages/013_impl-009_staging_stg_google_play__store_performance_country.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`；SHA-256 `ed3e3a4a943b8504299100aa6acd2684c9371bb8a4ddeaa2eca7a1ebc8c32494`。
契约行 360–381：

```
360:     - name: stg_google_play__store_performance_country
361:       description: "Store performance metrics by country"
362:       source_table: "raw.stats_store_performance_country"
363:       columns:
364:         - name: date_day
365:           data_type: DATE
366:           constraints: [not_null]
367:         - name: package_name
368:           data_type: VARCHAR
369:           constraints: [not_null]
370:         - name: country
371:           data_type: VARCHAR
372:           constraints: [not_null]
373:         - name: store_listing_visitors
374:           data_type: INTEGER
375:         - name: store_listing_conversion_rate
376:           data_type: DECIMAL(18,3)
377:         - name: store_listing_installers
378:           data_type: INTEGER
379:         - name: _fivetran_synced
380:           data_type: VARCHAR
381:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`，SHA-256 `52c299334f985027ac5c9f9bbc0be0f8f76f78b2da858fe65f68521477775ec5`，行 1–10。

```
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

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`，SHA-256 `5961baa68e2db107a8e91f721189efa0d863b9b3be85f2e8bbb12ab5fab43056`，行 1–58。

```
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

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 11/12、13/14 看过 country_region 与 country_code_numeric/alpha_2 的列和首行；event 15 编写映射，event 65/67 报告未说明本表 country 编码选择。实施清单不计通用策略。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 11：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/11.json`。
- event 12：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/12.json`。
- event 13：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/13.json`。
- event 14：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/14.json`。
- event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/15.json`。
- event 65：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/65.json`。
- event 67：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json`。

U 参与因素的 P、反证与可见性（盲标原判断）：

```json
[{"category":"U","label":"join_cardinality","P":"country_code_numeric 在映射表中唯一，LEFT JOIN 不会扩行","evidence":"源表 6400 行、连接后 8800 行、numeric_code 有 4 个重复组；event 13/14 只查列及首行，未核查连接键唯一性。单修连接处去重，规模 15200→12800、91200→76800。"}]
```

## 查询

核实查询 **2** 条；核实代价档：**多条查询**。诊断查询不计入 5 条上限。

### 核实：country 编码连接基数

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`。

```sql
SELECT (SELECT count(*) FROM raw.stats_store_performance_country) source_rows,(SELECT count(*) FROM raw.stats_store_performance_country p LEFT JOIN raw.google_play__country_codes c ON c.country_code_numeric=p.country_region) joined_rows,(SELECT count(*) FROM (SELECT country_code_numeric FROM raw.google_play__country_codes GROUP BY 1 HAVING count(*)>1)) duplicate_numeric_codes
```


```json
{"columns":["source_rows","joined_rows","duplicate_numeric_codes"],"rows":[[6400,8800,4]]}
```


### 核实：源键空值

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE date IS NULL) null_date,count(*) FILTER(WHERE package_name IS NULL) null_package,count(*) FILTER(WHERE country_region IS NULL) null_country FROM raw.stats_store_performance_country
```


```json
{"columns":["n","null_date","null_package","null_country"],"rows":[[6400,0,0,0]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-009_stg_google_play__store_performance_country.json](../023_reruns_impl-009_stg_google_play__store_performance_country.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|8800|6400|15200|91200|否|
|L1|8800|6400|15200|91200|否|
|L2|8800|6400|15200|91200|否|
|L3|8800|6400|15200|91200|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":15200,"package_name":15200,"country":15200,"store_listing_conversion_rate":15200,"store_listing_installers":15200,"store_listing_visitors":15200}`
- L1：`{"date_day":15200,"package_name":15200,"country":15200,"store_listing_conversion_rate":15200,"store_listing_installers":15200,"store_listing_visitors":15200}`
- L2：`{"date_day":15200,"package_name":15200,"country":15200,"store_listing_conversion_rate":15200,"store_listing_installers":15200,"store_listing_visitors":15200}`
- L3：`{"date_day":15200,"package_name":15200,"country":15200,"store_listing_conversion_rate":15200,"store_listing_installers":15200,"store_listing_visitors":15200}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-009_stg_google_play__store_performance_country/baseline.sql`；SHA-256 `52c299334f985027ac5c9f9bbc0be0f8f76f78b2da858fe65f68521477775ec5`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|8800|6400|15200|91200|否|
|L1|8800|6400|15200|91200|否|
|L2|8800|6400|15200|91200|否|
|L3|8800|6400|15200|91200|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":15200,"package_name":15200,"country":15200,"store_listing_conversion_rate":15200,"store_listing_installers":15200,"store_listing_visitors":15200}`
- L1：`{"date_day":15200,"package_name":15200,"country":15200,"store_listing_conversion_rate":15200,"store_listing_installers":15200,"store_listing_visitors":15200}`
- L2：`{"date_day":15200,"package_name":15200,"country":15200,"store_listing_conversion_rate":15200,"store_listing_installers":15200,"store_listing_visitors":15200}`
- L3：`{"date_day":15200,"package_name":15200,"country":15200,"store_listing_conversion_rate":15200,"store_listing_installers":15200,"store_listing_visitors":15200}`

#### country_projection

判定：主因；类别候选 A。见盲标记录

相对本轮基线减少行 12800、格 76800；按行优先、格次之排序。
共同控制后 SQL 第 4 行起、字符 offset 122 的唯一连续替换；其余字节不动。
替换前：
```sql
cc.country_code_alpha_2
```

替换后：
```sql
country_region
```

私有 SQL：`data/023_work/impl-009_stg_google_play__store_performance_country/country_projection.sql`；SHA-256 `246c0b119300cefbd415ad498a508a1e7ed05ed94c2263004597a7a977659e95`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|8800|6400|2400|14400|否|
|L1|8800|6400|2400|14400|否|
|L2|8800|6400|2400|14400|否|
|L3|8800|6400|2400|14400|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":2400,"package_name":2400,"country":2400,"store_listing_conversion_rate":2400,"store_listing_installers":2400,"store_listing_visitors":2400}`
- L1：`{"date_day":2400,"package_name":2400,"country":2400,"store_listing_conversion_rate":2400,"store_listing_installers":2400,"store_listing_visitors":2400}`
- L2：`{"date_day":2400,"package_name":2400,"country":2400,"store_listing_conversion_rate":2400,"store_listing_installers":2400,"store_listing_visitors":2400}`
- L3：`{"date_day":2400,"package_name":2400,"country":2400,"store_listing_conversion_rate":2400,"store_listing_installers":2400,"store_listing_visitors":2400}`

#### join_cardinality

判定：参与因素；类别候选 U。见盲标记录

相对本轮基线减少行 2400、格 14400；按行优先、格次之排序。
共同控制后 SQL 第 10 行起、字符 offset 523 的唯一连续替换；其余字节不动。
替换前：
```sql
raw.google_play__country_codes AS cc
```

替换后：
```sql
(SELECT * FROM raw.google_play__country_codes QUALIFY row_number() OVER(PARTITION BY country_code_numeric ORDER BY country_code_alpha_2)=1) AS cc
```

私有 SQL：`data/023_work/impl-009_stg_google_play__store_performance_country/join_cardinality.sql`；SHA-256 `f604ffa3748bfa78f3247da6066eded3993fdba53b779a6851cb730df6841b25`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6400|6400|12800|76800|否|
|L1|6400|6400|12800|76800|否|
|L2|6400|6400|12800|76800|否|
|L3|6400|6400|12800|76800|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"date_day":12800,"package_name":12800,"country":12800,"store_listing_conversion_rate":12800,"store_listing_installers":12800,"store_listing_visitors":12800}`
- L1：`{"date_day":12800,"package_name":12800,"country":12800,"store_listing_conversion_rate":12800,"store_listing_installers":12800,"store_listing_visitors":12800}`
- L2：`{"date_day":12800,"package_name":12800,"country":12800,"store_listing_conversion_rate":12800,"store_listing_installers":12800,"store_listing_visitors":12800}`
- L3：`{"date_day":12800,"package_name":12800,"country":12800,"store_listing_conversion_rate":12800,"store_listing_installers":12800,"store_listing_visitors":12800}`

## 规则问题

无

## 冻结后校准比较

先盲标并写入 [023_calibration_blind_decisions.json](../023_calibration_blind_decisions.json)，SHA-256 锁定于 [023_blind_lock.json](../023_blind_lock.json)，随后才读取 018。

与 018 的主因类别、参与因素、不确定性四档均一致。核实查询数量/代价档、把握可能不同，逐字段记录见 [023_calibration_comparison.json](../023_calibration_comparison.json)。
