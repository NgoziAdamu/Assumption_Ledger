# impl-003 / customer360__address

## 1. 错在哪里

地址内容一致，差异仅为契约明确允许任意排列的同priority地址rank。

已核实：CS上游用gold，双方38482行；留存差异的rank列最少不一致对数3192。两边都用 row_number() over(partition by customer360_id order by priority)，契约明确同priority排序不确定。去掉rank比较时原留存输出的其余列完全相同（见relaxed诊断）。新执行即使执行gold SQL本身，也不能保证复现留存rank；新基线数值和留存不同，是并列顺序的实际表现。归因判断：O，不把不同rank推成遗漏业务排序。

## 2. 依据

- 起点：[013精简包](../013_packages/013_impl-003_marts_customer360__address.md)。原013状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`，第1204–1256行。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__address.sql`；gold SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__address.sql`。精简包完整收录；下列补丁逐字给出定位原文。
- [完整事件记录](../014_trace_impl-003.json)；事件文件在该JSON的path中，可回查traces/dacomp_deimpl_prev.tar.gz。
- [查询原文与结果](../014_queries_impl-003.json)、[全部重跑记录](../014_reruns_impl-003.json)。

### SQL行号定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__address.sql`
```text
2:  select m.customer360_id,'marketo' as source_system,'primary' as address_type,s.address_line_1,s.address_line_2,s.city,s.state_code,s.country_code,s.postal_code,1 as priority
15: select customer360_id,source_system,address_type,address_line_1,address_line_2,city,state_code,state,country_code,country,country_alt_name,postal_code,priority,
16:  row_number() over(partition by customer360_id order by priority) as rank from enriched
```

gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__address.sql`
```text
25:         1 as priority,
44:         2 as priority,
63:         1 as priority,
82:         2 as priority,
111:         all_addresses.priority,
112:         row_number() over (partition by all_addresses.customer360_id order by all_addresses.priority) as rank
```

## 3. agent看过什么

event 1提供“within the same priority, order is unspecified and non-deterministic”；event 23直接写入该窗口表达式；event 45检查其他模型约束，没有证据表明本表要求更细排序。

已逐题核对event 1 message，包含本表契约完整原文；这不是把磁盘上存在的文档等同于agent已经阅读。schema输出、源数据值、运行日志分别处理。轨迹全量转录未删去截断标记；被截断的未显示部分不作为看到的证据。

## 4. 查询与重跑

核实查询实际执行 **0条**；核实代价：**需要查业务说明**。诊断查询不计入5条限制。重复执行的查询仍计数。

### 比较口径

原件均READ_ONLY；只把本节点引用表复制到data/014_work私有DuckDB后执行。staging输入来自agent留存库raw；003/008上游直接复制gold，实现CS。固定原评分的comparison_columns与key_columns；L0为lower/trim/NULL规范化，L1数字及布尔归一，L2数值两位小数，L3再放宽日期时间到日期。键始终固定L0，不在宽松档位重新归一。

无共同键时逐列0表示无可比较行，不表示一致。重复键按值/行多重集合抵消，报告最少不一致对数；同时公开额外行次数。为避免键被漏出整表判断，含键整表匹配用于本次U4；旧007式仅值列整表匹配并列展示。这里没有重定义原官方对错或修改旧状态。

比较列：`['address_line_1', 'address_line_2', 'address_type', 'city', 'country', 'country_alt_name', 'country_code', 'customer360_id', 'postal_code', 'priority', 'rank', 'source_system', 'state', 'state_code']`；键：`['customer360_id', 'state_code', 'state', 'country_code', 'country', 'postal_code']`。

### 留存基线（013材料来源）

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|38482|38482|0|0|6663|0/0|6663/6663|False|False|
|L1|38482|38482|0|0|6663|0/0|6663/6663|False|False|
|L2|38482|38482|0|0|6663|0/0|6663/6663|False|False|
|L3|38482|38482|0|0|6663|0/0|6663/6663|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|address_line_1|0|0|0|0|
|address_line_2|0|0|0|0|
|address_type|0|0|0|0|
|city|0|0|0|0|
|country|0|0|0|0|
|country_alt_name|0|0|0|0|
|country_code|0|0|0|0|
|customer360_id|0|0|0|0|
|postal_code|0|0|0|0|
|priority|0|0|0|0|
|rank|3192|3192|3192|3192|
|source_system|0|0|0|0|
|state|0|0|0|0|
|state_code|0|0|0|0|

### 重跑：baseline

不改SQL；建立本轮相同引擎、相同输入的比较基线。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|38482|38482|0|0|6664|0/0|6664/6664|False|False|
|L1|38482|38482|0|0|6664|0/0|6664/6664|False|False|
|L2|38482|38482|0|0|6664|0/0|6664/6664|False|False|
|L3|38482|38482|0|0|6664|0/0|6664/6664|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|address_line_1|0|0|0|0|
|address_line_2|0|0|0|0|
|address_type|0|0|0|0|
|city|0|0|0|0|
|country|0|0|0|0|
|country_alt_name|0|0|0|0|
|country_code|0|0|0|0|
|customer360_id|0|0|0|0|
|postal_code|0|0|0|0|
|priority|0|0|0|0|
|rank|2837|2837|2837|2837|
|source_system|0|0|0|0|
|state|0|0|0|0|
|state_code|0|0|0|0|

### 重跑：rank_neutral

只替换以下原文（其余字节经验证不变）：
```sql
row_number() over(partition by customer360_id order by priority) as rank
```
替换为：
```sql
NULL::BIGINT as rank
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|38482|38482|0|0|38482|0/0|38482/38482|False|False|
|L1|38482|38482|0|0|38482|0/0|38482/38482|False|False|
|L2|38482|38482|0|0|38482|0/0|38482/38482|False|False|
|L3|38482|38482|0|0|38482|0/0|38482/38482|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|address_line_1|0|0|0|0|
|address_line_2|0|0|0|0|
|address_type|0|0|0|0|
|city|0|0|0|0|
|country|0|0|0|0|
|country_alt_name|0|0|0|0|
|country_code|0|0|0|0|
|customer360_id|0|0|0|0|
|postal_code|0|0|0|0|
|priority|0|0|0|0|
|rank|38482|38482|38482|38482|
|source_system|0|0|0|0|
|state|0|0|0|0|
|state_code|0|0|0|0|

