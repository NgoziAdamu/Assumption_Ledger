# DAComp / impl-022_stg_recharge__subscription_history（v3）

## 错在哪里
agent把subscription_id作为输出和latest分组键，gold改取历史行id；输出身份约定和窗口粒度均不同。

证据复用入口：[018_impl-022_stg_recharge__subscription_history.md](../018_annotations/018_impl-022_stg_recharge__subscription_history.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## source_id_projection
- 角色：主要；类别：**Unstated Choice**；把握：中。
- 依据：输出id身份未指定；agent订阅外键关联有支持；5043→1833行。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 10 / content：
```text
_at: VARCHAR
  _fivetran_deleted: BOOLEAN
  _fivetran_synced: VARCHAR
subscription_history:
  id: BIGINT
  subscription_id: BIGINT
  status: VARCHAR
  created_at: VARCHAR
  updated_at: VARCHAR
  _fivetran_deleted: BOOLEAN
  _fivetran_synced: VARCHAR
[('address',), ('address_discounts',), ('address_shipping_line',), ('charge',), ('charge_discount',), ('charge_line_item',), ('charge_order_attribute',), ('charge_shipping_line',), ('charge_tax_line',), ('checkout',), ('customer',), ('discount',), ('one_time_product',), ('order_bool_int',), ('order_line_item',), ('orders',), ('subscription',), ('subscription_history',)]

 address [('id', 'BIGINT', 'YES', None, None, None), ('customer_id', 'BIGINT', 'YES', None, None, None), ('subscription_id', 'DOUBLE', 'YES', None, None, None), ('first_name', 'VARCHAR', 'YES', None, None, None), ('last_name', 'VARCHAR', 'YES', None, None, None), ('company', 'VARCHAR', 'YES', No
```
## window_partition
- 角色：参与；类别：**Unstated Choice**；把握：中。
- 依据：latest窗口分组未给表达式，5043→4818行。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 10 / content：
```text
_at: VARCHAR
  _fivetran_deleted: BOOLEAN
  _fivetran_synced: VARCHAR
subscription_history:
  id: BIGINT
  subscription_id: BIGINT
  status: VARCHAR
  created_at: VARCHAR
  updated_at: VARCHAR
  _fivetran_deleted: BOOLEAN
  _fivetran_synced: VARCHAR
[('address',), ('address_discounts',), ('address_shipping_line',), ('charge',), ('charge_discount',), ('charge_line_item',), ('charge_order_attribute',), ('charge_shipping_line',), ('charge_tax_line',), ('checkout',), ('customer',), ('discount',), ('one_time_product',), ('order_bool_int',), ('order_line_item',), ('orders',), ('subscription',), ('subscription_history',)]

 address [('id', 'BIGINT', 'YES', None, None, None), ('customer_id', 'BIGINT', 'YES', None, None, None), ('subscription_id', 'DOUBLE', 'YES', None, None, None), ('first_name', 'VARCHAR', 'YES', None, None, None), ('last_name', 'VARCHAR', 'YES', None, None, None), ('company', 'VARCHAR', 'YES', No
```

## 规模、证据复用与新做
主要原因：Unstated Choice。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-022_stg_recharge__subscription_history.md](../018_annotations/018_impl-022_stg_recharge__subscription_history.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_recharge__subscription_history
      description: "History of subscription status changes with most recent flag."
      source_table: raw.subscription_history
      columns:
        - name: subscription_id
          data_type: BIGINT
        - name: subscription_created_at
          data_type: TIMESTAMP
        - name: subscription_updated_at
          data_type: TIMESTAMP
        - name: subscription_status
          data_type: VARCHAR
        - name: is_most_recent_record
          data_type: BOOLEAN


# --------------------------------------------------------------------------- #
# PHASE 2: Defines the business logic from staging tables to analytical models. #
# --------------------------------------------------------------------------- #
modeling_spec:
  purpose: "Apply business logic to staging data to build intermediate reusable models and final marts ready for analytics and BI."
  design_principles:
    - "staging only references raw"
    - "intermediate only references staging"
    - "marts only reference intermediate"
    - "No cross-layer or same-layer dependencies"
    - "Grain must be explicit and unique per model"

  intermediate_models:
```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-022_stg_recharge__subscription_history.md:29)
- [SQL定位](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-022_stg_recharge__subscription_history.md:53)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-022_stg_recharge__subscription_history.md:211)
- [重跑 source_id_projection](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-022_stg_recharge__subscription_history.md:232)
- [重跑 source_id_group](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-022_stg_recharge__subscription_history.md:260)
- [重跑 deleted_filter](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-022_stg_recharge__subscription_history.md:288)
