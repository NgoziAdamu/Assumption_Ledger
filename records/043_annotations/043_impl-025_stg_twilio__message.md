# 043：impl-025_stg_twilio__message

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为10行/2487格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`C`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-025/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/sql/staging/stg_twilio__message.sql`；无SQL注释。材料包：`records/024_packages/024_impl-025_stg_twilio__message.md`。

staging采用agent留存raw；013直接源对照逐项列出。 013的call/message变化在015的gold raw中也有；本表仍照常评估。

已逐张读取 `records/013_raw_impl-025.json`；与gold关系见 `records/015_raw_impl-025.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.message_data`：initial 2500行/18列；agent留存 2500行/18列；013差异=False。

## 同源决定

同源决定：event 17，`/tmp/write_sql.py`：同一sql字典写入两张正式staging；电话标准化式重复使用，friendly_name后续独立调整。 目录编号：`025-write-sql`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 17，把原电话先去非数字字符、补+1，再检验正则；两张表三列共用写法。 本表点：from_normalized, to_normalized；编号 `025-phone-normalize`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共2条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引14（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `两处原始电话格式`：`records/024_queries.json` 数组索引15（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

涉及运行时间的基线与单改沿用同一固定时刻：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 1}]`；完整控制记录见复用重跑JSON。

## 点：from_normalized

类别：**Intent Misreading**；角色：参与；把握：高。

契约规定from正则验证失败置空；预先去标点补+1改变验证对象和失败动作。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-025_stg_twilio__message.json`，条目 `from_normalized`。

基线：L0=2495行/4972格; L1=2495行/4972格; L2=2495行/4972格; L3=2495行/4972格。

单改后：L0=2487行/2487格; L1=2487行/2487格; L2=2487行/2487格; L3=2487行/2487格。L0减量（先行后格）：8行/2485格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "regexp_replace(regexp_replace(\"from\", '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\\1') as from_normalized",
    "new": "\"from\" as from_normalized",
    "offset": 405
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。报告说明验证失败置NULL，没有说明本点先去标点补+1、把本应失败的原值改成有效电话的处理；另一张outgoing_caller_id的点名说明也不推广。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/output.jsonl`：

```text
        - name: error_message
          data_type: VARCHAR
        - name: message_from
          data_type: VARCHAR
          validation_rules:
            - rule: "message_from RLIKE '^\\+1[0-9]{10}$'"
              on_failure: nullify_field
        - name: message_id
          data_type: VARCHAR
        - name: messaging_service_id
          data_type: VARCHAR
        - name: num_media
          data_type: DOUBLE
        - name: num_segments
          data_type: DOUBLE
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `025-write-sql`；根源决定单元 `025-phone-normalize`。

## 点：to_normalized

类别：**Intent Misreading**；角色：主要；把握：高。

契约规定to正则验证失败置空；预先标准化将非法原值变为合法值。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-025_stg_twilio__message.json`，条目 `to_normalized`。

基线：L0=2495行/4972格; L1=2495行/4972格; L2=2495行/4972格; L3=2495行/4972格。

单改后：L0=2485行/2485格; L1=2485行/2485格; L2=2485行/2485格; L3=2485行/2485格。L0减量（先行后格）：10行/2487格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "regexp_replace(regexp_replace(\"to\", '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\\1') as to_normalized",
    "new": "\"to\" as to_normalized",
    "offset": 813
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。报告说明验证失败置NULL，没有说明本点先去标点补+1、把本应失败的原值改成有效电话的处理；另一张outgoing_caller_id的点名说明也不推广。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/output.jsonl`：

```text
            - rule: "status IN ('accepted','queued','sending','sent','failed','delivered','undelivered','receiving','received')"
              on_failure: nullify_field
        - name: message_to
          data_type: VARCHAR
          validation_rules:
            - rule: "message_to RLIKE '^\\+1[0-9]{10}$'"
              on_failure: nullify_field
        - name: updated_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "updated_at IS NULL OR updated_at >= created_at"
              on_failure: delete_row
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `025-write-sql`；根源决定单元 `025-phone-normalize`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
