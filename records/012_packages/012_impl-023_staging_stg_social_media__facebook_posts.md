# impl-023 / stg_social_media__facebook_posts

## basic_information

```json
{
  "task": "impl-023",
  "layer": "staging",
  "table": "stg_social_media__facebook_posts",
  "status": "待标注",
  "difference_source": {
    "kind": "date_aligned_011",
    "record": "records/011_table_alignment.jsonl",
    "detail_record": "records/011_alignment_impl-023.json",
    "candidate_date": "2025-10-17",
    "selection_reason": "011 执行与比较成功，使用该表已验证日期；优先 010 同题候选 / 共同兼容日，再按日期升序"
  },
  "status_record": "records/012_statuses.jsonl",
  "package_scope": "仅原文和机械统计；未概括轨迹、未推测原因"
}
```

## contract_specification

```json
{
  "source_path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml",
  "source_sha256": "385d3015ad05be572807bc2e1cdd7e520b96f3a4f279c3627821c15facf1b63f",
  "parse_mode": "strict",
  "requested_table": "stg_social_media__facebook_posts",
  "status": "found"
}
```
```json
{
  "yaml_path": [
    "staging_contract",
    "tables",
    3
  ],
  "start_line": 205,
  "end_line": 255
}
```
```yaml
    - name: stg_social_media__facebook_posts
      description: "Published, visible Facebook posts joined to page info, standardized fields for analysis; recent 2-year window."
      source_table: 
        - raw.facebook_pages_post_history
        - raw.facebook_pages_page_data
      columns:
        - name: id
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
          description: "From created_time."
        - name: post_id
          data_type: VARCHAR
          description: "CAST(id)."
        - name: post_message
          data_type: VARCHAR
          description: "COALESCE(message, '')."
        - name: page_id
          data_type: VARCHAR
          description: "CAST(page_id)."
        - name: page_name
          data_type: VARCHAR
          validation_rules:
            - rule: "page_name IS NOT NULL AND page_name <> ''"
              on_failure: correct  
          description: "Defaults to 'Unknown Page' when page name is missing."
        - name: page_username
          data_type: VARCHAR
        - name: page_category
          data_type: VARCHAR
        - name: page_followers
          data_type: BIGINT
        - name: shares
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
          description: "Default 0 in staging."
        - name: status_type
          data_type: VARCHAR
        - name: privacy_value
          data_type: VARCHAR
        - name: is_eligible_for_promotion
          data_type: BOOLEAN
        - name: is_instagram_eligible
          data_type: BOOLEAN
        - name: post_url
          data_type: VARCHAR
          validation_rules:
            - rule: "post_url ~ '^https://facebook\\.com/.+'"
              on_failure: correct

```

## agent_final_SQL

```json
{
  "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
  "sha256": "307c68e4a012050d9e198b5ed8f01c9da926f0cf637de3c7d898194ae2703b91",
  "start_line": 1,
  "end_line": 32
}
```
```sql
with post_metrics as (
    select post_id, max(post_impressions) as impressions
    from raw.facebook_pages_lifetime_post_metrics
    group by post_id
), pages as (
    select *, row_number() over (partition by id order by _fivetran_synced desc nulls last) as row_num
    from raw.facebook_pages_page_data
)
select
    p.id::varchar as id,
    p.created_time::timestamp as created_timestamp,
    p.id::varchar as post_id,
    coalesce(p.message, '')::varchar as post_message,
    cast(p.page_id as varchar) as page_id,
    coalesce(nullif(pg.name, ''), 'Unknown Page')::varchar as page_name,
    pg.username::varchar as page_username,
    pg.category::varchar as page_category,
    coalesce(try_cast(pg.fan_count as bigint), 0)::bigint as page_followers,
    coalesce(p.share_count, 0)::bigint as shares,
    coalesce(pm.impressions, 0)::bigint as impressions,
    p.status_type::varchar as status_type,
    p.privacy_value::varchar as privacy_value,
    p.is_eligible_for_promotion::boolean as is_eligible_for_promotion,
    p.is_instagram_eligible::boolean as is_instagram_eligible,
    ('https://facebook.com/' || p.id)::varchar as post_url
from raw.facebook_pages_post_history p
left join pages pg on p.page_id = pg.id and pg.row_num = 1
left join post_metrics pm on pm.post_id = p.id
where coalesce(p.is_published, false)
  and not coalesce(p.is_hidden, false)
  and p.created_time >= current_date - interval '2 years'
  and p.created_time is not null
```

## gold_SQL_仅供定位差异

```json
{
  "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
  "sha256": "ecc061ed53241d6ab1d83cc939d2673405bea6359a650d1b200fb7325443526c",
  "start_line": 1,
  "end_line": 58
}
```
```sql
-- Facebook posts staging table - Simplified version based on actual columns
-- Created based on real table structure analysis

WITH source_posts AS (
    SELECT
        id,
        created_time,
        page_id,
        status_type,
        message,
        share_count,
        is_published,
        privacy_value,
        is_hidden,
        is_eligible_for_promotion,
        is_instagram_eligible
    FROM raw.facebook_pages_post_history
    WHERE is_published = TRUE -- Only published posts
    AND is_hidden = FALSE -- Not hidden
    AND created_time >= CURRENT_DATE - INTERVAL '2 years' -- Recent posts only
),

-- Get page information
page_info AS (
    SELECT
        id AS page_id,
        name AS page_name,
        username,
        website,
        category,
        fan_count,
        talking_about_count,
        created_time AS page_created_time
    FROM raw.facebook_pages_page_data
    WHERE (_fivetran_deleted = FALSE OR _fivetran_deleted IS NULL)
        AND name IS NOT NULL -- Ensure page has a name
)

-- Simplified join just to get basic page info
SELECT
    sp.id,
    sp.created_time AS created_timestamp,
    CAST(sp.id AS VARCHAR) AS post_id,
    COALESCE(sp.message, '') AS post_message,
    CAST(sp.page_id AS VARCHAR) AS page_id,
    COALESCE(pi.page_name, 'Unknown Page') AS page_name,
    pi.username AS page_username,
    pi.category AS page_category,
    COALESCE(pi.fan_count, 0) AS page_followers,
    COALESCE(sp.share_count, 0) AS shares,
    0 AS impressions,
    sp.status_type,
    sp.privacy_value,
    sp.is_eligible_for_promotion,
    sp.is_instagram_eligible,
    CONCAT('https://facebook.com/', COALESCE(pi.page_id, sp.page_id), '/posts/', sp.id) AS post_url
FROM source_posts sp
LEFT JOIN page_info pi ON sp.page_id = pi.page_id
```

## differences

```json
{
  "kind": "date_aligned_011",
  "record": "records/011_table_alignment.jsonl",
  "detail_record": "records/011_alignment_impl-023.json",
  "prediction_database": "/home/katherine/Assumption_Ledger/data/011_agent_alignment/impl-023/stg_social_media__facebook_posts_2025-10-17.duckdb",
  "gold_database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb",
  "actual_schema": "staging",
  "table": "stg_social_media__facebook_posts",
  "candidate_date": "2025-10-17",
  "comparison_columns": [
    "created_timestamp",
    "id",
    "impressions",
    "is_eligible_for_promotion",
    "is_instagram_eligible",
    "page_category",
    "page_followers",
    "page_id",
    "page_name",
    "page_username",
    "post_id",
    "post_message",
    "post_url",
    "privacy_value",
    "shares",
    "status_type"
  ],
  "key_columns": [
    "id"
  ],
  "prediction_rows": 138,
  "gold_rows": 138,
  "row_delta": 0,
  "key_statistics": {
    "pred_distinct_keys": 138,
    "gold_distinct_keys": 138,
    "pred_duplicate_key_groups": 0,
    "gold_duplicate_key_groups": 0,
    "pred_only_keys": 0,
    "gold_only_keys": 0,
    "shared_keys": 138,
    "shared_nonunique_key_groups": 0
  },
  "l0_column_differences": [
    {
      "column": "id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "created_timestamp",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "impressions",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "is_eligible_for_promotion",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "is_instagram_eligible",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "page_category",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "page_followers",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 138,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 138,
      "pred_unmatched_value_occurrences": 138,
      "gold_unmatched_value_occurrences": 138,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "page_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "page_name",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "page_username",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "post_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "post_message",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "post_url",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 138,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 138,
      "pred_unmatched_value_occurrences": 138,
      "gold_unmatched_value_occurrences": 138,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "privacy_value",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "shares",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "status_type",
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
      "column": "created_timestamp",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "impressions",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "is_eligible_for_promotion",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "is_instagram_eligible",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "page_category",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "page_followers",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "page_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "page_name",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "page_username",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "post_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "post_message",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "post_url",
      "one_to_one_mismatch_rows": 138,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 138,
      "pred_unmatched_value_occurrences": 138,
      "gold_unmatched_value_occurrences": 138,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "privacy_value",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "shares",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "status_type",
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
  "selection_reason": "011 执行与比较成功，使用该表已验证日期；优先 010 同题候选 / 共同兼容日，再按日期升序",
  "value_representation": "Unmodified DuckDB CAST AS VARCHAR; SQL NULL is JSON null. Keys use the unchanged historical L0 normalization.",
  "new_queries_only_read_existing_results": true,
  "one_side_key_examples": {
    "prediction_only": [],
    "gold_only": []
  },
  "column_details": [
    {
      "column": "id",
      "l0_counts_verbatim": {
        "column": "id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "id",
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
      "column": "created_timestamp",
      "l0_counts_verbatim": {
        "column": "created_timestamp",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "created_timestamp",
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
      "column": "impressions",
      "l0_counts_verbatim": {
        "column": "impressions",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "impressions",
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
      "gold_actual_type": "INTEGER"
    },
    {
      "column": "is_eligible_for_promotion",
      "l0_counts_verbatim": {
        "column": "is_eligible_for_promotion",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "is_eligible_for_promotion",
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
      "column": "is_instagram_eligible",
      "l0_counts_verbatim": {
        "column": "is_instagram_eligible",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "is_instagram_eligible",
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
      "column": "page_category",
      "l0_counts_verbatim": {
        "column": "page_category",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "page_category",
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
      "column": "page_followers",
      "l0_counts_verbatim": {
        "column": "page_followers",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 138,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 138,
        "pred_unmatched_value_occurrences": 138,
        "gold_unmatched_value_occurrences": 138,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "page_followers",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "id": "514435155248890_7150369778798122"
          },
          "agent_key_raw_text": {
            "id": "514435155248890_7150369778798122"
          },
          "gold_key_raw_text": {
            "id": "514435155248890_7150369778798122"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "15072",
          "gold_value": "15072.0"
        },
        {
          "key_normalized": {
            "id": "514435155248892_2419193699044444"
          },
          "agent_key_raw_text": {
            "id": "514435155248892_2419193699044444"
          },
          "gold_key_raw_text": {
            "id": "514435155248892_2419193699044444"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "4140",
          "gold_value": "4140.0"
        },
        {
          "key_normalized": {
            "id": "514435155248895_2895703078598069"
          },
          "agent_key_raw_text": {
            "id": "514435155248895_2895703078598069"
          },
          "gold_key_raw_text": {
            "id": "514435155248895_2895703078598069"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "6710",
          "gold_value": "6710.0"
        },
        {
          "key_normalized": {
            "id": "514435155248917_6549259288442334"
          },
          "agent_key_raw_text": {
            "id": "514435155248917_6549259288442334"
          },
          "gold_key_raw_text": {
            "id": "514435155248917_6549259288442334"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "2110",
          "gold_value": "2110.0"
        },
        {
          "key_normalized": {
            "id": "514435155248918_4843126958870753"
          },
          "agent_key_raw_text": {
            "id": "514435155248918_4843126958870753"
          },
          "gold_key_raw_text": {
            "id": "514435155248918_4843126958870753"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "8348",
          "gold_value": "8348.0"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 138,
        "pred_unmatched_value_occurrences": 138,
        "gold_unmatched_value_occurrences": 138
      },
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "page_id",
      "l0_counts_verbatim": {
        "column": "page_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "page_id",
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
      "column": "page_name",
      "l0_counts_verbatim": {
        "column": "page_name",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "page_name",
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
      "column": "page_username",
      "l0_counts_verbatim": {
        "column": "page_username",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "page_username",
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
      "column": "post_id",
      "l0_counts_verbatim": {
        "column": "post_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "post_id",
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
      "column": "post_message",
      "l0_counts_verbatim": {
        "column": "post_message",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "post_message",
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
      "column": "post_url",
      "l0_counts_verbatim": {
        "column": "post_url",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 138,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 138,
        "pred_unmatched_value_occurrences": 138,
        "gold_unmatched_value_occurrences": 138,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "post_url",
        "one_to_one_mismatch_rows": 138,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 138,
        "pred_unmatched_value_occurrences": 138,
        "gold_unmatched_value_occurrences": 138,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "id": "514435155248890_7150369778798122"
          },
          "agent_key_raw_text": {
            "id": "514435155248890_7150369778798122"
          },
          "gold_key_raw_text": {
            "id": "514435155248890_7150369778798122"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "https://facebook.com/514435155248890_7150369778798122",
          "gold_value": "https://facebook.com/514435155250268/posts/514435155248890_7150369778798122"
        },
        {
          "key_normalized": {
            "id": "514435155248892_2419193699044444"
          },
          "agent_key_raw_text": {
            "id": "514435155248892_2419193699044444"
          },
          "gold_key_raw_text": {
            "id": "514435155248892_2419193699044444"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "https://facebook.com/514435155248892_2419193699044444",
          "gold_value": "https://facebook.com/514435155251029/posts/514435155248892_2419193699044444"
        },
        {
          "key_normalized": {
            "id": "514435155248895_2895703078598069"
          },
          "agent_key_raw_text": {
            "id": "514435155248895_2895703078598069"
          },
          "gold_key_raw_text": {
            "id": "514435155248895_2895703078598069"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "https://facebook.com/514435155248895_2895703078598069",
          "gold_value": "https://facebook.com/514435155250947/posts/514435155248895_2895703078598069"
        },
        {
          "key_normalized": {
            "id": "514435155248917_6549259288442334"
          },
          "agent_key_raw_text": {
            "id": "514435155248917_6549259288442334"
          },
          "gold_key_raw_text": {
            "id": "514435155248917_6549259288442334"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "https://facebook.com/514435155248917_6549259288442334",
          "gold_value": "https://facebook.com/514435155250799/posts/514435155248917_6549259288442334"
        },
        {
          "key_normalized": {
            "id": "514435155248918_4843126958870753"
          },
          "agent_key_raw_text": {
            "id": "514435155248918_4843126958870753"
          },
          "gold_key_raw_text": {
            "id": "514435155248918_4843126958870753"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "https://facebook.com/514435155248918_4843126958870753",
          "gold_value": "https://facebook.com/514435155250634/posts/514435155248918_4843126958870753"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 138,
        "pred_unmatched_value_occurrences": 138,
        "gold_unmatched_value_occurrences": 138
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "privacy_value",
      "l0_counts_verbatim": {
        "column": "privacy_value",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "privacy_value",
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
      "column": "shares",
      "l0_counts_verbatim": {
        "column": "shares",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "shares",
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
      "column": "status_type",
      "l0_counts_verbatim": {
        "column": "status_type",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "status_type",
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
    }
  ]
}
```

