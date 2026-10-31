# KramaBench / astronomy-hard-9（v3）

## 错在哪里
P：header=None的om[50]是ap-index。文档WORD50=ap-index、WORD51=f10.7，Python列49才是ap；032只改om[50]→om[49]，lag47→24，差23→0。

## 题面与判错记录
来源：[records/028_kramabench_packages/astronomy-hard-9.md](../028_kramabench_packages/astronomy-hard-9.md)，官方状态按029未通过不改。
```text
Determine the best lag (from 0 to 48 hours) between atmospheric drag--measured as semi-major axis change (in km) from TLE data of SATCAT 43180--and the OMNI AP index, that maximizes the r^2 correlation during May 1--30, 2024. TLE epoch times should be rounded to the nearest hour to align with AP measurements. Use hourly OMNI2 data. omni2 data format specification can be found at omni2.text file Use earth's gravitational paremeter mu = 398600.4418 km^3/s^2.
```
agent最终答案：
```text
47
```
参考答案：
```text
24
```
主要原因：Data Misconception；只能组合修复：否。
## 错误点：OMNI列号错位
- 角色：主要；类别：**Data Misconception**；把握：高。
P：header=None的om[50]是ap-index。文档WORD50=ap-index、WORD51=f10.7，Python列49才是ap；032只改om[50]→om[49]，lag47→24，差23→0。
- 是否说出：看到了但没提；证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.5.code` 原文（代码行从本代码块1起计）：
```text
for i,line in enumerate(spec.splitlines()):
 if 'ap-index' in line.lower() or 'F10.7' in line: print(i,line)
```
轨迹事件 `step.5.feedback` 原文（代码行从本代码块1起计）：
```text
25     ap-index and f10.7_index
166 50       I4   999      ap-index                     nT
```
证据：records/028_kramabench_packages/astronomy-hard-9.md；records/032_kramabench_queries/06_astronomy_hard_9.stdout.txt。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
step6反馈整体截断但50/51两行实际保留；只认实际保留原文，不认被省略部分。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
