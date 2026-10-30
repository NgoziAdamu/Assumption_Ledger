# impl-016 · stg_workday__position

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**C**；把握：高；主要错误点：validation_order。

先 trim 再按枚举校验，使两条原始值不合法的 employee_type 被保留。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-016_stg_workday__position.md](../023_packages/023_impl-016_stg_workday__position.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`；SHA-256 `8f0707fc595c6f2f1e46a1983436959278e10315cb723e975c2811858d737c91`。
契约行 126–150：

```
126:     - name: stg_workday__position
127:       description: "Cleaned position data including job titles, work schedules, and position lifecycle information"
128:       source_table: "raw.position"
129:       columns:
130:         - name: position_id
131:           data_type: VARCHAR
132:           constraints: [not_null, unique]
133:         - name: source_relation
134:           data_type: VARCHAR
135:           constraints: [not_null]
136:         - name: business_title
137:           data_type: VARCHAR
138:         - name: employee_type
139:           data_type: VARCHAR
140:           validation_rules:
141:             - rule: "employee_type IS NULL OR employee_type IN ('Regular', 'Contingent', 'Intern', 'Contractor')"
142:               on_failure: nullify_field
143:             - rule: "employee_type = TRIM(employee_type)"
144:               on_failure: correct
145:         - name: default_weekly_hours
146:           data_type: BIGINT
147:         - name: effective_start
148:           data_type: DATE
149:           constraints: [not_null]
150:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/staging/stg_workday__position.sql`，SHA-256 `e6a9659207c103c785eed0696c8411ef9d89d23dbaec4fa621ac372889c11528`，行 1–10。

```
1: SELECT
2:     CAST(r."position_id" AS VARCHAR) AS position_id,
3:     CAST('workday'::VARCHAR AS VARCHAR) AS source_relation,
4:     CAST(r."business_title" AS VARCHAR) AS business_title,
5:     CASE WHEN r.employee_type IS NOT NULL AND TRIM(r.employee_type) NOT IN ('Regular','Contingent','Intern','Contractor') THEN NULL ELSE TRIM(r.employee_type) END AS employee_type,
6:      try_cast(r."default_weekly_hours" AS BIGINT) AS default_weekly_hours,
7:      try_cast(r."effective_start" AS DATE) AS effective_start
8: FROM raw.position AS r
9: WHERE (r."position_id" IS NOT NULL)
10:   AND (r."effective_start" IS NOT NULL)
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/staging/stg_workday__position.sql`，SHA-256 `4570ef969f52a742773b099e020dc95a6941e2e9c0c8ee03630b43cd805b8ac2`，行 1–39。

```
1: with source_data as (
2:     select
3:         position_id,
4:         'workday' as source_relation,
5:         business_title,
6:         default_weekly_hours,
7:         employee_type,
8:         effective_start
9:     from raw.position
10: ),
11: 
12: validated_data as (
13:     select
14:         position_id,
15:         source_relation,
16:         business_title,
17:         cast(default_weekly_hours as bigint) as default_weekly_hours,
18:         case
19:             when employee_type is not null and employee_type not in ('Regular', 'Contingent', 'Intern', 'Contractor') then null
20:             when employee_type != trim(employee_type) then trim(employee_type)
21:             else employee_type
22:         end as employee_type,
23:         effective_start,
24:         -- Track validation for potential removal of invalid data
25:         case
26:             when employee_type is not null and employee_type not in ('Regular', 'Contingent', 'Intern', 'Contractor') then 'corrected'
27:             else 'pass'
28:         end as validation_status
29:     from source_data
30: )
31: 
32: select
33:     position_id,
34:     source_relation,
35:     business_title,
36:     default_weekly_hours,
37:     employee_type,
38:     effective_start
39: from validated_data
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 1 提供枚举原式与 trim 规则；event 19/20 读取 position 样例；event 21 生成 SQL。event 83 的 applied cleaning 工作清单不计通用策略。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json`。
- event 19：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/19.json`。
- event 20：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/20.json`。
- event 21：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/21.json`。
- event 83：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/83.json`。
## 查询

核实查询 **3** 条；核实代价档：**多条查询**。诊断查询不计入 5 条上限。

计数保守包含最初额外 2 条结构/少量样例查看。该探索未保留完整返回，不作为分类证据；下列聚合查询独立给出判断所需证据。

### 核实：校验次序

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/workday.duckdb`。

```sql
SELECT count(*) FILTER(WHERE employee_type NOT IN ('Regular','Contingent','Intern','Contractor') AND trim(employee_type) IN ('Regular','Contingent','Intern','Contractor')) trim_rescues FROM raw.position
```


```json
{"columns":["trim_rescues"],"rows":[[2]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-016_stg_workday__position.json](../023_reruns_impl-016_stg_workday__position.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/workday.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4000|4000|2|2|否|
|L1|4000|4000|2|2|否|
|L2|4000|4000|2|2|否|
|L3|4000|4000|2|2|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"employee_type":2}`
- L1：`{"employee_type":2}`
- L2：`{"employee_type":2}`
- L3：`{"employee_type":2}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-016_stg_workday__position/baseline.sql`；SHA-256 `e6a9659207c103c785eed0696c8411ef9d89d23dbaec4fa621ac372889c11528`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4000|4000|2|2|否|
|L1|4000|4000|2|2|否|
|L2|4000|4000|2|2|否|
|L3|4000|4000|2|2|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"employee_type":2}`
- L1：`{"employee_type":2}`
- L2：`{"employee_type":2}`
- L3：`{"employee_type":2}`

#### validation_order

判定：主因；类别候选 C。契约先对原始值执行枚举检查、再 trim；agent 用 trim 后值校验。

相对本轮基线减少行 2、格 2；按行优先、格次之排序。
共同控制后 SQL 第 5 行起、字符 offset 225 的唯一连续替换；其余字节不动。
替换前：
```sql
TRIM(r.employee_type) NOT IN
```

替换后：
```sql
r.employee_type NOT IN
```

私有 SQL：`data/023_work/impl-016_stg_workday__position/validation_order.sql`；SHA-256 `3b2745564b461a6c891df5976797ab7e9f80b7f38f1c3b27b53fbd8da7b87481`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4000|4000|0|0|是|
|L1|4000|4000|0|0|是|
|L2|4000|4000|0|0|是|
|L3|4000|4000|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 原始表改动核对

raw.person_contact_email_address initial/gold 7284、agent 2448。查完原始事件0–84、run.py 导入源码及013写操作清单，只有event39/40、53/54、65/66导入事件，输出均为7284；未找到削减到2448的命令或原因。不能把导入日志当作削减证据。

初始/gold 一致而 agent 有变化，依第 3 节照常标注，不标不可评估。完整表清单见 [023_raw_trace_review.json](../023_raw_trace_review.json)；输入不变性另由前后指纹验证。

## 规则问题

先 trim 再校验也可视为规则次序歧义；本次按第3节可执行原式的字面值校验，归 C，未改手册。
