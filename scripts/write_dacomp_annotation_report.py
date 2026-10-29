"""Write the task 012 delivery report from the audited mechanical records."""

from collections import Counter
import json

from complete_dacomp_comparisons import ROOT,RECORDS
from reconcile_dacomp_scope import jsonl


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(map(str,headers))+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,row))+' |' for row in rows])


def main():
    statuses=json.loads((RECORDS/'012_status_summary.json').read_text());sampling=json.loads((RECORDS/'012_sampling.json').read_text())
    packages=json.loads((RECORDS/'012_package_inventory.json').read_text());formats=json.loads((RECORDS/'012_format_summary.json').read_text())
    verified=json.loads((RECORDS/'012_validation.json').read_text());inputs=json.loads((RECORDS/'012_input_schema_checks.json').read_text())
    sample_rows=[]
    for p in packages:
        sample=next(s for s in sampling['samples'] if s['task']==p['task'])
        link=f"[MD](../records/012_packages/{p['stem']}.md) / [JSON](../records/012_packages/{p['stem']}.json)"
        basis='011 '+str(sample['candidate_date']) if sample['difference_basis_kind']=='date_aligned_011' else '007/009 原差异'
        sample_rows.append([p['task'],p['layer'],p['table'],basis,p['markdown_characters'],p['json_characters'],link])
    format_rows=[]
    for r in formats['tables_summary']:
        s=r['summary'];format_rows.append([r['task'],r['table'],r['whole_match_level_original'],s['changed_columns'],
            s['column_first_cleared_levels'].get('L1',0),s['column_first_cleared_levels'].get('L2',0),
            s['columns_declared_in_contract'],s['columns_with_description'],s['columns_with_column_block_precision_format_text']])
    extended=[p for p in packages if p['full_target_steps_exceed_60000']]
    missing=[p['task'] for p in packages if not p['result_md_present']]
    docs=[json.loads((RECORDS/'012_packages'/(p['stem']+'.json')).read_text()) for p in packages]
    explicit_truncation=sum(o['truncation']['status']=='原记录显式截断' for d in docs for step in d['trace_excerpts']['steps'] for o in step['outputs'])
    tagged=Counter(r['evidence_marker'] for r in statuses['date_changes'])
    protected='、'.join('/'.join(k) for k in verified['protected_L0_gold_L3_agent_tables_still_pending']) or '无'
    input_rows=[]
    for t in inputs['tasks']:
        name='app_session_standard_daily' if t['task']=='impl-019' else 'zuora_invoice_data'
        raw=t['agent_output_raw_vs_011_initial'];target=next(r for r in raw['tables'] if r['table']==name)
        input_rows.append([t['task'],t['same_start_file_sha256'],t['retained_start_vs_011_initial']['all_raw_schemas_equal'],
            name,len(target['right_columns'] or []),len(target['left_columns'] or [])])
    text=f'''# DAComp DE-Impl：最终待标注清单与试标材料包

## 任务

按 2026-10-29 修订规则，在 009 更正状态之外生成 012 状态文件；固定种子抽取每题 1 张待标注表，整理 30 份原文材料包；核对 19 张格式差异表的契约、实际类型和值样例；附查 011 两张执行失败表的输入库结构。仅整理原文与机械统计，不推测原因，不进行人工归因，不执行 agent / gold 节点 SQL。

## 结论

状态共 **1,069 行**；**日期差异 34 张、剩余待标注 283 张**，与用户给出的核对数一致，没有数量差异。004–011 的原记录和原始文件保持原样。

{table(['012 状态','表数'],[[k,v] for k,v in statuses['statuses'].items()])}

固定 `random.Random(20261029)`，按题号升序、题内按 `(layer, table)` 排序后依次 `choice`，得到下列 30 张。层分布为 **staging 23 / intermediate 4 / marts 3**。字符数是文件解码为 UTF-8 后的 Python `len`，不是字节；MD 与 JSON 表达同一组内容，格式开销不同。60,000 字符规则只用于轨迹命令 / 输出部分，不是整个材料包的长度上限。

{table(['题目','层','抽中表','差异依据','MD 字符','JSON 字符','材料包'],sample_rows)}

19 张格式差异表共提取 **40 个在 L1 / L2 消除差异的列**：40 列有契约列定义，**22 列有 description**，19 列的列块出现 precision / rounding / format / cast 等文字或显式带 scale 的类型声明。下面逐表列出，完整原文、实际类型和最多 5 组原始值对照在 [012_format_contracts.jsonl](../records/012_format_contracts.jsonl)。这些数字只描述文字是否出现，不判断是否违反契约。

{table(['题目','表','整表档位','差异列','L1 消除','L2 消除','契约有定义','有 description','列块有精度/格式等文字'],format_rows)}

## 详细发现

### 1. 新状态规则与逐表依据

[012_statuses.jsonl](../records/012_statuses.jsonl)和 [CSV](../records/012_statuses.csv)各 1,069 行，保留 `status_009`、新状态、规则依据、证据标记、来源记录、标注差异来源及所用日期；不覆盖 009 / 010。34 张日期差异中的证据标记分布：`{json.dumps(dict(tagged),ensure_ascii=False)}`。

- 在该表已验证日期，或该表日期未能验证但同题其他表验证过的日期，011 整表达到 L0/L1/L2，转“日期差异”。未验证该表日期时，同题支持表逐张列在 `same_task_date_witness_tables`。
- gold 仅日期层面验证，且在该表验证日期上 agent 整表达到 L0–L3，也转“日期差异”，全部加“日期层面证据”。
- gold 已 L0 验证、agent 仅 L3 一致时保持待标注。本次相应表为：`{protected}`。
- 修订记录原样记为 **2026-10-29**：日期未验证但同题已验证日期整表 L0/L1/L2 一致的表也转日期差异。该条新增支持了 1 张表，未把“未能验证”的 gold 标签改成已验证。

283 张待标注中，**69 张使用 011 日期对齐后的差异、214 张用原差异**。后者为：未进入 011 的 195 张、该表 gold 日期未验证的 17 张、011 执行失败的 2 张。多个已验证日期时，优先 010 的同题内容候选 / 共同兼容日，再按日期升序选取；每张表都记录选中的日期。原差异的 L0 计数直接引用 004 / 005 / 009，L3 及档位引用 007 / 009。

009 中 12 张 impl-002 表逐条沿用 010 的 `official_failed_replay_equal` 及完整注记 **“官方评分为失败，复比一致”**。它们没有重新解释成普通官方通过。

### 2. 抽样与材料包内容

[012_sampling.json](../records/012_sampling.json)保存种子、算法、每题候选表数、抽中位置和文件名。抽样实现为 [prepare_dacomp_annotation.py](../scripts/prepare_dacomp_annotation.py)，全程使用一个 Random 实例，没有逐题重置种子。

每包均包括完整表规格及行号、agent 最终 SQL 全文、标为“仅供定位差异”的 gold SQL 全文、选定差异来源、两侧行数与独有键计数 / 最多 10 个键样例、每个比较列的 L0 / L3 计数及最多 5 个 L0 样例键组、006 agent 约束检查、008 完整扫描记录、逐步原命令 / 输出、result.md 原句和原始位置清单。

值保留 DuckDB `CAST AS VARCHAR` 的原文字面表示，不做 trim、大小写或数值改写。键仍用历史 L0 规范化；重复键记录同键的值 / 次数，明确不是按列表位置配成唯一行。没有共同键时不虚构值对照；旧 L0 的 0 个观测行对不表示两侧值相同，L3 无法比较时保留 null。材料包不概括轨迹，也没有新增原因推测。

### 3. 轨迹选择、截断和原文边界

按 008 B7 的实际读取源表清单，以标识符完整词边界匹配本表名、源表全名或裸表名；只要命令或其关联输出命中，即纳入该步骤。原生 `event_id`、agent 命令序号、JSON 文件 / 字段 / 行号和 archive member 都保留。共核对 {verified['complete_trace_step_selection_verified']} 个相关步骤，没有只挑部分命中步骤。

命令 / 输出合计超过 60,000 字符时，完整保留含本表名的步骤，源表单独命中的其余步骤只列编号、位置、首行和截断元数据，不改写原文。有 {len(extended)} 包仅完整本表步骤就超过 60,000 字符；按“优先完整保留”的要求保留，并显式标出，而不是截去该步内容：

{table(['题目','完整保留轨迹字符','仅索引的源表步骤数'],[[p['task'],p['trace_kept_full_characters'],p['source_only_steps_indexed']] for p in extended])}

原记录显式截断标记共 {explicit_truncation} 处，包内保留其原文及“原记录显式截断”标记；未出现标记的输出记“未见显式截断标记”，不声称可以恢复记录外内容。材料包的索引化与原记录自带截断分开标记。

result.md 在 impl-015 / 022 的 `workspace/` 中，已按真实路径摘录。未找到 result.md 的题为 **{', '.join(missing)}**，已核对递归路径和 008 archive inventory；不以 result.json 的指令或输出代替 result.md。其余有 result.md 但未提本表名时，句子列表为空。摘录不限 008 关键词，能对应到 008 D10 的句子另附原 excerpt id。

### 4. 格式差异表的契约核对边界

19 张全部暂记“格式差异（待核契约）”。40 列的完整列块包括名称、类型、description / constraints 等原文，并附文件与行号；实际类型来自原预测结果和留存 gold。列块内相关文字与“同一表规格原文行同时含列名和精度等关键词”的上下文分开记录，后者不表示已确定该行文字适用于该列。相关文字检索模式保存在脚本常量 `PRECISION`，只做机械提取。

impl-028 `youtube__age_demographics_pivot` 为特殊原记录：007 的官方 L0 为 false、精确行元组 L0 为 true、共同键首档为 L0。本次共同键列差异数为 0，故没有列可以列为“在 L1 消除”；没有补造列差异，也没有更改其状态或判断原评分的原因。

### 5. 两张执行失败表的输入库结构

已核实 agent 工作目录留存的 `*_start.duckdb` 与 011 使用的初始库，**两题均 SHA-256 相同且全部 raw 表结构相同**。同时单列检查留存结果库内的 raw 表，不能把它与起始库混为一份文件：

{table(['题目','start SHA 相同','start raw 结构相同','相关 raw 表','初始库列数','留存结果 raw 列数'],input_rows)}

impl-019 的留存结果 raw 表出现 `app_downloa1d_date`（VARCHAR），相应初始表为 `app_download_date`（DATE）。impl-030 的初始 `zuora_invoice_data` 为 1 个 VARCHAR 列，列名是完整逗号连接的表头；留存结果 raw 表为分开的多列。完整列名 / 顺序 / 类型、其他 raw 表差异、run.py 原文和运行命令位置都在 [012_input_schema_checks.json](../records/012_input_schema_checks.json)。这里只记录结构，不解释 011 异常，不改变结论。所比较的是当前留存输入副本；所查 run_summary / 轨迹索引中没有运行开始时的单独数据库指纹，未用 mtime 补推历史。

## 证据来源

- [全量状态 JSONL](../records/012_statuses.jsonl)、[状态 CSV](../records/012_statuses.csv)、[规则与汇总](../records/012_status_summary.json)、[抽样](../records/012_sampling.json)、[材料包清单与字符数](../records/012_package_inventory.json)。
- [19 表契约与值样例](../records/012_format_contracts.jsonl)、[格式核对汇总](../records/012_format_summary.json)、[输入库结构](../records/012_input_schema_checks.json)。所有材料包见结论中的逐表链接。
- [验证](../records/012_validation.json)：独立核对 34 / 283、复现抽样，验证 30 对 MD / JSON 同内容、{verified['complete_SQL_files_verified']} 份 SQL 全文、{verified['archive_source_files_verified']} 份 archive 来源及 {verified['raw_package_value_samples_verified']} 组材料包原始值样例；另核对 {verified['raw_format_samples_and_independent_normalization_verified']} 组格式样例与独立容差规范化。[样例抽取规则测试](../records/012_tests.log)通过。
- [前后完整性](../records/012_input_integrity.json)：{verified['original_input_files_unchanged']} 个原始输入前后大小、mtime、SHA-256 一致，其中 {verified['original_databases_unchanged']} 个数据库。004–011 报告和记录均不改。
- 实现：[状态 / 抽样](../scripts/prepare_dacomp_annotation.py)、[包生成](../scripts/build_dacomp_annotation_packages.py)、[只读样例抽取](../scripts/dacomp_annotation_evidence.py)、[格式契约核对](../scripts/check_dacomp_format_contracts.py)、[输入结构核对](../scripts/check_dacomp_input_schemas.py)、[验证](../scripts/validate_dacomp_annotation.py)。过程命令及日志在 records/012_*；数据库比较中间文件只在 data/012_*，不进 git。没有执行 agent / gold 节点 SQL。

主要命令（使用既有 Python / DuckDB / SQLGlot 环境，前缀 `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`）：

```text
scripts/prepare_dacomp_annotation.py
-m unittest scripts/test_dacomp_annotation_evidence.py -v
scripts/build_dacomp_annotation_packages.py
scripts/check_dacomp_format_contracts.py
scripts/check_dacomp_input_schemas.py
scripts/validate_dacomp_annotation.py
scripts/write_dacomp_annotation_report.py
```

## 不确定或没查到的

未进行人工标注或错误原因判断。gold 日期的既有“未能验证”标签没有因本次状态规则被改写；格式契约文字是否构成约束、输出是否违反契约仍未判断。原轨迹已截断的部分不能恢复，缺失 result.md 的题不补写内容。重复键没有唯一行对应时，只提供值多重集合样例，不声称可以恢复唯一行配对。

## 建议的下一步

由用户和 Claude 使用这 30 份材料包开展试标，并决定标注规范及格式差异表的契约判定。012 清单和材料包可作为独立版本保留，004–011 继续作为原始比较记录。
'''
    path=ROOT/'notes/012_2026-10-29_DAComp待标注清单与试标材料包.md';path.write_text(text);print(path)


if __name__=='__main__':main()
