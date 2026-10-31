"""Render only mechanical comparison results; no interpretation of failures."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'records'
records=json.loads((R/'030_kramabench_tolerance_details.json').read_bytes())
s=json.loads((R/'030_kramabench_tolerance_summary.json').read_bytes())
v=json.loads((R/'030_kramabench_validation.json').read_bytes())
assert v['passed']

def cell(value):
    return str(value).replace('&','&amp;').replace('|','&#124;').replace('<','&lt;').replace('>','&gt;').replace('\n','<br>')

def witness(r):
    c=r['matched_using']
    if c is None:return '—'
    if c['operation']=='extract_number':return f"数字 `{c['token']}` → `{c['value']}`"
    if c['operation']=='prefix_before_delimiter':return '分隔符 `'+c['delimiter']+'` 前原文：`'+c['original_core']+'`'
    return '`'+json.dumps(c['value'],ensure_ascii=False)+'`'

report='''# KramaBench 宽松比对

日期：2026-10-31。

## 任务

以 `records/029_kramabench_final_scores.csv` 中 41 道未通过、1 道未交卷题为名单，使用原 meta.final_answer 与 workload.answer 逐档宽松比对。仅记录候选值、函数返回值及题面原句；不分析错因、不作错因归类、不重跑 agent、不补裁判、不改已有评分或文件。

## 结论

**已核实**：42 题中，39 题适用宽松比对，2 道 `string_approximate` 标“不适用”，1 道未交卷题标“无答案”。39 道适用题中，首次在**第 1 档对上 1 题、第 2 档对上 8 题、第 3 档对上 1 题**，共 10 题；其余 **29 题在各适用档均未对上**。

所有比对使用官方复制件中的原 `Success`、`F1` 定义，`Success=1` 或 `F1=1.0` 才记录为“对上”。已核对 210 条指标调用记录和 37 条题面原文摘录；**模型调用为 0，来源文件 SHA-256 未变**。本次表格是按指定放宽条件产生的比对记录，不写回 029 的官方最终状态。

## 详细发现

### 交付文件

- [030_kramabench_tolerance.csv](../records/030_kramabench_tolerance.csv)：42 题，包含答案原文、原值类型、各档状态、首次对上的档、实际使用值及题面原句。
- [030_kramabench_tolerance_details.json](../records/030_kramabench_tolerance_details.json)：逐题原输入、029 原行、每档全部候选及返回值、抽取数字的位置、取整前后值、题面句子起止位置。
- [030_kramabench_metric_calls.json](../records/030_kramabench_metric_calls.json)：每次 `Success/F1` 的实际输入和完整返回 tuple，按调用顺序保存；逐题详细记录通过 event 下标引用。
- [030_kramabench_tolerance_summary.json](../records/030_kramabench_tolerance_summary.json)：机械计数、名单、官方定义来源位置及输入 hash。
- [调用脚本](../records/030_kramabench_tolerance.py)、[检查脚本](../records/030_check_kramabench_tolerance.py)、[检查结果](../records/030_kramabench_validation.json)。

按本次要求，在 CSV/详细记录中保存这 42 题的答案摘录；数据湖与完整 workload 原件仍不入 Git。

### 比对口径

**第 0 档**：照抄 029 的最终状态、最终分数和分数出处，没有重新运行官方评测。42 题的该档分数均为 0；未交卷题仍保留 029 的“未交卷”原状态，后续档和首次对上字段另标“无答案”。

**第 1 档：统一类型。** 对两边字符串去首尾空白、转小写；`"true"/"false"` 转为 bool；完整的数字字符串转为 int/float（支持符号、小数、科学计数法）。列表递归处理各项。单值使用 `Success`，列表使用 `F1`。不去内部空格、连字符或普通标点，不改写专名，不自行换算单位。

对于列表类型中实际为字符串的答案，先用 `json.loads`、`ast.literal_eval` 尝试读取列表/元组；若不是列表/元组，按官方 F1 的后备规则用逗号拆分并去空项。本次所有 F1 调用均传入两个 list，因此官方源码中的 `eval()` 分支不会执行；没有执行答案里的文字或代码。此步骤只准备官方 F1 的列表输入，不额外从列表叙述文本提取所有数字。

**第 2 档：抽取核心内容。**

- 数值题：从原答案的文本表示中删除千分位逗号、`$`、`%`，逐个抽取所有带可选符号、小数和科学计数法的数字。按文本出现顺序逐个用 `Success` 与标准值比；任何一个返回 1 即记录对上，首次返回 1 的候选作为该档使用值。保留全部候选和返回值，不判断某个数是否真正代表最终答案。删除 `%` 不表示除以 100。
- `string_exact`：保留第 1 档值，并按用户给定顺序 `" — "`、`" ("`、`":"` **分别独立**生成“第一次出现该分隔符之前”的前缀候选；不是连续应用三个截断。候选再做第 1 档归一化，用 `Success` 比对。CSV 同时记录“标准答案是否原样出现在答案文本里”：只做区分大小写的原字符串 substring 检查；这个布尔记录**不作为对上条件**。原值不是两个字符串时该项标“不适用”。
- 列表：只有当答案每一项都是非空列表/元组时，才统一取第一元素；然后去掉每个字符串项末尾完整的括号后缀（包含可嵌套括号，若有多个末尾括号段则逐个去除），再做第 1 档归一化；标准列表保持第 1 档值，使用 `F1`。不去掉非末尾括号或其他标点。

**第 3 档：取整。** 数值题对第 2 档的所有数字候选，按标准答案在 workload 原 JSON 中的十进制小数位数使用 `Decimal + ROUND_HALF_UP` 四舍五入，然后仍用 `Success`。小数位数从原 JSON 数字 token 经 Decimal 获得，保留尾部零；科学计数法按展开后的小数位数计算，例如 `6.1655e-7` 为 11 位。整数标准值按 0 位处理，不依据题面将其额外解释成“最近千位”等其他规则。

列表题从第 2 档列表出发，按相同索引位置的标准数值的小数位数处理数值项，再整体调用 `F1`；标准对应项不是数值或不存在时，该项保持不变。`string_exact` 和没有可对齐数值项的列表不适用第 3 档。原题面的 round/nearest 等语句只摘录，不用它们另外改变这一档的规则。

**各档是否继续计算**：即使前档已对上，仍计算后续适用档，以填满逐档状态；“第一次对上的档”取最小档号。各档的全部对上数会重复，不能相加当作题数。没有改动官方 `Success` 自带的容差或 `F1` 自带的数值匹配规则；列表最终是否对上仍以整体 F1 恰好为 1 为准。

### 各档计数

| 档位 | 本档对上题数（可重复） | 首次在本档对上 | 截至本档至少对上一次 |
| --- | ---: | ---: | ---: |
| 第 0 档（029 原记录） | 0 | 0 | 0 |
| 第 1 档 | 1 | 1 | 1 |
| 第 2 档 | 9 | 8 | 9 |
| 第 3 档 | 4 | 1 | 10 |

第 3 档本档对上 4 题中，3 题已经在第 2 档对上；部分字符串/非数值列表只在前档适用，不能要求第 3 档的“本档对上数”大于前档。

### 逐题结果

“—”表示该列没有对上时使用值。各适用档均未对上不包括两道不适用题和一道无答案题。第 0 档列照抄 029 状态（各题该档分数均为 0）。

| 题号 | 答案类型 | 第 0 档 | 第 1 档 | 第 2 档 | 第 3 档 | 第一次对上 | 对上时实际使用值 |
| --- | --- | --- | --- | --- | --- | --- | --- |
'''
for r in records:
    first=str(r['first_match']) if not isinstance(r['first_match'],int) else f"第 {r['first_match']} 档"
    values=[r['task_id'],r['answer_type'],r['official_029_row']['最终状态'],
            *[r['stages'][str(i)]['status'] for i in [1,2,3]],first,witness(r)]
    report+='| '+' | '.join(cell(x) for x in values)+' |\n'
report+='''
### 各适用档均未对上的清单

以下 29 题的本次所有适用档均未对上；这里只列题号，不解释原因：

'''
report+='\n'.join('- `'+x+'`' for x in s['unmatched_eligible_tasks'])+'\n'
report+='''
未参与宽松比对的另列：`environment-hard-18`、`wildfire-hard-18` 为 `string_approximate`，标“不适用”；`astronomy-hard-11` 没有最终答案，标“无答案”。

### 题面答案形式原句

CSV 原句列按题保存，共 **27 题检出 37 句**。来源为 `meta.prompt_values.query`，已逐题与 workload.query 核对一致。分句边界为后接空白或结尾的 `. ! ?`，小数点和 URL 内部句点不拆分；摘录用原题面的字符位置切片，保留句内文字、标点和换行，不改写。

机械检索词为 `round/rounded/rounding`、`decimal/decimals`、`percentage/percentages/percent`、`nearest`、`format`、`list`、`answer`、`report`、`pair`、`positive`、`negative`、`true`、`false`、`full names`、`no explanation`、`%`（不区分大小写，英文词按词边界检索）。这里只摘取含关键词的原句，没有再判断其约束作用；同词的文件格式说明、问题描述等句子也可能被保留。未检出时 CSV 为空，仅表示本规则未检出，不断言题面没有答案形式要求。

每句的原始起止位置和命中词另存 details JSON；检查脚本确认全部 37 句均与对应 query 的原始切片逐字一致。

## 证据来源

- 名单和第 0 档：`records/029_kramabench_final_scores.csv`，筛选 `最终状态 in {未通过, 未交卷}`，共 42 行；未修改该表。
- agent 最终答案：`records/027_kramabench_source/runs/<批次>/<题号>_01/meta.json` 的 `final_answer`；标准答案：`data/kramabench/workload/<领域>.json` 对应 `id` 的 `answer`。详细记录逐题注明来源路径。
- 官方函数：`records/027_kramabench_source/official/benchmark/metrics.py` 的 `Success`、`F1`，以及所需 `Metric`、`str_to_float`、`try_convert_to_number`。脚本从源码 AST 取出这些**未修改的原定义**执行，不重写指标，也不导入 model、LLM 或其他无关指标。原定义的源码位置/hash 在 summary JSON 中。
- 调用与验证：[逐次调用记录](../records/030_kramabench_metric_calls.json)、[详细候选记录](../records/030_kramabench_tolerance_details.json)、[验证结果](../records/030_kramabench_validation.json)。验证覆盖 42 行 CSV、210 次官方函数返回重放、85 个取整候选数值及 37 条原文切片。
- 主要命令：`PYTHONDONTWRITEBYTECODE=1 python3 records/030_kramabench_tolerance.py > records/030_kramabench_tolerance.log 2>&1`；`PYTHONDONTWRITEBYTECODE=1 python3 records/030_check_kramabench_tolerance.py > records/030_kramabench_check.log 2>&1`；`python3 records/030_render_kramabench_tolerance_report.py`。
- 调用脚本禁用 socket 网络连接；没有读取 key、导入模型客户端或调用模型。所有 F1 入参都是 list，官方 `eval()` 分支不可达。验证前后来源 hash 相同，Git 中已有跟踪文件无改动。

## 不确定或没查到的

- 本次只能记录这些明确操作下的 `Success/F1` 返回值；“各适用档均未对上”不表示其他未指定的放宽方式也不可能对上。未增加同义词、地名改写、标点归一化、单位转换或人工答案选择。
- 字符串分隔符采用独立候选，列表取整采用按位置对齐；它们是本次明确记录的机械实现口径，不从题面推测其他解释。
- 关键词摘句不是语义筛选，可能保留并非答案输出约束的句子，也可能漏掉未含这些关键词的要求；已保存原 query 供直接查阅，不对这些句子作判定。
- 日志开头的 `Success ... unsupported argument types` 警告来自离线自检 `Success(True, "True")`；自检确认原函数返回 0，再检查统一类型后返回 1。它不是某道题的新增异常或错因判断。

## 建议的下一步

将本次 CSV 与原句摘录交给用户和 Claude 阅读；保持 029 正式分数原样。本任务到记录和核对为止，不据此改分、归类错因或继续运行 agent。
'''
path=ROOT/'notes/030_2026-10-31_KramaBench宽松比对.md'
with path.open('x',encoding='utf-8') as f:f.write(report)
print(f'Rendered {path.relative_to(ROOT)}')
