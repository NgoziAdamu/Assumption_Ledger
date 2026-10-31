# KramaBench GPT-6 Luna 基线记录

核查日期：2026-10-31。找到两批全量运行，覆盖全部 **104 道不同题**：困难题 62 道、简单题 42 道。按原记录，**54 题通过、40 题未通过、10 题待裁判**；40 题中有 1 题耗尽步数未交卷。两批均在新加坡时间 2026-10-18 运行。

主基线使用项目自己的工具调用循环，执行器基于 smolagents 接口；每题可访问所属领域的完整输入目录。评分使用从官方源码提取的确定性指标，**没有运行完整官方评测入口，也没有为待裁判题调用模型裁判**。

另找到三批五题试跑，共 15 题次，保留了失败尝试和再次运行的结果。随附 CSV 共 **119 行记录**：104 行主基线、15 行早期试跑；通过“批次类型”筛选即可区分。后续续跑和连续会话另行列出，不计入主基线。

本次只读取已有记录并计算计数、字符数和文件大小。没有分析错因、重新评分、执行轨迹代码、运行实验或复制已有文件。除本报告和 CSV 外，未主动写入其他文件；按本次只读要求，没有更新旧目录索引或提交推送。

## 运行日期与已有批次

“题次”是一次运行记录，同一道题在不同批次可重复出现。“运行正常结束”与“原评分通过”分别记录。

| 批次 | 新加坡时间（UTC+8） | 题次 | 原记录通过 / 未通过 / 待裁判 | 运行状态 |
| --- | --- | --- | --- | --- |
| 困难题全量 | 2026-10-18 02:26:01 至 2026-10-18 03:16:29 | 62 | 24 / 31 / 7 | success：61、max_steps_unanswered：1 |
| 简单题全量 | 2026-10-18 15:24:30 至 2026-10-18 15:49:29 | 42 | 30 / 9 / 3 | success：42 |
| 首轮五题尝试 | 2026-10-17 21:25:42 至 2026-10-17 21:25:58 | 5 | 0 / 5 / 0 | failed：5 |
| 首轮五题再次运行 | 2026-10-17 23:27:02 至 2026-10-17 23:46:09 | 5 | 3 / 2 / 0 | success：5 |
| 第二轮五题试跑 | 2026-10-18 01:32:21 至 2026-10-18 01:39:27 | 5 | 3 / 2 / 0 | failed：1、success：4 |

三批早期试跑都使用相同的五题：archeology-hard-5、biomedical-hard-1、environment-hard-10、environment-hard-17、legal-hard-15。这五题后来也出现在困难题全量批次中。两批全量各题只保存一次独立运行，重复次数配置均为 1；没有将五题试跑混入全量成绩。

## 运行配置

- 全量批次与第二轮五题试跑：项目原生工具调用循环，每轮最多执行一个 Python 工具调用。持久 Python 子进程在同一题内保留变量，题与题之间使用独立工作目录。执行器实现 smolagents 的 PythonExecutor 接口。没有使用 KramaBench 自带 DS-Guru。
- 首轮五题尝试及其再次运行：项目自定义的 smolagents RecordedCodeAgent，以代码块驱动执行；与后续原生工具调用版本分开记录。
- 所有上述批次的模型名均记录为 `openai/gpt-6-luna`，通过 OpenRouter 请求；成功响应中返回的模型名也为该值。推理强度为 `medium`，供应商参数校验开启，流式响应关闭。全量批次使用 `tool_choice=auto`；未发送 `parallel_tool_calls`。首轮失败尝试曾发送 `stop`，再次运行时未发送。
- 请求记录没有设置 `temperature`、`top_p`、`max_tokens` 或 `max_completion_tokens`；因此不能从本地记录给出这些参数的服务端默认值。
- 每题模型请求上限为 30 次，包含接口重试；并非保证执行 30 段代码。每个 Python 执行步骤限时 300 秒，HTTP 请求也设置 300 秒超时。没有独立的每题总时长上限。长执行观察反馈给模型时最多保留 4000 字符。
- 后续工具调用版本的接口重试最多 3 次尝试，重试等待为 5 秒、20 秒，并受上述 30 次请求总上限约束。每批全量共享 3 美元预算；每批五题试跑共享 2 美元预算。
- 数据按领域提供：每题可读取对应领域的整个输入目录，包含该领域的其他文件。没有按题面标注预选“相关文件”，也没有把六个领域合并成单一可访问目录。文件清单最多逐项列出 200 个文件，超出部分按目录汇总；这不减少目录内实际可访问的文件。没有使用另存的精简输入目录。

