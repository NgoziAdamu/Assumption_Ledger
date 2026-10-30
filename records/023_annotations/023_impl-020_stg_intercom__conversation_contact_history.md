# impl-020 · stg_intercom__conversation_contact_history

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：直接诊断（无正改善的单点排序）。

raw两列值域错位；agent按数据关系映射并输出BIGINT conversation_id，gold同名透传为VARCHAR，与契约类型不符。

参与因素：无。

标记：无。

核实：raw.contact_id全部4033可转BIGINT，raw.conversation_id全部不可转；后者与contact主表4024匹配，同名contact_id为0匹配。gold列类型诊断见023_diagnostics。

## 材料与比较口径

精简材料包：[023_impl-020_stg_intercom__conversation_contact_history.md](../023_packages/023_impl-020_stg_intercom__conversation_contact_history.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml`；SHA-256 `b19cdce65b55dd44086f5a7ef864055abfe48bd66f5d6f430785084ab3cd5314`。
契约行 155–166：

```
155:     - name: stg_intercom__conversation_contact_history
156:       description: "Mapping of conversations to contacts with activity filtering."
157:       source_table: raw.conversation_contact_history_data
158:       columns:
159:         - name: contact_id
160:           data_type: VARCHAR
161:         - name: conversation_id
162:           data_type: BIGINT
163:       row_filters:
164:         - rule: "coalesce(try_cast(_fivetran_active as BOOLEAN), true)"
165:           on_failure: delete_row
166:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/staging/stg_intercom__conversation_contact_history.sql`，SHA-256 `e92597ffc92f0690c4d37859cf0756bc316e15119344abe5d551f3e84d83a2b5`，行 1–5。

```
1: select
2:     try_cast(conversation_id as varchar) as contact_id,
3:     try_cast(contact_id as bigint) as conversation_id
4: from raw.conversation_contact_history_data
5: where coalesce(try_cast(_fivetran_active as boolean), true)
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/sql/staging/stg_intercom__conversation_contact_history.sql`，SHA-256 `4fe96ea93dc9da5355051187e3963677ad253ffcc49cdafa6fa3d619c28192f8`，行 1–5。

```
1: select
2:   contact_id,
3:   conversation_id
4: from raw.conversation_contact_history_data
5: where coalesce(try_cast(_fivetran_active as BOOLEAN), true)
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 21/22 可见两列与主表值域；event 25 生成交换映射；event 61 只解释conversation part错位，没有说明本映射表选择。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 21：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/21.json`。
- event 22：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/22.json`。
- event 25：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/25.json`。
- event 61：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/61.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：列值域与主表覆盖

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE try_cast(contact_id AS BIGINT) IS NOT NULL) contact_numeric,count(*) FILTER(WHERE try_cast(conversation_id AS BIGINT) IS NOT NULL) conversation_numeric,count(*) FILTER(WHERE conversation_id IN(SELECT id FROM raw.contact_history_data)) swapped_contact_matches,count(*) FILTER(WHERE contact_id IN(SELECT id FROM raw.contact_history_data)) named_contact_matches FROM raw.conversation_contact_history_data
```


```json
{"columns":["n","contact_numeric","conversation_numeric","swapped_contact_matches","named_contact_matches"],"rows":[[4033,4033,0,4024,0]]}
```


### 诊断：gold类型与契约

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`。

```sql
DESCRIBE staging.stg_intercom__conversation_contact_history
```


```json
{"columns":["column_name","column_type","null","key","default","extra"],"rows":[["contact_id","VARCHAR","YES",null,null,null],["conversation_id","VARCHAR","YES",null,null,null]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-020_stg_intercom__conversation_contact_history.json](../023_reruns_impl-020_stg_intercom__conversation_contact_history.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4033|4033|8066|16132|否|
|L1|4033|4033|8066|16132|否|
|L2|4033|4033|8066|16132|否|
|L3|4033|4033|8066|16132|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"contact_id":8066,"conversation_id":8066}`
- L1：`{"contact_id":8066,"conversation_id":8066}`
- L2：`{"contact_id":8066,"conversation_id":8066}`
- L3：`{"contact_id":8066,"conversation_id":8066}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-020_stg_intercom__conversation_contact_history/baseline.sql`；SHA-256 `e92597ffc92f0690c4d37859cf0756bc316e15119344abe5d551f3e84d83a2b5`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4033|4033|8066|16132|否|
|L1|4033|4033|8066|16132|否|
|L2|4033|4033|8066|16132|否|
|L3|4033|4033|8066|16132|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"contact_id":8066,"conversation_id":8066}`
- L1：`{"contact_id":8066,"conversation_id":8066}`
- L2：`{"contact_id":8066,"conversation_id":8066}`
- L3：`{"contact_id":8066,"conversation_id":8066}`
### 补充轮：[023_supplement_reruns_impl-020_stg_intercom__conversation_contact_history.json](../023_supplement_reruns_impl-020_stg_intercom__conversation_contact_history.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`。

共同时间控制：`[]`。

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_supplement_work/impl-020_stg_intercom__conversation_contact_history/baseline.sql`；SHA-256 `e92597ffc92f0690c4d37859cf0756bc316e15119344abe5d551f3e84d83a2b5`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4033|4033|8066|16132|否|
|L1|4033|4033|8066|16132|否|
|L2|4033|4033|8066|16132|否|
|L3|4033|4033|8066|16132|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"contact_id":8066,"conversation_id":8066}`
- L1：`{"contact_id":8066,"conversation_id":8066}`
- L2：`{"contact_id":8066,"conversation_id":8066}`
- L3：`{"contact_id":8066,"conversation_id":8066}`

#### contact_column

判定：不计参与因素；类别候选 O。原始列错位，agent 输出 contact VARCHAR 与数据关系一致；gold 按原名透传。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 2 行起、字符 offset 11 的唯一连续替换；其余字节不动。
替换前：
```sql
try_cast(conversation_id as varchar) as contact_id
```

替换后：
```sql
contact_id as contact_id
```

私有 SQL：`data/023_supplement_work/impl-020_stg_intercom__conversation_contact_history/contact_column.sql`；SHA-256 `e4d10b76789cb17a0607a38042d2ac765d3a8640a237d69da1cf49c72a076d4e`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4033|4033|8066|16132|否|
|L1|4033|4033|8066|16132|否|
|L2|4033|4033|8066|16132|否|
|L3|4033|4033|8066|16132|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"contact_id":8066,"conversation_id":8066}`
- L1：`{"contact_id":8066,"conversation_id":8066}`
- L2：`{"contact_id":8066,"conversation_id":8066}`
- L3：`{"contact_id":8066,"conversation_id":8066}`

#### conversation_column

判定：不计参与因素；类别候选 O。agent 遵守 conversation_id BIGINT；gold 保留无法转成 BIGINT 的原始字符串。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 3 行起、字符 offset 67 的唯一连续替换；其余字节不动。
替换前：
```sql
try_cast(contact_id as bigint) as conversation_id
```

替换后：
```sql
conversation_id as conversation_id
```

私有 SQL：`data/023_supplement_work/impl-020_stg_intercom__conversation_contact_history/conversation_column.sql`；SHA-256 `2a4c1dc38d437ef8b05315b58f12765eb4fe76eabc906aa81ac2b4638f41e9e4`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4033|4033|8066|16132|否|
|L1|4033|4033|8066|16132|否|
|L2|4033|4033|8066|16132|否|
|L3|4033|4033|8066|16132|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"contact_id":8066,"conversation_id":8066}`
- L1：`{"contact_id":8066,"conversation_id":8066}`
- L2：`{"contact_id":8066,"conversation_id":8066}`
- L3：`{"contact_id":8066,"conversation_id":8066}`

## 规则问题

两个评测键均不同，逐处改一列都不减少行/格规模；主因不能按正改善排序，但契约BIGINT与gold VARCHAR矛盾已直接核实，按第3节归O，不因交互改成X，也不打包两处修改。
