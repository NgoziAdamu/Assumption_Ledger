# impl-018 / stg_salesforce__opportunity_line_item

## basic_information

```json
{
  "task": "impl-018",
  "layer": "staging",
  "table": "stg_salesforce__opportunity_line_item",
  "status": "待标注",
  "difference_source": {
    "kind": "original_007_009",
    "record": "records/007_tolerance_tables.jsonl",
    "detail_record": "/home/katherine/Assumption_Ledger/records/004_staging_impl-018.json",
    "candidate_date": null,
    "selection_reason": "未进入 011，沿用原差异"
  },
  "status_record": "records/012_statuses.jsonl",
  "package_scope": "仅原文和机械统计；未概括轨迹、未推测原因"
}
```

## contract_specification

```json
{
  "source_path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml",
  "source_sha256": "d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2",
  "parse_mode": "strict",
  "requested_table": "stg_salesforce__opportunity_line_item",
  "status": "found"
}
```
```json
{
  "yaml_path": [
    "staging_contract",
    "tables",
    9
  ],
  "start_line": 747,
  "end_line": 786
}
```
```yaml
    - name: stg_salesforce__opportunity_line_item
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

## agent_final_SQL

```json
{
  "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
  "sha256": "df414b04f8faa46e8fad09eeb3ffe15dbcc9a76d05d5719959d21892c402c16a",
  "start_line": 1,
  "end_line": 19
}
```
```sql
select
      id as opportunity_line_item_id,
      id as opportunity_id,
      id as product_2_id,
      try_cast(created_date as TIMESTAMP) as created_date,
      description as opportunity_line_item_description,
      has_quantity_schedule as has_quantity_schedule,
      has_revenue_schedule as has_revenue_schedule,
      is_deleted as is_deleted,
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
      try_cast(list_price as DECIMAL) as list_price,
      pricebook_entry_id as pricebook_entry_id,
      try_cast(quantity as DECIMAL) as quantity,
      try_cast(service_date as DATE) as service_date,
      try_cast(sort_order as INTEGER) as sort_order,
      try_cast(total_price as DECIMAL) as total_price,
      try_cast(unit_price as DECIMAL) as unit_price
from raw.opportunity_line_item
where id is not null
```

## gold_SQL_仅供定位差异

```json
{
  "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
  "sha256": "c3b135a6cdfa60c88537d1fa6a01db623e1a1c4ab412ec2cc6ba429bbb175a40",
  "start_line": 1,
  "end_line": 29
}
```
```sql
with fields as (
    select *
    from raw.opportunity_line_item
), 

final as (
    select
        cast(id as varchar) as opportunity_line_item_id,
        cast(opportunity_id as varchar) as opportunity_id,
        cast(product_2_id as varchar) as product_2_id,
        cast(created_date as timestamp) as created_date,
        cast(description as varchar) as opportunity_line_item_description,
        cast(coalesce(has_quantity_schedule, false) as boolean) as has_quantity_schedule,
        cast(coalesce(has_revenue_schedule, false) as boolean) as has_revenue_schedule,
        cast(coalesce(is_deleted, false) as boolean) as is_deleted,
        cast(last_modified_date as timestamp) as last_modified_date,
        cast(list_price as decimal) as list_price,
        cast(pricebook_entry_id as varchar) as pricebook_entry_id,
        cast(quantity as decimal) as quantity,
        cast(service_date as date) as service_date,
        cast(sort_order as integer) as sort_order,
        cast(total_price as decimal) as total_price,
        cast(unit_price as decimal) as unit_price
    from fields
)

