# 015：逐张 raw 差异与待标注下游

只列 gold raw 存在、且与 initial 或 agent 至少一侧不同的 raw 表。下游只使用 008 B7 原记录的精确 schema.table 依赖边，筛选 013 状态为“待标注”。路径为一条最短路径，不代表唯一读取路径。

全量无差异记录及哈希：`015_raw_comparisons.jsonl` / `.csv`；逐题完整结构：`015_raw_impl-NNN.json`。

## impl-010 raw.deal_pipeline_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 20 | 20 | True | False | sorted_content_hash_differ |
| gold_vs_agent | 20 | 20 | True | False | sorted_content_hash_differ |

**按原顺序的列名与类型**

- gold：1. `pipeline_id` VARCHAR；2. `active` BOOLEAN；3. `display_order` BIGINT；4. `label` VARCHAR；5. `created_at` VARCHAR；6. `updated_at` VARCHAR
- initial：1. `pipeline_id` VARCHAR；2. `active` BOOLEAN；3. `display_order` BIGINT；4. `label` VARCHAR；5. `created_at` VARCHAR；6. `updated_at` VARCHAR
- agent：1. `pipeline_id` VARCHAR；2. `active` BOOLEAN；3. `display_order` BIGINT；4. `label` VARCHAR；5. `created_at` VARCHAR；6. `updated_at` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| intermediate | int_hubspot__owner_performance_metrics | 间接 | raw.deal_pipeline_data → staging.stg_hubspot__deal_pipeline → intermediate.int_hubspot__deals_enhanced → intermediate.int_hubspot__owner_performance_metrics |
| sales | hubspot__sales_performance_dashboard | 间接 | raw.deal_pipeline_data → staging.stg_hubspot__deal_pipeline → intermediate.int_hubspot__deals_enhanced → intermediate.int_hubspot__deal_performance_metrics → sales.hubspot__sales_performance_dashboard |
| sales | hubspot__sales_rep_performance | 间接 | raw.deal_pipeline_data → staging.stg_hubspot__deal_pipeline → intermediate.int_hubspot__deals_enhanced → intermediate.int_hubspot__deal_performance_metrics → sales.hubspot__sales_rep_performance |
| staging | stg_hubspot__deal_pipeline | 直接 | raw.deal_pipeline_data → staging.stg_hubspot__deal_pipeline |

来源：`015_raw_impl-010.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-010 raw.deal_pipeline_stage_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 104 | 104 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 104 | 104 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |

**按原顺序的列名与类型**

- gold：1. `stage_id` BIGINT；2. `pipeline_id` VARCHAR；3. `label` VARCHAR；4. `display_order` BIGINT；5. `probability` DOUBLE；6. `active` BOOLEAN；7. `closed_won` BOOLEAN；8. `created_at` VARCHAR；9. `updated_at` VARCHAR
- initial：1. `stage_id` BIGINT；2. `pipeline_id` VARCHAR；3. `label` VARCHAR；4. `display_order` BIGINT；5. `probability` DOUBLE；6. `active` BOOLEAN；7. `closed_won` BOOLEAN；8. `created_at` VARCHAR；9. `updated_at` VARCHAR；10. `is_closed` VARCHAR
- agent：1. `stage_id` BIGINT；2. `pipeline_id` VARCHAR；3. `label` VARCHAR；4. `display_order` BIGINT；5. `probability` DOUBLE；6. `active` BOOLEAN；7. `closed_won` BOOLEAN；8. `created_at` VARCHAR；9. `updated_at` VARCHAR；10. `is_closed` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| intermediate | int_hubspot__owner_performance_metrics | 间接 | raw.deal_pipeline_stage_data → staging.stg_hubspot__deal_pipeline_stage → intermediate.int_hubspot__deals_enhanced → intermediate.int_hubspot__owner_performance_metrics |
| sales | hubspot__sales_performance_dashboard | 间接 | raw.deal_pipeline_stage_data → staging.stg_hubspot__deal_pipeline_stage → intermediate.int_hubspot__deals_enhanced → intermediate.int_hubspot__deal_performance_metrics → sales.hubspot__sales_performance_dashboard |
| sales | hubspot__sales_rep_performance | 间接 | raw.deal_pipeline_stage_data → staging.stg_hubspot__deal_pipeline_stage → intermediate.int_hubspot__deals_enhanced → intermediate.int_hubspot__deal_performance_metrics → sales.hubspot__sales_rep_performance |
| staging | stg_hubspot__deal_pipeline_stage | 直接 | raw.deal_pipeline_stage_data → staging.stg_hubspot__deal_pipeline_stage |

来源：`015_raw_impl-010.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-010 raw.email_event_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 736 | 736 | True | False | sorted_content_hash_differ |
| gold_vs_agent | 736 | 736 | True | False | sorted_content_hash_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `app_id` BIGINT；3. `caused_by_created` BIGINT；4. `caused_by_id` BIGINT；5. `created` VARCHAR；6. `email_campaign_id` BIGINT；7. `obsoleted_by_created` BIGINT；8. `obsoleted_by_id` BIGINT；9. `portal_id` BIGINT；10. `sent_by_created` VARCHAR；11. `sent_by_id` BIGINT；12. `type` VARCHAR；13. `filtered_event` VARCHAR；14. `recipient` VARCHAR
- initial：1. `id` VARCHAR；2. `app_id` BIGINT；3. `caused_by_created` BIGINT；4. `caused_by_id` BIGINT；5. `created` VARCHAR；6. `email_campaign_id` BIGINT；7. `obsoleted_by_created` BIGINT；8. `obsoleted_by_id` BIGINT；9. `portal_id` BIGINT；10. `sent_by_created` VARCHAR；11. `sent_by_id` BIGINT；12. `type` VARCHAR；13. `filtered_event` VARCHAR；14. `recipient` VARCHAR
- agent：1. `id` VARCHAR；2. `app_id` BIGINT；3. `caused_by_created` BIGINT；4. `caused_by_id` BIGINT；5. `created` VARCHAR；6. `email_campaign_id` BIGINT；7. `obsoleted_by_created` BIGINT；8. `obsoleted_by_id` BIGINT；9. `portal_id` BIGINT；10. `sent_by_created` VARCHAR；11. `sent_by_id` BIGINT；12. `type` VARCHAR；13. `filtered_event` VARCHAR；14. `recipient` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_hubspot__email_event | 直接 | raw.email_event_data → staging.stg_hubspot__email_event |

来源：`015_raw_impl-010.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-010 raw.form_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1150 | 1150 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 1150 | 1150 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |

**按原顺序的列名与类型**

- gold：1. `guid` BIGINT；2. `action` VARCHAR；3. `created_at` VARCHAR；4. `css_class` VARCHAR；5. `follow_up_id` BIGINT；6. `form_type` VARCHAR；7. `lead_nurturing_campaign_id` BIGINT；8. `method` VARCHAR；9. `name` VARCHAR；10. `notify_recipients` VARCHAR；11. `portal_id` BIGINT；12. `redirect` VARCHAR；13. `submit_text` VARCHAR；14. `updated_at` VARCHAR
- initial：1. `guid` VARCHAR；2. `portal_id` INTEGER；3. `name` VARCHAR；4. `form_type` VARCHAR；5. `method` VARCHAR；6. `action` VARCHAR；7. `redirect` VARCHAR；8. `lead_nurturing_campaign_id` VARCHAR；9. `follow_up_id` VARCHAR；10. `created_at` VARCHAR；11. `updated_at` VARCHAR；12. `css_class` VARCHAR；13. `notify_recipients` VARCHAR；14. `submit_text` VARCHAR
- agent：1. `guid` VARCHAR；2. `portal_id` INTEGER；3. `name` VARCHAR；4. `form_type` VARCHAR；5. `method` VARCHAR；6. `action` VARCHAR；7. `redirect` VARCHAR；8. `lead_nurturing_campaign_id` VARCHAR；9. `follow_up_id` VARCHAR；10. `created_at` VARCHAR；11. `updated_at` VARCHAR；12. `css_class` VARCHAR；13. `notify_recipients` VARCHAR；14. `submit_text` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_hubspot__form | 直接 | raw.form_data → staging.stg_hubspot__form |

来源：`015_raw_impl-010.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-010 raw.ticket_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1150 | 1150 | True | False | sorted_content_hash_differ |
| gold_vs_agent | 1150 | 1150 | True | False | sorted_content_hash_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `is_deleted` VARCHAR；3. `property_closed_date` VARCHAR；4. `property_createdate` VARCHAR；5. `property_first_agent_reply_date` VARCHAR；6. `property_hs_pipeline` VARCHAR；7. `property_hs_pipeline_stage` VARCHAR；8. `property_hs_ticket_category` VARCHAR；9. `property_hs_ticket_priority` BIGINT；10. `property_hubspot_owner_id` BIGINT；11. `property_subject` VARCHAR；12. `property_content` VARCHAR
- initial：1. `id` VARCHAR；2. `is_deleted` VARCHAR；3. `property_closed_date` VARCHAR；4. `property_createdate` VARCHAR；5. `property_first_agent_reply_date` VARCHAR；6. `property_hs_pipeline` VARCHAR；7. `property_hs_pipeline_stage` VARCHAR；8. `property_hs_ticket_category` VARCHAR；9. `property_hs_ticket_priority` BIGINT；10. `property_hubspot_owner_id` BIGINT；11. `property_subject` VARCHAR；12. `property_content` VARCHAR
- agent：1. `id` VARCHAR；2. `is_deleted` VARCHAR；3. `property_closed_date` VARCHAR；4. `property_createdate` VARCHAR；5. `property_first_agent_reply_date` VARCHAR；6. `property_hs_pipeline` VARCHAR；7. `property_hs_pipeline_stage` VARCHAR；8. `property_hs_ticket_category` VARCHAR；9. `property_hs_ticket_priority` BIGINT；10. `property_hubspot_owner_id` BIGINT；11. `property_subject` VARCHAR；12. `property_content` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_hubspot__ticket | 直接 | raw.ticket_data → staging.stg_hubspot__ticket |

来源：`015_raw_impl-010.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-010 raw.ticket_pipeline_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1033 | 200 | False | 未比较 | ordered_columns_or_types_differ, row_counts_differ |
| gold_vs_agent | 1033 | 200 | False | 未比较 | ordered_columns_or_types_differ, row_counts_differ |

**按原顺序的列名与类型**

- gold：1. `pipeline_id` BIGINT；2. `active` VARCHAR；3. `display_order` BIGINT；4. `label` VARCHAR；5. `object_type_id` VARCHAR；6. `created_at` VARCHAR；7. `updated_at` VARCHAR
- initial：1. `pipeline_id` VARCHAR；2. `object_type_id` VARCHAR；3. `label` VARCHAR；4. `display_order` BIGINT；5. `active` BOOLEAN；6. `created_at` VARCHAR；7. `updated_at` VARCHAR
- agent：1. `pipeline_id` VARCHAR；2. `object_type_id` VARCHAR；3. `label` VARCHAR；4. `display_order` BIGINT；5. `active` BOOLEAN；6. `created_at` VARCHAR；7. `updated_at` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_hubspot__ticket_pipeline | 直接 | raw.ticket_pipeline_data → staging.stg_hubspot__ticket_pipeline |

来源：`015_raw_impl-010.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-010 raw.ticket_pipeline_stage_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 807 | 400 | False | 未比较 | ordered_columns_or_types_differ, row_counts_differ |
| gold_vs_agent | 807 | 400 | False | 未比较 | ordered_columns_or_types_differ, row_counts_differ |

**按原顺序的列名与类型**

- gold：1. `stage_id` BIGINT；2. `active` VARCHAR；3. `display_order` BIGINT；4. `is_closed` VARCHAR；5. `label` VARCHAR；6. `pipeline_id` BIGINT；7. `ticket_state` VARCHAR；8. `created_at` VARCHAR；9. `updated_at` VARCHAR
- initial：1. `stage_id` VARCHAR；2. `pipeline_id` VARCHAR；3. `label` VARCHAR；4. `ticket_state` VARCHAR；5. `display_order` BIGINT；6. `active` BOOLEAN；7. `is_closed` BOOLEAN；8. `created_at` VARCHAR；9. `updated_at` VARCHAR
- agent：1. `stage_id` VARCHAR；2. `pipeline_id` VARCHAR；3. `label` VARCHAR；4. `ticket_state` VARCHAR；5. `display_order` BIGINT；6. `active` BOOLEAN；7. `is_closed` BOOLEAN；8. `created_at` VARCHAR；9. `updated_at` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_hubspot__ticket_pipeline_stage | 直接 | raw.ticket_pipeline_stage_data → staging.stg_hubspot__ticket_pipeline_stage |

