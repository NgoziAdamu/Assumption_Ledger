# impl-007_app_reporting__user_value_segmentation_report（038 正式表）

主要原因：**其他**；把握：高。020定稿旧主要原因：`O`，仅原样保留。

## 范围与材料

- 层：marts。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`，[1827, 1910]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/marts/app_reporting__user_value_segmentation_report.sql`。

- 对比执行输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### gold_roi_labels_diagnostic

- 类别：其他；角色：并列；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约明确ROI标签High/Medium/Low/Uncertain；agent使用短标签，gold为High ROI Expected等长标签。按契约时agent正确；020仅替换ROI CASE验证标签差异。

判定顺序：第3节第1步及第6节；以契约/呈现条件定位差异。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: roi_expectation
>         data_type: VARCHAR
>         description: ROI expectation based on global_avg_clv thresholds (>500 High, >200 Medium, >50 Low, else Uncertain)

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/marts/app_reporting__user_value_segmentation_report.sql`，`delivered SQL`：

> CASE WHEN global_avg_clv>500 THEN 'High' WHEN global_avg_clv>200 THEN 'Medium' WHEN global_avg_clv>50 THEN 'Low' ELSE 'Uncertain' END roi_expectation

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: roi_expectation
>         data_type: VARCHAR
>         description: ROI expectation based on global_avg_clv thresholds (>500 High, >200 Medium, >50 Low, else Uncertain)

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-007_app_reporting__user_value_segmentation_report.json#gold_roi_labels_diagnostic`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 3/6 | 3/3 | 0/3 |
| L1 | 3/6 | 3/3 | 0/3 |
| L2 | 3/3 | 0/0 | 3/3 |
| L3 | 3/3 | 0/0 | 3/3 |

### global_avg_clv浮点输出呈现

- 类别：其他；角色：并列；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

按契约计算的global_avg_clv只剩二进制浮点末位差异，数值容差L2/L3消失；038只将双方输出该列round到10位，其他列比较条件不动，确认是无指定形式的数值呈现差异。

判定顺序：第3节第1步及第6节；以契约/呈现条件定位差异。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: global_avg_clv
>         data_type: DOUBLE
>         description: Unweighted average of the per-country average estimated CLV for the segment

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/marts/app_reporting__user_value_segmentation_report.sql`，`delivered SQL`：

> global AS(SELECT customer_segment,sum(customer_count) global_customer_count,sum(total_revenue) global_segment_revenue,avg(avg_estimated_clv) global_avg_clv,avg(avg_rfm_score) avg_rfm_score,count(DISTINCT buyer_country)::BIGINT countries_present,max(customer_count)::BIGINT largest_country_customer_count,sum(healthy_customers) healthy,sum(critical_customers) critical,sum(high_value_customers) high_value,sum(churn_risk_customers) churn_risk,sum(customer_count) total_customers FROM country GROUP BY customer_segment),

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: global_avg_clv
>         data_type: DOUBLE
>         description: Unweighted average of the per-country average estimated CLV for the segment

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/038_checks/rerun_impl-007_app_reporting__user_value_segmentation_report.json#clv_presentation`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 3/6 | 3/3 | 0/3 |
| L1 | 3/6 | 3/3 | 0/3 |
| L2 | 3/3 | 3/3 | 0/0 |
| L3 | 3/3 | 3/3 | 0/0 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[53]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='intermediate' AND table_name='int_user_rfm_analysis') ORDER BY table_schema,table_name,ordinal_position`。
