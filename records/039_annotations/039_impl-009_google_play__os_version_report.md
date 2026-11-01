# impl-009_google_play__os_version_report（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Quiet Downgrade**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 1360, "cell_scale": 22716}, "L1": {"row_scale": 1360, "cell_scale": 22722}, "L2": {"row_scale": 1360, "cell_scale": 22722}, "L3": {"row_scale": 1360, "cell_scale": 22722}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| device_installs | Quiet Downgrade | 参与 | 0 | 275 | 2 |
| device_uninstalls | Quiet Downgrade | 参与 | 0 | 314 | 2 |
| device_upgrades | Quiet Downgrade | 参与 | 0 | 276 | 2 |
| user_installs | Quiet Downgrade | 参与 | 0 | 278 | 2 |
| user_uninstalls | Quiet Downgrade | 参与 | 0 | 314 | 2 |
| active_devices_last_30_days | Quiet Downgrade | 主要 | 0 | 2451 | 2 |
| install_events | Quiet Downgrade | 参与 | 0 | 280 | 2 |
| uninstall_events | Quiet Downgrade | 参与 | 0 | 303 | 2 |
| update_events | Quiet Downgrade | 参与 | 0 | 278 | 2 |
| crashes | Quiet Downgrade | 参与 | 0 | 236 | 2 |
| anrs | Quiet Downgrade | 参与 | 0 | 212 | 2 |
| average_rating | Quiet Downgrade | 参与 | 0 | 286 | 2 |
| rolling_total_average_rating | Quiet Downgrade | 参与 | 0 | 278 | 2 |
| total_device_installs | Quiet Downgrade | 参与 | 0 | 272 | 2 |
| total_device_uninstalls | Quiet Downgrade | 参与 | 0 | 277 | 2 |
| net_device_installs | Quiet Downgrade | 参与 | 0 | 273 | 2 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: google_play__os_version_report
      description: Daily Google Play metrics by package and Android OS version with installs, events, crashes, ratings, and cumulative totals
      grain: One row per package_name, android_os_version, date_day (emitted when any source has data)
      source_models:
      - staging.stg_google_play__stats_installs_os_version
      - staging.stg_google_play__stats_crashes_os_version
      - staging.stg_google_play__stats_ratings_os_version
      business_logic: '- Source tables: installs, ratings, and crashes at a daily, package, and Android OS version level. - In installs, compute running cumulative totals of device installs and device uninstalls per package_name and android_os_version, ordered by date_day ascending and inclusive of the current day. - Full outer join installs, ratings, and crashes on date_day, package_name, and android_os_version: - For join equality only, treat NULL android_os_version as the placeholder ''null_os'' to align NULLs across sources. - Output keys (date_day, package_name, android_os_version) are the coalesced values across sources; if all are NULL for a key, the output remains NULL. - Rows are emitted when any source has data; duplicates in sources are not deduplicated. - Null handling: - Device/user counts, event counts, crashes, ANRs, and active devices are set to 0 when missing from their source. - average_rating and rolling_total_average_rating from ratings remain nullable. - Forward-fill within each package_name and android_os_version, ordered by date_day ascending: - Carry the most recent non-NULL value forward for rolling_total_average_rating, total_device_installs, and total_device_uninstalls. - Leading periods before the first non-NULL value remain NULL. - After forward-fill, total_device_installs and total_device_uninstalls are set to 0 where still NULL; rolling_total_average_rating remains nullable. - Final calculation: - net_device_installs equals total_device_installs minus total_device_uninstalls. - All windowed operations are ordered by date_day ascending and partitioned by package_name and android_os_version.'
      columns:
      - name: date_day
        data_type: DATE
        description: Metric date coalesced from sources; one row per date per package and OS version when any source has data.
        tests:
        - not_null
      - name: android_os_version
        data_type: VARCHAR
        description: Android OS version coalesced from sources; may be NULL when NULL in all; NULLs matched across sources using 'null_os' only for join equality.
      - name: package_name
        data_type: VARCHAR
        description: Google Play package identifier coalesced from sources.
        tests:
        - not_null
      - name: device_installs
        data_type: BIGINT
        description: Daily device installs from installs; set to 0 when missing.
        tests:
        - device_installs >= 0
      - name: device_uninstalls
        data_type: BIGINT
        description: Daily device uninstalls from installs; set to 0 when missing.
        tests:
        - device_uninstalls >= 0
      - name: device_upgrades
        data_type: BIGINT
        description: Daily device upgrades from installs; set to 0 when missing.
        tests:
        - device_upgrades >= 0
      - name: user_installs
        data_type: BIGINT
        description: Daily user installs from installs; set to 0 when missing.
        tests:
        - user_installs >= 0
      - name: user_uninstalls
        data_type: BIGINT
        description: Daily user uninstalls from installs; set to 0 when missing.
        tests:
        - user_uninstalls >= 0
      - name: install_events
        data_type: BIGINT
        description: Daily install events from installs; set to 0 when missing.
        tests:
        - install_events >= 0
      - name: uninstall_events
        data_type: BIGINT
        description: Daily uninstall events from installs; set to 0 when missing.
        tests:
        - uninstall_events >= 0
      - name: update_events
        data_type: BIGINT
        description: Daily update events from installs; set to 0 when missing.
        tests:
        - update_events >= 0
      - name: crashes
        data_type: BIGINT
        description: Daily crash count from crashes; set to 0 when missing.
        tests:
        - crashes >= 0
      - name: anrs
        data_type: BIGINT
        description: Daily ANR count from crashes; set to 0 when missing.
        tests:
        - anrs >= 0
      - name: active_devices_last_30_days
        data_type: BIGINT
        description: Active devices in the last 30 days from installs; set to 0 when missing.
        tests:
        - active_devices_last_30_days >= 0
      - name: average_rating
        data_type: DECIMAL(18,3)
        description: Daily average rating from ratings; nullable.
      - name: rolling_total_average_rating
        data_type: DECIMAL(18,3)
        description: Total average rating from ratings forward-filled by date within each package and OS; leading gaps remain NULL.
      - name: total_device_installs
        data_type: HUGEINT
        description: Running total of device installs within each package and OS ordered by date, forward-filled across later dates without installs, then set to 0 where still NULL; includes the current date.
        tests:
        - total_device_installs >= 0
      - name: total_device_uninstalls
        data_type: HUGEINT
        description: Running total of device uninstalls within each package and OS ordered by date, forward-filled across later dates without uninstalls, then set to 0 where still NULL; includes the current date.
        tests:
        - total_device_uninstalls >= 0
      - name: net_device_installs
        data_type: HUGEINT
        description: total_device_installs minus total_device_uninstalls after forward-fill and zero-fill; may be negative.
