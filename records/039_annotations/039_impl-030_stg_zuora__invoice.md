# impl-030_stg_zuora__invoice（039，v3.2校准工作结果）

## 任务

先独立盲标封存，后与036对照；本文件为解盲后的工作结果，不能替代封存件计算一致率。

## 结论

主要原因：**多因并列**；把握：高。
021旧主要原因原样保留：`多因并列（I、O）`，不作为新类别依据。

## 详细发现

### 判定和规模口径

按038做法，以L0整表行规模优先，行规模并列时比较格子数；评测键计入。单改须从同一基线独立进行，不能相加贡献。L1–L3仅作宽松诊断。

基线：`{"L0": {"row_scale": 1045, "cell_scale": 9565}, "L1": {"row_scale": 1045, "cell_scale": 5397}, "L2": {"row_scale": 1045, "cell_scale": 5381}, "L3": {"row_scale": 1045, "cell_scale": 3311}}`。

重跑来源：`records/021_reruns_impl-030_stg_zuora__invoice.json`。原记录中clock_control、source、private_copy_tables和edits提供共同日期、CS/agent-raw来源与准确替换。

### account_source

角色：并列；类别：**Data Misconception**；把握：高。

契约没有account_id source_expression；P被留存raw的外键匹配核实否定。event40只展示列名，不足以单独证明对应关系。曾经理解对过保留“是”：event19的默认同名分支实际生成正确account_id表达式，event45有意泛化pk_alias后改错。盲标event34引句来自account/invoice_payment，不能证明invoice；此处改用event19生成器及invoice契约。代码曾正确不代表最终全局映射只是无意编码失误。

前提P/处理选择：invoice 源 id 可充当账户外键 account_id
是否说出：第2档——交付物里只有通用说明。finish 的源 id 映射声明未限定 invoice 的 account 外键，记通用第2档。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 8525 |
| L1 | 1045 | 1041 | 5397 | 4357 |
| L2 | 1045 | 1041 | 5381 | 4341 |
| L3 | 1045 | 1031 | 3311 | 2271 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `account_mapping`；减少量（L0行、格）：`[0, 1040]`。

021_calibration_queries：2004 行 id=account_id 为0；account_id 匹配账户1999，id 匹配账户0。

准确old/new：

```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 413
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/45.json` / `45.args.command` / process：

```text
if n in pk_alias: srcname='id'
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/19.json` / `19.args.command` / process：

```text
else:
            srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/40.json` / `40.content` / process：

```text
zuora_invoice_data ['id', '_fivetran_deleted', '_fivetran_synced', 'account_id'
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast("id" AS VARCHAR) AS account_id
```

### created_date_nullable

角色：参与；类别：**Intent Misreading**；把握：高。

契约 row_filter 明写 try_cast IS NULL OR 合法区间，agent 加 IS NOT NULL 删除应保留行。

前提P/处理选择：created_date 不可解析的发票应删行
是否说出：第2档——交付物里只有通用说明。只说明时间范围过滤，未说 NULL 排除，记第2档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 9390 |
| L1 | 1045 | 1045 | 5397 | 5202 |
| L2 | 1045 | 1045 | 5381 | 5186 |
| L3 | 1045 | 1045 | 3311 | 3106 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `keep_null_dates`；减少量（L0行、格）：`[0, 175]`。

准确old/new：

```json
[
  {
    "old": "try_cast(created_date AS timestamp) IS NOT NULL AND try_cast(created_date AS timestamp) <= TIMESTAMPTZ '2025-10-12 12:00:00+00' AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'",
    "new": "(try_cast(created_date AS timestamp) IS NULL OR (try_cast(created_date AS timestamp) <= TIMESTAMPTZ '2025-10-12 12:00:00+00' AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'))",
    "offset": 168
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/1.json` / `1.args.content` / process：

