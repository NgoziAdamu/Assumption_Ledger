# impl-003 | staging | stg_customer360__state_territory_codes | 差异：S1；日期 原记录

## 契约完整原文

S3:69–96

```yaml
    - name: stg_customer360__state_territory_codes
      description: "Standardized state and territory code reference data with country relationships for address validation"
      source_table: raw.state_territory_codes
      columns:
        - name: state_territory
          data_type: VARCHAR(255)
          constraints: [not_null]
        - name: state_code
          data_type: VARCHAR(5)
          constraints: [not_null]
          validation_rules:
            - rule: "LENGTH(TRIM(state_code)) BETWEEN 2 AND 5"
              on_failure: delete_row
            - rule: "state_code = UPPER(TRIM(state_code))"
              on_failure: correct
        - name: alpha2_country_code
          data_type: VARCHAR(2)
          constraints: [not_null]
          validation_rules:
            - rule: "LENGTH(alpha2_country_code) = 2"
              on_failure: delete_row
            - rule: "alpha2_country_code = UPPER(TRIM(alpha2_country_code))"
              on_failure: correct
            - rule: "regexp_matches(alpha2_country_code, '^[A-Z]{2}$')" 
              on_failure: delete_row
            - rule: "alpha2_country_code IN (SELECT country_code_alpha_2 FROM stg_customer360__country_codes)"
              on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
with cleaned as (
    select
        nullif(trim(state_territory), '') as state_territory,
        upper(trim(state_code)) as state_code,
        upper(trim(alpha2_country_code)) as alpha2_country_code
    from raw.state_territory_codes
    where state_territory is not null and trim(state_territory) <> ''
      and state_code is not null and length(trim(state_code)) between 2 and 5
      and alpha2_country_code is not null and length(trim(alpha2_country_code)) = 2
      and regexp_matches(upper(trim(alpha2_country_code)), '^[A-Z]{2}$')
)
select c.state_territory, c.state_code, c.alpha2_country_code
from cleaned c
inner join staging.stg_customer360__country_codes cc
    on c.alpha2_country_code = cc.country_code_alpha_2
```

## gold SQL（仅供定位差异）

S5

```sql
with source as (
    select
        state_territory,
        state_code,
        alpha2_country_code
    from raw.state_territory_codes
),

cleaned as (
    select
        state_territory,
        upper(trim(state_code)) as state_code,
        upper(trim(alpha2_country_code)) as alpha2_country_code
    from source
),

validated as (
    select *
    from cleaned c
    where c.state_territory is not null
      and c.state_code is not null
      and length(trim(c.state_code)) between 2 and 5
      and c.alpha2_country_code is not null
      and length(c.alpha2_country_code) = 2
      and c.alpha2_country_code ~ '^[A-Z]{2}$'
      and exists (
        select 1
        from staging.stg_customer360__country_codes cc
        where cc.country_code_alpha_2 = c.alpha2_country_code
      )
)

select distinct * from validated
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 772 | 717 | 0 | 0 | 91 | 40 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"state_code":"ak","alpha2_country_code":"us"}</code> |
| K2 | <code>{"state_code":"al","alpha2_country_code":"us"}</code> |
| K3 | <code>{"state_code":"ar","alpha2_country_code":"us"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| state_territory | 0 | 55 | 0 | VARCHAR | VARCHAR |
| state_code | 0 | 55 | 0 | VARCHAR | VARCHAR |
| alpha2_country_code | 0 | 55 | 0 | VARCHAR | VARCHAR |

state_territory 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Alaska","rows":2}]</code> | <code>[{"value":"Alaska","rows":1}]</code> |
| K2 | <code>[{"value":"Alabama","rows":2}]</code> | <code>[{"value":"Alabama","rows":1}]</code> |
| K3 | <code>[{"value":"Arkansas","rows":2}]</code> | <code>[{"value":"Arkansas","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

state_code 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"AK","rows":2}]</code> | <code>[{"value":"AK","rows":1}]</code> |
| K2 | <code>[{"value":"AL","rows":2}]</code> | <code>[{"value":"AL","rows":1}]</code> |
| K3 | <code>[{"value":"AR","rows":2}]</code> | <code>[{"value":"AR","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

alpha2_country_code 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"US","rows":2}]</code> | <code>[{"value":"US","rows":1}]</code> |
| K2 | <code>[{"value":"US","rows":2}]</code> | <code>[{"value":"US","rows":1}]</code> |
| K3 | <code>[{"value":"US","rows":2}]</code> | <code>[{"value":"US","rows":1}]</code> |
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
| B7_read_not_specified | <code>["staging.stg_customer360__country_codes"]</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；task_instruction_not_agent_report         description: Resolved state/territory name from stg_customer360__state_territory_codes via (state_code,country_code) match; null if no match</code> |

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
put('staging','stg_customer360__state_territory_codes', '''
```
event 23 / message

```text
 from addresses a left join staging.stg_customer360__state_territory_codes st on a.state_code=st.state_code and a.country_code=st.alpha2_country_code
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-003.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/staging/stg_customer360__state_territory_codes.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/staging/stg_customer360__state_territory_codes.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `data/019_packages_work/019_impl-003_stg_customer360__state_territory_codes/019_impl-003_stg_customer360__state_territory_codes.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/customer360.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
