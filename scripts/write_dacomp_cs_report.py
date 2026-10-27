"""Render the numbered user report from validated mechanical records."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "records" / name).read_text())


def number(value, signed=False):
    return "—" if value is None else format(int(value), "+,d" if signed else ",d")


def main():
    overview = load("005_cs_overview.json")
    validation = load("005_cs_validation.json")
    integrity = load("005_cs_input_integrity.json")
    special = load("005_impl021_id核查.json")
    details = [json.loads(p.read_text()) for p in sorted((ROOT / "records").glob("005_cs_impl-*.json"))]
    tables = [(d, t) for d in details for t in d["tables"]]
    recovered_names = '；'.join(d['task']+' / '+t['table'] for d,t in tables if t['official_current_match'])
    rows = list(csv.DictReader((ROOT / "records/005_cs_summary.csv").open()))
    assert not validation["failures"] and len(rows) == overview["failed_nodes"]
    unavailable = [(d, t) for d, t in tables if not t["current_pred_execution"] or not t["gold"]["exists"]]
    no_shared = sum(t["alignment"].get("shared_keys") == 0 for d, t in tables)
    engines = {}
    for d, t in tables:
        if t["alignment"]["status"] not in ("missing_table_or_no_common_columns", "no_common_key_columns"):
            engine = t["alignment"].get("engine", "python_row_groups")
            engines[engine] = engines.get(engine, 0) + 1
    text = f"""# DAComp DE-Impl：CS 失败 intermediate / marts 逐表机械比对

## 任务

检查 30 题最终 CS 评分中不匹配的 intermediate、marts（含 mart 别名）表。按 003 号报告，对 impl-013、019、022 使用 compatibility 评分。重建“配置内上游及同层其他节点用 gold、当前节点用 agent SQL”的结果，按 004 口径记录行、列、类型、键、逐列值差异和真实样例；抽取节点 SQL 结构和对应契约原文。另独立核实 impl-021 四张 staging 表的完整规格及 ID 计数。日期：2026-10-27，Asia/Singapore。

本报告仅记录机械比对与原文抽取，没有判断错误原因、静默错误类型或研究假设，没有调用模型或重跑 agent。

## 结论

已核实：30 题中有 **{overview['tasks_with_failed_nodes']} 题、{overview['failed_nodes']} 张**目标失败表，包括 intermediate {overview['layers'].get('intermediate',0)} 张、marts {overview['layers'].get('marts',0)} 张。本次 **{overview['executed']} 张节点 SQL 执行成功，{overview['failed_nodes']-overview['executed']} 张未取得节点结果**；**{overview['gold_missing']} 张缺少 gold 同名表**。{overview['reproduced_matches']} 张在本次回放为匹配（{recovered_names}），历史标记仍保留；执行状态与原记录的差异条数为 {len(overview['prediction_execution_disagreements'])}。缺少任一侧时保留记录并将无法计算的指标记为未知。

全部目标已写入 [CSV 总表](../records/005_cs_summary.csv) 和逐题 JSON；同一条表记录含 SQL、结构抽取、契约完整原文及差异。impl-021 的 NULL/空字符串/字面值计数已独立查询，见下方单独小节。原始文件均只读；续跑检查点覆盖的 {integrity['files_checked']} 个输入文件在续跑前后大小、mtime、SHA-256 一致，另与既有 003/004 指纹交叉核对。

## 详细发现

### 1. 目标范围与结果重建

[完整最终评分选表依据](../records/005_cs_selection.json) 覆盖所有 30 题；只有 comparison_results=false 且 layer_name 为 intermediate/marts/mart 的表进入本次逐表清单。兼容评分来自 `20261025_de_batch_review_02/compatibility/impl-NNN/score.json`；其他题取 `scoring/impl-NNN/cs/score.json`。本次不以原始 CFS 结果库冒充 CS 节点结果。

官方 `CSEvaluator.evaluate_all_layers()` 在 `pred_dir/tmp/cs_hybrid.duckdb` 中保存临时 hybrid，finally 会删除 tmp；实际检索该批 review 目录也未找到遗留的 cs_hybrid.duckdb。因此本次在 `data/005_cs_work/` 的私有 gold 副本上重建，每张执行成功表另存到对应任务的 `node_results.duckdb`，数据库均不进 git。

