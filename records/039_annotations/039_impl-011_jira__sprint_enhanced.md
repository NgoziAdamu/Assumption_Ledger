# impl-011_jira__sprint_enhanced（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Quiet Downgrade**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 298, "cell_scale": 2086}, "L1": {"row_scale": 298, "cell_scale": 2086}, "L2": {"row_scale": 298, "cell_scale": 2086}, "L3": {"row_scale": 298, "cell_scale": 2086}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| story_points_committed | Quiet Downgrade | 并列 | 0 | 298 | 2 |
| story_point_estimate_committed | Quiet Downgrade | 并列 | 0 | 298 | 2 |
| story_points_end | Quiet Downgrade | 并列 | 0 | 298 | 2 |
| story_point_estimate_end | Quiet Downgrade | 并列 | 0 | 298 | 2 |
| story_points_completed | Quiet Downgrade | 并列 | 0 | 298 | 2 |
| story_point_estimate_completed | Quiet Downgrade | 并列 | 0 | 298 | 2 |
| issues_committed | Quiet Downgrade | 并列 | 0 | 298 | 2 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: jira__sprint_enhanced
      description: Enhanced sprint metrics aggregated from daily sprint issue history
      grain: One row per sprint_id
      source_models:
      - marts.jira__daily_sprint_issue_history
      business_logic: 'Build sprint-level metrics from marts.jira__daily_sprint_issue_history: - Sprint metadata: Keep distinct combinations of sprint_id, sprint_name, sprint_started_at, sprint_ended_at, sprint_completed_at, board_id, original_estimate_seconds, remaining_estimate_seconds, and time_spent_seconds. - Sprint issue metrics (evaluated across all daily rows for the sprint_id): - sprint_issues: count distinct issue_id across all days. - sprint_assignees: count distinct assignee_user_id across all days (NULL user_ids are not counted). - open_sprint_issues: count distinct issues that are marked as sprint-active and open on any recorded day. - resolved_sprint_issues: count distinct issues whose resolution timestamp is on or before the sprint end and for which there is at least one daily record on or after the resolution date (distinct prevents multi-day double counting). - Commit-at-start metrics (snapshot at sprint start, or today''s snapshot for future-start sprints): - Filter rows where date_day equals the sprint start date, or where date_day equals today and the sprint start date is in the future. - story_points_committed and story_point_estimate_committed: sum values with per-row NULL treated as 0. - issues_committed: count distinct issue_id in the filtered set. - If no rows match this filter for a sprint_id, these fields are NULL after the LEFT JOIN. - End-of-sprint metrics (snapshot on the sprint end date): - Filter rows where date_day equals the sprint end date. - story_points_end and story_point_estimate_end: sum values with per-row NULL treated as 0. - story_points_completed and story_point_estimate_completed: sum values only for rows where the issue is marked resolved-in-sprint; NULL values are ignored by the SUM; if the end snapshot exists but none qualify, the sum is 0; if no end snapshot exists, the value is NULL. - Final assembly: - LEFT JOIN the issue, start, and end metrics to the metadata by sprint_id. - For original_estimate_seconds, remaining_estimate_seconds, and time_spent_seconds, sum across all distinct metadata rows for each sprint_id, treating NULL as 0; other selected fields are carried through to produce one row per sprint_id.'
      columns:
      - name: sprint_id
        data_type: VARCHAR
        description: Sprint primary key from daily history; grouping key for all metrics
        tests:
        - not_null
      - name: sprint_name
        data_type: VARCHAR
        description: Sprint name from daily history
      - name: sprint_started_at
        data_type: TIMESTAMP
        description: Sprint planned start timestamp from daily history
      - name: sprint_ended_at
        data_type: TIMESTAMP
        description: Sprint planned end timestamp from daily history
      - name: sprint_completed_at
        data_type: TIMESTAMP
        description: Timestamp when the sprint was completed (may be NULL if not completed)
      - name: board_id
        data_type: VARCHAR
        description: Board identifier associated with the sprint
      - name: story_points_committed
        data_type: HUGEINT
        description: Sum of story_points at the start snapshot or today's snapshot for future sprints; per-row NULLs treated as 0; NULL if no start snapshot
      - name: story_point_estimate_committed
        data_type: HUGEINT
        description: Sum of story_point_estimate at the start snapshot or today's snapshot for future sprints; per-row NULLs treated as 0; NULL if no start snapshot
      - name: story_points_end
        data_type: HUGEINT
        description: Sum of story_points on the sprint end date; per-row NULLs treated as 0; NULL if no end snapshot
      - name: story_point_estimate_end
        data_type: HUGEINT
        description: Sum of story_point_estimate on the sprint end date; per-row NULLs treated as 0; NULL if no end snapshot
      - name: story_points_completed
        data_type: HUGEINT
        description: Sum of story_points for issues marked resolved in the sprint on the end snapshot; 0 if snapshot exists but none qualify; NULL if no end snapshot
      - name: story_point_estimate_completed
        data_type: HUGEINT
        description: Sum of story_point_estimate for issues marked resolved in the sprint on the end snapshot; 0 if snapshot exists but none qualify; NULL if no end snapshot
      - name: sprint_assignees
        data_type: BIGINT
        description: Distinct assignee_user_id count across all daily rows (NULLs not counted)
      - name: sprint_issues
        data_type: BIGINT
        description: Distinct issue_id count across all daily rows for the sprint_id
      - name: issues_committed
        data_type: BIGINT
        description: Distinct issue count at the start snapshot; NULL if no start snapshot
      - name: open_sprint_issues
        data_type: BIGINT
        description: Distinct issues active in the sprint and open on any recorded day
      - name: resolved_sprint_issues
        data_type: BIGINT
        description: Distinct issues resolved on or before sprint end and with a daily record on or after their resolution date
      - name: original_estimate_seconds
        data_type: DOUBLE
        description: Sum of original_estimate_seconds across distinct metadata rows; NULLs treated as 0; unit seconds
      - name: remaining_estimate_seconds
        data_type: DOUBLE
        description: Sum of remaining_estimate_seconds across distinct metadata rows; NULLs treated as 0; unit seconds
      - name: time_spent_seconds
        data_type: DOUBLE
        description: Sum of time_spent_seconds across distinct metadata rows; NULLs treated as 0; unit seconds
