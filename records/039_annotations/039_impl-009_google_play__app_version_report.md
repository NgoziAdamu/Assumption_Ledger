# impl-009_google_play__app_version_report（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Quiet Downgrade**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 1360, "cell_scale": 21635}, "L1": {"row_scale": 1360, "cell_scale": 21635}, "L2": {"row_scale": 1360, "cell_scale": 21635}, "L3": {"row_scale": 1360, "cell_scale": 21635}}`。

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
| crashes | Quiet Downgrade | 参与 | 0 | 1318 | 2 |
| anrs | Quiet Downgrade | 参与 | 0 | 1277 | 2 |
| average_rating | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| rolling_total_average_rating | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| total_device_installs | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| total_device_uninstalls | Quiet Downgrade | 并列 | 0 | 1360 | 2 |
| net_device_installs | Quiet Downgrade | 并列 | 0 | 1360 | 2 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: google_play__app_version_report
      description: App version performance by date with installs, uninstalls, crashes/ANRs, ratings, and cumulative metrics per OS version and device
      grain: One row per date_day, package_name, app_version_code, android_os_version, device
      source_models:
      - staging.stg_google_play__stats_installs_app_version
      - staging.stg_google_play__stats_crashes_app_version
      - staging.stg_google_play__stats_ratings_app_version
      business_logic: '- Inputs: - Installs: per date, package, app_version_code, android_os_version, device - Ratings: per date, package, app_version_code - Crashes: per date, package, app_version_code, android_os_version - Compute cumulative install totals on the installs input: - total_device_installs: cumulative sum of daily_device_installs by date_day ascending within (package_name, app_version_code) - total_device_uninstalls: cumulative sum of daily_device_uninstalls by date_day ascending within (package_name, app_version_code) - Note: ordering is by date_day only; if multiple rows share the same date_day, the physical/source row order determines evaluation within that day; device and android_os_version are not included in the partition. - Full outer join to unify datasets: - First join installs with ratings on (date_day, package_name, app_version_code) using null-safe comparison by substituting NULL app_version_code with ''null_version'' - Then join crashes on the available date from installs or ratings, plus (package_name, app_version_code, android_os_version), using null-safe comparison by substituting NULL app_version_code with ''null_version'' and NULL android_os_version with ''null_os''; android_os_version is compared as a string; device is not part of any join key. - Output dimensions: - date_day, app_version_code, package_name selected from installs if present, else ratings, else crashes - android_os_version from installs if present else crashes (as string) - device from installs only (NULL if the row originates only from ratings/crashes) - Populate metrics with deterministic null handling: - From installs: active_device_installs → active_devices_last_30_days; all daily device/user/event metrics treat missing values as 0 - From crashes: crashes and anrs treat missing values as 0; values repeat across devices because device is not joined - From ratings: average_rating is the daily average rating (NULL if missing); rolling_total_average_rating is the total-average rating (may be NULL) - Forward-fill selected metrics across dates within (package_name, app_version_code): - For rolling_total_average_rating and each cumulative total, create a segment identifier as the running count of non-NULL values by date_day ascending - Within each segment, carry forward the first observed non-NULL value to subsequent rows; values remain NULL until the first non-NULL appears - Finalize outputs: - total_device_installs and total_device_uninstalls are treated as 0 when still missing after forward-fill - net_device_installs = total_device_installs − total_device_uninstalls - No aggregation or de-duplication beyond the joins; duplicates from sources are preserved; original string casing and spacing are preserved'
      columns:
      - name: date_day
        data_type: DATE
        description: Selected from installs if present, else ratings, else crashes
        tests:
        - not_null
      - name: app_version_code
        data_type: VARCHAR
        description: Taken from whichever source is present; may be NULL; joins substitute NULL with 'null_version'
      - name: package_name
        data_type: VARCHAR
        description: Google Play package identifier selected from the available source
        tests:
        - not_null
      - name: android_os_version
        data_type: VARCHAR
        description: Android OS version from installs else crashes, compared as strings with 'null_os' used when missing
      - name: device
        data_type: VARCHAR
        description: Device identifier from installs; NULL when only ratings/crashes data exists
      - name: device_installs
        data_type: BIGINT
        description: Daily device installs from installs; missing values become 0
      - name: device_uninstalls
        data_type: BIGINT
        description: Daily device uninstalls from installs; missing values become 0
      - name: device_upgrades
        data_type: BIGINT
        description: Daily device upgrades from installs; missing values become 0
      - name: user_installs
        data_type: BIGINT
        description: Daily user installs from installs; missing values become 0
      - name: user_uninstalls
        data_type: BIGINT
        description: Daily user uninstalls from installs; missing values become 0
      - name: install_events
        data_type: BIGINT
        description: Daily install event count from installs; missing values become 0
      - name: uninstall_events
        data_type: BIGINT
        description: Daily uninstall event count from installs; missing values become 0
      - name: update_events
        data_type: BIGINT
        description: Daily update event count from installs; missing values become 0
      - name: crashes
        data_type: BIGINT
        description: Daily crash count joined by date/package/version/OS; missing values become 0 and values repeat across devices
      - name: anrs
        data_type: BIGINT
        description: Daily ANR count joined by date/package/version/OS; missing values become 0 and values repeat across devices
      - name: active_devices_last_30_days
        data_type: BIGINT
        description: Active devices in the last 30 days from installs; missing values become 0
      - name: average_rating
        data_type: DECIMAL(18,3)
        description: Daily average rating from ratings; NULL if unavailable; range 1–5 when present
      - name: rolling_total_average_rating
        data_type: DECIMAL(18,3)
        description: Total-average rating forward-filled by date within (package_name, app_version_code); NULL until the first non-NULL appears
      - name: total_device_installs
        data_type: HUGEINT
        description: Cumulative device installs by date within (package_name, app_version_code), forward-filled across gaps; missing values become 0; same-day tie order follows source row order
      - name: total_device_uninstalls
        data_type: HUGEINT
        description: Cumulative device uninstalls by date within (package_name, app_version_code), forward-filled across gaps; missing values become 0; same-day tie order follows source row order
      - name: net_device_installs
        data_type: HUGEINT
        description: Total device installs minus total device uninstalls; may be negative; never NULL
