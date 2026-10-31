# KramaBench / legal-hard-18（v3）

## 错在哪里
题面If the 2007 reports were distributed exactly like the 2024 ones；agent用2007已观测identity count259314而非总1070447乘2024类别比率。替换该基数得到91000，126000差35000→0。

## 题面与判错记录
来源：[records/028_kramabench_packages/legal-hard-18.md](../028_kramabench_packages/legal-hard-18.md)，官方状态按029未通过不改。
```text
If the 2007 reports were distributed exactly like the 2024 ones, how many identity theft reports in 2007 would concern people ages 40 or older (rounded to the nearest thousand)?
```
agent最终答案：
```text
126000
```
参考答案：
```text
91000
```
主要原因：Intent Misreading；只能组合修复：否。
## 错误点：保留2007身份盗窃数量
- 角色：主要；类别：**Intent Misreading**；把握：高。
题面If the 2007 reports were distributed exactly like the 2024 ones；agent用2007已观测identity count259314而非总1070447乘2024类别比率。替换该基数得到91000，126000差35000→0。
- 是否说出：看到了但没提；证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.5.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Calculating age distribution for reports**

I could calculate the sum of age 40+ for overall identity theft reports in 2024. It seems like this approach would adjust the statistics by excluding ages that aren't reported as 40 or older. The user's intention might be to determine the percentage of reports that fall into the 40+ age range. I'd need to apply this distribution, parse the data, and compute the necessary figures to get a clearer picture.
```
轨迹事件 `step.5.code` 原文（代码行从本代码块1起计）：
```text
vals=[21420,187195,291807,207658,135758,83485,36790,9605]
known=sum(vals); over40=sum(vals[4:]); print(known,over40,over40/known,259314*over40/known, round(259314*over40/known/1000)*1000, 259314*over40/1135291)
```
证据：records/028_kramabench_packages/legal-hard-18.md；records/034_checks/legal-hard-18_retry.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
未发现需改变手册定义的额外问题。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
