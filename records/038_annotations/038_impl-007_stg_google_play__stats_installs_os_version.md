# impl-007_stg_google_play__stats_installs_os_version（038 正式表）

主要原因：**Unstated Choice**；把握：高。020定稿旧主要原因：`A`，仅原样保留。

## 范围与材料

- 层：staging。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`，[240, 270]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_installs_os_version.sql`。

- 对比执行输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### active_devices_last_30_days

- 类别：Unstated Choice；角色：主要；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

raw有active_device_installs/current_device_installs，契约没有明确active_devices_last_30_days对应哪列或时间窗算法；agent选active、gold选current。未发现任何候选对比或疑问意识，代码选择本身不算第3档。

判定顺序：第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: active_devices_last_30_days
>           data_type: BIGINT

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_installs_os_version.sql`，`delivered SQL`：

> TRY_CAST(active_device_installs AS BIGINT) AS active_devices_last_30_days

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: active_devices_last_30_days
>           data_type: BIGINT

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-007_stg_google_play__stats_installs_os_version.json#active_devices_last_30_days`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 5999/11998 | 5945/5945 | 54/6053 |
| L1 | 5999/11998 | 5945/5945 | 54/6053 |
| L2 | 5999/11998 | 5945/5945 | 54/6053 |
| L3 | 5999/11998 | 5945/5945 | 54/6053 |

### user_uninstalls

- 类别：其他；角色：参与；把握：高。

- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约BIGINT计数；agent保留daily_user_uninstalls次数，gold把非零压为1。依契约读取，保留计数可成立，不能把gold布尔化作为agent应遵循算法。

判定顺序：第3节第1步及第6节；以契约/呈现条件定位差异。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: user_uninstalls
>           data_type: BIGINT

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_installs_os_version.sql`，`delivered SQL`：

> TRY_CAST(daily_user_uninstalls AS BIGINT) AS user_uninstalls

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/1.json`，`1.args.content`：

> - name: user_uninstalls
>           data_type: BIGINT

完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。

重跑/诊断：`records/020_reruns_impl-007_stg_google_play__stats_installs_os_version.json#user_uninstalls`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 5999/11998 | 5993/6053 | 6/5945 |
| L1 | 5999/11998 | 5993/6053 | 6/5945 |
| L2 | 5999/11998 | 5993/6053 | 6/5945 |
| L3 | 5999/11998 | 5993/6053 | 6/5945 |

## 规模、覆盖和不确定

按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[62]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='stats_installs_os_version') ORDER BY table_schema,table_name,ordinal_position`。

- `records/020_queries.json[63]`：`SELECT count(*) n, count(*) FILTER(WHERE active_device_installs<>current_device_installs) unequal, min(active_device_installs) min_active, min(current_device_installs) min_current, max(active_device_installs) max_active, max(current_device_installs) max_current FROM raw.stats_installs_os_version`。
