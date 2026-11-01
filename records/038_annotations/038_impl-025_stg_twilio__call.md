# 038 校准：impl-025_stg_twilio__call

## 结论

主要原因：**Intent Misreading**；并列类别：无；把握：高。这是解盲后的工作结果；盲标原件不变。

两表校准已完成；43张正式表尚未标注。本文件不计入正式批次分布。

## 手册第3～7节判断与规模

先整表行规模；行规模相同不能区分时比较格子规模。L0–L3 同结论。保留所有原始数值，不以旧类别定新类别。

先排除：未发现本表原始数据版本差异导致不可评估的证据；类别不从020旧标签映射。契约明确算法优先Intent，只有输出形式变化才考虑Form，原代码是否显露正确意图须单独核实。

| 实验 | L0 行/格 | L1 行/格 | L2 行/格 | L3 行/格 |
|---|---|---|---|---|
| baseline | 2492/4965 | 2492/4965 | 2492/4965 | 2492/4965 |
| phone_user | 2483/2483 | 2483/2483 | 2483/2483 | 2483/2483 |
| phone_contact | 2482/2482 | 2482/2482 | 2482/2482 | 2482/2482 |

重跑复用 `records/020_reruns_impl-025_stg_twilio__call.json`，完整SQL替换与逐列L0–L3结果保留于该文件；没有新执行SQL或打开数据库。Twilio重跑基线及单改均固定为2025-10-12，guide_event不依赖运行时钟。

## 逐点标注

### user_phone_number 先修复再校验

- 类别：Intent Misreading；角色：参与；把握：高。
- 判据：契约规定非法电话 nullify_field，未授权先去标点、补 +1 把不合法源值修复为合法。020 核实查询 2500 源行零条 from 符合要求；单改只撤掉该列修复。
- P：不适用（不是Data Misconception）
- 单改减少：9行／2482格。
- 是否说出：第2档，交付物里只有通用说明；盲标第4档。解盲后修订：交付报告中的清理/置空策略虽未点名本字段，但明确涉及本类处理，按036及037第2档口径接受；不是第1档。盲标把这类策略全部视作一般完成声明，判得过窄。
- 证据在场：是。event 1 初始任务完整给出本列正则和 nullify_field。
- 曾经理解对过：否；系统提示是否适用：不适用。
- 最终SQL证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/sql/staging/stg_twilio__call.sql`

```sql
        regexp_replace(regexp_replace(try_cast("from" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as user_phone_number_raw,
```

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/41.json`，event 41.args.final_thought

> 依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。

证据在场原句：event 1.args.content，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/1.json`

> - name: user_phone_number
>           data_type: VARCHAR
>           validation_rules:
>             - rule: "user_phone_number RLIKE '^\\+1[0-9]{10}$'"
>               on_failure: nullify_field

证据：`records/020_reruns_impl-025_stg_twilio__call.json#phone_user`；`records/020_calibration_queries.json`。

### contact_phone_number 先修复再校验

- 类别：Intent Misreading；角色：主要；把握：高。
- 判据：同一契约规则对 contact_phone_number 独立适用；020 核实查询零条 to 符合要求。两列可独立修改，不合成一个点。
- P：不适用（不是Data Misconception）
- 单改减少：10行／2483格。
- 是否说出：第2档，交付物里只有通用说明；盲标第4档。解盲后修订：交付报告中的清理/置空策略虽未点名本字段，但明确涉及本类处理，按036及037第2档口径接受；不是第1档。盲标把这类策略全部视作一般完成声明，判得过窄。
- 证据在场：是。event 1 初始任务完整给出本列正则和 nullify_field。
- 曾经理解对过：否；系统提示是否适用：不适用。
- 最终SQL证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/sql/staging/stg_twilio__call.sql`

```sql
        regexp_replace(regexp_replace(try_cast("to" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as contact_phone_number_raw,
```

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/41.json`，event 41.args.final_thought

> 依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。

证据在场原句：event 1.args.content，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/1.json`

> - name: contact_phone_number
>           data_type: VARCHAR
>           validation_rules:
>             - rule: "contact_phone_number RLIKE '^\\+1[0-9]{10}$'"
>               on_failure: nullify_field

证据：`records/020_reruns_impl-025_stg_twilio__call.json#phone_contact`；`records/020_calibration_queries.json`。

## 交付物核查

finish：event 41，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/41.json` 的 `args.final_thought`。本表最终SQL没有注释。

盲标delivery_review原文保留于封存件。工作行以每点disclosure_reason为准；URL和两项电话改第2档，latitude与key仍第4档。

## 规则问题

两列电话可分别单改，保留两点而不把整组修复冒充单点；contact减10行，user减9行。报告中的通用清理策略属于第2档，不证明已说明预修复选择。

## 证据来源与限制

020定稿旧主要原因原样为 `C`；只作追溯，不作v3.2判类依据。

来源：`records/020_calibration_queries.json`、`records/020_reruns_impl-025_stg_twilio__call.json`、`records/013_packages/013_impl-025_staging_stg_twilio__call.md`；封存及解盲详情见038对应JSON。

已核实来自实际打开的契约/SQL/事件和复用查询记录；没有新查数据库，因此不声称重新验证了整个数据集。