具体执行直接调用官方 `_ordered_layers`、`_resolve_schema_name`、`_ensure_gold_dependencies`、`_build_pred_table`、`_process_sql`、`_copy_table_from_gold`。每个目标节点执行前，将配置中较低层和同层其他表恢复为 gold；目标节点执行后关闭连接，使用官方 `CoreAccuracyEvaluator.compare_table` 复核，再恢复目标表。节点 SQL 保留官方 300 秒 timeout。013、019、022 同时使用既有 recursive SQL 查找和 VIEW 替换 compatibility 补丁；需要外部 raw source 的库按既有 helper 以 READ_ONLY 附加。

与完整官方运行的执行差别：本次只执行目标失败节点，跳过通过节点与 staging 节点的重建；依赖恢复仍按官方配置执行。只对私有 hybrid 副本设置可写权限，以便写入；原 gold 的权限不改。增加 SQL 异常记录、节点快照和逐键统计。官方 CREATE 返回失败时，绝不把副本里可能残留的 gold 目标当成预测。依赖恢复异常节点共 {overview['dependency_restore_error_nodes']} 张，详情保留在 dependency_restore_errors；执行异常原文在 build_errors，不在此作原因判断。

为核对跳过其他节点是否改变结果，另在私有 prediction/gold 副本上完整运行了 impl-021 的官方 CS 循环、impl-013 和 022 的 compatibility CS 循环，{len(validation['full_official_node_checks'])} 张目标节点的执行/存在性/匹配三项均与本次结果一致。[交叉核对](../records/005_cs_validation.json)、[021 完整评分](../records/005_cs_full_official_impl-021.json)、[013 完整评分](../records/005_cs_full_official_impl-013.json)、[022 完整评分](../records/005_cs_full_official_impl-022.json)。这几次也只执行 SQL，没有运行 agent。

本次严格按层名限定范围。评分里另外还有下列其他层，未纳入本次 intermediate/marts 表清单：

"""
    for item in overview["not_included_other_layers"]:
        names = ', '.join('`'+t+'`' for t in item["failed_tables"]) or '无失败表'
        text += f"- {item['task']} / {item['layer']}：{names}。\n"
    text += f"""
### 2. 与 004 一致的比较口径

- 官方值规范化为 `COALESCE(LOWER(TRIM(CAST(column AS VARCHAR))), 'null')`；按每表 compare_cols 与实际共同列的交集选主口径列，随后做整行 hash 多重集合比较。**不统一 round 到两位小数，也不全局忽略时间列**。本次沿用这一点，并另报所有共同列的差异、单侧列、大小写列名差异和类型差异。
- 本次逐键统计是官方整行比较之外的机械拆解。即使行数不同也继续比共同键，不能将不一致列数直接视为官方分数。类型和缺列单独记录，不混入值差异列数。
- 优先契约 primary_key、not_null/unique ID；同时识别列的 constraints 与 tests 中明写的 not_null、unique、primary_key，不添加契约没有的约束。缺少明确主键时沿用 004 的固定候选顺序，在 not_null ID、命名 key、实体 ID、ID/date/dimension 组合等中选可用字段。不按“共同键最多”挑字段。实际字段、选择理由和候选唯一性检查都在 alignment 内；推定对齐字段不宣称为业务主键。模型契约 tests 写法的补充识别只导致从既有只读节点快照重新计算键和值统计，没有再次执行 agent SQL，见 [最终整理记录](../records/005_cs_finalization.json)。
- 键和值均用相同规范化；SQL NULL 与字符串 null 在主比对口径中合并，但空字符串保留。本节与下方 impl-021 精确 ID 计数采用不同口径，后者不规范化。
- 共同键一对一时，逐列记录精确差异行数，并给最多 3 个真实键/预测值/gold 值样例。共同键非唯一时，逐列值多重集合先抵消，剩余 P/G 次出现至少有 min(P,G) 对值不同；此项是下界，不能唯一配对原始行。精确数、下界、双方未抵消频次分别保存，样例标明是残余多重集合。只有重复次数不同不虚构值差异。
- 本次 {overview['alignment_status'].get('grouped_nonunique_keys',0)} 张表含非唯一共同键，{no_shared} 张可比表的共同键数为 0；后者的共同键值差异列数为 0 只表示没有共同键，不表示整表匹配。缺表或执行失败记未知，不写成 0 行。样例少于 3 个时只给实际存在的样例。
- 通常使用原有 Python 分组；超过 100,000 行的表改用磁盘支持的 DuckDB 聚合，临时文件留在 data/ 私有工作目录。两种引擎在 10 个已知结果测试上输出一致，另有 4 项 SQL/契约抽取测试；本次可比表使用 Python 分组 {engines.get('python_row_groups',0)} 张、DuckDB 聚合 {engines.get('duckdb_disk_aggregation',0)} 张。独立 SQL 聚合抽查 {len(validation['independent_column_checks'])} 张表的逐列差异数，与记录一致。

