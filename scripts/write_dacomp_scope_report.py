"""Write task 009 from the verified comparison and reconciliation records."""

import json

from complete_dacomp_comparisons import RECORDS,ROOT


def main():
    comparison=json.loads((RECORDS/'009_comparison_summary.json').read_text())
    summary=json.loads((RECORDS/'009_denominator_summary.json').read_text())
    changes=json.loads((RECORDS/'009_status_changes.json').read_text())
    validation=json.loads((RECORDS/'009_validation.json').read_text())
    selection=json.loads((RECORDS/'009_selection.json').read_text())
    tolerance=[json.loads(line) for line in (RECORDS/'009_tolerance_tables.jsonl').read_text().splitlines()]
    details=[]
    for number in (2,10,12):details.extend(json.loads((RECORDS/f'009_cs_impl-{number:03d}.json').read_text())['tables'])
    index={(r['task'],r['table']):r for r in details}
    old=summary['old_008_status_counts'];new=summary['corrected_status_counts'];combined=summary['combined']
    groups=summary['nonstaging_by_layer_group'];nonstage=summary['nonstaging_total'];stage=summary['staging']
    level_counts=comparison['whole_levels'];replayed=comparison['official_replay_matches']
    group_rows=['| 层 | 原 CS 不匹配 | CS 执行失败 | 缺 gold | 两项重叠 | 不可比较并集 | 可双边比较（含 L0） | 重放 L0 匹配 | 可比较失败（扣 L0） |',
                '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    formulas=[]
    for label,k in [('intermediate','intermediate'),('marts','marts'),('其他层（sales / utils）','other'),('合计',None)]:
        c=nonstage if k is None else groups[k]
        group_rows.append(f"| {label} | {c['historical_failed']} | {c['cs_execution_failed']} | {c['gold_missing']} | {c['execution_failed_and_gold_missing']} | {c['unavailable_union']} | {c['bilateral_comparable_including_replay_pass']} | {c['replay_l0_matches']} | {c['comparable_failed_excluding_replay_pass']} |")
        formulas.append(f"- {label}：{c['historical_failed']} − {c['cs_execution_failed']} − {c['gold_missing']} + {c['execution_failed_and_gold_missing']} = {c['bilateral_comparable_including_replay_pass']}（可双边比较）；再减重放 L0 匹配 {c['replay_l0_matches']} = **{c['comparable_failed_excluding_replay_pass']}**（可比较失败）。")
    review_rows=['| 题目 / 表 | 008 状态 | 009 整表级别 | 009 状态 | 状态更新依据 |', '|---|---|---|---|---|']
    for r in changes:
        reason='前缀映射后完成双边补比；'+r['whole_level'] if r['task']=='impl-002' else '原 CS 记录为不匹配，本次补比；'+str(r['whole_level'])
        review_rows.append(f"| {r['task']} / {r['table']} | {r['old_008_status']} | {r['whole_level'] or '不可比较'} | {r['new_009_status']} | {reason} |")
    node_rows=['| 题目 / 表 | 节点预测行数 | gold 行数 | 共同键数 | 按键级别 | 整表级别 | agent / gold / 契约时间写法 |',
               '|---|---:|---:|---:|---|---|---|']
    for r in tolerance:
        times=r['time_dependencies']
        marker=' / '.join(('有' if times[k]['appears'] else '无') if times[k]['available'] else '未找到' for k in ('agent_sql','gold_sql','contract'))
        node_rows.append(f"| {r['task']} / {r['table']} | {r['baseline_prediction_rows']} | {r['baseline_gold_rows']} | {r['baseline_alignment'].get('shared_keys')} | {r['keyed_match_level'] or '不可比较'} | {r['whole_match_level'] or '不可比较'} | {marker} |")
    status_rows=['| 状态 | 008 | 009 更正后 | 变化 |','|---|---:|---:|---:|']
    for state in ('待标注','格式差异','官方判为通过','不可评估'):
        delta=new[state]-old[state]
        status_rows.append(f'| {state} | {old[state]} | {new[state]} | {delta:+d} |')
    status_equations=[]
    for state in ('待标注','格式差异','官方判为通过','不可评估'):
        incoming=sum(r['new_009_status']==state for r in changes)
        outgoing=sum(r['old_008_status']==state for r in changes)
        status_equations.append(f"- {state}：{old[state]} + {incoming}（转入）− {outgoing}（转出）= **{new[state]}**。")
    stage_levels=stage['whole_levels']
    nonlevels=nonstage['whole_levels_of_comparable_failures']
    format_terms=f"staging（{stage_levels.get('L1',0)} + {stage_levels.get('L2',0)}）+ 非 staging（{nonlevels.get('L1',0)} + {nonlevels.get('L2',0)}）"
    pending_terms=f"staging（{stage_levels.get('L3',0)} + {stage_levels.get('仍不匹配',0)}）+ 非 staging（{nonlevels.get('L3',0)} + {nonlevels.get('仍不匹配',0)}）"
    starts=[r['execution_started']['Asia/Singapore'] for r in details]
    ends=[r['execution_finished']['Asia/Singapore'] for r in details]
    evidence=json.loads((RECORDS/'009_official_evaluator_evidence.json').read_text())
    refs={b['symbol']:b for b in evidence['code']}
    def ref(name):
        b=refs[name];return f"`{b['path']}`，{b['start_line']}–{b['end_line']} 行"
    text=f'''# DAComp DE-Impl：补齐 21 张表的比对范围

## 任务

补比 impl-002 的 18 张带 pendo__ 前缀的 marts 表，以及 impl-010 的 2 张 sales 表、impl-012 的 1 张 utils 表。先核对原始 CS 评分，再在私有 gold 副本中只执行目标节点 SQL，按 005 做结构/键/逐列差异，按 007 做 L0–L3 比较。本次仅比较和统计。

节点执行日期为 **{min(starts)[:10]}**（Asia/Singapore），执行窗口 `{min(starts)}` 至 `{max(ends)}`；每张表保留 UTC、Asia/Singapore 和 DuckDB TimeZone / current_date 记录。未改动运行时间表达式。

## 结论

**已核实：21 张均在原始 CS 评分中判为不匹配，本次全部成功执行且找到 gold。** 补比整表首次匹配级别为：L0 {level_counts.get('L0',0)}、L1 {level_counts.get('L1',0)}、L2 {level_counts.get('L2',0)}、L3 {level_counts.get('L3',0)}、仍不匹配 {level_counts.get('仍不匹配',0)}。

更正后可比较失败表为 **{combined['comparable_failed']} 张**，其中 L1/L2 格式差异 **{combined['format_difference_L1_L2']} 张**，待标注 **{combined['pending_annotation_L3_or_unmatched']} 张**。这里的“可比较失败”扣除了 CS 重放中 L0 已匹配的表；未扣 L0 的双边比较基数是 {combined['bilateral_comparable_including_replay_pass']} 张。两种分母和完整算式如下。

{chr(10).join(status_rows)}

1,069 个交付目标的总分母不变；仅更新本次 21 张的状态依据。原始数据库的大小、mtime、SHA-256 前后相同，004–008 的记录与报告保持原样。

## 详细发现

### 1. 原始评分核对与官方前缀处理

三份原始 CS 文件均已直接打开：

- `/home/katherine/dac/runs/20261025_de_batch_review_02/scoring/impl-002/cs/score.json`：marts 的 18 个无前缀配置名全部 comparison_results=false、pred_execution=true、gold_execution=false。
- 同路径 impl-010/cs/score.json：sales.hubspot__sales_performance_dashboard、sales.hubspot__sales_rep_performance 均 comparison_results=false，pred_execution=true、gold_execution=true。
- 同路径 impl-012/cs/score.json：utils.marketo__calendar_spine 为 comparison_results=false，pred_execution=true、gold_execution=true。

[009_selection.json](../records/009_selection.json)逐张记录完整文件路径、JSON path、原评分 timestamp 和三个布尔值。没有“原记录并非不匹配”的候选，故未排除任何一张。

只读核对官方代码，已核实以下行为，不作判断：

- `_sql_name_for_table` / `_read_sql` 按配置名（或配置中的 sql_name）找文件，官方 config 的这 18 个键都是 account 等无前缀名；代码位置：{ref('CSEvaluator._sql_name_for_table')}；{ref('CSEvaluator._read_sql')}。
- `_resolve_schema_name` 只处理 mart / marts schema 别名；`_list_tables` 返回真实表名，不删除 pendo__ 前缀。代码位置：{ref('CSEvaluator._resolve_schema_name')}；{ref('CSEvaluator._list_tables')}。
- `evaluate_all_layers` 用配置键逐一执行，并直接以 `t in gold_tables` 填写 gold_execution。`CoreAccuracyEvaluator.compare_table` 同样按传入的完整 table_name 检查表是否存在。位置：{ref('CSEvaluator.evaluate_all_layers')}；{ref('CoreAccuracyEvaluator.compare_table')}。

因此，**原评分未把这 18 个无前缀目标对应到带前缀 gold 表**。原记录的 18 个 gold_execution=false，与同版本函数的只读成员检查结果一致；另一次成员检查确认 18 个带 pendo__ 的 gold 关系均存在。[原代码逐字摘录及 18 张成员检查](../records/009_official_evaluator_evidence.json)。

### 2. 本次 CS 节点执行与实际上游

本次只在内存中为 impl-002 的 18 个 marts 配置键加 pendo__，并添加 sql_name 指回原无前缀文件；compare_cols、权重和其他配置不变。使用官方 `_ensure_gold_dependencies`、`_build_pred_table`、`_process_sql`、超时执行和比较方法。这个显式目标名映射是本次与原官方调用的差别；没有修改官方代码、原配置、agent SQL 或原始库。

每题从 gold 复制私有库，目标执行前恢复全部较早配置层及同层其他配置表为 gold；每个目标结束后再把该目标恢复为 gold。只执行该目标的 agent SQL，上游不执行 agent SQL。成功节点分别留存在 `data/009_cs_work/.../node_results.duckdb`，精确路径在逐题记录里。原始 gold 通过 READ_ONLY 附加，原项目和本仓库在执行 sandbox 中只读挂载，网络关闭，子进程使用 scrubbed_env。数据库和临时比较文件均在 data/ 下。

实际直接源表逐张列于 `actual_gold_upstreams`，保留 SQL 位置、gold 恢复后的行数；行生成器单列。impl-002 同层依赖也读取 gold，例如 customer_lifecycle_insights 的 marts.pendo__visitor。全量直接源表清单与 008 的静态提取一致。

非标准层的上游口径：

| 目标 | 本节点实际读取的 gold 输入 | 官方配置顺序中已恢复的较早层 |
|---|---|---|
| sales.hubspot__sales_performance_dashboard | intermediate.int_hubspot__deal_performance_metrics | staging、intermediate、marketing |
| sales.hubspot__sales_rep_performance | intermediate.int_hubspot__owner_performance_metrics；intermediate.int_hubspot__deal_performance_metrics | staging、intermediate、marketing |
| utils.marketo__calendar_spine | raw.marketo_lead；另有 GENERATE_SERIES 行生成器 | staging、intermediate、marts；raw 保留 gold 副本原内容 |

sales dashboard 的对齐键为 created_year，原因字段是 fallback_required_columns_or_first_common_column；sales rep 用契约 not_null / unique 的 owner_id；calendar_spine 未找到对应表契约，以 date_day 这个推定日期维度对齐，原样记录 inferred_id_date_dimension_composite，不把它称为契约主键。

### 3. 21 张逐表结果与时间标记

{chr(10).join(node_rows)}

时间三列引用 008 C9 的独立原文位置，并再次核对输入文件未变；`run_time_sensitive` 仅表示本节点 agent SQL 出现运行时间写法，共 {comparison['runtime_sensitive_targets']}/21 张。gold SQL 和契约标记另外保留。**这不是“日期已被证明改变了分数”的判断。** 本次照实际执行日期运行，未冻结、替换日期或改 gold，日期影响留给下一任务。

比较口径完全沿用 005 / 007：L0 为官方字符串规范化、行 hash 多重集合比较，按配置 compare_cols 取实际列交集；不增加全局数值舍入或排除时间列。L1 统一精确数值与布尔表示；L2 数值 ROUND_HALF_UP 到两位小数；L3 明确舍弃 timestamp 的时间部分，仅保留日期。键列固定，并一直用 L0 键值对齐，不随容差重选键。

整表要求行数和完整比较行元组多重集合一致；按键只检查共同键内的完整行元组和重复次数。无共同键不记为匹配。非唯一键的逐列差异计数与样例沿用 005 的精确部分 / 多重集合下界定义，未虚构唯一行配对。L0 精确行元组与官方标记的差异条目数为 {len(comparison['l0_tuple_official_discrepancies'])}。

### 4. 更正后的完整分母算式

staging 沿用 004 的 CFS 不匹配集合与 007 重比结果：**{stage['historical_failed']} − {stage['unavailable']} = {stage['comparable_failed']}**，即不匹配 {stage['historical_failed']}、不可比较 {stage['unavailable']}、可比较失败 {stage['comparable_failed']}。其中没有本次重放 L0 已匹配项。

非 staging 用 30 题最终 CS 记录，impl-013、019、022 保持 003 / 005 的 compatibility 评分。历史不匹配数为原 005 的 186 + 新纳入其他层的 3 = **189**；impl-002 的 18 张原来已在这 186 张中，此次只是补齐可比较性，不能再加一次。

{chr(10).join(group_rows)}

执行失败和缺 gold 不是互斥项，完整算式为：

{chr(10).join(formulas)}

全范围（staging CFS + 非 staging CS，沿用既有混合口径）的算式：

- 历史不匹配：{stage['historical_failed']} + {nonstage['historical_failed']} = **{combined['historical_failed']}**。
- 不可比较：{stage['unavailable']} +（{nonstage['cs_execution_failed']} + {nonstage['gold_missing']} − {nonstage['execution_failed_and_gold_missing']}）= **{combined['unavailable']}**。
- 可双边比较的历史目标：{combined['historical_failed']} − {combined['unavailable']} = **{combined['bilateral_comparable_including_replay_pass']}**。
- 重放 L0 匹配：007 已有 1 + 本次新增 {replayed} = **{combined['replay_l0_matches']}**。
- **可比较失败：{combined['bilateral_comparable_including_replay_pass']} − {combined['replay_l0_matches']} = {combined['comparable_failed']}**，也等于 staging {stage['comparable_failed']} + 非 staging {nonstage['comparable_failed_excluding_replay_pass']}。
- 其中 L1/L2 格式差异：{format_terms} = **{combined['format_difference_L1_L2']}**。
- 待标注：{pending_terms} = **{combined['pending_annotation_L3_or_unmatched']}**。
- 核对：{combined['format_difference_L1_L2']} + {combined['pending_annotation_L3_or_unmatched']} = **{combined['comparable_failed']}**。

[分母汇总](../records/009_denominator_summary.json)与 [189 张非 staging 历史目标清单](../records/009_nonstaging_failure_catalog.json)保留每张的原始评分、可比较性、重放与容差结果。没有把“共同键为空”从整表比较分母中移走。

分母与 008 的 1,069 个交付目标还需区分两处范围事实：官方 CS 清单里的 test_timestamp 未出现在 agent 最终交付表 / SQL 中，且同时属于执行未完成和缺 gold 的交集；008 的交付清单另含 6 张 impl-006 缺 gold 的 staging 表，它们不在 004 的 176 张不匹配集合里。这些条目没有在本任务扩展重跑，清单原样列于 denominator_summary。故不可把上述历史不匹配范围的“不可比较数”直接当作 1,069 张交付清单中的“不可评估数”。

### 5. 与 008 逐项对照

共 {summary['changed_targets']} 张状态变化，全部来自本次 21 个目标：

{chr(10).join(status_equations)}

{chr(10).join(review_rows)}

状态更新依据仅是本次目标映射、范围补入及实测比较级别；不是表的原因归类。[21 张完整复核清单](../records/009_target_status_review.csv)也列出若有状态未变的目标；[变化清单](../records/009_status_changes.json)逐条记录来源；[全体更正状态 CSV](../records/009_corrected_statuses.csv) / [JSONL](../records/009_corrected_statuses.jsonl)共有 1,069 行。

## 证据来源

- 原评分及 JSON path：[009_selection.json](../records/009_selection.json)。只读官方函数、原配置与 gold 成员检查：[009_official_evaluator_evidence.json](../records/009_official_evaluator_evidence.json)。
- 005 格式的逐题详细比对：`records/009_cs_impl-002.json`、`009_cs_impl-010.json`、`009_cs_impl-012.json`，含行数、列名/类型、固定键、单边/共同键、每列差异与样例、原 SQL、契约及执行信息。
- 007 格式：[容差 CSV](../records/009_tolerance_tables.csv)、[JSONL](../records/009_tolerance_tables.jsonl)、`009_tolerance_cs_impl-NNN.json`；[比较汇总](../records/009_comparison_summary.json)。
- 执行：[009_execution.json](../records/009_execution.json)与 `009_execution_impl-NNN.log`。私有副本及 node_results.duckdb 全在 data/009_cs_work/，不进 git。未重跑 agent、模型或 run.py。
- [前后完整性](../records/009_input_integrity.json)：{validation['input_files_unchanged']} 个输入文件前后大小、mtime、SHA-256 一致，其中 {validation['original_databases_unchanged']} 个原始 DuckDB 文件；包括本任务引用的所有 004–008 记录和报告。独立验证再次核对一致。
- [验证结果](../records/009_validation.json)：全部 21 张官方只读 L0 复核一致；{len(validation['independent_decimal_counter_checks'])} 张真实表用独立 Decimal / Counter 实现核验 L0–L3 和 L3 列差异；上游 gold 行数、键统计、时间出处、CSV / JSONL 及分母集合算术核对一致。[4 项已知结果测试](../records/009_tests.log)通过。
- 实现：[complete_dacomp_comparisons.py](../scripts/complete_dacomp_comparisons.py)、[分母汇总](../scripts/reconcile_dacomp_scope.py)、[独立验证](../scripts/validate_dacomp_scope_completion.py)。比较引擎复用 004 / 005 / 007 脚本，未修改旧脚本。Python 3.12.15、DuckDB 1.5.6、SQLGlot 30.25.0；未安装新依赖。

执行命令：

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B scripts/complete_dacomp_comparisons.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B scripts/reconcile_dacomp_scope.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B scripts/validate_dacomp_scope_completion.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B -m unittest scripts/test_dacomp_scope_completion.py -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B scripts/write_dacomp_scope_report.py
```

## 不确定或没查到的

本次未处理日期依赖，也未推断它对各表结果的实际影响。gold 是已留存的库内容，不按本次日期重生成；本次重放结果不冒充原评分当时的输出。utils.marketo__calendar_spine 在原契约中未找到相应表规格，对齐依据已单列。非唯一键的逐列统计仍保留 005 / 007 的配对限制。

## 建议的下一步

按用户已说明的后续任务处理时间依赖；本次保留逐表时间原文位置、实际执行日期与不改日期的比较结果，供用户和 Claude 决定具体规则。
'''
    path=ROOT/'notes/009_2026-10-28_DAComp补齐比对范围.md';path.write_text(text);print(path)


if __name__=='__main__':main()
