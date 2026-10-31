# DAComp / impl-011_stg_jira__issue（v3）

## 错在哪里
三个估算/耗时字段优先使用带下划线列，gold优先同名列，契约未规定优先级。

证据复用入口：[018_impl-011_stg_jira__issue.md](../018_annotations/018_impl-011_stg_jira__issue.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## time_spent_priority
- 角色：主要；类别：**Unstated Choice**；把握：中。
- 依据：同名及下划线两列优先级未规定；8000行不降，单改减少8000格。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 10 / content：
```text
 None), ('_remaining_estimate', 'DOUBLE', 'YES', None, None, None), ('_time_spent', 'DOUBLE', 'YES', None, None, None), ('assignee', 'VARCHAR', 'YES', None, None, None), ('created', 'VARCHAR', 'YES', None, None, None), ('creator', 'VARCHAR', 'YES', None, None, None), ('description', 'VARCHAR', 'YES', None, None, None), ('due_date', 'VARCHAR', 'YES', None, None, None), ('environment', 'VARCHAR', 'YES', None, None, None), ('issue_type', 'VARCHAR', 'YES', None, None, None), ('key', 'VARCHAR', 'YES', None, None, None), ('last_viewed', 'VARCHAR', 'YES', None, None, None), ('original_estimate', 'DOUBLE', 'YES', None, None, None), ('parent_id', 'VARCHAR', 'YES', None, None, None), ('priority', 'VARCHAR', 'YES', None, None, None), ('project', 'VARCHAR', 'YES', None, None, None), ('remaining_estimate', 'DOUBLE', 'YES', None, None, None), ('reporter', 'VARCHAR', 'YES', None, None, None), ('resolution', 'VARCHAR', 'YE
```
## original_estimate_priority
- 角色：参与；类别：**Unstated Choice**；把握：中。
- 依据：源列优先级未规定，单改减少7999格。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 10 / content：
```text
 None), ('_remaining_estimate', 'DOUBLE', 'YES', None, None, None), ('_time_spent', 'DOUBLE', 'YES', None, None, None), ('assignee', 'VARCHAR', 'YES', None, None, None), ('created', 'VARCHAR', 'YES', None, None, None), ('creator', 'VARCHAR', 'YES', None, None, None), ('description', 'VARCHAR', 'YES', None, None, None), ('due_date', 'VARCHAR', 'YES', None, None, None), ('environment', 'VARCHAR', 'YES', None, None, None), ('issue_type', 'VARCHAR', 'YES', None, None, None), ('key', 'VARCHAR', 'YES', None, None, None), ('last_viewed', 'VARCHAR', 'YES', None, None, None), ('original_estimate', 'DOUBLE', 'YES', None, None, None), ('parent_id', 'VARCHAR', 'YES', None, None, None), ('priority', 'VARCHAR', 'YES', None, None, None), ('project', 'VARCHAR', 'YES', None, None, None), ('remaining_estimate', 'DOUBLE', 'YES', None, None, None), ('reporter', 'VARCHAR', 'YES', None, None, None), ('resolution', 'VARCHAR', 'YE
```
## remaining_estimate_priority
- 角色：参与；类别：**Unstated Choice**；把握：中。
- 依据：源列优先级未规定，单改减少7999格。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 10 / content：
```text
 None), ('_remaining_estimate', 'DOUBLE', 'YES', None, None, None), ('_time_spent', 'DOUBLE', 'YES', None, None, None), ('assignee', 'VARCHAR', 'YES', None, None, None), ('created', 'VARCHAR', 'YES', None, None, None), ('creator', 'VARCHAR', 'YES', None, None, None), ('description', 'VARCHAR', 'YES', None, None, None), ('due_date', 'VARCHAR', 'YES', None, None, None), ('environment', 'VARCHAR', 'YES', None, None, None), ('issue_type', 'VARCHAR', 'YES', None, None, None), ('key', 'VARCHAR', 'YES', None, None, None), ('last_viewed', 'VARCHAR', 'YES', None, None, None), ('original_estimate', 'DOUBLE', 'YES', None, None, None), ('parent_id', 'VARCHAR', 'YES', None, None, None), ('priority', 'VARCHAR', 'YES', None, None, None), ('project', 'VARCHAR', 'YES', None, None, None), ('remaining_estimate', 'DOUBLE', 'YES', None, None, None), ('reporter', 'VARCHAR', 'YES', None, None, None), ('resolution', 'VARCHAR', 'YE
```

## 规模、证据复用与新做
主要原因：Unstated Choice。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-011_stg_jira__issue.md](../018_annotations/018_impl-011_stg_jira__issue.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_jira__issue
      description: "Cleaned JIRA issues with validated statuses, standardized timestamps, and consistent foreign key references"
      source_table: "raw.issue"
      columns:
        - name: issue_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: issue_key
          data_type: VARCHAR
          constraints: [not_null]
        - name: issue_name
          data_type: VARCHAR
        - name: issue_description
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: resolved_at
          data_type: TIMESTAMP
        - name: updated_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: project_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: assignee_user_id
          data_type: VARCHAR
        - name: reporter_user_id
          data_type: VARCHAR
        - name: creator_user_id
          data_type: VARCHAR
        - name: status_id
          data_type: VARCHAR
        - name: priority_id
          data_type: VARCHAR
        - name: issue_type_id
          data_type: VARCHAR
        - name: resolution_id
          data_type: VARCHAR
        - name: parent_issue_id
          data_type: VARCHAR
        - name: due_date
          data_type: VARCHAR
        - name: environment
          data_type: VARCHAR
        - name: status_changed_at
          data_type: TIMESTAMP
        - name: original_estimate_seconds
          data_type: DOUBLE
        - name: remaining_estimate_seconds
          data_type: DOUBLE
        - name: time_spent_seconds
          data_type: DOUBLE
        - name: work_ratio
          data_type: DOUBLE

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-011_stg_jira__issue.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-011_stg_jira__issue.md:88)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-011_stg_jira__issue.md:296)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-011_stg_jira__issue.md:337)
- [重跑 original_estimate_priority](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-011_stg_jira__issue.md:374)
- [重跑 remaining_estimate_priority](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-011_stg_jira__issue.md:418)
- [重跑 time_spent_priority](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-011_stg_jira__issue.md:462)
