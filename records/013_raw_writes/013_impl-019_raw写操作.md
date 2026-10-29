# impl-019：raw 写语法与脚本调用原文

仅记录语法命中和调用源码；脚本分支执行、历史文件版本、操作是否改变数据未由静态匹配证明。

## event 27

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/27.json

```bash
python run.py > /tmp/run.log 2>&1; tail -80 /tmp/run.log
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 50

```text
                    col_defs.append(f"{safe} {typ}")
                self.conn.execute(f"CREATE OR REPLACE TABLE raw.{t} ({', '.join(col_defs)})")
                data = source.execute(f"SELECT * FROM {t}").fetchall()
                if data:
                    placeholders = ', '.join(['?' for _ in cols])
```

INSERT/REPLACE INTO；源码行 54

```text
                    placeholders = ', '.join(['?' for _ in cols])
                    self.conn.executemany(f"INSERT INTO raw.{t} VALUES ({placeholders})", data)
                logger.info(f"raw.{t} imported: {len(data)} rows")
        finally:
            source.close()
```

## event 35

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/35.json

```bash
python - <<'PY'
from pathlib import Path
# Missing raw fields called for in staging contract are represented as typed NULLs; source relation remains feed label.
for name in ['stg_apple_store__app_crash_daily','stg_apple_store__sales_subscription_summary','stg_apple_store__sales_subscription_events']:
 p=Path('sql/staging')/(name+'.sql'); s=p.read_text()
 # source_type does not exist in these raw feeds
 s=s.replace('cast(r.source_type AS VARCHAR) AS source_type','CAST(NULL AS VARCHAR) AS source_type')
 p.write_text(s)
# date spine references require explicit schema name
for p in Path('sql/intermediate').rglob('*.sql'):
 s=p.read_text().replace('FROM int_apple_store__date_spine','FROM intermediate.int_apple_store__date_spine')
 p.write_text(s)
# correct device report grain reference in marts
p=Path('sql/marts/apple_store__device_report.sql'); s=p.read_text().replace('intermediate.int_apple_store__device_report_report','intermediate.int_apple_store__device_report'); p.write_text(s)
PY
python run.py > /tmp/run2.log 2>&1; grep -E 'ERROR|WARNING - Skip|Created intermediate.*report|Created marts' /tmp/run2.log | tail -100
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 50

```text
                    col_defs.append(f"{safe} {typ}")
                self.conn.execute(f"CREATE OR REPLACE TABLE raw.{t} ({', '.join(col_defs)})")
                data = source.execute(f"SELECT * FROM {t}").fetchall()
                if data:
                    placeholders = ', '.join(['?' for _ in cols])
```

INSERT/REPLACE INTO；源码行 54

```text
                    placeholders = ', '.join(['?' for _ in cols])
                    self.conn.executemany(f"INSERT INTO raw.{t} VALUES ({placeholders})", data)
                logger.info(f"raw.{t} imported: {len(data)} rows")
        finally:
            source.close()
```

## event 37

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/37.json

```bash
mkdir -p sql/intermediate/reporting_grain; cp sql/intermediate/territory/reporting_grain/int_apple_store__territory_report.sql sql/intermediate/reporting_grain/; cp sql/intermediate/device_report/reporting_grain/int_apple_store__device_report.sql sql/intermediate/reporting_grain/; cp sql/intermediate/platform_version/reporting_grain/int_apple_store__platform_version_report.sql sql/intermediate/reporting_grain/; cp sql/intermediate/source_type/reporting_grain/int_apple_store__source_type_report.sql sql/intermediate/reporting_grain/; cp sql/intermediate/app_version/reporting_grain/int_apple_store__app_version_report.sql sql/intermediate/reporting_grain/; cp sql/intermediate/subscription/reporting_grain/int_apple_store__subscription_report.sql sql/intermediate/reporting_grain/; python run.py > /tmp/run3.log 2>&1; grep -E 'ERROR|WARNING - Skip' /tmp/run3.log; tail -20 /tmp/run3.log
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 50

```text
                    col_defs.append(f"{safe} {typ}")
                self.conn.execute(f"CREATE OR REPLACE TABLE raw.{t} ({', '.join(col_defs)})")
                data = source.execute(f"SELECT * FROM {t}").fetchall()
                if data:
                    placeholders = ', '.join(['?' for _ in cols])