来源：`015_raw_impl-010.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.address_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 5000 | 5000 | True | True | 无 |
| gold_vs_agent | 5000 | 5000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `city` VARCHAR；3. `country` VARCHAR；4. `country_sub_division_code` VARCHAR；5. `latitude` DOUBLE；6. `line_1` VARCHAR；7. `line_2` VARCHAR；8. `line_3` VARCHAR；9. `line_4` VARCHAR；10. `line_5` VARCHAR；11. `longitude` DOUBLE；12. `postal_code` BIGINT
- initial：1. `id` VARCHAR；2. `city` VARCHAR；3. `country` VARCHAR；4. `country_sub_division_code` VARCHAR；5. `latitude` DOUBLE；6. `line_1` VARCHAR；7. `line_2` VARCHAR；8. `line_3` VARCHAR；9. `line_4` VARCHAR；10. `line_5` VARCHAR；11. `longitude` DOUBLE；12. `postal_code` BIGINT
- agent：1. `id` VARCHAR；2. `city` VARCHAR；3. `country` VARCHAR；4. `country_sub_division_code` VARCHAR；5. `latitude` DOUBLE；6. `line_1` VARCHAR；7. `line_2` VARCHAR；8. `line_3` INTEGER；9. `line_4` INTEGER；10. `line_5` INTEGER；11. `longitude` DOUBLE；12. `postal_code` BIGINT

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.bill_payment_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | True | True | 无 |
| gold_vs_agent | 3000 | 3000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `check_bank_account_id` VARCHAR；3. `check_print_status` VARCHAR；4. `created_at` VARCHAR；5. `credit_card_account_id` VARCHAR；6. `currency_id` BIGINT；7. `department_id` VARCHAR；8. `doc_number` BIGINT；9. `exchange_rate` VARCHAR；10. `pay_type` VARCHAR；11. `payable_account_id` VARCHAR；12. `private_note` VARCHAR；13. `process_bill_payment` VARCHAR；14. `sync_token` BIGINT；15. `total_amount` DOUBLE；16. `transaction_date` TIMESTAMP；17. `updated_at` TIMESTAMP；18. `vendor_id` VARCHAR
- initial：1. `id` VARCHAR；2. `check_bank_account_id` VARCHAR；3. `check_print_status` VARCHAR；4. `created_at` VARCHAR；5. `credit_card_account_id` VARCHAR；6. `currency_id` BIGINT；7. `department_id` VARCHAR；8. `doc_number` BIGINT；9. `exchange_rate` VARCHAR；10. `pay_type` VARCHAR；11. `payable_account_id` VARCHAR；12. `private_note` VARCHAR；13. `process_bill_payment` VARCHAR；14. `sync_token` BIGINT；15. `total_amount` DOUBLE；16. `transaction_date` TIMESTAMP；17. `updated_at` TIMESTAMP；18. `vendor_id` VARCHAR
- agent：1. `id` VARCHAR；2. `check_bank_account_id` VARCHAR；3. `check_print_status` INTEGER；4. `created_at` INTEGER；5. `credit_card_account_id` VARCHAR；6. `currency_id` BIGINT；7. `department_id` VARCHAR；8. `doc_number` BIGINT；9. `exchange_rate` INTEGER；10. `pay_type` INTEGER；11. `payable_account_id` VARCHAR；12. `private_note` INTEGER；13. `process_bill_payment` INTEGER；14. `sync_token` BIGINT；15. `total_amount` DOUBLE；16. `transaction_date` TIMESTAMP；17. `updated_at` TIMESTAMP；18. `vendor_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.bundle_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 500 | 500 | True | True | 无 |
| gold_vs_agent | 500 | 500 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `active` BOOLEAN；3. `created_at` VARCHAR；4. `description` VARCHAR；5. `fully_qualified_name` VARCHAR；6. `name` VARCHAR；7. `print_grouped_items` VARCHAR；8. `purchase_cost` VARCHAR；9. `sync_token` BIGINT；10. `taxable` BOOLEAN；11. `unit_price` VARCHAR；12. `updated_at` TIMESTAMP
- initial：1. `id` VARCHAR；2. `active` BOOLEAN；3. `created_at` VARCHAR；4. `description` VARCHAR；5. `fully_qualified_name` VARCHAR；6. `name` VARCHAR；7. `print_grouped_items` VARCHAR；8. `purchase_cost` VARCHAR；9. `sync_token` BIGINT；10. `taxable` BOOLEAN；11. `unit_price` VARCHAR；12. `updated_at` TIMESTAMP
- agent：1. `id` VARCHAR；2. `active` BOOLEAN；3. `created_at` INTEGER；4. `description` VARCHAR；5. `fully_qualified_name` VARCHAR；6. `name` VARCHAR；7. `print_grouped_items` INTEGER；8. `purchase_cost` INTEGER；9. `sync_token` BIGINT；10. `taxable` BOOLEAN；11. `unit_price` INTEGER；12. `updated_at` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.bundle_item_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1500 | 1500 | True | True | 无 |
| gold_vs_agent | 1500 | 1500 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `bundle_id` BIGINT；2. `item_id` VARCHAR；3. `item_quantity` VARCHAR
- initial：1. `bundle_id` BIGINT；2. `item_id` VARCHAR；3. `item_quantity` VARCHAR
- agent：1. `bundle_id` BIGINT；2. `item_id` VARCHAR；3. `item_quantity` INTEGER

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.credit_card_payment_txn_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2000 | 2000 | True | True | 无 |
| gold_vs_agent | 2000 | 2000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `amount` DOUBLE；3. `bank_account_id` VARCHAR；4. `credit_card_account_id` VARCHAR；5. `created_at` VARCHAR；6. `updated_at` TIMESTAMP；7. `currency_id` BIGINT；8. `transaction_date` TIMESTAMP
- initial：1. `id` VARCHAR；2. `amount` DOUBLE；3. `bank_account_id` VARCHAR；4. `credit_card_account_id` VARCHAR；5. `created_at` VARCHAR；6. `updated_at` TIMESTAMP；7. `currency_id` BIGINT；8. `transaction_date` TIMESTAMP
- agent：1. `id` VARCHAR；2. `amount` DOUBLE；3. `bank_account_id` VARCHAR；4. `credit_card_account_id` VARCHAR；5. `created_at` INTEGER；6. `updated_at` TIMESTAMP；7. `currency_id` BIGINT；8. `transaction_date` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.credit_memo_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1000 | 1000 | True | True | 无 |
| gold_vs_agent | 1000 | 1000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `apply_tax_after_discount` VARCHAR；3. `balance` DOUBLE；4. `bill_email` VARCHAR；5. `billing_address_id` VARCHAR；6. `class_id` BIGINT；7. `created_at` VARCHAR；8. `currency_id` BIGINT；9. `custom_p_o_number` BIGINT；10. `customer_id` VARCHAR；11. `customer_memo` VARCHAR；12. `department_id` VARCHAR；13. `doc_number` BIGINT；14. `email_status` VARCHAR；15. `exchange_rate` VARCHAR；16. `global_tax_calculation` VARCHAR；17. `home_balance` DOUBLE；18. `home_total_amount` DOUBLE；19. `payment_method_id` BIGINT；20. `print_status` VARCHAR；21. `private_note` VARCHAR；22. `remaining_credit` VARCHAR；23. `sales_term_id` BIGINT；24. `shipping_address_id` VARCHAR；25. `sync_token` BIGINT；26. `total_amount` DOUBLE；27. `total_tax` DOUBLE；28. `transaction_date` TIMESTAMP；29. `updated_at` TIMESTAMP
- initial：1. `id` VARCHAR；2. `apply_tax_after_discount` VARCHAR；3. `balance` DOUBLE；4. `bill_email` VARCHAR；5. `billing_address_id` VARCHAR；6. `class_id` BIGINT；7. `created_at` VARCHAR；8. `currency_id` BIGINT；9. `custom_p_o_number` BIGINT；10. `customer_id` VARCHAR；11. `customer_memo` VARCHAR；12. `department_id` VARCHAR；13. `doc_number` BIGINT；14. `email_status` VARCHAR；15. `exchange_rate` VARCHAR；16. `global_tax_calculation` VARCHAR；17. `home_balance` DOUBLE；18. `home_total_amount` DOUBLE；19. `payment_method_id` BIGINT；20. `print_status` VARCHAR；21. `private_note` VARCHAR；22. `remaining_credit` VARCHAR；23. `sales_term_id` BIGINT；24. `shipping_address_id` VARCHAR；25. `sync_token` BIGINT；26. `total_amount` DOUBLE；27. `total_tax` DOUBLE；28. `transaction_date` TIMESTAMP；29. `updated_at` TIMESTAMP
- agent：1. `id` VARCHAR；2. `apply_tax_after_discount` INTEGER；3. `balance` DOUBLE；4. `bill_email` VARCHAR；5. `billing_address_id` VARCHAR；6. `class_id` BIGINT；7. `created_at` INTEGER；8. `currency_id` BIGINT；9. `custom_p_o_number` BIGINT；10. `customer_id` VARCHAR；11. `customer_memo` INTEGER；12. `department_id` VARCHAR；13. `doc_number` BIGINT；14. `email_status` VARCHAR；15. `exchange_rate` INTEGER；16. `global_tax_calculation` INTEGER；17. `home_balance` DOUBLE；18. `home_total_amount` DOUBLE；19. `payment_method_id` BIGINT；20. `print_status` INTEGER；21. `private_note` INTEGER；22. `remaining_credit` INTEGER；23. `sales_term_id` BIGINT；24. `shipping_address_id` VARCHAR；25. `sync_token` BIGINT；26. `total_amount` DOUBLE；27. `total_tax` DOUBLE；28. `transaction_date` TIMESTAMP；29. `updated_at` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.credit_memo_line_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2500 | 2500 | True | True | 无 |
| gold_vs_agent | 2500 | 2500 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `credit_memo_id` BIGINT；2. `index` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` VARCHAR；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` VARCHAR；12. `discount_percent_based` VARCHAR；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` VARCHAR；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` VARCHAR；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` VARCHAR；23. `sub_total_item_id` VARCHAR
- initial：1. `credit_memo_id` BIGINT；2. `index` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` VARCHAR；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` VARCHAR；12. `discount_percent_based` VARCHAR；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` VARCHAR；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` VARCHAR；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` VARCHAR；23. `sub_total_item_id` VARCHAR
- agent：1. `credit_memo_id` BIGINT；2. `index` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` INTEGER；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` INTEGER；12. `discount_percent_based` INTEGER；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` INTEGER；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` INTEGER；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` INTEGER；23. `sub_total_item_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.department_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 50 | 50 | True | True | 无 |
| gold_vs_agent | 50 | 50 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `active` VARCHAR；3. `created_at` VARCHAR；4. `fully_qualified_name` VARCHAR；5. `name` VARCHAR；6. `parent_department_id` VARCHAR；7. `sub_department` VARCHAR；8. `sync_token` VARCHAR；9. `updated_at` VARCHAR
- initial：1. `id` VARCHAR；2. `active` VARCHAR；3. `created_at` VARCHAR；4. `fully_qualified_name` VARCHAR；5. `name` VARCHAR；6. `parent_department_id` VARCHAR；7. `sub_department` VARCHAR；8. `sync_token` VARCHAR；9. `updated_at` VARCHAR
- agent：1. `id` VARCHAR；2. `active` VARCHAR；3. `created_at` VARCHAR；4. `fully_qualified_name` VARCHAR；5. `name` VARCHAR；6. `parent_department_id` INTEGER；7. `sub_department` VARCHAR；8. `sync_token` VARCHAR；9. `updated_at` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.deposit_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1500 | 1500 | True | True | 无 |
| gold_vs_agent | 1500 | 1500 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `account_id` VARCHAR；3. `cash_back_account_id` VARCHAR；4. `cash_back_amount` DOUBLE；5. `cash_back_memo` VARCHAR；6. `created_at` VARCHAR；7. `currency_id` BIGINT；8. `department_id` VARCHAR；9. `global_tax_calculation` VARCHAR；10. `home_total_amount` DOUBLE；11. `private_note` VARCHAR；12. `sync_token` BIGINT；13. `total_amount` DOUBLE；14. `transaction_date` TIMESTAMP；15. `transaction_source` VARCHAR；16. `transaction_status` VARCHAR；17. `updated_at` TIMESTAMP
- initial：1. `id` VARCHAR；2. `account_id` VARCHAR；3. `cash_back_account_id` VARCHAR；4. `cash_back_amount` DOUBLE；5. `cash_back_memo` VARCHAR；6. `created_at` VARCHAR；7. `currency_id` BIGINT；8. `department_id` VARCHAR；9. `global_tax_calculation` VARCHAR；10. `home_total_amount` DOUBLE；11. `private_note` VARCHAR；12. `sync_token` BIGINT；13. `total_amount` DOUBLE；14. `transaction_date` TIMESTAMP；15. `transaction_source` VARCHAR；16. `transaction_status` VARCHAR；17. `updated_at` TIMESTAMP
- agent：1. `id` VARCHAR；2. `account_id` VARCHAR；3. `cash_back_account_id` VARCHAR；4. `cash_back_amount` DOUBLE；5. `cash_back_memo` INTEGER；6. `created_at` INTEGER；7. `currency_id` BIGINT；8. `department_id` VARCHAR；9. `global_tax_calculation` INTEGER；10. `home_total_amount` DOUBLE；11. `private_note` INTEGER；12. `sync_token` BIGINT；13. `total_amount` DOUBLE；14. `transaction_date` TIMESTAMP；15. `transaction_source` INTEGER；16. `transaction_status` INTEGER；17. `updated_at` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.deposit_line_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | True | True | 无 |
| gold_vs_agent | 3000 | 3000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `deposit_id` BIGINT；2. `index` BIGINT；3. `amount` DOUBLE；4. `deposit_account_id` VARCHAR；5. `deposit_check_number` BIGINT；6. `deposit_class_id` BIGINT；7. `deposit_customer_id` VARCHAR；8. `deposit_payment_method_id` BIGINT；9. `deposit_tax_applicable_on` VARCHAR；10. `deposit_tax_code_id` BIGINT；11. `deposit_transaction_type` VARCHAR；12. `description` VARCHAR；13. `detail_type` VARCHAR；14. `expense_id` BIGINT；15. `invoice_id` BIGINT；16. `journal_entry_id` BIGINT；17. `payment_id` BIGINT；18. `purchase_id` BIGINT；19. `refund_receipt_id` BIGINT；20. `sales_receipt_id` BIGINT；21. `transfer_id` BIGINT；22. `bill_id` BIGINT；23. `vendor_credit_id` VARCHAR
- initial：1. `deposit_id` BIGINT；2. `index` BIGINT；3. `amount` DOUBLE；4. `deposit_account_id` VARCHAR；5. `deposit_check_number` BIGINT；6. `deposit_class_id` BIGINT；7. `deposit_customer_id` VARCHAR；8. `deposit_payment_method_id` BIGINT；9. `deposit_tax_applicable_on` VARCHAR；10. `deposit_tax_code_id` BIGINT；11. `deposit_transaction_type` VARCHAR；12. `description` VARCHAR；13. `detail_type` VARCHAR；14. `expense_id` BIGINT；15. `invoice_id` BIGINT；16. `journal_entry_id` BIGINT；17. `payment_id` BIGINT；18. `purchase_id` BIGINT；19. `refund_receipt_id` BIGINT；20. `sales_receipt_id` BIGINT；21. `transfer_id` BIGINT；22. `bill_id` BIGINT；23. `vendor_credit_id` VARCHAR
- agent：1. `deposit_id` BIGINT；2. `index` BIGINT；3. `amount` DOUBLE；4. `deposit_account_id` VARCHAR；5. `deposit_check_number` BIGINT；6. `deposit_class_id` BIGINT；7. `deposit_customer_id` VARCHAR；8. `deposit_payment_method_id` BIGINT；9. `deposit_tax_applicable_on` INTEGER；10. `deposit_tax_code_id` BIGINT；11. `deposit_transaction_type` INTEGER；12. `description` VARCHAR；13. `detail_type` INTEGER；14. `expense_id` BIGINT；15. `invoice_id` BIGINT；16. `journal_entry_id` BIGINT；17. `payment_id` BIGINT；18. `purchase_id` BIGINT；19. `refund_receipt_id` BIGINT；20. `sales_receipt_id` BIGINT；21. `transfer_id` BIGINT；22. `bill_id` BIGINT；23. `vendor_credit_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.estimate_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2000 | 2000 | True | True | 无 |
| gold_vs_agent | 2000 | 2000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `accepted_by` VARCHAR；3. `accepted_date` TIMESTAMP；4. `apply_tax_after_discount` VARCHAR；5. `bill_email` VARCHAR；6. `billing_address_id` VARCHAR；7. `class_id` BIGINT；8. `created_at` VARCHAR；9. `currency_id` BIGINT；10. `custom_p_o_number` BIGINT；11. `custom_sales_rep` VARCHAR；12. `customer_id` VARCHAR；13. `customer_memo` VARCHAR；14. `delivery_type` VARCHAR；15. `department_id` VARCHAR；16. `doc_number` BIGINT；17. `due_date` TIMESTAMP；18. `email_status` VARCHAR；19. `exchange_rate` VARCHAR；20. `expiration_date` TIMESTAMP；21. `global_tax_calculation` VARCHAR；22. `home_total_amount` DOUBLE；23. `print_status` VARCHAR；24. `private_note` VARCHAR；25. `sales_term_id` BIGINT；26. `ship_date` TIMESTAMP；27. `shipping_address_id` VARCHAR；28. `sync_token` BIGINT；29. `tax_code_id` BIGINT；30. `total_amount` DOUBLE；31. `total_tax` DOUBLE；32. `transaction_date` TIMESTAMP；33. `transaction_status` VARCHAR；34. `updated_at` TIMESTAMP
- initial：1. `id` VARCHAR；2. `accepted_by` VARCHAR；3. `accepted_date` TIMESTAMP；4. `apply_tax_after_discount` VARCHAR；5. `bill_email` VARCHAR；6. `billing_address_id` VARCHAR；7. `class_id` BIGINT；8. `created_at` VARCHAR；9. `currency_id` BIGINT；10. `custom_p_o_number` BIGINT；11. `custom_sales_rep` VARCHAR；12. `customer_id` VARCHAR；13. `customer_memo` VARCHAR；14. `delivery_type` VARCHAR；15. `department_id` VARCHAR；16. `doc_number` BIGINT；17. `due_date` TIMESTAMP；18. `email_status` VARCHAR；19. `exchange_rate` VARCHAR；20. `expiration_date` TIMESTAMP；21. `global_tax_calculation` VARCHAR；22. `home_total_amount` DOUBLE；23. `print_status` VARCHAR；24. `private_note` VARCHAR；25. `sales_term_id` BIGINT；26. `ship_date` TIMESTAMP；27. `shipping_address_id` VARCHAR；28. `sync_token` BIGINT；29. `tax_code_id` BIGINT；30. `total_amount` DOUBLE；31. `total_tax` DOUBLE；32. `transaction_date` TIMESTAMP；33. `transaction_status` VARCHAR；34. `updated_at` TIMESTAMP
- agent：1. `id` VARCHAR；2. `accepted_by` INTEGER；3. `accepted_date` TIMESTAMP；4. `apply_tax_after_discount` INTEGER；5. `bill_email` VARCHAR；6. `billing_address_id` VARCHAR；7. `class_id` BIGINT；8. `created_at` INTEGER；9. `currency_id` BIGINT；10. `custom_p_o_number` BIGINT；11. `custom_sales_rep` INTEGER；12. `customer_id` VARCHAR；13. `customer_memo` INTEGER；14. `delivery_type` INTEGER；15. `department_id` VARCHAR；16. `doc_number` BIGINT；17. `due_date` TIMESTAMP；18. `email_status` VARCHAR；19. `exchange_rate` INTEGER；20. `expiration_date` TIMESTAMP；21. `global_tax_calculation` INTEGER；22. `home_total_amount` DOUBLE；23. `print_status` INTEGER；24. `private_note` INTEGER；25. `sales_term_id` BIGINT；26. `ship_date` TIMESTAMP；27. `shipping_address_id` VARCHAR；28. `sync_token` BIGINT；29. `tax_code_id` BIGINT；30. `total_amount` DOUBLE；31. `total_tax` DOUBLE；32. `transaction_date` TIMESTAMP；33. `transaction_status` INTEGER；34. `updated_at` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.estimate_line_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 5000 | 5000 | True | True | 无 |
| gold_vs_agent | 5000 | 5000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `estimate_id` BIGINT；2. `index` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` VARCHAR；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` VARCHAR；12. `discount_percent_based` VARCHAR；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` VARCHAR；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` VARCHAR；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` VARCHAR；23. `sub_total_item_id` VARCHAR；24. `item_id` VARCHAR；25. `quantity` VARCHAR；26. `tax_code_id` BIGINT；27. `account_id` VARCHAR
- initial：1. `estimate_id` BIGINT；2. `index` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` VARCHAR；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` VARCHAR；12. `discount_percent_based` VARCHAR；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` VARCHAR；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` VARCHAR；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` VARCHAR；23. `sub_total_item_id` VARCHAR；24. `item_id` VARCHAR；25. `quantity` VARCHAR；26. `tax_code_id` BIGINT；27. `account_id` VARCHAR
- agent：1. `estimate_id` BIGINT；2. `index` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` INTEGER；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` INTEGER；12. `discount_percent_based` INTEGER；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` INTEGER；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` INTEGER；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` INTEGER；23. `sub_total_item_id` VARCHAR；24. `item_id` VARCHAR；25. `quantity` INTEGER；26. `tax_code_id` BIGINT；27. `account_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.invoice_line_bundle_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | True | True | 无 |
| gold_vs_agent | 3000 | 3000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `index` BIGINT；2. `invoice_id` BIGINT；3. `account_id` VARCHAR；4. `amount` DOUBLE；5. `class_id` BIGINT；6. `description` VARCHAR；7. `discount_amount` DOUBLE；8. `discount_rate` VARCHAR；9. `invoice_line_index` BIGINT；10. `item_id` VARCHAR；11. `line_num` VARCHAR；12. `quantity` VARCHAR；13. `service_date` TIMESTAMP；14. `tax_code_id` BIGINT；15. `unit_price` VARCHAR；16. `sales_item_item_id` VARCHAR；17. `sales_item_quantity` VARCHAR；18. `sales_item_tax_code_id` VARCHAR；19. `sales_item_account_id` VARCHAR
- initial：1. `index` BIGINT；2. `invoice_id` BIGINT；3. `account_id` VARCHAR；4. `amount` DOUBLE；5. `class_id` BIGINT；6. `description` VARCHAR；7. `discount_amount` DOUBLE；8. `discount_rate` VARCHAR；9. `invoice_line_index` BIGINT；10. `item_id` VARCHAR；11. `line_num` VARCHAR；12. `quantity` VARCHAR；13. `service_date` TIMESTAMP；14. `tax_code_id` BIGINT；15. `unit_price` VARCHAR；16. `sales_item_item_id` VARCHAR；17. `sales_item_quantity` VARCHAR；18. `sales_item_tax_code_id` VARCHAR；19. `sales_item_account_id` VARCHAR
- agent：1. `index` BIGINT；2. `invoice_id` BIGINT；3. `account_id` VARCHAR；4. `amount` DOUBLE；5. `class_id` BIGINT；6. `description` VARCHAR；7. `discount_amount` DOUBLE；8. `discount_rate` INTEGER；9. `invoice_line_index` BIGINT；10. `item_id` VARCHAR；11. `line_num` INTEGER；12. `quantity` INTEGER；13. `service_date` TIMESTAMP；14. `tax_code_id` BIGINT；15. `unit_price` INTEGER；16. `sales_item_item_id` VARCHAR；17. `sales_item_quantity` INTEGER；18. `sales_item_tax_code_id` VARCHAR；19. `sales_item_account_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.invoice_line_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 20000 | 20000 | True | True | 无 |
| gold_vs_agent | 20000 | 20000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `index` BIGINT；2. `invoice_id` VARCHAR；3. `amount` DOUBLE；4. `bundle_id` VARCHAR；5. `bundle_quantity` VARCHAR；6. `description` VARCHAR；7. `description_service_date` VARCHAR；8. `description_tax_code_id` VARCHAR；9. `discount_account_id` VARCHAR；10. `discount_class_id` VARCHAR；11. `discount_discount_percent` DOUBLE；12. `discount_percent_based` VARCHAR；13. `discount_tax_code_id` VARCHAR；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` BIGINT；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` DOUBLE；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` DOUBLE；20. `sales_item_service_date` VARCHAR；21. `sales_item_tax_code_id` BIGINT；22. `sales_item_unit_price` DOUBLE；23. `sub_total_item_id` VARCHAR；24. `item_id` VARCHAR；25. `quantity` VARCHAR；26. `tax_code_id` VARCHAR；27. `account_id` VARCHAR；28. `detail_type` VARCHAR
- initial：1. `index` BIGINT；2. `invoice_id` VARCHAR；3. `amount` DOUBLE；4. `bundle_id` VARCHAR；5. `bundle_quantity` VARCHAR；6. `description` VARCHAR；7. `description_service_date` VARCHAR；8. `description_tax_code_id` VARCHAR；9. `discount_account_id` VARCHAR；10. `discount_class_id` VARCHAR；11. `discount_discount_percent` DOUBLE；12. `discount_percent_based` VARCHAR；13. `discount_tax_code_id` VARCHAR；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` BIGINT；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` DOUBLE；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` DOUBLE；20. `sales_item_service_date` VARCHAR；21. `sales_item_tax_code_id` BIGINT；22. `sales_item_unit_price` DOUBLE；23. `sub_total_item_id` VARCHAR；24. `item_id` VARCHAR；25. `quantity` VARCHAR；26. `tax_code_id` VARCHAR；27. `account_id` VARCHAR；28. `detail_type` VARCHAR
- agent：1. `index` BIGINT；2. `invoice_id` VARCHAR；3. `amount` DOUBLE；4. `bundle_id` INTEGER；5. `bundle_quantity` INTEGER；6. `description` VARCHAR；7. `description_service_date` INTEGER；8. `description_tax_code_id` INTEGER；9. `discount_account_id` INTEGER；10. `discount_class_id` INTEGER；11. `discount_discount_percent` DOUBLE；12. `discount_percent_based` INTEGER；13. `discount_tax_code_id` INTEGER；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` BIGINT；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` DOUBLE；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` DOUBLE；20. `sales_item_service_date` INTEGER；21. `sales_item_tax_code_id` BIGINT；22. `sales_item_unit_price` DOUBLE；23. `sub_total_item_id` INTEGER；24. `item_id` INTEGER；25. `quantity` INTEGER；26. `tax_code_id` INTEGER；27. `account_id` VARCHAR；28. `detail_type` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_quickbooks__invoice_line | 直接 | raw.invoice_line_data → staging.stg_quickbooks__invoice_line |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.item_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2000 | 2000 | True | True | 无 |
| gold_vs_agent | 2000 | 2000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `active` VARCHAR；3. `asset_account_id` VARCHAR；4. `created_at` VARCHAR；5. `description` VARCHAR；6. `expense_account_id` VARCHAR；7. `fully_qualified_name` VARCHAR；8. `income_account_id` VARCHAR；9. `inventory_start_date` VARCHAR；10. `level` VARCHAR；11. `name` VARCHAR；12. `parent_item_id` VARCHAR；13. `purchase_cost` VARCHAR；14. `purchase_description` VARCHAR；15. `purchase_tax_code_id` VARCHAR；16. `purchase_tax_included` VARCHAR；17. `quantity_on_hand` VARCHAR；18. `sales_tax_code_id` VARCHAR；19. `sales_tax_included` VARCHAR；20. `stock_keeping_unit` VARCHAR；21. `sub_item` VARCHAR；22. `sync_token` VARCHAR；23. `taxable` VARCHAR；24. `track_quantity_on_hand` VARCHAR；25. `type` VARCHAR；26. `unit_price` VARCHAR；27. `updated_at` VARCHAR
- initial：1. `id` VARCHAR；2. `active` VARCHAR；3. `asset_account_id` VARCHAR；4. `created_at` VARCHAR；5. `description` VARCHAR；6. `expense_account_id` VARCHAR；7. `fully_qualified_name` VARCHAR；8. `income_account_id` VARCHAR；9. `inventory_start_date` VARCHAR；10. `level` VARCHAR；11. `name` VARCHAR；12. `parent_item_id` VARCHAR；13. `purchase_cost` VARCHAR；14. `purchase_description` VARCHAR；15. `purchase_tax_code_id` VARCHAR；16. `purchase_tax_included` VARCHAR；17. `quantity_on_hand` VARCHAR；18. `sales_tax_code_id` VARCHAR；19. `sales_tax_included` VARCHAR；20. `stock_keeping_unit` VARCHAR；21. `sub_item` VARCHAR；22. `sync_token` VARCHAR；23. `taxable` VARCHAR；24. `track_quantity_on_hand` VARCHAR；25. `type` VARCHAR；26. `unit_price` VARCHAR；27. `updated_at` VARCHAR
- agent：1. `id` VARCHAR；2. `active` VARCHAR；3. `asset_account_id` VARCHAR；4. `created_at` VARCHAR；5. `description` VARCHAR；6. `expense_account_id` VARCHAR；7. `fully_qualified_name` VARCHAR；8. `income_account_id` VARCHAR；9. `inventory_start_date` VARCHAR；10. `level` VARCHAR；11. `name` VARCHAR；12. `parent_item_id` INTEGER；13. `purchase_cost` VARCHAR；14. `purchase_description` VARCHAR；15. `purchase_tax_code_id` VARCHAR；16. `purchase_tax_included` VARCHAR；17. `quantity_on_hand` VARCHAR；18. `sales_tax_code_id` VARCHAR；19. `sales_tax_included` VARCHAR；20. `stock_keeping_unit` VARCHAR；21. `sub_item` VARCHAR；22. `sync_token` VARCHAR；23. `taxable` VARCHAR；24. `track_quantity_on_hand` VARCHAR；25. `type` VARCHAR；26. `unit_price` VARCHAR；27. `updated_at` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | quickbooks__general_ledger | 间接 | raw.item_data → staging.stg_quickbooks__item → intermediate.int_quickbooks__bill_double_entry → marts.quickbooks__general_ledger |
| staging | stg_quickbooks__item | 直接 | raw.item_data → staging.stg_quickbooks__item |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.journal_entry_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | True | True | 无 |
| gold_vs_agent | 3000 | 3000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `adjustment` VARCHAR；3. `created_at` VARCHAR；4. `currency_id` VARCHAR；5. `doc_number` VARCHAR；6. `exchange_rate` VARCHAR；7. `home_total_amount` VARCHAR；8. `private_note` VARCHAR；9. `sync_token` VARCHAR；10. `tax_code_id` VARCHAR；11. `total_amount` VARCHAR；12. `total_tax` VARCHAR；13. `transaction_date` VARCHAR；14. `updated_at` VARCHAR
- initial：1. `id` VARCHAR；2. `adjustment` VARCHAR；3. `created_at` VARCHAR；4. `currency_id` VARCHAR；5. `doc_number` VARCHAR；6. `exchange_rate` VARCHAR；7. `home_total_amount` VARCHAR；8. `private_note` VARCHAR；9. `sync_token` VARCHAR；10. `tax_code_id` VARCHAR；11. `total_amount` VARCHAR；12. `total_tax` VARCHAR；13. `transaction_date` VARCHAR；14. `updated_at` VARCHAR
- agent：1. `id` VARCHAR；2. `adjustment` INTEGER；3. `created_at` INTEGER；4. `currency_id` VARCHAR；5. `doc_number` VARCHAR；6. `exchange_rate` VARCHAR；7. `home_total_amount` VARCHAR；8. `private_note` INTEGER；9. `sync_token` VARCHAR；10. `tax_code_id` VARCHAR；11. `total_amount` VARCHAR；12. `total_tax` VARCHAR；13. `transaction_date` VARCHAR；14. `updated_at` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | quickbooks__general_ledger | 间接 | raw.journal_entry_data → staging.stg_quickbooks__journal_entry → intermediate.int_quickbooks__journal_entry_double_entry → marts.quickbooks__general_ledger |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.journal_entry_line_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 9000 | 9000 | True | True | 无 |
| gold_vs_agent | 9000 | 9000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `index` BIGINT；2. `journal_entry_id` VARCHAR；3. `account_id` VARCHAR；4. `amount` DOUBLE；5. `billable_status` VARCHAR；6. `class_id` BIGINT；7. `customer_id` VARCHAR；8. `department_id` VARCHAR；9. `description` VARCHAR；10. `description_service_date` TIMESTAMP；11. `description_tax_code_id` BIGINT；12. `employee_id` BIGINT；13. `posting_type` VARCHAR；14. `tax_amount` DOUBLE；15. `tax_applicable_on` VARCHAR；16. `tax_code_id` BIGINT；17. `vendor_id` VARCHAR
- initial：1. `index` BIGINT；2. `journal_entry_id` VARCHAR；3. `account_id` VARCHAR；4. `amount` DOUBLE；5. `billable_status` VARCHAR；6. `class_id` BIGINT；7. `customer_id` VARCHAR；8. `department_id` VARCHAR；9. `description` VARCHAR；10. `description_service_date` TIMESTAMP；11. `description_tax_code_id` BIGINT；12. `employee_id` BIGINT；13. `posting_type` VARCHAR；14. `tax_amount` DOUBLE；15. `tax_applicable_on` VARCHAR；16. `tax_code_id` BIGINT；17. `vendor_id` VARCHAR
- agent：1. `index` BIGINT；2. `journal_entry_id` VARCHAR；3. `account_id` VARCHAR；4. `amount` DOUBLE；5. `billable_status` INTEGER；6. `class_id` BIGINT；7. `customer_id` VARCHAR；8. `department_id` VARCHAR；9. `description` VARCHAR；10. `description_service_date` TIMESTAMP；11. `description_tax_code_id` BIGINT；12. `employee_id` BIGINT；13. `posting_type` VARCHAR；14. `tax_amount` DOUBLE；15. `tax_applicable_on` INTEGER；16. `tax_code_id` BIGINT；17. `vendor_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | quickbooks__general_ledger | 间接 | raw.journal_entry_line_data → staging.stg_quickbooks__journal_entry_line → intermediate.int_quickbooks__journal_entry_double_entry → marts.quickbooks__general_ledger |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.payment_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 6000 | 6000 | True | True | 无 |
| gold_vs_agent | 6000 | 6000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `created_at` VARCHAR；3. `credit_card_amount` VARCHAR；4. `credit_card_auth_code` VARCHAR；5. `credit_card_billing_address_street` VARCHAR；6. `credit_card_cc_expiry_month` VARCHAR；7. `credit_card_cc_expiry_year` VARCHAR；8. `credit_card_cctrans_id` VARCHAR；9. `credit_card_name_on_account` VARCHAR；10. `credit_card_postal_code` VARCHAR；11. `credit_card_process_payment` VARCHAR；12. `credit_card_status` VARCHAR；13. `credit_card_transaction_authorization_time` VARCHAR；14. `credit_card_type` VARCHAR；15. `currency_id` VARCHAR；16. `customer_id` VARCHAR；17. `deposit_to_account_id` VARCHAR；18. `exchange_rate` VARCHAR；19. `payment_method_id` VARCHAR；20. `private_note` VARCHAR；21. `process_payment` VARCHAR；22. `receivable_account_id` VARCHAR；23. `reference_number` VARCHAR；24. `sync_token` VARCHAR；25. `total_amount` VARCHAR；26. `transaction_date` VARCHAR；27. `transaction_source` VARCHAR；28. `transaction_status` VARCHAR；29. `unapplied_amount` VARCHAR；30. `updated_at` VARCHAR
- initial：1. `id` VARCHAR；2. `created_at` VARCHAR；3. `credit_card_amount` VARCHAR；4. `credit_card_auth_code` VARCHAR；5. `credit_card_billing_address_street` VARCHAR；6. `credit_card_cc_expiry_month` VARCHAR；7. `credit_card_cc_expiry_year` VARCHAR；8. `credit_card_cctrans_id` VARCHAR；9. `credit_card_name_on_account` VARCHAR；10. `credit_card_postal_code` VARCHAR；11. `credit_card_process_payment` VARCHAR；12. `credit_card_status` VARCHAR；13. `credit_card_transaction_authorization_time` VARCHAR；14. `credit_card_type` VARCHAR；15. `currency_id` VARCHAR；16. `customer_id` VARCHAR；17. `deposit_to_account_id` VARCHAR；18. `exchange_rate` VARCHAR；19. `payment_method_id` VARCHAR；20. `private_note` VARCHAR；21. `process_payment` VARCHAR；22. `receivable_account_id` VARCHAR；23. `reference_number` VARCHAR；24. `sync_token` VARCHAR；25. `total_amount` VARCHAR；26. `transaction_date` VARCHAR；27. `transaction_source` VARCHAR；28. `transaction_status` VARCHAR；29. `unapplied_amount` VARCHAR；30. `updated_at` VARCHAR
- agent：1. `id` VARCHAR；2. `created_at` INTEGER；3. `credit_card_amount` VARCHAR；4. `credit_card_auth_code` INTEGER；5. `credit_card_billing_address_street` INTEGER；6. `credit_card_cc_expiry_month` INTEGER；7. `credit_card_cc_expiry_year` INTEGER；8. `credit_card_cctrans_id` VARCHAR；9. `credit_card_name_on_account` VARCHAR；10. `credit_card_postal_code` INTEGER；11. `credit_card_process_payment` INTEGER；12. `credit_card_status` INTEGER；13. `credit_card_transaction_authorization_time` INTEGER；14. `credit_card_type` INTEGER；15. `currency_id` VARCHAR；16. `customer_id` VARCHAR；17. `deposit_to_account_id` VARCHAR；18. `exchange_rate` VARCHAR；19. `payment_method_id` VARCHAR；20. `private_note` INTEGER；21. `process_payment` INTEGER；22. `receivable_account_id` VARCHAR；23. `reference_number` VARCHAR；24. `sync_token` VARCHAR；25. `total_amount` VARCHAR；26. `transaction_date` VARCHAR；27. `transaction_source` INTEGER；28. `transaction_status` INTEGER；29. `unapplied_amount` VARCHAR；30. `updated_at` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | quickbooks__general_ledger | 间接 | raw.payment_data → staging.stg_quickbooks__payment → intermediate.int_quickbooks__payment_double_entry → marts.quickbooks__general_ledger |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.purchase_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2500 | 2500 | True | True | 无 |
| gold_vs_agent | 2500 | 2500 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `account_id` VARCHAR；3. `created_at` VARCHAR；4. `credit` VARCHAR；5. `currency_id` BIGINT；6. `customer_id` VARCHAR；7. `department_id` VARCHAR；8. `doc_number` BIGINT；9. `employee_id` BIGINT；10. `exchange_rate` VARCHAR；11. `global_tax_calculation` VARCHAR；12. `payment_method_id` BIGINT；13. `payment_type` VARCHAR；14. `print_status` VARCHAR；15. `private_note` VARCHAR；16. `remit_to_address_id` VARCHAR；17. `sync_token` BIGINT；18. `tax_code_id` BIGINT；19. `total_amount` DOUBLE；20. `total_tax` DOUBLE；21. `transaction_date` TIMESTAMP；22. `transaction_source` VARCHAR；23. `updated_at` TIMESTAMP；24. `vendor_id` VARCHAR
- initial：1. `id` VARCHAR；2. `account_id` VARCHAR；3. `created_at` VARCHAR；4. `credit` VARCHAR；5. `currency_id` BIGINT；6. `customer_id` VARCHAR；7. `department_id` VARCHAR；8. `doc_number` BIGINT；9. `employee_id` BIGINT；10. `exchange_rate` VARCHAR；11. `global_tax_calculation` VARCHAR；12. `payment_method_id` BIGINT；13. `payment_type` VARCHAR；14. `print_status` VARCHAR；15. `private_note` VARCHAR；16. `remit_to_address_id` VARCHAR；17. `sync_token` BIGINT；18. `tax_code_id` BIGINT；19. `total_amount` DOUBLE；20. `total_tax` DOUBLE；21. `transaction_date` TIMESTAMP；22. `transaction_source` VARCHAR；23. `updated_at` TIMESTAMP；24. `vendor_id` VARCHAR
- agent：1. `id` VARCHAR；2. `account_id` VARCHAR；3. `created_at` INTEGER；4. `credit` INTEGER；5. `currency_id` BIGINT；6. `customer_id` VARCHAR；7. `department_id` VARCHAR；8. `doc_number` BIGINT；9. `employee_id` BIGINT；10. `exchange_rate` INTEGER；11. `global_tax_calculation` INTEGER；12. `payment_method_id` BIGINT；13. `payment_type` INTEGER；14. `print_status` INTEGER；15. `private_note` INTEGER；16. `remit_to_address_id` VARCHAR；17. `sync_token` BIGINT；18. `tax_code_id` BIGINT；19. `total_amount` DOUBLE；20. `total_tax` DOUBLE；21. `transaction_date` TIMESTAMP；22. `transaction_source` INTEGER；23. `updated_at` TIMESTAMP；24. `vendor_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.purchase_line_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 6000 | 6000 | True | True | 无 |
| gold_vs_agent | 6000 | 6000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `index` BIGINT；2. `purchase_id` BIGINT；3. `account_expense_account_id` VARCHAR；4. `account_expense_billable_status` VARCHAR；5. `account_expense_class_id` VARCHAR；6. `account_expense_customer_id` VARCHAR；7. `account_expense_tax_amount` DOUBLE；8. `account_expense_tax_code_id` VARCHAR；9. `amount` DOUBLE；10. `description` VARCHAR；11. `item_expense_billable_status` VARCHAR；12. `item_expense_class_id` VARCHAR；13. `item_expense_customer_id` VARCHAR；14. `item_expense_item_id` VARCHAR；15. `item_expense_quantity` VARCHAR；16. `item_expense_tax_code_id` VARCHAR；17. `item_expense_unit_price` VARCHAR
- initial：1. `index` BIGINT；2. `purchase_id` BIGINT；3. `account_expense_account_id` VARCHAR；4. `account_expense_billable_status` VARCHAR；5. `account_expense_class_id` VARCHAR；6. `account_expense_customer_id` VARCHAR；7. `account_expense_tax_amount` DOUBLE；8. `account_expense_tax_code_id` VARCHAR；9. `amount` DOUBLE；10. `description` VARCHAR；11. `item_expense_billable_status` VARCHAR；12. `item_expense_class_id` VARCHAR；13. `item_expense_customer_id` VARCHAR；14. `item_expense_item_id` VARCHAR；15. `item_expense_quantity` VARCHAR；16. `item_expense_tax_code_id` VARCHAR；17. `item_expense_unit_price` VARCHAR
- agent：1. `index` BIGINT；2. `purchase_id` BIGINT；3. `account_expense_account_id` VARCHAR；4. `account_expense_billable_status` INTEGER；5. `account_expense_class_id` VARCHAR；6. `account_expense_customer_id` VARCHAR；7. `account_expense_tax_amount` DOUBLE；8. `account_expense_tax_code_id` VARCHAR；9. `amount` DOUBLE；10. `description` VARCHAR；11. `item_expense_billable_status` INTEGER；12. `item_expense_class_id` VARCHAR；13. `item_expense_customer_id` VARCHAR；14. `item_expense_item_id` VARCHAR；15. `item_expense_quantity` INTEGER；16. `item_expense_tax_code_id` VARCHAR；17. `item_expense_unit_price` INTEGER

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.purchase_order_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2000 | 2000 | True | True | 无 |
| gold_vs_agent | 2000 | 2000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `class_id` BIGINT；3. `created_at` VARCHAR；4. `currency_id` BIGINT；5. `custom_customer_type` VARCHAR；6. `custom_p_o_number` BIGINT；7. `doc_number` BIGINT；8. `due_date` TIMESTAMP；9. `exchange_rate` VARCHAR；10. `global_tax_calculation` VARCHAR；11. `memo` VARCHAR；12. `payable_account_id` VARCHAR；13. `private_note` VARCHAR；14. `sales_term_id` BIGINT；15. `shipping_address_id` VARCHAR；16. `status` VARCHAR；17. `sync_token` BIGINT；18. `tax_code_id` BIGINT；19. `total_amount` DOUBLE；20. `total_tax` DOUBLE；21. `transaction_date` TIMESTAMP；22. `updated_at` TIMESTAMP；23. `vendor_address_id` VARCHAR；24. `vendor_id` VARCHAR
- initial：1. `id` VARCHAR；2. `class_id` BIGINT；3. `created_at` VARCHAR；4. `currency_id` BIGINT；5. `custom_customer_type` VARCHAR；6. `custom_p_o_number` BIGINT；7. `doc_number` BIGINT；8. `due_date` TIMESTAMP；9. `exchange_rate` VARCHAR；10. `global_tax_calculation` VARCHAR；11. `memo` VARCHAR；12. `payable_account_id` VARCHAR；13. `private_note` VARCHAR；14. `sales_term_id` BIGINT；15. `shipping_address_id` VARCHAR；16. `status` VARCHAR；17. `sync_token` BIGINT；18. `tax_code_id` BIGINT；19. `total_amount` DOUBLE；20. `total_tax` DOUBLE；21. `transaction_date` TIMESTAMP；22. `updated_at` TIMESTAMP；23. `vendor_address_id` VARCHAR；24. `vendor_id` VARCHAR
- agent：1. `id` VARCHAR；2. `class_id` BIGINT；3. `created_at` INTEGER；4. `currency_id` BIGINT；5. `custom_customer_type` INTEGER；6. `custom_p_o_number` BIGINT；7. `doc_number` BIGINT；8. `due_date` TIMESTAMP；9. `exchange_rate` INTEGER；10. `global_tax_calculation` INTEGER；11. `memo` INTEGER；12. `payable_account_id` VARCHAR；13. `private_note` INTEGER；14. `sales_term_id` BIGINT；15. `shipping_address_id` VARCHAR；16. `status` INTEGER；17. `sync_token` BIGINT；18. `tax_code_id` BIGINT；19. `total_amount` DOUBLE；20. `total_tax` DOUBLE；21. `transaction_date` TIMESTAMP；22. `updated_at` TIMESTAMP；23. `vendor_address_id` VARCHAR；24. `vendor_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.purchase_order_line_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 5000 | 5000 | True | True | 无 |
| gold_vs_agent | 5000 | 5000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `index` BIGINT；2. `purchase_order_id` BIGINT；3. `account_expense_account_id` VARCHAR；4. `account_expense_billable_status` VARCHAR；5. `account_expense_class_id` VARCHAR；6. `account_expense_customer_id` VARCHAR；7. `account_expense_tax_amount` DOUBLE；8. `account_expense_tax_code_id` VARCHAR；9. `amount` DOUBLE；10. `description` VARCHAR；11. `item_expense_billable_status` VARCHAR；12. `item_expense_class_id` VARCHAR；13. `item_expense_customer_id` VARCHAR；14. `item_expense_item_id` VARCHAR；15. `item_expense_quantity` VARCHAR；16. `item_expense_tax_code_id` VARCHAR；17. `item_expense_unit_price` VARCHAR
- initial：1. `index` BIGINT；2. `purchase_order_id` BIGINT；3. `account_expense_account_id` VARCHAR；4. `account_expense_billable_status` VARCHAR；5. `account_expense_class_id` VARCHAR；6. `account_expense_customer_id` VARCHAR；7. `account_expense_tax_amount` DOUBLE；8. `account_expense_tax_code_id` VARCHAR；9. `amount` DOUBLE；10. `description` VARCHAR；11. `item_expense_billable_status` VARCHAR；12. `item_expense_class_id` VARCHAR；13. `item_expense_customer_id` VARCHAR；14. `item_expense_item_id` VARCHAR；15. `item_expense_quantity` VARCHAR；16. `item_expense_tax_code_id` VARCHAR；17. `item_expense_unit_price` VARCHAR
- agent：1. `index` BIGINT；2. `purchase_order_id` BIGINT；3. `account_expense_account_id` VARCHAR；4. `account_expense_billable_status` INTEGER；5. `account_expense_class_id` VARCHAR；6. `account_expense_customer_id` VARCHAR；7. `account_expense_tax_amount` DOUBLE；8. `account_expense_tax_code_id` VARCHAR；9. `amount` DOUBLE；10. `description` VARCHAR；11. `item_expense_billable_status` INTEGER；12. `item_expense_class_id` VARCHAR；13. `item_expense_customer_id` VARCHAR；14. `item_expense_item_id` VARCHAR；15. `item_expense_quantity` INTEGER；16. `item_expense_tax_code_id` VARCHAR；17. `item_expense_unit_price` INTEGER

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.refund_receipt_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 800 | 800 | True | True | 无 |
| gold_vs_agent | 800 | 800 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `apply_tax_after_discount` VARCHAR；3. `balance` DOUBLE；4. `bill_email` VARCHAR；5. `billing_address_id` VARCHAR；6. `check_payment_account_number` BIGINT；7. `check_payment_bank_name` VARCHAR；8. `check_payment_check_number` BIGINT；9. `check_payment_name_on_account` VARCHAR；10. `check_payment_status` VARCHAR；11. `class_id` BIGINT；12. `created_at` VARCHAR；13. `credit_card_amount` DOUBLE；14. `credit_card_auth_code` VARCHAR；15. `credit_card_billing_address_street` VARCHAR；16. `credit_card_cc_expiry_month` VARCHAR；17. `credit_card_cc_expiry_year` VARCHAR；18. `credit_card_cctrans_id` BIGINT；19. `credit_card_name_on_account` VARCHAR；20. `credit_card_postal_code` VARCHAR；21. `credit_card_process_payment` VARCHAR；22. `credit_card_status` VARCHAR；23. `credit_card_transaction_authorization_time` VARCHAR；24. `credit_card_type` VARCHAR；25. `currency_id` BIGINT；26. `customer_id` VARCHAR；27. `customer_memo` VARCHAR；28. `department_id` VARCHAR；29. `deposit_to_account_id` VARCHAR；30. `doc_number` BIGINT；31. `exchange_rate` VARCHAR；32. `global_tax_calculation` VARCHAR；33. `home_balance` DOUBLE；34. `home_total_amount` DOUBLE；35. `payment_method_id` BIGINT；36. `payment_reference_number` BIGINT；37. `payment_type` VARCHAR；38. `print_status` VARCHAR；39. `private_note` VARCHAR；40. `shipping_address_id` VARCHAR；41. `sync_token` BIGINT；42. `tax_code_id` BIGINT；43. `total_amount` DOUBLE；44. `total_tax` DOUBLE；45. `transaction_date` TIMESTAMP；46. `transaction_source` VARCHAR；47. `updated_at` TIMESTAMP
- initial：1. `id` VARCHAR；2. `apply_tax_after_discount` VARCHAR；3. `balance` DOUBLE；4. `bill_email` VARCHAR；5. `billing_address_id` VARCHAR；6. `check_payment_account_number` BIGINT；7. `check_payment_bank_name` VARCHAR；8. `check_payment_check_number` BIGINT；9. `check_payment_name_on_account` VARCHAR；10. `check_payment_status` VARCHAR；11. `class_id` BIGINT；12. `created_at` VARCHAR；13. `credit_card_amount` DOUBLE；14. `credit_card_auth_code` VARCHAR；15. `credit_card_billing_address_street` VARCHAR；16. `credit_card_cc_expiry_month` VARCHAR；17. `credit_card_cc_expiry_year` VARCHAR；18. `credit_card_cctrans_id` BIGINT；19. `credit_card_name_on_account` VARCHAR；20. `credit_card_postal_code` VARCHAR；21. `credit_card_process_payment` VARCHAR；22. `credit_card_status` VARCHAR；23. `credit_card_transaction_authorization_time` VARCHAR；24. `credit_card_type` VARCHAR；25. `currency_id` BIGINT；26. `customer_id` VARCHAR；27. `customer_memo` VARCHAR；28. `department_id` VARCHAR；29. `deposit_to_account_id` VARCHAR；30. `doc_number` BIGINT；31. `exchange_rate` VARCHAR；32. `global_tax_calculation` VARCHAR；33. `home_balance` DOUBLE；34. `home_total_amount` DOUBLE；35. `payment_method_id` BIGINT；36. `payment_reference_number` BIGINT；37. `payment_type` VARCHAR；38. `print_status` VARCHAR；39. `private_note` VARCHAR；40. `shipping_address_id` VARCHAR；41. `sync_token` BIGINT；42. `tax_code_id` BIGINT；43. `total_amount` DOUBLE；44. `total_tax` DOUBLE；45. `transaction_date` TIMESTAMP；46. `transaction_source` VARCHAR；47. `updated_at` TIMESTAMP
- agent：1. `id` VARCHAR；2. `apply_tax_after_discount` INTEGER；3. `balance` DOUBLE；4. `bill_email` VARCHAR；5. `billing_address_id` VARCHAR；6. `check_payment_account_number` BIGINT；7. `check_payment_bank_name` VARCHAR；8. `check_payment_check_number` BIGINT；9. `check_payment_name_on_account` VARCHAR；10. `check_payment_status` INTEGER；11. `class_id` BIGINT；12. `created_at` INTEGER；13. `credit_card_amount` DOUBLE；14. `credit_card_auth_code` INTEGER；15. `credit_card_billing_address_street` INTEGER；16. `credit_card_cc_expiry_month` INTEGER；17. `credit_card_cc_expiry_year` INTEGER；18. `credit_card_cctrans_id` BIGINT；19. `credit_card_name_on_account` VARCHAR；20. `credit_card_postal_code` INTEGER；21. `credit_card_process_payment` INTEGER；22. `credit_card_status` INTEGER；23. `credit_card_transaction_authorization_time` INTEGER；24. `credit_card_type` INTEGER；25. `currency_id` BIGINT；26. `customer_id` VARCHAR；27. `customer_memo` INTEGER；28. `department_id` VARCHAR；29. `deposit_to_account_id` VARCHAR；30. `doc_number` BIGINT；31. `exchange_rate` INTEGER；32. `global_tax_calculation` INTEGER；33. `home_balance` DOUBLE；34. `home_total_amount` DOUBLE；35. `payment_method_id` BIGINT；36. `payment_reference_number` BIGINT；37. `payment_type` INTEGER；38. `print_status` INTEGER；39. `private_note` INTEGER；40. `shipping_address_id` VARCHAR；41. `sync_token` BIGINT；42. `tax_code_id` BIGINT；43. `total_amount` DOUBLE；44. `total_tax` DOUBLE；45. `transaction_date` TIMESTAMP；46. `transaction_source` INTEGER；47. `updated_at` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.refund_receipt_line_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2000 | 2000 | True | True | 无 |
| gold_vs_agent | 2000 | 2000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `index` BIGINT；2. `refund_id` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` VARCHAR；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` VARCHAR；12. `discount_percent_based` VARCHAR；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` VARCHAR；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` VARCHAR；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` VARCHAR；23. `sub_total_item_id` VARCHAR
- initial：1. `index` BIGINT；2. `refund_id` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` VARCHAR；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` VARCHAR；12. `discount_percent_based` VARCHAR；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` VARCHAR；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` VARCHAR；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` VARCHAR；23. `sub_total_item_id` VARCHAR
- agent：1. `index` BIGINT；2. `refund_id` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` INTEGER；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` INTEGER；12. `discount_percent_based` INTEGER；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` INTEGER；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` INTEGER；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` INTEGER；23. `sub_total_item_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.sales_receipt_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 4000 | 4000 | True | True | 无 |
| gold_vs_agent | 4000 | 4000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `apply_tax_after_discount` VARCHAR；3. `balance` DOUBLE；4. `bill_email` VARCHAR；5. `billing_address_id` VARCHAR；6. `class_id` BIGINT；7. `created_at` VARCHAR；8. `credit_card_amount` DOUBLE；9. `credit_card_auth_code` VARCHAR；10. `credit_card_billing_address_street` VARCHAR；11. `credit_card_cc_expiry_month` VARCHAR；12. `credit_card_cc_expiry_year` VARCHAR；13. `credit_card_cctrans_id` BIGINT；14. `credit_card_name_on_account` VARCHAR；15. `credit_card_postal_code` VARCHAR；16. `credit_card_process_payment` VARCHAR；17. `credit_card_status` VARCHAR；18. `credit_card_transaction_authorization_time` VARCHAR；19. `credit_card_type` VARCHAR；20. `currency_id` BIGINT；21. `customer_id` VARCHAR；22. `customer_memo` VARCHAR；23. `delivery_time` VARCHAR；24. `delivery_type` VARCHAR；25. `department_id` VARCHAR；26. `deposit_to_account_id` VARCHAR；27. `doc_number` BIGINT；28. `email_status` VARCHAR；29. `exchange_rate` VARCHAR；30. `global_tax_calculation` VARCHAR；31. `home_balance` DOUBLE；32. `home_total_amount` DOUBLE；33. `payment_method_id` BIGINT；34. `payment_reference_number` BIGINT；35. `print_status` VARCHAR；36. `private_note` VARCHAR；37. `ship_date` TIMESTAMP；38. `shipping_address_id` VARCHAR；39. `sync_token` BIGINT；40. `tax_code_id` BIGINT；41. `total_amount` DOUBLE；42. `total_tax` DOUBLE；43. `tracking_number` BIGINT；44. `transaction_date` TIMESTAMP；45. `transaction_source` VARCHAR；46. `updated_at` TIMESTAMP
- initial：1. `id` VARCHAR；2. `apply_tax_after_discount` VARCHAR；3. `balance` DOUBLE；4. `bill_email` VARCHAR；5. `billing_address_id` VARCHAR；6. `class_id` BIGINT；7. `created_at` VARCHAR；8. `credit_card_amount` DOUBLE；9. `credit_card_auth_code` VARCHAR；10. `credit_card_billing_address_street` VARCHAR；11. `credit_card_cc_expiry_month` VARCHAR；12. `credit_card_cc_expiry_year` VARCHAR；13. `credit_card_cctrans_id` BIGINT；14. `credit_card_name_on_account` VARCHAR；15. `credit_card_postal_code` VARCHAR；16. `credit_card_process_payment` VARCHAR；17. `credit_card_status` VARCHAR；18. `credit_card_transaction_authorization_time` VARCHAR；19. `credit_card_type` VARCHAR；20. `currency_id` BIGINT；21. `customer_id` VARCHAR；22. `customer_memo` VARCHAR；23. `delivery_time` VARCHAR；24. `delivery_type` VARCHAR；25. `department_id` VARCHAR；26. `deposit_to_account_id` VARCHAR；27. `doc_number` BIGINT；28. `email_status` VARCHAR；29. `exchange_rate` VARCHAR；30. `global_tax_calculation` VARCHAR；31. `home_balance` DOUBLE；32. `home_total_amount` DOUBLE；33. `payment_method_id` BIGINT；34. `payment_reference_number` BIGINT；35. `print_status` VARCHAR；36. `private_note` VARCHAR；37. `ship_date` TIMESTAMP；38. `shipping_address_id` VARCHAR；39. `sync_token` BIGINT；40. `tax_code_id` BIGINT；41. `total_amount` DOUBLE；42. `total_tax` DOUBLE；43. `tracking_number` BIGINT；44. `transaction_date` TIMESTAMP；45. `transaction_source` VARCHAR；46. `updated_at` TIMESTAMP
- agent：1. `id` VARCHAR；2. `apply_tax_after_discount` INTEGER；3. `balance` DOUBLE；4. `bill_email` VARCHAR；5. `billing_address_id` VARCHAR；6. `class_id` BIGINT；7. `created_at` INTEGER；8. `credit_card_amount` DOUBLE；9. `credit_card_auth_code` INTEGER；10. `credit_card_billing_address_street` INTEGER；11. `credit_card_cc_expiry_month` INTEGER；12. `credit_card_cc_expiry_year` INTEGER；13. `credit_card_cctrans_id` BIGINT；14. `credit_card_name_on_account` VARCHAR；15. `credit_card_postal_code` INTEGER；16. `credit_card_process_payment` INTEGER；17. `credit_card_status` INTEGER；18. `credit_card_transaction_authorization_time` INTEGER；19. `credit_card_type` INTEGER；20. `currency_id` BIGINT；21. `customer_id` VARCHAR；22. `customer_memo` INTEGER；23. `delivery_time` INTEGER；24. `delivery_type` INTEGER；25. `department_id` VARCHAR；26. `deposit_to_account_id` VARCHAR；27. `doc_number` BIGINT；28. `email_status` VARCHAR；29. `exchange_rate` INTEGER；30. `global_tax_calculation` INTEGER；31. `home_balance` DOUBLE；32. `home_total_amount` DOUBLE；33. `payment_method_id` BIGINT；34. `payment_reference_number` BIGINT；35. `print_status` INTEGER；36. `private_note` INTEGER；37. `ship_date` TIMESTAMP；38. `shipping_address_id` VARCHAR；39. `sync_token` BIGINT；40. `tax_code_id` BIGINT；41. `total_amount` DOUBLE；42. `total_tax` DOUBLE；43. `tracking_number` BIGINT；44. `transaction_date` TIMESTAMP；45. `transaction_source` INTEGER；46. `updated_at` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.sales_receipt_line_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 10000 | 10000 | True | True | 无 |
| gold_vs_agent | 10000 | 10000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `index` BIGINT；2. `sales_receipt_id` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` VARCHAR；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` VARCHAR；12. `discount_percent_based` VARCHAR；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` VARCHAR；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` VARCHAR；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` VARCHAR；23. `sub_total_item_id` VARCHAR
- initial：1. `index` BIGINT；2. `sales_receipt_id` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` VARCHAR；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` VARCHAR；12. `discount_percent_based` VARCHAR；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` VARCHAR；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` VARCHAR；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` VARCHAR；23. `sub_total_item_id` VARCHAR
- agent：1. `index` BIGINT；2. `sales_receipt_id` BIGINT；3. `amount` DOUBLE；4. `bundle_id` BIGINT；5. `bundle_quantity` INTEGER；6. `description` VARCHAR；7. `description_service_date` TIMESTAMP；8. `description_tax_code_id` BIGINT；9. `discount_account_id` VARCHAR；10. `discount_class_id` BIGINT；11. `discount_discount_percent` INTEGER；12. `discount_percent_based` INTEGER；13. `discount_tax_code_id` BIGINT；14. `sales_item_account_id` VARCHAR；15. `sales_item_class_id` VARCHAR；16. `sales_item_discount_amount` DOUBLE；17. `sales_item_discount_rate` INTEGER；18. `sales_item_item_id` VARCHAR；19. `sales_item_quantity` INTEGER；20. `sales_item_service_date` TIMESTAMP；21. `sales_item_tax_code_id` VARCHAR；22. `sales_item_unit_price` INTEGER；23. `sub_total_item_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.transfer_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1000 | 1000 | True | True | 无 |
| gold_vs_agent | 1000 | 1000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `amount` DOUBLE；3. `created_at` VARCHAR；4. `from_account_id` VARCHAR；5. `private_note` VARCHAR；6. `sync_token` BIGINT；7. `to_account_id` VARCHAR；8. `transaction_date` TIMESTAMP；9. `updated_at` TIMESTAMP
- initial：1. `id` VARCHAR；2. `amount` DOUBLE；3. `created_at` VARCHAR；4. `from_account_id` VARCHAR；5. `private_note` VARCHAR；6. `sync_token` BIGINT；7. `to_account_id` VARCHAR；8. `transaction_date` TIMESTAMP；9. `updated_at` TIMESTAMP
- agent：1. `id` VARCHAR；2. `amount` DOUBLE；3. `created_at` INTEGER；4. `from_account_id` VARCHAR；5. `private_note` INTEGER；6. `sync_token` BIGINT；7. `to_account_id` VARCHAR；8. `transaction_date` TIMESTAMP；9. `updated_at` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.vendor_credit_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1200 | 1200 | True | True | 无 |
| gold_vs_agent | 1200 | 1200 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `balance` DOUBLE；3. `created_at` VARCHAR；4. `currency_id` BIGINT；5. `department_id` VARCHAR；6. `doc_number` BIGINT；7. `exchange_rate` VARCHAR；8. `global_tax_calculation` VARCHAR；9. `payable_account_id` VARCHAR；10. `private_note` VARCHAR；11. `sync_token` BIGINT；12. `total_amount` DOUBLE；13. `transaction_date` TIMESTAMP；14. `updated_at` TIMESTAMP；15. `vendor_id` VARCHAR
- initial：1. `id` VARCHAR；2. `balance` DOUBLE；3. `created_at` VARCHAR；4. `currency_id` BIGINT；5. `department_id` VARCHAR；6. `doc_number` BIGINT；7. `exchange_rate` VARCHAR；8. `global_tax_calculation` VARCHAR；9. `payable_account_id` VARCHAR；10. `private_note` VARCHAR；11. `sync_token` BIGINT；12. `total_amount` DOUBLE；13. `transaction_date` TIMESTAMP；14. `updated_at` TIMESTAMP；15. `vendor_id` VARCHAR
- agent：1. `id` VARCHAR；2. `balance` DOUBLE；3. `created_at` INTEGER；4. `currency_id` BIGINT；5. `department_id` VARCHAR；6. `doc_number` BIGINT；7. `exchange_rate` INTEGER；8. `global_tax_calculation` INTEGER；9. `payable_account_id` VARCHAR；10. `private_note` INTEGER；11. `sync_token` BIGINT；12. `total_amount` DOUBLE；13. `transaction_date` TIMESTAMP；14. `updated_at` TIMESTAMP；15. `vendor_id` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.vendor_credit_line_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | True | True | 无 |
| gold_vs_agent | 3000 | 3000 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `index` BIGINT；2. `vendor_credit_id` VARCHAR；3. `account_expense_account_id` VARCHAR；4. `account_expense_billable_status` VARCHAR；5. `account_expense_class_id` VARCHAR；6. `account_expense_customer_id` VARCHAR；7. `account_expense_tax_amount` DOUBLE；8. `account_expense_tax_code_id` VARCHAR；9. `amount` DOUBLE；10. `description` VARCHAR；11. `item_expense_billable_status` VARCHAR；12. `item_expense_class_id` VARCHAR；13. `item_expense_customer_id` VARCHAR；14. `item_expense_item_id` VARCHAR；15. `item_expense_quantity` VARCHAR；16. `item_expense_tax_code_id` VARCHAR；17. `item_expense_unit_price` VARCHAR；18. `private_note` VARCHAR
- initial：1. `index` BIGINT；2. `vendor_credit_id` VARCHAR；3. `account_expense_account_id` VARCHAR；4. `account_expense_billable_status` VARCHAR；5. `account_expense_class_id` VARCHAR；6. `account_expense_customer_id` VARCHAR；7. `account_expense_tax_amount` DOUBLE；8. `account_expense_tax_code_id` VARCHAR；9. `amount` DOUBLE；10. `description` VARCHAR；11. `item_expense_billable_status` VARCHAR；12. `item_expense_class_id` VARCHAR；13. `item_expense_customer_id` VARCHAR；14. `item_expense_item_id` VARCHAR；15. `item_expense_quantity` VARCHAR；16. `item_expense_tax_code_id` VARCHAR；17. `item_expense_unit_price` VARCHAR；18. `private_note` VARCHAR
- agent：1. `index` BIGINT；2. `vendor_credit_id` VARCHAR；3. `account_expense_account_id` VARCHAR；4. `account_expense_billable_status` INTEGER；5. `account_expense_class_id` VARCHAR；6. `account_expense_customer_id` VARCHAR；7. `account_expense_tax_amount` DOUBLE；8. `account_expense_tax_code_id` VARCHAR；9. `amount` DOUBLE；10. `description` VARCHAR；11. `item_expense_billable_status` INTEGER；12. `item_expense_class_id` VARCHAR；13. `item_expense_customer_id` VARCHAR；14. `item_expense_item_id` VARCHAR；15. `item_expense_quantity` INTEGER；16. `item_expense_tax_code_id` VARCHAR；17. `item_expense_unit_price` INTEGER；18. `private_note` INTEGER

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-015 raw.vendor_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1500 | 1500 | True | True | 无 |
| gold_vs_agent | 1500 | 1500 | False | True | ordered_columns_or_types_differ |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `account_number` VARCHAR；3. `active` VARCHAR；4. `alternate_phone` VARCHAR；5. `balance` VARCHAR；6. `billing_address_id` VARCHAR；7. `company_name` VARCHAR；8. `created_at` VARCHAR；9. `currency_id` VARCHAR；10. `display_name` VARCHAR；11. `email` VARCHAR；12. `family_name` VARCHAR；13. `fax_number` VARCHAR；14. `given_name` VARCHAR；15. `middle_name` VARCHAR；16. `mobile_phone` VARCHAR；17. `other_contacts` VARCHAR；18. `primary_phone` VARCHAR；19. `print_on_check_name` VARCHAR；20. `suffix` VARCHAR；21. `sync_token` VARCHAR；22. `tax_identifier` VARCHAR；23. `term_id` VARCHAR；24. `title` VARCHAR；25. `updated_at` VARCHAR；26. `vendor_1099` VARCHAR；27. `web_url` VARCHAR
- initial：1. `id` VARCHAR；2. `account_number` VARCHAR；3. `active` VARCHAR；4. `alternate_phone` VARCHAR；5. `balance` VARCHAR；6. `billing_address_id` VARCHAR；7. `company_name` VARCHAR；8. `created_at` VARCHAR；9. `currency_id` VARCHAR；10. `display_name` VARCHAR；11. `email` VARCHAR；12. `family_name` VARCHAR；13. `fax_number` VARCHAR；14. `given_name` VARCHAR；15. `middle_name` VARCHAR；16. `mobile_phone` VARCHAR；17. `other_contacts` VARCHAR；18. `primary_phone` VARCHAR；19. `print_on_check_name` VARCHAR；20. `suffix` VARCHAR；21. `sync_token` VARCHAR；22. `tax_identifier` VARCHAR；23. `term_id` VARCHAR；24. `title` VARCHAR；25. `updated_at` VARCHAR；26. `vendor_1099` VARCHAR；27. `web_url` VARCHAR
- agent：1. `id` VARCHAR；2. `account_number` VARCHAR；3. `active` VARCHAR；4. `alternate_phone` VARCHAR；5. `balance` VARCHAR；6. `billing_address_id` VARCHAR；7. `company_name` VARCHAR；8. `created_at` VARCHAR；9. `currency_id` VARCHAR；10. `display_name` VARCHAR；11. `email` VARCHAR；12. `family_name` VARCHAR；13. `fax_number` VARCHAR；14. `given_name` VARCHAR；15. `middle_name` INTEGER；16. `mobile_phone` VARCHAR；17. `other_contacts` INTEGER；18. `primary_phone` VARCHAR；19. `print_on_check_name` VARCHAR；20. `suffix` INTEGER；21. `sync_token` VARCHAR；22. `tax_identifier` VARCHAR；23. `term_id` VARCHAR；24. `title` INTEGER；25. `updated_at` VARCHAR；26. `vendor_1099` VARCHAR；27. `web_url` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_quickbooks__vendor | 直接 | raw.vendor_data → staging.stg_quickbooks__vendor |

来源：`015_raw_impl-015.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-016 raw.person_contact_email_address

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 7284 | 7284 | True | True | 无 |
| gold_vs_agent | 7284 | 2448 | True | 未比较 | row_counts_differ |

