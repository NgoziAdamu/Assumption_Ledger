# KramaBench / archeology-hard-7（v3）

## 错在哪里
0.1 degrees未指定平面欧氏或球面角距；step3算274、step5球面292、最终选球面。单改阈值使用dist得到274，差18→0。

## 题面与判错记录
来源：[records/028_kramabench_packages/archeology-hard-7.md](../028_kramabench_packages/archeology-hard-7.md)，官方状态按029未通过不改。
```text
How many modern cities with a population of over 100k are within 0.1 degrees of ancient Roman-era cities?
```
agent最终答案：
```text
292
```
参考答案：
```text
274
```
主要原因：已说出的选择；只能组合修复：否。
## 错误点：距离度量
- 角色：主要；类别：**已说出的选择**；把握：中。
0.1 degrees未指定平面欧氏或球面角距；step3算274、step5球面292、最终选球面。单改阈值使用dist得到274，差18→0。
- 是否说出：针对本处的具体说明；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
轨迹事件 `step.5.code` 原文（代码行从本代码块1起计）：
```text
import numpy as np
lat1=np.radians(wcoords[:,0]); lon1=np.radians(wcoords[:,1])
lat2=np.radians(rcoords[:,0]); lon2=np.radians(rcoords[:,1])
mins=[]
for a,b in zip(lat1,lon1):
    hav=np.sin((a-lat2)/2)**2 + np.cos(a)*np.cos(lat2)*np.sin((b-lon2)/2)**2
    mins.append(2*np.arcsin(np.sqrt(np.clip(hav,0,1))).min()*180/np.pi)
mins=np.array(mins)
print('great circle angular <=.1', (mins<=.1).sum())
print('box',((abs(wcoords[:,0]-rcoords[ix,0])<=.1)&(abs(wcoords[:,1]-rcoords[ix,1])<=.1)).sum())
print('differences euclid-vs-great-circle', ((dist<=.1)!=(mins<=.1)).sum())
```
证据：records/028_kramabench_packages/archeology-hard-7.md；records/034_checks/archeology-hard-7_euclidean.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
是否代码里明确标明great circle就算具体说明？选是：这里实际并列计算了两个度量并标明名称，不是普通无说明操作。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
