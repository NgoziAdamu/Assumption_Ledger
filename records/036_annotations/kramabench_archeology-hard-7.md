# KramaBench / archeology-hard-7：v3.1 修订

相对034：**改类别**。主要原因：已说出的选择 → **Unstated Choice**；只能组合修复：否 → 否；把握：中。

基础错误机制及原有查询见 [034原标注](../034_annotations/kramabench_archeology-hard-7.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。

## 距离度量

- 角色：主要；类别：已说出的选择 → **Unstated Choice**。
- 是否说出：针对本处的具体说明 → **过程中意识到了，交付物里没提**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

最终答案没有说明该处；第3档依据所引中间事件对做法、前提或呈现的明确表述。

来源：`records/028_kramabench_packages/archeology-hard-7.md`，事件/位置 `step.4.reasoning.1`。
```text
**Calculating proximity to ancient cities**

I think the question is about calculating how many modern cities are within 0.1 degrees of ancient Roman cities based on their coordinates. I'm estimating around 295 cities may fit this criterion using rectangular conditions. I’ve got to define the 0.1 degrees, focusing on latitude and longitude differences. While geodesic distance could be useful, I’ll likely stick to using Euclidean distance in this dataset. So, it’s about figuring out which modern cities exceed 100k in population within that threshold.**Calculating geospatial distance**

I need to consider geospatial distance by accounting for latitude and longitude. For a great-circle distance of less than or equal to 0.1 degrees, I might find a lower count due to the cosine of latitude differences. Understanding the Roman-era cities dataset is crucial, which includes 1,388 ancient cities established before or during that era between centuries BC and 244 AD. I want to calculate using the haversine formula for a 0.1-degree threshold, estimating around 262 matches, and validating with output lists.
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/archeology-hard-7.md;records/034_checks/archeology-hard-7_euclidean.json;records/036_checks/disclosure_audit.json;records/036_checks/endpoint_audit.json。
