# KramaBench / astronomy-hard-8（v3）

## 错在哪里
题面只要test RMSE，未给70/30、随机种子、有效标记及按小时聚合规则；agent比较seed和chrono，选80/20 seed42。隐藏子任务70/30不能确立agent义务。现有证据不足对每个预处理单独排名。 归因候选是已说出的选择，但还没有足以将多个独立选择逐个定因并排序的单改证据，正式主因留无法判定，不把整套方案捆成已验证错误点。 新诊断70/30时间顺序切分为[6.3294857e-7,5.1632430e-7]，仍非gold两个元素；不能只因数值接近就认已定主因。

## 题面与判错记录
来源：[records/028_kramabench_packages/astronomy-hard-8.md](../028_kramabench_packages/astronomy-hard-8.md)，官方状态按029未通过不改。
```text
Compare the predictive accuracy (using RMSE) of two single-variable linear regression models forecasting Swarm Alpha's along-track acceleration 3 hours ahead during May 11, 2024. Model 1 uses only OMNI Kp index as input; Model 2 uses only OMNI solar wind dynamic pressure (Pdyn) as input. Report both RMSE values on the test set in a list with format [number for Kp input, number for Pdyn input].
```
agent最终答案：
```text
[
    2.3827419950640467e-07,
    2.675054555311128e-07
  ]
```
参考答案：
```text
[
            6.1655e-07,
            5.1206e-07
        ]
```
主要原因：无法判定；只能组合修复：否。
## 错误点：未指定训练测试及预处理
- 角色：主要；类别：**无法判定**；把握：低。
题面只要test RMSE，未给70/30、随机种子、有效标记及按小时聚合规则；agent比较seed和chrono，选80/20 seed42。隐藏子任务70/30不能确立agent义务。现有证据不足对每个预处理单独排名。 归因候选是已说出的选择，但还没有足以将多个独立选择逐个定因并排序的单改证据，正式主因留无法判定，不把整套方案捆成已验证错误点。 新诊断70/30时间顺序切分为[6.3294857e-7,5.1632430e-7]，仍非gold两个元素；不能只因数值接近就认已定主因。
- 是否说出：针对本处的具体说明；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
轨迹事件 `step.9.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Computing scores and samples**

I’m working on retrieving scores from randomized splits of 21 samples. I need to compute different seeds chronologically while using the hourly mean. It's essential to provide the RMSE in a specific format without rounding. I’ll go ahead and return the numbers. It seems I might not need to apply a flag_val filter to ensure the data is clean. Okay, let’s test this out!
```
轨迹事件 `step.9.code` 原文（代码行从本代码块1起计）：
```text
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
sub=allx.dropna(subset=['y']).reset_index(drop=True)
for seed in [42,0,1,123]:
 tr,te=train_test_split(np.arange(len(sub)),test_size=.2,random_state=seed)
 scores=[]
 for col in ['kp','pdyn']:
  m=LinearRegression().fit(sub.loc[tr,[col]],sub.loc[tr,'y'])
  scores.append(mean_squared_error(sub.loc[te,'y'],m.predict(sub.loc[te,[col]]))**.5)
 print(seed,te, scores)
# chronological test last 20 percent
n=len(sub); tr=np.arange(int(n*.8)); te=np.arange(int(n*.8),n)
for col in ['kp','pdyn']:
 m=LinearRegression().fit(sub.loc[tr,[col]],sub.loc[tr,'y'])
 print('chrono',col,mean_squared_error(sub.loc[te,'y'],m.predict(sub.loc[te,[col]]))**.5)
```
证据：records/028_kramabench_packages/astronomy-hard-8.md；records/034_checks/astronomy-hard-8_split_candidates.json;records/034_checks/astronomy-hard-8_chrono70_retry.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
拆成多个Choice逐个单改或把建模方案视为一项？暂按方案列一项，低把握；不能从不同RMSE倒推出任一选项错误。 本次正式结论采用无法判定；候选机制不计入已定类别分布。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
