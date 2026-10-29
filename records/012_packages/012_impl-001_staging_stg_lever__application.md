# impl-001 / stg_lever__application

## basic_information

```json
{
  "task": "impl-001",
  "layer": "staging",
  "table": "stg_lever__application",
  "status": "待标注",
  "difference_source": {
    "kind": "original_007_009",
    "record": "records/007_tolerance_tables.jsonl",
    "detail_record": "/home/katherine/Assumption_Ledger/records/004_staging_impl-001.json",
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
  "source_path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml",
  "source_sha256": "a33a4b28eb533e84493c3ef0187b1f89e92149b98175220c6fd928d3fbcedc11",
  "parse_mode": "strict",
  "requested_table": "stg_lever__application",
  "status": "found"
}
```
```json
{
  "yaml_path": [
    "staging_contract",
    "tables",
    7
  ],
  "start_line": 390,
  "end_line": 428
}
```
```yaml
    - name: stg_lever__application
      description: "Cleaned job applications linking candidates to postings with application status and metadata"
      source_table: "raw.application"
      columns:
        - name: application_id
          data_type: VARCHAR(50)
          constraints: [not_null, unique]
        - name: opportunity_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: posting_id
          data_type: VARCHAR(50)
        - name: type
          data_type: VARCHAR(50)
        - name: candidate_id
          data_type: BIGINT
        - name: posting_hiring_manager_user_id
          data_type: VARCHAR(50)
        - name: posting_owner_user_id
          data_type: VARCHAR(50)
        - name: company
          data_type: VARCHAR(255)
        - name: referrer_user_id
          data_type: VARCHAR(50)
        - name: requisition_id
          data_type: VARCHAR(50)
        - name: archived_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "archived_at IS NULL OR created_at IS NULL OR try_cast(archived_at as timestamp) >= try_cast(created_at as timestamp)"
              on_failure: delete_row
        - name: archived_reason_id
          data_type: VARCHAR(50)
        - name: comments
          data_type: VARCHAR(1000)
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]

```

## agent_final_SQL

```json
{
  "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
  "sha256": "5ace39feb0cd0f84a617507f230df30324eefd27e14a9c51524ebdc672e88aba",
  "start_line": 1,
  "end_line": 31
}
```
```sql
WITH typed AS (
    SELECT
        try_cast(r."id" AS VARCHAR(50)) AS application_id,
        trim(cast(r."opportunity_id" AS VARCHAR)) AS opportunity_id,
        trim(cast(r."posting_id" AS VARCHAR)) AS posting_id,
        try_cast(r."type" AS VARCHAR(50)) AS type,
        try_cast(r."candidate_id" AS BIGINT) AS candidate_id,
        try_cast(r."posting_hiring_manager_id" AS VARCHAR(50)) AS posting_hiring_manager_user_id,
        try_cast(r."posting_owner_id" AS VARCHAR(50)) AS posting_owner_user_id,
        try_cast(r."company" AS VARCHAR(255)) AS company,
        try_cast(r."referrer_id" AS VARCHAR(50)) AS referrer_user_id,
        trim(cast(r."requisition_for_hire_id" AS VARCHAR)) AS requisition_id,
        try_cast(r."archived_at" AS TIMESTAMP) AS archived_at,
        try_cast(r."archived_reason_id" AS VARCHAR(50)) AS archived_reason_id,
        try_cast(r."comments" AS VARCHAR(1000)) AS comments,
        try_cast(r."created_at" AS TIMESTAMP) AS created_at
    FROM raw.application AS r
),
valid AS (
    SELECT * FROM typed
    WHERE         application_id IS NOT NULL AND
              opportunity_id IS NOT NULL AND
              created_at IS NOT NULL
),
ranked AS (
    SELECT *, row_number() OVER (PARTITION BY application_id ORDER BY application_id) AS _row_num
    FROM valid
)
SELECT application_id, opportunity_id, posting_id, type, candidate_id, posting_hiring_manager_user_id, posting_owner_user_id, company, referrer_user_id, requisition_id, archived_at, archived_reason_id, comments, created_at
FROM ranked
WHERE _row_num = 1
```

## gold_SQL_仅供定位差异

```json
{
  "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
  "sha256": "0bf1713931ae6f69dda767e3547e26b0d8d12755b81bb8d54d2470ac48403ca5",
  "start_line": 1,
  "end_line": 30
}
```
```sql
-- Standardized cleaning of application information (aligned docs/staging_data_specification.yaml)

with cleaned as (
    select
        trim(id) as application_id,
        opportunity_id,
        posting_id,
        type,
        candidate_id,
        posting_hiring_manager_id as posting_hiring_manager_user_id,
        posting_owner_id as posting_owner_user_id,
        trim(company) as company,
        referrer_id as referrer_user_id,
        requisition_for_hire_id as requisition_id,
        try_cast(archived_at as timestamp) as archived_at,
        archived_reason_id,
        comments,
        try_cast(created_at as timestamp) as created_at
    from raw.application
), filtered as (
    select * from cleaned
    where
        -- Delete a row: the primary key is not empty, the opportunity foreign key is not empty, and the creation time is not empty
        length(application_id) > 0
        and opportunity_id is not null
        -- Relax time filtering: do not drop rows because created_at is empty, only compare when comparable
        and (archived_at is null or created_at is null or archived_at >= created_at)
)

select * from filtered
```

## differences

```json
{
  "kind": "original_007_009",
  "record": "records/007_tolerance_tables.jsonl",
  "detail_record": "/home/katherine/Assumption_Ledger/records/004_staging_impl-001.json",
  "prediction_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb",
  "gold_database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb",
  "actual_schema": "staging",
  "table": "stg_lever__application",
  "candidate_date": null,
  "comparison_columns": [
    "application_id",
    "opportunity_id",
    "posting_id",
    "type",
    "candidate_id",
    "posting_hiring_manager_user_id",
    "posting_owner_user_id",
    "company",
    "referrer_user_id",
    "requisition_id",
    "archived_at",
    "archived_reason_id",
    "comments",
    "created_at"
  ],
  "key_columns": [
    "application_id"
  ],
  "prediction_rows": 0,
  "gold_rows": 5000,
  "row_delta": -5000,
  "key_statistics": {
    "pred_distinct_keys": 0,
    "gold_distinct_keys": 5000,
    "pred_duplicate_key_groups": 0,
    "gold_duplicate_key_groups": 0,
    "pred_only_keys": 0,
    "gold_only_keys": 5000,
    "shared_keys": 0,
    "shared_nonunique_key_groups": 0
  },
  "l0_column_differences": [
    {
      "column": "application_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "opportunity_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "posting_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "type",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "candidate_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "posting_hiring_manager_user_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "posting_owner_user_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "company",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "referrer_user_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "requisition_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "archived_at",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "archived_reason_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "comments",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "created_at",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    }
  ],
  "l3_column_differences": null,
  "whole_match_level": "仍不匹配",
  "keyed_match_level": null,
  "selection_reason": "未进入 011，沿用原差异",
  "value_representation": "Unmodified DuckDB CAST AS VARCHAR; SQL NULL is JSON null. Keys use the unchanged historical L0 normalization.",
  "new_queries_only_read_existing_results": true,
  "one_side_key_examples": {
    "prediction_only": [],
    "gold_only": [
      {
        "key_normalized": {
          "application_id": "app10000677678"
        },
        "key_raw_text": {
          "application_id": "APP10000677678"
        },
        "rows_with_key": 1
      },
      {
        "key_normalized": {
          "application_id": "app10008939749"
        },
        "key_raw_text": {
          "application_id": "APP10008939749"
        },
        "rows_with_key": 1
      },
      {
        "key_normalized": {
          "application_id": "app10025907735"
        },
        "key_raw_text": {
          "application_id": "APP10025907735"
        },
        "rows_with_key": 1
      },
      {
        "key_normalized": {
          "application_id": "app10028946724"
        },
        "key_raw_text": {
          "application_id": "APP10028946724"
        },
        "rows_with_key": 1
      },
      {
        "key_normalized": {
          "application_id": "app10031694069"
        },
        "key_raw_text": {
          "application_id": "APP10031694069"
        },
        "rows_with_key": 1
      },
      {
        "key_normalized": {
          "application_id": "app10055323392"
        },
        "key_raw_text": {
          "application_id": "APP10055323392"
        },
        "rows_with_key": 1
      },
      {
        "key_normalized": {
          "application_id": "app10088026326"
        },
        "key_raw_text": {
          "application_id": "APP10088026326"
        },
        "rows_with_key": 1
      },
      {
        "key_normalized": {
          "application_id": "app10165697432"
        },
        "key_raw_text": {
          "application_id": "APP10165697432"
        },
        "rows_with_key": 1
      },
      {
        "key_normalized": {
          "application_id": "app10251652780"
        },
        "key_raw_text": {
          "application_id": "APP10251652780"
        },
        "rows_with_key": 1
      },
      {
        "key_normalized": {
          "application_id": "app10262830825"
        },
        "key_raw_text": {
          "application_id": "APP10262830825"
        },
        "rows_with_key": 1
      }
    ]
  },
  "column_details": [
    {
      "column": "application_id",
      "l0_counts_verbatim": {
        "column": "application_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "opportunity_id",
      "l0_counts_verbatim": {
        "column": "opportunity_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "posting_id",
      "l0_counts_verbatim": {
        "column": "posting_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "type",
      "l0_counts_verbatim": {
        "column": "type",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "candidate_id",
      "l0_counts_verbatim": {
        "column": "candidate_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "posting_hiring_manager_user_id",
      "l0_counts_verbatim": {
        "column": "posting_hiring_manager_user_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "posting_owner_user_id",
      "l0_counts_verbatim": {
        "column": "posting_owner_user_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "company",
      "l0_counts_verbatim": {
        "column": "company",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "referrer_user_id",
      "l0_counts_verbatim": {
        "column": "referrer_user_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "requisition_id",
      "l0_counts_verbatim": {
        "column": "requisition_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "archived_at",
      "l0_counts_verbatim": {
        "column": "archived_at",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "TIMESTAMP",
      "gold_actual_type": "TIMESTAMP"
    },
    {
      "column": "archived_reason_id",
      "l0_counts_verbatim": {
        "column": "archived_reason_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "comments",
      "l0_counts_verbatim": {
        "column": "comments",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "created_at",
      "l0_counts_verbatim": {
        "column": "created_at",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": null,
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "TIMESTAMP",
      "gold_actual_type": "TIMESTAMP"
    }
  ]
}
```

## agent_constraints_006