```

INSERT/REPLACE INTO；源码行 54

```text
                    placeholders = ', '.join(['?' for _ in cols])
                    self.conn.executemany(f"INSERT INTO raw.{t} VALUES ({placeholders})", data)
                logger.info(f"raw.{t} imported: {len(data)} rows")
        finally:
            source.close()
```

## event 41

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/41.json

```bash
cat > sql/intermediate/int_apple_store__installation_and_deletion_daily.sql <<'SQL'
SELECT
    date_day,
    app_id,
    download_type,
    app_version,
    device,
    platform_version,
    source_type,
    page_type,
    app_download_date,
    territory,
    source_relation,
    SUM(CASE WHEN lower(download_type) = 'first-time download' THEN counts ELSE 0 END) AS first_time_downloads,
    SUM(CASE WHEN lower(download_type) = 'redownload' THEN counts ELSE 0 END) AS redownloads,
    SUM(CASE WHEN lower(download_type) IN ('first-time download', 'redownload') THEN counts ELSE 0 END) AS total_downloads,
    SUM(CASE WHEN lower(event) = 'delete' THEN counts ELSE 0 END) AS deletions,
    SUM(CASE WHEN lower(event) = 'install' THEN counts ELSE 0 END) AS installations
FROM staging.stg_apple_store__app_store_installation_and_deletion_daily
GROUP BY
    date_day,
    app_id,
    download_type,
    app_version,
    device,
    platform_version,
    source_type,
    page_type,
    app_download_date,
    territory,
    source_relation
SQL
# Ensure source contract session territory nullifies codes whose cleaned length is not 2
python - <<'PY'
from pathlib import Path
p=Path('sql/staging/stg_apple_store__app_session_daily.sql')
s=p.read_text().replace('upper(trim(cast(r.territory AS VARCHAR))) AS territory', "CASE WHEN length(trim(cast(r.territory AS VARCHAR))) = 2 THEN upper(trim(cast(r.territory AS VARCHAR))) ELSE NULL END AS territory")
p.write_text(s)
# remove redundant reporting grain copies from each family folder; execution_order expects common reporting_grain directory.
for fam in ['territory','device_report','platform_version','source_type','app_version','subscription']:
 p=Path('sql/intermediate')/fam/'reporting_grain'
 if p.exists():
  for f in p.glob('*.sql'): f.unlink()
  p.rmdir()
PY
python run.py > /tmp/run4.log 2>&1; grep -E 'ERROR|WARNING - Skip' /tmp/run4.log || true; tail -8 /tmp/run4.log
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 50

```text
                    col_defs.append(f"{safe} {typ}")
                self.conn.execute(f"CREATE OR REPLACE TABLE raw.{t} ({', '.join(col_defs)})")
                data = source.execute(f"SELECT * FROM {t}").fetchall()
                if data:
                    placeholders = ', '.join(['?' for _ in cols])
```

INSERT/REPLACE INTO；源码行 54

```text
                    placeholders = ', '.join(['?' for _ in cols])
                    self.conn.executemany(f"INSERT INTO raw.{t} VALUES ({placeholders})", data)
                logger.info(f"raw.{t} imported: {len(data)} rows")
        finally:
            source.close()
```

## event 47

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/47.json

```bash
cat > sql/intermediate/int_apple_store__installation_and_deletion_daily.sql <<'SQL'
SELECT
    date_day,
    app_id,
    download_type,
    app_version,
    device,
    platform_version,
    source_type,
    page_type,
    app_download_date,
    territory,
    source_relation,
    SUM(CASE WHEN lower(event) = 'delete' THEN counts ELSE 0 END) AS deletions,
    SUM(CASE WHEN lower(event) = 'install' THEN counts ELSE 0 END) AS installations
FROM staging.stg_apple_store__app_store_installation_and_deletion_daily
GROUP BY
    date_day,
    app_id,
    download_type,
    app_version,
    device,
    platform_version,
    source_type,
    page_type,
    app_download_date,
    territory,
    source_relation
SQL
python run.py > /tmp/finalrun.log 2>&1; grep -E 'ERROR|WARNING - Skip' /tmp/finalrun.log || true; grep 'Created marts' /tmp/finalrun.log
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 50

```text
                    col_defs.append(f"{safe} {typ}")
                self.conn.execute(f"CREATE OR REPLACE TABLE raw.{t} ({', '.join(col_defs)})")
                data = source.execute(f"SELECT * FROM {t}").fetchall()
                if data:
                    placeholders = ', '.join(['?' for _ in cols])
