# impl-003 | staging | stg_customer360__country_codes | 差异：S1；日期 原记录

## 契约完整原文

S3:31–68

```yaml
    - name: stg_customer360__country_codes
      description: "Standardized country code reference data supporting ISO 3166 standards for geographic data validation and normalization"
      source_table: raw.country_codes
      columns:
        - name: country_name
          data_type: VARCHAR(255)
          constraints: [not_null]
          validation_rules:
            - rule: "LENGTH(TRIM(country_name)) > 0"
              on_failure: delete_row
        - name: alternative_country_name
          data_type: VARCHAR(255)
        - name: country_code_numeric
          data_type: INTEGER
          validation_rules:
            - rule: "country_code_numeric BETWEEN 1 AND 999"
              on_failure: nullify_field
        - name: country_code_alpha_2
          data_type: VARCHAR(2)
          constraints: [not_null, unique]
          validation_rules:
            - rule: "LENGTH(country_code_alpha_2) = 2"
              on_failure: delete_row
            - rule: "country_code_alpha_2 = UPPER(TRIM(country_code_alpha_2))"
              on_failure: correct
            - rule: "country_code_alpha_2 ~ '^[A-Z]{2}$'"
              on_failure: delete_row
        - name: country_code_alpha_3
          data_type: VARCHAR(3)
          constraints: [not_null]
          validation_rules:
            - rule: "LENGTH(country_code_alpha_3) = 3"
              on_failure: delete_row
            - rule: "country_code_alpha_3 = UPPER(TRIM(country_code_alpha_3))"
              on_failure: correct
            - rule: "country_code_alpha_3 ~ '^[A-Z]{3}$'"
              on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
with cleaned as (
    select
        nullif(trim(country_name), '') as country_name,
        nullif(trim(alternative_country_name), '') as alternative_country_name,
        case when country_code_numeric between 1 and 999 then country_code_numeric::integer end as country_code_numeric,
        upper(trim(country_code_alpha_2)) as country_code_alpha_2,
        upper(trim(country_code_alpha_3)) as country_code_alpha_3
    from raw.country_codes
    where country_name is not null and length(trim(country_name)) > 0
      and length(trim(country_code_alpha_2)) = 2
      and regexp_matches(upper(trim(country_code_alpha_2)), '^[A-Z]{2}$')
      and length(trim(country_code_alpha_3)) = 3
      and regexp_matches(upper(trim(country_code_alpha_3)), '^[A-Z]{3}$')
), deduplicated as (
    select *, row_number() over (partition by country_code_alpha_2 order by country_name, country_code_alpha_3) as _row_num
    from cleaned
)
select country_name, alternative_country_name, country_code_numeric, country_code_alpha_2, country_code_alpha_3
from deduplicated
where _row_num = 1
```

## gold SQL（仅供定位差异）

S5

```sql
with source as (
    select
        country_name,
        alternative_country_name,
        country_code_numeric,
        country_code_alpha_2,
        country_code_alpha_3
    from raw.country_codes
),

cleaned as (
    select
        country_name,
        alternative_country_name,
        case when country_code_numeric between 1 and 999 then country_code_numeric else null end as country_code_numeric,
        upper(trim(country_code_alpha_2)) as country_code_alpha_2,
        upper(trim(country_code_alpha_3)) as country_code_alpha_3
    from source
),

validated as (
    select *
    from cleaned
    where country_name is not null
      and length(trim(country_name)) > 0
      and country_code_alpha_2 ~ '^[A-Z]{2}$'
      and country_code_alpha_3 ~ '^[A-Z]{3}$'
)

select distinct * from validated
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 30 | 31 | 0 | 0 | 0 | 1 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"country_code_alpha_2":"vg"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| country_name | 0 | 0 | 1 | VARCHAR | VARCHAR |
| alternative_country_name | 0 | 0 | 1 | VARCHAR | VARCHAR |
| country_code_numeric | 0 | 0 | 1 | INTEGER | BIGINT |
| country_code_alpha_2 | 0 | 0 | 1 | VARCHAR | VARCHAR |
| country_code_alpha_3 | 0 | 0 | 1 | VARCHAR | VARCHAR |

country_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Virgin Islands (British)","rows":1}]</code> | <code>[{"value":"Virgin Islands (British)","rows":1},{"value":"Virtual Country Gamma","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

alternative_country_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"British Virgin Islands","rows":1}]</code> | <code>[{"value":"British Virgin Islands","rows":1},{"value":"VCG","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

country_code_numeric 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"92","rows":1}]</code> | <code>[{"value":"92","rows":1},{"value":"997","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

country_code_alpha_2 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"VG","rows":1}]</code> | <code>[{"value":"VG","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

country_code_alpha_3 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"VGB","rows":1}]</code> | <code>[{"value":"VCG","rows":1},{"value":"VGB","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| D10_keyword_in_any_result_field | <code>命中数=3；task_instruction_not_agent_report         description: Alternative country name from stg_customer360__country_codes; null if no match</code> |

## 轨迹索引（不放输出原文）

本题事件总数：53；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 3128 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 11047 | true | false |
| 13 | run | cat customer360_start.yaml | 4237 | false | false |
| 15 | run | <code>find sql -type f -printf '%p %s bytes\n' &#124; sort; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('customer360_start.duckdb',read_only=True)<br>print(c.execute('show all tables').fetchall())<br>for t in ['mar</code> | 5054 | false | false |
| 17 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>P=Path('sql')<br>def put(layer,name,sql):<br>    (P/layer/f'{name}.sql').write_text(sql.strip()+"\n")<br># STAGING</code> | 0 | false | false |
| 23 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br># Generic distinct/index profile marts<br>put('marts','customer360__email', '''<br>with email_rows as (<br> select m.customer360_id, s.email from marts.customer360__mapping m inner j</code> | 0 | false | false |
| 29 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7140 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('customer360.duckdb',read_only=True)<br>checks={<br>'status_key_dups':"select count(*) from (select customer360_id from marts.customer360__status group by 1 ha</code> | 616 | false | false |

### agent action 的 thought/message 命中原句

event 17 / message

```text
put('staging','stg_customer360__country_codes', '''
```
event 17 / message

```text
inner join staging.stg_customer360__country_codes cc
```
event 23 / message

```text
 left join staging.stg_customer360__country_codes cc on a.country_code=cc.country_code_alpha_2
```
event 45 / message

```text
'country_code_invalid':"select count(*) from staging.stg_customer360__country_codes where length(country_code_alpha_2)<>2 or length(country_code_alpha_3)<>3",
```
event 45 / message

```text
'country_unique':"select count(*) from (select country_code_alpha_2 from staging.stg_customer360__country_codes group by 1 having count(*)>1)",
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-003.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/staging/stg_customer360__country_codes.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/staging/stg_customer360__country_codes.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `data/019_packages_work/019_impl-003_stg_customer360__country_codes/019_impl-003_stg_customer360__country_codes.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/customer360.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
