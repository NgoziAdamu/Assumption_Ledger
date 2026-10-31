# KramaBench / astronomy-hard-12（v3）

## 错在哪里
npz提供坐标网格和其他场，未提供所要求的势能值；agent没有现成势能场，却定义地表零点的GM(1/R-1/r)替代并提交。step8/13 reasoning具体说明无values file需自行生成。032的g(R+h)诊断也不完全匹配gold，不能把它当规范。

## 题面与判错记录
来源：[records/028_kramabench_packages/astronomy-hard-12.md](../028_kramabench_packages/astronomy-hard-12.md)，官方状态按029未通过不改。
```text
Estimate the mean geopotential energy per unit mass (in J/kg) experienced by Swarm-A from September 2 to 29, 2019 using precise orbital data. Use SP3 files to determine the satellite's geodetic position, and interpolate a mock geopotential field defined over latitude, longitude, and altitude to compute the potential energy at each timepoint. Average the results to compute the mean energy. Use earth radius 6371.0 km, and g = 9.80665 m/s^2. Answer round to 2 decimal places.
```
agent最终答案：
```text
4092167.75
```
参考答案：
```text
66822738.84
```
主要原因：已说出的降级；只能组合修复：否。
## 错误点：自造mock势能场
- 角色：主要；类别：**已说出的降级**；把握：低。
npz提供坐标网格和其他场，未提供所要求的势能值；agent没有现成势能场，却定义地表零点的GM(1/R-1/r)替代并提交。step8/13 reasoning具体说明无values file需自行生成。032的g(R+h)诊断也不完全匹配gold，不能把它当规范。
- 是否说出：针对本处的具体说明；证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
轨迹事件 `step.8.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Calculating geodetic conversion**

I need to perform a geodetic conversion to WGS84 and switch coordinates from kilometers to meters. The field should have a maximum altitude of 500, while the swarm altitude is approximately 450. I’m considering using the standard geopotential formula on the grid, possibly applying interpolation as well. Since there’s no values file provided, I'd be defining a mock field based on potential energy calculations, focusing on the gravity potential with latitude variation.**Evaluating geophysical calculations**

I’m looking into the spherical geopotential equation, U = g * R * h / (R + h), which gives potential energy per mass related to Earth's surface. I could interpolate that on the altitude grid since latitude and longitude dimensions are constant. The gravitational potential formula might work, but I need to evaluate approximate outputs. Altitude is around 460 km, but expected values aren't matching. I’ll also need to parse data for dates and sample counts, confirming everything with the WGS84 standard and setting field array values for interpolation.**Parsing altitude field data**

I’m working with a field altitude grid that ranges from 100 to 500 km, and I’ll interpolate values for each position. The SP3 documentation provides positions in kilometers based on an Earth-centered, Earth-fixed system. I need to filter the dataset for dates inclusive from September 2 to September 29, ensuring I capture all records from September 3 midnight in the corresponding file. With 10-second records, I expect to see around 8641 points daily, requiring careful parsing to avoid any gaps in the data.
```
轨迹事件 `step.8.code` 原文（代码行从本代码块1起计）：
```text
import datetime as dt, re, pandas as pd, numpy as np
for ff in sorted(spfiles):
 if '201909' in ff: print(os.path.basename(ff))
```
证据：records/028_kramabench_packages/astronomy-hard-12.md；records/032_kramabench_queries/03_astronomy_hard_12.stdout.txt。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。
## 本处规则问题
读法一：题目mock允许自己定义，归Choice；读法二：要求输入场不存在而自造替代，归Downgrade。依v3“要求的输入不存在”选二；若预期要生成场，应修订题面依据而非凭gold反推。
## 重放边界
本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。
