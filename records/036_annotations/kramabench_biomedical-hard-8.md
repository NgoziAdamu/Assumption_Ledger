# KramaBench / biomedical-hard-8：v3.1 修订

相对034：**只改档位**。主要原因：其他 → **其他**；只能组合修复：否 → 否；把握：中。

基础错误机制及原有查询见 [034原标注](../034_annotations/kramabench_biomedical-hard-8.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。

## protein与site粒度

- 角色：主要；类别：其他 → **其他**。
- 是否说出：针对本处的具体说明 → **过程中意识到了，交付物里没提**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：是（均沿用034）。

最终答案没有说明该处；第3档依据所引中间事件对做法、前提或呈现的明确表述。

来源：`records/028_kramabench_packages/biomedical-hard-8.md`，事件/位置 `step.16.reasoning.3`。
```text
**Planning gene analysis**

I’m working on the gene expression analysis, mainly focusing on the sheet differential proteins. I think simplifying the README under the sheet could help. The "FoldChange" column likely reflects a computation of endometrioid versus serous datasets in R. I may need candidates with hyperactivated genes that have significant positive phosphorylation in Endometrioid compared to Serous.

I want to get an exact list of associated genes and possibly the drugs linked to them. This output will be formatted as a list and provided in Python, noting the IDs of the sites as well.**Clarifying drug and gene targets**

I’m thinking about classifying only FDA-approved drugs and focusing on gene-target intersections. The table will describe "FDA-approved drugs" without mentioning their status. I’ll specifically identify protein sites as targets, highlighting genes like CDK12 and SMARCA4. I want to output five site IDs that correspond to the conditions of FDR < 0.05 and `FoldChange.phos > 0`.

I’ll validate that for the CNV-high endometrial samples, there are exactly nine. It seems there are three samples for CDK12 and two for SMARCA4. I'll determine which results need to be included based on the criteria.**Checking hyperactivated proteins**

I'm a bit concerned because the source for the "hyperactivated.csv" uses lowercase for the proteins list but includes sample identifiers in the data. I think the CNV high criteria might need to reflect `Genomics_subtype == 'CNV_high'` instead of `CNV_class == CNV_HIGH`. I should verify if this corresponds to the same nine Endometrioid samples. It’s important to double-check these settings to ensure I’m correctly interpreting the data and identifying the right samples!
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/biomedical-hard-8.md;records/034_checks/form_checks.json;records/036_checks/disclosure_audit.json。