## agent_constraints_006

```json
{
  "source_record": "records/006_contract_impl-023.json",
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
    "row_count": 0,
    "checks": {
      "grain": [],
      "primary_key": [],
      "not_null": [],
      "unique": []
    },
    "actual_table": "stg_social_media__facebook_posts",
    "actual_columns": [
      "id",
      "created_timestamp",
      "post_id",
      "post_message",
      "page_id",
      "page_name",
      "page_username",
      "page_category",
      "page_followers",
      "shares",
      "impressions",
      "status_type",
      "privacy_value",
      "is_eligible_for_promotion",
      "is_instagram_eligible",
      "post_url"
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
    "task": "impl-023",
    "layer": "staging",
    "table": "stg_social_media__facebook_posts",
    "logical_contract_table": "stg_social_media__facebook_posts",
    "delivery_name_mapping_evidence": [],
    "inventory_sources": {
      "retained_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb",
      "present_in_database": true,
      "agent_final_sql_files": [
        "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql"
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
          "007_prediction_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb"
        }
      ],
      "status": "待标注",
      "comparison_lookup_layer": "staging",
      "comparison_lookup_table": "stg_social_media__facebook_posts",
      "actual_gold_relation_exists": true
    },
    "contract": {
      "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml",
      "blocks": [
        {
          "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml",
          "start_line": 205,
          "end_line": 254,
          "original_text": "    - name: stg_social_media__facebook_posts\n      description: \"Published, visible Facebook posts joined to page info, standardized fields for analysis; recent 2-year window.\"\n      source_table: \n        - raw.facebook_pages_post_history\n        - raw.facebook_pages_page_data\n      columns:\n        - name: id\n          data_type: VARCHAR\n        - name: created_timestamp\n          data_type: TIMESTAMP\n          description: \"From created_time.\"\n        - name: post_id\n          data_type: VARCHAR\n          description: \"CAST(id).\"\n        - name: post_message\n          data_type: VARCHAR\n          description: \"COALESCE(message, '').\"\n        - name: page_id\n          data_type: VARCHAR\n          description: \"CAST(page_id).\"\n        - name: page_name\n          data_type: VARCHAR\n          validation_rules:\n            - rule: \"page_name IS NOT NULL AND page_name <> ''\"\n              on_failure: correct  \n          description: \"Defaults to 'Unknown Page' when page name is missing.\"\n        - name: page_username\n          data_type: VARCHAR\n        - name: page_category\n          data_type: VARCHAR\n        - name: page_followers\n          data_type: BIGINT\n        - name: shares\n          data_type: BIGINT\n        - name: impressions\n          data_type: BIGINT\n          description: \"Default 0 in staging.\"\n        - name: status_type\n          data_type: VARCHAR\n        - name: privacy_value\n          data_type: VARCHAR\n        - name: is_eligible_for_promotion\n          data_type: BOOLEAN\n        - name: is_instagram_eligible\n          data_type: BOOLEAN\n        - name: post_url\n          data_type: VARCHAR\n          validation_rules:\n            - rule: \"post_url ~ '^https://facebook\\\\.com/.+'\"\n              on_failure: correct\n",
          "yaml_path": [
            "staging_contract",
            "tables",
            3
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
          "name": "id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "created_timestamp",
          "type": "TIMESTAMP",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "post_id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "post_message",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "page_id",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "page_name",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "page_username",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "page_category",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "page_followers",
          "type": "BIGINT",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "shares",
          "type": "BIGINT",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "impressions",
          "type": "BIGINT",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "status_type",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "privacy_value",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "is_eligible_for_promotion",
          "type": "BOOLEAN",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "is_instagram_eligible",
          "type": "BOOLEAN",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        },
        {
          "name": "post_url",
          "type": "VARCHAR",
          "nonnull_rows": 0,
          "sql_null_rows": 0
        }
      ],
      "all_null_columns": [],
      "constant_nonnull_columns": [],
      "equal_column_groups": [],
      "profile_sql": "SELECT count(*),count(\"id\"),min(CAST(\"id\" AS VARCHAR)),max(CAST(\"id\" AS VARCHAR)),sum(hash(CAST(\"id\" AS VARCHAR))),count(\"created_timestamp\"),min(CAST(\"created_timestamp\" AS VARCHAR)),max(CAST(\"created_timestamp\" AS VARCHAR)),sum(hash(CAST(\"created_timestamp\" AS VARCHAR))),count(\"post_id\"),min(CAST(\"post_id\" AS VARCHAR)),max(CAST(\"post_id\" AS VARCHAR)),sum(hash(CAST(\"post_id\" AS VARCHAR))),count(\"post_message\"),min(CAST(\"post_message\" AS VARCHAR)),max(CAST(\"post_message\" AS VARCHAR)),sum(hash(CAST(\"post_message\" AS VARCHAR))),count(\"page_id\"),min(CAST(\"page_id\" AS VARCHAR)),max(CAST(\"page_id\" AS VARCHAR)),sum(hash(CAST(\"page_id\" AS VARCHAR))),count(\"page_name\"),min(CAST(\"page_name\" AS VARCHAR)),max(CAST(\"page_name\" AS VARCHAR)),sum(hash(CAST(\"page_name\" AS VARCHAR))),count(\"page_username\"),min(CAST(\"page_username\" AS VARCHAR)),max(CAST(\"page_username\" AS VARCHAR)),sum(hash(CAST(\"page_username\" AS VARCHAR))),count(\"page_category\"),min(CAST(\"page_category\" AS VARCHAR)),max(CAST(\"page_category\" AS VARCHAR)),sum(hash(CAST(\"page_category\" AS VARCHAR))),count(\"page_followers\"),min(CAST(\"page_followers\" AS VARCHAR)),max(CAST(\"page_followers\" AS VARCHAR)),sum(hash(CAST(\"page_followers\" AS VARCHAR))),count(\"shares\"),min(CAST(\"shares\" AS VARCHAR)),max(CAST(\"shares\" AS VARCHAR)),sum(hash(CAST(\"shares\" AS VARCHAR))),count(\"impressions\"),min(CAST(\"impressions\" AS VARCHAR)),max(CAST(\"impressions\" AS VARCHAR)),sum(hash(CAST(\"impressions\" AS VARCHAR))),count(\"status_type\"),min(CAST(\"status_type\" AS VARCHAR)),max(CAST(\"status_type\" AS VARCHAR)),sum(hash(CAST(\"status_type\" AS VARCHAR))),count(\"privacy_value\"),min(CAST(\"privacy_value\" AS VARCHAR)),max(CAST(\"privacy_value\" AS VARCHAR)),sum(hash(CAST(\"privacy_value\" AS VARCHAR))),count(\"is_eligible_for_promotion\"),min(CAST(\"is_eligible_for_promotion\" AS VARCHAR)),max(CAST(\"is_eligible_for_promotion\" AS VARCHAR)),sum(hash(CAST(\"is_eligible_for_promotion\" AS VARCHAR))),count(\"is_instagram_eligible\"),min(CAST(\"is_instagram_eligible\" AS VARCHAR)),max(CAST(\"is_instagram_eligible\" AS VARCHAR)),sum(hash(CAST(\"is_instagram_eligible\" AS VARCHAR))),count(\"post_url\"),min(CAST(\"post_url\" AS VARCHAR)),max(CAST(\"post_url\" AS VARCHAR)),sum(hash(CAST(\"post_url\" AS VARCHAR))) FROM \"staging\".\"stg_social_media__facebook_posts\"",
      "equal_column_confirmation_queries": [],
      "equality_policy": "exact CAST AS VARCHAR per row; no trim/case/numeric/date normalization; both NULL ignored; at least one nonnull equal row; one-sided NULL differs",
      "actual_schema": "staging",
      "actual_table": "stg_social_media__facebook_posts",
      "relation_type": "BASE TABLE"
    },
    "agent_sql": [
      {
        "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
        "status": "parsed",
        "parser": "30.25.0",
        "sources": [
          {
            "name": "raw.facebook_pages_post_history",
            "canonical": "raw.facebook_pages_post_history",
            "locations": [
              {
                "line": 26,
                "end_line": 26
              }
            ]
          },
          {
            "name": "raw.facebook_pages_page_data",
            "canonical": "raw.facebook_pages_page_data",
            "locations": [
              {
                "line": 7,
                "end_line": 7
              }
            ]
          },
          {
            "name": "raw.facebook_pages_lifetime_post_metrics",
            "canonical": "raw.facebook_pages_lifetime_post_metrics",
            "locations": [
              {
                "line": 3,
                "end_line": 3
              }
            ]
          }
        ],
        "unresolved_source_expressions": [],
        "row_generator_expressions": [],
        "outputs": [
          {
            "name": "id",
            "alternatives": [
              {
                "expression_sql": "CAST(p.id AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 10,
                "end_line": 10,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "id",
            "retained_output_ordinal": 1
          },
          {
            "name": "created_timestamp",
            "alternatives": [
              {
                "expression_sql": "CAST(p.created_time AS TIMESTAMP)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 11,
                "end_line": 11,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "created_timestamp",
            "retained_output_ordinal": 2
          },
          {
            "name": "post_id",
            "alternatives": [
              {
                "expression_sql": "CAST(p.id AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 12,
                "end_line": 12,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "post_id",
            "retained_output_ordinal": 3
          },
          {
            "name": "post_message",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(p.message, '') AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 13,
                "end_line": 13,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "post_message",
            "retained_output_ordinal": 4
          },
          {
            "name": "page_id",
            "alternatives": [
              {
                "expression_sql": "CAST(p.page_id AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 14,
                "end_line": 14,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "page_id",
            "retained_output_ordinal": 5
          },
          {
            "name": "page_name",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(NULLIF(pg.name, ''), 'Unknown Page') AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 15,
                "end_line": 15,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "page_name",
            "retained_output_ordinal": 6
          },
          {
            "name": "page_username",
            "alternatives": [
              {
                "expression_sql": "CAST(pg.username AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 16,
                "end_line": 16,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "page_username",
            "retained_output_ordinal": 7
          },
          {
            "name": "page_category",
            "alternatives": [
              {
                "expression_sql": "CAST(pg.category AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 17,
                "end_line": 17,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "page_category",
            "retained_output_ordinal": 8
          },
          {
            "name": "page_followers",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(TRY_CAST(pg.fan_count AS BIGINT), 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 18,
                "end_line": 18,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "page_followers",
            "retained_output_ordinal": 9
          },
          {
            "name": "shares",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(p.share_count, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 19,
                "end_line": 19,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "shares",
            "retained_output_ordinal": 10
          },
          {
            "name": "impressions",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(pm.impressions, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 20,
                "end_line": 20,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "impressions",
            "retained_output_ordinal": 11
          },
          {
            "name": "status_type",
            "alternatives": [
              {
                "expression_sql": "CAST(p.status_type AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 21,
                "end_line": 21,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "status_type",
            "retained_output_ordinal": 12
          },
          {
            "name": "privacy_value",
            "alternatives": [
              {
                "expression_sql": "CAST(p.privacy_value AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 22,
                "end_line": 22,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "privacy_value",
            "retained_output_ordinal": 13
          },
          {
            "name": "is_eligible_for_promotion",
            "alternatives": [
              {
                "expression_sql": "CAST(p.is_eligible_for_promotion AS BOOLEAN)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 23,
                "end_line": 23,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "is_eligible_for_promotion",
            "retained_output_ordinal": 14
          },
          {
            "name": "is_instagram_eligible",
            "alternatives": [
              {
                "expression_sql": "CAST(p.is_instagram_eligible AS BOOLEAN)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 24,
                "end_line": 24,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "is_instagram_eligible",
            "retained_output_ordinal": 15
          },
          {
            "name": "post_url",
            "alternatives": [
              {
                "expression_sql": "CAST(('https://facebook.com/' || p.id) AS TEXT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
                "line": 25,
                "end_line": 25,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "post_url",
            "retained_output_ordinal": 16
          }
        ],
        "null_literal_outputs": [],
        "constant_literal_outputs": [],
        "runtime_hits": [
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
            "line": 31,
            "column": 25,
            "matched_text": "current_date",
            "line_text": "  and p.created_time >= current_date - interval '2 years'",
            "context": "code"
          }
        ]
      }
    ],
    "source_comparison": {
      "contract": {
        "status": "specified",
        "references": [
          {
            "name": "raw.facebook_pages_post_history",
            "canonical": "raw.facebook_pages_post_history",
            "basis": "source_table",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml",
            "block_start_line": 205
          },
          {
            "name": "raw.facebook_pages_page_data",
            "canonical": "raw.facebook_pages_page_data",
            "basis": "source_table",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml",
            "block_start_line": 205
          },
          {
            "name": "raw.facebook_pages_post_history",
            "canonical": "raw.facebook_pages_post_history",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml",
            "line": 208,
            "line_text": "        - raw.facebook_pages_post_history"
          },
          {
            "name": "raw.facebook_pages_page_data",
            "canonical": "raw.facebook_pages_page_data",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml",
            "line": 209,
            "line_text": "        - raw.facebook_pages_page_data"
          }
        ],
        "canonical_names": [
          "raw.facebook_pages_page_data",
          "raw.facebook_pages_post_history"
        ]
      },
      "agent_direct_read_sources": [
        "raw.facebook_pages_lifetime_post_metrics",
        "raw.facebook_pages_page_data",
        "raw.facebook_pages_post_history"
      ],
      "scope": "direct physical relation references through reachable local CTE/subqueries; no transitive expansion through other output tables or stored views",
      "complete": true,
      "specified_but_not_read": [],
      "read_but_not_specified": [
        "raw.facebook_pages_lifetime_post_metrics"
      ]
    },
    "time_dependencies": {
      "agent_sql": {
        "available": true,
        "appears": true,
        "hits": [
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
            "line": 31,
            "column": 25,
            "matched_text": "current_date",
            "line_text": "  and p.created_time >= current_date - interval '2 years'",
            "context": "code"
          }
        ]
      },
      "gold_sql": {
        "available": true,
        "appears": true,
        "hits": [
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
            "line": 20,
            "column": 25,
            "matched_text": "CURRENT_DATE",
            "line_text": "    AND created_time >= CURRENT_DATE - INTERVAL '2 years' -- Recent posts only",
            "context": "code"
          }
        ],
        "paths": [
          "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql"
        ]
      },
      "contract": {
        "available": true,
        "appears": false,
        "hits": []
      }
    },
    "trace_flags": {
      "A1_zero_rows": true,
      "A2_all_null_column": false,
      "A3_constant_nonnull_column": false,
      "A4_equal_columns": false,
      "A4_equal_columns_different_description_texts": false,
      "B5_null_literal_output": false,
      "B6_constant_literal_output": false,
      "B7_specified_not_read": false,
      "B7_read_not_specified": true,
      "B8_shared_single_source": false,
      "C9_agent_runtime_text": true,
      "C9_gold_runtime_text": true,
      "C9_contract_runtime_text": false,
      "D10_keyword_in_final_report": false,
      "D10_keyword_in_any_result_field": false
    }
  }
}
```