### 3. SQL 与契约抽取字段

逐题 JSON 中每张表的 `agent_sql.raw_text` 是实际读取的节点 SQL，`official_processed_text` 是官方包装前的处理结果，`used_source_paths` 给来源。`structure.scopes` 按每个 SELECT 分开记录：每个 JOIN 的类型、左侧已有关系链、右侧表/子查询和 alias、完整 ON、USING 列、两侧含列引用的等值表达式；GROUP BY 原表达式（含序号/ALL）；WHERE/HAVING/QUALIFY 完整条件；DISTINCT、ROW_NUMBER 的 PARTITION/ORDER 和 COALESCE 的后备参数。

CTE/子查询保留逻辑名称并附 CTE 定义，不猜测未限定列的物理绑定；非等值连接及复合条件保留完整 ON。ROW_NUMBER 窗口、输出 alias 与过滤条件分别列出，并额外抽取 rank=1、rank<=1、rank<2 的语法候选；跨 scope alias 仅作候选关联，不断言绑定或业务去重意图，不把所有 ROW_NUMBER 都判成去重。SQLGlot 以 DuckDB dialect 解析，其格式化表达式可能与原文写法不同，原始 SQL 始终另外完整保留。

`contract.blocks` 是契约中同名表规格的完整原文，附源路径、SHA-256、YAML 路径与行号；不是改写或概述。共核对 {validation['verbatim_contract_blocks_checked']} 段原文、{validation['sql_source_texts_checked']} 份实际 SQL，JOIN 节点抽取覆盖 {validation['join_nodes_checked']} 个。impl-020 契约的反斜杠只在内存中的结构解析副本转义，原件和报告摘录不改写。test_timestamp 在整份契约和对应 SQL 目录未找到同名规格/SQL，明确记 missing。

### 4. 全部目标表总表

Δ行 = 本节点 CS 预测行数 − gold 行数。键 P/G/共为只在预测、只在 gold、双方都有的不同规范化键数。† 表示存在非唯一共同键，逐列数含上述下界。值差列数只计官方可用比较列；— 表示无法计算。表名链接可定位逐题 JSON 中完整的列、类型、逐列计数/样例、SQL 和契约。

| 任务 | 层 | 失败表 | 预测行 | gold 行 | Δ行 | 对齐字段 | 键 P/G/共 | 值差列数 |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | ---: |
"""
    for d, t in tables:
        a = t["alignment"]
        mark = '†' if a["status"] == 'grouped_nonunique_keys' else ''
        keys = '/'.join(number(a.get(k)) for k in ("pred_only_keys", "gold_only_keys", "shared_keys"))
        cols = ', '.join(a["columns"]) or '—'
        text += f"| {d['task']}{mark} | {t['layer']} | [{t['table']}](../records/005_cs_{d['task']}.json) | {number(t['prediction']['row_count'])} | {number(t['gold']['row_count'])} | {number(t['row_count_delta_pred_minus_gold'],True)} | {cols} | {keys} | {number(t['mismatching_official_columns'])}{mark} |\n"
    recovered = [(d, t) for d,t in tables if t["official_current_match"]]
    if recovered:
        text += '\n**与历史匹配标记不同的条目：** ' + '；'.join(d['task']+' / '+t['layer']+'.'+t['table'] for d,t in recovered) + '。它们在留存最终 CS 中为 false，本次回放按官方比较器为 true；完整官方循环的交叉核对见上文。仍保留在历史失败清单中，既不覆盖历史评分，也不判断差异原因。\n'
    text += "\n无法取得双边可比结果的条目单列如下。执行失败只表示没有可用预测结果；异常原文已保存，不做原因归类。\n\n| 任务 | 层/表 | 节点执行成功 | gold 存在 |\n| --- | --- | --- | --- |\n"
    for d, t in unavailable:
        text += f"| {d['task']} | {t['layer']}.{t['table']} | {t['current_pred_execution']} | {t['gold']['exists']} |\n"
    text += """
