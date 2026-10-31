# KramaBench / wildfire-hard-14：v3.1 修订

相对034：**只改档位**。主要原因：Unstated Choice → **Unstated Choice**；只能组合修复：否 → 否；把握：中。

基础错误机制及原有查询见 [034原标注](../034_annotations/kramabench_wildfire-hard-14.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。

## 州比例加权口径

- 角色：主要；类别：Unstated Choice → **Unstated Choice**。
- 是否说出：没有迹象 → **看到了相关信息，但没有意识到的迹象**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

中间比较0.64/0.42针对AQI阈值，不是本错误点的州/县比例加权；只记相关信息可见。

来源：`records/028_kramabench_packages/wildfire-hard-14.md`，事件/位置 `step.4.feedback`。
```text
n 50 states ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
only >150 0.6399680906820299
>100 0.4192615693324732
rows        State  prop_u150  prop_gt100  Total Acres Burned
  California   0.018958    0.055709           1081144.0
      Oregon   0.007894    0.015372           1797796.0
      Alaska   0.006856    0.017630            667075.0
  New Mexico   0.006849    0.037671             82531.0
North Dakota   0.006083    0.027981            173237.0
       Texas   0.005409    0.030318           1314903.0
 Connecticut   0.005054    0.032491               339.0
    Colorado   0.003724    0.033964             60539.0
     Arizona   0.003682    0.038233            282989.0
       Idaho   0.002036    0.006690            996762.0
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/wildfire-hard-14.md;records/032_kramabench_queries/09_wildfire_hard_14.stdout.txt;records/036_checks/disclosure_audit.json。