## trace_excerpts

```json
{
  "archive": "/home/katherine/Assumption_Ledger/traces/dacomp_deimpl_prev.tar.gz",
  "event_source_root": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent",
  "actual_read_sources_from_008_B7": [
    "raw.facebook_pages_lifetime_post_metrics",
    "raw.facebook_pages_page_data",
    "raw.facebook_pages_post_history"
  ],
  "name_match_policy": "Case-insensitive complete identifier-name boundaries; source names include qualified form and bare leaf name. No semantic association inferred.",
  "matched_step_count": 14,
  "full_original_characters_before_budget": 124982,
  "budget_triggered": true,
  "source_only_steps_indexed": 5,
  "retained_full_original_characters": 78505,
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
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/7.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1921,
    "decoded_characters": 73
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/7.json",
  "timestamp": "2026-10-25T05:10:33.465667",
  "target_table_name_hits": [
    "stg_social_media__facebook_posts"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 2167,
  "retention": "full_original"
}
```
```bash
cat config/layer_dependencies.yaml && find sql -type f -maxdepth 3 -print
```
```json
{
  "event_id": 8,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/8.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1606,
    "decoded_characters": 2094
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/8.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
# Social Media Reporting Layer Dependencies
# This file defines the execution order for SQL transformations

layers:
  staging:
    description: "Raw data standardization and cleaning with validation rules applied"
    tables:
      - stg_social_media__account_history
      - stg_social_media__twitter_user_history
      - stg_social_media__twitter_organic_tweets
      - stg_social_media__facebook_posts
      - stg_social_media__instagram_posts
      - stg_social_media__linkedin_posts
      - stg_social_media__youtube_videos

  intermediate:
    description: "Platform-specific business logic and data standardization"
    dependencies: ["staging"]
    tables:
      - social_media_reporting__facebook_posts_reporting
      - social_media_reporting__instagram_posts_reporting
      - social_media_reporting__linkedin_posts_reporting
      - social_media_reporting__twitter_posts_reporting
      - social_media_reporting__youtube_videos_reporting

  marts:
    description: "Analytics-ready unified reporting model"
    dependencies: ["intermediate"]
    tables:
      - social_media_reporting__daily_kpis
      - social_media_reporting__retention_kpis
      - social_media_reporting__ctr_by_platform
      - social_media_reporting__rollup_report

# Execution order within intermediate layer (important for testing consistency)
execution_order:
  intermediate:
    - social_media_reporting__facebook_posts_reporting
    - social_media_reporting__instagram_posts_reporting
    - social_media_reporting__linkedin_posts_reporting
    - social_media_reporting__twitter_posts_reporting
    - social_media_reporting__youtube_videos_reporting

  marts:
    - social_media_reporting__daily_kpis
    - social_media_reporting__retention_kpis
    - social_media_reporting__ctr_by_platform
    - social_media_reporting__rollup_reportfind: warning: you have specified the global option -maxdepth after the argument -type, but global options are not positional, i.e., -maxdepth affects tests specified before it as well as those specified after it.  Please specify global options before other arguments.
```

### event 9

```json
{
  "event_id": 9,
  "agent_command_sequence": 3,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/9.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1870,
    "decoded_characters": 22
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/9.json",
  "timestamp": "2026-10-25T05:10:33.502606",
  "target_table_name_hits": [
    "stg_social_media__facebook_posts"
  ],
  "source_table_name_hits": [
    "raw.facebook_pages_post_history",
    "raw.facebook_pages_page_data",
    "facebook_pages_post_history",
    "facebook_pages_page_data"
  ],
  "full_original_characters": 9959,
  "retention": "full_original"
}
```
```bash
sed -n '1,240p' run.py
```
```json
{
  "event_id": 10,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/10.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1556,
    "decoded_characters": 9937
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/10.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
#!/usr/bin/env python3
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


class SocialMediaDataPipeline:
    """Social Media Data Pipeline Orchestrator - Supports a Layered Schema Architecture"""

    def __init__(self,
                 source_db_path: str = "social_media_reporting_start.duckdb",
                 target_db_path: str = "social_media_reporting.duckdb",
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
            logger.error(f"Configuration file parsing error: {e}")
            raise

    def _initialize_database(self):
        """Initialize the working database, create the layered schema architecture, and import raw data"""
        logger.info(f"📥 Creating new layered database: {self.target_db_path}")


        if not os.path.exists(self.source_db_path):
            raise FileNotFoundError(f"Source database file not found: {self.source_db_path}")

        self.conn = duckdb.connect(self.target_db_path)


        self._create_schemas()


        self._import_raw_data()

        logger.info(f"✓ Layered database initialization complete: {self.target_db_path}")

    def _create_schemas(self):
        """Create schemas for the data layers"""
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
        """Load SQL file content"""
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
        """Process table references in SQL, converting them to schema.table format"""
        import re
        processed_sql = sql


        table_mappings = {}


        if current_layer == 'staging':
            table_mappings.update({
                'account_history': 'raw.account_history',
                'twitter_user_history': 'raw.twitter_user_history',
                'organic_tweet_report': 'raw.organic_tweet_report',
                'tweet': 'raw.tweet',
                'facebook_pages_post_history': 'raw.facebook_pages_post_history',
                'facebook_pages_page_data': 'raw.facebook_pages_page_data',
                'facebook_pages_lifetime_post_metrics_total_data': 'raw.facebook_pages_lifetime_post_metrics_total_data',
                'instagram_business_media_history': 'raw.instagram_business_media_history',
                'instagram_business_user_history': 'raw.instagram_business_user_history',
                'instagram_business_media_insights_data': 'raw.instagram_business_media_insights_data',
                'linkedin_pages_organization': 'raw.linkedin_pages_organization',
                'linkedin_pages_organization_ugc_post': 'raw.linkedin_pages_organization_ugc_post',
                'linkedin_pages_post_content': 'raw.linkedin_pages_post_content',
                'linkedin_pages_share_statistic_data': 'raw.linkedin_pages_share_statistic_data',
                'youtube_video': 'raw.youtube_video',
                'youtube_channel_basic': 'raw.youtube_channel_basic',
                'youtube_channel_demographics': 'raw.youtube_channel_demographics_data',
            })

        elif current_layer == 'intermediate':
            table_mappings.update({
                'stg_social_media__twitter_organic_tweets': 'staging.stg_social_media__twitter_organic_tweets',
                'stg_social_media__facebook_posts': 'staging.stg_social_media__facebook_posts',
                'stg_social_media__instagram_posts': 'staging.stg_social_media__instagram_posts',
                'stg_social_media__linkedin_posts': 'staging.stg_social_media__linkedin_posts',
                'stg_social_media__youtube_videos': 'staging.stg_social_media__youtube_videos',
            })

        elif current_layer == 'marts':
            table_mappings.update({
                'social_media_reporting__facebook_posts_reporting': 'intermediate.social_media_reporting__facebook_posts_reporting',
                'social_media_reporting__instagram_posts_reporting': 'intermediate.social_media_reporting__instagram_posts_reporting',
                'social_media_reporting__linkedin_posts_reporting': 'intermediate.social_media_reporting__linkedin_posts_reporting',
                'social_media_reporting__twitter_posts_reporting': 'intermediate.social_media_reporting__twitter_posts_reporting',
                'social_media_reporting__youtube_videos_reporting': 'intermediate.social_media_reporting__youtube_videos_reporting',
            })

        for table_name, schema_table in table_mappings.items():
            processed_sql = re.sub(r'\bfrom\s+' + re.escape(table_name) + r'\b', f'from {schema_table}', processed_sql, flags=re.IGNORECASE)
            processed_sql = re.sub(r'\bjoin\s+' + re.escape(table_name) + r'\b', f'join {schema_table}', processed_sql, flags=re.IGNORECASE)

        return processed_sql

    def _execute_layer(self, layer_name: str) -> bool:
        """Execute all tables in the specified layer"""
        layer_config = self.config['layers'][layer_name]
        tables = layer_config.get('tables', [])


        execution_order = self.config.get('execution_order', {}).get(layer_name, tables)

        logger.info(f"\n=== Executing {layer_name.upper()} Layer ===")
        logger.info(f"Description: {layer_config.get('description', '')}")

        success_count = 0
        total_count = len(execution_order)
```

### event 11