### 5. impl-021 独立核查：完整规格与 ID 三类计数

已核实：主要对照的“原始表”明确取 **gold 结果库同库的 raw.campaign/flow/metric/person**，gold 输出取 staging 同名目标表。另对留存 agent 结果库的 raw 表独立查询，四张表的下列计数均与 gold 库 raw 一致。初始仓库 klaviyo_start.duckdb 的 raw 内容并不完全相同，因此另表报告其计数，不将它混作实际结果库的 raw。

raw 列为 `ID`，gold 列分别为 campaign_id、flow_id、metric_id、person_id；映射已读取 gold staging SQL 核对。三项条件分别是 `ID IS NULL`、`CAST(ID AS VARCHAR) = ''`、`CAST(ID AS VARCHAR) = 'null'`。这里按精确、区分大小写的字符串比较，不 trim、不 lower、不把 SQL NULL 转字符串。下面只陈列计数与原文，不解释契约、raw 与 gold 的关系。

[完整 SQL、来源、规格原文和三库指纹](../records/005_impl021_id核查.json)。主要对照：

| staging 表 | raw 总行 | raw SQL NULL | raw 空串 | raw 字面 'null' | gold 总行 | gold SQL NULL | gold 空串 | gold 字面 'null' |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
"""
    for t in special["tables"]:
        vals = [t[s][k] for s in ("raw_counts", "gold_counts") for k in ("rows", "sql_null", "empty_string", "literal_lowercase_null")]
        text += '| ' + t["table"] + ' | ' + ' | '.join(number(v) for v in vals) + ' |\n'
    text += "\n初始仓库 start 库的 raw 表另列，列名均为 ID：\n\n| 原始表 | 总行 | SQL NULL | 空串 | 字面 'null' |\n| --- | ---: | ---: | ---: | ---: |\n"
    for t in special["tables"]:
        c = t["initial_repository_raw_counts"]
        text += '| ' + t["raw_table"] + ' | ' + ' | '.join(number(c[k]) for k in ("rows", "sql_null", "empty_string", "literal_lowercase_null")) + ' |\n'
    for t in special["tables"]:
        b = t["contract"]["blocks"][0]
        text += f"\n#### {t['table']}：契约完整原文\n\n来源：`{t['contract']['source_path']}`，第 {b['start_line']}–{b['end_line']} 行。\n\n```yaml\n" + b["original_text"].rstrip('\n') + '\n```\n'
    text += f"""
## 证据来源

