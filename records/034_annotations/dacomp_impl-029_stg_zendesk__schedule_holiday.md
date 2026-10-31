# DAComp / impl-029_stg_zendesk__schedule_holiday（v3）

## 错在哪里
一个start_date为2022-12-291163029，agent整串TRY_CAST为空，gold截前10位得到2022-12-29。

证据复用入口：[018_impl-029_stg_zendesk__schedule_holiday.md](../018_annotations/018_impl-029_stg_zendesk__schedule_holiday.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## date_prefix
- 角色：主要；类别：**Unstated Choice**；把握：中。
- 依据：畸形2022-12-291163029无指定恢复规则，安全转换与截前缀差异；单改1行1格→0。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 55 / args.final_thought：
```text
必填字段空值或转换失败的记录按契约过滤；可选字段转换失败会成为 `NULL`。重复记录、枚举和文本规范化没有超出契约进行更改。
```

## 规模、证据复用与新做
主要原因：Unstated Choice。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-029_stg_zendesk__schedule_holiday.md](../018_annotations/018_impl-029_stg_zendesk__schedule_holiday.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_zendesk__schedule_holiday
      description: "Holiday exceptions per schedule."
      source_table: raw.schedule_holiday_data
      columns:
        - name: schedule_holiday_id
          data_type: BIGINT
          constraints: [not_null]
        - name: schedule_id
          data_type: BIGINT
        - name: name
          data_type: VARCHAR
        - name: start_date
          data_type: DATE
        - name: end_date
          data_type: DATE

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-029_stg_zendesk__schedule_holiday.md:29)
- [SQL定位](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-029_stg_zendesk__schedule_holiday.md:49)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-029_stg_zendesk__schedule_holiday.md:179)
- [重跑 date_prefix](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-029_stg_zendesk__schedule_holiday.md:200)
- [重跑 deleted_filter](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-029_stg_zendesk__schedule_holiday.md:228)
