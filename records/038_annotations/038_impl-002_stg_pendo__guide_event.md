# 038 校准：impl-002_stg_pendo__guide_event

## 结论

主要原因：**多因并列**；并列类别：Intent Misreading；Unstated Choice；把握：高。这是解盲后的工作结果；盲标原件不变。

两表校准已完成；43张正式表尚未标注。本文件不计入正式批次分布。

## 手册第3～7节判断与规模

先整表行规模；行规模相同不能区分时比较格子规模。L0–L3 同结论。保留所有原始数值，不以旧类别定新类别。

先排除：未发现本表原始数据版本差异导致不可评估的证据；类别不从020旧标签映射。契约明确算法优先Intent，只有输出形式变化才考虑Form，原代码是否显露正确意图须单独核实。

| 实验 | L0 行/格 | L1 行/格 | L2 行/格 | L3 行/格 |
|---|---|---|---|---|
| baseline | 15000/43655 | 15000/43655 | 15000/43655 | 15000/43655 |
| latitude | 15000/30000 | 15000/30000 | 15000/30000 | 15000/30000 |
| url | 15000/28655 | 15000/28655 | 15000/28655 | 15000/28655 |
| key | 15000/28655 | 15000/28655 | 15000/28655 | 15000/28655 |

重跑复用 `records/020_reruns_impl-002_stg_pendo__guide_event.json`，完整SQL替换与逐列L0–L3结果保留于该文件；没有新执行SQL或打开数据库。Twilio重跑基线及单改均固定为2025-10-12，guide_event不依赖运行时钟。

## 逐点标注

### latitude 未处理超出正负90度的值

- 类别：Data Misconception；角色：参与；把握：高。
- 判据：契约没有规定 latitude 过滤算法；地理纬度硬约束可定，020 agent 留存 raw 核实查询 15000 行中 13655 行超界。P 被数据否定，依第5节硬约束归 Data。
- P：raw.guide_event.latitude 可以直接作为合法纬度使用，非空值均在 [-90,90]。
- 单改减少：0行／13655格。
- 是否说出：第4档，看到了相关信息，但没有意识到的迹象；盲标第4档。初始契约/列清单有相关信息，交付物未针对本处说明；代码仅实施所选做法，未发现比较候选、指出冲突或疑问的迹象。一般合规/完成陈述不当作披露。
- 证据在场：否。event 1 仅给 latitude 列名及 DOUBLE 类型；event 14/16 仅 schema，无超界统计/样例，不能单凭它们证明本批 raw 值超界。核实查询是标注者事后复用，非 agent 当时看到的输出。
- 曾经理解对过：否；系统提示是否适用：不适用。
- 最终SQL证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql`

```sql
    TRY_CAST(latitude AS DOUBLE) AS latitude,
```

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`，event 1.args.content

> - name: latitude
>           data_type: DOUBLE

证据：`records/020_reruns_impl-002_stg_pendo__guide_event.json#latitude`；`records/020_calibration_queries.json`。

### url 未执行契约正则置空规则

- 类别：Intent Misreading；角色：并列；把握：高。
- 判据：契约明确给出 url ~ 表达式和 nullify_field；按引擎字面语义执行，agent 只 TRIM/NULLIF，遗漏规定做法。不是依据 gold 发明验证算法，也不是仅呈现差异。
- P：不适用（不是Data Misconception）
- 单改减少：0行／15000格。
- 是否说出：第2档，交付物里只有通用说明；盲标第4档。解盲后修订：交付报告中的清理/置空策略虽未点名本字段，但明确涉及本类处理，按036及037第2档口径接受；不是第1档。盲标把这类策略全部视作一般完成声明，判得过窄。
- 证据在场：是。初始任务 event 1 args.content 完整包含本表的上述规则，未截断。
- 曾经理解对过：否；系统提示是否适用：不适用。
- 最终SQL证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql`

```sql
    CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END AS url,
```

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event 59.args.final_thought

> Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.

证据在场原句：event 1.args.content，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`

> - rule: "url IS NULL OR url ~ '^https?://'"
>               on_failure: nullify_field

证据：`records/020_reruns_impl-002_stg_pendo__guide_event.json#url`；`records/020_calibration_queries.json`。

### guide_event_key 拼接列与分隔符

- 类别：Unstated Choice；角色：并列；把握：高。
- 判据：契约仅写 Generated surrogate key，没定输入列、拼接顺序或分隔符；差异取决于材料没定的选择。键值为计算结果，非 Form Mismatch。
- P：不适用（不是Data Misconception）
- 单改减少：0行／15000格。
- 是否说出：第4档，看到了相关信息，但没有意识到的迹象；盲标第4档。初始契约/列清单有相关信息，交付物未针对本处说明；代码仅实施所选做法，未发现比较候选、指出冲突或疑问的迹象。一般合规/完成陈述不当作披露。
- 证据在场：不适用。不适用
- 曾经理解对过：不适用；系统提示是否适用：不适用。
- 最终SQL证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql`

```sql
    md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''))) AS guide_event_key
```

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`，event 1.args.content

> description: "Generated surrogate key"

证据：`records/020_reruns_impl-002_stg_pendo__guide_event.json#key`；`records/020_calibration_queries.json`。

## 交付物核查

finish：event 59，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json` 的 `args.final_thought`。本表最终SQL没有注释。

盲标delivery_review原文保留于封存件。工作行以每点disclosure_reason为准；URL和两项电话改第2档，latitude与key仍第4档。

## 规则问题

guide_event各单改的整表行数都不下降，采用037的“行规模相同则按格子”读法，URL与key各减15000格并列，latitude减13655格为参与因素。解盲确认036相同；不改手册。

## 证据来源与限制

020定稿旧主要原因原样为 `多因并列（C、A）`；只作追溯，不作v3.2判类依据。

来源：`records/020_calibration_queries.json`、`records/020_reruns_impl-002_stg_pendo__guide_event.json`、`records/013_packages/013_impl-002_staging_stg_pendo__guide_event.md`；封存及解盲详情见038对应JSON。

已核实来自实际打开的契约/SQL/事件和复用查询记录；没有新查数据库，因此不声称重新验证了整个数据集。
