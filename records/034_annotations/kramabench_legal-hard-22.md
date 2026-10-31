# KramaBench / legal-hard-22（v3）

## 错在哪里
agent用全部报告6471708，gold用身份盗窃1135291；62982分子一致，改分母0.0097→0.0555。题面all reports既可指全部也可指identity theft子域，不能把隐藏子任务当明文。

## 题面与判错记录
来源：[records/028_kramabench_packages/legal-hard-22.md](../028_kramabench_packages/legal-hard-22.md)，官方状态按029未通过不改。
```text
What is the proportion (round to 4 decimal places) of all reports who reported identity theft with Back Account (Theft Type) and New Accounts (Theft Subtype)?
```
agent最终答案：
```text
0.0097
```
参考答案：
```text
0.0555
```
主要原因：Unstated Choice；只能组合修复：否。
## 错误点：all reports分母范围
- 角色：主要；类别：**Unstated Choice**；把握：中。
agent用全部报告6471708，gold用身份盗窃1135291；62982分子一致，改分母0.0097→0.0555。题面all reports既可指全部也可指identity theft子域，不能把隐藏子任务当明文。
- 是否说出：没有迹象；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
轨迹事件 `step.4.code` 原文（代码行从本代码块1起计）：
```text
num=62982; denom=6471708; proportion=round(num/denom,4); print(num/denom, proportion); final_answer(proportion)
```
证据：records/028_kramabench_packages/legal-hard-22.md；records/034_checks/legal-hard-22_identity_denominator.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
all reports全局或限定于identity theft？自然全局读法成立，按Choice而不是Intent。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
