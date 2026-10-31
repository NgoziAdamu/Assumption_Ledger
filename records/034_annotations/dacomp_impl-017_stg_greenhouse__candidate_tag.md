# DAComp / impl-017_stg_greenhouse__candidate_tag（v3）

## 错在哪里
agent按复合主键去掉一个重复candidate-tag行，gold保留重复，造成1行2格差异。

证据复用入口：[018_impl-017_stg_greenhouse__candidate_tag.md](../018_annotations/018_impl-017_stg_greenhouse__candidate_tag.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## preserve_duplicate
- 角色：主要；类别：**其他**；把握：中。
- 依据：复合主键candidate_id/tag_id要求唯一，gold保留一条重复；取消去重1行2格→0。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 53 / args.final_thought：
```text
staging 对声明为主键的空值行进行过滤，并按主键分组只保留一条记录以满足唯一性；若重复键的内容不一致，合同没有规定优先版本，因而保留记录选择未定义，重复记录中的非键值可能丢失。
```

## 规模、证据复用与新做
主要原因：其他。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-017_stg_greenhouse__candidate_tag.md](../018_annotations/018_impl-017_stg_greenhouse__candidate_tag.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_greenhouse__candidate_tag
      description: "Cleaned candidate tag associations"
      source_table: "raw.candidate_tag"
      primary_key: ["candidate_id", "tag_id"]
      columns:
        - name: candidate_id
          data_type: BIGINT
          constraints: [not_null]
        - name: tag_id
          data_type: BIGINT
          constraints: [not_null]

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-017_stg_greenhouse__candidate_tag.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-017_stg_greenhouse__candidate_tag.md:44)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-017_stg_greenhouse__candidate_tag.md:174)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-017_stg_greenhouse__candidate_tag.md:196)
- [重跑 preserve_duplicate](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-017_stg_greenhouse__candidate_tag.md:216)