- [本次方法/范围元数据](../records/005_cs_overview.json)、[最终评分选表记录](../records/005_cs_selection.json)、[CSV 总表](../records/005_cs_summary.csv)。逐题记录名为 `records/005_cs_impl-NNN.json`。
- 官方代码：`{SUITE_PATH}/utils.py` 的 CSEvaluator / CoreAccuracyEvaluator，及同目录 evaluation_config_compare.yaml；源项目 compatibility 与 raw dependency helper：`/home/katherine/dac/src/de_cs_compat.py`、`de_gold_dependencies.py`。实际内容均已读取，指纹保存在 [输入完整性记录](../records/005_cs_input_integrity.json)。
- SQL 来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-NNN/agent/dacomp-de-impl-NNN/sql/`；gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-NNN/`；契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-NNN/docs/data_contract.yaml`。精确数据库文件名和实际路径见逐题记录。
- [逐节点重建/比较脚本](../scripts/compare_dacomp_cs_nodes.py)、[原有机械比对](../scripts/compare_dacomp_staging.py)、[磁盘聚合引擎](../scripts/dacomp_sql_diff.py)、[SQL/契约抽取](../scripts/dacomp_sql_extract.py)、[最终统计整理](../scripts/finalize_dacomp_cs_records.py)、[独立校验](../scripts/validate_dacomp_cs_results.py)。节点构建 sandbox 使用原件只读挂载、data/ 单题工作目录可写、网络关闭、scrubbed_env；[续跑命令记录](../records/005_cs_execution.json)、[补充工作进程命令](../records/005_cs_additional_execution.json)。各已完成任务的日志存为 `records/005_cs_execution_impl-NNN.log`。
- 运行命令：`PYTHONPATH=data/005_tools:scripts PYTHONDONTWRITEBYTECODE=1 /home/katherine/dac/.venv-openhands/bin/python scripts/compare_dacomp_cs_nodes.py`；独立校验运行同一环境下的 `scripts/validate_dacomp_cs_results.py`。流程中断后按完整逐题 JSON 续跑，未完成的单题使用新私有目录，不覆盖原件。前 10 题在断点前已完成，使用只读 sandbox；续跑前的检查点不冒充前 10 题的事前指纹。
- 续跑的 {integrity['files_checked']} 个输入前后指纹一致；其中与 004 既有输入 SHA-256 交叉核对 {validation['prior_input_baselines'].get('prior004_checked',0)} 个，与 003 归档清单交叉核对 {validation['prior_input_baselines'].get('prior003_archive_checked',0)} 个，均一致。[校验详情](../records/005_cs_validation.json)。impl-021 三库另有读取前后完整指纹。
- 测试：10 项既有比较测试、4 项 SQL/契约抽取测试、10 项 SQL/Python 引擎等价检查全部通过。[测试日志](../records/005_cs_tests.log)。独立 SQL 聚合抽查及完整官方流程核对也全部通过。
- 环境：Python {overview['python']}，DuckDB {overview['duckdb']}；SQLGlot 30.25.0。为抽取 SQL，执行 `/home/katherine/dac/.venv-openhands/bin/python -m pip install --target data/005_tools sqlglot`，下载约 798 KB wheel，实际安装 30.25.0；复现时可固定 `sqlglot==30.25.0`。源虚拟环境未安装/升级任何包。

## 不确定或没查到的

- 官方逐节点输出未留存；本次结果为按同一函数和补丁在私有副本上重建。执行状态与留存目标记录一致，匹配标记有 {overview['reproduced_matches']} 张不同，具体条目已单列；没有判断该差异的来源，也没有推定回放与历史物理字节、未声明行序或非确定性表达式逐字节相同。
- {overview['failed_nodes']-overview['executed']} 张节点执行未成功、{overview['gold_missing']} 张 gold 同名表缺失，详见单列清单，无法给出完整双边值比对；不以其他表或 CFS 输出补齐。test_timestamp 的契约/SQL 在对应目录和整份契约中未找到。
- not_null 不等于唯一主键；缺少声明时的对齐字段与重复组均显式记录。非唯一组只能给逐列多重集合下界，不能得到唯一原始行配对。没有将这些限制解释为失败原因。
- JOIN 列绑定只做语法抽取；CTE/子查询和未限定列不做未经核实的物理溯源，ROW_NUMBER 是否承担去重的业务意图也不判定。

## 建议的下一步

本任务的机械比对与信息抽取已完成。请用户与 Claude 根据逐题记录决定后续研究范围；本次不新增错误标签、不改 benchmark 契约或 gold、不向其他层扩展分析。
"""
    path = ROOT / "notes/005_2026-10-27_DAComp_CS节点逐表比对.md"
    path.write_text(text)
    print(path)


SUITE_PATH = "/home/katherine/dac/benchmarks/DAComp-code/dacomp-de/evaluation_suite"

if __name__ == "__main__":
    main()
