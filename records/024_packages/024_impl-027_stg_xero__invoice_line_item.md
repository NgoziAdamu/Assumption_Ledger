# impl-027 | staging | stg_xero__invoice_line_item | 差异：S1；日期 原记录

## 契约完整原文

S3:128–171

```yaml
    - name: stg_xero__invoice_line_item
      description: "Invoice line items with validated pricing amounts aligned to current SQL behavior."
      source_table: raw.xero_invoice_line_item_data
      columns:
        - name: line_item_id
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "line_item_id is present"
              on_failure: delete_row
        - name: invoice_id
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "invoice_id is present"
              on_failure: delete_row
        - name: account_code
          data_type: VARCHAR
        - name: description
          data_type: VARCHAR
        - name: discount_entered_as_percent
          data_type: BOOLEAN
        - name: discount_rate
          data_type: DECIMAL(18,2)
        - name: item_code
          data_type: VARCHAR
        - name: line_amount
          data_type: DECIMAL(18,2)
        - name: quantity
          data_type: DECIMAL(18,2)
        - name: tax_amount
          data_type: DECIMAL(18,2)
        - name: tax_type
          data_type: VARCHAR
        - name: unit_amount
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "If unit_amount is NULL or not a numeric value with up to 2 decimals, delete row"
              on_failure: delete_row
            - rule: "If unit_amount outside [-1000000, 1000000], delete row"
              on_failure: delete_row
        - name: processed_at
          data_type: TIMESTAMP

```

## agent 最终 SQL

S4

```sql
SELECT
    line_item_id::VARCHAR AS line_item_id,
    invoice_id::VARCHAR AS invoice_id,
    account_code::VARCHAR AS account_code,
    description::VARCHAR AS description,
    discount_entered_as_percent::BOOLEAN AS discount_entered_as_percent,
    TRY_CAST(discount_rate AS DECIMAL(18, 2)) AS discount_rate,
    item_code::VARCHAR AS item_code,
    TRY_CAST(line_amount AS DECIMAL(18, 2)) AS line_amount,
    TRY_CAST(quantity AS DECIMAL(18, 2)) AS quantity,
    TRY_CAST(tax_amount AS DECIMAL(18, 2)) AS tax_amount,
    tax_type::VARCHAR AS tax_type,
    TRY_CAST(unit_amount AS DECIMAL(18, 2)) AS unit_amount,
    TRY_CAST(_fivetran_synced AS TIMESTAMP) AS processed_at
FROM raw.xero_invoice_line_item_data
WHERE NULLIF(trim(line_item_id), '') IS NOT NULL
  AND NULLIF(trim(invoice_id), '') IS NOT NULL
  AND unit_amount IS NOT NULL
  AND unit_amount = round(unit_amount, 2)
  AND unit_amount BETWEEN -1000000 AND 1000000
```

## gold SQL（仅供定位差异）

S5

