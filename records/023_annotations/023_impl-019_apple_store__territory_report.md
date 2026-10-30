# impl-019 · apple_store__territory_report

用途：**全量**；层：`marts`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**A**；把握：高；主要错误点：join_ses。

sessions 的 NULL 键连接是主因，downloads 的 NULL 键连接为另一处 A 因素。

参与因素：A：join_dl（行减少1，格减少2）。

标记：无。

ip/dl/ins/ses 预聚合与契约“不聚合”不符，但各自单改规模均不减少，故不列参与因素；也不误标为U。

## 材料与比较口径

精简材料包：[023_impl-019_apple_store__territory_report.md](../023_packages/023_impl-019_apple_store__territory_report.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml`；SHA-256 `0546320393fa39035bd8afc85a91a28a2aedccc8bcd9f41662f8fb862b7f5be2`。
契约行 1949–2021：

```
1949:     - name: apple_store__territory_report
1950:       description: Daily territory/source metrics per app, built from reporting grain with left-joined measures and country metadata, zero-filled for missing measures.
1951:       grain: One row per (source_relation, date_day, app_id, source_type, territory) from intermediate.int_apple_store__territory_report
1952:       source_models:
1953:       - intermediate.int_apple_store__territory_report
1954:       - intermediate.int_apple_store__app_dim
1955:       - intermediate.int_apple_store__territory_impressions_page_views
1956:       - intermediate.int_apple_store__territory_downloads_daily
1957:       - intermediate.int_apple_store__territory_install_deletions
1958:       - intermediate.int_apple_store__territory_sessions_activity
1959:       - intermediate.int_apple_store__country_codes
1960:       business_logic: '- Start from intermediate.int_apple_store__territory_report as the complete reporting grain: one row per (source_relation, date_day, app_id, source_type, territory). - LEFT JOIN app_dim on app_id and source_relation to add app_name; if no match, app_name is NULL. - LEFT JOIN territory_impressions_page_views on app_id, date_day, source_type, territory, and source_relation; set impressions, impressions_unique_device, page_views, and page_views_unique_device to 0 when missing. - LEFT JOIN territory_downloads_daily on the same keys; set first_time_downloads, redownloads, and total_downloads to 0 when missing. - LEFT JOIN territory_install_deletions on the same keys; set deletions and installations to 0 when missing. - LEFT JOIN territory_sessions_activity on the same keys; set active_devices and sessions to 0 when missing. - LEFT JOIN country_codes on territory equals the two-letter country code; set territory_long to the alternative country name when available, otherwise the standard country name; territory_short mirrors the source territory code and is NULL only when the source territory is NULL; region and sub_region come from country_codes and are NULL when no match. - No aggregation or sorting is applied; base rows are preserved and any duplicates in joined sources will propagate. String casing and spacing are unchanged, and date_day is not truncated or timezone-adjusted.'
1961:       columns:
1962:       - name: source_relation
1963:         data_type: VARCHAR
1964:         description: Source system identifier from the reporting grain, also used in all joins.
1965:       - name: date_day
1966:         data_type: TIMESTAMP
1967:         description: Timestamp from the reporting grain; intended as a day but any time component is preserved.
1968:       - name: app_id
1969:         data_type: BIGINT
1970:         description: Application identifier from the reporting grain and the join key to all metric tables and app_dim.
1971:       - name: app_name
1972:         data_type: VARCHAR
1973:         description: Application name from app_dim joined on app_id and source_relation; NULL when no match.
1974:       - name: source_type
1975:         data_type: VARCHAR
1976:         description: Traffic source category from the reporting grain; passed through unchanged.
1977:       - name: territory_long
1978:         data_type: VARCHAR
1979:         description: Country long name from country_codes, preferring the alternative name when present; NULL when no country_codes match.
1980:       - name: territory_short
1981:         data_type: VARCHAR
1982:         description: Two-letter country code from the reporting grain; NULL only when the source territory is NULL.
1983:       - name: region
1984:         data_type: VARCHAR
1985:         description: Region from country_codes for the matched territory; NULL when no country_codes match.
1986:       - name: sub_region
1987:         data_type: VARCHAR
1988:         description: Sub-region from country_codes for the matched territory; NULL when no country_codes match.
1989:       - name: impressions
1990:         data_type: HUGEINT
1991:         description: Impressions from territory_impressions_page_views at the full grain; missing values output as 0.
1992:       - name: impressions_unique_device
1993:         data_type: HUGEINT
1994:         description: Unique-device impressions from territory_impressions_page_views; missing values output as 0.
1995:       - name: page_views
1996:         data_type: HUGEINT
1997:         description: Page views from territory_impressions_page_views; missing values output as 0.
1998:       - name: page_views_unique_device
1999:         data_type: HUGEINT
2000:         description: Unique-device page views from territory_impressions_page_views; missing values output as 0.
2001:       - name: first_time_downloads
2002:         data_type: HUGEINT
2003:         description: First-time downloads from territory_downloads_daily; missing values output as 0.
2004:       - name: redownloads
2005:         data_type: HUGEINT
2006:         description: Redownloads from territory_downloads_daily; missing values output as 0.
2007:       - name: total_downloads
2008:         data_type: HUGEINT
2009:         description: Total downloads from territory_downloads_daily; missing values output as 0.
2010:       - name: active_devices
2011:         data_type: HUGEINT
2012:         description: Active devices from territory_sessions_activity; missing values output as 0.
2013:       - name: deletions
2014:         data_type: HUGEINT
2015:         description: App deletions from territory_install_deletions; missing values output as 0.
2016:       - name: installations
2017:         data_type: HUGEINT
2018:         description: App installations from territory_install_deletions; missing values output as 0.
2019:       - name: sessions
2020:         data_type: HUGEINT
2021:         description: Sessions from territory_sessions_activity; missing values output as 0.
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql`，SHA-256 `06fdff20044f5fd61c0f5030c2cd3871a147abb4974c4d1ceea3e2ccd7d5653e`，行 1–34。

```
1: WITH g AS (SELECT source_relation, CAST(date_day AS TIMESTAMP) AS date_day, app_id, source_type, territory FROM intermediate.int_apple_store__territory_report),
2: app AS (SELECT source_relation, app_id, app_name FROM intermediate.int_apple_store__app_dim),
3: ip AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(impressions) AS impressions, SUM(impressions_unique_device) AS impressions_unique_device, SUM(page_views) AS page_views, SUM(page_views_unique_device) AS page_views_unique_device FROM intermediate.int_apple_store__territory_impressions_page_views GROUP BY source_relation, date_day, app_id, source_type, territory),
4: dl AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(first_time_downloads) AS first_time_downloads, SUM(redownloads) AS redownloads, SUM(total_downloads) AS total_downloads FROM intermediate.int_apple_store__territory_downloads_daily GROUP BY source_relation, date_day, app_id, source_type, territory),
5: ins AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(deletions) AS deletions, SUM(installations) AS installations FROM intermediate.int_apple_store__territory_install_deletions GROUP BY source_relation, date_day, app_id, source_type, territory),
6: ses AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(active_devices) AS active_devices, SUM(sessions) AS sessions FROM intermediate.int_apple_store__territory_sessions_activity GROUP BY source_relation, date_day, app_id, source_type, territory),
7: cc AS (SELECT country_code_alpha_2, alternative_country_name, country_name, region, sub_region FROM intermediate.int_apple_store__country_codes)
8: SELECT g.source_relation,
9:        g.date_day,
10:        g.app_id,
11:        app.app_name,
12:        COALESCE(cc.alternative_country_name, cc.country_name) AS territory_long,
13:        g.territory AS territory_short,
14:        cc.region,
15:        cc.sub_region,
16:        g.source_type,
17:        COALESCE(ip.impressions, 0) AS impressions,
18:        COALESCE(ip.impressions_unique_device, 0) AS impressions_unique_device,
19:        COALESCE(ip.page_views, 0) AS page_views,
20:        COALESCE(ip.page_views_unique_device, 0) AS page_views_unique_device,
21:        COALESCE(dl.first_time_downloads, 0) AS first_time_downloads,
22:        COALESCE(dl.redownloads, 0) AS redownloads,
23:        COALESCE(dl.total_downloads, 0) AS total_downloads,
24:        COALESCE(ins.deletions, 0) AS deletions,
25:        COALESCE(ins.installations, 0) AS installations,
26:        COALESCE(ses.active_devices, 0) AS active_devices,
27:        COALESCE(ses.sessions, 0) AS sessions
28: FROM g
29: LEFT JOIN ip ON g.source_relation IS NOT DISTINCT FROM ip.source_relation AND g.date_day IS NOT DISTINCT FROM ip.date_day AND g.app_id IS NOT DISTINCT FROM ip.app_id AND g.source_type IS NOT DISTINCT FROM ip.source_type AND g.territory IS NOT DISTINCT FROM ip.territory
30: LEFT JOIN dl ON g.source_relation IS NOT DISTINCT FROM dl.source_relation AND g.date_day IS NOT DISTINCT FROM dl.date_day AND g.app_id IS NOT DISTINCT FROM dl.app_id AND g.source_type IS NOT DISTINCT FROM dl.source_type AND g.territory IS NOT DISTINCT FROM dl.territory
31: LEFT JOIN ins ON g.source_relation IS NOT DISTINCT FROM ins.source_relation AND g.date_day IS NOT DISTINCT FROM ins.date_day AND g.app_id IS NOT DISTINCT FROM ins.app_id AND g.source_type IS NOT DISTINCT FROM ins.source_type AND g.territory IS NOT DISTINCT FROM ins.territory
32: LEFT JOIN ses ON g.source_relation IS NOT DISTINCT FROM ses.source_relation AND g.date_day IS NOT DISTINCT FROM ses.date_day AND g.app_id IS NOT DISTINCT FROM ses.app_id AND g.source_type IS NOT DISTINCT FROM ses.source_type AND g.territory IS NOT DISTINCT FROM ses.territory
33: LEFT JOIN app ON g.source_relation IS NOT DISTINCT FROM app.source_relation AND g.app_id IS NOT DISTINCT FROM app.app_id
34: LEFT JOIN cc ON g.territory = cc.country_code_alpha_2
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/sql/marts/apple_store__territory_report.sql`，SHA-256 `d0c84ecaf5b955e6c64a924660d1dad530ce095cdf79139b59b2a1cedffdecd6`，行 1–70。

```
1: -- Marts: Territory report
2: 
3: WITH app AS (
4:   SELECT app_id, app_name, source_relation
5:   FROM intermediate.int_apple_store__app_dim
6: ),
7: impressions_and_page_views AS (
8:   SELECT * FROM intermediate.int_apple_store__territory_impressions_page_views
9: ),
10: downloads_daily AS (
11:   SELECT * FROM intermediate.int_apple_store__territory_downloads_daily
12: ),
13: install_deletions AS (
14:   SELECT * FROM intermediate.int_apple_store__territory_install_deletions
15: ),
16: sessions_activity AS (
17:   SELECT * FROM intermediate.int_apple_store__territory_sessions_activity
18: ),
19: country_codes AS (
20:   SELECT * FROM intermediate.int_apple_store__country_codes
21: ),
22: reporting_grain AS (
23:   SELECT * FROM intermediate.int_apple_store__territory_report
24: ),
25: final AS (
26:   SELECT
27:     rg.source_relation,
28:     rg.date_day,
29:     rg.app_id,
30:     a.app_name,
31:     rg.source_type,
32:     COALESCE(country_codes.alternative_country_name, country_codes.country_name) AS territory_long,
33:     COALESCE(rg.territory, country_codes.country_code_alpha_2) AS territory_short,
34:     country_codes.region AS region,
35:     country_codes.sub_region AS sub_region,
36:     COALESCE(ip.impressions, 0) AS impressions,
37:     COALESCE(ip.impressions_unique_device, 0) AS impressions_unique_device,
38:     COALESCE(ip.page_views, 0) AS page_views,
39:     COALESCE(ip.page_views_unique_device, 0) AS page_views_unique_device,
40:     COALESCE(dd.first_time_downloads, 0) AS first_time_downloads,
41:     COALESCE(dd.redownloads, 0) AS redownloads,
42:     COALESCE(dd.total_downloads, 0) AS total_downloads,
43:     COALESCE(sa.active_devices, 0) AS active_devices,
44:     COALESCE(id.deletions, 0) AS deletions,
45:     COALESCE(id.installations, 0) AS installations,
46:     COALESCE(sa.sessions, 0) AS sessions
47:   FROM reporting_grain rg
48:   LEFT JOIN app a
49:     ON rg.app_id = a.app_id AND rg.source_relation = a.source_relation
50:   LEFT JOIN impressions_and_page_views ip
51:     ON rg.app_id = ip.app_id AND rg.date_day = ip.date_day
52:    AND rg.source_type = ip.source_type AND rg.territory = ip.territory
53:    AND rg.source_relation = ip.source_relation
54:   LEFT JOIN downloads_daily dd
55:     ON rg.app_id = dd.app_id AND rg.date_day = dd.date_day
56:    AND rg.source_type = dd.source_type AND rg.territory = dd.territory
57:    AND rg.source_relation = dd.source_relation
58:   LEFT JOIN install_deletions id
59:     ON rg.app_id = id.app_id AND rg.date_day = id.date_day
60:    AND rg.source_type = id.source_type AND rg.territory = id.territory
61:    AND rg.source_relation = id.source_relation
62:   LEFT JOIN sessions_activity sa
63:     ON rg.app_id = sa.app_id AND rg.date_day = sa.date_day
64:    AND rg.source_type = sa.source_type AND rg.territory = sa.territory
65:    AND rg.source_relation = sa.source_relation
66:   LEFT JOIN country_codes
67:     ON rg.territory = country_codes.country_code_alpha_2
68: )
69: SELECT *
70: FROM final
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 15 及后续模型命令生成null-safe joins；event 63 未解释NULL键连接选择。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/15.json`。
- event 63：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/63.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：NULL 连接键

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/apple_store.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE source_relation IS NULL OR date_day IS NULL OR app_id IS NULL OR source_type IS NULL OR territory IS NULL) null_keys FROM intermediate.int_apple_store__territory_sessions_activity
```


