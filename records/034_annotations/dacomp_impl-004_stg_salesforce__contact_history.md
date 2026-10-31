# DAComp / impl-004_stg_salesforce__contact_history（v3）

## 错在哪里
history_unique_key生成约定未写明，hash与id加时间导致全部键不相交；另有1行日期边界差异。

证据复用入口：[018_impl-004_stg_salesforce__contact_history.md](../018_annotations/018_impl-004_stg_salesforce__contact_history.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## history_key_frozen
- 角色：主要；类别：**已说出的选择**；把握：中。
- 依据：键公式未规定，hash和id+时间两种约定；共同固定时刻下6000行→1。
- 是否说出：针对本处的具体说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 51 / args.final_thought：
```text
History 原始表没有契约字段 `created_date` / `history_unique_key`，使用源 `_fivetran_start` 作为变更时间，并以 `_fivetran_start` 与 `_fivetran_end` 计算字符串唯一标识；该映射使快照能够按源可用的版本时间运行。
```
## activity_rule_gold_day
- 角色：非原因；类别：**Intent Misreading**；把握：中。
- 依据：日期校验单改6000行/126000格不变；存在未确立的前提，但不是判错原因。
- 是否说出：没有迹象。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/014_trace_impl-004.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。

## 规模、证据复用与新做
主要原因：已说出的选择。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-004_stg_salesforce__contact_history.md](../018_annotations/018_impl-004_stg_salesforce__contact_history.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_salesforce__contact_history
      description: "Historical tracking of contact changes"
      source_table: "raw.contact_history"
      columns:
        - name: contact_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: account_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: contact_description
          data_type: VARCHAR
        - name: email
          data_type: VARCHAR
        - name: first_name
          data_type: VARCHAR
        - name: is_deleted
          data_type: BOOLEAN
        - name: last_activity_date
          data_type: DATE
          validation_rules:
            - rule: "last_activity_date = CASE WHEN last_activity_date IS NOT NULL AND last_activity_date > CURRENT_DATE THEN NULL WHEN last_activity_date IS NOT NULL AND last_activity_date < '2020-01-01' THEN NULL ELSE last_activity_date END"
              on_failure: nullify_field
        - name: last_modified_date
          data_type: TIMESTAMP
        - name: last_name
          data_type: VARCHAR
        - name: lead_source
          data_type: VARCHAR
        - name: mailing_city
          data_type: VARCHAR
        - name: mailing_country
          data_type: VARCHAR
        - name: mailing_postal_code
          data_type: VARCHAR
          validation_rules:
            - rule: "mailing_postal_code = CASE WHEN mailing_postal_code = '' THEN NULL WHEN mailing_postal_code IS NOT NULL AND LENGTH(TRIM(mailing_postal_code)) < 3 THEN DELETE_ROW WHEN mailing_postal_code IS NOT NULL AND LENGTH(TRIM(mailing_postal_code)) > 12 THEN NULL ELSE UPPER(TRIM(mailing_postal_code)) END"
              on_failure: correct
        - name: mailing_state
          data_type: VARCHAR
        - name: mailing_street
          data_type: VARCHAR
        - name: mobile_phone
          data_type: VARCHAR
          validation_rules:
            - rule: "mobile_phone = CASE WHEN mobile_phone = '' THEN NULL WHEN mobile_phone IS NOT NULL AND LENGTH(REGEXP_REPLACE(mobile_phone, '[^0-9]', '')) < 10 THEN NULL ELSE REGEXP_REPLACE(mobile_phone, '[^0-9+()-]', '') END"
              on_failure: nullify_field
        - name: contact_name
          data_type: VARCHAR
        - name: owner_id
          data_type: VARCHAR
        - name: phone
          data_type: VARCHAR
        - name: title
          data_type: VARCHAR
        - name: history_unique_key
          data_type: VARCHAR

```

## 规则问题

hash是计算出的键，不能当纯呈现；具体披露的来源/公式足以按v3改记已说出的选择。

## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-004_stg_salesforce__contact_history.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-004_stg_salesforce__contact_history.md:91)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-004_stg_salesforce__contact_history.md:474)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-004_stg_salesforce__contact_history.md:516)
- [重跑 history_key](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-004_stg_salesforce__contact_history.md:553)
- [重跑 activity_rule](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-004_stg_salesforce__contact_history.md:597)
- [重跑 history_key_frozen](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-004_stg_salesforce__contact_history.md:641)
- [重跑 activity_rule_gold_day](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-004_stg_salesforce__contact_history.md:685)