```

### 逐点结论

#### device_installs

并列；**Quiet Downgrade**；把握高。

device_installs为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/021_supplement_reruns_impl-009_google_play__app_version_report.json` / `device_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

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
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/021_supplement_reruns_impl-009_google_play__app_version_report.json` / `device_uninstalls`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

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
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/021_supplement_reruns_impl-009_google_play__app_version_report.json` / `device_upgrades`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

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
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/021_supplement_reruns_impl-009_google_play__app_version_report.json` / `user_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

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
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/021_supplement_reruns_impl-009_google_play__app_version_report.json` / `user_uninstalls`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

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
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/021_supplement_reruns_impl-009_google_play__app_version_report.json` / `active_devices_last_30_days`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

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
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/021_reruns_impl-009_google_play__app_version_report.json` / `install_events`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

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
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/021_reruns_impl-009_google_play__app_version_report.json` / `uninstall_events`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

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
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/021_reruns_impl-009_google_play__app_version_report.json` / `update_events`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

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
| L0 | 1360 | 1360 | 21635 | 20317 |
| L1 | 1360 | 1360 | 21635 | 20317 |
| L2 | 1360 | 1360 | 21635 | 20317 |
| L3 | 1360 | 1360 | 21635 | 20317 |

重跑：`records/039_checks/supplement_impl-009_google_play__app_version_report.json` / `crashes`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.app_version_code as VARCHAR) AS app_version_code,
cast(src.package_name as VARCHAR) AS package_name,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.device as VARCHAR) AS device,
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
FROM staging.stg_google_play__stats_installs_app_version AS src
WHERE src.date_day IS NOT NULL