```json
{"columns":["n","null_keys"],"rows":[[2265,11]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-019_apple_store__territory_report.json](../023_reruns_impl-019_apple_store__territory_report.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/apple_store.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|12|24|否|
|L1|219960|219960|12|24|否|
|L2|219960|219960|12|24|否|
|L3|219960|219960|12|24|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L1：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L2：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L3：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-019_apple_store__territory_report/baseline.sql`；SHA-256 `06fdff20044f5fd61c0f5030c2cd3871a147abb4974c4d1ceea3e2ccd7d5653e`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|12|24|否|
|L1|219960|219960|12|24|否|
|L2|219960|219960|12|24|否|
|L3|219960|219960|12|24|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L1：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L2：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L3：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`

#### join_ses

判定：主因；类别候选 A。契约未明确 NULL 键是否相等连接；agent null-safe，gold 普通等号。

相对本轮基线减少行 11、格 22；按行优先、格次之排序。
共同控制后 SQL 第 32 行起、字符 offset 3392 的唯一连续替换；其余字节不动。
替换前：
```sql
LEFT JOIN ses ON g.source_relation IS NOT DISTINCT FROM ses.source_relation AND g.date_day IS NOT DISTINCT FROM ses.date_day AND g.app_id IS NOT DISTINCT FROM ses.app_id AND g.source_type IS NOT DISTINCT FROM ses.source_type AND g.territory IS NOT DISTINCT FROM ses.territory
```

替换后：
```sql
LEFT JOIN ses ON g.source_relation = ses.source_relation AND g.date_day = ses.date_day AND g.app_id = ses.app_id AND g.source_type = ses.source_type AND g.territory = ses.territory
```

私有 SQL：`data/023_work/impl-019_apple_store__territory_report/join_ses.sql`；SHA-256 `d611f61303b439f1157e95f61143b8966907af7a70deaf76ec45b0ac646d4505`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|1|2|否|
|L1|219960|219960|1|2|否|
|L2|219960|219960|1|2|否|
|L3|219960|219960|1|2|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"redownloads":1,"total_downloads":1}`
- L1：`{"redownloads":1,"total_downloads":1}`
- L2：`{"redownloads":1,"total_downloads":1}`
- L3：`{"redownloads":1,"total_downloads":1}`

