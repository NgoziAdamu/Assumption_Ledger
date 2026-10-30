# impl-020 | staging | stg_intercom__conversation_contact_history | 差异：S1；日期 原记录

## 契约完整原文

S3:155–166

```yaml
    - name: stg_intercom__conversation_contact_history
      description: "Mapping of conversations to contacts with activity filtering."
      source_table: raw.conversation_contact_history_data
      columns:
        - name: contact_id
          data_type: VARCHAR
        - name: conversation_id
          data_type: BIGINT
      row_filters:
        - rule: "coalesce(try_cast(_fivetran_active as BOOLEAN), true)"
          on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
select
    try_cast(conversation_id as varchar) as contact_id,
    try_cast(contact_id as bigint) as conversation_id
from raw.conversation_contact_history_data
where coalesce(try_cast(_fivetran_active as boolean), true)
```

## gold SQL（仅供定位差异）

S5

```sql
select
  contact_id,
  conversation_id
from raw.conversation_contact_history_data
where coalesce(try_cast(_fivetran_active as BOOLEAN), true)
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 4033 | 4033 | 4033 | 4033 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| conversation_id | 0 | 0 | 0 | BIGINT | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"contact_id":"000bc16cc04f472c8dcd20d6","conversation_id":"156643300002498"},{"contact_id":"000bc16cc04f472c8dcd20d6","conversation_id":"156643300003093"},{"contact_id":"0093697dc2f94d13ab4e609c","conversation_id":"156643300002091"},{"contact_id":"00a6cdc106c54b4aa043d402","conversation_id":"156643300002788"},{"contact_id":"00be0b3eceb8438793277c76","conversation_id":"156643300001723"}]</code> | <code>[{"contact_id":"156643300000029","conversation_id":"5eec5ff27c241f259ae27d75"},{"contact_id":"156643300000044","conversation_id":"5eed27c83784ef90f95c5082"},{"contact_id":"156643300000200","conversation_id":"5f0604960382a50f226b2496"},{"contact_id":"156643300000242","conversation_id":"5ed9ff581dff5e56251a4ac6"},{"contact_id":"156643300000684","conversation_id":"5ed93beb39021efc4ccd4ea5"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

没有 True 痕迹。

## 轨迹索引（不放输出原文）

本题事件总数：63；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 7463 | true | false |
| 11 | run | <code>cat intercom_start.yaml &amp;&amp; sed -n '1,240p' test_single_sql.py</code> | 8424 | false | false |
| 13 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,260p' docs/data_contract.yaml</code> | 9929 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('intercom_start.duckdb',read_only=True)<br>for t in c.execute('show tables').fetchall():<br> n=t[0]<br> print('\n',n,c.execute(f'select count(*) from "{n}"').fetc</code> | 14942 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/build.py &lt;&lt;'PY'<br># Marts<br>put(M/'intercom__company_enhanced.sql', '''select h.company_id, h.company_name, h.website, h.website_domain, h.industry, h.created_at, h.updated_at,<br>       h.user_c</code> | 1467 | true | false |
| 29 | run | python run.py | 4056 | true | false |
| 35 | run | <code>cat &gt; sql/staging/stg_intercom__conversation_part_history.sql &lt;&lt;'SQL'<br>with source_rows as (<br>    select<br>        try_cast(id as varchar) as conversation_part_id,<br>        coalesce(try_cast(part_type as v</code> | 0 | false | false |
| 37 | run | <code>cat &gt; sql/staging/stg_intercom__conversation_part_history.sql &lt;&lt;'SQL'<br>with source_rows as (<br>    select<br>        try_cast(id as varchar) as conversation_part_id,<br>        coalesce(try_cast(part_type as v</code> | 1094 | true | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>p='sql/marts/intercom__company_metrics.sql'<br>s=open(p).read()<br>s=s.replace("""convo_time_metrics as (<br>    select cc.company_id,<br>           median(cm.time_to_first_response_minutes)::doub</code> | 4130 | true | false |

### agent action 的 thought/message 命中原句

event 35 / message

```text
cat > sql/staging/stg_intercom__conversation_contact_history.sql <<'SQL'
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-020.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/staging/stg_intercom__conversation_contact_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/sql/staging/stg_intercom__conversation_contact_history.sql`
- S6: `records/006_contract_impl-020.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/result.md`
- S10: `data/023_packages_work/023_impl-020_stg_intercom__conversation_contact_history/023_impl-020_stg_intercom__conversation_contact_history.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions`