## 原有评分记录

下表只转写原有最终答案评分，不使用后续研究判定或人工复核替换分数。

| 领域 | 题数 | 原记录通过 | 原记录未通过 | 待裁判 |
| --- | --- | --- | --- | --- |
| 考古 | 12 | 5 | 7 | 0 |
| 天文 | 12 | 6 | 5 | 1 |
| 生物医学 | 9 | 5 | 4 | 0 |
| 环境 | 20 | 10 | 8 | 2 |
| 法律 | 30 | 20 | 7 | 3 |
| 野火 | 21 | 8 | 9 | 4 |

“是否做错”仅映射原记录：最终通过标记为 1 时填“否”，为 0 时填“是”；待裁判填“待裁判”，得分留空。未交卷原本记录为 0 分，因此计入未通过。本报告没有重新判断任何答案是否正确。

CSV 的“得分”保留二值最终通过标记；“主指标得分”另存原始指标值。“原始评分JSON”完整保留已有评分字段，包括数值误差指标、列表 F1（综合精确率与召回率的指标）、精确率和召回率。两道困难题的列表 F1 有部分分数：wildfire-hard-16 为 0.5，wildfire-hard-21 为 0.6666666666666666；两题原最终通过标记均为 0。

现存评分适配器从官方指标源码提取定义后调用；数值和精确字符串使用 Success，数值近似题另记绝对误差、平方误差与相对绝对误差分数，列表题使用 F1 等指标，并以 F1 等于 1 作为通过条件。适配器把字符串解析替换为安全字面量解析，使用本地确定性的一元词匹配实现，并阻止模型裁判。需要语义裁判的题保留待裁判。它没有运行官方完整评估器或逐子任务评测，不能将这里的记录描述为完整官方评测脚本的输出。

未通过的 40 题如下。表中题号本身带有领域和难度，CSV 同时提供单独的领域列。

| 领域 | 困难题未通过 | 简单题未通过 |
| --- | --- | --- |
| 考古 | archeology-hard-1、archeology-hard-2、archeology-hard-5、archeology-hard-7、archeology-hard-9、archeology-hard-12 | archeology-easy-8 |
| 天文 | astronomy-hard-8、astronomy-hard-9、astronomy-hard-11、astronomy-hard-12 | astronomy-easy-6 |
| 生物医学 | biomedical-hard-5、biomedical-hard-8 | biomedical-easy-2、biomedical-easy-9 |
| 环境 | environment-hard-7、environment-hard-15、environment-hard-16、environment-hard-19、environment-hard-20 | environment-easy-2、environment-easy-3、environment-easy-5 |
| 法律 | legal-hard-8、legal-hard-14、legal-hard-17、legal-hard-18、legal-hard-22、legal-hard-24、legal-hard-29 | 无 |
| 野火 | wildfire-hard-4、wildfire-hard-6、wildfire-hard-14、wildfire-hard-16、wildfire-hard-17、wildfire-hard-19、wildfire-hard-21 | wildfire-easy-1、wildfire-easy-9 |

待裁判共 10 题：environment-hard-12、environment-hard-18、legal-hard-2、legal-hard-23、wildfire-hard-7、wildfire-hard-12、wildfire-hard-18、astronomy-easy-4、legal-easy-25、wildfire-easy-13。它们没有被计入“做错”。