#### join_ip

判定：不计参与因素；类别候选 A。契约未明确 NULL 键是否相等连接；agent null-safe，gold 普通等号。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 29 行起、字符 offset 2576 的唯一连续替换；其余字节不动。
替换前：
```sql
LEFT JOIN ip ON g.source_relation IS NOT DISTINCT FROM ip.source_relation AND g.date_day IS NOT DISTINCT FROM ip.date_day AND g.app_id IS NOT DISTINCT FROM ip.app_id AND g.source_type IS NOT DISTINCT FROM ip.source_type AND g.territory IS NOT DISTINCT FROM ip.territory
```

替换后：
```sql
LEFT JOIN ip ON g.source_relation = ip.source_relation AND g.date_day = ip.date_day AND g.app_id = ip.app_id AND g.source_type = ip.source_type AND g.territory = ip.territory
```

私有 SQL：`data/023_work/impl-019_apple_store__territory_report/join_ip.sql`；SHA-256 `f9f6bcf7c0a8ebb8458b90fc5b4efa43854153209fe510e176d7c8a6c4d7e3a6`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|12|24|否|
|L1|219960|219960|12|24|否|
|L2|219960|219960|12|24|否|
|L3|219960|219960|12|24|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L1：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L2：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L3：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`

#### join_dl

判定：参与因素；类别候选 A。契约未明确 NULL 键是否相等连接；agent null-safe，gold 普通等号。

相对本轮基线减少行 1、格 2；按行优先、格次之排序。
共同控制后 SQL 第 30 行起、字符 offset 2846 的唯一连续替换；其余字节不动。
替换前：
```sql
LEFT JOIN dl ON g.source_relation IS NOT DISTINCT FROM dl.source_relation AND g.date_day IS NOT DISTINCT FROM dl.date_day AND g.app_id IS NOT DISTINCT FROM dl.app_id AND g.source_type IS NOT DISTINCT FROM dl.source_type AND g.territory IS NOT DISTINCT FROM dl.territory
```

替换后：
```sql
LEFT JOIN dl ON g.source_relation = dl.source_relation AND g.date_day = dl.date_day AND g.app_id = dl.app_id AND g.source_type = dl.source_type AND g.territory = dl.territory
```

私有 SQL：`data/023_work/impl-019_apple_store__territory_report/join_dl.sql`；SHA-256 `a8e87097b5283184e21f178d5237b5f99342ffebd776f520de9bfdc9270dc46c`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|11|22|否|
|L1|219960|219960|11|22|否|
|L2|219960|219960|11|22|否|
|L3|219960|219960|11|22|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":11,"sessions":11}`
- L1：`{"active_devices":11,"sessions":11}`
- L2：`{"active_devices":11,"sessions":11}`
- L3：`{"active_devices":11,"sessions":11}`

