# KramaBench / astronomy-hard-8：v3.1 修订

相对034：**补完无法判定**。主要原因：无法判定 → **Unstated Choice**；只能组合修复：否 → 否；把握：低。

基础错误机制及原有查询见 [034原标注](../034_annotations/kramabench_astronomy-hard-8.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

按第7节同类候选规则补为Unstated Choice（低把握）。训练比例、随机/时间切分、seed、小时聚合及有效标记处理均属未定处理约定。最终只交两个RMSE，中间step9/11才讨论方案，因此第3档。复用034的21条样本切分比较；本次按数值距离复算，但不将整套70/30方案冒充一个已隔离的单改。

## 未指定训练测试及预处理

- 角色：主要；类别：无法判定 → **Unstated Choice**。
- 是否说出：针对本处的具体说明 → **过程中意识到了，交付物里没提**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

最终答案没有说明该处；第3档依据所引中间事件对做法、前提或呈现的明确表述。

来源：`records/028_kramabench_packages/astronomy-hard-8.md`，事件/位置 `step.11.reasoning.1`。
```text
**Analyzing predictive forecasting tasks**

I'm thinking about predictive forecasting, specifically the RMSE being closer to 3.5e-7 instead of 2.5. It seems likely that the task could involve using a dataset with 1-second acceleration and hourly OMNI data. They might aggregate satellite data hourly to make predictions 3 hours ahead. I wonder if we can merge hourly predictors with high-resolution targets. Also, it looks like there's a need to split the dataset for training and testing. I'll need to check the OMNI2 low-res file for details on the data.**Considering data processing for forecasts**

It seems that an hourly format is appropriate for the task, suggesting a chronological split may be ideal for testing. I should probably use a conventional random 80/20 split on all 21 observations with fixed parameters. I’m thinking about reporting values in scientific notation, and it looks like I need to match predictors to the target time -3 hours. If I use Kp and Pdyn inputs from time t, maybe I can merge this at high resolution with hourly labels. I'll also need to ensure the validity of thrust events in the data.
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/astronomy-hard-8.md;records/034_checks/astronomy-hard-8_split_candidates.json;records/034_checks/astronomy-hard-8_chrono70_retry.json;records/036_checks/disclosure_audit.json;records/036_checks/endpoint_audit.json。
