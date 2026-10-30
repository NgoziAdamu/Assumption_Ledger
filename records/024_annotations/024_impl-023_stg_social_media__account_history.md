# impl-023 · stg_social_media__account_history

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

agent按BIGINT及非空键契约过滤后0行；gold保留2500个VARCHAR键，另保留或置空不合timezone表达式的值。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-023_stg_social_media__account_history.md](../024_packages/024_impl-023_stg_social_media__account_history.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。

```text
24:     - name: stg_social_media__account_history
25:       description: "Standardized account metadata with validated timezone field for downstream joins and reporting."
26:       source_table: raw.account_history
27:       columns:
28:         - name: id
29:           data_type: BIGINT
30:           constraints: [not_null]
31:         - name: updated_at
32:           data_type: TIMESTAMP
33:         - name: approval_status
34:           data_type: VARCHAR
35:         - name: business_id
36:           data_type: VARCHAR
37:         - name: business_name
38:           data_type: VARCHAR
39:         - name: created_at
40:           data_type: TIMESTAMP
41:         - name: deleted
42:           data_type: BOOLEAN
43:         - name: industry_type
44:           data_type: VARCHAR
45:         - name: name
46:           data_type: VARCHAR
47:         - name: salt
48:           data_type: VARCHAR
49:         - name: timezone
50:           data_type: VARCHAR
51:           constraints: [not_null]
52:           validation_rules:
53:             - rule: "timezone ~ '^[A-Z][a-z]+/[A-Z][a-z_]+$'"
54:               on_failure: delete_row
55:         - name: timezone_switch_at
56:           data_type: TIMESTAMP
57:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__account_history.sql`；SHA-256 `b53ae2527cb6982e6b2e6441a65e0e2c08a2e9cd6a45aefd3858e6906202e335`。

```text
1: select
2:     try_cast(id as bigint) as id,
3:     updated_at::timestamp as updated_at,
4:     approval_status::varchar as approval_status,
5:     business_id::varchar as business_id,
6:     business_name::varchar as business_name,
7:     created_at::timestamp as created_at,
8:     deleted::boolean as deleted,
9:     industry_type::varchar as industry_type,
10:     name::varchar as name,
11:     salt::varchar as salt,
12:     timezone::varchar as timezone,
13:     timezone_switch_at::timestamp as timezone_switch_at
14: from raw.account_history
15: where try_cast(id as bigint) is not null
16:   and timezone is not null
17:   and regexp_matches(timezone, '^[A-Z][a-z]+/[A-Z][a-z_]+$')
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__account_history.sql`；SHA-256 `d2961dff05230c077718ffd817d40c06157b6f3a1e83c90da0b61f5a7a8cf42a`。

```text
1: WITH source_data AS (
2:     SELECT
3:         id,
4:         updated_at,
5:         approval_status,
6:         business_id,
7:         business_name,
8:         created_at,
9:         deleted,
10:         industry_type,
11:         name,
12:         salt,
13:         timezone,
14:         timezone_switch_at
15:     FROM raw.account_history
16: ),
17: 
18: cleaned_data AS (
19:     SELECT
20:         id,
21:         updated_at,
22:         approval_status,
23:         business_id,
24:         business_name,
25:         created_at,
26:         deleted,
27:         industry_type,
28:         name,
29:         salt,
30:         -- Apply timezone validation and cleaning
31:         CASE
32:             WHEN timezone IS NULL THEN NULL
33:             WHEN timezone IN ('America/Los_Angeles', 'America/New_York', 'Europe/London', 'Europe/Paris', 'Asia/Singapore', 'Asia/Shanghai', 'America/Chicago', 'Europe/Berlin', 'Australia/Sydney') THEN timezone
34:             WHEN NOT REGEXP_MATCHES(timezone, '^[A-Z][a-z]+/[A-Z][a-z_]+$') THEN NULL
35:             ELSE timezone
36:         END AS timezone,
37:         timezone_switch_at
38:     FROM source_data
39:     WHERE timezone IS NOT NULL -- Remove rows with invalid timezone after validation
40: )
41: 
42: SELECT
43:     id,
44:     updated_at,
45:     approval_status,
46:     business_id,
47:     business_name,
48:     created_at,
49:     deleted,
50:     industry_type,
51:     name,
52:     salt,
53:     timezone,
54:     timezone_switch_at
55: FROM cleaned_data
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- 本表主要差异（O）：**针对本表的具体说明**；事件 53。
原句：

```
`account_history.id` 在源中为 VARCHAR，但契约要求 BIGINT；不可转换的键按无效主键处理并删除。
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('account_history') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["account_history","id","VARCHAR"],["account_history","updated_at","TIMESTAMP"],["account_history","_fivetran_synced","TIMESTAMP"],["account_history","approval_status","VARCHAR"],["account_history","business_id","VARCHAR"],["account_history","business_name","VARCHAR"],["account_history","created_at","TIMESTAMP"],["account_history","deleted","BOOLEAN"],["account_history","industry_type","VARCHAR"],["account_history","name","VARCHAR"],["account_history","salt","VARCHAR"],["account_history","timezone","VARCHAR"],["account_history","timezone_switch_at","TIMESTAMP"]]}
```


### 核实：契约键及timezone过滤计数
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT count(*) n,count(try_cast(id AS BIGINT)) numeric_id,count(*) FILTER(WHERE timezone IS NOT NULL AND NOT regexp_matches(timezone,'^[A-Z][a-z]+/[A-Z][a-z_]+$')) invalid_timezone FROM raw.account_history
```


