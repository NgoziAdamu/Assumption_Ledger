# KramaBench / archeology-hard-1（v3）

## 错在哪里
题面average ... from the first and last time且规定样点间线性插值，按整个区间平均的自然读法；step8只平均两端。单改年度格点8347.1887→8477.5473，与gold差230.3411→99.9825；未解释残差。

## 题面与判错记录
来源：[records/028_kramabench_packages/archeology-hard-1.md](../028_kramabench_packages/archeology-hard-1.md)，官方状态按029未通过不改。
```text
What is the average Potassium in ppm from the first and last time the study recorded people in the Maltese area? Assume that Potassium is linearly interpolated between samples. Round your answer to 4 decimal places.
```
agent最终答案：
```text
8347.1887
```
参考答案：
```text
8577.5298
```
主要原因：Intent Misreading；只能组合修复：否。
## 错误点：只平均两个端点
- 角色：主要；类别：**Intent Misreading**；把握：低。
题面average ... from the first and last time且规定样点间线性插值，按整个区间平均的自然读法；step8只平均两端。单改年度格点8347.1887→8477.5473，与gold差230.3411→99.9825；未解释残差。
- 是否说出：针对本处的具体说明；证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.8.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Calculating average potassium levels**

I need to determine the average potassium level in ppm from the first and last recorded times of a study in the Maltese area. I'm looking at the earliest date, around 6412 BP, and the latest at about 6005 BP. It seems like I should use these direct radiocarbon dates to interpolate and calculate the average. So, I’ll get started on that calculation!
```
轨迹事件 `step.8.code` 原文（代码行从本代码块1起计）：
```text
import numpy as np
ages=np.array([6.005,6.412])
vals=np.interp(ages,c.Age_ky,c.K)
print(vals, vals.mean(), round(float(vals.mean()),4))
# if choose chronology ages dates are calibrated? dates available only raw radiocarbon; identify units.
```
证据：records/028_kramabench_packages/archeology-hard-1.md；records/032_kramabench_queries/04_archeology_hard_1.stdout.txt;records/034_checks/archeology-hard-1_interval_mean.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
读法一：from first and last指仅两端；读法二：从首至尾整个区间。选二，插值条件支持区间；但gold子任务年龄整数化/插值规则仍未定，不能宣称单改完全解释。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
