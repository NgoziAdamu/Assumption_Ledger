# impl-002 / stg_pendo__guide_event

## basic_information

```json
{
  "task": "impl-002",
  "layer": "staging",
  "table": "stg_pendo__guide_event",
  "status": "待标注",
  "difference_source": {
    "kind": "original_007_009",
    "record": "records/007_tolerance_tables.jsonl",
    "detail_record": "/home/katherine/Assumption_Ledger/records/004_staging_impl-002.json",
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
  "source_path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml",
  "source_sha256": "3c77f4244379d0614d1bcc2d9dab0ebe31293601f6ccd33281c2e30d67ea5385",
  "parse_mode": "strict",
  "requested_table": "stg_pendo__guide_event",
  "status": "found"
}
```
```json
{
  "yaml_path": [
    "staging_contract",
    "tables",
    6
  ],
  "start_line": 268,
  "end_line": 321
}
```
```yaml
    - name: stg_pendo__guide_event
      description: "Cleaned guide interaction events with validated guide steps and timing"
      source_table: "raw.guide_event"
      columns:
        - name: account_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: guide_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: remote_ip
          data_type: VARCHAR(255)
          validation_rules:
            - rule: "remote_ip IS NULL OR remote_ip ~ '^([0-9]{1,3}){3}[0-9]{1,3}$' OR remote_ip ~ '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'"
              on_failure: nullify_field
        - name: server_name
          data_type: VARCHAR(255)
        - name: occurred_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: user_agent
          data_type: VARCHAR(255)
        - name: visitor_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: app_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: country
          data_type: VARCHAR(255)
        - name: guide_step_id
          data_type: BIGINT
        - name: latitude
          data_type: DOUBLE
        - name: longitude
          data_type: DOUBLE
          validation_rules:
            - rule: "longitude BETWEEN -180 AND 180 OR longitude IS NULL"
              on_failure: nullify_field
        - name: region
          data_type: VARCHAR(255)
        - name: type
          data_type: VARCHAR(255)
        - name: url
          data_type: VARCHAR(255)
          validation_rules:
            - rule: "url = NULLIF(TRIM(url), '')"
              on_failure: correct
            - rule: "url IS NULL OR url ~ '^https?://'"
              on_failure: nullify_field
        - name: guide_event_key
          data_type: VARCHAR(255)
          description: "Generated surrogate key"

```

## agent_final_SQL

```json
{
  "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
  "sha256": "8388508da34d60acc3a1ee931015fa1be0dbc093a5c8c16de6061c092f8268b4",
  "start_line": 1,
  "end_line": 18
}
```
```sql
SELECT
    CAST(account_id AS VARCHAR) AS account_id,
    CAST(guide_id AS VARCHAR) AS guide_id,
    CASE WHEN remote_ip IS NULL OR regexp_matches(CAST(remote_ip AS VARCHAR), '^([0-9]{1,3}\.){3}[0-9]{1,3}$') OR regexp_matches(CAST(remote_ip AS VARCHAR), '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$') THEN CAST(remote_ip AS VARCHAR) ELSE NULL END AS remote_ip,
    NULLIF(TRIM(CAST(server_name AS VARCHAR)), '') AS server_name,
    TRY_CAST(SUBSTRING(CAST(timestamp AS VARCHAR), 1, 23) AS TIMESTAMP) AS occurred_at,
    NULLIF(TRIM(CAST(user_agent AS VARCHAR)), '') AS user_agent,
    CAST(visitor_id AS VARCHAR) AS visitor_id,
    CAST(app_id AS VARCHAR) AS app_id,
    CAST(country AS VARCHAR) AS country,
    TRY_CAST(guide_step_id AS BIGINT) AS guide_step_id,
    TRY_CAST(latitude AS DOUBLE) AS latitude,
    CASE WHEN TRY_CAST(longitude AS DOUBLE) BETWEEN -180 AND 180 THEN TRY_CAST(longitude AS DOUBLE) ELSE NULL END AS longitude,
    CAST(region AS VARCHAR) AS region,
    CAST(type AS VARCHAR) AS type,
    CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END AS url,
    md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''))) AS guide_event_key
FROM raw.guide_event
```

## gold_SQL_仅供定位差异

```json
{
  "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
  "sha256": "71676c28db577a69d0a194a59199053efdc0318a6e5b415e7c971f7e6b0c2f58",
  "start_line": 1,
  "end_line": 83
}
```
```sql
-- Staging model for guide_event
-- Converted from DBT to DuckDB-compatible SQL
-- Implements data quality checks per staging_data_specification.yaml

SELECT
    -- Account ID with proper data type and validation
    CAST(account_id AS VARCHAR(50)) as account_id,

    -- App ID with proper data type and validation
    CAST(app_id AS VARCHAR(50)) as app_id,

    -- Geographic and location data
    CAST(country AS VARCHAR(255)) as country,
    CAST(guide_id AS VARCHAR(50)) as guide_id,
    CAST(guide_step_id AS BIGINT) as guide_step_id,

    -- Latitude with range validation
    CASE
        WHEN latitude BETWEEN -90 AND 90 THEN CAST(latitude AS DOUBLE)
        ELSE NULL
    END as latitude,

    -- Longitude with range validation
    CASE
        WHEN longitude BETWEEN -180 AND 180 THEN CAST(longitude AS DOUBLE)
        ELSE NULL
    END as longitude,

    CAST(region AS VARCHAR(255)) as region,

    -- Remote IP with validation pattern
    CASE
        WHEN remote_ip IS NULL THEN NULL
        WHEN remote_ip ~ '^([0-9]{1,3}\.){3}[0-9]{1,3}$' OR remote_ip ~ '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$' THEN CAST(remote_ip AS VARCHAR(255))
        ELSE NULL
    END as remote_ip,

    CAST(server_name AS VARCHAR(255)) as server_name,

    -- Occurred at with timestamp casting and not null constraint
    TRY_CAST(SUBSTRING(timestamp, 1, 23) AS TIMESTAMP) as occurred_at,

    CAST(type AS VARCHAR(255)) as type,

    -- URL with validation and correction rules
    CASE
        WHEN TRIM(url) = '' THEN NULL
        WHEN url IS NOT NULL AND url ~ '^https?://' THEN TRIM(url)
        ELSE NULL
    END as url,

    CAST(user_agent AS VARCHAR(255)) as user_agent,

    -- Visitor ID with proper data type and validation
    CAST(visitor_id AS VARCHAR(50)) as visitor_id,

    -- Generate a surrogate key using MD5 hash of concatenated fields
    CASE
        WHEN account_id IS NOT NULL AND guide_id IS NOT NULL AND timestamp IS NOT NULL AND visitor_id IS NOT NULL
        THEN MD5(CONCAT(
            COALESCE(CAST(visitor_id AS VARCHAR), ''),
            COALESCE(CAST(timestamp AS VARCHAR), ''),
            COALESCE(CAST(account_id AS VARCHAR), ''),
            COALESCE(server_name, ''),
            COALESCE(CAST(guide_id AS VARCHAR), ''),
            COALESCE(user_agent, ''),
            COALESCE(remote_ip, '')
        ))
        ELSE NULL
    END as guide_event_key

FROM raw.guide_event
WHERE
    -- Filter records with severe data quality issues
    account_id IS NOT NULL
    AND account_id != ''
    AND guide_id IS NOT NULL
    AND guide_id != ''
    AND timestamp IS NOT NULL
    AND visitor_id IS NOT NULL
    AND visitor_id != ''
    AND app_id IS NOT NULL
    AND app_id != ''
```

## differences

