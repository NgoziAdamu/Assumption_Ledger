# 043 校准定稿：impl-016_workday__organization_overview

## 任务

按冻结v3.2第3～8节盲标，封存后解盲。此件是解盲后的定稿，封存件不改。

## 结论

主要原因：多因并列；并列类别：Intent Misreading、其他。不是只能组合修复。

固定同一时钟基线(117行,696格)。annual_turnover_rate、management_ratio、两种label各减117格并列；assignment_join减5格，role_count_expression减71格。roles_join整块减少106格作为组合诊断，不覆盖逐点排序。

024旧主要原因：`多因并列（C、O）`，仅存档。

## 详细发现

### annual_turnover_rate

主要原因；Intent Misreading；把握高。

分母0时返回0是明确业务规则；agent用NULLIF后未补0。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-016_workday__organization_overview.json` / `annual_turnover_rate`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 579 |

| L1 | 117 | 117 | 696 | 579 |

| L2 | 117 | 117 | 696 | 579 |

| L3 | 117 | 117 | 696 | 579 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0.
```

### management_ratio

主要原因；Intent Misreading；把握高。

分母0时返回0是明确业务规则；agent用NULLIF后未补0。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-016_workday__organization_overview.json` / `management_ratio`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 579 |

| L1 | 117 | 117 | 696 | 579 |

| L2 | 117 | 117 | 696 | 579 |

| L3 | 117 | 117 | 696 | 579 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0.
```

### organization_maturity_level

并列主要原因；其他；把握高。

分桶相同，agent输出New/Young/Mature/Legacy与契约一致；gold使用扩展文案。只改变文字且无要求gold的具体字符串。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-016_workday__organization_overview.json` / `organization_maturity_level`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 579 |

| L1 | 117 | 117 | 696 | 579 |

| L2 | 117 | 117 | 696 | 579 |

| L3 | 117 | 117 | 696 | 579 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy.
```

### organization_size_category

并列主要原因；其他；把握高。

分桶相同，agent输出Empty/Micro等契约给出的词，gold使用扩展文案。第5/6节其他。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-016_workday__organization_overview.json` / `organization_size_category`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 579 |

| L1 | 117 | 117 | 696 | 579 |

| L2 | 117 | 117 | 696 | 579 |

| L3 | 117 | 117 | 696 | 579 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise.
```

### assignment_join

参与因素；Intent Misreading；把握高。

契约要求先按worker/role/source/organization联接再统计；agent直接按位置关系算平均任期，漏掉联接后的赋值权重。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-016_workday__organization_overview.json` / `assignment_join`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 691 |

| L1 | 117 | 117 | 696 | 691 |

| L2 | 117 | 117 | 696 | 691 |

| L3 | 117 | 117 | 696 | 691 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id.
```

### position_fill_rate

存在未确立的前提，但不是判错原因；Intent Misreading；把握高。

缺分母0时的默认0；本批CS输出单改不减少规模。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-016_workday__organization_overview.json` / `position_fill_rate`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 696 |

| L1 | 117 | 117 | 696 | 696 |

| L2 | 117 | 117 | 696 | 696 |

| L3 | 117 | 117 | 696 | 696 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0.
```

### high_risk_employee_percentage

存在未确立的前提，但不是判错原因；Intent Misreading；把握高。

缺分母0时的默认0；沿最终健康分计算后单改仍不减少规模。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-016_workday__organization_overview.json` / `high_risk_employee_percentage`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 696 |

| L1 | 117 | 117 | 696 | 696 |

| L2 | 117 | 117 | 696 | 696 |

| L3 | 117 | 117 | 696 | 696 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0.
```

### score_turnover

存在未确立的前提，但不是判错原因；Unstated Choice；把握中。

契约列出得分档位但没有列出对应阈值及零离职时是否同时要求正人数；具体分段是材料没定的选择。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-016_workday__organization_overview.json` / `score_turnover`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 696 |

| L1 | 117 | 117 | 696 | 696 |

| L2 | 117 | 117 | 696 | 696 |

| L3 | 117 | 117 | 696 | 696 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals.
```

### score_efficiency

存在未确立的前提，但不是判错原因；Unstated Choice；把握高。

契约列出效率得分档位但没有阈值数字；75/60与gold的80/70属未定选择。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-016_workday__organization_overview.json` / `score_efficiency`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 696 |

| L1 | 117 | 117 | 696 | 696 |

| L2 | 117 | 117 | 696 | 696 |

| L3 | 117 | 117 | 696 | 696 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals.
```

### score_risk

存在未确立的前提，但不是判错原因；Unstated Choice；把握高。

契约列出风险得分档位但没有阈值数字；10/20/30与gold的5/15/25属未定选择。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

