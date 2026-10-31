# KramaBench / biomedical-easy-2（v3）

## 错在哪里
题面限定研究中的Serous样本；Case_excluded的含义明确，agent未落实排除标记。68.1对68.5；排除Case_excluded=Yes后12行平均68.5。只见列名不足确定这14行中的具体排除事实。

## 题面与判错记录
来源：[records/028_kramabench_packages/biomedical-easy-2.md](../028_kramabench_packages/biomedical-easy-2.md)，官方状态按029未通过不改。
```text
What is the average age of patients with serous tumor samples analyzed in the study?
```
agent最终答案：
```text
68.1
```
参考答案：
```text
68.5
```
主要原因：Intent Misreading；只能组合修复：否。
## 错误点：未落实研究纳入范围
- 角色：主要；类别：**Intent Misreading**；把握：中。
题面限定研究中的Serous样本；Case_excluded的含义明确，agent未落实排除标记。68.1对68.5；排除Case_excluded=Yes后12行平均68.5。只见列名不足确定这14行中的具体排除事实。
- 是否说出：看到了但没提；证据在场：否；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.4.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Calculating mean age of tumor samples**

I want to calculate the mean age of serous tumor samples, which might involve looking at metadata that includes tumor types and patient age. I think I need to filter the data for the histologic type "serous" and I’m estimating that there are likely about 14 samples here. Maybe I should also consider if any age data is missing. I’ll need to check the rows to make sure I have everything I need.
```
轨迹事件 `step.4.code` 原文（代码行从本代码块1起计）：
```text
ser=d[(d['Histologic_type'].astype(str).str.strip().str.lower()=='serous') & (d['Proteomics_Tumor_Normal']=='Tumor')]; print(ser.shape); print(ser[['Proteomics_Participant_ID','Proteomics_Tumor_Normal','Histologic_type','Age']].to_string(index=False)); print('mean',ser.Age.mean(),'count',ser.Age.count(),'missing',ser.Age.isna().sum())
```
证据：records/028_kramabench_packages/biomedical-easy-2.md；records/032_kramabench_queries/07_biomedical_serous.stdout.txt。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
可读作全部附件Serous行或正式研究样本；选后者。Data/Intent边界：标记含义清楚，缺的是落实题目研究范围，因此Intent。证据在场严格要求看到具体排除信息，只有列名填否。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