```

INSERT/REPLACE INTO；源码行 54

```text
                    placeholders = ', '.join(['?' for _ in cols])
                    self.conn.executemany(f"INSERT INTO raw.{t} VALUES ({placeholders})", data)
                logger.info(f"raw.{t} imported: {len(data)} rows")
        finally:
            source.close()
```

## event 53

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/53.json

```bash
cat > /workspace/result.md <<'EOF'
【回复用户】

已按 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Apple Store SQL pipeline，文件位于 `sql/staging/`、`sql/intermediate/` 和 `sql/marts/`。中间层报告模型按运行器要求放置于 `sql/intermediate/reporting_grain/`。

**验证结果**
- 执行 `python run.py` 成功，无 SQL 错误或缺失模型警告；七个 marts 均成功生成。
- 实际生成行数：overview 747,000；territory 831,660；subscription 3,458,610；device 211,650；platform version 694,710；source type 37,350；app version 102,090。
- 核查日期 spine 有 2,490 行、2,490 个非空唯一日期；生成 SQL 文件均未以分号结尾，模型文件名与 contract 名称匹配。

**契约数据缺失与处理说明**
- 原始 crash 与 subscription feeds 不含契约要求的 `source_type` 字段。为保持 staging 输出字段及类型契约，相关 staging 模型以 `CAST(NULL AS VARCHAR)` 表达该字段；残余影响是这些来源的该属性不可用，依赖它的分组会归入 NULL 分组。未推断或伪造属性值。
- 会话来源原始日期/下载日期字段以字符串形式提供；使用 `TRY_CAST` 转为日期。会话 staging 按契约过滤无效、未来及 2020-01-01 以前日期，剔除空设备、非 Apple 设备及含字母的版本号；territory 标准化为大写、去除首尾空白，并将非两字符代码置 NULL。下载/安装版本字段按目标类型转 VARCHAR，保留其源值格式（原始数值 `329372.0` 会保留此表示）。
- country-code numeric 源字段是整数，而 staging 契约要求 VARCHAR；转换成 VARCHAR 后，源数据本身没有提供的前导零无法恢复。
- SQL 聚合保留契约要求的 NULL 与重复记录语义；marts 对缺失指标按契约补零。Subscription source 的键由 summary 与 events 堆叠并按契约字段去重。

未发现运行失败。`run.py` 的配置对部分 staging 字段使用了只存在于契约、但原始 feed 中不存在的列，本实现按上述最小安全方式处理并已验证整条 pipeline 可执行。
EOF
cat /workspace/result.md
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 50

```text
                    col_defs.append(f"{safe} {typ}")
                self.conn.execute(f"CREATE OR REPLACE TABLE raw.{t} ({', '.join(col_defs)})")
                data = source.execute(f"SELECT * FROM {t}").fetchall()
                if data:
                    placeholders = ', '.join(['?' for _ in cols])
```

INSERT/REPLACE INTO；源码行 54

```text
                    placeholders = ', '.join(['?' for _ in cols])
                    self.conn.executemany(f"INSERT INTO raw.{t} VALUES ({placeholders})", data)
                logger.info(f"raw.{t} imported: {len(data)} rows")
        finally:
            source.close()
```

## event 57

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/57.json

