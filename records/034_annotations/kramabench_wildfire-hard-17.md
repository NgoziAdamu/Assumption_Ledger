# KramaBench / wildfire-hard-17（v3）

## 错在哪里
题面weather stations used for fire site monitoring，agent平均全部2965个registry记录，未按fire.station_verified_in_psa筛。以NWS ID匹配759行均值4830.8524，round1=4830.9；3317.37差1513.53→0。

## 题面与判错记录
来源：[records/028_kramabench_packages/wildfire-hard-17.md](../028_kramabench_packages/wildfire-hard-17.md)，官方状态按029未通过不改。
```text
What is the average elevation (in feet) of the weather stations used for fire site monitoring in the NOAA dataset?
```
agent最终答案：
```text
3317.37
```
参考答案：
```text
4830.9
```
主要原因：Intent Misreading；只能组合修复：否。
## 错误点：未限定实际火场监测站
- 角色：主要；类别：**Intent Misreading**；把握：中。
题面weather stations used for fire site monitoring，agent平均全部2965个registry记录，未按fire.station_verified_in_psa筛。以NWS ID匹配759行均值4830.8524，round1=4830.9；3317.37差1513.53→0。
- 是否说出：看到了但没提；证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.3.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Calculating average elevation**

I'm considering the user's request about the average elevation of weather stations used for fire site monitoring in the NOAA dataset. I'll need to calculate the mean elevation, likely removing any null values. First, I should inspect the dataset's shape, check for missing data, and gather some descriptive statistics, especially around station uniqueness and total rows. There’s also a BOM column that seems off, so I’ll load the data and clearly summarize the elevation details.
```
轨迹事件 `step.3.code` 原文（代码行从本代码块1起计）：
```text
p=os.path.join(base,'PublicView_RAWS_-3515561676727363726.csv')
raw=pd.read_csv(p,encoding='cp1252',low_memory=False)
print(raw.shape)
print([(repr(c),raw[c].dtype,raw[c].isna().sum()) for c in raw.columns[:12]])
elevcol=[c for c in raw.columns if 'Elevation' in c][0]
e= pd.to_numeric(raw[elevcol],errors='coerce')
print('elevation count',e.count(),'missing',e.isna().sum(),'mean',e.mean(),'median',e.median(),'minmax',e.min(),e.max())
print('duplicates station',raw['Station Name'].nunique(), 'rows',len(raw))
print(raw[elevcol].describe())
```
证据：records/028_kramabench_packages/wildfire-hard-17.md；records/034_checks/wildfire-hard-17_id_diagnostic.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
是数据对应事实还是要求范围？本项已知只要实际使用站即可，按Intent；哪个ID用于关联用新诊断确认，不据相似名称猜。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