## 轨迹格式与截断

每题一个目录，目录内分别保存消息 JSONL（每行一个 JSON 记录）和执行 JSONL，不是把所有题合在一个轨迹文件。批次级汇总文件合并元数据和结果，但不代替逐题轨迹。

- 消息轨迹包含每次请求及其对话历史、模型返回的正文、工具调用和接口响应。模型返回的推理字段也随响应保存；部分字段不是可读自然语言，不能把所有推理字段都视为可读思考全文。请求中的重复历史也保留。
- 执行轨迹包含每步实际执行的代码、标准输出、错误输出、错误字段和完整执行观察。全量批次共 747 条执行记录，均有代码及这些输出字段；另外保留了执行开始和解析事件。没有代码执行的回复仍可在消息轨迹中找到。
- 最终答案保存在每题元数据及最终执行记录中。全量 103 题有提交的最终答案，astronomy-hard-11 未交卷，元数据最终答案为空。
- 依赖图和中间产物快照另存。它们不计入下文定义的文本轨迹字符数。

**执行输出存在两种保存范围。** 本地执行轨迹保留运行时捕获的完整输出；发给模型的长观察保留头尾，中间插入截断标记，总长 4000 字符。困难题有 105 个执行观察超过该上限，简单题有 39 个。这里按实际执行记录计数，没有把同一观察在后续请求历史中的重复出现重复计入。

实例：archeology-hard-12 的第 5 个执行步骤，本地标准输出和完整观察均为 **36,044 字符**；后续请求中的同一工具反馈为 **4000 字符**。以下是该反馈内截断位置的实际片段，前后的空格为表格对齐：

```text
    935
                      
... [output truncated] ...
                    Hungary-Venice (Dalmatia)
```

这说明模型看到的反馈被截断，而本地执行记录仍保存较长的输出。若代码或 pandas 自身只打印表头、预览或省略行，轨迹只能保存实际打印的内容，不能据此声称保存了完整中间表。

## 轨迹字符数与大小

统一口径：**轨迹字符数 = 原始消息 JSONL 的 UTF-8 解码字符数 + 原始执行 JSONL 的 UTF-8 解码字符数**。包含文件中的 JSON 字段名、转义字符、空白、换行和重复对话历史；不先反序列化后拼接正文。字节数是这两个原文件的字节长度之和。CSV 提供每题两个分项及合计。

| 批次 | 消息字符数 | 执行记录字符数 | 轨迹合计字符数 | UTF-8 字节数 |
| --- | --- | --- | --- | --- |
| 困难题全量 | 25,130,418 | 16,689,909 | 41,820,327 | 41,834,364 |
| 简单题全量 | 8,212,237 | 4,626,398 | 12,838,635 | 12,841,920 |
| 首轮五题尝试 | 26,816 | 0 | 26,816 | 26,816 |
| 首轮五题再次运行 | 4,013,277 | 1,207,182 | 5,220,459 | 5,225,146 |
| 第二轮五题试跑 | 2,026,166 | 1,206,309 | 3,232,475 | 3,233,532 |
| 主基线合计（104 题） | 33,342,655 | 21,316,307 | 54,658,962 | 54,676,284 |
| 连同早期试跑（119 题次） | 39,408,914 | 23,729,798 | 63,138,712 | 63,161,778 |

104 题主基线轨迹共 **54,658,962 字符，54,676,284 字节（52.14 MiB）**。包含早期试跑时为 **63,138,712 字符，63,161,778 字节（60.24 MiB）**。这些数值不包括元数据、依赖图、快照、工作目录或既有导出副本，因此不会因数据目录符号链接而重复计算数据湖。

## 本地材料与运行异常

六个领域的数据输入目录均存在，共 **1,742 个文件，666,850,039 字节（635.96 MiB）**。这是本地现有文件的清点，不代表已重新核验上游发布数据是否完整。

