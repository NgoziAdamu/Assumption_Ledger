# KramaBench / archeology-hard-12（v3）

## 错在哪里
agent明确报告449个起始年范围内冲突及447个全段在范围内的备选；gold409来自隐藏子任务对同演员重叠年份去重。题面没有给重叠合并和演员归并算法。未重建全部409的合并过程，主因把握低。 归因候选是已说出的选择，但还没有足以将多个独立选择逐个定因并排序的单改证据，正式主因留无法判定，不把整套方案捆成已验证错误点。 新诊断按原Conflict名称合并重叠时段449→446，仍不是409；演员规范化规则未复现。

## 题面与判错记录
来源：[records/028_kramabench_packages/archeology-hard-12.md](../028_kramabench_packages/archeology-hard-12.md)，官方状态按029未通过不改。
```text
Count the number of human conflicts between 800 and 1400 AD, and attribute them as best you can to modern countries. Define a conflict as between two actors that lasts at least a year.
```
agent最终答案：
```text
Using conflict_brecke.csv, I count 449 conflicts starting from 800 through 1400 (the file has no entries before 900) with EndYear - StartYear >= 1. Two of these continue past 1400; requiring the whole conflict to end by 1400 gives 447. Country counts below use the 449 start-year definition and count a conflict for each modern country attributed to an actor, so they overlap and do not sum to 449. Attribution is approximate: historical actors are mapped to successor/current territories; Byzantium is credited to both Greece and Turkey, and generic actors are assigned by their named location where possible.

Modern-country conflict involvements: United Kingdom: 86; Italy: 82; France: 78; Germany: 75; Turkey: 56; Russia: 53; Greece: 50; Spain: 49; Austria: 33; Poland: 21; Denmark: 19; Hungary: 18; Netherlands: 18; Lithuania: 18; Bulgaria: 14; Ukraine: 12; Sweden: 9; Czechia: 7; Norway: 7; Ireland: 6; Vatican City: 6; Morocco: 5; Belgium: 4; Portugal: 3; Switzerland: 3; Serbia: 2; Estonia: 2; Mongolia: 2; Finland: 1.
```
参考答案：
```text
409
```
主要原因：无法判定；只能组合修复：否。
## 错误点：冲突合并和时间边界
- 角色：主要；类别：**无法判定**；把握：低。
agent明确报告449个起始年范围内冲突及447个全段在范围内的备选；gold409来自隐藏子任务对同演员重叠年份去重。题面没有给重叠合并和演员归并算法。未重建全部409的合并过程，主因把握低。 归因候选是已说出的选择，但还没有足以将多个独立选择逐个定因并排序的单改证据，正式主因留无法判定，不把整套方案捆成已验证错误点。 新诊断按原Conflict名称合并重叠时段449→446，仍不是409；演员规范化规则未复现。
- 是否说出：针对本处的具体说明；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
轨迹事件 `step.11.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Evaluating regex issues**

I realized that I need to consider Czechia in my counts! I have to check why the alias regex was created before I updated the aliases, which could mean the alias patterns are outdated. It’s essential to regenerate the patterns after any changes. There's also an issue where the aliases based on regex could match substrings, like matching "Germany" within other entries. So, I'll need to regenerate those patterns correctly.
```
轨迹事件 `step.11.code` 原文（代码行从本代码块1起计）：
```text
alias_patterns=[(re.compile(r'(?<![a-z])'+re.escape(k).replace(r'\ ',r'\s+')+r'(?![a-z])',re.I),v,k) for k,v in sorted(aliases.items(),key=lambda kv:-len(kv[0]))]
long['Countries']=long.Conflict.map(attrib)
for ix,row in long.iterrows():
    n=row.Conflict
    if n.startswith('Celts-Vikings'): long.at[ix,'Countries']={'Ireland'}
    elif n.startswith('Christians-Muslims'): long.at[ix,'Countries']={'Turkey'}
    elif n.startswith('[Crusaders (Fourth) Venice]'): long.at[ix,'Countries']={'Italy','Hungary','Turkey','Greece'}
cc=Counter(c for cs in long.Countries for c in cs)
print(cc.most_common())
print('unassigned',long[long.Countries.map(len).eq(0)].Conflict.tolist())
```
证据：records/028_kramabench_packages/archeology-hard-12.md；subtask.3.query;subtask.5.query;subtask.6.answer;records/034_checks/conflict_diagnostic.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
读法一：原记录是冲突；读法二：演员同且年份重叠必须并为一个。选Choice，材料不能唯一确定归并与现代国家映射。 本次正式结论采用无法判定；候选机制不计入已定类别分布。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