```

### 逐点结论

#### story_points_committed

并列；**Quiet Downgrade**；把握高。

story_points_committed直接NULL，未用已有字段历史/issue/sprint窗口计算；不是原始列不存在。finish点名sprint performance analytics，不是一一对应的sprint_enhanced；只适用笼统复杂指标未完成，第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 298 | 298 | 2086 | 1788 |
| L1 | 298 | 298 | 2086 | 1788 |
| L2 | 298 | 298 | 2086 | 1788 |
| L3 | 298 | 298 | 2086 | 1788 |

重跑：`records/021_detailed_reruns_impl-011_jira__sprint_enhanced.json` / `story_points_committed`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
少数复杂分析并未完整实现合同中的每个指标/分支。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql` / `SQL.text`（sql）：

```text
null::hugeint story_points_committed
```

#### story_point_estimate_committed

并列；**Quiet Downgrade**；把握高。

story_point_estimate_committed直接NULL，未用已有字段历史/issue/sprint窗口计算；不是原始列不存在。finish点名sprint performance analytics，不是一一对应的sprint_enhanced；只适用笼统复杂指标未完成，第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 298 | 298 | 2086 | 1788 |
| L1 | 298 | 298 | 2086 | 1788 |
| L2 | 298 | 298 | 2086 | 1788 |
| L3 | 298 | 298 | 2086 | 1788 |

重跑：`records/021_detailed_reruns_impl-011_jira__sprint_enhanced.json` / `story_point_estimate_committed`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
少数复杂分析并未完整实现合同中的每个指标/分支。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql` / `SQL.text`（sql）：

```text
null::hugeint story_point_estimate_committed
```

#### story_points_end

并列；**Quiet Downgrade**；把握高。

story_points_end直接NULL，未用已有字段历史/issue/sprint窗口计算；不是原始列不存在。finish点名sprint performance analytics，不是一一对应的sprint_enhanced；只适用笼统复杂指标未完成，第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 298 | 298 | 2086 | 1788 |
| L1 | 298 | 298 | 2086 | 1788 |
| L2 | 298 | 298 | 2086 | 1788 |
| L3 | 298 | 298 | 2086 | 1788 |

重跑：`records/021_detailed_reruns_impl-011_jira__sprint_enhanced.json` / `story_points_end`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
少数复杂分析并未完整实现合同中的每个指标/分支。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql` / `SQL.text`（sql）：