六份主工作负载文件均存在，包含 **104 道题的标准答案及 631 条子任务标注**。子任务包含编号、步骤、问题、答案、答案类型和数据来源等字段；它们与标准答案保存在同一组 JSON 文件内。这六个载体文件合计 **6,930,166 字节（6.61 MiB）**，不是拆分后的答案或标注净大小。另有 104 份参考解法脚本，合计 214,813 字节。官方评测入口和指标源码均在本地。

全量批次的异常只记录如下：

- 困难题 astronomy-hard-11 达到 30 次模型请求上限，未交卷；其余 61 题正常交卷。简单题 42 题全部正常交卷。未发现两批中有步骤超时或整个任务失败状态，批次未启动题列表均为空。
- environment-hard-13 和 archeology-easy-3 各记录 1 次接口连接中断及 1 次请求重试，之后正常交卷。前者为困难题，后者为简单题。这是同一道题内重试请求，不是把整题从头运行一遍；这两次失败请求的费用字段为空。
- 执行轨迹含困难题 45 步、简单题 20 步非空错误记录。这里只计数，不分析错误来源或其与评分的关系。
- 首轮五题尝试的 5 题均为 failed，已有错误类型为 AgentGenerationError，没有执行代码。再次运行的五题全部正常交卷。第二轮五题试跑中 archeology-hard-5 为 failed，现存错误信息为“The CPython worker exited unexpectedly.”，记录 17 次模型调用、12 次执行；另四题正常交卷。
- 三批试跑和全量批次的同题记录均保留，没有覆盖早期结果。两批全量的同题目录没有发现第二份独立重跑结果。

此外还找到同一模型的后续实验：8 道题的 48 次续跑，以及 6 次连续会话（33 条问题记录，覆盖 11 个不同题号）。它们分别是已有中间状态上的续接、跨题连续会话；不与独立逐题主基线混算。此处仅登记其存在和位置，不评判实验结果。

## 技术细节、路径与核查口径

本报告：`/home/katherine/dac/notes/36_KramaBench基线记录.md`。随附 CSV：`/home/katherine/dac/notes/36_KramaBench基线逐题记录.csv`，编码 UTF-8，无 BOM。CSV 中逐行提供真实存在的结果、两份轨迹、依赖图和日志的绝对路径；“批次类型=主基线”对应本文的 104 题统计。

### 结果、轨迹与日志位置

| 批次 | 原始运行目录（结果、轨迹和日志均在其内） | 已有导出目录 |
| --- | --- | --- |
| 困难题全量 | `/home/katherine/dac/runs/20261018_hard_all_01` | `/home/katherine/dac/analysis/20261018_hard_all_01` |
| 简单题全量 | `/home/katherine/dac/runs/20261018_easy_all_01` | `/home/katherine/dac/analysis/20261018_easy_all_01` |
| 首轮五题尝试 | `/home/katherine/dac/runs/20261018_pilot_01` | 未找到同名目录 |
| 首轮五题再次运行 | `/home/katherine/dac/runs/20261018_pilot_01_1` | `/home/katherine/dac/analysis/20261018_pilot_01_1` |
| 第二轮五题试跑 | `/home/katherine/dac/runs/20261018_pilot_02` | `/home/katherine/dac/analysis/20261018_pilot_02` |

每个原始运行目录中，`summary.json` 为逐题结果汇总，`batch_meta.json` 为批次参数、未启动题列表和计数，`README.md` 保存原运行命令；逐题 `meta.json` 保存时间、配置、最终答案和评分，`messages.jsonl` 保存模型交互，`steps.jsonl` 保存代码及执行输出，`graph.json` 保存依赖图，`artifacts` 保存快照，工作目录内的 `.worker-stderr.log` 保存 worker 进程错误输出。CSV 给出这些逐题文件的完整实际位置。

全量共 104 份 worker 日志：困难题 62 份合计 1862 字节，其中 3 份非空；简单题 42 份均为空。非空文件为：