**按原顺序的列名与类型**

- gold：1. `email_id` VARCHAR；2. `person_id` VARCHAR；3. `email_address` VARCHAR；4. `email_code` VARCHAR；5. `email_comment` VARCHAR
- initial：1. `email_id` VARCHAR；2. `person_id` VARCHAR；3. `email_address` VARCHAR；4. `email_code` VARCHAR；5. `email_comment` VARCHAR
- agent：1. `email_id` VARCHAR；2. `person_id` VARCHAR；3. `email_address` VARCHAR；4. `email_code` VARCHAR；5. `email_comment` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | workday__employee_overview | 间接 | raw.person_contact_email_address → staging.stg_workday__person_contact_email_address → intermediate.int_workday__personal_details → intermediate.int_workday__worker_employee_enhanced → marts.workday__employee_overview |
| marts | workday__organization_overview | 间接 | raw.person_contact_email_address → staging.stg_workday__person_contact_email_address → intermediate.int_workday__personal_details → intermediate.int_workday__worker_employee_enhanced → marts.workday__employee_overview → marts.workday__organization_overview |
| marts | workday__position_overview | 间接 | raw.person_contact_email_address → staging.stg_workday__person_contact_email_address → intermediate.int_workday__personal_details → intermediate.int_workday__worker_employee_enhanced → marts.workday__employee_overview → marts.workday__position_overview |