```sql
-- Staging table for xero invoice line item data with unit amount cleaning

WITH raw_data AS (
    SELECT
        _fivetran_synced,
        account_code,
        description,
        discount_entered_as_percent,
        discount_rate,
        invoice_id,
        item_code,
        line_amount,
        line_item_id,
        quantity,
        tax_amount,
        tax_type,
        unit_amount,
        validation_errors
    FROM raw.xero_invoice_line_item_data
),

cleaned_data AS (
    SELECT
        -- Remove fivetran metadata
        account_code,
        description,
        discount_entered_as_percent,
        discount_rate,
        invoice_id,
        item_code,
        line_amount,
        line_item_id,
        quantity,
        tax_amount,
        tax_type,

        -- Apply validation rules for unit_amount (format -> nullify_field; range -> delete_row; completeness -> delete_row)
        CASE
            -- Nullify if format invalid (allow optional sign and up to 2 decimals)
            WHEN unit_amount IS NOT NULL AND NOT (CAST(unit_amount AS VARCHAR) ~ '^-?\d+(\.\d{1,2})?$') THEN NULL
            -- Keep as-is when format valid
            ELSE unit_amount
        END AS unit_amount,

        CURRENT_TIMESTAMP AS processed_at

    FROM raw_data
    WHERE line_item_id IS NOT NULL
      AND invoice_id IS NOT NULL
)

SELECT
    account_code,
    description,
    discount_entered_as_percent,
    discount_rate,
    invoice_id,
    item_code,
    line_amount,
    line_item_id,
    quantity,
    tax_amount,
    tax_type,
    unit_amount,
    processed_at
FROM cleaned_data
WHERE line_item_id IS NOT NULL
  AND invoice_id IS NOT NULL
  -- completeness: must have unit_amount
  AND unit_amount IS NOT NULL
  -- range: delete rows out of range
  AND unit_amount >= -1000000 AND unit_amount <= 1000000
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5000 | 5000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"invoice_id":"005de91d-48b2-4b47-a566-c0bbc670c5ae","line_item_id":"b684219f-ed33-4fd3-9d2e-74cfeff03df8"}</code> |
| K2 | <code>{"invoice_id":"012c6caf-bd7a-4f50-9112-7ca0d295e082","line_item_id":"e7c84a14-4d84-47b1-8c51-df208205c9fc"}</code> |
| K3 | <code>{"invoice_id":"012c6caf-bd7a-4f50-9112-7ca0d295e082","line_item_id":"f86d13b8-311e-4264-905d-027ea1ccbee7"}</code> |
| K4 | <code>{"invoice_id":"00dfece3-931d-44e3-9456-d0bbae2645bf","line_item_id":"880838d6-e2fd-4328-a0f5-187875ce617b"}</code> |
| K5 | <code>{"invoice_id":"012c6caf-bd7a-4f50-9112-7ca0d295e082","line_item_id":"53f5ac00-f131-4fa6-8b16-82dd10580a69"}</code> |
| K6 | <code>{"invoice_id":"014b1783-656d-4fcc-9901-82efa10327e3","line_item_id":"d8632738-7f6a-4ca2-9803-007bff0c923e"}</code> |
| K7 | <code>{"invoice_id":"000469e9-3580-4c72-bfb8-fe46e25eb08b","line_item_id":"47f1cb08-9952-48a3-9e5d-28523e4fb9fb"}</code> |
| K8 | <code>{"invoice_id":"005de91d-48b2-4b47-a566-c0bbc670c5ae","line_item_id":"14b2f4db-b97c-496c-9107-636a54ec4918"}</code> |
| K9 | <code>{"invoice_id":"0073ce09-524d-4e46-a5c2-da4610bde52e","line_item_id":"5bd6b9fe-1cbc-42de-a388-9a3065428500"}</code> |
| K10 | <code>{"invoice_id":"00a3f03e-3695-4460-9632-eb72bfc97ad2","line_item_id":"c55db230-3a8f-4b55-a673-83a356a31994"}</code> |
| K11 | <code>{"invoice_id":"017e7235-6be9-4f97-8e7a-ca909b60ef4a","line_item_id":"dbb13edf-299b-4a8f-88f7-f33fb81ec3a4"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_code | 0 | 0 | 0 | VARCHAR | BIGINT |
| description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| discount_entered_as_percent | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| discount_rate | 424 | 424 | 424 | DECIMAL(18,2) | DOUBLE |
| invoice_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| item_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| line_amount | 834 | 834 | 834 | DECIMAL(18,2) | DOUBLE |
| line_item_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| quantity | 4937 | 4937 | 4937 | DECIMAL(18,2) | DOUBLE |
| tax_amount | 1611 | 1611 | 1611 | DECIMAL(18,2) | DOUBLE |
| tax_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| unit_amount | 814 | 814 | 814 | DECIMAL(18,2) | DOUBLE |

discount_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 14.10 | 14.1 |
| K2 | 8.30 | 8.3 |
| K3 | 14.70 | 14.7 |

line_amount 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | 3667.10 | 3667.1 |
| K5 | 3750.00 | 3750.0 |
| K6 | 20.00 | 20.0 |

quantity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K7 | 1.00 | 1.0 |
| K8 | 47.81 | 47.8107 |
| K1 | 30.59 | 30.5936 |

tax_amount 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K8 | 2865.70 | 2865.7 |
| K9 | 2756.30 | 2756.3 |
| K10 | 3497.60 | 3497.6 |

unit_amount 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | 3750.00 | 3750.0 |
| K6 | 20.00 | 20.0 |
| K11 | 9.00 | 9.0 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| C9_gold_runtime_text | <code>S5:45 CURRENT_TIMESTAMP；命中数=1</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory  'line amount domain':"select count(*) filter(where unit_amount is null or abs(unit_amount)&gt;1000000) invalid from staging.stg_xero__invoice_line_item",</code> |

## 轨迹索引（不放输出原文）

本题事件总数：43；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find . -maxdepth 3 -type f &#124; sort &#124; head -200</code> | 1650 | false | false |
| 7 | run | <code>find sql -type f -maxdepth 4 -print -exec wc -l {} \; &amp;&amp; cat config/layer_dependencies.yaml</code> | 1748 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9771 | true | false |
| 11 | run | <code>cat xero_start.yaml &amp;&amp; cat docs/data_contract.yaml &#124; wc -l</code> | 2853 | false | false |
| 17 | run | <code>sed -n '1,220p' test_single_sql.py &amp;&amp; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('xero_start.duckdb',read_only=True)<br>for t in c.execute('show tables from raw').fetchall():<br> print('\n',t[0],c.execu</code> | 13602 | false | false |
| 19 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>stages={<br>'stg_xero__account':('xero_account_data', '''    account_id::VARCHAR AS account_id,<br>    na</code> | 0 | false | false |
| 21 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br><br>def write(layer,name,sql): Path(f'sql/{layer}/{name}.sql').write_text(sql.strip()+'\n')<br>write('intermediate','int_xero__tracking_categories_with_o</code> | 0 | false | false |
| 25 | run | <code>python run.py &gt; /tmp/run.log 2&gt;&amp;1; status=$?; tail -100 /tmp/run.log; exit $status</code> | 7453 | true | false |
| 27 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('xero.duckdb',read_only=True)<br>for q in ["select count(*),count(distinct line_item_id) from intermediate.int_xero__invoice_line_items_enriched", "select l</code> | 1073 | true | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('xero.duckdb',read_only=True)<br>checks={<br> 'invoice_item_enriched_pk':"select count(*) total, count(distinct line_item_id) distinct_ids, count(*) filter(whe</code> | 214 | false | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
'stg_xero__invoice_line_item':('xero_invoice_line_item_data', '''    line_item_id::VARCHAR AS line_item_id,
```
event 21 / message

```text
    FROM staging.stg_xero__invoice_line_item
```
event 27 / message

```text
for q in ["select count(*),count(distinct line_item_id) from intermediate.int_xero__invoice_line_items_enriched", "select line_item_id,count(*) n from intermediate.int_xero__invoice_line_items_enriched group by 1 having count(*)>1 order by n desc limit 10", "select account_code,count(*) n from staging.stg_xero__account group by 1 having count(*)>1 order by n desc limit 15", "select count(*) from staging.stg_xero__invoice_line_item"]:
```
event 31 / message

```text
 'line amount domain':"select count(*) filter(where unit_amount is null or abs(unit_amount)>1000000) invalid from staging.stg_xero__invoice_line_item",
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-027.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/staging/stg_xero__invoice_line_item.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/staging/stg_xero__invoice_line_item.sql`
- S6: `records/006_contract_impl-027.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/result.md`
- S10: `data/024_packages_work/024_impl-027_stg_xero__invoice_line_item/024_impl-027_stg_xero__invoice_line_item.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/xero.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions`
