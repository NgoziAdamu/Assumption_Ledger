# KramaBench / archeology-hard-2：v3.1 修订

相对034：**补完无法判定**。主要原因：无法判定 → **无法判定**；只能组合修复：否 → 否；把握：低。

基础错误机制及原有查询见 [034原标注](../034_annotations/kramabench_archeology-hard-2.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

补做三项沿原链到step8最终答案的单改。基线50.25（差11.83）；只反转年龄顺序49.75（差11.33）；只改年度插值50.25；只按年合并50.25。方向单改确定减少0.50，但候选年度处理链尚未识别，不能把测试的两种年度方案当成穷尽。新诊断发现隐藏日历7507个值与第一Age_ky列先round再乘1000全部相同；该轴并非湿干指数自带Age_ky.3。隐藏增长标记却有8360个（均值38.421%），和5993个有效湿干观测不等长，缺失行、年份并列排序/填充的作用未能分离。候选仍包含数据时间轴理解错误、未定抽样/缺失处理及参考链不一致，保持无法判定（低）。不是因减少不足一半或仍有残差而拒绝方向项，而是另一异类候选的修复尚不可确定。

## 时间方向及年度抽样残差

- 角色：主要；类别：无法判定 → **无法判定**。
- 是否说出：没有迹象 → **过程中意识到了，交付物里没提**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

最终答案没有说明该处；第3档依据所引中间事件对做法、前提或呈现的明确表述。

来源：`records/028_kramabench_packages/archeology-hard-2.md`，事件/位置 `step.8.reasoning.2`。
```text
**Analyzing wet-dry index data**

I’m considering that the "wet-dry index was increasing" reflects the direction of the index over time. I should chart age against the index, focusing on interval context values from 4 to 3000 KY. Since the question implies "Across the years" does not mean a strict calendar progression, I’ll calculate how the index changes based on 5993 observations. A reverse chronological view indicates different interpretations, but for increases in the index, I should verify the data order based on age to make accurate comparisons.**Calculating percentage of increases**

I’m thinking about how to use a calculation method to note the chronological convention, ideally showing a simple percentage. I can define consecutive observations where the index increases with the rise of age values, resulting in a calculated figure of 50.25%. That seems solid enough, so I’ll call that my final answer. Now, I just need to implement the final answer in code as per the developer's instructions.
```

证据复用/新增：复用；036新核交付物/轨迹；新做单改/诊断。来源：records/028_kramabench_packages/archeology-hard-2.md;records/032_kramabench_queries/05_archeology_hard_2.stdout.txt;records/034_checks/climate_diagnostic.json;records/036_checks/disclosure_audit.json;records/036_checks/rerun_summary.json;records/036_checks/archeology-hard-2_annual_diagnostic.json。

## 新单改的可识别范围

方向变化在已测三个单改中收益最大；它是已确认的减差因素，但另一候选（隐藏日历/空行链）的具体修复未识别，暂不能排序全部候选。原合并错误点保留，不把年度聚合零收益写成已排除所有年度因素。见 `036_checks/archeology-hard-2_*.json` 与 `annual_diagnostic.py`。