```

### 逐点结论

#### device_installs

参与；**Quiet Downgrade**；把握高。

device_installs为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22441 |
| L1 | 1360 | 1360 | 22722 | 22453 |
| L2 | 1360 | 1360 | 22722 | 22453 |
| L3 | 1360 | 1360 | 22722 | 22453 |

重跑：`records/021_supplement_reruns_impl-009_google_play__os_version_report.json` / `device_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
cast(0 as BIGINT) AS device_installs
```

#### device_uninstalls

参与；**Quiet Downgrade**；把握高。

device_uninstalls为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22402 |
| L1 | 1360 | 1360 | 22722 | 22414 |
| L2 | 1360 | 1360 | 22722 | 22414 |
| L3 | 1360 | 1360 | 22722 | 22414 |

重跑：`records/021_supplement_reruns_impl-009_google_play__os_version_report.json` / `device_uninstalls`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
cast(0 as BIGINT) AS device_uninstalls
```

#### device_upgrades

参与；**Quiet Downgrade**；把握高。

device_upgrades为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22440 |
| L1 | 1360 | 1360 | 22722 | 22451 |
| L2 | 1360 | 1360 | 22722 | 22451 |
| L3 | 1360 | 1360 | 22722 | 22451 |

重跑：`records/021_supplement_reruns_impl-009_google_play__os_version_report.json` / `device_upgrades`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS device_upgrades
```

#### user_installs

参与；**Quiet Downgrade**；把握高。

user_installs为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22438 |
| L1 | 1360 | 1360 | 22722 | 22451 |
| L2 | 1360 | 1360 | 22722 | 22451 |
| L3 | 1360 | 1360 | 22722 | 22451 |

重跑：`records/021_supplement_reruns_impl-009_google_play__os_version_report.json` / `user_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS user_installs
```

#### user_uninstalls

参与；**Quiet Downgrade**；把握高。

user_uninstalls为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22402 |
| L1 | 1360 | 1360 | 22722 | 22414 |
| L2 | 1360 | 1360 | 22722 | 22414 |
| L3 | 1360 | 1360 | 22722 | 22414 |

重跑：`records/021_supplement_reruns_impl-009_google_play__os_version_report.json` / `user_uninstalls`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS user_uninstalls
```

#### active_devices_last_30_days

主要；**Quiet Downgrade**；把握高。

active_devices_last_30_days为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 20265 |
| L1 | 1360 | 1360 | 22722 | 20265 |
| L2 | 1360 | 1360 | 22722 | 20265 |
| L3 | 1360 | 1360 | 22722 | 20265 |

重跑：`records/021_supplement_reruns_impl-009_google_play__os_version_report.json` / `active_devices_last_30_days`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS active_devices_last_30_days
```

#### install_events

参与；**Quiet Downgrade**；把握高。

install_events为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22436 |
| L1 | 1360 | 1360 | 22722 | 22448 |
| L2 | 1360 | 1360 | 22722 | 22448 |
| L3 | 1360 | 1360 | 22722 | 22448 |

重跑：`records/021_reruns_impl-009_google_play__os_version_report.json` / `install_events`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS install_events
```

#### uninstall_events

参与；**Quiet Downgrade**；把握高。

