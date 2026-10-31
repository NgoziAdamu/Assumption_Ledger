# KramaBench / archeology-hard-12：v3.1 修订

相对034：**补完无法判定**。主要原因：无法判定 → **已说出的选择**；只能组合修复：否 → 否；把握：低。

基础错误机制及原有查询见 [034原标注](../034_annotations/kramabench_archeology-hard-12.md)。本页只修订交付口径及本次指定的单改规则。

## 修订依据

按第7节同类候选规则补为已说出的选择（低把握）。起止年边界、原记录/同演员重叠合并、现代国家归属均是题面未定的处理约定；最终明确报告按起始年计449、全段计447和重叠归属。复用034合并诊断449→446；没有声称已逐项解释409。保留034同一候选组，组内具体排序未知。

## 冲突合并和时间边界

- 角色：主要；类别：无法判定 → **已说出的选择**。
- 是否说出：针对本处的具体说明 → **交付物里针对本处说明了**。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用（均沿用034）。

最终答案明确具体说明该处。

来源：`records/028_kramabench_packages/archeology-hard-12.md`，事件/位置 `final_answer`。
```text
Using conflict_brecke.csv, I count 449 conflicts starting from 800 through 1400 (the file has no entries before 900) with EndYear - StartYear >= 1. Two of these continue past 1400; requiring the whole conflict to end by 1400 gives 447. Country counts below use the 449 start-year definition and count a conflict for each modern country attributed to an actor, so they overlap and do not sum to 449. Attribution is approximate: historical actors are mapped to successor/current territories; Byzantium is credited to both Greece and Turkey, and generic actors are assigned by their named location where possible.

Modern-country conflict involvements: United Kingdom: 86; Italy: 82; France: 78; Germany: 75; Turkey: 56; Russia: 53; Greece: 50; Spain: 49; Austria: 33; Poland: 21; Denmark: 19; Hungary: 18; Netherlands: 18; Lithuania: 18; Bulgaria: 14; Ukraine: 12; Sweden: 9; Czechia: 7; Norway: 7; Ireland: 6; Vatican City: 6; Morocco: 5; Belgium: 4; Portugal: 3; Switzerland: 3; Serbia: 2; Estonia: 2; Mongolia: 2; Finland: 1.
```

证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/archeology-hard-12.md;subtask.3.query;subtask.5.query;subtask.6.answer;records/034_checks/conflict_diagnostic.json;records/036_checks/disclosure_audit.json。
