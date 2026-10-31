# KramaBench / environment-easy-3（v3）

## 错在哪里
题面问beaches且没有Boston Harbor限制；step7已经算全域268，step9改取名单8个海滩得到3。全域诊断复现268。

## 题面与判错记录
来源：[records/028_kramabench_packages/environment-easy-3.md](../028_kramabench_packages/environment-easy-3.md)，官方状态按029未通过不改。
```text
How many beaches had a higher bacterial exceedance rate for water samples collected in 2013 compared to 2012, excluding those with no samples in 2012?
```
agent最终答案：
```text
3
```
参考答案：
```text
268
```
主要原因：Intent Misreading；只能组合修复：否。
## 错误点：擅限Boston Harbor
- 角色：主要；类别：**Intent Misreading**；把握：高。
题面问beaches且没有Boston Harbor限制；step7已经算全域268，step9改取名单8个海滩得到3。全域诊断复现268。
- 是否说出：针对本处的具体说明；证据在场：是；曾经理解对过：是；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.7.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Computing beach data**

I need to figure out the bacterial exceedance rates by sampling each beach per year from pooled stations. I’m curious about how many Boston Harbor beaches have increased. I'll aggregate the data from the eight sampled beaches, excluding Castle Island. Boston lists nine beaches, but it seems Castle Island may lack data, combined with Pleasure Bay. It's unclear how playground samples relate to state data, so I'll work on computing the necessary information.
```
轨迹事件 `step.7.code` 原文（代码行从本代码块1起计）：
```text
# overall beach-year exceedance rates, identity community + Beach Name
all_d=pd.concat([d12.assign(year=2012),d13.assign(year=2013)])
g=all_d.groupby(['Community','Beach Name','year']).agg(n=('Violation','size'),exc=('Violation',lambda s:(s=='yes').sum()))
g['rate']=g.exc/g.n
wide=g['rate'].unstack()
print('identities with 2012',wide[2012].notna().sum(),'higher',((wide[2012].notna())&(wide[2013]>wide[2012])).sum())
# compare rates by beach name only
n=all_d.groupby(['Beach Name','year']).agg(n=('Violation','size'),exc=('Violation',lambda s:(s=='yes').sum())); n['rate']=n.exc/n.n
w=n.rate.unstack()
print('names with 2012',w[2012].notna().sum(),'higher',((w[2012].notna())&(w[2013]>w[2012])).sum())
```
轨迹事件 `step.7.feedback` 原文（代码行从本代码块1起计）：
```text
identities with 2012 1171 higher 268
names with 2012 1155 higher 267
```
证据：records/028_kramabench_packages/environment-easy-3.md；records/034_checks/environment-easy-3_all_beaches.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
未发现需改变手册定义的额外问题。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
