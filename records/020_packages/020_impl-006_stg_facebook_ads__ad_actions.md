# impl-006 | staging | stg_facebook_ads__ad_actions | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:581–647

```yaml
    - name: "stg_facebook_ads__ad_actions"
      description: "Staging table for Facebook Ads  Ad Actions"
      columns:
        - name: "platform"
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "UPPER(platform) = 'FACEBOOK_ADS'"
              on_failure: delete_row
        - name: "ad_id"
          data_type: VARCHAR
          constraints: [not_null]
        - name: "date_day"
          data_type: DATE
          constraints: [not_null]
          validation_rules:
            - rule: "date_day IS NOT NULL AND date_day >= '2020-01-01' AND date_day <= CURRENT_DATE"
              on_failure: delete_row
            - rule: "date_day NOT IN ('1970-01-01','1900-01-01','9999-12-31')"
              on_failure: delete_row
        - name: "action_type"
          data_type: VARCHAR
          constraints: [not_null]
        - name: "action_1_d_view"
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "action_1_d_view >= 0"
              on_failure: correct
            - rule: "action_1_d_view = ROUND(action_1_d_view, 2)"
              on_failure: correct
            - rule: "action_1_d_view IS NOT NULL OR action_1_d_view = 0"
              on_failure: correct
        - name: "action_7_d_click"
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "action_7_d_click >= 0"
              on_failure: correct
            - rule: "action_7_d_click = ROUND(action_7_d_click, 2)"
              on_failure: correct
            - rule: "action_7_d_click IS NOT NULL OR action_7_d_click = 0"
              on_failure: correct
        - name: "action_value"
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "action_value >= 0"
              on_failure: correct
            - rule: "action_value = ROUND(action_value, 2)"
              on_failure: correct
            - rule: "action_value IS NOT NULL OR action_value = 0"
              on_failure: correct
        - name: "inline_value"
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "inline_value >= 0"
              on_failure: correct
            - rule: "inline_value = ROUND(inline_value, 2)"
              on_failure: correct
            - rule: "inline_value IS NOT NULL OR inline_value = 0"
              on_failure: correct
        - name: "is_index_action"
          data_type: BOOLEAN
        - name: "_dbt_loaded_at"
          data_type: TIMESTAMP WITH TIME ZONE
          constraints: [not_null]
          validation_rules:
            - rule: "_dbt_loaded_at <= CURRENT_TIMESTAMP"
              on_failure: delete_row
```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT * FROM raw.facebook_ads_basic_ad_actions_data
),
cleaned AS (
    SELECT
        'FACEBOOK_ADS' AS platform,
        CAST(TRY_CAST("ad_id" AS VARCHAR) AS VARCHAR) AS ad_id,
        CAST(TRY_CAST(date AS DATE) AS DATE) AS date_day,
        TRY_CAST("action_type" AS VARCHAR) AS action_type,
        CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS action_1_d_view,
        CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS action_7_d_click,
        CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS action_value,
        CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS inline_value,
        CAST(NULL::BOOLEAN AS BOOLEAN) AS is_index_action,
        CURRENT_TIMESTAMP AS _dbt_loaded_at
    FROM source_rows
)
SELECT * FROM cleaned
```

## gold SQL（仅供定位差异）

S5

```sql
-- Facebook Ads Ad Actions Staging Model
-- Standardizes raw Facebook Ads action data for downstream consumption
-- Removes Fivetran-specific logic and converts to DuckDB-compatible SQL
-- Includes data quality validation rules per staging_data_specification.yaml

SELECT
    -- Platform Identifier (Rule 1: Platform name standardization)
    UPPER(TRIM('facebook_ads')) AS platform,

    -- Primary Keys
    CAST(TRIM(ad_id) AS VARCHAR) AS ad_id,

    CAST(
        CASE
            WHEN date IS NULL THEN NULL
            WHEN CAST(date AS DATE) < '2020-01-01' OR CAST(date AS DATE) > CURRENT_DATE THEN NULL
            WHEN CAST(date AS DATE) IN ('1970-01-01', '1900-01-01', '9999-12-31') THEN NULL
            ELSE date
        END AS DATE
    ) AS date_day,

    CAST(TRIM(action_type) AS VARCHAR) AS action_type,

    -- Action Attribution Windows (handle negative values)
    CAST(
        CASE
            WHEN _1_d_view < 0 THEN 0.0
            WHEN _1_d_view IS NULL THEN 0.0
            ELSE ROUND(_1_d_view, 2)
        END AS DECIMAL(18,2)
    ) AS action_1_d_view,

    CAST(
        CASE
            WHEN _7_d_click < 0 THEN 0.0
            WHEN _7_d_click IS NULL THEN 0.0
            ELSE ROUND(_7_d_click, 2)
        END AS DECIMAL(18,2)
    ) AS action_7_d_click,

    -- Action Metrics (handle negative values)
    CAST(
        CASE
            WHEN value < 0 THEN 0.0
            WHEN value IS NULL THEN 0.0
            ELSE ROUND(value, 2)
        END AS DECIMAL(18,2)
    ) AS action_value,

    CAST(
        CASE
            WHEN inline < 0 THEN 0.0
            WHEN inline IS NULL THEN 0.0
            ELSE ROUND(inline, 2)
        END AS DECIMAL(18,2)
    ) AS inline_value,

    -- Index Flag
    CASE
        WHEN index = 'True' THEN TRUE
        WHEN index = 'False' THEN FALSE
        ELSE FALSE
    END AS is_index_action,

    -- Data Quality (corrected datatype)
    CAST(CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE) AS _dbt_loaded_at

