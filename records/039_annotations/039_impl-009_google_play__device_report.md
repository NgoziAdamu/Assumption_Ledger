# impl-009_google_play__device_report（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Quiet Downgrade**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 1360, "cell_scale": 19040}, "L1": {"row_scale": 1360, "cell_scale": 19040}, "L2": {"row_scale": 1360, "cell_scale": 19040}, "L3": {"row_scale": 1360, "cell_scale": 19040}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| device_installs | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| device_uninstalls | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| device_upgrades | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| user_installs | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| user_uninstalls | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| active_devices_last_30_days | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| install_events | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| uninstall_events | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| update_events | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| average_rating | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| rolling_total_average_rating | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| total_device_installs | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| total_device_uninstalls | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| net_device_installs | Quiet Downgrade | 并列 | 0 | 1360 | 2 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: google_play__device_report
      description: Device-level daily performance joined from installs and ratings with forward-filled cumulative totals.
      grain: Rows per package_name, device, date_day from the full outer join; duplicates may exist if sources contain duplicates.
      source_models:
      - staging.stg_google_play__stats_installs_device
      - staging.stg_google_play__stats_ratings_device
      business_logic: '- Read installs and ratings from their staging sources. - In installs, compute running totals by device and package_name ordered by date_day ascending: - total_device_installs accumulates daily_device_installs. - total_device_uninstalls accumulates daily_device_uninstalls. - Full outer join installs and ratings on date_day and package_name, and match device values treating NULLs as equal; choose date_day, device, and package_name from the non-NULL side. - Set daily install/user/event metrics and active_devices_last_30_days to 0 when missing; keep ratings as provided: - average_rating comes from the daily rating. - rolling_total_average_rating comes from the life-to-date rating on that day. - Forward-fill within each device and package_name over ascending date_day: - Carry the latest non-NULL rolling_total_average_rating forward; it remains NULL until the first non-NULL appears. - Carry the latest non-NULL total_device_installs and total_device_uninstalls forward. - Finalize: - Replace remaining NULLs in total_device_installs and total_device_uninstalls with 0. - Compute net_device_installs as total_device_installs minus total_device_uninstalls. - Notes: - All running and forward-fill operations are ordered by date_day ascending. - No de-duplication is performed; if sources contain multiple rows for the same keys and date, all are retained.'
      columns:
      - name: date_day
        data_type: DATE
        description: Calendar date used to align and order metrics.
        tests:
        - not_null
      - name: device
        data_type: VARCHAR
        description: Device identifier chosen from installs or ratings; may be NULL only if missing in both sources.
      - name: package_name
        data_type: VARCHAR
        description: Google Play package identifier chosen from installs or ratings.
      - name: device_installs
        data_type: BIGINT
        description: Daily device installs from installs; NULLs are set to 0.
        tests:
        - device_installs >= 0
      - name: device_uninstalls
        data_type: BIGINT
        description: Daily device uninstalls from installs; NULLs are set to 0.
        tests:
        - device_uninstalls >= 0
      - name: device_upgrades
        data_type: BIGINT
        description: Daily device upgrades from installs; NULLs are set to 0.
        tests:
        - device_upgrades >= 0
      - name: user_installs
        data_type: BIGINT
        description: Daily user installs from installs; NULLs are set to 0.
        tests:
        - user_installs >= 0
      - name: user_uninstalls
        data_type: BIGINT
        description: Daily user uninstalls from installs; NULLs are set to 0.
        tests:
        - user_uninstalls >= 0
      - name: install_events
        data_type: BIGINT
        description: Daily install events from installs; NULLs are set to 0.
        tests:
        - install_events >= 0
      - name: uninstall_events
        data_type: BIGINT
        description: Daily uninstall events from installs; NULLs are set to 0.
        tests:
        - uninstall_events >= 0
      - name: update_events
        data_type: BIGINT
        description: Daily update events from installs; NULLs are set to 0.
        tests:
        - update_events >= 0
      - name: active_devices_last_30_days
        data_type: BIGINT
        description: Active devices in the last 30 days from installs; NULLs are set to 0.
        tests:
        - active_devices_last_30_days >= 0
      - name: average_rating
        data_type: DECIMAL(18,3)
        description: Daily average rating from ratings; may be NULL when no rating is reported.
      - name: rolling_total_average_rating
        data_type: DECIMAL(18,3)
        description: Life-to-date average rating forward-filled within device+package by ascending date; NULL until the first non-NULL.
      - name: total_device_installs
        data_type: HUGEINT
        description: Cumulative device installs within device+package ordered by date, forward-filled, then set to 0 when still missing.
        tests:
        - total_device_installs >= 0
      - name: total_device_uninstalls
        data_type: HUGEINT
        description: Cumulative device uninstalls within device+package ordered by date, forward-filled, then set to 0 when still missing.
        tests:
        - total_device_uninstalls >= 0
      - name: net_device_installs
        data_type: HUGEINT
        description: Difference of cumulative installs and uninstalls after null-to-zero handling; may be negative.
