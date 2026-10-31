# KramaBench / wildfire-hard-14（v3）

## 错在哪里
agent先按州加总分子分母，gold按县比例等权平均；题面未规定县权重。032县平均0.64688076→0.65，agent0.64，差0.01→0。

## 题面与判错记录
来源：[records/028_kramabench_packages/wildfire-hard-14.md](../028_kramabench_packages/wildfire-hard-14.md)，官方状态按029未通过不改。
```text
What is the correlation between the proportion of generally unsafe air quality days according to the EPA and the amount of land affected by fires in 2024? Round to 2 decimal places.
```
agent最终答案：
```text
0.64
```
参考答案：
```text
0.65
```
主要原因：Unstated Choice；只能组合修复：否。
## 错误点：州比例加权口径
- 角色：主要；类别：**Unstated Choice**；把握：中。
agent先按州加总分子分母，gold按县比例等权平均；题面未规定县权重。032县平均0.64688076→0.65，agent0.64，差0.01→0。
- 是否说出：没有迹象；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
轨迹事件 `step.4.code` 原文（代码行从本代码块1起计）：
```text
unsafe_cols=['Unhealthy Days','Very Unhealthy Days','Hazardous Days']
agg=aq.groupby('State')[['Days with AQI']+unsafe_cols+['Unhealthy for Sensitive Groups Days']].sum()
agg['prop_u150']=agg[unsafe_cols].sum(axis=1)/agg['Days with AQI']
agg['prop_gt100']=(agg[unsafe_cols+['Unhealthy for Sensitive Groups Days']].sum(axis=1))/agg['Days with AQI']
d=acres.merge(agg,left_on='State',right_index=True).dropna(subset=['Total Acres Burned'])
print('n',len(d),'states',d.State.tolist())
print('only >150', d['prop_u150'].corr(d['Total Acres Burned']))
print('>100', d['prop_gt100'].corr(d['Total Acres Burned']))
print('rows', d[['State','prop_u150','prop_gt100','Total Acres Burned']].sort_values('prop_u150',ascending=False).head(10).to_string(index=False))
```
证据：records/028_kramabench_packages/wildfire-hard-14.md；records/032_kramabench_queries/09_wildfire_hard_14.stdout.txt。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
汇总比例或县比例均值？两者统计对象不同但题面没定，Choice；不因数值接近就认gold口径必然。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
