import json,csv,collections
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'records/036_checks';s=json.loads((O/'summary.json').read_text());a=json.loads((O/'disclosure_audit.json').read_text())
classes=['Data Misconception','Intent Misreading','Unstated Choice','Quiet Downgrade','Form Mismatch','已说出的选择','已说出的降级','代码写错','其他','不可评估','无法判定','多因并列','未交卷']
table='| 主要原因 | DAComp 034 | DAComp 036 | KramaBench 034 | KramaBench 036 |\n|---|---:|---:|---:|---:|\n'
for cat in classes:table+='| '+cat+' | '+' | '.join(str(s['objects'][b][v].get(cat,0)) for b in ['DAComp','KramaBench'] for v in ['034','036'])+' |\n'
table+='| 合计 | 30 | 30 | 42 | 42 |'
grades=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象'];gt='| 档位 | DAComp | KramaBench | 合计 |\n|---|---:|---:|---:|\n'
for n,g in enumerate(grades,1):
 d=s['grades']['DAComp'].get(str(n),0);k=s['grades']['KramaBench'].get(str(n),0);gt+=f'| {n}. {g} | {d} | {k} | {d+k} |\n'
gt+='| 合计 | 80 | 43 | 123 |'
report=f'''# 036：按 v3.1 修订试点

## 任务

开始时 notes/、records/ 均无036编号，本次沿用036。仅修订034的72个对象：DAComp 30张表，KramaBench 41道失败题加 astronomy-hard-11 未交卷。未打开033盲标禁读材料；archeology-hard-5保留034，待人工复核。

Windows 下载目录的手册已按字节复制到 [docs/标注手册_v3.1.md](../docs/标注手册_v3.1.md)，通读全文并以其第12节四条修订为准。SHA-256：`5d15b996fdc4b0f8eea08f4bcff9a9fcee28d502890ea6d384a2b542fc6abc53`。源、目标逐字节相同；v3未改。本次固定该原文为交付使用的v3.1版本，没有自行增补规则。见[复制记录](../records/036_checks/manual_provenance.json)。

## 结论

已完成72个对象、123个错误点的五档复核，交付完整新CSV与32份有实质修订的对象说明；其余40份未复制。三道无法判定按同类候选规则补完，archeology-hard-2补做单改后仍无法判定。KramaBench原来从中间步骤认定“已说出”的四题已改回Unstated Choice或Quiet Downgrade。

astronomy-easy-6改为估计器是主要原因、符号是参与因素，取消“只能组合修复”。DAComp的对象主要原因分布不变；impl-020的一个非原因点因最终确有说明改为已说出的选择。所有原有基础类别仅在本任务指定规则影响处调整。

## 详细发现

### 交付及变更口径

- [036_objects.csv](../records/036_objects.csv)：72个对象完整版本。
- [036_points.csv](../records/036_points.csv)：123个错误点完整版本，列名为“是否说出（五档）”。
- [036_annotations/](../records/036_annotations/)：32份修订说明，每份列出相对034改变的类别、档位、原因和证据。
- [disclosure_audit.json](../records/036_checks/disclosure_audit.json)：全部123点逐点复核，包括未改对象；第1、2档均有交付物原句，第3档均有中间事件编号和原句。CSV中证据来源指向此文件，可用对象编号＋错误点名称定位。

“相对034”只统计分类、角色和档位的实质变化；旧四档到五档的等义名称替换、增加复核来源不算实质变化。“补完无法判定”表示完成指定的无法判定复核，含仍保留无法判定的archeology-hard-2，不表示四道均已定类。优先级为补完无法判定＞改类别＞只改档位＞未改。DAComp为25未改、4只改档位、1改类别；KramaBench为15未改、19只改档位、4改类别、4补完无法判定。

### 主要原因分布（对象数）

{table}

KramaBench“已说出的选择”从3到2不是单纯少一题：原3题archeology-hard-7、astronomy-easy-6、legal-hard-17均改为Unstated Choice，新补完的archeology-hard-12、wildfire-hard-18为已说出的选择。astronomy-hard-12从已说出的降级改Quiet Downgrade；astronomy-hard-8从无法判定改Unstated Choice。分类不改变029官方通过/失败状态。

### 五档分布（错误点数）

{gt}

第3档中，DAComp有 **2个Unstated Choice、0个Quiet Downgrade**；KramaBench有 **5个Unstated Choice、1个Quiet Downgrade**。前者为impl-007两项字段映射；后者为archeology-hard-7、astronomy-easy-6两项、astronomy-hard-8、legal-hard-17，以及astronomy-hard-12。计数含主要、并列、参与和非原因，不能直接当成对象分布。

第8节主口径只有第1档算“已说出”：DAComp 6点、KramaBench 4点（不限类别）；其中Choice/Downgrade对应的已说出点分别为DAComp 3/0、KramaBench 2/0。DAComp第三个已说出的选择是impl-020的非原因点，故对象主因只有2张。

另报第1、2档均算说出的口径：DAComp 44点、KramaBench 4点；只看Choice/Downgrade族则为DAComp 17个选择＋4个降级，KramaBench 2个选择＋0个降级。该口径仅统计，不改主CSV类别。

### 交付物核对

已核对30个implementation的最终报告/finish事件、所选30张表SQL，并扫描交付SQL目录全部1069份SQL及其中Python代码的注释。27份报告文件留存，29个implementation有finish事件；impl-002、018虽未在项目报告路径找到文件，finish分别59、99保存了完整最终报告，可算交付。impl-007事件65/67尝试写报告，66/68均失败，且无finish，故草稿不是交付物。

所选30份SQL无注释。其他SQL只有impl-030的line_item付款方式注释，与本批invoice错误点无关；impl-012附带测试脚本注释谈email_template脏数据，与lead名字空白无关。`.tmp/`生成脚本视为中间代码，理由是最终报告交付的是SQL目录，不是这些临时生成工具。来源与hash见[交付清单](../records/036_checks/deliverable_inventory.json)、[最终报告留存](../records/036_checks/delivery_sources.json)。

具体变化包括：impl-007由报告草稿认出的字段映射问题改第3档；impl-018事件57的外键注释在中间代码，改第3档；impl-020最终报告明确写出subject回退与错位conversation_id时间来源，相应点改第1档；impl-030通用类型说明覆盖原未定位的五个类型表示点，改第2档。其余非本次规则影响的类别保持034。

“看到了相关信息”与“证据在场”仍分开。environment-hard-18的大小写点从没有迹象改第4档，因为step5显示分年结果及2021为0；但足以证明大小写差异的原值输出被截断，证据在场仍否。所有证据在场、曾经理解对过、系统提示是否适用字段均保持034，不用本次完整读取补填agent当时没看到的内容。

### 四道无法判定

| 对象 | 036结果 | 依据与限制 |
|---|---|---|
| archeology-hard-12 | 已说出的选择，低 | 起止边界、冲突合并及现代国家归属均沿用034的Choice候选；最终说出449/447和归属重叠。原诊断同名合并449→446，不宣称已复现409。 |
| astronomy-hard-8 | Unstated Choice，低 | 切分比例/方式、seed、聚合、有效标记均属未定分析约定；只有中间讨论，最终仅两个RMSE。不要求先排出同类候选主次。 |
| wildfire-hard-18 | 已说出的选择，低 | 控制集、变换、75%分界及响应量组合为同类Choice候选；最终逐项披露。未复现隐藏模型，未逐项排序。 |
| archeology-hard-2 | 无法判定，低 | 三个独立单改均运行到step8最终答案；方向有收益，但年度/缺失处理链仍未识别，不能完整排序异类候选。 |

archeology-hard-2新单改：

| 版本 | 最终百分数 | 与38.42的差距 | 相对基线减少 |
|---|---:|---:|---:|
| 原链基线 | 50.25 | 11.83 | 0 |
| 只反转年龄顺序 | 49.75 | 11.33 | 0.50 |
| 只在原年龄轴上逐年度线性插值 | 50.25 | 11.83 | 0 |
| 只按整年合并同年观测 | 50.25 | 11.83 | 0 |

新诊断进一步核实：隐藏子任务的7507个日历年与第一Age_ky列先round再乘1000的前7507项全同，并非湿干指数自带的Age_ky.3；增长标记却有8360项，均值38.421%，有效湿干观测为5993项。12种轴/量化/顺序诊断仍未分离参考链的缺失行、并列年份处理。方向修正是已确认减差因素，但另一异类候选的“修复”还不可定义，故保留无法判定；没有以“减差未过半”或“仍有残差”作为门槛。见[重跑汇总](../records/036_checks/rerun_summary.json)、[年度链诊断](../records/036_checks/archeology-hard-2_annual_diagnostic.json)。

### 数值列表及单改终点

本批最终答案为纯数值列表的只有三题。astronomy-easy-6沿原step3重新计算，把step4常量当计算结果引用，保留原round6：

| 版本 | 最终答案 | 新规模 | 减少量 |
|---|---|---:|---:|
| 原链 | [-0.006853, -0.054269] | 0.078422 | 0 |
| 只改估计器 | [-0.019278, 0.001966] | 0.042544 | 0.035878 |
| 只改符号 | [0.006853, 0.054269] | 0.068716 | 0.009706 |
| 两者都改 | [0.019278, -0.001966] | 0.000056 | 0.078366 |

因此估计器主要、符号参与，不是只能组合修复。034把端点诊断同时round4，与单改其余不动的要求不符；036不再把组合结果称完全等于gold。

astronomy-hard-8规模从元素是否相同改为数值差：基线`6.2283034496e-7`，034时间70/30候选为`2.0662873241e-8`。**口径变化不影响结论**：同类候选可直接定Choice；该候选同时涉及切分方式/比例，不能据距离近强排单项。wildfire-hard-16基线`0.0001763338729167`，仅输出round3后为0；**口径变化不影响结论**，仍是题面未规定精度的“其他”。混合名称/计数的legal-hard-14不作为纯数值列表。

[终点核查](../records/036_checks/endpoint_audit.json)逐一审查13组034计算/诊断，包括常量答案题。archeology-hard-1、environment-easy-3、environment-hard-16、legal-hard-18等的最终值能追溯到重算结果，类别保持；纯输出形式变换按手册豁免重算。另有两处需明确：

- wildfire-hard-17原最终表达式保留两位小数，应为4830.85，差0.05；034用一位小数称完全对齐不成立。该筛选仍减差1513.48，Intent主因不变；数值更正在终点记录中，不复制一份分类字段未改的对象标注。
- environment-hard-18由重算后的年度趋势解释最终布尔值，分别False/False/False/True，保留组合修复结论；原轨迹没有显式布尔比较代码，沿用逐年方向相同的解释，限制列为规则问题。

### 新的规则问题

1. **impl-007、impl-018：中间的组级意识够不够第3档？** 读法一要求明确点名每个错误字段，则007报告草稿及018通用外键注释只能算相关信息；读法二允许同组共享前提的明确意识覆盖该组错误点。采用二：007点名Apple订阅summary/event的来源语义不一致，018明确“外键不能取行自身id”，与被标两点是同一前提；但没有声称识别了每张表的具体失误。该边界影响第3档计数，不影响基础类别。
2. **archeology-hard-12：同类候选组内披露程度不完全一致。** 读法一应先拆成单独的时间边界、冲突合并、国家归属，再分别判断；读法二保留034候选组，用最终针对该组的449/447及重叠归属说明记第1档。采用二以遵守本次不重做基础标注、同类候选可直接定类的范围；没有把“国家归属重叠”误称成明确说明了“同演员冲突去重”。组内单独披露和贡献尚未排序。
3. **environment-hard-18：定性常量没有唯一可执行引用。** 读法一只有能指向明确原表达式才可确认布尔终点；读法二允许按题面“same trend”及中间年度序列还原逐年方向判断。沿用二，保留034结论，并把这类诊断与原源码单改区分。原最终False可由序列解释，但无法证明agent采用了唯一的逐年方向比较算法。

上述边界按当前读法完成标注，未自行修改已复制的手册。交付物范围另明确为最终报告/SQL及交付代码注释；临时生成脚本不因仍留在工作目录就升为交付说明。

## 证据来源

原有证据复用034逐点标注/CSV、018轨迹审计、014/016/017事件留存、028原文材料包、032核实查询，以及034成功的计算诊断；未重新执行019～025数据库实验。所有旧证据路径保留在完整points CSV中。

本次新增是交付物/事件复核、两个对象的计算重跑（各含基线和3个变体）、archeology-hard-2的12种诊断组合，以及数值列表/终点重算。按对象计，基础数值证据复用70/72（约97%），新增完整计算链重跑2/72（约3%）；这不表示其余70个没有新做档位复核，全部123点都重新核对了交付口径。没有查写数据库、调用agent、下载数据或重跑其他批次。

执行命令（仓库根目录）：

```bash
cmp /mnt/c/Users/jucc116/Downloads/标注手册_v3.1.md docs/标注手册_v3.1.md
sha256sum /mnt/c/Users/jucc116/Downloads/标注手册_v3.1.md docs/标注手册_v3.1.md
PYTHONDONTWRITEBYTECODE=1 /home/katherine/dac/.venv/bin/python records/036_checks/reruns.py
PYTHONDONTWRITEBYTECODE=1 /home/katherine/dac/.venv/bin/python records/036_checks/annual_diagnostic.py
PYTHONDONTWRITEBYTECODE=1 python3 records/036_checks/build.py
PYTHONDONTWRITEBYTECODE=1 python3 records/036_checks/endpoint_audit.py
PYTHONDONTWRITEBYTECODE=1 python3 records/036_checks/deliverable_inventory.py
PYTHONDONTWRITEBYTECODE=1 python3 records/036_checks/validate.py
```

[验证记录](../records/036_checks/validation.json)：72/123对象及点键一致，32份改动对象说明对应CSV，五档取值与已说出类别一致，引句逐一回查原文成功；018～025、034记录及v3手册共1286个文件hash未变，git无原有跟踪文件改动。重跑输入文件仅记录[hash](../records/036_checks/rerun_input_hashes.json)，未提交原始数据。手册复制记录、脚本、日志和全部查询诊断均在records/036_checks/。

## 不确定或没查到的

- archeology-hard-2的隐藏年度/空行链仍未识别；三个同类候选组也没有逐项主次证据，均低把握。
- astronomy-hard-12缺mock场值，wildfire-hard-19缺所需2016日雨量，wildfire-hard-21缺房价文件；本任务复用034缺失核查和已有轨迹，未伪造文件来重跑。astronomy-hard-11仅保留未交卷。未新增失败的完整计算重跑。
- archeology-hard-5依指令未重新判类。environment-hard-18的布尔还原、组级意识/披露边界见规则问题；这些不确定性没有通过改手册消除。

## 建议的下一步

按已保存的v3.1原文用于其余批次；对上述边界保留可审计的对象备注。人工复核archeology-hard-5，并由用户/Claude决定是否继续追查archeology-hard-2；盲标对比仍由Claude完成，本次不读取033做对比。
'''
(R/'notes/036_2026-10-31_按v3.1修订试点.md').write_text(report)
