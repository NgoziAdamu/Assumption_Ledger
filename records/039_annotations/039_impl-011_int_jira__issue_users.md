# impl-011_int_jira__issue_users（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**代码写错**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`I`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 13, "cell_scale": 13}, "L1": {"row_scale": 13, "cell_scale": 13}, "L2": {"row_scale": 13, "cell_scale": 13}, "L3": {"row_scale": 13, "cell_scale": 13}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| derived_parent_name | 代码写错 | 主要 | 13 | 13 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: int_jira__issue_users
      description: Issue records from int_jira__issue_type_parents enriched with assignee and reporter attributes; parent_issue_id is derived from revised_parent_issue_id or parent_issue_id
      grain: One row per issue; may produce multiple rows per issue if the user table has duplicate user_id entries
      source_models:
      - intermediate.int_jira__issue_type_parents
      - staging.stg_jira__user
      business_logic: '- Start with all columns from intermediate.int_jira__issue_type_parents. - Derive parent_issue_id by taking revised_parent_issue_id when present; otherwise use the original parent_issue_id; both are treated as text, and the result is null if both are missing. - Keep all source columns unchanged; because issue_id is also selected explicitly, the output includes duplicate source versions named issue_id_1 and parent_issue_id_1. - Join the user table twice using left joins: on assignee_user_id to add assignee_name, assignee_timezone, assignee_email; on reporter_user_id to add reporter_email, reporter_name, reporter_timezone. - No filters, aggregation, or ordering are applied. All issues are retained; unmatched users yield null attributes. If the user table has multiple rows for a user_id, the result may have multiple rows per issue (no de-duplication).'
      columns:
      - name: issue_id
        data_type: VARCHAR
        description: Issue identifier selected explicitly from the source
        tests:
        - not_null
      - name: parent_issue_id
        data_type: VARCHAR
        description: 'Derived parent identifier: use revised_parent_issue_id when present, otherwise the original parent_issue_id; stored as text; null if both are missing'
      - name: original_estimate_seconds
        data_type: DOUBLE
        description: Original time estimate in seconds from the source
        tests:
        - original_estimate_seconds IS NULL OR original_estimate_seconds >= 0
      - name: remaining_estimate_seconds
        data_type: DOUBLE
        description: Remaining time estimate in seconds from the source
        tests:
        - remaining_estimate_seconds IS NULL OR remaining_estimate_seconds >= 0
      - name: time_spent_seconds
        data_type: DOUBLE
        description: Time spent in seconds from the source
        tests:
        - time_spent_seconds IS NULL OR time_spent_seconds >= 0
      - name: assignee_user_id
        data_type: VARCHAR
        description: Assignee user identifier from the source used to join user attributes
      - name: created_at
        data_type: TIMESTAMP
        description: Issue creation timestamp from the source
        tests:
        - not_null
      - name: resolved_at
        data_type: TIMESTAMP
        description: Issue resolution timestamp from the source; may be null
      - name: creator_user_id
        data_type: VARCHAR
        description: Creator user identifier from the source
      - name: issue_description
        data_type: VARCHAR
        description: Issue description text from the source
      - name: due_date
        data_type: VARCHAR
        description: Due date as stored in the source text; no parsing or conversion
      - name: environment
        data_type: VARCHAR
        description: Environment field from the source
      - name: issue_id_1
        data_type: VARCHAR
        description: Duplicate of the original issue_id retained when all source columns are included
      - name: issue_type_id
        data_type: VARCHAR
        description: Issue type identifier from the source
      - name: issue_key
        data_type: VARCHAR
        description: Human-readable issue key from the source
        tests:
        - not_null
      - name: parent_issue_id_1
        data_type: VARCHAR
        description: Original parent_issue_id from the source retained alongside the derived parent_issue_id
      - name: priority_id
        data_type: VARCHAR
        description: Priority identifier from the source
      - name: project_id
        data_type: VARCHAR
        description: Project identifier from the source
        tests:
        - not_null
      - name: reporter_user_id
        data_type: VARCHAR
        description: Reporter user identifier from the source used to join user attributes
      - name: resolution_id
        data_type: VARCHAR
        description: Resolution identifier from the source
      - name: status_id
        data_type: VARCHAR
        description: Status identifier from the source
      - name: status_changed_at
        data_type: TIMESTAMP
        description: Timestamp of the last status change from the source
      - name: issue_name
        data_type: VARCHAR
        description: Issue summary or title from the source
      - name: updated_at
        data_type: TIMESTAMP
        description: Last update timestamp from the source
        tests:
        - not_null
      - name: work_ratio
        data_type: DOUBLE
        description: Work completion ratio from the source
        tests:
        - work_ratio IS NULL OR work_ratio >= 0
      - name: revised_parent_issue_id
        data_type: VARCHAR
        description: Revised parent issue identifier used to derive parent_issue_id
      - name: issue_type
        data_type: VARCHAR
        description: Issue type name from the source
      - name: parent_issue_type
        data_type: VARCHAR
        description: Parent issue type name from the source
      - name: parent_issue_name
        data_type: VARCHAR
        description: Parent issue name from the source
      - name: parent_issue_key
        data_type: VARCHAR
        description: Parent issue key from the source
      - name: is_parent_epic
        data_type: BOOLEAN
        description: Indicates whether the parent issue is an epic, as provided by the source
      - name: assignee_name
        data_type: VARCHAR
        description: Assignee display name from the user table; null if no matching user
      - name: assignee_timezone
        data_type: VARCHAR
        description: Assignee time zone from the user table; null if no matching user
      - name: assignee_email
        data_type: VARCHAR
        description: Assignee email from the user table; null if no matching user
      - name: reporter_email
        data_type: VARCHAR
        description: Reporter email from the user table; null if no matching user
      - name: reporter_name
        data_type: VARCHAR
        description: Reporter display name from the user table; null if no matching user
      - name: reporter_timezone
        data_type: VARCHAR
        description: Reporter time zone from the user table; null if no matching user
```

### 逐点结论

#### derived_parent_name

主要；**代码写错**；把握高。

原SQL已计算正确coalesce(revised_parent_issue_id,parent_issue_id)，却命名parent_issue_id_derived；i.*保留未修正parent_issue_id。正确意图在代码中明确，实际交付列未被替换。finish只说已修复别名问题，不是披露本处仍有别名错误或采用何种默认处理，故不记第2档。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 0 | 13 | 0 |
| L1 | 13 | 0 | 13 | 0 |
| L2 | 13 | 0 | 13 | 0 |
| L3 | 13 | 0 | 13 | 0 |

重跑：`records/021_reruns_impl-011_int_jira__issue_users.json` / `derived_parent_name`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_users.sql` / `SQL.text`（sql）：

```text
i.*,coalesce(i.revised_parent_issue_id,i.parent_issue_id) parent_issue_id_derived
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`，行[1559, 1695]；材料包 `records/021_packages/021_impl-011_int_jira__issue_users.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_users.sql`；SHA-256 `d534cb67aa6c25fae9fc4c847d6673474758c223963d94d8ae3ca67f8ff00972`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / event 55。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共1条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 22，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
