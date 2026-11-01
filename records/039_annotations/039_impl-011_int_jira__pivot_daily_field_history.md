# impl-011_int_jira__pivot_daily_field_history（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`C`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 9755, "cell_scale": 29264}, "L1": {"row_scale": 9755, "cell_scale": 29264}, "L2": {"row_scale": 9755, "cell_scale": 29264}, "L3": {"row_scale": 9755, "cell_scale": 29264}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| status | Intent Misreading | 参与 | 0 | 9738 | 4 |
| sprint | Intent Misreading | 参与 | 0 | 2025 | 4 |
| story_points | Intent Misreading | 参与 | 0 | 7746 | 4 |
| story_point_estimate | Intent Misreading | 主要 | 0 | 9755 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: int_jira__pivot_daily_field_history
      description: Daily pivot of latest status, sprint, story points, and story point estimate per issue on days with changes
      grain: One row per issue_id per valid_starting_on (only days with a change in any pivoted field)
      source_models:
      - intermediate.int_jira__issue_field_history
      - intermediate.int_jira__issue_multiselect_history
      business_logic: '- Read single-value field changes from intermediate.int_jira__issue_field_history and multiselect field changes from intermediate.int_jira__issue_multiselect_history. - For multiselect changes, aggregate all values per (field_id, field_name, issue_id, updated_at) into one string joined by ", "; duplicates are preserved; NULL inputs are excluded; no ordering is enforced in the concatenation. - Union the aggregated multiselect changes with the single-value changes. - For each issue and field, each change timestamp starts a validity period that lasts until the next change; also derive the calendar date of the start. - Keep only relevant fields: status by field_id (case-insensitive), and sprint, story points, story point estimate by field_name (case-insensitive). - For each issue, field, and calendar date, retain the last change of that day (the highest change timestamp for that day; no tie-breaker beyond timestamp). - Replace a NULL field value with the literal "is_null"; otherwise keep the original text (including any comma-joined multiselect values). - Pivot to columns: status from field_id; sprint, story points, and story point estimate from field_name. Group by issue and date, and carry the week-start of the selected change timestamp. Use max as a pass-through since there is at most one selected value per field per day. - Output includes only dates where at least one relevant field changed for the issue. Unchanged fields on that date remain NULL; fields changed to true NULL appear as "is_null". - Compute issue_day_id as the MD5 of valid_starting_on concatenated with issue_id, with no delimiter.'
      columns:
      - name: valid_starting_on
        data_type: DATE
        description: Calendar date on which the day's selected field updates became valid
        tests:
        - not_null
      - name: issue_id
        data_type: VARCHAR
        description: Jira issue identifier for the daily pivot row
        tests:
        - not_null
      - name: valid_starting_at_week
        data_type: DATE
        description: Week start date based on the selected change timestamp for the day
      - name: status
        data_type: VARCHAR
        description: Latest status recorded that day; 'is_null' if the latest status was NULL; otherwise NULL when status did not change that day
      - name: sprint
        data_type: VARCHAR
        description: Latest sprint value(s) recorded that day as a comma-separated list; 'is_null' if the latest sprint was NULL; otherwise NULL when sprint did not change that day
      - name: story_points
        data_type: VARCHAR
        description: Latest 'story points' recorded that day; 'is_null' if the latest value was NULL; otherwise NULL when it did not change that day
      - name: story_point_estimate
        data_type: VARCHAR
        description: Latest 'story point estimate' recorded that day; 'is_null' if the latest value was NULL; otherwise NULL when it did not change that day
      - name: issue_day_id
        data_type: VARCHAR
        description: MD5 hash of valid_starting_on and issue_id concatenated with no delimiter
        tests:
        - not_null
```

### 逐点结论

#### status

参与；**Intent Misreading**；把握高。

P：status在透视后统一COALESCE为is_null。契约要求在透视前把真实NULL变更标为is_null，未变更字段在透视后仍为NULL；agent把未变更也写成is_null，改变明确的状态语义。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 9755 | 9755 | 29264 | 19526 |
| L1 | 9755 | 9755 | 29264 | 19526 |
| L2 | 9755 | 9755 | 29264 | 19526 |
| L3 | 9755 | 9755 | 29264 | 19526 |

重跑：`records/021_reruns_impl-011_int_jira__pivot_daily_field_history.json` / `status`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql` / `SQL.text`（sql）：

```text
max(field_value) filter(where lower(field_id)='status') status
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### sprint

参与；**Intent Misreading**；把握高。

P：sprint在透视后统一COALESCE为is_null。契约要求在透视前把真实NULL变更标为is_null，未变更字段在透视后仍为NULL；agent把未变更也写成is_null，改变明确的状态语义。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 9755 | 9755 | 29264 | 27239 |
| L1 | 9755 | 9755 | 29264 | 27239 |
| L2 | 9755 | 9755 | 29264 | 27239 |
| L3 | 9755 | 9755 | 29264 | 27239 |

重跑：`records/021_reruns_impl-011_int_jira__pivot_daily_field_history.json` / `sprint`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql` / `SQL.text`（sql）：

```text
max(field_value) filter(where lower(field_name)='sprint') sprint
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### story_points

参与；**Intent Misreading**；把握高。

P：story_points在透视后统一COALESCE为is_null。契约要求在透视前把真实NULL变更标为is_null，未变更字段在透视后仍为NULL；agent把未变更也写成is_null，改变明确的状态语义。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 9755 | 9755 | 29264 | 21518 |
| L1 | 9755 | 9755 | 29264 | 21518 |
| L2 | 9755 | 9755 | 29264 | 21518 |
| L3 | 9755 | 9755 | 29264 | 21518 |

重跑：`records/021_reruns_impl-011_int_jira__pivot_daily_field_history.json` / `story_points`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql` / `SQL.text`（sql）：

```text
max(field_value) filter(where lower(field_name)='story points') story_points
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### story_point_estimate

主要；**Intent Misreading**；把握高。

P：story_point_estimate在透视后统一COALESCE为is_null。契约要求在透视前把真实NULL变更标为is_null，未变更字段在透视后仍为NULL；agent把未变更也写成is_null，改变明确的状态语义。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 9755 | 9755 | 29264 | 19509 |
| L1 | 9755 | 9755 | 29264 | 19509 |
| L2 | 9755 | 9755 | 29264 | 19509 |
| L3 | 9755 | 9755 | 29264 | 19509 |

重跑：`records/021_reruns_impl-011_int_jira__pivot_daily_field_history.json` / `story_point_estimate`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql` / `SQL.text`（sql）：

```text
max(field_value) filter(where lower(field_name)='story point estimate') story_point_estimate
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`，行[1716, 1753]；材料包 `records/021_packages/021_impl-011_int_jira__pivot_daily_field_history.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql`；SHA-256 `60a973a17bdc42d140f9f9825153e8ddc47acf1c9fb996dc4ccebc3d143adf67`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / event 55。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共1条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 23，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
