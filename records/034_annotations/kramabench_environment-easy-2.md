# KramaBench / environment-easy-2（v3）

## 错在哪里
输出内容可经仅移除说明/多余字段恢复gold；新做输出级诊断相等，未重算业务数值。题面没有明确要求裸值或禁止解释。

## 题面与判错记录
来源：[records/028_kramabench_packages/environment-easy-2.md](../028_kramabench_packages/environment-easy-2.md)，官方状态按029未通过不改。
```text
Between 2002 and 2023 (inclusive), which years had a bacterial exceedance rate in water samples collected from freshwater beaches higher than the average freshwater beach exceedance rate (to 2 decimal places)?
```
agent最终答案：
```text
Average annual freshwater-beach exceedance rate: 4.04%. Years above average: 2003 (5.26%), 2011 (5.73%), 2015 (4.19%), 2018 (4.91%), 2020 (5.56%), 2021 (6.64%), 2022 (4.66%), and 2023 (5.57%).
```
参考答案：
```text
[
            2003,
            2011,
            2015,
            2018,
            2020,
            2021,
            2022,
            2023
        ]
```
主要原因：其他；只能组合修复：否。
## 错误点：答案附带说明或额外字段
- 角色：主要；类别：**其他**；把握：高。
输出内容可经仅移除说明/多余字段恢复gold；新做输出级诊断相等，未重算业务数值。题面没有明确要求裸值或禁止解释。
- 是否说出：没有迹象；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：是。
本处依据final_answer原文；无单独解释呈现选择的已确认事件，不用最终格式反推曾经说明过。
证据：records/028_kramabench_packages/environment-easy-2.md；records/030_kramabench_tolerance_details.json;records/034_checks/form_checks.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
读法一：问which/how many就隐含只交裸值；读法二：不等于明确格式规定。依v3选二，系统通用Python值要求只另记。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