```

### 逐点结论

#### device_installs

并列；**Quiet Downgrade**；把握高。

device_installs为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/021_supplement_reruns_impl-009_google_play__device_report.json` / `device_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
cast(0 as BIGINT) AS device_installs
```

#### device_uninstalls

并列；**Quiet Downgrade**；把握高。

device_uninstalls为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/021_supplement_reruns_impl-009_google_play__device_report.json` / `device_uninstalls`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
cast(0 as BIGINT) AS device_uninstalls
```

#### device_upgrades

并列；**Quiet Downgrade**；把握高。

device_upgrades为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/021_supplement_reruns_impl-009_google_play__device_report.json` / `device_upgrades`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS device_upgrades
```

#### user_installs

并列；**Quiet Downgrade**；把握高。

user_installs为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/021_supplement_reruns_impl-009_google_play__device_report.json` / `user_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS user_installs
```

#### user_uninstalls

并列；**Quiet Downgrade**；把握高。

user_uninstalls为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/021_supplement_reruns_impl-009_google_play__device_report.json` / `user_uninstalls`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS user_uninstalls
```

#### active_devices_last_30_days

并列；**Quiet Downgrade**；把握高。

active_devices_last_30_days为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/021_supplement_reruns_impl-009_google_play__device_report.json` / `active_devices_last_30_days`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS active_devices_last_30_days
```

#### install_events

并列；**Quiet Downgrade**；把握高。

install_events为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/021_reruns_impl-009_google_play__device_report.json` / `install_events`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS install_events
```

#### uninstall_events

并列；**Quiet Downgrade**；把握高。

uninstall_events为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/021_reruns_impl-009_google_play__device_report.json` / `uninstall_events`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS uninstall_events
```

#### update_events

并列；**Quiet Downgrade**；把握高。

update_events为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/021_reruns_impl-009_google_play__device_report.json` / `update_events`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS update_events
```

#### average_rating

并列；**Quiet Downgrade**；把握高。

average_rating被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/039_checks/supplement_impl-009_google_play__device_report.json` / `average_rating`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.device as VARCHAR) AS device,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_device AS src
WHERE src.date_day IS NOT NULL

```

#### rolling_total_average_rating

并列；**Quiet Downgrade**；把握高。

rolling_total_average_rating被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/039_checks/supplement_impl-009_google_play__device_report.json` / `rolling_total_average_rating`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.device as VARCHAR) AS device,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_device AS src
WHERE src.date_day IS NOT NULL

```

#### total_device_installs

并列；**Quiet Downgrade**；把握高。

total_device_installs被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/039_checks/supplement_impl-009_google_play__device_report.json` / `total_device_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.device as VARCHAR) AS device,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_device AS src
WHERE src.date_day IS NOT NULL

```

#### total_device_uninstalls

并列；**Quiet Downgrade**；把握高。

total_device_uninstalls被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/039_checks/supplement_impl-009_google_play__device_report.json` / `total_device_uninstalls`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.device as VARCHAR) AS device,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_device AS src
WHERE src.date_day IS NOT NULL

```

#### net_device_installs

并列；**Quiet Downgrade**；把握高。

net_device_installs被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 19040 | 17680 |
| L1 | 1360 | 1360 | 19040 | 17680 |
| L2 | 1360 | 1360 | 19040 | 17680 |
| L3 | 1360 | 1360 | 19040 | 17680 |

重跑：`records/039_checks/supplement_impl-009_google_play__device_report.json` / `net_device_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.device as VARCHAR) AS device,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_device AS src
WHERE src.date_day IS NOT NULL

```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，行[1640, 1722]；材料包 `records/021_packages/021_impl-009_google_play__device_report.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__device_report.sql`；SHA-256 `c68500309e0c2e4e3a7c135b70dab7419c8500627c18814f287b7ea41e7acea8`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / event 67。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 12，失败=True。
  - `records/021_supplement_queries.json` / index 13，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
