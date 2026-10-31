"""Render the report with a verbatim, deterministically sampled package excerpt."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'records'
s=json.loads((R/'028_kramabench_package_summary.json').read_text())
v=json.loads((R/'028_kramabench_validation.json').read_text())
assert v['passed']
sample=(R/'028_kramabench_report_sample.txt').read_bytes().decode('utf-8')
report=f'''# KramaBench 精简材料包

日期：2026-10-31。

## 任务

为既有 KramaBench 基线的 40 道未通过题和 10 道待裁判题制作逐题 Markdown 标注材料包。仅摘录原文、去除重复副本、统计字符和记录来源，不推测错因，不概括轨迹，不补评，不重跑。

## 结论

**已核实**：生成 **50 份材料包**，合计 **{s['package_total_chars']:,} 字符**；最小 **{s['package_min_chars']:,}**、中位数 **{s['package_median_chars']:,.0f}**、最大 **{s['package_max_chars']:,}**。50 题全部有可读 reasoning，按同一步逐字去重后合计 **{s['readable_reasoning_chars']:,} 字符**，分布在 **252 / 407** 个模型回复回合中。

材料包保留 **407 次模型回复、400 次代码执行、350 条可确认模型看到的 tool 反馈**。其中 **76 步**反馈被截断，均保存消息历史中的原文。**50 次末次执行没有后续请求中的 tool 反馈**，材料包明确标明缺失，不以本地完整输出补写。

独立检查脚本已通过：400 段代码与执行轨迹逐字一致，同时与模型工具参数中的代码一致；350 条反馈与请求历史逐字一致；题面、答案、315 条子任务的问题/答案、可读输出与 files_read 等 **2,254 个原文字段**均逐项核对。未改动来源文件，未运行任何保存的 agent 代码或评分入口。

## 详细发现

### 交付路径与选题

- 50 个逐题文件：[records/028_kramabench_packages/](../records/028_kramabench_packages/)，文件名为 `<题号>.md`。
- 逐题统计：[028_kramabench_package_stats.csv](../records/028_kramabench_package_stats.csv)。
- 每个原文字段及每步的来源索引：[028_kramabench_package_index.json](../records/028_kramabench_package_index.json)，包含 JSONL 行号、JSON 字段路径、模型 call、执行 step、tool_call_id、字符数及 SHA-256，不重复保存原文正文。
- 汇总：[028_kramabench_package_summary.json](../records/028_kramabench_package_summary.json)；检查结果：[028_kramabench_validation.json](../records/028_kramabench_validation.json)。
- 生成脚本：[028_build_kramabench_packages.py](../records/028_build_kramabench_packages.py)；独立检查脚本：[028_check_kramabench_packages.py](../records/028_check_kramabench_packages.py)。生成脚本拒绝覆盖已有材料包，检查脚本可以重复运行。

名单仅由两批全量运行的 meta 原 `score` 选取：`success=0` 共 40 题（39 题 `scored`、1 题 `unanswered`），加 `status=needs_judge` 共 10 题。六领域分布为考古 7、天文 6、生物医学 4、环境 10、法律 10、野火 13。没有混入通过题、15 次早期试跑或后续续跑。

材料包中的“官方评分状态”保留旧基线适配器的 `score` 原字段，并注明它不是完整官方评测入口的新结果。未把 `needs_judge` 改成失败；`astronomy-hard-11` 的最终答案保留 `null`，原运行状态为 `max_steps_unanswered`。

按本次明确要求，将这 50 题的标准答案及子任务原文放入 `records/028_kramabench_packages/` 并随材料包提交，作为本任务的标注摘录。未复制或提交数据湖文件、整份 workload 原件、其他题的 gold、变量快照或环境缓存。

### 原文和去重规则

1. **题面与答案**：题面取 `meta.prompt_values.query`，已逐题核对与 workload 中该题 query 相同。agent 最终答案取 `meta.final_answer`；标准答案与每条子任务的问题/答案按 workload 原顺序摘录。子任务节开头固定写明“以下内容 agent 看不到，只供标注使用”。不对任何答案做类型转换、清洗、解释或改写。
2. **字符串与 JSON 原文**：字符串以 JSON 解码后的原文呈现，保留原有空白和换行；数字、bool、null、数组、对象直接摘取源 JSON 的值文本，保留原序列化格式。代码围栏和 HTML 定位标记是材料包的展示包装。原文字段的字符长度写在标记中，围栏所需的额外换行不算正文，检查时据此取回精确 payload。
3. **步的定义**：一份 `direction=response` 模型消息算一步，按消息文件顺序排列。每步注明原模型 `call` 和执行 `step`，因此没有把二者当作同一个计数。7 次没有工具调用的纯文本回复也保留，注明无执行代码、无对应 tool 执行反馈、无 execution.files_read 字段。CSV 的“步数”采用模型回复回合数，合计 407；代码执行次数另在各材料包末尾列出，合计 400。
4. **模型输出**：每个 response 只取顶层 `message`，不再复制 `provider_response.choices[].message` 或请求中的 assistant 历史。保留 `content`、`reasoning` 和 `reasoning_details` 中可读的 `summary/text`。同一步只按**完整字符串相等**去重；不同步骤即使文字相同也保留。源记录中的 `reasoning.summary` 是模型原返回字段，本次没有另写摘要。仅在 `reasoning_details` 中出现的可读文本也已保留。
5. **加密 reasoning**：不保留 `reasoning.encrypted.data` 内容；每步只记录“有加密 reasoning，N 字符”，N 为该次顶层 message 中加密 data 字符串的长度之和，不计 provider_response 或历史副本。检查确认 376 段原加密 payload 均不在材料包中。
6. **代码与 files_read**：使用模型 `tool_call_id` 关联唯一 `kind=execution` 记录，并核对 `model_call`。只取该 execution 的完整 `code`、顶层 `files_read` 各一次，不重复 execution_started 事件、逐语句 `statements` 或工具参数中的代码副本。每题末尾对 files_read 的原始路径字符串做集合去重并排序；不归一化相对/绝对路径，不根据代码猜文件访问。
7. **模型看到的反馈**：只取实际 `direction=request` 的 `messages[]` 中 `role=tool`、`tool_call_id` 匹配的 `content`。同一 tool_call_id 在多个后续请求出现时先检查内容完全相同，再取首次出现的一份；请求 call 必须晚于产生代码的模型 call。不以 steps 中的 stdout、stderr 或 full_observation 代替模型看到的反馈。

**末次反馈缺失的处理**：50 题各有一次末次执行没有出现在后续请求的 tool 历史里，其中 49 次为 `is_final_answer=true`，1 次为 `astronomy-hard-11` 的最后执行。材料包只写“消息历史中未发现对应的 role=tool 反馈”等缺失说明，没有编造 feedback，也不把这些条目算成截断步骤。未保存为后续请求的输出不能被本任务证明为模型已看到。

### 字符数与分布

CSV 的“原始轨迹字符数”沿用 027 的口径：每题 messages.jsonl + steps.jsonl 的 UTF-8 解码字符数，含 JSON 转义、重复历史和包装；50 题合计 **{s['raw_total_chars']:,}**，逐题与 027 CSV 核对一致。

“材料包字符数”是实际 Markdown 文件 UTF-8 解码后的总字符数，包含题面、gold、子任务、原文字段、标题、定位标记和格式包装。它与原轨迹口径不同，新增的 gold/子任务也在总数中，不能将两者的差值全部解释为去重删除量。字符数均不是字节数或 token 数。

| 指标 | 字符数 | 对应题 |
| --- | ---: | --- |
| 50 包合计 | {s['package_total_chars']:,} | 全部 50 题 |
| 最小 | {s['package_min_chars']:,} | `{s['smallest_tasks'][0]}` |
| 中位数 | {s['package_median_chars']:,.0f} | 排序后第 25、26 个数的平均值 |
| 最大 | {s['package_max_chars']:,} | `{s['largest_tasks'][0]}` |

| 每包字符数区间 | 题数 |
| --- | ---: |
| ≤ 10,000 | 1 |
| 10,000 < N ≤ 50,000 | 32 |
| 50,000 < N ≤ 100,000 | 9 |
| > 100,000 | 8 |

315 条子任务的问题与标准答案原文字段合计 **{v['original_text_character_breakdown']['subtask_question_answer_chars']:,} 字符**。最大材料包 `astronomy-hard-11` 中，该部分为 **757,014 字符**；按用户要求保留原文，没有缩写长数组/对象。所有材料包的逐步原文字段（可读输出、代码、反馈、files_read）合计 **{v['original_text_character_breakdown']['step_original_fields_chars']:,} 字符**，不包含 Markdown 包装。

### 可读 reasoning 覆盖

- 有可读 reasoning 的题：**50 / 50**。
- 有可读 reasoning 的模型回复回合：**252 / 407**。
- 去除同一步完全相同字段副本后的可读 reasoning 总长：**157,202 字符**。
- 统计包含可读 `reasoning.summary`，不含 content、加密字符串、HTML/Markdown 标记或字段标题。跨步骤文本不去重。

### 截断规则与核验范围

50 份 meta 的 `parameters.max_output_chars` 均为 **4000**；保存的运行 prompt 也写明超出该限额时截断。对这 50 题有实际 tool 历史反馈的 350 次执行，机械核对得到：

- **76 次**本地 `full_observation` 超过 4000 字符，模型反馈均为 **4000 字符**；且逐字满足 **前 1986 字符 + `\\n... [output truncated] ...\\n`（28 字符）+ 后 1986 字符**。
- 其余 **274 次**反馈与本地 full_observation 完全相同，长度均不超过 4000。
- 每个截断步骤都写明“模型看到的被截断：看到 X 字符，完整输出 Y 字符”；材料包只放实际 tool content，不放被截去的完整输出。检查脚本也确认这 76 个完整 full_observation 字符串未进入对应材料包。

以上规则由本次收到的参数和实际记录核实，不是另行运行执行器得出的结果；不把 50 次缺少后续反馈的末次执行纳入可见反馈长度比较。

### 检查脚本与结果

执行：

```bash
python3 records/028_check_kramabench_packages.py
```

检查脚本不导入生成脚本，直接读取原 tar.gz、meta、workload、实际 Markdown 和来源索引。它按原模型回复重新建立步骤顺序与 tool 关联，并从 Markdown 的长度标记取回原文，核对以下内容：

- 50 题名单、400 段执行代码、350 条 role=tool 反馈及每步 files_read；代码还与模型工具调用参数交叉核对。
- 完整覆盖 407 次模型回复；50 次缺失末次反馈均有记录，未伪造为已见输出。
- 题面、最终答案、gold、315 条子任务及可读输出的来源与原文；加密 payload 未进入材料包。
- 截断提示的 X/Y、逐题 CSV 字符统计、reasoning 统计、全量 hash、随机样本前三步与包内文本一致。
- 只在内存中对一段代码和一段反馈各改动一个字符，逐字比较均拒绝；未改动材料包或源文件。

结果：**全部通过**，检查日志见 [028_kramabench_check.log](../records/028_kramabench_check.log)。该脚本只核对文本来源和机械统计，不验证任务答案是否正确。

### 随机抽样：材料包前 3 步原样

抽样方法：对 50 个题号排序后，执行 `random.Random(20261031).choice(sorted(task_ids))`。固定种子为 **20261031**，抽中 **`{s['random_sample_task']}`**。下文直接复制该 [材料包](../records/028_kramabench_packages/{s['random_sample_task']}.md) 中“第 1 步”至“第 3 步”整段文本，保持原文、标记和换行；未根据内容重新挑选题目。另存相同文本于 [028_kramabench_report_sample.txt](../records/028_kramabench_report_sample.txt)。

'''
report += sample
report += '''## 证据来源

- `traces/kramabench_luna_baseline.tar.gz`：两批全量的逐题 messages.jsonl 和 steps.jsonl；没有解压原始数据或执行其中代码。
- `records/027_kramabench_source/runs/{20261018_hard_all_01,20261018_easy_all_01}/<题号>_01/meta.json`：名单、评分状态、最终答案、prompt_values、4000 字符参数。
- `data/kramabench/workload/{archeology,astronomy,biomedical,environment,legal,wildfire}.json`：按 id 关联题目信息、标准答案与子任务；这些原件仍不入 Git。
- `records/027_kramabench_trace_characters.csv`：逐题原始轨迹字符数交叉核对。
- `records/027_kramabench_source/runtime/prompts/kramabench_system_v2.md` 第 6 行：运行时截断说明原文；参数值见 meta。
- `records/028_kramabench_package_index.json`：精确到归档成员、JSONL 行号和字段路径的出处。`records/028_kramabench_package_summary.json` 记录输入 SHA-256，检查脚本再次确认未变。
- 执行命令：`python3 records/028_build_kramabench_packages.py > records/028_kramabench_build.log 2>&1`；`python3 records/028_check_kramabench_packages.py > records/028_kramabench_check.log 2>&1`；`python3 records/028_render_kramabench_report.py`。未调用评分函数、模型 API 或基线运行命令。

## 不确定或没查到的

- 最后 50 次执行在已存消息历史里没有对应 tool 反馈；无法从这些记录证明模型实际看到了什么。没有用 full_observation 填补。
- files_read 只反映原执行器记录的字段。未记录的读取行为、不同路径是否指向同一文件不作推测；空列表也不解释成“实际没有读取”。
- 可读 reasoning 是保存下来的原字段，不能据此推断未保存的模型内部推理；加密 reasoning 只计长度。
- 材料包仅保留用户指定的字段，没有复制完整系统 prompt、后续用户控制消息、provider 元数据、逐语句依赖信息、完整本地输出或快照。原始轨迹仍保存在 027 归档中。
- 本次不裁定任何答案对错，不分析 40 道未通过题的错因，不为 10 道待裁判题补评分。

## 建议的下一步

将 50 份材料包交给用户与 Claude 标注；需要核对出处时使用索引和检查脚本。本次不改变研究设定或扩大到错因分析。
'''
path=ROOT/'notes/028_2026-10-31_KramaBench精简材料包.md'
path.write_text(report,encoding='utf-8')
assert sample in path.read_bytes().decode('utf-8')
print(f'Rendered {path.relative_to(ROOT)} ({len(report):,} characters)')