来源：`015_raw_impl-016.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-017 raw.scheduled_interview_snowflake

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2000 | 2000 | False | True | ordered_columns_or_types_differ |
| gold_vs_agent | 2000 | 2000 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` BIGINT；2. `application_id` BIGINT；3. `interview_id` BIGINT；4. `organizer_id` BIGINT；5. `end` TIMESTAMP；6. `location` VARCHAR；7. `status` VARCHAR；8. `created_at` TIMESTAMP；9. `updated_at` TIMESTAMP；10. `START` TIMESTAMP
- initial：1. `id` BIGINT；2. `application_id` BIGINT；3. `interview_id` BIGINT；4. `organizer_id` BIGINT；5. `end` TIMESTAMP；6. `location` VARCHAR；7. `status` VARCHAR；8. `created_at` TIMESTAMP；9. `updated_at` TIMESTAMP；10. `"START"` TIMESTAMP
- agent：1. `id` BIGINT；2. `application_id` BIGINT；3. `interview_id` BIGINT；4. `organizer_id` BIGINT；5. `end` TIMESTAMP；6. `location` VARCHAR；7. `status` VARCHAR；8. `created_at` TIMESTAMP；9. `updated_at` TIMESTAMP；10. `START` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-017.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-019 raw.app_crash_daily

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 3000 | 3000 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `_fivetran_id` VARCHAR；2. `app_id` BIGINT；3. `date` DATE；4. `app_version` VARCHAR；5. `device` VARCHAR；6. `platform_version` VARCHAR；7. `crashes` BIGINT；8. `unique_devices` BIGINT；9. `_fivetran_synced` VARCHAR
- initial：1. `_fivetran_id` VARCHAR；2. `_fivetran_synced` TIMESTAMP；3. `app_id` BIGINT；4. `app_version` VARCHAR；5. `crashes` BIGINT；6. `date` DATE；7. `device` VARCHAR；8. `platform_version` VARCHAR；9. `unique_devices` BIGINT
- agent：1. `_fivetran_id` VARCHAR；2. `app_id` BIGINT；3. `date` DATE；4. `app_version` VARCHAR；5. `device` VARCHAR；6. `platform_version` VARCHAR；7. `crashes` BIGINT；8. `unique_devices` BIGINT；9. `_fivetran_synced` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | apple_store__app_version_report | 间接 | raw.app_crash_daily → staging.stg_apple_store__app_crash_daily → intermediate.int_apple_store__app_version_app_crashes → marts.apple_store__app_version_report |

来源：`015_raw_impl-019.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-019 raw.app_session_standard_daily

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 3000 | 3000 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `_fivetran_id` VARCHAR；2. `app_id` BIGINT；3. `date` VARCHAR；4. `app_version` VARCHAR；5. `device` VARCHAR；6. `platform_version` VARCHAR；7. `source_type` VARCHAR；8. `page_type` VARCHAR；9. `app_downloa1d_date` VARCHAR；10. `territory` VARCHAR；11. `sessions` BIGINT；12. `total_session_duration` BIGINT；13. `unique_devices` BIGINT；14. `_fivetran_synced` VARCHAR
- initial：1. `_fivetran_id` VARCHAR；2. `_fivetran_synced` TIMESTAMP；3. `app_download_date` DATE；4. `app_id` BIGINT；5. `app_version` VARCHAR；6. `date` DATE；7. `device` VARCHAR；8. `page_type` VARCHAR；9. `platform_version` VARCHAR；10. `sessions` BIGINT；11. `source_type` VARCHAR；12. `territory` VARCHAR；13. `total_session_duration` BIGINT；14. `unique_devices` BIGINT
- agent：1. `_fivetran_id` VARCHAR；2. `app_id` BIGINT；3. `date` VARCHAR；4. `app_version` VARCHAR；5. `device` VARCHAR；6. `platform_version` VARCHAR；7. `source_type` VARCHAR；8. `page_type` VARCHAR；9. `app_downloa1d_date` VARCHAR；10. `territory` VARCHAR；11. `sessions` BIGINT；12. `total_session_duration` BIGINT；13. `unique_devices` BIGINT；14. `_fivetran_synced` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | apple_store__app_version_report | 间接 | raw.app_session_standard_daily → staging.stg_apple_store__app_session_daily → intermediate.int_apple_store__app_version_report → marts.apple_store__app_version_report |
| marts | apple_store__territory_report | 间接 | raw.app_session_standard_daily → staging.stg_apple_store__app_session_daily → intermediate.int_apple_store__territory_report → marts.apple_store__territory_report |
| staging | stg_apple_store__app_session_daily | 直接 | raw.app_session_standard_daily → staging.stg_apple_store__app_session_daily |

来源：`015_raw_impl-019.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-019 raw.app_store_app

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 300 | 300 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 300 | 300 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` BIGINT；2. `name` VARCHAR；3. `primary_locale` VARCHAR；4. `content_rights_declaration` VARCHAR；5. `was_made_for_kids` BOOLEAN；6. `subscription_status_url` VARCHAR；7. `subscription_status_url_version` VARCHAR；8. `subscription_status_url_for_sandbox` VARCHAR；9. `subscription_status_url_version_for_sandbox` VARCHAR；10. `_fivetran_synced` TIMESTAMP WITH TIME ZONE
- initial：1. `_fivetran_synced` TIMESTAMP；2. `content_rights_declaration` VARCHAR；3. `id` BIGINT；4. `name` VARCHAR；5. `primary_locale` VARCHAR；6. `subscription_status_url` VARCHAR；7. `subscription_status_url_for_sandbox` VARCHAR；8. `subscription_status_url_version` VARCHAR；9. `subscription_status_url_version_for_sandbox` VARCHAR；10. `was_made_for_kids` VARCHAR
- agent：1. `id` BIGINT；2. `name` VARCHAR；3. `primary_locale` VARCHAR；4. `content_rights_declaration` VARCHAR；5. `was_made_for_kids` BOOLEAN；6. `subscription_status_url` VARCHAR；7. `subscription_status_url_version` VARCHAR；8. `subscription_status_url_for_sandbox` VARCHAR；9. `subscription_status_url_version_for_sandbox` VARCHAR；10. `_fivetran_synced` TIMESTAMP WITH TIME ZONE

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | apple_store__app_version_report | 间接 | raw.app_store_app → staging.stg_apple_store__app_store_app → intermediate.int_apple_store__app_dim → marts.apple_store__app_version_report |
| marts | apple_store__territory_report | 间接 | raw.app_store_app → staging.stg_apple_store__app_store_app → intermediate.int_apple_store__app_dim → marts.apple_store__territory_report |

来源：`015_raw_impl-019.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-019 raw.app_store_discovery_and_engagement_standard_daily

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 3000 | 3000 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `_fivetran_id` VARCHAR；2. `app_id` BIGINT；3. `date` DATE；4. `event` VARCHAR；5. `page_type` VARCHAR；6. `source_type` VARCHAR；7. `engagement_type` VARCHAR；8. `device` VARCHAR；9. `platform_version` VARCHAR；10. `territory` VARCHAR；11. `counts` BIGINT；12. `unique_counts` BIGINT；13. `_fivetran_synced` VARCHAR
- initial：1. `_fivetran_id` VARCHAR；2. `_fivetran_synced` TIMESTAMP；3. `app_id` BIGINT；4. `counts` BIGINT；5. `date` DATE；6. `device` VARCHAR；7. `engagement_type` VARCHAR；8. `event` VARCHAR；9. `page_type` VARCHAR；10. `platform_version` VARCHAR；11. `source_type` VARCHAR；12. `territory` VARCHAR；13. `unique_counts` BIGINT
- agent：1. `_fivetran_id` VARCHAR；2. `app_id` BIGINT；3. `date` DATE；4. `event` VARCHAR；5. `page_type` VARCHAR；6. `source_type` VARCHAR；7. `engagement_type` VARCHAR；8. `device` VARCHAR；9. `platform_version` VARCHAR；10. `territory` VARCHAR；11. `counts` BIGINT；12. `unique_counts` BIGINT；13. `_fivetran_synced` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | apple_store__territory_report | 间接 | raw.app_store_discovery_and_engagement_standard_daily → staging.stg_apple_store__app_store_discovery_and_engagement_daily → intermediate.int_apple_store__territory_impressions_page_views → marts.apple_store__territory_report |

来源：`015_raw_impl-019.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-019 raw.app_store_download_standard_daily

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 3000 | 3000 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `_fivetran_id` VARCHAR；2. `app_id` BIGINT；3. `date` VARCHAR；4. `download_type` VARCHAR；5. `app_version` VARCHAR；6. `device` VARCHAR；7. `platform_version` VARCHAR；8. `source_type` VARCHAR；9. `page_type` VARCHAR；10. `pre_order` BOOLEAN；11. `territory` VARCHAR；12. `counts` BIGINT；13. `_fivetran_synced` VARCHAR
- initial：1. `_fivetran_id` VARCHAR；2. `_fivetran_synced` TIMESTAMP；3. `app_id` BIGINT；4. `app_version` VARCHAR；5. `counts` BIGINT；6. `date` DATE；7. `device` VARCHAR；8. `download_type` VARCHAR；9. `page_type` VARCHAR；10. `platform_version` VARCHAR；11. `pre_order` VARCHAR；12. `source_type` VARCHAR；13. `territory` VARCHAR
- agent：1. `_fivetran_id` VARCHAR；2. `app_id` BIGINT；3. `date` VARCHAR；4. `download_type` VARCHAR；5. `app_version` VARCHAR；6. `device` VARCHAR；7. `platform_version` VARCHAR；8. `source_type` VARCHAR；9. `page_type` VARCHAR；10. `pre_order` BOOLEAN；11. `territory` VARCHAR；12. `counts` BIGINT；13. `_fivetran_synced` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | apple_store__territory_report | 间接 | raw.app_store_download_standard_daily → staging.stg_apple_store__app_store_download_daily → intermediate.int_apple_store__territory_downloads_daily → marts.apple_store__territory_report |

来源：`015_raw_impl-019.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-019 raw.app_store_installation_and_deletion_standard_daily

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 3000 | 3000 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `_fivetran_id` VARCHAR；2. `app_id` BIGINT；3. `date` DATE；4. `event` VARCHAR；5. `download_type` VARCHAR；6. `app_version` DOUBLE；7. `device` VARCHAR；8. `platform_version` VARCHAR；9. `source_type` VARCHAR；10. `page_type` VARCHAR；11. `app_download_date` DATE；12. `territory` VARCHAR；13. `counts` BIGINT；14. `unique_devices` BIGINT；15. `_fivetran_synced` VARCHAR
- initial：1. `_fivetran_id` VARCHAR；2. `_fivetran_synced` TIMESTAMP；3. `app_download_date` DATE；4. `app_id` BIGINT；5. `app_version` VARCHAR；6. `counts` BIGINT；7. `date` DATE；8. `device` VARCHAR；9. `download_type` VARCHAR；10. `event` VARCHAR；11. `page_type` VARCHAR；12. `platform_version` VARCHAR；13. `source_type` VARCHAR；14. `territory` VARCHAR；15. `unique_devices` BIGINT
- agent：1. `_fivetran_id` VARCHAR；2. `app_id` BIGINT；3. `date` DATE；4. `event` VARCHAR；5. `download_type` VARCHAR；6. `app_version` DOUBLE；7. `device` VARCHAR；8. `platform_version` VARCHAR；9. `source_type` VARCHAR；10. `page_type` VARCHAR；11. `app_download_date` DATE；12. `territory` VARCHAR；13. `counts` BIGINT；14. `unique_devices` BIGINT；15. `_fivetran_synced` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | apple_store__app_version_report | 间接 | raw.app_store_installation_and_deletion_standard_daily → staging.stg_apple_store__app_store_installation_and_deletion_daily → intermediate.int_apple_store__app_version_install_deletions → marts.apple_store__app_version_report |
| marts | apple_store__territory_report | 间接 | raw.app_store_installation_and_deletion_standard_daily → staging.stg_apple_store__app_store_installation_and_deletion_daily → intermediate.int_apple_store__territory_install_deletions → marts.apple_store__territory_report |

来源：`015_raw_impl-019.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-019 raw.apple_store_country_codes

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 250 | 表不存在 | 未比较 | 未比较 | initial_missing_table |
| gold_vs_agent | 250 | 250 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `country_name` VARCHAR；2. `alternative_country_name` VARCHAR；3. `country_code_numeric` BIGINT；4. `country_code_alpha_2` VARCHAR；5. `country_code_alpha_3` VARCHAR；6. `region` VARCHAR；7. `region_code` VARCHAR；8. `sub_region` VARCHAR；9. `sub_region_code` VARCHAR
- initial：表不存在
- agent：1. `country_name` VARCHAR；2. `alternative_country_name` VARCHAR；3. `country_code_numeric` BIGINT；4. `country_code_alpha_2` VARCHAR；5. `country_code_alpha_3` VARCHAR；6. `region` VARCHAR；7. `region_code` VARCHAR；8. `sub_region` VARCHAR；9. `sub_region_code` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | apple_store__subscription_report | 间接 | raw.apple_store_country_codes → staging.stg_apple_store__country_codes → intermediate.int_apple_store__country_codes → marts.apple_store__subscription_report |
| marts | apple_store__territory_report | 间接 | raw.apple_store_country_codes → staging.stg_apple_store__country_codes → intermediate.int_apple_store__country_codes → marts.apple_store__territory_report |

来源：`015_raw_impl-019.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-019 raw.sales_subscription_event_summary

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 3000 | 3000 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `_fivetran_id` VARCHAR；2. `vendor_number` BIGINT；3. `event_date` VARCHAR；4. `event` VARCHAR；5. `app_name` VARCHAR；6. `app_apple_id` BIGINT；7. `subscription_name` VARCHAR；8. `subscription_apple_id` BIGINT；9. `subscription_group_id` BIGINT；10. `standard_subscription_duration` VARCHAR；11. `subscription_offer_type` VARCHAR；12. `subscription_offer_duration` VARCHAR；13. `marketing_opt_in` BOOLEAN；14. `marketing_opt_in_duration` VARCHAR；15. `preserved_pricing` BOOLEAN；16. `proceeds_reason` VARCHAR；17. `promotional_offer_name` VARCHAR；18. `promotional_offer_id` VARCHAR；19. `consecutive_paid_periods` BIGINT；20. `original_start_date` VARCHAR；21. `device` VARCHAR；22. `client` VARCHAR；23. `state` VARCHAR；24. `country` VARCHAR；25. `previous_subscription_name` VARCHAR；26. `previous_subscription_apple_id` BIGINT；27. `days_before_canceling` BIGINT；28. `cancellation_reason` VARCHAR；29. `days_canceled` BIGINT；30. `quantity` BIGINT；31. `paid_service_days_recovered` BIGINT；32. `_fivetran_synced` VARCHAR
- initial：1. `_fivetran_id` VARCHAR；2. `_fivetran_synced` TIMESTAMP；3. `app_apple_id` BIGINT；4. `app_name` VARCHAR；5. `cancellation_reason` VARCHAR；6. `client` VARCHAR；7. `consecutive_paid_periods` BIGINT；8. `country` VARCHAR；9. `days_before_canceling` BIGINT；10. `days_canceled` BIGINT；11. `device` VARCHAR；12. `event` VARCHAR；13. `event_date` DATE；14. `marketing_opt_in` BOOLEAN；15. `marketing_opt_in_duration` VARCHAR；16. `original_start_date` DATE；17. `paid_service_days_recovered` BIGINT；18. `preserved_pricing` BOOLEAN；19. `previous_subscription_apple_id` BIGINT；20. `previous_subscription_name` VARCHAR；21. `proceeds_reason` VARCHAR；22. `promotional_offer_id` VARCHAR；23. `promotional_offer_name` VARCHAR；24. `quantity` BIGINT；25. `standard_subscription_duration` VARCHAR；26. `state` VARCHAR；27. `subscription_apple_id` BIGINT；28. `subscription_group_id` BIGINT；29. `subscription_name` VARCHAR；30. `subscription_offer_duration` VARCHAR；31. `subscription_offer_type` VARCHAR；32. `vendor_number` BIGINT
- agent：1. `_fivetran_id` VARCHAR；2. `vendor_number` BIGINT；3. `event_date` VARCHAR；4. `event` VARCHAR；5. `app_name` VARCHAR；6. `app_apple_id` BIGINT；7. `subscription_name` VARCHAR；8. `subscription_apple_id` BIGINT；9. `subscription_group_id` BIGINT；10. `standard_subscription_duration` VARCHAR；11. `subscription_offer_type` VARCHAR；12. `subscription_offer_duration` VARCHAR；13. `marketing_opt_in` BOOLEAN；14. `marketing_opt_in_duration` VARCHAR；15. `preserved_pricing` BOOLEAN；16. `proceeds_reason` VARCHAR；17. `promotional_offer_name` VARCHAR；18. `promotional_offer_id` VARCHAR；19. `consecutive_paid_periods` BIGINT；20. `original_start_date` VARCHAR；21. `device` VARCHAR；22. `client` VARCHAR；23. `state` VARCHAR；24. `country` VARCHAR；25. `previous_subscription_name` VARCHAR；26. `previous_subscription_apple_id` BIGINT；27. `days_before_canceling` BIGINT；28. `cancellation_reason` VARCHAR；29. `days_canceled` BIGINT；30. `quantity` BIGINT；31. `paid_service_days_recovered` BIGINT；32. `_fivetran_synced` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | apple_store__subscription_report | 间接 | raw.sales_subscription_event_summary → staging.stg_apple_store__sales_subscription_events → intermediate.int_apple_store__subscription_events → marts.apple_store__subscription_report |

