# KramaBench / archeology-easy-8（v3）

## 错在哪里
agent 55，gold 52；子任务4明确55。agent对分号分隔、空串过滤的结果与子任务一致。不能以最终52反推另有三处应合并。

## 题面与判错记录
来源：[records/028_kramabench_packages/archeology-easy-8.md](../028_kramabench_packages/archeology-easy-8.md)，官方状态按029未通过不改。
```text
How many unique sources were used in the Roman cities dataset?
```
agent最终答案：
```text
55
```
参考答案：
```text
52
```
主要原因：其他；只能组合修复：否。
## 错误点：最终参考值与子任务不一致
- 角色：主要；类别：**其他**；把握：中。
agent 55，gold 52；子任务4明确55。agent对分号分隔、空串过滤的结果与子任务一致。不能以最终52反推另有三处应合并。
- 是否说出：针对本处的具体说明；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
轨迹事件 `step.7.code` 原文（代码行从本代码块1起计）：
```text
unique_sources={s.strip().rstrip('.') for x in bib for s in x.split(';') if s.strip().rstrip('.')}
print(len(unique_sources))
final_answer(55)
```
证据：records/028_kramabench_packages/archeology-easy-8.md；subtask.4.answer。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
读法一：55是未清洗引用；读法二：最终参考值与子任务冲突。选二：子任务明确给55，未找到唯一支持52的清洗规则。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
