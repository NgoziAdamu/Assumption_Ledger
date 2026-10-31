# DAComp / impl-015_stg_quickbooks__item（v3）

## 错在哪里
tax_code_id取sales_tax_code_id而gold填NULL；agent另在导入raw时通过pandas改变了全NULL列类型。

证据复用入口：[018_impl-015_stg_quickbooks__item.md](../018_annotations/018_impl-015_stg_quickbooks__item.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## tax_code_null
- 角色：主要；类别：**Unstated Choice**；把握：中。
- 依据：sales/purchase税代码各2000非空且互不等，未指定统一tax_code_id来源；改NULL使2000行→0。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 14 / content：
```text
e, None), ('quantity_on_hand', 'VARCHAR', 'YES', None, None, None), ('sales_tax_code_id', 'VARCHAR', 'YES', None, None, None), ('sales_tax_included', 'VARCHAR', 'YES', None, None, None), ('stock_keeping_unit', 'VARCHAR', 'YES', None, None, None), ('sub_item', 'VARCHAR', 'YES', None, None, None), ('sync_token', 'VARCHAR', 'YES', None, None, None), ('taxable', 'VARCHAR', 'YES', None, None, None), ('track_quantity_on_hand', 'VARCHAR', 'YES', None, None, None), ('type', 'VARCHAR', 'YES', None, None, None), ('unit_price', 'VARCHAR', 'YES', None, None, None), ('updated_at', 'VARCHAR', 'YES', None, None, None)]
journal_entry_data [('id', 'VARCHAR', 'YES', None, None, None), ('adjustment', 'VARCHAR', 'YES', None, None, None), ('created_at', 'VARCHAR', 'YES', None, None, None), ('currency_id', 'VARCHAR', 'YES', None, None, None), ('doc_number', 'VARCHAR', 'YES', None, None, None), ('exchange_rate', 'VARCHAR', 'YES',
```

## 规模、证据复用与新做
主要原因：Unstated Choice。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-015_stg_quickbooks__item.md](../018_annotations/018_impl-015_stg_quickbooks__item.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_quickbooks__item
      description: "Cleaned product and service items with standardized pricing and inventory information"
      source_table: "raw.item_data"
      columns:
        - name: item_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: parent_item_id
          data_type: VARCHAR
        - name: income_account_id
          data_type: VARCHAR
        - name: expense_account_id
          data_type: VARCHAR
        - name: asset_account_id
          data_type: VARCHAR
        - name: tax_code_id
          data_type: VARCHAR
        - name: sales_tax_code_id
          data_type: VARCHAR
        - name: purchase_tax_code_id
          data_type: VARCHAR
        - name: name
          data_type: VARCHAR
          constraints: [not_null]
        - name: description
          data_type: VARCHAR
        - name: fully_qualified_name
          data_type: VARCHAR
        - name: sku
          data_type: VARCHAR
        - name: type
          data_type: VARCHAR
        - name: unit_price
          data_type: DECIMAL(28,6)
        - name: purchase_cost
          data_type: DECIMAL(28,6)
        - name: quantity_on_hand
          data_type: DECIMAL(28,6)
        - name: is_active
          data_type: BOOLEAN
        - name: is_taxable
          data_type: BOOLEAN
        - name: track_quantity_on_hand
          data_type: BOOLEAN
        - name: created_at
          data_type: TIMESTAMP
        - name: updated_at
          data_type: TIMESTAMP
        - name: sync_token
          data_type: VARCHAR
        - name: source_relation
          data_type: VARCHAR
      filter_conditions:
        - "id is not null and name is not null and track_quantity_on_hand is not null"

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-015_stg_quickbooks__item.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-015_stg_quickbooks__item.md:87)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-015_stg_quickbooks__item.md:245)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-015_stg_quickbooks__item.md:285)
- [重跑 tax_code_null](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-015_stg_quickbooks__item.md:323)