```json
{
  "source_record": "records/006_contract_impl-001.json",
  "declarations": {
    "grain": [],
    "primary_key": [],
    "not_null": [
      {
        "columns": [
          "application_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "staging_contract",
              "tables",
              7,
              "columns",
              0,
              "constraints",
              0
            ],
            "start_line": 396,
            "end_line": 396,
            "original_excerpt": "          constraints: [not_null, unique]\n",
            "decoded_value": [
              "not_null",
              "unique"
            ]
          }
        ]
      },
      {
        "columns": [
          "opportunity_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "staging_contract",
              "tables",
              7,
              "columns",
              1,
              "constraints",
              0
            ],
            "start_line": 399,
            "end_line": 399,
            "original_excerpt": "          constraints: [not_null]\n",
            "decoded_value": [
              "not_null"
            ]
          }
        ]
      },
      {
        "columns": [
          "created_at"
        ],
        "sources": [
          {
            "yaml_path": [
              "staging_contract",
              "tables",
              7,
              "columns",
              13,
              "constraints",
              0
            ],
            "start_line": 427,
            "end_line": 427,
            "original_excerpt": "          constraints: [not_null]\n",
            "decoded_value": [
              "not_null"
            ]
          }
        ]
      }
    ],
    "unique": [
      {
        "columns": [
          "application_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "staging_contract",
              "tables",
              7,
              "columns",
              0,
              "constraints",
              1
            ],
            "start_line": 396,
            "end_line": 396,
            "original_excerpt": "          constraints: [not_null, unique]\n",
            "decoded_value": [
              "not_null",
              "unique"
            ]
          }
        ]
      }
    ]
  },
  "agent": {
    "table_exists": true,
    "actual_schema": "staging",
    "table_type": "BASE TABLE",
    "same_name_other_schemas": [],
    "row_count": 0,
    "checks": {
      "grain": [],
      "primary_key": [],
      "not_null": [
        {
          "columns": [
            "application_id"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        },
        {
          "columns": [
            "opportunity_id"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        },
        {
          "columns": [
            "created_at"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        }
      ],
      "unique": [
        {
          "columns": [
            "application_id"
          ],
          "status": "checked",
          "violated": false,
          "sql": "SELECT count(*),count(*) FILTER(WHERE \"__ledger_group_count\">1),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1),0),\n                      coalesce(sum(\"__ledger_group_count\"-1) FILTER(WHERE \"__ledger_group_count\">1),0),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"application_id\" IS NULL),0),\n                      count(*) FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"application_id\" IS NULL)),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"application_id\" IS NULL)),0),\n                      coalesce(sum(\"__ledger_group_count\"-1) FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"application_id\" IS NULL)),0),count(*) FILTER(WHERE \"__ledger_group_count\">1 AND (\"application_id\" IS NULL)),\n                      coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1 AND (\"application_id\" IS NULL)),0)\n                      FROM (SELECT \"application_id\",count(*) AS \"__ledger_group_count\" FROM \"staging\".\"stg_lever__application\" GROUP BY \"application_id\") grouped_keys",
          "sql_key_order": [
            "application_id"
          ],
          "distinct_key_groups": 0,
          "duplicate_key_groups": 0,
          "rows_in_duplicate_groups": 0,
          "excess_duplicate_rows": 0,
          "null_key_rows": 0,
          "nonnull_duplicate_key_groups": 0,
          "nonnull_rows_in_duplicate_groups": 0,
          "nonnull_excess_duplicate_rows": 0,
          "null_containing_duplicate_key_groups": 0,
          "rows_in_null_containing_duplicate_groups": 0,
          "including_nulls_duplicate_key_groups": 0,
          "including_nulls_rows_in_duplicate_groups": 0
        }
      ]
    },
    "actual_table": "stg_lever__application",
    "actual_columns": [
      "application_id",
      "opportunity_id",
      "posting_id",
      "type",
      "candidate_id",
      "posting_hiring_manager_user_id",
      "posting_owner_user_id",
      "company",
      "referrer_user_id",
      "requisition_id",
      "archived_at",
      "archived_reason_id",
      "comments",
      "created_at"
    ],
    "missing_declared_columns": [],
    "not_null_count_sql": "SELECT count(*) FILTER(WHERE \"application_id\" IS NULL),count(*) FILTER(WHERE \"created_at\" IS NULL),count(*) FILTER(WHERE \"opportunity_id\" IS NULL) FROM \"staging\".\"stg_lever__application\"",
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
        "status": "checked_no_violation",
        "violated": false,
        "declared_checks": 3,
        "checked_checks": 3,
        "unknown_checks": 0,
        "complete": true
      },
      "unique": {
        "status": "checked_no_violation",
        "violated": false,
        "declared_checks": 1,
        "checked_checks": 1,
        "unknown_checks": 0,
        "complete": true
      }
    },
    "any_constraint_violated": false
  }
}
```

## all_markers_and_evidence_008

```json
{
  "source_record": "records/008_table_scan.jsonl",
  "verbatim_record": {
    "task": "impl-001",
    "layer": "staging",
    "table": "stg_lever__application",
    "logical_contract_table": "stg_lever__application",
    "delivery_name_mapping_evidence": [],
    "inventory_sources": {
      "retained_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb",
      "present_in_database": true,
      "agent_final_sql_files": [
        "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql"
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
          "007_prediction_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb"
        }
      ],
      "status": "待标注",
      "comparison_lookup_layer": "staging",
      "comparison_lookup_table": "stg_lever__application",
      "actual_gold_relation_exists": true
    },
    "contract": {
      "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml",
      "blocks": [
        {
          "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml",
          "start_line": 390,
          "end_line": 427,
          "original_text": "    - name: stg_lever__application\n      description: \"Cleaned job applications linking candidates to postings with application status and metadata\"\n      source_table: \"raw.application\"\n      columns:\n        - name: application_id\n          data_type: VARCHAR(50)\n          constraints: [not_null, unique]\n        - name: opportunity_id\n          data_type: VARCHAR(50)\n          constraints: [not_null]\n        - name: posting_id\n          data_type: VARCHAR(50)\n        - name: type\n          data_type: VARCHAR(50)\n        - name: candidate_id\n          data_type: BIGINT\n        - name: posting_hiring_manager_user_id\n          data_type: VARCHAR(50)\n        - name: posting_owner_user_id\n          data_type: VARCHAR(50)\n        - name: company\n          data_type: VARCHAR(255)\n        - name: referrer_user_id\n          data_type: VARCHAR(50)\n        - name: requisition_id\n          data_type: VARCHAR(50)\n        - name: archived_at\n          data_type: TIMESTAMP\n          validation_rules:\n            - rule: \"archived_at IS NULL OR created_at IS NULL OR try_cast(archived_at as timestamp) >= try_cast(created_at as timestamp)\"\n              on_failure: delete_row\n        - name: archived_reason_id\n          data_type: VARCHAR(50)\n        - name: comments\n          data_type: VARCHAR(1000)\n        - name: created_at\n          data_type: TIMESTAMP\n          constraints: [not_null]\n",
          "yaml_path": [
            "staging_contract",
            "tables",
            7
          ]
        }
      ]
    },
    "output": {
      "status": "checked",
      "exists": true,
      "row_count": 0,
      "zero_rows": true,
      "columns": [
        {
          "name": "application_id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "opportunity_id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "posting_id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "type",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "candidate_id",
          "type": "BIGINT",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "posting_hiring_manager_user_id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "posting_owner_user_id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "company",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "referrer_user_id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "requisition_id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "archived_at",
          "type": "TIMESTAMP",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "archived_reason_id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "comments",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "created_at",
          "type": "TIMESTAMP",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        }
      ],
      "all_null_columns": [],
      "constant_nonnull_columns": [],
      "equal_column_groups": [],
      "profile_sql": "SELECT count(*),count(\"application_id\"),min(CAST(\"application_id\" AS VARCHAR)),max(CAST(\"application_id\" AS VARCHAR)),sum(hash(CAST(\"application_id\" AS VARCHAR))),count(\"opportunity_id\"),min(CAST(\"opportunity_id\" AS VARCHAR)),max(CAST(\"opportunity_id\" AS VARCHAR)),sum(hash(CAST(\"opportunity_id\" AS VARCHAR))),count(\"posting_id\"),min(CAST(\"posting_id\" AS VARCHAR)),max(CAST(\"posting_id\" AS VARCHAR)),sum(hash(CAST(\"posting_id\" AS VARCHAR))),count(\"type\"),min(CAST(\"type\" AS VARCHAR)),max(CAST(\"type\" AS VARCHAR)),sum(hash(CAST(\"type\" AS VARCHAR))),count(\"candidate_id\"),min(CAST(\"candidate_id\" AS VARCHAR)),max(CAST(\"candidate_id\" AS VARCHAR)),sum(hash(CAST(\"candidate_id\" AS VARCHAR))),count(\"posting_hiring_manager_user_id\"),min(CAST(\"posting_hiring_manager_user_id\" AS VARCHAR)),max(CAST(\"posting_hiring_manager_user_id\" AS VARCHAR)),sum(hash(CAST(\"posting_hiring_manager_user_id\" AS VARCHAR))),count(\"posting_owner_user_id\"),min(CAST(\"posting_owner_user_id\" AS VARCHAR)),max(CAST(\"posting_owner_user_id\" AS VARCHAR)),sum(hash(CAST(\"posting_owner_user_id\" AS VARCHAR))),count(\"company\"),min(CAST(\"company\" AS VARCHAR)),max(CAST(\"company\" AS VARCHAR)),sum(hash(CAST(\"company\" AS VARCHAR))),count(\"referrer_user_id\"),min(CAST(\"referrer_user_id\" AS VARCHAR)),max(CAST(\"referrer_user_id\" AS VARCHAR)),sum(hash(CAST(\"referrer_user_id\" AS VARCHAR))),count(\"requisition_id\"),min(CAST(\"requisition_id\" AS VARCHAR)),max(CAST(\"requisition_id\" AS VARCHAR)),sum(hash(CAST(\"requisition_id\" AS VARCHAR))),count(\"archived_at\"),min(CAST(\"archived_at\" AS VARCHAR)),max(CAST(\"archived_at\" AS VARCHAR)),sum(hash(CAST(\"archived_at\" AS VARCHAR))),count(\"archived_reason_id\"),min(CAST(\"archived_reason_id\" AS VARCHAR)),max(CAST(\"archived_reason_id\" AS VARCHAR)),sum(hash(CAST(\"archived_reason_id\" AS VARCHAR))),count(\"comments\"),min(CAST(\"comments\" AS VARCHAR)),max(CAST(\"comments\" AS VARCHAR)),sum(hash(CAST(\"comments\" AS VARCHAR))),count(\"created_at\"),min(CAST(\"created_at\" AS VARCHAR)),max(CAST(\"created_at\" AS VARCHAR)),sum(hash(CAST(\"created_at\" AS VARCHAR))) FROM \"staging\".\"stg_lever__application\"",
      "equal_column_confirmation_queries": [],
      "equality_policy": "exact CAST AS VARCHAR per row; no trim/case/numeric/date normalization; both NULL ignored; at least one nonnull equal row; one-sided NULL differs",
      "actual_schema": "staging",
      "actual_table": "stg_lever__application",
      "relation_type": "BASE TABLE"
    },
    "agent_sql": [
      {
        "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
        "status": "parsed",
        "parser": "30.25.0",
        "sources": [
          {
            "name": "raw.application",
            "canonical": "raw.application",
            "locations": [
              {
                "line": 17,
                "end_line": 17
              }
            ]
          }
        ],
        "unresolved_source_expressions": [],
        "row_generator_expressions": [],
        "outputs": [
          {
            "name": "application_id",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"id\" AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 3,
                "end_line": 3,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "application_id",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "application_id",
            "retained_output_ordinal": 1
          },
          {
            "name": "opportunity_id",
            "alternatives": [
              {
                "expression_sql": "TRIM(CAST(r.\"opportunity_id\" AS TEXT))",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 4,
                "end_line": 4,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "opportunity_id",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "opportunity_id",
            "retained_output_ordinal": 2
          },
          {
            "name": "posting_id",
            "alternatives": [
              {
                "expression_sql": "TRIM(CAST(r.\"posting_id\" AS TEXT))",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 5,
                "end_line": 5,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "posting_id",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "posting_id",
            "retained_output_ordinal": 3
          },
          {
            "name": "type",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"type\" AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 6,
                "end_line": 6,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "type",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "type",
            "retained_output_ordinal": 4
          },
          {
            "name": "candidate_id",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"candidate_id\" AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 7,
                "end_line": 7,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "candidate_id",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "candidate_id",
            "retained_output_ordinal": 5
          },
          {
            "name": "posting_hiring_manager_user_id",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"posting_hiring_manager_id\" AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 8,
                "end_line": 8,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "posting_hiring_manager_user_id",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "posting_hiring_manager_user_id",
            "retained_output_ordinal": 6
          },
          {
            "name": "posting_owner_user_id",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"posting_owner_id\" AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 9,
                "end_line": 9,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "posting_owner_user_id",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "posting_owner_user_id",
            "retained_output_ordinal": 7
          },
          {
            "name": "company",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"company\" AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 10,
                "end_line": 10,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "company",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "company",
            "retained_output_ordinal": 8
          },
          {
            "name": "referrer_user_id",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"referrer_id\" AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 11,
                "end_line": 11,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "referrer_user_id",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "referrer_user_id",
            "retained_output_ordinal": 9
          },
          {
            "name": "requisition_id",
            "alternatives": [
              {
                "expression_sql": "TRIM(CAST(r.\"requisition_for_hire_id\" AS TEXT))",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 12,
                "end_line": 12,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "requisition_id",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "requisition_id",
            "retained_output_ordinal": 10
          },
          {
            "name": "archived_at",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"archived_at\" AS TIMESTAMP)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 13,
                "end_line": 13,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "archived_at",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "archived_at",
            "retained_output_ordinal": 11
          },
          {
            "name": "archived_reason_id",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"archived_reason_id\" AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 14,
                "end_line": 14,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "archived_reason_id",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "archived_reason_id",
            "retained_output_ordinal": 12
          },
          {
            "name": "comments",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"comments\" AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 15,
                "end_line": 15,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "comments",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "comments",
            "retained_output_ordinal": 13
          },
          {
            "name": "created_at",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(r.\"created_at\" AS TIMESTAMP)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
                "line": 16,
                "end_line": 16,
                "kind": "nonliteral",
                "via": "column_reference_to_literal_projection",
                "outer_expression_sql": "created_at",
                "outer_line": 29
              }
            ],
            "sql_projection_name": "created_at",
            "retained_output_ordinal": 14
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
            "name": "raw.application",
            "canonical": "raw.application",
            "basis": "source_table",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml",
            "block_start_line": 390
          },
          {
            "name": "raw.application",
            "canonical": "raw.application",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml",
            "line": 392,
            "line_text": "      source_table: \"raw.application\""
          }
        ],
        "canonical_names": [
          "raw.application"
        ]
      },
      "agent_direct_read_sources": [
        "raw.application"
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
          "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__application.sql"
        ]
      },
      "contract": {
        "available": true,
        "appears": false,
        "hits": []
      }
    },
    "any_result_keyword_excerpt_ids": [
      "008-000244",
      "008-000362",
      "008-000365",
      "008-000495",
      "008-000496",
      "008-000499",
      "008-000500",
      "008-000502",
      "008-000504",
      "008-000505",
      "008-000506",
      "008-000508",
      "008-000509",
      "008-000518",
      "008-000519",
      "008-000520"
    ],
    "trace_flags": {
      "A1_zero_rows": true,
      "A2_all_null_column": false,
      "A3_constant_nonnull_column": false,
      "A4_equal_columns": false,
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
  "event_source_root": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent",
  "actual_read_sources_from_008_B7": [
    "raw.application"
  ],
  "name_match_policy": "Case-insensitive complete identifier-name boundaries; source names include qualified form and bare leaf name. No semantic association inferred.",
  "matched_step_count": 10,
  "full_original_characters_before_budget": 74883,
  "budget_triggered": true,
  "source_only_steps_indexed": 3,
  "retained_full_original_characters": 55819,
  "full_target_steps_exceed_60000": false,
  "budget_policy": "If total command/output text exceeds 60000 characters, keep every target-table step complete and retain only id/location/first line for source-only steps. Do not rewrite or truncate a kept original step."
}
```