来源：`015_raw_impl-019.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-019 raw.sales_subscription_summary

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3000 | 3000 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 3000 | 3000 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `_fivetran_id` VARCHAR；2. `vendor_number` BIGINT；3. `app_name` VARCHAR；4. `app_apple_id` BIGINT；5. `subscription_name` VARCHAR；6. `subscription_apple_id` BIGINT；7. `subscription_group_id` BIGINT；8. `standard_subscription_duration` VARCHAR；9. `customer_price` DOUBLE；10. `customer_currency` VARCHAR；11. `developer_proceeds` DOUBLE；12. `proceeds_currency` VARCHAR；13. `preserved_pricing` BOOLEAN；14. `proceeds_reason` VARCHAR；15. `subscription_offer_name` VARCHAR；16. `promotional_offer_id` VARCHAR；17. `state` VARCHAR；18. `country` VARCHAR；19. `device` VARCHAR；20. `client` VARCHAR；21. `active_standard_price_subscriptions` BIGINT；22. `active_free_trial_introductory_offer_subscriptions` BIGINT；23. `active_pay_up_front_introductory_offer_subscriptions` BIGINT；24. `active_pay_as_you_go_introductory_offer_subscriptions` BIGINT；25. `free_trial_promotional_offer_subscriptions` BIGINT；26. `pay_up_front_promotional_offer_subscriptions` BIGINT；27. `pay_as_you_go_promotional_offer_subscriptions` BIGINT；28. `marketing_opt_ins` BIGINT；29. `billing_retry` BIGINT；30. `grace_period` BIGINT；31. `free_trial_offer_code_subscriptions` BIGINT；32. `pay_up_front_offer_code_subscriptions` BIGINT；33. `pay_as_you_go_offer_code_subscriptions` BIGINT；34. `subscribers` BIGINT；35. `_fivetran_synced` VARCHAR；36. `date` VARCHAR
- initial：1. `_fivetran_id` VARCHAR；2. `_fivetran_synced` TIMESTAMP；3. `active_free_trial_introductory_offer_subscriptions` BIGINT；4. `active_pay_as_you_go_introductory_offer_subscriptions` BIGINT；5. `active_pay_up_front_introductory_offer_subscriptions` BIGINT；6. `active_standard_price_subscriptions` BIGINT；7. `app_apple_id` BIGINT；8. `app_name` VARCHAR；9. `billing_retry` BIGINT；10. `client` VARCHAR；11. `country` VARCHAR；12. `customer_currency` VARCHAR；13. `customer_price` DECIMAL(18,2)；14. `date` DATE；15. `developer_proceeds` DECIMAL(18,2)；16. `device` VARCHAR；17. `free_trial_offer_code_subscriptions` BIGINT；18. `free_trial_promotional_offer_subscriptions` BIGINT；19. `grace_period` BIGINT；20. `marketing_opt_ins` BIGINT；21. `pay_as_you_go_offer_code_subscriptions` BIGINT；22. `pay_as_you_go_promotional_offer_subscriptions` BIGINT；23. `pay_up_front_offer_code_subscriptions` BIGINT；24. `pay_up_front_promotional_offer_subscriptions` BIGINT；25. `preserved_pricing` BOOLEAN；26. `proceeds_currency` VARCHAR；27. `proceeds_reason` VARCHAR；28. `promotional_offer_id` VARCHAR；29. `standard_subscription_duration` VARCHAR；30. `state` VARCHAR；31. `subscribers` BIGINT；32. `subscription_apple_id` BIGINT；33. `subscription_group_id` BIGINT；34. `subscription_name` VARCHAR；35. `subscription_offer_name` VARCHAR；36. `vendor_number` BIGINT
- agent：1. `_fivetran_id` VARCHAR；2. `vendor_number` BIGINT；3. `app_name` VARCHAR；4. `app_apple_id` BIGINT；5. `subscription_name` VARCHAR；6. `subscription_apple_id` BIGINT；7. `subscription_group_id` BIGINT；8. `standard_subscription_duration` VARCHAR；9. `customer_price` DOUBLE；10. `customer_currency` VARCHAR；11. `developer_proceeds` DOUBLE；12. `proceeds_currency` VARCHAR；13. `preserved_pricing` BOOLEAN；14. `proceeds_reason` VARCHAR；15. `subscription_offer_name` VARCHAR；16. `promotional_offer_id` VARCHAR；17. `state` VARCHAR；18. `country` VARCHAR；19. `device` VARCHAR；20. `client` VARCHAR；21. `active_standard_price_subscriptions` BIGINT；22. `active_free_trial_introductory_offer_subscriptions` BIGINT；23. `active_pay_up_front_introductory_offer_subscriptions` BIGINT；24. `active_pay_as_you_go_introductory_offer_subscriptions` BIGINT；25. `free_trial_promotional_offer_subscriptions` BIGINT；26. `pay_up_front_promotional_offer_subscriptions` BIGINT；27. `pay_as_you_go_promotional_offer_subscriptions` BIGINT；28. `marketing_opt_ins` BIGINT；29. `billing_retry` BIGINT；30. `grace_period` BIGINT；31. `free_trial_offer_code_subscriptions` BIGINT；32. `pay_up_front_offer_code_subscriptions` BIGINT；33. `pay_as_you_go_offer_code_subscriptions` BIGINT；34. `subscribers` BIGINT；35. `_fivetran_synced` VARCHAR；36. `date` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | apple_store__subscription_report | 间接 | raw.sales_subscription_summary → staging.stg_apple_store__sales_subscription_summary → intermediate.int_apple_store__subscription_report → marts.apple_store__subscription_report |

来源：`015_raw_impl-019.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.admin_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3004 | 3004 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 3004 | 3004 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `job_title` VARCHAR；5. `email` VARCHAR；6. `name` VARCHAR
- initial：1. `id` BIGINT；2. `_fivetran_deleted` BOOLEAN；3. `_fivetran_synced` TIMESTAMP；4. `job_title` VARCHAR；5. `email` VARCHAR；6. `name` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `job_title` VARCHAR；5. `email` VARCHAR；6. `name` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.company_history_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2509 | 2509 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 2509 | 2509 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `updated_at` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `company_id` VARCHAR；5. `created_at` VARCHAR；6. `industry` VARCHAR；7. `last_request_at` VARCHAR；8. `monthly_spend` VARCHAR；9. `plan_id` VARCHAR；10. `plan_name` VARCHAR；11. `remote_created_at` VARCHAR；12. `session_count` VARCHAR；13. `size` VARCHAR；14. `user_count` VARCHAR；15. `website` VARCHAR；16. `name` VARCHAR；17. `_fivetran_active` VARCHAR；18. `_fivetran_start` VARCHAR；19. `_fivetran_end` VARCHAR
- initial：1. `id` VARCHAR；2. `updated_at` TIMESTAMP；3. `_fivetran_synced` TIMESTAMP；4. `company_id` VARCHAR；5. `created_at` TIMESTAMP；6. `industry` VARCHAR；7. `last_request_at` TIMESTAMP；8. `monthly_spend` BIGINT；9. `plan_id` VARCHAR；10. `plan_name` VARCHAR；11. `remote_created_at` TIMESTAMP；12. `session_count` BIGINT；13. `size` VARCHAR；14. `user_count` BIGINT；15. `website` VARCHAR；16. `name` VARCHAR；17. `_fivetran_active` BOOLEAN；18. `_fivetran_start` TIMESTAMP；19. `_fivetran_end` TIMESTAMP
- agent：1. `id` VARCHAR；2. `updated_at` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `company_id` VARCHAR；5. `created_at` VARCHAR；6. `industry` VARCHAR；7. `last_request_at` VARCHAR；8. `monthly_spend` VARCHAR；9. `plan_id` VARCHAR；10. `plan_name` VARCHAR；11. `remote_created_at` VARCHAR；12. `session_count` VARCHAR；13. `size` VARCHAR；14. `user_count` VARCHAR；15. `website` VARCHAR；16. `name` VARCHAR；17. `_fivetran_active` VARCHAR；18. `_fivetran_start` VARCHAR；19. `_fivetran_end` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | intercom__company_metrics | 间接 | raw.company_history_data → staging.stg_intercom__company_history → intermediate.int_intercom__company_history → marts.intercom__company_metrics |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.company_tag_history_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2431 | 2431 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 2431 | 2431 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `company_id` VARCHAR；2. `company_updated_at` VARCHAR；3. `tag_id` VARCHAR；4. `_fivetran_active` VARCHAR；5. `_fivetran_synced` VARCHAR；6. `_fivetran_start` VARCHAR；7. `_fivetran_end` VARCHAR
- initial：1. `company_id` VARCHAR；2. `company_updated_at` TIMESTAMP；3. `tag_id` BIGINT；4. `_fivetran_active` BOOLEAN；5. `_fivetran_synced` TIMESTAMP；6. `_fivetran_start` TIMESTAMP；7. `_fivetran_end` TIMESTAMP
- agent：1. `company_id` VARCHAR；2. `company_updated_at` VARCHAR；3. `tag_id` VARCHAR；4. `_fivetran_active` VARCHAR；5. `_fivetran_synced` VARCHAR；6. `_fivetran_start` VARCHAR；7. `_fivetran_end` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.contact_company_history_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1473 | 1473 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 1473 | 1473 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `contact_id` VARCHAR；2. `company_id` VARCHAR；3. `_fivetran_active` VARCHAR；4. `_fivetran_synced` VARCHAR；5. `_fivetran_start` VARCHAR；6. `_fivetran_end` VARCHAR
- initial：1. `contact_id` VARCHAR；2. `company_id` VARCHAR；3. `company_updated_at` TIMESTAMP；4. `_fivetran_active` BOOLEAN；5. `_fivetran_synced` TIMESTAMP；6. `_fivetran_start` TIMESTAMP；7. `_fivetran_end` TIMESTAMP
- agent：1. `contact_id` VARCHAR；2. `company_id` VARCHAR；3. `_fivetran_active` VARCHAR；4. `_fivetran_synced` VARCHAR；5. `_fivetran_start` VARCHAR；6. `_fivetran_end` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | intercom__company_metrics | 间接 | raw.contact_company_history_data → staging.stg_intercom__contact_company_history → intermediate.int_intercom__contact_company_history → marts.intercom__company_metrics |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.contact_history_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 3009 | 3009 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 3009 | 3009 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `updated_at` VARCHAR；3. `_fivetran_active` VARCHAR；4. `_fivetran_synced` VARCHAR；5. `admin_id` VARCHAR；6. `android_app_name` VARCHAR；7. `android_app_version` VARCHAR；8. `android_device` VARCHAR；9. `android_last_seen_at` VARCHAR；10. `android_os_version` VARCHAR；11. `android_sdk_version` VARCHAR；12. `browser` VARCHAR；13. `browser_language` VARCHAR；14. `browser_version` VARCHAR；15. `created_at` VARCHAR；16. `custom_onboarding_step` VARCHAR；17. `custom_organisation_id` VARCHAR；18. `custom_organisation_name` VARCHAR；19. `external_id` VARCHAR；20. `has_hard_bounced` VARCHAR；21. `ios_app_name` VARCHAR；22. `ios_app_version` VARCHAR；23. `ios_device` VARCHAR；24. `ios_last_seen_at` VARCHAR；25. `ios_os_version` VARCHAR；26. `ios_sdk_version` VARCHAR；27. `language_override` VARCHAR；28. `last_contacted_at` VARCHAR；29. `last_email_clicked_at` VARCHAR；30. `last_email_opened_at` VARCHAR；31. `last_replied_at` VARCHAR；32. `last_seen_at` VARCHAR；33. `location_city` VARCHAR；34. `location_country` VARCHAR；35. `location_region` VARCHAR；36. `marked_email_as_spam` VARCHAR；37. `os` VARCHAR；38. `phone` VARCHAR；39. `role` VARCHAR；40. `signed_up_at` VARCHAR；41. `unsubscribed_from_emails` VARCHAR；42. `workspace_id` VARCHAR；43. `avatar` VARCHAR；44. `custom_job_title` VARCHAR；45. `email` VARCHAR；46. `name` VARCHAR；47. `_fivetran_start` VARCHAR；48. `_fivetran_end` VARCHAR
- initial：1. `id` VARCHAR；2. `updated_at` TIMESTAMP；3. `_fivetran_active` BOOLEAN；4. `_fivetran_synced` TIMESTAMP；5. `admin_id` BIGINT；6. `android_app_name` VARCHAR；7. `android_app_version` VARCHAR；8. `android_device` VARCHAR；9. `android_last_seen_at` VARCHAR；10. `android_os_version` VARCHAR；11. `android_sdk_version` VARCHAR；12. `browser` VARCHAR；13. `browser_language` VARCHAR；14. `browser_version` DOUBLE；15. `created_at` TIMESTAMP；16. `custom_onboarding_step` VARCHAR；17. `custom_organisation_id` VARCHAR；18. `custom_organisation_name` VARCHAR；19. `external_id` VARCHAR；20. `has_hard_bounced` BOOLEAN；21. `ios_app_name` VARCHAR；22. `ios_app_version` VARCHAR；23. `ios_device` VARCHAR；24. `ios_last_seen_at` VARCHAR；25. `ios_os_version` VARCHAR；26. `ios_sdk_version` VARCHAR；27. `language_override` VARCHAR；28. `last_contacted_at` TIMESTAMP；29. `last_email_clicked_at` TIMESTAMP；30. `last_email_opened_at` TIMESTAMP；31. `last_replied_at` VARCHAR；32. `last_seen_at` TIMESTAMP；33. `location_city` VARCHAR；34. `location_country` VARCHAR；35. `location_region` VARCHAR；36. `marked_email_as_spam` BOOLEAN；37. `os` VARCHAR；38. `phone` VARCHAR；39. `role` VARCHAR；40. `signed_up_at` TIMESTAMP；41. `unsubscribed_from_emails` BOOLEAN；42. `workspace_id` VARCHAR；43. `avatar` VARCHAR；44. `custom_job_title` VARCHAR；45. `email` VARCHAR；46. `name` VARCHAR；47. `_fivetran_start` TIMESTAMP；48. `_fivetran_end` TIMESTAMP
- agent：1. `id` VARCHAR；2. `updated_at` VARCHAR；3. `_fivetran_active` VARCHAR；4. `_fivetran_synced` VARCHAR；5. `admin_id` VARCHAR；6. `android_app_name` VARCHAR；7. `android_app_version` VARCHAR；8. `android_device` VARCHAR；9. `android_last_seen_at` VARCHAR；10. `android_os_version` VARCHAR；11. `android_sdk_version` VARCHAR；12. `browser` VARCHAR；13. `browser_language` VARCHAR；14. `browser_version` VARCHAR；15. `created_at` VARCHAR；16. `custom_onboarding_step` VARCHAR；17. `custom_organisation_id` VARCHAR；18. `custom_organisation_name` VARCHAR；19. `external_id` VARCHAR；20. `has_hard_bounced` VARCHAR；21. `ios_app_name` VARCHAR；22. `ios_app_version` VARCHAR；23. `ios_device` VARCHAR；24. `ios_last_seen_at` VARCHAR；25. `ios_os_version` VARCHAR；26. `ios_sdk_version` VARCHAR；27. `language_override` VARCHAR；28. `last_contacted_at` VARCHAR；29. `last_email_clicked_at` VARCHAR；30. `last_email_opened_at` VARCHAR；31. `last_replied_at` VARCHAR；32. `last_seen_at` VARCHAR；33. `location_city` VARCHAR；34. `location_country` VARCHAR；35. `location_region` VARCHAR；36. `marked_email_as_spam` VARCHAR；37. `os` VARCHAR；38. `phone` VARCHAR；39. `role` VARCHAR；40. `signed_up_at` VARCHAR；41. `unsubscribed_from_emails` VARCHAR；42. `workspace_id` VARCHAR；43. `avatar` VARCHAR；44. `custom_job_title` VARCHAR；45. `email` VARCHAR；46. `name` VARCHAR；47. `_fivetran_start` VARCHAR；48. `_fivetran_end` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | intercom__company_metrics | 间接 | raw.contact_history_data → staging.stg_intercom__contact_history → intermediate.int_intercom__contact_latest → marts.intercom__company_metrics |
| staging | stg_intercom__contact_history | 直接 | raw.contact_history_data → staging.stg_intercom__contact_history |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.contact_tag_history_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2945 | 2945 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 2945 | 2945 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `contact_id` VARCHAR；2. `contact_updated_at` VARCHAR；3. `tag_id` VARCHAR；4. `_fivetran_active` VARCHAR；5. `_fivetran_synced` VARCHAR；6. `_fivetran_start` VARCHAR；7. `_fivetran_end` VARCHAR
- initial：1. `contact_id` VARCHAR；2. `contact_updated_at` TIMESTAMP；3. `tag_id` BIGINT；4. `_fivetran_synced` TIMESTAMP；5. `_fivetran_start` TIMESTAMP；6. `_fivetran_end` TIMESTAMP；7. `_fivetran_active` BOOLEAN
- agent：1. `contact_id` VARCHAR；2. `contact_updated_at` VARCHAR；3. `tag_id` VARCHAR；4. `_fivetran_active` VARCHAR；5. `_fivetran_synced` VARCHAR；6. `_fivetran_start` VARCHAR；7. `_fivetran_end` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.conversation_contact_history_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 4033 | 4033 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 4033 | 4033 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `conversation_id` VARCHAR；2. `contact_id` VARCHAR；3. `_fivetran_active` VARCHAR；4. `_fivetran_synced` VARCHAR；5. `_fivetran_start` VARCHAR；6. `_fivetran_end` VARCHAR
- initial：1. `contact_id` VARCHAR；2. `conversation_id` BIGINT；3. `conversation_updated_at` TIMESTAMP；4. `_fivetran_synced` TIMESTAMP；5. `_fivetran_start` TIMESTAMP；6. `_fivetran_end` TIMESTAMP；7. `_fivetran_active` BOOLEAN
- agent：1. `conversation_id` VARCHAR；2. `contact_id` VARCHAR；3. `_fivetran_active` VARCHAR；4. `_fivetran_synced` VARCHAR；5. `_fivetran_start` VARCHAR；6. `_fivetran_end` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_intercom__conversation_contact_history | 直接 | raw.conversation_contact_history_data → staging.stg_intercom__conversation_contact_history |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.conversation_history_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 29759 | 29758 | False | 未比较 | ordered_columns_or_types_differ, row_counts_differ |
| gold_vs_agent | 29759 | 29759 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `updated_at` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `assignee_id` VARCHAR；5. `assignee_type` VARCHAR；6. `conversation_rating_created_at` VARCHAR；7. `conversation_rating_remark` VARCHAR；8. `conversation_rating_value` VARCHAR；9. `created_at` VARCHAR；10. `first_contact_reply_created_at` VARCHAR；11. `first_contact_reply_type` VARCHAR；12. `priority` VARCHAR；13. `read` VARCHAR；14. `sla_name` VARCHAR；15. `sla_status` VARCHAR；16. `snoozed_until` VARCHAR；17. `source_author_id` VARCHAR；18. `source_author_type` VARCHAR；19. `source_delivered_as` VARCHAR；20. `source_id` VARCHAR；21. `source_type` VARCHAR；22. `state` VARCHAR；23. `waiting_since` VARCHAR；24. `first_contact_reply_url` VARCHAR；25. `source_body` VARCHAR；26. `source_subject` VARCHAR；27. `source_url` VARCHAR；28. `_fivetran_start` VARCHAR；29. `_fivetran_end` VARCHAR；30. `_fivetran_active` VARCHAR
- initial：1. `id` BIGINT；2. `updated_at` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `assignee_id` DOUBLE；5. `assignee_type` VARCHAR；6. `conversation_rating_created_at` VARCHAR；7. `conversation_rating_remark` VARCHAR；8. `conversation_rating_value` DOUBLE；9. `created_at` VARCHAR；10. `first_contact_reply_created_at` VARCHAR；11. `first_contact_reply_type` VARCHAR；12. `priority` VARCHAR；13. `read` BOOLEAN；14. `sla_name` VARCHAR；15. `sla_status` VARCHAR；16. `snoozed_until` VARCHAR；17. `source_author_id` VARCHAR；18. `source_author_type` VARCHAR；19. `source_delivered_as` VARCHAR；20. `source_id` BIGINT；21. `source_type` VARCHAR；22. `state` VARCHAR；23. `waiting_since` VARCHAR；24. `first_contact_reply_url` VARCHAR；25. `source_body` VARCHAR；26. `source_subject` VARCHAR；27. `source_url` VARCHAR；28. `_fivetran_start` VARCHAR；29. `_fivetran_end` VARCHAR；30. `_fivetran_active` BOOLEAN
- agent：1. `id` VARCHAR；2. `updated_at` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `assignee_id` VARCHAR；5. `assignee_type` VARCHAR；6. `conversation_rating_created_at` VARCHAR；7. `conversation_rating_remark` VARCHAR；8. `conversation_rating_value` VARCHAR；9. `created_at` VARCHAR；10. `first_contact_reply_created_at` VARCHAR；11. `first_contact_reply_type` VARCHAR；12. `priority` VARCHAR；13. `read` VARCHAR；14. `sla_name` VARCHAR；15. `sla_status` VARCHAR；16. `snoozed_until` VARCHAR；17. `source_author_id` VARCHAR；18. `source_author_type` VARCHAR；19. `source_delivered_as` VARCHAR；20. `source_id` VARCHAR；21. `source_type` VARCHAR；22. `state` VARCHAR；23. `waiting_since` VARCHAR；24. `first_contact_reply_url` VARCHAR；25. `source_body` VARCHAR；26. `source_subject` VARCHAR；27. `source_url` VARCHAR；28. `_fivetran_start` VARCHAR；29. `_fivetran_end` VARCHAR；30. `_fivetran_active` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| intermediate | int_intercom__conversation_part_aggregates | 间接 | raw.conversation_history_data → staging.stg_intercom__conversation_history → intermediate.int_intercom__conversation_part_aggregates |
| marts | intercom__company_metrics | 间接 | raw.conversation_history_data → staging.stg_intercom__conversation_history → intermediate.int_intercom__conversation_part_aggregates → marts.intercom__company_metrics |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.conversation_part_history_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 7524 | 7524 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 7524 | 7524 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `updated_at` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `author_id` VARCHAR；5. `author_type` VARCHAR；6. `body` VARCHAR；7. `conversation_id` VARCHAR；8. `created_at` VARCHAR；9. `delivered_as` VARCHAR；10. `external_id` VARCHAR；11. `part_type` VARCHAR；12. `rating_remark` VARCHAR；13. `rating_state` VARCHAR；14. `rating_value` VARCHAR；15. `subject` VARCHAR；16. `type` VARCHAR；17. `_fivetran_start` VARCHAR；18. `_fivetran_end` VARCHAR；19. `_fivetran_active` VARCHAR
- initial：1. `id` VARCHAR；2. `updated_at` TIMESTAMP；3. `_fivetran_synced` TIMESTAMP；4. `author_id` BIGINT；5. `author_type` VARCHAR；6. `body` VARCHAR；7. `created_at` TIMESTAMP；8. `conversation_id` BIGINT；9. `external_id` VARCHAR；10. `part_type` VARCHAR；11. `rating_remark` VARCHAR；12. `rating_value` BIGINT；13. `redacted` BOOLEAN；14. `social_respond` BOOLEAN；15. `type` VARCHAR；16. `updated_at_from_parts` TIMESTAMP；17. `url` VARCHAR；18. `_fivetran_start` TIMESTAMP；19. `_fivetran_end` TIMESTAMP；20. `_fivetran_active` BOOLEAN
- agent：1. `id` VARCHAR；2. `updated_at` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `author_id` VARCHAR；5. `author_type` VARCHAR；6. `body` VARCHAR；7. `conversation_id` VARCHAR；8. `created_at` VARCHAR；9. `delivered_as` VARCHAR；10. `external_id` VARCHAR；11. `part_type` VARCHAR；12. `rating_remark` VARCHAR；13. `rating_state` VARCHAR；14. `rating_value` VARCHAR；15. `subject` VARCHAR；16. `type` VARCHAR；17. `_fivetran_start` VARCHAR；18. `_fivetran_end` VARCHAR；19. `_fivetran_active` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| intermediate | int_intercom__conversation_part_aggregates | 间接 | raw.conversation_part_history_data → staging.stg_intercom__conversation_part_history → intermediate.int_intercom__conversation_part_aggregates |
| marts | intercom__company_metrics | 间接 | raw.conversation_part_history_data → staging.stg_intercom__conversation_part_history → intermediate.int_intercom__conversation_part_aggregates → marts.intercom__company_metrics |
| staging | stg_intercom__conversation_part_history | 直接 | raw.conversation_part_history_data → staging.stg_intercom__conversation_part_history |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.conversation_tag_history_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2996 | 2996 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 2996 | 2996 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `conversation_id` VARCHAR；2. `conversation_updated_at` VARCHAR；3. `tag_id` VARCHAR；4. `_fivetran_active` VARCHAR；5. `_fivetran_synced` VARCHAR；6. `_fivetran_start` VARCHAR；7. `_fivetran_end` VARCHAR
- initial：1. `conversation_id` BIGINT；2. `conversation_updated_at` TIMESTAMP；3. `tag_id` BIGINT；4. `_fivetran_active` BOOLEAN；5. `_fivetran_synced` TIMESTAMP；6. `_fivetran_start` TIMESTAMP；7. `_fivetran_end` TIMESTAMP
- agent：1. `conversation_id` VARCHAR；2. `conversation_updated_at` VARCHAR；3. `tag_id` VARCHAR；4. `_fivetran_active` VARCHAR；5. `_fivetran_synced` VARCHAR；6. `_fivetran_start` VARCHAR；7. `_fivetran_end` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.tag_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 124 | 123 | False | 未比较 | ordered_columns_or_types_differ, row_counts_differ |
| gold_vs_agent | 124 | 124 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `name` VARCHAR
- initial：1. `id` BIGINT；2. `_fivetran_deleted` BOOLEAN；3. `_fivetran_synced` VARCHAR；4. `name` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `name` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.team_admin_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 145 | 145 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 145 | 145 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `admin_id` VARCHAR；2. `team_id` VARCHAR；3. `_fivetran_deleted` VARCHAR；4. `_fivetran_synced` VARCHAR
- initial：1. `team_id` BIGINT；2. `admin_id` BIGINT；3. `team_updated_at` TIMESTAMP；4. `_fivetran_active` BOOLEAN；5. `_fivetran_synced` TIMESTAMP；6. `_fivetran_start` TIMESTAMP；7. `_fivetran_end` TIMESTAMP
- agent：1. `admin_id` VARCHAR；2. `team_id` VARCHAR；3. `_fivetran_deleted` VARCHAR；4. `_fivetran_synced` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-020 raw.team_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 52 | 51 | False | 未比较 | ordered_columns_or_types_differ, row_counts_differ |
| gold_vs_agent | 52 | 52 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `name` VARCHAR；3. `_fivetran_deleted` VARCHAR；4. `_fivetran_synced` VARCHAR
- initial：1. `id` BIGINT；2. `name` VARCHAR；3. `_fivetran_deleted` BOOLEAN；4. `_fivetran_synced` VARCHAR
- agent：1. `id` VARCHAR；2. `name` VARCHAR；3. `_fivetran_deleted` VARCHAR；4. `_fivetran_synced` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-020.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-021 raw.campaign

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 200 | 197 | False | 未比较 | ordered_columns_or_types_differ, row_counts_differ |
| gold_vs_agent | 200 | 200 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `ID` VARCHAR；2. `FROM_NAME` VARCHAR；3. `STATUS_ID` BIGINT；4. `CAMPAIGN_TYPE` VARCHAR；5. `STATUS_LABEL` VARCHAR；6. `FROM_EMAIL` VARCHAR；7. `SUBJECT` VARCHAR；8. `NAME` VARCHAR；9. `STATUS` VARCHAR；10. `CREATED` VARCHAR；11. `UPDATED` TIMESTAMP；12. `SEND_TIME` TIMESTAMP；13. `SENT_AT` TIMESTAMP；14. `_FIVETRAN_DELETED` VARCHAR；15. `EMAIL_TEMPLATE_ID` VARCHAR；16. `_FIVETRAN_SYNCED` VARCHAR；17. `ARCHIVED` VARCHAR；18. `SCHEDULED` VARCHAR；19. `column18` VARCHAR；20. `column19` VARCHAR；21. `column20` VARCHAR；22. `column21` VARCHAR；23. `column22` VARCHAR；24. `column23` VARCHAR；25. `column24` VARCHAR；26. `column25` VARCHAR；27. `column26` TIMESTAMP；28. `column27` TIMESTAMP；29. `column28` TIMESTAMP；30. `column29` TIMESTAMP；31. `column30` BOOLEAN；32. `column31` VARCHAR；33. `column32` TIMESTAMP；34. `column33` BOOLEAN；35. `column34` TIMESTAMP
- initial：1. `ID` VARCHAR；2. `FROM_NAME` VARCHAR；3. `STATUS_ID` VARCHAR；4. `CAMPAIGN_TYPE` VARCHAR；5. `STATUS_LABEL` VARCHAR；6. `FROM_EMAIL` VARCHAR；7. `SUBJECT` VARCHAR；8. `NAME` VARCHAR；9. `STATUS` VARCHAR；10. `CREATED` VARCHAR；11. `UPDATED` VARCHAR；12. `SEND_TIME` VARCHAR；13. `SENT_AT` VARCHAR；14. `_FIVETRAN_DELETED` VARCHAR；15. `EMAIL_TEMPLATE_ID` VARCHAR；16. `_FIVETRAN_SYNCED` VARCHAR；17. `ARCHIVED` VARCHAR；18. `SCHEDULED` VARCHAR
- agent：1. `ID` VARCHAR；2. `FROM_NAME` VARCHAR；3. `STATUS_ID` BIGINT；4. `CAMPAIGN_TYPE` VARCHAR；5. `STATUS_LABEL` VARCHAR；6. `FROM_EMAIL` VARCHAR；7. `SUBJECT` VARCHAR；8. `NAME` VARCHAR；9. `STATUS` VARCHAR；10. `CREATED` VARCHAR；11. `UPDATED` TIMESTAMP；12. `SEND_TIME` TIMESTAMP；13. `SENT_AT` TIMESTAMP；14. `_FIVETRAN_DELETED` VARCHAR；15. `EMAIL_TEMPLATE_ID` VARCHAR；16. `_FIVETRAN_SYNCED` VARCHAR；17. `ARCHIVED` VARCHAR；18. `SCHEDULED` VARCHAR；19. `column18` VARCHAR；20. `column19` VARCHAR；21. `column20` VARCHAR；22. `column21` VARCHAR；23. `column22` VARCHAR；24. `column23` VARCHAR；25. `column24` VARCHAR；26. `column25` VARCHAR；27. `column26` TIMESTAMP；28. `column27` TIMESTAMP；29. `column28` TIMESTAMP；30. `column29` TIMESTAMP；31. `column30` BOOLEAN；32. `column31` VARCHAR；33. `column32` TIMESTAMP；34. `column33` BOOLEAN；35. `column34` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| intermediate | int_klaviyo__events | 间接 | raw.campaign → staging.stg_klaviyo__campaign → intermediate.int_klaviyo__events |
| staging | stg_klaviyo__campaign | 直接 | raw.campaign → staging.stg_klaviyo__campaign |