复用 `records/024_reruns_impl-016_workday__organization_overview.json` / `score_risk`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 696 |

| L1 | 117 | 117 | 696 | 696 |

| L2 | 117 | 117 | 696 | 696 |

| L3 | 117 | 117 | 696 | 696 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals.
```

### role_count_expression

参与因素；Intent Misreading；把握中。

契约要求worker-position为关系入口并按关系中的role计数；agent在独立role-worker分支只计匹配到role master的id。单改目标计数表达式减少71格。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1完整给出联接规则；event 37只是写实现，没有指出冲突或替代；event 83完成报告未说明本处。SQL无注释。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

复用 `records/024_supplement_reruns_impl-016_workday__organization_overview.json` / `role_count_expression`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 625 |

| L1 | 117 | 117 | 696 | 625 |

| L2 | 117 | 117 | 696 | 625 |

| L3 | 117 | 117 | 696 | 625 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id.
```

### role_input_relation

存在未确立的前提，但不是判错原因；Intent Misreading；把握中。

契约明确先用worker-position联接role-worker；agent直接以role-worker作入口。单改入口使差异格子增加7，不作为参与因素；完整roles_join减少106是组合诊断，不重复记一个错误点。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1完整给出联接规则；event 37只是写实现，没有指出冲突或替代；event 83完成报告未说明本处。SQL无注释。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

复用 `records/024_supplement_reruns_impl-016_workday__organization_overview.json` / `role_input_relation`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 703 |

| L1 | 117 | 117 | 696 | 703 |

| L2 | 117 | 117 | 696 | 703 |

| L3 | 117 | 117 | 696 | 703 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id.
```

### role_management_role_employees

存在未确立的前提，但不是判错原因；Intent Misreading；把握中。

契约要求以worker-position关系中的工人按角色计数；agent从role-worker分支计数。当前数据下单改不改变规模。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1完整给出联接规则；event 37只是写实现，没有指出冲突或替代；event 83完成报告未说明本处。SQL无注释。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

复用 `records/024_supplement_reruns_impl-016_workday__organization_overview.json` / `role_management_role_employees`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 696 |

| L1 | 117 | 117 | 696 | 696 |

| L2 | 117 | 117 | 696 | 696 |

| L3 | 117 | 117 | 696 | 696 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id.
```

### role_director_role_employees

存在未确立的前提，但不是判错原因；Intent Misreading；把握中。

同上，Director角色的worker-position关系缺失；单改不改变规模。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1完整给出联接规则；event 37只是写实现，没有指出冲突或替代；event 83完成报告未说明本处。SQL无注释。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

复用 `records/024_supplement_reruns_impl-016_workday__organization_overview.json` / `role_director_role_employees`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 696 |

| L1 | 117 | 117 | 696 | 696 |

| L2 | 117 | 117 | 696 | 696 |

| L3 | 117 | 117 | 696 | 696 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id.
```

### role_lead_role_employees

存在未确立的前提，但不是判错原因；Intent Misreading；把握中。

同上，Lead角色的worker-position关系缺失；单改不改变规模。

是否说出：第4档，看到了相关信息，但没有意识到的迹象。event 1完整给出联接规则；event 37只是写实现，没有指出冲突或替代；event 83完成报告未说明本处。SQL无注释。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

复用 `records/024_supplement_reruns_impl-016_workday__organization_overview.json` / `role_lead_role_employees`。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 117 | 117 | 696 | 696 |

| L1 | 117 | 117 | 696 | 696 |

| L2 | 117 | 117 | 696 | 696 |

| L3 | 117 | 117 | 696 | 696 |

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/output.jsonl` / event 1 / `args.content`：

```text
Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id.
```

analysis_timestamp运行时差异先用同一固定时钟2025-10-13 13:18:28.226000+08:00控制；保留值696+117=813格，统一时钟后696格。不是新增错误前提。

## 证据来源

- 契约 `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`；SHA-256 `8f0707fc595c6f2f1e46a1983436959278e10315cb723e975c2811858d737c91`。

- 交付SQL `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql`；SHA-256 `b59173eeea3ae826802f8b6de9e99a323a7fbc82ab691ec5c31009dc9b51a552`。

- 013材料包、024核实查询/单改/补充单改、原始output.jsonl；043新增1条Reddit原始指标文本范围核实查询（只读）。

- 封存、对比与结构化定稿：`records/043_calibration_blind_sealed.json`、`records/043_calibration_comparison.json`、`records/043_checks/calibration_working.json`。

## 不确定或没查到的（含规则问题）

健康分具体阈值未在契约中找到；角色关系按现有逐点单改记录细分，不能把组合改动的106格收益套给一个单点。

## 建议的下一步

同一会话继续50张正式表。校准定稿与盲标一致率分开保存。