```json
{
  "kind": "original_007_009",
  "record": "records/007_tolerance_tables.jsonl",
  "detail_record": "/home/katherine/Assumption_Ledger/records/004_staging_impl-002.json",
  "prediction_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb",
  "gold_database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb",
  "actual_schema": "staging",
  "table": "stg_pendo__guide_event",
  "candidate_date": null,
  "comparison_columns": [
    "account_id",
    "app_id",
    "country",
    "guide_event_key",
    "guide_id",
    "guide_step_id",
    "latitude",
    "longitude",
    "region",
    "remote_ip",
    "server_name",
    "type",
    "url",
    "user_agent",
    "visitor_id"
  ],
  "key_columns": [
    "account_id",
    "app_id",
    "guide_id",
    "visitor_id"
  ],
  "prediction_rows": 15000,
  "gold_rows": 15000,
  "row_delta": 0,
  "key_statistics": {
    "pred_distinct_keys": 15000,
    "gold_distinct_keys": 15000,
    "pred_duplicate_key_groups": 0,
    "gold_duplicate_key_groups": 0,
    "pred_only_keys": 0,
    "gold_only_keys": 0,
    "shared_keys": 15000,
    "shared_nonunique_key_groups": 0
  },
  "l0_column_differences": [
    {
      "column": "account_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "app_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "country",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "guide_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "guide_step_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "latitude",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 13655,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 13655,
      "pred_unmatched_value_occurrences": 13655,
      "gold_unmatched_value_occurrences": 13655,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "longitude",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "region",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "remote_ip",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "server_name",
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
      "column": "url",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 15000,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 15000,
      "pred_unmatched_value_occurrences": 15000,
      "gold_unmatched_value_occurrences": 15000,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "user_agent",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "visitor_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "guide_event_key",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 15000,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 15000,
      "pred_unmatched_value_occurrences": 15000,
      "gold_unmatched_value_occurrences": 15000,
      "count_semantics": "exact_one_to_one_rows"
    }
  ],
  "l3_column_differences": [
    {
      "column": "account_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "app_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "country",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "guide_event_key",
      "one_to_one_mismatch_rows": 15000,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 15000,
      "pred_unmatched_value_occurrences": 15000,
      "gold_unmatched_value_occurrences": 15000,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "guide_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "guide_step_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "latitude",
      "one_to_one_mismatch_rows": 13655,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 13655,
      "pred_unmatched_value_occurrences": 13655,
      "gold_unmatched_value_occurrences": 13655,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "longitude",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "region",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "remote_ip",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "server_name",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "type",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "url",
      "one_to_one_mismatch_rows": 15000,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 15000,
      "pred_unmatched_value_occurrences": 15000,
      "gold_unmatched_value_occurrences": 15000,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "user_agent",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "visitor_id",
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
      "column": "account_id",
      "l0_counts_verbatim": {
        "column": "account_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "account_id",
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
      "column": "app_id",
      "l0_counts_verbatim": {
        "column": "app_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "app_id",
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
      "column": "country",
      "l0_counts_verbatim": {
        "column": "country",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "country",
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
      "column": "guide_id",
      "l0_counts_verbatim": {
        "column": "guide_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "guide_id",
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
      "column": "guide_step_id",
      "l0_counts_verbatim": {
        "column": "guide_step_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "guide_step_id",
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
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "latitude",
      "l0_counts_verbatim": {
        "column": "latitude",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 13655,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 13655,
        "pred_unmatched_value_occurrences": 13655,
        "gold_unmatched_value_occurrences": 13655,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "latitude",
        "one_to_one_mismatch_rows": 13655,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 13655,
        "pred_unmatched_value_occurrences": 13655,
        "gold_unmatched_value_occurrences": 13655,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000108",
            "visitor_id": "vis10000003172"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000108",
            "visitor_id": "VIS10000003172"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000108",
            "visitor_id": "VIS10000003172"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "207.38",
          "gold_value": null
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000147",
            "visitor_id": "vis10000001477"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000147",
            "visitor_id": "VIS10000001477"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000147",
            "visitor_id": "VIS10000001477"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "106.5",
          "gold_value": null
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000232",
            "visitor_id": "vis10000005067"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000232",
            "visitor_id": "VIS10000005067"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000232",
            "visitor_id": "VIS10000005067"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "385.3",
          "gold_value": null
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000298",
            "visitor_id": "vis10000001222"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000298",
            "visitor_id": "VIS10000001222"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000298",
            "visitor_id": "VIS10000001222"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "877.67",
          "gold_value": null
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000002",
            "guide_id": "gui10000000253",
            "visitor_id": "vis10000006171"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000002",
            "guide_id": "GUI10000000253",
            "visitor_id": "VIS10000006171"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000002",
            "guide_id": "GUI10000000253",
            "visitor_id": "VIS10000006171"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "753.31",
          "gold_value": null
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 13655,
        "pred_unmatched_value_occurrences": 13655,
        "gold_unmatched_value_occurrences": 13655
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "longitude",
      "l0_counts_verbatim": {
        "column": "longitude",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "longitude",
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
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "region",
      "l0_counts_verbatim": {
        "column": "region",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "region",
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
      "column": "remote_ip",
      "l0_counts_verbatim": {
        "column": "remote_ip",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "remote_ip",
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
      "column": "server_name",
      "l0_counts_verbatim": {
        "column": "server_name",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "server_name",
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
      "l3_counts_verbatim": {
        "column": "type",
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
      "column": "url",
      "l0_counts_verbatim": {
        "column": "url",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 15000,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 15000,
        "pred_unmatched_value_occurrences": 15000,
        "gold_unmatched_value_occurrences": 15000,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "url",
        "one_to_one_mismatch_rows": 15000,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 15000,
        "pred_unmatched_value_occurrences": 15000,
        "gold_unmatched_value_occurrences": 15000,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000108",
            "visitor_id": "vis10000003172"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000108",
            "visitor_id": "VIS10000003172"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000108",
            "visitor_id": "VIS10000003172"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "http://waters.com/",
          "gold_value": null
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000147",
            "visitor_id": "vis10000001477"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000147",
            "visitor_id": "VIS10000001477"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000147",
            "visitor_id": "VIS10000001477"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "http://www.swanson.org/",
          "gold_value": null
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000232",
            "visitor_id": "vis10000005067"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000232",
            "visitor_id": "VIS10000005067"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000232",
            "visitor_id": "VIS10000005067"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "https://robinson.com/",
          "gold_value": null
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000298",
            "visitor_id": "vis10000001222"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000298",
            "visitor_id": "VIS10000001222"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000298",
            "visitor_id": "VIS10000001222"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "https://www.peterson.biz/",
          "gold_value": null
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000002",
            "guide_id": "gui10000000253",
            "visitor_id": "vis10000006171"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000002",
            "guide_id": "GUI10000000253",
            "visitor_id": "VIS10000006171"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000002",
            "guide_id": "GUI10000000253",
            "visitor_id": "VIS10000006171"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "http://www.gilbert.info/",
          "gold_value": null
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 15000,
        "pred_unmatched_value_occurrences": 15000,
        "gold_unmatched_value_occurrences": 15000
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "user_agent",
      "l0_counts_verbatim": {
        "column": "user_agent",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "user_agent",
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
      "column": "visitor_id",
      "l0_counts_verbatim": {
        "column": "visitor_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "visitor_id",
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
      "column": "guide_event_key",
      "l0_counts_verbatim": {
        "column": "guide_event_key",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 15000,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 15000,
        "pred_unmatched_value_occurrences": 15000,
        "gold_unmatched_value_occurrences": 15000,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "guide_event_key",
        "one_to_one_mismatch_rows": 15000,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 15000,
        "pred_unmatched_value_occurrences": 15000,
        "gold_unmatched_value_occurrences": 15000,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000108",
            "visitor_id": "vis10000003172"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000108",
            "visitor_id": "VIS10000003172"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000108",
            "visitor_id": "VIS10000003172"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "083bcd6f6fd561ff09d075c6c809a0ed",
          "gold_value": "111c3ac5f90a51c7b6ae225bccb6aa25"
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000147",
            "visitor_id": "vis10000001477"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000147",
            "visitor_id": "VIS10000001477"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000147",
            "visitor_id": "VIS10000001477"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "eaaa1c6366e26f66655787b8e1ac206b",
          "gold_value": "9f9a029143f828a64cfe45c5ba07ab16"
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000232",
            "visitor_id": "vis10000005067"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000232",
            "visitor_id": "VIS10000005067"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000232",
            "visitor_id": "VIS10000005067"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "133ab0ded1aa1d1588a4cf37e12be554",
          "gold_value": "562db7dba343585f64c117ba9461f043"
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000001",
            "guide_id": "gui10000000298",
            "visitor_id": "vis10000001222"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000298",
            "visitor_id": "VIS10000001222"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000001",
            "guide_id": "GUI10000000298",
            "visitor_id": "VIS10000001222"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "1a7938400d771b5529787b1e99dbeef6",
          "gold_value": "7638766e42b65f87d8a298916774b6fe"
        },
        {
          "key_normalized": {
            "account_id": "3876159443212129",
            "app_id": "app10000000002",
            "guide_id": "gui10000000253",
            "visitor_id": "vis10000006171"
          },
          "agent_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000002",
            "guide_id": "GUI10000000253",
            "visitor_id": "VIS10000006171"
          },
          "gold_key_raw_text": {
            "account_id": "3876159443212129",
            "app_id": "APP10000000002",
            "guide_id": "GUI10000000253",
            "visitor_id": "VIS10000006171"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "1f1e399fe3a877fda1db98e7528fed1a",
          "gold_value": "a595f8c44d2dfbfcdb0daac7b89df6fb"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 15000,
        "pred_unmatched_value_occurrences": 15000,
        "gold_unmatched_value_occurrences": 15000
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    }
  ]
}
```

## agent_constraints_006