来源：`015_raw_impl-021.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-021 raw.event

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2500 | 2499 | False | 未比较 | ordered_columns_or_types_differ, row_counts_differ |
| gold_vs_agent | 2500 | 2500 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `ID` VARCHAR；2. `PERSON_ID` VARCHAR；3. `CAMPAIGN_ID` VARCHAR；4. `FLOW_ID` VARCHAR；5. `FLOW_MESSAGE_ID` VARCHAR；6. `UUID` VARCHAR；7. `DATETIME` TIMESTAMP；8. `TIMESTAMP` TIMESTAMP；9. `_FIVETRAN_DELETED` BOOLEAN；10. `METRIC_ID` VARCHAR；11. `TYPE` VARCHAR；12. `_VARIATION` VARCHAR；13. `PROPERTY_VALUE` VARCHAR；14. `PROPERTY_SOURCE_NAME` VARCHAR；15. `PROPERTY_EXTRA` VARCHAR；16. `PROPERTY_SHIPPING_RATE` VARCHAR；17. `PROPERTY_ITEMS` VARCHAR；18. `PROPERTY_TAGS` VARCHAR；19. `PROPERTY_ITEM_COUNT` BIGINT；20. `PROPERTY_COLLECTIONS` VARCHAR；21. `_FIVETRAN_SYNCED` TIMESTAMP；22. `PROPERTY_CURRENCY_CODE` VARCHAR；23. `PROPERTY_PRODUCT_ID` VARCHAR；24. `PROPERTY_QUANTITY` VARCHAR；25. `PROPERTY_NAME` VARCHAR；26. `PROPERTY_VARIANT_OPTION_TITLE` VARCHAR；27. `PROPERTY_SKU` VARCHAR；28. `PROPERTY_VARIANT_NAME` VARCHAR；29. `PROPERTY_VENDOR` VARCHAR；30. `PROPERTY_EVENT_ID` VARCHAR；31. `PROPERTY_TOTAL_DISCOUNTS` VARCHAR；32. `PROPERTY_ATTRIBUTION` VARCHAR；33. `PROPERTY_DISCOUNT_CODES` VARCHAR；34. `PROPERTY_FULFILLMENT_HOURS` VARCHAR；35. `PROPERTY_FULFILLMENT_STATUS` VARCHAR；36. `PROPERTY_SUBJECT` VARCHAR；37. `PROPERTY_TITLE` VARCHAR；38. `PROPERTY_MESSAGE_INTERACTION` VARCHAR；39. `PROPERTY_URL` VARCHAR；40. `PROPERTY_SHIPMENT_TYPE` VARCHAR；41. `PROPERTY_COURIER_NAME` VARCHAR；42. `PROPERTY_CURRENT_STATUS` VARCHAR；43. `PROPERTY_TRACKING_SHIP_DATE` VARCHAR；44. `PROPERTY_TRACKING_POSTAL_CODE` VARCHAR；45. `PROPERTY_SHIPMENT_PACKAGE_COUNT` VARCHAR；46. `PROPERTY_CAMPAIGN_NAME` VARCHAR；47. `PROPERTY_COHORT_MESSAGE_SEND_COHORT` VARCHAR；48. `PROPERTY_EMAIL_DOMAIN` VARCHAR；49. `PROPERTY_BOUNCE_TYPE` VARCHAR；50. `PROPERTY_CLIENT_TYPE` VARCHAR；51. `PROPERTY_CLIENT_OS` VARCHAR；52. `PROPERTY_CLIENT_NAME` VARCHAR；53. `PROPERTY_CLIENT_OS_FAMILY` VARCHAR；54. `PROPERTY_CLIENT_CANONICAL` VARCHAR；55. `PROPERTY_PAGE` VARCHAR；56. `PROPERTY_IS_SESSION_ACTIVITY` VARCHAR；57. `PROPERTY_OS` VARCHAR；58. `PROPERTY_SESSION_END` VARCHAR；59. `PROPERTY_BROWSER` VARCHAR；60. `PROPERTY_LIST` VARCHAR；61. `PROPERTY_COMPARE_AT_PRICE` DOUBLE；62. `PROPERTY_PRICE` DOUBLE；63. `PROPERTY_IMAGE_URL` VARCHAR；64. `PROPERTY_BRAND` VARCHAR；65. `PROPERTY_CATEGORIES` VARCHAR；66. `PROPERTY_VARIANT_OPTION_SIZE` VARCHAR；67. `PROPERTY_ATTRIBUTE_WORKOUT` VARCHAR；68. `PROPERTY_ATTRIBUTE_AGE` VARCHAR；69. `PROPERTY_ATTRIBUTE_FITNESS_GOAL` VARCHAR；70. `PROPERTY_ATTRIBUTE_BREAKFAST` VARCHAR；71. `PROPERTY_VARIANT_OPTION_TYPE` VARCHAR；72. `PROPERTY_COHORT_VARIATION_SEND_COHORT` VARCHAR；73. `PROPERTY_METHOD` VARCHAR；74. `PROPERTY_TO_NUMBER` VARCHAR；75. `PROPERTY_MESSAGE_TYPE` VARCHAR；76. `PROPERTY_FROM_NUMBER` VARCHAR；77. `PROPERTY_MESSAGE_FORMAT` VARCHAR；78. `PROPERTY_MESSAGE_NAME` VARCHAR；79. `PROPERTY_CARRIER_DELIVERY_STATUS` VARCHAR；80. `PROPERTY_FAILURE_TYPE` VARCHAR；81. `PROPERTY_FAILURE_SOURCE` VARCHAR；82. `PROPERTY_MESSAGE_BODY` VARCHAR；83. `PROPERTY_EMAIL` VARCHAR；84. `PROPERTY_ATTRIBUTE_KIT` VARCHAR；85. `PROPERTY_VENDOR_ERROR_CODE` VARCHAR；86. `PROPERTY_ORDR_DETAILS` VARCHAR；87. `PROPERTY_DATE_TO_SEND_GIFT` VARCHAR；88. `PROPERTY_RECIPIENT_NAME` VARCHAR；89. `PROPERTY_ATTRIBUTE_FACEBOOK_ORDER_RETAILER_ID` VARCHAR；90. `PROPERTY_SENDER_S_NAME` VARCHAR；91. `PROPERTY_ATTRIBUTE_KITID` VARCHAR；92. `PROPERTY_CONVERSATION_ID` VARCHAR；93. `PROPERTY_CONVERSATION_LINK` VARCHAR；94. `PROPERTY_CONVERSATION_CHANNEL` VARCHAR；95. `PROPERTY_RATING` VARCHAR；96. `PROPERTY_SCORE` VARCHAR；97. `PROPERTY_FROM_PHONE_REGION` VARCHAR；98. `PROPERTY_SHIPMENT_CARRIER` VARCHAR；99. `PROPERTY_SHIPMENT_STATUS` VARCHAR；100. `PROPERTY_TO_PHONE_REGION` VARCHAR；101. `column100` VARCHAR；102. `column101` VARCHAR；103. `column102` VARCHAR；104. `column103` VARCHAR；105. `column104` VARCHAR；106. `column105` TIMESTAMP；107. `column106` TIMESTAMP；108. `column107` BOOLEAN；109. `column108` VARCHAR；110. `column109` VARCHAR；111. `column110` VARCHAR；112. `column111` VARCHAR；113. `column112` VARCHAR；114. `column113` VARCHAR；115. `column114` VARCHAR；116. `column115` VARCHAR；117. `column116` VARCHAR；118. `column117` BIGINT；119. `column118` VARCHAR；120. `column119` TIMESTAMP；121. `column120` VARCHAR；122. `column121` VARCHAR；123. `column122` VARCHAR；124. `column123` VARCHAR；125. `column124` VARCHAR；126. `column125` VARCHAR；127. `column126` VARCHAR；128. `column127` VARCHAR；129. `column128` VARCHAR；130. `column129` VARCHAR；131. `column130` VARCHAR；132. `column131` VARCHAR；133. `column132` VARCHAR；134. `column133` VARCHAR；135. `column134` VARCHAR；136. `column135` VARCHAR；137. `column136` VARCHAR；138. `column137` VARCHAR；139. `column138` VARCHAR；140. `column139` VARCHAR；141. `column140` VARCHAR；142. `column141` VARCHAR；143. `column142` VARCHAR；144. `column143` VARCHAR；145. `column144` VARCHAR；146. `column145` VARCHAR；147. `column146` VARCHAR；148. `column147` VARCHAR；149. `column148` VARCHAR；150. `column149` VARCHAR；151. `column150` VARCHAR；152. `column151` VARCHAR；153. `column152` VARCHAR；154. `column153` VARCHAR；155. `column154` VARCHAR；156. `column155` VARCHAR；157. `column156` VARCHAR；158. `column157` VARCHAR；159. `column158` VARCHAR；160. `column159` DOUBLE；161. `column160` DOUBLE；162. `column161` VARCHAR；163. `column162` VARCHAR；164. `column163` VARCHAR；165. `column164` VARCHAR；166. `column165` VARCHAR；167. `column166` VARCHAR；168. `column167` VARCHAR；169. `column168` VARCHAR；170. `column169` VARCHAR；171. `column170` VARCHAR；172. `column171` VARCHAR；173. `column172` VARCHAR；174. `column173` VARCHAR；175. `column174` VARCHAR；176. `column175` VARCHAR；177. `column176` VARCHAR；178. `column177` VARCHAR；179. `column178` VARCHAR；180. `column179` VARCHAR；181. `column180` VARCHAR；182. `column181` VARCHAR；183. `column182` VARCHAR；184. `column183` VARCHAR；185. `column184` VARCHAR；186. `column185` VARCHAR；187. `column186` VARCHAR；188. `column187` VARCHAR；189. `column188` VARCHAR；190. `column189` VARCHAR；191. `column190` VARCHAR；192. `column191` VARCHAR；193. `column192` VARCHAR；194. `column193` VARCHAR；195. `column194` VARCHAR；196. `column195` VARCHAR；197. `column196` VARCHAR；198. `column197` VARCHAR；199. `column198` VARCHAR
- initial：1. `ID` VARCHAR；2. `PERSON_ID` VARCHAR；3. `CAMPAIGN_ID` VARCHAR；4. `FLOW_ID` VARCHAR；5. `FLOW_MESSAGE_ID` VARCHAR；6. `UUID` VARCHAR；7. `DATETIME` VARCHAR；8. `TIMESTAMP` VARCHAR；9. `_FIVETRAN_DELETED` VARCHAR；10. `METRIC_ID` VARCHAR；11. `TYPE` VARCHAR；12. `_VARIATION` VARCHAR；13. `PROPERTY_VALUE` VARCHAR；14. `PROPERTY_SOURCE_NAME` VARCHAR；15. `PROPERTY_EXTRA` VARCHAR；16. `PROPERTY_SHIPPING_RATE` VARCHAR；17. `PROPERTY_ITEMS` VARCHAR；18. `PROPERTY_TAGS` VARCHAR；19. `PROPERTY_ITEM_COUNT` VARCHAR；20. `PROPERTY_COLLECTIONS` VARCHAR；21. `_FIVETRAN_SYNCED` VARCHAR；22. `PROPERTY_CURRENCY_CODE` VARCHAR；23. `PROPERTY_PRODUCT_ID` VARCHAR；24. `PROPERTY_QUANTITY` VARCHAR；25. `PROPERTY_NAME` VARCHAR；26. `PROPERTY_VARIANT_OPTION_TITLE` VARCHAR；27. `PROPERTY_SKU` VARCHAR；28. `PROPERTY_VARIANT_NAME` VARCHAR；29. `PROPERTY_VENDOR` VARCHAR；30. `PROPERTY_EVENT_ID` VARCHAR；31. `PROPERTY_TOTAL_DISCOUNTS` VARCHAR；32. `PROPERTY_ATTRIBUTION` VARCHAR；33. `PROPERTY_DISCOUNT_CODES` VARCHAR；34. `PROPERTY_FULFILLMENT_HOURS` VARCHAR；35. `PROPERTY_FULFILLMENT_STATUS` VARCHAR；36. `PROPERTY_SUBJECT` VARCHAR；37. `PROPERTY_TITLE` VARCHAR；38. `PROPERTY_MESSAGE_INTERACTION` VARCHAR；39. `PROPERTY_URL` VARCHAR；40. `PROPERTY_SHIPMENT_TYPE` VARCHAR；41. `PROPERTY_COURIER_NAME` VARCHAR；42. `PROPERTY_CURRENT_STATUS` VARCHAR；43. `PROPERTY_TRACKING_SHIP_DATE` VARCHAR；44. `PROPERTY_TRACKING_POSTAL_CODE` VARCHAR；45. `PROPERTY_SHIPMENT_PACKAGE_COUNT` VARCHAR；46. `PROPERTY_CAMPAIGN_NAME` VARCHAR；47. `PROPERTY_COHORT_MESSAGE_SEND_COHORT` VARCHAR；48. `PROPERTY_EMAIL_DOMAIN` VARCHAR；49. `PROPERTY_BOUNCE_TYPE` VARCHAR；50. `PROPERTY_CLIENT_TYPE` VARCHAR；51. `PROPERTY_CLIENT_OS` VARCHAR；52. `PROPERTY_CLIENT_NAME` VARCHAR；53. `PROPERTY_CLIENT_OS_FAMILY` VARCHAR；54. `PROPERTY_CLIENT_CANONICAL` VARCHAR；55. `PROPERTY_PAGE` VARCHAR；56. `PROPERTY_IS_SESSION_ACTIVITY` VARCHAR；57. `PROPERTY_OS` VARCHAR；58. `PROPERTY_SESSION_END` VARCHAR；59. `PROPERTY_BROWSER` VARCHAR；60. `PROPERTY_LIST` VARCHAR；61. `PROPERTY_COMPARE_AT_PRICE` VARCHAR；62. `PROPERTY_PRICE` VARCHAR；63. `PROPERTY_IMAGE_URL` VARCHAR；64. `PROPERTY_BRAND` VARCHAR；65. `PROPERTY_CATEGORIES` VARCHAR；66. `PROPERTY_VARIANT_OPTION_SIZE` VARCHAR；67. `PROPERTY_ATTRIBUTE_WORKOUT` VARCHAR；68. `PROPERTY_ATTRIBUTE_AGE` VARCHAR；69. `PROPERTY_ATTRIBUTE_FITNESS_GOAL` VARCHAR；70. `PROPERTY_ATTRIBUTE_BREAKFAST` VARCHAR；71. `PROPERTY_VARIANT_OPTION_TYPE` VARCHAR；72. `PROPERTY_COHORT_VARIATION_SEND_COHORT` VARCHAR；73. `PROPERTY_METHOD` VARCHAR；74. `PROPERTY_TO_NUMBER` VARCHAR；75. `PROPERTY_MESSAGE_TYPE` VARCHAR；76. `PROPERTY_FROM_NUMBER` VARCHAR；77. `PROPERTY_MESSAGE_FORMAT` VARCHAR；78. `PROPERTY_MESSAGE_NAME` VARCHAR；79. `PROPERTY_CARRIER_DELIVERY_STATUS` VARCHAR；80. `PROPERTY_FAILURE_TYPE` VARCHAR；81. `PROPERTY_FAILURE_SOURCE` VARCHAR；82. `PROPERTY_MESSAGE_BODY` VARCHAR；83. `PROPERTY_EMAIL` VARCHAR；84. `PROPERTY_ATTRIBUTE_KIT` VARCHAR；85. `PROPERTY_VENDOR_ERROR_CODE` VARCHAR；86. `PROPERTY_ORDR_DETAILS` VARCHAR；87. `PROPERTY_DATE_TO_SEND_GIFT` VARCHAR；88. `PROPERTY_RECIPIENT_NAME` VARCHAR；89. `PROPERTY_ATTRIBUTE_FACEBOOK_ORDER_RETAILER_ID` VARCHAR；90. `PROPERTY_SENDER_S_NAME` VARCHAR；91. `PROPERTY_ATTRIBUTE_KITID` VARCHAR；92. `PROPERTY_CONVERSATION_ID` VARCHAR；93. `PROPERTY_CONVERSATION_LINK` VARCHAR；94. `PROPERTY_CONVERSATION_CHANNEL` VARCHAR；95. `PROPERTY_RATING` VARCHAR；96. `PROPERTY_SCORE` VARCHAR；97. `PROPERTY_FROM_PHONE_REGION` VARCHAR；98. `PROPERTY_SHIPMENT_CARRIER` VARCHAR；99. `PROPERTY_SHIPMENT_STATUS` VARCHAR；100. `PROPERTY_TO_PHONE_REGION` VARCHAR
- agent：1. `ID` VARCHAR；2. `PERSON_ID` VARCHAR；3. `CAMPAIGN_ID` VARCHAR；4. `FLOW_ID` VARCHAR；5. `FLOW_MESSAGE_ID` VARCHAR；6. `UUID` VARCHAR；7. `DATETIME` TIMESTAMP；8. `TIMESTAMP` TIMESTAMP；9. `_FIVETRAN_DELETED` BOOLEAN；10. `METRIC_ID` VARCHAR；11. `TYPE` VARCHAR；12. `_VARIATION` VARCHAR；13. `PROPERTY_VALUE` VARCHAR；14. `PROPERTY_SOURCE_NAME` VARCHAR；15. `PROPERTY_EXTRA` VARCHAR；16. `PROPERTY_SHIPPING_RATE` VARCHAR；17. `PROPERTY_ITEMS` VARCHAR；18. `PROPERTY_TAGS` VARCHAR；19. `PROPERTY_ITEM_COUNT` BIGINT；20. `PROPERTY_COLLECTIONS` VARCHAR；21. `_FIVETRAN_SYNCED` TIMESTAMP；22. `PROPERTY_CURRENCY_CODE` VARCHAR；23. `PROPERTY_PRODUCT_ID` VARCHAR；24. `PROPERTY_QUANTITY` VARCHAR；25. `PROPERTY_NAME` VARCHAR；26. `PROPERTY_VARIANT_OPTION_TITLE` VARCHAR；27. `PROPERTY_SKU` VARCHAR；28. `PROPERTY_VARIANT_NAME` VARCHAR；29. `PROPERTY_VENDOR` VARCHAR；30. `PROPERTY_EVENT_ID` VARCHAR；31. `PROPERTY_TOTAL_DISCOUNTS` VARCHAR；32. `PROPERTY_ATTRIBUTION` VARCHAR；33. `PROPERTY_DISCOUNT_CODES` VARCHAR；34. `PROPERTY_FULFILLMENT_HOURS` VARCHAR；35. `PROPERTY_FULFILLMENT_STATUS` VARCHAR；36. `PROPERTY_SUBJECT` VARCHAR；37. `PROPERTY_TITLE` VARCHAR；38. `PROPERTY_MESSAGE_INTERACTION` VARCHAR；39. `PROPERTY_URL` VARCHAR；40. `PROPERTY_SHIPMENT_TYPE` VARCHAR；41. `PROPERTY_COURIER_NAME` VARCHAR；42. `PROPERTY_CURRENT_STATUS` VARCHAR；43. `PROPERTY_TRACKING_SHIP_DATE` VARCHAR；44. `PROPERTY_TRACKING_POSTAL_CODE` VARCHAR；45. `PROPERTY_SHIPMENT_PACKAGE_COUNT` VARCHAR；46. `PROPERTY_CAMPAIGN_NAME` VARCHAR；47. `PROPERTY_COHORT_MESSAGE_SEND_COHORT` VARCHAR；48. `PROPERTY_EMAIL_DOMAIN` VARCHAR；49. `PROPERTY_BOUNCE_TYPE` VARCHAR；50. `PROPERTY_CLIENT_TYPE` VARCHAR；51. `PROPERTY_CLIENT_OS` VARCHAR；52. `PROPERTY_CLIENT_NAME` VARCHAR；53. `PROPERTY_CLIENT_OS_FAMILY` VARCHAR；54. `PROPERTY_CLIENT_CANONICAL` VARCHAR；55. `PROPERTY_PAGE` VARCHAR；56. `PROPERTY_IS_SESSION_ACTIVITY` VARCHAR；57. `PROPERTY_OS` VARCHAR；58. `PROPERTY_SESSION_END` VARCHAR；59. `PROPERTY_BROWSER` VARCHAR；60. `PROPERTY_LIST` VARCHAR；61. `PROPERTY_COMPARE_AT_PRICE` DOUBLE；62. `PROPERTY_PRICE` DOUBLE；63. `PROPERTY_IMAGE_URL` VARCHAR；64. `PROPERTY_BRAND` VARCHAR；65. `PROPERTY_CATEGORIES` VARCHAR；66. `PROPERTY_VARIANT_OPTION_SIZE` VARCHAR；67. `PROPERTY_ATTRIBUTE_WORKOUT` VARCHAR；68. `PROPERTY_ATTRIBUTE_AGE` VARCHAR；69. `PROPERTY_ATTRIBUTE_FITNESS_GOAL` VARCHAR；70. `PROPERTY_ATTRIBUTE_BREAKFAST` VARCHAR；71. `PROPERTY_VARIANT_OPTION_TYPE` VARCHAR；72. `PROPERTY_COHORT_VARIATION_SEND_COHORT` VARCHAR；73. `PROPERTY_METHOD` VARCHAR；74. `PROPERTY_TO_NUMBER` VARCHAR；75. `PROPERTY_MESSAGE_TYPE` VARCHAR；76. `PROPERTY_FROM_NUMBER` VARCHAR；77. `PROPERTY_MESSAGE_FORMAT` VARCHAR；78. `PROPERTY_MESSAGE_NAME` VARCHAR；79. `PROPERTY_CARRIER_DELIVERY_STATUS` VARCHAR；80. `PROPERTY_FAILURE_TYPE` VARCHAR；81. `PROPERTY_FAILURE_SOURCE` VARCHAR；82. `PROPERTY_MESSAGE_BODY` VARCHAR；83. `PROPERTY_EMAIL` VARCHAR；84. `PROPERTY_ATTRIBUTE_KIT` VARCHAR；85. `PROPERTY_VENDOR_ERROR_CODE` VARCHAR；86. `PROPERTY_ORDR_DETAILS` VARCHAR；87. `PROPERTY_DATE_TO_SEND_GIFT` VARCHAR；88. `PROPERTY_RECIPIENT_NAME` VARCHAR；89. `PROPERTY_ATTRIBUTE_FACEBOOK_ORDER_RETAILER_ID` VARCHAR；90. `PROPERTY_SENDER_S_NAME` VARCHAR；91. `PROPERTY_ATTRIBUTE_KITID` VARCHAR；92. `PROPERTY_CONVERSATION_ID` VARCHAR；93. `PROPERTY_CONVERSATION_LINK` VARCHAR；94. `PROPERTY_CONVERSATION_CHANNEL` VARCHAR；95. `PROPERTY_RATING` VARCHAR；96. `PROPERTY_SCORE` VARCHAR；97. `PROPERTY_FROM_PHONE_REGION` VARCHAR；98. `PROPERTY_SHIPMENT_CARRIER` VARCHAR；99. `PROPERTY_SHIPMENT_STATUS` VARCHAR；100. `PROPERTY_TO_PHONE_REGION` VARCHAR；101. `column100` VARCHAR；102. `column101` VARCHAR；103. `column102` VARCHAR；104. `column103` VARCHAR；105. `column104` VARCHAR；106. `column105` TIMESTAMP；107. `column106` TIMESTAMP；108. `column107` BOOLEAN；109. `column108` VARCHAR；110. `column109` VARCHAR；111. `column110` VARCHAR；112. `column111` VARCHAR；113. `column112` VARCHAR；114. `column113` VARCHAR；115. `column114` VARCHAR；116. `column115` VARCHAR；117. `column116` VARCHAR；118. `column117` BIGINT；119. `column118` VARCHAR；120. `column119` TIMESTAMP；121. `column120` VARCHAR；122. `column121` VARCHAR；123. `column122` VARCHAR；124. `column123` VARCHAR；125. `column124` VARCHAR；126. `column125` VARCHAR；127. `column126` VARCHAR；128. `column127` VARCHAR；129. `column128` VARCHAR；130. `column129` VARCHAR；131. `column130` VARCHAR；132. `column131` VARCHAR；133. `column132` VARCHAR；134. `column133` VARCHAR；135. `column134` VARCHAR；136. `column135` VARCHAR；137. `column136` VARCHAR；138. `column137` VARCHAR；139. `column138` VARCHAR；140. `column139` VARCHAR；141. `column140` VARCHAR；142. `column141` VARCHAR；143. `column142` VARCHAR；144. `column143` VARCHAR；145. `column144` VARCHAR；146. `column145` VARCHAR；147. `column146` VARCHAR；148. `column147` VARCHAR；149. `column148` VARCHAR；150. `column149` VARCHAR；151. `column150` VARCHAR；152. `column151` VARCHAR；153. `column152` VARCHAR；154. `column153` VARCHAR；155. `column154` VARCHAR；156. `column155` VARCHAR；157. `column156` VARCHAR；158. `column157` VARCHAR；159. `column158` VARCHAR；160. `column159` DOUBLE；161. `column160` DOUBLE；162. `column161` VARCHAR；163. `column162` VARCHAR；164. `column163` VARCHAR；165. `column164` VARCHAR；166. `column165` VARCHAR；167. `column166` VARCHAR；168. `column167` VARCHAR；169. `column168` VARCHAR；170. `column169` VARCHAR；171. `column170` VARCHAR；172. `column171` VARCHAR；173. `column172` VARCHAR；174. `column173` VARCHAR；175. `column174` VARCHAR；176. `column175` VARCHAR；177. `column176` VARCHAR；178. `column177` VARCHAR；179. `column178` VARCHAR；180. `column179` VARCHAR；181. `column180` VARCHAR；182. `column181` VARCHAR；183. `column182` VARCHAR；184. `column183` VARCHAR；185. `column184` VARCHAR；186. `column185` VARCHAR；187. `column186` VARCHAR；188. `column187` VARCHAR；189. `column188` VARCHAR；190. `column189` VARCHAR；191. `column190` VARCHAR；192. `column191` VARCHAR；193. `column192` VARCHAR；194. `column193` VARCHAR；195. `column194` VARCHAR；196. `column195` VARCHAR；197. `column196` VARCHAR；198. `column197` VARCHAR；199. `column198` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| intermediate | int_klaviyo__events | 间接 | raw.event → staging.stg_klaviyo__event → intermediate.int_klaviyo__events |
| intermediate | int_klaviyo__person_metrics | 间接 | raw.event → staging.stg_klaviyo__event → intermediate.int_klaviyo__person_metrics |
| staging | stg_klaviyo__event | 直接 | raw.event → staging.stg_klaviyo__event |

来源：`015_raw_impl-021.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-021 raw.flow

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 79 | 79 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 79 | 79 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `name` VARCHAR；3. `status` VARCHAR；4. `created` VARCHAR；5. `updated` VARCHAR；6. `customer_filter` VARCHAR；7. `_fivetran_deleted` BOOLEAN；8. `_fivetran_synced` VARCHAR；9. `archived` BOOLEAN；10. `trigger_type` VARCHAR
- initial：1. `ID` VARCHAR；2. `NAME` VARCHAR；3. `STATUS` VARCHAR；4. `CREATED` VARCHAR；5. `UPDATED` VARCHAR；6. `CUSTOMER_FILTER` VARCHAR；7. `_FIVETRAN_DELETED` VARCHAR；8. `_FIVETRAN_SYNCED` VARCHAR；9. `ARCHIVED` VARCHAR；10. `TRIGGER_TYPE` VARCHAR
- agent：1. `id` VARCHAR；2. `name` VARCHAR；3. `status` VARCHAR；4. `created` VARCHAR；5. `updated` VARCHAR；6. `customer_filter` VARCHAR；7. `_fivetran_deleted` BOOLEAN；8. `_fivetran_synced` VARCHAR；9. `archived` BOOLEAN；10. `trigger_type` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| intermediate | int_klaviyo__events | 间接 | raw.flow → staging.stg_klaviyo__flow → intermediate.int_klaviyo__events |
| staging | stg_klaviyo__flow | 直接 | raw.flow → staging.stg_klaviyo__flow |