FROM raw.facebook_ads_basic_ad_actions_data

WHERE date IS NOT NULL
    AND ad_id IS NOT NULL
    AND action_type IS NOT NULL
    -- Apply validation as per YAML specification
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 700 | 700 | 0 | 0 | 1 | 1 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"ad_id":"6215293456071","date_day":"2023-05-04"}</code> |
| K2 | <code>{"ad_id":"6215293456071","date_day":"2024-08-21"}</code> |
| K3 | <code>{"ad_id":"6215304566671","date_day":"2023-11-14"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| ad_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| date_day | 0 | 0 | 0 | DATE | DATE |
| action_1_d_view | 700 | 700 | 700 | DECIMAL(18,2) | DECIMAL(18,2) |
| action_7_d_click | 700 | 700 | 700 | DECIMAL(18,2) | DECIMAL(18,2) |
| action_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| action_value | 700 | 700 | 700 | DECIMAL(18,2) | DECIMAL(18,2) |
| inline_value | 700 | 700 | 700 | DECIMAL(18,2) | DECIMAL(18,2) |
| is_index_action | 700 | 700 | 700 | BOOLEAN | BOOLEAN |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |

action_1_d_view 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 529.31 |
| K2 | null | 537.08 |
| K3 | null | 738.51 |

action_7_d_click 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 633.79 |
| K2 | null | 217.41 |
| K3 | null | 501.39 |

action_value 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 344.95 |
| K2 | null | 733.21 |
| K3 | null | 508.16 |

inline_value 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 829.09 |
| K2 | null | 794.94 |
| K3 | null | 157.72 |

is_index_action 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | false |
| K2 | null | false |
| K3 | null | true |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>5列；[{"column":"action_1_d_view","table_rows":700},{"column":"action_7_d_click","table_rows":700},{"column":"action_value","table_rows":700}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"platform","value":"FACEBOOK_ADS"},{"column":"_dbt_loaded_at","value":"2026-10-25 01:52:29.238884+08"}]</code> |
| B5_null_literal_output | <code>5输出列；[{"column":"action_1_d_view","expression":["CAST(CAST(NULL AS DECIMAL(18, 2)) AS DECIMAL(18, 2))"]},{"column":"action_7_d_click","expression":["CAST(CAST(NULL AS DECIMAL(18, 2)) AS DECIMAL(18, 2))"]},{"column":"action_value","expression":["CAST(CAST(NULL AS DECIMAL(18, 2)) AS DECIMAL(18, 2))"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"platform","expression":["'FACEBOOK_ADS'"]}]</code> |
| C9_agent_runtime_text | <code>S4:15 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:16 CURRENT_DATE；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:597 CURRENT_DATE；命中数=2</code> |

## 轨迹索引（不放输出原文）

本题事件总数：99；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort &amp;&amp; cat config/layer_dependencies.yaml</code> | 7365 | true | false |
| 11 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting_start.duckdb',read_only=True)<br>print(c.execute('show all tables').fetchall()[:100])<br>PY</code> | 52227 | false | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('ad_reporting_start.yaml'))<br>print(type(x), x.keys())<br>print(str(x)[:2500])<br>PY</code> | 7232 | false | false |
| 17 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting_start.duckdb',read_only=True)<br>for r in c.execute("select table_name from information_schema.tables where table_schema='raw' order by 1").fe</code> | 26086 | false | false |
| 19 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml,duckdb,os,re<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>con=duckdb.connect('ad_reporting_start.duckdb',r</code> | 528 | false | false |
| 37 | run | <code>python run.py &gt; /tmp/runlog3 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog3;</code> | 6937 | true | false |
| 81 | run | <code>find sql -type f &#124; wc -l; grep -R ';' sql --include='*.sql' &#124; head; git status --short 2&gt;/dev/null &#124;&#124; true; python - &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c[</code> | 999 | true | false |
| 85 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=yaml.safe_load(open('docs/data_contract.yaml')); d=duckdb.connect('ad_reporting.duckdb',read_only=True)<br>for layer,key in [('staging','staging_contract'),('intermed</code> | 776 | true | false |

### agent action 的 thought/message 命中原句

未找到命中原句。

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_actions.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_actions.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_stg_facebook_ads__ad_actions/020_impl-006_stg_facebook_ads__ad_actions.json`
- S11: `data/011_agent_alignment/impl-006_attempt_01/stg_facebook_ads__ad_actions_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