```json
{
  "source_record": "records/006_contract_impl-002.json",
  "declarations": {
    "grain": [],
    "primary_key": [],
    "not_null": [
      {
        "columns": [
          "account_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "staging_contract",
              "tables",
              6,
              "columns",
              0,
              "constraints",
              0
            ],
            "start_line": 274,
            "end_line": 274,
            "original_excerpt": "          constraints: [not_null]\n",
            "decoded_value": [
              "not_null"
            ]
          }
        ]
      },
      {
        "columns": [
          "guide_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "staging_contract",
              "tables",
              6,
              "columns",
              1,
              "constraints",
              0
            ],
            "start_line": 277,
            "end_line": 277,
            "original_excerpt": "          constraints: [not_null]\n",
            "decoded_value": [
              "not_null"
            ]
          }
        ]
      },
      {
        "columns": [
          "occurred_at"
        ],
        "sources": [
          {
            "yaml_path": [
              "staging_contract",
              "tables",
              6,
              "columns",
              4,
              "constraints",
              0
            ],
            "start_line": 287,
            "end_line": 287,
            "original_excerpt": "          constraints: [not_null]\n",
            "decoded_value": [
              "not_null"
            ]
          }
        ]
      },
      {
        "columns": [
          "visitor_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "staging_contract",
              "tables",
              6,
              "columns",
              6,
              "constraints",
              0
            ],
            "start_line": 292,
            "end_line": 292,
            "original_excerpt": "          constraints: [not_null]\n",
            "decoded_value": [
              "not_null"
            ]
          }
        ]
      },
      {
        "columns": [
          "app_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "staging_contract",
              "tables",
              6,
              "columns",
              7,
              "constraints",
              0
            ],
            "start_line": 295,
            "end_line": 295,
            "original_excerpt": "          constraints: [not_null]\n",
            "decoded_value": [
              "not_null"
            ]
          }
        ]
      }
    ],
    "unique": []
  },
  "agent": {
    "table_exists": true,
    "actual_schema": "staging",
    "table_type": "BASE TABLE",
    "same_name_other_schemas": [],
    "row_count": 15000,
    "checks": {
      "grain": [],
      "primary_key": [],
      "not_null": [
        {
          "columns": [
            "account_id"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        },
        {
          "columns": [
            "guide_id"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        },
        {
          "columns": [
            "occurred_at"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        },
        {
          "columns": [
            "visitor_id"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        },
        {
          "columns": [
            "app_id"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        }
      ],
      "unique": []
    },
    "actual_table": "stg_pendo__guide_event",
    "actual_columns": [
      "account_id",
      "guide_id",
      "remote_ip",
      "server_name",
      "occurred_at",
      "user_agent",
      "visitor_id",
      "app_id",
      "country",
      "guide_step_id",
      "latitude",
      "longitude",
      "region",
      "type",
      "url",
      "guide_event_key"
    ],
    "missing_declared_columns": [],
    "not_null_count_sql": "SELECT count(*) FILTER(WHERE \"account_id\" IS NULL),count(*) FILTER(WHERE \"app_id\" IS NULL),count(*) FILTER(WHERE \"guide_id\" IS NULL),count(*) FILTER(WHERE \"occurred_at\" IS NULL),count(*) FILTER(WHERE \"visitor_id\" IS NULL) FROM \"staging\".\"stg_pendo__guide_event\"",
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
        "declared_checks": 5,
        "checked_checks": 5,
        "unknown_checks": 0,
        "complete": true
      },
      "unique": {
        "status": "not_declared",
        "violated": null,
        "declared_checks": 0,
        "checked_checks": 0,
        "unknown_checks": 0
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
    "task": "impl-002",
    "layer": "staging",
    "table": "stg_pendo__guide_event",
    "logical_contract_table": "stg_pendo__guide_event",
    "delivery_name_mapping_evidence": [],
    "inventory_sources": {
      "retained_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb",
      "present_in_database": true,
      "agent_final_sql_files": [
        "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql"
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
          "007_prediction_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb"
        }
      ],
      "status": "待标注",
      "comparison_lookup_layer": "staging",
      "comparison_lookup_table": "stg_pendo__guide_event",
      "actual_gold_relation_exists": true
    },
    "contract": {
      "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml",
      "blocks": [
        {
          "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml",
          "start_line": 268,
          "end_line": 320,
          "original_text": "    - name: stg_pendo__guide_event\n      description: \"Cleaned guide interaction events with validated guide steps and timing\"\n      source_table: \"raw.guide_event\"\n      columns:\n        - name: account_id\n          data_type: VARCHAR(50)\n          constraints: [not_null]\n        - name: guide_id\n          data_type: VARCHAR(50)\n          constraints: [not_null]\n        - name: remote_ip\n          data_type: VARCHAR(255)\n          validation_rules:\n            - rule: \"remote_ip IS NULL OR remote_ip ~ '^([0-9]{1,3}){3}[0-9]{1,3}$' OR remote_ip ~ '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'\"\n              on_failure: nullify_field\n        - name: server_name\n          data_type: VARCHAR(255)\n        - name: occurred_at\n          data_type: TIMESTAMP\n          constraints: [not_null]\n        - name: user_agent\n          data_type: VARCHAR(255)\n        - name: visitor_id\n          data_type: VARCHAR(50)\n          constraints: [not_null]\n        - name: app_id\n          data_type: VARCHAR(50)\n          constraints: [not_null]\n        - name: country\n          data_type: VARCHAR(255)\n        - name: guide_step_id\n          data_type: BIGINT\n        - name: latitude\n          data_type: DOUBLE\n        - name: longitude\n          data_type: DOUBLE\n          validation_rules:\n            - rule: \"longitude BETWEEN -180 AND 180 OR longitude IS NULL\"\n              on_failure: nullify_field\n        - name: region\n          data_type: VARCHAR(255)\n        - name: type\n          data_type: VARCHAR(255)\n        - name: url\n          data_type: VARCHAR(255)\n          validation_rules:\n            - rule: \"url = NULLIF(TRIM(url), '')\"\n              on_failure: correct\n            - rule: \"url IS NULL OR url ~ '^https?://'\"\n              on_failure: nullify_field\n        - name: guide_event_key\n          data_type: VARCHAR(255)\n          description: \"Generated surrogate key\"\n",
          "yaml_path": [
            "staging_contract",
            "tables",
            6
          ]
        }
      ]
    },
    "output": {
      "status": "checked",
      "exists": true,
      "row_count": 15000,
      "zero_rows": false,
      "columns": [
        {
          "name": "account_id",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "guide_id",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "remote_ip",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 15000
        },
        {
          "name": "server_name",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "occurred_at",
          "type": "TIMESTAMP",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "user_agent",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "visitor_id",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "app_id",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "country",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "guide_step_id",
          "type": "BIGINT",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "latitude",
          "type": "DOUBLE",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "longitude",
          "type": "DOUBLE",
          "nonnull_rows": 2692,
          "sql_null_rows": 12308
        },
        {
          "name": "region",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "type",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "url",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        },
        {
          "name": "guide_event_key",
          "type": "VARCHAR",
          "nonnull_rows": 15000,
          "sql_null_rows": 0
        }
      ],
      "all_null_columns": [
        {
          "column": "remote_ip",
          "table_rows": 15000
        }
      ],
      "constant_nonnull_columns": [],
      "equal_column_groups": [],
      "profile_sql": "SELECT count(*),count(\"account_id\"),min(CAST(\"account_id\" AS VARCHAR)),max(CAST(\"account_id\" AS VARCHAR)),sum(hash(CAST(\"account_id\" AS VARCHAR))),count(\"guide_id\"),min(CAST(\"guide_id\" AS VARCHAR)),max(CAST(\"guide_id\" AS VARCHAR)),sum(hash(CAST(\"guide_id\" AS VARCHAR))),count(\"remote_ip\"),min(CAST(\"remote_ip\" AS VARCHAR)),max(CAST(\"remote_ip\" AS VARCHAR)),sum(hash(CAST(\"remote_ip\" AS VARCHAR))),count(\"server_name\"),min(CAST(\"server_name\" AS VARCHAR)),max(CAST(\"server_name\" AS VARCHAR)),sum(hash(CAST(\"server_name\" AS VARCHAR))),count(\"occurred_at\"),min(CAST(\"occurred_at\" AS VARCHAR)),max(CAST(\"occurred_at\" AS VARCHAR)),sum(hash(CAST(\"occurred_at\" AS VARCHAR))),count(\"user_agent\"),min(CAST(\"user_agent\" AS VARCHAR)),max(CAST(\"user_agent\" AS VARCHAR)),sum(hash(CAST(\"user_agent\" AS VARCHAR))),count(\"visitor_id\"),min(CAST(\"visitor_id\" AS VARCHAR)),max(CAST(\"visitor_id\" AS VARCHAR)),sum(hash(CAST(\"visitor_id\" AS VARCHAR))),count(\"app_id\"),min(CAST(\"app_id\" AS VARCHAR)),max(CAST(\"app_id\" AS VARCHAR)),sum(hash(CAST(\"app_id\" AS VARCHAR))),count(\"country\"),min(CAST(\"country\" AS VARCHAR)),max(CAST(\"country\" AS VARCHAR)),sum(hash(CAST(\"country\" AS VARCHAR))),count(\"guide_step_id\"),min(CAST(\"guide_step_id\" AS VARCHAR)),max(CAST(\"guide_step_id\" AS VARCHAR)),sum(hash(CAST(\"guide_step_id\" AS VARCHAR))),count(\"latitude\"),min(CAST(\"latitude\" AS VARCHAR)),max(CAST(\"latitude\" AS VARCHAR)),sum(hash(CAST(\"latitude\" AS VARCHAR))),count(\"longitude\"),min(CAST(\"longitude\" AS VARCHAR)),max(CAST(\"longitude\" AS VARCHAR)),sum(hash(CAST(\"longitude\" AS VARCHAR))),count(\"region\"),min(CAST(\"region\" AS VARCHAR)),max(CAST(\"region\" AS VARCHAR)),sum(hash(CAST(\"region\" AS VARCHAR))),count(\"type\"),min(CAST(\"type\" AS VARCHAR)),max(CAST(\"type\" AS VARCHAR)),sum(hash(CAST(\"type\" AS VARCHAR))),count(\"url\"),min(CAST(\"url\" AS VARCHAR)),max(CAST(\"url\" AS VARCHAR)),sum(hash(CAST(\"url\" AS VARCHAR))),count(\"guide_event_key\"),min(CAST(\"guide_event_key\" AS VARCHAR)),max(CAST(\"guide_event_key\" AS VARCHAR)),sum(hash(CAST(\"guide_event_key\" AS VARCHAR))) FROM \"staging\".\"stg_pendo__guide_event\"",
      "equal_column_confirmation_queries": [],
      "equality_policy": "exact CAST AS VARCHAR per row; no trim/case/numeric/date normalization; both NULL ignored; at least one nonnull equal row; one-sided NULL differs",
      "actual_schema": "staging",
      "actual_table": "stg_pendo__guide_event",
      "relation_type": "BASE TABLE"
    },
    "agent_sql": [
      {
        "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
        "status": "parsed",
        "parser": "30.25.0",
        "sources": [
          {
            "name": "raw.guide_event",
            "canonical": "raw.guide_event",
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
            "name": "account_id",
            "alternatives": [
              {
                "expression_sql": "CAST(account_id AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 2,
                "end_line": 2,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "account_id",
            "retained_output_ordinal": 1
          },
          {
            "name": "guide_id",
            "alternatives": [
              {
                "expression_sql": "CAST(guide_id AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 3,
                "end_line": 3,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "guide_id",
            "retained_output_ordinal": 2
          },
          {
            "name": "remote_ip",
            "alternatives": [
              {
                "expression_sql": "CASE WHEN remote_ip IS NULL OR REGEXP_MATCHES(CAST(remote_ip AS TEXT), '^([0-9]{1,3}\\.){3}[0-9]{1,3}$') OR REGEXP_MATCHES(CAST(remote_ip AS TEXT), '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$') THEN CAST(remote_ip AS TEXT) ELSE NULL END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 4,
                "end_line": 4,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "remote_ip",
            "retained_output_ordinal": 3
          },
          {
            "name": "server_name",
            "alternatives": [
              {
                "expression_sql": "NULLIF(TRIM(CAST(server_name AS TEXT)), '')",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 5,
                "end_line": 5,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "server_name",
            "retained_output_ordinal": 4
          },
          {
            "name": "occurred_at",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(SUBSTRING(CAST(timestamp AS TEXT), 1, 23) AS TIMESTAMP)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 6,
                "end_line": 6,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "occurred_at",
            "retained_output_ordinal": 5
          },
          {
            "name": "user_agent",
            "alternatives": [
              {
                "expression_sql": "NULLIF(TRIM(CAST(user_agent AS TEXT)), '')",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 7,
                "end_line": 7,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "user_agent",
            "retained_output_ordinal": 6
          },
          {
            "name": "visitor_id",
            "alternatives": [
              {
                "expression_sql": "CAST(visitor_id AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 8,
                "end_line": 8,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "visitor_id",
            "retained_output_ordinal": 7
          },
          {
            "name": "app_id",
            "alternatives": [
              {
                "expression_sql": "CAST(app_id AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 9,
                "end_line": 9,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "app_id",
            "retained_output_ordinal": 8
          },
          {
            "name": "country",
            "alternatives": [
              {
                "expression_sql": "CAST(country AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 10,
                "end_line": 10,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "country",
            "retained_output_ordinal": 9
          },
          {
            "name": "guide_step_id",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(guide_step_id AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 11,
                "end_line": 11,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "guide_step_id",
            "retained_output_ordinal": 10
          },
          {
            "name": "latitude",
            "alternatives": [
              {
                "expression_sql": "TRY_CAST(latitude AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 12,
                "end_line": 12,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "latitude",
            "retained_output_ordinal": 11
          },
          {
            "name": "longitude",
            "alternatives": [
              {
                "expression_sql": "CASE WHEN TRY_CAST(longitude AS DOUBLE) BETWEEN -180 AND 180 THEN TRY_CAST(longitude AS DOUBLE) ELSE NULL END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 13,
                "end_line": 13,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "longitude",
            "retained_output_ordinal": 12
          },
          {
            "name": "region",
            "alternatives": [
              {
                "expression_sql": "CAST(region AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 14,
                "end_line": 14,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "region",
            "retained_output_ordinal": 13
          },
          {
            "name": "type",
            "alternatives": [
              {
                "expression_sql": "CAST(type AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 15,
                "end_line": 15,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "type",
            "retained_output_ordinal": 14
          },
          {
            "name": "url",
            "alternatives": [
              {
                "expression_sql": "CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS TEXT)), '') END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 16,
                "end_line": 16,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "url",
            "retained_output_ordinal": 15
          },
          {
            "name": "guide_event_key",
            "alternatives": [
              {
                "expression_sql": "MD5(CONCAT_WS('|', COALESCE(CAST(visitor_id AS TEXT), ''), COALESCE(CAST(timestamp AS TEXT), ''), COALESCE(CAST(guide_id AS TEXT), ''), COALESCE(CAST(account_id AS TEXT), '')))",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
                "line": 17,
                "end_line": 17,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "guide_event_key",
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
            "name": "raw.guide_event",
            "canonical": "raw.guide_event",
            "basis": "source_table",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml",
            "block_start_line": 268
          },
          {
            "name": "raw.guide_event",
            "canonical": "raw.guide_event",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml",
            "line": 270,
            "line_text": "      source_table: \"raw.guide_event\""
          }
        ],
        "canonical_names": [
          "raw.guide_event"
        ]
      },
      "agent_direct_read_sources": [
        "raw.guide_event"
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
          "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql"
        ]
      },
      "contract": {
        "available": true,
        "appears": false,
        "hits": []
      }
    },
    "any_result_keyword_excerpt_ids": [
      "008-001195",
      "008-001205",
      "008-001213",
      "008-001217"
    ],
    "trace_flags": {
      "A1_zero_rows": false,
      "A2_all_null_column": true,
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
  "event_source_root": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent",
  "actual_read_sources_from_008_B7": [
    "raw.guide_event"
  ],
  "name_match_policy": "Case-insensitive complete identifier-name boundaries; source names include qualified form and bare leaf name. No semantic association inferred.",
  "matched_step_count": 7,
  "full_original_characters_before_budget": 64193,
  "budget_triggered": true,
  "source_only_steps_indexed": 3,
  "retained_full_original_characters": 41975,
  "full_target_steps_exceed_60000": false,
  "budget_policy": "If total command/output text exceeds 60000 characters, keep every target-table step complete and retain only id/location/first line for source-only steps. Do not rewrite or truncate a kept original step."
}
```