```

#### anrs

参与；**Quiet Downgrade**；把握高。

anrs被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 21635 | 20358 |
| L1 | 1360 | 1360 | 21635 | 20358 |
| L2 | 1360 | 1360 | 21635 | 20358 |
| L3 | 1360 | 1360 | 21635 | 20358 |

重跑：`records/039_checks/supplement_impl-009_google_play__app_version_report.json` / `anrs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.app_version_code as VARCHAR) AS app_version_code,
cast(src.package_name as VARCHAR) AS package_name,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.device as VARCHAR) AS device,
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
FROM staging.stg_google_play__stats_installs_app_version AS src
WHERE src.date_day IS NOT NULL

```

#### average_rating

并列；**Quiet Downgrade**；把握高。

average_rating被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/039_checks/supplement_impl-009_google_play__app_version_report.json` / `average_rating`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.app_version_code as VARCHAR) AS app_version_code,
cast(src.package_name as VARCHAR) AS package_name,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.device as VARCHAR) AS device,
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
FROM staging.stg_google_play__stats_installs_app_version AS src
WHERE src.date_day IS NOT NULL

```

#### rolling_total_average_rating

并列；**Quiet Downgrade**；把握高。

rolling_total_average_rating被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/039_checks/supplement_impl-009_google_play__app_version_report.json` / `rolling_total_average_rating`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.app_version_code as VARCHAR) AS app_version_code,
cast(src.package_name as VARCHAR) AS package_name,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.device as VARCHAR) AS device,
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
FROM staging.stg_google_play__stats_installs_app_version AS src
WHERE src.date_day IS NOT NULL

```

#### total_device_installs

并列；**Quiet Downgrade**；把握高。

total_device_installs被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/039_checks/supplement_impl-009_google_play__app_version_report.json` / `total_device_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.app_version_code as VARCHAR) AS app_version_code,
cast(src.package_name as VARCHAR) AS package_name,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.device as VARCHAR) AS device,
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
FROM staging.stg_google_play__stats_installs_app_version AS src
WHERE src.date_day IS NOT NULL

```

#### total_device_uninstalls

并列；**Quiet Downgrade**；把握高。

total_device_uninstalls被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/039_checks/supplement_impl-009_google_play__app_version_report.json` / `total_device_uninstalls`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.app_version_code as VARCHAR) AS app_version_code,
cast(src.package_name as VARCHAR) AS package_name,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.device as VARCHAR) AS device,
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
FROM staging.stg_google_play__stats_installs_app_version AS src
WHERE src.date_day IS NOT NULL

```

#### net_device_installs

并列；**Quiet Downgrade**；把握高。

net_device_installs被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 1360 | 1360 | 21635 | 20275 |
| L1 | 1360 | 1360 | 21635 | 20275 |
| L2 | 1360 | 1360 | 21635 | 20275 |
| L3 | 1360 | 1360 | 21635 | 20275 |

重跑：`records/039_checks/supplement_impl-009_google_play__app_version_report.json` / `net_device_installs`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.app_version_code as VARCHAR) AS app_version_code,
cast(src.package_name as VARCHAR) AS package_name,
cast(src.android_os_version as VARCHAR) AS android_os_version,
cast(src.device as VARCHAR) AS device,
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
FROM staging.stg_google_play__stats_installs_app_version AS src
WHERE src.date_day IS NOT NULL

```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，行[1476, 1551]；材料包 `records/021_packages/021_impl-009_google_play__app_version_report.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__app_version_report.sql`；SHA-256 `7ee1e948cb0ee1bbee422fe6480e8638de1829d3997487f6ce23a486b237ca74`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / event 67。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 9，失败=True。
  - `records/021_supplement_queries.json` / index 10，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
