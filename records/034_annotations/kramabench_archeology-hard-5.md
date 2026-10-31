# KramaBench / archeology-hard-5（v3）

## 错在哪里
题面In the Maltese dataset；agent筛Region=Malta并取最北样本；gold子任务选row766。032核实row766为Southern Italy、Serra Cicora，而非Malta。存在题面地域/数据集称谓歧义，不据隐藏子任务反判agent应选意大利。

## 题面与判错记录
来源：[records/028_kramabench_packages/archeology-hard-5.md](../028_kramabench_packages/archeology-hard-5.md)，官方状态按029未通过不改。
```text
In the Maltese dataset, find the year of the most northern Neolithic sample, breaking ties by considering the later year. What is the maximum aluminum value recorded in the climate dataset in the closest year to that year? If there are multiple closest years, take the max aluminum value measured across all of them. Round your answer to 4 decimal places.
```
agent最终答案：
```text
36828.7165
```
参考答案：
```text
66158.3691
```
主要原因：其他；只能组合修复：否。
## 错误点：参考样本与地域限定冲突
- 角色：主要；类别：**其他**；把握：低。
题面In the Maltese dataset；agent筛Region=Malta并取最北样本；gold子任务选row766。032核实row766为Southern Italy、Serra Cicora，而非Malta。存在题面地域/数据集称谓歧义，不据隐藏子任务反判agent应选意大利。
- 是否说出：看到了但没提；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
轨迹事件 `step.7.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Clarifying dataset analysis**

I’m looking at a dataset with duplicate age columns, needing to focus on primary aluminum measurements. I have to find the nearest age to 6.412, which might relate to the year 6412. It could connect to calibrated BC ranges, possibly around 4-5k BCE, or even 3 million years ago. The prompt asks for the most northern Neolithic sample year and ties to the maximum aluminum value recorded closest to that year. I need to clarify how to bridge these datasets effectively.**Inferring climate age units**

I need to determine the climate age unit in kiloyears (ky). I should treat the date 6412 as a radiocarbon date in years before present (BP) and find the closest resemblance to Age_ky, which is 6.412. It seems like I have to bridge these two different age formats to understand their relation better. It’s crucial to clarify the context of these numbers and how they apply to my analysis.
```
轨迹事件 `step.7.code` 原文（代码行从本代码块1起计）：
```text
d=pd.read_excel(p)
m=d[(d.Region=='Malta')&(d.Culture=='Neolithic')]
print(m[['Site','date','Latitude','Longitude','Cal. BC 2 sigma','Cal. BC 2 sigma.1']].to_string(index=False))
print('max latitude',m.Latitude.max(),'rows',m[m.Latitude==m.Latitude.max()][['Site','date','Latitude']].to_string(index=False))
print('max date among north',m[m.Latitude==m.Latitude.max()].date.max())
```
证据：records/028_kramabench_packages/archeology-hard-5.md；records/032_kramabench_queries/02_archeology_hard_5.stdout.txt。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
读法一：Maltese指Malta地区；读法二：整本regional数据集俗称Maltese。选一；没有可见说明把Maltese定义为全区域，gold样本地域已核实。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
