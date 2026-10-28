"""Write the task 011 Chinese delivery report from its structured records."""

from collections import Counter
import json

from complete_dacomp_comparisons import ROOT, RECORDS
from reconcile_dacomp_scope import jsonl
from finalize_dacomp_agent_dates import GOLD, OUTCOMES


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(map(str,headers))+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,r))+' |' for r in rows])


def main():
    summary=json.loads((RECORDS/'011_summary.json').read_text());selection=json.loads((RECORDS/'011_selection.json').read_text())
    entries=jsonl(RECORDS/'011_table_alignment.jsonl');validation=json.loads((RECORDS/'011_validation.json').read_text())
    stats=summary['tables_by_gold_verification'];trials=summary['attempts_by_gold_verification']
    headers=['010 gold 验证结果','表数','L0/L1/L2 匹配','仅 L3 匹配','缩小但仍不匹配','数字无变化且仍不匹配','其他变化 / 数字不可直接比较','不可比较','有退化标记']
    rows=[]
    for g in GOLD:
        s=stats[g];rows.append([g,s['total'],*[s[o] for o in OUTCOMES],s['有退化标记']])
    rows.append(['合计',len(entries),*[sum(stats[g][o] for g in GOLD) for o in OUTCOMES],sum(stats[g]['有退化标记'] for g in GOLD)])
    bytask=[]
    for task in sorted({r['task'] for r in entries}):
        group=[r for r in entries if r['task']==task];counts=Counter(r['aggregate']['outcome'] for r in group)
        bytask.append([task,len(group),','.join(group[0]['dates']),*[counts[o] for o in OUTCOMES]])
    ambiguous=[]
    for task in ('impl-009','impl-022','impl-025','impl-028','impl-030'):
        group=[r for r in entries if r['task']==task]
        if not group:ambiguous.append([task,'无进入本次范围的表',0,'—','—','—','—']);continue
        for day in group[0]['dates']:
            attempts=[a for e in group for a in e['attempts'] if a['candidate_date']==day];levels=Counter(a.get('after',{}).get('whole_match_level') or '不可比较' for a in attempts)
            ambiguous.append([task,day,len(attempts),sum(levels[l] for l in ('L0','L1','L2')),levels['L3'],levels['仍不匹配'],levels['不可比较']])
    deg=[(e,a) for e in entries for a in e['attempts'] if a.get('degeneracy',{}).get('flagged')]
    zero=sum(any(a.get('degeneracy',{}).get('both_zero_rows') for a in e['attempts']) for e in entries)
    constant=sum(any(a.get('degeneracy',{}).get('clock_output_degeneracy') for a in e['attempts']) for e in entries)
    failed=summary['execution_failures']+summary['comparison_failures']
    failures='\n'.join(f"- {f['task']} / {f['table']} / {f['date']}: `{str(f.get('exception') or f.get('status')).splitlines()[0]}`" for f in failed) or '143 次目标执行与比较均完成，没有执行或比较异常。'
    starts=[a['started_at']['Asia/Singapore'] for e in entries for a in e['attempts']];ends=[a['finished_at']['Asia/Singapore'] for e in entries for a in e['attempts']]
    text=f'''# DAComp DE-Impl：agent SQL 日期对齐重跑

## 任务

核对 009 更正状态为“待标注”、008 C9 中 agent SQL / gold SQL 均命中运行时间写法的表，按 010 的日期固定 agent SQL 后只执行该节点。核实范围为 **{len(entries)} 张、{selection['tasks']} 题**，与用户预期 122 张一致；所有命中均有 SQL code 位置，不是仅注释命中。

staging 从原始初始库的私有副本执行，其他层在 gold 私有副本中使用 gold 上游。执行时段为 `{min(starts)}` 至 `{max(ends)}`（Asia/Singapore）。未重跑 gold SQL，未重算得分，004–010 的报告、记录和既有状态均不改。

## 结论

以下按 **122 张表**统计，并按 010 中该表的 gold 验证结果分开列出。日期不唯一的表在各日期分别执行后，在本表汇总中取“至少一个试验日达到的最佳匹配档位”，每张只计一次；没有据此选择真实生成日期。逐日期结果另外保留，共 **{summary['attempts']} 次**。

{table(headers,rows)}

最佳整表首次匹配档位的详细分布：`{json.dumps(summary['best_observed_whole_levels'],ensure_ascii=False)}`。退化标记可与匹配 / 不匹配结果重叠，不是额外的互斥类别，也不改变任何旧状态。

若“没有变化”不限整表档位，而按全部试验日的差异数字都没有变化统计，三组分别为：`{json.dumps(summary['all_dates_numeric_unchanged_tables_by_gold_verification'],ensure_ascii=False)}`。这一口径可能与“仅 L3 匹配”等列重叠，另列以便区分。

“缩小”采用严格的逐项口径：绝对行数差、两侧独有键数，以及 L0 / L3 每列的不一致计数和残余值出现次数，全部可比较且均不增加、至少一项减少。部分减小且部分增大、或有数字无法直接比较时，归入本次结果的“其他变化 / 数字不可直接比较”列；这里只描述数字，不作错误原因判断。

## 详细发现

### 1. 日期与范围

[011_selection.json](../records/011_selection.json)逐表保留 009 状态、008 来源文件、007 / 009 的比较列与键、010 的原样 gold 验证标签、日期列表及引用路径。122 张中 gold L0 验证 53 张、仅日期验证 51 张、未能验证 18 张；后者仍按任务要求执行，并保留“未能验证”标签。

010 的 gold 验证比较全部 gold 输出列，日期层面验证没有数值放宽；本次 agent 比较使用历史官方比较列与 L0–L3。两者用途和列范围不同，010 标签仅原样引用，没有用本次 agent 结果重新判定它。

有内容支持候选日的题使用 010 的 `inferred_content_supported_candidates`。5 题无法唯一定日时，使用 010 的 `all_successful_trial_dates` 全集，逐日执行；其中某些早期试验日仅兼容该题部分 gold 节点，故同时记录 `date_in_task_shared_compatible_dates_010` 和 `date_validated_for_this_gold_table_010`，不把全集误称为全题共同日期。impl-009 没有表进入本次范围。

{table(['题目','候选日','表 / 次数','L0–L2','仅 L3','仍不匹配','不可比较'],ambiguous)}

{summary['single_date_tables']} 张表只执行一个日期，{summary['multiple_date_tables']} 张表执行多个日期。日期不同导致本次结果类别或首次整表匹配档位不同的表有 {len(summary['tables_with_date_dependent_outcomes'])} 张，清单在 [011_summary.json](../records/011_summary.json)。

### 2. 替换与输入

复用 010 的 `freeze_sql`，按原始字节读取 SQL 并仅替换真正的运行时 token；CURRENT_DATE / TODAY 类替换为 DATE 字面量，CURRENT_TIMESTAMP / NOW 等替换为该日 **00:00:00 UTC 的 TIMESTAMPTZ**。时刻未知，午夜是占位，不表示恢复了历史时刻或时区。每次记录原文、文件、行列、offset、替换文本及替换前后 SHA-256。注释、字符串和标识符不替换。

原 SELECT 本体除这些位置外不改任何字节，仅增加外层 `CREATE OR REPLACE TABLE <target> AS`。与官方 CS 的差别是：不调用会 trim / 去分号 / 补 schema 的 `_process_sql`，以满足本任务的字节保留要求；输入仍按 CS 使用 gold。已有目标 view 先在私有副本中移除，兼容 005 / 009 的处理。没有执行 agent 的 run.py 或其他节点。

staging 的原始输入来自 003 已记录的初始 `*_start.duckdb`；其他层每题复制留存 gold，每次执行前后将当前目标复原，其余关系始终保留 gold 内容。impl-013 的外部 raw source 按既有 dependency adapter 以 READ_ONLY 连接。所有 SQL 进程通过 bwrap 将原项目 / 本仓库只读挂载，关闭网络，只开放各自 data/ 私有工作目录写入，并使用 scrubbed_env。

首次实现中，结果快照复制遇到私有 DuckDB 文件句柄冲突，已改为关闭执行连接后只读复制结果，并从新的工作目录重跑；初步不完整输出未计入本报告。[修正记录](../records/011_implementation_correction.json)。这不涉及原始库修改。

### 3. 对齐前后数字与比较口径

[011_date_alignment.csv](../records/011_date_alignment.csv)每张表 / 每个日期一行，共 {summary['attempts']} 行；[011_table_alignment.jsonl](../records/011_table_alignment.jsonl)每张表一行，共 {len(entries)} 行，包含全部日期尝试。两者都有对齐前后行数、行数差、两侧独有键数 / 共同键数、L0 与 L3 每列不一致数、首次整表 / 共同键匹配档位。逐题 `011_alignment_impl-NNN.json`另含替换和完整机械记录。

对齐前的行数、键数、档位和 L3 逐列计数直接复制 007 / 009，未重算；L0 逐列计数从其所引用的 004 / 005 / 009 原始表记录直接复制，并保留独立来源。对齐后的键列和比较列固定使用这些记录，不重新选键。重复键按原方法比较每个键内的值多重集合，不虚构逐行配对，计数保留 `minimum_value_mismatch_pairs` 语义；没有共同键时 L3 逐列计数为未知。旧口径 L0 此时保留“观测到 0 个不一致行对”，只表示没有行对可比，不是值一致。

L0 整表结论使用官方的 LOWER / TRIM / CAST AS VARCHAR / SQL NULL→字符串 null 及 MD5(CONCAT_WS('|',...)) 行多重集合；同时另存精确行元组结论。L1 统一可解析数值 / 布尔值，L2 再作 Decimal 两位舍入（负数中点远离 0），L3 再仅比较 ISO 日期部分。L3 **丢弃时间部分**。L1–L3 整表需行数相同且行多重集合一致；共同键内比较另列，不能代替整表匹配。口径沿用 007，没有扩展比较列。

逐题表数与结果如下；多日期题按本报告上述“最佳观察结果”只计一次。

{table(['题目','表数','日期','L0–L2','仅 L3','缩小仍不匹配','数字无变化仍不匹配','其他变化','不可比较'],bytask)}

### 4. 退化标记

有退化标记的不同表共 {sum(stats[g]['有退化标记'] for g in GOLD)} 张；两边均 0 行 {zero} 张，运行时间相关输出列在两边均为全 NULL 或单一非 NULL 值 {constant} 张，二者可重叠。逐个输出列的 NULL 数、不同非 NULL 值数及单一值保留在 `degeneracy.clock_output_columns`；也注明该列是否在历史比较列集合中。

另有 {summary['tables_with_unavailable_degeneracy_check']} 张表缺少成功结果，形态检查记未知，不作“没有退化标记”的结论。

时间相关输出列通过 SQLGlot 的输出值 lineage 沿本节点 CTE / 子查询抽取，只有过滤条件含时钟不会把全部输出列标为时间相关。NULL 与非 NULL 混合、即使非 NULL 仅一种值，也不算整列单一值；0 行的列不作全 NULL 断言，单一值要求非空表且全列非 NULL（包含 1 行表）。标记描述对齐后的输出形态，不能据此证明它相较对齐前才发生变化，也不能据此判断差异原因。未解析的输出 lineage 数为 {summary['unresolved_lineage_outputs']}。

impl-013 的两列未命名 CAST 输出在 DuckDB 与 SQLGlot 中的自动名称不同，已按输出顺序为分析 AST 临时加别名完成抽取；只更新 lineage / 形态标记，没有再次执行 agent SQL，也没有改比较数字。[抽取补齐记录](../records/011_lineage_refinement.json)。该临时别名从未用于执行 SQL。

### 5. 执行完整性与异常

{failures}

{validation['original_input_files_unchanged']} 个原始输入文件前后大小、mtime、SHA-256 一致，含 {validation['original_databases_unchanged']} 个数据库；004–010 的所有既有记录与报告保持原样。{validation['attempts_audited']} 次尝试、{validation['replacement_spans_audited']} 处替换全部通过原文重建核对。另挑 {len(validation['independent_replays'])} 个小规模代表节点，在新的私有副本重放，并用独立 Counter / Decimal / 日期解析复核 L0–L3、键数和逐列计数；结果均一致。

## 证据来源

- [范围与对齐前数字](../records/011_selection.json)、[逐表 JSONL](../records/011_table_alignment.jsonl)、[逐日期 CSV](../records/011_date_alignment.csv)、[总汇总](../records/011_summary.json)、[逐次摘要](../records/011_trial_summary.json)。
- [执行命令及工作目录](../records/011_execution.json)、[原始输入前指纹](../records/011_input_before.json)、[前后完整性](../records/011_input_integrity.json)、[验证](../records/011_validation.json)、[规则测试](../records/011_tests.log)。每题另存执行日志。
- 来源保持原样：[007 比较记录](../records/007_tolerance_tables.jsonl)、[009 补比记录](../records/009_tolerance_tables.jsonl)、[009 更正状态](../records/009_corrected_statuses.jsonl)、[008 扫描](../records/008_table_scan.jsonl)、[010 日期与逐表 gold 验证](../records/010_table_verification.jsonl)、[010 逐题日期](../records/010_task_summary.json)。
- 实现：[重跑](../scripts/align_dacomp_agent_dates.py)、[汇总](../scripts/finalize_dacomp_agent_dates.py)、[独立验证](../scripts/validate_dacomp_agent_dates.py)。完整冻结 SQL、数据库副本和比较中间文件仅在 data/011_*，不进 git。Python / DuckDB 使用既有环境，未安装新依赖。

主要命令（前缀为 `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`）：

```text
scripts/align_dacomp_agent_dates.py --prepare-only
-m unittest scripts/test_dacomp_agent_date_alignment.py -v
scripts/align_dacomp_agent_dates.py --jobs 2
scripts/repair_dacomp_date_lineage.py
scripts/finalize_dacomp_agent_dates.py
scripts/validate_dacomp_agent_dates.py
scripts/write_dacomp_agent_date_report.py
```

## 不确定或没查到的

010 未能唯一确定的日期仍然未知；仅某个兼容日重跑一致不能提升为真实日期。18 张表的 gold 验证标签仍是“未能验证”，本次结果没有改变这一事实。历史时刻与会话时区仍未恢复，timestamp 使用午夜 UTC 的限制沿用 010。

对齐前没有保存 L1 / L2 的逐列计数，因此没有补算或补写这些旧数字；两侧提供已有的 L0 / L3 逐列计数及四档整表 / 共同键结果。没有共同键时不能断言共同键内逐列相同。上述结果只描述本次固定日期重跑后的数字，不构成错误原因判断。

## 建议的下一步

由用户和 Claude 决定如何使用逐日期结果、gold 验证分组和退化标记。本次没有修改 009 / 010 状态，也没有据重跑结果新增错误归因。
'''
    path=ROOT/'notes/011_2026-10-29_DAComp日期对齐重跑.md';path.write_text(text)
    print(path)


if __name__=='__main__':main()