来源：`015_raw_impl-021.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-021 raw.metric

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 29 | 29 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 29 | 29 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `name` VARCHAR；3. `integration_id` VARCHAR；4. `created` VARCHAR；5. `updated` VARCHAR；6. `_fivetran_deleted` BOOLEAN；7. `_fivetran_synced` VARCHAR；8. `integration_category` VARCHAR；9. `integration_name` VARCHAR
- initial：1. `ID` VARCHAR；2. `NAME` VARCHAR；3. `INTEGRATION_ID` VARCHAR；4. `CREATED` VARCHAR；5. `UPDATED` VARCHAR；6. `_FIVETRAN_DELETED` VARCHAR；7. `_FIVETRAN_SYNCED` VARCHAR；8. `INTEGRATION_CATEGORY` VARCHAR；9. `INTEGRATION_NAME` VARCHAR
- agent：1. `id` VARCHAR；2. `name` VARCHAR；3. `integration_id` VARCHAR；4. `created` VARCHAR；5. `updated` VARCHAR；6. `_fivetran_deleted` BOOLEAN；7. `_fivetran_synced` VARCHAR；8. `integration_category` VARCHAR；9. `integration_name` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| intermediate | int_klaviyo__events | 间接 | raw.metric → staging.stg_klaviyo__metric → intermediate.int_klaviyo__events |
| staging | stg_klaviyo__metric | 直接 | raw.metric → staging.stg_klaviyo__metric |

来源：`015_raw_impl-021.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-021 raw.person

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1200 | 1199 | False | 未比较 | ordered_columns_or_types_differ, row_counts_differ |
| gold_vs_agent | 1200 | 1200 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `ID` VARCHAR；2. `UPDATED` TIMESTAMP；3. `CREATED` TIMESTAMP；4. `_FIVETRAN_DELETED` BOOLEAN；5. `FIRST_NAME` VARCHAR；6. `LAST_NAME` VARCHAR；7. `ADDRESS_1` VARCHAR；8. `ADDRESS_2` VARCHAR；9. `TITLE` VARCHAR；10. `TIMEZONE` VARCHAR；11. `ORGANIZATION` VARCHAR；12. `REGION` VARCHAR；13. `LONGITUDE` DOUBLE；14. `LATITUDE` DOUBLE；15. `PHONE_NUMBER` VARCHAR；16. `COUNTRY` VARCHAR；17. `ZIP` BIGINT；18. `CITY` VARCHAR；19. `EMAIL` VARCHAR；20. `CUSTOM_OBJECT` VARCHAR；21. `CUSTOM_EMAIL` VARCHAR；22. `CUSTOM_ACCEPTS_MARKETING` BOOLEAN；23. `CUSTOM_SHOPIFY_TAGS` VARCHAR；24. `_FIVETRAN_SYNCED` TIMESTAMP；25. `CUSTOM_CONSENT_FORM_ID` VARCHAR；26. `CUSTOM_SOURCE` VARCHAR；27. `CUSTOM_CONSENT_METHOD` VARCHAR；28. `CUSTOM_CONSENT` VARCHAR；29. `CUSTOM_GIFT_GIVER_NAME` VARCHAR；30. `CUSTOM_STATE` VARCHAR；31. `CUSTOM_FLOW` VARCHAR；32. `CUSTOM_GIFT_RECIPIENT_NAME` VARCHAR；33. `CUSTOM_LAST_SIGN_IN` TIMESTAMP；34. `CUSTOM_CONSENT_FORM_VERSION` BIGINT；35. `CUSTOM_CONSENT_TIMESTAMP` TIMESTAMP；36. `CUSTOM_MAIL_CHIMP_RATING` VARCHAR；37. `CUSTOM_GIFT_RECIPIENT_EMAIL` VARCHAR；38. `CUSTOM_GIFT_OPTIONS` VARCHAR；39. `CUSTOM_ADDRESS` VARCHAR；40. `CUSTOM_SUBSCRIPTION_EXPIRATION` VARCHAR；41. `CUSTOM_CITY` VARCHAR；42. `CUSTOM_ADDRESS_LINE_2` VARCHAR；43. `CUSTOM_ZIPCODE` BIGINT；44. `CUSTOM_EXPECTED_DATE_OF_NEXT_ORDER` DATE；45. `CUSTOM_SMS_ATTENTIVE_SIGNUP` BOOLEAN；46. `CUSTOM_PHONE` VARCHAR；47. `CUSTOM_AFTERPAY_ORDER` VARCHAR；48. `CUSTOM_PHONE_NUMBER_REGION` VARCHAR；49. `CUSTOM_NAME` VARCHAR；50. `CUSTOM_REFERRER_NAME` VARCHAR；51. `CUSTOM_REFERRER_EMAIL` VARCHAR；52. `CUSTOM_BIRTHDAY` VARCHAR；53. `CUSTOM_FIRST_PURCHASE_DATE_` TIMESTAMP；54. `CUSTOM_UNENGAGED` BOOLEAN；55. `CUSTOM_LANDING_PAGE_TAG` VARCHAR；56. `CUSTOM_FITNESS_GOAL` VARCHAR；57. `CUSTOM_AGE` VARCHAR；58. `CUSTOM_WORKOUT` VARCHAR；59. `CUSTOM_QUIZ` VARCHAR；60. `CUSTOM_BREAKFAST` VARCHAR；61. `CUSTOM_QUIZ_DATA` VARCHAR；62. `CUSTOM_RAF_SUBSCRIBE` BOOLEAN；63. `CUSTOM_SUPPRESS` BOOLEAN；64. `CUSTOM_SMS_CONSENT` BOOLEAN；65. `CUSTOM_GIFT_OPTION_DREAMBELT` VARCHAR；66. `CUSTOM_GIFT_OPTION_STARTER` VARCHAR；67. `CUSTOM_GIFT_OPTION_MACHINE` VARCHAR；68. `CUSTOM_LANDINGPAGE_TAG` VARCHAR；69. `LAST_EVENT_DATE` TIMESTAMP；70. `column069` TIMESTAMP；71. `column070` TIMESTAMP；72. `column071` BOOLEAN；73. `column072` VARCHAR；74. `column073` VARCHAR；75. `column074` VARCHAR；76. `column075` VARCHAR；77. `column076` VARCHAR；78. `column077` VARCHAR；79. `column078` VARCHAR；80. `column079` VARCHAR；81. `column080` DOUBLE；82. `column081` DOUBLE；83. `column082` BIGINT；84. `column083` VARCHAR；85. `column084` BIGINT；86. `column085` VARCHAR；87. `column086` VARCHAR；88. `column087` VARCHAR；89. `column088` VARCHAR；90. `column089` BOOLEAN；91. `column090` VARCHAR；92. `column091` TIMESTAMP；93. `column092` VARCHAR；94. `column093` VARCHAR；95. `column094` VARCHAR；96. `column095` VARCHAR；97. `column096` VARCHAR；98. `column097` VARCHAR；99. `column098` VARCHAR；100. `column099` VARCHAR；101. `column100` TIMESTAMP；102. `column101` VARCHAR；103. `column102` TIMESTAMP；104. `column103` VARCHAR；105. `column104` VARCHAR；106. `column105` VARCHAR；107. `column106` VARCHAR；108. `column107` VARCHAR；109. `column108` VARCHAR；110. `column109` VARCHAR；111. `column110` BIGINT；112. `column111` VARCHAR；113. `column112` BOOLEAN；114. `column113` VARCHAR；115. `column114` VARCHAR；116. `column115` VARCHAR；117. `column116` VARCHAR；118. `column117` VARCHAR；119. `column118` VARCHAR；120. `column119` VARCHAR；121. `column120` TIMESTAMP；122. `column121` BOOLEAN；123. `column122` VARCHAR；124. `column123` VARCHAR；125. `column124` VARCHAR；126. `column125` VARCHAR；127. `column126` VARCHAR；128. `column127` VARCHAR；129. `column128` VARCHAR；130. `column129` BOOLEAN；131. `column130` BOOLEAN；132. `column131` BOOLEAN；133. `column132` VARCHAR；134. `column133` VARCHAR；135. `column134` VARCHAR；136. `column135` VARCHAR；137. `column136` TIMESTAMP
- initial：1. `ID` VARCHAR；2. `UPDATED` VARCHAR；3. `CREATED` VARCHAR；4. `_FIVETRAN_DELETED` VARCHAR；5. `FIRST_NAME` VARCHAR；6. `LAST_NAME` VARCHAR；7. `ADDRESS_1` VARCHAR；8. `ADDRESS_2` VARCHAR；9. `TITLE` VARCHAR；10. `TIMEZONE` VARCHAR；11. `ORGANIZATION` VARCHAR；12. `REGION` VARCHAR；13. `LONGITUDE` VARCHAR；14. `LATITUDE` VARCHAR；15. `PHONE_NUMBER` VARCHAR；16. `COUNTRY` VARCHAR；17. `ZIP` VARCHAR；18. `CITY` VARCHAR；19. `EMAIL` VARCHAR；20. `CUSTOM_OBJECT` VARCHAR；21. `CUSTOM_EMAIL` VARCHAR；22. `CUSTOM_ACCEPTS_MARKETING` VARCHAR；23. `CUSTOM_SHOPIFY_TAGS` VARCHAR；24. `_FIVETRAN_SYNCED` VARCHAR；25. `CUSTOM_CONSENT_FORM_ID` VARCHAR；26. `CUSTOM_SOURCE` VARCHAR；27. `CUSTOM_CONSENT_METHOD` VARCHAR；28. `CUSTOM_CONSENT` VARCHAR；29. `CUSTOM_GIFT_GIVER_NAME` VARCHAR；30. `CUSTOM_STATE` VARCHAR；31. `CUSTOM_FLOW` VARCHAR；32. `CUSTOM_GIFT_RECIPIENT_NAME` VARCHAR；33. `CUSTOM_LAST_SIGN_IN` VARCHAR；34. `CUSTOM_CONSENT_FORM_VERSION` VARCHAR；35. `CUSTOM_CONSENT_TIMESTAMP` VARCHAR；36. `CUSTOM_MAIL_CHIMP_RATING` VARCHAR；37. `CUSTOM_GIFT_RECIPIENT_EMAIL` VARCHAR；38. `CUSTOM_GIFT_OPTIONS` VARCHAR；39. `CUSTOM_ADDRESS` VARCHAR；40. `CUSTOM_SUBSCRIPTION_EXPIRATION` VARCHAR；41. `CUSTOM_CITY` VARCHAR；42. `CUSTOM_ADDRESS_LINE_2` VARCHAR；43. `CUSTOM_ZIPCODE` VARCHAR；44. `CUSTOM_EXPECTED_DATE_OF_NEXT_ORDER` VARCHAR；45. `CUSTOM_SMS_ATTENTIVE_SIGNUP` VARCHAR；46. `CUSTOM_PHONE` VARCHAR；47. `CUSTOM_AFTERPAY_ORDER` VARCHAR；48. `CUSTOM_PHONE_NUMBER_REGION` VARCHAR；49. `CUSTOM_NAME` VARCHAR；50. `CUSTOM_REFERRER_NAME` VARCHAR；51. `CUSTOM_REFERRER_EMAIL` VARCHAR；52. `CUSTOM_BIRTHDAY` VARCHAR；53. `CUSTOM_FIRST_PURCHASE_DATE_` VARCHAR；54. `CUSTOM_UNENGAGED` VARCHAR；55. `CUSTOM_LANDING_PAGE_TAG` VARCHAR；56. `CUSTOM_FITNESS_GOAL` VARCHAR；57. `CUSTOM_AGE` VARCHAR；58. `CUSTOM_WORKOUT` VARCHAR；59. `CUSTOM_QUIZ` VARCHAR；60. `CUSTOM_BREAKFAST` VARCHAR；61. `CUSTOM_QUIZ_DATA` VARCHAR；62. `CUSTOM_RAF_SUBSCRIBE` VARCHAR；63. `CUSTOM_SUPPRESS` VARCHAR；64. `CUSTOM_SMS_CONSENT` VARCHAR；65. `CUSTOM_GIFT_OPTION_DREAMBELT` VARCHAR；66. `CUSTOM_GIFT_OPTION_STARTER` VARCHAR；67. `CUSTOM_GIFT_OPTION_MACHINE` VARCHAR；68. `CUSTOM_LANDINGPAGE_TAG` VARCHAR；69. `LAST_EVENT_DATE` VARCHAR
- agent：1. `ID` VARCHAR；2. `UPDATED` TIMESTAMP；3. `CREATED` TIMESTAMP；4. `_FIVETRAN_DELETED` BOOLEAN；5. `FIRST_NAME` VARCHAR；6. `LAST_NAME` VARCHAR；7. `ADDRESS_1` VARCHAR；8. `ADDRESS_2` VARCHAR；9. `TITLE` VARCHAR；10. `TIMEZONE` VARCHAR；11. `ORGANIZATION` VARCHAR；12. `REGION` VARCHAR；13. `LONGITUDE` DOUBLE；14. `LATITUDE` DOUBLE；15. `PHONE_NUMBER` VARCHAR；16. `COUNTRY` VARCHAR；17. `ZIP` BIGINT；18. `CITY` VARCHAR；19. `EMAIL` VARCHAR；20. `CUSTOM_OBJECT` VARCHAR；21. `CUSTOM_EMAIL` VARCHAR；22. `CUSTOM_ACCEPTS_MARKETING` BOOLEAN；23. `CUSTOM_SHOPIFY_TAGS` VARCHAR；24. `_FIVETRAN_SYNCED` TIMESTAMP；25. `CUSTOM_CONSENT_FORM_ID` VARCHAR；26. `CUSTOM_SOURCE` VARCHAR；27. `CUSTOM_CONSENT_METHOD` VARCHAR；28. `CUSTOM_CONSENT` VARCHAR；29. `CUSTOM_GIFT_GIVER_NAME` VARCHAR；30. `CUSTOM_STATE` VARCHAR；31. `CUSTOM_FLOW` VARCHAR；32. `CUSTOM_GIFT_RECIPIENT_NAME` VARCHAR；33. `CUSTOM_LAST_SIGN_IN` TIMESTAMP；34. `CUSTOM_CONSENT_FORM_VERSION` BIGINT；35. `CUSTOM_CONSENT_TIMESTAMP` TIMESTAMP；36. `CUSTOM_MAIL_CHIMP_RATING` VARCHAR；37. `CUSTOM_GIFT_RECIPIENT_EMAIL` VARCHAR；38. `CUSTOM_GIFT_OPTIONS` VARCHAR；39. `CUSTOM_ADDRESS` VARCHAR；40. `CUSTOM_SUBSCRIPTION_EXPIRATION` VARCHAR；41. `CUSTOM_CITY` VARCHAR；42. `CUSTOM_ADDRESS_LINE_2` VARCHAR；43. `CUSTOM_ZIPCODE` BIGINT；44. `CUSTOM_EXPECTED_DATE_OF_NEXT_ORDER` DATE；45. `CUSTOM_SMS_ATTENTIVE_SIGNUP` BOOLEAN；46. `CUSTOM_PHONE` VARCHAR；47. `CUSTOM_AFTERPAY_ORDER` VARCHAR；48. `CUSTOM_PHONE_NUMBER_REGION` VARCHAR；49. `CUSTOM_NAME` VARCHAR；50. `CUSTOM_REFERRER_NAME` VARCHAR；51. `CUSTOM_REFERRER_EMAIL` VARCHAR；52. `CUSTOM_BIRTHDAY` VARCHAR；53. `CUSTOM_FIRST_PURCHASE_DATE_` TIMESTAMP；54. `CUSTOM_UNENGAGED` BOOLEAN；55. `CUSTOM_LANDING_PAGE_TAG` VARCHAR；56. `CUSTOM_FITNESS_GOAL` VARCHAR；57. `CUSTOM_AGE` VARCHAR；58. `CUSTOM_WORKOUT` VARCHAR；59. `CUSTOM_QUIZ` VARCHAR；60. `CUSTOM_BREAKFAST` VARCHAR；61. `CUSTOM_QUIZ_DATA` VARCHAR；62. `CUSTOM_RAF_SUBSCRIBE` BOOLEAN；63. `CUSTOM_SUPPRESS` BOOLEAN；64. `CUSTOM_SMS_CONSENT` BOOLEAN；65. `CUSTOM_GIFT_OPTION_DREAMBELT` VARCHAR；66. `CUSTOM_GIFT_OPTION_STARTER` VARCHAR；67. `CUSTOM_GIFT_OPTION_MACHINE` VARCHAR；68. `CUSTOM_LANDINGPAGE_TAG` VARCHAR；69. `LAST_EVENT_DATE` TIMESTAMP；70. `column069` TIMESTAMP；71. `column070` TIMESTAMP；72. `column071` BOOLEAN；73. `column072` VARCHAR；74. `column073` VARCHAR；75. `column074` VARCHAR；76. `column075` VARCHAR；77. `column076` VARCHAR；78. `column077` VARCHAR；79. `column078` VARCHAR；80. `column079` VARCHAR；81. `column080` DOUBLE；82. `column081` DOUBLE；83. `column082` BIGINT；84. `column083` VARCHAR；85. `column084` BIGINT；86. `column085` VARCHAR；87. `column086` VARCHAR；88. `column087` VARCHAR；89. `column088` VARCHAR；90. `column089` BOOLEAN；91. `column090` VARCHAR；92. `column091` TIMESTAMP；93. `column092` VARCHAR；94. `column093` VARCHAR；95. `column094` VARCHAR；96. `column095` VARCHAR；97. `column096` VARCHAR；98. `column097` VARCHAR；99. `column098` VARCHAR；100. `column099` VARCHAR；101. `column100` TIMESTAMP；102. `column101` VARCHAR；103. `column102` TIMESTAMP；104. `column103` VARCHAR；105. `column104` VARCHAR；106. `column105` VARCHAR；107. `column106` VARCHAR；108. `column107` VARCHAR；109. `column108` VARCHAR；110. `column109` VARCHAR；111. `column110` BIGINT；112. `column111` VARCHAR；113. `column112` BOOLEAN；114. `column113` VARCHAR；115. `column114` VARCHAR；116. `column115` VARCHAR；117. `column116` VARCHAR；118. `column117` VARCHAR；119. `column118` VARCHAR；120. `column119` VARCHAR；121. `column120` TIMESTAMP；122. `column121` BOOLEAN；123. `column122` VARCHAR；124. `column123` VARCHAR；125. `column124` VARCHAR；126. `column125` VARCHAR；127. `column126` VARCHAR；128. `column127` VARCHAR；129. `column128` VARCHAR；130. `column129` BOOLEAN；131. `column130` BOOLEAN；132. `column131` BOOLEAN；133. `column132` VARCHAR；134. `column133` VARCHAR；135. `column134` VARCHAR；136. `column135` VARCHAR；137. `column136` TIMESTAMP

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| intermediate | int_klaviyo__events | 间接 | raw.person → staging.stg_klaviyo__person → intermediate.int_klaviyo__events |
| staging | stg_klaviyo__person | 直接 | raw.person → staging.stg_klaviyo__person |

来源：`015_raw_impl-021.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-025 raw.call_data_snowflake

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2500 | 2500 | False | True | ordered_columns_or_types_differ |
| gold_vs_agent | 2500 | 2500 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `account_id` VARCHAR；4. `annotation` DOUBLE；5. `answered_by` VARCHAR；6. `caller_name` DOUBLE；7. `created_at` VARCHAR；8. `direction` VARCHAR；9. `duration` BIGINT；10. `end_time` VARCHAR；11. `forwarded_from` DOUBLE；12. `"FROM"` BIGINT；13. `from_formatted` VARCHAR；14. `group_id` DOUBLE；15. `outgoing_caller_id` VARCHAR；16. `parent_call_id` DOUBLE；17. `price` DOUBLE；18. `price_unit` VARCHAR；19. `queue_time` BIGINT；20. `start_time` VARCHAR；21. `status` VARCHAR；22. `"TO"` BIGINT；23. `to_formatted` VARCHAR；24. `trunk_id` DOUBLE；25. `updated_at` VARCHAR
- initial：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `account_id` VARCHAR；4. `annotation` DOUBLE；5. `answered_by` VARCHAR；6. `caller_name` DOUBLE；7. `created_at` VARCHAR；8. `direction` VARCHAR；9. `duration` BIGINT；10. `end_time` VARCHAR；11. `forwarded_from` DOUBLE；12. `"""FROM"""` BIGINT；13. `from_formatted` VARCHAR；14. `group_id` DOUBLE；15. `outgoing_caller_id` VARCHAR；16. `parent_call_id` DOUBLE；17. `price` DOUBLE；18. `price_unit` VARCHAR；19. `queue_time` BIGINT；20. `start_time` VARCHAR；21. `status` VARCHAR；22. `"""TO"""` BIGINT；23. `to_formatted` VARCHAR；24. `trunk_id` DOUBLE；25. `updated_at` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `account_id` VARCHAR；4. `annotation` DOUBLE；5. `answered_by` VARCHAR；6. `caller_name` DOUBLE；7. `created_at` VARCHAR；8. `direction` VARCHAR；9. `duration` BIGINT；10. `end_time` VARCHAR；11. `forwarded_from` DOUBLE；12. `"FROM"` BIGINT；13. `from_formatted` VARCHAR；14. `group_id` DOUBLE；15. `outgoing_caller_id` VARCHAR；16. `parent_call_id` DOUBLE；17. `price` DOUBLE；18. `price_unit` VARCHAR；19. `queue_time` BIGINT；20. `start_time` VARCHAR；21. `status` VARCHAR；22. `"TO"` BIGINT；23. `to_formatted` VARCHAR；24. `trunk_id` DOUBLE；25. `updated_at` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-025.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-025 raw.message_data_snowflake

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2500 | 2500 | False | True | ordered_columns_or_types_differ |
| gold_vs_agent | 2500 | 2500 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `account_id` VARCHAR；4. `body` VARCHAR；5. `created_at` VARCHAR；6. `date_sent` VARCHAR；7. `direction` VARCHAR；8. `error_code` DOUBLE；9. `error_message` DOUBLE；10. `"FROM"` BIGINT；11. `messaging_service_sid` VARCHAR；12. `num_media` BIGINT；13. `num_segments` BIGINT；14. `price` DOUBLE；15. `price_unit` VARCHAR；16. `status` VARCHAR；17. `"TO"` BIGINT；18. `updated_at` VARCHAR
- initial：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `account_id` VARCHAR；4. `body` VARCHAR；5. `created_at` VARCHAR；6. `date_sent` VARCHAR；7. `direction` VARCHAR；8. `error_code` DOUBLE；9. `error_message` DOUBLE；10. `"""FROM"""` BIGINT；11. `messaging_service_sid` VARCHAR；12. `num_media` BIGINT；13. `num_segments` BIGINT；14. `price` DOUBLE；15. `price_unit` VARCHAR；16. `status` VARCHAR；17. `"""TO"""` BIGINT；18. `updated_at` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `account_id` VARCHAR；4. `body` VARCHAR；5. `created_at` VARCHAR；6. `date_sent` VARCHAR；7. `direction` VARCHAR；8. `error_code` DOUBLE；9. `error_message` DOUBLE；10. `"FROM"` BIGINT；11. `messaging_service_sid` VARCHAR；12. `num_media` BIGINT；13. `num_segments` BIGINT；14. `price` DOUBLE；15. `price_unit` VARCHAR；16. `status` VARCHAR；17. `"TO"` BIGINT；18. `updated_at` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-025.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-028 raw.channel_basic_a_2

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 150 | 表不存在 | 未比较 | 未比较 | initial_missing_table |
| gold_vs_agent | 150 | 表不存在 | 未比较 | 未比较 | agent_missing_table |

**按原顺序的列名与类型**

- gold：1. `date` DATE；2. `channel_id` VARCHAR；3. `video_id` VARCHAR；4. `channel_title` VARCHAR；5. `video_title` VARCHAR；6. `deleted` BOOLEAN；7. `_fivetran_synced` DATE；8. `average_view_duration_seconds` BIGINT；9. `average_view_duration_percentage` BIGINT；10. `views` BIGINT；11. `likes` BIGINT；12. `dislikes` BIGINT；13. `shares` BIGINT；14. `subscribers_gained` BIGINT；15. `subscribers_lost` BIGINT；16. `estimated_minutes_watched` BIGINT；17. `estimated_red_minutes_watched` BIGINT；18. `annotation_click_through_rate` DOUBLE；19. `annotation_close_rate` DOUBLE；20. `annotation_impressions` BIGINT；21. `annotation_clickable_impressions` BIGINT；22. `annotation_closable_impressions` BIGINT；23. `annotation_clicks` BIGINT；24. `annotation_closes` BIGINT；25. `viewers` BIGINT；26. `views_percentage` BIGINT；27. `average_time_in_video` BIGINT；28. `card_click_rate` DOUBLE；29. `card_impressions` BIGINT；30. `card_clickable_impressions` BIGINT；31. `card_clicks` BIGINT；32. `playlist_starts` BIGINT；33. `estimated_minutes_watched_from_playlists` BIGINT；34. `average_time_in_playlist` BIGINT
- initial：表不存在
- agent：表不存在

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-028.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-028 raw.channel_demographics_a_1

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 9450 | 表不存在 | 未比较 | 未比较 | initial_missing_table |
| gold_vs_agent | 9450 | 表不存在 | 未比较 | 未比较 | agent_missing_table |

**按原顺序的列名与类型**

- gold：1. `date` DATE；2. `channel_id` VARCHAR；3. `video_id` VARCHAR；4. `deleted` BOOLEAN；5. `country_code` VARCHAR；6. `age_group` VARCHAR；7. `gender` VARCHAR；8. `views_percentage` DOUBLE；9. `estimated_minutes_watched_percentage` DOUBLE；10. `_fivetran_synced` DATE
- initial：表不存在
- agent：表不存在

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-028.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-028 raw.video

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 5 | 表不存在 | 未比较 | 未比较 | initial_missing_table |
| gold_vs_agent | 5 | 表不存在 | 未比较 | 未比较 | agent_missing_table |

**按原顺序的列名与类型**

- gold：1. `video_id` VARCHAR；2. `id` VARCHAR；3. `deleted` BOOLEAN；4. `_fivetran_synced` DATE；5. `snippet_published_at` DATE；6. `snippet_channel_id` VARCHAR；7. `snippet_title` VARCHAR；8. `snippet_description` VARCHAR；9. `snippet_thumbnails` VARCHAR；10. `snippet_channel_title` VARCHAR；11. `snippet_tags` VARCHAR；12. `snippet_category_id` VARCHAR；13. `snippet_live_broadcast_content` VARCHAR；14. `snippet_localized_title` VARCHAR；15. `snippet_localized_description` VARCHAR；16. `snippet_default_language` VARCHAR；17. `snippet_default_audio_language` VARCHAR；18. `content_details_duration` VARCHAR；19. `content_details_dimension` VARCHAR；20. `content_details_definition` VARCHAR；21. `content_details_caption` VARCHAR；22. `content_details_licensed_content` VARCHAR；23. `content_details_region_restriction_blocked` VARCHAR；24. `content_details_region_restriction_allowed` VARCHAR；25. `content_details_content_rating` VARCHAR；26. `content_details_projection` VARCHAR；27. `content_details_has_custom_thumbnail` VARCHAR；28. `status_upload_status` VARCHAR；29. `status_failure_reason` VARCHAR；30. `status_rejection_reason` VARCHAR；31. `status_privacy_status` VARCHAR；32. `status_publish_at` VARCHAR；33. `status_license` VARCHAR；34. `status_embeddable` VARCHAR；35. `status_public_stats_viewable` VARCHAR；36. `statistics_view_count` VARCHAR；37. `statistics_like_count` VARCHAR；38. `statistics_dislike_count` VARCHAR；39. `statistics_favorite_count` VARCHAR；40. `statistics_comment_count` VARCHAR；41. `statistics_thumbnail_url` VARCHAR
- initial：表不存在
- agent：表不存在

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-028.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-028 raw.youtube_channel_basic_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 表不存在 | 3500 | 未比较 | 未比较 | gold_missing_table |
| gold_vs_agent | 表不存在 | 3500 | 未比较 | 未比较 | gold_missing_table |

**按原顺序的列名与类型**

- gold：表不存在
- initial：1. `_fivetran_id` VARCHAR；2. `date` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `annotation_click_through_rate` DOUBLE；5. `annotation_clickable_impressions` BIGINT；6. `annotation_clicks` BIGINT；7. `annotation_closable_impressions` BIGINT；8. `annotation_close_rate` DOUBLE；9. `annotation_closes` BIGINT；10. `annotation_impressions` BIGINT；11. `average_view_duration_percentage` DOUBLE；12. `average_view_duration_seconds` DOUBLE；13. `card_click_rate` DOUBLE；14. `card_clicks` BIGINT；15. `card_impressions` BIGINT；16. `card_teaser_click_rate` DOUBLE；17. `card_teaser_clicks` BIGINT；18. `card_teaser_impressions` BIGINT；19. `channel_id` VARCHAR；20. `comments` BIGINT；21. `country_code` VARCHAR；22. `dislikes` BIGINT；23. `likes` BIGINT；24. `live_or_on_demand` VARCHAR；25. `red_views` BIGINT；26. `red_watch_time_minutes` DOUBLE；27. `shares` BIGINT；28. `subscribed_status` VARCHAR；29. `subscribers_gained` BIGINT；30. `subscribers_lost` BIGINT；31. `video_id` VARCHAR；32. `videos_added_to_playlists` BIGINT；33. `videos_removed_from_playlists` BIGINT；34. `views` BIGINT；35. `watch_time_minutes` DOUBLE
- agent：1. `_fivetran_id` VARCHAR；2. `date` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `annotation_click_through_rate` DOUBLE；5. `annotation_clickable_impressions` BIGINT；6. `annotation_clicks` BIGINT；7. `annotation_closable_impressions` BIGINT；8. `annotation_close_rate` DOUBLE；9. `annotation_closes` BIGINT；10. `annotation_impressions` BIGINT；11. `average_view_duration_percentage` DOUBLE；12. `average_view_duration_seconds` DOUBLE；13. `card_click_rate` DOUBLE；14. `card_clicks` BIGINT；15. `card_impressions` BIGINT；16. `card_teaser_click_rate` DOUBLE；17. `card_teaser_clicks` BIGINT；18. `card_teaser_impressions` BIGINT；19. `channel_id` VARCHAR；20. `comments` BIGINT；21. `country_code` VARCHAR；22. `dislikes` BIGINT；23. `likes` BIGINT；24. `live_or_on_demand` VARCHAR；25. `red_views` BIGINT；26. `red_watch_time_minutes` DOUBLE；27. `shares` BIGINT；28. `subscribed_status` VARCHAR；29. `subscribers_gained` BIGINT；30. `subscribers_lost` BIGINT；31. `video_id` VARCHAR；32. `videos_added_to_playlists` BIGINT；33. `videos_removed_from_playlists` BIGINT；34. `views` BIGINT；35. `watch_time_minutes` DOUBLE

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_youtube__channel_basic | 直接 | raw.youtube_channel_basic_data → staging.stg_youtube__channel_basic |

来源：`015_raw_impl-028.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-028 raw.youtube_channel_demographics_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 表不存在 | 2509 | 未比较 | 未比较 | gold_missing_table |
| gold_vs_agent | 表不存在 | 2509 | 未比较 | 未比较 | gold_missing_table |

**按原顺序的列名与类型**

- gold：表不存在
- initial：1. `_fivetran_id` VARCHAR；2. `date` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `age_group` VARCHAR；5. `channel_id` VARCHAR；6. `country_code` VARCHAR；7. `gender` VARCHAR；8. `live_or_on_demand` VARCHAR；9. `subscribed_status` VARCHAR；10. `video_id` VARCHAR；11. `views_percentage` DOUBLE
- agent：1. `_fivetran_id` VARCHAR；2. `date` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `age_group` VARCHAR；5. `channel_id` VARCHAR；6. `country_code` VARCHAR；7. `gender` VARCHAR；8. `live_or_on_demand` VARCHAR；9. `subscribed_status` VARCHAR；10. `video_id` VARCHAR；11. `views_percentage` DOUBLE

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_youtube__channel_demographics | 直接 | raw.youtube_channel_demographics_data → staging.stg_youtube__channel_demographics |

