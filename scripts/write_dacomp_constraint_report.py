"""Render report 006 from verified constraint declarations and read-only counts."""

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT/'records'/name).read_text())


def main():
    summary=load('006_contract_summary.json');validation=load('006_validation.json');integrity=load('006_input_integrity.json')
    tasks=[load(f'006_contract_impl-{n:03d}.json') for n in range(1,31)]
    rows=[r for t in tasks for r in t['tables']]
    assert validation['passed'] and integrity['unchanged']
    overall=summary['summary']['any']
    text=f'''# DAComp DE-Impl：30 题契约约束检查

## 任务

对 30 题契约定义的全部表抽取 grain、primary_key、unique、not_null，涵盖 constraints 和 tests 两种写法；直接检查 agent 自己的留存预测库和 gold 库。记录声明粒度/主键的重复键组、组内行数、SQL NULL 和 unique 重复情况。只检查与统计，不判断错误原因。日期：2026-10-27，Asia/Singapore。

## 结论

已核实：契约共有 **{summary['table_definition_entries']:,} 处定义、{summary['tables']:,} 张不同表**，覆盖全部 30 题；每张表都已写入 [JSONL](../records/006_contract_checks.jsonl) 和 [CSV](../records/006_contract_checks.csv)，每表一行。重复出现的定义保留全部来源，相同约束只检查一次。

按下述口径确认，agent 有 **{overall['agent']['violating_tables']} 张表、{overall['agent']['violating_tasks']} 题**违反至少一项请求检查的约束；gold 有 **{overall['gold']['violating_tables']} 张表、{overall['gold']['violating_tasks']} 题**；**{overall['both_violating_tables']} 张表两边都违反至少一项**。这是已确认的违反数；缺表、缺列和无法解析的 grain 均保留为未知，不算通过，也不自动算违反。下表按约束类型分别统计。

两侧各有 **{summary['missing_tables']['agent']} 张契约表不存在**，缺表集合相同；不存在的表行数记为 JSON null / CSV 空值。**{integrity['files_checked']} 个原始输入文件**的大小、mtime、SHA-256 在检查前后完全一致。{len(validation['independent_sql_checks'])} 项独立 SQL 抽查、2,859 处约束来源核对、11 项测试全部通过。本次没有运行 agent、run.py 或节点 SQL 文件，也没有生成新的评分。

## 详细发现

### 1. 按类型汇总

“声明表数”指至少声明了该类约束的不同表数；“题数”按任务去重。“两边都违反”要求同一张表在两侧该类检查均有已确认违反，不要求是同一列。同一表可能违反多类约束，各行不能相加作为总表数。

| 约束类型 | 声明表数 | agent 违反表数 | agent 题数 | gold 违反表数 | gold 题数 | 两边都违反的表数 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
'''
    labels={'grain':'粒度 grain','primary_key':'主键 primary_key','not_null':'not_null','unique':'unique','any':'至少一类（表的并集）'}
    for kind in ('grain','primary_key','not_null','unique','any'):
        s=summary['summary'][kind]
        text+=f"| {labels[kind]} | {s['declared_tables']} | {s['agent']['violating_tables']} | {s['agent']['violating_tasks']} | {s['gold']['violating_tables']} | {s['gold']['violating_tasks']} | {s['both_violating_tables']} |\n"
    text+='''
下表将“已完成该类全部声明且未发现违反”和“尚不能判定”分开。某张表若已有一个明确违反项、另有缺列导致其他项未知，仍计入已确认违反表数；每条检查和 complete 标志保留在记录中。

| 类型 | agent 已检查且无违反 | agent 未能判定 | gold 已检查且无违反 | gold 未能判定 |
| --- | ---: | ---: | ---: | ---: |
'''
    for kind in ('grain','primary_key','not_null','unique','any'):
        s=summary['summary'][kind]
        text+=f"| {labels[kind]} | {s['agent']['checked_no_violation_tables']} | {s['agent']['unknown_tables']} | {s['gold']['checked_no_violation_tables']} | {s['gold']['unknown_tables']} |\n"
    text+=f'''
总体并集的声明表数为 {overall['declared_tables']}；其余 {summary['tables']-overall['declared_tables']} 张表没有声明这四类中的任何一类，仍记录存在性和行数，不虚构约束。汇总结果保存在 [summary JSON](../records/006_contract_summary.json)。

### 2. 全部表的范围与重复定义

本次按契约选表，不按得分或匹配标记筛选。agent 侧直接使用 `20261025_de_official_batch_01/impl-NNN/agent/dacomp-de-impl-NNN/` 中的留存数据库；gold 使用 `benchmarks/dacomp-de-gold/dacomp-de-impl-NNN/` 的数据库。数据库名只从官方配置读取，不用配置决定哪些契约表参与检查。

| 契约层 | 不同表数 |
| --- | ---: |
'''
    for layer,count in summary['layers'].items():text+=f'| {layer} | {count} |\n'
    text+='''
impl-010 的 marketing、sales、service 均在“全部契约表”的范围内。表名按契约原名、所属层查找；只允许 marts/mart 的 schema 别名及 DuckDB 标识符的大小写等价，不根据前缀、相似名称或业务含义换表。相同表名出现在其他 schema 时只记录位置，不直接替代。

impl-020 有两张 intermediate 表各定义了两次：

'''
    for d in summary['duplicate_definitions']:
        paths=[str(x['contract_yaml_path']) for x in d['definitions']]
        text+=f"- `{d['task']} / {d['layer']}.{d['table']}`，定义位置：{'; '.join(paths)}。\n"
    text+='''
重复定义不采用最后一项覆盖：保留所有 definitions 和 source 位置，相同约束合并来源，不同约束分别保留并检查；每张表在汇总中只计一次。[完整契约清单](../records/006_contract_inventory.json)。

### 3. 粒度的解析范围

'''
    status=summary['grain_status']
    text+=f'''不同表中，{status['not_declared']} 张没有 grain；{status['parsed']+status['unparsed']} 张声明了 grain，其中 **{status['parsed']} 张解析出明确列键、{status['unparsed']} 张保留原文并记为未解析**。两处重复定义的 grain 来源也分别保存，所以原始 grain 字段共 619 处。

解析只接受明确的“One row per …”列或列组合（也支持“One validated row per …”）：列名必须在本表契约 columns 中逐字对应，允许逗号、and、per、+、x、× 和外层括号；字段旁的简单来源注释可保留。with/from/where 等限制语保留原文，本次只检查列键唯一性，不执行这些文字描述的过滤规则。

出现额外且无法明确转为列的粒度、自然语言实体名、混合行类型、源记录粒度或明写允许重复的描述时，保留完整原文，不从 ID 命名、主键、SQL、实际库列或业务含义补全。Exactly one row / single-row snapshot 等无法转为列键的描述也记为未解析，不擅自用常量键代替。

[全部 {status['unparsed']} 条未解析 grain 原文](../records/006_unparsed_grains.csv)，每条均包含任务、层、表和未解析标记。所有已解析和未解析 grain 的原文、列和 YAML 来源也在主 JSONL/CSV 中；原始 YAML 行摘录保存在 declarations.grain.sources 中。未解析不会阻止该表独立声明的 primary_key、not_null、unique 检查。

### 4. SQL 检查口径

- **原生值。** 使用表中实际类型的值做 SQL GROUP BY；不额外 lower、trim、round，不把 SQL NULL 换成字符串。空字符串、字面字符串 'null' 不会被当作 SQL NULL。本任务检查契约约束，不调用 CS/CFS 值规范化比较器。
- **粒度。** 只按成功解析的 grain 列检查重复。含 SQL NULL 的相同键组合归为一组；不从 grain 自动新增 not_null 声明。
- **主键。** 对显式 primary_key（表级列组合或列级标记）同时检查重复和任一键列为 SQL NULL 的行数；重复组大于 0 或 NULL 键行大于 0，即记为主键违反。主键隐含的非空检查归在 primary_key 类，不凭空增加显式 not_null / unique 声明。
- **not_null。** 对 constraints/tests 中明确标记的列计 SQL NULL 行数；同时存在两种标记时合并成一次检查并保留两处来源。
- **unique。** 主统计对非 SQL NULL 的值检查唯一性；另同时提供把 NULL 也分组后的重复组数、组内行数，以及含 NULL 的重复组统计。SQL NULL 是否被禁止由 not_null 或 primary_key 单独体现。主汇总的 unique 违反表数使用非 NULL 口径，不混用额外统计。
- **重复数的含义。** duplicate_key_groups 是出现至少两行的不同键组数；rows_in_duplicate_groups 是这些组内的全部行数；excess_duplicate_rows 为各组大小减一之和。三者分别保存，不把“重复行数”含混地写成一个数字。
- **未知。** 缺表、约束列缺失、grain 未解析或查询错误都不写成 0。每项 status 和 violated 均单列；JSON null / CSV 空值表示无法判定。没有任何已知违反、但仍存在未知项时，不将整表判为已通过。

本次所有存在表的行数查询和约束查询均成功，查询错误为 0。gold 有 3 张表缺少 primary_key 所引用的列：impl-017 的 stg_greenhouse__user_email 缺 email，stg_greenhouse__email_address 和 stg_greenhouse__social_media_address 各缺 index；这些主键检查记为未知。其他约束缺列和缺表也逐项列在 [全部未知检查项](../records/006_unknown_checks.csv)。没有根据相似列名替换缺列。

### 5. 逐题并集汇总

下表“违反”指至少一类请求约束已有明确违反；“两边”指两侧各自至少一类被确认违反，可以是不同类型。这些数值只陈列计数，不用于解释得分或错误原因。

| 任务 | 契约表数 | agent 缺表 | gold 缺表 | agent 违反表数 | gold 违反表数 | 两边都违反的表数 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
'''
    for task in tasks:
        tables=task['tables']
        # Use layer/name tuples for per-task intersections, even when names repeat across layers.
        ap={(r['layer'],r['table']) for r in tables if r['agent']['any_constraint_violated'] is True};gp={(r['layer'],r['table']) for r in tables if r['gold']['any_constraint_violated'] is True}
        text+=f"| [{task['task']}](../records/006_contract_{task['task']}.json) | {len(tables)} | {sum(not r['agent']['table_exists'] for r in tables)} | {sum(not r['gold']['table_exists'] for r in tables)} | {len(ap)} | {len(gp)} | {len(ap&gp)} |\n"
    text+='''
### 6. 结构化记录怎么读

`006_contract_checks.jsonl` 每行是一张表，包含 task/layer/table、全部定义位置、declarations，以及 agent/gold 的独立结果；CSV 每表一行，适合排序和筛选。逐题 JSON 另有精确数据库路径、契约 SHA-256、检查开始/结束 UTC 时间。主要字段：

- declarations：grain 原文、解析状态/列；primary_key、unique、not_null 的列与来源。source 包含 YAML 路径、行号和原始字段摘录。
- agent/gold.table_exists、row_count：存在性与实际行数；实际 schema、表名、缺失声明列另列。
- agent/gold.checks：逐项 SQL、重复组/组内行/多余行、NULL 数、status 和 violated。unique 同时有 including_nulls 附加统计。
- categories：每类已检查项数、未知项数、是否确认违反；any_constraint_violated 是四类的并集状态。是否确认违反和是否全部检查完成分别表达。

其他 accepted_values、范围或表达式 tests 原样记录为 other_declared_tests_not_executed；本次不执行任意验证表达式，也不扩展到四类以外的检查。

## 证据来源

'''
    text+=f'''- [每表 JSONL](../records/006_contract_checks.jsonl)、[每表 CSV](../records/006_contract_checks.csv)、[汇总 JSON](../records/006_contract_summary.json)、[契约清单](../records/006_contract_inventory.json)、[未解析 grain 原文](../records/006_unparsed_grains.csv)、[未知项](../records/006_unknown_checks.csv)。逐题完整记录见上表链接。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-NNN/docs/data_contract.yaml`；agent 留存库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-NNN/agent/dacomp-de-impl-NNN/`；gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-NNN/`。文件名从官方 `evaluation_config_compare.yaml` 的 database_file 获取。
- 所有原始库均以 `duckdb.connect(..., read_only=True)` 打开；impl-013 的预测/gold 需要的 sibling netsuite_start.duckdb 也仅以 ATTACH … (READ_ONLY) 附加。GROUP BY 临时溢出目录在 `data/006_constraint_scratch/`，不提交数据库或原始数据。
- [输入指纹](../records/006_input_integrity.json)：93 个文件（30 契约、60 预测/gold 库、2 个外部 raw source 库、1 个配置）检查前后大小、mtime、SHA-256 一致；独立校验再次核实一致。
- impl-020 的契约无法严格按 YAML 解析，使用仅在内存中转义反斜杠的副本读取结构；grain 和约束字段摘录仍取原文件，未修改原件。原始解析错误和 parse_mode 保存在契约清单中，字段来源已逐处核对。
- [检查脚本](../scripts/check_dacomp_constraints.py)、[独立验证脚本](../scripts/validate_dacomp_constraints.py)、[已知结果测试](../scripts/test_dacomp_constraints.py)。实际命令：`PYTHONPATH=scripts PYTHONDONTWRITEBYTECODE=1 /home/katherine/dac/.venv-openhands/bin/python scripts/check_dacomp_constraints.py`；再运行 `scripts/validate_dacomp_constraints.py`。逐题命令和耗时在 [execution JSON](../records/006_execution.json)，日志为 `records/006_execution_impl-NNN.log`。
- [验证结果](../records/006_validation.json)：独立按源码文字位置核对 2,859 处约束声明（grain 619、primary_key 52、not_null 1,856、unique 332），合并后来源无遗漏、无新增；JSONL/CSV/逐题记录和各类汇总一致。{len(validation['independent_sql_checks'])} 项实际数据独立 SQL 抽查使用 window 分组计数或 count(*)−count(column)，与主 GROUP BY / FILTER 计数一致。
- [测试日志](../records/006_tests.log)：11 项通过，覆盖两种声明写法、复合键、重复定义、保守 grain 解析、原生字符串与 SQL NULL、unique NULL 口径、缺表/缺列/空表、只读文件不变与汇总去重。环境：Python {summary['python']}，DuckDB {summary['duckdb']}。没有安装新依赖。

## 不确定或没查到的

- 451 张表没有 grain；241 条 grain 无法按本次明确列键规则解析，保留全部原文。未从业务名词、未选出的维度、SQL 或实际数据反推字段，也未把允许重复的描述强行解释为唯一键声明。
- 两侧共同缺失的 27 张表没有可用行数或约束计数；部分存在表缺少被约束引用的列，均保留为未知。未知不表示违反，也不表示通过。
- 本次只核实声明与原生 SQL 计数，没有核实任何条件过滤、业务语义、类型约束、其他 tests 或报告以外的错误标签；不据此解释 agent 行为、官方分数或研究课题中的静默错误比例。

## 建议的下一步

本次约束检查与统计已完成。请用户与 Claude 决定是否需要进一步明确未解析 grain 的列定义；本任务不自动补写契约、改库或继续做错误原因分析。
'''
    path=ROOT/'notes/006_2026-10-27_DAComp契约约束检查.md'
    path.write_text(text)
    print(path)


if __name__=='__main__':main()
