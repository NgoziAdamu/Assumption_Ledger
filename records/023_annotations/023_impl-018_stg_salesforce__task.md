# impl-018 · stg_salesforce__task

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：status_filter。

agent 执行契约显式删除规则，gold 保留违反规则的记录。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-018_stg_salesforce__task.md](../023_packages/023_impl-018_stg_salesforce__task.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
契约行 595–646：

```
595:     - name: stg_salesforce__task
596:       description: "Cleaned task records with validated activity information and completion status"
597:       source_table: raw.task
598:       columns:
599:         - name: task_id
600:           data_type: VARCHAR
601:           constraints: [not_null, unique]
602:         - name: activity_date
603:           data_type: DATE
604:         - name: call_disposition
605:           data_type: VARCHAR
606:         - name: call_duration_in_seconds
607:           data_type: INTEGER
608:         - name: call_object
609:           data_type: VARCHAR
610:         - name: call_type
611:           data_type: VARCHAR
612:         - name: created_date
613:           data_type: TIMESTAMP
614:         - name: task_description
615:           data_type: VARCHAR
616:         - name: is_closed
617:           data_type: BOOLEAN
618:           constraints: [not_null]
619:         - name: is_deleted
620:           data_type: BOOLEAN
621:         - name: is_high_priority
622:           data_type: BOOLEAN
623:         - name: owner_id
624:           data_type: VARCHAR
625:           constraints: [not_null]
626:         - name: priority
627:           data_type: VARCHAR
628:         - name: status
629:           data_type: VARCHAR
630:           constraints: [not_null]
631:           validation_rules:
632:             - rule: "status IS NOT NULL"
633:               on_failure: delete_row
634:             - rule: "status IN ('Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred')"
635:               on_failure: delete_row
636:             - rule: "status = TRIM(status)"
637:               on_failure: correct
638:         - name: subject
639:           data_type: VARCHAR
640:         - name: type
641:           data_type: VARCHAR
642:         - name: what_id
643:           data_type: VARCHAR
644:         - name: who_id
645:           data_type: VARCHAR
646:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__task.sql`，SHA-256 `c8b08eb610b74932ac7ef89b47969b0690b0730f0b75de7d17c30233e3144d5c`，行 1–25。

```
1: select
2:       id as task_id,
3:       try_cast(activity_date as DATE) as activity_date,
4:       call_disposition as call_disposition,
5:       try_cast(call_duration_in_seconds as INTEGER) as call_duration_in_seconds,
6:       call_object as call_object,
7:       call_type as call_type,
8:       try_cast(created_date as TIMESTAMP) as created_date,
9:       description as task_description,
10:       is_closed as is_closed,
11:       is_deleted as is_deleted,
12:       is_high_priority as is_high_priority,
13:       owner_id as owner_id,
14:       priority as priority,
15:       trim(status) as status,
16:       subject as subject,
17:       "type" as type,
18:       what_id as what_id,
19:       who_id as who_id
20: from raw.task
21: where id is not null
22:   and is_closed is not null
23:   and owner_id is not null
24:   and trim(status) in ('Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred')
25: qualify row_number() over (partition by id order by id) = 1
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__task.sql`，SHA-256 `5990d0403823a370c7dd56f2d5076bb3eeb702dd9e3cab13ef5a328a5d73b2fd`，行 1–31。

```
1: with fields as (
2:     select *
3:     from raw.task
4: ), 
5: 
6: final as (
7:     select
8:         cast(id as varchar) as task_id,
9:         cast(activity_date as date) as activity_date,
10:         cast(call_disposition as varchar) as call_disposition,
11:         cast(call_duration_in_seconds as integer) as call_duration_in_seconds,
12:         cast(call_object as varchar) as call_object,
13:         cast(call_type as varchar) as call_type,
14:         cast(created_date as timestamp) as created_date,
15:         cast(description as varchar) as task_description,
16:         cast(coalesce(is_closed, false) as boolean) as is_closed,
17:         cast(coalesce(is_deleted, false) as boolean) as is_deleted,
18:         cast(coalesce(is_high_priority, false) as boolean) as is_high_priority,
19:         cast(owner_id as varchar) as owner_id,
20:         cast(priority as varchar) as priority,
21:         cast(status as varchar) as status,
22:         cast(subject as varchar) as subject,
23:         cast(type as varchar) as type,
24:         cast(what_id as varchar) as what_id,
25:         cast(who_id as varchar) as who_id
26:     from fields
27: )
28: 
29: select *
30: from final
31: where not coalesce(is_deleted, false)
```

## 轨迹可见性与不确定性

**四档：只有通用策略说明**。

event 1 提供校验表达式；event 17/18 查看raw；event 99：「严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空」。这是实际条件处理策略，不取实施清单。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json`。
- event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/17.json`。
- event 18：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/18.json`。
- event 99：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json`。

event 99 最终报告原文（用于检查说明是否超出工作清单）：

```
【回复用户】

已依据 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Salesforce SQL pipeline，文件写入 `sql/staging/`、`sql/intermediate/` 和 `sql/marts/`，命名与配置模型一致。

### 实施内容
- 实现全部 14 个 staging 表：按字段配置选择来源、重命名与类型转换，并落实适用的数据质量处理，例如删除无效/软删除记录、修正名称或状态空格、规范邮件、将无效可选字段置空及去除重复主键。
- 实现全部 7 个 intermediate 模型：覆盖账户增强、机会管道、活动摘要、线索转化、日期维度、用户绩效和 owner 级机会汇总。
- 实现全部 16 个 marts 模型：涵盖机会/线索事实表、账户 engagement、用户维度、owner/manager/team 绩效、日常活动、snapshot、history 及增强模型。
- SQL 使用 DuckDB 语法和显式 `schema.table` 引用；无 dbt `ref()`，SQL 文件末尾均无分号。

### 验证结果
- `python run.py` 成功完成：staging 14/14、intermediate 7/7、marts 16/16，无失败模型。
- 校验了模型输出字段与契约字段集合一致，以及指定业务键的非空/唯一性；核心账户、联系人、机会、用户、线索和活动表的键检查通过。数据质量过滤后示例行数：账户 2,999、用户 993、线索 2,996、任务 2,998。
- 所有 37 个 SQL 文件均已检查无结尾分号。

### 数据质量处理及边界说明
- 严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空；规范化处理保留可用记录。
- History 源数据没有契约所需的 `history_unique_key` 原始列，因此以实体记录 ID 与 Fivetran 起止时间生成确定性 MD5 键，用于稳定标识历史版本。精确重复输入仍会被视作同一历史键；源记录缺乏更细粒度的版本标识时，此类重复的区分能力有限。
- 原始 contact 缺少 `created_date`，opportunity history 缺少 `last_modified_date`；对应 staging 字段按目标类型输出 NULL，没有从不等价字段推断值。
- 日期依赖 `current_date` / `current_timestamp`，因此时间衍生值会随执行日期变化；活动摘要中的固定占位指标按契约保留。

### 排错记录
首次执行遇到的 SQL binder 错误由同一 SELECT 中引用尚未生成的计算字段所致，已改为直接由原始字段计算；后续因上游模型未创建而产生的依赖错误随之消除。最终全链路重跑成功，无未解决的 SQL 错误。
```

## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：status 删除条件

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

```sql
SELECT count(*) FILTER(WHERE status IS NULL OR trim(status) NOT IN ('Not Started','In Progress','Completed','Waiting on someone else','Deferred')) invalid_status FROM raw.task
```


```json
{"columns":["invalid_status"],"rows":[[2]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-018_stg_salesforce__task.json](../023_reruns_impl-018_stg_salesforce__task.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2998|3000|2|32|否|
|L1|2998|3000|2|32|否|
|L2|2998|3000|2|32|否|
|L3|2998|3000|2|32|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"task_id":2,"activity_date":2,"call_disposition":2,"call_duration_in_seconds":2,"call_object":2,"call_type":2,"is_closed":2,"is_deleted":2,"is_high_priority":2,"owner_id":2,"priority":2,"status":2,"subject":2,"type":2,"what_id":2,"who_id":2}`
- L1：`{"task_id":2,"activity_date":2,"call_disposition":2,"call_duration_in_seconds":2,"call_object":2,"call_type":2,"is_closed":2,"is_deleted":2,"is_high_priority":2,"owner_id":2,"priority":2,"status":2,"subject":2,"type":2,"what_id":2,"who_id":2}`
- L2：`{"task_id":2,"activity_date":2,"call_disposition":2,"call_duration_in_seconds":2,"call_object":2,"call_type":2,"is_closed":2,"is_deleted":2,"is_high_priority":2,"owner_id":2,"priority":2,"status":2,"subject":2,"type":2,"what_id":2,"who_id":2}`
- L3：`{"task_id":2,"activity_date":2,"call_disposition":2,"call_duration_in_seconds":2,"call_object":2,"call_type":2,"is_closed":2,"is_deleted":2,"is_high_priority":2,"owner_id":2,"priority":2,"status":2,"subject":2,"type":2,"what_id":2,"who_id":2}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-018_stg_salesforce__task/baseline.sql`；SHA-256 `c8b08eb610b74932ac7ef89b47969b0690b0730f0b75de7d17c30233e3144d5c`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2998|3000|2|32|否|
|L1|2998|3000|2|32|否|
|L2|2998|3000|2|32|否|
|L3|2998|3000|2|32|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"task_id":2,"activity_date":2,"call_disposition":2,"call_duration_in_seconds":2,"call_object":2,"call_type":2,"is_closed":2,"is_deleted":2,"is_high_priority":2,"owner_id":2,"priority":2,"status":2,"subject":2,"type":2,"what_id":2,"who_id":2}`
- L1：`{"task_id":2,"activity_date":2,"call_disposition":2,"call_duration_in_seconds":2,"call_object":2,"call_type":2,"is_closed":2,"is_deleted":2,"is_high_priority":2,"owner_id":2,"priority":2,"status":2,"subject":2,"type":2,"what_id":2,"who_id":2}`
- L2：`{"task_id":2,"activity_date":2,"call_disposition":2,"call_duration_in_seconds":2,"call_object":2,"call_type":2,"is_closed":2,"is_deleted":2,"is_high_priority":2,"owner_id":2,"priority":2,"status":2,"subject":2,"type":2,"what_id":2,"who_id":2}`
- L3：`{"task_id":2,"activity_date":2,"call_disposition":2,"call_duration_in_seconds":2,"call_object":2,"call_type":2,"is_closed":2,"is_deleted":2,"is_high_priority":2,"owner_id":2,"priority":2,"status":2,"subject":2,"type":2,"what_id":2,"who_id":2}`

#### status_filter

判定：主因；类别候选 O。agent 按契约删除无效状态，gold 留存。

相对本轮基线减少行 2、格 32；按行优先、格次之排序。
共同控制后 SQL 第 24 行起、字符 offset 752 的唯一连续替换；其余字节不动。
替换前：
```sql
and trim(status) in ('Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred')
```

替换后：
```sql
and TRUE
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__task/status_filter.sql`；SHA-256 `69c6470983c2b3b1db2116b1593005304628513d8cdb0565b2b9d6d4387d652b`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|0|0|是|
|L1|3000|3000|0|0|是|
|L2|3000|3000|0|0|是|
|L3|3000|3000|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 规则问题

无