#### join_ins

判定：不计参与因素；类别候选 A。契约未明确 NULL 键是否相等连接；agent null-safe，gold 普通等号。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 31 行起、字符 offset 3116 的唯一连续替换；其余字节不动。
替换前：
```sql
LEFT JOIN ins ON g.source_relation IS NOT DISTINCT FROM ins.source_relation AND g.date_day IS NOT DISTINCT FROM ins.date_day AND g.app_id IS NOT DISTINCT FROM ins.app_id AND g.source_type IS NOT DISTINCT FROM ins.source_type AND g.territory IS NOT DISTINCT FROM ins.territory
```

替换后：
```sql
LEFT JOIN ins ON g.source_relation = ins.source_relation AND g.date_day = ins.date_day AND g.app_id = ins.app_id AND g.source_type = ins.source_type AND g.territory = ins.territory
```

私有 SQL：`data/023_work/impl-019_apple_store__territory_report/join_ins.sql`；SHA-256 `e6e602d9f2bc66c42a9167b02a7cb3edbfd4edf1c7d9033e435c95abc1aba966`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|12|24|否|
|L1|219960|219960|12|24|否|
|L2|219960|219960|12|24|否|
|L3|219960|219960|12|24|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L1：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L2：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L3：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`

#### join_app

判定：不计参与因素；类别候选 A。契约未明确 NULL 键是否相等连接；agent null-safe，gold 普通等号。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 33 行起、字符 offset 3668 的唯一连续替换；其余字节不动。
替换前：
```sql
LEFT JOIN app ON g.source_relation IS NOT DISTINCT FROM app.source_relation AND g.app_id IS NOT DISTINCT FROM app.app_id
```

替换后：
```sql
LEFT JOIN app ON g.source_relation = app.source_relation AND g.app_id = app.app_id
```

私有 SQL：`data/023_work/impl-019_apple_store__territory_report/join_app.sql`；SHA-256 `bc85b700b204b634ddf554c0000813f54e322a48d66fda624e0e520fc51c8569`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|12|24|否|
|L1|219960|219960|12|24|否|
|L2|219960|219960|12|24|否|
|L3|219960|219960|12|24|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L1：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L2：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L3：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`