```json
{"columns":["n","numeric_id","invalid_timezone"],"rows":[[2500,0,1035]]}
```


### 诊断：多处组合仅诊断（不用于单点原因排名）
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
select
    id as id,
    updated_at::timestamp as updated_at,
    approval_status::varchar as approval_status,
    business_id::varchar as business_id,
    business_name::varchar as business_name,
    created_at::timestamp as created_at,
    deleted::boolean as deleted,
    industry_type::varchar as industry_type,
    name::varchar as name,
    salt::varchar as salt,
    timezone::varchar as timezone,
    timezone_switch_at::timestamp as timezone_switch_at
from raw.account_history
where true
  and timezone is not null
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|11|11|否|
|L1|2500|2500|11|11|否|
|L2|2500|2500|11|11|否|
|L3|2500|2500|11|11|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"timezone":11}`
- L1：`{"timezone":11}`
- L2：`{"timezone":11}`
- L3：`{"timezone":11}`
labels：`["id_type","id_filter","timezone_filter"]`

### 诊断：agent实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_social_media__account_history'
```


```json
{"columns":["column_name","data_type"],"rows":[["id","BIGINT"],["updated_at","TIMESTAMP"],["approval_status","VARCHAR"],["business_id","VARCHAR"],["business_name","VARCHAR"],["created_at","TIMESTAMP"],["deleted","BOOLEAN"],["industry_type","VARCHAR"],["name","VARCHAR"],["salt","VARCHAR"],["timezone","VARCHAR"],["timezone_switch_at","TIMESTAMP"]]}
```


### 诊断：agent有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT id,timezone FROM staging.stg_social_media__account_history LIMIT 3
```


```json
{"columns":["id","timezone"],"rows":[]}
```


### 诊断：gold实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_social_media__account_history'
```


```json
{"columns":["column_name","data_type"],"rows":[["id","VARCHAR"],["updated_at","TIMESTAMP"],["approval_status","VARCHAR"],["business_id","VARCHAR"],["business_name","VARCHAR"],["created_at","TIMESTAMP"],["deleted","BOOLEAN"],["industry_type","VARCHAR"],["name","VARCHAR"],["salt","VARCHAR"],["timezone","VARCHAR"],["timezone_switch_at","TIMESTAMP"]]}
```


### 诊断：gold有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT id,timezone FROM staging.stg_social_media__account_history LIMIT 3
```


```json
{"columns":["id","timezone"],"rows":[["18ce54lbsn8","America/Los_Angeles"],["18ce54lbsn8","America/Los_Angeles"],["18ce54lbsn8","America/Los_Angeles"]]}
```


### 诊断：gold SQL同gold输入重跑
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
WITH source_data AS (
    SELECT
        id,
        updated_at,
        approval_status,
        business_id,
        business_name,
        created_at,
        deleted,
        industry_type,
        name,
        salt,
        timezone,
        timezone_switch_at
    FROM raw.account_history
),

cleaned_data AS (
    SELECT
        id,
        updated_at,
        approval_status,
        business_id,
        business_name,
        created_at,
        deleted,
        industry_type,
        name,
        salt,
        -- Apply timezone validation and cleaning
        CASE
            WHEN timezone IS NULL THEN NULL
            WHEN timezone IN ('America/Los_Angeles', 'America/New_York', 'Europe/London', 'Europe/Paris', 'Asia/Singapore', 'Asia/Shanghai', 'America/Chicago', 'Europe/Berlin', 'Australia/Sydney') THEN timezone
            WHEN NOT REGEXP_MATCHES(timezone, '^[A-Z][a-z]+/[A-Z][a-z_]+$') THEN NULL
            ELSE timezone
        END AS timezone,
        timezone_switch_at
    FROM source_data
    WHERE timezone IS NOT NULL -- Remove rows with invalid timezone after validation
)

SELECT
    id,
    updated_at,
    approval_status,
    business_id,
    business_name,
    created_at,
    deleted,
    industry_type,
    name,
    salt,
    timezone,
    timezone_switch_at
FROM cleaned_data
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|0|0|是|
|L1|2500|2500|0|0|是|
|L2|2500|2500|0|0|是|
|L3|2500|2500|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 独立单点重跑

### 024_reruns_impl-023_stg_social_media__account_history.json
[024_reruns_impl-023_stg_social_media__account_history.json](../024_reruns_impl-023_stg_social_media__account_history.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|2500|2500|22500|否|
|L1|0|2500|2500|22500|否|
|L2|0|2500|2500|22500|否|
|L3|0|2500|2500|22500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L1：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L2：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L3：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`

