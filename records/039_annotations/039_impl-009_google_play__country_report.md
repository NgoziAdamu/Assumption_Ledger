# impl-009_google_play__country_report（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Quiet Downgrade**；把握：中；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 7100, "cell_scale": 184600}, "L1": {"row_scale": 7100, "cell_scale": 184600}, "L2": {"row_scale": 7100, "cell_scale": 184600}, "L3": {"row_scale": 7100, "cell_scale": 184600}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| 同类缺口组：机械fallback投影 | Quiet Downgrade | 主要 | 7100 | 184600 | 2 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: google_play__country_report
      description: Country-level performance metrics by package and day, joined across installs, ratings, and store performance and enriched with country metadata
      grain: One row per package_name per country_short per date_day
      source_models:
      - staging.stg_google_play__stats_installs_country
      - staging.stg_google_play__stats_ratings_country
      - staging.stg_google_play__store_performance_country
      - staging.stg_google_play__country_codes
      business_logic: '- Load installs, ratings, store_performance, and country_codes staging tables. - From installs: compute running cumulative device installs and uninstalls per (country, package_name) across ascending dates. - From store_performance: compute running cumulative store listing installers and visitors per (country, package_name) across ascending dates. - Full outer join installs and ratings on matching date_day and package_name; match country null-safe by treating missing country codes as a shared placeholder so missing values match each other. - Full outer join store_performance to the combined result using the available date_day, package_name, and null-safe country from either side. - Build daily fields on the joined rows: - For daily counts (device_installs, device_uninstalls, device_upgrades, user_installs, user_uninstalls, install_events, uninstall_events, update_events, store_listing_acquisitions, store_listing_visitors, active_devices_last_30_days) replace missing values with 0. - Pass through store_listing_conversion_rate as provided (may be missing). - Pass through ratings.daily_average_rating and ratings.total_average_rating (may be missing). - Forward-fill cumulative totals and rolling_total_average_rating: - For each country and package, segment the timeline by each new non-missing occurrence of the cumulative field. - Within each segment, carry the most recently observed non-missing value forward to later days; values remain missing before the first observation. - Enrich with country metadata: - Left join country_codes on ISO alpha-2; set country_long to alternative name when available, otherwise the standard name; include region and sub_region. - Final computations: - Replace any remaining missing cumulative totals (device installs/uninstalls, store acquisitions/visitors) with 0. - rolling_store_conversion_rate = cumulative installers divided by cumulative visitors, rounded to 4 decimals; result is NULL when visitors is zero or missing. - net_device_installs = cumulative device installs minus cumulative device uninstalls.'
      columns:
      - name: date_day
        data_type: DATE
        description: Calendar date resolved from any joined source; used to order window calculations
      - name: package_name
        data_type: VARCHAR
        description: Google Play package identifier; join key across sources; may be NULL if missing in all sources
      - name: country_short
        data_type: VARCHAR
        description: ISO alpha-2 country code from sources; may be NULL if absent; used for partitioning and country enrichment
      - name: country_long
        data_type: VARCHAR
        description: Country display name from codes, preferring the alternative name when available; NULL if no code match
      - name: region
        data_type: VARCHAR
        description: Region from country codes; NULL if no code match
      - name: sub_region
        data_type: VARCHAR
        description: Sub-region from country codes; NULL if no code match
      - name: device_installs
        data_type: BIGINT
        description: Daily device installs from installs; missing values replaced with 0
      - name: device_uninstalls
        data_type: BIGINT
        description: Daily device uninstalls from installs; missing values replaced with 0
      - name: device_upgrades
        data_type: BIGINT
        description: Daily device upgrades from installs; missing values replaced with 0
      - name: user_installs
        data_type: BIGINT
        description: Daily user installs from installs; missing values replaced with 0
      - name: user_uninstalls
        data_type: BIGINT
        description: Daily user uninstalls from installs; missing values replaced with 0
      - name: install_events
        data_type: BIGINT
        description: Daily install events from installs; missing values replaced with 0
      - name: uninstall_events
        data_type: BIGINT
        description: Daily uninstall events from installs; missing values replaced with 0
      - name: update_events
        data_type: BIGINT
        description: Daily update events from installs; missing values replaced with 0
      - name: store_listing_acquisitions
        data_type: INTEGER
        description: Daily installers from store listing; missing values replaced with 0
      - name: store_listing_visitors
        data_type: INTEGER
        description: Daily visitors to the store listing; missing values replaced with 0
      - name: store_listing_conversion_rate
        data_type: DECIMAL(18,3)
        description: Daily store listing conversion rate from store_performance; passed through as is; may be NULL
      - name: active_devices_last_30_days
        data_type: BIGINT
        description: Active devices in the last 30 days from installs; missing values replaced with 0
      - name: average_rating
        data_type: DECIMAL(18,3)
        description: Daily average rating from ratings; may be NULL; typical range 1.000–5.000
      - name: rolling_total_average_rating
        data_type: DECIMAL(18,3)
        description: Forward-filled cumulative average rating; NULL until first observed, then carried forward by date
      - name: total_device_installs
        data_type: HUGEINT
        description: Forward-filled running total of device installs per (country, package); set to 0 in final output when missing
      - name: total_device_uninstalls
        data_type: HUGEINT
        description: Forward-filled running total of device uninstalls per (country, package); set to 0 in final output when missing
      - name: total_store_acquisitions
        data_type: HUGEINT
        description: Forward-filled running total of store listing installers per (country, package); set to 0 in final output when missing
      - name: total_store_visitors
        data_type: HUGEINT
        description: Forward-filled running total of store listing visitors per (country, package); set to 0 in final output when missing
      - name: rolling_store_conversion_rate
        data_type: DOUBLE
        description: Cumulative installers divided by cumulative visitors, rounded to 4 decimals; NULL when visitors is zero or missing
      - name: net_device_installs
        data_type: HUGEINT
        description: Cumulative device installs minus cumulative device uninstalls; uses 0 when missing; may be negative