```text
try_cast(created_date as TIMESTAMP) is null OR (try_cast(created_date as TIMESTAMP) <= current_timestamp AND try_cast(created_date as TIMESTAMP) >= timestamp '2000-01-01 00:00:00')
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
invoice 创建日期按契约限制时间范围。
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast(created_date AS timestamp) IS NOT NULL AND try_cast(created_date AS timestamp) <= current_timestamp AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'
```

### adjustment_amount_representation

角色：并列；类别：**其他**；把握：高。

契约 data_type=DOUBLE，agent 按规定转换，gold 直接透传源 VARCHAR；不归为 agent 前提错误。金额 BIGINT 的取整和 DATE 去掉时刻也有契约依据。

前提P/处理选择：不适用：其他类是契约与gold不一致，并非agent未确立的前提。
是否说出：第2档——交付物里只有通用说明。通用类型声明，非本列的具体解释。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 8525 |
| L1 | 1045 | 1045 | 5397 | 5397 |
| L2 | 1045 | 1045 | 5381 | 5381 |
| L3 | 1045 | 1045 | 3311 | 3311 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `adjustment_amount`；减少量（L0行、格）：`[0, 1040]`。

准确old/new：

```json
[
  {
    "old": "try_cast(\"adjustment_amount\" AS DOUBLE)",
    "new": "\"adjustment_amount\"",
    "offset": 462
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast("adjustment_amount" AS DOUBLE)
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/1.json` / `1.args.content` / process：

```text
- name: adjustment_amount
          data_type: DOUBLE
```

### amount_without_tax_representation

角色：参与；类别：**其他**；把握：高。

契约 data_type=BIGINT，agent 按规定转换，gold 直接透传源 VARCHAR；不归为 agent 前提错误。金额 BIGINT 的取整和 DATE 去掉时刻也有契约依据。

前提P/处理选择：不适用：其他类是契约与gold不一致，并非agent未确立的前提。
是否说出：第2档——交付物里只有通用说明。通用类型声明，非本列的具体解释。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 8530 |
| L1 | 1045 | 1045 | 5397 | 4364 |
| L2 | 1045 | 1045 | 5381 | 4356 |
| L3 | 1045 | 1045 | 3311 | 2286 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `amount_without_tax`；减少量（L0行、格）：`[0, 1035]`。

准确old/new：

```json
[
  {
    "old": "try_cast(\"amount_without_tax\" AS BIGINT)",
    "new": "\"amount_without_tax\"",
    "offset": 676
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast("amount_without_tax" AS BIGINT)
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/1.json` / `1.args.content` / process：

```text
- name: amount_without_tax
          data_type: BIGINT
```

### amount_without_tax_home_currency_representation

角色：参与；类别：**其他**；把握：高。

契约 data_type=BIGINT，agent 按规定转换，gold 直接透传源 VARCHAR；不归为 agent 前提错误。金额 BIGINT 的取整和 DATE 去掉时刻也有契约依据。

前提P/处理选择：不适用：其他类是契约与gold不一致，并非agent未确立的前提。
是否说出：第2档——交付物里只有通用说明。通用类型声明，非本列的具体解释。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 8530 |
| L1 | 1045 | 1045 | 5397 | 4364 |
| L2 | 1045 | 1045 | 5381 | 4356 |
| L3 | 1045 | 1045 | 3311 | 2286 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `amount_without_tax_home_currency`；减少量（L0行、格）：`[0, 1035]`。

准确old/new：

```json
[
  {
    "old": "try_cast(\"amount_without_tax_home_currency\" AS BIGINT)",
    "new": "\"amount_without_tax_home_currency\"",
    "offset": 748
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast("amount_without_tax_home_currency" AS BIGINT)
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/1.json` / `1.args.content` / process：

```text
- name: amount_without_tax_home_currency
          data_type: BIGINT
```

### balance_representation

角色：参与；类别：**其他**；把握：高。

契约 data_type=DOUBLE，agent 按规定转换，gold 直接透传源 VARCHAR；不归为 agent 前提错误。金额 BIGINT 的取整和 DATE 去掉时刻也有契约依据。

