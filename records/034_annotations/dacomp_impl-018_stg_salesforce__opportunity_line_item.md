# DAComp / impl-018_stg_salesforce__opportunity_line_item（v3）

## 错在哪里
通用id映射把opportunity_id和product_2_id都写成本行id，后续修FK时漏掉此表，两项并列。

证据复用入口：[018_impl-018_stg_salesforce__opportunity_line_item.md](../018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## opportunity_source
- 角色：并列；类别：**代码写错**；把握：中。
- 依据：event57明确写canonical foreign keys should remain FK columns, not the row's own id；修复遗漏本表。单改减少3000格。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 14 / content：
```text
e, _fivetran_active, _fivetran_start, _fivetran_end, _fivetran_synced
opportunity_line_item id, created_by_id, created_date, description, discount, has_quantity_schedule, has_revenue_schedule, has_schedule, is_deleted, last_modified_by_id, last_modified_date, last_referenced_date, last_viewed_date, list_price, name, opportunity_id, pricebook_entry_id, product_2_id, product_code, quantity, service_date, sort_order, system_modstamp, total_price, unit_price
order_data id, account_id, activated_by_id, activated_date, billing_city, billing_country, billing_country_code, billing_geocode_accuracy, billing_latitude, billing_longitude, billing_postal_code, billing_state, billing_state_code, billing_street, company_authorized_by_id, contract_id, created_by_id, created_date, customer_authorized_by_id, description, effective_date, end_date, is_deleted, is_reduction_order, last_modified_by_id, last_modified_date, last_r
```
## product_source
- 角色：并列；类别：**代码写错**；把握：中。
- 依据：同一正确意图的修补漏项；单改减少3000格。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 14 / content：
```text
e, _fivetran_active, _fivetran_start, _fivetran_end, _fivetran_synced
opportunity_line_item id, created_by_id, created_date, description, discount, has_quantity_schedule, has_revenue_schedule, has_schedule, is_deleted, last_modified_by_id, last_modified_date, last_referenced_date, last_viewed_date, list_price, name, opportunity_id, pricebook_entry_id, product_2_id, product_code, quantity, service_date, sort_order, system_modstamp, total_price, unit_price
order_data id, account_id, activated_by_id, activated_date, billing_city, billing_country, billing_country_code, billing_geocode_accuracy, billing_latitude, billing_longitude, billing_postal_code, billing_state, billing_state_code, billing_street, company_authorized_by_id, contract_id, created_by_id, created_date, customer_authorized_by_id, description, effective_date, end_date, is_deleted, is_reduction_order, last_modified_by_id, last_modified_date, last_r
```

## 规模、证据复用与新做
主要原因：代码写错。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-018_stg_salesforce__opportunity_line_item.md](../018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_salesforce__opportunity_line_item
      description: "Cleaned opportunity line item records with validated product and pricing information"
      source_table: raw.opportunity_line_item
      columns:
        - name: opportunity_line_item_id
          data_type: VARCHAR
        - name: opportunity_id
          data_type: VARCHAR
        - name: product_2_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: opportunity_line_item_description
          data_type: VARCHAR
        - name: has_quantity_schedule
          data_type: BOOLEAN
        - name: has_revenue_schedule
          data_type: BOOLEAN
        - name: is_deleted
          data_type: BOOLEAN
          validation_rules:
            - rule: "NOT COALESCE(is_deleted, false)"
              on_failure: delete_row
        - name: last_modified_date
          data_type: TIMESTAMP
        - name: list_price
          data_type: DECIMAL
        - name: pricebook_entry_id
          data_type: VARCHAR
        - name: quantity
          data_type: DECIMAL
        - name: service_date
          data_type: DATE
        - name: sort_order
          data_type: INTEGER
        - name: total_price
          data_type: DECIMAL
        - name: unit_price
          data_type: DECIMAL

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md:72)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md:221)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md:258)
- [重跑 opportunity_source](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md:291)
- [重跑 product_source](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md:331)
- [重跑 deleted_filter](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-018_stg_salesforce__opportunity_line_item.md:371)
