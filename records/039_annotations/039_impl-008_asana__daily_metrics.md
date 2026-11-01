# impl-008_asana__daily_metrics（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Unstated Choice**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`A`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 2, "cell_scale": 8}, "L1": {"row_scale": 2, "cell_scale": 8}, "L2": {"row_scale": 2, "cell_scale": 8}, "L3": {"row_scale": 2, "cell_scale": 8}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| source_timezone_midnight | Unstated Choice | 主要 | 2 | 8 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: asana__daily_metrics
      description: Daily counts of tasks created, tasks completed, and their net difference, aggregated by calendar day.
      grain: One row per date_day
      source_models:
      - staging.stg_asana__task (created_at, completed_at)
      business_logic: 'Build two daily aggregates from staging.stg_asana__task: - Creations: for each task, take the calendar day of its creation timestamp; tasks missing a creation timestamp are counted under a single NULL day; count tasks per day and label as task_created. - Completions: for each task with a completion timestamp, take the calendar day of that timestamp; count tasks per day and label as task_completed. Combine both sets without deduplication, then for each day: - tasks_created = total counts from task_created entries for that day (else 0). - tasks_completed = total counts from task_completed entries for that day (else 0). - net_task_change = tasks_created minus tasks_completed. Output one row per day present in either set (including a NULL day if any tasks lack a creation timestamp), ordered ascending by date_day.'
      columns:
      - name: date_day
        data_type: TIMESTAMP WITH TIME ZONE
        description: Calendar day used for aggregation (midnight in its time zone); may be NULL only from missing created_at; one row per distinct value.
      - name: tasks_created
        data_type: HUGEINT
        description: Number of tasks whose creation timestamp falls on date_day; 0 if none; never NULL.
      - name: tasks_completed
        data_type: HUGEINT
        description: Number of tasks with a completion timestamp that falls on date_day; 0 if none; never NULL.
      - name: net_task_change
        data_type: HUGEINT
        description: tasks_created minus tasks_completed for the same date_day; can be negative; never NULL.
```

### 逐点结论

#### source_timezone_midnight

主要；**Unstated Choice**；把握高。

P：daily日界使用UTC午夜。契约涉及日期/午夜但未定源+08日界还是UTC日界；两种合理的时间归属改变2行8格，不是大面积解析失败。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2 | 0 | 8 | 0 |
| L1 | 2 | 0 | 8 | 0 |
| L2 | 2 | 0 | 8 | 0 |
| L3 | 2 | 0 | 8 | 0 |

重跑：`records/021_supplement_reruns_impl-008_asana__daily_metrics.json` / `source_timezone_midnight`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__daily_metrics.sql` / `SQL.text`（sql）：

```text
CAST(CAST(created_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC'
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`，行[974, 992]；材料包 `records/021_packages/021_impl-008_asana__daily_metrics.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__daily_metrics.sql`；SHA-256 `50c63fceadae16678066be2db07b734b1a976521f618de20908581930dfab83b`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / event 53。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共1条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 2，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