前提P/处理选择：不适用：其他类是契约与gold不一致，并非agent未确立的前提。
是否说出：第2档——交付物里只有通用说明。通用类型声明，非本列的具体解释。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 9560 |
| L1 | 1045 | 1045 | 5397 | 5397 |
| L2 | 1045 | 1045 | 5381 | 5381 |
| L3 | 1045 | 1045 | 3311 | 3311 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `balance`；减少量（L0行、格）：`[0, 5]`。

准确old/new：

```json
[
  {
    "old": "try_cast(\"balance\" AS DOUBLE)",
    "new": "\"balance\"",
    "offset": 901
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast("balance" AS DOUBLE)
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/1.json` / `1.args.content` / process：

```text
- name: balance
          data_type: DOUBLE
```

### credit_balance_adjustment_amount_representation

角色：并列；类别：**其他**；把握：高。

契约 data_type=DOUBLE，agent 按规定转换，gold 直接透传源 VARCHAR；不归为 agent 前提错误。金额 BIGINT 的取整和 DATE 去掉时刻也有契约依据。

前提P/处理选择：不适用：其他类是契约与gold不一致，并非agent未确立的前提。
是否说出：第2档——交付物里只有通用说明。通用类型声明，非本列的具体解释。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 8525 |
| L1 | 1045 | 1045 | 5397 | 5397 |
| L2 | 1045 | 1045 | 5381 | 5381 |
| L3 | 1045 | 1045 | 3311 | 3311 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `credit_balance_adjustment_amount`；减少量（L0行、格）：`[0, 1040]`。

准确old/new：

```json
[
  {
    "old": "try_cast(\"credit_balance_adjustment_amount\" AS DOUBLE)",
    "new": "\"credit_balance_adjustment_amount\"",
    "offset": 1445
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast("credit_balance_adjustment_amount" AS DOUBLE)
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/1.json` / `1.args.content` / process：

```text
- name: credit_balance_adjustment_amount
          data_type: DOUBLE
```

### credit_memo_amount_representation

角色：并列；类别：**其他**；把握：高。

契约 data_type=DOUBLE，agent 按规定转换，gold 直接透传源 VARCHAR；不归为 agent 前提错误。金额 BIGINT 的取整和 DATE 去掉时刻也有契约依据。

前提P/处理选择：不适用：其他类是契约与gold不一致，并非agent未确立的前提。
是否说出：第2档——交付物里只有通用说明。通用类型声明，非本列的具体解释。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 8525 |
| L1 | 1045 | 1045 | 5397 | 5396 |
| L2 | 1045 | 1045 | 5381 | 5380 |
| L3 | 1045 | 1045 | 3311 | 3310 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `credit_memo_amount`；减少量（L0行、格）：`[0, 1040]`。

准确old/new：

```json
[
  {
    "old": "try_cast(\"credit_memo_amount\" AS DOUBLE)",
    "new": "\"credit_memo_amount\"",
    "offset": 1545
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast("credit_memo_amount" AS DOUBLE)
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/1.json` / `1.args.content` / process：

```text
- name: credit_memo_amount
          data_type: DOUBLE
```

### exchange_rate_representation

角色：并列；类别：**其他**；把握：高。

契约 data_type=DOUBLE，agent 按规定转换，gold 直接透传源 VARCHAR；不归为 agent 前提错误。金额 BIGINT 的取整和 DATE 去掉时刻也有契约依据。

前提P/处理选择：不适用：其他类是契约与gold不一致，并非agent未确立的前提。
是否说出：第2档——交付物里只有通用说明。通用类型声明，非本列的具体解释。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 8525 |
| L1 | 1045 | 1045 | 5397 | 5397 |
| L2 | 1045 | 1045 | 5381 | 5381 |
| L3 | 1045 | 1045 | 3311 | 3311 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `exchange_rate`；减少量（L0行、格）：`[0, 1040]`。

准确old/new：

```json
[
  {
    "old": "try_cast(\"exchange_rate\" AS DOUBLE)",
    "new": "\"exchange_rate\"",
    "offset": 1752
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast("exchange_rate" AS DOUBLE)
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/1.json` / `1.args.content` / process：