```json
{
  "event_id": 11,
  "agent_command_sequence": 4,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/11.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1898,
    "decoded_characters": 49
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/11.json",
  "timestamp": "2026-10-25T05:10:33.529716",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "facebook_pages_lifetime_post_metrics",
    "facebook_pages_post_history",
    "facebook_pages_page_data"
  ],
  "full_original_characters": 6481,
  "retention": "index_and_first_line_only",
  "first_line_original": "sed -n '1,220p' social_media_reporting_start.yaml"
}
```
```json
{
  "event_id": 12,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/12.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1584,
    "decoded_characters": 6432
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/12.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 13

```json
{
  "event_id": 13,
  "agent_command_sequence": 5,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/13.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1921,
    "decoded_characters": 72
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/13.json",
  "timestamp": "2026-10-25T05:10:33.555947",
  "target_table_name_hits": [
    "stg_social_media__facebook_posts"
  ],
  "source_table_name_hits": [
    "raw.facebook_pages_post_history",
    "raw.facebook_pages_page_data",
    "facebook_pages_post_history",
    "facebook_pages_page_data"
  ],
  "full_original_characters": 9757,
  "retention": "full_original"
}
```
```bash
wc -l docs/data_contract.yaml && sed -n '1,240p' docs/data_contract.yaml
```
```json
{
  "event_id": 14,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/14.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1607,
    "decoded_characters": 9685
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/14.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
987 docs/data_contract.yaml
version: "1.0"
metadata:
  description: "Complete data pipeline specification for Social Media Reporting source system. This YAML is the single source of truth describing what transformations must occur from raw to staging to intermediate and marts. It defines table purposes, validation actions, and business logic in natural language."
  author: "Data Engineering Team"
  pipeline_phases: ["staging_contract", "modeling_spec"]

# --------------------------------------------------------------------------- #
# PHASE 1: Defines the transformation from raw data to clean staging tables.  #
# --------------------------------------------------------------------------- #
staging_contract:
  purpose: "Transform raw social media data into clean, validated staging tables that are standardized across platforms, with data quality steps applied before business modeling."
  quality_actions:
    correct:
      description: "Automatically fix deterministic format issues such as casing, whitespace trimming, protocol normalization for URLs, and standardized date/timezone formats."
      examples: ["LOWER(TRIM(screen_name))", "normalize phone numbers", "ensure https:// protocol for URL fields", "standardize valid IANA timezones when pattern matches"]
    delete_row:
      description: "Remove entire row when records contain severe data quality issues that make them unusable downstream."
      examples: ["screen_name contains disallowed characters and cannot be corrected", "invalid primary keys", "timezone not in allowed list AND malformed format", "phone numbers with impossible format"]
    nullify_field:
      description: "Set invalid field values to NULL when the field is non-critical and record can still be useful downstream."
      examples: ["optional URL fails regex but record otherwise usable", "emails array malformed for page metadata", "non-essential descriptive fields corrupted"]

  tables:
    - name: stg_social_media__account_history
      description: "Standardized account metadata with validated timezone field for downstream joins and reporting."
      source_table: raw.account_history
      columns:
        - name: id
          data_type: BIGINT
          constraints: [not_null]
        - name: updated_at
          data_type: TIMESTAMP
        - name: approval_status
          data_type: VARCHAR
        - name: business_id
          data_type: VARCHAR
        - name: business_name
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
        - name: deleted
          data_type: BOOLEAN
        - name: industry_type
          data_type: VARCHAR
        - name: name
          data_type: VARCHAR
        - name: salt
          data_type: VARCHAR
        - name: timezone
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "timezone ~ '^[A-Z][a-z]+/[A-Z][a-z_]+$'"
              on_failure: delete_row
        - name: timezone_switch_at
          data_type: TIMESTAMP

    - name: stg_social_media__twitter_user_history
      description: "Cleaned and standardized Twitter user profile attributes for safe downstream joins and reporting."
      source_table: raw.twitter_user_history
      columns:
        - name: id
          data_type: BIGINT
          constraints: [not_null]
        - name: _fivetran_synced
          data_type: TIMESTAMP
        - name: screen_name
          data_type: VARCHAR
          constraints: [not_null]
          description: >
            Best-effort cleaning to keep only [A-Za-z0-9_]; rows with NULL/blank or harmful characters are removed.
          validation_rules:
            - rule: "screen_name = CASE WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '') END"
              on_failure: correct
            - rule: "screen_name IS NOT NULL AND NOT (screen_name RLIKE '[!@#$%^&*()+=<>?}{|,]')"
              on_failure: delete_row
        - name: url
          data_type: VARCHAR
          validation_rules:
            - rule: "url IS NULL OR url RLIKE '^https?://[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?'"
              on_failure: nullify_field
            - rule: "url IS NULL OR (url RLIKE '^(https?://)?[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?' AND url RLIKE '^https?://')"
              on_failure: correct
        - name: created_at
          data_type: TIMESTAMP
        - name: followers_count
          data_type: BIGINT
        - name: following_count
          data_type: BIGINT
          description: "Renamed from friends_count."
        - name: listed_count
          data_type: BIGINT
        - name: favourites_count
          data_type: BIGINT
        - name: statuses_count
          data_type: BIGINT
        - name: verified
          data_type: BOOLEAN
        - name: protected
          data_type: BOOLEAN
          description: "Derived from protected_user: TRUE if protected_user=TRUE else FALSE."
        - name: default_profile
          data_type: BOOLEAN
        - name: default_profile_image
          data_type: BOOLEAN
        - name: location
          data_type: VARCHAR
        - name: description
          data_type: VARCHAR
        - name: time_zone
          data_type: VARCHAR
        - name: lang
          data_type: VARCHAR

    - name: stg_social_media__twitter_organic_tweets
      description: "Tweet-level organic performance records enriched with tweet text and user attributes; recent 2-year window."
      source_table: raw.organic_tweet_report
      notes:
        - "Rows restricted to last 2 years via: date >= CURRENT_DATE - INTERVAL '2 years'."
        - "Tweet text joined from raw.tweet.full_text; user attributes joined from raw.twitter_user_history."
        - "All metrics default to 0 when NULL."
        - "engagement_rate guarded against division by zero."
      columns:
        - name: account_id
          data_type: VARCHAR
        - name: date
          data_type: DATE
        - name: organic_tweet_id
          data_type: VARCHAR
          description: "CAST(o.organic_tweet_id AS VARCHAR)."
        - name: placement
          data_type: VARCHAR
        - name: _fivetran_synced
          data_type: TIMESTAMP
        - name: app_clicks
          data_type: BIGINT
        - name: card_engagements
          data_type: BIGINT
        - name: carousel_swipes
          data_type: BIGINT
        - name: clicks
          data_type: BIGINT
        - name: engagements
          data_type: BIGINT
        - name: follows
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
        - name: likes
          data_type: BIGINT
        - name: poll_card_vote
          data_type: BIGINT
        - name: qualified_impressions
          data_type: BIGINT
        - name: replies
          data_type: BIGINT
        - name: retweets
          data_type: BIGINT
        - name: tweets_send
          data_type: BIGINT
        - name: unfollows
          data_type: BIGINT
        - name: url_clicks
          data_type: BIGINT
        - name: video_15_s_views
          data_type: BIGINT
        - name: video_3_s_100_pct_views
          data_type: BIGINT
        - name: video_6_s_views
          data_type: BIGINT
        - name: video_content_starts
          data_type: BIGINT
        - name: video_cta_clicks
          data_type: BIGINT
        - name: video_total_views
          data_type: BIGINT
        - name: video_views_100
          data_type: BIGINT
        - name: video_views_25
          data_type: BIGINT
        - name: video_views_50
          data_type: BIGINT
        - name: video_views_75
          data_type: BIGINT
        - name: tweet_text
          data_type: VARCHAR
          description: "From raw.tweet.full_text."
        - name: screen_name
          data_type: VARCHAR
          description: "From raw.twitter_user_history.screen_name."
        - name: user_name
          data_type: VARCHAR
          description: "From raw.twitter_user_history.name."
        - name: lang
          data_type: VARCHAR
          description: "From raw.tweet.lang."
        - name: tweet_created_at
          data_type: TIMESTAMP
          description: "From raw.tweet.created_at."
        - name: engagement_rate
          data_type: DOUBLE
          description: "CASE WHEN impressions > 0 THEN engagements / impressions ELSE 0.0 END."


    - name: stg_social_media__facebook_posts
      description: "Published, visible Facebook posts joined to page info, standardized fields for analysis; recent 2-year window."
      source_table: 
        - raw.facebook_pages_post_history
        - raw.facebook_pages_page_data
      columns:
        - name: id
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
          description: "From created_time."
        - name: post_id
          data_type: VARCHAR
          description: "CAST(id)."
        - name: post_message
          data_type: VARCHAR
          description: "COALESCE(message, '')."
        - name: page_id
          data_type: VARCHAR
          description: "CAST(page_id)."
        - name: page_name
          data_type: VARCHAR
          validation_rules:
            - rule: "page_name IS NOT NULL AND page_name <> ''"
              on_failure: correct  
          description: "Defaults to 'Unknown Page' when page name is missing."
        - name: page_username
          data_type: VARCHAR
        - name: page_category
          data_type: VARCHAR
        - name: page_followers
          data_type: BIGINT
        - name: shares
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
```

### event 15

```json
{
  "event_id": 15,
  "agent_command_sequence": 6,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/15.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1856,
    "decoded_characters": 41
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/15.json",
  "timestamp": "2026-10-25T05:10:36.610833",
  "target_table_name_hits": [
    "stg_social_media__facebook_posts"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 16597,
  "retention": "full_original"
}
```
```bash
sed -n '220,520p' docs/data_contract.yaml
```
```json
{
  "event_id": 16,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/16.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1542,
    "decoded_characters": 16556
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/16.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
          data_type: VARCHAR
          description: "COALESCE(message, '')."
        - name: page_id
          data_type: VARCHAR
          description: "CAST(page_id)."
        - name: page_name
          data_type: VARCHAR
          validation_rules:
            - rule: "page_name IS NOT NULL AND page_name <> ''"
              on_failure: correct  
          description: "Defaults to 'Unknown Page' when page name is missing."
        - name: page_username
          data_type: VARCHAR
        - name: page_category
          data_type: VARCHAR
        - name: page_followers
          data_type: BIGINT
        - name: shares
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
          description: "Default 0 in staging."
        - name: status_type
          data_type: VARCHAR
        - name: privacy_value
          data_type: VARCHAR
        - name: is_eligible_for_promotion
          data_type: BOOLEAN
        - name: is_instagram_eligible
          data_type: BOOLEAN
        - name: post_url
          data_type: VARCHAR
          validation_rules:
            - rule: "post_url ~ '^https://facebook\\.com/.+'"
              on_failure: correct

    - name: stg_social_media__instagram_posts
      description: "Normalized Instagram media posts enriched with account details and insights metrics; username cleaned; recent 2-year window."
      source_table: raw.instagram_business_media_history
      columns:
        - name: post_id
          data_type: VARCHAR
        - name: ig_post_id
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
        - name: post_caption
          data_type: VARCHAR
          description: "COALESCE(caption, '')."
        - name: page_id
          data_type: VARCHAR
          description: "CAST(user_id AS VARCHAR) from media history."
        - name: page_name
          data_type: VARCHAR
          description: "COALESCE(u.account_name, m.username, 'Unknown Account')."
        - name: account_username
          data_type: VARCHAR
          description: >
              Best-effort cleaning:
              - If NULL or blank -> NULL
              - Else remove characters not in [A-Za-z0-9_.] via REGEXP_REPLACE
              No re-validation of '..', '__', '_.' patterns; no forced 1–30 length trimming.
          validation_rules:
            - rule: "account_username = CASE WHEN account_username IS NULL OR TRIM(account_username) = '' THEN NULL ELSE REGEXP_REPLACE(account_username, '[^A-Za-z0-9_.]', '') END"
              on_failure: correct
        - name: media_type
          data_type: VARCHAR
        - name: media_type_category
          data_type: VARCHAR
          description: "Derived: IMAGE->Photo, VIDEO->Video, CAROUSEL_ALBUM->Carousel, REEL->Reel, STORY->Story, else passthrough."
        - name: post_url
          data_type: VARCHAR
          description: "permalink from media history."
        - name: media_url
          data_type: VARCHAR
        - name: impressions_override
          data_type: BIGINT
          description: "Default to 0 when insights missing; used for fallback impressions."
        - name: impressions
          data_type: BIGINT
          description: "COALESCE(mi.impressions, 0) from media insights."
        - name: likes
          data_type: BIGINT
          description: "COALESCE(mi.likes, 0) from media insights."
        - name: comments
          data_type: BIGINT
          description: "COALESCE(mi.comments, 0) from media insights."
        - name: saves
          data_type: BIGINT
          description: "COALESCE(mi.saves, 0) from media insights."
        - name: shares
          data_type: BIGINT
          description: "COALESCE(mi.shares, 0) from media insights."
        - name: engagement
          data_type: BIGINT
          description: "COALESCE(mi.engagement, 0) from media insights."
        - name: reach
          data_type: BIGINT
          description: "COALESCE(mi.reach, 0) from media insights."
        - name: account_followers
          data_type: BIGINT
          description: "COALESCE(u.followers_count, 0) from user history."
        - name: account_media_count
          data_type: BIGINT
        - name: engagement_rate
          data_type: DOUBLE
          description: "Computed as engagement / impressions; defaults to 0.0 when denominator is not positive."
        - name: _fivetran_synced
          data_type: TIMESTAMP
          description: "_fivetran_synced from media history."

    - name: stg_social_media__linkedin_posts
      description: "Minimal staging representation of LinkedIn organization UGC posts with standardized identifiers and URL."
      source_table: raw.linkedin_pages_organization_ugc_post
      columns:
        - name: organization_id
          data_type: VARCHAR
        - name: post_id
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
        - name: platform
          data_type: VARCHAR
        - name: post_message
          data_type: VARCHAR
        - name: content_type
          data_type: VARCHAR
        - name: post_url
          data_type: VARCHAR
          validation_rules:
            - rule: "post_url RLIKE '^https://www.linkedin.com/feed/update/.+'"
              on_failure: correct

    - name: stg_social_media__youtube_videos
      description: "YouTube videos staged with standardized fields and basic derived metrics; recent 2-year window."
      source_table: raw.youtube_video
      notes:
        - "Include only videos with view data: statistics_view_count IS NOT NULL."
        - "Restrict to last 2 years: snippet_published_at >= CURRENT_DATE - INTERVAL '2 years'."
        - "post_url is constructed as https://img.youtube.com/vi/{video_id}/default.jpg."
        - "All numeric metrics default to 0 when NULL."
        - "impressions and clicks both mirror statistics_view_count per SQL."
      columns:
        - name: video_id
          data_type: VARCHAR
          description: "CAST(id AS VARCHAR)."
        - name: video_published_at
          data_type: TIMESTAMP
          description: "snippet_published_at."
        - name: video_title
          data_type: VARCHAR
        - name: video_description
          data_type: VARCHAR
        - name: channel_id
          data_type: VARCHAR
        - name: channel_title
          data_type: VARCHAR
        - name: page_name
          data_type: VARCHAR
        - name: post_url
          data_type: VARCHAR
          description: "Thumbnail URL used as post URL: https://img.youtube.com/vi/{video_id}/default.jpg."
          validation_rules:
            - rule: "post_url RLIKE '^https://img.youtube.com/vi/.+/default.jpg'"
              on_failure: correct
        - name: privacy_status
          data_type: VARCHAR
        - name: clicks
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
          description: "COALESCE(statistics_view_count, 0) — estimated as views in SQL."
        - name: likes
          data_type: BIGINT
        - name: comments
          data_type: BIGINT
        - name: estimated_shares
          data_type: BIGINT
          description: >
            CASE WHEN statistics_like_count > 10 THEN FLOOR(statistics_like_count / 10) ELSE 0 END.
        - name: subscribers
          data_type: BIGINT
          description: "COALESCE(channel_info.channel_subscribers, 0)."
        - name: engagement_rate
          data_type: DOUBLE
          description: "CASE WHEN impressions > 0 THEN (likes + comments + estimated_shares)::DOUBLE / impressions ELSE 0.0 END."
        - name: _fivetran_synced
          data_type: TIMESTAMP
          description: "_fivetran_synced from raw.youtube_video."


# --------------------------------------------------------------------------- #
# PHASE 2: Defines the business logic from staging to analytical models.      #
# --------------------------------------------------------------------------- #
modeling_spec:
  purpose: "Apply business logic and generate analysis-ready models using strictly layered dependencies."
  design_principles:
    - "Staging layer must only reference raw tables."
    - "Intermediate layer must only reference staging tables."
    - "Marts layer must only reference intermediate tables."
    - "Cross-layer and same-layer dependencies are prohibited."
    - "Grain must be explicit and unique per model."

  intermediate_models:
    - name: social_media_reporting__facebook_posts_reporting
      description: Standardizes Facebook posts from staging, filters to last two years, and adds content classification, text metrics, date buckets, per-page window features, and engagement rate
      grain: One row per post_id per page_id (source duplicates preserved)
      source_models:
      - staging.stg_social_media__facebook_posts
      business_logic: '- Source and filters: - Read from staging.stg_social_media__facebook_posts. - Cast page_id and post_id to text. - Require created_timestamp to be non-NULL and within the last two years relative to CURRENT_DATE. - Replace NULLs: post_message and post_url -> empty string; shares and impressions -> 0. - Set likes, comments, and clicks to 0 (not available in source). - Content typing and link flag (evaluated on the lowercased message, matched anywhere in the text): - content_type precedence: link if a URL pattern ("http://" or "https://") is present; else photo if "image" or "photo" is present; else video if "video" is present; else text. - has_link is TRUE when a URL pattern is present, otherwise FALSE. - Text metrics: - text_length_chars is the number of characters in the trimmed message. - text_word_count is 0 if the trimmed message is empty; otherwise count spaces in the trimmed message and add 1; only the space character is treated as a separator, and consecutive spaces each add to the count. - Date buckets from created_timestamp: - day/week/month are the start-of-day, start-of-week (engine default week start), and start-of-month buckets. - Per-page windows: - page_recency_rank is the row number per page_id ordered by created_timestamp descending; 1 is most recent; ties on timestamp are ordered arbitrarily. - rolling_7_post_shares is the sum of shares over the current post and the six immediately prior posts per page_id ordered by created_timestamp; includes the current row and uses the 0 defaults for missing shares. - Final fields: - platform is the literal "facebook". - engagement_rate is 0.0 when impressions are 0; otherwise (likes + shares + comments) divided by impressions; computed as a double and not capped.'
      columns:
      - name: page_id
        data_type: VARCHAR
        description: Facebook page identifier cast to text; may be NULL; used as the partition key for window functions
      - name: page_name
        data_type: VARCHAR
        description: Facebook page name passed through from source; may be NULL
      - name: post_id
        data_type: VARCHAR
        description: Facebook post identifier cast to text; duplicates from source are preserved
      - name: post_message
        data_type: VARCHAR
        description: Post message text with NULLs replaced by empty string; original casing and whitespace preserved
      - name: created_timestamp
        data_type: TIMESTAMP
        description: Post creation timestamp required to be non-NULL and within the last two years relative to CURRENT_DATE
      - name: platform
        data_type: VARCHAR
        description: Literal value 'facebook' for all rows
      - name: clicks
        data_type: BIGINT
        description: Clicks set to 0 because not available in source; non-NULL constant
      - name: impressions
        data_type: INTEGER
        description: Impressions from source with NULLs replaced by 0; non-NULL; used as the engagement_rate denominator when greater than 0
      - name: likes
        data_type: BIGINT
        description: Likes set to 0 because not available in source; non-NULL constant
      - name: shares
        data_type: BIGINT
        description: Shares from source with NULLs replaced by 0; non-NULL; used in rolling_7_post_shares and engagement_rate
      - name: comments
        data_type: BIGINT
        description: Comments set to 0 because not available in source; non-NULL constant
      - name: post_url
        data_type: VARCHAR
        description: Post URL with NULLs replaced by empty string; original text preserved
      - name: content_type
        data_type: VARCHAR
        description: 'Derived label with precedence: link if a URL pattern is present; else photo if ''image'' or ''photo'' is present; else video if ''video'' is present; otherwise text'
      - name: has_link
        data_type: BOOLEAN
        description: TRUE when the lowercased message contains a URL pattern ('http://' or 'https://'); otherwise FALSE; non-NULL
      - name: text_length_chars
        data_type: BIGINT
        description: Character count of the trimmed message; 0 for empty string; non-NULL
      - name: text_word_count
        data_type: BIGINT
        description: 'Word count based on spaces in the trimmed message: 0 if empty; else number of spaces plus 1; only the space character is treated as a separator'
      - name: day
        data_type: DATE
        description: Start-of-day date bucket derived from created_timestamp
      - name: week
        data_type: DATE
        description: Start-of-week date bucket derived from created_timestamp using the engine’s default week start
      - name: month
        data_type: DATE
        description: Start-of-month date bucket derived from created_timestamp
      - name: page_recency_rank
        data_type: BIGINT
        description: Row number per page_id ordered by created_timestamp descending; 1 is most recent; ties are ordered arbitrarily
      - name: rolling_7_post_shares
        data_type: BIGINT
        description: Sum of shares over the current and six prior posts per page_id ordered by created_timestamp; includes the current row; shares default to 0
      - name: engagement_rate
        data_type: DOUBLE
        description: If impressions are 0 then 0.0; otherwise (likes + shares + comments) divided by impressions; computed as a double and not capped
    - name: social_media_reporting__instagram_posts_reporting
      description: Standardized Instagram post records with unified metrics, content format mapping, and engagement rates for the last 2 years
      grain: One row per source post record (no deduplication)
      source_models:
      - staging.stg_social_media__instagram_posts
      business_logic: '- Source: staging.stg_social_media__instagram_posts. - Filter rows where page_id is not null and created_timestamp is within the last 2 years from current date. - Metrics standardization: - Treat missing as 0: impressions, likes, comments, saves, shares, reach, engagement, account_followers. - calculated_engagement_rate: - If impressions > 0 and a source engagement_rate exists, use that value. - Else if impressions > 0, compute engagement divided by impressions (engagement treated as 0 when missing). - Else set to 0.0. - content_format mapping from media_type_category: - Photo, Video, Carousel -> "Feed Post"; Reel -> "Reel"; Story -> "Story"; otherwise use the original category (may be null). - Final shaping: - Cast page_id and post_id to VARCHAR. - post_message = post_caption with nulls replaced by empty string; post_url with nulls replaced by empty string. - platform = ''instagram''. - clicks = engagement with nulls treated as 0. - followers_engagement_rate = engagement divided by account_followers when followers > 0 (engagement treated as 0 when missing); otherwise 0.0. - Output one row per source post record; no additional aggregation or ordering.'
      columns:
      - name: page_id
        data_type: VARCHAR
        description: Instagram business account identifier; filtered to non-null and cast to VARCHAR
        tests:
        - not_null
      - name: page_name
        data_type: VARCHAR
        description: Account/page display name from the source; may be null
      - name: post_id
        data_type: VARCHAR
        description: Instagram media identifier; cast to VARCHAR
      - name: post_message
        data_type: VARCHAR
        description: Post caption text with NULL replaced by empty string; casing and whitespace are preserved
      - name: created_timestamp
        data_type: TIMESTAMP
        description: Media creation timestamp; only posts from the last 2 years are included
```

### event 23

```json
{
  "event_id": 23,
  "agent_command_sequence": 10,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/23.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1861,
    "decoded_characters": 290
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/23.json",
  "timestamp": "2026-10-25T05:10:40.323848",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "facebook_pages_lifetime_post_metrics",
    "facebook_pages_post_history",
    "facebook_pages_page_data"
  ],
  "full_original_characters": 31229,
  "retention": "index_and_first_line_only",
  "first_line_original": "python - <<'PY'\n"
}
```
```json
{
  "event_id": 24,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/24.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1547,
    "decoded_characters": 30939
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/24.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 29

```json
{
  "event_id": 29,
  "agent_command_sequence": 13,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/29.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 27253,
    "decoded_characters": 12624
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/29.json",
  "timestamp": "2026-10-25T05:11:18.741227",
  "target_table_name_hits": [
    "stg_social_media__facebook_posts"
  ],
  "source_table_name_hits": [
    "raw.facebook_pages_lifetime_post_metrics",
    "facebook_pages_lifetime_post_metrics",
    "raw.facebook_pages_post_history",
    "raw.facebook_pages_page_data",
    "facebook_pages_post_history",
    "facebook_pages_page_data"
  ],
  "full_original_characters": 12624,
  "retention": "full_original"
}
```
```bash
mkdir -p sql/staging sql/intermediate sql/marts && cat > /tmp/write_sql.py <<'PY'
from pathlib import Path
files={}
files['staging/stg_social_media__account_history.sql'] = '''select
    try_cast(id as bigint) as id,
    updated_at::timestamp as updated_at,
    approval_status::varchar as approval_status,
    business_id::varchar as business_id,
    business_name::varchar as business_name,
    created_at::timestamp as created_at,
    deleted::boolean as deleted,
    industry_type::varchar as industry_type,
    name::varchar as name,
    salt::varchar as salt,
    timezone::varchar as timezone,
    timezone_switch_at::timestamp as timezone_switch_at
from raw.account_history
where try_cast(id as bigint) is not null
  and timezone is not null
  and regexp_matches(timezone, '^[A-Z][a-z]+/[A-Z][a-z_]+$')'''
files['staging/stg_social_media__twitter_user_history.sql'] = '''with user_cleaned as (
    select
        try_cast(id as bigint) as id,
        _fivetran_synced::timestamp as _fivetran_synced,
        case when screen_name is null or trim(screen_name) = '' then null
             else regexp_replace(screen_name, '[^A-Za-z0-9_]', '', 'g') end as screen_name,
        case
            when url is null then null
            when regexp_matches(url, '^(https?://)?[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?')
                then case when regexp_matches(url, '^https?://') then url else 'https://' || url end
            else null
        end as url,
        created_at::timestamp as created_at,
        try_cast(followers_count as bigint) as followers_count,
        try_cast(friends_count as bigint) as following_count,
        try_cast(listed_count as bigint) as listed_count,
        try_cast(favourites_count as bigint) as favourites_count,
        try_cast(statuses_count as bigint) as statuses_count,
        verified::boolean as verified,
        coalesce(protected_user, false)::boolean as protected,
        default_profile::boolean as default_profile,
        default_profile_image::boolean as default_profile_image,
        location::varchar as location,
        description::varchar as description,
        time_zone::varchar as time_zone,
        lang::varchar as lang
    from raw.twitter_user_history
)
select *
from user_cleaned
where id is not null
  and screen_name is not null
  and screen_name <> '' '''
files['staging/stg_social_media__twitter_organic_tweets.sql'] = '''with organic as (
    select *
    from raw.organic_tweet_report
    where cast(date as date) >= current_date - interval '2 years'
),
tweets as (
    select
        try_cast(id as bigint) as tweet_id,
        full_test as tweet_text,
        lang,
        created_at as tweet_created_at
    from raw.tweet
),
users as (
    select *, row_number() over (partition by id order by _fivetran_synced desc nulls last) as row_num
    from raw.twitter_user_history
)
select
    o.account_id::varchar as account_id,
    cast(o.date as date) as date,
    cast(o.organic_tweet_id as varchar) as organic_tweet_id,
    o.placement::varchar as placement,
    o._fivetran_synced::timestamp as _fivetran_synced,
    coalesce(o.app_clicks, 0)::bigint as app_clicks,
    coalesce(o.card_engagements, 0)::bigint as card_engagements,
    coalesce(o.carousel_swipes, 0)::bigint as carousel_swipes,
    coalesce(o.clicks, 0)::bigint as clicks,
    coalesce(o.engagements, 0)::bigint as engagements,
    coalesce(o.follows, 0)::bigint as follows,
    coalesce(o.impressions, 0)::bigint as impressions,
    coalesce(o.likes, 0)::bigint as likes,
    coalesce(o.poll_card_vote, 0)::bigint as poll_card_vote,
    coalesce(o.qualified_impressions, 0)::bigint as qualified_impressions,
    coalesce(o.replies, 0)::bigint as replies,
    coalesce(o.retweets, 0)::bigint as retweets,
    coalesce(o.tweets_send, 0)::bigint as tweets_send,
    coalesce(o.unfollows, 0)::bigint as unfollows,
    coalesce(o.url_clicks, 0)::bigint as url_clicks,
    coalesce(o.video_15_s_views, 0)::bigint as video_15_s_views,
    coalesce(o.video_3_s_100_pct_views, 0)::bigint as video_3_s_100_pct_views,
    coalesce(o.video_6_s_views, 0)::bigint as video_6_s_views,
    coalesce(o.video_content_starts, 0)::bigint as video_content_starts,
    coalesce(o.video_cta_clicks, 0)::bigint as video_cta_clicks,
    coalesce(o.video_total_views, 0)::bigint as video_total_views,
    coalesce(o.video_views_100, 0)::bigint as video_views_100,
    coalesce(o.video_views_25, 0)::bigint as video_views_25,
    coalesce(o.video_views_50, 0)::bigint as video_views_50,
    coalesce(o.video_views_75, 0)::bigint as video_views_75,
    t.tweet_text::varchar as tweet_text,
    regexp_replace(u.screen_name, '[^A-Za-z0-9_]', '', 'g')::varchar as screen_name,
    u.name::varchar as user_name,
    t.lang::varchar as lang,
    t.tweet_created_at::timestamp as tweet_created_at,
    case when coalesce(o.impressions, 0) > 0
         then coalesce(o.engagements, 0)::double / o.impressions else 0.0 end as engagement_rate
from organic o
left join tweets t on try_cast(o.organic_tweet_id as bigint) = t.tweet_id
left join users u on u.id = o.account_id and u.row_num = 1'''
files['staging/stg_social_media__facebook_posts.sql'] = '''with post_metrics as (
    select post_id, max(post_impressions) as impressions
    from raw.facebook_pages_lifetime_post_metrics
    group by post_id
), pages as (
    select *, row_number() over (partition by id order by _fivetran_synced desc nulls last) as row_num
    from raw.facebook_pages_page_data
)
select
    p.id::varchar as id,
    p.created_time::timestamp as created_timestamp,
    p.id::varchar as post_id,
    coalesce(p.message, '')::varchar as post_message,
    cast(p.page_id as varchar) as page_id,
    coalesce(nullif(pg.name, ''), 'Unknown Page')::varchar as page_name,
    pg.username::varchar as page_username,
    pg.category::varchar as page_category,
    coalesce(try_cast(pg.fan_count as bigint), 0)::bigint as page_followers,
    coalesce(p.share_count, 0)::bigint as shares,
    coalesce(pm.impressions, 0)::bigint as impressions,
    p.status_type::varchar as status_type,
    p.privacy_value::varchar as privacy_value,
    p.is_eligible_for_promotion::boolean as is_eligible_for_promotion,
    p.is_instagram_eligible::boolean as is_instagram_eligible,
    ('https://facebook.com/' || p.id)::varchar as post_url
from raw.facebook_pages_post_history p
left join pages pg on p.page_id = pg.id and pg.row_num = 1
left join post_metrics pm on pm.post_id = p.id
where coalesce(p.is_published, false)
  and not coalesce(p.is_hidden, false)
  and p.created_time >= current_date - interval '2 years'
  and p.created_time is not null'''
files['staging/stg_social_media__instagram_posts.sql'] = '''with users as (
    select *, row_number() over (partition by id order by _fivetran_synced desc nulls last) as row_num
    from raw.instagram_business_user_history
), insights as (
    select
        id,
        coalesce(carousel_album_impressions, video_photo_impressions, story_impressions, video_views, reel_plays, 0) as impressions,
        coalesce(like_count, reel_likes, 0) as likes,
        coalesce(comment_count, reel_comments, 0) as comments,
        coalesce(carousel_album_saved, video_photo_saved, 0) as saves,
        coalesce(carousel_album_shares, video_photo_shares, story_shares, reel_shares, 0) as shares,
        coalesce(carousel_album_engagement, video_photo_engagement, reel_total_interactions, 0) as engagement,
        coalesce(carousel_album_reach, video_photo_reach, story_reach, reel_reach, 0) as reach
    from raw.instagram_business_media_insights
)
select
    cast(m.id as varchar) as post_id,
    cast(m.ig_id as varchar) as ig_post_id,
    m.created_time::timestamp as created_timestamp,
    coalesce(m.caption, '')::varchar as post_caption,
    cast(m.user_id as varchar) as page_id,
    coalesce(nullif(u.name, ''), nullif(m.username, ''), 'Unknown Account')::varchar as page_name,
    case when m.username is null or trim(m.username) = '' then null
         else regexp_replace(m.username, '[^A-Za-z0-9_.]', '', 'g') end::varchar as account_username,
    m.media_type::varchar as media_type,
    case upper(m.media_type)
        when 'IMAGE' then 'Photo'
        when 'VIDEO' then 'Video'
        when 'CAROUSEL_ALBUM' then 'Carousel'
        when 'REEL' then 'Reel'
        when 'STORY' then 'Story'
        else m.media_type end::varchar as media_type_category,
    m.permalink::varchar as post_url,
    m.media_url::varchar as media_url,
    coalesce(i.impressions, 0)::bigint as impressions_override,
    coalesce(i.impressions, 0)::bigint as impressions,
    coalesce(i.likes, 0)::bigint as likes,
    coalesce(i.comments, 0)::bigint as comments,
    coalesce(i.saves, 0)::bigint as saves,
    coalesce(i.shares, 0)::bigint as shares,
    coalesce(i.engagement, 0)::bigint as engagement,
    coalesce(i.reach, 0)::bigint as reach,
    coalesce(try_cast(u.followers_count as bigint), 0)::bigint as account_followers,
    coalesce(try_cast(u.media_count as bigint), 0)::bigint as account_media_count,
    case when coalesce(i.impressions, 0) > 0 then coalesce(i.engagement, 0)::double / i.impressions else 0.0 end as engagement_rate,
    m._fivetran_synced::timestamp as _fivetran_synced
from raw.instagram_business_media_history m
left join users u on m.user_id = u.id and u.row_num = 1
left join insights i on m.id = i.id
where m.created_time >= current_date - interval '2 years'
  and m.created_time is not null'''
files['staging/stg_social_media__linkedin_posts.sql'] = '''with post_metrics as (
    select
        _share_entity_urn,
        max(click_count) as click_count,
        max(impression_count) as impression_count,
        max(like_count) as like_count,
        max(share_count) as share_count,
        max(comment_count) as comment_count,
        max(engagement) as engagement
    from raw.linkedin_pages_share_statistic
    group by _share_entity_urn
)
select
    cast(o.organiation_id as varchar) as organization_id,
    o.ugc_post_id::varchar as post_id,
    h.created_time::timestamp as created_timestamp,
    'linkedin'::varchar as platform,
    coalesce(pc.article_title, pc.media_title, h.commentary)::varchar as post_message,
    pc.type::varchar as content_type,
    ('https://www.linkedin.com/feed/update/' || o.ugc_post_id)::varchar as post_url
from raw.linkedin_pages_organization_ugc_post o
left join raw.linkedin_pages_ugc_post_history h on h.id = o.ugc_post_id
left join raw.linkedin_pages_post_content pc on pc.post_id = regexp_replace(o.ugc_post_id, '^urn:li:share:', 'urn:li:share:')
left join post_metrics pm on pm._share_entity_urn = o.ugc_post_id
where o.organiation_id is not null'''
files['staging/stg_social_media__youtube_videos.sql'] = '''with channel_info as (
    select channel_id, max(channel_subscribers) as channel_subscribers
    from raw.youtube_channel_basic
    group by channel_id
)
select
    cast(v.id as varchar) as video_id,
    v.snippet_published_at::timestamp as video_published_at,
    v.snippet_title::varchar as video_title,
    v.snippet_description::varchar as video_description,
    v.snippet_channel_id::varchar as channel_id,
    v.snippet_channel_title::varchar as channel_title,
    coalesce(v.snippet_channel_title, 'Unknown Channel')::varchar as page_name,
    ('https://img.youtube.com/vi/' || v.id || '/default.jpg')::varchar as post_url,
    v.privacy_status::varchar as privacy_status,
    coalesce(v.statistics_view_count, 0)::bigint as clicks,
    coalesce(v.statistics_view_count, 0)::bigint as impressions,
    coalesce(v.statistics_like_count, 0)::bigint as likes,
    coalesce(v.statistics_comment_count, 0)::bigint as comments,
    case when v.statistics_like_count > 10 then floor(v.statistics_like_count / 10.0)::bigint else 0 end as estimated_shares,
    coalesce(try_cast(ci.channel_subscribers as bigint), 0)::bigint as subscribers,
    case when coalesce(v.statistics_view_count, 0) > 0
         then (coalesce(v.statistics_like_count, 0) + coalesce(v.statistics_comment_count, 0)
               + case when v.statistics_like_count > 10 then floor(v.statistics_like_count / 10.0) else 0 end)::double / v.statistics_view_count
         else 0.0 end as engagement_rate,
    v._fivetran_synced::timestamp as _fivetran_synced
from raw.youtube_video v
left join channel_info ci on ci.channel_id = v.snippet_channel_id
where v.statistics_view_count is not null
  and v.snippet_published_at >= current_date - interval '2 years'
  and v.snippet_published_at is not null'''
for name,sql in files.items():
 p=Path('sql')/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(sql+'\n')
PY
python /tmp/write_sql.py
```
```json
{
  "event_id": 30,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/30.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 26937,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/30.json",
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
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/31.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 21387,
    "decoded_characters": 9709
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/31.json",
  "timestamp": "2026-10-25T05:11:41.125017",
  "target_table_name_hits": [
    "stg_social_media__facebook_posts"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 9709,
  "retention": "full_original"
}
```
```bash
cat >> /tmp/write_sql.py <<'PY'
files['intermediate/social_media_reporting__facebook_posts_reporting.sql'] = '''with source_posts as (
    select
        cast(page_id as varchar) as page_id,
        page_name,
        cast(post_id as varchar) as post_id,
        coalesce(post_message, '') as post_message,
        created_timestamp,
        coalesce(shares, 0)::bigint as shares,
        coalesce(impressions, 0)::integer as impressions,
        coalesce(post_url, '') as post_url
    from staging.stg_social_media__facebook_posts
    where created_timestamp is not null
      and created_timestamp >= current_date - interval '2 years'
),
classified_posts as (
    select *,
        lower(post_message) as lower_message,
        case
            when contains(lower(post_message), 'http://') or contains(lower(post_message), 'https://') then 'link'
            when contains(lower(post_message), 'image') or contains(lower(post_message), 'photo') then 'photo'
            when contains(lower(post_message), 'video') then 'video'
            else 'text'
        end as content_type
    from source_posts
),
featured_posts as (
    select *,
        row_number() over (partition by page_id order by created_timestamp desc) as page_recency_rank,
        sum(shares) over (
            partition by page_id order by created_timestamp
            rows between 6 preceding and current row
        ) as rolling_7_post_shares
    from classified_posts
)
select
    page_id,
    page_name,
    post_id,
    post_message,
    created_timestamp,
    'facebook'::varchar as platform,
    0::bigint as clicks,
    impressions,
    0::bigint as likes,
    shares,
    0::bigint as comments,
    post_url,
    content_type,
    (contains(lower_message, 'http://') or contains(lower_message, 'https://')) as has_link,
    length(trim(post_message))::bigint as text_length_chars,
    case when trim(post_message) = '' then 0
         else length(trim(post_message)) - length(replace(trim(post_message), ' ', '')) + 1 end::bigint as text_word_count,
    cast(created_timestamp as date) as day,
    date_trunc('week', created_timestamp)::date as week,
    date_trunc('month', created_timestamp)::date as month,
    page_recency_rank,
    rolling_7_post_shares::bigint as rolling_7_post_shares,
    case when impressions > 0 then shares::double / impressions else 0.0 end as engagement_rate
from featured_posts'''
files['intermediate/social_media_reporting__instagram_posts_reporting.sql'] = '''with source_posts as (
    select *
    from staging.stg_social_media__instagram_posts
    where page_id is not null
      and created_timestamp >= current_date - interval '2 years'
)
select
    cast(page_id as varchar) as page_id,
    page_name,
    cast(post_id as varchar) as post_id,
    coalesce(post_caption, '')::varchar as post_message,
    created_timestamp,
    'instagram'::varchar as platform,
    coalesce(engagement, 0)::bigint as clicks,
    coalesce(impressions, 0)::bigint as impressions,
    coalesce(likes, 0)::bigint as likes,
    coalesce(shares, 0)::bigint as shares,
    coalesce(comments, 0)::bigint as comments,
    coalesce(post_url, '')::varchar as post_url,
    coalesce(saves, 0)::bigint as saves,
    coalesce(reach, 0)::bigint as reach,
    coalesce(account_followers, 0)::bigint as account_followers,
    case media_type_category
        when 'Photo' then 'Feed Post'
        when 'Video' then 'Feed Post'
        when 'Carousel' then 'Feed Post'
        when 'Reel' then 'Reel'
        when 'Story' then 'Story'
        else media_type_category end::varchar as content_format,
    case when coalesce(impressions, 0) > 0 and engagement_rate is not null then engagement_rate::double
         when coalesce(impressions, 0) > 0 then coalesce(engagement, 0)::double / impressions
         else 0.0 end as calculated_engagement_rate,
    case when coalesce(account_followers, 0) > 0 then coalesce(engagement, 0)::double / account_followers else 0.0 end as followers_engagement_rate
from source_posts'''
files['intermediate/social_media_reporting__linkedin_posts_reporting.sql'] = '''with source_posts as (
    select *
    from staging.stg_social_media__linkedin_posts
    where organization_id is not null
      and created_timestamp is not null
      and created_timestamp >= current_date - interval '4 years'
),
normalized_posts as (
    select
        organization_id::varchar as page_id,
        case when trim(organization_id) = '' then null else organization_id::varchar end as page_name,
        post_id::varchar as post_id,
        coalesce(post_message, 'LinkedIn Post')::varchar as post_message,
        created_timestamp,
        coalesce(0, 0)::integer as clicks,
        0::integer as impressions,
        0::integer as likes,
        0::integer as shares,
        0::integer as comments,
        content_type
    from source_posts
)
select
    page_id,
    page_name,
    post_id,
    post_message,
    created_timestamp,
    'linkedin'::varchar as platform,
    clicks,
    impressions,
    likes,
    shares,
    comments,
    case when post_id is null then null else 'https://www.linkedin.com/feed/update/' || post_id end::varchar as post_url,
    case content_type
        when 'article' then 'Article'
        when 'share' then 'Shared Content'
        when 'media' then 'Media Post'
        when 'poll' then 'Poll'
        else 'Text Post' end::varchar as post_category,
    case when impressions > 0 then (clicks + likes + comments + shares)::double / impressions else 0.0 end as calculated_engagement_rate
from normalized_posts'''
files['intermediate/social_media_reporting__twitter_posts_reporting.sql'] = '''with valid_tweets as (
    select *
    from staging.stg_social_media__twitter_organic_tweets
    where organic_tweet_id is not null
),
row_candidates as (
    select
        *,
        coalesce(nullif(screen_name, ''), nullif(user_name, ''), account_id::varchar) as page_name_candidate
    from valid_tweets
),
aggregated_tweets as (
    select
        account_id::varchar as page_id,
        max(page_name_candidate) as page_name,
        cast(organic_tweet_id as varchar) as post_id,
        max(tweet_text) as post_message,
        min(tweet_created_at) as created_timestamp,
        sum(clicks) as clicks,
        sum(impressions) as impressions,
        sum(likes) as likes,
        sum(retweets) as shares,
        sum(replies) as comments,
        sum(app_clicks) as app_clicks,
        sum(url_clicks) as url_clicks,
        sum(qualified_impressions) as qualified_impressions,
        avg(engagement_rate) as engagement_rate
    from row_candidates
    group by account_id, organic_tweet_id
),
metric_defaults as (
    select
        *,
        coalesce(clicks, 0)::hugeint as clicks_defaulted,
        coalesce(impressions, 0)::hugeint as impressions_defaulted,
        coalesce(likes, 0)::hugeint as likes_defaulted,
        coalesce(shares, 0)::hugeint as shares_defaulted,
        coalesce(comments, 0)::hugeint as comments_defaulted
    from aggregated_tweets
)
select
    page_id,
    page_name,
    post_id,
    post_message,
    created_timestamp,
    'twitter'::varchar as platform,
    clicks_defaulted as clicks,
    impressions_defaulted as impressions,
    likes_defaulted as likes,
    shares_defaulted as shares,
    comments_defaulted as comments,
    case when page_name is null then null else 'https://twitter.com/' || page_name || '/status/' || post_id end::varchar as post_url,
    coalesce(app_clicks, 0)::hugeint as app_clicks,
    coalesce(url_clicks, 0)::hugeint as url_clicks,
    coalesce(qualified_impressions, 0)::hugeint as qualified_impressions,
    coalesce(engagement_rate, 0.0)::double as engagement_rate,
    case when impressions_defaulted > 0
         then (likes_defaulted + shares_defaulted + comments_defaulted)::double / impressions_defaulted
         else 0.0 end as calculated_engagement_rate
from metric_defaults'''
files['intermediate/social_media_reporting__youtube_videos_reporting.sql'] = '''with source_videos as (
    select *
    from staging.stg_social_media__youtube_videos
    where video_id is not null
      and video_published_at is not null
      and video_published_at >= current_date - interval '2 years'
),
video_metrics as (
    select
        cast(channel_id as varchar) as page_id,
        coalesce(channel_title, 'Unknown Channel')::varchar as page_name,
        cast(video_id as varchar) as post_id,
        video_description::varchar as post_message,
        video_published_at as created_timestamp,
        coalesce(clicks, 0)::bigint as clicks,
        coalesce(impressions, 0)::bigint as impressions,
        coalesce(likes, 0)::bigint as likes,
        coalesce(estimated_shares, 0)::bigint as shares,
        coalesce(comments, 0)::bigint as comments,
        post_url,
        privacy_status,
        coalesce(subscribers, 0)::double as channel_subscribers,
        coalesce(engagement_rate, 0.0)::double as source_engagement_rate
    from source_videos
)
select
    page_id,
    page_name,
    post_id,
    post_message,
    created_timestamp,
    'youtube'::varchar as platform,
    clicks,
    impressions,
    likes,
    shares,
    comments,
    post_url,
    case when source_engagement_rate > 0 then source_engagement_rate
         when clicks > 0 then (likes + comments + shares)::double / clicks else 0.0 end as calculated_engagement_rate,
    privacy_status,
    channel_subscribers,
    0::integer as channel_total_videos,
    case when channel_subscribers > 0 then clicks::double / channel_subscribers else 0.0 end as views_per_subscriber,
    case when clicks > 0 then likes::double / clicks else 0.0 end as likes_per_view_ratio
from video_metrics'''
PY
python /tmp/write_sql.py
```
```json
{
  "event_id": 32,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/32.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 21071,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/32.json",
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

### event 33

```json
{
  "event_id": 33,
  "agent_command_sequence": 15,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/33.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 27394,
    "decoded_characters": 12695
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/33.json",
  "timestamp": "2026-10-25T05:12:04.953956",
  "target_table_name_hits": [
    "stg_social_media__facebook_posts"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 13612,
  "retention": "full_original"
}
```
```bash
cat >> /tmp/write_sql.py <<'PY'
files['marts/social_media_reporting__rollup_report.sql'] = '''with all_posts as (
    select page_id, page_name, post_id, post_message, created_timestamp, platform,
           clicks, impressions, likes, shares, comments, post_url
    from intermediate.social_media_reporting__facebook_posts_reporting
    union all
    select page_id, page_name, post_id, post_message, created_timestamp, platform,
           clicks, impressions, likes, shares, comments, post_url
    from intermediate.social_media_reporting__instagram_posts_reporting
    union all
    select page_id, page_name, post_id, post_message, created_timestamp, platform,
           clicks, impressions, likes, shares, comments, post_url
    from intermediate.social_media_reporting__linkedin_posts_reporting
    union all
    select page_id, page_name, post_id, post_message, created_timestamp, platform,
           clicks, impressions, likes, shares, comments, post_url
    from intermediate.social_media_reporting__twitter_posts_reporting
    union all
    select page_id, page_name, post_id, post_message, created_timestamp, platform,
           clicks, impressions, likes, shares, comments, post_url
    from intermediate.social_media_reporting__youtube_videos_reporting
),
recent_posts as (
    select
        page_id, page_name, post_id, coalesce(post_message, '')::varchar as post_message,
        created_timestamp, platform,
        coalesce(clicks, 0)::hugeint as clicks,
        coalesce(impressions, 0)::hugeint as impressions,
        coalesce(likes, 0)::hugeint as likes,
        coalesce(shares, 0)::hugeint as shares,
        coalesce(comments, 0)::hugeint as comments,
        coalesce(post_url, '')::varchar as post_url
    from all_posts
    where created_timestamp is not null
      and ((platform = 'linkedin' and created_timestamp >= current_date - interval '4 years')
        or (platform <> 'linkedin' and created_timestamp >= current_date - interval '2 years'))
),
scored_posts as (
    select *,
        case when impressions > 0 then (clicks + likes + shares + comments)::double / impressions else 0.0 end as engagement_rate,
        case platform
            when 'facebook' then case when impressions > 0 then 75 else 50 end
            when 'instagram' then case when impressions > 0 then 90 else 50 end
            when 'twitter' then case when impressions > 0 then 80 else 50 end
            when 'youtube' then case when clicks > 0 then 95 else 50 end
            when 'linkedin' then case when impressions > 0 then 70 else 50 end
            else 50 end::integer as content_quality_score
    from recent_posts
),
ranked_posts as (
    select *,
        row_number() over (partition by platform, cast(created_timestamp as date) order by impressions desc) as daily_platform_rank,
        row_number() over (partition by platform order by impressions desc) as platform_lifetime_rank
    from scored_posts
)
select
    page_id, page_name, post_id, created_timestamp, platform, post_message, post_url,
    clicks, impressions, likes, shares, comments, engagement_rate, content_quality_score,
    daily_platform_rank, platform_lifetime_rank
from ranked_posts
order by created_timestamp desc, engagement_rate desc'''
files['marts/social_media_reporting__daily_kpis.sql'] = '''with platform_posts as (
    select platform, created_timestamp, page_id,
           coalesce(content_type, 'text') as content_type,
           clicks, impressions, likes, shares, comments
    from intermediate.social_media_reporting__facebook_posts_reporting
    union all
    select platform, created_timestamp, page_id,
           coalesce(content_format, 'Feed Post') as content_type,
           clicks, impressions, likes, shares, comments
    from intermediate.social_media_reporting__instagram_posts_reporting
    union all
    select platform, created_timestamp, page_id,
           coalesce(post_category, 'Text Post') as content_type,
           clicks, impressions, likes, shares, comments
    from intermediate.social_media_reporting__linkedin_posts_reporting
    union all
    select platform, created_timestamp, page_id,
           case
               when contains(lower(coalesce(post_message, '')), 'http://') or contains(lower(coalesce(post_message, '')), 'https://') then 'link'
               when contains(lower(coalesce(post_message, '')), 'image') or contains(lower(coalesce(post_message, '')), 'photo') then 'photo'
               when contains(lower(coalesce(post_message, '')), 'video') then 'video'
               else 'text' end as content_type,
           clicks, impressions, likes, shares, comments
    from intermediate.social_media_reporting__twitter_posts_reporting
    union all
    select platform, created_timestamp, page_id, 'video' as content_type,
           clicks, impressions, likes, shares, comments
    from intermediate.social_media_reporting__youtube_videos_reporting
),
normalized_posts as (
    select platform, cast(created_timestamp as date) as day, lower(content_type) as content_type,
           page_id, coalesce(clicks, 0) as clicks, coalesce(impressions, 0) as impressions,
           coalesce(likes, 0) as likes, coalesce(shares, 0) as shares,
           coalesce(comments, 0) as comments
    from platform_posts
    where created_timestamp is not null
),
daily_aggregates as (
    select platform, day, content_type,
           count(*)::bigint as posts_count,
           count(distinct page_id)::bigint as active_accounts_count,
           sum(clicks)::hugeint as clicks,
           sum(impressions)::hugeint as impressions,
           sum(likes)::hugeint as likes,
           sum(shares)::hugeint as shares,
           sum(comments)::hugeint as comments
    from normalized_posts
    group by platform, day, content_type
),
platform_bounds as (
    select platform, min(day) as first_day, max(day) as last_day
    from normalized_posts
    group by platform
),
date_spine as (
    select b.platform, cast(g.day_value as date) as day
    from platform_bounds b,
         generate_series(b.first_day, b.last_day - interval '1 day', interval '1 day') as g(day_value)
),
filled_daily as (
    select
        s.platform,
        s.day,
        coalesce(a.content_type, 'text') as content_type,
        coalesce(a.posts_count, 0)::bigint as posts_count,
        coalesce(a.active_accounts_count, 0)::bigint as active_accounts_count,
        coalesce(a.clicks, 0)::hugeint as clicks,
        coalesce(a.impressions, 0)::hugeint as impressions,
        coalesce(a.likes, 0)::hugeint as likes,
        coalesce(a.shares, 0)::hugeint as shares,
        coalesce(a.comments, 0)::hugeint as comments
    from date_spine s
    left join daily_aggregates a on a.platform = s.platform and a.day = s.day
)
select
    platform, day, content_type, posts_count, active_accounts_count,
    clicks, impressions, likes, shares, comments,
    case when impressions > 0 and active_accounts_count > 0 then clicks::double / impressions else 0.0 end as ctr,
    case when impressions > 0 then (clicks + likes + shares + comments)::double / impressions else 0.0 end as engagement_rate
from filled_daily'''
files['marts/social_media_reporting__retention_kpis.sql'] = '''with page_activity as (
    select 'facebook'::varchar as platform, page_id, date_trunc('week', created_timestamp)::date as activity_week
    from intermediate.social_media_reporting__facebook_posts_reporting where created_timestamp is not null
    union all
    select 'instagram', page_id, date_trunc('week', created_timestamp)::date
    from intermediate.social_media_reporting__instagram_posts_reporting where created_timestamp is not null
    union all
    select 'linkedin', page_id, date_trunc('week', created_timestamp)::date
    from intermediate.social_media_reporting__linkedin_posts_reporting where created_timestamp is not null
    union all
    select 'twitter', page_id, date_trunc('week', created_timestamp)::date
    from intermediate.social_media_reporting__twitter_posts_reporting where created_timestamp is not null
    union all
    select 'youtube', page_id, date_trunc('week', created_timestamp)::date
    from intermediate.social_media_reporting__youtube_videos_reporting where created_timestamp is not null
),
active_page_weeks as (
    select distinct platform, activity_week, page_id
    from page_activity
    where page_id is not null
),
page_cohorts as (
    select platform, page_id, min(activity_week) as cohort_week
    from active_page_weeks
    group by platform, page_id
),
cohort_sizes as (
    select platform, cohort_week, count(distinct page_id)::bigint as cohort_pages
    from page_cohorts
    group by platform, cohort_week
),
cohort_spine as (
    select c.platform, c.cohort_week, offsets.week_offset::bigint as week_offset,
           (c.cohort_week + offsets.week_offset * interval '1 week')::timestamp as target_week,
           c.cohort_pages
    from cohort_sizes c,
         unnest(range(0, 13)) as offsets(week_offset)
),
weekly_activity as (
    select platform, activity_week, count(distinct page_id)::bigint as retained_pages
    from active_page_weeks
    group by platform, activity_week
)
select
    s.platform,
    s.cohort_week,
    s.week_offset,
    s.target_week,
    s.cohort_pages,
    coalesce(a.retained_pages, 0)::bigint as retained_pages,
    case when s.cohort_pages > 0 then coalesce(a.retained_pages, 0)::double / s.cohort_pages else 0.0 end as retention_rate
from cohort_spine s
left join weekly_activity a
    on a.platform = s.platform and a.activity_week = cast(s.target_week as date)'''
files['marts/social_media_reporting__ctr_by_platform.sql'] = '''with platform_posts as (
    select platform, created_timestamp, page_id,
           coalesce(content_type, 'text') as content_type,
           clicks, impressions, likes, shares, comments
    from intermediate.social_media_reporting__facebook_posts_reporting
    union all
    select platform, created_timestamp, page_id,
           coalesce(content_format, 'feed post') as content_type,
           clicks, impressions, likes, shares, comments
    from intermediate.social_media_reporting__instagram_posts_reporting
    union all
    select platform, created_timestamp, page_id,
           coalesce(post_category, 'text post') as content_type,
           clicks, impressions, likes, shares, comments
    from intermediate.social_media_reporting__linkedin_posts_reporting
    union all
    select platform, created_timestamp, page_id,
           case
               when contains(lower(coalesce(post_message, '')), 'http://') or contains(lower(coalesce(post_message, '')), 'https://') then 'link'
               when contains(lower(coalesce(post_message, '')), 'image') or contains(lower(coalesce(post_message, '')), 'photo') then 'photo'
               when contains(lower(coalesce(post_message, '')), 'video') then 'video'
               else 'text' end as content_type,
           clicks, impressions, likes, shares, comments
    from intermediate.social_media_reporting__twitter_posts_reporting
    union all
    select platform, created_timestamp, page_id, 'video' as content_type,
           clicks, impressions, likes, shares, comments
    from intermediate.social_media_reporting__youtube_videos_reporting
),
normalized_posts as (
    select platform, date_trunc('month', created_timestamp)::date as month,
           lower(content_type) as content_type, page_id,
           coalesce(clicks, 0) as clicks, coalesce(impressions, 0) as impressions,
           coalesce(likes, 0) as likes, coalesce(shares, 0) as shares,
           coalesce(comments, 0) as comments
    from platform_posts
    where created_timestamp is not null
),
monthly_aggregates as (
    select platform, month, content_type,
           count(*)::bigint as posts_count,
           count(distinct page_id)::bigint as active_accounts_count,
           sum(clicks)::hugeint as clicks,
           sum(impressions)::hugeint as impressions,
           sum(likes)::hugeint as likes,
           sum(shares)::hugeint as shares,
           sum(comments)::hugeint as comments
    from normalized_posts
    group by platform, month, content_type
)
select
    platform, month, content_type, posts_count, active_accounts_count,
    clicks, impressions, likes, shares, comments,
    case when impressions > 0 and active_accounts_count > 0 then clicks::double / impressions else 0.0 end as ctr,
    case when impressions > 0 then (likes + shares + comments)::double / impressions else 0.0 end as engagement_rate
from monthly_aggregates'''
for name,sql in files.items():
 p=Path('sql')/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(sql+'\n')
PY
python /tmp/write_sql.py
find sql -type f | sort
```
```json
{
  "event_id": 34,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/34.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 27077,
    "decoded_characters": 917
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/34.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
sql/intermediate/social_media_reporting__facebook_posts_reporting.sql
sql/intermediate/social_media_reporting__instagram_posts_reporting.sql
sql/intermediate/social_media_reporting__linkedin_posts_reporting.sql
sql/intermediate/social_media_reporting__twitter_posts_reporting.sql
sql/intermediate/social_media_reporting__youtube_videos_reporting.sql
sql/marts/social_media_reporting__ctr_by_platform.sql
sql/marts/social_media_reporting__daily_kpis.sql
sql/marts/social_media_reporting__retention_kpis.sql
sql/marts/social_media_reporting__rollup_report.sql
sql/staging/stg_social_media__account_history.sql
sql/staging/stg_social_media__facebook_posts.sql
sql/staging/stg_social_media__instagram_posts.sql
sql/staging/stg_social_media__linkedin_posts.sql
sql/staging/stg_social_media__twitter_organic_tweets.sql
sql/staging/stg_social_media__twitter_user_history.sql
sql/staging/stg_social_media__youtube_videos.sql
```

### event 37

```json
{
  "event_id": 37,
  "agent_command_sequence": 17,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/37.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2592,
    "decoded_characters": 625
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/37.json",
  "timestamp": "2026-10-25T05:14:41.502133",
  "target_table_name_hits": [
    "stg_social_media__facebook_posts"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 2089,
  "retention": "full_original"
}
```
```bash
grep 'staging\.|intermediate\.|marts\.' /tmp/pipeline.log | tail -35; python - <<'PY'
import duckdb
c=duckdb.connect('social_media_reporting.duckdb',read_only=True)
for schema in ['staging','intermediate','marts']:
 for t,n in c.execute(f"select table_name, (select count(*) from "+schema+".\""+"'"+"'"+") from information_schema.tables where table_schema='"+schema+"'").fetchall() if False else []: pass
 for (t,) in c.execute(f"select table_name from information_schema.tables where table_schema='{schema}'").fetchall():
  print(schema,t,c.execute(f'select count(*) from {schema}."{t}"').fetchone()[0])
PY
ls -l sql/staging
```
```json
{
  "event_id": 38,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/38.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2275,
    "decoded_characters": 1464
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/38.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
staging stg_social_media__account_history 0
staging stg_social_media__facebook_posts 0
staging stg_social_media__instagram_posts 0
staging stg_social_media__linkedin_posts 100
staging stg_social_media__twitter_organic_tweets 0
staging stg_social_media__twitter_user_history 1
staging stg_social_media__youtube_videos 0
intermediate social_media_reporting__facebook_posts_reporting 0
intermediate social_media_reporting__instagram_posts_reporting 0
intermediate social_media_reporting__linkedin_posts_reporting 0
intermediate social_media_reporting__twitter_posts_reporting 0
intermediate social_media_reporting__youtube_videos_reporting 0
marts social_media_reporting__ctr_by_platform 0
marts social_media_reporting__daily_kpis 0
marts social_media_reporting__retention_kpis 0
marts social_media_reporting__rollup_report 0
total 28
-rw-r--r-- 1 katherine katherine  635 Oct 25 05:12 stg_social_media__account_history.sql
-rw-r--r-- 1 katherine katherine 1457 Oct 25 05:12 stg_social_media__facebook_posts.sql
-rw-r--r-- 1 katherine katherine 2755 Oct 25 05:12 stg_social_media__instagram_posts.sql
-rw-r--r-- 1 katherine katherine 1142 Oct 25 05:12 stg_social_media__linkedin_posts.sql
-rw-r--r-- 1 katherine katherine 2705 Oct 25 05:12 stg_social_media__twitter_organic_tweets.sql
-rw-r--r-- 1 katherine katherine 1449 Oct 25 05:12 stg_social_media__twitter_user_history.sql
-rw-r--r-- 1 katherine katherine 1770 Oct 25 05:12 stg_social_media__youtube_videos.sql
```

### event 39

```json
{
  "event_id": 39,
  "agent_command_sequence": 18,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/39.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2313,
    "decoded_characters": 529
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/39.json",
  "timestamp": "2026-10-25T05:14:46.632028",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "facebook_pages_post_history"
  ],
  "full_original_characters": 1986,
  "retention": "index_and_first_line_only",
  "first_line_original": "python - <<'PY'\n"
}
```
```json
{
  "event_id": 40,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/40.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1996,
    "decoded_characters": 1457
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/40.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 43

```json
{
  "event_id": 43,
  "agent_command_sequence": 20,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/43.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1911,
    "decoded_characters": 329
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/43.json",
  "timestamp": "2026-10-25T05:15:04.857610",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "facebook_pages_post_history"
  ],
  "full_original_characters": 5297,
  "retention": "index_and_first_line_only",
  "first_line_original": "python - <<'PY'\n"
}
```
```json
{
  "event_id": 44,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/44.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1594,
    "decoded_characters": 4968
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/44.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 45

```json
{
  "event_id": 45,
  "agent_command_sequence": 21,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/45.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2964,
    "decoded_characters": 845
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/45.json",
  "timestamp": "2026-10-25T05:15:14.867909",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "raw.facebook_pages_post_history",
    "facebook_pages_post_history"
  ],
  "full_original_characters": 1484,
  "retention": "index_and_first_line_only",
  "first_line_original": "python - <<'PY'\n"
}
```
```json
{
  "event_id": 46,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/46.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2647,
    "decoded_characters": 639
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/46.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 49

```json
{
  "event_id": 49,
  "agent_command_sequence": 23,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/49.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2041,
    "decoded_characters": 391
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/49.json",
  "timestamp": "2026-10-25T05:15:54.287745",
  "target_table_name_hits": [
    "stg_social_media__facebook_posts"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 1991,
  "retention": "full_original"
}
```
```bash
python - <<'PY'
from pathlib import Path
for p in Path('sql').rglob('*.sql'):
 s=p.read_text()
 assert not s.rstrip().endswith(';'), p
 assert 'ref(' not in s.lower(), p
 print(f'{p}: {len(s.splitlines())} lines, {len(s)} bytes')
PY
python run.py > /tmp/pipeline_rerun.log 2>&1; echo rerun_exit:$?; grep -E 'layer complete|Errors occurred|pipeline execution complete' /tmp/pipeline_rerun.log
```
```json
{
  "event_id": 50,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/50.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1724,
    "decoded_characters": 1600
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/50.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
sql/marts/social_media_reporting__rollup_report.sql: 60 lines, 3142 bytes
sql/marts/social_media_reporting__ctr_by_platform.sql: 56 lines, 2898 bytes
sql/marts/social_media_reporting__daily_kpis.sql: 80 lines, 3834 bytes
sql/marts/social_media_reporting__retention_kpis.sql: 54 lines, 2361 bytes
sql/staging/stg_social_media__youtube_videos.sql: 31 lines, 1770 bytes
sql/staging/stg_social_media__account_history.sql: 17 lines, 635 bytes
sql/staging/stg_social_media__linkedin_posts.sql: 25 lines, 1142 bytes
sql/staging/stg_social_media__facebook_posts.sql: 32 lines, 1457 bytes
sql/staging/stg_social_media__instagram_posts.sql: 51 lines, 2755 bytes
sql/staging/stg_social_media__twitter_user_history.sql: 33 lines, 1449 bytes
sql/staging/stg_social_media__twitter_organic_tweets.sql: 58 lines, 2705 bytes
sql/intermediate/social_media_reporting__linkedin_posts_reporting.sql: 43 lines, 1468 bytes
sql/intermediate/social_media_reporting__twitter_posts_reporting.sql: 61 lines, 2266 bytes
sql/intermediate/social_media_reporting__instagram_posts_reporting.sql: 34 lines, 1527 bytes
sql/intermediate/social_media_reporting__facebook_posts_reporting.sql: 59 lines, 2280 bytes
sql/intermediate/social_media_reporting__youtube_videos_reporting.sql: 46 lines, 1694 bytes
rerun_exit:0
2026-10-25 05:15:54,553 - INFO - STAGING layer complete: 7/7 tables created successfully
2026-10-25 05:15:54,584 - INFO - INTERMEDIATE layer complete: 5/5 tables created successfully
2026-10-25 05:15:54,618 - INFO - MARTS layer complete: 4/4 tables created successfully
🎉 Social media data pipeline execution complete!
```

## result_md_table_sentences

```json
{
  "present": true,
  "path": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md",
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md",
  "sha256": "4fa02286da75b623258ea6e5642f22c03c2ca45c73855639ece14bfdf5aece9c",
  "sentences": [],
  "policy": "All sentences naming the table; includes sentences without 008 keywords. Existing D10 ids attached where applicable."
}
```

## original_files

```json
{
  "paths": [
    "/home/katherine/Assumption_Ledger/data/011_agent_alignment/impl-023/stg_social_media__facebook_posts_2025-10-17.duckdb",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/10.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/11.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/12.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/13.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/14.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/15.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/16.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/23.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/24.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/29.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/30.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/31.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/32.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/33.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/34.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/37.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/38.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/39.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/40.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/43.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/44.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/45.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/46.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/49.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/50.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/7.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/8.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/9.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql",
    "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml",
    "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql"
  ],
  "archive": "/home/katherine/Assumption_Ledger/traces/dacomp_deimpl_prev.tar.gz",
  "gold_SQL_search_root": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql",
  "gold_SQL_search_names": [
    "stg_social_media__facebook_posts",
    "stg_social_media__facebook_posts"
  ],
  "source_fingerprints": "records/012_input_before.json"
}
```
