# impl-012 / int_marketo__lead（全量；v2）

## 1. 差异与结论

只有STRING_AGG(DISTINCT)无序串接的元素先后不同。契约明确不保证顺序；对留存两侧只规范化该串接序列后，包含评测键的整表L0一致。

主要原因：**O**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-012_int_marketo__lead.md](../../records/022_packages/022_impl-012_int_marketo__lead.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-012_int_marketo__lead/022_impl-012_int_marketo__lead.json`。
- 比较结果：[022_reruns_impl-012_int_marketo__lead.json](../022_reruns_impl-012_int_marketo__lead.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`。

原件第651–699行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/intermediate/int_marketo__lead.sql`；原件第1–1行。

```sql
   1: WITH deleted_leads AS (SELECT DISTINCT lead_id FROM staging.stg_marketo__activity_delete_lead), unique_merges AS (SELECT lead_id, STRING_AGG(DISTINCT merged_lead_ids, ', ') AS merged_into_lead_id FROM staging.stg_marketo__activity_merge_leads GROUP BY lead_id) SELECT l.lead_id,l.email,l.first_name,l.last_name,l.created_timestamp,l.updated_timestamp,(d.lead_id IS NOT NULL) AS is_deleted,m.merged_into_lead_id,(m.merged_into_lead_id IS NOT NULL) AS is_merged FROM staging.stg_marketo__lead l LEFT JOIN deleted_leads d USING (lead_id) LEFT JOIN unique_merges m USING (lead_id)
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/intermediate/int_marketo__lead.sql`；原件第1–28行。

```sql
   1: -- Intermediate: Lead dimension with merge and delete flags
   2: WITH leads AS (
   3:     SELECT *
   4:     FROM staging.stg_marketo__lead
   5: ), activity_merge_leads AS (
   6:     SELECT *
   7:     FROM staging.stg_marketo__activity_merge_leads
   8: ), unique_merges AS (
   9:     SELECT
  10:         lead_id,
  11:         STRING_AGG(DISTINCT merged_lead_ids::VARCHAR, ', ') as merged_into_lead_id
  12:     FROM activity_merge_leads
  13:     GROUP BY 1
  14: ), deleted_leads AS (
  15:     SELECT DISTINCT lead_id
  16:     FROM staging.stg_marketo__activity_delete_lead
  17: ), joined AS (
  18:     SELECT
  19:         leads.*,
  20:         CASE WHEN deleted_leads.lead_id IS NOT NULL THEN TRUE ELSE FALSE END as is_deleted,
  21:         unique_merges.merged_into_lead_id,
  22:         CASE WHEN unique_merges.merged_into_lead_id IS NOT NULL THEN TRUE ELSE FALSE END as is_merged
  23:     FROM leads
  24:     LEFT JOIN deleted_leads ON leads.lead_id = deleted_leads.lead_id
  25:     LEFT JOIN unique_merges ON leads.lead_id = unique_merges.lead_id
  26: )
  27: SELECT *
  28: FROM joined
```

## 3. agent看到的材料与不确定性

已检视该题全部57个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 13 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/13.json`。
- event 14 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/14.json`。

四档：**看到了但没提**。

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

## 4. 核实查询与诊断

核实查询共**3条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT 'staging.stg_marketo__activity_delete_lead' source_table,count(*) rows FROM staging.stg_marketo__activity_delete_lead UNION ALL SELECT 'staging.stg_marketo__activity_merge_leads' source_table,count(*) rows FROM staging.stg_marketo__activity_merge_leads UNION ALL SELECT 'staging.stg_marketo__lead' source_table,count(*) rows FROM staging.stg_marketo__lead
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ....stg_marketo__activity_delete_lead' source_table,count(*) rows FROM staging.stg_marketo__activity_delete_lead UNION...\n                                                                     ^"}
```

### 核实 V2：merge重复组

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT count(*) leads,sum(n) merge_rows,count(*) FILTER(WHERE n>1) multi_value_leads FROM (SELECT lead_id,count(DISTINCT merged_lead_ids) n FROM staging.stg_marketo__activity_merge_leads GROUP BY lead_id)
```

```json
{"columns": ["leads", "merge_rows", "multi_value_leads"], "result": [[754, 800, 42]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT 'staging.stg_marketo__activity_delete_lead' source_table,count(*) source_rows FROM staging.stg_marketo__activity_delete_lead UNION ALL SELECT 'staging.stg_marketo__activity_merge_leads' source_table,count(*) source_rows FROM staging.stg_marketo__activity_merge_leads UNION ALL SELECT 'staging.stg_marketo__lead' source_table,count(*) source_rows FROM staging.stg_marketo__lead
```

```json
{"columns": ["source_table", "source_rows"], "result": [["staging.stg_marketo__activity_delete_lead", 500], ["staging.stg_marketo__activity_merge_leads", 800], ["staging.stg_marketo__lead", 5984]]}
```

### 诊断（允许gold，不计5条）

`records/022_diagnostics.json` 本表条目：

```json
{"index": 0, "kind": "诊断查询", "queries": [], "order_canonicalization": {"levels": [{"level": "L0", "agent_rows": 5990, "gold_rows": 5990, "agent_only_key_rows": 0, "gold_only_key_rows": 0, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"lead_id": 0, "created_timestamp": 0, "email": 0, "first_name": 0, "is_deleted": 0, "is_merged": 0, "last_name": 0, "merged_into_lead_id": 0, "updated_timestamp": 0}, "key_aware_agent_unmatched": 0, "key_aware_gold_unmatched": 0, "whole_match": true, "row_scale": 0, "cell_scale": 0, "comparison_column_count_including_keys": 9}, {"level": "L1", "agent_rows": 5990, "gold_rows": 5990, "agent_only_key_rows": 0, "gold_only_key_rows": 0, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"lead_id": 0, "created_timestamp": 0, "email": 0, "first_name": 0, "is_deleted": 0, "is_merged": 0, "last_name": 0, "merged_into_lead_id": 0, "updated_timestamp": 0}, "key_aware_agent_unmatched": 0, "key_aware_gold_unmatched": 0, "whole_match": true, "row_scale": 0, "cell_scale": 0, "comparison_column_count_including_keys": 9}, {"level": "L2", "agent_rows": 5990, "gold_rows": 5990, "agent_only_key_rows": 0, "gold_only_key_rows": 0, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"lead_id": 0, "created_timestamp": 0, "email": 0, "first_name": 0, "is_deleted": 0, "is_merged": 0, "last_name": 0, "merged_into_lead_id": 0, "updated_timestamp": 0}, "key_aware_agent_unmatched": 0, "key_aware_gold_unmatched": 0, "whole_match": true, "row_scale": 0, "cell_scale": 0, "comparison_column_count_including_keys": 9}, {"level": "L3", "agent_rows": 5990, "gold_rows": 5990, "agent_only_key_rows": 0, "gold_only_key_rows": 0, "common_key_agent_excess_rows": 0, "common_key_gold_excess_rows": 0, "common_key_different_rows_or_min_pairs": 0, "column_mismatches": {"lead_id": 0, "created_timestamp": 0, "email": 0, "first_name": 0, "is_deleted": 0, "is_merged": 0, "last_name": 0, "merged_into_lead_id": 0, "updated_timestamp": 0}, "key_aware_agent_unmatched": 0, "key_aware_gold_unmatched": 0, "whole_match": true, "row_scale": 0, "cell_scale": 0, "comparison_column_count_including_keys": 9}], "first_match": "L0"}, "transformation": "仅对merged_into_lead_id以逗号空格分组、排序；其他列和重复次数原样，键保留。"}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["lead_id"]`；比较列：`["created_timestamp", "email", "first_name", "is_deleted", "is_merged", "last_name", "lead_id", "merged_into_lead_id", "updated_timestamp"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 5990/5990 | 0/0 | 0/0 | 18 | 18 | 18 | False |
| L1 | 5990/5990 | 0/0 | 0/0 | 18 | 18 | 18 | False |
| L2 | 5990/5990 | 0/0 | 0/0 | 18 | 18 | 18 | False |
| L3 | 5990/5990 | 0/0 | 0/0 | 18 | 18 | 18 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| lead_id | 0 | 0 | 0 | 0 |
| created_timestamp | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| is_deleted | 0 | 0 | 0 | 0 |
| is_merged | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| merged_into_lead_id | 18 | 18 | 18 | 18 |
| updated_timestamp | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-012_int_marketo__lead/baseline.sql`；SHA-256：`041141f0abf834b9079343df41529c6c5f36cdce1eaa2a966ae1bbaec51984dc`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 5990/5990 | 0/0 | 0/0 | 11 | 11 | 11 | False |
| L1 | 5990/5990 | 0/0 | 0/0 | 11 | 11 | 11 | False |
| L2 | 5990/5990 | 0/0 | 0/0 | 11 | 11 | 11 | False |
| L3 | 5990/5990 | 0/0 | 0/0 | 11 | 11 | 11 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| lead_id | 0 | 0 | 0 | 0 |
| created_timestamp | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| is_deleted | 0 | 0 | 0 | 0 |
| is_merged | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| merged_into_lead_id | 11 | 11 | 11 | 11 |
| updated_timestamp | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

不适用：契约允许顺序的O诊断。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。


## 规则问题

无。按v2冻结定义执行。
