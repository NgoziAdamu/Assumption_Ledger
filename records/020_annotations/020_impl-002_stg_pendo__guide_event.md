> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-002 / stg_pendo__guide_event（校准）

## 结论

主要原因：**多因并列（C、A）**；把握：高。url 未执行契约 ~ '^https?://' 的整串匹配效果，C；surrogate key 契约未指定拼接字段/顺序/分隔符，A。二者单修均不减少行数、各减少15000格，并列。latitude 依赖值都在[-90,90]的未核实假设，查询证伪13655行，单修减少13655格，为U参与因素。

参与因素：U：latitude（单修减少13655格，行数不变）。标记：无。

## 差异与归因依据

url 未执行契约 ~ '^https?://' 的整串匹配效果，C；surrogate key 契约未指定拼接字段/顺序/分隔符，A。二者单修均不减少行数、各减少15000格，并列。latitude 依赖值都在[-90,90]的未核实假设，查询证伪13655行，单修减少13655格，为U参与因素。

层：staging；比较库schema：staging；评测键：account_id, app_id, guide_id, visitor_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml:268–321`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql:1–18`；SHA-256 `8388508da34d60acc3a1ee931015fa1be0dbc093a5c8c16de6061c092f8268b4`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql:1–83`；SHA-256 `71676c28db577a69d0a194a59199053efdc0318a6e5b415e7c971f7e6b0c2f58`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- latitude：
```sql
TRY_CAST(latitude AS DOUBLE) AS latitude
```
→
```sql
CASE WHEN TRY_CAST(latitude AS DOUBLE) BETWEEN -90 AND 90 THEN TRY_CAST(latitude AS DOUBLE) ELSE NULL END AS latitude
```

- url：
```sql
CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END AS url
```
→
```sql
CASE WHEN url ~ '^https?://' THEN NULLIF(TRIM(CAST(url AS VARCHAR)), '') ELSE NULL END AS url
```

- key：
```sql
md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), '')))
```
→
```sql
CASE
        WHEN account_id IS NOT NULL AND guide_id IS NOT NULL AND timestamp IS NOT NULL AND visitor_id IS NOT NULL
        THEN MD5(CONCAT(
            COALESCE(CAST(visitor_id AS VARCHAR), ''),
            COALESCE(CAST(timestamp AS VARCHAR), ''),
            COALESCE(CAST(account_id AS VARCHAR), ''),
            COALESCE(server_name, ''),
            COALESCE(CAST(guide_id AS VARCHAR), ''),
            COALESCE(user_agent, ''),
            COALESCE(remote_ip, '')
        ))
        ELSE NULL
    END
```

## agent可见证据与不确定性

不确定性四档：**C：只有通用策略说明；A：只有通用策略说明**。

020_reruns_impl-002_stg_pendo__guide_event.json；020_calibration_queries.json；event13/14仅看schema；event19生成代码；event59泛称event-key generation、filtering and nullification，无本表选择理由。

完整事件扫描数：61；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 10 | 9 | stg_pendo__guide_event | False |
| 14 | 13 | guide_event | False |
| 18 | 17 | guide_event | False |
| 26 | 25 | guide_event | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：1；核实代价档：一条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb`

```sql
SELECT count(*) n, count(*) FILTER (WHERE latitude NOT BETWEEN -90 AND 90) invalid_latitude FROM raw.guide_event
```

结果：`[[15000, 13655]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=43 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-002_stg_pendo__guide_event/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[]`。

留存结果同口径规模：15000行 / 43655格；重跑基线：15000行 / 43655格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:15000行/43655格 / L1:15000行/43655格 / L2:15000行/43655格 / L3:15000行/43655格 | 均未整表匹配 |
| latitude | L0:15000行/30000格 / L1:15000行/30000格 / L2:15000行/30000格 / L3:15000行/30000格 | 均未整表匹配 |
| url | L0:15000行/28655格 / L1:15000行/28655格 / L2:15000行/28655格 / L3:15000行/28655格 | 均未整表匹配 |
| key | L0:15000行/28655格 / L1:15000行/28655格 / L2:15000行/28655格 / L3:15000行/28655格 | 均未整表匹配 |

latitude不满足独立主因的一半门槛，但满足U前三项和参与因素减少格子数要求。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"guide_event_key": 15000, "latitude": 13655, "url": 15000} |
| latitude | {"guide_event_key": 15000, "url": 15000} |
| url | {"guide_event_key": 15000, "latitude": 13655} |
| key | {"latitude": 13655, "url": 15000} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。代理键改为gold表达式仅用于衡量未规定选择的影响，不把gold当作契约。 不确定性盲标把event59的event-key generation泛述计为通用策略；018只对URL采用通用策略、对key计“看到了但没提”。保留盲标，不在对照后改写；此处通用“工作内容”是否足以算“策略说明”存在边界，018的更窄读法亦有依据。

## 证据路径

- 精简材料包：`records/013_packages/013_impl-002_staging_stg_pendo__guide_event.md`。
- 重跑：`records/020_reruns_impl-002_stg_pendo__guide_event.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