- `/home/katherine/dac/runs/20261018_hard_all_01/astronomy-hard-11_01/workspace/.worker-stderr.log`：1330 字节。
- `/home/katherine/dac/runs/20261018_hard_all_01/astronomy-hard-9_01/workspace/.worker-stderr.log`：266 字节。
- `/home/katherine/dac/runs/20261018_hard_all_01/legal-hard-7_01/workspace/.worker-stderr.log`：266 字节。

在这两批运行目录内未找到另存的批次终端 stdout/stderr 日志；实际代码的标准输出和错误输出见执行 JSONL。既有导出目录仅登记其位置，本次没有生成或更新任何导出副本；本文字符数只统计原始目录。

截断实例的证据文件：`/home/katherine/dac/runs/20261018_hard_all_01/archeology-hard-12_01/steps.jsonl` 与 `/home/katherine/dac/runs/20261018_hard_all_01/archeology-hard-12_01/messages.jsonl`。用第 5 步记录的工具调用编号关联后续请求中的同一工具消息。

后续续跑：`/home/katherine/dac/runs/20261019_continuation_01`，汇总为 `continuation_summary.json`、`sample_results.csv`。实际 UTC 时间为 2026-10-18 12:49:51 至 13:13:53，即新加坡时间当日 20:49:51 至 21:13:53。

连续会话：`/home/katherine/dac/runs/20261018_session_pilot_01`，汇总为 `summary.json`、`summary.csv`。6 次真实模型会话的 UTC 时间为 2026-10-18 15:25:48 至 16:10:33，即新加坡时间 2026-10-18 23:25:48 至 2026-10-19 00:10:33。目录名中的日期未必等于全部记录的实际日期，应以元数据为准。

### 数据湖位置与大小

| 领域 | 数据路径 | 文件数 | 逻辑大小（字节） |
| --- | --- | --- | --- |
| 考古 | `/home/katherine/dac/benchmarks/KramaBench/data/archeology/input` | 5 | 7507730 |
| 天文 | `/home/katherine/dac/benchmarks/KramaBench/data/astronomy/input` | 1538 | 506180725 |
| 生物医学 | `/home/katherine/dac/benchmarks/KramaBench/data/biomedical/input` | 8 | 89659472 |
| 环境 | `/home/katherine/dac/benchmarks/KramaBench/data/environment/input` | 37 | 30877625 |
| 法律 | `/home/katherine/dac/benchmarks/KramaBench/data/legal/input` | 132 | 882402 |
| 野火 | `/home/katherine/dac/benchmarks/KramaBench/data/wildfire/input` | 22 | 31742085 |

总根目录为 `/home/katherine/dac/benchmarks/KramaBench/data`，大小按普通文件字节数求和，不沿符号链接重复累计。另一个本地精简输入目录为 `/home/katherine/dac/benchmarks/KramaBench/dr-input`，共 750 个文件、448,621,746 字节；主基线元数据的数据根目录指向上表的完整领域输入目录。

### 标准答案、子任务与参考解法

| 领域 | 标准答案与子任务标注的共同载体 | 题数 | 子任务数 | 大小（字节） |
| --- | --- | --- | --- | --- |
| 考古 | `/home/katherine/dac/benchmarks/KramaBench/workload/archeology.json` | 12 | 71 | 2176360 |
| 天文 | `/home/katherine/dac/benchmarks/KramaBench/workload/astronomy.json` | 12 | 68 | 3465724 |
| 生物医学 | `/home/katherine/dac/benchmarks/KramaBench/workload/biomedical.json` | 9 | 38 | 57337 |
| 环境 | `/home/katherine/dac/benchmarks/KramaBench/workload/environment.json` | 20 | 148 | 431167 |
| 法律 | `/home/katherine/dac/benchmarks/KramaBench/workload/legal.json` | 30 | 186 | 330920 |
| 野火 | `/home/katherine/dac/benchmarks/KramaBench/workload/wildfire.json` | 21 | 120 | 468658 |

