# impl-020 · int_intercom__conversation_part_aggregates

用途：**全量**；层：`intermediate`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**U**；把握：高；主要错误点：conversation_coverage。

从part聚合驱动并内连接conversation，依赖每个conversation都有part的假设，丢弃无匹配part的对话。

参与因素：无。

标记：证据曾出现但被忽略。

P：每个conversation均有part。核实可见库5726个conversation无part；CS上游0匹配，漏6703。U前三条件满足（已见行数反证却忽略）；单点6703→0，满足第4条件。初轮left_conversation仅保留part方向，非正确coverage修正，排除。

## 材料与比较口径

精简材料包：[023_impl-020_int_intercom__conversation_part_aggregates.md](../023_packages/023_impl-020_int_intercom__conversation_part_aggregates.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml`；SHA-256 `b19cdce65b55dd44086f5a7ef864055abfe48bd66f5d6f430785084ab3cd5314`。
契约行 541–602：

```
541:     - name: int_intercom__conversation_part_aggregates
542:       description: "Per-conversation aggregates and key event timestamps derived from conversation parts."
543:       grain: "One row per conversation_id"
544:       source_models: [staging.stg_intercom__conversation_part_history, staging.stg_intercom__conversation_history]
545:       business_logic: >
546:         For each conversation, compute counts of parts, assignments, and reopen events.
547:         Identify first and last timestamps for assignments, contact replies, admin responses, and reopen events.
548:         The first contact reply considers parts authored by a contact (user or lead) and is used for time-to-close metrics downstream.
549:       columns:
550:         - name: conversation_id
551:           data_type: BIGINT
552:           description: "Conversation identifier."
553:           tests: [not_null]
554:         - name: conversation_created_at
555:           data_type: TIMESTAMP
556:           description: "Creation time of the conversation carried forward for time-based metrics."
557:           tests: [not_null]
558:         - name: count_total_parts
559:           data_type: BIGINT
560:           description: "Total number of parts associated with the conversation."
561:           tests: ["count_total_parts >= 0"]
562:         - name: first_contact_reply_at
563:           data_type: TIMESTAMP
564:           description: "Timestamp of the first reply authored by a contact (user or lead)."
565:           tests: []
566:         - name: first_assignment_at
567:           data_type: TIMESTAMP
568:           description: "Timestamp of the first assignment-related part."
569:           tests: []
570:         - name: first_admin_response_at
571:           data_type: TIMESTAMP
572:           description: "Timestamp of the first admin-authored comment with body content."
573:           tests: []
574:         - name: first_reopen_at
575:           data_type: TIMESTAMP
576:           description: "Timestamp of the first reopen event for the conversation."
577:           tests: []
578:         - name: last_assignment_at
579:           data_type: TIMESTAMP
580:           description: "Timestamp of the last assignment-related part."
581:           tests: []
582:         - name: last_contact_reply_at
583:           data_type: TIMESTAMP
584:           description: "Timestamp of the last contact-authored reply."
585:           tests: []
586:         - name: last_admin_response_at
587:           data_type: TIMESTAMP
588:           description: "Timestamp of the last admin-authored response with body content."
589:           tests: []
590:         - name: last_reopen_at
591:           data_type: TIMESTAMP
592:           description: "Timestamp of the last reopen event for the conversation."
593:           tests: []
594:         - name: count_assignments
595:           data_type: BIGINT
596:           description: "Number of assignment-related parts."
597:           tests: ["count_assignments >= 0"]
598:         - name: count_reopens
599:           data_type: BIGINT
600:           description: "Number of reopen events."
601:           tests: ["count_reopens >= 0"]
602:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/intermediate/int_intercom__conversation_part_aggregates.sql`，SHA-256 `20c9d50c5125f7db529695fb5fba8fb4fde3d634c4f31c70deff77d3c899e0a1`，行 1–24。

```
1: with parts as (
2:     select *, lower(coalesce(part_type, '')) as event_type
3:     from staging.stg_intercom__conversation_part_history
4:     where conversation_id is not null
5: ), rollup as (
6:     select conversation_id, count(*)::bigint as count_total_parts,
7:         min(created_at) filter (where author_type in ('user', 'lead')) as first_contact_reply_at,
8:         min(created_at) filter (where event_type like '%assign%') as first_assignment_at,
9:         min(created_at) filter (where author_type = 'admin' and event_type in ('comment','message','reply') and nullif(trim(body),'') is not null) as first_admin_response_at,
10:         min(created_at) filter (where event_type like '%reopen%') as first_reopen_at,
11:         max(created_at) filter (where event_type like '%assign%') as last_assignment_at,
12:         max(created_at) filter (where author_type in ('user', 'lead')) as last_contact_reply_at,
13:         max(created_at) filter (where author_type = 'admin' and event_type in ('comment','message','reply') and nullif(trim(body),'') is not null) as last_admin_response_at,
14:         max(created_at) filter (where event_type like '%reopen%') as last_reopen_at,
15:         count(*) filter (where event_type like '%assign%')::bigint as count_assignments,
16:         count(*) filter (where event_type like '%reopen%')::bigint as count_reopens
17:     from parts group by conversation_id
18: )
19: select r.conversation_id, c.created_at as conversation_created_at, r.count_total_parts,
20:        r.first_contact_reply_at, r.first_assignment_at, r.first_admin_response_at, r.first_reopen_at,
21:        r.last_assignment_at, r.last_contact_reply_at, r.last_admin_response_at, r.last_reopen_at,
22:        r.count_assignments, r.count_reopens
23: from rollup r join staging.stg_intercom__conversation_history c on r.conversation_id=c.conversation_id
24: qualify row_number() over (partition by r.conversation_id order by coalesce(c.updated_at,c.created_at) desc nulls last)=1
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/sql/intermediate/int_intercom__conversation_part_aggregates.sql`，SHA-256 `afbce90a3b86edd4b2e23a93cdfde3de5294d61227a17fafa44faed3da3e3333`，行 1–30。

```
1: with latest_conversation_part as (
2:   select *
3:   from staging.stg_intercom__conversation_part_history
4: ),
5: latest_conversation as (
6:   select *
7:   from staging.stg_intercom__conversation_history
8: ),
9: final as (
10:   select
11:     latest_conversation.conversation_id,
12:     latest_conversation.created_at as conversation_created_at,
13:     count(latest_conversation_part.conversation_part_id) as count_total_parts,
14:     min(case when latest_conversation_part.part_type = 'comment' and latest_conversation_part.author_type in ('lead','user') then latest_conversation_part.created_at else null end) as first_contact_reply_at,
15:     min(case when latest_conversation_part.part_type like '%assignment%' then latest_conversation_part.created_at else null end) as first_assignment_at,
16:     min(case when latest_conversation_part.part_type in ('comment','assignment') and latest_conversation_part.author_type = 'admin' and latest_conversation_part.body is not null then latest_conversation_part.created_at else null end) as first_admin_response_at,
17:     min(case when latest_conversation_part.part_type = 'open' then latest_conversation_part.created_at else null end) as first_reopen_at,
18:     max(case when latest_conversation_part.part_type like '%assignment%' then latest_conversation_part.created_at else null end) as last_assignment_at,
19:     max(case when latest_conversation_part.part_type = 'comment' and latest_conversation_part.author_type in ('lead','user') then latest_conversation_part.created_at else null end) as last_contact_reply_at,
20:     max(case when latest_conversation_part.part_type in ('comment','assignment') and latest_conversation_part.author_type = 'admin' and latest_conversation_part.body is not null then latest_conversation_part.created_at else null end) as last_admin_response_at,
21:     max(case when latest_conversation_part.part_type = 'open' then latest_conversation_part.created_at else null end) as last_reopen_at,
22:     sum(case when latest_conversation_part.part_type like '%assignment%' then 1 else 0 end) as count_assignments,
23:     sum(case when latest_conversation_part.part_type = 'open' then 1 else 0 end) as count_reopens
24:   from latest_conversation
25:   left join latest_conversation_part
26:     on latest_conversation.conversation_id = latest_conversation_part.conversation_id
27:   group by 1, 2
28: )
29: select *
30: from final
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 39/40 已看到 conversation 6703 与 part aggregates 977；event 61 报告同样给出977而未解释覆盖缺口。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 39：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/39.json`。
- event 40：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/40.json`。
- event 61：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/61.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：agent 可见连接覆盖

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`。

```sql
SELECT (SELECT count(*) FROM staging.stg_intercom__conversation_history) conversations,(SELECT count(*) FROM staging.stg_intercom__conversation_history c WHERE NOT EXISTS(SELECT 1 FROM staging.stg_intercom__conversation_part_history p WHERE p.conversation_id=c.conversation_id)) conversations_without_parts,(SELECT count(*) FROM staging.stg_intercom__conversation_part_history p WHERE NOT EXISTS(SELECT 1 FROM staging.stg_intercom__conversation_history c WHERE p.conversation_id=c.conversation_id)) orphan_parts
```


```json
{"columns":["conversations","conversations_without_parts","orphan_parts"],"rows":[[6703,5726,2607]]}
```


### 诊断：CS 连接覆盖

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`。

```sql
SELECT (SELECT count(*) FROM staging.stg_intercom__conversation_history) conversations,(SELECT count(*) FROM staging.stg_intercom__conversation_part_history p JOIN staging.stg_intercom__conversation_history c USING(conversation_id)) joined_parts
```


```json
{"columns":["conversations","joined_parts"],"rows":[[6703,0]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-020_int_intercom__conversation_part_aggregates.json](../023_reruns_impl-020_int_intercom__conversation_part_aggregates.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|6703|6703|26812|否|
|L1|0|6703|6703|26812|否|
|L2|0|6703|6703|26812|否|
|L3|0|6703|6703|26812|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`
- L1：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`
- L2：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`
- L3：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-020_int_intercom__conversation_part_aggregates/baseline.sql`；SHA-256 `20c9d50c5125f7db529695fb5fba8fb4fde3d634c4f31c70deff77d3c899e0a1`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|6703|6703|26812|否|
|L1|0|6703|6703|26812|否|
|L2|0|6703|6703|26812|否|
|L3|0|6703|6703|26812|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`
- L1：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`
- L2：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`
- L3：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`

#### left_conversation

判定：探索修正方向不成立，排除归因；类别候选 U。假设每个 part conversation 均存在 history 主表；需可见数据核实。

相对本轮基线减少行 -7520、格 -30080；按行优先、格次之排序。
共同控制后 SQL 第 23 行起、字符 offset 1693 的唯一连续替换；其余字节不动。
替换前：
```sql
from rollup r join staging.stg_intercom__conversation_history c
```

替换后：
```sql
from rollup r left join staging.stg_intercom__conversation_history c
```

私有 SQL：`data/023_work/impl-020_int_intercom__conversation_part_aggregates/left_conversation.sql`；SHA-256 `d8c85f99c57ea03648457922845d4c3cd3d11bc0c40d171aa8ed19cfb3f81c04`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|7520|6703|14223|56892|否|
|L1|7520|6703|14223|56892|否|
|L2|7520|6703|14223|56892|否|
|L3|7520|6703|14223|56892|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"conversation_id":14223,"count_assignments":14223,"count_reopens":14223,"count_total_parts":14223}`
- L1：`{"conversation_id":14223,"count_assignments":14223,"count_reopens":14223,"count_total_parts":14223}`
- L2：`{"conversation_id":14223,"count_assignments":14223,"count_reopens":14223,"count_total_parts":14223}`
- L3：`{"conversation_id":14223,"count_assignments":14223,"count_reopens":14223,"count_total_parts":14223}`
### 补充轮：[023_supplement_reruns_impl-020_int_intercom__conversation_part_aggregates.json](../023_supplement_reruns_impl-020_int_intercom__conversation_part_aggregates.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`。

共同时间控制：`[]`。

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_supplement_work/impl-020_int_intercom__conversation_part_aggregates/baseline.sql`；SHA-256 `20c9d50c5125f7db529695fb5fba8fb4fde3d634c4f31c70deff77d3c899e0a1`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|6703|6703|26812|否|
|L1|0|6703|6703|26812|否|
|L2|0|6703|6703|26812|否|
|L3|0|6703|6703|26812|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`
- L1：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`
- L2：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`
- L3：`{"conversation_id":6703,"count_assignments":6703,"count_reopens":6703,"count_total_parts":6703}`

#### conversation_coverage

判定：主因；类别候选 U。P=每个 conversation 都有匹配的 part；由 part 驱动的内连接丢失无 part 对话。可见库5726个对话无 part；CS 全部无匹配。

相对本轮基线减少行 6703、格 26812；按行优先、格次之排序。
共同控制后 SQL 第 23 行起、字符 offset 1693 的唯一连续替换；其余字节不动。
替换前：
```sql
from rollup r join staging.stg_intercom__conversation_history c on r.conversation_id=c.conversation_id
```

替换后：
```sql
from (SELECT c0.conversation_id,coalesce(r0.count_total_parts,0) count_total_parts,r0.first_contact_reply_at,r0.first_assignment_at,r0.first_admin_response_at,r0.first_reopen_at,r0.last_assignment_at,r0.last_contact_reply_at,r0.last_admin_response_at,r0.last_reopen_at,coalesce(r0.count_assignments,0) count_assignments,coalesce(r0.count_reopens,0) count_reopens FROM staging.stg_intercom__conversation_history c0 LEFT JOIN rollup r0 ON c0.conversation_id=r0.conversation_id) r join staging.stg_intercom__conversation_history c on r.conversation_id=c.conversation_id
```

私有 SQL：`data/023_supplement_work/impl-020_int_intercom__conversation_part_aggregates/conversation_coverage.sql`；SHA-256 `5a4e0042728beac5e3ca134d252ee7d19a8fadeab9210aaf1e17843259c2c25b`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6703|6703|0|0|是|
|L1|6703|6703|0|0|是|
|L2|6703|6703|0|0|是|
|L3|6703|6703|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 规则问题

“For each conversation”可理解为明确规定全量驱动（C），也可理解为实体粒度而未指定连接实现（U）。本次选U：关键依赖是每个conversation存在part，agent可见数据明确反证；单改驱动连接后CS L0全匹配。
