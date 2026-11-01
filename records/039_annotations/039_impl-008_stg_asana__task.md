# impl-008_stg_asana__task（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`O`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 2102, "cell_scale": 2623}, "L1": {"row_scale": 2102, "cell_scale": 2623}, "L2": {"row_scale": 2102, "cell_scale": 2623}, "L3": {"row_scale": 829, "cell_scale": 829}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| due_source_choice | Unstated Choice | 参与 | 584 | 829 | 4 |
| due_gold_type | 其他 | 主要 | 631 | 907 | 2 |
| start_gold_type | 其他 | 参与 | 366 | 887 | 2 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: stg_asana__task
      description: "Standardized task entities with validated completion status, dates, and assignment relationships. Uses robust parsing and pattern checks to exclude rows where modified_at is clearly non-date text; other non-parsable date fields are set to NULL."
      source_table: "raw.task_data"
      columns:
        - name: task_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: assignee_user_id
          data_type: BIGINT
        - name: is_completed
          data_type: BOOLEAN
          constraints: [not_null]
        - name: completed_at
          data_type: TIMESTAMP
        - name: completed_by_user_id
          data_type: BIGINT
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: due_date
          data_type: TIMESTAMP
        - name: modified_at
          data_type: TIMESTAMP
        - name: task_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: parent_task_id
          data_type: BIGINT
        - name: start_date
          data_type: TIMESTAMP
        - name: task_description
          data_type: VARCHAR
        - name: workspace_id
          data_type: BIGINT

```

### 逐点结论

#### due_source_choice

参与；**Unstated Choice**；把握高。

P：due_at优先于due_on。契约未写两列优先级；非解析失败或把明确有效值变空。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2102 | 1518 | 2623 | 1794 |
| L1 | 2102 | 1518 | 2623 | 1794 |
| L2 | 2102 | 1518 | 2623 | 1794 |
| L3 | 829 | 0 | 829 | 0 |

重跑：`records/021_supplement_reruns_impl-008_stg_asana__task.json` / `due_source_choice`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/staging/stg_asana__task.sql` / `SQL.text`（sql）：

```text
COALESCE(CAST(TRY_STRPTIME(due_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP), CAST(TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP))
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### due_gold_type

主要；**其他**；把握高。

契约规定TIMESTAMP，agent无时区时间满足类型；gold按TIMESTAMPTZ时刻比较。该点只诊断gold类型/时区呈现不一致，不把gold选择当agent应遵守的规则。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2102 | 1471 | 2623 | 1716 |
| L1 | 2102 | 1471 | 2623 | 1716 |
| L2 | 2102 | 1471 | 2623 | 1716 |
| L3 | 829 | 829 | 829 | 829 |

重跑：`records/021_supplement_reruns_impl-008_stg_asana__task.json` / `due_gold_type`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / `53.args.final_thought`（delivery）：

```text
日期文本使用 `TRY_STRPTIME` 处理源数据中 `+0800` 时区格式，无法解析的可选日期会转为 NULL。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/staging/stg_asana__task.sql` / `SQL.text`（sql）：

```text
COALESCE(CAST(TRY_STRPTIME(due_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP), CAST(TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP))
```

#### start_gold_type

参与；**其他**；把握高。

契约规定TIMESTAMP，agent无时区时间满足类型；gold按TIMESTAMPTZ时刻比较。该点只诊断gold类型/时区呈现不一致，不把gold选择当agent应遵守的规则。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2102 | 1736 | 2623 | 1736 |
| L1 | 2102 | 1736 | 2623 | 1736 |
| L2 | 2102 | 1736 | 2623 | 1736 |
| L3 | 829 | 829 | 829 | 829 |

重跑：`records/021_supplement_reruns_impl-008_stg_asana__task.json` / `start_gold_type`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / `53.args.final_thought`（delivery）：

```text
日期文本使用 `TRY_STRPTIME` 处理源数据中 `+0800` 时区格式，无法解析的可选日期会转为 NULL。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/staging/stg_asana__task.sql` / `SQL.text`（sql）：

```text
CAST(TRY_STRPTIME(start_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP)
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`，行[117, 151]；材料包 `records/021_packages/021_impl-008_stg_asana__task.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/staging/stg_asana__task.sql`；SHA-256 `ea60d0bb38b23b4c5e7043d46e7e3d8a9e3ac5aac702ea3ba578de4a08248bb9`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / event 53。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 7，失败=False。
  - `records/021_supplement_queries.json` / index 1，失败=False。

## 不确定或没查到的（含规则问题）

- 原021 due_date/start_date解析替换不改善差异，不另计Data点；分开源列优先级与gold类型。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
