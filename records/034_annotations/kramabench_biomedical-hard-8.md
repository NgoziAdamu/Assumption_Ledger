# KramaBench / biomedical-hard-8（v3）

## 错在哪里
题面明确protein sites，agent返回5个位点而gold仅2个protein。去位点后相同；不能反判输出位点违背题面。

## 题面与判错记录
来源：[records/028_kramabench_packages/biomedical-hard-8.md](../028_kramabench_packages/biomedical-hard-8.md)，官方状态按029未通过不改。
```text
Which protein sites are found to be hyperactivated in CNV-high endometroid samples and are targeted by FDA-approved drugs?
```
agent最终答案：
```text
[
    "CDK12-S1082",
    "CDK12-S301",
    "CDK12-T692",
    "SMARCA4-S1484",
    "SMARCA4-S695"
  ]
```
参考答案：
```text
[
            "CDK12",
            "SMARCA4"
        ]
```
主要原因：其他；只能组合修复：否。
## 错误点：protein与site粒度
- 角色：主要；类别：**其他**；把握：中。
题面明确protein sites，agent返回5个位点而gold仅2个protein。去位点后相同；不能反判输出位点违背题面。
- 是否说出：针对本处的具体说明；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：是。
轨迹事件 `step.16.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Evaluating drug approvals**

I need to determine which drug on the list is actually FDA-approved. It seems like the entries in the G-FDA approved drugs list are supposed to represent curated FDA-approved interactions. However, the list appears to include a mix of investigational drugs and potentially incorrect entries. I'm considering if the interactions come from aggregated annotations, and recognizing that CDK12 inhibitors are likely experimental, whereas olaparib, which targets PARP1/2 and is an approved drug, seems relevant.
```
轨迹事件 `step.16.code` 原文（代码行从本代码块1起计）：
```text
# Verify candidates through subtype-based label, joined gene targets and FDR-significant positive phosphosites
sub=meta[(meta.Histologic_type=='Endometrioid')&(meta.Genomics_subtype=='CNV_high')]
print('subtype samples',sub.idx.tolist(),'same=',set(sub.idx)==set(cnv_endo.idx))
genes=set(h[h.sample_id.isin(sub.idx)].protein)
target_genes=genes & set(drug.gene_name)
ans=ph[(ph.Gene.isin(target_genes))&(ph['FoldChange.phos']>0)&(ph['FDR.phos']<0.05)].sort_values(['Gene','ID'])
print('hyperactivated target genes',sorted(target_genes))
print(ans[['ID','Gene','FoldChange.phos','FDR.phos']].to_string(index=False))
```
证据：records/028_kramabench_packages/biomedical-hard-8.md；records/034_checks/form_checks.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
sites可被宽泛读为proteins或具体磷酸位点；选择后者自然读法，记参考粒度与题面不一致，而非Form Mismatch。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
