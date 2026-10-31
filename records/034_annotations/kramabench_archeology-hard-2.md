# KramaBench / archeology-hard-2（v3）

## 错在哪里
按age升序得到50.25%；032以相同有效列反序49.75%，仍非38.42。子任务使用日历年且包含重复整数年，无法由目前的单改证据确定差异主项；不把反序一项冒充完整解释。 新诊断：两种年龄列分别排序、用全部8360行或5993有效点作分母也没有复现38.42。

## 题面与判错记录
来源：[records/028_kramabench_packages/archeology-hard-2.md](../028_kramabench_packages/archeology-hard-2.md)，官方状态按029未通过不改。
```text
Across the years, what was the percent of years the wet-dry index was increasing? Give your answer in percentage, round your answer to 2 decimal places.
```
agent最终答案：
```text
50.25
```
参考答案：
```text
38.42
```
主要原因：无法判定；只能组合修复：否。
## 错误点：时间方向及年度抽样残差
- 角色：主要；类别：**无法判定**；把握：低。
按age升序得到50.25%；032以相同有效列反序49.75%，仍非38.42。子任务使用日历年且包含重复整数年，无法由目前的单改证据确定差异主项；不把反序一项冒充完整解释。 新诊断：两种年龄列分别排序、用全部8360行或5993有效点作分母也没有复现38.42。
- 是否说出：没有迹象；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
轨迹事件 `step.7.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Clarifying data calculations**

I need to clarify the years I'm working with and maybe take a sample interval of 0.5 ka. I’ll calculate the proportion across adjacent time samples where the wet-dry index is increasing. With 5994 values, that gives me 5993 intervals, and I want to find the percent of positive differences. When considering “percent of years,” I might need to sum the rising years versus total years based on annual data. I’ll make sure to include headers and count consecutive differences greater than zero.
```
轨迹事件 `step.7.code` 原文（代码行从本代码块1起计）：
```text
# numeric records, measure successive increases along age sequence
ages=pd.to_numeric(w.iloc[:,0],errors='coerce')
idx=pd.to_numeric(w.iloc[:,1],errors='coerce')
valid=pd.DataFrame({'age':ages,'index':idx}).dropna().sort_values('age')
delta=valid['index'].diff()
print(len(valid), int(delta.gt(0).sum()), int(delta.lt(0).sum()), int(delta.eq(0).sum()))
print(delta.gt(0).sum()/(len(valid)-1)*100)
```
证据：records/028_kramabench_packages/archeology-hard-2.md；records/032_kramabench_queries/05_archeology_hard_2.stdout.txt;records/034_checks/climate_diagnostic.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
读法一：按原样点计增加比例；读法二：按年度插值/聚合后计比例。方向可由年龄轴判断，但年度离散规则未规定；暂不强定主因。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
