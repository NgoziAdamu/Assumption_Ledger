# KramaBench / wildfire-hard-6：v3.1 修订

相对034：**只改档位**。主要原因：Data Misconception → **Data Misconception**；只能组合修复：否 → 否；把握：高。

基础错误机制及原有查询见 [034原标注](../034_annotations/kramabench_wildfire-hard-6.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。

## 误缩短NOAA覆盖起点

- 角色：主要；类别：Data Misconception → **Data Misconception**。
- 是否说出：针对本处的具体说明 → **过程中意识到了，交付物里没提**。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用（均沿用034）。

中间明确声称NOAA从2000开始；最终相关覆盖前提没有交代。

来源：`records/028_kramabench_packages/wildfire-hard-6.md`，事件/位置 `step.4.reasoning.1`。
```text
**Assessing NOAA and NIFC data**

I’m looking at NOAA monthly stats beginning from the year 2000, which include annual totals. I’ll compute the sums for each year, especially since there's overlap with NIFC data. To do this, I might focus on the monthly aggregates provided by NOAA. I’ll parse the data using `pd.read_csv`, skipping the first two rows to get relevant info. Also, I want to assess the intersection of years from 2002 to 2016 while looking into NOAA wildfire records as well!
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/wildfire-hard-6.md;records/032_kramabench_queries/08_wildfire_hard_6.stdout.txt;records/036_checks/disclosure_audit.json。