select *
from final
where not coalesce(is_deleted, false)
```

## differences

```json
{
  "kind": "original_007_009",
  "record": "records/007_tolerance_tables.jsonl",
  "detail_record": "/home/katherine/Assumption_Ledger/records/004_staging_impl-018.json",
  "prediction_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb",
  "gold_database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb",
  "actual_schema": "staging",
  "table": "stg_salesforce__opportunity_line_item",
  "candidate_date": null,
  "comparison_columns": [
    "created_date",
    "has_quantity_schedule",
    "has_revenue_schedule",
    "is_deleted",
    "last_modified_date",
    "list_price",
    "opportunity_id",
    "pricebook_entry_id",
    "product_2_id",
    "quantity",
    "service_date",
    "sort_order",
    "total_price",
    "unit_price"
  ],
  "key_columns": [
    "opportunity_line_item_id"
  ],
  "prediction_rows": 3000,
  "gold_rows": 3000,
  "row_delta": 0,
  "key_statistics": {
    "pred_distinct_keys": 3000,
    "gold_distinct_keys": 3000,
    "pred_duplicate_key_groups": 0,
    "gold_duplicate_key_groups": 0,
    "pred_only_keys": 0,
    "gold_only_keys": 0,
    "shared_keys": 3000,
    "shared_nonunique_key_groups": 0
  },
  "l0_column_differences": [
    {
      "column": "opportunity_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 3000,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 3000,
      "pred_unmatched_value_occurrences": 3000,
      "gold_unmatched_value_occurrences": 3000,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "product_2_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 3000,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 3000,
      "pred_unmatched_value_occurrences": 3000,
      "gold_unmatched_value_occurrences": 3000,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "created_date",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "has_quantity_schedule",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "has_revenue_schedule",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "is_deleted",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "last_modified_date",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "list_price",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "pricebook_entry_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "quantity",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "service_date",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "sort_order",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "total_price",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "unit_price",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    }
  ],
  "l3_column_differences": [
    {
      "column": "created_date",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "has_quantity_schedule",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "has_revenue_schedule",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "is_deleted",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "last_modified_date",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "list_price",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "opportunity_id",
      "one_to_one_mismatch_rows": 3000,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 3000,
      "pred_unmatched_value_occurrences": 3000,
      "gold_unmatched_value_occurrences": 3000,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "pricebook_entry_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "product_2_id",
      "one_to_one_mismatch_rows": 3000,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 3000,
      "pred_unmatched_value_occurrences": 3000,
      "gold_unmatched_value_occurrences": 3000,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "quantity",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "service_date",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "sort_order",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "total_price",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "unit_price",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    }
  ],
  "whole_match_level": "仍不匹配",
  "keyed_match_level": "仍不匹配",
  "selection_reason": "未进入 011，沿用原差异",
  "value_representation": "Unmodified DuckDB CAST AS VARCHAR; SQL NULL is JSON null. Keys use the unchanged historical L0 normalization.",
  "new_queries_only_read_existing_results": true,
  "one_side_key_examples": {
    "prediction_only": [],
    "gold_only": []
  },
  "column_details": [
    {
      "column": "opportunity_id",
      "l0_counts_verbatim": {
        "column": "opportunity_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 3000,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 3000,
        "pred_unmatched_value_occurrences": 3000,
        "gold_unmatched_value_occurrences": 3000,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "opportunity_id",
        "one_to_one_mismatch_rows": 3000,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 3000,
        "pred_unmatched_value_occurrences": 3000,
        "gold_unmatched_value_occurrences": 3000,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "opportunity_line_item_id": "00k029dqfahx6ne"
          },
          "agent_key_raw_text": {
            "opportunity_line_item_id": "00k029DQfAHx6ne"
          },
          "gold_key_raw_text": {
            "opportunity_line_item_id": "00k029DQfAHx6ne"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "00k029DQfAHx6ne",
          "gold_value": "006qOaMamPeRpWP"
        },
        {
          "key_normalized": {
            "opportunity_line_item_id": "00k031neiuy8t7u"
          },
          "agent_key_raw_text": {
            "opportunity_line_item_id": "00k031NEIUy8T7U"
          },
          "gold_key_raw_text": {
            "opportunity_line_item_id": "00k031NEIUy8T7U"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "00k031NEIUy8T7U",
          "gold_value": "006xzqLEcGYSYmZ"
        },
        {
          "key_normalized": {
            "opportunity_line_item_id": "00k03mk8nktyeqn"
          },
          "agent_key_raw_text": {
            "opportunity_line_item_id": "00k03MK8NKTyEQn"
          },
          "gold_key_raw_text": {
            "opportunity_line_item_id": "00k03MK8NKTyEQn"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "00k03MK8NKTyEQn",
          "gold_value": "006neRhwd0tjLlF"
        },
        {
          "key_normalized": {
            "opportunity_line_item_id": "00k03ssa8vhlkhm"
          },
          "agent_key_raw_text": {
            "opportunity_line_item_id": "00k03SSA8vhlkHm"
          },
          "gold_key_raw_text": {
            "opportunity_line_item_id": "00k03SSA8vhlkHm"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "00k03SSA8vhlkHm",
          "gold_value": "006MeZ1b74lekzD"
        },
        {
          "key_normalized": {
            "opportunity_line_item_id": "00k05jhhlvdue5c"
          },
          "agent_key_raw_text": {
            "opportunity_line_item_id": "00k05JhhlVdue5C"
          },
          "gold_key_raw_text": {
            "opportunity_line_item_id": "00k05JhhlVdue5C"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "00k05JhhlVdue5C",
          "gold_value": "0069llsbEY7sna2"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 3000,
        "pred_unmatched_value_occurrences": 3000,
        "gold_unmatched_value_occurrences": 3000
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "product_2_id",
      "l0_counts_verbatim": {
        "column": "product_2_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 3000,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 3000,
        "pred_unmatched_value_occurrences": 3000,
        "gold_unmatched_value_occurrences": 3000,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "product_2_id",
        "one_to_one_mismatch_rows": 3000,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 3000,
        "pred_unmatched_value_occurrences": 3000,
        "gold_unmatched_value_occurrences": 3000,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "opportunity_line_item_id": "00k029dqfahx6ne"
          },
          "agent_key_raw_text": {
            "opportunity_line_item_id": "00k029DQfAHx6ne"
          },
          "gold_key_raw_text": {
            "opportunity_line_item_id": "00k029DQfAHx6ne"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "00k029DQfAHx6ne",
          "gold_value": "01tmdUhPdsLSok7"
        },
        {
          "key_normalized": {
            "opportunity_line_item_id": "00k031neiuy8t7u"
          },
          "agent_key_raw_text": {
            "opportunity_line_item_id": "00k031NEIUy8T7U"
          },
          "gold_key_raw_text": {
            "opportunity_line_item_id": "00k031NEIUy8T7U"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "00k031NEIUy8T7U",
          "gold_value": "01tIDWfK9qMB7tQ"
        },
        {
          "key_normalized": {
            "opportunity_line_item_id": "00k03mk8nktyeqn"
          },
          "agent_key_raw_text": {
            "opportunity_line_item_id": "00k03MK8NKTyEQn"
          },
          "gold_key_raw_text": {
            "opportunity_line_item_id": "00k03MK8NKTyEQn"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "00k03MK8NKTyEQn",
          "gold_value": "01tSH1dHUrvv9z3"
        },
        {
          "key_normalized": {
            "opportunity_line_item_id": "00k03ssa8vhlkhm"
          },
          "agent_key_raw_text": {
            "opportunity_line_item_id": "00k03SSA8vhlkHm"
          },
          "gold_key_raw_text": {
            "opportunity_line_item_id": "00k03SSA8vhlkHm"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "00k03SSA8vhlkHm",
          "gold_value": "01tFDe8FJHAR360"
        },
        {
          "key_normalized": {
            "opportunity_line_item_id": "00k05jhhlvdue5c"
          },
          "agent_key_raw_text": {
            "opportunity_line_item_id": "00k05JhhlVdue5C"
          },
          "gold_key_raw_text": {
            "opportunity_line_item_id": "00k05JhhlVdue5C"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "00k05JhhlVdue5C",
          "gold_value": "01t8r4JixeuQMtq"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 3000,
        "pred_unmatched_value_occurrences": 3000,
        "gold_unmatched_value_occurrences": 3000
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "created_date",
      "l0_counts_verbatim": {
        "column": "created_date",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "created_date",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "TIMESTAMP",
      "gold_actual_type": "TIMESTAMP"
    },
    {
      "column": "has_quantity_schedule",
      "l0_counts_verbatim": {
        "column": "has_quantity_schedule",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "has_quantity_schedule",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BOOLEAN",
      "gold_actual_type": "BOOLEAN"
    },
    {
      "column": "has_revenue_schedule",
      "l0_counts_verbatim": {
        "column": "has_revenue_schedule",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "has_revenue_schedule",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BOOLEAN",
      "gold_actual_type": "BOOLEAN"
    },
    {
      "column": "is_deleted",
      "l0_counts_verbatim": {
        "column": "is_deleted",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "is_deleted",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BOOLEAN",
      "gold_actual_type": "BOOLEAN"
    },
    {
      "column": "last_modified_date",
      "l0_counts_verbatim": {
        "column": "last_modified_date",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "last_modified_date",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "TIMESTAMP",
      "gold_actual_type": "TIMESTAMP"
    },
    {
      "column": "list_price",
      "l0_counts_verbatim": {
        "column": "list_price",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "list_price",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DECIMAL(18,3)",
      "gold_actual_type": "DECIMAL(18,3)"
    },
    {
      "column": "pricebook_entry_id",
      "l0_counts_verbatim": {
        "column": "pricebook_entry_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "pricebook_entry_id",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "quantity",
      "l0_counts_verbatim": {
        "column": "quantity",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "quantity",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DECIMAL(18,3)",
      "gold_actual_type": "DECIMAL(18,3)"
    },
    {
      "column": "service_date",
      "l0_counts_verbatim": {
        "column": "service_date",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "service_date",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DATE",
      "gold_actual_type": "DATE"
    },
    {
      "column": "sort_order",
      "l0_counts_verbatim": {
        "column": "sort_order",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "sort_order",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "INTEGER",
      "gold_actual_type": "INTEGER"
    },
    {
      "column": "total_price",
      "l0_counts_verbatim": {
        "column": "total_price",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "total_price",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DECIMAL(18,3)",
      "gold_actual_type": "DECIMAL(18,3)"
    },
    {
      "column": "unit_price",
      "l0_counts_verbatim": {
        "column": "unit_price",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "unit_price",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DECIMAL(18,3)",
      "gold_actual_type": "DECIMAL(18,3)"
    }
  ]
}
```

## agent_constraints_006

```json
{
  "source_record": "records/006_contract_impl-018.json",
  "declarations": {
    "grain": [],
    "primary_key": [],
    "not_null": [],
    "unique": []
  },
  "agent": {
    "table_exists": true,
    "actual_schema": "staging",
    "table_type": "BASE TABLE",
    "same_name_other_schemas": [],
    "row_count": 3000,
    "checks": {
      "grain": [],
      "primary_key": [],
      "not_null": [],
      "unique": []
    },
    "actual_table": "stg_salesforce__opportunity_line_item",
    "actual_columns": [
      "opportunity_line_item_id",
      "opportunity_id",
      "product_2_id",
      "created_date",
      "opportunity_line_item_description",
      "has_quantity_schedule",
      "has_revenue_schedule",
      "is_deleted",
      "last_modified_date",
      "list_price",
      "pricebook_entry_id",
      "quantity",
      "service_date",
      "sort_order",
      "total_price",
      "unit_price"
    ],
    "missing_declared_columns": [],
    "categories": {
      "grain": {
        "status": "not_declared",
        "violated": null,
        "declared_checks": 0,
        "checked_checks": 0,
        "unknown_checks": 0
      },
      "primary_key": {
        "status": "not_declared",
        "violated": null,
        "declared_checks": 0,
        "checked_checks": 0,
        "unknown_checks": 0
      },
      "not_null": {
        "status": "not_declared",
        "violated": null,
        "declared_checks": 0,
        "checked_checks": 0,
        "unknown_checks": 0
      },
      "unique": {
        "status": "not_declared",
        "violated": null,
        "declared_checks": 0,
        "checked_checks": 0,
        "unknown_checks": 0
      }
    },
    "any_constraint_violated": null
  }
}
```

## all_markers_and_evidence_008

```json
{
  "source_record": "records/008_table_scan.jsonl",
  "verbatim_record": {
    "task": "impl-018",
    "layer": "staging",
    "table": "stg_salesforce__opportunity_line_item",
    "logical_contract_table": "stg_salesforce__opportunity_line_item",
    "delivery_name_mapping_evidence": [],
    "inventory_sources": {
      "retained_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb",
      "present_in_database": true,
      "agent_final_sql_files": [
        "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql"
      ]
    },
    "status_007": {
      "gold_table_exists_in_original_gold": true,
      "whole_level_007": "仍不匹配",
      "007_present": true,
      "004_failed_set_member": true,
      "005_failed_set_member": false,
      "005_current_pred_execution": null,
      "status_sources": [
        {
          "record": "records/007_tolerance_tables.jsonl",
          "scope": "staging",
          "rule": "whole_match_level",
          "value": "仍不匹配",
          "007_prediction_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb"
        }
      ],
      "status": "待标注",
      "comparison_lookup_layer": "staging",
      "comparison_lookup_table": "stg_salesforce__opportunity_line_item",
      "actual_gold_relation_exists": true
    },
    "contract": {
      "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml",
      "blocks": [
        {
          "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml",
          "start_line": 747,
          "end_line": 785,
          "original_text": "    - name: stg_salesforce__opportunity_line_item\n      description: \"Cleaned opportunity line item records with validated product and pricing information\"\n      source_table: raw.opportunity_line_item\n      columns:\n        - name: opportunity_line_item_id\n          data_type: VARCHAR\n        - name: opportunity_id\n          data_type: VARCHAR\n        - name: product_2_id\n          data_type: VARCHAR\n        - name: created_date\n          data_type: TIMESTAMP\n        - name: opportunity_line_item_description\n          data_type: VARCHAR\n        - name: has_quantity_schedule\n          data_type: BOOLEAN\n        - name: has_revenue_schedule\n          data_type: BOOLEAN\n        - name: is_deleted\n          data_type: BOOLEAN\n          validation_rules:\n            - rule: \"NOT COALESCE(is_deleted, false)\"\n              on_failure: delete_row\n        - name: last_modified_date\n          data_type: TIMESTAMP\n        - name: list_price\n          data_type: DECIMAL\n        - name: pricebook_entry_id\n          data_type: VARCHAR\n        - name: quantity\n          data_type: DECIMAL\n        - name: service_date\n          data_type: DATE\n        - name: sort_order\n          data_type: INTEGER\n        - name: total_price\n          data_type: DECIMAL\n        - name: unit_price\n          data_type: DECIMAL\n",
          "yaml_path": [
            "staging_contract",
            "tables",
            9
          ]
        }
      ]
    },
    "output": {
      "status": "checked",
      "exists": true,
      "row_count": 3000,
      "zero_rows": false,
      "columns": [
        {
          "name": "opportunity_line_item_id",
          "type": "VARCHAR",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "opportunity_id",
          "type": "VARCHAR",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "product_2_id",
          "type": "VARCHAR",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "created_date",
          "type": "TIMESTAMP",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "opportunity_line_item_description",
          "type": "VARCHAR",
          "nonnull_rows": 1258,
          "sql_null_rows": 1742
        },
        {
          "name": "has_quantity_schedule",
          "type": "BOOLEAN",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "has_revenue_schedule",
          "type": "BOOLEAN",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "is_deleted",
          "type": "BOOLEAN",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "last_modified_date",
          "type": "TIMESTAMP",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "list_price",
          "type": "DECIMAL(18,3)",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "pricebook_entry_id",
          "type": "VARCHAR",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "quantity",
          "type": "DECIMAL(18,3)",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "service_date",
          "type": "DATE",
          "nonnull_rows": 886,
          "sql_null_rows": 2114
        },
        {
          "name": "sort_order",
          "type": "INTEGER",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "total_price",
          "type": "DECIMAL(18,3)",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        },
        {
          "name": "unit_price",
          "type": "DECIMAL(18,3)",
          "nonnull_rows": 3000,
          "sql_null_rows": 0
        }
      ],
      "all_null_columns": [],
      "constant_nonnull_columns": [
        {
          "column": "is_deleted",
          "type": "BOOLEAN",
          "value": "false",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 3000,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml",
                "start_line": 765,
                "end_line": 769,
                "original_text": "        - name: is_deleted\n          data_type: BOOLEAN\n          validation_rules:\n            - rule: \"NOT COALESCE(is_deleted, false)\"\n              on_failure: delete_row\n",
                "name": "is_deleted",
                "description": null,
                "specification": {
                  "name": "is_deleted",
                  "data_type": "BOOLEAN",
                  "validation_rules": [
                    {
                      "rule": "NOT COALESCE(is_deleted, false)",
                      "on_failure": "delete_row"
                    }
                  ]
                }
              }
            ],
            "meaning_description_status": "契约未描述含义"
          }
        }
      ],
      "equal_column_groups": [
        {
          "columns": [
            "opportunity_line_item_id",
            "opportunity_id",
            "product_2_id"
          ],
          "table_rows": 3000,
          "nonnull_equal_rows": 3000,
          "both_null_rows_ignored": 0,
          "mismatch_rows": 0,
          "column_contracts": {
            "opportunity_line_item_id": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml",
                  "start_line": 751,
                  "end_line": 752,
                  "original_text": "        - name: opportunity_line_item_id\n          data_type: VARCHAR\n",
                  "name": "opportunity_line_item_id",
                  "description": null,
                  "specification": {
                    "name": "opportunity_line_item_id",
                    "data_type": "VARCHAR"
                  }
                }
              ],
              "meaning_description_status": "契约未描述含义"
            },
            "opportunity_id": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml",
                  "start_line": 753,
                  "end_line": 754,
                  "original_text": "        - name: opportunity_id\n          data_type: VARCHAR\n",
                  "name": "opportunity_id",
                  "description": null,
                  "specification": {
                    "name": "opportunity_id",
                    "data_type": "VARCHAR"
                  }
                }
              ],
              "meaning_description_status": "契约未描述含义"
            },
            "product_2_id": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml",
                  "start_line": 755,
                  "end_line": 756,
                  "original_text": "        - name: product_2_id\n          data_type: VARCHAR\n",
                  "name": "product_2_id",
                  "description": null,
                  "specification": {
                    "name": "product_2_id",
                    "data_type": "VARCHAR"
                  }
                }
              ],
              "meaning_description_status": "契约未描述含义"
            }
          },
          "description_pairs": [
            {
              "left": "opportunity_line_item_id",
              "right": "opportunity_id",
              "both_have_explicit_descriptions": false,
              "description_texts_differ": false,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "opportunity_line_item_id",
              "right": "product_2_id",
              "both_have_explicit_descriptions": false,
              "description_texts_differ": false,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "opportunity_id",
              "right": "product_2_id",
              "both_have_explicit_descriptions": false,
              "description_texts_differ": false,
              "semantic_equivalence_evaluated": false
            }
          ],
          "has_pair_with_different_explicit_description": false,
          "meaning_status": "契约未描述含义差别"
        }
      ],
      "profile_sql": "SELECT count(*),count(\"opportunity_line_item_id\"),min(CAST(\"opportunity_line_item_id\" AS VARCHAR)),max(CAST(\"opportunity_line_item_id\" AS VARCHAR)),sum(hash(CAST(\"opportunity_line_item_id\" AS VARCHAR))),count(\"opportunity_id\"),min(CAST(\"opportunity_id\" AS VARCHAR)),max(CAST(\"opportunity_id\" AS VARCHAR)),sum(hash(CAST(\"opportunity_id\" AS VARCHAR))),count(\"product_2_id\"),min(CAST(\"product_2_id\" AS VARCHAR)),max(CAST(\"product_2_id\" AS VARCHAR)),sum(hash(CAST(\"product_2_id\" AS VARCHAR))),count(\"created_date\"),min(CAST(\"created_date\" AS VARCHAR)),max(CAST(\"created_date\" AS VARCHAR)),sum(hash(CAST(\"created_date\" AS VARCHAR))),count(\"opportunity_line_item_description\"),min(CAST(\"opportunity_line_item_description\" AS VARCHAR)),max(CAST(\"opportunity_line_item_description\" AS VARCHAR)),sum(hash(CAST(\"opportunity_line_item_description\" AS VARCHAR))),count(\"has_quantity_schedule\"),min(CAST(\"has_quantity_schedule\" AS VARCHAR)),max(CAST(\"has_quantity_schedule\" AS VARCHAR)),sum(hash(CAST(\"has_quantity_schedule\" AS VARCHAR))),count(\"has_revenue_schedule\"),min(CAST(\"has_revenue_schedule\" AS VARCHAR)),max(CAST(\"has_revenue_schedule\" AS VARCHAR)),sum(hash(CAST(\"has_revenue_schedule\" AS VARCHAR))),count(\"is_deleted\"),min(CAST(\"is_deleted\" AS VARCHAR)),max(CAST(\"is_deleted\" AS VARCHAR)),sum(hash(CAST(\"is_deleted\" AS VARCHAR))),count(\"last_modified_date\"),min(CAST(\"last_modified_date\" AS VARCHAR)),max(CAST(\"last_modified_date\" AS VARCHAR)),sum(hash(CAST(\"last_modified_date\" AS VARCHAR))),count(\"list_price\"),min(CAST(\"list_price\" AS VARCHAR)),max(CAST(\"list_price\" AS VARCHAR)),sum(hash(CAST(\"list_price\" AS VARCHAR))),count(\"pricebook_entry_id\"),min(CAST(\"pricebook_entry_id\" AS VARCHAR)),max(CAST(\"pricebook_entry_id\" AS VARCHAR)),sum(hash(CAST(\"pricebook_entry_id\" AS VARCHAR))),count(\"quantity\"),min(CAST(\"quantity\" AS VARCHAR)),max(CAST(\"quantity\" AS VARCHAR)),sum(hash(CAST(\"quantity\" AS VARCHAR))),count(\"service_date\"),min(CAST(\"service_date\" AS VARCHAR)),max(CAST(\"service_date\" AS VARCHAR)),sum(hash(CAST(\"service_date\" AS VARCHAR))),count(\"sort_order\"),min(CAST(\"sort_order\" AS VARCHAR)),max(CAST(\"sort_order\" AS VARCHAR)),sum(hash(CAST(\"sort_order\" AS VARCHAR))),count(\"total_price\"),min(CAST(\"total_price\" AS VARCHAR)),max(CAST(\"total_price\" AS VARCHAR)),sum(hash(CAST(\"total_price\" AS VARCHAR))),count(\"unit_price\"),min(CAST(\"unit_price\" AS VARCHAR)),max(CAST(\"unit_price\" AS VARCHAR)),sum(hash(CAST(\"unit_price\" AS VARCHAR))) FROM \"staging\".\"stg_salesforce__opportunity_line_item\"",
      "equal_column_confirmation_queries": [
        {
          "left": "opportunity_line_item_id",
          "right": "opportunity_id",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"opportunity_line_item_id\" AS VARCHAR) IS DISTINCT FROM CAST(\"opportunity_id\" AS VARCHAR)),count(*) FILTER(WHERE \"opportunity_line_item_id\" IS NOT NULL AND \"opportunity_id\" IS NOT NULL AND CAST(\"opportunity_line_item_id\" AS VARCHAR)=CAST(\"opportunity_id\" AS VARCHAR)) FROM \"staging\".\"stg_salesforce__opportunity_line_item\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 3000
        },
        {
          "left": "opportunity_line_item_id",
          "right": "product_2_id",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"opportunity_line_item_id\" AS VARCHAR) IS DISTINCT FROM CAST(\"product_2_id\" AS VARCHAR)),count(*) FILTER(WHERE \"opportunity_line_item_id\" IS NOT NULL AND \"product_2_id\" IS NOT NULL AND CAST(\"opportunity_line_item_id\" AS VARCHAR)=CAST(\"product_2_id\" AS VARCHAR)) FROM \"staging\".\"stg_salesforce__opportunity_line_item\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 3000
        }
      ],
      "equality_policy": "exact CAST AS VARCHAR per row; no trim/case/numeric/date normalization; both NULL ignored; at least one nonnull equal row; one-sided NULL differs",
      "actual_schema": "staging",
      "actual_table": "stg_salesforce__opportunity_line_item",
      "relation_type": "BASE TABLE"
    },
    "agent_sql": [
      {
        "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
        "status": "parsed",
        "parser": "30.25.0",
        "sources": [
          {
            "name": "raw.opportunity_line_item",
            "canonical": "raw.opportunity_line_item",
            "locations": [
              {
                "line": 18,
                "end_line": 18
              }
            ]
          }
        ],
        "unresolved_source_expressions": [],
        "row_generator_expressions": [],
        "outputs": [
          {
            "name": "opportunity_line_item_id",
            "alternatives": [
              {
                "expression_sql": "id",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 2,
                "end_line": 2,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "opportunity_line_item_id",
            "retained_output_ordinal": 1
          },
          {
            "name": "opportunity_id",
            "alternatives": [
              {
                "expression_sql": "id",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 3,
                "end_line": 3,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "opportunity_id",
            "retained_output_ordinal": 2
          },
          {
            "name": "product_2_id",
            "alternatives": [
              {
                "expression_sql": "id",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 4,
                "end_line": 4,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "product_2_id",
            "retained_output_ordinal": 3
          },
          {
            "name": "created_date",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(created_date AS TIMESTAMP)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 5,
                "end_line": 5,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "created_date",
            "retained_output_ordinal": 4
          },
          {
            "name": "opportunity_line_item_description",
            "alternatives": [
              {
                "expression_sql": "description",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 6,
                "end_line": 6,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "opportunity_line_item_description",
            "retained_output_ordinal": 5
          },
          {
            "name": "has_quantity_schedule",
            "alternatives": [
              {
                "expression_sql": "has_quantity_schedule",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 7,
                "end_line": 7,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "has_quantity_schedule",
            "retained_output_ordinal": 6
          },
          {
            "name": "has_revenue_schedule",
            "alternatives": [
              {
                "expression_sql": "has_revenue_schedule",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 8,
                "end_line": 8,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "has_revenue_schedule",
            "retained_output_ordinal": 7
          },
          {
            "name": "is_deleted",
            "alternatives": [
              {
                "expression_sql": "is_deleted",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 9,
                "end_line": 9,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "is_deleted",
            "retained_output_ordinal": 8
          },
          {
            "name": "last_modified_date",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(last_modified_date AS TIMESTAMP)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 10,
                "end_line": 10,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "last_modified_date",
            "retained_output_ordinal": 9
          },
          {
            "name": "list_price",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(list_price AS DECIMAL(18, 3))",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 2,
                "end_line": 11,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "list_price",
            "retained_output_ordinal": 10
          },
          {
            "name": "pricebook_entry_id",
            "alternatives": [
              {
                "expression_sql": "pricebook_entry_id",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 12,
                "end_line": 12,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "pricebook_entry_id",
            "retained_output_ordinal": 11
          },
          {
            "name": "quantity",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(quantity AS DECIMAL(18, 3))",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 2,
                "end_line": 13,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "quantity",
            "retained_output_ordinal": 12
          },
          {
            "name": "service_date",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(service_date AS DATE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 14,
                "end_line": 14,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "service_date",
            "retained_output_ordinal": 13
          },
          {
            "name": "sort_order",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(sort_order AS INT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 15,
                "end_line": 15,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "sort_order",
            "retained_output_ordinal": 14
          },
          {
            "name": "total_price",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(total_price AS DECIMAL(18, 3))",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 2,
                "end_line": 16,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "total_price",
            "retained_output_ordinal": 15
          },
          {
            "name": "unit_price",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(unit_price AS DECIMAL(18, 3))",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
                "line": 2,
                "end_line": 17,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "unit_price",
            "retained_output_ordinal": 16
          }
        ],
        "null_literal_outputs": [],
        "constant_literal_outputs": [],
        "runtime_hits": []
      }
    ],
    "source_comparison": {
      "contract": {
        "status": "specified",
        "references": [
          {
            "name": "raw.opportunity_line_item",
            "canonical": "raw.opportunity_line_item",
            "basis": "source_table",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml",
            "block_start_line": 747
          },
          {
            "name": "raw.opportunity_line_item",
            "canonical": "raw.opportunity_line_item",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml",
            "line": 749,
            "line_text": "      source_table: raw.opportunity_line_item"
          }
        ],
        "canonical_names": [
          "raw.opportunity_line_item"
        ]
      },
      "agent_direct_read_sources": [
        "raw.opportunity_line_item"
      ],
      "scope": "direct physical relation references through reachable local CTE/subqueries; no transitive expansion through other output tables or stored views",
      "complete": true,
      "specified_but_not_read": [],
      "read_but_not_specified": []
    },
    "time_dependencies": {
      "agent_sql": {
        "available": true,
        "appears": false,
        "hits": []
      },
      "gold_sql": {
        "available": true,
        "appears": false,
        "hits": [],
        "paths": [
          "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql"
        ]
      },
      "contract": {
        "available": true,
        "appears": false,
        "hits": []
      }
    },
    "any_result_keyword_excerpt_ids": [
      "008-009801",
      "008-009819"
    ],
    "trace_flags": {
      "A1_zero_rows": false,
      "A2_all_null_column": false,
      "A3_constant_nonnull_column": true,
      "A4_equal_columns": true,
      "A4_equal_columns_different_description_texts": false,
      "B5_null_literal_output": false,
      "B6_constant_literal_output": false,
      "B7_specified_not_read": false,
      "B7_read_not_specified": false,
      "B8_shared_single_source": false,
      "C9_agent_runtime_text": false,
      "C9_gold_runtime_text": false,
      "C9_contract_runtime_text": false,
      "D10_keyword_in_final_report": false,
      "D10_keyword_in_any_result_field": true
    }
  }
}
```

## trace_excerpts

```json
{
  "archive": "/home/katherine/Assumption_Ledger/traces/dacomp_deimpl_prev.tar.gz",
  "event_source_root": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent",
  "actual_read_sources_from_008_B7": [
    "raw.opportunity_line_item"
  ],
  "name_match_policy": "Case-insensitive complete identifier-name boundaries; source names include qualified form and bare leaf name. No semantic association inferred.",
  "matched_step_count": 12,
  "full_original_characters_before_budget": 111561,
  "budget_triggered": true,
  "source_only_steps_indexed": 2,
  "retained_full_original_characters": 70825,
  "full_target_steps_exceed_60000": true,
  "budget_policy": "If total command/output text exceeds 60000 characters, keep every target-table step complete and retain only id/location/first line for source-only steps. Do not rewrite or truncate a kept original step."
}
```

### event 7

```json
{
  "event_id": 7,
  "agent_command_sequence": 2,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/7.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1592,
    "decoded_characters": 60
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/7.json",
  "timestamp": "2026-10-25T04:02:54.696288",
  "target_table_name_hits": [
    "stg_salesforce__opportunity_line_item"
  ],
  "source_table_name_hits": [
    "raw.opportunity_line_item",
    "opportunity_line_item"
  ],
  "full_original_characters": 11992,
  "retention": "full_original"
}
```
```bash
cat config/layer_dependencies.yaml && sed -n '1,220p' run.py
```
```json
{
  "event_id": 8,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/8.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1277,
    "decoded_characters": 11932
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/8.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
layers:
  staging:
    description: "Normalized Raw Data Layer - cleans and normalizes raw data from Salesforce"
    dependencies: []
    tables:
      - stg_salesforce__account
      - stg_salesforce__contact
      - stg_salesforce__event
      - stg_salesforce__lead
      - stg_salesforce__opportunity
      - stg_salesforce__opportunity_line_item
      - stg_salesforce__order
      - stg_salesforce__product_2
      - stg_salesforce__task
      - stg_salesforce__user
      - stg_salesforce__user_role
      - stg_salesforce__account_history
      - stg_salesforce__contact_history
      - stg_salesforce__opportunity_history

  intermediate:
    description: "Middle layer - business logic and data aggregation processing"
    dependencies: ["staging"]
    tables:
      - int_salesforce__date_spine
      - int_salesforce__account_enhanced
      - int_salesforce__lead_conversion_funnel
      - int_salesforce__opportunity_pipeline
      - int_salesforce__activity_summary
      - int_salesforce__user_performance
      - int_salesforce__opportunity_aggregation_by_owner

  marts:
    description: "Data mart layer - analytics-ready business view"
    dependencies: ["staging", "intermediate"] 
    tables:
      - fct_salesforce__lead_performance
      - fct_salesforce__sales_pipeline
      - fct_salesforce__account_engagement
      - dim_salesforce__user
      - salesforce__revenue_analytics
      - salesforce__team_performance
      - salesforce__contact_enhanced
      - salesforce__daily_activity
      - salesforce__manager_performance
      - salesforce__opportunity_enhanced
      - salesforce__opportunity_line_item_enhanced
      - salesforce__owner_performance
      - salesforce__sales_snapshot
      - salesforce__account_daily_history
      - salesforce__contact_daily_history
      - salesforce__opportunity_daily_history

execution_order:
  staging:
    - stg_salesforce__account
    - stg_salesforce__contact
    - stg_salesforce__event
    - stg_salesforce__lead
    - stg_salesforce__opportunity
    - stg_salesforce__opportunity_line_item
    - stg_salesforce__order
    - stg_salesforce__product_2
    - stg_salesforce__task
    - stg_salesforce__user
    - stg_salesforce__user_role
    - stg_salesforce__account_history
    - stg_salesforce__contact_history
    - stg_salesforce__opportunity_history
  
  intermediate:
    - int_salesforce__date_spine
    - int_salesforce__account_enhanced
    - int_salesforce__lead_conversion_funnel
    - int_salesforce__opportunity_pipeline
    - int_salesforce__activity_summary
    - int_salesforce__user_performance
    - int_salesforce__opportunity_aggregation_by_owner
  
  marts:
    - fct_salesforce__lead_performance
    - fct_salesforce__sales_pipeline
    - fct_salesforce__account_engagement
    - dim_salesforce__user
    - salesforce__revenue_analytics
    - salesforce__team_performance
    - salesforce__contact_enhanced
    - salesforce__opportunity_enhanced
    - salesforce__opportunity_line_item_enhanced
    - salesforce__daily_activity
    - salesforce__owner_performance
    - salesforce__manager_performance
    - salesforce__sales_snapshot
    - salesforce__account_daily_history
    - salesforce__contact_daily_history
    - salesforce__opportunity_daily_history#!/usr/bin/env python3
import os
import yaml
import duckdb
from pathlib import Path
from typing import List, Optional
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SalesforceDataPipeline:
    """Salesforce Data Pipeline Orchestrator - Supports a layered Schema architecture"""
    
    def __init__(self, 
                 source_db_path: str = "salesforce_start.duckdb", 
                 target_db_path: str = "salesforce.duckdb",
                 config_path: str = "config/layer_dependencies.yaml"):
        self.source_db_path = source_db_path
        self.target_db_path = target_db_path
        self.config_path = config_path
        self.config = self._load_config()
        self.sql_dir = Path("sql")
        
                
        self.schema_config = {
            'raw': 'raw',                       
            'staging': 'staging',               
            'intermediate': 'intermediate',             
            'marts': 'marts'                     
        }
        
                
        self.conn = None
        
    def _load_config(self) -> dict:
        """Loads the configuration file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def _initialize_database(self):
        """Initializes the working database, creates the layered schema architecture, and imports raw data."""
        logger.info(f"📥 Creating new layered database: {self.target_db_path}")
        
                
        if not os.path.exists(self.source_db_path):
            raise FileNotFoundError(f"Source database file not found: {self.source_db_path}")
        
        self.conn = duckdb.connect(self.target_db_path)
        
                
        self._create_schemas()
        
                
        self._import_raw_data()
        
        logger.info(f"✓ Layered database initialization complete: {self.target_db_path}")
    
    def _create_schemas(self):
        """Creates the schemas for the data layers."""
        logger.info("🏗️ Creating Schema layered architecture")
        
        for layer, schema_name in self.schema_config.items():
            try:
                self.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                logger.info(f"  ✓ Created schema: {schema_name}")
            except Exception as e:
                logger.error(f"  ✗ Failed to create schema {schema_name}: {e}")
                raise
    
    def _import_raw_data(self):
        """Imports raw data from the source database to the raw schema."""
        logger.info("📥 Importing raw data to raw schema")
        
                
        try:
            source_conn = duckdb.connect(self.source_db_path)
        except Exception as e:
            logger.error(f"Could not connect to source database {self.source_db_path}: {e}")
            raise
        
        try:
            
            tables_result = source_conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'raw'").fetchall()
            source_tables = [table[0] for table in tables_result]
            
            logger.info(f"Found {len(source_tables)} raw tables")
            
                        
            for table_name in source_tables:
                try:
                    
                    data = source_conn.execute(f"SELECT * FROM raw.{table_name}").fetchall()
                    columns_info = source_conn.execute(f"DESCRIBE raw.{table_name}").fetchall()
                    
                                        
                    column_defs = []
                    for col_info in columns_info:
                        col_name, col_type = col_info[0], col_info[1]
                        
                        if col_name.lower() in ['end', 'start', 'order', 'group', 'select', 'from', 'where']:
                            safe_col_name = f'"{col_name}"'
                        else:
                            safe_col_name = col_name
                        column_defs.append(f"{safe_col_name} {col_type}")
                    
                    create_sql = f"CREATE OR REPLACE TABLE raw.{table_name} ({', '.join(column_defs)})"
                    self.conn.execute(create_sql)
                    
                                        
                    if data:
                        placeholders = ', '.join(['?' for _ in columns_info])
                        insert_sql = f"INSERT INTO raw.{table_name} VALUES ({placeholders})"
                        self.conn.executemany(insert_sql, data)
                    
                    logger.info(f"  ✓ raw.{table_name}: {len(data)} rows")
                    
                except Exception as e:
                    logger.error(f"  ✗ Failed to import table {table_name}: {e}")
        
        finally:
            source_conn.close()
        
        logger.info("✓ Raw data import complete")
    
    def _load_sql_file(self, file_path: Path) -> str:
        """Loads the content of a SQL file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"SQL file {file_path} not found")
            raise
    
    def _execute_sql(self, sql: str, table_name: str, layer_name: str) -> bool:
        """Executes SQL and creates a table in the specified schema."""
        try:
            
            target_schema = self.schema_config[layer_name]
            full_table_name = f"{target_schema}.{table_name}"
            
                        
            processed_sql = self._process_sql_references(sql, layer_name)
            
                        
            create_table_sql = f"CREATE OR REPLACE TABLE {full_table_name} AS ({processed_sql})"
            
            logger.info(f"Executing: {full_table_name}")
            self.conn.execute(create_table_sql)
            
                        
            count_result = self.conn.execute(f"SELECT COUNT(*) FROM {full_table_name}").fetchone()
            row_count = count_result[0] if count_result else 0
            
            logger.info(f"✓ {full_table_name}: {row_count:,} rows")
            return True
            
        except Exception as e:
            logger.error(f"✗ {full_table_name}: {e}")
            return False
    
    def _process_sql_references(self, sql: str, current_layer: str) -> str:
        """Processes table references in SQL, converting them to schema.table format."""
        import re
        processed_sql = sql
        
                
        cte_pattern = r'(\w+)\s+as\s*\('
        cte_names = set(re.findall(cte_pattern, sql, re.IGNORECASE))
        
                
        salesforce_table_mappings = {
        
            'account': 'raw.account',
            'contact': 'raw.contact',
            'opportunity': 'raw.opportunity',
            'lead': 'raw.lead',
            'user': 'raw.user',
            'user_role': 'raw.user_role',
            'event': 'raw.event',
            'task': 'raw.task',
            'opportunity_line_item': 'raw.opportunity_line_item',
            'order_data': 'raw.order_data',
            'product_2': 'raw.product_2',
            'account_history': 'raw.account_history',
            'contact_history': 'raw.contact_history',
            'opportunity_history': 'raw.opportunity_history'
        }
        
                
        for table_name, schema_table in salesforce_table_mappings.items():
            if table_name not in cte_names:
                pattern = r'\bfrom\s+' + re.escape(table_name) + r'\b'
                replacement = f'from {schema_table}'
                processed_sql = re.sub(pattern, replacement, processed_sql, flags=re.IGNORECASE)
        
        processed_sql = re.sub(r'\bfrom\s+staging\.', 'from staging.', processed_sql, flags=re.IGNORECASE)
        
                
        processed_sql = re.sub(r'\bfrom\s+intermediate\.', 'from intermediate.', processed_sql, flags=re.IGNORECASE)
        
                
        processed_sql = re.sub(r'\bfrom\s+marts\.', 'from marts.', processed_sql, flags=re.IGNORECASE)
        
        return processed_sql
    
    def _execute_layer(self, layer_name: str) -> bool:
        """Executes all tables for a specified layer."""
```

### event 13

```json
{
  "event_id": 13,
  "agent_command_sequence": 5,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/13.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1488,
    "decoded_characters": 122
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/13.json",
  "timestamp": "2026-10-25T04:03:04.850074",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "opportunity_line_item"
  ],
  "full_original_characters": 8994,
  "retention": "index_and_first_line_only",
  "first_line_original": "python - <<'PY'\n"
}
```
```json
{
  "event_id": 14,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/14.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1173,
    "decoded_characters": 8872
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/14.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 15

```json
{
  "event_id": 15,
  "agent_command_sequence": 6,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/15.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1720,
    "decoded_characters": 235
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/15.json",
  "timestamp": "2026-10-25T04:03:09.711439",
  "target_table_name_hits": [
    "stg_salesforce__opportunity_line_item"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 7021,
  "retention": "full_original"
}
```
```bash
python - <<'PY'
import yaml
x=yaml.safe_load(open('docs/data_contract.yaml'))
print([t['name'] for t in x['staging_contract']['tables']])
for t in x['staging_contract']['tables']:
 print(t['name'], [c['name'] for c in t['columns']])
PY
```
```json
{
  "event_id": 16,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/16.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1405,
    "decoded_characters": 6786
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/16.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
['stg_salesforce__account', 'stg_salesforce__contact', 'stg_salesforce__opportunity', 'stg_salesforce__user', 'stg_salesforce__lead', 'stg_salesforce__task', 'stg_salesforce__event', 'stg_salesforce__user_role', 'stg_salesforce__product_2', 'stg_salesforce__opportunity_line_item', 'stg_salesforce__order', 'stg_salesforce__account_history', 'stg_salesforce__contact_history', 'stg_salesforce__opportunity_history']
stg_salesforce__account ['account_id', 'account_number', 'account_name', 'account_description', 'account_source', 'industry', 'annual_revenue', 'number_of_employees', 'website', 'owner_id', 'type', 'billing_city', 'billing_country', 'billing_postal_code', 'billing_state', 'billing_state_code', 'billing_street', 'last_activity_date', 'last_referenced_date', 'last_viewed_date', 'master_record_id', 'ownership', 'parent_id', 'rating', 'record_type_id', 'shipping_city', 'shipping_country', 'shipping_country_code', 'shipping_postal_code', 'shipping_state', 'shipping_state_code', 'shipping_street', 'is_deleted']
stg_salesforce__contact ['account_id', 'assistant_name', 'assistant_phone', 'birthdate', 'created_date', 'department', 'contact_description', 'email', 'email_bounced_date', 'email_bounced_reason', 'fax', 'first_name', 'home_phone', 'contact_id', 'is_deleted', 'is_email_bounced', 'last_activity_date', 'last_curequest_date', 'last_cuupdate_date', 'last_modified_date', 'last_name', 'last_referenced_date', 'last_viewed_date', 'lead_source', 'mailing_city', 'mailing_country', 'mailing_country_code', 'mailing_postal_code', 'mailing_state', 'mailing_state_code', 'mailing_street', 'master_record_id', 'mobile_phone', 'contact_name', 'other_city', 'other_country', 'other_phone', 'other_postal_code', 'other_state', 'other_street', 'owner_id', 'phone', 'photo_url', 'reports_to_id', 'salutation', 'title']
stg_salesforce__opportunity ['account_id', 'amount', 'campaign_id', 'close_date', 'created_date', 'opportunity_description', 'expected_revenue', 'fiscal', 'fiscal_quarter', 'fiscal_year', 'forecast_category', 'forecast_category_name', 'has_open_activity', 'has_opportunity_line_item', 'has_overdue_task', 'opportunity_id', 'is_closed', 'is_deleted', 'is_won', 'last_activity_date', 'last_referenced_date', 'last_viewed_date', 'lead_source', 'opportunity_name', 'next_step', 'owner_id', 'probability', 'record_type_id', 'stage_name', 'synced_quote_id', 'type', 'is_created_this_month', 'is_created_this_quarter', 'days_since_created', 'days_to_close', 'is_closed_this_month', 'is_closed_this_quarter']
stg_salesforce__user ['account_id', 'alias', 'city', 'company_name', 'contact_id', 'country', 'country_code', 'department', 'email', 'first_name', 'user_id', 'individual_id', 'is_active', 'last_login_date', 'last_name', 'last_referenced_date', 'last_viewed_date', 'manager_id', 'user_name', 'postal_code', 'profile_id', 'state', 'state_code', 'street', 'title', 'user_role_id', 'user_type', 'username']
stg_salesforce__lead ['lead_id', 'first_name', 'last_name', 'lead_name', 'email', 'company', 'title', 'phone', 'lead_source', 'status', 'owner_id', 'is_deleted', 'lead_description', 'annual_revenue', 'city', 'converted_account_id', 'converted_contact_id', 'converted_date', 'converted_opportunity_id', 'country', 'country_code', 'created_by_id', 'created_date', 'email_bounced_date', 'email_bounced_reason', 'fax', 'geocode_accuracy', 'has_opted_out_of_email', 'industry', 'is_converted', 'is_unread_by_owner', 'last_activity_date', 'last_modified_date', 'last_referenced_date', 'last_viewed_date', 'latitude', 'longitude', 'master_record_id', 'mobile_phone', 'number_of_employees', 'photo_url', 'postal_code', 'salutation', 'state', 'state_code', 'street', 'system_modstamp', 'website']
stg_salesforce__task ['task_id', 'activity_date', 'call_disposition', 'call_duration_in_seconds', 'call_object', 'call_type', 'created_date', 'task_description', 'is_closed', 'is_deleted', 'is_high_priority', 'owner_id', 'priority', 'status', 'subject', 'type', 'what_id', 'who_id']
stg_salesforce__event ['event_id', 'activity_date', 'activity_date_time', 'is_deleted', 'event_description', 'duration_in_minutes', 'end_date_time', 'location', 'owner_id', 'start_date_time', 'subject', 'type', 'what_id', 'who_id']
stg_salesforce__user_role ['user_role_id', 'user_role_name', 'developer_name', 'parent_role_id', 'rollup_description']
stg_salesforce__product_2 ['product_2_id', 'created_date', 'product_description', 'external_data_source_id', 'external_id', 'family', 'is_active', 'is_archived', 'is_deleted', 'last_modified_date', 'product_name', 'product_code', 'quantity_unit_of_measure']
stg_salesforce__opportunity_line_item ['opportunity_line_item_id', 'opportunity_id', 'product_2_id', 'created_date', 'opportunity_line_item_description', 'has_quantity_schedule', 'has_revenue_schedule', 'is_deleted', 'last_modified_date', 'list_price', 'pricebook_entry_id', 'quantity', 'service_date', 'sort_order', 'total_price', 'unit_price']
stg_salesforce__order ['order_id', 'account_id', 'activated_by_id', 'activated_date', 'billing_city', 'billing_country', 'billing_postal_code', 'billing_state', 'billing_street', 'company_authorized_by_id', 'contract_id', 'created_date', 'customer_authorized_by_id', 'order_description', 'effective_date', 'end_date', 'is_deleted', 'last_modified_date', 'order_number', 'original_order_id', 'owner_id', 'status', 'total_amount', 'pricebook_2_id', 'shipping_city', 'shipping_country', 'shipping_postal_code', 'shipping_state', 'shipping_street', 'type']
stg_salesforce__account_history ['account_id', 'account_number', 'account_source', 'annual_revenue', 'billing_city', 'billing_country', 'billing_postal_code', 'billing_state', 'billing_street', 'created_date', 'account_description', 'industry', 'is_deleted', 'last_activity_date', 'account_name', 'number_of_employees', 'owner_id', 'ownership', 'parent_id', 'rating', 'shipping_city', 'shipping_country', 'shipping_postal_code', 'shipping_state', 'shipping_street', 'type', 'website', 'history_unique_key']
stg_salesforce__contact_history ['contact_id', 'account_id', 'created_date', 'contact_description', 'email', 'first_name', 'is_deleted', 'last_activity_date', 'last_modified_date', 'last_name', 'lead_source', 'mailing_city', 'mailing_country', 'mailing_postal_code', 'mailing_state', 'mailing_street', 'mobile_phone', 'contact_name', 'owner_id', 'phone', 'title', 'history_unique_key']
stg_salesforce__opportunity_history ['opportunity_id', 'account_id', 'amount', 'close_date', 'created_date', 'opportunity_description', 'expected_revenue', 'forecast_category', 'is_closed', 'is_deleted', 'is_won', 'last_activity_date', 'last_modified_date', 'lead_source', 'opportunity_name', 'next_step', 'owner_id', 'probability', 'stage_name', 'type', 'history_unique_key']
```

### event 17

```json
{
  "event_id": 17,
  "agent_command_sequence": 7,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/17.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1951,
    "decoded_characters": 342
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/17.json",
  "timestamp": "2026-10-25T04:03:17.890402",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "opportunity_line_item"
  ],
  "full_original_characters": 31742,
  "retention": "index_and_first_line_only",
  "first_line_original": "python - <<'PY'\n"
}
```
```json
{
  "event_id": 18,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/18.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1635,
    "decoded_characters": 31400
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/18.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 19

```json
{
  "event_id": 19,
  "agent_command_sequence": 8,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/19.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 12817,
    "decoded_characters": 5601
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/19.json",
  "timestamp": "2026-10-25T04:03:37.867128",
  "target_table_name_hits": [
    "stg_salesforce__opportunity_line_item"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 5601,
  "retention": "full_original"
}
```
```bash
mkdir -p sql/staging sql/intermediate sql/marts; cat > /tmp/build.py <<'PY'
import yaml, pathlib
contract=yaml.safe_load(open('docs/data_contract.yaml'))
source=yaml.safe_load(open('salesforce_start.yaml'))
base=pathlib.Path('sql/staging')
# source name overrides
mapping={'account_id':'id','account_name':'name','account_description':'description','contact_id':'id','contact_description':'description','contact_name':'name','opportunity_id':'id','opportunity_description':'description','opportunity_name':'name','user_id':'id','user_name':'name','lead_id':'id','lead_name':'name','lead_description':'description','task_id':'id','task_description':'description','event_id':'id','event_description':'description','user_role_id':'id','user_role_name':'name','product_2_id':'id','product_description':'description','product_name':'name','opportunity_line_item_id':'id','opportunity_line_item_description':'description','order_id':'id','order_description':'description','history_unique_key':None}
for tab in contract['staging_contract']['tables']:
 n=tab['name']; raw=tab['source_table'].split('.')[1]
 selects=[]
 for col in tab['columns']:
  name=col['name']; src=mapping.get(name,name)
  if name=='history_unique_key':
   # deterministic row identity from entity, source timestamp, and source values
   keyid={'stg_salesforce__account_history':'account_id','stg_salesforce__contact_history':'contact_id','stg_salesforce__opportunity_history':'opportunity_id'}.get(n,'id')
   expr=f"md5(concat_ws('|', coalesce(cast({keyid} as varchar), ''), coalesce(cast(_fivetran_start as varchar), ''), coalesce(cast(_fivetran_end as varchar), '')))"
  else:
   typ=col['data_type']
   expr=f'"{src}"' if src in ('type','order','start','end') else src
   if name in ('created_date',) and n.endswith('_history'): expr='_fivetran_start'
   if typ in ('DATE','TIMESTAMP','INTEGER','DECIMAL(15,2)','DECIMAL(18,2)','DECIMAL(18,3)','DECIMAL(5,2)','DECIMAL'):
    expr=f'try_cast({expr} as {typ})'
   if name in ('account_name',) and n=='stg_salesforce__account': expr='trim(cast(name as varchar))'
   if name=='email' and n in ('stg_salesforce__contact','stg_salesforce__user'): expr='lower(trim(email))'
   # validation nullification
   if name in ('email',) and n=='stg_salesforce__contact':
    expr="case when email is null or (length(lower(trim(email))) <= 255 and regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')) then lower(trim(email)) else null end"
   if name in ('annual_revenue','amount','probability'):
    if name=='annual_revenue' and n=='stg_salesforce__account': expr=f"case when {expr} >= 0 and {expr} <= 999999999999.99 then {expr} else null end"
    if name=='amount' and n=='stg_salesforce__opportunity': expr=f"case when {expr} >= 0 and {expr} <= 999999999999.99 then {expr} else null end"
    if name=='probability': expr=f"case when {expr} between 0 and 100 then {expr} else null end"
   if name in ('close_date','birthdate','start_date_time','end_date_time'):
    # leave casts; validate date ranges in guards below
    pass
  selects.append(f'    {expr} as {name}')
 filters=[]
 if n=='stg_salesforce__account': filters=['id is not null',"regexp_matches(id, '^[A-Za-z0-9]{15,18}$')",'name is not null',"trim(name) <> ''",'not coalesce(is_deleted, false)']
 if n=='stg_salesforce__contact': filters=['id is not null',"regexp_matches(id, '^[A-Za-z0-9]{15,18}$')",'not coalesce(is_deleted, false)']
 if n=='stg_salesforce__opportunity': filters=['id is not null',"regexp_matches(id, '^[A-Za-z0-9]{15,18}$')",'not coalesce(is_deleted, false)',"trim(name) <> ''",'length(trim(name)) <= 255']
 if n=='stg_salesforce__user': filters=['id is not null','email is not null',"regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')",'length(lower(trim(email))) <= 255','is_active is not null','last_name is not null','name is not null','username is not null']
 if n=='stg_salesforce__lead': filters=['id is not null','last_name is not null','name is not null','status in (\'Open - Not Contacted\', \'Working - Contacted\', \'Closed - Converted\', \'Closed - Not Converted\')']
 if n=='stg_salesforce__task': filters=['id is not null','is_closed is not null','owner_id is not null','status in (\'Not Started\', \'In Progress\', \'Completed\', \'Waiting on someone else\', \'Deferred\')']
 if n=='stg_salesforce__event': filters=['id is not null','owner_id is not null']
 if n=='stg_salesforce__user_role': filters=['id is not null','name is not null']
 if n=='stg_salesforce__product_2': filters=['id is not null','is_active is not null','name is not null']
 if n=='stg_salesforce__opportunity_line_item': filters=['id is not null']
 if n=='stg_salesforce__account_history': filters=['id is not null']
 if n=='stg_salesforce__contact_history': filters=['id is not null']
 if n=='stg_salesforce__opportunity_history': filters=['id is not null']
 # generic unique dedupe by designated keys
 unique=[c['name'] for c in tab['columns'] if 'unique' in c.get('constraints',[])]
 # source key aliases
 key={'account_id':'id','contact_id':'id','opportunity_id':'id','user_id':'id','lead_id':'id','task_id':'id','event_id':'id','user_role_id':'id','product_2_id':'id','opportunity_line_item_id':'id','history_unique_key':'id'}.get(unique[0]) if unique else None
 q='\n'.join(['select','  '+',\n  '.join(selects),f'from raw.{raw}']+(['where '+'\n  and '.join(filters)] if filters else []))
 if unique and key:
  q+=f'\nqualify row_number() over (partition by {key} order by {key}) = 1'
 (base/f'{n}.sql').write_text(q+'\n')
PY
python /tmp/build.py
```
```json
{
  "event_id": 20,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/20.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 12501,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/20.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text

```

### event 31

```json
{
  "event_id": 31,
  "agent_command_sequence": 14,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/31.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 15849,
    "decoded_characters": 7166
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/31.json",
  "timestamp": "2026-10-25T04:05:16.984956",
  "target_table_name_hits": [
    "stg_salesforce__opportunity_line_item"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 7166,
  "retention": "full_original"
}
```
```bash
cat > sql/marts/salesforce__opportunity_line_item_enhanced.sql <<'SQL'
with line_items as (
 select oli.*,opp.opportunity_name,opp.account_id,opp.owner_id as opportunity_owner_id,opp.stage_name,opp.close_date,opp.is_won,opp.is_closed,opp.forecast_category,
 p.product_name,p.product_code,p.family as product_family,a.account_name,a.industry as account_industry,u.user_name as opportunity_owner_name,u.email as opportunity_owner_email
 from staging.stg_salesforce__opportunity_line_item oli
 left join staging.stg_salesforce__opportunity opp on oli.opportunity_id=opp.opportunity_id
 left join staging.stg_salesforce__product_2 p on oli.product_2_id=p.product_2_id
 left join staging.stg_salesforce__account a on opp.account_id=a.account_id
 left join staging.stg_salesforce__user u on opp.owner_id=u.user_id
)
select opportunity_line_item_id,opportunity_id,product_2_id,created_date,opportunity_line_item_description,has_quantity_schedule,has_revenue_schedule,is_deleted,
 last_modified_date,list_price,pricebook_entry_id,quantity,service_date,sort_order,total_price,unit_price,opportunity_name,account_id,opportunity_owner_id,
 stage_name,close_date,is_won,is_closed,forecast_category,product_name,product_code,product_family,account_name,account_industry,opportunity_owner_name,opportunity_owner_email,
 case when is_won is true then 'Won' when is_won is false and is_closed is true then 'Lost'
 when is_closed is false and lower(forecast_category) in ('pipeline','forecast','bestcase') then 'Pipeline' else 'Other' end as opportunity_status
from line_items
SQL
cat > sql/marts/salesforce__daily_activity.sql <<'SQL'
with task_daily as (
 select activity_date::date as date_day,count(*) as tasks_completed from staging.stg_salesforce__task where activity_date is not null group by 1
),
event_daily as (
 select coalesce(activity_date::date,activity_date_time::date) as date_day,count(*) as events_completed
 from staging.stg_salesforce__event where coalesce(activity_date,activity_date_time) is not null group by 1
),
lead_created as (
 select created_date::date as date_day,count(*) as leads_created from staging.stg_salesforce__lead where created_date is not null group by 1
),
lead_converted as (
 select converted_date::date as date_day,count(*) as leads_converted from staging.stg_salesforce__lead
 where is_converted is true and converted_date is not null group by 1
),
opportunity_base as (
 select *,created_date::date as created_day,close_date::date as close_day,
 case when is_won is true then 'Won' when is_won is false and is_closed is true then 'Lost'
 when is_closed is false and lower(forecast_category) in ('pipeline','forecast','bestcase') then 'Pipeline' else 'Other' end as deal_status
 from staging.stg_salesforce__opportunity
),
opp_created as (
 select created_day as date_day,count(*) as opportunities_created,round(sum(amount)) as opportunities_created_amount
 from opportunity_base where created_day is not null group by 1
),
opp_closed as (
 select close_day as date_day,count(*) filter(where deal_status='Won') as opportunities_won,
 coalesce(round(sum(amount) filter(where deal_status='Won')),0) as opportunities_won_amount,
 count(*) filter(where deal_status='Lost') as opportunities_lost,
 round(sum(amount) filter(where deal_status='Lost')) as opportunities_lost_amount,
 round(sum(amount) filter(where deal_status='Pipeline')) as pipeline_amount
 from opportunity_base where close_day is not null group by 1
)
select d.date_day,lc.leads_created,lcv.leads_converted,t.tasks_completed,e.events_completed,oc.opportunities_created,oc.opportunities_created_amount,
 oh.opportunities_won,oh.opportunities_won_amount,oh.opportunities_lost,oh.opportunities_lost_amount,oh.pipeline_amount
from intermediate.int_salesforce__date_spine d left join lead_created lc using(date_day)
left join lead_converted lcv using(date_day) left join task_daily t using(date_day) left join event_daily e using(date_day)
left join opp_created oc using(date_day) left join opp_closed oh using(date_day)
SQL
cat > sql/marts/salesforce__sales_snapshot.sql <<'SQL'
with context as (
 select current_date as snapshot_date,date_trunc('month',current_date)::date as current_month_start,
 date_trunc('quarter',current_date)::date as current_quarter_start,date_trunc('year',current_date)::date as current_year_start
),
opportunity_metrics as (
 select count(*) as total_opportunities,count(*) filter(where is_won is true) as won_opportunities,
 count(*) filter(where is_closed is true and is_won is not true) as lost_opportunities,count(*) filter(where is_closed is false) as open_opportunities,
 sum(amount) as total_opportunity_value,sum(case when is_won is true then amount else 0 end) as won_amount,
 sum(case when is_closed is true and is_won is not true then amount else 0 end) as lost_amount,
 sum(case when is_closed is false then amount else 0 end) as pipeline_amount,
 avg(days_to_close) filter(where is_closed is true) as avg_days_to_close,avg(amount) filter(where is_won is true) as avg_won_deal_size,
 count(*) filter(where is_created_this_month is true) as opportunities_created_this_month,
 count(*) filter(where is_created_this_quarter is true) as opportunities_created_this_quarter,
 count(*) filter(where is_won is true and is_closed_this_month is true) as opportunities_won_this_month,
 count(*) filter(where is_won is true and is_closed_this_quarter is true) as opportunities_won_this_quarter,
 sum(case when is_created_this_month is true then amount else 0 end) as pipeline_created_this_month,
 sum(case when is_created_this_quarter is true then amount else 0 end) as pipeline_created_this_quarter,
 sum(case when is_won is true and is_closed_this_month is true then amount else 0 end) as revenue_this_month,
 sum(case when is_won is true and is_closed_this_quarter is true then amount else 0 end) as revenue_this_quarter
 from staging.stg_salesforce__opportunity where not coalesce(is_deleted,false)
),
lead_metrics as (
 select count(*) as total_leads,count(*) filter(where is_converted is true) as converted_leads,count(*) filter(where is_converted is false) as open_leads,
 case when count(*)>0 then round(count(*) filter(where is_converted is true)::double/count(*)*100,2) end as conversion_rate_pct
 from staging.stg_salesforce__lead where not coalesce(is_deleted,false)
),
account_metrics as (
 select count(*) as total_accounts,count(distinct owner_id) as unique_account_owners,count(distinct industry) as unique_industries,avg(number_of_employees) as avg_company_size
 from staging.stg_salesforce__account where not coalesce(is_deleted,false)
),
user_metrics as (
 select count(*) as total_users,count(*) filter(where is_active is true) as active_users from staging.stg_salesforce__user
)
select c.*,o.*,l.*,a.*,u.*,
 case when o.total_opportunities>0 then round(o.won_opportunities::double/o.total_opportunities*100,2) else 0.0 end as win_rate_pct,
 case when o.total_opportunities>0 then round((o.won_opportunities+o.lost_opportunities)::double/o.total_opportunities*100,2) else 0.0 end as close_rate_pct
from context c cross join opportunity_metrics o cross join lead_metrics l cross join account_metrics a cross join user_metrics u
SQL
```
```json
{
  "event_id": 32,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/32.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 15532,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/32.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text

```

### event 35

```json
{
  "event_id": 35,
  "agent_command_sequence": 16,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/35.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 3537,
    "decoded_characters": 1135
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/35.json",
  "timestamp": "2026-10-25T04:05:54.579741",
  "target_table_name_hits": [
    "stg_salesforce__opportunity_line_item"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 1982,
  "retention": "full_original"
}
```
```bash
python - <<'PY'
import yaml
src=yaml.safe_load(open('salesforce_start.yaml')); co=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']
mp={'account_id':'id','account_name':'name','account_description':'description','contact_id':'id','contact_description':'description','contact_name':'name','opportunity_id':'id','opportunity_description':'description','opportunity_name':'name','user_id':'id','user_name':'name','lead_id':'id','lead_name':'name','lead_description':'description','task_id':'id','task_description':'description','event_id':'id','event_description':'description','user_role_id':'id','user_role_name':'name','product_2_id':'id','product_description':'description','product_name':'name','opportunity_line_item_id':'id','opportunity_line_item_description':'description','order_id':'id','order_description':'description','history_unique_key':'id'}
for t in co:
 raw=t['source_table'].split('.')[1]; missing=[]
 for c in t['columns']:
  if c['name']=='history_unique_key':continue
  col=mp.get(c['name'],c['name'])
  if col not in src[raw]:missing.append((c['name'],col))
 print(t['name'],missing)
PY
```
```json
{
  "event_id": 36,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/36.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 3220,
    "decoded_characters": 847
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/36.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
stg_salesforce__account []
stg_salesforce__contact [('created_date', 'created_date')]
stg_salesforce__opportunity [('is_created_this_month', 'is_created_this_month'), ('is_created_this_quarter', 'is_created_this_quarter'), ('days_since_created', 'days_since_created'), ('days_to_close', 'days_to_close'), ('is_closed_this_month', 'is_closed_this_month'), ('is_closed_this_quarter', 'is_closed_this_quarter')]
stg_salesforce__user []
stg_salesforce__lead []
stg_salesforce__task []
stg_salesforce__event []
stg_salesforce__user_role []
stg_salesforce__product_2 []
stg_salesforce__opportunity_line_item []
stg_salesforce__order []
stg_salesforce__account_history [('created_date', 'created_date')]
stg_salesforce__contact_history [('created_date', 'created_date')]
stg_salesforce__opportunity_history [('last_modified_date', 'last_modified_date')]
```

### event 43

```json
{
  "event_id": 43,
  "agent_command_sequence": 20,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/43.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1386,
    "decoded_characters": 71
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/43.json",
  "timestamp": "2026-10-25T04:11:24.635871",
  "target_table_name_hits": [
    "stg_salesforce__opportunity_line_item"
  ],
  "source_table_name_hits": [
    "raw.opportunity_line_item",
    "opportunity_line_item"
  ],
  "full_original_characters": 15682,
  "retention": "full_original"
}
```
```bash
tail -180 /tmp/run2.log; grep -E '✗|ERROR|layer complete' /tmp/run2.log
```
```json
{
  "event_id": 44,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/44.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1068,
    "decoded_characters": 15611
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/44.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
2026-10-25 04:08:21,220 - INFO -   ✓ Created schema: intermediate
2026-10-25 04:08:21,224 - INFO -   ✓ Created schema: marts
2026-10-25 04:08:21,224 - INFO - 📥 Importing raw data to raw schema
2026-10-25 04:08:21,245 - INFO - Found 14 raw tables
2026-10-25 04:08:38,524 - INFO -   ✓ raw.account: 3000 rows
2026-10-25 04:08:54,727 - INFO -   ✓ raw.account_history: 3000 rows
2026-10-25 04:09:12,829 - INFO -   ✓ raw.contact: 3000 rows
2026-10-25 04:09:27,656 - INFO -   ✓ raw.contact_history: 3000 rows
2026-10-25 04:09:43,471 - INFO -   ✓ raw.event: 3000 rows
2026-10-25 04:09:59,732 - INFO -   ✓ raw.lead: 3000 rows
2026-10-25 04:10:13,395 - INFO -   ✓ raw.opportunity: 3000 rows
2026-10-25 04:10:27,052 - INFO -   ✓ raw.opportunity_history: 3000 rows
2026-10-25 04:10:39,846 - INFO -   ✓ raw.opportunity_line_item: 3000 rows
2026-10-25 04:10:56,377 - INFO -   ✓ raw.order_data: 3000 rows
2026-10-25 04:10:58,548 - INFO -   ✓ raw.product_2: 500 rows
2026-10-25 04:11:13,645 - INFO -   ✓ raw.task: 3000 rows
2026-10-25 04:11:19,722 - INFO -   ✓ raw.user: 1000 rows
2026-10-25 04:11:19,917 - INFO -   ✓ raw.user_role: 50 rows
2026-10-25 04:11:19,924 - INFO - ✓ Raw data import complete
2026-10-25 04:11:19,924 - INFO - ✓ Layered database initialization complete: salesforce.duckdb
2026-10-25 04:11:19,924 - INFO - 🧼 Cleaning previously generated schemas and tables...
2026-10-25 04:11:19,929 - INFO - ✓ Dropped schema: staging
2026-10-25 04:11:19,933 - INFO - ✓ Dropped schema: intermediate
2026-10-25 04:11:19,936 - INFO - ✓ Dropped schema: marts
2026-10-25 04:11:19,937 - INFO - Cleaning complete
2026-10-25 04:11:19,937 - INFO - 🏗️ Creating Schema layered architecture
2026-10-25 04:11:19,937 - INFO -   ✓ Created schema: raw
2026-10-25 04:11:19,940 - INFO -   ✓ Created schema: staging
2026-10-25 04:11:19,943 - INFO -   ✓ Created schema: intermediate
2026-10-25 04:11:19,946 - INFO -   ✓ Created schema: marts
2026-10-25 04:11:19,946 - INFO - 
=== Executing STAGING Layer ===
2026-10-25 04:11:19,946 - INFO - Description: Normalized Raw Data Layer - cleans and normalizes raw data from Salesforce
2026-10-25 04:11:19,947 - INFO - Executing: staging.stg_salesforce__account
2026-10-25 04:11:19,972 - INFO - ✓ staging.stg_salesforce__account: 2,999 rows
2026-10-25 04:11:19,973 - INFO - Executing: staging.stg_salesforce__contact
2026-10-25 04:11:20,000 - INFO - ✓ staging.stg_salesforce__contact: 3,000 rows
2026-10-25 04:11:20,001 - INFO - Executing: staging.stg_salesforce__event
2026-10-25 04:11:20,016 - INFO - ✓ staging.stg_salesforce__event: 3,000 rows
2026-10-25 04:11:20,017 - INFO - Executing: staging.stg_salesforce__lead
2026-10-25 04:11:20,053 - INFO - ✓ staging.stg_salesforce__lead: 2,994 rows
2026-10-25 04:11:20,054 - INFO - Executing: staging.stg_salesforce__opportunity
2026-10-25 04:11:20,061 - ERROR - ✗ staging.stg_salesforce__opportunity: Binder Error: Column "days_since_created" referenced that exists in the SELECT clause - but this column cannot be referenced before it is defined
2026-10-25 04:11:20,062 - INFO - Executing: staging.stg_salesforce__opportunity_line_item
2026-10-25 04:11:20,072 - INFO - ✓ staging.stg_salesforce__opportunity_line_item: 3,000 rows
2026-10-25 04:11:20,073 - INFO - Executing: staging.stg_salesforce__order
2026-10-25 04:11:20,584 - INFO - ✓ staging.stg_salesforce__order: 3,000 rows
2026-10-25 04:11:20,584 - INFO - Executing: staging.stg_salesforce__product_2
2026-10-25 04:11:20,593 - INFO - ✓ staging.stg_salesforce__product_2: 500 rows
2026-10-25 04:11:20,594 - INFO - Executing: staging.stg_salesforce__task
2026-10-25 04:11:20,615 - INFO - ✓ staging.stg_salesforce__task: 2,998 rows
2026-10-25 04:11:20,616 - INFO - Executing: staging.stg_salesforce__user
2026-10-25 04:11:20,630 - INFO - ✓ staging.stg_salesforce__user: 993 rows
2026-10-25 04:11:20,631 - INFO - Executing: staging.stg_salesforce__user_role
2026-10-25 04:11:20,638 - INFO - ✓ staging.stg_salesforce__user_role: 50 rows
2026-10-25 04:11:20,639 - INFO - Executing: staging.stg_salesforce__account_history
2026-10-25 04:11:20,657 - INFO - ✓ staging.stg_salesforce__account_history: 2,018 rows
2026-10-25 04:11:20,658 - INFO - Executing: staging.stg_salesforce__contact_history
2026-10-25 04:11:20,677 - INFO - ✓ staging.stg_salesforce__contact_history: 2,434 rows
2026-10-25 04:11:20,678 - INFO - Executing: staging.stg_salesforce__opportunity_history
2026-10-25 04:11:20,678 - ERROR - ✗ staging.stg_salesforce__opportunity_history: Binder Error: Column "last_modified_date" referenced that exists in the SELECT clause - but this column cannot be referenced before it is defined
2026-10-25 04:11:20,678 - INFO - STAGING layer complete: 12/14 tables created successfully
2026-10-25 04:11:20,678 - INFO - 
=== Executing INTERMEDIATE Layer ===
2026-10-25 04:11:20,678 - INFO - Description: Middle layer - business logic and data aggregation processing
2026-10-25 04:11:20,679 - INFO - Executing: intermediate.int_salesforce__date_spine
2026-10-25 04:11:20,680 - ERROR - ✗ intermediate.int_salesforce__date_spine: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
Did you mean "stg_salesforce__opportunity_line_item"?

LINE 3:     from staging.stg_salesforce__opportunity
                 ^
2026-10-25 04:11:20,681 - INFO - Executing: intermediate.int_salesforce__account_enhanced
2026-10-25 04:11:20,697 - INFO - ✓ intermediate.int_salesforce__account_enhanced: 2,999 rows
2026-10-25 04:11:20,698 - INFO - Executing: intermediate.int_salesforce__lead_conversion_funnel
2026-10-25 04:11:20,727 - INFO - ✓ intermediate.int_salesforce__lead_conversion_funnel: 2,994 rows
2026-10-25 04:11:20,728 - INFO - Executing: intermediate.int_salesforce__opportunity_pipeline
2026-10-25 04:11:20,729 - ERROR - ✗ intermediate.int_salesforce__opportunity_pipeline: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
Did you mean "stg_salesforce__opportunity_line_item"?

LINE 2:     select * from staging.stg_salesforce__opportunity where not coalesce(is_d...
                          ^
2026-10-25 04:11:20,730 - INFO - Executing: intermediate.int_salesforce__activity_summary
2026-10-25 04:11:20,744 - INFO - ✓ intermediate.int_salesforce__activity_summary: 2,999 rows
2026-10-25 04:11:20,745 - INFO - Executing: intermediate.int_salesforce__user_performance
2026-10-25 04:11:20,746 - ERROR - ✗ intermediate.int_salesforce__user_performance: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
Did you mean "stg_salesforce__opportunity_line_item"?

LINE 11:     from staging.stg_salesforce__opportunity where not coalesce(is_d...
                  ^
2026-10-25 04:11:20,747 - INFO - Executing: intermediate.int_salesforce__opportunity_aggregation_by_owner
2026-10-25 04:11:20,748 - ERROR - ✗ intermediate.int_salesforce__opportunity_aggregation_by_owner: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
Did you mean "stg_salesforce__opportunity_line_item"?

LINE 14:     from staging.stg_salesforce__opportunity o
                  ^
2026-10-25 04:11:20,748 - INFO - INTERMEDIATE layer complete: 3/7 tables created successfully
2026-10-25 04:11:20,748 - INFO - 
=== Executing MARTS Layer ===
2026-10-25 04:11:20,748 - INFO - Description: Data mart layer - analytics-ready business view
2026-10-25 04:11:20,749 - INFO - Executing: marts.fct_salesforce__lead_performance
2026-10-25 04:11:20,769 - INFO - ✓ marts.fct_salesforce__lead_performance: 2,994 rows
2026-10-25 04:11:20,770 - INFO - Executing: marts.fct_salesforce__sales_pipeline
2026-10-25 04:11:20,771 - ERROR - ✗ marts.fct_salesforce__sales_pipeline: Catalog Error: Table with name int_salesforce__opportunity_pipeline does not exist!
Did you mean "int_salesforce__account_enhanced"?

LINE 8:  from intermediate.int_salesforce__opportunity_pipeline op
              ^
2026-10-25 04:11:20,772 - INFO - Executing: marts.fct_salesforce__account_engagement
2026-10-25 04:11:20,796 - INFO - ✓ marts.fct_salesforce__account_engagement: 2,999 rows
2026-10-25 04:11:20,797 - INFO - Executing: marts.dim_salesforce__user
2026-10-25 04:11:20,798 - ERROR - ✗ marts.dim_salesforce__user: Catalog Error: Table with name int_salesforce__user_performance does not exist!
Did you mean "int_salesforce__lead_conversion_funnel"?

LINE 7:  left join intermediate.int_salesforce__user_performance up on u.user_id...
                   ^
2026-10-25 04:11:20,799 - INFO - Executing: marts.salesforce__revenue_analytics
2026-10-25 04:11:20,800 - ERROR - ✗ marts.salesforce__revenue_analytics: Catalog Error: Table with name int_salesforce__opportunity_pipeline does not exist!
Did you mean "int_salesforce__account_enhanced"?

LINE 2:  select * from intermediate.int_salesforce__opportunity_pipeline where...
                       ^
2026-10-25 04:11:20,802 - INFO - Executing: marts.salesforce__team_performance
2026-10-25 04:11:20,803 - ERROR - ✗ marts.salesforce__team_performance: Catalog Error: Table with name dim_salesforce__user does not exist!
Did you mean "fct_salesforce__lead_performance"?

LINE 14:  from marts.dim_salesforce__user d
               ^
2026-10-25 04:11:20,803 - INFO - Executing: marts.salesforce__contact_enhanced
2026-10-25 04:11:20,832 - INFO - ✓ marts.salesforce__contact_enhanced: 3,000 rows
2026-10-25 04:11:20,834 - INFO - Executing: marts.salesforce__opportunity_enhanced
2026-10-25 04:11:20,834 - ERROR - ✗ marts.salesforce__opportunity_enhanced: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
Did you mean "stg_salesforce__opportunity_line_item"?

LINE 8:  from staging.stg_salesforce__opportunity o
              ^
2026-10-25 04:11:20,835 - INFO - Executing: marts.salesforce__opportunity_line_item_enhanced
2026-10-25 04:11:20,835 - ERROR - ✗ marts.salesforce__opportunity_line_item_enhanced: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
Did you mean "stg_salesforce__opportunity_line_item"?

LINE 5:  left join staging.stg_salesforce__opportunity opp on oli.opportunity_id...
                   ^
2026-10-25 04:11:20,836 - INFO - Executing: marts.salesforce__daily_activity
2026-10-25 04:11:20,837 - ERROR - ✗ marts.salesforce__daily_activity: Catalog Error: Table with name int_salesforce__date_spine does not exist!
Did you mean "int_salesforce__account_enhanced"?

LINE 35: from intermediate.int_salesforce__date_spine d left join lead_cr...
              ^
2026-10-25 04:11:20,837 - INFO - Executing: marts.salesforce__owner_performance
2026-10-25 04:11:20,838 - ERROR - ✗ marts.salesforce__owner_performance: Catalog Error: Table with name int_salesforce__opportunity_aggregation_by_owner does not exist!
Did you mean "int_salesforce__activity_summary"?

LINE 7: from intermediate.int_salesforce__opportunity_aggregation_by_own...
             ^
2026-10-25 04:11:20,838 - INFO - Executing: marts.salesforce__manager_performance
2026-10-25 04:11:20,839 - ERROR - ✗ marts.salesforce__manager_performance: Catalog Error: Table with name salesforce__owner_performance does not exist!
Did you mean "salesforce__contact_enhanced"?

LINE 13:  from marts.salesforce__owner_performance where manager_id is...
               ^
2026-10-25 04:11:20,840 - INFO - Executing: marts.salesforce__sales_snapshot
2026-10-25 04:11:20,841 - ERROR - ✗ marts.salesforce__sales_snapshot: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
Did you mean "stg_salesforce__opportunity_line_item"?

LINE 20:  from staging.stg_salesforce__opportunity where not coalesce(is_d...
               ^
2026-10-25 04:11:20,841 - INFO - Executing: marts.salesforce__account_daily_history
2026-10-25 04:11:20,857 - INFO - ✓ marts.salesforce__account_daily_history: 2,018 rows
2026-10-25 04:11:20,858 - INFO - Executing: marts.salesforce__contact_daily_history
2026-10-25 04:11:20,876 - INFO - ✓ marts.salesforce__contact_daily_history: 2,434 rows
2026-10-25 04:11:20,876 - INFO - Executing: marts.salesforce__opportunity_daily_history
2026-10-25 04:11:20,877 - ERROR - ✗ marts.salesforce__opportunity_daily_history: Catalog Error: Table with name stg_salesforce__opportunity_history does not exist!
Did you mean "stg_salesforce__opportunity_line_item"?

LINE 6:  from staging.stg_salesforce__opportunity_history where is_deleted...
              ^
2026-10-25 04:11:20,877 - INFO - MARTS layer complete: 5/16 tables created successfully
2026-10-25 04:11:20,877 - ERROR - 
❌ Errors occurred during data pipeline execution

❌ Errors occurred during data transformation, please check the logs
2026-10-25 04:11:20,061 - ERROR - ✗ staging.stg_salesforce__opportunity: Binder Error: Column "days_since_created" referenced that exists in the SELECT clause - but this column cannot be referenced before it is defined
2026-10-25 04:11:20,678 - ERROR - ✗ staging.stg_salesforce__opportunity_history: Binder Error: Column "last_modified_date" referenced that exists in the SELECT clause - but this column cannot be referenced before it is defined
2026-10-25 04:11:20,678 - INFO - STAGING layer complete: 12/14 tables created successfully
2026-10-25 04:11:20,680 - ERROR - ✗ intermediate.int_salesforce__date_spine: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
2026-10-25 04:11:20,729 - ERROR - ✗ intermediate.int_salesforce__opportunity_pipeline: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
2026-10-25 04:11:20,746 - ERROR - ✗ intermediate.int_salesforce__user_performance: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
2026-10-25 04:11:20,748 - ERROR - ✗ intermediate.int_salesforce__opportunity_aggregation_by_owner: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
2026-10-25 04:11:20,748 - INFO - INTERMEDIATE layer complete: 3/7 tables created successfully
2026-10-25 04:11:20,771 - ERROR - ✗ marts.fct_salesforce__sales_pipeline: Catalog Error: Table with name int_salesforce__opportunity_pipeline does not exist!
2026-10-25 04:11:20,798 - ERROR - ✗ marts.dim_salesforce__user: Catalog Error: Table with name int_salesforce__user_performance does not exist!
2026-10-25 04:11:20,800 - ERROR - ✗ marts.salesforce__revenue_analytics: Catalog Error: Table with name int_salesforce__opportunity_pipeline does not exist!
2026-10-25 04:11:20,803 - ERROR - ✗ marts.salesforce__team_performance: Catalog Error: Table with name dim_salesforce__user does not exist!
2026-10-25 04:11:20,834 - ERROR - ✗ marts.salesforce__opportunity_enhanced: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
2026-10-25 04:11:20,835 - ERROR - ✗ marts.salesforce__opportunity_line_item_enhanced: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
2026-10-25 04:11:20,837 - ERROR - ✗ marts.salesforce__daily_activity: Catalog Error: Table with name int_salesforce__date_spine does not exist!
2026-10-25 04:11:20,838 - ERROR - ✗ marts.salesforce__owner_performance: Catalog Error: Table with name int_salesforce__opportunity_aggregation_by_owner does not exist!
2026-10-25 04:11:20,839 - ERROR - ✗ marts.salesforce__manager_performance: Catalog Error: Table with name salesforce__owner_performance does not exist!
2026-10-25 04:11:20,841 - ERROR - ✗ marts.salesforce__sales_snapshot: Catalog Error: Table with name stg_salesforce__opportunity does not exist!
2026-10-25 04:11:20,877 - ERROR - ✗ marts.salesforce__opportunity_daily_history: Catalog Error: Table with name stg_salesforce__opportunity_history does not exist!
2026-10-25 04:11:20,877 - INFO - MARTS layer complete: 5/16 tables created successfully
2026-10-25 04:11:20,877 - ERROR - 
```

### event 49

```json
{
  "event_id": 49,
  "agent_command_sequence": 23,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/49.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2476,
    "decoded_characters": 606
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/49.json",
  "timestamp": "2026-10-25T04:11:42.886265",
  "target_table_name_hits": [
    "stg_salesforce__opportunity_line_item"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 15479,
  "retention": "full_original"
}
```
```bash
for f in sql/staging/*.sql; do echo ==== $f; grep -E 'md5|history_unique_key|created_date as|last_modified_date' $f; done; python - <<'PY'
import duckdb
c=duckdb.connect('salesforce.duckdb',read_only=True)
for schema in ['staging','intermediate','marts']:
 print(schema,c.execute(f"select table_name from information_schema.tables where table_schema='{schema}' order by 1").fetchall())
for t in ['stg_salesforce__account','stg_salesforce__contact','stg_salesforce__opportunity','stg_salesforce__user','stg_salesforce__lead','stg_salesforce__event']:
 print(t,c.execute('describe staging.'+t).fetchall())
PY
```
```json
{
  "event_id": 50,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/50.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2158,
    "decoded_characters": 14873
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/50.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
==== sql/staging/stg_salesforce__account.sql
==== sql/staging/stg_salesforce__account_history.sql
      md5(concat_ws('|', coalesce(cast(account_id as varchar), ''), coalesce(cast(_fivetran_start as varchar), ''), coalesce(cast(_fivetran_end as varchar), ''))) as history_unique_key
==== sql/staging/stg_salesforce__contact.sql
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
==== sql/staging/stg_salesforce__contact_history.sql
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
      md5(concat_ws('|', coalesce(cast(contact_id as varchar), ''), coalesce(cast(_fivetran_start as varchar), ''), coalesce(cast(_fivetran_end as varchar), ''))) as history_unique_key
==== sql/staging/stg_salesforce__event.sql
==== sql/staging/stg_salesforce__lead.sql
      try_cast(created_date as TIMESTAMP) as created_date,
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
==== sql/staging/stg_salesforce__opportunity.sql
      try_cast(created_date as TIMESTAMP) as created_date,
==== sql/staging/stg_salesforce__opportunity_history.sql
      cast(null as TIMESTAMP) as last_modified_date,
      md5(concat_ws('|', coalesce(cast(id as varchar), ''), coalesce(cast(_fivetran_start as varchar), ''), coalesce(cast(_fivetran_end as varchar), ''))) as history_unique_key
==== sql/staging/stg_salesforce__opportunity_line_item.sql
      try_cast(created_date as TIMESTAMP) as created_date,
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
==== sql/staging/stg_salesforce__order.sql
      try_cast(created_date as TIMESTAMP) as created_date,
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
==== sql/staging/stg_salesforce__product_2.sql
      try_cast(created_date as TIMESTAMP) as created_date,
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
==== sql/staging/stg_salesforce__task.sql
      try_cast(created_date as TIMESTAMP) as created_date,
==== sql/staging/stg_salesforce__user.sql
==== sql/staging/stg_salesforce__user_role.sql
staging [('stg_salesforce__account',), ('stg_salesforce__account_history',), ('stg_salesforce__contact',), ('stg_salesforce__contact_history',), ('stg_salesforce__event',), ('stg_salesforce__lead',), ('stg_salesforce__opportunity',), ('stg_salesforce__opportunity_history',), ('stg_salesforce__opportunity_line_item',), ('stg_salesforce__order',), ('stg_salesforce__product_2',), ('stg_salesforce__task',), ('stg_salesforce__user',), ('stg_salesforce__user_role',)]
intermediate [('int_salesforce__account_enhanced',), ('int_salesforce__activity_summary',), ('int_salesforce__date_spine',), ('int_salesforce__lead_conversion_funnel',), ('int_salesforce__opportunity_aggregation_by_owner',), ('int_salesforce__opportunity_pipeline',), ('int_salesforce__user_performance',)]
marts [('dim_salesforce__user',), ('fct_salesforce__account_engagement',), ('fct_salesforce__lead_performance',), ('fct_salesforce__sales_pipeline',), ('salesforce__account_daily_history',), ('salesforce__contact_daily_history',), ('salesforce__contact_enhanced',), ('salesforce__daily_activity',), ('salesforce__manager_performance',), ('salesforce__opportunity_daily_history',), ('salesforce__opportunity_enhanced',), ('salesforce__opportunity_line_item_enhanced',), ('salesforce__owner_performance',), ('salesforce__revenue_analytics',), ('salesforce__sales_snapshot',), ('salesforce__team_performance',)]
stg_salesforce__account [('account_id', 'VARCHAR', 'YES', None, None, None), ('account_number', 'VARCHAR', 'YES', None, None, None), ('account_name', 'VARCHAR', 'YES', None, None, None), ('account_description', 'VARCHAR', 'YES', None, None, None), ('account_source', 'VARCHAR', 'YES', None, None, None), ('industry', 'VARCHAR', 'YES', None, None, None), ('annual_revenue', 'DECIMAL(15,2)', 'YES', None, None, None), ('number_of_employees', 'INTEGER', 'YES', None, None, None), ('website', 'VARCHAR', 'YES', None, None, None), ('owner_id', 'VARCHAR', 'YES', None, None, None), ('type', 'VARCHAR', 'YES', None, None, None), ('billing_city', 'VARCHAR', 'YES', None, None, None), ('billing_country', 'VARCHAR', 'YES', None, None, None), ('billing_postal_code', 'VARCHAR', 'YES', None, None, None), ('billing_state', 'VARCHAR', 'YES', None, None, None), ('billing_state_code', 'VARCHAR', 'YES', None, None, None), ('billing_street', 'VARCHAR', 'YES', None, None, None), ('last_activity_date', 'DATE', 'YES', None, None, None), ('last_referenced_date', 'TIMESTAMP', 'YES', None, None, None), ('last_viewed_date', 'TIMESTAMP', 'YES', None, None, None), ('master_record_id', 'VARCHAR', 'YES', None, None, None), ('ownership', 'VARCHAR', 'YES', None, None, None), ('parent_id', 'VARCHAR', 'YES', None, None, None), ('rating', 'VARCHAR', 'YES', None, None, None), ('record_type_id', 'VARCHAR', 'YES', None, None, None), ('shipping_city', 'VARCHAR', 'YES', None, None, None), ('shipping_country', 'VARCHAR', 'YES', None, None, None), ('shipping_country_code', 'VARCHAR', 'YES', None, None, None), ('shipping_postal_code', 'VARCHAR', 'YES', None, None, None), ('shipping_state', 'VARCHAR', 'YES', None, None, None), ('shipping_state_code', 'VARCHAR', 'YES', None, None, None), ('shipping_street', 'VARCHAR', 'YES', None, None, None), ('is_deleted', 'BOOLEAN', 'YES', None, None, None)]
stg_salesforce__contact [('account_id', 'VARCHAR', 'YES', None, None, None), ('assistant_name', 'VARCHAR', 'YES', None, None, None), ('assistant_phone', 'VARCHAR', 'YES', None, None, None), ('birthdate', 'DATE', 'YES', None, None, None), ('created_date', 'TIMESTAMP', 'YES', None, None, None), ('department', 'VARCHAR', 'YES', None, None, None), ('contact_description', 'VARCHAR', 'YES', None, None, None), ('email', 'VARCHAR', 'YES', None, None, None), ('email_bounced_date', 'TIMESTAMP', 'YES', None, None, None), ('email_bounced_reason', 'VARCHAR', 'YES', None, None, None), ('fax', 'VARCHAR', 'YES', None, None, None), ('first_name', 'VARCHAR', 'YES', None, None, None), ('home_phone', 'VARCHAR', 'YES', None, None, None), ('contact_id', 'VARCHAR', 'YES', None, None, None), ('is_deleted', 'BOOLEAN', 'YES', None, None, None), ('is_email_bounced', 'BOOLEAN', 'YES', None, None, None), ('last_activity_date', 'DATE', 'YES', None, None, None), ('last_curequest_date', 'TIMESTAMP', 'YES', None, None, None), ('last_cuupdate_date', 'TIMESTAMP', 'YES', None, None, None), ('last_modified_date', 'TIMESTAMP', 'YES', None, None, None), ('last_name', 'VARCHAR', 'YES', None, None, None), ('last_referenced_date', 'TIMESTAMP', 'YES', None, None, None), ('last_viewed_date', 'TIMESTAMP', 'YES', None, None, None), ('lead_source', 'VARCHAR', 'YES', None, None, None), ('mailing_city', 'VARCHAR', 'YES', None, None, None), ('mailing_country', 'VARCHAR', 'YES', None, None, None), ('mailing_country_code', 'VARCHAR', 'YES', None, None, None), ('mailing_postal_code', 'VARCHAR', 'YES', None, None, None), ('mailing_state', 'VARCHAR', 'YES', None, None, None), ('mailing_state_code', 'VARCHAR', 'YES', None, None, None), ('mailing_street', 'VARCHAR', 'YES', None, None, None), ('master_record_id', 'VARCHAR', 'YES', None, None, None), ('mobile_phone', 'VARCHAR', 'YES', None, None, None), ('contact_name', 'VARCHAR', 'YES', None, None, None), ('other_city', 'VARCHAR', 'YES', None, None, None), ('other_country', 'VARCHAR', 'YES', None, None, None), ('other_phone', 'VARCHAR', 'YES', None, None, None), ('other_postal_code', 'VARCHAR', 'YES', None, None, None), ('other_state', 'VARCHAR', 'YES', None, None, None), ('other_street', 'VARCHAR', 'YES', None, None, None), ('owner_id', 'VARCHAR', 'YES', None, None, None), ('phone', 'VARCHAR', 'YES', None, None, None), ('photo_url', 'VARCHAR', 'YES', None, None, None), ('reports_to_id', 'VARCHAR', 'YES', None, None, None), ('salutation', 'VARCHAR', 'YES', None, None, None), ('title', 'VARCHAR', 'YES', None, None, None)]
stg_salesforce__opportunity [('account_id', 'VARCHAR', 'YES', None, None, None), ('amount', 'DECIMAL(18,2)', 'YES', None, None, None), ('campaign_id', 'VARCHAR', 'YES', None, None, None), ('close_date', 'DATE', 'YES', None, None, None), ('created_date', 'TIMESTAMP', 'YES', None, None, None), ('opportunity_description', 'VARCHAR', 'YES', None, None, None), ('expected_revenue', 'DECIMAL(15,2)', 'YES', None, None, None), ('fiscal', 'VARCHAR', 'YES', None, None, None), ('fiscal_quarter', 'INTEGER', 'YES', None, None, None), ('fiscal_year', 'INTEGER', 'YES', None, None, None), ('forecast_category', 'VARCHAR', 'YES', None, None, None), ('forecast_category_name', 'VARCHAR', 'YES', None, None, None), ('has_open_activity', 'BOOLEAN', 'YES', None, None, None), ('has_opportunity_line_item', 'BOOLEAN', 'YES', None, None, None), ('has_overdue_task', 'BOOLEAN', 'YES', None, None, None), ('opportunity_id', 'VARCHAR', 'YES', None, None, None), ('is_closed', 'BOOLEAN', 'YES', None, None, None), ('is_deleted', 'BOOLEAN', 'YES', None, None, None), ('is_won', 'BOOLEAN', 'YES', None, None, None), ('last_activity_date', 'DATE', 'YES', None, None, None), ('last_referenced_date', 'TIMESTAMP', 'YES', None, None, None), ('last_viewed_date', 'TIMESTAMP', 'YES', None, None, None), ('lead_source', 'VARCHAR', 'YES', None, None, None), ('opportunity_name', 'VARCHAR', 'YES', None, None, None), ('next_step', 'VARCHAR', 'YES', None, None, None), ('owner_id', 'VARCHAR', 'YES', None, None, None), ('probability', 'DECIMAL(5,2)', 'YES', None, None, None), ('record_type_id', 'VARCHAR', 'YES', None, None, None), ('stage_name', 'VARCHAR', 'YES', None, None, None), ('synced_quote_id', 'VARCHAR', 'YES', None, None, None), ('type', 'VARCHAR', 'YES', None, None, None), ('is_created_this_month', 'BOOLEAN', 'YES', None, None, None), ('is_created_this_quarter', 'BOOLEAN', 'YES', None, None, None), ('days_since_created', 'INTEGER', 'YES', None, None, None), ('days_to_close', 'INTEGER', 'YES', None, None, None), ('is_closed_this_month', 'BOOLEAN', 'YES', None, None, None), ('is_closed_this_quarter', 'BOOLEAN', 'YES', None, None, None)]
stg_salesforce__user [('account_id', 'VARCHAR', 'YES', None, None, None), ('alias', 'VARCHAR', 'YES', None, None, None), ('city', 'VARCHAR', 'YES', None, None, None), ('company_name', 'VARCHAR', 'YES', None, None, None), ('contact_id', 'VARCHAR', 'YES', None, None, None), ('country', 'VARCHAR', 'YES', None, None, None), ('country_code', 'VARCHAR', 'YES', None, None, None), ('department', 'VARCHAR', 'YES', None, None, None), ('email', 'VARCHAR', 'YES', None, None, None), ('first_name', 'VARCHAR', 'YES', None, None, None), ('user_id', 'VARCHAR', 'YES', None, None, None), ('individual_id', 'VARCHAR', 'YES', None, None, None), ('is_active', 'BOOLEAN', 'YES', None, None, None), ('last_login_date', 'TIMESTAMP', 'YES', None, None, None), ('last_name', 'VARCHAR', 'YES', None, None, None), ('last_referenced_date', 'TIMESTAMP', 'YES', None, None, None), ('last_viewed_date', 'TIMESTAMP', 'YES', None, None, None), ('manager_id', 'VARCHAR', 'YES', None, None, None), ('user_name', 'VARCHAR', 'YES', None, None, None), ('postal_code', 'VARCHAR', 'YES', None, None, None), ('profile_id', 'VARCHAR', 'YES', None, None, None), ('state', 'VARCHAR', 'YES', None, None, None), ('state_code', 'VARCHAR', 'YES', None, None, None), ('street', 'VARCHAR', 'YES', None, None, None), ('title', 'VARCHAR', 'YES', None, None, None), ('user_role_id', 'VARCHAR', 'YES', None, None, None), ('user_type', 'VARCHAR', 'YES', None, None, None), ('username', 'VARCHAR', 'YES', None, None, None)]
stg_salesforce__lead [('lead_id', 'VARCHAR', 'YES', None, None, None), ('first_name', 'VARCHAR', 'YES', None, None, None), ('last_name', 'VARCHAR', 'YES', None, None, None), ('lead_name', 'VARCHAR', 'YES', None, None, None), ('email', 'VARCHAR', 'YES', None, None, None), ('company', 'VARCHAR', 'YES', None, None, None), ('title', 'VARCHAR', 'YES', None, None, None), ('phone', 'VARCHAR', 'YES', None, None, None), ('lead_source', 'VARCHAR', 'YES', None, None, None), ('status', 'VARCHAR', 'YES', None, None, None), ('owner_id', 'VARCHAR', 'YES', None, None, None), ('is_deleted', 'BOOLEAN', 'YES', None, None, None), ('lead_description', 'VARCHAR', 'YES', None, None, None), ('annual_revenue', 'DECIMAL(18,3)', 'YES', None, None, None), ('city', 'VARCHAR', 'YES', None, None, None), ('converted_account_id', 'VARCHAR', 'YES', None, None, None), ('converted_contact_id', 'VARCHAR', 'YES', None, None, None), ('converted_date', 'TIMESTAMP', 'YES', None, None, None), ('converted_opportunity_id', 'VARCHAR', 'YES', None, None, None), ('country', 'VARCHAR', 'YES', None, None, None), ('country_code', 'VARCHAR', 'YES', None, None, None), ('created_by_id', 'VARCHAR', 'YES', None, None, None), ('created_date', 'TIMESTAMP', 'YES', None, None, None), ('email_bounced_date', 'TIMESTAMP', 'YES', None, None, None), ('email_bounced_reason', 'VARCHAR', 'YES', None, None, None), ('fax', 'VARCHAR', 'YES', None, None, None), ('geocode_accuracy', 'VARCHAR', 'YES', None, None, None), ('has_opted_out_of_email', 'BOOLEAN', 'YES', None, None, None), ('industry', 'VARCHAR', 'YES', None, None, None), ('is_converted', 'BOOLEAN', 'YES', None, None, None), ('is_unread_by_owner', 'BOOLEAN', 'YES', None, None, None), ('last_activity_date', 'DATE', 'YES', None, None, None), ('last_modified_date', 'TIMESTAMP', 'YES', None, None, None), ('last_referenced_date', 'TIMESTAMP', 'YES', None, None, None), ('last_viewed_date', 'TIMESTAMP', 'YES', None, None, None), ('latitude', 'DECIMAL(18,3)', 'YES', None, None, None), ('longitude', 'DECIMAL(18,3)', 'YES', None, None, None), ('master_record_id', 'VARCHAR', 'YES', None, None, None), ('mobile_phone', 'VARCHAR', 'YES', None, None, None), ('number_of_employees', 'INTEGER', 'YES', None, None, None), ('photo_url', 'VARCHAR', 'YES', None, None, None), ('postal_code', 'VARCHAR', 'YES', None, None, None), ('salutation', 'VARCHAR', 'YES', None, None, None), ('state', 'VARCHAR', 'YES', None, None, None), ('state_code', 'VARCHAR', 'YES', None, None, None), ('street', 'VARCHAR', 'YES', None, None, None), ('system_modstamp', 'TIMESTAMP', 'YES', None, None, None), ('website', 'VARCHAR', 'YES', None, None, None)]
stg_salesforce__event [('event_id', 'VARCHAR', 'YES', None, None, None), ('activity_date', 'TIMESTAMP', 'YES', None, None, None), ('activity_date_time', 'TIMESTAMP', 'YES', None, None, None), ('is_deleted', 'BOOLEAN', 'YES', None, None, None), ('event_description', 'VARCHAR', 'YES', None, None, None), ('duration_in_minutes', 'INTEGER', 'YES', None, None, None), ('end_date_time', 'TIMESTAMP', 'YES', None, None, None), ('location', 'VARCHAR', 'YES', None, None, None), ('owner_id', 'VARCHAR', 'YES', None, None, None), ('start_date_time', 'TIMESTAMP', 'YES', None, None, None), ('subject', 'VARCHAR', 'YES', None, None, None), ('type', 'VARCHAR', 'YES', None, None, None), ('what_id', 'VARCHAR', 'YES', None, None, None), ('who_id', 'VARCHAR', 'YES', None, None, None)]
```

### event 63

```json
{
  "event_id": 63,
  "agent_command_sequence": 30,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/63.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 4538,
    "decoded_characters": 1615
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/63.json",
  "timestamp": "2026-10-25T04:12:53.449749",
  "target_table_name_hits": [
    "stg_salesforce__opportunity_line_item"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 2204,
  "retention": "full_original"
}
```
```bash
python - <<'PY'
import duckdb,yaml,pathlib
c=duckdb.connect('salesforce.duckdb',read_only=True)
con=yaml.safe_load(open('docs/data_contract.yaml'))
for layer, schema, key in [('staging_contract','staging','name')]:
 for m in con[layer]['tables']:
  table=m['name']; n=c.execute(f'select count(*) from {schema}.{table}').fetchone()[0]
  if table.endswith('__account') or table.endswith('__user') or table.endswith('__lead') or table.endswith('__task') or table.endswith('__event') or table.endswith('__opportunity'):
   pk=m['columns'][0]['name']
   # unique constraints defined in contract only
  print(table,n)
for layer,schema in [('intermediate_models','intermediate'),('marts_models','marts')]:
 for m in con['modeling_spec'][layer]:
  actual=[r[0] for r in c.execute(f'describe {schema}.{m["name"]}').fetchall()]
  expected=[x['name'] for x in m['columns']]
  assert set(actual)==set(expected),(m['name'],set(expected)-set(actual),set(actual)-set(expected))
print('Contract model field sets match')
print('account uniqueness',c.execute('select count(*),count(distinct account_id) from intermediate.int_salesforce__account_enhanced').fetchone())
print('lead uniqueness',c.execute('select count(*),count(distinct lead_id) from intermediate.int_salesforce__lead_conversion_funnel').fetchone())
print('account fct',c.execute('select count(*),count(distinct account_id) from marts.fct_salesforce__account_engagement').fetchone())
print('SQL file count',len(list(pathlib.Path('sql').rglob('*.sql'))),'semicolons',[(str(p),';' in p.read_text()) for p in pathlib.Path('sql').rglob('*.sql') if ';' in p.read_text()])
PY
```
```json
{
  "event_id": 64,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/64.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 4219,
    "decoded_characters": 589
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/64.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
stg_salesforce__account 2999
stg_salesforce__contact 3000
stg_salesforce__opportunity 3000
stg_salesforce__user 993
stg_salesforce__lead 2996
stg_salesforce__task 2998
stg_salesforce__event 3000
stg_salesforce__user_role 50
stg_salesforce__product_2 500
stg_salesforce__opportunity_line_item 3000
stg_salesforce__order 3000
stg_salesforce__account_history 2018
stg_salesforce__contact_history 2434
stg_salesforce__opportunity_history 3000
Contract model field sets match
account uniqueness (2999, 2999)
lead uniqueness (2996, 2996)
account fct (2999, 2999)
SQL file count 37 semicolons []
```

### event 67

```json
{
  "event_id": 67,
  "agent_command_sequence": 32,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/67.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1440,
    "decoded_characters": 89
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/67.json",
  "timestamp": "2026-10-25T04:13:05.978082",
  "target_table_name_hits": [
    "stg_salesforce__opportunity_line_item"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 1245,
  "retention": "full_original"
}
```
```bash
for f in sql/staging/*.sql; do printf '%-55s ' "$(basename "$f")"; sed -n '2p' "$f"; done
```
```json
{
  "event_id": 68,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/68.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1121,
    "decoded_characters": 1156
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/68.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
stg_salesforce__account.sql                                   id as account_id,
stg_salesforce__account_history.sql                           id as account_id,
stg_salesforce__contact.sql                                   account_id as account_id,
stg_salesforce__contact_history.sql                           id as contact_id,
stg_salesforce__event.sql                                     id as event_id,
stg_salesforce__lead.sql                                      id as lead_id,
stg_salesforce__opportunity.sql                               account_id as account_id,
stg_salesforce__opportunity_history.sql                       id as opportunity_id,
stg_salesforce__opportunity_line_item.sql                     id as opportunity_line_item_id,
stg_salesforce__order.sql                                     id as order_id,
stg_salesforce__product_2.sql                                 id as product_2_id,
stg_salesforce__task.sql                                      id as task_id,
stg_salesforce__user.sql                                      account_id as account_id,
stg_salesforce__user_role.sql                                 id as user_role_id,
```

### event 89

```json
{
  "event_id": 89,
  "agent_command_sequence": 43,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/89.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 3888,
    "decoded_characters": 1304
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/89.json",
  "timestamp": "2026-10-25T04:14:27.027534",
  "target_table_name_hits": [
    "stg_salesforce__opportunity_line_item"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 2453,
  "retention": "full_original"
}
```
```bash
python - <<'PY'
import yaml,duckdb
c=duckdb.connect('salesforce.duckdb',read_only=True); spec=yaml.safe_load(open('docs/data_contract.yaml'))
for t in spec['staging_contract']['tables']:
 name=t['name']; cols=c.execute(f'describe staging.{name}').fetchall(); expected=t['columns']
 if [x[0] for x in cols] != [x['name'] for x in expected]: print('column mismatch',name)
 for got,want in zip(cols,expected):
  typ=got[1].upper().replace(' ','')
  exp=want['data_type'].upper().replace(' ','')
  if typ!=exp: print('type mismatch',name,got[0],typ,exp)
print('quality checks on nulls/unique keys')
for sch,tbl,key in [('staging','stg_salesforce__account','account_id'),('staging','stg_salesforce__contact','contact_id'),('staging','stg_salesforce__opportunity','opportunity_id'),('staging','stg_salesforce__user','user_id'),('staging','stg_salesforce__lead','lead_id'),('staging','stg_salesforce__task','task_id'),('staging','stg_salesforce__event','event_id'),('staging','stg_salesforce__account_history','history_unique_key'),('staging','stg_salesforce__contact_history','history_unique_key'),('staging','stg_salesforce__opportunity_history','history_unique_key')]:
 print(tbl,c.execute(f'select count(*),count({key}),count(distinct {key}) from {sch}.{tbl}').fetchone())
PY
find sql -type f | sort | wc -l
```
```json
{
  "event_id": 90,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/90.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 3569,
    "decoded_characters": 1149
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/90.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
type mismatch stg_salesforce__opportunity_line_item list_price DECIMAL(18,3) DECIMAL
type mismatch stg_salesforce__opportunity_line_item quantity DECIMAL(18,3) DECIMAL
type mismatch stg_salesforce__opportunity_line_item total_price DECIMAL(18,3) DECIMAL
type mismatch stg_salesforce__opportunity_line_item unit_price DECIMAL(18,3) DECIMAL
type mismatch stg_salesforce__order total_amount DECIMAL(18,3) DECIMAL
type mismatch stg_salesforce__opportunity_history amount DECIMAL(18,3) DECIMAL
type mismatch stg_salesforce__opportunity_history expected_revenue DECIMAL(18,3) DECIMAL
type mismatch stg_salesforce__opportunity_history probability DECIMAL(18,3) DECIMAL
quality checks on nulls/unique keys
stg_salesforce__account (2999, 2999, 2999)
stg_salesforce__contact (3000, 3000, 3000)
stg_salesforce__opportunity (3000, 3000, 3000)
stg_salesforce__user (993, 993, 993)
stg_salesforce__lead (2996, 2996, 2996)
stg_salesforce__task (2998, 2998, 2998)
stg_salesforce__event (3000, 3000, 3000)
stg_salesforce__account_history (3000, 3000, 3000)
stg_salesforce__contact_history (2434, 2434, 2434)
stg_salesforce__opportunity_history (3000, 3000, 3000)
37
```

## result_md_table_sentences

```json
{
  "present": false,
  "searched_path": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/result.md",
  "sentences": []
}
```

## original_files

```json
{
  "paths": [
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/13.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/14.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/15.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/16.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/17.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/18.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/19.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/20.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/31.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/32.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/35.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/36.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/43.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/44.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/49.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/50.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/63.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/64.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/67.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/68.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/7.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/8.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/89.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/90.json",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql",
    "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml",
    "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb",
    "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql"
  ],
  "archive": "/home/katherine/Assumption_Ledger/traces/dacomp_deimpl_prev.tar.gz",
  "gold_SQL_search_root": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql",
  "gold_SQL_search_names": [
    "stg_salesforce__opportunity_line_item",
    "stg_salesforce__opportunity_line_item"
  ],
  "source_fingerprints": "records/012_input_before.json"
}
```
