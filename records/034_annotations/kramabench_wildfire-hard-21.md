# KramaBench / wildfire-hard-21（v3）

## 错在哪里
ZHVI.csv为子任务明确依赖；递归本地data/kramabench/data未找到。依第3节先排不可评估，不继续把替代量或拒答作为判错原因。

## 题面与判错记录
来源：[records/028_kramabench_packages/wildfire-hard-21.md](../028_kramabench_packages/wildfire-hard-21.md)，官方状态按029未通过不改。
```text
Based on NOAA data, what are the top 3 states that lost the most residential property in value between 2005 and 2010 (including 2005 and 2010)? Answer in state full names and do not discard rows with missing values unecessarily.
```
agent最终答案：
```text
[
    "California",
    "Idaho",
    "Montana"
  ]
```
参考答案：
```text
[
            "California",
            "Washington",
            "Idaho"
        ]
```
主要原因：不可评估；只能组合修复：否。
## 错误点：参考必需文件缺失
- 角色：主要；类别：**不可评估**；把握：高。
ZHVI.csv为子任务明确依赖；递归本地data/kramabench/data未找到。依第3节先排不可评估，不继续把替代量或拒答作为判错原因。
- 是否说出：没有迹象；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
本处依据final_answer原文；无单独解释呈现选择的已确认事件，不用最终格式反推曾经说明过。
证据：records/028_kramabench_packages/wildfire-hard-21.md；records/034_checks/missing_files.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
未发现需改变手册定义的额外问题。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
