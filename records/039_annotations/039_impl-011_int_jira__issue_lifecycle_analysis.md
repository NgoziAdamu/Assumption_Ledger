# impl-011_int_jira__issue_lifecycle_analysis（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`C`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 1542, "cell_scale": 1542}, "L1": {"row_scale": 1542, "cell_scale": 1542}, "L2": {"row_scale": 1542, "cell_scale": 1542}, "L3": {"row_scale": 1542, "cell_scale": 1542}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| remove_many_to_many | Intent Misreading | 主要 | 1542 | 1542 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: int_jira__issue_lifecycle_analysis
      description: Issue lifecycle metrics and activity-based classifications derived from non-null field history changes
      grain: One row per issue_id
      source_models:
      - staging.stg_jira__issue
      - staging.stg_jira__issue_field_history
      business_logic: '- Build issue_activity_history from staging.stg_jira__issue_field_history: - Keep only records where field_value is present. - For each issue_id, sort changes by updated_at ascending and derive: - previous_change_time: the timestamp of the immediately prior change for the same issue; null for the first change. - change_sequence: the 1-based position of the change in the sorted list. - total_changes: the total number of non-null field_value changes for the issue (reference only). - If multiple changes share an identical updated_at within an issue, their tie-order is implementation-dependent (no secondary tiebreaker). - Build activity_patterns by retaining only changes with a previous_change_time and compute: - days_between_changes: elapsed time in days between change_time and previous_change_time. - hours_between_changes: elapsed time in hours between change_time and previous_change_time (intermediate only; not output). - Summarize per issue_id (issue_activity_summary): - total_field_changes: the count of retained changes (number of consecutive intervals). - avg_days_between_changes: average of days_between_changes. - max_days_between_changes: maximum of days_between_changes. - activity_variance: standard deviation of days_between_changes. - first_change_time: earliest change_time among retained changes. - last_change_time: latest change_time among retained changes. - When no retained changes exist, the summary has no row; downstream metrics remain null, with total_field_changes set to 0 in the final step. - Build issue_base_info from staging.stg_jira__issue and compute: - total_lifecycle_days: elapsed time in days from created_at to resolved_at; if unresolved, to the current timestamp at execution. - Final integration and classifications (left join summary to base on issue_id): - total_field_changes: set to 0 when summary is missing; other summary metrics remain null when missing. - activity_pattern: - If total_field_changes = 0 → "No Activity". - Otherwise by avg_days_between_changes: ≤1 → "High Activity"; ≤7 → "Regular Activity"; ≤30 → "Low Activity"; else → "Minimal Activity". - lifecycle_speed: - By total_lifecycle_days: ≤7 → "Fast"; ≤30 → "Normal"; ≤90 → "Slow"; else → "Very Slow". - risk_indicator (applied in order): - If total_lifecycle_days > 90 and total_field_changes < 5 → "Stagnant". - Else if max_days_between_changes > 30 → "Inactive Periods". - Else if total_field_changes > 50 → "Over Worked". - Else → "Normal". - Output one row per issue_id from staging.stg_jira__issue; the final result is ordered by issue_id ascending.'
      columns:
      - name: issue_id
        data_type: VARCHAR
        description: Primary grouping key from Jira; exactly one output row per issue_id
        tests:
        - not_null
        - unique
      - name: issue_key
        data_type: VARCHAR
        description: Human-readable Jira issue key (e.g., PROJ-123)
        tests:
        - not_null
      - name: issue_type_id
        data_type: VARCHAR
        description: Issue type identifier from Jira
      - name: priority_id
        data_type: VARCHAR
        description: Priority identifier from Jira
      - name: project_id
        data_type: VARCHAR
        description: Project identifier from Jira
        tests:
        - not_null
      - name: created_at
        data_type: TIMESTAMP
        description: Issue creation timestamp from Jira
        tests:
        - not_null
      - name: resolved_at
        data_type: TIMESTAMP
        description: Issue resolution timestamp; null if unresolved
      - name: assignee_user_id
        data_type: VARCHAR
        description: Current assignee user identifier from Jira
      - name: reporter_user_id
        data_type: VARCHAR
        description: Reporter user identifier from Jira
      - name: total_lifecycle_days
        data_type: DOUBLE
        description: Fractional days from created_at to resolved_at; if unresolved, to current_timestamp at execution; no rounding
      - name: total_field_changes
        data_type: BIGINT
        description: Count of consecutive change intervals (rows with non-null previous_change_time) over non-null field_value changes; 0 when none
      - name: avg_days_between_changes
        data_type: DOUBLE
        description: 'Average of days_between_changes across change intervals; unit: days; null when no intervals'
      - name: max_days_between_changes
        data_type: DOUBLE
        description: 'Maximum of days_between_changes across change intervals; unit: days; null when no intervals'
      - name: activity_variance
        data_type: DOUBLE
        description: Standard deviation of days_between_changes across change intervals; null when no intervals
      - name: first_change_time
        data_type: TIMESTAMP
        description: Earliest change_time among intervals (second or later change); null when no intervals
      - name: last_change_time
        data_type: TIMESTAMP
        description: Latest change_time among intervals; null when no intervals
      - name: activity_pattern
        data_type: VARCHAR
        description: 'Classification: No Activity if total_field_changes=0; else High/Regular/Low/Minimal based on avg_days_between_changes thresholds'
        tests:
        - activity_pattern IN ('No Activity', 'High Activity', 'Regular Activity', 'Low Activity', 'Minimal Activity')
      - name: lifecycle_speed
        data_type: VARCHAR
        description: 'Classification from total_lifecycle_days: Fast (≤7), Normal (≤30), Slow (≤90), else Very Slow'
        tests:
        - lifecycle_speed IN ('Fast', 'Normal', 'Slow', 'Very Slow')
      - name: risk_indicator
        data_type: VARCHAR
        description: 'Risk classification applied in order: Stagnant, then Inactive Periods, then Over Worked, else Normal'
        tests:
        - risk_indicator IN ('Normal', 'Stagnant', 'Inactive Periods', 'Over Worked')
```

### 逐点结论

#### remove_many_to_many

主要；**Intent Misreading**；把握高。

P：按issue聚合生命周期之前可额外连接该issue的所有history行。契约明确基于相邻活动变更区间计算次数和平均时长；这个额外多对多放大转移数，做法由规格定下，归Intent而非Data。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1542 | 0 | 1542 | 0 |
| L1 | 1542 | 0 | 1542 | 0 |
| L2 | 1542 | 0 | 1542 | 0 |
| L3 | 1542 | 0 | 1542 | 0 |

重跑：`records/021_reruns_impl-011_int_jira__issue_lifecycle_analysis.json` / `remove_many_to_many`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_lifecycle_analysis.sql` / `SQL.text`（sql）：

```text
select h.issue_id,h.change_time,a.days_between_changes from h join a using(issue_id) where h.previous_change_time is not null
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`，行[676, 755]；材料包 `records/021_packages/021_impl-011_int_jira__issue_lifecycle_analysis.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_lifecycle_analysis.sql`；SHA-256 `2c383e7769d8ea535ad35f72d10f5d01c39ad4107e5eca0e245781071225c7f5`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / event 55。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共1条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 21，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