uninstall_events为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22413 |
| L1 | 1360 | 1360 | 22722 | 22426 |
| L2 | 1360 | 1360 | 22722 | 22426 |
| L3 | 1360 | 1360 | 22722 | 22426 |

重跑：`records/021_reruns_impl-009_google_play__os_version_report.json` / `uninstall_events`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS uninstall_events
```

#### update_events

参与；**Quiet Downgrade**；把握高。

update_events为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22438 |
| L1 | 1360 | 1360 | 22722 | 22449 |
| L2 | 1360 | 1360 | 22722 | 22449 |
| L3 | 1360 | 1360 | 22722 | 22449 |

重跑：`records/021_reruns_impl-009_google_play__os_version_report.json` / `update_events`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
cast(NULL as BIGINT) AS update_events
```

#### crashes

参与；**Quiet Downgrade**；把握高。

crashes被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22480 |
| L1 | 1360 | 1360 | 22722 | 22493 |
| L2 | 1360 | 1360 | 22722 | 22493 |
| L3 | 1360 | 1360 | 22722 | 22493 |

重跑：`records/039_checks/supplement_impl-009_google_play__os_version_report.json` / `crashes`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as BIGINT) AS crashes,
cast(0 as BIGINT) AS anrs,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_os_version AS src
WHERE src.date_day IS NOT NULL

```

#### anrs

参与；**Quiet Downgrade**；把握高。

anrs被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22504 |
| L1 | 1360 | 1360 | 22722 | 22517 |
| L2 | 1360 | 1360 | 22722 | 22517 |
| L3 | 1360 | 1360 | 22722 | 22517 |

重跑：`records/039_checks/supplement_impl-009_google_play__os_version_report.json` / `anrs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as BIGINT) AS crashes,
cast(0 as BIGINT) AS anrs,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_os_version AS src
WHERE src.date_day IS NOT NULL

```

#### average_rating

参与；**Quiet Downgrade**；把握高。

average_rating被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22430 |
| L1 | 1360 | 1360 | 22722 | 22441 |
| L2 | 1360 | 1360 | 22722 | 22441 |
| L3 | 1360 | 1360 | 22722 | 22441 |

重跑：`records/039_checks/supplement_impl-009_google_play__os_version_report.json` / `average_rating`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as BIGINT) AS crashes,
cast(0 as BIGINT) AS anrs,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_os_version AS src
WHERE src.date_day IS NOT NULL

```

#### rolling_total_average_rating

参与；**Quiet Downgrade**；把握高。

rolling_total_average_rating被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22438 |
| L1 | 1360 | 1360 | 22722 | 22450 |
| L2 | 1360 | 1360 | 22722 | 22450 |
| L3 | 1360 | 1360 | 22722 | 22450 |

重跑：`records/039_checks/supplement_impl-009_google_play__os_version_report.json` / `rolling_total_average_rating`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as BIGINT) AS crashes,
cast(0 as BIGINT) AS anrs,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_os_version AS src
WHERE src.date_day IS NOT NULL

```

#### total_device_installs

参与；**Quiet Downgrade**；把握高。

total_device_installs被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22444 |
| L1 | 1360 | 1360 | 22722 | 22456 |
| L2 | 1360 | 1360 | 22722 | 22456 |
| L3 | 1360 | 1360 | 22722 | 22456 |

重跑：`records/039_checks/supplement_impl-009_google_play__os_version_report.json` / `total_device_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as BIGINT) AS crashes,
cast(0 as BIGINT) AS anrs,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_os_version AS src
WHERE src.date_day IS NOT NULL

```

#### total_device_uninstalls

参与；**Quiet Downgrade**；把握高。

total_device_uninstalls被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22439 |
| L1 | 1360 | 1360 | 22722 | 22450 |
| L2 | 1360 | 1360 | 22722 | 22450 |
| L3 | 1360 | 1360 | 22722 | 22450 |

重跑：`records/039_checks/supplement_impl-009_google_play__os_version_report.json` / `total_device_uninstalls`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as BIGINT) AS crashes,
cast(0 as BIGINT) AS anrs,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_os_version AS src
WHERE src.date_day IS NOT NULL

```

#### net_device_installs

参与；**Quiet Downgrade**；把握高。

net_device_installs被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 22716 | 22443 |
| L1 | 1360 | 1360 | 22722 | 22455 |
| L2 | 1360 | 1360 | 22722 | 22455 |
| L3 | 1360 | 1360 | 22722 | 22455 |

重跑：`records/039_checks/supplement_impl-009_google_play__os_version_report.json` / `net_device_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as BIGINT) AS crashes,
cast(0 as BIGINT) AS anrs,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_os_version AS src
WHERE src.date_day IS NOT NULL

```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，行[1793, 1888]；材料包 `records/021_packages/021_impl-009_google_play__os_version_report.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__os_version_report.sql`；SHA-256 `384c68ae1d32b4c42c006d9ef9cb208300e0ae49f840fe912e877e79fd026630`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / event 67。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 14，失败=True。
  - `records/021_supplement_queries.json` / index 15，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