```text
null::hugeint story_points_end
```

#### story_point_estimate_end

并列；**Quiet Downgrade**；把握高。

story_point_estimate_end直接NULL，未用已有字段历史/issue/sprint窗口计算；不是原始列不存在。finish点名sprint performance analytics，不是一一对应的sprint_enhanced；只适用笼统复杂指标未完成，第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 298 | 298 | 2086 | 1788 |
| L1 | 298 | 298 | 2086 | 1788 |
| L2 | 298 | 298 | 2086 | 1788 |
| L3 | 298 | 298 | 2086 | 1788 |

重跑：`records/021_detailed_reruns_impl-011_jira__sprint_enhanced.json` / `story_point_estimate_end`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
少数复杂分析并未完整实现合同中的每个指标/分支。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql` / `SQL.text`（sql）：

```text
null::hugeint story_point_estimate_end
```

#### story_points_completed

并列；**Quiet Downgrade**；把握高。

story_points_completed直接NULL，未用已有字段历史/issue/sprint窗口计算；不是原始列不存在。finish点名sprint performance analytics，不是一一对应的sprint_enhanced；只适用笼统复杂指标未完成，第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 298 | 298 | 2086 | 1788 |
| L1 | 298 | 298 | 2086 | 1788 |
| L2 | 298 | 298 | 2086 | 1788 |
| L3 | 298 | 298 | 2086 | 1788 |

重跑：`records/021_detailed_reruns_impl-011_jira__sprint_enhanced.json` / `story_points_completed`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
少数复杂分析并未完整实现合同中的每个指标/分支。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql` / `SQL.text`（sql）：

```text
null::hugeint story_points_completed
```

#### story_point_estimate_completed

并列；**Quiet Downgrade**；把握高。

story_point_estimate_completed直接NULL，未用已有字段历史/issue/sprint窗口计算；不是原始列不存在。finish点名sprint performance analytics，不是一一对应的sprint_enhanced；只适用笼统复杂指标未完成，第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 298 | 298 | 2086 | 1788 |
| L1 | 298 | 298 | 2086 | 1788 |
| L2 | 298 | 298 | 2086 | 1788 |
| L3 | 298 | 298 | 2086 | 1788 |

重跑：`records/021_detailed_reruns_impl-011_jira__sprint_enhanced.json` / `story_point_estimate_completed`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
少数复杂分析并未完整实现合同中的每个指标/分支。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql` / `SQL.text`（sql）：

```text
null::hugeint story_point_estimate_completed
```

#### issues_committed

并列；**Quiet Downgrade**；把握高。

issues_committed直接NULL，未用已有字段历史/issue/sprint窗口计算；不是原始列不存在。finish点名sprint performance analytics，不是一一对应的sprint_enhanced；只适用笼统复杂指标未完成，第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 298 | 298 | 2086 | 1788 |
| L1 | 298 | 298 | 2086 | 1788 |
| L2 | 298 | 298 | 2086 | 1788 |
| L3 | 298 | 298 | 2086 | 1788 |

重跑：`records/021_detailed_reruns_impl-011_jira__sprint_enhanced.json` / `issues_committed`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
少数复杂分析并未完整实现合同中的每个指标/分支。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql` / `SQL.text`（sql）：

```text
null::bigint issues_committed
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`，行[2177, 2245]；材料包 `records/021_packages/021_impl-011_jira__sprint_enhanced.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql`；SHA-256 `230eda3392cc2b380fb230cc02d031f9f39454c06d97226ef0571bca075884dd`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / event 55。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 28，失败=True。
  - `records/021_supplement_queries.json` / index 21，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