以上六份主文件中的 `answer` 为标准答案，`answer_type` 为答案类型，`subtasks` 为子任务标注，`data_sources` 为相关数据标注。没有把 tiny 或 quick-start 文件中的重复题再加入主题数。参考解法根目录为 `/home/katherine/dac/benchmarks/KramaBench/solutions`。

### 官方评测文件与实际评分适配器

| 官方文件 | 大小（字节） |
| --- | --- |
| /home/katherine/dac/benchmarks/KramaBench/evaluate.py | 10111 |
| /home/katherine/dac/benchmarks/KramaBench/eval.sh | 1250 |
| /home/katherine/dac/benchmarks/KramaBench/scripts/eval.sh | 328 |
| /home/katherine/dac/benchmarks/KramaBench/benchmark/evaluator.py | 8918 |
| /home/katherine/dac/benchmarks/KramaBench/benchmark/metrics.py | 20116 |
| /home/katherine/dac/benchmarks/KramaBench/benchmark/benchmark.py | 11905 |
| /home/katherine/dac/benchmarks/KramaBench/benchmark/executor.py | 10369 |

本项目实际评分入口为 `/home/katherine/dac/src/dac/scoring.py` 中的 `official_score()`、`metric_definitions()`；实际加载的官方指标文件为上表 `benchmark/metrics.py`。两批所有逐题元数据的评分来源均为 `official_deterministic_definitions`。读取评分记录时未调用上述评分函数或执行官方脚本。

### 时间、版本与验证

| 批次 | UTC 开始与结束时间 | 记录的 Git 提交 | 工作区未提交改动 |
| --- | --- | --- | --- |
| 困难题全量 | 2026-10-17T18:26:01.955779+00:00 至 2026-10-17T19:16:29.712848+00:00 | e211824208147599702c61b9c2e3a15c1c458248 | False |
| 简单题全量 | 2026-10-18T07:24:30.056542+00:00 至 2026-10-18T07:49:29.440238+00:00 | 4d72494a1c3d778e5521699d44fc717f3d24fcab | False |
| 首轮五题尝试 | 2026-10-17T13:25:42.309955+00:00 至 2026-10-17T13:25:58.174642+00:00 | 5a16cba0678b1f4ca8d03166f7127bf35e91bd31 | False |
| 首轮五题再次运行 | 2026-10-17T15:27:02.336378+00:00 至 2026-10-17T15:46:09.714175+00:00 | 48c95ee63ef112c2e67ed5f33955ac4f14da289b | False |
| 第二轮五题试跑 | 2026-10-17T17:32:21.952302+00:00 至 2026-10-17T17:39:27.652588+00:00 | 9327db8a48f841b02af93c2403577b24d583d058 | False |

元数据所记环境：Python 3.12.15、smolagents 1.26.0、pandas 2.3.3、NumPy 2.5.4、pyarrow 26.0.0。本次未安装或升级依赖。

通过只读 Git 历史查看两批运行时的模型适配器、工具循环、执行器和评分适配器；文件字节哈希均与当时逐题元数据中的源码哈希匹配。简单题元数据虽标记存在未提交改动，但上述四个被引用源码文件均与所记提交一致。批次结果汇总与各题元数据逐项一致；104 个主基线题号与六份主工作负载题号集合一致。

文件统计在已激活的项目虚拟环境中用 Python 只读完成。没有导入 Agent 入口、调用模型或执行保存的代码，没有访问凭据目录或环境变量文件。写入报告与 CSV 前后，所读运行元数据、汇总、轨迹、依赖图和 worker 日志的 SHA-256 均核对不变。进入本次工作时已有的提示词审批文件改动未触碰。

密钥扫描：本次仅扫描新报告和 CSV，不导出原始轨迹内容。按完整且实际存在的 runs/analysis 路径规则放行 0 条（0 个不同路径字符串）；无示例。没有使用原件逐字证据或 Python 属性链豁免。
