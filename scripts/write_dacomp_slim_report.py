"""Task 013 Chinese delivery report from mechanical evidence and supplied review."""

import json

from complete_dacomp_comparisons import ROOT,RECORDS


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(map(str,headers))+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,row))+' |' for row in rows])


def main():
    packages=json.loads((RECORDS/'013_package_inventory.json').read_text());raw=json.loads((RECORDS/'013_raw_summary.json').read_text())
    states=json.loads((RECORDS/'013_status_summary.json').read_text());validation=json.loads((RECORDS/'013_validation.json').read_text())
    package_rows=[[p['task'],p['table'],p['characters'],p['without_SQL_contract_original_characters'],p['thought_message_sentence_characters'],
        '[材料包](../'+p['path']+')'] for p in packages]
    raw_rows=[]
    for r in raw['tasks_summary']:
        raw_rows.append([r['task'],r['initial_raw_tables'],r['agent_raw_tables'],r['different_tables'],r['schema_different_tables'],
            r['row_count_different_tables'],r['raw_write_syntax_steps'],
            '[差异与元数据](../records/013_raw_'+r['task']+'.json) / [命令原文](../records/013_raw_writes/013_'+r['task']+'_raw写操作.md)'])
    over=[p for p in packages if p['without_SQL_contract_original_characters']>15000]
    extra_rows=[[p['task'],p['without_SQL_contract_original_characters'],p['thought_message_sentence_characters']] for p in over]
    text=f'''# 精简试标材料包与原始数据改动检查

## 任务

为 012 抽中的同一批 30 张表生成精简 Markdown；只读比较全部 30 题初始 `*_start.duckdb` 与 agent 留存库的 raw 表清单、按顺序的列名 / 类型和行数，并摘录轨迹中的写 raw 语法；按用户和 Claude 的复核原文，把 19 张格式差异表写入独立的新状态文件。没有执行 agent / gold 节点 SQL，没有修改 012 材料包或 004–012 记录。

## 结论

**30 份精简版已完成**，同批抽样、差异依据及日期沿用 012。26 份扣除 SQL / 契约原文后不超过 15,000 字符；impl-016 为 15,001 字符。另 3 份因必须保留的 thought/message 原句较长，实际超过该目标，原句未截断。每份字符数如下（UTF-8 解码后 Python `len`；保留原换行）：

{table(['题目','表','总字符','扣 SQL/契约原文后','命中 thought/message 原句字符','精简版'],package_rows)}

**raw 比较共 691 对表，9 题的 68 张表在本次比较字段上有不同**。已逐项列出表存在性、列名 / 类型 / 顺序以及行数差异；这不是单元格内容比较。另记录 **207 个写 raw 语法或脚本调用语法匹配步骤**，完整命令和源码片段保存在 records/013_raw_writes/ 及结构化记录中；语法匹配不表示已证明运行分支执行或数据发生改动。

用户复核清单 **A=9、B=8、C=2，共 19 张**，与 012 名单逐张一致，无增减或自行归类。全量新状态仍为 1,069 行：

{table(['013 状态','数量'],[[k,v] for k,v in states['statuses'].items()])}

## 详细发现

### 1. 精简版内容与长度口径

[013_package_inventory.json](../records/013_package_inventory.json)逐包记录总字符、免计的契约 / SQL 原文字符、扣除原文后的字符及移除整段章节后的字符。目标口径只免计正式契约章节和双方 SQL 章节内的原文；thought/message 中即使含命令或 SQL 回显，仍算在其余字符内。

每份保留：一行基本信息和差异来源 / 日期；完整契约与双方 SQL；Markdown 行数 / 键数 / 重复键组总表及逐列 L0 计数、未抵消次数和实际类型；不一致列至多 3 个样例、独有键各至多 5 个样例；仅 agent 违反为 True 的 006 约束；仅 True 的 008 标记及最少证据；332 个步骤的逐行轨迹索引；agent action 的 thought/message 命中原句；result.md 命中原句；集中列出的原始路径。

为接近长度目标，样例可从每列 3 个缩为 1 个、独有键可缩至 1 个，均在用户给出的上限内；每个比较列的统计仍完整保留。重复样例键以 K1 / K2 等代号引用同包的完整键映射；重复键值保留值 / 次数，并明确不是按列表位置作唯一配对。表格仅作可逆 HTML 转义以显示换行和分隔符，值没有做新的数值、日期或大小写处理。

下面 4 份严格数值大于 15,000（其中 impl-016 仅多 1 字符，仍接近目标）。impl-001、011、013 的命中原句本身即为 17,246 / 26,380 / 15,182 字符，因而没有为了压缩而省去这些必需原句：

{table(['题目','扣 SQL/契约后字符','必须保留的 thought/message 原句字符'],extra_rows)}

轨迹索引只保留命令原文前 200 个 Unicode 字符、输出字符数、输出是否命中本表、是否有原记录显式截断标记；不附输出正文。thought/message 取 agent action 事件的顶层及 args 中同名文本字段，排除 observation 的环境输出；生成的 `Running command:` message 中的命中句也按原文保留。每句附 event id 和字段名，没有概括或改写。原始事件总数和归档事件目录逐包写明，所有路径集中在末尾以 S1 等编号引用；仓库内相对路径有明确根目录。

### 2. 30 题 raw 表结构与行数

所有原库均以 READ_ONLY 打开。表 / 视图都纳入清单；按表名对齐，记录每侧完整的列名、数据类型与 ordinal_position，以及精确 `COUNT(*)`。不存在的一侧为 null，不作 0 行处理。下表“列结构差异”包括缺表，“行数差异”也包括不可比较的缺表；两列可重叠，不能相加当作不同表总数。

{table(['题目','初始表数','agent 表数','不同表数','列结构不同','行数不同/缺表','写语法步骤','完整记录'],raw_rows)}

[013_raw_tables.jsonl](../records/013_raw_tables.jsonl)保存全部 691 对表；[013_raw_differences.md](../records/013_raw_differences.md)和 [CSV](../records/013_raw_differences.csv)逐项列出全部 68 张不同表的字段和计数。每题 JSON 包含双方完整顺序列清单、仅一侧列、共同列类型差、顺序变化、行数差和原库路径。本次判差字段是表清单、列结构和行数；表 / 视图类型也保留为元数据，没有将其单独计入这 68 张。

### 3. 写 raw 语法与脚本证据

[013_raw_write_steps.jsonl](../records/013_raw_write_steps.jsonl)每个命中步骤一行，共 207 行；每题的完整命令 Markdown 见上表链接。记录 event id、原事件文件 / archive member、完整命令、命令内原始写语法、涉及的脚本与原文源码片段、原记录 exit code。CREATE / REPLACE TABLE 或 VIEW、CREATE / DROP SCHEMA、ALTER / DROP / TRUNCATE、INSERT / REPLACE / MERGE INTO、UPDATE、DELETE FROM、COPY FROM 等按明确的 raw 目标匹配；COPY TO 和 SELECT 不作为写匹配。另匹配少量显式 schema=raw 的写 API。

脚本调用语法检查覆盖命令中明确的 Python / Bash / sh `.py` / `.sh` 路径。能从历史命令中的 literal heredoc 或 literal Path.write_text 恢复的脚本，保留该文字来源；其余使用最终留存源码，并明确标注“历史运行版本未确认”。本语法范围中未恢复源码的调用数为 {raw['unresolved_script_calls']}；这不是对所有动态代码生成方式的完备证明。

源码中含写 SQL、命令中含脚本调用语法，以及某条 SQL 分支实际执行是不同证据。记录明确设置 `runtime_branch_execution_proven=false` 和 `exact_runtime_file_version_verified=false`，没有把静态匹配当作已经修改 raw 的证明，也没有判断这些操作是否正确。没有执行任何摘出的命令、run.py 或其他脚本。

### 4. 用户复核后的 19 张格式差异

[013_review_basis.json](../records/013_review_basis.json)保存用户和 Claude 提供的依据原文；[名单核对](../records/013_review_correspondence.json)确认 A/B/C 与 012 逐张对应。每张新状态都附复核日期 **2026-10-29**、分组、依据原文和来源；这些是用户提供的复核结论，Codex 没有重新归类。

- A，9 张：**agent 输出类型符合契约声明，gold 类型与契约声明不同（9 张）**。
- B，8 张：**差异仅为浮点运算末位误差，契约未要求舍入或要求不舍入（8 张）**。impl-005 keyword segmentation 另保留原文：**其中 ctr 列 1 行 4.7226 / 4.7225，契约要求保留 4 位小数，经用户复核按格式差异处理**。
- C，2 张：impl-013 原文 **契约声明 DOUBLE，agent 为 DOUBLE 1.0，gold 为 BOOLEAN true**；impl-028 原文 **行元组完全一致，官方 L0 判为不一致**。

[013_statuses.jsonl](../records/013_statuses.jsonl)与 [CSV](../records/013_statuses.csv)各 1,069 行，只有这 19 张从“格式差异（待核契约）”变为“格式差异”，其余状态逐张不变；保留原 012 状态和 010 的 impl-002 注记。

## 证据来源

- [精简包清单与字符数](../records/013_package_inventory.json)、上方 30 个包链接；完整原包仍在 records/012_packages/。
- [raw 全量元数据 / 行数](../records/013_raw_tables.jsonl)、[全部差异 Markdown](../records/013_raw_differences.md)、[差异 CSV](../records/013_raw_differences.csv)、[逐题汇总](../records/013_raw_summary.json)、[完整写语法步骤](../records/013_raw_write_steps.jsonl)。
- [新状态](../records/013_statuses.jsonl)、[用户复核依据](../records/013_review_basis.json)、[19 表对应核对](../records/013_review_correspondence.json)。
- [验证](../records/013_validation.json)：30 份原文与索引核对、{validation['contract_and_SQL_original_blocks_preserved']} 个契约 / SQL 原文块、332 个索引行、{validation['agent_thought_message_sentences_verified']} 个 thought/message 命中句、691 对表及 {validation['raw_side_table_counts_and_ordered_schemas_rechecked']} 个单侧表结构 / 行数复查、207 条完整命令。[3 项扫描规则测试](../records/013_tests.log)通过。
- [前后完整性](../records/013_input_integrity.json)：{validation['original_input_files_unchanged']} 个原始文件前后大小、mtime、SHA-256 一致，其中 {validation['original_databases_unchanged']} 个数据库；004–012 记录及 012 材料包均不改。
- 实现：[状态与输入指纹](../scripts/prepare_dacomp_slim.py)、[精简包](../scripts/build_dacomp_slim_packages.py)、[raw 核对与命令静态扫描](../scripts/audit_dacomp_raw.py)、[差异清单](../scripts/write_dacomp_raw_differences.py)、[验证](../scripts/validate_dacomp_slim.py)。临时文件仅在 data/013_*，没有数据下载或环境安装。

主要命令（前缀 `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`）：

```text
scripts/prepare_dacomp_slim.py
scripts/audit_dacomp_raw.py
scripts/build_dacomp_slim_packages.py
-m unittest scripts/test_dacomp_raw_scan.py -v
scripts/write_dacomp_raw_differences.py
scripts/validate_dacomp_slim.py
scripts/write_dacomp_slim_report.py
```

## 不确定或没查到的

没有比较 raw 单元格内容；相同表结构与行数不证明单元格内容相同。静态扫描不证明动态拼接的目标、脚本历史运行版本或 SQL 分支执行，原轨迹未留存的内容不补写。3 份精简包中必须保留的命中原句已超过长度目标，均保持原文并报告实际字符数，没有截断。没有自行判断 raw 操作是否正确，也没有自行改变用户提供的复核分类。

## 建议的下一步

用户和 Claude 可使用精简版试标，需要更长证据时按 S 编号回到原文件或 012 完整包；raw 差异和命令语法记录可单独对照。后续如何解释这些记录由用户和 Claude 决定。
'''
    path=ROOT/'notes/013_2026-10-29_精简材料包与原始数据改动检查.md';path.write_text(text);print(path)


if __name__=='__main__':main()
