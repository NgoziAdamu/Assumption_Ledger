"""Render the receipt report from inspected records; no benchmark execution."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'records'
s = json.loads((R / '027_kramabench_verification.json').read_text())
pending = json.loads((R / '027_kramabench_pending_judge.json').read_text())
chars = list(csv.DictReader((R / '027_kramabench_trace_characters.csv').open()))
out = []
def add(text=''):
    out.append(text)

add('''# KramaBench 材料接收

日期：2026-10-31。来源：`/home/katherine/dac`（用户给出的 `~dac` 在当前 shell 未展开；已核实实际目录）。

## 任务

接收旧项目 104 题 GPT-6 Luna 主基线材料，排除 15 次早期试跑轨迹；逐题查清 10 道“待裁判”为什么没有评分，记录官方补评所需材料。只复制和读取既有记录，不判断答题错因、不运行轨迹代码、不重跑、不补评、不调用模型。

## 结论

**已核实**：主基线为困难题 62 道、简单题 42 道，104 个不同题号；原评分为 54 题通过、40 题未通过、10 题待裁判，未改变任何分数。复制的 4,546 个源文件合计 740,539,606 字节，逐文件字节数和 SHA-256 均与源文件一致；所选源文件复核未变，旧项目 Git 状态前后相同。

**已核实**：10 题全部标为 `string_approximate`，都有非空最终答案，运行状态全部为 `success`。实际适配器在读取答案类型后直接返回 `needs_judge`，未调用模型裁判。这 10 个“无分数”状态的原因是评分分支主动跳过裁判，没有证据把它们归因为答案格式解析失败。这里不判断这些答案对错。

官方本地源码的对应指标为 `llm_paraphrase`，指定裁判模型 `gpt-5-mini`，调用 OpenAI Chat Completions API，读取环境变量 `OPENAI_API_KEY`。本次未查验账户权限、模型服务可用性或 API 余额。

## 详细发现

### 复制清单与路径

| 材料 | 本项目位置 | 范围 |
| --- | --- | --- |
| 104 题轨迹归档 | `traces/kramabench_luna_baseline.tar.gz` | 按原批次/题目录保存 `messages.jsonl`、`steps.jsonl`、`graph.json`、workspace 执行输出捕获文件和 worker 日志 |
| 旧报告与 CSV | `records/027_kramabench_source/36_KramaBench基线记录.md`、`36_KramaBench基线逐题记录.csv` | 原名、原字节复制；CSV 保留原有 119 行，主基线 104 行，早期试跑 15 行 |
| 运行配置、最终答案及评分 | `records/027_kramabench_source/runs/<批次>/` | 两批各 4 个批次文件；104 份 `<题号>_01/meta.json`，包含 `parameters`、`prompt_values`、版本、最终答案及 `score` |
| 当时使用的 prompt、评分适配器及运行入口 | `records/027_kramabench_source/runtime/` | 4 个 prompt 文件和 `scoring.py`、`run_kramabench.py`、`prompting.py`；未复制凭据 |
| 官方评测入口和支撑文件 | `records/027_kramabench_source/official/` | `evaluate.py`、两个 `eval.sh`、`pyproject.toml`、7 个 benchmark 模块、4 个 fixtures、5 个 llm_tools 模块；20 文件原样复制，不含第三方仓库整体 |
| 六领域数据湖 | `data/kramabench/data/<领域>/input/` | 1,742 文件，不入 Git |
| 标准答案及子任务标注 | `data/kramabench/workload/<领域>.json` | 六份共同载体，104 题、631 条 subtasks，不入 Git |

源批次只取 `runs/20261018_hard_all_01` 和 `runs/20261018_easy_all_01`。逐文件源路径、目的路径（归档成员用 `::` 分隔）、字节数和 SHA-256 见 [复制清单](../records/027_kramabench_copy_manifest.json)。每题最终答案和评分仍在原 `meta.json` 与 `summary.json` 中，不另造评分文件；103 题有提交答案，`astronomy-hard-11` 的 `final_answer=null` 原样保留。

轨迹中的代码保存在每步 `code` 和模型的工具参数内；这些运行的 workspace 没有独立 `.py` 最终代码文件。归档保留内嵌代码，没有把快照或数据表当代码归档。

按本项目 `traces/` 规则，排除两批的变量/表快照及 workspace JSON 共 2,100 文件、823,479,797 字节，也没有跟随 104 个数据目录符号链接。未复制 15 次早期试跑、续跑、连续会话、精简数据目录或参考解法。详见 [排除清单](../records/027_kramabench_excluded_files.json)。本次“文件数和字节数一致”指上述明确选定的材料与其源文件一致，不是整个 runs 目录镜像。

### 复制核对

以下每项源/目的文件数均相同，字节数为普通文件内容的逻辑字节数；归档项按解压后的成员内容计算，不将 tar 头部或 gzip 开销算作源文件大小。

| 材料 | 源文件数 = 目的文件数 | 源字节数 | 目的字节数 | SHA-256 |
| --- | ---: | ---: | ---: | --- |''')
labels = {'original_reports': '旧报告与 CSV', 'batch_configuration_results': '批次配置与汇总', 'per_task_meta': '逐题 meta',
          'messages.jsonl': '消息轨迹', 'steps.jsonl': '执行轨迹', 'graph.json': '依赖图', 'execution_capture_logs': '执行输出与 worker 日志',
          'gold_subtasks': '标准答案与子任务共同载体', 'official_evaluation': '官方评测文件', 'runtime_config_source': '旧项目配置/评分相关源码', 'runtime_prompts': '运行 prompts'}
for key,g in s['groups'].items():
    add(f"| {labels.get(key, key.replace('data_lake_', '数据湖：'))} | {g['files']:,} | {g['source_bytes']:,} | {g['destination_bytes']:,} | 全部一致 |")
add(f"| **合计** | **{s['copied_source_files']:,}** | **{s['copied_source_bytes']:,}** | **{s['copied_source_bytes']:,}** | **全部一致** |")
add(f'''
归档共 **{s['archive']['files']:,} 个文件**，成员内容 **{s['archive']['uncompressed_file_bytes']:,} 字节**，压缩后 **{s['archive']['compressed_bytes']:,} 字节（{s['archive']['compressed_bytes']/1024**2:.2f} MiB）**。

归档 SHA-256：`{s['archive']['sha256']}`。

两份 JSONL/题的核心轨迹合计 **208 文件、54,658,962 字符、54,676,284 字节**，与原报告/CSV 一致。62/42 题分批计数、104 个唯一题号、15 次试跑排除、10 个待裁判、104 题/631 子任务全部核对通过。数据湖总计 **1,742 文件、666,850,039 字节**，与旧报告一致。结构化结果见 [校验记录](../records/027_kramabench_verification.json)。

104 份元数据中的评分源码 hash 均匹配复制的 `scoring.py`；4 个 prompt 的 hash 也逐题匹配。官方目录当前 Git commit 为 `{s['official_local_git_commit']}`，工作区干净；它是本次接收的本地源码版本，不把它推断为运行当时未记录的官方版本。旧项目原有 `prompts/approved.txt` 改动和两份未跟踪旧报告保持原状态。

### 10 道待裁判：逐题证据

实际适配器 [runtime/src/dac/scoring.py 第 54–60 行](../records/027_kramabench_source/runtime/src/dac/scoring.py#L54) 原文如下；这段源码的 hash 已与 104 份运行元数据核对：

```python
def official_score(task, answer, benchmark):
    kind = task["answer_type"]
    source = "official_deterministic_definitions"
    if kind == "string_approximate":
        return {{"status": "needs_judge", "success": None, "source": source}}
    if answer is None:
        return {{"status": "unanswered", "success": 0, "source": source}}
```

逐题 `score` 原文字段相同：`"status": "needs_judge"`、`"success": null`、`"source": "official_deterministic_definitions"`。下表每行指向该题原始 meta；答案类型来自 `data/kramabench/workload/<领域>.json` 对应 `id`。完整逐题证据索引见 [待裁判记录](../records/027_kramabench_pending_judge.json)。

| 题号/评分原件 | workload 的 answer_type | 已提交答案的 Python 类型 | 未评分的已核实原因 |
| --- | --- | --- | --- |''')
for p in pending:
    add(f"| [{p['task_id']}](../{p['meta']}) | `string_approximate` | `{p['final_answer_type']}` | 命中上引第 57–58 行，直接写入 `needs_judge`，未调用裁判 |")
add('''
这些记录不是“完全没有评分对象”，而是有明确的待裁判状态、没有数值分数。环境题的 bool 答案、天文题的 dict 答案也命中同一个前置分支；不能从它们的类型另行推断解析失败。官方 `LLMParaphrase` 在裁判前对 predicted 和 target 均调用 `str()`（见下节），本次没有执行这一转换来评分。

### 按官方方法补评需要什么（本次未执行）

1. **脚本与规则**：已复制的 `official/benchmark/evaluator.py`、`metrics.py`、`fixtures/answer_type_fixtures.json`、`llm_tools/gpt_interface.py`、`llm_tools/prompts.py` 及导入依赖。fixture 原文为 `"name": "string_approximate", "metrics": ["llm_paraphrase"]`。不能继续用旧 `scoring.py` 直接补这 10 题，因为它仍会返回 `needs_judge`。
2. **输入**：从 10 份 meta 取出原 `final_answer`，从本地 workload 取对应原 `answer`；如果使用 `Evaluator.evaluate_results()`，需要把记录包装成 `{"task_id": "对应题号", "model_output": {"answer": 原final_answer}}`，保持值类型不变，使用只含这 10 个 task 的 workload，设置 `run_subtasks=False, evaluate_pipeline=False`。`evaluator.py` 按 `response["model_output"]["answer"]` 取值，不接受现有 meta 直接作为 response。本次只记录所需转换，未生成或执行补评适配器。
3. **裁判模型与 API**：本地源码指定 `gpt-5-mini`。`gpt_interface.py` 第 22、28 行读取 `OPENAI_API_KEY` 并构造 `OpenAI(api_key=OPENAI_API_KEY)`，第 145–148 行调用 `self.client.chat.completions.create(model=self.model, messages=messages)`；文件没有显式设置 `base_url`。需要可访问相应服务并有模型权限/额度的 API key，由运行环境提供，不能写入仓库。基线答题使用 OpenRouter 的 `openai/gpt-6-luna`，这与官方裁判脚本的模型和客户端配置不同。
4. **Python 依赖**：原 `pyproject.toml` 写 `requires-python = ">=3.10"`、`openai==1.72.0`、`typeguard>=4.0.0`、`rouge-score>=0.1.0` 等。实际导入还涉及 `nltk`、`untruncate_json` 和 `ollama`；`nltk`、`untruncate_json` 未列在该文件的依赖列表，`ollama` 在 optional baselines 中。补评前需另行准备并核实环境；本次未安装、导入或测试第三方评测代码。
5. **结果与运行边界**：保存官方 `llm_paraphrase` 返回值及 token usage、API/解析日志，不能把裁判返回 `None` 当作确定的 0 分。仅补最终答案时无需重跑 agent、读数据湖或执行模型生成的代码；标准答案和待评最终答案已齐。官方 `evaluate.py` 是完整 workflow 入口，默认会运行 benchmark，且默认开启 pipeline evaluation；直接运行现成 `eval.sh` 也不是这 10 题的专用补评命令。若以后选完整入口，需要准备兼容的 system cache，并使用 `--use_system_cache --no_pipeline_eval` 等匹配参数；本次没有准备或验证该完整流程。

官方 [metrics.py 第 338–344 行](../records/027_kramabench_source/official/benchmark/metrics.py#L338) 原文：

```python
        predicted = str(predicted)
        target = str(target)
        llm_interface = GPTInterface(model="gpt-5-mini")
        is_paraphrase, token_usage, token_usage_input, token_usage_output = llm_interface.evaluate_paraphrase(predicted, target)
        if is_paraphrase is not None:
            return (int(is_paraphrase), token_usage, token_usage_input, token_usage_output)
        return (None, token_usage, token_usage_input, token_usage_output)
```

裁判 prompt 原文（[prompts.py 第 4 行](../records/027_kramabench_source/official/benchmark/llm_tools/prompts.py#L4)）：

> You will receive two sentences A and B. Do these two sentences mean the same thing? Answer with only one word "yes" or "no".

官方 API 异常或未抽取出 yes/no 时会返回 `None`。脚本原文包括 `GPTInterface.evaluate_paraphrase: ERROR {e}` 和 `GPTInterface.evaluate_paraphrase: Failed to extract T/F value from answer {answer}.`（[gpt_interface.py 第 160–168 行](../records/027_kramabench_source/official/benchmark/llm_tools/gpt_interface.py#L160)）。这些是补评时需要记录的失败分支，不是本次 10 题已经发生的日志。

### 逐题轨迹内容与字符数

下表对**原始消息 JSONL + 执行 JSONL**做互斥字符分区，以便四列之和严格等于原 CSV 的轨迹字符数。计数单位是 UTF-8 解码后的 Unicode 字符，不是 bytes 或 tokens。保留原文件中的重复历史、provider_response 副本和逐语句记录；**不代表去重后的模型正文长度**。依赖图、workspace 日志、快照不纳入本表。

- **模型输出**：assistant 消息的 `content`、`refusal`、`reasoning`、`reasoning_details` 下的字符串值，包含历史及响应副本，也包含 `reasoning.encrypted` 的不透明字符串，不能当可读思考全文。
- **代码**：任意 `code` 字段的字符串及 `run_python` 的 `function.arguments` 字符串（后者含参数 JSON 包装）；包含执行开始事件、逐语句及历史中的副本。
- **执行输出**：steps 中 `stdout/stderr/error/display/traceback/full_observation` 字段的字符串，以及消息历史 role=tool 的 `content`；完整观察与 stdout 的重复都保留。模型看到的截断反馈与本地完整输出是不同的保存字段。
- **其他**：其余全部字符，包括系统/用户 prompt、字段名、结构标点、空白换行、非字符串值、时间/用量/指纹/依赖元数据。前三类以原始 JSON 字符串 token 长度计（含首尾引号、转义序列），不是反序列化后的正文长度；结构标点及 key 归其他。

分类实现：[027_receive_kramabench.py](../records/027_receive_kramabench.py) 的 `character_parts()`；机器可读表：[027_kramabench_trace_characters.csv](../records/027_kramabench_trace_characters.csv)。

| 题号 | 原评分映射 | 模型输出 | 代码 | 执行输出 | 其他 | 合计字符 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |''')
keys = ['model_chars','code_chars','execution_output_chars','other_chars','total_chars']
for c in chars:
    label = {'是':'未通过','否':'通过','待裁判':'待裁判'}[c['recorded_result']]
    add('| '+c['task_id']+' | '+label+' | '+' | '.join(f"{int(c[k]):,}" for k in keys)+' |')
add('| **合计** | 104 题 | '+' | '.join(f"**{sum(int(c[k]) for c in chars):,}**" for k in keys)+' |')
add('''
### 原评分未通过题的前 3 步原样摘录

选 `archeology-hard-12`，只依据原 `meta.json` 中 `score.success=0` 选题，不分析其答案错因。原件为归档内 `20261018_hard_all_01/archeology-hard-12_01/steps.jsonl`。第 1/3/5 行是 `execution_started` 事件，第 **2/4/6 行**分别是前三个完整 execution 记录。

完整三行已逐字节摘录为 [027_kramabench_example_first3_steps.jsonl](../records/027_kramabench_example_first3_steps.jsonl)（18,322 字节，保持原字段顺序、JSON 转义和换行）。以下先展示每步 `code` 与 `full_observation` 的原值，便于阅读；只做 JSON 解码展示，没有修正代码、删减输出或将日志错误解释成最终答错原因。
''')
raw = (R / '027_kramabench_example_first3_steps.jsonl').read_text()
for line in raw.splitlines():
    d=json.loads(line)
    add(f"#### 第 {d['step']} 步\n\n`code` 原值：\n\n```python\n"+d['code']+('' if d['code'].endswith('\n') else '\n')+'```\n\n`full_observation` 原值：\n\n```text\n'+d['full_observation']+('' if d['full_observation'].endswith('\n') else '\n')+'```\n')
add('<details>\n<summary>完整原始 JSONL 三行（展开查看实际轨迹格式）</summary>\n\n```jsonl\n'+raw+'```\n\n</details>')
add('''
## 证据来源

- 旧报告和 CSV：本报告上方所列同名原样副本；旧绝对路径保持原文，副本的新位置由复制清单映射。
- 评分状态、最终答案和运行参数：`records/027_kramabench_source/runs/` 的 104 份 meta 和两份 summary；该目录还保留批次 README 的原运行命令。
- 官方评分规则/API：`records/027_kramabench_source/official/` 中的 evaluator、metrics、fixtures、llm_tools 和 evaluate.py；均已实际打开核对，不使用网页描述替代本地实现。
- 核对与边界： [复制清单](../records/027_kramabench_copy_manifest.json)、[排除清单](../records/027_kramabench_excluded_files.json)、[校验结果](../records/027_kramabench_verification.json)、[最终核验](../records/027_kramabench_final_audit.json)、[执行日志](../records/027_kramabench_receipt.log)。最终核验覆盖两批所有文件的复制/排除去向、归档内 104 题与 747 条 execution 记录、103 份非空最终答案，以及示例原文逐字节一致。
- 主要执行命令：`python3 records/027_receive_kramabench.py > records/027_kramabench_receipt.log 2>&1`；`python3 records/027_render_kramabench_report.py`；使用 `rg`、`sed`、`nl`、Python JSON/CSV 只读读取原材料；用 `tarfile` 打包及逐成员读取校验、`hashlib.sha256` 比对；Git 只读状态核验使用 `--no-optional-locks`。未执行旧 README 中的运行命令和任何官方评测脚本。
- 首次文件预检命中加密 reasoning 字符串中间的类 token 片段，尚未复制即中止；核实字段路径后给凭据模式加 token 边界，再次预检和复制成功。对 2,798 份待入库源文件的指定凭据模式检查为 0 命中；没有读取凭据文件或写出凭据值。模式检查不是凭据绝对不存在的证明。

## 不确定或没查到的

- 本次只核验本地材料复制完整，不验证数据湖相对上游发布物是否完整，也不从未调用过的裁判推断答案对错。
- 两批未发现另存的批次终端 stdout/stderr 日志；执行输出在 steps JSONL、workspace 捕获文件及 worker 日志中。10 题未调用裁判，因此没有对应裁判 API 响应/失败日志；其未评分原因由记录的答案类型、评分状态和 hash 匹配的适配器代码确定。
- 未查 API key、模型权限、配额、网络可达性，也未验证官方依赖能否直接安装运行。`gpt-5-mini` 是这份本地官方源码的配置，不是对当前线上可用模型的声明。
- 原 `models.py`、`tool_loop.py` 当前文件 hash 与运行元数据不一致，未将它们作为当时实现复制。本次接收的运行事实以原参数、prompt hash 和原轨迹为准；已复制的评分适配器与 prompts 有运行 hash 验证。没有为重跑搭建完整旧环境。
- 轨迹含重复历史和不透明 reasoning 数据；字符统计不可解释为独立生成量或可读推理量。图中的 artifact 路径可能指向本次按规则未复制的旧快照。
- 报告中旧任务 `meta.prompt_values` 和原始轨迹内的题面/打印数据是运行记录组成部分；原始数据湖文件、gold 和子任务载体只在 `data/`。未把原始输入目录、环境缓存、第三方仓库或参考解法放入轨迹归档。

## 建议的下一步

如用户与 Claude 决定补评，仅为这 10 道已保存的最终答案准备官方 Evaluator 输入和所需 API 环境，保留官方裁判结果、token usage 与失败日志，并单独记录补评日期和版本。本任务停在材料接收与证据记录，不补评、不重跑、不改变研究设定。
''')
(ROOT / 'notes/027_2026-10-31_KramaBench材料接收.md').write_text('\n'.join(out), encoding='utf-8')
print('Rendered notes/027_2026-10-31_KramaBench材料接收.md')
