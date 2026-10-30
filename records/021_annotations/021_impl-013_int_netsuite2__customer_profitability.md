# impl-013 / int_netsuite2__customer_profitability（校准）

## 结论

主要原因：**C**；把握：高。契约明确按连续百分位阈值划分 revenue_score，agent 用 ntile(5) 等行数分桶。只替换该窗口表达式后行/格规模2/4→0/0，L0全表匹配。

参与因素：无。标记：无。

## 差异与归因依据

契约明确按连续百分位阈值划分 revenue_score，agent 用 ntile(5) 等行数分桶。只替换该窗口表达式后行/格规模2/4→0/0，L0全表匹配。

层：intermediate；实际schema：intermediate；评测键：customer_profitability_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml:929–1026`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_profitability.sql:1–1`，SHA-256 `dd5a04a8917c21bf5aff1837a553d8ec0454d7d136ae222e84f8ccd2d7d5303d`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_profitability.sql:1–240`，SHA-256 `2d7ffe4fb23a8c1e53850ba71bb1355162f8d9a5280f66c6bd42f99080188052`。

- percentiles：agent SQL第1行起：
```sql
ntile(5) OVER(ORDER BY total_revenue)
```
替换为：
```sql
CASE WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.8) FROM metrics) THEN 5 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.6) FROM metrics) THEN 4 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.4) FROM metrics) THEN 3 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.2) FROM metrics) THEN 2 ELSE 1 END
```

## agent可见证据与不确定性

**看到了但没提**。

event 51→52 展示本表 revenue_score/total_customer_score 列结构；event19生成 ntile SQL，event63最终报告未说明该分桶差别。未将程序内部读取YAML等同于向agent展示全文。 首次核实查询使用保留字rows作别名，解析失败，改为n后成功；失败计入查询条数。

事件定位补充：报告写入命令为event63，最终finish为event65，二者内容一致；盲标锁定文件保持原样。

扫描67个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=40。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 10 | 9 | False |
| 22 | 21 | False |
| 34 | 33 | False |
| 36 | 35 | False |
| 42 | 41 | False |
| 52 | 51 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`；记录：`records/021_calibration_queries.json`。

```sql
SELECT count(*) n, count(*) FILTER(WHERE revenue_score IS NOT NULL) scored FROM intermediate.int_netsuite2__customer_profitability
```

结果（列顺序["n", "scored"]）：`[[115, 115]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：2行/4格；选定基线：2行/4格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 5}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 2行/4格；L1 2行/4格；L2 2行/4格；L3 2行/4格 | 均未整表匹配 |
| percentiles | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |

不适用：独立盲标主因不是U。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"revenue_score": 2, "total_customer_score": 2} |
| percentiles | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/013_packages/013_impl-013_intermediate_int_netsuite2__customer_profitability.md`。
- 完整机械材料（可由prepare脚本重建）：`records/012_packages/012_impl-013_intermediate_int_netsuite2__customer_profitability.json`。
- 重跑：`records/021_reruns_impl-013_int_netsuite2__customer_profitability.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