```

### 逐点结论

#### 同类缺口组：机械fallback投影

主要；**Quiet Downgrade**；把握中。

同类缺口组：安装、ratings与store多源合并；国家统计；累计/滚动指标与地区补充。event39用同一个fallback循环，取source_models[0]、只投影少数维度，其余常量/NULL；整表没有实现要求的关系。该首源在CS可为空，缺少其他分支仍是本表自己的缺口。只能整体诊断的机械生成模型按第7节同类候选处理，不能称每个字段都已单改。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 7100 | 0 | 184600 | 0 |
| L1 | 7100 | 0 | 184600 | 0 |
| L2 | 7100 | 0 | 184600 | 0 |
| L3 | 7100 | 0 | 184600 | 0 |

重跑：`records/021_reruns_impl-009_google_play__country_report.json` / `whole_implementation_diagnostic`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__country_report.sql` / `SQL.text`（sql）：

```text
SELECT
cast(src.date_day as DATE) AS date_day,
cast(src.package_name as VARCHAR) AS package_name,
cast(src.country as VARCHAR) AS country_short,
cast(NULL as VARCHAR) AS country_long,
cast(NULL as VARCHAR) AS region,
cast(NULL as VARCHAR) AS sub_region,
cast(0 as BIGINT) AS device_installs,
cast(0 as BIGINT) AS device_uninstalls,
cast(NULL as BIGINT) AS device_upgrades,
cast(NULL as BIGINT) AS user_installs,
cast(NULL as BIGINT) AS user_uninstalls,
cast(NULL as BIGINT) AS install_events,
cast(NULL as BIGINT) AS uninstall_events,
cast(NULL as BIGINT) AS update_events,
cast(0 as INTEGER) AS store_listing_acquisitions,
cast(0 as INTEGER) AS store_listing_visitors,
cast(NULL as DECIMAL(18,3)) AS store_listing_conversion_rate,
cast(NULL as BIGINT) AS active_devices_last_30_days,
cast(NULL as DECIMAL(18,3)) AS average_rating,
cast(NULL as DECIMAL(18,3)) AS rolling_total_average_rating,
cast(NULL as HUGEINT) AS total_device_installs,
cast(NULL as HUGEINT) AS total_device_uninstalls,
cast(NULL as HUGEINT) AS total_store_acquisitions,
cast(NULL as HUGEINT) AS total_store_visitors,
cast(NULL as DOUBLE) AS rolling_store_conversion_rate,
cast(NULL as HUGEINT) AS net_device_installs
FROM staging.stg_google_play__stats_installs_country AS src
WHERE src.date_day IS NOT NULL
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，行[1552, 1639]；材料包 `records/021_packages/021_impl-009_google_play__country_report.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__country_report.sql`；SHA-256 `190e82a18461170bdf37bf3f55145c62c6b206a18d1be463b4376d8d22bcf825`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / event 67。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 11，失败=True。
  - `records/021_supplement_queries.json` / index 12，失败=False。

## 不确定或没查到的（含规则问题）

- 规则问题：按用户允许的同脚本机械生成例外记一个同类缺口组；只确立类别，不从整表恢复推导各子指标贡献。event39原脚本见轨迹审计。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
