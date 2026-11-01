# 040 正式标注：impl-013_stg_netsuite2__entities

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。022旧主要原因仅原样存档为 `I`，不作为新类别依据。

## 结论

主要原因：**代码写错**；把握中；共10个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### restore_entity_id

主要；**代码写错**；把握中。

event15已明确写出该列源映射和转换意图；因旧源表名schema lookup失败生成NULL，event25只改FROM没有重生成投影。按代码自身意图证据归代码写错，逐列恢复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 700 | 700 | 4900 | 4200 |
| L1 | 700 | 700 | 4900 | 4200 |
| L2 | 700 | 700 | 4900 | 4200 |
| L3 | 700 | 700 | 4900 | 4200 |



来源：`records/040_checks/supplement_impl-013_stg_netsuite2__entities.json` / `restore_entity_id`。L0减少0行、700格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: entity_id
          data_type: VARCHAR
          constraints: [not_null, unique]

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: entity_id
          data_type: VARCHAR
          constraints: [not_null, unique]

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(NULL AS VARCHAR) AS entity_id

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（intent；普通SQL表达式不是披露）

```text

'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json` / `args.command` / event 25（process；普通SQL表达式不是披露）

```text

p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)

```

### restore_parent_id

非原因；**Quiet Downgrade**；把握中。

原始entities列清单有parent，生成器没有parent_id→parent映射，最终整列NULL；没有正确映射意图证据，不随其他列一律判代码写错，按有候选列但未判断的降级。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 700 | 700 | 4900 | 4900 |
| L1 | 700 | 700 | 4900 | 4900 |
| L2 | 700 | 700 | 4900 | 4900 |
| L3 | 700 | 700 | 4900 | 4900 |



来源：`records/040_checks/supplement_impl-013_stg_netsuite2__entities.json` / `restore_parent_id`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: parent_id
          data_type: VARCHAR

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: parent_id
          data_type: VARCHAR

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(NULL AS VARCHAR) AS parent_id

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（intent；普通SQL表达式不是披露）

```text

'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json` / `args.command` / event 25（process；普通SQL表达式不是披露）

```text

p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/12.json` / `content` / event 12（related；普通SQL表达式不是披露）

```text

 netsuite2_entities_data : id, altemail, altname, altphone, comments, contact, customer, date_deleted, datecreated, email, employee, entityid, entitynumber, entitytitle, externalid, fax, firstname, genericresource, homephone, isinactive, isperson, laborcost, lastmodifieddate, lastname, middlename, mobilephone, othername, parent, partner, phone, project, projecttemplate, salutation, title, toplevelparent, type, vendor

```

### restore_entity_name

非原因；**代码写错**；把握中。

event15已明确写出该列源映射和转换意图；因旧源表名schema lookup失败生成NULL，event25只改FROM没有重生成投影。按代码自身意图证据归代码写错，逐列恢复。 此处恢复agent原定entityid，不使用gold的entitytitle冒充agent意图；当前空主键过滤使该列单改没有贡献。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 700 | 700 | 4900 | 4900 |
| L1 | 700 | 700 | 4900 | 4900 |
| L2 | 700 | 700 | 4900 | 4900 |
| L3 | 700 | 700 | 4900 | 4900 |



来源：`records/040_checks/supplement_impl-013_stg_netsuite2__entities.json` / `restore_entity_name`。L0减少0行、0格。

非原因说明：此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: entity_name
          data_type: VARCHAR

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: entity_name
          data_type: VARCHAR

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(NULL AS VARCHAR) AS entity_name

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（intent；普通SQL表达式不是披露）

```text

'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json` / `args.command` / event 25（process；普通SQL表达式不是披露）

```text

p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)

```

### restore_entity_type

非原因；**代码写错**；把握中。

event15已明确写出该列源映射和转换意图；因旧源表名schema lookup失败生成NULL，event25只改FROM没有重生成投影。按代码自身意图证据归代码写错，逐列恢复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 700 | 700 | 4900 | 4900 |
| L1 | 700 | 700 | 4900 | 4900 |
| L2 | 700 | 700 | 4900 | 4900 |
| L3 | 700 | 700 | 4900 | 4900 |



来源：`records/040_checks/supplement_impl-013_stg_netsuite2__entities.json` / `restore_entity_type`。L0减少0行、0格。

非原因说明：此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: entity_type
          data_type: VARCHAR

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: entity_type
          data_type: VARCHAR

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(NULL AS VARCHAR) AS entity_type

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（intent；普通SQL表达式不是披露）

```text

'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json` / `args.command` / event 25（process；普通SQL表达式不是披露）

```text

p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)

```

### restore_is_person

非原因；**代码写错**；把握中。

event15已明确写出该列源映射和转换意图；因旧源表名schema lookup失败生成NULL，event25只改FROM没有重生成投影。按代码自身意图证据归代码写错，逐列恢复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 700 | 700 | 4900 | 4900 |
| L1 | 700 | 700 | 4900 | 4900 |
| L2 | 700 | 700 | 4900 | 4900 |
| L3 | 700 | 700 | 4900 | 4900 |



来源：`records/040_checks/supplement_impl-013_stg_netsuite2__entities.json` / `restore_is_person`。L0减少0行、0格。

非原因说明：此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: is_person
          data_type: BOOLEAN

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: is_person
          data_type: BOOLEAN

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(NULL AS BOOLEAN) AS is_person

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（intent；普通SQL表达式不是披露）

```text

'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json` / `args.command` / event 25（process；普通SQL表达式不是披露）

```text

p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)

```

### restore_contact_id

非原因；**代码写错**；把握中。

