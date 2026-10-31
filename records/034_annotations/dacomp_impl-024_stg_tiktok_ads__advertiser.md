# DAComp / impl-024_stg_tiktok_ads__advertiser（v3）

## 错在哪里
email正则的域名接受范围不同：agent把adv12@sub..example.com置NULL，gold保留。

证据复用入口：[018_impl-024_stg_tiktok_ads__advertiser.md](../018_annotations/018_impl-024_stg_tiktok_ads__advertiser.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## email_pattern
- 角色：主要；类别：**Unstated Choice**；把握：中。
- 依据：standard pattern (local@domain.tld)没有边界模式；连续点的接受与拒绝不同，单改1行1格→0。不援引未经核实的领域约定。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 63 / args.final_thought：
```text
可选邮箱/名称/手机号字段验证失败时置 NULL，记录仍保留。
```

## 规模、证据复用与新做
主要原因：Unstated Choice。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-024_stg_tiktok_ads__advertiser.md](../018_annotations/018_impl-024_stg_tiktok_ads__advertiser.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_tiktok_ads__advertiser
      description: "Cleaned advertiser master data with normalized contact fields and type-safe numeric conversions."
      source_table: raw.tiktok_advertiser_data
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: advertiser_id
          data_type: VARCHAR
        - name: address
          data_type: VARCHAR
        - name: balance
          data_type: DOUBLE
          validation_rules:
            - rule: "balance is numeric"
              on_failure: nullify_field
        - name: company
          data_type: VARCHAR
        - name: contacter
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: currency
          data_type: VARCHAR
        - name: description
          data_type: VARCHAR
        - name: email
          data_type: VARCHAR
          validation_rules:
            - rule: "email normalized to lowercase and trimmed"
              on_failure: correct
            - rule: "email matches standard pattern (local@domain.tld)"
              on_failure: nullify_field
        - name: industry
          data_type: VARCHAR
        - name: language
          data_type: VARCHAR
        - name: advertiser_name
          data_type: VARCHAR
          validation_rules:
            - rule: "name trimmed"
              on_failure: correct
            - rule: "name length between 3 and 100 and only alphanumeric plus spaces"
              on_failure: nullify_field
        - name: cellphone_number
          data_type: VARCHAR
          validation_rules:
            - rule: "strip non-digit characters except leading '+'"
              on_failure: correct
            - rule: "must conform to E.164 format"
              on_failure: nullify_field
        - name: telephone_number
          data_type: VARCHAR
        - name: timezone
          data_type: VARCHAR

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-024_stg_tiktok_ads__advertiser.md:29)
- [SQL定位](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-024_stg_tiktok_ads__advertiser.md:88)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-024_stg_tiktok_ads__advertiser.md:299)
- [重跑 email_pattern](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-024_stg_tiktok_ads__advertiser.md:331)
