# impl-010_stg_hubspot__engagement_email（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`C`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 7, "cell_scale": 42}, "L1": {"row_scale": 7, "cell_scale": 42}, "L2": {"row_scale": 7, "cell_scale": 42}, "L3": {"row_scale": 7, "cell_scale": 42}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| unique_engagement | Intent Misreading | 主要 | 7 | 42 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: stg_hubspot__engagement_email
      description: "Email-specific engagement details and metadata"
      source_table: raw.engagement_email_data
      columns:
        - name: engagement_id
          data_type: VARCHAR
          constraints: [unique]
        - name: engagement_type
          data_type: VARCHAR
        - name: email_subject
          data_type: VARCHAR
        - name: email_text
          data_type: VARCHAR
        - name: owner_id
          data_type: VARCHAR
        - name: team_id
          data_type: VARCHAR
        - name: all_owner_ids
          data_type: BIGINT
        - name: all_team_ids
          data_type: BIGINT
        - name: modified_by
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: engagement_timestamp
          data_type: TIMESTAMP
        - name: last_modified_date
          data_type: TIMESTAMP
        - name: _fivetran_synced
          data_type: TIMESTAMP WITH TIME ZONE

```

### 逐点结论

#### unique_engagement

主要；**Intent Misreading**；把握高。

P：engagement_id重复可直接保留。契约明确unique；单改仅落实该约束。用last_modified选择保留项是诊断具体实现，不据此创造契约未写的优先级要求。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 0 | 42 | 0 |
| L1 | 7 | 0 | 42 | 0 |
| L2 | 7 | 0 | 42 | 0 |
| L3 | 7 | 0 | 42 | 0 |

重跑：`records/021_reruns_impl-010_stg_hubspot__engagement_email.json` / `unique_engagement`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__engagement_email.sql` / `SQL.text`（sql）：

```text
where engagement_id is not null
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`，行[430, 461]；材料包 `records/021_packages/021_impl-010_stg_hubspot__engagement_email.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__engagement_email.sql`；SHA-256 `56ffdf87e6c50d16075e01d3560d49604254810c850231f2879896ddeccbaa33`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json` / event 73。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共1条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 18，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