event15已明确写出该列源映射和转换意图；因旧源表名schema lookup失败生成NULL，event25只改FROM没有重生成投影。按代码自身意图证据归代码写错，逐列恢复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 700 | 700 | 4900 | 4900 |
| L1 | 700 | 700 | 4900 | 4900 |
| L2 | 700 | 700 | 4900 | 4900 |
| L3 | 700 | 700 | 4900 | 4900 |



来源：`records/040_checks/supplement_impl-013_stg_netsuite2__entities.json` / `restore_contact_id`。L0减少0行、0格。

非原因说明：此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: contact_id
          data_type: DOUBLE

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: contact_id
          data_type: DOUBLE

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(NULL AS DOUBLE) AS contact_id

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（intent；普通SQL表达式不是披露）

```text

'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json` / `args.command` / event 25（process；普通SQL表达式不是披露）

```text

p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)

```

### restore_customer_id

非原因；**代码写错**；把握中。

event15已明确写出该列源映射和转换意图；因旧源表名schema lookup失败生成NULL，event25只改FROM没有重生成投影。按代码自身意图证据归代码写错，逐列恢复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 700 | 700 | 4900 | 4900 |
| L1 | 700 | 700 | 4900 | 4900 |
| L2 | 700 | 700 | 4900 | 4900 |
| L3 | 700 | 700 | 4900 | 4900 |



来源：`records/040_checks/supplement_impl-013_stg_netsuite2__entities.json` / `restore_customer_id`。L0减少0行、0格。

非原因说明：此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: customer_id
          data_type: VARCHAR

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: customer_id
          data_type: VARCHAR

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(NULL AS VARCHAR) AS customer_id

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（intent；普通SQL表达式不是披露）

```text

'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json` / `args.command` / event 25（process；普通SQL表达式不是披露）

```text

p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)

```

### restore_employee_id

非原因；**代码写错**；把握中。

event15已明确写出该列源映射和转换意图；因旧源表名schema lookup失败生成NULL，event25只改FROM没有重生成投影。按代码自身意图证据归代码写错，逐列恢复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 700 | 700 | 4900 | 4900 |
| L1 | 700 | 700 | 4900 | 4900 |
| L2 | 700 | 700 | 4900 | 4900 |
| L3 | 700 | 700 | 4900 | 4900 |



来源：`records/040_checks/supplement_impl-013_stg_netsuite2__entities.json` / `restore_employee_id`。L0减少0行、0格。

非原因说明：此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: employee_id
          data_type: DOUBLE

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: employee_id
          data_type: DOUBLE

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(NULL AS DOUBLE) AS employee_id

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（intent；普通SQL表达式不是披露）

```text

'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json` / `args.command` / event 25（process；普通SQL表达式不是披露）

```text

p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)

```

### restore_job_id

非原因；**代码写错**；把握中。

event15已明确写出该列源映射和转换意图；因旧源表名schema lookup失败生成NULL，event25只改FROM没有重生成投影。按代码自身意图证据归代码写错，逐列恢复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 700 | 700 | 4900 | 4900 |
| L1 | 700 | 700 | 4900 | 4900 |
| L2 | 700 | 700 | 4900 | 4900 |
| L3 | 700 | 700 | 4900 | 4900 |



来源：`records/040_checks/supplement_impl-013_stg_netsuite2__entities.json` / `restore_job_id`。L0减少0行、0格。

非原因说明：此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: job_id
          data_type: DOUBLE

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: job_id
          data_type: DOUBLE

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(NULL AS DOUBLE) AS job_id

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（intent；普通SQL表达式不是披露）

```text

'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json` / `args.command` / event 25（process；普通SQL表达式不是披露）

```text

p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)

```

### restore_vendor_id

非原因；**代码写错**；把握中。

event15已明确写出该列源映射和转换意图；因旧源表名schema lookup失败生成NULL，event25只改FROM没有重生成投影。按代码自身意图证据归代码写错，逐列恢复。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 700 | 700 | 4900 | 4900 |
| L1 | 700 | 700 | 4900 | 4900 |
| L2 | 700 | 700 | 4900 | 4900 |
| L3 | 700 | 700 | 4900 | 4900 |



来源：`records/040_checks/supplement_impl-013_stg_netsuite2__entities.json` / `restore_vendor_id`。L0减少0行、0格。

非原因说明：此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: vendor_id
          data_type: DOUBLE



```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: vendor_id
          data_type: DOUBLE



```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CAST(NULL AS DOUBLE) AS vendor_id

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（intent；普通SQL表达式不是披露）

```text

'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/25.json` / `args.command` / event 25（process；普通SQL表达式不是披露）

```text

p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)

```

### 排除的旧候选/无差异诊断

- `placeholder_mapping`：022整组恢复只作组级差异定位；主因排序改用040各列单改。

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`；行段[[145, 170]]；SHA-256 `c152a30bcad4df785d3f0ea461101eb8a4b36e4fa06059739a80e04998c4150f`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql`；SHA-256 `1e8241e8a238acb2aea104580dc60b307bb4dee018eb0d77a79cacbb7e45e1a7`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`；材料包：`records/022_packages/022_impl-013_stg_netsuite2__entities.md`。

- 基线源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共3条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 35；上游可见行数；失败=True。

  - `records/022_queries.json` / index 36；候选ID列；失败=False。

  - `records/022_queries_retry.json` / index 24；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

多个NULL投影共享生成器源名问题，但按列给单改。主键单改只减格也足以定主因；其余列被空主键过滤遮住。022整组恢复保留作定位，不替代独立点收益。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
