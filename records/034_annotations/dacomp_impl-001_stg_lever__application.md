# DAComp / impl-001_stg_lever__application（v3）

## 错在哪里
agent 按契约删除解析后创建时间为空的全部5000行；gold保留这些行，去掉该筛选即完全匹配。

证据复用入口：[018_impl-001_stg_lever__application.md](../018_annotations/018_impl-001_stg_lever__application.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## allow_null_created
- 角色：主要；类别：**其他**；把握：中。
- 依据：契约 created_at not_null；gold保留5000个解析后NULL。按契约筛选与gold冲突，5000行→0。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 67 / args.final_thought：
```text
转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。
```

## 规模、证据复用与新做
主要原因：其他。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-001_stg_lever__application.md](../018_annotations/018_impl-001_stg_lever__application.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_lever__application
      description: "Cleaned job applications linking candidates to postings with application status and metadata"
      source_table: "raw.application"
      columns:
        - name: application_id
          data_type: VARCHAR(50)
          constraints: [not_null, unique]
        - name: opportunity_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: posting_id
          data_type: VARCHAR(50)
        - name: type
          data_type: VARCHAR(50)
        - name: candidate_id
          data_type: BIGINT
        - name: posting_hiring_manager_user_id
          data_type: VARCHAR(50)
        - name: posting_owner_user_id
          data_type: VARCHAR(50)
        - name: company
          data_type: VARCHAR(255)
        - name: referrer_user_id
          data_type: VARCHAR(50)
        - name: requisition_id
          data_type: VARCHAR(50)
        - name: archived_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "archived_at IS NULL OR created_at IS NULL OR try_cast(archived_at as timestamp) >= try_cast(created_at as timestamp)"
              on_failure: delete_row
        - name: archived_reason_id
          data_type: VARCHAR(50)
        - name: comments
          data_type: VARCHAR(1000)
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-001_stg_lever__application.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-001_stg_lever__application.md:71)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-001_stg_lever__application.md:271)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-001_stg_lever__application.md:306)
- [重跑 allow_null_created](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-001_stg_lever__application.md:338)
- [重跑 archive_check](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-001_stg_lever__application.md:378)
