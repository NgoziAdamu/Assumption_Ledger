# impl-011_int_jira__issue_calendar_spine（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Intent Misreading**；把握：中；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`C`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 4715176, "cell_scale": 12116456}, "L1": {"row_scale": 4715176, "cell_scale": 12116456}, "L2": {"row_scale": 4715176, "cell_scale": 12116456}, "L3": {"row_scale": 4715176, "cell_scale": 12116456}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| unresolved_open_until | Intent Misreading | 主要 | 4094566 | 10254626 | 4 |
| history_driver | 其他 | 参与 | 1482146 | 4446438 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: int_jira__issue_calendar_spine
      description: Daily calendar spine of Jira issues with open-state window and derived week metrics
      grain: One row per issue_id per date_day
      source_models:
      - staging.stg_jira__issue (issue_id, created_at, resolved_at)
      - intermediate.int_jira__field_history_scd (issue_id, valid_starting_on)
      business_logic: '- Build a daily date spine from 2016-01-01 through seven days after today. - For each issue, derive created_on as the calendar date of created_at. Set open_until to today if the issue is unresolved; otherwise to the calendar date of the field-history valid_starting_on. - Join issues to the date spine and include a row when date_day is on or after created_on and on or before one month after open_until. If multiple history records match, earliest_open_until_date is the minimum open_until for that issue_id and date_day. - Create issue_day_id as an MD5 hash of date_day and issue_id concatenated with no delimiter. - Derive earliest_open_until_week as the Monday start of the week containing earliest_open_until_date. - Limit the final output to date_day not later than today. - Determinism and null policy: - All timestamps are converted to calendar dates; comparisons are inclusive. - Only (issue_id, date_day) pairs that meet the window are emitted; earliest_open_until_date is non-null for all rows. - Grouping enforces one row per (issue_id, date_day); issue_day_id is unique.'
      columns:
      - name: date_day
        data_type: DATE
        description: Calendar date in scope (2016-01-01 through today, inclusive) when the issue is within its open window
        tests:
        - not_null
      - name: issue_id
        data_type: VARCHAR
        description: Jira issue identifier associated with the date_day
        tests:
        - not_null
      - name: issue_day_id
        data_type: VARCHAR
        description: MD5 of date_day and issue_id concatenated with no delimiter; unique per (date_day, issue_id)
        tests:
        - not_null
        - unique
      - name: earliest_open_until_date
        data_type: DATE
        description: Minimum open_until among matched history rows for this (issue_id, date_day); open_until is today if unresolved, else the field-history starting date
      - name: earliest_open_until_week
        data_type: DATE
        description: Monday week start derived from earliest_open_until_date
```

### 逐点结论

#### unresolved_open_until

主要；**Intent Misreading**；把握高。

P：未解决issue也以最后历史记录日期作为结束日。契约明确未解决者延续到today；该条件改变日历范围。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4715176 | 620610 | 12116456 | 1861830 |
| L1 | 4715176 | 620610 | 12116456 | 1861830 |
| L2 | 4715176 | 620610 | 12116456 | 1861830 |
| L3 | 4715176 | 620610 | 12116456 | 1861830 |

重跑：`records/021_fast_reruns_impl-011_int_jira__issue_calendar_spine.json` / `unresolved_open_until`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_calendar_spine.sql` / `SQL.text`（sql）：

```text
with dates as (select unnest(generate_series(date '2016-01-01',current_date,interval 1 day))::date date_day), bounds as (select issue_id,cast(created_at as date) created_on,coalesce(cast(valid_starting_on as date),current_date) open_until from staging.stg_jira__issue i left join intermediate.int_jira__field_history_scd f using(issue_id)), joined as (select b.issue_id,d.date_day,min(b.open_until) earliest_open_until_date from bounds b join dates d on d.date_day>=b.created_on and d.date_day<=b.open_until+interval 1 month group by b.issue_id,d.date_day) select date_day,issue_id,md5(cast(date_day as varchar)||issue_id) issue_day_id,earliest_open_until_date,cast(date_trunc('week',earliest_open_until_date) as date) earliest_open_until_week from joined

```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### history_driver

参与；**其他**；把握中。

agent以issue主表驱动并LEFT JOIN历史，契约写For each issue、Join issues to date spine；gold反而由字段历史驱动，漏掉没有历史的issue。该对照改成history驱动只用于定位gold行范围，不把agent实际做法说反，也不要求为迎合gold排除无历史issue。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 4715176 | 3233030 | 12116456 | 7670018 |
| L1 | 4715176 | 3233030 | 12116456 | 7670018 |
| L2 | 4715176 | 3233030 | 12116456 | 7670018 |
| L3 | 4715176 | 3233030 | 12116456 | 7670018 |

重跑：`records/021_fast_reruns_impl-011_int_jira__issue_calendar_spine.json` / `history_driver`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_calendar_spine.sql` / `SQL.text`（sql）：

```text
from staging.stg_jira__issue i left join intermediate.int_jira__field_history_scd f using(issue_id)
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`，行[1415, 1444]；材料包 `records/021_packages/021_impl-011_int_jira__issue_calendar_spine.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_calendar_spine.sql`；SHA-256 `0abbf26265983866f09b8f7074bd88466f2ef76e7c7ec0f048fc9bb585dfc387`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / event 55。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共1条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 20，失败=False。

## 不确定或没查到的（含规则问题）

- 规则问题：契约For each issue与Join issues to date spine按自然读法包括无历史issue；选其他。若把历史存在视为隐含入选条件则可读为Choice，契约未明写该过滤。与未解决issue必须延续today的明确Intent点分开。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
