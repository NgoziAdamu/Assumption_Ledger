# impl-012 / marketo__calendar_spine（全量；v2）

## 1. 差异与结论

utils日历到今天或下周相差7行；搜索完整data_contract未发现该表的业务定义，依赖配置只列模型。差异取决于未定日历终点。

主要原因：**A**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| calendar_end | A | 7 | 7 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-012_marketo__calendar_spine.md](../../records/022_packages/022_impl-012_marketo__calendar_spine.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-012_marketo__calendar_spine/022_impl-012_marketo__calendar_spine.json`。
- 比较结果：[022_reruns_impl-012_marketo__calendar_spine.json](../022_reruns_impl-012_marketo__calendar_spine.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`。

未在完整data_contract中检出本表定义；已搜索依赖配置与utils SQL，配置仅指示依赖。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/utils/marketo__calendar_spine.sql`；原件第1–1行。

```sql
   1: WITH date_bounds AS ( SELECT COALESCE(MIN(TRY_CAST(created_at AS DATE)), CURRENT_DATE) AS min_date, CURRENT_DATE AS max_date FROM raw.marketo_lead ) SELECT CAST(generate_series AS DATE) AS date_day FROM date_bounds, GENERATE_SERIES(min_date, max_date, INTERVAL 1 DAY) AS calendar(generate_series)
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/utils/marketo__calendar_spine.sql`；原件第1–19行。

```sql
   1: WITH date_range AS (
   2:     SELECT 
   3:         MIN(created_at) as min_date,
   4:         CURRENT_DATE + INTERVAL '1 week' as max_date
   5:     FROM raw.marketo_lead
   6: ),
   7: 
   8: spine AS (
   9:     SELECT 
  10:         generate_series::DATE as date_day
  11:     FROM generate_series(
  12:         (SELECT CAST(min_date AS DATE) FROM date_range),
  13:         (SELECT max_date FROM date_range),
  14:         INTERVAL '1 day'
  15:     )
  16: )
  17: 
  18: SELECT date_day
  19: FROM spine
```

## 3. agent看到的材料与不确定性

已检视该题全部57个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 55 / finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/55.json`。

四档：**针对本表的具体说明**。

原句（见上述最终报告事件）：

```text
日历延伸至当前日期，并按 lead created date 起算。
```

## 4. 核实查询与诊断

核实查询共**2条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT 'raw.marketo_lead' source_table,count(*) rows FROM raw.marketo_lead
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.marketo_lead' source_table,count(*) rows FROM raw.marketo_lead\n                                                        ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT 'raw.marketo_lead' source_table,count(*) source_rows FROM raw.marketo_lead
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.marketo_lead", 6000]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 2}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["date_day"]`；比较列：`["date_day"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 2477/2484 | 0/7 | 0/0 | 0 | 7 | 7 | False |
| L1 | 2477/2484 | 0/7 | 0/0 | 0 | 7 | 7 | False |
| L2 | 2477/2484 | 0/7 | 0/0 | 0 | 7 | 7 | False |
| L3 | 2477/2484 | 0/7 | 0/0 | 0 | 7 | 7 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| date_day | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-012_marketo__calendar_spine/baseline.sql`；SHA-256：`73b5ce60f60accc4cc1b333f77964c6d8141a49721037ab4f07affd77039bf72`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 2477/2484 | 0/7 | 0/0 | 0 | 7 | 7 | False |
| L1 | 2477/2484 | 0/7 | 0/0 | 0 | 7 | 7 | False |
| L2 | 2477/2484 | 0/7 | 0/0 | 0 | 7 | 7 | False |
| L3 | 2477/2484 | 0/7 | 0/0 | 0 | 7 | 7 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| date_day | 0 | 0 | 0 | 0 |

### calendar_end

SQL：`data/022_work/impl-012_marketo__calendar_spine/calendar_end.sql`；SHA-256：`0b0042507bd49c65fc389d04164dd7b64f2a190dfcde4e1043fa625ecb935a60`。

替换offset=105，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
DATE '2025-10-12' AS max_date
-- 新
DATE '2025-10-12' + INTERVAL '1 week' AS max_date
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 2484/2484 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 2484/2484 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 2484/2484 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 2484/2484 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| date_day | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：calendar_end；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- calendar_end：A；主项。契约未检出该utils表定义；gold多未来7天。（行减少7，格减少7）

## 规则问题

无。按v2冻结定义执行。
