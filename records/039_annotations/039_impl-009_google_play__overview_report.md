# impl-009_google_play__overview_report（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Quiet Downgrade**；把握：中；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 3568, "cell_scale": 67792}, "L1": {"row_scale": 3568, "cell_scale": 67792}, "L2": {"row_scale": 3568, "cell_scale": 67792}, "L3": {"row_scale": 3568, "cell_scale": 67792}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| 同类缺口组：机械fallback投影 | Quiet Downgrade | 主要 | 3568 | 67792 | 2 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: google_play__overview_report
      description: Daily Google Play performance overview per app combining installs, events, store listing, crashes/ANRs, and ratings
      grain: One row per package_name per date_day present in any source
      source_models:
      - staging.stg_google_play__stats_installs_overview
      - staging.stg_google_play__stats_ratings_overview
      - staging.stg_google_play__stats_crashes_overview
      - intermediate.int_google_play__store_performance
      business_logic: '- Aggregate store performance: - Filter intermediate.int_google_play__store_performance to performance_type = ''country''. - For each (date_day, package_name), sum visitors and installers; take the simple (unweighted) average of conversion rate, ignoring missing values. - Compute running totals for installs: - For each package_name ordered by date_day ascending, compute cumulative totals of daily_device_installs and daily_device_uninstalls. - Combine sources: - Full outer join installs (with running totals), ratings, store_performance (aggregated), and crashes on (date_day, package_name). - When date or package is missing in a source, choose the first available from installs, then ratings, then store_performance, then crashes. - Set missing counts to 0 for device/user installs, uninstalls, upgrades; install/uninstall/update events; crashes; ANRs; active devices; store installers and visitors. Leave store listing conversion rate and daily average rating as NULL if absent. - Forward-fill selected metrics by app: - Within each package_name ordered by date_day, carry forward the latest non-null values for total average rating, cumulative device installs, and cumulative device uninstalls; before the first non-null appears, these remain NULL. - Final calculations: - Default total_device_installs and total_device_uninstalls to 0 in the output. - rolling_store_conversion_rate = acquisitions divided by visitors, rounded to 4 decimals; return NULL when visitors is 0. - net_device_installs = total_device_installs minus total_device_uninstalls. - Output one row per (package_name, date_day).'
      columns:
      - name: date_day
        data_type: DATE
        description: Date chosen from the first available among installs, ratings, store performance, and crashes in that order
        tests:
        - not_null
      - name: package_name
        data_type: VARCHAR
        description: App package identifier chosen from the first available among installs, ratings, store performance, and crashes in that order
        tests:
        - not_null
      - name: device_installs
        data_type: BIGINT
        description: Daily device installs; missing values set to 0; no smoothing or rounding
      - name: device_uninstalls
        data_type: BIGINT
        description: Daily device uninstalls; missing values set to 0; no smoothing or rounding
      - name: device_upgrades
        data_type: BIGINT
        description: Daily device upgrades; missing values set to 0; no smoothing or rounding
      - name: user_installs
        data_type: BIGINT
        description: Daily user installs; missing values set to 0; no smoothing or rounding
      - name: user_uninstalls
        data_type: BIGINT
        description: Daily user uninstalls; missing values set to 0; no smoothing or rounding
      - name: crashes
        data_type: BIGINT
        description: Daily crash events; missing values set to 0; per app per day
      - name: anrs
        data_type: BIGINT
        description: Daily ANR events; missing values set to 0; per app per day
      - name: install_events
        data_type: BIGINT
        description: Daily install events; missing values set to 0; event counts unchanged
      - name: uninstall_events
        data_type: BIGINT
        description: Daily uninstall events; missing values set to 0; event counts unchanged
      - name: update_events
        data_type: BIGINT
        description: Daily update events; missing values set to 0; event counts unchanged
      - name: store_listing_acquisitions
        data_type: HUGEINT
        description: Sum of store installers across country rows per day and app; defaults to 0 when store performance is absent
      - name: store_listing_visitors
        data_type: HUGEINT
        description: Sum of store visitors across country rows per day and app; defaults to 0 when store performance is absent
      - name: store_listing_conversion_rate
        data_type: DOUBLE
        description: Unweighted average of store listing conversion rate across country rows per day and app; NULL when no rows; no rounding applied
      - name: active_devices_last_30_days
        data_type: BIGINT
        description: Active devices in the last 30 days from installs; missing values set to 0
      - name: average_rating
        data_type: DECIMAL(18,3)
        description: Daily average rating; may be NULL; three-decimal precision
      - name: rolling_total_average_rating
        data_type: DECIMAL(18,3)
        description: Forward-filled total average rating per app ordered by date; remains NULL until the first non-null appears
      - name: total_device_installs
        data_type: HUGEINT
        description: Cumulative device installs per app ordered by date; forward-filled across days without install data; defaults to 0 in output
      - name: total_device_uninstalls
        data_type: HUGEINT
        description: Cumulative device uninstalls per app ordered by date; forward-filled across days without install data; defaults to 0 in output
      - name: rolling_store_conversion_rate
        data_type: DOUBLE
        description: Acquisitions divided by visitors, rounded to 4 decimals; returns NULL when visitors equals 0
      - name: net_device_installs
        data_type: HUGEINT
        description: Total device installs minus total device uninstalls after defaulting NULLs to 0
```

### 逐点结论

#### 同类缺口组：机械fallback投影

主要；**Quiet Downgrade**；把握中。

同类缺口组：安装、ratings、崩溃及store来源合并；应用日汇总、累计/滚动指标。event39用同一个fallback循环，取source_models[0]、只投影少数维度，其余常量/NULL；整表没有实现要求的关系。该首源在CS可为空，缺少其他分支仍是本表自己的缺口。只能整体诊断的机械生成模型按第7节同类候选处理，不能称每个字段都已单改。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 3568 | 0 | 67792 | 0 |
| L1 | 3568 | 0 | 67792 | 0 |
| L2 | 3568 | 0 | 67792 | 0 |
| L3 | 3568 | 0 | 67792 | 0 |

重跑：`records/021_reruns_impl-009_google_play__overview_report.json` / `whole_implementation_diagnostic`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__overview_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.package_name as VARCHAR) AS package_name,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(0 as BIGINT) AS crashes,
cast(0 as BIGINT) AS anrs,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as HUGEINT) AS store_listing_acquisitions,
cast(0 as HUGEINT) AS store_listing_visitors,
cast(NULL as DOUBLE) AS store_listing_conversion_rate,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as DOUBLE) AS rolling_store_conversion_rate,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_overview AS src
WHERE src.date_day IS NOT NULL
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，行[1889, 1968]；材料包 `records/021_packages/021_impl-009_google_play__overview_report.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__overview_report.sql`；SHA-256 `d3a3e2e6354111470f0f19d061e1636b8a71cc8a32c18a1dcc20b1ccf26d9c41`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / event 67。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 15，失败=True。
  - `records/021_supplement_queries.json` / index 16，失败=False。

## 不确定或没查到的（含规则问题）

- 规则问题：按用户允许的同脚本机械生成例外记一个同类缺口组；只确立类别，不从整表恢复推导各子指标贡献。event39原脚本见轨迹审计。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