### event 9

```json
{
  "event_id": 9,
  "agent_command_sequence": 3,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/9.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1708,
    "decoded_characters": 60
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/9.json",
  "timestamp": "2026-10-25T00:43:40.435992",
  "target_table_name_hits": [
    "stg_pendo__guide_event"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 14139,
  "retention": "full_original"
}
```
```bash
cat config/layer_dependencies.yaml && sed -n '1,240p' run.py
```
```json
{
  "event_id": 10,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/10.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1393,
    "decoded_characters": 14079
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/10.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
# Data layer execution dependencies
# This file defines the execution order for SQL transformations

layers:
  staging:
    description: "Raw data standardization and cleaning"
    tables:
      - stg_pendo__account_history
      - stg_pendo__application_history
      - stg_pendo__event
      - stg_pendo__feature_event
      - stg_pendo__feature_history
      - stg_pendo__group
      - stg_pendo__guide_event
      - stg_pendo__guide_history
      - stg_pendo__guide_step_history
      - stg_pendo__page_event
      - stg_pendo__page_history
      - stg_pendo__page_rule_history
      - stg_pendo__poll
      - stg_pendo__poll_event
      - stg_pendo__user
      - stg_pendo__visitor_account_history
      - stg_pendo__visitor_history

  intermediate:
    description: "Business logic and data integration"
    dependencies: ["staging"]
    tables:
      # Latest history models
      - int_pendo__latest_account
      - int_pendo__latest_application
      - int_pendo__latest_feature
      - int_pendo__latest_guide
      - int_pendo__latest_guide_step
      - int_pendo__latest_nps_rating
      - int_pendo__latest_page
      - int_pendo__latest_page_rule
      - int_pendo__latest_visitor
      - int_pendo__latest_visitor_account
      # Daily metrics models
      - int_pendo__calendar_spine
      - int_pendo__account_daily_metrics
      - int_pendo__feature_daily_metrics
      - int_pendo__guide_daily_metrics
      - int_pendo__page_daily_metrics
      - int_pendo__visitor_daily_metrics
      # Other intermediate models
      - int_pendo__feature_info
      - int_pendo__guide_alltime_metrics
      - int_pendo__guide_info
      - int_pendo__page_info
      # Advanced analytics models
      - int_pendo__user_lifecycle_segments
      - int_pendo__conversion_funnel_analysis
      - int_pendo__product_health_metrics
      - int_pendo__customer_rfm_analysis
      - int_pendo__data_quality_checks

  marts:
    description: "Analysis-ready business entities"
    dependencies: ["intermediate"]
    tables:
      - pendo__account
      - pendo__account_daily_metrics
      - pendo__feature
      - pendo__feature_daily_metrics
      - pendo__feature_event
      - pendo__guide
      - pendo__guide_daily_metrics
      - pendo__guide_event
      - pendo__page
      - pendo__page_daily_metrics
      - pendo__page_event
      - pendo__visitor
      - pendo__visitor_daily_metrics
      - pendo__visitor_feature
      # Advanced analytics marts
      - pendo__customer_lifecycle_insights
      - pendo__product_adoption_analytics
      - pendo__product_adoption_summary
      - pendo__executive_dashboard_metrics

# Execution order within each layer (if specific order needed)
execution_order:
  intermediate:
    # Latest history models first
    - int_pendo__latest_account
    - int_pendo__latest_application
    - int_pendo__latest_feature
    - int_pendo__latest_guide
    - int_pendo__latest_guide_step
    - int_pendo__latest_nps_rating
    - int_pendo__latest_page
    - int_pendo__latest_page_rule
    - int_pendo__latest_visitor
    - int_pendo__latest_visitor_account
    # Daily metrics models
    - int_pendo__calendar_spine
    - int_pendo__account_daily_metrics
    - int_pendo__feature_daily_metrics
    - int_pendo__guide_daily_metrics
    - int_pendo__page_daily_metrics
    - int_pendo__visitor_daily_metrics
    # Other intermediate models
    - int_pendo__feature_info
    - int_pendo__guide_alltime_metrics
    - int_pendo__guide_info
    - int_pendo__page_info
    # Advanced analytics models (must come after basic models)
    - int_pendo__user_lifecycle_segments
    - int_pendo__conversion_funnel_analysis
    - int_pendo__product_health_metrics
    - int_pendo__customer_rfm_analysis
    - int_pendo__data_quality_checks
  
  marts:
    # Base entities first
    - pendo__account
    - pendo__feature
    - pendo__guide
    - pendo__page
    - pendo__visitor
    # Events second
    - pendo__feature_event
    - pendo__guide_event
    - pendo__page_event
    - pendo__visitor_feature
    # Daily metrics last
    - pendo__account_daily_metrics
    - pendo__feature_daily_metrics
    - pendo__guide_daily_metrics
    - pendo__page_daily_metrics
    - pendo__visitor_daily_metrics
    # Advanced analytics marts (depend on base marts)
    - pendo__customer_lifecycle_insights
    - pendo__product_adoption_analytics
    - pendo__product_adoption_summary
    - pendo__executive_dashboard_metrics#!/usr/bin/env python3
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


class PendoDataPipeline:
    """Pendo Data Pipeline Orchestrator - Supports a layered Schema architecture"""
    
    def __init__(self, 
                 source_db_path: str = "pendo_start.duckdb", 
                 target_db_path: str = "pendo.duckdb",
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
        """Load the configuration file"""
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
        """Initialize the working database, create the layered schema architecture, and import raw data"""
        logger.info(f"📥 Creating a new layered database: {self.target_db_path}")
        
                
        if not os.path.exists(self.source_db_path):
            raise FileNotFoundError(f"Source database file not found: {self.source_db_path}")
        
        self.conn = duckdb.connect(self.target_db_path)
        
        self._create_schemas()
        
                
        self._import_raw_data()
        
        logger.info(f"✓ Layered database initialization complete: {self.target_db_path}")
    
    def _create_schemas(self):
        """Create the schemas for the data layers"""
        logger.info("🏗️ Creating Schema layered architecture")
        
        for layer, schema_name in self.schema_config.items():
            try:
                self.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                logger.info(f"  ✓ Created schema: {schema_name}")
            except Exception as e:
                logger.error(f"  ✗ Failed to create schema {schema_name}: {e}")
                raise
    
    def _import_raw_data(self):
        """Import raw data from the source database to the raw schema"""
        logger.info("📥 Importing raw data to the raw schema")
        
                
        try:
            
            source_conn = duckdb.connect(self.source_db_path)
            
                        
            try:
                tables_result = source_conn.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'raw'
                """).fetchall()
            except:
                
                tables_result = source_conn.execute("SHOW TABLES").fetchall()
            
            source_tables = [table[0] for table in tables_result]
            logger.info(f"Found {len(source_tables)} raw tables")
            
                        
            for table_name in source_tables:
                try:
                    
                    try:
                        data = source_conn.execute(f"SELECT * FROM raw.{table_name}").fetchall()
                        columns_info = source_conn.execute(f"DESCRIBE raw.{table_name}").fetchall()
                    except:
                        
                        data = source_conn.execute(f"SELECT * FROM {table_name}").fetchall()
                        columns_info = source_conn.execute(f"DESCRIBE {table_name}").fetchall()
                    
                    column_defs = []
                    for col_info in columns_info:
                        col_name, col_type = col_info[0], col_info[1]
                        column_defs.append(f"{col_name} {col_type}")
                    
                    create_sql = f"CREATE OR REPLACE TABLE raw.{table_name} ({', '.join(column_defs)})"
                    self.conn.execute(create_sql)
                    
                                        
                    if data:
                        placeholders = ', '.join(['?' for _ in columns_info])
                        insert_sql = f"INSERT INTO raw.{table_name} VALUES ({placeholders})"
                        self.conn.executemany(insert_sql, data)
                    
                    logger.info(f"  ✓ raw.{table_name}: {len(data):,} rows")
                    
                except Exception as e:
                    logger.error(f"  ✗ Failed to import table {table_name}: {e}")
                    
            source_conn.close()
                    
        except Exception as e:
            logger.error(f"Failed to import raw data: {e}")
            raise
        
        logger.info("✓ Raw data import complete")
    
    def _load_sql_file(self, file_path: Path) -> str:
        """Load the content of an SQL file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"SQL file {file_path} not found")
            raise
    
    def _execute_sql(self, sql: str, table_name: str, layer_name: str) -> bool:
        """Execute SQL and create a table in the specified schema"""
        try:
            
            target_schema = self.schema_config[layer_name]
            full_table_name = f"{target_schema}.{table_name}"
            
                        
            create_table_sql = f"CREATE OR REPLACE TABLE {full_table_name} AS ({sql})"
            
            logger.info(f"Executing: {full_table_name}")
            self.conn.execute(create_table_sql)
            
                        
            count_result = self.conn.execute(f"SELECT COUNT(*) FROM {full_table_name}").fetchone()
            row_count = count_result[0] if count_result else 0
            
            logger.info(f"✓ {full_table_name}: {row_count:,} rows")
            return True
            
        except Exception as e:
            logger.error(f"✗ {full_table_name}: {e}")
            return False
    
    def _execute_layer(self, layer_name: str) -> bool:
        """Execute all tables in a specified layer"""
        layer_config = self.config['layers'][layer_name]
        tables = layer_config.get('tables', [])
        
                
        execution_order = self.config.get('execution_order', {}).get(layer_name, tables)
        
        logger.info(f"\n=== Executing {layer_name.upper()} Layer ===")
        logger.info(f"Description: {layer_config.get('description', '')}")
        
        success_count = 0
        total_count = len(execution_order)
        
        for table_name in execution_order:
            
            sql_file_path = self.sql_dir / layer_name / f"{table_name}.sql"
            
                        
            if not sql_file_path.exists() and layer_name == 'intermediate':
                
                for subdir in ['latest_history', 'daily_metrics']:
                    subdir_path = self.sql_dir / layer_name / subdir / f"{table_name}.sql"
                    if subdir_path.exists():
                        sql_file_path = subdir_path
                        break
                
                if not sql_file_path.exists():
                    sql_file_path = self.sql_dir / layer_name / f"{table_name}.sql"
            
            if not sql_file_path.exists() and layer_name == 'marts':
                
                if table_name.startswith('pendo__'):
                    file_name = table_name[7:] + '.sql'                 
                    sql_file_path = self.sql_dir / layer_name / file_name
            
            if not sql_file_path.exists():
                logger.warning(f"Skipping {table_name}: SQL file does not exist ({sql_file_path})")
                continue
            
            sql_content = self._load_sql_file(sql_file_path)
            if self._execute_sql(sql_content, table_name, layer_name):
                success_count += 1
        
        logger.info(f"{layer_name.upper()} layer complete: {success_count}/{total_count} tables created successfully")
        return success_count == total_count
    
    def _clean_generated_tables(self):
        """Clean up all generated tables, preserving the raw data schema"""
        logger.info("🧼 Cleaning up previously generated schemas and tables...")
        
                
        schemas_to_clean = ['staging', 'intermediate', 'marts']
        
        for schema_name in schemas_to_clean:
            try:
                
                result = self.conn.execute(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema_name}'").fetchall()
                if result:
                    self.conn.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
                    logger.info(f"✓ Dropped schema: {schema_name}")
            except Exception as e:
                logger.warning(f"Failed to drop schema {schema_name}: {e}")
        
```

