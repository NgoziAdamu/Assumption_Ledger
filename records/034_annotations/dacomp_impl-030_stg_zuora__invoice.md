# DAComp / impl-030_stg_zuora__invoice（v3）

## 错在哪里
account_id误取invoice id与四项数值表示差异各1040格并列；另有日期/金额类型差异及错误丢弃5条空日期记录。

证据复用入口：[018_impl-030_stg_zuora__invoice.md](../018_annotations/018_impl-030_stg_zuora__invoice.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## account_source
- 角色：并列；类别：**Data Misconception**；把握：中。
- 依据：P：invoice.id能充当account_id；可见raw核实account_id关联1999行，id关联0行。单改减少1040格。
- 是否说出：只有通用策略说明。
- 证据在场：否；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/017_trace_impl-030.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
实际可见列名/通用输出不能单凭它确定匹配或唯一性；核实查询为标注者事后执行。
event 71 / args.final_thought：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。
```
## adjustment_amount_representation
- 角色：并列；类别：**其他**；把握：中。
- 依据：契约DOUBLE，agent遵守而gold VARCHAR；单改减少1040格。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 71 / args.final_thought：
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```
## credit_balance_adjustment_amount_representation
- 角色：并列；类别：**其他**；把握：中。
- 依据：契约DOUBLE，agent遵守而gold VARCHAR；单改减少1040格。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 71 / args.final_thought：
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```
## credit_memo_amount_representation
- 角色：并列；类别：**其他**；把握：中。
- 依据：契约DOUBLE，agent遵守而gold VARCHAR；单改减少1040格。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 71 / args.final_thought：
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```
## exchange_rate_representation
- 角色：并列；类别：**其他**；把握：中。
- 依据：契约DOUBLE，agent遵守而gold VARCHAR；单改减少1040格。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 71 / args.final_thought：
```text
合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
```
## created_date_nullable
- 角色：参与；类别：**Intent Misreading**；把握：中。
- 依据：规格显式OR NULL，agent误删5行；单改减少175格。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/017_trace_impl-030.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 71 / args.final_thought：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。
```
四档引句为关联证据；本处可见性另按在场栏判断，未将通用策略算成具体披露。
## amount_without_tax_representation
- 角色：参与；类别：**其他**；把握：中。
- 依据：类型/表示与契约冲突，单改减少1035格。
- 是否说出：没有迹象。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。
## amount_without_tax_home_currency_representation
- 角色：参与；类别：**其他**；把握：中。
- 依据：类型/表示与契约冲突，单改减少1035格。
- 是否说出：没有迹象。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。
## exchange_rate_date_representation
- 角色：参与；类别：**其他**；把握：中。
- 依据：类型/表示与契约冲突，单改减少1035格。
- 是否说出：没有迹象。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。
## target_date_representation
- 角色：参与；类别：**其他**；把握：中。
- 依据：类型/表示与契约冲突，单改减少1035格。
- 是否说出：没有迹象。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。
## balance_representation
- 角色：参与；类别：**其他**；把握：中。
- 依据：类型/表示与契约冲突，单改减少5格。
- 是否说出：没有迹象。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。

## 规模、证据复用与新做
主要原因：多因并列。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-030_stg_zuora__invoice.md](../018_annotations/018_impl-030_stg_zuora__invoice.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_zuora__invoice
      description: "Cleaned invoices with safe casting and temporal validity checks; latest snapshot indicator provided."
      source_table: raw.zuora_invoice_data
      columns:
        - name: invoice_id
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: adjustment_amount
          data_type: DOUBLE
        - name: amount
          data_type: DOUBLE
          source_expression: "case when nullif(amount,'') is null then null else cast(amount as DOUBLE) end"
        - name: amount_home_currency
          data_type: DOUBLE
          source_expression: "case when nullif(amount_home_currency,'') is null then null else cast(amount_home_currency as DOUBLE) end"
        - name: amount_without_tax
          data_type: BIGINT
        - name: amount_without_tax_home_currency
          data_type: BIGINT
        - name: auto_pay
          data_type: BOOLEAN
        - name: balance
          data_type: DOUBLE
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: comments
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
          source_expression: "case when try_cast(created_date as TIMESTAMP) is null then null when try_cast(created_date as TIMESTAMP) > current_timestamp then null when try_cast(created_date as TIMESTAMP) < timestamp '2000-01-01 00:00:00' then null else cast(created_date as TIMESTAMP) end"
        - name: credit_balance_adjustment_amount
          data_type: DOUBLE
        - name: credit_memo_amount
          data_type: DOUBLE
        - name: default_payment_method_id
          data_type: VARCHAR
        - name: due_date
          data_type: DATE
          source_expression: "try_cast(due_date as DATE)"
        - name: exchange_rate
          data_type: DOUBLE
        - name: exchange_rate_date
          data_type: DATE
        - name: home_currency
          data_type: VARCHAR
        - name: includes_one_time
          data_type: BOOLEAN
        - name: includes_recurring
          data_type: BOOLEAN
        - name: includes_usage
          data_type: BOOLEAN
        - name: invoice_date
          data_type: DATE
          source_expression: "try_cast(invoice_date as DATE)"
        - name: invoice_number
          data_type: VARCHAR
        - name: last_email_sent_date
          data_type: TIMESTAMP
          source_expression: "case when nullif(last_email_sent_date,'') is null then null else cast(last_email_sent_date as TIMESTAMP) end"
        - name: parent_account_id
          data_type: VARCHAR
        - name: payment_amount
          data_type: DOUBLE
          source_expression: "case when nullif(payment_amount,'') is null then null else cast(payment_amount as DOUBLE) end"
        - name: payment_term
          data_type: VARCHAR
        - name: posted_by
          data_type: VARCHAR
        - name: posted_date
          data_type: TIMESTAMP
          source_expression: "cast(posted_date as TIMESTAMP)"
        - name: refund_amount
          data_type: DOUBLE
          source_expression: "case when nullif(refund_amount,'') is null then null else cast(refund_amount as DOUBLE) end"
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: source
          data_type: VARCHAR
        - name: source_id
          data_type: VARCHAR
        - name: source_type
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
        - name: target_date
          data_type: DATE
        - name: tax_amount
          data_type: DOUBLE
          source_expression: "case when nullif(tax_amount,'') is null then null else cast(tax_amount as DOUBLE) end"
        - name: tax_status
          data_type: VARCHAR
        - name: transaction_currency
          data_type: VARCHAR
        - name: transferred_to_accounting
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
          source_expression: "cast(updated_date as TIMESTAMP)"
        - name: is_most_recent_record
          data_type: BOOLEAN
          source_expression: "row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1"
      row_filters:
        - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
          on_failure: delete_row
        - rule: "try_cast(created_date as TIMESTAMP) is null OR (try_cast(created_date as TIMESTAMP) <= current_timestamp AND try_cast(created_date as TIMESTAMP) >= timestamp '2000-01-01 00:00:00')"
          on_failure: delete_row

```

## 规则问题

主键与外键同名映射可读作代码写错或Data；没有本表正确外键意图，不能凭实现粗糙认代码错。用实际关联0/1999反证P，选Data；只看到列名不算看到匹配反证。

## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:29)
- [SQL定位](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:146)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:480)
- [重跑 account_source](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:542)
- [重跑 created_null_allowed](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:611)
- [重跑 adjustment_amount_representation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:680)
- [重跑 amount_without_tax_representation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:749)
- [重跑 amount_without_tax_home_currency_representation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:818)
- [重跑 balance_representation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:887)
- [重跑 credit_balance_adjustment_amount_representation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:956)
- [重跑 credit_memo_amount_representation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:1025)
- [重跑 exchange_rate_representation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:1094)
- [重跑 exchange_rate_date_representation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:1163)
- [重跑 target_date_representation](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-030_stg_zuora__invoice.md:1232)