#### aggregate_ip

判定：不计参与因素；类别候选 C。契约明确不聚合，agent 额外 group by。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 3 行起、字符 offset 255 的唯一连续替换；其余字节不动。
替换前：
```sql
ip AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(impressions) AS impressions, SUM(impressions_unique_device) AS impressions_unique_device, SUM(page_views) AS page_views, SUM(page_views_unique_device) AS page_views_unique_device FROM intermediate.int_apple_store__territory_impressions_page_views GROUP BY source_relation, date_day, app_id, source_type, territory),
```

替换后：
```sql
ip AS (SELECT source_relation, date_day, app_id, source_type, territory, impressions, impressions_unique_device, page_views, page_views_unique_device FROM intermediate.int_apple_store__territory_impressions_page_views),
```

私有 SQL：`data/023_work/impl-019_apple_store__territory_report/aggregate_ip.sql`；SHA-256 `da077aee1b9001180d654bcf50890cb92f2e396ad1186c8a0ce6682e5e8ba2e3`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|12|24|否|
|L1|219960|219960|12|24|否|
|L2|219960|219960|12|24|否|
|L3|219960|219960|12|24|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L1：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L2：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L3：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`

#### aggregate_dl

判定：不计参与因素；类别候选 C。契约明确不聚合，agent 额外 group by。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 4 行起、字符 offset 648 的唯一连续替换；其余字节不动。
替换前：
```sql
dl AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(first_time_downloads) AS first_time_downloads, SUM(redownloads) AS redownloads, SUM(total_downloads) AS total_downloads FROM intermediate.int_apple_store__territory_downloads_daily GROUP BY source_relation, date_day, app_id, source_type, territory),
```

替换后：
```sql
dl AS (SELECT source_relation, date_day, app_id, source_type, territory, first_time_downloads, redownloads, total_downloads FROM intermediate.int_apple_store__territory_downloads_daily),
```

私有 SQL：`data/023_work/impl-019_apple_store__territory_report/aggregate_dl.sql`；SHA-256 `5453e21455138a87c9887027c9bce95ba4fd26aef5ccd22337eb1b8df10959a9`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|12|24|否|
|L1|219960|219960|12|24|否|
|L2|219960|219960|12|24|否|
|L3|219960|219960|12|24|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L1：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L2：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L3：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`