来源：`015_raw_impl-028.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-028 raw.youtube_video_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 表不存在 | 2501 | 未比较 | 未比较 | gold_missing_table |
| gold_vs_agent | 表不存在 | 2501 | 未比较 | 未比较 | gold_missing_table |

**按原顺序的列名与类型**

- gold：表不存在
- initial：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `content_details_caption` BOOLEAN；4. `content_details_definition` VARCHAR；5. `content_details_dimension` VARCHAR；6. `content_details_duration` VARCHAR；7. `content_details_has_custom_thumbnail` BOOLEAN；8. `content_details_licensed_content` BOOLEAN；9. `content_details_projection` VARCHAR；10. `content_details_region_restriction` DOUBLE；11. `etag` VARCHAR；12. `kind` VARCHAR；13. `player_embed_height` DOUBLE；14. `player_embed_html` VARCHAR；15. `player_embed_width` DOUBLE；16. `privacy_status` VARCHAR；17. `snippet_category_id` BIGINT；18. `snippet_channel_id` VARCHAR；19. `snippet_channel_title` VARCHAR；20. `snippet_default_audio_language` DOUBLE；21. `snippet_default_language` DOUBLE；22. `snippet_description` VARCHAR；23. `snippet_live_broadcast_content` VARCHAR；24. `snippet_localized` VARCHAR；25. `snippet_published_at` VARCHAR；26. `snippet_tags` DOUBLE；27. `snippet_thumbnails` DOUBLE；28. `snippet_title` VARCHAR；29. `statistics_comment_count` BIGINT；30. `statistics_dislike_count` BIGINT；31. `statistics_favorite_count` BIGINT；32. `statistics_like_count` BIGINT；33. `statistics_view_count` BIGINT；34. `status_embeddable` BOOLEAN；35. `status_failure_reason` DOUBLE；36. `status_license` VARCHAR；37. `status_made_for_kids` BOOLEAN；38. `status_public_stats_viewable` BOOLEAN；39. `status_publish_at` DOUBLE；40. `status_rejection_reason` DOUBLE；41. `status_self_declared_made_for_kids` BOOLEAN；42. `upload_status` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `content_details_caption` BOOLEAN；4. `content_details_definition` VARCHAR；5. `content_details_dimension` VARCHAR；6. `content_details_duration` VARCHAR；7. `content_details_has_custom_thumbnail` BOOLEAN；8. `content_details_licensed_content` BOOLEAN；9. `content_details_projection` VARCHAR；10. `content_details_region_restriction` DOUBLE；11. `etag` VARCHAR；12. `kind` VARCHAR；13. `player_embed_height` DOUBLE；14. `player_embed_html` VARCHAR；15. `player_embed_width` DOUBLE；16. `privacy_status` VARCHAR；17. `snippet_category_id` BIGINT；18. `snippet_channel_id` VARCHAR；19. `snippet_channel_title` VARCHAR；20. `snippet_default_audio_language` DOUBLE；21. `snippet_default_language` DOUBLE；22. `snippet_description` VARCHAR；23. `snippet_live_broadcast_content` VARCHAR；24. `snippet_localized` VARCHAR；25. `snippet_published_at` VARCHAR；26. `snippet_tags` DOUBLE；27. `snippet_thumbnails` DOUBLE；28. `snippet_title` VARCHAR；29. `statistics_comment_count` BIGINT；30. `statistics_dislike_count` BIGINT；31. `statistics_favorite_count` BIGINT；32. `statistics_like_count` BIGINT；33. `statistics_view_count` BIGINT；34. `status_embeddable` BOOLEAN；35. `status_failure_reason` DOUBLE；36. `status_license` VARCHAR；37. `status_made_for_kids` BOOLEAN；38. `status_public_stats_viewable` BOOLEAN；39. `status_publish_at` DOUBLE；40. `status_rejection_reason` DOUBLE；41. `status_self_declared_made_for_kids` BOOLEAN；42. `upload_status` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| intermediate | int_youtube__video | 间接 | raw.youtube_video_data → staging.stg_youtube__video → intermediate.int_youtube__video |
| staging | stg_youtube__video | 直接 | raw.youtube_video_data → staging.stg_youtube__video |

来源：`015_raw_impl-028.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-029 raw.brand_data_postgres

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1 | 1 | False | True | ordered_columns_or_types_differ |
| gold_vs_agent | 1 | 1 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `active` VARCHAR；5. `brand_url` VARCHAR；6. `default` VARCHAR；7. `has_help_center` VARCHAR；8. `help_center_state` VARCHAR；9. `logo_content_type` VARCHAR；10. `logo_content_url` VARCHAR；11. `logo_deleted` VARCHAR；12. `logo_file_name` VARCHAR；13. `logo_height` VARCHAR；14. `logo_id` VARCHAR；15. `logo_inline` VARCHAR；16. `logo_mapped_content_url` VARCHAR；17. `logo_size` VARCHAR；18. `logo_url` VARCHAR；19. `logo_width` VARCHAR；20. `name` VARCHAR；21. `subdomain` VARCHAR；22. `url` VARCHAR
- initial：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `active` VARCHAR；5. `brand_url` VARCHAR；6. `"default"` VARCHAR；7. `has_help_center` VARCHAR；8. `help_center_state` VARCHAR；9. `logo_content_type` VARCHAR；10. `logo_content_url` VARCHAR；11. `logo_deleted` VARCHAR；12. `logo_file_name` VARCHAR；13. `logo_height` VARCHAR；14. `logo_id` VARCHAR；15. `logo_inline` VARCHAR；16. `logo_mapped_content_url` VARCHAR；17. `logo_size` VARCHAR；18. `logo_url` VARCHAR；19. `logo_width` VARCHAR；20. `name` VARCHAR；21. `subdomain` VARCHAR；22. `url` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `active` VARCHAR；5. `brand_url` VARCHAR；6. `default` VARCHAR；7. `has_help_center` VARCHAR；8. `help_center_state` VARCHAR；9. `logo_content_type` VARCHAR；10. `logo_content_url` VARCHAR；11. `logo_deleted` VARCHAR；12. `logo_file_name` VARCHAR；13. `logo_height` VARCHAR；14. `logo_id` VARCHAR；15. `logo_inline` VARCHAR；16. `logo_mapped_content_url` VARCHAR；17. `logo_size` VARCHAR；18. `logo_url` VARCHAR；19. `logo_width` VARCHAR；20. `name` VARCHAR；21. `subdomain` VARCHAR；22. `url` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-029.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-029 raw.user_data_snowflake

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 10 | 10 | False | True | ordered_columns_or_types_differ |
| gold_vs_agent | 10 | 10 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `ACTIVE` VARCHAR；4. `alias` VARCHAR；5. `authenticity_token` VARCHAR；6. `chat_only` VARCHAR；7. `created_at` VARCHAR；8. `details` VARCHAR；9. `email` VARCHAR；10. `external_id` VARCHAR；11. `last_login_at` VARCHAR；12. `locale` VARCHAR；13. `locale_id` VARCHAR；14. `moderator` VARCHAR；15. `name` VARCHAR；16. `notes` VARCHAR；17. `only_private_comments` VARCHAR；18. `organization_id` VARCHAR；19. `phone` VARCHAR；20. `remote_photo_url` VARCHAR；21. `restricted_agent` VARCHAR；22. `role` VARCHAR；23. `shared` VARCHAR；24. `shared_agent` VARCHAR；25. `signature` VARCHAR；26. `suspended` VARCHAR；27. `ticket_restriction` VARCHAR；28. `time_zone` VARCHAR；29. `two_factor_auth_enabled` VARCHAR；30. `updated_at` VARCHAR；31. `url` VARCHAR；32. `verified` VARCHAR
- initial：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `"ACTIVE"` VARCHAR；4. `alias` VARCHAR；5. `authenticity_token` VARCHAR；6. `chat_only` VARCHAR；7. `created_at` VARCHAR；8. `details` VARCHAR；9. `email` VARCHAR；10. `external_id` VARCHAR；11. `last_login_at` VARCHAR；12. `locale` VARCHAR；13. `locale_id` VARCHAR；14. `moderator` VARCHAR；15. `name` VARCHAR；16. `notes` VARCHAR；17. `only_private_comments` VARCHAR；18. `organization_id` VARCHAR；19. `phone` VARCHAR；20. `remote_photo_url` VARCHAR；21. `restricted_agent` VARCHAR；22. `role` VARCHAR；23. `shared` VARCHAR；24. `shared_agent` VARCHAR；25. `signature` VARCHAR；26. `suspended` VARCHAR；27. `ticket_restriction` VARCHAR；28. `time_zone` VARCHAR；29. `two_factor_auth_enabled` VARCHAR；30. `updated_at` VARCHAR；31. `url` VARCHAR；32. `verified` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_synced` VARCHAR；3. `ACTIVE` VARCHAR；4. `alias` VARCHAR；5. `authenticity_token` VARCHAR；6. `chat_only` VARCHAR；7. `created_at` VARCHAR；8. `details` VARCHAR；9. `email` VARCHAR；10. `external_id` VARCHAR；11. `last_login_at` VARCHAR；12. `locale` VARCHAR；13. `locale_id` VARCHAR；14. `moderator` VARCHAR；15. `name` VARCHAR；16. `notes` VARCHAR；17. `only_private_comments` VARCHAR；18. `organization_id` VARCHAR；19. `phone` VARCHAR；20. `remote_photo_url` VARCHAR；21. `restricted_agent` VARCHAR；22. `role` VARCHAR；23. `shared` VARCHAR；24. `shared_agent` VARCHAR；25. `signature` VARCHAR；26. `suspended` VARCHAR；27. `ticket_restriction` VARCHAR；28. `time_zone` VARCHAR；29. `two_factor_auth_enabled` VARCHAR；30. `updated_at` VARCHAR；31. `url` VARCHAR；32. `verified` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| — | 无可追溯的待标注下游 | — | — |

来源：`015_raw_impl-029.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-030 raw.zuora_account_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 7504 | 7504 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 7504 | 7504 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `account_number` VARCHAR；5. `additional_email_addresses` VARCHAR；6. `allow_invoice_edit` VARCHAR；7. `auto_pay` VARCHAR；8. `balance` VARCHAR；9. `bcd_setting_option` VARCHAR；10. `bill_cycle_day` VARCHAR；11. `bill_to_contact_id` VARCHAR；12. `bill_to_id` VARCHAR；13. `communication_profile_id` VARCHAR；14. `created_by_id` VARCHAR；15. `created_date` VARCHAR；16. `credit_balance` VARCHAR；17. `crm_id` VARCHAR；18. `currency` VARCHAR；19. `customer_service_rep_name` VARCHAR；20. `default_payment_method_id` VARCHAR；21. `invoice_delivery_prefs_email` VARCHAR；22. `invoice_delivery_prefs_print` VARCHAR；23. `invoice_template_id` VARCHAR；24. `last_invoice_date` VARCHAR；25. `mrr` VARCHAR；26. `name` VARCHAR；27. `notes` VARCHAR；28. `parent_account_id` VARCHAR；29. `parent_id` VARCHAR；30. `payment_gateway` VARCHAR；31. `payment_term` VARCHAR；32. `purchase_order_number` VARCHAR；33. `sales_rep_name` VARCHAR；34. `sequence_set_id` VARCHAR；35. `sold_to_contact_id` VARCHAR；36. `sold_to_id` VARCHAR；37. `status` VARCHAR；38. `tax_company_code` VARCHAR；39. `tax_exempt_certificate_id` VARCHAR；40. `tax_exempt_certificate_type` VARCHAR；41. `tax_exempt_description` VARCHAR；42. `tax_exempt_effective_date` VARCHAR；43. `tax_exempt_entity_use_code` VARCHAR；44. `tax_exempt_expiration_date` VARCHAR；45. `tax_exempt_issuing_jurisdiction` VARCHAR；46. `tax_exempt_status` VARCHAR；47. `testcustom_1_c` VARCHAR；48. `testcustom_2_c` VARCHAR；49. `total_debit_memo_balance` VARCHAR；50. `total_invoice_balance` VARCHAR；51. `unapplied_balance` VARCHAR；52. `unapplied_credit_memo_amount` VARCHAR；53. `updated_by_id` VARCHAR；54. `updated_date` VARCHAR；55. `vatid` VARCHAR；56. `batch` VARCHAR
- initial：1. `id,_fivetran_deleted,_fivetran_synced,account_number,additional_email_addresses,allow_invoice_edit,auto_pay,balance,bcd_setting_option,bill_cycle_day,bill_to_contact_id,bill_to_id,communication_profile_id,created_by_id,created_date,credit_balance,crm_id,currency,customer_service_rep_name,default_payment_method_id,invoice_delivery_prefs_email,invoice_delivery_prefs_print,invoice_template_id,last_invoice_date,mrr,name,notes,parent_account_id,parent_id,payment_gateway,payment_term,purchase_order_number,sales_rep_name,sequence_set_id,sold_to_contact_id,sold_to_id,status,tax_company_code,tax_exempt_certificate_id,tax_exempt_certificate_type,tax_exempt_description,tax_exempt_effective_date,tax_exempt_entity_use_code,tax_exempt_expiration_date,tax_exempt_issuing_jurisdiction,tax_exempt_status,testcustom_1_c,testcustom_2_c,total_debit_memo_balance,total_invoice_balance,unapplied_balance,unapplied_credit_memo_amount,updated_by_id,updated_date,vatid,batch` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `account_number` VARCHAR；5. `additional_email_addresses` VARCHAR；6. `allow_invoice_edit` VARCHAR；7. `auto_pay` VARCHAR；8. `balance` VARCHAR；9. `bcd_setting_option` VARCHAR；10. `bill_cycle_day` VARCHAR；11. `bill_to_contact_id` VARCHAR；12. `bill_to_id` VARCHAR；13. `communication_profile_id` VARCHAR；14. `created_by_id` VARCHAR；15. `created_date` VARCHAR；16. `credit_balance` VARCHAR；17. `crm_id` VARCHAR；18. `currency` VARCHAR；19. `customer_service_rep_name` VARCHAR；20. `default_payment_method_id` VARCHAR；21. `invoice_delivery_prefs_email` VARCHAR；22. `invoice_delivery_prefs_print` VARCHAR；23. `invoice_template_id` VARCHAR；24. `last_invoice_date` VARCHAR；25. `mrr` VARCHAR；26. `name` VARCHAR；27. `notes` VARCHAR；28. `parent_account_id` VARCHAR；29. `parent_id` VARCHAR；30. `payment_gateway` VARCHAR；31. `payment_term` VARCHAR；32. `purchase_order_number` VARCHAR；33. `sales_rep_name` VARCHAR；34. `sequence_set_id` VARCHAR；35. `sold_to_contact_id` VARCHAR；36. `sold_to_id` VARCHAR；37. `status` VARCHAR；38. `tax_company_code` VARCHAR；39. `tax_exempt_certificate_id` VARCHAR；40. `tax_exempt_certificate_type` VARCHAR；41. `tax_exempt_description` VARCHAR；42. `tax_exempt_effective_date` VARCHAR；43. `tax_exempt_entity_use_code` VARCHAR；44. `tax_exempt_expiration_date` VARCHAR；45. `tax_exempt_issuing_jurisdiction` VARCHAR；46. `tax_exempt_status` VARCHAR；47. `testcustom_1_c` VARCHAR；48. `testcustom_2_c` VARCHAR；49. `total_debit_memo_balance` VARCHAR；50. `total_invoice_balance` VARCHAR；51. `unapplied_balance` VARCHAR；52. `unapplied_credit_memo_amount` VARCHAR；53. `updated_by_id` VARCHAR；54. `updated_date` VARCHAR；55. `vatid` VARCHAR；56. `batch` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | zuora__account_overview | 间接 | raw.zuora_account_data → staging.stg_zuora__account → intermediate.int_zuora__account_current → marts.zuora__account_overview |
| staging | stg_zuora__account | 直接 | raw.zuora_account_data → staging.stg_zuora__account |

来源：`015_raw_impl-030.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-030 raw.zuora_amendment_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 505 | 505 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 505 | 505 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `auto_renew` VARCHAR；5. `booking_date` VARCHAR；6. `code` VARCHAR；7. `contract_effective_date` VARCHAR；8. `created_by_id` VARCHAR；9. `created_date` VARCHAR；10. `current_term` VARCHAR；11. `current_term_period_type` VARCHAR；12. `customer_acceptance_date` VARCHAR；13. `description` VARCHAR；14. `effective_date` VARCHAR；15. `effective_policy` VARCHAR；16. `name` VARCHAR；17. `new_rate_plan_id` VARCHAR；18. `removed_rate_plan_id` VARCHAR；19. `renewal_setting` VARCHAR；20. `renewal_term` VARCHAR；21. `renewal_term_period_type` VARCHAR；22. `resume_date` VARCHAR；23. `service_activation_date` VARCHAR；24. `specific_update_date` VARCHAR；25. `status` VARCHAR；26. `sub_type` VARCHAR；27. `subscription_id` VARCHAR；28. `suspend_date` VARCHAR；29. `term_start_date` VARCHAR；30. `term_type` VARCHAR；31. `type` VARCHAR；32. `updated_by_id` VARCHAR；33. `updated_date` VARCHAR
- initial：1. `id,_fivetran_deleted,_fivetran_synced,auto_renew,booking_date,code,contract_effective_date,created_by_id,created_date,current_term,current_term_period_type,customer_acceptance_date,description,effective_date,effective_policy,name,new_rate_plan_id,removed_rate_plan_id,renewal_setting,renewal_term,renewal_term_period_type,resume_date,service_activation_date,specific_update_date,status,sub_type,subscription_id,suspend_date,term_start_date,term_type,type,updated_by_id,updated_date` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `auto_renew` VARCHAR；5. `booking_date` VARCHAR；6. `code` VARCHAR；7. `contract_effective_date` VARCHAR；8. `created_by_id` VARCHAR；9. `created_date` VARCHAR；10. `current_term` VARCHAR；11. `current_term_period_type` VARCHAR；12. `customer_acceptance_date` VARCHAR；13. `description` VARCHAR；14. `effective_date` VARCHAR；15. `effective_policy` VARCHAR；16. `name` VARCHAR；17. `new_rate_plan_id` VARCHAR；18. `removed_rate_plan_id` VARCHAR；19. `renewal_setting` VARCHAR；20. `renewal_term` VARCHAR；21. `renewal_term_period_type` VARCHAR；22. `resume_date` VARCHAR；23. `service_activation_date` VARCHAR；24. `specific_update_date` VARCHAR；25. `status` VARCHAR；26. `sub_type` VARCHAR；27. `subscription_id` VARCHAR；28. `suspend_date` VARCHAR；29. `term_start_date` VARCHAR；30. `term_type` VARCHAR；31. `type` VARCHAR；32. `updated_by_id` VARCHAR；33. `updated_date` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| staging | stg_zuora__amendment | 直接 | raw.zuora_amendment_data → staging.stg_zuora__amendment |

来源：`015_raw_impl-030.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-030 raw.zuora_contact_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 7504 | 7504 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 7504 | 7504 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `account_id` VARCHAR；5. `address_1` VARCHAR；6. `address_2` VARCHAR；7. `city` VARCHAR；8. `country` VARCHAR；9. `county` VARCHAR；10. `created_by_id` VARCHAR；11. `created_date` VARCHAR；12. `description` VARCHAR；13. `fax` VARCHAR；14. `first_name` VARCHAR；15. `home_phone` VARCHAR；16. `last_name` VARCHAR；17. `mobile_phone` VARCHAR；18. `nick_name` VARCHAR；19. `other_phone` VARCHAR；20. `other_phone_type` VARCHAR；21. `personal_email` VARCHAR；22. `postal_code` VARCHAR；23. `state` VARCHAR；24. `tax_region` VARCHAR；25. `updated_by_id` VARCHAR；26. `updated_date` VARCHAR；27. `work_email` VARCHAR；28. `work_phone` VARCHAR
- initial：1. `id,_fivetran_deleted,_fivetran_synced,account_id,address_1,address_2,city,country,county,created_by_id,created_date,description,fax,first_name,home_phone,last_name,mobile_phone,nick_name,other_phone,other_phone_type,personal_email,postal_code,state,tax_region,updated_by_id,updated_date,work_email,work_phone` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `account_id` VARCHAR；5. `address_1` VARCHAR；6. `address_2` VARCHAR；7. `city` VARCHAR；8. `country` VARCHAR；9. `county` VARCHAR；10. `created_by_id` VARCHAR；11. `created_date` VARCHAR；12. `description` VARCHAR；13. `fax` VARCHAR；14. `first_name` VARCHAR；15. `home_phone` VARCHAR；16. `last_name` VARCHAR；17. `mobile_phone` VARCHAR；18. `nick_name` VARCHAR；19. `other_phone` VARCHAR；20. `other_phone_type` VARCHAR；21. `personal_email` VARCHAR；22. `postal_code` VARCHAR；23. `state` VARCHAR；24. `tax_region` VARCHAR；25. `updated_by_id` VARCHAR；26. `updated_date` VARCHAR；27. `work_email` VARCHAR；28. `work_phone` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | zuora__account_overview | 间接 | raw.zuora_contact_data → staging.stg_zuora__contact → intermediate.int_zuora__contact_current → marts.zuora__account_overview |
| staging | stg_zuora__contact | 直接 | raw.zuora_contact_data → staging.stg_zuora__contact |

来源：`015_raw_impl-030.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-030 raw.zuora_invoice_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 2004 | 2004 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 2004 | 2004 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `account_id` VARCHAR；5. `adjustment_amount` VARCHAR；6. `amount` VARCHAR；7. `amount_currency_rounding` VARCHAR；8. `amount_home_currency` VARCHAR；9. `amount_without_tax` VARCHAR；10. `amount_without_tax_currency_rounding` VARCHAR；11. `amount_without_tax_home_currency` VARCHAR；12. `auto_pay` VARCHAR；13. `balance` VARCHAR；14. `bill_to_contact_id` VARCHAR；15. `comments` VARCHAR；16. `created_by_id` VARCHAR；17. `created_date` VARCHAR；18. `credit_balance_adjustment_amount` VARCHAR；19. `default_payment_method_id` VARCHAR；20. `due_date` VARCHAR；21. `exchange_rate` VARCHAR；22. `exchange_rate_date` VARCHAR；23. `home_currency` VARCHAR；24. `includes_one_time` VARCHAR；25. `includes_recurring` VARCHAR；26. `includes_usage` VARCHAR；27. `invoice_date` VARCHAR；28. `invoice_number` VARCHAR；29. `last_email_sent_date` VARCHAR；30. `parent_account_id` VARCHAR；31. `payment_amount` VARCHAR；32. `payment_term` VARCHAR；33. `posted_by` VARCHAR；34. `posted_date` VARCHAR；35. `provider_exchange_rate_date` VARCHAR；36. `refund_amount` VARCHAR；37. `reversed` VARCHAR；38. `sold_to_contact_id` VARCHAR；39. `source` VARCHAR；40. `source_id` VARCHAR；41. `source_type` VARCHAR；42. `status` VARCHAR；43. `target_date` VARCHAR；44. `tax_amount` VARCHAR；45. `tax_exempt_amount` VARCHAR；46. `tax_message` VARCHAR；47. `tax_status` VARCHAR；48. `template_id` VARCHAR；49. `transaction_currency` VARCHAR；50. `transferred_to_accounting` VARCHAR；51. `updated_by_id` VARCHAR；52. `updated_date` VARCHAR；53. `sequence_set_id` VARCHAR；54. `credit_memo_amount` VARCHAR
- initial：1. `id,_fivetran_deleted,_fivetran_synced,account_id,adjustment_amount,amount,amount_currency_rounding,amount_home_currency,amount_without_tax,amount_without_tax_currency_rounding,amount_without_tax_home_currency,auto_pay,balance,bill_to_contact_id,comments,created_by_id,created_date,credit_balance_adjustment_amount,default_payment_method_id,due_date,exchange_rate,exchange_rate_date,home_currency,includes_one_time,includes_recurring,includes_usage,invoice_date,invoice_number,last_email_sent_date,parent_account_id,payment_amount,payment_term,posted_by,posted_date,provider_exchange_rate_date,refund_amount,reversed,sold_to_contact_id,source,source_id,source_type,status,target_date,tax_amount,tax_exempt_amount,tax_message,tax_status,template_id,transaction_currency,transferred_to_accounting,updated_by_id,updated_date,sequence_set_id,credit_memo_amount` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `account_id` VARCHAR；5. `adjustment_amount` VARCHAR；6. `amount` VARCHAR；7. `amount_currency_rounding` VARCHAR；8. `amount_home_currency` VARCHAR；9. `amount_without_tax` VARCHAR；10. `amount_without_tax_currency_rounding` VARCHAR；11. `amount_without_tax_home_currency` VARCHAR；12. `auto_pay` VARCHAR；13. `balance` VARCHAR；14. `bill_to_contact_id` VARCHAR；15. `comments` VARCHAR；16. `created_by_id` VARCHAR；17. `created_date` VARCHAR；18. `credit_balance_adjustment_amount` VARCHAR；19. `default_payment_method_id` VARCHAR；20. `due_date` VARCHAR；21. `exchange_rate` VARCHAR；22. `exchange_rate_date` VARCHAR；23. `home_currency` VARCHAR；24. `includes_one_time` VARCHAR；25. `includes_recurring` VARCHAR；26. `includes_usage` VARCHAR；27. `invoice_date` VARCHAR；28. `invoice_number` VARCHAR；29. `last_email_sent_date` VARCHAR；30. `parent_account_id` VARCHAR；31. `payment_amount` VARCHAR；32. `payment_term` VARCHAR；33. `posted_by` VARCHAR；34. `posted_date` VARCHAR；35. `provider_exchange_rate_date` VARCHAR；36. `refund_amount` VARCHAR；37. `reversed` VARCHAR；38. `sold_to_contact_id` VARCHAR；39. `source` VARCHAR；40. `source_id` VARCHAR；41. `source_type` VARCHAR；42. `status` VARCHAR；43. `target_date` VARCHAR；44. `tax_amount` VARCHAR；45. `tax_exempt_amount` VARCHAR；46. `tax_message` VARCHAR；47. `tax_status` VARCHAR；48. `template_id` VARCHAR；49. `transaction_currency` VARCHAR；50. `transferred_to_accounting` VARCHAR；51. `updated_by_id` VARCHAR；52. `updated_date` VARCHAR；53. `sequence_set_id` VARCHAR；54. `credit_memo_amount` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | zuora__account_overview | 间接 | raw.zuora_invoice_data → staging.stg_zuora__invoice → intermediate.int_zuora__invoice_base → marts.zuora__account_overview |
| staging | stg_zuora__invoice | 直接 | raw.zuora_invoice_data → staging.stg_zuora__invoice |

来源：`015_raw_impl-030.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。

## impl-030 raw.zuora_taxation_item_data

| 比较 | gold 行数 | 另一侧行数 | 按顺序列名/类型一致 | 内容哈希一致 | 差异字段 |
|---|---:|---:|---|---|---|
| gold_vs_initial | 1005 | 1005 | False | False | ordered_columns_or_types_differ, sorted_content_hash_differ |
| gold_vs_agent | 1005 | 1005 | True | True | 无 |

**按原顺序的列名与类型**

- gold：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `account_id` VARCHAR；5. `account_receivable_accounting_code_id` VARCHAR；6. `accounting_code` VARCHAR；7. `accounting_period_id` VARCHAR；8. `amendment_id` VARCHAR；9. `balance` VARCHAR；10. `bill_to_contact_id` VARCHAR；11. `created_by_id` VARCHAR；12. `created_date` VARCHAR；13. `credit_amount` VARCHAR；14. `default_payment_method_id` VARCHAR；15. `exchange_rate` VARCHAR；16. `exchange_rate_date` VARCHAR；17. `exempt_amount` VARCHAR；18. `exempt_amount_currency_rounding` VARCHAR；19. `exempt_amount_home_currency` VARCHAR；20. `home_currency` VARCHAR；21. `invoice_id` VARCHAR；22. `invoice_item_id` VARCHAR；23. `journal_entry_id` VARCHAR；24. `journal_run_id` VARCHAR；25. `jurisdiction` VARCHAR；26. `location_code` VARCHAR；27. `name` VARCHAR；28. `payment_amount` VARCHAR；29. `product_id` VARCHAR；30. `product_rate_plan_charge_id` VARCHAR；31. `product_rate_plan_id` VARCHAR；32. `provider_exchange_rate_date` VARCHAR；33. `rate_plan_charge_id` VARCHAR；34. `rate_plan_id` VARCHAR；35. `sales_tax_payable_accounting_code_id` VARCHAR；36. `sold_to_contact_id` VARCHAR；37. `subscription_id` VARCHAR；38. `tax_amount` VARCHAR；39. `tax_amount_currency_rounding` VARCHAR；40. `tax_amount_home_currency` VARCHAR；41. `tax_code` VARCHAR；42. `tax_code_description` VARCHAR；43. `tax_date` VARCHAR；44. `tax_mode` VARCHAR；45. `tax_rate` VARCHAR；46. `tax_rate_description` VARCHAR；47. `tax_rate_type` VARCHAR；48. `transaction_currency` VARCHAR；49. `updated_by_id` VARCHAR；50. `updated_date` VARCHAR；51. `parent_account_id` VARCHAR；52. `seller_registration` VARCHAR；53. `tax_description` VARCHAR；54. `customer_code` VARCHAR；55. `tax_rule_id` VARCHAR；56. `exempt_certificate` VARCHAR
- initial：1. `id,_fivetran_deleted,_fivetran_synced,account_id,account_receivable_accounting_code_id,accounting_code,accounting_period_id,amendment_id,balance,bill_to_contact_id,created_by_id,created_date,credit_amount,default_payment_method_id,exchange_rate,exchange_rate_date,exempt_amount,exempt_amount_currency_rounding,exempt_amount_home_currency,home_currency,invoice_id,invoice_item_id,journal_entry_id,journal_run_id,jurisdiction,location_code,name,payment_amount,product_id,product_rate_plan_charge_id,product_rate_plan_id,provider_exchange_rate_date,rate_plan_charge_id,rate_plan_id,sales_tax_payable_accounting_code_id,sold_to_contact_id,subscription_id,tax_amount,tax_amount_currency_rounding,tax_amount_home_currency,tax_code,tax_code_description,tax_date,tax_mode,tax_rate,tax_rate_description,tax_rate_type,transaction_currency,updated_by_id,updated_date,parent_account_id,seller_registration,tax_description,customer_code,tax_rule_id,exempt_certificate` VARCHAR
- agent：1. `id` VARCHAR；2. `_fivetran_deleted` VARCHAR；3. `_fivetran_synced` VARCHAR；4. `account_id` VARCHAR；5. `account_receivable_accounting_code_id` VARCHAR；6. `accounting_code` VARCHAR；7. `accounting_period_id` VARCHAR；8. `amendment_id` VARCHAR；9. `balance` VARCHAR；10. `bill_to_contact_id` VARCHAR；11. `created_by_id` VARCHAR；12. `created_date` VARCHAR；13. `credit_amount` VARCHAR；14. `default_payment_method_id` VARCHAR；15. `exchange_rate` VARCHAR；16. `exchange_rate_date` VARCHAR；17. `exempt_amount` VARCHAR；18. `exempt_amount_currency_rounding` VARCHAR；19. `exempt_amount_home_currency` VARCHAR；20. `home_currency` VARCHAR；21. `invoice_id` VARCHAR；22. `invoice_item_id` VARCHAR；23. `journal_entry_id` VARCHAR；24. `journal_run_id` VARCHAR；25. `jurisdiction` VARCHAR；26. `location_code` VARCHAR；27. `name` VARCHAR；28. `payment_amount` VARCHAR；29. `product_id` VARCHAR；30. `product_rate_plan_charge_id` VARCHAR；31. `product_rate_plan_id` VARCHAR；32. `provider_exchange_rate_date` VARCHAR；33. `rate_plan_charge_id` VARCHAR；34. `rate_plan_id` VARCHAR；35. `sales_tax_payable_accounting_code_id` VARCHAR；36. `sold_to_contact_id` VARCHAR；37. `subscription_id` VARCHAR；38. `tax_amount` VARCHAR；39. `tax_amount_currency_rounding` VARCHAR；40. `tax_amount_home_currency` VARCHAR；41. `tax_code` VARCHAR；42. `tax_code_description` VARCHAR；43. `tax_date` VARCHAR；44. `tax_mode` VARCHAR；45. `tax_rate` VARCHAR；46. `tax_rate_description` VARCHAR；47. `tax_rate_type` VARCHAR；48. `transaction_currency` VARCHAR；49. `updated_by_id` VARCHAR；50. `updated_date` VARCHAR；51. `parent_account_id` VARCHAR；52. `seller_registration` VARCHAR；53. `tax_description` VARCHAR；54. `customer_code` VARCHAR；55. `tax_rule_id` VARCHAR；56. `exempt_certificate` VARCHAR

**013 待标注下游**

| 层 | 表 | 直接/间接 | 一条最短读取路径 |
|---|---|---|---|
| marts | zuora__account_overview | 间接 | raw.zuora_taxation_item_data → staging.stg_zuora__taxation_item → intermediate.int_zuora__billing_enriched → marts.zuora__account_overview |
| staging | stg_zuora__taxation_item | 直接 | raw.zuora_taxation_item_data → staging.stg_zuora__taxation_item |

来源：`015_raw_impl-030.json`、`008_table_scan.jsonl` 的 source_comparison.agent_direct_read_sources、`013_statuses.jsonl`。
