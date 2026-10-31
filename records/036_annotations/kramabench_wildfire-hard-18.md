# KramaBench / wildfire-hard-18：v3.1 修订

相对034：**补完无法判定**。主要原因：无法判定 → **已说出的选择**；只能组合修复：否 → 否；把握：低。

基础错误机制及原有查询见 [034原标注](../034_annotations/kramabench_wildfire-hard-18.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

按第7节同类候选规则补为已说出的选择（低把握）。控制变量集、log1p变换、75% suppression分界、建筑威胁量组合均沿用034的Choice候选解释。最终具体披露这些设定；未知哪个选择贡献最大，不宣称已复现隐藏模型。

## 回归设定和响应量

- 角色：主要；类别：无法判定 → **已说出的选择**。
- 是否说出：针对本处的具体说明 → **交付物里针对本处说明了**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

最终答案明确具体说明该处。

来源：`records/028_kramabench_packages/wildfire-hard-18.md`，事件/位置 `final_answer`。
```text
No—not as a causal conclusion, and not for both outcomes. In the NOAA incident data (6,649 complete cases), I compared fires classified as Full Suppression at the 75% threshold (5,627 cases in the model) with Other, using regressions of log(1 + outcome) that controlled for relative humidity, wind, ERC, precipitation, start year, region, cause, and start day of year, with HC3 robust confidence intervals. Full Suppression was associated with about 60% lower duration on the transformed scale (95% CI: 57%–63% lower; p<0.001). But the summed count of primary residences, commercial buildings, and outbuildings threatened was about 207% higher on the transformed scale (95% CI: 149%–278% higher; p<0.001). This does not show fewer buildings affected: the NOAA fields measure buildings threatened, not buildings actually damaged or destroyed. The result is observational, not evidence that suppression caused fires to end sooner or caused the difference in exposure; treatment selection, initial fire size/severity, and other unmeasured factors could explain the associations. Thus: a strong weather-adjusted association with shorter duration, but no support for fewer buildings threatened, and no causal determination.
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/wildfire-hard-18.md;step.6.code;step.6.feedback;records/036_checks/disclosure_audit.json。
