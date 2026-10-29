# 全部 raw 表清单 / 列结构 / 行数差异

仅记录元数据与计数，不比较单元格值，不判断原因或操作是否正确。

## impl-015

### raw.address_data

初始存在：True；agent 存在：True；初始行数：5000；agent 行数：5000。

type_differences

```json
[
  {
    "column": "line_3",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "line_4",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "line_5",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.bill_payment_data

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "check_print_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "exchange_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "pay_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "process_bill_payment",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.bundle_data

初始存在：True；agent 存在：True；初始行数：500；agent 行数：500。

type_differences

```json
[
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "print_grouped_items",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "purchase_cost",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "unit_price",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.bundle_item_data

初始存在：True；agent 存在：True；初始行数：1500；agent 行数：1500。

type_differences

```json
[
  {
    "column": "item_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.credit_card_payment_txn_data

初始存在：True；agent 存在：True；初始行数：2000；agent 行数：2000。

type_differences

```json
[
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.credit_memo_data

初始存在：True；agent 存在：True；初始行数：1000；agent 行数：1000。

type_differences

```json
[
  {
    "column": "apply_tax_after_discount",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "customer_memo",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "exchange_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "global_tax_calculation",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "print_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "remaining_credit",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.credit_memo_line_data

初始存在：True；agent 存在：True；初始行数：2500；agent 行数：2500。

type_differences

```json
[
  {
    "column": "bundle_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_discount_percent",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_percent_based",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_discount_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_unit_price",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.department_data

初始存在：True；agent 存在：True；初始行数：50；agent 行数：50。

type_differences

```json
[
  {
    "column": "parent_department_id",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.deposit_data

初始存在：True；agent 存在：True；初始行数：1500；agent 行数：1500。

type_differences

```json
[
  {
    "column": "cash_back_memo",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "global_tax_calculation",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "transaction_source",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "transaction_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.deposit_line_data

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "deposit_tax_applicable_on",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "deposit_transaction_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "detail_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.estimate_data

初始存在：True；agent 存在：True；初始行数：2000；agent 行数：2000。

type_differences

```json
[
  {
    "column": "accepted_by",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "apply_tax_after_discount",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "custom_sales_rep",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "customer_memo",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "delivery_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "exchange_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "global_tax_calculation",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "print_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "transaction_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.estimate_line_data

初始存在：True；agent 存在：True；初始行数：5000；agent 行数：5000。

type_differences

```json
[
  {
    "column": "bundle_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_discount_percent",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_percent_based",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_discount_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_unit_price",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.invoice_line_bundle_data

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "discount_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "line_num",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "unit_price",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.invoice_line_data

初始存在：True；agent 存在：True；初始行数：20000；agent 行数：20000。

type_differences

```json
[
  {
    "column": "bundle_id",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "bundle_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "description_service_date",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "description_tax_code_id",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_account_id",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_class_id",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_percent_based",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_tax_code_id",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "item_id",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_service_date",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sub_total_item_id",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "tax_code_id",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.item_data

初始存在：True；agent 存在：True；初始行数：2000；agent 行数：2000。

type_differences

```json
[
  {
    "column": "parent_item_id",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.journal_entry_data

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "adjustment",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.journal_entry_line_data

初始存在：True；agent 存在：True；初始行数：9000；agent 行数：9000。

type_differences

```json
[
  {
    "column": "billable_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "tax_applicable_on",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.payment_data

初始存在：True；agent 存在：True；初始行数：6000；agent 行数：6000。

type_differences

```json
[
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_auth_code",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_billing_address_street",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_cc_expiry_month",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_cc_expiry_year",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_postal_code",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_process_payment",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_transaction_authorization_time",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "process_payment",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "transaction_source",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "transaction_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.purchase_data

初始存在：True；agent 存在：True；初始行数：2500；agent 行数：2500。

type_differences

```json
[
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "exchange_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "global_tax_calculation",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "payment_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "print_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "transaction_source",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.purchase_line_data

初始存在：True；agent 存在：True；初始行数：6000；agent 行数：6000。

type_differences

```json
[
  {
    "column": "account_expense_billable_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "item_expense_billable_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "item_expense_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "item_expense_unit_price",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.purchase_order_data

初始存在：True；agent 存在：True；初始行数：2000；agent 行数：2000。

type_differences

```json
[
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "custom_customer_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "exchange_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "global_tax_calculation",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "memo",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.purchase_order_line_data

初始存在：True；agent 存在：True；初始行数：5000；agent 行数：5000。

type_differences

```json
[
  {
    "column": "account_expense_billable_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "item_expense_billable_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "item_expense_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "item_expense_unit_price",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.refund_receipt_data

初始存在：True；agent 存在：True；初始行数：800；agent 行数：800。

type_differences

```json
[
  {
    "column": "apply_tax_after_discount",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "check_payment_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_auth_code",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_billing_address_street",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_cc_expiry_month",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_cc_expiry_year",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_postal_code",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_process_payment",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_transaction_authorization_time",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "customer_memo",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "exchange_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "global_tax_calculation",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "payment_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "print_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "transaction_source",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.refund_receipt_line_data

初始存在：True；agent 存在：True；初始行数：2000；agent 行数：2000。

type_differences

```json
[
  {
    "column": "bundle_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_discount_percent",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_percent_based",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_discount_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_unit_price",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.sales_receipt_data

初始存在：True；agent 存在：True；初始行数：4000；agent 行数：4000。

type_differences

```json
[
  {
    "column": "apply_tax_after_discount",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_auth_code",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_billing_address_street",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_cc_expiry_month",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_cc_expiry_year",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_postal_code",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_process_payment",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_transaction_authorization_time",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "credit_card_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "customer_memo",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "delivery_time",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "delivery_type",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "exchange_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "global_tax_calculation",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "print_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "transaction_source",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.sales_receipt_line_data

初始存在：True；agent 存在：True；初始行数：10000；agent 行数：10000。

type_differences

```json
[
  {
    "column": "bundle_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_discount_percent",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "discount_percent_based",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_discount_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "sales_item_unit_price",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.transfer_data

初始存在：True；agent 存在：True；初始行数：1000；agent 行数：1000。

type_differences

```json
[
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.vendor_credit_data

初始存在：True；agent 存在：True；初始行数：1200；agent 行数：1200。

type_differences

```json
[
  {
    "column": "created_at",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "exchange_rate",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "global_tax_calculation",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.vendor_credit_line_data

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "account_expense_billable_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "item_expense_billable_status",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "item_expense_quantity",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "item_expense_unit_price",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "private_note",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

### raw.vendor_data

初始存在：True；agent 存在：True；初始行数：1500；agent 行数：1500。

type_differences

```json
[
  {
    "column": "middle_name",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "other_contacts",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "suffix",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  },
  {
    "column": "title",
    "initial_type": "VARCHAR",
    "agent_type": "INTEGER"
  }
]
```

## impl-016

### raw.person_contact_email_address

初始存在：True；agent 存在：True；初始行数：7284；agent 行数：2448。

## impl-017

### raw.scheduled_interview_snowflake

初始存在：True；agent 存在：True；初始行数：2000；agent 行数：2000。

initial_only_columns

```json
[
  {
    "name": "\"START\"",
    "type": "TIMESTAMP",
    "ordinal_position": 10
  }
]
```

agent_only_columns

```json
[
  {
    "name": "START",
    "type": "TIMESTAMP",
    "ordinal_position": 10
  }
]
```

## impl-019

### raw.app_crash_daily

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_position": 2,
    "agent_position": 9
  },
  {
    "column": "app_id",
    "initial_position": 3,
    "agent_position": 2
  },
  {
    "column": "crashes",
    "initial_position": 5,
    "agent_position": 7
  },
  {
    "column": "date",
    "initial_position": 6,
    "agent_position": 3
  },
  {
    "column": "device",
    "initial_position": 7,
    "agent_position": 5
  },
  {
    "column": "platform_version",
    "initial_position": 8,
    "agent_position": 6
  },
  {
    "column": "unique_devices",
    "initial_position": 9,
    "agent_position": 8
  }
]
```

### raw.app_session_standard_daily

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

initial_only_columns

```json
[
  {
    "name": "app_download_date",
    "type": "DATE",
    "ordinal_position": 3
  }
]
```

agent_only_columns

```json
[
  {
    "name": "app_downloa1d_date",
    "type": "VARCHAR",
    "ordinal_position": 9
  }
]
```

type_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "date",
    "initial_type": "DATE",
    "agent_type": "VARCHAR"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_position": 2,
    "agent_position": 14
  },
  {
    "column": "app_id",
    "initial_position": 4,
    "agent_position": 2
  },
  {
    "column": "app_version",
    "initial_position": 5,
    "agent_position": 4
  },
  {
    "column": "date",
    "initial_position": 6,
    "agent_position": 3
  },
  {
    "column": "device",
    "initial_position": 7,
    "agent_position": 5
  },
  {
    "column": "platform_version",
    "initial_position": 9,
    "agent_position": 6
  },
  {
    "column": "sessions",
    "initial_position": 10,
    "agent_position": 11
  },
  {
    "column": "source_type",
    "initial_position": 11,
    "agent_position": 7
  },
  {
    "column": "territory",
    "initial_position": 12,
    "agent_position": 10
  },
  {
    "column": "total_session_duration",
    "initial_position": 13,
    "agent_position": 12
  },
  {
    "column": "unique_devices",
    "initial_position": 14,
    "agent_position": 13
  }
]
```

### raw.app_store_app

初始存在：True；agent 存在：True；初始行数：300；agent 行数：300。

type_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "TIMESTAMP WITH TIME ZONE"
  },
  {
    "column": "was_made_for_kids",
    "initial_type": "VARCHAR",
    "agent_type": "BOOLEAN"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_position": 1,
    "agent_position": 10
  },
  {
    "column": "content_rights_declaration",
    "initial_position": 2,
    "agent_position": 4
  },
  {
    "column": "id",
    "initial_position": 3,
    "agent_position": 1
  },
  {
    "column": "name",
    "initial_position": 4,
    "agent_position": 2
  },
  {
    "column": "primary_locale",
    "initial_position": 5,
    "agent_position": 3
  },
  {
    "column": "subscription_status_url_for_sandbox",
    "initial_position": 7,
    "agent_position": 8
  },
  {
    "column": "subscription_status_url_version",
    "initial_position": 8,
    "agent_position": 7
  },
  {
    "column": "was_made_for_kids",
    "initial_position": 10,
    "agent_position": 5
  }
]
```

### raw.app_store_discovery_and_engagement_standard_daily

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_position": 2,
    "agent_position": 13
  },
  {
    "column": "app_id",
    "initial_position": 3,
    "agent_position": 2
  },
  {
    "column": "counts",
    "initial_position": 4,
    "agent_position": 11
  },
  {
    "column": "date",
    "initial_position": 5,
    "agent_position": 3
  },
  {
    "column": "device",
    "initial_position": 6,
    "agent_position": 8
  },
  {
    "column": "event",
    "initial_position": 8,
    "agent_position": 4
  },
  {
    "column": "page_type",
    "initial_position": 9,
    "agent_position": 5
  },
  {
    "column": "platform_version",
    "initial_position": 10,
    "agent_position": 9
  },
  {
    "column": "source_type",
    "initial_position": 11,
    "agent_position": 6
  },
  {
    "column": "territory",
    "initial_position": 12,
    "agent_position": 10
  },
  {
    "column": "unique_counts",
    "initial_position": 13,
    "agent_position": 12
  }
]
```

### raw.app_store_download_standard_daily

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "date",
    "initial_type": "DATE",
    "agent_type": "VARCHAR"
  },
  {
    "column": "pre_order",
    "initial_type": "VARCHAR",
    "agent_type": "BOOLEAN"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_position": 2,
    "agent_position": 13
  },
  {
    "column": "app_id",
    "initial_position": 3,
    "agent_position": 2
  },
  {
    "column": "app_version",
    "initial_position": 4,
    "agent_position": 5
  },
  {
    "column": "counts",
    "initial_position": 5,
    "agent_position": 12
  },
  {
    "column": "date",
    "initial_position": 6,
    "agent_position": 3
  },
  {
    "column": "device",
    "initial_position": 7,
    "agent_position": 6
  },
  {
    "column": "download_type",
    "initial_position": 8,
    "agent_position": 4
  },
  {
    "column": "platform_version",
    "initial_position": 10,
    "agent_position": 7
  },
  {
    "column": "pre_order",
    "initial_position": 11,
    "agent_position": 10
  },
  {
    "column": "source_type",
    "initial_position": 12,
    "agent_position": 8
  },
  {
    "column": "territory",
    "initial_position": 13,
    "agent_position": 11
  }
]
```

### raw.app_store_installation_and_deletion_standard_daily

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "app_version",
    "initial_type": "VARCHAR",
    "agent_type": "DOUBLE"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_position": 2,
    "agent_position": 15
  },
  {
    "column": "app_download_date",
    "initial_position": 3,
    "agent_position": 11
  },
  {
    "column": "app_id",
    "initial_position": 4,
    "agent_position": 2
  },
  {
    "column": "app_version",
    "initial_position": 5,
    "agent_position": 6
  },
  {
    "column": "counts",
    "initial_position": 6,
    "agent_position": 13
  },
  {
    "column": "date",
    "initial_position": 7,
    "agent_position": 3
  },
  {
    "column": "device",
    "initial_position": 8,
    "agent_position": 7
  },
  {
    "column": "download_type",
    "initial_position": 9,
    "agent_position": 5
  },
  {
    "column": "event",
    "initial_position": 10,
    "agent_position": 4
  },
  {
    "column": "page_type",
    "initial_position": 11,
    "agent_position": 10
  },
  {
    "column": "platform_version",
    "initial_position": 12,
    "agent_position": 8
  },
  {
    "column": "source_type",
    "initial_position": 13,
    "agent_position": 9
  },
  {
    "column": "territory",
    "initial_position": 14,
    "agent_position": 12
  },
  {
    "column": "unique_devices",
    "initial_position": 15,
    "agent_position": 14
  }
]
```

### raw.apple_store_country_codes

初始存在：False；agent 存在：True；初始行数：None；agent 行数：250。

agent_only_columns

```json
[
  {
    "name": "country_name",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "alternative_country_name",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "country_code_numeric",
    "type": "BIGINT",
    "ordinal_position": 3
  },
  {
    "name": "country_code_alpha_2",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "country_code_alpha_3",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "region",
    "type": "VARCHAR",
    "ordinal_position": 6
  },
  {
    "name": "region_code",
    "type": "VARCHAR",
    "ordinal_position": 7
  },
  {
    "name": "sub_region",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "sub_region_code",
    "type": "VARCHAR",
    "ordinal_position": 9
  }
]
```

存在一侧的完整列清单

```json
[
  {
    "name": "country_name",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "alternative_country_name",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "country_code_numeric",
    "type": "BIGINT",
    "ordinal_position": 3
  },
  {
    "name": "country_code_alpha_2",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "country_code_alpha_3",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "region",
    "type": "VARCHAR",
    "ordinal_position": 6
  },
  {
    "name": "region_code",
    "type": "VARCHAR",
    "ordinal_position": 7
  },
  {
    "name": "sub_region",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "sub_region_code",
    "type": "VARCHAR",
    "ordinal_position": 9
  }
]
```

### raw.sales_subscription_event_summary

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "event_date",
    "initial_type": "DATE",
    "agent_type": "VARCHAR"
  },
  {
    "column": "original_start_date",
    "initial_type": "DATE",
    "agent_type": "VARCHAR"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_position": 2,
    "agent_position": 32
  },
  {
    "column": "app_apple_id",
    "initial_position": 3,
    "agent_position": 6
  },
  {
    "column": "app_name",
    "initial_position": 4,
    "agent_position": 5
  },
  {
    "column": "cancellation_reason",
    "initial_position": 5,
    "agent_position": 28
  },
  {
    "column": "client",
    "initial_position": 6,
    "agent_position": 22
  },
  {
    "column": "consecutive_paid_periods",
    "initial_position": 7,
    "agent_position": 19
  },
  {
    "column": "country",
    "initial_position": 8,
    "agent_position": 24
  },
  {
    "column": "days_before_canceling",
    "initial_position": 9,
    "agent_position": 27
  },
  {
    "column": "days_canceled",
    "initial_position": 10,
    "agent_position": 29
  },
  {
    "column": "device",
    "initial_position": 11,
    "agent_position": 21
  },
  {
    "column": "event",
    "initial_position": 12,
    "agent_position": 4
  },
  {
    "column": "event_date",
    "initial_position": 13,
    "agent_position": 3
  },
  {
    "column": "marketing_opt_in",
    "initial_position": 14,
    "agent_position": 13
  },
  {
    "column": "marketing_opt_in_duration",
    "initial_position": 15,
    "agent_position": 14
  },
  {
    "column": "original_start_date",
    "initial_position": 16,
    "agent_position": 20
  },
  {
    "column": "paid_service_days_recovered",
    "initial_position": 17,
    "agent_position": 31
  },
  {
    "column": "preserved_pricing",
    "initial_position": 18,
    "agent_position": 15
  },
  {
    "column": "previous_subscription_apple_id",
    "initial_position": 19,
    "agent_position": 26
  },
  {
    "column": "previous_subscription_name",
    "initial_position": 20,
    "agent_position": 25
  },
  {
    "column": "proceeds_reason",
    "initial_position": 21,
    "agent_position": 16
  },
  {
    "column": "promotional_offer_id",
    "initial_position": 22,
    "agent_position": 18
  },
  {
    "column": "promotional_offer_name",
    "initial_position": 23,
    "agent_position": 17
  },
  {
    "column": "quantity",
    "initial_position": 24,
    "agent_position": 30
  },
  {
    "column": "standard_subscription_duration",
    "initial_position": 25,
    "agent_position": 10
  },
  {
    "column": "state",
    "initial_position": 26,
    "agent_position": 23
  },
  {
    "column": "subscription_apple_id",
    "initial_position": 27,
    "agent_position": 8
  },
  {
    "column": "subscription_group_id",
    "initial_position": 28,
    "agent_position": 9
  },
  {
    "column": "subscription_name",
    "initial_position": 29,
    "agent_position": 7
  },
  {
    "column": "subscription_offer_duration",
    "initial_position": 30,
    "agent_position": 12
  },
  {
    "column": "subscription_offer_type",
    "initial_position": 31,
    "agent_position": 11
  },
  {
    "column": "vendor_number",
    "initial_position": 32,
    "agent_position": 2
  }
]
```

### raw.sales_subscription_summary

初始存在：True；agent 存在：True；初始行数：3000；agent 行数：3000。

type_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "customer_price",
    "initial_type": "DECIMAL(18,2)",
    "agent_type": "DOUBLE"
  },
  {
    "column": "date",
    "initial_type": "DATE",
    "agent_type": "VARCHAR"
  },
  {
    "column": "developer_proceeds",
    "initial_type": "DECIMAL(18,2)",
    "agent_type": "DOUBLE"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_position": 2,
    "agent_position": 35
  },
  {
    "column": "active_free_trial_introductory_offer_subscriptions",
    "initial_position": 3,
    "agent_position": 22
  },
  {
    "column": "active_pay_as_you_go_introductory_offer_subscriptions",
    "initial_position": 4,
    "agent_position": 24
  },
  {
    "column": "active_pay_up_front_introductory_offer_subscriptions",
    "initial_position": 5,
    "agent_position": 23
  },
  {
    "column": "active_standard_price_subscriptions",
    "initial_position": 6,
    "agent_position": 21
  },
  {
    "column": "app_apple_id",
    "initial_position": 7,
    "agent_position": 4
  },
  {
    "column": "app_name",
    "initial_position": 8,
    "agent_position": 3
  },
  {
    "column": "billing_retry",
    "initial_position": 9,
    "agent_position": 29
  },
  {
    "column": "client",
    "initial_position": 10,
    "agent_position": 20
  },
  {
    "column": "country",
    "initial_position": 11,
    "agent_position": 18
  },
  {
    "column": "customer_currency",
    "initial_position": 12,
    "agent_position": 10
  },
  {
    "column": "customer_price",
    "initial_position": 13,
    "agent_position": 9
  },
  {
    "column": "date",
    "initial_position": 14,
    "agent_position": 36
  },
  {
    "column": "developer_proceeds",
    "initial_position": 15,
    "agent_position": 11
  },
  {
    "column": "device",
    "initial_position": 16,
    "agent_position": 19
  },
  {
    "column": "free_trial_offer_code_subscriptions",
    "initial_position": 17,
    "agent_position": 31
  },
  {
    "column": "free_trial_promotional_offer_subscriptions",
    "initial_position": 18,
    "agent_position": 25
  },
  {
    "column": "grace_period",
    "initial_position": 19,
    "agent_position": 30
  },
  {
    "column": "marketing_opt_ins",
    "initial_position": 20,
    "agent_position": 28
  },
  {
    "column": "pay_as_you_go_offer_code_subscriptions",
    "initial_position": 21,
    "agent_position": 33
  },
  {
    "column": "pay_as_you_go_promotional_offer_subscriptions",
    "initial_position": 22,
    "agent_position": 27
  },
  {
    "column": "pay_up_front_offer_code_subscriptions",
    "initial_position": 23,
    "agent_position": 32
  },
  {
    "column": "pay_up_front_promotional_offer_subscriptions",
    "initial_position": 24,
    "agent_position": 26
  },
  {
    "column": "preserved_pricing",
    "initial_position": 25,
    "agent_position": 13
  },
  {
    "column": "proceeds_currency",
    "initial_position": 26,
    "agent_position": 12
  },
  {
    "column": "proceeds_reason",
    "initial_position": 27,
    "agent_position": 14
  },
  {
    "column": "promotional_offer_id",
    "initial_position": 28,
    "agent_position": 16
  },
  {
    "column": "standard_subscription_duration",
    "initial_position": 29,
    "agent_position": 8
  },
  {
    "column": "state",
    "initial_position": 30,
    "agent_position": 17
  },
  {
    "column": "subscribers",
    "initial_position": 31,
    "agent_position": 34
  },
  {
    "column": "subscription_apple_id",
    "initial_position": 32,
    "agent_position": 6
  },
  {
    "column": "subscription_group_id",
    "initial_position": 33,
    "agent_position": 7
  },
  {
    "column": "subscription_name",
    "initial_position": 34,
    "agent_position": 5
  },
  {
    "column": "subscription_offer_name",
    "initial_position": 35,
    "agent_position": 15
  },
  {
    "column": "vendor_number",
    "initial_position": 36,
    "agent_position": 2
  }
]
```

## impl-020

### raw.admin_data

初始存在：True；agent 存在：True；初始行数：3004；agent 行数：3004。

type_differences

```json
[
  {
    "column": "_fivetran_deleted",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  }
]
```

### raw.company_history_data

初始存在：True；agent 存在：True；初始行数：2509；agent 行数：2509。

type_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_end",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_start",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "created_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "last_request_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "monthly_spend",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  },
  {
    "column": "remote_created_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "session_count",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  },
  {
    "column": "updated_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "user_count",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  }
]
```

### raw.company_tag_history_data

初始存在：True；agent 存在：True；初始行数：2431；agent 行数：2431。

type_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_end",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_start",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "company_updated_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "tag_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  }
]
```

### raw.contact_company_history_data

初始存在：True；agent 存在：True；初始行数：1473；agent 行数：1473。

initial_only_columns

```json
[
  {
    "name": "company_updated_at",
    "type": "TIMESTAMP",
    "ordinal_position": 3
  }
]
```

type_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_end",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_start",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_position": 4,
    "agent_position": 3
  },
  {
    "column": "_fivetran_end",
    "initial_position": 7,
    "agent_position": 6
  },
  {
    "column": "_fivetran_start",
    "initial_position": 6,
    "agent_position": 5
  },
  {
    "column": "_fivetran_synced",
    "initial_position": 5,
    "agent_position": 4
  }
]
```

### raw.contact_history_data

初始存在：True；agent 存在：True；初始行数：3009；agent 行数：3009。

type_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_end",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_start",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "admin_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  },
  {
    "column": "browser_version",
    "initial_type": "DOUBLE",
    "agent_type": "VARCHAR"
  },
  {
    "column": "created_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "has_hard_bounced",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "last_contacted_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "last_email_clicked_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "last_email_opened_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "last_seen_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "marked_email_as_spam",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "signed_up_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "unsubscribed_from_emails",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "updated_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  }
]
```

### raw.contact_tag_history_data

初始存在：True；agent 存在：True；初始行数：2945；agent 行数：2945。

type_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_end",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_start",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "contact_updated_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "tag_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_position": 7,
    "agent_position": 4
  },
  {
    "column": "_fivetran_end",
    "initial_position": 6,
    "agent_position": 7
  },
  {
    "column": "_fivetran_start",
    "initial_position": 5,
    "agent_position": 6
  },
  {
    "column": "_fivetran_synced",
    "initial_position": 4,
    "agent_position": 5
  }
]
```

### raw.conversation_contact_history_data

初始存在：True；agent 存在：True；初始行数：4033；agent 行数：4033。

initial_only_columns

```json
[
  {
    "name": "conversation_updated_at",
    "type": "TIMESTAMP",
    "ordinal_position": 3
  }
]
```

type_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_end",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_start",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "conversation_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_position": 7,
    "agent_position": 3
  },
  {
    "column": "contact_id",
    "initial_position": 1,
    "agent_position": 2
  },
  {
    "column": "conversation_id",
    "initial_position": 2,
    "agent_position": 1
  }
]
```

### raw.conversation_history_data

初始存在：True；agent 存在：True；初始行数：29758；agent 行数：29759。

type_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "assignee_id",
    "initial_type": "DOUBLE",
    "agent_type": "VARCHAR"
  },
  {
    "column": "conversation_rating_value",
    "initial_type": "DOUBLE",
    "agent_type": "VARCHAR"
  },
  {
    "column": "id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  },
  {
    "column": "read",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "source_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  }
]
```

### raw.conversation_part_history_data

初始存在：True；agent 存在：True；初始行数：7524；agent 行数：7524。

initial_only_columns

```json
[
  {
    "name": "redacted",
    "type": "BOOLEAN",
    "ordinal_position": 13
  },
  {
    "name": "social_respond",
    "type": "BOOLEAN",
    "ordinal_position": 14
  },
  {
    "name": "updated_at_from_parts",
    "type": "TIMESTAMP",
    "ordinal_position": 16
  },
  {
    "name": "url",
    "type": "VARCHAR",
    "ordinal_position": 17
  }
]
```

agent_only_columns

```json
[
  {
    "name": "delivered_as",
    "type": "VARCHAR",
    "ordinal_position": 9
  },
  {
    "name": "rating_state",
    "type": "VARCHAR",
    "ordinal_position": 13
  },
  {
    "name": "subject",
    "type": "VARCHAR",
    "ordinal_position": 15
  }
]
```

type_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_end",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_start",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "author_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  },
  {
    "column": "conversation_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  },
  {
    "column": "created_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "rating_value",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  },
  {
    "column": "updated_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_position": 20,
    "agent_position": 19
  },
  {
    "column": "_fivetran_end",
    "initial_position": 19,
    "agent_position": 18
  },
  {
    "column": "_fivetran_start",
    "initial_position": 18,
    "agent_position": 17
  },
  {
    "column": "conversation_id",
    "initial_position": 8,
    "agent_position": 7
  },
  {
    "column": "created_at",
    "initial_position": 7,
    "agent_position": 8
  },
  {
    "column": "external_id",
    "initial_position": 9,
    "agent_position": 10
  },
  {
    "column": "part_type",
    "initial_position": 10,
    "agent_position": 11
  },
  {
    "column": "rating_remark",
    "initial_position": 11,
    "agent_position": 12
  },
  {
    "column": "rating_value",
    "initial_position": 12,
    "agent_position": 14
  },
  {
    "column": "type",
    "initial_position": 15,
    "agent_position": 16
  }
]
```

### raw.conversation_tag_history_data

初始存在：True；agent 存在：True；初始行数：2996；agent 行数：2996。

type_differences

```json
[
  {
    "column": "_fivetran_active",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_end",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_start",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "conversation_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  },
  {
    "column": "conversation_updated_at",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "tag_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  }
]
```

### raw.tag_data

初始存在：True；agent 存在：True；初始行数：123；agent 行数：124。

type_differences

```json
[
  {
    "column": "_fivetran_deleted",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  }
]
```

### raw.team_admin_data

初始存在：True；agent 存在：True；初始行数：145；agent 行数：145。

initial_only_columns

```json
[
  {
    "name": "team_updated_at",
    "type": "TIMESTAMP",
    "ordinal_position": 3
  },
  {
    "name": "_fivetran_active",
    "type": "BOOLEAN",
    "ordinal_position": 4
  },
  {
    "name": "_fivetran_start",
    "type": "TIMESTAMP",
    "ordinal_position": 6
  },
  {
    "name": "_fivetran_end",
    "type": "TIMESTAMP",
    "ordinal_position": 7
  }
]
```

agent_only_columns

```json
[
  {
    "name": "_fivetran_deleted",
    "type": "VARCHAR",
    "ordinal_position": 3
  }
]
```

type_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_type": "TIMESTAMP",
    "agent_type": "VARCHAR"
  },
  {
    "column": "admin_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  },
  {
    "column": "team_id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  }
]
```

column_order_differences

```json
[
  {
    "column": "_fivetran_synced",
    "initial_position": 5,
    "agent_position": 4
  },
  {
    "column": "admin_id",
    "initial_position": 2,
    "agent_position": 1
  },
  {
    "column": "team_id",
    "initial_position": 1,
    "agent_position": 2
  }
]
```

### raw.team_data

初始存在：True；agent 存在：True；初始行数：51；agent 行数：52。

type_differences

```json
[
  {
    "column": "_fivetran_deleted",
    "initial_type": "BOOLEAN",
    "agent_type": "VARCHAR"
  },
  {
    "column": "id",
    "initial_type": "BIGINT",
    "agent_type": "VARCHAR"
  }
]
```

## impl-021

### raw.campaign

初始存在：True；agent 存在：True；初始行数：197；agent 行数：200。

agent_only_columns

```json
[
  {
    "name": "column18",
    "type": "VARCHAR",
    "ordinal_position": 19
  },
  {
    "name": "column19",
    "type": "VARCHAR",
    "ordinal_position": 20
  },
  {
    "name": "column20",
    "type": "VARCHAR",
    "ordinal_position": 21
  },
  {
    "name": "column21",
    "type": "VARCHAR",
    "ordinal_position": 22
  },
  {
    "name": "column22",
    "type": "VARCHAR",
    "ordinal_position": 23
  },
  {
    "name": "column23",
    "type": "VARCHAR",
    "ordinal_position": 24
  },
  {
    "name": "column24",
    "type": "VARCHAR",
    "ordinal_position": 25
  },
  {
    "name": "column25",
    "type": "VARCHAR",
    "ordinal_position": 26
  },
  {
    "name": "column26",
    "type": "TIMESTAMP",
    "ordinal_position": 27
  },
  {
    "name": "column27",
    "type": "TIMESTAMP",
    "ordinal_position": 28
  },
  {
    "name": "column28",
    "type": "TIMESTAMP",
    "ordinal_position": 29
  },
  {
    "name": "column29",
    "type": "TIMESTAMP",
    "ordinal_position": 30
  },
  {
    "name": "column30",
    "type": "BOOLEAN",
    "ordinal_position": 31
  },
  {
    "name": "column31",
    "type": "VARCHAR",
    "ordinal_position": 32
  },
  {
    "name": "column32",
    "type": "TIMESTAMP",
    "ordinal_position": 33
  },
  {
    "name": "column33",
    "type": "BOOLEAN",
    "ordinal_position": 34
  },
  {
    "name": "column34",
    "type": "TIMESTAMP",
    "ordinal_position": 35
  }
]
```

type_differences

```json
[
  {
    "column": "SEND_TIME",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  },
  {
    "column": "SENT_AT",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  },
  {
    "column": "STATUS_ID",
    "initial_type": "VARCHAR",
    "agent_type": "BIGINT"
  },
  {
    "column": "UPDATED",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  }
]
```

### raw.event

初始存在：True；agent 存在：True；初始行数：2499；agent 行数：2500。

agent_only_columns

```json
[
  {
    "name": "column100",
    "type": "VARCHAR",
    "ordinal_position": 101
  },
  {
    "name": "column101",
    "type": "VARCHAR",
    "ordinal_position": 102
  },
  {
    "name": "column102",
    "type": "VARCHAR",
    "ordinal_position": 103
  },
  {
    "name": "column103",
    "type": "VARCHAR",
    "ordinal_position": 104
  },
  {
    "name": "column104",
    "type": "VARCHAR",
    "ordinal_position": 105
  },
  {
    "name": "column105",
    "type": "TIMESTAMP",
    "ordinal_position": 106
  },
  {
    "name": "column106",
    "type": "TIMESTAMP",
    "ordinal_position": 107
  },
  {
    "name": "column107",
    "type": "BOOLEAN",
    "ordinal_position": 108
  },
  {
    "name": "column108",
    "type": "VARCHAR",
    "ordinal_position": 109
  },
  {
    "name": "column109",
    "type": "VARCHAR",
    "ordinal_position": 110
  },
  {
    "name": "column110",
    "type": "VARCHAR",
    "ordinal_position": 111
  },
  {
    "name": "column111",
    "type": "VARCHAR",
    "ordinal_position": 112
  },
  {
    "name": "column112",
    "type": "VARCHAR",
    "ordinal_position": 113
  },
  {
    "name": "column113",
    "type": "VARCHAR",
    "ordinal_position": 114
  },
  {
    "name": "column114",
    "type": "VARCHAR",
    "ordinal_position": 115
  },
  {
    "name": "column115",
    "type": "VARCHAR",
    "ordinal_position": 116
  },
  {
    "name": "column116",
    "type": "VARCHAR",
    "ordinal_position": 117
  },
  {
    "name": "column117",
    "type": "BIGINT",
    "ordinal_position": 118
  },
  {
    "name": "column118",
    "type": "VARCHAR",
    "ordinal_position": 119
  },
  {
    "name": "column119",
    "type": "TIMESTAMP",
    "ordinal_position": 120
  },
  {
    "name": "column120",
    "type": "VARCHAR",
    "ordinal_position": 121
  },
  {
    "name": "column121",
    "type": "VARCHAR",
    "ordinal_position": 122
  },
  {
    "name": "column122",
    "type": "VARCHAR",
    "ordinal_position": 123
  },
  {
    "name": "column123",
    "type": "VARCHAR",
    "ordinal_position": 124
  },
  {
    "name": "column124",
    "type": "VARCHAR",
    "ordinal_position": 125
  },
  {
    "name": "column125",
    "type": "VARCHAR",
    "ordinal_position": 126
  },
  {
    "name": "column126",
    "type": "VARCHAR",
    "ordinal_position": 127
  },
  {
    "name": "column127",
    "type": "VARCHAR",
    "ordinal_position": 128
  },
  {
    "name": "column128",
    "type": "VARCHAR",
    "ordinal_position": 129
  },
  {
    "name": "column129",
    "type": "VARCHAR",
    "ordinal_position": 130
  },
  {
    "name": "column130",
    "type": "VARCHAR",
    "ordinal_position": 131
  },
  {
    "name": "column131",
    "type": "VARCHAR",
    "ordinal_position": 132
  },
  {
    "name": "column132",
    "type": "VARCHAR",
    "ordinal_position": 133
  },
  {
    "name": "column133",
    "type": "VARCHAR",
    "ordinal_position": 134
  },
  {
    "name": "column134",
    "type": "VARCHAR",
    "ordinal_position": 135
  },
  {
    "name": "column135",
    "type": "VARCHAR",
    "ordinal_position": 136
  },
  {
    "name": "column136",
    "type": "VARCHAR",
    "ordinal_position": 137
  },
  {
    "name": "column137",
    "type": "VARCHAR",
    "ordinal_position": 138
  },
  {
    "name": "column138",
    "type": "VARCHAR",
    "ordinal_position": 139
  },
  {
    "name": "column139",
    "type": "VARCHAR",
    "ordinal_position": 140
  },
  {
    "name": "column140",
    "type": "VARCHAR",
    "ordinal_position": 141
  },
  {
    "name": "column141",
    "type": "VARCHAR",
    "ordinal_position": 142
  },
  {
    "name": "column142",
    "type": "VARCHAR",
    "ordinal_position": 143
  },
  {
    "name": "column143",
    "type": "VARCHAR",
    "ordinal_position": 144
  },
  {
    "name": "column144",
    "type": "VARCHAR",
    "ordinal_position": 145
  },
  {
    "name": "column145",
    "type": "VARCHAR",
    "ordinal_position": 146
  },
  {
    "name": "column146",
    "type": "VARCHAR",
    "ordinal_position": 147
  },
  {
    "name": "column147",
    "type": "VARCHAR",
    "ordinal_position": 148
  },
  {
    "name": "column148",
    "type": "VARCHAR",
    "ordinal_position": 149
  },
  {
    "name": "column149",
    "type": "VARCHAR",
    "ordinal_position": 150
  },
  {
    "name": "column150",
    "type": "VARCHAR",
    "ordinal_position": 151
  },
  {
    "name": "column151",
    "type": "VARCHAR",
    "ordinal_position": 152
  },
  {
    "name": "column152",
    "type": "VARCHAR",
    "ordinal_position": 153
  },
  {
    "name": "column153",
    "type": "VARCHAR",
    "ordinal_position": 154
  },
  {
    "name": "column154",
    "type": "VARCHAR",
    "ordinal_position": 155
  },
  {
    "name": "column155",
    "type": "VARCHAR",
    "ordinal_position": 156
  },
  {
    "name": "column156",
    "type": "VARCHAR",
    "ordinal_position": 157
  },
  {
    "name": "column157",
    "type": "VARCHAR",
    "ordinal_position": 158
  },
  {
    "name": "column158",
    "type": "VARCHAR",
    "ordinal_position": 159
  },
  {
    "name": "column159",
    "type": "DOUBLE",
    "ordinal_position": 160
  },
  {
    "name": "column160",
    "type": "DOUBLE",
    "ordinal_position": 161
  },
  {
    "name": "column161",
    "type": "VARCHAR",
    "ordinal_position": 162
  },
  {
    "name": "column162",
    "type": "VARCHAR",
    "ordinal_position": 163
  },
  {
    "name": "column163",
    "type": "VARCHAR",
    "ordinal_position": 164
  },
  {
    "name": "column164",
    "type": "VARCHAR",
    "ordinal_position": 165
  },
  {
    "name": "column165",
    "type": "VARCHAR",
    "ordinal_position": 166
  },
  {
    "name": "column166",
    "type": "VARCHAR",
    "ordinal_position": 167
  },
  {
    "name": "column167",
    "type": "VARCHAR",
    "ordinal_position": 168
  },
  {
    "name": "column168",
    "type": "VARCHAR",
    "ordinal_position": 169
  },
  {
    "name": "column169",
    "type": "VARCHAR",
    "ordinal_position": 170
  },
  {
    "name": "column170",
    "type": "VARCHAR",
    "ordinal_position": 171
  },
  {
    "name": "column171",
    "type": "VARCHAR",
    "ordinal_position": 172
  },
  {
    "name": "column172",
    "type": "VARCHAR",
    "ordinal_position": 173
  },
  {
    "name": "column173",
    "type": "VARCHAR",
    "ordinal_position": 174
  },
  {
    "name": "column174",
    "type": "VARCHAR",
    "ordinal_position": 175
  },
  {
    "name": "column175",
    "type": "VARCHAR",
    "ordinal_position": 176
  },
  {
    "name": "column176",
    "type": "VARCHAR",
    "ordinal_position": 177
  },
  {
    "name": "column177",
    "type": "VARCHAR",
    "ordinal_position": 178
  },
  {
    "name": "column178",
    "type": "VARCHAR",
    "ordinal_position": 179
  },
  {
    "name": "column179",
    "type": "VARCHAR",
    "ordinal_position": 180
  },
  {
    "name": "column180",
    "type": "VARCHAR",
    "ordinal_position": 181
  },
  {
    "name": "column181",
    "type": "VARCHAR",
    "ordinal_position": 182
  },
  {
    "name": "column182",
    "type": "VARCHAR",
    "ordinal_position": 183
  },
  {
    "name": "column183",
    "type": "VARCHAR",
    "ordinal_position": 184
  },
  {
    "name": "column184",
    "type": "VARCHAR",
    "ordinal_position": 185
  },
  {
    "name": "column185",
    "type": "VARCHAR",
    "ordinal_position": 186
  },
  {
    "name": "column186",
    "type": "VARCHAR",
    "ordinal_position": 187
  },
  {
    "name": "column187",
    "type": "VARCHAR",
    "ordinal_position": 188
  },
  {
    "name": "column188",
    "type": "VARCHAR",
    "ordinal_position": 189
  },
  {
    "name": "column189",
    "type": "VARCHAR",
    "ordinal_position": 190
  },
  {
    "name": "column190",
    "type": "VARCHAR",
    "ordinal_position": 191
  },
  {
    "name": "column191",
    "type": "VARCHAR",
    "ordinal_position": 192
  },
  {
    "name": "column192",
    "type": "VARCHAR",
    "ordinal_position": 193
  },
  {
    "name": "column193",
    "type": "VARCHAR",
    "ordinal_position": 194
  },
  {
    "name": "column194",
    "type": "VARCHAR",
    "ordinal_position": 195
  },
  {
    "name": "column195",
    "type": "VARCHAR",
    "ordinal_position": 196
  },
  {
    "name": "column196",
    "type": "VARCHAR",
    "ordinal_position": 197
  },
  {
    "name": "column197",
    "type": "VARCHAR",
    "ordinal_position": 198
  },
  {
    "name": "column198",
    "type": "VARCHAR",
    "ordinal_position": 199
  }
]
```

type_differences

```json
[
  {
    "column": "DATETIME",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  },
  {
    "column": "PROPERTY_COMPARE_AT_PRICE",
    "initial_type": "VARCHAR",
    "agent_type": "DOUBLE"
  },
  {
    "column": "PROPERTY_ITEM_COUNT",
    "initial_type": "VARCHAR",
    "agent_type": "BIGINT"
  },
  {
    "column": "PROPERTY_PRICE",
    "initial_type": "VARCHAR",
    "agent_type": "DOUBLE"
  },
  {
    "column": "TIMESTAMP",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  },
  {
    "column": "_FIVETRAN_DELETED",
    "initial_type": "VARCHAR",
    "agent_type": "BOOLEAN"
  },
  {
    "column": "_FIVETRAN_SYNCED",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  }
]
```

### raw.flow

初始存在：True；agent 存在：True；初始行数：79；agent 行数：79。

initial_only_columns

```json
[
  {
    "name": "ID",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "NAME",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "STATUS",
    "type": "VARCHAR",
    "ordinal_position": 3
  },
  {
    "name": "CREATED",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "UPDATED",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "CUSTOMER_FILTER",
    "type": "VARCHAR",
    "ordinal_position": 6
  },
  {
    "name": "_FIVETRAN_DELETED",
    "type": "VARCHAR",
    "ordinal_position": 7
  },
  {
    "name": "_FIVETRAN_SYNCED",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "ARCHIVED",
    "type": "VARCHAR",
    "ordinal_position": 9
  },
  {
    "name": "TRIGGER_TYPE",
    "type": "VARCHAR",
    "ordinal_position": 10
  }
]
```

agent_only_columns

```json
[
  {
    "name": "id",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "name",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "status",
    "type": "VARCHAR",
    "ordinal_position": 3
  },
  {
    "name": "created",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "updated",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "customer_filter",
    "type": "VARCHAR",
    "ordinal_position": 6
  },
  {
    "name": "_fivetran_deleted",
    "type": "BOOLEAN",
    "ordinal_position": 7
  },
  {
    "name": "_fivetran_synced",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "archived",
    "type": "BOOLEAN",
    "ordinal_position": 9
  },
  {
    "name": "trigger_type",
    "type": "VARCHAR",
    "ordinal_position": 10
  }
]
```

### raw.metric

初始存在：True；agent 存在：True；初始行数：29；agent 行数：29。

initial_only_columns

```json
[
  {
    "name": "ID",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "NAME",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "INTEGRATION_ID",
    "type": "VARCHAR",
    "ordinal_position": 3
  },
  {
    "name": "CREATED",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "UPDATED",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "_FIVETRAN_DELETED",
    "type": "VARCHAR",
    "ordinal_position": 6
  },
  {
    "name": "_FIVETRAN_SYNCED",
    "type": "VARCHAR",
    "ordinal_position": 7
  },
  {
    "name": "INTEGRATION_CATEGORY",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "INTEGRATION_NAME",
    "type": "VARCHAR",
    "ordinal_position": 9
  }
]
```

agent_only_columns

```json
[
  {
    "name": "id",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "name",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "integration_id",
    "type": "VARCHAR",
    "ordinal_position": 3
  },
  {
    "name": "created",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "updated",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "_fivetran_deleted",
    "type": "BOOLEAN",
    "ordinal_position": 6
  },
  {
    "name": "_fivetran_synced",
    "type": "VARCHAR",
    "ordinal_position": 7
  },
  {
    "name": "integration_category",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "integration_name",
    "type": "VARCHAR",
    "ordinal_position": 9
  }
]
```

### raw.person

初始存在：True；agent 存在：True；初始行数：1199；agent 行数：1200。

agent_only_columns

```json
[
  {
    "name": "column069",
    "type": "TIMESTAMP",
    "ordinal_position": 70
  },
  {
    "name": "column070",
    "type": "TIMESTAMP",
    "ordinal_position": 71
  },
  {
    "name": "column071",
    "type": "BOOLEAN",
    "ordinal_position": 72
  },
  {
    "name": "column072",
    "type": "VARCHAR",
    "ordinal_position": 73
  },
  {
    "name": "column073",
    "type": "VARCHAR",
    "ordinal_position": 74
  },
  {
    "name": "column074",
    "type": "VARCHAR",
    "ordinal_position": 75
  },
  {
    "name": "column075",
    "type": "VARCHAR",
    "ordinal_position": 76
  },
  {
    "name": "column076",
    "type": "VARCHAR",
    "ordinal_position": 77
  },
  {
    "name": "column077",
    "type": "VARCHAR",
    "ordinal_position": 78
  },
  {
    "name": "column078",
    "type": "VARCHAR",
    "ordinal_position": 79
  },
  {
    "name": "column079",
    "type": "VARCHAR",
    "ordinal_position": 80
  },
  {
    "name": "column080",
    "type": "DOUBLE",
    "ordinal_position": 81
  },
  {
    "name": "column081",
    "type": "DOUBLE",
    "ordinal_position": 82
  },
  {
    "name": "column082",
    "type": "BIGINT",
    "ordinal_position": 83
  },
  {
    "name": "column083",
    "type": "VARCHAR",
    "ordinal_position": 84
  },
  {
    "name": "column084",
    "type": "BIGINT",
    "ordinal_position": 85
  },
  {
    "name": "column085",
    "type": "VARCHAR",
    "ordinal_position": 86
  },
  {
    "name": "column086",
    "type": "VARCHAR",
    "ordinal_position": 87
  },
  {
    "name": "column087",
    "type": "VARCHAR",
    "ordinal_position": 88
  },
  {
    "name": "column088",
    "type": "VARCHAR",
    "ordinal_position": 89
  },
  {
    "name": "column089",
    "type": "BOOLEAN",
    "ordinal_position": 90
  },
  {
    "name": "column090",
    "type": "VARCHAR",
    "ordinal_position": 91
  },
  {
    "name": "column091",
    "type": "TIMESTAMP",
    "ordinal_position": 92
  },
  {
    "name": "column092",
    "type": "VARCHAR",
    "ordinal_position": 93
  },
  {
    "name": "column093",
    "type": "VARCHAR",
    "ordinal_position": 94
  },
  {
    "name": "column094",
    "type": "VARCHAR",
    "ordinal_position": 95
  },
  {
    "name": "column095",
    "type": "VARCHAR",
    "ordinal_position": 96
  },
  {
    "name": "column096",
    "type": "VARCHAR",
    "ordinal_position": 97
  },
  {
    "name": "column097",
    "type": "VARCHAR",
    "ordinal_position": 98
  },
  {
    "name": "column098",
    "type": "VARCHAR",
    "ordinal_position": 99
  },
  {
    "name": "column099",
    "type": "VARCHAR",
    "ordinal_position": 100
  },
  {
    "name": "column100",
    "type": "TIMESTAMP",
    "ordinal_position": 101
  },
  {
    "name": "column101",
    "type": "VARCHAR",
    "ordinal_position": 102
  },
  {
    "name": "column102",
    "type": "TIMESTAMP",
    "ordinal_position": 103
  },
  {
    "name": "column103",
    "type": "VARCHAR",
    "ordinal_position": 104
  },
  {
    "name": "column104",
    "type": "VARCHAR",
    "ordinal_position": 105
  },
  {
    "name": "column105",
    "type": "VARCHAR",
    "ordinal_position": 106
  },
  {
    "name": "column106",
    "type": "VARCHAR",
    "ordinal_position": 107
  },
  {
    "name": "column107",
    "type": "VARCHAR",
    "ordinal_position": 108
  },
  {
    "name": "column108",
    "type": "VARCHAR",
    "ordinal_position": 109
  },
  {
    "name": "column109",
    "type": "VARCHAR",
    "ordinal_position": 110
  },
  {
    "name": "column110",
    "type": "BIGINT",
    "ordinal_position": 111
  },
  {
    "name": "column111",
    "type": "VARCHAR",
    "ordinal_position": 112
  },
  {
    "name": "column112",
    "type": "BOOLEAN",
    "ordinal_position": 113
  },
  {
    "name": "column113",
    "type": "VARCHAR",
    "ordinal_position": 114
  },
  {
    "name": "column114",
    "type": "VARCHAR",
    "ordinal_position": 115
  },
  {
    "name": "column115",
    "type": "VARCHAR",
    "ordinal_position": 116
  },
  {
    "name": "column116",
    "type": "VARCHAR",
    "ordinal_position": 117
  },
  {
    "name": "column117",
    "type": "VARCHAR",
    "ordinal_position": 118
  },
  {
    "name": "column118",
    "type": "VARCHAR",
    "ordinal_position": 119
  },
  {
    "name": "column119",
    "type": "VARCHAR",
    "ordinal_position": 120
  },
  {
    "name": "column120",
    "type": "TIMESTAMP",
    "ordinal_position": 121
  },
  {
    "name": "column121",
    "type": "BOOLEAN",
    "ordinal_position": 122
  },
  {
    "name": "column122",
    "type": "VARCHAR",
    "ordinal_position": 123
  },
  {
    "name": "column123",
    "type": "VARCHAR",
    "ordinal_position": 124
  },
  {
    "name": "column124",
    "type": "VARCHAR",
    "ordinal_position": 125
  },
  {
    "name": "column125",
    "type": "VARCHAR",
    "ordinal_position": 126
  },
  {
    "name": "column126",
    "type": "VARCHAR",
    "ordinal_position": 127
  },
  {
    "name": "column127",
    "type": "VARCHAR",
    "ordinal_position": 128
  },
  {
    "name": "column128",
    "type": "VARCHAR",
    "ordinal_position": 129
  },
  {
    "name": "column129",
    "type": "BOOLEAN",
    "ordinal_position": 130
  },
  {
    "name": "column130",
    "type": "BOOLEAN",
    "ordinal_position": 131
  },
  {
    "name": "column131",
    "type": "BOOLEAN",
    "ordinal_position": 132
  },
  {
    "name": "column132",
    "type": "VARCHAR",
    "ordinal_position": 133
  },
  {
    "name": "column133",
    "type": "VARCHAR",
    "ordinal_position": 134
  },
  {
    "name": "column134",
    "type": "VARCHAR",
    "ordinal_position": 135
  },
  {
    "name": "column135",
    "type": "VARCHAR",
    "ordinal_position": 136
  },
  {
    "name": "column136",
    "type": "TIMESTAMP",
    "ordinal_position": 137
  }
]
```

type_differences

```json
[
  {
    "column": "CREATED",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  },
  {
    "column": "CUSTOM_ACCEPTS_MARKETING",
    "initial_type": "VARCHAR",
    "agent_type": "BOOLEAN"
  },
  {
    "column": "CUSTOM_CONSENT_FORM_VERSION",
    "initial_type": "VARCHAR",
    "agent_type": "BIGINT"
  },
  {
    "column": "CUSTOM_CONSENT_TIMESTAMP",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  },
  {
    "column": "CUSTOM_EXPECTED_DATE_OF_NEXT_ORDER",
    "initial_type": "VARCHAR",
    "agent_type": "DATE"
  },
  {
    "column": "CUSTOM_FIRST_PURCHASE_DATE_",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  },
  {
    "column": "CUSTOM_LAST_SIGN_IN",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  },
  {
    "column": "CUSTOM_RAF_SUBSCRIBE",
    "initial_type": "VARCHAR",
    "agent_type": "BOOLEAN"
  },
  {
    "column": "CUSTOM_SMS_ATTENTIVE_SIGNUP",
    "initial_type": "VARCHAR",
    "agent_type": "BOOLEAN"
  },
  {
    "column": "CUSTOM_SMS_CONSENT",
    "initial_type": "VARCHAR",
    "agent_type": "BOOLEAN"
  },
  {
    "column": "CUSTOM_SUPPRESS",
    "initial_type": "VARCHAR",
    "agent_type": "BOOLEAN"
  },
  {
    "column": "CUSTOM_UNENGAGED",
    "initial_type": "VARCHAR",
    "agent_type": "BOOLEAN"
  },
  {
    "column": "CUSTOM_ZIPCODE",
    "initial_type": "VARCHAR",
    "agent_type": "BIGINT"
  },
  {
    "column": "LAST_EVENT_DATE",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  },
  {
    "column": "LATITUDE",
    "initial_type": "VARCHAR",
    "agent_type": "DOUBLE"
  },
  {
    "column": "LONGITUDE",
    "initial_type": "VARCHAR",
    "agent_type": "DOUBLE"
  },
  {
    "column": "UPDATED",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  },
  {
    "column": "ZIP",
    "initial_type": "VARCHAR",
    "agent_type": "BIGINT"
  },
  {
    "column": "_FIVETRAN_DELETED",
    "initial_type": "VARCHAR",
    "agent_type": "BOOLEAN"
  },
  {
    "column": "_FIVETRAN_SYNCED",
    "initial_type": "VARCHAR",
    "agent_type": "TIMESTAMP"
  }
]
```

## impl-025

### raw.call_data_snowflake

初始存在：True；agent 存在：True；初始行数：2500；agent 行数：2500。

initial_only_columns

```json
[
  {
    "name": "\"\"\"FROM\"\"\"",
    "type": "BIGINT",
    "ordinal_position": 12
  },
  {
    "name": "\"\"\"TO\"\"\"",
    "type": "BIGINT",
    "ordinal_position": 22
  }
]
```

agent_only_columns

```json
[
  {
    "name": "\"FROM\"",
    "type": "BIGINT",
    "ordinal_position": 12
  },
  {
    "name": "\"TO\"",
    "type": "BIGINT",
    "ordinal_position": 22
  }
]
```

### raw.message_data_snowflake

初始存在：True；agent 存在：True；初始行数：2500；agent 行数：2500。

initial_only_columns

```json
[
  {
    "name": "\"\"\"FROM\"\"\"",
    "type": "BIGINT",
    "ordinal_position": 10
  },
  {
    "name": "\"\"\"TO\"\"\"",
    "type": "BIGINT",
    "ordinal_position": 17
  }
]
```

agent_only_columns

```json
[
  {
    "name": "\"FROM\"",
    "type": "BIGINT",
    "ordinal_position": 10
  },
  {
    "name": "\"TO\"",
    "type": "BIGINT",
    "ordinal_position": 17
  }
]
```

## impl-029

### raw.brand_data_postgres

初始存在：True；agent 存在：True；初始行数：1；agent 行数：1。

initial_only_columns

```json
[
  {
    "name": "\"default\"",
    "type": "VARCHAR",
    "ordinal_position": 6
  }
]
```

agent_only_columns

```json
[
  {
    "name": "default",
    "type": "VARCHAR",
    "ordinal_position": 6
  }
]
```

### raw.user_data_snowflake

初始存在：True；agent 存在：True；初始行数：10；agent 行数：10。

initial_only_columns

```json
[
  {
    "name": "\"ACTIVE\"",
    "type": "VARCHAR",
    "ordinal_position": 3
  }
]
```

agent_only_columns

```json
[
  {
    "name": "ACTIVE",
    "type": "VARCHAR",
    "ordinal_position": 3
  }
]
```

## impl-030

### raw.zuora_account_data

初始存在：True；agent 存在：True；初始行数：7504；agent 行数：7504。

initial_only_columns

```json
[
  {
    "name": "id,_fivetran_deleted,_fivetran_synced,account_number,additional_email_addresses,allow_invoice_edit,auto_pay,balance,bcd_setting_option,bill_cycle_day,bill_to_contact_id,bill_to_id,communication_profile_id,created_by_id,created_date,credit_balance,crm_id,currency,customer_service_rep_name,default_payment_method_id,invoice_delivery_prefs_email,invoice_delivery_prefs_print,invoice_template_id,last_invoice_date,mrr,name,notes,parent_account_id,parent_id,payment_gateway,payment_term,purchase_order_number,sales_rep_name,sequence_set_id,sold_to_contact_id,sold_to_id,status,tax_company_code,tax_exempt_certificate_id,tax_exempt_certificate_type,tax_exempt_description,tax_exempt_effective_date,tax_exempt_entity_use_code,tax_exempt_expiration_date,tax_exempt_issuing_jurisdiction,tax_exempt_status,testcustom_1_c,testcustom_2_c,total_debit_memo_balance,total_invoice_balance,unapplied_balance,unapplied_credit_memo_amount,updated_by_id,updated_date,vatid,batch",
    "type": "VARCHAR",
    "ordinal_position": 1
  }
]
```

agent_only_columns

```json
[
  {
    "name": "id",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "_fivetran_deleted",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "_fivetran_synced",
    "type": "VARCHAR",
    "ordinal_position": 3
  },
  {
    "name": "account_number",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "additional_email_addresses",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "allow_invoice_edit",
    "type": "VARCHAR",
    "ordinal_position": 6
  },
  {
    "name": "auto_pay",
    "type": "VARCHAR",
    "ordinal_position": 7
  },
  {
    "name": "balance",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "bcd_setting_option",
    "type": "VARCHAR",
    "ordinal_position": 9
  },
  {
    "name": "bill_cycle_day",
    "type": "VARCHAR",
    "ordinal_position": 10
  },
  {
    "name": "bill_to_contact_id",
    "type": "VARCHAR",
    "ordinal_position": 11
  },
  {
    "name": "bill_to_id",
    "type": "VARCHAR",
    "ordinal_position": 12
  },
  {
    "name": "communication_profile_id",
    "type": "VARCHAR",
    "ordinal_position": 13
  },
  {
    "name": "created_by_id",
    "type": "VARCHAR",
    "ordinal_position": 14
  },
  {
    "name": "created_date",
    "type": "VARCHAR",
    "ordinal_position": 15
  },
  {
    "name": "credit_balance",
    "type": "VARCHAR",
    "ordinal_position": 16
  },
  {
    "name": "crm_id",
    "type": "VARCHAR",
    "ordinal_position": 17
  },
  {
    "name": "currency",
    "type": "VARCHAR",
    "ordinal_position": 18
  },
  {
    "name": "customer_service_rep_name",
    "type": "VARCHAR",
    "ordinal_position": 19
  },
  {
    "name": "default_payment_method_id",
    "type": "VARCHAR",
    "ordinal_position": 20
  },
  {
    "name": "invoice_delivery_prefs_email",
    "type": "VARCHAR",
    "ordinal_position": 21
  },
  {
    "name": "invoice_delivery_prefs_print",
    "type": "VARCHAR",
    "ordinal_position": 22
  },
  {
    "name": "invoice_template_id",
    "type": "VARCHAR",
    "ordinal_position": 23
  },
  {
    "name": "last_invoice_date",
    "type": "VARCHAR",
    "ordinal_position": 24
  },
  {
    "name": "mrr",
    "type": "VARCHAR",
    "ordinal_position": 25
  },
  {
    "name": "name",
    "type": "VARCHAR",
    "ordinal_position": 26
  },
  {
    "name": "notes",
    "type": "VARCHAR",
    "ordinal_position": 27
  },
  {
    "name": "parent_account_id",
    "type": "VARCHAR",
    "ordinal_position": 28
  },
  {
    "name": "parent_id",
    "type": "VARCHAR",
    "ordinal_position": 29
  },
  {
    "name": "payment_gateway",
    "type": "VARCHAR",
    "ordinal_position": 30
  },
  {
    "name": "payment_term",
    "type": "VARCHAR",
    "ordinal_position": 31
  },
  {
    "name": "purchase_order_number",
    "type": "VARCHAR",
    "ordinal_position": 32
  },
  {
    "name": "sales_rep_name",
    "type": "VARCHAR",
    "ordinal_position": 33
  },
  {
    "name": "sequence_set_id",
    "type": "VARCHAR",
    "ordinal_position": 34
  },
  {
    "name": "sold_to_contact_id",
    "type": "VARCHAR",
    "ordinal_position": 35
  },
  {
    "name": "sold_to_id",
    "type": "VARCHAR",
    "ordinal_position": 36
  },
  {
    "name": "status",
    "type": "VARCHAR",
    "ordinal_position": 37
  },
  {
    "name": "tax_company_code",
    "type": "VARCHAR",
    "ordinal_position": 38
  },
  {
    "name": "tax_exempt_certificate_id",
    "type": "VARCHAR",
    "ordinal_position": 39
  },
  {
    "name": "tax_exempt_certificate_type",
    "type": "VARCHAR",
    "ordinal_position": 40
  },
  {
    "name": "tax_exempt_description",
    "type": "VARCHAR",
    "ordinal_position": 41
  },
  {
    "name": "tax_exempt_effective_date",
    "type": "VARCHAR",
    "ordinal_position": 42
  },
  {
    "name": "tax_exempt_entity_use_code",
    "type": "VARCHAR",
    "ordinal_position": 43
  },
  {
    "name": "tax_exempt_expiration_date",
    "type": "VARCHAR",
    "ordinal_position": 44
  },
  {
    "name": "tax_exempt_issuing_jurisdiction",
    "type": "VARCHAR",
    "ordinal_position": 45
  },
  {
    "name": "tax_exempt_status",
    "type": "VARCHAR",
    "ordinal_position": 46
  },
  {
    "name": "testcustom_1_c",
    "type": "VARCHAR",
    "ordinal_position": 47
  },
  {
    "name": "testcustom_2_c",
    "type": "VARCHAR",
    "ordinal_position": 48
  },
  {
    "name": "total_debit_memo_balance",
    "type": "VARCHAR",
    "ordinal_position": 49
  },
  {
    "name": "total_invoice_balance",
    "type": "VARCHAR",
    "ordinal_position": 50
  },
  {
    "name": "unapplied_balance",
    "type": "VARCHAR",
    "ordinal_position": 51
  },
  {
    "name": "unapplied_credit_memo_amount",
    "type": "VARCHAR",
    "ordinal_position": 52
  },
  {
    "name": "updated_by_id",
    "type": "VARCHAR",
    "ordinal_position": 53
  },
  {
    "name": "updated_date",
    "type": "VARCHAR",
    "ordinal_position": 54
  },
  {
    "name": "vatid",
    "type": "VARCHAR",
    "ordinal_position": 55
  },
  {
    "name": "batch",
    "type": "VARCHAR",
    "ordinal_position": 56
  }
]
```

### raw.zuora_amendment_data

初始存在：True；agent 存在：True；初始行数：505；agent 行数：505。

initial_only_columns

```json
[
  {
    "name": "id,_fivetran_deleted,_fivetran_synced,auto_renew,booking_date,code,contract_effective_date,created_by_id,created_date,current_term,current_term_period_type,customer_acceptance_date,description,effective_date,effective_policy,name,new_rate_plan_id,removed_rate_plan_id,renewal_setting,renewal_term,renewal_term_period_type,resume_date,service_activation_date,specific_update_date,status,sub_type,subscription_id,suspend_date,term_start_date,term_type,type,updated_by_id,updated_date",
    "type": "VARCHAR",
    "ordinal_position": 1
  }
]
```

agent_only_columns

```json
[
  {
    "name": "id",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "_fivetran_deleted",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "_fivetran_synced",
    "type": "VARCHAR",
    "ordinal_position": 3
  },
  {
    "name": "auto_renew",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "booking_date",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "code",
    "type": "VARCHAR",
    "ordinal_position": 6
  },
  {
    "name": "contract_effective_date",
    "type": "VARCHAR",
    "ordinal_position": 7
  },
  {
    "name": "created_by_id",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "created_date",
    "type": "VARCHAR",
    "ordinal_position": 9
  },
  {
    "name": "current_term",
    "type": "VARCHAR",
    "ordinal_position": 10
  },
  {
    "name": "current_term_period_type",
    "type": "VARCHAR",
    "ordinal_position": 11
  },
  {
    "name": "customer_acceptance_date",
    "type": "VARCHAR",
    "ordinal_position": 12
  },
  {
    "name": "description",
    "type": "VARCHAR",
    "ordinal_position": 13
  },
  {
    "name": "effective_date",
    "type": "VARCHAR",
    "ordinal_position": 14
  },
  {
    "name": "effective_policy",
    "type": "VARCHAR",
    "ordinal_position": 15
  },
  {
    "name": "name",
    "type": "VARCHAR",
    "ordinal_position": 16
  },
  {
    "name": "new_rate_plan_id",
    "type": "VARCHAR",
    "ordinal_position": 17
  },
  {
    "name": "removed_rate_plan_id",
    "type": "VARCHAR",
    "ordinal_position": 18
  },
  {
    "name": "renewal_setting",
    "type": "VARCHAR",
    "ordinal_position": 19
  },
  {
    "name": "renewal_term",
    "type": "VARCHAR",
    "ordinal_position": 20
  },
  {
    "name": "renewal_term_period_type",
    "type": "VARCHAR",
    "ordinal_position": 21
  },
  {
    "name": "resume_date",
    "type": "VARCHAR",
    "ordinal_position": 22
  },
  {
    "name": "service_activation_date",
    "type": "VARCHAR",
    "ordinal_position": 23
  },
  {
    "name": "specific_update_date",
    "type": "VARCHAR",
    "ordinal_position": 24
  },
  {
    "name": "status",
    "type": "VARCHAR",
    "ordinal_position": 25
  },
  {
    "name": "sub_type",
    "type": "VARCHAR",
    "ordinal_position": 26
  },
  {
    "name": "subscription_id",
    "type": "VARCHAR",
    "ordinal_position": 27
  },
  {
    "name": "suspend_date",
    "type": "VARCHAR",
    "ordinal_position": 28
  },
  {
    "name": "term_start_date",
    "type": "VARCHAR",
    "ordinal_position": 29
  },
  {
    "name": "term_type",
    "type": "VARCHAR",
    "ordinal_position": 30
  },
  {
    "name": "type",
    "type": "VARCHAR",
    "ordinal_position": 31
  },
  {
    "name": "updated_by_id",
    "type": "VARCHAR",
    "ordinal_position": 32
  },
  {
    "name": "updated_date",
    "type": "VARCHAR",
    "ordinal_position": 33
  }
]
```

### raw.zuora_contact_data

初始存在：True；agent 存在：True；初始行数：7504；agent 行数：7504。

initial_only_columns

```json
[
  {
    "name": "id,_fivetran_deleted,_fivetran_synced,account_id,address_1,address_2,city,country,county,created_by_id,created_date,description,fax,first_name,home_phone,last_name,mobile_phone,nick_name,other_phone,other_phone_type,personal_email,postal_code,state,tax_region,updated_by_id,updated_date,work_email,work_phone",
    "type": "VARCHAR",
    "ordinal_position": 1
  }
]
```

agent_only_columns

```json
[
  {
    "name": "id",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "_fivetran_deleted",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "_fivetran_synced",
    "type": "VARCHAR",
    "ordinal_position": 3
  },
  {
    "name": "account_id",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "address_1",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "address_2",
    "type": "VARCHAR",
    "ordinal_position": 6
  },
  {
    "name": "city",
    "type": "VARCHAR",
    "ordinal_position": 7
  },
  {
    "name": "country",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "county",
    "type": "VARCHAR",
    "ordinal_position": 9
  },
  {
    "name": "created_by_id",
    "type": "VARCHAR",
    "ordinal_position": 10
  },
  {
    "name": "created_date",
    "type": "VARCHAR",
    "ordinal_position": 11
  },
  {
    "name": "description",
    "type": "VARCHAR",
    "ordinal_position": 12
  },
  {
    "name": "fax",
    "type": "VARCHAR",
    "ordinal_position": 13
  },
  {
    "name": "first_name",
    "type": "VARCHAR",
    "ordinal_position": 14
  },
  {
    "name": "home_phone",
    "type": "VARCHAR",
    "ordinal_position": 15
  },
  {
    "name": "last_name",
    "type": "VARCHAR",
    "ordinal_position": 16
  },
  {
    "name": "mobile_phone",
    "type": "VARCHAR",
    "ordinal_position": 17
  },
  {
    "name": "nick_name",
    "type": "VARCHAR",
    "ordinal_position": 18
  },
  {
    "name": "other_phone",
    "type": "VARCHAR",
    "ordinal_position": 19
  },
  {
    "name": "other_phone_type",
    "type": "VARCHAR",
    "ordinal_position": 20
  },
  {
    "name": "personal_email",
    "type": "VARCHAR",
    "ordinal_position": 21
  },
  {
    "name": "postal_code",
    "type": "VARCHAR",
    "ordinal_position": 22
  },
  {
    "name": "state",
    "type": "VARCHAR",
    "ordinal_position": 23
  },
  {
    "name": "tax_region",
    "type": "VARCHAR",
    "ordinal_position": 24
  },
  {
    "name": "updated_by_id",
    "type": "VARCHAR",
    "ordinal_position": 25
  },
  {
    "name": "updated_date",
    "type": "VARCHAR",
    "ordinal_position": 26
  },
  {
    "name": "work_email",
    "type": "VARCHAR",
    "ordinal_position": 27
  },
  {
    "name": "work_phone",
    "type": "VARCHAR",
    "ordinal_position": 28
  }
]
```

### raw.zuora_invoice_data

初始存在：True；agent 存在：True；初始行数：2004；agent 行数：2004。

initial_only_columns

```json
[
  {
    "name": "id,_fivetran_deleted,_fivetran_synced,account_id,adjustment_amount,amount,amount_currency_rounding,amount_home_currency,amount_without_tax,amount_without_tax_currency_rounding,amount_without_tax_home_currency,auto_pay,balance,bill_to_contact_id,comments,created_by_id,created_date,credit_balance_adjustment_amount,default_payment_method_id,due_date,exchange_rate,exchange_rate_date,home_currency,includes_one_time,includes_recurring,includes_usage,invoice_date,invoice_number,last_email_sent_date,parent_account_id,payment_amount,payment_term,posted_by,posted_date,provider_exchange_rate_date,refund_amount,reversed,sold_to_contact_id,source,source_id,source_type,status,target_date,tax_amount,tax_exempt_amount,tax_message,tax_status,template_id,transaction_currency,transferred_to_accounting,updated_by_id,updated_date,sequence_set_id,credit_memo_amount",
    "type": "VARCHAR",
    "ordinal_position": 1
  }
]
```

agent_only_columns

```json
[
  {
    "name": "id",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "_fivetran_deleted",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "_fivetran_synced",
    "type": "VARCHAR",
    "ordinal_position": 3
  },
  {
    "name": "account_id",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "adjustment_amount",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "amount",
    "type": "VARCHAR",
    "ordinal_position": 6
  },
  {
    "name": "amount_currency_rounding",
    "type": "VARCHAR",
    "ordinal_position": 7
  },
  {
    "name": "amount_home_currency",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "amount_without_tax",
    "type": "VARCHAR",
    "ordinal_position": 9
  },
  {
    "name": "amount_without_tax_currency_rounding",
    "type": "VARCHAR",
    "ordinal_position": 10
  },
  {
    "name": "amount_without_tax_home_currency",
    "type": "VARCHAR",
    "ordinal_position": 11
  },
  {
    "name": "auto_pay",
    "type": "VARCHAR",
    "ordinal_position": 12
  },
  {
    "name": "balance",
    "type": "VARCHAR",
    "ordinal_position": 13
  },
  {
    "name": "bill_to_contact_id",
    "type": "VARCHAR",
    "ordinal_position": 14
  },
  {
    "name": "comments",
    "type": "VARCHAR",
    "ordinal_position": 15
  },
  {
    "name": "created_by_id",
    "type": "VARCHAR",
    "ordinal_position": 16
  },
  {
    "name": "created_date",
    "type": "VARCHAR",
    "ordinal_position": 17
  },
  {
    "name": "credit_balance_adjustment_amount",
    "type": "VARCHAR",
    "ordinal_position": 18
  },
  {
    "name": "default_payment_method_id",
    "type": "VARCHAR",
    "ordinal_position": 19
  },
  {
    "name": "due_date",
    "type": "VARCHAR",
    "ordinal_position": 20
  },
  {
    "name": "exchange_rate",
    "type": "VARCHAR",
    "ordinal_position": 21
  },
  {
    "name": "exchange_rate_date",
    "type": "VARCHAR",
    "ordinal_position": 22
  },
  {
    "name": "home_currency",
    "type": "VARCHAR",
    "ordinal_position": 23
  },
  {
    "name": "includes_one_time",
    "type": "VARCHAR",
    "ordinal_position": 24
  },
  {
    "name": "includes_recurring",
    "type": "VARCHAR",
    "ordinal_position": 25
  },
  {
    "name": "includes_usage",
    "type": "VARCHAR",
    "ordinal_position": 26
  },
  {
    "name": "invoice_date",
    "type": "VARCHAR",
    "ordinal_position": 27
  },
  {
    "name": "invoice_number",
    "type": "VARCHAR",
    "ordinal_position": 28
  },
  {
    "name": "last_email_sent_date",
    "type": "VARCHAR",
    "ordinal_position": 29
  },
  {
    "name": "parent_account_id",
    "type": "VARCHAR",
    "ordinal_position": 30
  },
  {
    "name": "payment_amount",
    "type": "VARCHAR",
    "ordinal_position": 31
  },
  {
    "name": "payment_term",
    "type": "VARCHAR",
    "ordinal_position": 32
  },
  {
    "name": "posted_by",
    "type": "VARCHAR",
    "ordinal_position": 33
  },
  {
    "name": "posted_date",
    "type": "VARCHAR",
    "ordinal_position": 34
  },
  {
    "name": "provider_exchange_rate_date",
    "type": "VARCHAR",
    "ordinal_position": 35
  },
  {
    "name": "refund_amount",
    "type": "VARCHAR",
    "ordinal_position": 36
  },
  {
    "name": "reversed",
    "type": "VARCHAR",
    "ordinal_position": 37
  },
  {
    "name": "sold_to_contact_id",
    "type": "VARCHAR",
    "ordinal_position": 38
  },
  {
    "name": "source",
    "type": "VARCHAR",
    "ordinal_position": 39
  },
  {
    "name": "source_id",
    "type": "VARCHAR",
    "ordinal_position": 40
  },
  {
    "name": "source_type",
    "type": "VARCHAR",
    "ordinal_position": 41
  },
  {
    "name": "status",
    "type": "VARCHAR",
    "ordinal_position": 42
  },
  {
    "name": "target_date",
    "type": "VARCHAR",
    "ordinal_position": 43
  },
  {
    "name": "tax_amount",
    "type": "VARCHAR",
    "ordinal_position": 44
  },
  {
    "name": "tax_exempt_amount",
    "type": "VARCHAR",
    "ordinal_position": 45
  },
  {
    "name": "tax_message",
    "type": "VARCHAR",
    "ordinal_position": 46
  },
  {
    "name": "tax_status",
    "type": "VARCHAR",
    "ordinal_position": 47
  },
  {
    "name": "template_id",
    "type": "VARCHAR",
    "ordinal_position": 48
  },
  {
    "name": "transaction_currency",
    "type": "VARCHAR",
    "ordinal_position": 49
  },
  {
    "name": "transferred_to_accounting",
    "type": "VARCHAR",
    "ordinal_position": 50
  },
  {
    "name": "updated_by_id",
    "type": "VARCHAR",
    "ordinal_position": 51
  },
  {
    "name": "updated_date",
    "type": "VARCHAR",
    "ordinal_position": 52
  },
  {
    "name": "sequence_set_id",
    "type": "VARCHAR",
    "ordinal_position": 53
  },
  {
    "name": "credit_memo_amount",
    "type": "VARCHAR",
    "ordinal_position": 54
  }
]
```

### raw.zuora_taxation_item_data

初始存在：True；agent 存在：True；初始行数：1005；agent 行数：1005。

initial_only_columns

```json
[
  {
    "name": "id,_fivetran_deleted,_fivetran_synced,account_id,account_receivable_accounting_code_id,accounting_code,accounting_period_id,amendment_id,balance,bill_to_contact_id,created_by_id,created_date,credit_amount,default_payment_method_id,exchange_rate,exchange_rate_date,exempt_amount,exempt_amount_currency_rounding,exempt_amount_home_currency,home_currency,invoice_id,invoice_item_id,journal_entry_id,journal_run_id,jurisdiction,location_code,name,payment_amount,product_id,product_rate_plan_charge_id,product_rate_plan_id,provider_exchange_rate_date,rate_plan_charge_id,rate_plan_id,sales_tax_payable_accounting_code_id,sold_to_contact_id,subscription_id,tax_amount,tax_amount_currency_rounding,tax_amount_home_currency,tax_code,tax_code_description,tax_date,tax_mode,tax_rate,tax_rate_description,tax_rate_type,transaction_currency,updated_by_id,updated_date,parent_account_id,seller_registration,tax_description,customer_code,tax_rule_id,exempt_certificate",
    "type": "VARCHAR",
    "ordinal_position": 1
  }
]
```

agent_only_columns

```json
[
  {
    "name": "id",
    "type": "VARCHAR",
    "ordinal_position": 1
  },
  {
    "name": "_fivetran_deleted",
    "type": "VARCHAR",
    "ordinal_position": 2
  },
  {
    "name": "_fivetran_synced",
    "type": "VARCHAR",
    "ordinal_position": 3
  },
  {
    "name": "account_id",
    "type": "VARCHAR",
    "ordinal_position": 4
  },
  {
    "name": "account_receivable_accounting_code_id",
    "type": "VARCHAR",
    "ordinal_position": 5
  },
  {
    "name": "accounting_code",
    "type": "VARCHAR",
    "ordinal_position": 6
  },
  {
    "name": "accounting_period_id",
    "type": "VARCHAR",
    "ordinal_position": 7
  },
  {
    "name": "amendment_id",
    "type": "VARCHAR",
    "ordinal_position": 8
  },
  {
    "name": "balance",
    "type": "VARCHAR",
    "ordinal_position": 9
  },
  {
    "name": "bill_to_contact_id",
    "type": "VARCHAR",
    "ordinal_position": 10
  },
  {
    "name": "created_by_id",
    "type": "VARCHAR",
    "ordinal_position": 11
  },
  {
    "name": "created_date",
    "type": "VARCHAR",
    "ordinal_position": 12
  },
  {
    "name": "credit_amount",
    "type": "VARCHAR",
    "ordinal_position": 13
  },
  {
    "name": "default_payment_method_id",
    "type": "VARCHAR",
    "ordinal_position": 14
  },
  {
    "name": "exchange_rate",
    "type": "VARCHAR",
    "ordinal_position": 15
  },
  {
    "name": "exchange_rate_date",
    "type": "VARCHAR",
    "ordinal_position": 16
  },
  {
    "name": "exempt_amount",
    "type": "VARCHAR",
    "ordinal_position": 17
  },
  {
    "name": "exempt_amount_currency_rounding",
    "type": "VARCHAR",
    "ordinal_position": 18
  },
  {
    "name": "exempt_amount_home_currency",
    "type": "VARCHAR",
    "ordinal_position": 19
  },
  {
    "name": "home_currency",
    "type": "VARCHAR",
    "ordinal_position": 20
  },
  {
    "name": "invoice_id",
    "type": "VARCHAR",
    "ordinal_position": 21
  },
  {
    "name": "invoice_item_id",
    "type": "VARCHAR",
    "ordinal_position": 22
  },
  {
    "name": "journal_entry_id",
    "type": "VARCHAR",
    "ordinal_position": 23
  },
  {
    "name": "journal_run_id",
    "type": "VARCHAR",
    "ordinal_position": 24
  },
  {
    "name": "jurisdiction",
    "type": "VARCHAR",
    "ordinal_position": 25
  },
  {
    "name": "location_code",
    "type": "VARCHAR",
    "ordinal_position": 26
  },
  {
    "name": "name",
    "type": "VARCHAR",
    "ordinal_position": 27
  },
  {
    "name": "payment_amount",
    "type": "VARCHAR",
    "ordinal_position": 28
  },
  {
    "name": "product_id",
    "type": "VARCHAR",
    "ordinal_position": 29
  },
  {
    "name": "product_rate_plan_charge_id",
    "type": "VARCHAR",
    "ordinal_position": 30
  },
  {
    "name": "product_rate_plan_id",
    "type": "VARCHAR",
    "ordinal_position": 31
  },
  {
    "name": "provider_exchange_rate_date",
    "type": "VARCHAR",
    "ordinal_position": 32
  },
  {
    "name": "rate_plan_charge_id",
    "type": "VARCHAR",
    "ordinal_position": 33
  },
  {
    "name": "rate_plan_id",
    "type": "VARCHAR",
    "ordinal_position": 34
  },
  {
    "name": "sales_tax_payable_accounting_code_id",
    "type": "VARCHAR",
    "ordinal_position": 35
  },
  {
    "name": "sold_to_contact_id",
    "type": "VARCHAR",
    "ordinal_position": 36
  },
  {
    "name": "subscription_id",
    "type": "VARCHAR",
    "ordinal_position": 37
  },
  {
    "name": "tax_amount",
    "type": "VARCHAR",
    "ordinal_position": 38
  },
  {
    "name": "tax_amount_currency_rounding",
    "type": "VARCHAR",
    "ordinal_position": 39
  },
  {
    "name": "tax_amount_home_currency",
    "type": "VARCHAR",
    "ordinal_position": 40
  },
  {
    "name": "tax_code",
    "type": "VARCHAR",
    "ordinal_position": 41
  },
  {
    "name": "tax_code_description",
    "type": "VARCHAR",
    "ordinal_position": 42
  },
  {
    "name": "tax_date",
    "type": "VARCHAR",
    "ordinal_position": 43
  },
  {
    "name": "tax_mode",
    "type": "VARCHAR",
    "ordinal_position": 44
  },
  {
    "name": "tax_rate",
    "type": "VARCHAR",
    "ordinal_position": 45
  },
  {
    "name": "tax_rate_description",
    "type": "VARCHAR",
    "ordinal_position": 46
  },
  {
    "name": "tax_rate_type",
    "type": "VARCHAR",
    "ordinal_position": 47
  },
  {
    "name": "transaction_currency",
    "type": "VARCHAR",
    "ordinal_position": 48
  },
  {
    "name": "updated_by_id",
    "type": "VARCHAR",
    "ordinal_position": 49
  },
  {
    "name": "updated_date",
    "type": "VARCHAR",
    "ordinal_position": 50
  },
  {
    "name": "parent_account_id",
    "type": "VARCHAR",
    "ordinal_position": 51
  },
  {
    "name": "seller_registration",
    "type": "VARCHAR",
    "ordinal_position": 52
  },
  {
    "name": "tax_description",
    "type": "VARCHAR",
    "ordinal_position": 53
  },
  {
    "name": "customer_code",
    "type": "VARCHAR",
    "ordinal_position": 54
  },
  {
    "name": "tax_rule_id",
    "type": "VARCHAR",
    "ordinal_position": 55
  },
  {
    "name": "exempt_certificate",
    "type": "VARCHAR",
    "ordinal_position": 56
  }
]
```