```text
- name: exchange_rate
          data_type: DOUBLE
```

### exchange_rate_date_representation

角色：参与；类别：**其他**；把握：高。

契约 data_type=DATE，agent 按规定转换，gold 直接透传源 VARCHAR；不归为 agent 前提错误。金额 BIGINT 的取整和 DATE 去掉时刻也有契约依据。

前提P/处理选择：不适用：其他类是契约与gold不一致，并非agent未确立的前提。
是否说出：第2档——交付物里只有通用说明。通用类型声明，非本列的具体解释。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 8530 |
| L1 | 1045 | 1045 | 5397 | 4362 |
| L2 | 1045 | 1045 | 5381 | 4346 |
| L3 | 1045 | 1045 | 3311 | 3311 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `exchange_rate_date`；减少量（L0行、格）：`[0, 1035]`。

准确old/new：

```json
[
  {
    "old": "try_cast(\"exchange_rate_date\" AS DATE)",
    "new": "\"exchange_rate_date\"",
    "offset": 1814
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast("exchange_rate_date" AS DATE)
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/1.json` / `1.args.content` / process：

```text
- name: exchange_rate_date
          data_type: DATE
```

### target_date_representation

角色：参与；类别：**其他**；把握：高。

契约 data_type=DATE，agent 按规定转换，gold 直接透传源 VARCHAR；不归为 agent 前提错误。金额 BIGINT 的取整和 DATE 去掉时刻也有契约依据。

前提P/处理选择：不适用：其他类是契约与gold不一致，并非agent未确立的前提。
是否说出：第2档——交付物里只有通用说明。通用类型声明，非本列的具体解释。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 1045 | 1045 | 9565 | 8530 |
| L1 | 1045 | 1045 | 5397 | 4362 |
| L2 | 1045 | 1045 | 5381 | 4346 |
| L3 | 1045 | 1045 | 3311 | 3311 |

单改：`records/021_reruns_impl-030_stg_zuora__invoice.json` / `target_date`；减少量（L0行、格）：`[0, 1035]`。

准确old/new：

```json
[
  {
    "old": "try_cast(\"target_date\" AS DATE)",
    "new": "\"target_date\"",
    "offset": 3100
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json` / `71.args.final_thought` / delivery：

```text
严格按 staging 类型输出，在业务比较时对枚举做文本转换。
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql` / `SQL.text` / delivered_code：

```text
try_cast("target_date" AS DATE)
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/1.json` / `1.args.content` / process：

```text
- name: target_date
          data_type: DATE
```

## 证据来源

- 契约/SQL材料包：`records/013_packages/013_impl-030_staging_stg_zuora__invoice.md`。
- 原始契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql`。
- 原始交付报告及SQL注释清单：`records/039_checks/delivery_sources.json`。
- 核实查询复用（保守计入失败共2条，不超过5）：`records/021_calibration_queries.json#impl-030`、`records/017_queries_impl-030.json#V2`。
- 盲标封存、解盲差异：`records/039_calibration_blind_sealed.json`、`records/039_calibration_comparison.json`。

## 不确定或没查到的（含规则问题）

- 沿用038按(L0行减少,L0格减少)排序：行并列时用格子数；盲标曾严格按行数判只能组合修复。该读法差异单列规则问题，封存件不改。组合诊断全表对齐只说明差异覆盖，不参与单改排序。
- 补充组合诊断为L0–L3全表0行/0格，见`records/039_checks/calibration_combo.json`。它不是单点排序证据，也不表示agent违反了类型契约。
- 曾经理解对过保留“是”，与036不同，依据已在account_source列明。盲标event34引句回查能匹配文本，但不属于本张invoice；工作结果已撤回其证明作用。

## 建议的下一步

由用户与Claude复核校准中的规则读法和轨迹证据差异；第二阶段继续同一会话的40张正式表，不重新盲标、不改封存件。
