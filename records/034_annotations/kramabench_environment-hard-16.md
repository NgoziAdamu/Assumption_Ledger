# KramaBench / environment-hard-16（v3）

## 错在哪里
题面marine beaches 2002–2023没有Boston Harbor限制；step5用9个名单，输出0。放开到全部Marine按名称聚合74，差60→14，仍有残差；不能声称已完全复现60。

## 题面与判错记录
来源：[records/028_kramabench_packages/environment-hard-16.md](../028_kramabench_packages/environment-hard-16.md)，官方状态按029未通过不改。
```text
How many marine beaches (from 2002 to 2023 inclusive) remained safe to swimming for the entire time (i.e., no violation at all throughout the seasons; if no data for a beach in a particular year, assume safe)?
```
agent最终答案：
```text
0
```
参考答案：
```text
60
```
主要原因：Intent Misreading；只能组合修复：否。
## 错误点：擅限Boston Harbor
- 角色：主要；类别：**Intent Misreading**；把握：低。
题面marine beaches 2002–2023没有Boston Harbor限制；step5用9个名单，输出0。放开到全部Marine按名称聚合74，差60→14，仍有残差；不能声称已完全复现60。
- 是否说出：看到了但没提；证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.5.code` 原文（代码行从本代码块1起计）：
```text
targets=['Constitution','Castle Island','Pleasure Bay','City Point','M Street Beach','Carson Beach','Malibu','Tenean','Wollaston']
for term in targets:
 x=marine[marine['Beach Name'].str.contains(term,case=False,na=False)]
 v=x[x['Violation'].astype(str).str.strip().str.lower().eq('yes')]
 print(term, 'years', sorted(x.Year.unique().tolist()),'records',len(x),'violations',len(v), 'violation years', sorted(v.Year.unique().tolist()),'names',x['Beach Name'].unique().tolist())
```
证据：records/028_kramabench_packages/environment-hard-16.md；records/034_checks/environment-hard-16_identity_diagnostic.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
海滩身份按名称或community+name？分别74/75且均非60；已核实范围错误能减少差距，但残差不能猜成唯一键问题。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