#### aggregate_ins

判定：不计参与因素；类别候选 C。契约明确不聚合，agent 额外 group by。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 5 行起、字符 offset 975 的唯一连续替换；其余字节不动。
替换前：
```sql
ins AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(deletions) AS deletions, SUM(installations) AS installations FROM intermediate.int_apple_store__territory_install_deletions GROUP BY source_relation, date_day, app_id, source_type, territory),
```

替换后：
```sql
ins AS (SELECT source_relation, date_day, app_id, source_type, territory, deletions, installations FROM intermediate.int_apple_store__territory_install_deletions),
```

私有 SQL：`data/023_work/impl-019_apple_store__territory_report/aggregate_ins.sql`；SHA-256 `2b0e1a0a9c77c552f5832a3cfd3d5493818aeb4e153f71597b5b454a65296532`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|12|24|否|
|L1|219960|219960|12|24|否|
|L2|219960|219960|12|24|否|
|L3|219960|219960|12|24|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L1：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L2：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L3：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`

#### aggregate_ses

判定：不计参与因素；类别候选 C。契约明确不聚合，agent 额外 group by。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 6 行起、字符 offset 1246 的唯一连续替换；其余字节不动。
替换前：
```sql
ses AS (SELECT source_relation, date_day, app_id, source_type, territory, SUM(active_devices) AS active_devices, SUM(sessions) AS sessions FROM intermediate.int_apple_store__territory_sessions_activity GROUP BY source_relation, date_day, app_id, source_type, territory),
```

替换后：
```sql
ses AS (SELECT source_relation, date_day, app_id, source_type, territory, active_devices, sessions FROM intermediate.int_apple_store__territory_sessions_activity),
```

私有 SQL：`data/023_work/impl-019_apple_store__territory_report/aggregate_ses.sql`；SHA-256 `3c47a172dd8b7cedf477657d28478d4de0f76fcec7e5f7518e0fe8a365b1b300`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|219960|219960|12|24|否|
|L1|219960|219960|12|24|否|
|L2|219960|219960|12|24|否|
|L3|219960|219960|12|24|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L1：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L2：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`
- L3：`{"active_devices":11,"redownloads":1,"sessions":11,"total_downloads":1}`

## 规则问题

无
