# impl-008_stg_asana__section（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`C`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 7, "cell_scale": 14}, "L1": {"row_scale": 7, "cell_scale": 14}, "L2": {"row_scale": 7, "cell_scale": 14}, "L3": {"row_scale": 7, "cell_scale": 14}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| required_project_id | Intent Misreading | 主要 | 7 | 14 | 2 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: stg_asana__section
      description: "Standardized project sections for organizing tasks with validated project relationships"
      source_table: "raw.section_data"
      columns:
        - name: section_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: section_name
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "section_name = TRIM(section_name)"
              on_failure: correct
              description: "Remove whitespace from section names"
            - rule: "LENGTH(section_name) >= 1"
              on_failure: delete_row
              description: "Section name cannot be empty"
        - name: project_id
          data_type: BIGINT
          constraints: [not_null]

```

### 逐点结论

#### required_project_id

主要；**Intent Misreading**；把握高。

P：只检查原始project_id非空就满足BIGINT not_null。契约约束的是转换后的字段；解析后NULL仍被交出。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 0 | 14 | 0 |
| L1 | 7 | 0 | 14 | 0 |
| L2 | 7 | 0 | 14 | 0 |
| L3 | 7 | 0 | 14 | 0 |

重跑：`records/021_reruns_impl-008_stg_asana__section.json` / `required_project_id`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / `53.args.final_thought`（delivery）：

```text
staging 中对必需键为空或严重无效的记录进行过滤
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/staging/stg_asana__section.sql` / `SQL.text`（sql）：

```text
WHERE _rn = 1
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`，行[215, 238]；材料包 `records/021_packages/021_impl-008_stg_asana__section.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/staging/stg_asana__section.sql`；SHA-256 `556bdc2761a6469a5bf32724442f8eb5630d49f79182b47a9938a3dfaeb71c6c`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / event 53。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共1条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 6，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
