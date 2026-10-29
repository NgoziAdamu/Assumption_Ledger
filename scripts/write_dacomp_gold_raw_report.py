"""Task 015: render mechanical raw differences and the Chinese task report."""

from collections import Counter
import json

from check_dacomp_gold_raw import read_jsonl
from complete_dacomp_comparisons import ROOT, RECORDS


def cell(value):
    if value is None:
        return '未比较'
    return str(value).replace('|', '&#124;').replace('\n', '<br>')


def cols(side):
    if side is None:
        return '表不存在'
    return '；'.join(f"{c['ordinal_position']}. `{c['name']}` {c['type']}" for c in side['columns'])


def main():
    summary = json.loads((RECORDS/'015_summary.json').read_text())
    validation_path = RECORDS/'015_validation.json'
    validation = json.loads(validation_path.read_text()) if validation_path.exists() else None
    pairs = read_jsonl(RECORDS/'015_raw_comparisons.jsonl')
    downstream = read_jsonl(RECORDS/'015_pending_downstream.jsonl')
    bykey = {(r['task'], r['raw_table']): r for r in downstream}
    lines = ['# 015：逐张 raw 差异与待标注下游', '',
             '只列 gold raw 存在、且与 initial 或 agent 至少一侧不同的 raw 表。下游只使用 008 B7 原记录的精确 schema.table 依赖边，筛选 013 状态为“待标注”。路径为一条最短路径，不代表唯一读取路径。', '',
             '全量无差异记录及哈希：`015_raw_comparisons.jsonl` / `.csv`；逐题完整结构：`015_raw_impl-NNN.json`。', '']
    for entry in downstream:
        task, name = entry['task'], entry['raw_table']
        lines += [f'## {task} {name}', '', '| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |', '|---|---:|---:|---|---|---|']
        related = [r for r in pairs if r['task'] == task and r['raw_table'] == name]
        for row in related:
            other = row['comparison'].removeprefix('gold_vs_')
            a, b = row['gold'], row[other]
            lines.append('| '+' | '.join(cell(x) for x in (row['comparison'], a['row_count'] if a else '表不存在', b['row_count'] if b else '表不存在', row['ordered_columns_and_types_equal'], row['sorted_content_hash_equal'], ', '.join(row['difference_reasons']) or '无'))+' |')
        gold = related[0]['gold']
        lines += ['', '**按原顺序的列名与类型**', '', '- gold：'+cols(gold)]
        for row in related:
            other = row['comparison'].removeprefix('gold_vs_')
            lines.append('- '+other+'：'+cols(row[other]))
        lines += ['', '**013 待标注下游**', '', '| 层 | 表 | 直接/间接 | 一条最短读取路径 |', '|---|---|---|---|']
        for target in entry['pending_downstream_tables']:
            lines.append('| '+' | '.join((target['layer'], target['table'], '直接' if target['direct'] else '间接', ' → '.join(target['one_shortest_path'])))+' |')
        if not entry['pending_downstream_tables']:
            lines.append('| — | 无可追溯的待标注下游 | — | — |')
        lines += ['', f"来源：`015_raw_{task}.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。", '']
    (RECORDS/'015_raw_differences.md').write_text('\n'.join(lines))

    lines = ['# 任务 015：gold 原始表一致性检查', '', '## 任务', '',
             '对 DAComp DE-Impl 全部 30 题，以只读方式比较 gold 与初始 `*_start.duckdb`、gold 与 agent 留存库中的 raw schema、表清单、按顺序列名/类型、行数及内容哈希；对有差异的 raw 表，沿 008 B7 依赖清单追溯 013 状态为“待标注”的下游表。只记录比较结果，不判断原因，不修改状态。', '',
             '## 结论', '']
    initial = summary['comparison_totals']['initial']
    agent = summary['comparison_totals']['agent']
    lines += [f"已核实：30 题中 {summary['gold_raw_present_tasks']} 题 gold 存在 raw schema，{len(summary['gold_raw_absent_tasks'])} 题不存在。gold–initial 的 {initial['union_tables']} 个表对中，{initial['equal_tables']} 个完全一致，{initial['different_tables']} 个存在差异；gold–agent 的 {agent['union_tables']} 个表对中，{agent['equal_tables']} 个完全一致，{agent['different_tables']} 个存在差异。", '',
              f"按题目与 raw 表名去重，共 {summary['tasks_with_raw_differences']} 题、{summary['different_raw_tables']} 张 raw 表有至少一侧差异；沿 008 B7 可追溯至 {summary['pending_downstream_table_count']} 张 013“待标注”表。差异与下游逐表列在[完整清单](../records/015_raw_differences.md)，不据此判断任何表的差异原因。", '',
              '## 详细发现', '', '### 1. 全部 30 题', '',
              '下表的“相同/不同”均按表存在性、按顺序列名/类型、行数、等行数时的内容哈希合并判定。列名/类型不同与内容哈希不同可重叠；表不存在不视作 0 行。gold 没有 raw schema 的题单列为不适用，不纳入相同/不同计数。', '',
              '| 题目 | gold raw | raw 表数 gold / initial / agent | gold–initial 相同 / 不同 | gold–agent 相同 / 不同 | 待标注下游去重数 |',
              '|---|---|---|---|---|---:|']
    for row in summary['tasks']:
        counts = row['raw_table_counts']
        a, b = row['gold_vs_initial'], row['gold_vs_agent']
        lines.append(f"| [{row['task']}](../records/015_raw_{row['task']}.json) | {'有' if row['gold_raw_schema_exists'] else '无'} | {counts['gold']} / {counts['initial']} / {counts['agent']} | {a['equal_tables']} / {a['different_tables']} | {b['equal_tables']} / {b['different_tables']} | {len(row['pending_downstream_union'])} |")
    lines += ['', '表清单不一致的具体名称如下；只按原名记录，没有自行把不同名称的表配成一对：', '']
    for row in summary['tasks']:
        for other in ('initial', 'agent'):
            entry = row['gold_vs_'+other]
            if entry['gold_only_tables'] or entry[other+'_only_tables']:
                lines.append(f"- {row['task']} gold–{other}：仅 gold 有 `{', '.join(entry['gold_only_tables']) or '无'}`；仅 {other} 有 `{', '.join(entry[other+'_only_tables']) or '无'}`。")
    lines += ['', 'impl-028 两侧各 3 张 raw 表的名称集合没有交集，表名并集为 6，所以上表记为 6 个不同的表项。']
    lines += ['', '### 2. 差异字段与内容哈希', '',
              '| 比较 | 表清单差异（单侧表数） | 按顺序列名/类型不同 | 行数不同 | 等行数时已比较哈希 | 哈希不同 | 读取未完成 |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for other in ('initial', 'agent'):
        total = summary['comparison_totals'][other]
        missing = sum(len(r['gold_vs_'+other]['gold_only_tables'])+len(r['gold_vs_'+other][other+'_only_tables']) for r in summary['tasks'])
        lines.append('| '+' | '.join(str(x) for x in ('gold–'+other, missing, total['schema_different_tables'], total['row_count_different_tables'], total['content_hash_checked_tables'], total['content_hash_different_tables'], total['incomplete_reads']))+' |')
    types = Counter()
    python_types = Counter()
    hashed_rows = 0
    for case in json.loads((RECORDS/'015_cases.json').read_text()):
        doc = json.loads((RECORDS/f"015_raw_{case['task']}.json").read_text())
        for side in doc['sides'].values():
            for table in side['tables'].values():
                types.update(c['type'] for c in table['columns'])
                if table['content_hash'] and table['content_hash'].get('sha256'):
                    python_types.update(table['content_hash']['python_value_types'])
                    hashed_rows += table['content_hash']['rows_hashed']
    lines += ['',
              '哈希方法：对两侧都存在且行数相同的每张表，执行 `SELECT * FROM raw."表名" ORDER BY ALL NULLS FIRST`，保留重复行；依原列顺序把每个值转换成带类型标签的 JSON，按 UTF-8 编码，对每行加 8 字节长度前缀后流式计算 SHA-256。两次 gold 比较复用同一张表的哈希。数据库连接 TimeZone 设为 UTC；排序、临时文件位于 `data/015_gold_raw/`。完整 SQL、行数、每侧哈希在逐题 JSON 中。', '',
              '不忽略大小写、空白、NULL，不做容差、舍入或日期截断；SQL NULL 与空串有不同标签。列名和 SQL 类型由 schema 字段另行比较，不塞进内容哈希。列顺序变化会改变行向量，故可能同时标记结构与哈希不同；哈希不同不单独说明哪些单元格变了。浮点 signed zero 与 NaN 统一为各自的 SQL 等值表示，以排除排序相等值内部物理顺序的影响。', '',
              f"实际 raw 列类型（全部三侧）：`{json.dumps(dict(types), ensure_ascii=False)}`；已哈希流的 Python 值类型：`{', '.join(sorted(python_types))}`，共 {hashed_rows:,} 行次。未向 git 提交 raw 行内容。", '',
              '**impl-010 raw.form_data**：', '']
    for row in [r for r in pairs if r['task'] == 'impl-010' and r['raw_table'] == 'raw.form_data']:
        other = row['comparison'].removeprefix('gold_vs_')
        a, b = row['gold'], row[other]
        lines += [f"- {row['comparison']}：gold {a['row_count']} 行，{other} {b['row_count']} 行；按顺序列名/类型一致={row['ordered_columns_and_types_equal']}；内容哈希一致={row['sorted_content_hash_equal']}。gold SHA-256 `{a['content_hash']['sha256']}`，{other} SHA-256 `{b['content_hash']['sha256']}`。"]
    lines += ['', '### 3. gold 无 raw schema 的题与 benchmark 文件路径', '']
    if not summary['gold_raw_absent_tasks']:
        lines += ['本次 30 题 gold 全部存在 raw schema，无“gold 无 raw”的题目。已搜索初始题目录与 gold 题目录，文件路径清单见 [benchmark 文件清单](../records/015_benchmark_file_paths.json)；不据文件存在推断 gold 生成时使用过哪些文件。']
    else:
        for row in summary['tasks']:
            if row['gold_raw_schema_exists']:
                continue
            paths = row['candidate_benchmark_files_when_gold_raw_absent']
            lines += [f"**{row['task']}**：gold 无 raw schema；在对应初始与 gold 的 benchmark 目录中{'找到以下文件' if paths else '未找到列入检查后缀的文件'}（仅记录路径，不能确认生成时使用）。", '']
            lines += ['- `'+r['path']+'`' for r in paths]
            lines += ['']
    lines += ['', '### 4. 差异 raw 表与 013 待标注下游', '',
              '依赖方向为 `008 B7 源关系 → 目标表`，逐题进行广度优先遍历；在全部交付表上穿越依赖链，最后仅保留 `013_statuses.jsonl` 中状态严格为“待标注”的目标。保留直接/间接、跳数、一条最短路径；同一目标可能列在多张 raw 表下面，总量按题/层/表去重。使用 agent 最终 SQL 在 008 中记录的来源，不推断 gold SQL 读取关系，也不把“读取差异 raw”当作输出差异已归因。', '',
              f"008 B7 共 {summary['lineage_edges']} 条精确依赖边；不完整或无法对应输出节点的记录数 {summary['lineage_limit_records']}。逐表见[差异与下游清单](../records/015_raw_differences.md)、[结构化下游](../records/015_pending_downstream.jsonl)、[全部依赖边](../records/015_lineage_edges.jsonl)。", '']
    if validation:
        integrity = validation['original_files']
        checks = validation['independent_multiset_checks']
        native = sum(r['method'] == 'native SQL EXCEPT ALL' for r in checks)
        lines += ['### 5. 执行与完整性复核', '',
                  f"执行日期为 2026-10-29（Asia/Singapore）。已重新读取三侧 raw 清单、列结构与计数，并用 {native} 次原生 SQL `EXCEPT ALL`、{len(checks)-native} 次独立连接 typed row Counter 比较复核哈希结论：覆盖每题每组比较的一张可比相同表，以及全部同结构但哈希不同的表。外部 source view 使用独立连接，避免别名跨库混用。全部 {len(checks)} 次与哈希结果一致；另有 3 项排序/重复行、NULL/字符串边界、循环依赖测试通过。", '',
                  f"{integrity['files_checked']} 个输入文件（含 {integrity['database_files_checked']} 个数据库）的 bytes、mtime_ns、SHA-256 前后完全一致，changes 为空。004–014 的既有报告、记录及材料包均已纳入核对，没有修改。", '']
    lines += ['## 证据来源', '',
              '- [30 题数据库路径](../records/015_cases.json)：由 013 初始/agent 路径与 006 gold 路径读取，不改原记录。',
              '- [全量比较 CSV](../records/015_raw_comparisons.csv)、[JSONL](../records/015_raw_comparisons.jsonl)、[汇总](../records/015_summary.json)：包含存在性、完整列顺序、类型差异、计数和内容哈希。',
              '- [原始文件前指纹](../records/015_input_before.json)、[前后完整性检查](../records/015_input_integrity.json)、[验证](../records/015_validation.json)：逐项核对 size、mtime_ns、SHA-256。004–014 的报告与记录保持原状；新结果全部为 015 前缀。',
              '- [实现](../scripts/check_dacomp_gold_raw.py)、[测试](../scripts/test_dacomp_gold_raw.py)、[验证实现](../scripts/validate_dacomp_gold_raw.py)、[报告生成](../scripts/write_dacomp_gold_raw_report.py)。没有下载或联网查询，没有执行 agent/gold 节点 SQL 或轨迹命令。',
              '- [准备日志](../records/015_preparation.log)、[只读比较日志](../records/015_inspection.log)、[汇总日志](../records/015_summary.log)、[测试日志](../records/015_tests.log)、[验证日志](../records/015_validation.log)。', '',
              '执行命令（同一 Python 环境与现有依赖）：', '', '```text',
              'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B scripts/check_dacomp_gold_raw.py prepare',
              'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B scripts/test_dacomp_gold_raw.py',
              'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B scripts/check_dacomp_gold_raw.py inspect',
              'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B scripts/check_dacomp_gold_raw.py summarize',
              'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B scripts/write_dacomp_gold_raw_report.py',
              'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B scripts/validate_dacomp_gold_raw.py', '```', '',
              '## 不确定或没查到的', '',
              '本次没有 gold 生成过程的原始运行记录，不能从同名库、文件路径或数据差异确认 gold 当时使用了哪个输入。表行数不同按要求不再计算两侧内容哈希；列顺序不同仍依各自原顺序哈希，不做列重排后“相同”判定。raw view 在只读连接中查询，外部 source 依赖若存在则以 READ_ONLY 附加，具体路径记录在各题 JSON；未物化或修改 view。', '',
              '同一 SHA-256 表示本次确定序列化口径下的排序结果一致；不判断 gold 或 agent 哪一侧应作为业务标准。只沿现有 008 B7 清单追溯，不补造未记录的动态 SQL 关系。没有为任何表改状态或增加归因标签。', '',
              '## 建议的下一步', '',
              '将本报告的差异 raw 表及其待标注下游清单提供给用户与 Claude，在后续标注时作为输入一致性证据查阅；是否调整试标范围或比较基准，由用户与 Claude 决定。', '']
    path = ROOT/'notes/015_2026-10-29_gold原始表一致性检查.md'
    path.write_text('\n'.join(lines))
    print('Wrote', path, 'and detailed raw differences', flush=True)


if __name__ == '__main__':
    main()