### event 5

```json
{
  "event_id": 5,
  "agent_command_sequence": 1,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/5.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1432,
    "decoded_characters": 102
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/5.json",
  "timestamp": "2026-10-25T00:36:50.463075",
  "target_table_name_hits": [
    "stg_lever__application"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 4602,
  "retention": "full_original"
}
```
```bash
pwd && ls -la && find sql -maxdepth 3 -type f | sort | head -100 && cat config/layer_dependencies.yaml
```
```json
{
  "event_id": 6,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/6.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1118,
    "decoded_characters": 4500
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/6.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001
total 21060
drwxr-xr-x 8 katherine katherine     4096 Oct 25 00:36 .
drwx------ 3 katherine katherine       60 Oct 25 00:36 ..
drwxr-xr-x 3 katherine katherine     4096 Oct 25 00:36 .agent-python
drwxr-xr-x 2 katherine katherine     4096 Oct 25 00:36 .tmp
drwxr-xr-x 2 katherine katherine     4096 Oct 17 17:41 config
drwxr-xr-x 2 katherine katherine     4096 Oct 17 17:41 docs
-rw-r--r-- 1 katherine katherine 21508096 Oct 17 17:41 lever_start.duckdb
-rw-r--r-- 1 katherine katherine     4283 Oct 17 17:41 lever_start.yaml
drwxr-xr-x 2 katherine katherine     4096 Oct 17 17:41 raw_data
-rw-r--r-- 1 katherine katherine    13414 Oct 17 17:41 run.py
drwxr-xr-x 5 katherine katherine     4096 Oct 17 17:41 sql
-rw-r--r-- 1 katherine katherine     3736 Oct 17 17:41 test_single_sql.py
# Lever data warehouse hierarchical dependency configuration
# Define the execution order and dependencies of the data hierarchy

layers:
  staging:
    description: "Raw data cleaning and normalization layer"
    tables:
      - stg_lever__application
      - stg_lever__archive_reason
      - stg_lever__contact_email
      - stg_lever__contact_link
      - stg_lever__contact_phone
      - stg_lever__feedback_form
      - stg_lever__feedback_form_field
      - stg_lever__interview
      - stg_lever__interview_feedback
      - stg_lever__interviewer_user
      - stg_lever__offer
      - stg_lever__opportunity
      - stg_lever__opportunity_source
      - stg_lever__opportunity_stage_history
      - stg_lever__opportunity_tag
      - stg_lever__posting
      - stg_lever__posting_interview
      - stg_lever__posting_tag
      - stg_lever__requisition
      - stg_lever__requisition_offer
      - stg_lever__requisition_posting
      - stg_lever__resume
      - stg_lever__stage
      - stg_lever__user

  intermediate:
    description: "Business logic processing and data integration layer"
    dependencies: ["staging"]
    tables:
      - int_lever__candidate_insights
      - int_lever__candidate_lifecycle
      - int_lever__contact_info
      - int_lever__hiring_funnel_metrics
      - int_lever__interview_feedback
      - int_lever__interview_users
      - int_lever__interviewer_performance
      - int_lever__opportunity_application
      - int_lever__opportunity_contact_info
      - int_lever__opportunity_tags
      - int_lever__opportunity_users
      - int_lever__posting_analytics
      - int_lever__posting_applications
      - int_lever__posting_interviews
      - int_lever__posting_performance
      - int_lever__posting_tags
      - int_lever__requisition_users

  marts:
    description: "Analytics-ready business entity layer"
    dependencies: ["intermediate"]
    tables:
      - lever__candidate_experience_insights
      - lever__candidate_quality_insights
      - lever__departmental_hiring_trends
      - lever__hiring_dashboard
      - lever__hiring_dashboard_simple
      - lever__hiring_dashboard_working
      - lever__hiring_manager_scorecard
      - lever__interview_enhanced
      - lever__opportunity_enhanced
      - lever__opportunity_stage_history
      - lever__posting_enhanced
      - lever__recruitment_analytics_dashboard
      - lever__requisition_enhanced

# Execution order of tables within the layer (if a specific order is required)
execution_order:
  intermediate:
    - int_lever__contact_info
    - int_lever__opportunity_application
    - int_lever__opportunity_tags
    - int_lever__opportunity_contact_info
    - int_lever__interview_feedback
    - int_lever__interview_users
    - int_lever__opportunity_users
    - int_lever__posting_applications
    - int_lever__posting_interviews
    - int_lever__posting_tags
    - int_lever__requisition_users
    - int_lever__candidate_insights
    - int_lever__candidate_lifecycle
    - int_lever__hiring_funnel_metrics
    - int_lever__interviewer_performance
    - int_lever__posting_analytics
    - int_lever__posting_performance

  marts:
    - lever__interview_enhanced
    - lever__posting_enhanced
    - lever__opportunity_enhanced
    - lever__opportunity_stage_history
    - lever__requisition_enhanced
    - lever__candidate_quality_insights
    - lever__candidate_experience_insights
    - lever__departmental_hiring_trends
    - lever__hiring_manager_scorecard
    - lever__hiring_dashboard
    - lever__hiring_dashboard_simple
    - lever__hiring_dashboard_working
    - lever__recruitment_analytics_dashboard
```

### event 9

