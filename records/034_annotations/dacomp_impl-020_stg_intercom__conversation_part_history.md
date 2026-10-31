# DAComp / impl-020_stg_intercom__conversation_part_history（v3）

## 错在哪里
agent从复合id提取BIGINT会话号而gold保留原列时间文本，另补subject到part_type；gold类型与契约冲突。

证据复用入口：[018_impl-020_stg_intercom__conversation_part_history.md](../018_annotations/018_impl-020_stg_intercom__conversation_part_history.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## conversation_direct
- 角色：主要；类别：**其他**；把握：中。
- 依据：契约BIGINT，gold保留时间VARCHAR；agent遵守类型；7524→7476行。
- 是否说出：针对本处的具体说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 61 / args.final_thought：
```text
原始 conversation part 文件中的实际列数据与源 schema 声明不一致：对话 ID 实际可从 part `id` 的前缀提取，事件时间可从错位的原始 `conversation_id` 字段解析，事件类型可从 `subject` 字段回退获取。
```
## part_type_direct
- 角色：非原因；类别：**Unstated Choice**；把握：中。
- 依据：以subject恢复缺失part_type未规定；单改行不降，存在未确立的前提，但不是判错原因。
- 是否说出：没有迹象。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。
## created_at_source
- 角色：非原因；类别：**Intent Misreading**；把握：中。
- 依据：source_expression未遵守，但非评分列且单改无影响。
- 是否说出：没有迹象。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-020.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。

## 规模、证据复用与新做
主要原因：其他。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-020_stg_intercom__conversation_part_history.md](../018_annotations/018_impl-020_stg_intercom__conversation_part_history.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_intercom__conversation_part_history
      description: "Conversation part events with typing and activity filtering."
      source_table: raw.conversation_part_history_data
      columns:
        - name: conversation_part_id
          data_type: VARCHAR
          source_expression: "id"
        - name: part_type
          data_type: VARCHAR
        - name: body
          data_type: VARCHAR
        - name: conversation_id
          data_type: BIGINT
        - name: author_id
          data_type: VARCHAR
        - name: author_type
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
          source_expression: "try_cast(created_at as timestamp)"
        - name: updated_at
          data_type: TIMESTAMP
      row_filters:
        - rule: "coalesce(try_cast(_fivetran_active as BOOLEAN), true)"
          on_failure: delete_row

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-020_stg_intercom__conversation_part_history.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-020_stg_intercom__conversation_part_history.md:58)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-020_stg_intercom__conversation_part_history.md:179)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-020_stg_intercom__conversation_part_history.md:207)
- [重跑 part_type_direct](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-020_stg_intercom__conversation_part_history.md:231)
- [重跑 conversation_direct](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-020_stg_intercom__conversation_part_history.md:262)
- [重跑 created_contract](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-020_stg_intercom__conversation_part_history.md:293)
