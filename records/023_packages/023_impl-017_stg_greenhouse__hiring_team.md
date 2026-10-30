# impl-017 | staging | stg_greenhouse__hiring_team | 差异：S1；日期 原记录

## 契约完整原文

S3:387–400

```yaml
    - name: stg_greenhouse__hiring_team
      description: "Cleaned hiring team assignments"
      source_table: "raw.hiring_team"
      primary_key: ["job_id", "user_id"]
      columns:
        - name: job_id
          data_type: BIGINT
          constraints: [not_null]
        - name: user_id
          data_type: BIGINT
          constraints: [not_null]
        - name: role
          data_type: VARCHAR(100)

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        TRY_CAST(job_id AS BIGINT) AS "job_id",
        TRY_CAST(user_id AS BIGINT) AS "user_id",
        TRY_CAST(role AS VARCHAR(100)) AS "role",
        ROW_NUMBER() OVER (PARTITION BY "job_id", "user_id" ORDER BY "job_id", "user_id") AS _row_num
    FROM raw.hiring_team
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE "job_id" IS NOT NULL AND "user_id" IS NOT NULL AND "job_id" IS NOT NULL AND "user_id" IS NOT NULL
)
SELECT "job_id", "user_id", "role"
FROM validated_rows
WHERE _row_num = 1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Purpose: Standardize hiring_team data with validation
-- Source: raw.hiring_team
-- Target: staging.stg_greenhouse__hiring_team

with source as (
    select * from raw.hiring_team
),

renamed as (
    select
        cast(job_id as bigint) as job_id,
        cast(upper(trim(role)) as varchar) as hiring_team_role,
        cast(user_id as bigint) as user_id
    from source
),

validated as (
    select
        job_id,
        hiring_team_role,
        user_id
    from renamed

    where
        -- Ensure required fields are not null (composite key)
        job_id is not null
        and user_id is not null
)

select * from validated
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1999 | 2000 | 0 | 0 | 0 | 1 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"job_id":"191","user_id":"1415"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| job_id | 0 | 0 | 1 | BIGINT | BIGINT |
| user_id | 0 | 0 | 1 | BIGINT | BIGINT |

job_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"191","rows":1}]</code> | <code>[{"value":"191","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

user_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"1415","rows":1}]</code> | <code>[{"value":"1415","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

没有 True 痕迹。

## 轨迹索引（不放输出原文）

本题事件总数：55；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find . -maxdepth 3 -type f &#124; sort &#124; head -100</code> | 2041 | false | false |
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 12604 | true | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('greenhouse_start.duckdb',read_only=True)<br>for t in c.execute("select table_name from information_schema.tables where table_schema='raw' order by 1").fetc</code> | 3529 | false | false |
| 17 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; python - &lt;&lt;'PY'<br>import yaml, pathlib<br>c=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br># raw source names differ from c</code> | 0 | false | false |
| 19 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>I=Path('sql/intermediate'); M=Path('sql/marts')<br>def w(d,n,s): (d/f'{n}.sql').write_text(s.strip()+"\n")<br>w(I,'int_greenhouse__user_emails', '''WITH ema</code> | 0 | false | false |
| 29 | run | <code>grep -E 'Executing: staging&#124;ERROR - ✗ staging&#124;staging\.' /tmp/run.log &#124; head -90</code> | 7093 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('greenhouse.duckdb',read_only=True)<br>for s in ['staging','intermediate','mart']:<br> print('\n',s)<br> for (t,) in c.execute(f"select table_name from informatio</code> | 1807 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
    FROM staging.stg_greenhouse__hiring_team AS ht
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-017.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/staging/stg_greenhouse__hiring_team.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/sql/staging/stg_greenhouse__hiring_team.sql`
- S6: `records/006_contract_impl-017.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/result.md`
- S10: `data/023_packages_work/023_impl-017_stg_greenhouse__hiring_team/023_impl-017_stg_greenhouse__hiring_team.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/greenhouse.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/greenhouse.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions`