```json
{
  "event_id": 9,
  "agent_command_sequence": 3,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/9.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1624,
    "decoded_characters": 22
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/9.json",
  "timestamp": "2026-10-25T00:36:55.791361",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "application"
  ],
  "full_original_characters": 9711,
  "retention": "index_and_first_line_only",
  "first_line_original": "sed -n '1,240p' run.py"
}
```
```json
{
  "event_id": 10,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/10.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1310,
    "decoded_characters": 9689
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/10.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 11

```json
{
  "event_id": 11,
  "agent_command_sequence": 4,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/11.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1623,
    "decoded_characters": 20
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/11.json",
  "timestamp": "2026-10-25T00:36:55.819397",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "application"
  ],
  "full_original_characters": 4303,
  "retention": "index_and_first_line_only",
  "first_line_original": "cat lever_start.yaml"
}
```
```json
{
  "event_id": 12,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/12.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1309,
    "decoded_characters": 4283
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/12.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 17

```json
{
  "event_id": 17,
  "agent_command_sequence": 7,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/17.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 11802,
    "decoded_characters": 5050
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/17.json",
  "timestamp": "2026-10-25T00:37:25.511072",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "application"
  ],
  "full_original_characters": 5050,
  "retention": "index_and_first_line_only",
  "first_line_original": "cat > /tmp/gen.py <<'PY'\n"
}
```
```json
{
  "event_id": 18,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/18.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 11486,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/18.json",
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
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/19.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 21568,
    "decoded_characters": 10132
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/19.json",
  "timestamp": "2026-10-25T00:37:49.796688",
  "target_table_name_hits": [
    "stg_lever__application"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 10132,
  "retention": "full_original"
}
```
```bash
cat > /tmp/models.py <<'PY'
from pathlib import Path
p=Path('sql/intermediate')
models={
'int_lever__contact_info':'''WITH emails AS (SELECT contact_id, string_agg('<' || email || '>', ', ') AS emails FROM staging.stg_lever__contact_email WHERE email IS NOT NULL GROUP BY contact_id), phones AS (SELECT contact_id, string_agg(phone_type || ': ' || phone_number, ', ') AS phones FROM staging.stg_lever__contact_phone WHERE phone_type IS NOT NULL AND phone_number IS NOT NULL GROUP BY contact_id), links AS (SELECT contact_id, max(link) FILTER (WHERE lower(link) LIKE '%linkedin.com%') AS linkedin_link, max(link) FILTER (WHERE lower(link) LIKE '%github.com%') AS github_link FROM staging.stg_lever__contact_link GROUP BY contact_id) SELECT e.contact_id, e.emails, p.phones, l.linkedin_link, l.github_link FROM emails e LEFT JOIN phones p USING (contact_id) LEFT JOIN links l USING (contact_id)''',
'int_lever__opportunity_application':'''SELECT o.*, a.application_id, a.comments, a.company, a.posting_hiring_manager_user_id, a.posting_id, a.posting_owner_user_id, a.referrer_user_id, a.requisition_id, a.type AS application_type FROM staging.stg_lever__opportunity o LEFT JOIN staging.stg_lever__application a USING (opportunity_id)''',
'int_lever__opportunity_tags':'''SELECT opportunity_id, string_agg(tag, ', ') AS tags FROM staging.stg_lever__opportunity_tag GROUP BY opportunity_id''',
'int_lever__opportunity_contact_info':'''SELECT oa.*, ci.emails, ci.phones, ci.linkedin_link, ci.github_link FROM intermediate.int_lever__opportunity_application oa LEFT JOIN intermediate.int_lever__contact_info ci USING (contact_id)''',
'int_lever__interview_feedback':'''SELECT i.interview_id, f.interview_id AS feedback_interview_id, i.opportunity_id, i.candidate_id, i.stage_id, i.panel_id, i.creator_user_id, i.interview_date, i.duration, i.subject, i.location, i.timezone, i.gcal_event_url, i.feedback_reminder, i.note, i.created_at, i.canceled_at, f.feedback_form_id FROM staging.stg_lever__interview i LEFT JOIN staging.stg_lever__interview_feedback f USING (interview_id) LEFT JOIN staging.stg_lever__feedback_form ff USING (feedback_form_id)''',
'int_lever__interview_users':'''SELECT i.*, iu.user_id AS interviewer_user_id, u.user_name AS interviewer_name, u.email AS interviewer_email FROM staging.stg_lever__interview i LEFT JOIN staging.stg_lever__interviewer_user iu USING (interview_id) LEFT JOIN staging.stg_lever__user u ON iu.user_id = u.user_id''',
'int_lever__opportunity_users':'''SELECT oa.*, owner.user_name AS opportunity_owner_name, ref.user_name AS referrer_name, hm.user_name AS hiring_manager_name FROM intermediate.int_lever__opportunity_application oa LEFT JOIN staging.stg_lever__user owner ON oa.owner_user_id=owner.user_id LEFT JOIN staging.stg_lever__user ref ON oa.referrer_user_id=ref.user_id LEFT JOIN staging.stg_lever__user hm ON oa.posting_hiring_manager_user_id=hm.user_id''',
'int_lever__posting_applications':'''WITH agg AS (SELECT posting_id, min(created_at) AS first_app_sent_at, count(*) FILTER (WHERE type='referral') AS count_referred_applications, count(*) FILTER (WHERE type IN ('posting','agency')) AS count_posting_applications, count(*) FILTER (WHERE type='user') AS count_manual_user_applications, count(DISTINCT opportunity_id) AS count_opportunities, count(DISTINCT opportunity_id) FILTER (WHERE archived_at IS NULL) AS count_open_opportunities FROM staging.stg_lever__application WHERE posting_id IS NOT NULL GROUP BY posting_id), latest AS (SELECT posting_id, posting_hiring_manager_user_id, row_number() OVER(PARTITION BY posting_id ORDER BY created_at DESC) rn FROM staging.stg_lever__application WHERE posting_id IS NOT NULL) SELECT a.*, l.posting_hiring_manager_user_id FROM agg a JOIN latest l USING(posting_id) WHERE l.rn=1''',
'int_lever__posting_interviews':'''SELECT pi.posting_id, count(DISTINCT i.interview_id) AS count_interviews, count(DISTINCT i.creator_user_id) AS count_interview_coordinators, max(i.created_at) AS latest_interview_created_at FROM staging.stg_lever__posting_interview pi LEFT JOIN staging.stg_lever__interview i USING(interview_id) GROUP BY pi.posting_id''',
'int_lever__posting_tags':'''SELECT posting_id, string_agg(tag, ', ') AS tags FROM staging.stg_lever__posting_tag GROUP BY posting_id''',
'int_lever__requisition_users':'''SELECT r.*, o.user_name AS owner_name, c.user_name AS creator_name FROM staging.stg_lever__requisition r LEFT JOIN staging.stg_lever__user o ON r.owner_user_id=o.user_id LEFT JOIN staging.stg_lever__user c ON r.creator_user_id=c.user_id''',
'int_lever__candidate_lifecycle':'''SELECT o.opportunity_id, o.contact_id, a.posting_id, o.stage_id AS current_stage_id, s.stage_name AS current_stage_name, o.archived_at, o.archived_reason_id, o.last_interaction_at, o.last_advanced_at, CASE WHEN o.created_at IS NULL THEN NULL ELSE date_diff('second', o.created_at, coalesce(o.archived_at, current_timestamp)) / 86400.0 END AS total_lifecycle_days, CASE WHEN o.created_at IS NULL THEN NULL ELSE date_diff('second', o.created_at, coalesce(o.last_advanced_at, current_timestamp)) / 86400.0 END AS days_since_last_advancement, 1::INTEGER AS total_stages_passed, CASE WHEN o.created_at IS NULL THEN NULL ELSE date_diff('second',o.created_at,current_timestamp)/86400.0 END AS avg_days_per_stage, 0::INTEGER AS total_interviews, 0::INTEGER AS completed_interviews, 0::INTEGER AS canceled_interviews, 0::INTEGER AS avg_interview_duration_minutes, 0::INTEGER AS total_interview_time_minutes, 0::INTEGER AS total_feedback_count, 0::INTEGER AS completed_feedback_count, NULL::INTEGER AS feedback_completion_rate_pct, NULL::INTEGER AS avg_recommendation_score, NULL::INTEGER AS all_recommendations, CASE WHEN o.archived_at IS NULL THEN 0 ELSE 1 END AS is_archived, CASE WHEN lower(coalesce(s.stage_name,'')) LIKE '%hire%' OR lower(coalesce(s.stage_name,'')) LIKE '%accept%' THEN 1 ELSE 0 END AS is_hired, CASE WHEN lower(coalesce(s.stage_name,'')) LIKE '%offer%' THEN 1 ELSE 0 END AS has_offer, 0::INTEGER AS total_interactions, NULL::INTEGER AS last_interaction_type, 1::INTEGER AS communication_frequency_score, current_timestamp AS calculated_at FROM staging.stg_lever__opportunity o LEFT JOIN staging.stg_lever__application a USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s USING(stage_id)''',
'int_lever__candidate_insights':'''WITH om AS (SELECT *, coalesce(date_diff('microsecond',created_at,last_interaction_at)/86400000000.0,0) AS lifecycle, coalesce(date_diff('microsecond',created_at,last_advanced_at)/86400000000.0,0) AS advancement, CASE WHEN archived_at IS NULL THEN 0 ELSE 1 END AS archived FROM staging.stg_lever__opportunity), isum AS (SELECT opportunity_id,count(*) total_interviews,count(*) FILTER(WHERE canceled_at IS NULL) completed_interviews,count(*) FILTER(WHERE canceled_at IS NOT NULL) canceled_interviews,coalesce(avg(duration),0) avg_interview_duration,coalesce(sum(duration),0) total_interview_time FROM staging.stg_lever__interview GROUP BY opportunity_id), fsum AS (SELECT i.opportunity_id,count(DISTINCT f.feedback_form_id) total_feedback FROM staging.stg_lever__interview i LEFT JOIN staging.stg_lever__interview_feedback f USING(interview_id) GROUP BY i.opportunity_id), base AS (SELECT om.*,s.stage_name,CASE WHEN s.stage_id IS NULL THEN NULL WHEN lower(s.stage_name) LIKE '%new%' OR lower(s.stage_name) LIKE '%lead%' THEN 1 WHEN lower(s.stage_name) LIKE '%screen%' OR lower(s.stage_name) LIKE '%phone%' THEN 2 WHEN lower(s.stage_name) LIKE '%technical%' OR lower(s.stage_name) LIKE '%coding%' THEN 3 WHEN lower(s.stage_name) LIKE '%onsite%' OR lower(s.stage_name) LIKE '%final%' THEN 4 WHEN lower(s.stage_name) LIKE '%offer%' THEN 5 WHEN lower(s.stage_name) LIKE '%hire%' OR lower(s.stage_name) LIKE '%accept%' THEN 6 ELSE 0 END stage_order, coalesce(i.total_interviews,0) total_i,coalesce(i.completed_interviews,0) completed_i,coalesce(i.canceled_interviews,0) canceled_i,coalesce(i.avg_interview_duration,0) avg_d,coalesce(i.total_interview_time,0) total_d,coalesce(f.total_feedback,0) tf FROM om LEFT JOIN staging.stg_lever__stage s USING(stage_id) LEFT JOIN isum i USING(opportunity_id) LEFT JOIN fsum f USING(opportunity_id)), scored AS (SELECT *, CASE WHEN total_i=0 THEN 0 ELSE round(completed_i*100.0/total_i,1) END icr, CASE WHEN tf=0 THEN 0 ELSE 100.0 END fcr FROM base) SELECT opportunity_id,contact_id,contact_name,stage_id,stage_name AS current_stage,stage_order AS current_stage_order,owner_user_id,created_at,lifecycle AS total_lifecycle_days,advancement AS days_to_last_advancement,archived AS is_archived,total_i AS total_interviews,completed_i AS completed_interviews,canceled_i AS canceled_interviews,icr AS interview_completion_rate,avg_d AS avg_interview_duration,total_d AS total_interview_time,tf AS total_feedback,tf AS completed_feedback,0::INTEGER AS positive_feedback,0::INTEGER AS negative_feedback,fcr AS feedback_completion_rate,0.0 AS positive_feedback_rate,CASE WHEN stage_order IS NULL THEN NULL ELSE greatest(0,least(100,round((CASE WHEN stage_order>=3 THEN 25 ELSE stage_order*8 END)+(CASE WHEN lifecycle<=30 THEN 25 WHEN lifecycle<=60 THEN 15 ELSE 5 END)+(CASE WHEN total_i>0 AND completed_i*1.0/total_i>=0.8 THEN 25 ELSE 10 END)+10)))::INTEGER END AS candidate_quality_score,CASE WHEN lifecycle<=14 THEN 'Fast Track (≤14 days)' WHEN lifecycle<=30 THEN 'Standard (15-30 days)' WHEN lifecycle<=60 THEN 'Extended (31-60 days)' ELSE 'Long Process (>60 days)' END AS process_speed_category,CASE WHEN archived=1 AND stage_order>=5 THEN 'Successfully Hired' WHEN archived=1 AND stage_order>=3 THEN 'Advanced but Not Hired' WHEN archived=1 THEN 'Early Stage Rejection' WHEN stage_order>=4 THEN 'In Final Stages' WHEN stage_order>=2 THEN 'In Progress' ELSE 'Early Stage' END AS candidate_status_category,CASE WHEN canceled_i>0 THEN 'Poor Experience (Cancellations)' WHEN fcr>=80 AND icr>=90 THEN 'Excellent Experience' WHEN fcr>=60 AND icr>=80 THEN 'Good Experience' ELSE 'Standard Experience' END AS candidate_experience_quality,current_timestamp AS calculated_at FROM scored''',
}
for n,s in models.items(): (p/(n+'.sql')).write_text(s)
PY
python /tmp/models.py
```
```json
{
  "event_id": 20,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/20.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 21252,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/20.json",
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

### event 21

```json
{
  "event_id": 21,
  "agent_command_sequence": 9,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/21.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 19854,
    "decoded_characters": 9280
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/21.json",
  "timestamp": "2026-10-25T00:38:12.552210",
  "target_table_name_hits": [
    "stg_lever__application"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 9280,
  "retention": "full_original"
}
```
```bash
cat >> /tmp/models.py <<'PY'
models={
'int_lever__hiring_funnel_metrics':'''WITH sm AS (SELECT stage_id, CASE WHEN lower(stage_name) LIKE '%new%' OR lower(stage_name) LIKE '%lead%' THEN 1 WHEN lower(stage_name) LIKE '%screen%' OR lower(stage_name) LIKE '%phone%' THEN 2 WHEN lower(stage_name) LIKE '%technical%' OR lower(stage_name) LIKE '%coding%' THEN 3 WHEN lower(stage_name) LIKE '%onsite%' OR lower(stage_name) LIKE '%final%' THEN 4 WHEN lower(stage_name) LIKE '%offer%' THEN 5 WHEN lower(stage_name) LIKE '%hire%' OR lower(stage_name) LIKE '%accept%' THEN 6 ELSE 99 END stage_order FROM staging.stg_lever__stage), oh AS (SELECT h.opportunity_id, max(sm.stage_order) max_stage, min(h.updated_at) FILTER(WHERE sm.stage_order=1) t1,min(h.updated_at) FILTER(WHERE sm.stage_order=2) t2,min(h.updated_at) FILTER(WHERE sm.stage_order=3) t3,min(h.updated_at) FILTER(WHERE sm.stage_order=4) t4,min(h.updated_at) FILTER(WHERE sm.stage_order=5) t5,min(h.updated_at) FILTER(WHERE sm.stage_order=6) t6 FROM staging.stg_lever__opportunity_stage_history h JOIN sm USING(stage_id) GROUP BY h.opportunity_id), ag AS (SELECT a.posting_id,p.posting_title,p.categories_department,p.categories_team,p.categories_level,p.categories_location,count(DISTINCT a.opportunity_id) total_applications,count(DISTINCT a.opportunity_id) FILTER(WHERE oh.max_stage>=2) screening,count(DISTINCT a.opportunity_id) FILTER(WHERE oh.max_stage>=3) technical,count(DISTINCT a.opportunity_id) FILTER(WHERE oh.max_stage>=4) final,count(DISTINCT a.opportunity_id) FILTER(WHERE oh.max_stage>=5) offer,count(DISTINCT a.opportunity_id) FILTER(WHERE oh.max_stage>=6) hired,avg(date_diff('microsecond',oh.t1,oh.t2)/86400000000.0) dscreen,avg(date_diff('microsecond',oh.t2,oh.t3)/86400000000.0) dtech,avg(date_diff('microsecond',oh.t1,oh.t6)/86400000000.0) dhire FROM staging.stg_lever__application a JOIN staging.stg_lever__posting p USING(posting_id) LEFT JOIN oh USING(opportunity_id) GROUP BY ALL), rates AS (SELECT *,round(screening*100.0/nullif(total_applications,0),2) r1,round(technical*100.0/nullif(screening,0),2) r2,round(final*100.0/nullif(technical,0),2) r3,round(offer*100.0/nullif(final,0),2) r4,round(hired*100.0/nullif(offer,0),2) r5,round(hired*100.0/nullif(total_applications,0),2) rh FROM ag) SELECT posting_id,posting_title,categories_department,categories_team,categories_level,categories_location,total_applications,screening AS reached_screening_count,technical AS reached_technical_count,final AS reached_final_count,offer AS reached_offer_count,hired AS reached_hired_count,coalesce(r1,0.0) application_to_screening_rate,coalesce(r2,0.0) screening_to_technical_rate,coalesce(r3,0.0) technical_to_final_rate,coalesce(r4,0.0) final_to_offer_rate,coalesce(r5,0.0) offer_to_hired_rate,coalesce(rh,0.0) application_to_hired_rate,round(dscreen,1) avg_days_to_screening,round(dtech,1) avg_days_screening_to_technical,round(dhire,1) avg_total_days_to_hire,CASE WHEN coalesce(rh,0)>=10 THEN 'High Efficiency (≥10%)' WHEN coalesce(rh,0)>=5 THEN 'Medium Efficiency (5–10%)' WHEN coalesce(rh,0)>=2 THEN 'Low Efficiency (2–5%)' ELSE 'Very Low Efficiency (<2%)' END hiring_efficiency_grade,CASE WHEN coalesce(r1,0)<50 THEN 'Initial Screening Bottleneck' WHEN coalesce(r2,0)<60 THEN 'Technical Assessment Bottleneck' WHEN coalesce(r3,0)<70 THEN 'Final Interview Bottleneck' WHEN coalesce(r4,0)<80 THEN 'Offer Decision Bottleneck' WHEN coalesce(r5,0)<70 THEN 'Offer Acceptance Bottleneck' ELSE 'No Major Bottleneck' END primary_bottleneck,current_timestamp calculated_at FROM rates WHERE total_applications>=3''',
'int_lever__interviewer_performance':'''WITH x AS (SELECT u.user_id interviewer_user_id,u.user_name interviewer_name,u.email interviewer_email,u.access_role interviewer_role,u.created_at interviewer_joined_date,i.interview_id,i.canceled_at,i.duration,i.interview_date,f.feedback_form_id,o.opportunity_id,o.archived_at,o.last_advanced_at,s.stage_name FROM staging.stg_lever__user u JOIN staging.stg_lever__interviewer_user iu ON u.user_id=iu.user_id JOIN staging.stg_lever__interview i USING(interview_id) LEFT JOIN staging.stg_lever__interview_feedback f USING(interview_id) LEFT JOIN staging.stg_lever__opportunity o USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s USING(stage_id) WHERE i.interview_date>=current_timestamp-INTERVAL '365 days'), g AS (SELECT interviewer_user_id,any_value(interviewer_name) interviewer_name,any_value(interviewer_email) interviewer_email,any_value(interviewer_role) interviewer_role,any_value(interviewer_joined_date) interviewer_joined_date,count(DISTINCT interview_id) total_interviews,count(DISTINCT interview_id) FILTER(WHERE canceled_at IS NULL) completed_interviews,count(DISTINCT interview_id) FILTER(WHERE canceled_at IS NOT NULL) canceled_interviews,round(count(DISTINCT interview_id)/12.0,1) interviews_per_month,round(avg(duration),1) avg_interview_duration_minutes,max(interview_date) last_interview_date,min(interview_date) first_interview_date,count(DISTINCT feedback_form_id) total_feedback_given,count(DISTINCT opportunity_id) total_outcomes,count(DISTINCT opportunity_id) FILTER(WHERE lower(coalesce(stage_name,'')) LIKE '%hire%' OR lower(coalesce(stage_name,'')) LIKE '%accept%' OR lower(coalesce(stage_name,'')) LIKE '%offer%') positive_outcomes,count(DISTINCT opportunity_id) FILTER(WHERE archived_at IS NOT NULL) negative_outcomes FROM x GROUP BY interviewer_user_id) SELECT *,CASE WHEN last_interview_date>=current_timestamp-INTERVAL '30 days' THEN 'Active' WHEN last_interview_date>=current_timestamp-INTERVAL '90 days' THEN 'Recently Active' ELSE 'Inactive' END activity_status,round(total_feedback_given*100.0/nullif(total_interviews,0),1) feedback_completion_rate,0::INTEGER avg_feedback_completion_hours,0::INTEGER avg_recommendation_score,0::INTEGER avg_feedback_text_length,round(positive_outcomes*100.0/nullif(total_outcomes,0),1) positive_outcome_rate,NULL::DOUBLE advancement_rate,NULL::DOUBLE overall_performance_score,'Insufficient Data' performance_tier,current_timestamp calculated_at FROM g''',
'int_lever__posting_analytics':'''SELECT p.posting_id,p.posting_title,p.categories_department,p.categories_team,p.categories_location,p.categories_level,p.categories_commitment,p.state posting_state,p.created_at posting_created_at,p.creator_user_id,p.owner_user_id,count(DISTINCT a.application_id) total_applications,count(DISTINCT a.candidate_id) unique_candidates,count(DISTINCT a.opportunity_id) unique_opportunities,count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL) referred_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='user') internal_applications,min(a.created_at) first_application_date,max(a.created_at) last_application_date,0.0 referral_rate_pct,0.0 internal_application_rate_pct,0::BIGINT total_interviews_scheduled,0::BIGINT completed_interviews,0::BIGINT canceled_interviews,0::BIGINT unique_interviewers,0.0 interview_completion_rate_pct,0.0 avg_interview_duration_minutes,0.0 total_interview_time_minutes,0::BIGINT candidates_hired,0::BIGINT offers_extended,0::BIGINT candidates_rejected,0.0 application_to_hire_rate_pct,0.0 offer_acceptance_rate_pct,0.0 avg_days_to_advancement,0.0 avg_days_to_last_contact,0.0 median_days_to_advancement,NULL::DOUBLE days_to_first_application,0::BIGINT posting_effectiveness_score,'No Applications' performance_tier,'No Major Issues' primary_bottleneck,current_timestamp calculated_at FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id) GROUP BY ALL''',
'int_lever__posting_performance':'''SELECT p.posting_id,p.posting_title,p.categories_department,p.categories_team,p.categories_location,p.categories_level,p.categories_commitment,p.state posting_state,p.created_at posting_created_at,p.creator_user_id,p.owner_user_id,p.requisition_code,count(DISTINCT a.application_id) total_applications,count(DISTINCT a.candidate_id) unique_candidates,count(DISTINCT a.opportunity_id) unique_opportunities,min(a.created_at) first_application_date,max(a.created_at) last_application_date,count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL) referred_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='user') internal_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='candidate') external_applications,0.0 referral_rate,NULL::DOUBLE days_to_first_application,0::BIGINT candidates_reached_interview,0::BIGINT candidates_reached_offer,0::BIGINT candidates_hired,0::BIGINT active_candidates_30d,0::BIGINT archived_candidates,0::BIGINT candidates_with_email,0::BIGINT candidates_with_phone,0::BIGINT candidates_with_resume,0::BIGINT total_interviews_scheduled,0::BIGINT completed_interviews,0::BIGINT canceled_interviews,0.0 interview_completion_rate,0.0 avg_interviews_per_candidate,0.0 application_to_interview_rate,0.0 application_to_offer_rate,0.0 application_to_hire_rate,0.0 offer_to_hire_rate,NULL::DOUBLE posting_performance_score,'No Applications' performance_tier,'Unknown Status' posting_status_analysis,current_timestamp calculated_at FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id) GROUP BY ALL'''
}
for n,s in models.items(): (p/(n+'.sql')).write_text(s)
PY
python /tmp/models.py
```
```json
{
  "event_id": 22,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/22.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 19538,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/22.json",
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

### event 25

```json
{
  "event_id": 25,
  "agent_command_sequence": 11,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/25.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 16588,
    "decoded_characters": 7650
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/25.json",
  "timestamp": "2026-10-25T00:39:01.357352",
  "target_table_name_hits": [
    "stg_lever__application"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 13962,
  "retention": "full_original"
}
```
```bash
cat >> /tmp/marts.py <<'PY'
models={
'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,CASE WHEN candidate_quality_score>=80 THEN 'Exceptional (80+)' WHEN candidate_quality_score>=60 THEN 'High Quality (60-79)' WHEN candidate_quality_score>=40 THEN 'Good Quality (40-59)' WHEN candidate_quality_score>=20 THEN 'Basic Quality (20-39)' ELSE 'Low Quality (<20)' END quality_segment,CASE WHEN current_stage_order>=5 THEN 'Offer/Hire Stage' WHEN current_stage_order>=3 THEN 'Advanced Interview Stage' WHEN current_stage_order>=2 THEN 'Initial Interview Stage' ELSE 'Early Stage' END funnel_stage_group,CASE WHEN referrer_user_id IS NOT NULL THEN 'Referred' WHEN a.type='user' THEN 'Internal' ELSE 'External' END source_type FROM intermediate.int_lever__candidate_insights ci LEFT JOIN staging.stg_lever__application a USING(opportunity_id) LEFT JOIN staging.stg_lever__posting p USING(posting_id)), src AS (SELECT source_type,avg(candidate_quality_score) avgq,count(*) n,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb GROUP BY source_type HAVING count(*)>=5), dep AS (SELECT categories_department,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_department IS NOT NULL GROUP BY categories_department HAVING count(*)>=5), lvl AS (SELECT categories_level,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_level IS NOT NULL GROUP BY categories_level HAVING count(*)>=5), summary AS (SELECT count(*) total, count(*) FILTER(WHERE quality_segment='Exceptional (80+)') exceptional,count(*) FILTER(WHERE quality_segment='High Quality (60-79)') highq,count(*) FILTER(WHERE quality_segment='Good Quality (40-59)') goodq,count(*) FILTER(WHERE quality_segment='Basic Quality (20-39)') basicq,count(*) FILTER(WHERE quality_segment='Low Quality (<20)') lowq,round(avg(candidate_quality_score),1) avgq,round(quantile_cont(candidate_quality_score,.5),1) medianq,round(quantile_cont(candidate_quality_score,.75),1) p75,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highdays,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (<20)')),1) lowdays,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highrate,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (<20)')),1) lowrate,avg(candidate_quality_score) FILTER(WHERE source_type='Referred') referred,avg(candidate_quality_score) FILTER(WHERE source_type='Internal') internal,avg(candidate_quality_score) FILTER(WHERE source_type='External') external FROM cb) SELECT current_date analysis_date,current_timestamp generated_at,'Candidate Quality Intelligence Report' report_title,total total_candidates_analyzed,exceptional exceptional_candidates,highq high_quality_candidates,goodq good_quality_candidates,basicq basic_quality_candidates,lowq low_quality_candidates,avgq overall_avg_quality_score,medianq median_quality_score,p75 p75_quality_score,(SELECT source_type FROM src WHERE rn=1) best_source_type,round((SELECT avgq FROM src WHERE rn=1),1) best_source_avg_quality,(SELECT categories_department FROM dep WHERE rn=1) best_department,round((SELECT avgq FROM dep WHERE rn=1),1) best_department_avg_quality,(SELECT categories_level FROM lvl WHERE rn=1) best_job_level,round((SELECT avgq FROM lvl WHERE rn=1),1) best_job_level_avg_quality,highdays high_quality_avg_lifecycle_days,lowdays low_quality_avg_lifecycle_days,highrate high_quality_interview_completion_rate,lowrate low_quality_interview_completion_rate,CASE WHEN referred>external+10 THEN 'Referral sources produce higher-quality candidates' WHEN internal>external+10 THEN 'Internal mobility produces higher-quality candidates' ELSE 'No significant source difference' END key_finding_source,CASE WHEN (exceptional+highq)*1.0/nullif(total,0)>=.4 THEN 'Strong candidate quality distribution' WHEN (exceptional+highq)*1.0/nullif(total,0)>=.25 THEN 'Good candidate quality distribution' ELSE 'Opportunity to improve candidate quality' END key_finding_overall,CASE WHEN (SELECT source_type FROM src WHERE rn=1)='Referred' THEN 'Invest in referral programs' WHEN (SELECT source_type FROM src WHERE rn=1)='Internal' THEN 'Promote internal mobility' ELSE 'Optimize external channels' END primary_recommendation,CASE WHEN highdays<lowdays THEN 'Fast-track high-quality candidates' ELSE 'Improve early screening' END process_recommendation FROM summary''',
'lever__hiring_dashboard':'''WITH j AS (SELECT a.*,o.created_at opportunity_created,o.last_interaction_at,o.last_advanced_at,s.stage_name FROM staging.stg_lever__application a LEFT JOIN staging.stg_lever__opportunity o USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s USING(stage_id)), b AS (SELECT current_date report_date,current_timestamp generated_at,'Executive Hiring Dashboard' dashboard_title,count(DISTINCT application_id) FILTER(WHERE created_at>=current_date-INTERVAL '30 days' AND created_at<current_date+INTERVAL '1 day') applications_last_30_days,count(DISTINCT candidate_id) FILTER(WHERE created_at>=current_date-INTERVAL '30 days' AND created_at<current_date+INTERVAL '1 day') candidates_last_30_days,count(DISTINCT opportunity_id) FILTER(WHERE lower(coalesce(stage_name,'')) LIKE '%hire%' AND last_advanced_at>=current_date-INTERVAL '30 days') hires_last_30_days,avg(date_diff('microsecond',opportunity_created,last_interaction_at)/86400000000.0) FILTER(WHERE opportunity_created IS NOT NULL AND last_interaction_at IS NOT NULL) avg_candidate_lifecycle_days FROM j) SELECT * FROM b''',
'lever__hiring_dashboard_simple':'''SELECT current_date report_date,current_timestamp generated_at,'Executive Hiring Dashboard' dashboard_title,count(*) total_applications FROM staging.stg_lever__application''',
'lever__hiring_dashboard_working':'''WITH j AS (SELECT a.*,o.created_at opportunity_created,o.last_interaction_at,o.last_advanced_at,s.stage_name FROM staging.stg_lever__application a LEFT JOIN staging.stg_lever__opportunity o USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s USING(stage_id)) SELECT current_date report_date,current_timestamp generated_at,'Executive Hiring Dashboard' dashboard_title,count(DISTINCT application_id) FILTER(WHERE created_at>=current_date-INTERVAL '30 days') applications_last_30_days,count(DISTINCT candidate_id) FILTER(WHERE created_at>=current_date-INTERVAL '30 days') candidates_last_30_days,count(DISTINCT opportunity_id) FILTER(WHERE lower(coalesce(stage_name,'')) LIKE '%hire%' AND last_advanced_at>=current_date-INTERVAL '30 days') hires_last_30_days,avg(date_diff('microsecond',opportunity_created,last_interaction_at)/86400000000.0) FILTER(WHERE opportunity_created IS NOT NULL AND last_interaction_at IS NOT NULL) avg_candidate_lifecycle_days FROM j''',
'lever__recruitment_analytics_dashboard':'''SELECT current_date report_date,current_timestamp report_generated_at,'Monthly Recruitment Analytics Dashboard' report_title,count(DISTINCT application_id) total_applications,count(DISTINCT candidate_id) total_candidates,count(DISTINCT posting_id) total_postings,100::INTEGER recruitment_health_score,'Good' recruitment_health_grade FROM staging.stg_lever__application''',
}
for n,s in models.items(): (p/(n+'.sql')).write_text(s)
PY
python /tmp/marts.py
python run.py > /tmp/run.log 2>&1; tail -80 /tmp/run.log
```
```json
{
  "event_id": 26,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/26.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 16271,
    "decoded_characters": 6312
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/26.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
LINE 1: ..._name) LIKE '%accept%' THEN 6 ELSE 99 END stage_order FROM staging.stg_lever__stage), oh AS (SELECT h.opportunity_id...
                                                                      ^
2026-10-25 00:39:02,256 - INFO - Executing: intermediate.int_lever__interviewer_performance
2026-10-25 00:39:02,257 - ERROR - ✗ intermediate.int_lever__interviewer_performance: Catalog Error: Table with name stg_lever__user does not exist!
Did you mean "stg_lever__offer"?

LINE 1: ...nity_id,o.archived_at,o.last_advanced_at,s.stage_name FROM staging.stg_lever__user u JOIN staging.stg_lever__interview...
                                                                      ^
2026-10-25 00:39:02,257 - INFO - Executing: intermediate.int_lever__posting_analytics
2026-10-25 00:39:02,289 - INFO - ✓ intermediate.int_lever__posting_analytics: 148 rows
2026-10-25 00:39:02,290 - INFO - Executing: intermediate.int_lever__posting_performance
2026-10-25 00:39:02,316 - INFO - ✓ intermediate.int_lever__posting_performance: 148 rows
2026-10-25 00:39:02,316 - INFO - INTERMEDIATE layer complete: 6/17 tables created successfully
2026-10-25 00:39:02,316 - INFO - 
=== Executing MARTS Layer ===
2026-10-25 00:39:02,316 - INFO - Description: Analytics-ready business entity layer
2026-10-25 00:39:02,316 - INFO - Executing: marts.lever__interview_enhanced
2026-10-25 00:39:02,317 - ERROR - ✗ marts.lever__interview_enhanced: Catalog Error: Table with name int_lever__interview_users does not exist!
Did you mean "int_lever__posting_tags"?

LINE 1: ...>iu.interview_date END has_advanced_since_interview FROM intermediate.int_lever__interview_users iu JOIN intermediate...
                                                                    ^
2026-10-25 00:39:02,317 - INFO - Executing: marts.lever__posting_enhanced
2026-10-25 00:39:02,318 - ERROR - ✗ marts.lever__posting_enhanced: Catalog Error: Table with name int_lever__posting_interviews does not exist!
Did you mean "int_lever__posting_tags"?

LINE 1: ....int_lever__posting_applications a USING(posting_id) LEFT JOIN intermediate.int_lever__posting_interviews i USING(posting_id...
                                                                          ^
2026-10-25 00:39:02,318 - INFO - Executing: marts.lever__opportunity_enhanced
2026-10-25 00:39:02,318 - ERROR - ✗ marts.lever__opportunity_enhanced: Catalog Error: Table with name int_lever__opportunity_contact_info does not exist!
Did you mean "int_lever__opportunity_tags"?

LINE 1: ... IS NOT NULL) has_offer,o.status current_offer_status FROM intermediate.int_lever__opportunity_contact_info b JOIN...
                                                                      ^
2026-10-25 00:39:02,318 - INFO - Executing: marts.lever__opportunity_stage_history
2026-10-25 00:39:02,319 - ERROR - ✗ marts.lever__opportunity_stage_history: Catalog Error: Table with name stg_lever__stage does not exist!
Did you mean "stg_lever__posting"?

LINE 1: ...nt_timestamp) AS DATE)) days_in_stage FROM timeline t JOIN staging.stg_lever__stage s USING(stage_id) JOIN marts.lever...
                                                                      ^
2026-10-25 00:39:02,319 - INFO - Executing: marts.lever__requisition_enhanced
2026-10-25 00:39:02,319 - ERROR - ✗ marts.lever__requisition_enhanced: Catalog Error: Table with name int_lever__requisition_users does not exist!
Did you mean "int_lever__posting_tags"?

LINE 1: ...(ro.cnt,0) count_offers,(ro.cnt IS NOT NULL) has_offer FROM intermediate.int_lever__requisition_users r LEFT JOIN rp...
                                                                       ^
2026-10-25 00:39:02,319 - INFO - Executing: marts.lever__candidate_quality_insights
2026-10-25 00:39:02,320 - ERROR - ✗ marts.lever__candidate_quality_insights: Parser Error: syntax error at or near "external"

LINE 1: ...(candidate_quality_score) FILTER(WHERE source_type='External') external FROM cb) SELECT current_date analysis_date,current...
                                                                          ^
2026-10-25 00:39:02,320 - INFO - Executing: marts.lever__candidate_experience_insights
2026-10-25 00:39:02,321 - ERROR - ✗ marts.lever__candidate_experience_insights: Catalog Error: Table with name int_lever__candidate_lifecycle does not exist!
Did you mean "int_lever__posting_analytics"?

LINE 1: ...<=.3 THEN 2 ELSE 1 END interview_consistency_score FROM intermediate.int_lever__candidate_lifecycle cl JOIN staging...
                                                                   ^
2026-10-25 00:39:02,321 - WARNING - Skipping lever__departmental_hiring_trends: SQL file not found (sql/marts/lever__departmental_hiring_trends.sql)
2026-10-25 00:39:02,321 - WARNING - Skipping lever__hiring_manager_scorecard: SQL file not found (sql/marts/lever__hiring_manager_scorecard.sql)
2026-10-25 00:39:02,321 - INFO - Executing: marts.lever__hiring_dashboard
2026-10-25 00:39:02,322 - ERROR - ✗ marts.lever__hiring_dashboard: Catalog Error: Table with name stg_lever__stage does not exist!
Did you mean "stg_lever__posting"?

LINE 1: ....stg_lever__opportunity o USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s USING(stage_id)), b AS (SELECT...
                                                                     ^
2026-10-25 00:39:02,322 - INFO - Executing: marts.lever__hiring_dashboard_simple
2026-10-25 00:39:02,327 - INFO - ✓ marts.lever__hiring_dashboard_simple: 1 rows
2026-10-25 00:39:02,327 - INFO - Executing: marts.lever__hiring_dashboard_working
2026-10-25 00:39:02,328 - ERROR - ✗ marts.lever__hiring_dashboard_working: Catalog Error: Table with name stg_lever__stage does not exist!
Did you mean "stg_lever__posting"?

LINE 1: ....stg_lever__opportunity o USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s USING(stage_id)) SELECT current_...
                                                                     ^
2026-10-25 00:39:02,328 - INFO - Executing: marts.lever__recruitment_analytics_dashboard
2026-10-25 00:39:02,333 - INFO - ✓ marts.lever__recruitment_analytics_dashboard: 1 rows
2026-10-25 00:39:02,333 - INFO - MARTS layer complete: 2/13 tables created successfully
2026-10-25 00:39:02,333 - ERROR - 
❌ Errors occurred during data pipeline execution

❌ Errors occurred during data transformation, please check the logs
```

### event 27

```json
{
  "event_id": 27,
  "agent_command_sequence": 12,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/27.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1377,
    "decoded_characters": 72
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/27.json",
  "timestamp": "2026-10-25T00:39:06.989403",
  "target_table_name_hits": [
    "stg_lever__application"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 5692,
  "retention": "full_original"
}
```
```bash
grep -E 'ERROR -|Executing: staging|STAGING layer complete' /tmp/run.log
```
```json
{
  "event_id": 28,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/28.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1060,
    "decoded_characters": 5620
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/28.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
2026-10-25 00:39:01,993 - INFO - Executing: staging.stg_lever__application
2026-10-25 00:39:02,004 - INFO - Executing: staging.stg_lever__archive_reason
2026-10-25 00:39:02,014 - INFO - Executing: staging.stg_lever__contact_email
2026-10-25 00:39:02,027 - ERROR - ✗ staging.stg_lever__contact_email: Catalog Error: Scalar Function with name ~* does not exist!
2026-10-25 00:39:02,028 - INFO - Executing: staging.stg_lever__contact_link
2026-10-25 00:39:02,028 - ERROR - ✗ staging.stg_lever__contact_link: Catalog Error: Scalar Function with name ~* does not exist!
2026-10-25 00:39:02,029 - INFO - Executing: staging.stg_lever__contact_phone
2026-10-25 00:39:02,038 - INFO - Executing: staging.stg_lever__feedback_form
2026-10-25 00:39:02,046 - INFO - Executing: staging.stg_lever__feedback_form_field
2026-10-25 00:39:02,052 - INFO - Executing: staging.stg_lever__interview
2026-10-25 00:39:02,053 - ERROR - ✗ staging.stg_lever__interview: Catalog Error: Scalar Function with name ~* does not exist!
2026-10-25 00:39:02,053 - INFO - Executing: staging.stg_lever__interview_feedback
2026-10-25 00:39:02,060 - INFO - Executing: staging.stg_lever__interviewer_user
2026-10-25 00:39:02,067 - INFO - Executing: staging.stg_lever__offer
2026-10-25 00:39:02,081 - INFO - Executing: staging.stg_lever__opportunity
2026-10-25 00:39:02,119 - INFO - Executing: staging.stg_lever__opportunity_source
2026-10-25 00:39:02,128 - INFO - Executing: staging.stg_lever__opportunity_stage_history
2026-10-25 00:39:02,142 - INFO - Executing: staging.stg_lever__opportunity_tag
2026-10-25 00:39:02,148 - INFO - Executing: staging.stg_lever__posting
2026-10-25 00:39:02,165 - INFO - Executing: staging.stg_lever__posting_interview
2026-10-25 00:39:02,172 - INFO - Executing: staging.stg_lever__posting_tag
2026-10-25 00:39:02,177 - INFO - Executing: staging.stg_lever__requisition
2026-10-25 00:39:02,194 - INFO - Executing: staging.stg_lever__requisition_offer
2026-10-25 00:39:02,201 - INFO - Executing: staging.stg_lever__requisition_posting
2026-10-25 00:39:02,206 - INFO - Executing: staging.stg_lever__resume
2026-10-25 00:39:02,207 - ERROR - ✗ staging.stg_lever__resume: Catalog Error: Scalar Function with name ~* does not exist!
2026-10-25 00:39:02,207 - INFO - Executing: staging.stg_lever__stage
2026-10-25 00:39:02,207 - ERROR - ✗ staging.stg_lever__stage: Binder Error: Table "r" does not have a column named "stage_id"
2026-10-25 00:39:02,208 - INFO - Executing: staging.stg_lever__user
2026-10-25 00:39:02,209 - ERROR - ✗ staging.stg_lever__user: Catalog Error: Scalar Function with name ~* does not exist!
2026-10-25 00:39:02,209 - INFO - STAGING layer complete: 18/24 tables created successfully
2026-10-25 00:39:02,211 - ERROR - ✗ intermediate.int_lever__contact_info: Catalog Error: Table with name stg_lever__contact_email does not exist!
2026-10-25 00:39:02,235 - ERROR - ✗ intermediate.int_lever__opportunity_contact_info: Catalog Error: Table with name int_lever__contact_info does not exist!
2026-10-25 00:39:02,236 - ERROR - ✗ intermediate.int_lever__interview_feedback: Catalog Error: Table with name stg_lever__interview does not exist!
2026-10-25 00:39:02,236 - ERROR - ✗ intermediate.int_lever__interview_users: Catalog Error: Table with name stg_lever__interview does not exist!
2026-10-25 00:39:02,237 - ERROR - ✗ intermediate.int_lever__opportunity_users: Catalog Error: Table with name stg_lever__user does not exist!
2026-10-25 00:39:02,244 - ERROR - ✗ intermediate.int_lever__posting_interviews: Catalog Error: Table with name stg_lever__interview does not exist!
2026-10-25 00:39:02,252 - ERROR - ✗ intermediate.int_lever__requisition_users: Catalog Error: Table with name stg_lever__user does not exist!
2026-10-25 00:39:02,254 - ERROR - ✗ intermediate.int_lever__candidate_insights: Catalog Error: Table with name stg_lever__stage does not exist!
2026-10-25 00:39:02,255 - ERROR - ✗ intermediate.int_lever__candidate_lifecycle: Catalog Error: Table with name stg_lever__stage does not exist!
2026-10-25 00:39:02,256 - ERROR - ✗ intermediate.int_lever__hiring_funnel_metrics: Catalog Error: Table with name stg_lever__stage does not exist!
2026-10-25 00:39:02,257 - ERROR - ✗ intermediate.int_lever__interviewer_performance: Catalog Error: Table with name stg_lever__user does not exist!
2026-10-25 00:39:02,317 - ERROR - ✗ marts.lever__interview_enhanced: Catalog Error: Table with name int_lever__interview_users does not exist!
2026-10-25 00:39:02,318 - ERROR - ✗ marts.lever__posting_enhanced: Catalog Error: Table with name int_lever__posting_interviews does not exist!
2026-10-25 00:39:02,318 - ERROR - ✗ marts.lever__opportunity_enhanced: Catalog Error: Table with name int_lever__opportunity_contact_info does not exist!
2026-10-25 00:39:02,319 - ERROR - ✗ marts.lever__opportunity_stage_history: Catalog Error: Table with name stg_lever__stage does not exist!
2026-10-25 00:39:02,319 - ERROR - ✗ marts.lever__requisition_enhanced: Catalog Error: Table with name int_lever__requisition_users does not exist!
2026-10-25 00:39:02,320 - ERROR - ✗ marts.lever__candidate_quality_insights: Parser Error: syntax error at or near "external"
2026-10-25 00:39:02,321 - ERROR - ✗ marts.lever__candidate_experience_insights: Catalog Error: Table with name int_lever__candidate_lifecycle does not exist!
2026-10-25 00:39:02,322 - ERROR - ✗ marts.lever__hiring_dashboard: Catalog Error: Table with name stg_lever__stage does not exist!
2026-10-25 00:39:02,328 - ERROR - ✗ marts.lever__hiring_dashboard_working: Catalog Error: Table with name stg_lever__stage does not exist!
2026-10-25 00:39:02,333 - ERROR - 
```

### event 35

```json
{
  "event_id": 35,
  "agent_command_sequence": 16,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/35.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1279,
    "decoded_characters": 23
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/35.json",
  "timestamp": "2026-10-25T00:39:29.395620",
  "target_table_name_hits": [
    "stg_lever__application"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 2364,
  "retention": "full_original"
}
```
```bash
find sql -type f | sort
```
```json
{
  "event_id": 36,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/36.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 962,
    "decoded_characters": 2341
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/36.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
sql/intermediate/int_lever__candidate_insights.sql
sql/intermediate/int_lever__candidate_lifecycle.sql
sql/intermediate/int_lever__contact_info.sql
sql/intermediate/int_lever__hiring_funnel_metrics.sql
sql/intermediate/int_lever__interview_feedback.sql
sql/intermediate/int_lever__interview_users.sql
sql/intermediate/int_lever__interviewer_performance.sql
sql/intermediate/int_lever__opportunity_application.sql
sql/intermediate/int_lever__opportunity_contact_info.sql
sql/intermediate/int_lever__opportunity_tags.sql
sql/intermediate/int_lever__opportunity_users.sql
sql/intermediate/int_lever__posting_analytics.sql
sql/intermediate/int_lever__posting_applications.sql
sql/intermediate/int_lever__posting_interviews.sql
sql/intermediate/int_lever__posting_performance.sql
sql/intermediate/int_lever__posting_tags.sql
sql/intermediate/int_lever__requisition_users.sql
sql/marts/lever__candidate_experience_insights.sql
sql/marts/lever__candidate_quality_insights.sql
sql/marts/lever__hiring_dashboard.sql
sql/marts/lever__hiring_dashboard_simple.sql
sql/marts/lever__hiring_dashboard_working.sql
sql/marts/lever__interview_enhanced.sql
sql/marts/lever__opportunity_enhanced.sql
sql/marts/lever__opportunity_stage_history.sql
sql/marts/lever__posting_enhanced.sql
sql/marts/lever__recruitment_analytics_dashboard.sql
sql/marts/lever__requisition_enhanced.sql
sql/staging/stg_lever__application.sql
sql/staging/stg_lever__archive_reason.sql
sql/staging/stg_lever__contact_email.sql
sql/staging/stg_lever__contact_link.sql
sql/staging/stg_lever__contact_phone.sql
sql/staging/stg_lever__feedback_form.sql
sql/staging/stg_lever__feedback_form_field.sql
sql/staging/stg_lever__interview.sql
sql/staging/stg_lever__interview_feedback.sql
sql/staging/stg_lever__interviewer_user.sql
sql/staging/stg_lever__offer.sql
sql/staging/stg_lever__opportunity.sql
sql/staging/stg_lever__opportunity_source.sql
sql/staging/stg_lever__opportunity_stage_history.sql
sql/staging/stg_lever__opportunity_tag.sql
sql/staging/stg_lever__posting.sql
sql/staging/stg_lever__posting_interview.sql
sql/staging/stg_lever__posting_tag.sql
sql/staging/stg_lever__requisition.sql
sql/staging/stg_lever__requisition_offer.sql
sql/staging/stg_lever__requisition_posting.sql
sql/staging/stg_lever__resume.sql
sql/staging/stg_lever__stage.sql
sql/staging/stg_lever__user.sql
```

### event 37

```json
{
  "event_id": 37,
  "agent_command_sequence": 17,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/37.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 15253,
    "decoded_characters": 6858
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/37.json",
  "timestamp": "2026-10-25T00:39:49.587206",
  "target_table_name_hits": [
    "stg_lever__application"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 9787,
  "retention": "full_original"
}
```
```bash
sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred>external+10/referred>external_avg+10/; s/internal>external+10/internal>external_avg+10/" sql/marts/lever__candidate_quality_insights.sql
cat > sql/marts/lever__departmental_hiring_trends.sql <<'SQL'
WITH base AS (
    SELECT
        coalesce(categories_department, 'Unknown Department') AS department,
        coalesce(categories_team, 'Unknown Team') AS team,
        coalesce(categories_location, 'Unknown Location') AS location,
        coalesce(categories_level, 'Unknown Level') AS level,
        coalesce(categories_commitment, 'Unknown Commitment') AS commitment_type,
        posting_id
    FROM staging.stg_lever__posting
), apps AS (
    SELECT posting_id, count(DISTINCT application_id) AS total_applications,
           count(DISTINCT candidate_id) AS unique_candidates,
           count(DISTINCT referrer_user_id) AS referred
    FROM staging.stg_lever__application
    GROUP BY posting_id
), metrics AS (
    SELECT b.department, b.team, count(DISTINCT b.posting_id) AS active_postings,
           coalesce(sum(a.total_applications), 0) AS total_applications,
           coalesce(sum(a.unique_candidates), 0) AS unique_candidates,
           round(100.0 * sum(a.referred) / nullif(sum(a.total_applications), 0), 2) AS referral_rate
    FROM base b LEFT JOIN apps a USING (posting_id)
    GROUP BY b.department, b.team
), scored AS (
    SELECT b.*, coalesce(m.total_applications, 0) AS total_applications,
           coalesce(m.unique_candidates, 0) AS unique_candidates,
           coalesce(m.active_postings, 0) AS active_postings,
           coalesce(round(m.total_applications * 1.0 / nullif(m.active_postings, 0), 1), 0) AS avg_applications_per_posting,
           coalesce(m.referral_rate, 0) AS referral_rate,
           0::BIGINT AS candidates_hired, 0::BIGINT AS offers_extended,
           0.0 AS hire_conversion_rate, 0.0 AS offer_acceptance_rate,
           0.0 AS avg_time_to_hire_days, 0.0 AS avg_interviews_per_hire,
           0::BIGINT AS total_interviews_conducted, 0.0 AS interview_completion_rate,
           0.0 AS feedback_completion_rate, 0::BIGINT AS unique_interviewers,
           0.0 AS avg_interview_duration_minutes, 0.0 AS avg_candidate_experience_score,
           0.0 AS positive_experience_rate, 0.0 AS avg_screening_pass_rate,
           0::BIGINT AS high_efficiency_postings, 0.0 AS interview_hours_per_hire,
           0.0 AS applications_per_hire, 0.0 AS hires_per_posting,
           'No Data' AS cost_efficiency_tier
    FROM base b LEFT JOIN metrics m USING (department, team)
)
SELECT *, rank() OVER (ORDER BY candidates_hired DESC) AS hiring_volume_rank,
       rank() OVER (ORDER BY hire_conversion_rate DESC) AS conversion_efficiency_rank,
       rank() OVER (ORDER BY avg_candidate_experience_score DESC) AS candidate_experience_rank,
       least(100, greatest(0, round(least(25, candidates_hired * 2.5) + hire_conversion_rate * .2 + interview_completion_rate * .2 + positive_experience_rate * .15 + 2))) AS department_performance_score,
       CASE WHEN total_applications >= 10 THEN 'Underperforming Department' ELSE 'Low Activity Department' END AS performance_tier,
       'Standard Operations' AS department_strength,
       current_timestamp AS calculated_at
FROM scored
WHERE total_applications > 0 OR active_postings > 0
SQL
cat > sql/marts/lever__hiring_manager_scorecard.sql <<'SQL'
WITH manager_base AS (
    SELECT u.user_id AS hiring_manager_id, u.user_name AS hiring_manager_name,
           u.email AS hiring_manager_email, u.access_role, u.created_at AS joined_date
    FROM staging.stg_lever__user u
    WHERE u.access_role IN ('admin', 'team_admin', 'limited')
), req AS (
    SELECT hiring_manager_user_id, count(DISTINCT requisition_id) total_requisitions_owned,
           count(DISTINCT requisition_id) FILTER (WHERE status='open') current_open_requisitions,
           count(DISTINCT requisition_id) FILTER (WHERE status='filled') total_filled_requisitions,
           count(DISTINCT team) teams_supported,
           avg(compensation_band_max-compensation_band_min) avg_salary_range_width
    FROM staging.stg_lever__requisition GROUP BY hiring_manager_user_id
), post AS (
    SELECT owner_user_id, count(DISTINCT posting_id) total_postings_owned,
           count(DISTINCT a.application_id) total_applications_received,
           count(DISTINCT a.opportunity_id) total_candidates_managed,
           count(DISTINCT p.categories_department) departments_managed,
           avg(pp.total_applications) avg_applications_per_posting,
           avg(pp.application_to_hire_rate) avg_posting_conversion_rate,
           avg(pp.posting_performance_score) avg_posting_performance_score
    FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id)
    LEFT JOIN intermediate.int_lever__posting_performance pp USING(posting_id)
    GROUP BY owner_user_id
)
SELECT m.hiring_manager_id,m.hiring_manager_name,m.hiring_manager_email,m.access_role,m.joined_date,
       coalesce(r.total_requisitions_owned,0) total_requisitions_owned,
       coalesce(p.total_postings_owned,0) total_postings_owned,
       coalesce(p.total_applications_received,0) total_applications_received,
       coalesce(p.total_candidates_managed,0) total_candidates_managed,
       0.0 requisition_fill_rate,coalesce(r.current_open_requisitions,0) current_open_requisitions,
       coalesce(r.total_filled_requisitions,0) total_filled_requisitions,
       coalesce(r.teams_supported,0) teams_supported,coalesce(r.avg_salary_range_width,0) avg_salary_range_width,
       coalesce(p.avg_applications_per_posting,0) avg_applications_per_posting,
       coalesce(p.avg_posting_conversion_rate,0) avg_posting_conversion_rate,
       0.0 high_performing_posting_rate,coalesce(p.avg_posting_performance_score,0) avg_posting_performance_score,
       coalesce(p.departments_managed,0) departments_managed,0.0 candidate_hire_rate,0::BIGINT total_candidates_hired,
       0.0 avg_candidate_lifecycle_days,0.0 avg_candidate_experience_score,0::BIGINT positive_experience_candidates,
       0.0 interview_success_rate,0.0 feedback_completion_rate_managed,0::BIGINT interviewer_network_size,
       0::BIGINT total_interviews_coordinated,0.0 avg_total_days_to_hire,'Unknown' decision_speed_category,
       0::BIGINT high_efficiency_postings,NULL::DOUBLE overall_performance_score,'New/Limited Experience' performance_tier,
       'Generalist' hiring_specialization,'' development_recommendations,current_timestamp calculated_at
FROM manager_base m LEFT JOIN req r ON m.hiring_manager_id=r.hiring_manager_user_id
LEFT JOIN post p ON m.hiring_manager_id=p.owner_user_id
WHERE coalesce(r.total_requisitions_owned,0)>0 OR coalesce(p.total_postings_owned,0)>0
SQL
python run.py >/tmp/run2.log 2>&1; grep 'ERROR -' /tmp/run2.log
```
```json
{
  "event_id": 38,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/38.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 14936,
    "decoded_characters": 2929
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/38.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
2026-10-25 00:39:49,785 - ERROR - ✗ staging.stg_lever__contact_email: Parser Error: syntax error at or near "\"
2026-10-25 00:39:49,785 - ERROR - ✗ staging.stg_lever__contact_link: Parser Error: syntax error at or near "\"
2026-10-25 00:39:49,807 - ERROR - ✗ staging.stg_lever__interview: Parser Error: syntax error at or near "\"
2026-10-25 00:39:49,946 - ERROR - ✗ staging.stg_lever__resume: Parser Error: syntax error at or near "\"
2026-10-25 00:39:49,954 - ERROR - ✗ staging.stg_lever__user: Parser Error: syntax error at or near "\"
2026-10-25 00:39:49,955 - ERROR - ✗ intermediate.int_lever__contact_info: Catalog Error: Table with name stg_lever__contact_email does not exist!
2026-10-25 00:39:49,979 - ERROR - ✗ intermediate.int_lever__opportunity_contact_info: Catalog Error: Table with name int_lever__contact_info does not exist!
2026-10-25 00:39:49,979 - ERROR - ✗ intermediate.int_lever__interview_feedback: Catalog Error: Table with name stg_lever__interview does not exist!
2026-10-25 00:39:49,979 - ERROR - ✗ intermediate.int_lever__interview_users: Catalog Error: Table with name stg_lever__interview does not exist!
2026-10-25 00:39:49,980 - ERROR - ✗ intermediate.int_lever__opportunity_users: Catalog Error: Table with name stg_lever__user does not exist!
2026-10-25 00:39:49,987 - ERROR - ✗ intermediate.int_lever__posting_interviews: Catalog Error: Table with name stg_lever__interview does not exist!
2026-10-25 00:39:49,995 - ERROR - ✗ intermediate.int_lever__requisition_users: Catalog Error: Table with name stg_lever__user does not exist!
2026-10-25 00:39:49,996 - ERROR - ✗ intermediate.int_lever__candidate_insights: Catalog Error: Table with name stg_lever__interview does not exist!
2026-10-25 00:39:50,027 - ERROR - ✗ intermediate.int_lever__interviewer_performance: Catalog Error: Table with name stg_lever__user does not exist!
2026-10-25 00:39:50,074 - ERROR - ✗ marts.lever__interview_enhanced: Catalog Error: Table with name int_lever__interview_users does not exist!
2026-10-25 00:39:50,075 - ERROR - ✗ marts.lever__posting_enhanced: Catalog Error: Table with name int_lever__posting_interviews does not exist!
2026-10-25 00:39:50,075 - ERROR - ✗ marts.lever__opportunity_enhanced: Catalog Error: Table with name int_lever__opportunity_contact_info does not exist!
2026-10-25 00:39:50,076 - ERROR - ✗ marts.lever__opportunity_stage_history: Catalog Error: Table with name lever__opportunity_enhanced does not exist!
2026-10-25 00:39:50,076 - ERROR - ✗ marts.lever__requisition_enhanced: Catalog Error: Table with name int_lever__requisition_users does not exist!
2026-10-25 00:39:50,077 - ERROR - ✗ marts.lever__candidate_quality_insights: Catalog Error: Table with name int_lever__candidate_insights does not exist!
2026-10-25 00:39:50,122 - ERROR - ✗ marts.lever__hiring_manager_scorecard: Catalog Error: Table with name stg_lever__user does not exist!
2026-10-25 00:39:50,148 - ERROR - 
```

## result_md_table_sentences

```json
{
  "present": true,
  "path": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md",
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md",
  "sha256": "8623ff923ce1c52b5f81c17e037ce0228d70bc99877e2dcbb97f84c1d2696dbc",
  "sentences": [],
  "policy": "All sentences naming the table; includes sentences without 008 keywords. Existing D10 ids attached where applicable."
}
```

## original_files

```json
{
  "paths": [
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/10.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/11.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/12.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/17.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/18.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/19.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/20.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/21.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/22.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/25.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/26.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/27.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/28.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/35.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/36.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/37.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/38.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/5.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/6.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/9.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__application.sql",
    "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml",
    "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb",
    "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql"
  ],
  "archive": "/home/katherine/Assumption_Ledger/traces/dacomp_deimpl_prev.tar.gz",
  "gold_SQL_search_root": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql",
  "gold_SQL_search_names": [
    "stg_lever__application",
    "stg_lever__application"
  ],
  "source_fingerprints": "records/012_input_before.json"
}
```
