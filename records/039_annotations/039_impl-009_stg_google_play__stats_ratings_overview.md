# impl-009_stg_google_play__stats_ratings_overview（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`C`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 2928, "cell_scale": 11712}, "L1": {"row_scale": 2928, "cell_scale": 11712}, "L2": {"row_scale": 2928, "cell_scale": 11712}, "L3": {"row_scale": 2928, "cell_scale": 11712}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| required_fields | Intent Misreading | 主要 | 2928 | 11712 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: stg_google_play__stats_ratings_overview
      description: "Cleaned daily rating statistics at the app level"
      source_table: "raw.stats_ratings_overview"
      columns:
        - name: date_day
          data_type: DATE
          constraints: [not_null]
        - name: package_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: daily_average_rating
          data_type: NUMERIC
        - name: total_average_rating
          data_type: NUMERIC
        - name: _fivetran_synced
          data_type: VARCHAR

```

### 逐点结论

#### required_fields

主要；**Intent Misreading**；把握高。

P：date_day可以保留NULL。契约date_day/package_name显式not_null，交付SQL无必填过滤。finish点名installs_overview的缺日期不是本张ratings_overview；“基础投影/部分校验”不是对本处缺键政策的说明，故第4档。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2928 | 0 | 11712 | 0 |
| L1 | 2928 | 0 | 11712 | 0 |
| L2 | 2928 | 0 | 11712 | 0 |
| L3 | 2928 | 0 | 11712 | 0 |

重跑：`records/021_reruns_impl-009_stg_google_play__stats_ratings_overview.json` / `required_fields`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__stats_ratings_overview.sql` / `SQL.text`（sql）：

```text
FROM raw.stats_ratings_overview
```

否定披露的审计范围：finish event 67 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，行[185, 201]；材料包 `records/021_packages/021_impl-009_stg_google_play__stats_ratings_overview.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__stats_ratings_overview.sql`；SHA-256 `d267487bcded89f289b35404826b9afe9a48dd17f24282cf5cc31ca62a043504`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / event 67。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共1条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 17，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
