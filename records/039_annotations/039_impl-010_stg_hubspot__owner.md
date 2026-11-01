# impl-010_stg_hubspot__owner（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`O`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 200, "cell_scale": 400}, "L1": {"row_scale": 200, "cell_scale": 400}, "L2": {"row_scale": 200, "cell_scale": 400}, "L3": {"row_scale": 200, "cell_scale": 400}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| created_timestamp | 其他 | 并列 | 0 | 200 | 2 |
| updated_timestamp | 其他 | 并列 | 0 | 200 | 2 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: stg_hubspot__owner
      description: "Cleaned sales representative and owner records with validated contact information"
      source_table: raw.owner_data
      columns:
        - name: owner_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: portal_id
          data_type: BIGINT
          constraints: [not_null]
        - name: active_user_id
          data_type: VARCHAR
        - name: email_address
          data_type: VARCHAR
        - name: first_name
          data_type: VARCHAR
        - name: last_name
          data_type: VARCHAR
        - name: full_name
          data_type: VARCHAR
        - name: owner_type
          data_type: VARCHAR
          constraints: [not_null]
        - name: created_timestamp
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: updated_timestamp
          data_type: TIMESTAMP
        - name: _fivetran_synced
          data_type: TIMESTAMP WITH TIME ZONE

```

### 逐点结论

#### created_timestamp

并列；**其他**；把握高。

agent按契约输出TIMESTAMP，前19位能解析有效时间；gold的整串格式限制将这200个值置NULL。不是agent大面积解析失败，契约未要求拒绝带后缀的有效输入。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 200 | 200 | 400 | 200 |
| L1 | 200 | 200 | 400 | 200 |
| L2 | 200 | 200 | 400 | 200 |
| L3 | 200 | 200 | 400 | 200 |

重跑：`records/021_reruns_impl-010_stg_hubspot__owner.json` / `created_timestamp`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json` / `73.args.final_thought`（delivery）：

```text
原始 HubSpot 时间字符串按日期时间前 19 位解析，以支持时区偏移和小数秒，同时输出合同指定的无时区 `TIMESTAMP`。空值或无法解析的时间转换为 NULL；必需创建日期无效的行按合同要求排除。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__owner.sql` / `SQL.text`（sql）：

```text
try_strptime(substr(created_at, 1, 19), '%Y-%m-%d %H:%M:%S')
```

#### updated_timestamp

并列；**其他**；把握高。

agent按契约输出TIMESTAMP，前19位能解析有效时间；gold的整串格式限制将这200个值置NULL。不是agent大面积解析失败，契约未要求拒绝带后缀的有效输入。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 200 | 200 | 400 | 200 |
| L1 | 200 | 200 | 400 | 200 |
| L2 | 200 | 200 | 400 | 200 |
| L3 | 200 | 200 | 400 | 200 |

重跑：`records/021_reruns_impl-010_stg_hubspot__owner.json` / `updated_timestamp`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json` / `73.args.final_thought`（delivery）：

```text
原始 HubSpot 时间字符串按日期时间前 19 位解析，以支持时区偏移和小数秒，同时输出合同指定的无时区 `TIMESTAMP`。空值或无法解析的时间转换为 NULL；必需创建日期无效的行按合同要求排除。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__owner.sql` / `SQL.text`（sql）：

```text
try_strptime(substr(updated_at, 1, 19), '%Y-%m-%d %H:%M:%S')
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`，行[193, 223]；材料包 `records/021_packages/021_impl-010_stg_hubspot__owner.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__owner.sql`；SHA-256 `39af2a049c430bec09a60fc7032c24c4610309b3f303bef308d656c8595d2ded`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json` / event 73。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 19，失败=False。
  - `records/021_supplement_queries.json` / index 4，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