### event 13

```json
{
  "event_id": 13,
  "agent_command_sequence": 5,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/13.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2182,
    "decoded_characters": 439
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/13.json",
  "timestamp": "2026-10-25T00:43:46.465944",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "guide_event"
  ],
  "full_original_characters": 17714,
  "retention": "index_and_first_line_only",
  "first_line_original": "find sql -maxdepth 3 -print; python - <<'PY'\n"
}
```
```json
{
  "event_id": 14,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/14.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1867,
    "decoded_characters": 17275
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/14.json",
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
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/17.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1878,
    "decoded_characters": 314
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/17.json",
  "timestamp": "2026-10-25T00:43:59.226892",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "guide_event"
  ],
  "full_original_characters": 1356,
  "retention": "index_and_first_line_only",
  "first_line_original": "python - <<'PY'\n"
}
```
```json
{
  "event_id": 18,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/18.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1563,
    "decoded_characters": 1042
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/18.json",
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
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/19.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 12746,
    "decoded_characters": 5583
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/19.json",
  "timestamp": "2026-10-25T00:44:21.018314",
  "target_table_name_hits": [
    "stg_pendo__guide_event"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 5583,
  "retention": "full_original"
}
```
```bash
cat > /tmp/generate.py <<'PY'
import yaml,os
from pathlib import Path
c=yaml.safe_load(open('docs/data_contract.yaml'))
for d in ['sql/staging','sql/intermediate','sql/marts']: Path(d).mkdir(parents=True,exist_ok=True)
# Contract column -> raw column overrides
maps={
'stg_pendo__user':{'user_id':'id'}, 'stg_pendo__event':{'occurred_at':'timestamp'},
'stg_pendo__application_history':{'application_id':'id','application_name':'name','is_integrated':'integrated','first_event_at':'first_event_time'},
'stg_pendo__account_history':{'account_id':'id','account_id_hash':'id_hash','first_visit_at':'first_visit','last_visit_at':'last_visit'},
'stg_pendo__visitor_history':{'visitor_id':'id','visitor_id_hash':'id_hash','first_visit_at':'first_visit','last_visit':'last_visit'},
'stg_pendo__visitor_account_history':{}, 'stg_pendo__feature_event':{'occurred_at':'timestamp'},
'stg_pendo__guide_event':{'occurred_at':'timestamp'}, 'stg_pendo__page_event':{'occurred_at':'timestamp'},
'stg_pendo__poll_event':{'occurred_at':'timestamp'}, 'stg_pendo__poll':{'poll_id':'id','follow_up_poll_id':'attribute_follow_up'},
'stg_pendo__page_history':{'page_id':'id','page_name':'name','is_dirty':'dirty'},
'stg_pendo__feature_history':{'feature_id':'id','feature_name':'name','is_dirty':'dirty'},
'stg_pendo__guide_history':{'guide_id':'id','guide_name':'name','device_type':'attribute_device_type'},
'stg_pendo__group':{'group_id':'id','group_name':'name'},
'stg_pendo__guide_step_history':{},'stg_pendo__page_rule_history':{},
'stg_pendo__application_history':{'display_name':'display_name'} }
raw_names={'stg_pendo__group':'group_data'}
for t in c['staging_contract']['tables']:
 name=t['name']; raw=t['source_table'].split('.')[1]; raw=raw_names.get(name,raw); mp=maps.get(name,{})
 cols=[]
 for col in t['columns']:
  n=col['name']; src=col.get('source_column',mp.get(n,n))
  typ=col['data_type'];
  if name=='stg_pendo__user':
   expr={'user_id':'CAST(id AS VARCHAR)','deleted_at':"TRY_CAST(NULLIF(deleted_at, '') AS TIMESTAMP)",'first_name':'CAST(first_name AS VARCHAR)','last_name':'CAST(last_name AS VARCHAR)','user_type':'LOWER(TRIM(user_type))','username':'LOWER(TRIM(username))'}[n]
  elif n in ('occurred_at','created_at','last_updated_at','first_visit_at','last_visit_at','first_event_at','reset_at','valid_through','published_at','visitor_last_updated_at','guide_last_updated_at','page_last_updated_at','deleted_at'):
   # source contract specified string timestamps with timezone and raw might string
   expr=f"TRY_CAST(SUBSTRING(CAST({src} AS VARCHAR), 1, 23) AS TIMESTAMP)"
  elif n in ('remote_ip',):
   expr=f"CASE WHEN {src} IS NULL OR regexp_matches(CAST({src} AS VARCHAR), '^([0-9]{{1,3}}\\.){{3}}[0-9]{{1,3}}$') OR regexp_matches(CAST({src} AS VARCHAR), '^([0-9a-fA-F]{{0,4}}:){{2,7}}[0-9a-fA-F]{{0,4}}$') THEN CAST({src} AS VARCHAR) ELSE NULL END"
  elif n in ('server_name','user_agent','url'):
   base=f'NULLIF(TRIM(CAST({src} AS VARCHAR)), \'\')'
   expr=f"CASE WHEN {n if src==n else base} IS NULL THEN NULL ELSE {base} END" if n=='url' else base
  elif n=='account_id' and name=='stg_pendo__event':
   expr='CAST(account_id AS VARCHAR)'
  elif n=='event_key':
   expr="md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''), coalesce(server_name, ''), coalesce(user_agent, ''), coalesce(remote_ip, '')))"
  elif n in ('feature_event_key','guide_event_key','page_event_key','poll_event_key'):
   entity={'feature_event_key':'feature_id','guide_event_key':'guide_id','page_event_key':'page_id','poll_event_key':'poll_id'}[n]
   expr=f"md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST({entity} AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), '')))"
  else:
   expr=f'TRY_CAST({src} AS {typ})' if typ not in ('VARCHAR(50)','VARCHAR(100)','VARCHAR(255)','VARCHAR(65535)') else f'CAST({src} AS VARCHAR)'
   if typ.startswith('VARCHAR'): expr=f'CAST({src} AS VARCHAR)'
   if name=='stg_pendo__event' and n in ('num_events','num_minutes'):
    expr=f"CASE WHEN TRY_CAST({src} AS BIGINT) BETWEEN 0 AND {'10000' if n=='num_events' else '1440'} THEN TRY_CAST({src} AS BIGINT) ELSE NULL END"
   if name=='stg_pendo__event' and n=='account_id': expr='CAST(account_id AS VARCHAR)'
   if name=='stg_pendo__feature_event' and n in ('num_events','num_minutes'): expr=f'TRY_CAST({src} AS DOUBLE)'
   if name=='stg_pendo__guide_event' and n=='longitude': expr=f'CASE WHEN TRY_CAST({src} AS DOUBLE) BETWEEN -180 AND 180 THEN TRY_CAST({src} AS DOUBLE) ELSE NULL END'
   if name=='stg_pendo__poll_event' and n in ('latitude','longitude'):
    lo,hi=((-90,90) if n=='latitude' else (-180,180)); expr=f'CASE WHEN TRY_CAST({src} AS DOUBLE) BETWEEN {lo} AND {hi} THEN TRY_CAST({src} AS DOUBLE) ELSE NULL END'
  cols.append(f'    {expr} AS {n}')
 wh=[]
 for w in t.get('where_conditions',[]):
  if w=='id IS NOT NULL': wh.append('id IS NOT NULL')
  elif w=='id != \'\'': wh.append("id != ''")
  else: wh.append(w)
 if name=='stg_pendo__user': wh += ["user_type IN ('system','internal','api','external')", "username IS NOT NULL AND LENGTH(TRIM(username)) > 0"]
 if name=='stg_pendo__event': wh += ["visitor_id IS NOT NULL AND visitor_id != ''", "account_id IS NOT NULL AND account_id != ''", "app_id IS NOT NULL AND app_id != ''", 'timestamp IS NOT NULL']
 sql='SELECT\n'+',\n'.join(cols)+f'\nFROM raw.{raw}'
 if wh: sql+='\nWHERE '+'\n  AND '.join(wh)
 Path(f'sql/staging/{name}.sql').write_text(sql)
PY
python /tmp/generate.py
```
```json
{
  "event_id": 20,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/20.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 12430,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/20.json",
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
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/21.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 21968,
    "decoded_characters": 10323
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/21.json",
  "timestamp": "2026-10-25T00:44:51.448559",
  "target_table_name_hits": [
    "stg_pendo__guide_event"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 10323,
  "retention": "full_original"
}
```
```bash
cat > /tmp/inter.py <<'PY'
from pathlib import Path
I=Path('sql/intermediate')
def put(n,s): (I/(n+'.sql')).write_text(s.strip())
# latest rank generation
for name,src,pk,ts,cols in [
('latest_account','staging.stg_pendo__account_history','account_id','last_updated_at','*'),('latest_application','staging.stg_pendo__application_history','application_id','last_updated_at','*'),('latest_feature','staging.stg_pendo__feature_history','feature_id','last_updated_at','*'),('latest_guide','staging.stg_pendo__guide_history','guide_id','last_updated_at','*'),('latest_page','staging.stg_pendo__page_history','page_id','last_updated_at','*'),('latest_visitor','staging.stg_pendo__visitor_history','visitor_id','last_updated_at','*'),('latest_visitor_account','staging.stg_pendo__visitor_account_history','visitor_id, account_id','visitor_last_updated_at','*'),('latest_guide_step','staging.stg_pendo__guide_step_history','guide_id, step_id','guide_last_updated_at','*'),('latest_page_rule','staging.stg_pendo__page_rule_history','page_id, rule','page_last_updated_at','*')]:
 suffix=name.replace('latest_','')
 put('int_pendo__'+name,f'''WITH ranked AS (\n    SELECT *, row_number() OVER (PARTITION BY {pk} ORDER BY {ts} DESC) AS latest_{suffix}_index\n    FROM {src}\n)\nSELECT * FROM ranked WHERE latest_{suffix}_index = 1''')
put('int_pendo__latest_nps_rating','''WITH nps_polls AS (SELECT poll_id FROM staging.stg_pendo__poll WHERE lower(attribute_type) = 'npsrating'), ranked AS (SELECT e.visitor_id, CAST(e.account_id AS VARCHAR) AS account_id, TRY_CAST(e.poll_response AS INTEGER) AS nps_rating, row_number() OVER (PARTITION BY e.visitor_id ORDER BY e.occurred_at DESC) AS rn FROM staging.stg_pendo__poll_event e INNER JOIN nps_polls p USING (poll_id)) SELECT visitor_id, account_id, nps_rating FROM ranked WHERE rn = 1''')
put('int_pendo__calendar_spine','''WITH bounds AS (SELECT min(CAST(created_at AS DATE)) AS start_date, current_date + 7 AS end_date FROM staging.stg_pendo__application_history) SELECT unnest(generate_series(start_date, end_date, INTERVAL 1 DAY))::DATE AS date_day FROM bounds WHERE start_date IS NOT NULL AND start_date <= end_date''')
put('int_pendo__account_daily_metrics','''WITH event_daily AS (SELECT CAST(occurred_at AS DATE) occurred_on, account_id, count(DISTINCT visitor_id) count_active_visitors, sum(num_minutes) sum_minutes, sum(num_events) sum_events, count(*) count_event_records FROM staging.stg_pendo__event GROUP BY 1,2), page_daily AS (SELECT CAST(occurred_at AS DATE) occurred_on, account_id, count(DISTINCT page_id) count_pages_viewed, count(DISTINCT visitor_id) count_page_viewing_visitors FROM staging.stg_pendo__page_event GROUP BY 1,2), feature_daily AS (SELECT CAST(occurred_at AS DATE) occurred_on, account_id, count(DISTINCT feature_id) count_features_clicked FROM staging.stg_pendo__feature_event GROUP BY 1,2) SELECT e.occurred_on,e.account_id,e.count_active_visitors,e.sum_minutes,e.sum_events,e.count_event_records,coalesce(p.count_pages_viewed,0) count_pages_viewed,coalesce(f.count_features_clicked,0) count_features_clicked,coalesce(p.count_page_viewing_visitors,0) count_page_viewing_visitors,coalesce(p.count_page_viewing_visitors,0) count_feature_clicking_visitors FROM event_daily e LEFT JOIN page_daily p USING(occurred_on,account_id) LEFT JOIN feature_daily f USING(occurred_on,account_id)''')
def daily(tab,entity,idcol,add_first=True):
 # output all defined daily columns templates feature/page
 source='staging.stg_pendo__'+tab
 if entity=='feature':
  put('int_pendo__feature_daily_metrics', '''WITH base AS (SELECT CAST(occurred_at AS DATE) occurred_on, * FROM staging.stg_pendo__feature_event), vf AS (SELECT visitor_id,feature_id,min(occurred_on) first_on FROM base GROUP BY 1,2), af AS (SELECT account_id,feature_id,min(occurred_on) first_on FROM base GROUP BY 1,2), agg AS (SELECT b.occurred_on,b.feature_id,sum(num_events) sum_clicks,count(*) count_click_events,count(DISTINCT visitor_id) count_visitors,count(DISTINCT account_id) count_accounts,count(DISTINCT CASE WHEN b.occurred_on=v.first_on THEN b.visitor_id END) count_first_time_visitors,count(DISTINCT CASE WHEN b.occurred_on=a.first_on THEN b.account_id END) count_first_time_accounts,sum(num_minutes) sum_minutes FROM base b LEFT JOIN vf v USING(visitor_id,feature_id) LEFT JOIN af a USING(account_id,feature_id) GROUP BY 1,2), totals AS (SELECT occurred_on,sum(sum_clicks) td,sum(count_visitors) tv,sum(count_accounts) ta FROM agg GROUP BY 1) SELECT a.occurred_on,a.feature_id,a.sum_clicks,a.count_click_events,a.count_visitors,a.count_accounts,a.count_first_time_visitors,a.count_first_time_accounts,a.count_visitors-a.count_first_time_visitors count_return_visitors,a.count_accounts-a.count_first_time_accounts count_return_accounts,round(a.sum_minutes/NULLIF(a.count_visitors,0),3) avg_daily_minutes_per_visitor,round(a.sum_clicks/NULLIF(a.count_visitors,0),3) avg_daily_clicks_per_visitor,round(100*a.sum_clicks/NULLIF(t.td,0),3) percent_of_daily_feature_clicks,round(100*a.count_visitors/NULLIF(t.tv,0),3) percent_of_daily_feature_visitors,round(100*a.count_accounts/NULLIF(t.ta,0),3) percent_of_daily_feature_accounts FROM agg a JOIN totals t USING(occurred_on)''')
 if entity=='page':
  put('int_pendo__page_daily_metrics','''WITH base AS (SELECT CAST(occurred_at AS DATE) occurred_on,* FROM staging.stg_pendo__page_event), vf AS (SELECT visitor_id,page_id,min(occurred_on) first_on FROM base GROUP BY 1,2), af AS (SELECT account_id,page_id,min(occurred_on) first_on FROM base GROUP BY 1,2), agg AS (SELECT b.occurred_on,b.page_id,sum(num_events) sum_pageviews,count(*) count_pageview_events,count(DISTINCT visitor_id) count_visitors,count(DISTINCT account_id) count_accounts,count(DISTINCT CASE WHEN b.occurred_on=v.first_on THEN b.visitor_id END) count_first_time_visitors,count(DISTINCT CASE WHEN b.occurred_on=a.first_on THEN b.account_id END) count_first_time_accounts,sum(num_minutes) sum_minutes FROM base b LEFT JOIN vf v USING(visitor_id,page_id) LEFT JOIN af a USING(account_id,page_id) GROUP BY 1,2), totals AS (SELECT occurred_on,sum(sum_pageviews) tp,sum(count_visitors) tv,sum(count_accounts) ta FROM agg GROUP BY 1) SELECT a.occurred_on,a.page_id,a.sum_pageviews,a.count_pageview_events,a.count_visitors,a.count_accounts,a.count_first_time_visitors,a.count_first_time_accounts,a.count_visitors-a.count_first_time_visitors count_return_visitors,a.count_accounts-a.count_first_time_accounts count_return_accounts,round(a.sum_minutes/NULLIF(a.count_visitors,0),3) avg_daily_minutes_per_visitor,round(a.sum_pageviews/NULLIF(a.count_visitors,0),3) avg_daily_pageviews_per_visitor,round(100*a.sum_pageviews/NULLIF(t.tp,0),3) percent_of_daily_pageviews,round(100*a.count_visitors/NULLIF(t.tv,0),3) percent_of_daily_page_visitors,round(100*a.count_accounts/NULLIF(t.ta,0),3) percent_of_daily_page_accounts FROM agg a JOIN totals t USING(occurred_on)''')
daily('feature_event','feature','feature_id'); daily('page_event','page','page_id')
put('int_pendo__guide_alltime_metrics','''SELECT guide_id,count(DISTINCT visitor_id) count_visitors,count(DISTINCT account_id) count_accounts,count(*) count_events,min(occurred_at) first_event_at,max(occurred_at) last_event_at,count(DISTINCT CASE WHEN type='shown' THEN visitor_id END) count_visitors_shown,count(DISTINCT CASE WHEN type='dismissed' THEN visitor_id END) count_visitors_dismissed,count(DISTINCT CASE WHEN type='advanced' THEN visitor_id END) count_visitors_advanced,count(DISTINCT CASE WHEN type='completed' THEN visitor_id END) count_visitors_completed,count(DISTINCT CASE WHEN type='snoozed' THEN visitor_id END) count_visitors_snoozed FROM staging.stg_pendo__guide_event GROUP BY guide_id''')
put('int_pendo__guide_daily_metrics','''WITH b AS (SELECT *,CAST(occurred_at AS DATE) occurred_on FROM staging.stg_pendo__guide_event), v AS (SELECT guide_id,visitor_id,min(occurred_on) first_on FROM b GROUP BY 1,2), a AS (SELECT guide_id,account_id,min(occurred_on) first_on FROM b GROUP BY 1,2), g AS (SELECT b.occurred_on,b.guide_id,count(*) count_guide_events,count(DISTINCT b.visitor_id) count_visitors,count(DISTINCT b.account_id) count_accounts,count(DISTINCT CASE WHEN b.occurred_on=v.first_on THEN b.visitor_id END) count_first_time_visitors,count(DISTINCT CASE WHEN b.occurred_on=a.first_on THEN b.visitor_id END) count_first_time_accounts,count(DISTINCT CASE WHEN type='shown' THEN visitor_id END) count_visitors_shown,count(DISTINCT CASE WHEN type='dismissed' THEN visitor_id END) count_visitors_dismissed,count(DISTINCT CASE WHEN type='advanced' THEN visitor_id END) count_visitors_advanced,count(DISTINCT CASE WHEN type='completed' THEN visitor_id END) count_visitors_completed FROM b LEFT JOIN v USING(guide_id,visitor_id) LEFT JOIN a USING(guide_id,account_id) GROUP BY 1,2), t AS (SELECT occurred_on,sum(count_visitors) tv,sum(count_accounts) ta FROM g GROUP BY 1) SELECT g.occurred_on,g.guide_id,g.count_guide_events,g.count_visitors,g.count_accounts,g.count_first_time_visitors,g.count_first_time_accounts,g.count_visitors-g.count_first_time_visitors count_return_visitors,g.count_accounts-g.count_first_time_accounts count_return_accounts,round(100*g.count_visitors/NULLIF(t.tv,0),3) percent_of_daily_guide_visitors,round(100*g.count_accounts/NULLIF(t.ta,0),3) percent_of_daily_guide_accounts,g.count_visitors_shown,g.count_visitors_dismissed,g.count_visitors_advanced,g.count_visitors_completed FROM g JOIN t USING(occurred_on)''')
put('int_pendo__visitor_daily_metrics','''WITH e AS (SELECT CAST(occurred_at AS DATE) occurred_on,visitor_id,sum(num_events) sum_events,sum(num_minutes) sum_minutes,count(*) count_event_records FROM staging.stg_pendo__event GROUP BY 1,2), f AS (SELECT CAST(occurred_at AS DATE) occurred_on,visitor_id,count(DISTINCT feature_id) count_features_clicked FROM staging.stg_pendo__feature_event GROUP BY 1,2), p AS (SELECT CAST(occurred_at AS DATE) occurred_on,visitor_id,count(DISTINCT page_id) count_pages_viewed FROM staging.stg_pendo__page_event GROUP BY 1,2) SELECT e.occurred_on,e.visitor_id,e.sum_events,e.sum_minutes,e.count_event_records,coalesce(p.count_pages_viewed,0) count_pages_viewed,coalesce(f.count_features_clicked,0) count_features_clicked FROM e LEFT JOIN f USING(occurred_on,visitor_id) LEFT JOIN p USING(occurred_on,visitor_id)''')
PY
python /tmp/inter.py
```
```json
{
  "event_id": 22,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/22.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 21652,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/22.json",
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
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/25.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1359,
    "decoded_characters": 54
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/25.json",
  "timestamp": "2026-10-25T00:45:25.970884",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "guide_event"
  ],
  "full_original_characters": 3148,
  "retention": "index_and_first_line_only",
  "first_line_original": "python run.py > /tmp/runlog 2>&1; tail -30 /tmp/runlog"
}
```
```json
{
  "event_id": 26,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/26.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1043,
    "decoded_characters": 3094
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/26.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 35

```json
{
  "event_id": 35,
  "agent_command_sequence": 16,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/35.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 25158,
    "decoded_characters": 11930
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/35.json",
  "timestamp": "2026-10-25T00:56:44.126550",
  "target_table_name_hits": [
    "stg_pendo__guide_event"
  ],
  "source_table_name_hits": [
    "guide_event"
  ],
  "full_original_characters": 11930,
  "retention": "full_original"
}
```
```bash
cat > /tmp/marts.py <<'PY'
from pathlib import Path
M=Path('sql/marts')
def put(n,s): (M/(n+'.sql')).write_text(s.strip())
# model names mapped pendo__ prefix stripping run.py
put('account','''WITH v AS (SELECT account_id,count(DISTINCT visitor_id) count_associated_visitors FROM intermediate.int_pendo__latest_visitor_account GROUP BY 1), n AS (SELECT account_id,min(nps_rating) min_nps_rating,max(nps_rating) max_nps_rating,avg(nps_rating) avg_nps_rating FROM intermediate.int_pendo__latest_nps_rating GROUP BY 1), d AS (SELECT account_id,sum(count_active_visitors) count_active_visitors,sum(count_page_viewing_visitors) count_page_viewing_visitors,sum(count_feature_clicking_visitors) count_feature_clicking_visitors,count(DISTINCT occurred_on) count_active_days,count(DISTINCT date_trunc('month',occurred_on)) count_active_months,sum(sum_minutes) sum_minutes,sum(sum_events) sum_events,sum(count_event_records) count_event_records,min(occurred_on) first_event_on,max(occurred_on) last_event_on FROM intermediate.int_pendo__account_daily_metrics GROUP BY 1) SELECT a.*,coalesce(v.count_associated_visitors,0) count_associated_visitors,n.min_nps_rating,n.max_nps_rating,n.avg_nps_rating,coalesce(d.count_active_visitors,0) count_active_visitors,coalesce(d.count_page_viewing_visitors,0) count_page_viewing_visitors,coalesce(d.count_feature_clicking_visitors,0) count_feature_clicking_visitors,coalesce(d.count_active_days,0) count_active_days,coalesce(d.count_active_months,0) count_active_months,coalesce(d.sum_minutes,0) sum_minutes,coalesce(d.sum_events,0) sum_events,coalesce(d.count_event_records,0) count_event_records,coalesce(d.sum_minutes/NULLIF(d.count_active_days,0),0) average_daily_minutes,coalesce(d.sum_events/NULLIF(d.count_active_days,0),0) average_daily_events,d.first_event_on,d.last_event_on FROM intermediate.int_pendo__latest_account a LEFT JOIN v USING(account_id) LEFT JOIN n USING(account_id) LEFT JOIN d USING(account_id)''')
put('visitor','''WITH v AS (SELECT visitor_id,count(*) count_associated_accounts FROM intermediate.int_pendo__latest_visitor_account GROUP BY 1), n AS (SELECT visitor_id,nps_rating FROM intermediate.int_pendo__latest_nps_rating), d AS (SELECT visitor_id,count(DISTINCT occurred_on) count_active_days,count(DISTINCT date_trunc('month',occurred_on)) count_active_months,sum(sum_minutes) sum_minutes,sum(sum_events) sum_events,sum(count_event_records) count_event_records,min(occurred_on) first_event_on,max(occurred_on) last_event_on FROM intermediate.int_pendo__visitor_daily_metrics GROUP BY 1) SELECT l.*,v.count_associated_accounts,n.nps_rating latest_nps_rating,coalesce(d.count_active_days,0) count_active_days,coalesce(d.count_active_months,0) count_active_months,coalesce(d.sum_minutes,0) sum_minutes,coalesce(d.sum_events,0) sum_events,coalesce(d.count_event_records,0) count_event_records,coalesce(d.sum_minutes/NULLIF(d.count_active_days,0),0) average_daily_minutes,coalesce(d.sum_events/NULLIF(d.count_active_days,0),0) average_daily_events,d.first_event_on,d.last_event_on FROM intermediate.int_pendo__latest_visitor l LEFT JOIN v USING(visitor_id) LEFT JOIN n USING(visitor_id) LEFT JOIN d USING(visitor_id)''')
put('feature','''WITH m AS (SELECT feature_id,count(DISTINCT visitor_id) count_visitors,count(DISTINCT account_id) count_accounts,sum(num_events) sum_clicks,count(*) count_click_events,min(occurred_at) first_click_at,max(occurred_at) last_click_at,round(sum(num_minutes)/NULLIF(count(DISTINCT visitor_id),0),3) avg_visitor_minutes,round(sum(num_events)/NULLIF(count(DISTINCT visitor_id),0),3) avg_visitor_events FROM staging.stg_pendo__feature_event GROUP BY 1) SELECT f.*,coalesce(m.count_visitors,0) count_visitors,coalesce(m.count_accounts,0) count_accounts,coalesce(m.sum_clicks,0) sum_clicks,coalesce(m.count_click_events,0) count_click_events,m.first_click_at,m.last_click_at,coalesce(m.avg_visitor_minutes,0) avg_visitor_minutes,coalesce(m.avg_visitor_events,0) avg_visitor_events FROM intermediate.int_pendo__feature_info f LEFT JOIN m USING(feature_id)''')
put('guide','''SELECT g.*,m.count_accounts,m.count_visitors_advanced,m.count_visitors_dismissed,m.count_visitors_shown,m.count_visitors,m.first_event_at,m.last_event_at FROM intermediate.int_pendo__guide_info g LEFT JOIN intermediate.int_pendo__guide_alltime_metrics m USING(guide_id)''')
put('page','''WITH m AS (SELECT page_id,count(DISTINCT visitor_id) count_visitors,count(DISTINCT account_id) count_accounts,sum(num_events) sum_pageviews,count(*) count_pageview_events,min(occurred_at) first_pageview_at,max(occurred_at) last_pageview_at,round(sum(num_minutes)/NULLIF(count(DISTINCT visitor_id),0),3) avg_visitor_minutes,round(sum(num_events)/NULLIF(count(DISTINCT visitor_id),0),3) avg_visitor_pageviews FROM staging.stg_pendo__page_event GROUP BY 1) SELECT p.*,coalesce(m.count_visitors,0) count_visitors,coalesce(m.count_accounts,0) count_accounts,coalesce(m.sum_pageviews,0) sum_pageviews,coalesce(m.count_pageview_events,0) count_pageview_events,m.first_pageview_at,m.last_pageview_at,coalesce(m.avg_visitor_minutes,0) avg_visitor_minutes,coalesce(m.avg_visitor_pageviews,0) avg_visitor_pageviews FROM intermediate.int_pendo__latest_page p LEFT JOIN m USING(page_id)''')
put('feature_event','''WITH w AS (SELECT *,lag(feature_id) OVER(PARTITION BY visitor_id ORDER BY occurred_at) previous_feature_id,lag(occurred_at) OVER(PARTITION BY visitor_id ORDER BY occurred_at) previous_feature_event_at,lag(num_minutes) OVER(PARTITION BY visitor_id ORDER BY occurred_at) previous_feature_num_minutes,lag(num_events) OVER(PARTITION BY visitor_id ORDER BY occurred_at) previous_feature_num_events FROM staging.stg_pendo__feature_event) SELECT w.*,f.feature_name,f.page_id,f.page_name,f.product_area_name,f.group_id product_area_id,f.app_display_name,f.app_platform,p.feature_name previous_feature_name,p.page_id previous_feature_page_id,p.page_name previous_feature_page_name,p.product_area_name previous_feature_product_area_name,p.group_id previous_feature_product_area_id FROM w INNER JOIN intermediate.int_pendo__feature_info f USING(feature_id) LEFT JOIN intermediate.int_pendo__feature_info p ON w.previous_feature_id=p.feature_id''')
put('guide_event','''SELECT e.*,g.guide_name,g.app_display_name,g.app_platform FROM staging.stg_pendo__guide_event e INNER JOIN intermediate.int_pendo__guide_info g USING(guide_id)''')
put('page_event','''WITH w AS (SELECT *,lag(page_id) OVER(PARTITION BY visitor_id ORDER BY occurred_at) previous_page_id,lag(occurred_at) OVER(PARTITION BY visitor_id ORDER BY occurred_at) previous_page_event_at,lag(num_minutes) OVER(PARTITION BY visitor_id ORDER BY occurred_at) previous_page_num_minutes,lag(num_events) OVER(PARTITION BY visitor_id ORDER BY occurred_at) previous_page_num_events FROM staging.stg_pendo__page_event) SELECT w.*,p.page_name,p.group_id product_area_id,pp.page_name previous_page_name,pp.group_id previous_page_product_area_id FROM w INNER JOIN intermediate.int_pendo__latest_page p USING(page_id) LEFT JOIN intermediate.int_pendo__latest_page pp ON w.previous_page_id=pp.page_id''')
# Simple full model aliases then enrich where sufficient
put('account_daily_metrics','''WITH starts AS (SELECT account_id,min(occurred_on) first_event_on FROM intermediate.int_pendo__account_daily_metrics GROUP BY 1), spine AS (SELECT s.account_id,c.date_day FROM starts s CROSS JOIN intermediate.int_pendo__calendar_spine c WHERE c.date_day BETWEEN s.first_event_on AND current_date) SELECT s.date_day,s.account_id,d.count_active_visitors,d.sum_minutes,d.sum_events,d.count_event_records,d.count_pages_viewed,d.count_features_clicked,d.count_page_viewing_visitors,d.count_feature_clicking_visitors FROM spine s LEFT JOIN intermediate.int_pendo__account_daily_metrics d ON s.account_id=d.account_id AND s.date_day=d.occurred_on''')
put('feature_daily_metrics','''WITH f AS (SELECT feature_id,feature_name,group_id,product_area_name,page_id,page_name,CAST(created_at AS DATE) created_on,coalesce(CAST(valid_through AS DATE),current_date) valid_on FROM intermediate.int_pendo__feature_info) SELECT c.date_day,f.feature_id,f.feature_name,f.group_id,f.product_area_name,f.page_id,f.page_name,coalesce(m.sum_clicks,0) sum_clicks,coalesce(m.count_visitors,0) count_visitors,coalesce(m.count_accounts,0) count_accounts,coalesce(m.count_first_time_visitors,0) count_first_time_visitors,coalesce(m.count_first_time_accounts,0) count_first_time_accounts,coalesce(m.count_return_visitors,0) count_return_visitors,coalesce(m.count_return_accounts,0) count_return_accounts,coalesce(m.avg_daily_minutes_per_visitor,0) avg_daily_minutes_per_visitor,coalesce(m.avg_daily_clicks_per_visitor,0) avg_daily_clicks_per_visitor,coalesce(m.percent_of_daily_feature_clicks,0) percent_of_daily_feature_clicks,coalesce(m.percent_of_daily_feature_visitors,0) percent_of_daily_feature_visitors,coalesce(m.percent_of_daily_feature_accounts,0) percent_of_daily_feature_accounts,coalesce(m.count_click_events,0) count_click_events FROM f CROSS JOIN intermediate.int_pendo__calendar_spine c LEFT JOIN intermediate.int_pendo__feature_daily_metrics m ON m.feature_id=f.feature_id AND m.occurred_on=c.date_day WHERE c.date_day BETWEEN f.created_on AND f.valid_on''')
put('guide_daily_metrics','''WITH g AS (SELECT guide_id,guide_name,CAST(created_at AS DATE) created_on FROM intermediate.int_pendo__guide_info) SELECT c.date_day,g.guide_id,g.guide_name,m.count_accounts,m.count_visitors FROM g CROSS JOIN intermediate.int_pendo__calendar_spine c LEFT JOIN intermediate.int_pendo__guide_daily_metrics m ON m.guide_id=g.guide_id AND m.occurred_on=c.date_day WHERE c.date_day BETWEEN g.created_on AND current_date''')
put('page_daily_metrics','''WITH p AS (SELECT page_id,page_name,group_id,CAST(created_at AS DATE) created_on,coalesce(CAST(valid_through AS DATE),current_date) valid_on FROM intermediate.int_pendo__latest_page) SELECT c.date_day,p.page_id,p.page_name,p.group_id,coalesce(m.sum_pageviews,0) sum_pageviews,coalesce(m.count_visitors,0) count_visitors,coalesce(m.count_accounts,0) count_accounts,coalesce(m.count_first_time_visitors,0) count_first_time_visitors,coalesce(m.count_first_time_accounts,0) count_first_time_accounts,coalesce(m.count_return_visitors,0) count_return_visitors,coalesce(m.count_return_accounts,0) count_return_accounts,coalesce(m.avg_daily_minutes_per_visitor,0) avg_daily_minutes_per_visitor,coalesce(m.avg_daily_pageviews_per_visitor,0) avg_daily_pageviews_per_visitor,coalesce(m.percent_of_daily_pageviews,0) percent_of_daily_pageviews,coalesce(m.percent_of_daily_page_visitors,0) percent_of_daily_page_visitors,coalesce(m.percent_of_daily_page_accounts,0) percent_of_daily_page_accounts,coalesce(m.count_pageview_events,0) count_pageview_events FROM p CROSS JOIN intermediate.int_pendo__calendar_spine c LEFT JOIN intermediate.int_pendo__page_daily_metrics m ON m.page_id=p.page_id AND m.occurred_on=c.date_day WHERE c.date_day BETWEEN p.created_on AND p.valid_on''')
put('visitor_daily_metrics','''WITH s AS (SELECT visitor_id,min(occurred_on) first_on FROM intermediate.int_pendo__visitor_daily_metrics WHERE occurred_on IS NOT NULL GROUP BY 1) SELECT c.date_day,s.visitor_id,m.sum_minutes,m.sum_events,m.count_event_records,m.count_pages_viewed,m.count_features_clicked FROM s CROSS JOIN intermediate.int_pendo__calendar_spine c LEFT JOIN intermediate.int_pendo__visitor_daily_metrics m ON m.visitor_id=s.visitor_id AND m.occurred_on=c.date_day WHERE c.date_day BETWEEN s.first_on AND current_date''')
put('visitor_feature','''SELECT visitor_id,feature_id,min(occurred_at) first_click_at,max(occurred_at) last_click_at,sum(num_events) sum_clicks,sum(num_minutes) sum_minutes,round(sum(num_minutes)/NULLIF(count(DISTINCT CAST(occurred_at AS DATE)),0),3) avg_daily_minutes,count(DISTINCT CAST(occurred_at AS DATE)) count_active_days,count(*) count_click_events FROM staging.stg_pendo__feature_event GROUP BY 1,2''')
PY
python /tmp/marts.py
```
```json
{
  "event_id": 36,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/36.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 24841,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/36.json",
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

## result_md_table_sentences

```json
{
  "present": false,
  "searched_path": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/result.md",
  "sentences": []
}
```

## original_files

```json
{
  "paths": [
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/10.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/13.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/14.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/17.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/18.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/19.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/20.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/21.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/22.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/25.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/26.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/35.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/36.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/9.json",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql",
    "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml",
    "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb",
    "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql"
  ],
  "archive": "/home/katherine/Assumption_Ledger/traces/dacomp_deimpl_prev.tar.gz",
  "gold_SQL_search_root": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql",
  "gold_SQL_search_names": [
    "stg_pendo__guide_event",
    "stg_pendo__guide_event"
  ],
  "source_fingerprints": "records/012_input_before.json"
}
```