### gold SQL在同一私有输入上的诊断

这是诊断，不是局部修复，也不用于证明U4。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|38482|38482|0|0|6664|0/0|6664/6664|False|False|
|L1|38482|38482|0|0|6664|0/0|6664/6664|False|False|
|L2|38482|38482|0|0|6664|0/0|6664/6664|False|False|
|L3|38482|38482|0|0|6664|0/0|6664/6664|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|address_line_1|0|0|0|0|
|address_line_2|0|0|0|0|
|address_type|0|0|0|0|
|city|0|0|0|0|
|country|0|0|0|0|
|country_alt_name|0|0|0|0|
|country_code|0|0|0|0|
|customer360_id|0|0|0|0|
|postal_code|0|0|0|0|
|priority|0|0|0|0|
|rank|2837|2837|2837|2837|
|source_system|0|0|0|0|
|state|0|0|0|0|
|state_code|0|0|0|0|

## 5. 类别和把握

- 主要原因：**O**（归因判断）。
- 参与因素：无。
- 标记：无。
- 把握：**高**。
- 重跑是否满足U第4条件：否（没有合格的局部U修复）。

不存在必须满足的“priority唯一”假设：契约明确允许并列，代码也能合法处理并列。

## 规则问题

重跑中rank_neutral把agent rank改为空仅用于展示单侧改值并非修复，不能用作U证据。放宽评测的对照是双侧忽略rank，仅用于确认O；不改变原官方判错状态。重复键下的整行最少不一致对数与逐列最少对数不能相加或互换。

共同问题：手册第1节“不预设类别分布”与末句“希望未核实假设多”存在张力；本次以逐条证据条件为准，不按期望调整分布。U3“没看过任何足以判断P的东西”与“证据曾出现但被忽略仍归U”按后者作为例外解释。