```bash
mkdir -p /workspace && cat > /workspace/result.md <<'EOF'
【回复用户】

已按 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Apple Store SQL pipeline，文件位于 `sql/staging/`、`sql/intermediate/` 和 `sql/marts/`。中间层报告模型按运行器要求放置于 `sql/intermediate/reporting_grain/`。

**验证结果**
- 执行 `python run.py` 成功，无 SQL 错误或缺失模型警告；七个 marts 均成功生成。
- 实际生成行数：overview 747,000；territory 831,660；subscription 3,458,610；device 211,650；platform version 694,710；source type 37,350；app version 102,090。
- 核查日期 spine 有 2,490 行、2,490 个非空唯一日期；生成 SQL 文件均未以分号结尾，模型文件名与 contract 名称匹配。

**契约数据缺失与处理说明**
- 原始 crash 与 subscription feeds 不含契约要求的 `source_type` 字段。为保持 staging 输出字段及类型契约，相关 staging 模型以 `CAST(NULL AS VARCHAR)` 表达该字段；残余影响是这些来源的该属性不可用，依赖它的分组会归入 NULL 分组。未推断或伪造属性值。
- 会话来源原始日期/下载日期字段以字符串形式提供；使用 `TRY_CAST` 转为日期。会话 staging 按契约过滤无效、未来及 2020-01-01 以前日期，剔除空设备、非 Apple 设备及含字母的版本号；territory 标准化为大写、去除首尾空白，并将非两字符代码置 NULL。下载/安装版本字段按目标类型转 VARCHAR，保留其源值格式（原始数值 `329372.0` 会保留此表示）。
- country-code numeric 源字段是整数，而 staging 契约要求 VARCHAR；转换成 VARCHAR 后，源数据本身没有提供的前导零无法恢复。
- SQL 聚合保留契约要求的 NULL 与重复记录语义；marts 对缺失指标按契约补零。Subscription source 的键由 summary 与 events 堆叠并按契约字段去重。

未发现运行失败。`run.py` 的配置对部分 staging 字段使用了只存在于契约、但原始 feed 中不存在的列，本实现按上述最小安全方式处理并已验证整条 pipeline 可执行。
EOF
cat /workspace/result.md
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 50

```text
                    col_defs.append(f"{safe} {typ}")
                self.conn.execute(f"CREATE OR REPLACE TABLE raw.{t} ({', '.join(col_defs)})")
                data = source.execute(f"SELECT * FROM {t}").fetchall()
                if data:
                    placeholders = ', '.join(['?' for _ in cols])
```

INSERT/REPLACE INTO；源码行 54

```text
                    placeholders = ', '.join(['?' for _ in cols])
                    self.conn.executemany(f"INSERT INTO raw.{t} VALUES ({placeholders})", data)
                logger.info(f"raw.{t} imported: {len(data)} rows")
        finally:
            source.close()
```

## event 61

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/61.json

```bash
cat > result.md <<'EOF'
【回复用户】

已按 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Apple Store SQL pipeline，文件位于 `sql/staging/`、`sql/intermediate/` 和 `sql/marts/`。中间层报告模型按运行器要求放置于 `sql/intermediate/reporting_grain/`。

**验证结果**
- 执行 `python run.py` 成功，无 SQL 错误或缺失模型警告；七个 marts 均成功生成。
- 实际生成行数：overview 747,000；territory 831,660；subscription 3,458,610；device 211,650；platform version 694,710；source type 37,350；app version 102,090。
- 核查日期 spine 有 2,490 行、2,490 个非空唯一日期；生成 SQL 文件均未以分号结尾，模型文件名与 contract 名称匹配。

**契约数据缺失与处理说明**
- 原始 crash 与 subscription feeds 不含契约要求的 `source_type` 字段。为保持 staging 输出字段及类型契约，相关 staging 模型以 `CAST(NULL AS VARCHAR)` 表达该字段；残余影响是这些来源的该属性不可用，依赖它的分组会归入 NULL 分组。未推断或伪造属性值。
- 会话来源原始日期/下载日期字段以字符串形式提供；使用 `TRY_CAST` 转为日期。会话 staging 按契约过滤无效、未来及 2020-01-01 以前日期，剔除空设备、非 Apple 设备及含字母的版本号；territory 标准化为大写、去除首尾空白，并将非两字符代码置 NULL。下载/安装版本字段按目标类型转 VARCHAR，保留其源值格式（原始数值 `329372.0` 会保留此表示）。
- country-code numeric 源字段是整数，而 staging 契约要求 VARCHAR；转换成 VARCHAR 后，源数据本身没有提供的前导零无法恢复。
- SQL 聚合保留契约要求的 NULL 与重复记录语义；marts 对缺失指标按契约补零。Subscription source 的键由 summary 与 events 堆叠并按契约字段去重。

未发现运行失败。`run.py` 的配置对部分 staging 字段使用了只存在于契约、但原始 feed 中不存在的列，本实现按上述最小安全方式处理并已验证整条 pipeline 可执行。
EOF
cat result.md
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 50

```text
                    col_defs.append(f"{safe} {typ}")
                self.conn.execute(f"CREATE OR REPLACE TABLE raw.{t} ({', '.join(col_defs)})")
                data = source.execute(f"SELECT * FROM {t}").fetchall()
                if data:
                    placeholders = ', '.join(['?' for _ in cols])
```

INSERT/REPLACE INTO；源码行 54

```text
                    placeholders = ', '.join(['?' for _ in cols])
                    self.conn.executemany(f"INSERT INTO raw.{t} VALUES ({placeholders})", data)
                logger.info(f"raw.{t} imported: {len(data)} rows")
        finally:
            source.close()
```