#### baseline
私有SQL：`data/024_work/impl-023_stg_social_media__account_history/baseline.sql`；SHA-256 `b53ae2527cb6982e6b2e6441a65e0e2c08a2e9cd6a45aefd3858e6906202e335`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|2500|2500|22500|否|
|L1|0|2500|2500|22500|否|
|L2|0|2500|2500|22500|否|
|L3|0|2500|2500|22500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L1：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L2：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L3：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`

#### id_type
不计参与因素；类别候选O。契约BIGINT而gold保留VARCHAR的非数值键。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第2行、offset 11起替换；其他字节相同。
原表达式：
```sql
try_cast(id as bigint) as id
```

修改后：
```sql
id as id
```

私有SQL：`data/024_work/impl-023_stg_social_media__account_history/id_type.sql`；SHA-256 `b64245c5530bc565c550fa1f61ed0e856aa8d0975772b341b67b951de4e3a3b6`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|2500|2500|22500|否|
|L1|0|2500|2500|22500|否|
|L2|0|2500|2500|22500|否|
|L3|0|2500|2500|22500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L1：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L2：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L3：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`

#### id_filter
不计参与因素；类别候选O。契约id非空与BIGINT，gold保留不能转为数值的ID。
相对本轮基线：行减少-1465，格减少-13185。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第15行、offset 506起替换；其他字节相同。
原表达式：
```sql
where try_cast(id as bigint) is not null
```

修改后：
```sql
where true
```

私有SQL：`data/024_work/impl-023_stg_social_media__account_history/id_filter.sql`；SHA-256 `36028cd195bad46bb3e829fbdb0e61bd145e287242841f9dd39fc7b2e3a2d442`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1465|2500|3965|35685|否|
|L1|1465|2500|3965|35685|否|
|L2|1465|2500|3965|35685|否|
|L3|1465|2500|3965|35685|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":3965,"business_id":3965,"approval_status":3965,"business_name":3965,"deleted":3965,"industry_type":3965,"name":3965,"salt":3965,"timezone":3965}`
- L1：`{"id":3965,"business_id":3965,"approval_status":3965,"business_name":3965,"deleted":3965,"industry_type":3965,"name":3965,"salt":3965,"timezone":3965}`
- L2：`{"id":3965,"business_id":3965,"approval_status":3965,"business_name":3965,"deleted":3965,"industry_type":3965,"name":3965,"salt":3965,"timezone":3965}`
- L3：`{"id":3965,"business_id":3965,"approval_status":3965,"business_name":3965,"deleted":3965,"industry_type":3965,"name":3965,"salt":3965,"timezone":3965}`

#### timezone_filter
不计参与因素；类别候选O。契约要求无效timezone删行；gold对部分无效值置空或白名单保留。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第17行、offset 574起替换；其他字节相同。
原表达式：
```sql
  and regexp_matches(timezone, '^[A-Z][a-z]+/[A-Z][a-z_]+$')
```

修改后：
```sql

```

私有SQL：`data/024_work/impl-023_stg_social_media__account_history/timezone_filter.sql`；SHA-256 `69d6074ef17c29c1eb969b29f5a7630adc7f930f1c6ca48f384501240d002794`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|2500|2500|22500|否|
|L1|0|2500|2500|22500|否|
|L2|0|2500|2500|22500|否|
|L3|0|2500|2500|22500|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L1：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L2：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
- L3：`{"id":2500,"business_id":2500,"approval_status":2500,"business_name":2500,"deleted":2500,"industry_type":2500,"name":2500,"salt":2500,"timezone":2500}`
## 规则问题

类型投影、键非空过滤与timezone过滤相互遮蔽，单改均不降低规模。直接核实gold类型和契约冲突归O，不按零改善标X；组合诊断剩11个timezone格。

