# impl-021 · stg_klaviyo__metric

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：null_id_filter。

agent按契约ID not_null过滤，gold保留NULL ID；仅放开该过滤后L0全匹配。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-021_stg_klaviyo__metric.md](../023_packages/023_impl-021_stg_klaviyo__metric.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml`；SHA-256 `db04fb84955b6385dd63b72bdf7aae27ac9f612a685f938eabf7051f12cd675f`。
契约行 141–163：

```
141:     - name: stg_klaviyo__metric
142:       description: "Cleaned metric dimension with integration attributes."
143:       source_table: raw.metric
144:       columns:
145:         - name: created_at
146:           data_type: TIMESTAMP
147:         - name: metric_id
148:           data_type: VARCHAR
149:           constraints: [not_null]
150:         - name: integration_id
151:           data_type: VARCHAR
152:         - name: integration_name
153:           data_type: VARCHAR
154:         - name: integration_category
155:           data_type: VARCHAR
156:         - name: metric_name
157:           data_type: VARCHAR
158:         - name: updated_at
159:           data_type: TIMESTAMP
160:         - name: source_relation
161:           data_type: VARCHAR
162:           constraints: [not_null]
163:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/staging/stg_klaviyo__metric.sql`，SHA-256 `9b08f4223583fc13348616dbbc9a25eefecb6dc8813eb5dbad22aeefd874e6e1`，行 1–4。

```
1: select try_cast(created as timestamp) created_at, cast(id as varchar) metric_id, cast(integration_id as varchar) integration_id,
2:  cast(integration_name as varchar) integration_name, cast(integration_category as varchar) integration_category,
3:  cast(name as varchar) metric_name, try_cast(updated as timestamp) updated_at, 'klaviyo'::varchar source_relation
4: from raw.metric where nullif(trim(cast(id as varchar)), '') is not null
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/sql/staging/stg_klaviyo__metric.sql`，SHA-256 `5442ef40eb163b6da9395c9290ac06a6a798ad9b5fbe75cf5d14b78e65bb00ca`，行 1–16。

```
1: with base as (
2:     select * from raw.metric
3: ),
4: final as (
5:     select
6:         created as created_at,
7:         cast(id as varchar) as metric_id,
8:         cast(integration_id as varchar) as integration_id,
9:         integration_name,
10:         integration_category,
11:         name as metric_name,
12:         updated as updated_at,
13:         'klaviyo' as source_relation
14:     from base
15: )
16: select * from final
```

## 轨迹可见性与不确定性

**四档：只有通用策略说明**。

event 19/20、23/24 显式查看raw ID非空计数；event 41：「无效关键 ID 和非法邮件记录被排除」。这是跨表条件处理策略，非工作清单。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 19：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/19.json`。
- event 20：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/20.json`。
- event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/23.json`。
- event 24：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/24.json`。
- event 41：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/41.json`。

event 41 最终报告原文（用于检查说明是否超出工作清单）：

```
【回复用户】

已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 Klaviyo SQL 数据管道，SQL 文件均放置在 `sql/staging/`、`sql/intermediate/`、`sql/marts/`，共 18 个模型文件。SQL 使用 DuckDB 语法、直接以 `schema.table` 引用上游、不含 dbt `ref()`，且文件末尾无分号。

**执行验证**
- `python run.py` 成功完成 staging → intermediate → marts 全部层级转换。
- 构建行数：staging campaign 2、event 2,500、flow 1、metric 1、person 2；intermediate event_attribution 2,500、events 2,500、person_campaign_flow 9、campaign_flow_metrics 7、person_metrics 3、campaigns_enriched 2、flows_enriched 1、persons_enriched 2；marts events 2,500、campaigns 2、flows 1、persons 2、person_campaign_flow 9。
- 检查 campaign/person/event/flow/metric staging 主键字段无空值及重复；event 的 `(source_relation, event_id)` 在 staging、intermediate 与 marts 均无空值及重复。

**数据质量处理与边界说明**
- staging 清洗邮件和 timezone 大小写、空白，标准化电话，安全转换时间/数值；无效关键 ID 和非法邮件记录被排除，超长 person email 置空，负的 price/compare-at-price 置空。
- 事件 attribution 解析按契约优先级提取 JSON 子事件 ID，查找限定同一 `source_relation`；事件重复保留且照常计数。
- 契约未指定 `source_relation` 的字面值，本实现使用固定来源键 `'klaviyo'`。电话号码按 E.164-like 格式加前缀 `+`，未推断国家码。
- 所有 SQL 文件遵循 DuckDB/直接 schema-table 引用规范。`python run.py` 成功，无失败 SQL 语句；目标数据库为 `klaviyo.duckdb`。
```

## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：ID 空值

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE id IS NULL) null_id,count(*) FILTER(WHERE trim(id)='') blank_id FROM raw.metric
```


```json
{"columns":["n","null_id","blank_id"],"rows":[[29,28,0]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-021_stg_klaviyo__metric.json](../023_reruns_impl-021_stg_klaviyo__metric.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|29|28|168|否|
|L1|1|29|28|168|否|
|L2|1|29|28|168|否|
|L3|1|29|28|168|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"metric_id":28,"integration_id":28,"integration_category":28,"integration_name":28,"metric_name":28,"source_relation":28}`
- L1：`{"metric_id":28,"integration_id":28,"integration_category":28,"integration_name":28,"metric_name":28,"source_relation":28}`
- L2：`{"metric_id":28,"integration_id":28,"integration_category":28,"integration_name":28,"metric_name":28,"source_relation":28}`
- L3：`{"metric_id":28,"integration_id":28,"integration_category":28,"integration_name":28,"metric_name":28,"source_relation":28}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-021_stg_klaviyo__metric/baseline.sql`；SHA-256 `9b08f4223583fc13348616dbbc9a25eefecb6dc8813eb5dbad22aeefd874e6e1`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1|29|28|168|否|
|L1|1|29|28|168|否|
|L2|1|29|28|168|否|
|L3|1|29|28|168|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"metric_id":28,"integration_id":28,"integration_category":28,"integration_name":28,"metric_name":28,"source_relation":28}`
- L1：`{"metric_id":28,"integration_id":28,"integration_category":28,"integration_name":28,"metric_name":28,"source_relation":28}`
- L2：`{"metric_id":28,"integration_id":28,"integration_category":28,"integration_name":28,"metric_name":28,"source_relation":28}`
- L3：`{"metric_id":28,"integration_id":28,"integration_category":28,"integration_name":28,"metric_name":28,"source_relation":28}`

#### null_id_filter

判定：主因；类别候选 O。前三表契约明确 ID not_null，gold 保留 NULL；person 没有非空要求，额外删除为未规定取舍。

相对本轮基线减少行 28、格 168；按行优先、格次之排序。
共同控制后 SQL 第 4 行起、字符 offset 378 的唯一连续替换；其余字节不动。
替换前：
```sql
nullif(trim(cast(id as varchar)), '') is not null
```

替换后：
```sql
TRUE
```

私有 SQL：`data/023_work/impl-021_stg_klaviyo__metric/null_id_filter.sql`；SHA-256 `dae27dddcd1cf2ac4255818e8a24177ad1dbad4c8262994fa465cc59c9ae74a3`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|29|29|0|0|是|
|L1|29|29|0|0|是|
|L2|29|29|0|0|是|
|L3|29|29|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 规则问题

无
