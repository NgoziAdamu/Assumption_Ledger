# impl-019 · apple_store__app_version_report

用途：**全量**；层：`marts`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**A**；把握：高；主要错误点：join_ses。

session metrics 的 NULL 连接键使用 null-safe 相等，gold 使用普通等号；契约未说明该边界。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-019_apple_store__app_version_report.md](../023_packages/023_impl-019_apple_store__app_version_report.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml`；SHA-256 `0546320393fa39035bd8afc85a91a28a2aedccc8bcd9f41662f8fb862b7f5be2`。
契约行 1807–1860：

```
1807:     - name: apple_store__app_version_report
1808:       description: Daily app-version metrics by source_type per app and source_relation; rows follow reporting_grain and missing metrics are output as 0
1809:       grain: One row per source_relation, date_day, app_id, source_type, app_version
1810:       source_models:
1811:       - intermediate.int_apple_store__app_version_report
1812:       - intermediate.int_apple_store__app_dim
1813:       - intermediate.int_apple_store__app_version_app_crashes
1814:       - intermediate.int_apple_store__app_version_install_deletions
1815:       - intermediate.int_apple_store__app_version_sessions_activity
1816:       business_logic: '- Drive the output from intermediate.int_apple_store__app_version_report (reporting_grain), emitting exactly one row per (source_relation, date_day, app_id, source_type, app_version). - Crashes: join intermediate.int_apple_store__app_version_app_crashes at the same grain without further aggregation. - Installations and deletions: sum per (app_id, date_day, app_version, source_type, source_relation) in intermediate.int_apple_store__app_version_install_deletions before joining. - Sessions and active_devices: sum per (app_id, date_day, app_version, source_type, source_relation) in intermediate.int_apple_store__app_version_sessions_activity before joining. - Left join each metric set to reporting_grain on (app_id, date_day, app_version, source_type, source_relation). - Left join app_name from intermediate.int_apple_store__app_dim on (app_id, source_relation). - Convert NULL metric values to 0; preserve original values otherwise. No sorting or rounding is applied.'
1817:       columns:
1818:       - name: source_relation
1819:         data_type: VARCHAR
1820:         description: Source system identifier from reporting_grain; part of the grain
1821:         tests:
1822:         - not_null
1823:       - name: date_day
1824:         data_type: TIMESTAMP
1825:         description: Reporting day from reporting_grain; matched on exact equality
1826:         tests:
1827:         - not_null
1828:       - name: app_id
1829:         data_type: BIGINT
1830:         description: App identifier from reporting_grain; part of the grain
1831:         tests:
1832:         - not_null
1833:       - name: app_name
1834:         data_type: VARCHAR
1835:         description: App name joined from app_dim by (app_id, source_relation); NULL if no match
1836:       - name: source_type
1837:         data_type: VARCHAR
1838:         description: Traffic/source category from reporting_grain; part of the grain
1839:         tests:
1840:         - not_null
1841:       - name: app_version
1842:         data_type: VARCHAR
1843:         description: App version from reporting_grain; part of the grain
1844:         tests:
1845:         - not_null
1846:       - name: crashes
1847:         data_type: HUGEINT
1848:         description: Crash count taken at the reporting grain; NULLs replaced with 0
1849:       - name: deletions
1850:         data_type: HUGEINT
1851:         description: Deletion count summed per grain from install_deletions; NULLs replaced with 0
1852:       - name: installations
1853:         data_type: HUGEINT
1854:         description: Installation count summed per grain from install_deletions; NULLs replaced with 0
1855:       - name: active_devices
1856:         data_type: HUGEINT
1857:         description: Active device count summed per grain from sessions_activity; NULLs replaced with 0
1858:       - name: sessions
1859:         data_type: HUGEINT
1860:         description: Session count summed per grain from sessions_activity; NULLs replaced with 0
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/marts/apple_store__app_version_report.sql`，SHA-256 `92d385b5ca9e6368c72376c0eddccc816c026dc3af5dce071eb64f790ff783f5`，行 1–21。

```
1: WITH g AS (SELECT source_relation, CAST(date_day AS TIMESTAMP) AS date_day, app_id, source_type, app_version FROM intermediate.int_apple_store__app_version_report),
2: cr AS (SELECT source_relation, date_day, app_id, source_type, app_version, crashes FROM intermediate.int_apple_store__app_version_app_crashes),
3: inst AS (SELECT source_relation, date_day, app_id, source_type, app_version, SUM(installations) AS installations, SUM(deletions) AS deletions FROM intermediate.int_apple_store__app_version_install_deletions GROUP BY source_relation, date_day, app_id, source_type, app_version),
4: ses AS (SELECT source_relation, date_day, app_id, source_type, app_version, SUM(sessions) AS sessions, SUM(active_devices) AS active_devices FROM intermediate.int_apple_store__app_version_sessions_activity GROUP BY source_relation, date_day, app_id, source_type, app_version),
5: app AS (SELECT source_relation, app_id, app_name FROM intermediate.int_apple_store__app_dim)
6: SELECT g.source_relation,
7:        g.date_day,
8:        g.app_id,
9:        app.app_name,
10:        g.source_type,
11:        g.app_version,
12:        COALESCE(cr.crashes, 0) AS crashes,
13:        COALESCE(inst.installations, 0) AS installations,
14:        COALESCE(inst.deletions, 0) AS deletions,
15:        COALESCE(ses.sessions, 0) AS sessions,
16:        COALESCE(ses.active_devices, 0) AS active_devices
17: FROM g
18: LEFT JOIN cr ON g.source_relation IS NOT DISTINCT FROM cr.source_relation AND g.date_day IS NOT DISTINCT FROM cr.date_day AND g.app_id IS NOT DISTINCT FROM cr.app_id AND g.source_type IS NOT DISTINCT FROM cr.source_type AND g.app_version IS NOT DISTINCT FROM cr.app_version
19: LEFT JOIN inst ON g.source_relation IS NOT DISTINCT FROM inst.source_relation AND g.date_day IS NOT DISTINCT FROM inst.date_day AND g.app_id IS NOT DISTINCT FROM inst.app_id AND g.source_type IS NOT DISTINCT FROM inst.source_type AND g.app_version IS NOT DISTINCT FROM inst.app_version
20: LEFT JOIN ses ON g.source_relation IS NOT DISTINCT FROM ses.source_relation AND g.date_day IS NOT DISTINCT FROM ses.date_day AND g.app_id IS NOT DISTINCT FROM ses.app_id AND g.source_type IS NOT DISTINCT FROM ses.source_type AND g.app_version IS NOT DISTINCT FROM ses.app_version
21: LEFT JOIN app ON g.source_relation IS NOT DISTINCT FROM app.source_relation AND g.app_id IS NOT DISTINCT FROM app.app_id
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/sql/marts/apple_store__app_version_report.sql`，SHA-256 `cf8fdfd7c5900e6a2382db11fc78833ac4d7d113fc499f11b4604a7e08c3a402`，行 1–67。

```
1: -- Marts: App Version report
2: -- Depends only on intermediate layer
3: 
4: WITH app AS (
5:     SELECT app_id, app_name, source_relation
6:     FROM intermediate.int_apple_store__app_dim
7: ),
8: app_crashes AS (
9:     SELECT app_id, date_day, app_version, source_type, source_relation,
10:            crashes
11:     FROM intermediate.int_apple_store__app_version_app_crashes
12: ),
13: install_deletions AS (
14:     SELECT app_id, date_day, app_version, source_type, source_relation,
15:            SUM(installations) AS installations,
16:            SUM(deletions) AS deletions
17:     FROM intermediate.int_apple_store__app_version_install_deletions
18:     GROUP BY app_id, date_day, app_version, source_type, source_relation
19: ),
20: sessions_activity AS (
21:     SELECT app_id, date_day, app_version, source_type, source_relation,
22:            SUM(sessions) AS sessions,
23:            SUM(active_devices) AS active_devices
24:     FROM intermediate.int_apple_store__app_version_sessions_activity
25:     GROUP BY app_id, date_day, app_version, source_type, source_relation
26: ),
27: reporting_grain AS (
28:     SELECT * FROM intermediate.int_apple_store__app_version_report
29: ),
30: final AS (
31:     SELECT
32:         rg.source_relation,
33:         rg.date_day,
34:         rg.app_id,
35:         a.app_name,
36:         rg.source_type,
37:         rg.app_version,
38:         COALESCE(ac.crashes, 0) AS crashes,
39:         COALESCE(id.deletions, 0) AS deletions,
40:         COALESCE(id.installations, 0) AS installations,
41:         COALESCE(sa.active_devices, 0) AS active_devices,
42:         COALESCE(sa.sessions, 0) AS sessions
43:     FROM reporting_grain AS rg
44:     LEFT JOIN app_crashes AS ac
45:         ON rg.app_id = ac.app_id
46:         AND rg.date_day = ac.date_day
47:         AND rg.source_type = ac.source_type
48:         AND rg.app_version = ac.app_version
49:         AND rg.source_relation = ac.source_relation
50:     LEFT JOIN install_deletions AS id
51:         ON rg.app_id = id.app_id
52:         AND rg.date_day = id.date_day
53:         AND rg.source_type = id.source_type
54:         AND rg.app_version = id.app_version
55:         AND rg.source_relation = id.source_relation
56:     LEFT JOIN sessions_activity AS sa
57:         ON rg.app_id = sa.app_id
58:         AND rg.date_day = sa.date_day
59:         AND rg.source_type = sa.source_type
60:         AND rg.app_version = sa.app_version
61:         AND rg.source_relation = sa.source_relation
62:     LEFT JOIN app AS a
63:         ON rg.app_id = a.app_id
64:         AND rg.source_relation = a.source_relation
65: )
66: SELECT *
67: FROM final
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 11/12 看过raw和各source信息；event 15 后续模型生成session join；event 63 未解释NULL键相等策略。“聚合保留NULL”不等于解释join NULL语义。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 11：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/11.json`。
- event 12：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/12.json`。
- event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/15.json`。
- event 63：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/63.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：NULL 连接键

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/apple_store.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE source_relation IS NULL OR date_day IS NULL OR app_id IS NULL OR source_type IS NULL OR app_version IS NULL) null_keys FROM intermediate.int_apple_store__app_version_sessions_activity
```


```json
{"columns":["n","null_keys"],"rows":[[350,346]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-019_apple_store__app_version_report.json](../023_reruns_impl-019_apple_store__app_version_report.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-019/apple_store.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|82485|82485|342|959|否|
|L1|82485|82485|342|959|否|
|L2|82485|82485|342|959|否|
|L3|82485|82485|342|959|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":342,"sessions":342,"source_type":275}`
- L1：`{"active_devices":342,"sessions":342,"source_type":275}`
- L2：`{"active_devices":342,"sessions":342,"source_type":275}`
- L3：`{"active_devices":342,"sessions":342,"source_type":275}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-019_apple_store__app_version_report/baseline.sql`；SHA-256 `92d385b5ca9e6368c72376c0eddccc816c026dc3af5dce071eb64f790ff783f5`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|82485|82485|342|959|否|
|L1|82485|82485|342|959|否|
|L2|82485|82485|342|959|否|
|L3|82485|82485|342|959|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":342,"sessions":342,"source_type":275}`
- L1：`{"active_devices":342,"sessions":342,"source_type":275}`
- L2：`{"active_devices":342,"sessions":342,"source_type":275}`
- L3：`{"active_devices":342,"sessions":342,"source_type":275}`

#### join_cr

判定：不计参与因素；类别候选 A。契约未明确 NULL 键是否相等连接；agent null-safe，gold 普通等号。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 18 行起、字符 offset 1343 的唯一连续替换；其余字节不动。
替换前：
```sql
LEFT JOIN cr ON g.source_relation IS NOT DISTINCT FROM cr.source_relation AND g.date_day IS NOT DISTINCT FROM cr.date_day AND g.app_id IS NOT DISTINCT FROM cr.app_id AND g.source_type IS NOT DISTINCT FROM cr.source_type AND g.app_version IS NOT DISTINCT FROM cr.app_version
```

替换后：
```sql
LEFT JOIN cr ON g.source_relation = cr.source_relation AND g.date_day = cr.date_day AND g.app_id = cr.app_id AND g.source_type = cr.source_type AND g.app_version = cr.app_version
```

私有 SQL：`data/023_work/impl-019_apple_store__app_version_report/join_cr.sql`；SHA-256 `736d2eef60fdfdf9a532d8a21a8f3e17451def66d1b817c6cba7eeac8b1fec39`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|82485|82485|342|959|否|
|L1|82485|82485|342|959|否|
|L2|82485|82485|342|959|否|
|L3|82485|82485|342|959|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":342,"sessions":342,"source_type":275}`
- L1：`{"active_devices":342,"sessions":342,"source_type":275}`
- L2：`{"active_devices":342,"sessions":342,"source_type":275}`
- L3：`{"active_devices":342,"sessions":342,"source_type":275}`

#### join_inst

判定：不计参与因素；类别候选 A。契约未明确 NULL 键是否相等连接；agent null-safe，gold 普通等号。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 19 行起、字符 offset 1617 的唯一连续替换；其余字节不动。
替换前：
```sql
LEFT JOIN inst ON g.source_relation IS NOT DISTINCT FROM inst.source_relation AND g.date_day IS NOT DISTINCT FROM inst.date_day AND g.app_id IS NOT DISTINCT FROM inst.app_id AND g.source_type IS NOT DISTINCT FROM inst.source_type AND g.app_version IS NOT DISTINCT FROM inst.app_version
```

替换后：
```sql
LEFT JOIN inst ON g.source_relation = inst.source_relation AND g.date_day = inst.date_day AND g.app_id = inst.app_id AND g.source_type = inst.source_type AND g.app_version = inst.app_version
```

私有 SQL：`data/023_work/impl-019_apple_store__app_version_report/join_inst.sql`；SHA-256 `1e054fa1c009ac28c5986a249fc1f93ac7253c19c4d9ed9e53dae87d841b5dd4`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|82485|82485|342|959|否|
|L1|82485|82485|342|959|否|
|L2|82485|82485|342|959|否|
|L3|82485|82485|342|959|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":342,"sessions":342,"source_type":275}`
- L1：`{"active_devices":342,"sessions":342,"source_type":275}`
- L2：`{"active_devices":342,"sessions":342,"source_type":275}`
- L3：`{"active_devices":342,"sessions":342,"source_type":275}`

#### join_ses

判定：主因；类别候选 A。契约未明确 NULL 键是否相等连接；agent null-safe，gold 普通等号。

相对本轮基线减少行 342、格 959；按行优先、格次之排序。
共同控制后 SQL 第 20 行起、字符 offset 1903 的唯一连续替换；其余字节不动。
替换前：
```sql
LEFT JOIN ses ON g.source_relation IS NOT DISTINCT FROM ses.source_relation AND g.date_day IS NOT DISTINCT FROM ses.date_day AND g.app_id IS NOT DISTINCT FROM ses.app_id AND g.source_type IS NOT DISTINCT FROM ses.source_type AND g.app_version IS NOT DISTINCT FROM ses.app_version
```

替换后：
```sql
LEFT JOIN ses ON g.source_relation = ses.source_relation AND g.date_day = ses.date_day AND g.app_id = ses.app_id AND g.source_type = ses.source_type AND g.app_version = ses.app_version
```

私有 SQL：`data/023_work/impl-019_apple_store__app_version_report/join_ses.sql`；SHA-256 `0e629a834af3f8eda8f3a44ea5944f263c7b8331183d04164315fbfd07f4c21f`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|82485|82485|0|0|是|
|L1|82485|82485|0|0|是|
|L2|82485|82485|0|0|是|
|L3|82485|82485|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

#### join_app

判定：不计参与因素；类别候选 A。契约未明确 NULL 键是否相等连接；agent null-safe，gold 普通等号。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 21 行起、字符 offset 2183 的唯一连续替换；其余字节不动。
替换前：
```sql
LEFT JOIN app ON g.source_relation IS NOT DISTINCT FROM app.source_relation AND g.app_id IS NOT DISTINCT FROM app.app_id
```

替换后：
```sql
LEFT JOIN app ON g.source_relation = app.source_relation AND g.app_id = app.app_id
```

私有 SQL：`data/023_work/impl-019_apple_store__app_version_report/join_app.sql`；SHA-256 `27bbc1674a7be8d7837b012e5cc0c4766f069778263536721dc08547e8360ab9`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|82485|82485|342|959|否|
|L1|82485|82485|342|959|否|
|L2|82485|82485|342|959|否|
|L3|82485|82485|342|959|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"active_devices":342,"sessions":342,"source_type":275}`
- L1：`{"active_devices":342,"sessions":342,"source_type":275}`
- L2：`{"active_devices":342,"sessions":342,"source_type":275}`
- L3：`{"active_devices":342,"sessions":342,"source_type":275}`

## 规则问题

无
